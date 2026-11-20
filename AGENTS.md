# SPEK — règle permanente pour assistants et agents de code

**Lire d'abord** [`docs/POINT_ENTREE_REGISTRES_SPEK.md`](docs/POINT_ENTREE_REGISTRES_SPEK.md) et [`docs/CARTE_REPOS_ET_CHEMINS.md`](docs/CARTE_REPOS_ET_CHEMINS.md). Il n'est pas nécessaire de redécouvrir les registres à chaque intervention.

## Invariant éditorial

Ne jamais commencer un nouveau document Kristal par un assemblage improvisé de `rhetorical.definition` ou un sélecteur automatique de templates. SPEK possède déjà **deux niveaux distincts** :

1. **Registres éditoriaux** : 19 recettes Arketype/layouts, 127 propositions individualisées, cinq revues approfondies, 19 layouts spécialisés, registre des affectations approuvées actuellement vide.
2. **Moteur rhétorique récursif** : 62 templates versionnés, contrats de cardinalité et d'assemblage, réalisations fournies de l'extérieur.

Les deux niveaux n'ont pas un format interchangeable. Leur raccordement exige un **dossier de liaison explicite et vérifiable**, aucune inférence des faits par SPEK et aucune approbation implicite. Pour Agriculture, la proposition est `arketype-modele-multiplexe`; la revue spécialisée comporte six sections distinctes `soil`, `crop`, `inputs`, `practices`, `yield`, `cross`. Ne pas assimiler le pilote à quatre sections et ses fixtures à cette revue.

## Un seul chemin de fabrication

1. Inspecter la proposition avec `scripts/orchestrer_registre_spek.py inspect`.
2. Préparer un dossier explicite `scaffold` **privé** : tous les chemins, assertion IDs et champs sont initialement vides.
3. Renseigner seulement les valeurs autorisées et effectivement retrouvées dans l'état source exact; lier les sections, les clés de feuilles de l'instance SPEK et les choix de templates.
4. `check` avant `build`; `build` délègue au **même** `scripts/construire_pages_kristals.py`, lui-même dépendant du raccordement GF déjà installé. Ni nouveau renderer, ni nouveau moteur SemantiK.
5. Validation sémantique, revue humaine, C1/C2/C3/C4 et Publisher restent distincts; ne jamais publier depuis ce dépôt.

Pas de modifications du canon Kristal, pas de commit/push/publication automatique, pas de transfert des données sources dans un dépôt public. Ne pas modifier Konstellation dans la branche SPEK. Les chemins absolus sont une aide pour Windows, pas un accès distant à la machine.

## État des versions

L'overlay `v0.5.0a1` est une couche **privée et additive** sur le correctif cumulatif `v0.4.0a1`; ne remplace pas la version générale du produit SPEK et n'affirme pas un RuntimeSet Agriculture actif. L'aperçu Agriculture/Sol v11.1 reste une *fixture/source-littérale*. Le registre de revue Agriculture est rattaché à un snapshot portable **v8** : toute transition vers v11.1 exige une nouvelle revue de source, et ne peut pas être affirmée par une empreinte copiée.
