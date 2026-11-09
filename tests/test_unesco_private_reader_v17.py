import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'spek'))
from unesco_private_reader_v17 import build,ReaderError

def data():
    nodes=[{'unesco_id':f'concept{i}','label_en':('Test <unsafe>' if i==10 else f'Test {i}')} for i in range(1,42)]
    stmts=[{'unesco_id':nodes[i%41]['unesco_id'],'proposal_ref':f'P{i}',
            'evidence_status':'NOT_ATTESTED','editorial_selected_en':('Content <script>' if i==0 else f'Claim {i}')}
           for i in range(85)]
    links=[{'source':'concept1','target':'concept2','relation':'related'} for _ in range(61)]
    graph={'branch':'unesco-mt1-10','canonical_graph_built':False,
      'nodes':nodes,'candidate_statements':stmts,'skos_internal_observations':links}
    identities={'concepts':[{'unesco_id':n['unesco_id'],'provisional_KQ':f'KQ{i+1}',
        'qid_candidate_unapproved':''} for i,n in enumerate(nodes)]}
    return graph,identities

class TestPrivateReader(unittest.TestCase):
 def test_full_private_site_no_html_injection(self):
    files=build(*data())
    self.assertEqual(len(files),43)
    self.assertIn(b'&lt;script&gt;',files['reader_en/concept1.html'])
    self.assertNotIn(b'<script>',files['reader_en/concept1.html'])
    self.assertIn(b'NOT canonical articles',files['reader_en/index.html'])
 def test_no_canonical_laundering(self):
    g,m=data();g['canonical_graph_built']=True
    with self.assertRaises(ReaderError):build(g,m)
 def test_reject_attested_claim_from_editorial(self):
    g,m=data();g['candidate_statements'][0]['evidence_status']='ATTESTED'
    with self.assertRaises(ReaderError):build(g,m)
 def test_reject_external_relation(self):
    g,m=data();g['skos_internal_observations'][0]['target']='concept99999'
    with self.assertRaises(ReaderError):build(g,m)
if __name__=='__main__':unittest.main()
