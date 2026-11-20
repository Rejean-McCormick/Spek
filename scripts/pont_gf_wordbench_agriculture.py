"""Raccord SPEK → GF WordBench, sans moteur GF concurrent et sans approbation.

`check_french_pilot` délègue au précontrôle *natif* de WordBench.
`run_french_probe` délègue la véritable exécution à WordBench; le résultat
reste un candidat Defluens, jamais une réalisation du domaine Agriculture.
`requirements_from_v8` structure les 96 assertions candidates déjà auditées
pour préparer de véritables CommunicationRequest, sans en inventer.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

WORD_BENCH_WIN = r'C:\mycode\Grammatical-Framework\GF_Wordbench'
RGL_WIN = r'C:\mycode\Grammatical-Framework\gf-rgl'
EXPECTED_SOURCE_SHA = 'ae3cf84ab47a1ea3c710785f5749c7cacd8274d389f767958c7327c6c1a72918'
BINDING = 'liaison-agriculture-v8-CANDIDATE-NON-APPROUVEE.json'
AUDIT = 'audit-candidats-assertions-v8.json'


class WordBenchBridgeError(ValueError):
    pass


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _checked_file(path: Path) -> Path:
    if not path.is_file() or path.is_symlink():
        raise WordBenchBridgeError('Fichier absent ou symbolique : '+str(path))
    return path


def _read_json(path: Path) -> dict:
    data = json.loads(_checked_file(path).read_text(encoding='utf-8-sig'))
    if not isinstance(data, dict):
        raise WordBenchBridgeError('Objet JSON requis : '+str(path))
    return data


def _wb_root(path: Path) -> Path:
    path = path.expanduser().absolute()
    if (path/'GF_Wordbench'/'pyproject.toml').is_file() and not (path/'pyproject.toml').is_file():
        path = path/'GF_Wordbench'
    for name in ('pyproject.toml', 'src/gf_wordbench/practical/pilot.py',
                 'pilots/practical_generation_v1/Fre/pilot_manifest.json',
                 'profiles/practical_generation_v1.json'):
        _checked_file(path/name)
    return path


def _launch_native(wordbench: Path, operation: str, *, gf_exe: Path | None = None,
                   rgl_root: Path | None = None, out: Path | None = None,
                   scenario: str = 'factual-present') -> dict:
    """No copied GF runner; official WordBench module is the only executor."""
    root = _wb_root(wordbench)
    args = [sys.executable, '-B', '-m', 'gf_wordbench.practical.pilot',
            operation, '--language', 'Fre']
    if operation == 'run':
        if gf_exe is None or rgl_root is None or out is None:
            raise WordBenchBridgeError('Exécution GF exige gf.exe, RGL et une sortie privée')
        if scenario not in ('factual-present','possibility','source-attribution'):
            raise WordBenchBridgeError('La sonde ciblée n’autorise que 3 scénarios français préparés')
        if not gf_exe.is_file() or gf_exe.name.lower() not in ('gf','gf.exe'):
            raise WordBenchBridgeError('GF officiel introuvable')
        if not (rgl_root/'src/french/GrammarFre.gf').is_file():
            raise WordBenchBridgeError('RGL française introuvable')
        args += ['--gf-executable',str(gf_exe),'--rgl-root',str(rgl_root),
                 '--output-root',str(out),'--scenario',scenario]
    elif operation != 'check':
        raise WordBenchBridgeError('Opération WordBench inconnue')
    env = os.environ.copy()
    env['PYTHONPATH'] = str(root/'src') + (os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    # WordBench owns the GF process and timeout on `run`. No shell or new GF command.
    try:
        process = subprocess.run(args, cwd=root, env=env, capture_output=True,
                                 text=True, encoding='utf-8', errors='replace',
                                 timeout=100 if operation == 'check' else 250)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise WordBenchBridgeError('Impossible d’exécuter le précontrôle WordBench : '+str(exc)) from exc
    if process.returncode not in ((0,) if operation == 'check' else (0,1)):
        raise WordBenchBridgeError('WordBench natif a refusé : '+process.stderr[-1200:])
    try:
        result = json.loads(process.stdout)
    except json.JSONDecodeError as exc:
        raise WordBenchBridgeError('Rapport WordBench natif non JSON : '+process.stdout[-300:]) from exc
    if not isinstance(result, dict) or result.get('language') != 'Fre':
        raise WordBenchBridgeError('Identité du rapport WordBench français incorrecte')
    return result


def check_french_pilot(*, wordbench: Path, rgl_root: Path, gf_exe: Path) -> dict[str, Any]:
    """State both the *real* WordBench preflight and the unproven release gates."""
    result: dict[str, Any] = {
        'format':'spek.wordbench-fre-agriculture-capability/1.0',
        'wordbench_root':str(wordbench), 'rgl_root':str(rgl_root), 'gf_executable':str(gf_exe),
        'wordbench_found':False, 'wordbench_native_preflight_ok':False,
        'rgl_french_found':(rgl_root/'src/french/GrammarFre.gf').is_file(),
        'gf_executable_found':gf_exe.is_file(), 'prepared_french_scenarios':0,
        'gf_run_executed':False,'french_gold_approved':False,
        'agriculture_domain_profile_proven':False,'runtime_activated':False,
        'publisher_release_ready':False,'publication_authorized':False,
        'status':'BLOCKED_WORDBENCH_PREFLIGHT','errors':[],
    }
    try:
        root=_wb_root(wordbench)
        result['wordbench_found']=True
        result['wordbench_root']=str(root)
        res=_launch_native(root,'check')
        if (res.get('status')!='preflight_ok' or res.get('gf_executed') is not False
                or not isinstance(res.get('scenario_ids'),list)
                or res.get('scenario_count')!=len(res['scenario_ids'])
                or res.get('scenario_count')!=15 or len(set(res['scenario_ids']))!=15):
            raise WordBenchBridgeError('Contrat natif Fre : précontrôle inattendu')
        result['wordbench_native_preflight_ok']=True
        result['prepared_french_scenarios']=15
        result['french_gold_approved']=(res.get('gold_approved') is True)
        result['wordbench_fre_lexical_status']=res.get('lexical_status')
        result['manifest_sha256']=_sha(root/'pilots/practical_generation_v1/Fre/pilot_manifest.json')
        result['profile_sha256']=_sha(root/'profiles/practical_generation_v1.json')
        result['status']=('FRENCH_DEFLUENS_PILOT_READY_TO_PROBE_NOT_AGRICULTURE'
                          if result['rgl_french_found'] and result['gf_executable_found']
                          else 'BLOCKED_FRENCH_RGL_OR_GF')
    except (WordBenchBridgeError,OSError,ValueError,ImportError) as exc:
        result['errors'].append(str(exc)[:750])
    return result


def _load_checker(path:Path):
    spec=importlib.util.spec_from_file_location('spek_agri_checker_wordbench_bridge',_checked_file(path))
    if spec is None or spec.loader is None:
        raise WordBenchBridgeError('Vérificateur SPEK introuvable')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def requirements_from_v8(*, spek: Path, source: Path, private_root: Path) -> dict:
    """Prepare exact work for GF *without deciding the semantics or article*."""
    spek=spek.expanduser().resolve(strict=True)
    source=source.expanduser().resolve(strict=True)
    private_root=private_root.expanduser().resolve(strict=True)
    checker=_load_checker(spek/'scripts/verifier_candidature_agriculture.py')
    verified=checker.verify(source, private_root/BINDING, private_root/AUDIT, spek)
    if _sha(source)!=EXPECTED_SOURCE_SHA or verified.get('candidate_unique_assertions')!=96:
        raise WordBenchBridgeError('Source v8 ou sélection 96 différente du dossier audité')
    bridge=_read_json(private_root/BINDING)
    audit=_read_json(private_root/AUDIT)
    sections=[]
    tasks=[]
    predicates=Counter()
    for sec, detailed in zip(bridge['sections'], audit['sections']):
        sid=sec['section_id']
        sections.append({
            'section_id':sid,'layout_id':sec['layout_id'],
            'selected_candidate_count':len(sec['source_assertion_ids']),
            'mandatory_limits':{'status':'EDITORIAL_REVIEW_REQUIRED',
                                'source_assertion_id':None,'semantic_request':None,
                                'linguistic_realization':None},
        })
        for slot, rows in detailed['slot_candidates'].items():
            for row in rows:
                predicates[row['predicate']]+=1
                tasks.append({
                    'section_id':sid,'layout_id':sec['layout_id'],'slot':slot,
                    'assertion_id':row['assertion_id'],'source_pointer':row['source_pointer'],
                    'predicate':row['predicate'],'subject':row['subject'],'object':row['object'],
                    'record_role':row['record_role'],'evidence_refs':row['evidence_refs'],
                    'selection_authority':'AI_CANDIDATE_PENDING_EDITORIAL_REVIEW',
                    'semantik_operation':None,'communication_request':None,
                    'lexical_bindings':None,'gf_expression':None,
                    'gf_wordbench_evidence':None,'mapping_status':'UNMAPPED_NEEDS_EXPLICIT_CONTRACT',
                })
    if len(tasks)!=96 or len({r['assertion_id'] for r in tasks})!=96:
        raise WordBenchBridgeError('Inventaire des exigences GF incohérent')
    return {
        'format':'spek.agriculture-gf-development-requirements/1.0',
        'authority':'PRIVATE_GROUNDING_AND_REQUIREMENTS_ONLY',
        'source_state_sha256':EXPECTED_SOURCE_SHA,
        'registry_sha256':bridge['registry_sha256'],
        'kristal_identity':'agriculture','basis':'deep_review',
        'primary_composition_id':bridge['primary_composition_id'],
        'section_count':len(sections),'candidate_assertion_count':len(tasks),
        'predicate_inventory':[{'predicate':key,'candidate_count':value}
                               for key,value in sorted(predicates.items())],
        'sections':sections,'gf_development_tasks':tasks,
        'french_wordbench_practical_pilot_is_domain_grammar':False,
        'runtime_set_qualified':False,'semantik_executed':False,
        'editorial_approved':False,'publication_authorized':False,
        'status':'PRIVATE_GF_MAPPING_TASKS_PREPARED_NOT_BUILDABLE',
    }


def run_french_probe(*, wordbench:Path, rgl_root:Path, gf_exe:Path, output_root:Path,
                     scenario:str='factual-present')->dict:
    state=check_french_pilot(wordbench=wordbench,rgl_root=rgl_root,gf_exe=gf_exe)
    if state['status']!='FRENCH_DEFLUENS_PILOT_READY_TO_PROBE_NOT_AGRICULTURE':
        raise WordBenchBridgeError('Précontrôle natif insuffisant pour exécuter le pilote français')
    report=_launch_native(wordbench,'run',gf_exe=gf_exe,rgl_root=rgl_root,out=output_root,
                          scenario=scenario)
    rows=report.get('scenarios',[])
    if not isinstance(rows,list) or len(rows)!=1 or rows[0].get('id')!=scenario:
        raise WordBenchBridgeError('Rapport de la sonde WordBench incomplet ou incorrect')
    return {'format':'spek.wordbench-native-french-probe/1.0',
            'wordbench_native_run':True,'scenario_id':scenario,
            'wordbench_scenario_status':rows[0].get('status'),
            'native_report_path':str(Path(report['review_template_path']).with_name('pilot_run.json'))
                if isinstance(report.get('review_template_path'),str) else None,
            'gf_agriculture_profile_execution_proven':False,
            'french_gold_approved':False,'publication_authorized':False,
            'status': 'WORDBENCH_FRE_GF_CANDIDATE_NOT_AGRICULTURE'
                if rows[0].get('status')=='candidate_for_review' else 'WORDBENCH_FRE_PROBE_FAILED'}
