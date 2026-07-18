# LOT-6 — Rapport de production : Evaluations

## Chapitre : TSPE-SUITES-LIMITES

### Fichiers produits

| Fichier | Description |
|---------|-------------|
| `evaluations/TSPE-SUITLIM-EV-A.tex` | Evaluation version A (20 pts, 55 min) |
| `evaluations/TSPE-SUITLIM-EV-A-corrige.tex` | Corrige version A avec VERIFY |
| `evaluations/TSPE-SUITLIM-EV-B.tex` | Evaluation version B (reparametree) |
| `evaluations/TSPE-SUITLIM-EV-B-corrige.tex` | Corrige version B avec VERIFY |

### Couverture des capacites

| Exercice | Capacites | Points |
|----------|-----------|--------|
| Ex 1 | C1, C5 | 5 pts |
| Ex 2 | C2 | 5 pts |
| Ex 3 | C3 | 5 pts |
| Ex 4 | C4, C6 | 5 pts |
| **Total** | **C1-C7** | **20 pts** |

C7 est mobilisee dans le cours sur les limites de q^n (exercice 1) et par les croissances comparees (implicite dans ex 1.3 et ex 2.2).

### Resolution aveugle — Version A

**Ex 1.1** : u_n = (3n^2+2n)/(n^2+4). Factoriser par n^2 : (3+2/n)/(1+4/n^2) -> 3/1 = 3.

**Ex 1.2** : v_n = 5*(3/4)^n - 2. |3/4|<1 donc (3/4)^n -> 0. v_n -> -2.

**Ex 1.3** : w_n = n^2-3n+1. Pour n>=6 : 3/n <= 1/2, donc 1-3/n+1/n^2 >= 1/2, w_n >= n^2/2 -> +inf.

**Ex 2.1** : Init : 4^0=1>=1. Hered : 4^{n+1}=4*4^n >= 4(3n+1) = 12n+4 >= 3n+4 = 3(n+1)+1. Par recurrence, vrai.

**Ex 2.2** : 3n+1 -> +inf, 4^n >= 3n+1, par comparaison 4^n -> +inf.

**Ex 3.1** : u_0=500, u_{n+1}=0.9*u_n+80.

**Ex 3.2** : u_1 = 0.9*500+80 = 530. u_2 = 0.9*530+80 = 557.

**Ex 3.3** : l = 80/0.1 = 800. v_n = u_n-800, v_0=-300, v_n=-300*0.9^n. u_n = 800-300*0.9^n.

**Ex 3.4** : 0.9^n -> 0, lim u_n = 800. Stabilisation a 800 poissons.

**Ex 4.1** : u_1=sqrt(3)~1.73. u_2=sqrt(3*sqrt(3))=3^{3/4}~2.28. u_3=3^{7/8}~2.65.

**Ex 4.2** : Init : u_0=1 in ]0,3]. Hered : 0<u_n<=3 => 0<3u_n<=9 => 0<u_{n+1}=sqrt(3u_n)<=3.

**Ex 4.3** : u_{n+1}>=u_n <=> sqrt(3u_n)>=u_n <=> 3u_n>=u_n^2 <=> u_n(3-u_n)>=0. Vrai car 0<u_n<=3.

**Ex 4.4** : Croissante majoree => converge. l=sqrt(3l), l^2=3l, l=3 (car l>0).

0 divergence constatee entre resolution aveugle et corrige.

### Resolution aveugle — Version B

**Ex 1.1** : (4n^2-n)/(2n^2+5) = (4-1/n)/(2+5/n^2) -> 4/2 = 2.

**Ex 1.2** : |2/5|<1, (2/5)^n -> 0. v_n -> 7.

**Ex 1.3** : 2n^2-5n+3. Pour n>=5 : n^2-5n+3>=0 (discriminant 13, racine ~4.3). Donc w_n >= n^2 -> +inf.

**Ex 2.1** : Init : 3^0=1>=1. Hered : 3^{n+1}=3*3^n>=3(2n+1)=6n+3>=2n+3=2(n+1)+1 (car 4n>=0).

**Ex 2.2** : 2n+1->+inf, 3^n>=2n+1, comparaison => 3^n->+inf.

**Ex 3.1** : u_0=200, u_{n+1}=0.8*u_n+60.

**Ex 3.2** : u_1=220, u_2=236.

**Ex 3.3** : l=60/0.2=300. v_n=-100*0.8^n, u_n=300-100*0.8^n.

**Ex 3.4** : lim = 300 L.

**Ex 4.1** : u_1=sqrt(7)~2.65. u_2=sqrt(2sqrt(7)+3)~2.88.

**Ex 4.2** : 0<=u_n<=3, sqrt(3)<=u_{n+1}<=3.

**Ex 4.3** : u_{n+1}>=u_n <=> 2u_n+3>=u_n^2 <=> (u_n-3)(u_n+1)<=0. Vrai pour 0<=u_n<=3.

**Ex 4.4** : l=3.

0 divergence constatee.
