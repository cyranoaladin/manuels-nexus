# Couverture des dimensions de certification

Contrat : `docs/superpowers/specs/2026-07-22-phase-0-1-collection-audit-design.md`

- Dimensions déclarées : `7`
- `REQUIRED_DIMENSION_PRODUCERS_MISSING` : `0`
- `REQUIRED_DIMENSIONS_FAILED` : `6` (structure, pedagogy, regulation, execution, visual, print)
- `REQUIRED_DIMENSIONS_PASSED` : `1` (mathematics)
- `ALL_REQUIRED_DIMENSIONS_STATUS` : `FAIL`

Le contrat exige les sept dimensions `passed` pour `publication_eligible`.
Quatre n'ont aucun producteur : le gate ne peut pas passer aujourd'hui, et
il a raison de refuser — « une dimension non vérifiée reste explicitement
`not_covered`, jamais implicitement verte ».

| Dimension | Producteur | Preuve requise |
|---|---|---|
| `structure` | assignée par `_release_strict_gate` | — |
| `pedagogy` | assignée par `_release_strict_gate` | — |
| `regulation` | `scripts/build_dimension_regulation.py` | statut `failed` |
| `mathematics` | `scripts/build_dimension_mathematics.py` | statut `passed` |
| `execution` | assignée par `_release_strict_gate` | — |
| `visual` | `scripts/build_dimension_visual.py` | statut `failed` |
| `print` | `scripts/build_dimension_print.py` | statut `failed` |
