# E.2.2 — Tableau de rapprochement 1SPE-SECOND-DEGRE

Date : 16 juillet 2026.

## Methode de decomptage

Comptage des lignes `\input{...}` dans le fichier maitre
`build/1SPE-SECOND-DEGRE/1SPE-SECOND-DEGRE_complet.tex` (91 lignes, genere par `scripts/assemble.py`).
Les corriges ne sont pas inclus dans la variante `complet` ; comptes sur disque.

## Tableau par type d'objet

| Type d'objet | LOT | Attendu (LOT-7) | Constate (maitre .tex) | Constate (disque) | Ecart |
|---|---|---:|---:|---:|---|
| Cours (C1-C6 + ouverture + diagnostic) | LOT-3 | 8 | 8 (l.17-24) | 8 | 0 |
| Methodes | LOT-3 | 6 | 6 (l.25-30) | 6 | 0 |
| Exercices | LOT-4 | 42 | 42 (l.31-72) | 42 | 0 |
| Corriges | LOT-4 | 42 | 0 (non inclus variante complet) | 42 | 0 |
| Coups de pouce | LOT-4 | 0 | 0 | 0 | 0 |
| QCM (fichier unique, 18 questions) | LOT-5 | 1 | 1 (l.75) | 1 | 0 |
| Remediation (FR-R1..R5 + RE-C1..C6) | LOT-5 | 11 | 11 (l.80-90) | 11 | 0 |
| TD (contextualise + fil rouge) | LOT-6 | 2 | 2 (l.73-74) | 2 | 0 |
| Evaluations (A + A-corrige + B + B-corrige) | LOT-6 | 4 | 4 (l.76-79) | 4 | 0 |
| **Total \input** | | **74** | **74** | | |
| **Total fichiers .tex sur disque** | | | | **116** | |
| **PDF** | LOT-7 | 64 p. (819 Ko) | 61 p. (349 Ko) | | **-3 p.** |

## Analyse de l'ecart de pages (64 -> 61)

Voir `validations/E2/diff_visuel_pages.md` pour le detail.

## Verdict

Inventaire objet : **0 ecart**. La re-attestation est confirmee sur les objets.
L'ecart de pagination est analyse et explique dans le livrable E.2.4.
