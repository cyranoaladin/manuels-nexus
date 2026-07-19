# Page 13 Diagnostics Layout Fix Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recomposer la page 13 en pleine largeur, sans superposition ni débordement, en conservant le QCM source et les quatorze autres pages à l'identique.

**Architecture:** `faireLePoint` reste responsable de la transition QCM → diagnostics, mais le mode diagnostics ne rouvre plus `multicols`. Le contrôleur acquiert deux validateurs indépendants : inspection des marqueurs/logs TeX et inspection géométrique XHTML issue de `pdftotext -bbox-layout`; les PNG hors p.13 sont protégés par SHA-256 et la nouvelle p.13 par SHA + comparaison AE.

**Tech Stack:** Python 3.11, pytest, LuaLaTeX, KOMA-Script, `multicol`, Poppler (`pdftotext -bbox-layout`, `pdftoppm`), ImageMagick (`compare`, `identify`).

**Spec:** `docs/superpowers/specs/2026-07-19-page-13-diagnostics-layout-fix-design.md`

**Working directory:** toutes les commandes ci-dessous sont exécutées depuis
`Mathematiques/manuel-maths` dans le worktree `charte-v5-b-it2`.

---

## Chunk 1: Régression observable et correction de classe

### Task 1: Validateurs de log et de géométrie

**Files:**
- Modify: `scripts/check_maquette_v5.py`
- Modify: `tests/test_maquette_v5.py`

- [ ] **Step 1: écrire les tests unitaires rouges des marqueurs diagnostics.** Ajouter `test_diagnostics_log_contract` avec trois intervalles START/END propres ; exiger le rejet d'un marqueur absent/déséquilibré, d'un quatrième intervalle, d'un `Overfull \\hbox` et d'un `Overfull \\vbox` dans n'importe quel intervalle.
- [ ] **Step 2: exécuter `python3 -m pytest tests/test_maquette_v5.py::test_diagnostics_log_contract -q`.** Attendu : FAIL, `assert_diagnostics_log_clean` absent.
- [ ] **Step 3: implémenter `assert_diagnostics_log_clean(log, expected_passes=3)`.** Extraire la séquence de tous les marqueurs et exiger exactement `START, END` répété trois fois ; rejeter `START START END END`, tout marqueur parasite et tout ordre croisé, puis inspecter chaque corps.
- [ ] **Step 4: réexécuter le test de l'étape 2.** Attendu : `1 passed`.
- [ ] **Step 5: écrire les tests unitaires rouges du parseur bbox.** Ajouter une fixture XHTML avec en-tête `Corrigés` à y≈36, titre, en-tête `Question`, quinze lignes Q1–Q15, 45 lignes A/C/D, dernière ligne « placement de la virgule », `Réponses correctes`, grille Q1–Q15, `Score` contenant les octets de contrôle `\x03` issus des `\square`, puis pied `NEXUS RÉUSSITE` et folio à y≈806. Tester un document conforme puis les variantes : chevauchement tableau/réponses, chevauchement réponses/score, xMin < 56, xMax > 459.5 ou yMax > 768 sur une ligne du corps, ligne Q manquante et diagnostic manquant ; l'en-tête et le pied hors bornes restent admis.
- [ ] **Step 6: exécuter `python3 -m pytest tests/test_maquette_v5.py::test_diagnostics_bbox_contract -q`.** Attendu : FAIL, `assert_diagnostics_bbox_layout` absent.
- [ ] **Step 7: implémenter `assert_diagnostics_bbox_layout(xhtml)`.** Supprimer d'abord uniquement les caractères interdits par XML 1.0 avec `re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", xhtml)`, puis utiliser `xml.etree.ElementTree`, normaliser chaque ligne et calculer ses bornes. Délimiter trois régions par les ancres titre → `Réponses correctes` → `Score`; exiger Q1–Q15 et 45 lignes `A|C|D :` dans la première, Q11–Q15 dans la seconde, puis appliquer la marge de 6 pt. Contrôler les limites seulement sur les lignes du corps, en excluant sémantiquement l'en-tête, `NEXUS RÉUSSITE` et le folio ; lever `AcceptanceError` avec le critère en échec. Le test doit prouver que les cases nettoyées n'empêchent pas de retrouver les Q du score.
- [ ] **Step 8: réexécuter le test de l'étape 6 puis les deux tests unitaires.** Attendu : `2 passed`.

### Task 2: Reproduction PDF de la page 13 cassée

**Files:**
- Modify: `tests/test_maquette_v5.py`
- Preserve: `chapitres/1SPE-DERIVATION-LOCAL/qcm/1SPE-DERIVATION-LOCAL-QCM.tex`

- [ ] **Step 1: ajouter `test_page13_diagnostics_layout_pdf`.** Générer les renvois, lancer trois LuaLaTeX, concaténer leurs sorties, extraire p.12–15 avec `pdftotext -layout` et p.13 avec `-bbox-layout`. Appeler d'abord le validateur géométrique, puis exiger trois paires de marqueurs propres, les quatre chaînes diagnostics seulement p.13, un seul `Corrigés` p.13, p.14 vide, deux `Corrigés` p.15 et le hash QCM canonique.
- [ ] **Step 2: exécuter `python3 -m pytest tests/test_maquette_v5.py::test_page13_diagnostics_layout_pdf -q`.** Attendu RED d'abord sur la géométrie actuelle (réponses au-dessus de la fin du tableau), indépendamment des marqueurs encore absents ; le log confirme séparément 314,99474 pt et 54,94688 pt de débordement.
- [ ] **Step 3: vérifier que l'échec est dû au rendu et non à la fixture.** Consigner dans le test les quatre chaînes diagnostics exactes et utiliser le PDF réel, sans mock.

### Task 3: Pleine largeur et typographie locale

**Files:**
- Modify: `gabarits/nexus-manuel-v5.cls:505-560`
- Modify: `tests/test_maquette_v5.py`

- [ ] **Step 1: ajouter au contrat source les exigences rouges.** Dans `test_qcm_and_corrections_source_contract`, exiger START/END, `\fontsize{6.6}{7.6}\selectfont`, `\setlength{\tabcolsep}{2pt}`, `\renewcommand{\arraystretch}{1.08}`, absence de `\begin{multicols}{2}` après l'écriture du mark `Corrigés`, et fermeture conditionnelle à la fin.
- [ ] **Step 2: exécuter le contrat source.** Attendu RED sur ces nouvelles exigences.
- [ ] **Step 3: modifier minimalement `faireLePoint`.** À l'interception du `\newpage`, fermer le QCM multicolonné, expédier p.12, écrire le mark, activer le mode diagnostics et le marqueur START, appliquer les trois valeurs typographiques, mais ne pas rouvrir `multicols`. À la fin, fermer `multicols` seulement hors diagnostics ; en mode diagnostics, exécuter d'abord `\clearpage` pour expédier p.13, écrire END immédiatement après, puis restaurer l'onglet sans seconde fermeture de colonnes.
- [ ] **Step 4: exécuter `python3 -m pytest tests/test_maquette_v5.py::test_qcm_and_corrections_source_contract tests/test_maquette_v5.py::test_page13_diagnostics_layout_pdf -q -x`.** Attendu GREEN ; si la géométrie échoue, ne modifier qu'une seule valeur typographique à la fois et documenter l'hypothèse.
- [ ] **Step 5: vérifier le log réel.** Entre START/END : zéro `Overfull \\hbox`, zéro `Overfull \\vbox`; le hash du QCM reste `cb34cb2351761e1c60d15eb5b95bcbc656c718fb19b6dca15290e3df3384b9e3`.

## Chunk 2: Contrôleur, références et livraison

Les hashes hors p.13 sont figés avant tout nouveau rendu, directement depuis le
commit validé `67d979b`. Table canonique :

```text
01 1e065c44ee1cd031aad570b4f4c5a98aa7ced55bceba78f418ff3ba31d63a24d
02 83eaaf15bad92a303ce8c367c3dffd498fea505930aaf4be6b06322bd2d07d10
03 4247bbe4325551dd26164476f9773fc8a11f1a131f3481a8da39e60b8e95c1c1
04 8229c5aaa4bcec461bf8442c4c448655315a4fb2fedf11a0052dcebdfb8c93c2
05 54d58a7128379386bfb32f79f6e8b0a3e8ea1916cdd785df748044fac2fcd30a
06 c9ab92b231ec622b7e0312355cd5168dc3e7c678fdcfb9cf994cf9db389a5e71
07 b3499d26ce3c43b206b1913bc3a3bc6960bd0827e131a4634d8807f4f7ecd233
08 7dc9d309b149ce5717e1f7aeab803c45f282c6cb4a4973668ffb3d1d267764ac
09 fbe900adaa69d7374e0be7ead78dcc2295e03d35671281e4c7e0890d656e726e
10 50aec5774963497bdf290b68c571dfa3d13336ded825e5969a3aee66834497be
11 91f971e7ae61251c03e023fcd680982667810e2639d0d5aec02a66140129684d
12 eeb87208366ce9f12da4cd478040ad417bcfea65d9b65c591cad477555832093
14 c9ab92b231ec622b7e0312355cd5168dc3e7c678fdcfb9cf994cf9db389a5e71
15 988b636d4f82ae6fcad93a4651cb43639744aa9094e1d31a4e190a36da1e91b4
```

Avant Task 4, vérifier au moins une fois chaque valeur par
`git show 67d979b:Mathematiques/manuel-maths/validations/v5/page-XX.png | sha256sum`.

### Task 4: Acceptation bout en bout de la nouvelle page 13

**Files:**
- Modify: `scripts/check_maquette_v5.py`
- Modify: `tests/test_maquette_v5.py`

- [ ] **Step 1: étendre le faux outillage des tests.** Le faux LuaLaTeX émet une paire START/END par passe ; le faux `pdftotext -bbox-layout` renvoie la fixture géométrique conforme.
- [ ] **Step 2: écrire les attentes rouges de l'acceptation.** Exiger dans le contrôleur trois intervalles de log propres, la géométrie p.13, les quatre chaînes propres aux diagnostics, l'absence p.12/14 et les rubriques/onglets p.13/p.15.
- [ ] **Step 3: exécuter `python3 -m pytest tests/test_maquette_v5.py::test_checker_cli_synthetic_exit_codes tests/test_maquette_v5.py::test_maquette_v5_acceptance -q -x`.** Attendu RED sur le premier critère non branché.
- [ ] **Step 4: brancher les validateurs dans `compile_maquette`/`accept_maquette`.** Ajouter l'extraction bbox p.13 au résultat compilé ou dans l'acceptation, sans dupliquer les appels externes inutiles.
- [ ] **Step 5: réexécuter les deux tests.** Attendu : les nouveaux contrôles structurels passent et l'acceptation réelle atteint l'ancien oracle, puis échoue avec AE non nul contre `validations/v5-it1/page-13.png`; aucune nouvelle référence n'est créée automatiquement.

### Task 5: Protection des quatorze pages et nouvel oracle p.13

**Files:**
- Modify: `scripts/check_maquette_v5.py`
- Modify: `tests/test_maquette_v5.py`
- Create: `validations/v5-it2/page-13.png`
- Modify: `validations/v5/page-13.png`

- [ ] **Step 1: ajouter la table SHA-256 des PNG hors p.13.** Copier exactement les quatorze valeurs canoniques ci-dessus, issues de `67d979b` avant rerendu ; le test échoue si une page 1–12 ou 14–15 change après le rendu à 150 dpi.
- [ ] **Step 2: exécuter le test PDF réel.** Attendu : hashes hors p.13 identiques et p.13 différente de `validations/v5-it1/page-13.png`.
- [ ] **Step 3: inspecter `validations/v5/page-13.png` à pleine résolution.** Vérifier lisibilité ≥6,6 pt, alignement, ordre tableau/réponses/score, absence de texte au-delà des bordures et marge avant le pied.
- [ ] **Step 4: créer mécaniquement `validations/v5-it2/page-13.png` depuis le rendu inspecté.** Calculer son SHA-256 et l'ajouter à `PAGE_13_REFERENCE_SHA256`.
- [ ] **Step 5: remplacer tous les usages de l'ancien oracle.** Le contrôleur vérifie le SHA de `validations/v5-it2/page-13.png` puis exige `compare -metric AE = 0` avec le rendu courant. Migrer aussi `test_qcm_diagnostics_and_corrections_pdf` vers l'oracle it2 ; conserver uniquement l'assertion du SHA historique de `validations/v5-it1/page-13.png`, sans comparaison AE. Dans `test_checker_cli_synthetic_exit_codes`, copier la nouvelle référence it2 dans le `synthetic_root` pour que chemin et SHA soient réels avant le faux `compare`.
- [ ] **Step 6: exécuter `python3 -m pytest tests/test_maquette_v5.py::test_page13_diagnostics_layout_pdf tests/test_maquette_v5.py::test_maquette_v5_acceptance -q`.** Attendu : `2 passed`.

### Task 6: Rapport, revue et vérification finale

**Files:**
- Modify: `MAQUETTE_V5_A_VALIDER.md`
- Modify: `docs/superpowers/specs/2026-07-19-page-13-diagnostics-layout-fix-design.md` seulement si l'implémentation révèle une contrainte validée différente
- Modify: `docs/superpowers/plans/2026-07-19-page-13-diagnostics-layout-fix.md` pour cocher les étapes terminées

- [ ] **Step 1: mettre à jour le rapport.** Remplacer « page 13 non retouchée/AE=0 it1 » par l'audit des deux débordements, la pleine largeur, les preuves bbox/log, le hash it2 et la pause bloquante inchangée.
- [ ] **Step 2: exécuter `python3 scripts/check_maquette_v5.py --manifest build/maquette-v5/manifest.json`.** Attendu exact : `MAQUETTE V5: PASS — 15 pages; blanches 6,14; renvois 2/2; marginnote colonnes 0`.
- [ ] **Step 3: exécuter `python3 -m pytest tests/test_maquette_v5.py -q`.** Attendu : tous les tests v5 passent.
- [ ] **Step 4: exécuter `make check-latex` puis `python3 -m pytest tests/ -q`.** Attendu : codes 0, aucune régression.
- [ ] **Step 5: demander une revue indépendante.** Résoudre tout P0/P1, relancer les validations affectées et vérifier visuellement p.13.
- [ ] **Step 6: vérifier l'isolation.** `git diff --check`, worktree principal inchangé, aucun fichier QCM/TSPE/NSI modifié, aucun push/déploiement.
- [ ] **Step 7: créer un commit local limité à la correction p.13.** Message : `[CHARTE][V5.B-it2] corrige diagnostics page 13`.
