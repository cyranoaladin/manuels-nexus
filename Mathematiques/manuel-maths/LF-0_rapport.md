# LF.0 — Non-regression de la classe nexus-manuel.cls

## Date : 18 juillet 2026

## Ajouts cls posterieurs aux 5 premiers chapitres
- `\demonstration{...}` : paragraphe demonstration (commit 399e994)
- `\exerciceEval{n}{pts}{cap}{comp}` : en-tete exercice d'evaluation (commit f615938)
- `\begin{coupdepouce}{id}...\end{coupdepouce}` : env no-op (commit 4c91d1c)

## Recompilation des 10 chapitres

| Chapitre | Pages | Taille | Compilation | verify_pdf |
|---|---:|---:|---|---|
| 1SPE-SUITES | 82 | 492 Ko | PASS | PASS |
| 1SPE-SECOND-DEGRE | 65 | 369 Ko | PASS | PASS |
| 1SPE-DERIVATION-LOCAL | 39 | 253 Ko | PASS | PASS |
| 1SPE-DERIVATION-GLOBAL | 46 | 294 Ko | PASS | PASS |
| 1SPE-EXPONENTIELLE | 46 | 297 Ko | PASS (fix contrat.yaml e^{u(x)}) | PASS |
| 1SPE-TRIGONOMETRIE | 33 | 208 Ko | PASS | PASS |
| 1SPE-PRODUIT-SCALAIRE | 30 | 192 Ko | PASS | PASS |
| 1SPE-GEOMETRIE-REPEREE | 33 | 198 Ko | PASS | PASS |
| 1SPE-PROBA-COND | 31 | 186 Ko | PASS | PASS |
| 1SPE-VARIABLES-ALEATOIRES | 37 | 225 Ko | PASS | PASS |
| **Total** | **442** | **2 714 Ko** | **10/10** | **10/10** |

## Correction appliquee
- `1SPE-EXPONENTIELLE/contrat.yaml` : `e^{u(x)}` -> `$\mathrm{e}^{u(x)}$` (math mode)

## CDP : harmonisation des formats
- 2 chapitres (EXPONENTIELLE, PRODUIT-SCALAIRE) : 32 fichiers CDP utilisent `\begin{coupdepouce}{id}...\end{coupdepouce}`
- 8 chapitres : CDP utilisent `\coupDePouce{n}{text}` directement
- Les deux formats coexistent sans conflit grace a l'env no-op dans la cls
- Pas de migration necessaire : meme rendu visuel

## Sync charte
- `check_charte_sync.py` : 7/7 fichiers identiques (Maths = NSI)
