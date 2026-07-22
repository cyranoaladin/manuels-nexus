# Phase 0.1 Collection Audit Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore the 73 historical tests, then deliver validated and reproducible Phase 0.1 audit artifacts, gates, debt controls, build evidence, and CI.

**Architecture:** Preserve `scripts/inventory_collection.py` as the public orchestration module and `scripts/inventory_graph.py` as its graph helper until contracts stabilize. Add versioned data contracts under `audit/schemas/v1/`, keep raw anomalies separate from dispositions and baseline, and make all writes a validated repository-confined transaction.

**Tech Stack:** Python 3.12, pytest, PyYAML, jsonschema, Ruff, mypy, pytest-cov/coverage, Git, GitHub Actions.

---

## Chunk 1: Historical recovery and machine contracts

### Task 0: Verify the mandatory recovery preflight without writing code

**Files:**
- Verify: `audit/PHASE_0_1_REPRISE_WIP.md`
- Verify: `audit/chutes/2026-07-22-wip-independent-review.md`
- Verify: `scripts/inventory_collection.py`

- [ ] **Step 1: Verify the 36-test inventory and grouping**

Run: `rg -n '^([0-9]+\.|#### Groupe|### Cause racine)' audit/PHASE_0_1_REPRISE_WIP.md`
Expected: four groups, numbered tests 1 through 36, and the responsible
classification changes.

- [ ] **Step 2: Verify independent Chutes evidence and local decisions**

Run: `test -s audit/chutes/2026-07-22-wip-independent-review.md`
Expected: exit 0; the file records Chutes conclusions, local reproduction,
retained recommendations and the rejected fixture workaround.

- [ ] **Step 3: Reproduce the root cause locally**

Run: `python -c "from pathlib import Path; import scripts.inventory_collection as m; print(m._collect_role_patterns(Path('.'))[:3])"`
Expected before correction: empty role patterns and order.

- [ ] **Step 4: Verify the worktree before the first RED test**

Run: `git diff --check`
Expected: no output.

Run: `git status --short --branch`
Expected: the two inherited Python modifications plus reviewed audit/design/plan
files; no staged file.

### Task 1: Restore the historical WIP behavior

**Files:**
- Modify: `scripts/inventory_collection.py:130-230,1334-1361,1716-1730,2828-3435`
- Modify: `scripts/inventory_graph.py:288-331`
- Modify: `tests/test_inventory_collection.py`
- Update: `audit/PHASE_0_1_REPRISE_WIP.md`
- Update: `audit/chutes/2026-07-22-wip-independent-review.md`
- Create: `docs/superpowers/specs/2026-07-22-phase-0-1-collection-audit-design.md`
- Create: `docs/superpowers/plans/2026-07-22-phase-0-1-collection-audit.md`

- [ ] **Step 1: Add a focused fallback regression test**

```python
def test_source_roles_fall_back_when_configuration_is_absent(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    sources = {
        f"{base}/contrat.yaml": _contract("1SPE-TEST", "1SPE", capacities=1),
        f"{base}/cours/c1.tex": _meta(status="approved"),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)

    assert list(inventory["manuals"]["1SPE"]["chapters"]) == ["1SPE-TEST"]
```

- [ ] **Step 2: Run the focused test and verify RED**

Run: `pytest -q tests/test_inventory_collection.py::test_source_roles_fall_back_when_configuration_is_absent`
Expected: FAIL because the chapter list is empty.

- [ ] **Step 3: Implement one canonical fallback constant**

Move the built-in role patterns/order to immutable constants. Return them when
the roles file is absent, loads as `None`, is empty, or lacks usable roles. Do
not add configuration files to historical fixtures.

- [ ] **Step 4: Run focused then historical tests**

Run: `pytest -q tests/test_inventory_collection.py::test_source_roles_fall_back_when_configuration_is_absent`
Expected: PASS.

Run: `pytest -q tests/test_inventory_collection.py`
Expected: remaining failures reveal only masked WIP regressions.

- [ ] **Step 5: Add and observe RED for raw anomaly immutability**

Add `test_build_inventory_keeps_raw_anomalies_unqualified`, using one missing
META file and asserting its raw mapping contains only the detector's `path` and
`reason`, never derived `source`, `fingerprint`, `disposition` or `blocking`.

Run: `pytest -q tests/test_inventory_collection.py::test_build_inventory_keeps_raw_anomalies_unqualified`
Expected: FAIL because the WIP adds `source` in place.

- [ ] **Step 6: Stop mutating raw anomalies and verify GREEN**

Remove only the post-analysis `setdefault("source", ...)` mutation. Derived
qualification will later receive a separate structure.

Run the focused test. Expected: PASS.

- [ ] **Step 7: Add and observe RED for renderer compatibility**

Add `test_build_inventory_artifacts_renders_markdown_without_parsing_it_as_yaml`.
Create a valid temporary Git repository, invoke `build_inventory_artifacts`,
assert all expected paths exist and parse only `.json/.yaml` as structured data.

Run the focused test. Expected: FAIL with an unexpected `marker` keyword before
any output replacement.

- [ ] **Step 8: Align renderer interfaces and verify GREEN**

Add explicit optional `marker`/`root` parameters to the renderer definitions,
use the passed marker, and validate Markdown only as non-empty UTF-8 text. Do not
change report content yet.

Run the focused test. Expected: PASS.

- [ ] **Step 9: Add and observe RED for metadata-error orphan policy**

Add `test_metadata_errors_are_not_duplicated_as_orphan_files` with one absent
META, one malformed META and one valid unreachable TeX file. Assert both metadata
errors are absent from `orphan_files` and the valid unreachable file remains.

Run the focused test. Expected: FAIL because only `MetadataMissingError` enters
`metadata_error_paths`.

- [ ] **Step 10: Make the skip policy symmetric and verify GREEN**

Add every caught `MetadataError` path to the skip set and rename the graph helper
argument `skipped_paths`. Run the focused test. Expected: PASS.

- [ ] **Step 11: Verify the exact historical and expanded gates**

Run the untouched HEAD snapshot suite already recorded in the audit. Expected:
`73 passed`.

Run: `pytest -q tests/test_inventory_collection.py`
Expected: the 73 historical cases plus the parameterized regression cases pass.

Run: `ruff check scripts/inventory_collection.py scripts/inventory_graph.py tests/test_inventory_collection.py`
Expected: no findings.

Run: `git diff --check`
Expected: no output.

- [ ] **Step 12: Commit the recovery**

Run: `git status --short` and confirm only reviewed recovery/audit files.
Run: `git add scripts/inventory_collection.py scripts/inventory_graph.py tests/test_inventory_collection.py audit/PHASE_0_1_REPRISE_WIP.md audit/chutes/2026-07-21-mcp-smoke-test.md audit/chutes/2026-07-22-wip-independent-review.md docs/superpowers/specs/2026-07-22-phase-0-1-collection-audit-design.md docs/superpowers/plans/2026-07-22-phase-0-1-collection-audit.md`
Run: `git commit -m "[AUDIT][P0.1] restaure les tests historiques du WIP"`

### Task 2: Stabilize formats and versioned schemas

**Files:**
- Modify: `scripts/inventory_collection.py`
- Modify: `tests/test_inventory_collection.py`
- Create: `audit/schemas/v1/inventory-collection.schema.json`
- Create: `audit/schemas/v1/ecarts-et-contradictions.schema.json`
- Create: `audit/schemas/v1/matrice-livrables.schema.json`
- Create: `audit/schemas/v1/source-roles.schema.json`
- Create: `audit/schemas/v1/anomaly-dispositions.schema.json`
- Create: `audit/schemas/v1/anomalies-baseline.schema.json`
- Create: `audit/schemas/v1/build-manifest.schema.json`
- Regenerate: `audit/INVENTAIRE_COLLECTION.json`
- Regenerate: `audit/ECARTS_ET_CONTRADICTIONS.yaml`
- Regenerate: `audit/MATRICE_LIVRABLES.yaml`

- [ ] **Step 1: Add RED parsing and missing-schema tests**

Add parameterized tests which load every generated YAML with `yaml.safe_load`,
every JSON with `json.loads`, validate the loaded payload against its declared
schema, reject an unknown schema version, and reject a missing schema.

- [ ] **Step 2: Add a RED shared-digest test**

Render the inventory JSON, discrepancies YAML and matrix YAML in memory and
assert identical `schema_version`, `source_digest`, `model_digest` and
`provenance` values.

- [ ] **Step 3: Create minimal versioned schemas**

Require this common output envelope in all three model artifacts:

```json
{
  "required": [
    "artifact_type", "schema_version", "schema_ref", "source_digest",
    "model_digest", "provenance"
  ],
  "properties": {
    "schema_version": {"const": 1},
    "source_digest": {"pattern": "^sha256:[0-9a-f]{64}$"},
    "model_digest": {"pattern": "^sha256:[0-9a-f]{64}$"},
    "provenance": {"type": "object"}
  }
}
```

Then require `manuals/anomalies` for inventory, `claims/anomalies/counts` for
discrepancies and `manuals` for the matrix. Control schemas require
`control_digest`; baseline/build schemas require referenced model/source digests.
Set `additionalProperties` deliberately per top-level object.

- [ ] **Step 4: Implement strict parsing and schema routing**

Route `.json` through `json.loads`, `.yaml/.yml` through `yaml.safe_load`, and
Markdown through UTF-8 text validation only. Treat schema absence as an error.
Use the valid `# generated by ...` YAML comment.

- [ ] **Step 5: Implement canonical model digest**

Build one `canonical_model_payload` containing source digest/files, manuals, raw
anomalies, graph, correction links, declared assemblies, PDFs, report
reconciliation, coherence checks and matrix. Exclude the complete envelope,
provenance, observed builds and every digest field. Serialize as compact UTF-8
JSON with sorted keys and semantic list order, hash once, then inject the result
into all three machine envelopes. Compute observed build state separately.

- [ ] **Step 6: Run tests and regenerate artifacts**

Run targeted schema tests, then `pytest -q tests/test_inventory_collection.py`.
Generate artifacts once, parse them independently, generate them again in a
temporary directory and compare the three machine files byte for byte.

- [ ] **Step 7: Commit formats and schemas**

Run `git diff --check`, `git status --short`, and targeted tests.
Run: `git add scripts/inventory_collection.py tests/test_inventory_collection.py audit/schemas/v1/inventory-collection.schema.json audit/schemas/v1/ecarts-et-contradictions.schema.json audit/schemas/v1/matrice-livrables.schema.json audit/schemas/v1/source-roles.schema.json audit/schemas/v1/anomaly-dispositions.schema.json audit/schemas/v1/anomalies-baseline.schema.json audit/schemas/v1/build-manifest.schema.json audit/INVENTAIRE_COLLECTION.json audit/ECARTS_ET_CONTRADICTIONS.yaml audit/MATRICE_LIVRABLES.yaml`
Run: `git commit -m "[AUDIT][P0.1] stabilise formats et schemas"`

## Chunk 2: Reports, gates, classification, and debt qualification

### Task 3: Make reports and counters reliable and expose CLI gates

**Files:**
- Modify: `scripts/inventory_collection.py`
- Modify: `tests/test_inventory_collection.py`
- Regenerate: `ETAT_COLLECTION.md`
- Regenerate: `audit/INVENTAIRE_COLLECTION.md`
- Regenerate: `audit/AUDIT_CONSOLIDE.md`

- [ ] **Step 1: Add RED object-count tests**

Build a chapter containing objects that contribute to overlapping metrics and
assert `object_count == len(objects)`, `content_file_count` is explicit and no
counter is computed from `sum(totals.values())`.

- [ ] **Step 2: Add RED human-renderer tests**

Assert no generated report contains `id=—, detail=—, code=—`; each anomaly row
uses its real non-null stable fields; `ETAT_COLLECTION.md` stays below the agreed
250-line limit and refers readers to machine artifacts for exhaustive lists.

- [ ] **Step 3: Add RED CLI contract tests**

Use subprocess tests for `--check`, `--validate-model`, `--release-strict`,
`--fail-on-new` and `--require-clean`. Assert documented exit codes and sorted,
machine-readable reasons. Assert exit codes `3/6/7/5/4` respectively, that
`--check` preserves pre/post SHA-256 of every output, and that a provisional or
missing baseline makes `--fail-on-new` fail with code 5. Cover a dirty tree,
unborn HEAD and detached HEAD for `--require-clean`. Assert all seven coverage
dimensions are exposed and uncovered dimensions are never green.

- [ ] **Step 4: Add RED blocker and eligibility tests**

Create a manual with an exercise lacking its correction and assert
`missing_corrections` is an active structural blocker,
`phase0_structural_eligible is False` and `publication_eligible is False`. Create
a structurally clean manual without pedagogical/visual/print proof and assert
`phase0_structural_eligible is True` while `publication_eligible is False`.

- [ ] **Step 5: Implement counter and renderer changes**

Use stored object counts, a deterministic anomaly field selector, summary tables
and bounded blocker samples. Keep exhaustive payloads only in JSON/YAML.

- [ ] **Step 6: Implement gate result plumbing**

Make each gate return a structured result consumed by both CLI output and
artifact rendering. Use `0` success, `2` usage, `3` check drift, `4` dirty tree,
`5` debt/baseline, `6` invalid model, `7` release blocked and `8` baseline-update
precondition. Evaluate clean, model, check, debt, release in that order.
`--release-strict` must remain nonzero for current content without relying on a
baseline.

- [ ] **Step 7: Verify and regenerate reports**

Run targeted tests, the historical suite, report line-count/forbidden-line
checks and `git diff --check`.

- [ ] **Step 8: Commit reports, counters, and gate contracts**

Run: `git diff --check` and require no output.
Run: `git status --short` and review every path before staging.
Run: `git add scripts/inventory_collection.py tests/test_inventory_collection.py ETAT_COLLECTION.md audit/INVENTAIRE_COLLECTION.md audit/AUDIT_CONSOLIDE.md`
Run: `git commit -m "[AUDIT][P0.1] fiabilise les rapports et compteurs"`

### Task 4: Add source roles and separate dispositions

**Files:**
- Modify: `scripts/inventory_collection.py`
- Modify: `tests/test_inventory_collection.py`
- Create: `audit/SOURCE_ROLES.yaml`
- Create: `audit/ANOMALY_DISPOSITIONS.yaml`

- [ ] **Step 1: Add RED role-precedence tests**

Parameterize `_harvest/**/*.candidate.tex`,
`build/maquette-v5/renvois.tex`, fixtures, validations/visual references,
archives and generated dependencies. Assert specific roles win before
`production_object`.

- [ ] **Step 2: Add RED raw/disposition separation tests**

Take a deep copy of `inventory["anomalies"]`, apply dispositions, and assert the
raw copy is byte-equivalent. Test every allowed disposition and the required
accepted-exception fields, including expiration.

Require `fingerprint`, `disposition`, `owner`, `justification`, `approved_by`
and `decision_ref` for all dispositions; proof for resolved/generated/intentional
qualifications; and scope, author, blocking plus expiry/review condition for
`accepted_exception`.

- [ ] **Step 3: Implement and validate source roles**

Create the versioned YAML and validate it with the source-role schema. Keep the
in-code fallback semantically equivalent. Order patterns from specific to
general.

- [ ] **Step 4: Implement disposition lookup as a separate view**

Return qualification records keyed by fingerprint. Do not add disposition,
blocking or fingerprint fields into raw anomaly mappings.

- [ ] **Step 5: Qualify known generated and intentional cases**

Record `renvois.tex` as generated and only evidence-backed maquette repetitions
as intentional reuse. Keep unknown or genuine debts active.

- [ ] **Step 6: Verify and commit classification/dispositions**

Run targeted tests, historical tests, schema validation, `git diff --check` and
`git status --short`.
Run: `git add scripts/inventory_collection.py tests/test_inventory_collection.py audit/SOURCE_ROLES.yaml audit/ANOMALY_DISPOSITIONS.yaml`
Run: `git commit -m "[AUDIT][P0.2] ajoute classification et dispositions"`

### Task 5: Add deterministic fingerprints and debt comparison

**Files:**
- Modify: `scripts/inventory_collection.py`
- Modify: `tests/test_inventory_collection.py`
- Create: `audit/ANOMALIES_BASELINE.json`
- Create: `audit/BASELINE_UPDATE_REPORT.md`

- [ ] **Step 1: Add RED fingerprint tests**

Assert stability across mapping/list order, line/date/tool-message changes and
absolute-root changes. Assert category, manual, chapter, normalized source,
field, target/ID or stable reason-code changes alter the fingerprint. Assert
`fingerprint_schema_version == 1`.

- [ ] **Step 2: Add RED multiset comparison tests**

Cover new, unchanged, resolved, modified, occurrence growth, stable-total
replacement, severity escalation, lost disposition and resolved-fingerprint
regression. Assert disappearance reports improvement and never fails alone.
Assert a new active anomaly without owner, justification or qualification fails.

- [ ] **Step 3: Add RED update-baseline CLI tests**

Assert refusal for dirty repo, invalid model, empty reason/approver and automatic
CI usage. Assert diff, SHA, old/new digests, resolved history and update report
are retained.

Add `test_baseline_ready_reports_all_ten_stabilization_checks`. Assert the gate
names historical/Phase-0 tests, schema parsing, renderers, object counts,
`_harvest`, `renvois.tex`, intentional reuse, false-positive/active disposition
coverage, fingerprint determinism and final model validation. One false check
must make update return code 8.

- [ ] **Step 4: Implement fingerprint v1 and comparison**

Use explicit canonical fields and stable reason codes. Detect modifications by
stable locator plus changed fingerprint. Preserve resolved fingerprints forever
unless a separately specified migration changes the schema.

- [ ] **Step 5: Implement explicit baseline update**

Add `--update-baseline --reason --approved-by`. Reject a final baseline until all
stabilization preconditions pass. A provisional baseline must declare
`provisional: true` and cannot satisfy the mandatory gate.

Implement `baseline_ready` as ten named structured results. Recalculate
automatic checks; obtain human decisions only from schema-valid dispositions
with proof and decision references. Do not accept a manually supplied readiness
boolean.

- [ ] **Step 6: Create only a provisional working baseline in this commit**

Create `audit/ANOMALIES_BASELINE.json` with `provisional: true` only to exercise
schema and comparison paths. `--fail-on-new` must remain code 5 against it. Do
not claim a stabilized baseline or invoke the update command from the dirty
implementation worktree.

- [ ] **Step 7: Verify and commit debt comparison implementation**

Run targeted tests and historical suite; assert `--fail-on-new` rejects the
provisional baseline and `--release-strict` is independently red.
Run: `git diff --check` and require no output.
Run: `git status --short` and review every path before staging.
Run: `git add scripts/inventory_collection.py tests/test_inventory_collection.py audit/ANOMALIES_BASELINE.json`
Run: `git commit -m "[AUDIT][P0.2] ajoute baseline et comparaison de dette"`

## Chunk 3: Transaction safety, observed builds, and CI

### Task 6: Make provenance reproducible and writes transactional

**Files:**
- Modify: `scripts/inventory_collection.py`
- Modify: `tests/test_inventory_collection.py`
- Regenerate: machine and human audit artifacts

- [ ] **Step 1: Add RED provenance tests**

Assert SHA, branch, dirty state, modified tracked files, relevant untracked
files, generator version/hash and real tool versions. Assert two runs under the
same `SOURCE_DATE_EPOCH` produce identical provenance.

- [ ] **Step 2: Add RED path and transaction tests**

Cover absolute paths, `..`, symlink escapes, concurrent processes, stale locks,
timeout, injected mid-batch replace failure and byte-identical rollback.

Expected errors are `InventoryError` containing `outside repository`,
`symlink escape`, `generation lock timeout` or `transaction rolled back`. A live
lock is never removed. A lock JSON record with dead PID and age at least 20
seconds is quarantined once; malformed or younger locks time out. A forced
failure on replacement N restores SHA-256 of all pre-existing outputs and leaves
no new target.

- [ ] **Step 3: Implement deterministic provenance**

Use Git metadata and `SOURCE_DATE_EPOCH` or a stable commit timestamp. Query Git,
Python, TeX/PDF tools by their actual executables. Classify untracked relevance
without counting temporary output directories.

- [ ] **Step 4: Hold one lock for the whole transaction**

Resolve all targets under the repository, acquire a process-identified lock,
render and validate every payload, stage backups, replace the lot, and release
only after success or rollback.

Store PID, process-start token and creation timestamp in the lock. Reclaim only
when the PID/start token no longer identifies a live owner and the age threshold
has elapsed. Keep the lock across render, validation, comparison and apply.

- [ ] **Step 5: Verify reproducibility and commit safety**

Generate twice into isolated directories, compare byte for byte, run concurrency
and rollback tests, historical suite, `git diff --check` and status.
Run: `git add scripts/inventory_collection.py tests/test_inventory_collection.py ETAT_COLLECTION.md audit/INVENTAIRE_COLLECTION.json audit/INVENTAIRE_COLLECTION.md audit/AUDIT_CONSOLIDE.md audit/ECARTS_ET_CONTRADICTIONS.yaml audit/MATRICE_LIVRABLES.yaml`
Run: `git commit -m "[AUDIT][P0.2] ajoute provenance et ecritures transactionnelles"`

### Task 7: Distinguish declared assemblies from observed builds

**Files:**
- Modify: `scripts/inventory_collection.py`
- Modify: `scripts/inventory_assembly.py`
- Modify: `NSI/scripts/assemble.py`
- Modify: `Mathematiques/manuel-maths/scripts/assemble.py`
- Modify: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
- Modify: `Mathematiques/manuel-maths/scripts/build_maquette_v5.py`
- Modify: `tests/test_inventory_collection.py`
- Create: `audit/BUILD_MANIFEST.json`

- [ ] **Step 1: Add RED semantic-separation tests**

Assert AST/regex discoveries appear only in `declared_assemblies`; no PDF is an
observed build without a valid manifest. Preserve `assemblies` as an equality
alias for historical consumers.

- [ ] **Step 2: Add RED manifest tests**

Require Git SHA, source digest, ordered objects, variant, PDF, pages, SHA-256,
tool versions and gate results. Reject missing PDF, digest mismatch, page mismatch
and unordered/set-like object data.

Add one integration test per assembly entrypoint using a fake successful LaTeX
process that writes a PDF fixture and an ordered trace. Assert the manifest order
equals the actual submission order, not a sorted AST-derived set.

- [ ] **Step 3: Implement declared/observed fields**

Populate `declared_assemblies` from existing analysis. Load `observed_builds`
only from validated manifest entries tied to the current source digest and Git
SHA.

- [ ] **Step 4: Prepare the real build manifest**

Add an opt-in trace output to each real assembly entrypoint. Surround each
submitted object with `NEXUS_OBJECT_BEGIN/END` TeX log markers, compile with
`-recorder`, and derive the treated order only by crossing marker order in the
`.log` with opened inputs in the `.fls`. Finalize a record only after the LaTeX
process succeeds. Recompute PDF SHA-256 and pages with `pdfinfo`; capture actual
tool versions and gate JSON.
Create the versioned envelope. Record only builds with this execution trace;
leave the list empty rather than infer evidence, and expose explicit release
blockers for missing observed variants.

- [ ] **Step 5: Verify and commit build evidence**

Run targeted/historical tests, schema validation, gates and diff checks.
Run: `git diff --check` and require no output.
Run: `git status --short` and review every path before staging.
Run: `git add scripts/inventory_collection.py scripts/inventory_assembly.py NSI/scripts/assemble.py Mathematiques/manuel-maths/scripts/assemble.py Mathematiques/manuel-maths/scripts/assemble_manuel.py Mathematiques/manuel-maths/scripts/build_maquette_v5.py tests/test_inventory_collection.py audit/BUILD_MANIFEST.json`
Run: `git commit -m "[AUDIT][P0.2] distingue assemblages declares et builds observes"`

### Task 7b: Freeze the first stable baseline from a clean commit

**Files:**
- Modify: `audit/ANOMALIES_BASELINE.json`
- Create or modify: `audit/BASELINE_UPDATE_REPORT.md`

- [ ] **Step 1: Verify all stabilization preconditions from a clean tree**

Run `git status --short` and require no output. Run `--validate-model` and require
code 0. Verify renderers, counters, `_harvest`, `renvois.tex`, intentional reuse,
false-positive dispositions and fingerprint tests are all green.

- [ ] **Step 2: Run the explicit baseline update**

Run: `python scripts/inventory_collection.py --update-baseline --reason "Gel initial apres stabilisation Phase 0.1" --approved-by "Alaeddine"`
Expected: prints active/new/resolved/modified diff, old/new digests and SHA Git;
writes a non-provisional baseline plus update report while preserving resolved
history.

- [ ] **Step 3: Verify gates and commit only the baseline transition**

Run `--validate-model` and `--fail-on-new`; both must return 0.
Run `--release-strict`; it must return 7 with deterministic blockers.
Run `git diff --check` and require no output.
Run `git status --short` and confirm only the two baseline transition files.
Stage only the two explicit baseline files.
Run: `git commit -m "[AUDIT][P0.2] fige la baseline initiale stabilisee"`

### Task 8: Wire the complete Phase 0.1 CI

**Files:**
- Create: `.github/workflows/ci-audit-collection.yml`
- Create or modify: `pyproject.toml`
- Modify: `tests/test_inventory_collection.py`
- Modify: audit artifacts if final generation changes them

- [ ] **Step 1: Add local CI configuration**

Pin `ruff==0.6.9`, `mypy==2.1.0`, `pytest==9.0.2`, `pytest-cov==7.0.0`,
`coverage==7.13.2`, `jsonschema==4.26.0` and `PyYAML==6.0.1`. Configure line and
branch measurement; record the measured percentages without inventing a lower
threshold.

- [ ] **Step 2: Implement the workflow**

Install pinned test tools, run lint, typing, tests, coverage, independent
JSON/YAML validation, two isolated generations with byte comparison, `--check`,
`--validate-model`, `--fail-on-new`, and a shell assertion that
`--release-strict` fails with its documented exit code and blocker inventory.
Never invoke `--update-baseline`.

Exact commands:

```bash
ruff check scripts tests
mypy scripts/inventory_collection.py scripts/inventory_graph.py scripts/inventory_assembly.py
pytest -q --cov=scripts --cov-branch --cov-report=term-missing --cov-report=xml
python -c "from pathlib import Path; import json,yaml; paths=[Path(p) for p in __import__('subprocess').check_output(['git','ls-files','*.json','*.yaml','*.yml'], text=True).splitlines()]; [(json.loads(p.read_text(encoding='utf-8')) if p.suffix == '.json' else yaml.safe_load(p.read_text(encoding='utf-8'))) for p in paths]; print(f'validated {len(paths)} JSON/YAML files')"
python scripts/inventory_collection.py --validate-model
python scripts/inventory_collection.py --check
python scripts/inventory_collection.py --fail-on-new
mkdir -p .phase01-repro/run1/audit .phase01-repro/run2/audit
export SOURCE_DATE_EPOCH="$(git show -s --format=%ct HEAD)"
python scripts/inventory_collection.py --audit-dir .phase01-repro/run1/audit --etat-path .phase01-repro/run1/ETAT_COLLECTION.md
python scripts/inventory_collection.py --audit-dir .phase01-repro/run2/audit --etat-path .phase01-repro/run2/ETAT_COLLECTION.md
diff -ru .phase01-repro/run1 .phase01-repro/run2
set +e
python scripts/inventory_collection.py --release-strict > .phase01-repro/release-strict.json
release_code=$?
set -e
test "$release_code" -eq 7
python -c "import json; p=json.load(open('.phase01-repro/release-strict.json', encoding='utf-8')); assert p['gate']=='release-strict' and p['blocker_count'] > 0"
```

- [ ] **Step 3: Upload audit evidence**

Upload coverage reports, gate outputs, generated artifacts, reproducibility diff
and build manifest with `if: always()`.

- [ ] **Step 4: Run the full local Phase 0.1 gate**

Run the exact workflow commands locally. Expected: lint/type/tests/coverage,
parsing, reproducibility, check, validate-model and fail-on-new pass;
release-strict fails only in the controlled assertion with a deterministic
positive blocker count.

- [ ] **Step 5: Commit CI**

Run `git diff --check`, `git status --short` and final tests.
Run: `git add .github/workflows/ci-audit-collection.yml pyproject.toml tests/test_inventory_collection.py audit/INVENTAIRE_COLLECTION.json audit/INVENTAIRE_COLLECTION.md audit/AUDIT_CONSOLIDE.md audit/ECARTS_ET_CONTRADICTIONS.yaml audit/MATRICE_LIVRABLES.yaml ETAT_COLLECTION.md`
Run: `git commit -m "[CI][AUDIT] branche les gates de Phase 0.1"`

### Task 9: Verify, publish, and open the draft PR

**Files:**
- No planned source changes; only evidence updates if verification proves they
  are required.

- [ ] **Step 1: Invoke verification-before-completion**

Run the full local Phase 0.1 command set from a clean worktree and record exact
pass counts, coverage, artifact validation and release blocker count.

- [ ] **Step 2: Invoke requesting-code-review**

Review the complete diff from `f500166` to HEAD for correctness, security,
determinism and requirement coverage. Address findings with focused tests and an
appropriate existing commit boundary.

- [ ] **Step 3: Push without force**

Run: `git push origin finalisation/collection-v1`.

- [ ] **Step 4: Open a real draft PR**

Verify GitHub CLI authentication. Open a draft PR from
`finalisation/collection-v1` to `main`, capture its real number, and do not claim
success if the command fails.

- [ ] **Step 5: Report the required final line**

Report: `TERMINÉ <SHA> — draft PR <numéro ou NON OUVERTE> — Phase 0.1 — tests <résultat> — release-strict rouge avec <nombre> bloqueurs inventoriés`.
