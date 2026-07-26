# Baseline 1SPE Roots of Trust Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make official baseline verification depend only on full historical
commit identifiers, evidence embedded in the historical runtime, and a
versioned tag snapshot anchored at the capture commit.

**Architecture:** The current bootstrap authenticates the artifact commit and
extracts the runtime, schema, manifest, and tag anchor from its unique parent.
The extracted v1 runtime supplies its own immutable full refs and test evidence
and validates report tags against the extracted anchor. Live refs and
worktree copies never participate in the historical verdict.

**Tech Stack:** Python 3.12, Git object plumbing, JSON Schema, pytest.

---

### Task 1: Historical refs and evidence

**Files:**
- Modify: `scripts/capture_initial_state_1spe.py`
- Modify: `tests/test_capture_initial_state_1spe.py`

- [x] Write failing tests proving short-name shadowing and current-bootstrap
  constant mutation cannot alter official verification.
- [x] Write a failing test proving internal runtime mode rejects freely
  supplied refs or evidence.
- [x] Replace official abbreviated refs with full SHA-1 values.
- [x] Remove refs and evidence from the bootstrap-to-runtime protocol.
- [x] Make the extracted runtime use and validate only its committed v1
  constants and evidence.
- [x] Run the focused tests and retain their RED then GREEN evidence.

### Task 2: Versioned tag anchor

**Files:**
- Create: `release/baseline-tags-1spe.json`
- Modify: `release/baseline-scope-1spe.json`
- Modify: `schemas/baseline_1spe.schema.json`
- Modify: `scripts/capture_initial_state_1spe.py`
- Modify: `tests/test_capture_initial_state_1spe.py`
- Modify: `README.md`

- [x] Write failing tests for coordinated artifact tag forgery, worktree
  anchor mutation, missing anchor, forbidden Git mode, and inconsistent
  snapshot hash.
- [x] Define a deterministic closed anchor with full origin/current SHAs,
  canonical tag arrays, and per-array SHA-256 values.
- [x] Record the anchor path and blob SHA-256 in official report provenance.
- [x] Extract the anchor from `capture_head`, require Git mode `100644`, and
  compare report tags directly with it.
- [x] Make official generation consume the anchor; retain live-tag discovery
  only for explicitly generic capture API calls.
- [x] Document the tag anchor as a root of trust and include it in the
  manufacturing scope.
- [ ] Run focused and complete capture tests.

### Task 3: Immutable publication and verification

**Files:**
- Modify: `validations/release-1spe/baseline.json`
- Modify: `validations/release-1spe/baseline.md`

- [ ] Commit code, tests, documentation, schema, manifest, and anchor with a
  clean worktree.
- [ ] Capture twice from that commit and compare JSON/Markdown SHA-256 values.
- [ ] Commit only the two artifacts as the unique child.
- [ ] Run `--verify-existing`, then the fresh global suite alone.
- [ ] Run diff, mode, parentage, hash, and worktree checks.
- [ ] Request a final contradictory review of both repaired P1 boundaries.
