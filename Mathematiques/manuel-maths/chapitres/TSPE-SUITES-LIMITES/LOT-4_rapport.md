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

## Audit de reprise — 2026-08-05

50 exercices (parcours1:20, parcours2:15, parcours3:15) + 19 coups de pouce +
50 corriges, couverture C1-C7 complete. SymPy : 0 FAIL. Spot-check manuel
(EX-001/CO-001 et autres) : corrects, coherents avec l'enonce. R3 (anti-
similarite) non automatisable ici : pas de DB/pgvector configuree dans cet
environnement (cf. `terminale/collection-v1` ROADMAP) ; mode ex-nihilo deja
valide en LOT 1 rend ce check moins critique (sources_inspiration: [] partout,
pas de corpus externe reutilise). Statut : valide.
