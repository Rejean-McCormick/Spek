"""Private SPEK vNext recursive composition → SemantiK Architect execution.

Additive operator tool; does not replace SPEK's existing semantic transfer,
source-binding, editorial lock, composition engine or publisher. Requires a
pinned and verified private editorial lock. No remote/git/canon writes.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


def _safe_dir(path: Path, *, name: str) -> Path:
    if path.is_symlink() or not path.is_dir():
        raise ValueError(f"{name} : dossier absent ou lien symbolique")
    return path.resolve(strict=True)


def _safe_file(path: Path, *, name: str) -> Path:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{name} : fichier absent ou lien symbolique")
    return path.resolve(strict=True)


def _outside_git(destination: Path, spek_root: Path) -> Path:
    """Refuse every output under a Git worktree or the SPEK repository."""
    raw = destination.expanduser().absolute()
    # Refuse symlink ancestors before normalizing any '..' path segments.
    for directory in (raw, *raw.parents):
        if directory.is_symlink():
            raise ValueError("Ancêtre de sortie symbolique interdit")
    target = raw.resolve(strict=False)
    if target.exists() or target.is_symlink():
        raise ValueError("Sortie déjà présente : répertoire neuf obligatoire")
    root = spek_root.resolve()
    if target == root or target.is_relative_to(root):
        raise ValueError("Sortie privée à placer hors du dépôt SPEK")
    for directory in (target, *target.parents):
        if directory.is_symlink():
            raise ValueError("Ancêtre de sortie symbolique interdit")
        if (directory / ".git").exists():
            raise ValueError("Sortie privée interdite dans un dépôt Git")
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def _request_for_leaf(leaf: Any, requests_root: Path, language: str, runtime_id: str, profile: str) -> dict:
    from spek.composition.commands import read_instance
    from spek.slot_dialogue import KIND_POLICY, compose_request
    from spek.core import ValidationError

    # Match the exact existing SPEK vNext request-ref resolution rules.
    req_name = Path(leaf.request_ref).name
    ref = Path(leaf.request_ref)
    if (ref.is_absolute() or ".." in ref.parts or not req_name.endswith(".json")
            or req_name in {".", ".."}):
        raise ValidationError("Référence de requête non sûre")
    path = _safe_file(requests_root / req_name, name="Requête SemantiK")
    if not path.is_relative_to(requests_root):
        raise ValidationError("Requête hors du dossier privé")
    request = read_instance(path)
    if request.get("capability_profile") != profile:
        raise ValidationError("Profil SemantiK non conforme à l'édition demandée")
    selector = request.get("runtime_selector")
    if not isinstance(selector, dict) or selector.get("runtime_set_id") != runtime_id:
        raise ValidationError("RuntimeSet non épinglé explicitement dans la requête")
    if not isinstance(request.get("context"), dict) or request["context"].get("target_language") != language:
        raise ValidationError("Langue de la requête différente")
    _, force, kinds, limit = KIND_POLICY[leaf.kind]
    prepared = compose_request(request, {"force": force, "block_kinds": kinds, "max_length": limit}, language=language)
    if prepared.get("semantic_graph") != request.get("semantic_graph") or prepared.get("obligations") != request.get("obligations"):
        raise ValidationError("Modification des faits ou obligations interdite")
    return prepared


def execute(
    *, spek_root: Path, instance: Path, requests_dir: Path, lock: Path,
    architect: Path, runtime_root: Path, gf_exe: Path,
    language: str, runtime_id: str, profile: str, out: Path,
    source_graph: Path | None = None, identity_map: Path | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    """Realize explicit leaves, verify with existing SPEK adapters and preview.

    Returns only public-safe counts/status/path; private requests/results are
    transient under the private output parent and deleted on completion.
    """
    # Script resides under SPEK/scripts; ensure sibling SPEK package is importable
    # even when Python's script directory, rather than cwd, is sys.path[0].
    spek_root = _safe_dir(Path(spek_root), name="Dépôt SPEK")
    if str(spek_root) not in sys.path:
        sys.path.insert(0, str(spek_root))
    from spek.composition.commands import load, preview, read_instance
    from spek.composition.editorial_lock import verify
    from spek.composition.semantik_adapter import import_results
    from spek.composition.engine import materialize
    from spek.semantik_execution import _architect_root, _python_executable
    from spek.core import ValidationError

    instance = _safe_file(Path(instance), name="Instance de composition")
    requests_dir = _safe_dir(Path(requests_dir), name="Requêtes")
    lock = _safe_file(Path(lock), name="Verrou privé")
    architect, runtime_root = _architect_root(Path(architect), Path(runtime_root))
    gf_exe = _safe_file(Path(gf_exe), name="Exécutable GF")
    if gf_exe.name.lower() not in {"gf.exe", "gf"}:
        raise ValidationError("Exécutable GF officiel attendu (gf.exe ou gf)")
    if language not in {"fr", "en", "it"} or not runtime_id or not profile:
        raise ValidationError("Langue, profil ou RuntimeSet invalide")
    if not isinstance(timeout, int) or not 5 <= timeout <= 600:
        raise ValidationError("Délai hors bornes")
    if source_graph is not None:
        source_graph = _safe_file(Path(source_graph), name="Graphe source")
    if identity_map is not None:
        identity_map = _safe_file(Path(identity_map), name="Table de migration")

    # The approved plan is intentionally NOT inferred. This private lock also
    # binds source hashes and every CommunicationRequest before execution.
    verified_lock = read_instance(lock)
    if verified_lock.get("language") != language:
        raise ValidationError("Langue du verrou différente")
    verify(verified_lock, spek_root, instance, requests_dir,
           source_graph=source_graph, identity_map=identity_map)
    resolved = load(spek_root, instance)
    if not resolved.leaves or len(resolved.leaves) > 400:
        raise ValidationError("Composition vide ou trop volumineuse pour ce pilote")

    refs = [Path(leaf.request_ref).name for leaf in resolved.leaves]
    if len(refs) != len(set(refs)):
        raise ValidationError("Une requête SemantiK différente est requise pour chaque feuille")
    source_requests: list[tuple[str, dict]] = []
    # Prepare *all* requests before invoking a subprocess.
    for leaf in resolved.leaves:
        source_requests.append((Path(leaf.request_ref).name,
                                _request_for_leaf(leaf, requests_dir, language, runtime_id, profile)))

    output = _outside_git(Path(out), spek_root)
    env = os.environ.copy()
    env["SEMANTIK_GF_EXECUTABLE"] = str(gf_exe)
    src = str(architect / "src")
    env["PYTHONPATH"] = src + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")

    # No generated private source enters the SPEK checkout or public pages.
    with tempfile.TemporaryDirectory(prefix="spek-gf-verifie-", dir=output.parent) as folder:
        scratch = Path(folder)
        input_dir, result_dir = scratch / "requests", scratch / "results"
        input_dir.mkdir()
        result_dir.mkdir()
        for name, request in source_requests:
            (input_dir / name).write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            command = [_python_executable(), "-m", "semantik_architect.adapters.inbound.cli.main",
                       "--runtime-root", str(runtime_root), "render", str(input_dir / name)]
            try:
                cp = subprocess.run(command, cwd=architect, env=env, capture_output=True,
                                    text=True, encoding="utf-8", timeout=timeout, check=False)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise ValidationError("GF ou SemantiK indisponible; aucun document produit") from exc
            if cp.returncode != 0 or len(cp.stdout) > 2_000_000:
                # Don't leak source IDs or raw stderr in logs/UI.
                raise ValidationError("Réalisation GF refusée ou trop volumineuse; aucune phrase de secours")
            try:
                result = json.loads(cp.stdout)
            except (ValueError, TypeError) as exc:
                raise ValidationError("SemantiK n'a pas renvoyé un CommunicationResult JSON") from exc
            if not isinstance(result, dict) or result.get("schema_version") != "1.0":
                raise ValidationError("Résultat de réalisation SemantiK incorrect")
            (result_dir / name).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        # Reuse SPEK's authoritative pair checker: full obligation coverage,
        # source_refs, language/locale, deterministic_result_id and runtime pin.
        bundle = import_results(resolved, input_dir, result_dir, language)
        materialize(resolved, bundle, language)
        realization_file = scratch / "realizations.json"
        realization_file.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report = preview(spek_root, instance, realization_file, language, output,
                         title="Composition SPEK — aperçu privé")
        return {"status":"PRIVATE_GF_REALIZED_NOT_APPROVED",
                "language":language, "profile":profile,
                "runtime_set_id":runtime_id, "leaves":len(resolved.leaves),
                "html":report["page"], "markdown":report["markdown"],
                "publication_authorized":False}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="SPEK récursif → SemantiK/GF : aperçu privé uniquement")
    p.add_argument("--spek-root", type=Path, required=True)
    p.add_argument("--instance", type=Path, required=True)
    p.add_argument("--requests-dir", type=Path, required=True)
    p.add_argument("--lock", type=Path, required=True, help="Verrou privé compose-lock déjà produit et vérifiable")
    p.add_argument("--architect", type=Path, required=True)
    p.add_argument("--runtime-root", type=Path, required=True)
    p.add_argument("--gf-exe", type=Path, required=True)
    p.add_argument("--language", choices=["fr", "en", "it"], required=True)
    p.add_argument("--runtime-id", required=True)
    p.add_argument("--profile", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--source-graph", type=Path)
    p.add_argument("--identity-map", type=Path)
    p.add_argument("--timeout", type=int, default=60)
    a = p.parse_args(argv)
    try:
        result = execute(spek_root=a.spek_root, instance=a.instance,
                         requests_dir=a.requests_dir, lock=a.lock,
                         architect=a.architect, runtime_root=a.runtime_root,
                         gf_exe=a.gf_exe, language=a.language,
                         runtime_id=a.runtime_id, profile=a.profile, out=a.out,
                         source_graph=a.source_graph, identity_map=a.identity_map,
                         timeout=a.timeout)
    except (ValueError, OSError, ImportError) as exc:
        print(json.dumps({"status":"BLOCKED", "reason":"private_realization_failed",
                          "message_safe":str(exc) if not isinstance(exc, OSError) else "Fichier/outil indisponible",
                          "publication_authorized":False}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
