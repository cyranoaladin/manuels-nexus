# Maquette v5 — Itération 2 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produire et valider la maquette v5 itération 2 de 15 pages, sans réécriture des objets ni impact sur v4.1/TSPE.

**Architecture:** Une classe v5 isolée adapte les macros v4.1 au rendu demandé. Un manifeste versionné fixe l'échantillon ; un assembleur Python lit ses META et génère une table LaTeX ; un contrôleur indépendant compile et inspecte le PDF.

**Tech Stack:** Python 3, pytest, LuaLaTeX/KOMA-Script, TikZ, poppler (`pdfinfo`, `pdftotext`, `pdftoppm`).

---

## Chunk 1: Contrats automatiques et génération META

### Task 1: Parser et valider les META

**Files:**
- Create: `tests/test_maquette_v5.py`
- Create: `scripts/build_maquette_v5.py`
- Create: `build/maquette-v5/manifest.json` (versionné avec `git add -f`)

- [ ] **Step 1: Écrire `test_parse_meta_requires_valid_json_in_first_ten_lines` et `test_parse_meta_requires_typed_fields_and_matching_paths`.** Les fixtures temporaires couvrent `id`, `type_objet`, `methodes`, `parcours`, `duree_min`, `fichier_tex`, `corrige_tex`, ligne META tardive, JSON invalide et fichier/corrigé absent.
- [ ] **Step 2: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_parse_meta_requires_valid_json_in_first_ten_lines tests/test_maquette_v5.py::test_parse_meta_requires_typed_fields_and_matching_paths -q`.** Attendu : FAIL avec `ModuleNotFoundError: No module named 'build_maquette_v5'`.
- [ ] **Step 3: Implémenter `MetaError`, `parse_meta(path, root)` et les validations locales.** Une erreur de contrat doit devenir le code CLI 2.
- [ ] **Step 4: Réexécuter la commande de l'étape 2.** Attendu : `2 passed`.
- [ ] **Step 5: Écrire `test_build_reference_table_rejects_duplicate_and_unknown_ids`.** Le doublon entre fichiers et toute référence manifeste inconnue doivent lever `MetaError`.
- [ ] **Step 6: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_build_reference_table_rejects_duplicate_and_unknown_ids -q`.** Attendu : FAIL parce que `build_reference_table` n'existe pas.
- [ ] **Step 7: Implémenter l'agrégation ordonnée et les erreurs inter-fichiers dans `build_reference_table(manifest, root)`.**
- [ ] **Step 8: Réexécuter l'étape 6.** Attendu : `1 passed`.

### Task 2: Générer la table LaTeX déterministe

**Files:**
- Modify: `tests/test_maquette_v5.py`
- Modify: `scripts/build_maquette_v5.py`
- Create: `build/maquette-v5/manifest.json`
- Generate only: `build/maquette-v5/renvois.tex` (ignoré, non versionné)

- [ ] **Step 1: Écrire `test_render_reference_table_preserves_order_and_exact_contract`.** L'oracle exige l'ordre visible manifeste (EX-001/002/007/008/009/010/005/003/004/006/011…020), la numérotation 1…20, `ex:<ID>`, `meth:<ID>`, `corr:start`, le mapping difficulté `1 → un losange plein + deux contours`, `2 → deux pleins + un contour`, `3 → trois pleins`, les pictos manifestes EX-005 calculatrice/EX-006 Python/EX-015 calculatrice, et les deux chaînes exactes de renvoi.
- [ ] **Step 2: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_render_reference_table_preserves_order_and_exact_contract -q`.** Attendu : FAIL faute de rendu.
- [ ] **Step 3: Implémenter `render_reference_table(records, manifest)` et la CLI `--manifest/--output`.** Le fichier généré ne contient aucun corps d'objet ; il ne contient les IDs que dans les noms de déclarations/labels internes.
- [ ] **Step 4: Réexécuter l'étape 2.** Attendu : `1 passed`.
- [ ] **Step 5: Écrire le manifeste canonique.** Il fixe pages 1–15, blancs `[6,14]`, deux cours, méthodes META M1–M4, M1 rendu + applications 001/002/005, ordre visible des vingt exercices, QCM avec SHA-256, corrigés affichés 001–005, `corr:start`, neuf folios exacts et pictogrammes.
- [ ] **Step 6: Exécuter `python3 scripts/build_maquette_v5.py --manifest build/maquette-v5/manifest.json --output build/maquette-v5/renvois.tex`.** Attendu : `RENVOIS V5: 20 exercices, 1 méthode, 3 pictogrammes` et code 0.

### Task 3: Construire le contrôleur PDF testable

**Files:**
- Modify: `tests/test_maquette_v5.py`
- Create: `scripts/check_maquette_v5.py`

- [ ] **Step 1: Écrire `test_pdf_text_helpers_and_margin_log_contract`.** Exiger : espaces seuls = page vide ; deux chaînes exactes présentes ; `NEXUS-V5-MARGINNOTE-REDIRECTED` autorisé ; `NEXUS-V5-MARGINNOTE-COLUMNS-EMITTED` fatal.
- [ ] **Step 2: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_pdf_text_helpers_and_margin_log_contract -q`.** Attendu : FAIL faute de module.
- [ ] **Step 3: Implémenter `normalize_text`, `page_text_is_empty`, `required_strings_present` et `assert_no_two_column_marginnotes`.**
- [ ] **Step 4: Réexécuter l'étape 2.** Attendu : `1 passed`.
- [ ] **Step 5: Écrire `test_compile_maquette_runs_generator_three_lualatex_passes_and_pdfinfo`.** Employer de faux exécutables temporaires via `PATH` pour enregistrer les appels réels de sous-processus, sans mock Python ; exiger cwd racine, générateur une fois, LuaLaTeX trois fois et `pdfinfo` une fois.
- [ ] **Step 6: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_compile_maquette_runs_generator_three_lualatex_passes_and_pdfinfo -q`.** Attendu : FAIL faute d'orchestrateur.
- [ ] **Step 7: Implémenter `compile_maquette(manifest_path, root)` et les codes 0/1/2.** Interdire dans le log `!`, `Undefined control sequence`, références indéfinies et dans le texte `??`.
- [ ] **Step 8: Réexécuter l'étape 6.** Attendu : `1 passed`.
- [ ] **Step 9: Écrire `test_maquette_v5_acceptance` sans marqueur pytest personnalisé.** Le test appelle la CLI réelle et exige le résumé exact `MAQUETTE V5: PASS — 15 pages; blanches 6,14; renvois 2/2; marginnote colonnes 0`.
- [ ] **Step 10: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_maquette_v5_acceptance -q`.** Attendu RED : compilation ou critères d'itération 1 en échec.

## Chunk 2: Gabarits v5 et assemblage sans réécriture

### Task 4: Corriger marks, ouverture et pages blanches

**Files:**
- Modify: `gabarits/nexus-manuel-v5.cls`
- Modify: `build/maquette-v5/maquette.tex`
- Test: `tests/test_maquette_v5.py`

- [ ] **Step 1: Écrire `test_navigation_and_blank_page_source_contract`.** Exiger une classe de marks dédiée, lecture du mark de page, `\ouverturechapitreV`, style `blanche` sans en-tête/pied, `current page`, `opacity=0.04`, et aucune commande/glyphe `diamond` dans l'implémentation blanche.
- [ ] **Step 2: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_navigation_and_blank_page_source_contract -q`.** Attendu : FAIL sur la classe v5 HEAD.
- [ ] **Step 3: Implémenter les marks et `\ouverturechapitreV`.** Le sommaire rend exactement neuf entrées et les folios du manifeste ; `\rubrique` n'est appelé qu'après la coupure précédente.
- [ ] **Step 4: Implémenter `blanche` et `\nxPageBlancheDecoree`.** Aucun folio ni `\null` textuel ; seul le TikZ overlay expédie la page.
- [ ] **Step 5: Réexécuter l'étape 2.** Attendu : `1 passed`.
- [ ] **Step 6: Étendre l'acceptation PDF pour extraire page par page `OUVERTURE` p.1, `COURS` p.2–5, `MÉTHODES` p.7–8, `EXERCICES` p.9–10, `FAIRE LE POINT` p.11–12, diagnostics p.13, `CORRIGÉS` p.15, les neuf temps et zéro `??`.** Ce test restera rouge jusqu'à l'assemblage complet.

### Task 5: Corriger la grille de cours

**Files:**
- Modify: `gabarits/nexus-manuel-v5.cls`
- Test: `tests/test_maquette_v5.py`

- [ ] **Step 1: Écrire `test_course_margin_and_non_orphan_source_contract`.** Exiger filet fin, interligne explicite, espacement vertical minimal et enveloppe non sécable pour `pourAllerPlusLoin`, sans `marginparwidth=0` dans le cours.
- [ ] **Step 2: Exécuter le test ciblé.** Attendu : FAIL.
- [ ] **Step 3: Implémenter l'adaptation locale des macros de marge et du bloc d'approfondissement.** Ne modifier aucun fichier de cours.
- [ ] **Step 4: Réexécuter le test ciblé.** Attendu : `1 passed`.

### Task 6: Composer la méthode appariée et son fallback

**Files:**
- Modify: `gabarits/nexus-manuel-v5.cls`
- Modify: `build/maquette-v5/maquette.tex`
- Test: `tests/test_maquette_v5.py`

- [ ] **Step 1: Écrire `test_method_pairing_redirects_annotations_and_defines_fallback`.** Exiger `methodePairee`, `separationApplications`, call-outs ①②③, deux à trois applications, warning `NEXUS-V5-PAIRING-FALLBACK`, redirection `MARGINNOTE-REDIRECTED` et marqueur interdit distinct.
- [ ] **Step 2: Exécuter le test ciblé.** Attendu : FAIL.
- [ ] **Step 3: Implémenter M1 à gauche et l'adaptateur d'applications à droite.** `\commentaireMarge` devient appel/légende interne ; `\marginnote` ne peut appeler l'original lorsque `\ifnxDeuxColonnes` est vrai.
- [ ] **Step 4: Ajouter `test_method_pairing_fallback_fixture_compiles` avec une paire d'une seule application.** Attendu initial : FAIL sans warning/fallback.
- [ ] **Step 5: Implémenter la dégradation simple largeur puis exécuter les deux tests.** Attendu : `2 passed`, warning présent uniquement dans la fixture.

### Task 7: Adapter les exercices depuis META

**Files:**
- Modify: `gabarits/nexus-manuel-v5.cls`
- Modify: `build/maquette-v5/maquette.tex`
- Generate: `build/maquette-v5/renvois.tex`
- Test: `tests/test_maquette_v5.py`

- [ ] **Step 1: Écrire `test_exercise_adapter_source_contract`.** Exiger adaptation locale de `exercice` dans `grilleExercices`, labels générés, losanges 1/2/3, pictos et renvois ; interdire l'émission du premier argument ID.
- [ ] **Step 2: Exécuter le test ciblé.** Attendu : FAIL.
- [ ] **Step 3: Implémenter l'adaptateur et inclure `renvois.tex`.** `maquette.tex` conserve uniquement les vingt `\input` d'objets source.
- [ ] **Step 4: Réexécuter le test ciblé.** Attendu : `1 passed`.

### Task 8: Sécuriser QCM et corrigés sans toucher les diagnostics

**Files:**
- Modify: `gabarits/nexus-manuel-v5.cls`
- Modify: `build/maquette-v5/maquette.tex`
- Test: `tests/test_maquette_v5.py`

- [ ] **Step 1: Écrire `test_qcm_and_corrections_source_contract`.** Exiger `\tfrac`, item principal emballé sans coupure, titre Corrigés unique et mark Corrigés après coupure.
- [ ] **Step 2: Écrire `test_qcm_source_hash_is_unchanged`.** Comparer au SHA-256 canonique du manifeste.
- [ ] **Step 3: Exécuter les deux tests.** Attendu : au moins le contrat source FAIL, hash PASS.
- [ ] **Step 4: Implémenter les contextes QCM/corrigés dans la seule classe v5.** Ne modifier ni le QCM ni ses diagnostics.
- [ ] **Step 5: Réexécuter les deux tests.** Attendu : `2 passed`.

### Task 9: Fermer l'acceptation PDF

**Files:**
- Modify: `scripts/check_maquette_v5.py`
- Modify: `tests/test_maquette_v5.py`
- Modify as required by failing criterion only: `gabarits/nexus-manuel-v5.cls`, `build/maquette-v5/maquette.tex`

- [ ] **Step 1: Compléter la CLI avec `pdfinfo`, `pdftotext` par page, chaînes exactes, rubriques attendues, pages blanches manifeste, IDs techniques absents, log marginal, SHA QCM et `compare -metric AE` page 13 contre `validations/v5-it1/page-13.png` égal à zéro.**
- [ ] **Step 2: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_maquette_v5_acceptance -q`.** Attendu : `1 passed` et résumé PASS exact.
- [ ] **Step 3: Exécuter `python3 -m pytest tests/test_maquette_v5.py -q`.** Attendu : tous les tests v5 PASS, aucun `PytestUnknownMarkWarning`.

## Chunk 3: Livrables, inspection et commit isolé

### Task 10: Produire et inspecter les livrables

**Files:**
- Produce locally: `build/maquette-v5/maquette.pdf`
- Create once as immutable reference: `validations/v5-it1/page-13.png`
- Modify/Create: `validations/v5/page-01.png` … `validations/v5/page-15.png`
- Modify: `MAQUETTE_V5_A_VALIDER.md`

- [ ] **Step 1: Exécuter `python3 scripts/check_maquette_v5.py --manifest build/maquette-v5/manifest.json`.** Attendu : résumé PASS exact et code 0.
- [ ] **Step 2: Avant la première compilation v5-it2, rasteriser la page 13 du PDF d'itération 1 en `validations/v5-it1/page-13.png`, puis exécuter `pdftoppm -png -r 150 build/maquette-v5/maquette.pdf validations/v5/page`.** Attendu : référence AVANT présente et exactement `page-01.png` à `page-15.png` pour it2.
- [ ] **Step 3: Produire `/tmp/maquette-v5-it2-contact.png` avec `montage validations/v5/page-{01..15}.png -thumbnail 240x340 -tile 5x3 -geometry +8+8 /tmp/maquette-v5-it2-contact.png`.**
- [ ] **Step 4: Inspecter la planche puis les pages 1, 2–5, 6, 7–8, 9–10, 11–13, 14 et 15 à pleine résolution.** Vérifier visuellement chacun des huit critères de la matrice et que la page 13 conserve sa grille/table.
- [ ] **Step 5: Mettre à jour `MAQUETTE_V5_A_VALIDER.md`.** Inclure chemins exacts, commande/preuve automatique, tableau AVANT/APRÈS des huit critères, et `PAUSE BLOQUANTE — EN ATTENTE DE « MAQUETTE V5 VALIDÉE »` ; ne lancer aucun déploiement.

### Task 11: Vérifier et créer le commit demandé

**Files:**
- Version: classe, maquette, manifeste forcé, scripts, tests, docs, rapport, référence `v5-it1/page-13.png` et 15 PNG it2.
- Do not version: `build/maquette-v5/renvois.tex`, auxiliaires LaTeX et PDF (livrable local conforme à la convention existante).

- [ ] **Step 1: Lire complètement `superpowers:verification-before-completion` et `superpowers:finishing-a-development-branch`.**
- [ ] **Step 2: Exécuter `python3 -m pytest tests/test_maquette_v5.py -q`, `python3 scripts/check_maquette_v5.py --manifest build/maquette-v5/manifest.json`, `make check-latex` et `python3 -m pytest tests/ -q`.** Attendu : tous codes 0 ; 15 pages ; contrôles v5 PASS ; suite générale au moins `1633 passed, 5 skipped` plus les nouveaux tests.
- [ ] **Step 3: Exécuter `git diff --check`.** Attendu : aucune sortie.
- [ ] **Step 4: Ajouter uniquement l'allowlist v5, avec `git add -f build/maquette-v5/manifest.json` et sans ajouter le PDF/renvois/auxiliaires.**
- [ ] **Step 5: Exécuter `git diff --cached --check`, comparer `git diff --cached --name-only` à l'allowlist et lire `git diff --cached`.** Attendu : aucun fichier TSPE, NSI ou v4.1.
- [ ] **Step 6: Créer le commit `git commit -m '[CHARTE][V5.B-it2] maquette v5 iteration 2'`.** Le commit est le livrable d'itération ; la pause bloque le déploiement ultérieur, pas la création de ce commit de validation.
- [ ] **Step 7: Vérifier `git show --stat --oneline HEAD` et l'absence de push/déploiement.**
