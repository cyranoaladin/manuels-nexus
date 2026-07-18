# LOT-7 — Rapport d'assemblage : TSPE-SUITES-LIMITES

## Chapitre : Complements sur les suites — limites et convergence

### Inventaire complet

#### Cours (LOT-3)

| Fichier | Contenu | Capacites |
|---------|---------|-----------|
| `cours/10_C1_convergence_divergence.tex` | Definitions formelles, operations limites | C1 |
| `cours/11_C2_recurrence.tex` | Principe de recurrence | C2 |
| `cours/12_C3_modelisation.tex` | Suites auxiliaires, modeles discrets | C3 |
| `cours/13_C4_suite_croissante_non_majoree.tex` | Theoreme + demo exigible | C4 |
| `cours/14_C5_bernoulli_qn.tex` | Bernoulli + limite q^n (demo exigible) | C5 |
| `cours/15_C6_comparaison.tex` | Comparaison + gendarmes (demo exigible) | C6 |
| `cours/16_C7_limites_exponentielle.tex` | Limites exp +inf/-inf (demo exigible) | C7 |
| `cours/07_td_contextualise.tex` | TD capital taux variable | C1,C3,C5,C6 |
| `cours/07_td_fil_rouge.tex` | TD suite recurrente complete | C1-C7 |

#### Methodes (LOT-3)

| Fichier | Methode |
|---------|---------|
| `methodes/TSPE-SUITLIM-ME-001.tex` | M1 : Determiner la limite |
| `methodes/TSPE-SUITLIM-ME-002.tex` | M2 : Rediger une recurrence |
| `methodes/TSPE-SUITLIM-ME-003.tex` | M3 : Suite arithmetico-geometrique |
| `methodes/TSPE-SUITLIM-ME-004.tex` | M4 : Monotonie/comparaison |
| `methodes/TSPE-SUITLIM-ME-005.tex` | M5 : Bernoulli et croissances comparees |

#### Exercices (LOT-4)

50 exercices `TSPE-SUITLIM-EX-001.tex` a `EX-050.tex`
50 corriges `TSPE-SUITLIM-CO-001.tex` a `CO-050.tex`
18 CDP `TSPE-SUITLIM-EX-*-CDP.tex`

Distribution :
- Parcours 1 : 20 exercices
- Parcours 2 : 15 exercices
- Parcours 3 : 15 exercices

#### QCM + Remediation (LOT-5)

| Fichier | Contenu |
|---------|---------|
| `qcm/TSPE-SUITES-LIMITES-QCM.tex` | 15 questions |
| `qcm/TSPE-SUITES-LIMITES-QCM.json` | Version JSON + diagnostics |
| `remediation/TSPE-SUITES-LIMITES-FR-R1.tex` | Suites arith/geo |
| `remediation/TSPE-SUITES-LIMITES-FR-R2.tex` | Sens de variation |
| `remediation/TSPE-SUITES-LIMITES-FR-R3.tex` | Exponentielle |
| `remediation/TSPE-SUITES-LIMITES-FR-R4.tex` | Derivation |
| `remediation/TSPE-SUITES-LIMITES-FR-R5.tex` | Inegalites |
| `remediation/TSPE-SUITES-LIMITES-RE-C1.tex` | Convergence/divergence |
| `remediation/TSPE-SUITES-LIMITES-RE-C2.tex` | Recurrence |
| `remediation/TSPE-SUITES-LIMITES-RE-C3.tex` | Modelisation |
| `remediation/TSPE-SUITES-LIMITES-RE-C4.tex` | Suite monotone bornee |
| `remediation/TSPE-SUITES-LIMITES-RE-C5.tex` | Bernoulli/exp |

#### Evaluations (LOT-6)

| Fichier | Description |
|---------|-------------|
| `evaluations/TSPE-SUITLIM-EV-A.tex` | Version A (20 pts, 55 min) |
| `evaluations/TSPE-SUITLIM-EV-A-corrige.tex` | Corrige A |
| `evaluations/TSPE-SUITLIM-EV-B.tex` | Version B (reparametree) |
| `evaluations/TSPE-SUITLIM-EV-B-corrige.tex` | Corrige B |

### Matrice de couverture capacites x parcours

| | P1 | P2 | P3 | Cours | Methode | QCM | EV-A | EV-B |
|---|---|---|---|---|---|---|---|---|
| C1 | 3 ex | 2 ex | 2 ex | oui | M1 | 2Q | Ex1 | Ex1 |
| C2 | 3 ex | 2 ex | 2 ex | oui | M2 | 2Q | Ex2 | Ex2 |
| C3 | 3 ex | 2 ex | 2 ex | oui | M3 | 2Q | Ex3 | Ex3 |
| C4 | 3 ex | 2 ex | 2 ex | oui | M4 | 2Q | Ex4 | Ex4 |
| C5 | 3 ex | 2 ex | 2 ex | oui | M5 | 3Q | Ex1 | Ex1 |
| C6 | 3 ex | 2 ex | 2 ex | oui | M4 | 2Q | Ex4 | Ex4 |
| C7 | 2 ex | 3 ex | 3 ex | oui | M5 | 2Q | impl | impl |

Couverture : 100% des capacites sur tous les parcours et supports.

### Demonstrations exigibles

| Demo | Localisation |
|------|--------------|
| Suite croissante non majoree -> +inf | `cours/13_C4` |
| Inegalite de Bernoulli | `cours/14_C5` |
| Limite de q^n | `cours/14_C5` |
| Theoreme de comparaison | `cours/15_C6` |
| Theoreme des gendarmes | `cours/15_C6` |
| lim e^x en +inf | `cours/16_C7` |
| lim e^x en -inf | `cours/16_C7` |
| lim e^x/x en +inf | `cours/16_C7` |

### Statistiques

- Total fichiers crees : 119
  - 9 cours
  - 5 methodes
  - 50 exercices + 18 CDP = 68
  - 50 corriges
  - 2 QCM (tex + json)
  - 10 remediation (5 FR + 5 RE)
  - 4 evaluations
  - 5 rapports LOT

### Actions restantes

- [ ] make verify CHAP=TSPE-SUITES-LIMITES
- [ ] make similarity CHAP=TSPE-SUITES-LIMITES
- [ ] make check-latex
- [ ] Revue humaine du contrat de sortie LOT-7
