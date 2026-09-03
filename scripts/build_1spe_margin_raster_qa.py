#!/usr/bin/env python3
"""Les 3 990 notes de marge, regardées une par une sur la page rendue.

Le contrat des marges est vérifié ailleurs, et complètement : identité,
placement, géométrie physique, liens, écart de six points, confinement au rail.
`margin_ledger.verify_margin_layout` le fait sur le PDF livré, et ce module ne
le refait pas.

Il regarde ce que ce contrôle-là ne peut pas voir. Une note peut être placée au
bon endroit, du bon côté, dans le bon rectangle, et ne rien laisser sur la
page : c'est exactement ce qui s'est produit pendant toute une campagne, quand
le compositeur capturait ses notes sans jamais les dessiner. Le Form XObject
existait, sa boîte était juste, son contenu était vide d'encre.

La mesure est donc celle de la TRACE : la zone de chaque note est rendue, et
l'on compte la part de ses pixels qui s'écartent de la couleur dominante. Une
note invisible n'en laisse aucune. Le seuil est le même que pour les
ouvertures, et le minimum réellement observé est publié à chaque construction
pour qu'il reste vérifiable.

L'inventaire lu est celui que la construction PUBLIE à côté du PDF : ce sont
les notes du manuel livré, pas celles d'un document recompilé pour l'occasion.

Métriques bloquantes : `MARGIN_NOTES_WITHOUT_TRACE`,
`MARGIN_NOTES_OUTSIDE_THEIR_PAGE`, `MARGIN_NOTES_NOT_INSPECTED`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT, relative  # noqa: E402


def _label(path: Path) -> str:
    """Chemin lisible, y compris pour une sonde fabriquée hors du dépôt."""

    try:
        return relative(path)
    except ValueError:
        return str(path)


JSON_TARGET = ROOT / "audit/1SPE_MARGIN_RASTER_QA.json"
MD_TARGET = ROOT / "audit/1SPE_MARGIN_RASTER_QA.md"
GENERATED_BY = "scripts/build_1spe_margin_raster_qa.py"

BUILD = ROOT / "Mathematiques/manuel-maths/build/MANUEL_1SPE"
VARIANTS = ("eleve", "professeur")

RASTER_DPI = 300
# Le plancher sépare « de l'encre » de « pas d'encre » -- pas « beaucoup » de
# « peu ». Une note invisible marque exactement 0 ; la note la moins encrée du
# corpus, un identifiant professeur court dans un rail large, en marque environ
# 2,8 %. Un pour cent tient donc entre les deux, et le minimum réellement
# observé est publié par classe à chaque construction pour que cet écart reste
# vérifiable plutôt que supposé.
MINIMUM_INK_COVERAGE = 0.01
SP_PER_BP = 65536 * 7227 / 7200


class MarginRasterError(RuntimeError):
    """Une preuve manque : les notes ne peuvent pas être regardées."""


def _reject(message: str) -> None:
    raise MarginRasterError(message)


def _fitz() -> Any:
    try:
        import fitz
    except ModuleNotFoundError:  # pragma: no cover - dependance de gate
        _reject("PyMuPDF (fitz) est requis")
    return fitz


def ink_coverage(page: Any, box: Any) -> float:
    """La part des pixels d'une zone qui s'écartent de sa couleur dominante."""

    pixmap = page.get_pixmap(dpi=RASTER_DPI, clip=box, annots=False)
    samples = pixmap.samples
    stride = pixmap.n
    counts: dict[bytes, int] = {}
    total = 0
    for offset in range(0, len(samples), stride):
        pixel = bytes(samples[offset : offset + stride])
        counts[pixel] = counts.get(pixel, 0) + 1
        total += 1
    if total == 0:
        return 0.0
    return 1.0 - max(counts.values()) / total


def _ledger_modules() -> tuple[Any, Any]:
    """Le ledger et le contrat, chargés là où ils vivent."""

    import importlib.util  # noqa: PLC0415

    modules = []
    for name, relative_path in (
        ("margin_contract_raster", "scripts/margin_contract.py"),
        ("margin_ledger_raster", "scripts/margin_ledger.py"),
    ):
        path = ROOT / "Mathematiques/manuel-maths" / relative_path
        if not path.is_file():
            _reject(f"module absent : {_label(path)}")
        specification = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(specification)
        sys.modules[name] = module
        specification.loader.exec_module(module)
        modules.append(module)
    return modules[1], modules[0]


def rendered_boxes(variant: str, pdf: Path, inventory: Path) -> dict[str, Any]:
    """Le rectangle RÉELLEMENT occupé par chaque note, lu dans le PDF livré.

    Ce module ne recalcule pas où les notes se trouvent. Il le demande au
    ledger, qui le reconstruit depuis les objets du PDF -- la position du Form,
    sa boîte, la translation qui le pose. Recalculer serait se donner une
    deuxième idée de l'endroit où les notes vivent, et deux idées finissent
    toujours par diverger sans que personne le sache.
    """

    ledger_module, contract_module = _ledger_modules()
    capture = json.loads(inventory.read_text(encoding="utf-8"))
    stable = contract_module.materialize_stable_layout(capture)
    links = pdf.parent / f"MANUEL_1SPE_{variant}.margin-links.json"
    if not links.is_file():
        _reject(f"inventaire de liens absent : {_label(links)}")
    try:
        ledger = ledger_module.reconstruct_margin_ledger(pdf, capture, stable, links)
    except ledger_module.MarginLedgerError as error:
        _reject(f"reconstruction du ledger refusée pour {variant} : {error}")
    return {row["note_id"]: row for row in ledger["notes"]}


def measure(variant: str) -> dict[str, Any]:
    pdf = BUILD / f"MANUEL_1SPE_{variant}.pdf"
    inventory = BUILD / f"MANUEL_1SPE_{variant}.margin-layout.json"
    for path in (pdf, inventory):
        if not path.is_file():
            _reject(f"absent : {_label(path)}")
    layout = json.loads(inventory.read_text(encoding="utf-8"))
    if layout.get("state") != "stable":
        _reject(f"inventaire non stabilisé pour {variant} : {layout.get('state')}")

    fitz = _fitz()
    boxes = rendered_boxes(variant, pdf, inventory)
    traceless: list[dict[str, Any]] = []
    outside: list[dict[str, Any]] = []
    weakest = 1.0
    inspected = 0
    by_role: dict[str, dict[str, Any]] = {}

    with fitz.open(pdf) as document:
        for note in layout["notes"]:
            index = note.get("target_shipout_index")
            if index is None:
                continue
            entry = boxes.get(note["id"])
            if entry is None:
                _reject(f"le ledger ne connaît pas la note {note['id']}")
            if index > document.page_count:
                _reject(f"la note {note['id']} vise une page hors du document")
            page = document[index - 1]
            trim = page.trimbox
            left, top, right, bottom = entry["bbox_sp"]
            box = fitz.Rect(
                trim.x0 + left / SP_PER_BP,
                trim.y0 + top / SP_PER_BP,
                trim.x0 + right / SP_PER_BP,
                trim.y0 + bottom / SP_PER_BP,
            )
            role = note["role"]
            summary = by_role.setdefault(
                role,
                {
                    "role": role,
                    "inspected": 0,
                    "without_trace": 0,
                    "weakest_ink_coverage": 1.0,
                },
            )
            if not box.intersects(page.rect):
                outside.append({"id": note["id"], "page": index})
                continue
            coverage = ink_coverage(page, box)
            inspected += 1
            summary["inspected"] += 1
            weakest = min(weakest, coverage)
            summary["weakest_ink_coverage"] = round(
                min(summary["weakest_ink_coverage"], coverage), 5
            )
            if coverage < MINIMUM_INK_COVERAGE:
                traceless.append(
                    {
                        "id": note["id"],
                        "role": role,
                        "page": index,
                        "ink_coverage": round(coverage, 5),
                    }
                )
                summary["without_trace"] += 1

    declared = len(
        [note for note in layout["notes"] if note.get("target_shipout_index")]
    )
    return {
        "variant": variant,
        "pdf_path": _label(pdf),
        "inventory_path": _label(inventory),
        "declared_placed_notes": declared,
        "roles": sorted(by_role.values(), key=lambda row: row["role"]),
        "traceless": traceless[:40],
        "outside_their_page": outside[:40],
        "MARGIN_NOTES_INSPECTED": inspected,
        "MARGIN_NOTES_WITHOUT_TRACE": len(traceless),
        "MARGIN_NOTES_OUTSIDE_THEIR_PAGE": len(outside),
        "MARGIN_NOTES_NOT_INSPECTED": declared - inspected - len(outside),
        "WEAKEST_INK_COVERAGE": round(weakest, 5) if inspected else 0.0,
    }


def build() -> dict[str, Any]:
    variants = [measure(variant) for variant in VARIANTS]
    return {
        "artifact_type": "1spe_margin_raster_qa",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "raster_dpi": RASTER_DPI,
        "minimum_ink_coverage": MINIMUM_INK_COVERAGE,
        "what_this_measures_that_the_ledger_cannot": (
            "Une note peut être placée au bon endroit, du bon côté, dans le bon "
            "rectangle, et ne rien laisser sur la page. C'est ce qui s'est "
            "produit pendant toute une campagne : le Form XObject existait, sa "
            "boîte était juste, son contenu était vide d'encre."
        ),
        "geometry_is_verified_elsewhere": {
            "by": "Mathematiques/manuel-maths/scripts/margin_ledger.py",
            "what": (
                "identité, placement, géométrie physique, liens, écart de six "
                "points, confinement au rail et aux obstacles"
            ),
            "on": "le PDF livré, par test_margin_production_path.py",
        },
        "the_inventory_is_the_one_the_build_publishes": True,
        "the_boxes_are_read_from_the_ledger_not_recomputed": (
            "Le rectangle de chaque note est celui que le ledger reconstruit "
            "depuis les objets du PDF livré. Le recalculer ici donnerait une "
            "deuxième idée de l'endroit où les notes vivent, et deux idées "
            "finissent par diverger sans que personne le sache."
        ),
        "variants": variants,
        "summary": {
            "MARGIN_NOTES_INSPECTED": sum(
                row["MARGIN_NOTES_INSPECTED"] for row in variants
            ),
            "MARGIN_NOTES_WITHOUT_TRACE": sum(
                row["MARGIN_NOTES_WITHOUT_TRACE"] for row in variants
            ),
            "MARGIN_NOTES_OUTSIDE_THEIR_PAGE": sum(
                row["MARGIN_NOTES_OUTSIDE_THEIR_PAGE"] for row in variants
            ),
            "MARGIN_NOTES_NOT_INSPECTED": sum(
                row["MARGIN_NOTES_NOT_INSPECTED"] for row in variants
            ),
            "WEAKEST_INK_COVERAGE": min(
                (row["WEAKEST_INK_COVERAGE"] for row in variants), default=0.0
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Notes de marge — contrôle sur le rendu",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"Rendu à {payload['raster_dpi']} dpi.",
        "",
        f"> {payload['what_this_measures_that_the_ledger_cannot']}",
        "",
        "La géométrie est vérifiée ailleurs, par "
        f"`{payload['geometry_is_verified_elsewhere']['by']}` : "
        f"{payload['geometry_is_verified_elsewhere']['what']}, sur "
        f"{payload['geometry_is_verified_elsewhere']['on']}.",
        "",
        "## Métriques",
        "",
        "| Métrique | Valeur |",
        "|---|---:|",
    ]
    for name, value in payload["summary"].items():
        lines.append(f"| `{name}` | {value} |")
    for row in payload["variants"]:
        lines += [
            "",
            f"## Variante `{row['variant']}` — {row['MARGIN_NOTES_INSPECTED']} notes",
            "",
            "| Classe | Inspectées | Sans trace | Trace la plus faible |",
            "|---|---:|---:|---:|",
        ]
        for entry in row["roles"]:
            lines.append(
                f"| `{entry['role']}` | {entry['inspected']} | "
                f"{entry['without_trace']} | {entry['weakest_ink_coverage']} |"
            )
        if row["traceless"]:
            lines += ["", "### Sans trace", ""]
            for entry in row["traceless"]:
                lines.append(
                    f"- `{entry['id']}` page {entry['page']} — "
                    f"{entry['ink_coverage']}"
                )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ne rien écrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build()
    except MarginRasterError as error:
        print(f"1SPE-MARGIN-RASTER-QA-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"écrit {JSON_TARGET.name} et {MD_TARGET.name}")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    summary = payload["summary"]
    blocking = (
        "MARGIN_NOTES_WITHOUT_TRACE",
        "MARGIN_NOTES_OUTSIDE_THEIR_PAGE",
        "MARGIN_NOTES_NOT_INSPECTED",
    )
    return 1 if any(summary[name] for name in blocking) else 0


if __name__ == "__main__":
    raise SystemExit(main())
