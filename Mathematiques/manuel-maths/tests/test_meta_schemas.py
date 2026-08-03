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


def test_margin_proof_private_envelope_requires_a_lowercase_32_hex_nonce() -> None:
    for bad_nonce in ("short", "A" * 32, "g" * 32, "0" * 33):
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


def test_margin_proof_projection_sorts_notes_and_omits_volatile_fields() -> None:
    layout = _margin_proof_fixture("margin-stable-layout.valid.json")
    layout["notes"].reverse()

    projection = margin_contract.canonical_capture_projection(layout)

    assert [note["global_order"] for note in projection["notes"]] == [1, 2]
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
