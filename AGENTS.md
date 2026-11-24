# SPEK — état permanent, version d'intégration v0.8.0a1 (20 novembre 2026)

**TOUJOURS COMMENCER ICI.** L'utilisateur a déjà fourni les chemins, les registres et le snapshot Agriculture. Ne lui redemandez pas ces éléments et ne créez pas de second moteur de pages/templates. Lire `docs/POINT_ENTREE_REGISTRES_SPEK.md`, `docs/PILOTAGE_INTEGRAL_AGRICULTURE_V8.md` et `docs/RACCORDEMENT_GFWORDBENCH_AGRICULTURE.md`, puis `docs/RACCORDEMENT_DIK_AGRICULTURE.md` avant de coder.

## Chemins confirmés par l'utilisateur

- SPEK : `C:\mycode\Spek_Semantic-publishing\Spek`
- Kristal Agriculture **v8 étudié** : `C:\mycode\Kristal\locals\Kristal-Agriculture\.kristal\v8\portable-state.kristal-state.json`, SHA-256 brut `ae3cf84ab47a1ea3c710785f5749c7cacd8274d389f767958c7327c6c1a72918` (391 assertions uniques; `schema_version` dans le JSON = `6.0`, ce qui n'est pas une contradiction de fichier)
- SemantiK Architect : `C:\mycode\SemantiK_Architect\SemantiK_Architect`
- GF CLI : `C:\mycode\Grammatical-Framework\gf-3.12-windows\gf.exe`
- SemantiK Runtime Orchestrator : `C:\mycode\SemantiK_Architect\SemantiK_Runtime_Orchestrator` (rapporté, non vérifié en exécution dans ce pilote)
- Konstellation : `C:\mycode\Konstellation\Konstellation` (branche distincte)

- GF WordBench : `C:\mycode\Grammatical-Framework\GF_Wordbench` (source intégrale fournie, 2 036 fichiers, 20 novembre 2026)
- GF RGL : `C:\mycode\Grammatical-Framework\gf-rgl` (index fourni, 3 167 fichiers; source non transmise)

Le chemin local du Publisher reste inconnu. L'environnement d'exécution de l'assistant n'accède pas aux disques Windows.

## Source de vérité éditoriale

Les registres EXISTENT : `template_library/wiki/composition-registry.json` (19), `compositions/*.json`, `kristal-ai-proposals.json` (127), `kristal-structure-reviews.json` (5 revues), `specialized-template-designs.json` (19 layouts typés), `kristal-assignments.json` (**aucune affectation approuvée**), et 62 templates sous `template_library/rhetorical/templates`.

Agriculture est une proposition `arketype-modele-multiplexe` et sa revue approfondie déclare six sections ordonnées : `soil`, `crop`, `inputs`, `practices`, `yield`, `cross` (layouts spécialisés). Ne pas substituer l'ancien glossaire de quatre sections. Ces deux bibliothèques n'ont pas le même format; la combinaison rhétorique doit être déclarée dans une instance et liée explicitement à la revue.

## État Agriculture et unique parcours de code

- Source v8 identique retrouvée sur Windows. Candidature **96 assertions distinctes**, réparties 18/14/12/15/15/22 : **revue éditoriale toujours pending**. Cette sélection n'a aucune autorité de publication.
- Le nouveau script `scripts/piloter_agriculture_registres.py` pilote uniquement les composants existants. `doctor` contrôle la provenance et la sélection privée; `preview` appelle `python -m spek preview-structure` (HTML source d'inspection, PAS GF); `check` exige une liaison de page complète, confronte les pointeurs aux IDs exacts et délègue à `scripts/orchestrer_registre_spek.py`; `build` délègue au même `scripts/construire_pages_kristals.py` et à `scripts/realiser_composition_semantik.py`.
- Il reste à qualifier les champs `limits` des six layouts, à choisir les assertions après revue humaine, créer les véritables `CommunicationRequest` Agriculture et vérifier un RuntimeSet GF agricole compatible, lier explicitement instances/feuilles/verrous/plan, puis faire vérifier la page.
- Le succès antérieur d'un `render` français **Konstellation** ne prouve pas un runtime Agriculture. La validation d'un SHA v8 ne vaut pas engagement canonique v9 ni décision éditoriale.
- Publication C1/C2/C3/C4 et Publisher : **jamais automatiques**, aucune opération Git ni réseau. Les données privées restent sous `Documents\SPEK-PRIVE\Agriculture-v8`, hors Git.

Le pilote GF WordBench Fre est **Defluens**, avec 15 scénarios natifs à précontrôle d'intégrité, pas un RuntimeSet Agriculture : aucun gold français indépendant n'est approuvé dans le snapshot inspecté. Ne pas confondre un test GF WordBench avec une phrase Agriculture réalisée. `doctor` intègre son précontrôle natif (`scripts/pont_gf_wordbench_agriculture.py`), et `requirements` prépare 96 tâches sourcées non mappées sans réécrire WordBench/SA. `probe-fre` délègue la seule sonde GF à WordBench sur demande explicite.

Le prochain assistant devrait lire le rapport `doctor` avant de suggérer un correctif. Demander uniquement les preuves concrètes encore manquantes (ex. profil/runtime Agriculture ou résultat de prévisualisation refusé), jamais des éléments déjà confirmés.

## diK — contrat lexical réellement inspecté (20 novembre 2026, v0.8)

Le snapshot `znapshot_diK_11201331.zip` a été inspecté et sa chaîne native
`world lexemes-import → lexemes-audit → gf-handoff → gf-audit → semantik-knowledge → semantik-knowledge-audit`
a été exécutée sur son échantillon avec succès. **Deux** candidats de lexèmes français,
**zéro** GF binding, **zéro** correspondance Kristal approuvée. Le chemin
`C:\mycode\diK\diK` apparaît dans la documentation de diK, mais **n'a pas été vérifié par le terminal utilisateur**.
Le pont SPEK `scripts/pont_dik_semantik.py` ne traduit jamais des labels en IDs
KQ/KP/KA et ne crée ni `.gf`, ni RuntimeSet. `doctor`, `probe-dik` et
`lexical-needs` sont décrits dans `docs/RACCORDEMENT_DIK_AGRICULTURE.md`.
L'export diK `semantik.knowledge.json` est *knowledge-only* et ne constitue
PAS un lexique de réalisation ou une autorisation GF.

## Interface fédérée diK V5.9 — règle additive candidate

Ne jamais traiter `dik.federated-semantic-registry/0.1-candidate` comme une source d’autorité canonique ou une permission de publier. Toute identité locale exige `namespace_id+KQ/KP`; un Q/P Wikidata n’est qu’un alignement externe revu. Le précontrôle vérifie uniquement l’intégrité. Consulter `docs/DIK_FEDERATED_REGISTRY_BOUNDARY.md`. Les contraintes propriétaire existantes prévalent.
