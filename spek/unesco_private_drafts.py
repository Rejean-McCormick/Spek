"""Private editorial draft from *already realized* KAs of one branch Kristal.

No Wikipedia translation, no LLM or GF invocation, no invented semantic content,
no GitHub writes. Content is only text already supplied and attributed in the
frozen phrase file. Drafts remain unpublishable even when marked 'reviewed'.
This is a narrow UNESCO pilot adapter, not a replacement for Spek's approved
editorial-layout compiler and independent C1-C4 publication gates.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,shutil,sys,tempfile
from pathlib import Path

IN_PROFILE='kristal.integration.unesco-mt1-10-semantic-handoff/1.0'
PHRASE_PROFILE='spek.unesco-mt1-10-frozen-phrases/1.0'
OUT_PROFILE='spek.unesco-mt1-10-private-drafts/1.0'
LOCALES=('en','fr','es','de','nl','sv','da','no','nn','fi','et','af','it','pt')
SHA=re.compile(r'^[0-9a-f]{64}$')
class DraftError(ValueError):pass

def load(path):
    if not path.is_file() or path.stat().st_size>10_000_000:raise DraftError('Missing or oversized JSON source')
    return json.loads(path.read_text('utf8'))

def sha(content):return hashlib.sha256(content).hexdigest()

def safe_md(value):
    if not isinstance(value,str) or len(value)>12000 or not value.strip():raise DraftError('Missing or oversized realized text')
    # Escape Markdown and HTML. Forbid control characters in editorial text.
    if any(ord(c)<32 and c not in '\t\n' for c in value):raise DraftError('Control characters in realized text')
    text=' '.join(value.split())
    return re.sub(r'([\\`*_{}\[\]()<>#+!|])',r'\\\1',text)

def prepare(handoff:dict,phrases:dict):
    if handoff.get('profile')!=IN_PROFILE or handoff.get('branch')!='unesco-mt1-10' or handoff.get('semantic_grain')!='one_branch_kristal':
        raise DraftError('Wrong semantic handoff')
    if handoff.get('publication_authorized') is not False or handoff.get('authoritative_authoring_checked') is not False:
        raise DraftError('Unexpected authority claim in research handoff')
    if (phrases.get('profile')!=PHRASE_PROFILE or phrases.get('branch')!='unesco-mt1-10' or
        phrases.get('locale')!=handoff.get('locale') or phrases.get('view_sha256')!=handoff.get('view_sha256')):
        raise DraftError('Phrase bundle does not belong to this exact v11 view/locale')
    locale=handoff['locale']
    if locale not in LOCALES:raise DraftError('Unknown UNESCO pilot locale')
    items=phrases.get('items')
    if not isinstance(items,dict):raise DraftError('Frozen phrases keyed by KA required')
    selected=handoff.get('selections')
    if not isinstance(selected,list) or not selected:
        raise DraftError('No reviewed KQ selections: refuse to fabricate article identities')
    namespace=handoff.get('namespace_id')
    graph_id=handoff.get('graph_id')
    if not isinstance(namespace,str) or not namespace.strip() or not isinstance(graph_id,str) or not graph_id.strip():
        raise DraftError('Missing actual graph and namespace identity')
    pages={};used=set();semantic_index={}
    for concept in selected:
        cid=concept.get('unesco_id');kid=concept.get('local_kq')
        if not re.fullmatch(r'concept[1-9][0-9]*',str(cid)) or not re.fullmatch(r'KQ[0-9]+',str(kid)):
            raise DraftError('Invalid UNESCO/KQ identity')
        if cid in pages:raise DraftError('Duplicate concept')
        lex=concept.get('lexical')
        if not isinstance(lex,dict) or lex.get('status') not in ('direct','fallback'):
            raise DraftError('Missing realized topic label')
        title=safe_md(lex.get('term'))
        assertions=concept.get('assertions')
        if not isinstance(assertions,list) or not assertions:raise DraftError('Refuse empty semantic article')
        lines=[f'# {title}','',f'> PRIVATE DRAFT — NOT FOR PUBLICATION. Semantic branch unesco-mt1-10. Locale `{locale}`.','',
               f'UNESCO ID: `{cid}` · Canonical referent: `{kid}` · Graph: `{handoff.get("graph_id", "not supplied")}`','',
               '## Structured assertions (source-backed, not independently verified)','']
        for a in assertions:
            aid=a.get('id')
            if not re.fullmatch(r'KA[0-9]+',str(aid)) or aid in used:raise DraftError('Invalid/duplicate KA')
            src=a.get('sources')
            if not isinstance(src,list) or not src or any(not re.fullmatch(r'KS[0-9]+',str(k)) for k in src):
                raise DraftError('Cannot draft unsourced KA')
            v=items.get(aid)
            if not isinstance(v,dict):raise DraftError('Missing frozen realization for '+aid)
            if v.get('channel') not in ('semantik_architect','ai_preconstructed'):
                raise DraftError('Unrecognized realization channel: '+aid)
            # Qualification cannot be asserted by a caller-supplied phrase.
            # No trusted RuntimeSet attestation verifier exists at this edge.
            if v.get('status') not in ('draft','reviewed'):
                raise DraftError('Unattested/qualified realization refused: '+aid)
            if v['channel']=='ai_preconstructed':
                if any(k in v for k in ('runtime_set_id','request_id','gf_function')):
                    raise DraftError('AI text may not claim SemantiK or GF runtime identity: '+aid)
                if not (isinstance(v.get('model_id'),str) and v['model_id'].strip() and
                        isinstance(v.get('generation_ref'),str) and v['generation_ref'].strip() and
                        isinstance(v.get('prompt_sha256'),str) and
                        re.fullmatch(r'(?:sha256:)?[0-9a-f]{64}',v['prompt_sha256'])):
                    raise DraftError('AI realization requires actual generation provenance: '+aid)
                if v['status']=='reviewed':
                    review=v.get('human_review')
                    if not isinstance(review,dict) or review.get('status')!='approved' or not review.get('review_ref'):
                        raise DraftError('Reviewed AI text requires declared external review: '+aid)
            if not isinstance(v.get('provenance_ref'),str) or not v['provenance_ref'].strip():
                raise DraftError('Missing realization provenance: '+aid)
            text=safe_md(v.get('text'))
            lines.extend([f'- {text}  ',f'  - Semantic statement: `{aid}`; evidence: '+', '.join(f'`{e}`' for e in src),
                          f'  - Realization: `{v["channel"]}` / `{v["status"]}` / `{safe_md(v["provenance_ref"])}`',''])
            used.add(aid)
        # A language-independent semantic fingerprint is retained per page.
        # It compares the canonical assertion payload, not translated prose.
        semantic_rows=[{'id':a['id'],'subject':a.get('subject'),
                        'predicate':a.get('predicate'),'object':a.get('object'),
                        'sources':sorted(a['sources'])} for a in assertions]
        semantic_rows.sort(key=lambda a:a['id'])
        canonical=sha(json.dumps({'namespace_id':namespace,'graph_id':graph_id,
                  'unesco_id':cid,'local_kq':kid,'assertions':semantic_rows},
                  sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8'))
        semantic_index[cid]={'local_kq':kid,'assertions_sha256':canonical,
                             'ka_ids':[a['id'] for a in semantic_rows]}
        lines.extend(['---','',f'Private projection of a single branch Kristal. No runtime attestation, semantic C1/C2 approval or redistribution rights were verified.',''])
        pages[cid+'.md']='\n'.join(lines)
    if set(items)!=used:raise DraftError('Unreferenced frozen KA or incomplete article selection')
    manifest={'profile':OUT_PROFILE,'branch':'unesco-mt1-10','locale':locale,
              'namespace_id':namespace,'semantic_graph_id':graph_id,'semantic_view_sha256':handoff['view_sha256'],
              'one_branch_kristal':True,'generated_drafts':len(pages),
              'runtime_attestation_verified':False,'canonical_approval_verified':False,
              'content_rights_verified':False,'public_release_authorized':False,
              'status':'PRIVATE_PREVIEW_ONLY','semantic_index':semantic_index,
              'files':{name:sha(text.encode('utf8')) for name,text in pages.items()}}
    return pages,manifest

def write_private(handoff_path:Path,phrase_path:Path,out:Path):
    h=load(handoff_path);p=load(phrase_path)
    pages,manifest=prepare(h,p)
    out=out.resolve()
    if out.exists() or out.is_symlink() or any((a/'.git').exists() for a in out.parents):
        raise DraftError('New private output directory outside Git required')
    if not out.parent.is_dir():raise DraftError('Output parent must exist')
    stage=Path(tempfile.mkdtemp(prefix='.'+out.name+'-spek-',dir=out.parent))
    try:
        for name,body in pages.items(): (stage/name).write_text(body,encoding='utf8')
        (stage/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
        os.rename(stage,out)
    finally:
        if stage.exists():shutil.rmtree(stage)
    return manifest

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--handoff',type=Path,required=True);p.add_argument('--phrases',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(argv)
    try:
        x=write_private(a.handoff,a.phrases,a.out)
        print(json.dumps({'drafts':x['generated_drafts'],'locale':x['locale'],'publication':'BLOCKED','out':str(a.out)}));return 0
    except (DraftError,ValueError,TypeError,FileExistsError,OSError) as e:
        print(json.dumps({'status':'BLOCKED','error':str(e)}),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
