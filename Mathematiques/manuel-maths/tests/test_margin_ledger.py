from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from copy import deepcopy
from pathlib import Path
from types import ModuleType
from typing import Any

import pikepdf
import pytest


MANUAL_ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = MANUAL_ROOT / "scripts" / "margin_ledger.py"
CONTRACT_PATH = MANUAL_ROOT / "scripts" / "margin_contract.py"
MAX_PASSES = 6
CAPTURE_RECORD = re.compile(r"NEXUS-MARGIN-CAPTURE:(nxm:[^:\s]+:[^:\s]+:\d{8})")
FORM_RECORD = re.compile(
    r"NEXUS-MARGIN-FORM:(nxm:[^:\s]+:[^:\s]+:\d{8}):(\d+)"
)
FIXTURE_ROOT = MANUAL_ROOT / "tests" / "fixtures"
SP_PER_PT = 65536
SP_TO_BP = 72 / (72.27 * SP_PER_PT)


def _load_module(path: Path, name: str) -> ModuleType:
    assert path.is_file(), f"module PDF manquant: {path}"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_contract() -> ModuleType:
    return _load_module(CONTRACT_PATH, "margin_contract_for_ledger_test")


def _load_ledger() -> ModuleType:
    return _load_module(LEDGER_PATH, "margin_ledger_for_test")


def _atomic_json(path: Path, document: dict[str, Any]) -> None:
    contract = _load_contract()
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(contract.canonical_json_bytes(document))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _run_private_passes(
    source: Path,
    output_directory: Path,
    *,
    run_nonce: str = "0123456789abcdef0123456789abcdef",
    variant: str = "eleve",
) -> dict[str, Any]:
    contract = _load_contract()
    output_directory.mkdir(parents=True, exist_ok=True)
    previous = output_directory / "margin-layout.previous.json"
    next_layout = output_directory / "margin-layout.next.json"
    next_links = output_directory / "margin-links.next.json"
    stable_path = output_directory / "margin-stable-layout.json"
    observations: list[dict[str, Any]] = []

    for pass_number in range(1, MAX_PASSES + 1):
        next_layout.unlink(missing_ok=True)
        next_links.unlink(missing_ok=True)
        environment = os.environ.copy()
        environment.update(
            {
                "NEXUS_MARGIN_RUN_NONCE": run_nonce,
                "NEXUS_MARGIN_VARIANT": variant,
                "NEXUS_MARGIN_PASS_NUMBER": str(pass_number),
                "NEXUS_MARGIN_LAYOUT_PREVIOUS": str(previous),
                "NEXUS_MARGIN_LAYOUT_NEXT": str(next_layout),
                "NEXUS_MARGIN_LINK_INVENTORY_NEXT": str(next_links),
                "NEXUS_MARGIN_MARKER_METADATA": "1",
                "SOURCE_DATE_EPOCH": "1704067200",
                "TZ": "UTC",
            }
        )
        result = subprocess.run(
            [
                "lualatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={output_directory}",
                str(source),
            ],
            cwd=MANUAL_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout[-10000:] + result.stderr
        assert next_layout.is_file(), "margin-layout.next.json absent"
        assert next_links.is_file(), "margin-links.next.json absent"
        layout = json.loads(next_layout.read_text(encoding="utf-8"))
        link_inventory = json.loads(next_links.read_text(encoding="utf-8"))
        contract.validate_margin_layout(layout)
        assert layout["notes"], "zéro capture ne constitue pas une preuve PDF"
        observations.append(
            {
                "layout": layout,
                "captures": CAPTURE_RECORD.findall(result.stdout),
                "forms": FORM_RECORD.findall(result.stdout),
                "stdout": result.stdout,
            }
        )
        os.replace(next_layout, previous)
        if layout["state"] == "stable":
            assert layout["read_digest"] == layout["computed_digest"]
            stable = contract.materialize_stable_layout(layout)
            _atomic_json(stable_path, stable)
            break
        assert layout["state"] in {"collecting", "changed"}
    else:
        pytest.fail("placements marginaux non stabilisés après six passes")

    pdf_path = output_directory / f"{source.stem}.pdf"
    assert pdf_path.is_file()
    return {
        "capture": json.loads(previous.read_text(encoding="utf-8")),
        "stable": json.loads(stable_path.read_text(encoding="utf-8")),
        "stable_bytes": stable_path.read_bytes(),
        "links": link_inventory,
        "pdf": pdf_path,
        "observations": observations,
    }


def _marked_content_counts(pdf_path: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    with pikepdf.Pdf.open(pdf_path) as pdf:
        for page in pdf.pages:
            for operands, operator in pikepdf.parse_content_stream(page):
                if str(operator) not in {"BMC", "BDC"} or not operands:
                    continue
                tag = str(operands[0]).removeprefix("/")
                if tag.startswith("NXMargin"):
                    counts[tag] += 1
    return counts


def _rectangles_overlap(first: list[int], second: list[int]) -> bool:
    return max(first[0], second[0]) < min(first[2], second[2]) and max(
        first[1], second[1]
    ) < min(first[3], second[3])


def _link_annotations(pdf_path: Path) -> list[dict[str, Any]]:
    links: list[dict[str, Any]] = []
    with pikepdf.Pdf.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            for annotation in page.obj.get("/Annots", []):
                item = annotation
                if str(item.get("/Subtype", "")) != "/Link":
                    continue
                action = item.get("/A")
                links.append(
                    {
                        "page": page_index,
                        "rect": tuple(float(value) for value in item["/Rect"]),
                        "action": str(action.get("/S", "")) if action else "",
                        "uri": str(action.get("/URI", "")) if action else "",
                        "destination": str(
                            (action.get("/D") if action else None)
                            or item.get("/Dest", "")
                        ),
                    }
                )
    return links


def _replace_page_instructions(
    pdf: pikepdf.Pdf,
    page: pikepdf.Page,
    instructions: list[Any],
) -> None:
    page.obj["/Contents"] = pikepdf.Stream(
        pdf, pikepdf.unparse_content_stream(instructions)
    )


def _without_first_margin_anchor(instructions: list[Any]) -> list[Any]:
    result: list[Any] = []
    skipping = False
    nested = 0
    removed = False
    for instruction in instructions:
        operands, operator = instruction
        operation = str(operator)
        if (
            not removed
            and not skipping
            and operation == "BDC"
            and operands
            and str(operands[0]) == "/NXMarginAnchor"
        ):
            skipping = True
            nested = 1
            removed = True
            continue
        if skipping:
            if operation in {"BDC", "BMC"}:
                nested += 1
            elif operation == "EMC":
                nested -= 1
                if nested == 0:
                    skipping = False
            continue
        result.append(instruction)
    assert removed and not skipping
    return result


def _with_first_margin_anchor_property(
    instructions: list[Any], key: str, value: Any
) -> list[Any]:
    mutated = False
    for operands, operator in instructions:
        if (
            not mutated
            and str(operator) == "BDC"
            and len(operands) == 2
            and str(operands[0]) == "/NXMarginAnchor"
        ):
            operands[1][key] = value
            mutated = True
            break
    assert mutated
    return instructions


def _with_margin_note_property(
    instructions: list[Any], note_id: str, key: str, value: Any
) -> list[Any]:
    mutated = False
    for operands, operator in instructions:
        if (
            not mutated
            and str(operator) == "BDC"
            and len(operands) == 2
            and str(operands[0]) == "/NXMarginNote"
            and str(operands[1].get("/ID", "")) == note_id
        ):
            operands[1][key] = value
            mutated = True
            break
    assert mutated
    return instructions


def _first_margin_anchor_segment(instructions: list[Any]) -> list[Any]:
    segment: list[Any] = []
    collecting = False
    nested = 0
    for instruction in instructions:
        operands, operator = instruction
        operation = str(operator)
        if (
            not collecting
            and operation == "BDC"
            and operands
            and str(operands[0]) == "/NXMarginAnchor"
        ):
            collecting = True
            nested = 1
        if collecting:
            segment.append(instruction)
            if operation in {"BDC", "BMC"} and len(segment) > 1:
                nested += 1
            elif operation == "EMC":
                nested -= 1
                if nested == 0:
                    break
    assert segment and nested == 0
    return segment


def _reverse_margin_note_segments(instructions: list[Any]) -> list[Any]:
    remainder: list[Any] = []
    segments: list[list[Any]] = []
    index = 0
    while index < len(instructions):
        operands, operator = instructions[index]
        if (
            str(operator) == "BDC"
            and operands
            and str(operands[0]) == "/NXMarginNote"
        ):
            segment: list[Any] = []
            depth = 0
            while index < len(instructions):
                instruction = instructions[index]
                operation = str(instruction[1])
                segment.append(instruction)
                if operation in {"BDC", "BMC"}:
                    depth += 1
                elif operation == "EMC":
                    depth -= 1
                    if depth == 0:
                        index += 1
                        break
                index += 1
            assert depth == 0
            segments.append(segment)
            continue
        remainder.append(instructions[index])
        index += 1
    assert len(segments) >= 2
    return remainder + [item for segment in reversed(segments) for item in segment]


def _reverse_margin_anchor_segments(instructions: list[Any]) -> list[Any]:
    remainder: list[Any] = []
    segments: list[list[Any]] = []
    index = 0
    while index < len(instructions):
        operands, operator = instructions[index]
        if (
            str(operator) == "BDC"
            and operands
            and str(operands[0]) == "/NXMarginAnchor"
        ):
            segment: list[Any] = []
            depth = 0
            while index < len(instructions):
                instruction = instructions[index]
                operation = str(instruction[1])
                segment.append(instruction)
                if operation in {"BDC", "BMC"}:
                    depth += 1
                elif operation == "EMC":
                    depth -= 1
                    if depth == 0:
                        index += 1
                        break
                index += 1
            assert depth == 0
            segments.append(segment)
            continue
        remainder.append(instructions[index])
        index += 1
    assert len(segments) >= 2
    return remainder + [item for segment in reversed(segments) for item in segment]


def _first_margin_form(pdf: pikepdf.Pdf) -> tuple[Any, Any]:
    for page in pdf.pages:
        xobjects = page.obj["/Resources"].get("/XObject", {})
        for name in xobjects:
            form = xobjects[name]
            if form.get("/NXMarginID"):
                return xobjects, form
    raise AssertionError("Form marginale absente")


def _assert_qpdf_valid(pdf_path: Path) -> None:
    result = subprocess.run(
        ["qpdf", "--check", str(pdf_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _geometry_evidence(*, same_page: bool = False) -> tuple[dict[str, Any], ...]:
    capture = json.loads((FIXTURE_ROOT / "margin-layout.valid.json").read_text())
    stable = json.loads(
        (FIXTURE_ROOT / "margin-stable-layout.valid.json").read_text()
    )
    ledger = json.loads((FIXTURE_ROOT / "margin-ledger.valid.json").read_text())
    if same_page:
        for layout in (capture, stable):
            note = layout["notes"][1]
            note.update(
                {
                    "target_shipout_index": 1,
                    "target_y_sp": 800000,
                    "effective_height_sp": note["base_height_sp"],
                    "report_depth": 0,
                    "requires_marker": False,
                }
            )
            layout["pages"][0]["placed_note_ids"] = [
                layout["notes"][0]["id"],
                note["id"],
            ]
            layout["pages"][0]["reported_note_ids"] = []
            layout["pages"][1]["carry_in_note_ids"] = []
            layout["pages"][1]["placed_note_ids"] = []
        ledger["notes"][1].update(
            {
                "target_shipout_index": 1,
                "target_folio": "1",
                "bbox_sp": [900000, 800000, 1100000, 900000],
                "anchor_count": 0,
                "report_depth": 0,
                "requires_marker": False,
            }
        )
    contract = _load_contract()
    ledger["capture_inventory_digest"] = contract.canonical_digest(
        contract.canonical_capture_projection(capture)
    )
    ledger["stable_layout_digest"] = contract.canonical_digest(stable)
    return capture, stable, ledger


def _write_geometry_pdf(
    path: Path,
    stable: dict[str, Any],
    ledger: dict[str, Any],
    *,
    crop_origin: tuple[float, float] = (0.0, 0.0),
    user_unit: float = 1.0,
    rotate: int = 0,
    rendered_bboxes: dict[str, list[int]] | None = None,
) -> None:
    rendered_bboxes = rendered_bboxes or {}
    notes_by_page: dict[int, list[dict[str, Any]]] = {}
    for note in ledger["notes"]:
        notes_by_page.setdefault(note["target_shipout_index"], []).append(note)

    pdf = pikepdf.Pdf.new()
    llx, lly = crop_origin
    for page_record in stable["pages"]:
        width = page_record["page_width_sp"] * SP_TO_BP / user_unit
        height = page_record["page_height_sp"] * SP_TO_BP / user_unit
        urx, ury = llx + width, lly + height
        page = pdf.add_blank_page(
            page_size=(max(100.0, urx + 5.0), max(100.0, ury + 5.0))
        )
        page.obj["/CropBox"] = pikepdf.Array([llx, lly, urx, ury])
        page.obj["/UserUnit"] = user_unit
        page.obj["/Rotate"] = rotate
        xobjects = pikepdf.Dictionary()
        page.obj["/Resources"] = pikepdf.Dictionary({"/XObject": xobjects})
        chunks: list[str] = []
        for note in ledger["notes"]:
            if note["requires_marker"] and note["origin_shipout_index"] == page_record[
                "shipout_index"
            ]:
                chunks.append(
                    "/NXMarginAnchor << "
                    f"/ID ({note['note_id']}) /Order {note['global_order']} "
                    ">> BDC EMC"
                )
        for index, note in enumerate(
            notes_by_page.get(page_record["shipout_index"], []), start=1
        ):
            form_name = f"/Fm{page_record['shipout_index']}_{index}"
            expected = note["bbox_sp"]
            width_user = (expected[2] - expected[0]) * SP_TO_BP / user_unit
            height_user = (expected[3] - expected[1]) * SP_TO_BP / user_unit
            fx0, fy0 = -1.25, 2.5
            form = pikepdf.Stream(pdf, b"")
            form["/Type"] = pikepdf.Name("/XObject")
            form["/Subtype"] = pikepdf.Name("/Form")
            form["/BBox"] = pikepdf.Array(
                [fx0, fy0, fx0 + width_user, fy0 + height_user]
            )
            form["/Matrix"] = pikepdf.Array([1, 0, 0, 1, 0, 0])
            form["/Resources"] = pikepdf.Dictionary()
            form["/NXMarginID"] = pikepdf.String(note["note_id"])
            form["/NXMarginRole"] = pikepdf.String(note["role"])
            form["/NXMarginOrder"] = note["global_order"]
            xobjects[form_name] = form

            actual = rendered_bboxes.get(note["note_id"], expected)
            pdf_left = llx + actual[0] * SP_TO_BP / user_unit
            pdf_bottom = ury - actual[3] * SP_TO_BP / user_unit
            tx, ty = pdf_left - fx0, pdf_bottom - fy0
            chunks.extend(
                [
                    "/NXMarginNote << "
                    f"/BBoxSP [{' '.join(str(value) for value in expected)}] "
                    f"/ID ({note['note_id']}) /Order {note['global_order']} "
                    f"/OriginPage {note['origin_shipout_index']} "
                    f"/OriginFolio ({note['origin_folio']}) "
                    f"/TargetPage {note['target_shipout_index']} "
                    f"/TargetFolio ({note['target_folio']}) "
                    f"/ReportDepth {note['report_depth']} "
                    f"/RequiresMarker {'true' if note['requires_marker'] else 'false'} "
                    f"/Role ({note['role']}) >> BDC",
                    "q",
                    f"1 0 0 1 {tx:.12f} {ty:.12f} cm",
                    f"{form_name} Do",
                    "Q",
                    "EMC",
                ]
            )
        page.obj["/Contents"] = pikepdf.Stream(
            pdf, ("\n".join(chunks) + "\n").encode("ascii")
        )
    pdf.save(path, min_version="1.6")

    rendered_projection = []
    with pikepdf.Pdf.open(path) as reopened:
        forms_by_id = {
            str(xobjects[name]["/NXMarginID"]): xobjects[name]
            for page in reopened.pages
            for xobjects in (page.obj["/Resources"]["/XObject"],)
            for name in xobjects
        }
        for note in ledger["notes"]:
            form = forms_by_id[note["note_id"]]
            note["form_xref"] = form.objgen[0]
            note["rendered_stream_digest"] = _sha256(form.read_bytes())
            rendered_projection.append(
                {
                    "note_id": note["note_id"],
                    "rendered_stream_digest": note["rendered_stream_digest"],
                }
            )
    contract = _load_contract()
    ledger["rendered_stream_digest"] = contract.canonical_digest(rendered_projection)
    ledger["pdf_sha256"] = _sha256(path.read_bytes())


def _refresh_pdf_digest(path: Path, ledger: dict[str, Any]) -> None:
    ledger["pdf_sha256"] = _sha256(path.read_bytes())


def test_margin_geometry_recto_verso_cropbox_userunit_and_actual_form_bbox_ctm(
    tmp_path: Path,
) -> None:
    capture, stable, ledger = _geometry_evidence()
    pdf = tmp_path / "shifted-crop-userunit.pdf"
    _write_geometry_pdf(
        pdf,
        stable,
        ledger,
        crop_origin=(17.0, 23.0),
        user_unit=2.0,
    )

    result = _load_ledger().verify_margin_layout(pdf, capture, stable, ledger)

    assert result.passed is True
    assert result.variant == "eleve"
    assert result.note_count == 2


def test_margin_gate_propagates_runner_environment_and_timeout_to_qpdf_poppler(
    tmp_path: Path,
) -> None:
    capture, stable, ledger = _geometry_evidence()
    pdf_path = tmp_path / "controlled-tools.pdf"
    _write_geometry_pdf(pdf_path, stable, ledger)
    with pikepdf.Pdf.open(pdf_path) as pdf:
        dimensions = [
            (
                float(page.obj["/CropBox"][2] - page.obj["/CropBox"][0]),
                float(page.obj["/CropBox"][3] - page.obj["/CropBox"][1]),
            )
            for page in pdf.pages
        ]
    bbox_xml = "<doc>" + "".join(
        f'<page width="{width:.12f}" height="{height:.12f}" />'
        for width, height in dimensions
    ) + "</doc>"
    environment = {"PATH": "/controlled/bin", "TZ": "UTC"}
    calls = []

    def runner(command, **kwargs):
        calls.append((command, kwargs))
        stdout = bbox_xml if "-bbox-layout" in command else ""
        return type(
            "Completed",
            (),
            {"returncode": 0, "stdout": stdout, "stderr": ""},
        )()

    result = _load_ledger().verify_margin_layout(
        pdf_path,
        capture,
        stable,
        ledger,
        runner=runner,
        environment=environment,
    )

    assert result.qpdf_checked is True
    assert result.poppler_checked is True
    assert [call[0][0] for call in calls] == ["qpdf", "pdftotext", "pdftotext"]
    assert all(call[1]["timeout"] == 20 for call in calls)
    assert all(call[1]["env"] == environment for call in calls)
    assert all(call[1]["env"] is not environment for call in calls)


@pytest.mark.parametrize(
    ("case", "rendered_bboxes", "reason"),
    [
        (
            "overlap",
            {"nxm:eleve:vocab:00000002": [900000, 250000, 1100000, 350000]},
            "rendered notes nxm:eleve:appui:00000001 and "
            "nxm:eleve:vocab:00000002 intersect",
        ),
        (
            "spacing",
            {
                "nxm:eleve:vocab:00000002": [
                    900000,
                    300000 + 6 * SP_PER_PT - 1,
                    1100000,
                    400000 + 6 * SP_PER_PT - 1,
                ]
            },
            "have less than 6pt vertical gap",
        ),
        (
            "rail",
            {"nxm:eleve:appui:00000001": [700000, 200000, 900000, 300000]},
            "escapes the effective outer rail",
        ),
        (
            "obstacle",
            {"nxm:eleve:appui:00000001": [900000, 110000, 1100000, 210000]},
            "intersects obstacle page-1-header",
        ),
    ],
)
def test_margin_geometry_rejects_collisions_spacing_rail_and_obstacles(
    tmp_path: Path,
    case: str,
    rendered_bboxes: dict[str, list[int]],
    reason: str,
) -> None:
    capture, stable, ledger = _geometry_evidence(same_page=True)
    pdf = tmp_path / f"{case}.pdf"
    _write_geometry_pdf(pdf, stable, ledger, rendered_bboxes=rendered_bboxes)
    ledger_module = _load_ledger()

    with pytest.raises(ledger_module.MarginLedgerError, match=re.escape(reason)):
        ledger_module.verify_margin_layout(pdf, capture, stable, ledger)


def test_margin_geometry_allows_one_sp_but_rejects_two_sp_coordinate_error(
    tmp_path: Path,
) -> None:
    note_id = "nxm:eleve:appui:00000001"
    capture, stable, ledger = _geometry_evidence()
    within = tmp_path / "within-one-sp.pdf"
    _write_geometry_pdf(
        within,
        stable,
        ledger,
        rendered_bboxes={note_id: [900000, 199999, 1100000, 299999]},
    )
    ledger_module = _load_ledger()
    assert ledger_module.verify_margin_layout(within, capture, stable, ledger).passed

    outside = tmp_path / "outside-one-sp.pdf"
    _write_geometry_pdf(
        outside,
        stable,
        ledger,
        rendered_bboxes={note_id: [900000, 200002, 1100000, 300002]},
    )
    with pytest.raises(ledger_module.MarginLedgerError, match="differs by more than 1sp"):
        ledger_module.verify_margin_layout(outside, capture, stable, ledger)


def test_margin_geometry_rejects_fractional_error_above_one_sp(tmp_path: Path) -> None:
    note_id = "nxm:eleve:appui:00000001"
    capture, stable, ledger = _geometry_evidence()
    pdf = tmp_path / "fractional-error.pdf"
    _write_geometry_pdf(
        pdf,
        stable,
        ledger,
        rendered_bboxes={note_id: [900000, 200001.4, 1100000, 300001.4]},
    )
    ledger_module = _load_ledger()

    with pytest.raises(ledger_module.MarginLedgerError, match="differs by more than 1sp"):
        ledger_module.verify_margin_layout(pdf, capture, stable, ledger)


def test_margin_geometry_uses_inherited_cropbox_and_rejects_inherited_rotate(
    tmp_path: Path,
) -> None:
    capture, stable, ledger = _geometry_evidence()
    inherited_crop = tmp_path / "inherited-crop.pdf"
    _write_geometry_pdf(inherited_crop, stable, ledger, crop_origin=(11.0, 13.0))
    with pikepdf.Pdf.open(inherited_crop, allow_overwriting_input=True) as pdf:
        crop = pikepdf.Array(pdf.pages[0].obj["/CropBox"])
        parent = pdf.pages[0].obj["/Parent"]
        parent["/CropBox"] = crop
        for page in pdf.pages:
            del page.obj["/CropBox"]
        pdf.save(inherited_crop)
    _refresh_pdf_digest(inherited_crop, ledger)
    ledger_module = _load_ledger()
    assert ledger_module.verify_margin_layout(
        inherited_crop, capture, stable, ledger
    ).passed

    inherited_rotate = tmp_path / "inherited-rotate.pdf"
    _write_geometry_pdf(inherited_rotate, stable, ledger)
    with pikepdf.Pdf.open(inherited_rotate, allow_overwriting_input=True) as pdf:
        parent = pdf.pages[0].obj["/Parent"]
        parent["/Rotate"] = 90
        for page in pdf.pages:
            del page.obj["/Rotate"]
        pdf.save(inherited_rotate)
    _refresh_pdf_digest(inherited_rotate, ledger)

    with pytest.raises(ledger_module.MarginLedgerError, match="/Rotate must be 0"):
        ledger_module.verify_margin_layout(
            inherited_rotate, capture, stable, ledger
        )


def test_margin_geometry_fails_closed_on_nonzero_rotate(tmp_path: Path) -> None:
    capture, stable, ledger = _geometry_evidence()
    pdf = tmp_path / "rotated.pdf"
    _write_geometry_pdf(pdf, stable, ledger, rotate=90)
    ledger_module = _load_ledger()

    with pytest.raises(ledger_module.MarginLedgerError, match="/Rotate must be 0"):
        ledger_module.verify_margin_layout(pdf, capture, stable, ledger)


def _first_margin_note_segment(instructions: list[Any]) -> list[Any]:
    segment: list[Any] = []
    collecting = False
    nested = 0
    for instruction in instructions:
        operands, operator = instruction
        operation = str(operator)
        if (
            not collecting
            and operation == "BDC"
            and operands
            and str(operands[0]) == "/NXMarginNote"
        ):
            collecting = True
            nested = 1
        if collecting:
            segment.append(instruction)
            if operation in {"BDC", "BMC"} and len(segment) > 1:
                nested += 1
            elif operation == "EMC":
                nested -= 1
                if nested == 0:
                    break
    assert segment and nested == 0
    return segment


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_xobject_marked_content_bijection_counts_before_collision(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "three-identical-anchors.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel}
\nxVersionProfesseurfalse
\begin{document}
\noindent Ancre commune\margeAppui{Premier appui rendu.}%
\margeAppui{Deuxième appui rendu.}%
\margeAppui{Troisième appui rendu.} Fin.
\newpage
Page de report disponible.
\end{document}
""",
        encoding="utf-8",
    )
    build = _run_private_passes(fixture, tmp_path / "build")
    expected_ids = [
        "nxm:eleve:appui:00000001",
        "nxm:eleve:appui:00000002",
        "nxm:eleve:appui:00000003",
    ]

    final_observation = build["observations"][-1]
    assert Counter(final_observation["captures"]) == Counter(expected_ids)
    assert len(final_observation["captures"]) == 3
    assert [note_id for note_id, _ in final_observation["forms"]] == expected_ids
    form_indices = [int(form_index) for _, form_index in final_observation["forms"]]
    assert form_indices == sorted(form_indices)
    counts = _marked_content_counts(build["pdf"])
    assert counts["NXMarginNote"] == 3, "compter le rendu avant la collision"

    ledger_module = _load_ledger()
    ledger = ledger_module.reconstruct_margin_ledger(
        build["pdf"], build["capture"], build["stable"], build["links"]
    )
    assert [note["note_id"] for note in ledger["notes"]] == expected_ids
    assert [note["note_count"] for note in ledger["notes"]] == [1, 1, 1]
    assert len({note["form_xref"] for note in ledger["notes"]}) == 3
    assert all(
        note["anchor_count"] == (1 if note["requires_marker"] else 0)
        for note in ledger["notes"]
    )
    assert all(
        left < right and top < bottom
        for left, top, right, bottom in (note["bbox_sp"] for note in ledger["notes"])
    )
    for index, note in enumerate(ledger["notes"]):
        for other in ledger["notes"][index + 1 :]:
            assert not _rectangles_overlap(note["bbox_sp"], other["bbox_sp"])

    extracted = subprocess.run(
        ["pdftotext", str(build["pdf"]), "-"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "nxm:" not in extracted


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_marked_content_anchor_only_for_displaced_and_reported_notes(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "marker-states.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel}
\nxVersionProfesseurfalse
\begin{document}
\noindent Note stable\nxMarginRailNote{appui}{Note sans repère.}
\nxMarginReserveRect{strong-shift}{%
  \dimexpr1in+\hoffset+\oddsidemargin+\textwidth+\marginparsep\relax}{9cm}{%
  \dimexpr1in+\hoffset+\oddsidemargin+\textwidth+\marginparsep+\marginparwidth\relax}{14cm}
\vspace*{6cm}
Note déplacée\nxMarginRailNote{commentaire}{Note fortement déplacée.}
\vspace*{8cm}
Note reportée\nxMarginRailNote{vocab}{%
  \rule{0pt}{9cm}Note reportée assez haute, avec une deuxième ligne, une troisième ligne,
  une quatrième ligne et une cinquième ligne dans la marge.}
\newpage
Page cible du report.\vfill
\end{document}
""",
        encoding="utf-8",
    )
    build = _run_private_passes(fixture, tmp_path / "build")
    expected_ids = [
        "nxm:eleve:appui:00000001",
        "nxm:eleve:commentaire:00000002",
        "nxm:eleve:vocab:00000003",
    ]

    assert len(build["capture"]["notes"]) == 3
    counts = _marked_content_counts(build["pdf"])
    assert counts["NXMarginNote"] == 3
    assert counts["NXMarginAnchor"] == 2

    ledger = _load_ledger().reconstruct_margin_ledger(
        build["pdf"], build["capture"], build["stable"], build["links"]
    )
    assert [note["note_id"] for note in ledger["notes"]] == expected_ids
    by_id = {note["note_id"]: note for note in ledger["notes"]}
    assert by_id[expected_ids[0]]["anchor_count"] == 0
    assert by_id[expected_ids[0]]["requires_marker"] is False
    assert by_id[expected_ids[1]]["anchor_count"] == 1
    assert by_id[expected_ids[1]]["requires_marker"] is True
    assert by_id[expected_ids[1]]["report_depth"] == 0
    assert by_id[expected_ids[2]]["anchor_count"] == 1
    assert by_id[expected_ids[2]]["requires_marker"] is True
    assert by_id[expected_ids[2]]["report_depth"] >= 1
    extracted = subprocess.run(
        ["pdftotext", str(build["pdf"]), "-"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "suite de la page 1" in extracted
    assert "page 0000" not in extracted


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_xobject_links_remap_uri_lines_and_internal_goto_without_duplicates(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "margin-links.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel}
\nxVersionProfesseurfalse
\usepackage{hyperref}
\begin{document}
\hypertarget{nx-ledger-target}{Destination interne}
\noindent Liens\nxMarginRailNote{appui}{%
  \href{https://example.invalid/nexus-margin-ledger}{%
    Un lien URI volontairement long qui occupe plusieurs lignes dans la marge.}%
  Puis un \hyperlink{nx-ledger-target}{lien interne}.}
\newpage
Page témoin.
\end{document}
""",
        encoding="utf-8",
    )
    build = _run_private_passes(fixture, tmp_path / "build")
    assert len(build["capture"]["notes"]) == 1
    assert _marked_content_counts(build["pdf"])["NXMarginNote"] == 1

    _load_ledger().reconstruct_margin_ledger(
        build["pdf"], build["capture"], build["stable"], build["links"]
    )
    links = _link_annotations(build["pdf"])
    uri_links = [link for link in links if "nexus-margin-ledger" in link["uri"]]
    goto_links = [
        link
        for link in links
        if link["action"] == "/GoTo" or "nx-ledger-target" in link["destination"]
    ]
    assert len(uri_links) >= 2, "un rectangle URI est requis par ligne couverte"
    assert len({link["rect"] for link in uri_links}) == len(uri_links)
    assert len(goto_links) == 1
    signatures = {
        (link["page"], link["rect"], link["action"], link["uri"], link["destination"])
        for link in links
    }
    assert len(signatures) == len(links), "aucune annotation lien dupliquée"


def test_ledger_rejects_pdf_adversarial_mutations(tmp_path: Path) -> None:
    ledger_module = _load_ledger()
    fixture = MANUAL_ROOT / "tests" / "fixtures" / "margin-ledger.valid.json"
    valid = json.loads(fixture.read_text(encoding="utf-8"))

    duplicate_note = deepcopy(valid)
    duplicate_note["notes"].append(deepcopy(duplicate_note["notes"][0]))
    with pytest.raises(ledger_module.MarginLedgerError):
        ledger_module.validate_ledger_document(duplicate_note)

    missing_anchor = deepcopy(valid)
    missing_anchor["notes"][1]["anchor_count"] = 0
    with pytest.raises(ledger_module.MarginLedgerError):
        ledger_module.validate_ledger_document(missing_anchor)

    invalid_bbox = deepcopy(valid)
    invalid_bbox["notes"][0]["bbox_sp"] = [10, 10, 10, 20]
    with pytest.raises(ledger_module.MarginLedgerError):
        ledger_module.validate_ledger_document(invalid_bbox)


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_pdf_adversaries_bbox_anchor_note_link_and_student_id_fail(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "adversarial-ledger.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel}
\nxVersionProfesseurfalse
\usepackage{hyperref}
\begin{document}
\hypertarget{nx-adversarial-target}{Destination interne}
\nxMarginReserveRect{strong-shift}{%
  \dimexpr1in+\hoffset+\oddsidemargin+\textwidth+\marginparsep\relax}{3cm}{%
  \dimexpr1in+\hoffset+\oddsidemargin+\textwidth+\marginparsep+\marginparwidth\relax}{12cm}
\vspace*{5cm}
Liens\nxMarginRailNote{appui}{%
  \href{https://example.invalid/nexus-adversarial}{%
    Lien URI multiligne pour la mutation des annotations de page.}%
  Puis \hyperlink{nx-adversarial-target}{le lien interne}.}
\newpage Page deux.
\end{document}
""",
        encoding="utf-8",
    )
    build = _run_private_passes(fixture, tmp_path / "build")
    ledger_module = _load_ledger()
    original = ledger_module.reconstruct_margin_ledger(
        build["pdf"], build["capture"], build["stable"], build["links"]
    )
    assert original["notes"][0]["anchor_count"] == 1
    assert len(_link_annotations(build["pdf"])) >= 3

    bbox_pdf = tmp_path / "mutated-bbox.pdf"
    with pikepdf.Pdf.open(build["pdf"]) as pdf:
        form = next(
            page.obj["/Resources"]["/XObject"][name]
            for page in pdf.pages
            for name in page.obj["/Resources"].get("/XObject", {})
            if page.obj["/Resources"]["/XObject"][name].get("/NXMarginID")
        )
        form["/BBox"][2] = float(form["/BBox"][2]) + 1
        pdf.save(bbox_pdf)

    missing_anchor_pdf = tmp_path / "mutated-missing-anchor.pdf"
    with pikepdf.Pdf.open(build["pdf"]) as pdf:
        page = pdf.pages[0]
        instructions = list(pikepdf.parse_content_stream(page))
        _replace_page_instructions(pdf, page, _without_first_margin_anchor(instructions))
        pdf.save(missing_anchor_pdf)

    anchor_order_pdf = tmp_path / "mutated-anchor-order.pdf"
    with pikepdf.Pdf.open(build["pdf"]) as pdf:
        page = pdf.pages[0]
        instructions = list(pikepdf.parse_content_stream(page))
        mutated = _with_first_margin_anchor_property(instructions, "/Order", 999)
        _replace_page_instructions(pdf, page, mutated)
        pdf.save(anchor_order_pdf)

    with pytest.raises(ledger_module.MarginLedgerError):
        ledger_module.reconstruct_margin_ledger(
            anchor_order_pdf, build["capture"], build["stable"], build["links"]
        )

    malformed_anchor_pdfs: list[Path] = []
    for suffix, key, value in (
        ("order-string", "/Order", pikepdf.String("1")),
        ("order-multiple", "/Order", pikepdf.Array([1, 999])),
        ("unexpected-key", "/Unexpected", 1),
    ):
        mutation = tmp_path / f"mutated-anchor-{suffix}.pdf"
        with pikepdf.Pdf.open(build["pdf"]) as pdf:
            page = pdf.pages[0]
            instructions = list(pikepdf.parse_content_stream(page))
            mutated = _with_first_margin_anchor_property(instructions, key, value)
            _replace_page_instructions(pdf, page, mutated)
            pdf.save(mutation)
        malformed_anchor_pdfs.append(mutation)

    for mutation in malformed_anchor_pdfs:
        with pytest.raises(ledger_module.MarginLedgerError):
            ledger_module.reconstruct_margin_ledger(
                mutation, build["capture"], build["stable"], build["links"]
            )

    duplicate_note_pdf = tmp_path / "mutated-duplicate-note.pdf"
    with pikepdf.Pdf.open(build["pdf"]) as pdf:
        page = pdf.pages[0]
        instructions = list(pikepdf.parse_content_stream(page))
        duplicated = instructions + _first_margin_note_segment(instructions)
        _replace_page_instructions(pdf, page, duplicated)
        pdf.save(duplicate_note_pdf)

    duplicate_link_pdf = tmp_path / "mutated-duplicate-link.pdf"
    with pikepdf.Pdf.open(build["pdf"]) as pdf:
        page = pdf.pages[0]
        annotations = page.obj["/Annots"]
        annotations.append(annotations[0])
        pdf.save(duplicate_link_pdf)

    internal_id_pdf = tmp_path / "mutated-internal-id.pdf"
    with pikepdf.Pdf.open(build["pdf"]) as pdf:
        page = pdf.pages[0]
        fonts = page.obj["/Resources"]["/Font"]
        font_name = next(iter(fonts.keys()))
        injected = pikepdf.Stream(
            pdf,
            f"BT {font_name} 10 Tf 72 72 Td (1SPE-INJECTED-ID) Tj ET".encode(),
        )
        existing = page.obj["/Contents"]
        page.obj["/Contents"] = pikepdf.Array([existing, injected])
        pdf.save(internal_id_pdf)

    for mutation in (
        bbox_pdf,
        missing_anchor_pdf,
        duplicate_note_pdf,
        duplicate_link_pdf,
        internal_id_pdf,
    ):
        with pytest.raises(ledger_module.MarginLedgerError):
            ledger_module.reconstruct_margin_ledger(
                mutation, build["capture"], build["stable"], build["links"]
            )

    assert ledger_module.reconstruct_margin_ledger(
        build["pdf"], build["capture"], build["stable"], build["links"]
    ) == original


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_pdf_bijection_rejects_independent_mutations(tmp_path: Path) -> None:
    fixture = tmp_path / "complete-bijection-adversaries.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel}
\nxVersionProfesseurfalse
\usepackage{hyperref}
\begin{document}
\hypertarget{nx-complete-target}{Destination interne}
\noindent Ancre commune\nxMarginRailNote{appui}{%
  \href{https://example.invalid/nexus-complete-bijection}{%
    Lien URI multiligne pour la mutation des annotations de page.}%
  Puis \hyperlink{nx-complete-target}{lien interne}.}%
\nxMarginRailNote{commentaire}{Deuxième note au même ancrage.}%
\nxMarginRailNote{vocab}{Troisième note au même ancrage.} Fin.
\newpage Page cible disponible.
\end{document}
""",
        encoding="utf-8",
    )
    build = _run_private_passes(fixture, tmp_path / "build")
    ledger_module = _load_ledger()
    original_bytes = build["pdf"].read_bytes()
    original = ledger_module.reconstruct_margin_ledger(
        build["pdf"], build["capture"], build["stable"], build["links"]
    )
    marker_id = next(note["note_id"] for note in original["notes"] if note["requires_marker"])
    assert len(original["notes"]) == 3
    assert _link_annotations(build["pdf"])

    mutations: dict[str, Path] = {}

    marker_pdf = tmp_path / "mutation-1-marker-self-justified.pdf"
    with pikepdf.Pdf.open(build["pdf"]) as pdf:
        page = pdf.pages[0]
        instructions = list(pikepdf.parse_content_stream(page))
        instructions = _with_margin_note_property(
            instructions, marker_id, "/RequiresMarker", False
        )
        instructions = _without_first_margin_anchor(instructions)
        _replace_page_instructions(pdf, page, instructions)
        pdf.save(marker_pdf)
    mutations["requires-marker-self-justified"] = marker_pdf

    moved_anchor_pdf = tmp_path / "mutation-2-anchor-wrong-page.pdf"
    with pikepdf.Pdf.open(build["pdf"]) as pdf:
        origin_page = pdf.pages[0]
        target_page = pdf.pages[1]
        origin_instructions = list(pikepdf.parse_content_stream(origin_page))
        anchor_segment = _first_margin_anchor_segment(origin_instructions)
        _replace_page_instructions(
            pdf, origin_page, _without_first_margin_anchor(origin_instructions)
        )
        target_instructions = list(pikepdf.parse_content_stream(target_page))
        _replace_page_instructions(pdf, target_page, target_instructions + anchor_segment)
        pdf.save(moved_anchor_pdf)
    mutations["anchor-wrong-page"] = moved_anchor_pdf

    missing_links_pdf = tmp_path / "mutation-3-links-deleted.pdf"
    with pikepdf.Pdf.open(build["pdf"]) as pdf:
        for page in pdf.pages:
            annotations = [
                item
                for item in page.obj.get("/Annots", [])
                if str(item.get("/Subtype", "")) != "/Link"
            ]
            page.obj["/Annots"] = pikepdf.Array(annotations)
        pdf.save(missing_links_pdf)
    mutations["links-deleted"] = missing_links_pdf

    translated_bbox_pdf = tmp_path / "mutation-4-bbox-translated.pdf"
    with pikepdf.Pdf.open(build["pdf"]) as pdf:
        _, form = _first_margin_form(pdf)
        for index in range(4):
            form["/BBox"][index] = float(form["/BBox"][index]) + 1
        pdf.save(translated_bbox_pdf)
    mutations["bbox-translated"] = translated_bbox_pdf

    orphan_form_pdf = tmp_path / "mutation-5-orphan-form.pdf"
    with pikepdf.Pdf.open(build["pdf"]) as pdf:
        xobjects, form = _first_margin_form(pdf)
        orphan = pikepdf.Stream(pdf, form.read_bytes())
        for key, value in form.items():
            if str(key) not in {"/Length", "/Filter", "/DecodeParms"}:
                orphan[key] = value
        xobjects["/NXMarginOrphan"] = orphan
        pdf.save(orphan_form_pdf)
    mutations["orphan-form"] = orphan_form_pdf

    reversed_notes_pdf = tmp_path / "mutation-6-note-order.pdf"
    with pikepdf.Pdf.open(build["pdf"]) as pdf:
        page = pdf.pages[0]
        instructions = list(pikepdf.parse_content_stream(page))
        _replace_page_instructions(pdf, page, _reverse_margin_note_segments(instructions))
        pdf.save(reversed_notes_pdf)
    mutations["note-order"] = reversed_notes_pdf

    bogus_form_tag_pdf = tmp_path / "mutation-7-bogus-form-tag.pdf"
    with pikepdf.Pdf.open(build["pdf"]) as pdf:
        _, form = _first_margin_form(pdf)
        form.write(b"/NXMarginBogus BMC EMC\n" + form.read_bytes())
        pdf.save(bogus_form_tag_pdf)
    mutations["bogus-form-tag"] = bogus_form_tag_pdf

    zero_matrix_pdf = tmp_path / "mutation-8-zero-matrix.pdf"
    with pikepdf.Pdf.open(build["pdf"]) as pdf:
        _, form = _first_margin_form(pdf)
        form["/Matrix"] = pikepdf.Array([0, 0, 0, 0, 0, 0])
        pdf.save(zero_matrix_pdf)
    mutations["zero-matrix"] = zero_matrix_pdf

    chained_uri_pdf = tmp_path / "mutation-9-chained-uri-action.pdf"
    with pikepdf.Pdf.open(build["pdf"]) as pdf:
        mutated = False
        for page in pdf.pages:
            for annotation in page.obj.get("/Annots", []):
                action = annotation.get("/A")
                if action is not None and str(action.get("/S", "")) == "/URI":
                    action["/Next"] = pikepdf.Dictionary(
                        {
                            "/S": pikepdf.Name("/JavaScript"),
                            "/JS": pikepdf.String("app.alert('mutation')"),
                        }
                    )
                    mutated = True
                    break
            if mutated:
                break
        assert mutated
        pdf.save(chained_uri_pdf)
    mutations["chained-uri-action"] = chained_uri_pdf

    reversed_anchors_pdf = tmp_path / "mutation-10-anchor-order.pdf"
    with pikepdf.Pdf.open(build["pdf"]) as pdf:
        page = pdf.pages[0]
        instructions = list(pikepdf.parse_content_stream(page))
        _replace_page_instructions(pdf, page, _reverse_margin_anchor_segments(instructions))
        pdf.save(reversed_anchors_pdf)
    mutations["anchor-order"] = reversed_anchors_pdf

    additional_action_pdf = tmp_path / "mutation-11-annotation-aa.pdf"
    with pikepdf.Pdf.open(build["pdf"]) as pdf:
        mutated = False
        for page in pdf.pages:
            for annotation in page.obj.get("/Annots", []):
                action = annotation.get("/A")
                if action is not None and str(action.get("/S", "")) == "/URI":
                    annotation["/AA"] = pikepdf.Dictionary(
                        {
                            "/E": pikepdf.Dictionary(
                                {
                                    "/S": pikepdf.Name("/JavaScript"),
                                    "/JS": pikepdf.String("app.alert('annotation')"),
                                }
                            )
                        }
                    )
                    mutated = True
                    break
            if mutated:
                break
        assert mutated
        pdf.save(additional_action_pdf)
    mutations["annotation-aa"] = additional_action_pdf

    intersecting_javascript_pdf = tmp_path / "mutation-12-intersecting-javascript.pdf"
    with pikepdf.Pdf.open(build["pdf"]) as pdf:
        annotation = pikepdf.Dictionary(
            {
                "/Type": pikepdf.Name("/Annot"),
                "/Subtype": pikepdf.Name("/Link"),
                "/Rect": pikepdf.Array([0, 700, 520, 770]),
                "/A": pikepdf.Dictionary(
                    {
                        "/S": pikepdf.Name("/JavaScript"),
                        "/JS": pikepdf.String("app.alert('intersection')"),
                    }
                ),
            }
        )
        pdf.pages[0].obj["/Annots"].append(pdf.make_indirect(annotation))
        pdf.save(intersecting_javascript_pdf)
    mutations["intersecting-javascript"] = intersecting_javascript_pdf

    extra_page_pdf = tmp_path / "mutation-13-extra-page.pdf"
    with pikepdf.Pdf.open(build["pdf"]) as pdf:
        page = pdf.add_blank_page(page_size=(595, 842))
        annotation = pikepdf.Dictionary(
            {
                "/Type": pikepdf.Name("/Annot"),
                "/Subtype": pikepdf.Name("/Link"),
                "/Rect": pikepdf.Array([0, 700, 520, 770]),
                "/A": pikepdf.Dictionary(
                    {
                        "/S": pikepdf.Name("/JavaScript"),
                        "/JS": pikepdf.String("app.alert('extra-page')"),
                    }
                ),
            }
        )
        page.obj["/Annots"] = pikepdf.Array([pdf.make_indirect(annotation)])
        pdf.save(extra_page_pdf)
    mutations["extra-page"] = extra_page_pdf

    accepted: list[str] = []
    for name, mutation in mutations.items():
        _assert_qpdf_valid(mutation)
        try:
            ledger_module.reconstruct_margin_ledger(
                mutation, build["capture"], build["stable"], build["links"]
            )
        except ledger_module.MarginLedgerError:
            continue
        accepted.append(name)

    assert build["pdf"].read_bytes() == original_bytes
    assert ledger_module.reconstruct_margin_ledger(
        build["pdf"], build["capture"], build["stable"], build["links"]
    ) == original
    assert accepted == [], f"mutations PDF acceptées: {accepted}"


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_bijection_ledger_bytes_ignore_private_run_nonce(tmp_path: Path) -> None:
    fixture = tmp_path / "deterministic-ledger.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel}
\nxVersionProfesseurfalse
\begin{document}
Texte\margeAppui{Note déterministe.}
\newpage Page deux.
\end{document}
""",
        encoding="utf-8",
    )
    first = _run_private_passes(
        fixture,
        tmp_path / "first",
        run_nonce="11111111111111111111111111111111",
    )
    second = _run_private_passes(
        fixture,
        tmp_path / "second",
        run_nonce="22222222222222222222222222222222",
    )
    ledger_module = _load_ledger()
    first_ledger = ledger_module.reconstruct_margin_ledger(
        first["pdf"], first["capture"], first["stable"], first["links"]
    )
    second_ledger = ledger_module.reconstruct_margin_ledger(
        second["pdf"], second["capture"], second["stable"], second["links"]
    )
    contract = _load_contract()

    assert first["stable_bytes"] == second["stable_bytes"]
    assert contract.canonical_digest(
        contract.canonical_capture_projection(first["capture"])
    ) == contract.canonical_digest(
        contract.canonical_capture_projection(second["capture"])
    )
    assert contract.canonical_json_bytes(first_ledger) == contract.canonical_json_bytes(
        second_ledger
    )
