# LOT 3 — Cours et méthodes du chapitre TSPE-DERIVATION-CONVEXITE

## Date : 23 juillet 2026

## Contenu produit

### Cours (6 sections, strates 1-2-3)
| Fichier | Capacité | Lignes | Contenu |
|---------|----------|--------|--------|
| 10_C1_derivee_composee.tex | C1 | 75 | Théorème (v∘u)', cas particuliers (e^u, ln u, u^n, √u), exemples |
| 11_C2_etude_complete.tex | C2 | 75 | Méthode d'étude complète, exemple guidé |
| 12_C3_convexite_inegalites.tex | C3 | 92 | Définition convexité, lien avec f'', inégalités, Jensen |
| 13_C4_esquisse_courbe.tex | C4 | 77 | Lien f/f'/f'', esquisse depuis tableaux de variations |
| 14_C5_lecture_graphique.tex | C5 | 61 | Lecture graphique convexité/concavité, points d'inflexion |
| 15_C6_courbe_tangentes.tex | C6 | 70 | Démonstration exigible : f'' ≥ 0 ⇒ courbe au-dessus des tangentes |

### Méthodes (5 fiches)
| Fichier | Capacités | Méthode | Contenu |
|---------|-----------|---------|--------|
| ME-001 | C1 | M1 | Dériver une fonction composée |
| ME-002 | C2 | M2 | Mener une étude complète de fonction |
| ME-003 | C3, C6 | M3 | Démontrer des inégalités par convexité |
| ME-004 | C4, C5 | M4 | Esquisser et lire graphiquement la convexité |
| ME-005 | C1, C2 | M5 | Combiner dérivation composée et étude complète |

### TD (2 activités)
| Fichier | Type | Contenu |
|---------|------|---------|
| 07_td_contextualise.tex | TD contextualisé | Optimisation de boîte de conserve (volume fixe, minimisation métal) |
| 07_td_fil_rouge.tex | TD fil rouge | Étude de fonction coût et convexité |

## Compilation
- `make chapter CHAP=TSPE-DERIVATION-CONVEXITE` : PDF 15 pages généré
- `verify_pdf` : PASS (code 0)
- LuaLaTeX 1.17.0 (TeX Live 2023)

## Revues
- R1 (conformité programme) : PASS — les strates 1 et 2 n'utilisent que les notions du référentiel
- R6 (compilation) : PASS — 15 pages, 0 erreur fatale
- R7 (pas d'invention) : PASS — formulations alignées sur BO 2019
- Démonstration exigible C6 : rédigée intégralement dans l'environnement \demonstration

## Coût API estimé : ~0 $

## Audit 2026-08-05 (branche terminale/collection-v1) — LOT 3
make verify : 0 FAIL (120 OK / 22 REVIEW). Demonstration exigible C6 (courbe
au-dessus des tangentes) relue manuellement : correcte et rigoureuse (etude du
signe de phi(x)=f(x)-f(a)-f'(a)(x-a) via la monotonie de f'). Aucun brouillon
ni artefact laisse dans le texte (balayage grep). Compilation : succes direct
(27 pages) grace au correctif de tolerance du solveur de marge (cf. commit
c3a1034) — aucune reecriture de contenu necessaire pour ce chapitre.
