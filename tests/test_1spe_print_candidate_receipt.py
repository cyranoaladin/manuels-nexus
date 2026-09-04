"""Un reçu de candidat d'impression doit pouvoir PÉRIMER.

Celui qui portait ce nom était une saisie manuelle : rien ne le produisait,
donc rien ne le rafraîchissait. Il décrivait encore un manuel de 357 et 629
pages, sans signets ni TrimBox, et bloquait la release au nom d'un état qui
n'existait plus. Un reçu insensible à ce qu'il atteste ne prouve rien.

Ce module vérifie qu'il est dérivé du manifeste et des contrôles déjà produits,
qu'il décrit bien les sources courantes, et qu'il n'approuve rien. Puis il mute
les preuves pour montrer qu'il sait dire non.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_print_candidate_receipt as gate  # noqa: E402


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not gate.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {gate.JSON_TARGET}")
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


def test_the_receipt_describes_the_current_sources(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    assert summary["RECEIPT_DESCRIBES_HEAD"] is True
    assert summary["OBSERVED_VARIANTS"] == summary["EXPECTED_VARIANTS"] == 2
    assert payload["observed_source_digest"] == payload["current_source_digest"]


def test_the_page_counts_come_from_the_build_not_from_history(
    payload: dict[str, Any],
) -> None:
    """Ni 363 ni 635 ne sont une référence : le compte vient du manifeste."""

    counts = payload["summary"]["PAGE_COUNTS"]
    manifest = json.loads(
        (ROOT / "audit/BUILD_MANIFEST.json").read_text(encoding="utf-8")
    )
    observed = {
        build["variant"]: build["page_count"]
        for build in manifest["builds"]
        if build["manual"] == "1SPE"
    }
    assert counts == observed
    assert counts["professeur"] > counts["eleve"]
    source = (ROOT / "scripts/build_1spe_print_candidate_receipt.py").read_text(
        encoding="utf-8"
    )
    for historical in ("363", "635", "355", "627"):
        assert historical not in source, historical


def test_each_variant_carries_the_evidence_of_its_own_build(
    payload: dict[str, Any],
) -> None:
    for row in payload["variants"].values():
        assert row["pdf_sha256"].startswith("sha256:")
        assert row["log_sha256"] is not None, row["variant"]
        assert row["margin_layout_sha256"] is not None, row["variant"]
        assert row["margin_links_sha256"] is not None, row["variant"]
        assert row["preflight_present"] is True, row["variant"]
        assert row["observed_receipt_present"] is True, row["variant"]
        assert (ROOT / row["pdf_path"]).is_file(), row["pdf_path"]


def test_the_quality_evidence_is_cited_and_all_of_it_is_zero(
    payload: dict[str, Any],
) -> None:
    """Le reçu cite les contrôles ; il ne refait aucune mesure."""

    assert payload["quality_evidence_is_cited_not_recomputed"] is True
    assert payload["summary"]["QA_ARTIFACTS_MISSING"] == 0
    assert payload["summary"]["QA_METRICS_NOT_ZERO"] == 0
    cited = {row["artifact"] for row in payload["quality_evidence"]}
    assert cited == set(gate.QA_SOURCES)
    for row in payload["quality_evidence"]:
        assert (ROOT / row["artifact"]).is_file()
        for name, value in row["metrics"].items():
            assert value == 0, (row["artifact"], name, value)


def test_the_receipt_approves_nothing(payload: dict[str, Any]) -> None:
    assert payload["approves_nothing"] is True
    for expected in ("FINAL_CONTENT_SHA", "revues humaines", "D7"):
        assert expected in payload["not_final"]


# ---------------------------------------------------------------------------
#  Mutations
# ---------------------------------------------------------------------------


def test_a_manifest_that_observes_nothing_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Sans construction observée, il n'y a rien à recevoir."""

    empty = tmp_path / "BUILD_MANIFEST.json"
    empty.write_text(json.dumps({"builds": []}), encoding="utf-8")
    monkeypatch.setattr(gate, "MANIFEST", empty)

    with pytest.raises(gate.ReceiptError, match="aucune construction"):
        gate.build_receipt()
    assert gate.main(["--check"]) == 2


def test_sources_that_moved_since_the_build_are_seen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """C'est exactement le défaut d'origine : un reçu qui survit aux sources."""

    manifest = json.loads(
        (ROOT / "audit/BUILD_MANIFEST.json").read_text(encoding="utf-8")
    )
    manifest["source_digest"] = "sha256:" + "0" * 64
    moved = tmp_path / "BUILD_MANIFEST.json"
    moved.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(gate, "MANIFEST", moved)

    result = gate.build_receipt()

    assert result["summary"]["RECEIPT_DESCRIBES_HEAD"] is False
    assert gate.main(["--check"]) == 1


def test_a_single_recorded_variant_is_not_a_pair(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = json.loads(
        (ROOT / "audit/BUILD_MANIFEST.json").read_text(encoding="utf-8")
    )
    manifest["builds"] = [
        build for build in manifest["builds"] if build["variant"] == "eleve"
    ]
    partial = tmp_path / "BUILD_MANIFEST.json"
    partial.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(gate, "MANIFEST", partial)

    result = gate.build_receipt()

    assert result["summary"]["OBSERVED_VARIANTS"] == 1
    assert result["summary"]["RECEIPT_DESCRIBES_HEAD"] is False


def test_a_quality_metric_that_stops_being_zero_is_seen(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Le reçu cite les contrôles : il doit refuser quand l'un d'eux parle."""

    monkeypatch.setattr(
        gate,
        "quality_evidence",
        lambda: (
            [
                {
                    "artifact": "audit/1SPE_ALL_PAGES_QA.json",
                    "artifact_sha256": "sha256:0",
                    "metrics": {"TEXT_INSIDE_SAFETY_MARGIN": 3},
                }
            ],
            [],
        ),
    )

    result = gate.build_receipt()

    assert result["summary"]["QA_METRICS_NOT_ZERO"] == 1
    assert gate.main(["--check"]) == 1


def test_a_missing_quality_artifact_is_named(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        gate, "QA_SOURCES", {"audit/ABSENT.json": ("UNE_METRIQUE",)}
    )

    result = gate.build_receipt()

    assert result["summary"]["QA_ARTIFACTS_MISSING"] == 1
    assert result["missing_quality_artifacts"] == ["audit/ABSENT.json"]
    assert gate.main(["--check"]) == 1
