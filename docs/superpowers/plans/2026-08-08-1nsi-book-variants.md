# 1NSI Book Variants Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** permettre à `NSI/scripts/assemble.py --book 1NSI --variant ...` d'assembler les variantes `complet`, `remediation`, `methodes` et `amenagee` en incluant seulement les chapitres réellement alimentés.

**Architecture:** conserver la collecte variant-aware du mode chapitre et ajouter une collecte livre élève dédiée. Le manifeste `1NSI` reste unique ; `complet` prend les objets élève des 10 chapitres mais exclut corrigés, évaluations barémées, remédiations corrigées et chemins professeur. Le master force le mode élève et neutralise les corps `corrige` sans supprimer leurs sources.

**Tech Stack:** Python 3.11, pytest, LuaLaTeX, gabarits Nexus, `verify_pdf`.

**Statut au 2026-08-08 :** les quatre variantes 1NSI sont implémentées et validées. Ce
statut ne couvre ni TNSI ni une release globale de la collection.

---

## Chunk 1: Tests rouges de sélection variant-aware

### Task 1: Figer la résolution des chapitres par variante

**Files:**
- Modify: `NSI/tests/test_assemble_book.py`
- Modify: `NSI/scripts/assemble.py`

- [x] **Step 1: Write the failing test**

```python
def test_collect_book_chapters_methodes_1nsi():
    chapters = assemble.collect_book_chapters("1NSI", "methodes")
    assert [path.name for path in chapters] == ["1NSI-TYPES-CONSTRUITS"]
```

- [x] **Step 2: Run test to verify it fails**

Run: `cd NSI && python3 -m pytest tests/test_assemble_book.py -q`
Expected: FAIL because `collect_book_chapters` does not accept the variant logic yet.

- [x] **Step 3: Write minimal implementation**

```python
def collect_book_chapters(book_id: str, variant: str = "complet") -> list[Path]:
    ...
```

- [x] **Step 4: Run test to verify it passes**

Run: `cd NSI && python3 -m pytest tests/test_assemble_book.py -q`
Expected: PASS for variant-aware chapter selection.

- [x] **Step 5: Commit**

```bash
git add NSI/tests/test_assemble_book.py NSI/scripts/assemble.py
git commit -m "[1NSI][ASSEMBLAGE] fige la selection des chapitres par variante"
```

### Task 2: Figer l'échec sur variante vide

**Files:**
- Modify: `NSI/tests/test_assemble_book.py`
- Modify: `NSI/scripts/assemble.py`

- [x] **Step 1: Write the failing test**

```python
def test_build_book_rejects_chapter_only_variants():
    with pytest.raises(ValueError, match="Variante de livre non prise en charge"):
        assemble.build_book("1NSI", "professeur")
```

- [x] **Step 2: Run test to verify it fails**

Run: `cd NSI && python3 -m pytest tests/test_assemble_book.py -q`
Expected: FAIL because the mode livre does not yet reject chapter-only variants before loading the manifest.

- [x] **Step 3: Write minimal implementation**

```python
if variant not in BOOK_VARIANTS:
    raise ValueError(...)
```

- [x] **Step 4: Run test to verify it passes**

Run: `cd NSI && python3 -m pytest tests/test_assemble_book.py -q`
Expected: PASS with explicit rejection of `professeur` and `parcours1` in book mode; chapter mode remains unchanged.

- [x] **Step 5: Commit**

```bash
git add NSI/tests/test_assemble_book.py NSI/scripts/assemble.py
git commit -m "[1NSI][ASSEMBLAGE] refuse les variantes de livre vides"
```

## Chunk 2: Implémentation de l’assemblage variant-aware

### Task 3: Rendre `render_book_master` sensible au variant

**Files:**
- Modify: `NSI/scripts/assemble.py`
- Modify: `NSI/tests/test_assemble_book.py`

- [x] **Step 1: Write the failing test**

```python
def test_render_book_master_methodes_contains_one_chapter():
    tex = assemble.render_book_master("1NSI", "methodes")
    assert tex.count("\\chapter{") == 1
    assert "1NSI-TYPES-CONSTRUITS" in tex
```

- [x] **Step 2: Run test to verify it fails**

Run: `cd NSI && python3 -m pytest tests/test_assemble_book.py -q`
Expected: FAIL because `render_book_master` still assumes `complet`.

- [x] **Step 3: Write minimal implementation**

```python
def render_book_master(book_id: str, variant: str = "complet") -> str:
    ...
```

- [x] **Step 4: Run test to verify it passes**

Run: `cd NSI && python3 -m pytest tests/test_assemble_book.py -q`
Expected: PASS.

- [x] **Step 5: Commit**

```bash
git add NSI/scripts/assemble.py NSI/tests/test_assemble_book.py
git commit -m "[1NSI][ASSEMBLAGE] rend le master livre sensible aux variantes"
```

### Task 4: Exposer la variante livre dans `Makefile`

**Files:**
- Modify: `NSI/Makefile`

- [x] **Step 1: Write the failing test**

No code test; verify via command behavior.

- [x] **Step 2: Run command to verify current limitation**

Run: `cd NSI && make book VARIANT=methodes`
Expected: build still uses the default book behavior or ignores `VARIANT`.

- [x] **Step 3: Write minimal implementation**

```make
VARIANT ?= complet
book:
	$(PY) scripts/assemble.py --book 1NSI --variant $(VARIANT)
```

- [x] **Step 4: Run command to verify it passes**

Run: `cd NSI && make book VARIANT=methodes`
Expected: methodes book is built.

- [x] **Step 5: Commit**

```bash
git add NSI/Makefile
git commit -m "[1NSI][ASSEMBLAGE] expose la variante du mode livre"
```

## Chunk 3: Vérification réelle

### Task 5: Vérifier tests et builds réels

**Files:**
- Read/verify: `NSI/build/books/*.pdf`
- Read/verify: `NSI/build/books/*.log`

- [x] **Step 1: Run focused tests**

Run: `cd NSI && python3 -m pytest tests/test_assemble_book.py -q`
Expected: PASS

- [x] **Step 2: Run regression-adjacent tests**

Run: `cd NSI && python3 -m pytest tests/test_verify_python.py tests/test_gates_corpus.py -q`
Expected: PASS

- [x] **Step 3: Build the four 1NSI variants**

Run:
- `cd NSI && python3 scripts/assemble.py --book 1NSI --variant complet`
- `cd NSI && python3 scripts/assemble.py --book 1NSI --variant remediation`
- `cd NSI && python3 scripts/assemble.py --book 1NSI --variant methodes`
- `cd NSI && python3 scripts/assemble.py --book 1NSI --variant amenagee`

Expected: four PDFs generated, with partial books for `methodes` and `amenagee`.

- [x] **Step 4: Validate the artifacts**

Run `verify_pdf` on each generated PDF under `NSI/build/books/`.
Expected: exit code `0` for each, no fatal/Overfull/Underfull log entry, and `pdftotext` exposes neither `Corrigé`, `Barème indicatif` nor identifiant `1NSI-*`.
Each PDF must also expose non-empty Title, Author, Subject and Keywords metadata. Its
outline must be non-empty.

Safe `lstinline|...|` delimiters for mapping literals are required in every source selected
by the four student-book variants. Unselected professor and evaluation sources remain out
of scope.

- [x] **Step 5: Commit**

```bash
git add NSI/scripts/assemble.py NSI/Makefile NSI/tests/test_assemble_book.py docs/superpowers/specs/2026-08-08-1nsi-book-variants-design.md docs/superpowers/plans/2026-08-08-1nsi-book-variants.md
git commit -m "[1NSI][ASSEMBLAGE] generalise le mode livre aux declinaisons"
```
