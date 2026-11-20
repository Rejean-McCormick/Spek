"""Test de l'installateur cumulatif sur un faux dépôt, jamais sur le SPEK réel."""
from __future__ import annotations
import importlib.util
import hashlib
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
# SPEK_REGISTRY_FIRST_V050A1_INSTALLED_CHECKOUT
# Le pack v0.4 conserve son test de distribution dans le ZIP extrait.
# Dans le checkout SPEK, son INSTALLER_CUMULATIF.py n'est PAS installé.
# Ne pas déclencher d'erreur de collecte : le test s'exécute dans le pack.
import unittest as _unittest
if not (Path(__file__).resolve().parents[1]/"INSTALLER_CUMULATIF.py").is_file():
    raise _unittest.SkipTest("Test de l'installateur v0.4 : exécuter depuis le ZIP extrait")
spec=importlib.util.spec_from_file_location('spek_cumulative_agri_installer',ROOT/'INSTALLER_CUMULATIF.py')
ins=importlib.util.module_from_spec(spec);spec.loader.exec_module(ins)

class InstallerPilot(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.root=Path(t.name);self.target=self.root/'Spek';self.target.mkdir()
        for rel in ins.REQUIRED:
            p=self.target/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('# fake SPEK core',encoding='utf-8')

    def test_manifest_integrity(self):
        refs=ins._manifest()
        self.assertEqual(len(refs),15)
        self.assertEqual(set(refs),set(ins.FILES))

    def test_install_new_full_bundle(self):
        r=ins.install(self.target)
        self.assertEqual(r['installed'],15)
        self.assertEqual(r['replaced'],0)
        self.assertEqual(r['git_operations'],0)
        for rel in ins.FILES:self.assertEqual(ins.sha(ROOT/rel),ins.sha(self.target/rel))

    def test_installed_previous_v030a2_only_adds_five_files(self):
        for rel in ins.FILES[:10]:
            p=self.target/rel;p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes((ROOT/rel).read_bytes())
        new,same,replacements=ins.inspect(self.target)
        self.assertEqual((len(new),len(same),len(replacements)),(5,10,0))
        self.assertEqual(ins.install(self.target)['installed'],5)
        self.assertEqual(ins.install(self.target)['already_identical'],15)

    def test_conflicting_existing_code_refused_without_partial_changes(self):
        p=self.target/ins.FILES[0];p.parent.mkdir(parents=True,exist_ok=True);p.write_text('modified',encoding='utf-8')
        with self.assertRaises(ValueError):ins.install(self.target)
        self.assertFalse((self.target/'scripts/pilote_agriculture_sol.py').exists())

    def test_old_utf8_test_upgrade_is_only_replacement(self):
        ins.install(self.target)
        rel='tests/test_construire_pages_kristals.py'
        current=(ROOT/rel).read_text(encoding='utf-8')
        original=(current.replace('.read_text(encoding="utf-8")','.read_text()')
                  .replace('page.write_text(page.read_text()+"<script>alert(1)</script>",encoding="utf-8")',
                           'page.write_text(page.read_text()+"<script>alert(1)</script>")'))
        self.assertEqual(hashlib.sha256(original.encode('utf-8')).hexdigest(),ins.PREVIOUS_VERSION_HASHES[rel])
        (self.target/rel).write_text(original,encoding='utf-8')
        result=ins.install(self.target)
        self.assertEqual(result['replaced'],1)
        self.assertEqual(result['installed'],0)
        self.assertEqual(result['already_identical'],14)

if __name__=='__main__':unittest.main()
