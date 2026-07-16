# E.2.1 — Tableau de rapprochement 1SPE-SUITES

Date : 16 juillet 2026.

## Methode de decomptage

Comptage des lignes `\input{...}` dans le fichier maitre
`build/1SPE-SUITES/1SPE-SUITES_complet.tex` (102 lignes, genere par `scripts/assemble.py`).
Les corriges (`corriges/`) ne sont pas inclus dans la variante `complet` (variante eleve) ;
ils sont comptes separement sur disque via `ls chapitres/1SPE-SUITES/corriges/*.tex | wc -l`.

## Tableau par type d'objet

| Type d'objet | LOT | Attendu (rapports) | Constate (maitre .tex) | Constate (disque) | Ecart |
|---|---|---:|---:|---:|---|
| Cours (sections C1-C7 + ouverture + diagnostic) | LOT-3 | 9 | 9 (l.18-26) | 9 | 0 |
| Methodes | LOT-3 | 7 | 7 (l.27-33) | 7 | 0 |
| Exercices | LOT-4 | 49 | 49 (l.34-82) | 49 | 0 |
| Corriges | LOT-4 | 49 | 0 (non inclus variante complet) | 49 | 0 |
| Coups de pouce | LOT-4 | 0 | 0 | 0 | 0 |
| QCM (fichier unique, 21 questions) | LOT-5 | 1 | 1 (l.85) | 1 | 0 |
| Remediation (FR-R1..R5 + RE-C1..C7) | LOT-5 | 12 | 12 (l.90-101) | 12 | 0 |
| TD (contextualise + fil rouge) | LOT-6 | 2 | 2 (l.83-84) | 2 | 0 |
| Evaluations (A + A-corrige + B + B-corrige) | LOT-6 | 4 | 4 (l.86-89) | 4 | 0 |
| **Total \input** | | **84** | **84** | | |
| **Total fichiers .tex sur disque** | | | | **133** | |
| **PDF** | LOT-7 | 82 p. (979 Ko) | 77 p. (462 Ko) | | **-5 p.** |

## Analyse de l'ecart de pages (82 -> 77)

Voir `validations/E2/diff_visuel_pages.md` pour le detail.

## Verdict

Inventaire objet : **0 ecart**. La re-attestation est confirmee sur les objets.
L'ecart de pagination est analyse et explique dans le livrable E.2.4.
