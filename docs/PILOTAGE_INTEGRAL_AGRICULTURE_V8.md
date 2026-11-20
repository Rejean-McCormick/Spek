# Agriculture v8 — orchestration complète sans nouveau moteur

**Statut : privé, non réalisé GF Agriculture, non approuvé, non publiable.** Overlay cumulatif v0.8.0a1, 20 novembre 2026; pilote WordBench natif ajouté. Les contrôles GF français ne prouvent pas l’exécution Agriculture. Ne pas confondre « code de pilotage installé » et « page finale produite ».

## Ce que le correctif fait déjà

- Conserve les 19/127/5 registres SPEK, les 27 layouts et les 62 templates récursifs **sans les modifier**.
- Conserve l'exécuteur GF récursif, le moteur HTML/Markdown et l'orchestrateur registre-first déjà testés sur Windows.
- Dépose la candidature sourcée Agriculture **dans `Documents\SPEK-PRIVE\Agriculture-v8`**, pas dans Git : pont `spek.registry-first-explicit-bridge/1.0` avec 96 références, audit détaillé par JSON Pointer et revue candidate.
- `doctor` contrôle le snapshot v8 et le registre actuel, fournit un diagnostic distinguant source, templates, slots, GF et publication.
- `preview` **délègue au `preview-structure` natif de SPEK** pour construire un HTML source, jamais GF, jamais publiable.
- `check` valide un futur pont éditorial complet et chaque paire assertion/JSON Pointer, puis délègue au précontrôle SPEK déjà installé ; `build` construit la collection via le moteur GF/HTML existant ; `package` via l'emballeur SPEK existant.

## Installation — un seul ZIP

Depuis le dossier extrait du nouveau ZIP :

```powershell
$spek='C:\mycode\Spek_Semantic-publishing\Spek'
py -3.12 .\INSTALLER_SPEK_INTEGRAL_v07.py --target $spek
py -3.12 .\INSTALLER_SPEK_INTEGRAL_v07.py --target $spek --install
```

L'installateur utilise une **simulation par défaut**, contrôle les SHA-256, refuse les modifications inconnues, et sauvegarde les anciennes documentations dans le dossier privé. L'installation ne fait **aucun commit, push, publication ou appel réseau**. Il ne dépose pas le snapshot de 391 assertions dans le dépôt SPEK.

## Première recette sur Windows

```powershell
$spek='C:\mycode\Spek_Semantic-publishing\Spek'
$ctl=Join-Path $spek 'scripts\piloter_agriculture_registres.py'

# Diagnostic source + registres + candidats + manques
py -3.12 $ctl --spek-root $spek doctor --report "$HOME\Downloads\diagnostic-spek-agriculture-$(Get-Date -Format yyyyMMdd-HHmmss).json"

# Page de structure produite par le moteur natif SPEK (NON GF)
$out="$HOME\Downloads\Agriculture-Structure-$(Get-Date -Format yyyyMMdd-HHmmss)"
py -3.12 $ctl --spek-root $spek preview --out $out
if (Test-Path "$out\inspection-structurelle.html") { Start-Process "$out\inspection-structurelle.html" }
```

Si `preview-structure` échoue, envoyer son journal et le diagnostic; ne pas inventer un HTML de remplacement ni un nouveau renderer.

## Ce qui manque encore pour la page finale GF, précisément

| Élément | Preuve disponible | Décision/artefact manquant |
|---|---|---|
| Source Agriculture | SHA brut v8 exact, 391 assertions | Examen indépendant de l'autorité actuelle de l'état si nécessaire |
| Sélection | 96 candidates cohérentes, 6 sections | Décision de retenir/écarter, revue de sources et relations |
| Layouts | Six contrats SPEK existants | Slot obligatoire `limits` (1 à 4), non alimenté par assertions qualifiées |
| GF | GF CLI opérationnel sur profil Konstellation FR | **Profil/RuntimeSet Agriculture réellement capable et qualifié**, requêtes SemantiK Agriculture, résultats vérifiés |
| Instances | Moteur récursif et HTML testés | Liaison des templates rhétoriques aux sections spécialisées, clés et couverture |
| Publication | Pipeline distinct documenté | C1/C2/C3/C4 + admission du Publisher + approbation du site exact |

**`validated` dans le snapshot v8 n'est pas l'approbation scientifique indépendante d'une page.** Le dossier candidat ne peut pas être converti automatiquement en affectation officielle : ne jamais modifier `kristal-assignments.json` sans décision documentée.

## Quand les véritables requêtes GF et un plan complet existent

```powershell
$binding='C:\chemin\prive\liaison-pleinement-revue.json'
$plan='C:\chemin\prive\plan-collection-gf.json'
$sa='C:\mycode\SemantiK_Architect\SemantiK_Architect'
$gf='C:\mycode\Grammatical-Framework\gf-3.12-windows\gf.exe'

py -3.12 $ctl --spek-root $spek check --binding $binding --plan $plan
py -3.12 $ctl --spek-root $spek build --binding $binding --plan $plan `
 --architect $sa --runtime-root "$sa\runtime" --gf-exe $gf `
 --out "$HOME\Downloads\SPEK-SITE-PRIVE-NOUVEAU"
py -3.12 $ctl --spek-root $spek package "$HOME\Downloads\SPEK-SITE-PRIVE-NOUVEAU" `
 --out "$HOME\Downloads\SPEK-SITE-PRIVE-NOUVEAU.zip"
```

Le précontrôle refusera un dossier encore `pending`, sans pages, sans requêtes, sans lock ou sans profil GF. C'est le résultat voulu. Les données publiques ne sont jamais fabriquées par ce pilote.

## Raccordement GF WordBench français (v0.7)

Le nouveau `doctor` exécute la commande native de contrôle WordBench Fre : intégrité de ses 15 scénarios déjà présents. **Cela ne lance pas GF, ne crée pas un runtime Agriculture et n’approuve aucun gold.** Exécuter `requirements --out <nouveau-fichier-privé.json>` pour émettre le cahier de correspondances des 96 assertions; leur opération SemantiK est volontairement `null`. Une véritable sonde française native WordBench (non Agriculture) est disponible via `probe-fre --scenario factual-present --out <nouveau-dossier-privé>`.

Voir `docs/RACCORDEMENT_GFWORDBENCH_AGRICULTURE.md` pour les chemins exacts. Le `build` du véritable article Agriculture reste conditionné à un runtime de domaine compatible et à l’admission éditoriale; cet overlay n’en invente pas.

## V0.8 : relai diK sans doublon

Le snapshot diK du 20 novembre a été inspecté. Ses opérations natives
`world gf-handoff` et `world semantik-knowledge` sont disponibles, mais
restent candidates. Le pont `scripts/pont_dik_semantik.py` exécute le test
lexical hors ligne sur la fixture diK, et prépare les besoins de références
sémantiques de nos 96 tâches (sans mapping). Voir `docs/RACCORDEMENT_DIK_AGRICULTURE.md`.
