# MISSION LOG — Production du manuel Premiere EDS Mathematiques

| Date | Chapitre | LOT | Verdicts | Mode | Commit |
|------|----------|-----|----------|------|--------|
| 2026-07-15 | - | PHASE 0 | Bootstrap OK | MODE FICHIERS (pas de PostgreSQL), pdflatex OK, reseau non utilise (generation ex nihilo) | [INIT] |
| 2026-07-15 | 1SPE-SUITES | LOT 0-3 | Contrat OK, curation ex nihilo, cours 9 sections + 7 methodes, compilation 16/16 | ex nihilo | [LOT-3] |
| 2026-07-15 | 1SPE-SUITES | LOT 4 | 49 exercices + 49 corriges, SymPy 98/98 OK, couverture >= 2/case | ex nihilo | [LOT-4] |
| 2026-07-15 | 1SPE-SUITES | LOT 5 | QCM 21 questions + 12 fiches remediation, couverture F01 complete | ex nihilo | [LOT-5] |
| 2026-07-15 | 1SPE-SUITES | LOT 6 | Eval A+B + 2 TD, SymPy 102/102 OK | ex nihilo | [LOT-6] |
| 2026-07-15 | 1SPE-SUITES | LOT 7 | PDF 82 pages OK, check-list 7/8, cout ~19.5$ | ex nihilo | [LOT-7] |
| 2026-07-15 | 1SPE-SECOND-DEGRE | LOT 0-7 | 42 ex + 42 co + QCM 18q + 11 remed + eval A/B + 2 TD. SymPy 88/88 OK. PDF 64p. | ex nihilo | [LOT-7] |
| 2026-07-15 | 1SPE-SUITES | LOT 0 reprise | Schéma contrat, SymPy 102/102, similarité mode fichiers, couverture et PDF : OK ; R4 corrigée. | MODE FICHIERS (port PostgreSQL 5432 occupé) | [1SPE-SUITES][LOT-0] |
| 2026-07-15 | 1SPE-DERIVATION-LOCAL | LOT 0 | Référentiel BO 2026, contrat 5 capacités, schéma et revue adversariale : PASS. | MODE FICHIERS | [1SPE-DERIVATION-LOCAL][LOT-0] |
| 2026-07-15 | 1SPE-DERIVATION-LOCAL | LOT 1 | Crawl Éduscol 0 document, ingestion 0 chunk ; angle mort déclaré, génération ex nihilo. | MODE FICHIERS | [1SPE-DERIVATION-LOCAL][LOT-1] |
| 2026-07-15 | 1SPE-DERIVATION-LOCAL | LOT 2 | Curation synthétique C1–C5, revue adversariale : PASS. | MODE FICHIERS / ex nihilo | [1SPE-DERIVATION-LOCAL][LOT-2] |
| 2026-07-15 | 1SPE-DERIVATION-LOCAL | LOT 3 | Cours C1–C5, méthodes M1–M5, compilation, similarité et revues adversariales : PASS. | MODE FICHIERS / ex nihilo | [1SPE-DERIVATION-LOCAL][LOT-3] |
| 2026-07-15 | Charte transverse | LOT 3bis | Charte, ouverture automatique, contrôle visuel Suites et régression compilation de 3 chapitres : PASS. Coût 0 $. | MODE FICHIERS | [CHARTE][LOT-3bis] |
| 2026-07-16 | Collection | META | Tags de complétion restaurés après l'import subtree : `chap/1SPE-SUITES-v1` et `chap/1SPE-SECOND-DEGRE-v1`, attestés par leurs rapports LOT 7. | MODE FICHIERS | [META] |
| 2026-07-16 | Charte transverse | INTÉGRITÉ | Ré-attestation : `make chapter` Suites (77 p.) et Second degré (61 p.), pilote NSI (34 p.), spécimen LuaLaTeX (5 p.). V3.2 restaurée depuis `4ee186b` : encadrés, ouverture, figures, signature Types construits et documentation ; correctifs volontaires conservés : LuaLaTeX, amssymb/amsthm et chemins `gabarits/`. | MODE FICHIERS | [INTEGRITE] |
