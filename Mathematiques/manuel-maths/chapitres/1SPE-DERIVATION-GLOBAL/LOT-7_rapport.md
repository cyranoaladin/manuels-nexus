# LOT 7 — Assemblage et check-list — 1SPE-DERIVATION-GLOBAL

Date : 2026-07-16.

## PDF

- Fichier : `build/1SPE-DERIVATION-GLOBAL/1SPE-DERIVATION-GLOBAL_complet.pdf`
- Pages : 46
- Compilation : PASS

## SymPy

114 fichiers vérifiés OK, 0 FAIL, 26 REVIEW (CDP/corrigés éval sans bloc calculable).
146 blocs BEGIN-VERIFY individuels (50 EX + 50 CO + 8 EV + 30 remédiation + 8 cours).
Script `verify_sympy.py` étendu pour couvrir remediation/, cours/, qcm/ (anciennement limité à exercices/corriges/evaluations).

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

- **EV-A** : LOT-6_rapport.md §3 — protocole complet + calculs (4 exercices),
  comparaison §4. 1 erreur détectée et corrigée (EX-3 numérateur h').
  0 divergence résiduelle.
- **EV-B** : LOT-6_rapport.md §7 — protocole complet + calculs (4 exercices),
  comparaison §8. 0 divergence. Résolution aveugle A+B : 0 divergence totale.

## Assertions rétablies (I.1)

- RE-C4 b3 : échec dû à une erreur du contenu imprimé. Le numérateur de h'
  est `x²-2x-4` (racines 1±√5), pas `x²-2x-3=(x-3)(x+1)`. Corrigé corrigé,
  assertion rétablie avec la valeur vraie.
- RE-C5 b3 : échec dû à une erreur d'assertion (`Rational(10,3)` au lieu de
  `Rational(5,3)`). Le contenu imprimé est correct (x=5/3, V=2000/27).
  Assertion rétablie avec la valeur vraie.

## Cohérence I.2 — fichiers modifiés par sed

| Fichier | Verdict | Notes |
|---------|---------|-------|
| FR-R1.tex | PASS | 3 ex : taux de variation, nombre dérivé, pentes |
| FR-R2.tex | PASS | 3 ex : équations de tangentes |
| FR-R3.tex | PASS | 3 ex : calcul littéral, factorisations |
| FR-R4.tex | PASS | 3 ex : discriminant, racines, signes |
| FR-R5.tex | PASS | 3 ex : sens de variation |
| RE-C1.tex | PASS | 3 ex : dérivées de référence |
| RE-C2.tex | PASS | 3 ex : somme, produit, quotient |
| RE-C3.tex | PASS | 3 ex : signe dérivée, variations |
| RE-C4.tex | PASS | 3 ex ; EX3 numérateur `x²-2x-4` conforme VERIFY et texte |
| RE-C5.tex | PASS | 3 ex ; EX3 `x=5/3`, `V=2000/27` conforme VERIFY et texte |
| EV-A.tex | PASS | 4 ex : tous blocs VERIFY concordants |
| EV-A-corrige.tex | PASS | Numérateur EX3 corrigé `x²-2x-2` (LOT-6 §5) |
| EV-B.tex | PASS | 4 ex reparamétrés, VERIFY concordants |
| EV-B-corrige.tex | PASS | Valeurs concordantes |
| 07_td_contextualise.tex | PASS | Profit P(x), 4 parties, VERIFY OK |
| 07_td_fil_rouge.tex | PASS | Boîte cylindrique S(r), 4 parties, VERIFY OK |

16 fichiers vérifiés : **16/16 PASS**.

## CI GitHub Actions

| Commit | Run | Résultat | Cause échec |
|--------|-----|----------|-------------|
| eea9b2c (LOT-5-6-7) | 29541576600 | FAILURE | Schémas : `"prouver"`/`"critiquer"` hors enum |
| 0960188 (EXPO LOT-0) | 29541703587 | FAILURE | Idem (chapitres pas modifiés, même base) |
| d1cb480 (intégrité) | 29542267235 | FAILURE | Idem |
| 998db4d (CI-fix) | 29560207886 | SUCCESS | 4 META corrigés, test 540/540 PASS |

Cause racine : EX-009, EX-010, EX-019, EX-020 utilisaient `"prouver"` ou `"critiquer"` dans `competences[]`, hors de l'enum du schéma BO (`["chercher","modeliser","representer","calculer","raisonner","communiquer"]`). Corrigé : remplacé par `"raisonner"` (subsumant prouver/critiquer en maths).

Tag : `chap/1SPE-DERIVATION-GLOBAL-v1`.
Tags remote (4/4) : SUITES, SECOND-DEGRE, DERIVATION-LOCAL, DERIVATION-GLOBAL.
