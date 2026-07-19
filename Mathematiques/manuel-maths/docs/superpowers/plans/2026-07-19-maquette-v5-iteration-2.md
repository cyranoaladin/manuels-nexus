# Maquette v5 — Itération 2 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produire et contrôler une maquette v5 itération 2 de 15 pages, sans réécriture des objets ni impact sur v4.1, TSPE ou le déploiement.

**Architecture:** La classe v5 isole la composition ; un manifeste canonique fixe l'échantillon ; un générateur Python valide les META et produit les tables LaTeX ; un contrôleur indépendant compile, inspecte le PDF et génère les livrables. Le QCM source et la page 13 de référence sont immuables.

**Tech Stack:** Python 3.11, pytest, LuaLaTeX/KOMA-Script, TikZ, poppler (`pdfinfo`, `pdftotext`, `pdftoppm`), ImageMagick (`compare`, `montage`).

---

## Chunk 1: Contrats de données, génération et contrôleur testable

### Task 1: Manifeste canonique et parseur META

**Files:**
- Create: `build/maquette-v5/manifest.json`
- Create: `scripts/build_maquette_v5.py`
- Create: `tests/test_maquette_v5.py`
- Reference: `docs/superpowers/specs/2026-07-19-maquette-v5-iteration-2-design.md`

- [ ] **Step 1: Écrire le bootstrap d'import du test.** Définir `ROOT = Path(__file__).resolve().parents[1]`, insérer `str(ROOT / "scripts")` dans `sys.path`, puis importer d'abord `MetaError` et `load_manifest`; l'import de `parse_meta` est ajouté avec les tests de l'étape 6.
- [ ] **Step 2: Écrire `test_canonical_manifest_contract`.** Le test exige le schéma normatif complet de la spec : version 2, PDF, 15 pages, blanches `[6,14]`, 4 méthodes canoniques, M1 + applications 001/002/005, ordre canonique des 20 exercices, répartition `{"9":11,"10":9}`, trois pictos, hash QCM, cinq corrigés, neuf couples temps/folio et deux chaînes exactes.
- [ ] **Step 3: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_canonical_manifest_contract -q`.** Attendu RED : échec `FileNotFoundError` ou `ModuleNotFoundError` directement lié aux fichiers absents.
- [ ] **Step 4: Créer le manifeste exactement comme dans la section « Manifeste normatif » de la spec et le squelette `build_maquette_v5.py`.** Définir `MetaError`; `load_manifest(path, root)` retourne un dict ou lève `MetaError`.
- [ ] **Step 5: Réexécuter l'étape 3.** Attendu GREEN : `1 passed`.
- [ ] **Step 6: Ajouter l'import de `parse_meta` puis écrire `test_parse_meta_exercise_contract` paramétré.** Couvrir META absente, après ligne 10, JSON invalide, ID vide, mauvais `type_objet`, `methodes` vide/mal formé, `parcours` hors 1–3/non entier, `duree_min <= 0`, chemin absolu/hors racine/absent, `fichier_tex` discordant et corrigé absent ; chaque cas lève `MetaError`.
- [ ] **Step 7: Écrire `test_parse_meta_method_contract`.** Une méthode valide n'exige que `id`, `type_objet="methode"`, `methodes`; champs manquants ou code non `M[0-9]+` lèvent `MetaError`.
- [ ] **Step 8: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_parse_meta_exercise_contract tests/test_maquette_v5.py::test_parse_meta_method_contract -q`.** Attendu RED : `parse_meta` incomplet.
- [ ] **Step 9: Implémenter `parse_meta(path, root)`.** Lire au plus dix lignes, résoudre les chemins sous `root` avec `Path.relative_to`, valider les branches exercice/méthode séparément et ne jamais lire/émettre le corps de l'objet.
- [ ] **Step 10: Réexécuter l'étape 8.** Attendu GREEN : tous les cas passent.
- [ ] **Step 11: Écrire `test_generator_cli_invalid_json_returns_2_without_traceback`.** Lancer la CLI réelle sur un JSON syntaxiquement invalide ; exiger code 2, `META V5:` dans stderr et absence de `Traceback`.
- [ ] **Step 12: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_generator_cli_invalid_json_returns_2_without_traceback -q`.** Attendu RED : point d'entrée CLI absent ou traceback.
- [ ] **Step 13: Implémenter le point d'entrée CLI minimal puis réexécuter la commande de l'étape 12.** Attendu GREEN : `1 passed`.

### Task 2: Table de renvois déterministe

**Files:**
- Modify: `scripts/build_maquette_v5.py`
- Modify: `tests/test_maquette_v5.py`
- Generate only: `build/maquette-v5/renvois.tex`

- [ ] **Step 1: Écrire `test_build_reference_table_rejects_duplicate_unknown_and_bad_pairing`.** Doublon et ID inconnu lèvent `MetaError`; 0/1 applications connues sont valides avec fallback; 2/3 valides rendent une paire; 4 lèvent `MetaError`.
- [ ] **Step 2: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_build_reference_table_rejects_duplicate_unknown_and_bad_pairing -q`.** Attendu RED : fonction `build_reference_table` absente.
- [ ] **Step 3: Implémenter `build_reference_table(manifest, root)`.** Indexer les META par ID canonique, préserver `exercise_order`, calculer numéros visibles, méthode, durée, parcours, picto, chemin d'input et chemin de corrigé.
- [ ] **Step 4: Réexécuter l'étape 2.** Attendu GREEN : `1 passed`.
- [ ] **Step 5: Écrire `test_generator_cli_unknown_id_returns_2_without_traceback`, puis exécuter `python3 -m pytest tests/test_maquette_v5.py::test_generator_cli_unknown_id_returns_2_without_traceback -q`.** Attendu RED : la CLI ne valide pas encore les références inter-fichiers.
- [ ] **Step 6: Brancher `build_reference_table` dans la CLI et réexécuter la commande de l'étape 5.** Attendu GREEN : `1 passed`.
- [ ] **Step 7: Écrire `test_render_reference_table_exact_contract`.** Exiger les 20 labels `ex:<ID>`, 4 labels `meth:<ID>`, `corr:start`, losanges 1/2/3, trois pictos, la chaîne `S'entraîner : ex. 1, 2, 7 p. 9`, la chaîne `→ M1 · Corrigé p. 15`, et interdire tout corps d'énoncé.
- [ ] **Step 8: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_render_reference_table_exact_contract -q`.** Attendu RED : fonction de rendu absente.
- [ ] **Step 9: Implémenter `render_reference_table(records, manifest)`.** Produire seulement des `\csname`/déclarations lookup, labels et chaînes ; l'ID n'est permis que dans les noms internes et arguments de labels.
- [ ] **Step 10: Réexécuter la commande de l'étape 8.** Attendu GREEN : `1 passed`.
- [ ] **Step 11: Écrire `test_generator_cli_success_returns_0`, puis exécuter `python3 -m pytest tests/test_maquette_v5.py::test_generator_cli_success_returns_0 -q`.** Attendu RED : la CLI ne rend pas encore le fichier/résumé final.
- [ ] **Step 12: Achever la CLI et réexécuter la commande de l'étape 11.** Attendu GREEN : `1 passed`.
- [ ] **Step 13: Exécuter en plus `python3 scripts/build_maquette_v5.py --manifest build/maquette-v5/manifest.json --output build/maquette-v5/renvois.tex`.** Attendu : résumé exact `RENVOIS V5: 20 exercices, 1 méthode, 3 pictogrammes` et code 0.

### Task 3: Contrôleur PDF unitaire et orchestration synthétique

**Files:**
- Create: `scripts/check_maquette_v5.py`
- Modify: `tests/test_maquette_v5.py`

- [ ] **Step 1: Écrire `test_pdf_text_helpers_and_margin_log_contract`.** Exiger que form-feed, espaces ASCII/Unicode et sauts seuls donnent une page vide ; que les deux chaînes normalisées soient trouvées ; que `NEXUS-V5-MARGINNOTE-REDIRECTED` soit admis et `NEXUS-V5-MARGINNOTE-COLUMNS-EMITTED` fatal.
- [ ] **Step 2: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_pdf_text_helpers_and_margin_log_contract -q`.** Attendu RED : module/fonctions absents.
- [ ] **Step 3: Implémenter `normalize_text`, `page_text_is_empty`, `required_strings_present`, `assert_no_two_column_marginnotes` et `AcceptanceError`.
- [ ] **Step 4: Réexécuter l'étape 2.** Attendu GREEN : `1 passed`.
- [ ] **Step 5: Écrire `test_compile_maquette_calls_generator_three_lualatex_and_pdfinfo`.** Créer de faux exécutables `python3`, `lualatex`, `pdfinfo` et `pdftotext` dans `tmp_path/bin`, journaliser leurs argv/cwd via un fichier, préfixer `PATH`, appeler `compile_maquette`; exiger générateur ×1, LuaLaTeX ×3, pdfinfo ×1, pdftotext ×1 et cwd `ROOT`. Le faux `pdftotext` renvoie un texte sain sans `??`.
- [ ] **Step 6: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_compile_maquette_calls_generator_three_lualatex_and_pdfinfo -q`.** Attendu RED : orchestrateur absent.
- [ ] **Step 7: Implémenter `run_checked` et `compile_maquette(manifest_path, root)`.** Rejeter code non nul, `Undefined control sequence`, ligne d'erreur `!`, références indéfinies et `??` extrait.
- [ ] **Step 8: Réexécuter l'étape 6.** Attendu GREEN : `1 passed`.
- [ ] **Step 9: Écrire `test_checker_cli_synthetic_exit_codes` avec faux outils : manifeste invalide → 2, compilation/acceptation invalide → 1, succès synthétique → 0, tous sans traceback.** Ne pas créer encore l'acceptation réelle.
- [ ] **Step 10: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_checker_cli_synthetic_exit_codes -q`.** Attendu RED : `main()` absent/incomplet.
- [ ] **Step 11: Implémenter `main()` puis réexécuter la commande de l'étape 10.** Attendu GREEN : `1 passed`.
- [ ] **Step 12: Exécuter `python3 -m pytest tests/test_maquette_v5.py -q`.** Attendu GREEN pour tout le chunk 1.

## Chunk 2: Classe v5 et assemblage déclaratif

### Task 4: Marks, ouverture et pages blanches

**Files:**
- Modify: `gabarits/nexus-manuel-v5.cls`
- Modify: `build/maquette-v5/maquette.tex`
- Modify: `tests/test_maquette_v5.py`

- [ ] **Step 1: Écrire `test_navigation_opening_and_blank_source_contract`.** Exiger une classe de marks dédiée, lecture du mark de page, `\ouverturechapitreV`, séquence coupure→blanche→nouveau mark, `\thispagestyle{blanche}`, boîte vide sans glyphe, `current page`, `opacity=0.04`, et interdire `diamond`/`⋄`/`◆` dans la macro blanche.
- [ ] **Step 2: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_navigation_opening_and_blank_source_contract -q`.** Attendu RED sur la classe HEAD.
- [ ] **Step 3: Implémenter `\rubrique`, `\nxRubriquePage`, `\nxPageBlancheDecoree` et `blanche`.** La page est expédiée par `\vbox to \textheight{\vfil}`; le mark suivant n'est écrit qu'après `\clearpage` et la blanche éventuelle.
- [ ] **Step 4: Implémenter `\ouverturechapitreV` et l'assemblage p.1.** Réutiliser les quatre blocs existants, afficher exactement neuf temps/folios et l'onglet OUVERTURE.
- [ ] **Step 5: Réexécuter l'étape 2.** Attendu GREEN : `1 passed`.
- [ ] **Step 6: Écrire `test_navigation_blank_fixture_pdf`.** Compiler une fixture de cinq pages et extraire chaque page ; exiger marks A/A, page blanche vide, puis marks B/B et sommaire sans `??`.
- [ ] **Step 7: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_navigation_blank_fixture_pdf -q`.** Attendu RED initial sur le mark ou la page vide ; après correction limitée à la classe, réexécuter et obtenir GREEN : `1 passed`.

### Task 5: Cours à marge active et pagination sûre

**Files:**
- Modify: `gabarits/nexus-manuel-v5.cls`
- Modify: `build/maquette-v5/maquette.tex`
- Modify: `tests/test_maquette_v5.py`

- [ ] **Step 1: Écrire `test_course_source_contract`.** Exiger `\coursVocab`, `\coursRenvoi`, interligne 10 pt, filet 0,4 pt, espacement 9 pt, pas de `marginparwidth=0` dans le cours, compteur d'alertes réinitialisé au shipout, coupure avant la troisième, et `needspace` pour `\approfondissement`.
- [ ] **Step 2: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_course_source_contract -q`.** Attendu RED : interfaces absentes.
- [ ] **Step 3: Implémenter les registres et adaptations locales.** Les deux notes vocabulaire et le renvoi reprennent des formulations déjà présentes ; ne modifier aucun fichier `cours/*.tex`.
- [ ] **Step 4: Réexécuter l'étape 2.** Attendu GREEN : `1 passed`.
- [ ] **Step 5: Écrire `test_course_fixture_pdf`.** Compiler les deux inputs réels p.2–5 ; extraire deux termes vocabulaire et un renvoi, compter au plus deux titres `Erreur fréquente` par page, vérifier le titre `Pour aller plus loin` avec au moins deux lignes sur la même page et un blanc final <25 %.
- [ ] **Step 6: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_course_fixture_pdf -q`.** Attendu RED sur la pagination HEAD adaptée.
- [ ] **Step 7: Ajuster seulement les seuils de la classe, réexécuter l'étape 6.** Attendu GREEN : `1 passed`.

### Task 6: Méthode appariée, call-outs et fallback

**Files:**
- Modify: `gabarits/nexus-manuel-v5.cls`
- Modify: `build/maquette-v5/maquette.tex`
- Modify: `tests/test_maquette_v5.py`

- [ ] **Step 1: Écrire `test_method_pairing_source_contract`.** Exiger `methodePairee`, `separationApplications`, call-outs ①②③, légendes groupées, note bas de bloc, test `marginparwidth=0pt` ou multicol, markers REDIRECTED/EMITTED et fallback warning.
- [ ] **Step 2: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_method_pairing_source_contract -q`.** Attendu RED.
- [ ] **Step 3: Implémenter l'adaptateur local.** L'input M1 reste inchangé ; `\commentaireMarge` devient appels/légendes ; `\refExos{M1}` lit la chaîne générée ; les trois inputs d'application restent inchangés et sans badges techniques.
- [ ] **Step 4: Réexécuter l'étape 2.** Attendu GREEN.
- [ ] **Step 5: Écrire `test_method_pairing_fixtures`.** Compiler des manifestes à 0,1,2,3 applications et valider 0/1 fallback avec warning, 2/3 paire sans warning, REDIRECTED autorisé, EMITTED absent ; tester 4 applications et ID inconnu via CLI → code 2.
- [ ] **Step 6: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_method_pairing_fixtures -q`.** Attendu RED initial sur au moins un cas.
- [ ] **Step 7: Achever fallback et validations, puis réexécuter.** Attendu GREEN : `1 passed`.

### Task 7: Exercices inchangés, badges META et renvois

**Files:**
- Modify: `gabarits/nexus-manuel-v5.cls`
- Modify: `build/maquette-v5/maquette.tex`
- Modify: `tests/test_maquette_v5.py`
- Consume generated: `build/maquette-v5/renvois.tex`

- [ ] **Step 1: Écrire `test_exercise_adapter_source_contract`.** Exiger vingt `\input` d'exercices inchangés dans l'ordre manifeste, adaptation locale de `exercice`, lookup par premier argument sans composition, trois niveaux de losanges, trois pictos, labels et renvois ; interdire les copies inline d'énoncés.
- [ ] **Step 2: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_exercise_adapter_source_contract -q`.** Attendu RED.
- [ ] **Step 3: Implémenter l'adaptateur et l'assemblage p.9–10.** Garder le filet `\columnseprule=0.3pt`; rediriger toute marginnote vers la note bas de bloc ; ne jamais appeler l'original.
- [ ] **Step 4: Réexécuter l'étape 2.** Attendu GREEN.
- [ ] **Step 5: Écrire `test_exercise_grid_fixture_pdf`.** Exiger 11 badges p.9, 9 p.10, les deux chaînes exactes, trois pictos, vingt IDs techniques absents, markers EMITTED absents et détection raster du filet central sur chaque page.
- [ ] **Step 6: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_exercise_grid_fixture_pdf -q`.** Attendu RED initial sur un compte/renvoi/filet ; après correction limitée à la classe, réexécuter et obtenir GREEN : `1 passed`.

### Task 8: QCM compact, diagnostics immuables et corrigés

**Files:**
- Modify: `gabarits/nexus-manuel-v5.cls`
- Modify: `build/maquette-v5/maquette.tex`
- Modify: `tests/test_maquette_v5.py`
- Preserve: `chapitres/1SPE-DERIVATION-LOCAL/qcm/1SPE-DERIVATION-LOCAL-QCM.tex`
- Reference: `validations/v5-it1/page-13.png`

- [ ] **Step 1: Écrire `test_qcm_hash_is_immutable` puis exécuter `python3 -m pytest tests/test_maquette_v5.py::test_qcm_hash_is_immutable -q`.** Exiger le SHA-256 canonique. Attendu GREEN : `1 passed` avant tout changement.
- [ ] **Step 2: Écrire `test_qcm_and_corrections_source_contract`.** Exiger `\tfrac` local p.11–12, items groupés, interception du `\newpage` unique, fermeture du contexte étroit avant p.13, restauration gabarit/mark Corrigés, coupure→blanche p.14→mark Corrigés, titre unique et `\label{corr:start}` unique avant les cinq corrigés.
- [ ] **Step 3: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_qcm_and_corrections_source_contract -q`.** Attendu RED.
- [ ] **Step 4: Implémenter les contextes v5 sans toucher le QCM ni les corrigés sources.** Les IDs des corrigés ne sont pas composés.
- [ ] **Step 5: Réexécuter l'étape 3.** Attendu GREEN.
- [ ] **Step 6: Écrire `test_qcm_diagnostics_and_corrections_pdf`.** Compiler l'assemblage réel, vérifier fractions compactes et items complets p.11–12, lancer `compare -metric AE validations/v5-it1/page-13.png <raster-p13>` et exiger `0`, puis exiger un seul titre/mark Corrigés p.15.
- [ ] **Step 7: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_qcm_diagnostics_and_corrections_pdf tests/test_maquette_v5.py::test_qcm_hash_is_immutable -q`.** Attendu RED initial sur pagination/raster ; après correction limitée au contexte, réexécuter et obtenir GREEN : `2 passed`, hash inchangé et page 13 AE=0.

## Chunk 3: Acceptation réelle, livrables et commit isolé

### Task 9: Acceptation bout en bout

**Files:**
- Modify: `scripts/check_maquette_v5.py`
- Modify: `tests/test_maquette_v5.py`

- [ ] **Step 1: Écrire maintenant `test_maquette_v5_acceptance`.** Appeler la CLI réelle ; exiger code 0 et stdout exact `MAQUETTE V5: PASS — 15 pages; blanches 6,14; renvois 2/2; marginnote colonnes 0`.
- [ ] **Step 2: Exécuter `python3 -m pytest tests/test_maquette_v5.py::test_maquette_v5_acceptance -q`.** Attendu RED sur le premier critère d'acceptation encore absent.
- [ ] **Step 3: Compléter le contrôleur un critère à la fois.** Exiger 15 pages ; rubriques page par page ; neuf temps/folios ; blanches 6/14 ; chaînes 2/2 ; 20 IDs absents ; badges 11/9 ; filet ; log marginal ; hash QCM ; p.13 AE=0 ; zéro `??`/erreur/référence indéfinie ; puis générer exactement les 15 PNG `validations/v5/page-01.png` à `page-15.png` à 150 dpi et vérifier leur résolution.
- [ ] **Step 4: Réexécuter l'étape 2 après chaque critère corrigé.** Attendu final GREEN : `1 passed` et résumé exact.
- [ ] **Step 5: Exécuter `python3 -m pytest tests/test_maquette_v5.py -q`.** Attendu : tous les tests v5 passent, sans warning pytest.

### Task 10: PDF, PNG, inspection et rapport AVANT/APRÈS

**Files:**
- Produce local: `build/maquette-v5/maquette.pdf`
- Add: `validations/v5-it1/page-13.png`
- Add/Modify: `validations/v5/page-01.png` … `page-15.png`
- Modify: `MAQUETTE_V5_A_VALIDER.md`

- [ ] **Step 1: Exécuter `python3 scripts/check_maquette_v5.py --manifest build/maquette-v5/manifest.json`.** Attendu : résumé PASS exact et code 0.
- [ ] **Step 2: Vérifier la provenance de la référence.** `git merge-base --is-ancestor 7d64cdc HEAD` retourne 0 ; le PNG p.13 existe, fait 150 dpi et son hash est consigné dans le rapport.
- [ ] **Step 3: Vérifier les PNG it2 générés par le contrôleur.** Exiger exactement `page-01.png` à `page-15.png`, résolution 150 dpi et dates postérieures au PDF ; ne pas les produire par une voie parallèle.
- [ ] **Step 4: Construire `/tmp/maquette-v5-it2-contact.png` avec `montage validations/v5/page-{01..15}.png -thumbnail 240x340 -tile 5x3 -geometry +8+8 /tmp/maquette-v5-it2-contact.png`.
- [ ] **Step 5: Inspecter la planche et chaque page à pleine résolution.** Vérifier les huit défauts, les 11/9 badges, les deux filets, fractions, call-outs, blancs décorés, et l'intégrité diagnostics.
- [ ] **Step 6: Mettre à jour `MAQUETTE_V5_A_VALIDER.md`.** Ajouter fichiers exacts, commande/preuve, hash référence, et tableau `Défaut | AVANT it1 | APRÈS it2 | Preuve | Statut`; terminer par `PAUSE BLOQUANTE — EN ATTENTE DE « MAQUETTE V5 VALIDÉE »`.
- [ ] **Step 7: Bloquer sur tout défaut visuel.** Le tableau doit avoir huit statuts APRÈS au vert et zéro défaut ouvert. Sinon corriger le seul composant responsable, relancer Task 9 au complet, régénérer/inspecter les PNG et mettre à jour le rapport avant Task 11.

### Task 11: Vérification finale et commit demandé

**Files:**
- Stage only: classe v5, maquette, manifeste forcé, scripts v5, tests v5, spec/plan, rapport, référence p.13 et 15 PNG.
- Never stage: classe v4.1, chapitres source, TSPE, NSI, PDF/auxiliaires/`renvois.tex` ignorés.

- [ ] **Step 1: Lire complètement `superpowers:verification-before-completion`, `superpowers:requesting-code-review` et `superpowers:finishing-a-development-branch`.**
- [ ] **Step 2: Demander une revue finale indépendante et résoudre tout point bloquant.**
- [ ] **Step 3: Exécuter frais `python3 -m pytest tests/test_maquette_v5.py -q`.** Attendu : tous les tests v5 passent.
- [ ] **Step 4: Exécuter frais `python3 scripts/check_maquette_v5.py --manifest build/maquette-v5/manifest.json`.** Attendu : résumé PASS exact.
- [ ] **Step 5: Exécuter frais `make check-latex` puis `python3 -m pytest tests/ -q`.** Attendu : codes 0, aucune régression.
- [ ] **Step 6: Capturer l'état du worktree principal avec `git -C /home/alaeddine/Documents/Manuels_Nexus status --short` et comparer à l'état initial consigné ; exiger aucune modification causée par it2.**
- [ ] **Step 7: Écrire l'allowlist exacte dans `/tmp/maquette-v5-it2-allowlist.txt`, puis comparer avec `git status --short --untracked-files=all` normalisé.** Échec si un fichier modifié/non suivi n'est pas dans l'allowlist ou si un chemin v4.1, `chapitres/`, TSPE ou NSI apparaît.
- [ ] **Step 8: Exécuter `git diff --check`.** Attendu : aucune sortie.
- [ ] **Step 9: Ajouter uniquement l'allowlist v5, avec `git add -f build/maquette-v5/manifest.json`, puis exécuter `git diff --cached --check`, comparer exactement `git diff --cached --name-only` à l'allowlist et lire le diff staged.** Attendu : zéro fichier v4.1/chapitre/TSPE/NSI et aucun artefact ignoré.
- [ ] **Step 10: Créer `git commit -m '[CHARTE][V5.B-it2] maquette v5 iteration 2'`.**
- [ ] **Step 11: Vérifier `git show --stat --oneline HEAD`, recontrôler le worktree principal inchangé, et confirmer qu'aucun push/déploiement n'a été lancé.**
