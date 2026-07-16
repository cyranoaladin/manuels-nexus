import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_charte_sync import COMMON_FILES, find_mismatches  # noqa: E402


def test_find_mismatches_reports_only_divergent_common_files(tmp_path):
    maths = tmp_path / "maths"
    nsi = tmp_path / "nsi"
    for relative in COMMON_FILES:
        for root in (maths, nsi):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("identique", encoding="utf-8")

    changed = nsi / COMMON_FILES[0]
    changed.write_text("différent", encoding="utf-8")

    assert find_mismatches(maths, nsi) == [COMMON_FILES[0]]
