# Dynamic Rubric Tab Length Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adapter automatiquement la longueur des onglets latéraux au libellé afin que `AUTO-ÉVALUATION` reste entièrement lisible sur les pages 11 et 12, sans modifier les autres contenus.

**Architecture:** `\nxOngletRubrique` compose une seule fois le mark résolu dans une boîte locale, calcule `max(16 mm, largeur + 6 mm)`, puis réutilise cette dimension pour le rectangle et le centre du texte sur les deux parités. Une fixture PDF teste la contenance par corrélation entre BBox Poppler et composante colorée raster ; l'acceptation complète conserve les anciens rendus p.11–12, consacre les nouveaux oracles itération 2 et protège toutes les autres pages par hash/AE.

**Tech Stack:** LaTeX/LuaLaTeX, TikZ, KOMA-Script marks, Python 3.11, pytest, Pillow, Poppler (`pdftotext -bbox-layout`, `pdftoppm`), ImageMagick (`compare`, `identify`).

**Spec:** `docs/superpowers/specs/2026-07-20-dynamic-rubric-tab-length-design.md`

**Working directory:** toutes les commandes sont exécutées depuis `Mathematiques/manuel-maths` dans le worktree `charte-v5-b-it2`.

---

## Chunk 1: Preuve rouge et correction de classe

### Task 1: Historique p.11–12 et test géométrique rouge

**Files:**
- Create: `validations/v5-it1/page-11.png`
- Create: `validations/v5-it1/page-12.png`
- Modify: `tests/test_maquette_v5.py`
- Preserve: `gabarits/nexus-manuel-v5.cls`

- [ ] **Step 1: figer les deux rendus défectueux avant toute recompilation.** Copier mécaniquement `validations/v5/page-11.png` et `page-12.png` vers `validations/v5-it1/`. Vérifier les SHA historiques directement contre le commit `f2aee3d` :

```text
page-11 91f971e7ae61251c03e023fcd680982667810e2639d0d5aec02a66140129684d
page-12 eeb87208366ce9f12da4cd478040ad417bcfea65d9b65c591cad477555832093
```

- [ ] **Step 2: ajouter le contrat source rouge.** Créer `test_rubric_tab_dynamic_source_contract` et isoler le corps de `\nxOngletRubrique`. Exiger une boîte de mesure locale, la police exacte, `+6mm`, le minimum `16mm`, une dimension unique pour les deux rectangles et leurs demi-décalages, `inner sep=0pt`, ainsi que l'absence des deux extensions fixes `-16mm`/`+(-12mm,-16mm)` actuelles.
- [ ] **Step 3: ajouter les helpers de géométrie de test.** Dans `tests/test_maquette_v5.py`, parser le XHTML `pdftotext -bbox-layout`, sélectionner le mot tourné au bord extérieur plutôt que l'en-tête courant, puis charger le PNG 300 dpi avec Pillow. Dans la bande extérieure et la zone haute, isoler la composante connexe de pixels `chapcolor` qui contient l'onglet ; convertir les BBox PDF en pixels avec `300/72`.
- [ ] **Step 4: écrire `test_rubric_tab_dynamic_fixture_pdf`.** Compiler une fixture de quatre pages : `Cours` p.1–2, puis `Auto-évaluation` p.3–4, avec pages impaire et paire. Rendre à 300 dpi et extraire les quatre BBox. Pour chaque page, exiger inclusion du texte dans le rectangle et asymétrie longitudinale ≤0,5 mm. Exiger en plus :
  - onglet `COURS` = 16 mm avec tolérance raster ≤0,5 pt ;
  - onglet `AUTO-ÉVALUATION` strictement plus long que 16 mm ;
  - padding de chaque extrémité ≥3 mm −0,5 pt ;
  - même longueur à ±0,5 pt entre pages paire/impaire d'un même libellé.
- [ ] **Step 5: exécuter les deux tests rouges.**

```bash
python3 -m pytest \
  tests/test_maquette_v5.py::test_rubric_tab_dynamic_source_contract \
  tests/test_maquette_v5.py::test_rubric_tab_dynamic_fixture_pdf -q -x
```

Attendu : le contrat source échoue sur l'absence de mesure automatique ; en l'exécutant seul après confirmation, la fixture échoue sur la contenance/padding de `AUTO-ÉVALUATION`. Aucun fichier de classe ne doit avoir changé.
- [ ] **Step 6: exécuter le test des SHA historiques.** Étendre `test_validation_png_reference_hashes` pour vérifier les deux copies it1, puis exécuter ce test. Attendu : PASS.
- [ ] **Step 7: commit.**

```bash
git add tests/test_maquette_v5.py validations/v5-it1/page-11.png validations/v5-it1/page-12.png
git commit -m "[CHARTE][V5.B-it2] reproduit onglets trop courts"
```

### Task 2: Longueur automatique dans la classe v5

**Files:**
- Modify: `gabarits/nexus-manuel-v5.cls:70-96`
- Modify: `tests/test_maquette_v5.py` uniquement si la fixture révèle une différence de parsing démontrée, jamais pour relâcher les seuils

- [ ] **Step 1: déclarer les registres dédiés.** Ajouter une boîte, une longueur totale et une demi-longueur dont les noms sont spécifiques à l'onglet, par exemple :

```tex
\newsavebox{\nxVOngletTextBox}
\newlength{\nxVOngletLength}
\newlength{\nxVOngletHalfLength}
```

- [ ] **Step 2: composer et mesurer une fois dans un groupe local.** À l'intérieur de `\nxOngletRubrique`, après le test de suppression et avant TikZ :

```tex
\begingroup
\sbox{\nxVOngletTextBox}{{\titrefont\fontsize{6}{6}\selectfont
  \color{white}\MakeUppercase{\nxRubriquePage}}}%
\setlength{\nxVOngletLength}{\dimexpr\wd\nxVOngletTextBox+6mm\relax}%
\ifdim\nxVOngletLength<16mm\setlength{\nxVOngletLength}{16mm}\fi
\setlength{\nxVOngletHalfLength}{\nxVOngletLength}%
\divide\nxVOngletHalfLength by 2
```

Fermer le groupe après le TikZ. Ne pas créer de globale de rubrique et ne pas contourner `\nxRubriquePage`.
- [ ] **Step 3: piloter fond et texte avec les mêmes longueurs.** Remplacer `-16mm` par `-\nxVOngletLength` sur les deux rectangles ; remplacer le `-8mm` vertical du nœud par `-\nxVOngletHalfLength` ; rendre `\usebox{\nxVOngletTextBox}` dans le nœud avec `inner sep=0pt`. Conserver 12 mm, les rotations, le côté, l'ancrage extérieur et `\ongletY`.
- [ ] **Step 4: exécuter le contrat source.** Attendu : PASS.
- [ ] **Step 5: exécuter la fixture réelle.** Attendu : PASS sur les quatre pages et aucun `Overfull` dans la sortie LuaLaTeX.
- [ ] **Step 6: exécuter les tests de navigation existants.**

```bash
python3 -m pytest \
  tests/test_maquette_v5.py::test_navigation_opening_and_blank_source_contract \
  tests/test_maquette_v5.py::test_navigation_blank_fixture_pdf \
  tests/test_maquette_v5.py::test_rubric_tab_dynamic_source_contract \
  tests/test_maquette_v5.py::test_rubric_tab_dynamic_fixture_pdf -q
```

Attendu : tous PASS.
- [ ] **Step 7: commit.**

```bash
git add gabarits/nexus-manuel-v5.cls tests/test_maquette_v5.py
git commit -m "[CHARTE][V5.B-it2] adapte longueur des onglets"
```

## Chunk 2: Acceptation visuelle et livraison

### Task 3: Oracles p.11–12 et contrôleur bout en bout

**Files:**
- Modify: `scripts/check_maquette_v5.py`
- Modify: `tests/test_maquette_v5.py`
- Modify: `validations/v5/page-11.png`
- Modify: `validations/v5/page-12.png`
- Create: `validations/v5-it2/page-11.png`
- Create: `validations/v5-it2/page-12.png`
- Preserve: `validations/v5/page-13.png`
- Preserve: `validations/v5-it2/page-13.png`
- Preserve: `chapitres/1SPE-DERIVATION-LOCAL/qcm/1SPE-DERIVATION-LOCAL-QCM.tex`

- [ ] **Step 1: écrire les attentes rouges du contrôleur.** Ajouter les constantes `HISTORICAL_TAB_PAGE_REFERENCE_SHA256` pour p.11–12 et `TAB_PAGE_REFERENCE_SHA256` pour les futurs oracles it2. Étendre les tests pour exiger : SHA historiques, SHA it2, `AE=0` p.11 et p.12, et rejet indépendant d'une différence sur chacun. Le faux environnement copie les quatre références p.11–12 et distingue `compare_diff_tab_11`, `compare_diff_tab_12` et `compare_diff_page_13`.
- [ ] **Step 2: exécuter les tests synthétiques.**

```bash
python3 -m pytest \
  tests/test_maquette_v5.py::test_validation_png_reference_hashes \
  tests/test_maquette_v5.py::test_checker_cli_synthetic_exit_codes -q -x
```

Attendu : RED, car les références it2 p.11–12 et le branchement du contrôleur n'existent pas.
- [ ] **Step 3: recompiler la maquette complète sans modifier les hashes.**

```bash
python3 scripts/check_maquette_v5.py --manifest build/maquette-v5/manifest.json
```

Attendu : échec uniquement sur `page 11 altérée` ou `page 12 altérée` après que les contrôles structurels ont passé. Conserver les PNG générés dans `validations/v5/`.
- [ ] **Step 4: prouver l'isolation avant consécration.** Calculer les SHA des quinze PNG et vérifier que seuls p.11–12 diffèrent de `f2aee3d`; vérifier que p.13 vaut toujours `2edeb64a24a83e38a88a0aefab83e54452eec3c9270cbeee3dc3afefb201af23`.
- [ ] **Step 5: inspecter p.11 et p.12 à pleine résolution.** Utiliser `view_image` en détail original et des crops 100 %. Vérifier le libellé complet, le padding, le centrage, la symétrie, l'absence de contact avec le corps et la continuité de la couleur. Ne pas créer d'oracle si l'inspection échoue.
- [ ] **Step 6: créer mécaniquement les oracles it2.** Copier les deux PNG inspectés vers `validations/v5-it2/`, calculer leurs SHA, puis renseigner `TAB_PAGE_REFERENCE_SHA256`. Remplacer uniquement les entrées 11 et 12 de `NON_DIAGNOSTICS_PAGE_SHA256`.
- [ ] **Step 7: brancher les trois comparaisons actuelles.** Dans `accept_maquette`, vérifier d'abord les SHA it1 p.11–12, puis les SHA it2, puis `compare -metric AE = 0` entre oracles it2 et images générées p.11–12. Conserver sans changement les preuves et la comparaison p.13.
- [ ] **Step 8: mettre à jour le faux outillage.** Copier les références réelles dans le `synthetic_root`; faire retourner `AE=42` uniquement pour la page désignée par le mode. Vérifier que les messages identifient p.11, p.12 ou p.13 sans ambiguïté.
- [ ] **Step 9: exécuter les contrôles ciblés.**

```bash
python3 -m pytest \
  tests/test_maquette_v5.py::test_rubric_tab_dynamic_fixture_pdf \
  tests/test_maquette_v5.py::test_validation_png_reference_hashes \
  tests/test_maquette_v5.py::test_checker_cli_synthetic_exit_codes \
  tests/test_maquette_v5.py::test_maquette_v5_acceptance -q
```

Attendu : tous PASS ; AE p.11/p.12/p.13 = 0 ; 15 pages ; p.14 vide ; QCM canonique inchangé.
- [ ] **Step 10: commit.**

```bash
git add scripts/check_maquette_v5.py tests/test_maquette_v5.py \
  validations/v5/page-11.png validations/v5/page-12.png \
  validations/v5-it2/page-11.png validations/v5-it2/page-12.png
git commit -m "[CHARTE][V5.B-it2] fige onglets auto-evaluation"
```

### Task 4: Rapport, vérification complète et revue

**Files:**
- Modify: `MAQUETTE_V5_A_VALIDER.md`
- Modify: `docs/superpowers/plans/2026-07-20-dynamic-rubric-tab-length.md`

- [ ] **Step 1: mettre à jour le tableau AVANT/APRÈS.** Documenter p.11–12 : fond fixe 16 mm et texte blanc partiellement invisible → longueur automatique, police 6 pt, épaisseur 12 mm, padding minimal 3 mm, preuves géométriques et SHA des deux oracles.
- [ ] **Step 2: exécuter le contrôleur public.**

```bash
python3 scripts/check_maquette_v5.py --manifest build/maquette-v5/manifest.json
```

Attendu exact :

```text
MAQUETTE V5: PASS — 15 pages; blanches 6,14; renvois 2/2; marginnote colonnes 0
```

- [ ] **Step 3: exécuter les tests v5.**

```bash
python3 -m pytest tests/test_maquette_v5.py -q
```

Attendu : code 0, aucune régression.
- [ ] **Step 4: exécuter les contrôles dépôt.**

```bash
make check-latex
python3 -m pytest tests/ -q
git diff --check
```

Attendu : codes 0.
- [ ] **Step 5: vérifier les invariants.** Le SHA QCM reste
  `cb34cb2351761e1c60d15eb5b95bcbc656c718fb19b6dca15290e3df3384b9e3` ;
  p.13 conserve son SHA/oracle `2edeb64a24a83e38a88a0aefab83e54452eec3c9270cbeee3dc3afefb201af23` ;
  aucun fichier TSPE/NSI n'est modifié ; aucune branche principale, aucun push et
  aucun déploiement ne sont effectués.
- [ ] **Step 6: demander une revue indépendante du diff complet.** Résoudre tout finding P0/P1/P2, relancer les validations affectées et faire confirmer visuellement les deux parités.
- [ ] **Step 7: cocher le plan et créer le commit documentaire final.**

```bash
git add MAQUETTE_V5_A_VALIDER.md \
  docs/superpowers/plans/2026-07-20-dynamic-rubric-tab-length.md
git commit -m "[CHARTE][V5.B-it2] documente onglets adaptatifs"
```

- [ ] **Step 8: conserver la branche isolée.** Worktree propre, branche `charte/v5-b-it2`, aucun merge/push/déploiement avant `MAQUETTE V5 VALIDÉE`.
