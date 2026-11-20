"""SPEK Agriculture v8 — pilotage registre-first, sans moteur concurrent.

Toujours privé. Réutilise les registres, l'audit de candidature, le précontrôle
récursif v0.5 et les rendus SPEK existants. Ne crée aucun texte ni n'active
une affectation/publication. Les diagnostics sont non normatifs.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

SOURCE_SHA = 'ae3cf84ab47a1ea3c710785f5749c7cacd8274d389f767958c7327c6c1a72918'
SOURCE_WIN = r'C:\mycode\Kristal\locals\Kristal-Agriculture\.kristal\v8\portable-state.kristal-state.json'
SPEK_WIN = r'C:\mycode\Spek_Semantic-publishing\Spek'
ARCHITECT_WIN = r'C:\mycode\SemantiK_Architect\SemantiK_Architect'
GF_WIN = r'C:\mycode\Grammatical-Framework\gf-3.12-windows\gf.exe'
WORDBENCH_WIN = r'C:\mycode\Grammatical-Framework\GF_Wordbench'
RGL_WIN = r'C:\mycode\Grammatical-Framework\gf-rgl'
DIK_WIN = r'C:\mycode\diK\diK'  # chemin documente par diK, NON confirme chez l'utilisateur
FILES = {
    'binding': 'liaison-agriculture-v8-CANDIDATE-NON-APPROUVEE.json',
    'audit': 'audit-candidats-assertions-v8.json',
}


class PilotError(ValueError):
    pass


def _load_py(file: Path, name: str):
    if file.is_symlink() or not file.is_file():
        raise PilotError('Composant existant introuvable : ' + str(file))
    spec = importlib.util.spec_from_file_location(name, file)
    if spec is None or spec.loader is None:
        raise PilotError('Impossible de charger le composant ' + name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha(file: Path) -> str:
    h = hashlib.sha256()
    with file.open('rb') as s:
        for block in iter(lambda: s.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def _json(file: Path) -> dict:
    if file.is_symlink() or not file.is_file():
        raise PilotError('JSON introuvable ou symbolique : ' + str(file))
    obj = json.loads(file.read_text(encoding='utf-8-sig'))
    if not isinstance(obj, dict):
        raise PilotError('JSON objet attendu : ' + str(file))
    return obj


def _plain_private_path(path: Path, spek: Path, other_repos: tuple[Path, ...] = ()) -> Path:
    path = path.expanduser().absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise PilotError('Sortie symbolique interdite')
    for repo in (spek, *other_repos):
        repo = repo.expanduser().absolute()
        if path == repo or path.is_relative_to(repo):
            raise PilotError('Sortie privée interdite dans un dépôt')
    if any((p / '.git').exists() for p in (path, *path.parents)):
        raise PilotError('Sortie privée interdite dans un dépôt Git')
    if path.exists():
        raise PilotError('Sortie privée déjà existante — nouveau dossier/fichier requis')
    return path


def _registered(spek: Path, source: Path):
    registry = _load_py(spek / 'scripts' / 'orchestrer_registre_spek.py', 'spek_registry_first_installed')
    ctx = registry.read_context(spek, 'agriculture')
    expected = ctx['review']['source']['portable_state_raw_sha256']
    if expected != SOURCE_SHA:
        raise PilotError('Empreinte source v8 enregistrée différente du pilote')
    if not source.is_file() or source.is_symlink() or _sha(source) != SOURCE_SHA:
        raise PilotError('Source Agriculture v8 absente ou SHA-256 différent')
    return registry, ctx


def audit_candidate(*, spek: Path, source: Path, private_root: Path) -> dict:
    spek = spek.expanduser().resolve(strict=True)
    source = source.expanduser().resolve(strict=True)
    private_root = private_root.expanduser().resolve(strict=True)
    registry, context = _registered(spek, source)
    check = _load_py(spek / 'scripts' / 'verifier_candidature_agriculture.py', 'spek_agri_v8_candidate_checker')
    binding = private_root / FILES['binding']
    audit = private_root / FILES['audit']
    report = check.verify(source, binding, audit, spek)
    bridge = _json(binding)
    if bridge['registry_sha256'] != context['registry_sha256']:
        raise PilotError('Le registre SPEK a changé depuis la sélection candidate : relecture obligatoire')
    if bridge['source_state']['raw_sha256'] != SOURCE_SHA:
        raise PilotError('La sélection candidate référence une autre source')
    if registry.describe(context)['primary_composition_id'] != 'arketype-modele-multiplexe':
        raise PilotError('La composition principale a changé')
    return report


def candidate_runtime_entries(architect: Path) -> list[str]:
    """Noms de profils potentiels seulement; n'affirme JAMAIS une exécution GF."""
    result: list[str] = []
    for relative in ('profiles', 'runtime'):
        folder = architect / relative
        if folder.is_dir() and not folder.is_symlink():
            for item in sorted(folder.iterdir(), key=lambda p: p.name):
                if (not item.is_symlink() and
                        any(term in item.name.lower() for term in ('agricult', 'soil', 'crop'))):
                    result.append(relative + '/' + item.name)
                    if len(result) >= 50:
                        return result
    return result


def doctor(*, spek: Path, source: Path, private_root: Path,
           architect: Path | None = None, gf_exe: Path | None = None,
           wordbench: Path | None = None, rgl_root: Path | None = None,
           dik_root: Path | None = None) -> dict:
    """Diagnostic sans écriture. Les booléens mesurent les fichiers, pas la qualification."""
    spek = spek.expanduser()
    source = source.expanduser()
    private_root = private_root.expanduser()
    architect = architect or Path(ARCHITECT_WIN)
    gf_exe = gf_exe or Path(GF_WIN)
    wordbench = wordbench or Path(WORDBENCH_WIN)
    rgl_root = rgl_root or Path(RGL_WIN)
    result: dict[str, Any] = {
        'format': 'spek.agriculture-v8-registry-first-diagnostic/1.0',
        'kristal_identity': 'agriculture',
        'source_v8_sha256_expected': SOURCE_SHA,
        'source_v8_match': False,
        'registry_match': False,
        'candidate_integrity': 'NOT_RUN',
        'candidate_assertions': 0,
        'sections': 6,
        'missing_layout_slots': {},
        'gf_executable_found': gf_exe.is_file(),
        'architect_root_found': architect.is_dir(),
        'agriculture_profile_name_candidates_unverified': candidate_runtime_entries(architect),
        'gf_agriculture_profile_execution_proven': False,
        'editorial_approval': False,
        'public_authorized': False,
        'publisher_release_ready': False,
        'blockers': [],
    }
    if (spek/'scripts'/'pont_gf_wordbench_agriculture.py').is_file():
        bridge = _load_py(spek/'scripts'/'pont_gf_wordbench_agriculture.py', 'spek_wb_natif')
        result['gf_wordbench_french_pilot'] = bridge.check_french_pilot(
            wordbench=wordbench, rgl_root=rgl_root, gf_exe=gf_exe)
    else:
        result['gf_wordbench_french_pilot'] = {'status': 'BRIDGE_NOT_INSTALLED',
            'agriculture_domain_profile_proven': False, 'publication_authorized': False}
    if (spek/'scripts'/'pont_dik_semantik.py').is_file():
        dik = _load_py(spek/'scripts'/'pont_dik_semantik.py','spek_dik_bridge_doctor')
        result['dik_semantik_lexical_handoff'] = dik.discover(
            root=dik_root or Path(DIK_WIN),architect=architect)
    else:
        result['dik_semantik_lexical_handoff'] = {'status':'BRIDGE_NOT_INSTALLED',
            'agriculture_lexical_approval_proven':False,'publication_authorized':False}
    if not spek.is_dir():
        result['blockers'].append('Dépôt SPEK introuvable')
    if not source.is_file() or source.is_symlink() or _sha(source) != SOURCE_SHA:
        result['blockers'].append('Source Agriculture v8 introuvable ou empreinte différente')
    else:
        result['source_v8_match'] = True
    if result['source_v8_match'] and spek.is_dir():
        try:
            report = audit_candidate(spek=spek, source=source, private_root=private_root)
            result['registry_match'] = True
            result['candidate_integrity'] = report['status']
            result['candidate_assertions'] = report['candidate_unique_assertions']
            result['missing_layout_slots'] = report['layout_slots_missing']
        except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError, ImportError) as e:
            result['blockers'].append('Registre/sélection privée non validés : '+str(e)[:400])
    if result['candidate_integrity'] == 'SOURCE_V8_CANDIDATE_INTEGRITY_VERIFIED_NOT_BUILDABLE':
        result['blockers'].append('6 layouts : qualification de limites obligatoire non réalisée')
        result['blockers'].append('Candidature de 96 assertions : révision éditoriale indépendante en attente')
    result['blockers'].append('Requêtes Agriculture et exécution GF/PGF compatible non démontrées')
    result['blockers'].append('Instances récursives + verrou et plan de collection GF non fournis')
    result['blockers'].append('Publisher et validations de diffusion indépendants non fournis')
    result['status'] = ('SOURCE_AND_REGISTRY_CANDIDATES_VERIFIED_NOT_BUILDABLE'
                        if result['registry_match'] else 'BLOCKED_SOURCE_OR_REGISTRY')
    return result


def inspect_source_bindings(*, binding: Path, source: Path) -> dict:
    """Vérifier chaque assertion et chaque JSON Pointer dans un pont prêt pour GF."""
    b = _json(binding)
    state = _json(source)
    if _sha(source) != SOURCE_SHA:
        raise PilotError('Source v8 différente — correspondances non vérifiables')
    assertions = state.get('assertions')
    if not isinstance(assertions, list):
        raise PilotError('Assertions source absentes')
    sections = b.get('sections')
    if not isinstance(sections, list) or len(sections) != 6:
        raise PilotError('Six sections du registre requises')
    found = 0
    for section in sections:
        ids, pointers = section.get('source_assertion_ids'), section.get('semantic_source_paths')
        if not isinstance(ids, list) or not isinstance(pointers, list) or len(ids) != len(pointers):
            raise PilotError('Assertions et chemins des sections divergents')
        for aid, pointer in zip(ids, pointers):
            if not isinstance(pointer, str) or not pointer.startswith('#/assertions/'):
                raise PilotError('Chemin source non pointé sur une assertion')
            suffix = pointer.removeprefix('#/assertions/')
            if not suffix.isdecimal() or str(int(suffix)) != suffix:
                raise PilotError('Index d’assertion non canonique')
            idx = int(suffix)
            if idx >= len(assertions) or assertions[idx].get('assertion_id') != aid:
                raise PilotError('Index/source/assertion incompatibles')
            found += 1
    return {'source_assertion_links_checked': found, 'status': 'SOURCE_POINTERS_VERIFIED',
            'semantic_approval': False, 'publication_authorized': False}


def preflight(*, spek: Path, binding: Path, plan: Path) -> dict:
    registry = _load_py(spek / 'scripts' / 'orchestrer_registre_spek.py', 'spek_registry_first_preflight')
    report = registry.validate(spek, binding, plan)
    b = _json(binding)
    source_str = b['source_state']['file']
    source = Path(source_str)
    if not source.is_absolute():
        source = binding.parent / source
    verified = inspect_source_bindings(binding=binding, source=source)
    return {'registry': report, 'source': verified, 'publication_authorized': False}


def build(*, spek: Path, binding: Path, plan: Path, architect: Path,
          runtime_root: Path, gf_exe: Path, out: Path) -> dict:
    check = preflight(spek=spek, binding=binding, plan=plan)
    registry = _load_py(spek / 'scripts' / 'orchestrer_registre_spek.py', 'spek_registry_first_build')
    builder = registry._builder(spek)
    produced = builder.build(plan=plan, spek_root=spek, architect=architect,
                             runtime_root=runtime_root, gf_exe=gf_exe, out=out)
    verified = builder.verify(out)
    return {'status': 'PRIVATE_GF_BUILD_VERIFIED_NOT_PUBLISHABLE', 'preflight': check,
            'site': produced, 'verification': verified, 'publication_authorized': False}


def native_preview(*, spek: Path, source: Path, private_root: Path, out: Path) -> dict:
    """Appelle seulement SPEK preview-structure, aucun autre renderer."""
    audit_candidate(spek=spek, source=source, private_root=private_root)
    # source is .../Kristal-Agriculture/.kristal/v8/portable-state.kristal-state.json
    work = source.parent.parent.parent
    if not (work / '.kristal').is_dir():
        raise PilotError('Workspace Kristal local non trouvé')
    out = _plain_private_path(out, spek, (work,))
    out.parent.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, '-m', 'spek', 'preview-structure', '--kristal', str(work), '--out', str(out)]
    try:
        subprocess.run(command, cwd=spek, check=True, timeout=90)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        raise PilotError('Aperçu structurel SPEK refusé : '+type(e).__name__) from e
    if not out.is_dir() or not (out / 'inspection-structurelle.html').is_file():
        raise PilotError('Le moteur SPEK n’a pas créé le document HTML attendu')
    return {'status': 'PRIVATE_SOURCE_STRUCTURE_PREVIEW_ONLY',
            'html': str(out / 'inspection-structurelle.html'),
            'gf_rendered': False, 'publication_authorized': False}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description='Un seul point d’entrée Agriculture — registres, source, SPEK et GF privés')
    p.add_argument('--spek-root', type=Path, default=Path(SPEK_WIN))
    p.add_argument('--source', type=Path, default=Path(SOURCE_WIN))
    p.add_argument('--private-root', type=Path, default=Path.home() / 'Documents' / 'SPEK-PRIVE' / 'Agriculture-v8')
    sub = p.add_subparsers(dest='command', required=True)
    d = sub.add_parser('doctor', help='Diagnostic lisible, hors publication')
    d.add_argument('--architect', type=Path, default=Path(ARCHITECT_WIN))
    d.add_argument('--gf-exe', type=Path, default=Path(GF_WIN))
    d.add_argument('--wordbench-root', type=Path, default=Path(WORDBENCH_WIN))
    d.add_argument('--rgl-root', type=Path, default=Path(RGL_WIN))
    d.add_argument('--dik-root', type=Path, default=Path(DIK_WIN))
    d.add_argument('--report', type=Path, help='Nouveau JSON de diagnostic hors Git')
    probe_dik = sub.add_parser('probe-dik',help='Six commandes diK natives sur une fixture, sans activation')
    probe_dik.add_argument('--dik-root',type=Path,default=Path(DIK_WIN))
    probe_dik.add_argument('--architect',type=Path,default=Path(ARCHITECT_WIN))
    probe_dik.add_argument('--report',type=Path,help='JSON prive nouveau, facultatif')
    lex = sub.add_parser('lexical-needs',help='Lister les besoins lexicaux des 96 taches sans correspondance devinee')
    lex.add_argument('--out',type=Path,required=True)
    req = sub.add_parser('requirements', help='Créer les 96 exigences GF source-vérifiées, non mappées')
    req.add_argument('--out', type=Path, required=True)
    probe = sub.add_parser('probe-fre', help='Sonde GF française NATIVE WordBench, non Agriculture')
    probe.add_argument('--wordbench-root', type=Path, default=Path(WORDBENCH_WIN))
    probe.add_argument('--rgl-root', type=Path, default=Path(RGL_WIN))
    probe.add_argument('--gf-exe', type=Path, default=Path(GF_WIN))
    probe.add_argument('--scenario', choices=('factual-present','possibility','source-attribution'), default='factual-present')
    probe.add_argument('--out', type=Path, required=True)
    pr = sub.add_parser('preview', help='Rendu structurel existant de SPEK : source, PAS GF')
    pr.add_argument('--out', type=Path, required=True)
    check = sub.add_parser('check', help='Pont éditorial complet + source/pointeurs avant GF')
    check.add_argument('--binding', type=Path, required=True)
    check.add_argument('--plan', type=Path, required=True)
    b = sub.add_parser('build', help='Délègue au constructeur GF/HTML SPEK installé')
    for name in ['binding', 'plan', 'architect', 'runtime-root', 'gf-exe', 'out']:
        b.add_argument('--'+name, type=Path, required=True)
    pkg = sub.add_parser('package', help='Vérification + archive du site privé via SPEK existant')
    pkg.add_argument('site', type=Path)
    pkg.add_argument('--out', type=Path, required=True)
    args = p.parse_args(argv)
    try:
        spek = args.spek_root.expanduser().resolve(strict=True)
        if args.command == 'doctor':
            result = doctor(spek=spek, source=args.source, private_root=args.private_root,
                            architect=args.architect, gf_exe=args.gf_exe,
                            wordbench=args.wordbench_root, rgl_root=args.rgl_root, dik_root=args.dik_root)
            if args.report:
                target = _plain_private_path(args.report, spek)
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('x', encoding='utf-8') as fp:
                    fp.write(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
        elif args.command == 'probe-dik':
            dik=_load_py(spek/'scripts'/'pont_dik_semantik.py','spek_dik_native_probe')
            result=dik.test_native_fixture(root=args.dik_root,architect=args.architect)
            if args.report:
                target=_plain_private_path(args.report,spek,(args.dik_root,args.architect))
                target.parent.mkdir(parents=True,exist_ok=True)
                with target.open('x',encoding='utf-8') as f:
                    json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
        elif args.command == 'lexical-needs':
            wb=_load_py(spek/'scripts'/'pont_gf_wordbench_agriculture.py','spek_wb_lexical_requirements')
            dik=_load_py(spek/'scripts'/'pont_dik_semantik.py','spek_dik_lexical_requirements')
            source=Path(args.source).expanduser().resolve(strict=True)
            tasks=wb.requirements_from_v8(spek=spek,source=source,private_root=args.private_root)
            result=dik.lexical_requirements(requirements=tasks,source_sha256=SOURCE_SHA)
            target=_plain_private_path(args.out,spek)
            target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('x',encoding='utf-8') as f:
                json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
            result={k:v for k,v in result.items() if k not in ('items','predicates')} | {'output':str(target)}
        elif args.command == 'requirements':
            bridge = _load_py(spek/'scripts'/'pont_gf_wordbench_agriculture.py', 'spek_wb_requirements')
            result = bridge.requirements_from_v8(spek=spek, source=args.source, private_root=args.private_root)
            target = _plain_private_path(args.out, spek)
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('x', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
                f.write('\n')
            result = {k:v for k,v in result.items() if k not in ('gf_development_tasks','predicate_inventory','sections')} | {'output':str(target)}
        elif args.command == 'probe-fre':
            bridge = _load_py(spek/'scripts'/'pont_gf_wordbench_agriculture.py', 'spek_wb_run')
            target = _plain_private_path(args.out, spek, (args.wordbench_root,args.rgl_root))
            result = bridge.run_french_probe(wordbench=args.wordbench_root,rgl_root=args.rgl_root,
                gf_exe=args.gf_exe,output_root=target,scenario=args.scenario)
        elif args.command == 'preview':
            result = native_preview(spek=spek, source=args.source, private_root=args.private_root, out=args.out)
        elif args.command == 'check':
            result = preflight(spek=spek, binding=args.binding, plan=args.plan)
        elif args.command == 'build':
            result = build(spek=spek, binding=args.binding, plan=args.plan,
                           architect=args.architect, runtime_root=args.runtime_root,
                           gf_exe=args.gf_exe, out=args.out)
        else:
            bld = _load_py(spek / 'scripts' / 'construire_pages_kristals.py', 'spek_legacy_static_builder')
            result = bld.package(site=args.site, out=args.out)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (PilotError, ValueError, OSError, ImportError, KeyError, TypeError, json.JSONDecodeError) as e:
        print(json.dumps({'status': 'REFUSED_PRIVATE', 'message': str(e)[:500],
                          'publication_authorized': False}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
