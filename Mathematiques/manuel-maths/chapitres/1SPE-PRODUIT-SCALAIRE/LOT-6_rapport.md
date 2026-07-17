# LOT 6 — Rapport de production
**Chapitre :** 1SPE-PRODUIT-SCALAIRE
**Date :** 2026-07-17
**Statut :** genere

---

## 1. Fichiers produits

| Fichier | Type | Points | Duree | Capacites |
|---|---|---|---|---|
| `evaluations/1SPE-PRODSCAL-EV-A.tex` | Evaluation A | 20 | 55 min | C1, C2, C3, C4, C5 |
| `evaluations/1SPE-PRODSCAL-EV-A-corrige.tex` | Corrige A | — | — | C1-C5 |
| `evaluations/1SPE-PRODSCAL-EV-B.tex` | Evaluation B (reparametree) | 20 | 55 min | C1, C2, C3, C4, C5 |
| `evaluations/1SPE-PRODSCAL-EV-B-corrige.tex` | Corrige B | — | — | C1-C5 |
| `cours/07_td_contextualise.tex` | TD navigation et cap | — | 50 min | C1, C3, C5 |
| `cours/07_td_fil_rouge.tex` | TD fil rouge randonneur | — | 50 min | C1-C5 |

---

## 2. Structure des evaluations

### Evaluation A
| Exercice | Points | Capacites | Contenu |
|---|---|---|---|
| Ex 1 | 5 | C1, C2 | u=(3,-1), v=(2,5) : PS, normes, identites |
| Ex 2 | 5 | C3 | A(1,2), B(4,0), C(3,5) : triangle rectangle, angles |
| Ex 3 | 5 | C4 | A(0,0), B(6,0), C(2,4) : mediatrice, hauteur, aire |
| Ex 4 | 5 | C5 | AB=8, AC=5, angle=pi/3 : Al-Kashi, aire |

### Evaluation B (reparametree)
| Exercice | Points | Capacites | Contenu |
|---|---|---|---|
| Ex 1 | 5 | C1, C2 | u=(4,2), v=(-1,3) : PS, normes, identites |
| Ex 2 | 5 | C3 | A(0,1), B(3,-1), C(2,4) : triangle rectangle, angles |
| Ex 3 | 5 | C4 | A(0,0), B(8,0), C(3,6) : mediatrice, hauteur, aire |
| Ex 4 | 5 | C5 | AB=6, AC=10, angle=pi/4 : Al-Kashi, aire |

---

## 3. TRACED — Resolution aveugle de l'Evaluation A

*Cette section presente la resolution complete de l'Evaluation A realisee de maniere aveugle (sans consulter le corrige), suivie d'une comparaison point par point.*

---

### EXERCICE 1 — resolution aveugle

**Donnees :** u=(3,-1), v=(2,5).

**Q1.** u.v = 3*2 + (-1)*5 = 6 - 5 = 1.

**Q2.** ||u|| = sqrt(9+1) = sqrt(10). ||v|| = sqrt(4+25) = sqrt(29).

**Q3.** ||u+v||^2 = ||u||^2 + 2*u.v + ||v||^2 = 10 + 2 + 29 = 41. ||u+v|| = sqrt(41).

**Q4.** (u+v).(u-v) = ||u||^2 - ||v||^2 = 10 - 29 = -19.

---

### EXERCICE 2 — resolution aveugle

**Donnees :** A(1,2), B(4,0), C(3,5).

**Q1.** AB=(3,-2), AC=(2,3). AB.AC = 6-6 = 0. Rectangle en A.

**Q2.** BA=(-3,2), BC=(-1,5). BA.BC = 3+10 = 13. ||BA||=sqrt(13), ||BC||=sqrt(26).
cos(B) = 13/(sqrt(13)*sqrt(26)) = 13/(13*sqrt(2)) = 1/sqrt(2) = sqrt(2)/2.
Angle B = pi/4.

**Q3.** Angle C = pi - pi/2 - pi/4 = pi/4. Triangle rectangle isocele en A.

---

### EXERCICE 3 — resolution aveugle

**Donnees :** A(0,0), B(6,0), C(2,4).

**Q1.** I=(3,0), AB=(6,0). Mediatrice : x = 3.

**Q2.** BC=(-4,4). H = B + t*BC = (6-4t, 4t).
AH.BC = 0 : (6-4t)(-4) + (4t)(4) = -24+16t+16t = -24+32t = 0 => t=3/4.
H = (3, 3).

**Q3.** Aire = 1/2 * |6*4 - 2*0| = 12.

---

### EXERCICE 4 — resolution aveugle

**Donnees :** AB=8, AC=5, angle(BAC)=pi/3.

**Q1.** BC^2 = 64 + 25 - 2*8*5*cos(pi/3) = 89 - 80*(1/2) = 89 - 40 = 49. BC = 7.

**Q2.** cos(B) = (49+64-25)/(2*7*8) = 88/112 = 11/14.

**Q3.** Aire = 1/2 * 8 * 5 * sin(pi/3) = 20 * sqrt(3)/2 = 10*sqrt(3) ~ 17.3.

---

## 4. Comparaison resolution aveugle EV-A vs corrige

| Exercice | Question | Resolution aveugle | Corrige | Concordance |
|---|---|---|---|---|
| Ex 1 | Q1 | u.v = 1 | idem | PASS |
| Ex 1 | Q2 | sqrt(10), sqrt(29) | idem | PASS |
| Ex 1 | Q3 | ||u+v||^2 = 41 | idem | PASS |
| Ex 1 | Q4 | -19 | idem | PASS |
| Ex 2 | Q1 | Rectangle en A | idem | PASS |
| Ex 2 | Q2 | Angle B = pi/4 | idem | PASS |
| Ex 2 | Q3 | Angle C = pi/4 | idem | PASS |
| Ex 3 | Q1 | x = 3 | idem | PASS |
| Ex 3 | Q2 | H = (3, 3) | idem | PASS |
| Ex 3 | Q3 | Aire = 12 | idem | PASS |
| Ex 4 | Q1 | BC = 7 | idem | PASS |
| Ex 4 | Q2 | cos(B) = 11/14 | idem | PASS |
| Ex 4 | Q3 | 10*sqrt(3) | idem | PASS |

**0 divergence EV-A.**

---

## 7. TRACED — Resolution aveugle de l'Evaluation B

### EXERCICE 1 — resolution aveugle

**Donnees :** u=(4,2), v=(-1,3).

**Q1.** u.v = -4+6 = 2.

**Q2.** ||u|| = sqrt(20) = 2*sqrt(5). ||v|| = sqrt(10).

**Q3.** ||u-v||^2 = 20 - 2*2 + 10 = 26. ||u-v|| = sqrt(26).

**Q4.** (u+v).(u-v) = 20 - 10 = 10.

### EXERCICE 2 — resolution aveugle

**Donnees :** A(0,1), B(3,-1), C(2,4).

**Q1.** AB=(3,-2), AC=(2,3). AB.AC = 6-6 = 0. Rectangle en A.

**Q2.** BA=(-3,2), BC=(-1,5). BA.BC = 3+10 = 13.
cos(B) = 13/(sqrt(13)*sqrt(26)) = sqrt(2)/2. Angle B = pi/4.

**Q3.** Angle C = pi/4.

### EXERCICE 3 — resolution aveugle

**Donnees :** A(0,0), B(8,0), C(3,6).

**Q1.** I=(4,0), AB=(8,0). Mediatrice : x = 4.

**Q2.** BC=(-5,6). H = B + t*BC = (8-5t, 6t).
AH.BC = 0: (8-5t)(-5) + (6t)(6) = -40 + 25t + 36t = 61t - 40 = 0 => t = 40/61.
H = (288/61, 240/61).

**Q3.** Aire = 1/2 * |8*6 - 3*0| = 24.

### EXERCICE 4 — resolution aveugle

**Donnees :** AB=6, AC=10, angle=pi/4.

**Q1.** BC^2 = 36 + 100 - 120*cos(pi/4) = 136 - 60*sqrt(2) ~ 51.15. BC ~ 7.15.

**Q2.** cos(B) = (BC^2 + 36 - 100)/(2*BC*6) = (72-60*sqrt(2))/(12*BC) ~ -0.150.

**Q3.** Aire = 1/2 * 6 * 10 * sin(pi/4) = 30*sqrt(2)/2 = 15*sqrt(2) ~ 21.2.

---

## 8. Comparaison resolution aveugle EV-B vs corrige

| Exercice | Question | Resolution aveugle | Corrige | Concordance |
|---|---|---|---|---|
| Ex 1 | Q1 | u.v = 2 | idem | PASS |
| Ex 1 | Q2 | 2*sqrt(5), sqrt(10) | idem | PASS |
| Ex 1 | Q3 | ||u-v||^2 = 26 | idem | PASS |
| Ex 1 | Q4 | 10 | idem | PASS |
| Ex 2 | Q1 | Rectangle en A | idem | PASS |
| Ex 2 | Q2 | Angle B = pi/4 | idem | PASS |
| Ex 2 | Q3 | Angle C = pi/4 | idem | PASS |
| Ex 3 | Q1 | x = 4 | idem | PASS |
| Ex 3 | Q2 | H = (288/61, 240/61) | idem | PASS |
| Ex 3 | Q3 | Aire = 24 | idem | PASS |
| Ex 4 | Q1 | BC = sqrt(136-60*sqrt(2)) ~ 7.15 | idem | PASS |
| Ex 4 | Q2 | cos(B) ~ -0.150 | idem | PASS |
| Ex 4 | Q3 | 15*sqrt(2) | idem | PASS |

**0 divergence EV-B.** Resolution aveugle complete (A+B) : **0 divergence residuelle totale**.

---

## 9. Points ouverts

- Resolution aveugle A+B : **0 divergence residuelle totale**.
- SymPy EV-A : PASS (4 blocs VERIFY).
- SymPy EV-B : PASS (4 blocs VERIFY).
