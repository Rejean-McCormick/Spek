# SPEK v0.7 — raccordement GF WordBench natif pour Agriculture

**20 novembre 2026 — privé et non publiable.** Ce document réunit le véritable contenu WordBench fourni et l'overlay SPEK v0.6 installé sur Windows. Il ne réécrit ni GF, ni WordBench, ni SemantiK Architect, ni les templates SPEK.

## Dépôts connus

| Outil | Chemin réel Windows | Contrat |
|---|---|---|
| SPEK | `C:\mycode\Spek_Semantic-publishing\Spek` | Source de vérité des 6 layouts Agriculture et de la composition récursive |
| Agriculture v8 | `C:\mycode\Kristal\locals\Kristal-Agriculture\.kristal\v8\portable-state.kristal-state.json` | 391 assertions, SHA exact `ae3cf84ab47a1ea3c710785f5749c7cacd8274d389f767958c7327c6c1a72918` |
| GF WordBench | `C:\mycode\Grammatical-Framework\GF_Wordbench` | `src/gf_wordbench/practical/pilot.py`, pilote **Fre** avec 15 `.gfs` et hashes |
| GF RGL | `C:\mycode\Grammatical-Framework\gf-rgl` | Sources françaises `src/french/`, chemins RGL à fournir au processus WordBench |
| GF CLI | `C:\mycode\Grammatical-Framework\gf-3.12-windows\gf.exe` | Véritable compilateur, pas un profil |
| SemantiK Architect | `C:\mycode\SemantiK_Architect\SemantiK_Architect` | Seule autorité de création/validation des `CommunicationRequest` |

## Pourquoi la chaîne n'est pas encore complète

WordBench prévoit 15 capacités françaises : `factual-present`, `past-event`, `past-state`, `future-reference`, `factual-negation`, `temporal-order`, `condition-real`, `possibility`, `source-attribution`, `quantity`, `location`, `instruction`, `prohibition`, `obligation`, `conditional-instruction`. La commande native `check` vérifie les scripts et hashes, **sans GF**. Le snapshot inspecté indique `gold_approved: false`, `lexical_status: provisional_unreviewed`. Même une sonde GF française réussie n'est **pas** un RuntimeSet Agriculture.

La source Agriculture possède des prédicats spécifiques (`agriculture.has_definition`, `agriculture.can_limit`, `agriculture.connects_stage`, etc.). Le mapping prédicat → opération SemantiK → lexique/constructeur GF et le runtime compatible ne sont pas fournis. Les 6 slots `limits` demeurent incomplètement qualifiés. Aucun mot de domaine ne doit être injecté silencieusement dans des phrases comme « est lié à » pour prétendre couvrir le corpus.

## Une seule entrée SPEK

```powershell
$spek = 'C:\mycode\Spek_Semantic-publishing\Spek'
$ctl = "$spek\scripts\piloter_agriculture_registres.py"

# Diagnostic source/registres + précontrôle natif WordBench Fre, sans exécution GF ni écriture WordBench
py -3.12 $ctl --spek-root $spek doctor

# Production privée d'un cahier de 96 exigences GF exactes, sans mapping inventé
$out = "$HOME\Documents\SPEK-PRIVE\Agriculture-v8\exigences-gf-$(Get-Date -Format yyyyMMdd-HHmmss).json"
py -3.12 $ctl --spek-root $spek requirements --out $out

# OPTIONNEL : véritable sonde GF native WordBench pour UNE capacité Defluens Fre,
# preuve technique du banc français, non preuve Agriculture
$probe = "$HOME\Documents\SPEK-PRIVE\Agriculture-v8\sonde-wb-fre-$(Get-Date -Format yyyyMMdd-HHmmss)"
py -3.12 $ctl --spek-root $spek probe-fre --scenario factual-present --out $probe
```

`doctor` appelle **le propre** `python -m gf_wordbench.practical.pilot check --language Fre` de WordBench avec `PYTHONPATH` ciblé. `probe-fre` appelle **son propre** `run` avec GF réel et RGL. Ces actions n'écrivent ni dans SPEK, ni dans WordBench, ni dans RGL, ni dans SemantiK Architect. `requirements` crée un seul nouveau JSON dans un dossier privé ; il refuse un nom de fichier déjà utilisé.

Les 96 tâches sont groupées par les six sections/layers déjà audités. Chaque tâche porte un `assertion_id`, un JSON Pointer, un slot, un prédicat, un sujet/objet et les preuves : `semantik_operation`, `communication_request`, `lexical_bindings`, `gf_expression` sont **null**, à remplir seulement après définition et validation indépendante. Aucune modification n'est faite au registre source et la publication reste interdite.

## Pour l'étape suivante

Le résultat WordBench Fre déterminera si la base grammaticale est techniquement opérationnelle. **L'étape de développement indispensable**, distincte de cette sonde, est la définition d'une grammaire/profil de domaine Agriculture dans le flux officiel SemantiK (puis compilation, conformance, linguistique, instantiation SPEK et Publisher). Ne pas recopier le pilote Defluens dans SPEK et ne pas convertir les golds non approuvés en certificat.

## Fichiers inspectés du snapshot complet WordBench

- `src/gf_wordbench/practical/pilot.py` : `check` vérifie les scénarios `.gfs` et les SHA-256, `run` exécute le vrai GF via `prepare_and_execute_scenario` et produit des **candidats** ; c'est l'interface réellement appelée par SPEK v0.7.
- `pilots/practical_generation_v1/Fre/pilot_manifest.json` : 15 scénarios et 15 sources/modules associés, `gold_approved: false` et `lexical_status: provisional_unreviewed` dans le snapshot du 20 novembre.
- `src/gf_wordbench/practical/semantik_handoff.py` : export expérimental Defluens pour 14 langues; beaucoup de correspondances SA réclament une extension ou une preuve de fonctionnalité. **Ce n'est pas** un pont de domaine Agriculture.
- `src/gf_wordbench/validation/semantik_handoff/service.py` : contrôle d'un paquet de candidats Phrase Ops vers WordBench, pas une certification linguistique.
- `tools/build_semantik_profile3_candidate.py` : compile des profils SA existants (Konstellation, attributs, Defluens Core), **aucun profil Agriculture n'y figure dans le snapshot**. Ne pas l'utiliser comme générateur générique agricole.
- `docs/gf/GF_PGF_BUILD.md` : la construction d'un PGF exige un artefact et une identité de build courants ; un fichier ancien ne vaut pas preuve de release.

Ces constats sont **tirés du snapshot WordBench reçu**. Elles ne prouvent pas que des changements non transmis sont absents sur le disque Windows. Un résultat GF Fre doit être conservé dans le répertoire privé de son run et revu; il n'active aucun profil Architect et ne satisfait aucun verrou SPEK par lui-même.
