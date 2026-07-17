# LOT 7 — Assemblage et check-list — 1SPE-PRODUIT-SCALAIRE

Date : 2026-07-17.

## SymPy

119 blocs VERIFY OK, 0 FAIL, 21 REVIEW (CDP/corriges eval/QCM sans bloc calculable).
Corrections VERIFY : C4_applications diff_sq+2*IM -> diff_sq-2*IM, RE-C3 acos float -> Rational.
140 fichiers de validation dans `validations/`.

## Check-list qualite (docs/01 Partie 8)

- [x] 100 % des capacites (C1-C5) couvertes.
- [x] Chaque capacite a : methode, exercices en 3 parcours, question QCM, remediation.
- [x] Chaque prerequis a sa fiche de remise a niveau (R1-R5).
- [x] Tous les exercices parcours 1 sont corriges + CDP (18/18).
- [x] Chaque definition a exemple + contre-exemple.
- [x] >= 3 erreurs frequentes par section de cours.
- [x] Seuil E5 = 50 exercices atteste (LOT-4_rapport.md).
- [ ] Temps verifies sur eleves reels (A_VALIDER_HUMAIN).

## Cout API estime

- LOT 0-2 : ~0 $
- LOT 3 : ~3 $
- LOT 4 : ~8 $
- LOT 5 : ~4 $
- LOT 6 : ~4 $
- LOT 7 : ~0 $
- **TOTAL : ~19 $** (sous le budget de 40 $)

## Resolution aveugle

- **EV-A** : LOT-6_rapport.md section 3 -- protocole complet + calculs (4 exercices),
  comparaison section 4. 0 divergence.
- **EV-B** : LOT-6_rapport.md section 7 -- protocole complet + calculs (4 exercices),
  comparaison section 8. 0 divergence. Resolution aveugle A+B : 0 divergence totale.

## Inventaire

| Repertoire | Fichiers | Detail |
|---|---|---|
| cours/ | 7 | 5 sections C1-C5 + 2 TD |
| methodes/ | 5 | M1-M5 |
| exercices/ | 68 | 50 EX + 18 CDP |
| corriges/ | 50 | CO-001 a CO-050 |
| remediation/ | 10 | 5 FR-R + 5 RE-C |
| evaluations/ | 4 | EV-A, EV-A-corrige, EV-B, EV-B-corrige |
| qcm/ | 2 | TEX + JSON |
| validations/ | 0 | A generer par verify_sympy.py |
| rapports | 7 | LOT-0 a LOT-7 |
| **Total** | **153+** | |

## CI GitHub Actions

A valider apres push.

Tag : `chap/1SPE-PRODUIT-SCALAIRE-v1`.
