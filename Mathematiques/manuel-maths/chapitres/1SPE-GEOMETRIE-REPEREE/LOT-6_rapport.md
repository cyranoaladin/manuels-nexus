# LOT 6 — Evaluations du chapitre 1SPE-GEOMETRIE-REPEREE

## Date : 17 juillet 2026

## Objets produits
- Sujet A (55 min, 20 pts) : 5 exercices couvrant C1-C5
- Corrige A : standard copie modele, bareme par competence
- Sujet B : version isomorphe par re-parametrage
- Corrige B : adapte aux nouvelles valeurs

## Parametres
- Sujet A : A(1,3), B(5,1), Omega(3,-1), r=4
- Sujet B : A(2,5), B(6,-1), Omega(4,1), r=3

## Resolution aveugle EV-A (TRACED)

**Ex 1 (C1):** A(1,3), B(5,1).
- Q1: AB=(4,-2). Q2: m=-2/4=-1/2. Q3: x+2y-7=0. Q4: 1+6-7=0, 5+2-7=0. OK.

**Ex 2 (C2):** D: x+2y-7=0.
- Q1: Normal (1,2), directeur (-2,1).
- Q2: D' perp par M(3,4): 2x-y-2=0. Q3: (1,2)·(2,-1)=0. OK.

**Ex 3 (C3):** Omega(3,-1), r=4.
- Q1: (x-3)^2+(y+1)^2=16. Q2: (7-3)^2+0=16 oui. Q3: 0+(3+1)^2=16 oui.
- Q4: x^2+y^2-6x+2y-6=0, completion -> Omega(3,-1), r=4. OK.

**Ex 4 (C4):** D: x+2y-7=0, C: Omega(3,-1), r=4.
- Q1: d=|3-2-7|/sqrt(5)=6/sqrt(5)=6sqrt(5)/5 ~ 2.68. Q2: d<r secante.
- Q3: 5y^2-14y+1=0, Delta=176, y=(7+-2sqrt(11))/5. OK.

**Ex 5 (C5):** A(1,3), B(5,1), Omega(3,-1).
- Q1: Aire=1/2|4*(-4)-(-2)*2|=1/2*12=6.
- Q2: t=4/5, H=(21/5,7/5). Q3: h=6sqrt(5)/5. OK.

Score aveugle EV-A : 20/20.

## Resolution aveugle EV-B (TRACED)

**Ex 1 (C1):** A(2,5), B(6,-1).
- Q1: AB=(4,-6). Q2: m=-3/2. Q3: 3x+2y-16=0. Q4: 6+10-16=0, 18-2-16=0. OK.

**Ex 2 (C2):** D: 3x+2y-16=0.
- Q1: Normal (3,2), directeur (-2,3).
- Q2: D' perp par M(1,2): 2x-3y+4=0. Q3: (3,2)·(2,-3)=0. OK.

**Ex 3 (C3):** Omega(4,1), r=3.
- Q1: (x-4)^2+(y-1)^2=9. Q2: (7-4)^2+0=9 oui. Q3: 0+(4-1)^2=9 oui.
- Q4: x^2+y^2-8x-2y+8=0, completion -> Omega(4,1), r=3. OK.

**Ex 4 (C4):** D: 3x+2y-16=0, C: Omega(4,1), r=3.
- Q1: d=|12+2-16|/sqrt(13)=2/sqrt(13)=2sqrt(13)/13 ~ 0.55. Q2: d<r secante.
- Q3: substitution y=(16-3x)/2 dans equation cercle. OK.

**Ex 5 (C5):** A(2,5), B(6,-1), Omega(4,1).
- Q1: Aire=1/2|4*(-4)-(-6)*2|=1/2*4=2.
- Q2: t=8/13, H=(58/13,17/13). Q3: h=2sqrt(13)/13. OK.

Score aveugle EV-B : 20/20.

## Bilan : 0 divergence A+B.

## Cout API estime
- ~4 $
