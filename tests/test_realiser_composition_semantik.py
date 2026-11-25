"""Isolated regression tests for the additive SPEK→SA runner.

Mocked SA results exercise adapter control flow only. They are not evidence of
actual GF execution, a valid SemantiK result or public qualification.
"""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

FILE = Path(__file__).resolve().parents[1] / "scripts" / "realiser_composition_semantik.py"
SPEC = importlib.util.spec_from_file_location("spek_gf_runner_patch_test", FILE)
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class FileSecurity(unittest.TestCase):
    def test_file_checks(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            good = root / "x.txt"
            good.write_text("hello")
            self.assertEqual(RUNNER._safe_file(good, name="x"), good.resolve())
            with self.assertRaises(ValueError):
                RUNNER._safe_file(root / "missing", name="x")
            with self.assertRaises(ValueError):
                RUNNER._safe_dir(good, name="x")

    def test_reject_existing_or_inside_repo(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            repo = root / "spek"; repo.mkdir()
            with self.assertRaisesRegex(ValueError, "hors du dépôt"):
                RUNNER._outside_git(repo / "out", repo)
            already = root / "out"; already.mkdir()
            with self.assertRaisesRegex(ValueError, "présente"):
                RUNNER._outside_git(already, repo)

    def test_reject_git_worktree(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            repo = root / "spek"; repo.mkdir()
            another = root / "other"; another.mkdir()
            (another / ".git").mkdir()
            with self.assertRaisesRegex(ValueError, "dépôt Git"):
                RUNNER._outside_git(another / "out", repo)

    def test_accept_new_private_target(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            repo = root / "spek"; repo.mkdir()
            target = root / "private" / "edition-1"
            self.assertEqual(RUNNER._outside_git(target, repo), target.resolve())
            self.assertTrue(target.parent.is_dir())
            self.assertFalse(target.exists())

    def test_symlink_path_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            repo = root / "spek"; repo.mkdir()
            file = root / "file.txt"; file.write_text("x")
            link = root / "link.txt"
            try:
                link.symlink_to(file)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks not supported by this user")
            with self.assertRaises(ValueError):
                RUNNER._safe_file(link, name="x")


class Workflow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.spek = root / "spek"; self.spek.mkdir()
        self.instance = root / "instance.json"; self.instance.write_text("{}")
        self.req = root / "private-requests"; self.req.mkdir()
        self.lock = root / "lock.json"; self.lock.write_text(json.dumps({"language":"fr"}))
        self.arch = root / "architect"; self.arch.mkdir()
        self.runtime = root / "runtime"; self.runtime.mkdir()
        self.gf = root / "gf.exe"; self.gf.write_bytes(b"fixture-not-a-real-gf-binary")
        self.output = root / "previews" / "new-edition"
        self.request = {"schema_version":"1.0", "context":{"target_language":"fr"},
             "capability_profile":"konstellation-explorer-3",
             "runtime_selector":{"runtime_set_id":"konstellation-fr-3"},
             "semantic_graph":{"id":"g1"},"obligations":[{"obligation_id":"o1"}]}
        (self.req / "r1.json").write_text(json.dumps(self.request))
        self.leaf = types.SimpleNamespace(key="k1", request_ref="requests/r1.json",kind="fact")
        self.modules = self.make_modules()
        self.kwargs = dict(spek_root=self.spek,instance=self.instance,requests_dir=self.req,
             lock=self.lock,architect=self.arch,runtime_root=self.runtime,gf_exe=self.gf,
             language="fr",runtime_id="konstellation-fr-3",profile="konstellation-explorer-3",
             out=self.output)

    def tearDown(self):
        self.tmp.cleanup()

    def make_modules(self):
        modules={}
        def mod(name, **kw):
            m=types.ModuleType(name)
            m.__dict__.update(kw)
            modules[name]=m
            return m
        class ValidationError(ValueError):pass
        mod("spek")
        mod("spek.core",ValidationError=ValidationError)
        mod("spek.composition")
        mod("spek.composition.commands",
            read_instance=lambda path:json.loads(Path(path).read_text()),
            load=lambda root,instance:types.SimpleNamespace(leaves=(self.leaf,)),
            preview=self.fake_preview)
        mod("spek.composition.editorial_lock",verify=lambda *a,**kw:{"status":"PASS_PRIVATE_UNQUALIFIED"})
        mod("spek.composition.semantik_adapter",import_results=self.fake_import)
        mod("spek.composition.engine",materialize=lambda *a,**kw:{"k1":"phrase"})
        mod("spek.semantik_execution",_architect_root=lambda a,b:(a,b),
            _python_executable=lambda:sys.executable)
        mod("spek.slot_dialogue",KIND_POLICY={"fact":("state","PRESENT",["utterance"],250)},
            compose_request=lambda obj,form,language:dict(obj))
        return modules

    @staticmethod
    def fake_import(resolved,reqs,results,lang):
        assert (reqs / "r1.json").is_file()
        assert (results / "r1.json").is_file()
        return {"format":"kristal.layout-realizations/0.1",
                "entries":{"k1":{"fr":{"text":"phrase","provider":"semantik_architect","status":"fixture"}}}}

    @staticmethod
    def fake_preview(root,instance,realizations,language,out,**kw):
        assert realizations.is_file()
        out.mkdir()
        (out / "index.html").write_text("private preview")
        (out / "Brouillon-prive.md").write_text("private preview")
        return {"page":str(out / "index.html"),"markdown":str(out / "Brouillon-prive.md")}

    def test_mocked_sa_success_transmits_gf_environment(self):
        seen={}
        def fake_run(cmd,**kwargs):
            seen.update(kwargs)
            seen["cmd"]=cmd
            return types.SimpleNamespace(returncode=0,stdout='{"schema_version":"1.0"}',stderr="")
        with patch.dict(sys.modules,self.modules),patch.object(subprocess,"run",side_effect=fake_run):
            res=RUNNER.execute(**self.kwargs)
        self.assertEqual(res["status"],"PRIVATE_GF_REALIZED_NOT_APPROVED")
        self.assertFalse(res["publication_authorized"])
        self.assertTrue(self.output.joinpath("index.html").exists())
        self.assertEqual(seen["env"]["SEMANTIK_GF_EXECUTABLE"],str(self.gf.resolve()))
        self.assertIn("--runtime-root",seen["cmd"])
        self.assertEqual(sorted(p.name for p in self.output.parent.iterdir()),["new-edition"])

    def test_mocked_sa_failure_writes_no_preview(self):
        with patch.dict(sys.modules,self.modules),patch.object(subprocess,"run",
              return_value=types.SimpleNamespace(returncode=2,stdout="{}",stderr="sensitive")):
            with self.assertRaisesRegex(ValueError,"Réalisation GF refusée"):
                RUNNER.execute(**self.kwargs)
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.output.parent.iterdir()),[])

    def test_mismatched_profile_blocks_before_subprocess(self):
        self.request["capability_profile"]="wrong"
        (self.req / "r1.json").write_text(json.dumps(self.request))
        with patch.dict(sys.modules,self.modules),patch.object(subprocess,"run") as call:
            with self.assertRaisesRegex(ValueError,"Profil SemantiK non conforme"):
                RUNNER.execute(**self.kwargs)
        call.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_mismatched_runtime_blocks_before_subprocess(self):
        self.request["runtime_selector"]["runtime_set_id"]="other"
        (self.req / "r1.json").write_text(json.dumps(self.request))
        with patch.dict(sys.modules,self.modules),patch.object(subprocess,"run") as call:
            with self.assertRaisesRegex(ValueError,"RuntimeSet non épinglé"):
                RUNNER.execute(**self.kwargs)
        call.assert_not_called()

    def test_wrong_lock_language_blocks(self):
        self.lock.write_text(json.dumps({"language":"en"}))
        with patch.dict(sys.modules,self.modules),patch.object(subprocess,"run") as call:
            with self.assertRaisesRegex(ValueError,"Langue du verrou différente"):
                RUNNER.execute(**self.kwargs)
        call.assert_not_called()


if __name__ == "__main__":
    unittest.main()
