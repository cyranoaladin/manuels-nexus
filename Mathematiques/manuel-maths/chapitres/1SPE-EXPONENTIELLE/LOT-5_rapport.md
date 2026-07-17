# LOT 5 — Rapport de production
**Chapitre :** 1SPE-EXPONENTIELLE
**Date :** 2026-07-17
**Statut :** généré

---

## 1. QCM (fichier `qcm/`)

| Fichier | Questions | Capacités couvertes |
|---|---|---|
| `1SPE-EXPONENTIELLE-QCM.tex` | 15 (3 par capacité) | C1, C2, C3, C4, C5 |
| `1SPE-EXPONENTIELLE-QCM.json` | 15 entrées avec distracteurs | C1, C2, C3, C4, C5 |

**Structure du QCM :**
- Subsection par capacité (C1 à C5)
- 3 questions par capacité, 4 propositions chacune (A–D)
- Grille de correction avec tableau de diagnostic (erreur type + renvoi méthode)

---

## 2. Fiches de remise à niveau prérequis (fichiers `remediation/FR-R*.tex`)

| Fichier | Prérequis | Exercices | BEGIN-VERIFY |
|---|---|---|---|
| `FR-R1.tex` | R1 — Dérivée somme/produit/quotient | 3 | 3 |
| `FR-R2.tex` | R2 — Signe de la dérivée et variations | 3 | 3 |
| `FR-R3.tex` | R3 — Résolution second degré | 3 | 3 |
| `FR-R4.tex` | R4 — Puissances entières | 3 | 3 |
| `FR-R5.tex` | R5 — Suites géométriques | 3 | 3 |

**Total prérequis :** 5 fiches × 3 exercices = **15 exercices**

---

## 3. Fiches de remédiation capacités (fichiers `remediation/RE-C*.tex`)

| Fichier | Capacité | Exercices | BEGIN-VERIFY |
|---|---|---|---|
| `RE-C1.tex` | C1 — Définition de l'exponentielle | 3 | 3 |
| `RE-C2.tex` | C2 — Propriétés algébriques | 3 | 3 |
| `RE-C3.tex` | C3 — Variations et limites | 3 | 3 |
| `RE-C4.tex` | C4 — Dériver e^{u(x)} | 3 | 3 |
| `RE-C5.tex` | C5 — Équations et inéquations | 3 | 3 |

**Total capacités :** 5 fiches × 3 exercices = **15 exercices**

---

## 4. Bilan du LOT

- **QCM :** 15 questions, chaque distracteur documenté avec erreur type et renvoi méthode.
- **Remédiation totale :** 10 fiches, 30 exercices, tous avec blocs BEGIN-VERIFY SymPy.
- **Couverture :** R1–R5 et C1–C5 intégralement couverts.
- **SymPy :** FR-R1 OK, FR-R2 OK, FR-R3 OK, FR-R4 OK, FR-R5 OK, RE-C1..C5 OK.
