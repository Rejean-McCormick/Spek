"""Offline, source-backed *structural audit* of AI-prescribed Kristal sections.

This preview does not implement production Spek editorial layouts or SemantiK,
does not select assertions for public disclosure, and cannot publish anything.
No heuristic classification, template discovery, temporal/casual inference, or
substituted prose: the reviewed source coordinates drive the entire display.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
import tempfile
from typing import Any

from .core import ValidationError
from .studio_workflow import inspect_kristal

FORMAT = 'spek.wiki-structural-preview-contracts/1.0'
MANIFEST_FORMAT = 'spek.private-structural-audit/1.0'
_ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
_FAMILIES = {'network', 'chain', 'matrix', 'ledger', 'taxonomy', 'trajectory', 'provenance'}


def load_preview_contracts(root: Path) -> dict[str, dict]:
    """Explicit list of human/AI-authored preview kinds, never derived from Kristal data."""
    path = Path(root)/'template_library'/'wiki'/'structural-preview-contracts.json'
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 150_000:
        raise ValidationError('Contrats d’inspection structurelle manquants ou non admissibles')
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise ValidationError('Contrats d’inspection structurelle illisibles') from exc
    if (not isinstance(data, dict) or data.get('format') != FORMAT
            or data.get('publication_eligible') is not False
            or data.get('template_inference_allowed') is not False
            or data.get('production_layouts_implemented') is not True):
        raise ValidationError('Contrats structurels non conformes à la séparation édition/publication')
    items = data.get('templates')
    if not isinstance(items, list) or len(items) != 19:
        raise ValidationError('Le catalogue structurel doit contenir 19 gabarits explicites')
    contracts = {}
    for item in items:
        if not isinstance(item,dict) or not _ID.fullmatch(str(item.get('id',''))):
            raise ValidationError('Identifiant structurel invalide')
        if (item['id'] in contracts or item.get('preview_kind') not in _FAMILIES
                or item.get('status') != 'AUDIT_PREVIEW_ONLY'
                or not isinstance(item.get('label'),str) or not item['label']):
            raise ValidationError('Contrat de gabarit structurel ambigu')
        contracts[item['id']] = item
    # These previews are strictly a view of the existing 19 explicitly specified templates.
    backlog = Path(root)/'template_library'/'wiki'/'specialized-template-designs.json'
    expected = json.loads(backlog.read_text(encoding='utf-8'))
    if set(contracts) != {t['id'] for t in expected.get('templates', [])}:
        raise ValidationError('Les contrats d’aperçu divergent du registre des gabarits à développer')
    return contracts


def _h(value: Any) -> str:
    return escape(str(value), quote=True)


def _read_source(folder: Path, review: dict) -> tuple[list[dict], str]:
    base = Path(folder).resolve(strict=True)
    rel = Path(review['source']['portable_state_relative_path'])
    if rel.is_absolute() or any(p in ('..','.') for p in rel.parts):
        raise ValidationError('Chemin source non autorisé dans la revue')
    target = base
    for part in rel.parts:
        target = target/part
        if target.is_symlink():
            raise ValidationError('Lien symbolique interdit dans le chemin source')
    if not target.resolve(strict=False).is_relative_to(base):
        raise ValidationError('Chemin source hors Kristal')
    if not target.is_file() or target.stat().st_size > 20_000_000:
        raise ValidationError('État portable absent ou trop volumineux')
    content = target.read_bytes()
    current = sha256(content).hexdigest()
    if current != review['source']['portable_state_raw_sha256']:
        raise ValidationError('La source locale diffère du snapshot étudié : nouvelle revue nécessaire')
    try:
        state = json.loads(content)
    except ValueError as exc:
        raise ValidationError('État portable JSON invalide') from exc
    if (not isinstance(state,dict) or state.get('schema_version') != '6.0'
            or state.get('artifact_type') != 'kristal_state'
            or not isinstance(state.get('assertions'),list)):
        raise ValidationError('État Kristal portable v8/v6 inattendu')
    assertions = state['assertions']
    if len(assertions) != review['source']['assertion_occurrences']:
        raise ValidationError('Nombre d’assertions différent de la revue')
    if any(not isinstance(a,dict) for a in assertions):
        raise ValidationError('Assertion mal formée')
    return assertions, current


def _term(value: Any) -> str:
    """Represent a raw term as source data, not a translated or interpreted label."""
    if isinstance(value,dict):
        kind = value.get('kind')
        item = value.get('id') if 'id' in value else value.get('value')
        if item is not None:
            return (str(kind) + ': ' if kind else '') + str(item)
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    if isinstance(value,(str,int,float,bool)) or value is None:
        return str(value)
    return json.dumps(value,ensure_ascii=False,sort_keys=True)


def _items(assertions: list[dict], positions: list[int]):
    for position in positions:
        record=assertions[position]
        statement=record.get('statement') or {}
        if not isinstance(statement,dict): statement={}
        yield {
            'position':position,
            'id':str(record.get('assertion_id','(identifiant absent)')),
            'subject':_term(statement.get('subject','(absent)')),
            'predicate':_term(statement.get('predicate','(absent)')),
            'object':_term(statement.get('object','(absent)')),
            'status':str(record.get('assertion_status','(non déclaré)')),
            'evidence':record.get('evidence_refs') if isinstance(record.get('evidence_refs'),list) else [],
        }


def _render_section_rows(kind: str, records: list[dict]) -> str:
    """Seven bounded visual encodings; they never claim verified edges/hierarchies/ledgers."""
    if kind in ('network', 'chain','trajectory','taxonomy'):
        mark={'network':'⇄','chain':'→','trajectory':'↝','taxonomy':'↳'}[kind]
        lines=[]
        for r in records:
            lines.append(
                '<div class="relation"><div class="rel-grid">'
                f'<span class="term">{_h(r["subject"])}</span>'
                f'<span class="operator"><span aria-hidden="true">{mark}</span> {_h(r["predicate"])}</span>'
                f'<span class="term">{_h(r["object"])}</span></div>'
                f'<p class="meta">Position #{r["position"]} · {_h(r["id"])} · État source : {_h(r["status"])}</p>'
                f'<details><summary>Provenance brute ({len(r["evidence"])})</summary><ul>'
                + ''.join(f'<li><code>{_h(x)}</code></li>' for x in r['evidence'])
                + '</ul></details></div>')
        return ''.join(lines)
    if kind=='provenance':
        inverted:dict[str,list[int]]={}
        for r in records:
            for evidence in r['evidence']:
                inverted.setdefault(str(evidence),[]).append(r['position'])
        out=['<p>Références de preuve déclarées dans les assertions. Leur validité externe n’est pas contrôlée.</p>']
        for ref,indices in sorted(inverted.items()):
            out.append(f'<details class="relation"><summary><code>{_h(ref)}</code> — {len(indices)} occurrences</summary><p>Positions : {_h(", ".join(str(i) for i in indices))}</p></details>')
        if not inverted: out.append('<p>Aucune référence de preuve déclarée.</p>')
        return ''.join(out)
    heading = ('Débit / crédit non attestés · affichage de triples bruts'
               if kind=='ledger' else 'Observations brutes · axes non déduits')
    rows=[f'<p class="meta">{_h(heading)}</p>','<div class="table-scroll"><table><thead><tr><th>Position</th><th>Sujet</th><th>Prédicat</th><th>Objet</th><th>Preuves déclarées</th></tr></thead><tbody>']
    for r in records:
        rows.append('<tr>'
                    f'<td>#{r["position"]}</td><td>{_h(r["subject"])}</td>'
                    f'<td>{_h(r["predicate"])}</td><td>{_h(r["object"])}</td>'
                    f'<td>{_h(", ".join(str(e) for e in r["evidence"]))}</td></tr>')
    rows.append('</tbody></table></div>')
    return ''.join(rows)


def _render_document(info:dict, review:dict, assertions:list[dict], digest:str,contracts:dict) -> str:
    slug=info['identity']
    title=info.get('title') or slug
    sections=review['ordered_structural_sections']
    links=[]
    blocks=[]
    for idx,section in enumerate(sections,1):
        template=section['planned_template_id']
        contract=contracts[template]
        positions=section['source_observation']['source_positions_zero_based']
        records=list(_items(assertions,positions))
        sec_id='s'+str(idx)
        links.append(f'<a href="#{sec_id}"><b>{idx:02d}</b> {_h(section["heading"])} <small>{len(records)}</small></a>')
        blocks.append(
            f'<section id="{sec_id}"><div class="section-label">Partie {idx} · Aperçu {_h(contract["preview_kind"])}</div>'
            f'<h2>{_h(section["heading"])}</h2>'
            f'<p class="sub">Gabarit prescrit : <code>{_h(template)}</code> · {_h(contract["label"])} · {len(records)} occurrences</p>'
            f'<p>{_h(section.get("editorial_intent", ""))}</p>'
            '<p class="note">Inspection structurelle uniquement : les relations ci-dessous sont des triples tels que déclarés. '
            'Les liens visuels ne prouvent ni causalité, ni chronologie, ni hiérarchie, ni équilibrage comptable.</p>'
            '<details><summary>Afficher les assertions source de cette partie</summary>'
            + _render_section_rows(contract['preview_kind'],records)
            + '</details></section>'
        )
    risks=''.join(f'<li>{_h(r)}</li>' for r in review.get('exclusions_and_risks',[]))
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src 'none'; form-action 'none'; base-uri 'none'">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_h(title)} · inspection Spek</title><style>
:root{{color-scheme:light;font-family:system-ui,Segoe UI,sans-serif;background:#f6f7fb;color:#1d2532}}*{{box-sizing:border-box}}
body{{margin:0}}.banner{{background:#1c2b4a;color:white;padding:18px 4vw;border-bottom:4px solid #c66d30}}
.banner h1{{font-size:1.5rem;margin:8px 0}}.banner p{{max-width:1000px;line-height:1.5;margin:4px 0}}
.shell{{display:grid;grid-template-columns:minmax(210px,270px) minmax(0,1fr);gap:20px;max-width:1520px;margin:auto;padding:24px}}
nav{{position:sticky;top:15px;align-self:start;background:white;border:1px solid #d8deeb;border-radius:12px;padding:15px}}
nav a{{display:block;color:#24385d;text-decoration:none;border-bottom:1px solid #eee;padding:10px 4px;font-size:.9rem;line-height:1.4}}nav a:hover{{background:#f5f7fd}}nav small{{float:right}}
main{{min-width:0}}section{{background:white;border:1px solid #d8deeb;padding:22px;margin-bottom:18px;border-radius:12px}}
h2{{font-size:1.25rem}}.section-label{{font-size:.78rem;font-weight:bold;letter-spacing:.06em;color:#57667f;text-transform:uppercase}}
.sub,.meta{{font-size:.82rem;color:#586176;overflow-wrap:anywhere}}.note{{background:#fffaeb;border-left:3px solid #c58c22;padding:12px;color:#59420a}}
.relation{{border:1px solid #dce2ed;border-radius:8px;margin:10px 0;padding:12px;background:#fbfcff;overflow-wrap:anywhere}}
.rel-grid{{display:grid;grid-template-columns:minmax(0,1fr) minmax(90px,auto) minmax(0,1fr);gap:12px;align-items:center}}
.term{{overflow-wrap:anywhere}}.operator{{color:#425d82;font-size:.86rem}}code{{white-space:normal;overflow-wrap:anywhere}}
details>summary{{cursor:pointer;padding:8px;font-weight:600}}.table-scroll{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;font-size:.85rem}}th,td{{border:1px solid #d9deea;text-align:left;padding:8px;overflow-wrap:anywhere;max-width:280px}}th{{background:#f0f3f9}}
@media(max-width:850px){{.shell{{display:block;padding:12px}}nav{{position:static;margin-bottom:15px}}.rel-grid{{display:block}}.operator{{display:block;padding:5px}}}}
</style></head><body><header class="banner"><strong>SPEK · ATELIER DE COMPOSITION</strong>
<h1>{_h(title)} <span style="font-size:.7em;opacity:.8">({_h(slug)})</span></h1>
<p>APERÇU STRUCTUREL PRIVÉ — NON PUBLIABLE. Source locale identique aux octets étudiés : <code>{_h(digest)}</code>.</p>
<p>{len(assertions)} occurrences d’assertions · {len(sections)} sections prescrites par l’IA · aucune assertion choisie pour publication · aucune réalisation SemantiK.</p>
</header><div class="shell"><nav><h2>Plan du Kristal</h2>{''.join(links)}<a href="#risks">Limites et risques</a></nav>
<main>{''.join(blocks)}<section id="risks"><h2>Limites et risques connus</h2><ul>{risks}</ul>
<p>Seuls les identifiants et triples de la source sont affichés : pas de texte de synthèse généré, pas de certification C1/C2/C3, pas de RuntimeSet SemantiK attesté, pas d’export GitHub Wiki.</p></section></main></div></body></html>'''


def create_structural_preview(spek_root: Path, kristal_folder: Path, *, output: Path | None=None) -> dict[str, Any]:
    """Build an offline HTML source audit ONLY for one of the five reviewed Kristals.

    Fails closed when source hashes differ or no reviewed positions exist. A
    private temporary directory is used by default, outside the source repo.
    """
    spek_root=Path(spek_root).resolve(strict=True)
    kristal_folder=Path(kristal_folder).resolve(strict=True)
    info=inspect_kristal(kristal_folder,spek_root)
    review=info.get('structure_review')
    if not info.get('proposal') or not review:
        raise ValidationError('Aucune revue canonique détaillée disponible pour ce Kristal (122 en attente)')
    contracts=load_preview_contracts(spek_root)
    for section in review['ordered_structural_sections']:
        if section['planned_template_id'] not in contracts:
            raise ValidationError('Gabarit spécialisé sans contrat d’aperçu')
    assertions,digest=_read_source(kristal_folder,review)
    html=_render_document(info,review,assertions,digest,contracts)
    if output is None:
        folder=Path(tempfile.mkdtemp(prefix='spek-audit-prive-'))
    else:
        folder=Path(output).expanduser().resolve()
        if folder.exists():
            raise ValidationError('Dossier de sortie déjà existant')
        if folder.is_relative_to(kristal_folder) or folder.is_relative_to(spek_root):
            raise ValidationError('La sortie ne peut pas être dans le Kristal ou dans Spek')
        folder.mkdir(parents=False,exist_ok=False)
    page=folder/'inspection-structurelle.html'
    page.write_text(html,encoding='utf-8')
    manifest={
        'format':MANIFEST_FORMAT,
        'publication_eligible':False,'approval':'NONE','semantik_realized':False,
        'source_raw_sha256':digest,
        'kristal_slug':info['identity'],
        'assertion_occurrences':len(assertions),
        'sections':[{'id':s['section_id'],'template_id':s['planned_template_id'],
                     'observed_occurrences':len(s['source_observation']['source_positions_zero_based'])}
                    for s in review['ordered_structural_sections']],
        'page_sha256':sha256(page.read_bytes()).hexdigest(),
        'warning':'LOCAL SOURCE AUDIT ONLY; NEVER TRANSFER AS A GITHUB WIKI PUBLICATION',
    }
    (folder/'inspection-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {'page':str(page),'directory':str(folder),'manifest':manifest,'status':'PRIVATE_SOURCE_AUDIT_NOT_PUBLISHABLE'}
