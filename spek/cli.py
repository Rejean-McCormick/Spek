"""Command line interface. No network calls, no GitHub writes, no canon writes."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import os
import shutil
import tempfile
from pathlib import Path
from .core import LANGS, ValidationError, compile_inputs, digest, read_json
from .render import article_html, article_tex, article_pdf, landing_html
from .document import project_document
from .bridge import bridge_import, fetch_konstellation
from .ai_phrases import import_ai
from .education import import_educational
from .wiki import build_wiki, verify_wiki, load_profiles

ROOT = Path(__file__).resolve().parent.parent

def load_model(args, production=False):
    source = read_json(Path(args.source))
    realizations = read_json(Path(args.realizations))
    ld = [read_json(p) for p in sorted(Path(args.layouts).glob('*.json'))]
    if not ld:
        raise ValidationError(f'No layouts in {args.layouts}')
    ss = read_json(Path(args.state_snapshot)) if args.state_snapshot else None
    return compile_inputs(source,realizations,ld,languages=tuple(args.languages.split(',')),
                          state_snapshot=ss,production=production)

def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, content):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(content,encoding='utf-8')

def build(args):
    model=load_model(args,production=args.production)
    dest=Path(args.out).resolve()
    if dest in {Path.cwd().resolve(), ROOT.resolve(), dest.parent}:
        raise ValidationError('Refusing unsafe output root')
    if dest.is_symlink() or (dest.exists() and not dest.is_dir()):
        raise ValidationError('Output destination is not a plain directory')
    if dest.exists() and any(dest.iterdir()):
        # Never silently combine files from older, differently configured builds.
        verify_site(dest)
    formats=set(args.formats.split(','))
    if formats - {'html','pdf','tex'} or not formats:
        raise ValidationError('Only html,pdf,tex are supported')
    dest.parent.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix='.'+dest.name+'-stage-',dir=dest.parent))
    try:
        if 'html' in formats:
            write(staging/'index.html',landing_html(model))
        for lang in model.languages:
            root=staging/lang
            write(root/'document.json',json.dumps(project_document(model,lang).to_dict(),ensure_ascii=False,sort_keys=True,indent=2)+'\n')
            if 'html' in formats:
                write(root/'index.html',article_html(model,lang,formats=formats))
            if 'tex' in formats:
                write(root/'article.tex',article_tex(model,lang))
            if 'pdf' in formats:
                root.mkdir(parents=True,exist_ok=True)
                article_pdf(model,lang,root/'article.pdf')
        paths=sorted(x for x in staging.rglob('*') if x.is_file() and x.name!='manifest.json')
        manifest={
          'format':'kristal.layout-build-manifest/0.1',
          'mode':'production_candidate' if args.production else 'demonstration',
          'status':'built_not_published_not_activated',
          'article_id':model.source['article']['id'],
          'languages':list(model.languages),
          'layouts':[{'id':k,'version':v['version']} for k,v in sorted(model.layouts.items())],
          'source_sha256':model.source_hash,
          'realizations_sha256':model.realization_hash,
          'layouts_sha256':model.layout_hash,
          'source_identity_reference_checked':model.source_verified,
          'semantic_certification':'not_evaluated',
          'publication_authorization':'not_granted_by_compiler',
          'files':{str(p.relative_to(staging)).replace('\\','/'):hash_file(p) for p in paths},
        }
        write(staging/'manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
        verify_site(staging)
        if dest.exists():
            if dest.is_symlink():raise ValidationError('Output destination changed to symlink')
            shutil.rmtree(dest)
        os.replace(staging,dest)
    finally:
        if staging.exists():shutil.rmtree(staging)
    print(f"BUILD: {manifest['mode']} · {len(manifest['files'])} artifacts · {','.join(model.languages)} · {dest}")
    return manifest

def verify_site(path, *, require_production=False):
    raw_out=Path(path)
    if raw_out.is_symlink():
        raise ValidationError('Site root must not be a symlink')
    out=raw_out.resolve()
    if (out/'manifest.json').is_symlink():
        raise ValidationError('Manifest must not be a symlink')
    manifest=read_json(out/'manifest.json')
    if manifest.get('format')!='kristal.layout-build-manifest/0.1':
        raise ValidationError('Not a layout build manifest')
    if require_production and manifest.get('mode')!='production_candidate':
        raise ValidationError('Public deployment prohibited for demonstration artifacts')
    if require_production and (manifest.get('source_identity_reference_checked') is not True):
        raise ValidationError('Missing source state reference check')
    files=manifest.get('files')
    if not isinstance(files,dict) or not files:
        raise ValidationError('Invalid/empty manifest files')
    expected=set()
    for rel,dig in files.items():
        p=Path(rel)
        if p.is_absolute() or '..' in p.parts or p.as_posix()!=rel or not rel:
            raise ValidationError('Unsafe file path in manifest')
        if not isinstance(dig,str) or len(dig)!=64:
            raise ValidationError('Invalid digest in manifest')
        dest=out/p
        if any(parent.is_symlink() for parent in (dest, *dest.parents) if parent != out and out in parent.parents) or not dest.is_file() or not dest.resolve().is_relative_to(out):
            raise ValidationError(f'Unsafe/missing file {rel}')
        if hash_file(dest)!=dig:
            raise ValidationError(f'File altered since compilation: {rel}')
        expected.add(rel)
    actual={str(x.relative_to(out)).replace('\\','/') for x in out.rglob('*') if x.is_file() and x.name!='manifest.json'}
    if actual!=expected:
        raise ValidationError('Unlisted or missing file in build output')
    if require_production:
        if set(manifest.get('languages',[]))!={'fr','en','it'}:
            raise ValidationError('This deployment workflow requires fr,en,it')
        if not {'index.html','fr/index.html','en/index.html','it/index.html'}<=expected:
            raise ValidationError('Missing landing or language pages')
    print(f'VERIFIED: {len(files)} files · {manifest["mode"]}')
    return manifest

def import_semantik(args):
    """Import known SemantiK prototype `cases` with explicit case→unit/lang mapping.

    This is not a runtime execution or certification adapter. Entries are
    explicitly marked as fixtures/unqualified and never silently promoted.
    """
    raw=read_json(Path(args.input)); mapping=read_json(Path(args.mapping))
    if not isinstance(raw.get('cases'),list) or raw.get('status')!='PASS':
        raise ValidationError('Expected successful SemantiK prototype cases JSON')
    mp=mapping.get('cases')
    if not isinstance(mp,dict) or not mp:
        raise ValidationError('Missing cases mapping')
    cases={item.get('case'):item for item in raw['cases']}
    entries={}
    for case,binding in mp.items():
        if case not in cases:
            raise ValidationError('No SemantiK case: '+case)
        key=binding.get('realization_key')
        lang=binding.get('language')
        if not isinstance(key,str) or lang not in LANGS:
            raise ValidationError('Invalid binding for '+case)
        item=cases[case];txt=item.get('plain_text')
        if not isinstance(txt,str) or not txt.strip() or not item.get('request_id'):
            raise ValidationError('Missing phrase or request identity in '+case)
        if lang in entries.get(key,{}):
            raise ValidationError('Duplicate bound realization '+key+'/'+lang)
        entries.setdefault(key,{})[lang]={'text':txt,'status':'fixture','provider':'semantik_prototype_import',
          'request_id':item['request_id'],'runtime_set_id':item.get('runtime',{}).get('runtime_set_id',''),
          'qualification':'not_evaluated_no_gf_compiler', 'case':case}
    output={'format':'kristal.layout-realizations/0.1','note':'UNQUALIFIED SemantiK prototype import; fill missing languages and obtain independent qualification for real publication.', 'entries':entries}
    write(Path(args.out),json.dumps(output,indent=2,ensure_ascii=False)+'\n')
    print(f'IMPORTED: {len(entries)} phrase bindings (fixture only) → {args.out}')

def main(argv=None):
    parser=argparse.ArgumentParser(description='Spek: offline semantic publishing compiler')
    sub=parser.add_subparsers(dest='command',required=True)
    def model_opts(p):
        p.add_argument('--source',default=str(ROOT/'examples/article.json'))
        p.add_argument('--realizations',default=str(ROOT/'examples/realizations.json'))
        p.add_argument('--layouts',default=str(ROOT/'layouts'))
        p.add_argument('--languages',default='fr,en,it')
        p.add_argument('--state-snapshot',help='Required to cross-check a v9 reference for production')
    chk=sub.add_parser('check');model_opts(chk)
    b=sub.add_parser('build');model_opts(b)
    b.add_argument('--out',default='dist');b.add_argument('--formats',default='html,pdf,tex')
    b.add_argument('--production',action='store_true',help='Block fixtures & unreviewed languages, not an authorization to publish')
    v=sub.add_parser('verify-site');v.add_argument('site');v.add_argument('--require-production',action='store_true')
    i=sub.add_parser('import-semantik');i.add_argument('--input',required=True);i.add_argument('--mapping',required=True);i.add_argument('--out',required=True)
    bridge=sub.add_parser('bridge-import', help='Read-only import of a pinned external selection')
    bridge.add_argument('--adapter',required=True,choices=('konstellation','exchange'))
    bridge.add_argument('--input',required=True,help='Exported Konstellation ResultSet or Spek exchange JSON')
    bridge.add_argument('--template',required=True,help='Locally approved Spek article template')
    bridge.add_argument('--mapping',required=True,help='Explicit binding map with payload digests')
    bridge.add_argument('--out',required=True)
    kfetch=sub.add_parser('bridge-fetch-konstellation',help='Explicit opt-in POST /api/query snapshot capture')
    kfetch.add_argument('--base-url',required=True)
    kfetch.add_argument('--query-file',required=True)
    kfetch.add_argument('--token-env',help='Name of environment variable holding bearer token')
    kfetch.add_argument('--out',required=True)
    ai=sub.add_parser('import-ai' ,help='Import preconstructed AI phrases (no SemantiK call)')
    ai.add_argument('--input',required=True)
    ai.add_argument('--base',help='Existing realization bundle to extend (no overwrite)')
    ai.add_argument('--out',required=True)
    wb=sub.add_parser('build-wiki',help='Create a PRIVATE Arketype-specific GitHub Wiki draft using Spek/SemantiK realizations')
    wb.add_argument('--source',required=True,help='Explicitly selected Spek semantic article.json')
    wb.add_argument('--realizations',required=True,help='Frozen SemantiK realization bundle JSON')
    wb.add_argument('--layouts',default=str(ROOT/'layouts'))
    wb.add_argument('--templates',default=str(ROOT/'wiki-templates'/'archetype-profiles.json'))
    wb.add_argument('--archetype',required=True,help='Explicit Arketype slug, never inferred from title')
    wb.add_argument('--language',default='fr',choices=LANGS)
    wb.add_argument('--slug',required=True,help='Safe page identifier: lowercase letters/digits/hyphens')
    wb.add_argument('--out',required=True,help='New private destination directory, never a Git checkout')
    wb.add_argument('--state-snapshot',help='Required for a real v9 pinned Kristal state')
    wb.add_argument('--demonstration',action='store_true',help='Only for fixture previews, never a publication authorization')
    wv=sub.add_parser('verify-wiki',help='Verify the SHA-256 inventory of a private draft')
    wv.add_argument('path')
    wl=sub.add_parser('list-wiki-templates',help='List Spek Wiki layouts allowed by each Arketype')
    wl.add_argument('--templates',default=str(ROOT/'wiki-templates'/'archetype-profiles.json'))
    edu=sub.add_parser('import-educational',help='Import a curated Ekole/Kompose local-preview projection (never raw upstream data)')
    edu.add_argument('--adapter',required=True,choices=('ekole','kompose'))
    edu.add_argument('--input',required=True)
    edu.add_argument('--out-dir',required=True)
    args=parser.parse_args(argv)
    try:
        if args.command=='check':
            m=load_model(args);print(f'PASS: {len(m.sections)} sections · {len(m.units)} units · {len(m.evidence)} evidence · {",".join(m.languages)} · demo={m.demo}')
        elif args.command=='build': build(args)
        elif args.command=='build-wiki':
            manifest=build_wiki(source=Path(args.source),realizations=Path(args.realizations),
                layouts=Path(args.layouts),templates=Path(args.templates),
                archetype=args.archetype,language=args.language,slug=args.slug,
                out=Path(args.out),demonstration=args.demonstration,
                state_snapshot=Path(args.state_snapshot) if args.state_snapshot else None)
            print('PRIVATE WIKI DRAFT: '+str(args.out)+' | '+', '.join(manifest['files']))
        elif args.command=='verify-wiki':
            manifest=verify_wiki(Path(args.path))
            print('WIKI VERIFIED: '+str(len(manifest['files']))+' Markdown files (NOT publication approval)')
        elif args.command=='list-wiki-templates':
            templates=load_profiles(Path(args.templates))
            for slug, row in sorted(templates.items()):
                print(slug+': '+', '.join(row['allowed_layouts']))
        elif args.command=='verify-site':verify_site(args.site,require_production=args.require_production)
        elif args.command=='import-semantik':import_semantik(args)
        elif args.command=='bridge-import':
            value=bridge_import(args.adapter,read_json(Path(args.input)),read_json(Path(args.template)),read_json(Path(args.mapping)))
            write(Path(args.out),json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
            print(f'BRIDGED: {args.adapter} · {len(value["units"])} semantic units · local preview only · {args.out}')
        elif args.command=='bridge-fetch-konstellation':
            token=os.environ.get(args.token_env,'') if args.token_env else ''
            if args.token_env and not token:
                raise ValidationError('Requested bearer token environment variable is empty')
            val=fetch_konstellation(args.base_url,read_json(Path(args.query_file)),token=token)
            write(Path(args.out),json.dumps(val,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
            print(f'CAPTURED: complete Konstellation ResultSet · {args.out}')
        elif args.command=='import-educational':
            source,realizations=import_educational(read_json(Path(args.input)),args.adapter)
            target=Path(args.out_dir).resolve()
            if target.is_symlink() or target in {Path.cwd().resolve(),ROOT.resolve()} or target.exists() and any(target.iterdir()):
                raise ValidationError('Educational import output must be a new/empty directory')
            write(target/'article.json',json.dumps(source,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
            write(target/'realizations.json',json.dumps(realizations,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
            print(f'IMPORTED: {args.adapter} · {len(source["sections"])} layouts · local preview only · {target}')
        elif args.command=='import-ai':
            val=import_ai(read_json(Path(args.input)),read_json(Path(args.base)) if args.base else None)
            write(Path(args.out),json.dumps(val,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
            print(f'AI IMPORTED: {len(val["entries"])} keys · preconstructed only · {args.out}')
        return 0
    except (ValidationError,OSError,ValueError,KeyError) as e:
        print('BLOCKED: '+str(e),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
