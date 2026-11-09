#!/usr/bin/env python3
"""41 apercus editoriaux anglais, depuis les decisions privees uniquement.

Ce ne sont pas des projections du Kristal canonique ni des realisations GF.
"""
from __future__ import annotations
from collections import defaultdict
import re
class PreviewError(ValueError): pass

def esc(text):
    if not isinstance(text,str) or not text.strip() or len(text)>12000 or any(ord(c)<32 and c not in '\n\t' for c in text):
        raise PreviewError('Texte absent, trop grand ou invalide')
    return re.sub(r'([\\`*_{}\[\]()<>#+!|])',r'\\\1',' '.join(text.split()))

def compose(decision_bundle):
    if (decision_bundle.get('branch')!='unesco-mt1-10' or decision_bundle.get('editorial_decisions_count')!=191
            or decision_bundle.get('admission_to_canon_authorized') is not False):
        raise PreviewError('Contrat editorial refuse')
    items=decision_bundle['decisions']; ident={x['ref']:x for x in items if x['type']=='IDENTITE'}
    props=defaultdict(list); rels=defaultdict(list)
    for x in items:
        if x['type']=='PROPOSITION':props[x['unesco_id']].append(x)
        elif x['type']=='SKOS_INTERNE':
            rels[x['source_unesco_id']].append(x)
    if len(ident)!=41 or len([x for x in items if x['type']=='PROPOSITION'])!=85:raise PreviewError('Cardinalite invalide')
    files={}
    for cid,info in sorted(ident.items()):
        if not re.fullmatch(r'concept[1-9][0-9]*',cid) or not info['source_uri'].endswith('/'+cid):
            raise PreviewError('Ancre concept invalide')
        if not props[cid]:raise PreviewError('Concept sans proposition: '+cid)
        lines=[f'# {esc(info["label_en"])}','','> PRIVATE AI EDITORIAL PREVIEW — NOT A CANONICAL KRISTAL PROJECTION.','',
               f'UNESCO thesaurus anchor: `{cid}` — {esc(info["source_uri"])}','',
               '## Candidate overview (not independently attested)','']
        for p in props[cid]:
            if p.get('evidence_status')!='NOT_ATTESTED':raise PreviewError('Preuve non attendue')
            lines.append(f'- {esc(p["chosen_text_en"])}  ')
            lines.append(f'  - Proposal: `{p["ref"]}`; editorial status: `{p["decision_editoriale"]}`; KS: **not attested**')
        if rels[cid]:
            lines.extend(['','## Observed thesaurus relations (not canonical properties)',''])
            for r in rels[cid]:
                lines.append(f'- `{r["relation_skos"]}` — `{r["target_unesco_id"]}` (source observation `{r["ref"]}`)')
        lines.extend(['','---','This is a private editorial working paper. No KQ/KP/KA/KS has been minted or approved.','No GF RuntimeSet, multilingual realization, distribution right, or GitHub publication gate has been qualified.',''])
        files[f'apercus_en/{cid}.md']='\n'.join(lines).encode('utf8')
    if len(files)!=41:raise PreviewError('41 apercus attendus')
    return files
