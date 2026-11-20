# SPEK — point d'entrée unique permanent « registres → pages »

**Mise à jour 20 novembre 2026, overlay cumulatif v0.8.0a1.** Ne pas recréer le catalogue, les templates ni le moteur HTML. Toute nouvelle conversation commence par `AGENTS.md`, ce document et `PILOTAGE_INTEGRAL_AGRICULTURE_V8.md`, puis `RACCORDEMENT_GFWORDBENCH_AGRICULTURE.md` et `RACCORDEMENT_DIK_AGRICULTURE.md`.

## Registres déjà construits — sources exactes

| Rôle | Chemin relatif SPEK | Statut |
|---|---|---|
| 19 compositions de sections/layouts | `template_library/wiki/composition-registry.json` + `compositions/*.json` | Propositions Arketype |
| 127 propositions individualisées | `template_library/wiki/kristal-ai-proposals.json` | Non approuvées |
| 5 revues de source approfondies | `template_library/wiki/kristal-structure-reviews.json` | Lecture de snapshots, non qualifiées |
| 19 layouts spécialisés et 8 historiques | `template_library/wiki/specialized-template-designs.json` et `layouts/*.json` | Moteurs typés existants |
| Affectations validées | `template_library/wiki/kristal-assignments.json` | **Vides** |
| 62 templates rhétoriques | `template_library/rhetorical/templates/*.json` | Récursifs, contrat différent des layouts |
| Contrôle de raccordement | `scripts/orchestrer_registre_spek.py` | Privé, vérifie plan, instances, empreintes, sources |
| **Pilote Agriculture v8** | `scripts/piloter_agriculture_registres.py` | Vérifie candidat/source, délègue aux moteurs existants |
| **Qualification GF Fre** | `scripts/pont_gf_wordbench_agriculture.py` | Délégation précontrôle/sonde au WordBench natif, sans prétention Agriculture |
| Réalisation GF existante | `scripts/realiser_composition_semantik.py` | Requêtes explicites + provenance, aucun fait inventé |
| Site HTML/Markdown existant | `scripts/construire_pages_kristals.py` | Site statique privé, manifeste et archive |

## Composition Agriculture — ce qui est établi

1. **Proposition individuelle** : `arketype-modele-multiplexe`; la recette générique contient `entites` (`concept-card`), `couches` (`comparison`), `sources` (`evidence-comparison`), mais la proposition Agriculture ne retient explicitement que `entites` en candidature.
2. **Revue spécialisée distincte** : six sections `soil`, `crop`, `inputs`, `practices`, `yield`, `cross`, avec layouts `agroecosystem-network`, `agroecosystem-network`, `inputs-practices-matrix`, `practice-interface-map`, `evidence-constraint-matrix`, `relation-network`. Les six sont initialement `NOT_SELECTED`.
3. **Source d'origine** : `C:\mycode\Kristal\locals\Kristal-Agriculture\.kristal\v8\portable-state.kristal-state.json`, SHA-256 **brut** `ae3cf84ab47a1ea3c710785f5749c7cacd8274d389f767958c7327c6c1a72918`. L'utilisateur a prouvé deux fois l'égalité sur son poste; le contenu exact de 391 assertions a ensuite été fourni et audité.
4. **Candidature sourcée** : 96 assertions distinctes, réparties 18/14/12/15/15/22 ; aucune n'est sélectionnée officiellement. `decision=pending`, `pages=[]`, `coverage=[]` sont intentionnels. Le slot obligatoire `limits` de chaque layout n'est pas couvert par une unité autorisée; les warnings techniques ne sont pas des assertions scientifiques réalisables.
5. **Autre pilote** : page source-littérale v11.1 (408 assertions) et un glossaire de quatre sections. Elle est HTML valide, mais ne prouve PAS le rendu riche Agriculture v8 ni GF et ne remplace pas le plan enregistré.

## Chaîne de fabrication sans duplication

`Kristal locals v8 exact → registres AI (proposition + revue) → sélection éditoriale contrôlée → liaison explicite section/layout/feuilles → SemantiK Architect/GF (RuntimeSet réellement vérifié) → moteur SPEK récursif et layouts typés → collection HTML/Markdown privée → revue indépendante → Publisher avec autorisations C1/C2/C3/C4`.

**Attention :** les 19 layouts typés et les 62 templates récursifs sont deux contrats distincts. L'orchestrateur ne transforme pas magiquement un layout `agroecosystem-network` en instance `rhetorical.*`. La correspondance doit être établie, vérifiée et justifiée; le code refuse les feuilles ou assertions manquantes.

## Commandes Windows — une seule entrée

Depuis n'importe quel terminal avec Python 3.12 :

```powershell
$spek = 'C:\mycode\Spek_Semantic-publishing\Spek'
$ctl = Join-Path $spek 'scripts\piloter_agriculture_registres.py'
py -3.12 $ctl --spek-root $spek doctor
# HTML privé d'inspection structurelle PRODUIT PAR SPEK (sans GF)
py -3.12 $ctl --spek-root $spek preview --out "$HOME\Downloads\Agriculture-structure-$(Get-Date -Format yyyyMMdd-HHmmss)"
```

Le contrôle `doctor` doit signaler `SOURCE_AND_REGISTRY_CANDIDATES_VERIFIED_NOT_BUILDABLE` et six `limits` manquants, tant qu'aucune revue éditoriale/PGF Agriculture n'a été fournie. Ce statut est un **résultat attendu, pas une réussite de publication**.

Quand une vraie liaison complète et le plan GF existent (ils ne sont PAS inventés par cet overlay), `check`, puis `build`, puis `package` délèguent aux modules déjà installés. Voir le guide du pilote pour les commandes exactes.

Les docs historiques conservent parfois des instantanés antérieurs. **Ce point d'entrée prévaut comme résumé d'intégration**, mais les contrats et versions de chaque outil restent autoritatifs pour l'exécution.

## Liaison WordBench disponible (v0.7)

Le code contrôle les 15 scénarios français déjà présents dans WordBench sans doubler son moteur, et crée sur demande un inventaire privé **des 96 obligations de mapping Agriculture** avec prédicat, sujet, objet, preuve, section et slot. Aucun `CommunicationRequest`, constructeur GF, glossaire ou qualification n’est inventé. Commandes sous `docs/RACCORDEMENT_GFWORDBENCH_AGRICULTURE.md`. Les 15 scénarios Defluens Fre, même exécutés, ne valent pas une compilation PGF de domaine Agriculture.

## diK — raccordement lexical natif (v0.8)

Ne pas demander à l'utilisateur de redécouvrir diK ni de transmettre de nouveau son archive.
Les fichiers du snapshot réel existent dans `src/dik/gf_handoff.py`,
`src/dik/semantik_handoff.py` et `docs/docs/30_SEMANTIK_GF_HANDOFF_V09.md`.
L'exemple français passe les six commandes natives sur l'échantillon diK,
mais le transfert reste `CANDIDATE_ONLY` sans mapping GF ou approbation.
Exécuter `doctor`, puis si utile `probe-dik`; le rapport exact de besoins
lexicaux Agriculture sort de `lexical-needs`.
Voir `docs/RACCORDEMENT_DIK_AGRICULTURE.md`.
