import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from assemble import collect  # noqa: E402


def test_collect_places_coups_de_pouce_after_exercises(tmp_path):
    for name in ("cours", "methodes", "exercices", "coups_de_pouce"):
        (tmp_path / name).mkdir()
    (tmp_path / "cours" / "10_C1.tex").write_text("", encoding="utf-8")
    (tmp_path / "exercices" / "EX-001.tex").write_text("", encoding="utf-8")
    (tmp_path / "coups_de_pouce" / "EX-001-CDP.tex").write_text("", encoding="utf-8")

    files = collect(tmp_path, "complet")

    assert [f.name for f in files] == ["10_C1.tex", "EX-001.tex", "EX-001-CDP.tex"]
