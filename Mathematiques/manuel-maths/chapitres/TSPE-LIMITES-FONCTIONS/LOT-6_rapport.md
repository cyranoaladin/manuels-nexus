# LOT-6 — Rapport de production : Evaluations

## Chapitre : TSPE-LIMITES-FONCTIONS

### Fichiers produits

| Fichier | Description |
|---------|-------------|
| `evaluations/TSPE-LIMFCT-EV-A.tex` | Evaluation version A (20 pts, 55 min) |
| `evaluations/TSPE-LIMFCT-EV-A-corrige.tex` | Corrige version A avec VERIFY |
| `evaluations/TSPE-LIMFCT-EV-B.tex` | Evaluation version B (reparametree) |
| `evaluations/TSPE-LIMFCT-EV-B-corrige.tex` | Corrige version B avec VERIFY |

### Couverture des capacites

| Exercice | Capacites | Points |
|----------|-----------|--------|
| Ex 1 | C1 | 6 pts |
| Ex 2 | C2 | 7 pts |
| Ex 3 | C3 | 7 pts |
| **Total** | **C1-C3** | **20 pts** |

### Resolution aveugle — Version A

**Ex 1.1** : (3x^2+x-1)/(x^2-2). Factoriser par x^2 : (3+1/x-1/x^2)/(1-2/x^2) -> 3/1 = 3.

**Ex 1.2** : 5*(1/3)^x + 2. |1/3|<1 donc (1/3)^x -> 0. lim = 0+2 = 2.

**Ex 1.3** : x^2-4x+1 = x^2(1-4/x+1/x^2). x^2 -> +inf, parenthese -> 1 > 0. lim = +inf.

**Ex 2.1** : (2x+5)/(x-1) = (2+5/x)/(1-1/x) -> 2 en +/- inf. AH y = 2.

**Ex 2.2** : Num en 1 : 2+5=7 > 0. x-1 -> 0^+ : f -> +inf. x-1 -> 0^- : f -> -inf. AV x = 1.

**Ex 2.3** : (2x+5)/(x-1) = (2(x-1)+7)/(x-1) = 2 + 7/(x-1). Verifie.

**Ex 2.4** : f(x)-2 = 7/(x-1). x>1 : >0, au-dessus. x<1 : <0, en dessous.

**Ex 3.1** : f(x) = (x^2-3)/e^x. Croissances comparees : x^2/e^x -> 0. lim(+inf) = 0. AH y=0. lim(-inf) : x^2-3 -> +inf, e^{-x} -> +inf. lim = +inf.

**Ex 3.2** : f'(x) = 2x*e^{-x} + (x^2-3)(-e^{-x}) = (2x-x^2+3)e^{-x} = (-x^2+2x+3)e^{-x}. -x^2+2x+3 = -(x^2-2x-3) = -(x-3)(x+1). OK.

**Ex 3.3** : f'(x) = 0 en x=-1 et x=3. Positif sur ]-1,3[. f decroissante sur ]-inf,-1], croissante sur [-1,3], decroissante sur [3,+inf[.

**Ex 3.4** : f(3) = (9-3)e^{-3} = 6e^{-3} ~ 0.30.

0 divergence constatee entre resolution aveugle et corrige.

### Resolution aveugle — Version B

**Ex 1.1** : (4x^2-3x)/(2x^2+1) = (4-3/x)/(2+1/x^2) -> 4/2 = 2.

**Ex 1.2** : |2/5|<1, (2/5)^x -> 0. 3*0 - 1 = -1.

**Ex 1.3** : -x^3+2x^2+5 = x^3(-1+2/x+5/x^3). x^3 -> +inf, (-1+...) -> -1 < 0. lim = -inf.

**Ex 2.1** : (3x-2)/(x+4) = (3-2/x)/(1+4/x) -> 3. AH y = 3.

**Ex 2.2** : Num en -4 : -12-2 = -14 < 0. x+4 -> 0^+ : f -> -14/0^+ = -inf. x+4 -> 0^- : f -> -14/0^- = +inf. AV x = -4.

**Ex 2.3** : (3x-2)/(x+4) = (3(x+4)-14)/(x+4) = 3 - 14/(x+4). Verifie.

**Ex 2.4** : f(x)-3 = -14/(x+4). x>-4 : <0, en dessous. x<-4 : >0, au-dessus.

**Ex 3.1** : (x^2+2x)*e^{-x} = (x^2+2x)/e^x. Croissances comparees. lim(+inf) = 0. AH y=0.

lim(-inf) : x^2+2x = x(x+2) -> +inf (x^2 preponderant), e^{-x} -> +inf. Produit +inf.

**Ex 3.2** : f'(x) = (2x+2)e^{-x} + (x^2+2x)(-e^{-x}) = (2x+2-x^2-2x)e^{-x} = (-x^2+2)e^{-x}.

**Ex 3.3** : f'(x) = 0 iff x^2 = 2 iff x = +/- sqrt(2). f croissante sur [-sqrt(2), sqrt(2)], decroissante ailleurs.

**Ex 3.4** : f(sqrt(2)) = (2+2sqrt(2))e^{-sqrt(2)} = 2(1+sqrt(2))e^{-sqrt(2)} ~ 1.41.

0 divergence constatee.
