# Canonical Manual Collection Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the six Nexus manual source sets, selected existing builds, manifests, and production tooling into one verified `collection_canonique/` tree without losing WIP or upgrading any publication status.

**Architecture:** A fail-closed migration controller first inventories both repository worktrees and produces a frozen entry-by-entry plan. Existing consumers gain an explicit collection-root option, the complete target is built and tested in inactive staging, then one journaled cutover moves tracked and untracked entries together with the consumer defaults. TNSI remains source-only and blocked until a manifest and observed build prove 12/12 chapters.

**Tech Stack:** Python 3.12, pytest, JSON Schema, PyYAML, Git, GNU Make, LuaLaTeX, Poppler/qpdf, GitHub Actions.

**Design:** `docs/superpowers/specs/2026-08-08-collection-canonique-design.md`

---

## File Structure

The migration introduces these focused units before cutover:

- `nexus_collection/layout.py`: one typed legacy/canonical layout contract shared by all producers.
- `scripts/canonical_model.py`: immutable entry, candidate, operation, plan, and worktree-state records.
- `scripts/canonical_scan.py`: exhaustive `lstat` and Git snapshot collection only.
- `scripts/canonical_ownership.py`: reference graph and file ownership classification only.
- `scripts/canonical_selection.py`: logical deliverable grouping, winner ranking, and loser dispositions only.
- `scripts/canonical_state.py`: locked compare-and-swap journal and transition invariants only.
- `scripts/canonical_stage.py`: safe staging, exact reconciliation, cutover operations, and per-entry removal only.
- `nexus_collection/source_authority.py`: digest-bound authority for staged tracked and approved untracked source inputs.
- `scripts/canonical_migration.py`: thin CLI that delegates to the modules above.
- `scripts/verify_canonical_staging.py`: isolated staged-build and deterministic-inventory evidence.
- `tests/test_collection_layout.py`: layout confinement and legacy/canonical resolution tests.
- `tests/test_canonical_scan.py`: filesystem, Git state, WIP drift, and root-pruning tests.
- `tests/test_canonical_ownership.py`: dependency ownership tests.
- `tests/test_canonical_selection.py`: candidate and disposition tests.
- `tests/test_canonical_state.py`: transition, locking, crash, and replay tests.
- `tests/test_canonical_stage.py`: staging, reconciliation, cutover, and removal tests.
- `tests/test_canonical_source_authority.py`: staged-source attestation and drift tests.
- `tests/test_canonical_cli.py`: command/state/exit-code tests.
- `tests/test_canonical_assemblies.py`: six-manual manifest tests.
- `tests/test_verify_canonical_staging.py`: command matrix and evidence tests.
- `audit/CANONICAL_PATH_RULES.yaml`: versioned data mapping manual prefixes, roles, shared components, exclusions, and target paths.
- `audit/schemas/v1/canonical-path-rules.schema.json`: mapping contract.
- `audit/schemas/v1/canonical-migration-plan.schema.json`: exhaustive preflight contract.
- `audit/schemas/v1/canonical-migration-state.schema.json`: journal and transition contract.
- `audit/schemas/v1/canonical-migration-authority.schema.json`: finalized plan/state/disposition authority archive.
- `audit/schemas/v1/canonical-assembly.schema.json`: per-manual assembly contract.
- `audit/schemas/v1/canonical-migration-dispositions.schema.json`: explicit human decisions for blockers and divergent losers.
- `audit/CANONICAL_MIGRATION_DISPOSITIONS.yaml`: versioned approved decisions, empty by default.

At cutover, the controller moves those units and the existing production trees into:

- `collection_canonique/shared/collection/`: inventory, migration, build evidence, audit schemas, and tests.
- `collection_canonique/shared/mathematiques/`: shared Mathématiques assemblers, templates, tests, configuration, and assets.
- `collection_canonique/shared/nsi/`: shared NSI assemblers, templates, tests, configuration, and assets.
- `collection_canonique/manuels/<ID>/source/`: chapters, manual-only references, tests, and assets.
- `collection_canonique/manuels/<ID>/manifests/assembly.json`: sole authoritative ordered assembly declaration.
- `collection_canonique/manuels/<ID>/build/`: selected named deliverables and direct build evidence only.
- `collection_canonique/manuels/<ID>/meta/`: provenance and gate-derived status.
- `collection_canonique/inventory/`: generated collection index, migration report, final state, and checksums.

Repository policy remains at root: `AGENTS.md`, `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md`, `.github/`, `docs/`, and `pyproject.toml`. Their active path references are updated during cutover.

## Chunk 1A: Preserve WIP and freeze exhaustive inputs

### Task 1: Validate and commit the inherited 1NSI WIP separately

**Files:**
- Modify: `NSI/Makefile`
- Modify: `NSI/scripts/assemble.py`
- Modify: `NSI/chapitres/1NSI-TYPES-CONSTRUITS/amenagee/1NSI-TC-AM-EXTRAIT.tex`
- Modify: `NSI/tests/test_gates_corpus.py`
- Create: `NSI/gabarits/book_master.tex`
- Create: `NSI/manifests/books/1NSI.json`
- Create: `NSI/tests/test_assemble_book.py`
- Create: `docs/superpowers/specs/2026-08-08-1nsi-book-variants-design.md`
- Create: `docs/superpowers/plans/2026-08-08-assemblage-manuel-1nsi.md`
- Create: `docs/superpowers/plans/2026-08-08-1nsi-book-variants.md`

- [ ] **Step 1: Re-audit the inherited diff**

Run: `git status --short --branch && git diff --check && git diff -- NSI/Makefile NSI/scripts/assemble.py NSI/chapitres/1NSI-TYPES-CONSTRUITS/amenagee/1NSI-TC-AM-EXTRAIT.tex NSI/tests/test_gates_corpus.py`

Expected: only the already inventoried 1NSI book/variant WIP and its untracked files; no staged files.

- [ ] **Step 2: Run focused 1NSI tests**

Run: `cd NSI && python3 -m pytest tests/test_assemble_book.py tests/test_gates_corpus.py -q`

Expected: PASS.

- [ ] **Step 3: Build the four supported book variants**

Run:

```bash
(cd NSI && python3 scripts/assemble.py --book 1NSI --variant complet)
(cd NSI && python3 scripts/assemble.py --book 1NSI --variant remediation)
(cd NSI && python3 scripts/assemble.py --book 1NSI --variant methodes)
(cd NSI && python3 scripts/assemble.py --book 1NSI --variant amenagee)
```

Expected: `MANUEL_1NSI_v1.pdf`, `_remediation.pdf`, `_methodes.pdf`, and `_amenagee.pdf` exist under `NSI/build/books/`; every command exits 0.

- [ ] **Step 4: Run adjacent NSI gates**

Run: `cd NSI && python3 -m pytest tests/test_verify_python.py tests/test_gates_corpus.py tests/test_assemble_book.py -q`

Expected: PASS.

- [ ] **Step 5: Commit the book implementation without generated PDFs**

Run:

```bash
git add NSI/Makefile NSI/scripts/assemble.py NSI/gabarits/book_master.tex NSI/manifests/books/1NSI.json NSI/tests/test_assemble_book.py docs/superpowers/specs/2026-08-08-1nsi-book-variants-design.md docs/superpowers/plans/2026-08-08-assemblage-manuel-1nsi.md docs/superpowers/plans/2026-08-08-1nsi-book-variants.md
git diff --cached --check
git commit -m "[LATEX] finalise le mode livre et ses variantes 1NSI"
```

Expected: one commit; `NSI/build/books/*.pdf` remains unstaged for later canonical selection.

- [ ] **Step 6: Commit the amenagee regression separately**

Run:

```bash
git add NSI/chapitres/1NSI-TYPES-CONSTRUITS/amenagee/1NSI-TC-AM-EXTRAIT.tex NSI/tests/test_gates_corpus.py
git diff --cached --check
git commit -m "[TESTS] verrouille le rendu tabulaire de la variante amenagee"
```

Run: `git status --short --branch && git diff --check`

Expected: a second atomic commit; tracked tree clean. Generated `NSI/build/books/` PDF, `.tex`, `.log`, `.aux`, and `.toc` files may remain ignored/untracked and are inventoried explicitly for canonical selection or exclusion.

### Task 2: Define closed migration contracts and schema registration

**Files:**
- Create: `audit/CANONICAL_PATH_RULES.yaml`
- Create: `audit/CANONICAL_MIGRATION_DISPOSITIONS.yaml`
- Create: `audit/schemas/v1/canonical-path-rules.schema.json`
- Create: `audit/schemas/v1/canonical-migration-plan.schema.json`
- Create: `audit/schemas/v1/canonical-migration-state.schema.json`
- Create: `audit/schemas/v1/canonical-migration-authority.schema.json`
- Create: `audit/schemas/v1/canonical-assembly.schema.json`
- Create: `audit/schemas/v1/canonical-migration-dispositions.schema.json`
- Create: `tests/test_canonical_model.py`
- Modify: `scripts/inventory_collection.py`
- Modify: `tests/test_inventory_collection.py`

- [ ] **Step 1: Write RED schema-registry tests**

Require `SCHEMA_REGISTRY` and the exact-schema-directory test to contain all six new schemas. Require every schema to set `additionalProperties: false` at its root and reject an unknown field.

```python
def test_canonical_rules_cover_exact_manual_set(canonical_rules):
    assert set(canonical_rules["manuals"]) == {
        "1SPE", "TSPE_2026_2027", "TCOMPL", "TEXPERTES", "1NSI", "TNSI"
    }


def test_tnsi_rule_has_no_partial_build_authority(canonical_rules):
    tnsi = canonical_rules["manuals"]["TNSI"]
    assert tnsi["required_chapter_count"] == 12
    assert tnsi["allow_partial_build"] is False
```

- [ ] **Step 2: Run registry tests to verify RED**

Run: `pytest -q tests/test_canonical_model.py tests/test_inventory_collection.py -k 'canonical or schema_directory or registry'`

Expected: FAIL because contracts and registrations are absent.

- [ ] **Step 3: Implement the exact v1 payloads**

`canonical-path-rules` requires `artifact_type`, `schema_version`, `control_digest`, exact `manuals`, `scan_includes`, `shared_targets`, `excluded_names`, and `excluded_suffixes`. Each manual requires `subject`, `chapter_prefixes`, `referential_prefixes`, `required_chapter_count`, `allow_partial_build`, and closed `targets` (`source`, `manifest`, optional `build`).

`canonical-migration-plan` requires `artifact_type`, `schema_version`, `plan_digest`, `rules_digest`, `roots`, `entries`, `operations`, `dispositions_digest`, and `counts`. Root records require `root_id`, resolved path, device/inode identity, branch, HEAD, full sorted Git-status entries, porcelain-status digest, and explicit includes. Entry records require `entry_id`, root/path, kind, mode, size, `mtime_ns`, optional SHA-256/Git object, tracking/status classification, ownership, decision, reason, and target. Operation records require ID, ordered phases (`stage`, `cutover`, optional `cleanup`), nonempty `entry_ids`, action, ordered expected source size/digest records, and ordered zero-or-more target path/size/digest records. Ordinary copy/move/remove operations require one entry and at most one target; the closed `split_build_manifest` action alone permits one source and exactly six derived targets, each with a stable derived entry ID.

`canonical-migration-state` requires `state`, `revision`, `previous_state_digest`, `plan_digest`, worktree SHAs, completed operation-phase records (`operation_id`, `phase`, result digest), check results, expected root digests, and optional last error. Completing `stage` never implies `cutover` or `cleanup`; phase dependencies are schema-validated.

`canonical-migration-authority` requires the complete immutable plan payload, final state payload, approved dispositions payload, each canonical digest, final collection tree digest, and sorted relative source-authority records with path, kind, mode, size, and SHA-256. Cross-payload digests and entry partitions must reconcile exactly.

`canonical-assembly` requires `manual_id`, `subject`, `edition`, required/observed counts, `coverage_status`, ordered distinct chapters, variants, shared dependencies, and optional output. Output is forbidden unless coverage is complete.

`canonical-migration-dispositions` requires a control digest and records with `entry_id`, decision enum (`assign_owner`, `select_winner`, `discard_approved`, `exclude_approved`, `materialize_approved`), reason, approver, expected size, and expected SHA-256 when the entry is regular. `assign_owner` also requires `selected_owner`; `select_winner` requires `selected_candidate_id`.

Every v1 digest uses canonical JSON encoded as UTF-8 with sorted keys, compact separators, no NaN/Infinity, and normalized POSIX paths. A payload digest excludes its own digest field and explicitly schema-marked volatile fields only; tests pin the exact included/excluded field set so two implementations cannot disagree.

- [ ] **Step 4: Register schemas and verify GREEN**

Run: `pytest -q tests/test_canonical_model.py tests/test_inventory_collection.py -k 'canonical or schema_directory or registry'`

Expected: PASS.

- [ ] **Step 5: Commit the contracts**

Run:

```bash
git add audit/CANONICAL_PATH_RULES.yaml audit/CANONICAL_MIGRATION_DISPOSITIONS.yaml audit/schemas/v1/canonical-path-rules.schema.json audit/schemas/v1/canonical-migration-plan.schema.json audit/schemas/v1/canonical-migration-state.schema.json audit/schemas/v1/canonical-migration-authority.schema.json audit/schemas/v1/canonical-assembly.schema.json audit/schemas/v1/canonical-migration-dispositions.schema.json scripts/inventory_collection.py tests/test_canonical_model.py tests/test_inventory_collection.py
git diff --cached --check
git status --short
git commit -m "[AUDIT] definit les contrats de migration canonique"
```

### Task 3: Implement exhaustive scanning and frozen WIP snapshots

**Files:**
- Create: `scripts/canonical_model.py`
- Create: `scripts/canonical_scan.py`
- Create: `tests/test_canonical_scan.py`
- Modify: `.gitignore`

- [ ] **Step 1: Write RED entry and worktree-state tests**

Use this public contract:

```python
@dataclass(frozen=True)
class ScanRoot:
    root_id: str
    repository_root: Path
    includes: tuple[PurePosixPath, ...]


@dataclass(frozen=True)
class GitStatusEntry:
    index_status: str
    worktree_status: str
    path: PurePosixPath
    original_path: PurePosixPath | None
    kind: str
    size: int | None
    sha256: str | None
    in_scope: bool


@dataclass(frozen=True)
class WorktreeState:
    root_id: str
    resolved_path: str
    device: int
    inode: int
    branch: str
    head: str
    status_entries: tuple[GitStatusEntry, ...]
    porcelain_sha256: str


@dataclass(frozen=True)
class EntrySnapshot:
    entry_id: str
    root_id: str
    path: PurePosixPath
    kind: str
    mode: int
    size: int
    mtime_ns: int
    sha256: str | None
    git_object: str | None
    tracking: str
    safety_status: str
    safety_reason: str | None


@dataclass(frozen=True)
class MigrationSnapshot:
    worktrees: tuple[WorktreeState, ...]
    entries: tuple[EntrySnapshot, ...]
    snapshot_digest: str
```

The fixture must create a hidden file, empty directory, symlink, Unicode file, tracked regular file, modified tracked file, renamed file, untracked regular file, and FIFO when supported. Assert all entries and Git-status records are present exactly once, symlink/FIFO entries carry `safety_status="blocked"` and stable reasons, out-of-scope status is explicitly classified, and `.git` plus `.worktrees` are absent because they are not in `includes`.

- [ ] **Step 2: Run scanner tests to verify RED**

Run: `pytest -q tests/test_canonical_scan.py`

Expected: FAIL because scan/model modules are absent.

- [ ] **Step 3: Implement read-only scanning**

Expose `scan_roots(roots: tuple[ScanRoot, ...]) -> MigrationSnapshot` and `verify_frozen_snapshot(snapshot, journaled_operations) -> tuple[str, ...]`. Use sorted explicit includes, `os.scandir`/`lstat`, `O_NOFOLLOW`, finite Git timeouts, and root device/inode checks. Never recurse from repository root and never follow links.

- [ ] **Step 4: Add drift tests**

Test content replacement, same-size replacement, chmod, mtime-only change, deletion, new entry, HEAD change, branch change, porcelain-status change, root path substitution, and device/inode substitution. A journaled move is accepted only when old path, new path, expected digest, and permitted state all match.

- [ ] **Step 5: Verify GREEN and ignore only control scratch**

Run: `pytest -q tests/test_canonical_scan.py`

Add only `/.migration/` to `.gitignore`; do not ignore `collection_canonique/`.

- [ ] **Step 6: Commit the scanner**

Run:

```bash
git add .gitignore scripts/canonical_model.py scripts/canonical_scan.py tests/test_canonical_scan.py
git diff --cached --check
git status --short
git commit -m "[AUDIT] inventorie exhaustivement les arbres legacy"
```

## Chunk 1B: Classify ownership and select canonical winners

### Task 4: Implement dependency-based ownership

**Files:**
- Create: `scripts/canonical_ownership.py`
- Create: `tests/test_canonical_ownership.py`

- [ ] **Step 1: Write RED ownership tests**

Fixtures must cover chapter-prefix ownership, manual referentials, one-manual tests/assets, shared discipline scripts/templates, collection tooling, authoritative assembly manifests, a shared asset referenced by two manuals, and an unreferenced ambiguous file. The expected owner is a canonical component ID; the ambiguous file is blocked.

- [ ] **Step 2: Run ownership tests to verify RED**

Run: `pytest -q tests/test_canonical_ownership.py`

Expected: FAIL.

- [ ] **Step 3: Implement the reference graph API**

Expose `build_reference_graph(snapshot, rules) -> ReferenceGraph` and `classify_ownership(entry, graph, rules) -> OwnershipDecision`. Parse supported LaTeX inputs, Python imports/path literals, Makefile/CI paths, and manifest references. Prefix rules may confirm an unambiguous owner but cannot override a graph conflict.

- [ ] **Step 4: Verify GREEN and commit**

Run: `pytest -q tests/test_canonical_ownership.py`

Then run:

```bash
git add scripts/canonical_ownership.py tests/test_canonical_ownership.py
git diff --cached --check
git status --short
git commit -m "[AUDIT] attribue chaque source a un composant canonique"
```

### Task 5: Implement deterministic winner selection and conflict blocking

**Files:**
- Modify: `scripts/canonical_model.py`
- Create: `scripts/canonical_selection.py`
- Create: `tests/test_canonical_selection.py`

- [ ] **Step 1: Write RED selection tests with full candidate fixtures**

Use a `candidate()` fixture requiring every ranking field. Test these exact sets:

- root candidate coverage 10 with valid evidence versus active-worktree coverage 1: root wins;
- `release_named` versus `specimen` for the same role/edition: release wins and specimen is excluded;
- byte-identical candidates equal on evidence/coverage/gates/recency: active worktree wins;
- equal-quality candidates with different SHA-256: selection is blocked, so no winner;
- equal-quality candidates from incomparable Git/build recency domains: selection is blocked with `incomparable_recency`;
- unique untracked loser without approved disposition: selection is blocked;
- TNSI coverage 6 of required 12: no build winner and stable `tnsi_incomplete_6_of_12` reason.

- [ ] **Step 2: Run selection tests to verify RED**

Run: `pytest -q tests/test_canonical_selection.py`

Expected: FAIL.

- [ ] **Step 3: Implement ranking and dispositions**

Expose this public contract:

```python
@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    entry_id: str
    manual_id: str
    deliverable_role: str
    edition: str
    sha256: str
    size: int
    evidence_valid: bool
    coverage: int
    gate_strength: int
    artifact_kind: str
    variant: str
    tracking: str
    git_object: str | None
    recency_domain: str
    recency_value: tuple[int, str]
    active_worktree: bool


@dataclass(frozen=True)
class SelectionRules:
    required_coverage: Mapping[str, int]
    artifact_priority: Mapping[str, int]


@dataclass(frozen=True)
class ApprovedDisposition:
    entry_id: str
    candidate_id: str
    decision: str
    expected_sha256: str
    expected_size: int
    selected_candidate_id: str | None
    control_digest: str
    approver: str
    reason: str


@dataclass(frozen=True)
class LoserDisposition:
    candidate_id: str
    entry_id: str
    decision: str
    reason: str


@dataclass(frozen=True)
class SelectionBlocker:
    candidate_ids: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class SelectionResult:
    winners: tuple[Candidate, ...]
    loser_dispositions: tuple[LoserDisposition, ...]
    blockers: tuple[SelectionBlocker, ...]
    selection_digest: str


def select_candidates(
    candidates: tuple[Candidate, ...],
    rules: SelectionRules,
    approved_dispositions: tuple[ApprovedDisposition, ...],
) -> SelectionResult: ...
```

`SelectionResult` contains sorted `winners`, one typed loser disposition per nonwinner, and sorted blockers with stable reason codes. Group by `(manual_id, deliverable_role, edition)`. Rank valid evidence, coverage, gate strength, artifact kind, explicit variant, then recency only when `recency_domain` matches; otherwise a tie remains `incomparable_recency`. Use active-worktree only for byte-identical ties. Divergent ties remain blocked. Any divergent losing candidate with `tracking` untracked/ignored and no Git object is `unique_untracked_loser` until an exact approved disposition preserves or discards it. An approved disposition is accepted only when its entry/candidate ID, digest, size, decision-specific field, control digest, approver, and reason all match.

- [ ] **Step 4: Prove order independence**

Parameterize each fixture with original and reversed candidate order and assert equal serialized selection results and `selection_digest`. Task 8 later incorporates that digest into the complete preflight plan digest.

Run: `pytest -q tests/test_canonical_selection.py`

Expected: PASS.

- [ ] **Step 5: Commit selection logic**

Run:

```bash
git add scripts/canonical_model.py scripts/canonical_selection.py tests/test_canonical_selection.py
git diff --cached --check
git status --short
git commit -m "[AUDIT] selectionne les sources et livrables canoniques"
```

- [ ] **Step 6: Verify the complete preflight chunk**

Run: `pytest -q tests/test_canonical_model.py tests/test_canonical_scan.py tests/test_canonical_ownership.py tests/test_canonical_selection.py tests/test_inventory_collection.py && git diff --check && git status --short --branch`

Expected: PASS; only previously identified WIP or ignored build residues remain outside committed preflight work.

## Chunk 2: Add the resumable transaction without moving production files

### Task 6: Implement locked state transitions and compare-and-swap journaling

**Files:**
- Create: `scripts/canonical_state.py`
- Create: `tests/test_canonical_state.py`
- Validate: `audit/schemas/v1/canonical-migration-state.schema.json`

- [ ] **Step 1: Write RED transition-invariant tests**

Allow only these edges and require the named evidence:

| Transition | Required evidence |
|---|---|
| `inventoried -> staged` | zero blocked operations and unchanged frozen roots |
| `staged -> verified` | exact staged partition, immutable staging digest, passed build/inventory evidence |
| `verified -> cutover_in_progress` | fresh frozen-root check and complete ordered operation list |
| `cutover_in_progress -> cutover` | every required `cutover` phase for move/default/CI operations complete and canonical consumer check passed; cleanup phases remain pending |
| `cutover -> legacy_removed` | post-cutover gates recorded, exact legacy partition, zero blocked entries |

Reject skipped/backward transitions, missing plan digest, changed root identity/HEAD/status, and a journal located inside a moved root.

- [ ] **Step 2: Add RED concurrency, crash, replay, and authorized-status tests**

Use two processes attempting the same revision; exactly one succeeds and the other receives stable `state_conflict`. Inject failure before temp write, before replace, after replace, and during directory fsync. Reopening must yield either the previous or next schema-valid state, never a merged/lost update. Replaying a completed operation must be a no-op only when its result digest matches.

Every journal operation declares the exact Git-status entry delta it is allowed to cause. Tests prove `record_operation` atomically advances both the operation result and expected sorted Git-status digest; an extra/missing/modified status entry remains drift even during cutover.

- [ ] **Step 3: Run all state tests to verify RED**

Run: `pytest -q tests/test_canonical_state.py`

Expected: FAIL before implementation.

- [ ] **Step 4: Implement locked compare-and-swap writes**

Expose `load_state()`, `transition(expected_revision, expected_digest, target, evidence)`, `operation_lock(expected_revision, expected_digest, operation_id, phase)`, and lock-required `record_operation(operation_lease, result_digest, expected_status_delta)`. Hold the same exclusive `fcntl.flock` lease across fresh filesystem checks, mutation, all durability syncs, Git-status verification, and journal recording; a worker that loses the initial revision/digest check mutates nothing. Validate phase dependencies, schema, and distinct `(operation_id, phase)` completion. Write an exclusive state temporary, `fsync`, `os.replace`, and `fsync` the state parent. Recompute sorted Git-status entries after each authorized operation and accept only the declared delta before recording its new expected digest.

- [ ] **Step 5: Verify GREEN and commit**

Run: `pytest -q tests/test_canonical_state.py`

Then:

```bash
git add scripts/canonical_state.py tests/test_canonical_state.py
git diff --cached --check
git status --short
git commit -m "[AUDIT] ajoute le journal reprenable de migration"
```

### Task 7: Implement safe staging, exact partitions, and per-entry removal

**Files:**
- Create: `scripts/canonical_stage.py`
- Create: `tests/test_canonical_stage.py`

- [ ] **Step 1: Write all RED staging, cutover, cleanup, directory, and replay tests**

Require staging under `.migration/staged/collection_canonique`, no legacy mutation, no symlink destination, no hardlink reuse, identical regular-file bytes/modes, empty directories and directory modes, and explicit exclusions. Cover staged copy, cutover move, exact source unlink, bottom-up empty-directory removal, finalization, and `--cleanup` of verifier copies. Inject interruption after the first of three files, leave a stale temporary, rerun, and assert only missing/invalid operations are repeated.

Before implementation, add fresh-before-unlink/rmdir mutations, concurrent workers targeting the same entry, and injected failures before every file/directory `fsync`. Assert a losing/stale worker performs no mutation, drift preserves the source, and no operation is journal-complete before all affected parent directories are durable.

- [ ] **Step 2: Run staging tests to verify RED**

Run: `pytest -q tests/test_canonical_stage.py`

Expected: FAIL.

- [ ] **Step 3: Implement safe staging and operation replay**

Expose `stage_entry`, `stage_directory`, `apply_cutover_operation`, `remove_entry`, `remove_empty_directory`, and `finalize_control_plane`, each requiring the operation lease from Task 6. Use descriptor-relative opens with `O_NOFOLLOW`, explicit parent creation, exclusive temporary files, digest/mode verification, `os.replace`, and journal updates. Before completion, `fsync` the file and destination parent; rename/move also syncs the source parent, and unlink/rmdir syncs its parent. Persist directory modes and empty-directory entries. A stale temporary is removed only when its name and parent match the current operation ID.

- [ ] **Step 4: Implement exact set reconciliation**

Expose `reconcile(entry_ids, moved_ids, excluded_ids, blocked_ids)`. Require the three result sets to be pairwise disjoint and their union to equal the scanned entry-ID set. The transition to `legacy_removed` additionally requires `blocked_ids == set()`; counts are reported but never used as proof.

- [ ] **Step 5: Implement fresh-before-unlink removal**

Immediately before each unlink/rmdir, `lstat` and hash the entry and compare it to its current journal expectation. Mutation after preview must return `legacy_drift` and preserve the entry. Reject a directory until all children have completed dispositions.

- [ ] **Step 6: Verify GREEN and commit**

Run: `pytest -q tests/test_canonical_stage.py`

Then:

```bash
git add scripts/canonical_stage.py tests/test_canonical_stage.py
git diff --cached --check
git status --short
git commit -m "[AUDIT] stage et reconcilie les entrees canoniques"
```

### Task 8: Expose the thin CLI and exact state guards

**Files:**
- Create: `scripts/canonical_migration.py`
- Create: `tests/test_canonical_cli.py`
- Generate: `.migration/control/migration-plan.json`
- Generate: `.migration/control/migration-state.json`
- Generate: `.migration/control/preflight-summary.md`

- [ ] **Step 1: Write RED parser/state/exit-code tests**

The exact subcommands are `preflight`, `report`, `disposition`, `stage`, `verify-staging`, `verify-frozen`, `plan-consumers`, `begin-cutover`, `resume-cutover`, `verify-consumers`, `record-post-cutover-evidence`, `complete-cutover`, `record-commit`, `reconcile`, `remove-legacy`, and `finalize`.

Require these guards: `disposition` only from `inventoried` with zero completed operation phases; `stage` only from blocker-free `inventoried` or the same immutable plan already in `staged`; `verify-staging` only from `staged`; `plan-consumers` and `begin-cutover` only from `verified`; `resume-cutover`, `verify-consumers`, `record-post-cutover-evidence`, and `complete-cutover` only from `cutover_in_progress`; `complete-cutover` additionally requires every planned `cutover` phase while leaving declared cleanup phases pending; `record-commit --phase dispositions` only from operation-free `inventoried`, `record-commit --phase cutover` only from `cutover`; `reconcile` and `remove-legacy` only from `cutover`; `finalize` only from `legacy_removed`. `report` is read-only in every state. `preflight --check` writes nothing.

Use exit codes `0` success, `2` usage, `3` drift, `4` valid preflight with unresolved blockers, `5` invalid state/CAS conflict, `6` staging/evidence failure, `7` cutover refusal, and `8` removal/finalization refusal.

- [ ] **Step 2: Run CLI tests to verify RED**

Run: `pytest -q tests/test_canonical_cli.py`

Expected: FAIL.

- [ ] **Step 3: Implement delegation-only CLI handlers**

Each handler parses arguments, calls one focused module, prints one sorted JSON result, and returns the stable exit code. `disposition` writes only `audit/CANONICAL_MIGRATION_DISPOSITIONS.yaml`, requires nonblank reason/approver, current entry digest and size, plus `--selected-owner` for `assign_owner` or `--selected-candidate-id` for `select_winner`. Under the state lock it atomically writes the YAML and advances only the expected Git-status digest for that exact path, without recording an operation phase; the later disposition commit must clear that exact status through `record-commit`. `report` supports exact filters `blocked`, `discard_required`, `move`, `exclude`, `incomplete`, and `all`.

`preflight` may create a plan only when no state exists, or replace an `inventoried` plan only when it has zero completed operation phases. `disposition` has the same `inventoried`/zero-phase pre-write guard and must validate state before opening its tracked YAML; in every later state it writes nothing. Once any operation phase is recorded, changed rules/dispositions require a new state directory. `stage` accepts blocker-free `inventoried` or resumable `staged`; a resumed run must use the same immutable plan and staging digest. `verify-staging` only accepts `staged`; all later guards remain as listed above. The verifier CLI defines `--cleanup` as exact per-entry deletion of its own verification root after evidence has been durably copied outside it; it rejects any other root.

`plan-consumers --output consumer-patch.json` renders the closed canonical path/default/CI transforms without writing production files. It records every consumer path, preimage size/digest, full expected postimage size/digest, and expected Git-status delta; unknown content or an unconsumed legacy reference is code 7. It also writes and validates `git-pathspecs.nul` from the union of move sources/targets and consumer paths. `begin-cutover` requires both files and binds their digests into state; `resume-cutover` applies their expected bytes as journaled operations rather than accepting ad hoc consumer edits.

`record-commit` is the only permitted HEAD advance while migration state remains active. It requires an expected parent SHA, new commit SHA, phase name, and frozen NUL pathspec; validates a single-parent commit whose exact diff is confined to that pathspec and whose worktree is otherwise at the journaled status; then atomically advances expected HEAD/status. Phase `dispositions` is allowed only in operation-free `inventoried` and only for `audit/CANONICAL_MIGRATION_DISPOSITIONS.yaml`; phase `cutover` is allowed only after transition to `cutover` and only for the frozen migration pathspec.

- [ ] **Step 4: Verify CLI GREEN**

Run: `pytest -q tests/test_canonical_cli.py`

Expected: PASS.

- [ ] **Step 5: Commit code/tests before creating active state**

Run:

```bash
git add scripts/canonical_migration.py tests/test_canonical_cli.py
git diff --cached --check
git status --short
git commit -m "[AUDIT] expose le controleur de migration canonique"
```

- [ ] **Step 6: Verify a complete successful CLI lifecycle in a temporary Git fixture**

Require and run one integration test that performs, in valid order, preflight, an exact disposition commit plus operation-free `record-commit --phase dispositions`, refreshed preflight, disposition rejection after operations, interrupted/resumed stage, staging evidence, `plan-consumers`, begin/resume cutover, consumer/gate evidence, complete cutover, a real fixture commit plus `record-commit --phase cutover`, reconcile, preview/apply removal, and finalize. Assert every state/digest and final archived partition.

Run: `pytest -q tests/test_canonical_state.py tests/test_canonical_stage.py tests/test_canonical_cli.py`

Expected: PASS, including the complete successful lifecycle and every refusal path.

- [ ] **Step 7: Generate the first real read-only preflight**

Run:

```bash
python3 scripts/canonical_migration.py preflight \
  --primary-root /home/alaeddine/Documents/Manuels_Nexus/.worktrees/finalisation-collection-v1 \
  --fallback-root /home/alaeddine/Documents/Manuels_Nexus \
  --rules audit/CANONICAL_PATH_RULES.yaml \
  --dispositions audit/CANONICAL_MIGRATION_DISPOSITIONS.yaml \
  --state-dir .migration/control
```

The rules' explicit includes are the only scanned roots. They exclude `.git`, `.worktrees`, and the primary worktree nested beneath the fallback root by construction. Expected: exit 0 when no blockers, otherwise exit 4 with a valid `inventoried` plan/state and complete blocked report; no production file changes.

- [ ] **Step 8: Review blockers and verify the complete transaction chunk**

Run: `python3 scripts/canonical_migration.py report --state-dir .migration/control --only blocked,discard_required`

Expected: each row includes entry ID, root/path, kind, tracking, digest, ownership, target/reason, and allowed disposition. Do not stage while any row remains.

Do not commit `.migration/`; final evidence is archived after successful cleanup.

Run: `pytest -q tests/test_canonical_state.py tests/test_canonical_stage.py tests/test_canonical_cli.py && git diff --check && git status --short --branch`

Expected: PASS; tracked status is clean and only ignored `.migration/` evidence plus previously identified build residues remain.

## Chunk 3: Make every producer root-aware and manifest-driven

### Task 9: Declare authoritative manifests in legacy paths for later journaled moves

**Files:**
- Create: `tests/test_canonical_assemblies.py`
- Create: `Mathematiques/manuel-maths/manifests/books/1SPE.json`
- Create: `Mathematiques/manuel-maths/manifests/books/TSPE_2026_2027.json`
- Create: `Mathematiques/manuel-maths/manifests/books/TCOMPL.json`
- Create: `Mathematiques/manuel-maths/manifests/books/TEXPERTES.json`
- Modify: `NSI/manifests/books/1NSI.json`
- Create: `NSI/manifests/books/TNSI.json`

- [ ] **Step 1: Write RED manifest-authority tests**

Assert schema validity, exact ordered distinct chapters, expected observed counts `10, 11, 9, 5, 10, 6`, and required counts equal to observed except TNSI required 12. TNSI chapters are exactly `TNSI-ALGORITHMIQUE`, `TNSI-ARCHITECTURES-MATERIELLES-SY`, `TNSI-BASES-DE-DONNEES`, `TNSI-HISTOIRE-INFORMATIQUE`, `TNSI-LANGAGES-ET-PROGRAMMATION`, and `TNSI-STRUCTURES-DONNEES`; it has `coverage_status: blocked`, empty variants, and no output field. 1NSI variants are `complet`, `remediation`, `methodes`, and `amenagee`.

- [ ] **Step 2: Run tests to verify RED**

Run: `pytest -q tests/test_canonical_assemblies.py`

Expected: FAIL because normalized manifests are absent.

- [ ] **Step 3: Write the six authoritative manifests directly**

Use `apply_patch` to write sorted/indented UTF-8 JSON after manually reconciling current assembler declarations and actual chapter directories. These six files become the only ordered assembly authority immediately; no generator or second literal declaration is introduced. Tests parse each payload through `canonical-assembly.schema.json` and compare every chapter path to an existing source directory.

- [ ] **Step 4: Verify manifests and source coverage**

Run:

```bash
pytest -q tests/test_canonical_assemblies.py
```

Expected: exit 0. No `collection_canonique/` directory exists yet; the migration map targets these legacy manifests to final `manifests/assembly.json` paths.

- [ ] **Step 5: Commit**

Run:

```bash
git add tests/test_canonical_assemblies.py Mathematiques/manuel-maths/manifests/books/1SPE.json Mathematiques/manuel-maths/manifests/books/TSPE_2026_2027.json Mathematiques/manuel-maths/manifests/books/TCOMPL.json Mathematiques/manuel-maths/manifests/books/TEXPERTES.json NSI/manifests/books/1NSI.json NSI/manifests/books/TNSI.json
git diff --cached --check
git status --short
git commit -m "[AUDIT] declare les assemblages canoniques"
```

### Task 10: Add one typed CollectionLayout contract

**Files:**
- Create: `nexus_collection/__init__.py`
- Create: `nexus_collection/layout.py`
- Create: `nexus_collection/source_authority.py`
- Create: `tests/test_collection_layout.py`
- Create: `tests/test_canonical_source_authority.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: Write RED layout tests**

Require `CollectionLayout.legacy(repository_root)`, `CollectionLayout.canonical(collection_root)`, and `CollectionLayout.auto(script_path, explicit_collection_root=None)`. A shared `complete_collection_fixture` always creates schema-valid manifests for all six IDs, even when a test exercises one manual. Test `shared_root(subject)`, `manual_source(id)`, `chapters(id)`, `assembly_manifest(id)`, `build(id)`, and collection inventory paths. Explicit canonical roots must never fall back to legacy; unknown IDs, symlink roots, and paths escaping the root are rejected.

Add RED source-authority tests proving that Git-tracked legacy inputs are accepted. A staged regular file is accepted only when state is `staged` or later, every staging operation is complete, and the schema-valid plan contains the same entry ID, source/staged paths, size, digest, and approved untracked disposition. An `inventoried`/partially staged state, changed bytes, excluded entry, missing disposition payload, or path escape returns stable `untrusted_source`.

Add replica tests for `SourceAuthority.from_staged_replica(plan, state, dispositions, staged_root, replica_root)`: require the verified immutable-input partition digest, which includes selected source/template/config/manifest inputs but explicitly excludes selected or generated `build/` outputs. Resolve each replica input by its staged-root-relative path and compare mode/size/SHA-256 to both plan entry and staged file before authorization. Reject extra/missing immutable input entries, symlink/hardlink substitution, or a replica outside its bound root; allow excluded build outputs to be removed and regenerated without changing source authority.

- [ ] **Step 2: Run tests to verify RED**

Run: `pytest -q tests/test_collection_layout.py tests/test_canonical_source_authority.py`

Expected: FAIL.

- [ ] **Step 3: Implement immutable layout resolution**

The dataclass stores resolved root, mode (`legacy` or `canonical`), and the exact manual map. Legacy paths reproduce current locations. Canonical paths implement the approved tree. `auto()` derives canonical mode only when the script is physically under `collection_canonique/shared/`; otherwise it derives the Git root and legacy mode. An explicit root must contain all six assembly manifests.

Expose `SourceAuthority.from_git(repository_root)`, `SourceAuthority.from_staged_plan(plan, state, dispositions, staged_root)`, `SourceAuthority.from_staged_replica(plan, state, dispositions, staged_root, replica_root)`, and `SourceAuthority.from_final_evidence(evidence, collection_root)`, plus `authorize_regular(path) -> AuthorizedSource`. `from_staged_*` accepts only a complete `staged` or later state, not merely `inventoried`; this is the authority used to generate the build evidence required for the `staged -> verified` transition. Assemblers and build-evidence writers authorize every source/template/config input before opening it; no mode weakens Git/source checks globally.

- [ ] **Step 4: Verify and commit**

Run:

```bash
pytest -q tests/test_collection_layout.py tests/test_canonical_source_authority.py
git add nexus_collection/__init__.py nexus_collection/layout.py nexus_collection/source_authority.py tests/test_collection_layout.py tests/test_canonical_source_authority.py pyproject.toml
git diff --cached --check
git status --short
git commit -m "[AUDIT] ajoute le contrat de chemins canoniques"
```

### Task 11: Make Mathématiques assemblers root-aware

**Files:**
- Modify: `Mathematiques/manuel-maths/scripts/common.py`
- Modify: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
- Modify: `Mathematiques/manuel-maths/scripts/assemble_livrets.py`
- Create: `Mathematiques/manuel-maths/scripts/check_variant_separation.py`
- Modify: `Mathematiques/manuel-maths/Makefile`
- Modify: `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py`
- Modify: `Mathematiques/manuel-maths/tests/test_assemble_livrets.py`
- Modify: `Mathematiques/manuel-maths/tests/test_assemble_engine.py`
- Modify: `Mathematiques/manuel-maths/tests/test_pdf_integrity.py`
- Create: `Mathematiques/manuel-maths/tests/test_variant_separation.py`
- Modify: `scripts/inventory_assembly.py`
- Modify: `tests/test_inventory_collection.py`

- [ ] **Step 1: Write RED explicit-layout tests**

Create a complete temporary canonical fixture with one manual chapter, assembly manifest, shared template/config, and output directory. Assert `--collection-root` reads only those paths, writes only to that manual build, and a missing explicit path fails without consulting legacy. Add the same root option to `assemble_livrets.py`. Require every manual and supplement output to atomically write `build/evidence/<pdf-stem>.receipt.json` under the existing observed-build receipt schema, with confined durable `log_path`, exact source/input digests, variant, PDF digest, and Math margin evidence. Add RED `check_variant_separation.py` API/CLI tests for teacher-only text, internal IDs/placeholders, identical PDF extraction, and receipt-input leakage.

- [ ] **Step 2: Write RED manifest-authority tests**

Change the legacy Python chapter literal in a fixture while leaving `assembly.json` fixed. The assembler and static inventory must use only the manifest order. Removing a manifest chapter must fail closed.

- [ ] **Step 3: Run focused tests to verify RED**

Run: `(cd Mathematiques/manuel-maths && PYTHONPATH=../.. python3 -m pytest tests/test_assemble_manuel_observed.py tests/test_assemble_livrets.py tests/test_assemble_engine.py tests/test_pdf_integrity.py tests/test_variant_separation.py -q) && PYTHONPATH=. pytest -q tests/test_inventory_collection.py -k assembler`

Expected: FAIL.

- [ ] **Step 4: Implement layout injection and manifest authority**

Add `--collection-root` to both assembler CLIs and `COLLECTION_ROOT ?=` Make support. Before cutover, the Makefile exports `PYTHONPATH := $(abspath ../..):$(PYTHONPATH)`; canonical CI and the staging verifier later export `<collection-root>/shared/collection/python`. Accept injectable `CollectionLayout` and `SourceAuthority` instances in `main()`. Replace manual chapter literals with `assembly.json`; update static inventory to parse the schema-validated manifest. Preserve all receipt, `.fls`, confinement, symlink/hardlink, reproducibility, and atomic-promotion checks against the selected layout and authorize each opened input. Extend the existing receipt writer to manuals and all three supplements, durably promoting log/receipt with the PDF. Implement `check_variant_separation.verify_pair(...)` and its exact CLI as the Math API consumed in Task 15.

- [ ] **Step 5: Verify complete Mathématiques regression**

Run: `(cd Mathematiques/manuel-maths && PYTHONPATH=../.. python3 -m pytest tests/ -q) && PYTHONPATH=. pytest -q tests/test_inventory_collection.py -k assembler`

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```bash
git add Mathematiques/manuel-maths/scripts/common.py Mathematiques/manuel-maths/scripts/assemble_manuel.py Mathematiques/manuel-maths/scripts/assemble_livrets.py Mathematiques/manuel-maths/scripts/check_variant_separation.py Mathematiques/manuel-maths/Makefile Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py Mathematiques/manuel-maths/tests/test_assemble_livrets.py Mathematiques/manuel-maths/tests/test_assemble_engine.py Mathematiques/manuel-maths/tests/test_pdf_integrity.py Mathematiques/manuel-maths/tests/test_variant_separation.py scripts/inventory_assembly.py tests/test_inventory_collection.py
git diff --cached --check
git status --short
git commit -m "[LATEX] rend les assemblages mathematiques root-aware"
```

### Task 12: Make NSI root-aware and retain the 12/12 TNSI lock

**Files:**
- Modify: `NSI/scripts/common.py`
- Modify: `NSI/scripts/assemble.py`
- Modify: `NSI/scripts/gates_corpus/check_eleve_no_corrige.py`
- Modify: `NSI/Makefile`
- Modify: `NSI/tests/test_assemble_book.py`
- Modify: `NSI/tests/test_corpus_readonly.py`
- Modify: `NSI/tests/test_gates_corpus.py`
- Modify: `NSI/tests/test_meta_schemas.py`
- Modify: `NSI/tests/test_verify_python.py`

- [ ] **Step 1: Write RED canonical-root fixture tests**

Build a temporary canonical fixture containing the six TNSI chapter directories and a schema-valid TNSI manifest with `required_chapter_count: 12`, `observed_chapter_count: 6`, and `coverage_status: blocked`. Assert `collect_book_chapters("TNSI", layout=layout)` raises `ValueError("TNSI exige 12/12 chapitres; observe: 6/12")` and that `layout.build("TNSI")` is not created.

Create a separate complete 1NSI fixture and assert rendered input paths, template path, and output path all stay inside its explicit canonical layout even when valid-looking legacy files exist nearby. Require each of the four 1NSI variants to atomically write `build/evidence/<pdf-stem>.receipt.json` under the observed-build receipt schema with durable confined `log_path`, exact inputs/variant, and PDF digest. Add RED tests for `check_eleve_no_corrige.scan(layout, book, variant, generated_tex)` and its `--collection-root --book --variant --generated-tex` CLI; no module-level legacy root is allowed.

- [ ] **Step 2: Run focused tests to verify RED**

Run: `(cd NSI && PYTHONPATH=.. python3 -m pytest tests/test_assemble_book.py tests/test_corpus_readonly.py tests/test_gates_corpus.py tests/test_meta_schemas.py tests/test_verify_python.py -q)`

Expected: FAIL.

- [ ] **Step 3: Implement layout injection and fail-closed coverage**

Add `--collection-root` and `COLLECTION_ROOT ?=`; before cutover, the Makefile exports `PYTHONPATH := $(abspath ..):$(PYTHONPATH)`. Read manifests/source/templates/build through `CollectionLayout` and authorize every input through an injected `SourceAuthority`. Reuse the observed-build receipt writer and durably promote a receipt/log with every 1NSI PDF. Make the student-leak gate root-aware through the explicit API/CLI above. Before creating a TNSI build directory or receipt, require complete status, exactly 12 distinct manifest chapters, and all 12 source directories. Keep variant behavior unchanged for 1NSI.

- [ ] **Step 4: Verify NSI tests without real staging**

Run: `(cd NSI && PYTHONPATH=.. python3 -m pytest tests/ -q)`

Expected: PASS. Real staging builds occur only after Task 15 creates staging.

- [ ] **Step 5: Commit**

Run:

```bash
git add NSI/scripts/common.py NSI/scripts/assemble.py NSI/scripts/gates_corpus/check_eleve_no_corrige.py NSI/Makefile NSI/tests/test_assemble_book.py NSI/tests/test_corpus_readonly.py NSI/tests/test_gates_corpus.py NSI/tests/test_meta_schemas.py NSI/tests/test_verify_python.py
git diff --cached --check
git status --short
git commit -m "[LATEX] rend les assemblages NSI root-aware"
```

### Task 13: Make inventory paths canonical while preserving baseline fingerprints

**Files:**
- Modify: `scripts/inventory_collection.py`
- Modify: `scripts/inventory_assembly.py`
- Modify: `scripts/inventory_pdf.py`
- Modify: `scripts/inventory_graph.py`
- Modify: `tests/test_inventory_collection.py`
- Modify: `audit/SOURCE_ROLES.yaml`
- Create: `docs/codex/CANONICAL_LOGICAL_PATH_COMPATIBILITY.md`

- [ ] **Step 1: Write RED temporary-canonical-tree tests**

Require inventory discovery of six canonical manuals, per-manual builds, TNSI blocked 6/12, and rejection of top-level legacy production roots when the supplied root has canonical mode. This uses a `tmp_path` fixture, not real staging. Test `--write-reports --output-dir PATH`: output must remain outside the scanned collection root, writes are atomic, and two runs to distinct directories are byte-identical.

- [ ] **Step 2: Write RED v1 fingerprint-stability tests**

For existing representative math/NSI anomalies, translate canonical physical paths to the documented legacy-stable logical v1 path and assert byte-identical fingerprints, occurrence counts, severities, owners, and dispositions. A canonical path with no reversible mapping is invalid, not omitted.

Pin at least these existing baseline examples exactly:

| Logical v1 source | Category | Occurrence | Expected fingerprint |
|---|---|---:|---|
| `NSI/chapitres/1NSI-TYPES-CONSTRUITS/exercices/1NSI-TC-EX-014.tex` | `blocking_statuses` | 1 | `0039a2dd21589133` |
| `Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/remediation/1SPE-EXPONENTIELLE-FR-R3.tex` | `blocking_statuses` | 1 | `004bbf93370edfde` |
| `Mathematiques/manuel-maths/chapitres/TSPE-SUITES-LIMITES/corriges/TSPE-SUITLIM-CO-027.tex` | `blocking_statuses` | 1 | `0051e512462af811` |
| `Mathematiques/manuel-maths/chapitres/TSPE-SUITES-LIMITES/corriges/TSPE-SUITLIM-CO-017.tex` | `unassembled_objects` | 1 | `00e2433d22373b5c` |

For the first two records also assert severity `blocking` and owners `direction_scientifique_programme` then `direction_editoriale_pedagogique`, plus their unchanged baseline dispositions.

- [ ] **Step 3: Run focused tests to verify RED**

Run: `pytest -q tests/test_inventory_collection.py -k 'canonical or logical_path or fingerprint'`

Expected: FAIL.

- [ ] **Step 4: Implement physical/logical path separation**

Output canonical physical paths. Fingerprint v1 alone uses the reversible logical mapping to avoid baseline churn. Document the compatibility boundary and a future schema-migration requirement in the named doc; do not update baseline or fingerprint version.

- [ ] **Step 5: Run the full inventory suite and commit**

Run: `pytest -q tests/test_inventory_collection.py`

Expected: PASS.

Run:

```bash
git add scripts/inventory_collection.py scripts/inventory_assembly.py scripts/inventory_pdf.py scripts/inventory_graph.py tests/test_inventory_collection.py audit/SOURCE_ROLES.yaml docs/codex/CANONICAL_LOGICAL_PATH_COMPATIBILITY.md
git diff --cached --check
git status --short
git commit -m "[AUDIT] rend l'inventaire compatible avec les chemins canoniques"
```

### Task 14: Split observed-build evidence by manual without losing records

**Files:**
- Modify: `scripts/build_manifest.py`
- Modify: `scripts/ci_audit_collection.py`
- Modify: `scripts/inventory_collection.py`
- Modify: `scripts/canonical_stage.py`
- Modify: `tests/test_build_manifest.py`
- Modify: `tests/test_ci_audit_collection.py`
- Modify: `tests/test_inventory_collection.py`
- Modify: `tests/test_canonical_stage.py`
- Modify: `audit/BUILD_PRODUCERS.yaml`

- [ ] **Step 1: Write RED split/reconciliation tests**

Given an existing global manifest, derive exactly one ordered per-manual payload for every known manual, preserve every build record once, preserve stale/empty status, and reject duplicate or unknown manual records. Recombining the six payloads must equal the original canonical build list and digest.

- [ ] **Step 2: Write RED canonical receipt tests**

Require observed evidence at `manuels/<ID>/manifests/build.json`, PDF under the same manual's `build/`, and canonical source confinement. Retain current concurrent-writer, same-size drift, symlink/hardlink, receipt recomputation, and rollback tests.

Require canonical inventory to discover and validate all six per-manual `build.json` files and reject a fallback global manifest. Add phase-aware tests for `split_build_manifest`: `stage` creates exactly six schema-valid derived entries under staging, preserves every record once, fsyncs each file/directory, and verifies recombination; `cutover` freshly verifies and promotes all six derived entries to final targets; `cleanup` removes the legacy global manifest only after all six final targets are durable. Interrupt and replay each phase independently.

- [ ] **Step 3: Run tests to verify RED**

Run: `pytest -q tests/test_build_manifest.py tests/test_ci_audit_collection.py tests/test_inventory_collection.py tests/test_canonical_stage.py -k 'manual_manifest or canonical or split or recombine'`

Expected: FAIL.

- [ ] **Step 4: Implement split storage and compatibility read**

The current global manifest remains the legacy read source until cutover. Canonical mode in `inventory_collection.py` reads/writes six per-manual files only and rejects fallback. `canonical_stage.py` implements one `split_build_manifest` operation with independently journaled `stage`, `cutover`, and `cleanup` phases. Stage records six derived IDs/output digests; cutover requires those exact staged digests and records six final digests; cleanup requires all final digests before removing the freshly verified global source. No record is silently promoted or made publishable.

- [ ] **Step 5: Verify full build-evidence tests and commit**

Run: `pytest -q tests/test_build_manifest.py tests/test_ci_audit_collection.py tests/test_inventory_collection.py tests/test_canonical_stage.py`

Expected: PASS.

Run:

```bash
git add scripts/build_manifest.py scripts/ci_audit_collection.py scripts/inventory_collection.py scripts/canonical_stage.py tests/test_build_manifest.py tests/test_ci_audit_collection.py tests/test_inventory_collection.py tests/test_canonical_stage.py audit/BUILD_PRODUCERS.yaml
git diff --cached --check
git status --short
git commit -m "[AUDIT] repartit les preuves de build par manuel"
```

- [ ] **Step 6: Verify the complete producer chunk**

Run: `PYTHONPATH=. pytest -q tests/test_canonical_assemblies.py tests/test_collection_layout.py tests/test_canonical_source_authority.py tests/test_inventory_collection.py tests/test_build_manifest.py tests/test_ci_audit_collection.py tests/test_canonical_stage.py && (cd Mathematiques/manuel-maths && PYTHONPATH=../.. python3 -m pytest tests/ -q) && (cd NSI && PYTHONPATH=.. python3 -m pytest tests/ -q)`

Expected: PASS; every assembler consumes the manifest and source authority interfaces, and TNSI still refuses 6/12 without creating `build/`.

## Chunk 4A: Stage and verify the inactive canonical tree

### Task 15: Implement isolated staging verification

**Files:**
- Create: `scripts/pdf_preflight.py`
- Create: `scripts/verify_canonical_staging.py`
- Create: `tests/test_pdf_preflight.py`
- Create: `tests/test_verify_canonical_staging.py`

- [ ] **Step 1: Write RED command-matrix tests**

Require these exact jobs: Mathématiques manuals `1SPE`, `TSPE_2026_2027`, `TCOMPL`, `TEXPERTES` in `eleve` and `professeur`; 1SPE supplements `methodes`, `evaluations`, `remediation`; 1NSI variants `complet`, `remediation`, `methodes`, `amenagee`; TNSI expected refusal code 1 with no build directory; inventory `--validate-model` code 0; two generated inventory trees byte-identical. Every job record contains command, cwd, expected/actual code, stdout/stderr digests, and output digests.

The `--verification-root` argument is the exact destination collection root, so the verifier sets `ROOT=<verification-root>` without appending another `collection_canonique`. It sets `PYTHONPATH=$ROOT/shared/collection/python:$ROOT/shared/mathematiques/scripts:$ROOT/shared/nsi/scripts`, `SOURCE_AUTHORITY_PLAN=<state-dir>/migration-plan.json`, `SOURCE_AUTHORITY_STATE=<state-dir>/migration-state.json`, `SOURCE_AUTHORITY_DISPOSITIONS=<explicit dispositions path>`, `SOURCE_AUTHORITY_STAGED_ROOT=<staged root>`, and `SOURCE_AUTHORITY_REPLICA_ROOT=$ROOT`. It uses these exact command forms and expected artifacts:

| Job | Working directory and command | Expected artifact/code |
|---|---|---|
| Math manual | `$ROOT/shared/mathematiques`; `python3 scripts/assemble_manuel.py --collection-root "$ROOT" --manual <ID> --variant <eleve|professeur>` | `manuels/<ID>/build/<name>.pdf`, code 0 |
| 1SPE supplement | `$ROOT/shared/mathematiques`; `python3 scripts/assemble_livrets.py --collection-root "$ROOT" --livret <methodes|evaluations|remediation>` | `manuels/1SPE/build/MANUEL_1SPE_<livret>.pdf`, code 0 |
| 1NSI | `$ROOT/shared/nsi`; `python3 scripts/assemble.py --collection-root "$ROOT" --book 1NSI --variant <variant>` | `manuels/1NSI/build/MANUEL_1NSI_v1<suffix>.pdf`, code 0 |
| TNSI lock | `$ROOT/shared/nsi`; `python3 scripts/assemble.py --collection-root "$ROOT" --book TNSI --variant complet` | no `manuels/TNSI/build`, code 1 and exact 6/12 reason |

Math output names are `MANUEL_1SPE_{eleve,professeur}.pdf`, `MANUEL_TSPE_2026-2027_{eleve,professeur}.pdf`, `MANUEL_TCOMPL_{eleve,professeur}.pdf`, and `MANUEL_TEXPERTES_{eleve,professeur}.pdf`. 1NSI suffixes are empty, `_remediation`, `_methodes`, and `_amenagee`.

Every successful job must create a schema-valid confined receipt at `manuels/<ID>/build/evidence/<pdf-stem>.receipt.json` and its referenced durable `log_path`. A missing/invalid receipt or log is a migration-verification failure. Run every exact PDF publication preflight below, but record its independent `publication_gate_passed` and stable reasons rather than requiring green publication status. For each Math eleve/professeur pair, run the variant-separation checker; for 1NSI, run its student-leak gate on all four variants. Any red outcome is preserved in manual status and `release-strict`, never silently skipped or promoted.

Pin these verifier APIs and reject any missing receipt/log rather than skipping a check:

```python
run_pdf_preflight(subject, pdf_path, build_receipt_path) -> JobEvidence
verify_math_variant_pair(manual_id, student_pdf, professor_pdf, student_receipt, professor_receipt) -> JobEvidence
verify_nsi_student_variant(book, variant, generated_tex, build_receipt) -> JobEvidence
run_inventory_generation(collection_root, output_dir) -> JobEvidence
```

`run_pdf_preflight` schema-validates the receipt, resolves its confined `log_path`, and calls `shared/collection/scripts/pdf_preflight.py::verify_release_pdf(request: PdfPreflightRequest) -> PdfPreflightResult`. That new focused module calls the subject's `shared/<subject>/scripts/pdf_integrity.py::verify_pdf`, `qpdf --check`, `qpdf --json`, `pdfinfo`, and `pdffonts`; it reports nonempty outlines/link annotations, required metadata fields (`Title`, `Author`, `Subject`, `Keywords`), embedded fonts, and every `Overfull \\hbox`, `Overfull \\vbox`, `NEXUS-MARGIN-ERROR`, missing glyph, or missing asset in the durable log. Math receipts additionally report existing margin-ledger evidence consumed by `margin_ledger.verify_margin_layout`. `verify_math_variant_pair` extracts both PDFs with `pdftotext -layout`, invokes `shared/mathematiques/scripts/check_variant_separation.py::verify_pair`, and reports teacher-only markers, internal IDs/placeholders, identical variants, or teacher-only receipt inputs in the student build. `verify_nsi_student_variant` invokes `shared/nsi/scripts/gates_corpus/check_eleve_no_corrige.py::scan(...)` against the explicit layout and generated TeX. Tests pin exact API arguments, qpdf JSON parsing, metadata keys, log patterns, and stable failure reasons.

Build every non-TNSI job twice from clean output directories. Migration verification passes only when both builds complete, normalized PDF/receipt digests and all publication-gate result payloads are identical, source authority is valid, and no output escapes confinement. Publication gates may remain red; evidence and manual status must preserve those exact reds. TNSI must refuse identically twice at 6/12 without creating output. This keeps consolidation possible while `release-strict` remains truthfully red.

Run deterministic inventory exactly twice to output directories outside `ROOT`:

```bash
python3 "$ROOT/shared/collection/scripts/inventory_collection.py" --root "$ROOT" --write-reports --output-dir "$EVIDENCE_TMP/inventory-1"
python3 "$ROOT/shared/collection/scripts/inventory_collection.py" --root "$ROOT" --write-reports --output-dir "$EVIDENCE_TMP/inventory-2"
```

Require equal sorted relative file sets and byte-identical contents; neither output directory may be visible to the scanned root.

- [ ] **Step 2: Run tests to verify RED**

Run: `pytest -q tests/test_pdf_preflight.py tests/test_verify_canonical_staging.py`

Expected: FAIL.

- [ ] **Step 3: Implement isolated verification**

The verifier supports closed modes `staging` and `post-cutover`. Live mode requires `--state-dir` plus `--dispositions`; finalized mode requires `--authority-evidence`, which embeds the validated plan/state/disposition payload digests. It copies the supplied tree to the requested verification root, removes only build outputs in that copy, recomputes the complete immutable-input partition digest (not the mutable build-output partition), constructs `SourceAuthority.from_staged_replica(...)` or `from_final_evidence(...)`, runs the fixed build/PDF/inventory matrix, and writes evidence outside the copy. `post-cutover` additionally runs all three canonical test trees, sorted discovered `manuels/*/source/tests/test_*.py`, `test_tex_glyph_contract.py`, `test_canonical_active_paths.py`, and the three inventory gates. It never writes into the supplied tree. Require at least 2 GiB free before the full matrix and print an expected 60-90 minute runtime warning.

- [ ] **Step 4: Verify GREEN and commit**

Run: `pytest -q tests/test_pdf_preflight.py tests/test_verify_canonical_staging.py`

Then run:

```bash
git add scripts/pdf_preflight.py scripts/verify_canonical_staging.py tests/test_pdf_preflight.py tests/test_verify_canonical_staging.py
git diff --cached --stat
git diff --cached --check
git status --short
git commit -m "[TESTS] automatise la verification du staging canonique"
```

### Task 16: Resolve blockers, stage the real tree, and reach verified state

**Files:**
- Modify when approved: `audit/CANONICAL_MIGRATION_DISPOSITIONS.yaml`
- Generate: `.migration/staged/collection_canonique/**`
- Transient then remove through verifier `--cleanup`: `.migration/verification/collection_canonique/**`
- Generate: `.migration/control/migration-plan.json`
- Generate: `.migration/control/migration-state.json`
- Generate: `.migration/control/staging-evidence.json`

- [ ] **Step 1: Regenerate real preflight on the clean tracked tree**

Run the exact Task 8 preflight command.

Expected: current HEAD/branch/status digests recorded; exit 0 or blocker exit 4; no production mutation.

- [ ] **Step 2: Resolve each blocker through explicit dispositions**

For every report row, use only:

```bash
python3 scripts/canonical_migration.py disposition --state-dir .migration/control --entry-id ENTRY_ID --decision DECISION --reason "HUMAN_REASON" --approved-by "HUMAN_APPROVER"
```

`DECISION` must be one schema enum. Add `--selected-candidate-id CANDIDATE_ID` for `select_winner`, `--selected-owner COMPONENT_ID` for `assign_owner`, and `--expected-size BYTES --expected-sha256 HEX` for every regular entry decision. Unique WIP/divergent losers use `select_winner` or `discard_approved`; ambiguous ownership uses `assign_owner`; symlinks use `materialize_approved` or `exclude_approved`; special files use `exclude_approved`. The CLI verifies the current digest/size before recording. Do not infer approvals.

After the human-approved batch is complete, run exactly:

```bash
printf '%s\0' audit/CANONICAL_MIGRATION_DISPOSITIONS.yaml > .migration/control/disposition-pathspecs.nul
git add audit/CANONICAL_MIGRATION_DISPOSITIONS.yaml
git diff --cached --check
git status --short
DISPOSITION_PARENT=$(git rev-parse HEAD)
git commit -m "[AUDIT] consigne les dispositions de migration"
python3 scripts/canonical_migration.py record-commit \
  --state-dir .migration/control \
  --phase dispositions \
  --expected-parent "$DISPOSITION_PARENT" \
  --commit HEAD \
  --pathspec .migration/control/disposition-pathspecs.nul
python3 scripts/canonical_migration.py preflight \
  --primary-root /home/alaeddine/Documents/Manuels_Nexus/.worktrees/finalisation-collection-v1 \
  --fallback-root /home/alaeddine/Documents/Manuels_Nexus \
  --rules audit/CANONICAL_PATH_RULES.yaml \
  --dispositions audit/CANONICAL_MIGRATION_DISPOSITIONS.yaml \
  --state-dir .migration/control
```

Expected: `record-commit` proves the only HEAD delta is the exact disposition file, then preflight replaces the still-operation-free `inventoried` snapshot with that committed HEAD and clean tracked status; blockers are zero. Any later disposition change requires a new state directory and the same review/commit sequence.

- [ ] **Step 3: Stage without changing legacy**

Run: `python3 scripts/canonical_migration.py stage --state-dir .migration/control`

Expected: state `staged`; frozen legacy digests unchanged; exact partition has zero blocked IDs.

- [ ] **Step 4: Run the full isolated verification matrix**

Run:

```bash
python3 scripts/verify_canonical_staging.py \
  --mode staging \
  --staged-root .migration/staged/collection_canonique \
  --verification-root .migration/verification/collection_canonique \
  --evidence .migration/control/staging-evidence.json \
  --state-dir .migration/control \
  --dispositions audit/CANONICAL_MIGRATION_DISPOSITIONS.yaml \
  --cleanup
```

Expected: exit 0; 8 Mathématiques manual builds, 3 supplements, and 4 1NSI variants pass; TNSI exits 1 with exact 6/12 reason and no build directory; two inventory outputs are byte-identical. Evidence is durable under control, and the verifier removes its exact `.migration/verification/collection_canonique` copy before returning; only immutable staging remains for cutover.

- [ ] **Step 5: Transition to verified only after evidence validation**

Run: `python3 scripts/canonical_migration.py verify-staging --state-dir .migration/control --evidence .migration/control/staging-evidence.json`

Expected: staging digest unchanged since Step 3; evidence schema/digests valid; state becomes `verified`.

- [ ] **Step 6: Review every cutover operation**

Run: `python3 scripts/canonical_migration.py report --state-dir .migration/control --only move,exclude`

Expected: every old/new path and checksum shown; no operation targets home, repository root, `.git`, `.worktrees`, or unrelated root policy/docs. `AGENTS.md`, contractual spec, `.github/`, `docs/`, and `pyproject.toml` are consumer edits, not move targets.

## Chunk 4B: Cut over and remove legacy paths

### Task 17: Perform one transactional move/default/CI cutover

**Files:**
- Move: frozen entries under `Mathematiques/manuel-maths/**`, `NSI/**`, and root collection tooling
- Modify: `.github/workflows/ci-audit-collection.yml`
- Modify: `.github/workflows/ci-mathematiques.yml`
- Modify: `.github/workflows/ci-nsi.yml`
- Remove after root equivalent exists: legacy nested `NSI/.github/workflows/ci.yml`
- Modify: `AGENTS.md`
- Modify: `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md`
- Modify: `pyproject.toml`
- Modify: canonical copies of `test_ci_audit_collection.py`, `test_ci_nsi.py`, `test_tex_glyph_contract.py`, and path-contract tests
- Create: `collection_canonique/README.md`
- Generate: `collection_canonique/INDEX.md`
- Generate: `collection_canonique/manuels/*/meta/PROVENANCE.md`
- Generate: `collection_canonique/manuels/*/meta/STATUS.yaml`
- Generate: `.migration/control/consumer-patch.json`
- Generate: `.migration/control/post-cutover-evidence.json`
- Generate: `.migration/control/git-pathspecs.nul`

- [ ] **Step 1: Freeze consumer postimages, recheck inputs, and enter maintenance**

Run:

```bash
python3 scripts/canonical_migration.py verify-frozen --state-dir .migration/control
python3 scripts/canonical_migration.py plan-consumers \
  --state-dir .migration/control \
  --output .migration/control/consumer-patch.json \
  --pathspec-output .migration/control/git-pathspecs.nul
python3 scripts/canonical_migration.py begin-cutover \
  --state-dir .migration/control \
  --consumer-plan .migration/control/consumer-patch.json \
  --git-pathspecs .migration/control/git-pathspecs.nul
```

Expected: all exit 0; the consumer plan lists exact pre/post digests for the three root workflows, root policy/contracts, `pyproject.toml`, canonical active-path tests, generated index/meta files, and nested NSI workflow removal. The NUL pathspec exactly covers every move source/target and consumer path. Their digests are bound into state `cutover_in_progress`; no concurrent production build is allowed.

- [ ] **Step 2: Apply/resume the frozen moves and consumer operations**

Run:

```bash
if test -f scripts/canonical_migration.py; then
  CONTROLLER=scripts/canonical_migration.py
else
  CONTROLLER=collection_canonique/shared/collection/scripts/canonical_migration.py
fi
PYTHONPATH="$PWD:$PWD/collection_canonique/shared/collection/python${PYTHONPATH:+:$PYTHONPATH}" python3 "$CONTROLLER" resume-cutover --state-dir .migration/control
```

Expected: all planned source/build/manifests are at canonical targets with staging-identical digests; every root consumer equals its frozen postimage; nested `NSI/.github/workflows/ci.yml` is removed only after the root workflow counterpart exists. Migration modules/tests move as the final cutover operations to `collection_canonique/shared/collection/`. State stores `controller_path=collection_canonique/shared/collection/scripts/canonical_migration.py`; an interrupted run after that move is resumed with the canonical path. State remains `cutover_in_progress` pending post-cutover evidence.

- [ ] **Step 3: Prove exact consumer postimages and active paths**

Run:

```bash
export PYTHONPATH="$PWD/collection_canonique/shared/collection/python:$PWD/collection_canonique/shared/mathematiques/scripts:$PWD/collection_canonique/shared/nsi/scripts"
python3 collection_canonique/shared/collection/scripts/canonical_migration.py verify-consumers \
  --state-dir .migration/control \
  --consumer-plan .migration/control/consumer-patch.json
test ! -e collection_canonique/shared/nsi/.github/workflows/ci.yml
```

The command compares every path to `consumer-patch.json`, verifies its recorded Git-status delta, requires canonical working directories/triggers/fonts/build uploads/test paths/inventory/manifests, and rejects active `Mathematiques/manuel-maths` or top-level `NSI/` references outside migration provenance/history fixtures.

- [ ] **Step 4: Run the exact post-move suites and record gate evidence**

Run:

```bash
export PYTHONPATH="$PWD/collection_canonique/shared/collection/python:$PWD/collection_canonique/shared/mathematiques/scripts:$PWD/collection_canonique/shared/nsi/scripts"
python3 -m pytest -q collection_canonique/shared/collection/tests
python3 -m pytest -q collection_canonique/shared/mathematiques/tests
python3 -m pytest -q collection_canonique/shared/nsi/tests
MANUAL_TESTS=$(find collection_canonique/manuels -type f -path '*/source/tests/test_*.py' -print | LC_ALL=C sort)
test -z "$MANUAL_TESTS" || python3 -m pytest -q $MANUAL_TESTS
python3 -m pytest -q collection_canonique/shared/collection/tests/test_tex_glyph_contract.py collection_canonique/shared/collection/tests/test_canonical_active_paths.py
test ! -e collection_canonique/shared/nsi/.github/workflows/ci.yml
python3 collection_canonique/shared/collection/scripts/inventory_collection.py --root collection_canonique --validate-model
python3 collection_canonique/shared/collection/scripts/inventory_collection.py --root collection_canonique --fail-on-new
set +e
python3 collection_canonique/shared/collection/scripts/inventory_collection.py --root collection_canonique --release-strict
RELEASE_STRICT_CODE=$?
set -e
test "$RELEASE_STRICT_CODE" -eq 7
POST_VERIFY_DIR=$(mktemp -d /tmp/nexus-post-cutover.XXXXXX)
python3 collection_canonique/shared/collection/scripts/verify_canonical_staging.py \
  --mode post-cutover \
  --staged-root collection_canonique \
  --verification-root "$POST_VERIFY_DIR/collection_canonique" \
  --evidence .migration/control/post-cutover-evidence.json \
  --state-dir .migration/control \
  --dispositions collection_canonique/shared/collection/audit/CANONICAL_MIGRATION_DISPOSITIONS.yaml \
  --cleanup
python3 collection_canonique/shared/collection/scripts/canonical_migration.py record-post-cutover-evidence \
  --state-dir .migration/control \
  --evidence .migration/control/post-cutover-evidence.json \
  --consumer-plan .migration/control/consumer-patch.json
```

Expected: all suites pass; `validate-model` and `fail-on-new` are 0; `release-strict` is exactly 7 for recorded real reasons including 1SPE NO-GO and TNSI 6/12. Evidence contains command, cwd, environment digest, exit code, stdout/stderr digests, tested path list, consumer digest, and resulting Git-status digest.

- [ ] **Step 5: Complete cutover only from recorded evidence**

Run:

```bash
export PYTHONPATH="$PWD/collection_canonique/shared/collection/python:$PWD/collection_canonique/shared/mathematiques/scripts:$PWD/collection_canonique/shared/nsi/scripts"
python3 collection_canonique/shared/collection/scripts/canonical_migration.py complete-cutover \
  --state-dir .migration/control \
  --consumer-evidence .migration/control/consumer-patch.json \
  --gate-evidence .migration/control/post-cutover-evidence.json
```

Expected: state `cutover`; every required move/consumer `cutover` phase complete, declared cleanup phases remain pending by design and do not block this transition, controller path canonical, consumer and gate evidence digests valid, and current Git status exactly the journaled status.

- [ ] **Step 6: Review and commit the single coherent cutover**

Run:

```bash
export PYTHONPATH="$PWD/collection_canonique/shared/collection/python:$PWD/collection_canonique/shared/mathematiques/scripts:$PWD/collection_canonique/shared/nsi/scripts"
git status --short
git diff --stat
git diff --check
python3 collection_canonique/shared/collection/scripts/canonical_migration.py report --state-dir .migration/control --only blocked
python3 collection_canonique/shared/collection/scripts/canonical_migration.py report --state-dir .migration/control --only incomplete
```

Expected: blocked report empty; incomplete report contains exactly the declared `cleanup` phases reserved for Task 18 and no pending `stage`/`cutover` phase; no unrelated WIP. Use the NUL-delimited pathspec generated from the frozen operation journal:

```bash
git add --pathspec-from-file=.migration/control/git-pathspecs.nul --pathspec-file-nul
git diff --cached --check
git status --short
CUTOVER_PARENT=$(git rev-parse HEAD)
git commit -m "[AUDIT] bascule la production vers la collection canonique"
python3 collection_canonique/shared/collection/scripts/canonical_migration.py record-commit \
  --state-dir .migration/control \
  --phase cutover \
  --expected-parent "$CUTOVER_PARENT" \
  --commit HEAD \
  --pathspec .migration/control/git-pathspecs.nul
```

Expected: the commit diff exactly matches the frozen pathspec; state now records the new HEAD and clean journaled status before reconciliation.

### Task 18: Reconcile, remove exact leftovers, and archive final evidence

**Files:**
- Remove only journal-listed excluded legacy/staging entries
- Generate: `collection_canonique/inventory/migration-report.json`
- Generate: `collection_canonique/inventory/migration-state.final.json`
- Generate: `collection_canonique/inventory/migration-authority.final.json`
- Generate: `collection_canonique/inventory/checksums.sha256`
- Regenerate: `collection_canonique/inventory/collection.json`
- Regenerate: `collection_canonique/INDEX.md`

- [ ] **Step 1: Reconcile and preview exact removals**

Run:

```bash
PYTHONPATH=collection_canonique/shared/collection/python python3 collection_canonique/shared/collection/scripts/canonical_migration.py reconcile --state-dir .migration/control
PYTHONPATH=collection_canonique/shared/collection/python python3 collection_canonique/shared/collection/scripts/canonical_migration.py remove-legacy --state-dir .migration/control --check
```

Expected: scanned entry IDs are the disjoint union of moved/excluded IDs; blocked is empty. Preview contains only journal-listed exclusions, empty legacy directories, and staging entries owned by declared cleanup phases. No verification copy remains from Task 16 or Task 17 because each verifier run used `--cleanup`.

- [ ] **Step 2: Apply per-entry removals with fresh checks**

Run: `PYTHONPATH=collection_canonique/shared/collection/python python3 collection_canonique/shared/collection/scripts/canonical_migration.py remove-legacy --state-dir .migration/control --apply`

Expected: each entry is freshly `lstat`/hashed immediately before unlink/rmdir; any drift stops with code 8 and preserves the entry. No broad recursive target is accepted. State becomes `legacy_removed` only after all entries pass.

- [ ] **Step 3: Finalize from the already-canonical control plane**

Run:

```bash
PYTHONPATH=collection_canonique/shared/collection/python python3 collection_canonique/shared/collection/scripts/canonical_migration.py finalize \
  --state-dir .migration/control \
  --collection-root collection_canonique
```

Expected: schema-valid final state/report/checksums/inventory/index are generated from the canonical controller. Define the reproducible `production_tree_digest` over sorted `(relative POSIX path, kind, mode, size, SHA-256)` records after all inventory/index/meta generation, excluding only `inventory/migration-authority.final.json`, `inventory/checksums.sha256`, `inventory/finalize-pathspecs.nul`, and documented transient verification files. `migration-authority.final.json` embeds the immutable plan entry/operation payload, final state, approved migration dispositions, their canonical digests, that non-self-referential production digest, and the relative source-authority map required by `SourceAuthority.from_final_evidence`; tests reject omission or mismatch. Generate authority next, then `checksums.sha256` last over the production partition plus the authority file while excluding itself and the transient pathspec. The archive proves the control-plane cutover completed in Task 17. `.migration/` is removed entry-by-entry only after both final archives are verified; the exact Git cleanup scope is written as NUL-delimited `collection_canonique/inventory/finalize-pathspecs.nul`.

- [ ] **Step 4: Assert old roots absent and canonical TNSI lock present**

Run:

```bash
test ! -e Mathematiques/manuel-maths
test ! -e NSI
test ! -e scripts/canonical_migration.py
test ! -e collection_canonique/shared/nsi/.github/workflows/ci.yml
test -d collection_canonique/manuels/1SPE/source
test -d collection_canonique/manuels/1NSI/source
test ! -e collection_canonique/manuels/TNSI/build
test -f collection_canonique/inventory/migration-state.final.json
test -f collection_canonique/inventory/migration-authority.final.json
```

Expected: every command exits 0.

- [ ] **Step 5: Run complete verification and second isolated build pass**

Run:

```bash
export PYTHONPATH="$PWD/collection_canonique/shared/collection/python:$PWD/collection_canonique/shared/mathematiques/scripts:$PWD/collection_canonique/shared/nsi/scripts"
python3 -m pytest -q collection_canonique/shared/collection/tests
python3 -m pytest -q collection_canonique/shared/mathematiques/tests
python3 -m pytest -q collection_canonique/shared/nsi/tests
MANUAL_TESTS=$(find collection_canonique/manuels -type f -path '*/source/tests/test_*.py' -print | LC_ALL=C sort)
test -z "$MANUAL_TESTS" || python3 -m pytest -q $MANUAL_TESTS
VERIFICATION_TMP_DIR=$(mktemp -d /tmp/nexus-canonical-verification.XXXXXX)
python3 collection_canonique/shared/collection/scripts/verify_canonical_staging.py --mode post-cutover --staged-root collection_canonique --verification-root "$VERIFICATION_TMP_DIR/collection_canonique" --evidence "$VERIFICATION_TMP_DIR/evidence.json" --authority-evidence collection_canonique/inventory/migration-authority.final.json --cleanup
python3 collection_canonique/shared/collection/scripts/inventory_collection.py --root collection_canonique --validate-model
python3 collection_canonique/shared/collection/scripts/inventory_collection.py --root collection_canonique --fail-on-new
set +e
python3 collection_canonique/shared/collection/scripts/inventory_collection.py --root collection_canonique --release-strict
RELEASE_STRICT_CODE=$?
set -e
test "$RELEASE_STRICT_CODE" -eq 7
```

Expected: tests and double-build reproducibility pass; every PDF preflight executes and reproduces its exact recorded red/green payload without status promotion; validate/fail-on-new code 0, release-strict code 7, and TNSI creates no build.

- [ ] **Step 6: Review and commit final reconciliation**

Run `git status --short`, `git diff --stat`, and `git diff --check`; inspect every generated report and deletion. Then:

```bash
git add --pathspec-from-file=collection_canonique/inventory/finalize-pathspecs.nul --pathspec-file-nul
git diff --cached --check
git status --short
git commit -m "[AUDIT] atteste l'abandon des chemins legacy"
```

## Chunk 5: Review, branch attestation, and human-only main handoff

### Task 19: Implement a read-only main-worktree collision auditor

**Files:**
- Create: `collection_canonique/shared/collection/scripts/main_handoff.py`
- Create: `collection_canonique/shared/collection/tests/test_main_handoff.py`
- Create: `collection_canonique/inventory/main-handoff-dispositions.yaml`

- [ ] **Step 1: Write RED collision and drift tests**

Fixtures must classify every untracked main entry as `identical_collision`, `divergent_collision`, `fallback_selected`, `unrelated_untracked`, or `worktree_admin`. Test an identical tracked counterpart, divergent same path, selected fallback logo, unrelated file, and `.worktrees/`. The `.worktrees/` root is one identity-bound administrative record that is pruned without recursion and is never eligible for `apply-approved`. Mutating any entry after report generation must make `verify-report` fail before cleanup.

Pin the public API as `build_report(main_root, final_root) -> HandoffReport`, `verify_report(report, main_root, final_root) -> VerificationResult`, `validate_dispositions(report, payload) -> tuple[ApprovedAction, ...]`, and `apply_approved(actions, main_root) -> ApplyResult`. Invoke both API and CLI in mutation tests. Stable CLI codes are `0` report/verify/apply success, `2` usage, `3` report drift, `4` invalid/missing disposition, and `8` fresh-check or apply failure.

- [ ] **Step 2: Run tests to verify RED**

Run: `PYTHONPATH=collection_canonique/shared/collection/python python3 -m pytest -q collection_canonique/shared/collection/tests/test_main_handoff.py`

Expected: FAIL.

- [ ] **Step 3: Implement read-only report and disposition validation**

`report` records path, class, mode, size, `mtime_ns`, SHA-256, final counterpart digest, and proposed action. `verify-report` rechecks all fields. `apply-approved` accepts only explicit versioned dispositions with path, expected size/digest, decision, reason, and human approver; it performs fresh per-file checks and rejects broad targets. Directories are represented by all descendant entries plus a final empty-directory action, never recursive deletion. It never touches `.git` or `.worktrees`.

- [ ] **Step 4: Verify GREEN and commit**

Run the focused test, then stage the three exact files, run `git diff --cached --check` and `git status --short`, and commit `[AUDIT] prepare le handoff controle vers main`.

### Task 20: Perform adversarial review and branch attestation

**Files:**
- Create: `collection_canonique/shared/collection/tests/test_canonical_adversarial.py`
- Create: `collection_canonique/inventory/MIGRATION_ATTESTATION.md`

- [ ] **Step 1: Add, run, and commit exact mutation tests**

In `test_canonical_adversarial.py`, use existing migration fixtures to inject same-size source replacement, symlink destination, missing move, duplicate PDF winner, stale manifest, TNSI 6/12 build, and changed main-only untracked file. Assert respectively exit/reason `3/source_drift`, `6/unsafe_destination`, `7/incomplete_operation`, `4/divergent_winner`, `6/stale_manifest`, `7/tnsi_incomplete_6_of_12`, and `3/main_handoff_drift`.

Run: `PYTHONPATH=collection_canonique/shared/collection/python python3 -m pytest -q collection_canonique/shared/collection/tests/test_canonical_adversarial.py`

Expected: PASS.

Run:

```bash
git add collection_canonique/shared/collection/tests/test_canonical_adversarial.py
git diff --cached --check
git status --short
git commit -m "[TESTS] ajoute les mutations adversariales de migration"
```

Expected: the adversarial test is committed before review and the branch is clean.

- [ ] **Step 2: Request review on the exact migration range**

Use `superpowers:requesting-code-review` for `4c43781..HEAD`, which includes the approved plan and every implementation commit including the adversarial tests. Address findings with `superpowers:receiving-code-review`. After each fix run its named focused test, commit the correction atomically, then rerun the three canonical suites from Task 17 Step 4 plus the adversarial test. Repeat review until no actionable finding remains.

- [ ] **Step 3: Capture final evidence SHA and exact gates**

Run:

```bash
git status --short --branch
git diff --check
git log --oneline --decorate -15
git rev-parse HEAD
python3 collection_canonique/shared/collection/scripts/inventory_collection.py --root collection_canonique --validate-model
python3 collection_canonique/shared/collection/scripts/inventory_collection.py --root collection_canonique --fail-on-new
set +e
python3 collection_canonique/shared/collection/scripts/inventory_collection.py --root collection_canonique --release-strict
RELEASE_STRICT_CODE=$?
set -e
test "$RELEASE_STRICT_CODE" -eq 7
```

Expected: clean branch; validate/fail-on-new 0; release-strict 7.

- [ ] **Step 4: Write and commit the evidence attestation**

Using `apply_patch`, record the Step 3 SHA as `evidence_sha` (not the future attestation commit), branch, entry partition, checksum digest, exact build matrix, gate codes/reasons, open P0s, TNSI 6/12 lock, review range/outcome, and pending main decision. Run `git diff --check`, stage only the attestation, then commit `[AUDIT] atteste la collection canonique sur la branche de finalisation`. Report the resulting attestation commit SHA separately.

### Task 21: Freeze an exact SHA, obtain approval, and perform the main handoff

**Files:**
- Read-only then explicitly approved cleanup: `/home/alaeddine/Documents/Manuels_Nexus`
- Remove after merged-main verification: `/home/alaeddine/Documents/Manuels_Nexus/.worktrees/finalisation-collection-v1`
- Delete after integration proof and approval: branch `finalisation/collection-v1`
- Generate: `collection_canonique/inventory/main-handoff-report.json`
- Modify after explicit path decisions: `collection_canonique/inventory/main-handoff-dispositions.yaml`

- [ ] **Step 1: Generate the exact main collision report**

From the active worktree run:

```bash
PYTHONPATH=collection_canonique/shared/collection/python python3 collection_canonique/shared/collection/scripts/main_handoff.py report \
  --main-root /home/alaeddine/Documents/Manuels_Nexus \
  --final-root /home/alaeddine/Documents/Manuels_Nexus/.worktrees/finalisation-collection-v1 \
  --output collection_canonique/inventory/main-handoff-report.json
```

Expected: every current untracked entry is listed, including `.agents/`, `.codex/`, `AGENTS.md`, the contractual specification, `docs/codex/`, both logos, and the pruned `.worktrees/` administrative root. Outside `.worktrees/`, every descendant file and empty directory is classified with exact size/digest/counterpart.

- [ ] **Step 2: Request path decisions without requesting the handoff yet**

Present every divergent/unrelated/fallback-selected path with size, digest, counterpart, and proposed decision. Ask only for explicit per-path decisions: integrate, `discard_approved`, or retain/block. Identical collisions may be proposed for exact deletion. This response authorizes recording dispositions, not cleanup, fast-forward, worktree removal, or branch deletion.

- [ ] **Step 3: Record decisions and finish every branch mutation**

For each integration decision, add unique content through a dedicated reviewed commit, rerun affected tests, regenerate the report, and repeat Step 2 for changed classifications. Retention remains a blocker. Once only approved removals remain, use `apply_patch` to write the exact records, then run:

```bash
git add collection_canonique/inventory/main-handoff-dispositions.yaml collection_canonique/inventory/main-handoff-report.json
git diff --cached --check
git commit -m "[AUDIT] consigne les dispositions du handoff main"
PYTHONPATH=collection_canonique/shared/collection/python python3 collection_canonique/shared/collection/scripts/main_handoff.py verify-report \
  --main-root /home/alaeddine/Documents/Manuels_Nexus \
  --final-root /home/alaeddine/Documents/Manuels_Nexus/.worktrees/finalisation-collection-v1 \
  --report collection_canonique/inventory/main-handoff-report.json
```

Expected: dispositions/report are committed, verification returns 0, and main is unchanged.

- [ ] **Step 4: Review, run all gates, and create the final immutable SHA**

Review the range since Task 20's attestation with `superpowers:requesting-code-review`; address and commit every finding. Run the complete Task 18 Step 5 suites, manual tests, isolated build matrix, inventory gates, and adversarial test. Update `MIGRATION_ATTESTATION.md` with the current `evidence_sha`, exact report/disposition digests, review result, matrix/gate results, and pending destructive approval, then run `git add collection_canonique/inventory/MIGRATION_ATTESTATION.md && git diff --cached --check && git commit -m "[AUDIT] reatteste le handoff main"`. After that final commit, rerun:

```bash
FINAL_SHA=$(git rev-parse HEAD)
export PYTHONPATH="$PWD/collection_canonique/shared/collection/python:$PWD/collection_canonique/shared/mathematiques/scripts:$PWD/collection_canonique/shared/nsi/scripts"
python3 -m pytest -q collection_canonique/shared/collection/tests collection_canonique/shared/mathematiques/tests collection_canonique/shared/nsi/tests
MANUAL_TESTS=$(find collection_canonique/manuels -type f -path '*/source/tests/test_*.py' -print | LC_ALL=C sort)
test -z "$MANUAL_TESTS" || python3 -m pytest -q $MANUAL_TESTS
VERIFICATION_TMP_DIR=$(mktemp -d /tmp/nexus-final-handoff.XXXXXX)
python3 collection_canonique/shared/collection/scripts/verify_canonical_staging.py --mode post-cutover --staged-root collection_canonique --verification-root "$VERIFICATION_TMP_DIR/collection_canonique" --evidence "$VERIFICATION_TMP_DIR/evidence.json" --authority-evidence collection_canonique/inventory/migration-authority.final.json --cleanup
python3 collection_canonique/shared/collection/scripts/inventory_collection.py --root collection_canonique --validate-model
python3 collection_canonique/shared/collection/scripts/inventory_collection.py --root collection_canonique --fail-on-new
set +e
python3 collection_canonique/shared/collection/scripts/inventory_collection.py --root collection_canonique --release-strict
RELEASE_STRICT_CODE=$?
set -e
test "$RELEASE_STRICT_CODE" -eq 7
PYTHONPATH=collection_canonique/shared/collection/python python3 collection_canonique/shared/collection/scripts/main_handoff.py verify-report --main-root /home/alaeddine/Documents/Manuels_Nexus --final-root /home/alaeddine/Documents/Manuels_Nexus/.worktrees/finalisation-collection-v1 --report collection_canonique/inventory/main-handoff-report.json
test "$(git rev-parse HEAD)" = "$FINAL_SHA"
test -z "$(git status --porcelain=v1)"
```

Any failure, drift, dirty branch, or later commit invalidates `FINAL_SHA` and returns to this step.

- [ ] **Step 5: Request final approval for the exact immutable SHA**

Report `FINAL_SHA`, main SHA, `git merge-base --is-ancestor main "$FINAL_SHA"`, exact main status, every approved cleanup path/digest, exact `merge --ff-only` command, worktree path, empty `.worktrees` removal, and branch deletion. Request explicit approval covering those operations and post-merge verification. State that SHA/report drift cancels approval. Make no commit or destructive change before the response.

- [ ] **Step 6: Revalidate approval and apply only approved cleanup in main**

Assert branch HEAD still equals the SHA explicitly approved by the human and `verify-report` still returns 0. From main run:

```bash
PYTHONPATH=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/finalisation-collection-v1/collection_canonique/shared/collection/python python3 /home/alaeddine/Documents/Manuels_Nexus/.worktrees/finalisation-collection-v1/collection_canonique/shared/collection/scripts/main_handoff.py apply-approved \
  --main-root /home/alaeddine/Documents/Manuels_Nexus \
  --report /home/alaeddine/Documents/Manuels_Nexus/.worktrees/finalisation-collection-v1/collection_canonique/inventory/main-handoff-report.json \
  --dispositions /home/alaeddine/Documents/Manuels_Nexus/.worktrees/finalisation-collection-v1/collection_canonique/inventory/main-handoff-dispositions.yaml
```

Expected: only approved entries and now-empty approved directories are removed; `.worktrees` is untouched; main status contains only the administrative `.worktrees/` entry.

- [ ] **Step 7: Fast-forward main to exactly the approved SHA**

Invoke `superpowers:finishing-a-development-branch`, but use only the existing main worktree and the explicitly approved merge:

```bash
APPROVED_FINAL_SHA="<40-hex SHA explicitly approved in Step 5>"
git -C /home/alaeddine/Documents/Manuels_Nexus status --short --branch
git -C /home/alaeddine/Documents/Manuels_Nexus merge --ff-only finalisation/collection-v1
test "$(git -C /home/alaeddine/Documents/Manuels_Nexus rev-parse HEAD)" = "$APPROVED_FINAL_SHA"
test "$(git -C /home/alaeddine/Documents/Manuels_Nexus/.worktrees/finalisation-collection-v1 rev-parse HEAD)" = "$APPROVED_FINAL_SHA"
test -z "$(git -C /home/alaeddine/Documents/Manuels_Nexus/.worktrees/finalisation-collection-v1 status --porcelain=v1)"
```

Any non-fast-forward, SHA mismatch, or dirty finalisation worktree stops the handoff.

- [ ] **Step 8: Verify merged main before deleting the fallback worktree**

From main, first set `APPROVED_FINAL_SHA="<the same 40-hex SHA explicitly approved in Step 5>"`, then rerun the three canonical suites, discovered manual tests, isolated build matrix, `validate-model`, `fail-on-new`, and expected `release-strict=7` exactly as in Step 4. Assert main HEAD remains `APPROVED_FINAL_SHA`, canonical 1SPE/1NSI sources exist, and TNSI has no build. Do not remove the worktree or branch unless all checks pass.

- [ ] **Step 9: Remove the redundant worktree and branch only after proof**

From main run:

```bash
git worktree remove /home/alaeddine/Documents/Manuels_Nexus/.worktrees/finalisation-collection-v1
git branch --merged main
git branch -d finalisation/collection-v1
rmdir /home/alaeddine/Documents/Manuels_Nexus/.worktrees
```

Expected: the exact worktree and fully merged branch are removed, then only the empty `.worktrees` directory is removed; all operations were covered by Step 5 approval.

- [ ] **Step 10: Verify final state from surviving main**

Working directory: `/home/alaeddine/Documents/Manuels_Nexus`.

```bash
APPROVED_FINAL_SHA="<the same 40-hex SHA explicitly approved in Step 5>"
git worktree list
git status --short --branch
test "$(git rev-parse HEAD)" = "$APPROVED_FINAL_SHA"
test -d collection_canonique/manuels/1SPE/source
test -d collection_canonique/manuels/1NSI/source
test ! -e collection_canonique/manuels/TNSI/build
python3 collection_canonique/shared/collection/scripts/inventory_collection.py --root collection_canonique --validate-model
python3 collection_canonique/shared/collection/scripts/inventory_collection.py --root collection_canonique --fail-on-new
set +e
python3 collection_canonique/shared/collection/scripts/inventory_collection.py --root collection_canonique --release-strict
RELEASE_STRICT_CODE=$?
set -e
test "$RELEASE_STRICT_CODE" -eq 7
```

Expected: one worktree on clean `main`, approved SHA preserved, one canonical production tree, validate/fail-on-new 0, release-strict 7, and no TNSI build.
