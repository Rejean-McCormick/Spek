# SPEK — premier raccordement récursif à SemantiK/GF (correctif additif)

**État : pilote privé, non qualifié pour publication. Date : 19 novembre 2026.**

## Fait nouveau confirmé sur Windows

Le propriétaire a exécuté, avec `SEMANTIK_GF_EXECUTABLE` configuré, la commande officielle de SemantiK Architect `render` sur la requête `A001-core.json`, en utilisant le RuntimeSet `konstellation-fr-3`. Le moteur a retourné un `CommunicationResult/1.0` complet en `fr-CA`, avec texte « Augustin défend l’existence du libre arbitre. », couverture de l'obligation `o1`, source et identité déterministe.

Cette preuve valide **une réalisation française GF effective sur le poste de l'opérateur**, pas une page SPEK, un article Agriculture, les autres langues, la qualité linguistique générale ou les autorisations C1/C2/C3.

## Conception : aucune duplication de mécanisme

Le pilote ajoute `scripts/realiser_composition_semantik.py`, un **adaptateur d'exécution** pour une composition déjà assignée et verrouillée. Il réutilise :

- `spek.composition.commands.load` : expansion et validation du template récursif ;
- `spek.composition.editorial_lock.verify` : mêmes empreintes, sélection explicite et rattachements des requêtes que `compose-verify-lock` ;
- `spek.slot_dialogue.compose_request` : forme demandée à SemantiK, sans mutation des graphes ni des obligations ;
- `spek.semantik_execution._architect_root` et `_python_executable` : outil SemantiK officiel et interpréteur console ;
- `spek.composition.semantik_adapter.import_results` : vérification stricte de chaque paire requête/résultat, y compris la couverture, les sources et l'empreinte déterministe ;
- `spek.composition.commands.preview` : rendu HTML/Markdown **privé**, sans publication.

Le seul nouveau comportement est de lancer, pour chaque requête explicitement référencée par une feuille, `python -m semantik_architect.adapters.inbound.cli.main --runtime-root <root> render <request>`, en passant la variable d'environnement `SEMANTIK_GF_EXECUTABLE` à un chemin `gf.exe` explicitement fourni.

Le correctif n'ajoute aucune option au CLI `spek` historique, ne modifie pas le moteur récursif, les templates, les registres, les Kristals, les RuntimeSets ou le Publisher, et ne déclenche aucune écriture GitHub.

## Installation additive et réversible

Extraire le ZIP dans un répertoire temporaire, **pas** directement dans le dépôt SPEK. Puis :

```powershell
$pack = 'C:\Chemin\SPEK_CORRECTIF_GF_RECURSIF_2026-11-19'
$spek = 'C:\mycode\Spek_Semantic-publishing\Spek'

py -3.12 "$pack\INSTALLER_CORRECTIF.py" --target "$spek"            # Inspection seule
py -3.12 "$pack\INSTALLER_CORRECTIF.py" --target "$spek" --install  # Installation explicite
```

L'installateur refuse de remplacer un fichier déjà présent. Il copie quatre fichiers nouveaux, les contrôle par SHA-256 et ne touche pas à Git ni aux sources existantes. Pour revenir en arrière, supprimer **seulement ces quatre fichiers** après revue des modifications locales.

## Prérequis pour tester une composition réelle

1. Une instance `spek.composition-instance/1.0` existante avec des feuilles liées chacune à une `CommunicationRequest` explicite et unique ;
2. Un registre de requêtes privées dont les `source_refs` sont compatibles avec les `source_assertion_refs` de l'instance ;
3. Un verrou `spek.private-editorial-handoff/1.0`, créé via la **commande existante** `compose-lock` ;
4. Un vrai runtime compatible avec **la langue, le profil et chaque opération demandée**, indiqué dans chaque requête ;
5. Le `gf.exe` de l'opérateur ;
6. Un dossier de sortie privé **nouveau, hors de tout dépôt Git**.

Exemple de verrou (commande existante, dépend d'un vrai ensemble de requêtes/instances) :

```powershell
py -3.12 -m spek compose-lock `
  --instance 'C:\Prive\Edition\instance.json' `
  --library-root 'C:\mycode\Spek_Semantic-publishing\Spek' `
  --requests-dir 'C:\Prive\Edition\requests' `
  --language fr `
  --out 'C:\Prive\Edition\composition.lock.json'
```

Le contrôle d'existence des assertions dans un graphe v11 peut être ajouté à `compose-lock` et au pilote en fournissant explicitement le même `--source-graph` et, au besoin, `--identity-map`. Sans graphe, les références sources sont **liées entre l'instance et les requêtes, mais non certifiées canoniquement**.

## Première exécution réelle (quand les requêtes compatibles sont prêtes)

```powershell
$spek = 'C:\mycode\Spek_Semantic-publishing\Spek'
$sa = 'C:\mycode\SemantiK_Architect\SemantiK_Architect'
$gf = 'C:\mycode\Grammatical-Framework\gf-3.12-windows\gf.exe'

& "$spek\LANCER_REALISATION_RECURSIVE.cmd" `
  --instance 'C:\Prive\Edition\instance.json' `
  --requests-dir 'C:\Prive\Edition\requests' `
  --lock 'C:\Prive\Edition\composition.lock.json' `
  --architect $sa `
  --runtime-root "$sa\runtime" `
  --gf-exe $gf `
  --language fr `
  --runtime-id konstellation-fr-3 `
  --profile konstellation-explorer-3 `
  --out 'C:\Prive\Edition\aperçu-nouveau'
```

**Attention :** `konstellation-fr-3` est démontré pour une requête Konstellation. Il n'est pas automatiquement compatible avec Agriculture/Sol. Un profil/lexique/ensemble d'opérations Agriculture qualifié sera nécessaire pour cette première publication scientifique.

Le test `A001-core.json` fournit la preuve que GF peut produire une phrase, mais **il ne constitue pas, à lui seul, une instance SPEK verrouillée**. Sa référence source contient des caractères qui peuvent être incompatibles avec les règles actuelles des bindings éditoriaux SPEK ; ne pas contourner ces règles ou fabriquer des assertions pour forcer le test.

## Comportement et sécurité

- Le programme vérifie le verrou **avant** de lancer un sous-processus ; seules les requêtes déclarées dans le template sont utilisées.
- Chaque requête doit épingler `runtime_selector.runtime_set_id` et `capability_profile`. Pas de sélection silencieuse d'un autre RuntimeSet.
- Chaque exécution utilise le CLI officiel `render`, une instance GF configurée explicitement et un temps maximal borné.
- Toute erreur d'exécution, de schéma, de couverture, de provenance ou de changement de version provoque un **refus** et ne produit aucun aperçu final.
- Les requêtes et résultats transitoires sont isolés dans un dossier temporaire privé sous la racine choisie, puis supprimés. Les sorties finales contiennent uniquement `index.html` et `Brouillon-prive.md`.
- Le programme n'établit pas la justesse scientifique de la source, ne confirme pas la qualité des relations rhétoriques déclarées et ne crée aucune autorisation de publication.

## Validation de la livraison

```powershell
py -3.12 -m unittest discover -s tests -p test_realiser_composition_semantik.py -v
```

Les tests du pack emploient des **subprocessus simulés** pour vérifier la mise en forme des appels, la transmission de `SEMANTIK_GF_EXECUTABLE`, le refus d'un RuntimeSet différent, l'absence de sortie partielle et le respect des dossiers privés. Ils **ne prétendent pas reproduire ton exécution GF réelle**. Le test d'intégration complet attend une vraie instance éditoriale, ses requêtes et son verrou.

## Limites du correctif

- Pas de sélection automatique de faits, de règles rhétoriques ni de template ; ces décisions sont prises et vérifiées en amont.
- Pas d'automatisation des 127 propositions (les assignations approuvées restent vides dans SPEK), ni du corpus multilingue complet.
- Pas de vérification exhaustive de la qualification d'un RuntimeSet par ce script ; utiliser `semantik-runtime-orchestrator inspect-profile` et l'exécution `render` officielle.
- Pas de déploiement, GitHub Wiki, GitHub Pages ou publication ; barrières C1/C2/C3 toujours externes.
- Aucun test effectué sur le clone local Windows : valider les versions, l'installateur et le scénario réel sur le poste propriétaire avant toute intégration stable.
