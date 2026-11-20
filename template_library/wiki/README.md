<!-- SPEK_REGISTRY_FIRST_V050A1 -->
> **MISE À JOUR OBLIGATOIRE (19-11-2026)** : lire `docs/POINT_ENTREE_REGISTRES_SPEK.md`
> et `docs/CARTE_REPOS_ET_CHEMINS.md` AVANT toute construction d'article Kristal.
> Les 19 recettes Arketype, les 127 propositions par Kristal, les cinq revues
> structurelles et les 62 templates récursifs existent déjà. Le nouveau script
> `scripts/orchestrer_registre_spek.py` contrôle une liaison explicite entre les
> deux niveaux et délègue aux moteurs déjà installés. Ce document conserve
> aussi ci-dessous son contenu historique, qui peut être antérieur à ces acquis.
> **Aucune proposition n'est une assignation approuvée. Aucun aperçu n'est publiable.**

# Wiki SPEK — registres effectivement présents

- `composition-registry.json` : **19** recettes Arketype.
- `compositions/*.json` : détails des combinaisons de layouts et de sections.
- `kristal-ai-proposals.json` : **127** propositions individualisées.
- `kristal-structure-reviews.json` : **5** revues approfondies.
- `specialized-template-designs.json` + `layouts/` : **19** layouts typés spécialisés en complément des huit historiques.
- `kristal-assignments.json` : affectations approuvées **encore vides**.
- `template_library/rhetorical/templates/` : **62 templates rhétoriques**, format différent des recettes/layouts.

Le script `scripts/orchestrer_registre_spek.py` fournit le contrôle de liaison explicite entre ces niveaux; il ne remplit pas les assertions et ne publie pas.

---

## Historique conservé (potentiellement périmé)

# Wiki template library

Implemented category: 19 Arketype profiles in `archetype-profiles.json`, 19 AI-authored **candidate** compositions in `compositions/`, one `composition-registry.json` and an **empty** `kristal-assignments.json` awaiting the Manager report of 127 Kristals.

Spek does **not** infer the best template from a Kristal. It checks and displays only explicit editorial prescriptions. The existing eight reusable `layouts/` remain the execution contracts. Some recipes flag specialized layouts not yet implemented.

Use `python -m spek check-wiki-compositions` or `python -m spek list-wiki-compositions`. The `CATALOGUE_COMPOSITIONS_IA.html` file is a static visual catalog, **not** a generated Kristal wiki page.
