# A6 Chapter PDF Path Reproducibility Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the chapter PDF producer byte-reproducible across different absolute worktree roots by sharing the A4 deterministic trailer identity contract.

**Architecture:** Extract only the existing A4 trailer preimage function into a focused shared module. Keep the manual producer API compatible. The chapter producer discovers the exhaustive repository input graph through a discarded `-recorder` pass, validates it fail-closed, then injects the shared deterministic `/ID` and verifies that the final recorder graph is unchanged.

**Tech Stack:** Python 3.12, pytest, LuaLaTeX/LuaTeX 1.17, qpdf, pdfinfo, pdftotext, Git.

---

## Chunk 1: TDD et correctif producteur

### Task 1: Reproduire le défaut inter-racines

**Files:**
- Modify: `Mathematiques/manuel-maths/tests/test_assemble_engine.py`
- Create: `audit/A6_CHAPTER_PDF_PATH_REPRODUCIBILITY.md`

- [ ] **Step 1: Ajouter la fixture de deux racines**

Créer `root-A` et `root-B` avec le même chapitre, contrat, master et classe
minimale. Compiler sous le même environnement A4 et comparer pages, texte,
QDF, trailer et octets.

- [ ] **Step 2: Vérifier RED**

Run:

```bash
python -m pytest -q \
  Mathematiques/manuel-maths/tests/test_assemble_engine.py \
  -k 'path_independent'
```

Expected: FAIL sur `pdf_a.read_bytes() == pdf_b.read_bytes()` ; les textes et
pages doivent déjà être identiques.

- [ ] **Step 3: Archiver le diagnostic réel**

Documenter le SHA source disqualifié, TCOMPL/complet, deux racines absolues,
pages, SHA PDF/QDF/texte, IDs et cause racine dans l'audit demandé.

### Task 2: Partager le contrat A4

**Files:**
- Create: `Mathematiques/manuel-maths/scripts/pdf_reproducibility.py`
- Modify: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
- Modify: `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py`
- Test: `Mathematiques/manuel-maths/tests/test_assemble_engine.py`

- [ ] **Step 1: Ajouter la matrice rouge des dix cas mandatés**

Tester au niveau PDF compilé : (1) racines absolues distinctes, (2) run IDs
distincts, (3) horloges distinctes, (4) mutation d'un octet pertinent,
(5) restauration exacte et (10) deux vrais worktrees Git. Tester au niveau
helper **et** PDF : (6) élève/professeur déterministes et distincts lorsque le
contenu ou la variante diffère, (7) chapitre distinct et (8) version producteur
distincte. Tester au niveau préimage : (9) remplacement d'un ancien PDF suivi
sans changement. Comparer octets/SHA, trailer, pages et texte selon le cas.

- [ ] **Step 2: Extraire la règle existante sans changer sa préimage**

Déplacer `PDF_TRAILER_ID_SCHEME`,
`PDF_TRAILER_PRODUCER_SCHEMA_VERSION` et `pdf_trailer_identity` dans le helper
commun. Les importer dans `assemble_manuel.py` pour préserver le producteur A4
et ses tests.

- [ ] **Step 3: Vérifier la non-régression A4 ciblée**

Run:

```bash
python -m pytest -q \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  -k 'trailer or reproducible_run_id'
```

Expected: PASS.

- [ ] **Step 4: Rejouer l'autorité A4 PDF1 à PDF10 intégralement**

Run:

```bash
python -m pytest -q tests/test_pdf_reproducibility.py
```

Expected: PASS sans modification de la sérialisation, de la normalisation des
chemins ni des identités manuels observées.

### Task 3: Injecter l'identité chapitre minimale

**Files:**
- Modify: `Mathematiques/manuel-maths/scripts/assemble.py`
- Test: `Mathematiques/manuel-maths/tests/test_assemble_engine.py`

- [ ] **Step 1: Découvrir le graphe effectif par une passe jetable**

Compiler avec `-recorder`, jeter le PDF provisoire et parser le `.fls`. Inclure
toute entrée Git suivie réellement lue dans le dépôt, y compris les dépendances
transitives de classe/charte/pont. Exclure seulement la toolchain externe et
les sorties générées confinées au build.

- [ ] **Step 2: Valider et canoniser fail-closed**

Exiger fichier lisible et suivi, chemin résolu sous la racine d'autorité, clé
Git relative canonique injective, supports obligatoires présents et aucune
dépendance interne non classée. Ajouter des mutations pour : objet, contrat,
gabarit, wrapper, classe/charte/pont et support transitif ; ainsi que support
absent, symlink hors racine, collision et entrée interne non suivie.

- [ ] **Step 3: Injecter le trailer partagé fail-closed**

Calculer l'ID avec `manual="chapter:<id>"`, la variante, le master final et le
graphe, puis injecter une seule ligne après `\documentclass`.

- [ ] **Step 4: Vérifier le graphe final puis GREEN et mutations**

Recompiler avec `-recorder`, reconstruire le graphe et exiger égalité exacte
des clés et hashes avec la découverte avant d'accepter le PDF.

Run:

```bash
python -m pytest -q Mathematiques/manuel-maths/tests/test_assemble_engine.py
```

Expected: tous PASS, y compris compilation byte-identique dans deux racines.

- [ ] **Step 5: Rejouer RED sans correctif puis restaurer GREEN**

Neutraliser temporairement l'injection dans une copie de test, constater la
divergence, puis rétablir le code et revérifier le PASS.

### Task 4: Revue et commit atomique

**Files:** tous les fichiers des Tasks 1–3.

- [ ] **Step 1: Exécuter ciblés, py_compile et diff-check**

- [ ] **Step 2: Faire relire spécification puis qualité**

- [ ] **Step 3: Commit atomique**

```bash
git add -- \
  Mathematiques/manuel-maths/scripts/pdf_reproducibility.py \
  Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  Mathematiques/manuel-maths/scripts/assemble.py \
  Mathematiques/manuel-maths/tests/test_assemble_engine.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  audit/A6_CHAPTER_PDF_PATH_REPRODUCIBILITY.md
git commit -m "[PDF] make chapter trailer identity path independent"
```

## Chunk 2: Re-scellement A6

### Task 5: Preuve réelle inter-clones avant replay global

**Files:** aucun fichier source.

- [ ] **Step 1: Créer deux clones neufs au commit producteur**
- [ ] **Step 2: Compiler TCOMPL/complet et parcours1 sous l'environnement A4**
- [ ] **Step 3: Exiger masters, pages, texte, trailer et PDF SHA A == B**
- [ ] **Step 4: STOP si le moindre octet diverge**

### Task 6: Rejouer la validation complète

**Files:** artefacts gérés uniquement si les digests sont stale.

- [ ] **Step 1: Rafraîchir manifeste vide puis inventaire par commits dédiés si requis**
- [ ] **Step 2: Rejouer root, Math, NSI et ciblés A1–A6**
- [ ] **Step 3: Rejouer check, validate-model, fail-on-new, release-strict et les 89 bindings**
- [ ] **Step 4: Rejouer les builds A6 TCOMPL et smoke 1NSI**
- [ ] **Step 5: Mettre à jour l'attestation A6 en marquant le SHA précédent disqualifié**
- [ ] **Step 6: Commit de scellement et obtenir le nouveau A6_SOURCE_SHA**

### Task 7: Fresh A / Fresh B définitifs

**Files:** aucun edit dans les clones.

- [ ] **Step 1: Recréer deux clones de zéro au nouveau SHA**
- [ ] **Step 2: Rejouer toutes les suites, gates, bindings et builds**
- [ ] **Step 3: Comparer inventaires, masters, pages, PDFs et digests A == B**
- [ ] **Step 4: Déclarer A6 PASS seulement sur preuve complète**
- [ ] **Step 5: Enchaîner immédiatement sur T1 structurel conformément au
  dernier mandat publish-ready, qui supersède le STOP de l'ancien lot A6**
