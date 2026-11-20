"""Registry-first PRIVATE editorial control, reused by existing SPEK engines.

Reads existing 19/127/deep-review registries; never chooses facts/templates, never
approves assignments or publishes. A typed bridge must explicitly connect
registry sections to the already existing recursive instance/leaf semantics.
This is NOT another renderer or a replacement for the current GF/site builders.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any

FORMAT = "spek.registry-first-explicit-bridge/1.0"
AUTHORITY = "explicit_editorial_bindings_private_not_approved"
SLUG = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,75}[a-z0-9])?\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z")


class RegistryError(ValueError):
    pass


def _json(path: Path, maximum: int = 4_000_000) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > maximum:
        raise RegistryError("Fichier JSON absent, symbolique ou trop volumineux")
    try:
        content = json.loads(path.read_text(encoding="utf-8-sig"))
    except (UnicodeError, OSError, ValueError) as exc:
        raise RegistryError("JSON UTF-8 invalide") from exc
    if not isinstance(content, dict):
        raise RegistryError("Objet JSON attendu")
    return content


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(2 ** 20), b""):
            h.update(block)
    return h.hexdigest()


def _id(identity: str) -> str:
    if not isinstance(identity, str) or not SLUG.fullmatch(identity):
        raise RegistryError("Identité Kristal non canonique; pas de normalisation implicite")
    return identity


def read_context(spek_root: Path, identity: str) -> dict:
    """Read-only exact lookup. Refuses missing proposal, mismatched registry IDs."""
    root = Path(spek_root).expanduser().resolve(strict=True)
    _id(identity)
    wiki = root / "template_library" / "wiki"
    sources = {
        "proposals": wiki / "kristal-ai-proposals.json",
        "registry": wiki / "composition-registry.json",
        "reviews": wiki / "kristal-structure-reviews.json",
        "assignments": wiki / "kristal-assignments.json",
        "designs": wiki / "specialized-template-designs.json",
    }
    if any(p.is_symlink() for p in (wiki, *sources.values())):
        raise RegistryError("Registre symbolique refusé")
    data = {key: _json(path, 4_000_000) for key, path in sources.items()}
    if (data["proposals"].get("format") != "spek.wiki-ai-kristal-proposals/1.0"
        or data["proposals"].get("policy", {}).get("runtime_template_inference_allowed") is not False
        or data["registry"].get("format") != "spek.wiki-ai-composition-registry/1.0"
        or data["registry"].get("allow_runtime_template_inference") is not False
        or data["assignments"].get("format") != "spek.wiki-kristal-composition-assignments/1.0"
        or data["assignments"].get("policy", {}).get("runtime_inference_allowed") is not False):
        raise RegistryError("Politique non-inférentielle ou contrat du registre incompatible")
    proposal = data["proposals"].get("proposals", {}).get(identity)
    if not isinstance(proposal, dict) or proposal.get("kristal_identity") != identity:
        raise RegistryError("Proposition exacte absente; aucune composition devinée")
    primary = proposal.get("primary_composition_id")
    if primary not in data["registry"].get("compositions", {}):
        raise RegistryError("La composition principale n'existe pas dans le registre des 19")
    recipe_rel = data["registry"]["compositions"][primary].get("file", "")
    if not isinstance(recipe_rel, str) or not re.fullmatch(r"compositions/[a-z0-9-]+\.json", recipe_rel):
        raise RegistryError("Référence de recette non sûre")
    recipe = _json(wiki / recipe_rel)
    if recipe.get("composition_id") != primary or recipe.get("format") != "spek.wiki-ai-composition/1.0":
        raise RegistryError("Recette non conforme à la proposition")
    reviews = data["reviews"].get("reviews", {})
    review = reviews.get(identity) if isinstance(reviews, dict) else None
    if review is not None and (not isinstance(review, dict) or review.get("kristal_identity") != identity):
        raise RegistryError("Revue structurelle incohérente")
    assignments = data["assignments"].get("assignments")
    if not isinstance(assignments, dict):
        raise RegistryError("Registre des assignations invalide")
    design_map = {row.get("id"): row for row in data["designs"].get("templates", []) if isinstance(row, dict)}
    review_sections = review.get("ordered_structural_sections", []) if review else []
    proposal_sections = proposal.get("ordered_sections")
    if not isinstance(proposal_sections, list) or not proposal_sections:
        raise RegistryError("Proposition individualisée sans sections déclarées")
    recipe_keys = [(s.get("section_id"), s.get("layout_id")) for s in recipe.get("sections_in_order", [])]
    proposal_keys = [(s.get("section_id"), s.get("layout_id")) for s in proposal_sections]
    if any(k not in recipe_keys for k in proposal_keys) or len(set(proposal_keys))!=len(proposal_keys):
        raise RegistryError("Sections candidates non conformes à la recette du registre")
    recipe_indices = [recipe_keys.index(k) for k in proposal_keys]
    if recipe_indices != sorted(recipe_indices):
        raise RegistryError("Ordre de la proposition non conforme à la recette")
    for s in review_sections:
        if not isinstance(s, dict) or not isinstance(s.get("section_id"), str):
            raise RegistryError("Section de revue incohérente")
        layout_id = s.get("planned_template_id")
        if layout_id not in design_map or not (root / "layouts" / (layout_id + ".json")).is_file():
            raise RegistryError("Layout spécialisé du registre absent de la bibliothèque SPEK")
    return {
        "root": root, "identity": identity, "proposal": proposal, "recipe": recipe,
        "review": review, "assignment": assignments.get(identity),
        "revision": data["proposals"].get("revision"),
        "registry_sha256": {key: _sha(path) for key, path in sources.items()},
        "review_sections": review_sections, "proposal_sections": proposal_sections,
    }


def describe(context: dict) -> dict:
    proposal, review = context["proposal"], context["review"]
    return {
        "kristal_identity": context["identity"],
        "primary_composition_id": proposal["primary_composition_id"],
        "supplementary_composition_ids": proposal.get("supplementary_composition_ids", []),
        "recipe_sections": [{"section_id": s["section_id"], "layout_id": s["layout_id"]}
                            for s in context["recipe"]["sections_in_order"]],
        "candidate_sections_for_kristal": [{"section_id": s["section_id"], "layout_id": s["layout_id"]}
                                           for s in context["proposal_sections"]],
        "deep_review_sections": [{"section_id": s["section_id"], "layout_id": s["planned_template_id"],
                                  "selection_status": s.get("selection_status", "UNKNOWN")}
                                 for s in context["review_sections"]],
        "deep_review_available": review is not None,
        "approved_assignment_present": context["assignment"] is not None,
        "status": "AI_CANDIDATE_PRIVATE_NOT_APPROVED",
        "publication_authorized": False,
    }


def scaffold(context: dict, basis: str) -> dict:
    """Only copy structural candidate IDs; leave facts, paths and GF bindings empty."""
    if basis not in ("deep_review", "recipe"):
        raise RegistryError("Base non prise en charge")
    if basis == "deep_review":
        if context["review"] is None:
            raise RegistryError("Aucune revue approfondie pour ce Kristal")
        rows = [(s["section_id"], s["planned_template_id"]) for s in context["review_sections"]]
        source = context["review"].get("source", {})
        observed = source.get("portable_state_raw_sha256")
        provenance = source.get("portable_state_relative_path")
    else:
        rows = [(s["section_id"], s["layout_id"]) for s in context["proposal_sections"]]
        observed = None
        provenance = None
    return {
        "format": FORMAT,
        "authority": AUTHORITY,
        "kristal_identity": context["identity"],
        "primary_composition_id": context["proposal"]["primary_composition_id"],
        "basis": basis,
        "registry_sha256": dict(context["registry_sha256"]),
        "observed_source": {"file_in_review": provenance, "raw_sha256": observed,
                            "note": "Empreinte d'un snapshot étudié, PAS un engagement canonique"},
        "source_state": {"file": None, "raw_sha256": None},
        "pages": [],
        "sections": [
            {"section_id": sid, "layout_id": lid, "decision": "pending",
             "reason": "", "source_assertion_ids": [], "semantic_source_paths": [],
             "coverage": []}
            for sid, lid in rows
        ],
        "status": "DRAFT_WITHOUT_ASSERTION_SELECTION",
        "publication_authorized": False,
    }


def _private_file_destination(path: Path, spek_root: Path) -> Path:
    p = path.expanduser().absolute()
    if any(x.is_symlink() for x in (p, *p.parents)):
        raise RegistryError("Liens symboliques interdits")
    p = p.resolve(strict=False)
    if p.exists() or p == spek_root or p.is_relative_to(spek_root):
        raise RegistryError("Nouveau fichier de sortie hors de SPEK requis")
    if any((x / ".git").exists() for x in (p.parent, *p.parents)):
        raise RegistryError("Sortie privée interdite dans un dépôt Git")
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _resolve_ref(value: str, base: Path) -> Path:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise RegistryError("Chemin éditorial absent")
    p = Path(value)
    if ".." in p.parts:
        raise RegistryError("Chemin avec traversée interdite")
    p = p if p.is_absolute() else base / p
    if p.is_symlink() or not p.is_file():
        raise RegistryError("Fichier éditorial absent ou symbolique")
    return p.resolve(strict=True)


def _templates(node: Any) -> set[str]:
    refs = {node.template_ref}
    for _, children in node.ordered:
        for child in children:
            if hasattr(child, "template_ref"):
                refs |= _templates(child)
    return refs


def _load_engine(root: Path, instance: Path):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from spek.composition.commands import load
    return load(root, instance)


def validate(spek_root: Path, bridge_path: Path, plan_path: Path, *, context: dict | None = None,
             load_engine=None, parse_site_plan=None) -> dict:
    """Fail-closed preflight. Does not claim semantic review or public authority."""
    root = Path(spek_root).expanduser().resolve(strict=True)
    bridge_path, plan_path = Path(bridge_path), Path(plan_path)
    bridge = _json(bridge_path)
    if bridge.get("format") != FORMAT or bridge.get("authority") != AUTHORITY:
        raise RegistryError("Contrat de liaison éditoriale incompatible")
    if bridge.get("publication_authorized") is not False:
        raise RegistryError("La liaison ne peut autoriser une publication")
    identity = _id(bridge.get("kristal_identity"))
    context = context or read_context(root, identity)
    if (context["identity"] != identity or
            bridge.get("primary_composition_id") != context["proposal"]["primary_composition_id"]):
        raise RegistryError("Plan éditorial divergent de la proposition du Kristal")
    if bridge.get("registry_sha256") != context["registry_sha256"]:
        raise RegistryError("Registre modifié depuis la préparation du plan : nouvelle revue requise")
    basis = bridge.get("basis")
    expected = scaffold(context, basis)
    actual_sections = bridge.get("sections")
    if not isinstance(actual_sections, list) or [(s.get("section_id"), s.get("layout_id")) for s in actual_sections if isinstance(s,dict)] != [
            (s["section_id"], s["layout_id"]) for s in expected["sections"]] or len(actual_sections) != len(expected["sections"]):
        raise RegistryError("Sections et ordre divergents du registre; aucun réarrangement implicite")
    observed = expected["observed_source"]
    if bridge.get("observed_source") != observed:
        raise RegistryError("Empreinte du snapshot examiné ou provenance de revue altérée")
    source = bridge.get("source_state")
    if not isinstance(source, dict) or set(source) != {"file", "raw_sha256"} or not isinstance(source["raw_sha256"], str) or not SHA.fullmatch(source["raw_sha256"]):
        raise RegistryError("Source réelle et empreinte SHA-256 obligatoires")
    if basis == "deep_review" and source["raw_sha256"] != observed["raw_sha256"]:
        raise RegistryError("La source n'est PAS le snapshot revu; revue/migration explicite requise")
    source_file = _resolve_ref(source["file"], bridge_path.parent)
    if _sha(source_file) != source["raw_sha256"]:
        raise RegistryError("Empreinte des octets de la source divergente")
    if parse_site_plan is None:
        sys.path.insert(0, str(root / "scripts")) if str(root / "scripts") not in sys.path else None
        from construire_pages_kristals import parse_plan
        parse_site_plan = parse_plan
    plan = parse_site_plan(plan_path)
    pages = bridge.get("pages")
    if not isinstance(pages, list) or not pages:
        raise RegistryError("Aucune page explicite liée au registre")
    plan_keys = {(p["id"], p["language"]): p for p in plan["pages"]}
    if len(pages) != len(plan_keys):
        raise RegistryError("Les pages de la liaison et du plan GF ne coïncident pas")
    instance_keys: dict[str, set[str]] = {}
    leaf_refs: dict[str, dict[str, set[str]]] = {}
    seen: set[tuple[str,str]] = set()
    for p in pages:
        if not isinstance(p, dict) or set(p) != {"id", "language", "instance", "instance_sha256", "template_refs"}:
            raise RegistryError("Page éditoriale incomplète")
        k = (p["id"], p["language"])
        if k in seen or k not in plan_keys:
            raise RegistryError("Page inconnue ou répétée")
        seen.add(k)
        instance = _resolve_ref(p["instance"], bridge_path.parent)
        if (not isinstance(p["instance_sha256"], str) or
                not SHA.fullmatch(p["instance_sha256"]) or
                _sha(instance) != p["instance_sha256"]):
            raise RegistryError("Empreinte de l'instance récursive divergente")
        expected_instance = _resolve_ref(plan_keys[k]["instance"], plan_path.parent)
        if instance != expected_instance:
            raise RegistryError("L'instance du plan ne correspond pas à la liaison")
        if "source_graph" not in plan_keys[k]:
            raise RegistryError("Source v11 explicitement liée au plan GF obligatoire")
        graph = _resolve_ref(plan_keys[k]["source_graph"], plan_path.parent)
        if graph != source_file:
            raise RegistryError("Le graphe du plan GF diverge de la source épinglée dans le registre")
        if load_engine is None:
            resolved = _load_engine(root, instance)
        else:
            resolved = load_engine(root, instance)
        refs = _templates(resolved.root)
        if (not isinstance(p["template_refs"], list) or not p["template_refs"]
                or len(p["template_refs"]) != len(set(p["template_refs"]))
                or set(p["template_refs"]) != refs):
            raise RegistryError("Combinaison récursive réelle différente de la combinaison déclarée")
        key = p["id"] + ":" + p["language"]
        instance_keys[key] = {leaf.key for leaf in resolved.leaves}
        leaf_refs[key] = {leaf.key: set(leaf.source_assertion_refs) for leaf in resolved.leaves}
        if len(instance_keys[key]) != len(resolved.leaves):
            raise RegistryError("Clés de réalisation dupliquées")
    used_keys = {k: set() for k in instance_keys}
    included = 0
    for s in actual_sections:
        decision = s.get("decision")
        if set(s) != {"section_id", "layout_id", "decision", "reason", "source_assertion_ids", "semantic_source_paths", "coverage"}:
            raise RegistryError("Section : champs manquants ou non autorisés")
        if decision == "omit":
            if (not isinstance(s["reason"], str) or not s["reason"].strip()
                    or s["source_assertion_ids"] or s["semantic_source_paths"] or s["coverage"]):
                raise RegistryError("Omission : raison explicite et absence de liaison requises")
            continue
        if decision != "include":
            raise RegistryError("Section candidate non décidée : include ou omit")
        included += 1
        ids = s["source_assertion_ids"]
        paths = s["semantic_source_paths"]
        cov = s["coverage"]
        if (not isinstance(ids, list) or not ids or len(ids) != len(set(ids))
                or any(not isinstance(x,str) or not SAFE_ID.fullmatch(x) for x in ids)
                or not isinstance(paths,list) or not paths
                or any(not isinstance(x,str) or not x.strip() for x in paths)
                or not isinstance(cov,list) or not cov):
            raise RegistryError("Section incluse sans faits, chemins et couverture explicitement sélectionnés")
        section_refs = set()
        for row in cov:
            if not isinstance(row,dict) or set(row) != {"page_key", "realization_keys"}:
                raise RegistryError("Couverture d'une section invalide")
            page_key = row["page_key"]
            rk = row["realization_keys"]
            if (page_key not in used_keys or not isinstance(rk,list) or not rk
                    or len(set(rk)) != len(rk)):
                raise RegistryError("Affectation page/feuilles de section invalide")
            for key in rk:
                if key not in leaf_refs[page_key] or key in used_keys[page_key]:
                    raise RegistryError("Feuille non existante ou déjà affectée à une autre section")
                used_keys[page_key].add(key)
                section_refs |= leaf_refs[page_key][key]
        if section_refs != set(ids):
            raise RegistryError("Les assertions sélectionnées ne correspondent pas aux feuilles de SPEK")
    if not included or any(used_keys[k] != instance_keys[k] for k in used_keys):
        raise RegistryError("Chaque feuille doit appartenir exactement à une section incluse")
    if bridge.get("status") != "EXPLICIT_PRIVATE_SELECTION_PENDING_INDEPENDENT_REVIEW":
        raise RegistryError("Statut de liaison privé attendu")
    return {"status": "PRIVATE_REGISTRY_PREFLIGHT_VERIFIED",
            "kristal_identity": identity, "pages": len(pages), "sections_included": included,
            "unique_realization_keys": sum(len(v) for v in used_keys.values()),
            "source_fingerprint_matched": True, "recursive_template_sets_matched": True,
            "semantic_qualification_proven": False, "publication_authorized": False,
            "can_attempt_private_GF_build": True}


def _builder(root: Path):
    fn = root / "scripts" / "construire_pages_kristals.py"
    if fn.is_symlink() or not fn.is_file():
        raise RegistryError("Constructeur cumulatif existant introuvable")
    spec = importlib.util.spec_from_file_location("spek_existing_page_builder", fn)
    if spec is None or spec.loader is None:
        raise RegistryError("Constructeur SPEK non chargeable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Registre SPEK d'abord — composition privée, sans nouveau moteur ni publication")
    parser.add_argument("--spek-root", required=True, type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect", help="Lire proposition, recette des 19 et revue détaillée")
    inspect.add_argument("--kristal", required=True)
    draft = commands.add_parser("scaffold", help="Dossier vide de sélection explicite hors des dépôts Git")
    draft.add_argument("--kristal", required=True)
    draft.add_argument("--basis", choices=["deep_review", "recipe"], default="deep_review")
    draft.add_argument("--out", required=True, type=Path)
    check = commands.add_parser("check", help="Valider la liaison exacte avant le moteur GF existant")
    check.add_argument("--binding", required=True, type=Path)
    check.add_argument("--plan", required=True, type=Path)
    build = commands.add_parser("build", help="Contrôler puis déléguer au constructeur de pages existant")
    for x in (build,):
        x.add_argument("--binding", required=True, type=Path)
        x.add_argument("--plan", required=True, type=Path)
        x.add_argument("--architect", required=True, type=Path)
        x.add_argument("--runtime-root", required=True, type=Path)
        x.add_argument("--gf-exe", required=True, type=Path)
        x.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command in ("inspect", "scaffold"):
            ctx = read_context(args.spek_root, args.kristal)
            if args.command == "inspect":
                value = describe(ctx)
            else:
                output = _private_file_destination(args.out, ctx["root"])
                value = scaffold(ctx, args.basis)
                with output.open("x", encoding="utf-8") as f:
                    f.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
                value = {"status": "DRAFT_PRIVATE_NOT_APPROVED", "file": str(output),
                         "sections_pending": len(value["sections"]), "publication_authorized": False}
        else:
            value = validate(args.spek_root, args.binding, args.plan)
            if args.command == "build":
                root = args.spek_root.expanduser().resolve(strict=True)
                existing = _builder(root)
                built = existing.build(plan=args.plan, spek_root=root, architect=args.architect,
                                       runtime_root=args.runtime_root, gf_exe=args.gf_exe, out=args.out)
                value = {"registry_preflight": value, "existing_builder_result": built,
                         "publication_authorized": False}
        print(json.dumps(value, indent=2, ensure_ascii=False))
        return 0
    except (RegistryError, ValueError, OSError, KeyError, TypeError, ImportError) as exc:
        print("REFUS REGISTRE-FIRST : " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
