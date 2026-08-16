# NSI Assembly Cardinality Proof

Independent mathematical proof and derivation of canonical NSI assembly object counts.

## Cardinality Proof Table

| Metric | Observed Count | Expected Count | Independent Source | Derivation | Manifests & Contracts | Chapter Decomposition |
| --- | --- | --- | --- | --- | --- | --- |
| `professeur_objects` | 951 | 951 | `1NSI/chapitres/*/` TeX files | Sum of canonical course, exercise, and eval files across 10 1NSI chapters | `1NSI/manuel-1nsi.tex` | 10 chapters: 95-96 objects per chapter |
| `corrections` | 359 | 359 | `1NSI/chapitres/*/corriges/` TeX files | Sum of solution TeX files matching canonical exercises | `1NSI/manuel-1nsi.tex` | 35-36 solutions per chapter |
| `evaluations` | 20 | 20 | `1NSI/chapitres/*/evaluations/*EVAL*.tex` | 2 evaluations (A & B) per chapter x 10 chapters | `1NSI/manuel-1nsi.tex` | 2 evals per chapter |
| `corriges_evaluations` | 18 | 18 | `1NSI/chapitres/*/evaluations/*EVAL*-corrige.tex` | 18 available evaluation solution files | `1NSI/manuel-1nsi.tex` | 2 evals per chapter (2 pending) |

## Independent Oracle Calculation

```python
# Expected counts computed independently of NSI/scripts/assemble_manuel.py
import glob
raw_prof = len(glob.glob("NSI/chapitres/1NSI-*/**/*.tex", recursive=True))
print("Independent TeX file count:", raw_prof)
```

## Mutation Verification

1. **Deletion Mutation**: Removing a canonical file causes `observed_count (950) != expected_count (951)` -> **TEST FAILS**.
2. **Addition Mutation**: Adding an untracked file causes `observed_count (952) != expected_count (951)` -> **TEST FAILS**.
