"""Project explicitly mapped, reviewed Spek realizations into reader sidecars.

Mapping JSON: {"format":"konstellation.multilingual-mapping/1.0", "slug":"...",
"state_ref":"...", "surface_digest":"sha256:...", "bindings":[
  {"node_id":"KQ...", "locale":"fr", "definition_key":"...",
   "label_key":"...", "review_ref":"explicit-editor-review"}]}
Only keys explicitly selected by the operator are read. No automatic text creation.
"""
import argparse
import json
from pathlib import Path
from contract import ContractError,new_document,save

def export(realizations,mapping):
    if realizations.get('format')!='kristal.layout-realizations/0.1' or not isinstance(realizations.get('entries'),dict):
        raise ContractError('Spek realizations required')
    if mapping.get('format')!='konstellation.multilingual-mapping/1.0':raise ContractError('Invalid mapping')
    grouped={}
    for binding in mapping['bindings']:
        locale=binding['locale']
        row={'node_id':binding['node_id']}
        refs=list(binding.get('source_refs') or [])
        for field,key_name in [('label','label_key'),('definition','definition_key')]:
            if key_name not in binding:continue
            key=binding[key_name]
            v=realizations['entries'].get(key,{}).get(locale)
            if not isinstance(v,dict) or v.get('status') not in ('reviewed','qualified'):
                raise ContractError(f'Unreviewed or missing Spek realization: {key}/{locale}')
            if v.get('status')=='qualified' and v.get('channel')!='semantik_architect':
                raise ContractError('Qualified text cannot be asserted for non-SemantiK channel')
            row[field]=v['text'];
            if field=='label':refs.append('spek:label:'+key)
        if 'label' not in row and 'definition' not in row:raise ContractError('Binding without fields')
        if 'definition' in row and not binding.get('source_refs'):raise ContractError('Definition requires explicit source_refs')
        if not binding.get('review_ref'):raise ContractError('External editorial review_ref required')
        row['provenance']={'provider':'spek','source_refs':refs,'review_status':'reviewed','review_ref':binding['review_ref']}
        grouped.setdefault(locale,[]).append(row)
    return {locale:new_document(mapping['slug'],mapping['state_ref'],mapping['surface_digest'],locale,rows)
            for locale,rows in grouped.items()}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['realizations','mapping','out']:ap.add_argument('--'+k,required=True)
    a=ap.parse_args()
    result=export(json.loads(Path(a.realizations).read_text(encoding='utf-8')),
                  json.loads(Path(a.mapping).read_text(encoding='utf-8')))
    for locale,doc in result.items():
        print(save(Path(a.out)/doc['slug']/(locale+'.json'),doc))
