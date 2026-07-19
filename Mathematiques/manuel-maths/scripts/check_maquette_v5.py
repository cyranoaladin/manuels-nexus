#!/usr/bin/env python3
"""Compile and inspect the isolated v5 validation mock-up."""

from __future__ import annotations

import argparse
import hashlib
import math
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

from build_maquette_v5 import MetaError, load_manifest


PAGE_13_REFERENCE_SHA256 = (
    "ea1750a0f56ecd3b2761614709f96f9b267569ece45bc4103aa11dc2007dacf1"
)


class AcceptanceError(RuntimeError):
    """Report compilation or PDF acceptance failures."""


def normalize_text(value: str) -> str:
    """Normalize extracted PDF text for stable content comparisons."""
    normalized = unicodedata.normalize("NFKC", value).replace("\ufeff", "")
    normalized = normalized.replace("’", "'").replace("‘", "'")
    return " ".join(normalized.split())


def page_text_is_empty(value: str) -> bool:
    return normalize_text(value) == ""


def required_strings_present(value: str, required: list[str]) -> bool:
    normalized = normalize_text(value)
    return all(normalize_text(expected) in normalized for expected in required)


def assert_no_two_column_marginnotes(log: str) -> None:
    marker = "NEXUS-V5-MARGINNOTE-COLUMNS-EMITTED"
    if marker in log:
        raise AcceptanceError(marker)


def assert_no_compact_correction_overfull(log: str) -> None:
    """Reject horizontal collisions inside the p.15 three-column block."""
    start = "NEXUS-V5-COMPACT-CORRECTIONS-START"
    end = "NEXUS-V5-COMPACT-CORRECTIONS-END"
    if start not in log or end not in log:
        return
    compact_log = log[log.index(start) : log.index(end)]
    if "Overfull \\hbox" in compact_log:
        raise AcceptanceError("débordement horizontal des corrigés compacts")


def assert_diagnostics_log_clean(log: str, expected_passes: int = 3) -> None:
    """Require one balanced, overflow-free diagnostics interval per TeX pass."""
    start = "NEXUS-V5-DIAGNOSTICS-START"
    end = "NEXUS-V5-DIAGNOSTICS-END"
    marker_pattern = re.compile(r"NEXUS-V5-DIAGNOSTICS-[A-Z][A-Z0-9_-]*")
    markers = list(marker_pattern.finditer(log))
    expected_sequence = [
        marker for _ in range(expected_passes) for marker in (start, end)
    ]
    if [marker.group(0) for marker in markers] != expected_sequence:
        raise AcceptanceError("marqueurs diagnostics absents, parasites ou déséquilibrés")

    for pass_number in range(expected_passes):
        interval_start = markers[2 * pass_number].end()
        interval_end = markers[2 * pass_number + 1].start()
        interval = log[interval_start:interval_end]
        if "Overfull \\hbox" in interval or "Overfull \\vbox" in interval:
            raise AcceptanceError(
                f"débordement dans les diagnostics, passe {pass_number + 1}"
            )


def assert_diagnostics_bbox_layout(xhtml: str) -> None:
    """Validate the semantic regions and geometry of diagnostics page XHTML."""
    xml = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", xhtml)
    try:
        document = ET.fromstring(xml)
    except (ET.ParseError, ValueError) as exc:
        raise AcceptanceError(f"XHTML diagnostics invalide: {exc}") from exc

    lines: list[dict[str, object]] = []
    for element in document.findall(".//{*}line"):
        text = normalize_text(" ".join(element.itertext()))
        if not text:
            continue
        try:
            line = {
                "text": text,
                "x_min": float(element.attrib["xMin"]),
                "y_min": float(element.attrib["yMin"]),
                "x_max": float(element.attrib["xMax"]),
                "y_max": float(element.attrib["yMax"]),
            }
        except (KeyError, ValueError) as exc:
            raise AcceptanceError("boîte de ligne diagnostics invalide") from exc
        coordinates = [
            float(line[coordinate])
            for coordinate in ("x_min", "y_min", "x_max", "y_max")
        ]
        if not all(math.isfinite(coordinate) for coordinate in coordinates):
            raise AcceptanceError("coordonnée diagnostics non finie")
        if (
            float(line["x_min"]) > float(line["x_max"])
            or float(line["y_min"]) > float(line["y_max"])
        ):
            raise AcceptanceError("boîte de ligne diagnostics incohérente")
        lines.append(line)

    def anchor_index(label: str, *, prefix: bool = False) -> int:
        matches = [
            index
            for index, line in enumerate(lines)
            if (
                str(line["text"]).startswith(label)
                if prefix
                else label in str(line["text"])
            )
        ]
        if len(matches) != 1:
            raise AcceptanceError(f"ancre diagnostics invalide: {label}")
        return matches[0]

    title_index = anchor_index("Correction et diagnostics")
    responses_index = anchor_index("Réponses correctes")
    score_index = anchor_index("Score", prefix=True)
    if not title_index < responses_index < score_index:
        raise AcceptanceError("ordre des régions diagnostics invalide")

    def is_header_or_footer(line: dict[str, object]) -> bool:
        text = str(line["text"])
        return (
            text == "Corrigés"
            or text == "NEXUS RÉUSSITE"
            or (re.fullmatch(r"\d+", text) is not None and float(line["y_min"]) > 768.0)
        )

    for line in lines:
        if is_header_or_footer(line):
            continue
        if (
            float(line["x_min"]) < 56.0
            or float(line["x_max"]) > 459.5
            or float(line["y_max"]) > 768.0
        ):
            raise AcceptanceError(f"ligne hors corps diagnostics: {line['text']}")

    table_lines = lines[title_index + 1 : responses_index]
    response_lines = lines[responses_index + 1 : score_index]
    score_lines = [
        line for line in lines[score_index:] if not is_header_or_footer(line)
    ]
    question_numbers = [
        int(match.group(1))
        for line in table_lines
        for match in re.finditer(r"\bQ(1[0-5]|[1-9])\b", str(line["text"]))
    ]
    if len(question_numbers) != 15 or set(question_numbers) != set(range(1, 16)):
        raise AcceptanceError("lignes Q1–Q15 diagnostics incomplètes")

    diagnostics = [
        line
        for line in table_lines
        if re.match(r"^[ACD]\s*:", str(line["text"])) is not None
    ]
    if len(diagnostics) != 45:
        raise AcceptanceError(
            f"diagnostics distracteurs: attendu 45, obtenu {len(diagnostics)}"
        )
    final_diagnostic = [
        line for line in diagnostics if "placement de la virgule" in str(line["text"])
    ]
    if len(final_diagnostic) != 1:
        raise AcceptanceError("dernier diagnostic absent: placement de la virgule")

    grid_numbers = [
        int(match.group(1))
        for line in response_lines
        for match in re.finditer(r"\bQ(1[0-5]|[1-9])\b", str(line["text"]))
    ]
    if len(grid_numbers) != 15 or set(grid_numbers) != set(range(1, 16)):
        raise AcceptanceError("grille Q1–Q15 incomplète")
    final_grid_lines = [
        line
        for line in response_lines
        if any(
            int(match.group(1)) in range(11, 16)
            for match in re.finditer(
                r"\bQ(1[0-5]|[1-9])\b", str(line["text"])
            )
        )
    ]
    if not final_grid_lines:
        raise AcceptanceError("lignes Q11–Q15 absentes")

    responses_anchor = lines[responses_index]
    score_anchor = lines[score_index]
    title_anchor = lines[title_index]
    if any(
        float(line["y_min"]) < float(title_anchor["y_max"])
        or float(line["y_max"]) > float(responses_anchor["y_min"])
        for line in table_lines
    ):
        raise AcceptanceError("ligne hors région tableau diagnostics")
    if any(
        float(line["y_min"]) < float(responses_anchor["y_max"])
        or float(line["y_max"]) > float(score_anchor["y_min"])
        for line in response_lines
    ):
        raise AcceptanceError("ligne hors région réponses diagnostics")
    if any(
        float(line["y_min"]) < float(score_anchor["y_max"])
        for line in score_lines[1:]
    ):
        raise AcceptanceError("ligne hors région score diagnostics")

    def assert_region_rectangles_disjoint(
        region_name: str, region_lines: list[dict[str, object]]
    ) -> None:
        tolerance = 0.25
        for index, first in enumerate(region_lines):
            for second in region_lines[index + 1 :]:
                horizontal_overlap = min(
                    float(first["x_max"]), float(second["x_max"])
                ) - max(float(first["x_min"]), float(second["x_min"]))
                vertical_overlap = min(
                    float(first["y_max"]), float(second["y_max"])
                ) - max(float(first["y_min"]), float(second["y_min"]))
                if horizontal_overlap > tolerance and vertical_overlap > tolerance:
                    raise AcceptanceError(
                        f"collision interne dans la région {region_name} diagnostics"
                    )

    assert_region_rectangles_disjoint("tableau", table_lines)
    assert_region_rectangles_disjoint("réponses", response_lines)
    assert_region_rectangles_disjoint("score", score_lines)

    table_bottom = max(float(line["y_max"]) for line in table_lines)
    if float(responses_anchor["y_min"]) - table_bottom < 6.0:
        raise AcceptanceError("collision tableau diagnostics / réponses correctes")
    grid_top = min(float(line["y_min"]) for line in response_lines)
    if grid_top < float(responses_anchor["y_max"]):
        raise AcceptanceError("collision réponses correctes / grille diagnostics")
    grid_bottom = max(float(line["y_max"]) for line in response_lines)
    if float(score_anchor["y_min"]) - grid_bottom < 6.0:
        raise AcceptanceError("collision grille diagnostics / score")


def run_checked(
    command: list[str], cwd: Path, *, meta_exit_code: bool = False
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise AcceptanceError(f"commande impossible: {command[0]}: {exc}") from exc
    if meta_exit_code and result.returncode == 2:
        detail = (result.stderr or result.stdout).strip()
        if detail.startswith("META V5:"):
            detail = detail.removeprefix("META V5:").strip()
        raise MetaError(detail or "générateur META en échec")
    if result.returncode != 0:
        raise AcceptanceError(
            f"commande en échec ({result.returncode}): {' '.join(command)}"
        )
    return result


def _assert_clean_tex_output(output: str) -> None:
    if "Undefined control sequence" in output:
        raise AcceptanceError("Undefined control sequence")
    if re.search(r"(?m)^!", output):
        raise AcceptanceError("ligne d'erreur TeX")
    if "Missing character" in output:
        raise AcceptanceError("glyphe manquant")
    assert_no_two_column_marginnotes(output)
    assert_no_compact_correction_overfull(output)


def _assert_no_undefined_references(output: str) -> None:
    if re.search(r"undefined (?:references?|citations?)", output, re.IGNORECASE):
        raise AcceptanceError("références indéfinies")
    if re.search(r"Reference .* undefined", output, re.IGNORECASE):
        raise AcceptanceError("référence indéfinie")
    if re.search(r"Citation (?:'.*?'|`.*?'|\S+).* undefined", output, re.IGNORECASE):
        raise AcceptanceError("citation indéfinie")


def compile_maquette(manifest_path: Path, root: Path) -> dict[str, str]:
    """Generate references, run three TeX passes, then extract PDF metadata/text."""
    try:
        safe_root = root.resolve(strict=True)
    except OSError as exc:
        raise AcceptanceError(f"racine absente: {root}") from exc
    try:
        manifest = manifest_path.resolve(strict=True)
    except OSError as exc:
        raise MetaError(f"manifest absent: {manifest_path}") from exc
    try:
        manifest.relative_to(safe_root)
    except ValueError as exc:
        raise AcceptanceError("manifeste hors racine") from exc

    generator = safe_root / "scripts" / "build_maquette_v5.py"
    output_dir = Path("build/maquette-v5")
    run_checked(
        [
            "python3",
            str(generator),
            "--manifest",
            str(manifest),
            "--output",
            str(output_dir / "renvois.tex"),
        ],
        safe_root,
        meta_exit_code=True,
    )

    tex_command = [
        "lualatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={output_dir}",
        str(output_dir / "maquette.tex"),
    ]
    tex_output: list[str] = []
    for _ in range(3):
        result = run_checked(tex_command, safe_root)
        combined = result.stdout + result.stderr
        _assert_clean_tex_output(combined)
        tex_output.append(combined)
    _assert_no_undefined_references(tex_output[-1])

    pdf = output_dir / "maquette.pdf"
    pdfinfo = run_checked(["pdfinfo", str(pdf)], safe_root)
    extracted = run_checked(["pdftotext", "-layout", str(pdf), "-"], safe_root)
    if "??" in extracted.stdout:
        raise AcceptanceError("?? dans le texte PDF extrait")
    return {
        "log": "".join(tex_output),
        "pdfinfo": pdfinfo.stdout,
        "text": extracted.stdout,
    }


def _page_text(pdf: Path, page: int, root: Path, *, layout: bool = False) -> str:
    command = ["pdftotext"]
    if layout:
        command.append("-layout")
    command.extend(["-f", str(page), "-l", str(page), str(pdf), "-"])
    return run_checked(command, root).stdout


def _assert_page_count(pdfinfo: str, expected: int) -> None:
    match = re.search(r"(?m)^Pages:\s+(\d+)\s*$", pdfinfo)
    if match is None or int(match.group(1)) != expected:
        actual = match.group(1) if match is not None else "absent"
        raise AcceptanceError(f"pages: attendu {expected}, obtenu {actual}")


def _render_validation_pngs(pdf: Path, root: Path, expected_pages: int) -> list[Path]:
    destination = root / "validations/v5"
    destination.mkdir(parents=True, exist_ok=True)
    for stale in destination.glob("page-[0-9][0-9].png"):
        stale.unlink()
    run_checked(
        ["pdftoppm", "-png", "-r", "150", str(pdf), str(destination / "page")],
        root,
    )
    expected = [destination / f"page-{page:02d}.png" for page in range(1, expected_pages + 1)]
    actual = sorted(destination.glob("page-[0-9][0-9].png"))
    if actual != expected:
        raise AcceptanceError("jeu de PNG 150 dpi incomplet")
    for image in expected:
        dimensions = run_checked(
            ["identify", "-format", "%w %h", str(image)], root
        ).stdout.strip()
        if dimensions != "1241 1754":
            raise AcceptanceError(f"dimensions PNG invalides: {image.name}: {dimensions}")
    return expected


def accept_maquette(
    manifest: dict, compiled: dict[str, str], root: Path
) -> str:
    """Apply the page-level v5 acceptance contract and render validation PNGs."""
    expected_pages = manifest["expected_pages"]
    _assert_page_count(compiled["pdfinfo"], expected_pages)
    assert_no_two_column_marginnotes(compiled["log"])

    pdf = root / manifest["output_pdf"]
    if not pdf.is_file():
        raise AcceptanceError(f"PDF absent: {pdf}")
    raw_pages = {
        page: _page_text(pdf, page, root, layout=True)
        for page in range(1, expected_pages + 1)
    }
    pages = {page: normalize_text(text) for page, text in raw_pages.items()}

    for page in manifest["blank_pages"]:
        if not page_text_is_empty(raw_pages[page]):
            raise AcceptanceError(f"page blanche {page} non vide")

    expected_rubrics = {
        1: "OUVERTURE",
        2: "Cours",
        3: "Cours",
        4: "Cours",
        5: "Cours",
        7: "Méthodes",
        8: "Méthodes",
        9: "Exercices",
        10: "Exercices",
        11: "Auto-évaluation",
        12: "Auto-évaluation",
        13: "Corrigés",
        15: "Corrigés",
    }
    for page, rubric in expected_rubrics.items():
        if normalize_text(rubric) not in pages[page]:
            raise AcceptanceError(f"rubrique {rubric} absente p. {page}")

    opening = raw_pages[1]
    for label, folio in manifest["chapter_toc"]:
        if re.search(
            rf"(?m)^\s*{re.escape(label)}\b.*\b{folio}\s*$", opening
        ) is None:
            raise AcceptanceError(f"sommaire absent: {label} {folio}")

    combined = " ".join(pages.values())
    if not required_strings_present(combined, manifest["required_strings"]):
        raise AcceptanceError("renvoi généré absent")
    for object_id in manifest["exercise_order"]:
        if object_id in combined:
            raise AcceptanceError(f"ID technique visible: {object_id}")
    page_counts = manifest["exercise_page_counts"]
    for page in (9, 10):
        actual = pages[page].count("Corrigé p. 15")
        expected = page_counts[str(page)]
        if actual != expected:
            raise AcceptanceError(
                f"badges p. {page}: attendu {expected}, obtenu {actual}"
            )
    if "REPÈRES DE RÉSOLUTION" not in pages[7] or "À VOUS DE JOUER" not in pages[8]:
        raise AcceptanceError("méthode appariée incomplète")
    for question in range(1, 9):
        if f"[Q{question}]" not in pages[11] or f"[Q{question}]" in pages[12]:
            raise AcceptanceError(f"QCM mal paginé: Q{question}")
    for question in range(9, 16):
        if f"[Q{question}]" in pages[11] or f"[Q{question}]" not in pages[12]:
            raise AcceptanceError(f"QCM mal paginé: Q{question}")
    if pages[15].count("Corrigés") != 2:
        raise AcceptanceError("titre Corrigés dupliqué ou absent")
    if re.search(r"Corrigé[ \t]{1,3}[0-9]+\s*\.", raw_pages[15]) is not None:
        raise AcceptanceError("numéro de corrigé désynchronisé p. 15")

    images = _render_validation_pngs(pdf, root, expected_pages)
    reference = root / "validations/v5-it1/page-13.png"
    if not reference.is_file():
        raise AcceptanceError("référence it1 p.13 absente")
    reference_sha = hashlib.sha256(reference.read_bytes()).hexdigest()
    if reference_sha != PAGE_13_REFERENCE_SHA256:
        raise AcceptanceError("référence it1 p.13 altérée")
    comparison = run_checked(
        ["compare", "-metric", "AE", str(reference), str(images[12]), "null:"],
        root,
    )
    if comparison.stderr.strip() != "0":
        raise AcceptanceError(f"page 13 modifiée: AE={comparison.stderr.strip()}")

    return (
        "MAQUETTE V5: PASS — 15 pages; blanches 6,14; "
        "renvois 2/2; marginnote colonnes 0"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args(argv)
    root = Path.cwd()

    try:
        manifest = load_manifest(args.manifest, root)
    except MetaError as exc:
        print(f"META V5: {exc}", file=sys.stderr)
        return 2
    try:
        compiled = compile_maquette(args.manifest, root)
        summary = accept_maquette(manifest, compiled, root)
    except MetaError as exc:
        print(f"META V5: {exc}", file=sys.stderr)
        return 2
    except AcceptanceError as exc:
        print(f"MAQUETTE V5: {exc}", file=sys.stderr)
        return 1
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
