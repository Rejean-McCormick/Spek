import importlib.util
from pathlib import Path
import unittest
P=Path(__file__).resolve().parents[1]/'spek/unesco_editorial_previews_v14.py'
s=importlib.util.spec_from_file_location('spek_v14',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def demo():
 decisions=[]
 for i in range(41):
  c=f'concept{i+1}'
  decisions.append({'type':'IDENTITE','ref':c,'source_uri':f'http://x.example/{c}','label_en':f'Subject {i}',
                    'label_fr':'', 'qid_candidate':None})
 for i in range(85):
  decisions.append({'type':'PROPOSITION','unesco_id':f'concept{1+i%41}','ref':f'P{i}',
                    'chosen_text_en':'<important> source text','decision_editoriale':'PRIVE',
                    'evidence_status':'NOT_ATTESTED'})
 return {'branch':'unesco-mt1-10','editorial_decisions_count':191,'admission_to_canon_authorized':False,'decisions':decisions}
class Tests(unittest.TestCase):
 def test_41_previews_created_escaping_html(self):
  pages=m.compose(demo());self.assertEqual(len(pages),41)
  self.assertIn(b'\\<important\\>',pages['apercus_en/concept1.md'])
 def test_refuse_canonical_claim(self):
  a=demo();a['admission_to_canon_authorized']=True
  with self.assertRaises(m.PreviewError):m.compose(a)
 def test_refuse_unsourced_as_evidence(self):
  a=demo();a['decisions'][41]['evidence_status']='QUALIFIED_KS'
  with self.assertRaises(m.PreviewError):m.compose(a)
 def test_no_empty_concept(self):
  a=demo();a['decisions']=[x for x in a['decisions'] if x.get('unesco_id')!='concept41']
  with self.assertRaises(m.PreviewError):m.compose(a)
if __name__=='__main__':unittest.main()
