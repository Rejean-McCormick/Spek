"""Read-only audit of an explicit, non-approved Agriculture v8 SPEK binding.

Does not generate text, templates or page, and cannot authorize publication.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path

SHA='ae3cf84ab47a1ea3c710785f5749c7cacd8274d389f767958c7327c6c1a72918'
STAGES={'soil':79,'crop_organism':75,'inputs':66,'practices':91,'yield':62,'cross':18}
ORDER=['soil','crop','inputs','practices','yield','cross']

def json_file(path:Path):
    if path.is_symlink() or not path.is_file():raise ValueError('Fichier absent ou lien symbolique: '+str(path))
    return json.loads(path.read_text(encoding='utf-8-sig'))

def digest(path:Path):return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(source:Path,binding:Path,audit:Path,spek_root:Path|None=None)->dict:
    if digest(source)!=SHA:raise ValueError('REFUS: snapshot source différent de la revue v8')
    state=json_file(source)
    ass=state.get('assertions',[])
    if (len(ass)!=391 or len({a['assertion_id'] for a in ass})!=391
            or state['artifact_type']!='kristal_state' or state['applicability']['domain']!='agriculture'):
        raise ValueError('REFUS: inventaire source Agriculture incohérent')
    groups=collections.Counter(next((c['value'] for c in a.get('coordinates',[]) if c.get('axis')=='production_stage'),'cross') for a in ass)
    if dict(groups)!=STAGES:raise ValueError('REFUS: catégories du corpus divergentes')
    registered=set(state.get('source_refs',[]))
    if any(set(a.get('evidence_refs',[]))-registered for a in ass):
        raise ValueError('REFUS: evidence_ref non déclarée dans le corpus')
    b=json_file(binding)
    a=json_file(audit)
    if (b['format']!='spek.registry-first-explicit-bridge/1.0'
            or b['kristal_identity']!='agriculture' or b['basis']!='deep_review'
            or b['primary_composition_id']!='arketype-modele-multiplexe'
            or b['source_state']['raw_sha256']!=SHA or b['observed_source']['raw_sha256']!=SHA
            or b.get('publication_authorized') is not False
            or b.get('pages')!=[]
            or b.get('status')!='DRAFT_WITH_CANDIDATE_ASSERTIONS_PENDING_GF_AND_REVIEW'):
        raise ValueError('REFUS: contrat de liaison non approuvée altéré')
    if (a['source_sha256']!=SHA or a['source_count']!=391
            or a.get('gf_rendered') is not False or a.get('publication_authorized') is not False):
        raise ValueError('REFUS: audit source incohérent ou déclaration de qualification abusive')
    if ([s['section_id'] for s in b['sections']]!=ORDER
            or [s['section_id'] for s in a['sections']]!=ORDER):
        raise ValueError('REFUS: sections du registre changées')
    selected=set()
    counts={}
    unsatisfied={}
    for sec,asec in zip(b['sections'],a['sections']):
        sid=sec['section_id']
        if (asec['section_id']!=sid or asec['layout_id']!=sec['layout_id']
                or sec['decision']!='pending' or sec['coverage']!=[]
                or asec.get('metadata_warning_is_not_assertion') is not True):
            raise ValueError('REFUS: section non conforme ou prétendue approuvée: '+sid)
        grouped=asec['slot_candidates']
        candidates=[r for rows in grouped.values() for r in rows]
        if set(grouped)!=( {'context','axes','entries'} if sid in ('inputs','yield') else {'context','entities','relations'}):
            raise ValueError('REFUS: slots candidats incompatibles: '+sid)
        if ([r['assertion_id'] for r in candidates]!=sec['source_assertion_ids']
                or [r['source_pointer'] for r in candidates]!=sec['semantic_source_paths']):
            raise ValueError('REFUS: pointeurs de liaison et audit divergents: '+sid)
        for r in candidates:
            idx=r['source_index_zero_based']
            if (not isinstance(idx,int) or idx<0 or idx>=len(ass)
                    or r['source_pointer']!=f'#/assertions/{idx}' or idx in selected):
                raise ValueError('REFUS: index invalide ou double sélection')
            selected.add(idx)
            original=ass[idx]
            fields={'assertion_id':original['assertion_id'],
                    'predicate':original['statement']['predicate'],
                    'subject':original['statement']['subject'],
                    'object':original['statement']['object'],
                    'evidence_refs':original['evidence_refs'],
                    'record_role':original['record_role'],
                    'assertion_status':original['assertion_status']}
            for key,val in fields.items():
                if r[key]!=val:raise ValueError('REFUS: assertion candidate non fidèle au corpus: '+key)
            original_stage=next((c['value'] for c in original.get('coordinates',[]) if c.get('axis')=='production_stage'),None)
            if r['original_production_stage']!=original_stage:raise ValueError('REFUS: origine de section différente')
            if sid!='cross' and original_stage!=({'crop':'crop_organism'}.get(sid,sid)):
                raise ValueError('REFUS: assertion hors de sa section revue')
        counts[sid]=len(candidates)
        if spek_root is not None:
            layout_file=spek_root/'layouts'/(sec['layout_id']+'.json')
            layout=json_file(layout_file)
            if layout['id']!=sec['layout_id']:
                raise ValueError('REFUS: contrat de layout contradictoire')
            missing=[]
            for slot,contract in layout['slots'].items():
                n=len(grouped.get(slot,[]))
                if n<contract['min']:
                    missing.append({'slot':slot,'present':n,'required_min':contract['min']})
                if n>contract['max']:
                    raise ValueError('REFUS: trop de candidats au slot '+sid+'/'+slot)
            unsatisfied[sid]=missing
        else:
            unsatisfied[sid]=[{'slot':'limits','present':0,'required_min':1}]
    if (len(selected)!=a['selected_unique_assertion_ids']
            or len(selected)!=sum(len(s['source_assertion_ids']) for s in b['sections'])
            or len(selected)+a['unselected_assertion_count']!=391):
        raise ValueError('REFUS: couverture numérique incohérente')
    if not all(unsatisfied.values()):
        raise ValueError('REFUS: audit ne peut déclarer silencieusement un layout complet')
    return {
        'status':'SOURCE_V8_CANDIDATE_INTEGRITY_VERIFIED_NOT_BUILDABLE',
        'snapshot_sha256':SHA,'source_assertions':len(ass),
        'candidate_unique_assertions':len(selected),
        'selected_by_section':counts,
        'layout_slots_missing':unsatisfied,
        'all_pages_realized_by_GF':False,
        'editorial_approval':False,'publication_authorized':False,
    }

def main():
    ap=argparse.ArgumentParser(description='Vérification en lecture seule de la candidature SPEK Agriculture v8')
    ap.add_argument('--source',required=True,type=Path)
    ap.add_argument('--binding',type=Path,default=Path(__file__).with_name('liaison-agriculture-v8-CANDIDATE-NON-APPROUVEE.json'))
    ap.add_argument('--audit',type=Path,default=Path(__file__).with_name('audit-candidats-assertions-v8.json'))
    ap.add_argument('--spek-root',type=Path)
    args=ap.parse_args()
    try:
        report=verify(args.source,args.binding,args.audit,args.spek_root)
    except (ValueError,OSError,KeyError,TypeError,json.JSONDecodeError) as e:
        ap.exit(2, 'REFUS AUDIT : '+str(e)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
