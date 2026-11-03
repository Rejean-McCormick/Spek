# 16 — Audit approfondi et plan de finalisation Spek vNext

**Date :** 2026-11-03  
**Statut :** plan proposé et vérifié contre les archives fournies ; **aucune modification du moteur livrée par ce document**.  
**Objectif :** passer d'un pilote Agriculture de définitions sources à un article réellement réalisé par SemantiK, assemblé par Spek, justifié assertion par assertion, puis publiable par un parcours indépendant de qualification.

## 1. Dossier examiné et limite des conclusions

Archives examinées : `SPEK_REPO_COMPLET_GRAMMAIRE_DISCURSIVE_2026-11-03.zip`, `SPEK_PILOTE_AGRICULTURE_LANCEURS_PYW_DEPOT_DIRECT_2026-11-03.zip`, `znapshot_SemantiK_Architect_11021338.zip`, `znapshot_SemantiK_Runtime_Orchestrator_11021338.zip`, `Kristal-Manager_Code_snapshot(9).zip`.

**Test réel de l'archive Spek extraite :** `python -m pytest -q --disable-warnings --maxfail=1` → **207 passed, 28 subtests passed** (environnement Linux du contrôle ; ne constitue pas une vérification Windows ni GF/PGF). L'appel direct à `pytest -q` ne trouvait pas le module `spek` dans cet environnement : garder `python -m pytest` comme entrée portable.

**Agriculture :** 391 assertions présentes dans la source annoncée ; 25 assertions distinctes intégrées ; 51 feuilles/réalisations de type `fixture`, dont des titres, étiquettes et définitions ; six sections ; aucun résultat GF/PGF réel ; qualification/publication absentes. Le pilote référence un état canonique **v6**, tandis que `spek/composition/source_binding.py` vérifie seulement les identifiants d'un graphe **v11 explicitement fourni**. Ne pas confondre les deux contrôles.

**Fait architectural :** les 62 modèles rhétoriques comportent des `discourse_model`, mais le pilote Agriculture utilise principalement `rhetorical.definition` (19 instances), `rhetorical.qualification` (une instance), et les deux templates Wiki `domain-primer`/`domain-section`. Les modèles disponibles ne constituent donc pas une preuve d'orchestration éditoriale riche.

## 2. Diagnostic causal

### D1 — Un article n'est pas une série de définitions

Le pilote découpe le corpus par domaines puis remplit un couple « libellé → définition ». Il manque un **plan éditorial explicite** pour chaque section : question directrice, angle du passage, relations justifiées, ordre des mouvements, limites, liens entre sections, contenu non retenu et motifs de refus.

**Conséquence :** un texte exact sur chaque terme peut demeurer un glossaire. Ajouter d'autres patterns sans produire les relations autorisées ne résout pas le problème.

### D2 — Les requêtes SemantiK sont grammaticalement trop pauvres pour une rhétorique riche

Les 51 requêtes existantes s'appuient principalement sur une relation locale `has_definition`, un sujet et une valeur littérale ; l'obligation habituelle porte une seule assertion et `ordering: FREE`. Ce modèle peut demander une réalisation de définition, mais ne représente pas, par lui-même, une comparaison, un support de preuve, une condition, une causalité ou une opposition **à contenu**.

**Règle :** la relation rhétorique doit être soutenue par un lien de provenance et une décision éditoriale révisée ; le fait de choisir un template nommé `rst-cause` ne suffit jamais.

### D3 — La validation actuelle ne certifie ni le sens ni la publication

`resolve()` vérifie références, cardinalités et contrats. `discourse_audit()` compte les liens **déclarés, non vérifiés**. `verify_v11_assertion_refs()` contrôle l'existence des IDs dans un graphe v11, pas la correspondance sémantique ni l'autorisation. L'import SemantiK vérifie les paires requête/résultat après réalisation, mais le pilote utilise des fixtures.

**Règle :** distinguer « ID existe », « assertion autorisée », « relation étayée », « réalisation fidèle » et « publication autorisée ».

### D4 — Le RuntimeSet est un verrou dur, pas une option UX

Le snapshot Architect reçu comporte des sources `.gf` et les manifests des profils Konstellation, mais pas de `.pgf` compilé. Le profil Agriculture demandé (`agriculture-reference-1`) n'est pas déclaré comme profil publié du RuntimeSet reçu. Une validation de schéma des 51 requêtes ne prouve donc pas leur réalisabilité.

**Règle :** un RuntimeSet complet, compatible, qualifié, avec lexique du domaine et preuves de conformité est une dépendance externe indispensable. Ne jamais remplacer son absence par des reformulations Python ou IA présentées comme résultats SemantiK.

### D5 — Les rendus restent des projections de phrases complètes

`engine.py` possède une représentation récursive et quatre dispositions (`flow`, `stack`, `two_column`, `compact_list`), mais le rendu HTML et Markdown est codé séparément. Le rendu HTML émet actuellement un `<h2>` fixe pour un slot `section_heading`, sans dériver une hiérarchie sémantique de documents imbriqués. Les frontières de paragraphe sont prescrites au template, sans vérification de fluidité interphrastique.

**Conséquence :** il faut une **représentation intermédiaire de lecture** commune aux deux formats, avec titres hiérarchisés, paragraphes, listes, citations autorisées, blocs comparatifs et contrôle de la ponctuation/jointure.

### D6 — Le versionnement est insuffisamment immuable

La doc vNext reconnaît que certains contrats rhétoriques ont été enrichis tout en gardant `@1.0.0`. À composition et version identiques, un catalogue modifié peut changer un rendu. Épingler le commit ou le hash actuellement est un palliatif.

**Règle :** toute modification de sémantique de slot, de mouvement, de groupe de paragraphes ou de rendu contractuel exige une nouvelle version de template et un lockfile d'exécution.

### D7 — Prévisualiser, approuver et publier sont trois opérations différentes

Le Manager fourni distingue observation, proposition, approbation, application et publication. Les règles C1/C2/C3 et les étapes GitHub ne peuvent être remplacées par un bouton « publier » dans Spek ; la publication du Wiki natif est un parcours distinct du push du corpus public.

## 3. Architecture cible : responsabilités préservées

```text
Kristal canonique immuable (état précis et référentiel des assertions)
       │
       ▼
Kristal-Manager : projection admissible + sélection validée + contexte C1/C2/C3
       │   paquet de faits autorisés, relations sourcées et portée
       ▼
Plan éditorial IA : proposition lisible et vérifiable, jamais auto-approuvée
       │   sections + objectifs + références + relations + templates épinglés
       ▼
Spek : validation du plan, expansion récursive, slots et exigences de forme
       │   requêtes SemantiK et ordre des obligations sous contrôle
       ▼
SemantiK Architect + RuntimeSet GF/PGF QUALIFIÉ : petites réalisations FR
       │   blocs, couverture et provenance exactes
       ▼
Spek : vérification + document IR unique + HTML/Markdown privés
       │   audit sémantique et relecture éditoriale
       ▼
Kristal-Manager / autorité de publication : qualification et C1/C2/C3
       │   paquet signé/pinné et confirmation explicite
       ▼
Export GitHub Wiki / pages autorisées (action séparée)
```

**Interdictions invariantes :** Spek ne parcourt pas le Kristal pour choisir les faits ; SemantiK ne décide pas du plan de chapitre ; le moteur Spek n'écrit pas une phrase de secours ; l'IA propose le plan et les relations sans les transformer en faits canoniques ; un aperçu n'accorde aucun droit de publication.

## 4. Plan ordonné par dépendances

### P0 — Stabiliser le dépôt et les contrats

**Dépendances :** aucune. **À faire d'abord.**

- Geler la version de référence, les fixtures, les 207 tests / 28 sous-tests ; maintenir une preuve CI Linux et Windows (`py -3 -m pytest`).
- Inventorier les 62 contrats et leurs empreintes ; publier des définitions réellement immuables et augmenter les versions quand la présentation ou la rhétorique changent.
- Distinguer nettement trois statuts de sortie : `fixture_demonstration`, `source_literal_review`, `semantik_verified`; aucun n'implique `publishable`.
- Ajouter une seule commande de diagnostic d'environnement : Spek, Python, données source, version Manager, sélection, profil SemantiK, runtime GF, ressources lexicales, dossier privé.
- Assurer l'exclusion Git du pilote et des artefacts temporaires ; rien de sensible sous l'arborescence des pages publiables.

**Recette :** un même manifeste de composition donne exactement la même sortie avec les mêmes entrées ; modifier une définition épinglée entraîne un refus explicite.

### P1 — Construire la projection éditoriale canonique Agriculture

**Dépendance : P0. Responsable des autorisations : Kristal-Manager.**

- Lire les vrais artefacts v6 du pilote, puis définir l'adaptateur v6 → paquet d'assertions autorisées ; accepter ultérieurement v11 via adaptateur distinct et identifié ; ne jamais comparer implicitement des IDs entre versions.
- Produire un `EditorialSourceBundle` immuable : état/hash, assertions choisies, portée, polarité, modalités, qualificatifs, exceptions, source(s), éventuelles relations déjà présentes et statut décisionnel.
- Séparer `has_definition`, relations explicites du graphe, relations éditoriales proposées et relations approuvées ; ne jamais élever l'une au statut de l'autre.
- Pour chaque lien rhétorique envisagé, stocker `source_assertion_refs`, type de relation, justification, niveau de confiance, auteur/relecteur, `APPROVED` / `PENDING` / `REJECTED` et restrictions.
- Interdire la création de liens causaux/comparatifs sans preuve suffisante ; autoriser des structures descriptives plus modestes, par exemple les attributs du sol dans une élaboration, lorsque l'adéquation est révisée.

**Recette :** toutes les obligations visibles dans une phrase et tous les liens sémantiquement substantiels renvoient à des assertions et à une décision ; les seules définitions ne peuvent pas passer pour des preuves de causalité.

### P2 — Plan éditorial exécutable, proposé par l'IA et révisable

**Dépendance : P1.**

- Introduire un `EditorialPlan/1.0` (contrat nouveau, proposé) : identité de Kristal/état, public/langue/genre, sections, question directrice, contenu autorisé, liens, template(s) versionnés, cardinalités, priorité de lecture, politique de titres, limites obligatoires et exclusions motivées.
- L'IA analyse la projection **autorisée** et propose, pour chaque section, un **graphe de mouvements** ; elle ne remplit pas la chaîne publique avec des phrases libres ni n'ajoute d'assertions.
- Définir pour Agriculture une composition explicative, et non une série de 19 cartes de définition : introduction → système → six sections → intégration transversale → portée/limites.
- Sélectionner un sous-ensemble étayé des 62 modèles : `definition`, `rst-elaboration`, `rst-background`, `rst-contrast`/comparaison seulement si des bases comparables existent, `qualification`, `rst-summary` ; réserver `rst-cause`, Toulmin/Walton aux relations qui supportent réellement ces mouvements.
- Conserver une revue de plan humaine/Manager séparée du simple « plan structurel valide ».

**Recette :** la section « Sol » décrit le sujet, distingue texture/structure/matière organique, utilise des paragraphes cohérents et expose ses limites, sans inventer une conséquence agronomique.

### P3 — Dialogue Spek → SemantiK enrichi au niveau du passage

**Dépendance : P2 ; collaboration avec le propriétaire d'Architect.**

- Projeter chaque feuille vers une `CommunicationRequest` officielle à partir des obligations **déjà admises**, pas de `string` brut réétiqueté en fait.
- Conserver `semantic_graph`, `obligations`, provenance et conditions de validité ; définir une intention de phrase (définition, cadrage, comparaison, concession, qualification, liaison) et sa portée.
- Établir une politique de cohésion au niveau du *passage* : ordre contraint, entités saillantes et références anaphoriques, transitions non factuelles autorisées par Architect, limites de longueur, et correction des reprises grammaticales. SemantiK peut varier la réalisation grammaticalement quand son contrat l'autorise ; Spek n'improvise pas de variantes artistiques.
- Ne pas bricoler un champ JSON inconnu dans `CommunicationRequest/1.0` : documenter et adopter une extension normative **commune** (ou des requêtes bornées existantes quand elles suffisent), avec compatibilité et schémas.
- Contrôler que l'obligation voulue par le template ne devient pas une affirmation plus forte ou plus générale que la source.

**Recette :** les requêtes d'un passage couvrent les assertions admises, préservent leur modalité et reçoivent des contraintes linguistiques que le validateur et le RuntimeSet reconnaissent.

### P4 — Débloquer GF/PGF en commençant par une tranche verticale

**Dépendance : P3 pour le contrat ; équipe SemantiK/GF pour l'exécution. Chemin critique.**

- Détecter la chaîne GF, vérifier/compléter les sources `.gf`, compiler le `.pgf`, documenter GF/RGL, langues concrètes, hachages et licences.
- Publier un **petit profil français** d'abord : 8 à 12 réalisations pour la section « Sol » (noms et définitions, classification, propriétés, une énumération/élaboration, qualification) ; constituer le lexique agricole minimal.
- Vérifier que `has_definition` et les frames réellement employées ont un pont SA↔GF conforme ; ne pas traiter une définition littérale complète comme une grammaire par simple recopie opaque.
- Ajouter tests de couverture exacte, déterminisme, syntaxe française, accord, négation/nuance, source et non-omission ; produire preuves de conformité et un RuntimeSet `RELEASED` correspondant au profil utilisé.
- Étendre à 51 champs seulement après la preuve de bout en bout de la petite tranche ; refuser les champs non réalisables, pas de texte de secours.

**Recette :** `SemantiKArchitect.render()` rend réellement les phrases d'une section, le résultat est vérifié par l'adaptateur Spek et **aucune entrée `fixture` ne traverse la sortie vérifiée**.

### P5 — Rendu documentaire et contrôle de qualité de lecture

**Dépendance : P2 et P4.**

- Ajouter une représentation intermédiaire unique `ReaderDocument` avec sections, titres sémantiques, paragraphes, phrases, listes, comparaisons, notes de portée, citations publiques et emplacements de provenance privée.
- Produire HTML et Markdown depuis **le même IR** ; niveaux de titres accessibles et cohérents, pas de `<h2>` constant à chaque profondeur ; rendu mobile ; éviter les cartes répétitives et les « titre : définition » par défaut.
- Assembler des unités **complètes** ; absence de phrase de raccord → échec ou séparation volontaire selon contrat, jamais collage de fragments illégitimes.
- Installer des tests sur un corpus de lecture : répétition, pronoms ambigus, connecteurs trop nombreux, paragraphes trop courts, entrée hors portée, rupture de sujet, divergence HTML/Markdown ; revues linguistiques humaines indispensables.
- Garder l'aperçu privé, titres et descriptions non techniques ; rendre des **références bibliographiques lisibles** seulement quand elles sont autorisées, sans exposer IDs canoniques et hashes.

**Recette :** le même plan produit HTML/Markdown cohérents ; audit privé relie chaque phrase à ses obligations ; les lecteurs jugent le texte explicatif et non glossarial.

### P6 — Revue, attestation et publication séparée

**Dépendances : P1–P5. Responsable : Manager et autorités indépendantes.**

- Préparer un `PublicationCandidate` figé : commit/artifact hash, états sélectionnés, template lockfile, RuntimeSet, résultats, coverage, références et verdicts de revue.
- Confirmer les décisions éditoriales et la validité sémantique des liens ; rejeter les contradictions, surinterprétations, omissions de réserves et les contenus sensibles.
- Déléguer strictement les qualifications, reçus C1/C2/C3, contrôles C123, révocation et approbations aux parcours indépendants existants du Manager et du dépôt public.
- Générer Home, Sidebar et pages seulement après admissibilité ; effectuer un *dry-run* puis une décision de publication distincte ; **aucun push depuis `compose-preview` ou les lanceurs `.pyw`**.
- Vérifier pages Wiki, liens, navigation, rendu public, pagination/sections, et correspondance aux artefacts épinglés ; confirmer aussi le dépôt wiki activé avant d'annoncer la publication.

**Recette :** la publication est impossible sans décision vérifiée, preuve d'approbation et action distincte de l'opérateur ; les sorties privées ne peuvent être prises pour des pages publiques.

### P7 — Industrialiser, puis étendre aux autres Kristals

**Dépendance : Agriculture complet qualifié.**

- Mettre le parcours dans **un seul atelier Spek** : sélectionner Kristal et état → revoir la proposition IA → choisir les templates → vérifier couverture/runtime → réaliser → lire → faire réviser → remettre au Manager.
- Ergonomie Windows : `.pyw` avec erreurs affichées, CLI parallèles, aucun `.ps1` nécessaire, sans imposer aux utilisateurs de manipuler 51 fichiers JSON.
- Épingler la configuration par projet/édition ; tests régressifs et relecture des décisions après changement de source, template, lexique ou runtime.
- Répliquer par familles de Kristals avec preuves source, plans individuels et profils linguistiques compatibles ; ne pas traiter les 127 propositions initiales comme 127 plans approuvés.

**Recette :** l'interface accomplit le même parcours que la CLI, avec statuts réels et aucun bouton ne franchit une autorité extérieure.

## 5. Jalons de livraison conseillés (pas des promesses de calendrier)

| Jalon | Livrable utile | Critère bloquant |
| --- | --- | --- |
| M0 — Base reproductible | Versions/locks + tests + diagnostic | Le catalogue ne change pas silencieusement |
| M1 — Agriculture/Sol structuré | Sources admises, relations révisées, plan discursif + aperçu de structure | Chaque mouvement est ancré et adéquat |
| M2 — Agriculture/Sol **réel SemantiK** | 8–12 unités FR GF/PGF, résultat vérifié, lecture revue | 0 phrase fixture et profil RuntimeSet qualifié |
| M3 — Agriculture intégral privé | Six sections, interfaces, limites, fiches de couverture, rendu HTML/MD | Passage complet sans assertion ni relation inventée |
| M4 — Candidat Wiki | Revue et paquet de publication épinglé, admissibilité C1/C2/C3 | Verdicts indépendants, pas d'autorisation supposée |
| M5 — Déploiement autorisé | Pages Wiki après action distincte et validation de destination | Commit et pages publics conformes aux attestations |
| M6 — Généralisation | Pipeline et plans répétés sur d'autres Kristals | Aucune projection implicite ou approbation automatique |

**Chemin critique :** source admissible → relations justifiées → plan éditorial approuvé → requêtes sémantiques compatibles → RuntimeSet GF/PGF publié → réalisation réelle → revue → publication. Les enrichissements de CSS, du catalogue de 62 patterns et les formats PDF peuvent avancer en parallèle, mais ne débloquent pas ce chemin.

## 6. Priorités de conception : faire moins mais prouver davantage

- Ne **pas** développer de nouveau moteur de prose IA dans Spek.
- Ne **pas** sélectionner automatiquement « Toulmin » parce qu'il est dans le catalogue ; un argument demande thèse, preuves, garantie et réserves vraiment présentes.
- Ne **pas** assimiler un lien RST déclaré à une relation vraie ; RST formalise une intention discursive, pas une preuve scientifique.
- Ne **pas** imposer 51 phrases GF immédiatement ; la section « Sol » est le premier test de qualité et de contrat.
- Ne **pas** fusionner le pilote v6 et le contrôle source v11 sans projection explicitement versionnée.
- Ne **pas** appeler `verified` un texte source `fixture` ; séparer les statuts dans le code, les manifests et l'interface.
- Ne **pas** commencer par publier ; établir d'abord un article privé de référence et son audit.

## 7. Décision à adopter pour la mise à niveau

**Proposition :** figer l'interface vNext actuelle, ne conserver comme premier cas de travail que la section Agriculture « Sol », puis mettre en œuvre P0 → P1 → P2 et P3/P4 en tandem. P5 termine l'article, P6 gère la publication. Les 62 templates demeurent une bibliothèque de composition ; on les **curate** par cas d'usage au lieu de les exécuter arbitrairement.

**Définition de « Spek finalisé » pour ce pilote :** on peut sélectionner un état canonique, soumettre un plan de composition et ses relations à la bonne autorité, obtenir des phrases GF/PGF fidèles de SemantiK, les composer en article lisible HTML/Markdown, inspecter un audit complet, puis transmettre un candidat admissible au processus indépendant de publication. La publication effective reste un acte distinct.

## 8. Références utiles (sans prétention de certification)

- RST et relations noyau/satellite : https://www.sfu.ca/rst/01intro/definitions.html
- W3C PROV-O pour les idées de traçabilité entités/activités/agents : https://www.w3.org/TR/prov-o/
- W3C SHACL pour les validations de graphes RDF *si* les projections sont exposées comme RDF : https://www.w3.org/TR/shacl/
- GF/PGF : https://www.grammaticalframework.org/doc/gf-refman.html
- Dans les sources fournies : Architect `docs/04_COMMUNICATION_SEMANTICS_LOCK.md`, `docs/05_LANGUAGE_PLANNING_LOCK.md`, `docs/08_RUNTIME_ARTIFACT_LOCK.md` ; Manager `docs/09-securite/publication-et-separation-des-droits.md`, `docs/MANAGER_PUBLICATION_GITHUB_UI.md` ; Spek `docs/COMPOSITION_RECURSIVE_VNEXT/{11,14,15}*.md`.
