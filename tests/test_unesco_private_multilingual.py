import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from spek.unesco_private_drafts import write_private
from spek.unesco_private_multilingual import write_private as assemble,prepare,AssembleError

class TestMultilingual(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory(); self.addCleanup(t.cleanup)
        self.root=pathlib.Path(t.name)
        self.h={'profile':'kristal.integration.unesco-mt1-10-semantic-handoff/1.0',
                'branch':'unesco-mt1-10','semantic_grain':'one_branch_kristal',
                'publication_authorized':False,'authoritative_authoring_checked':False,
                'locale':'en','view_sha256':'view-en',
                'graph_id':'branch-graph-1','namespace_id':'urn:unesco:mt1-10',
                'selections':[{'unesco_id':'concept10','local_kq':'KQ1',
                  'lexical':{'status':'direct','term':'Education'},
                  'assertions':[{'id':'KA1','subject':'KQ1','predicate':'KP2',
                    'object':{'kind':'entity','id':'KQ2'},'sources':['KS1']}]}]}
        self.p={'profile':'spek.unesco-mt1-10-frozen-phrases/1.0',
                'branch':'unesco-mt1-10','locale':'en','view_sha256':'view-en',
                'items':{'KA1':{'text':'Example sentence.','channel':'semantik_architect',
                                'status':'draft','provenance_ref':'capture-1'}}}
        self.dirs=[]

    def draft(self,locale='en'):
        h=json.loads(json.dumps(self.h));p=json.loads(json.dumps(self.p))
        h['locale']=p['locale']=locale
        h['view_sha256']=p['view_sha256']='view-'+locale
        h['selections'][0]['lexical']['term']='Éducation' if locale=='fr' else 'Education'
        out=self.root/('draft-'+locale)
        hf=self.root/('handoff-'+locale+'.json'); pf=self.root/('phrases-'+locale+'.json')
        hf.write_text(json.dumps(h),encoding='utf8');pf.write_text(json.dumps(p),encoding='utf8')
        write_private(hf,pf,out)
        self.dirs.append(out)
        return out

    def test_assembled_projections_share_one_kristal_not_translation(self):
        self.draft('fr');self.draft('en')
        r=assemble(self.dirs,self.root/'multilingual')
        self.assertEqual(r['available_article_projections'],2)
        self.assertEqual(r['unfilled_article_slots'],572)
        self.assertEqual(r['available_locales'],['en','fr'])
        self.assertFalse(r['public_release_authorized'])
        self.assertEqual((self.root/'multilingual/en/concept10.md').read_bytes(),
                         (self.root/'draft-en/concept10.md').read_bytes())
        self.assertTrue((self.root/'multilingual/index.md').is_file())
        self.assertEqual(len(list((self.root/'multilingual').rglob('concept10.md'))),2)

    def test_single_locale_does_not_fill_missing_573(self):
        self.draft('en');r=prepare(self.dirs)[1]
        self.assertEqual(r['available_article_projections'],1)
        self.assertEqual(r['unfilled_article_slots'],573)

    def test_tampered_article_refused(self):
        d=self.draft('en')
        (d/'concept10.md').write_text('tampered',encoding='utf8')
        with self.assertRaisesRegex(AssembleError,'digest mismatch'):
            prepare(self.dirs)

    def test_duplicate_locale_refused(self):
        self.draft('en'); self.dirs.append(self.dirs[0])
        with self.assertRaisesRegex(AssembleError,'Duplicate locale'):
            prepare(self.dirs)

    def test_graph_mismatch_refused(self):
        self.draft('en');self.h['graph_id']='other-branch';self.draft('fr')
        with self.assertRaisesRegex(AssembleError,'Multiple canonical'):
            prepare(self.dirs)

    def test_semantic_drift_refused(self):
        self.draft('en');self.h['selections'][0]['assertions'][0]['sources']=['KS9'];self.draft('fr')
        with self.assertRaisesRegex(AssembleError,'Semantic drift'):
            prepare(self.dirs)

    def test_fake_public_flag_refused(self):
        d=self.draft('en');f=d/'manifest.json';m=json.loads(f.read_text('utf8'))
        m['public_release_authorized']=True;f.write_text(json.dumps(m),encoding='utf8')
        with self.assertRaisesRegex(AssembleError,'approval'):
            prepare(self.dirs)

    def test_extra_unlisted_file_refused(self):
        d=self.draft('en');(d/'private-key.txt').write_text('secret',encoding='utf8')
        with self.assertRaisesRegex(AssembleError,'Unexpected'):
            prepare(self.dirs)

    def test_symlinked_article_refused(self):
        d=self.draft('en');p=d/'concept10.md';p.unlink()
        target=self.root/'copied.md';target.write_text('text',encoding='utf8');p.symlink_to(target)
        with self.assertRaisesRegex(AssembleError,'Symlinked'):
            prepare(self.dirs)

if __name__=='__main__':unittest.main()
