---
name: nexus-manual-quality
description: Use for auditing, correcting, compiling, validating, reviewing, or releasing Nexus Réussite school manuals, especially the Mathématiques Première spécialité 2026-2027 manual. Trigger on manual, LaTeX, curriculum compliance, mathematical review, student/teacher variants, PDF preflight, educational design, Chutes expert review, or release-quality work. Do not use for unrelated software tasks.
---

# Nexus Manual Quality

## Required context

1. Read the applicable `AGENTS.md`.
2. Read `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md` for Mathématiques Première.
3. Read current files under `audit/` and `docs/codex/`.
4. Inspect Git status and preserve WIP.

## Workflow

### 1. Establish the state

Run:

```bash
git status --short --branch
git rev-parse HEAD
git log --oneline --decorate -15
git diff --stat
git diff --check
```

Record:

- branch;
- HEAD;
- dirty files;
- applicable instruction files;
- current phase;
- known red gates.

### 2. Classify the task

Choose one primary lane:

- mathematical correctness;
- curriculum compliance;
- pedagogy;
- Python;
- LaTeX/layout;
- student/teacher separation;
- PDF/preflight;
- inventory/CI;
- release governance.

Do not mix unrelated lanes in one commit.

### 3. Consult official evidence

For curriculum or exam claims:

- use official French education sources;
- record URL, date, effective year and digest;
- update the programme matrix;
- distinguish mandatory, optional enrichment and out-of-scope content.

### 4. Use Chutes when available

- smoke-test the MCP;
- use only listed models;
- consult an independent relevant expert;
- do not transmit secrets or personal data;
- verify recommendations locally;
- save a compact report in `audit/chutes/`.

### 5. Reproduce before fixing

For every defect:

- reproduce it;
- locate all occurrences;
- assign severity;
- identify cause;
- define expected behavior;
- write or plan a regression test.

### 6. Implement minimally

- preserve identifiers and history;
- change the smallest coherent surface;
- avoid silent migrations;
- avoid weakening gates;
- keep student and teacher objects distinct;
- keep internal IDs out of student rendering.

### 7. Validate

Use the relevant checks:

- SymPy and numerical assertions;
- Python parse, execution and output comparison;
- schema and reference validation;
- student/teacher inclusion diff;
- LaTeX compile and log classification;
- full-page rendering and visual review;
- PDF metadata, links, bookmarks and fonts;
- curriculum matrix coverage;
- baseline comparison.

### 8. Adversarial review

Try to break the change:

- mutate a sign or answer;
- insert a correction into the student variant;
- introduce a broken reference;
- use a long title;
- overflow a marginal note;
- use typographic quotes in Python;
- rebuild twice.

The gate should fail for the injected defect.

### 9. Commit atomically

Before commit:

```bash
git diff --check
git status --short
git diff --stat
```

Use a scoped prefix such as `[MATH]`, `[PROGRAMME]`, `[LATEX]`, `[PYTHON]`, `[TESTS]`, or `[CI]`.

### 10. Report

Return:

```text
ÉTAT <SHA>
Branche :
Lane :
Defects fixed :
Tests :
Gates :
Remaining P0 :
Human decisions :
PR :
Next atomic action :
```

## Stop conditions

Stop and report instead of proceeding when:

- a destructive Git action would be required;
- official sources conflict or are unclear;
- a critical mathematical decision lacks independent review;
- WIP provenance is unknown;
- a baseline update lacks human approval;
- release claims cannot be proved.

## Release rule

A known or baselined anomaly can still block release. `--fail-on-new` controls regression; `--release-strict` controls publishability.
