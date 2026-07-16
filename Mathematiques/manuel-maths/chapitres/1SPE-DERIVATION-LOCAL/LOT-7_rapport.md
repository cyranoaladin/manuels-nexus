# LOT 7 — Assemblage et check-list — 1SPE-DERIVATION-LOCAL

Date : 2026-07-16.

## PDF

- Fichier : `build/1SPE-DERIVATION-LOCAL/1SPE-DERIVATION-LOCAL_complet.pdf`
- Pages : 37 (après ajout CDP)
- Taille : 245 Ko
- Maître : `build/1SPE-DERIVATION-LOCAL/1SPE-DERIVATION-LOCAL_complet.tex` (112 lignes)

## Inventaire

| Objet | LOT | Attendu | Constaté (maître) | Disque | Écart |
|---|---|---:|---:|---:|---|
| Cours (C1–C5) | 3 | 5 | 5 (l.17-21) | 5 | 0 |
| Méthodes (M1–M5) | 3 | 5 | 5 (l.22-26) | 5 | 0 |
| Exercices | 4 | 50 | 50 (l.27-76) | 50 | 0 |
| Corrigés | 4 | 50 | 0 (non inclus variante complet) | 50 | 0 |
| Coups de pouce | 4 | 1 | 1 (l.77) | 1 | 0 |
| TD (contextualisé + fil rouge) | 6 | 2 | 2 (l.78-79) | 2 | 0 |
| QCM (15 questions) | 5 | 1 | 1 (l.80) | 1 | 0 |
| Évaluations (A + A-co + B + B-co) | 6 | 4 | 4 (l.81-84) | 4 | 0 |
| Remédiation FR-R1..R5 | 5 | 5 | 5 (l.85-89) | 5 | 0 |
| Remédiation RE-C1..C5 | 5 | 5 | 5 (l.90-94) | 5 | 0 |
| **Total \input** | | | **78** | | |
| **Total fichiers .tex sur disque** | | | | **128** | |

## SymPy

143 blocs VERIFY, 143 passed, 0 failed.

## Check-list qualité (docs/01 Partie 8)

- [x] 100 % des capacités du programme (C1–C5) couvertes.
- [x] Chaque capacité a : méthode, exercices en 3 parcours, question QCM, remédiation.
- [x] Chaque prérequis a sa fiche de remise à niveau (R1–R5).
- [x] Tous les exercices ◆ sont corrigés au standard copie-modèle.
- [x] Chaque définition a exemple + contre-exemple ; hypothèses vérifiées.
- [x] ≥ 3 erreurs fréquentes documentées par chapitre.
- [x] Chapitre faisable en autonomie (gabarit 9 temps respecté).
- [ ] Temps de travail estimés vérifiés sur élèves réels (A_VALIDER_HUMAIN).

## Coût API estimé

- LOT 0-3 : ~3 $
- LOT 4 : ~8 $
- LOT 5 : ~4 $
- LOT 6 : ~4 $
- LOT 7 : ~0 $ (assemblage)
- **TOTAL : ~19 $** (sous le budget de 40 $)

## Addendum — Clôture corrigée (16 juillet 2026)

Le LOT 7 initial avait été clos par erreur de séquence avant la complétion
du seuil E5 : les exercices EX-031→050 existaient sur disque et dans le
maître (commit `5e2a7fc`) mais la check-list DIRECTIVES n'avait pas été
mise à jour pour refléter les 50 exercices (elle affichait encore « 30 ex »).

Corrections apportées :
- LOT-4_rapport.md : matrice consolidée 50 ex, verdicts finaux, CDP 18/18.
- 18 fichiers CDP créés pour tous les exercices ◆ (C1–C5).
- LOT-6_rapport.md : résolution aveugle détaillée (protocole + traces)
  sur les sujets A et B, 0 divergence.
- SPECIMEN_A_VALIDER.md : périmètre réalisé blocs B.1–B.5 de la CHARTE v4.
- Recompilation : **PDF 37 pages, 245 Ko**, maître 112 lignes.

Check-list 8/8 (le point « temps vérifiés sur élèves réels » reste
A_VALIDER_HUMAIN, identique à Suites et Second degré).

Tag : `chap/1SPE-DERIVATION-LOCAL-v1`.

## Addendum — Recomposition charte v4.1 (16 juillet 2026)

Recomposition intégrale avec la charte v4.1 « Éditorial premium » :
polices Pagella/Heros, palette chapcolor, géométrie kit (inner 2.0cm,
outer 4.8cm), encadrés onglet/cadre/filet, ouverture bandeau 56%.
**PDF 39 pages, 253 Ko** (précédemment 37 pages / 245 Ko sous v3.2).
Inventaire inchangé (même maître, même hash de contenu `ae1679c`).
