# Passe massive d'intégration — huit dépôts (2026-11-03)

## Portée et statut

**Candidat technique d'intégration, non qualifié comme produit final.**
Les modifications de cette passe sont coordonnées entre Spek, SemantiK Architect,
SemantiK Runtime Orchestrator, Kristal-Manager, Arketype, Kristal-Framework,
Kristal-Integration-Pack et kristal-public. Aucun fichier canonique n'est
modifié, aucune phrase GF/PGF n'est produite, aucun contrôle C1/C2/C3
n'est contourné, aucune publication GitHub n'est déclenchée.

## Échange privé versionné

La commande `compose-lock` produit `spek.private-editorial-handoff/1.0`.
Elle exige un binding explicite pour chaque phrase et des obligations
`CommunicationRequest/1.0` dont les `source_refs` correspondent exactement
aux assertions sélectionnées dans le slot. Elle épingle les SHA256 des templates,
requêtes et de la composition. Les relations rhétoriques restent déclarées mais
**non vérifiées**. `compose-verify-lock` recalcule tous ces engagements.

Ce document contient des identifiants privés et ne doit **jamais** être mis
sous contrôle de version dans un dépôt public. Les aperçus HTML/Markdown ne
contiennent pas ce paquet. L'interface graphique offre « Vérifier les sources
et verrouiller le plan… » sous les options avancées.

### Identité historique v6 et v11

Le pilote Agriculture référence des assertions historiques du corpus v6.
Le graphe v11 contient des IDs stables nouveaux (`KA...`). Le Kristal
possède une table de migration explicite
`.kristal/v11/identity-migration-map.json`, sous `by_kind.A`.

Les contrôles `compose-source-check` et `compose-lock` acceptent désormais
`--identity-map` avec `--source-graph`, sans jamais traduire ou réécrire les
identifiants dans les requêtes. **La table, le graphe et leurs empreintes
font partie de la preuve privée**, mais ne certifient pas le sens.

### Défaut décelé dans le pilote Agriculture

- 51 slots au total ; **50** possèdent un ancrage explicite.
- `limites.portee` ne comporte aucun `source_assertion_refs` et formule une
  précaution de domaine : la chaîne stricte la **refuse**.
- Une variante de recette `wiki.domain-primer-source-bound@1.0.0` permet,
  lorsqu'elle est explicitement choisie par l'éditeur, d'omettre ce slot
  non sourcé ; elle ne le transforme pas en fait ni en autorisation.
- La variante privée de recette utilisée pour la qualification technique
  conservait 50 demandes d'Architect et 25 assertions distinctes.
- Le contrôle via la table de migration réelle a trouvé 25 correspondances
  v6→v11 ; le contrôle de Manager ne confère aucune autorité C1/C2/C3.

## Contrats séparés

- **Spek** : composition, verrous des entrées, source binding, affichage privé.
- **Manager** : contrôle d'existence et d'identité dans le graphe fourni,
  sans qualifier les relations ni autoriser la publication.
- **Architect** : validation du contrat des demandes et obligations
  `CommunicationRequest/1.0`, sans grammaire ni reformulation libre.
- **Runtime Orchestrator** : contrôle d'activation, des artefacts `.pgf`,
  des hashes et des preuves de conformité ; une présence locale n'est pas
  une preuve que toutes les phrases sont réalisables.
- **Arketype** : 57 suggestions versionnées couvrant 19 archétypes,
  explicitement non normatives et non sélectionnantes.
- **Framework** : profil JSON Schema d'interopérabilité privé, sans
  modification du canon normatif v11.
- **Integration Pack** : audit multi-processus des huit dépôts, sans Git ni réseau.
- **kristal-public** : le contrôleur Wiki rejette les signatures de
  provenance interne dans les pages candidates.

## Commandes Windows (aucun script PowerShell)

Depuis `C:\mycode\Spek_Semantic-publishing\Spek`, avec un pilote local installé :

```text
py -3 -m spek compose-source-check --instance pilotes_prives\agriculture-premier-document\instance\agriculture.instance.json --state-source <graphe-v11.json> --identity-map <identity-migration-map.json>
```

Le verrou exige un dossier privé extérieur au dépôt :

```text
py -3 -m spek compose-lock --instance <composition.instance.json> --requests-dir <dossier-requests> --source-graph <graphe-v11.json> --identity-map <identity-migration-map.json> --out <nouveau-fichier-prive.json>
```

`compose-verify-lock` recalcule le verrou avec les mêmes arguments plus
`--lock`. Le code échoue si un champ n'est pas sourcé, si un fichier a changé
ou si les identités ne sont pas reliées explicitement.

## Blocages pour déclarer le PRODUIT FINAL

1. Compiler et qualifier un **vrai** RuntimeSet `agriculture-reference-1`
   avec des programmes GF/PGF testés. Les snapshots fournis ne contiennent
   **aucun** fichier `.pgf` et aucun compilateur `gf` n'était installé ici.
2. Exiger que les relations nécessaires à une argumentation soient elles-mêmes
   justifiées, pas seulement présentes dans les assertions.
3. Alimenter les 62 templates par des compositions éditoriales révisées,
   et pas seulement les définitions du glossaire pilote.
4. Qualifier la fidélité linguistique de chaque réalisation et le document
   dans son ensemble ; les tests structurels seuls ne suffisent pas.
5. Vérifier les approbations indépendantes C1/C2/C3 sur les artefacts publics
   exacts avant tout `git push`.
6. Corriger les échecs préexistants des tests et ressources manquantes dans
   les snapshots Manager, Arketype et kristal-public. Ne jamais les masquer
   en faisant échouer ouvert les contrôles de publication.

Aucune de ces étapes ne doit devenir un mécanisme de phrases fictives pour
remplacer un RuntimeSet absent. La chaîne échoue fermée par défaut.
