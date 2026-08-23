# Programme 333/333 and QCM 330/330 Closure Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the official-program mapping and independently validate every Math QCM on the current integration base while preserving all T1 structural invariants.

**Architecture:** Keep official programme atoms independent from internal capacities, then map in both directions. Reclassify good future-programme material as explicit optional extension without allowing it into mandatory diagnostics, QCM or assessments. Treat JSON as canonical QCM source, regenerate TeX, and require independent solution evidence plus causal diagnostics for all 330 questions.

**Tech Stack:** Python 3.12, pytest, JSON/YAML, LaTeX, SymPy where appropriate, canonical Nexus inventory/gates.

---

## Chunk 1: Current-head programme reconciliation

### Task 1: Revalidate the accepted side-car against integration HEAD

**Files:**
- Read: `audit/CODEX_HANDOFF_CURRENT_HEAD.md`
- Read: `audit/OFFICIAL_PROGRAM_ATOMS_2026_2027.json`
- Read: `audit/QCM_SCIENTIFIC_ANSWER_KEY_AUDIT.json`

- [ ] Resolve `audit/adversarial-reconciliation-2026` and compare it with the side-car base.
- [ ] Revalidate source/test commits only; exclude PDFs, manifests and generated inventories from authority.
- [ ] Record the integration base and preserve a clean dedicated branch.

### Task 2: Reclassify 1SPE trigonometry C3/C4/C5

**Files:**
- Modify: `Mathematiques/manuel-maths/referentiel/capacites_1SPE_TRIGONOMETRIE.json`
- Modify: `Mathematiques/manuel-maths/chapitres/1SPE-TRIGONOMETRIE/contrat.yaml`
- Modify: affected course/method/exercise/QCM/evaluation/remediation metadata
- Test: targeted programme-scope tests under `tests/` or `Mathematiques/manuel-maths/tests/`

- [ ] Inventory every C3/C4/C5 consumer and write a failing scope-classification test.
- [ ] Verify the test fails because future Terminale content is still mandatory/unlabelled.
- [ ] Keep C1/C2 canonical and reclassify good C3/C4/C5 resources as `OPTIONAL_EXTENSION` labelled “Approfondissement — Vers la Terminale”.
- [ ] Remove optional resources from mandatory diagnostic, assessment, QCM and remediation coverage.
- [ ] Regenerate derived artifacts and run targeted tests.
- [ ] Commit `[PROGRAMME] Reclasser les approfondissements trigonométriques 1SPE`.

### Task 3: Reclassify the named binomial law in 1SPE

**Files:**
- Modify: `Mathematiques/manuel-maths/referentiel/capacites_1SPE_VARIABLES_ALEATOIRES.json`
- Modify: `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/contrat.yaml`
- Modify: affected course/method/exercise/QCM/evaluation/remediation metadata
- Test: targeted programme-scope tests

- [ ] Inventory every named-binomial consumer and write a failing scope-classification test.
- [ ] Preserve mandatory Bernoulli repetition, trees, success counts and random-variable moments without naming a mandatory binomial law.
- [ ] Reclassify sound formal binomial-law resources as `OPTIONAL_EXTENSION` labelled “Vers la Terminale — formalisation par la loi binomiale”.
- [ ] Exclude optional binomial formalism from mandatory QCM, assessments and FULL criteria.
- [ ] Run targeted tests and commit a separate `[PROGRAMME]` change.

### Task 4: Close the two mandatory unmapped atoms

**Files:**
- Create: `audit/MANDATORY_UNMAPPED_ATOMS_CLOSURE.json`
- Create: `audit/MANDATORY_UNMAPPED_ATOMS_CLOSURE.md`
- Modify: exact affected contract/content/mapping files discovered by the audit
- Test: `tests/test_mandatory_unmapped_atoms_closure.py`

- [ ] Write a failing test requiring exact identification and non-UNKNOWN gap classification for both atoms.
- [ ] Determine whether each is content, contract, mapping or chapter-scope debt.
- [ ] Implement the smallest scientifically sufficient correction.
- [ ] Require `MANDATORY_MAPPED=333/333` without assigning FULL.
- [ ] Run schema, programme and inventory-targeted checks; commit atomically.

## Chunk 2: Official-source completeness and bidirectional scope

### Task 5: Audit source segments against atoms

**Files:**
- Create: `audit/OFFICIAL_SOURCE_SEGMENTS_2026_2027.json`
- Create: `audit/OFFICIAL_SOURCE_SEGMENTS_2026_2027.md`
- Create/modify: a deterministic builder under `scripts/`
- Test: dedicated currentness/completeness test under `tests/`

- [ ] Define a deterministic official-segment schema covering contents, capacities, mandatory demonstrations, algorithms, limitations, automatismes and transversal competencies.
- [ ] Write failing tests for zero unparsed mandatory segments, duplicate atoms, ambiguous atoms and wrong-year atoms.
- [ ] Extract all six official documents directly and map each segment to one or more stable atoms.
- [ ] Resolve every failure without using internal capacities as source authority.
- [ ] Commit the completed source-segment ledger and tests.

### Task 6: Audit manual-to-programme direction

**Files:**
- Create: `audit/MANUAL_TO_PROGRAMME_CLASSIFICATION_2026_2027.json`
- Create: `audit/MANUAL_TO_PROGRAMME_CLASSIFICATION_2026_2027.md`
- Test: dedicated classification/currentness tests

- [ ] Classify every significant manual object as mandatory programme, prerequisite, optional extension, exam preparation, cultural/history, methodology or other explicit.
- [ ] Write a failing test requiring `UNJUSTIFIED_OUT_OF_PROGRAM_CONTENT=0` and exact source digests.
- [ ] Resolve classifications, prioritising 1SPE future-programme material.
- [ ] Commit without promoting review status.

## Chunk 3: Independent QCM closure

### Task 7: Recompute all 330 Math QCM

**Files:**
- Modify: all affected `Mathematiques/manuel-maths/chapitres/*/qcm/*-QCM.json`
- Regenerate: corresponding `*-QCM.tex`
- Modify: `audit/QCM_SCIENTIFIC_ANSWER_KEY_AUDIT.json`
- Modify: `audit/QCM_SCIENTIFIC_ANSWER_KEY_AUDIT.md`
- Test: QCM scientific audit and source-uniqueness tests

- [ ] Partition pending questions by manual/chapter and independently solve each one.
- [ ] For every detected defect, first write a failing regression test reproducing the wrong key, ambiguity, absent answer, wrong capacity/year or diagnostic mismatch.
- [ ] Correct the canonical JSON minimally, regenerate TeX and verify the new test.
- [ ] Replace or justify every generic diagnostic with a causal error explanation.
- [ ] Record statement, options, solution, uniqueness, diagnostics, difficulty, programme alignment and variant visibility for all 330.
- [ ] Require all eight critical QCM counters to equal zero.
- [ ] Run the QCM milestone suite and commit by coherent chapter/manual batches.

## Chunk 4: Early science/pedagogy and milestone gates

### Task 8: Start chapter-level science and pedagogy reviews

**Files:**
- Create or update current-SHA review ledgers under `audit/`
- No status promotion without the required independent/human receipt

- [ ] Start with 1SPE trigonométrie and variables aléatoires, then high-density QCM chapters.
- [ ] Record scientific and pedagogical findings separately.
- [ ] Invalidate any receipt whose source SHA no longer matches.

### Task 9: Preserve invariants and issue the milestone handoff

**Files:**
- Update: `audit/CODEX_HANDOFF_CURRENT_HEAD.md`
- Regenerate only current-tree audit artifacts required by canonical procedures

- [ ] Run targeted tests throughout; defer large suites until `PROGRAMME_333_333` and `QCM_330_330` are both achieved.
- [ ] Require all T1 structural counts to remain zero after every source batch.
- [ ] Run currentness/schema, `validate-model` and `fail-on-new` at the milestone.
- [ ] Report FULL honestly, with no alias from path existence.
- [ ] Stop at the requested checkpoint or immediately on a new scientific/regulatory P0.
