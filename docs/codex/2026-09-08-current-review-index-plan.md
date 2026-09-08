# Current review index implementation plan

> For agentic workers: execute the approved bounded task in the current worktree; parent review precedes the centralised commit.

**Goal:** derive one current review row for each canonical content object without promoting historical evidence or creating human approvals.

**Architecture:** `build(root, inventory)` reads the fresh canonical inventory and current sources. Historical queues and retired versions are separate evidence references. Only explicit independent reviews bound to the current source, semantic digest and required source dependencies may close a review dimension as `VALIDATED_BY_EVIDENCE`.

**Tech stack:** Python, existing inventory and semantic normalisation helpers, JSON, pytest.

- [x] Add mutation tests for duplicate objects, omitted sources, rewritten content, dependency changes, reused retired identifiers, unsupported review dimensions and forged human approval.
- [x] Execute the tests before implementing the new producer and record the expected failures.
- [x] Add `scripts/build_current_review_index.py` with a pure injectable build function and a command using a freshly built inventory by default.
- [x] Add the empty independent review ledger and its documented record contract; absence of a review remains pending.
- [x] Run focused tests, generate only the new index, and verify a second independent generation compares equal by content. HEAD remains observation metadata.
- [x] Parent review: inspect the diff and evidence before a dedicated local commit. No release receipt, human signature, freeze or promotion is produced.

The first index does not adopt the path-only non-formalisable reviews or the satellite containment heuristic as scientific proof. Their references remain visible with the reason they were not credited. A reused path or object ID does not inherit the retired version's evidence.


Execution evidence (2026-09-08): the missing producer and controlled source,
dependency, authority, data/code-applicability and consumer-routing mutations
were observed red before correction. The final targeted mutation and fixture
selection passed (47 tests). Two full in-memory generations over a fresh
inventory matched by content; the captured worktree contained 3445 objects.
Current views explicitly carry base HEAD, worktree status and input digests.
The development capture is in `/tmp/nexus_current_review_index_candidate.json`;
no tracked current index was deposited while scientific sources were changing.

Consumers NEW_AUTHORING and NON_FORMALIZABLE now recompute the index rather
than trusting its deposited JSON. Legacy closure classifications are references
to the immutable takeover snapshot, so generated consumers cannot become cyclic
inputs to the index. Code applicability covers mathematics and NSI; data review
requires an explicit applicability examination. Neither dimension closes from
absence of a filename pattern.

The independent ledger is deliberately empty in this implementation. New
reviews must carry actual independent rationales and bind the current source,
semantic digest and chapter dependencies. Existing 1NSI records were not
silently imported: its own validation currently rejects the obsolete protocol
digest. Historical path-only mathematical declarations, substring containment
and copied QCM states do not establish a current review binding.


Final dependency amendment: the index follows local TeX input/listing/figure
references transitively, hashes images and Lua resources, and binds each
manual's official programme coverage mapping. Missing, ambiguous, unresolved or
out-of-repository references fail explicitly. Source/dependency sets are checked
again after reading. Four additional controlled mutations (figure, programme
mapping, escaping path, missing listing) passed after the required red run.

Final affected-module run: 110 passed, 4 failed. The remaining failures concern
the non-regenerated disposition ledger, the historical build-manifest fixture,
the historical fixed SUITES receipt count, and the stale course ownership input
to the publish matrix. The assertions were not weakened. See the development
run log `/tmp/nexus_review_delivery_final_tests.log` during this session; these
runtime captures are not release receipts.

Parent counter-review (2026-09-08): removed credit from old aggregate capacity
signatures and answer counts; required correction alignment for hints, adapted
exercises and remediations; retained pending findings as unknown instead of
zero. Current dependencies include the actual programme registry, normative
source bytes, the TSPE alias mapping, and execution protocol helpers. Source
mutations for these omissions failed before correction. The final index module
run passed 38 tests; Ruff passed. These are development checks, not full-suite
or release evidence. The former temporary capture predates these amendments
and must not be presented as current.
