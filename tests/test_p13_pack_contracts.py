"""RED/GREEN contract: P13 pack sources must call \\nsiheader, not the bare
`siheader{...}` typo that silently drops through pdflatex as plain text."""

from pathlib import Path

import pytest

P13_DIR = (
    Path(__file__).resolve().parents[1]
    / "NSI"
    / "corpus_nsi"
    / "latex"
    / "packs"
    / "premiere"
    / "P13"
)

P13_SOURCES = [
    "P13_aides.tex",
    "P13_corrige.tex",
    "P13_cours.tex",
    "P13_evaluation.tex",
    "P13_fiche_methode.tex",
    "P13_td.tex",
    "P13_td_eleve.tex",
    "P13_tp.tex",
    "P13_tp_eleve.tex",
    "P13_trace.tex",
]


@pytest.mark.parametrize("filename", P13_SOURCES)
def test_p13_source_calls_nsiheader_with_backslash(filename: str) -> None:
    text = (P13_DIR / filename).read_text(encoding="utf-8")
    assert "\\nsiheader{" in text, f"{filename} does not call \\nsiheader{{...}}"
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("siheader{"):
            pytest.fail(f"{filename} calls bare siheader{{...}} without a leading backslash")
