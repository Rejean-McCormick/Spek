# Carte stable des dépôts utiles à SPEK — état au 20 novembre 2026

| Projet | Chemin local Windows | Confirmation |
|---|---|---|
| SPEK | `C:\mycode\Spek_Semantic-publishing\Spek` | Utilisateur, 26 tests cumulés et 17 tests registre passés |
| Kristal Agriculture v8 | `C:\mycode\Kristal\locals\Kristal-Agriculture\.kristal\v8\portable-state.kristal-state.json` | **Utilisateur : SHA-256 exact confirmé 2 fois** ; source de 391 assertions communiquée |
| SemantiK Architect | `C:\mycode\SemantiK_Architect\SemantiK_Architect` | GF réel exécuté avec ce dépôt pour Konstellation FR |
| GF CLI | `C:\mycode\Grammatical-Framework\gf-3.12-windows\gf.exe` | GF réel Konstellation FR exécuté |
| SemantiK Runtime Orchestrator | `C:\mycode\SemantiK_Architect\SemantiK_Runtime_Orchestrator` | Chemin rapporté ; profils Konstellation inspectés, statut de publication non acquis |
| Konstellation | `C:\mycode\Konstellation\Konstellation` | Prompt PowerShell confirmé ; ne pas toucher ici |
| Kristal-Manager | **À déterminer seulement si action Manager nécessaire** | Amont des liaisons/qualification |
| Arketype | Chemin local non nécessaire à ce pilote | Ses 19 recettes sont déjà versionnées dans SPEK |
| Publisher / EncyK Publication Orchestrator | **Chemin local non confirmé** | Admission et publication séparées |
| **GF WordBench** | `C:\mycode\Grammatical-Framework\GF_Wordbench` | Racine confirmée par index + snapshot complet; pilote natif Fre 15 scénarios, gold non approuvé |
| **GF RGL** | `C:\mycode\Grammatical-Framework\gf-rgl` | Index local fourni, sources françaises sous `src/french/` ; pas un profil Agriculture |
| GF Audit | Chemin local non confirmé | Ne pas deviner ; outil distinct |

Les dépôts GitHub de lecture utilisés précédemment incluent `Rejean-McCormick/Spek` et `Rejean-McCormick/kristal-public`. Ils ne donnent **pas** d'accès aux fichiers Windows de l'utilisateur. Ne pas deviner les chemins manquants, et ne pas transférer des données canon ou privées dans des dépôts publics.

## Anti-redécouverte

La recherche des registres est terminée. Lire `AGENTS.md`, `docs/POINT_ENTREE_REGISTRES_SPEK.md`, puis la proposition `proposals.agriculture` et la revue `reviews.agriculture`. Le nouveau pilote `scripts/piloter_agriculture_registres.py doctor` vérifie le même inventaire. **Ne pas confondre source v8 et graphe v11.1, ni interpréter un `validated` du fichier comme approbation de publication.**

## Contrôle GF officiel depuis SPEK v0.7

`py -3.12 scripts\piloter_agriculture_registres.py doctor` délègue le précontrôle des 15 scénarios Fre à `python -m gf_wordbench.practical.pilot check --language Fre` via `PYTHONPATH` explicite et sans écrire dans WordBench. Voir `docs/RACCORDEMENT_GFWORDBENCH_AGRICULTURE.md`. Aucune exécution GF réelle Agriculture n'est démontrée par ce contrôle.

## diK (snapshot de code inspecté le 20 novembre 2026)

- **diK** : documentation interne : `C:\mycode\diK\diK`, chemin local **non confirmé** ;
  détectable via `--dik-root` sans question préalable si le dossier existe.
- Contrat lexical réel : `src/dik/gf_handoff.py`, `src/dik/semantik_handoff.py`,
  `docs/docs/30_SEMANTIK_GF_HANDOFF_V09.md` ; `use_for=knowledge`, pas de RuntimeSet.
- **GF WordBench** est responsable des sondes/compilations, pas diK.
- **SemantiK Architect** décide explicitement de l'opération et du lexique de réalisation.
- SPEK ne revendique aucune identité lexicale approuvée à partir d'une similarité de mot.
