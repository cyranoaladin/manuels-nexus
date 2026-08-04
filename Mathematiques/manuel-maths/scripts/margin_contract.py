"""Validate and canonically serialize margin-compositor proof artefacts."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

SCHEMA_ROOT = Path(__file__).resolve().parents[1] / "schemas"
MARGIN_GAP_SP = 6 * 65536


class MarginContractError(ValueError):
    """A margin proof does not satisfy its closed data contract."""


def _load_schema(name: str) -> dict[str, Any]:
    schema = json.loads((SCHEMA_ROOT / name).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


def _schema_validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(_load_schema(name))


def _json_path(parts: list[Any]) -> str:
    return "$" + "".join(
        f"[{part}]" if isinstance(part, int) else f".{part}" for part in parts
    )


def _validate_schema(document: Any, schema_name: str) -> dict[str, Any]:
    errors = sorted(
        _schema_validator(schema_name).iter_errors(document),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        first = errors[0]
        path = _json_path(list(first.absolute_path))
        raise MarginContractError(f"{schema_name}: {path}: {first.message}")
    if not isinstance(document, dict):  # Defensive; the root schema already checks it.
        raise MarginContractError(f"{schema_name}: root must be an object")
    return document


def _reject(message: str) -> None:
    raise MarginContractError(message)


def _require_unique(values: list[Any], label: str) -> None:
    if len(values) != len(set(values)):
        _reject(f"duplicate {label}")


def _require_canonical_order(keys: list[tuple[Any, ...]], label: str) -> None:
    if any(current >= following for current, following in zip(keys, keys[1:])):
        _reject(f"noncanonical {label} order")


def _validate_rect(rect: dict[str, Any], page: dict[str, Any], label: str) -> None:
    left = rect["left_sp"]
    top = rect["top_sp"]
    right = rect["right_sp"]
    bottom = rect["bottom_sp"]
    if not left < right or not top < bottom:
        _reject(f"{label} must have positive width and height")
    if right > page["page_width_sp"] or bottom > page["page_height_sp"]:
        _reject(f"{label} lies outside its page")


def _expected_page_memberships(
    note: dict[str, Any],
) -> tuple[set[int], set[int], set[int], set[int]]:
    origin = note["origin_shipout_index"]
    target = note["target_shipout_index"]
    native = {origin}
    carry: set[int] = set()
    placed: set[int] = set()
    reported: set[int] = set()
    if target is None:
        return native, carry, placed, reported

    if target < origin:
        _reject(f"note {note['id']} targets a page before its origin")
    expected_depth = target - origin
    if note["report_depth"] != expected_depth:
        _reject(f"note {note['id']} has an incoherent report_depth")

    placed.add(target)
    if expected_depth:
        carry.update(range(origin + 1, target + 1))
        reported.update(range(origin, target))
    return native, carry, placed, reported


def _rectangles_intersect_with_positive_area(
    first: tuple[int, int, int, int],
    second: tuple[int, int, int, int],
) -> bool:
    first_left, first_top, first_right, first_bottom = first
    second_left, second_top, second_right, second_bottom = second
    return max(first_left, second_left) < min(first_right, second_right) and max(
        first_top, second_top
    ) < min(first_bottom, second_bottom)


def _validate_stable_placed_geometry(
    pages: list[dict[str, Any]], notes_by_id: dict[str, dict[str, Any]]
) -> None:
    for page in pages:
        page_index = page["shipout_index"]
        safe_rect = page["safe_rect"]
        placed_rectangles: list[tuple[str, tuple[int, int, int, int]]] = []
        obstacle_rectangles = [
            (
                obstacle["id"],
                (
                    obstacle["left_sp"],
                    obstacle["top_sp"],
                    obstacle["right_sp"],
                    obstacle["bottom_sp"],
                ),
            )
            for obstacle in page["obstacles"]
        ]

        for note_id in page["placed_note_ids"]:
            note = notes_by_id[note_id]
            target_y = note["target_y_sp"]
            if note["target_shipout_index"] != page_index or target_y is None:
                _reject(f"placed note {note_id} does not target page {page_index}")
            rectangle = (
                safe_rect["left_sp"],
                target_y,
                safe_rect["left_sp"] + note["width_sp"],
                target_y + note["effective_height_sp"],
            )
            for obstacle_id, obstacle_rectangle in obstacle_rectangles:
                if _rectangles_intersect_with_positive_area(
                    rectangle, obstacle_rectangle
                ):
                    _reject(f"placed note {note_id} intersects obstacle {obstacle_id}")
            for other_note_id, other_rectangle in placed_rectangles:
                if _rectangles_intersect_with_positive_area(rectangle, other_rectangle):
                    _reject(f"placed notes {other_note_id} and {note_id} intersect")
            if placed_rectangles:
                previous_note_id, previous_rectangle = placed_rectangles[-1]
                vertical_gap = rectangle[1] - previous_rectangle[3]
                if vertical_gap < MARGIN_GAP_SP:
                    _reject(
                        f"placed notes {previous_note_id} and {note_id} "
                        "have less than 6pt vertical gap"
                    )
            placed_rectangles.append((note_id, rectangle))


def _validate_layout_semantics(
    document: dict[str, Any], *, require_complete: bool
) -> None:
    # Canonical arrays are fail-closed: pages by shipout index; notes by
    # (global_order, id); obstacles by geometry then id; native IDs by origin
    # y/order/id; carry/report IDs by order/id; placed IDs by target y/order/id.
    notes = document["notes"]
    pages = document["pages"]

    _require_unique([note["id"] for note in notes], "note id")
    _require_unique([note["global_order"] for note in notes], "global_order")
    _require_canonical_order(
        [(note["global_order"], note["id"]) for note in notes],
        "notes",
    )
    page_indexes = [page["shipout_index"] for page in pages]
    _require_unique(page_indexes, "shipout_index")
    if page_indexes != list(range(1, len(pages) + 1)):
        _reject("pages must be ordered and contiguous from shipout_index 1")

    obstacle_ids = [obstacle["id"] for page in pages for obstacle in page["obstacles"]]
    _require_unique(obstacle_ids, "obstacle id")

    notes_by_id = {note["id"]: note for note in notes}
    pages_by_index = {page["shipout_index"]: page for page in pages}
    memberships: dict[str, dict[str, set[int]]] = {
        field: {note_id: set() for note_id in notes_by_id}
        for field in (
            "native_note_ids",
            "carry_in_note_ids",
            "placed_note_ids",
            "reported_note_ids",
        )
    }

    for page in pages:
        safe_rect = page["safe_rect"]
        _validate_rect(safe_rect, page, f"page {page['shipout_index']} safe_rect")
        expected_side = "right" if page["shipout_index"] % 2 else "left"
        if page["rail_side"] != expected_side:
            _reject(f"page {page['shipout_index']} has an incoherent rail_side")
        for obstacle in page["obstacles"]:
            _validate_rect(
                obstacle,
                page,
                f"obstacle {obstacle['id']}",
            )
        _require_canonical_order(
            [
                (
                    obstacle["top_sp"],
                    obstacle["bottom_sp"],
                    obstacle["left_sp"],
                    obstacle["right_sp"],
                    obstacle["id"],
                )
                for obstacle in page["obstacles"]
            ],
            f"page {page['shipout_index']} obstacles",
        )
        for field in memberships:
            for note_id in page[field]:
                if note_id not in notes_by_id:
                    _reject(
                        f"page {page['shipout_index']} {field} references "
                        f"unknown note {note_id}"
                    )
                memberships[field][note_id].add(page["shipout_index"])

        _require_canonical_order(
            [
                (
                    notes_by_id[note_id]["origin_y_sp"],
                    notes_by_id[note_id]["global_order"],
                    note_id,
                )
                for note_id in page["native_note_ids"]
            ],
            f"page {page['shipout_index']} native_note_ids",
        )
        for field in ("carry_in_note_ids", "reported_note_ids"):
            _require_canonical_order(
                [
                    (notes_by_id[note_id]["global_order"], note_id)
                    for note_id in page[field]
                ],
                f"page {page['shipout_index']} {field}",
            )
        placed_keys: list[tuple[Any, ...]] = []
        for note_id in page["placed_note_ids"]:
            target_y = notes_by_id[note_id]["target_y_sp"]
            if target_y is None:
                _reject(f"placed note {note_id} has no target_y_sp")
            placed_keys.append(
                (target_y, notes_by_id[note_id]["global_order"], note_id)
            )
        _require_canonical_order(
            placed_keys,
            f"page {page['shipout_index']} placed_note_ids",
        )

    for note in notes:
        note_id = note["id"]
        origin_index = note["origin_shipout_index"]
        target_index = note["target_shipout_index"]
        target_y = note["target_y_sp"]
        if origin_index not in pages_by_index:
            _reject(f"note {note_id} references an unknown origin page")
        origin_page = pages_by_index[origin_index]
        if note["origin_folio"] != origin_page["folio"]:
            _reject(f"note {note_id} origin folio does not match its page")
        if note["origin_y_sp"] > origin_page["page_height_sp"]:
            _reject(f"note {note_id} origin lies outside its page")
        if (target_index is None) != (target_y is None):
            _reject(f"note {note_id} has a half-null target")
        if target_index is not None and target_index not in pages_by_index:
            _reject(f"note {note_id} references an unknown target page")
        if require_complete and target_index is None:
            _reject(f"stable note {note_id} has no target")
        expected_effective_height = note["base_height_sp"]
        if note["report_depth"] > 0:
            expected_effective_height += note["report_decoration_height_sp"]
        if note["effective_height_sp"] != expected_effective_height:
            _reject(f"note {note_id} has an incoherent effective height")
        if note["report_depth"] > 0:
            if note["report_decoration_height_sp"] <= 0:
                _reject(f"reported note {note_id} lacks report decoration")
            if not note["requires_marker"]:
                _reject(f"reported note {note_id} lacks its marker")

        if target_index is not None:
            target_page = pages_by_index[target_index]
            safe_rect = target_page["safe_rect"]
            if target_y < safe_rect["top_sp"]:
                _reject(f"note {note_id} starts above the target safe rectangle")
            if target_y + note["effective_height_sp"] > safe_rect["bottom_sp"]:
                _reject(f"note {note_id} ends below the target safe rectangle")
            if note["width_sp"] > safe_rect["right_sp"] - safe_rect["left_sp"]:
                _reject(f"note {note_id} is wider than the target safe rectangle")

        native, carry, placed, reported = _expected_page_memberships(note)
        expected = {
            "native_note_ids": native,
            "carry_in_note_ids": carry,
            "placed_note_ids": placed,
            "reported_note_ids": reported,
        }
        for field, expected_pages in expected.items():
            if memberships[field][note_id] != expected_pages:
                _reject(f"note {note_id} has incoherent {field}")

    if require_complete:
        _validate_stable_placed_geometry(pages, notes_by_id)


def validate_margin_layout(document: Any) -> dict[str, Any]:
    """Validate a volatile, run-private layout envelope."""

    layout = _validate_schema(document, "margin-layout.schema.json")
    state = layout["state"]
    if state == "changed" and layout["read_digest"] == layout["computed_digest"]:
        _reject("changed layout must have different read and computed digests")
    if state == "stable" and layout["read_digest"] != layout["computed_digest"]:
        _reject("stable layout must have equal read and computed digests")
    _validate_layout_semantics(layout, require_complete=state == "stable")
    return layout


def validate_stable_layout(document: Any) -> dict[str, Any]:
    """Validate a nonce-free stable layout payload."""

    layout = _validate_schema(document, "margin-stable-layout.schema.json")
    _validate_layout_semantics(layout, require_complete=True)
    return layout


def validate_margin_ledger(document: Any) -> dict[str, Any]:
    """Validate a canonical ledger reconstructed from a produced PDF."""

    ledger = _validate_schema(document, "margin-ledger.schema.json")
    notes = ledger["notes"]
    _require_unique([note["note_id"] for note in notes], "ledger note id")
    _require_unique([note["global_order"] for note in notes], "ledger global_order")
    _require_unique([note["form_xref"] for note in notes], "ledger form_xref")
    _require_canonical_order(
        [(note["global_order"], note["note_id"]) for note in notes],
        "ledger notes",
    )

    folio_by_shipout_index: dict[int, str] = {}
    for note in notes:
        note_id = note["note_id"]
        left, top, right, bottom = note["bbox_sp"]
        if not left < right or not top < bottom:
            _reject(f"ledger note {note_id} has an incoherent bbox_sp")
        if note["note_count"] != 1:
            _reject(f"ledger note {note_id} must occur exactly once")
        expected_anchors = 1 if note["requires_marker"] else 0
        if note["anchor_count"] != expected_anchors:
            _reject(f"ledger note {note_id} has an incoherent anchor count")
        if note["target_shipout_index"] < note["origin_shipout_index"]:
            _reject(f"ledger note {note_id} targets a page before its origin")
        if note["report_depth"] != (
            note["target_shipout_index"] - note["origin_shipout_index"]
        ):
            _reject(f"ledger note {note_id} has an incoherent report_depth")
        if note["report_depth"] > 0 and not note["requires_marker"]:
            _reject(f"reported ledger note {note_id} lacks its marker")

        for index_field, folio_field, label in (
            (
                "origin_shipout_index",
                "origin_folio",
                "origin",
            ),
            (
                "target_shipout_index",
                "target_folio",
                "target",
            ),
        ):
            index = note[index_field]
            folio = note[folio_field]
            if (
                index in folio_by_shipout_index
                and folio_by_shipout_index[index] != folio
            ):
                _reject(f"ledger has inconsistent {label} folios for page {index}")
            folio_by_shipout_index[index] = folio
    return ledger


def materialize_stable_layout(envelope: Any) -> dict[str, Any]:
    """Strip volatile pass metadata from a validated stable envelope."""

    validated = validate_margin_layout(envelope)
    if validated["state"] != "stable":
        _reject("only a stable layout envelope can be materialized")
    stable = {
        key: deepcopy(validated[key])
        for key in (
            "schema_version",
            "variant",
            "geometry_digest",
            "semantic_digest",
            "max_passes",
            "notes",
            "pages",
        )
    }
    return validate_stable_layout(stable)


def canonical_capture_projection(layout: Any) -> dict[str, Any]:
    """Return the nonce-free, placement-free capture identity of a layout."""

    validator: Callable[[Any], dict[str, Any]]
    if isinstance(layout, dict) and "run_nonce" in layout:
        validator = validate_margin_layout
    else:
        validator = validate_stable_layout
    validated = validator(layout)
    capture_fields = (
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
    )
    notes = [
        {key: deepcopy(note[key]) for key in capture_fields}
        for note in validated["notes"]
    ]
    return {
        "schema_version": validated["schema_version"],
        "variant": validated["variant"],
        "geometry_digest": validated["geometry_digest"],
        "semantic_digest": validated["semantic_digest"],
        "notes": notes,
    }


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize JSON deterministically as compact, sorted UTF-8 bytes."""

    try:
        text = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    except (TypeError, ValueError) as exc:
        raise MarginContractError(f"value is not canonical JSON: {exc}") from exc
    return text.encode("utf-8")


def canonical_digest(value: Any) -> str:
    """Return the prefixed SHA-256 of canonical JSON bytes."""

    return "sha256:" + hashlib.sha256(canonical_json_bytes(value)).hexdigest()
