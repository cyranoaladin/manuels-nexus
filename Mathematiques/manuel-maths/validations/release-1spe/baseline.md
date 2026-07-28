# Baseline exhaustive 1SPE

## Racine de confiance préservée

- Commit origine immuable : `41eaa745d000953654f7f07f6760c675cdae91d5`.
- Commit préflight capturé : `ca16edbb51d7f0122fcbbfea5cccfa7e2066cd63`.
- Les champs `origin`, `current`, `scope`, `capture_context`, `completeness` et `remediation_history` sont repris sans mutation.

## Comptes calculés depuis l'arbre

- Chapitres : **10**.
- Objets : **3071**.
- Seuil d'exercices par chapitre : **50**.
- Fichiers 1SPE non classés : **0**.
- Statuts : `{"fix": 6, "keep": 1470, "remove_from_release": 86, "review_required": 1509}`.

| Chapitre | Exercices | Gate 50 | Objets |
|---|---:|---|---:|
| `1SPE-DERIVATION-GLOBAL` | 53 | `certified` | 311 |
| `1SPE-DERIVATION-LOCAL` | 50 | `certified` | 316 |
| `1SPE-EXPONENTIELLE` | 50 | `certified` | 295 |
| `1SPE-GEOMETRIE-REPEREE` | 50 | `certified` | 300 |
| `1SPE-PROBA-COND` | 50 | `certified` | 298 |
| `1SPE-PRODUIT-SCALAIRE` | 50 | `certified` | 296 |
| `1SPE-SECOND-DEGRE` | 42 | `needs_fix` | 231 |
| `1SPE-SUITES` | 49 | `needs_fix` | 396 |
| `1SPE-TRIGONOMETRIE` | 20 | `needs_fix` | 211 |
| `1SPE-VARIABLES-ALEATOIRES` | 50 | `certified` | 300 |

## Builds historiques

### Eleve

- Statut : `failed` ; pages : **0**.
- Erreurs : 1 ; avertissements : 7 ; références : 0 ; débordements : 17.
- Commande exacte : `/home/alaeddine/Documents/Manuels_Nexus/Mathematiques/manuel-maths/.worktrees/1spe-bat-2026/Mathematiques/manuel-maths/.venv/bin/python scripts/assemble_manuel.py --variant eleve`.

### Professeur

- Statut : `failed` ; pages : **0**.
- Erreurs : 2 ; avertissements : 7 ; références : 0 ; débordements : 24.
- Commande exacte : `/home/alaeddine/Documents/Manuels_Nexus/Mathematiques/manuel-maths/.worktrees/1spe-bat-2026/Mathematiques/manuel-maths/.venv/bin/python scripts/assemble_manuel.py --variant professeur`.

## Auto-revue contradictoire

- Les comptes d'exercices ont été recalculés indépendamment par glob, hors fichiers `-CDP.tex`.
- La fraîcheur de chaque preuve est vraie si et seulement si son SHA déclaré égale le SHA courant de l'objet.
- Les statuts ont été contestés contre les six raisons contrôlables : `outside_program`, `stale_proof`, `missing_solution`, `duplicate_canonical_id`, `invalid_metadata`, `compilation_failure`.
- Revue consignée : **17 familles** et **170 échantillons** ; dix objets sont contrôlés dans chaque famille présente (ou la famille entière si elle en contient moins).

| Famille | Échantillons (max. 10) | Constat |
|---|---|---|
| `aid` | `1SPE-DERGLOBAL-EX-001-CDP:AID`, `1SPE-DERGLOBAL-EX-002-CDP:AID`, `1SPE-DERGLOBAL-EX-003-CDP:AID`, `1SPE-DERGLOBAL-EX-004-CDP:AID`, `1SPE-DERGLOBAL-EX-011-CDP:AID`, `1SPE-DERGLOBAL-EX-012-CDP:AID`, `1SPE-DERGLOBAL-EX-013-CDP:AID`, `1SPE-DERGLOBAL-EX-014-CDP:AID`, `1SPE-DERGLOBAL-EX-021-CDP:AID`, `1SPE-DERGLOBAL-EX-022-CDP:AID` | 10 relus, 0 avec raison contrôlée |
| `assessment` | `1SPE-DERGLOBAL-EV-A`, `1SPE-DERGLOBAL-EV-B`, `1SPE-DERLOCAL-EV-A`, `1SPE-DERLOCAL-EV-B`, `1SPE-EXPO-EV-A`, `1SPE-EXPO-EV-B`, `1SPE-GEOREP-EV-A`, `1SPE-GEOREP-EV-B`, `1SPE-PROBCOND-EV-A`, `1SPE-PROBCOND-EV-B` | 10 relus, 0 avec raison contrôlée |
| `chapter_contract` | `CHAPITRES/1SPE-DERIVATION-GLOBAL/CONTRAT`, `CHAPITRES/1SPE-DERIVATION-LOCAL/CONTRAT`, `CHAPITRES/1SPE-EXPONENTIELLE/CONTRAT`, `CHAPITRES/1SPE-GEOMETRIE-REPEREE/CONTRAT`, `CHAPITRES/1SPE-PROBA-COND/CONTRAT`, `CHAPITRES/1SPE-PRODUIT-SCALAIRE/CONTRAT`, `CHAPITRES/1SPE-SECOND-DEGRE/CONTRAT`, `CHAPITRES/1SPE-SUITES/CONTRAT`, `CHAPITRES/1SPE-TRIGONOMETRIE/CONTRAT`, `CHAPITRES/1SPE-VARIABLES-ALEATOIRES/CONTRAT` | 10 relus, 0 avec raison contrôlée |
| `chapter_metadata` | `CHAPITRES/1SPE-DERIVATION-GLOBAL/DOSSIER_CURATION`, `CHAPITRES/1SPE-DERIVATION-LOCAL/DOSSIER_CURATION`, `CHAPITRES/1SPE-EXPONENTIELLE/DOSSIER_CURATION`, `CHAPITRES/1SPE-GEOMETRIE-REPEREE/DOSSIER_CURATION`, `CHAPITRES/1SPE-PROBA-COND/DOSSIER_CURATION`, `CHAPITRES/1SPE-PRODUIT-SCALAIRE/DOSSIER_CURATION`, `CHAPITRES/1SPE-SECOND-DEGRE/DOSSIER_CURATION`, `CHAPITRES/1SPE-SUITES/DOSSIER_CURATION`, `CHAPITRES/1SPE-TRIGONOMETRIE/DOSSIER_CURATION`, `CHAPITRES/1SPE-VARIABLES-ALEATOIRES/DOSSIER_CURATION` | 10 relus, 0 avec raison contrôlée |
| `course` | `1SPE-DERGLOBAL-COURS-C1`, `1SPE-DERGLOBAL-COURS-C2`, `1SPE-DERGLOBAL-COURS-C3`, `1SPE-DERGLOBAL-COURS-C4`, `1SPE-DERGLOBAL-COURS-C5`, `1SPE-DERIVATION-LOCAL-CR-010`, `1SPE-DERIVATION-LOCAL-CR-011`, `1SPE-DERIVATION-LOCAL-CR-012`, `1SPE-DERIVATION-LOCAL-CR-013`, `1SPE-DERIVATION-LOCAL-CR-014` | 10 relus, 0 avec raison contrôlée |
| `exercise` | `1SPE-DERGLOBAL-EX-001`, `1SPE-DERGLOBAL-EX-002`, `1SPE-DERGLOBAL-EX-003`, `1SPE-DERGLOBAL-EX-004`, `1SPE-DERGLOBAL-EX-005`, `1SPE-DERGLOBAL-EX-006`, `1SPE-DERGLOBAL-EX-007`, `1SPE-DERGLOBAL-EX-008`, `1SPE-DERGLOBAL-EX-009`, `1SPE-DERGLOBAL-EX-010` | 10 relus, 0 avec raison contrôlée |
| `font` | `GABARITS/FONTS/JETBRAINSMONO-BOLD`, `GABARITS/FONTS/JETBRAINSMONO-BOLDITALIC`, `GABARITS/FONTS/JETBRAINSMONO-ITALIC`, `GABARITS/FONTS/JETBRAINSMONO-REGULAR`, `GABARITS/FONTS/LICENSE-JETBRAINSMONO`, `GABARITS/FONTS/LICENSE-LIBERTINUS`, `GABARITS/FONTS/LICENSE-MONTSERRAT`, `GABARITS/FONTS/LIBERTINUSMATH-REGULAR`, `GABARITS/FONTS/LIBERTINUSSERIF-BOLD`, `GABARITS/FONTS/LIBERTINUSSERIF-BOLDITALIC` | 10 relus, 0 avec raison contrôlée |
| `grading_scale` | `1SPE-DERGLOBAL-EV-A-corrige:SCALE`, `1SPE-DERGLOBAL-EV-B-corrige:SCALE`, `1SPE-DERLOCAL-EV-A-corrige:SCALE`, `1SPE-DERLOCAL-EV-B-corrige:SCALE`, `1SPE-EXPO-EV-A-corrige:SCALE`, `1SPE-EXPO-EV-B-corrige:SCALE`, `1SPE-GEOREP-EV-A-corrige:SCALE`, `1SPE-GEOREP-EV-B-corrige:SCALE`, `1SPE-PROBCOND-EV-A-corrige:SCALE`, `1SPE-PROBCOND-EV-B-corrige:SCALE` | 10 relus, 0 avec raison contrôlée |
| `method` | `1SPE-DERGLOBAL-ME-001`, `1SPE-DERGLOBAL-ME-002`, `1SPE-DERGLOBAL-ME-003`, `1SPE-DERGLOBAL-ME-004`, `1SPE-DERGLOBAL-ME-005`, `1SPE-DERLOCAL-ME-001`, `1SPE-DERLOCAL-ME-002`, `1SPE-DERLOCAL-ME-003`, `1SPE-DERLOCAL-ME-004`, `1SPE-DERLOCAL-ME-005` | 10 relus, 0 avec raison contrôlée |
| `outside_program` | `1SPE-TRIGO-CR-012`, `1SPE-TRIGO-CR-013`, `1SPE-TRIGO-CR-014`, `1SPE-TRIGO-CO-021`, `1SPE-TRIGO-CO-022`, `1SPE-TRIGO-CO-023`, `1SPE-TRIGO-CO-024`, `1SPE-TRIGO-CO-025`, `1SPE-TRIGO-CO-026`, `1SPE-TRIGO-CO-027` | 10 relus, 10 avec raison contrôlée |
| `qcm_json` | `CHAPITRES/1SPE-DERIVATION-GLOBAL/QCM/1SPE-DERIVATION-GLOBAL-QCM:JSON`, `CHAPITRES/1SPE-DERIVATION-LOCAL/QCM/1SPE-DERIVATION-LOCAL-QCM:JSON`, `CHAPITRES/1SPE-EXPONENTIELLE/QCM/1SPE-EXPONENTIELLE-QCM:JSON`, `CHAPITRES/1SPE-GEOMETRIE-REPEREE/QCM/1SPE-GEOREP-QCM:JSON`, `CHAPITRES/1SPE-PROBA-COND/QCM/1SPE-PROBCOND-QCM:JSON`, `CHAPITRES/1SPE-PRODUIT-SCALAIRE/QCM/1SPE-PRODUIT-SCALAIRE-QCM:JSON`, `CHAPITRES/1SPE-SECOND-DEGRE/QCM/1SPE-SECDEG-QCM:JSON`, `CHAPITRES/1SPE-SUITES/QCM/1SPE-SUITES-QCM:JSON`, `CHAPITRES/1SPE-TRIGONOMETRIE/QCM/1SPE-TRIGONOMETRIE-QCM:JSON`, `CHAPITRES/1SPE-VARIABLES-ALEATOIRES/QCM/1SPE-VARALEA-QCM:JSON` | 10 relus, 0 avec raison contrôlée |
| `qcm_tex` | `1SPE-DERIVATION-GLOBAL-QCM:TEX`, `1SPE-DERIVATION-LOCAL-QCM:TEX`, `1SPE-EXPONENTIELLE-QCM:TEX`, `1SPE-GEOREP-QCM:TEX`, `1SPE-PROBCOND-QCM:TEX`, `1SPE-PRODUIT-SCALAIRE-QCM:TEX`, `1SPE-SECDEG-QCM:TEX`, `CHAPITRES/1SPE-SUITES/QCM/.GITKEEP:TEX`, `1SPE-SUITES-QCM:TEX`, `1SPE-TRIGO-QCM:TEX` | 10 relus, 1 avec raison contrôlée |
| `remediation` | `1SPE-DERIVATION-GLOBAL-FR-R1`, `1SPE-DERIVATION-GLOBAL-FR-R2`, `1SPE-DERIVATION-GLOBAL-FR-R3`, `1SPE-DERIVATION-GLOBAL-FR-R4`, `1SPE-DERIVATION-GLOBAL-FR-R5`, `1SPE-DERIVATION-GLOBAL-RE-C1`, `1SPE-DERIVATION-GLOBAL-RE-C2`, `1SPE-DERIVATION-GLOBAL-RE-C3`, `1SPE-DERIVATION-GLOBAL-RE-C4`, `1SPE-DERIVATION-GLOBAL-RE-C5` | 10 relus, 0 avec raison contrôlée |
| `report` | `CHAPITRES/1SPE-DERIVATION-GLOBAL/LOT-0_RAPPORT`, `CHAPITRES/1SPE-DERIVATION-GLOBAL/LOT-1_RAPPORT`, `CHAPITRES/1SPE-DERIVATION-GLOBAL/LOT-2_RAPPORT`, `CHAPITRES/1SPE-DERIVATION-GLOBAL/LOT-4_RAPPORT`, `CHAPITRES/1SPE-DERIVATION-GLOBAL/LOT-5_RAPPORT`, `CHAPITRES/1SPE-DERIVATION-GLOBAL/LOT-6_RAPPORT`, `CHAPITRES/1SPE-DERIVATION-GLOBAL/LOT-7_RAPPORT`, `CHAPITRES/1SPE-DERIVATION-LOCAL/LOT-0_RAPPORT`, `CHAPITRES/1SPE-DERIVATION-LOCAL/LOT-1_RAPPORT`, `CHAPITRES/1SPE-DERIVATION-LOCAL/LOT-2_RAPPORT` | 10 relus, 0 avec raison contrôlée |
| `solution` | `1SPE-DERGLOBAL-CO-001`, `1SPE-DERGLOBAL-CO-002`, `1SPE-DERGLOBAL-CO-003`, `1SPE-DERGLOBAL-CO-004`, `1SPE-DERGLOBAL-CO-005`, `1SPE-DERGLOBAL-CO-006`, `1SPE-DERGLOBAL-CO-007`, `1SPE-DERGLOBAL-CO-008`, `1SPE-DERGLOBAL-CO-009`, `1SPE-DERGLOBAL-CO-010` | 10 relus, 0 avec raison contrôlée |
| `transversal` | `1SPE-DERGLOBAL-TD-CONTEXTUALISE`, `1SPE-DERGLOBAL-TD-FIL-ROUGE`, `1SPE-DERLOCAL-TD-CONTEXTE`, `1SPE-DERLOCAL-TD-FILROUGE`, `1SPE-EXPO-TD-CONTEXTUALISE`, `1SPE-EXPO-TD-FIL-ROUGE`, `1SPE-GEOREP-COURS-07-TC`, `1SPE-GEOREP-COURS-07-FR`, `1SPE-PROBCOND-TD-001`, `1SPE-PROBCOND-TD-002` | 10 relus, 0 avec raison contrôlée |
| `validation` | `07_td_contextualise:PROOF`, `07_td_fil_rouge:PROOF`, `10_C1_derivees_reference:PROOF`, `11_C2_regles_derivation:PROOF`, `12_C3_signe_variations:PROOF`, `13_C4_extremums:PROOF`, `14_C5_optimisation:PROOF`, `1SPE-DERGLOBAL-CO-001:PROOF`, `1SPE-DERGLOBAL-CO-002:PROOF`, `1SPE-DERGLOBAL-CO-003:PROOF` | 10 relus, 10 avec raison contrôlée |

## Inventaire intégral

| Objet | Famille | Statut | Chemin |
|---|---|---|---|
| `1SPE-TRIGO-CR-012` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/12_C3_formules_addition.tex` |
| `1SPE-TRIGO-CR-013` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/13_C4_equations_trigonometriques.tex` |
| `1SPE-TRIGO-CR-014` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/14_C5_fonctions_cos_sin.tex` |
| `1SPE-TRIGO-CO-021` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-021.tex` |
| `1SPE-TRIGO-CO-022` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-022.tex` |
| `1SPE-TRIGO-CO-023` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-023.tex` |
| `1SPE-TRIGO-CO-024` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-024.tex` |
| `1SPE-TRIGO-CO-025` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-025.tex` |
| `1SPE-TRIGO-CO-026` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-026.tex` |
| `1SPE-TRIGO-CO-027` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-027.tex` |
| `1SPE-TRIGO-CO-028` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-028.tex` |
| `1SPE-TRIGO-CO-029` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-029.tex` |
| `1SPE-TRIGO-CO-030` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-030.tex` |
| `1SPE-TRIGO-CO-031` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-031.tex` |
| `1SPE-TRIGO-CO-032` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-032.tex` |
| `1SPE-TRIGO-CO-033` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-033.tex` |
| `1SPE-TRIGO-CO-034` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-034.tex` |
| `1SPE-TRIGO-CO-035` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-035.tex` |
| `1SPE-TRIGO-CO-036` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-036.tex` |
| `1SPE-TRIGO-CO-037` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-037.tex` |
| `1SPE-TRIGO-CO-038` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-038.tex` |
| `1SPE-TRIGO-CO-039` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-039.tex` |
| `1SPE-TRIGO-CO-040` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-040.tex` |
| `1SPE-TRIGO-CO-041` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-041.tex` |
| `1SPE-TRIGO-CO-042` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-042.tex` |
| `1SPE-TRIGO-CO-043` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-043.tex` |
| `1SPE-TRIGO-CO-044` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-044.tex` |
| `1SPE-TRIGO-CO-045` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-045.tex` |
| `1SPE-TRIGO-CO-046` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-046.tex` |
| `1SPE-TRIGO-CO-047` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-047.tex` |
| `1SPE-TRIGO-CO-048` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-048.tex` |
| `1SPE-TRIGO-CO-049` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-049.tex` |
| `1SPE-TRIGO-CO-050` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-CO-050.tex` |
| `1SPE-TRIGO-EV-A-corrige` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EV-A-corrige.tex` |
| `1SPE-TRIGO-EV-A` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EV-A.tex` |
| `1SPE-TRIGO-EV-B-corrige` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EV-B-corrige.tex` |
| `1SPE-TRIGO-EV-B` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EV-B.tex` |
| `1SPE-TRIGO-EX-021-CDP` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-021-CDP.tex` |
| `1SPE-TRIGO-EX-021` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-021.tex` |
| `1SPE-TRIGO-EX-022-CDP` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-022-CDP.tex` |
| `1SPE-TRIGO-EX-022` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-022.tex` |
| `1SPE-TRIGO-EX-023-CDP` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-023-CDP.tex` |
| `1SPE-TRIGO-EX-023` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-023.tex` |
| `1SPE-TRIGO-EX-024-CDP` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-024-CDP.tex` |
| `1SPE-TRIGO-EX-024` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-024.tex` |
| `1SPE-TRIGO-EX-025` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-025.tex` |
| `1SPE-TRIGO-EX-026` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-026.tex` |
| `1SPE-TRIGO-EX-027` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-027.tex` |
| `1SPE-TRIGO-EX-028` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-028.tex` |
| `1SPE-TRIGO-EX-029` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-029.tex` |
| `1SPE-TRIGO-EX-030` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-030.tex` |
| `1SPE-TRIGO-EX-031-CDP` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-031-CDP.tex` |
| `1SPE-TRIGO-EX-031` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-031.tex` |
| `1SPE-TRIGO-EX-032-CDP` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-032-CDP.tex` |
| `1SPE-TRIGO-EX-032` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-032.tex` |
| `1SPE-TRIGO-EX-033-CDP` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-033-CDP.tex` |
| `1SPE-TRIGO-EX-033` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-033.tex` |
| `1SPE-TRIGO-EX-034-CDP` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-034-CDP.tex` |
| `1SPE-TRIGO-EX-034` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-034.tex` |
| `1SPE-TRIGO-EX-035` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-035.tex` |
| `1SPE-TRIGO-EX-036` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-036.tex` |
| `1SPE-TRIGO-EX-037` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-037.tex` |
| `1SPE-TRIGO-EX-038` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-038.tex` |
| `1SPE-TRIGO-EX-039` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-039.tex` |
| `1SPE-TRIGO-EX-040` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-040.tex` |
| `1SPE-TRIGO-EX-041-CDP` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-041-CDP.tex` |
| `1SPE-TRIGO-EX-041` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-041.tex` |
| `1SPE-TRIGO-EX-042-CDP` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-042-CDP.tex` |
| `1SPE-TRIGO-EX-042` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-042.tex` |
| `1SPE-TRIGO-EX-043` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-043.tex` |
| `1SPE-TRIGO-EX-044` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-044.tex` |
| `1SPE-TRIGO-EX-045` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-045.tex` |
| `1SPE-TRIGO-EX-046` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-046.tex` |
| `1SPE-TRIGO-EX-047` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-047.tex` |
| `1SPE-TRIGO-EX-048` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-048.tex` |
| `1SPE-TRIGO-EX-049` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-049.tex` |
| `1SPE-TRIGO-EX-050` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-EX-050.tex` |
| `1SPE-TRIGO-FR-R3` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-FR-R3.tex` |
| `1SPE-TRIGO-FR-R4` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-FR-R4.tex` |
| `1SPE-TRIGO-FR-R5` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-FR-R5.tex` |
| `1SPE-TRIGO-ME-003` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-ME-003.tex` |
| `1SPE-TRIGO-ME-004` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-ME-004.tex` |
| `1SPE-TRIGO-ME-005` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-ME-005.tex` |
| `1SPE-TRIGO-RE-C3` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-RE-C3.tex` |
| `1SPE-TRIGO-RE-C4` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-RE-C4.tex` |
| `1SPE-TRIGO-RE-C5` | `outside_program` | `remove_from_release` (outside_program) | `backlog_tspe_v2/1SPE-TRIGONOMETRIE/1SPE-TRIGO-RE-C5.tex` |
| `CHAPITRES/1SPE-DERIVATION-GLOBAL/LOT-0_RAPPORT` | `report` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/LOT-0_rapport.md` |
| `CHAPITRES/1SPE-DERIVATION-GLOBAL/LOT-1_RAPPORT` | `report` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/LOT-1_rapport.md` |
| `CHAPITRES/1SPE-DERIVATION-GLOBAL/LOT-2_RAPPORT` | `report` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/LOT-2_rapport.md` |
| `CHAPITRES/1SPE-DERIVATION-GLOBAL/LOT-4_RAPPORT` | `report` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/LOT-4_rapport.md` |
| `CHAPITRES/1SPE-DERIVATION-GLOBAL/LOT-5_RAPPORT` | `report` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/LOT-5_rapport.md` |
| `CHAPITRES/1SPE-DERIVATION-GLOBAL/LOT-6_RAPPORT` | `report` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/LOT-6_rapport.md` |
| `CHAPITRES/1SPE-DERIVATION-GLOBAL/LOT-7_RAPPORT` | `report` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/LOT-7_rapport.md` |
| `CHAPITRES/1SPE-DERIVATION-GLOBAL/CONTRAT` | `chapter_contract` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/contrat.yaml` |
| `1SPE-DERGLOBAL-CO-001` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-001.tex` |
| `1SPE-DERGLOBAL-CO-002` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-002.tex` |
| `1SPE-DERGLOBAL-CO-003` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-003.tex` |
| `1SPE-DERGLOBAL-CO-004` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-004.tex` |
| `1SPE-DERGLOBAL-CO-005` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-005.tex` |
| `1SPE-DERGLOBAL-CO-006` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-006.tex` |
| `1SPE-DERGLOBAL-CO-007` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-007.tex` |
| `1SPE-DERGLOBAL-CO-008` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-008.tex` |
| `1SPE-DERGLOBAL-CO-009` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-009.tex` |
| `1SPE-DERGLOBAL-CO-010` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-010.tex` |
| `1SPE-DERGLOBAL-CO-011` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-011.tex` |
| `1SPE-DERGLOBAL-CO-012` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-012.tex` |
| `1SPE-DERGLOBAL-CO-013` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-013.tex` |
| `1SPE-DERGLOBAL-CO-014` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-014.tex` |
| `1SPE-DERGLOBAL-CO-015` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-015.tex` |
| `1SPE-DERGLOBAL-CO-016` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-016.tex` |
| `1SPE-DERGLOBAL-CO-017` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-017.tex` |
| `1SPE-DERGLOBAL-CO-018` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-018.tex` |
| `1SPE-DERGLOBAL-CO-019` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-019.tex` |
| `1SPE-DERGLOBAL-CO-020` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-020.tex` |
| `1SPE-DERGLOBAL-CO-021` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-021.tex` |
| `1SPE-DERGLOBAL-CO-022` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-022.tex` |
| `1SPE-DERGLOBAL-CO-023` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-023.tex` |
| `1SPE-DERGLOBAL-CO-024` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-024.tex` |
| `1SPE-DERGLOBAL-CO-025` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-025.tex` |
| `1SPE-DERGLOBAL-CO-026` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-026.tex` |
| `1SPE-DERGLOBAL-CO-027` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-027.tex` |
| `1SPE-DERGLOBAL-CO-028` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-028.tex` |
| `1SPE-DERGLOBAL-CO-029` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-029.tex` |
| `1SPE-DERGLOBAL-CO-030` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-030.tex` |
| `1SPE-DERGLOBAL-CO-031` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-031.tex` |
| `1SPE-DERGLOBAL-CO-032` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-032.tex` |
| `1SPE-DERGLOBAL-CO-033` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-033.tex` |
| `1SPE-DERGLOBAL-CO-034` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-034.tex` |
| `1SPE-DERGLOBAL-CO-035` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-035.tex` |
| `1SPE-DERGLOBAL-CO-036` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-036.tex` |
| `1SPE-DERGLOBAL-CO-037` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-037.tex` |
| `1SPE-DERGLOBAL-CO-038` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-038.tex` |
| `1SPE-DERGLOBAL-CO-039` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-039.tex` |
| `1SPE-DERGLOBAL-CO-040` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-040.tex` |
| `1SPE-DERGLOBAL-CO-041` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-041.tex` |
| `1SPE-DERGLOBAL-CO-042` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-042.tex` |
| `1SPE-DERGLOBAL-CO-043` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-043.tex` |
| `1SPE-DERGLOBAL-CO-044` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-044.tex` |
| `1SPE-DERGLOBAL-CO-045` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-045.tex` |
| `1SPE-DERGLOBAL-CO-046` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-046.tex` |
| `1SPE-DERGLOBAL-CO-047` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-047.tex` |
| `1SPE-DERGLOBAL-CO-048` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-048.tex` |
| `1SPE-DERGLOBAL-CO-049` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-049.tex` |
| `1SPE-DERGLOBAL-CO-050` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-050.tex` |
| `1SPE-DERGLOBAL-CO-051` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-051.tex` |
| `1SPE-DERGLOBAL-CO-052` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-052.tex` |
| `1SPE-DERGLOBAL-CO-053` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/corriges/1SPE-DERGLOBAL-CO-053.tex` |
| `1SPE-DERGLOBAL-TD-CONTEXTUALISE` | `transversal` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/cours/07_td_contextualise.tex` |
| `1SPE-DERGLOBAL-TD-FIL-ROUGE` | `transversal` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/cours/07_td_fil_rouge.tex` |
| `1SPE-DERGLOBAL-COURS-C1` | `course` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/cours/10_C1_derivees_reference.tex` |
| `1SPE-DERGLOBAL-COURS-C2` | `course` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/cours/11_C2_regles_derivation.tex` |
| `1SPE-DERGLOBAL-COURS-C3` | `course` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/cours/12_C3_signe_variations.tex` |
| `1SPE-DERGLOBAL-COURS-C4` | `course` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/cours/13_C4_extremums.tex` |
| `1SPE-DERGLOBAL-COURS-C5` | `course` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/cours/14_C5_optimisation.tex` |
| `CHAPITRES/1SPE-DERIVATION-GLOBAL/DOSSIER_CURATION` | `chapter_metadata` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/dossier_curation.json` |
| `1SPE-DERGLOBAL-EV-A-corrige:SCALE` | `grading_scale` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/evaluations/1SPE-DERGLOBAL-EV-A-corrige.tex` |
| `1SPE-DERGLOBAL-EV-A` | `assessment` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/evaluations/1SPE-DERGLOBAL-EV-A.tex` |
| `1SPE-DERGLOBAL-EV-B-corrige:SCALE` | `grading_scale` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/evaluations/1SPE-DERGLOBAL-EV-B-corrige.tex` |
| `1SPE-DERGLOBAL-EV-B` | `assessment` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/evaluations/1SPE-DERGLOBAL-EV-B.tex` |
| `1SPE-DERGLOBAL-EX-001-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-001-CDP.tex` |
| `1SPE-DERGLOBAL-EX-001` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-001.tex` |
| `1SPE-DERGLOBAL-EX-002-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-002-CDP.tex` |
| `1SPE-DERGLOBAL-EX-002` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-002.tex` |
| `1SPE-DERGLOBAL-EX-003-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-003-CDP.tex` |
| `1SPE-DERGLOBAL-EX-003` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-003.tex` |
| `1SPE-DERGLOBAL-EX-004-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-004-CDP.tex` |
| `1SPE-DERGLOBAL-EX-004` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-004.tex` |
| `1SPE-DERGLOBAL-EX-005` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-005.tex` |
| `1SPE-DERGLOBAL-EX-006` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-006.tex` |
| `1SPE-DERGLOBAL-EX-007` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-007.tex` |
| `1SPE-DERGLOBAL-EX-008` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-008.tex` |
| `1SPE-DERGLOBAL-EX-009` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-009.tex` |
| `1SPE-DERGLOBAL-EX-010` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-010.tex` |
| `1SPE-DERGLOBAL-EX-011-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-011-CDP.tex` |
| `1SPE-DERGLOBAL-EX-011` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-011.tex` |
| `1SPE-DERGLOBAL-EX-012-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-012-CDP.tex` |
| `1SPE-DERGLOBAL-EX-012` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-012.tex` |
| `1SPE-DERGLOBAL-EX-013-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-013-CDP.tex` |
| `1SPE-DERGLOBAL-EX-013` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-013.tex` |
| `1SPE-DERGLOBAL-EX-014-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-014-CDP.tex` |
| `1SPE-DERGLOBAL-EX-014` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-014.tex` |
| `1SPE-DERGLOBAL-EX-015` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-015.tex` |
| `1SPE-DERGLOBAL-EX-016` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-016.tex` |
| `1SPE-DERGLOBAL-EX-017` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-017.tex` |
| `1SPE-DERGLOBAL-EX-018` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-018.tex` |
| `1SPE-DERGLOBAL-EX-019` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-019.tex` |
| `1SPE-DERGLOBAL-EX-020` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-020.tex` |
| `1SPE-DERGLOBAL-EX-021-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-021-CDP.tex` |
| `1SPE-DERGLOBAL-EX-021` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-021.tex` |
| `1SPE-DERGLOBAL-EX-022-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-022-CDP.tex` |
| `1SPE-DERGLOBAL-EX-022` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-022.tex` |
| `1SPE-DERGLOBAL-EX-023-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-023-CDP.tex` |
| `1SPE-DERGLOBAL-EX-023` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-023.tex` |
| `1SPE-DERGLOBAL-EX-024-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-024-CDP.tex` |
| `1SPE-DERGLOBAL-EX-024` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-024.tex` |
| `1SPE-DERGLOBAL-EX-025` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-025.tex` |
| `1SPE-DERGLOBAL-EX-026` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-026.tex` |
| `1SPE-DERGLOBAL-EX-027` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-027.tex` |
| `1SPE-DERGLOBAL-EX-028` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-028.tex` |
| `1SPE-DERGLOBAL-EX-029` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-029.tex` |
| `1SPE-DERGLOBAL-EX-030` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-030.tex` |
| `1SPE-DERGLOBAL-EX-031-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-031-CDP.tex` |
| `1SPE-DERGLOBAL-EX-031` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-031.tex` |
| `1SPE-DERGLOBAL-EX-032-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-032-CDP.tex` |
| `1SPE-DERGLOBAL-EX-032` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-032.tex` |
| `1SPE-DERGLOBAL-EX-033-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-033-CDP.tex` |
| `1SPE-DERGLOBAL-EX-033` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-033.tex` |
| `1SPE-DERGLOBAL-EX-034-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-034-CDP.tex` |
| `1SPE-DERGLOBAL-EX-034` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-034.tex` |
| `1SPE-DERGLOBAL-EX-035` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-035.tex` |
| `1SPE-DERGLOBAL-EX-036` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-036.tex` |
| `1SPE-DERGLOBAL-EX-037` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-037.tex` |
| `1SPE-DERGLOBAL-EX-038` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-038.tex` |
| `1SPE-DERGLOBAL-EX-039` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-039.tex` |
| `1SPE-DERGLOBAL-EX-040` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-040.tex` |
| `1SPE-DERGLOBAL-EX-041-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-041-CDP.tex` |
| `1SPE-DERGLOBAL-EX-041` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-041.tex` |
| `1SPE-DERGLOBAL-EX-042-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-042-CDP.tex` |
| `1SPE-DERGLOBAL-EX-042` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-042.tex` |
| `1SPE-DERGLOBAL-EX-043` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-043.tex` |
| `1SPE-DERGLOBAL-EX-044` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-044.tex` |
| `1SPE-DERGLOBAL-EX-045` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-045.tex` |
| `1SPE-DERGLOBAL-EX-046` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-046.tex` |
| `1SPE-DERGLOBAL-EX-047` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-047.tex` |
| `1SPE-DERGLOBAL-EX-048` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-048.tex` |
| `1SPE-DERGLOBAL-EX-049` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-049.tex` |
| `1SPE-DERGLOBAL-EX-050` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-050.tex` |
| `1SPE-DERGLOBAL-EX-051` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-051.tex` |
| `1SPE-DERGLOBAL-EX-052` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-052.tex` |
| `1SPE-DERGLOBAL-EX-053` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-053.tex` |
| `1SPE-DERGLOBAL-ME-001` | `method` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/methodes/1SPE-DERGLOBAL-ME-001.tex` |
| `1SPE-DERGLOBAL-ME-002` | `method` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/methodes/1SPE-DERGLOBAL-ME-002.tex` |
| `1SPE-DERGLOBAL-ME-003` | `method` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/methodes/1SPE-DERGLOBAL-ME-003.tex` |
| `1SPE-DERGLOBAL-ME-004` | `method` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/methodes/1SPE-DERGLOBAL-ME-004.tex` |
| `1SPE-DERGLOBAL-ME-005` | `method` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/methodes/1SPE-DERGLOBAL-ME-005.tex` |
| `CHAPITRES/1SPE-DERIVATION-GLOBAL/QCM/1SPE-DERIVATION-GLOBAL-QCM:JSON` | `qcm_json` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/qcm/1SPE-DERIVATION-GLOBAL-QCM.json` |
| `1SPE-DERIVATION-GLOBAL-QCM:TEX` | `qcm_tex` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/qcm/1SPE-DERIVATION-GLOBAL-QCM.tex` |
| `1SPE-DERIVATION-GLOBAL-FR-R1` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/remediation/1SPE-DERIVATION-GLOBAL-FR-R1.tex` |
| `1SPE-DERIVATION-GLOBAL-FR-R2` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/remediation/1SPE-DERIVATION-GLOBAL-FR-R2.tex` |
| `1SPE-DERIVATION-GLOBAL-FR-R3` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/remediation/1SPE-DERIVATION-GLOBAL-FR-R3.tex` |
| `1SPE-DERIVATION-GLOBAL-FR-R4` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/remediation/1SPE-DERIVATION-GLOBAL-FR-R4.tex` |
| `1SPE-DERIVATION-GLOBAL-FR-R5` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/remediation/1SPE-DERIVATION-GLOBAL-FR-R5.tex` |
| `1SPE-DERIVATION-GLOBAL-RE-C1` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/remediation/1SPE-DERIVATION-GLOBAL-RE-C1.tex` |
| `1SPE-DERIVATION-GLOBAL-RE-C2` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/remediation/1SPE-DERIVATION-GLOBAL-RE-C2.tex` |
| `1SPE-DERIVATION-GLOBAL-RE-C3` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/remediation/1SPE-DERIVATION-GLOBAL-RE-C3.tex` |
| `1SPE-DERIVATION-GLOBAL-RE-C4` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/remediation/1SPE-DERIVATION-GLOBAL-RE-C4.tex` |
| `1SPE-DERIVATION-GLOBAL-RE-C5` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/remediation/1SPE-DERIVATION-GLOBAL-RE-C5.tex` |
| `07_td_contextualise:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/07_td_contextualise.sympy.json` |
| `07_td_fil_rouge:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/07_td_fil_rouge.sympy.json` |
| `10_C1_derivees_reference:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/10_C1_derivees_reference.sympy.json` |
| `11_C2_regles_derivation:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/11_C2_regles_derivation.sympy.json` |
| `12_C3_signe_variations:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/12_C3_signe_variations.sympy.json` |
| `13_C4_extremums:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/13_C4_extremums.sympy.json` |
| `14_C5_optimisation:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/14_C5_optimisation.sympy.json` |
| `1SPE-DERGLOBAL-CO-001:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-001.sympy.json` |
| `1SPE-DERGLOBAL-CO-002:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-002.sympy.json` |
| `1SPE-DERGLOBAL-CO-003:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-003.sympy.json` |
| `1SPE-DERGLOBAL-CO-004:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-004.sympy.json` |
| `1SPE-DERGLOBAL-CO-005:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-005.sympy.json` |
| `1SPE-DERGLOBAL-CO-006:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-006.sympy.json` |
| `1SPE-DERGLOBAL-CO-007:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-007.sympy.json` |
| `1SPE-DERGLOBAL-CO-008:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-008.sympy.json` |
| `1SPE-DERGLOBAL-CO-009:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-009.sympy.json` |
| `1SPE-DERGLOBAL-CO-010:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-010.sympy.json` |
| `1SPE-DERGLOBAL-CO-011:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-011.sympy.json` |
| `1SPE-DERGLOBAL-CO-012:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-012.sympy.json` |
| `1SPE-DERGLOBAL-CO-013:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-013.sympy.json` |
| `1SPE-DERGLOBAL-CO-014:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-014.sympy.json` |
| `1SPE-DERGLOBAL-CO-015:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-015.sympy.json` |
| `1SPE-DERGLOBAL-CO-016:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-016.sympy.json` |
| `1SPE-DERGLOBAL-CO-017:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-017.sympy.json` |
| `1SPE-DERGLOBAL-CO-018:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-018.sympy.json` |
| `1SPE-DERGLOBAL-CO-019:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-019.sympy.json` |
| `1SPE-DERGLOBAL-CO-020:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-020.sympy.json` |
| `1SPE-DERGLOBAL-CO-021:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-021.sympy.json` |
| `1SPE-DERGLOBAL-CO-022:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-022.sympy.json` |
| `1SPE-DERGLOBAL-CO-023:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-023.sympy.json` |
| `1SPE-DERGLOBAL-CO-024:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-024.sympy.json` |
| `1SPE-DERGLOBAL-CO-025:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-025.sympy.json` |
| `1SPE-DERGLOBAL-CO-026:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-026.sympy.json` |
| `1SPE-DERGLOBAL-CO-027:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-027.sympy.json` |
| `1SPE-DERGLOBAL-CO-028:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-028.sympy.json` |
| `1SPE-DERGLOBAL-CO-029:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-029.sympy.json` |
| `1SPE-DERGLOBAL-CO-030:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-030.sympy.json` |
| `1SPE-DERGLOBAL-CO-031:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-031.sympy.json` |
| `1SPE-DERGLOBAL-CO-032:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-032.sympy.json` |
| `1SPE-DERGLOBAL-CO-033:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-033.sympy.json` |
| `1SPE-DERGLOBAL-CO-034:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-034.sympy.json` |
| `1SPE-DERGLOBAL-CO-035:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-035.sympy.json` |
| `1SPE-DERGLOBAL-CO-036:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-036.sympy.json` |
| `1SPE-DERGLOBAL-CO-037:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-037.sympy.json` |
| `1SPE-DERGLOBAL-CO-038:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-038.sympy.json` |
| `1SPE-DERGLOBAL-CO-039:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-039.sympy.json` |
| `1SPE-DERGLOBAL-CO-040:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-040.sympy.json` |
| `1SPE-DERGLOBAL-CO-041:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-041.sympy.json` |
| `1SPE-DERGLOBAL-CO-042:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-042.sympy.json` |
| `1SPE-DERGLOBAL-CO-043:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-043.sympy.json` |
| `1SPE-DERGLOBAL-CO-044:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-044.sympy.json` |
| `1SPE-DERGLOBAL-CO-045:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-045.sympy.json` |
| `1SPE-DERGLOBAL-CO-046:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-046.sympy.json` |
| `1SPE-DERGLOBAL-CO-047:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-047.sympy.json` |
| `1SPE-DERGLOBAL-CO-048:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-048.sympy.json` |
| `1SPE-DERGLOBAL-CO-049:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-049.sympy.json` |
| `1SPE-DERGLOBAL-CO-050:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-050.sympy.json` |
| `1SPE-DERGLOBAL-CO-051:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-051.sympy.json` |
| `1SPE-DERGLOBAL-CO-052:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-052.sympy.json` |
| `1SPE-DERGLOBAL-CO-053:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-CO-053.sympy.json` |
| `1SPE-DERGLOBAL-EV-A-corrige:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EV-A-corrige.sympy.json` |
| `1SPE-DERGLOBAL-EV-A:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EV-A.sympy.json` |
| `1SPE-DERGLOBAL-EV-B-corrige:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EV-B-corrige.sympy.json` |
| `1SPE-DERGLOBAL-EV-B:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EV-B.sympy.json` |
| `1SPE-DERGLOBAL-EX-001-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-001-CDP.sympy.json` |
| `1SPE-DERGLOBAL-EX-001:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-001.sympy.json` |
| `1SPE-DERGLOBAL-EX-002-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-002-CDP.sympy.json` |
| `1SPE-DERGLOBAL-EX-002:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-002.sympy.json` |
| `1SPE-DERGLOBAL-EX-003-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-003-CDP.sympy.json` |
| `1SPE-DERGLOBAL-EX-003:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-003.sympy.json` |
| `1SPE-DERGLOBAL-EX-004-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-004-CDP.sympy.json` |
| `1SPE-DERGLOBAL-EX-004:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-004.sympy.json` |
| `1SPE-DERGLOBAL-EX-005:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-005.sympy.json` |
| `1SPE-DERGLOBAL-EX-006:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-006.sympy.json` |
| `1SPE-DERGLOBAL-EX-007:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-007.sympy.json` |
| `1SPE-DERGLOBAL-EX-008:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-008.sympy.json` |
| `1SPE-DERGLOBAL-EX-009:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-009.sympy.json` |
| `1SPE-DERGLOBAL-EX-010:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-010.sympy.json` |
| `1SPE-DERGLOBAL-EX-011-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-011-CDP.sympy.json` |
| `1SPE-DERGLOBAL-EX-011:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-011.sympy.json` |
| `1SPE-DERGLOBAL-EX-012-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-012-CDP.sympy.json` |
| `1SPE-DERGLOBAL-EX-012:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-012.sympy.json` |
| `1SPE-DERGLOBAL-EX-013-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-013-CDP.sympy.json` |
| `1SPE-DERGLOBAL-EX-013:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-013.sympy.json` |
| `1SPE-DERGLOBAL-EX-014-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-014-CDP.sympy.json` |
| `1SPE-DERGLOBAL-EX-014:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-014.sympy.json` |
| `1SPE-DERGLOBAL-EX-015:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-015.sympy.json` |
| `1SPE-DERGLOBAL-EX-016:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-016.sympy.json` |
| `1SPE-DERGLOBAL-EX-017:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-017.sympy.json` |
| `1SPE-DERGLOBAL-EX-018:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-018.sympy.json` |
| `1SPE-DERGLOBAL-EX-019:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-019.sympy.json` |
| `1SPE-DERGLOBAL-EX-020:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-020.sympy.json` |
| `1SPE-DERGLOBAL-EX-021-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-021-CDP.sympy.json` |
| `1SPE-DERGLOBAL-EX-021:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-021.sympy.json` |
| `1SPE-DERGLOBAL-EX-022-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-022-CDP.sympy.json` |
| `1SPE-DERGLOBAL-EX-022:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-022.sympy.json` |
| `1SPE-DERGLOBAL-EX-023-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-023-CDP.sympy.json` |
| `1SPE-DERGLOBAL-EX-023:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-023.sympy.json` |
| `1SPE-DERGLOBAL-EX-024-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-024-CDP.sympy.json` |
| `1SPE-DERGLOBAL-EX-024:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-024.sympy.json` |
| `1SPE-DERGLOBAL-EX-025:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-025.sympy.json` |
| `1SPE-DERGLOBAL-EX-026:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-026.sympy.json` |
| `1SPE-DERGLOBAL-EX-027:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-027.sympy.json` |
| `1SPE-DERGLOBAL-EX-028:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-028.sympy.json` |
| `1SPE-DERGLOBAL-EX-029:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-029.sympy.json` |
| `1SPE-DERGLOBAL-EX-030:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-030.sympy.json` |
| `1SPE-DERGLOBAL-EX-031-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-031-CDP.sympy.json` |
| `1SPE-DERGLOBAL-EX-031:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-031.sympy.json` |
| `1SPE-DERGLOBAL-EX-032-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-032-CDP.sympy.json` |
| `1SPE-DERGLOBAL-EX-032:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-032.sympy.json` |
| `1SPE-DERGLOBAL-EX-033-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-033-CDP.sympy.json` |
| `1SPE-DERGLOBAL-EX-033:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-033.sympy.json` |
| `1SPE-DERGLOBAL-EX-034-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-034-CDP.sympy.json` |
| `1SPE-DERGLOBAL-EX-034:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-034.sympy.json` |
| `1SPE-DERGLOBAL-EX-035:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-035.sympy.json` |
| `1SPE-DERGLOBAL-EX-036:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-036.sympy.json` |
| `1SPE-DERGLOBAL-EX-037:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-037.sympy.json` |
| `1SPE-DERGLOBAL-EX-038:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-038.sympy.json` |
| `1SPE-DERGLOBAL-EX-039:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-039.sympy.json` |
| `1SPE-DERGLOBAL-EX-040:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-040.sympy.json` |
| `1SPE-DERGLOBAL-EX-041-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-041-CDP.sympy.json` |
| `1SPE-DERGLOBAL-EX-041:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-041.sympy.json` |
| `1SPE-DERGLOBAL-EX-042-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-042-CDP.sympy.json` |
| `1SPE-DERGLOBAL-EX-042:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-042.sympy.json` |
| `1SPE-DERGLOBAL-EX-043:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-043.sympy.json` |
| `1SPE-DERGLOBAL-EX-044:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-044.sympy.json` |
| `1SPE-DERGLOBAL-EX-045:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-045.sympy.json` |
| `1SPE-DERGLOBAL-EX-046:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-046.sympy.json` |
| `1SPE-DERGLOBAL-EX-047:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-047.sympy.json` |
| `1SPE-DERGLOBAL-EX-048:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-048.sympy.json` |
| `1SPE-DERGLOBAL-EX-049:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-049.sympy.json` |
| `1SPE-DERGLOBAL-EX-050:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-050.sympy.json` |
| `1SPE-DERGLOBAL-EX-051:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-051.sympy.json` |
| `1SPE-DERGLOBAL-EX-052:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-052.sympy.json` |
| `1SPE-DERGLOBAL-EX-053:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERGLOBAL-EX-053.sympy.json` |
| `1SPE-DERIVATION-GLOBAL-FR-R1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERIVATION-GLOBAL-FR-R1.sympy.json` |
| `1SPE-DERIVATION-GLOBAL-FR-R2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERIVATION-GLOBAL-FR-R2.sympy.json` |
| `1SPE-DERIVATION-GLOBAL-FR-R3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERIVATION-GLOBAL-FR-R3.sympy.json` |
| `1SPE-DERIVATION-GLOBAL-FR-R4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERIVATION-GLOBAL-FR-R4.sympy.json` |
| `1SPE-DERIVATION-GLOBAL-FR-R5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERIVATION-GLOBAL-FR-R5.sympy.json` |
| `1SPE-DERIVATION-GLOBAL-QCM:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERIVATION-GLOBAL-QCM.sympy.json` |
| `1SPE-DERIVATION-GLOBAL-RE-C1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERIVATION-GLOBAL-RE-C1.sympy.json` |
| `1SPE-DERIVATION-GLOBAL-RE-C2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERIVATION-GLOBAL-RE-C2.sympy.json` |
| `1SPE-DERIVATION-GLOBAL-RE-C3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERIVATION-GLOBAL-RE-C3.sympy.json` |
| `1SPE-DERIVATION-GLOBAL-RE-C4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERIVATION-GLOBAL-RE-C4.sympy.json` |
| `1SPE-DERIVATION-GLOBAL-RE-C5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-GLOBAL/validations/1SPE-DERIVATION-GLOBAL-RE-C5.sympy.json` |
| `CHAPITRES/1SPE-DERIVATION-GLOBAL/VALIDATIONS/COURS-03:PROOF` | `validation` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/validations/cours-03.png` |
| `CHAPITRES/1SPE-DERIVATION-GLOBAL/VALIDATIONS/EXERCICES-15:PROOF` | `validation` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/validations/exercices-15.png` |
| `CHAPITRES/1SPE-DERIVATION-GLOBAL/VALIDATIONS/OUVERTURE-01:PROOF` | `validation` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/validations/ouverture-01.png` |
| `CHAPITRES/1SPE-DERIVATION-GLOBAL/VALIDATIONS/QCM-35:PROOF` | `validation` | `keep` | `chapitres/1SPE-DERIVATION-GLOBAL/validations/qcm-35.png` |
| `CHAPITRES/1SPE-DERIVATION-LOCAL/LOT-0_RAPPORT` | `report` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/LOT-0_rapport.md` |
| `CHAPITRES/1SPE-DERIVATION-LOCAL/LOT-1_RAPPORT` | `report` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/LOT-1_rapport.md` |
| `CHAPITRES/1SPE-DERIVATION-LOCAL/LOT-2_RAPPORT` | `report` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/LOT-2_rapport.md` |
| `CHAPITRES/1SPE-DERIVATION-LOCAL/LOT-3_RAPPORT` | `report` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/LOT-3_rapport.md` |
| `CHAPITRES/1SPE-DERIVATION-LOCAL/LOT-4_RAPPORT` | `report` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/LOT-4_rapport.md` |
| `CHAPITRES/1SPE-DERIVATION-LOCAL/LOT-5_RAPPORT` | `report` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/LOT-5_rapport.md` |
| `CHAPITRES/1SPE-DERIVATION-LOCAL/LOT-6_RAPPORT` | `report` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/LOT-6_rapport.md` |
| `CHAPITRES/1SPE-DERIVATION-LOCAL/LOT-7_RAPPORT` | `report` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/LOT-7_rapport.md` |
| `CHAPITRES/1SPE-DERIVATION-LOCAL/CONTRAT` | `chapter_contract` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/contrat.yaml` |
| `1SPE-DERLOCAL-CO-001` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-001.tex` |
| `1SPE-DERLOCAL-CO-002` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-002.tex` |
| `1SPE-DERLOCAL-CO-003` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-003.tex` |
| `1SPE-DERLOCAL-CO-004` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-004.tex` |
| `1SPE-DERLOCAL-CO-005` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-005.tex` |
| `1SPE-DERLOCAL-CO-006` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-006.tex` |
| `1SPE-DERLOCAL-CO-007` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-007.tex` |
| `1SPE-DERLOCAL-CO-008` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-008.tex` |
| `1SPE-DERLOCAL-CO-009` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-009.tex` |
| `1SPE-DERLOCAL-CO-010` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-010.tex` |
| `1SPE-DERLOCAL-CO-011` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-011.tex` |
| `1SPE-DERLOCAL-CO-012` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-012.tex` |
| `1SPE-DERLOCAL-CO-013` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-013.tex` |
| `1SPE-DERLOCAL-CO-014` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-014.tex` |
| `1SPE-DERLOCAL-CO-015` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-015.tex` |
| `1SPE-DERLOCAL-CO-016` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-016.tex` |
| `1SPE-DERLOCAL-CO-017` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-017.tex` |
| `1SPE-DERLOCAL-CO-018` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-018.tex` |
| `1SPE-DERLOCAL-CO-019` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-019.tex` |
| `1SPE-DERLOCAL-CO-020` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-020.tex` |
| `1SPE-DERLOCAL-CO-021` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-021.tex` |
| `1SPE-DERLOCAL-CO-022` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-022.tex` |
| `1SPE-DERLOCAL-CO-023` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-023.tex` |
| `1SPE-DERLOCAL-CO-024` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-024.tex` |
| `1SPE-DERLOCAL-CO-025` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-025.tex` |
| `1SPE-DERLOCAL-CO-026` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-026.tex` |
| `1SPE-DERLOCAL-CO-027` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-027.tex` |
| `1SPE-DERLOCAL-CO-028` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-028.tex` |
| `1SPE-DERLOCAL-CO-029` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-029.tex` |
| `1SPE-DERLOCAL-CO-030` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-030.tex` |
| `1SPE-DERLOCAL-CO-031` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-031.tex` |
| `1SPE-DERLOCAL-CO-032` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-032.tex` |
| `1SPE-DERLOCAL-CO-033` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-033.tex` |
| `1SPE-DERLOCAL-CO-034` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-034.tex` |
| `1SPE-DERLOCAL-CO-035` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-035.tex` |
| `1SPE-DERLOCAL-CO-036` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-036.tex` |
| `1SPE-DERLOCAL-CO-037` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-037.tex` |
| `1SPE-DERLOCAL-CO-038` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-038.tex` |
| `1SPE-DERLOCAL-CO-039` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-039.tex` |
| `1SPE-DERLOCAL-CO-040` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-040.tex` |
| `1SPE-DERLOCAL-CO-041` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-041.tex` |
| `1SPE-DERLOCAL-CO-042` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-042.tex` |
| `1SPE-DERLOCAL-CO-043` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-043.tex` |
| `1SPE-DERLOCAL-CO-044` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-044.tex` |
| `1SPE-DERLOCAL-CO-045` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-045.tex` |
| `1SPE-DERLOCAL-CO-046` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-046.tex` |
| `1SPE-DERLOCAL-CO-047` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-047.tex` |
| `1SPE-DERLOCAL-CO-048` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-048.tex` |
| `1SPE-DERLOCAL-CO-049` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-049.tex` |
| `1SPE-DERLOCAL-CO-050` | `solution` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/corriges/1SPE-DERLOCAL-CO-050.tex` |
| `1SPE-DERLOCAL-TD-CONTEXTE` | `transversal` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/cours/07_td_contextualise.tex` |
| `1SPE-DERLOCAL-TD-FILROUGE` | `transversal` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/cours/07_td_fil_rouge.tex` |
| `1SPE-DERIVATION-LOCAL-CR-010` | `course` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/cours/10_C1_taux_variation.tex` |
| `1SPE-DERIVATION-LOCAL-CR-011` | `course` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/cours/11_C2_nombre_derive.tex` |
| `1SPE-DERIVATION-LOCAL-CR-012` | `course` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/cours/12_C3_tangente.tex` |
| `1SPE-DERIVATION-LOCAL-CR-013` | `course` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/cours/13_C4_equation_tangente.tex` |
| `1SPE-DERIVATION-LOCAL-CR-014` | `course` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/cours/14_C5_approximation_lineaire.tex` |
| `CHAPITRES/1SPE-DERIVATION-LOCAL/DOSSIER_CURATION` | `chapter_metadata` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/dossier_curation.json` |
| `1SPE-DERLOCAL-EV-A-corrige:SCALE` | `grading_scale` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/evaluations/1SPE-DERLOCAL-EV-A-corrige.tex` |
| `1SPE-DERLOCAL-EV-A` | `assessment` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/evaluations/1SPE-DERLOCAL-EV-A.tex` |
| `1SPE-DERLOCAL-EV-B-corrige:SCALE` | `grading_scale` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/evaluations/1SPE-DERLOCAL-EV-B-corrige.tex` |
| `1SPE-DERLOCAL-EV-B` | `assessment` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/evaluations/1SPE-DERLOCAL-EV-B.tex` |
| `1SPE-DERLOCAL-EX-001-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-001-CDP.tex` |
| `1SPE-DERLOCAL-EX-001` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-001.tex` |
| `1SPE-DERLOCAL-EX-002-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-002-CDP.tex` |
| `1SPE-DERLOCAL-EX-002` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-002.tex` |
| `1SPE-DERLOCAL-EX-003` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-003.tex` |
| `1SPE-DERLOCAL-EX-004` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-004.tex` |
| `1SPE-DERLOCAL-EX-005` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-005.tex` |
| `1SPE-DERLOCAL-EX-006` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-006.tex` |
| `1SPE-DERLOCAL-EX-007-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-007-CDP.tex` |
| `1SPE-DERLOCAL-EX-007` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-007.tex` |
| `1SPE-DERLOCAL-EX-008-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-008-CDP.tex` |
| `1SPE-DERLOCAL-EX-008` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-008.tex` |
| `1SPE-DERLOCAL-EX-009` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-009.tex` |
| `1SPE-DERLOCAL-EX-010` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-010.tex` |
| `1SPE-DERLOCAL-EX-011` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-011.tex` |
| `1SPE-DERLOCAL-EX-012` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-012.tex` |
| `1SPE-DERLOCAL-EX-013-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-013-CDP.tex` |
| `1SPE-DERLOCAL-EX-013` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-013.tex` |
| `1SPE-DERLOCAL-EX-014-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-014-CDP.tex` |
| `1SPE-DERLOCAL-EX-014` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-014.tex` |
| `1SPE-DERLOCAL-EX-015` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-015.tex` |
| `1SPE-DERLOCAL-EX-016` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-016.tex` |
| `1SPE-DERLOCAL-EX-017` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-017.tex` |
| `1SPE-DERLOCAL-EX-018` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-018.tex` |
| `1SPE-DERLOCAL-EX-019-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-019-CDP.tex` |
| `1SPE-DERLOCAL-EX-019` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-019.tex` |
| `1SPE-DERLOCAL-EX-020-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-020-CDP.tex` |
| `1SPE-DERLOCAL-EX-020` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-020.tex` |
| `1SPE-DERLOCAL-EX-021` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-021.tex` |
| `1SPE-DERLOCAL-EX-022` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-022.tex` |
| `1SPE-DERLOCAL-EX-023` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-023.tex` |
| `1SPE-DERLOCAL-EX-024` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-024.tex` |
| `1SPE-DERLOCAL-EX-025-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-025-CDP.tex` |
| `1SPE-DERLOCAL-EX-025` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-025.tex` |
| `1SPE-DERLOCAL-EX-026-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-026-CDP.tex` |
| `1SPE-DERLOCAL-EX-026` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-026.tex` |
| `1SPE-DERLOCAL-EX-027` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-027.tex` |
| `1SPE-DERLOCAL-EX-028` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-028.tex` |
| `1SPE-DERLOCAL-EX-029` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-029.tex` |
| `1SPE-DERLOCAL-EX-030` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-030.tex` |
| `1SPE-DERLOCAL-EX-031-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-031-CDP.tex` |
| `1SPE-DERLOCAL-EX-031` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-031.tex` |
| `1SPE-DERLOCAL-EX-032-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-032-CDP.tex` |
| `1SPE-DERLOCAL-EX-032` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-032.tex` |
| `1SPE-DERLOCAL-EX-033-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-033-CDP.tex` |
| `1SPE-DERLOCAL-EX-033` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-033.tex` |
| `1SPE-DERLOCAL-EX-034-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-034-CDP.tex` |
| `1SPE-DERLOCAL-EX-034` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-034.tex` |
| `1SPE-DERLOCAL-EX-035-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-035-CDP.tex` |
| `1SPE-DERLOCAL-EX-035` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-035.tex` |
| `1SPE-DERLOCAL-EX-036-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-036-CDP.tex` |
| `1SPE-DERLOCAL-EX-036` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-036.tex` |
| `1SPE-DERLOCAL-EX-037-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-037-CDP.tex` |
| `1SPE-DERLOCAL-EX-037` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-037.tex` |
| `1SPE-DERLOCAL-EX-038-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-038-CDP.tex` |
| `1SPE-DERLOCAL-EX-038` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-038.tex` |
| `1SPE-DERLOCAL-EX-039` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-039.tex` |
| `1SPE-DERLOCAL-EX-040` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-040.tex` |
| `1SPE-DERLOCAL-EX-041` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-041.tex` |
| `1SPE-DERLOCAL-EX-042` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-042.tex` |
| `1SPE-DERLOCAL-EX-043` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-043.tex` |
| `1SPE-DERLOCAL-EX-044` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-044.tex` |
| `1SPE-DERLOCAL-EX-045` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-045.tex` |
| `1SPE-DERLOCAL-EX-046` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-046.tex` |
| `1SPE-DERLOCAL-EX-047` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-047.tex` |
| `1SPE-DERLOCAL-EX-048` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-048.tex` |
| `1SPE-DERLOCAL-EX-049` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-049.tex` |
| `1SPE-DERLOCAL-EX-050` | `exercise` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-050.tex` |
| `1SPE-DERLOCAL-ME-001` | `method` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/methodes/1SPE-DERLOCAL-ME-001.tex` |
| `1SPE-DERLOCAL-ME-002` | `method` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/methodes/1SPE-DERLOCAL-ME-002.tex` |
| `1SPE-DERLOCAL-ME-003` | `method` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/methodes/1SPE-DERLOCAL-ME-003.tex` |
| `1SPE-DERLOCAL-ME-004` | `method` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/methodes/1SPE-DERLOCAL-ME-004.tex` |
| `1SPE-DERLOCAL-ME-005` | `method` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/methodes/1SPE-DERLOCAL-ME-005.tex` |
| `CHAPITRES/1SPE-DERIVATION-LOCAL/QCM/1SPE-DERIVATION-LOCAL-QCM:JSON` | `qcm_json` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/qcm/1SPE-DERIVATION-LOCAL-QCM.json` |
| `1SPE-DERIVATION-LOCAL-QCM:TEX` | `qcm_tex` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/qcm/1SPE-DERIVATION-LOCAL-QCM.tex` |
| `1SPE-DERIVATION-LOCAL-FR-R1` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/remediation/1SPE-DERIVATION-LOCAL-FR-R1.tex` |
| `1SPE-DERIVATION-LOCAL-FR-R2` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/remediation/1SPE-DERIVATION-LOCAL-FR-R2.tex` |
| `1SPE-DERIVATION-LOCAL-FR-R3` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/remediation/1SPE-DERIVATION-LOCAL-FR-R3.tex` |
| `1SPE-DERIVATION-LOCAL-FR-R4` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/remediation/1SPE-DERIVATION-LOCAL-FR-R4.tex` |
| `1SPE-DERIVATION-LOCAL-FR-R5` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/remediation/1SPE-DERIVATION-LOCAL-FR-R5.tex` |
| `1SPE-DERIVATION-LOCAL-RE-C1` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/remediation/1SPE-DERIVATION-LOCAL-RE-C1.tex` |
| `1SPE-DERIVATION-LOCAL-RE-C2` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/remediation/1SPE-DERIVATION-LOCAL-RE-C2.tex` |
| `1SPE-DERIVATION-LOCAL-RE-C3` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/remediation/1SPE-DERIVATION-LOCAL-RE-C3.tex` |
| `1SPE-DERIVATION-LOCAL-RE-C4` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/remediation/1SPE-DERIVATION-LOCAL-RE-C4.tex` |
| `1SPE-DERIVATION-LOCAL-RE-C5` | `remediation` | `keep` | `chapitres/1SPE-DERIVATION-LOCAL/remediation/1SPE-DERIVATION-LOCAL-RE-C5.tex` |
| `07_td_contextualise:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/07_td_contextualise.sympy.json` |
| `07_td_fil_rouge:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/07_td_fil_rouge.sympy.json` |
| `10_C1_taux_variation:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/10_C1_taux_variation.similarity.json` |
| `10_C1_taux_variation:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/10_C1_taux_variation.sympy.json` |
| `11_C2_nombre_derive:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/11_C2_nombre_derive.similarity.json` |
| `11_C2_nombre_derive:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/11_C2_nombre_derive.sympy.json` |
| `12_C3_tangente:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/12_C3_tangente.similarity.json` |
| `12_C3_tangente:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/12_C3_tangente.sympy.json` |
| `13_C4_equation_tangente:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/13_C4_equation_tangente.similarity.json` |
| `13_C4_equation_tangente:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/13_C4_equation_tangente.sympy.json` |
| `14_C5_approximation_lineaire:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/14_C5_approximation_lineaire.similarity.json` |
| `14_C5_approximation_lineaire:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/14_C5_approximation_lineaire.sympy.json` |
| `1SPE-DERIVATION-LOCAL-CR-013:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERIVATION-LOCAL-CR-013.adversarial.json` |
| `1SPE-DERIVATION-LOCAL-FR-R1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERIVATION-LOCAL-FR-R1.sympy.json` |
| `1SPE-DERIVATION-LOCAL-FR-R2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERIVATION-LOCAL-FR-R2.sympy.json` |
| `1SPE-DERIVATION-LOCAL-FR-R3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERIVATION-LOCAL-FR-R3.sympy.json` |
| `1SPE-DERIVATION-LOCAL-FR-R4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERIVATION-LOCAL-FR-R4.sympy.json` |
| `1SPE-DERIVATION-LOCAL-FR-R5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERIVATION-LOCAL-FR-R5.sympy.json` |
| `1SPE-DERIVATION-LOCAL-QCM:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERIVATION-LOCAL-QCM.sympy.json` |
| `1SPE-DERIVATION-LOCAL-RE-C1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERIVATION-LOCAL-RE-C1.sympy.json` |
| `1SPE-DERIVATION-LOCAL-RE-C2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERIVATION-LOCAL-RE-C2.sympy.json` |
| `1SPE-DERIVATION-LOCAL-RE-C3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERIVATION-LOCAL-RE-C3.sympy.json` |
| `1SPE-DERIVATION-LOCAL-RE-C4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERIVATION-LOCAL-RE-C4.sympy.json` |
| `1SPE-DERIVATION-LOCAL-RE-C5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERIVATION-LOCAL-RE-C5.sympy.json` |
| `1SPE-DERLOCAL-CO-001:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-001.similarity.json` |
| `1SPE-DERLOCAL-CO-001:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-001.sympy.json` |
| `1SPE-DERLOCAL-CO-002:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-002.sympy.json` |
| `1SPE-DERLOCAL-CO-003:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-003.sympy.json` |
| `1SPE-DERLOCAL-CO-004:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-004.sympy.json` |
| `1SPE-DERLOCAL-CO-005:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-005.sympy.json` |
| `1SPE-DERLOCAL-CO-006:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-006.sympy.json` |
| `1SPE-DERLOCAL-CO-007:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-007.sympy.json` |
| `1SPE-DERLOCAL-CO-008:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-008.sympy.json` |
| `1SPE-DERLOCAL-CO-009:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-009.sympy.json` |
| `1SPE-DERLOCAL-CO-010:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-010.sympy.json` |
| `1SPE-DERLOCAL-CO-011:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-011.sympy.json` |
| `1SPE-DERLOCAL-CO-012:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-012.sympy.json` |
| `1SPE-DERLOCAL-CO-013:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-013.sympy.json` |
| `1SPE-DERLOCAL-CO-014:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-014.sympy.json` |
| `1SPE-DERLOCAL-CO-015:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-015.sympy.json` |
| `1SPE-DERLOCAL-CO-016:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-016.sympy.json` |
| `1SPE-DERLOCAL-CO-017:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-017.sympy.json` |
| `1SPE-DERLOCAL-CO-018:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-018.sympy.json` |
| `1SPE-DERLOCAL-CO-019:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-019.sympy.json` |
| `1SPE-DERLOCAL-CO-020:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-020.sympy.json` |
| `1SPE-DERLOCAL-CO-021:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-021.sympy.json` |
| `1SPE-DERLOCAL-CO-022:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-022.sympy.json` |
| `1SPE-DERLOCAL-CO-023:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-023.sympy.json` |
| `1SPE-DERLOCAL-CO-024:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-024.sympy.json` |
| `1SPE-DERLOCAL-CO-025:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-025.sympy.json` |
| `1SPE-DERLOCAL-CO-026:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-026.sympy.json` |
| `1SPE-DERLOCAL-CO-027:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-027.sympy.json` |
| `1SPE-DERLOCAL-CO-028:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-028.sympy.json` |
| `1SPE-DERLOCAL-CO-029:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-029.sympy.json` |
| `1SPE-DERLOCAL-CO-030:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-030.sympy.json` |
| `1SPE-DERLOCAL-CO-031:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-031.sympy.json` |
| `1SPE-DERLOCAL-CO-032:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-032.sympy.json` |
| `1SPE-DERLOCAL-CO-033:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-033.sympy.json` |
| `1SPE-DERLOCAL-CO-034:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-034.sympy.json` |
| `1SPE-DERLOCAL-CO-035:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-035.sympy.json` |
| `1SPE-DERLOCAL-CO-036:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-036.sympy.json` |
| `1SPE-DERLOCAL-CO-037:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-037.sympy.json` |
| `1SPE-DERLOCAL-CO-038:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-038.sympy.json` |
| `1SPE-DERLOCAL-CO-039:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-039.sympy.json` |
| `1SPE-DERLOCAL-CO-040:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-040.sympy.json` |
| `1SPE-DERLOCAL-CO-041:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-041.sympy.json` |
| `1SPE-DERLOCAL-CO-042:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-042.sympy.json` |
| `1SPE-DERLOCAL-CO-043:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-043.sympy.json` |
| `1SPE-DERLOCAL-CO-044:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-044.sympy.json` |
| `1SPE-DERLOCAL-CO-045:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-045.sympy.json` |
| `1SPE-DERLOCAL-CO-046:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-046.sympy.json` |
| `1SPE-DERLOCAL-CO-047:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-047.sympy.json` |
| `1SPE-DERLOCAL-CO-048:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-048.sympy.json` |
| `1SPE-DERLOCAL-CO-049:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-049.sympy.json` |
| `1SPE-DERLOCAL-CO-050:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-CO-050.sympy.json` |
| `1SPE-DERLOCAL-EV-A-corrige:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EV-A-corrige.sympy.json` |
| `1SPE-DERLOCAL-EV-A:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EV-A.sympy.json` |
| `1SPE-DERLOCAL-EV-B-corrige:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EV-B-corrige.sympy.json` |
| `1SPE-DERLOCAL-EV-B:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EV-B.sympy.json` |
| `1SPE-DERLOCAL-EX-001-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-001-CDP.sympy.json` |
| `1SPE-DERLOCAL-EX-001:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-001.similarity.json` |
| `1SPE-DERLOCAL-EX-001:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-001.sympy.json` |
| `1SPE-DERLOCAL-EX-002-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-002-CDP.sympy.json` |
| `1SPE-DERLOCAL-EX-002:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-002.sympy.json` |
| `1SPE-DERLOCAL-EX-003:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-003.sympy.json` |
| `1SPE-DERLOCAL-EX-004:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-004.sympy.json` |
| `1SPE-DERLOCAL-EX-005:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-005.sympy.json` |
| `1SPE-DERLOCAL-EX-006:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-006.sympy.json` |
| `1SPE-DERLOCAL-EX-007-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-007-CDP.sympy.json` |
| `1SPE-DERLOCAL-EX-007:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-007.sympy.json` |
| `1SPE-DERLOCAL-EX-008-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-008-CDP.sympy.json` |
| `1SPE-DERLOCAL-EX-008:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-008.sympy.json` |
| `1SPE-DERLOCAL-EX-009:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-009.sympy.json` |
| `1SPE-DERLOCAL-EX-010:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-010.sympy.json` |
| `1SPE-DERLOCAL-EX-011:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-011.sympy.json` |
| `1SPE-DERLOCAL-EX-012:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-012.sympy.json` |
| `1SPE-DERLOCAL-EX-013-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-013-CDP.sympy.json` |
| `1SPE-DERLOCAL-EX-013:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-013.sympy.json` |
| `1SPE-DERLOCAL-EX-014-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-014-CDP.sympy.json` |
| `1SPE-DERLOCAL-EX-014:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-014.sympy.json` |
| `1SPE-DERLOCAL-EX-015:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-015.sympy.json` |
| `1SPE-DERLOCAL-EX-016:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-016.sympy.json` |
| `1SPE-DERLOCAL-EX-017:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-017.sympy.json` |
| `1SPE-DERLOCAL-EX-018:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-018.sympy.json` |
| `1SPE-DERLOCAL-EX-019-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-019-CDP.sympy.json` |
| `1SPE-DERLOCAL-EX-019:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-019.sympy.json` |
| `1SPE-DERLOCAL-EX-020-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-020-CDP.sympy.json` |
| `1SPE-DERLOCAL-EX-020:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-020.sympy.json` |
| `1SPE-DERLOCAL-EX-021:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-021.sympy.json` |
| `1SPE-DERLOCAL-EX-022:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-022.sympy.json` |
| `1SPE-DERLOCAL-EX-023:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-023.sympy.json` |
| `1SPE-DERLOCAL-EX-024:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-024.sympy.json` |
| `1SPE-DERLOCAL-EX-025-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-025-CDP.sympy.json` |
| `1SPE-DERLOCAL-EX-025:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-025.sympy.json` |
| `1SPE-DERLOCAL-EX-026-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-026-CDP.sympy.json` |
| `1SPE-DERLOCAL-EX-026:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-026.sympy.json` |
| `1SPE-DERLOCAL-EX-027:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-027.sympy.json` |
| `1SPE-DERLOCAL-EX-028:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-028.sympy.json` |
| `1SPE-DERLOCAL-EX-029:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-029.sympy.json` |
| `1SPE-DERLOCAL-EX-030:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-030.sympy.json` |
| `1SPE-DERLOCAL-EX-031-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-031-CDP.sympy.json` |
| `1SPE-DERLOCAL-EX-031:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-031.sympy.json` |
| `1SPE-DERLOCAL-EX-032-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-032-CDP.sympy.json` |
| `1SPE-DERLOCAL-EX-032:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-032.sympy.json` |
| `1SPE-DERLOCAL-EX-033-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-033-CDP.sympy.json` |
| `1SPE-DERLOCAL-EX-033:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-033.sympy.json` |
| `1SPE-DERLOCAL-EX-034-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-034-CDP.sympy.json` |
| `1SPE-DERLOCAL-EX-034:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-034.sympy.json` |
| `1SPE-DERLOCAL-EX-035-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-035-CDP.sympy.json` |
| `1SPE-DERLOCAL-EX-035:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-035.sympy.json` |
| `1SPE-DERLOCAL-EX-036-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-036-CDP.sympy.json` |
| `1SPE-DERLOCAL-EX-036:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-036.sympy.json` |
| `1SPE-DERLOCAL-EX-037-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-037-CDP.sympy.json` |
| `1SPE-DERLOCAL-EX-037:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-037.sympy.json` |
| `1SPE-DERLOCAL-EX-038-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-038-CDP.sympy.json` |
| `1SPE-DERLOCAL-EX-038:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-038.sympy.json` |
| `1SPE-DERLOCAL-EX-039:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-039.sympy.json` |
| `1SPE-DERLOCAL-EX-040:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-040.sympy.json` |
| `1SPE-DERLOCAL-EX-041:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-041.sympy.json` |
| `1SPE-DERLOCAL-EX-042:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-042.sympy.json` |
| `1SPE-DERLOCAL-EX-043:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-043.sympy.json` |
| `1SPE-DERLOCAL-EX-044:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-044.sympy.json` |
| `1SPE-DERLOCAL-EX-045:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-045.sympy.json` |
| `1SPE-DERLOCAL-EX-046:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-046.sympy.json` |
| `1SPE-DERLOCAL-EX-047:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-047.sympy.json` |
| `1SPE-DERLOCAL-EX-048:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-048.sympy.json` |
| `1SPE-DERLOCAL-EX-049:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-049.sympy.json` |
| `1SPE-DERLOCAL-EX-050:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-EX-050.sympy.json` |
| `1SPE-DERLOCAL-ME-001:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-ME-001.adversarial.json` |
| `1SPE-DERLOCAL-ME-001:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-ME-001.similarity.json` |
| `1SPE-DERLOCAL-ME-002:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-ME-002.adversarial.json` |
| `1SPE-DERLOCAL-ME-002:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-ME-002.similarity.json` |
| `1SPE-DERLOCAL-ME-003:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-ME-003.adversarial.json` |
| `1SPE-DERLOCAL-ME-003:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-ME-003.similarity.json` |
| `1SPE-DERLOCAL-ME-004:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-ME-004.adversarial.json` |
| `1SPE-DERLOCAL-ME-004:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-ME-004.similarity.json` |
| `1SPE-DERLOCAL-ME-005:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-ME-005.adversarial.json` |
| `1SPE-DERLOCAL-ME-005:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/1SPE-DERLOCAL-ME-005.similarity.json` |
| `1SPE-DERIVATION-LOCAL-CONTRAT:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/contrat.adversarial.json` |
| `1SPE-DERIVATION-LOCAL-CURATION:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-DERIVATION-LOCAL/validations/curation.adversarial.json` |
| `CHAPITRES/1SPE-EXPONENTIELLE/LOT-0_RAPPORT` | `report` | `keep` | `chapitres/1SPE-EXPONENTIELLE/LOT-0_rapport.md` |
| `CHAPITRES/1SPE-EXPONENTIELLE/LOT-1_RAPPORT` | `report` | `keep` | `chapitres/1SPE-EXPONENTIELLE/LOT-1_rapport.md` |
| `CHAPITRES/1SPE-EXPONENTIELLE/LOT-2_RAPPORT` | `report` | `keep` | `chapitres/1SPE-EXPONENTIELLE/LOT-2_rapport.md` |
| `CHAPITRES/1SPE-EXPONENTIELLE/LOT-4_RAPPORT` | `report` | `keep` | `chapitres/1SPE-EXPONENTIELLE/LOT-4_rapport.md` |
| `CHAPITRES/1SPE-EXPONENTIELLE/LOT-5_RAPPORT` | `report` | `keep` | `chapitres/1SPE-EXPONENTIELLE/LOT-5_rapport.md` |
| `CHAPITRES/1SPE-EXPONENTIELLE/LOT-6_RAPPORT` | `report` | `keep` | `chapitres/1SPE-EXPONENTIELLE/LOT-6_rapport.md` |
| `CHAPITRES/1SPE-EXPONENTIELLE/LOT-7_RAPPORT` | `report` | `keep` | `chapitres/1SPE-EXPONENTIELLE/LOT-7_rapport.md` |
| `CHAPITRES/1SPE-EXPONENTIELLE/CONTRAT` | `chapter_contract` | `keep` | `chapitres/1SPE-EXPONENTIELLE/contrat.yaml` |
| `1SPE-EXPO-CO-001` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-001.tex` |
| `1SPE-EXPO-CO-002` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-002.tex` |
| `1SPE-EXPO-CO-003` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-003.tex` |
| `1SPE-EXPO-CO-004` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-004.tex` |
| `1SPE-EXPO-CO-005` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-005.tex` |
| `1SPE-EXPO-CO-006` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-006.tex` |
| `1SPE-EXPO-CO-007` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-007.tex` |
| `1SPE-EXPO-CO-008` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-008.tex` |
| `1SPE-EXPO-CO-009` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-009.tex` |
| `1SPE-EXPO-CO-010` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-010.tex` |
| `1SPE-EXPO-CO-011` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-011.tex` |
| `1SPE-EXPO-CO-012` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-012.tex` |
| `1SPE-EXPO-CO-013` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-013.tex` |
| `1SPE-EXPO-CO-014` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-014.tex` |
| `1SPE-EXPO-CO-015` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-015.tex` |
| `1SPE-EXPO-CO-016` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-016.tex` |
| `1SPE-EXPO-CO-017` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-017.tex` |
| `1SPE-EXPO-CO-018` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-018.tex` |
| `1SPE-EXPO-CO-019` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-019.tex` |
| `1SPE-EXPO-CO-020` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-020.tex` |
| `1SPE-EXPO-CO-021` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-021.tex` |
| `1SPE-EXPO-CO-022` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-022.tex` |
| `1SPE-EXPO-CO-023` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-023.tex` |
| `1SPE-EXPO-CO-024` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-024.tex` |
| `1SPE-EXPO-CO-025` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-025.tex` |
| `1SPE-EXPO-CO-026` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-026.tex` |
| `1SPE-EXPO-CO-027` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-027.tex` |
| `1SPE-EXPO-CO-028` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-028.tex` |
| `1SPE-EXPO-CO-029` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-029.tex` |
| `1SPE-EXPO-CO-030` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-030.tex` |
| `1SPE-EXPO-CO-031` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-031.tex` |
| `1SPE-EXPO-CO-032` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-032.tex` |
| `1SPE-EXPO-CO-033` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-033.tex` |
| `1SPE-EXPO-CO-034` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-034.tex` |
| `1SPE-EXPO-CO-035` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-035.tex` |
| `1SPE-EXPO-CO-036` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-036.tex` |
| `1SPE-EXPO-CO-037` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-037.tex` |
| `1SPE-EXPO-CO-038` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-038.tex` |
| `1SPE-EXPO-CO-039` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-039.tex` |
| `1SPE-EXPO-CO-040` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-040.tex` |
| `1SPE-EXPO-CO-041` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-041.tex` |
| `1SPE-EXPO-CO-042` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-042.tex` |
| `1SPE-EXPO-CO-043` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-043.tex` |
| `1SPE-EXPO-CO-044` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-044.tex` |
| `1SPE-EXPO-CO-045` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-045.tex` |
| `1SPE-EXPO-CO-046` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-046.tex` |
| `1SPE-EXPO-CO-047` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-047.tex` |
| `1SPE-EXPO-CO-048` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-048.tex` |
| `1SPE-EXPO-CO-049` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-049.tex` |
| `1SPE-EXPO-CO-050` | `solution` | `keep` | `chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-050.tex` |
| `1SPE-EXPO-TD-CONTEXTUALISE` | `transversal` | `keep` | `chapitres/1SPE-EXPONENTIELLE/cours/07_td_contextualise.tex` |
| `1SPE-EXPO-TD-FIL-ROUGE` | `transversal` | `keep` | `chapitres/1SPE-EXPONENTIELLE/cours/07_td_fil_rouge.tex` |
| `1SPE-EXPO-COURS-C1` | `course` | `keep` | `chapitres/1SPE-EXPONENTIELLE/cours/10_C1_definition_exponentielle.tex` |
| `1SPE-EXPO-COURS-C2` | `course` | `keep` | `chapitres/1SPE-EXPONENTIELLE/cours/11_C2_proprietes_algebriques.tex` |
| `1SPE-EXPO-COURS-C3` | `course` | `keep` | `chapitres/1SPE-EXPONENTIELLE/cours/12_C3_variations_limites.tex` |
| `1SPE-EXPO-COURS-C4` | `course` | `keep` | `chapitres/1SPE-EXPONENTIELLE/cours/13_C4_derivation_eu.tex` |
| `1SPE-EXPO-COURS-C5` | `course` | `keep` | `chapitres/1SPE-EXPONENTIELLE/cours/14_C5_equations_inequations.tex` |
| `CHAPITRES/1SPE-EXPONENTIELLE/DOSSIER_CURATION` | `chapter_metadata` | `keep` | `chapitres/1SPE-EXPONENTIELLE/dossier_curation.json` |
| `1SPE-EXPO-EV-A-corrige:SCALE` | `grading_scale` | `keep` | `chapitres/1SPE-EXPONENTIELLE/evaluations/1SPE-EXPO-EV-A-corrige.tex` |
| `1SPE-EXPO-EV-A` | `assessment` | `keep` | `chapitres/1SPE-EXPONENTIELLE/evaluations/1SPE-EXPO-EV-A.tex` |
| `1SPE-EXPO-EV-B-corrige:SCALE` | `grading_scale` | `keep` | `chapitres/1SPE-EXPONENTIELLE/evaluations/1SPE-EXPO-EV-B-corrige.tex` |
| `1SPE-EXPO-EV-B` | `assessment` | `keep` | `chapitres/1SPE-EXPONENTIELLE/evaluations/1SPE-EXPO-EV-B.tex` |
| `1SPE-EXPO-EX-001-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-001-CDP.tex` |
| `1SPE-EXPO-EX-001` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-001.tex` |
| `1SPE-EXPO-EX-002-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-002-CDP.tex` |
| `1SPE-EXPO-EX-002` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-002.tex` |
| `1SPE-EXPO-EX-003-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-003-CDP.tex` |
| `1SPE-EXPO-EX-003` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-003.tex` |
| `1SPE-EXPO-EX-004-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-004-CDP.tex` |
| `1SPE-EXPO-EX-004` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-004.tex` |
| `1SPE-EXPO-EX-005` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-005.tex` |
| `1SPE-EXPO-EX-006` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-006.tex` |
| `1SPE-EXPO-EX-007` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-007.tex` |
| `1SPE-EXPO-EX-008` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-008.tex` |
| `1SPE-EXPO-EX-009` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-009.tex` |
| `1SPE-EXPO-EX-010` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-010.tex` |
| `1SPE-EXPO-EX-011-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-011-CDP.tex` |
| `1SPE-EXPO-EX-011` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-011.tex` |
| `1SPE-EXPO-EX-012-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-012-CDP.tex` |
| `1SPE-EXPO-EX-012` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-012.tex` |
| `1SPE-EXPO-EX-013-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-013-CDP.tex` |
| `1SPE-EXPO-EX-013` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-013.tex` |
| `1SPE-EXPO-EX-014-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-014-CDP.tex` |
| `1SPE-EXPO-EX-014` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-014.tex` |
| `1SPE-EXPO-EX-015` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-015.tex` |
| `1SPE-EXPO-EX-016` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-016.tex` |
| `1SPE-EXPO-EX-017` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-017.tex` |
| `1SPE-EXPO-EX-018` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-018.tex` |
| `1SPE-EXPO-EX-019` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-019.tex` |
| `1SPE-EXPO-EX-020` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-020.tex` |
| `1SPE-EXPO-EX-021-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-021-CDP.tex` |
| `1SPE-EXPO-EX-021` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-021.tex` |
| `1SPE-EXPO-EX-022-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-022-CDP.tex` |
| `1SPE-EXPO-EX-022` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-022.tex` |
| `1SPE-EXPO-EX-023-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-023-CDP.tex` |
| `1SPE-EXPO-EX-023` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-023.tex` |
| `1SPE-EXPO-EX-024-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-024-CDP.tex` |
| `1SPE-EXPO-EX-024` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-024.tex` |
| `1SPE-EXPO-EX-025` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-025.tex` |
| `1SPE-EXPO-EX-026` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-026.tex` |
| `1SPE-EXPO-EX-027` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-027.tex` |
| `1SPE-EXPO-EX-028` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-028.tex` |
| `1SPE-EXPO-EX-029` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-029.tex` |
| `1SPE-EXPO-EX-030` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-030.tex` |
| `1SPE-EXPO-EX-031-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-031-CDP.tex` |
| `1SPE-EXPO-EX-031` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-031.tex` |
| `1SPE-EXPO-EX-032-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-032-CDP.tex` |
| `1SPE-EXPO-EX-032` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-032.tex` |
| `1SPE-EXPO-EX-033-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-033-CDP.tex` |
| `1SPE-EXPO-EX-033` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-033.tex` |
| `1SPE-EXPO-EX-034-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-034-CDP.tex` |
| `1SPE-EXPO-EX-034` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-034.tex` |
| `1SPE-EXPO-EX-035` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-035.tex` |
| `1SPE-EXPO-EX-036` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-036.tex` |
| `1SPE-EXPO-EX-037` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-037.tex` |
| `1SPE-EXPO-EX-038` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-038.tex` |
| `1SPE-EXPO-EX-039` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-039.tex` |
| `1SPE-EXPO-EX-040` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-040.tex` |
| `1SPE-EXPO-EX-041-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-041-CDP.tex` |
| `1SPE-EXPO-EX-041` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-041.tex` |
| `1SPE-EXPO-EX-042-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-042-CDP.tex` |
| `1SPE-EXPO-EX-042` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-042.tex` |
| `1SPE-EXPO-EX-043` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-043.tex` |
| `1SPE-EXPO-EX-044` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-044.tex` |
| `1SPE-EXPO-EX-045` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-045.tex` |
| `1SPE-EXPO-EX-046` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-046.tex` |
| `1SPE-EXPO-EX-047` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-047.tex` |
| `1SPE-EXPO-EX-048` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-048.tex` |
| `1SPE-EXPO-EX-049` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-049.tex` |
| `1SPE-EXPO-EX-050` | `exercise` | `keep` | `chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-050.tex` |
| `1SPE-EXPO-ME-001` | `method` | `keep` | `chapitres/1SPE-EXPONENTIELLE/methodes/1SPE-EXPO-ME-001.tex` |
| `1SPE-EXPO-ME-002` | `method` | `keep` | `chapitres/1SPE-EXPONENTIELLE/methodes/1SPE-EXPO-ME-002.tex` |
| `1SPE-EXPO-ME-003` | `method` | `keep` | `chapitres/1SPE-EXPONENTIELLE/methodes/1SPE-EXPO-ME-003.tex` |
| `1SPE-EXPO-ME-004` | `method` | `keep` | `chapitres/1SPE-EXPONENTIELLE/methodes/1SPE-EXPO-ME-004.tex` |
| `1SPE-EXPO-ME-005` | `method` | `keep` | `chapitres/1SPE-EXPONENTIELLE/methodes/1SPE-EXPO-ME-005.tex` |
| `CHAPITRES/1SPE-EXPONENTIELLE/QCM/1SPE-EXPONENTIELLE-QCM:JSON` | `qcm_json` | `keep` | `chapitres/1SPE-EXPONENTIELLE/qcm/1SPE-EXPONENTIELLE-QCM.json` |
| `1SPE-EXPONENTIELLE-QCM:TEX` | `qcm_tex` | `keep` | `chapitres/1SPE-EXPONENTIELLE/qcm/1SPE-EXPONENTIELLE-QCM.tex` |
| `1SPE-EXPONENTIELLE-FR-R1` | `remediation` | `keep` | `chapitres/1SPE-EXPONENTIELLE/remediation/1SPE-EXPONENTIELLE-FR-R1.tex` |
| `1SPE-EXPONENTIELLE-FR-R2` | `remediation` | `keep` | `chapitres/1SPE-EXPONENTIELLE/remediation/1SPE-EXPONENTIELLE-FR-R2.tex` |
| `1SPE-EXPONENTIELLE-FR-R3` | `remediation` | `keep` | `chapitres/1SPE-EXPONENTIELLE/remediation/1SPE-EXPONENTIELLE-FR-R3.tex` |
| `1SPE-EXPONENTIELLE-FR-R4` | `remediation` | `keep` | `chapitres/1SPE-EXPONENTIELLE/remediation/1SPE-EXPONENTIELLE-FR-R4.tex` |
| `1SPE-EXPONENTIELLE-FR-R5` | `remediation` | `keep` | `chapitres/1SPE-EXPONENTIELLE/remediation/1SPE-EXPONENTIELLE-FR-R5.tex` |
| `1SPE-EXPONENTIELLE-RE-C1` | `remediation` | `keep` | `chapitres/1SPE-EXPONENTIELLE/remediation/1SPE-EXPONENTIELLE-RE-C1.tex` |
| `1SPE-EXPONENTIELLE-RE-C2` | `remediation` | `keep` | `chapitres/1SPE-EXPONENTIELLE/remediation/1SPE-EXPONENTIELLE-RE-C2.tex` |
| `1SPE-EXPONENTIELLE-RE-C3` | `remediation` | `keep` | `chapitres/1SPE-EXPONENTIELLE/remediation/1SPE-EXPONENTIELLE-RE-C3.tex` |
| `1SPE-EXPONENTIELLE-RE-C4` | `remediation` | `keep` | `chapitres/1SPE-EXPONENTIELLE/remediation/1SPE-EXPONENTIELLE-RE-C4.tex` |
| `1SPE-EXPONENTIELLE-RE-C5` | `remediation` | `keep` | `chapitres/1SPE-EXPONENTIELLE/remediation/1SPE-EXPONENTIELLE-RE-C5.tex` |
| `07_td_contextualise:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/07_td_contextualise.sympy.json` |
| `07_td_fil_rouge:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/07_td_fil_rouge.sympy.json` |
| `10_C1_definition_exponentielle:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/10_C1_definition_exponentielle.sympy.json` |
| `11_C2_proprietes_algebriques:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/11_C2_proprietes_algebriques.sympy.json` |
| `12_C3_variations_limites:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/12_C3_variations_limites.sympy.json` |
| `13_C4_derivation_eu:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/13_C4_derivation_eu.sympy.json` |
| `14_C5_equations_inequations:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/14_C5_equations_inequations.sympy.json` |
| `1SPE-EXPO-CO-001:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-001.sympy.json` |
| `1SPE-EXPO-CO-002:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-002.sympy.json` |
| `1SPE-EXPO-CO-003:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-003.sympy.json` |
| `1SPE-EXPO-CO-004:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-004.sympy.json` |
| `1SPE-EXPO-CO-005:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-005.sympy.json` |
| `1SPE-EXPO-CO-006:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-006.sympy.json` |
| `1SPE-EXPO-CO-007:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-007.sympy.json` |
| `1SPE-EXPO-CO-008:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-008.sympy.json` |
| `1SPE-EXPO-CO-009:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-009.sympy.json` |
| `1SPE-EXPO-CO-010:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-010.sympy.json` |
| `1SPE-EXPO-CO-011:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-011.sympy.json` |
| `1SPE-EXPO-CO-012:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-012.sympy.json` |
| `1SPE-EXPO-CO-013:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-013.sympy.json` |
| `1SPE-EXPO-CO-014:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-014.sympy.json` |
| `1SPE-EXPO-CO-015:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-015.sympy.json` |
| `1SPE-EXPO-CO-016:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-016.sympy.json` |
| `1SPE-EXPO-CO-017:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-017.sympy.json` |
| `1SPE-EXPO-CO-018:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-018.sympy.json` |
| `1SPE-EXPO-CO-019:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-019.sympy.json` |
| `1SPE-EXPO-CO-020:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-020.sympy.json` |
| `1SPE-EXPO-CO-021:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-021.sympy.json` |
| `1SPE-EXPO-CO-022:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-022.sympy.json` |
| `1SPE-EXPO-CO-023:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-023.sympy.json` |
| `1SPE-EXPO-CO-024:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-024.sympy.json` |
| `1SPE-EXPO-CO-025:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-025.sympy.json` |
| `1SPE-EXPO-CO-026:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-026.sympy.json` |
| `1SPE-EXPO-CO-027:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-027.sympy.json` |
| `1SPE-EXPO-CO-028:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-028.sympy.json` |
| `1SPE-EXPO-CO-029:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-029.sympy.json` |
| `1SPE-EXPO-CO-030:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-030.sympy.json` |
| `1SPE-EXPO-CO-031:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-031.sympy.json` |
| `1SPE-EXPO-CO-032:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-032.sympy.json` |
| `1SPE-EXPO-CO-033:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-033.sympy.json` |
| `1SPE-EXPO-CO-034:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-034.sympy.json` |
| `1SPE-EXPO-CO-035:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-035.sympy.json` |
| `1SPE-EXPO-CO-036:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-036.sympy.json` |
| `1SPE-EXPO-CO-037:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-037.sympy.json` |
| `1SPE-EXPO-CO-038:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-038.sympy.json` |
| `1SPE-EXPO-CO-039:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-039.sympy.json` |
| `1SPE-EXPO-CO-040:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-040.sympy.json` |
| `1SPE-EXPO-CO-041:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-041.sympy.json` |
| `1SPE-EXPO-CO-042:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-042.sympy.json` |
| `1SPE-EXPO-CO-043:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-043.sympy.json` |
| `1SPE-EXPO-CO-044:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-044.sympy.json` |
| `1SPE-EXPO-CO-045:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-045.sympy.json` |
| `1SPE-EXPO-CO-046:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-046.sympy.json` |
| `1SPE-EXPO-CO-047:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-047.sympy.json` |
| `1SPE-EXPO-CO-048:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-048.sympy.json` |
| `1SPE-EXPO-CO-049:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-049.sympy.json` |
| `1SPE-EXPO-CO-050:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-CO-050.sympy.json` |
| `1SPE-EXPO-EV-A-corrige:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EV-A-corrige.sympy.json` |
| `1SPE-EXPO-EV-A:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EV-A.sympy.json` |
| `1SPE-EXPO-EV-B-corrige:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EV-B-corrige.sympy.json` |
| `1SPE-EXPO-EV-B:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EV-B.sympy.json` |
| `1SPE-EXPO-EX-001-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-001-CDP.sympy.json` |
| `1SPE-EXPO-EX-001:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-001.sympy.json` |
| `1SPE-EXPO-EX-002-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-002-CDP.sympy.json` |
| `1SPE-EXPO-EX-002:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-002.sympy.json` |
| `1SPE-EXPO-EX-003-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-003-CDP.sympy.json` |
| `1SPE-EXPO-EX-003:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-003.sympy.json` |
| `1SPE-EXPO-EX-004-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-004-CDP.sympy.json` |
| `1SPE-EXPO-EX-004:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-004.sympy.json` |
| `1SPE-EXPO-EX-005:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-005.sympy.json` |
| `1SPE-EXPO-EX-006:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-006.sympy.json` |
| `1SPE-EXPO-EX-007:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-007.sympy.json` |
| `1SPE-EXPO-EX-008:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-008.sympy.json` |
| `1SPE-EXPO-EX-009:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-009.sympy.json` |
| `1SPE-EXPO-EX-010:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-010.sympy.json` |
| `1SPE-EXPO-EX-011-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-011-CDP.sympy.json` |
| `1SPE-EXPO-EX-011:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-011.sympy.json` |
| `1SPE-EXPO-EX-012-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-012-CDP.sympy.json` |
| `1SPE-EXPO-EX-012:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-012.sympy.json` |
| `1SPE-EXPO-EX-013-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-013-CDP.sympy.json` |
| `1SPE-EXPO-EX-013:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-013.sympy.json` |
| `1SPE-EXPO-EX-014-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-014-CDP.sympy.json` |
| `1SPE-EXPO-EX-014:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-014.sympy.json` |
| `1SPE-EXPO-EX-015:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-015.sympy.json` |
| `1SPE-EXPO-EX-016:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-016.sympy.json` |
| `1SPE-EXPO-EX-017:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-017.sympy.json` |
| `1SPE-EXPO-EX-018:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-018.sympy.json` |
| `1SPE-EXPO-EX-019:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-019.sympy.json` |
| `1SPE-EXPO-EX-020:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-020.sympy.json` |
| `1SPE-EXPO-EX-021-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-021-CDP.sympy.json` |
| `1SPE-EXPO-EX-021:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-021.sympy.json` |
| `1SPE-EXPO-EX-022-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-022-CDP.sympy.json` |
| `1SPE-EXPO-EX-022:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-022.sympy.json` |
| `1SPE-EXPO-EX-023-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-023-CDP.sympy.json` |
| `1SPE-EXPO-EX-023:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-023.sympy.json` |
| `1SPE-EXPO-EX-024-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-024-CDP.sympy.json` |
| `1SPE-EXPO-EX-024:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-024.sympy.json` |
| `1SPE-EXPO-EX-025:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-025.sympy.json` |
| `1SPE-EXPO-EX-026:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-026.sympy.json` |
| `1SPE-EXPO-EX-027:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-027.sympy.json` |
| `1SPE-EXPO-EX-028:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-028.sympy.json` |
| `1SPE-EXPO-EX-029:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-029.sympy.json` |
| `1SPE-EXPO-EX-030:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-030.sympy.json` |
| `1SPE-EXPO-EX-031-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-031-CDP.sympy.json` |
| `1SPE-EXPO-EX-031:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-031.sympy.json` |
| `1SPE-EXPO-EX-032-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-032-CDP.sympy.json` |
| `1SPE-EXPO-EX-032:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-032.sympy.json` |
| `1SPE-EXPO-EX-033-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-033-CDP.sympy.json` |
| `1SPE-EXPO-EX-033:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-033.sympy.json` |
| `1SPE-EXPO-EX-034-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-034-CDP.sympy.json` |
| `1SPE-EXPO-EX-034:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-034.sympy.json` |
| `1SPE-EXPO-EX-035:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-035.sympy.json` |
| `1SPE-EXPO-EX-036:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-036.sympy.json` |
| `1SPE-EXPO-EX-037:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-037.sympy.json` |
| `1SPE-EXPO-EX-038:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-038.sympy.json` |
| `1SPE-EXPO-EX-039:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-039.sympy.json` |
| `1SPE-EXPO-EX-040:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-040.sympy.json` |
| `1SPE-EXPO-EX-041-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-041-CDP.sympy.json` |
| `1SPE-EXPO-EX-041:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-041.sympy.json` |
| `1SPE-EXPO-EX-042-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-042-CDP.sympy.json` |
| `1SPE-EXPO-EX-042:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-042.sympy.json` |
| `1SPE-EXPO-EX-043:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-043.sympy.json` |
| `1SPE-EXPO-EX-044:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-044.sympy.json` |
| `1SPE-EXPO-EX-045:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-045.sympy.json` |
| `1SPE-EXPO-EX-046:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-046.sympy.json` |
| `1SPE-EXPO-EX-047:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-047.sympy.json` |
| `1SPE-EXPO-EX-048:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-048.sympy.json` |
| `1SPE-EXPO-EX-049:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-049.sympy.json` |
| `1SPE-EXPO-EX-050:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPO-EX-050.sympy.json` |
| `1SPE-EXPONENTIELLE-FR-R1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPONENTIELLE-FR-R1.sympy.json` |
| `1SPE-EXPONENTIELLE-FR-R2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPONENTIELLE-FR-R2.sympy.json` |
| `1SPE-EXPONENTIELLE-FR-R3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPONENTIELLE-FR-R3.sympy.json` |
| `1SPE-EXPONENTIELLE-FR-R4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPONENTIELLE-FR-R4.sympy.json` |
| `1SPE-EXPONENTIELLE-FR-R5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPONENTIELLE-FR-R5.sympy.json` |
| `1SPE-EXPONENTIELLE-QCM:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPONENTIELLE-QCM.sympy.json` |
| `1SPE-EXPONENTIELLE-RE-C1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPONENTIELLE-RE-C1.sympy.json` |
| `1SPE-EXPONENTIELLE-RE-C2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPONENTIELLE-RE-C2.sympy.json` |
| `1SPE-EXPONENTIELLE-RE-C3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPONENTIELLE-RE-C3.sympy.json` |
| `1SPE-EXPONENTIELLE-RE-C4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPONENTIELLE-RE-C4.sympy.json` |
| `1SPE-EXPONENTIELLE-RE-C5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-EXPONENTIELLE/validations/1SPE-EXPONENTIELLE-RE-C5.sympy.json` |
| `CHAPITRES/1SPE-GEOMETRIE-REPEREE/LOT-0_RAPPORT` | `report` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/LOT-0_rapport.md` |
| `CHAPITRES/1SPE-GEOMETRIE-REPEREE/LOT-1_RAPPORT` | `report` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/LOT-1_rapport.md` |
| `CHAPITRES/1SPE-GEOMETRIE-REPEREE/LOT-2_RAPPORT` | `report` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/LOT-2_rapport.md` |
| `CHAPITRES/1SPE-GEOMETRIE-REPEREE/LOT-3_RAPPORT` | `report` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/LOT-3_rapport.md` |
| `CHAPITRES/1SPE-GEOMETRIE-REPEREE/LOT-4_RAPPORT` | `report` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/LOT-4_rapport.md` |
| `CHAPITRES/1SPE-GEOMETRIE-REPEREE/LOT-5_RAPPORT` | `report` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/LOT-5_rapport.md` |
| `CHAPITRES/1SPE-GEOMETRIE-REPEREE/LOT-6_RAPPORT` | `report` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/LOT-6_rapport.md` |
| `CHAPITRES/1SPE-GEOMETRIE-REPEREE/LOT-7_RAPPORT` | `report` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/LOT-7_rapport.md` |
| `CHAPITRES/1SPE-GEOMETRIE-REPEREE/CONTRAT` | `chapter_contract` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/contrat.yaml` |
| `1SPE-GEOREP-CO-001` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-001.tex` |
| `1SPE-GEOREP-CO-002` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-002.tex` |
| `1SPE-GEOREP-CO-003` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-003.tex` |
| `1SPE-GEOREP-CO-004` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-004.tex` |
| `1SPE-GEOREP-CO-005` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-005.tex` |
| `1SPE-GEOREP-CO-006` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-006.tex` |
| `1SPE-GEOREP-CO-007` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-007.tex` |
| `1SPE-GEOREP-CO-008` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-008.tex` |
| `1SPE-GEOREP-CO-009` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-009.tex` |
| `1SPE-GEOREP-CO-010` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-010.tex` |
| `1SPE-GEOREP-CO-011` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-011.tex` |
| `1SPE-GEOREP-CO-012` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-012.tex` |
| `1SPE-GEOREP-CO-013` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-013.tex` |
| `1SPE-GEOREP-CO-014` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-014.tex` |
| `1SPE-GEOREP-CO-015` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-015.tex` |
| `1SPE-GEOREP-CO-016` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-016.tex` |
| `1SPE-GEOREP-CO-017` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-017.tex` |
| `1SPE-GEOREP-CO-018` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-018.tex` |
| `1SPE-GEOREP-CO-019` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-019.tex` |
| `1SPE-GEOREP-CO-020` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-020.tex` |
| `1SPE-GEOREP-CO-021` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-021.tex` |
| `1SPE-GEOREP-CO-022` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-022.tex` |
| `1SPE-GEOREP-CO-023` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-023.tex` |
| `1SPE-GEOREP-CO-024` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-024.tex` |
| `1SPE-GEOREP-CO-025` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-025.tex` |
| `1SPE-GEOREP-CO-026` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-026.tex` |
| `1SPE-GEOREP-CO-027` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-027.tex` |
| `1SPE-GEOREP-CO-028` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-028.tex` |
| `1SPE-GEOREP-CO-029` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-029.tex` |
| `1SPE-GEOREP-CO-030` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-030.tex` |
| `1SPE-GEOREP-CO-031` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-031.tex` |
| `1SPE-GEOREP-CO-032` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-032.tex` |
| `1SPE-GEOREP-CO-033` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-033.tex` |
| `1SPE-GEOREP-CO-034` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-034.tex` |
| `1SPE-GEOREP-CO-035` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-035.tex` |
| `1SPE-GEOREP-CO-036` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-036.tex` |
| `1SPE-GEOREP-CO-037` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-037.tex` |
| `1SPE-GEOREP-CO-038` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-038.tex` |
| `1SPE-GEOREP-CO-039` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-039.tex` |
| `1SPE-GEOREP-CO-040` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-040.tex` |
| `1SPE-GEOREP-CO-041` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-041.tex` |
| `1SPE-GEOREP-CO-042` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-042.tex` |
| `1SPE-GEOREP-CO-043` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-043.tex` |
| `1SPE-GEOREP-CO-044` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-044.tex` |
| `1SPE-GEOREP-CO-045` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-045.tex` |
| `1SPE-GEOREP-CO-046` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-046.tex` |
| `1SPE-GEOREP-CO-047` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-047.tex` |
| `1SPE-GEOREP-CO-048` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-048.tex` |
| `1SPE-GEOREP-CO-049` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-049.tex` |
| `1SPE-GEOREP-CO-050` | `solution` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/corriges/1SPE-GEOREP-CO-050.tex` |
| `1SPE-GEOREP-COURS-00` | `course` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/cours/00_ouverture.tex` |
| `1SPE-GEOREP-COURS-01` | `course` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/cours/01_diagnostic.tex` |
| `1SPE-GEOREP-COURS-07-TC` | `transversal` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/cours/07_td_contextualise.tex` |
| `1SPE-GEOREP-COURS-07-FR` | `transversal` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/cours/07_td_fil_rouge.tex` |
| `1SPE-GEOREP-CR-010` | `course` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/cours/10_C1_equation_cartesienne_droite.tex` |
| `1SPE-GEOREP-CR-011` | `course` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/cours/11_C2_vecteur_normal.tex` |
| `1SPE-GEOREP-CR-012` | `course` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/cours/12_C3_equation_cercle.tex` |
| `1SPE-GEOREP-CR-013` | `course` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/cours/13_C4_positions_relatives.tex` |
| `1SPE-GEOREP-CR-014` | `course` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/cours/14_C5_problemes_repere.tex` |
| `CHAPITRES/1SPE-GEOMETRIE-REPEREE/DOSSIER_CURATION` | `chapter_metadata` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/dossier_curation.json` |
| `1SPE-GEOREP-EV-A-corrige:SCALE` | `grading_scale` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/evaluations/1SPE-GEOREP-EV-A-corrige.tex` |
| `1SPE-GEOREP-EV-A` | `assessment` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/evaluations/1SPE-GEOREP-EV-A.tex` |
| `1SPE-GEOREP-EV-B-corrige:SCALE` | `grading_scale` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/evaluations/1SPE-GEOREP-EV-B-corrige.tex` |
| `1SPE-GEOREP-EV-B` | `assessment` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/evaluations/1SPE-GEOREP-EV-B.tex` |
| `1SPE-GEOREP-EX-001-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-001-CDP.tex` |
| `1SPE-GEOREP-EX-001` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-001.tex` |
| `1SPE-GEOREP-EX-002-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-002-CDP.tex` |
| `1SPE-GEOREP-EX-002` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-002.tex` |
| `1SPE-GEOREP-EX-003-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-003-CDP.tex` |
| `1SPE-GEOREP-EX-003` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-003.tex` |
| `1SPE-GEOREP-EX-004-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-004-CDP.tex` |
| `1SPE-GEOREP-EX-004` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-004.tex` |
| `1SPE-GEOREP-EX-005` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-005.tex` |
| `1SPE-GEOREP-EX-006` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-006.tex` |
| `1SPE-GEOREP-EX-007` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-007.tex` |
| `1SPE-GEOREP-EX-008` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-008.tex` |
| `1SPE-GEOREP-EX-009` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-009.tex` |
| `1SPE-GEOREP-EX-010` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-010.tex` |
| `1SPE-GEOREP-EX-011-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-011-CDP.tex` |
| `1SPE-GEOREP-EX-011` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-011.tex` |
| `1SPE-GEOREP-EX-012-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-012-CDP.tex` |
| `1SPE-GEOREP-EX-012` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-012.tex` |
| `1SPE-GEOREP-EX-013-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-013-CDP.tex` |
| `1SPE-GEOREP-EX-013` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-013.tex` |
| `1SPE-GEOREP-EX-014-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-014-CDP.tex` |
| `1SPE-GEOREP-EX-014` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-014.tex` |
| `1SPE-GEOREP-EX-015` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-015.tex` |
| `1SPE-GEOREP-EX-016` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-016.tex` |
| `1SPE-GEOREP-EX-017` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-017.tex` |
| `1SPE-GEOREP-EX-018` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-018.tex` |
| `1SPE-GEOREP-EX-019` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-019.tex` |
| `1SPE-GEOREP-EX-020` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-020.tex` |
| `1SPE-GEOREP-EX-021-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-021-CDP.tex` |
| `1SPE-GEOREP-EX-021` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-021.tex` |
| `1SPE-GEOREP-EX-022-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-022-CDP.tex` |
| `1SPE-GEOREP-EX-022` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-022.tex` |
| `1SPE-GEOREP-EX-023-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-023-CDP.tex` |
| `1SPE-GEOREP-EX-023` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-023.tex` |
| `1SPE-GEOREP-EX-024-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-024-CDP.tex` |
| `1SPE-GEOREP-EX-024` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-024.tex` |
| `1SPE-GEOREP-EX-025` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-025.tex` |
| `1SPE-GEOREP-EX-026` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-026.tex` |
| `1SPE-GEOREP-EX-027` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-027.tex` |
| `1SPE-GEOREP-EX-028` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-028.tex` |
| `1SPE-GEOREP-EX-029` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-029.tex` |
| `1SPE-GEOREP-EX-030` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-030.tex` |
| `1SPE-GEOREP-EX-031-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-031-CDP.tex` |
| `1SPE-GEOREP-EX-031` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-031.tex` |
| `1SPE-GEOREP-EX-032-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-032-CDP.tex` |
| `1SPE-GEOREP-EX-032` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-032.tex` |
| `1SPE-GEOREP-EX-033-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-033-CDP.tex` |
| `1SPE-GEOREP-EX-033` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-033.tex` |
| `1SPE-GEOREP-EX-034-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-034-CDP.tex` |
| `1SPE-GEOREP-EX-034` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-034.tex` |
| `1SPE-GEOREP-EX-035` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-035.tex` |
| `1SPE-GEOREP-EX-036` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-036.tex` |
| `1SPE-GEOREP-EX-037` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-037.tex` |
| `1SPE-GEOREP-EX-038` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-038.tex` |
| `1SPE-GEOREP-EX-039` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-039.tex` |
| `1SPE-GEOREP-EX-040` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-040.tex` |
| `1SPE-GEOREP-EX-041-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-041-CDP.tex` |
| `1SPE-GEOREP-EX-041` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-041.tex` |
| `1SPE-GEOREP-EX-042-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-042-CDP.tex` |
| `1SPE-GEOREP-EX-042` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-042.tex` |
| `1SPE-GEOREP-EX-043` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-043.tex` |
| `1SPE-GEOREP-EX-044` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-044.tex` |
| `1SPE-GEOREP-EX-045` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-045.tex` |
| `1SPE-GEOREP-EX-046` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-046.tex` |
| `1SPE-GEOREP-EX-047` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-047.tex` |
| `1SPE-GEOREP-EX-048` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-048.tex` |
| `1SPE-GEOREP-EX-049` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-049.tex` |
| `1SPE-GEOREP-EX-050` | `exercise` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-050.tex` |
| `1SPE-GEOREP-ME-001` | `method` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/methodes/1SPE-GEOREP-ME-001.tex` |
| `1SPE-GEOREP-ME-002` | `method` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/methodes/1SPE-GEOREP-ME-002.tex` |
| `1SPE-GEOREP-ME-003` | `method` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/methodes/1SPE-GEOREP-ME-003.tex` |
| `1SPE-GEOREP-ME-004` | `method` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/methodes/1SPE-GEOREP-ME-004.tex` |
| `1SPE-GEOREP-ME-005` | `method` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/methodes/1SPE-GEOREP-ME-005.tex` |
| `CHAPITRES/1SPE-GEOMETRIE-REPEREE/QCM/1SPE-GEOREP-QCM:JSON` | `qcm_json` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/qcm/1SPE-GEOREP-QCM.json` |
| `1SPE-GEOREP-QCM:TEX` | `qcm_tex` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/qcm/1SPE-GEOREP-QCM.tex` |
| `1SPE-GEOREP-FR-R1` | `remediation` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/remediation/1SPE-GEOREP-FR-R1.tex` |
| `1SPE-GEOREP-FR-R2` | `remediation` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/remediation/1SPE-GEOREP-FR-R2.tex` |
| `1SPE-GEOREP-FR-R3` | `remediation` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/remediation/1SPE-GEOREP-FR-R3.tex` |
| `1SPE-GEOREP-FR-R4` | `remediation` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/remediation/1SPE-GEOREP-FR-R4.tex` |
| `1SPE-GEOREP-FR-R5` | `remediation` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/remediation/1SPE-GEOREP-FR-R5.tex` |
| `1SPE-GEOREP-RE-C1` | `remediation` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/remediation/1SPE-GEOREP-RE-C1.tex` |
| `1SPE-GEOREP-RE-C2` | `remediation` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/remediation/1SPE-GEOREP-RE-C2.tex` |
| `1SPE-GEOREP-RE-C3` | `remediation` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/remediation/1SPE-GEOREP-RE-C3.tex` |
| `1SPE-GEOREP-RE-C4` | `remediation` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/remediation/1SPE-GEOREP-RE-C4.tex` |
| `1SPE-GEOREP-RE-C5` | `remediation` | `keep` | `chapitres/1SPE-GEOMETRIE-REPEREE/remediation/1SPE-GEOREP-RE-C5.tex` |
| `00_ouverture:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/00_ouverture.sympy.json` |
| `01_diagnostic:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/01_diagnostic.sympy.json` |
| `07_td_contextualise:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/07_td_contextualise.sympy.json` |
| `07_td_fil_rouge:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/07_td_fil_rouge.sympy.json` |
| `10_C1_equation_cartesienne_droite:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/10_C1_equation_cartesienne_droite.sympy.json` |
| `11_C2_vecteur_normal:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/11_C2_vecteur_normal.sympy.json` |
| `12_C3_equation_cercle:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/12_C3_equation_cercle.sympy.json` |
| `13_C4_positions_relatives:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/13_C4_positions_relatives.sympy.json` |
| `14_C5_problemes_repere:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/14_C5_problemes_repere.sympy.json` |
| `1SPE-GEOREP-CO-001:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-001.sympy.json` |
| `1SPE-GEOREP-CO-002:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-002.sympy.json` |
| `1SPE-GEOREP-CO-003:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-003.sympy.json` |
| `1SPE-GEOREP-CO-004:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-004.sympy.json` |
| `1SPE-GEOREP-CO-005:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-005.sympy.json` |
| `1SPE-GEOREP-CO-006:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-006.sympy.json` |
| `1SPE-GEOREP-CO-007:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-007.sympy.json` |
| `1SPE-GEOREP-CO-008:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-008.sympy.json` |
| `1SPE-GEOREP-CO-009:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-009.sympy.json` |
| `1SPE-GEOREP-CO-010:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-010.sympy.json` |
| `1SPE-GEOREP-CO-011:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-011.sympy.json` |
| `1SPE-GEOREP-CO-012:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-012.sympy.json` |
| `1SPE-GEOREP-CO-013:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-013.sympy.json` |
| `1SPE-GEOREP-CO-014:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-014.sympy.json` |
| `1SPE-GEOREP-CO-015:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-015.sympy.json` |
| `1SPE-GEOREP-CO-016:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-016.sympy.json` |
| `1SPE-GEOREP-CO-017:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-017.sympy.json` |
| `1SPE-GEOREP-CO-018:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-018.sympy.json` |
| `1SPE-GEOREP-CO-019:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-019.sympy.json` |
| `1SPE-GEOREP-CO-020:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-020.sympy.json` |
| `1SPE-GEOREP-CO-021:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-021.sympy.json` |
| `1SPE-GEOREP-CO-022:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-022.sympy.json` |
| `1SPE-GEOREP-CO-023:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-023.sympy.json` |
| `1SPE-GEOREP-CO-024:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-024.sympy.json` |
| `1SPE-GEOREP-CO-025:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-025.sympy.json` |
| `1SPE-GEOREP-CO-026:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-026.sympy.json` |
| `1SPE-GEOREP-CO-027:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-027.sympy.json` |
| `1SPE-GEOREP-CO-028:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-028.sympy.json` |
| `1SPE-GEOREP-CO-029:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-029.sympy.json` |
| `1SPE-GEOREP-CO-030:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-030.sympy.json` |
| `1SPE-GEOREP-CO-031:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-031.sympy.json` |
| `1SPE-GEOREP-CO-032:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-032.sympy.json` |
| `1SPE-GEOREP-CO-033:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-033.sympy.json` |
| `1SPE-GEOREP-CO-034:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-034.sympy.json` |
| `1SPE-GEOREP-CO-035:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-035.sympy.json` |
| `1SPE-GEOREP-CO-036:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-036.sympy.json` |
| `1SPE-GEOREP-CO-037:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-037.sympy.json` |
| `1SPE-GEOREP-CO-038:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-038.sympy.json` |
| `1SPE-GEOREP-CO-039:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-039.sympy.json` |
| `1SPE-GEOREP-CO-040:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-040.sympy.json` |
| `1SPE-GEOREP-CO-041:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-041.sympy.json` |
| `1SPE-GEOREP-CO-042:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-042.sympy.json` |
| `1SPE-GEOREP-CO-043:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-043.sympy.json` |
| `1SPE-GEOREP-CO-044:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-044.sympy.json` |
| `1SPE-GEOREP-CO-045:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-045.sympy.json` |
| `1SPE-GEOREP-CO-046:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-046.sympy.json` |
| `1SPE-GEOREP-CO-047:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-047.sympy.json` |
| `1SPE-GEOREP-CO-048:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-048.sympy.json` |
| `1SPE-GEOREP-CO-049:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-049.sympy.json` |
| `1SPE-GEOREP-CO-050:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-CO-050.sympy.json` |
| `1SPE-GEOREP-EV-A-corrige:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EV-A-corrige.sympy.json` |
| `1SPE-GEOREP-EV-A:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EV-A.sympy.json` |
| `1SPE-GEOREP-EV-B-corrige:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EV-B-corrige.sympy.json` |
| `1SPE-GEOREP-EV-B:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EV-B.sympy.json` |
| `1SPE-GEOREP-EX-001-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-001-CDP.sympy.json` |
| `1SPE-GEOREP-EX-001:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-001.sympy.json` |
| `1SPE-GEOREP-EX-002-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-002-CDP.sympy.json` |
| `1SPE-GEOREP-EX-002:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-002.sympy.json` |
| `1SPE-GEOREP-EX-003-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-003-CDP.sympy.json` |
| `1SPE-GEOREP-EX-003:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-003.sympy.json` |
| `1SPE-GEOREP-EX-004-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-004-CDP.sympy.json` |
| `1SPE-GEOREP-EX-004:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-004.sympy.json` |
| `1SPE-GEOREP-EX-005:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-005.sympy.json` |
| `1SPE-GEOREP-EX-006:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-006.sympy.json` |
| `1SPE-GEOREP-EX-007:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-007.sympy.json` |
| `1SPE-GEOREP-EX-008:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-008.sympy.json` |
| `1SPE-GEOREP-EX-009:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-009.sympy.json` |
| `1SPE-GEOREP-EX-010:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-010.sympy.json` |
| `1SPE-GEOREP-EX-011-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-011-CDP.sympy.json` |
| `1SPE-GEOREP-EX-011:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-011.sympy.json` |
| `1SPE-GEOREP-EX-012-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-012-CDP.sympy.json` |
| `1SPE-GEOREP-EX-012:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-012.sympy.json` |
| `1SPE-GEOREP-EX-013-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-013-CDP.sympy.json` |
| `1SPE-GEOREP-EX-013:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-013.sympy.json` |
| `1SPE-GEOREP-EX-014-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-014-CDP.sympy.json` |
| `1SPE-GEOREP-EX-014:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-014.sympy.json` |
| `1SPE-GEOREP-EX-015:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-015.sympy.json` |
| `1SPE-GEOREP-EX-016:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-016.sympy.json` |
| `1SPE-GEOREP-EX-017:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-017.sympy.json` |
| `1SPE-GEOREP-EX-018:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-018.sympy.json` |
| `1SPE-GEOREP-EX-019:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-019.sympy.json` |
| `1SPE-GEOREP-EX-020:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-020.sympy.json` |
| `1SPE-GEOREP-EX-021-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-021-CDP.sympy.json` |
| `1SPE-GEOREP-EX-021:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-021.sympy.json` |
| `1SPE-GEOREP-EX-022-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-022-CDP.sympy.json` |
| `1SPE-GEOREP-EX-022:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-022.sympy.json` |
| `1SPE-GEOREP-EX-023-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-023-CDP.sympy.json` |
| `1SPE-GEOREP-EX-023:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-023.sympy.json` |
| `1SPE-GEOREP-EX-024-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-024-CDP.sympy.json` |
| `1SPE-GEOREP-EX-024:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-024.sympy.json` |
| `1SPE-GEOREP-EX-025:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-025.sympy.json` |
| `1SPE-GEOREP-EX-026:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-026.sympy.json` |
| `1SPE-GEOREP-EX-027:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-027.sympy.json` |
| `1SPE-GEOREP-EX-028:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-028.sympy.json` |
| `1SPE-GEOREP-EX-029:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-029.sympy.json` |
| `1SPE-GEOREP-EX-030:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-030.sympy.json` |
| `1SPE-GEOREP-EX-031-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-031-CDP.sympy.json` |
| `1SPE-GEOREP-EX-031:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-031.sympy.json` |
| `1SPE-GEOREP-EX-032-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-032-CDP.sympy.json` |
| `1SPE-GEOREP-EX-032:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-032.sympy.json` |
| `1SPE-GEOREP-EX-033-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-033-CDP.sympy.json` |
| `1SPE-GEOREP-EX-033:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-033.sympy.json` |
| `1SPE-GEOREP-EX-034-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-034-CDP.sympy.json` |
| `1SPE-GEOREP-EX-034:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-034.sympy.json` |
| `1SPE-GEOREP-EX-035:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-035.sympy.json` |
| `1SPE-GEOREP-EX-036:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-036.sympy.json` |
| `1SPE-GEOREP-EX-037:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-037.sympy.json` |
| `1SPE-GEOREP-EX-038:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-038.sympy.json` |
| `1SPE-GEOREP-EX-039:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-039.sympy.json` |
| `1SPE-GEOREP-EX-040:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-040.sympy.json` |
| `1SPE-GEOREP-EX-041-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-041-CDP.sympy.json` |
| `1SPE-GEOREP-EX-041:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-041.sympy.json` |
| `1SPE-GEOREP-EX-042-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-042-CDP.sympy.json` |
| `1SPE-GEOREP-EX-042:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-042.sympy.json` |
| `1SPE-GEOREP-EX-043:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-043.sympy.json` |
| `1SPE-GEOREP-EX-044:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-044.sympy.json` |
| `1SPE-GEOREP-EX-045:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-045.sympy.json` |
| `1SPE-GEOREP-EX-046:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-046.sympy.json` |
| `1SPE-GEOREP-EX-047:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-047.sympy.json` |
| `1SPE-GEOREP-EX-048:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-048.sympy.json` |
| `1SPE-GEOREP-EX-049:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-049.sympy.json` |
| `1SPE-GEOREP-EX-050:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-EX-050.sympy.json` |
| `1SPE-GEOREP-FR-R1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-FR-R1.sympy.json` |
| `1SPE-GEOREP-FR-R2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-FR-R2.sympy.json` |
| `1SPE-GEOREP-FR-R3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-FR-R3.sympy.json` |
| `1SPE-GEOREP-FR-R4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-FR-R4.sympy.json` |
| `1SPE-GEOREP-FR-R5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-FR-R5.sympy.json` |
| `1SPE-GEOREP-QCM:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-QCM.sympy.json` |
| `1SPE-GEOREP-RE-C1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-RE-C1.sympy.json` |
| `1SPE-GEOREP-RE-C2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-RE-C2.sympy.json` |
| `1SPE-GEOREP-RE-C3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-RE-C3.sympy.json` |
| `1SPE-GEOREP-RE-C4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-RE-C4.sympy.json` |
| `1SPE-GEOREP-RE-C5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-GEOMETRIE-REPEREE/validations/1SPE-GEOREP-RE-C5.sympy.json` |
| `CHAPITRES/1SPE-PROBA-COND/LOT-0_RAPPORT` | `report` | `keep` | `chapitres/1SPE-PROBA-COND/LOT-0_rapport.md` |
| `CHAPITRES/1SPE-PROBA-COND/LOT-1_RAPPORT` | `report` | `keep` | `chapitres/1SPE-PROBA-COND/LOT-1_rapport.md` |
| `CHAPITRES/1SPE-PROBA-COND/LOT-2_RAPPORT` | `report` | `keep` | `chapitres/1SPE-PROBA-COND/LOT-2_rapport.md` |
| `CHAPITRES/1SPE-PROBA-COND/LOT-3_RAPPORT` | `report` | `keep` | `chapitres/1SPE-PROBA-COND/LOT-3_rapport.md` |
| `CHAPITRES/1SPE-PROBA-COND/LOT-4_RAPPORT` | `report` | `keep` | `chapitres/1SPE-PROBA-COND/LOT-4_rapport.md` |
| `CHAPITRES/1SPE-PROBA-COND/LOT-5_RAPPORT` | `report` | `keep` | `chapitres/1SPE-PROBA-COND/LOT-5_rapport.md` |
| `CHAPITRES/1SPE-PROBA-COND/LOT-6_RAPPORT` | `report` | `keep` | `chapitres/1SPE-PROBA-COND/LOT-6_rapport.md` |
| `CHAPITRES/1SPE-PROBA-COND/LOT-7_RAPPORT` | `report` | `keep` | `chapitres/1SPE-PROBA-COND/LOT-7_rapport.md` |
| `CHAPITRES/1SPE-PROBA-COND/CONTRAT` | `chapter_contract` | `keep` | `chapitres/1SPE-PROBA-COND/contrat.yaml` |
| `1SPE-PROBCOND-CO-001` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-001.tex` |
| `1SPE-PROBCOND-CO-002` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-002.tex` |
| `1SPE-PROBCOND-CO-003` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-003.tex` |
| `1SPE-PROBCOND-CO-004` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-004.tex` |
| `1SPE-PROBCOND-CO-005` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-005.tex` |
| `1SPE-PROBCOND-CO-006` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-006.tex` |
| `1SPE-PROBCOND-CO-007` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-007.tex` |
| `1SPE-PROBCOND-CO-008` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-008.tex` |
| `1SPE-PROBCOND-CO-009` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-009.tex` |
| `1SPE-PROBCOND-CO-010` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-010.tex` |
| `1SPE-PROBCOND-CO-011` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-011.tex` |
| `1SPE-PROBCOND-CO-012` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-012.tex` |
| `1SPE-PROBCOND-CO-013` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-013.tex` |
| `1SPE-PROBCOND-CO-014` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-014.tex` |
| `1SPE-PROBCOND-CO-015` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-015.tex` |
| `1SPE-PROBCOND-CO-016` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-016.tex` |
| `1SPE-PROBCOND-CO-017` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-017.tex` |
| `1SPE-PROBCOND-CO-018` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-018.tex` |
| `1SPE-PROBCOND-CO-019` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-019.tex` |
| `1SPE-PROBCOND-CO-020` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-020.tex` |
| `1SPE-PROBCOND-CO-021` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-021.tex` |
| `1SPE-PROBCOND-CO-022` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-022.tex` |
| `1SPE-PROBCOND-CO-023` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-023.tex` |
| `1SPE-PROBCOND-CO-024` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-024.tex` |
| `1SPE-PROBCOND-CO-025` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-025.tex` |
| `1SPE-PROBCOND-CO-026` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-026.tex` |
| `1SPE-PROBCOND-CO-027` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-027.tex` |
| `1SPE-PROBCOND-CO-028` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-028.tex` |
| `1SPE-PROBCOND-CO-029` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-029.tex` |
| `1SPE-PROBCOND-CO-030` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-030.tex` |
| `1SPE-PROBCOND-CO-031` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-031.tex` |
| `1SPE-PROBCOND-CO-032` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-032.tex` |
| `1SPE-PROBCOND-CO-033` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-033.tex` |
| `1SPE-PROBCOND-CO-034` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-034.tex` |
| `1SPE-PROBCOND-CO-035` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-035.tex` |
| `1SPE-PROBCOND-CO-036` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-036.tex` |
| `1SPE-PROBCOND-CO-037` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-037.tex` |
| `1SPE-PROBCOND-CO-038` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-038.tex` |
| `1SPE-PROBCOND-CO-039` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-039.tex` |
| `1SPE-PROBCOND-CO-040` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-040.tex` |
| `1SPE-PROBCOND-CO-041` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-041.tex` |
| `1SPE-PROBCOND-CO-042` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-042.tex` |
| `1SPE-PROBCOND-CO-043` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-043.tex` |
| `1SPE-PROBCOND-CO-044` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-044.tex` |
| `1SPE-PROBCOND-CO-045` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-045.tex` |
| `1SPE-PROBCOND-CO-046` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-046.tex` |
| `1SPE-PROBCOND-CO-047` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-047.tex` |
| `1SPE-PROBCOND-CO-048` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-048.tex` |
| `1SPE-PROBCOND-CO-049` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-049.tex` |
| `1SPE-PROBCOND-CO-050` | `solution` | `keep` | `chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-050.tex` |
| `1SPE-PROBCOND-CR-001` | `course` | `keep` | `chapitres/1SPE-PROBA-COND/cours/01_diagnostic.tex` |
| `1SPE-PROBCOND-TD-001` | `transversal` | `keep` | `chapitres/1SPE-PROBA-COND/cours/07_td_contextualise.tex` |
| `1SPE-PROBCOND-TD-002` | `transversal` | `keep` | `chapitres/1SPE-PROBA-COND/cours/07_td_fil_rouge.tex` |
| `1SPE-PROBCOND-CR-010` | `course` | `keep` | `chapitres/1SPE-PROBA-COND/cours/10_C1_probabilite_conditionnelle.tex` |
| `1SPE-PROBCOND-CR-011` | `course` | `keep` | `chapitres/1SPE-PROBA-COND/cours/11_C2_arbre_pondere.tex` |
| `1SPE-PROBCOND-CR-012` | `course` | `keep` | `chapitres/1SPE-PROBA-COND/cours/12_C3_probabilites_totales.tex` |
| `1SPE-PROBCOND-CR-013` | `course` | `keep` | `chapitres/1SPE-PROBA-COND/cours/13_C4_independance.tex` |
| `1SPE-PROBCOND-CR-014` | `course` | `keep` | `chapitres/1SPE-PROBA-COND/cours/14_C5_problemes_contextualises.tex` |
| `CHAPITRES/1SPE-PROBA-COND/DOSSIER_CURATION` | `chapter_metadata` | `keep` | `chapitres/1SPE-PROBA-COND/dossier_curation.json` |
| `1SPE-PROBCOND-EV-A-corrige:SCALE` | `grading_scale` | `keep` | `chapitres/1SPE-PROBA-COND/evaluations/1SPE-PROBCOND-EV-A-corrige.tex` |
| `1SPE-PROBCOND-EV-A` | `assessment` | `keep` | `chapitres/1SPE-PROBA-COND/evaluations/1SPE-PROBCOND-EV-A.tex` |
| `1SPE-PROBCOND-EV-B-corrige:SCALE` | `grading_scale` | `keep` | `chapitres/1SPE-PROBA-COND/evaluations/1SPE-PROBCOND-EV-B-corrige.tex` |
| `1SPE-PROBCOND-EV-B` | `assessment` | `keep` | `chapitres/1SPE-PROBA-COND/evaluations/1SPE-PROBCOND-EV-B.tex` |
| `1SPE-PROBCOND-EX-001-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-001-CDP.tex` |
| `1SPE-PROBCOND-EX-001` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-001.tex` |
| `1SPE-PROBCOND-EX-002-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-002-CDP.tex` |
| `1SPE-PROBCOND-EX-002` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-002.tex` |
| `1SPE-PROBCOND-EX-003-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-003-CDP.tex` |
| `1SPE-PROBCOND-EX-003` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-003.tex` |
| `1SPE-PROBCOND-EX-004-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-004-CDP.tex` |
| `1SPE-PROBCOND-EX-004` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-004.tex` |
| `1SPE-PROBCOND-EX-005` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-005.tex` |
| `1SPE-PROBCOND-EX-006` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-006.tex` |
| `1SPE-PROBCOND-EX-007` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-007.tex` |
| `1SPE-PROBCOND-EX-008` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-008.tex` |
| `1SPE-PROBCOND-EX-009` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-009.tex` |
| `1SPE-PROBCOND-EX-010` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-010.tex` |
| `1SPE-PROBCOND-EX-011-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-011-CDP.tex` |
| `1SPE-PROBCOND-EX-011` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-011.tex` |
| `1SPE-PROBCOND-EX-012-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-012-CDP.tex` |
| `1SPE-PROBCOND-EX-012` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-012.tex` |
| `1SPE-PROBCOND-EX-013-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-013-CDP.tex` |
| `1SPE-PROBCOND-EX-013` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-013.tex` |
| `1SPE-PROBCOND-EX-014-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-014-CDP.tex` |
| `1SPE-PROBCOND-EX-014` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-014.tex` |
| `1SPE-PROBCOND-EX-015` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-015.tex` |
| `1SPE-PROBCOND-EX-016` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-016.tex` |
| `1SPE-PROBCOND-EX-017` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-017.tex` |
| `1SPE-PROBCOND-EX-018` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-018.tex` |
| `1SPE-PROBCOND-EX-019` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-019.tex` |
| `1SPE-PROBCOND-EX-020` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-020.tex` |
| `1SPE-PROBCOND-EX-021-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-021-CDP.tex` |
| `1SPE-PROBCOND-EX-021` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-021.tex` |
| `1SPE-PROBCOND-EX-022-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-022-CDP.tex` |
| `1SPE-PROBCOND-EX-022` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-022.tex` |
| `1SPE-PROBCOND-EX-023-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-023-CDP.tex` |
| `1SPE-PROBCOND-EX-023` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-023.tex` |
| `1SPE-PROBCOND-EX-024-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-024-CDP.tex` |
| `1SPE-PROBCOND-EX-024` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-024.tex` |
| `1SPE-PROBCOND-EX-025` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-025.tex` |
| `1SPE-PROBCOND-EX-026` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-026.tex` |
| `1SPE-PROBCOND-EX-027` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-027.tex` |
| `1SPE-PROBCOND-EX-028` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-028.tex` |
| `1SPE-PROBCOND-EX-029` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-029.tex` |
| `1SPE-PROBCOND-EX-030` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-030.tex` |
| `1SPE-PROBCOND-EX-031-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-031-CDP.tex` |
| `1SPE-PROBCOND-EX-031` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-031.tex` |
| `1SPE-PROBCOND-EX-032-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-032-CDP.tex` |
| `1SPE-PROBCOND-EX-032` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-032.tex` |
| `1SPE-PROBCOND-EX-033` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-033.tex` |
| `1SPE-PROBCOND-EX-034` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-034.tex` |
| `1SPE-PROBCOND-EX-035` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-035.tex` |
| `1SPE-PROBCOND-EX-036` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-036.tex` |
| `1SPE-PROBCOND-EX-037` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-037.tex` |
| `1SPE-PROBCOND-EX-038` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-038.tex` |
| `1SPE-PROBCOND-EX-039` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-039.tex` |
| `1SPE-PROBCOND-EX-040` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-040.tex` |
| `1SPE-PROBCOND-EX-041-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-041-CDP.tex` |
| `1SPE-PROBCOND-EX-041` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-041.tex` |
| `1SPE-PROBCOND-EX-042-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-042-CDP.tex` |
| `1SPE-PROBCOND-EX-042` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-042.tex` |
| `1SPE-PROBCOND-EX-043-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-043-CDP.tex` |
| `1SPE-PROBCOND-EX-043` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-043.tex` |
| `1SPE-PROBCOND-EX-044-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-044-CDP.tex` |
| `1SPE-PROBCOND-EX-044` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-044.tex` |
| `1SPE-PROBCOND-EX-045` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-045.tex` |
| `1SPE-PROBCOND-EX-046` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-046.tex` |
| `1SPE-PROBCOND-EX-047` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-047.tex` |
| `1SPE-PROBCOND-EX-048` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-048.tex` |
| `1SPE-PROBCOND-EX-049` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-049.tex` |
| `1SPE-PROBCOND-EX-050` | `exercise` | `keep` | `chapitres/1SPE-PROBA-COND/exercices/1SPE-PROBCOND-EX-050.tex` |
| `1SPE-PROBCOND-ME-001` | `method` | `keep` | `chapitres/1SPE-PROBA-COND/methodes/1SPE-PROBCOND-ME-001.tex` |
| `1SPE-PROBCOND-ME-002` | `method` | `keep` | `chapitres/1SPE-PROBA-COND/methodes/1SPE-PROBCOND-ME-002.tex` |
| `1SPE-PROBCOND-ME-003` | `method` | `keep` | `chapitres/1SPE-PROBA-COND/methodes/1SPE-PROBCOND-ME-003.tex` |
| `1SPE-PROBCOND-ME-004` | `method` | `keep` | `chapitres/1SPE-PROBA-COND/methodes/1SPE-PROBCOND-ME-004.tex` |
| `1SPE-PROBCOND-ME-005` | `method` | `keep` | `chapitres/1SPE-PROBA-COND/methodes/1SPE-PROBCOND-ME-005.tex` |
| `CHAPITRES/1SPE-PROBA-COND/QCM/1SPE-PROBCOND-QCM:JSON` | `qcm_json` | `keep` | `chapitres/1SPE-PROBA-COND/qcm/1SPE-PROBCOND-QCM.json` |
| `1SPE-PROBCOND-QCM:TEX` | `qcm_tex` | `keep` | `chapitres/1SPE-PROBA-COND/qcm/1SPE-PROBCOND-QCM.tex` |
| `1SPE-PROBCOND-FR-R1` | `remediation` | `keep` | `chapitres/1SPE-PROBA-COND/remediation/1SPE-PROBCOND-FR-R1.tex` |
| `1SPE-PROBCOND-FR-R2` | `remediation` | `keep` | `chapitres/1SPE-PROBA-COND/remediation/1SPE-PROBCOND-FR-R2.tex` |
| `1SPE-PROBCOND-FR-R3` | `remediation` | `keep` | `chapitres/1SPE-PROBA-COND/remediation/1SPE-PROBCOND-FR-R3.tex` |
| `1SPE-PROBCOND-FR-R4` | `remediation` | `keep` | `chapitres/1SPE-PROBA-COND/remediation/1SPE-PROBCOND-FR-R4.tex` |
| `1SPE-PROBCOND-FR-R5` | `remediation` | `keep` | `chapitres/1SPE-PROBA-COND/remediation/1SPE-PROBCOND-FR-R5.tex` |
| `1SPE-PROBCOND-RE-C1` | `remediation` | `keep` | `chapitres/1SPE-PROBA-COND/remediation/1SPE-PROBCOND-RE-C1.tex` |
| `1SPE-PROBCOND-RE-C2` | `remediation` | `keep` | `chapitres/1SPE-PROBA-COND/remediation/1SPE-PROBCOND-RE-C2.tex` |
| `1SPE-PROBCOND-RE-C3` | `remediation` | `keep` | `chapitres/1SPE-PROBA-COND/remediation/1SPE-PROBCOND-RE-C3.tex` |
| `1SPE-PROBCOND-RE-C4` | `remediation` | `keep` | `chapitres/1SPE-PROBA-COND/remediation/1SPE-PROBCOND-RE-C4.tex` |
| `1SPE-PROBCOND-RE-C5` | `remediation` | `keep` | `chapitres/1SPE-PROBA-COND/remediation/1SPE-PROBCOND-RE-C5.tex` |
| `01_diagnostic:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-PROBA-COND/validations/01_diagnostic.sympy.json` |
| `07_td_contextualise:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-PROBA-COND/validations/07_td_contextualise.sympy.json` |
| `07_td_fil_rouge:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-PROBA-COND/validations/07_td_fil_rouge.sympy.json` |
| `10_C1_probabilite_conditionnelle:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/10_C1_probabilite_conditionnelle.sympy.json` |
| `11_C2_arbre_pondere:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/11_C2_arbre_pondere.sympy.json` |
| `12_C3_probabilites_totales:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/12_C3_probabilites_totales.sympy.json` |
| `13_C4_independance:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/13_C4_independance.sympy.json` |
| `14_C5_problemes_contextualises:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-PROBA-COND/validations/14_C5_problemes_contextualises.sympy.json` |
| `1SPE-PROBCOND-CO-001:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-001.sympy.json` |
| `1SPE-PROBCOND-CO-002:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-002.sympy.json` |
| `1SPE-PROBCOND-CO-003:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-003.sympy.json` |
| `1SPE-PROBCOND-CO-004:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-004.sympy.json` |
| `1SPE-PROBCOND-CO-005:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-005.sympy.json` |
| `1SPE-PROBCOND-CO-006:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-006.sympy.json` |
| `1SPE-PROBCOND-CO-007:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-007.sympy.json` |
| `1SPE-PROBCOND-CO-008:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-008.sympy.json` |
| `1SPE-PROBCOND-CO-009:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-009.sympy.json` |
| `1SPE-PROBCOND-CO-010:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-010.sympy.json` |
| `1SPE-PROBCOND-CO-011:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-011.sympy.json` |
| `1SPE-PROBCOND-CO-012:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-012.sympy.json` |
| `1SPE-PROBCOND-CO-013:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-013.sympy.json` |
| `1SPE-PROBCOND-CO-014:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-014.sympy.json` |
| `1SPE-PROBCOND-CO-015:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-015.sympy.json` |
| `1SPE-PROBCOND-CO-016:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-016.sympy.json` |
| `1SPE-PROBCOND-CO-017:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-017.sympy.json` |
| `1SPE-PROBCOND-CO-018:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-018.sympy.json` |
| `1SPE-PROBCOND-CO-019:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-019.sympy.json` |
| `1SPE-PROBCOND-CO-020:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-020.sympy.json` |
| `1SPE-PROBCOND-CO-021:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-021.sympy.json` |
| `1SPE-PROBCOND-CO-022:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-022.sympy.json` |
| `1SPE-PROBCOND-CO-023:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-023.sympy.json` |
| `1SPE-PROBCOND-CO-024:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-024.sympy.json` |
| `1SPE-PROBCOND-CO-025:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-025.sympy.json` |
| `1SPE-PROBCOND-CO-026:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-026.sympy.json` |
| `1SPE-PROBCOND-CO-027:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-027.sympy.json` |
| `1SPE-PROBCOND-CO-028:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-028.sympy.json` |
| `1SPE-PROBCOND-CO-029:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-029.sympy.json` |
| `1SPE-PROBCOND-CO-030:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-030.sympy.json` |
| `1SPE-PROBCOND-CO-031:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-031.sympy.json` |
| `1SPE-PROBCOND-CO-032:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-032.sympy.json` |
| `1SPE-PROBCOND-CO-033:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-033.sympy.json` |
| `1SPE-PROBCOND-CO-034:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-034.sympy.json` |
| `1SPE-PROBCOND-CO-035:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-035.sympy.json` |
| `1SPE-PROBCOND-CO-036:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-036.sympy.json` |
| `1SPE-PROBCOND-CO-037:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-037.sympy.json` |
| `1SPE-PROBCOND-CO-038:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-038.sympy.json` |
| `1SPE-PROBCOND-CO-039:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-039.sympy.json` |
| `1SPE-PROBCOND-CO-040:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-040.sympy.json` |
| `1SPE-PROBCOND-CO-041:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-041.sympy.json` |
| `1SPE-PROBCOND-CO-042:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-042.sympy.json` |
| `1SPE-PROBCOND-CO-043:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-043.sympy.json` |
| `1SPE-PROBCOND-CO-044:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-044.sympy.json` |
| `1SPE-PROBCOND-CO-045:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-045.sympy.json` |
| `1SPE-PROBCOND-CO-046:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-046.sympy.json` |
| `1SPE-PROBCOND-CO-047:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-047.sympy.json` |
| `1SPE-PROBCOND-CO-048:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-048.sympy.json` |
| `1SPE-PROBCOND-CO-049:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-049.sympy.json` |
| `1SPE-PROBCOND-CO-050:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-CO-050.sympy.json` |
| `1SPE-PROBCOND-EV-A-corrige:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EV-A-corrige.sympy.json` |
| `1SPE-PROBCOND-EV-A:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EV-A.sympy.json` |
| `1SPE-PROBCOND-EV-B-corrige:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EV-B-corrige.sympy.json` |
| `1SPE-PROBCOND-EV-B:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EV-B.sympy.json` |
| `1SPE-PROBCOND-EX-001-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-001-CDP.sympy.json` |
| `1SPE-PROBCOND-EX-001:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-001.sympy.json` |
| `1SPE-PROBCOND-EX-002-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-002-CDP.sympy.json` |
| `1SPE-PROBCOND-EX-002:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-002.sympy.json` |
| `1SPE-PROBCOND-EX-003-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-003-CDP.sympy.json` |
| `1SPE-PROBCOND-EX-003:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-003.sympy.json` |
| `1SPE-PROBCOND-EX-004-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-004-CDP.sympy.json` |
| `1SPE-PROBCOND-EX-004:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-004.sympy.json` |
| `1SPE-PROBCOND-EX-005:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-005.sympy.json` |
| `1SPE-PROBCOND-EX-006:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-006.sympy.json` |
| `1SPE-PROBCOND-EX-007:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-007.sympy.json` |
| `1SPE-PROBCOND-EX-008:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-008.sympy.json` |
| `1SPE-PROBCOND-EX-009:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-009.sympy.json` |
| `1SPE-PROBCOND-EX-010:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-010.sympy.json` |
| `1SPE-PROBCOND-EX-011-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-011-CDP.sympy.json` |
| `1SPE-PROBCOND-EX-011:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-011.sympy.json` |
| `1SPE-PROBCOND-EX-012-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-012-CDP.sympy.json` |
| `1SPE-PROBCOND-EX-012:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-012.sympy.json` |
| `1SPE-PROBCOND-EX-013-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-013-CDP.sympy.json` |
| `1SPE-PROBCOND-EX-013:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-013.sympy.json` |
| `1SPE-PROBCOND-EX-014-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-014-CDP.sympy.json` |
| `1SPE-PROBCOND-EX-014:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-014.sympy.json` |
| `1SPE-PROBCOND-EX-015:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-015.sympy.json` |
| `1SPE-PROBCOND-EX-016:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-016.sympy.json` |
| `1SPE-PROBCOND-EX-017:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-017.sympy.json` |
| `1SPE-PROBCOND-EX-018:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-018.sympy.json` |
| `1SPE-PROBCOND-EX-019:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-019.sympy.json` |
| `1SPE-PROBCOND-EX-020:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-020.sympy.json` |
| `1SPE-PROBCOND-EX-021-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-021-CDP.sympy.json` |
| `1SPE-PROBCOND-EX-021:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-021.sympy.json` |
| `1SPE-PROBCOND-EX-022-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-022-CDP.sympy.json` |
| `1SPE-PROBCOND-EX-022:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-022.sympy.json` |
| `1SPE-PROBCOND-EX-023-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-023-CDP.sympy.json` |
| `1SPE-PROBCOND-EX-023:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-023.sympy.json` |
| `1SPE-PROBCOND-EX-024-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-024-CDP.sympy.json` |
| `1SPE-PROBCOND-EX-024:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-024.sympy.json` |
| `1SPE-PROBCOND-EX-025:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-025.sympy.json` |
| `1SPE-PROBCOND-EX-026:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-026.sympy.json` |
| `1SPE-PROBCOND-EX-027:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-027.sympy.json` |
| `1SPE-PROBCOND-EX-028:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-028.sympy.json` |
| `1SPE-PROBCOND-EX-029:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-029.sympy.json` |
| `1SPE-PROBCOND-EX-030:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-030.sympy.json` |
| `1SPE-PROBCOND-EX-031-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-031-CDP.sympy.json` |
| `1SPE-PROBCOND-EX-031:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-031.sympy.json` |
| `1SPE-PROBCOND-EX-032-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-032-CDP.sympy.json` |
| `1SPE-PROBCOND-EX-032:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-032.sympy.json` |
| `1SPE-PROBCOND-EX-033:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-033.sympy.json` |
| `1SPE-PROBCOND-EX-034:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-034.sympy.json` |
| `1SPE-PROBCOND-EX-035:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-035.sympy.json` |
| `1SPE-PROBCOND-EX-036:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-036.sympy.json` |
| `1SPE-PROBCOND-EX-037:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-037.sympy.json` |
| `1SPE-PROBCOND-EX-038:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-038.sympy.json` |
| `1SPE-PROBCOND-EX-039:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-039.sympy.json` |
| `1SPE-PROBCOND-EX-040:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-040.sympy.json` |
| `1SPE-PROBCOND-EX-041-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-041-CDP.sympy.json` |
| `1SPE-PROBCOND-EX-041:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-041.sympy.json` |
| `1SPE-PROBCOND-EX-042-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-042-CDP.sympy.json` |
| `1SPE-PROBCOND-EX-042:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-042.sympy.json` |
| `1SPE-PROBCOND-EX-043-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-043-CDP.sympy.json` |
| `1SPE-PROBCOND-EX-043:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-043.sympy.json` |
| `1SPE-PROBCOND-EX-044-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-044-CDP.sympy.json` |
| `1SPE-PROBCOND-EX-044:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-044.sympy.json` |
| `1SPE-PROBCOND-EX-045:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-045.sympy.json` |
| `1SPE-PROBCOND-EX-046:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-046.sympy.json` |
| `1SPE-PROBCOND-EX-047:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-047.sympy.json` |
| `1SPE-PROBCOND-EX-048:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-048.sympy.json` |
| `1SPE-PROBCOND-EX-049:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-049.sympy.json` |
| `1SPE-PROBCOND-EX-050:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-EX-050.sympy.json` |
| `1SPE-PROBCOND-FR-R1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-FR-R1.sympy.json` |
| `1SPE-PROBCOND-FR-R2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-FR-R2.sympy.json` |
| `1SPE-PROBCOND-FR-R3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-FR-R3.sympy.json` |
| `1SPE-PROBCOND-FR-R4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-FR-R4.sympy.json` |
| `1SPE-PROBCOND-FR-R5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-FR-R5.sympy.json` |
| `1SPE-PROBCOND-QCM:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-QCM.sympy.json` |
| `1SPE-PROBCOND-RE-C1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-RE-C1.sympy.json` |
| `1SPE-PROBCOND-RE-C2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-RE-C2.sympy.json` |
| `1SPE-PROBCOND-RE-C3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-RE-C3.sympy.json` |
| `1SPE-PROBCOND-RE-C4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-RE-C4.sympy.json` |
| `1SPE-PROBCOND-RE-C5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PROBA-COND/validations/1SPE-PROBCOND-RE-C5.sympy.json` |
| `CHAPITRES/1SPE-PRODUIT-SCALAIRE/LOT-0_RAPPORT` | `report` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/LOT-0_rapport.md` |
| `CHAPITRES/1SPE-PRODUIT-SCALAIRE/LOT-1_RAPPORT` | `report` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/LOT-1_rapport.md` |
| `CHAPITRES/1SPE-PRODUIT-SCALAIRE/LOT-2_RAPPORT` | `report` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/LOT-2_rapport.md` |
| `CHAPITRES/1SPE-PRODUIT-SCALAIRE/LOT-3_RAPPORT` | `report` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/LOT-3_rapport.md` |
| `CHAPITRES/1SPE-PRODUIT-SCALAIRE/LOT-4_RAPPORT` | `report` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/LOT-4_rapport.md` |
| `CHAPITRES/1SPE-PRODUIT-SCALAIRE/LOT-5_RAPPORT` | `report` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/LOT-5_rapport.md` |
| `CHAPITRES/1SPE-PRODUIT-SCALAIRE/LOT-6_RAPPORT` | `report` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/LOT-6_rapport.md` |
| `CHAPITRES/1SPE-PRODUIT-SCALAIRE/LOT-7_RAPPORT` | `report` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/LOT-7_rapport.md` |
| `CHAPITRES/1SPE-PRODUIT-SCALAIRE/CONTRAT` | `chapter_contract` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/contrat.yaml` |
| `1SPE-PRODSCAL-CO-001` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-001.tex` |
| `1SPE-PRODSCAL-CO-002` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-002.tex` |
| `1SPE-PRODSCAL-CO-003` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-003.tex` |
| `1SPE-PRODSCAL-CO-004` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-004.tex` |
| `1SPE-PRODSCAL-CO-005` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-005.tex` |
| `1SPE-PRODSCAL-CO-006` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-006.tex` |
| `1SPE-PRODSCAL-CO-007` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-007.tex` |
| `1SPE-PRODSCAL-CO-008` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-008.tex` |
| `1SPE-PRODSCAL-CO-009` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-009.tex` |
| `1SPE-PRODSCAL-CO-010` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-010.tex` |
| `1SPE-PRODSCAL-CO-011` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-011.tex` |
| `1SPE-PRODSCAL-CO-012` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-012.tex` |
| `1SPE-PRODSCAL-CO-013` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-013.tex` |
| `1SPE-PRODSCAL-CO-014` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-014.tex` |
| `1SPE-PRODSCAL-CO-015` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-015.tex` |
| `1SPE-PRODSCAL-CO-016` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-016.tex` |
| `1SPE-PRODSCAL-CO-017` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-017.tex` |
| `1SPE-PRODSCAL-CO-018` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-018.tex` |
| `1SPE-PRODSCAL-CO-019` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-019.tex` |
| `1SPE-PRODSCAL-CO-020` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-020.tex` |
| `1SPE-PRODSCAL-CO-021` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-021.tex` |
| `1SPE-PRODSCAL-CO-022` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-022.tex` |
| `1SPE-PRODSCAL-CO-023` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-023.tex` |
| `1SPE-PRODSCAL-CO-024` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-024.tex` |
| `1SPE-PRODSCAL-CO-025` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-025.tex` |
| `1SPE-PRODSCAL-CO-026` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-026.tex` |
| `1SPE-PRODSCAL-CO-027` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-027.tex` |
| `1SPE-PRODSCAL-CO-028` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-028.tex` |
| `1SPE-PRODSCAL-CO-029` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-029.tex` |
| `1SPE-PRODSCAL-CO-030` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-030.tex` |
| `1SPE-PRODSCAL-CO-031` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-031.tex` |
| `1SPE-PRODSCAL-CO-032` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-032.tex` |
| `1SPE-PRODSCAL-CO-033` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-033.tex` |
| `1SPE-PRODSCAL-CO-034` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-034.tex` |
| `1SPE-PRODSCAL-CO-035` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-035.tex` |
| `1SPE-PRODSCAL-CO-036` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-036.tex` |
| `1SPE-PRODSCAL-CO-037` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-037.tex` |
| `1SPE-PRODSCAL-CO-038` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-038.tex` |
| `1SPE-PRODSCAL-CO-039` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-039.tex` |
| `1SPE-PRODSCAL-CO-040` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-040.tex` |
| `1SPE-PRODSCAL-CO-041` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-041.tex` |
| `1SPE-PRODSCAL-CO-042` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-042.tex` |
| `1SPE-PRODSCAL-CO-043` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-043.tex` |
| `1SPE-PRODSCAL-CO-044` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-044.tex` |
| `1SPE-PRODSCAL-CO-045` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-045.tex` |
| `1SPE-PRODSCAL-CO-046` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-046.tex` |
| `1SPE-PRODSCAL-CO-047` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-047.tex` |
| `1SPE-PRODSCAL-CO-048` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-048.tex` |
| `1SPE-PRODSCAL-CO-049` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-049.tex` |
| `1SPE-PRODSCAL-CO-050` | `solution` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/corriges/1SPE-PRODSCAL-CO-050.tex` |
| `1SPE-PRODSCAL-TD-CONTEXTUALISE` | `transversal` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/cours/07_td_contextualise.tex` |
| `1SPE-PRODSCAL-TD-FIL-ROUGE` | `transversal` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/cours/07_td_fil_rouge.tex` |
| `1SPE-PRODSCAL-COURS-C1` | `course` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/cours/10_C1_produit_scalaire.tex` |
| `1SPE-PRODSCAL-COURS-C2` | `course` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/cours/11_C2_proprietes.tex` |
| `1SPE-PRODSCAL-COURS-C3` | `course` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/cours/12_C3_orthogonalite.tex` |
| `1SPE-PRODSCAL-COURS-C4` | `course` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/cours/13_C4_applications.tex` |
| `1SPE-PRODSCAL-COURS-C5` | `course` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/cours/14_C5_al_kashi.tex` |
| `CHAPITRES/1SPE-PRODUIT-SCALAIRE/DOSSIER_CURATION` | `chapter_metadata` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/dossier_curation.json` |
| `1SPE-PRODSCAL-EV-A-corrige:SCALE` | `grading_scale` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/evaluations/1SPE-PRODSCAL-EV-A-corrige.tex` |
| `1SPE-PRODSCAL-EV-A` | `assessment` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/evaluations/1SPE-PRODSCAL-EV-A.tex` |
| `1SPE-PRODSCAL-EV-B-corrige:SCALE` | `grading_scale` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/evaluations/1SPE-PRODSCAL-EV-B-corrige.tex` |
| `1SPE-PRODSCAL-EV-B` | `assessment` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/evaluations/1SPE-PRODSCAL-EV-B.tex` |
| `1SPE-PRODSCAL-EX-001-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-001-CDP.tex` |
| `1SPE-PRODSCAL-EX-001` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-001.tex` |
| `1SPE-PRODSCAL-EX-002-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-002-CDP.tex` |
| `1SPE-PRODSCAL-EX-002` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-002.tex` |
| `1SPE-PRODSCAL-EX-003-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-003-CDP.tex` |
| `1SPE-PRODSCAL-EX-003` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-003.tex` |
| `1SPE-PRODSCAL-EX-004-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-004-CDP.tex` |
| `1SPE-PRODSCAL-EX-004` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-004.tex` |
| `1SPE-PRODSCAL-EX-005` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-005.tex` |
| `1SPE-PRODSCAL-EX-006` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-006.tex` |
| `1SPE-PRODSCAL-EX-007` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-007.tex` |
| `1SPE-PRODSCAL-EX-008` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-008.tex` |
| `1SPE-PRODSCAL-EX-009` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-009.tex` |
| `1SPE-PRODSCAL-EX-010` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-010.tex` |
| `1SPE-PRODSCAL-EX-011-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-011-CDP.tex` |
| `1SPE-PRODSCAL-EX-011` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-011.tex` |
| `1SPE-PRODSCAL-EX-012-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-012-CDP.tex` |
| `1SPE-PRODSCAL-EX-012` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-012.tex` |
| `1SPE-PRODSCAL-EX-013-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-013-CDP.tex` |
| `1SPE-PRODSCAL-EX-013` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-013.tex` |
| `1SPE-PRODSCAL-EX-014-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-014-CDP.tex` |
| `1SPE-PRODSCAL-EX-014` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-014.tex` |
| `1SPE-PRODSCAL-EX-015` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-015.tex` |
| `1SPE-PRODSCAL-EX-016` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-016.tex` |
| `1SPE-PRODSCAL-EX-017` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-017.tex` |
| `1SPE-PRODSCAL-EX-018` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-018.tex` |
| `1SPE-PRODSCAL-EX-019` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-019.tex` |
| `1SPE-PRODSCAL-EX-020` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-020.tex` |
| `1SPE-PRODSCAL-EX-021-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-021-CDP.tex` |
| `1SPE-PRODSCAL-EX-021` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-021.tex` |
| `1SPE-PRODSCAL-EX-022-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-022-CDP.tex` |
| `1SPE-PRODSCAL-EX-022` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-022.tex` |
| `1SPE-PRODSCAL-EX-023-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-023-CDP.tex` |
| `1SPE-PRODSCAL-EX-023` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-023.tex` |
| `1SPE-PRODSCAL-EX-024-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-024-CDP.tex` |
| `1SPE-PRODSCAL-EX-024` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-024.tex` |
| `1SPE-PRODSCAL-EX-025` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-025.tex` |
| `1SPE-PRODSCAL-EX-026` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-026.tex` |
| `1SPE-PRODSCAL-EX-027` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-027.tex` |
| `1SPE-PRODSCAL-EX-028` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-028.tex` |
| `1SPE-PRODSCAL-EX-029` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-029.tex` |
| `1SPE-PRODSCAL-EX-030` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-030.tex` |
| `1SPE-PRODSCAL-EX-031-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-031-CDP.tex` |
| `1SPE-PRODSCAL-EX-031` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-031.tex` |
| `1SPE-PRODSCAL-EX-032-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-032-CDP.tex` |
| `1SPE-PRODSCAL-EX-032` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-032.tex` |
| `1SPE-PRODSCAL-EX-033-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-033-CDP.tex` |
| `1SPE-PRODSCAL-EX-033` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-033.tex` |
| `1SPE-PRODSCAL-EX-034-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-034-CDP.tex` |
| `1SPE-PRODSCAL-EX-034` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-034.tex` |
| `1SPE-PRODSCAL-EX-035` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-035.tex` |
| `1SPE-PRODSCAL-EX-036` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-036.tex` |
| `1SPE-PRODSCAL-EX-037` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-037.tex` |
| `1SPE-PRODSCAL-EX-038` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-038.tex` |
| `1SPE-PRODSCAL-EX-039` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-039.tex` |
| `1SPE-PRODSCAL-EX-040` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-040.tex` |
| `1SPE-PRODSCAL-EX-041-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-041-CDP.tex` |
| `1SPE-PRODSCAL-EX-041` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-041.tex` |
| `1SPE-PRODSCAL-EX-042-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-042-CDP.tex` |
| `1SPE-PRODSCAL-EX-042` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-042.tex` |
| `1SPE-PRODSCAL-EX-043` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-043.tex` |
| `1SPE-PRODSCAL-EX-044` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-044.tex` |
| `1SPE-PRODSCAL-EX-045` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-045.tex` |
| `1SPE-PRODSCAL-EX-046` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-046.tex` |
| `1SPE-PRODSCAL-EX-047` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-047.tex` |
| `1SPE-PRODSCAL-EX-048` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-048.tex` |
| `1SPE-PRODSCAL-EX-049` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-049.tex` |
| `1SPE-PRODSCAL-EX-050` | `exercise` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-050.tex` |
| `1SPE-PRODSCAL-ME-001` | `method` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/methodes/1SPE-PRODSCAL-ME-001.tex` |
| `1SPE-PRODSCAL-ME-002` | `method` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/methodes/1SPE-PRODSCAL-ME-002.tex` |
| `1SPE-PRODSCAL-ME-003` | `method` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/methodes/1SPE-PRODSCAL-ME-003.tex` |
| `1SPE-PRODSCAL-ME-004` | `method` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/methodes/1SPE-PRODSCAL-ME-004.tex` |
| `1SPE-PRODSCAL-ME-005` | `method` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/methodes/1SPE-PRODSCAL-ME-005.tex` |
| `CHAPITRES/1SPE-PRODUIT-SCALAIRE/QCM/1SPE-PRODUIT-SCALAIRE-QCM:JSON` | `qcm_json` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/qcm/1SPE-PRODUIT-SCALAIRE-QCM.json` |
| `1SPE-PRODUIT-SCALAIRE-QCM:TEX` | `qcm_tex` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/qcm/1SPE-PRODUIT-SCALAIRE-QCM.tex` |
| `1SPE-PRODUIT-SCALAIRE-FR-R1` | `remediation` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/remediation/1SPE-PRODUIT-SCALAIRE-FR-R1.tex` |
| `1SPE-PRODUIT-SCALAIRE-FR-R2` | `remediation` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/remediation/1SPE-PRODUIT-SCALAIRE-FR-R2.tex` |
| `1SPE-PRODUIT-SCALAIRE-FR-R3` | `remediation` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/remediation/1SPE-PRODUIT-SCALAIRE-FR-R3.tex` |
| `1SPE-PRODUIT-SCALAIRE-FR-R4` | `remediation` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/remediation/1SPE-PRODUIT-SCALAIRE-FR-R4.tex` |
| `1SPE-PRODUIT-SCALAIRE-FR-R5` | `remediation` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/remediation/1SPE-PRODUIT-SCALAIRE-FR-R5.tex` |
| `1SPE-PRODUIT-SCALAIRE-RE-C1` | `remediation` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/remediation/1SPE-PRODUIT-SCALAIRE-RE-C1.tex` |
| `1SPE-PRODUIT-SCALAIRE-RE-C2` | `remediation` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/remediation/1SPE-PRODUIT-SCALAIRE-RE-C2.tex` |
| `1SPE-PRODUIT-SCALAIRE-RE-C3` | `remediation` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/remediation/1SPE-PRODUIT-SCALAIRE-RE-C3.tex` |
| `1SPE-PRODUIT-SCALAIRE-RE-C4` | `remediation` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/remediation/1SPE-PRODUIT-SCALAIRE-RE-C4.tex` |
| `1SPE-PRODUIT-SCALAIRE-RE-C5` | `remediation` | `keep` | `chapitres/1SPE-PRODUIT-SCALAIRE/remediation/1SPE-PRODUIT-SCALAIRE-RE-C5.tex` |
| `07_td_contextualise:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/07_td_contextualise.sympy.json` |
| `07_td_fil_rouge:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/07_td_fil_rouge.sympy.json` |
| `10_C1_produit_scalaire:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/10_C1_produit_scalaire.sympy.json` |
| `11_C2_proprietes:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/11_C2_proprietes.sympy.json` |
| `12_C3_orthogonalite:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/12_C3_orthogonalite.sympy.json` |
| `13_C4_applications:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/13_C4_applications.sympy.json` |
| `14_C5_al_kashi:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/14_C5_al_kashi.sympy.json` |
| `1SPE-PRODSCAL-CO-001:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-001.sympy.json` |
| `1SPE-PRODSCAL-CO-002:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-002.sympy.json` |
| `1SPE-PRODSCAL-CO-003:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-003.sympy.json` |
| `1SPE-PRODSCAL-CO-004:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-004.sympy.json` |
| `1SPE-PRODSCAL-CO-005:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-005.sympy.json` |
| `1SPE-PRODSCAL-CO-006:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-006.sympy.json` |
| `1SPE-PRODSCAL-CO-007:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-007.sympy.json` |
| `1SPE-PRODSCAL-CO-008:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-008.sympy.json` |
| `1SPE-PRODSCAL-CO-009:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-009.sympy.json` |
| `1SPE-PRODSCAL-CO-010:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-010.sympy.json` |
| `1SPE-PRODSCAL-CO-011:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-011.sympy.json` |
| `1SPE-PRODSCAL-CO-012:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-012.sympy.json` |
| `1SPE-PRODSCAL-CO-013:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-013.sympy.json` |
| `1SPE-PRODSCAL-CO-014:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-014.sympy.json` |
| `1SPE-PRODSCAL-CO-015:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-015.sympy.json` |
| `1SPE-PRODSCAL-CO-016:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-016.sympy.json` |
| `1SPE-PRODSCAL-CO-017:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-017.sympy.json` |
| `1SPE-PRODSCAL-CO-018:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-018.sympy.json` |
| `1SPE-PRODSCAL-CO-019:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-019.sympy.json` |
| `1SPE-PRODSCAL-CO-020:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-020.sympy.json` |
| `1SPE-PRODSCAL-CO-021:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-021.sympy.json` |
| `1SPE-PRODSCAL-CO-022:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-022.sympy.json` |
| `1SPE-PRODSCAL-CO-023:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-023.sympy.json` |
| `1SPE-PRODSCAL-CO-024:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-024.sympy.json` |
| `1SPE-PRODSCAL-CO-025:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-025.sympy.json` |
| `1SPE-PRODSCAL-CO-026:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-026.sympy.json` |
| `1SPE-PRODSCAL-CO-027:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-027.sympy.json` |
| `1SPE-PRODSCAL-CO-028:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-028.sympy.json` |
| `1SPE-PRODSCAL-CO-029:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-029.sympy.json` |
| `1SPE-PRODSCAL-CO-030:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-030.sympy.json` |
| `1SPE-PRODSCAL-CO-031:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-031.sympy.json` |
| `1SPE-PRODSCAL-CO-032:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-032.sympy.json` |
| `1SPE-PRODSCAL-CO-033:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-033.sympy.json` |
| `1SPE-PRODSCAL-CO-034:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-034.sympy.json` |
| `1SPE-PRODSCAL-CO-035:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-035.sympy.json` |
| `1SPE-PRODSCAL-CO-036:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-036.sympy.json` |
| `1SPE-PRODSCAL-CO-037:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-037.sympy.json` |
| `1SPE-PRODSCAL-CO-038:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-038.sympy.json` |
| `1SPE-PRODSCAL-CO-039:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-039.sympy.json` |
| `1SPE-PRODSCAL-CO-040:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-040.sympy.json` |
| `1SPE-PRODSCAL-CO-041:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-041.sympy.json` |
| `1SPE-PRODSCAL-CO-042:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-042.sympy.json` |
| `1SPE-PRODSCAL-CO-043:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-043.sympy.json` |
| `1SPE-PRODSCAL-CO-044:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-044.sympy.json` |
| `1SPE-PRODSCAL-CO-045:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-045.sympy.json` |
| `1SPE-PRODSCAL-CO-046:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-046.sympy.json` |
| `1SPE-PRODSCAL-CO-047:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-047.sympy.json` |
| `1SPE-PRODSCAL-CO-048:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-048.sympy.json` |
| `1SPE-PRODSCAL-CO-049:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-049.sympy.json` |
| `1SPE-PRODSCAL-CO-050:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-CO-050.sympy.json` |
| `1SPE-PRODSCAL-EV-A-corrige:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EV-A-corrige.sympy.json` |
| `1SPE-PRODSCAL-EV-A:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EV-A.sympy.json` |
| `1SPE-PRODSCAL-EV-B-corrige:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EV-B-corrige.sympy.json` |
| `1SPE-PRODSCAL-EV-B:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EV-B.sympy.json` |
| `1SPE-PRODSCAL-EX-001-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-001-CDP.sympy.json` |
| `1SPE-PRODSCAL-EX-001:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-001.sympy.json` |
| `1SPE-PRODSCAL-EX-002-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-002-CDP.sympy.json` |
| `1SPE-PRODSCAL-EX-002:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-002.sympy.json` |
| `1SPE-PRODSCAL-EX-003-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-003-CDP.sympy.json` |
| `1SPE-PRODSCAL-EX-003:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-003.sympy.json` |
| `1SPE-PRODSCAL-EX-004-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-004-CDP.sympy.json` |
| `1SPE-PRODSCAL-EX-004:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-004.sympy.json` |
| `1SPE-PRODSCAL-EX-005:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-005.sympy.json` |
| `1SPE-PRODSCAL-EX-006:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-006.sympy.json` |
| `1SPE-PRODSCAL-EX-007:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-007.sympy.json` |
| `1SPE-PRODSCAL-EX-008:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-008.sympy.json` |
| `1SPE-PRODSCAL-EX-009:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-009.sympy.json` |
| `1SPE-PRODSCAL-EX-010:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-010.sympy.json` |
| `1SPE-PRODSCAL-EX-011-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-011-CDP.sympy.json` |
| `1SPE-PRODSCAL-EX-011:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-011.sympy.json` |
| `1SPE-PRODSCAL-EX-012-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-012-CDP.sympy.json` |
| `1SPE-PRODSCAL-EX-012:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-012.sympy.json` |
| `1SPE-PRODSCAL-EX-013-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-013-CDP.sympy.json` |
| `1SPE-PRODSCAL-EX-013:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-013.sympy.json` |
| `1SPE-PRODSCAL-EX-014-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-014-CDP.sympy.json` |
| `1SPE-PRODSCAL-EX-014:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-014.sympy.json` |
| `1SPE-PRODSCAL-EX-015:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-015.sympy.json` |
| `1SPE-PRODSCAL-EX-016:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-016.sympy.json` |
| `1SPE-PRODSCAL-EX-017:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-017.sympy.json` |
| `1SPE-PRODSCAL-EX-018:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-018.sympy.json` |
| `1SPE-PRODSCAL-EX-019:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-019.sympy.json` |
| `1SPE-PRODSCAL-EX-020:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-020.sympy.json` |
| `1SPE-PRODSCAL-EX-021-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-021-CDP.sympy.json` |
| `1SPE-PRODSCAL-EX-021:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-021.sympy.json` |
| `1SPE-PRODSCAL-EX-022-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-022-CDP.sympy.json` |
| `1SPE-PRODSCAL-EX-022:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-022.sympy.json` |
| `1SPE-PRODSCAL-EX-023-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-023-CDP.sympy.json` |
| `1SPE-PRODSCAL-EX-023:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-023.sympy.json` |
| `1SPE-PRODSCAL-EX-024-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-024-CDP.sympy.json` |
| `1SPE-PRODSCAL-EX-024:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-024.sympy.json` |
| `1SPE-PRODSCAL-EX-025:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-025.sympy.json` |
| `1SPE-PRODSCAL-EX-026:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-026.sympy.json` |
| `1SPE-PRODSCAL-EX-027:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-027.sympy.json` |
| `1SPE-PRODSCAL-EX-028:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-028.sympy.json` |
| `1SPE-PRODSCAL-EX-029:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-029.sympy.json` |
| `1SPE-PRODSCAL-EX-030:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-030.sympy.json` |
| `1SPE-PRODSCAL-EX-031-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-031-CDP.sympy.json` |
| `1SPE-PRODSCAL-EX-031:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-031.sympy.json` |
| `1SPE-PRODSCAL-EX-032-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-032-CDP.sympy.json` |
| `1SPE-PRODSCAL-EX-032:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-032.sympy.json` |
| `1SPE-PRODSCAL-EX-033-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-033-CDP.sympy.json` |
| `1SPE-PRODSCAL-EX-033:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-033.sympy.json` |
| `1SPE-PRODSCAL-EX-034-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-034-CDP.sympy.json` |
| `1SPE-PRODSCAL-EX-034:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-034.sympy.json` |
| `1SPE-PRODSCAL-EX-035:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-035.sympy.json` |
| `1SPE-PRODSCAL-EX-036:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-036.sympy.json` |
| `1SPE-PRODSCAL-EX-037:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-037.sympy.json` |
| `1SPE-PRODSCAL-EX-038:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-038.sympy.json` |
| `1SPE-PRODSCAL-EX-039:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-039.sympy.json` |
| `1SPE-PRODSCAL-EX-040:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-040.sympy.json` |
| `1SPE-PRODSCAL-EX-041-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-041-CDP.sympy.json` |
| `1SPE-PRODSCAL-EX-041:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-041.sympy.json` |
| `1SPE-PRODSCAL-EX-042-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-042-CDP.sympy.json` |
| `1SPE-PRODSCAL-EX-042:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-042.sympy.json` |
| `1SPE-PRODSCAL-EX-043:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-043.sympy.json` |
| `1SPE-PRODSCAL-EX-044:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-044.sympy.json` |
| `1SPE-PRODSCAL-EX-045:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-045.sympy.json` |
| `1SPE-PRODSCAL-EX-046:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-046.sympy.json` |
| `1SPE-PRODSCAL-EX-047:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-047.sympy.json` |
| `1SPE-PRODSCAL-EX-048:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-048.sympy.json` |
| `1SPE-PRODSCAL-EX-049:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-049.sympy.json` |
| `1SPE-PRODSCAL-EX-050:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODSCAL-EX-050.sympy.json` |
| `1SPE-PRODUIT-SCALAIRE-FR-R1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODUIT-SCALAIRE-FR-R1.sympy.json` |
| `1SPE-PRODUIT-SCALAIRE-FR-R2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODUIT-SCALAIRE-FR-R2.sympy.json` |
| `1SPE-PRODUIT-SCALAIRE-FR-R3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODUIT-SCALAIRE-FR-R3.sympy.json` |
| `1SPE-PRODUIT-SCALAIRE-FR-R4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODUIT-SCALAIRE-FR-R4.sympy.json` |
| `1SPE-PRODUIT-SCALAIRE-FR-R5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODUIT-SCALAIRE-FR-R5.sympy.json` |
| `1SPE-PRODUIT-SCALAIRE-QCM:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODUIT-SCALAIRE-QCM.sympy.json` |
| `1SPE-PRODUIT-SCALAIRE-RE-C1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODUIT-SCALAIRE-RE-C1.sympy.json` |
| `1SPE-PRODUIT-SCALAIRE-RE-C2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODUIT-SCALAIRE-RE-C2.sympy.json` |
| `1SPE-PRODUIT-SCALAIRE-RE-C3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODUIT-SCALAIRE-RE-C3.sympy.json` |
| `1SPE-PRODUIT-SCALAIRE-RE-C4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODUIT-SCALAIRE-RE-C4.sympy.json` |
| `1SPE-PRODUIT-SCALAIRE-RE-C5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-PRODUIT-SCALAIRE/validations/1SPE-PRODUIT-SCALAIRE-RE-C5.sympy.json` |
| `CHAPITRES/1SPE-SECOND-DEGRE/LOT-0_RAPPORT` | `report` | `keep` | `chapitres/1SPE-SECOND-DEGRE/LOT-0_rapport.md` |
| `CHAPITRES/1SPE-SECOND-DEGRE/LOT-7_RAPPORT` | `report` | `keep` | `chapitres/1SPE-SECOND-DEGRE/LOT-7_rapport.md` |
| `CHAPITRES/1SPE-SECOND-DEGRE/CONTRAT` | `chapter_contract` | `keep` | `chapitres/1SPE-SECOND-DEGRE/contrat.yaml` |
| `1SPE-SECDEG-CO-001` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-001.tex` |
| `1SPE-SECDEG-CO-002` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-002.tex` |
| `1SPE-SECDEG-CO-003` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-003.tex` |
| `1SPE-SECDEG-CO-004` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-004.tex` |
| `1SPE-SECDEG-CO-005` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-005.tex` |
| `1SPE-SECDEG-CO-006` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-006.tex` |
| `1SPE-SECDEG-CO-007` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-007.tex` |
| `1SPE-SECDEG-CO-008` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-008.tex` |
| `1SPE-SECDEG-CO-009` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-009.tex` |
| `1SPE-SECDEG-CO-010` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-010.tex` |
| `1SPE-SECDEG-CO-011` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-011.tex` |
| `1SPE-SECDEG-CO-012` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-012.tex` |
| `1SPE-SECDEG-CO-013` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-013.tex` |
| `1SPE-SECDEG-CO-014` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-014.tex` |
| `1SPE-SECDEG-CO-015` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-015.tex` |
| `1SPE-SECDEG-CO-016` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-016.tex` |
| `1SPE-SECDEG-CO-017` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-017.tex` |
| `1SPE-SECDEG-CO-018` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-018.tex` |
| `1SPE-SECDEG-CO-019` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-019.tex` |
| `1SPE-SECDEG-CO-020` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-020.tex` |
| `1SPE-SECDEG-CO-021` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-021.tex` |
| `1SPE-SECDEG-CO-022` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-022.tex` |
| `1SPE-SECDEG-CO-023` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-023.tex` |
| `1SPE-SECDEG-CO-024` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-024.tex` |
| `1SPE-SECDEG-CO-025` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-025.tex` |
| `1SPE-SECDEG-CO-026` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-026.tex` |
| `1SPE-SECDEG-CO-027` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-027.tex` |
| `1SPE-SECDEG-CO-028` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-028.tex` |
| `1SPE-SECDEG-CO-029` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-029.tex` |
| `1SPE-SECDEG-CO-030` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-030.tex` |
| `1SPE-SECDEG-CO-031` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-031.tex` |
| `1SPE-SECDEG-CO-032` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-032.tex` |
| `1SPE-SECDEG-CO-033` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-033.tex` |
| `1SPE-SECDEG-CO-034` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-034.tex` |
| `1SPE-SECDEG-CO-035` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-035.tex` |
| `1SPE-SECDEG-CO-036` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-036.tex` |
| `1SPE-SECDEG-CO-037` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-037.tex` |
| `1SPE-SECDEG-CO-038` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-038.tex` |
| `1SPE-SECDEG-CO-039` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-039.tex` |
| `1SPE-SECDEG-CO-040` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-040.tex` |
| `1SPE-SECDEG-CO-041` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-041.tex` |
| `1SPE-SECDEG-CO-042` | `solution` | `keep` | `chapitres/1SPE-SECOND-DEGRE/corriges/1SPE-SECDEG-CO-042.tex` |
| `1SPE-SECDEG-CR-000` | `course` | `keep` | `chapitres/1SPE-SECOND-DEGRE/cours/00_ouverture.tex` |
| `1SPE-SECDEG-CR-001` | `course` | `keep` | `chapitres/1SPE-SECOND-DEGRE/cours/01_diagnostic.tex` |
| `1SPE-SECDEG-TD-CONTEXTUALISE` | `transversal` | `keep` | `chapitres/1SPE-SECOND-DEGRE/cours/07_td_contextualise.tex` |
| `1SPE-SECDEG-TD-FIL-ROUGE` | `transversal` | `keep` | `chapitres/1SPE-SECOND-DEGRE/cours/07_td_fil_rouge.tex` |
| `1SPE-SECDEG-CR-010` | `course` | `keep` | `chapitres/1SPE-SECOND-DEGRE/cours/10_C1_formes_trinome.tex` |
| `1SPE-SECDEG-CR-011` | `course` | `keep` | `chapitres/1SPE-SECOND-DEGRE/cours/11_C2_parabole_variations.tex` |
| `1SPE-SECDEG-CR-012` | `course` | `keep` | `chapitres/1SPE-SECOND-DEGRE/cours/12_C3_discriminant.tex` |
| `1SPE-SECDEG-CR-013` | `course` | `keep` | `chapitres/1SPE-SECOND-DEGRE/cours/13_C4_factorisation_signe.tex` |
| `1SPE-SECDEG-CR-014` | `course` | `keep` | `chapitres/1SPE-SECOND-DEGRE/cours/14_C5_inequations.tex` |
| `1SPE-SECDEG-CR-015` | `course` | `keep` | `chapitres/1SPE-SECOND-DEGRE/cours/15_C6_optimisation.tex` |
| `CHAPITRES/1SPE-SECOND-DEGRE/DOSSIER_CURATION` | `chapter_metadata` | `keep` | `chapitres/1SPE-SECOND-DEGRE/dossier_curation.json` |
| `1SPE-SECDEG-EV-A-corrige:SCALE` | `grading_scale` | `keep` | `chapitres/1SPE-SECOND-DEGRE/evaluations/1SPE-SECDEG-EV-A-corrige.tex` |
| `1SPE-SECDEG-EV-A` | `assessment` | `keep` | `chapitres/1SPE-SECOND-DEGRE/evaluations/1SPE-SECDEG-EV-A.tex` |
| `1SPE-SECDEG-EV-B-corrige:SCALE` | `grading_scale` | `keep` | `chapitres/1SPE-SECOND-DEGRE/evaluations/1SPE-SECDEG-EV-B-corrige.tex` |
| `1SPE-SECDEG-EV-B` | `assessment` | `keep` | `chapitres/1SPE-SECOND-DEGRE/evaluations/1SPE-SECDEG-EV-B.tex` |
| `1SPE-SECDEG-EX-001` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-001.tex` |
| `1SPE-SECDEG-EX-002` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-002.tex` |
| `1SPE-SECDEG-EX-003` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-003.tex` |
| `1SPE-SECDEG-EX-004` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-004.tex` |
| `1SPE-SECDEG-EX-005` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-005.tex` |
| `1SPE-SECDEG-EX-006` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-006.tex` |
| `1SPE-SECDEG-EX-007` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-007.tex` |
| `1SPE-SECDEG-EX-008` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-008.tex` |
| `1SPE-SECDEG-EX-009` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-009.tex` |
| `1SPE-SECDEG-EX-010` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-010.tex` |
| `1SPE-SECDEG-EX-011` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-011.tex` |
| `1SPE-SECDEG-EX-012` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-012.tex` |
| `1SPE-SECDEG-EX-013` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-013.tex` |
| `1SPE-SECDEG-EX-014` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-014.tex` |
| `1SPE-SECDEG-EX-015` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-015.tex` |
| `1SPE-SECDEG-EX-016` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-016.tex` |
| `1SPE-SECDEG-EX-017` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-017.tex` |
| `1SPE-SECDEG-EX-018` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-018.tex` |
| `1SPE-SECDEG-EX-019` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-019.tex` |
| `1SPE-SECDEG-EX-020` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-020.tex` |
| `1SPE-SECDEG-EX-021` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-021.tex` |
| `1SPE-SECDEG-EX-022` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-022.tex` |
| `1SPE-SECDEG-EX-023` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-023.tex` |
| `1SPE-SECDEG-EX-024` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-024.tex` |
| `1SPE-SECDEG-EX-025` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-025.tex` |
| `1SPE-SECDEG-EX-026` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-026.tex` |
| `1SPE-SECDEG-EX-027` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-027.tex` |
| `1SPE-SECDEG-EX-028` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-028.tex` |
| `1SPE-SECDEG-EX-029` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-029.tex` |
| `1SPE-SECDEG-EX-030` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-030.tex` |
| `1SPE-SECDEG-EX-031` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-031.tex` |
| `1SPE-SECDEG-EX-032` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-032.tex` |
| `1SPE-SECDEG-EX-033` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-033.tex` |
| `1SPE-SECDEG-EX-034` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-034.tex` |
| `1SPE-SECDEG-EX-035` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-035.tex` |
| `1SPE-SECDEG-EX-036` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-036.tex` |
| `1SPE-SECDEG-EX-037` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-037.tex` |
| `1SPE-SECDEG-EX-038` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-038.tex` |
| `1SPE-SECDEG-EX-039` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-039.tex` |
| `1SPE-SECDEG-EX-040` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-040.tex` |
| `1SPE-SECDEG-EX-041` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-041.tex` |
| `1SPE-SECDEG-EX-042` | `exercise` | `keep` | `chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-042.tex` |
| `1SPE-SECDEG-ME-001` | `method` | `keep` | `chapitres/1SPE-SECOND-DEGRE/methodes/1SPE-SECDEG-ME-001.tex` |
| `1SPE-SECDEG-ME-002` | `method` | `keep` | `chapitres/1SPE-SECOND-DEGRE/methodes/1SPE-SECDEG-ME-002.tex` |
| `1SPE-SECDEG-ME-003` | `method` | `keep` | `chapitres/1SPE-SECOND-DEGRE/methodes/1SPE-SECDEG-ME-003.tex` |
| `1SPE-SECDEG-ME-004` | `method` | `keep` | `chapitres/1SPE-SECOND-DEGRE/methodes/1SPE-SECDEG-ME-004.tex` |
| `1SPE-SECDEG-ME-005` | `method` | `keep` | `chapitres/1SPE-SECOND-DEGRE/methodes/1SPE-SECDEG-ME-005.tex` |
| `1SPE-SECDEG-ME-006` | `method` | `keep` | `chapitres/1SPE-SECOND-DEGRE/methodes/1SPE-SECDEG-ME-006.tex` |
| `CHAPITRES/1SPE-SECOND-DEGRE/QCM/1SPE-SECDEG-QCM:JSON` | `qcm_json` | `keep` | `chapitres/1SPE-SECOND-DEGRE/qcm/1SPE-SECDEG-QCM.json` |
| `1SPE-SECDEG-QCM:TEX` | `qcm_tex` | `keep` | `chapitres/1SPE-SECOND-DEGRE/qcm/1SPE-SECDEG-QCM.tex` |
| `1SPE-SECDEG-FR-R1` | `remediation` | `keep` | `chapitres/1SPE-SECOND-DEGRE/remediation/1SPE-SECDEG-FR-R1.tex` |
| `1SPE-SECDEG-FR-R2` | `remediation` | `keep` | `chapitres/1SPE-SECOND-DEGRE/remediation/1SPE-SECDEG-FR-R2.tex` |
| `1SPE-SECDEG-FR-R3` | `remediation` | `keep` | `chapitres/1SPE-SECOND-DEGRE/remediation/1SPE-SECDEG-FR-R3.tex` |
| `1SPE-SECDEG-FR-R4` | `remediation` | `keep` | `chapitres/1SPE-SECOND-DEGRE/remediation/1SPE-SECDEG-FR-R4.tex` |
| `1SPE-SECDEG-FR-R5` | `remediation` | `keep` | `chapitres/1SPE-SECOND-DEGRE/remediation/1SPE-SECDEG-FR-R5.tex` |
| `1SPE-SECDEG-RE-C1` | `remediation` | `keep` | `chapitres/1SPE-SECOND-DEGRE/remediation/1SPE-SECDEG-RE-C1.tex` |
| `1SPE-SECDEG-RE-C2` | `remediation` | `keep` | `chapitres/1SPE-SECOND-DEGRE/remediation/1SPE-SECDEG-RE-C2.tex` |
| `1SPE-SECDEG-RE-C3` | `remediation` | `keep` | `chapitres/1SPE-SECOND-DEGRE/remediation/1SPE-SECDEG-RE-C3.tex` |
| `1SPE-SECDEG-RE-C4` | `remediation` | `keep` | `chapitres/1SPE-SECOND-DEGRE/remediation/1SPE-SECDEG-RE-C4.tex` |
| `1SPE-SECDEG-RE-C5` | `remediation` | `keep` | `chapitres/1SPE-SECOND-DEGRE/remediation/1SPE-SECDEG-RE-C5.tex` |
| `1SPE-SECDEG-RE-C6` | `remediation` | `keep` | `chapitres/1SPE-SECOND-DEGRE/remediation/1SPE-SECDEG-RE-C6.tex` |
| `00_ouverture:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/00_ouverture.sympy.json` |
| `01_diagnostic:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/01_diagnostic.sympy.json` |
| `07_td_contextualise:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/07_td_contextualise.sympy.json` |
| `07_td_fil_rouge:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/07_td_fil_rouge.sympy.json` |
| `10_C1_formes_trinome:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/10_C1_formes_trinome.sympy.json` |
| `11_C2_parabole_variations:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/11_C2_parabole_variations.sympy.json` |
| `12_C3_discriminant:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/12_C3_discriminant.sympy.json` |
| `13_C4_factorisation_signe:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/13_C4_factorisation_signe.sympy.json` |
| `14_C5_inequations:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/14_C5_inequations.sympy.json` |
| `15_C6_optimisation:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/15_C6_optimisation.sympy.json` |
| `1SPE-SECDEG-CO-001:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-001.sympy.json` |
| `1SPE-SECDEG-CO-002:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-002.sympy.json` |
| `1SPE-SECDEG-CO-003:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-003.sympy.json` |
| `1SPE-SECDEG-CO-004:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-004.sympy.json` |
| `1SPE-SECDEG-CO-005:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-005.sympy.json` |
| `1SPE-SECDEG-CO-006:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-006.sympy.json` |
| `1SPE-SECDEG-CO-007:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-007.sympy.json` |
| `1SPE-SECDEG-CO-008:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-008.sympy.json` |
| `1SPE-SECDEG-CO-009:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-009.sympy.json` |
| `1SPE-SECDEG-CO-010:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-010.sympy.json` |
| `1SPE-SECDEG-CO-011:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-011.sympy.json` |
| `1SPE-SECDEG-CO-012:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-012.sympy.json` |
| `1SPE-SECDEG-CO-013:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-013.sympy.json` |
| `1SPE-SECDEG-CO-014:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-014.sympy.json` |
| `1SPE-SECDEG-CO-015:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-015.sympy.json` |
| `1SPE-SECDEG-CO-016:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-016.sympy.json` |
| `1SPE-SECDEG-CO-017:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-017.sympy.json` |
| `1SPE-SECDEG-CO-018:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-018.sympy.json` |
| `1SPE-SECDEG-CO-019:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-019.sympy.json` |
| `1SPE-SECDEG-CO-020:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-020.sympy.json` |
| `1SPE-SECDEG-CO-021:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-021.sympy.json` |
| `1SPE-SECDEG-CO-022:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-022.sympy.json` |
| `1SPE-SECDEG-CO-023:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-023.sympy.json` |
| `1SPE-SECDEG-CO-024:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-024.sympy.json` |
| `1SPE-SECDEG-CO-025:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-025.sympy.json` |
| `1SPE-SECDEG-CO-026:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-026.sympy.json` |
| `1SPE-SECDEG-CO-027:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-027.sympy.json` |
| `1SPE-SECDEG-CO-028:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-028.sympy.json` |
| `1SPE-SECDEG-CO-029:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-029.sympy.json` |
| `1SPE-SECDEG-CO-030:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-030.sympy.json` |
| `1SPE-SECDEG-CO-031:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-031.sympy.json` |
| `1SPE-SECDEG-CO-032:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-032.sympy.json` |
| `1SPE-SECDEG-CO-033:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-033.sympy.json` |
| `1SPE-SECDEG-CO-034:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-034.sympy.json` |
| `1SPE-SECDEG-CO-035:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-035.sympy.json` |
| `1SPE-SECDEG-CO-036:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-036.sympy.json` |
| `1SPE-SECDEG-CO-037:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-037.sympy.json` |
| `1SPE-SECDEG-CO-038:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-038.sympy.json` |
| `1SPE-SECDEG-CO-039:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-039.sympy.json` |
| `1SPE-SECDEG-CO-040:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-040.sympy.json` |
| `1SPE-SECDEG-CO-041:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-041.sympy.json` |
| `1SPE-SECDEG-CO-042:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-CO-042.sympy.json` |
| `1SPE-SECDEG-EV-A-corrige:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EV-A-corrige.sympy.json` |
| `1SPE-SECDEG-EV-A:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EV-A.sympy.json` |
| `1SPE-SECDEG-EV-B-corrige:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EV-B-corrige.sympy.json` |
| `1SPE-SECDEG-EV-B:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EV-B.sympy.json` |
| `1SPE-SECDEG-EX-001:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-001.sympy.json` |
| `1SPE-SECDEG-EX-002:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-002.sympy.json` |
| `1SPE-SECDEG-EX-003:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-003.sympy.json` |
| `1SPE-SECDEG-EX-004:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-004.sympy.json` |
| `1SPE-SECDEG-EX-005:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-005.sympy.json` |
| `1SPE-SECDEG-EX-006:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-006.sympy.json` |
| `1SPE-SECDEG-EX-007:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-007.sympy.json` |
| `1SPE-SECDEG-EX-008:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-008.sympy.json` |
| `1SPE-SECDEG-EX-009:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-009.sympy.json` |
| `1SPE-SECDEG-EX-010:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-010.sympy.json` |
| `1SPE-SECDEG-EX-011:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-011.sympy.json` |
| `1SPE-SECDEG-EX-012:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-012.sympy.json` |
| `1SPE-SECDEG-EX-013:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-013.sympy.json` |
| `1SPE-SECDEG-EX-014:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-014.sympy.json` |
| `1SPE-SECDEG-EX-015:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-015.sympy.json` |
| `1SPE-SECDEG-EX-016:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-016.sympy.json` |
| `1SPE-SECDEG-EX-017:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-017.sympy.json` |
| `1SPE-SECDEG-EX-018:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-018.sympy.json` |
| `1SPE-SECDEG-EX-019:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-019.sympy.json` |
| `1SPE-SECDEG-EX-020:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-020.sympy.json` |
| `1SPE-SECDEG-EX-021:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-021.sympy.json` |
| `1SPE-SECDEG-EX-022:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-022.sympy.json` |
| `1SPE-SECDEG-EX-023:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-023.sympy.json` |
| `1SPE-SECDEG-EX-024:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-024.sympy.json` |
| `1SPE-SECDEG-EX-025:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-025.sympy.json` |
| `1SPE-SECDEG-EX-026:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-026.sympy.json` |
| `1SPE-SECDEG-EX-027:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-027.sympy.json` |
| `1SPE-SECDEG-EX-028:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-028.sympy.json` |
| `1SPE-SECDEG-EX-029:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-029.sympy.json` |
| `1SPE-SECDEG-EX-030:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-030.sympy.json` |
| `1SPE-SECDEG-EX-031:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-031.sympy.json` |
| `1SPE-SECDEG-EX-032:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-032.sympy.json` |
| `1SPE-SECDEG-EX-033:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-033.sympy.json` |
| `1SPE-SECDEG-EX-034:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-034.sympy.json` |
| `1SPE-SECDEG-EX-035:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-035.sympy.json` |
| `1SPE-SECDEG-EX-036:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-036.sympy.json` |
| `1SPE-SECDEG-EX-037:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-037.sympy.json` |
| `1SPE-SECDEG-EX-038:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-038.sympy.json` |
| `1SPE-SECDEG-EX-039:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-039.sympy.json` |
| `1SPE-SECDEG-EX-040:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-040.sympy.json` |
| `1SPE-SECDEG-EX-041:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-041.sympy.json` |
| `1SPE-SECDEG-EX-042:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-EX-042.sympy.json` |
| `1SPE-SECDEG-FR-R1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-FR-R1.sympy.json` |
| `1SPE-SECDEG-FR-R2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-FR-R2.sympy.json` |
| `1SPE-SECDEG-FR-R3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-FR-R3.sympy.json` |
| `1SPE-SECDEG-FR-R4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-FR-R4.sympy.json` |
| `1SPE-SECDEG-FR-R5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-FR-R5.sympy.json` |
| `1SPE-SECDEG-QCM:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-QCM.sympy.json` |
| `1SPE-SECDEG-RE-C1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-RE-C1.sympy.json` |
| `1SPE-SECDEG-RE-C2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-RE-C2.sympy.json` |
| `1SPE-SECDEG-RE-C3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-RE-C3.sympy.json` |
| `1SPE-SECDEG-RE-C4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-RE-C4.sympy.json` |
| `1SPE-SECDEG-RE-C5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-RE-C5.sympy.json` |
| `1SPE-SECDEG-RE-C6:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SECOND-DEGRE/validations/1SPE-SECDEG-RE-C6.sympy.json` |
| `CHAPITRES/1SPE-SUITES/LOT-0_RAPPORT` | `report` | `keep` | `chapitres/1SPE-SUITES/LOT-0_rapport.md` |
| `CHAPITRES/1SPE-SUITES/LOT-1_RAPPORT` | `report` | `keep` | `chapitres/1SPE-SUITES/LOT-1_rapport.md` |
| `CHAPITRES/1SPE-SUITES/LOT-2_RAPPORT` | `report` | `keep` | `chapitres/1SPE-SUITES/LOT-2_rapport.md` |
| `CHAPITRES/1SPE-SUITES/LOT-3_RAPPORT` | `report` | `keep` | `chapitres/1SPE-SUITES/LOT-3_rapport.md` |
| `CHAPITRES/1SPE-SUITES/LOT-4_RAPPORT` | `report` | `keep` | `chapitres/1SPE-SUITES/LOT-4_rapport.md` |
| `CHAPITRES/1SPE-SUITES/LOT-5_RAPPORT` | `report` | `keep` | `chapitres/1SPE-SUITES/LOT-5_rapport.md` |
| `CHAPITRES/1SPE-SUITES/LOT-6_RAPPORT` | `report` | `keep` | `chapitres/1SPE-SUITES/LOT-6_rapport.md` |
| `CHAPITRES/1SPE-SUITES/LOT-7_RAPPORT` | `report` | `keep` | `chapitres/1SPE-SUITES/LOT-7_rapport.md` |
| `CHAPITRES/1SPE-SUITES/CONTRAT` | `chapter_contract` | `keep` | `chapitres/1SPE-SUITES/contrat.yaml` |
| `CHAPITRES/1SPE-SUITES/CORRIGES/.GITKEEP` | `solution` | `fix` (invalid_metadata) | `chapitres/1SPE-SUITES/corriges/.gitkeep` |
| `1SPE-SUITES-CO-001` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-001.tex` |
| `1SPE-SUITES-CO-002` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-002.tex` |
| `1SPE-SUITES-CO-003` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-003.tex` |
| `1SPE-SUITES-CO-004` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-004.tex` |
| `1SPE-SUITES-CO-005` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-005.tex` |
| `1SPE-SUITES-CO-006` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-006.tex` |
| `1SPE-SUITES-CO-007` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-007.tex` |
| `1SPE-SUITES-CO-008` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-008.tex` |
| `1SPE-SUITES-CO-009` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-009.tex` |
| `1SPE-SUITES-CO-010` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-010.tex` |
| `1SPE-SUITES-CO-011` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-011.tex` |
| `1SPE-SUITES-CO-012` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-012.tex` |
| `1SPE-SUITES-CO-013` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-013.tex` |
| `1SPE-SUITES-CO-014` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-014.tex` |
| `1SPE-SUITES-CO-015` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-015.tex` |
| `1SPE-SUITES-CO-016` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-016.tex` |
| `1SPE-SUITES-CO-017` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-017.tex` |
| `1SPE-SUITES-CO-018` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-018.tex` |
| `1SPE-SUITES-CO-019` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-019.tex` |
| `1SPE-SUITES-CO-020` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-020.tex` |
| `1SPE-SUITES-CO-021` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-021.tex` |
| `1SPE-SUITES-CO-022` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-022.tex` |
| `1SPE-SUITES-CO-023` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-023.tex` |
| `1SPE-SUITES-CO-024` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-024.tex` |
| `1SPE-SUITES-CO-025` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-025.tex` |
| `1SPE-SUITES-CO-026` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-026.tex` |
| `1SPE-SUITES-CO-027` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-027.tex` |
| `1SPE-SUITES-CO-028` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-028.tex` |
| `1SPE-SUITES-CO-029` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-029.tex` |
| `1SPE-SUITES-CO-030` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-030.tex` |
| `1SPE-SUITES-CO-031` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-031.tex` |
| `1SPE-SUITES-CO-032` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-032.tex` |
| `1SPE-SUITES-CO-033` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-033.tex` |
| `1SPE-SUITES-CO-034` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-034.tex` |
| `1SPE-SUITES-CO-035` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-035.tex` |
| `1SPE-SUITES-CO-036` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-036.tex` |
| `1SPE-SUITES-CO-037` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-037.tex` |
| `1SPE-SUITES-CO-038` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-038.tex` |
| `1SPE-SUITES-CO-039` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-039.tex` |
| `1SPE-SUITES-CO-040` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-040.tex` |
| `1SPE-SUITES-CO-041` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-041.tex` |
| `1SPE-SUITES-CO-042` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-042.tex` |
| `1SPE-SUITES-CO-043` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-043.tex` |
| `1SPE-SUITES-CO-044` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-044.tex` |
| `1SPE-SUITES-CO-045` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-045.tex` |
| `1SPE-SUITES-CO-046` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-046.tex` |
| `1SPE-SUITES-CO-047` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-047.tex` |
| `1SPE-SUITES-CO-048` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-048.tex` |
| `1SPE-SUITES-CO-049` | `solution` | `keep` | `chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-049.tex` |
| `CHAPITRES/1SPE-SUITES/COURS/.GITKEEP` | `course` | `fix` (invalid_metadata) | `chapitres/1SPE-SUITES/cours/.gitkeep` |
| `1SPE-SUITES-COURS-00` | `course` | `keep` | `chapitres/1SPE-SUITES/cours/00_ouverture.tex` |
| `1SPE-SUITES-COURS-01` | `course` | `keep` | `chapitres/1SPE-SUITES/cours/01_diagnostic.tex` |
| `1SPE-SUITES-COURS-07-TC` | `transversal` | `keep` | `chapitres/1SPE-SUITES/cours/07_td_contextualise.tex` |
| `1SPE-SUITES-COURS-07-FR` | `transversal` | `keep` | `chapitres/1SPE-SUITES/cours/07_td_fil_rouge.tex` |
| `1SPE-SUITES-CR-010` | `course` | `keep` | `chapitres/1SPE-SUITES/cours/10_C1_generalites_suites.tex` |
| `1SPE-SUITES-CR-011` | `course` | `keep` | `chapitres/1SPE-SUITES/cours/11_C2_suites_arithmetiques.tex` |
| `1SPE-SUITES-CR-012` | `course` | `keep` | `chapitres/1SPE-SUITES/cours/12_C3_suites_geometriques.tex` |
| `1SPE-SUITES-CR-013` | `course` | `keep` | `chapitres/1SPE-SUITES/cours/13_C4_sommes.tex` |
| `1SPE-SUITES-CR-014` | `course` | `keep` | `chapitres/1SPE-SUITES/cours/14_C5_variations.tex` |
| `1SPE-SUITES-CR-015` | `course` | `keep` | `chapitres/1SPE-SUITES/cours/15_C6_modelisation.tex` |
| `1SPE-SUITES-CR-016` | `course` | `keep` | `chapitres/1SPE-SUITES/cours/16_C7_algorithmique.tex` |
| `CHAPITRES/1SPE-SUITES/DOSSIER_CURATION` | `chapter_metadata` | `keep` | `chapitres/1SPE-SUITES/dossier_curation.json` |
| `CHAPITRES/1SPE-SUITES/EVALUATIONS/.GITKEEP` | `assessment` | `fix` (invalid_metadata) | `chapitres/1SPE-SUITES/evaluations/.gitkeep` |
| `1SPE-SUITES-EV-A-corrige:SCALE` | `grading_scale` | `keep` | `chapitres/1SPE-SUITES/evaluations/1SPE-SUITES-EV-A-corrige.tex` |
| `1SPE-SUITES-EV-A` | `assessment` | `keep` | `chapitres/1SPE-SUITES/evaluations/1SPE-SUITES-EV-A.tex` |
| `1SPE-SUITES-EV-B-corrige:SCALE` | `grading_scale` | `keep` | `chapitres/1SPE-SUITES/evaluations/1SPE-SUITES-EV-B-corrige.tex` |
| `1SPE-SUITES-EV-B` | `assessment` | `keep` | `chapitres/1SPE-SUITES/evaluations/1SPE-SUITES-EV-B.tex` |
| `1SPE-SUITES-EX-001` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-001.tex` |
| `1SPE-SUITES-EX-002` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-002.tex` |
| `1SPE-SUITES-EX-003` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-003.tex` |
| `1SPE-SUITES-EX-004` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-004.tex` |
| `1SPE-SUITES-EX-005` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-005.tex` |
| `1SPE-SUITES-EX-006` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-006.tex` |
| `1SPE-SUITES-EX-007` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-007.tex` |
| `1SPE-SUITES-EX-008` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-008.tex` |
| `1SPE-SUITES-EX-009` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-009.tex` |
| `1SPE-SUITES-EX-010` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-010.tex` |
| `1SPE-SUITES-EX-011` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-011.tex` |
| `1SPE-SUITES-EX-012` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-012.tex` |
| `1SPE-SUITES-EX-013` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-013.tex` |
| `1SPE-SUITES-EX-014` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-014.tex` |
| `1SPE-SUITES-EX-015` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-015.tex` |
| `1SPE-SUITES-EX-016` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-016.tex` |
| `1SPE-SUITES-EX-017` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-017.tex` |
| `1SPE-SUITES-EX-018` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-018.tex` |
| `1SPE-SUITES-EX-019` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-019.tex` |
| `1SPE-SUITES-EX-020` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-020.tex` |
| `1SPE-SUITES-EX-021` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-021.tex` |
| `1SPE-SUITES-EX-022` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-022.tex` |
| `1SPE-SUITES-EX-023` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-023.tex` |
| `1SPE-SUITES-EX-024` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-024.tex` |
| `1SPE-SUITES-EX-025` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-025.tex` |
| `1SPE-SUITES-EX-026` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-026.tex` |
| `1SPE-SUITES-EX-027` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-027.tex` |
| `1SPE-SUITES-EX-028` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-028.tex` |
| `1SPE-SUITES-EX-029` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-029.tex` |
| `1SPE-SUITES-EX-030` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-030.tex` |
| `1SPE-SUITES-EX-031` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-031.tex` |
| `1SPE-SUITES-EX-032` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-032.tex` |
| `1SPE-SUITES-EX-033` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-033.tex` |
| `1SPE-SUITES-EX-034` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-034.tex` |
| `1SPE-SUITES-EX-035` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-035.tex` |
| `1SPE-SUITES-EX-036` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-036.tex` |
| `1SPE-SUITES-EX-037` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-037.tex` |
| `1SPE-SUITES-EX-038` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-038.tex` |
| `1SPE-SUITES-EX-039` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-039.tex` |
| `1SPE-SUITES-EX-040` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-040.tex` |
| `1SPE-SUITES-EX-041` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-041.tex` |
| `1SPE-SUITES-EX-042` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-042.tex` |
| `1SPE-SUITES-EX-043` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-043.tex` |
| `1SPE-SUITES-EX-044` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-044.tex` |
| `1SPE-SUITES-EX-045` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-045.tex` |
| `1SPE-SUITES-EX-046` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-046.tex` |
| `1SPE-SUITES-EX-047` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-047.tex` |
| `1SPE-SUITES-EX-048` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-048.tex` |
| `1SPE-SUITES-EX-049` | `exercise` | `keep` | `chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-049.tex` |
| `CHAPITRES/1SPE-SUITES/METHODES/.GITKEEP` | `method` | `fix` (invalid_metadata) | `chapitres/1SPE-SUITES/methodes/.gitkeep` |
| `1SPE-SUITES-ME-001` | `method` | `keep` | `chapitres/1SPE-SUITES/methodes/1SPE-SUITES-ME-001.tex` |
| `1SPE-SUITES-ME-002` | `method` | `keep` | `chapitres/1SPE-SUITES/methodes/1SPE-SUITES-ME-002.tex` |
| `1SPE-SUITES-ME-003` | `method` | `keep` | `chapitres/1SPE-SUITES/methodes/1SPE-SUITES-ME-003.tex` |
| `1SPE-SUITES-ME-004` | `method` | `keep` | `chapitres/1SPE-SUITES/methodes/1SPE-SUITES-ME-004.tex` |
| `1SPE-SUITES-ME-005` | `method` | `keep` | `chapitres/1SPE-SUITES/methodes/1SPE-SUITES-ME-005.tex` |
| `1SPE-SUITES-ME-006` | `method` | `keep` | `chapitres/1SPE-SUITES/methodes/1SPE-SUITES-ME-006.tex` |
| `1SPE-SUITES-ME-007` | `method` | `keep` | `chapitres/1SPE-SUITES/methodes/1SPE-SUITES-ME-007.tex` |
| `CHAPITRES/1SPE-SUITES/QCM/.GITKEEP:TEX` | `qcm_tex` | `fix` (invalid_metadata) | `chapitres/1SPE-SUITES/qcm/.gitkeep` |
| `CHAPITRES/1SPE-SUITES/QCM/1SPE-SUITES-QCM:JSON` | `qcm_json` | `keep` | `chapitres/1SPE-SUITES/qcm/1SPE-SUITES-QCM.json` |
| `1SPE-SUITES-QCM:TEX` | `qcm_tex` | `keep` | `chapitres/1SPE-SUITES/qcm/1SPE-SUITES-QCM.tex` |
| `CHAPITRES/1SPE-SUITES/REMEDIATION/.GITKEEP` | `remediation` | `fix` (invalid_metadata) | `chapitres/1SPE-SUITES/remediation/.gitkeep` |
| `1SPE-SUITES-FR-R1` | `remediation` | `keep` | `chapitres/1SPE-SUITES/remediation/1SPE-SUITES-FR-R1.tex` |
| `1SPE-SUITES-FR-R2` | `remediation` | `keep` | `chapitres/1SPE-SUITES/remediation/1SPE-SUITES-FR-R2.tex` |
| `1SPE-SUITES-FR-R3` | `remediation` | `keep` | `chapitres/1SPE-SUITES/remediation/1SPE-SUITES-FR-R3.tex` |
| `1SPE-SUITES-FR-R4` | `remediation` | `keep` | `chapitres/1SPE-SUITES/remediation/1SPE-SUITES-FR-R4.tex` |
| `1SPE-SUITES-FR-R5` | `remediation` | `keep` | `chapitres/1SPE-SUITES/remediation/1SPE-SUITES-FR-R5.tex` |
| `1SPE-SUITES-RE-C1` | `remediation` | `keep` | `chapitres/1SPE-SUITES/remediation/1SPE-SUITES-RE-C1.tex` |
| `1SPE-SUITES-RE-C2` | `remediation` | `keep` | `chapitres/1SPE-SUITES/remediation/1SPE-SUITES-RE-C2.tex` |
| `1SPE-SUITES-RE-C3` | `remediation` | `keep` | `chapitres/1SPE-SUITES/remediation/1SPE-SUITES-RE-C3.tex` |
| `1SPE-SUITES-RE-C4` | `remediation` | `keep` | `chapitres/1SPE-SUITES/remediation/1SPE-SUITES-RE-C4.tex` |
| `1SPE-SUITES-RE-C5` | `remediation` | `keep` | `chapitres/1SPE-SUITES/remediation/1SPE-SUITES-RE-C5.tex` |
| `1SPE-SUITES-RE-C6` | `remediation` | `keep` | `chapitres/1SPE-SUITES/remediation/1SPE-SUITES-RE-C6.tex` |
| `1SPE-SUITES-RE-C7` | `remediation` | `keep` | `chapitres/1SPE-SUITES/remediation/1SPE-SUITES-RE-C7.tex` |
| `00_ouverture:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/00_ouverture.similarity.json` |
| `00_ouverture:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/00_ouverture.sympy.json` |
| `01_diagnostic:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/01_diagnostic.similarity.json` |
| `01_diagnostic:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/01_diagnostic.sympy.json` |
| `07_td_contextualise:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/07_td_contextualise.similarity.json` |
| `07_td_contextualise:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/07_td_contextualise.sympy.json` |
| `07_td_fil_rouge:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/07_td_fil_rouge.similarity.json` |
| `07_td_fil_rouge:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/07_td_fil_rouge.sympy.json` |
| `10_C1_generalites_suites:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/10_C1_generalites_suites.similarity.json` |
| `10_C1_generalites_suites:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/10_C1_generalites_suites.sympy.json` |
| `11_C2_suites_arithmetiques:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/11_C2_suites_arithmetiques.similarity.json` |
| `11_C2_suites_arithmetiques:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/11_C2_suites_arithmetiques.sympy.json` |
| `12_C3_suites_geometriques:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/12_C3_suites_geometriques.similarity.json` |
| `12_C3_suites_geometriques:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/12_C3_suites_geometriques.sympy.json` |
| `13_C4_sommes:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/13_C4_sommes.similarity.json` |
| `13_C4_sommes:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/13_C4_sommes.sympy.json` |
| `14_C5_variations:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/14_C5_variations.similarity.json` |
| `14_C5_variations:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/14_C5_variations.sympy.json` |
| `15_C6_modelisation:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/15_C6_modelisation.similarity.json` |
| `15_C6_modelisation:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/15_C6_modelisation.sympy.json` |
| `16_C7_algorithmique:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/16_C7_algorithmique.similarity.json` |
| `16_C7_algorithmique:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/16_C7_algorithmique.sympy.json` |
| `1SPE-SUITES-CO-001:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-001.similarity.json` |
| `1SPE-SUITES-CO-001:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-001.sympy.json` |
| `1SPE-SUITES-CO-002:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-002.similarity.json` |
| `1SPE-SUITES-CO-002:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-002.sympy.json` |
| `1SPE-SUITES-CO-003:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-003.similarity.json` |
| `1SPE-SUITES-CO-003:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-003.sympy.json` |
| `1SPE-SUITES-CO-004:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-004.similarity.json` |
| `1SPE-SUITES-CO-004:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-004.sympy.json` |
| `1SPE-SUITES-CO-005:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-005.similarity.json` |
| `1SPE-SUITES-CO-005:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-005.sympy.json` |
| `1SPE-SUITES-CO-006:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-006.similarity.json` |
| `1SPE-SUITES-CO-006:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-006.sympy.json` |
| `1SPE-SUITES-CO-007:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-007.similarity.json` |
| `1SPE-SUITES-CO-007:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-007.sympy.json` |
| `1SPE-SUITES-CO-008:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-008.similarity.json` |
| `1SPE-SUITES-CO-008:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-008.sympy.json` |
| `1SPE-SUITES-CO-009:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-009.similarity.json` |
| `1SPE-SUITES-CO-009:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-009.sympy.json` |
| `1SPE-SUITES-CO-010:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-010.similarity.json` |
| `1SPE-SUITES-CO-010:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-010.sympy.json` |
| `1SPE-SUITES-CO-011:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-011.similarity.json` |
| `1SPE-SUITES-CO-011:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-011.sympy.json` |
| `1SPE-SUITES-CO-012:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-012.similarity.json` |
| `1SPE-SUITES-CO-012:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-012.sympy.json` |
| `1SPE-SUITES-CO-013:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-013.similarity.json` |
| `1SPE-SUITES-CO-013:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-013.sympy.json` |
| `1SPE-SUITES-CO-014:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-014.similarity.json` |
| `1SPE-SUITES-CO-014:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-014.sympy.json` |
| `1SPE-SUITES-CO-015:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-015.similarity.json` |
| `1SPE-SUITES-CO-015:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-015.sympy.json` |
| `1SPE-SUITES-CO-016:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-016.similarity.json` |
| `1SPE-SUITES-CO-016:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-016.sympy.json` |
| `1SPE-SUITES-CO-017:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-017.similarity.json` |
| `1SPE-SUITES-CO-017:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-017.sympy.json` |
| `1SPE-SUITES-CO-018:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-018.similarity.json` |
| `1SPE-SUITES-CO-018:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-018.sympy.json` |
| `1SPE-SUITES-CO-019:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-019.similarity.json` |
| `1SPE-SUITES-CO-019:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-019.sympy.json` |
| `1SPE-SUITES-CO-020:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-020.similarity.json` |
| `1SPE-SUITES-CO-020:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-020.sympy.json` |
| `1SPE-SUITES-CO-021:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-021.similarity.json` |
| `1SPE-SUITES-CO-021:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-021.sympy.json` |
| `1SPE-SUITES-CO-022:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-022.similarity.json` |
| `1SPE-SUITES-CO-022:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-022.sympy.json` |
| `1SPE-SUITES-CO-023:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-023.similarity.json` |
| `1SPE-SUITES-CO-023:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-023.sympy.json` |
| `1SPE-SUITES-CO-024:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-024.similarity.json` |
| `1SPE-SUITES-CO-024:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-024.sympy.json` |
| `1SPE-SUITES-CO-025:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-025.similarity.json` |
| `1SPE-SUITES-CO-025:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-025.sympy.json` |
| `1SPE-SUITES-CO-026:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-026.similarity.json` |
| `1SPE-SUITES-CO-026:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-026.sympy.json` |
| `1SPE-SUITES-CO-027:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-027.similarity.json` |
| `1SPE-SUITES-CO-027:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-027.sympy.json` |
| `1SPE-SUITES-CO-028:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-028.similarity.json` |
| `1SPE-SUITES-CO-028:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-028.sympy.json` |
| `1SPE-SUITES-CO-029:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-029.similarity.json` |
| `1SPE-SUITES-CO-029:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-029.sympy.json` |
| `1SPE-SUITES-CO-030:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-030.similarity.json` |
| `1SPE-SUITES-CO-030:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-030.sympy.json` |
| `1SPE-SUITES-CO-031:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-031.similarity.json` |
| `1SPE-SUITES-CO-031:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-031.sympy.json` |
| `1SPE-SUITES-CO-032:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-032.similarity.json` |
| `1SPE-SUITES-CO-032:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-032.sympy.json` |
| `1SPE-SUITES-CO-033:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-033.similarity.json` |
| `1SPE-SUITES-CO-033:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-033.sympy.json` |
| `1SPE-SUITES-CO-034:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-034.similarity.json` |
| `1SPE-SUITES-CO-034:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-034.sympy.json` |
| `1SPE-SUITES-CO-035:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-035.similarity.json` |
| `1SPE-SUITES-CO-035:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-035.sympy.json` |
| `1SPE-SUITES-CO-036:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-036.similarity.json` |
| `1SPE-SUITES-CO-036:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-036.sympy.json` |
| `1SPE-SUITES-CO-037:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-037.similarity.json` |
| `1SPE-SUITES-CO-037:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-037.sympy.json` |
| `1SPE-SUITES-CO-038:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-038.similarity.json` |
| `1SPE-SUITES-CO-038:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-038.sympy.json` |
| `1SPE-SUITES-CO-039:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-039.similarity.json` |
| `1SPE-SUITES-CO-039:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-039.sympy.json` |
| `1SPE-SUITES-CO-040:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-040.similarity.json` |
| `1SPE-SUITES-CO-040:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-040.sympy.json` |
| `1SPE-SUITES-CO-041:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-041.similarity.json` |
| `1SPE-SUITES-CO-041:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-041.sympy.json` |
| `1SPE-SUITES-CO-042:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-042.similarity.json` |
| `1SPE-SUITES-CO-042:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-042.sympy.json` |
| `1SPE-SUITES-CO-043:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-043.similarity.json` |
| `1SPE-SUITES-CO-043:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-043.sympy.json` |
| `1SPE-SUITES-CO-044:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-044.similarity.json` |
| `1SPE-SUITES-CO-044:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-044.sympy.json` |
| `1SPE-SUITES-CO-045:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-045.similarity.json` |
| `1SPE-SUITES-CO-045:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-045.sympy.json` |
| `1SPE-SUITES-CO-046:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-046.similarity.json` |
| `1SPE-SUITES-CO-046:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-046.sympy.json` |
| `1SPE-SUITES-CO-047:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-047.similarity.json` |
| `1SPE-SUITES-CO-047:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-047.sympy.json` |
| `1SPE-SUITES-CO-048:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-048.similarity.json` |
| `1SPE-SUITES-CO-048:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-048.sympy.json` |
| `1SPE-SUITES-CO-049:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-049.similarity.json` |
| `1SPE-SUITES-CO-049:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-CO-049.sympy.json` |
| `1SPE-SUITES-EV-A-corrige:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EV-A-corrige.similarity.json` |
| `1SPE-SUITES-EV-A-corrige:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EV-A-corrige.sympy.json` |
| `1SPE-SUITES-EV-A:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EV-A.similarity.json` |
| `1SPE-SUITES-EV-A:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EV-A.sympy.json` |
| `1SPE-SUITES-EV-B-corrige:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EV-B-corrige.similarity.json` |
| `1SPE-SUITES-EV-B-corrige:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EV-B-corrige.sympy.json` |
| `1SPE-SUITES-EV-B:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EV-B.similarity.json` |
| `1SPE-SUITES-EV-B:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EV-B.sympy.json` |
| `1SPE-SUITES-EX-001:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-001.similarity.json` |
| `1SPE-SUITES-EX-001:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-001.sympy.json` |
| `1SPE-SUITES-EX-002:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-002.similarity.json` |
| `1SPE-SUITES-EX-002:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-002.sympy.json` |
| `1SPE-SUITES-EX-003:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-003.similarity.json` |
| `1SPE-SUITES-EX-003:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-003.sympy.json` |
| `1SPE-SUITES-EX-004:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-004.similarity.json` |
| `1SPE-SUITES-EX-004:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-004.sympy.json` |
| `1SPE-SUITES-EX-005:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-005.similarity.json` |
| `1SPE-SUITES-EX-005:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-005.sympy.json` |
| `1SPE-SUITES-EX-006:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-006.similarity.json` |
| `1SPE-SUITES-EX-006:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-006.sympy.json` |
| `1SPE-SUITES-EX-007:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-007.similarity.json` |
| `1SPE-SUITES-EX-007:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-007.sympy.json` |
| `1SPE-SUITES-EX-008:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-008.similarity.json` |
| `1SPE-SUITES-EX-008:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-008.sympy.json` |
| `1SPE-SUITES-EX-009:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-009.similarity.json` |
| `1SPE-SUITES-EX-009:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-009.sympy.json` |
| `1SPE-SUITES-EX-010:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-010.similarity.json` |
| `1SPE-SUITES-EX-010:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-010.sympy.json` |
| `1SPE-SUITES-EX-011:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-011.similarity.json` |
| `1SPE-SUITES-EX-011:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-011.sympy.json` |
| `1SPE-SUITES-EX-012:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-012.similarity.json` |
| `1SPE-SUITES-EX-012:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-012.sympy.json` |
| `1SPE-SUITES-EX-013:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-013.similarity.json` |
| `1SPE-SUITES-EX-013:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-013.sympy.json` |
| `1SPE-SUITES-EX-014:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-014.similarity.json` |
| `1SPE-SUITES-EX-014:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-014.sympy.json` |
| `1SPE-SUITES-EX-015:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-015.similarity.json` |
| `1SPE-SUITES-EX-015:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-015.sympy.json` |
| `1SPE-SUITES-EX-016:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-016.similarity.json` |
| `1SPE-SUITES-EX-016:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-016.sympy.json` |
| `1SPE-SUITES-EX-017:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-017.similarity.json` |
| `1SPE-SUITES-EX-017:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-017.sympy.json` |
| `1SPE-SUITES-EX-018:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-018.similarity.json` |
| `1SPE-SUITES-EX-018:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-018.sympy.json` |
| `1SPE-SUITES-EX-019:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-019.similarity.json` |
| `1SPE-SUITES-EX-019:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-019.sympy.json` |
| `1SPE-SUITES-EX-020:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-020.similarity.json` |
| `1SPE-SUITES-EX-020:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-020.sympy.json` |
| `1SPE-SUITES-EX-021:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-021.similarity.json` |
| `1SPE-SUITES-EX-021:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-021.sympy.json` |
| `1SPE-SUITES-EX-022:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-022.similarity.json` |
| `1SPE-SUITES-EX-022:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-022.sympy.json` |
| `1SPE-SUITES-EX-023:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-023.similarity.json` |
| `1SPE-SUITES-EX-023:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-023.sympy.json` |
| `1SPE-SUITES-EX-024:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-024.similarity.json` |
| `1SPE-SUITES-EX-024:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-024.sympy.json` |
| `1SPE-SUITES-EX-025:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-025.similarity.json` |
| `1SPE-SUITES-EX-025:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-025.sympy.json` |
| `1SPE-SUITES-EX-026:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-026.similarity.json` |
| `1SPE-SUITES-EX-026:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-026.sympy.json` |
| `1SPE-SUITES-EX-027:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-027.similarity.json` |
| `1SPE-SUITES-EX-027:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-027.sympy.json` |
| `1SPE-SUITES-EX-028:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-028.similarity.json` |
| `1SPE-SUITES-EX-028:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-028.sympy.json` |
| `1SPE-SUITES-EX-029:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-029.similarity.json` |
| `1SPE-SUITES-EX-029:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-029.sympy.json` |
| `1SPE-SUITES-EX-030:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-030.similarity.json` |
| `1SPE-SUITES-EX-030:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-030.sympy.json` |
| `1SPE-SUITES-EX-031:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-031.similarity.json` |
| `1SPE-SUITES-EX-031:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-031.sympy.json` |
| `1SPE-SUITES-EX-032:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-032.similarity.json` |
| `1SPE-SUITES-EX-032:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-032.sympy.json` |
| `1SPE-SUITES-EX-033:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-033.similarity.json` |
| `1SPE-SUITES-EX-033:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-033.sympy.json` |
| `1SPE-SUITES-EX-034:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-034.similarity.json` |
| `1SPE-SUITES-EX-034:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-034.sympy.json` |
| `1SPE-SUITES-EX-035:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-035.similarity.json` |
| `1SPE-SUITES-EX-035:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-035.sympy.json` |
| `1SPE-SUITES-EX-036:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-036.similarity.json` |
| `1SPE-SUITES-EX-036:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-036.sympy.json` |
| `1SPE-SUITES-EX-037:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-037.similarity.json` |
| `1SPE-SUITES-EX-037:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-037.sympy.json` |
| `1SPE-SUITES-EX-038:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-038.similarity.json` |
| `1SPE-SUITES-EX-038:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-038.sympy.json` |
| `1SPE-SUITES-EX-039:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-039.similarity.json` |
| `1SPE-SUITES-EX-039:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-039.sympy.json` |
| `1SPE-SUITES-EX-040:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-040.similarity.json` |
| `1SPE-SUITES-EX-040:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-040.sympy.json` |
| `1SPE-SUITES-EX-041:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-041.similarity.json` |
| `1SPE-SUITES-EX-041:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-041.sympy.json` |
| `1SPE-SUITES-EX-042:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-042.similarity.json` |
| `1SPE-SUITES-EX-042:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-042.sympy.json` |
| `1SPE-SUITES-EX-043:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-043.similarity.json` |
| `1SPE-SUITES-EX-043:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-043.sympy.json` |
| `1SPE-SUITES-EX-044:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-044.similarity.json` |
| `1SPE-SUITES-EX-044:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-044.sympy.json` |
| `1SPE-SUITES-EX-045:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-045.similarity.json` |
| `1SPE-SUITES-EX-045:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-045.sympy.json` |
| `1SPE-SUITES-EX-046:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-046.similarity.json` |
| `1SPE-SUITES-EX-046:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-046.sympy.json` |
| `1SPE-SUITES-EX-047:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-047.similarity.json` |
| `1SPE-SUITES-EX-047:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-047.sympy.json` |
| `1SPE-SUITES-EX-048:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-048.similarity.json` |
| `1SPE-SUITES-EX-048:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-048.sympy.json` |
| `1SPE-SUITES-EX-049:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-049.similarity.json` |
| `1SPE-SUITES-EX-049:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-EX-049.sympy.json` |
| `1SPE-SUITES-FR-R1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-FR-R1.sympy.json` |
| `1SPE-SUITES-FR-R2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-FR-R2.sympy.json` |
| `1SPE-SUITES-FR-R3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-FR-R3.sympy.json` |
| `1SPE-SUITES-FR-R4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-FR-R4.sympy.json` |
| `1SPE-SUITES-FR-R5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-FR-R5.sympy.json` |
| `1SPE-SUITES-ME-001:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-ME-001.similarity.json` |
| `1SPE-SUITES-ME-002:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-ME-002.similarity.json` |
| `1SPE-SUITES-ME-003:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-ME-003.similarity.json` |
| `1SPE-SUITES-ME-004:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-ME-004.similarity.json` |
| `1SPE-SUITES-ME-005:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-ME-005.similarity.json` |
| `1SPE-SUITES-ME-006:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-ME-006.similarity.json` |
| `1SPE-SUITES-ME-007:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-ME-007.similarity.json` |
| `1SPE-SUITES-QCM:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-QCM.sympy.json` |
| `1SPE-SUITES-RE-C1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-RE-C1.sympy.json` |
| `1SPE-SUITES-RE-C2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-RE-C2.sympy.json` |
| `1SPE-SUITES-RE-C3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-RE-C3.sympy.json` |
| `1SPE-SUITES-RE-C4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-RE-C4.sympy.json` |
| `1SPE-SUITES-RE-C5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-RE-C5.sympy.json` |
| `1SPE-SUITES-RE-C6:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-RE-C6.sympy.json` |
| `1SPE-SUITES-RE-C7:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-SUITES/validations/1SPE-SUITES-RE-C7.sympy.json` |
| `CHAPITRES/1SPE-TRIGONOMETRIE/LOT-0_RAPPORT` | `report` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/LOT-0_rapport.md` |
| `CHAPITRES/1SPE-TRIGONOMETRIE/LOT-1_RAPPORT` | `report` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/LOT-1_rapport.md` |
| `CHAPITRES/1SPE-TRIGONOMETRIE/LOT-2_RAPPORT` | `report` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/LOT-2_rapport.md` |
| `CHAPITRES/1SPE-TRIGONOMETRIE/LOT-3_RAPPORT` | `report` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/LOT-3_rapport.md` |
| `CHAPITRES/1SPE-TRIGONOMETRIE/LOT-4_RAPPORT` | `report` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/LOT-4_rapport.md` |
| `CHAPITRES/1SPE-TRIGONOMETRIE/LOT-5_RAPPORT` | `report` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/LOT-5_rapport.md` |
| `CHAPITRES/1SPE-TRIGONOMETRIE/LOT-6_RAPPORT` | `report` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/LOT-6_rapport.md` |
| `CHAPITRES/1SPE-TRIGONOMETRIE/LOT-7_ADDENDUM_BO2026` | `report` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/LOT-7_addendum_bo2026.md` |
| `CHAPITRES/1SPE-TRIGONOMETRIE/LOT-7_RAPPORT` | `report` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/LOT-7_rapport.md` |
| `CHAPITRES/1SPE-TRIGONOMETRIE/CONTRAT` | `chapter_contract` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/contrat.yaml` |
| `1SPE-TRIGO-CO-001` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-001.tex` |
| `1SPE-TRIGO-CO-002` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-002.tex` |
| `1SPE-TRIGO-CO-003` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-003.tex` |
| `1SPE-TRIGO-CO-004` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-004.tex` |
| `1SPE-TRIGO-CO-005` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-005.tex` |
| `1SPE-TRIGO-CO-006` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-006.tex` |
| `1SPE-TRIGO-CO-007` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-007.tex` |
| `1SPE-TRIGO-CO-008` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-008.tex` |
| `1SPE-TRIGO-CO-009` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-009.tex` |
| `1SPE-TRIGO-CO-010` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-010.tex` |
| `1SPE-TRIGO-CO-011` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-011.tex` |
| `1SPE-TRIGO-CO-012` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-012.tex` |
| `1SPE-TRIGO-CO-013` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-013.tex` |
| `1SPE-TRIGO-CO-014` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-014.tex` |
| `1SPE-TRIGO-CO-015` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-015.tex` |
| `1SPE-TRIGO-CO-016` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-016.tex` |
| `1SPE-TRIGO-CO-017` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-017.tex` |
| `1SPE-TRIGO-CO-018` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-018.tex` |
| `1SPE-TRIGO-CO-019` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-019.tex` |
| `1SPE-TRIGO-CO-020` | `solution` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/corriges/1SPE-TRIGO-CO-020.tex` |
| `1SPE-TRIGO-TD-CONTEXTUALISE` | `transversal` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/cours/07_td_contextualise.tex` |
| `1SPE-TRIGO-TD-FIL-ROUGE` | `transversal` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/cours/07_td_fil_rouge.tex` |
| `1SPE-TRIGO-CR-010` | `course` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/cours/10_C1_cercle_trigonometrique.tex` |
| `1SPE-TRIGO-CR-011` | `course` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/cours/11_C2_cosinus_sinus.tex` |
| `CHAPITRES/1SPE-TRIGONOMETRIE/DOSSIER_CURATION` | `chapter_metadata` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/dossier_curation.json` |
| `1SPE-TRIGO-EX-001-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-001-CDP.tex` |
| `1SPE-TRIGO-EX-001` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-001.tex` |
| `1SPE-TRIGO-EX-002-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-002-CDP.tex` |
| `1SPE-TRIGO-EX-002` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-002.tex` |
| `1SPE-TRIGO-EX-003-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-003-CDP.tex` |
| `1SPE-TRIGO-EX-003` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-003.tex` |
| `1SPE-TRIGO-EX-004-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-004-CDP.tex` |
| `1SPE-TRIGO-EX-004` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-004.tex` |
| `1SPE-TRIGO-EX-005` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-005.tex` |
| `1SPE-TRIGO-EX-006` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-006.tex` |
| `1SPE-TRIGO-EX-007` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-007.tex` |
| `1SPE-TRIGO-EX-008` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-008.tex` |
| `1SPE-TRIGO-EX-009` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-009.tex` |
| `1SPE-TRIGO-EX-010` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-010.tex` |
| `1SPE-TRIGO-EX-011-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-011-CDP.tex` |
| `1SPE-TRIGO-EX-011` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-011.tex` |
| `1SPE-TRIGO-EX-012-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-012-CDP.tex` |
| `1SPE-TRIGO-EX-012` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-012.tex` |
| `1SPE-TRIGO-EX-013-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-013-CDP.tex` |
| `1SPE-TRIGO-EX-013` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-013.tex` |
| `1SPE-TRIGO-EX-014-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-014-CDP.tex` |
| `1SPE-TRIGO-EX-014` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-014.tex` |
| `1SPE-TRIGO-EX-015` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-015.tex` |
| `1SPE-TRIGO-EX-016` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-016.tex` |
| `1SPE-TRIGO-EX-017` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-017.tex` |
| `1SPE-TRIGO-EX-018` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-018.tex` |
| `1SPE-TRIGO-EX-019` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-019.tex` |
| `1SPE-TRIGO-EX-020` | `exercise` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-020.tex` |
| `1SPE-TRIGO-ME-001` | `method` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/methodes/1SPE-TRIGO-ME-001.tex` |
| `1SPE-TRIGO-ME-002` | `method` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/methodes/1SPE-TRIGO-ME-002.tex` |
| `CHAPITRES/1SPE-TRIGONOMETRIE/QCM/1SPE-TRIGONOMETRIE-QCM:JSON` | `qcm_json` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/qcm/1SPE-TRIGONOMETRIE-QCM.json` |
| `1SPE-TRIGO-QCM:TEX` | `qcm_tex` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/qcm/1SPE-TRIGONOMETRIE-QCM.tex` |
| `1SPE-TRIGO-FR-R1` | `remediation` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/remediation/1SPE-TRIGO-FR-R1.tex` |
| `1SPE-TRIGO-FR-R2` | `remediation` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/remediation/1SPE-TRIGO-FR-R2.tex` |
| `1SPE-TRIGO-RE-C1` | `remediation` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/remediation/1SPE-TRIGO-RE-C1.tex` |
| `1SPE-TRIGO-RE-C2` | `remediation` | `keep` | `chapitres/1SPE-TRIGONOMETRIE/remediation/1SPE-TRIGO-RE-C2.tex` |
| `07_td_contextualise:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/07_td_contextualise.sympy.json` |
| `07_td_fil_rouge:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/07_td_fil_rouge.sympy.json` |
| `10_C1_cercle_trigonometrique:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/10_C1_cercle_trigonometrique.sympy.json` |
| `11_C2_cosinus_sinus:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/11_C2_cosinus_sinus.sympy.json` |
| `12_C3_formules_addition:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/12_C3_formules_addition.sympy.json` |
| `13_C4_equations_trigonometriques:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/13_C4_equations_trigonometriques.sympy.json` |
| `14_C5_fonctions_cos_sin:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/14_C5_fonctions_cos_sin.sympy.json` |
| `1SPE-TRIGO-CO-001:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-001.sympy.json` |
| `1SPE-TRIGO-CO-002:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-002.sympy.json` |
| `1SPE-TRIGO-CO-003:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-003.sympy.json` |
| `1SPE-TRIGO-CO-004:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-004.sympy.json` |
| `1SPE-TRIGO-CO-005:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-005.sympy.json` |
| `1SPE-TRIGO-CO-006:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-006.sympy.json` |
| `1SPE-TRIGO-CO-007:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-007.sympy.json` |
| `1SPE-TRIGO-CO-008:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-008.sympy.json` |
| `1SPE-TRIGO-CO-009:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-009.sympy.json` |
| `1SPE-TRIGO-CO-010:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-010.sympy.json` |
| `1SPE-TRIGO-CO-011:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-011.sympy.json` |
| `1SPE-TRIGO-CO-012:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-012.sympy.json` |
| `1SPE-TRIGO-CO-013:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-013.sympy.json` |
| `1SPE-TRIGO-CO-014:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-014.sympy.json` |
| `1SPE-TRIGO-CO-015:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-015.sympy.json` |
| `1SPE-TRIGO-CO-016:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-016.sympy.json` |
| `1SPE-TRIGO-CO-017:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-017.sympy.json` |
| `1SPE-TRIGO-CO-018:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-018.sympy.json` |
| `1SPE-TRIGO-CO-019:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-019.sympy.json` |
| `1SPE-TRIGO-CO-020:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-020.sympy.json` |
| `1SPE-TRIGO-CO-021:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-021.sympy.json` |
| `1SPE-TRIGO-CO-022:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-022.sympy.json` |
| `1SPE-TRIGO-CO-023:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-023.sympy.json` |
| `1SPE-TRIGO-CO-024:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-024.sympy.json` |
| `1SPE-TRIGO-CO-025:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-025.sympy.json` |
| `1SPE-TRIGO-CO-026:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-026.sympy.json` |
| `1SPE-TRIGO-CO-027:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-027.sympy.json` |
| `1SPE-TRIGO-CO-028:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-028.sympy.json` |
| `1SPE-TRIGO-CO-029:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-029.sympy.json` |
| `1SPE-TRIGO-CO-030:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-030.sympy.json` |
| `1SPE-TRIGO-CO-031:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-031.sympy.json` |
| `1SPE-TRIGO-CO-032:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-032.sympy.json` |
| `1SPE-TRIGO-CO-033:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-033.sympy.json` |
| `1SPE-TRIGO-CO-034:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-034.sympy.json` |
| `1SPE-TRIGO-CO-035:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-035.sympy.json` |
| `1SPE-TRIGO-CO-036:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-036.sympy.json` |
| `1SPE-TRIGO-CO-037:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-037.sympy.json` |
| `1SPE-TRIGO-CO-038:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-038.sympy.json` |
| `1SPE-TRIGO-CO-039:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-039.sympy.json` |
| `1SPE-TRIGO-CO-040:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-040.sympy.json` |
| `1SPE-TRIGO-CO-041:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-041.sympy.json` |
| `1SPE-TRIGO-CO-042:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-042.sympy.json` |
| `1SPE-TRIGO-CO-043:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-043.sympy.json` |
| `1SPE-TRIGO-CO-044:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-044.sympy.json` |
| `1SPE-TRIGO-CO-045:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-045.sympy.json` |
| `1SPE-TRIGO-CO-046:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-046.sympy.json` |
| `1SPE-TRIGO-CO-047:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-047.sympy.json` |
| `1SPE-TRIGO-CO-048:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-048.sympy.json` |
| `1SPE-TRIGO-CO-049:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-049.sympy.json` |
| `1SPE-TRIGO-CO-050:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-CO-050.sympy.json` |
| `1SPE-TRIGO-EV-A-corrige:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EV-A-corrige.sympy.json` |
| `1SPE-TRIGO-EV-A:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EV-A.sympy.json` |
| `1SPE-TRIGO-EV-B-corrige:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EV-B-corrige.sympy.json` |
| `1SPE-TRIGO-EV-B:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EV-B.sympy.json` |
| `1SPE-TRIGO-EX-001-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-001-CDP.sympy.json` |
| `1SPE-TRIGO-EX-001:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-001.sympy.json` |
| `1SPE-TRIGO-EX-002-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-002-CDP.sympy.json` |
| `1SPE-TRIGO-EX-002:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-002.sympy.json` |
| `1SPE-TRIGO-EX-003-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-003-CDP.sympy.json` |
| `1SPE-TRIGO-EX-003:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-003.sympy.json` |
| `1SPE-TRIGO-EX-004-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-004-CDP.sympy.json` |
| `1SPE-TRIGO-EX-004:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-004.sympy.json` |
| `1SPE-TRIGO-EX-005:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-005.sympy.json` |
| `1SPE-TRIGO-EX-006:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-006.sympy.json` |
| `1SPE-TRIGO-EX-007:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-007.sympy.json` |
| `1SPE-TRIGO-EX-008:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-008.sympy.json` |
| `1SPE-TRIGO-EX-009:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-009.sympy.json` |
| `1SPE-TRIGO-EX-010:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-010.sympy.json` |
| `1SPE-TRIGO-EX-011-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-011-CDP.sympy.json` |
| `1SPE-TRIGO-EX-011:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-011.sympy.json` |
| `1SPE-TRIGO-EX-012-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-012-CDP.sympy.json` |
| `1SPE-TRIGO-EX-012:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-012.sympy.json` |
| `1SPE-TRIGO-EX-013-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-013-CDP.sympy.json` |
| `1SPE-TRIGO-EX-013:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-013.sympy.json` |
| `1SPE-TRIGO-EX-014-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-014-CDP.sympy.json` |
| `1SPE-TRIGO-EX-014:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-014.sympy.json` |
| `1SPE-TRIGO-EX-015:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-015.sympy.json` |
| `1SPE-TRIGO-EX-016:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-016.sympy.json` |
| `1SPE-TRIGO-EX-017:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-017.sympy.json` |
| `1SPE-TRIGO-EX-018:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-018.sympy.json` |
| `1SPE-TRIGO-EX-019:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-019.sympy.json` |
| `1SPE-TRIGO-EX-020:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-020.sympy.json` |
| `1SPE-TRIGO-EX-021-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-021-CDP.sympy.json` |
| `1SPE-TRIGO-EX-021:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-021.sympy.json` |
| `1SPE-TRIGO-EX-022-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-022-CDP.sympy.json` |
| `1SPE-TRIGO-EX-022:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-022.sympy.json` |
| `1SPE-TRIGO-EX-023-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-023-CDP.sympy.json` |
| `1SPE-TRIGO-EX-023:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-023.sympy.json` |
| `1SPE-TRIGO-EX-024-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-024-CDP.sympy.json` |
| `1SPE-TRIGO-EX-024:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-024.sympy.json` |
| `1SPE-TRIGO-EX-025:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-025.sympy.json` |
| `1SPE-TRIGO-EX-026:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-026.sympy.json` |
| `1SPE-TRIGO-EX-027:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-027.sympy.json` |
| `1SPE-TRIGO-EX-028:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-028.sympy.json` |
| `1SPE-TRIGO-EX-029:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-029.sympy.json` |
| `1SPE-TRIGO-EX-030:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-030.sympy.json` |
| `1SPE-TRIGO-EX-031-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-031-CDP.sympy.json` |
| `1SPE-TRIGO-EX-031:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-031.sympy.json` |
| `1SPE-TRIGO-EX-032-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-032-CDP.sympy.json` |
| `1SPE-TRIGO-EX-032:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-032.sympy.json` |
| `1SPE-TRIGO-EX-033-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-033-CDP.sympy.json` |
| `1SPE-TRIGO-EX-033:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-033.sympy.json` |
| `1SPE-TRIGO-EX-034-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-034-CDP.sympy.json` |
| `1SPE-TRIGO-EX-034:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-034.sympy.json` |
| `1SPE-TRIGO-EX-035:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-035.sympy.json` |
| `1SPE-TRIGO-EX-036:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-036.sympy.json` |
| `1SPE-TRIGO-EX-037:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-037.sympy.json` |
| `1SPE-TRIGO-EX-038:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-038.sympy.json` |
| `1SPE-TRIGO-EX-039:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-039.sympy.json` |
| `1SPE-TRIGO-EX-040:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-040.sympy.json` |
| `1SPE-TRIGO-EX-041-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-041-CDP.sympy.json` |
| `1SPE-TRIGO-EX-041:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-041.sympy.json` |
| `1SPE-TRIGO-EX-042-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-042-CDP.sympy.json` |
| `1SPE-TRIGO-EX-042:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-042.sympy.json` |
| `1SPE-TRIGO-EX-043:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-043.sympy.json` |
| `1SPE-TRIGO-EX-044:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-044.sympy.json` |
| `1SPE-TRIGO-EX-045:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-045.sympy.json` |
| `1SPE-TRIGO-EX-046:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-046.sympy.json` |
| `1SPE-TRIGO-EX-047:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-047.sympy.json` |
| `1SPE-TRIGO-EX-048:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-048.sympy.json` |
| `1SPE-TRIGO-EX-049:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-049.sympy.json` |
| `1SPE-TRIGO-EX-050:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-EX-050.sympy.json` |
| `1SPE-TRIGO-FR-R1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-FR-R1.sympy.json` |
| `1SPE-TRIGO-FR-R2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-FR-R2.sympy.json` |
| `1SPE-TRIGO-FR-R3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-FR-R3.sympy.json` |
| `1SPE-TRIGO-FR-R4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-FR-R4.sympy.json` |
| `1SPE-TRIGO-FR-R5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-FR-R5.sympy.json` |
| `1SPE-TRIGO-RE-C1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-RE-C1.sympy.json` |
| `1SPE-TRIGO-RE-C2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-RE-C2.sympy.json` |
| `1SPE-TRIGO-RE-C3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-RE-C3.sympy.json` |
| `1SPE-TRIGO-RE-C4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-RE-C4.sympy.json` |
| `1SPE-TRIGO-RE-C5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGO-RE-C5.sympy.json` |
| `1SPE-TRIGONOMETRIE-QCM:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-TRIGONOMETRIE/validations/1SPE-TRIGONOMETRIE-QCM.sympy.json` |
| `CHAPITRES/1SPE-VARIABLES-ALEATOIRES/LOT-0_RAPPORT` | `report` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/LOT-0_rapport.md` |
| `CHAPITRES/1SPE-VARIABLES-ALEATOIRES/LOT-1_RAPPORT` | `report` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/LOT-1_rapport.md` |
| `CHAPITRES/1SPE-VARIABLES-ALEATOIRES/LOT-2_RAPPORT` | `report` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/LOT-2_rapport.md` |
| `CHAPITRES/1SPE-VARIABLES-ALEATOIRES/LOT-3_RAPPORT` | `report` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/LOT-3_rapport.md` |
| `CHAPITRES/1SPE-VARIABLES-ALEATOIRES/LOT-4_RAPPORT` | `report` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/LOT-4_rapport.md` |
| `CHAPITRES/1SPE-VARIABLES-ALEATOIRES/LOT-5_RAPPORT` | `report` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/LOT-5_rapport.md` |
| `CHAPITRES/1SPE-VARIABLES-ALEATOIRES/LOT-6_RAPPORT` | `report` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/LOT-6_rapport.md` |
| `CHAPITRES/1SPE-VARIABLES-ALEATOIRES/LOT-7_RAPPORT` | `report` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/LOT-7_rapport.md` |
| `CHAPITRES/1SPE-VARIABLES-ALEATOIRES/CONTRAT` | `chapter_contract` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/contrat.yaml` |
| `1SPE-VARALEA-CO-001` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-001.tex` |
| `1SPE-VARALEA-CO-002` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-002.tex` |
| `1SPE-VARALEA-CO-003` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-003.tex` |
| `1SPE-VARALEA-CO-004` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-004.tex` |
| `1SPE-VARALEA-CO-005` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-005.tex` |
| `1SPE-VARALEA-CO-006` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-006.tex` |
| `1SPE-VARALEA-CO-007` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-007.tex` |
| `1SPE-VARALEA-CO-008` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-008.tex` |
| `1SPE-VARALEA-CO-009` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-009.tex` |
| `1SPE-VARALEA-CO-010` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-010.tex` |
| `1SPE-VARALEA-CO-011` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-011.tex` |
| `1SPE-VARALEA-CO-012` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-012.tex` |
| `1SPE-VARALEA-CO-013` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-013.tex` |
| `1SPE-VARALEA-CO-014` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-014.tex` |
| `1SPE-VARALEA-CO-015` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-015.tex` |
| `1SPE-VARALEA-CO-016` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-016.tex` |
| `1SPE-VARALEA-CO-017` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-017.tex` |
| `1SPE-VARALEA-CO-018` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-018.tex` |
| `1SPE-VARALEA-CO-019` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-019.tex` |
| `1SPE-VARALEA-CO-020` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-020.tex` |
| `1SPE-VARALEA-CO-021` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-021.tex` |
| `1SPE-VARALEA-CO-022` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-022.tex` |
| `1SPE-VARALEA-CO-023` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-023.tex` |
| `1SPE-VARALEA-CO-024` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-024.tex` |
| `1SPE-VARALEA-CO-025` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-025.tex` |
| `1SPE-VARALEA-CO-026` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-026.tex` |
| `1SPE-VARALEA-CO-027` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-027.tex` |
| `1SPE-VARALEA-CO-028` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-028.tex` |
| `1SPE-VARALEA-CO-029` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-029.tex` |
| `1SPE-VARALEA-CO-030` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-030.tex` |
| `1SPE-VARALEA-CO-031` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-031.tex` |
| `1SPE-VARALEA-CO-032` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-032.tex` |
| `1SPE-VARALEA-CO-033` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-033.tex` |
| `1SPE-VARALEA-CO-034` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-034.tex` |
| `1SPE-VARALEA-CO-035` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-035.tex` |
| `1SPE-VARALEA-CO-036` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-036.tex` |
| `1SPE-VARALEA-CO-037` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-037.tex` |
| `1SPE-VARALEA-CO-038` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-038.tex` |
| `1SPE-VARALEA-CO-039` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-039.tex` |
| `1SPE-VARALEA-CO-040` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-040.tex` |
| `1SPE-VARALEA-CO-041` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-041.tex` |
| `1SPE-VARALEA-CO-042` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-042.tex` |
| `1SPE-VARALEA-CO-043` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-043.tex` |
| `1SPE-VARALEA-CO-044` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-044.tex` |
| `1SPE-VARALEA-CO-045` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-045.tex` |
| `1SPE-VARALEA-CO-046` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-046.tex` |
| `1SPE-VARALEA-CO-047` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-047.tex` |
| `1SPE-VARALEA-CO-048` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-048.tex` |
| `1SPE-VARALEA-CO-049` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-049.tex` |
| `1SPE-VARALEA-CO-050` | `solution` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-050.tex` |
| `1SPE-VARALEA-CR-000` | `course` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/cours/00_ouverture.tex` |
| `1SPE-VARALEA-CR-001` | `course` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/cours/01_diagnostic.tex` |
| `1SPE-VARALEA-TD-CONTEXTUALISE` | `transversal` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/cours/07_td_contextualise.tex` |
| `1SPE-VARALEA-TD-FIL-ROUGE` | `transversal` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/cours/07_td_fil_rouge.tex` |
| `1SPE-VARALEA-CR-010` | `course` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/cours/10_C1_loi_probabilite.tex` |
| `1SPE-VARALEA-CR-011` | `course` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/cours/11_C2_esperance_variance.tex` |
| `1SPE-VARALEA-CR-012` | `course` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/cours/12_C3_bernoulli_binomiale.tex` |
| `1SPE-VARALEA-CR-013` | `course` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/cours/13_C4_esperance_binomiale.tex` |
| `1SPE-VARALEA-CR-014` | `course` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/cours/14_C5_problemes_contextualises.tex` |
| `CHAPITRES/1SPE-VARIABLES-ALEATOIRES/DOSSIER_CURATION` | `chapter_metadata` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/dossier_curation.json` |
| `1SPE-VARALEA-EV-A-corrige:SCALE` | `grading_scale` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/evaluations/1SPE-VARALEA-EV-A-corrige.tex` |
| `1SPE-VARALEA-EV-A` | `assessment` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/evaluations/1SPE-VARALEA-EV-A.tex` |
| `1SPE-VARALEA-EV-B-corrige:SCALE` | `grading_scale` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/evaluations/1SPE-VARALEA-EV-B-corrige.tex` |
| `1SPE-VARALEA-EV-B` | `assessment` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/evaluations/1SPE-VARALEA-EV-B.tex` |
| `1SPE-VARALEA-EX-001-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-001-CDP.tex` |
| `1SPE-VARALEA-EX-001` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-001.tex` |
| `1SPE-VARALEA-EX-002-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-002-CDP.tex` |
| `1SPE-VARALEA-EX-002` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-002.tex` |
| `1SPE-VARALEA-EX-003` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-003.tex` |
| `1SPE-VARALEA-EX-004` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-004.tex` |
| `1SPE-VARALEA-EX-005-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-005-CDP.tex` |
| `1SPE-VARALEA-EX-005` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-005.tex` |
| `1SPE-VARALEA-EX-006` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-006.tex` |
| `1SPE-VARALEA-EX-007-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-007-CDP.tex` |
| `1SPE-VARALEA-EX-007` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-007.tex` |
| `1SPE-VARALEA-EX-008` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-008.tex` |
| `1SPE-VARALEA-EX-009` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-009.tex` |
| `1SPE-VARALEA-EX-010` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-010.tex` |
| `1SPE-VARALEA-EX-011-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-011-CDP.tex` |
| `1SPE-VARALEA-EX-011` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-011.tex` |
| `1SPE-VARALEA-EX-012` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-012.tex` |
| `1SPE-VARALEA-EX-013-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-013-CDP.tex` |
| `1SPE-VARALEA-EX-013` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-013.tex` |
| `1SPE-VARALEA-EX-014-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-014-CDP.tex` |
| `1SPE-VARALEA-EX-014` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-014.tex` |
| `1SPE-VARALEA-EX-015` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-015.tex` |
| `1SPE-VARALEA-EX-016` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-016.tex` |
| `1SPE-VARALEA-EX-017-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-017-CDP.tex` |
| `1SPE-VARALEA-EX-017` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-017.tex` |
| `1SPE-VARALEA-EX-018` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-018.tex` |
| `1SPE-VARALEA-EX-019` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-019.tex` |
| `1SPE-VARALEA-EX-020` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-020.tex` |
| `1SPE-VARALEA-EX-021` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-021.tex` |
| `1SPE-VARALEA-EX-022-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-022-CDP.tex` |
| `1SPE-VARALEA-EX-022` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-022.tex` |
| `1SPE-VARALEA-EX-023` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-023.tex` |
| `1SPE-VARALEA-EX-024-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-024-CDP.tex` |
| `1SPE-VARALEA-EX-024` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-024.tex` |
| `1SPE-VARALEA-EX-025` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-025.tex` |
| `1SPE-VARALEA-EX-026-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-026-CDP.tex` |
| `1SPE-VARALEA-EX-026` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-026.tex` |
| `1SPE-VARALEA-EX-027` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-027.tex` |
| `1SPE-VARALEA-EX-028` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-028.tex` |
| `1SPE-VARALEA-EX-029` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-029.tex` |
| `1SPE-VARALEA-EX-030` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-030.tex` |
| `1SPE-VARALEA-EX-031-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-031-CDP.tex` |
| `1SPE-VARALEA-EX-031` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-031.tex` |
| `1SPE-VARALEA-EX-032` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-032.tex` |
| `1SPE-VARALEA-EX-033-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-033-CDP.tex` |
| `1SPE-VARALEA-EX-033` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-033.tex` |
| `1SPE-VARALEA-EX-034` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-034.tex` |
| `1SPE-VARALEA-EX-035` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-035.tex` |
| `1SPE-VARALEA-EX-036` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-036.tex` |
| `1SPE-VARALEA-EX-037` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-037.tex` |
| `1SPE-VARALEA-EX-038` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-038.tex` |
| `1SPE-VARALEA-EX-039` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-039.tex` |
| `1SPE-VARALEA-EX-040` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-040.tex` |
| `1SPE-VARALEA-EX-041-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-041-CDP.tex` |
| `1SPE-VARALEA-EX-041` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-041.tex` |
| `1SPE-VARALEA-EX-042` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-042.tex` |
| `1SPE-VARALEA-EX-043-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-043-CDP.tex` |
| `1SPE-VARALEA-EX-043` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-043.tex` |
| `1SPE-VARALEA-EX-044` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-044.tex` |
| `1SPE-VARALEA-EX-045-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-045-CDP.tex` |
| `1SPE-VARALEA-EX-045` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-045.tex` |
| `1SPE-VARALEA-EX-046` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-046.tex` |
| `1SPE-VARALEA-EX-047-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-047-CDP.tex` |
| `1SPE-VARALEA-EX-047` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-047.tex` |
| `1SPE-VARALEA-EX-048` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-048.tex` |
| `1SPE-VARALEA-EX-049` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-049.tex` |
| `1SPE-VARALEA-EX-050-CDP:AID` | `aid` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-050-CDP.tex` |
| `1SPE-VARALEA-EX-050` | `exercise` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-050.tex` |
| `1SPE-VARALEA-ME-001` | `method` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/methodes/1SPE-VARALEA-ME-001.tex` |
| `1SPE-VARALEA-ME-002` | `method` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/methodes/1SPE-VARALEA-ME-002.tex` |
| `1SPE-VARALEA-ME-003` | `method` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/methodes/1SPE-VARALEA-ME-003.tex` |
| `1SPE-VARALEA-ME-004` | `method` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/methodes/1SPE-VARALEA-ME-004.tex` |
| `1SPE-VARALEA-ME-005` | `method` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/methodes/1SPE-VARALEA-ME-005.tex` |
| `CHAPITRES/1SPE-VARIABLES-ALEATOIRES/QCM/1SPE-VARALEA-QCM:JSON` | `qcm_json` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/qcm/1SPE-VARALEA-QCM.json` |
| `1SPE-VARALEA-QCM:TEX` | `qcm_tex` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/qcm/1SPE-VARALEA-QCM.tex` |
| `1SPE-VARALEA-FR-R1` | `remediation` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/remediation/1SPE-VARALEA-FR-R1.tex` |
| `1SPE-VARALEA-FR-R2` | `remediation` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/remediation/1SPE-VARALEA-FR-R2.tex` |
| `1SPE-VARALEA-FR-R3` | `remediation` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/remediation/1SPE-VARALEA-FR-R3.tex` |
| `1SPE-VARALEA-FR-R4` | `remediation` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/remediation/1SPE-VARALEA-FR-R4.tex` |
| `1SPE-VARALEA-FR-R5` | `remediation` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/remediation/1SPE-VARALEA-FR-R5.tex` |
| `1SPE-VARALEA-RE-C1` | `remediation` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/remediation/1SPE-VARALEA-RE-C1.tex` |
| `1SPE-VARALEA-RE-C2` | `remediation` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/remediation/1SPE-VARALEA-RE-C2.tex` |
| `1SPE-VARALEA-RE-C3` | `remediation` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/remediation/1SPE-VARALEA-RE-C3.tex` |
| `1SPE-VARALEA-RE-C4` | `remediation` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/remediation/1SPE-VARALEA-RE-C4.tex` |
| `1SPE-VARALEA-RE-C5` | `remediation` | `keep` | `chapitres/1SPE-VARIABLES-ALEATOIRES/remediation/1SPE-VARALEA-RE-C5.tex` |
| `00_ouverture:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/00_ouverture.sympy.json` |
| `01_diagnostic:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/01_diagnostic.sympy.json` |
| `07_td_contextualise:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/07_td_contextualise.sympy.json` |
| `07_td_fil_rouge:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/07_td_fil_rouge.sympy.json` |
| `10_C1_loi_probabilite:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/10_C1_loi_probabilite.sympy.json` |
| `11_C2_esperance_variance:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/11_C2_esperance_variance.sympy.json` |
| `12_C3_bernoulli_binomiale:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/12_C3_bernoulli_binomiale.sympy.json` |
| `13_C4_esperance_binomiale:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/13_C4_esperance_binomiale.sympy.json` |
| `14_C5_problemes_contextualises:PROOF` | `validation` | `review_required` (duplicate_canonical_id, stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/14_C5_problemes_contextualises.sympy.json` |
| `1SPE-VARALEA-CO-001:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-001.sympy.json` |
| `1SPE-VARALEA-CO-002:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-002.sympy.json` |
| `1SPE-VARALEA-CO-003:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-003.sympy.json` |
| `1SPE-VARALEA-CO-004:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-004.sympy.json` |
| `1SPE-VARALEA-CO-005:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-005.sympy.json` |
| `1SPE-VARALEA-CO-006:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-006.sympy.json` |
| `1SPE-VARALEA-CO-007:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-007.sympy.json` |
| `1SPE-VARALEA-CO-008:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-008.sympy.json` |
| `1SPE-VARALEA-CO-009:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-009.sympy.json` |
| `1SPE-VARALEA-CO-010:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-010.sympy.json` |
| `1SPE-VARALEA-CO-011:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-011.sympy.json` |
| `1SPE-VARALEA-CO-012:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-012.sympy.json` |
| `1SPE-VARALEA-CO-013:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-013.sympy.json` |
| `1SPE-VARALEA-CO-014:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-014.sympy.json` |
| `1SPE-VARALEA-CO-015:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-015.sympy.json` |
| `1SPE-VARALEA-CO-016:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-016.sympy.json` |
| `1SPE-VARALEA-CO-017:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-017.sympy.json` |
| `1SPE-VARALEA-CO-018:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-018.sympy.json` |
| `1SPE-VARALEA-CO-019:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-019.sympy.json` |
| `1SPE-VARALEA-CO-020:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-020.sympy.json` |
| `1SPE-VARALEA-CO-021:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-021.sympy.json` |
| `1SPE-VARALEA-CO-022:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-022.sympy.json` |
| `1SPE-VARALEA-CO-023:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-023.sympy.json` |
| `1SPE-VARALEA-CO-024:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-024.sympy.json` |
| `1SPE-VARALEA-CO-025:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-025.sympy.json` |
| `1SPE-VARALEA-CO-026:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-026.sympy.json` |
| `1SPE-VARALEA-CO-027:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-027.sympy.json` |
| `1SPE-VARALEA-CO-028:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-028.sympy.json` |
| `1SPE-VARALEA-CO-029:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-029.sympy.json` |
| `1SPE-VARALEA-CO-030:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-030.sympy.json` |
| `1SPE-VARALEA-CO-031:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-031.sympy.json` |
| `1SPE-VARALEA-CO-032:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-032.sympy.json` |
| `1SPE-VARALEA-CO-033:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-033.sympy.json` |
| `1SPE-VARALEA-CO-034:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-034.sympy.json` |
| `1SPE-VARALEA-CO-035:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-035.sympy.json` |
| `1SPE-VARALEA-CO-036:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-036.sympy.json` |
| `1SPE-VARALEA-CO-037:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-037.sympy.json` |
| `1SPE-VARALEA-CO-038:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-038.sympy.json` |
| `1SPE-VARALEA-CO-039:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-039.sympy.json` |
| `1SPE-VARALEA-CO-040:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-040.sympy.json` |
| `1SPE-VARALEA-CO-041:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-041.sympy.json` |
| `1SPE-VARALEA-CO-042:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-042.sympy.json` |
| `1SPE-VARALEA-CO-043:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-043.sympy.json` |
| `1SPE-VARALEA-CO-044:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-044.sympy.json` |
| `1SPE-VARALEA-CO-045:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-045.sympy.json` |
| `1SPE-VARALEA-CO-046:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-046.sympy.json` |
| `1SPE-VARALEA-CO-047:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-047.sympy.json` |
| `1SPE-VARALEA-CO-048:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-048.sympy.json` |
| `1SPE-VARALEA-CO-049:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-049.sympy.json` |
| `1SPE-VARALEA-CO-050:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-CO-050.sympy.json` |
| `1SPE-VARALEA-EV-A-corrige:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EV-A-corrige.sympy.json` |
| `1SPE-VARALEA-EV-A:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EV-A.sympy.json` |
| `1SPE-VARALEA-EV-B-corrige:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EV-B-corrige.sympy.json` |
| `1SPE-VARALEA-EV-B:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EV-B.sympy.json` |
| `1SPE-VARALEA-EX-001-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-001-CDP.sympy.json` |
| `1SPE-VARALEA-EX-001:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-001.sympy.json` |
| `1SPE-VARALEA-EX-002-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-002-CDP.sympy.json` |
| `1SPE-VARALEA-EX-002:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-002.sympy.json` |
| `1SPE-VARALEA-EX-003:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-003.sympy.json` |
| `1SPE-VARALEA-EX-004:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-004.sympy.json` |
| `1SPE-VARALEA-EX-005-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-005-CDP.sympy.json` |
| `1SPE-VARALEA-EX-005:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-005.sympy.json` |
| `1SPE-VARALEA-EX-006:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-006.sympy.json` |
| `1SPE-VARALEA-EX-007-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-007-CDP.sympy.json` |
| `1SPE-VARALEA-EX-007:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-007.sympy.json` |
| `1SPE-VARALEA-EX-008:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-008.sympy.json` |
| `1SPE-VARALEA-EX-009:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-009.sympy.json` |
| `1SPE-VARALEA-EX-010:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-010.sympy.json` |
| `1SPE-VARALEA-EX-011-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-011-CDP.sympy.json` |
| `1SPE-VARALEA-EX-011:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-011.sympy.json` |
| `1SPE-VARALEA-EX-012:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-012.sympy.json` |
| `1SPE-VARALEA-EX-013-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-013-CDP.sympy.json` |
| `1SPE-VARALEA-EX-013:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-013.sympy.json` |
| `1SPE-VARALEA-EX-014-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-014-CDP.sympy.json` |
| `1SPE-VARALEA-EX-014:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-014.sympy.json` |
| `1SPE-VARALEA-EX-015:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-015.sympy.json` |
| `1SPE-VARALEA-EX-016:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-016.sympy.json` |
| `1SPE-VARALEA-EX-017-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-017-CDP.sympy.json` |
| `1SPE-VARALEA-EX-017:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-017.sympy.json` |
| `1SPE-VARALEA-EX-018:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-018.sympy.json` |
| `1SPE-VARALEA-EX-019:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-019.sympy.json` |
| `1SPE-VARALEA-EX-020:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-020.sympy.json` |
| `1SPE-VARALEA-EX-021:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-021.sympy.json` |
| `1SPE-VARALEA-EX-022-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-022-CDP.sympy.json` |
| `1SPE-VARALEA-EX-022:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-022.sympy.json` |
| `1SPE-VARALEA-EX-023:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-023.sympy.json` |
| `1SPE-VARALEA-EX-024-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-024-CDP.sympy.json` |
| `1SPE-VARALEA-EX-024:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-024.sympy.json` |
| `1SPE-VARALEA-EX-025:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-025.sympy.json` |
| `1SPE-VARALEA-EX-026-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-026-CDP.sympy.json` |
| `1SPE-VARALEA-EX-026:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-026.sympy.json` |
| `1SPE-VARALEA-EX-027:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-027.sympy.json` |
| `1SPE-VARALEA-EX-028:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-028.sympy.json` |
| `1SPE-VARALEA-EX-029:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-029.sympy.json` |
| `1SPE-VARALEA-EX-030:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-030.sympy.json` |
| `1SPE-VARALEA-EX-031-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-031-CDP.sympy.json` |
| `1SPE-VARALEA-EX-031:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-031.sympy.json` |
| `1SPE-VARALEA-EX-032:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-032.sympy.json` |
| `1SPE-VARALEA-EX-033-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-033-CDP.sympy.json` |
| `1SPE-VARALEA-EX-033:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-033.sympy.json` |
| `1SPE-VARALEA-EX-034:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-034.sympy.json` |
| `1SPE-VARALEA-EX-035:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-035.sympy.json` |
| `1SPE-VARALEA-EX-036:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-036.sympy.json` |
| `1SPE-VARALEA-EX-037:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-037.sympy.json` |
| `1SPE-VARALEA-EX-038:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-038.sympy.json` |
| `1SPE-VARALEA-EX-039:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-039.sympy.json` |
| `1SPE-VARALEA-EX-040:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-040.sympy.json` |
| `1SPE-VARALEA-EX-041-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-041-CDP.sympy.json` |
| `1SPE-VARALEA-EX-041:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-041.sympy.json` |
| `1SPE-VARALEA-EX-042:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-042.sympy.json` |
| `1SPE-VARALEA-EX-043-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-043-CDP.sympy.json` |
| `1SPE-VARALEA-EX-043:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-043.sympy.json` |
| `1SPE-VARALEA-EX-044:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-044.sympy.json` |
| `1SPE-VARALEA-EX-045-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-045-CDP.sympy.json` |
| `1SPE-VARALEA-EX-045:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-045.sympy.json` |
| `1SPE-VARALEA-EX-046:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-046.sympy.json` |
| `1SPE-VARALEA-EX-047-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-047-CDP.sympy.json` |
| `1SPE-VARALEA-EX-047:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-047.sympy.json` |
| `1SPE-VARALEA-EX-048:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-048.sympy.json` |
| `1SPE-VARALEA-EX-049:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-049.sympy.json` |
| `1SPE-VARALEA-EX-050-CDP:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-050-CDP.sympy.json` |
| `1SPE-VARALEA-EX-050:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-EX-050.sympy.json` |
| `1SPE-VARALEA-FR-R1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-FR-R1.sympy.json` |
| `1SPE-VARALEA-FR-R2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-FR-R2.sympy.json` |
| `1SPE-VARALEA-FR-R3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-FR-R3.sympy.json` |
| `1SPE-VARALEA-FR-R4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-FR-R4.sympy.json` |
| `1SPE-VARALEA-FR-R5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-FR-R5.sympy.json` |
| `1SPE-VARALEA-QCM:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-QCM.sympy.json` |
| `1SPE-VARALEA-RE-C1:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-RE-C1.sympy.json` |
| `1SPE-VARALEA-RE-C2:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-RE-C2.sympy.json` |
| `1SPE-VARALEA-RE-C3:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-RE-C3.sympy.json` |
| `1SPE-VARALEA-RE-C4:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-RE-C4.sympy.json` |
| `1SPE-VARALEA-RE-C5:PROOF` | `validation` | `review_required` (stale_proof) | `chapitres/1SPE-VARIABLES-ALEATOIRES/validations/1SPE-VARALEA-RE-C5.sympy.json` |
| `GABARITS/FONTS/JETBRAINSMONO-BOLD` | `font` | `keep` | `gabarits/fonts/JetBrainsMono-Bold.otf` |
| `GABARITS/FONTS/JETBRAINSMONO-BOLDITALIC` | `font` | `keep` | `gabarits/fonts/JetBrainsMono-BoldItalic.otf` |
| `GABARITS/FONTS/JETBRAINSMONO-ITALIC` | `font` | `keep` | `gabarits/fonts/JetBrainsMono-Italic.otf` |
| `GABARITS/FONTS/JETBRAINSMONO-REGULAR` | `font` | `keep` | `gabarits/fonts/JetBrainsMono-Regular.otf` |
| `GABARITS/FONTS/LICENSE-JETBRAINSMONO` | `font` | `keep` | `gabarits/fonts/LICENSE-JetBrainsMono.txt` |
| `GABARITS/FONTS/LICENSE-LIBERTINUS` | `font` | `keep` | `gabarits/fonts/LICENSE-Libertinus.txt` |
| `GABARITS/FONTS/LICENSE-MONTSERRAT` | `font` | `keep` | `gabarits/fonts/LICENSE-Montserrat.txt` |
| `GABARITS/FONTS/LIBERTINUSMATH-REGULAR` | `font` | `keep` | `gabarits/fonts/LibertinusMath-Regular.otf` |
| `GABARITS/FONTS/LIBERTINUSSERIF-BOLD` | `font` | `keep` | `gabarits/fonts/LibertinusSerif-Bold.otf` |
| `GABARITS/FONTS/LIBERTINUSSERIF-BOLDITALIC` | `font` | `keep` | `gabarits/fonts/LibertinusSerif-BoldItalic.otf` |
| `GABARITS/FONTS/LIBERTINUSSERIF-ITALIC` | `font` | `keep` | `gabarits/fonts/LibertinusSerif-Italic.otf` |
| `GABARITS/FONTS/LIBERTINUSSERIF-REGULAR` | `font` | `keep` | `gabarits/fonts/LibertinusSerif-Regular.otf` |
| `GABARITS/FONTS/MONTSERRAT-BOLD` | `font` | `keep` | `gabarits/fonts/Montserrat-Bold.otf` |
| `GABARITS/FONTS/MONTSERRAT-ITALIC` | `font` | `keep` | `gabarits/fonts/Montserrat-Italic.otf` |
| `GABARITS/FONTS/MONTSERRAT-MEDIUM` | `font` | `keep` | `gabarits/fonts/Montserrat-Medium.otf` |
| `GABARITS/FONTS/MONTSERRAT-MEDIUMITALIC` | `font` | `keep` | `gabarits/fonts/Montserrat-MediumItalic.otf` |
| `GABARITS/FONTS/MONTSERRAT-REGULAR` | `font` | `keep` | `gabarits/fonts/Montserrat-Regular.otf` |
| `GABARITS/FONTS/MONTSERRAT-SEMIBOLD` | `font` | `keep` | `gabarits/fonts/Montserrat-SemiBold.otf` |
| `GABARITS/FONTS/MONTSERRAT-SEMIBOLDITALIC` | `font` | `keep` | `gabarits/fonts/Montserrat-SemiBoldItalic.otf` |
| `GABARITS/FONTS/MONTSERRAT-THIN` | `font` | `keep` | `gabarits/fonts/Montserrat-Thin.otf` |
| `TRANSVERSAL/AVANT_PROPOS` | `transversal` | `keep` | `transversal/avant_propos.tex` |
| `TRANSVERSAL/FORMULAIRE` | `transversal` | `keep` | `transversal/formulaire.tex` |
| `TRANSVERSAL/INDEX_CAPACITES` | `transversal` | `keep` | `transversal/index_capacites.tex` |
| `TRANSVERSAL/MEMO_PYTHON` | `transversal` | `keep` | `transversal/memo_python.tex` |
| `TRANSVERSAL/MODE_EMPLOI` | `transversal` | `keep` | `transversal/mode_emploi.tex` |
| `TRANSVERSAL/PAGE_DE_GARDE` | `transversal` | `keep` | `transversal/page_de_garde.tex` |
| `VALIDATIONS/RELEASE-1SPE/BASELINE-BUILD-ELEVE:PROOF` | `validation` | `review_required` (compilation_failure) | `validations/release-1spe/baseline-build-eleve.json` |
| `VALIDATIONS/RELEASE-1SPE/BASELINE-BUILD-PROFESSEUR:PROOF` | `validation` | `review_required` (compilation_failure) | `validations/release-1spe/baseline-build-professeur.json` |
| `VALIDATIONS/RELEASE-1SPE/PROGRAMME-1SPE-2026.ATTESTATION:PROOF` | `validation` | `keep` | `validations/release-1spe/programme-1spe-2026.attestation.json` |
| `VALIDATIONS/RELEASE-1SPE/REVUE-PROGRAMME:PROOF` | `validation` | `keep` | `validations/release-1spe/revue-programme.md` |
| `VALIDATIONS/RELEASE-1SPE/TOOLCHAIN:PROOF` | `validation` | `keep` | `validations/release-1spe/toolchain.json` |
