#!/usr/bin/env python3
"""Offline, private English reading surface from editorial candidates only.

This is not the GF or canonical Kristal projection engine. No translations or
published articles are fabricated. Output is local, static and labelled.
"""
from __future__ import annotations
from collections import defaultdict
from html import escape
import json
import re

class ReaderError(ValueError):pass

def build(graph:dict,identities:dict):
    if graph.get('branch')!='unesco-mt1-10' or graph.get('canonical_graph_built') is not False:
        raise ReaderError('Graphe prive requis')
    nodes=graph.get('nodes',[]);statements=graph.get('candidate_statements',[]);links=graph.get('skos_internal_observations',[])
    if (len(nodes),len(statements),len(links))!=(41,85,61):raise ReaderError('Cardinalite invalide')
    mapped={x['unesco_id']:x for x in identities.get('concepts',[])}
    if len(mapped)!=41:raise ReaderError('41 KQ provisoires attendus')
    by_concept=defaultdict(list);by_link=defaultdict(list);node_ids={x['unesco_id'] for x in nodes}
    for s in statements:
        if s.get('unesco_id') not in node_ids or s.get('evidence_status')!='NOT_ATTESTED':
            raise ReaderError('Texte non trace ou fausse preuve')
        by_concept[s['unesco_id']].append(s)
    for link in links:
        if link.get('source') not in node_ids or link.get('target') not in node_ids:
            raise ReaderError('Lien SKOS externe en interne')
        by_link[link['source']].append(link)
    files={};rows=[];titles={n['unesco_id']:n['label_en'] for n in nodes}
    css='body{font:17px/1.6 system-ui,sans-serif;max-width:850px;margin:2rem auto;padding:0 1rem;color:#152335}a{color:#1553a7}small,.dim{color:#526071}.notice{padding:1rem;border:1px solid #b7a56d;background:#fffaf0}li{margin-bottom:.75rem}header{border-bottom:1px solid #ccd1db}code{font-size:.82em}'
    for n in sorted(nodes,key=lambda x:x['unesco_id']):
        cid=n['unesco_id']; title=n['label_en'];kq=mapped[cid]['provisional_KQ'];qid=mapped[cid]['qid_candidate_unapproved']
        if not re.fullmatch(r'concept[1-9][0-9]*',cid) or not by_concept[cid]:raise ReaderError('Concept sans proposition')
        parts=['<!doctype html>','<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
          '<title>'+escape(title)+'</title>','<style>'+css+'</style>','<body><header><p><a href="index.html">UNESCO Educational Policy / private preview</a></p></header>',
          '<h1>'+escape(title)+'</h1>',
          '<div class="notice"><strong>Private editorial draft — not a canonical Kristal projection.</strong> Statements require qualified sources (KS), canonical approval and GF realization before publication.</div>',
          '<p><small>UNESCO anchor: <code>'+escape(cid)+'</code> · Provisional KQ: <code>'+escape(kq)+'</code> · Wikidata candidate: '+escape(qid or 'none')+'</small></p>',
          '<h2>Editorial statements (unattested)</h2><ol>']
        for stmt in by_concept[cid]:
            chosen=stmt.get('editorial_selected_en')
            if not isinstance(chosen,str) or not chosen.strip():raise ReaderError('Texte vide')
            parts.append('<li>'+escape(chosen)+' <small>[proposal '+escape(str(stmt['proposal_ref']))+'; KS not attested]</small></li>')
        parts.append('</ol><h2>Observed thesaurus relations (not KA)</h2><ul>')
        for relation in by_link[cid]:
            dest=relation['target']
            parts.append('<li>'+escape(str(relation['relation']))+' → <a href="'+dest+'.html">'+escape(titles[dest])+'</a></li>')
        parts.append('</ul><footer><small>Generated offline from local editorial files. Not released. No publication or authorization implied.</small></footer></body></html>')
        files['reader_en/'+cid+'.html']='\n'.join(parts).encode('utf-8')
        rows.append({'unesco_id':cid,'title_en':title,'provisional_KQ':kq,'qid_candidate':qid,
                     'editorial_statement_count':len(by_concept[cid]),'local_page':'reader_en/'+cid+'.html',
                     'canonical_article':False,'GF_realized':False,'publication_authorized':False})
    idx=['<!doctype html>','<html lang="en"><meta charset="utf-8"><title>UNESCO Educational Policy — private previews</title>',
       '<style>'+css+'</style><body><h1>UNESCO Educational Policy</h1>',
       '<div class="notice">41 private English editorial previews. NOT canonical articles, GF realizations or public release.</div>',
       '<ol>']
    for r in rows: idx.append('<li><a href="'+r['unesco_id']+'.html">'+escape(r['title_en'])+'</a> <small>('+r['unesco_id']+')</small></li>')
    idx.append('</ol></body></html>')
    files['reader_en/index.html']='\n'.join(idx).encode('utf-8')
    files['reader_en/catalogue.json']=(json.dumps({'format':'koa.unesco-v17-private-reader/1.0','branch':'unesco-mt1-10','articles_generated':0,
        'private_previews':rows,'public_release_authorized':False},ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode('utf-8')
    if len(files)!=43:raise ReaderError('41 pages + 2 index attendus')
    return files
