from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'scripts/pont_gf_wordbench_agriculture.py'
spec=importlib.util.spec_from_file_location('spek_wordbench_bridge_tests',FILE)
bridge=importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class FrenchPilotTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home=Path(self.tmp.name)
        self.wb=self.home/'GF_Wordbench'
        self.source=self.wb/'src/gf_wordbench/practical'
        self.source.mkdir(parents=True)
        for name in (self.wb/'src/gf_wordbench/__init__.py',self.source/'__init__.py'):
            name.write_text('',encoding='utf-8')
        self.wb.joinpath('pilots/practical_generation_v1/Fre').mkdir(parents=True)
        self.wb.joinpath('profiles').mkdir(parents=True)
        (self.wb/'pyproject.toml').write_text('[project]\nname="stub"\n',encoding='utf-8')
        (self.wb/'pilots/practical_generation_v1/Fre/pilot_manifest.json').write_text('{}')
        (self.wb/'profiles/practical_generation_v1.json').write_text('{}')
        self.rgl=self.home/'RGL'
        (self.rgl/'src/french').mkdir(parents=True)
        (self.rgl/'src/french/GrammarFre.gf').write_text('')
        self.gf=self.home/'gf.exe'
        self.gf.write_text('not-executable')
        self.code='''import json,sys\nif 'check' in sys.argv:\n print(json.dumps({'language':'Fre','status':'preflight_ok','gf_executed':False,'scenario_ids':['scenario'+str(i) for i in range(15)],'scenario_count':15,'gold_approved':False,'lexical_status':'provisional_unreviewed'}))\nelse:\n print(json.dumps({'language':'Fre','scenarios':[{'id':'factual-present','status':'candidate_for_review'}],'review_template_path':'C:/private/review_template.json'}))\n'''
        (self.source/'pilot.py').write_text(self.code,encoding='utf-8')

    def test_no_promotion_of_defluens_pilot(self):
        result=bridge.check_french_pilot(wordbench=self.wb,rgl_root=self.rgl,gf_exe=self.gf)
        self.assertTrue(result['wordbench_native_preflight_ok'])
        self.assertEqual(result['prepared_french_scenarios'],15)
        self.assertEqual(result['status'],'FRENCH_DEFLUENS_PILOT_READY_TO_PROBE_NOT_AGRICULTURE')
        self.assertFalse(result['agriculture_domain_profile_proven'])
        self.assertFalse(result['gf_run_executed'])
        self.assertFalse(result['publication_authorized'])

    def test_accepts_optional_nested_root(self):
        result=bridge.check_french_pilot(wordbench=self.home,rgl_root=self.rgl,gf_exe=self.gf)
        self.assertTrue(result['wordbench_native_preflight_ok'])

    def test_missing_rgl_prevents_readiness(self):
        result=bridge.check_french_pilot(wordbench=self.wb,rgl_root=self.home/'nonexistent',gf_exe=self.gf)
        self.assertEqual(result['status'],'BLOCKED_FRENCH_RGL_OR_GF')

    def test_native_preflight_failure_is_explicit(self):
        (self.source/'pilot.py').write_text('raise SystemExit(2)',encoding='utf-8')
        result=bridge.check_french_pilot(wordbench=self.wb,rgl_root=self.rgl,gf_exe=self.gf)
        self.assertEqual(result['status'],'BLOCKED_WORDBENCH_PREFLIGHT')
        self.assertTrue(result['errors'])

    def test_unsupported_scenario_is_refused_before_gf(self):
        with self.assertRaises(bridge.WordBenchBridgeError):
            bridge._launch_native(self.wb,'run',gf_exe=self.gf,rgl_root=self.rgl,
                                  out=self.home/'private',scenario='anything')

    def test_requirements_cannot_pass_if_references_unverified(self):
        repo=self.home/'Spek'
        (repo/'scripts').mkdir(parents=True)
        (repo/'scripts/verifier_candidature_agriculture.py').write_text('def verify(*args): raise ValueError("source manipulated")')
        source=self.home/'file.json'
        source.write_text('{}')
        with self.assertRaisesRegex(ValueError,'source manipulated'):
            bridge.requirements_from_v8(spek=repo,source=source,private_root=self.home)

if __name__=='__main__':unittest.main()
