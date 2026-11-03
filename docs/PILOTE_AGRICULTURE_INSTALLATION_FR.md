# Pilote Agriculture — archive à déposer dans Spek

**Statut** : brouillon privé issu de 25 assertions canoniques, 51 demandes de formulation structurées, **0 réalisation GF/PGF**.

## Installation

Extraire `SPEK_PILOTE_AGRICULTURE_LANCEURS_PYW_DEPOT_DIRECT_2026-11-03.zip` **à l'intérieur** de la racine du dépôt Spek :

`C:\mycode\Spek_Semantic-publishing\Spek\`

L'archive ne contient pas de préfixe `Spek/`. Elle n'écrase pas le moteur ou les fichiers Git existants.

## Fichiers installés

- `template_library/wiki/templates/domain-primer.json` : template de document Wiki.
- `template_library/wiki/templates/domain-section.json` : template de section.
- `pilotes_prives/agriculture-premier-document/` : projet pilote, instance, requêtes, aperçus, scripts et audit privé.
- `pilotes_prives/.gitignore` : ignore les projets privés lors d'un `git add .`.

## Ouvrir le pilote sous Windows (sans script PowerShell)

Dans l'Explorateur Windows, ouvrir :

`pilotes_prives\agriculture-premier-document\PILOTE_AGRICULTURE.pyw`

La fenêtre contient trois actions : **Tester le plan**, **Générer et ouvrir l'aperçu privé**, **Ouvrir l'aperçu déjà fourni**.

Les deux raccourcis `.pyw` suivants peuvent aussi être lancés directement :

- `TESTER_PLAN_SPEK.pyw` : ouvre la fenêtre et démarre la validation.
- `PREVISUALISER_PILOTE_AGRICULTURE.pyw` : ouvre la fenêtre et régénère un aperçu dans un nouveau dossier temporaire privé.

Les `.pyw` nécessitent Python 3 et l'association Windows des fichiers `.pyw` à Python. Ils n'utilisent **ni PowerShell ni sa politique d'exécution**. Les erreurs s'affichent dans la fenêtre.

En cas d'absence d'association `.pyw`, utiliser cette commande depuis le dossier Spek :

```powershell
py -3 .\pilotes_prives\agriculture-premier-document\PILOTE_AGRICULTURE.pyw
```

L'ancien fichier `OUVRIR_PILOTE_AGRICULTURE.cmd` ouvre seulement l'aperçu HTML déjà présent, sans recalcul.

**Si tu as déjà extrait une version précédente** : les anciens `.ps1` restent éventuellement sur ton disque (une extraction ZIP ne supprime pas les anciens fichiers). Ils ne sont plus nécessaires ; tu peux les supprimer manuellement. Il n'est pas nécessaire de changer `ExecutionPolicy`.


## Frontières

Les phrases du premier aperçu sont des valeurs sources littérales, **pas** des textes produits par SemantiK. Le projet de réalisation GF/PGF attend un RuntimeSet utilisable et approuvé. Aucune publication Wiki ni qualification C1/C2/C3 n'est incluse. Les dossiers `interne/` et `requests/` contiennent des données techniques privées : ils ne doivent pas être publiés.
