# 17 — Recette finale, traçabilité et responsabilités

**Statut : cible proposée, non implémentée.** Complète le document [16 — Audit et plan](16_AUDIT_ET_PLAN_DE_FINALISATION_2026-11-03.md).

## Responsabilités par frontière

| Décision ou action | Autorité principale | Spek doit | Spek ne doit jamais |
| --- | --- | --- | --- |
| Définir l'état canonique | Kristal/Manager | Référencer l'identité précise | Modifier le canonique |
| Sélectionner assertions et portée | Édition/Manager | Refuser la liste absente/non admise | Explorer le contenu pour improviser une sélection |
| Proposer le plan et les motifs rhétoriques | IA en amont | Valider le plan approuvé et les contrats | Prétendre qu'un motif « prouve » la relation |
| Approuver une relation sémantique | Autorité éditoriale compétente | Vérifier présence de verdict et portée | Déduire une causalité de deux définitions voisines |
| Produire les petites phrases | SemantiK Architect + RuntimeSet GF | Contraindre, appeler/importer, vérifier | Modifier, réécrire ou inventer les phrases |
| Rendre HTML/Markdown | Spek | Respecter modèle et accessibilité | Afficher les IDs internes à la lecture |
| Publier une page | Manager/autorités/dépôt public | Fournir paquet et audit | Pousser depuis aperçu ou `.pyw` |

## Contrats *proposés*, à spécifier avant implémentation

1. `spek.editorial-source-bundle/1.0` : `source_state`, `state_hash`, `assertions[]`, `approved_relations[]`, `scope`, `status`, `decision_refs`. Pour une simple proposition : `status: PENDING`, jamais déduire `APPROVED`.
2. `spek.editorial-plan/1.0` : `document_id`, `source_bundle_ref`, `intended_audience`, `language`, `sections[]`, `template_ref@semver`, `nodes[]`, `obligation_bindings[]`, `relation_bindings[]`, `limitations[]`.
3. `spek.execution-lock/1.0` : empreintes de l'état, du plan, de tous les templates et du catalogue, version Spek, version Architect, ID RuntimeSet, lexique, locale, contraintes et IDs de résultat.
4. `spek.review-report/1.0` : couverture par obligation, incohérences, relations non vérifiées, provenance, adéquation des réalisations, contrôles de confidentialité et décisions signées/identifiées.
5. `spek.reader-document/1.0` : IR de rendu construit seulement à partir de réalisations vérifiées, avec hiérarchie de titres, paragraphes, rôles, publications de sources autorisées, ordre et limites.

**Aucun de ces schémas n'est actuellement annoncé comme un contrat exécutable dans ce plan.** Ne pas les injecter directement dans les API SemantiK v1 existantes.

## Matrice de recette (véritable terminaison)

| ID | Essai | Résultat nécessaire |
| --- | --- | --- |
| T01 | Changer une assertion après verrouillage | Refus (état/hash divergent) |
| T02 | Utiliser une assertion non approuvée | Refus, aucun aperçu « vérifié » |
| T03 | Modèle causal sans preuve causale révisée | Refus ou rétrogradation explicite en modèle descriptif (pas automatique silencieuse) |
| T04 | Deux définitions sans relation | Aucun « donc », « parce que », « prouve » ajouté par Spek |
| T05 | Désigner un template avec version réinterprétée | Refus selon lockfile |
| T06 | RuntimeSet absent/incompatible/non RELEASED | Échec bloquant, zéro sortie SemantiK présentée comme réelle |
| T07 | Une des N réalisations manque | Échec atomique, sans fallback de fixture |
| T08 | Résultat SemantiK perd une obligation ou une limitation | Refus via validation de couverture/provenance et revue |
| T09 | Deux résultats deviennent interchangeables sans clé/provenance | Refus de permutation |
| T10 | Section « Sol » avec 8–12 unités GF/PGF réelles | Texte lisible, provenance de chaque unité et rendu privé vérifié |
| T11 | Réalisation grammaticale en français | Accord, référence anaphorique, ponctuation et limites examinés ; tests de conformance métier |
| T12 | HTML vs Markdown | Même hiérarchie, même contenu, mêmes réserves, formats corrects |
| T13 | Contenu source privé ou ID `urn:` / SHA dans lecture | Aucune fuite ; audit séparé |
| T14 | Aperçu privé sans reçus C1/C2/C3 | Publication techniquement interdite |
| T15 | Appuyer sur `.pyw` de prévisualisation | Pas de git add, commit, push, réseau implicite ni changement du canonique |
| T16 | Refaire le rendu avec mêmes locks | Sorties identiques à métadonnées volatiles exclues |
| T17 | Modification de lexique/runtime/template | Révision, requalification et nouvelle identité d'édition requises |
| T18 | 6 sections Agriculture complètes | Aucune phrase fixture, audit de couverture, revue de lecture et relations explicitées |
| T19 | Contrôle C1/C2/C3 et destination Wiki | Vérification par autorité appropriée avant action de publication distincte |
| T20 | Passage à un second Kristal | Nouveau plan individualisé ; aucune assignation présumée parmi les 127 propositions |

## Qualité éditoriale : éviter les faux indicateurs

Le nombre de templates ou la longueur du texte ne mesurent pas la qualité du discours. Un document plus court et rigoureusement borné est préférable à un discours riche construit sur des relations déduites. Pour chaque section, contrôler manuellement : question directrice intelligible, fidélité des propositions, ordre explicatif, cohésion sans répétition excessive, limites, références consultables, et absence de rhétorique injustifiée.

Les seuils numériques définitifs (par exemple proportion maximale de répétitions ou longueur moyenne de paragraphe) doivent être fixés après une revue du premier corpus réel ; **aucun seuil de qualité linguistique scientifique ne peut être déduit des 207 tests techniques**.

## Jalon immédiat à ouvrir en développement

**M1 — Agriculture/Sol (sans publication)**

Livrer dans cet ordre : (a) projection v6 versionnée et refs avec statut éditorial ; (b) plan « Sol » explicatif approuvé, soumis aux contrats rhétoriques ; (c) 8–12 requêtes SemantiK qui représentent les obligations effectives ; (d) RuntimeSet français GF/PGF qualifié pour ce sous-ensemble ; (e) HTML+Markdown privés et audit ; (f) rapport de revue avec tous les tests de recette applicables. Ne pas développer les cinq autres sections avant T10 et T11.
