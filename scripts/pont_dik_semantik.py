"""Pont d'audit SPEK→diK→SemantiK, basé sur les commandes *natives* diK.

Ne construit ni dictionnaire agréé, ni expression GF, ni RuntimeSet.
Ne convertit jamais un ID Wikidata L/Q/P en identité Kristal.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

DEFAULT_DIK = Path(r'C:\mycode\diK\diK')
DEFAULT_ARCHITECT = Path(r'C:\mycode\SemantiK_Architect\SemantiK_Architect')
REQUIRED = (
    'src/dik/cli.py', 'src/dik/gf_handoff.py',
    'src/dik/semantik_handoff.py',
    'examples/world-dictionaries/wikidata-lexeme-sample.jsonl',
)
OPERATIONS = ('lexemes-import','lexemes-audit','gf-handoff',
              'gf-audit','semantik-knowledge','semantik-knowledge-audit')

class DiKBridgeError(ValueError):
    pass


def _sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for blob in iter(lambda:stream.read(1024*1024),b''):
            h.update(blob)
    return h.hexdigest()


def root_from_hint(path: Path) -> Path:
    """Accepte les deux racines Windows habituelles, sans fouille réseau/Git."""
    path = path.expanduser().absolute()
    choices=(path,path/'diK')
    for candidate in choices:
        if all((candidate/rel).is_file() and not (candidate/rel).is_symlink() for rel in REQUIRED):
            return candidate
    raise DiKBridgeError('Racine diK inconnue, ou code natif de transfert absent : '+str(path))


def _native(root: Path, command: str, flags: dict[str,str]) -> dict[str,Any]:
    if command not in OPERATIONS:
        raise DiKBridgeError('Commande diK non autorisée')
    args=[sys.executable,'-B','-m','dik.cli','world',command]
    for key,value in flags.items():
        if key not in {'dump','snapshot','output-dir','dir','observations','handoff','locale'}:
            raise DiKBridgeError('Option diK non autorisée : '+key)
        args += ['--'+key, str(value)]
    env=os.environ.copy()
    env['PYTHONPATH']=str(root/'src')+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    env['PYTHONDONTWRITEBYTECODE']='1'
    try:
        proc=subprocess.run(args,cwd=root,env=env,capture_output=True,text=True,
                            encoding='utf-8',errors='replace',timeout=100)
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise DiKBridgeError('diK natif inexécutable : '+str(exc)) from exc
    if proc.returncode != 0:
        raise DiKBridgeError('Commande diK refusée '+command+' : '+proc.stderr[-900:])
    try:
        data=json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise DiKBridgeError('Rapport diK natif non JSON : '+command) from exc
    if not isinstance(data,dict):
        raise DiKBridgeError('Rapport diK natif incorrect')
    return data


def discover(*, root:Path=DEFAULT_DIK, architect:Path=DEFAULT_ARCHITECT) -> dict:
    """Doctor sans écriture ni présomption de couplage sémantique."""
    report={'format':'spek.dik-semantik-discovery/1.0','dik_hint':str(root),
            'dik_source_found':False,'architect_schema_found':False,
            'native_handoff_available':False,'agriculture_lexical_approval_proven':False,
            'gf_functions_created':0,'runtime_activated':False,
            'publication_authorized':False,'status':'DIK_NOT_FOUND'}
    try:
        validated=root_from_hint(root)
    except DiKBridgeError as exc:
        report['detail']=str(exc)
        return report
    report['dik_root']=str(validated)
    report['dik_source_found']=True
    schema=architect/'schemas'/'lexical_artifact.schema.json'
    if schema.is_file() and not schema.is_symlink():
        try:
            obj=json.loads(schema.read_text(encoding='utf-8'))
            report['architect_schema_found']='1.1' in obj.get('properties',{}).get('schema_version',{}).get('enum',[])
            report['architect_lexical_schema_sha256']=_sha(schema)
        except (OSError,ValueError,TypeError):
            pass
    report['native_handoff_available']=True
    report['status']='DIK_NATIVE_CANDIDATE_HANDOFF_PRESENT_NOT_ACTIVATED'
    return report


def test_native_fixture(*,root:Path,architect:Path=DEFAULT_ARCHITECT) -> dict:
    """Exécute réellement 6 commandes natives diK sur SON fixture hors dépôts.

    Cette preuve teste le transfert, PAS l'identité Agriculture ni l'approbation.
    """
    dic=root_from_hint(root)
    sample=dic/'examples/world-dictionaries/wikidata-lexeme-sample.jsonl'
    with tempfile.TemporaryDirectory(prefix='spek-dik-offline-') as td:
        tmp=Path(td)
        obs=tmp/'observations'; gf=tmp/'gf'; sa=tmp/'semantik'
        steps=[
          ('lexemes-import',{'dump':str(sample),'snapshot':'spek-local-fixture','output-dir':str(obs)}),
          ('lexemes-audit',{'dir':str(obs)}),
          ('gf-handoff',{'observations':str(obs),'locale':'fr','output-dir':str(gf)}),
          ('gf-audit',{'dir':str(gf)}),
          ('semantik-knowledge',{'handoff':str(gf),'output-dir':str(sa)}),
          ('semantik-knowledge-audit',{'dir':str(sa)}),
        ]
        reports={name:_native(dic,name,flags) for name,flags in steps}
        imported=reports['lexemes-import']; candidate=reports['gf-handoff'];
        knowledge=reports['semantik-knowledge']; final=reports['semantik-knowledge-audit']
        if (imported.get('published_dictionaries')!=0 or imported.get('approved_kristal_crosswalks')!=0
             or candidate.get('gf_functions_created')!=0 or candidate.get('verified_dictionaries')!=0
             or knowledge.get('gf_bindings')!=0 or knowledge.get('released') is not False
             or final.get('valid') is not True or final.get('gf_bindings')!=0):
            raise DiKBridgeError('Rapport diK inattendu : admission non autorisée')
        return {'format':'spek.dik-real-native-offline-test/1.0',
                'status':'DIK_SIX_NATIVE_STEPS_PASS_ON_SAMPLE_NOT_AGRICULTURE',
                'native_commands_executed':list(reports),
                'source_sample_sha256':_sha(sample),
                'sample_lexemes':imported['lexemes'],
                'french_lexeme_candidates':candidate['candidate_lexemes'],
                'semantik_knowledge_entries':knowledge['entries'],
                'gf_functions_created':0,'approved_kristal_crosswalks':0,
                'agriculture_semantic_lexical_mapping_proven':False,
                'gf_agriculture_runtime_proven':False,
                'publication_authorized':False,
                'architect_contract':discover(root=dic,architect=architect)}


def lexical_requirements(*, requirements:dict, source_sha256:str) -> dict:
    """Groupe les références de sujet/objet déjà sélectionnées ; aucune recherche de mot automatique."""
    if (requirements.get('kristal_identity')!='agriculture'
            or requirements.get('authority')!='PRIVATE_GROUNDING_AND_REQUIREMENTS_ONLY'
            or requirements.get('source_state_sha256')!=source_sha256):
        raise DiKBridgeError('Cahier Agriculture non vérifié pour diK')
    tasks=requirements.get('gf_development_tasks')
    if not isinstance(tasks,list) or len(tasks)!=96:
        raise DiKBridgeError('96 tâches GF exactes requises')
    concepts:dict[str,dict] = {}
    for task in tasks:
        if task.get('mapping_status')!='UNMAPPED_NEEDS_EXPLICIT_CONTRACT':
            raise DiKBridgeError('Statut de mapping modifié sans révision')
        for pos in ('subject','object'):
            item=task.get(pos)
            if not isinstance(item,dict) or item.get('kind')!='item':
                continue
            ref=item.get('id')
            if not isinstance(ref,str) or not ref.startswith('urn:kristal:agriculture:'):
                raise DiKBridgeError('Identité de concept incompatible')
            c=concepts.setdefault(ref,{'semantic_ref':ref,'sections':set(), 'occurrences':0,
                                       'lexeme_ref':None,'gf_binding':None,
                                       'review_status':'PENDING_SEMANTIC_LEXICAL_REVIEW', 'source_assertion_links':[]})
            c['sections'].add(task['section_id']);c['occurrences']+=1
            if isinstance(task.get('assertion_id'),str) and isinstance(task.get('source_pointer'),str):
                c['source_assertion_links'].append({'id':task['assertion_id'], 'pointer':task['source_pointer']})
    data=[dict(c,sections=sorted(c['sections'])) for _,c in sorted(concepts.items())]
    predicates=Counter(t['predicate'] for t in tasks)
    return {'format':'spek.agriculture-dik-lexical-needs/1.0',
            'status':'CANDIDATE_ONLY_NOT_MAPPED','source_state_sha256':source_sha256,
            'source_assertion_tasks':len(tasks), 'distinct_predicates':len(predicates),
            'semantic_references':len(data), 'items':data,
            'predicates':[{'predicate':k,'task_count':v} for k,v in sorted(predicates.items())],
            'dik_crosswalks_approved':0,'gf_bindings_approved':0,
            'purpose':'Explicit domain dictionary review; no L/Q/P or linguistic sense inferred',
            'publication_authorized':False}
