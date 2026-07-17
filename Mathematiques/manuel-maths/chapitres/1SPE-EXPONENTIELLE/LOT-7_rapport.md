# LOT 7 — Assemblage et check-list — 1SPE-EXPONENTIELLE

Date : 2026-07-17.

## SymPy

119 blocs VERIFY OK, 0 FAIL, 21 REVIEW (CDP/corrigés éval/QCM sans bloc calculable).
140 fichiers de validation dans `validations/`.
5 assertions corrigées en phase de vérification (imports manquants, symboles complexes vs réels).

## Check-list qualité (docs/01 Partie 8)

- [x] 100 % des capacités (C1–C5) couvertes.
- [x] Chaque capacité a : méthode, exercices en 3 parcours, question QCM, remédiation.
- [x] Chaque prérequis a sa fiche de remise à niveau (R1–R5).
- [x] Tous les exercices ◆ sont corrigés + CDP (18/18).
- [x] Chaque définition a exemple + contre-exemple.
- [x] ≥ 3 erreurs fréquentes par section.
- [x] Seuil E5 = 50 exercices attesté (LOT-4_rapport.md).
- [ ] Temps vérifiés sur élèves réels (A_VALIDER_HUMAIN).

## Coût API estimé

- LOT 0-2 : ~0 $
- LOT 3 : ~3 $
- LOT 4 : ~8 $
- LOT 5 : ~4 $
- LOT 6 : ~4 $
- LOT 7 : ~0 $
- **TOTAL : ~19 $** (sous le budget de 40 $)

## Inspection PNG (150 dpi, `validations/`)

| Page | Contenu | Accents | Encadrés | Losanges | Overfull | Verdict |
|---|---|---|---|---|---|---|
| p.1 ouverture | Bandeau indigo, n° géant, titre blanc | OK | Objectifs chapcolor!7 | — | 0 | PASS |
| p.3 cours C1 | nxdef onglet plein, nxthm cadre+bandeau | OK | Kit v4.1 conforme | — | 0 | PASS |
| p.10 cours C4 | Formule (e^u)'=u'e^u encadrée | OK | — | — | 0 | PASS |
| p.15 exercices | Badge arrondi indigo, 3 parcours | OK | — | ◆ à l'accent | 0 | PASS |
| p.35 QCM | Grille A-D, diagnostics | OK | — | — | 0 | PASS |

## Résolution aveugle

- **EV-A** : LOT-6_rapport.md §3 — protocole complet + calculs (4 exercices),
  comparaison §4. 0 divergence.
- **EV-B** : LOT-6_rapport.md §7 — protocole complet + calculs (4 exercices),
  comparaison §8. 0 divergence. Résolution aveugle A+B : 0 divergence totale.

## Inventaire

| Répertoire | Fichiers | Détail |
|---|---|---|
| cours/ | 7 | 5 sections C1-C5 + 2 TD |
| methodes/ | 5 | M1-M5 |
| exercices/ | 68 | 50 EX + 18 CDP |
| corriges/ | 50 | CO-001 à CO-050 |
| remediation/ | 10 | 5 FR-R + 5 RE-C |
| evaluations/ | 4 | EV-A, EV-A-corrige, EV-B, EV-B-corrige |
| qcm/ | 2 | TEX + JSON |
| validations/ | 140 | .sympy.json |
| rapports | 7 | LOT-0 à LOT-7 |
| **Total** | **293** | |

## CI GitHub Actions

À valider après push.

Tag : `chap/1SPE-EXPONENTIELLE-v1`.
