"""Spek v0.2 HTML, XeLaTeX and PDF adapters for one shared document model."""
from __future__ import annotations
import html
import os
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape
from .core import Compiled, ValidationError, escape_tex
from .document import SpekDocument, DocumentItem, DocumentSection, project_document
from .locale import UI
from .inspector import card_inspector

CSS = '''
:root{--ink:#1b2937;--muted:#5e7080;--paper:#f6f7f9;--line:#d9e0e7;--accent:#215d8e;--soft:#edf3f7;--amber:#95600b}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.58}
.wrapper{max-width:1030px;margin:auto;padding:34px 26px 90px}header{padding:22px 0 26px;border-bottom:2px solid var(--ink)}
nav{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;font-size:.83rem;color:var(--muted)}nav a{color:var(--accent);text-decoration:none;padding:6px 9px;border-radius:6px}nav a[aria-current]{background:#e1edf6;font-weight:700}
.eyebrow{color:var(--accent);text-transform:uppercase;letter-spacing:.15em;font-weight:750;font-size:.76rem}
h1{font-family:Georgia,serif;font-size:clamp(2rem,4.1vw,3.5rem);line-height:1.16;letter-spacing:-.025em;margin:20px 0 12px;max-width:830px}
.subtitle{font-size:1.13rem;color:var(--muted);max-width:760px}.warning{display:inline-block;background:#fff1d1;border:1px solid #edcb8b;color:#744700;padding:7px 10px;border-radius:4px;font-weight:750;font-size:.73rem;letter-spacing:.04em}
.abstract{margin:25px 0 14px;border-left:4px solid var(--accent);padding:4px 22px;max-width:870px}.abstract h2{margin:0 0 6px;font-size:1rem}
.toc{margin:25px 0;padding:18px 22px;background:white;border:1px solid var(--line);border-radius:10px}.toc strong{display:block;margin-bottom:5px}.toc a{display:inline-block;margin-right:18px;color:var(--accent);text-decoration:none;font-size:.91rem}
section.panel{margin:36px 0;background:white;border:1px solid var(--line);box-shadow:0 4px 25px #172e4910;border-radius:12px;overflow:hidden;break-inside:avoid}
.section-head{padding:24px 26px 17px;border-bottom:1px solid var(--line)}.section-head .label{font-size:.73rem;letter-spacing:.11em;text-transform:uppercase;color:var(--accent);font-weight:800}.section-head h2{font-family:Georgia,serif;font-size:1.75rem;margin:6px 0}
.content{padding:25px 26px}.highlight{border-left:4px solid var(--accent);background:var(--soft);padding:18px 22px;border-radius:0 7px 7px 0}.small{font-size:.8rem;color:var(--muted)}.block-label{font-size:.72rem;letter-spacing:.075em;text-transform:uppercase;color:var(--muted);font-weight:800;display:block;margin-bottom:8px}
p{margin:0 0 10px}.text-value{font-size:1.02rem}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:16px}.tile{padding:17px 19px;border:1px solid var(--line);border-radius:8px;background:#fff}.tile p:last-child{margin-bottom:0}
.ref{display:block;color:var(--muted);font-family:ui-monospace,monospace;font-size:.67rem;margin-top:10px;overflow-wrap:anywhere}.path{display:flex;align-items:stretch;gap:12px;margin-top:14px}.path>.tile{flex:1}.connector{align-self:center;color:var(--accent);font-size:1.4rem}
.compare{display:grid;grid-template-columns:1fr 1fr;gap:0;margin-top:17px;border:1px solid var(--line);border-radius:8px;overflow:hidden}.compare>div{padding:18px}.compare>div+div{border-left:1px solid var(--line)}.compare>div:first-child{background:var(--soft)}
footer{border-top:1px solid var(--line);padding-top:25px;margin-top:50px;color:var(--muted);font-size:.78rem}.foot-id{font-family:ui-monospace,monospace;overflow-wrap:anywhere}.badge{color:var(--amber);font-size:.76rem;font-weight:750;margin-bottom:9px}
@media(max-width:670px){.wrapper{padding:15px 14px 50px}.content,.section-head{padding:17px}.grid,.compare{grid-template-columns:1fr}.compare>div+div{border-left:none;border-top:1px solid var(--line)}.path{flex-direction:column}.connector{transform:rotate(90deg)}.toc a{display:block;margin:7px 0}}
.unit+.unit{border-top:1px solid var(--line);margin-top:12px;padding-top:12px}.exports{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0}.exports a{font-size:.85rem;display:inline-block;color:var(--accent);padding:7px 11px;border:1px solid var(--line);border-radius:6px;background:white;text-decoration:none} .highlight .ref{padding-top:4px} .tile .block-label{margin-bottom:8px}

.source-navigation{display:inline-flex;padding:7px 10px;margin:6px 0 14px;color:#125581;border:1px solid #b6cfe4;border-radius:5px;font-size:.8rem;font-weight:700;text-decoration:none}.source-navigation:hover{background:#e3f1f9}
/* Per-card offline Source Explorer: HTML details/summary works without JS. */
.source-inspector{border-top:1px solid var(--line);margin-top:14px;padding-top:10px}
.source-trigger{cursor:pointer;color:var(--accent);font-weight:750;font-size:.82rem;list-style:none;display:flex;align-items:center;gap:8px;padding:7px 6px;border-radius:6px;max-width:max-content}
.source-trigger::-webkit-details-marker{display:none}
.source-trigger:hover{background:#dcebf5}.source-trigger:focus-visible{outline:3px solid #236a9e;outline-offset:3px}
.source-trigger-caret{margin-left:5px;transition:transform .15s}.source-inspector[open] .source-trigger-caret{transform:rotate(180deg)}
.source-panel{background:#f8fafc;border:1px solid var(--line);border-radius:8px;margin-top:10px;padding:16px;min-width:0}
.source-record+.source-record{border-top:2px solid var(--line);margin-top:18px;padding-top:18px}
.source-record h4{font-size:.96rem;margin:0 0 15px}.source-record h4 code{display:inline-block;overflow-wrap:anywhere;font-weight:500;font-size:.77rem;background:#e7eef5;padding:3px 6px;border-radius:3px}
.source-record h5{font-size:.73rem;text-transform:uppercase;letter-spacing:.07em;color:#395870;margin:16px 0 8px}
.source-attributes,.evidence-entry dl{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px 16px;margin:0}
.source-attribute{min-width:0;padding:6px 0;border-bottom:1px solid #e7edf2}.source-attribute dt{font-size:.72rem;color:#546779;font-weight:700}.source-attribute dd{margin:3px 0 0;overflow-wrap:anywhere;font-size:.83rem}
.not-provided{color:#82909d;font-size:.77rem}.source-note{font-size:.8rem;color:var(--muted);margin-bottom:10px}
.token-scroll{overflow-x:auto;max-width:100%;border:1px solid var(--line);border-radius:6px;background:white}
.token-scroll:focus-visible{outline:2px solid var(--accent)}
.token-table{border-collapse:collapse;width:100%;font-size:.77rem;min-width:550px}
.token-table th,.token-table td{border-bottom:1px solid #e4eaf0;text-align:left;padding:8px;vertical-align:top;overflow-wrap:anywhere}
.token-table thead th{background:#eaf1f6;color:#294860;font-weight:750}
.token-table tbody th{font-weight:700;color:var(--ink)}.token-table tbody tr:last-child td,.token-table tbody tr:last-child th{border-bottom:0}
.evidence-entry{background:white;border:1px solid var(--line);padding:12px 14px;border-radius:6px;margin:8px 0}
.evidence-entry strong{font-size:.82rem}.evidence-entry p{font-size:.83rem;margin-top:5px}
.source-fingerprint{margin-top:15px;border-top:1px solid var(--line);padding-top:10px;font-size:.74rem;overflow-wrap:anywhere}
.source-fingerprint code{display:block;font-size:.69rem;margin-top:3px}
@media(max-width:670px){.source-panel{padding:11px}.source-attributes,.evidence-entry dl{grid-template-columns:1fr}}
.source-modal{width:min(870px,calc(100vw - 24px));max-width:870px;max-height:min(88vh,900px);padding:0;overflow:auto;border:1px solid #c4d4e1;border-radius:13px;box-shadow:0 18px 80px #091d3480;background:#f8fafc;color:var(--ink)}
.source-modal::backdrop{background:rgba(9,29,52,.58)}
.source-modal-header{position:sticky;top:0;z-index:1;padding:14px 20px;display:flex;align-items:center;justify-content:space-between;gap:16px;background:white;border-bottom:1px solid var(--line)}
.source-modal-header h2{font-size:1.1rem;margin:0}.source-modal-close{border:1px solid var(--line);border-radius:7px;background:white;color:var(--accent);padding:7px 12px;cursor:pointer;font:inherit;font-size:.88rem}
.source-modal-close:focus-visible{outline:3px solid var(--accent)}
.source-modal-content{padding:14px 20px 25px}.source-modal .source-panel{border:0;background:transparent;padding:0;margin:0}
.source-modal .token-table{min-width:670px}.source-modal .source-attributes{grid-template-columns:repeat(2,minmax(0,1fr))}
@media(max-width:670px){.source-modal-content{padding:10px}.source-modal-header{padding:10px 13px}.source-modal .source-attributes{grid-template-columns:1fr}}

@media print{body{background:white}.wrapper{padding:0}.panel{box-shadow:none;break-inside:avoid}nav{display:none}footer{break-before:avoid}}
'''

def _unit_html(item: DocumentItem) -> str:
    a = lambda val: html.escape(val, quote=True)
    refs=','.join(item.evidence_refs)
    return (f'<div class="unit" data-unit-id="{a(item.id)}" data-kind="{a(item.kind)}" '
            f'data-status="{a(item.status)}" data-evidence-refs="{a(refs)}">'
            f'<p class="text-value">{html.escape(item.text)}</p>'
            '</div>')


def _slot_html(section: DocumentSection, slot: str, doc: SpekDocument, css_class='tile') -> str:
    items=section.items(slot)
    if not items:
        return ''
    return (f'<div class="{css_class}" data-slot="{html.escape(slot)}">'
            f'<span class="block-label">{html.escape(UI[doc.language][slot])}</span>'
            + ''.join(_unit_html(item) for item in items)
            + card_inspector(items, doc, slot=slot) + '</div>')


def section_html(doc: SpekDocument, sec: DocumentSection) -> str:
    l = sec.layout; t = UI[doc.language]
    top=(f'<section class="panel" id="{html.escape(sec.id, quote=True)}">'
         f'<div class="section-head"><span class="label">{html.escape(t[l])} · {html.escape(l)} v{html.escape(sec.layout_version)}</span>'
         f'<h2>{html.escape(sec.heading)}</h2></div><div class="content">')
    if l=='result-card':
        body=(_slot_html(sec,'claim',doc,'highlight')
              +'<div class="grid">'+_slot_html(sec,'conditions',doc)+_slot_html(sec,'evidence',doc)+'</div>'
              +'<div class="grid">'+_slot_html(sec,'uncertainty',doc)+_slot_html(sec,'implications',doc)+'</div>')
    elif l=='argument-map':
        body=(_slot_html(sec,'thesis',doc,'highlight')
              +'<div class="grid">'+_slot_html(sec,'premises',doc)+'</div><div class="path">'
              +_slot_html(sec,'inference',doc)+'<span class="connector" aria-hidden="true">→</span>'
              +_slot_html(sec,'conclusion',doc)+'</div>'
              +'<div class="grid">'+_slot_html(sec,'objection',doc)+'</div>')
    elif l=='comparison':
        body=(_slot_html(sec,'topic',doc,'highlight')
              +'<div class="grid">'+_slot_html(sec,'criterion',doc)+'</div><div class="compare">'
              +'<div>'+_slot_html(sec,'approach_a',doc)+'</div><div>'+_slot_html(sec,'approach_b',doc)+'</div></div>'
              +'<div class="grid">'+_slot_html(sec,'synthesis',doc)+_slot_html(sec,'limitations',doc)+'</div>')
    else:
        raise ValidationError('Unknown renderer: '+l)
    return top+body+'</div></section>'


def article_html(m: Compiled, lang: str, formats=('html','pdf','tex')) -> str:
    doc=project_document(m,lang);t=UI[lang]
    warn=f'<p class="warning">{html.escape(t["demo"])}</p>' if doc.demonstration else ''
    langs=' '.join(f'<a href="../{x}/index.html" hreflang="{x}" '+('aria-current="page"' if x==lang else '')+f'>{x.upper()}</a>' for x in m.languages)
    toc=' '.join(f'<a href="#{html.escape(sec.id,quote=True)}">{html.escape(sec.heading)}</a>' for sec in doc.sections)
    sections='\n'.join(section_html(doc,s) for s in doc.sections)
    status=t['source_checked'] if doc.source_verified else t['source_unchecked']
    links=[]
    if 'pdf' in formats:links.append(f'<a href="article.pdf" download>{html.escape(t["pdf"])}</a>')
    if 'tex' in formats:links.append(f'<a href="article.tex" download>{html.escape(t["latex"])}</a>')
    links.append(f'<a href="document.json" download>{html.escape(t["document"])}</a>')
    exports=f'<div class="exports" aria-label="{html.escape(t["exports"])}">'+''.join(links)+'</div>'
    modal = (f'<dialog class="source-modal" id="spek-source-dialog" aria-labelledby="spek-source-title">'
             f'<header class="source-modal-header"><h2 id="spek-source-title"></h2>'
             f'<button type="button" class="source-modal-close">{html.escape({"fr":"Fermer","en":"Close","it":"Chiudi"}[lang])}</button>'
             f'</header><div id="spek-source-content" class="source-modal-content"></div></dialog>')
    # Progressive enhancement: no-JS readers still have expandable native details.
    modal_script = """<script>
(() => {
  const dialog = document.getElementById('spek-source-dialog');
  const content = document.getElementById('spek-source-content');
  const title = document.getElementById('spek-source-title');
  const close = dialog.querySelector('.source-modal-close');
  let trigger = null;
  document.addEventListener('click', event => {
    const summary = event.target.closest('summary.source-trigger');
    if (!summary || !dialog.showModal) return;
    event.preventDefault();
    const details = summary.closest('details.source-inspector');
    if (!details) return;
    const panel = details.querySelector(':scope > .source-panel');
    const card = details.closest('[data-slot]');
    if (!panel || !card) return;
    trigger = summary;
    title.textContent = card.querySelector('.block-label')?.textContent || summary.textContent;
    content.replaceChildren(panel.cloneNode(true));
    dialog.showModal();
    close.focus();
  });
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => { content.replaceChildren(); trigger?.focus(); });
})();
</script>"""
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(doc.title)}</title><meta name="description" content="{html.escape(doc.abstract, quote=True)}"><style>{CSS}</style></head>
<body><main class="wrapper"><nav><span>SPEK · 0.4</span><div aria-label="{html.escape(t['lang'])}">{langs}</div></nav>
<header><span class="eyebrow">{html.escape(t['eyebrow'])}</span><h1>{html.escape(doc.title)}</h1><p class="subtitle">{html.escape(doc.subtitle)}</p>{warn}{exports}</header>
<div class="abstract"><h2>{html.escape(t['abstract'])}</h2><p>{html.escape(doc.abstract)}</p></div>
<div class="toc"><strong>{html.escape(t['contents'])}</strong>{toc}</div>
{sections}
<footer><strong>{html.escape(t['trace'])}</strong><p>{html.escape(t['source_status'])}: {html.escape(status)}. {html.escape(t['evidence_notice'])}</p><p class="foot-id">{html.escape(t['source'])}: {html.escape(doc.source_sha256)} · {html.escape(t['realizations'])}: {html.escape(doc.realizations_sha256)} · {html.escape(t['layouts'])}: {html.escape(doc.layouts_sha256)}</p></footer>
</main>{modal}{modal_script}</body></html>'''


def landing_html(m: Compiled) -> str:
    choices = ' '.join(
        f'<a href="{lang}/index.html" hreflang="{lang}" style="display:inline-block;padding:16px 22px;margin:10px;background:white;color:#215d8e;border-radius:7px;border:1px solid #cbd5df;text-decoration:none">{label} →</a>'
        for lang, label in [('en', 'English'), ('fr', 'Français'), ('it', 'Italiano')] if lang in m.languages)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>Spek — Structured multilingual publications</title></head>'
            f'<body style="font-family:system-ui;background:#f6f7f9;color:#1b2937;max-width:780px;margin:10vh auto;padding:30px">'
            f'<p style="letter-spacing:.18em;color:#215d8e">SPEK · 0.4</p>'
            f'<h1>One meaning. Many structured expressions.</h1>'
            f'<p>Multilingual editorial prototype. Demonstration content only; not scientifically validated.</p>'
            f'<nav aria-label="Select article language">{choices}</nav></body></html>')


def article_tex(m: Compiled, lang: str) -> str:
    doc=project_document(m,lang);t=UI[lang]
    def body(sec,slot):
        return r'\par\smallskip '.join(escape_tex(i.text)+r'\par{\scriptsize\ttfamily '+escape_tex(i.trace())+r'}'
                    for i in sec.items(slot))
    def sl(sec,name):
        return r'\spekSlot{'+escape_tex(t[name])+'}{'+body(sec,name)+'}' if sec.items(name) else ''
    def featured(sec,name):
        return r'\spekFeatured{'+escape_tex(t[name])+'}{'+body(sec,name)+'}' if sec.items(name) else ''
    def pair(sec,a,b):
        return (r'\noindent\begin{minipage}[t]{.48\linewidth}'+sl(sec,a)+r'\end{minipage}\hfill'
               +r'\begin{minipage}[t]{.48\linewidth}'+sl(sec,b)+r'\end{minipage}\par\bigskip')
    content=[]
    for sec in doc.sections:
        content.append(r'\section{'+escape_tex(sec.heading)+'}')
        content.append(r'\textit{'+escape_tex(t[sec.layout])+'}'+ '\n')
        content.append('% spek-section-id: '+sec.id+'\n')
        if sec.layout=='result-card':
            content.extend([featured(sec,'claim'),pair(sec,'conditions','evidence'),pair(sec,'uncertainty','implications')])
        elif sec.layout=='argument-map':
            content.extend([featured(sec,'thesis'),sl(sec,'premises'),pair(sec,'inference','conclusion'),sl(sec,'objection')])
        elif sec.layout=='comparison':
            content.extend([featured(sec,'topic'),sl(sec,'criterion'),pair(sec,'approach_a','approach_b'),pair(sec,'synthesis','limitations')])
    banner = (r'\noindent\fbox{\parbox{0.95\textwidth}{\textbf{'+escape_tex(t['demo'])+'}}}'+'\n') if doc.demonstration else ''
    preamble=[r'\documentclass[11pt,a4paper]{article}',r'\usepackage{fontspec}',
        # Portable across Linux / Windows, without bundling proprietary fonts.
        r'\IfFontExistsTF{DejaVu Sans}{\setmainfont{DejaVu Sans}}{\IfFontExistsTF{Segoe UI}{\setmainfont{Segoe UI}}{\setmainfont{Latin Modern Roman}}}',
        r'\usepackage[margin=24mm]{geometry}',r'\usepackage{xcolor}',
        r'\usepackage{hyperref}',r'\usepackage{xurl}',r'\usepackage{parskip}',
        r'\definecolor{kblue}{HTML}{215D8E}',r'\definecolor{ksoft}{HTML}{EDF3F7}',
        r'\newcommand{\spekSlot}[2]{\par\medskip{\small\bfseries\color{kblue}#1}\par\smallskip #2\par}',
        r'\newcommand{\spekFeatured}[2]{\par\medskip\noindent\fcolorbox{kblue}{ksoft}{\parbox{\dimexpr\linewidth-2\fboxsep-2\fboxrule}{\textbf{#1}\par\medskip #2}}\par\bigskip}',
        r'\hypersetup{colorlinks=true,linkcolor=kblue}',r'\title{'+escape_tex(doc.title)+'}',r'\date{}',
        r'\begin{document}',r'\maketitle',banner,r'\begin{abstract}',escape_tex(doc.abstract),r'\end{abstract}',
        r'\tableofcontents',r'\newpage','\n'.join(content),
        r'\section*{'+escape_tex(t['trace'])+'}',
        r'\small '+escape_tex(t['source_status'])+': '+escape_tex(t['source_checked'] if doc.source_verified else t['source_unchecked']),
        r'\par '+escape_tex(t['source'])+': '+r'\nolinkurl{'+doc.source_sha256+'}',
        r'\par '+escape_tex(t['realizations'])+': '+r'\nolinkurl{'+doc.realizations_sha256+'}',
        r'\par '+escape_tex(t['layouts'])+': '+r'\nolinkurl{'+doc.layouts_sha256+'}',
        r'\end{document}']
    return '\n'.join(preamble)+'\n'


def _pdf_font_paths() -> tuple[Path,Path]:
    '''Use installed TrueType fonts; never bundle or silently use WinAnsi Helvetica.''' 
    specified=(os.getenv('SPEK_FONT_REGULAR'),os.getenv('SPEK_FONT_BOLD'))
    if any(specified):
        if not all(specified):
            raise ValidationError('Set both SPEK_FONT_REGULAR and SPEK_FONT_BOLD to TTF paths')
        paths=tuple(Path(x).expanduser() for x in specified)
        if not all(p.is_file() for p in paths):
            raise ValidationError('Configured PDF Unicode fonts not found: SPEK_FONT_REGULAR / SPEK_FONT_BOLD')
        return paths
    system = Path(os.environ.get('WINDIR', 'C:/Windows'))/'Fonts'
    pairs = [
        (Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')),
        (system/'segoeui.ttf',system/'segoeuib.ttf'),
        (system/'arial.ttf',system/'arialbd.ttf'),
        (Path('/Library/Fonts/Arial Unicode.ttf'),Path('/Library/Fonts/Arial Bold.ttf')),
        (Path('/System/Library/Fonts/Supplemental/Arial.ttf'),Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')),
    ]
    for normal,bold in pairs:
        if normal.is_file() and bold.is_file():return normal,bold
    raise ValidationError('No installed Unicode TTF pair found for PDF. Set SPEK_FONT_REGULAR and SPEK_FONT_BOLD; see docs/FONTS.md.')


def article_pdf(m: Compiled, lang: str, path: Path) -> None:
    try:
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError as err:
        raise RuntimeError('PDF requires reportlab. Install: pip install -r requirements.txt') from err
    docmodel=project_document(m,lang); t=UI[lang]
    normal,bold=_pdf_font_paths()
    pdfmetrics.registerFont(TTFont('SpekUnicode',str(normal)))
    pdfmetrics.registerFont(TTFont('SpekUnicodeBold',str(bold)))
    pdfmetrics.registerFontFamily('SpekUnicode',normal='SpekUnicode',bold='SpekUnicodeBold',italic='SpekUnicode',boldItalic='SpekUnicodeBold')
    # Explicit glyph check: a PDF is rejected rather than silently replacing symbols.
    needed=[docmodel.title,docmodel.subtitle,docmodel.abstract,t['abstract'],t['trace'],
            t['demo'] if docmodel.demonstration else '',t['source_checked'],t['source_unchecked']]
    for sec in docmodel.sections:
        needed.extend([sec.heading,t[sec.layout]])
        for slot,items in sec.slots.items():
            if items:needed.append(t[slot])
            needed.extend(i.text+' '+i.trace() for i in items)
    for font_name in ('SpekUnicode','SpekUnicodeBold'):
        face=pdfmetrics.getFont(font_name).face
        missing={c for value in needed for c in value if ord(c)>31 and c not in '\r\n' and ord(c) not in face.charToGlyph}
        if missing:
            examples=', '.join(f'U+{ord(c):04X}' for c in sorted(missing)[:8])
            raise ValidationError('PDF font missing required Unicode glyph(s) '+examples+'. Configure SPEK_FONT_REGULAR and SPEK_FONT_BOLD.')
    dark=colors.HexColor('#1b2937'); muted=colors.HexColor('#627384'); accent=colors.HexColor('#215d8e')
    pale=colors.HexColor('#edf3f7');line=colors.HexColor('#d9e0e7')
    styles={
        'title':ParagraphStyle('title',fontName='SpekUnicodeBold',fontSize=20.5,leading=26,spaceAfter=9,textColor=dark),
        'subtitle':ParagraphStyle('subtitle',fontName='SpekUnicode',fontSize=10,leading=14,spaceAfter=9,textColor=muted),
        'head':ParagraphStyle('head',fontName='SpekUnicodeBold',fontSize=13.2,leading=17,spaceBefore=12,spaceAfter=5,textColor=accent,keepWithNext=True),
        'minor':ParagraphStyle('minor',fontName='SpekUnicodeBold',fontSize=8.4,leading=10,spaceBefore=4,spaceAfter=3,textColor=muted,keepWithNext=True),
        'body':ParagraphStyle('body',fontName='SpekUnicode',fontSize=8.5,leading=12.3,spaceAfter=3,textColor=dark),
        'note':ParagraphStyle('note',fontName='SpekUnicode',fontSize=6.2,leading=9,spaceAfter=3,textColor=muted,wordWrap='CJK'),
        'warning':ParagraphStyle('warning',fontName='SpekUnicodeBold',fontSize=7.5,leading=10,spaceAfter=7,textColor=colors.HexColor('#936108')),
    }
    def para(text,style='body'):
        return Paragraph(xml_escape(text),styles[style])
    story=[para(docmodel.title,'title'),para(docmodel.subtitle,'subtitle')]
    if docmodel.demonstration:story.append(para(t['demo'],'warning'))
    story.extend([para(t['abstract'],'minor'),para(docmodel.abstract),HRFlowable(width='100%',thickness=.7,color=line)])
    card_width=A4[0]-2*43-12
    def box(items,label,fill=colors.white,width=card_width):
        rows=[para(label,'minor')]
        for item in items:
            rows.extend([para(item.text),para(item.trace(),'note')])
        tb=Table([[rows]],colWidths=[width],hAlign='LEFT')
        tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),fill),('BOX',(0,0),(-1,-1),.65,line),
               ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),
               ('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),2),
               ('BOTTOMPADDING',(0,0),(-1,-1),4)]))
        return tb
    col=(card_width-11)/2
    def paired(sec,a,b,shade=False):
        return Table([[box(sec.items(a),t[a],pale if shade else colors.white,width=col),
                       box(sec.items(b),t[b],width=col)]],colWidths=[col+5.5,col+5.5],hAlign='LEFT',
                     style=TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),
                           ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),5.5),
                           ('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
    for sec in docmodel.sections:
        story.append(para(sec.heading,'head'))
        if sec.layout=='result-card':
            story.extend([box(sec.items('claim'),t['claim'],pale),Spacer(1,6),
                          paired(sec,'conditions','evidence'),paired(sec,'uncertainty','implications')])
        elif sec.layout=='argument-map':
            story.extend([box(sec.items('thesis'),t['thesis'],pale),Spacer(1,5),
                          box(sec.items('premises'),t['premises']),Spacer(1,5),
                          paired(sec,'inference','conclusion',True),box(sec.items('objection'),t['objection'])])
        elif sec.layout=='comparison':
            story.extend([box(sec.items('topic'),t['topic'],pale),Spacer(1,5),
                          box(sec.items('criterion'),t['criterion']),
                          paired(sec,'approach_a','approach_b',True),
                          paired(sec,'synthesis','limitations')])
        story.append(Spacer(1,7))
    # Trace block may not break into an orphan page with only hashes.
    meta=[para(t['trace'],'minor'),
          para(t['source_status']+': '+(t['source_checked'] if docmodel.source_verified else t['source_unchecked']),'note'),
          para(t['source']+': '+docmodel.source_sha256,'note'),
          para(t['realizations']+': '+docmodel.realizations_sha256,'note'),
          para(t['layouts']+': '+docmodel.layouts_sha256,'note')]
    story.append(KeepTogether([HRFlowable(width='100%',thickness=.7,color=line)]+meta))
    def page(canvas,pdf_doc):
        canvas.saveState();canvas.setFont('SpekUnicode',7);canvas.setFillColor(muted)
        canvas.drawString(43,27,'SPEK · 0.4')
        canvas.drawRightString(A4[0]-43,27,str(pdf_doc.page))
        canvas.restoreState()
    pdf=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=43,leftMargin=43,
                          topMargin=39,bottomMargin=40,
                          title=docmodel.title,author='Spek — demonstration' if docmodel.demonstration else 'Spek',invariant=1)
    pdf.build(story,onFirstPage=page,onLaterPages=page)
