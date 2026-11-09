"""Nonpublishable UNESCO Educational Policy / 14-language projection work queue.

Consumes EncyKlopedia's *private* candidate inventory. Does not draft prose,
translate Wikipedia, certify KQ/KP/KA/KS, or invoke publication workflows.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,sys,tempfile
from pathlib import Path

PROFILE_IN = 'encyklopedia.unesco-local-wikipedia-handoff/1.0'
PROFILE_OUT = 'spek.unesco-mt1-10-private-projection-queue/1.0'
LOCALES=('en','fr','es','de','nl','sv','da','no','nn','fi','et','af','it','pt')
CID=re.compile(r'^concept[1-9][0-9]*$')


class PlanningError(ValueError):pass


def build_queue(data:dict, *,source_sha256:str):
    if not isinstance(data,dict) or data.get('profile')!=PROFILE_IN:
        raise PlanningError('Input is not the explicitly qualified *type* of private handoff')
    if data.get('branch')!='unesco-mt1-10' or data.get('semantic_grain')!='one_branch_kristal':
        raise PlanningError('Wrong branch or semantic granularity')
    if data.get('not_canonical') is not True or data.get('not_publication') is not True or data.get('approval_status')!='BLOCKED':
        raise PlanningError('Unexpected canonical or publication authorization in candidate handoff')
    if data.get('wiki_content_extracted') is not False or data.get('wikidata_mapping_approval') is not False:
        raise PlanningError('Unrecognized evidence status; refuse content or approved crosswalk assertions')
    if data.get('languages')!=list(LOCALES) or data.get('article_count')!=0:
        raise PlanningError('The 14-language candidate pilot must not contain an article corpus')
    records=data.get('records')
    if not isinstance(records,list) or len(records)!=41:
        raise PlanningError('Expected exactly 41 source concept records')
    names=set();jobs=[]
    for record in records:
        cid=record.get('unesco_id')
        if not isinstance(cid,str) or not CID.fullmatch(cid) or cid in names:
            raise PlanningError('Invalid/repeated UNESCO source concept identity')
        names.add(cid)
        if record.get('canonical_KQ') is not None or record.get('canonical_KA') or record.get('canonical_KS'):
            raise PlanningError('Unexpected canonical identity or assertion in research inventory')
        if record.get('article_projection_status')!='not_generated':
            raise PlanningError('Unexpected generated article in research inventory')
        wiki=record.get('wikidata') or {}
        if wiki.get('canonical_exact_match') is not False or wiki.get('match_status') not in ('unreviewed_candidate','none'):
            raise PlanningError('Wikidata candidate was incorrectly promoted')
        languages=record.get('language_channels')
        if not isinstance(languages,dict) or set(languages)!=set(LOCALES):
            raise PlanningError('Incomplete or unexpected language channels')
        for loc in LOCALES:
            lex=languages[loc]
            if lex.get('label_status') not in ('source_label_present','missing'):
                raise PlanningError('Illegal lexical approval/qualification status')
            jobs.append({
                'unesco_id':cid,'locale':loc,
                'lexical_source_label_present':lex['label_status']=='source_label_present',
                'semantic_graph_review':'MISSING',
                'qualified_realization':'MISSING',
                'source_licensing_review':'MISSING',
                'article_built':False,
                'publication_authorized':False,
                'status':'BLOCKED_PENDING_CANONICAL_AND_LANGUAGE_REVIEW',
            })
    return {'profile':PROFILE_OUT,'branch':'unesco-mt1-10','source_sha256':source_sha256,
            'one_branch_kristal':True,'concept_count':41,'language_count':len(LOCALES),
            'projection_queue_size':len(jobs),'generated_articles':0,
            'approved_assertions':0,'public_release_authorized':False,
            'publication_status':'BLOCKED','jobs':jobs}


def read_inventory(path:Path):
    if not path.is_file() or path.stat().st_size>4_000_000:
        raise PlanningError('Missing or oversized private inventory')
    source=path.read_bytes()
    return json.loads(source),hashlib.sha256(source).hexdigest()


def write_private_new_file(dest:Path, data:dict):
    dest=dest.resolve()
    for ancestor in (dest.parent,*dest.parents):
        if (ancestor/'.git').exists():raise PlanningError('Refuse writing in Git working tree')
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():raise PlanningError('Existing destination cannot be overwritten')
    fd,temp=tempfile.mkstemp(prefix='.spek_unesco_',suffix='.tmp',dir=dest.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf8') as f:
            json.dump(data,f,ensure_ascii=False,sort_keys=True,indent=2)
            f.write('\n');f.flush();os.fsync(f.fileno())
        if dest.exists():raise PlanningError('Destination appeared during generation')
        os.replace(temp,dest)
    finally:
        if os.path.exists(temp):os.unlink(temp)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inventory',required=True,type=Path)
    p.add_argument('--out',type=Path,help='Private JSON outside Git (omit for plan-only summary)')
    a=p.parse_args(argv)
    try:
        data,digest=read_inventory(a.inventory)
        result=build_queue(data,source_sha256=digest)
        if a.out:write_private_new_file(a.out,result)
        print(json.dumps({'branch':result['branch'],'projection_slots':len(result['jobs']),
                          'articles_generated':0,'publication':'BLOCKED',
                          'out':str(a.out) if a.out else None},ensure_ascii=False))
        return 0
    except (PlanningError,ValueError,KeyError,TypeError) as e:
        print(json.dumps({'status':'BLOCKED','error':str(e)},ensure_ascii=False),file=sys.stderr)
        return 2

if __name__=='__main__':raise SystemExit(main())
