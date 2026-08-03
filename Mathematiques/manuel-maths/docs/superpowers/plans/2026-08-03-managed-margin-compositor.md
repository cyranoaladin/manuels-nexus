# Managed Margin Compositor Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace independent `\marginnote` placement in the complete 1SPE manuals with a deterministic LuaTeX compositor that keeps every pedagogical annotation in the outer margin without collisions.

**Architecture:** TeX captures every annotation once into a Lua node-list and records an anchor. A pure Lua solver computes stable outer-margin placements over bounded compilation passes, including obstacles and ordered page reports. The final PDF exposes controlled marked contents and Form XObjects; a Python postflight cross-checks those objects, the capture inventory and the geometry ledger before the assembler may publish the PDF.

**Tech Stack:** LuaHBTeX 1.17 / TeX Live 2023, LaTeX3, Lua 5.3 via `texlua`, Python 3.12, pytest, pikepdf, Poppler bbox extraction, JSON Schema, existing atomic build/receipt pipeline.

**Approved design:** `Mathematiques/manuel-maths/docs/superpowers/specs/2026-08-03-managed-margin-compositor-design.md`

**Execution anchor:** Before Task 1, record the commit containing this approved plan as `starting_sha`. Preserve that value in the final review README; all baseline and changed-page comparisons use this fixed SHA, not a later implementation commit.

---

## File structure

### New production files

- `Mathematiques/manuel-maths/gabarits/nexus-margin-rail.tex` — public-to-internal TeX adapters, one-time note boxing, anchor overlays, safe rectangles and Lua callbacks.
- `Mathematiques/manuel-maths/gabarits/nexus-margin-layout.lua` — deterministic pure placement solver, canonical state comparison and bounded-report rules.
- `Mathematiques/manuel-maths/gabarits/nexus-margin-json.lua` — self-contained strict JSON decoding plus canonical sorted-key encoding shared by LuaTeX and the solver CLI.
- `Mathematiques/manuel-maths/gabarits/nexus-margin-shipout.lua` — per-pass node-list registry, Form XObject/marked-content emission and final capture inventory.
- `Mathematiques/manuel-maths/scripts/solve_margin_layout.lua` — thin `texlua` CLI around the pure layout module; no persistence or TeX state.
- `Mathematiques/manuel-maths/scripts/margin_contract.py` — shared JSON Schema and semantic validation for layout and ledger evidence.
- `Mathematiques/manuel-maths/scripts/margin_ledger.py` — inspect the produced PDF, reconstruct the canonical ledger and validate capture/placement/PDF bijections.
- `Mathematiques/manuel-maths/schemas/margin-layout.schema.json` — closed schema for canonical pass state.
- `Mathematiques/manuel-maths/schemas/margin-stable-layout.schema.json` — nonce-free canonical placement payload admitted to observed evidence.
- `Mathematiques/manuel-maths/schemas/margin-ledger.schema.json` — closed schema for the final PDF-derived ledger.

### New tests

- `Mathematiques/manuel-maths/tests/test_margin_layout.py` — pure Lua solver and convergence protocol.
- `Mathematiques/manuel-maths/tests/test_margin_compositor_pdf.py` — real LuaLaTeX fixtures, recto-verso, breakable boxes, reports and student/teacher payloads.
- `Mathematiques/manuel-maths/tests/test_margin_ledger.py` — PDF object, marked-content, ledger and bbox adversarial tests.
- `Mathematiques/manuel-maths/tests/fixtures/margin-layout.valid.json` — minimal complete canonical layout envelope.
- `Mathematiques/manuel-maths/tests/fixtures/margin-stable-layout.valid.json` — minimal nonce-free stable placement payload.
- `Mathematiques/manuel-maths/tests/fixtures/margin-ledger.valid.json` — minimal complete PDF-derived ledger.

### Existing files modified

- `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls` — load the compositor and route five existing margin-producing components through it.
- `Mathematiques/manuel-maths/scripts/assemble_manuel.py` — bounded stable-pass loop, postflight, promotion and receipt dependencies.
- `Mathematiques/manuel-maths/scripts/pdf_integrity.py` — invoke the margin postflight as a mandatory check.
- `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py` — fake-runner state machine and closed evidence assertions.
- `Mathematiques/manuel-maths/tests/test_pdf_integrity.py` — fail-closed margin proof contract.
- `scripts/build_manifest.py` and `tests/test_build_manifest.py` — prove the two generated dependencies through the recorder and their digests.
- `audit/schemas/v1/build-manifest.schema.json` — admit the recorded `qpdf`/`pikepdf` tool evidence if required by the final parser route.
- `.github/workflows/ci-mathematiques.yml` and `.github/workflows/ci-audit-collection.yml` — install the frozen PDF-inspection dependency and publish review artefacts.

---

## Chunk 1: Closed contracts and deterministic placement solver

### Task 1: Freeze the layout and ledger schemas

**Files:**
- Create: `Mathematiques/manuel-maths/schemas/margin-layout.schema.json`
- Create: `Mathematiques/manuel-maths/schemas/margin-stable-layout.schema.json`
- Create: `Mathematiques/manuel-maths/schemas/margin-ledger.schema.json`
- Create: `Mathematiques/manuel-maths/tests/fixtures/margin-layout.valid.json`
- Create: `Mathematiques/manuel-maths/tests/fixtures/margin-stable-layout.valid.json`
- Create: `Mathematiques/manuel-maths/tests/fixtures/margin-ledger.valid.json`
- Create: `Mathematiques/manuel-maths/scripts/margin_contract.py`
- Modify: `Mathematiques/manuel-maths/tests/test_meta_schemas.py`

- [ ] **Step 1: Write failing schema-registration tests**

Create `tests/fixtures/`, then add parametrized tests that load all three schemas with `jsonschema.Draft202012Validator.check_schema`, validate one canonical fixture through `margin_contract`, and reject extra keys, floating-point dimensions, an invalid SHA-256 and, for the private envelope only, a non-32-hex layout run nonce. Import it like the existing manual-local helpers—prepend `MANUAL_ROOT / "scripts"` to `sys.path`, then `import margin_contract`—because the repository-root `scripts` package would otherwise mask this directory. Add separate semantic-validator tests for duplicate IDs, duplicate `shipout_index` values and broken page/note references; JSON Schema alone cannot express those relations for object records.

```python
@pytest.mark.parametrize(
    "schema_name,fixture_name",
    [
        ("margin-layout.schema.json", "margin-layout.valid.json"),
        ("margin-stable-layout.schema.json", "margin-stable-layout.valid.json"),
        ("margin-ledger.schema.json", "margin-ledger.valid.json"),
    ],
)
def test_margin_proof_schemas_are_closed(schema_name, fixture_name):
    schema = json.loads((SCHEMAS / schema_name).read_text(encoding="utf-8"))
    fixture = json.loads((FIXTURES / fixture_name).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert not list(Draft202012Validator(schema).iter_errors(fixture))
    fixture["unexpected"] = True
    assert list(Draft202012Validator(schema).iter_errors(fixture))
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```bash
pytest -q Mathematiques/manuel-maths/tests/test_meta_schemas.py -k margin_proof
```

Expected: FAIL because the three schema files and fixtures are absent.

- [ ] **Step 3: Add closed schemas and minimal valid fixtures**

Freeze one representation used by schema, CLI, Lua solver and TeX. The only public algorithm is:

```text
solve(current_layout, previous_layout_or_nil) -> next_layout
```

The layout schema must require exactly these root keys:

```json
{
  "schema_version": 1,
  "run_nonce": "0123456789abcdef0123456789abcdef",
  "variant": "eleve",
  "geometry_digest": "sha256:...",
  "semantic_digest": "sha256:...",
  "state": "stable",
  "pass_number": 3,
  "max_passes": 6,
  "read_digest": "sha256:...",
  "computed_digest": "sha256:...",
  "error_code": null,
  "notes": [],
  "pages": []
}
```

Every coordinate and dimension is an integer scaled point. Each page requires unique `shipout_index`, `folio`, `page_width_sp`, `page_height_sp`, `rail_side`, `safe_rect`, `native_note_ids`, `carry_in_note_ids`, `placed_note_ids`, `reported_note_ids` and page-local `obstacles`. Every obstacle requires a globally unique `id` and `left_sp`, `top_sp`, `right_sp`, `bottom_sp`. Each top-level note requires `id`, `role`, `global_order`, `origin_shipout_index`, `origin_folio`, `origin_y_sp`, nullable `target_shipout_index`/`target_y_sp`, `width_sp`, `base_height_sp`, `report_decoration_height_sp`, `effective_height_sp`, `report_depth`, `requires_marker` and `semantic_digest`. `margin_contract.py` loads the schemas and enforces globally unique note/obstacle IDs, unique page indexes, total page-reference consistency and one occurrence of each note ID in the appropriate page lists.

Use schema conditionals plus the semantic validator: `collecting` has `read_digest: null` and `error_code: null`; `changed` and `stable` require both SHA digests and no error; `failed` requires a closed enumerated `error_code`. The semantic validator additionally requires different digests for `changed`, equal digests for `stable`, monotonically valid pass numbers and `max_passes == 6`.

The pass envelope above is private and volatile because it contains `run_nonce`, `state`, `pass_number`, `read_digest`, `computed_digest` and `error_code`. Define a separate final stable-layout schema containing exactly `schema_version`, `variant`, `geometry_digest`, `semantic_digest`, `max_passes`, `notes` and `pages`. It reuses the exact note/page/obstacle definitions but contains no nonce, pass state, path or timestamp. `margin_contract.py` materializes it only from a validated `stable` envelope with equal digests; these canonical bytes are the `MANUEL_1SPE_<variant>.margin-layout.json` dependency compared across builds.

Also define `canonical_capture_projection(layout)` in `margin_contract.py`. It emits only `schema_version`, `variant`, `geometry_digest`, `semantic_digest` and notes sorted by `global_order`/ID with their capture-time fields (`id`, `role`, order, origin, width/base/decorated heights and semantic digest), excluding run nonce, pass state, target placement and backend IDs. The current private capture inventory and final stable layout must project to identical bytes. The ledger's `capture_inventory_digest` is the SHA-256 of these bytes, never a digest of the volatile envelope. Tests vary only nonce/pass metadata and require identical projection digest, stable layout and ledger.

The ledger schema is the canonical, PDF-derived payload and therefore contains no run nonce or other volatile envelope field. It removes pass state and requires exactly `schema_version`, `variant`, `pdf_sha256`, `capture_inventory_digest`, `stable_layout_digest`, `rendered_stream_digest` and `notes`. Each ledger note requires `note_id`, `role`, `global_order`, origin/target shipout and folio, `bbox_sp` as four integers, `semantic_digest`, `rendered_stream_digest`, positive `form_xref`, `anchor_count`, `note_count`, `report_depth` and `requires_marker`. `margin_contract.py` requires unique note IDs/xrefs, `note_count == 1`, and `anchor_count == 1` exactly when `requires_marker` is true. The same PDF and stable layout must serialize to byte-identical ledger bytes in distinct private runs.

- [ ] **Step 4: Run the schema tests and verify GREEN**

Run the command from Step 2. Expected: PASS.

- [ ] **Step 5: Commit the closed proof contracts**

```bash
git add Mathematiques/manuel-maths/schemas/margin-*.schema.json \
  Mathematiques/manuel-maths/tests/fixtures/margin-*.valid.json \
  Mathematiques/manuel-maths/scripts/margin_contract.py \
  Mathematiques/manuel-maths/tests/test_meta_schemas.py
git commit -m "[TESTS] fige les contrats du compositeur de marge"
```

### Task 2: Implement the pure top-down Lua solver

**Files:**
- Create: `Mathematiques/manuel-maths/gabarits/nexus-margin-layout.lua`
- Create: `Mathematiques/manuel-maths/gabarits/nexus-margin-json.lua`
- Create: `Mathematiques/manuel-maths/scripts/solve_margin_layout.lua`
- Create: `Mathematiques/manuel-maths/tests/test_margin_layout.py`

- [ ] **Step 1: Write a failing `texlua` test for three identical anchors**

The test writes canonical input JSON with three 30 pt notes at the same anchor, invokes:

```bash
texlua Mathematiques/manuel-maths/scripts/solve_margin_layout.lua \
  --solve INPUT.json --output OUTPUT.json
```

Later convergence tests add the optional `--previous PREVIOUS.json`; omitting it passes `nil` to the same solver signature.

The current input uses the exact Task 1 envelope: one page contains the three IDs in `native_note_ids`, and the three records live in top-level `notes`; the first call passes `nil` as previous layout. Assert the returned `pages[0].placed_note_ids`, preserved `global_order`, and `target_y_sp` equal anchor, anchor + height + 6 pt, and anchor + 2 × (height + 6 pt). Also retain deep copies and assert the in-process `solve(current, previous_or_nil)` call does not mutate either input table.

- [ ] **Step 2: Verify RED**

Run:

```bash
pytest -q Mathematiques/manuel-maths/tests/test_margin_layout.py \
  -k identical_anchors
```

Expected: FAIL because the Lua module is absent.

- [ ] **Step 3: Implement the minimal pure solver API**

Export a Lua table whose sole public solver signature is `solve(current_layout, previous_layout_or_nil) -> next_layout`, using the exact Task 1 envelope for each non-nil argument. Never sort or modify caller-owned tables: copy records and page ID arrays before placement.

```lua
local M = {}
local GAP_SP = 6 * 65536

function M.place_page(page, notes_by_id)
  local cursor = page.safe_rect.top_sp
  local placed = {}
  for _, note_id in ipairs(copy_array(page.carry_in_note_ids)) do
    local note = copy_record(notes_by_id[note_id])
    note.target_y_sp = cursor
    cursor = cursor + note.effective_height_sp + GAP_SP
    placed[#placed + 1] = note
  end
  local native = copy_records(page.native_note_ids, notes_by_id)
  table.sort(native, function(a, b)
    if a.origin_y_sp == b.origin_y_sp then
      return a.global_order < b.global_order
    end
    return a.origin_y_sp < b.origin_y_sp
  end)
  for _, note in ipairs(native) do
    note.target_y_sp = math.max(note.origin_y_sp, cursor)
    cursor = note.target_y_sp + note.effective_height_sp + GAP_SP
    placed[#placed + 1] = note
  end
  return placed
end

return M
```

`nexus-margin-json.lua` must be self-contained: its strict decoder preserves a `JSON_NULL` sentinel, tags array and object containers distinctly (including empty/nested containers), rejects duplicate keys and rejects non-whitespace bytes after the first complete JSON value. It rejects non-integer numeric fields and provides a canonical UTF-8 encoder with recursively sorted object keys. Add direct round-trip tests for `null`, `{}`, `[]`, nested empty containers, duplicate keys and trailing data. `scripts/solve_margin_layout.lua` is the only CLI: it parses required `--solve/--output` plus optional `--previous`, loads the two modules by repository-relative path, and writes returned bytes. The pure module ends with `return M` and contains no CLI or filesystem persistence.

- [ ] **Step 4: Verify GREEN and add order adversaries**

Run the Step 2 command. Add an automated adversarial fixture whose input array order disagrees with `global_order`; assert deterministic sorting without ever editing production code during the test.

- [ ] **Step 5: Commit the minimal solver**

```bash
git add Mathematiques/manuel-maths/gabarits/nexus-margin-layout.lua \
  Mathematiques/manuel-maths/gabarits/nexus-margin-json.lua \
  Mathematiques/manuel-maths/scripts/solve_margin_layout.lua \
  Mathematiques/manuel-maths/tests/test_margin_layout.py
git commit -m "[LATEX] ajoute le solveur déterministe de marge"
```

### Task 3: Add obstacles, minimal-suffix reports and decorated height

**Files:**
- Modify: `Mathematiques/manuel-maths/gabarits/nexus-margin-layout.lua`
- Modify: `Mathematiques/manuel-maths/tests/test_margin_layout.py`

- [ ] **Step 1: Write four failing solver tests**

Cover:

1. one of four notes is the shortest suffix required to report;
2. carry-in notes start at `safe_rect.top_sp` and precede native notes;
3. a middle obstacle moves the candidate below `obstacle.bottom_sp + GAP_SP`;
4. a report cartouche raises `effective_height_sp` enough to trigger a second-page cascade.

```python
assert page1["placed_note_ids"] == ["n1", "n2", "n3"]
assert page1["reported_note_ids"] == ["n4"]
assert page2["carry_in_note_ids"] == ["n4"]
assert notes_by_id["n4"]["target_y_sp"] == page2["safe_rect"]["top_sp"]
```

- [ ] **Step 2: Verify all four tests are RED for the intended reasons**

Run:

```bash
pytest -q Mathematiques/manuel-maths/tests/test_margin_layout.py \
  -k 'suffix or carry or obstacle or cartouche'
```

Expected: four assertion failures, not parser errors.

- [ ] **Step 3: Implement exact obstacle/report rules**

Add focused functions:

```lua
function M.skip_obstacles(y_sp, height_sp, obstacles)
  local candidate = y_sp
  local changed = true
  while changed do
    changed = false
    for _, obstacle in ipairs(obstacles) do
      local bottom = candidate + height_sp
      if candidate < obstacle.bottom_sp and bottom > obstacle.top_sp then
        candidate = obstacle.bottom_sp + GAP_SP
        changed = true
      end
    end
  end
  return candidate
end

function M.longest_fitting_prefix(notes, safe_bottom_sp)
  local keep = 0
  for index, note in ipairs(notes) do
    if note.target_y_sp + note.effective_height_sp <= safe_bottom_sp then
      keep = index
    else
      break
    end
  end
  return keep
end
```

Transfer `notes[keep + 1:]` without reversal and increment `report_depth`. Recompute, never accumulate, `effective_height_sp = base_height_sp + report_decoration_height_sp` when `report_depth > 0`; otherwise use `base_height_sp`. Add a cascade assertion proving that the decoration is added once at depth 1 and is not added again at depths 2 or 3. Task 6 must measure the same decoration as a TeX box and record that measurement in capture state so solver and rendered Form agree.

- [ ] **Step 4: Verify GREEN plus three-page cascade**

Run the complete `test_margin_layout.py`. Expected: PASS.

- [ ] **Step 5: Commit the complete placement rules**

```bash
git add Mathematiques/manuel-maths/gabarits/nexus-margin-layout.lua \
  Mathematiques/manuel-maths/tests/test_margin_layout.py
git commit -m "[LATEX] résout obstacles et reports de marge"
```

### Task 4: Implement the six-pass canonical convergence protocol

**Files:**
- Modify: `Mathematiques/manuel-maths/gabarits/nexus-margin-layout.lua`
- Modify: `Mathematiques/manuel-maths/tests/test_margin_layout.py`

- [ ] **Step 1: Write failing transition and contamination tests**

Assert:

- no previous file → `collecting`;
- different canonical placement → `changed`;
- identical read/computed digest → `stable`;
- a sixth non-stable pass → `failed` with `margin-layout-oscillation`;
- mismatched `run_nonce` → `failed` with `foreign-margin-layout`;
- changing only the envelope nonce does not change the canonical placement digest.

- [ ] **Step 2: Verify RED**

```bash
pytest -q Mathematiques/manuel-maths/tests/test_margin_layout.py -k convergence
```

Expected: FAIL because no state protocol exists.

- [ ] **Step 3: Implement canonical identity separately from the envelope**

Use named constants and an explicit digest payload:

```lua
local MAX_PASSES = 6

function M.canonical_identity(layout)
  return {
    schema_version = layout.schema_version,
    variant = layout.variant,
    geometry_digest = layout.geometry_digest,
    semantic_digest = layout.semantic_digest,
    max_passes = MAX_PASSES,
    notes = layout.notes,
    pages = layout.pages,
  }
end
```

Serialize UTF-8 with sorted keys and scaled-point integers. Never include time, temporary paths, table iteration order or nonce in the canonical digest. Keep the Lua API unique: `solve(current, previous_or_nil) -> next_layout`; Lua never emits a second stable payload. Only Python `margin_contract.materialize_stable_layout(validated_stable_envelope)` may strip volatile fields and serialize the final nonce-free evidence. The Lua module only returns canonical envelope bytes and digests; it does not persist state. Task 10 delegates schema/semantic validation, stable projection, unique sibling temporary creation, file `fsync`, `os.replace` and directory `fsync` to the existing Python atomic primitives in `assemble_manuel.py`.

- [ ] **Step 4: Verify GREEN and deterministic byte identity**

In one pytest case, invoke the CLI twice against the same explicit input and two explicit output paths in the same `tmp_path`, then compare `read_bytes()`. Expected: PASS and byte identity. Add a regression proving that `solve()` leaves its input deeply unchanged and cannot produce a false `stable` through aliasing.

- [ ] **Step 5: Commit the convergence protocol**

```bash
git add Mathematiques/manuel-maths/gabarits/nexus-margin-layout.lua \
  Mathematiques/manuel-maths/tests/test_margin_layout.py
git commit -m "[LATEX] borne la convergence des placements marginaux"
```

---

## Chunk 2: TeX capture, PDF evidence and mandatory postflight

### Task 5: Capture annotations once across normal and breakable contexts

**Files:**
- Create: `Mathematiques/manuel-maths/gabarits/nexus-margin-rail.tex`
- Create: `Mathematiques/manuel-maths/gabarits/nexus-margin-shipout.lua`
- Create: `Mathematiques/manuel-maths/tests/test_margin_compositor_pdf.py`
- Modify: `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls`

- [ ] **Step 1: Write a failing real LuaLaTeX capture-inventory fixture**

Compile a two-page document using the real class with three `\margeAppui` calls at one anchor. Require a capture inventory containing exactly three distinct IDs, three semantic payloads and three shipout-resolved anchors. The already observed legacy collision is documented in the approved design and review artefacts; do not retain an assertion that the corrected class must reproduce it.

- [ ] **Step 2: Verify RED on the real engine**

```bash
pytest -q Mathematiques/manuel-maths/tests/test_margin_compositor_pdf.py \
  -k identical_anchor
```

Expected: FAIL because the exact capture inventory is absent. The fixture must fail if zero notes are captured.

- [ ] **Step 3: Implement one-time capture and the shared adapter**

`nexus-margin-rail.tex` exposes `\nxMarginRailNote{role}{payload}`. Before capture, it increments one global counter that is never reset by chapter and derives the ASCII control ID `nxm:<variant>:<role>:%08d`; the same ID is used for capture, placement and anchor. Public macros never supply the control ID themselves.

Its core is:

```tex
\NewDocumentCommand\nxMarginRailNote{m m}{%
  \stepcounter{nxMarginGlobalOrder}%
  \edef\nxMarginCurrentId{\nxMarginStableId{#1}{\arabic{nxMarginGlobalOrder}}}%
  \setbox\nxMarginCaptureBox=\vbox{%
    \hsize=\marginparwidth #2}%
  \directlua{nexus_margin.capture_box(
    "\luaescapestring{\nxMarginCurrentId}",
    "\luaescapestring{#1}",
    \number\value{nxMarginGlobalOrder},
    \number\nxMarginCaptureBox)}%
  \nxMarginDeferredAnchor{\nxMarginCurrentId}%
}
```

The Lua side immediately calls `node.copy_list(tex.box[number].list)` and computes `semantic_digest` from a normalized, recursively walked copy of the rendered node-list (glyph/font/character, glue, kern, rule and controlled whatsit semantics; exclude volatile backend object numbers). It stores dimensions without reevaluating the payload. In horizontal mode, `\nxMarginDeferredAnchor` inserts a zero-dimension `\vadjust` carrying a `savepos`/user whatsit; in vertical mode it inserts that zero-dimension whatsit directly. Anchor coordinates and absolute shipout index are read only in the shipout callback. Route `\margeAppui`, `\commentaireMarge`, `\vocab`, exercise chrono and professor-only IDs through this command after variant filtering. Remove their direct `\marginnote` calls, but do not edit chapter sources.

At the end of each TeX pass, `nexus-margin-shipout.lua` closes the current capture/page envelope, calls the pure `nexus-margin-layout.solve(current, previous)` in memory, canonically encodes the returned envelope, and writes only the run-private candidate `margin-layout.next.json`. It never replaces `previous`. The pytest helper drives private passes itself before Task 10 exists: after each LuaLaTeX process exits, it validates `next` with `margin_contract.py`, atomically promotes it to `previous`, and repeats until `stable` or pass 6. On `stable`, `margin_contract.py` also materializes and validates the separate nonce-free `margin-stable-layout.json` candidate used by PDF/ledger checks. This helper mirrors the future assembler state machine and fails on a missing/foreign/malformed state; it never promotes a PDF.

`\nxMarginDeferredAnchor` must receive an immediately expanded literal copy of `\nxMarginCurrentId` (for example through an expl3 value argument or an `\edef`-built whatsit), never a token that will be expanded at shipout after its group has ended. The fixture compares the literal ID stored in every capture record with the ID recovered from the corresponding anchor whatsit at shipout.

- [ ] **Step 4: Verify GREEN capture, stable IDs and no direct public margin path**

Run the Step 2 test and source contracts asserting those five components call `\nxMarginRailNote` and no longer call `\marginnote` directly. Assert the same ordered three IDs on every private pass and exactly one capture/anchor record per ID. Do not yet claim zero PDF collision: Form emission is introduced in Task 8. Expected: PASS.

- [ ] **Step 5: Commit capture and adapters**

```bash
git add Mathematiques/manuel-maths/gabarits/nexus-margin-rail.tex \
  Mathematiques/manuel-maths/gabarits/nexus-margin-shipout.lua \
  Mathematiques/manuel-maths/gabarits/nexus-manuel.cls \
  Mathematiques/manuel-maths/tests/test_margin_compositor_pdf.py
git commit -m "[LATEX] capture les annotations dans une voie unique"
```

### Task 6: Prove breakable boxes, variants, parity and safe obstacles

**Files:**
- Modify: `Mathematiques/manuel-maths/gabarits/nexus-margin-rail.tex`
- Modify: `Mathematiques/manuel-maths/gabarits/nexus-margin-shipout.lua`
- Modify: `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls`
- Modify: `Mathematiques/manuel-maths/tests/test_margin_compositor_pdf.py`

- [ ] **Step 1: Add five failing real fixtures**

1. a breakable `fichemethode` spanning two pages with a local macro, math, color and link commands in captured notes;
2. an inserted blank page plus reset logical folio, proving side selection follows absolute shipout index;
3. a middle `\nxMarginReserveRect` obstacle;
4. an oversized unbreakable horizontal element, expecting a hard failure;
5. student/professor exercise metadata, expecting chrono in both and internal ID only in professor.

Also increment a TeX counter inside the note and assert its final value is exactly 1, proving no double evaluation. Exercise `\nxMarginRailNote` in vertical mode, horizontal mode and a broken `tcolorbox`; require the same ordered IDs on every private pass.

- [ ] **Step 2: Verify RED fixture by fixture**

```bash
pytest -q Mathematiques/manuel-maths/tests/test_margin_compositor_pdf.py \
  -k 'breakable or parity or obstacle or oversized or variant'
```

Expected: each case fails on its intended assertion.

- [ ] **Step 3: Implement geometry, reservations and variant payloads**

At each shipout, record absolute index, folio, page size, effective outer rail rectangle and declared obstacles in scaled points. `\nxMarginReserveRect` must register top/bottom/left/right values without pixel constants. Capture exercise payload only after `\ifnxVersionProfesseur` filtering. Fail with `NEXUS-MARGIN-ERROR:<code>:<id>` for width, height or placement violations.

Measure the report cartouche as its own TeX box and record `report_decoration_height_sp` from that exact box before solving. Register enough controlled link-whatsit metadata for Task 8 to reconstruct links, but defer PDF link survival assertions until Form emission exists.

- [ ] **Step 4: Verify GREEN and unchanged main-flow pagination**

Run all real capture/layout fixtures. Compare page count and the coordinates of named body-text sentinels with marker metadata enabled and disabled; do not compare the whole extracted bbox because future visible overlay markers legitimately add glyphs. Expected: identical body flow and PASS.

- [ ] **Step 5: Commit robust contexts and geometry**

```bash
git add Mathematiques/manuel-maths/gabarits/nexus-margin-*.tex \
  Mathematiques/manuel-maths/gabarits/nexus-margin-*.lua \
  Mathematiques/manuel-maths/gabarits/nexus-manuel.cls \
  Mathematiques/manuel-maths/tests/test_margin_compositor_pdf.py
git commit -m "[LATEX] sécurise reports recto verso et encadrés"
```

### Task 7: Install the frozen PDF inspection stack before ledger tests

**Files:**
- Modify: `Mathematiques/manuel-maths/requirements.txt`
- Modify: `requirements-ci-audit.txt`
- Modify: `.github/workflows/ci-mathematiques.yml`
- Modify: `.github/workflows/ci-audit-collection.yml`
- Modify: `tests/test_ci_audit_collection.py`

- [ ] **Step 1: Write failing dependency-availability tests**

Require `pikepdf==8.7.1` rather than treating the locally installed distro package as a repository dependency. Require its complete pinned transitive closure in the `--no-deps` Phase 0 requirements, `qpdf` in both apt lists, and `ubuntu-24.04` rather than the drifting `ubuntu-latest` runner for the mathematics workflow. Parse both workflows as YAML and assert each ledger test job can import pikepdf and execute `qpdf --version` before running pytest.

- [ ] **Step 2: Verify RED**

```bash
pytest -q tests/test_ci_audit_collection.py -k 'pikepdf or qpdf or math_runner'
```

Expected: FAIL because neither workflow currently installs the complete inspection stack and the mathematics runner is not frozen.

- [ ] **Step 3: Pin the direct and transitive dependencies**

Add `pikepdf==8.7.1` to the manual requirements. Regenerate and commit its exact Python dependency closure (`Deprecated`, `wrapt`, `lxml`, `packaging`, `Pillow` as applicable) in `requirements-ci-audit.txt`, preserving `pip install --no-deps` plus `pip check`. Add `qpdf` to both system package lists and make the mathematics workflow install the pinned pikepdf requirement before ledger tests. The runtime tests must fail closed if import or executable discovery fails.

- [ ] **Step 4: Verify GREEN locally and in workflow contracts**

```bash
pytest -q tests/test_ci_audit_collection.py -k 'requirements or pikepdf or qpdf or math_runner'
python3 - <<'PY'
import pikepdf
assert pikepdf.__version__ == "8.7.1"
PY
qpdf --version
```

Expected: PASS; local pikepdf is 8.7.1 and qpdf is available. Version evidence is added to observed receipts separately in Task 12.

- [ ] **Step 5: Commit the available inspection stack**

```bash
git add Mathematiques/manuel-maths/requirements.txt requirements-ci-audit.txt \
  .github/workflows/ci-mathematiques.yml .github/workflows/ci-audit-collection.yml \
  tests/test_ci_audit_collection.py
git commit -m "[CI] installe les outils figés de preuve PDF"
```

### Task 8: Emit Form XObjects and reconstruct the PDF-derived ledger

**Files:**
- Modify: `Mathematiques/manuel-maths/gabarits/nexus-margin-rail.tex`
- Modify: `Mathematiques/manuel-maths/gabarits/nexus-margin-shipout.lua`
- Create: `Mathematiques/manuel-maths/scripts/margin_ledger.py`
- Create: `Mathematiques/manuel-maths/tests/test_margin_ledger.py`

- [ ] **Step 1: Write failing PDF object and bijection tests**

Build one fixture with three identical-anchor notes and a second fixture with one unmarked note, one strongly displaced note and one reported note. Require exactly three captured IDs and exactly three rendered `NXMarginNote` instances before asserting zero collision, so disappearance can never pass. Assert one dedicated Form XObject per note, `NXMarginAnchor` only for strongly displaced/reported notes, valid `/BBox`, and no control IDs in `pdftotext` output. Add URI-multiline and internal-GoTo notes; require their actions and per-line rectangles to survive without duplicate annotations.

- [ ] **Step 2: Verify RED**

```bash
pytest -q Mathematiques/manuel-maths/tests/test_margin_ledger.py \
  -k 'xobject or marked_content or bijection'
```

Expected: FAIL because no ledger parser or marked contents exist.

- [ ] **Step 3: Implement deterministic Form XObject emission, link remapping and the parser**

On every pass that starts with a valid `previous` layout, rebuild the decorated TeX box from the already captured node-list without reevaluating source tokens and render its overlay according to that prior placement. The pass does not yet know whether it will be retained. At end of pass it recalculates `next`; the Python driver preserves the just-produced PDF only if `next.state == stable` and `read_digest == computed_digest`, otherwise it discards that PDF and advances the state. Traverse each box to collect every link start/end pair, its URI or GoTo action/destination, and one rectangle per spanned line; remove or neutralize the original link whatsits because page annotations are not legal inside a Form XObject. In ascending `global_order`, create each Form with LuaTeX `\saveboxresource`, record `\lastsavedboxresourceindex`, and place it with `\useboxresource`. Wrap the page-level `Do` invocation in marked content `NXMarginNote`; wrap the separate zero-size anchor marker in `NXMarginAnchor`. After applying the target transform, create page annotations for each saved link rectangle and prove none remain duplicated inside the Form.

Use pikepdf for structured parsing and `qpdf --check` as an independent CLI cross-check. Use exactly the ledger contract already validated by `margin_contract.py`; do not define a second partial model. The Python representation includes:

```python
@dataclass(frozen=True)
class MarginLedgerEntry:
    note_id: str
    role: str
    global_order: int
    origin_shipout_index: int
    origin_folio: str
    target_shipout_index: int
    target_folio: str
    bbox_sp: tuple[int, int, int, int]
    semantic_digest: str
    rendered_stream_digest: str
    form_xref: int
    anchor_count: int
    note_count: int
    report_depth: int
    requires_marker: bool
```

Traverse page content streams, resolve each Form XObject `/BBox`, decode the stream for `rendered_stream_digest`, and write the exact sorted canonical ledger root, including its aggregate `rendered_stream_digest`. Compute `capture_inventory_digest` only through `margin_contract.canonical_capture_projection`, and require the private-pass projection to equal the stable-layout projection. Reject unknown tags, duplicate IDs, a note without its required anchor, an anchor without a note, or any control ID visible through text extraction. Run the same fixture in two distinct private run directories and require identical capture-projection digest, stable-layout bytes and ledger bytes despite different layout run nonces.

- [ ] **Step 4: Verify GREEN and adversarial mutations**

Create independent mutated PDF copies under `tmp_path`: alter one `/BBox`, delete one anchor, duplicate one note tag, duplicate a link annotation and inject an internal 1SPE ID into student text. Confirm each copy makes the checker fail while the original fixture remains untouched.

- [ ] **Step 5: Commit PDF identity evidence**

```bash
git add Mathematiques/manuel-maths/gabarits/nexus-margin-* \
  Mathematiques/manuel-maths/scripts/margin_ledger.py \
  Mathematiques/manuel-maths/tests/test_margin_ledger.py
git commit -m "[PDF] prouve les objets marginaux rendus"
```

### Task 9: Make zero-collision margin proof a mandatory full-manual PDF gate

**Files:**
- Modify: `Mathematiques/manuel-maths/scripts/margin_ledger.py`
- Modify: `Mathematiques/manuel-maths/scripts/pdf_integrity.py`
- Modify: `Mathematiques/manuel-maths/tests/test_margin_ledger.py`
- Modify: `Mathematiques/manuel-maths/tests/test_pdf_integrity.py`

- [ ] **Step 1: Write failing geometry and fail-closed tests**

The bbox layer must reject intersecting notes, less than 6 pt vertical spacing, a note outside the effective outer rail, overlap with a reserved rectangle, a missing ledger and an unavailable PDF parser. Add known-coordinate recto and verso fixtures plus PDFs with shifted CropBox, `/UserUnit`, and nonzero `/Rotate`.

- [ ] **Step 2: Verify RED**

```bash
pytest -q \
  Mathematiques/manuel-maths/tests/test_margin_ledger.py \
  Mathematiques/manuel-maths/tests/test_pdf_integrity.py \
  -k margin
```

Expected: FAIL because `verify_pdf` has no explicit full-manual margin-proof mode.

- [ ] **Step 3: Implement the composed gate**

Freeze coordinates before implementing the checker. Canonical `bbox_sp = [left, top, right, bottom]` uses the CropBox upper-left as origin, x increasing right and y increasing down. Convert TeX sp to physical PDF bp exactly as `bp = sp × 72 / (72.27 × 65536)`, then divide by `/UserUnit` to obtain PDF user-space values. For an unrotated page:

```text
pdf_left   = CropBox.llx + sp_to_bp(left) / UserUnit
pdf_bottom = CropBox.ury - sp_to_bp(bottom) / UserUnit
```

Translate the Form's actual `/BBox [fx0 fy0 fx1 fy1]` by `(pdf_left - fx0, pdf_bottom - fy0)` before `Do`; the postflight composes this CTM and reconstructs the canonical top-left bbox. Support nonzero CropBox origins and positive `/UserUnit`; fail closed on any `/Rotate != 0` in this first version. Poppler coordinates must be normalized through the same CropBox before comparison. All four coordinates must agree within one scaled point.

`verify_margin_layout(pdf, capture_inventory, stable_layout, ledger)` must:

1. validate all three contracts: private pass envelope, nonce-free stable layout and PDF-derived ledger;
2. require byte-identical `canonical_capture_projection` from the validated private envelope and stable layout, then equal ID sets and role/variant cardinalities in the ledger;
3. compare Form `/BBox` and ledger coordinates in one documented TeX-to-PDF coordinate system;
4. allow at most 1 scaled point of conversion/rounding tolerance;
5. reject overlap, rail escape, obstacle intersection and spacing below 6 pt;
6. check student/professor payload policy;
7. require `qpdf --check` and return a structured result consumed by `verify_pdf`.

Extend the historical gate compatibly:

```python
verify_pdf(
    pdf,
    log,
    *,
    require_margin_proof: bool = False,
    margin_evidence: MarginEvidence | None = None,
    runner=None,
    environment=None,
)
```

Existing chapter/specimen callers keep the default. `require_margin_proof=True` fails closed on absent or invalid evidence and is mandatory only for `assemble_manuel.py` from Task 10 onward. Import pikepdf lazily so a historical lightweight caller does not fail unless it requests the proof. Propagate the injected runner, sanitized environment and the existing 20-second timeout to qpdf/Poppler calls.

- [ ] **Step 4: Verify GREEN and mutation sensitivity**

Run the Step 2 command. Expected: PASS. Re-run one overlap mutation and confirm one deterministic failure reason.

- [ ] **Step 5: Commit the mandatory margin gate**

```bash
git add Mathematiques/manuel-maths/scripts/margin_ledger.py \
  Mathematiques/manuel-maths/scripts/pdf_integrity.py \
  Mathematiques/manuel-maths/tests/test_margin_ledger.py \
  Mathematiques/manuel-maths/tests/test_pdf_integrity.py
git commit -m "[PDF] bloque toute collision de notes marginales"
```

---

## Chunk 3: Bounded assembler, observed evidence and full-manual proof

### Task 10: Replace the fixed three passes with a bounded stable-pass loop

**Files:**
- Modify: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
- Modify: `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py`
- Modify: `scripts/build_manifest.py`
- Modify: `tests/test_build_manifest.py`

- [ ] **Step 1: Extend the fake runner and write failing orchestration tests**

Teach `FakeProductionRunner` to emit pass states. Test normal `collecting → changed → stable` in three calls, stability on pass 4, oscillation through pass 6, foreign nonce, missing status and malformed status. Assert full-manual `verify_pdf(require_margin_proof=True)` is called only after stable state. Add receipt/preflight validation tests for the new closed structured margin check and `receipt_schema_version: 2` before changing production code.

- [ ] **Step 2: Verify RED**

```bash
pytest -q \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  tests/test_build_manifest.py \
  -k 'margin_state or stable_pass or oscillation or margin_layout or receipt_schema_version'
```

Expected: FAIL because the assembler still executes exactly three unconditional passes.

- [ ] **Step 3: Implement the bounded loop**

Add a versioned constant and closed reader:

```python
MARGIN_MAX_PASSES = 6

for pass_number in range(1, MARGIN_MAX_PASSES + 1):
    proc = run_lualatex(...)
    status = load_margin_status(run_status_path, run_id, variant)
    if status["state"] == "stable":
        stable_pass = pass_number
        break
else:
    raise AssemblyError("placements marginaux non stabilisés après 6 passes")
```

Reject `failed`, an unexpected transition, mismatched run/variant/schema, missing layout or a PDF whose pass did not read and recompute the same digest. On the accepted stable pass, call `margin_contract.materialize_stable_layout(status)` and validate its nonce-free bytes before PDF postflight or publication. Do not add free-form scalar checks to the currently closed preflight map. Extend the exact producer/recorder contract with:

```json
"margin_layout": {
  "passed": true,
  "max_passes": 6,
  "stable_pass": 3,
  "read_digest": "sha256:...",
  "computed_digest": "sha256:..."
}
```

`build_manifest.py` requires this object for every `receipt_schema_version: 2` complete-manual receipt, rejects extra/missing keys, enforces `1 <= stable_pass <= max_passes == 6` and equal digests. Preserve read compatibility for historical receipts without that field only when their compiled master also lacks the literal compositor schema marker `NEXUS-MARGIN-COMPOSITOR-SCHEMA:1`; if the marker is present, a missing/downgraded receipt version or `margin_layout` is a hard failure. The assembler emits the marker and activates `verify_pdf(..., require_margin_proof=True, margin_evidence=...)` before producing a version-2 check.

- [ ] **Step 4: Verify GREEN and preserve private-run cleanup**

Run the Step 2 command plus all private-run cleanup tests. Expected: PASS and no `.run` directory after success or failure.

- [ ] **Step 5: Commit stable orchestration**

```bash
git add Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  scripts/build_manifest.py tests/test_build_manifest.py
git commit -m "[PDF] attend la stabilité des marges avant publication"
```

### Task 11: Promote and record stable layout plus PDF ledger atomically

**Files:**
- Modify: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
- Modify: `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py`
- Modify: `scripts/build_manifest.py`
- Modify: `tests/test_build_manifest.py`

- [ ] **Step 1: Write failing evidence-closure tests**

Require canonical outputs:

```text
MANUEL_1SPE_<variant>.margin-layout.json
MANUEL_1SPE_<variant>.margin-ledger.json
```

Require both canonical paths in `generated_dependencies`, both digests in the observed manifest, and their private source paths in FLS `OUTPUT`. Add a closed receipt table mapping each private FLS source to its canonical promoted destination and digest; cover the private master `INPUT` similarly. Require preservation of every previous canonical artefact and `audit/BUILD_MANIFEST.json` if any promotion or recorder validation fails.

- [ ] **Step 2: Verify RED**

```bash
pytest -q \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  tests/test_build_manifest.py \
  -k 'margin_dependency or margin_ledger or generated_dependencies'
```

Expected: FAIL because receipts still declare an empty dependency list.

- [ ] **Step 3: Extend atomic evidence publication**

Open the run-private JSON outputs once through TeX `\openout` so `-recorder` records them, then let Lua/Python replace their private candidate contents. Compile from a private candidate master as well, leaving every canonical file untouched through compilation and gates. Fingerprint layout and ledger alongside master/log/FLS/PDF. Keep the `.run` directory alive through the recorder.

After schema, ledger, bbox and variant gates pass, reuse the variant lock already held by `_main_locked`—never reacquire it—and acquire a repository-wide publication lock at the distinct Git-private path `nexus-observed-publication.lock`, derived with `git rev-parse --git-path`. It must not reuse the recorder's existing `nexus-build.lock`.

Make every `build_manifest.py` writer participate in the publication lock. A direct invocation opens and locks `nexus-observed-publication.lock` before taking `nexus-build.lock`. The assembler opens/locks it once, passes that descriptor to the recorder subprocess with `pass_fds`, and sets a dedicated inherited-FD variable in the otherwise sanitized child environment. The child accepts inheritance only after verifying the descriptor is open, refers to the same regular Git-private path/inode with `O_NOFOLLOW` protections, and still owns an exclusive `flock`; otherwise it fails rather than bypassing the lock. It then takes only `nexus-build.lock`. Lock order is therefore variant → publication → build-manifest for assembler calls and publication → build-manifest for direct calls.

Hold the publication lock across backup, promotion, recorder and rollback so no direct recorder or other variant can update `audit/BUILD_MANIFEST.json` in the rollback window. Add real subprocess tests for valid inherited-FD completion, forged/missing descriptor rejection, a direct recorder waiting behind the assembler, and concurrent variant builds serializing without deadlock.

Start one recoverable publication transaction. Copy the old canonical master, log, FLS, PDF, preflight, receipt, layout, ledger and `audit/BUILD_MANIFEST.json` to uniquely named private backups; `fsync` each backup and directory. Promote the complete candidate set, write report/receipt, call the recorder while the FLS sources and candidate master still exist, and delete backups only after recorder success. On any exception or nonzero recorder result, restore the whole previous set (including absence), `fsync` every affected directory, and then delete the private run. Tests inject failure at every promotion boundary and after manifest replacement, plus concurrent builds of both variants proving serialization without deadlock.

Populate:

```python
generated_dependencies = [
    f"{git_relative_prefix}/{tex_name}.margin-layout.json",
    f"{git_relative_prefix}/{tex_name}.margin-ledger.json",
]
```

Add a closed `fls_promotions` receipt list whose records contain `kind` (`INPUT`/`OUTPUT`), private FLS path, canonical path and SHA-256. `build_manifest.py` reads both sides while `.run` exists, requires byte/digest equality, proves the private source in the correct FLS set, then accepts only the mapped canonical layout/ledger as generated dependencies. Do not weaken `_read_proof_file`, FLS proof, digest comparison or Git snapshot checks.

- [ ] **Step 4: Verify GREEN and tamper resistance**

Run Step 2. Then alter one ledger byte between preflight and receipt creation, fail each sequential promotion, and force a recorder failure after manifest replacement. In every case assert the byte-identical previous canonical set is restored and no backup or `.run` directory remains.

- [ ] **Step 5: Commit observed margin dependencies**

```bash
git add Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  scripts/build_manifest.py tests/test_build_manifest.py
git commit -m "[AUDIT] enregistre les preuves de placement marginal"
```

### Task 12: Record the frozen inspection toolchain in observed evidence

**Files:**
- Modify: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
- Modify: `scripts/build_manifest.py`
- Modify: `audit/schemas/v1/build-manifest.schema.json`
- Modify: `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py`
- Modify: `tests/test_build_manifest.py`

- [ ] **Step 1: Write failing dependency and tool-version tests**

Require `tool_contract_version: 2`, `qpdf --version` and the pinned pikepdf version in new assembler receipts, preflights, observed builds and the closed build-manifest schema. Reject missing, extra or locally mismatched versions before recording a new build. Task 7 already proves installation; this task only closes observed evidence. Existing manifest entries remain valid under legacy tool contract 1 until rebuilt.

- [ ] **Step 2: Verify RED**

```bash
pytest -q Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  tests/test_build_manifest.py -k tool_versions
```

Expected: FAIL because `qpdf`/pikepdf are not yet admitted by the closed observed tool contract and JSON Schema.

- [ ] **Step 3: Record the already pinned inspection stack**

Version both exact tool contracts in producer, recorder and `audit/schemas/v1/build-manifest.schema.json`: absent/legacy contract 1 accepts exactly the historical four keys only for a master without the compositor schema marker; contract 2 is mandatory with receipt schema 2/the marker and requires exactly six keys. Invoke qpdf as `qpdf --version`. Pikepdf has no supported CLI version command, so collect it with `[sys.executable, "-c", "import pikepdf; print('pikepdf ' + pikepdf.__version__)"]`. Use the same sanitized environment and 20-second timeout as existing tools, normalize only the first non-empty line, and require receipt/local equality. Add mixed-manifest fixtures proving old four-tool entries and new six-tool entries validate together, while a marked new build cannot claim contract 1.

- [ ] **Step 4: Verify GREEN and schema closure**

Run the Step 2 tests, validate a real build fixture against the JSON Schema and run Ruff on modified Python. Expected: PASS.

- [ ] **Step 5: Commit frozen PDF inspection dependencies**

```bash
git add Mathematiques/manuel-maths/scripts/assemble_manuel.py scripts/build_manifest.py \
  audit/schemas/v1/build-manifest.schema.json \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  tests/test_build_manifest.py
git commit -m "[AUDIT] enregistre les versions des outils de marge"
```

### Task 13: Rebuild the student manual and prove pages 18–21

**Files:**
- Modify generated: `Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf`
- Regenerate runtime evidence: matching `.log`, `.fls`, `.preflight.json`, `.receipt.json`, `.margin-layout.json`, `.margin-ledger.json` (ignored; proved by the observed manifest, not force-added to Git)
- Create: `audit/visual-margin-review-2026-08-03/README.md`
- Create review images under: `audit/visual-margin-review-2026-08-03/eleve/`

- [ ] **Step 1: Run targeted tests before the real build**

```bash
pytest -q \
  Mathematiques/manuel-maths/tests/test_margin_layout.py \
  Mathematiques/manuel-maths/tests/test_margin_compositor_pdf.py \
  Mathematiques/manuel-maths/tests/test_margin_ledger.py \
  Mathematiques/manuel-maths/tests/test_pdf_integrity.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py
```

Expected: PASS.

- [ ] **Step 2: Build and record the student variant**

```bash
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  --variant eleve --record-observed
```

Expected: exit 0, stable margin pass ≤ 6, margin gate PASS, student separation PASS.

Copy the PDF, stable layout and ledger to an external `mktemp -d` snapshot, run the same `--record-observed` command a second time from the same source commit/environment, and compare the three final files byte for byte. The second receipt remains canonical and matches the second log/FLS; delete the temporary snapshot after PASS.

- [ ] **Step 3: Produce review artefacts without creating a baseline**

Rasterize pages 18–21 and all pages in the top decile of margin density. Record old/new PDF hashes, page counts, tool versions, page mapping and the automated ledger summary. Do not write under any baseline directory and do not modify any golden hash.

- [ ] **Step 4: Inspect the rendered pages at full resolution**

Confirm notes are legible, remain in the outer rail, preserve reading order, show correct report markers and do not obscure headers, folios or tabs. Record human-review status as `pending` until explicitly approved.

- [ ] **Step 5: Commit the student proof separately**

```bash
git add Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf \
  audit/visual-margin-review-2026-08-03
git commit -m "[PDF] reconstruit le manuel élève sans collisions marginales"
```

### Task 14: Rebuild professor, reattest both variants and run Phase 0

**Files:**
- Modify generated: professor PDF; regenerate ignored matching runtime evidence without force-adding it
- Modify generated: `audit/BUILD_MANIFEST.json`, collection inventory and Phase 0 reports
- Extend: `audit/visual-margin-review-2026-08-03/README.md`
- Create review images under: `audit/visual-margin-review-2026-08-03/professeur/`

- [ ] **Step 1: Build and record the professor variant**

```bash
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  --variant professeur --record-observed
```

Expected: exit 0, stable margin pass ≤ 6, internal IDs present only in professor payload, zero collision.

- [ ] **Step 2: Verify deterministic double builds**

Snapshot the professor PDF, stable layout and ledger in `mktemp -d`, run the same professor `--record-observed` build a second time before any commit, and compare all three byte for byte. The student pair was already compared in Task 13. Keep only the second matching professor receipt/log/FLS and remove the temporary snapshot. Expected: all comparisons identical.

- [ ] **Step 3: Run complete affected suites and quality tools**

```bash
python -m pytest -q --import-mode=importlib
python -m ruff check .
python -m mypy --cache-dir /tmp/nexus-margin-mypy
python3 scripts/inventory_collection.py --validate-model
python3 scripts/inventory_collection.py --fail-on-new
python3 scripts/inventory_collection.py --release-strict
```

Expected: pytest/Ruff/mypy/validate-model/fail-on-new PASS. Capture `release-strict` twice; require its documented exit code 7 and byte-identical sorted blocker output. It remains red only for explicit publication blockers and must no longer report marginal collisions.

- [ ] **Step 4: Reattest and validate observed evidence**

Because the private `.run` sources authenticated by FLS are intentionally deleted after each successful transaction, do not replay an old receipt after the build. Reattest by running new observed builds, whose internal recorder executes while those private sources still exist. Run this exact sequence from the repository root:

```bash
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  --variant eleve --record-observed
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  --variant professeur --record-observed
python3 scripts/inventory_collection.py
```

Hash both PDFs, both stable layouts, both ledgers, `audit/BUILD_MANIFEST.json`, `audit/INVENTAIRE_COLLECTION.json`, `audit/INVENTAIRE_COLLECTION.md`, `audit/AUDIT_CONSOLIDE.md`, `audit/ECARTS_ET_CONTRADICTIONS.yaml`, `audit/MATRICE_LIVRABLES.yaml` and `ETAT_COLLECTION.md`; repeat the exact three-command sequence and require byte-identical files/hashes. Each assembler internally calls `build_manifest.py --receipt` before deleting `.run`. Confirm both PDF hashes, page counts, layout/ledger digests and six tool versions appear in the observed manifest.

- [ ] **Step 5: Complete professor visual review artefacts without baseline mutation**

Add before/after pages, dense-page contact sheet and review checklist. Confirm with:

```bash
git diff --name-only "$starting_sha" -- \
  ':(glob)**/validations/**' ':(glob)audit/visual-baseline*'
git ls-files --others --exclude-standard -- \
  ':(glob)**/validations/**' ':(glob)audit/visual-baseline*'
```

Expected: no visual baseline path changed.

- [ ] **Step 6: Commit professor PDF, then audit evidence in separate commits**

```bash
git add Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf \
  audit/visual-margin-review-2026-08-03
git commit -m "[PDF] reconstruit le manuel professeur sans collisions marginales"

git add audit/BUILD_MANIFEST.json audit/INVENTAIRE_COLLECTION.json \
  audit/INVENTAIRE_COLLECTION.md audit/AUDIT_CONSOLIDE.md \
  audit/ECARTS_ET_CONTRADICTIONS.yaml audit/MATRICE_LIVRABLES.yaml \
  ETAT_COLLECTION.md
git commit -m "[AUDIT] réatteste les deux manuels après correction des marges"
```

- [ ] **Step 7: Stop for human review before any baseline decision**

Report PDF links, old/new hashes, pages changed, margin ledger summary, all green/red gates and the review directory. Do not update any baseline and do not claim publication acceptance.

---

## Final verification checklist

- [ ] `git diff --check` is clean.
- [ ] Worktree contains only intentional files.
- [ ] Every production behavior was introduced after a witnessed failing test.
- [ ] Both stable placements converge within six passes.
- [ ] Both PDF ledgers are bijective with their capture inventories.
- [ ] Bbox gate reports zero marginal intersection and ≥6 pt spacing.
- [ ] Student PDF has no correction, teacher payload or visible internal ID.
- [ ] Professor PDF preserves expected IDs and corrections.
- [ ] Links inside moved notes remain functional.
- [ ] Two builds produce byte-identical PDF/layout/ledger artefacts.
- [ ] No visual baseline file or digest changed.
- [ ] `release_acceptance=false`; general manual status remains NO-GO.
