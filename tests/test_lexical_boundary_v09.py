import hashlib
import json
import pytest
from spek.lexical_boundary import inspect_lexical_dependency
from spek.core import ValidationError


def seed(tmp_path):
    data={'schema_version':'1.1','entries':[]}
    blob=json.dumps(data).encode()
    (tmp_path/'lexicon.candidate.json').write_bytes(blob)
    (tmp_path/'manifest.json').write_text(json.dumps({'schema_id':'gf-wordbench.dik-semantik-lexicon/1.0-candidate',
        'status':'DEVELOPMENT_CANDIDATE','released':False,'gf_verified':False,
        'locale':'fr','knowledge_entries':0,'human_reviewed_binding_candidates':0,
        'lexicon_sha256':hashlib.sha256(blob).hexdigest()}))


def test_spek_sees_provenance_without_importing_realization(tmp_path):
    seed(tmp_path)
    r=inspect_lexical_dependency(tmp_path)
    assert r['realizations_imported']==0 and r['publication_eligible'] is False


def test_spek_refuses_forged_release(tmp_path):
    seed(tmp_path)
    manifest=json.loads((tmp_path/'manifest.json').read_text())
    manifest['released']=True
    (tmp_path/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValidationError,match='refuse'):
        inspect_lexical_dependency(tmp_path)


def test_spek_detects_tamper(tmp_path):
    seed(tmp_path)
    (tmp_path/'lexicon.candidate.json').write_text('changed')
    with pytest.raises(ValidationError,match='Empreinte'):
        inspect_lexical_dependency(tmp_path)
