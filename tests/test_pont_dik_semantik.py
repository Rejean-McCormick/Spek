from __future__ import annotations
from pathlib import Path
import importlib.util
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('spek_dik_bridge_test',ROOT/'scripts/pont_dik_semantik.py')
dik=importlib.util.module_from_spec(spec);spec.loader.exec_module(dik)

class NativeDiKBridgeTests(unittest.TestCase):
    def test_missing_dik_does_not_claim_coverage(self):
        with tempfile.TemporaryDirectory() as t:
            result=dik.discover(root=Path(t)/'absent')
            self.assertFalse(result['dik_source_found'])
            self.assertFalse(result['agriculture_lexical_approval_proven'])
            self.assertEqual(result['status'],'DIK_NOT_FOUND')

    def test_fake_dik_directory_not_accepted(self):
        with tempfile.TemporaryDirectory() as t:
            (Path(t)/'src'/'dik').mkdir(parents=True)
            (Path(t)/'src'/'dik'/'cli.py').write_text('')
            with self.assertRaises(dik.DiKBridgeError):
                dik.root_from_hint(Path(t))

    def test_exact_lexical_requirements_with_no_fake_identity(self):
        sha='a'*64
        tasks=[]
        for i in range(96):
            tasks.append({'section_id':'soil' if i<40 else 'crop',
                          'predicate':'agriculture.influences' if i%2 else 'agriculture.has_definition',
                          'mapping_status':'UNMAPPED_NEEDS_EXPLICIT_CONTRACT',
                          'subject':{'kind':'item','id':'urn:kristal:agriculture:concept:soil'},
                          'object':({'kind':'item','id':'urn:kristal:agriculture:concept:yield'}
                                    if i%2 else {'kind':'string','value':'sol'})})
        bundle={'kristal_identity':'agriculture','authority':'PRIVATE_GROUNDING_AND_REQUIREMENTS_ONLY',
                'source_state_sha256':sha,'gf_development_tasks':tasks}
        res=dik.lexical_requirements(requirements=bundle,source_sha256=sha)
        self.assertEqual(res['source_assertion_tasks'],96)
        self.assertEqual(res['semantic_references'],2)
        self.assertEqual(res['gf_bindings_approved'],0)
        self.assertEqual(res['items'][0]['review_status'],'PENDING_SEMANTIC_LEXICAL_REVIEW')
        self.assertFalse(res['publication_authorized'])
        tasks[0]['mapping_status']='APPROVED'
        with self.assertRaises(dik.DiKBridgeError):
            dik.lexical_requirements(requirements=bundle,source_sha256=sha)

    def test_nonagricultural_reference_fails(self):
        x={'kristal_identity':'agriculture','authority':'PRIVATE_GROUNDING_AND_REQUIREMENTS_ONLY',
           'source_state_sha256':'x','gf_development_tasks':[]}
        x['gf_development_tasks']=[{'section_id':'soil','predicate':'p','mapping_status':'UNMAPPED_NEEDS_EXPLICIT_CONTRACT',
                 'subject':{'kind':'item','id':'wikidata:lexeme:L100'},'object':{'kind':'string','value':'x'}}]*96
        with self.assertRaises(dik.DiKBridgeError):
            dik.lexical_requirements(requirements=x,source_sha256='x')

    def test_native_real_dik_if_snapshot_configured(self):
        import os
        root=os.environ.get('SPEK_TEST_REAL_DIK_ROOT')
        if not root:
            self.skipTest('Le test natif diK complet nécessite SPEK_TEST_REAL_DIK_ROOT')
        report=dik.test_native_fixture(root=Path(root))
        self.assertEqual(report['native_commands_executed'],list(dik.OPERATIONS))
        self.assertEqual(report['gf_functions_created'],0)
        self.assertFalse(report['publication_authorized'])
        self.assertEqual(report['sample_lexemes'],2)

if __name__=='__main__':unittest.main()
