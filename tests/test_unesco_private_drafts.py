import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from spek.unesco_private_drafts import prepare,DraftError
class TestPrivateDrafts(unittest.TestCase):
 def setUp(self):
  self.h={'profile':'kristal.integration.unesco-mt1-10-semantic-handoff/1.0','branch':'unesco-mt1-10','semantic_grain':'one_branch_kristal','publication_authorized':False,'authoritative_authoring_checked':False,'locale':'fr','view_sha256':'abcdef','graph_id':'g1','namespace_id':'urn:unesco:pilot','selections':[{'unesco_id':'concept10','local_kq':'KQ1','lexical':{'status':'direct','term':'Éducation'},'assertions':[{'id':'KA1','subject':'KQ1','predicate':'KP2','object':{'kind':'entity','id':'KQ2'},'sources':['KS1']}]}]}
  self.p={'profile':'spek.unesco-mt1-10-frozen-phrases/1.0','branch':'unesco-mt1-10','locale':'fr','view_sha256':'abcdef','items':{'KA1':{'text':'Un texte <inclus> vérifié pour le rendu privé.','channel':'semantik_architect','status':'draft','provenance_ref':'capture-local-1'}}}
 def test_generates_only_frozen_text_no_public_rights(self):
  pages,manifest=prepare(self.h,self.p)
  self.assertIn('concept10.md',pages);self.assertIn('texte',pages['concept10.md'])
  self.assertNotIn('<inclus>',pages['concept10.md'])
  self.assertIn('`KS1`',pages['concept10.md'])
  self.assertFalse(manifest['public_release_authorized'])
 def test_missing_ka_refuses(self):
  self.p['items']={}
  with self.assertRaises(DraftError):prepare(self.h,self.p)
 def test_bad_source_ref_refuses(self):
  self.h['selections'][0]['assertions'][0]['sources']=[]
  with self.assertRaises(DraftError):prepare(self.h,self.p)
 def test_no_kq_refuses(self):
  self.h['selections']=[]
  with self.assertRaises(DraftError):prepare(self.h,self.p)
 def test_rejects_falsely_qualified_ai_text(self):
  v=self.p['items']['KA1']
  v.update({'channel':'ai_preconstructed','status':'qualified','model_id':'a','generation_ref':'b','prompt_sha256':'a'*64})
  with self.assertRaisesRegex(DraftError,'Unattested/qualified'):
   prepare(self.h,self.p)
 def test_rejects_falsely_qualified_semantik(self):
  self.p['items']['KA1']['status']='qualified'
  with self.assertRaisesRegex(DraftError,'Unattested/qualified'):
   prepare(self.h,self.p)
 def test_reviewed_ai_requires_external_review(self):
  v=self.p['items']['KA1']
  v.update({'channel':'ai_preconstructed','status':'reviewed','model_id':'actual-model','generation_ref':'actual-call','prompt_sha256':'a'*64})
  with self.assertRaisesRegex(DraftError,'review'):
   prepare(self.h,self.p)
  v['human_review']={'status':'approved','review_ref':'review-file-1'}
  pages,manifest=prepare(self.h,self.p)
  self.assertFalse(manifest['runtime_attestation_verified'])
 def test_fingerprint_is_independent_of_language(self):
  _,x=prepare(self.h,self.p)
  self.h['locale']=self.p['locale']='en';self.h['selections'][0]['lexical']['term']='Education'
  _,y=prepare(self.h,self.p)
  self.assertEqual(x['semantic_index']['concept10']['assertions_sha256'],y['semantic_index']['concept10']['assertions_sha256'])
 def test_14_language_scope_does_not_imply_qualification(self):
  self.h['locale']=self.p['locale']='et'
  pages,manifest=prepare(self.h,self.p)
  self.assertEqual(manifest['locale'],'et');self.assertFalse(manifest['runtime_attestation_verified'])
if __name__=='__main__':unittest.main()
