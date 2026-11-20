<!-- SPEK_REGISTRY_FIRST_V050A1 -->
> **MISE À JOUR OBLIGATOIRE (19-11-2026)** : lire `docs/POINT_ENTREE_REGISTRES_SPEK.md`
> et `docs/CARTE_REPOS_ET_CHEMINS.md` AVANT toute construction d'article Kristal.
> Les 19 recettes Arketype, les 127 propositions par Kristal, les cinq revues
> structurelles et les 62 templates récursifs existent déjà. Le nouveau script
> `scripts/orchestrer_registre_spek.py` contrôle une liaison explicite entre les
> deux niveaux et délègue aux moteurs déjà installés. Ce document conserve
> aussi ci-dessous son contenu historique, qui peut être antérieur à ces acquis.
> **Aucune proposition n'est une assignation approuvée. Aucun aperçu n'est publiable.**

# SPEK — Agriculture / Sol : première page et chemin vers la réalisation réelle GF

Date de référence : 19 novembre 2026. **PILOTE PRIVÉ — NE PAS PUBLIER.**

## Ce qui a réellement été vérifié

- Le correctif cumulatif SPEK v0.3.0a2 est installé et 26 tests ont passé sur le Windows de l'opérateur.
- Le profil SemantiK `konstellation-fr-3` dispose d'un `grammar.pgf` contrôlé et a réellement produit « Augustin défend l’existence du libre arbitre. » via `gf.exe`.
- Cela **ne qualifie pas** les requêtes Agriculture. Le profil `konstellation-explorer-3` n'est pas un profil de réalisation agricole.
- Une archive de `kristal-public` disponible lors de l'analyse contient un graphe Agriculture v11.1 de **408 assertions**, révision candidate et non une preuve d'activation/publication. SHA-256 octet exact du fichier : `d35ac9409c2457b1bcc7e60a697e5b05863d52498cfae8d8a5a8aad8de325026`.
- Le précédent pilote éditorial Agriculture annonçait 25 assertions, 51 feuilles, et des textes `fixture` : ces textes ne sont pas des résultats GF. Le projet privé `pilotes_prives/agriculture-premier-document` n'est **pas** présent dans le dépôt public Spek, et sa présence sur Windows doit être inspectée.

## Deux sorties séparées (ne pas les confondre)

1. **Aperçu HTML source-littéral** : 18 extraits français reproduits exactement depuis une révision v11.1 candidate, regroupés selon un plan éditorial proposé ; HTML et Markdown vérifiables, `audit-prive.json` séparé. Ceci n'appelle **ni** les templates récursifs exécutables **ni** SemantiK/GF. Ne jamais étiqueter `GF_REALIZED`.
2. **Page SPEK/GF réelle** : exige une `spek.composition-instance/1.0` explicitement liée à de vraies assertions choisies, ses `CommunicationRequest`, un verrou `spek.private-editorial-handoff/1.0` vérifié, et un RuntimeSet **compatible Agriculture** ; les scripts v0.3.0a2 `realiser_composition_semantik.py` / `construire_pages_kristals.py` réalisent ensuite la page entière en HTML+Markdown. N'inventez ni autorisation, ni profil GF, ni requête.

## Générer / vérifier la première page SOURCE depuis une copie exacte du graphe

Si tu possèdes le dépôt `kristal-public` local vérifié, source attendue :

`kristals\agriculture\canon\domain\v11\updates\wikidata-2026-10-27-v11-1\semantic-graph.json`

Depuis SPEK, dans PowerShell :

```powershell
$script = '.\scripts\pilote_agriculture_sol.py'
$graph = 'C:\CHEMIN\kristal-public\kristals\agriculture\canon\domain\v11\updates\wikidata-2026-10-27-v11-1\semantic-graph.json'
$out = "$env:USERPROFILE\Downloads\AGRICULTURE_SOL_SOURCE_PRIVEE"
py -3.12 $script preview-sources --graph $graph --out $out --spek-root (Get-Location).Path
py -3.12 $script verify $out
Start-Process "$out\index.html"
```

Sortie **neuve**, hors de SPEK et des dépôts Git ; aucune écriture du canon. Une source d'une autre révision est **refusée**, et devra faire l'objet d'une nouvelle sélection et d'un nouveau verrou. Le ZIP de livraison joint contient une version déjà construite de cet aperçu, consultable sans GF.

## Inspecter les conditions de la véritable génération GF sur ton Windows

```powershell
$spek='C:\mycode\Spek_Semantic-publishing\Spek'
$sa='C:\mycode\SemantiK_Architect\SemantiK_Architect'
$gf='C:\mycode\Grammatical-Framework\gf-3.12-windows\gf.exe'
py -3.12 "$spek\scripts\pilote_agriculture_sol.py" doctor `
  --spek-root $spek --architect $sa --gf-exe $gf `
  --pilot-root "$spek\pilotes_prives\agriculture-premier-document"
```

Le rapport indique quels fichiers d'entrée du pilote existent et quels profils sont *activés*. Il n'affirme jamais qu'un profil activé pour Konstellation est compétent pour Agriculture.

## Faire produire une PAGE GF RÉELLE par SPEK (quand les entrées existent)

1. Examiner la **vraie** composition et les vrais `CommunicationRequest` de `pilotes_prives/agriculture-premier-document`, si ce projet a été déposé localement. Les numéros et chemins du pilote historique doivent être vérifiés, non supposés.
2. Définir/valider l'affectation explicite à Agriculture/Sol ; choisir les assertions et relations justifiées. La simple présence d'un ID dans le graphe ne vaut pas approbation.
3. Obtenir un RuntimeSet avec capacités et lexique couvrant ces demandes ; utiliser WordBench → SemantiK Conformance → SemantiK Runtime Orchestrator, **pas** un profil Konstellation substitué silencieusement.
4. Vérifier les sources et établir le verrou privé (`py -3.12 -m spek compose-lock ...`). Le verrou de SPEK est un contrôle d'intégrité, pas une approbation.
5. Définir le plan de collection en reprenant exactement `examples/PLAN_COLLECTION_PRIVEE.exemple.json`, mais avec les vrais chemins privés et le profil/runtime **vérifiés**. Pour une première page, ne conserver que l'entrée française de `agriculture-sol`.
6. Construire avec l'outil cumulatif existant (ne pas recopier de moteur) :

```powershell
py -3.12 scripts\construire_pages_kristals.py build `
  --plan C:\CHEMIN_PRIVE\plan-agriculture-sol.json `
  --spek-root C:\mycode\Spek_Semantic-publishing\Spek `
  --architect C:\mycode\SemantiK_Architect\SemantiK_Architect `
  --runtime-root C:\mycode\SemantiK_Architect\SemantiK_Architect\runtime `
  --gf-exe C:\mycode\Grammatical-Framework\gf-3.12-windows\gf.exe `
  --out "$env:USERPROFILE\Downloads\AGRICULTURE_SOL_GF_PRIVE"
```

7. Vérifier le site produit par `scripts\construire_pages_kristals.py verify`. L'outil conserve la mention « aperçu privé » et la publication reste interdite en attendant validation indépendante et raccordement Publisher.

## Critère de succès réel

**PAS** : un fichier `.pgf` existe. **PAS** : une fiche source HTML s'affiche. **OUI, lorsque démontré** : les feuilles de la composition Agriculture reçoivent toutes un véritable `CommunicationResult` complet, cohérent et fidèle avec RuntimeSet compatible, leurs rendus SPEK HTML+Markdown sont vérifiés, et la revue éditoriale confirme une page lisible. Cela ne constitue toujours pas la permission de publier.

## Référence aux templates existants

- `wiki.domain-primer-source-bound@1.0.0` : article de référence et sections imbriquées.
- `wiki.domain-section@1.0.0` : titre, définition focale et développements.
- `rhetorical.definition@1.0.0` : term / definition, pas de réécriture autonome.

Le présent paquet ne modifie aucun de ces contrats. Les 18 extraits ne forment pas à eux seuls un article scientifique rédigé.

## Démontrer IMMÉDIATEMENT la composition avec les vrais templates SPEK (sans prétendre faire du GF)

Le pack contient également `apercu_prive/SPEK_COMPOSITION_LITTERALE_NON_GF/instance.json` et `realizations-source-litterale-fr.json`. Ce sont une **véritable instance des templates SPEK existants** et ses 36 feuilles, dont **18 extraits source exacts** et **18 libellés éditoriaux proposés**. Les 36 valeurs sont marquées `status=fixture` ; elles ne viennent PAS de SemantiK. Les références `requests/*.json` sont volontairement des espaces réservés sans fichiers : `compose-lock` et le pipeline GF réel doivent refuser en l'absence de requêtes approuvées.

Depuis `C:\mycode\Spek_Semantic-publishing\Spek`, après extraction de ce ZIP, remplacer seulement le chemin `Downloads\...` par le dossier où le ZIP a été extrait :

```powershell
$source="C:\CHEMIN_EXTRACTION\apercu_prive\SPEK_COMPOSITION_LITTERALE_NON_GF"
$out="$env:USERPROFILE\Downloads\AGRICULTURE_SOL_SPEK_TEMPLATE_PRIVE"
py -3.12 -m spek compose-check --instance "$source\instance.json"
py -3.12 -m spek compose-preview `
  --instance "$source\instance.json" `
  --realizations "$source\realizations-source-litterale-fr.json" `
  --language fr `
  --title "Agriculture — Le sol (textes sources, non GF)" `
  --out $out
Start-Process "$out\index.html"
```

**Ne pas confondre :** la page HTML source-littérale fournie dans le ZIP est déjà produite par l'outil d'inspection. L'HTML créé par `compose-preview` sera, lui, le **vrai rendu du moteur récursif SPEK** mais avec les textes littéraux non-GF. Une troisième étape (plan éditorial approuvé + demandes SA + RuntimeSet Agriculture) produira la page GF réelle.
