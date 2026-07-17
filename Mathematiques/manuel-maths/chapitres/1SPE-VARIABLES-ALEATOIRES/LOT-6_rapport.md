# LOT 6 — Evaluations du chapitre 1SPE-VARIABLES-ALEATOIRES

## Date : 17 juillet 2026

## Fichiers produits
| Fichier | Type | Points | Duree | Capacites |
|---|---|---|---|---|
| `evaluations/1SPE-VARALEA-EV-A.tex` | Evaluation A | 20 | 55 min | C1-C5 |
| `evaluations/1SPE-VARALEA-EV-A-corrige.tex` | Corrige A | -- | -- | C1-C5 |
| `evaluations/1SPE-VARALEA-EV-B.tex` | Evaluation B | 20 | 55 min | C1-C5 |
| `evaluations/1SPE-VARALEA-EV-B-corrige.tex` | Corrige B | -- | -- | C1-C5 |

## Resolution aveugle EV-A (TRACED)

**Ex 1 (C1, C2):** 4R, 3B, 1V. X: R->1, B->3, V->10.
- Q1: P(X=1)=1/2, P(X=3)=3/8, P(X=10)=1/8.
- Q2: E(X) = 4/8+9/8+10/8 = 23/8 = 2.875. En moyenne ~2.88 euros.
- Q3: E(X^2) = 4/8+27/8+100/8 = 131/8.
- Q4: V(X) = 131/8-(23/8)^2 = 1048/64-529/64 = 519/64. sigma = sqrt(519)/8.
- Q5: E(G) = E(X)-3 = 23/8-3 = -1/8. Jeu defavorable.

**Ex 2 (C3, C4):** X ~ B(6, 1/3).
- Q1: P(X=0) = (2/3)^6 = 64/729.
- Q2: P(X=2) = C(6,2)x(1/3)^2x(2/3)^4 = 15x1/9x16/81 = 80/243.
- Q3: E(X) = 2. V(X) = 4/3. sigma = 2sqrt(3)/3.
- Q4: P(X>=1) = 1-64/729 = 665/729.

**Ex 3 (C5):** Double aux des. Mise=3, gain si double=15. P(double)=1/6.
- E(G) = 12x1/6+(-3)x5/6 = 2-5/2 = -1/2. Jeu defavorable.

Score aveugle EV-A : 20/20.

## Resolution aveugle EV-B (TRACED)

**Ex 1 (C1, C2):** 5R(2pts), 3J(5pts), 2V(8pts). Total 10.
- Q1: P(X=2)=1/2, P(X=5)=3/10, P(X=8)=1/5.
- Q2: E(X) = 10/10+15/10+16/10 = 41/10 = 4.1.
- Q3: E(X^2) = 20/10+75/10+128/10 = 223/10.
- Q4: V(X) = 223/10-(41/10)^2 = 2230/100-1681/100 = 549/100. sigma = sqrt(549)/10.

**Ex 2 (C3, C4):** X ~ B(5, 1/4).
- Q1: P(X=0) = (3/4)^5 = 243/1024.
- Q2: P(X=3) = C(5,3)x(1/4)^3x(3/4)^2 = 10x1/64x9/16 = 45/512.
- Q3: E(X) = 5/4. V(X) = 15/16.

**Ex 3 (C5):** Assurance. Prime=80, sinistre=2000, p=1/50.
- E(benefice) = 80-2000x1/50 = 80-40 = 40 euros. Contrat rentable.

Score aveugle EV-B : 20/20.

## Bilan : 0 divergence A+B.

## Cout API estime : ~4 $
