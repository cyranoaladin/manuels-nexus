# Build Producer Registry Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the hard-coded build-producer integration debt with a fail-closed, versioned registry cross-checked against declared manual assemblies and observed build receipts.

**Architecture:** Add one schema-validated YAML control listing only producers for currently declared manual assemblies. Derive integration from the exact equality of required and registered assembly IDs, the assembler recorded by static analysis, the canonical recorder path, and valid observed builds. Because the new control changes the static source digest, invalidate the old observed manifest and re-attest professor then student PDFs through the existing reproducible assembler.

**Tech Stack:** Python 3.12, pytest, JSON Schema Draft 2020-12, YAML, LuaLaTeX `-recorder`, Poppler preflight, Git.

---

## Chunk 1: Versioned producer control

### Task 1: Specify schema registration and fail-closed loading

**Files:**
- Modify: `tests/test_inventory_collection.py`
- Modify: `scripts/inventory_collection.py`
- Create: `audit/schemas/v1/build-producers.schema.json`
- Create: `audit/BUILD_PRODUCERS.yaml`

- [ ] **Step 1: Write the RED schema registration test**

Extend the schema parameter list with `build-producers.schema.json` and assert:

```python
assert inventory_module._schema_ref_for("build_producers", 1) == (
    "audit/schemas/v1/build-producers.schema.json"
)
```

- [ ] **Step 2: Run the schema tests and verify RED**

Run:

```bash
python -m pytest tests/test_inventory_collection.py \
  -q -k 'v1_json_schemas or schema_directory or build_producers'
```

Expected: FAIL because `build_producers` and its schema do not exist.

- [ ] **Step 3: Add the minimal Draft 2020-12 schema and registry entry**

The schema must set `additionalProperties: false` at every object level and
require:

```text
artifact_type = build_producers
schema_version = 1
schema_ref = audit/schemas/v1/build-producers.schema.json
control_digest = sha256:...
producers = non-empty unique producer objects
```

Each producer requires `producer_id`, `assembler`, `recorder` and a non-empty,
unique `assembly_ids` list. Paths must be canonical repository-relative POSIX
paths and producer IDs must match `^[a-z0-9]+(?:-[a-z0-9]+)*$`.

Register the schema in `SCHEMA_REGISTRY` and add:

```python
BUILD_PRODUCERS_FILE = "audit/BUILD_PRODUCERS.yaml"
CANONICAL_BUILD_RECORDER = "scripts/build_manifest.py"
```

- [ ] **Step 4: Write RED loader tests**

Add focused tests for:

- valid canonical payload;
- bad `control_digest`;
- duplicate producer ID;
- duplicate assembly coverage across producers;
- absolute/traversing assembler path;
- symlink, missing, non-regular or untracked assembler;
- non-canonical recorder;
- non-canonical producer ordering and assembly ordering.

The wished-for API is:

```python
producers = inventory_module._load_build_producers(repository)
```

- [ ] **Step 5: Run the loader tests and verify RED**

Run:

```bash
python -m pytest tests/test_inventory_collection.py \
  -q -k 'build_producer'
```

Expected: FAIL because `_load_build_producers` is absent.

- [ ] **Step 6: Implement the minimal loader**

Reuse `_load_control_yaml_payload()`, `_validate_control_payload()` and Git's
tracked-file set. Validate paths lexically before any filesystem access, refuse
symlinks/non-regular files, and return canonical producer dictionaries sorted
by `producer_id`.

- [ ] **Step 7: Materialize the canonical control**

Create the single current producer:

```yaml
producer_id: math-1spe-manual
assembler: Mathematiques/manuel-maths/scripts/assemble_manuel.py
recorder: scripts/build_manifest.py
assembly_ids:
  - math:manual:1SPE:eleve
  - math:manual:1SPE:professeur
```

Calculate `control_digest` with the production `_control_digest()` helper; do
not hand-edit the digest after validation.

- [ ] **Step 8: Verify GREEN for schema and loader**

Run:

```bash
python -m pytest tests/test_inventory_collection.py \
  -q -k 'v1_json_schemas or schema_directory or build_producer'
python -m ruff check scripts/inventory_collection.py \
  tests/test_inventory_collection.py
```

Expected: PASS.

## Chunk 2: Derived integration state

### Task 2: Replace the hard-coded sentinel with evidence

**Files:**
- Modify: `tests/test_build_manifest.py`
- Modify: `tests/test_inventory_collection.py`
- Modify: `scripts/inventory_collection.py`
- Modify: `audit/schemas/v1/inventory-collection.schema.json`

- [ ] **Step 1: Write RED unit tests for the integration calculation**

Define a wished-for pure function:

```python
result = inventory_module._observed_build_integration(
    declared_assemblies,
    observed_builds,
    producers,
)
```

Assert the complete 1SPE fixture yields:

```python
assert result["status"] == "integrated"
assert result["required_producers"] == ["math-1spe-manual"]
assert result["integrated_producers"] == ["math-1spe-manual"]
assert result["missing_assembly_ids"] == []
assert result["unobserved_assembly_ids"] == []
assert result["unexpected_assembly_ids"] == []
```

Also require `not_integrated` for a missing student observation, missing
registry coverage, unknown registry assembly, duplicate coverage, or assembler
mismatch.

- [ ] **Step 2: Run the integration tests and verify RED**

Run:

```bash
python -m pytest tests/test_build_manifest.py \
  -q -k 'observed_build_integration or producer'
```

Expected: FAIL because the current value is a hard-coded two-field mapping.

- [ ] **Step 3: Implement the pure integration calculation**

Derive observed assembly IDs from exact `(manual, variant)` matches against
declared manual assemblies. Never infer variants from filenames. Return sorted
diagnostic lists and compute `status` from empty diagnostic lists plus complete
producer observation.

- [ ] **Step 4: Wire the loader and calculation into `_build_inventory()`**

Load producers before observed integration and replace:

```python
{"entrypoint": "...", "status": "not_integrated"}
```

with the pure derived payload. Extend the inventory schema to validate the
detailed result with no additional properties.

- [ ] **Step 5: Update the release-gate regression tests**

Assert:

- complete evidence removes `build_receipt_producteurs_non_intégrés`;
- any incomplete producer evidence retains it;
- other release reasons and uncovered dimensions remain unchanged;
- no test turns `release-strict` into success for the real repository.

- [ ] **Step 6: Verify GREEN and mutation resistance**

Run:

```bash
python -m pytest tests/test_build_manifest.py tests/test_inventory_collection.py \
  -q -k 'observed_build_integration or producer or release_execution'
```

Then temporarily mutate one fixture assembler or omit one observation and prove
the focused test fails before restoring the fixture through `apply_patch`.

## Chunk 3: CI contract and migration

### Task 3: Update the Phase 0 CI contract without weakening release strictness

**Files:**
- Modify: `tests/test_ci_audit_collection.py`
- Modify: `scripts/ci_audit_collection.py`
- Modify: `docs/codex/CI_AUDIT_PHASE_0.md`

- [ ] **Step 1: Write RED CI-contract tests**

Replace the historical requirement that the generic producer debt be present
with requirements that:

- `observed_build_integration.status == integrated` in the generated inventory;
- the generic producer debt is absent for the real repository;
- `release-strict` still returns exactly `7` with real non-producer debts;
- output remains deterministic across the repeated release run.

- [ ] **Step 2: Run and verify RED**

```bash
python -m pytest tests/test_ci_audit_collection.py -q -k 'release or producer'
```

Expected: FAIL against the old CI assertion.

- [ ] **Step 3: Implement the minimal CI contract change**

Read and validate the generated inventory proof; do not merely delete the old
assertion. Keep requirements for integration debt, 1SPE debt, deterministic
reasons and uncovered release dimensions.

- [ ] **Step 4: Verify focused CI tests GREEN**

```bash
python -m pytest tests/test_ci_audit_collection.py -q
python -m ruff check scripts/ci_audit_collection.py \
  tests/test_ci_audit_collection.py
```

Expected: PASS.

### Task 4: Invalidate stale observed builds and regenerate Phase 0 artifacts

**Files:**
- Modify: `audit/BUILD_MANIFEST.json`
- Modify generated inventory/report artifacts

- [ ] **Step 1: Prove the old manifest is rejected after the registry change**

Run `--validate-model` and confirm the expected `source_digest` or
`model_digest` mismatch. Do not add a compatibility bypass.

- [ ] **Step 2: Replace only the observed builds with a valid empty envelope**

Use the existing controlled empty-manifest refresh path. Keep schema,
provenance and state digest valid; do not edit generated reports manually.

- [ ] **Step 3: Regenerate the six managed artifacts**

```bash
python scripts/inventory_collection.py
python scripts/inventory_collection.py --check
python scripts/inventory_collection.py --validate-model
python scripts/inventory_collection.py --fail-on-new
```

Expected: all non-release gates return `0`; `release-strict` remains `7` and
temporarily reports missing observed 1SPE variants.

- [ ] **Step 4: Commit the registry implementation atomically**

```bash
git diff --check
git status --short
git add scripts tests audit docs/codex
git commit -m "[AUDIT] dérive l intégration des producteurs de builds"
```

Do not stage any visual baseline path.

## Chunk 4: Re-attestation of observed PDFs

### Task 5: Re-attest the professor variant

**Files:**
- Modify: `Mathematiques/manuel-maths/config/reproducible-build.json`
- Modify if reproducibly changed: professor PDF
- Modify: `audit/BUILD_MANIFEST.json`

- [ ] Fix the reproducibility epoch to the committed registry source state and
commit that configuration alone.
- [ ] Build the professor variant normally and record its SHA/page count.
- [ ] Version the PDF only if bytes changed, in a `[PDF]` commit.
- [ ] Rebuild with `--record-observed`; require recorder exit `0`, preflight
success, `-recorder` evidence and byte identity with the versioned PDF.
- [ ] Commit only the professor receipt/manifest update as `[AUDIT]`.

### Task 6: Re-attest the student variant

**Files:**
- Modify if reproducibly changed: student PDF
- Modify: `audit/BUILD_MANIFEST.json`

- [ ] Build the student variant normally and record its SHA/page count.
- [ ] Prove the student-separation gate passes and no professor object leaks.
- [ ] Version the PDF only if bytes changed, in a `[PDF]` commit.
- [ ] Rebuild with `--record-observed`; require byte identity and recorder exit
`0`.
- [ ] Commit only the student receipt/manifest update as `[AUDIT]`.

### Task 7: Regenerate and verify the final inventory

**Files:**
- Modify generated audit artifacts

- [ ] Regenerate all inventory artifacts from the two valid observed builds.
- [ ] Assert `observed_build_integration.status == integrated`.
- [ ] Assert `build_receipt_producteurs_non_intégrés` is absent and the real
`release-strict` reason count decreases without any baseline update.
- [ ] Commit the generated attestation separately as `[AUDIT]`.

## Chunk 5: Full verification and remote evidence

### Task 8: Run the complete quality suite

- [ ] Run focused tests for inventory, manifests and CI.
- [ ] Run the complete pytest suite with the CI import mode and coverage.
- [ ] Run Ruff, mypy and structured-data parsing.
- [ ] Run the five Phase 0 gates with exact contractual codes.
- [ ] Run double generation and byte comparison.
- [ ] Run PDF preflight for both variants.
- [ ] Verify `git diff --check` and a clean worktree.
- [ ] Prove no path under visual baselines, validation PNGs or visual review
directories changed relative to the starting SHA `b4b7354`.

### Task 9: Push and inspect CI

- [ ] Push `finalisation/collection-v1` non-forced.
- [ ] Confirm the new branch SHA on `origin`.
- [ ] Watch both Phase 0 audits plus Mathématiques and NSI checks.
- [ ] Inspect the canonical push artifact and record the new reason count.
- [ ] Keep `release_acceptance=false` and the manual `NO-GO`.
