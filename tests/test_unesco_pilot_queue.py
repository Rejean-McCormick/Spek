"""No actual article publication, semantic approval or network is used."""
from __future__ import annotations
import json,unittest
from spek import unesco_pilot as p


class QueueTests(unittest.TestCase):
    def good(self):
        records=[]
        for i in range(1,42):
            records.append({'unesco_id':f'concept{i}','canonical_KQ':None,'canonical_KA':[],'canonical_KS':[],
                'wikidata':{'canonical_exact_match':False,'match_status':'unreviewed_candidate' if i==1 else 'none'},
                'article_projection_status':'not_generated',
                'language_channels':{x:{'label_status':'source_label_present' if x=='en' else 'missing'} for x in p.LOCALES}})
        return {'profile':p.PROFILE_IN,'branch':'unesco-mt1-10','semantic_grain':'one_branch_kristal',
             'not_canonical':True,'not_publication':True,'approval_status':'BLOCKED',
             'wiki_content_extracted':False,'wikidata_mapping_approval':False,
             'article_count':0,'languages':list(p.LOCALES),'records':records}

    def test_41x14(self):
        q=p.build_queue(self.good(),source_sha256='a'*64)
        self.assertEqual(q['projection_queue_size'],574)
        self.assertEqual(q['generated_articles'],0)
        self.assertEqual(q['publication_status'],'BLOCKED')
        self.assertTrue(all(not j['article_built'] for j in q['jobs']))

    def test_reject_fake_canon(self):
        d=self.good();d['records'][0]['canonical_KA']=['KA123']
        with self.assertRaisesRegex(p.PlanningError,'canonical'):
            p.build_queue(d,source_sha256='a'*64)

    def test_reject_auto_publication(self):
        d=self.good();d['approval_status']='APPROVED'
        with self.assertRaisesRegex(p.PlanningError,'authorization'):
            p.build_queue(d,source_sha256='a'*64)

    def test_reject_qid_match_promotion(self):
        d=self.good();d['records'][0]['wikidata']['canonical_exact_match']=True
        with self.assertRaisesRegex(p.PlanningError,'promoted'):
            p.build_queue(d,source_sha256='a'*64)

    def test_reject_auto_language_qualification(self):
        d=self.good();d['records'][0]['language_channels']['fr']['label_status']='qualified'
        with self.assertRaisesRegex(p.PlanningError,'lexical'):
            p.build_queue(d,source_sha256='a'*64)

    def test_reject_missing_locale(self):
        d=self.good();del d['records'][0]['language_channels']['fr']
        with self.assertRaisesRegex(p.PlanningError,'language channels'):
            p.build_queue(d,source_sha256='a'*64)

if __name__=='__main__':unittest.main()
