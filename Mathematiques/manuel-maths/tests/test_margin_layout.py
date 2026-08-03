from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest


MANUAL_ROOT = Path(__file__).resolve().parents[1]
SOLVER = MANUAL_ROOT / "scripts" / "solve_margin_layout.lua"
JSON_CODEC = MANUAL_ROOT / "gabarits" / "nexus-margin-json.lua"
LAYOUT_FIXTURE = MANUAL_ROOT / "tests" / "fixtures" / "margin-layout.valid.json"
SP_PER_PT = 65536


def _load_margin_contract():
    module_path = MANUAL_ROOT / "scripts" / "margin_contract.py"
    spec = importlib.util.spec_from_file_location("margin_contract_for_layout_test", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _layout_with_identical_anchors() -> dict[str, object]:
    anchor_sp = 20 * SP_PER_PT
    height_sp = 30 * SP_PER_PT
    note_ids = ["note-a", "note-b", "note-c"]
    notes = [
        {
            "id": note_id,
            "role": "appui",
            "global_order": global_order,
            "origin_shipout_index": 1,
            "origin_folio": "1",
            "origin_y_sp": anchor_sp,
            "target_shipout_index": None,
            "target_y_sp": None,
            "width_sp": 12 * SP_PER_PT,
            "base_height_sp": height_sp,
            "report_decoration_height_sp": 0,
            "effective_height_sp": height_sp,
            "report_depth": 0,
            "requires_marker": False,
            "semantic_digest": f"sha256:{global_order:064x}",
        }
        for note_id, global_order in zip(note_ids, (1, 2, 3), strict=True)
    ]
    return {
        "schema_version": 1,
        "run_nonce": "0123456789abcdef0123456789abcdef",
        "variant": "eleve",
        "geometry_digest": f"sha256:{1:064x}",
        "semantic_digest": f"sha256:{2:064x}",
        "state": "collecting",
        "pass_number": 1,
        "max_passes": 6,
        "read_digest": None,
        "computed_digest": f"sha256:{3:064x}",
        "error_code": None,
        "notes": notes,
        "pages": [
            {
                "shipout_index": 1,
                "folio": "1",
                "page_width_sp": 100 * SP_PER_PT,
                "page_height_sp": 200 * SP_PER_PT,
                "rail_side": "right",
                "safe_rect": {
                    "left_sp": 80 * SP_PER_PT,
                    "top_sp": 10 * SP_PER_PT,
                    "right_sp": 95 * SP_PER_PT,
                    "bottom_sp": 190 * SP_PER_PT,
                },
                "native_note_ids": note_ids,
                "carry_in_note_ids": [],
                "placed_note_ids": [],
                "reported_note_ids": [],
                "obstacles": [],
            }
        ],
    }


def _layout_whose_stack_overflows_safe_rect() -> dict[str, object]:
    layout = _layout_with_identical_anchors()
    layout["notes"] = layout["notes"][:2]
    page = layout["pages"][0]
    page["native_note_ids"] = ["note-a", "note-b"]
    page["safe_rect"]["bottom_sp"] = 80 * SP_PER_PT
    return layout


def test_identical_anchors_are_placed_top_down(tmp_path: Path) -> None:
    source = tmp_path / "layout.json"
    output = tmp_path / "solved.json"
    source.write_text(
        json.dumps(_layout_with_identical_anchors(), ensure_ascii=False),
        encoding="utf-8",
    )

    subprocess.run(
        ["texlua", str(SOLVER), "--solve", str(source), "--output", str(output)],
        check=True,
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    solved = json.loads(output.read_text(encoding="utf-8"))
    _load_margin_contract().validate_margin_layout(solved)
    assert solved["pages"][0]["placed_note_ids"] == ["note-a", "note-b", "note-c"]
    assert solved["pages"][0]["native_note_ids"] == ["note-a", "note-b", "note-c"]
    assert [note["id"] for note in solved["notes"]] == ["note-a", "note-b", "note-c"]
    notes = {note["id"]: note for note in solved["notes"]}
    anchor_sp = 20 * SP_PER_PT
    step_sp = 36 * SP_PER_PT
    assert [notes[note_id]["target_y_sp"] for note_id in ("note-a", "note-b", "note-c")] == [
        anchor_sp,
        anchor_sp + step_sp,
        anchor_sp + 2 * step_sp,
    ]
    assert [notes[note_id]["global_order"] for note_id in ("note-a", "note-b", "note-c")] == [
        1,
        2,
        3,
    ]


def test_layout_solve_rejects_a_candidate_below_the_safe_rect(tmp_path: Path) -> None:
    source = tmp_path / "overflow.json"
    driver = tmp_path / "overflow-driver.lua"
    overflowing = _layout_whose_stack_overflows_safe_rect()
    _load_margin_contract().validate_margin_layout(overflowing)
    _write_json(source, overflowing)
    driver.write_text(
        """
local json = assert(loadfile(arg[1]))()
local layout = assert(loadfile(arg[2]))()
local file = assert(io.open(arg[3], "rb"))
local current = json.decode(file:read("*a"))
assert(file:close())
local ok, result = pcall(layout.solve, current, nil)
if ok then
  io.write(json.encode(result))
  os.exit(0)
end
io.stderr:write(tostring(result), "\\n")
os.exit(1)
""".strip(),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "texlua",
            str(driver),
            str(JSON_CODEC),
            str(MANUAL_ROOT / "gabarits" / "nexus-margin-layout.lua"),
            str(source),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "invalid margin layout at result.notes[note-b].target_y_sp" in result.stderr


@pytest.mark.parametrize("existing_output", [False, True])
def test_cli_rejects_an_overflowing_candidate_without_publishing_output(
    tmp_path: Path, existing_output: bool
) -> None:
    source = tmp_path / "overflow.json"
    output = tmp_path / "output.json"
    overflowing = _layout_whose_stack_overflows_safe_rect()
    _load_margin_contract().validate_margin_layout(overflowing)
    _write_json(source, overflowing)
    if existing_output:
        output.write_bytes(b"old-output")

    result = _run_solver(source, output, cwd=tmp_path)

    assert result.returncode != 0
    assert result.stderr.startswith("margin-layout-cli:")
    assert "result.notes[note-b].target_y_sp" in result.stderr
    if existing_output:
        assert output.read_bytes() == b"old-output"
    else:
        assert not output.exists()


def _run_codec(tmp_path: Path, payload: bytes) -> subprocess.CompletedProcess[bytes]:
    driver = tmp_path / "codec-driver.lua"
    driver.write_text(
        """
local json = assert(loadfile(arg[1]))()
local input = io.stdin:read("*a")
local ok, result = pcall(function()
  return json.encode(json.decode(input))
end)
if not ok then
  io.stderr:write(tostring(result), "\\n")
  os.exit(1)
end
io.stdout:write(result)
""".strip(),
        encoding="utf-8",
    )
    return subprocess.run(
        ["texlua", str(driver), str(JSON_CODEC)],
        input=payload,
        cwd=tmp_path,
        capture_output=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("payload", "canonical"),
    [
        (b"null", b"null"),
        (b"{}", b"{}"),
        (b"[]", b"[]"),
        (b'{"array":[{},[],null],"object":{"empty":{}}}', b'{"array":[{},[],null],"object":{"empty":{}}}'),
        ('{"clé":"déjà 😀"}'.encode(), '{"clé":"déjà 😀"}'.encode()),
        (b'{"emoji":"\\ud83d\\ude00","accent":"\\u00e9"}', '{"accent":"é","emoji":"😀"}'.encode()),
        (b'{"z":0,"a":1,"middle":{"y":2,"b":3}}', b'{"a":1,"middle":{"b":3,"y":2},"z":0}'),
        ('{"é":1,"z":2}'.encode(), '{"z":2,"é":1}'.encode()),
        (
            b'{"controls":"\\/\\b\\f\\n\\r\\t\\u0000"}',
            b'{"controls":"/\\b\\f\\n\\r\\t\\u0000"}',
        ),
        (b"-9007199254740991", b"-9007199254740991"),
        (b"9007199254740991", b"9007199254740991"),
    ],
)
def test_json_codec_round_trips_canonical_utf8(
    tmp_path: Path, payload: bytes, canonical: bytes
) -> None:
    result = _run_codec(tmp_path, payload)

    assert result.returncode == 0, result.stderr.decode(errors="replace")
    assert result.stdout == canonical


@pytest.mark.parametrize(
    "payload",
    [
        b'{"duplicate":1,"duplicate":2}',
        b'{"duplicate":1,"\\u0064uplicate":2}',
        b"null trailing",
        b'"\\x"',
        b'"line\nfeed"',
        b'"\\ud800"',
        b'"\\udc00"',
        b'"\\ud800\\u0041"',
        b"[1,]",
        b'{"a":1,}',
        b"\xef\xbb\xbfnull",
        b"1.0",
        b"1e3",
        b"-2E4",
        b"01",
        b"9007199254740992",
        b"-9223372036854775808",
        b"9223372036854775807",
        b'"\xc0\x80"',
        b'"\xed\xa0\x80"',
        b'"\xf4\x90\x80\x80"',
        b'"\xe2\x82"',
    ],
)
def test_json_codec_rejects_non_strict_input(tmp_path: Path, payload: bytes) -> None:
    result = _run_codec(tmp_path, payload)

    assert result.returncode != 0
    assert b"JSON decode error" in result.stderr


def _run_lua_source(tmp_path: Path, source: str) -> subprocess.CompletedProcess[str]:
    driver = tmp_path / "direct-driver.lua"
    driver.write_text(source, encoding="utf-8")
    return subprocess.run(
        ["texlua", str(driver), str(JSON_CODEC)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )


def test_json_codec_exposes_null_and_nested_container_tags(tmp_path: Path) -> None:
    result = _run_lua_source(
        tmp_path,
        """
local json = assert(loadfile(arg[1]))()
local value = json.decode('{"object":{},"array":[],"nested":[{},[]],"null":null}')
assert(json.container_type(value) == "object")
assert(json.container_type(value.object) == "object")
assert(json.container_type(value.array) == "array")
assert(json.container_type(value.nested) == "array")
assert(json.container_type(value.nested[1]) == "object")
assert(json.container_type(value.nested[2]) == "array")
assert(json.container_type(value.null) == "null")
assert(not rawequal(value.null, json.JSON_NULL))
io.write(json.encode(value))
""".strip(),
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == '{"array":[],"nested":[{},[]],"null":null,"object":{}}'


@pytest.mark.parametrize(
    "statement",
    [
        "return json.encode({})",
        'local value = json.new_object(); value[1] = "x"; return json.encode(value)',
        'local value = json.new_array(); value[2] = "x"; return json.encode(value)',
        "return json.encode(1.0)",
        "return json.encode(0 / 0)",
        "return json.encode(math.huge)",
        "return json.encode(math.mininteger)",
        "return json.encode(math.maxinteger)",
        "return json.encode(string.char(0xC0, 0x80))",
    ],
)
def test_json_encoder_rejects_ambiguous_or_invalid_values(
    tmp_path: Path, statement: str
) -> None:
    result = _run_lua_source(
        tmp_path,
        f"""
local json = assert(loadfile(arg[1]))()
local ok, message = pcall(function()
  {statement}
end)
if ok then
  error("encoding unexpectedly succeeded", 0)
end
io.stderr:write(tostring(message), "\\n")
os.exit(1)
""".strip(),
    )

    assert result.returncode != 0
    assert "JSON encode error" in result.stderr


def test_json_encoder_keeps_booleans_distinct_from_integers(tmp_path: Path) -> None:
    result = _run_lua_source(
        tmp_path,
        """
local json = assert(loadfile(arg[1]))()
io.write(json.encode(true), " ", json.encode(false), " ", json.encode(1))
""".strip(),
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true false 1"


def _run_solver(
    source: Path,
    output: Path,
    *,
    previous: Path | None = None,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    command = ["texlua", str(SOLVER), "--solve", str(source), "--output", str(output)]
    if previous is not None:
        command.extend(["--previous", str(previous)])
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def _stable_identical_layout() -> dict[str, object]:
    layout = _layout_with_identical_anchors()
    layout["state"] = "stable"
    layout["pass_number"] = 2
    layout["read_digest"] = layout["computed_digest"]
    target_positions = [20 * SP_PER_PT, 56 * SP_PER_PT, 92 * SP_PER_PT]
    for note, target_y in zip(layout["notes"], target_positions, strict=True):
        note["target_shipout_index"] = 1
        note["target_y_sp"] = target_y
    layout["pages"][0]["placed_note_ids"] = ["note-a", "note-b", "note-c"]
    return layout


def _mutate_contract_case(layout: dict[str, object], case: str) -> None:
    if case == "unexpected_root":
        layout["unexpected"] = True
    elif case == "unexpected_page":
        layout["pages"][0]["unexpected"] = True
    elif case == "unexpected_safe_rect":
        layout["pages"][0]["safe_rect"]["unexpected"] = True
    elif case == "unexpected_obstacle":
        layout["pages"][0]["obstacles"][0]["unexpected"] = True
    elif case == "unexpected_note":
        layout["notes"][0]["unexpected"] = True
    elif case == "stable_read_null":
        layout["read_digest"] = None
    elif case == "collecting_read_digest":
        layout["state"] = "collecting"
    elif case == "collecting_error":
        layout["state"] = "collecting"
        layout["read_digest"] = None
        layout["error_code"] = "malformed-margin-layout"
    elif case == "changed_equal_digests":
        layout["state"] = "changed"
    elif case == "stable_unequal_digests":
        layout["computed_digest"] = f"sha256:{4:064x}"
    elif case == "failed_without_error":
        layout["state"] = "failed"
        layout["error_code"] = None
    elif case == "noncanonical_notes":
        layout["notes"].reverse()
    elif case == "noncanonical_pages":
        layout["pages"].reverse()
    elif case == "noncanonical_native_ids":
        layout["pages"][0]["native_note_ids"].reverse()
    elif case == "noncanonical_obstacles":
        existing = layout["pages"][0]["obstacles"][0]
        later = {
            "id": "page-1-later",
            "left_sp": existing["left_sp"],
            "top_sp": 400000,
            "right_sp": existing["right_sp"],
            "bottom_sp": 450000,
        }
        layout["pages"][0]["obstacles"] = [later, existing]
    elif case == "duplicate_obstacle_id":
        layout["pages"][1]["obstacles"][0]["id"] = layout["pages"][0][
            "obstacles"
        ][0]["id"]
    elif case == "noncontiguous_pages":
        layout["pages"][1]["shipout_index"] = 3
    elif case == "wrong_rail_side":
        layout["pages"][0]["rail_side"] = "left"
    elif case == "invalid_safe_rect":
        layout["pages"][0]["safe_rect"]["right_sp"] = layout["pages"][0][
            "safe_rect"
        ]["left_sp"]
    elif case == "invalid_obstacle_rect":
        layout["pages"][0]["obstacles"][0]["bottom_sp"] = layout["pages"][0][
            "page_height_sp"
        ] + 1
    elif case == "unknown_page_note_reference":
        layout["pages"][0]["native_note_ids"][0] = "unknown"
    elif case == "unknown_target_page":
        layout["notes"][0]["target_shipout_index"] = 3
    elif case == "half_null_target":
        layout["notes"][0]["target_y_sp"] = None
    elif case == "incoherent_effective_height":
        layout["notes"][0]["effective_height_sp"] += 1
    elif case == "incoherent_membership":
        layout["pages"][1]["placed_note_ids"] = []
    elif case == "obstacle_intersection":
        layout["pages"][0]["obstacles"][0].update(
            {"top_sp": 200000, "bottom_sp": 250000}
        )
    elif case == "insufficient_gap":
        layout.clear()
        layout.update(_stable_identical_layout())
        layout["notes"][1]["target_y_sp"] -= 1
    else:  # pragma: no cover - keeps the mutation table fail-closed.
        raise AssertionError(f"unknown contract mutation {case}")


@pytest.mark.parametrize(
    "case",
    [
        "unexpected_root",
        "unexpected_page",
        "unexpected_safe_rect",
        "unexpected_obstacle",
        "unexpected_note",
        "stable_read_null",
        "collecting_read_digest",
        "collecting_error",
        "changed_equal_digests",
        "stable_unequal_digests",
        "failed_without_error",
        "noncanonical_notes",
        "noncanonical_pages",
        "noncanonical_native_ids",
        "noncanonical_obstacles",
        "duplicate_obstacle_id",
        "noncontiguous_pages",
        "wrong_rail_side",
        "invalid_safe_rect",
        "invalid_obstacle_rect",
        "unknown_page_note_reference",
        "unknown_target_page",
        "half_null_target",
        "incoherent_effective_height",
        "incoherent_membership",
        "obstacle_intersection",
        "insufficient_gap",
    ],
)
def test_lua_and_python_contracts_reject_the_same_layout_mutations(
    tmp_path: Path, case: str
) -> None:
    layout = json.loads(LAYOUT_FIXTURE.read_text(encoding="utf-8"))
    _mutate_contract_case(layout, case)
    contract = _load_margin_contract()
    with pytest.raises(contract.MarginContractError):
        contract.validate_margin_layout(layout)
    source = tmp_path / f"{case}.json"
    output = tmp_path / "must-not-exist.json"
    _write_json(source, layout)

    result = _run_solver(source, output, cwd=tmp_path)

    assert result.returncode != 0
    assert result.stderr.startswith("margin-layout-cli:")
    assert not output.exists()


def test_previous_stable_layout_with_null_read_digest_is_rejected(
    tmp_path: Path,
) -> None:
    current = tmp_path / "current.json"
    previous = tmp_path / "previous.json"
    output = tmp_path / "must-not-exist.json"
    _write_json(current, _layout_with_identical_anchors())
    invalid_previous = json.loads(LAYOUT_FIXTURE.read_text(encoding="utf-8"))
    invalid_previous["read_digest"] = None
    contract = _load_margin_contract()
    with pytest.raises(contract.MarginContractError):
        contract.validate_margin_layout(invalid_previous)
    _write_json(previous, invalid_previous)

    result = _run_solver(current, output, previous=previous, cwd=tmp_path)

    assert result.returncode != 0
    assert "previous.read_digest" in result.stderr
    assert not output.exists()


def test_solver_is_byte_deterministic_for_explicit_outputs(tmp_path: Path) -> None:
    source = tmp_path / "input.json"
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    _write_json(source, _layout_with_identical_anchors())

    first_run = _run_solver(source, first, cwd=tmp_path)
    second_run = subprocess.run(
        [
            "texlua",
            "scripts/solve_margin_layout.lua",
            "--solve",
            str(source),
            "--output",
            str(second),
        ],
        cwd=MANUAL_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert first_run.returncode == 0, first_run.stderr
    assert second_run.returncode == 0, second_run.stderr
    assert first.read_bytes() == second.read_bytes()
    contract = _load_margin_contract()
    contract.validate_margin_layout(json.loads(first.read_text(encoding="utf-8")))
    contract.validate_margin_layout(json.loads(second.read_text(encoding="utf-8")))


def test_solver_does_not_mutate_current_or_previous_tables(tmp_path: Path) -> None:
    current_path = tmp_path / "current.json"
    previous_path = tmp_path / "previous.json"
    _write_json(current_path, _layout_with_identical_anchors())
    _write_json(previous_path, _layout_with_identical_anchors())
    driver = tmp_path / "immutability-driver.lua"
    driver.write_text(
        """
local json = assert(loadfile(arg[1]))()
local layout = assert(loadfile(arg[2]))()
local function read(path)
  local file = assert(io.open(path, "rb"))
  local value = json.decode(file:read("*a"))
  assert(file:close())
  return value
end
local current = read(arg[3])
local previous = read(arg[4])
local current_before = json.encode(current)
local previous_before = json.encode(previous)
local solved = layout.solve(current, previous)
assert(json.encode(current) == current_before, "current layout mutated")
assert(json.encode(previous) == previous_before, "previous layout mutated")
assert(solved ~= current, "solver returned current table")
assert(solved.notes ~= current.notes, "solver reused notes array")
assert(solved.notes[1] ~= current.notes[1], "solver reused a note record")
assert(solved.pages[1] ~= current.pages[1], "solver reused a page record")
io.write(json.encode(solved))
""".strip(),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "texlua",
            str(driver),
            str(JSON_CODEC),
            str(MANUAL_ROOT / "gabarits" / "nexus-margin-layout.lua"),
            str(current_path),
            str(previous_path),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    solved = json.loads(result.stdout)
    _load_margin_contract().validate_margin_layout(solved)
    assert solved["pages"][0]["placed_note_ids"] == [
        "note-a",
        "note-b",
        "note-c",
    ]


def test_solver_deep_copies_every_json_metatable_including_null(tmp_path: Path) -> None:
    current_path = tmp_path / "current.json"
    previous_path = tmp_path / "previous.json"
    _write_json(current_path, _layout_with_identical_anchors())
    _write_json(previous_path, _layout_with_identical_anchors())
    driver = tmp_path / "metatable-driver.lua"
    driver.write_text(
        """
local json = assert(loadfile(arg[1]))()
local layout = assert(loadfile(arg[2]))()
local function read(path)
  local file = assert(io.open(path, "rb"))
  local value = json.decode(file:read("*a"))
  assert(file:close())
  return value
end
local function collect_metatables(value, found)
  found = found or {}
  if type(value) ~= "table" then
    return found
  end
  local metatable = getmetatable(value)
  assert(type(metatable) == "table", "JSON table lacks a metatable")
  found[metatable] = true
  if json.container_type(value) ~= "null" then
    for _, child in next, value do
      collect_metatables(child, found)
    end
  end
  return found
end
local function assert_disjoint(first, second, label)
  for metatable in next, first do
    assert(not second[metatable], label .. " shares a metatable")
  end
end
local current = read(arg[3])
local previous = read(arg[4])
local solved = layout.solve(current, previous)
local current_metatables = collect_metatables(current)
local previous_metatables = collect_metatables(previous)
local solved_metatables = collect_metatables(solved)
assert_disjoint(current_metatables, previous_metatables, "current/previous")
assert_disjoint(current_metatables, solved_metatables, "current/result")
assert_disjoint(previous_metatables, solved_metatables, "previous/result")
assert(not rawequal(solved.read_digest, current.read_digest), "result reused current null")
assert(not rawequal(solved.read_digest, previous.read_digest), "result reused previous null")
getmetatable(solved).__result_mutation = true
getmetatable(solved.notes).__result_array_mutation = true
getmetatable(solved.notes[1]).__result_record_mutation = true
getmetatable(solved.read_digest).__result_null_mutation = true
assert(getmetatable(current).__result_mutation == nil)
assert(getmetatable(previous).__result_mutation == nil)
assert(getmetatable(current.notes).__result_array_mutation == nil)
assert(getmetatable(previous.notes).__result_array_mutation == nil)
assert(getmetatable(current.notes[1]).__result_record_mutation == nil)
assert(getmetatable(previous.notes[1]).__result_record_mutation == nil)
assert(getmetatable(current.read_digest).__result_null_mutation == nil)
assert(getmetatable(previous.read_digest).__result_null_mutation == nil)
getmetatable(current.pages).__current_mutation = true
assert(getmetatable(previous.pages).__current_mutation == nil)
assert(getmetatable(solved.pages).__current_mutation == nil)
io.write(json.encode(solved))
""".strip(),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "texlua",
            str(driver),
            str(JSON_CODEC),
            str(MANUAL_ROOT / "gabarits" / "nexus-margin-layout.lua"),
            str(current_path),
            str(previous_path),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    _load_margin_contract().validate_margin_layout(json.loads(result.stdout))


def test_layout_module_exposes_only_the_pure_solve_api(tmp_path: Path) -> None:
    result = _run_lua_source(
        tmp_path,
        f"""
local layout = assert(loadfile([[{MANUAL_ROOT / "gabarits" / "nexus-margin-layout.lua"}]]))()
local count = 0
for key, value in next, layout do
  count = count + 1
  assert(key == "solve", "unexpected public key " .. tostring(key))
  assert(type(value) == "function", "solve is not a function")
end
assert(count == 1, "expected exactly one public API entry")
""".strip(),
    )

    assert result.returncode == 0, result.stderr


def test_carry_in_starts_at_safe_top_and_precedes_native_notes(tmp_path: Path) -> None:
    layout = _layout_with_identical_anchors()
    carried = layout["notes"][0]
    carried["id"] = "carried"
    carried["global_order"] = 1
    carried["origin_shipout_index"] = 1
    carried["target_shipout_index"] = 2
    carried["target_y_sp"] = 15 * SP_PER_PT
    carried["report_decoration_height_sp"] = 5 * SP_PER_PT
    carried["effective_height_sp"] = 35 * SP_PER_PT
    carried["report_depth"] = 1
    carried["requires_marker"] = True
    native = layout["notes"][1]
    native["id"] = "native"
    native["global_order"] = 2
    native["origin_shipout_index"] = 2
    native["origin_folio"] = "2"
    native["target_shipout_index"] = 2
    native["target_y_sp"] = 56 * SP_PER_PT
    layout["notes"] = [carried, native]
    first_page = layout["pages"][0]
    first_page["native_note_ids"] = ["carried"]
    first_page["reported_note_ids"] = ["carried"]
    second_page = {
        **first_page,
        "shipout_index": 2,
        "folio": "2",
        "rail_side": "left",
        "native_note_ids": ["native"],
        "carry_in_note_ids": ["carried"],
        "placed_note_ids": ["carried", "native"],
        "reported_note_ids": [],
        "safe_rect": {**first_page["safe_rect"], "top_sp": 15 * SP_PER_PT},
    }
    layout["pages"] = [first_page, second_page]
    source = tmp_path / "input.json"
    output = tmp_path / "output.json"
    _write_json(source, layout)

    result = _run_solver(source, output, cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    solved = json.loads(output.read_text(encoding="utf-8"))
    _load_margin_contract().validate_margin_layout(solved)
    assert solved["pages"][1]["placed_note_ids"] == ["carried", "native"]
    notes = {note["id"]: note for note in solved["notes"]}
    assert notes["carried"]["target_y_sp"] == 15 * SP_PER_PT
    assert notes["native"]["target_y_sp"] == 56 * SP_PER_PT


@pytest.mark.parametrize(
    "case",
    [
        "duplicate_top_level_id",
        "unknown_native_id",
        "missing_native_id",
        "duplicate_native_id",
        "bad_notes_container",
        "boolean_global_order",
        "string_origin_y",
        "bad_page_width",
        "bad_obstacles_container",
        "bad_role",
        "bad_requires_marker",
        "bad_nullable_target",
        "bad_digest",
        "bad_state",
    ],
)
def test_solver_rejects_missing_duplicate_and_badly_typed_data(
    tmp_path: Path, case: str
) -> None:
    layout = _layout_with_identical_anchors()
    if case == "duplicate_top_level_id":
        layout["notes"][1]["id"] = layout["notes"][0]["id"]
    elif case == "unknown_native_id":
        layout["pages"][0]["native_note_ids"][0] = "unknown"
    elif case == "missing_native_id":
        layout["pages"][0]["native_note_ids"].pop()
    elif case == "duplicate_native_id":
        layout["pages"][0]["native_note_ids"][1] = layout["pages"][0][
            "native_note_ids"
        ][0]
    elif case == "bad_notes_container":
        layout["notes"] = {"not": "an array"}
    elif case == "boolean_global_order":
        layout["notes"][0]["global_order"] = True
    elif case == "string_origin_y":
        layout["notes"][0]["origin_y_sp"] = "20pt"
    elif case == "bad_page_width":
        layout["pages"][0]["page_width_sp"] = "wide"
    elif case == "bad_obstacles_container":
        layout["pages"][0]["obstacles"] = {"not": "an array"}
    elif case == "bad_role":
        layout["notes"][0]["role"] = False
    elif case == "bad_requires_marker":
        layout["notes"][0]["requires_marker"] = 0
    elif case == "bad_nullable_target":
        layout["notes"][0]["target_y_sp"] = "unset"
    elif case == "bad_digest":
        layout["notes"][0]["semantic_digest"] = "not-a-digest"
    elif case == "bad_state":
        layout["state"] = "finished"
    contract = _load_margin_contract()
    with pytest.raises(contract.MarginContractError):
        contract.validate_margin_layout(layout)
    source = tmp_path / "invalid.json"
    output = tmp_path / "must-not-exist.json"
    _write_json(source, layout)

    result = _run_solver(source, output, cwd=tmp_path)

    assert result.returncode != 0
    assert result.stderr.startswith("margin-layout-cli:")
    assert "stack traceback" not in result.stderr
    assert not output.exists()


def test_solver_validates_previous_without_mutating_output(tmp_path: Path) -> None:
    source = tmp_path / "current.json"
    previous = tmp_path / "previous.json"
    output = tmp_path / "must-not-exist.json"
    _write_json(source, _layout_with_identical_anchors())
    bad_previous = copy.deepcopy(_layout_with_identical_anchors())
    bad_previous["notes"][0]["effective_height_sp"] = "thirty points"
    _write_json(previous, bad_previous)

    result = _run_solver(source, output, previous=previous, cwd=tmp_path)

    assert result.returncode != 0
    assert "previous.notes" in result.stderr
    assert not output.exists()


@pytest.mark.parametrize(
    "arguments",
    [
        ["--unknown", "value"],
        ["--solve", "one", "--solve", "two", "--output", "out"],
        ["--output", "out"],
        ["--solve", "input"],
        ["--solve", "--output", "out"],
        ["--solve", "input", "--output"],
    ],
)
def test_cli_rejects_unknown_duplicate_and_missing_options(
    tmp_path: Path, arguments: list[str]
) -> None:
    result = subprocess.run(
        ["texlua", str(SOLVER), *arguments],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert result.stderr.startswith("margin-layout-cli:")
    assert "stack traceback" not in result.stderr


def test_cli_rejects_output_aliasing_an_input_without_touching_it(tmp_path: Path) -> None:
    source = tmp_path / "input.json"
    original = json.dumps(_layout_with_identical_anchors()).encode()
    source.write_bytes(original)

    result = subprocess.run(
        [
            "texlua",
            str(SOLVER),
            "--solve",
            str(source),
            "--output",
            str(tmp_path / "." / "input.json"),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "output must differ" in result.stderr
    assert source.read_bytes() == original


@pytest.mark.parametrize("alias_kind", ["symlink", "hardlink"])
def test_cli_rejects_filesystem_alias_of_input(
    tmp_path: Path, alias_kind: str
) -> None:
    source = tmp_path / "input.json"
    alias = tmp_path / "output.json"
    original = json.dumps(_layout_with_identical_anchors()).encode()
    source.write_bytes(original)
    if alias_kind == "symlink":
        alias.symlink_to(source)
    else:
        alias.hardlink_to(source)

    result = _run_solver(source, alias, cwd=tmp_path)

    assert result.returncode != 0
    assert "output must differ" in result.stderr
    assert source.read_bytes() == original


def test_cli_leaves_existing_output_untouched_on_invalid_json(tmp_path: Path) -> None:
    source = tmp_path / "invalid.json"
    output = tmp_path / "existing.json"
    source.write_bytes(b'{"broken":')
    output.write_bytes(b"preserve-me")

    result = _run_solver(source, output, cwd=tmp_path)

    assert result.returncode != 0
    assert result.stderr.startswith("margin-layout-cli:")
    assert "stack traceback" not in result.stderr
    assert output.read_bytes() == b"preserve-me"


def test_cli_never_follows_unrelated_output_symlink(tmp_path: Path) -> None:
    source = tmp_path / "input.json"
    victim = tmp_path / "unrelated.txt"
    output = tmp_path / "output.json"
    _write_json(source, _layout_with_identical_anchors())
    victim.write_bytes(b"third-party-bytes")
    output.symlink_to(victim)
    entries_before = {path.name for path in tmp_path.iterdir()}

    result = _run_solver(source, output, cwd=tmp_path)

    assert result.returncode != 0
    assert "symbolic link" in result.stderr
    assert output.is_symlink()
    assert victim.read_bytes() == b"third-party-bytes"
    assert {path.name for path in tmp_path.iterdir()} == entries_before


def test_cli_preserves_existing_output_when_temp_creation_fails(tmp_path: Path) -> None:
    source = tmp_path / "input.json"
    locked_parent = tmp_path / "locked"
    locked_parent.mkdir()
    output = locked_parent / "output.json"
    _write_json(source, _layout_with_identical_anchors())
    output.write_bytes(b"old-output")
    locked_parent.chmod(0o500)

    try:
        result = _run_solver(source, output, cwd=tmp_path)
    finally:
        locked_parent.chmod(0o700)

    assert result.returncode != 0
    assert output.read_bytes() == b"old-output"
    assert [path.name for path in locked_parent.iterdir()] == ["output.json"]


def test_cli_rejects_directory_output_without_temp_residue(tmp_path: Path) -> None:
    source = tmp_path / "input.json"
    output = tmp_path / "output.json"
    _write_json(source, _layout_with_identical_anchors())
    output.mkdir()
    entries_before = {path.name for path in tmp_path.iterdir()}

    result = _run_solver(source, output, cwd=tmp_path)

    assert result.returncode != 0
    assert "regular file" in result.stderr
    assert output.is_dir()
    assert {path.name for path in tmp_path.iterdir()} == entries_before


def test_cli_rejects_missing_output_parent_without_residue(tmp_path: Path) -> None:
    source = tmp_path / "input.json"
    missing_parent = tmp_path / "missing"
    output = missing_parent / "output.json"
    _write_json(source, _layout_with_identical_anchors())

    result = _run_solver(source, output, cwd=tmp_path)

    assert result.returncode != 0
    assert not missing_parent.exists()


@pytest.mark.parametrize("failure_stage", ["write", "close", "rename"])
def test_cli_preserves_existing_output_on_publication_failure(
    tmp_path: Path, failure_stage: str
) -> None:
    source = tmp_path / "input.json"
    output = tmp_path / "output.json"
    driver = tmp_path / "publication-failure-driver.lua"
    _write_json(source, _layout_with_identical_anchors())
    output.write_bytes(b"old-output")
    driver.write_text(
        """
local stage = arg[1]
local solver = arg[2]
local input = arg[3]
local output = arg[4]
local real_open = io.open
local real_rename = os.rename
if stage == "write" or stage == "close" then
  io.open = function(path, mode)
    if mode == "wb" and path:match("/payload$") then
      local fake = {}
      function fake:write(_)
        if stage == "write" then
          return nil, "simulated write failure"
        end
        return self
      end
      function fake:close()
        if stage == "close" then
          return nil, "simulated close failure"
        end
        return true
      end
      return fake
    end
    return real_open(path, mode)
  end
elseif stage == "rename" then
  os.rename = function(_, _)
    return nil, "simulated rename failure"
  end
end
arg = {
  [0] = solver,
  "--solve", input,
  "--output", output,
}
dofile(solver)
os.rename = real_rename
""".strip(),
        encoding="utf-8",
    )
    entries_before = {path.name for path in tmp_path.iterdir()}

    result = subprocess.run(
        [
            "texlua",
            str(driver),
            failure_stage,
            str(SOLVER),
            str(source),
            str(output),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert f"simulated {failure_stage} failure" in result.stderr
    assert output.read_bytes() == b"old-output"
    assert {path.name for path in tmp_path.iterdir()} == entries_before
