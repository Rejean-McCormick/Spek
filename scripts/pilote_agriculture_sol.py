"""Lecture privée, source-littérale, du pilote Agriculture/Sol.

Ne remplace ni le renderer SPEK, ni SemantiK, ni une revue éditoriale.
Ce script fournit seulement la première inspection de SOURCE et vérifie
les prérequis avant le véritable build de composition SPEK/GF existant.
"""
from __future__ import annotations

import argparse
import hashlib
from html import escape
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any

FORMAT = "spek.agriculture-source-literal-preview/1.0"
EXPECTED_GRAPH_SHA256 = "d35ac9409c2457b1bcc7e60a697e5b05863d52498cfae8d8a5a8aad8de325026"
GRAPH_SCHEMA = "11.0"
DEFINITION_PROPERTY = "KP16213057290867159002953"
MAX_SOURCE_BYTES = 3_000_000
# Ces décisions d'ORDRE DE LECTURE sont des choix éditoriaux candidats,
# et ne sont PAS des assertions canoniques ni des choix du runtime SPEK.
SECTIONS = (
    ("Structure et conditions du sol", (
        ("Fertilité", "KA15833957396088538396077"),
        ("Organisation physique", "KA738539793958188491641886"),
        ("Profil vertical", "KA296553465465957478049147"),
        ("Circulation de l’air", "KA240516812867821829502603"),
        ("Densité et compaction", "KA5164259585077693864152"),
    )),
    ("Eau, nutriments et racines", (
        ("Eau retenue", "KA660781382282183172547388"),
        ("Eau accessible à la plante", "KA806988109313094652212691"),
        ("Zone racinaire", "KA258842896490376399981850"),
        ("Acidité et alcalinité", "KA277661942795860714628178"),
        ("Système sol–culture", "KA697517656684268215683802"),
    )),
    ("Vie du sol et matière organique", (
        ("Organismes du sol", "KA542140816375926807808441"),
        ("Activités microbiennes", "KA828705007546891185353903"),
        ("Carbone organique", "KA299461914893189106605266"),
    )),
    ("Gestion, protection et limites", (
        ("Amendement organique", "KA1051702346989764550583504"),
        ("Couvert végétal", "KA137629190216722949581529"),
        ("Érosion", "KA390348975555570256218409"),
        ("Salinisation", "KA734126844246091880720863"),
        ("Opérations et état du sol", "KA201304371479732671849444"),
    )),
)


class PreviewError(ValueError):
    pass


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_assertions(path: Path) -> tuple[dict[str, dict], bytes]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_SOURCE_BYTES:
        raise PreviewError("Graphe source absent, symbolique ou trop volumineux")
    raw = path.read_bytes()
    if sha(raw) != EXPECTED_GRAPH_SHA256:
        raise PreviewError("Empreinte de graphe divergente : révision différente, revue requise")
    try:
        graph = json.loads(raw)
    except (ValueError,UnicodeError) as exc:
        raise PreviewError("Graphe source non lisible") from exc
    if (not isinstance(graph,dict) or graph.get("schema_version")!=GRAPH_SCHEMA
            or graph.get("artifact_type")!="kristal_semantic_graph"
            or not isinstance(graph.get("assertions"),list)):
        raise PreviewError("Graphe v11 non conforme")
    keyed = {}
    for a in graph["assertions"]:
        if not isinstance(a,dict) or not isinstance(a.get("id"),str) or a["id"] in keyed:
            raise PreviewError("Assertions absentes, invalides ou dupliquées")
        keyed[a["id"]] = a
    if len(keyed) != 408:
        raise PreviewError("Nombre d'assertions différent de la source examinée")
    return keyed, raw


def selected_text(keyed: dict[str,dict]) -> list[dict]:
    results = []
    seen = set()
    for section_index,(heading, entries) in enumerate(SECTIONS):
        for label, assertion_id in entries:
            if assertion_id in seen:
                raise PreviewError("Sélection éditoriale dupliquée")
            seen.add(assertion_id)
            a = keyed.get(assertion_id)
            if not isinstance(a,dict) or a.get("predicate") != DEFINITION_PROPERTY:
                raise PreviewError("Référence de définition inexistante ou hors de la propriété attendue")
            obj = a.get("object")
            if (not isinstance(obj,dict) or obj.get("kind") != "literal"
                    or obj.get("language") != "fr" or obj.get("datatype") != "string"
                    or not isinstance(obj.get("value"),str) or not obj["value"].strip()):
                raise PreviewError("Définition source française manquante")
            sources = a.get("sources",[])
            if not isinstance(sources,list) or not sources or any(not isinstance(x,str) for x in sources):
                raise PreviewError("Provenance d'assertion absente")
            results.append({"section": section_index,"heading": heading,"editorial_label":label,
                            "id":assertion_id,"subject":a.get("subject"),
                            "text":obj["value"],"sources":sources})
    return results


def _safe_out(out: Path, root: Path | None = None) -> Path:
    out = out.expanduser().absolute()
    for node in (out,*out.parents):
        if node.is_symlink():
            raise PreviewError("Chemin de sortie symbolique interdit")
    dest = out.resolve(strict=False)
    if dest.exists():
        raise PreviewError("Dossier de sortie déjà présent : écriture interdite")
    if root is not None and dest.is_relative_to(root.resolve()):
        raise PreviewError("Aperçu privé interdit à l'intérieur du dépôt SPEK")
    if any((p/".git").exists() for p in dest.parents):
        raise PreviewError("Aperçu privé interdit dans un dépôt Git")
    if not dest.parent.is_dir():
        raise PreviewError("Créer d'abord le répertoire parent privé de destination")
    return dest


def _md_quote(s: str) -> str:
    # Une citation source brute est toujours du texte ; jamais du markup.
    return s.replace('\\','\\\\').replace('<','&lt;').replace('>','&gt;').replace('\n',' ').replace('\r',' ')


def _render_html(rows: list[dict]) -> str:
    nav = ''.join(f'<a href="#g{i}">{escape(h)}</a>' for i,(h,_) in enumerate(SECTIONS))
    sections=[]
    for i,(heading,entries) in enumerate(SECTIONS):
        cards=[]
        for row in [v for v in rows if v['section']==i]:
            cards.append('<section class="fact"><p class="kicker">Libellé éditorial provisoire</p>'
                +'<h3>'+escape(row['editorial_label'])+'</h3>'
                +'<blockquote>'+escape(row['text'])+'</blockquote>'
                +'<p class="source-tag">Extrait littéral d’une assertion v11 candidate, références vérifiables dans l’audit privé.</p></section>')
        sections.append(f'<section class="chapter" id="g{i}"><h2>{escape(heading)}</h2>'
                        +'<div class="cards">'+''.join(cards)+'</div></section>')
    return ('<!doctype html>\n<html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow,noarchive">'
        '<title>Agriculture — Sol | inspection privée des sources</title>'
        '<style>:root{color-scheme:light;--ink:#16312e;--muted:#526b65;--green:#1e6864;--line:#d5e5df;--bg:#f5f8f6}'
        '*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 system-ui,Segoe UI,sans-serif}'
        'header{background:#103f3b;color:white;padding:3rem max(1rem,calc((100vw - 1050px)/2)) 3.5rem}'
        'header .eyebrow{font-size:.8rem;letter-spacing:.12em;text-transform:uppercase;color:#c6ebe1}'
        'h1{font-size:clamp(2.4rem,5vw,4.3rem);line-height:1.07;margin:.4rem 0 1rem;font-weight:750}'
        '.lede{max-width:760px;color:#e1f4ee;font-size:1.1rem}main{max-width:1050px;margin:auto;padding:2rem 1.25rem 4rem}'
        '.notice{border-left:5px solid #a65c17;background:#fff6e9;padding:1rem 1.3rem;margin:0 0 1.8rem}'
        'nav{display:flex;flex-wrap:wrap;gap:.6rem;margin:1rem 0 2.5rem}nav a{display:inline-block;border:1px solid var(--line);'
        'padding:.5rem .8rem;border-radius:22px;color:var(--green);background:white;text-decoration:none;font-size:.9rem}'
        'nav a:hover{text-decoration:underline}.chapter{padding:1rem 0 2rem;border-top:1px solid var(--line)}h2{font-size:1.65rem;line-height:1.2}'
        '.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(275px,1fr));gap:1rem}'
        '.fact{border:1px solid var(--line);background:white;padding:1.35rem;border-radius:10px;box-shadow:0 3px 15px #123c3210}'
        '.kicker{text-transform:uppercase;font-size:.64rem;letter-spacing:.1em;color:var(--muted);margin:0}.fact h3{margin:.2rem 0 .7rem;color:var(--green);font-size:1.11rem}'
        'blockquote{border:0;margin:0;font-size:1rem}.source-tag{font-size:.75rem;color:var(--muted);margin:1rem 0 0}'
        '.method{border:1px solid var(--line);background:white;padding:1.3rem 1.5rem;border-radius:9px}'
        'a{color:var(--green)}footer{font-size:.82rem;color:var(--muted);margin-top:2rem}'
        '@media print{header{color:#222;background:white;padding:1rem}body{background:white}.fact{break-inside:avoid;box-shadow:none}}</style></head><body>'
        '<header><p class="eyebrow">Kristal Agriculture · Collection documentaire</p><h1>Le sol</h1>'
        '<p class="lede">Définitions sourcées et regroupées pour inspection éditoriale. Les textes ci-dessous sont reproduits '
        'à partir d’une révision candidate du graphe v11.</p></header><main><article>'
        '<div class="notice"><strong>APERÇU PRIVÉ — NON PUBLIABLE.</strong> '
        'Cette page n’est <strong>pas</strong> une génération GF, ni un article scientifique approuvé. '
        'Les intitulés de rubrique et de carte sont des propositions de composition, non des noms canoniques validés. '
        'Les relations de causalité et les liens rhétoriques restent à examiner.</div>'
        '<p><strong>Orientation documentaire du Kristal :</strong> Sol → organisme cultivé → intrants → pratiques → rendement. '
        'Cet ordre sert à la navigation et ne constitue pas une chaîne causale déterministe.</p>'
        '<nav aria-label="Rubriques">'+nav+'</nav>'+''.join(sections)
        +'<section class="chapter" id="method"><h2>Provenance et portée</h2><div class="method">'
        '<p><strong>Source examinée :</strong> Kristal-Agriculture, révision v11.1 candidate datée du 27 octobre 2026. '
        'Les 18 extraits sont copiés sans traduction ni reformulation des assertions originales. '
        'Un audit privé relie chaque extrait à son identifiant d’assertion, son sujet et ses références de provenance.</p>'
        '<p><strong>À faire pour une véritable publication SPEK :</strong> sélection éditoriale approuvée, '
        'requêtes SemantiK qualifiées, réalisation GF/PGF de toutes les unités, revue sémantique et linguistique, '
        'puis autorisations C1/C2/C3 et contrôle Publisher.</p></div></section></article>'
        '<footer>Page statique de contrôle éditorial, construite en lecture seule. Aucun accès réseau, aucune publication.</footer></main></body></html>\n')


def build_preview(graph_path: Path, out: Path, *, spek_root: Path | None = None) -> dict:
    keyed,raw = source_assertions(Path(graph_path))
    rows = selected_text(keyed)
    dest = _safe_out(Path(out), Path(spek_root) if spek_root is not None else None)
    html=_render_html(rows)
    md_parts=['# Le sol — inspection privée de sources','',
        '> APERÇU PRIVÉ, NON PUBLIABLE. Textes source littéraux, sans réalisation GF et sans approbation éditoriale.','',
        'Orientation documentaire : Sol → organisme cultivé → intrants → pratiques → rendement.',
        'Cette orientation ne déclare aucune causalité déterministe.','']
    for i,(heading,entries) in enumerate(SECTIONS):
        md_parts.extend(['## '+heading,''])
        for r in [r for r in rows if r['section']==i]:
            md_parts.extend(['### '+r['editorial_label'],'', '> '+_md_quote(r['text']),''])
    md_parts.extend(['## Statut','',
        'Révision candidate non qualifiée. Aucune réalisation GF, aucune autorisation de publication.',''])
    audit={"format":FORMAT,"status":"PRIVATE_SOURCE_LITERAL_NOT_GF_NOT_PUBLISHABLE",
           "source":{"kind":"kristal_v11_candidate_graph","sha256":sha(raw),"size_bytes":len(raw),
                     "assertions_in_graph":len(keyed),"active_qualified_release":False},
           "selected":[{"section":r['heading'],"editorial_label":r['editorial_label'],
                        "assertion_id":r['id'],"subject":r['subject'],"source_ids":r['sources'],
                        "literal_sha256":sha(r['text'].encode('utf-8'))} for r in rows],
           "selected_count":len(rows),"template_target":"wiki.domain-primer-source-bound@1.0.0",
           "actual_spek_template_engine_executed":False,"semantik_gf_executed":False,
           "editorial_approval":False,"c1_c2_c3":False,"publication_authorized":False}
    with tempfile.TemporaryDirectory(prefix=".agriculture-source-preview-",dir=dest.parent) as tmp:
        site=Path(tmp)/'site';site.mkdir()
        (site/'index.html').write_text(html,encoding='utf-8')
        (site/'page.md').write_text('\n'.join(md_parts),encoding='utf-8')
        (site/'audit-prive.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        hashes={f:sha((site/f).read_bytes()) for f in ('index.html','page.md','audit-prive.json')}
        manifest={"format":FORMAT,"status":"PRIVATE_SOURCE_LITERAL_NOT_GF_NOT_PUBLISHABLE",
                  "files_sha256":hashes,"source_sha256":sha(raw),"selected_count":len(rows),
                  "publisher_contract":"NONE","publication_authorized":False}
        (site/'site-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        verify_preview(site)
        os.replace(site,dest)
    return {"status":audit['status'],"source_sha256":sha(raw),"definitions":len(rows),
            "html":str(dest/'index.html'),"markdown":str(dest/'page.md'),"publication_authorized":False}


def verify_preview(site:Path)->dict:
    site=Path(site)
    if site.is_symlink() or not site.is_dir(): raise PreviewError("Site source privé absent")
    files={p.name for p in site.iterdir() if p.is_file() and not p.is_symlink()}
    if files!={'index.html','page.md','audit-prive.json','site-manifest.json'}:
        raise PreviewError("Fichiers de site privé manquants ou inattendus")
    manifest=json.loads((site/'site-manifest.json').read_text(encoding='utf-8'))
    audit=json.loads((site/'audit-prive.json').read_text(encoding='utf-8'))
    if (manifest.get('format')!=FORMAT or audit.get('format')!=FORMAT
            or manifest.get('status')!='PRIVATE_SOURCE_LITERAL_NOT_GF_NOT_PUBLISHABLE'
            or audit.get('status')!='PRIVATE_SOURCE_LITERAL_NOT_GF_NOT_PUBLISHABLE'
            or manifest.get('publication_authorized') is not False
            or audit.get('semantik_gf_executed') is not False):
        raise PreviewError("Statut de confidentialité/qualification incorrect")
    hashes=manifest.get('files_sha256',{})
    if set(hashes)!={'index.html','page.md','audit-prive.json'}:
        raise PreviewError("Inventaire des empreintes incorrect")
    for rel,h in hashes.items():
        if sha((site/rel).read_bytes())!=h:
            raise PreviewError("Contenu de la page modifié après construction")
    return {"status":"PASS_PRIVATE_SOURCE_PREVIEW","definitions":audit['selected_count'],
            "publisher_eligible":False}


def export_spek_literal_fixture(graph_path: Path, out: Path, *, spek_root: Path | None = None) -> dict:
    """Instantiate REAL existing SPEK template refs with source-literal fixtures.

    Request references here are placeholders deliberately without request files;
    compose-preview works, while compose-lock and real GF execution must refuse.
    """
    keyed, raw = source_assertions(Path(graph_path))
    selected = selected_text(keyed)
    by_id = {r['id']:r for r in selected}
    dest = _safe_out(Path(out), Path(spek_root) if spek_root is not None else None)
    entries:dict[str,dict] = {}
    used_ids:set[str] = set()

    def leaf(key:str, kind:str, text:str, assertion_id:str|None=None)->dict:
        if key in entries or not re.fullmatch(r'[a-z][a-z0-9._-]{0,95}',key):
            raise PreviewError('Clé SPEK invalide ou dupliquée')
        if not text or len(text)>5000:
            raise PreviewError('Libellé/texte SPEK trop grand')
        entries[key]={'fr':{'text':text,'status':'fixture',
                    'provider':'agriculture_v11_1_source_literal_or_editorial_candidate',
                    'qualification':'SOURCE_LITERAL_OR_EDITORIAL_LABEL_NOT_GF_NOT_APPROVED'}}
        if assertion_id:
            if assertion_id not in by_id or assertion_id in used_ids or text!=by_id[assertion_id]['text']:
                raise PreviewError('Ancrage textuel ambigu dans la proposition SPEK')
            used_ids.add(assertion_id)
            entries[key]['fr']['source_assertion_id']=assertion_id
        return {'node_type':'text_slot','kind':kind,'realization_key':key,
                'communication_request_ref':'requests/'+key+'.json',
                'source_assertion_refs':[assertion_id] if assertion_id else []}

    # Introduction : définition-source en ouverture, sans gloser ni inventer.
    first=selected[0]
    intro={
        'node_type':'template_ref','instance_id':'intro','template_ref':'rhetorical.definition@1.0.0',
        'bindings':{
            'term':leaf('intro.term','concept',first['editorial_label']),
            'definition':leaf('intro.definition','definition',first['text'],first['id']),
        }
    }
    sections=[]
    for i,(heading, raw_cards) in enumerate(SECTIONS,1):
        cards=list(raw_cards)
        if i==1:cards=cards[1:]  # premier extrait consommé dans l'introduction
        if len(cards)<2 or len(cards)>9:raise PreviewError('Cardinalité incompatible avec le template de section')
        lead_label, lead_id=cards[0]
        lead=by_id[lead_id]
        details=[]
        for j,(label,aid) in enumerate(cards[1:],1):
            row=by_id[aid]; prefix=f's{i}.detail{j}'
            details.append({'node_type':'template_ref','instance_id':f'detail-{j}',
                'template_ref':'rhetorical.definition@1.0.0',
                'bindings':{
                    'term':leaf(prefix+'.term','concept',label),
                    'definition':leaf(prefix+'.definition','definition',row['text'],aid)
                }})
        sections.append({'node_type':'template_ref','instance_id':f'section-{i}',
            'template_ref':'wiki.domain-section@1.0.0',
            'bindings':{
                'heading':leaf(f's{i}.heading','concept',heading),
                'lead':leaf(f's{i}.lead','definition',lead['text'],lead_id),
                'details':{'node_type':'repeat','template_ref':'rhetorical.definition@1.0.0',
                           'min':len(details),'max':len(details),'instances':details}
            }})
    if used_ids!={r['id'] for r in selected}:
        raise PreviewError('Couverture d’extraits insuffisante dans le template')
    instance={'format':'spek.composition-instance/1.0','instance_id':'agriculture-sol-v11-1-source-literal-candidate',
              'template_ref':'wiki.domain-primer-source-bound@1.0.0',
              'authority':'editorial_bindings_explicit_not_approved',
              'bindings':{
                  'introduction':intro,
                  'sections':{'node_type':'repeat','template_ref':'wiki.domain-section@1.0.0',
                              'min':4,'max':4,'instances':sections},
              },
              'presentation':{'layout_variant':'stack','join_mode':'block','show_template_labels':False}}
    bundle={'format':'kristal.layout-realizations/0.1',
            'note':'SOURCE_LITERAL_AND_EDITORIAL_LABELS_ONLY; FIXTURE; ZERO GF; PRIVATE NOT PUBLISHABLE',
            'entries':entries}
    meta={'format':'spek.agriculture-source-template-handoff/0.1',
          'source_sha256':sha(raw),'status':'SOURCE_LITERAL_FIXTURES_ONLY',
          'templates_used':['wiki.domain-primer-source-bound@1.0.0',
                            'wiki.domain-section@1.0.0','rhetorical.definition@1.0.0'],
          'assertions_bound':len(used_ids),'text_slots':len(entries),
          'request_files_created':0,'real_semantik_results':0,'publication_authorized':False}
    instructions=(
        '# Composition source-littérale par les véritables templates SPEK\n\n'
        '**PROPOSITION PRIVÉE / FIXTURE : aucune phrase GF, aucune autorisation éditoriale.**\n\n'
        'Depuis le dépôt SPEK installé sur ton poste :\n\n'
        '```powershell\n'
        'py -3.12 -m spek compose-check --instance "C:\\CHEMIN\\spek-template-litteral\\instance.json"\n'
        'py -3.12 -m spek compose-preview --instance "C:\\CHEMIN\\spek-template-litteral\\instance.json" '
        '--realizations "C:\\CHEMIN\\spek-template-litteral\\realizations-source-litterale-fr.json" '
        '--language fr --title "Agriculture — Le sol (source-littérale)" '
        '--out "$env:USERPROFILE\\Downloads\\AGRICULTURE_SOL_SPEK_TEMPLATE_PRIVE"\n'
        'Start-Process "$env:USERPROFILE\\Downloads\\AGRICULTURE_SOL_SPEK_TEMPLATE_PRIVE\\index.html"\n'
        '```\n\n'
        'Les `communication_request_ref` sont des références préparatoires **sans fichiers**. '
        'Ne pas appeler `compose-lock` ou prétendre qu’elles sont des requêtes SemantiK réalisées. '
        'Pour un article GF, remplacer cette proposition par un plan approuvé et des requêtes réelles, '
        'puis utiliser `scripts/construire_pages_kristals.py`.\n'
    )
    with tempfile.TemporaryDirectory(prefix='.agri-spek-source-',dir=dest.parent) as tmp:
        area=Path(tmp)/'source-template';area.mkdir()
        for name,obj in [('instance.json',instance),('realizations-source-litterale-fr.json',bundle),('audit-prive.json',meta)]:
            (area/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (area/'LISEZ_MOI.md').write_text(instructions,encoding='utf-8')
        os.replace(area,dest)
    return {'status':'PRIVATE_SPEK_TEMPLATE_FIXTURE_NOT_GF','assertions':len(used_ids),
            'text_slots':len(entries),'path':str(dest),'publication_authorized':False}


def doctor(spek_root:Path, architect:Path, gf_exe:Path, pilot_root:Path|None=None)->dict:
    spek_root=Path(spek_root);architect=Path(architect);gf_exe=Path(gf_exe)
    expected=[spek_root/'spek/composition/engine.py',spek_root/'scripts/realiser_composition_semantik.py',
              spek_root/'scripts/construire_pages_kristals.py',
              architect/'src/semantik_architect/adapters/inbound/cli/main.py',gf_exe]
    flags={p.name+'@'+str(i):p.is_file() and not p.is_symlink() for i,p in enumerate(expected)}
    root=architect/'runtime';bindings={}
    try:
        a=json.loads((root/'activation.json').read_text(encoding='utf-8'))
        if isinstance(a,dict) and isinstance(a.get('bindings'),dict):
            bindings={str(k):str(v) for k,v in a['bindings'].items()}
    except (OSError,ValueError):pass
    if pilot_root is not None:
        pilot_root=Path(pilot_root)
        flags['pilot_root']=pilot_root.is_dir() and not pilot_root.is_symlink()
        # No automatic unbounded recursive scan of private files.
        for rel in ('instance/agriculture.instance.json','requests'):
            flags['pilot_'+rel]= (pilot_root/rel).exists()
    return {"status":"READ_ONLY_ENVIRONMENT_INSPECTION","requirements":flags,
            "activated_profile_bindings":bindings,
            "agriculture_profile_qualified":False,
            "note":"L'activation Konstellation ne prouve pas une couverture GF pour Agriculture/Sol.",
            "no_files_modified":True,"publication_authorized":False}


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description="Pilote Agriculture/Sol : prévisualisation de sources et diagnostic GF privé")
    sub=p.add_subparsers(dest='cmd',required=True)
    b=sub.add_parser('preview-sources',help='Page HTML source-littérale, explicitement non GF et non publiable')
    b.add_argument('--graph',type=Path,required=True);b.add_argument('--out',type=Path,required=True)
    b.add_argument('--spek-root',type=Path)
    ex=sub.add_parser('export-spek-fixture',help='Véritable instance de templates SPEK, avec textes sources fixtures et sans GF')
    ex.add_argument('--graph',type=Path,required=True);ex.add_argument('--out',type=Path,required=True)
    ex.add_argument('--spek-root',type=Path)
    v=sub.add_parser('verify',help='Contrôler les empreintes du site privé source-littéral');v.add_argument('site',type=Path)
    d=sub.add_parser('doctor',help='Inventaire en lecture seule des prérequis du véritable pipeline GF/SPEK')
    d.add_argument('--spek-root',type=Path,required=True)
    d.add_argument('--architect',type=Path,required=True)
    d.add_argument('--gf-exe',type=Path,required=True)
    d.add_argument('--pilot-root',type=Path)
    args=p.parse_args(argv)
    try:
        if args.cmd=='preview-sources':out=build_preview(args.graph,args.out,spek_root=args.spek_root)
        elif args.cmd=='export-spek-fixture':out=export_spek_literal_fixture(args.graph,args.out,spek_root=args.spek_root)
        elif args.cmd=='verify':out=verify_preview(args.site)
        else:out=doctor(args.spek_root,args.architect,args.gf_exe,args.pilot_root)
        print(json.dumps(out,ensure_ascii=False,indent=2));return 0
    except (PreviewError,OSError,ValueError,UnicodeError) as exc:
        print(json.dumps({"status":"BLOCKED","reason":str(exc) if isinstance(exc,PreviewError) else "Échec de validation privée",
                          "publication_authorized":False},ensure_ascii=False),file=sys.stderr)
        return 2

if __name__=='__main__':raise SystemExit(main())
