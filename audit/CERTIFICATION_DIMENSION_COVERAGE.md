# Couverture des dimensions de certification

Contrat : `docs/superpowers/specs/2026-07-22-phase-0-1-collection-audit-design.md`

- Dimensions déclarées : `7`
- Dimensions réellement assignées par le gate : `3`
- `REQUIRED_DIMENSIONS_NOT_COVERED` : `4`
- `release-strict` satisfiable en l'état : `False`

Le contrat exige les sept dimensions `passed` pour `publication_eligible`.
Quatre n'ont aucun producteur : le gate ne peut pas passer aujourd'hui, et
il a raison de refuser — « une dimension non vérifiée reste explicitement
`not_covered`, jamais implicitement verte ».

| Dimension | Producteur | Preuve requise |
|---|---|---|
| `structure` | assignée par `_release_strict_gate` | — |
| `pedagogy` | assignée par `_release_strict_gate` | — |
| `regulation` | **aucun** — scripts/build_official_program_coverage.py (non branché sur la dimension) | Couverture des programmes officiels, année applicable |
| `mathematics` | **aucun** — scripts/audit_mathematical_correctness.py (inexistant) | Audit scientifique indépendant du contenu mathématique imprimé |
| `execution` | assignée par `_release_strict_gate` | — |
| `visual` | **aucun** — aucun (les QA raster existants sont partiels et par manuel) | Inspection ou mesure visuelle réelle des PDF rendus |
| `print` | **aucun** — scripts/build_final_preflight_and_regression.py (non branché sur le gate) | Preflight des PDF lié au HEAD de release |
