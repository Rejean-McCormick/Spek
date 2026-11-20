# SPEK → diK → SemantiK Architect : chaîne lexicale vérifiée, non activée

**20 novembre 2026 — référence cumulative v0.8.**

## Recherche effectuée sans demander de nouveau les dépôts

Le ZIP `znapshot_diK_11201331.zip` contient le vrai code diK et ses tests.
Le pont native `src/dik/gf_handoff.py` convertit des observations Wikidata
L/S/F vérifiées en candidats de mapping français `gf_function: null`.
Le pont `src/dik/semantik_handoff.py` produit ensuite
`semantik.knowledge.json` compatible avec le schéma lexical SA 1.1 et
`gf-mapping-review.template.json`, avec `use_for: knowledge` et aucune
correspondance approuvée. **Cela ne suffit pas à générer une phrase.**

La même chaîne de six opérations a été exécutée par l'assistant sur
l'échantillon natif de diK : 2 lexèmes, 2 entrées knowledge,
0 fonctions GF, 0 correspondances Kristal acceptées. Test pertinent du
logiciel, **pas un test linguistique Agriculture**, ni un test chez l'utilisateur.

## Actions réellement exécutables sur Windows (PowerShell 5.1 ou 7)

```powershell
$spek = 'C:\mycode\Spek_Semantic-publishing\Spek'
$ctl = "$spek\scripts\piloter_agriculture_registres.py"

# Recherche sans écriture; examine diK + WordBench + source v8 + SPEK
py -3.12 $ctl --spek-root $spek doctor

# Exécute les 6 vraies commandes diK, uniquement sur SON échantillon local.
# Aucune mutation des dépôts. Chemin diK deviné par sa documentation,
# remplaçable par --dik-root si l'organisation locale est différente.
py -3.12 $ctl --spek-root $spek probe-dik

# Extrait les identités de concepts des 96 tâches Agriculture vérifiées.
# Sortie privée, aucune liaison lexicale automatique.
$out = "$HOME\Documents\SPEK-PRIVE\Agriculture-v8\besoins-lexicaux-$(Get-Date -Format yyyyMMdd-HHmmss).json"
py -3.12 $ctl --spek-root $spek lexical-needs --out $out
```

## Contrat de sécurité des identités

Les IDs `wikidata:lexeme:L...` ne sont pas des identités Kristal KQ/KP/KA.
Une correspondance basée seulement sur le mot « sol », `soil`, `crop` ou
son équivalent dans une autre langue est insuffisante.
La validation sémantique et les sens doivent être revus; GF WordBench
valide grammaire/morphologie; SemantiK Architect lie des fonctions GF et
le RuntimeSet; SPEK assemble une page sur des résultats réels;
Publisher décide indépendamment de la diffusion.

## Ce qui ne peut pas être déclaré terminé

Ni l'échantillon diK ni le pilote Defluens Fre de WordBench ne prouvent
un lexique Agriculture complet, un RuntimeSet Agriculture ou les 6 slots
`limits` approuvés. Le registre Agriculture est candidat. Les 96 tâches
contiennent 55 définitions et 41 autres relations/éléments de contenu :
une sélection éditoriale finale reste nécessaire, surtout pour éviter
une page réduite à un glossaire.

Ce patch n'écrit jamais dans diK, WordBench, RGL, SemantiK Architect,
Kristal, ni Publisher.

## Inventaire déjà livré dans le dossier privé

Le fichier `besoins-lexicaux-agriculture-v8-CANDIDAT.json` dérive des
96 assertions candidates auditées : **58 références sémantiques de sujet/objet**
avec liens `assertion_id` et JSON Pointer, et **19 prédicats**. Il reste en
`CANDIDATE_ONLY_NOT_MAPPED`; aucune entrée ne contient une identité diK
ou une expression GF devinée. Il est installé automatiquement hors Git,
sans commande `lexical-needs` obligatoire.
