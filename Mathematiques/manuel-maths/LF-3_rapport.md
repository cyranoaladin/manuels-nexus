# LF.3 — Assemblage MANUEL_1SPE_v1

## Date : 18 juillet 2026

## Script
- `scripts/assemble_manuel.py` : assembleur multi-chapitres
- Variantes : `--variant professeur` (tout) et `--variant eleve` (sans corriges/baremes)
- 3 passes LuaLaTeX (TDM + references), verify_pdf vert

## Variante professeur

| Propriete | Valeur |
|---|---|
| Pages | 445 |
| Taille | 2.1 Mo |
| Chapitres | 10 (ordre du programme) |
| Transversal front | page de garde, avant-propos, mode d'emploi, TDM |
| Transversal back | formulaire, memo Python, index capacites |
| verify_pdf | PASS (exit 0) |
| Compilation | 3 passes LuaLaTeX, 0 erreur |

## Inspection PNG (variante professeur)

| Page | Contenu | Verdict |
|---|---|---|
| 1 | Page de garde | PASS — titre, sous-titre, programme 2026 |
| 5 | Mode d'emploi (9 temps) | PASS — losanges, CDP, mise en page |
| 100 | Second degre (cours C5-C6) | PASS — proprietes, exemples, encadres |
| 300 | Trigonometrie (TD) | PASS — exercices, folios continus |
| 440 | Annexes (fin formulaire) | PASS |

## Folios
- Numerotation continue 1-445
- TDM generee automatiquement (3 passes)
- En-tetes par chapitre avec numeros de section

## Points ouverts
- `\couleurchapitre` : tous les chapitres partagent la meme couleur (chapcolor unique). Differenciation par chapitre : A_VALIDER_HUMAIN (maquette graphique).
