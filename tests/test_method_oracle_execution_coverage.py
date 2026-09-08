"""Exercise the real CLI on temporary fixtures, including deliberate bad oracles."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "Mathematiques/manuel-maths"


def _runner(tmp_path: Path) -> Path:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    for name in ("verify_sympy.py", "common.py"):
        shutil.copyfile(MANUAL / "scripts" / name, scripts / name)
    return scripts / "verify_sympy.py"


def _run(runner: Path, chapter: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(runner), "--chap", chapter],
        cwd=runner.parent.parent,
        env={**os.environ, "PYTHON_DOTENV_DISABLED": "1"},
        text=True, capture_output=True, timeout=20,
    )


def test_a_false_method_oracle_changes_the_cli_and_receipt_to_failure(tmp_path: Path) -> None:
    runner = _runner(tmp_path)
    source = tmp_path / "chapitres/PROBE/methodes/METHOD.tex"
    source.parent.mkdir(parents=True)
    source.write_text("% BEGIN-VERIFY\n% assert 2 + 2 == 4\n% END-VERIFY\n")
    receipt = source.parent.parent / "validations/METHOD.sympy.json"
    assert _run(runner, "PROBE").returncode == 0
    before = json.loads(receipt.read_text())
    assert before["verdict"] == "pass"
    assert before["verification_protocol"] == "EXECUTED_ASSERTIONS_PER_BLOCK_V1"
    assert before["verifier_sha256"] == "sha256:" + hashlib.sha256(runner.read_bytes()).hexdigest()
    source.write_text(source.read_text().replace("== 4", "== 5"))
    assert _run(runner, "PROBE").returncode == 1
    after = json.loads(receipt.read_text())
    assert after["verdict"] == "fail"
    assert after["source_sha256"] != before["source_sha256"]
    assert after["source_sha256"] == "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()


def test_a_second_method_block_is_executed_and_no_oracle_is_not_a_pass(tmp_path: Path) -> None:
    runner = _runner(tmp_path)
    directory = tmp_path / "chapitres/PROBE/methodes"
    directory.mkdir(parents=True)
    (directory / "TWO.tex").write_text(
        "% BEGIN-VERIFY\n% assert True\n% END-VERIFY\n"
        "% BEGIN-VERIFY\n% assert False\n% END-VERIFY\n"
    )
    (directory / "NONE.tex").write_text("Un raisonnement sans oracle mécanique.\n")
    assert _run(runner, "PROBE").returncode == 1
    results = {p.stem: json.loads(p.read_text())["verdict"]
               for p in (directory.parent / "validations").glob("*.json")}
    assert results == {"TWO.sympy": "fail", "NONE.sympy": "manual_review"}


def test_every_current_method_oracle_location_is_reached_by_the_cli(tmp_path: Path) -> None:
    runner = _runner(tmp_path)
    # Independent recursive inventory; neither a fixed count nor the verifier's
    # own list of directories defines what must be exercised.
    expected = set()
    for source in sorted((MANUAL / "chapitres").rglob("*.tex")):
        relative = source.relative_to(MANUAL)
        if "methodes" not in relative.parts or "validations" in relative.parts:
            continue
        if not re.search(r"^% BEGIN-VERIFY\s*$", source.read_text(), re.M):
            continue
        expected.add(relative.as_posix())
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("% BEGIN-VERIFY\n% assert False, 'coverage mutation'\n% END-VERIFY\n")
    assert expected, "empty corpus must not certify coverage"
    for chapter in sorted({Path(p).parts[1] for p in expected}):
        assert _run(runner, chapter).returncode == 1
    receipts = [json.loads(p.read_text()) for p in (tmp_path / "chapitres").rglob("*.sympy.json")]
    assert {row["source_path"] for row in receipts} == expected
    assert len(receipts) == len(expected)
    assert all(row["verdict"] == "fail" for row in receipts)


@pytest.mark.parametrize("script", [
    "import sympy",
    "assert True\ntry:\n    assert 1 / 0\nexcept ZeroDivisionError:\n    pass",
    "class BadTruth:\n    def __bool__(self):\n        raise ValueError\nassert True\ntry:\n    assert BadTruth()\nexcept ValueError:\n    pass",
    "if False:\n    assert False",
    "import sys\nsys.exit(0)",
    "try:\n    assert False\nexcept AssertionError:\n    pass",
])
def test_an_oracle_without_successfully_exercised_assertions_is_not_a_pass(
    tmp_path: Path, script: str,
) -> None:
    runner = _runner(tmp_path)
    source = tmp_path / "chapitres/PROBE/methodes/EMPTY_PROOF.tex"
    source.parent.mkdir(parents=True)
    source.write_text("% BEGIN-VERIFY\n" + "\n".join("% " + line for line in script.splitlines())
                      + "\n% END-VERIFY\n")
    assert _run(runner, "PROBE").returncode == 1
    result = json.loads((source.parent.parent / "validations/EMPTY_PROOF.sympy.json").read_text())
    assert result["verdict"] == "fail"


def test_each_method_block_must_exercise_assertions_and_blocks_share_variables(tmp_path: Path) -> None:
    runner = _runner(tmp_path)
    source = tmp_path / "chapitres/PROBE/methodes/TWO.tex"
    source.parent.mkdir(parents=True)
    source.write_text("% BEGIN-VERIFY\n% x = 4\n% assert x == 4\n% END-VERIFY\n"
                      "% BEGIN-VERIFY\n% assert x * 2 == 8\n% END-VERIFY\n")
    assert _run(runner, "PROBE").returncode == 0
    source.write_text(source.read_text().replace("% assert x * 2 == 8", "% if False:\n%     assert x * 2 == 9"))
    assert _run(runner, "PROBE").returncode == 1


def test_a_receipt_cannot_bind_a_source_changed_during_execution(tmp_path: Path) -> None:
    runner = _runner(tmp_path)
    source = tmp_path / "chapitres/PROBE/methodes/RACE.tex"
    source.parent.mkdir(parents=True)
    source.write_text("% BEGIN-VERIFY\n% from pathlib import Path\n"
                      + "% Path(" + repr(str(source)) + ").write_text('changed')\n"
                      + "% assert 2 + 2 == 4\n% END-VERIFY\n")
    assert _run(runner, "PROBE").returncode == 1
    result = json.loads((source.parent.parent / "validations/RACE.sympy.json").read_text())
    assert result["verdict"] == "fail"
    assert "source changed" in result["details"]["output"]
    assert result["source_sha256"] != "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()


def test_assertion_in_a_class_preserves_truth_and_lazy_failure_message(tmp_path: Path) -> None:
    runner = _runner(tmp_path)
    source = tmp_path / "chapitres/PROBE/methodes/CLASS.tex"
    source.parent.mkdir(parents=True)
    script = "class Check:\n    def run(self):\n        assert 2 + 2 == 4, 1 / 0\nCheck().run()"
    source.write_text("% BEGIN-VERIFY\n" + "\n".join("% " + line for line in script.splitlines())
                      + "\n% END-VERIFY\n")
    assert _run(runner, "PROBE").returncode == 0


def test_future_flags_remain_active_across_blocks(tmp_path: Path) -> None:
    runner = _runner(tmp_path)
    source = tmp_path / "chapitres/PROBE/methodes/FUTURE.tex"
    source.parent.mkdir(parents=True)
    source.write_text("% BEGIN-VERIFY\n% from __future__ import annotations\n% assert True\n% END-VERIFY\n"
                      "% BEGIN-VERIFY\n% def identity(x: Unknown):\n%     return x\n"
                      "% assert identity(4) == 4\n% END-VERIFY\n")
    assert _run(runner, "PROBE").returncode == 0
