"""Offline tests of multi-page SPEK site assembly; GF mocked, not a release test."""
from __future__ import annotations
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0,str(SCRIPTS))
import construire_pages_kristals as mod


class CollectionCase(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root = Path(self.t.name)
        self.spek = self.root / "spek"
        (self.spek / "spek" / "composition").mkdir(parents=True)
        (self.spek / "spek" / "composition" / "engine.py").write_text("# stub: tests only")
        self.input = self.root / "private"; self.input.mkdir()
        self.plan = self.input / "plan.json"
        self.out = self.root / "private-site" / "edition-001"
        self.default = {
            "format":mod.PLAN_FORMAT,
            "authority":mod.AUTHORITY,
            "collection":{"id":"kristal-public-pilot","title":"Collection Kristal",
                          "description":"Pages documentaires de démonstration"},
            "pages":[{"id":"agriculture-sol","title":"Agriculture — Sol", "language":"fr",
                      "instance":"instance.json","requests_dir":"requests","lock":"lock.json",
                      "profile":"konstellation-explorer-3","runtime_id":"konstellation-fr-3",
                      "source_graph":"semantic-graph.json"},
                     {"id":"agriculture-sol","title":"Agriculture — Sol", "language":"en",
                      "instance":"instance-en.json","requests_dir":"requests-en","lock":"lock-en.json",
                      "profile":"defluens-core-1","runtime_id":"defluens-core-en-1"}]}
        self.kw=dict(plan=self.plan,spek_root=self.spek,architect=self.root / "architect",
                     runtime_root=self.root / "runtime",gf_exe=self.root / "gf.exe",out=self.out)
        self.save()

    def save(self):
        self.plan.write_text(json.dumps(self.default,ensure_ascii=False),encoding="utf-8")

    def fake_realization(self, **kwargs):
        out=kwargs["out"]
        out.mkdir(parents=True)
        text=f"Sujet de la composition {kwargs['language']}."
        (out/"index.html").write_text('<!doctype html><html lang="fr"><head><meta charset="utf-8">'
                                      '<title>Composition SPEK — aperçu privé</title></head>'
                                      '<body><main><h1>Composition SPEK — aperçu privé</h1>'
                                      '<p>Aperçu privé</p><article><section><h2>Contexte</h2>'
                                      f'<p>{text}</p></section></article></main></body></html>',encoding="utf-8")
        (out/"Brouillon-prive.md").write_text('# Composition SPEK — aperçu privé\n\n> Aperçu privé\n\n## Contexte\n\n'+text+'\n',encoding="utf-8")
        return {"status":"PRIVATE_GF_REALIZED_NOT_APPROVED","publication_authorized":False,
                "language":kwargs["language"],"html":str(out/"index.html")}

    def build(self):
        with patch.object(mod,"run_realization",side_effect=self.fake_realization):
            return mod.build(**self.kw)

    def test_build_complete_html_pages_and_verify(self):
        result=self.build()
        self.assertEqual(result["pages"],2)
        self.assertFalse(result["public_authorized"])
        self.assertTrue((self.out/"index.html").is_file())
        self.assertTrue((self.out/"pages/fr/agriculture-sol/index.html").is_file())
        self.assertTrue((self.out/"pages/fr/agriculture-sol/page.md").is_file())
        self.assertTrue((self.out/"pages/en/agriculture-sol/index.html").is_file())
        body=(self.out/"pages/fr/agriculture-sol/index.html").read_text(encoding="utf-8")
        self.assertIn("<article>",body)
        self.assertIn("<h2>Contexte</h2>",body)
        self.assertIn("<h1>Agriculture — Sol</h1>",body)
        self.assertIn("<title>Agriculture — Sol</title>",body)
        self.assertIn("# Agriculture — Sol",(self.out/"pages/fr/agriculture-sol/page.md").read_text(encoding="utf-8"))
        self.assertIn('href="../../en/agriculture-sol/index.html"',body)
        self.assertIn('href="../../../index.html"',body)
        self.assertEqual(mod.verify(self.out)["page_count"],2)

    def test_site_handoff_has_no_private_source_paths(self):
        self.build()
        handoff=(self.out/"publication-handoff.json").read_text(encoding="utf-8")
        manifest=(self.out/"site-manifest.json").read_text(encoding="utf-8")
        self.assertNotIn("requests",handoff+manifest)
        self.assertNotIn("lock.json",handoff+manifest)
        self.assertNotIn(str(self.input),handoff+manifest)
        self.assertIn('"publication_eligible": false',handoff)
        self.assertNotIn("semantic-graph.json",handoff+manifest)

    def test_tampered_html_rejected(self):
        self.build()
        with (self.out/"pages/fr/agriculture-sol/index.html").open("a") as f:f.write("modified")
        with self.assertRaisesRegex(mod.SiteError,"Empreinte"):
            mod.verify(self.out)

    def test_unexpected_file_rejected(self):
        self.build()
        (self.out/"private-requests.json").write_text("{}")
        with self.assertRaisesRegex(mod.SiteError,"Fichiers"):
            mod.verify(self.out)

    def test_replacing_manifest_status_detected(self):
        self.build()
        manifest=json.loads((self.out/"site-manifest.json").read_text(encoding="utf-8"))
        manifest["public_authorized"]=True
        (self.out/"site-manifest.json").write_text(json.dumps(manifest))
        with self.assertRaisesRegex(mod.SiteError,"Statut"):
            mod.verify(self.out)

    def test_failed_second_page_has_no_final_site(self):
        count=[0]
        def fail(**kwargs):
            count[0]+=1
            if count[0]==2:raise mod.SiteError("Failed language")
            return self.fake_realization(**kwargs)
        with patch.object(mod,"run_realization",side_effect=fail):
            with self.assertRaises(mod.SiteError):mod.build(**self.kw)
        self.assertFalse(self.out.exists())
        self.assertEqual(list(self.out.parent.iterdir()),[])

    def test_duplicate_page_rejected_before_runner(self):
        self.default["pages"].append(dict(self.default["pages"][0]))
        self.save()
        with patch.object(mod,"run_realization") as runner:
            with self.assertRaisesRegex(mod.SiteError,"dupliquée"):
                mod.build(**self.kw)
            runner.assert_not_called()

    def test_unsupported_language_rejected(self):
        self.default["pages"][0]["language"]="es"
        self.save()
        with self.assertRaisesRegex(mod.SiteError,"Langue"):
            mod.parse_plan(self.plan)

    def test_unsafe_slug_and_html_title_rejected(self):
        self.default["pages"][0]["id"]="../danger"
        self.save()
        with self.assertRaises(mod.SiteError):mod.parse_plan(self.plan)
        self.default["pages"][0]["id"]="agriculture-sol"
        self.default["pages"][0]["title"]="<script>alert(1)</script>"
        self.save()
        with self.assertRaises(mod.SiteError):mod.parse_plan(self.plan)

    def test_empty_plan_rejected(self):
        self.default["pages"]=[]
        self.save()
        with self.assertRaisesRegex(mod.SiteError,"1 à 500"):
            mod.parse_plan(self.plan)

    def test_invalid_issuer_rejected(self):
        self.default["authority"]="approved_for_publication"
        self.save()
        with self.assertRaisesRegex(mod.SiteError,"autorité"):
            mod.parse_plan(self.plan)

    def test_second_build_requires_new_destination(self):
        self.build()
        with patch.object(mod,"run_realization") as runner:
            with self.assertRaisesRegex(ValueError,"présente"):
                mod.build(**self.kw)
            runner.assert_not_called()

    def test_different_build_paths_do_not_change_file_hashes(self):
        self.build()
        target=self.out
        self.kw["out"]=self.root/"private-site"/"edition-002"
        self.build()
        self.assertEqual((target/"site-manifest.json").read_bytes(),
                         (self.kw["out"]/"site-manifest.json").read_bytes())

    def test_zip_contains_only_verified_static_site(self):
        self.build()
        archive=self.root/"archive-privee.zip"
        result=mod.package(site=self.out,out=archive)
        self.assertFalse(result["public_authorized"])
        import zipfile
        with zipfile.ZipFile(archive) as z:
            paths=z.namelist()
            self.assertIn("index.html",paths)
            self.assertIn("site-manifest.json",paths)
            self.assertNotIn("requests/anything.json",paths)
            self.assertEqual(len(paths),8)  # index + handoff + manifest + sha + 2*(html, md)

    def test_reject_git_output(self):
        other=self.root/"git";other.mkdir();(other/".git").mkdir()
        self.kw["out"]=other/"site"
        with patch.object(mod,"run_realization") as runner:
            with self.assertRaisesRegex(ValueError,"dépôt Git"):
                mod.build(**self.kw)
            runner.assert_not_called()

    def test_reject_script_in_spek_html(self):
        def injected(**kwargs):
            res=self.fake_realization(**kwargs)
            page=kwargs["out"]/"index.html"
            page.write_text(page.read_text(encoding="utf-8")+"<script>alert(1)</script>",encoding="utf-8")
            return res
        with patch.object(mod,"run_realization",side_effect=injected):
            with self.assertRaisesRegex(mod.SiteError,"actif"):
                mod.build(**self.kw)
        self.assertFalse(self.out.exists())


if __name__=="__main__":unittest.main()
