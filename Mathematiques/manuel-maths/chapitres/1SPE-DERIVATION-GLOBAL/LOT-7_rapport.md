# LOT 7 — Assemblage et check-list — 1SPE-DERIVATION-GLOBAL

Date : 2026-07-16.

## PDF

- Fichier : `build/1SPE-DERIVATION-GLOBAL/1SPE-DERIVATION-GLOBAL_complet.pdf`
- Pages : 46
- Compilation : PASS

## SymPy

146 blocs VERIFY, 146 passed, 0 failed.

## Check-list qualité (docs/01 Partie 8)

- [x] 100 % des capacités (C1–C5) couvertes.
- [x] Chaque capacité a : méthode, exercices en 3 parcours, question QCM, remédiation.
- [x] Chaque prérequis a sa fiche de remise à niveau (R1–R5).
- [x] Tous les exercices ◆ sont corrigés + CDP.
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
| p.3 cours | nxdef onglet plein, nxthm cadre+bandeau | OK | Kit v4.1 conforme | — | 0 | PASS |
| p.15 exercices | Badge arrondi indigo, 3 parcours | OK | — | ◆ à l'accent | 0 | PASS |
| p.35 QCM | Grille A-D, diagnostics | OK | — | — | 0 | PASS |

## Résolution aveugle

Tracée dans LOT-6_rapport.md §3 : protocole complet + calculs pour EV-A
(4 exercices), comparaison point par point §4. 0 divergence résiduelle.
Une erreur détectée et corrigée dans EX-3 (numérateur h').

## Assertions rétablies (I.1)

- RE-C4 b3 : échec dû à une erreur du contenu imprimé. Le numérateur de h'
  est `x²-2x-4` (racines 1±√5), pas `x²-2x-3=(x-3)(x+1)`. Corrigé corrigé,
  assertion rétablie avec la valeur vraie.
- RE-C5 b3 : échec dû à une erreur d'assertion (`Rational(10,3)` au lieu de
  `Rational(5,3)`). Le contenu imprimé est correct (x=5/3, V=2000/27).
  Assertion rétablie avec la valeur vraie.

## Cohérence I.2 — fichiers modifiés par sed

16 fichiers vérifiés : 16/16 PASS (voir tableau dans le commit).

Tag : `chap/1SPE-DERIVATION-GLOBAL-v1`.
