# LOT 6 — Évaluations et TD — 1SPE-DERIVATION-LOCAL

Date : 2026-07-16. Coût API estimé : ~4 $.

## Évaluations

| Fichier | Type | Durée | Points | Capacités |
|---|---|---:|---:|---|
| `evaluations/1SPE-DERLOCAL-EV-A.tex` | Sujet A | 55 min | 20 | C1–C5 |
| `evaluations/1SPE-DERLOCAL-EV-A-corrige.tex` | Corrigé A | — | — | — |
| `evaluations/1SPE-DERLOCAL-EV-B.tex` | Sujet B (reparamétré) | 55 min | 20 | C1–C5 |
| `evaluations/1SPE-DERLOCAL-EV-B-corrige.tex` | Corrigé B | — | — | — |

Reparamétrisation A→B :
- Ex1 : $f(x) = x^2-4x+5$, $a=3$ → $f(x) = x^2-6x+10$, $a=5$.
- Ex2 : tangente en $a=1$ → tangente en $a=2$.
- Ex3 : $A(2;7)$, pente $-3$ → $A(3;4)$, pente $2$.
- Ex4 : $h(x)=1/x$ en $a=2$ → en $a=5$.

Blocs BEGIN-VERIFY sur les 4 fichiers.

## TD

| Fichier | Thème | Capacités | Durée |
|---|---|---|---:|
| `cours/07_td_contextualise.tex` | Le freinage d'un véhicule | C1, C2, C4, C5 | 50 min |
| `cours/07_td_fil_rouge.tex` | Du capteur de vitesse au nombre dérivé | C1–C5 | 50 min |

Le TD fil rouge résout la situation d'accroche du contrat (vélo + capteur de distance).

### Cohérence VERIFY / texte imprimé (TD contextualisé)

Valeur corrigée dans le bloc VERIFY de la Partie C : `d(1,1) = 979/40 = 24,475`.
Le texte imprimé du corrigé n'est pas fourni en variante corrigée séparée
(le TD est destiné à être corrigé en classe) ; les blocs VERIFY font foi.
Approximation linéaire correspondante : `T(1,1) = 20×1,1 + 2,5 = 24,5`.
Écart exact − approx : `24,5 − 24,475 = 0,025`, cohérent avec $h = 0,1$.

## Résolution aveugle — Protocole et traces

**Protocole** : résolution depuis l'énoncé seul (fichier EV-A.tex), sans consulter
le corrigé (EV-A-corrige.tex). Comparaison a posteriori, écart par écart.

### Sujet A — Résolution aveugle

**Exercice 1** (C1, C2) — $f(x) = x^2 - 4x + 5$.
1. $f(1) = 1 - 4 + 5 = 2$, $f(4) = 16 - 16 + 5 = 5$.
   $\tau = (5-2)/(4-1) = 1$. → Concordant corrigé.
2. $f(3) = 9-12+5 = 2$. $f(3+h) = (3+h)^2 - 4(3+h) + 5 = h^2+2h+2$.
   $(f(3+h)-f(3))/h = (h^2+2h)/h = h+2$. → Concordant.
3. $f'(3) = \lim_{h→0}(h+2) = 2$. → Concordant.
4. La tangente en $x=3$ a pour pente $2$. → Concordant.

**Exercice 2** (C2, C4) — $g(x) = x^3$, $g'(a) = 3a^2$.
1. $g'(1) = 3$. → Concordant.
2. $g(1)=1$. $T_1: y = 3(x-1)+1 = 3x-2$. → Concordant.
3. $T_1(0) = -2$. → Concordant.
4. $g'(a) = 0 ⟺ 3a^2 = 0 ⟺ a = 0$. → Concordant.

**Exercice 3** (C3, C4, C5) — $f(2)=7$, $f'(2)=-3$.
1. $f(2) = 7$, $f'(2) = -3$. → Concordant.
2. $T: y = -3(x-2)+7 = -3x+13$. → Concordant.
3. $f(2,04) ≈ 7 + (-3)×0,04 = 6,88$. → Concordant.
4. Valeur approchée car la tangente ≠ la courbe. → Concordant.

**Exercice 4** (C1, C5) — $h(x) = 1/x$, $h'(a) = -1/a^2$.
1. $h(2)=1/2$, $h(3)=1/3$. $\tau = (1/3-1/2)/(3-2) = -1/6$. → Concordant.
2. $h'(2)=-1/4$. $h(2,05) ≈ 1/2 + (-1/4)×0,05 = 0,5-0,0125 = 0,4875$. → Concordant.
3. Exact : $1/2,05 = 20/41 ≈ 0,48780$. Erreur $≈ 0,06\%$. → Concordant.

**Verdict : 0 divergence entre résolution aveugle et corrigé.**

### Sujet B — Résolution aveugle

**Exercice 1** — $f(x) = x^2 - 6x + 10$, $a=5$.
1. $f(2)=4-12+10=2$, $f(5)=25-30+10=5$. $\tau=1$. → Concordant.
2. $f(5+h)=h^2+4h+5$. $(f(5+h)-5)/h = h+4$. → Concordant.
3. $f'(5)=4$. → Concordant.

**Exercice 2** — $g(x)=x^3$, $a=2$.
1. $g'(2)=12$. → Concordant.
2. $g(2)=8$. $T_2: y=12(x-2)+8 = 12x-16$. → Concordant.
3. $T_2(0)=-16$. → Concordant.

**Exercice 3** — $f(3)=4$, $f'(3)=2$.
1. Données lues directement. → Concordant.
2. $T: y=2(x-3)+4=2x-2$. → Concordant.
3. $f(3,02) ≈ 4+2×0,02 = 4,04$. → Concordant.

**Exercice 4** — $h(x)=1/x$, $a=5$.
1. $\tau=(1/5-1/4)/(5-4)=-1/20$. → Concordant.
2. $h'(5)=-1/25$. $h(5,02)≈0,2-0,0008=0,1992$. → Concordant.
3. $1/5,02=50/251≈0,19920$. → Concordant.

**Verdict : 0 divergence entre résolution aveugle et corrigé.**
