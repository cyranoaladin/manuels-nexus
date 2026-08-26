# T3 First Vertical Content Wave Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development to execute this plan task-by-task, with specification review followed by code/content-quality review.

**Goal:** Close the first vertical T3 wave for `1SPE-EXPONENTIELLE`, `1SPE-SUITES`, `1SPE-VARIABLES-ALEATOIRES`, and `TNSI-PROJET`, while independently sealing the official mandatory-atom denominator and completing the read-only style runtime map.

**Architecture:** Treat every chapter as a vertical release slice: programme mapping, content gaps, assessment, remediation, science, pedagogy, editorial quality, variants, build evidence, and current receipts are one closure unit. Generated ledgers remain derived from canonical sources and existing producers; human approvals remain external facts and are never inferred from machine review. Technical-trust gates are checked after every relevant lot and full suites are reserved for the completed-wave milestone.

**Tech Stack:** Python 3, pytest, YAML/JSON schemas, LaTeX/LuaLaTeX, existing repository audit/build producers, SymPy where mathematically useful.

---

## Task 0: Freeze the Wave A authorization and debt scope

**Files:**
- Create: `audit/T3_WAVE_A_INITIAL_FREEZE.json`
- Create: `audit/T3_WAVE_A_INITIAL_FREEZE.md`
- Create: `scripts/build_t3_wave_a_initial_freeze.py`
- Test: `tests/test_t3_wave_a_initial_freeze.py`

- [ ] Record `WAVE_A_SOURCE_SHA=7b6140920c1e09d359bc7bf0d837192f3fe455da`, the exact residual-13 digest `sha256:1abe51ad406752b1e09996020c1afb2db3982ac2741cf98ed7b2118f302ace98`, and the exact 2/5/4/2 partition from that immutable Git tree. Because the first Suites TDD lot was already present when the artefact was materialized, record this chronology explicitly and enumerate the post-freeze worktree diff; never claim the file was written before those edits.
- [ ] Freeze the exact 89 previously qualified fingerprints and a deterministic set digest; identify their Wave A intersection explicitly.
- [ ] Add a failing integrity test before creating the freeze artefact; require disjoint sets and `UNKNOWN=0`.
- [ ] At the end of the wave, reconcile exactly `INITIAL + DISCOVERED = FIXED + REMOVED + REVIEW_CLOSED + RESIDUAL` with all non-null intersections reported and no double counting.

## Task 1: Seal the official source denominator independently

**Files:**
- Create: `audit/OFFICIAL_SOURCE_SEGMENT_LEDGER.json`
- Create: `audit/OFFICIAL_SOURCE_SEGMENT_LEDGER.md`
- Create: `audit/OFFICIAL_ATOMIZATION_SECOND_PASS.json`
- Create: `audit/OFFICIAL_ATOMIZATION_SECOND_PASS.md`
- Create: `scripts/build_official_atomization_second_pass.py`
- Modify only if source-ledger fields require it: `scripts/build_official_source_segments.py`
- Test: `tests/test_official_source_segments.py`
- Test: `tests/test_official_atom_definitions.py`
- Test: `tests/test_official_atomization_second_pass.py`

- [ ] Add failing assertions for all 985 source segments, explicit no-atom reasons, `UNKNOWN = 0`, and exact segment-to-atom traceability.
- [ ] Implement the second pass in a separate producer that imports no first-pass extraction or normalization code; compare first and second pass only through their serialized outputs.
- [ ] Add mutations proving that a changed/dropped/duplicated first-pass atom is detected by an unchanged second pass.
- [ ] Prove `MANDATORY_SEGMENT_UNREPRESENTED`, `PHANTOM_ATOM`, `DUPLICATE_ATOM`, `AMBIGUOUS_ATOM`, `WRONG_YEAR_ATOM`, and `MANDATORY_CLASSIFICATION_DISAGREEMENT` are all zero; adopt any demonstrated denominator change rather than preserving 596.
- [ ] Run `pytest -q tests/test_official_source_segments.py tests/test_official_atom_definitions.py tests/test_official_atomization_second_pass.py`.

## Task 2: Complete the read-only runtime-style forensic map

**Files:**
- Modify: `audit/CANONICAL_STYLE_RUNTIME_REGISTRY.json`
- Modify: `audit/CANONICAL_STYLE_RUNTIME_REGISTRY.md`
- Create: `audit/STYLE_CONSUMER_GRAPH.json`
- Create: `audit/STYLE_CONSUMER_GRAPH.md`
- Create: `audit/STYLE_DUPLICATE_FORENSICS.json`
- Create: `audit/STYLE_DUPLICATE_FORENSICS.md`
- Modify: `scripts/build_canonical_style_runtime_registry.py`
- Test: `tests/test_canonical_style_runtime_registry.py`

- [ ] Add failing tests requiring every `.cls`, `.sty`, macro file, icon/figure set, and font configuration to have canonical path, consumers, runtime state, duplicate relation, and lifecycle classification.
- [ ] Derive the consumer graph from build/manifests and source includes without deleting or redirecting runtime files.
- [ ] Account exactly for the current 21 duplicate physical files, 18 groups, and 16 potentially noncanonical runtime paths, reporting disagreement rather than concealing it.
- [ ] Run `pytest -q tests/test_canonical_style_runtime_registry.py`.

## Task 3: Build Wave A object and governance ledgers

**Files:**
- Modify: `audit/RESIDUAL_13_SUNSET_LEDGER.json`
- Modify: `audit/RESIDUAL_13_SUNSET_LEDGER.md`
- Modify: `audit/DEBT_BURNDOWN.json`
- Modify: `audit/DEBT_BURNDOWN.md`
- Create: `audit/T3_WAVE_A_OBJECT_LEDGER.json`
- Create: `audit/T3_WAVE_A_OBJECT_LEDGER.md`
- Test: add focused tests under `tests/` following the closest existing ledger test pattern.

- [ ] Inventory 100% of publishable objects in the four Wave A chapters and map all 13 residual fingerprints plus the exact Wave A intersection of the frozen previous-89 set.
- [ ] Determine the repository-authoritative human-review granularity by schema/policy; record pending requirements without creating approval receipts. Require separate programme/pedagogy and science reviewers, `reviewer != modifier/generator`, and review provenance. If an authoritative human receipt is required but absent, report `PENDING_HUMAN`, never `COMPLETE`.
- [ ] Add failing integrity tests for complete object coverage, no `UNKNOWN`, current source hashes, and no administrative closure.
- [ ] Generate the ledgers and make the focused tests pass.

## Task 4: Close `1SPE-EXPONENTIELLE` vertically

**Files:**
- Modify as proved necessary: `Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/**`
- Modify: chapter-specific review evidence under `audit/`
- Test: focused chapter/science/QCM/remediation tests under `tests/`

- [ ] Establish programme, QCM, remediation, EX/CO, variant, science, pedagogy, editorial, richness, and progression findings for every publishable object. For every capacity, require an exact-ID/current-SHA matrix of the eleven Nexus links, blind resolution evidence, mutation evidence, A/B assessments, and student/teacher inclusion manifests; missing links must be exactly zero before closure.
- [ ] For each deterministic defect, first add a failing regression test, then apply the minimum source correction and rerun the focused test.
- [ ] Independently review `1SPE-EXPO-COURS-C5` and `1SPE-EXPO-COURS-C5-ALGORITHMES` with distinct modifier, science-review, and programme/pedagogy-review identities; close their debt only if all required current evidence and authoritative receipts exist, otherwise place them in the canonical human-review packet as `PENDING_HUMAN`.
- [ ] Build/render both affected variants, inspect logs and pages, then run inventory/check, `--validate-model`, and `--fail-on-new`.

## Task 5: Close `1SPE-SUITES` vertically

**Files:**
- Modify as proved necessary: `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/**`
- Modify: `audit/CHAPTER_READINESS_1SPE_SUITES.json`
- Modify: chapter-specific review evidence under `audit/`
- Test: focused chapter/science/QCM/remediation tests under `tests/`

- [ ] Audit every publishable object, all EX/CO pairs, figures/tables, QCM diagnostics, remediation loops, variants, editorial quality, task richness, and progression. Require the exact-ID/current-SHA eleven-link Nexus matrix, blind resolution, mutations, A/B assessments, and variant manifests for every capacity.
- [ ] TDD-close deterministic findings, including the five residual objects and any previous qualified debt in the chapter.
- [ ] Independently verify the complete error→help→remediation→correction→autonomous exercise→revalidation loop for `1SPE-SUITES-RE-C8`.
- [ ] Build/render both variants and run the focused trust gates.

### Task 5A: Bound and remove the 1SPE-SUITES wrong-year P0 before vertical closure

**Files:**
- Create: `audit/1SPE_SUITES_WRONG_YEAR_P0_FORENSICS.json`
- Create: `audit/1SPE_SUITES_WRONG_YEAR_P0_FORENSICS.md`
- Create: `scripts/build_1spe_suites_wrong_year_p0_forensics.py`
- Test: `tests/test_1spe_suites_wrong_year_p0_forensics.py`
- Modify only after claim classification: the exact `1SPE-SUITES` EX/CO sources proved wrong-year

- [ ] First commit the pre-existing Wave A freeze, independent official atomization proof, scientific edge-case corrections, and CR-017 LaTeX fix in separate atomic commits. Record a clean `PRE_P0_REWRITE_SHA`; do not rebase or switch an unfrozen WIP.
- [ ] Record `CURRENT_INTEGRATION_SHA=git rev-parse audit/adversarial-reconciliation-2026` and prove whether it is an ancestor, descendant, or divergent from the working branch before deciding on a side-car branch.
- [ ] Produce claim-level forensics for the exact 19-object union. Distinguish `LOG_OR_FORMAL_THRESHOLD_SET`, `FORMAL_LIMIT_CONVERGENCE_SET`, their exact intersection, student-statement versus correction-only versus both, and classify every relevant passage as `KEEP_AS_IS`, `REWRITE_TO_1SPE`, `OPTIONAL_TERMINALE_EXTENSION`, or `DELETE_INVALID`; require `UNKNOWN=0` and `|UNION|=19`.
- [ ] Preserve numerical/algorithmic threshold search and intuitive limit conjecture. Remove logarithms as a solving tool, formal convergence theorems, and formal passage to a limit from the mandatory Première path. Do not change a conforming exercise statement when only its correction is wrong-year.
- [ ] Start with one representative threshold pair and one representative formal-limit pair. Add contextual failing tests first, rewrite minimally, independently review science/programme/exercise-solution alignment, and only then apply the proved patterns to the remaining exact claims.
- [ ] Reconcile every EX/CO pair for questions, data, notation, methods, answers, units, rounding, barème, and capacities. Require `STALE_CORRECTION=0`, `TERMINALE_METHOD_IN_1SPE_SOLUTION=0`, and `QUESTION_WITHOUT_VALID_SOLUTION=0`.
- [ ] Independently review all 19 objects for science, programme, exercise-solution alignment, pedagogy, and editorial quality. A machine review does not create a human approval receipt.
- [ ] Build all relevant chapter variants and affected 1SPE student/teacher variants, raster-inspect every affected page at >=150 dpi, and require zero visible overflow/underflow, missing glyph, undefined reference, or student/teacher leak.
- [ ] Commit the P0 lot atomically, record `P0_FIX_SOURCE_SHA`, refresh canonical derived artefacts, and replay inventory/check, validate-model, fail-on-new, release-strict, structural invariants, and affected suites without modifying baseline, policy, D7, or approval receipts.

## Task 6: Close `1SPE-VARIABLES-ALEATOIRES` vertically

**Files:**
- Modify as proved necessary: `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/**`
- Modify: chapter-specific review evidence under `audit/`
- Test: focused chapter/science/QCM/remediation tests under `tests/`

- [ ] Audit the complete chapter for programme, probability definitions/hypotheses/calculations, EX/CO consistency, QCM, remediation, pedagogy, editorial quality, variants, richness, and progression. Require the exact-ID/current-SHA eleven-link Nexus matrix, blind resolution, mutations, A/B assessments, and variant manifests for every capacity.
- [ ] TDD-close deterministic findings and independently review the four residual objects.
- [ ] Build/render both variants and run the focused trust gates.

## Task 7: Close `TNSI-PROJET` vertically

**Files:**
- Modify as proved necessary: `NSI/chapitres/TNSI-PROJET/**`
- Modify: chapter-specific review evidence under `audit/`
- Test: focused NSI model/code/project tests under `tests/`

- [ ] Audit every project object, executable code path, scaffold classification, programme mapping, pedagogy, editorial quality, variants, and visual layout. Require the exact-ID/current-SHA eleven-link Nexus matrix, blind resolution, mutations, A/B assessments, and variant manifests for every capacity.
- [ ] TDD-close deterministic findings and independently review `TNSI-PROJET-ANNUEL` and `TNSI-PROJET-CONTRACT`.
- [ ] Build/render student and teacher variants A/B and run the focused trust gates.

## Task 8: Freeze the completed first wave and verify invariants

**Files:**
- Create: `audit/T3_FIRST_VERTICAL_CONTENT_WAVE.json`
- Create: `audit/T3_FIRST_VERTICAL_CONTENT_WAVE.md`
- Test: `tests/test_t3_first_vertical_content_wave.py`
- Modify: applicable chapter-readiness, debt-sunset, QCM, remediation, programme, and release-strict derived reports.

- [ ] First add a failing acceptance test for the two wave-checkpoint artefacts, then generate them through a canonical producer.
- [ ] Regenerate all affected canonical audits sequentially without changing anomaly baseline, qualification policy, D7, or human approvals; prove these authorities unchanged by path diff and content hash.
- [ ] Require current receipts for science, pedagogy, editorial, assessment, year, variant, and visual dimensions before marking a chapter complete or an atom `FULL`.
- [ ] For every capacity in all four Wave A chapters, require all eleven Nexus roles to be non-empty and traced by exact ID/current SHA, with `missing_link_count=0`; any missing link prevents chapter completion.
- [ ] Require repository root, Math, and NSI full suites to have `failed=0` and `errors=0`; require `--validate-model` and `--fail-on-new` to pass and all T1 structural invariants to remain zero.
- [ ] Require `--release-strict` to remain deterministically `BLOCKED` while out-of-wave release debt exists, with exact reason IDs, counts, and digest. This red gate neither blocks wave closure nor proves publish readiness.
- [ ] Require affected student/teacher builds A and B to succeed and match, with current manifests, visual receipts, and zero visible layout defect.
- [ ] Record the exact release-strict reason IDs/digest delta, debt sunsets, QCM coverage/audit totals, remediation state, atom denominator/FULL count, style map, and build evidence at the final source SHA.
- [ ] Reconcile the frozen 13 and previous-89 intersections exactly; request independent specification and content/code-quality reviews of the complete diff and correct every proved issue before reporting `FIRST_VERTICAL_CONTENT_WAVE_COMPLETE`, which remains explicitly distinct from `FINAL_PUBLISH_READY`.

## Execution ownership and atomicity

- [ ] Within Tasks 4–7, split work into exclusive lanes and atomic commits/lots: scientific correction plus regression test; programme mapping; pedagogy/remediation/QCM; editorial/layout; then derived evidence. Do not mix these intents.
- [ ] A chapter worker owns only its chapter sources and focused tests. Chapter workers must not regenerate shared ledgers, baselines, policy, D7, or human-approval artefacts.
- [ ] Integrate and regenerate shared derived reports sequentially in Task 8 after chapter lanes are reviewed, preventing shared-file collisions.
