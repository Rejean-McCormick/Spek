"""Regressions du pilote source littérale. Toutes les données de test sont synthétiques."""
from __future__ import annotations
import importlib.util
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('spek_agriculture_source_preview',HERE/'scripts/pilote_agriculture_sol.py')
mod=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(mod)

class PilotSourcePreviewTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.root=Path(t.name)
        self.graph=self.root/'graph.json'
        rows=[]
        for i in range(408):
            rows.append({'id':f'KA-SYNTH-{i:03d}','subject':f'KQ-SYNTH-{i:03d}',
                         'predicate':mod.DEFINITION_PROPERTY,
                         'object':{'kind':'literal','datatype':'string','language':'fr',
                                   'value':'Phrase synthétique de test numéro '+str(i)+'.'},
                         'sources':['KS-SYNTH-TEST']})
        for section,entries in mod.SECTIONS:
            for _,ka in entries:
                row=rows.pop()
                row['id']=ka
                row['object']['value']='Contenu de test seulement.'
                rows.insert(0,row)
        self.assertEqual(len(rows),408)
        self.graph.write_text(json.dumps({'schema_version':'11.0','artifact_type':'kristal_semantic_graph',
                     'assertions':rows},ensure_ascii=False),encoding='utf-8')
        self.hash=hashlib.sha256(self.graph.read_bytes()).hexdigest()
        self.patch=patch.object(mod,'EXPECTED_GRAPH_SHA256',self.hash)
        self.patch.start();self.addCleanup(self.patch.stop)

    def test_real_structure_builds_and_verifies_with_synthetic_test_data(self):
        site=self.root/'site'
        outcome=mod.build_preview(self.graph,site)
        self.assertEqual(outcome['definitions'],18)
        self.assertEqual(mod.verify_preview(site)['definitions'],18)
        html=(site/'index.html').read_text(encoding='utf-8')
        self.assertEqual(html.count('Contenu de test seulement.'),18)
        self.assertIn('NON PUBLIABLE',html)
        self.assertNotIn('KA-SYNTH-',html)
        audit=json.loads((site/'audit-prive.json').read_text(encoding='utf-8'))
        self.assertFalse(audit['actual_spek_template_engine_executed'])
        self.assertFalse(audit['semantik_gf_executed'])
        self.assertFalse(audit['publication_authorized'])

    def test_tamper_detection(self):
        site=self.root/'site';mod.build_preview(self.graph,site)
        with (site/'index.html').open('a',encoding='utf-8') as f:f.write('MODIFIED')
        with self.assertRaisesRegex(mod.PreviewError,'modifié'):
            mod.verify_preview(site)

    def test_refuses_source_change(self):
        with self.graph.open('a',encoding='utf-8') as f:f.write(' ')
        with self.assertRaisesRegex(mod.PreviewError,'Empreinte'):
            mod.build_preview(self.graph,self.root/'site')
        self.assertFalse((self.root/'site').exists())

    def test_refuses_unknown_selected_assertion(self):
        data=json.loads(self.graph.read_text(encoding='utf-8'))
        data['assertions']=[a for a in data['assertions'] if a['id']!='KA15833957396088538396077']
        data['assertions'].append({'id':'KA-NON-SELECTED','predicate':mod.DEFINITION_PROPERTY,
                                  'object':{'kind':'literal','datatype':'string','language':'fr','value':'Fictif'},
                                  'sources':['KS-SYNTH-TEST']})
        self.graph.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
        with patch.object(mod,'EXPECTED_GRAPH_SHA256',hashlib.sha256(self.graph.read_bytes()).hexdigest()):
            with self.assertRaisesRegex(mod.PreviewError,'inexistante'):
                mod.build_preview(self.graph,self.root/'site')

    def test_refuses_existing_or_git_destination(self):
        site=self.root/'site';site.mkdir()
        with self.assertRaisesRegex(mod.PreviewError,'déjà présent'):
            mod.build_preview(self.graph,site)
        git=self.root/'checkout';git.mkdir();(git/'.git').mkdir()
        with self.assertRaisesRegex(mod.PreviewError,'dépôt Git'):
            mod.build_preview(self.graph,git/'site')

    def test_no_internal_mutation_and_doctor_does_not_claim_agriculture(self):
        s=self.root/'spek';s.mkdir();a=self.root/'architect';a.mkdir()
        report=mod.doctor(s,a,self.root/'not-installed-gf.exe')
        self.assertFalse(report['agriculture_profile_qualified'])
        self.assertTrue(report['no_files_modified'])
        self.assertEqual(sorted(x.name for x in self.root.iterdir()),['architect','graph.json','spek'])

    def test_export_exact_18_sources_to_existing_spek_template_contract(self):
        dest=self.root/'spek-source-instance'
        report=mod.export_spek_literal_fixture(self.graph,dest)
        self.assertEqual(report['assertions'],18)
        self.assertEqual(report['text_slots'],36)
        inst=json.loads((dest/'instance.json').read_text(encoding='utf-8'))
        bundle=json.loads((dest/'realizations-source-litterale-fr.json').read_text(encoding='utf-8'))
        self.assertEqual(inst['template_ref'],'wiki.domain-primer-source-bound@1.0.0')
        self.assertEqual(inst['authority'],'editorial_bindings_explicit_not_approved')
        sections=inst['bindings']['sections']['instances']
        self.assertEqual(len(sections),4)
        self.assertEqual(len(bundle['entries']),36)
        self.assertTrue(all(v['fr']['status']=='fixture' for v in bundle['entries'].values()))
        self.assertEqual(sum(bool(v['fr'].get('source_assertion_id')) for v in bundle['entries'].values()),18)
        self.assertNotIn('requests/',str(list(dest.iterdir())))
        self.assertFalse(json.loads((dest/'audit-prive.json').read_text(encoding='utf-8'))['publication_authorized'])

    def test_preview_does_not_appear_inside_spek_root(self):
        with self.assertRaisesRegex(mod.PreviewError,'dépôt SPEK'):
            mod.build_preview(self.graph,self.root/'my-spek'/'preview',spek_root=self.root/'my-spek')

if __name__=='__main__':unittest.main()

