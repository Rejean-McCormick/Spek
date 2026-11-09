import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'integrations'/'konstellation_light'))
from contract import new_document,validate,ContractError
DIGEST='sha256:'+'a'*64
class ContractTests(unittest.TestCase):
    def test_locale_without_fixed_supported_languages(self):
        doc=new_document('astronomy','urn:kristal:astronomy:state',DIGEST,'ja',[
            {'node_id':'KQ1','label':'星', 'provenance':{'provider':'dik','source_refs':[], 'review_status':'reviewed','review_ref':'review:1'}}])
        self.assertEqual(validate(doc,require_reviewed=True)['locale'],'ja')
    def test_candidate_never_published_by_reader(self):
        doc=new_document('astronomy','urn:kristal:astronomy:state',DIGEST,'fr-CA',[
            {'node_id':'KQ1','definition':'Note candidate.', 'provenance':{'provider':'editorial','source_refs':['source:1'], 'review_status':'candidate'}}])
        with self.assertRaises(ContractError):validate(doc,require_reviewed=True)
    def test_reject_duplicate_identity(self):
        row={'node_id':'KQ1','label':'Term', 'provenance':{'provider':'dik','source_refs':[], 'review_status':'reviewed','review_ref':'r1'}}
        with self.assertRaises(ContractError):new_document('astronomy','urn:kristal:astronomy:state',DIGEST,'en',[row,row])

from from_spek import export
class SpekAdapterTests(unittest.TestCase):
    def test_explicit_mapping_and_review_required(self):
        realizations={'format':'kristal.layout-realizations/0.1','entries':{'d1':{'ja':{'text':'定義', 'status':'reviewed','channel':'ai_preconstructed'}}}}
        mapping={'format':'konstellation.multilingual-mapping/1.0','slug':'astronomy','state_ref':'urn:x','surface_digest':DIGEST,
                 'bindings':[{'node_id':'KQ1','locale':'ja','definition_key':'d1','review_ref':'editor:12','source_refs':['example:source']}]}
        result=export(realizations,mapping)
        self.assertEqual(result['ja']['entries'][0]['definition'],'定義')
        realizations['entries']['d1']['ja']['status']='fixture'
        with self.assertRaises(ContractError):export(realizations,mapping)
