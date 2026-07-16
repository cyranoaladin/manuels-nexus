# LOT 7 — Assemblage du chapitre 1SPE-SECOND-DEGRE

## PDF produits
- `build/1SPE-SECOND-DEGRE/1SPE-SECOND-DEGRE_complet.pdf` : 64 pages, 819 Ko

## Verdicts globaux
- SymPy (R2) : 88/88 OK (42 exercices + 42 corriges + 4 evaluations)
- Compilation (R6) : OK (assemblage complet)
- Couverture (F01/F05) : complete, >= 3 exercices par case
- Demonstration exigible C3 : formules du discriminant redigee en strate 3

## Cout API estime total chapitre
- ~20 $ (sous le budget de 40 $)

## Addendum — Re-attestation du 16/07/2026

PDF recompile : **61 pages, 349 Ko** (contre 64 pages, 819 Ko au LOT-7 initial).

### Inventaire des objets (methode : comptage des `\input` dans le maitre)

| Objet | Attendu | Constate (maitre) | Constate (disque) |
|---|---:|---:|---:|
| Cours (C1-C6 + ouverture + diagnostic) | 8 | 8 | 8 |
| Methodes | 6 | 6 | 6 |
| Exercices | 42 | 42 | 42 |
| Corriges | 42 | — (variante eleve) | 42 |
| QCM (18 questions) | 1 | 1 | 1 |
| Remediation (FR-R1..R5 + RE-C1..C6) | 11 | 11 | 11 |
| TD | 2 | 2 | 2 |
| Evaluations | 4 | 4 | 4 |

### Cause de l'ecart de pagination (64 -> 61)

Meme cause que le chapitre SUITES : restauration de la charte v3.2 dans
`nexus-manuel.cls` (suppression du `\fontsize{9.5}{13.5}` dans les tcolorbox,
baseline skip plus compact). Gain proportionnel : 3/64 = 4.7%.

Aucun objet de contenu n'a ete ajoute ni supprime. Verdicts SymPy : 88/88 OK.

### Defaut constate

Meme defaut de sous-titre « Manuel NSI Premiere » que SUITES (cls:361).
