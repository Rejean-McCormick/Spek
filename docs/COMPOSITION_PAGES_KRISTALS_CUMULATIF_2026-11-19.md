<!-- SPEK_REGISTRY_FIRST_V050A1 -->
> **MISE À JOUR OBLIGATOIRE (19-11-2026)** : lire `docs/POINT_ENTREE_REGISTRES_SPEK.md`
> et `docs/CARTE_REPOS_ET_CHEMINS.md` AVANT toute construction d'article Kristal.
> Les 19 recettes Arketype, les 127 propositions par Kristal, les cinq revues
> structurelles et les 62 templates récursifs existent déjà. Le nouveau script
> `scripts/orchestrer_registre_spek.py` contrôle une liaison explicite entre les
> deux niveaux et délègue aux moteurs déjà installés. Ce document conserve
> aussi ci-dessous son contenu historique, qui peut être antérieur à ces acquis.
> **Aucune proposition n'est une assignation approuvée. Aucun aperçu n'est publiable.**

# SPEK — pages documentaires complètes, correctif cumulatif

**Date :** 19 novembre 2026  
**Statut :** implémentation additive et prévisualisation privée ; publication publique bloquée jusqu'aux qualifications externes.  
**Dépôt cible :** SPEK sur la base GitHub `0358b2e9fefadae44902f9d3b4b38ef11a5081e6`, sous réserve de conformité du clone local.

## 1. Objet — ce n'est plus un simple générateur de phrases

La chaîne de conception et de réalisation existante de SPEK sait **déjà produire des pages HTML complètes et des documents Markdown** à partir des compositions récursives et des unités SemantiK.

Ce correctif conserve le pilote GF précédent (`scripts/realiser_composition_semantik.py`) et ajoute **l'assemblage de plusieurs pages en une collection statique consultable**. Il n'implémente aucune nouvelle grammaire GF, aucun moteur de templates, aucun choix automatique de faits, ni aucun Publisher parallèle.

```text
Kristal (état et assertions exacts)  -- décision éditoriale explicite -->
composition SPEK (template récursif, sous-templates, sections, rhétorique)
  -- compose-lock source/plan/templates/requests -->
CommunicationRequest(s) par langue
  -- SemantiK Architect + PGF vérifié et activé -->
CommunicationResult(s) avec obligation et source
  -- SPEK compose-import-semantik et preview natifs -->
PAGE HTML COMPLÈTE + PAGE MARKDOWN
  -- correctif cumulatif assemble -->
INDEX + PAGES PAR LANGUE + MANIFESTE ET EMPREINTES
  -- revue/qualification/admission séparées -->
Publisher (plus tard, seulement après autorisations)
```

**Formats livrés par le moteur récursif actuel : HTML et Markdown.** Les anciens rendus PDF/LaTeX existent pour les anciens layouts ; on ne les revendique pas comme compilés par cette branche récursive sans la migration et les tests correspondants.

## 2. Capacités SPEK réutilisées au lieu d'être recodées

- `template_library/rhetorical/templates/` : **62 templates** avec grammaire du discours ;
- `template_library/wiki/compositions/` : **19 compositions candidates** ;
- `layouts/` : **27 layouts historiques et spécialisés** ;
- `template_library/wiki/kristal-ai-proposals.json` : **127 propositions**, non assignations approuvées ;
- `spek.composition.engine` : expansion récursive des templates ;
- `spek.composition.editorial_lock` : vérification des empreintes et des références ;
- `spek.composition.semantik_adapter` : contrôle strict des résultats SemantiK ;
- `spek.composition.commands.preview` : HTML/Markdown natifs ;
- `scripts/realiser_composition_semantik.py` (correctif antérieur compris) : exécution réelle de chaque feuille via CLI SemantiK.

Aucun des 127 choix proposés ne devient approuvé par le présent patch. Le registre d'assignations SPEK demeure inchangé.

## 3. Installer cumulativement sous Windows

Extraire le ZIP **dans un dossier temporaire, hors de SPEK** puis, depuis PowerShell :

```powershell
cd "C:\DossierOuLeZipEstExtrait"
py -3.12 .\INSTALLER_CUMULATIF.py --target "C:\mycode\Spek_Semantic-publishing\Spek"
py -3.12 .\INSTALLER_CUMULATIF.py --target "C:\mycode\Spek_Semantic-publishing\Spek" --install
```

Sans `--install`, vérification seulement. L'installateur :

1. vérifie la présence des modules SPEK existants ;
2. recalcule tous les SHA-256 des fichiers de correctif ;
3. reconnaît les quatre fichiers identiques du correctif GF précédent et ne les remplace pas ;
4. crée exclusivement les nouveaux fichiers ;
5. **refuse toute collision avec un fichier de contenu différent** ;
6. ne fait aucun appel réseau et n'utilise ni Git ni activation de RuntimeSet.

Un rollback consiste à retirer uniquement les fichiers ajoutés, après vérification qu'ils n'ont pas été modifiés par l'utilisateur. Les fichiers SPEK originaux ne sont pas remplacés.

## 4. Préparer UNE vraie composition (avant le lot)

Les contenus sont préparés par le responsable éditorial ou Manager dans un dossier privé hors dépôt. Les références du Kristal, la sélection des assertions et le choix des templates doivent être **explicites**.

```powershell
$spek="C:\mycode\Spek_Semantic-publishing\Spek"
cd $spek
py -3.12 -m spek compose-check --instance "C:\ProjetPrive\agriculture\sol\instance-fr.json"

py -3.12 -m spek compose-lock `
  --instance "C:\ProjetPrive\agriculture\sol\instance-fr.json" `
  --requests-dir "C:\ProjetPrive\agriculture\sol\requests-fr" `
  --language fr `
  --source-graph "C:\ProjetPrive\agriculture\sol\semantic-graph.json" `
  --identity-map "C:\ProjetPrive\agriculture\sol\identity-migration-map.json" `
  --out "C:\ProjetPrive\agriculture\sol\verrou-fr.json"
```

Si une table v6→v11 n'est pas pertinente pour l'état choisi, supprimer `--identity-map`. Le graphe/source est une référence de vérification de présence, **pas** une preuve que des relations rhétoriques sont justifiées.

**Important :** le RuntimeSet `konstellation-fr-3` a réellement généré la phrase A001 sur le Windows de l'utilisateur, mais **cela ne le qualifie pas pour le lexique et le discours d'Agriculture**. Ne pas copier cet ID dans un plan Agriculture sans une requête et un profil compatibles. Le plan exemple contient des champs à remplacer volontairement.

## 5. Planifier plusieurs pages et langues

Copier `examples/PLAN_COLLECTION_PRIVEE.exemple.json` dans `C:\ProjetPrive\ma-collection\plan.json` et modifier :

- `collection` — identifiant, titre et description ;
- `pages[]` — **une entrée par Kristal/section/langue** ;
- `id` — slug stable, réutilisé pour les autres langues de la même page ;
- `instance` — `spek.composition-instance/1.0` exacte ;
- `requests_dir` — dossier des requêtes SemantiK de cette langue ;
- `lock` — verrou privé produit via `compose-lock` pour cette même langue ;
- `profile` et `runtime_id` — obligatoirement compatibles avec les sélecteurs des requêtes et les RuntimeSets réels ;
- `source_graph` et `identity_map` — référence de vérification d'existence et migration (facultatives pour un essai privé ; recommandées pour toute préparation sérieuse).

Les chemins locaux d'entrée et le contenu des verrous **ne sont jamais intégrés** au site généré. Pas de classeur canonique scanné automatiquement, pas de traduction fictive. Aucune entrée implicite pour une langue indisponible.

**Limite du SPEK vNext actuel :** `fr`, `en`, `it`. Les autres langues exigent une extension explicite du moteur SPEK et des RuntimeSets SemantiK qualifiés. Le fait que le futur objectif soit quinze langues ne constitue pas une couverture actuelle.

## 6. Construire un site HTML statique privé

```powershell
$spek = "C:\mycode\Spek_Semantic-publishing\Spek"
$sa = "C:\mycode\SemantiK_Architect\SemantiK_Architect"
$gf = "C:\mycode\Grammatical-Framework\gf-3.12-windows\gf.exe"

cd $spek
py -3.12 scripts\construire_pages_kristals.py build `
  --spek-root "$spek" `
  --plan "C:\ProjetPrive\ma-collection\plan.json" `
  --architect "$sa" `
  --runtime-root "$sa\runtime" `
  --gf-exe "$gf" `
  --out "C:\ProjetPrive\sites-prives\edition-001"
```

Le moteur :

1. valide toutes les entrées et refuse les pages/variantes dupliquées ;
2. exécute **toutes les feuilles** de chaque composition avec le PGF choisi ;
3. utilise les contrôles SPEK existants pour couverture/obligations/sources et identité du résultat ;
4. écrit chaque HTML/Markdown natif de SPEK ;
5. ajoute une navigation entre les pages et langues sans modifier le texte de `<article>` ;
6. construit un index lisible ;
7. écrit un manifeste de fichiers et leurs SHA-256, plus un handoff privé ;
8. vérifie le site entier ; publie atomiquement le résultat **uniquement** si toutes les pages passent.

Aucune page partielle ne reste dans `edition-001` lorsqu'une langue ou un champ échoue. Il faut sélectionner **une nouvelle destination vide** à chaque édition.

### Arborescence du résultat

```text
edition-001/
  index.html
  pages/
    fr/
      agriculture-sol/
        index.html    <- HTML SPEK complet
        page.md       <- Markdown SPEK
    en/
      agriculture-sol/
        index.html
        page.md
  publication-handoff.json     <- privé, publication_eligible: false
  site-manifest.json           <- routes + empreintes
  site-manifest.sha256         <- contrôle du manifeste
```

Ouvrir `index.html` localement dans le navigateur. Les liens relatifs fonctionnent sans serveur ni réseau.

## 7. Vérifier et créer le lot privé

```powershell
py -3.12 scripts\construire_pages_kristals.py verify "C:\ProjetPrive\sites-prives\edition-001"

py -3.12 scripts\construire_pages_kristals.py package `
  "C:\ProjetPrive\sites-prives\edition-001" `
  --out "C:\ProjetPrive\lots-prives\edition-001-prive.zip"
```

Le ZIP ne comprend **que** les pages statiques et leurs manifestes : jamais les requêtes, verrous, chemins canoniques, outils GF ou caches privés. Il porte un statut **non publiable**.

## 8. Ce qui reste à faire AVANT la publication

Une page HTML statique peut techniquement être hébergée sur GitHub Pages ou par un serveur statique, mais **ce pack ne confère aucune autorisation de publication** et ne crée aucun déploiement.

Le vrai Publisher doit être raccordé à ce nouveau format récursif, avec réception d'un bundle approuvé, vérification du Kristal et des pages exactes, revues éditoriales et linguistiques, contrôles C1/C2/C3 puis signature/autorisation de la destination. Ne pas contourner le pipeline historique `spek build --production` en faisant passer `site-manifest.json` pour son manifeste : les formats sont distincts. Voir `docs/ADAPTATEUR_PUBLISHER_REQUIS.md`.

## 9. Recette réalisée dans ce pack / limites

- **31 tests autonomes passés** sur les deux scripts additifs ; les cas d'exécution GF sont simulés dans ces tests (le véritable essai GF sur Windows, A001, est fourni par l'utilisateur séparément).
- Deux langues/pages testées sur un moteur SPEK simulé ; HTML complet, Markdown, index et liens ; refus des doublons, chemins risqués, contenu actif, modification après empreinte, destination Git, résultat partiel.
- Pas de test Windows du nouveau constructeur, pas d'essai de composition Agriculture réelle, pas de qualification des 15 langues, pas d'activation ni de publication.

**Critère du prochain jalon :** une première page Agriculture/Sol issue d'une instance éditoriale verrouillée et de **plusieurs** réalisations GF admissibles, inspectée dans son HTML/Markdown complet. Ensuite seulement industrialiser la collection.
