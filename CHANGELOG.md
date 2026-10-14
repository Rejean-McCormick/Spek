# Changelog

## 0.5.0 — Educational publishing, independent Ekole/Kompose adapters

- Five additional typed layouts (eight total), localized in FR/EN/IT and rendered in HTML, PDF and LaTeX.
- `spek.educational-projection/1` curated input contract, `import-educational --adapter ekole|kompose` and independently verifiable local builds.
- Fail-closed rejection of teacher/session/PII fields, unknown metadata, unreferenced phrase payloads, private evidence locations and session-restricted Kompose content.
- No public release/teacher grade/clinical inference or educational authority conferred by the export. All educational imports remain local preview projections and cannot pass Spek's production gate.
- A fictitious Ekole school-garden example across five layouts and a separate Kompose public-excerpt example, neither an actual upstream deployment.
- Windows-friendly `.bat` demo script, fixed the PowerShell bridge demo's comma argument issue, tests and English wiki additions.


## 0.4.0 — Autonomous interoperability and language-channel separation

- Spek is a standalone compiler; external connectors are optional.
- `bridge-import --adapter konstellation|exchange` converts explicitly mapped, scoped export payloads to derived Spek article sources.
- `bridge-fetch-konstellation` adds opt-in read-only `/api/query` capture with environment-sourced bearer token and redirect blocking.
- `import-ai` ingests preconstructed AI text without calling SemantiK; provenance channel, model, generation and review status are distinct from GF runtime qualification.
- Structured Source Explorer offers source-system references and an operator-configured outbound deep link.
- Synthetic Konstellation `ResultSet 0.2` and generic exchange fixtures; regression tests for scope, integrity, non-escalation and linguistic provenance.
- Full English connector and language-channel docs and Wiki pages.
- External source projections are never canonically verified or auto-authorized for production.

## 0.3.0 — Source Explorer

- Added a native, accessible **Explore source** toggle to every HTML card, in French, English, and Italian.
- Displayed typed semantic references, qualifications, provenance, realization provider/status and evidence links as structured records, not inline raw metadata or JSON.
- Added surface-word tables, validated optional per-word annotations and an explicit distinction between user-supplied linguistic properties and unanalysed surface text.
- Extended the shared `SpekDocument` projection to `spek.document/0.3` with explicit word annotations and evidence details; PDF and TeX semantic trace rendering is unchanged.
- Added 9 source-explorer regression tests. Demonstration word annotations remain unqualified manual fixtures.
- No automatic GitHub publication, external state activation, SemantiK certification, or language translation.

# Changelog

## 0.2.0 — Rendering and semantic fidelity

- Added a versioned, derived `SpekDocument` projection used by HTML, PDF, LaTeX and `document.json`.
- Preserved all semantic IDs, status, evidence links and locators in the renderers.
- Prevented orphaned PDF trace blocks and corrected the French demo's third blank-like page.
- Added installed Unicode font discovery and fail-closed glyph checks on Windows/Linux.
- Localized provenance metadata and linked language pages to PDF, LaTeX and JSON exports.
- Grouped evidence, fixed repeated comparison criterion labels, and expanded regression testing.
- Kept v0.1 source/layout contracts and publishing protections unchanged.


## 0.1.0 — Initial Spek repository candidate

- Named the local publishing prototype **Spek** (spec / speak / speck).
- Kept the validated Kristal editorial input format identifiers at `0.1` for compatibility.
- Included three layouts and trilingual demonstration outputs.
- Added a versioned English wiki, integration notes, local Git instructions, and guarded publishing workflows.
- Explicitly documented missing upstream qualifications and authorization boundaries.
