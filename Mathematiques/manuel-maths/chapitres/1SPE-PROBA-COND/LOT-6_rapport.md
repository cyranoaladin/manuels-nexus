# LOT 6 --- Rapport de production
**Chapitre :** 1SPE-PROBA-COND
**Date :** 2026-07-17
**Statut :** genere

---

## 1. Fichiers produits

| Fichier | Type | Points | Duree | Capacites |
|---|---|---|---|---|
| `evaluations/1SPE-PROBCOND-EV-A.tex` | Evaluation A | 20 | 55 min | C1, C2, C3, C4, C5 |
| `evaluations/1SPE-PROBCOND-EV-A-corrige.tex` | Corrige A | --- | --- | C1-C5 |
| `evaluations/1SPE-PROBCOND-EV-B.tex` | Evaluation B (reparametree) | 20 | 55 min | C1, C2, C3, C4, C5 |
| `evaluations/1SPE-PROBCOND-EV-B-corrige.tex` | Corrige B | --- | --- | C1-C5 |
| `cours/07_td_contextualise.tex` | TD depistage et VPP | --- | 50 min | C1, C2, C3, C5 |
| `cours/07_td_fil_rouge.tex` | TD controle qualite multi-fournisseurs | --- | 50 min | C1-C5 |

---

## 2. Structure des evaluations

### Evaluation A
| Exercice | Points | Capacites | Contenu |
|---|---|---|---|
| Ex 1 | 5 | C1, C2 | Sac 3R+2V, gagner : arbre, P(G), P_G(R) |
| Ex 2 | 6 | C3, C5 | Test depistage sens 90%, spec 96%, prev 3% |
| Ex 3 | 4 | C4 | P(A)=1/2, P(B)=1/5, P(AinterB)=1/10 : independance |
| Ex 4 | 5 | C3, C5 | Assurance jeunes/seniors, P(accident), P_A(J) |

### Evaluation B (reparametree)
| Exercice | Points | Capacites | Contenu |
|---|---|---|---|
| Ex 1 | 5 | C1, C2 | Sac 2B+3N, gagner : arbre, P(G), P_G(B) |
| Ex 2 | 6 | C3, C5 | Test depistage sens 95%, spec 95%, prev 2% |
| Ex 3 | 4 | C4 | P(A)=1/3, P(B)=3/8, P(AinterB)=1/8 : independance |
| Ex 4 | 5 | C3, C5 | Usine 2 fournisseurs F1(70%,2%) F2(30%,6%) |

---

## 3. TRACED --- Resolution aveugle de l'Evaluation A

*Resolution complete sans consulter le corrige.*

---

### EXERCICE 1 --- resolution aveugle

**Donnees :** Sac 3R, 2V. P_R(G)=1/2, P_V(G)=1/4.

**Q1.** P(R) = 3/5, P(V) = 2/5. Branches : R -> G(1/2), Gbar(1/2); V -> G(1/4), Gbar(3/4).

**Q2.** P(R inter G) = 3/5 x 1/2 = 3/10.

**Q3.** P(G) = P(R inter G) + P(V inter G) = 3/10 + 2/5 x 1/4 = 3/10 + 1/10 = 2/5.

**Q4.** P_G(R) = P(R inter G)/P(G) = (3/10)/(2/5) = 3/10 x 5/2 = 3/4.

---

### EXERCICE 2 --- resolution aveugle

**Donnees :** Sensibilite 90%, specificite 96%, prevalence 3%.

**Q1.** P(M) = 3/100, P_M(T) = 9/10, P_Mbar(T) = 1 - 96/100 = 4/100 = 1/25.

**Q2.** P(T) = 3/100 x 9/10 + 97/100 x 1/25.
= 27/1000 + 97/2500.
= 270/10000 + 388/10000 = 658/10000 = 329/5000.

**Q3.** P_T(M) = P(M inter T)/P(T) = (27/1000)/(329/5000) = 27/1000 x 5000/329 = 135/329.

Verification : 135/329 approx 0.410 = 41.0%.

**Q4.** VPP d'environ 41% : un test positif ne correspond a la maladie que dans 2 cas sur 5. La prevalence de 3% genere des faux positifs en nombre.

---

### EXERCICE 3 --- resolution aveugle

**Donnees :** P(A)=1/2, P(B)=1/5, P(A inter B)=1/10.

**Q1.** P(A) x P(B) = 1/2 x 1/5 = 1/10 = P(A inter B). Independants.

**Q2.** P(A union B) = 1/2 + 1/5 - 1/10 = 5/10 + 2/10 - 1/10 = 6/10 = 3/5.

**Q3.** P(Abar inter B) = P(B) - P(A inter B) = 1/5 - 1/10 = 1/10.
P(Abar) x P(B) = 1/2 x 1/5 = 1/10 = P(Abar inter B). Donc Abar et B independants.

---

### EXERCICE 4 --- resolution aveugle

**Donnees :** P(J)=1/5, P(S)=4/5, P_J(A)=1/10, P_S(A)=1/40.

**Q2.** P(A) = 1/5 x 1/10 + 4/5 x 1/40 = 1/50 + 4/200 = 1/50 + 1/50 = 2/50 = 1/25.

**Q3.** P_A(J) = P(J inter A)/P(A) = (1/50)/(1/25) = 1/50 x 25 = 1/2.

---

## 4. Comparaison resolution aveugle EV-A vs corrige

| Exercice | Question | Resolution aveugle | Corrige | Concordance |
|---|---|---|---|---|
| Ex 1 | Q1 | Arbre construit | idem | ok |
| Ex 1 | Q2 | P(R inter G)=3/10 | 3/10 | ok |
| Ex 1 | Q3 | P(G)=2/5 | 2/5 | ok |
| Ex 1 | Q4 | P_G(R)=3/4 | 3/4 | ok |
| Ex 2 | Q1 | P(M)=3/100, P_M(T)=9/10, P_Mbar(T)=1/25 | idem | ok |
| Ex 2 | Q2 | P(T)=329/5000 | 329/5000 | ok |
| Ex 2 | Q3 | P_T(M)=135/329 | 135/329 | ok |
| Ex 2 | Q4 | VPP ~41% | idem | ok |
| Ex 3 | Q1 | independants (produit=1/10) | idem | ok |
| Ex 3 | Q2 | P(AuB)=3/5 | 3/5 | ok |
| Ex 3 | Q3 | Abar et B independants | idem | ok |
| Ex 4 | Q2 | P(A)=1/25 | 1/25 | ok |
| Ex 4 | Q3 | P_A(J)=1/2 | 1/2 | ok |

**0 divergence EV-A.**

---

## 5. TRACED --- Resolution aveugle de l'Evaluation B

---

### EXERCICE 1 --- resolution aveugle

**Donnees :** Sac 2B, 3N. P_B(G)=3/4, P_N(G)=1/3.

**Q1.** P(B) = 2/5, P(N) = 3/5. Branches construites.

**Q2.** P(B inter G) = 2/5 x 3/4 = 6/20 = 3/10.

**Q3.** P(G) = 3/10 + 3/5 x 1/3 = 3/10 + 1/5 = 3/10 + 2/10 = 5/10 = 1/2.

**Q4.** P_G(B) = (3/10)/(1/2) = 3/10 x 2 = 3/5.

---

### EXERCICE 2 --- resolution aveugle

**Donnees :** Sensibilite 95%, specificite 95%, prevalence 2%.

**Q1.** P(M) = 1/50, P_M(T) = 19/20, P_Mbar(T) = 1 - 95/100 = 1/20.

**Q2.** P(T) = 1/50 x 19/20 + 49/50 x 1/20 = 19/1000 + 49/1000 = 68/1000 = 17/250.

**Q3.** P_T(M) = (19/1000)/(17/250) = 19/1000 x 250/17 = 4750/17000 = 19/68.

Verification : 19/68 approx 0.279 = 27.9%.

**Q4.** VPP d'environ 28% : moins d'un test positif sur trois correspond a un vrai malade.

---

### EXERCICE 3 --- resolution aveugle

**Donnees :** P(A)=1/3, P(B)=3/8, P(A inter B)=1/8.

**Q1.** P(A) x P(B) = 1/3 x 3/8 = 3/24 = 1/8 = P(A inter B). Independants.

**Q2.** P(A union B) = 1/3 + 3/8 - 1/8 = 8/24 + 9/24 - 3/24 = 14/24 = 7/12.

**Q3.** P_A(B) = (1/8)/(1/3) = 3/8 = P(B). Confirme l'independance.

---

### EXERCICE 4 --- resolution aveugle

**Donnees :** F1(70%, defaut 2%), F2(30%, defaut 6%).

**Q2.** P(D) = 7/10 x 1/50 + 3/10 x 3/50 = 7/500 + 9/500 = 16/500 = 4/125.

**Q3.** P_D(F2) = (9/500)/(4/125) = 9/500 x 125/4 = 1125/2000 = 9/16.

Verification : 9/16 = 0.5625 = 56.25%.

---

## 6. Comparaison resolution aveugle EV-B vs corrige

| Exercice | Question | Resolution aveugle | Corrige | Concordance |
|---|---|---|---|---|
| Ex 1 | Q2 | P(B inter G)=3/10 | 3/10 | ok |
| Ex 1 | Q3 | P(G)=1/2 | 1/2 | ok |
| Ex 1 | Q4 | P_G(B)=3/5 | 3/5 | ok |
| Ex 2 | Q1 | P(M)=1/50, P_M(T)=19/20, P_Mbar(T)=1/20 | idem | ok |
| Ex 2 | Q2 | P(T)=17/250 | 17/250 | ok |
| Ex 2 | Q3 | P_T(M)=19/68 | 19/68 | ok |
| Ex 3 | Q1 | independants (1/8=1/8) | idem | ok |
| Ex 3 | Q2 | P(AuB)=7/12 | 7/12 | ok |
| Ex 3 | Q3 | P_A(B)=3/8=P(B) | idem | ok |
| Ex 4 | Q2 | P(D)=4/125 | 4/125 | ok |
| Ex 4 | Q3 | P_D(F2)=9/16 | 9/16 | ok |

**0 divergence EV-B.**

---

## 7. Bilan

- Resolution aveugle A + B : **0 divergence residuelle totale**.
- Tous les blocs BEGIN-VERIFY sont presents dans les 4 fichiers d'evaluation.
- Les deux TD comportent des blocs BEGIN-VERIFY complets.
