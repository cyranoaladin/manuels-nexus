# Applicabilité des rubriques auxiliaires

Un chapitre sans objet d'une rubrique n'est un défaut que si la rubrique
y est pédagogiquement attendue. Une absence non motivée reste une lacune.

- Chapitres sans objet : `5`
- `REAL_CONTENT_GAP` : `0`
- `NOT_PEDAGOGICALLY_REQUIRED` : `3`
- `COVERED_BY_ANOTHER_OBJECT` : `2`

| Manuel | Rubrique | Chapitre | Verdict |
|---|---|---|---|
| `TNSI` | `remediation` | `TNSI-HISTOIRE-INFORMATIQUE` | `COVERED_BY_ANOTHER_OBJECT` |
| `TNSI` | `remediation` | `TNSI-PROJET` | `NOT_PEDAGOGICALLY_REQUIRED` |
| `TNSI` | `banque_ecrite` | `TNSI-PROJET` | `NOT_PEDAGOGICALLY_REQUIRED` |
| `TNSI` | `banque_pratique` | `TNSI-HISTOIRE-INFORMATIQUE` | `COVERED_BY_ANOTHER_OBJECT` |
| `TNSI` | `banque_pratique` | `TNSI-PROJET` | `NOT_PEDAGOGICALLY_REQUIRED` |

## Motivations

- `TNSI-HISTOIRE-INFORMATIQUE` / `remediation` — Chapitre de culture : deux cours, deux exercices, aucune procédure à automatiser. Les erreurs visées sont des confusions de repères historiques, que les diagnostics du QCM du chapitre traitent déjà option par option.
- `TNSI-PROJET` / `remediation` — Le chapitre ne porte ni cours ni exercice : il porte le projet annuel. La remédiation d'un projet passe par ses jalons et sa grille critériée, qui existent et sont vérifiés par le gate d'évaluation. Une fiche de remédiation y serait sans objet.
- `TNSI-PROJET` / `banque_ecrite` — ASSESSMENT_MODE = PROJECT_ASSESSMENT, décision humaine du 2026-09-06. L'épreuve écrite de spécialité ne demande à personne de conduire un projet sur copie : les deux capacités du chapitre sont évaluées par le projet annuel et sa grille critériée.
- `TNSI-HISTOIRE-INFORMATIQUE` / `banque_pratique` — MENE2516123N définit l'épreuve pratique comme « résolution de problèmes et programmation sur machine ». Les deux capacités du chapitre — situer une évolution dans le temps, en expliquer les conséquences — ne se programment pas. Elles sont évaluées à l'écrit, par TNSI-ECRIT-S6-EX3.
- `TNSI-PROJET` / `banque_pratique` — Même raison qu'à l'écrit. Le projet annuel dure l'année ; il ne se traite pas en une heure sur machine.
