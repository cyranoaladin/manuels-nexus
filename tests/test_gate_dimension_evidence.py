"""Le gate lit le statut réel des dimensions, et refuse une preuve périmée.

Deux confusions à écarter. D'abord, « la dimension a un producteur » n'est pas
« la dimension est satisfaite » : une preuve rouge couvre la dimension sans la
valider. Ensuite, une preuve n'est fraîche que si les octets qu'elle dit avoir
mesurés sont toujours ceux du dépôt — la fraîcheur se vérifie sur les entrées
déclarées, pas sur le HEAD git, sinon committer l'artefact de preuve le
périmerait à l'instant même de son enregistrement.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certification_dimensions as cd  # noqa: E402
import inventory_collection as ic  # noqa: E402


def _evidence(tmp_path: Path, *, status: str, inputs: list[str]) -> Path:
    (tmp_path / "audit").mkdir(parents=True, exist_ok=True)
    for relative in inputs:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("contenu", encoding="utf-8")
    digest = cd.digest_inputs([tmp_path / r for r in inputs], tmp_path)
    path = tmp_path / "audit/DIMENSION_TEST.json"
    path.write_text(json.dumps({
        "status": status,
        "evidence_head": "0" * 40,
        "input_digest": digest,
        "input_paths": inputs,
    }), encoding="utf-8")
    return path


@pytest.mark.parametrize("status", ["passed", "failed"])
def test_a_fresh_evidence_reports_its_real_status(tmp_path: Path, status: str) -> None:
    _evidence(tmp_path, status=status, inputs=["src/a.tex"])
    assert ic._dimension_status_from_evidence(tmp_path, "audit/DIMENSION_TEST.json") == status


def test_a_mutated_input_makes_the_evidence_stale(tmp_path: Path) -> None:
    _evidence(tmp_path, status="passed", inputs=["src/a.tex", "src/b.tex"])
    (tmp_path / "src/b.tex").write_text("autre contenu", encoding="utf-8")
    assert ic._dimension_status_from_evidence(tmp_path, "audit/DIMENSION_TEST.json") == "not_covered"


def test_a_removed_input_makes_the_evidence_stale(tmp_path: Path) -> None:
    _evidence(tmp_path, status="passed", inputs=["src/a.tex"])
    (tmp_path / "src/a.tex").unlink()
    assert ic._dimension_status_from_evidence(tmp_path, "audit/DIMENSION_TEST.json") == "not_covered"


def test_evidence_without_declared_inputs_is_never_trusted(tmp_path: Path) -> None:
    (tmp_path / "audit").mkdir(parents=True)
    (tmp_path / "audit/DIMENSION_TEST.json").write_text(
        json.dumps({"status": "passed", "input_digest": "sha256:" + "0" * 64}), encoding="utf-8"
    )
    assert ic._dimension_status_from_evidence(tmp_path, "audit/DIMENSION_TEST.json") == "not_covered"


def test_a_missing_or_unreadable_artifact_is_not_covered(tmp_path: Path) -> None:
    assert ic._dimension_status_from_evidence(tmp_path, "audit/ABSENT.json") == "not_covered"
    (tmp_path / "audit").mkdir(parents=True)
    (tmp_path / "audit/BROKEN.json").write_text("pas du json", encoding="utf-8")
    assert ic._dimension_status_from_evidence(tmp_path, "audit/BROKEN.json") == "not_covered"


def test_an_unknown_status_value_is_refused(tmp_path: Path) -> None:
    _evidence(tmp_path, status="probablement bon", inputs=["src/a.tex"])
    assert ic._dimension_status_from_evidence(tmp_path, "audit/DIMENSION_TEST.json") == "not_covered"


def test_the_four_dimensions_are_wired_into_the_gate() -> None:
    assert set(ic.DIMENSION_EVIDENCE_ARTIFACTS) == {
        "mathematics", "regulation", "print", "visual",
    }
    for relative in ic.DIMENSION_EVIDENCE_ARTIFACTS.values():
        assert relative.startswith("audit/DIMENSION_")


def test_the_shared_freshness_helper_agrees_with_the_gate(tmp_path: Path) -> None:
    """Le producteur et le gate ne doivent pas avoir deux notions de fraîcheur."""
    path = _evidence(tmp_path, status="passed", inputs=["src/a.tex"])
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert cd.evidence_is_fresh(payload, tmp_path) is True
    (tmp_path / "src/a.tex").write_text("muté", encoding="utf-8")
    assert cd.evidence_is_fresh(payload, tmp_path) is False
