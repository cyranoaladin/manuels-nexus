# Green P0 Student/Teacher Separation Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the fifteen approved student-separation contracts green while preserving all teacher QCM diagnostics and marking schemes, resolving all 63 provisional method links, and producing four explicitly intermediate, visually approved PDFs.

**Architecture:** Capture the clean, versioned tip of `wave0/p0-green-launch` after its three implementation plans are committed, and create the implementation branch/worktree from that dynamic SHA; `114c4acc525b31153e601e93ab121d857a3eaff2` remains only its required launch ancestor. Keep JSON as the sole source for the eight mixed QCMs, generate one student body and one teacher diagnostics body, and make assembler and maquette invoke one explicit class-level diagnostics-transition command whose body owns the bilateral page/rubric rendering. Share one pure student-text policy between the assembler and recorder, prove every method call bijectively from a source token and saved coordinate to one PDF annotation and destination, and keep disciplinary, Python, pedagogy, LaTeX, audit, and PDF changes in separate commits.

**Tech Stack:** Python 3, pytest, JSON/YAML `% META:` records, LuaLaTeX (three passes), LaTeX/hyperref, pikepdf, qpdf, Poppler (`pdftotext`, `pdfinfo`, `pdffonts`, `pdftoppm`), ImageMagick (`compare`, `montage`), Git worktrees.

---

## Preconditions and immutable contracts

- Approved design: `docs/superpowers/specs/2026-08-13-green-p0-separation-eleve-design.md`.
- Wave 0 orchestrator: `docs/superpowers/specs/2026-08-13-wave-0-green-p0-launch-design.md`.
- Approved Red milestone: `c50e455ec1bd3e0506e482e0e475abcd5451e5bb`.
- Required launch ancestor: `114c4acc525b31153e601e93ab121d857a3eaff2`.
- Implementation base: the clean, dynamically captured tip of `wave0/p0-green-launch` after all three approved Green plans are versioned; call this SHA `<launch-base>` throughout.
- Implementation branch: `green/p0-student-separation`.
- Worktree: `/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation`.
- The manual remains **NO-GO publication**. This plan neither clears overflow debt nor changes PDF metadata, global bookmarks, global links, tagging, observed manifests, anomaly baselines, or release gates.
- Never use `--record-observed` in this worktree. Never update `validations/v5*`, `audit/ANOMALIES_BASELINE.json`, or `audit/BUILD_MANIFEST.json` to make a gate pass.
- Stop on any unexpected JSON/TeX QCM divergence, mathematical ambiguity, missing link target, changed v5 PNG, unapproved visual change, new teacher-content loss, weakened/skipped test, or tool failure.
- After every implementation task, use `superpowers:requesting-code-review`; before applying review feedback, use `superpowers:receiving-code-review`. A disciplinary reviewer must not be the author of the two QCM corrections.
- Every Bash block is self-contained: it enables `set -euo pipefail`, assigns
  the absolute worktree to `target`, changes to it, and asserts
  `test "$(pwd -P)" = "$target"` before any other command. Do not rely on a
  shell variable or cwd established by a previous checkbox.
- Every edit checkbox uses `apply_patch` only. Its patch header must name the
  exact absolute target, for example
  `*** Update File: /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation/<repository-relative-path>`.
  A relative patch target, an unresolved variable, a glob, or an edit outside
  the task's `Files` allowlist is a hard stop.

## File map

**Create**

- `scripts/student_text_policy.py` — pure, repository-wide student-text policy.
- `tests/test_student_text_policy.py` — shared policy API, exact reasons, false-positive and mutation contracts.
- `Mathematiques/manuel-maths/tests/test_qcm_math_p0.py` — independent regression contracts for Exponentielle Q9 and Produit scalaire Q8.
- `Mathematiques/manuel-maths/tests/test_training_links.py` — exhaustive source, assembler, AUX, and PDF-link contracts for the 63 calls.
- `scripts/build_wave0_separation_evidence.py` — deterministic intermediate visual-evidence and manifest builder; it never approves.
- `tests/test_wave0_separation_evidence.py` — closed schema, hash, path, identity, and failure tests for the evidence manifest.
- `audit/wave0-green-p0-separation-qcm-migration-2026-08-13.json` — exhaustive eight-QCM pre-generation comparison and independent decision.
- `audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json` — human decision and exact before/after hashes for four canonical PDFs.
- `audit/visual-wave0-green-p0-separation-2026-08-13/pages/` — only affected before/after page PNGs and diffs.
- `audit/visual-wave0-green-p0-separation-2026-08-13/contact-sheets/` — four review sheets.
- Eight generated `Mathematiques/manuel-maths/chapitres/<chapter>/diagnostics/<name>-QCM-DIAGNOSTICS.tex` files.

**Modify**

- `Mathematiques/manuel-maths/scripts/assemble_manuel.py` — shared policy delegation, diagnostics routing and bilateral boundaries, method-target derivation, chapter context, labels, and link rendering.
- `scripts/build_manifest.py` — delegate its existing public/private wrapper to the shared policy.
- `Mathematiques/manuel-maths/scripts/build_qcm_tex.py` — validate and atomically maintain both JSON-derived TeX outputs.
- `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py` — policy delegation, object routing, rubric boundaries, target mapping, and master contracts.
- `tests/test_build_manifest.py` — recorder delegation and identical-policy contracts.
- `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py` — eight-source migration table and exact two-output checks.
- `Mathematiques/manuel-maths/build/maquette-v5/manifest.json` — separate `student` and `diagnostics` QCM paths/hashes.
- `Mathematiques/manuel-maths/build/maquette-v5/maquette.tex` — include both bodies with the same semantic bilateral boundary.
- `Mathematiques/manuel-maths/scripts/build_maquette_v5.py` — validate the two-file manifest shape without weakening existing checks.
- `Mathematiques/manuel-maths/tests/test_maquette_v5.py` — two hashes, body equivalence, boundary, page-count, and immutable PNG contracts.
- `Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/qcm/1SPE-EXPONENTIELLE-QCM.tex` — transitional Q9 correction before regeneration.
- `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/qcm/1SPE-PRODUIT-SCALAIRE-QCM.json` — canonical Q8 single-answer correction.
- `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/qcm/1SPE-PRODUIT-SCALAIRE-QCM.tex` — matching transitional Q8 correction before regeneration.
- The other six mixed QCM TeX files under their existing `qcm/` folders — replace them only with generated student bodies.
- `Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/evaluations/TSPE-DERIVATION-CONVEXITE-EV-{A,B}.tex` — public student presentation without ID or points.
- `Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/evaluations/TSPE-DERIVATION-CONVEXITE-EV-{A,B}-corrige.tex` — teacher 20-point/4×5-point marking schemes.
- `Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls` — required `\nxQcmDiagnostics{<path>}` bilateral-boundary interface, then chapter-scoped `\refExos` hyperlink rendering.
- `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls` — load hyperref once and provide the strict base `\refExos` contract.
- Four tracked canonical PDFs under `Mathematiques/manuel-maths/build/MANUEL_1SPE/` and `Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/` — only after explicit human visual approval.
- `README.md` — replace only Wave 0 separation statements proved by this lot; retain NO-GO and remaining red gates.

## Chunk 1: Isolated workspace, sharper Red contracts, and disciplinary prerequisite

### Task 1: Create and attest the implementation worktree

**Files:**
- Read: `AGENTS.md`
- Read: `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md`
- Read: `docs/superpowers/specs/2026-08-13-green-p0-separation-eleve-design.md`
- Read: `docs/superpowers/specs/2026-08-13-wave-0-green-p0-launch-design.md`

- [ ] **Step 1: Confirm the documentation base is immutable**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/wave0-p0-green-launch
cd "$target"
test "$(pwd -P)" = "$target"
launch_worktree=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/wave0-p0-green-launch
git -C "$launch_worktree" status --short --branch
test -z "$(git -C "$launch_worktree" status --porcelain)"
test "$(git -C "$launch_worktree" branch --show-current)" = \
  wave0/p0-green-launch
launch_base=$(git -C "$launch_worktree" rev-parse HEAD)
git -C "$launch_worktree" merge-base --is-ancestor \
  114c4acc525b31153e601e93ab121d857a3eaff2 "$launch_base"
for path in \
  docs/superpowers/specs/2026-08-13-wave-0-green-p0-launch-design.md \
  docs/superpowers/specs/2026-08-13-green-p0-separation-eleve-design.md \
  docs/superpowers/specs/2026-08-13-green-p0-programme-tspe-design.md \
  docs/superpowers/specs/2026-08-13-green-p0-overflow-preflight-design.md \
  docs/superpowers/plans/2026-08-13-green-p0-separation-eleve.md \
  docs/superpowers/plans/2026-08-13-green-p0-programme-tspe.md \
  docs/superpowers/plans/2026-08-13-green-p0-overflow-preflight.md
do
  git -C "$launch_worktree" cat-file -e "$launch_base:$path"
done
printf 'launch_base=%s\n' "$launch_base"
git branch --list green/p0-student-separation
git worktree list --porcelain
```

Expected: documentation worktree and index are clean, branch is exactly
`wave0/p0-green-launch`, `<launch-base>` descends from `114c4acc`, all four
controlling specs and all three Green plans exist in that commit, and neither the target
branch nor worktree exists. Record `<launch-base>` in the execution log. If any
file is merely untracked or another agent uses either target name, stop and
coordinate; do not delete, reuse, or build from the unversioned state.

- [ ] **Step 2: Create the dedicated branch and worktree**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/wave0-p0-green-launch
cd "$target"
test "$(pwd -P)" = "$target"
launch_worktree=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/wave0-p0-green-launch
launch_base=$(git -C "$launch_worktree" rev-parse wave0/p0-green-launch)
test "$launch_base" = "$(git -C "$launch_worktree" rev-parse HEAD)"
test -z "$(git -C "$launch_worktree" status --porcelain)"
git worktree add -b green/p0-student-separation \
  /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation \
  "$launch_base"
```

Expected: `Preparing worktree (new branch 'green/p0-student-separation')` and
checkout of the recorded `<launch-base>` SHA.

- [ ] **Step 3: Perform the mandatory startup audit inside the new worktree**

Run from the new worktree:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
git status --short --branch
git rev-parse HEAD
git log --oneline --decorate -15
git diff --stat
git diff --check
launch_base=$(git merge-base \
  green/p0-student-separation wave0/p0-green-launch)
test "$(git rev-parse HEAD)" = "$launch_base"
```

Expected: branch `green/p0-student-separation`, HEAD exactly the recorded
`<launch-base>`, clean tree, empty diff, and exit 0.

- [ ] **Step 4: Read every applicable agent instruction and quality gate completely**

Run from the new worktree; the line-count assertions prevent a silently
truncated read if one of these contracts changes after this plan:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
test "$(wc -l < AGENTS.md)" -eq 228
sed -n '1,120p' AGENTS.md
sed -n '121,228p' AGENTS.md
test "$(wc -l < docs/codex/QUALITY_GATES.md)" -eq 138
sed -n '1,138p' docs/codex/QUALITY_GATES.md
test "$(wc -l < docs/codex/CI_AUDIT_PHASE_0.md)" -eq 56
sed -n '1,56p' docs/codex/CI_AUDIT_PHASE_0.md
```

Expected: every asserted line count matches and every bounded range is read.
If a count differs, recalculate explicit non-overlapping ranges that cover
`1..EOF`, read them, and update the execution log before continuing.

- [ ] **Step 5: Read the cahier des charges completely in bounded ranges**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
test "$(wc -l < CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md)" -eq 1141
sed -n '1,300p' CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md
sed -n '301,600p' CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md
sed -n '601,900p' CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md
sed -n '901,1141p' CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md
```

Expected: the four ranges cover every line exactly once. Record the student,
teacher, LaTeX/PDF, mathematical-review, TDD, and release constraints.

- [ ] **Step 6: Read both approved designs completely and assert their contracts**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
test "$(wc -l < docs/superpowers/specs/2026-08-13-green-p0-separation-eleve-design.md)" -eq 312
sed -n '1,160p' docs/superpowers/specs/2026-08-13-green-p0-separation-eleve-design.md
sed -n '161,312p' docs/superpowers/specs/2026-08-13-green-p0-separation-eleve-design.md
test "$(wc -l < docs/superpowers/specs/2026-08-13-wave-0-green-p0-launch-design.md)" -eq 164
sed -n '1,164p' docs/superpowers/specs/2026-08-13-wave-0-green-p0-launch-design.md
python3 - <<'PY'
from pathlib import Path

separation = Path("docs/superpowers/specs/2026-08-13-green-p0-separation-eleve-design.md").read_text(encoding="utf-8")
orchestrator = Path("docs/superpowers/specs/2026-08-13-wave-0-green-p0-launch-design.md").read_text(encoding="utf-8")
for token in (
    "c50e455e", "quinze", "Huit objets", "tableau de migration",
    "qcm_diagnostics", "63 appels", "quatre PDF", "NO-GO",
    "approbation visuelle explicite", "revue mathématique indépendante",
):
    assert token in separation, token
for token in (
    "wave0/p0-green-launch", "green/p0-student-separation",
    "green/p0-programme-tspe", "green/p0-overflow",
    "quatre PDF", "validation humaine avant toute fusion",
):
    assert token in orchestrator, token
print("contrats specs separation/orchestrateur: PASS")
PY
```

Expected: complete reads and `contrats specs separation/orchestrateur: PASS`.

- [ ] **Step 7: Read the current audit completely and assert the observed baseline**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
test "$(wc -l < audit/AUDIT_ETAT_PROJET_2026-08-13.md)" -eq 254
sed -n '1,130p' audit/AUDIT_ETAT_PROJET_2026-08-13.md
sed -n '131,254p' audit/AUDIT_ETAT_PROJET_2026-08-13.md
python3 - <<'PY'
from pathlib import Path

text = Path("audit/AUDIT_ETAT_PROJET_2026-08-13.md").read_text(encoding="utf-8")
for token in ("NO-GO", "P0", "qcm", "barème", "renvoi", "Overfull"):
    assert token.casefold() in text.casefold(), token
print("audit baseline: PASS")
PY
```

Expected: the audit is read through EOF and the baseline assertion passes.
Any contradiction is resolved by authority order before tests are edited.

- [ ] **Step 8: Verify the required local toolchain**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 --version > /tmp/green-p0-separation-python.version 2>&1
lualatex --version > /tmp/green-p0-separation-lualatex.version 2>&1
pdftotext -v > /tmp/green-p0-separation-pdftotext.version 2>&1
pdfinfo -v > /tmp/green-p0-separation-pdfinfo.version 2>&1
pdffonts -v > /tmp/green-p0-separation-pdffonts.version 2>&1
qpdf --version > /tmp/green-p0-separation-qpdf.version 2>&1
compare -version > /tmp/green-p0-separation-compare.version 2>&1
python3 -c 'import pikepdf; print(pikepdf.__version__)' \
  > /tmp/green-p0-separation-pikepdf.version
for receipt in \
  /tmp/green-p0-separation-python.version \
  /tmp/green-p0-separation-lualatex.version \
  /tmp/green-p0-separation-pdftotext.version \
  /tmp/green-p0-separation-pdfinfo.version \
  /tmp/green-p0-separation-pdffonts.version \
  /tmp/green-p0-separation-qpdf.version \
  /tmp/green-p0-separation-compare.version \
  /tmp/green-p0-separation-pikepdf.version
do
  test -s "$receipt"
  sed -n '1p' "$receipt"
done
```

Expected: every command exits 0. A missing tool is a hard stop before any test or source edit.

### Task 2: Freeze the existing Red evidence and add structural contracts

**Files:**
- Modify: `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py`
- Modify: `tests/test_build_manifest.py`
- Modify: `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py`
- Modify: `Mathematiques/manuel-maths/tests/test_maquette_v5.py`
- Create: `tests/test_student_text_policy.py`
- Create: `Mathematiques/manuel-maths/tests/test_qcm_math_p0.py`
- Create: `Mathematiques/manuel-maths/tests/test_training_links.py`
- Create: `tests/test_wave0_separation_evidence.py`

- [ ] **Step 1: Prove the sealed Red node inventory before adding tests**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
set -euo pipefail
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_p0_student_pdf_text_gate_rejects_observed_leaks \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_student_pdf_text_gate_accepts_student_instructions \
  tests/test_build_manifest.py::test_p0_recorder_student_gate_rejects_observed_leaks \
  Mathematiques/manuel-maths/tests/test_p0_student_artifacts.py \
  --collect-only -q -p no:cacheprovider \
  | tee /tmp/green-p0-separation-red-collect.log
python3 - <<'PY'
from pathlib import Path

lines = Path("/tmp/green-p0-separation-red-collect.log").read_text(encoding="utf-8").splitlines()
nodes = [line for line in lines if "::test_" in line]
assert len(nodes) == 15, nodes
assert sum("test_p0_student_pdf_text_gate_rejects_observed_leaks" in n for n in nodes) == 6
assert sum("test_student_pdf_text_gate_accepts_student_instructions" in n for n in nodes) == 1
assert sum("test_p0_recorder_student_gate_rejects_observed_leaks" in n for n in nodes) == 6
assert sum("test_p0_student_artifacts.py::" in n for n in nodes) == 2
assert not any("SKIPPED" in n or "XFAIL" in n for n in lines)
print("sealed Red inventory: 6+1+6+2=15")
PY
```

Expected: `sealed Red inventory: 6+1+6+2=15`; no extra, missing,
skipped, or xfailed node.

- [ ] **Step 2: Reproduce the six assembler-policy failures**

Run with `set +e`, capture the exit status without a pipeline, then assert it:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
set +e
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_p0_student_pdf_text_gate_rejects_observed_leaks \
  -q -p no:cacheprovider > /tmp/green-p0-separation-red-assembler.log 2>&1
status=$?
set -e
test "$status" -eq 1
rg -n '^6 failed in ' /tmp/green-p0-separation-red-assembler.log
```

Expected: exit 1 and exactly `6 failed`; all failures belong to the named
parameterized node.

- [ ] **Step 3: Reproduce the one assembler false-positive failure**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
set +e
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_student_pdf_text_gate_accepts_student_instructions \
  -q -p no:cacheprovider > /tmp/green-p0-separation-red-false-positive.log 2>&1
status=$?
set -e
test "$status" -eq 1
rg -n '^1 failed in ' /tmp/green-p0-separation-red-false-positive.log
```

Expected: exit 1 and exactly `1 failed` for the seven-counterexample contract.

- [ ] **Step 4: Reproduce the six recorder-policy failures**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
set +e
python3 -m pytest \
  tests/test_build_manifest.py::test_p0_recorder_student_gate_rejects_observed_leaks \
  -q -p no:cacheprovider > /tmp/green-p0-separation-red-recorder.log 2>&1
status=$?
set -e
test "$status" -eq 1
rg -n '^6 failed in ' /tmp/green-p0-separation-red-recorder.log
```

Expected: exit 1 and exactly `6 failed`, all owned by the recorder contract.

- [ ] **Step 5: Reproduce the two tracked-PDF failures**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
set +e
python3 -m pytest Mathematiques/manuel-maths/tests/test_p0_student_artifacts.py \
  -q -p no:cacheprovider > /tmp/green-p0-separation-red-pdf.log 2>&1
status=$?
set -e
test "$status" -eq 1
rg -n '^2 failed in ' /tmp/green-p0-separation-red-pdf.log
```

Expected: exit 1 and exactly `2 failed`, one 1SPE and one TSPE PDF node. This
completes the auditable `6 + 1 + 6 + 2 = 15` Red contract by responsibility.

- [ ] **Step 6: Add Red policy-source and equality tests**

Add tests that load `scripts/student_text_policy.py`, assert the exact five stable reasons, compare both existing wrappers to the shared function over every positive and false-positive case, and inspect both wrapper sources to ensure they call the shared function rather than define regex tuples locally.

Required core assertions:

```python
assert assemble_manuel.student_text_violations(text) == expected
assert manifest_module._student_text_violations(text) == expected
assert student_text_policy.student_text_violations(text) == expected
assert "student_text_policy.student_text_violations" in assembler_source
assert "student_text_policy.student_text_violations" in recorder_source
```

Name the delegation/source-inspection node in each modified historical test
file exactly `test_shared_student_text_policy_delegation`.

- [ ] **Step 7: Run the new policy-source tests and observe Red**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest tests/test_student_text_policy.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_p0_student_pdf_text_gate_rejects_observed_leaks \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_student_pdf_text_gate_accepts_student_instructions \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_shared_student_text_policy_delegation \
  tests/test_build_manifest.py::test_p0_recorder_student_gate_rejects_observed_leaks \
  tests/test_build_manifest.py::test_recorder_student_text_gate_allows_correction_instructions \
  tests/test_build_manifest.py::test_shared_student_text_policy_delegation \
  -q -p no:cacheprovider
```

Expected: FAIL because `scripts/student_text_policy.py` is absent and both consumers still own different regex sets; the historical false-positive tests remain PASS.

- [ ] **Step 8: Add the pure eight-QCM snapshot helper**

Use `apply_patch` with the absolute `test_qcm_source_unique.py` target. Add
`load_qcm_snapshot(json_path, tex_path) -> list[dict[str, object]]`, returning
for every question exactly `id`, four ordered `options`, `correcte`, and
`diagnostics`. Add a helper-only fixture test using `tmp_path`; it must pass
without production changes.

- [ ] **Step 9: Run the QCM snapshot-helper test Green**

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_load_qcm_snapshot_preserves_ordered_fields \
  -q -p no:cacheprovider
```

Expected: `1 passed`; this validates test infrastructure only.

- [ ] **Step 10: Add Red two-output and routing contracts**

Apply the exact test patches to `test_qcm_source_unique.py` and
`test_assemble_manuel_observed.py`. Parameterize the approved eight chapters.
Require one student output under `qcm/`, one teacher output under
`diagnostics/`, matching IDs/types, no teacher field or boundary in the student
body, exact answer/diagnostic preservation in the teacher body, exhaustive
`--check`, double student exclusion, and professor `qcm` then `diagnostics`
order.

Create and name explicitly in the assembler test file
`test_qcm_folder_type_and_variant_routing`. It asserts the closed folder/type
policy and exact student/professor order; Task 5 Step 19 executes this same
node Green.

- [ ] **Step 11: Run the two-output contracts Red**

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
set +e
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_eight_qcm_json_sources_require_two_exact_outputs \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_qcm_folder_type_and_variant_routing \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_qcm_diagnostics_routing_and_bilateral_boundary \
  -q -p no:cacheprovider > /tmp/green-p0-qcm-split-red.log 2>&1
status=$?
set -e
test "$status" -eq 1
rg -n 'FAILED.*(two_exact_outputs|folder_type_and_variant|bilateral_boundary)' /tmp/green-p0-qcm-split-red.log
```

Expected: exit 1 because no diagnostics output/routing exists.

- [ ] **Step 12: Add and run the Produit scalaire mutation Red**

Apply `test_product_scalar_mutation_rejects_second_true_answer(tmp_path)` to
the absolute `test_qcm_math_p0.py` target. It copies the canonical JSON into
`tmp_path`, replaces option C by `de même norme`, calls the validator against
that temporary path, and expects the disciplinary error. Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_qcm_math_p0.py::test_product_scalar_mutation_rejects_second_true_answer \
  -q -p no:cacheprovider
```

Expected: `1 passed`; the pure test validator rejects the temporary second
answer and no tracked source changes.

- [ ] **Step 13: Add Red bilateral-rubric and semantic-maquette tests**

Assert the professor master contains, for every diagnostics object, exactly:

```text
QCM object end
\clearpage
\rubrique{Corrigés}
diagnostics object begin/input/end
\clearpage
next \rubrique or next chapter opening
```

Assert the student master contains no `diagnostics/` input. Require both the
professor assembler and `maquette.tex` to invoke exactly
`\nxQcmDiagnostics{<repository-relative diagnostics path>}`. The class command,
not either generated body, expands to the bilateral `\clearpage`,
`\rubrique{Corrigés}`, input, `\clearpage` contract and closes the active QCM
columns exactly once. Extend the v5 manifest tests to require `qcm.student` and
`qcm.diagnostics`, two SHA-256 values, both semantic inputs in `maquette.tex`,
concatenated bodies equal to the old mixed body after removing only the former
separator, expected 15 pages, and all historical PNG hashes unchanged. Reject
any internal `\newpage` in either generated body.

Name the focused historical-file nodes exactly
`test_qcm_diagnostics_routing_and_bilateral_boundary`,
`test_professor_diagnostics_bilateral_pdf_pages`,
`test_qcm_semantic_diagnostics_boundary_contract`, and
`test_professor_keeps_all_eight_diagnostics` so later Green gates can select
only separation ownership.

Also create and name explicitly in `test_assemble_manuel_observed.py`:
`test_qcm_diagnostics_path_validation`, covering safe repository-relative
diagnostics paths and path escape rejection; and
`test_qcm_professor_student_master_templates`, covering the exact professor
and student `faireLePoint` templates. Task 5 Step 24 executes both Green.

- [ ] **Step 14: Run the semantic-boundary contracts Red**

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
set +e
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_qcm_diagnostics_routing_and_bilateral_boundary \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_qcm_diagnostics_path_validation \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_qcm_professor_student_master_templates \
  Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_qcm_semantic_diagnostics_boundary_contract \
  -q -p no:cacheprovider > /tmp/green-p0-qcm-boundary-red.log 2>&1
status=$?
set -e
test "$status" -eq 1
rg -n 'FAILED.*(bilateral_boundary|path_validation|master_templates|semantic_diagnostics)' /tmp/green-p0-qcm-boundary-red.log
```

Expected: exit 1; the semantic interface does not exist.

- [ ] **Step 15: Add Red TSPE evaluation tests**

For both A and B, assert the statement prints the public title and duration but neither `TSPE-...`, `Bareme/Barème`, total points, exercise points, nor question points. Assert the correction prints a total of 20 points and exactly four 5-point exercise allocations, while `bareme_total: 20` remains in statement metadata.

Name the focused node in the historical assembler test exactly
`test_tspe_evaluation_student_teacher_contract`.

- [ ] **Step 16: Run the TSPE evaluation contract Red**

Run the exact node and require exit 1 for the visible IDs/points and absent
teacher marking schemes; store output in
`/tmp/green-p0-tspe-evaluation-red.log` and assert its node name:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
set +e
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_tspe_evaluation_student_teacher_contract \
  -q -p no:cacheprovider > /tmp/green-p0-tspe-evaluation-red.log 2>&1
status=$?
set -e
test "$status" -eq 1
rg -n 'FAILED.*test_tspe_evaluation_student_teacher_contract' \
  /tmp/green-p0-tspe-evaluation-red.log
```

- [ ] **Step 17: Add the PDF-link trace parser helper**

Apply the helper patch to the absolute `test_training_links.py` target. Add
`parse_aux_training_trace(text) -> dict[str, Trace]` and
`match_saved_point_to_link(page, x_sp, y_sp) -> Annotation`; unit fixtures
must reject duplicate tokens, absent coordinates, zero/multiple containing
rectangles, and malformed destinations.

- [ ] **Step 18: Run link-helper fixtures Green**

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_training_links.py::test_parse_aux_training_trace_closed_contract \
  Mathematiques/manuel-maths/tests/test_training_links.py::test_match_saved_point_to_exactly_one_link \
  -q -p no:cacheprovider
```

Expected: both helper nodes pass without production code.

- [ ] **Step 19: Add Red bijection tests for all 63 method calls and real PDF links**

Implement helpers that scan only method objects included by the 1SPE and TSPE assemblers. Assert exactly 63 `(chapter, method)` calls, unique labels `nx:training:<chapter>:<method>`, explicit metadata mapping except the approved capacity fallback for `1SPE-EXPONENTIELLE/M5` and all five `1SPE-VARIABLES-ALEATOIRES` methods, failure on no target/duplicate label/chapter mismatch, no provisional text, three-pass AUX resolution, and one real PDF `/Link` annotation whose destination page is the selected exercise page for each call.

Assign each source occurrence a deterministic token from repository-relative
method path plus ordinal. Require an AUX trace row
`token -> (page, x-sp, y-sp, target-label)` for each call. Use pikepdf to match
the saved point to exactly one `/Link` rectangle on the same page, resolve its
named destination, and compare the destination page object with the selected
exercise page. Assert bijectively: 63 unique source tokens, 63 coordinates, 63
matched annotations, 63 destinations, no unmatched annotation, collision, or
many-to-one source match. Text occurrence alone is never proof.

Name the end-to-end node exactly
`test_63_source_tokens_match_pdf_annotations_and_destinations`.

- [ ] **Step 20: Run the 63-link end-to-end contract Red**

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
set +e
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_training_links.py::test_63_source_tokens_match_pdf_annotations_and_destinations \
  -q -p no:cacheprovider > /tmp/green-p0-training-links-red.log 2>&1
status=$?
set -e
test "$status" -eq 1
rg -n 'FAILED.*test_63_source_tokens' /tmp/green-p0-training-links-red.log
rg -n 'source token|AUX trace' /tmp/green-p0-training-links-red.log
```

Expected: exit 1 for missing source tokens/AUX trace, not helper failure.

- [ ] **Step 21: Add Red evidence-tool tests before implementation**

In `tests/test_wave0_separation_evidence.py`, freeze the schema from Task 9,
four exact artifact identities, no-overwrite review-run behavior, hash checks,
and invalidation on any rebuilt PDF divergence. The tool does not exist yet.
Run the single file and require FAIL for import/CLI absence:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
set +e
python3 -m pytest tests/test_wave0_separation_evidence.py \
  -q -p no:cacheprovider > /tmp/green-p0-evidence-red.log 2>&1
status=$?
set -e
test "$status" -eq 1
rg -n 'build_wave0_separation_evidence' /tmp/green-p0-evidence-red.log
```

- [ ] **Step 22: Run every new structural test and record expected Red causes**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest \
  tests/test_student_text_policy.py \
  Mathematiques/manuel-maths/tests/test_qcm_math_p0.py \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py \
  Mathematiques/manuel-maths/tests/test_training_links.py \
  Mathematiques/manuel-maths/tests/test_maquette_v5.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  tests/test_wave0_separation_evidence.py \
  tests/test_build_manifest.py \
  -q -p no:cacheprovider
```

Expected: new tests fail only because the shared policy, two-output generator, evaluation split, routing, labels, and real links do not exist; historical tests unrelated to these features pass. No test may be marked skip/xfail.

- [ ] **Step 23: Commit tests only**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest \
  tests/test_student_text_policy.py \
  tests/test_wave0_separation_evidence.py \
  Mathematiques/manuel-maths/tests/test_qcm_math_p0.py \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py \
  Mathematiques/manuel-maths/tests/test_training_links.py \
  Mathematiques/manuel-maths/tests/test_maquette_v5.py \
  --collect-only -q -p no:cacheprovider > /tmp/green-p0-tests-commit.collect
test -s /tmp/green-p0-tests-commit.collect
git diff --check
git status --short
git add tests/test_student_text_policy.py tests/test_build_manifest.py \
  tests/test_wave0_separation_evidence.py \
  Mathematiques/manuel-maths/tests/test_qcm_math_p0.py \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py \
  Mathematiques/manuel-maths/tests/test_training_links.py \
  Mathematiques/manuel-maths/tests/test_maquette_v5.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py
python3 -c 'import subprocess,sys; actual=sorted(subprocess.check_output(["git","diff","--cached","--name-only"], text=True).splitlines()); expected=sorted(sys.argv[1:]); assert actual == expected, (actual, expected)' \
  tests/test_student_text_policy.py \
  tests/test_build_manifest.py \
  tests/test_wave0_separation_evidence.py \
  Mathematiques/manuel-maths/tests/test_qcm_math_p0.py \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py \
  Mathematiques/manuel-maths/tests/test_training_links.py \
  Mathematiques/manuel-maths/tests/test_maquette_v5.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py
git diff --cached --check
git commit -m "[TESTS] precise le contrat structurel des variantes"
test -z "$(git diff --cached --name-only)"
git status --short
```

Expected: only test files are staged; commit succeeds. Request a read-only compliance review of the Red commit before production changes.

### Task 3: Prove and correct the two mathematical P0s

**Files:**
- Modify: `Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/qcm/1SPE-EXPONENTIELLE-QCM.tex`
- Modify: `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/qcm/1SPE-PRODUIT-SCALAIRE-QCM.json`
- Modify: `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/qcm/1SPE-PRODUIT-SCALAIRE-QCM.tex`
- Test: `Mathematiques/manuel-maths/tests/test_qcm_math_p0.py`

- [ ] **Step 1: Run only the two disciplinary regressions and observe Red**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_qcm_math_p0.py \
  -q -p no:cacheprovider
```

Expected: Exponentielle Q9 fails because TeX option A contradicts JSON/correct answer; Produit scalaire Q8 fails because B and C are both mathematically true.

- [ ] **Step 2: Correct Exponentielle Q9 minimally**

In the transitional TeX, make option A exactly `e^{2,5} < e^{\sqrt 7}`, option B the strict inverse, answer A, and diagnostics consistent with JSON. Do not edit the already-correct JSON.

- [ ] **Step 3: Correct Produit scalaire Q8 at the canonical source**

Keep `u=(2,3)`, `v=(3,-2)`, correct answer B `orthogonaux`, and replace option C in JSON by an unambiguously false distractor, for example `de normes différentes`; update C's diagnostic to state that both norms equal `\sqrt{13}`. Mirror exactly this change in the transitional TeX question and diagnostics table.

- [ ] **Step 4: Run the disciplinary tests Green**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_qcm_math_p0.py \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py \
  -q -p no:cacheprovider
```

Expected: the two disciplinary regressions pass; source-unique migration tests
remain Red only for the not-yet-implemented split.

- [ ] **Step 5: Prove the second-answer mutation through `tmp_path`**

Run only the test that copies the canonical JSON into pytest's `tmp_path`,
changes option C in that copy to `de même norme`, and passes the copied path to
the validator:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
before=$(git hash-object Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/qcm/1SPE-PRODUIT-SCALAIRE-QCM.json)
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_qcm_math_p0.py::test_product_scalar_mutation_rejects_second_true_answer \
  -q -p no:cacheprovider
after=$(git hash-object Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/qcm/1SPE-PRODUIT-SCALAIRE-QCM.json)
test "$before" = "$after"
```

Expected: `1 passed` and identical tracked-source blob hashes. No shell edit,
checkout, restore, or in-place mutation is permitted.

- [ ] **Step 6: Pause for independent mathematical review**

Provide the reviewer the two statements, all four options, correct letters, all distractor diagnostics, and the test output. The reviewer must explicitly approve both questions. If either is rejected or ambiguous, stop and revise under a new Red test; **do not regenerate any QCM before approval**.

- [ ] **Step 7: Commit the reviewed mathematical correction alone**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_qcm_math_p0.py \
  -q -p no:cacheprovider
git diff --check
git status --short
git add \
  Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/qcm/1SPE-EXPONENTIELLE-QCM.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/qcm/1SPE-PRODUIT-SCALAIRE-QCM.json \
  Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/qcm/1SPE-PRODUIT-SCALAIRE-QCM.tex
python3 -c 'import subprocess,sys; actual=sorted(subprocess.check_output(["git","diff","--cached","--name-only"], text=True).splitlines()); expected=sorted(sys.argv[1:]); assert actual == expected, (actual, expected)' \
  Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/qcm/1SPE-EXPONENTIELLE-QCM.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/qcm/1SPE-PRODUIT-SCALAIRE-QCM.json \
  Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/qcm/1SPE-PRODUIT-SCALAIRE-QCM.tex
git diff --cached --check
git commit -m "[MATH] corrige les deux incoherences QCM"
test -z "$(git diff --cached --name-only)"
git status --short
```

Expected: exactly three content files; no generator or layout file. Record reviewer identity and decision in the PR/review record, not by self-approval.

### Task 4: Centralize the student-text policy

**Files:**
- Create: `scripts/student_text_policy.py`
- Test: `tests/test_student_text_policy.py`
- Modify: `scripts/build_manifest.py`
- Modify: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
- Test: `tests/test_build_manifest.py`
- Test: `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py`

- [ ] **Step 1: Re-run the shared-policy tests Red**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest tests/test_student_text_policy.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_p0_student_pdf_text_gate_rejects_observed_leaks \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_student_pdf_text_gate_accepts_student_instructions \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_shared_student_text_policy_delegation \
  tests/test_build_manifest.py::test_p0_recorder_student_gate_rejects_observed_leaks \
  tests/test_build_manifest.py::test_recorder_student_text_gate_allows_correction_instructions \
  tests/test_build_manifest.py::test_shared_student_text_policy_delegation \
  -q -p no:cacheprovider
```

Expected: FAIL for absent shared module/delegation and missing observed patterns.

- [ ] **Step 2: Implement the pure policy minimally**

Expose only:

```python
def student_text_violations(text: str) -> list[str]:
    """Return stable P0 reasons in deterministic contract order."""
```

Recognize case/accent variants of internal `1SPE-`, `TSPE-`, `1NSI-` IDs; correction/diagnostics headings, correct-answer headings and correction keys; all printed barèmes; teacher notes; and provisional `(renvois exercices M…)`. Return each reason once in this exact order: `identifiant interne`, `corrigé`, `barème enseignant`, `note enseignant`, `renvoi provisoire`. Keep the seven approved student counterexamples clean.

- [ ] **Step 3: Delegate both wrappers without changing their public names**

Import the root module from both consumers. `assemble_manuel.student_text_violations` and `build_manifest._student_text_violations` remain callable and return the shared function result. Do not move `pdftotext`, error handling, timeouts, or domain exceptions into the pure module.

- [ ] **Step 4: Run policy tests Green and mutate an extracted text**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest tests/test_student_text_policy.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_p0_student_pdf_text_gate_rejects_observed_leaks \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_student_pdf_text_gate_accepts_student_instructions \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_shared_student_text_policy_delegation \
  tests/test_build_manifest.py::test_p0_recorder_student_gate_rejects_observed_leaks \
  tests/test_build_manifest.py::test_recorder_student_text_gate_allows_correction_instructions \
  tests/test_build_manifest.py::test_shared_student_text_policy_delegation \
  -q -p no:cacheprovider
```

Expected: PASS. Then feed `Clé de correction` to both wrappers; both must return `['corrigé']`. Feed `Corrige le programme.`; both must return `[]`.

- [ ] **Step 5: Commit the policy atomically**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
git diff --check
git status --short
git add scripts/student_text_policy.py tests/test_student_text_policy.py \
  scripts/build_manifest.py tests/test_build_manifest.py \
  Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py
python3 -c 'import subprocess,sys; actual=sorted(subprocess.check_output(["git","diff","--cached","--name-only"], text=True).splitlines()); expected=sorted(sys.argv[1:]); assert actual == expected, (actual, expected)' \
  scripts/student_text_policy.py \
  tests/test_student_text_policy.py \
  scripts/build_manifest.py \
  tests/test_build_manifest.py \
  Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py
git diff --cached --check
git commit -m "[PYTHON] centralise la politique de separation eleve"
test -z "$(git diff --cached --name-only)"
git status --short
```

Expected: shared policy and delegation only; no QCM, evaluation, LaTeX-class, or PDF changes.

## Chunk 2: JSON-derived QCMs, variant routing, maquette, evaluations, and links

### Task 5: Generate two closed TeX bodies from each canonical QCM JSON

**Files:**
- Create: `audit/wave0-green-p0-separation-qcm-migration-2026-08-13.json`
- Modify: `Mathematiques/manuel-maths/scripts/build_qcm_tex.py`
- Modify: `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py`
- Modify: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
- Modify: `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py`
- Modify: `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/qcm/1SPE-DERIVATION-LOCAL-QCM.json`
- Modify: `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/qcm/1SPE-DERIVATION-GLOBAL-QCM.json`
- Modify: `Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls`
- Create: `scripts/build_wave0_separation_evidence.py`
- Modify generated: the eight existing `qcm/*-QCM.tex` files listed in the design
- Create generated: the matching eight `diagnostics/*-QCM-DIAGNOSTICS.tex` files

- [ ] **Step 1: Run the two-output/source-unique tests Red**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  -k 'qcm or diagnostic or rubrique' -q -p no:cacheprovider
```

Expected: FAIL because seven TeX files are hand-maintained, diagnostics are embedded, `diagnostics/` is unknown, and no bilateral boundary exists.

- [ ] **Step 2: Transcribe Dérivation locale into its canonical JSON**

Use `apply_patch` with exact target
`/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation/Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/qcm/1SPE-DERIVATION-LOCAL-QCM.json`.
Transcribe only `titre`, `enonce`, and ordered `options` from the current TeX;
do not change IDs, answers, or diagnostics. Run the focused snapshot comparison
for this chapter:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest \
  'Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_current_qcm_snapshots_equal[1SPE-DERIVATION-LOCAL]' \
  -q -p no:cacheprovider
```

Expected: `1 passed` and the expected question count.

- [ ] **Step 3: Transcribe Dérivation globale into its canonical JSON**

Apply the same bounded operation to exact target
`/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation/Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/qcm/1SPE-DERIVATION-GLOBAL-QCM.json`,
then run its focused snapshot comparison. Expected: equality and no change to
IDs, answers, or diagnostics. Every one of the eight JSON files now has title,
`id`, `capacite`, `enonce`, four ordered options, one `correcte`, and three
distractor diagnostics; any mismatch stops the task.

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest \
  'Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_current_qcm_snapshots_equal[1SPE-DERIVATION-GLOBAL]' \
  -q -p no:cacheprovider
```

Expected: `1 passed`; any mismatch stops before the migration artifact.

- [ ] **Step 4: Write the exhaustive eight-QCM migration artifact**

Create the versioned JSON with a closed top-level shape:

Use `apply_patch` with exact target
`/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation/audit/wave0-green-p0-separation-qcm-migration-2026-08-13.json`.

```json
{
  "schema_version": 1,
  "artifact_identity": "wave0-separation-qcm-migration",
  "source_commit": "<git rev-parse HEAD at artifact creation>",
  "decision": {"status": "pending", "reviewed_by": null, "reviewed_at": null},
  "provenance_events": [],
  "qcm": []
}
```

The `qcm` array has exactly eight rows in the approved chapter order. Every row
records chapter, JSON and current TeX repository-relative paths and SHA-256,
question count, then every question's `id`, ordered four options, `correcte`,
and all diagnostics on both sides. `source_commit` must equal the fresh output
of `git rev-parse HEAD` at artifact creation; it anchors repository history but
does not claim that the uncommitted Dérivation transcriptions already exist in
that commit. Every row has `"differences": []` only after comparing the two
current working-tree representations field by field. Do not assert equality
between a committed historical blob and an uncommitted transcription.

The separate `provenance_events` array records the historical Exponentielle
Q9 correction, Produit scalaire Q8 correction, and two Dérivation JSON
transcriptions. The two math events carry a separate `math_commit` equal to
the `[MATH]` SHA; the transcription events carry a working-tree receipt rather
than misusing `source_commit`. Every event includes reason, source path,
before/after SHA-256, and independent reviewer state. Those events explain
how equal current representations were obtained without being exceptions to
equality. Tests reject a non-empty row difference, wrong source commit,
missing/duplicate chapter, question, option, diagnostic, path, hash, or
provenance event; an unordered summary is not a substitute for this table.

- [ ] **Step 5: PAUSE — obtain independent migration approval before generation**

Give an independent reviewer the complete artifact and the current JSON/TeX
blobs for all eight QCM. The reviewer must confirm each equality row, every
separate provenance event, and absence of silent preference, then set only `decision.status =
"approved"`, name and zoned timestamp. Re-run the closed-schema/hash test.
Stop on rejection or `pending`; **do not invoke `build_qcm_tex.py` in write
mode before this explicit eight-QCM approval**. The author of a transcribed or
mathematically corrected row cannot approve that row.

- [ ] **Step 6: Split the renderer into explicit student and diagnostics functions**

Implement focused functions such as:

Use `apply_patch` with exact target
`/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation/Mathematiques/manuel-maths/scripts/build_qcm_tex.py`.

```python
def render_student(data: dict[str, object]) -> str: ...
def render_diagnostics(data: dict[str, object]) -> str: ...
def output_paths(source: Path, chapter: str) -> tuple[Path, Path]: ...
```

The student META retains the historical QCM ID/type. The teacher META uses `<chapter>-QCM-DIAGNOSTICS`, type `qcm_diagnostics`, and the same `genere_depuis`. Neither body contains `\clearpage` nor `\rubrique`. Keep rendering deterministic and never edit generated bodies manually after this point.

- [ ] **Step 7: Add Red crash-recovery tests for the TeX pair**

Using `apply_patch` with the absolute
`.../Mathematiques/manuel-maths/tests/test_qcm_source_unique.py` target, add
and name exactly these four nodes, which later commands execute verbatim:

1. `test_qcm_pair_transaction_recovers_every_promotion_failure`;
2. `test_qcm_pair_lock_paths_and_durable_temps`;
3. `test_qcm_pair_journal_and_backups_are_durable`;
4. `test_qcm_pair_ordered_promotions`.

Parameterize them for these exact fault points: after journal fsync, after
student backup, after diagnostics backup, after student promotion, after
diagnostics promotion, and during each rollback promotion. Each fixture uses
`tmp_path`, starts with two distinct old files, invokes recovery after the
injected exception, and asserts the pair is either wholly old or wholly new —
never mixed. Also cover both targets initially absent and only one initially
present.

- [ ] **Step 8: Run the pair-transaction tests Red**

Run the exact node added above:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
set +e
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_qcm_pair_transaction_recovers_every_promotion_failure \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_qcm_pair_lock_paths_and_durable_temps \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_qcm_pair_journal_and_backups_are_durable \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_qcm_pair_ordered_promotions \
  -q -p no:cacheprovider > /tmp/green-p0-qcm-transaction-red.log 2>&1
status=$?
set -e
test "$status" -eq 1
for node in \
  test_qcm_pair_transaction_recovers_every_promotion_failure \
  test_qcm_pair_lock_paths_and_durable_temps \
  test_qcm_pair_journal_and_backups_are_durable \
  test_qcm_pair_ordered_promotions
do
  rg -n "FAILED.*$node" /tmp/green-p0-qcm-transaction-red.log
done
```

Expected: exit 1 and all four named nodes are observed Red before Steps 10,
12, 14 and 16 make their respective behavior Green.

- [ ] **Step 9: Implement lock, validated paths, and durable temporaries**

Patch only the absolute generator. Validate/render both bodies before I/O;
refuse path escape, symlink, non-regular target, and concurrent adjacent lock.
Write two unique adjacent temporaries with `flush`, file `os.fsync`, and parent
directory fsync. Do not promote or back up yet.

- [ ] **Step 10: Run lock/temp/fsync tests Green**

Run the exact transaction parameters `lock`, `path`, `student-temp`, and
`diagnostics-temp`. Expected: all pass; the broader promotion cases remain Red.

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_qcm_pair_lock_paths_and_durable_temps -q -p no:cacheprovider
```

- [ ] **Step 11: Implement the durable journal and two backups**

Add the closed JSON journal with original-existence bits, paths, hashes and
state; fsync it and its directory. Back up student then diagnostics to unique
adjacent files, fsync each, and journal each transition. No promotion yet.

- [ ] **Step 12: Run journal/backup failure tests Green**

Run exact parameters `journal-fsync`, `student-backup`, and
`diagnostics-backup`. Expected: all recover to the wholly old pair.

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_qcm_pair_journal_and_backups_are_durable -q -p no:cacheprovider
```

- [ ] **Step 13: Implement ordered promotion and committed cleanup**

Promote student then diagnostics with `os.replace`, journal/fsync after each,
verify both hashes, mark committed, then remove backups/temps/journal and fsync
directories. Do not implement rollback recovery in this checkbox.

- [ ] **Step 14: Run both ordered-promotion tests Green**

Run parameters `student-promotion` and `diagnostics-promotion` after Step 13.
Expected: a fully valid new pair is finalized, never mixed. Rollback-injection
cases remain Red until Step 15.

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_qcm_pair_ordered_promotions -q -p no:cacheprovider
```

- [ ] **Step 15: Implement idempotent rollback and startup recovery**

On a noncommitted journal, restore both originals or remove targets whose
original-existence bit is false. Journal each rollback promotion so failure is
retryable. A malformed/stale journal is code 2; `--check` performs no recovery
write and returns 1 only for missing/divergent output.

- [ ] **Step 16: Run the complete transaction suite Green**

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_qcm_pair_transaction_recovers_every_promotion_failure \
  -q -p no:cacheprovider
```

Expected: every parameterized promotion and rollback fault passes, and every
recovered pair is wholly old or wholly new.

- [ ] **Step 17: Re-run the focused routing contract Red**

Run `test_qcm_diagnostics_routing_and_bilateral_boundary` alone. Expected:
FAIL because the folder/type policy and professor ordering are absent.

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_qcm_diagnostics_routing_and_bilateral_boundary -q -p no:cacheprovider
```

- [ ] **Step 18: Add diagnostics as a closed routing category**

In `assemble_manuel.py`, insert `("diagnostics", "*")` immediately after `("qcm", "*")`, map it to `Corrigés`, add it to `ELEVE_EXCLUDES`, and keep `qcm_diagnostics` out of `ELEVE_ALLOWED_TYPES`. Do not place diagnostics in the general final corrections folder.

Apply this patch only to exact target
`/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation/Mathematiques/manuel-maths/scripts/assemble_manuel.py`.

- [ ] **Step 19: Run folder/type routing Green**

Run the focused routing node without its LaTeX source assertion. Expected:
student excludes diagnostics by folder and type, professor orders it after QCM.

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_qcm_folder_type_and_variant_routing -q -p no:cacheprovider
```

- [ ] **Step 20: Re-run only the class command/state test Red**

Run only the focused maquette/class node below. Expected: FAIL for absent
command and state guard. Path validation/templates belong only to Steps 23–24.

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_qcm_semantic_diagnostics_boundary_contract -q -p no:cacheprovider
```

- [ ] **Step 21: Implement the LaTeX command API and closed-state machine**

Define in `nexus-manuel-v5.cls` the explicit public interface
`\nxQcmDiagnostics{<repository-relative-path>}` and a private closed-state
flag. Apply Step 21 exclusively to absolute target
`/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation/Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls`.
Do not modify the assembler, validate repository paths, or generate master
templates in this step.

On its only allowed invocation inside `faireLePoint`, the semantic command
closes the open item box if needed, closes `multicols` exactly once, restores
the QCM-local definitions, emits `\clearpage`, emits
`\rubrique{Corrigés}`, applies diagnostics formatting, inputs the validated
argument, emits the bilateral final `\clearpage`, and marks the environment
closed. The `faireLePoint` end code observes that flag and performs cleanup
without a second `\end{multicols}` or page break. Without the command, its end
code closes the student columns once and emits the historical student exit
break. A second invocation or invocation outside `faireLePoint` is a hard
LaTeX error. Repository-path validation remains assembler-owned.

Generated student and diagnostics bodies contain no `\newpage`, `\clearpage`,
rubric, environment boundary, or column transition. This source contract is
implemented and Green before Task 6 touches the maquette.

- [ ] **Step 22: Run command/state tests Green**

Run only the class fixture cases: student closes columns once; professor
transition closes once; second/outside invocation hard-fails. Expected: PASS.

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_qcm_semantic_diagnostics_boundary_contract -q -p no:cacheprovider
```

- [ ] **Step 23: Implement validated assembler invocation paths**

Patch exclusively absolute target
`/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation/Mathematiques/manuel-maths/scripts/assemble_manuel.py`.
Validate the repository-relative `diagnostics/` path. Emit professor template
`begin faireLePoint`, student QCM input, semantic diagnostics invocation, `end
faireLePoint`; emit student template `begin faireLePoint`, student QCM input,
`end faireLePoint`, without diagnostics command/input. Do not modify the class.

- [ ] **Step 24: Run path, routing, and bilateral-source tests Green**

Run only the focused assembler/bilateral nodes. Expected: exact professor/student
templates, hard failure for unsafe path, no generated-body boundary commands.

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_qcm_diagnostics_path_validation \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_qcm_professor_student_master_templates \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_qcm_diagnostics_routing_and_bilateral_boundary \
  -q -p no:cacheprovider
```

- [ ] **Step 25: Generate all eight pairs after the approval gate**

Run from `Mathematiques/manuel-maths`:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
for chapter in \
  1SPE-SUITES 1SPE-SECOND-DEGRE 1SPE-DERIVATION-LOCAL \
  1SPE-DERIVATION-GLOBAL 1SPE-EXPONENTIELLE \
  1SPE-PRODUIT-SCALAIRE 1SPE-VARIABLES-ALEATOIRES \
  TSPE-CONTINUITE; do
  python3 Mathematiques/manuel-maths/scripts/build_qcm_tex.py --chap "$chapter"
done
```

Expected: eight success lines, each naming both outputs and the exact question count; no hand-written QCM suffix remains.

- [ ] **Step 26: Verify both outputs and routing Green**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
for chapter in \
  1SPE-SUITES 1SPE-SECOND-DEGRE 1SPE-DERIVATION-LOCAL \
  1SPE-DERIVATION-GLOBAL 1SPE-EXPONENTIELLE \
  1SPE-PRODUIT-SCALAIRE 1SPE-VARIABLES-ALEATOIRES \
  TSPE-CONTINUITE; do
  python3 Mathematiques/manuel-maths/scripts/build_qcm_tex.py \
    --chap "$chapter" --check
done
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_qcm_math_p0.py \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  -k 'qcm or diagnostic or rubrique or student_order or professor_order' \
  -q -p no:cacheprovider
```

Expected: all commands PASS; professor keeps all eight diagnostic grids, student keeps none, and bilateral source ordering is exact.

- [ ] **Step 27: Verify scope and defer the atomic commit until the maquette is migrated**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
git diff --check
git status --short
test -z "$(git diff --name-only | rg '\.pdf$' || true)"
```

Expected: only the eight approved JSON/TeX pairs, eight new diagnostics,
generator, routing, and tests are changed, with no PDF. Leave them unstaged and
continue directly to Task 6; the approved design requires the Dérivation locale
split and maquette migration in the same commit. Do not commit or amend here.

### Task 6: Migrate the immutable v5 maquette contract atomically

**Files:**
- Modify: `Mathematiques/manuel-maths/build/maquette-v5/manifest.json`
- Modify: `Mathematiques/manuel-maths/build/maquette-v5/maquette.tex`
- Modify: `Mathematiques/manuel-maths/scripts/build_maquette_v5.py`
- Modify: `Mathematiques/manuel-maths/tests/test_maquette_v5.py`
- Modify: `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/qcm/1SPE-DERIVATION-LOCAL-QCM.json`
- Modify: `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/qcm/1SPE-DERIVATION-GLOBAL-QCM.json`
- Modify: `Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls`
- Create: `scripts/build_wave0_separation_evidence.py`
- Verify only: `Mathematiques/manuel-maths/scripts/check_maquette_v5.py`

- [ ] **Step 1: Run the migrated maquette tests Red**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_maquette_v5.py \
  -k 'manifest or qcm or diagnostics or immutable' -q -p no:cacheprovider
```

Expected: FAIL because manifest v2 has one `qcm.file/sha256` and maquette has one mixed input.

- [ ] **Step 2: Update the manifest schema without weakening validation**

Replace `qcm.file/sha256` with exactly:

```json
"qcm": {
  "student": {"file": ".../qcm/...-QCM.tex", "sha256": "..."},
  "diagnostics": {"file": ".../diagnostics/...-QCM-DIAGNOSTICS.tex", "sha256": "..."}
}
```

Increment the closed manifest version and update `build_maquette_v5.py` to validate both repository-relative regular files and both 64-hex hashes. Retain every unrelated manifest field and validator.

- [ ] **Step 3: Invoke the shared semantic boundary in the maquette**

Keep the student QCM at the historical input point. At the exact former suffix
location, invoke only
`\nxQcmDiagnostics{<repository-relative diagnostics path>}`. Do not duplicate
literal page breaks/rubrics in `maquette.tex`, do not use an internal
`\newpage` as a signal, and do not intercept page-break commands. The tested
class interface from Task 5 closes `faireLePoint` columns exactly once and owns
the same bilateral rendering used by the professor assembler. Never hide a
double break with negative spacing.

- [ ] **Step 4: Verify source equivalence and immutable hashes**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_maquette_v5.py \
  -k 'manifest or qcm or diagnostics or immutable or source_contract' \
  -q -p no:cacheprovider
```

Expected: PASS; concatenated new bodies equal the old professor body modulo only the removed separator command; both hashes are checked.

- [ ] **Step 5: Compile and compare the full maquette**

Run from `Mathematiques/manuel-maths`:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 Mathematiques/manuel-maths/scripts/build_maquette_v5.py \
  --manifest Mathematiques/manuel-maths/build/maquette-v5/manifest.json \
  --output Mathematiques/manuel-maths/build/maquette-v5/renvois.tex
python3 Mathematiques/manuel-maths/scripts/check_maquette_v5.py \
  --manifest Mathematiques/manuel-maths/build/maquette-v5/manifest.json
```

Expected exact final summary: `MAQUETTE V5: PASS — 15 pages; blanches 6,14; renvois 2/2; marginnote colonnes 0`. All historical PNG checks remain unchanged and PASS.

- [ ] **Step 6: Stop on any visual change**

If page count or any historical PNG hash changes, preserve the generated before/after evidence outside tracked baselines, report the exact pages, and pause for a distinct human decision. Do not edit `check_maquette_v5.py` hash constants or `validations/v5*` in this lot.

- [ ] **Step 7: Implement the evidence helper already frozen by Red tests**

Use `apply_patch` against the absolute
`.../scripts/build_wave0_separation_evidence.py` target. Implement the closed
`prepare`/`check` interface and schema specified in Task 9, with no approval
mode and no generated evidence. This implementation joins the existing
generator `[PYTHON]` commit so the approved specification remains at eight
base commits; its tests remain in the first `[TESTS]` commit.

- [ ] **Step 8: Run the evidence helper Green and its stale-hash mutation**

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest tests/test_wave0_separation_evidence.py \
  -q -p no:cacheprovider
```

Expected: all evidence helper/schema tests pass, including no-overwrite and
stale-PDF rejection fixtures.

- [ ] **Step 9: Fold maquette, generator, and evidence helper into the fourth commit**

The approved design requires the Dérivation locale split and maquette migration
in the same commit. Stage the exact allowlist, inspect it, and commit:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
git status --short
git diff --check
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py \
  Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_qcm_semantic_diagnostics_boundary_contract \
  tests/test_wave0_separation_evidence.py \
  -q -p no:cacheprovider
allowed=( Mathematiques/manuel-maths/scripts/build_qcm_tex.py \
  scripts/build_wave0_separation_evidence.py \
  audit/wave0-green-p0-separation-qcm-migration-2026-08-13.json \
  Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/qcm/1SPE-DERIVATION-LOCAL-QCM.json \
  Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/qcm/1SPE-DERIVATION-GLOBAL-QCM.json \
  Mathematiques/manuel-maths/chapitres/1SPE-SUITES/qcm/1SPE-SUITES-QCM.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-SUITES/diagnostics/1SPE-SUITES-QCM-DIAGNOSTICS.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/qcm/1SPE-SECDEG-QCM.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/diagnostics/1SPE-SECDEG-QCM-DIAGNOSTICS.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/qcm/1SPE-DERIVATION-LOCAL-QCM.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/diagnostics/1SPE-DERIVATION-LOCAL-QCM-DIAGNOSTICS.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/qcm/1SPE-DERIVATION-GLOBAL-QCM.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/diagnostics/1SPE-DERIVATION-GLOBAL-QCM-DIAGNOSTICS.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/qcm/1SPE-EXPONENTIELLE-QCM.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/diagnostics/1SPE-EXPONENTIELLE-QCM-DIAGNOSTICS.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/qcm/1SPE-PRODUIT-SCALAIRE-QCM.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/diagnostics/1SPE-PRODUIT-SCALAIRE-QCM-DIAGNOSTICS.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/qcm/1SPE-VARALEA-QCM.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/diagnostics/1SPE-VARALEA-QCM-DIAGNOSTICS.tex \
  Mathematiques/manuel-maths/chapitres/TSPE-CONTINUITE/qcm/TSPE-CONTINUITE-QCM.tex \
  Mathematiques/manuel-maths/chapitres/TSPE-CONTINUITE/diagnostics/TSPE-CONTINUITE-QCM-DIAGNOSTICS.tex \
  Mathematiques/manuel-maths/build/maquette-v5/manifest.json \
  Mathematiques/manuel-maths/build/maquette-v5/maquette.tex \
  Mathematiques/manuel-maths/scripts/build_maquette_v5.py \
  Mathematiques/manuel-maths/tests/test_maquette_v5.py \
  Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls )
git add -- "${allowed[@]}"
python3 -c 'import subprocess,sys; actual=sorted(subprocess.check_output(["git","diff","--cached","--name-only"], text=True).splitlines()); expected=sorted(sys.argv[1:]); assert actual == expected, (actual, expected)' \
  "${allowed[@]}"
git diff --cached --check
test -z "$(git diff --cached --name-only | rg '\.pdf$' || true)"
git commit -m "[PYTHON] genere separement QCM et diagnostics"
test -z "$(git diff --cached --name-only)"
git status --short
```

Expected: the fourth commit contains generator/routing, the evidence helper,
the two JSON migrations,
eight student outputs, eight diagnostics outputs, maquette manifest/builder/test,
and the required minimal v5 semantic boundary. If any part was already
committed, stop and ask for human authorization before rewriting history; do
not amend automatically.

### Task 7: Move TSPE marking schemes out of the student statements

**Files:**
- Modify: `Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/evaluations/TSPE-DERIVATION-CONVEXITE-EV-A.tex`
- Modify: `Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/evaluations/TSPE-DERIVATION-CONVEXITE-EV-B.tex`
- Modify: `Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/evaluations/TSPE-DERIVATION-CONVEXITE-EV-A-corrige.tex`
- Modify: `Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/evaluations/TSPE-DERIVATION-CONVEXITE-EV-B-corrige.tex`
- Test: `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py`
- Test: `Mathematiques/manuel-maths/tests/test_p0_student_artifacts.py`

- [ ] **Step 1: Run structural evaluation tests Red**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  -k 'tspe and evaluation' -q -p no:cacheprovider
```

Expected: FAIL for visible internal IDs and five occurrences of printed points per student statement, and absent explicit marking scheme in each correction.

- [ ] **Step 2: Make the two statements public-only**

Render titles exactly `Évaluation A — Dérivation et convexité` and `Évaluation B — Dérivation et convexité`, retain `Durée : 55 min`, and remove all printed total/exercise/question points and visible internal IDs. Preserve statement questions and `% BEGIN-VERIFY` calculations unchanged; retain metadata `bareme_total: 20`.

- [ ] **Step 3: Add the full marking scheme to both teacher corrections**

At the start of each correction, print `Barème : 20 points`, then label exercises 1–4 as 5 points each. Do not expose internal IDs merely to prove routing; metadata already carries the evaluation relationship.

- [ ] **Step 4: Run structural and SymPy-backed tests Green**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  -k 'tspe and evaluation' -q -p no:cacheprovider
PYTHONPATH=Mathematiques/manuel-maths/scripts python3 - <<'PY'
from pathlib import Path
from verify_sympy import extract_scripts, run_sandbox

root = Path("Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/evaluations")
scripts = [
    (path, script)
    for path in sorted(root.glob("*.tex"))
    for script in extract_scripts(path.read_text(encoding="utf-8"))
]
assert len(scripts) == 4, len(scripts)
for path, script in scripts:
    verdict, details = run_sandbox(script)
    assert verdict == "pass", f"{path}: {details}"
print("4 blocs SymPy TSPE: PASS")
PY
```

Expected: evaluation structure PASS and `4 blocs SymPy TSPE: PASS`. This reuses
the repository verifier without calling its receipt-writing CLI.

- [ ] **Step 5: Commit pedagogy/content separately**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
git diff --check
git status --short
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_tspe_evaluation_student_teacher_contract \
  -q -p no:cacheprovider
allowed=( \
  Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/evaluations/TSPE-DERIVATION-CONVEXITE-EV-A.tex \
  Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/evaluations/TSPE-DERIVATION-CONVEXITE-EV-B.tex \
  Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/evaluations/TSPE-DERIVATION-CONVEXITE-EV-A-corrige.tex \
  Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/evaluations/TSPE-DERIVATION-CONVEXITE-EV-B-corrige.tex )
git add -- "${allowed[@]}"
python3 -c 'import subprocess,sys; actual=sorted(subprocess.check_output(["git","diff","--cached","--name-only"], text=True).splitlines()); expected=sorted(sys.argv[1:]); assert actual == expected, (actual, expected)' \
  "${allowed[@]}"
git diff --cached --check
git commit -m "[PEDAGOGIE] separe les baremes des evaluations TSPE"
test -z "$(git diff --cached --name-only)"
git status --short
```

Expected: exactly four TSPE evaluation files; no assembler or PDF.

## Chunk 3: Chapter-scoped method-link engine

### Task 8: Resolve all 63 method references to chapter-scoped exercise targets

**Files:**
- Modify: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
- Modify: `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls`
- Modify: `Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls`
- Modify: `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py`
- Create/modify: `Mathematiques/manuel-maths/tests/test_training_links.py`

- [ ] **Step 1: Run source and mapping tests Red**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_training_links.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  -k 'training or refExos or method_target or chapter_context' \
  -q -p no:cacheprovider
```

Expected: FAIL because `\refExos` emits provisional text/warnings and mapping is absent.

- [ ] **Step 2: Implement only the closed method-call parser**

Reuse the existing `% META:` boundary and add a pure parser for actual
`\refExos{M…}` occurrences returning source path, ordinal, chapter and method.
Do not select targets or emit TeX in this checkbox.

- [ ] **Step 3: Run parser fixtures Green**

Run `test_parse_training_calls_closed_contract`. Expected: ordered calls pass;
malformed META, unsupported call syntax and cross-chapter input fail closed.

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_training_links.py::test_parse_training_calls_closed_contract -q -p no:cacheprovider
```

- [ ] **Step 4: Implement only deterministic target mapping**

Add `resolve_training_targets(...)`. Select the first explicit `methodes`
target in assembly order, with only the six approved capacity fallbacks.
Zero target, duplicate label, or chapter mismatch raises `AssemblyError`.

- [ ] **Step 5: Run the pure mapping-helper contract Green**

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_training_links.py::test_resolve_training_targets_explicit_and_six_fallbacks \
  Mathematiques/manuel-maths/tests/test_training_links.py::test_resolve_training_targets_rejects_missing_duplicate_and_cross_chapter \
  -q -p no:cacheprovider
```

Expected: both helper nodes pass, with 63 mappings and exactly six fallbacks.

- [ ] **Step 6: Run chapter-context and target-label tests Red**

Run the focused source node. Expected: FAIL because chapter context and
chapter-scoped labels are absent.

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_training_links.py::test_chapter_context_and_target_labels -q -p no:cacheprovider
```

- [ ] **Step 7: Emit only chapter context and target labels**

Before each chapter opening, emit a safe chapter-context macro. Immediately before the wrapped input of each selected exercise, emit:

```tex
\phantomsection\label{nx:training:<chapter>:<method>}
```

Use lowercase/uppercase consistently and never label only by `M1`. Do not add
AUX traces or hyperlinks yet.

- [ ] **Step 8: Run context/label source tests Green**

Expected: 63 unique chapter-scoped labels and six fallback receipts.

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_training_links.py::test_chapter_context_and_target_labels -q -p no:cacheprovider
```

- [ ] **Step 9: Run AUX-token/coordinate tests Red**

Run the focused trace node. Expected: FAIL because source tokens and saved
coordinates are absent.

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_training_links.py::test_aux_tokens_and_saved_coordinates -q -p no:cacheprovider
```

- [ ] **Step 10: Emit only deterministic AUX tokens and coordinates**

Derive each token from relative method path plus ordinal. Emit token, path,
ordinal, page, x-sp, y-sp and target label via the available LuaTeX position
primitive. Reject duplicate token or missing coordinate; do not render the
final hyperlink yet.

- [ ] **Step 11: Run AUX-token/coordinate tests Green**

Expected: exactly 63 unique parseable traces and coordinates.

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_training_links.py::test_aux_tokens_and_saved_coordinates -q -p no:cacheprovider
```

- [ ] **Step 12: Run hyperlink/destination tests Red**

Run the focused `/Link` node. Expected: FAIL because annotations/destinations
are absent even though labels and AUX traces exist.

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_training_links.py::test_pdf_link_annotation_and_destination -q -p no:cacheprovider
```

- [ ] **Step 13: Implement only label-backed hyperlink rendering**

Load hyperref once. Define base/v5 `\refExos` to render the student phrase,
`\pageref`, and `\hyperref` to the active chapter/method label. Missing context
or label is a hard package error; the saved coordinate must lie in the link
rectangle.

- [ ] **Step 14: Run exhaustive source/link tests Green**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest Mathematiques/manuel-maths/tests/test_training_links.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  -k 'training or refExos or method_target or chapter_context' \
  -q -p no:cacheprovider
```

Expected: PASS with exactly 63 calls, 63 globally unique source tokens and
`(chapter, method)` mappings, six documented fallbacks, and zero unresolved
mapping.

- [ ] **Step 15: Run the missing-target mutation independently**

The focused test copies the relevant method/exercise tree under `tmp_path`,
removes one target only there, assembles from that explicit root, and requires
`AssemblyError`. Run it and prove the tracked tree is unchanged:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
before=$(git diff -- Mathematiques/manuel-maths/chapitres | sha256sum)
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_training_links.py::test_missing_target_mutation_raises_assembly_error \
  -q -p no:cacheprovider
after=$(git diff -- Mathematiques/manuel-maths/chapitres | sha256sum)
test "$before" = "$after"
```

Expected: `1 passed` and identical before/after diff hashes.

- [ ] **Step 16: Build 1SPE student for three-pass AUX proof**

Run without `--record-observed`:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  --manual 1SPE --variant eleve
```

Expected: exit 0 after three passes; no `--record-observed`.

- [ ] **Step 17: Build 1SPE teacher for three-pass AUX proof**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  --manual 1SPE --variant professeur
```

Expected: exit 0 after three passes; no `--record-observed`.

- [ ] **Step 18: Build TSPE student for three-pass AUX proof**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  --manual TSPE_2026_2027 --variant eleve
```

Expected: exit 0 after three passes; no `--record-observed`.

- [ ] **Step 19: Build TSPE teacher for three-pass AUX proof**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  --manual TSPE_2026_2027 --variant professeur
```

Expected: exit 0 after three passes; no `--record-observed`.

- [ ] **Step 20: Inspect logs and separate foreign overflow debt**

Run an explicit four-log allowlist through `rg` for undefined references and
record hbox/vbox counts per artifact in the execution log. Expected: zero
undefined-reference matches. Existing Overfull counts are foreign debt, never
owned test failures and never silently counted as Green.

- [ ] **Step 21: Verify all 63 token-coordinate-annotation-destination chains**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_training_links.py::test_63_source_tokens_match_pdf_annotations_and_destinations \
  -q -p no:cacheprovider
```

Expected: PASS; set equality holds between 63 source tokens, 63 AUX
coordinates, 63 unique `/Link` rectangles containing those coordinates, and 63
resolved destinations. Each destination page object contains the selected
exercise target. Missing/extra/many-to-one annotations, text without an
annotation, or a wrong page is FAIL.

- [ ] **Step 22: Commit the link engine atomically**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
git diff --check
git status --short
python3 -m pytest Mathematiques/manuel-maths/tests/test_training_links.py \
  -q -p no:cacheprovider
allowed=( Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  Mathematiques/manuel-maths/gabarits/nexus-manuel.cls \
  Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls \
  Mathematiques/manuel-maths/tests/test_training_links.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py )
git add -- "${allowed[@]}"
python3 -c 'import subprocess,sys; actual=sorted(subprocess.check_output(["git","diff","--cached","--name-only"], text=True).splitlines()); expected=sorted(sys.argv[1:]); assert actual == expected, (actual, expected)' \
  "${allowed[@]}"
git diff --cached --check
git commit -m "[LATEX] resout les renvois methodes vers les exercices"
test -z "$(git diff --cached --name-only)"
git status --short
```

Expected: link mapping/rendering/tests only; no PDFs or baselines.

---

## Chunk 4: Build the four editions and seal intermediate evidence

### Task 9: Add a deterministic visual-evidence contract

**Files:**
- Verify (implemented in commit 4): `scripts/build_wave0_separation_evidence.py`
- Test (already committed Red): `tests/test_wave0_separation_evidence.py`
- Create later: `audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json`
- Create later: `audit/visual-wave0-green-p0-separation-2026-08-13/pages/**`
- Create later: `audit/visual-wave0-green-p0-separation-2026-08-13/contact-sheets/**`

- [ ] **Step 1: Re-run the committed evidence schema and implementation Green**

The first `[TESTS]` commit contains fixtures for one changed-page PDF and four
artifact entries. They require this exact top-level contract:

```json
{
  "schema_version": 1,
  "artifact_identity": "wave0-separation-intermediate",
  "review_run": "2026-08-13-r1",
  "supersedes": null,
  "decision": {
    "status": "pending",
    "approved_by": null,
    "approved_at": null,
    "scope": "visual-separation-only"
  },
  "artifacts": {},
  "tool_versions": {}
}
```

The object keys are exactly `1SPE:eleve`, `1SPE:professeur`,
`TSPE_2026_2027:eleve`, and `TSPE_2026_2027:professeur`. Each value requires
`path`, `before_sha256`, `after_sha256`, `page_count`, `affected_pages`,
`page_evidence`, `contact_sheet`, and
`overfull_debt: {"hbox": <int>, "vbox": <int>}`. Each page-evidence entry
requires the page number, before/after/diff image paths, and all three image
SHA-256 values.

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest tests/test_wave0_separation_evidence.py \
  -q -p no:cacheprovider
```

Expected: PASS because commit 4 implements the frozen Red contract. The tests
reject a wrong artifact identity, a missing artifact, a stale PDF/image hash,
an undeclared Overfull count, `approved` without approver/date/scope, reuse of
an existing output directory, and a rebuilt PDF divergent from an old
approval.

- [ ] **Step 2: Inspect the closed preparation interface before use**

Confirm the versioned CLI exposes two modes only:

```text
build_wave0_separation_evidence.py prepare --before-root DIR --after-root DIR --output DIR --dpi 150
build_wave0_separation_evidence.py check --manifest FILE --require-status pending|approved
```

`prepare` rasterizes every before/after page to a temporary directory, compares
page PNG hashes, and copies only changed/missing page pairs and their visual
diffs into `pages/`. It creates one contact sheet per artifact, records tool
versions (`python`, `pdftoppm`, `pdftotext`, `qpdf`, `lualatex`), PDF/page/image
hashes, and exact Overfull counts from the four after-build logs. It always
records the output-directory review-run suffix and optional `supersedes`
pointer. It refuses an existing output directory, then writes
`decision.status = "pending"`; the program has no `approve` mode.

`check` resolves every path relative to the repository, recalculates every
declared SHA-256, verifies all four canonical PDFs, and rejects unknown or
missing keys. It never changes the manifest.

- [ ] **Step 3: Re-run the stale-hash mutation independently**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest tests/test_wave0_separation_evidence.py \
  -q -p no:cacheprovider
```

Expected: PASS. The fixture copy after `prepare` makes `check` fail with exact
`after_sha256 mismatch`; restoring the fixture makes the same check return 0.
No commit occurs in this task.

### Task 10: Rebuild and qualify the four canonical PDFs

**Files:**
- Modify by build only: `Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf`
- Modify by build only: `Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf`
- Modify by build only: `Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf`
- Modify by build only: `Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.pdf`

- [ ] **Step 1: Preserve the four immutable before-build PDFs**

Run once; stop if the explicit temporary directory already exists:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
before_root=/tmp/nexus-wave0-separation-before-launch
launch_base=$(git merge-base \
  green/p0-student-separation wave0/p0-green-launch)
test ! -e "$before_root"
mkdir -p "$before_root/MANUEL_1SPE" \
  "$before_root/MANUEL_TSPE_2026-2027"
git show "$launch_base":Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf \
  > "$before_root/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf"
git show "$launch_base":Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf \
  > "$before_root/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf"
git show "$launch_base":Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf \
  > "$before_root/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf"
git show "$launch_base":Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.pdf \
  > "$before_root/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.pdf"
sha256sum "$before_root"/*/*.pdf
```

Expected: four non-empty PDFs and four recorded hashes. Keep this exact
directory through Task 11; it is evidence input, not a tracked baseline.

- [ ] **Step 2: Verify only the exact separation-owned nodes before building**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
for chapter in \
  1SPE-SUITES 1SPE-SECOND-DEGRE 1SPE-DERIVATION-LOCAL \
  1SPE-DERIVATION-GLOBAL 1SPE-EXPONENTIELLE \
  1SPE-PRODUIT-SCALAIRE 1SPE-VARIABLES-ALEATOIRES \
  TSPE-CONTINUITE; do
  python3 Mathematiques/manuel-maths/scripts/build_qcm_tex.py \
    --chap "$chapter" --check
done
python3 -m pytest \
  tests/test_student_text_policy.py \
  tests/test_wave0_separation_evidence.py \
  Mathematiques/manuel-maths/tests/test_qcm_math_p0.py \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py \
  Mathematiques/manuel-maths/tests/test_training_links.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_p0_student_pdf_text_gate_rejects_observed_leaks \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_student_pdf_text_gate_accepts_student_instructions \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_shared_student_text_policy_delegation \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_qcm_diagnostics_routing_and_bilateral_boundary \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_tspe_evaluation_student_teacher_contract \
  tests/test_build_manifest.py::test_p0_recorder_student_gate_rejects_observed_leaks \
  tests/test_build_manifest.py::test_recorder_student_text_gate_allows_correction_instructions \
  tests/test_build_manifest.py::test_shared_student_text_policy_delegation \
  -q -p no:cacheprovider
```

Expected: PASS for exactly the owned files/nodes listed above. These three new
node names in the modified historical files are part of the Red contract and
must be created with exactly these names; do not replace this allowlist with
`-k` or a whole historical file.

- [ ] **Step 3: Record the known foreign producer-surface debt separately**

Run only the foreign node, never in the owned Green invocation:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
set +e
python3 -m pytest \
  tests/test_build_manifest.py::test_versioned_build_producers_register_exact_1nsi_manual_surface \
  -q -p no:cacheprovider > /tmp/green-p0-separation-foreign-producer.log 2>&1
status=$?
set -e
test "$status" -eq 1
rg -n '^1 failed in ' /tmp/green-p0-separation-foreign-producer.log
```

Expected: the known non-separation node remains a separately reported failure.
Any PASS or different failure is new evidence to investigate, not a reason to
change an owned expectation.

- [ ] **Step 4: Build the 1SPE student edition**

Run exactly, without `--record-observed`:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py --manual 1SPE --variant eleve
```

Expected: exit 0 after three LuaLaTeX passes; preserve its log.

- [ ] **Step 5: Build the 1SPE teacher edition**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py --manual 1SPE --variant professeur
```

Expected: exit 0 after three LuaLaTeX passes; preserve its log.

- [ ] **Step 6: Build the TSPE student edition**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py --manual TSPE_2026_2027 --variant eleve
```

Expected: exit 0 after three LuaLaTeX passes; preserve its log.

- [ ] **Step 7: Build the TSPE teacher edition**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py --manual TSPE_2026_2027 --variant professeur
```

Expected: exit 0 after three LuaLaTeX passes. The four build checkboxes each
own one artifact only; `audit/BUILD_MANIFEST.json` is untouched.

- [ ] **Step 8: Inspect logs and record hashes separately from builds**

Run an explicit four-log allowlist. Assert zero undefined references, record
the hbox/vbox counts separately as foreign overflow debt, then run `sha256sum`
on the explicit four-PDF allowlist into
`/tmp/green-p0-separation-after.sha256`. Expected: four hashes and no build
failure hidden in a pipeline.

- [ ] **Step 9: Run PDF preflight independently of the builds**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
for pdf in \
  Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf \
  Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf \
  Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf \
  Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.pdf
do
  qpdf --check "$pdf"
  pdffonts "$pdf" | awk 'NR > 2 && $(NF-4) != "yes" { bad=1 } END { exit bad }'
  pdfinfo "$pdf" | rg '^(Pages|Page size|PDF version):'
done
```

Expected: all qpdf checks exit 0, every listed font is embedded, and all four
PDFs report a non-zero page count.

- [ ] **Step 10: Extract and make the exact fifteen sealed Red cases Green**

Run only the fifteen cases approved at `c50e455e`: six assembler policy cases,
six recorder policy cases, two real-PDF cases, and the single Mathématiques
non-false-positive case.

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_p0_student_pdf_text_gate_rejects_observed_leaks \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_student_pdf_text_gate_accepts_student_instructions \
  tests/test_build_manifest.py::test_p0_recorder_student_gate_rejects_observed_leaks \
  Mathematiques/manuel-maths/tests/test_p0_student_artifacts.py \
  --collect-only -q -p no:cacheprovider
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_p0_student_pdf_text_gate_rejects_observed_leaks \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_student_pdf_text_gate_accepts_student_instructions \
  tests/test_build_manifest.py::test_p0_recorder_student_gate_rejects_observed_leaks \
  Mathematiques/manuel-maths/tests/test_p0_student_artifacts.py \
  -q -p no:cacheprovider
```

Expected: collection summary exactly `15 tests collected`; execution summary
exactly `15 passed`. Any collection drift is a contract change and stops the
lot.

- [ ] **Step 11: Prove professor retention and bilateral PDF boundaries**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_professor_keeps_all_eight_diagnostics \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_tspe_evaluation_student_teacher_contract \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_professor_diagnostics_bilateral_pdf_pages \
  -q -p no:cacheprovider
```

Expected: PASS for all eight professor diagnostics bodies, both TSPE marking
schemes, preceding `Auto-évaluation` pages, first/last `Corrigés` pages, and a
clean first page of the following object. Zero teacher material is lost.

- [ ] **Step 12: Verify the 63 PDF links as a separate artifact gate**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_training_links.py::test_63_source_tokens_match_pdf_annotations_and_destinations \
  -q -p no:cacheprovider
```

Expected: `1 passed`; the node proves the complete token/coordinate/annotation/
destination bijection and is not conflated with builds, log counts, or hashes.

### Task 11: Generate evidence and pause for human visual approval

**Files:**
- Create: `audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json`
- Create: `audit/visual-wave0-green-p0-separation-2026-08-13/pages/**`
- Create: `audit/visual-wave0-green-p0-separation-2026-08-13/contact-sheets/**`

- [ ] **Step 1: Prepare the pending manifest and all changed-page evidence**

Run from the repository root:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 scripts/build_wave0_separation_evidence.py prepare \
  --before-root /tmp/nexus-wave0-separation-before-launch \
  --after-root Mathematiques/manuel-maths/build \
  --output audit/visual-wave0-green-p0-separation-2026-08-13 \
  --dpi 150
python3 scripts/build_wave0_separation_evidence.py check \
  --manifest audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --require-status pending
```

Expected: exit 0; identity is `wave0-separation-intermediate`; all four
canonical PDF `after_sha256` values match the working tree; every affected page
has before/after/diff images and belongs to exactly one contact sheet. The
manifest explicitly records residual hbox/vbox counts and remains NO-GO.

- [ ] **Step 2: Inspect textual and page-level changes before asking approval**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
git diff --numstat -- \
  Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf \
  Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf \
  Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf \
  Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.pdf
python3 -m pytest tests/test_wave0_separation_evidence.py \
  -q -p no:cacheprovider
```

Open all four generated contact sheets and every non-empty diff image. Confirm
no clipped/hidden text, no unexpected page-sharing around diagnostics, stable
v5 maquette pages, correct headers, and no student-visible key, marking scheme,
internal ID, or provisional method reference.

- [ ] **Step 3: PAUSE — obtain explicit human approval or rejection**

Present the manifest, four contact sheets, affected-page list, and declared
Overfull debt. Stop until a named human responds with an explicit decision for
the exact four `after_sha256` values. Silence, prior design approval, or an
agent review is not visual approval.

If rejected, set no approval fields, preserve the pending evidence, and return
to the owning task. Do not update a baseline or commit PDFs.

- [ ] **Step 4: Record only the human decision after approval**

After explicit approval, use `apply_patch` with exact target
`/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation/audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json`
to change only:

```json
"status": "approved",
"approved_by": "<human name>",
"approved_at": "<ISO-8601 date-time with zone>",
"scope": "visual-separation-only"
```

Then run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 scripts/build_wave0_separation_evidence.py check \
  --manifest audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --require-status approved
```

Expected: PASS. Approval is limited to the intermediate visual separation; it
does not approve residual Overfull debt, publication, or any baseline change.

- [ ] **Step 5: Lock the approval to this run and define the divergence stop**

Record that `2026-08-13-r1` approval is valid only for its four exact
`after_sha256` values. If any later rebuild differs, the current artifacts are
immediately unapproved: do not edit or overwrite this directory or decision.
Create a new directory such as
`audit/visual-wave0-green-p0-separation-2026-08-13-r2/`, set
`review_run = 2026-08-13-r2`, `supersedes` to the r1 manifest path and decision
to `pending`, regenerate all affected evidence/contact sheets, and repeat the
named human review. Only the new approved run may be staged. The old run stays
immutable historical proof; divergence can never inherit its approval.

### Task 12: Commit only the approved audit account

**Files:**
- Modify: `README.md`
- Add: evidence files from Tasks 9 and 11

- [ ] **Step 1: Update README claims through the proven state only**

Using `apply_patch` with exact target
`/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation/README.md`,
document the JSON-to-two-TeX QCM flow, shared student-text
policy, professor-only diagnostics, TSPE evaluation separation, 63 real method
links, the four approved intermediate PDFs, and the visual manifest path. Keep
the project verdict **NO-GO publication** and list Overfull, PDF metadata,
bookmarks, and global-link work as open.

- [ ] **Step 2: Verify the approved evidence immediately before staging**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 scripts/build_wave0_separation_evidence.py check \
  --manifest audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --require-status approved
python3 -m pytest tests/test_wave0_separation_evidence.py \
  -q -p no:cacheprovider
```

Expected: PASS and exact approved hashes. Do not run the inventory generator:
the changed tracked sources intentionally make its observed build
`source_digest` stale, and this lot may neither rebind nor record that manifest.

- [ ] **Step 3: Stage and commit proof material without code, tests, or PDFs**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
git status --short
git diff --check
git add README.md audit/visual-wave0-green-p0-separation-2026-08-13
python3 - <<'PY'
import json
import subprocess
from pathlib import Path

manifest = Path("audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json")
payload = json.loads(manifest.read_text(encoding="utf-8"))
expected = {"README.md", manifest.as_posix()}
for artifact in payload["artifacts"].values():
    expected.add(artifact["contact_sheet"])
    for page in artifact["page_evidence"]:
        expected.update((page["before"], page["after"], page["diff"]))
actual = set(subprocess.check_output(
    ["git", "diff", "--cached", "--name-only"], text=True
).splitlines())
assert actual == expected, (sorted(actual), sorted(expected))
PY
git diff --cached --check
test -z "$(git diff --cached --name-only | rg '(^scripts/|^tests/|\.pdf$)' || true)"
test -z "$(git diff --cached --name-only | rg '^(ETAT_COLLECTION.md|audit/(INVENTAIRE_COLLECTION|AUDIT_CONSOLIDE|ECARTS_ET_CONTRADICTIONS|MATRICE_LIVRABLES))' || true)"
python3 scripts/build_wave0_separation_evidence.py check \
  --manifest audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --require-status approved
git commit -m "[AUDIT] consigne la revue visuelle intermediaire"
test -z "$(git diff --cached --name-only)"
git status --short
```

Expected: the seventh commit contains only the human-reviewed evidence tree and
its README account, but no implementation, test, generated inventory report,
canonical PDF, observed manifest, or baseline mutation.

### Task 13: Commit exactly the four human-approved PDFs

- [ ] **Step 1: Prove approval hashes immediately before staging**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 scripts/build_wave0_separation_evidence.py check \
  --manifest audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --require-status approved
git status --short
```

Expected: PASS and exactly four modified canonical PDFs remain unstaged.

- [ ] **Step 2: Stage the exact PDF allowlist**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
git status --short
git diff --check
allowed=( \
  Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf \
  Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf \
  Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf \
  Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.pdf )
git add -- "${allowed[@]}"
python3 -c 'import subprocess,sys; actual=sorted(subprocess.check_output(["git","diff","--cached","--name-only"], text=True).splitlines()); expected=sorted(sys.argv[1:]); assert actual == expected, (actual, expected)' \
  "${allowed[@]}"
git diff --cached --check
python3 scripts/build_wave0_separation_evidence.py check \
  --manifest audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --require-status approved
```

Expected: exactly the approved four PDF blobs are staged and all hashes still
match.

- [ ] **Step 3: Commit the intermediate artifacts separately**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
git status --short
git diff --cached --check
python3 scripts/build_wave0_separation_evidence.py check \
  --manifest audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --require-status approved
git commit -m "[PDF] versionne les editions separees intermediaires"
test -z "$(git diff --cached --name-only)"
git status --short
```

Expected: the eighth base commit contains only four PDFs. These artifacts retain
identity `wave0-separation-intermediate` and **NO-GO**, ready to be consumed by
the overflow lot; they are not observed builds or release candidates.

---

## Chunk 5: Final gates, independent reviews, and handoff

### Task 14: Verify the complete separation lot

- [ ] **Step 1: Run the TSPE evaluation scripts without generating receipts**

The repository has no `test_generated_status.py`; this exact read-only command
is the authoritative replacement for the placeholder discovery command in
Task 7 Step 4:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
PYTHONPATH=Mathematiques/manuel-maths/scripts python3 - <<'PY'
from pathlib import Path
from verify_sympy import extract_scripts, run_sandbox

root = Path("Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/evaluations")
count = 0
for path in sorted(root.glob("*.tex")):
    scripts = extract_scripts(path.read_text(encoding="utf-8"))
    assert scripts, f"bloc BEGIN-VERIFY absent: {path}"
    for script in scripts:
        verdict, details = run_sandbox(script)
        assert verdict == "pass", f"{path}: {details}"
        count += 1
assert count == 4, count
print("4 blocs SymPy TSPE: PASS")
PY
```

Expected: `4 blocs SymPy TSPE: PASS`; no validation JSON is written.

- [ ] **Step 2: Run the exact separation-owned source and artifact nodes**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_p0_student_artifacts.py \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py \
  Mathematiques/manuel-maths/tests/test_qcm_math_p0.py \
  Mathematiques/manuel-maths/tests/test_training_links.py \
  tests/test_student_text_policy.py \
  tests/test_wave0_separation_evidence.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_p0_student_pdf_text_gate_rejects_observed_leaks \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_student_pdf_text_gate_accepts_student_instructions \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_shared_student_text_policy_delegation \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_qcm_diagnostics_routing_and_bilateral_boundary \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_tspe_evaluation_student_teacher_contract \
  tests/test_build_manifest.py::test_p0_recorder_student_gate_rejects_observed_leaks \
  tests/test_build_manifest.py::test_recorder_student_text_gate_allows_correction_instructions \
  tests/test_build_manifest.py::test_shared_student_text_policy_delegation \
  Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_canonical_manifest_contract \
  Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_qcm_hash_is_immutable \
  Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_qcm_and_corrections_source_contract \
  Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_qcm_semantic_diagnostics_boundary_contract \
  Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_page13_diagnostics_layout_pdf \
  Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_qcm_diagnostics_and_corrections_pdf \
  Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_maquette_v5_acceptance \
  -q -p no:cacheprovider
```

Expected: every listed owned node passes. Run the exact foreign producer node
from Task 10 Step 3 separately and retain its expected one-failure log; never
collect the entire historical recorder file in the owned Green result.

- [ ] **Step 3: Re-run deterministic generators, maquette, and PDF checks**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
for chapter in \
  1SPE-SUITES 1SPE-SECOND-DEGRE 1SPE-DERIVATION-LOCAL \
  1SPE-DERIVATION-GLOBAL 1SPE-EXPONENTIELLE \
  1SPE-PRODUIT-SCALAIRE 1SPE-VARIABLES-ALEATOIRES \
  TSPE-CONTINUITE; do
  python3 Mathematiques/manuel-maths/scripts/build_qcm_tex.py \
    --chap "$chapter" --check
done
python3 Mathematiques/manuel-maths/scripts/check_maquette_v5.py \
  --manifest Mathematiques/manuel-maths/build/maquette-v5/manifest.json
python3 scripts/build_wave0_separation_evidence.py check \
  --manifest audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --require-status approved
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_training_links.py::test_63_source_tokens_match_pdf_annotations_and_destinations \
  -q -p no:cacheprovider
```

Expected: generator/checker PASS, exact historical maquette summary preserved,
four approved hashes current, and all 63 PDF destinations valid.

- [ ] **Step 4: Record the four approved hashes before rebuilding**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
sha256sum \
  Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf \
  Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf \
  Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf \
  Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.pdf \
  > /tmp/nexus-wave0-separation-before-rebuild.sha256
```

Expected: four hash lines exactly matching the approved manifest.

- [ ] **Step 5: Rebuild 1SPE student without recording observed state**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py --manual 1SPE --variant eleve
```

Expected: exit 0; one build only.

- [ ] **Step 6: Rebuild 1SPE teacher without recording observed state**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py --manual 1SPE --variant professeur
```

Expected: exit 0; one build only.

- [ ] **Step 7: Rebuild TSPE student without recording observed state**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py --manual TSPE_2026_2027 --variant eleve
```

Expected: exit 0; one build only.

- [ ] **Step 8: Rebuild TSPE teacher without recording observed state**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py --manual TSPE_2026_2027 --variant professeur
```

Expected: exit 0; one build only.

- [ ] **Step 9: Compare rebuilt hashes and enforce approval invalidation**

Run the comparison separately from all builds:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
set +e
sha256sum --check /tmp/nexus-wave0-separation-before-rebuild.sha256
hash_status=$?
set -e
test "$hash_status" -eq 0
```

Expected: status 0 and four `OK` lines. If nonzero, the old visual approval is
invalid for the current artifacts: the explicit test fails and execution
stops; do not overwrite r1 evidence or
commit PDFs, create a new `-r2` evidence directory with `supersedes`, return to
Tasks 10–13, obtain a fresh human decision, then add atomic corrective
`[AUDIT]` and `[PDF]` commits. A divergent rebuild can never inherit approval.

- [ ] **Step 10: Prove the expected worktree inventory failure as JSON**

Run after the eight base commits when the tree is clean; repeat this exact step
after every later review correction:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
set -uo pipefail
set +e
inventory_output=$(python3 scripts/inventory_collection.py --check --require-clean 2>&1)
inventory_status=$?
set -euo pipefail
printf '%s\n' "$inventory_output" | tee /tmp/green-p0-separation-inventory.log
test "$inventory_status" -eq 3
printf '%s\n' "$inventory_output" | python3 -c '
import json, sys
payload = json.loads(sys.stdin.read().splitlines()[-1])
assert payload["gate"] == "check"
assert payload["exit_code"] == 3
assert payload["reasons"] == [
    "check_error:source_digest du manifeste de build incohérent"
]
'
```

Expected: code 3 and exactly the single `source_digest` JSON reason. A branch
provenance string, dirty-tree reason, extra reason, or piped-away exit code is
a blocker. Never regenerate/rebind `audit/BUILD_MANIFEST.json` here.

- [ ] **Step 11: Run final Git and base-commit governance checks**

Run:

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-student-separation
cd "$target"
test "$(pwd -P)" = "$target"
launch_base=$(git merge-base \
  green/p0-student-separation wave0/p0-green-launch)
git diff --check "$launch_base"..HEAD
test "$(git rev-list --count "$launch_base"..HEAD)" -ge 8
git log --reverse --format='%s' "$launch_base"..HEAD \
  > /tmp/green-p0-separation-subjects.txt
python3 - <<'PY'
from pathlib import Path

subjects = Path("/tmp/green-p0-separation-subjects.txt").read_text(encoding="utf-8").splitlines()
base = [
    "[TESTS] precise le contrat structurel des variantes",
    "[MATH] corrige les deux incoherences QCM",
    "[PYTHON] centralise la politique de separation eleve",
    "[PYTHON] genere separement QCM et diagnostics",
    "[PEDAGOGIE] separe les baremes des evaluations TSPE",
    "[LATEX] resout les renvois methodes vers les exercices",
    "[AUDIT] consigne la revue visuelle intermediaire",
    "[PDF] versionne les editions separees intermediaires",
]
assert subjects[:8] == base, subjects[:8]
allowed_review = {
    "[TESTS] repond a la revue separation eleve",
    "[MATH] repond a la revue separation eleve",
    "[PYTHON] repond a la revue separation eleve",
    "[PEDAGOGIE] repond a la revue separation eleve",
    "[LATEX] repond a la revue separation eleve",
    "[AUDIT] repond a la revue separation eleve",
    "[PDF] repond a la revue separation eleve",
}
assert all(subject in allowed_review for subject in subjects[8:]), subjects[8:]
print(f"8 base commits + {len(subjects) - 8} atomic review commits: PASS")
PY
git status --short --branch
```

Expected: clean tree, eight immutable base commits in the exact order above,
then zero or more atomic review commits using only the closed subjects. For
each review commit, inspect `git diff-tree --no-commit-id --name-only -r <sha>`:
its prefix must match one ownership lane, `[AUDIT]` may contain only README and
the evidence directory, and `[PDF]` only the four canonical PDFs. Never amend,
squash, or rewrite the eight base commits to satisfy a review.

On the attested integration checkout, run `inventory_collection.py --check
--release-strict --require-clean` and record expected exit 7. Metadata,
bookmarks, global links, and declared Overfull debt remain release blockers;
the manual remains **NO-GO publication**.

- [ ] **Step 12: Request two independent read-only reviews**

Use `superpowers:requesting-code-review` and dispatch two reviewers in parallel:

1. specification/compliance review against `AGENTS.md`, the cahier des charges,
   approved spec, Red commit `c50e455e`, and the complete eight-base-plus-review diff;
2. implementation/quality review covering math reviewer evidence, source
   authority, generator atomicity, variant preservation, 63 PDF links, builds,
   and manifest/hash integrity.

Each reviewer returns `✅ Approved` or blocking findings with path/line and a
minimal required correction. Stop on any blocking finding. Neither reviewer
may replace the named human visual approval or the independent math review.

- [ ] **Step 13: Apply any review finding through a fresh atomic TDD cycle**

For each blocking finding, first write a 2–5 minute micro-plan that names the
exact absolute test and production paths, exact pytest node, expected Red
message, mutation, and one allowed review subject. Use `apply_patch` on the
absolute test path; run only that node and capture exit 1 plus the expected
failure. Then patch the exact production path minimally, run the same node
Green and its mutation, followed by all owned gates.

Before every review commit, run `git status --short`, tests, `git diff
--check`, define a literal Bash `allowed=(...)` array containing every and only
the exact repository-relative paths for that finding, stage with `git add --
"${allowed[@]}"`, compare the cached path set to the array, run `git diff
--cached --check`, commit with the closed lane subject, assert the index empty,
and print status. No glob, amend, squash, mixed lane, or direct fix without a
fresh Red observation is allowed. A source/layout correction invalidates prior
PDF approval until Tasks 10–13 are replayed; a mathematical correction also
requires a new independent disciplinary review. Rerun Steps 1–11, then request
both independent reviews again until both approve.

- [ ] **Step 14: PAUSE — human handoff before integration or push**

Use `superpowers:verification-before-completion`, then
`superpowers:finishing-a-development-branch`. Present the eight base commits plus
any atomic review commits, exact
test counts, four PDF hashes, manifest decision, residual gate debt, review
verdicts, and this mandatory status block:

```text
ÉTAT <SHA>
Branche : green/p0-student-separation
Phase : Green P0 — séparation élève terminée, intégration en attente
Commits : <8 base SHAs and subjects; then review commits if any>
Tests : <exact commands/counts>
Gates verts : <targeted gates>
Gates rouges : release-strict=7; Overfull/métadonnées/signets/liens globaux
P0 ouverts : <none in this lot; list all out-of-scope P0s>
Décisions humaines : math review; visual approver/date/scope
PR : non créée sauf instruction explicite
Prochaine action : décision humaine merge/push or overflow stacked lot
```

Do not merge, rebase, push, record observed builds, or update visual/debt
baselines without a new explicit human instruction.
