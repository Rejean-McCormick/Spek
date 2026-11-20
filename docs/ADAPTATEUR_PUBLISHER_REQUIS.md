# SPEK ↔ Publisher : alignement du lot statique récursif

**Décision :** les pages compilées par SPEK et les autorisations de publication sont deux étapes indépendantes. Le format `spek.private-static-collection/1.0` est **un format privé de ce correctif**, pas un nouveau contrat normatif approuvé du Publisher.

## État du code aujourd'hui

- SPEK vNext compose directement des **documents complets** HTML et Markdown en privé.
- Son historique `spek build --production` produit et vérifie un format de site **différent** (articles plats, manifestes et états v9), avec contrôles techniques.
- Le présent correctif assemble les pages récursives en un site HTML statique privé avec `site-manifest.json`, `site-manifest.sha256` et `publication-handoff.json`.
- `publication-handoff.json` déclare **toujours** `publication_eligible: false`, `public_authorized: false`, `c1_c2_c3: NOT_VERIFIED` et `publisher_contract: NOT_RATIFIED_FOR_RECURSIVE_SITE`.
- Le Publisher ne peut pas prendre ce statut privé et le requalifier silencieusement.

## Adapter sans dupliquer

Le futur adaptateur Publisher (à réaliser dans le composant qui possède l'autorité de livraison) recevra deux entrées séparées :

1. **Lot SPEK de lecture** : pages HTML/Markdown statiques, inventaire des empreintes, routes, langues, manifestes techniques ;
2. **Paquet de qualification externe** : identité/version canonique du Kristal, sélection/admission des assertions et relations, revue scientifique, revue linguistique, décision de divulgation et preuves C1/C2/C3 liées aux **octets exacts** du site, destination et révision d'édition.

Ni l'une ni l'autre de ces entrées n'est à créer automatiquement à partir d'un titre de template ou d'un statut « tests OK ». Les preuves privées sensibles restent dans un canal interne et **ne sont pas copiées dans GitHub Pages**.

```text
SPEK private static site + private approved editorial records
    -> Publisher adapter (future, external gate, explicit)
        -> verify hashes, policy, corpus identity, reviews, destination
        -> sanitized public build receipt, immutable edition identity
        -> explicit approved static deployment
```

### Règles de refus de l'adaptateur

- Une page absente ou un hash divergent refuse le lot entier.
- Une langue dont l'équivalence ou le RuntimeSet manque est refusée ; aucune traduction de secours.
- Une relation de preuve/causalité non qualifiée n'est pas réinterprétée en publication.
- Un `site-manifest` privé n'est jamais un manifeste de production SPEK à lui seul.
- Aucune qualification C1/C2/C3 rétroactive, aucun push/commit automatique, aucun contournement des barrières existantes.
- Tout export de logs doit supprimer les chemins, IDs de requêtes, identifiants privés et références de sources confidentielles.

## Première recette d'intégration (réservée au jalon suivant)

Avec une véritable page Agriculture/Sol : `compose-lock`, vérification de la sélection source, réalisation GF multilingue pour les langues *disponibles*, rendu SPEK, revue du document, contrôle de chaque empreinte, puis passage d'un paquet de décision approuvé à l'adaptateur Publisher. Vérifier la préservation de toutes les autorisations avant d'ajouter quelque opération réseau que ce soit.

La sortie du présent pack ne doit **jamais être placée telle quelle dans un dépôt Pages public**, même si son HTML s'ouvre dans un navigateur.
