from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RENDER_ROOTS = (
    ROOT / "Mathematiques/manuel-maths/gabarits",
    ROOT / "Mathematiques/manuel-maths/chapitres",
    ROOT / "NSI/gabarits",
    ROOT / "NSI/chapitres",
)


def _rendered_tex_lines(path: Path) -> list[str]:
    return [
        line.split("%", 1)[0]
        for line in path.read_text(encoding="utf-8").splitlines()
    ]


@pytest.mark.parametrize("glyph", ("◆", "✓", "✗"))
def test_rendered_tex_avoids_font_dependent_glyphs(glyph):
    offenders = []
    for source_root in RENDER_ROOTS:
        for path in source_root.rglob("*.tex"):
            if any(glyph in line for line in _rendered_tex_lines(path)):
                offenders.append(path.relative_to(ROOT).as_posix())

    assert offenders == []


def test_margin_notes_use_the_vector_check_icon():
    offenders = []
    for source_root in RENDER_ROOTS:
        for path in source_root.rglob("*.tex"):
            if any(
                "\\commentaireMarge{" in line and "\\checkmark" in line
                for line in _rendered_tex_lines(path)
            ):
                offenders.append(path.relative_to(ROOT).as_posix())

    assert offenders == []
