<!-- kOA Doc Server · Docs IA · lot 03 · projet : Spek · proposition dérivée à valider -->
# Navigation IA — Spek

**Objet constaté :** Composition éditoriale et publication multilingue avec templates récursifs et intégration SemantiK.

**Frontière de responsabilité :** Spek possède le document et l’édition; SemantiK Architect réalise les contenus linguistiques; publication et revue humaine sont distinctes.

**Source :** `SmartDump_20261120_221507.zip` → `Spek_Code_snapshot.zip` (20 novembre 2026). Le chemin Windows est une déclaration de snapshot, pas une vérification de l'état actuel.

**Statut :** Documentation de navigation dérivée de sources propriétaires, à revoir. Ce document ne vaut ni profil d'ingénierie mesuré, ni certification, ni permission d'exécution.

## Ordre de lecture — fichiers réellement présents dans la capture

1. [`README.md`](../../README.md) — SHA-256 `0fc730ed380cbe11…` dans la capture.
2. [`AGENTS.md`](../../AGENTS.md) — SHA-256 `3b33a80202cbcb3b…` dans la capture.
3. [`docs/README.md`](../../docs/README.md) — SHA-256 `883ee2bbb99671ed…` dans la capture.
4. [`docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md) — SHA-256 `6008da87fab342aa…` dans la capture.
5. [`docs/COMPOSITION_RECURSIVE_VNEXT/README.md`](../../docs/COMPOSITION_RECURSIVE_VNEXT/README.md) — SHA-256 `0b120ddd643c60a3…` dans la capture.

## Parcours recommandé pour une intervention assistée par IA

1. Identifier la question, le sous-système concerné et les responsabilités du propriétaire.
2. Lire les documents ci-dessus **dans cet ordre**; consulter les contrats et consignes propriétaires plus récents si le checkout a évolué.
3. Lire AGENTS, architecture et contrat de template, distinguer vNext des parties qualifiées, tester le rendu en bac à sable puis soumettre le résultat à revue.
4. Établir les vérifications effectivement disponibles dans la révision locale, consigner les résultats et ne conclure qu'à l'intérieur du périmètre couvert.
5. Proposer les changements; demander une décision explicite avant toute écriture à effet, déploiement, publication ou promotion de preuves.

## Risque propre à ce dépôt

Les 127 propositions de registre et les options de publication ne sont pas modifiées par la nouvelle architecture de templates; ne pas publier automatiquement.

## Compléments

- [`AI_CONTEXT.md`](AI_CONTEXT.md) : règles de travail et frontières de confiance.
- `AGENTS.md` : s'il existe déjà chez le propriétaire, ses consignes priment sur ces propositions; sinon l'overlay peut en ajouter un sans remplacement.
- `PROFIL_INGENIERIE.md` : optionnel, uniquement après exécution réelle de RepoSurveyor sur un dépôt local et accord explicite pour sa copie.
- Le Framework Kristal v11 est un standard documentaire **facultatif** : lire le profil réellement verrouillé, sans imposer de migration.

## Multilingual alignment — 2026-11-26

Read the [dated owner-context addendum](MULTILINGUAL_ALIGNMENT_2026-11-26.md). It records the observed scope, authority and pending gates; it does not replace owner contracts or certify current code.
