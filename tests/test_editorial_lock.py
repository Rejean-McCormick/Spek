"""Fail-closed end-to-end private composition/request/template identity locks."""
import json
from pathlib import Path
import pytest

from spek.composition.editorial_lock import prepare, verify
from spek.composition.source_binding import verify_v11_assertion_refs
from spek.composition.commands import load
from spek.core import ValidationError

REPO = Path(__file__).resolve().parents[1]


def fixture(tmp_path):
    reqs=tmp_path/'requests'; reqs.mkdir()
    instance={
        'format':'spek.composition-instance/1.0','instance_id':'test-editorial-lock',
        'template_ref':'rhetorical.definition@1.0.0',
        'authority':'editorial_bindings_explicit_not_approved',
        'bindings':{s:{'node_type':'text_slot','kind':kind,'realization_key':s,
                       'communication_request_ref':f'requests/{s}.json',
                       'source_assertion_refs':['old:source-1']}
                    for s,kind in [('term','concept'),('definition','definition')]}}
    instance_path=tmp_path/'instance.json'; instance_path.write_text(json.dumps(instance),encoding='utf-8')
    for s,force in [('term','PRESENT'),('definition','ASSERT')]:
        request={'schema_version':'1.0','semantic_graph':{'graph_id':'graph:test','nodes':[],
            'statements':[{'id':'s1','source_refs':['old:source-1']}]},
            'obligations':[{'obligation_id':'o1','semantic_refs':['s1'],'force':force,
                            'source_refs':['old:source-1']}],
            'context':{'target_language':'fr'},
            'constraints':{'allowed_block_kinds':['utterance'], 'max_length':1000},
            'capability_profile':'agriculture-reference-1'}
        (reqs/f'{s}.json').write_text(json.dumps(request),encoding='utf-8')
    graph=tmp_path/'graph.json';graph.write_text(json.dumps({
        'schema_version':'11.0','artifact_type':'kristal_semantic_graph',
        'assertions':[{'id':'KA100'}]}),encoding='utf-8')
    migration=tmp_path/'identity-map.json';migration.write_text(json.dumps({
        'by_kind':{'A':{'old:source-1':'KA100'}}}),encoding='utf-8')
    return instance_path,reqs,graph,migration


def test_explicit_v6_to_v11_identity_mapping(tmp_path):
    instance,reqs,graph,migration=fixture(tmp_path)
    resolved=load(REPO,instance)
    with pytest.raises(ValidationError):
        verify_v11_assertion_refs(resolved,graph)
    evidence=verify_v11_assertion_refs(resolved,graph,migration)
    assert evidence['assertions_translated_by_explicit_map']==1


def test_private_lock_recalculates_all_pins(tmp_path):
    instance,reqs,graph,migration=fixture(tmp_path)
    lock=prepare(REPO,instance,reqs,'fr',source_graph=graph,identity_map=migration)
    assert lock['selected_assertion_count']==1
    assert len(lock['fields'])==2
    assert lock['source']['assertions_mapped']==1
    assert verify(lock,REPO,instance,reqs,source_graph=graph,identity_map=migration)['fields']==2
    request=reqs/'definition.json'
    data=json.loads(request.read_text());data['semantic_graph']['statements'][0]['source_refs']=['old:altered']
    request.write_text(json.dumps(data))
    with pytest.raises(ValidationError):
        verify(lock,REPO,instance,reqs,source_graph=graph,identity_map=migration)


def test_unanchored_or_mismatched_obligation_is_refused(tmp_path):
    instance,reqs,graph,migration=fixture(tmp_path)
    data=json.loads(instance.read_text());data['bindings']['term']['source_assertion_refs']=[]
    instance.write_text(json.dumps(data))
    with pytest.raises(ValidationError):
        prepare(REPO,instance,reqs,'fr')
    data['bindings']['term']['source_assertion_refs']=['old:source-1']
    instance.write_text(json.dumps(data))
    request=reqs/'term.json';r=json.loads(request.read_text())
    r['obligations'][0]['source_refs']=['old:other']
    request.write_text(json.dumps(r))
    with pytest.raises(ValidationError):
        prepare(REPO,instance,reqs,'fr')


def test_reused_request_file_refused_even_with_distinct_realization_keys(tmp_path):
    instance,reqs,graph,migration=fixture(tmp_path)
    data=json.loads(instance.read_text(encoding='utf-8'))
    data['bindings']['definition']['communication_request_ref']='requests/term.json'
    instance.write_text(json.dumps(data),encoding='utf-8')
    with pytest.raises(ValidationError,match='même requête'):
        prepare(REPO,instance,reqs,'fr',source_graph=graph,identity_map=migration)


def test_private_preview_refuses_other_git_checkout(tmp_path):
    from spek.composition.commands import preview
    instance,reqs,_,_=fixture(tmp_path)
    git_root=tmp_path/'other-public-repository'
    (git_root/'.git').mkdir(parents=True)
    out=git_root/'private-preview'
    with pytest.raises(ValidationError,match='dépôt Git'):
        preview(REPO,instance,tmp_path/'missing-realizations.json','fr',out)
    assert not out.exists()
