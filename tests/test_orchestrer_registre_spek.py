"""Offline contract tests: no SPEK renderer, repo, GF or Publisher is mocked as qualified."""
import importlib.util
import hashlib
import json
from pathlib import Path
import tempfile
import types
import unittest

BASE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('registry_first_overlay',BASE/'scripts/orchestrer_registre_spek.py')
reg=importlib.util.module_from_spec(spec);spec.loader.exec_module(reg)


def dump(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8')


class RegistryCases(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.t=Path(temp.name);self.s=self.t/'Spek';self.s.mkdir()
        self.wiki=self.s/'template_library/wiki';self.wiki.mkdir(parents=True)
        self.state=self.t/'portable.json';self.state.write_text('source state en test',encoding='utf-8')
        self.hash=hashlib.sha256(self.state.read_bytes()).hexdigest()
        self.identity='agriculture'
        self.cid='arketype-modele-multiplexe'
        dump(self.wiki/'kristal-ai-proposals.json',{
            'format':'spek.wiki-ai-kristal-proposals/1.0','revision':'r1',
            'policy':{'runtime_template_inference_allowed':False},
            'proposals':{self.identity:{'kristal_identity':self.identity,'primary_composition_id':self.cid,
                       'supplementary_composition_ids':[],
                       'ordered_sections':[{'section_id':'entites','layout_id':'concept-card'}]}}})
        dump(self.wiki/'composition-registry.json',{
            'format':'spek.wiki-ai-composition-registry/1.0','allow_runtime_template_inference':False,
            'compositions':{self.cid:{'file':'compositions/modele-multiplexe.json'}}})
        dump(self.wiki/'compositions/modele-multiplexe.json',{
            'format':'spek.wiki-ai-composition/1.0','composition_id':self.cid,
            'sections_in_order':[{'section_id':'entites','layout_id':'concept-card'}]})
        dump(self.wiki/'kristal-structure-reviews.json',{
            'reviews':{'agriculture':{'kristal_identity':'agriculture',
                'source':{'portable_state_raw_sha256':self.hash,'portable_state_relative_path':'v8.json'},
                'ordered_structural_sections':[
                {'section_id':'soil','planned_template_id':'agroecosystem-network','selection_status':'NOT_SELECTED'},
                {'section_id':'crop','planned_template_id':'agroecosystem-network','selection_status':'NOT_SELECTED'}]}}})
        dump(self.wiki/'kristal-assignments.json',{
            'format':'spek.wiki-kristal-composition-assignments/1.0',
            'policy':{'runtime_inference_allowed':False},'assignments':{}})
        dump(self.wiki/'specialized-template-designs.json',{
            'templates':[{'id':'agroecosystem-network'}]})
        dump(self.s/'layouts/agroecosystem-network.json',{'id':'agroecosystem-network'})
        self.ctx=reg.read_context(self.s,self.identity)
        self.bridge=reg.scaffold(self.ctx,'deep_review')
        self.path=self.t/'bridge.json'
        self.plan=self.t/'plan.json';self.instance=self.t/'instance.json';dump(self.instance,{'format':'test'})
        self.fake=types.SimpleNamespace(
            root=types.SimpleNamespace(template_ref='wiki.article@1.0.0',ordered=(
                ('children',(types.SimpleNamespace(template_ref='rhetorical.definition@1.0.0',ordered=()),)),)),
            leaves=[types.SimpleNamespace(key='soil.term',source_assertion_refs=('A:soil',)),
                    types.SimpleNamespace(key='soil.definition',source_assertion_refs=('A:soil',))])
        self.plan_obj={'pages':[{'id':'agriculture-sol','language':'fr','instance':str(self.instance),
                                            'source_graph':str(self.state)}]}

    def run_check(self):
        dump(self.path,self.bridge)
        dump(self.plan,self.plan_obj)
        return reg.validate(self.s,self.path,self.plan,context=self.ctx,
                           load_engine=lambda root,path:self.fake,
                           parse_site_plan=lambda path:self.plan_obj)

    def populate(self):
        self.bridge['source_state']={'file':str(self.state),'raw_sha256':self.hash}
        self.bridge['status']='EXPLICIT_PRIVATE_SELECTION_PENDING_INDEPENDENT_REVIEW'
        self.bridge['pages']=[{'id':'agriculture-sol','language':'fr','instance':str(self.instance),
             'instance_sha256':hashlib.sha256(self.instance.read_bytes()).hexdigest(),
             'template_refs':['wiki.article@1.0.0','rhetorical.definition@1.0.0']}]
        self.bridge['sections'][0].update({
            'decision':'include','source_assertion_ids':['A:soil'],
            'semantic_source_paths':['/agriculture/soil'],'coverage':[
             {'page_key':'agriculture-sol:fr','realization_keys':['soil.term','soil.definition']} ]})
        self.bridge['sections'][1].update({'decision':'omit','reason':'Sans assertions retenues'})

    def test_inventory_exact_registry_before_templates(self):
        d=reg.describe(self.ctx)
        self.assertEqual(d['primary_composition_id'],self.cid)
        self.assertEqual(len(d['deep_review_sections']),2)
        self.assertEqual(len(d['recipe_sections']),1)
        self.assertEqual(len(d['candidate_sections_for_kristal']),1)
        self.assertFalse(d['approved_assignment_present'])
        self.assertFalse(d['publication_authorized'])

    def test_scaffold_never_selects_fact_or_assigns_template_execution(self):
        self.assertEqual(len(self.bridge['sections']),2)
        self.assertEqual(self.bridge['pages'],[])
        self.assertTrue(all(not s['source_assertion_ids'] for s in self.bridge['sections']))
        self.assertTrue(all(not s['coverage'] for s in self.bridge['sections']))
        self.assertIsNone(self.bridge['source_state']['file'])
        with self.assertRaisesRegex(reg.RegistryError,'Source réelle'):
            self.run_check()

    def test_ready_private_only_with_explicit_matches(self):
        self.populate();r=self.run_check()
        self.assertTrue(r['can_attempt_private_GF_build'])
        self.assertTrue(r['recursive_template_sets_matched'])
        self.assertEqual(r['unique_realization_keys'],2)
        self.assertFalse(r['publication_authorized'])
        self.assertFalse(r['semantic_qualification_proven'])

    def test_rejects_unreviewed_revision_of_source(self):
        self.populate();self.state.write_text('revision differente')
        with self.assertRaisesRegex(reg.RegistryError,'Empreinte des octets'):
            self.run_check()

    def test_rejects_source_snapshot_mismatch_even_if_file_hash_matches(self):
        self.populate();self.bridge['source_state']['raw_sha256']='a'*64
        with self.assertRaisesRegex(reg.RegistryError,'snapshot revu'):
            self.run_check()

    def test_rejects_instance_change_even_with_same_template_ids(self):
        self.populate()
        dump(self.instance, {'format':'test','changed':True})
        with self.assertRaisesRegex(reg.RegistryError,'Empreinte de l\'instance'):
            self.run_check()

    def test_rejects_unlinked_or_different_source_graph(self):
        self.populate()
        self.plan_obj['pages'][0].pop('source_graph')
        with self.assertRaisesRegex(reg.RegistryError,'Source v11 explicitement'):
            self.run_check()

    def test_rejects_template_combination_changed(self):
        self.populate();self.bridge['pages'][0]['template_refs']=['wiki.article@1.0.0']
        with self.assertRaisesRegex(reg.RegistryError,'Combinaison récursive'):
            self.run_check()

    def test_rejects_false_assertion_binding(self):
        self.populate();self.bridge['sections'][0]['source_assertion_ids']=['A:autre']
        with self.assertRaisesRegex(reg.RegistryError,'assertions sélectionnées'):
            self.run_check()

    def test_rejects_hidden_leaf_or_double_bind(self):
        self.populate();self.bridge['sections'][0]['coverage'][0]['realization_keys']=['soil.term']
        with self.assertRaisesRegex(reg.RegistryError,'Chaque feuille'):
            self.run_check()

    def test_rejects_changed_proposal_registry(self):
        self.populate();self.bridge['registry_sha256']['proposals']='0'*64
        with self.assertRaisesRegex(reg.RegistryError,'Registre modifié'):
            self.run_check()

    def test_omit_requires_reason(self):
        self.populate();self.bridge['sections'][1]['reason']=''
        with self.assertRaisesRegex(reg.RegistryError,'Omission'):
            self.run_check()

    def test_refuses_implicit_identity_matching(self):
        with self.assertRaisesRegex(reg.RegistryError,'canonique'):
            reg.read_context(self.s,'Kristal-Agriculture')

    def test_refuses_inference_enabled(self):
        x=reg._json(self.wiki/'kristal-ai-proposals.json')
        x['policy']['runtime_template_inference_allowed']=True
        dump(self.wiki/'kristal-ai-proposals.json',x)
        with self.assertRaisesRegex(reg.RegistryError,'non-inférentielle'):
            reg.read_context(self.s,'agriculture')

    def test_recipe_scaffold_uses_19_catalog_not_rhetorical_definitions(self):
        d=reg.scaffold(self.ctx,'recipe')
        self.assertEqual(d['sections'][0]['layout_id'],'concept-card')
        self.assertIsNone(d['observed_source']['raw_sha256'])
        self.assertFalse(d['publication_authorized'])

    def test_refuses_source_read_path_traversal(self):
        self.populate();self.bridge['source_state']['file']='../source.json'
        with self.assertRaisesRegex(reg.RegistryError,'traversée'):
            self.run_check()

    def test_refuses_preview_overwrite_or_under_repo(self):
        with self.assertRaisesRegex(reg.RegistryError,'hors de SPEK'):
            reg._private_file_destination(self.s/'private.json',self.s.resolve())
        path=self.t/'report.json';path.touch()
        with self.assertRaisesRegex(reg.RegistryError,'Nouveau fichier'):
            reg._private_file_destination(path,self.s.resolve())

if __name__ == '__main__':unittest.main()
