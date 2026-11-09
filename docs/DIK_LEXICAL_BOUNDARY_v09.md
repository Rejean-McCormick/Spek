# Spek and diK: keep the lexical/publication boundary intact

Spek does **not** ingest diK dictionaries as document text, invent semantic
identity, compile GF functions or turn candidate lexical artifacts into
`kristal.layout-realizations/0.1` records.

New diagnostic only:

```powershell
cd C:\mycode\Spek_Semantic-publishing\Spek
python -m spek.cli inspect-lexical-dependency --bundle C:\lex-data\wordbench-fr
```

This confirms SHA-256, provenance, source schema and candidate status, but
returns `realizations_imported=0` and `publication_eligible=false`. To compose
actual documents, continue using the existing **paired** SemantiK
`CommunicationRequest`/`CommunicationResult` importer, whose obligation and
runtime-identity checks are not weakened.

Owner split: diK lexical sources; WordBench GF mapping/build; SemantiK
realization; Spek rhetorical composition and layouts; Defluens local control.
