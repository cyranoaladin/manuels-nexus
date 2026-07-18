# LOT-4 — Rapport de production : Exercices + Corriges + CDP

## Chapitre : TSPE-LIMITES-FONCTIONS

### Inventaire : 50 exercices, 50 corriges, 14 CDP

### Couverture par capacite et parcours

| Capacite | Exercices | P1 | P2 | P3 | CDP |
|----------|-----------|----|----|----|----|
| C1 | EX-001 a EX-020 | 001-008 (8) | 009-014 (6) | 015-020 (6) | 001-007 |
| C2 | EX-021 a EX-035 | 021-027 (7) | 028-031 (4) | 032-035 (4) | 021-024 |
| C3 | EX-036 a EX-050 | 036-041 (6) | 042-045 (4) | 046-050 (5) | 036-038 |

### Totaux

| Parcours | Nombre |
|----------|--------|
| Parcours 1 | 21 exercices (~42%) |
| Parcours 2 | 14 exercices (~28%) |
| Parcours 3 | 15 exercices (~30%) |
| CDP | 14 fichiers (tous en P1) |

### Verification

- Tous les exercices ont un bloc BEGIN-VERIFY/END-VERIFY avec assertions SymPy.
- Tous les corriges ont un bloc BEGIN-VERIFY/END-VERIFY.
- Les META headers incluent fichier_tex et corrige_tex.
- Couverture 100% des 3 capacites sur les 3 parcours.

### Types d'exercices

- P1 : calculs directs de limites, limites usuelles, operations, compositions
- P2 : formes indeterminees, etudes partielles, asymptotes avec exp
- P3 : type bac (etudes completes de fonctions, demonstrations, modelisation)

### Points ouverts

- Verification SymPy via make verify a effectuer.
- Similarite via make similarity a effectuer.
