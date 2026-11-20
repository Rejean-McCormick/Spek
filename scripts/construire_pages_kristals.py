"""SPEK vNext -> complete static HTML/Markdown collection, PRIVATE only.

Builds a multi-page offline *reading* site from explicit, individually locked
recursive compositions. Reuses the earlier GF executor and SPEK's native HTML
and Markdown renderers; it never selects assertions, creates prose, authorizes
publication, pushes to GitHub, or calls Konstellation.

Use ``build``, ``verify`` and ``package``. All outputs are local/private.
"""
from __future__ import annotations

import argparse
import hashlib
from html import escape
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from typing import Any
import zipfile

PLAN_FORMAT = "spek.private-collection-plan/1.0"
SITE_FORMAT = "spek.private-static-collection/1.0"
HANDOFF_FORMAT = "spek.publisher-handoff-private/0.1"
AUTHORITY = "private_editorial_bindings_not_publication_approval"
ALLOWED_LANGUAGES = frozenset({"fr", "en", "it"})  # SPEK vNext's present language set
MAX_PAGES = 500
SAFE_SLUG = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?\Z")
SHA256 = re.compile(r"[a-f0-9]{64}\Z")


class SiteError(ValueError):
    """Fail-closed static-site builder problem."""


def _read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 2_000_000:
        raise SiteError("Plan ou manifeste JSON absent, symbolique ou trop volumineux")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError, UnicodeError) as exc:
        raise SiteError("JSON illisible") from exc
    if not isinstance(value, dict):
        raise SiteError("Objet JSON attendu")
    return value


def _slug(value: Any) -> str:
    if not isinstance(value, str) or not SAFE_SLUG.fullmatch(value):
        raise SiteError("Identifiant de page/collection invalide")
    return value


def _reader_text(value: Any, *, label: str, limit: int) -> str:
    if (not isinstance(value, str) or not 1 <= len(value.strip()) <= limit
            or value.strip() != value or any(ord(c) < 32 or ord(c) == 127 for c in value)
            or any(c in value for c in "<>\\")):
        raise SiteError(f"{label} invalide pour une page de lecture")
    return value


def _private_path(value: Any, base: Path) -> Path:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise SiteError("Chemin d'entrée privé invalide")
    supplied = Path(value).expanduser()
    return supplied if supplied.is_absolute() else base / supplied


def parse_plan(plan_path: Path) -> dict:
    """Pure, strict validation. No filesystem, source, or runtime access."""
    data = _read_json(plan_path)
    if set(data) != {"format", "authority", "collection", "pages"}:
        raise SiteError("Champs du plan inconnus ou manquants")
    if data["format"] != PLAN_FORMAT or data["authority"] != AUTHORITY:
        raise SiteError("Contrat ou autorité du plan incompatible")
    collection = data["collection"]
    if not isinstance(collection, dict) or set(collection) != {"id", "title", "description"}:
        raise SiteError("Métadonnées de collection incomplètes")
    _slug(collection["id"])
    _reader_text(collection["title"], label="Titre de collection", limit=140)
    _reader_text(collection["description"], label="Description de collection", limit=250)
    pages = data["pages"]
    if not isinstance(pages, list) or not 1 <= len(pages) <= MAX_PAGES:
        raise SiteError("Le plan doit contenir de 1 à 500 pages explicites")
    keys = {"id", "title", "language", "instance", "requests_dir", "lock", "runtime_id", "profile"}
    optional = {"source_graph", "identity_map"}
    seen = set()
    for page in pages:
        if not isinstance(page, dict) or not keys.issubset(page) or set(page) - (keys | optional):
            raise SiteError("Page : champs inconnus ou manquants")
        slug = _slug(page["id"])
        lang = page["language"]
        if lang not in ALLOWED_LANGUAGES:
            raise SiteError("Langue non prise en charge par SPEK récursif (fr, en, it)")
        identity = (slug, lang)
        if identity in seen:
            raise SiteError("Page/locale dupliquée")
        seen.add(identity)
        _reader_text(page["title"], label="Titre de page", limit=140)
        for field in ("instance", "requests_dir", "lock"):
            if not isinstance(page[field], str) or not page[field].strip():
                raise SiteError("Lien à une source privée manquant")
        for field in ("runtime_id", "profile"):
            if not isinstance(page[field], str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}", page[field]):
                raise SiteError("Profil/RuntimeSet invalide")
        if "identity_map" in page and "source_graph" not in page:
            raise SiteError("Table de migration sans graphe source")
        for field in optional:
            if field in page and (not isinstance(page[field], str) or not page[field].strip()):
                raise SiteError("Chemin de référence privé vide")
    return data


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_file(file: Path) -> str:
    h = hashlib.sha256()
    with file.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _relative_files(root: Path) -> list[Path]:
    files = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise SiteError("Un site statique ne peut contenir aucun lien symbolique")
        if path.is_file():
            files.append(path)
        elif not path.is_dir():
            raise SiteError("Type de fichier inattendu dans le site")
    return sorted(files, key=lambda x: x.relative_to(root).as_posix())


def _check_html(data: str, *, reference: str) -> None:
    low = data.lower()
    if not low.startswith("<!doctype html>") or "<main>" not in low or "<article>" not in low:
        raise SiteError("Le renderer SPEK n'a pas livré une page HTML complète")
    if any(x in low for x in ("<script", "<iframe", "<object", "<embed", "<form", "javascript:", "file://")):
        raise SiteError("Contenu HTML actif ou non local interdit dans l'aperçu")
    if re.search(r"[a-zA-Z]:\\", data):
        raise SiteError("Chemin privé détecté dans une page de lecture")
    if not reference.startswith("pages/"):
        raise SiteError("Route HTML non attendue")


def _index_html(collection: dict, pages: list[dict]) -> str:
    items = []
    for p in pages:
        title = escape(p["title"])
        language = escape(p["language"])
        route = escape(p["html"], quote=True)
        items.append(f'<li><a href="{route}">{title}</a> <span lang="en">({language})</span></li>')
    return ('<!doctype html><html lang="fr"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{escape(collection["title"])}</title>'
            '<style>body{font-family:system-ui,Segoe UI,sans-serif;color:#203a37;background:#f5f9f7;line-height:1.6}'
            'main{max-width:880px;margin:3rem auto;padding:2rem;background:white;border-radius:12px}'
            'a{color:#1e6864}li{margin:.5rem 0}.note{padding:1rem;background:#eaf3ef;border-left:4px solid #1e6864}'
            '</style></head><body><main>'
            f'<h1>{escape(collection["title"])}</h1><p>{escape(collection["description"])}</p>'
            '<p class="note">Collection en aperçu privé. Aucune autorisation de publication n’est accordée.</p>'
            '<h2>Pages composées avec SPEK</h2><ul>' + "".join(items) + '</ul></main></body></html>')


def _add_navigation(html: str, page: dict, siblings: list[dict]) -> str:
    nav = '<nav aria-label="Navigation de la collection" style="margin-bottom:1rem;padding-bottom:1rem;border-bottom:1px solid #d9e6e2">'
    nav += '<a href="../../../index.html">← Collection</a>'
    for p in siblings:
        if p["id"] == page["id"] and p["language"] != page["language"]:
            lang = escape(p["language"])
            nav += f' · <a hreflang="{lang}" href="../../{lang}/{escape(page["id"], quote=True)}/index.html">{lang}</a>'
    nav += "</nav>"
    return html.replace("<main>", "<main>" + nav, 1)


def _assert_destination(target: Path, spek_root: Path) -> Path:
    # Use exactly the old runner's private output and Git-worktree policy.
    from realiser_composition_semantik import _outside_git
    return _outside_git(target, spek_root)


def run_realization(**kwargs):
    """Only one execution adapter (the cumulative GF patch). Mock at this seam."""
    from realiser_composition_semantik import execute
    return execute(**kwargs)


def build(*, plan: Path, spek_root: Path, architect: Path, runtime_root: Path,
          gf_exe: Path, out: Path, timeout: int = 60) -> dict:
    plan = Path(plan)
    specification = parse_plan(plan)
    spek_root = Path(spek_root).expanduser().resolve(strict=True)
    if not (spek_root / "spek" / "composition" / "engine.py").is_file():
        raise SiteError("Le dépôt SPEK récursif attendu est absent")
    target = _assert_destination(Path(out), spek_root)
    base = plan.parent
    with tempfile.TemporaryDirectory(prefix=".spek-pages-privees-", dir=target.parent) as scratch:
        area = Path(scratch)
        site = area / "site"
        site.mkdir()
        records: list[dict] = []
        requested = specification["pages"]
        for i, page in enumerate(requested):
            preview_root = area / "source-previews" / f"{i:04d}"
            preview_root.parent.mkdir(parents=True, exist_ok=True)
            args = {
                "spek_root": spek_root,
                "instance": _private_path(page["instance"], base),
                "requests_dir": _private_path(page["requests_dir"], base),
                "lock": _private_path(page["lock"], base),
                "architect": Path(architect),
                "runtime_root": Path(runtime_root),
                "gf_exe": Path(gf_exe),
                "language": page["language"],
                "runtime_id": page["runtime_id"],
                "profile": page["profile"],
                "source_graph": _private_path(page["source_graph"], base) if "source_graph" in page else None,
                "identity_map": _private_path(page["identity_map"], base) if "identity_map" in page else None,
                "out": preview_root,
                "timeout": timeout,
            }
            result = run_realization(**args)
            if (result.get("status") != "PRIVATE_GF_REALIZED_NOT_APPROVED"
                    or result.get("publication_authorized") is not False
                    or result.get("language") != page["language"]):
                raise SiteError("La réalisation source ne possède pas le statut privé attendu")
            html_path = preview_root / "index.html"
            md_path = preview_root / "Brouillon-prive.md"
            if not html_path.is_file() or not md_path.is_file() or html_path.is_symlink() or md_path.is_symlink():
                raise SiteError("SPEK n'a pas livré les deux formats attendus")
            html = html_path.read_text(encoding="utf-8")
            route = f'pages/{page["language"]}/{page["id"]}/index.html'
            _check_html(html, reference=route)
            if "Aperçu privé" not in html:
                raise SiteError("La mention de prévisualisation privée manque")
            # The prior GF runner used a fixed *outer* preview title. Change
            # only the reader document's title and h1, never its <article>.
            generic_title = "Composition SPEK — aperçu privé"
            html = html.replace("<title>" + generic_title + "</title>",
                                "<title>" + escape(page["title"]) + "</title>", 1)
            html = html.replace("<h1>" + generic_title + "</h1>",
                                "<h1>" + escape(page["title"]) + "</h1>", 1)
            html = _add_navigation(html, page, requested)
            md = md_path.read_text(encoding="utf-8")
            if "Aperçu privé" not in md:
                raise SiteError("Le Markdown n'indique pas son statut privé")
            if md.startswith("# " + generic_title + "\n"):
                # Markdown title is sanitized by SPEK's renderer; text is
                # strictly restricted above (no markup or control chars).
                md = "# " + page["title"] + md[len("# " + generic_title):]
            dest = site / route
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(html, encoding="utf-8")
            md_rel = f'pages/{page["language"]}/{page["id"]}/page.md'
            (site / md_rel).write_text(md, encoding="utf-8")
            records.append({"id":page["id"],"title":page["title"],"language":page["language"],
                            "html":route,"markdown":md_rel,
                            "source_graph_supplied": "source_graph" in page,
                            "status":"PRIVATE_GF_REALIZED_NOT_APPROVED"})
        (site / "index.html").write_text(_index_html(specification["collection"], records), encoding="utf-8")
        handoff = {
            "format": HANDOFF_FORMAT,
            "collection_id": specification["collection"]["id"],
            "producer": "SPEK-recursive-templates-and-SemantiK-GF",
            "site_entry": "index.html",
            "page_count": len(records),
            "languages": sorted({p["language"] for p in records}),
            "status": "PRIVATE_REVIEW_REQUIRED",
            "publication_eligible": False,
            "public_authorized": False,
            "editorial_review": "NOT_ESTABLISHED",
            "c1_c2_c3": "NOT_VERIFIED",
            "publisher_contract": "NOT_RATIFIED_FOR_RECURSIVE_SITE",
            "manual_next_step": "Qualify exact source and output; approve release; integrate an authorized Publisher adapter",
        }
        _write_json(site / "publication-handoff.json", handoff)
        files = {f.relative_to(site).as_posix(): _hash_file(f) for f in _relative_files(site)}
        manifest = {"format": SITE_FORMAT,"collection_id":specification["collection"]["id"],
                    "status":"PRIVATE_GF_COMPOSED_NOT_PUBLISHABLE",
                    "public_authorized":False,"pages":records,
                    "files_sha256":files,"page_count":len(records),
                    "build_digest":"sha256:"+_sha(json.dumps(files,sort_keys=True,separators=(",",":")).encode("utf-8"))}
        _write_json(site / "site-manifest.json", manifest)
        (site / "site-manifest.sha256").write_text(_hash_file(site / "site-manifest.json") + "  site-manifest.json\n", encoding="ascii")
        verify(site)
        # A partially generated or failed page collection is never exposed as final.
        os.replace(site, target)
    return {"status":"PRIVATE_SITE_BUILT_NOT_PUBLISHABLE","collection_id":specification["collection"]["id"],
            "pages":len(records),"languages":sorted({p["language"] for p in records}),
            "site":str(target),"publication_eligible":False,"public_authorized":False}


def verify(site: Path) -> dict:
    site = Path(site)
    if site.is_symlink() or not site.is_dir():
        raise SiteError("Site introuvable ou lien symbolique")
    manifest = _read_json(site / "site-manifest.json")
    handoff = _read_json(site / "publication-handoff.json")
    if (manifest.get("format") != SITE_FORMAT or manifest.get("public_authorized") is not False
            or manifest.get("status") != "PRIVATE_GF_COMPOSED_NOT_PUBLISHABLE"
            or handoff.get("format") != HANDOFF_FORMAT
            or handoff.get("public_authorized") is not False
            or handoff.get("publication_eligible") is not False
            or handoff.get("status") != "PRIVATE_REVIEW_REQUIRED"):
        raise SiteError("Statut privé/public ou contrat de remise incorrect")
    pages = manifest.get("pages")
    hashes = manifest.get("files_sha256")
    if (not isinstance(pages,list) or not 1 <= len(pages) <= MAX_PAGES
            or not isinstance(hashes,dict) or manifest.get("page_count")!=len(pages)
            or handoff.get("page_count")!=len(pages)
            or handoff.get("collection_id")!=manifest.get("collection_id")):
        raise SiteError("Inventaire de pages ou statut de collection incorrect")
    expected_routes={"index.html","publication-handoff.json","site-manifest.json","site-manifest.sha256"}
    for page in pages:
        if not isinstance(page,dict) or page.get("status")!="PRIVATE_GF_REALIZED_NOT_APPROVED":
            raise SiteError("Statut d'une page incorrect")
        _slug(page.get("id"))
        if page.get("language") not in ALLOWED_LANGUAGES:
            raise SiteError("Langue invalide dans le manifeste")
        expected_html=f'pages/{page["language"]}/{page["id"]}/index.html'
        expected_md=f'pages/{page["language"]}/{page["id"]}/page.md'
        if page.get("html")!=expected_html or page.get("markdown")!=expected_md:
            raise SiteError("Route de page non conforme")
        expected_routes.update({expected_html,expected_md})
    files=_relative_files(site)
    present={x.relative_to(site).as_posix() for x in files}
    if present!=expected_routes or set(hashes)!=(expected_routes-{"site-manifest.json","site-manifest.sha256"}):
        raise SiteError("Fichiers imprévus, manquants ou inventaire divergent")
    if any(not isinstance(digest,str) or not SHA256.fullmatch(digest) for digest in hashes.values()):
        raise SiteError("Empreinte SHA256 invalide")
    for name,digest in hashes.items():
        if _hash_file(site/name)!=digest:
            raise SiteError("Empreinte de site divergente (fichier modifié)")
    commitment = _sha(json.dumps(hashes,sort_keys=True,separators=(",",":")).encode("utf-8"))
    if manifest.get("build_digest")!="sha256:"+commitment:
        raise SiteError("Empreinte de construction divergente")
    recorded=(site/"site-manifest.sha256").read_text(encoding="ascii")
    if recorded!=_hash_file(site/"site-manifest.json")+"  site-manifest.json\n":
        raise SiteError("Empreinte du manifeste incorrecte")
    for page in pages:
        body=(site/page["html"]).read_text(encoding="utf-8")
        _check_html(body,reference=page["html"])
        if "Aperçu privé" not in body:
            raise SiteError("Mention privée absente")
    return {"status":"PASS_PRIVATE_STATIC_SITE","page_count":len(pages),
            "languages":sorted({p["language"] for p in pages}),
            "public_authorized":False,"publisher_eligible":False}


def package(*, site: Path, out: Path) -> dict:
    site = Path(site).resolve(strict=True)
    summary = verify(site)
    dest = Path(out).expanduser().absolute()
    if dest.exists() or dest.is_symlink() or dest.suffix.lower()!=".zip":
        raise SiteError("Archive cible : nouveau fichier ZIP obligatoire")
    # No hidden repository or public deploy destination.
    for folder in (dest.parent, *dest.parents):
        if folder.is_symlink() or (folder/".git").exists():
            raise SiteError("Archive privée interdite dans un dépôt Git")
    if dest.is_relative_to(site):
        raise SiteError("Archive ZIP interdite dans son propre site")
    dest.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=".spek-private-",suffix=".zip",dir=dest.parent,delete=False) as handle:
        temp=Path(handle.name)
    try:
        with zipfile.ZipFile(temp,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
            for file in _relative_files(site):
                # Relative names only, never input/operational paths.
                archive.write(file,file.relative_to(site).as_posix())
        os.replace(temp,dest)
    except BaseException:
        temp.unlink(missing_ok=True)
        raise
    return {**summary,"status":"PACKAGED_PRIVATE_NOT_PUBLISHABLE","archive":str(dest)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Composer les pages HTML d'une collection Kristal via SPEK, en privé")
    sub=ap.add_subparsers(dest="command",required=True)
    b=sub.add_parser("build",help="Réaliser toutes les compositions épinglées et construire le site privé")
    for key in ("plan","spek-root","architect","runtime-root","gf-exe","out"):
        b.add_argument("--"+key,type=Path,required=True)
    b.add_argument("--timeout",type=int,default=60)
    v=sub.add_parser("verify",help="Vérifier les fichiers, empreintes, pages et statut privé")
    v.add_argument("site",type=Path)
    z=sub.add_parser("package",help="Emballer le site privé dans un ZIP; ne publie rien")
    z.add_argument("site",type=Path)
    z.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(argv)
    try:
        if a.command=="build":
            result=build(plan=a.plan,spek_root=a.spek_root,architect=a.architect,
                         runtime_root=a.runtime_root,gf_exe=a.gf_exe,out=a.out,timeout=a.timeout)
        elif a.command=="verify":result=verify(a.site)
        else:result=package(site=a.site,out=a.out)
    except (SiteError,ValueError,OSError,UnicodeError,FileNotFoundError) as exc:
        # Only our vetted, source-free SiteError messages are user-visible.
        safe = str(exc) if isinstance(exc, SiteError) else "Contrôle ou réalisation privée refusée"
        print(json.dumps({"status":"BLOCKED","reason":"collection_private_build_or_check_failed",
                          "message_safe":safe,"type":type(exc).__name__,
                          "publication_authorized":False},ensure_ascii=False),file=sys.stderr)
        return 2
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
