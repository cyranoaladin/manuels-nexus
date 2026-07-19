#!/usr/bin/env python3
"""Compile and inspect the isolated v5 validation mock-up."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import unicodedata
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
