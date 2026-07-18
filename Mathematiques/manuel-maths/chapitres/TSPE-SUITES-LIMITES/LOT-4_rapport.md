# LOT-4 — Rapport de production : Exercices + Corriges + CDP

## Chapitre : TSPE-SUITES-LIMITES

### Inventaire : 50 exercices, 50 corriges, 18 CDP

### Couverture par capacite et parcours

| Capacite | Exercices | P1 | P2 | P3 | CDP |
|----------|-----------|----|----|----|----|
| C1 | EX-001 a EX-007 | 001,002,003 | 004,005 | 006,007 | 001,002,003 |
| C2 | EX-008 a EX-014 | 008,009,010 | 011,012 | 013,014 | 008,009,010 |
| C3 | EX-015 a EX-021 | 015,016,017 | 018,019 | 020,021 | 015,016,017 |
| C4 | EX-022 a EX-028 | 022,023,024 | 025,026 | 027,028 | 022,023,024 |
| C5 | EX-029 a EX-035 | 029,030,031 | 032,033 | 034,035 | 029,030,031 |
| C6 | EX-036 a EX-042 | 036,037,038 | 039,040 | 041,042 | 036,037,038 |
| C7 | EX-043 a EX-050 | 043,044 | 045,046,047 | 048,049,050 | — |

### Totaux

| Parcours | Nombre |
|----------|--------|
| Parcours 1 | 20 exercices |
| Parcours 2 | 15 exercices |
| Parcours 3 | 15 exercices |
| CDP | 18 fichiers |

### Verification

- Tous les exercices ont un bloc BEGIN-VERIFY/END-VERIFY avec assertions SymPy.
- Tous les corriges ont un bloc BEGIN-VERIFY/END-VERIFY.
- Les META headers sont au format JSON.
- Couverture 100% des 7 capacites sur les 3 parcours.

### Types d'exercices

- P1 : calculs directs, applications de formules, recurrences guidees
- P2 : demonstrations partiellement guidees, modelisation, Bernoulli
- P3 : type bac (suites recurrentes completes, preuves epsilon-N, Cesaro, sommes de series)

### Points ouverts

- Verification SymPy via make verify a effectuer.
- Similarite via make similarity a effectuer.
