"""Immutable, private editorial handoff for recursive compositions.

The caller supplies every template, binding, assertion and CommunicationRequest.
This module never chooses facts, approves relationships, renders language or publishes.
An exported handoff contains private source IDs and MUST remain outside public Git.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from spek.core import ValidationError
from spek.slot_dialogue import KIND_POLICY, compose_request
from .commands import load, read_instance
from .engine import Library, Leaf, Node
from .source_binding import verify_v11_assertion_refs

FORMAT = 'spek.private-editorial-handoff/1.0'


def _hash(path: Path) -> str:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 20_000_000:
        raise ValidationError('Fichier d’entrée absent, symbolique ou trop volumineux')
    return 'sha256:' + hashlib.sha256(path.read_bytes()).hexdigest()


def _relations(value: dict) -> list[dict]:
    """Traverse only nodes already validated by the recursive resolver."""
    found: list[dict] = []
    def walk(node: dict) -> None:
        if 'editorial_relation' in node:
            rel = node['editorial_relation']
            found.append({'template_ref': node['template_ref'],
                          'relation_tag': rel['relation_tag'],
                          'status': rel['status'],
                          'source_assertion_refs': sorted(rel['source_assertion_refs'])})
        for v in node.get('bindings', {}).values():
            if isinstance(v, dict) and v.get('node_type') == 'repeat':
                children = v['instances']
            else:
                children = v if isinstance(v, list) else [v]
            for child in children:
                if isinstance(child, dict) and child.get('node_type') == 'template_ref':
                    walk(child)
    walk(value)
    return sorted(found, key=lambda item: (item['template_ref'],item['relation_tag'],','.join(item['source_assertion_refs'])))


def prepare(root: Path, instance_path: Path, requests_dir: Path, language: str,
            *, source_graph: Path | None = None, identity_map: Path | None = None) -> dict[str, Any]:
    """Produce a deterministic private manifest, fail closed on orphan anchors.

    This is a source/request *consistency* check, not logical entailment or C1/C2/C3.
    """
    root = Path(root).resolve()
    instance_path = Path(instance_path)
    requests_dir = Path(requests_dir)
    if requests_dir.is_symlink() or not requests_dir.is_dir():
        raise ValidationError('Dossier de requêtes privé absent ou symbolique')
    resolved = load(root, instance_path)
    if not resolved.leaves:
        raise ValidationError('Composition sans champs linguistiques')
    definitions = Library(root / 'template_library').definitions
    used_templates: set[str] = set()
    def visit(node: Node) -> None:
        used_templates.add(node.template_ref)
        for _, group in node.ordered:
            for item in group:
                if isinstance(item, Node): visit(item)
    visit(resolved.root)
    locks=[]
    for ref in sorted(used_templates):
        obj = definitions[ref]
        category, name = obj['template_id'].split('.',1)
        template_path = root / 'template_library' / category / 'templates' / (name + '.json')
        locks.append({'template_ref':ref,'sha256':_hash(template_path)})
    fields=[]
    selected_refs=set()
    for leaf in resolved.leaves:
        if not leaf.source_assertion_refs:
            raise ValidationError('Un champ n’est pas ancré dans des assertions sélectionnées')
        filename=Path(leaf.request_ref).name
        reqpath=requests_dir/filename
        if not reqpath.resolve().is_relative_to(requests_dir.resolve()):
            raise ValidationError('Chemin de requête hors du dossier privé')
        request=read_instance(reqpath)
        _,force,kinds,limit=KIND_POLICY[leaf.kind]
        bounded=compose_request(request,{'force':force,'block_kinds':kinds,'max_length':limit},language=language)
        if bounded['semantic_graph'] != request['semantic_graph'] or bounded['obligations'] != request['obligations']:
            raise ValidationError('Faits ou obligations modifiés par le cadrage Spek')
        source_refs=set()
        for obligation in request['obligations']:
            refs=obligation.get('source_refs')
            if not isinstance(refs,list) or not refs:
                raise ValidationError('Une obligation SemantiK ne possède pas de références source')
            source_refs.update(refs)
        anchored=set(leaf.source_assertion_refs)
        if source_refs != anchored:
            raise ValidationError('Désaccord entre références sélectionnées et obligations SemantiK')
        selected_refs.update(anchored)
        fields.append({'realization_key':leaf.key,'request_file':filename,'request_sha256':_hash(reqpath),
                       'source_assertion_refs':sorted(anchored), 'slot_kind':leaf.kind, 'required_force':force,
                       'discourse_function':leaf.discourse_function,
                       'obligations_count':len(request['obligations']),
                       'allowed_block_kinds':bounded['constraints']['allowed_block_kinds']})
    original = read_instance(instance_path)
    relations=_relations(original)
    for relation in relations:
        if not set(relation['source_assertion_refs']).issubset(selected_refs):
            raise ValidationError('Relation rhétorique liée à des assertions non retenues')
    source={'kind':'not_supplied','sha256':None,'assertion_existence_checked':False}
    if identity_map is not None and source_graph is None:
        raise ValidationError('Table d’identité sans graphe source v11')
    if source_graph is not None:
        graph_path=Path(source_graph)
        check=verify_v11_assertion_refs(resolved,graph_path,identity_map)
        source={'kind':'kristal_v11_semantic_graph','sha256':_hash(graph_path),
                'assertion_existence_checked':True,
                'assertions_in_supplied_graph':check['assertions_in_supplied_graph'],
                'identity_migration_sha256':_hash(Path(identity_map)) if identity_map is not None else None,
                'assertions_mapped':check['assertions_translated_by_explicit_map']}
    return {'format':FORMAT,'status':'PRIVATE_UNQUALIFIED_NOT_PUBLISHABLE',
            'instance_id':resolved.instance_id,'instance_sha256':_hash(instance_path),
            'language':language,'source':source,'template_locks':locks,
            'fields':fields,'selected_assertion_count':len(selected_refs),
            'relations_declared_unverified':relations,
            'qualification':{'semantic_entailment_checked':False,
                             'semantik_result_pairs_verified':False,
                             'rhetorical_relations_approved':False,
                             'c1_c2_c3_approved':False,
                             'publication_authorized':False}}


def verify(lock: dict, root: Path, instance_path: Path, requests_dir: Path,
           *, source_graph: Path | None = None, identity_map: Path | None = None) -> dict:
    """Recalculate every content pin and reject any changed input."""
    if not isinstance(lock,dict) or lock.get('format') != FORMAT:
        raise ValidationError('Format de verrou éditorial incorrect')
    fresh=prepare(root,instance_path,requests_dir,lock['language'],source_graph=source_graph,identity_map=identity_map)
    if fresh != lock:
        raise ValidationError('Verrou éditorial altéré ou obsolète : les sources ont changé')
    return {'format':'spek.private-editorial-verification/1.0','status':'PASS_PRIVATE_UNQUALIFIED',
            'locked_templates':len(fresh['template_locks']),'fields':len(fresh['fields']),
            'selected_assertions':fresh['selected_assertion_count'],
            'publication_authorized':False}
