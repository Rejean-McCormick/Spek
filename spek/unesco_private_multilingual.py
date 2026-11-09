"""Assemble *existing* private UNESCO article projections, never translations.

Input: distinct language directories produced by spek.unesco_private_drafts.
All article bytes are copied unchanged after SHA-256 verification. The set may
be incomplete. One canonical branch namespace and graph must be shared by all
languages, and a concept's canonical semantic fingerprint cannot drift between
language projections. No new prose, Kristal identity, qualification or public
publication is produced by this module.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

from .unesco_private_drafts import OUT_PROFILE, LOCALES

PROFILE = 'spek.unesco-mt1-10-private-multilingual/1.0'
DIGEST = re.compile(r'^[0-9a-f]{64}$')
ARTICLE = re.compile(r'^concept[1-9][0-9]*\.md$')
CONCEPT = re.compile(r'^concept(?:[1-9]|[1-3][0-9]|4[01])$')
KQ = re.compile(r'^KQ[0-9]+$')
KA = re.compile(r'^KA[0-9]+$')

class AssembleError(ValueError):
    pass


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _not_symlinked(path: Path):
    for part in (path, *path.parents):
        if part.is_symlink():
            raise AssembleError('Symlinked input/output path refused')


def _outside_git(path: Path):
    for part in (path, *path.parents):
        if (part / '.git').exists():
            raise AssembleError('Private output inside a Git checkout refused')


def _read_private_projection(directory: Path):
    _not_symlinked(directory)
    if not directory.is_dir():
        raise AssembleError('Missing private projection directory')
    manifest_file = directory / 'manifest.json'
    _not_symlinked(manifest_file)
    if not manifest_file.is_file() or manifest_file.stat().st_size > 3_000_000:
        raise AssembleError('Missing or oversized private manifest')
    raw = manifest_file.read_bytes()
    try:
        d = json.loads(raw)
    except (ValueError,UnicodeDecodeError) as exc:
        raise AssembleError('Invalid JSON manifest') from exc
    if (not isinstance(d, dict) or d.get('profile') != OUT_PROFILE or
        d.get('branch') != 'unesco-mt1-10' or d.get('one_branch_kristal') is not True or
        d.get('status') != 'PRIVATE_PREVIEW_ONLY'):
        raise AssembleError('Wrong private projection profile/branch')
    if any(d.get(k) is not False for k in (
        'runtime_attestation_verified', 'canonical_approval_verified',
        'content_rights_verified', 'public_release_authorized')):
        raise AssembleError('Refuse a projection asserting approval/public rights')
    locale = d.get('locale')
    if locale not in LOCALES:
        raise AssembleError('Locale not in UNESCO pilot scope')
    ns = d.get('namespace_id')
    graph = d.get('semantic_graph_id')
    if not isinstance(ns,str) or not ns.strip() or not isinstance(graph,str) or not graph.strip():
        raise AssembleError('Canonical graph and namespace must be supplied')
    files = d.get('files'); semantics=d.get('semantic_index')
    if not isinstance(files,dict) or not files or not isinstance(semantics,dict):
        raise AssembleError('Missing article hashes or semantic fingerprints')
    if len(files)>41 or d.get('generated_drafts') != len(files):
        raise AssembleError('Draft count inconsistent with UNESCO branch')
    ids = {x[:-3] for x in files}
    if not ids or ids != set(semantics):
        raise AssembleError('Missing or extra semantic fingerprint for a page')
    content = {}
    for name, expected in files.items():
        if not isinstance(name,str) or not ARTICLE.fullmatch(name) or not CONCEPT.fullmatch(name[:-3]):
            raise AssembleError('Unsafe article name')
        if not isinstance(expected,str) or not DIGEST.fullmatch(expected):
            raise AssembleError('Malformed article digest')
        p=directory / name
        _not_symlinked(p)
        if not p.is_file() or p.stat().st_size > 512_000:
            raise AssembleError('Missing or oversized article')
        body=p.read_bytes()
        if _sha(body)!=expected:
            raise AssembleError('Article digest mismatch: '+name)
        sem=semantics[name[:-3]]
        if (not isinstance(sem,dict) or not KQ.fullmatch(str(sem.get('local_kq'))) or
            not isinstance(sem.get('assertions_sha256'),str) or
            not DIGEST.fullmatch(sem['assertions_sha256']) or
            not isinstance(sem.get('ka_ids'),list) or not sem['ka_ids'] or
            any(not KA.fullmatch(str(a)) for a in sem['ka_ids'])):
            raise AssembleError('Invalid semantic proof for '+name)
        content[name]=body
    # A bogus file in a draft directory can be a concealed leak if copied.
    # This assembler copies only named articles and refuses unlisted files.
    actual={p.name for p in directory.iterdir()}
    if actual != set(files) | {'manifest.json'}:
        raise AssembleError('Unexpected files in private draft directory')
    return d, _sha(raw), content


def prepare(draft_dirs: list[Path]):
    if not draft_dirs or len(draft_dirs)>len(LOCALES):
        raise AssembleError('Provide 1 to 14 distinct language draft directories')
    locale_data={}
    graph_id=None;namespace=None; all_semantics={}; articles={}
    source_manifests={}
    for draft_dir in draft_dirs:
        d, manifest_sha, files = _read_private_projection(draft_dir)
        locale=d['locale']
        if locale in locale_data:
            raise AssembleError('Duplicate locale: '+locale)
        if graph_id is None:
            graph_id=d['semantic_graph_id']; namespace=d['namespace_id']
        if (graph_id,namespace)!=(d['semantic_graph_id'],d['namespace_id']):
            raise AssembleError('Multiple canonical branch graphs detected')
        for cid,sem in d['semantic_index'].items():
            key=(sem['local_kq'],sem['assertions_sha256'],tuple(sorted(sem['ka_ids'])))
            if cid in all_semantics and all_semantics[cid]!=key:
                raise AssembleError('Semantic drift between languages for '+cid)
            all_semantics[cid]=key
        locale_data[locale]=d
        source_manifests[locale]=manifest_sha
        articles[locale]=files
    covered=sum(len(v) for v in articles.values())
    outcome={'profile':PROFILE,'branch':'unesco-mt1-10',
             'one_branch_kristal':True,'semantic_graph_id':graph_id,'namespace_id':namespace,
             'target_concepts':41,'target_locales':list(LOCALES),
             'available_locales':sorted(articles),'available_concepts':len(all_semantics),
             'available_article_projections':covered,'unfilled_article_slots':41*len(LOCALES)-covered,
             'locale_source_manifest_sha256':source_manifests,
             'locale_file_sha256':{k:{name:_sha(body) for name,body in v.items()}
                                  for k,v in sorted(articles.items())},
             'runtime_attestation_verified':False,'canonical_approval_verified':False,
             'content_rights_verified':False,'public_release_authorized':False,
             'status':'PRIVATE_MULTILINGUAL_PREVIEW_ONLY'}
    return articles,outcome


def write_private(draft_dirs: list[Path], out: Path):
    articles,manifest=prepare(draft_dirs)
    _not_symlinked(out)
    _outside_git(out)
    if out.exists():
        raise AssembleError('Output must be a NEW private directory')
    if not out.parent.is_dir():
        raise AssembleError('Output parent must exist')
    for p in draft_dirs:
        r=p.resolve()
        if out.resolve()==r or r.is_relative_to(out.resolve()):
            raise AssembleError('Output may not enclose source input')
    stage=Path(tempfile.mkdtemp(prefix='.'+out.name+'-multilingual-',dir=out.parent))
    try:
        for locale,files in articles.items():
            lang_dir=stage/locale
            lang_dir.mkdir()
            for filename,blob in files.items():
                (lang_dir/filename).write_bytes(blob)
        toc=['# UNESCO Educational Policy — aperçu privé',
             '', '**NON PUBLIABLE :** aucune autorisation de diffusion ni attestation linguistique.',
             '', 'Les pages ci-dessous proviennent de projections existantes du même Kristal;',
             'aucune phrase ni traduction n’a été générée par cet assembleur.', '']
        for locale in sorted(articles):
            toc.extend([f'## {locale}', ''])
            for filename in sorted(articles[locale]):
                toc.append(f'- [{filename[:-3]}]({locale}/{filename})')
            toc.append('')
        (stage/'index.md').write_text('\n'.join(toc)+'\n',encoding='utf8')
        manifest['index_md_sha256']=_sha((stage/'index.md').read_bytes())
        (stage/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        os.rename(stage,out)
    finally:
        if stage.exists():shutil.rmtree(stage)
    return manifest


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--draft-dir',type=Path,required=True,action='append')
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(argv)
    try:
        result=write_private(a.draft_dir,a.out)
        print(json.dumps({'status':result['status'],
                          'available_article_projections':result['available_article_projections'],
                          'unfilled_article_slots':result['unfilled_article_slots'],
                          'out':str(a.out),'publication':'BLOCKED'},ensure_ascii=False))
        return 0
    except (AssembleError,ValueError,TypeError,KeyError,OSError) as e:
        print(json.dumps({'status':'BLOCKED','error':str(e)},ensure_ascii=False),file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
