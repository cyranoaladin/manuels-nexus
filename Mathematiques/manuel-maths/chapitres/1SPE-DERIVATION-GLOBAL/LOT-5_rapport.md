# LOT 5 — Rapport de production
**Chapitre :** 1SPE-DERIVATION-GLOBAL
**Date :** 2026-07-16
**Statut :** généré

---

## 1. QCM (fichier `qcm/`)

| Fichier | Questions | Capacités couvertes |
|---|---|---|
| `1SPE-DERIVATION-GLOBAL-QCM.tex` | 15 (3 par capacité) | C1, C2, C3, C4, C5 |
| `1SPE-DERIVATION-GLOBAL-QCM.json` | 15 entrées avec distracteurs | C1, C2, C3, C4, C5 |

**Structure du QCM :**
- Subsection par capacité (C1 à C5)
- 3 questions par capacité, 4 propositions chacune (A–D)
- Grille de correction avec tableau de diagnostic (erreur type + renvoi méthode)
- Grille de réponses rapides (tableau 5×3)
- Encart score + cases à cocher par capacité

**Réponses correctes :**
Q1:B, Q2:C, Q3:C, Q4:A, Q5:C, Q6:B, Q7:C, Q8:C, Q9:C, Q10:B, Q11:B, Q12:B, Q13:B, Q14:C, Q15:C

---

## 2. Fiches de remise à niveau prérequis (fichiers `remediation/FR-R*.tex`)

| Fichier | Prérequis | Exercices | BEGIN-VERIFY |
|---|---|---|---|
| `FR-R1.tex` | R1 — Taux de variation et nombre dérivé | 3 | 3 |
| `FR-R2.tex` | R2 — Équation de la tangente | 3 | 3 |
| `FR-R3.tex` | R3 — Calcul littéral (développer, factoriser, signe) | 3 | 3 |
| `FR-R4.tex` | R4 — Polynômes du second degré (racines, signe) | 3 | 3 |
| `FR-R5.tex` | R5 — Sens de variation d'une fonction | 3 | 3 |

**Total prérequis :** 5 fiches × 3 exercices = **15 exercices**

---

## 3. Fiches de remédiation capacités (fichiers `remediation/RE-C*.tex`)

| Fichier | Capacité | Exercices | BEGIN-VERIFY |
|---|---|---|---|
| `RE-C1.tex` | C1 — Dérivées de référence | 3 | 3 |
| `RE-C2.tex` | C2 — Règles de dérivation | 3 | 3 |
| `RE-C3.tex` | C3 — Signe de la dérivée et variations | 3 | 3 |
| `RE-C4.tex` | C4 — Extremums | 3 | 3 |
| `RE-C5.tex` | C5 — Optimisation | 3 | 3 |

**Total capacités :** 5 fiches × 3 exercices = **15 exercices**

---

## 4. Bilan du LOT

- **QCM :** 15 questions, chaque distracteur documenté avec erreur type et renvoi méthode.
- **Remédiation totale :** 10 fiches, 30 exercices, tous avec blocs BEGIN-VERIFY SymPy.
- **Couverture :** R1–R5 et C1–C5 intégralement couverts.
- **Points ouverts :** aucun — tous les blocs BEGIN-VERIFY sont syntaxiquement corrects. La vérification effective par `make verify CHAP=1SPE-DERIVATION-GLOBAL` est à lancer avant validation finale.
