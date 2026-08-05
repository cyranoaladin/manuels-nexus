# LOT 6 — Évaluations A+B et résolution aveugle

## Date : 23 juillet 2026

## Évaluations produites

### Évaluation A (55 min, barème 20 pts)

| Exercice | Capacités | Points | Contenu |
|----------|-----------|--------|--------|
| 1 | C1 | 5 | Dérivée de e^(2x²+1) et ln(x²+3) |
| 2 | C2 | 5 | Étude complète de x²·e^(-x) |
| 3 | C3, C6 | 5 | Convexité de e^x, inégalité e^x ≥ 1+x |
| 4 | C4, C5 | 5 | Esquisse de x³-6x²+9x+1, inflexion en x=2 |

### Évaluation B (55 min, barème 20 pts) — version re-paramétrée

| Exercice | Capacités | Points | Contenu |
|----------|-----------|--------|--------|
| 1 | C1 | 5 | Dérivée de e^(3x²+2) et ln(x²+5) |
| 2 | C2 | 5 | Étude complète de x³·e^(-x) |
| 3 | C3, C6 | 5 | Convexité de e^x, tangente en ln(2) |
| 4 | C4, C5 | 5 | Esquisse de x³-9x²+24x+2, inflexion en x=3 |

### TD (déjà présents au LOT 3)

| TD | Fichier | Contenu |
|----|---------|---------|
| TD contextualisé | cours/07_td_contextualise.tex | Optimisation de boîte de conserve |
| TD fil rouge | cours/07_td_fil_rouge.tex | Étude de fonction coût et convexité |

## Résolution aveugle

### Méthode
Les blocs VERIFY des évaluations A et B ont été résolus indépendamment par SymPy.
Chaque assertion a été exécutée sans accès au corrigé source, puis comparée au résultat attendu.

### Résultats

| Évaluation | Assertions SymPy | Verdict |
|------------|-----------------|---------|
| EV-A | 14 assertions | **PASS** (0 divergence) |
| EV-A-corrige | 14 assertions | **PASS** (0 divergence) |
| EV-B | 14 assertions | **PASS** (0 divergence) |
| EV-B-corrige | 14 assertions | **PASS** (0 divergence) |

**Total : 120 OK / 0 FAIL** (tous les objets du chapitre confondus)

### Vérification de la re-paramétrisation A → B

| Dimension | A | B | Divergence |
|-----------|---|---|------------|
| Ex 1 : fonction exponentielle | e^(2x²+1) | e^(3x²+2) | Valeurs différentes ✓ |
| Ex 1 : logarithme | ln(x²+3) | ln(x²+5) | Valeurs différentes ✓ |
| Ex 2 : fonction | x²·e^(-x) | x³·e^(-x) | Fonction différente ✓ |
| Ex 2 : extremum | x=2, 4e^(-2) | x=3, 27e^(-3) | Valeurs différentes ✓ |
| Ex 3 : inégalité | e^x ≥ 1+x | tangente en ln(2) | Approche différente ✓ |
| Ex 4 : polynôme | x³-6x²+9x+1 | x³-9x²+24x+2 | Valeurs différentes ✓ |
| Ex 4 : inflexion | x=2 | x=3 | Valeurs différentes ✓ |

**Conclusion : 0 divergence structurelle, re-paramétrisation conforme.**

## Gates

- R2 (SymPy) : **120 OK / 0 FAIL** — PASS
- Résolution aveugle A+B : **0 divergence** — PASS
- R6 (compilation) : PDF 28 pages — PASS

## Coût API estimé : ~0 $

## Audit 2026-08-05 (branche terminale/collection-v1) — LOT 6
Evaluations A/B presentes avec corriges, enonces distincts.
