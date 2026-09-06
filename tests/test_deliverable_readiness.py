"""La maturité produit ne doit pas être mesurée par un reçu de build.

`RELEASE_READY` exige un HEAD gelé, un build final, un manifeste et une
approbation humaine — toutes choses interdites tant que le contenu bouge. S'en
servir pour mesurer l'avancement rendait tout livrable éternellement « non
prêt » quel que soit le travail accompli. `DEVELOPMENT_READY` mesure ce qui
progresse ; `RELEASE_READY` conserve ses exigences intactes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_release_deliverable_readiness as readiness  # noqa: E402


@pytest.fixture(scope="module")
def payload():
    return readiness.build()


def test_development_readiness_never_requires_a_build_receipt(payload) -> None:
    assert payload["summary"]["CURRENT_BUILD_RECEIPTS_REQUIRED_DURING_DEVELOPMENT"] is False
    for row in payload["deliverables"]:
        assert "receipt" not in row["axes"]


def test_release_readiness_keeps_all_of_its_requirements(payload) -> None:
    """Aucun gate de release n'est affaibli par la nouvelle métrique."""
    assert payload["summary"]["RELEASE_READY"] == 0
    for row in payload["deliverables"]:
        assert row["release_ready"] is False
        assert set(row["release_ready_blocked_by"]) == {
            "FROZEN_HEAD", "FINAL_BUILD", "CURRENT_MANIFEST",
            "REPRODUCIBILITY", "PREFLIGHT", "HUMAN_APPROVAL",
        }


def test_the_twenty_four_required_deliverables_are_measured(payload) -> None:
    assert payload["summary"]["REQUIRED_RELEASE_DELIVERABLES"] == 24
    assert len(payload["deliverables"]) == 24


def test_a_deliverable_is_ready_only_when_every_axis_is_green(payload) -> None:
    for row in payload["deliverables"]:
        assert row["development_ready"] == all(row["axes"].values()), row["deliverable_id"]


def test_the_remaining_gaps_are_content_gaps(payload) -> None:
    """Les trois manquants sont des contenus absents, pas des outils absents."""
    not_ready = {
        row["deliverable_id"]: [axis for axis, ok in row["axes"].items() if not ok]
        for row in payload["deliverables"] if not row["development_ready"]
    }
    assert set(not_ready) == {
        "TNSI::banque_ecrite", "TNSI::banque_pratique", "TNSI::version_amenagee",
    }
    for missing in not_ready.values():
        assert "content" in missing or "development_build" in missing


def test_the_build_matcher_ignores_in_progress_work_directories(tmp_path: Path) -> None:
    """Le PDF d'un build en cours vit dans un répertoire caché : il ne compte pas."""
    root = tmp_path / "build"
    (root / "MANUEL_X" / ".MANUEL_X_eleve-abcdef").mkdir(parents=True)
    (root / "MANUEL_X" / ".MANUEL_X_eleve-abcdef" / "MANUEL_X_eleve.pdf").write_bytes(b"%PDF")
    original = dict(readiness.BUILD_ROOTS)
    try:
        readiness.BUILD_ROOTS.clear()
        readiness.BUILD_ROOTS["test"] = root
        assert readiness._development_build("X", "eleve")["present"] is False
        (root / "MANUEL_X" / "MANUEL_X_eleve.pdf").write_bytes(b"%PDF")
        assert readiness._development_build("X", "eleve")["present"] is True
    finally:
        readiness.BUILD_ROOTS.clear()
        readiness.BUILD_ROOTS.update(original)


def test_the_matcher_tolerates_hyphenated_build_directories() -> None:
    """Le scope écrit `TSPE_2026_2027`, le répertoire de build `TSPE_2026-2027`."""
    assert readiness._normalise("MANUEL_TSPE_2026-2027").endswith(
        readiness._normalise("TSPE_2026_2027")
    )


# --- Le contrôle de fuite élève ne doit pas confondre un adjectif ------------

def test_student_leak_pattern_ignores_the_adjective() -> None:
    """« l'invariant corrigé par une assertion » est un énoncé, pas un corrigé."""
    sys.path.insert(0, str(ROOT / "NSI/scripts"))
    import pdf_integrity

    innocent = "Écrire une fonction qui vérifie l'invariant corrigé par une assertion."
    assert pdf_integrity.BOOK_STUDENT_LEAK.search(innocent) is None
    assert pdf_integrity.BOOK_STUDENT_LEAK.search("Corriger le code pour garantir la terminaison.") is None

    for leak in ("Corrigé\nExercice 1", "  Corrigés\n", "Barème indicatif : 4 points"):
        assert pdf_integrity.BOOK_STUDENT_LEAK.search(leak) is not None, leak
