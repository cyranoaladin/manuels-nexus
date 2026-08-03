"""Valide les en-têtes % META de tous les .tex contre les schémas JSON."""

import json
import re
import sys
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, validate

MANUAL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = MANUAL_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import margin_contract  # noqa: E402

SCHEMAS = MANUAL_ROOT / "schemas"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
EX_SCHEMA = json.loads((SCHEMAS / "exercice.schema.json").read_text(encoding="utf-8"))
META = re.compile(r"% META: (\{.*\})")

tex_files = sorted((MANUAL_ROOT / "chapitres").rglob("*.tex"))


@pytest.mark.parametrize(
    "tex", tex_files, ids=lambda p: str(p.relative_to(MANUAL_ROOT))
)
def test_meta_valid(tex):
    m = META.search(tex.read_text(encoding="utf-8"))
    assert m, f"{tex} : en-tête % META manquant (règle R4)"
    meta = json.loads(m.group(1))
    if meta.get("type_objet") == "exercice":
        validate(meta, EX_SCHEMA)


def test_contrats_schema():
    import yaml
    from jsonschema import validate as v

    schema = json.loads(
        (SCHEMAS / "contrat_chapitre.schema.json").read_text(encoding="utf-8")
    )
    for c in (MANUAL_ROOT / "chapitres").glob("*/contrat.yaml"):
        v(yaml.safe_load(c.read_text(encoding="utf-8")), schema)


MARGIN_PROOFS = (
    (
        "margin-layout.schema.json",
        "margin-layout.valid.json",
        margin_contract.validate_margin_layout,
    ),
    (
        "margin-stable-layout.schema.json",
        "margin-stable-layout.valid.json",
        margin_contract.validate_stable_layout,
    ),
    (
        "margin-ledger.schema.json",
        "margin-ledger.valid.json",
        margin_contract.validate_margin_ledger,
    ),
)
MARGIN_GAP_SP = 6 * 65536

DIGEST_PATHS = (
    (
        "margin-layout.valid.json",
        margin_contract.validate_margin_layout,
        ("geometry_digest",),
    ),
    (
        "margin-layout.valid.json",
        margin_contract.validate_margin_layout,
        ("semantic_digest",),
    ),
    (
        "margin-layout.valid.json",
        margin_contract.validate_margin_layout,
        ("read_digest",),
    ),
    (
        "margin-layout.valid.json",
        margin_contract.validate_margin_layout,
        ("computed_digest",),
    ),
    (
        "margin-layout.valid.json",
        margin_contract.validate_margin_layout,
        ("notes", 0, "semantic_digest"),
    ),
    (
        "margin-stable-layout.valid.json",
        margin_contract.validate_stable_layout,
        ("geometry_digest",),
    ),
    (
        "margin-stable-layout.valid.json",
        margin_contract.validate_stable_layout,
        ("semantic_digest",),
    ),
    (
        "margin-stable-layout.valid.json",
        margin_contract.validate_stable_layout,
        ("notes", 0, "semantic_digest"),
    ),
    (
        "margin-ledger.valid.json",
        margin_contract.validate_margin_ledger,
        ("pdf_sha256",),
    ),
    (
        "margin-ledger.valid.json",
        margin_contract.validate_margin_ledger,
        ("capture_inventory_digest",),
    ),
    (
        "margin-ledger.valid.json",
        margin_contract.validate_margin_ledger,
        ("stable_layout_digest",),
    ),
    (
        "margin-ledger.valid.json",
        margin_contract.validate_margin_ledger,
        ("rendered_stream_digest",),
    ),
    (
        "margin-ledger.valid.json",
        margin_contract.validate_margin_ledger,
        ("notes", 0, "semantic_digest"),
    ),
    (
        "margin-ledger.valid.json",
        margin_contract.validate_margin_ledger,
        ("notes", 0, "rendered_stream_digest"),
    ),
)


def _margin_proof_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _margin_proof_assert_rejected(validator, document: dict) -> None:
    with pytest.raises(margin_contract.MarginContractError):
        validator(document)


@pytest.mark.parametrize("schema_name,fixture_name,contract_validator", MARGIN_PROOFS)
def test_margin_proof_schemas_are_closed(
    schema_name: str, fixture_name: str, contract_validator
) -> None:
    schema = json.loads((SCHEMAS / schema_name).read_text(encoding="utf-8"))
    fixture = _margin_proof_fixture(fixture_name)

    Draft202012Validator.check_schema(schema)
    assert not list(Draft202012Validator(schema).iter_errors(fixture))
    assert contract_validator(fixture) == fixture

    fixture["unexpected"] = True
    assert list(Draft202012Validator(schema).iter_errors(fixture))
    _margin_proof_assert_rejected(contract_validator, fixture)


def test_margin_proof_layout_and_stable_layout_share_exact_record_definitions() -> None:
    private_schema = json.loads(
        (SCHEMAS / "margin-layout.schema.json").read_text(encoding="utf-8")
    )
    stable_schema = json.loads(
        (SCHEMAS / "margin-stable-layout.schema.json").read_text(encoding="utf-8")
    )

    for definition in ("rect", "obstacle", "note_id_list", "page", "note"):
        assert private_schema["$defs"][definition] == stable_schema["$defs"][definition]


@pytest.mark.parametrize(
    "fixture_name,validator,path",
    [
        (
            "margin-layout.valid.json",
            margin_contract.validate_margin_layout,
            ("notes", 0),
        ),
        (
            "margin-layout.valid.json",
            margin_contract.validate_margin_layout,
            ("pages", 0),
        ),
        (
            "margin-stable-layout.valid.json",
            margin_contract.validate_stable_layout,
            ("pages", 0, "safe_rect"),
        ),
        (
            "margin-stable-layout.valid.json",
            margin_contract.validate_stable_layout,
            ("pages", 0, "obstacles", 0),
        ),
        (
            "margin-ledger.valid.json",
            margin_contract.validate_margin_ledger,
            ("notes", 0),
        ),
    ],
)
def test_margin_proof_schemas_reject_nested_extra_keys(
    fixture_name: str, validator, path: tuple[str | int, ...]
) -> None:
    document = _margin_proof_fixture(fixture_name)
    target = document
    for component in path:
        target = target[component]
    target["unexpected"] = True
    _margin_proof_assert_rejected(validator, document)


@pytest.mark.parametrize(
    "fixture_name,validator,path",
    [
        (
            "margin-layout.valid.json",
            margin_contract.validate_margin_layout,
            ("notes", 0, "width_sp"),
        ),
        (
            "margin-stable-layout.valid.json",
            margin_contract.validate_stable_layout,
            ("pages", 0, "safe_rect", "right_sp"),
        ),
        (
            "margin-ledger.valid.json",
            margin_contract.validate_margin_ledger,
            ("notes", 0, "bbox_sp", 2),
        ),
    ],
)
def test_margin_proof_schemas_reject_floating_point_dimensions(
    fixture_name: str, validator, path: tuple[str | int, ...]
) -> None:
    document = _margin_proof_fixture(fixture_name)
    target = document
    for component in path[:-1]:
        target = target[component]
    target[path[-1]] = 1.5
    _margin_proof_assert_rejected(validator, document)


@pytest.mark.parametrize(
    "fixture_name,validator,path",
    [
        (
            "margin-layout.valid.json",
            margin_contract.validate_margin_layout,
            ("pass_number",),
        ),
        (
            "margin-stable-layout.valid.json",
            margin_contract.validate_stable_layout,
            ("notes", 0, "global_order"),
        ),
        (
            "margin-ledger.valid.json",
            margin_contract.validate_margin_ledger,
            ("notes", 0, "form_xref"),
        ),
    ],
)
def test_margin_proof_schemas_do_not_treat_booleans_as_integers(
    fixture_name: str, validator, path: tuple[str | int, ...]
) -> None:
    document = _margin_proof_fixture(fixture_name)
    target = document
    for component in path[:-1]:
        target = target[component]
    target[path[-1]] = True
    _margin_proof_assert_rejected(validator, document)


@pytest.mark.parametrize(
    "fixture_name,validator,field",
    [
        (
            "margin-layout.valid.json",
            margin_contract.validate_margin_layout,
            "geometry_digest",
        ),
        (
            "margin-stable-layout.valid.json",
            margin_contract.validate_stable_layout,
            "semantic_digest",
        ),
        (
            "margin-ledger.valid.json",
            margin_contract.validate_margin_ledger,
            "pdf_sha256",
        ),
    ],
)
def test_margin_proof_schemas_reject_malformed_sha256(
    fixture_name: str, validator, field: str
) -> None:
    document = _margin_proof_fixture(fixture_name)
    document[field] = "sha256:not-a-digest"
    _margin_proof_assert_rejected(validator, document)


def test_margin_proof_schema_patterns_have_exact_lengths() -> None:
    for schema_name in (
        "margin-layout.schema.json",
        "margin-stable-layout.schema.json",
        "margin-ledger.schema.json",
    ):
        schema = json.loads((SCHEMAS / schema_name).read_text(encoding="utf-8"))
        assert schema["$defs"]["sha256"]["minLength"] == 71
        assert schema["$defs"]["sha256"]["maxLength"] == 71

    private_schema = json.loads(
        (SCHEMAS / "margin-layout.schema.json").read_text(encoding="utf-8")
    )
    assert private_schema["$defs"]["run_nonce"]["minLength"] == 32
    assert private_schema["$defs"]["run_nonce"]["maxLength"] == 32


@pytest.mark.parametrize("fixture_name,validator,path", DIGEST_PATHS)
@pytest.mark.parametrize("suffix", ["\n", "\r", "\u2028", "\u2029", "\u00a0"])
def test_margin_proof_digest_fields_reject_trailing_unicode(
    fixture_name: str,
    validator,
    path: tuple[str | int, ...],
    suffix: str,
) -> None:
    document = _margin_proof_fixture(fixture_name)
    target = document
    for component in path[:-1]:
        target = target[component]
    target[path[-1]] += suffix

    _margin_proof_assert_rejected(validator, document)


def test_margin_proof_private_envelope_requires_a_lowercase_32_hex_nonce() -> None:
    trailing_unicode = ("\n", "\r", "\u2028", "\u2029", "\u00a0")
    for bad_nonce in (
        "short",
        "A" * 32,
        "g" * 32,
        "0" * 33,
        *("0" * 32 + suffix for suffix in trailing_unicode),
    ):
        document = _margin_proof_fixture("margin-layout.valid.json")
        document["run_nonce"] = bad_nonce
        _margin_proof_assert_rejected(margin_contract.validate_margin_layout, document)


@pytest.mark.parametrize(
    "fixture_name,validator",
    [
        (
            "margin-layout.valid.json",
            margin_contract.validate_margin_layout,
        ),
        (
            "margin-stable-layout.valid.json",
            margin_contract.validate_stable_layout,
        ),
    ],
)
def test_margin_proof_layout_rejects_duplicate_note_ids_and_orders(
    fixture_name: str, validator
) -> None:
    original = _margin_proof_fixture(fixture_name)

    duplicate_id = deepcopy(original)
    duplicate_id["notes"][1]["id"] = duplicate_id["notes"][0]["id"]
    _margin_proof_assert_rejected(validator, duplicate_id)

    duplicate_order = deepcopy(original)
    duplicate_order["notes"][1]["global_order"] = duplicate_order["notes"][0][
        "global_order"
    ]
    _margin_proof_assert_rejected(validator, duplicate_order)


@pytest.mark.parametrize(
    "fixture_name,validator",
    [
        (
            "margin-layout.valid.json",
            margin_contract.validate_margin_layout,
        ),
        (
            "margin-stable-layout.valid.json",
            margin_contract.validate_stable_layout,
        ),
    ],
)
def test_margin_proof_layout_rejects_duplicate_shipouts_and_obstacles(
    fixture_name: str, validator
) -> None:
    original = _margin_proof_fixture(fixture_name)

    duplicate_shipout = deepcopy(original)
    copied_page = deepcopy(duplicate_shipout["pages"][0])
    copied_page["folio"] = "duplicate"
    copied_page["native_note_ids"] = []
    copied_page["placed_note_ids"] = []
    copied_page["reported_note_ids"] = []
    copied_page["obstacles"] = []
    duplicate_shipout["pages"].append(copied_page)
    _margin_proof_assert_rejected(validator, duplicate_shipout)

    duplicate_obstacle = deepcopy(original)
    obstacle = deepcopy(duplicate_obstacle["pages"][0]["obstacles"][0])
    duplicate_obstacle["pages"][1]["obstacles"].append(obstacle)
    _margin_proof_assert_rejected(validator, duplicate_obstacle)


def _margin_proof_empty_three_page_layout(fixture_name: str) -> dict:
    layout = _margin_proof_fixture(fixture_name)
    layout["notes"] = []
    for page in layout["pages"]:
        page["native_note_ids"] = []
        page["carry_in_note_ids"] = []
        page["placed_note_ids"] = []
        page["reported_note_ids"] = []
        page["obstacles"] = []
    third_page = deepcopy(layout["pages"][0])
    third_page["shipout_index"] = 3
    third_page["folio"] = "3"
    layout["pages"].append(third_page)
    return layout


@pytest.mark.parametrize(
    "fixture_name,validator",
    [
        ("margin-layout.valid.json", margin_contract.validate_margin_layout),
        (
            "margin-stable-layout.valid.json",
            margin_contract.validate_stable_layout,
        ),
    ],
)
def test_margin_proof_pages_must_be_contiguous_from_one(
    fixture_name: str, validator
) -> None:
    layout = _margin_proof_empty_three_page_layout(fixture_name)
    assert validator(layout) == layout

    del layout["pages"][1]

    _margin_proof_assert_rejected(validator, layout)


def _margin_proof_prepare_two_reported_notes(layout: dict) -> None:
    first_note, second_note = layout["notes"]
    first_note["target_shipout_index"] = 2
    first_note["target_y_sp"] = 800000
    first_note["report_decoration_height_sp"] = 20000
    first_note["effective_height_sp"] = 120000
    first_note["report_depth"] = 1
    first_note["requires_marker"] = True

    first_page, second_page = layout["pages"]
    first_page["placed_note_ids"] = []
    first_page["reported_note_ids"] = [first_note["id"], second_note["id"]]
    second_page["carry_in_note_ids"] = [first_note["id"], second_note["id"]]
    second_page["placed_note_ids"] = [second_note["id"], first_note["id"]]


def _margin_proof_add_second_obstacle(layout: dict) -> None:
    layout["pages"][0]["obstacles"].append(
        {
            "id": "page-1-middle",
            "left_sp": 900000,
            "top_sp": 800000,
            "right_sp": 1100000,
            "bottom_sp": 850000,
        }
    )


def _margin_proof_permute_canonical_category(layout: dict, category: str) -> None:
    if category == "pages":
        layout["pages"].reverse()
    elif category == "notes":
        layout["notes"].reverse()
    elif category == "obstacles":
        layout["pages"][0]["obstacles"].reverse()
    elif category == "native_note_ids":
        layout["pages"][0]["native_note_ids"].reverse()
    else:
        page_index = 0 if category == "reported_note_ids" else 1
        layout["pages"][page_index][category].reverse()


@pytest.mark.parametrize(
    "fixture_name,validator",
    [
        ("margin-layout.valid.json", margin_contract.validate_margin_layout),
        (
            "margin-stable-layout.valid.json",
            margin_contract.validate_stable_layout,
        ),
    ],
)
@pytest.mark.parametrize(
    "category",
    [
        "pages",
        "notes",
        "obstacles",
        "native_note_ids",
        "carry_in_note_ids",
        "reported_note_ids",
        "placed_note_ids",
    ],
)
def test_margin_proof_layout_rejects_noncanonical_array_order(
    fixture_name: str, validator, category: str
) -> None:
    layout = _margin_proof_fixture(fixture_name)
    if category == "obstacles":
        _margin_proof_add_second_obstacle(layout)
        assert validator(layout) == layout
    if category in {"carry_in_note_ids", "reported_note_ids", "placed_note_ids"}:
        _margin_proof_prepare_two_reported_notes(layout)
        assert validator(layout) == layout

    canonical_bytes = margin_contract.canonical_json_bytes(layout)
    _margin_proof_permute_canonical_category(layout, category)

    assert margin_contract.canonical_json_bytes(layout) != canonical_bytes
    _margin_proof_assert_rejected(validator, layout)


def test_margin_proof_report_depth_is_the_shipout_index_difference() -> None:
    layout = _margin_proof_fixture("margin-stable-layout.valid.json")
    third_page = deepcopy(layout["pages"][0])
    third_page["shipout_index"] = 3
    third_page["folio"] = "3"
    third_page["native_note_ids"] = []
    third_page["carry_in_note_ids"] = [layout["notes"][1]["id"]]
    third_page["placed_note_ids"] = [layout["notes"][1]["id"]]
    third_page["reported_note_ids"] = []
    third_page["obstacles"] = []
    layout["pages"].append(third_page)

    reported_note = layout["notes"][1]
    reported_note["target_shipout_index"] = 3
    reported_note["target_y_sp"] = 200000
    reported_note["report_depth"] = 2
    layout["pages"][1]["placed_note_ids"] = []
    layout["pages"][1]["reported_note_ids"] = [reported_note["id"]]
    assert margin_contract.validate_stable_layout(layout) == layout

    reported_note["report_depth"] = 1
    _margin_proof_assert_rejected(margin_contract.validate_stable_layout, layout)


@pytest.mark.parametrize(
    "fixture_name,validator",
    [
        (
            "margin-layout.valid.json",
            margin_contract.validate_margin_layout,
        ),
        (
            "margin-stable-layout.valid.json",
            margin_contract.validate_stable_layout,
        ),
    ],
)
def test_margin_proof_layout_rejects_broken_page_and_note_references(
    fixture_name: str, validator
) -> None:
    original = _margin_proof_fixture(fixture_name)

    missing_origin_page = deepcopy(original)
    missing_origin_page["notes"][0]["origin_shipout_index"] = 999
    _margin_proof_assert_rejected(validator, missing_origin_page)

    wrong_folio = deepcopy(original)
    wrong_folio["notes"][0]["origin_folio"] = "not-the-page-folio"
    _margin_proof_assert_rejected(validator, wrong_folio)

    unknown_list_id = deepcopy(original)
    unknown_list_id["pages"][0]["native_note_ids"][0] = "missing-note"
    _margin_proof_assert_rejected(validator, unknown_list_id)

    missing_carry_reference = deepcopy(original)
    missing_carry_reference["pages"][1]["carry_in_note_ids"] = []
    _margin_proof_assert_rejected(validator, missing_carry_reference)

    placement_on_wrong_page = deepcopy(original)
    placement_on_wrong_page["pages"][1]["placed_note_ids"].append(
        placement_on_wrong_page["notes"][0]["id"]
    )
    _margin_proof_assert_rejected(validator, placement_on_wrong_page)

    duplicate_within_list = deepcopy(original)
    duplicate_within_list["pages"][0]["native_note_ids"].append(
        duplicate_within_list["pages"][0]["native_note_ids"][0]
    )
    _margin_proof_assert_rejected(validator, duplicate_within_list)

    half_null_target = deepcopy(original)
    half_null_target["notes"][0]["target_y_sp"] = None
    _margin_proof_assert_rejected(validator, half_null_target)


def test_margin_proof_layout_rejects_incoherent_rectangles_and_heights() -> None:
    original = _margin_proof_fixture("margin-stable-layout.valid.json")

    inverted_rect = deepcopy(original)
    inverted_rect["pages"][0]["safe_rect"]["right_sp"] = inverted_rect["pages"][0][
        "safe_rect"
    ]["left_sp"]
    _margin_proof_assert_rejected(margin_contract.validate_stable_layout, inverted_rect)

    rect_outside_page = deepcopy(original)
    rect_outside_page["pages"][0]["obstacles"][0]["bottom_sp"] = (
        rect_outside_page["pages"][0]["page_height_sp"] + 1
    )
    _margin_proof_assert_rejected(
        margin_contract.validate_stable_layout, rect_outside_page
    )

    wrong_effective_height = deepcopy(original)
    wrong_effective_height["notes"][1]["effective_height_sp"] += 1
    _margin_proof_assert_rejected(
        margin_contract.validate_stable_layout, wrong_effective_height
    )


def _margin_proof_place_both_notes_on_first_page(
    layout: dict, *, second_y_sp: int
) -> None:
    second_note = layout["notes"][1]
    second_note["target_shipout_index"] = 1
    second_note["target_y_sp"] = second_y_sp
    second_note["report_decoration_height_sp"] = 0
    second_note["effective_height_sp"] = second_note["base_height_sp"]
    second_note["report_depth"] = 0

    first_page, second_page = layout["pages"]
    first_page["placed_note_ids"].append(second_note["id"])
    first_page["reported_note_ids"] = []
    second_page["carry_in_note_ids"] = []
    second_page["placed_note_ids"] = []


@pytest.mark.parametrize(
    "fixture_name,validator",
    [
        (
            "margin-stable-layout.valid.json",
            margin_contract.validate_stable_layout,
        ),
        ("margin-layout.valid.json", margin_contract.validate_margin_layout),
    ],
)
def test_margin_proof_stable_geometry_rejects_overlapping_notes(
    fixture_name: str, validator
) -> None:
    layout = _margin_proof_fixture(fixture_name)
    _margin_proof_place_both_notes_on_first_page(layout, second_y_sp=200000)

    _margin_proof_assert_rejected(
        validator,
        layout,
    )


def test_margin_proof_stable_geometry_rejects_note_obstacle_intersection() -> None:
    layout = _margin_proof_fixture("margin-stable-layout.valid.json")
    layout["notes"][0]["target_y_sp"] = 149999

    _margin_proof_assert_rejected(
        margin_contract.validate_stable_layout,
        layout,
    )


def test_margin_proof_stable_geometry_allows_tangent_obstacle_edge() -> None:
    obstacle_tangent = _margin_proof_fixture("margin-stable-layout.valid.json")
    obstacle_tangent["notes"][0]["target_y_sp"] = 150000
    assert margin_contract.validate_stable_layout(obstacle_tangent) == obstacle_tangent


def test_margin_proof_stable_geometry_accepts_exactly_six_point_note_gap() -> None:
    layout = _margin_proof_fixture("margin-stable-layout.valid.json")
    _margin_proof_place_both_notes_on_first_page(
        layout,
        second_y_sp=200000 + 100000 + MARGIN_GAP_SP,
    )

    assert margin_contract.validate_stable_layout(layout) == layout


def test_margin_proof_stable_geometry_rejects_gap_one_sp_too_short() -> None:
    layout = _margin_proof_fixture("margin-stable-layout.valid.json")
    _margin_proof_place_both_notes_on_first_page(
        layout,
        second_y_sp=200000 + 100000 + MARGIN_GAP_SP - 1,
    )

    _margin_proof_assert_rejected(margin_contract.validate_stable_layout, layout)


def test_margin_proof_stable_geometry_rejects_tangent_notes() -> None:
    layout = _margin_proof_fixture("margin-stable-layout.valid.json")
    _margin_proof_place_both_notes_on_first_page(layout, second_y_sp=300000)

    _margin_proof_assert_rejected(margin_contract.validate_stable_layout, layout)


def test_margin_proof_stable_geometry_keeps_the_valid_fixture_green() -> None:
    layout = _margin_proof_fixture("margin-stable-layout.valid.json")

    assert margin_contract.validate_stable_layout(layout) == layout


@pytest.mark.parametrize("state", ["collecting", "changed"])
def test_margin_proof_nonstable_unplaced_notes_need_no_final_geometry(
    state: str,
) -> None:
    layout = _margin_proof_fixture("margin-layout.valid.json")
    layout["state"] = state
    if state == "collecting":
        layout["pass_number"] = 1
        layout["read_digest"] = None
    else:
        layout["computed_digest"] = "sha256:" + "f" * 64
    for note in layout["notes"]:
        note["target_shipout_index"] = None
        note["target_y_sp"] = None
        note["report_decoration_height_sp"] = 0
        note["effective_height_sp"] = note["base_height_sp"]
        note["report_depth"] = 0
    for page in layout["pages"]:
        page["carry_in_note_ids"] = []
        page["placed_note_ids"] = []
        page["reported_note_ids"] = []

    assert margin_contract.validate_margin_layout(layout) == layout


def test_margin_proof_layout_enforces_state_digest_transitions() -> None:
    stable = _margin_proof_fixture("margin-layout.valid.json")

    changed_with_equal_digests = deepcopy(stable)
    changed_with_equal_digests["state"] = "changed"
    _margin_proof_assert_rejected(
        margin_contract.validate_margin_layout, changed_with_equal_digests
    )

    stable_with_different_digests = deepcopy(stable)
    stable_with_different_digests["computed_digest"] = "sha256:" + "f" * 64
    _margin_proof_assert_rejected(
        margin_contract.validate_margin_layout, stable_with_different_digests
    )

    collecting_with_read_digest = deepcopy(stable)
    collecting_with_read_digest["state"] = "collecting"
    collecting_with_read_digest["pass_number"] = 1
    _margin_proof_assert_rejected(
        margin_contract.validate_margin_layout, collecting_with_read_digest
    )

    failed_with_unknown_code = deepcopy(stable)
    failed_with_unknown_code["state"] = "failed"
    failed_with_unknown_code["error_code"] = "anything-goes"
    _margin_proof_assert_rejected(
        margin_contract.validate_margin_layout, failed_with_unknown_code
    )

    pass_zero = deepcopy(stable)
    pass_zero["pass_number"] = 0
    _margin_proof_assert_rejected(margin_contract.validate_margin_layout, pass_zero)


@pytest.mark.parametrize("state", ["collecting", "changed", "stable", "failed"])
def test_margin_proof_layout_accepts_each_closed_state(state: str) -> None:
    envelope = _margin_proof_fixture("margin-layout.valid.json")
    envelope["state"] = state
    if state == "collecting":
        envelope["pass_number"] = 1
        envelope["read_digest"] = None
    elif state == "changed":
        envelope["computed_digest"] = "sha256:" + "f" * 64
    elif state == "failed":
        envelope["error_code"] = "margin-layout-oscillation"

    assert margin_contract.validate_margin_layout(envelope) == envelope


def test_margin_proof_ledger_rejects_duplicate_ids_orders_and_xrefs() -> None:
    original = _margin_proof_fixture("margin-ledger.valid.json")

    duplicate_id = deepcopy(original)
    duplicate_id["notes"][1]["note_id"] = duplicate_id["notes"][0]["note_id"]
    _margin_proof_assert_rejected(margin_contract.validate_margin_ledger, duplicate_id)

    duplicate_order = deepcopy(original)
    duplicate_order["notes"][1]["global_order"] = duplicate_order["notes"][0][
        "global_order"
    ]
    _margin_proof_assert_rejected(
        margin_contract.validate_margin_ledger, duplicate_order
    )

    duplicate_xref = deepcopy(original)
    duplicate_xref["notes"][1]["form_xref"] = duplicate_xref["notes"][0]["form_xref"]
    _margin_proof_assert_rejected(
        margin_contract.validate_margin_ledger, duplicate_xref
    )


def test_margin_proof_ledger_rejects_cross_role_folio_conflicts() -> None:
    ledger = _margin_proof_fixture("margin-ledger.valid.json")
    ledger["notes"][0]["target_folio"] = "WRONG"

    _margin_proof_assert_rejected(margin_contract.validate_margin_ledger, ledger)


@pytest.mark.parametrize(
    "requires_marker,anchor_count,note_count",
    [
        (False, 1, 1),
        (True, 0, 1),
        (False, 0, 0),
        (True, 1, 2),
    ],
)
def test_margin_proof_ledger_enforces_marker_and_note_cardinality(
    requires_marker: bool, anchor_count: int, note_count: int
) -> None:
    ledger = _margin_proof_fixture("margin-ledger.valid.json")
    ledger_note = ledger["notes"][0]
    ledger_note["requires_marker"] = requires_marker
    ledger_note["anchor_count"] = anchor_count
    ledger_note["note_count"] = note_count
    _margin_proof_assert_rejected(margin_contract.validate_margin_ledger, ledger)


def test_margin_proof_materializes_only_a_valid_stable_envelope() -> None:
    envelope = _margin_proof_fixture("margin-layout.valid.json")
    expected = _margin_proof_fixture("margin-stable-layout.valid.json")

    stable = margin_contract.materialize_stable_layout(envelope)

    assert stable == expected
    assert margin_contract.validate_stable_layout(stable) == stable
    assert set(stable) == {
        "schema_version",
        "variant",
        "geometry_digest",
        "semantic_digest",
        "max_passes",
        "notes",
        "pages",
    }

    non_stable = deepcopy(envelope)
    non_stable["state"] = "changed"
    non_stable["computed_digest"] = "sha256:" + "f" * 64
    with pytest.raises(margin_contract.MarginContractError):
        margin_contract.materialize_stable_layout(non_stable)


def test_margin_proof_projection_and_stable_layout_ignore_pass_metadata() -> None:
    first = _margin_proof_fixture("margin-layout.valid.json")
    second = deepcopy(first)
    second["run_nonce"] = "fedcba9876543210fedcba9876543210"
    second["pass_number"] = first["pass_number"] + 1

    first_projection = margin_contract.canonical_capture_projection(first)
    second_projection = margin_contract.canonical_capture_projection(second)
    first_stable = margin_contract.materialize_stable_layout(first)
    second_stable = margin_contract.materialize_stable_layout(second)

    assert first_projection == second_projection
    assert first_projection == margin_contract.canonical_capture_projection(
        first_stable
    )
    assert second_projection == margin_contract.canonical_capture_projection(
        second_stable
    )
    assert margin_contract.canonical_json_bytes(
        first_projection
    ) == margin_contract.canonical_json_bytes(second_projection)
    assert margin_contract.canonical_digest(
        first_projection
    ) == margin_contract.canonical_digest(second_projection)
    assert first_stable == second_stable
    assert margin_contract.canonical_json_bytes(
        first_stable
    ) == margin_contract.canonical_json_bytes(second_stable)


def test_margin_proof_projection_preserves_validated_note_order() -> None:
    layout = _margin_proof_fixture("margin-stable-layout.valid.json")

    projection = margin_contract.canonical_capture_projection(layout)

    assert [note["id"] for note in projection["notes"]] == [
        note["id"] for note in layout["notes"]
    ]
    assert set(projection) == {
        "schema_version",
        "variant",
        "geometry_digest",
        "semantic_digest",
        "notes",
    }
    assert set(projection["notes"][0]) == {
        "id",
        "role",
        "global_order",
        "origin_shipout_index",
        "origin_folio",
        "origin_y_sp",
        "width_sp",
        "base_height_sp",
        "report_decoration_height_sp",
        "effective_height_sp",
        "semantic_digest",
    }


def test_margin_proof_canonical_serialization_is_compact_sorted_utf8() -> None:
    first = {"z": "\N{LATIN SMALL LETTER E WITH ACUTE}", "a": [2, 1]}
    second = {"a": [2, 1], "z": "\N{LATIN SMALL LETTER E WITH ACUTE}"}

    assert margin_contract.canonical_json_bytes(first) == (
        b'{"a":[2,1],"z":"\xc3\xa9"}'
    )
    assert margin_contract.canonical_json_bytes(first) == (
        margin_contract.canonical_json_bytes(second)
    )
    assert margin_contract.canonical_digest(first) == (
        "sha256:" "9e5bce4df644abba8f41fa80ec66c7e1439ebbd4fd0f559148e3af9dc9afe9ef"
    )
