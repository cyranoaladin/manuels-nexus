# LOT 3 — Cours + Fiches methodes du chapitre 1SPE-SUITES

## Objets produits

### Cours (9 fichiers)
- 00_ouverture.tex : page d'ouverture (contrat, prerequis, accroche, temps)
- 01_diagnostic.tex : diagnostic d'entree 10 questions (R1-R5) + grille decodage + bloc VERIFY
- 10_C1_generalites_suites.tex : definitions suite, explicite, recurrence (3 strates)
- 11_C2_suites_arithmetiques.tex : suite arithmetique (3 strates)
- 12_C3_suites_geometriques.tex : suite geometrique (3 strates)
- 13_C4_sommes.tex : sommes + demonstrations exigibles (3 strates, demo Gauss + geo)
- 14_C5_variations.tex : sens de variation (3 methodes, 3 strates)
- 15_C6_modelisation.tex : modelisation (modeles lineaire/exponentiel, 3 strates)
- 16_C7_algorithmique.tex : algorithmique Python (terme/somme/seuil, 3 strates)

### Methodes (7 fiches)
- ME-001 (M1) : Calculer les termes d'une suite
- ME-002 (M2) : Montrer qu'une suite est arithmetique
- ME-003 (M3) : Montrer qu'une suite est geometrique
- ME-004 (M4) : Calculer une somme de termes
- ME-005 (M5) : Etudier le sens de variation
- ME-006 (M6) : Modeliser une situation par une suite
- ME-007 (M7) : Ecrire un programme Python (terme/somme/seuil)

## Verdicts
- Compilation (R6) : 16/16 fichiers OK
- Conformite (R1) : strates 1-2 utilisent uniquement les notions du referentiel
- Erreurs frequentes : >= 3 par section de cours (total > 10 sur le chapitre)
- Demonstrations exigibles (C4) : somme des entiers (Gauss) + somme geometrique (telescopage), redigees integralement en strate 3

## Corrections apportees
- nexus-manuel.cls : \margeAppui utilise \itshape au lieu de \textit (paragraphes autorisees)
- nexus-manuel.cls : ajout du package eurosym
- ME-007 : blocs Python places hors des arguments de macro (limitation listings/verbatim)
- ME-005/006/007 : renommes de M5_*.tex vers 1SPE-SUITES-ME-00*.tex (convention)

## Cout API estime
- ~3 $ (generation cours + methodes par sous-agents)
