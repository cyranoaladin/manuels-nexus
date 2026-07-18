# LOT-3 — Rapport de production : Cours + Methodes

## Chapitre : TSPE-SUITES-LIMITES

### Fichiers produits

| Fichier | Objet | Capacites |
|---------|-------|-----------|
| `cours/10_C1_convergence_divergence.tex` | Definitions formelles, operations sur les limites | C1 |
| `cours/11_C2_recurrence.tex` | Principe de recurrence, structure de redaction | C2 |
| `cours/12_C3_modelisation.tex` | Suites auxiliaires, modeles discrets, point fixe | C3 |
| `cours/13_C4_suite_croissante_non_majoree.tex` | Theoreme + demonstration exigible | C4 |
| `cours/14_C5_bernoulli_qn.tex` | Inegalite de Bernoulli + limite q^n (demonstrations exigibles) | C5 |
| `cours/15_C6_comparaison.tex` | Theoreme de comparaison + gendarmes (demonstrations exigibles) | C6 |
| `cours/16_C7_limites_exponentielle.tex` | Limites exp en +inf et -inf (demonstrations exigibles) | C7 |
| `cours/07_td_contextualise.tex` | TD: capital place a taux variable | C1, C3, C5, C6 |
| `cours/07_td_fil_rouge.tex` | TD fil rouge: etude complete d'une suite recurrente | C1-C7 |
| `methodes/TSPE-SUITLIM-ME-001.tex` | Determiner la limite d'une suite | C1 |
| `methodes/TSPE-SUITLIM-ME-002.tex` | Rediger une demonstration par recurrence | C2 |
| `methodes/TSPE-SUITLIM-ME-003.tex` | Etudier une suite arithmetico-geometrique | C3 |
| `methodes/TSPE-SUITLIM-ME-004.tex` | Monotonie/comparaison pour convergence/divergence | C4, C6 |
| `methodes/TSPE-SUITLIM-ME-005.tex` | Bernoulli et croissances comparees | C5, C7 |

### Demonstrations exigibles

- C4 : Suite croissante non majoree tend vers +inf (dans 13_C4)
- C5 : Inegalite de Bernoulli par recurrence + limite de q^n (dans 14_C5)
- C6 : Theoreme de comparaison + theoreme des gendarmes (dans 15_C6)
- C7 : Limites de l'exponentielle en +inf et -inf (dans 16_C7)

### Decisions

- Les TD contexualise et fil rouge contiennent des VERIFY blocks avec assertions SymPy.
- Le TD fil rouge couvre les 7 capacites via une suite recurrente u_{n+1} = (u_n+3)/(u_n+1).
- Piste Grand Oral proposee dans C3 (modelisation medicament).
- 5 fiches methodes couvrant M1-M5.

### Points ouverts

- Verification LaTeX (make check-latex) a effectuer.
