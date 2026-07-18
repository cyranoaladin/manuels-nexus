# LOT-7 — Rapport d'assemblage : TSPE-LIMITES-FONCTIONS

## Chapitre : Limites des fonctions

### Inventaire complet

#### Cours (LOT-3)

| Fichier | Contenu | Capacites |
|---------|---------|-----------|
| `cours/10_C1_limites_fonctions.tex` | Limites en +/-inf, en un point, limites usuelles, operations, FI, terme preponderant, croissances comparees, composition | C1 |
| `cours/11_C2_asymptotes.tex` | AH, AV, interpretation graphique, methode de determination | C2 |
| `cours/12_C3_croissance_comparee.tex` | x^n vs exp, \demonstration{} exigible, consequences en -inf | C3 |
| `cours/07_td_contextualise.tex` | TD: concentration d'un medicament (pharmacocinetique) | C1, C2, C3 |
| `cours/07_td_fil_rouge.tex` | TD: fonction rationnelle + fonction avec exponentielle | C1, C2, C3 |

#### Methodes (LOT-3)

| Fichier | Methode |
|---------|---------|
| `methodes/TSPE-LIMFCT-ME-001.tex` | M1 : Determiner la limite d'une fonction |
| `methodes/TSPE-LIMFCT-ME-002.tex` | M2 : Determiner les asymptotes d'une courbe |
| `methodes/TSPE-LIMFCT-ME-003.tex` | M3 : Utiliser les croissances comparees avec l'exponentielle |

#### Exercices (LOT-4)

50 exercices `TSPE-LIMFCT-EX-001.tex` a `EX-050.tex`
50 corriges `TSPE-LIMFCT-CO-001.tex` a `CO-050.tex`
14 CDP `TSPE-LIMFCT-EX-*-CDP.tex`

Distribution :
- Parcours 1 : 21 exercices (~42%)
- Parcours 2 : 14 exercices (~28%)
- Parcours 3 : 15 exercices (~30%)

#### QCM + Remediation (LOT-5)

| Fichier | Contenu |
|---------|---------|
| `qcm/TSPE-LIMITES-FONCTIONS-QCM.tex` | 15 questions (5 par capacite) |
| `qcm/TSPE-LIMITES-FONCTIONS-QCM.json` | Version JSON + diagnostics |
| `remediation/TSPE-LIMITES-FONCTIONS-FR-R1.tex` | Limites de suites |
| `remediation/TSPE-LIMITES-FONCTIONS-FR-R2.tex` | Derivation |
| `remediation/TSPE-LIMITES-FONCTIONS-FR-R3.tex` | Exponentielle |
| `remediation/TSPE-LIMITES-FONCTIONS-FR-R4.tex` | Fonctions de reference |
| `remediation/TSPE-LIMITES-FONCTIONS-FR-R5.tex` | Notion intuitive de limite |
| `remediation/TSPE-LIMITES-FONCTIONS-RE-C1.tex` | Determiner des limites |
| `remediation/TSPE-LIMITES-FONCTIONS-RE-C2.tex` | Asymptotes |
| `remediation/TSPE-LIMITES-FONCTIONS-RE-C3.tex` | Croissances comparees |

#### Evaluations (LOT-6)

| Fichier | Description |
|---------|-------------|
| `evaluations/TSPE-LIMFCT-EV-A.tex` | Version A (20 pts, 55 min) |
| `evaluations/TSPE-LIMFCT-EV-A-corrige.tex` | Corrige A avec VERIFY |
| `evaluations/TSPE-LIMFCT-EV-B.tex` | Version B (reparametree) |
| `evaluations/TSPE-LIMFCT-EV-B-corrige.tex` | Corrige B avec VERIFY |

### Matrice de couverture capacites x parcours

| | P1 | P2 | P3 | Cours | Methode | QCM | EV-A | EV-B |
|---|---|---|---|---|---|---|---|---|
| C1 | 8 ex | 6 ex | 6 ex | oui | M1 | 5Q | Ex1 | Ex1 |
| C2 | 7 ex | 4 ex | 4 ex | oui | M2 | 5Q | Ex2 | Ex2 |
| C3 | 6 ex | 4 ex | 5 ex | oui | M3 | 5Q | Ex3 | Ex3 |

Couverture : 100% des capacites sur tous les parcours et supports.

### Demonstration exigible

| Demo | Localisation |
|------|--------------|
| Croissance comparee x^n et exp en +inf | `cours/12_C3_croissance_comparee.tex` |

### Statistiques

- Total fichiers crees : 131
  - 5 cours (3 + 2 TD)
  - 3 methodes
  - 50 exercices + 14 CDP = 64
  - 50 corriges
  - 2 QCM (tex + json)
  - 8 remediation (5 FR + 3 RE)
  - 4 evaluations
  - 7 rapports/meta (contrat, dossier_curation, LOT-0 a LOT-7)

### Actions restantes

- [ ] make verify CHAP=TSPE-LIMITES-FONCTIONS
- [ ] make similarity CHAP=TSPE-LIMITES-FONCTIONS
- [ ] make check-latex
- [ ] Revue humaine du contrat de sortie LOT-7
