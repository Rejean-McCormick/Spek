# Spek.

**Structured knowledge. Reusable forms. Multilingual publications.**

**Version: 0.2.0 — Rendering & Semantic Fidelity** ([upgrade guide](docs/UPGRADE_0.2.md), [font configuration](docs/FONTS.md)).

Spek is a **local-first semantic publishing engine** that assembles readable scientific-style documents from **typed semantic units**, **short language realizations**, and **standardized editorial layouts**. One content model can be expressed in multiple languages without asking a language engine to improvise long paragraphs.

> **Spek is a publishing layer, not a source of scientific truth.** The included article is fictional/illustrative, and its French, English, and Italian sentences are manually supplied fixtures—not certified SemantiK output. Spek does **not** compute or authenticate Kristal v9 canonical commitments, certify GF/PGF RuntimeSets, grant publication approval, or activate Kristal states.

## Why Spek?

- **Spec**: a layout is an explicit, versioned contract specifying the kinds of information it requires.
- **Speak**: SemantiK or another reviewed realization provider supplies short language-specific expressions.
- **Speck**: a small, independently traceable presentation unit can be reused in larger articles.

**Crystallize the form; vary the content.** Spek makes information easier to scan and compare, while preserving evidence, scope, limitations, and provenance. Layouts communicate relationships between units, not merely their typography.

## What's included

| Area | Contents |
| --- | --- |
| Engine | Python module `spek`; CLI `spek` / `python -m spek` |
| Layout library | `result-card`, `argument-map`, `comparison` (JSON contract + dedicated HTML/TeX/PDF presentation) |
| Language support | FR, EN, IT strict parity; no automatic translation or silent fallback |
| Output | Static HTML, PDF, XeLaTeX source, per-language `document.json`, SHA-256 inventory (`manifest.json`) |
| Integrity | Typed slots, bounded cardinality, cross-references, epistemic labels, shared rendering model and source-reference checks |
| Integration | Explicit importer for the supplied historical SemantiK phrase prototype; never upgrades fixtures to qualified data |
| Operations | CI preview, manual fail-closed GitHub Pages workflow, local site verifier |
| Documentation | Detailed `/docs` plus a complete English GitHub wiki source in `/wiki` |

## Try it locally

Requirements: **Python 3.10+**. No external service is called while compiling. PDFs use ReportLab and installed Unicode TrueType fonts (`requirements.txt`); HTML and TeX can be generated with Python's standard library. Regression tests additionally use `pypdf`.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m spek check
python -m spek build --out dist --formats html,pdf,tex
python -m spek verify-site dist
python -m http.server 8000 --directory dist
# Open http://localhost:8000/
```

Or install the CLI locally: `python -m pip install -e .` and use `spek check`, `spek build`, etc. The CLI's default example paths target this source checkout; for work outside the checkout specify `--source`, `--realizations`, and `--layouts`.

For an actual article:

```bash
python -m spek check \
  --source my-article.json --realizations my-realizations.json --layouts layouts
python -m spek build \
  --source my-article.json --realizations my-realizations.json --layouts layouts \
  --languages en,fr,it --formats html,tex,pdf --out dist
```

**A successful demonstration build is not permission to publish.** Publication of real research requires reviewed, qualified source data and separate authorization.

## Architecture

```text
           Canonical Kristal knowledge (external authority)
                            |
            vetted, derived semantic projection
                            v
                  Article source JSON
                            |        reviewed short phrases
                            |       /    (SemantiK or other)
                            v      v
                   +--------------------+
                   |    Spek compiler   |<---- versioned layout library
                   | validate & compose |
                   +--------------------+
                            |
             SpekDocument (derived; per language)
                            |
          HTML / PDF / XeLaTeX / document.json
                            |
                  SHA-256 build manifest
                            |
                   local scientific QA
                            |
              independent publication approval
                            |
              manually gated GitHub Pages publish
```

The derived article source is **not a new canonical Kristal artifact**. Spek reads it and emits other derivatives; it does not write back to Kristal.

## The three layouts

| Layout ID | Required semantic roles | Main reading pattern |
| --- | --- | --- |
| `result-card` | claim, applicability, evidence, uncertainty | Main finding → proof/scope → limitation |
| `argument-map` | thesis, evidence-linked premises, inference, conclusion | Argument chain, with optional objection |
| `comparison` | topic, criterion, alternatives A/B, synthesis, limitation | Side-by-side methods or theories |

The `layouts/*.json` files hold **typed slot contracts**. The current prototype's renderers are explicit Python templates in `spek/render.py`; adding a wholly new layout requires updating the renderer as well as adding a JSON file. This is intentionally **not** a generic arbitrary-template interpreter yet. See [Layout design](docs/LAYOUT_DESIGN.md).

For v0.2 output parity, PDF font setup and existing output migration see [Upgrade guide](docs/UPGRADE_0.2.md) and [Fonts](docs/FONTS.md).

## GitHub wiki

The English wiki is checked into [`wiki/`](wiki/Home.md) for versioned review. GitHub stores its live wiki in a **separate repository** (`OWNER/Spek.wiki.git`), so it is **not** automatically created by pushing this main repository. See [Wiki publishing](docs/WIKI_PUBLISHING.md) and `scripts/sync-wiki.sh` for the controlled sync procedure.

## CI and public deployment

- `.github/workflows/quality.yml`: tests, checks, demonstration preview archive. **Never publishes.**
- `.github/workflows/publish.yml`: manual publish of an already locally compiled `published-site/` directory. Rejects demonstration artifacts and requires the protected environment `public-pages` and an environment-scoped `KRISTAL_PUBLICATION_GATE=authorized`. **Never recompiles, modifies canon, or activates a state.**
- `published-site/` is ignored locally by default; explicitly force-add only a reviewed public release payload after independent approval: `git add -f published-site/`.
- GitHub repository creation, Pages activation, external Kristal approvals, and initial wiki creation are **operator actions**; no remote account changes happen during a local build.

See [Release and deployment](docs/PUBLISHING.md), [Security](docs/SECURITY_MODEL.md), and [GitHub setup](docs/GITHUB_SETUP.md).

## Project map

```text
spek/                  validator, compiler and renderers
layouts/               typed, reusable layout definitions
examples/              illustrative semantic content + realization bundles
tests/                 automated test suite
docs/                  source-controlled engineering documentation
wiki/                  complete English GitHub wiki source (including Home and _Sidebar)
scripts/               safe wiki sync and repository setup assistance
.github/workflows/     offline CI previews and gated Pages workflow
```

## Project status

**Prototype 0.1 / experimental.** FR/EN/IT outputs and local tests are available. Real SemantiK RuntimeSet execution, JCS commitment verification, JATS/Crossref/DOI support, externally authenticated approval records, generalized layout rendering, and independent translation equivalence tests are **not implemented**. Do not infer those capabilities from the example.

See [Roadmap](docs/ROADMAP.md). Contributions are welcome via the proposed [contribution guide](CONTRIBUTING.md); **no copyright license is granted by this repository unless the rights holder explicitly adds a license** (see [License decision](LICENSE-DECISION.md)).
