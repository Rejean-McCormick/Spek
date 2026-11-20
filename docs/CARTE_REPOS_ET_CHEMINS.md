# Carte des dépôts utiles à SPEK — chemins et niveaux de preuve

**Révision : 19 novembre 2026.** Cette carte sert d'index opérationnel, non de constat d'accès distant. Un chemin cité dans un guide n'est pas nécessairement présent sur le PC. Les connecteurs GitHub et le conteneur de travail ne peuvent pas exécuter des commandes dans un dossier local Windows sans résultat fourni par l'opérateur.

| Rôle | Chemin Windows | Justification / niveau de preuve |
|---|---|---|
| SPEK, code et template manager | `C:\mycode\Spek_Semantic-publishing\Spek` | **Confirmé** par `cd` et les journaux pytest utilisateur (26 tests passés). Dépôt distant lu : `Rejean-McCormick/Spek`. |
| SemantiK Architect, realization CLI | `C:\mycode\SemantiK_Architect\SemantiK_Architect` | **Confirmé** dans l'exécution réelle `render` avec GF. |
| Grammatical Framework, CLI Windows | `C:\mycode\Grammatical-Framework\gf-3.12-windows\gf.exe` | **Confirmé** par l'exécution du `CommunicationResult` français. |
| SemantiK Runtime Orchestrator | `C:\mycode\SemantiK_Architect\SemantiK_Runtime_Orchestrator` | **Chemin rapporté** dans le contexte technique antérieur; pas revérifié sur ce poste dans cette recette. |
| Konstellation | `C:\mycode\Konstellation\Konstellation` | **Confirmé** par le prompt PowerShell fourni; **branche distincte**, ne pas la modifier ici. |
| Kristal `locals` | `C:\mycode\Kristal\locals` | **Chemin cité dans les anciens guides SPEK**, pas confirmé comme chemin courant. Canon à déterminer localement, jamais inventé. |
| Kristal public (lecture) | chemin local **inconnu** | Dépôt distant **consulté** : `Rejean-McCormick/kristal-public` ; snapshot local sur serveur analysé. Ne pas inférer son emplacement Windows. |
| Kristal-Manager / C1/C2/C3 | chemin local **inconnu** | Acteur amont pour les décisions, les sources et les autorisations; aucune modification par cet overlay. |
| Arketype | chemin local **inconnu** | Les 19 recettes sont déjà vendues/versionnées **dans SPEK** ; inutile de dupliquer le moteur. |
| Publisher / EncyK Publication Orchestrator | chemin local **inconnu** | L'overlay ne déploie rien; exigences de publication indépendantes. |
| GF WordBench / GF Audit | chemins locaux **inconnus** | Conformance/compilation/audit amont; ne jamais traiter un PGF trouvé comme automatiquement publié. |

## Interfaces de code déjà existantes

- `spek/composition_registry.py`: validation des 19 recettes et affectations explicites (lecture seulement).
- `spek/composition/engine.py`, `spek/composition/commands.py`: templates récursifs et rendu HTML/Markdown, déjà testés sur Windows.
- `scripts/realiser_composition_semantik.py`: appelle le CLI officiel Architect/PGF; verrous et paires vérifiés.
- `scripts/construire_pages_kristals.py`: assemble le site statique privé et son manifeste.
- `scripts/orchestrer_registre_spek.py`: **seul nouvel adaptateur de contrôle**, ne contient aucun moteur de templates/rendu/publication.

## Règle anti-redécouverte

Avant de créer un outil, une composition ou un rapprochement nouveau, ouvrir dans cet ordre :

1. [`POINT_ENTREE_REGISTRES_SPEK.md`](POINT_ENTREE_REGISTRES_SPEK.md)
2. `template_library/wiki/kristal-ai-proposals.json` à la clé exacte du Kristal
3. `template_library/wiki/kristal-structure-reviews.json` à la clé exacte si elle existe
4. `template_library/wiki/composition-registry.json` et la recette citée
5. `template_library/wiki/kristal-assignments.json` pour vérifier si l'affectation est approuvée
6. `template_library/rhetorical/templates/` et la véritable instance de composition avant toute modification de code

Aucune action réseau, Git, canon, transfert de données privées ou Publisher n'est incluse dans le correctif.
