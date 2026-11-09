"""Portable contract for OPTIONAL multilingual reading annotations.

This does not verify editor authority, source truth, grammar, C1/C2/C3/C4, or
change any canonical Kristal. Used by local integration adapters only.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
FORMAT = 'konstellation.multilingual-read/1.0'
LOCALE = re.compile(r'[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*\Z')
SLUG = re.compile(r'[a-z0-9][a-z0-9-]{0,99}\Z')
SHA = re.compile(r'sha256:[0-9a-f]{64}\Z')
PROVIDERS = {'dik', 'semantik_architect', 'spek', 'editorial'}

class ContractError(ValueError): pass

def _text(x, limit, multiline=False):
    return isinstance(x, str) and 0 < len(x.strip()) <= limit and not any((ord(c) < 32 and (not multiline or c not in '\n\r')) or ord(c) == 127 for c in x)

def validate(doc, *, require_reviewed=False):
    if not isinstance(doc, dict) or not {'format','slug','state_ref','surface_digest','locale','authority','entries'}<=set(doc) or set(doc)-{'format','slug','state_ref','surface_digest','locale','authority','entries','relations'}:
        raise ContractError('Unexpected multilingual document keys')
    if doc['format'] != FORMAT or doc['authority'] != 'derived_non_authoritative':
        raise ContractError('Unknown multilingual format/authority')
    if not isinstance(doc['slug'], str) or not SLUG.fullmatch(doc['slug']):
        raise ContractError('Invalid slug')
    if not _text(doc['state_ref'],300) or not isinstance(doc['surface_digest'], str) or not SHA.fullmatch(doc['surface_digest']):
        raise ContractError('Invalid state/digest')
    if not isinstance(doc['locale'], str) or not LOCALE.fullmatch(doc['locale']):
        raise ContractError('Invalid locale')
    rows=doc['entries']
    if not isinstance(rows,list) or len(rows)>12000:raise ContractError('Invalid entries')
    seen=set()
    for row in rows:
        if not isinstance(row,dict) or not {'node_id','provenance'}<=set(row) or set(row)-{'node_id','label','definition','provenance'}:
            raise ContractError('Invalid entry')
        if not _text(row['node_id'],300) or row['node_id'] in seen:raise ContractError('Invalid/duplicate node id')
        seen.add(row['node_id'])
        if 'label' not in row and 'definition' not in row:raise ContractError('Entry without readable content')
        for k,limit in [('label',600),('definition',4000)]:
            if k in row and not _text(row[k],limit,multiline=(k=='definition')):raise ContractError('Invalid '+k)
        p=row['provenance']
        if not isinstance(p,dict) or not {'provider','source_refs','review_status'}<=set(p) or set(p)-{'provider','source_refs','review_status','review_ref','runtime_set_id'}:
            raise ContractError('Invalid provenance keys')
        if p['provider'] not in PROVIDERS or p['review_status'] not in {'candidate','reviewed'}:
            raise ContractError('Invalid provenance status')
        if p['review_status']=='reviewed' and not _text(p.get('review_ref'),300):
            raise ContractError('Reviewed entry requires review_ref')
        if require_reviewed and p['review_status']!='reviewed':raise ContractError('Unreviewed entry forbidden in reader')
        if not isinstance(p['source_refs'],list) or len(p['source_refs'])>80 or ('definition' in row and not p['source_refs']) or any(not _text(v,300) for v in p['source_refs']):
            raise ContractError('Invalid source references')
        for k in ['review_ref','runtime_set_id']:
            if k in p and not _text(p[k],300):raise ContractError('Invalid '+k)
    relations=doc.get('relations',[])
    if not isinstance(relations,list) or len(relations)>5000:raise ContractError('Invalid relation labels')
    seen_rel=set()
    for row in relations:
        if not isinstance(row,dict) or set(row)!={'relation_id','label','provenance'}:
            raise ContractError('Invalid relation entry')
        rid=row['relation_id']
        if not _text(rid,180) or rid in seen_rel or not _text(row['label'],600):
            raise ContractError('Duplicate or invalid relation id/label')
        seen_rel.add(rid)
        pr=row['provenance']
        if (not isinstance(pr,dict) or pr.get('review_status') not in {'candidate','reviewed'} or
            pr.get('provider') not in PROVIDERS or not isinstance(pr.get('source_refs'),list) or
            len(pr['source_refs'])>80 or any(not _text(v,300) for v in pr['source_refs']) or
            set(pr)-{'provider','source_refs','review_status','review_ref','runtime_set_id'}):
            raise ContractError('Invalid relation provenance')
        if pr['review_status']=='reviewed' and not _text(pr.get('review_ref'),300):
            raise ContractError('Reviewed relation requires review_ref')
        if require_reviewed and pr['review_status']!='reviewed':raise ContractError('Unreviewed relation forbidden')
    return doc

def new_document(slug,state_ref,surface_digest,locale,entries,relations=None):
    doc={'format':FORMAT,'slug':slug,'state_ref':state_ref,'surface_digest':surface_digest,
                     'locale':locale,'authority':'derived_non_authoritative','entries':entries}
    if relations:doc['relations']=relations
    return validate(doc)

def save(path, doc):
    validate(doc)
    path=Path(path)
    if path.exists():raise ContractError('Refusing to overwrite an existing multilingual document')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(doc,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return path
