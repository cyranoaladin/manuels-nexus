# LOT 6 — Rapport de production
**Chapitre :** 1SPE-EXPONENTIELLE
**Date :** 2026-07-17
**Statut :** généré

---

## 1. Fichiers produits

| Fichier | Type | Points | Durée | Capacités |
|---|---|---|---|---|
| `evaluations/1SPE-EXPO-EV-A.tex` | Évaluation A | 20 | 55 min | C1, C2, C3, C4, C5 |
| `evaluations/1SPE-EXPO-EV-A-corrige.tex` | Corrigé A | — | — | C1–C5 |
| `evaluations/1SPE-EXPO-EV-B.tex` | Évaluation B (reparamétrée) | 20 | 55 min | C1, C2, C3, C4, C5 |
| `evaluations/1SPE-EXPO-EV-B-corrige.tex` | Corrigé B | — | — | C1–C5 |
| `cours/07_td_contextualise.tex` | TD désintégration radioactive | — | 50 min | C3, C4, C5 |
| `cours/07_td_fil_rouge.tex` | TD fil rouge intérêts composés | — | 50 min | C1–C5 |

---

## 2. Structure des évaluations

### Évaluation A
| Exercice | Points | Capacités | Contenu |
|---|---|---|---|
| Ex 1 | 5 | C1, C2 | $f(x) = e^{2x-1}$ : dérivée, simplification, valeurs, équation diff |
| Ex 2 | 6 | C3, C4 | $g(x) = (x-2)e^x$ : dérivée, variations, minimum, limites |
| Ex 3 | 5 | C2, C4, C5 | $h(x) = e^{2x}-5e^x+4$ : substitution, second degré, inéquation |
| Ex 4 | 4 | C5 | Population $P(t) = 50000 e^{0.02t}$, doublement, seuil |

### Évaluation B (reparamétrée)
| Exercice | Points | Capacités | Contenu |
|---|---|---|---|
| Ex 1 | 5 | C1, C2 | $f(x) = e^{3x+2}$ : dérivée, simplification, valeurs, équation diff |
| Ex 2 | 6 | C3, C4 | $g(x) = (x+1)e^{-x}$ : dérivée, variations, maximum, limites |
| Ex 3 | 5 | C2, C4, C5 | $h(x) = e^{2x}-3e^x+2$ : substitution, second degré, inéquation |
| Ex 4 | 4 | C5 | Population $P(t) = 30000 e^{0.03t}$, doublement, seuil |

---

## 3. TRACED — Résolution aveugle de l'Évaluation A

*Cette section présente la résolution complète de l'Évaluation A réalisée de manière aveugle (sans consulter le corrigé), suivie d'une comparaison point par point.*

---

### EXERCICE 1 — résolution aveugle

**Données :** $f(x) = e^{2x-1}$.

**Q1.** On pose $u(x) = 2x - 1$, donc $u'(x) = 2$. Par la formule $(e^u)' = u' e^u$ :
$$f'(x) = 2 e^{2x-1}.$$

**Q2.** $e^{2x-1} \times e^{1-x} = e^{(2x-1)+(1-x)} = e^{x}.$

**Q3.** $f(0) = e^{-1} = 1/e \approx 0{,}368.$
$f(1/2) = e^{2 \times 1/2 - 1} = e^{0} = 1.$ Le point $(1/2; 1)$ est sur la courbe.

**Q4.** $f'(x) = 2e^{2x-1} = 2f(x)$, donc $f$ vérifie $y' = 2y$.

---

### EXERCICE 2 — résolution aveugle

**Données :** $g(x) = (x-2)e^x$.

**Q1.** Produit : $u = x-2$, $v = e^x$, $u' = 1$, $v' = e^x$.
$$g'(x) = e^x + (x-2)e^x = (1 + x - 2)e^x = (x-1)e^x.$$

**Q2.** $e^x > 0$ pour tout $x$, donc $\text{signe}(g') = \text{signe}(x-1)$.
$g'(x) = 0 \Leftrightarrow x = 1.$
$g'(x) < 0$ pour $x < 1$, $g'(x) > 0$ pour $x > 1$.

$g(1) = (1-2)e^1 = -e \approx -2{,}72.$

Tableau de variations : décroissante sur $]-\infty; 1]$, croissante sur $[1; +\infty[$.

**Q3.** Minimum de $g$ : $-e$ atteint en $x = 1$.

**Q4.** $\lim_{x \to +\infty} g(x) = +\infty$ (produit $+\infty \times +\infty$).
$\lim_{x \to -\infty} g(x) = 0$ (résultat de cours : $x e^x \to 0$).

---

### EXERCICE 3 — résolution aveugle

**Données :** $h(x) = e^{2x} - 5e^x + 4$.

**Q1.** $X = e^x$ donc $e^{2x} = X^2$. $h(x) = X^2 - 5X + 4$.

**Q2.** $\Delta = 25 - 16 = 9$. $X_1 = (5-3)/2 = 1$, $X_2 = (5+3)/2 = 4$.

**Q3.** $e^x = 1 \Rightarrow x = 0$. $e^x = 4 \Rightarrow x = \ln 4$.
Solutions : $S = \{0; \ln 4\}$.

**Q4.** $(X-1)(X-4) \leq 0 \Leftrightarrow 1 \leq X \leq 4 \Leftrightarrow 0 \leq x \leq \ln 4$.
$S = [0; \ln 4]$.

---

### EXERCICE 4 — résolution aveugle

**Données :** $P(t) = 50000 e^{0.02t}$.

**Q1.** $P(0) = 50000 e^0 = 50000$. Population initiale en 2020.

**Q2.** $P(10) = 50000 e^{0.2} \approx 50000 \times 1{,}2214 \approx 61070$.

**Q3.** $P(t) = 100000 \Leftrightarrow e^{0.02t} = 2 \Leftrightarrow t = \ln 2 / 0.02 = 50\ln 2 \approx 34{,}66$. Année : 2055.

**Q4.** $P(t) \geq 75000 \Leftrightarrow e^{0.02t} \geq 3/2 \Leftrightarrow t \geq 50 \ln(3/2) \approx 20{,}27$. Année : 2041.

---

## 4. Comparaison résolution aveugle EV-A vs corrigé

| Exercice | Question | Résolution aveugle | Corrigé | Concordance |
|---|---|---|---|---|
| Ex 1 | Q1 | $f'(x) = 2e^{2x-1}$ | idem | ✓ |
| Ex 1 | Q2 | $e^x$ | idem | ✓ |
| Ex 1 | Q3 | $f(0) = e^{-1}$, $f(1/2) = 1$ | idem | ✓ |
| Ex 1 | Q4 | $f' = 2f$ | idem | ✓ |
| Ex 2 | Q1 | $g' = (x-1)e^x$ | idem | ✓ |
| Ex 2 | Q2 | décroissante puis croissante, charnière $x=1$ | idem | ✓ |
| Ex 2 | Q3 | min $-e$ en $x=1$ | idem | ✓ |
| Ex 2 | Q4 | $+\infty$ et $0$ | idem | ✓ |
| Ex 3 | Q1 | $X^2-5X+4$ | idem | ✓ |
| Ex 3 | Q2 | $X=1$, $X=4$ | idem | ✓ |
| Ex 3 | Q3 | $x=0$, $x=\ln 4$ | idem | ✓ |
| Ex 3 | Q4 | $[0; \ln 4]$ | idem | ✓ |
| Ex 4 | Q1 | $P(0) = 50000$ | idem | ✓ |
| Ex 4 | Q2 | $\approx 61070$ | idem | ✓ |
| Ex 4 | Q3 | $t = 50\ln 2 \approx 34{,}7$, année 2055 | idem | ✓ |
| Ex 4 | Q4 | $t \geq 50\ln(3/2) \approx 20{,}3$, année 2041 | idem | ✓ |

**0 divergence EV-A.**

---

## 7. TRACED — Résolution aveugle de l'Évaluation B

### EXERCICE 1 — résolution aveugle

**Données :** $f(x) = e^{3x+2}$.

**Q1.** $u(x) = 3x+2$, $u'(x) = 3$. $f'(x) = 3e^{3x+2}$.

**Q2.** $e^{3x+2}/e^{x+2} = e^{(3x+2)-(x+2)} = e^{2x}$.

**Q3.** $f(0) = e^2 \approx 7{,}389$. $f(-2/3) = e^{-2+2} = e^0 = 1$.

**Q4.** $f'(x) = 3e^{3x+2} = 3f(x)$, donc $f$ vérifie $y' = 3y$.

### EXERCICE 2 — résolution aveugle

**Données :** $g(x) = (x+1)e^{-x}$.

**Q1.** $u = x+1$, $v = e^{-x}$, $u' = 1$, $v' = -e^{-x}$.
$g'(x) = e^{-x} + (x+1)(-e^{-x}) = e^{-x}(1 - x - 1) = -xe^{-x}$.

**Q2.** $e^{-x} > 0$, signe de $g'$ = signe de $-x$.
$g'(x) = 0 \Leftrightarrow x = 0$. Croissante sur $]-\infty; 0]$, décroissante sur $[0; +\infty[$.
$g(0) = 1$.

**Q3.** Maximum de $g$ : $1$ en $x = 0$.

**Q4.** $\lim_{x \to +\infty} g(x) = 0$ (croissance de $e^x$ l'emporte).
$\lim_{x \to -\infty} g(x) = -\infty$ (produit $-\infty \times +\infty$).

### EXERCICE 3 — résolution aveugle

**Données :** $h(x) = e^{2x} - 3e^x + 2$.

**Q1.** $X = e^x$, $h = X^2 - 3X + 2$.

**Q2.** $\Delta = 9 - 8 = 1$. $X_1 = (3-1)/2 = 1$, $X_2 = (3+1)/2 = 2$.

**Q3.** $e^x = 1 \Rightarrow x = 0$. $e^x = 2 \Rightarrow x = \ln 2$. $S = \{0; \ln 2\}$.

**Q4.** $(X-1)(X-2) \leq 0 \Leftrightarrow 1 \leq X \leq 2 \Leftrightarrow 0 \leq x \leq \ln 2$.
$S = [0; \ln 2]$.

### EXERCICE 4 — résolution aveugle

**Données :** $P(t) = 30000 e^{0.03t}$.

**Q1.** $P(0) = 30000$.

**Q2.** $P(10) = 30000 e^{0.3} \approx 30000 \times 1{,}3499 \approx 40496$.

**Q3.** $e^{0.03t} = 2 \Rightarrow t = \ln 2 / 0.03 = 100\ln 2/3 \approx 23{,}1$. Année 2044.

**Q4.** $e^{0.03t} \geq 3/2 \Rightarrow t \geq 100\ln(3/2)/3 \approx 13{,}5$. Année 2034.

---

## 8. Comparaison résolution aveugle EV-B vs corrigé

| Exercice | Question | Résolution aveugle | Corrigé | Concordance |
|---|---|---|---|---|
| Ex 1 | Q1 | $f'(x) = 3e^{3x+2}$ | idem | ✓ |
| Ex 1 | Q2 | $e^{2x}$ | idem | ✓ |
| Ex 1 | Q3 | $f(0) = e^2$, $f(-2/3) = 1$ | idem | ✓ |
| Ex 1 | Q4 | $f' = 3f$ | idem | ✓ |
| Ex 2 | Q1 | $g' = -xe^{-x}$ | idem | ✓ |
| Ex 2 | Q2 | croissante puis décroissante, charnière $x=0$ | idem | ✓ |
| Ex 2 | Q3 | max $1$ en $x=0$ | idem | ✓ |
| Ex 2 | Q4 | $0$ et $-\infty$ | idem | ✓ |
| Ex 3 | Q1 | $X^2-3X+2$ | idem | ✓ |
| Ex 3 | Q2 | $X=1$, $X=2$ | idem | ✓ |
| Ex 3 | Q3 | $x=0$, $x=\ln 2$ | idem | ✓ |
| Ex 3 | Q4 | $[0; \ln 2]$ | idem | ✓ |
| Ex 4 | Q1 | $P(0) = 30000$ | idem | ✓ |
| Ex 4 | Q2 | $\approx 40496$ | idem | ✓ |
| Ex 4 | Q3 | $100\ln 2/3 \approx 23{,}1$, année 2044 | idem | ✓ |
| Ex 4 | Q4 | $100\ln(3/2)/3 \approx 13{,}5$, année 2034 | idem | ✓ |

**0 divergence EV-B.** Résolution aveugle complète (A+B) : **0 divergence résiduelle totale**.

---

## 9. Points ouverts

- Résolution aveugle A+B : **0 divergence résiduelle totale**.
- SymPy EV-A : PASS (4 blocs VERIFY).
- SymPy EV-B : PASS (4 blocs VERIFY).
