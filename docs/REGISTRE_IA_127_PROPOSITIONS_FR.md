<!-- SPEK_REGISTRY_FIRST_V050A1 -->
> **MISE À JOUR OBLIGATOIRE (19-11-2026)** : lire `docs/POINT_ENTREE_REGISTRES_SPEK.md`
> et `docs/CARTE_REPOS_ET_CHEMINS.md` AVANT toute construction d'article Kristal.
> Les 19 recettes Arketype, les 127 propositions par Kristal, les cinq revues
> structurelles et les 62 templates récursifs existent déjà. Le nouveau script
> `scripts/orchestrer_registre_spek.py` contrôle une liaison explicite entre les
> deux niveaux et délègue aux moteurs déjà installés. Ce document conserve
> aussi ci-dessous son contenu historique, qui peut être antérieur à ces acquis.
> **Aucune proposition n'est une assignation approuvée. Aucun aperçu n'est publiable.**

# Spek — propositions éditoriales pour les 127 Kristals

## Source et périmètre

Ce registre est produit à partir du rapport `scan-20261102-151729-edac94.zip`, généré par Kristal-Manager le **2 novembre 2026**. Le rapport contient 127 entrées distinctes, des modèles natifs déclarés, leurs descriptions, des orientations et des chemins canoniques déclarés. Le rapport indique **`qualification: NOT_ESTABLISHED`**.

L'IA a choisi, à partir de ces métadonnées déclarées, **une recette principale et deux recettes complémentaires par Kristal**, soit des plans documentaires provisoires. Les compositions comprennent quatre à six sections sélectionnées dans les 19 recettes d'Arketype. La proposition ne prouve pas que chaque section peut être remplie : les champs obligatoires et les assertions sources doivent être examinés séparément.

## Où consulter

- **Interface :** `Spek_Template_Manager.pyw` → Bibliothèque → Wiki → **Kristals · compositions proposées (127)**, ou ouvrir un dossier Kristal local et cliquer sur **Voir la composition**.
- **Registre machine :** `template_library/wiki/kristal-ai-proposals.json`.
- **Catalogue HTML lisible :** `template_library/wiki/CATALOGUE_127_COMPOSITIONS_IA.html` (ouvrir dans un navigateur).
- **Recettes de base :** `template_library/wiki/compositions/*.json`.
- **Assignations exécutables / approuvées :** `template_library/wiki/kristal-assignments.json` reste volontairement **vide**.

## Interprétation des champs

- `primary_composition_id` et `supplementary_composition_ids` : décisions de design prises par l'IA, non déduites par le programme Spek.
- `ordered_sections` : ordre recommandé, avec IDs exacts de recette et de layout. Les chemins sont seulement des **candidats déclarés**, non des associations vérifiées aux assertions.
- `structural_layout_gaps` : besoins de layouts spécialisés déjà signalés dans les recettes, à examiner pour une projection fidèle.
- `observed_snapshot.digest_reported_unverified` : valeur rapportée, **non recalculée** ; ne pas l'utiliser comme `state_sha256` qualifié.
- `publication_eligible: false` : aucune publication autorisée par ce registre.

## Avant d'activer une assignation réelle

1. Examiner l'état canonique exact du Kristal et les relations de chaque partie.
2. Choisir les assertions et lier les IDs et chemins vérifiés aux sections.
3. Comparer chaque section aux champs obligatoires du layout ; retirer les sections non justifiées.
4. Calculer et épingler l'empreinte de l'état source, obtenir les formulations réelles de SemantiK Architect et vérifier leur couverture.
5. Approuver explicitement la composition et la page finale. Les autorisations C1/C2/C3 restent distinctes.

Aucun de ces contrôles n'est effectué automatiquement par le registre provisoire. **Spek ne choisit pas de templates et ne rédige pas de contenus**. Il peut uniquement afficher les propositions rédigées hors ligne par l'IA.

## Installation

Pour le correctif ZIP : fermer Spek, extraire le ZIP **dans le dossier parent de `Spek/`** en remplaçant les fichiers, puis lancer `START_SPEK.bat` ou `Spek_Template_Manager.pyw`. Le correctif ne modifie ni `GitSink.bat`, ni `locals`, ni les assignations approuvées. Vérifier les modifications Git avant tout push : ce registre est volontairement non qualifié et ne doit pas être interprété comme une publication.
