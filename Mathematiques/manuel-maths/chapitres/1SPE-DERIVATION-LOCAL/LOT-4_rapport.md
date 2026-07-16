# LOT-4 — Exercices 1SPE-DERIVATION-LOCAL (rapport intermédiaire)

Date : 2026-07-15. Coût API estimé : ~8 $ (production exercices + corrigés).

## Matrice capacités × parcours

| | ◆ | ◆◆ | ◆◆◆ | Total |
|---|---|---|---|---|
| C1 Taux de variation | EX-001, EX-002 | EX-003, EX-004 | EX-005, EX-006 | 6 |
| C2 Nombre dérivé | EX-007, EX-008 | EX-009, EX-010 | EX-011, EX-012 | 6 |
| C3 Tangente | EX-013, EX-014 | EX-015, EX-016 | EX-017, EX-018 | 6 |
| C4 Équation tangente | EX-019, EX-020 | EX-021, EX-022 | EX-023, EX-024 | 6 |
| C5 Approximation | EX-025, EX-026 | EX-027, EX-028 | EX-029, EX-030 | 6 |
| **Total** | **10** | **10** | **10** | **30** |

Cases vides : **0**. Minimum F01 (≥2/case) : **rempli**.

## Ratio parcours

- ◆ : 10/30 = 33% (cible 40%)
- ◆◆ : 10/30 = 33% (cible 40%)
- ◆◆◆ : 10/30 = 33% (cible 20%)

Ratio à ajuster avec les 20 exercices supplémentaires (E5 : ≥50 total) : ajouter 8◆ + 8◆◆ + 4◆◆◆.

## Différenciation des parcours

- ◆ : exercices directs, calcul guidé, coups de pouce disponibles.
- ◆◆ : contextes réels (vitesse, coût, population, température, bénéfice), format bac à questions progressives.
- ◆◆◆ : conjecture + démonstration, recherche de paramètre, analyse d'erreur, problèmes ouverts.

## Gates

- Compilation : PASS pour les 30 exercices et 30 corrigés.
- SymPy : 30/30 verified.
- Figures dans les cours : 5 figures ajoutées (C1–C5).

## Complément EX-031→050 (16 juillet 2026)

20 exercices + 20 corrigés ajoutés : 8◆ + 8◆◆ + 4◆◆◆.

| | ◆ | ◆◆ | ◆◆◆ | Total |
|---|---|---|---|---|
| C1 | EX-031, EX-032 | EX-039, EX-040 | — | +4 |
| C2 | EX-033, EX-034 | EX-041, EX-042 | — | +4 |
| C3 | EX-035, EX-036 | EX-043 | — | +3 |
| C4 | EX-037 | EX-044 | — | +2 |
| C5 | EX-038 | EX-045, EX-046 | — | +3 |
| Multi | — | — | EX-047 (C1+C2+C4), EX-048 (C2+C3+C5), EX-049 (C1+C4+C5), EX-050 (C2+C3+C4) | +4 |
| **Sous-total** | **8** | **8** | **4** | **20** |

**Total chapitre : 50 exercices + 50 corrigés. Seuil E5 atteint.**

Ratio final : 18◆ (36%) + 18◆◆ (36%) + 14◆◆◆ (28%).

SymPy : **100/100 OK**.

## Matrice consolidée (50 exercices)

| | ◆ | ◆◆ | ◆◆◆ | Total |
|---|---|---|---|---|
| C1 | EX-001, EX-002, EX-031, EX-032 | EX-003, EX-004, EX-039, EX-040 | EX-005, EX-006 | 10 |
| C2 | EX-007, EX-008, EX-033, EX-034 | EX-009, EX-010, EX-041, EX-042 | EX-011, EX-012 | 10 |
| C3 | EX-013, EX-014, EX-035, EX-036 | EX-015, EX-016, EX-043 | EX-017, EX-018 | 9 |
| C4 | EX-019, EX-020, EX-037 | EX-021, EX-022, EX-044 | EX-023, EX-024 | 7 |
| C5 | EX-025, EX-026, EX-038 | EX-027, EX-028, EX-045, EX-046 | EX-029, EX-030 | 7 |
| Multi | — | — | EX-047 (C1+C2+C4), EX-048 (C2+C3+C5), EX-049 (C1+C4+C5), EX-050 (C2+C3+C4) | 4 |
| **Total** | **18** | **18** | **14** | **50** |

Cases vides : **0**. Minimum F01 (≥2/case) : **rempli** (C4◆ = 3 ≥ 2, C5◆ = 3 ≥ 2, etc.).

## Coups de pouce (CDP)

18 fichiers CDP créés pour tous les exercices ◆ :
- C1 : EX-001-CDP, EX-002-CDP, EX-031-CDP, EX-032-CDP
- C2 : EX-007-CDP, EX-008-CDP, EX-033-CDP, EX-034-CDP
- C3 : EX-013-CDP, EX-014-CDP, EX-035-CDP, EX-036-CDP
- C4 : EX-019-CDP, EX-020-CDP, EX-037-CDP
- C5 : EX-025-CDP, EX-026-CDP, EX-038-CDP

## Verdicts finaux

- SymPy : **100/100 OK** (50 exercices + 50 corrigés).
- `make verify` global (incluant LOT 5-7) : **143/143 OK**.
- Compilation : PASS.
- CDP : 18/18 (tous les ◆).
