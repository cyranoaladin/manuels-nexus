# 1NSI Canonical Manual Assembler Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** déclarer, construire et attester les sept variantes canoniques du manuel 1NSI, en couvrant les dix chapitres et les 109 corrigés actuellement hors assemblage, sans assembler TNSI.

**Architecture:** `NSI/scripts/assemble_manuel.py` devient l'unique déclaration statique et runtime des variantes manuelles 1NSI. L'analyseur lit ses règles littérales par AST, tandis que l'assembleur réutilise les primitives sûres existantes et produit des reçus validés par `scripts/build_manifest.py`. Le préflight commun devient sensible au rôle sans affaiblir les contrôles PDF.

**Tech Stack:** Python 3.12, pytest, LuaLaTeX, PyMuPDF, Poppler, YAML/JSON Schema, inventaire Nexus.

---

## Chunk 1: Modèle d'assemblage déclaré

### Task 1: Fermer la sélection de variante dans le contrat AST

**Files:**
- Modify: `tests/test_inventory_collection.py`
- Modify: `scripts/inventory_assembly.py`
- Modify: `scripts/inventory_collection.py`

- [ ] **Step 1: Write failing parser and selection tests**

Exiger `VARIANT_ORDERS` et `ELEVE_VARIANTS` dans les constantes AST, l'égalité
des clés de `VARIANT_ORDERS` avec `VARIANTS`, des règles bien formées, et un
`ELEVE_VARIANTS` non vide inclus dans les variantes et contenant `eleve`.
Tester aussi les sélections `evaluations` et `projets`, les filtres metadata
sur toutes les variantes élèves et l'allowlist de
`NSI/scripts/assemble_manuel.py`.

- [ ] **Step 2: Run tests and verify RED**

```bash
pytest -q \
  tests/test_inventory_collection.py::test_manual_variant_orders_are_literal_closed_and_validated \
  tests/test_inventory_collection.py::test_declared_variant_orders_drive_specialized_manual_selection \
  tests/test_inventory_collection.py::test_graph_source_role_policies_are_explicit
```

Expected: FAIL because the analyzer ignores the new literals and the NSI manual
assembler is not allowlisted.

- [ ] **Step 3: Implement the minimal inventory model**

Étendre `analyze_assembler`, `validate_analysis`, `select_items` et
`_build_manual_assemblies`. Refuser les tables partielles, variantes étrangères,
règles mal formées et assembleurs élèves sans filtre metadata fail-closed.

- [ ] **Step 4: Run adjacent tests**

```bash
pytest -q tests/test_inventory_collection.py -k 'assembler or assembl or source_role_policies'
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/inventory_assembly.py scripts/inventory_collection.py tests/test_inventory_collection.py
git commit -m "[AUDIT] ferme le contrat des variantes manuelles"
```

## Chunk 2: Assembleur 1NSI exécutable

### Task 2: Construire les sept variantes avec séparation de rôle

**Files:**
- Create: `NSI/scripts/assemble_manuel.py`
- Create: `NSI/tests/test_assemble_manuel.py`
- Modify: `NSI/scripts/assemble.py`
- Modify: `NSI/scripts/pdf_integrity.py`
- Modify: `NSI/tests/test_pdf_integrity.py`
- Modify: `NSI/gabarits/book_master.tex`
- Modify: `NSI/Makefile`
- Modify: `tests/test_inventory_collection.py`

- [ ] **Step 1: Write failing runtime tests**

Exiger les dix `CHAPITRES`, les sept `VARIANTS`, `VARIANT_ORDERS` et
`ELEVE_VARIANTS` exacts ; les 109 chemins `corriges/` dans `professeur` et
aucun dans les cinq variantes élèves ; `evaluations` en rôle professeur et
`projets` en rôle élève ; le setup LaTeX propre à chaque rôle ; les sorties
`NSI/build/MANUEL_1NSI/MANUEL_1NSI_<variant>.pdf` ; le rejet avant écriture
d'une variante inconnue ou vide ; et le dispatch de `make book`.

Ajouter les tests du préflight : contrôles communs toujours actifs, recherche de
fuite uniquement lorsque le rôle élève l'exige.

Écrire dès cette étape RED le test réel de parité des sept listes
`included_objects`, les assertions zéro chapitre/objet 1NSI hors assemblage,
et les assertions d'absence d'assembly manuelle TNSI.

- [ ] **Step 2: Run tests and verify RED**

```bash
cd NSI
pytest -q tests/test_assemble_manuel.py tests/test_pdf_integrity.py
```

Expected: FAIL because the canonical assembler and role-aware preflight do not exist.

- [ ] **Step 3: Implement selection, rendering and local build**

Créer l'adaptateur avec des littéraux purs utilisés au runtime et par AST.
Réutiliser les validations de manifeste, chemins, compilation, staging et
promotion de `assemble.py`. Remplacer les lignes de rôle figées du gabarit par
`%%VARIANT_SETUP%%`. Ajouter au préflight un paramètre explicite de contrôle
des fuites, conservé à `True` par défaut. Adapter aussi le mode livre
historique de `assemble.py` pour injecter son setup élève.

- [ ] **Step 4: Prove runtime/inventory parity**

Ajouter un test réel comparant, pour les sept variantes, les objets META runtime
avec `included_objects`. Vérifier également zéro chapitre 1NSI hors manuel,
zéro objet 1NSI non assemblé, aucune assembly manuelle TNSI et invariance des
variantes de chapitre TNSI.

- [ ] **Step 5: Run focused tests**

```bash
pytest -q NSI/tests/test_assemble_manuel.py NSI/tests/test_assemble_book.py NSI/tests/test_pdf_integrity.py
pytest -q tests/test_inventory_collection.py -k '1nsi or manual_assembler or variant_orders'
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add NSI/scripts/assemble_manuel.py NSI/scripts/assemble.py NSI/scripts/pdf_integrity.py NSI/gabarits/book_master.tex NSI/Makefile NSI/tests/test_assemble_manuel.py NSI/tests/test_pdf_integrity.py tests/test_inventory_collection.py
git commit -m "[LATEX] branche les sept variantes manuelles 1NSI"
```

## Chunk 3: Preuves observées

### Task 3: Émettre des reçus 1NSI fermés

**Files:**
- Modify: `NSI/scripts/assemble_manuel.py`
- Modify: `NSI/tests/test_assemble_manuel.py`
- Modify: `scripts/build_manifest.py`
- Modify: `audit/BUILD_PRODUCERS.yaml`
- Modify: `tests/test_build_manifest.py`

- [ ] **Step 1: Write failing receipt and producer tests**

Exiger un producteur `nsi-1nsi-manual` couvrant exactement les sept assembly IDs
`nsi:manual:1NSI:<variant>`. Tester un receipt fermé contenant uniquement les
champs admis : chemins des preuves, dépendances, reproductibilité, compilation,
préflight et `student_separation` seulement pour les variantes élèves. Tester
que le recorder dérive inclus/exclus/trace depuis FLS et journal, réexécute la
séparation pour les cinq variantes élèves, et ne conserve aucun receipt après
échec.

- [ ] **Step 2: Run tests and verify RED**

```bash
pytest -q NSI/tests/test_assemble_manuel.py tests/test_build_manifest.py -k '1nsi or producer or receipt'
```

Expected: FAIL because the producer and receipt path are absent.

- [ ] **Step 3: Implement observed recording**

Ajouter `--record-observed`. Après promotion, écrire atomiquement le receipt puis
appeler `scripts/build_manifest.py --receipt`. Réutiliser le schéma et les
contrôles de provenance existants. Généraliser dans le recorder la décision de
séparation élève à partir du contrat de variante fermé. Recalculer le
`control_digest` canonique de `audit/BUILD_PRODUCERS.yaml`.

- [ ] **Step 4: Verify and commit**

```bash
pytest -q NSI/tests/test_assemble_manuel.py tests/test_build_manifest.py -k '1nsi or producer or receipt or student_separation'
python3 scripts/inventory_collection.py --validate-model
git add NSI/scripts/assemble_manuel.py NSI/tests/test_assemble_manuel.py scripts/build_manifest.py audit/BUILD_PRODUCERS.yaml tests/test_build_manifest.py
git commit -m "[PDF] atteste les producteurs manuels 1NSI"
```

## Chunk 4: Builds réels et audit

### Task 4: Construire et inventorier les sept PDF

**Files:**
- Modify: `NSI/.gitignore`
- Create: `NSI/build/MANUEL_1NSI/MANUEL_1NSI_eleve.pdf`
- Create: `NSI/build/MANUEL_1NSI/MANUEL_1NSI_professeur.pdf`
- Create: `NSI/build/MANUEL_1NSI/MANUEL_1NSI_methodes.pdf`
- Create: `NSI/build/MANUEL_1NSI/MANUEL_1NSI_remediation.pdf`
- Create: `NSI/build/MANUEL_1NSI/MANUEL_1NSI_amenagee.pdf`
- Create: `NSI/build/MANUEL_1NSI/MANUEL_1NSI_evaluations.pdf`
- Create: `NSI/build/MANUEL_1NSI/MANUEL_1NSI_projets.pdf`
- Modify: `audit/BUILD_MANIFEST.json`
- Modify: `audit/INVENTAIRE_COLLECTION.json`
- Modify: `audit/INVENTAIRE_COLLECTION.md`
- Modify: `audit/ECARTS_ET_CONTRADICTIONS.yaml`
- Modify: `audit/MATRICE_LIVRABLES.yaml`

- [ ] **Step 1: Build the seven PDFs without recording**

Sur le HEAD source propre, exécuter les sept commandes sans
`--record-observed`. Contrôler tous les PDF, logs, métadonnées, polices,
outlines et liens. Scanner les cinq PDF élèves contre les fuites ; vérifier la
présence attendue de contenu corrigé dans `professeur` et `evaluations`.

- [ ] **Step 2: Track and commit the canonical PDFs**

Modifier `NSI/.gitignore` pour réinclure exclusivement les sept PDF sous
`NSI/build/MANUEL_1NSI/`. Ajouter la règle et les sept PDF, vérifier le diff
indexé et committer :

```bash
git add NSI/.gitignore NSI/build/MANUEL_1NSI/*.pdf
git diff --cached --check
git status --short
git commit -m "[PDF] suit les sept manuels canoniques 1NSI"
```

- [ ] **Step 3: Refresh and commit the empty build manifest**

Après le commit des PDF, rafraîchir le manifeste vide sur l'arbre propre :

```bash
python3 scripts/build_manifest.py --refresh-empty
git diff --check
git status --short
git add audit/BUILD_MANIFEST.json
git diff --cached --check
git commit -m "[AUDIT] realigne le manifeste avant builds 1NSI"
```

- [ ] **Step 4: Rebuild and record all variants**

```bash
cd NSI
python3 scripts/assemble_manuel.py --variant eleve --record-observed
python3 scripts/assemble_manuel.py --variant professeur --record-observed
python3 scripts/assemble_manuel.py --variant methodes --record-observed
python3 scripts/assemble_manuel.py --variant remediation --record-observed
python3 scripts/assemble_manuel.py --variant amenagee --record-observed
python3 scripts/assemble_manuel.py --variant evaluations --record-observed
python3 scripts/assemble_manuel.py --variant projets --record-observed
```

Expected: seven canonical PDFs, seven manifest entries, no TNSI output.

- [ ] **Step 5: Verify reproducibility and commit the manifest**

Après chaque build observé, vérifier que seuls le manifeste et les preuves
ignorées ont changé : les sept PDF suivis doivent rester byte-identiques.

```bash
git add audit/BUILD_MANIFEST.json
git diff --cached --check
git status --short
git commit -m "[PDF] enregistre les sept builds canoniques 1NSI"
```

- [ ] **Step 6: Regenerate reports without updating baseline**

Régénérer l'inventaire, vérifier le diff déterministe, puis committer uniquement
les rapports générés. La baseline approuvée reste inchangée.

```bash
python3 scripts/inventory_collection.py
git diff --check
git add audit/INVENTAIRE_COLLECTION.json audit/INVENTAIRE_COLLECTION.md audit/ECARTS_ET_CONTRADICTIONS.yaml audit/MATRICE_LIVRABLES.yaml
git diff --cached --check
git status --short
git commit -m "[AUDIT] regenere la collection apres assemblage 1NSI"
```

## Chunk 5: Vérification finale

### Task 5: Prouver la réduction de dette et le gel TNSI

**Files:**
- Verify only

- [ ] **Step 1: Run full targeted suites**

```bash
pytest NSI/tests tests/test_inventory_collection.py tests/test_build_manifest.py --tb=short
```

- [ ] **Step 2: Run inventory gates**

```bash
python3 scripts/inventory_collection.py --check
python3 scripts/inventory_collection.py --validate-model
python3 scripts/inventory_collection.py --fail-on-new
python3 scripts/inventory_collection.py --release-strict
```

Expected: first three green; `--release-strict` red for remaining blockers.

- [ ] **Step 3: Prove scope and cleanliness**

```bash
git diff 5f6ebbf..HEAD --name-only -- 'NSI/chapitres/TNSI-*'
git diff 5f6ebbf..HEAD --name-only -- 'NSI/manifests/books/TNSI.json'
find NSI/build -iname '*TNSI*' -print
git status --short --branch
git diff --check
```

Expected: no TNSI chapter or manifest path, no TNSI build output, and a clean
worktree.

- [ ] **Step 4: Independent final review**

Faire relire le range pour conformité au design, sécurité des receipts,
séparation élève/professeur et absence d'affaiblissement des gates.
