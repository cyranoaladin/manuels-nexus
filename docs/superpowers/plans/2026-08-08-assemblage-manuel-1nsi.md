# Manuel 1NSI Assembly Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** produire `MANUEL_1NSI_v1.pdf` depuis les 10 chapitres Première NSI déjà présents dans `NSI/chapitres/`.

**Architecture:** étendre `NSI/scripts/assemble.py` avec un mode `--book` adossé à un manifeste versionné décrivant le manuel. Le pipeline réutilise la collecte d'objets chapitre, la compilation LaTeX existante et `verify_pdf`, via un nouveau gabarit maître de manuel.

**Tech Stack:** Python 3.11, pytest, LuaLaTeX, gabarits LaTeX Nexus, scripts NSI existants.

---

## Chunk 1: Tests rouges pour le mode manuel

### Task 1: Définir l'API des manifestes de manuel

**Files:**
- Create: `NSI/tests/test_assemble_book.py`
- Modify: `NSI/scripts/assemble.py`

- [ ] **Step 1: Write the failing test**

```python
def test_load_book_manifest_1nsi():
    manifest = assemble.load_book_manifest("1NSI")
    assert manifest["output_name"] == "MANUEL_1NSI_v1"
    assert len(manifest["chapters"]) == 10
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd NSI && .venv/bin/python -m pytest tests/test_assemble_book.py -q`
Expected: FAIL with missing `load_book_manifest` or missing manifest file.

- [ ] **Step 3: Write minimal implementation**

```python
def load_book_manifest(book_id: str) -> dict:
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd NSI && .venv/bin/python -m pytest tests/test_assemble_book.py -q`
Expected: PASS for manifest loading assertions.

- [ ] **Step 5: Commit**

```bash
git add NSI/tests/test_assemble_book.py NSI/scripts/assemble.py
git commit -m "[1NSI][ASSEMBLAGE] ajoute les tests du mode manuel"
```

### Task 2: Figer la résolution ordonnée des chapitres

**Files:**
- Create: `NSI/tests/test_assemble_book.py`
- Modify: `NSI/scripts/assemble.py`

- [ ] **Step 1: Write the failing test**

```python
def test_collect_book_chapters_1nsi():
    chapters = assemble.collect_book_chapters("1NSI")
    assert chapters[0].name == "1NSI-TYPES-BASE"
    assert chapters[-1].name == "1NSI-PROJET-METHODES"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd NSI && .venv/bin/python -m pytest tests/test_assemble_book.py -q`
Expected: FAIL with missing `collect_book_chapters`.

- [ ] **Step 3: Write minimal implementation**

```python
def collect_book_chapters(book_id: str) -> list[Path]:
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd NSI && .venv/bin/python -m pytest tests/test_assemble_book.py -q`
Expected: PASS for ordered chapter resolution.

- [ ] **Step 5: Commit**

```bash
git add NSI/tests/test_assemble_book.py NSI/scripts/assemble.py
git commit -m "[1NSI][ASSEMBLAGE] fige l'ordre du manuel Premiere"
```

## Chunk 2: Implémentation minimale du pipeline livre

### Task 3: Ajouter le manifeste et le gabarit maître

**Files:**
- Create: `NSI/manifests/books/1NSI.json`
- Create: `NSI/gabarits/book_master.tex`

- [ ] **Step 1: Write the failing test**

```python
def test_book_master_template_exists():
    assert (ROOT / "gabarits" / "book_master.tex").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd NSI && .venv/bin/python -m pytest tests/test_assemble_book.py -q`
Expected: FAIL because template does not exist.

- [ ] **Step 3: Write minimal implementation**

```json
{
  "book_id": "1NSI",
  "title": "Manuel NSI Première",
  "niveau": "Première",
  "matiere": "NSI",
  "output_name": "MANUEL_1NSI_v1",
  "chapters": ["1NSI-TYPES-BASE", "..."]
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd NSI && .venv/bin/python -m pytest tests/test_assemble_book.py -q`
Expected: PASS for manifest and template existence.

- [ ] **Step 5: Commit**

```bash
git add NSI/manifests/books/1NSI.json NSI/gabarits/book_master.tex NSI/tests/test_assemble_book.py
git commit -m "[1NSI][ASSEMBLAGE] ajoute le manifeste et le gabarit du manuel"
```

### Task 4: Étendre `assemble.py` au mode `--book`

**Files:**
- Modify: `NSI/scripts/assemble.py`
- Modify: `NSI/Makefile`

- [ ] **Step 1: Write the failing test**

```python
def test_build_book_master_contains_all_chapters():
    tex = assemble.render_book_master("1NSI")
    assert "\\\\chapter" not in tex
    assert "1NSI-TYPES-BASE" in tex
    assert "1NSI-PROJET-METHODES" in tex
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd NSI && .venv/bin/python -m pytest tests/test_assemble_book.py -q`
Expected: FAIL with missing `render_book_master`.

- [ ] **Step 3: Write minimal implementation**

```python
def render_book_master(book_id: str) -> str:
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd NSI && .venv/bin/python -m pytest tests/test_assemble_book.py -q`
Expected: PASS with generated master text including all 10 chapters.

- [ ] **Step 5: Commit**

```bash
git add NSI/scripts/assemble.py NSI/Makefile NSI/tests/test_assemble_book.py
git commit -m "[1NSI][ASSEMBLAGE] ajoute le mode --book"
```

## Chunk 3: Vérification réelle

### Task 5: Vérifier tests ciblés et build du manuel

**Files:**
- Read/verify: `NSI/build/books/MANUEL_1NSI_v1.pdf`
- Read/verify: `NSI/build/books/MANUEL_1NSI_v1.log`

- [ ] **Step 1: Run focused tests**

Run: `cd NSI && .venv/bin/python -m pytest tests/test_assemble_book.py -q`
Expected: PASS

- [ ] **Step 2: Run regression-adjacent tests**

Run: `cd NSI && .venv/bin/python -m pytest tests/test_verify_python.py tests/test_gates_corpus.py -q`
Expected: PASS

- [ ] **Step 3: Build the manual**

Run: `cd NSI && .venv/bin/python scripts/assemble.py --book 1NSI`
Expected: PDF created at `build/books/MANUEL_1NSI_v1.pdf`

- [ ] **Step 4: Validate the artifact**

Run: `cd NSI && .venv/bin/python -c "from pathlib import Path; from pdf_integrity import verify_pdf; raise SystemExit(verify_pdf(Path('build/books/MANUEL_1NSI_v1.pdf'), Path('build/books/MANUEL_1NSI_v1.log')))"` with `PYTHONPATH=scripts`
Expected: exit code `0`

- [ ] **Step 5: Commit**

```bash
git add NSI/scripts/assemble.py NSI/Makefile NSI/gabarits/book_master.tex NSI/manifests/books/1NSI.json NSI/tests/test_assemble_book.py
git commit -m "[1NSI][ASSEMBLAGE] produit le manuel Premiere NSI"
```

Plan complete and saved to `docs/superpowers/plans/2026-08-08-assemblage-manuel-1nsi.md`. Ready to execute.
