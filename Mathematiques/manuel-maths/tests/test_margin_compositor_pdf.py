from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import pytest


MANUAL_ROOT = Path(__file__).resolve().parents[1]
CLASS_PATH = MANUAL_ROOT / "gabarits" / "nexus-manuel.cls"
MAX_PASSES = 6
RUN_NONCE = "0123456789abcdef0123456789abcdef"
CAPTURE_RECORD = re.compile(r"NEXUS-MARGIN-CAPTURE:(nxm:[^:\s]+:[^:\s]+:\d{8})")
ANCHOR_RECORD = re.compile(r"NEXUS-MARGIN-ANCHOR:(nxm:[^:\s]+:[^:\s]+:\d{8})")


def _load_margin_contract():
    module_path = MANUAL_ROOT / "scripts" / "margin_contract.py"
    spec = importlib.util.spec_from_file_location(
        "margin_contract_for_compositor_test", module_path
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _atomic_write_json(path: Path, document: dict[str, Any]) -> None:
    contract = _load_margin_contract()
    path.parent.mkdir(parents=True, exist_ok=True)
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


def _assert_nonempty_capture_inventory(layout: dict[str, Any]) -> None:
    assert layout["notes"], "zero annotation capturée doit faire échouer la fixture"


def _run_private_passes(source: Path, output_directory: Path) -> list[dict[str, Any]]:
    contract = _load_margin_contract()
    previous = output_directory / "margin-layout.previous.json"
    next_layout = output_directory / "margin-layout.next.json"
    stable_layout = output_directory / "margin-stable-layout.json"
    observed: list[dict[str, Any]] = []

    for pass_number in range(1, MAX_PASSES + 1):
        next_layout.unlink(missing_ok=True)
        environment = os.environ.copy()
        environment.update(
            {
                "NEXUS_MARGIN_RUN_NONCE": RUN_NONCE,
                "NEXUS_MARGIN_VARIANT": "eleve",
                "NEXUS_MARGIN_PASS_NUMBER": str(pass_number),
                "NEXUS_MARGIN_LAYOUT_PREVIOUS": str(previous),
                "NEXUS_MARGIN_LAYOUT_NEXT": str(next_layout),
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
        assert result.returncode == 0, result.stdout[-8000:] + result.stderr
        assert next_layout.is_file(), "inventaire de capture margin-layout.next.json absent"

        layout = json.loads(next_layout.read_text(encoding="utf-8"))
        contract.validate_margin_layout(layout)
        _assert_nonempty_capture_inventory(layout)
        assert layout["run_nonce"] == RUN_NONCE
        assert layout["variant"] == "eleve"
        assert layout["pass_number"] == pass_number

        capture_ids = CAPTURE_RECORD.findall(result.stdout)
        anchor_ids = ANCHOR_RECORD.findall(result.stdout)
        observed.append(
            {
                "layout": layout,
                "capture_ids": capture_ids,
                "anchor_ids": anchor_ids,
            }
        )

        os.replace(next_layout, previous)
        if layout["state"] == "stable":
            stable = contract.materialize_stable_layout(layout)
            contract.validate_stable_layout(stable)
            _atomic_write_json(stable_layout, stable)
            break
        assert layout["state"] in {"collecting", "changed"}
    else:
        pytest.fail("placements marginaux non stabilisés après six passes privées")

    assert stable_layout.is_file()
    assert (output_directory / f"{source.stem}.pdf").is_file()
    return observed


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_identical_anchor_captures_three_notes_once_on_every_private_pass(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "identical-anchor.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel}
\nxVersionProfesseurfalse
\begin{document}
\noindent Ancre commune\margeAppui{Premier appui}%
\margeAppui{Deuxième appui}%
\margeAppui{Troisième appui}. Fin de ligne.
\vfill
\newpage
Seconde page témoin.
\end{document}
""",
        encoding="utf-8",
    )

    passes = _run_private_passes(fixture, tmp_path)
    expected_ids = [
        "nxm:eleve:appui:00000001",
        "nxm:eleve:appui:00000002",
        "nxm:eleve:appui:00000003",
    ]

    assert len(passes) >= 2
    for observed in passes:
        layout = observed["layout"]
        notes = layout["notes"]
        assert len(layout["pages"]) == 2
        assert [note["id"] for note in notes] == expected_ids
        assert len({note["semantic_digest"] for note in notes}) == 3
        assert len({note["origin_y_sp"] for note in notes}) == 1
        assert Counter(observed["capture_ids"]) == Counter(
            {note_id: 1 for note_id in expected_ids}
        )
        assert Counter(observed["anchor_ids"]) == Counter(
            {note_id: 1 for note_id in expected_ids}
        )

    assert [[note["id"] for note in item["layout"]["notes"]] for item in passes] == [
        expected_ids
    ] * len(passes)


def test_capture_inventory_oracle_rejects_zero_notes() -> None:
    with pytest.raises(AssertionError, match="zero annotation capturée"):
        _assert_nonempty_capture_inventory({"notes": []})


def test_public_margin_components_use_only_the_shared_rail_adapter() -> None:
    source = CLASS_PATH.read_text(encoding="utf-8")

    assert r"\nxMarginRailNote{appui}" in source
    assert r"\nxMarginRailNote{commentaire}" in source
    assert r"\nxMarginRailNote{vocab}" in source
    assert r"\nxMarginRailNote{chrono}" in source
    assert r"\nxMarginRailNote{professor-id}" in source
    assert r"\marginnote{" not in source
    assert "nexus-margin-rail.tex" in source
