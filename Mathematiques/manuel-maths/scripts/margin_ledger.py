#!/usr/bin/env python3
"""Reconstruct the canonical margin ledger from rendered PDF evidence."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import asdict, dataclass
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable, Mapping, Sequence

import pikepdf


SCRIPT_DIRECTORY = Path(__file__).resolve().parent
CONTROL_ID_PATTERN = re.compile(r"\bnxm:[^\s]+")
STUDENT_INTERNAL_ID_PATTERN = re.compile(r"\b1SPE-[A-Z0-9][A-Z0-9-]*\b")
KNOWN_MARGIN_TAGS = {"NXMarginNote", "NXMarginAnchor"}
NOTE_PROPERTY_KEYS = {
    "/BBoxSP",
    "/ID",
    "/Order",
    "/OriginFolio",
    "/OriginPage",
    "/ReportDepth",
    "/RequiresMarker",
    "/Role",
    "/TargetFolio",
    "/TargetPage",
}
BP_TO_SP = 72.27 * 65536 / 72
SP_TO_BP_EXACT = Fraction(7200, 7227 * 65536)
BP_TO_SP_EXACT = 1 / SP_TO_BP_EXACT
FORM_BBOX_ROUNDING_TOLERANCE_SP = 32
MARGIN_GEOMETRY_TOLERANCE_SP = 1
MARGIN_GAP_SP = 6 * 65536
LINK_RECT_TOLERANCE_BP = 0.002
COMMAND_TIMEOUT_SECONDS = 20


class MarginLedgerError(ValueError):
    """Raised when PDF evidence does not satisfy the frozen margin contract."""


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


@dataclass(frozen=True)
class MarginVerificationResult:
    """Closed, machine-consumable result of the composed margin gate."""

    passed: bool
    variant: str
    page_count: int
    note_count: int
    qpdf_checked: bool
    poppler_checked: bool
    capture_inventory_digest: str
    stable_layout_digest: str
    ledger_digest: str


def _load_margin_contract() -> ModuleType:
    module_name = "margin_contract_for_margin_ledger"
    if module_name in sys.modules:
        return sys.modules[module_name]
    path = SCRIPT_DIRECTORY / "margin_contract.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise MarginLedgerError(f"cannot load margin contract: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _reject(message: str) -> None:
    raise MarginLedgerError(message)


def _load_document(value: Mapping[str, Any] | str | Path, label: str) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    path = Path(value)
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MarginLedgerError(f"cannot read {label}: {exc}") from exc
    if not isinstance(document, dict):
        _reject(f"{label} root must be an object")
    return document


def _validate_inputs(
    capture_inventory: Mapping[str, Any] | str | Path,
    stable_layout: Mapping[str, Any] | str | Path,
) -> tuple[dict[str, Any], dict[str, Any], ModuleType]:
    contract = _load_margin_contract()
    capture = _load_document(capture_inventory, "capture inventory")
    stable = _load_document(stable_layout, "stable layout")
    try:
        contract.validate_margin_layout(capture)
        contract.validate_stable_layout(stable)
    except contract.MarginContractError as exc:
        raise MarginLedgerError(f"invalid margin evidence: {exc}") from exc
    if capture["state"] != "stable" or capture["read_digest"] != capture["computed_digest"]:
        _reject("PDF evidence is retainable only from a stable equal-digest pass")
    capture_projection = contract.canonical_capture_projection(capture)
    stable_projection = contract.canonical_capture_projection(stable)
    if contract.canonical_json_bytes(capture_projection) != contract.canonical_json_bytes(
        stable_projection
    ):
        _reject("capture inventory and stable layout projections differ")
    if capture["variant"] != stable["variant"]:
        _reject("capture inventory and stable layout variants differ")
    return capture, stable, contract


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _pdf_name(value: Any) -> str:
    return str(value).removeprefix("/")


def _pdf_exact_string(value: Any, label: str) -> str:
    if not isinstance(value, pikepdf.String):
        _reject(f"{label} must be one PDF string")
    rendered = str(value)
    if not rendered:
        _reject(f"empty {label}")
    return rendered


def _pdf_exact_integer(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        _reject(f"{label} must be one PDF integer")
    return value


def _pdf_boolean(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        _reject(f"{label} must be a boolean")
    return value


def _bbox_sp(value: Any, label: str) -> tuple[int, int, int, int]:
    if not isinstance(value, (list, pikepdf.Array)) or len(value) != 4:
        _reject(f"{label} must contain four coordinates")
    coordinates = tuple(
        _pdf_exact_integer(coordinate, f"{label}[{index}]")
        for index, coordinate in enumerate(value)
    )
    left, top, right, bottom = coordinates
    if left >= right or top >= bottom:
        _reject(f"{label} must have positive width and height")
    return coordinates


def _form_bbox(form: Any, note_id: str) -> tuple[float, float, float, float]:
    bbox = form.get("/BBox")
    if not isinstance(bbox, pikepdf.Array) or len(bbox) != 4:
        _reject(f"Form for {note_id} has no four-coordinate /BBox")
    try:
        values = tuple(float(coordinate) for coordinate in bbox)
    except (TypeError, ValueError, OverflowError) as exc:
        raise MarginLedgerError(f"Form for {note_id} has a nonnumeric /BBox") from exc
    if values[0] >= values[2] or values[1] >= values[3]:
        _reject(f"Form for {note_id} has an invalid /BBox")
    return values


def _check_form_bbox_dimensions(
    bbox: tuple[float, float, float, float],
    stable_note: Mapping[str, Any],
) -> None:
    note_id = stable_note["id"]
    expected_sp = (0, 0, stable_note["width_sp"], stable_note["effective_height_sp"])
    actual_sp = tuple(round(coordinate * BP_TO_SP) for coordinate in bbox)
    if any(
        abs(actual - expected) > FORM_BBOX_ROUNDING_TOLERANCE_SP
        for actual, expected in zip(actual_sp, expected_sp, strict=True)
    ):
        _reject(f"Form /BBox coordinate frame differs from stable note {note_id}")


def _check_form_matrix(form: Any, note_id: str) -> None:
    matrix = form.get("/Matrix")
    if matrix is None:
        return
    if not isinstance(matrix, pikepdf.Array) or len(matrix) != 6:
        _reject(f"Form /Matrix for {note_id} must contain six numbers")
    values: list[float] = []
    for value in matrix:
        if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
            _reject(f"Form /Matrix for {note_id} must contain only PDF numbers")
        numeric = float(value)
        if not math.isfinite(numeric):
            _reject(f"Form /Matrix for {note_id} must contain finite numbers")
        values.append(numeric)
    if tuple(values) != (1.0, 0.0, 0.0, 1.0, 0.0, 0.0):
        _reject(f"Form /Matrix for {note_id} must be the identity transform")


def _expected_bbox(note: Mapping[str, Any], pages: Mapping[int, Mapping[str, Any]]) -> tuple[int, int, int, int]:
    target_index = note["target_shipout_index"]
    page = pages.get(target_index)
    if page is None:
        _reject(f"stable note {note['id']} targets an unknown page")
    left = page["safe_rect"]["left_sp"]
    top = note["target_y_sp"]
    return left, top, left + note["width_sp"], top + note["effective_height_sp"]


def _validate_link_inventory(
    value: Mapping[str, Any] | str | Path,
    capture: Mapping[str, Any],
) -> dict[str, Any]:
    document = _load_document(value, "private link inventory")
    if set(document) != {
        "schema_version",
        "variant",
        "run_nonce",
        "pass_number",
        "notes",
    }:
        _reject("private link inventory has unexpected or missing root fields")
    if (
        isinstance(document["schema_version"], bool)
        or not isinstance(document["schema_version"], int)
        or document["schema_version"] != 1
    ):
        _reject("private link inventory has an unsupported schema version")
    for key in ("variant", "run_nonce"):
        if not isinstance(document[key], str) or document[key] != capture[key]:
            _reject(f"private link inventory has an incoherent {key}")
    if (
        isinstance(document["pass_number"], bool)
        or not isinstance(document["pass_number"], int)
        or document["pass_number"] != capture["pass_number"]
    ):
        _reject("private link inventory has an incoherent pass_number")
    notes = document["notes"]
    if not isinstance(notes, list) or len(notes) != len(capture["notes"]):
        _reject("private link inventory note count differs from capture")
    for record, captured in zip(notes, capture["notes"], strict=True):
        if not isinstance(record, dict) or set(record) != {
            "note_id",
            "global_order",
            "marker_threshold_sp",
            "links",
        }:
            _reject("private link inventory note has an invalid structure")
        if not isinstance(record["note_id"], str) or record["note_id"] != captured["id"]:
            _reject("private link inventory note ID differs from capture")
        if (
            isinstance(record["global_order"], bool)
            or not isinstance(record["global_order"], int)
            or record["global_order"] != captured["global_order"]
        ):
            _reject("private link inventory order differs from capture")
        if (
            isinstance(record["marker_threshold_sp"], bool)
            or not isinstance(record["marker_threshold_sp"], int)
            or record["marker_threshold_sp"] < 1
        ):
            _reject("private link inventory marker threshold is invalid")
        links = record["links"]
        if not isinstance(links, list):
            _reject("private link inventory links must be an array")
        for link in links:
            if not isinstance(link, dict) or set(link) != {"rect_sp", "action"}:
                _reject("private link inventory entry has an invalid structure")
            rect = link["rect_sp"]
            if (
                not isinstance(rect, list)
                or len(rect) != 4
                or any(isinstance(item, bool) or not isinstance(item, int) for item in rect)
                or rect[0] >= rect[2]
                or rect[1] >= rect[3]
            ):
                _reject("private link inventory rectangle is invalid")
            action = link["action"]
            if not isinstance(action, dict) or set(action) != {"kind", "target"}:
                _reject("private link inventory action has an invalid structure")
            if not isinstance(action["kind"], str) or action["kind"] not in {
                "URI",
                "GoTo",
            }:
                _reject("private link inventory action kind is unsupported")
            if not isinstance(action["target"], str) or not action["target"]:
                _reject("private link inventory action target is invalid")
    return document


def _annotation_rect(annotation: Any) -> tuple[float, float, float, float]:
    rect = annotation.get("/Rect")
    if not isinstance(rect, pikepdf.Array) or len(rect) != 4:
        _reject("link annotation has no four-coordinate /Rect")
    if any(
        isinstance(value, bool) or not isinstance(value, (int, float, Decimal))
        for value in rect
    ):
        _reject("link annotation /Rect must contain only PDF numbers")
    values = tuple(float(value) for value in rect)
    if not all(math.isfinite(value) for value in values):
        _reject("link annotation /Rect must contain finite numbers")
    if values[0] >= values[2] or values[1] >= values[3]:
        _reject("link annotation has an invalid /Rect")
    return values


def _annotation_dictionary_is_exact(annotation: Any, action_kind: str) -> bool:
    expected_keys = {"/Type", "/Subtype", "/Rect", "/A"}
    if action_kind == "GoTo":
        expected_keys.add("/Border")
    if {str(key) for key in annotation.keys()} != expected_keys:
        return False
    annotation_type = annotation.get("/Type")
    subtype = annotation.get("/Subtype")
    if (
        not isinstance(annotation_type, pikepdf.Name)
        or str(annotation_type) != "/Annot"
        or not isinstance(subtype, pikepdf.Name)
        or str(subtype) != "/Link"
    ):
        return False
    if action_kind == "GoTo":
        border = annotation.get("/Border")
        if not isinstance(border, pikepdf.Array) or len(border) != 3:
            return False
        if any(isinstance(value, bool) or not isinstance(value, int) for value in border):
            return False
        if tuple(border) != (0, 0, 0):
            return False
    return True


def _annotation_action(annotation: Any) -> tuple[str, str] | None:
    action = annotation.get("/A")
    if not isinstance(action, pikepdf.Dictionary):
        return None
    raw_kind = action.get("/S")
    if not isinstance(raw_kind, pikepdf.Name):
        return None
    action_kind = str(raw_kind).removeprefix("/")
    action_keys = {str(key) for key in action.keys()}
    if action_kind == "URI":
        if not _annotation_dictionary_is_exact(annotation, action_kind):
            return None
        if action_keys != {"/Type", "/S", "/URI"}:
            return None
        if not isinstance(action.get("/Type"), pikepdf.Name) or str(
            action["/Type"]
        ) != "/Action":
            return None
        target = action.get("/URI")
        return ("URI", str(target)) if isinstance(target, pikepdf.String) else None
    if action_kind == "GoTo":
        if not _annotation_dictionary_is_exact(annotation, action_kind):
            return None
        if action_keys != {"/S", "/D"}:
            return None
        target = action.get("/D")
        return ("GoTo", str(target)) if isinstance(target, pikepdf.String) else None
    return None


def _expected_link_records(
    inventory: Mapping[str, Any],
    stable_notes: Mapping[str, Mapping[str, Any]],
    pages: Mapping[int, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    expected: list[dict[str, Any]] = []
    for note_record in inventory["notes"]:
        note = stable_notes[note_record["note_id"]]
        page = pages[note["target_shipout_index"]]
        decoration_sp = (
            note["report_decoration_height_sp"] if note["report_depth"] > 0 else 0
        )
        for link in note_record["links"]:
            left, top, right, bottom = link["rect_sp"]
            absolute_left = page["safe_rect"]["left_sp"] + left
            absolute_right = page["safe_rect"]["left_sp"] + right
            absolute_top = note["target_y_sp"] + decoration_sp + top
            absolute_bottom = note["target_y_sp"] + decoration_sp + bottom
            expected.append(
                {
                    "page": note["target_shipout_index"],
                    "rect": (
                        absolute_left / BP_TO_SP,
                        (page["page_height_sp"] - absolute_bottom) / BP_TO_SP,
                        absolute_right / BP_TO_SP,
                        (page["page_height_sp"] - absolute_top) / BP_TO_SP,
                    ),
                    "action": (link["action"]["kind"], link["action"]["target"]),
                }
            )
    return expected


def _check_expected_links(
    pdf: pikepdf.Pdf,
    inventory: Mapping[str, Any],
    stable_notes: Mapping[str, Mapping[str, Any]],
    pages: Mapping[int, Mapping[str, Any]],
) -> None:
    actual: list[dict[str, Any]] = []
    for page_index, page in enumerate(pdf.pages, start=1):
        annotations = page.obj.get("/Annots", [])
        if not isinstance(annotations, (list, pikepdf.Array)):
            _reject(f"page {page_index} /Annots must be an array")
        for annotation in annotations:
            if str(annotation.get("/Subtype", "")) != "/Link":
                continue
            actual.append(
                {
                    "page": page_index,
                    "rect": _annotation_rect(annotation),
                    "action": _annotation_action(annotation),
                }
            )
    used: set[int] = set()
    for expected in _expected_link_records(inventory, stable_notes, pages):
        matches = [
            index
            for index, candidate in enumerate(actual)
            if index not in used
            and candidate["page"] == expected["page"]
            and candidate["action"] == expected["action"]
            and all(
                abs(left - right) <= LINK_RECT_TOLERANCE_BP
                for left, right in zip(candidate["rect"], expected["rect"], strict=True)
            )
        ]
        if len(matches) != 1:
            _reject("captured marginal link action or rectangle did not survive exactly")
        used.add(matches[0])
    marginal_actual: set[int] = set(used)
    for index, candidate in enumerate(actual):
        page = pages.get(candidate["page"])
        if page is None:
            continue
        safe = page["safe_rect"]
        rail_rect = (
            safe["left_sp"] / BP_TO_SP,
            (page["page_height_sp"] - safe["bottom_sp"]) / BP_TO_SP,
            safe["right_sp"] / BP_TO_SP,
            (page["page_height_sp"] - safe["top_sp"]) / BP_TO_SP,
        )
        candidate_rect = candidate["rect"]
        intersects_rail = max(candidate_rect[0], rail_rect[0]) < min(
            candidate_rect[2], rail_rect[2]
        ) and max(candidate_rect[1], rail_rect[1]) < min(
            candidate_rect[3], rail_rect[3]
        )
        if intersects_rail:
            marginal_actual.add(index)
    if marginal_actual != used:
        _reject("page margin link inventory is not exhaustive")


def _annotation_signature(annotation: Any) -> tuple[str, ...]:
    rect = _annotation_rect(annotation)
    action = annotation.get("/A")
    return (
        *(str(value) for value in rect),
        str(action.get("/S", "")) if action else "",
        str(action.get("/URI", "")) if action else "",
        str(action.get("/D", "")) if action else str(annotation.get("/Dest", "")),
    )


def _check_link_duplicates(pdf: pikepdf.Pdf) -> None:
    for page_index, page in enumerate(pdf.pages, start=1):
        signatures: set[tuple[str, ...]] = set()
        for reference in page.obj.get("/Annots", []):
            annotation = reference
            if str(annotation.get("/Subtype", "")) != "/Link":
                continue
            signature = _annotation_signature(annotation)
            if signature in signatures:
                _reject(f"duplicate link annotation on page {page_index}")
            signatures.add(signature)


def _command_options(environment: Mapping[str, str] | None) -> dict[str, Any]:
    options: dict[str, Any] = {
        "capture_output": True,
        "text": True,
        "timeout": COMMAND_TIMEOUT_SECONDS,
        "check": False,
    }
    if environment is not None:
        options["env"] = dict(environment)
    return options


def _check_extracted_text(
    pdf_path: Path,
    variant: str,
    *,
    runner: Any = None,
    environment: Mapping[str, str] | None = None,
) -> None:
    active_runner = subprocess.run if runner is None else runner
    try:
        result = active_runner(
            ["pdftotext", str(pdf_path), "-"],
            **_command_options(environment),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise MarginLedgerError(f"cannot extract PDF text: {exc}") from exc
    if result.returncode != 0:
        _reject(f"pdftotext rejected PDF: {result.stderr.strip()}")
    if CONTROL_ID_PATTERN.search(result.stdout):
        _reject("a margin control ID is visible in extracted text")
    if variant == "eleve" and STUDENT_INTERNAL_ID_PATTERN.search(result.stdout):
        _reject("an internal 1SPE ID is visible in student extracted text")


def _text_operands(instructions: Iterable[Any]) -> Iterable[str]:
    for operands, operator in instructions:
        operation = str(operator)
        if operation in {"Tj", "'", '"'} and operands:
            yield str(operands[-1])
        elif operation == "TJ" and operands and isinstance(operands[0], pikepdf.Array):
            for item in operands[0]:
                if isinstance(item, pikepdf.String):
                    yield str(item)


def _check_pdf_text_operators(pdf: pikepdf.Pdf, variant: str) -> None:
    streams: list[Any] = [page for page in pdf.pages]
    seen_forms: set[int] = set()
    for page in pdf.pages:
        xobjects = page.obj.get("/Resources", {}).get("/XObject", {})
        for name in xobjects:
            form = xobjects[name]
            if str(form.get("/Subtype", "")) != "/Form":
                continue
            xref = form.objgen[0]
            if xref not in seen_forms:
                seen_forms.add(xref)
                streams.append(form)
    for stream in streams:
        try:
            instructions = pikepdf.parse_content_stream(stream)
        except pikepdf.PdfError as exc:
            raise MarginLedgerError(f"cannot parse PDF text operators: {exc}") from exc
        for text in _text_operands(instructions):
            if CONTROL_ID_PATTERN.search(text):
                _reject("a margin control ID is present in a PDF text operator")
            if variant == "eleve" and STUDENT_INTERNAL_ID_PATTERN.search(text):
                _reject("an internal 1SPE ID is present in a student PDF text operator")


def _check_pdf_page_sequence(pdf: pikepdf.Pdf, stable: Mapping[str, Any]) -> None:
    stable_pages = stable["pages"]
    if len(pdf.pages) != len(stable_pages):
        _reject("PDF page count differs from stable layout")
    pages_by_index: dict[int, Mapping[str, Any]] = {}
    for expected_index, page in enumerate(stable_pages, start=1):
        if page["shipout_index"] != expected_index:
            _reject("stable page shipout indices are not contiguous and ordered")
        if not isinstance(page["folio"], str) or not page["folio"]:
            _reject(f"stable page {expected_index} has an invalid folio")
        pages_by_index[expected_index] = page
    for note in stable["notes"]:
        origin = pages_by_index.get(note["origin_shipout_index"])
        target = pages_by_index.get(note["target_shipout_index"])
        if origin is None or target is None:
            _reject(f"stable note {note['id']} references a non-PDF page")
        if note["origin_folio"] != origin["folio"]:
            _reject(f"stable note {note['id']} origin folio differs from its page")


def _margin_forms(pdf: pikepdf.Pdf) -> dict[int, Any]:
    forms: dict[int, Any] = {}
    visited: set[int] = set()

    def visit_resources(resources: Any) -> None:
        if not isinstance(resources, pikepdf.Dictionary):
            _reject("PDF /Resources must be a dictionary")
        xobjects = resources.get("/XObject")
        if xobjects is None:
            return
        if not isinstance(xobjects, pikepdf.Dictionary):
            _reject("PDF /XObject resources must be a dictionary")
        for name in xobjects:
            candidate = xobjects[name]
            xref = candidate.objgen[0]
            if xref in visited:
                continue
            visited.add(xref)
            is_form = str(candidate.get("/Subtype", "")) == "/Form"
            if candidate.get("/NXMarginID") is not None:
                if not is_form or xref < 1:
                    _reject("an NXMarginID resource is not an indirect Form XObject")
                forms[xref] = candidate
            if is_form and candidate.get("/Resources") is not None:
                visit_resources(candidate["/Resources"])

    for page in pdf.pages:
        visit_resources(page.obj.get("/Resources"))
    return forms


def _check_form_margin_tags(forms: Mapping[int, Any]) -> None:
    for xref, form in forms.items():
        try:
            instructions = pikepdf.parse_content_stream(form)
        except pikepdf.PdfError as exc:
            raise MarginLedgerError(f"cannot parse marginal Form {xref}: {exc}") from exc
        stack: list[str] = []
        for operands, operator in instructions:
            operation = str(operator)
            if operation in {"BMC", "BDC"}:
                if not operands:
                    _reject(f"empty marked-content operator in marginal Form {xref}")
                tag = _pdf_name(operands[0])
                if tag.startswith("NXMargin"):
                    _reject(f"margin marked-content tag {tag} is forbidden inside Form {xref}")
                stack.append(tag)
            elif operation == "EMC":
                if not stack:
                    _reject(f"unbalanced EMC in marginal Form {xref}")
                stack.pop()
        if stack:
            _reject(f"unclosed marked content in marginal Form {xref}")


def _run_qpdf_check(
    pdf_path: Path,
    *,
    runner: Any = None,
    environment: Mapping[str, str] | None = None,
) -> None:
    active_runner = subprocess.run if runner is None else runner
    try:
        result = active_runner(
            ["qpdf", "--check", str(pdf_path)],
            **_command_options(environment),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise MarginLedgerError(f"qpdf unavailable or timed out: {exc}") from exc
    if result.returncode != 0:
        _reject(f"qpdf rejected PDF: {(result.stdout + result.stderr).strip()}")


def _marked_occurrences(
    pdf: pikepdf.Pdf,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    notes: list[dict[str, Any]] = []
    anchors: list[dict[str, Any]] = []
    for page_index, page in enumerate(pdf.pages, start=1):
        stack: list[dict[str, Any]] = []
        try:
            instructions = pikepdf.parse_content_stream(page)
        except pikepdf.PdfError as exc:
            raise MarginLedgerError(f"cannot parse page {page_index} content: {exc}") from exc
        for operands, operator in instructions:
            operation = str(operator)
            if operation in {"BMC", "BDC"}:
                if not operands:
                    _reject(f"empty marked-content operator on page {page_index}")
                tag = _pdf_name(operands[0])
                if tag.startswith("NXMargin") and tag not in KNOWN_MARGIN_TAGS:
                    _reject(f"unknown margin marked-content tag {tag}")
                record: dict[str, Any] = {"tag": tag}
                if tag in KNOWN_MARGIN_TAGS:
                    if operation != "BDC" or len(operands) != 2 or not isinstance(
                        operands[1], pikepdf.Dictionary
                    ):
                        _reject(f"{tag} requires one inline property dictionary")
                    properties = operands[1]
                    if tag == "NXMarginAnchor":
                        property_keys = {str(key) for key in properties.keys()}
                        if property_keys != {"/ID", "/Order"}:
                            _reject("NXMarginAnchor has unexpected or missing properties")
                        record.update(
                            {
                                "properties": properties,
                                "note_id": _pdf_exact_string(
                                    properties.get("/ID"), "NXMarginAnchor /ID"
                                ),
                                "order": _pdf_exact_integer(
                                    properties.get("/Order"), "NXMarginAnchor /Order"
                                ),
                                "page_index": page_index,
                            }
                        )
                        anchors.append(record)
                    else:
                        if {str(key) for key in properties.keys()} != NOTE_PROPERTY_KEYS:
                            _reject("NXMarginNote has unexpected or missing properties")
                        note_id = _pdf_exact_string(properties.get("/ID"), f"{tag} /ID")
                        order = _pdf_exact_integer(
                            properties.get("/Order"), f"{tag} /Order"
                        )
                        record.update(
                            {
                                "properties": properties,
                                "note_id": note_id,
                                "order": order,
                            }
                        )
                        record.update(
                            {
                                "page_index": page_index,
                                "page": page,
                                "form_name": None,
                            }
                        )
                        notes.append(record)
                stack.append(record)
            elif operation == "Do":
                active_notes = [item for item in stack if item["tag"] == "NXMarginNote"]
                if active_notes:
                    active = active_notes[-1]
                    if active["form_name"] is not None:
                        _reject(f"NXMarginNote {active['note_id']} invokes multiple Forms")
                    if len(operands) != 1:
                        _reject(f"NXMarginNote {active['note_id']} has malformed Do")
                    active["form_name"] = operands[0]
            elif operation == "EMC":
                if not stack:
                    _reject(f"unbalanced EMC on page {page_index}")
                stack.pop()
        if stack:
            _reject(f"unclosed marked content on page {page_index}")
    return notes, anchors


def _stable_requires_marker(
    note: Mapping[str, Any], marker_threshold_sp: int
) -> bool:
    return bool(
        note["requires_marker"]
        or note["report_depth"] > 0
        or note["target_shipout_index"] != note["origin_shipout_index"]
        or abs(note["target_y_sp"] - note["origin_y_sp"])
        > marker_threshold_sp
    )


def _entry_from_occurrence(
    occurrence: Mapping[str, Any],
    stable_note: Mapping[str, Any],
    marker_threshold_sp: int,
    anchor_count: int,
    pages: Mapping[int, Mapping[str, Any]],
) -> MarginLedgerEntry:
    note_id = occurrence["note_id"]
    properties = occurrence["properties"]
    if occurrence["form_name"] is None:
        _reject(f"NXMarginNote {note_id} does not invoke a Form XObject")
    if occurrence["page_index"] != stable_note["target_shipout_index"]:
        _reject(f"NXMarginNote {note_id} is on the wrong page")
    resources = occurrence["page"].obj.get("/Resources")
    xobjects = resources and resources.get("/XObject")
    if xobjects is None or occurrence["form_name"] not in xobjects:
        _reject(f"NXMarginNote {note_id} references an unknown Form XObject")
    form = xobjects[occurrence["form_name"]]
    if str(form.get("/Subtype", "")) != "/Form":
        _reject(f"NXMarginNote {note_id} does not reference a /Form")
    form_bbox = _form_bbox(form, note_id)
    _check_form_bbox_dimensions(form_bbox, stable_note)
    _check_form_matrix(form, note_id)
    if "/Annots" in form:
        _reject(f"Form for {note_id} illegally contains annotations")
    if _pdf_exact_string(form.get("/NXMarginID"), "Form /NXMarginID") != note_id:
        _reject(f"Form identity differs for {note_id}")
    if _pdf_exact_string(form.get("/NXMarginRole"), "Form /NXMarginRole") != stable_note[
        "role"
    ]:
        _reject(f"Form role differs for {note_id}")
    if _pdf_exact_integer(
        form.get("/NXMarginOrder"), "Form /NXMarginOrder"
    ) != stable_note["global_order"]:
        _reject(f"Form order differs for {note_id}")

    bbox = _bbox_sp(properties.get("/BBoxSP"), f"NXMarginNote {note_id} /BBoxSP")
    if bbox != _expected_bbox(stable_note, pages):
        _reject(f"NXMarginNote {note_id} /BBoxSP differs from stable placement")
    expected_properties: tuple[tuple[str, Any], ...] = (
        ("/Role", stable_note["role"]),
        ("/Order", stable_note["global_order"]),
        ("/OriginPage", stable_note["origin_shipout_index"]),
        ("/OriginFolio", stable_note["origin_folio"]),
        ("/TargetPage", stable_note["target_shipout_index"]),
        ("/TargetFolio", pages[stable_note["target_shipout_index"]]["folio"]),
        ("/ReportDepth", stable_note["report_depth"]),
    )
    for key, expected in expected_properties:
        actual = properties.get(key)
        if isinstance(expected, int):
            actual = _pdf_exact_integer(actual, f"NXMarginNote {note_id} {key}")
        else:
            actual = _pdf_exact_string(actual, f"NXMarginNote {note_id} {key}")
        if actual != expected:
            _reject(f"NXMarginNote {note_id} has incoherent {key}")
    requires_marker = _pdf_boolean(
        properties.get("/RequiresMarker"), f"NXMarginNote {note_id} /RequiresMarker"
    )
    expected_requires_marker = _stable_requires_marker(stable_note, marker_threshold_sp)
    if requires_marker != expected_requires_marker:
        _reject(f"NXMarginNote {note_id} has self-justified /RequiresMarker")
    expected_anchor_count = 1 if expected_requires_marker else 0
    if anchor_count != expected_anchor_count:
        _reject(f"NXMarginNote {note_id} has an incoherent anchor count")

    try:
        stream = form.read_bytes()
    except pikepdf.PdfError as exc:
        raise MarginLedgerError(f"cannot decode Form for {note_id}: {exc}") from exc
    return MarginLedgerEntry(
        note_id=note_id,
        role=stable_note["role"],
        global_order=stable_note["global_order"],
        origin_shipout_index=stable_note["origin_shipout_index"],
        origin_folio=stable_note["origin_folio"],
        target_shipout_index=stable_note["target_shipout_index"],
        target_folio=pages[stable_note["target_shipout_index"]]["folio"],
        bbox_sp=bbox,
        semantic_digest=stable_note["semantic_digest"],
        rendered_stream_digest=_sha256_bytes(stream),
        form_xref=form.objgen[0],
        anchor_count=anchor_count,
        note_count=1,
        report_depth=stable_note["report_depth"],
        requires_marker=expected_requires_marker,
    )


def validate_ledger_document(document: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a ledger with the one authoritative margin contract."""

    contract = _load_margin_contract()
    try:
        return contract.validate_margin_ledger(dict(document))
    except contract.MarginContractError as exc:
        raise MarginLedgerError(f"invalid margin ledger: {exc}") from exc


def reconstruct_margin_ledger(
    pdf_path: str | Path,
    capture_inventory: Mapping[str, Any] | str | Path,
    stable_layout: Mapping[str, Any] | str | Path,
    link_inventory: Mapping[str, Any] | str | Path,
) -> dict[str, Any]:
    """Return the sorted canonical ledger reconstructed from actual PDF objects."""

    pdf_file = Path(pdf_path)
    capture, stable, contract = _validate_inputs(capture_inventory, stable_layout)
    expected_links = _validate_link_inventory(link_inventory, capture)
    if not pdf_file.is_file():
        _reject(f"PDF does not exist: {pdf_file}")
    _run_qpdf_check(pdf_file)
    _check_extracted_text(pdf_file, stable["variant"])

    stable_notes = stable["notes"]
    stable_by_id = {note["id"]: note for note in stable_notes}
    link_notes_by_id = {note["note_id"]: note for note in expected_links["notes"]}
    pages = {page["shipout_index"]: page for page in stable["pages"]}
    try:
        with pikepdf.Pdf.open(pdf_file) as pdf:
            _check_pdf_page_sequence(pdf, stable)
            _check_pdf_text_operators(pdf, stable["variant"])
            forms = _margin_forms(pdf)
            _check_form_margin_tags(forms)
            occurrences, anchor_occurrences = _marked_occurrences(pdf)
            occurrence_counts = Counter(item["note_id"] for item in occurrences)
            anchors = Counter(item["note_id"] for item in anchor_occurrences)
            stable_ids = [note["id"] for note in stable_notes]
            if set(occurrence_counts) != set(stable_ids):
                _reject("PDF note IDs differ from stable capture IDs")
            duplicate_ids = [
                note_id for note_id, count in occurrence_counts.items() if count != 1
            ]
            if duplicate_ids:
                _reject(f"PDF note IDs are duplicated: {', '.join(sorted(duplicate_ids))}")
            encountered = [(item["order"], item["note_id"]) for item in occurrences]
            stable_encountered = [
                (note["global_order"], note["id"]) for note in stable_notes
            ]
            if encountered != stable_encountered:
                _reject("PDF note encounter order differs from stable global order")
            if set(anchors) - set(stable_ids):
                _reject("an anchor exists without a captured note")
            expected_anchor_order = sorted(
                (
                    note["origin_shipout_index"],
                    note["global_order"],
                    note["id"],
                )
                for note in stable_notes
                if _stable_requires_marker(
                    note,
                    link_notes_by_id[note["id"]]["marker_threshold_sp"],
                )
            )
            encountered_anchor_order = [
                (anchor["page_index"], anchor["order"], anchor["note_id"])
                for anchor in anchor_occurrences
            ]
            if encountered_anchor_order != expected_anchor_order:
                _reject("PDF anchor encounter order differs from stable global order")
            for anchor in anchor_occurrences:
                stable_note = stable_by_id[anchor["note_id"]]
                if anchor["order"] != stable_note["global_order"]:
                    _reject(
                        f"NXMarginAnchor {anchor['note_id']} /Order differs "
                        "from stable global_order"
                    )
                if anchor["page_index"] != stable_note["origin_shipout_index"]:
                    _reject(
                        f"NXMarginAnchor {anchor['note_id']} is not on its origin page"
                    )
            by_id = {item["note_id"]: item for item in occurrences}
            entries = [
                _entry_from_occurrence(
                    by_id[note_id],
                    stable_by_id[note_id],
                    link_notes_by_id[note_id]["marker_threshold_sp"],
                    anchors[note_id],
                    pages,
                )
                for note_id in stable_ids
            ]
            entry_xrefs = {entry.form_xref for entry in entries}
            if set(forms) != entry_xrefs:
                _reject("marginal Form inventory is not bijective with rendered notes")
            form_ids = [
                _pdf_exact_string(form.get("/NXMarginID"), "Form /NXMarginID")
                for form in forms.values()
            ]
            if len(set(form_ids)) != len(form_ids):
                _reject("marginal Form IDs are duplicated")
            _check_expected_links(pdf, expected_links, stable_by_id, pages)
            _check_link_duplicates(pdf)
    except pikepdf.PdfError as exc:
        raise MarginLedgerError(f"cannot inspect PDF: {exc}") from exc

    entries.sort(key=lambda item: (item.global_order, item.note_id.encode("utf-8")))
    if [entry.note_id for entry in entries] != [note["id"] for note in stable_notes]:
        _reject("PDF note order differs from stable layout")
    if len({entry.form_xref for entry in entries}) != len(entries):
        _reject("multiple notes reference the same Form XObject")
    note_documents = [asdict(entry) for entry in entries]
    for note in note_documents:
        note["bbox_sp"] = list(note["bbox_sp"])
    rendered_projection = [
        {
            "note_id": entry.note_id,
            "rendered_stream_digest": entry.rendered_stream_digest,
        }
        for entry in entries
    ]
    capture_projection = contract.canonical_capture_projection(capture)
    ledger = {
        "schema_version": 1,
        "variant": stable["variant"],
        "pdf_sha256": _sha256_bytes(pdf_file.read_bytes()),
        "capture_inventory_digest": contract.canonical_digest(capture_projection),
        "stable_layout_digest": contract.canonical_digest(stable),
        "rendered_stream_digest": contract.canonical_digest(rendered_projection),
        "notes": note_documents,
    }
    return validate_ledger_document(ledger)


def _pdf_fraction(value: Any, label: str) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        _reject(f"{label} must be a finite PDF number")
    try:
        number = Fraction(str(value)) if isinstance(value, float) else Fraction(value)
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise MarginLedgerError(f"{label} must be a finite PDF number") from exc
    return number


def _pdf_box(value: Any, label: str) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    if not isinstance(value, (list, pikepdf.Array)) or len(value) != 4:
        _reject(f"{label} must contain four coordinates")
    box = tuple(
        _pdf_fraction(coordinate, f"{label}[{index}]")
        for index, coordinate in enumerate(value)
    )
    if box[0] >= box[2] or box[1] >= box[3]:
        _reject(f"{label} must have positive width and height")
    return box


def _page_frame(
    page: Any, page_index: int
) -> tuple[tuple[Fraction, Fraction, Fraction, Fraction], Fraction]:
    crop_value = page.obj.get("/CropBox") or page.obj.get("/MediaBox")
    crop = _pdf_box(crop_value, f"page {page_index} /CropBox")
    user_unit = _pdf_fraction(page.obj.get("/UserUnit", 1), f"page {page_index} /UserUnit")
    if user_unit <= 0:
        _reject(f"page {page_index} /UserUnit must be positive")
    rotate = _pdf_fraction(page.obj.get("/Rotate", 0), f"page {page_index} /Rotate")
    if rotate != 0:
        _reject(f"page {page_index} /Rotate must be 0")
    return crop, user_unit


def _compose_affine(
    current: tuple[Fraction, Fraction, Fraction, Fraction, Fraction, Fraction],
    following: tuple[Fraction, Fraction, Fraction, Fraction, Fraction, Fraction],
) -> tuple[Fraction, Fraction, Fraction, Fraction, Fraction, Fraction]:
    a, b, c, d, e, f = current
    aa, bb, cc, dd, ee, ff = following
    return (
        a * aa + c * bb,
        b * aa + d * bb,
        a * cc + c * dd,
        b * cc + d * dd,
        a * ee + c * ff + e,
        b * ee + d * ff + f,
    )


def _rendered_margin_occurrences(pdf: pikepdf.Pdf) -> list[dict[str, Any]]:
    identity = (
        Fraction(1),
        Fraction(0),
        Fraction(0),
        Fraction(1),
        Fraction(0),
        Fraction(0),
    )
    rendered: list[dict[str, Any]] = []
    for page_index, page in enumerate(pdf.pages, start=1):
        ctm = identity
        graphics_stack: list[
            tuple[Fraction, Fraction, Fraction, Fraction, Fraction, Fraction]
        ] = []
        marked_stack: list[tuple[str, str | None]] = []
        resources = page.obj.get("/Resources")
        xobjects = resources and resources.get("/XObject")
        try:
            instructions = pikepdf.parse_content_stream(page)
        except pikepdf.PdfError as exc:
            raise MarginLedgerError(
                f"cannot parse page {page_index} geometry: {exc}"
            ) from exc
        for operands, operator in instructions:
            operation = str(operator)
            if operation == "q":
                graphics_stack.append(ctm)
            elif operation == "Q":
                if not graphics_stack:
                    _reject(f"unbalanced Q on page {page_index}")
                ctm = graphics_stack.pop()
            elif operation == "cm":
                if len(operands) != 6:
                    _reject(f"malformed cm on page {page_index}")
                matrix = tuple(
                    _pdf_fraction(value, f"page {page_index} cm[{position}]")
                    for position, value in enumerate(operands)
                )
                ctm = _compose_affine(ctm, matrix)
            elif operation in {"BMC", "BDC"}:
                tag = _pdf_name(operands[0]) if operands else ""
                note_id: str | None = None
                if tag == "NXMarginNote" and len(operands) == 2:
                    note_id = _pdf_exact_string(
                        operands[1].get("/ID"), "NXMarginNote /ID"
                    )
                marked_stack.append((tag, note_id))
            elif operation == "Do":
                active = next(
                    (
                        item
                        for item in reversed(marked_stack)
                        if item[0] == "NXMarginNote"
                    ),
                    None,
                )
                if active is None:
                    continue
                if len(operands) != 1 or xobjects is None or operands[0] not in xobjects:
                    _reject(f"NXMarginNote {active[1]} invokes an unknown Form")
                rendered.append(
                    {
                        "note_id": active[1],
                        "page_index": page_index,
                        "form": xobjects[operands[0]],
                        "ctm": ctm,
                    }
                )
            elif operation == "EMC":
                if not marked_stack:
                    _reject(f"unbalanced EMC on page {page_index}")
                marked_stack.pop()
        if graphics_stack:
            _reject(f"unclosed graphics state on page {page_index}")
        if marked_stack:
            _reject(f"unclosed marked content on page {page_index}")
    return rendered


def _canonical_rendered_bbox_sp(
    occurrence: Mapping[str, Any],
    crop: tuple[Fraction, Fraction, Fraction, Fraction],
    user_unit: Fraction,
) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    note_id = occurrence["note_id"]
    form_bbox = _pdf_box(occurrence["form"].get("/BBox"), f"Form {note_id} /BBox")
    _check_form_matrix(occurrence["form"], note_id)
    a, b, c, d, e, f = occurrence["ctm"]
    if (a, b, c, d) != (1, 0, 0, 1):
        _reject(f"NXMarginNote {note_id} must use a translation-only CTM")
    pdf_left = form_bbox[0] + e
    pdf_bottom = form_bbox[1] + f
    pdf_right = form_bbox[2] + e
    pdf_top = form_bbox[3] + f
    llx, _lly, _urx, ury = crop
    return (
        (pdf_left - llx) * user_unit * BP_TO_SP_EXACT,
        (ury - pdf_top) * user_unit * BP_TO_SP_EXACT,
        (pdf_right - llx) * user_unit * BP_TO_SP_EXACT,
        (ury - pdf_bottom) * user_unit * BP_TO_SP_EXACT,
    )


def _rectangles_intersect(
    first: Sequence[Fraction], second: Sequence[Fraction]
) -> bool:
    return max(first[0], second[0]) < min(first[2], second[2]) and max(
        first[1], second[1]
    ) < min(first[3], second[3])


def _check_poppler_cropboxes(
    pdf_path: Path,
    frames: Sequence[
        tuple[tuple[Fraction, Fraction, Fraction, Fraction], Fraction]
    ],
    *,
    runner: Any = None,
    environment: Mapping[str, str] | None = None,
) -> None:
    active_runner = subprocess.run if runner is None else runner
    try:
        result = active_runner(
            ["pdftotext", "-cropbox", "-bbox-layout", str(pdf_path), "-"],
            **_command_options(environment),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise MarginLedgerError(f"cannot obtain Poppler crop coordinates: {exc}") from exc
    if result.returncode != 0:
        _reject(f"Poppler rejected PDF geometry: {result.stderr.strip()}")
    try:
        root = ET.fromstring(result.stdout)
    except ET.ParseError as exc:
        raise MarginLedgerError(f"Poppler returned malformed bbox XML: {exc}") from exc
    page_elements = [element for element in root.iter() if element.tag.endswith("page")]
    if len(page_elements) != len(frames):
        _reject("Poppler page inventory differs from the PDF CropBox inventory")
    for page_index, (element, frame) in enumerate(
        zip(page_elements, frames, strict=True), start=1
    ):
        crop, user_unit = frame
        try:
            poppler_width = Fraction(element.attrib["width"])
            poppler_height = Fraction(element.attrib["height"])
        except (KeyError, ValueError, ZeroDivisionError) as exc:
            raise MarginLedgerError(
                f"Poppler page {page_index} lacks normalized dimensions"
            ) from exc
        expected_width = crop[2] - crop[0]
        expected_height = crop[3] - crop[1]
        for actual, expected in (
            (poppler_width, expected_width),
            (poppler_height, expected_height),
        ):
            difference_sp = abs(actual - expected) * user_unit * BP_TO_SP_EXACT
            if difference_sp > MARGIN_GEOMETRY_TOLERANCE_SP:
                _reject(
                    f"Poppler page {page_index} coordinates differ from its CropBox"
                )


def _check_margin_payload_policy(
    variant: str,
    stable_notes: Sequence[Mapping[str, Any]],
) -> None:
    for note in stable_notes:
        expected_prefix = f"nxm:{variant}:{note['role']}:"
        if not note["id"].startswith(expected_prefix):
            _reject(f"margin note {note['id']} violates variant/role identity policy")
        if variant == "eleve" and note["role"] == "professor-id":
            _reject("student margin evidence contains a professor-only payload")


def verify_margin_layout(
    pdf: str | Path,
    capture_inventory: Mapping[str, Any] | str | Path,
    stable_layout: Mapping[str, Any] | str | Path,
    ledger: Mapping[str, Any] | str | Path,
    *,
    runner: Any = None,
    environment: Mapping[str, str] | None = None,
) -> MarginVerificationResult:
    """Verify contract, identity and physical geometry of every marginal note.

    Canonical boxes are TeX scaled points relative to the CropBox upper-left;
    x increases right and y increases down. PDF user coordinates are converted
    through the page's positive /UserUnit. Nonzero /Rotate is intentionally
    rejected by this first closed coordinate convention.
    """

    pdf_file = Path(pdf)
    if not pdf_file.is_file():
        _reject(f"PDF does not exist: {pdf_file}")
    capture, stable, contract = _validate_inputs(capture_inventory, stable_layout)
    ledger = _load_document(ledger, "margin ledger")
    try:
        contract.validate_margin_ledger(ledger)
    except contract.MarginContractError as exc:
        raise MarginLedgerError(f"invalid margin ledger: {exc}") from exc

    capture_projection = contract.canonical_capture_projection(capture)
    stable_projection = contract.canonical_capture_projection(stable)
    if contract.canonical_json_bytes(capture_projection) != contract.canonical_json_bytes(
        stable_projection
    ):
        _reject("capture inventory and stable layout projections differ")
    capture_digest = contract.canonical_digest(capture_projection)
    stable_digest = contract.canonical_digest(stable)
    if ledger["capture_inventory_digest"] != capture_digest:
        _reject("ledger capture inventory digest differs from validated evidence")
    if ledger["stable_layout_digest"] != stable_digest:
        _reject("ledger stable layout digest differs from validated evidence")
    if ledger["pdf_sha256"] != _sha256_bytes(pdf_file.read_bytes()):
        _reject("ledger PDF digest differs from the inspected PDF")
    if ledger["variant"] != stable["variant"]:
        _reject("ledger variant differs from stable layout")

    stable_notes = stable["notes"]
    stable_by_id = {note["id"]: note for note in stable_notes}
    ledger_notes = ledger["notes"]
    ledger_by_id = {note["note_id"]: note for note in ledger_notes}
    stable_ids = [note["id"] for note in stable_notes]
    ledger_ids = [note["note_id"] for note in ledger_notes]
    if set(stable_ids) != set(ledger_ids):
        _reject("ledger note IDs differ from stable capture IDs")
    stable_cardinality = Counter((stable["variant"], note["role"]) for note in stable_notes)
    ledger_cardinality = Counter((ledger["variant"], note["role"]) for note in ledger_notes)
    if stable_cardinality != ledger_cardinality:
        _reject("ledger role/variant cardinalities differ from stable capture")
    _check_margin_payload_policy(stable["variant"], stable_notes)

    pages = {page["shipout_index"]: page for page in stable["pages"]}
    for note_id in stable_ids:
        stable_note = stable_by_id[note_id]
        ledger_note = ledger_by_id[note_id]
        expected_bbox = _expected_bbox(stable_note, pages)
        expected_fields = {
            "role": stable_note["role"],
            "global_order": stable_note["global_order"],
            "origin_shipout_index": stable_note["origin_shipout_index"],
            "origin_folio": stable_note["origin_folio"],
            "target_shipout_index": stable_note["target_shipout_index"],
            "target_folio": pages[stable_note["target_shipout_index"]]["folio"],
            "bbox_sp": list(expected_bbox),
            "semantic_digest": stable_note["semantic_digest"],
            "report_depth": stable_note["report_depth"],
        }
        for field, expected in expected_fields.items():
            if ledger_note[field] != expected:
                _reject(f"ledger note {note_id} has incoherent {field}")
        if stable_note["requires_marker"] and not ledger_note["requires_marker"]:
            _reject(f"ledger note {note_id} drops a stable required marker")

    _run_qpdf_check(pdf_file, runner=runner, environment=environment)
    _check_extracted_text(
        pdf_file,
        stable["variant"],
        runner=runner,
        environment=environment,
    )
    try:
        with pikepdf.Pdf.open(pdf_file) as pdf:
            _check_pdf_page_sequence(pdf, stable)
            _check_pdf_text_operators(pdf, stable["variant"])
            frames = [
                _page_frame(page, page_index)
                for page_index, page in enumerate(pdf.pages, start=1)
            ]
            for page_index, (frame, stable_page) in enumerate(
                zip(frames, stable["pages"], strict=True), start=1
            ):
                crop, user_unit = frame
                dimensions_sp = (
                    (crop[2] - crop[0]) * user_unit * BP_TO_SP_EXACT,
                    (crop[3] - crop[1]) * user_unit * BP_TO_SP_EXACT,
                )
                expected_dimensions = (
                    stable_page["page_width_sp"],
                    stable_page["page_height_sp"],
                )
                if any(
                    abs(actual - expected) > MARGIN_GEOMETRY_TOLERANCE_SP
                    for actual, expected in zip(
                        dimensions_sp, expected_dimensions, strict=True
                    )
                ):
                    _reject(f"page {page_index} CropBox differs from stable geometry")

            forms = _margin_forms(pdf)
            _check_form_margin_tags(forms)
            occurrences, anchors = _marked_occurrences(pdf)
            rendered = _rendered_margin_occurrences(pdf)
            occurrence_counts = Counter(item["note_id"] for item in occurrences)
            rendered_counts = Counter(item["note_id"] for item in rendered)
            if set(occurrence_counts) != set(stable_ids) or set(rendered_counts) != set(
                stable_ids
            ):
                _reject("rendered PDF note IDs differ from stable capture IDs")
            if any(occurrence_counts[note_id] != 1 for note_id in stable_ids) or any(
                rendered_counts[note_id] != 1 for note_id in stable_ids
            ):
                _reject("each captured margin note must render exactly once")
            encountered_order = [
                (item["order"], item["note_id"]) for item in occurrences
            ]
            expected_order = [
                (note["global_order"], note["id"]) for note in stable_notes
            ]
            if encountered_order != expected_order:
                _reject("rendered margin note order differs from stable global order")
            anchor_counts = Counter(item["note_id"] for item in anchors)
            if set(anchor_counts) - set(stable_ids):
                _reject("an anchor exists without a captured note")
            for anchor in anchors:
                stable_note = stable_by_id[anchor["note_id"]]
                if anchor["order"] != stable_note["global_order"]:
                    _reject(f"rendered anchor {anchor['note_id']} has the wrong order")
                if anchor["page_index"] != stable_note["origin_shipout_index"]:
                    _reject(f"rendered anchor {anchor['note_id']} is on the wrong page")

            rendered_by_id = {item["note_id"]: item for item in rendered}
            occurrence_by_id = {item["note_id"]: item for item in occurrences}
            actual_bboxes: dict[str, tuple[Fraction, Fraction, Fraction, Fraction]] = {}
            rendered_projection = []
            for note_id in stable_ids:
                ledger_note = ledger_by_id[note_id]
                occurrence = occurrence_by_id[note_id]
                rendered_occurrence = rendered_by_id[note_id]
                form = rendered_occurrence["form"]
                if rendered_occurrence["page_index"] != ledger_note[
                    "target_shipout_index"
                ]:
                    _reject(f"rendered note {note_id} is on the wrong page")
                if form.objgen[0] != ledger_note["form_xref"]:
                    _reject(f"rendered note {note_id} references the wrong Form XObject")
                if _pdf_exact_string(form.get("/NXMarginID"), "Form /NXMarginID") != note_id:
                    _reject(f"Form identity differs for {note_id}")
                if _pdf_exact_string(form.get("/NXMarginRole"), "Form /NXMarginRole") != ledger_note[
                    "role"
                ]:
                    _reject(f"Form role differs for {note_id}")
                if _pdf_exact_integer(form.get("/NXMarginOrder"), "Form /NXMarginOrder") != ledger_note[
                    "global_order"
                ]:
                    _reject(f"Form order differs for {note_id}")
                if _bbox_sp(
                    occurrence["properties"].get("/BBoxSP"),
                    f"NXMarginNote {note_id} /BBoxSP",
                ) != tuple(ledger_note["bbox_sp"]):
                    _reject(f"NXMarginNote {note_id} /BBoxSP differs from ledger")
                expected_properties: tuple[tuple[str, Any], ...] = (
                    ("/Role", ledger_note["role"]),
                    ("/Order", ledger_note["global_order"]),
                    ("/OriginPage", ledger_note["origin_shipout_index"]),
                    ("/OriginFolio", ledger_note["origin_folio"]),
                    ("/TargetPage", ledger_note["target_shipout_index"]),
                    ("/TargetFolio", ledger_note["target_folio"]),
                    ("/ReportDepth", ledger_note["report_depth"]),
                    ("/RequiresMarker", ledger_note["requires_marker"]),
                )
                for key, expected in expected_properties:
                    actual = occurrence["properties"].get(key)
                    if isinstance(expected, bool):
                        actual = _pdf_boolean(actual, f"NXMarginNote {note_id} {key}")
                    elif isinstance(expected, int):
                        actual = _pdf_exact_integer(
                            actual, f"NXMarginNote {note_id} {key}"
                        )
                    else:
                        actual = _pdf_exact_string(
                            actual, f"NXMarginNote {note_id} {key}"
                        )
                    if actual != expected:
                        _reject(f"NXMarginNote {note_id} has incoherent {key}")
                if anchor_counts[note_id] != ledger_note["anchor_count"]:
                    _reject(f"rendered note {note_id} has an incoherent anchor count")
                try:
                    stream_digest = _sha256_bytes(form.read_bytes())
                except pikepdf.PdfError as exc:
                    raise MarginLedgerError(f"cannot decode Form for {note_id}: {exc}") from exc
                if stream_digest != ledger_note["rendered_stream_digest"]:
                    _reject(f"rendered stream digest differs for {note_id}")
                rendered_projection.append(
                    {"note_id": note_id, "rendered_stream_digest": stream_digest}
                )
                frame = frames[rendered_occurrence["page_index"] - 1]
                actual_bboxes[note_id] = _canonical_rendered_bbox_sp(
                    rendered_occurrence, *frame
                )
            if contract.canonical_digest(rendered_projection) != ledger[
                "rendered_stream_digest"
            ]:
                _reject("aggregate rendered stream digest differs from ledger")
            if set(forms) != {ledger_by_id[note_id]["form_xref"] for note_id in stable_ids}:
                _reject("marginal Form inventory is not bijective with ledger notes")

            for page_index in range(1, len(stable["pages"]) + 1):
                page_note_ids = [
                    note_id
                    for note_id in stable_ids
                    if rendered_by_id[note_id]["page_index"] == page_index
                ]
                for position, note_id in enumerate(page_note_ids):
                    for other_id in page_note_ids[position + 1 :]:
                        if _rectangles_intersect(
                            actual_bboxes[note_id], actual_bboxes[other_id]
                        ):
                            _reject(f"rendered notes {note_id} and {other_id} intersect")
                vertically_sorted = sorted(
                    page_note_ids,
                    key=lambda note_id: (
                        actual_bboxes[note_id][1],
                        ledger_by_id[note_id]["global_order"],
                        note_id.encode("utf-8"),
                    ),
                )
                for first_id, second_id in zip(
                    vertically_sorted, vertically_sorted[1:]
                ):
                    gap = actual_bboxes[second_id][1] - actual_bboxes[first_id][3]
                    if gap < MARGIN_GAP_SP:
                        _reject(
                            f"rendered notes {first_id} and {second_id} "
                            "have less than 6pt vertical gap"
                        )
                stable_page = pages[page_index]
                safe = stable_page["safe_rect"]
                safe_box = (
                    Fraction(safe["left_sp"]),
                    Fraction(safe["top_sp"]),
                    Fraction(safe["right_sp"]),
                    Fraction(safe["bottom_sp"]),
                )
                for note_id in page_note_ids:
                    box = actual_bboxes[note_id]
                    if (
                        box[0] < safe_box[0] - MARGIN_GEOMETRY_TOLERANCE_SP
                        or box[1] < safe_box[1] - MARGIN_GEOMETRY_TOLERANCE_SP
                        or box[2] > safe_box[2] + MARGIN_GEOMETRY_TOLERANCE_SP
                        or box[3] > safe_box[3] + MARGIN_GEOMETRY_TOLERANCE_SP
                    ):
                        _reject(f"rendered note {note_id} escapes the effective outer rail")
                    for obstacle in stable_page["obstacles"]:
                        obstacle_box = (
                            Fraction(obstacle["left_sp"]),
                            Fraction(obstacle["top_sp"]),
                            Fraction(obstacle["right_sp"]),
                            Fraction(obstacle["bottom_sp"]),
                        )
                        if _rectangles_intersect(box, obstacle_box):
                            _reject(
                                f"rendered note {note_id} intersects obstacle "
                                f"{obstacle['id']}"
                            )
                    expected_box = ledger_by_id[note_id]["bbox_sp"]
                    if any(
                        abs(actual - Fraction(expected))
                        > MARGIN_GEOMETRY_TOLERANCE_SP
                        for actual, expected in zip(box, expected_box, strict=True)
                    ):
                        _reject(
                            f"rendered note {note_id} differs by more than 1sp "
                            "from ledger coordinates"
                        )
    except pikepdf.PdfError as exc:
        raise MarginLedgerError(f"cannot inspect PDF: {exc}") from exc

    _check_poppler_cropboxes(
        pdf_file,
        frames,
        runner=runner,
        environment=environment,
    )
    return MarginVerificationResult(
        passed=True,
        variant=stable["variant"],
        page_count=len(stable["pages"]),
        note_count=len(stable_notes),
        qpdf_checked=True,
        poppler_checked=True,
        capture_inventory_digest=capture_digest,
        stable_layout_digest=stable_digest,
        ledger_digest=contract.canonical_digest(ledger),
    )


def write_margin_ledger(
    pdf_path: str | Path,
    capture_inventory: Mapping[str, Any] | str | Path,
    stable_layout: Mapping[str, Any] | str | Path,
    link_inventory: Mapping[str, Any] | str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    """Atomically write deterministic canonical ledger bytes."""

    contract = _load_margin_contract()
    ledger = reconstruct_margin_ledger(
        pdf_path, capture_inventory, stable_layout, link_inventory
    )
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.", suffix=".tmp", dir=output.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(contract.canonical_json_bytes(ledger))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, output)
        directory_descriptor = os.open(output.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        temporary.unlink(missing_ok=True)
    return ledger


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--capture-inventory", required=True, type=Path)
    parser.add_argument("--stable-layout", required=True, type=Path)
    parser.add_argument("--link-inventory", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        write_margin_ledger(
            arguments.pdf,
            arguments.capture_inventory,
            arguments.stable_layout,
            arguments.link_inventory,
            arguments.output,
        )
    except MarginLedgerError as exc:
        print(f"NEXUS-MARGIN-LEDGER-ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
