# Historical Baseline Idempotence and Re-attestation Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the approved 186-fingerprint materialization idempotent when older registered debts have disappeared, update assembler fixtures to the current student whitelist contract, and re-attest both 1SPE PDFs without changing any visual baseline.

**Architecture:** Keep the approved policy, its 186 fingerprints, and all decision digests immutable. Build the policy-managed result from the union of active entries regenerated from raw anomalies and already-materialized managed entries whose raw anomaly has disappeared; validate that union against the immutable count, fingerprint digest, category counts, owner counts, and record digests. Active qualified fingerprints must remain a subset of the historical registry, while resolved entries from this policy or an older policy are validated and preserved field-for-field. Keep the static assembler fail-closed for student variants, but require `ELEVE_ALLOWED_TYPES` only when `eleve` is actually resolved.

**Tech Stack:** Python 3.12, pytest, YAML/JSON schemas, Git, LuaLaTeX, Poppler PDF preflight.

---

## Chunk 1: Historical materialization

### Task 1: Prove resolved historical records are preserved

**Files:**
- Modify: `tests/test_baseline_qualification.py`
- Modify: `scripts/baseline_qualification.py`

- [x] Add a synthetic regression test containing one active entry managed by the current policy, one resolved entry managed by the current policy, and one resolved entry from an older policy.
- [x] Run the test and verify it fails with `historical disposition set does not match active records`.
- [x] Replace equality with the subset invariant: every active qualified fingerprint must be registered, while additional registered fingerprints are retained as history.
- [x] Remove the assumption that every current-policy fingerprint remains active only after current-policy records already exist; a pre-materialization drift with no managed history must still fail closed.
- [x] Regenerate active current-policy entries from raw anomalies, validate and preserve resolved current-policy entries field-for-field, and validate the union against the immutable approved count/digest/category/owner contract.
- [x] Validate and preserve resolved older-policy entries field-for-field; reject a key mismatch, invalid disposition, missing conditional proof, or invalid qualification digest instead of absorbing it.
- [x] Run the focused baseline tests and verify the approved count/digest remains exactly 186 / `sha256:ac046f...`.

### Task 2: Remove the time-dependent historical checkout fixture

**Files:**
- Modify: `tests/test_baseline_qualification.py`

- [x] Replace the time-dependent historical checkout with a synthetic approved-set fixture containing active managed, resolved managed, and older-policy history.
- [x] Simulate the pre-materialization state using matching approved pre-materialization digests and no current-policy history.
- [x] Materialize once, then remove one managed raw anomaly, mark the remaining records qualified, and rerun with changed observed digests.
- [x] Assert the second disposition payload is field-for-field equivalent to the first and any tampered resolved managed record is rejected.

## Chunk 2: Static assembler fixtures

### Task 3: Scope the whitelist requirement to student variants

**Files:**
- Modify: `tests/test_inventory_collection.py`
- Modify: `scripts/inventory_assembly.py`

- [x] Add a failing test proving a professor-only manual assembler remains valid without `ELEVE_ALLOWED_TYPES`.
- [x] Verify the test fails because the assembler is rejected.
- [x] Require the whitelist only when `eleve` is among the resolved variants.
- [x] Add `ELEVE_ALLOWED_TYPES` to every fixture that declares the student variant.
- [x] Verify missing, empty, dynamic, or malformed student whitelists still fail closed whenever `eleve` is resolved, including through literal `argparse` choices; unresolved/empty variants remain invalid independently.

## Chunk 3: Verification and observed builds

### Task 4: Validate and commit the inventory fixes

**Files:**
- Modify generated audit reports after source commits.

- [x] Run Ruff, mypy, `git diff --check` (all green as of commit `f9ad08b`).
- [ ] Run all baseline and inventory tests. (blocked by the same stale-manifest issue below: `build_inventory()` raises `source_digest du manifeste de build incohérent` on every invocation while `audit/BUILD_MANIFEST.json` still references `git_sha 169fc804...`, a commit that predates the margin-solver work merged since.)
- [x] Commit baseline idempotence and fixture-contract changes separately. (pre-existing, done in commits before this session — unrelated content-only fixes landed as `f9ad08b`.)
- [ ] **BLOCKED** — Invalidate the stale observed-build manifest and refresh its empty envelope. `build_manifest.py --refresh-empty` only accepts an *already-empty* manifest (`refresh interdit: le manifeste doit être strictement vide`); there is no CLI path today to move a non-empty, source-mismatched manifest to empty. Every inventory/digest computation path (`_build_inventory`, including the `_EMPTY_MANIFEST_REFRESH_CAPABILITY` bootstrap path) requires reading and validating the *existing* manifest first, which is exactly what's stale — a genuine chicken-and-egg gap in the current tooling, not a usage error. This needs a new, deliberately reviewed capability (e.g. an explicit `--invalidate-stale-manifest` path with its own preconditions/tests) added to `build_manifest.py` in a follow-up session; do not hand-write `audit/BUILD_MANIFEST.json` to route around it.

### Task 5: Re-attest professor and student PDFs

**Files:**
- Update: `Mathematiques/manuel-maths/config/reproducible-build.json`
- Update: `Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf`
- Update: `Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf`
- Update: `audit/BUILD_MANIFEST.json`
- Update generated audit reports.

- [x] Fix the reproducible epoch to a committed source state. (`config/reproducible-build.json` pinned to `f9ad08b`, commit `2a67348`.)
- [x] Build and version the professor PDF; rebuild and prove byte identity (`sha256:ff355302...` identical across two independent compiles, commit `2a67348`). Both `--variant professeur` and `--variant eleve` now compile end-to-end without a single LuaLaTeX error for the first time since the margin-solver commits landed (was failing on ~90 distinct oversized/malformed margin notes across every 1SPE chapter plus a handful of TSPE ones — see commits `fb3867a`, `6b29a46`, `338f5fa`, `f9ad08b`).
- [ ] **BLOCKED on the manifest gap above** — `--record-observed` itself fails (`build manifest refusé: dérivation du receipt refusée: InventoryError`) because deriving receipt evidence calls `build_inventory()`, which hits the same stale-manifest wall. No receipt has been recorded yet for either variant.
- [x] Build and version the student PDF (commit `a956a2b`); byte-identity re-check not yet attempted (same blocker would apply).
- [ ] Regenerate audit reports without visual-baseline writes. (not attempted — blocked upstream.)
- [ ] Run the complete pytest suite and all Phase 0 gates. (last full run pre-dates these fixes: 3289 passed / 10 failed, all 10 failures traced to the same stale-manifest cause.)
- [ ] Prove in read-only mode that `git diff --name-only` contains no visual-baseline, validation PNG, or visual review path.
- [ ] Confirm `release-strict` remains red only for explicit publication debt. (currently red for the wrong reason — `inventaire_indisponible` — not real 1SPE debt; will only be meaningful once the manifest is unblocked.)

**2026-08-05 session summary:** the actual manual-authoring blocker (LaTeX compile failures) is resolved; both PDFs build cleanly. The remaining blocker is infrastructural (build-manifest bootstrap gap), independent of manual content, and should be the very next atomic task.
