# SPEK — point d'entrée permanent : registres → compositions → pages

**Statut : référence d'intégration, version overlay v0.5.0a1, 19 novembre 2026.** Ce fichier évite de redécouvrir à chaque nouvelle intervention la logique de composition déjà construite. Les fichiers JSON d'origine sont l'autorité pour leurs propres propositions; ce guide ne les réécrit pas.

## 1. Sources exactes dans le dépôt SPEK

| Fonction | Chemin relatif | Rôle | Autorité |
|---|---|---|---|
| 19 recettes Arketype | `template_library/wiki/composition-registry.json` | Registre des combinaisons de **layouts/sections** | Design candidat |
| Détails des 19 recettes | `template_library/wiki/compositions/*.json` | `sections_in_order`, slots, contraintes par layout | Design candidat |
| 127 choix individualisés | `template_library/wiki/kristal-ai-proposals.json` | `proposals.<slug>.primary_composition_id`, sections candidates | IA, non approuvée |
| 5 revues approfondies | `template_library/wiki/kristal-structure-reviews.json` | `reviews.<slug>.ordered_structural_sections`, empreinte source observée | Revue structurelle, non qualifiée |
| 19 layouts spécialisés | `template_library/wiki/specialized-template-designs.json` et `layouts/*.json` | Contrats typés réalisés par SPEK | Type et présentation, pas faits |
| Assignations individuelles | `template_library/wiki/kristal-assignments.json` | Validation humaine, état épinglé, assertions sélectionnées | **Vide au contrôle** |
| 62 templates récursifs | `template_library/rhetorical/templates/*.json` | Mouvements rhétoriques, sous-templates, répétitions | Moteur de présentation |
| Moteur récursif | `spek/composition/engine.py`, `spek/composition/commands.py` | `resolve`, `compose-check`, `compose-preview` | Exécution locale privée |
| Registry reader existant | `spek/composition_registry.py` | Contrats des 19 recettes et assignations explicites | Lecture uniquement |
| GF existant | `scripts/realiser_composition_semantik.py` | Une page SPEK/PGF depuis requêtes et verrou | Privé, non publié |
| Constructeur existant | `scripts/construire_pages_kristals.py` | Collection HTML/Markdown et manifeste | Privé, non publié |
| **Overlay (nouveau)** | `scripts/orchestrer_registre_spek.py` | Contrôle de raccordement des deux niveaux puis délégation | Précontrôle, pas renderer |

**Ne pas confondre** `composition-registry.json` (recettes Arketype/layouts) et les 62 templates `rhetorical` (arbres exécutables). Une association entre ces familles doit être expliquée par le dossier éditorial; elle n'existe pas par simple égalité de noms.

## 2. Agriculture : la combinaison déjà enregistrée

- Identité canonique : `agriculture`.
- Composition principale : `arketype-modele-multiplexe` (`template_library/wiki/compositions/modele-multiplexe.json`).
- Recette historique : `entites` (`concept-card`), `couches` (`comparison`), `sources` (`evidence-comparison`). La proposition individualisée Agriculture ne retient actuellement que la première section parmi ses `ordered_sections` candidates : ne pas prétendre que les trois sont assignées.
- Revue approfondie, distincte de la recette générique : `soil` et `crop` (`agroecosystem-network`), `inputs` (`inputs-practices-matrix`), `practices` (`practice-interface-map`), `yield` (`evidence-constraint-matrix`), `cross` (`relation-network`).
- Le registre de revue mentionne **391 occurrences d'assertions en v8** et une empreinte brute du fichier portable étudié. La page source-littérale ultérieure provient d'un **autre graphe, v11.1, 408 assertions** : ne jamais présumer qu'une section, un ID ou une relation se transpose telle quelle. La revue/migration v11.1 n'est pas faite.
- Le pilote récursif à quatre sections utilisant surtout `wiki.domain-primer-source-bound`, `wiki.domain-section`, `rhetorical.definition` est une **démonstration locale non-GF**. C'est une composition valide, mais **pas** l'exécution des plans de registre Agriculture.
- Les cinq revues détaillées sont : AI, Accounting, Aerospace, Aging, Agriculture. Les 122 autres propositions nécessitent les données sources réelles pour être qualifiées.

## 3. Commandes Windows PowerShell 7

Depuis le dépôt SPEK installé :

```powershell
$spek='C:\mycode\Spek_Semantic-publishing\Spek'
$ctl=Join-Path $spek 'scripts\orchestrer_registre_spek.py'

# Vérification immédiate des choix enregistrés (ne modifie rien)
py -3.12 $ctl --spek-root $spek inspect --kristal agriculture

# Copie de structure NON REMPLIE dans un fichier privé neuf, hors Git
$binding=Join-Path $HOME 'Downloads\spek-agriculture-registre-liaison-privee.json'
py -3.12 $ctl --spek-root $spek scaffold --kristal agriculture --basis deep_review --out $binding
```

Le fichier contient les six sections exactes de la revue approfondie, mais **aucun chemin de source activé, aucune assertion sélectionnée, aucune page et aucune combinaison récursive validée**. Les renseigner explicitement après revue. `--basis recipe` reprend au contraire les sections **réellement proposées pour ce Kristal** dans les 127 fiches (pour Agriculture : `entites`, et non les trois sections de la recette générique); ne pas fusionner silencieusement les deux variantes.

Le contrat d'une page dans `pages` inclut `instance_sha256` (empreinte SHA-256 des **octets de l'instance SPEK**), en plus des `template_refs`. Le moteur vérifie les noms de templates, mais l'empreinte épingle aussi leur **combinaison exacte, leur ordre et leurs bindings**, qui ne doivent pas changer après revue. Le plan GF doit comprendre un `source_graph` explicite égal à `source_state.file` du dossier de liaison. La vérification du plan, des verrous et des résultats reste assurée par les **moteurs existants**.

Une fois la source et les demandes documentaires réellement présentes :

```powershell
$plan='C:\CHEMIN_PRIVE_VERIFIE\plan-collection-gf.json'
py -3.12 $ctl --spek-root $spek check --binding $binding --plan $plan

# Le même constructeur SPEK existant est invoqué UNIQUEMENT si check réussit.
$sa='C:\mycode\SemantiK_Architect\SemantiK_Architect'
$gf='C:\mycode\Grammatical-Framework\gf-3.12-windows\gf.exe'
py -3.12 $ctl --spek-root $spek build `
  --binding $binding --plan $plan --architect $sa `
  --runtime-root "$sa\runtime" --gf-exe $gf `
  --out "$HOME\Downloads\AGRICULTURE_GF_REGISTRE_PRIVE"
```

Le dossier de liaison utilise `spek.registry-first-explicit-bridge/1.0`. Remplir :

- `source_state.file` et son SHA-256 **des octets exacts**. Pour `basis=deep_review`, il doit correspondre au snapshot examiné en v8 (sinon **refus**, nouvelle revue requise).
- `pages` : identité/locale de chaque page du plan GF, chemin d'instance identique au plan, **empreinte SHA-256 de l’instance**, et ensemble exact de références des templates récursifs réellement résolus.
- `sections` : décision `include`/`omit` pour **chaque** section dans l'ordre du registre, justification d'omission ou bien IDs d'assertion, chemins sémantiques et `coverage` explicite (`page_key`, `realization_keys`). L'union des assertions par section doit être égale aux références des feuilles assignées; chaque feuille doit appartenir à une seule section.
- `status = EXPLICIT_PRIVATE_SELECTION_PENDING_INDEPENDENT_REVIEW`, `publication_authorized = false`. Cela permet uniquement **une tentative de réalisation privée**; ce n'est pas une décision éditoriale finale.

`check` ne remplace pas la validation sémantique indépendante. Le constructeur historique vérifie ses verrous et paires requête/résultat; le GF/PGF doit ensuite correspondre aux capacités exigées par le domaine, et l'article complet doit être revu avant Publisher.

## 4. Interopérabilité : aucune duplication

**Séquence attendue :** registre → sélection éditoriale explicite → contrôle overlay → `spek/composition/engine.py` → `scripts/realiser_composition_semantik.py` → SemantiK Architect / GF + RuntimeSet qualifié via SRO → `scripts/construire_pages_kristals.py` → vérification de site → revue humaine et autorisations C1/C2/C3/C4 → Publisher.

La commande historique `construire_pages_kristals.py build` reste accessible pour la compatibilité des pilotes privés déjà réalisés; elle **ne vérifie pas le registre**. Pour un nouveau document Kristal, appeler `orchestrer_registre_spek.py build` à sa place. Cet overlay n'altère ni le canon, ni les assignments d'autorité, ni le HTML du moteur.

**Ce que la recette ne prouve pas :** aucune réalisation de domaine Agriculture attestée par GF, aucune fidélité sémantique certifiée, aucune autorisation de publier, aucune activation Kristal.
