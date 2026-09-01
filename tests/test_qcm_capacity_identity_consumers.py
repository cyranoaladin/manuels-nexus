"""Les producteurs QCM résolvent leurs capacités par UID canonique."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def identity():
    return _load("qcm_test_capacity_identity", "capacity_identity.py")


@pytest.fixture(scope="module")
def consumers():
    return (
        _load("qcm_gap_metrics_identity_test", "build_qcm_gap_metrics.py"),
        _load(
            "qcm_capacity_debt_identity_test",
            "build_qcm_capacity_coverage_debt.py",
        ),
    )


def _chapter(tmp_path: Path, capacity: str) -> tuple[Path, Path]:
    corpus = tmp_path / "chapitres"
    chapter = corpus / "TSPE-X"
    (chapter / "qcm").mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        yaml.safe_dump(
            {
                "chapitre": "TSPE-X",
                "capacites": [
                    {"code": "C1", "ref_capacite": "REF-C1"},
                    {"code": "C10", "ref_capacite": "TSPE-CONCLGN-C1"},
                ],
            }
        ),
        encoding="utf-8",
    )
    (chapter / "qcm/TSPE-X-QCM.json").write_text(
        json.dumps(
            {
                "chapitre": "TSPE-X",
                "questions": [
                    {
                        "id": "Q1",
                        "capacite": capacity,
                        "correcte": "A",
                        "options": {"A": "a", "B": "b", "C": "c", "D": "d"},
                        "diagnostics": {
                            key: {"erreur": "e", "renvoi": "C10"}
                            for key in "BCD"
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return corpus, chapter


@pytest.mark.parametrize("consumer_index", [0, 1])
def test_unknown_qcm_capacity_blocks_both_producers(
    identity, consumers, tmp_path: Path, consumer_index: int
) -> None:
    corpus, _chapter_path = _chapter(tmp_path, "FAUSSE-C999")
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))
    consumer = consumers[consumer_index]
    with pytest.raises(identity.UnresolvedCapacityIdentity):
        if consumer_index == 0:
            consumer.build_report(resolver=resolver, chapters_root=corpus)
        else:
            consumer.build_debt(resolver=resolver, chapter_root=corpus)


def test_official_reference_credits_c10_and_never_local_c1(
    identity, consumers, tmp_path: Path
) -> None:
    corpus, _chapter_path = _chapter(tmp_path, "TSPE-CONCLGN-C1")
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))

    metrics = consumers[0].build_report(resolver=resolver, chapters_root=corpus)
    missing = metrics["CHAPTER_CAPACITY_PAIRS_WITHOUT_ANY_QCM"]["by_chapter"]
    assert missing["TSPE-X"] == ["C1"]

    debt = consumers[1].build_debt(resolver=resolver, chapter_root=corpus)
    assert debt["missing_by_chapter"]["TSPE-X"] == ["C1"]


def test_default_collection_scope_includes_math_and_nsi(consumers) -> None:
    metrics = consumers[0].build_report()
    paths = {row["path"] for row in metrics["source_inputs"]}
    assert any(path.startswith("Mathematiques/") for path in paths)
    assert any(path.startswith("NSI/") for path in paths)

    debt = consumers[1].build_debt()
    chapters = {row["chapter"] for row in debt["source_inputs"]}
    assert any(chapter.startswith("1NSI-") for chapter in chapters)
    assert any(chapter.startswith("TNSI-") for chapter in chapters)
    assert any(chapter.startswith("1SPE-") for chapter in chapters)
    assert any(chapter.startswith("TSPE-") for chapter in chapters)


def test_contract_chapter_without_qcm_is_reported_as_debt(
    identity, consumers, tmp_path: Path
) -> None:
    corpus = tmp_path / "chapitres"
    chapter = corpus / "TSPE-X"
    chapter.mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        yaml.safe_dump(
            {
                "chapitre": "TSPE-X",
                "capacites": [
                    {"code": "C1", "ref_capacite": "TSPE-X-C1"},
                ],
            }
        ),
        encoding="utf-8",
    )
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))

    debt = consumers[1].build_debt(resolver=resolver, chapter_root=corpus)

    assert debt["missing_by_chapter"] == {"TSPE-X": ["C1"]}
    assert debt["inventory"]["chapters"] == 1
    assert debt["inventory"]["qcm_files"] == 0
    assert debt["objective_zero"] is False


@pytest.mark.parametrize("consumer_index", [0, 1])
def test_multiple_qcm_sources_fail_closed(
    identity, consumers, tmp_path: Path, consumer_index: int
) -> None:
    corpus, chapter = _chapter(tmp_path, "C1")
    first = json.loads((chapter / "qcm/TSPE-X-QCM.json").read_text(encoding="utf-8"))
    (chapter / "qcm/TSPE-X-SECOND-QCM.json").write_text(
        json.dumps(first), encoding="utf-8"
    )
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))
    with pytest.raises(ValueError, match="MULTIPLE_QCM_SOURCES"):
        if consumer_index == 0:
            consumers[0].build_report(resolver=resolver, chapters_root=corpus)
        else:
            consumers[1].build_debt(resolver=resolver, chapter_root=corpus)


def test_qcm_declared_for_another_chapter_fails_closed(
    identity, consumers, tmp_path: Path
) -> None:
    corpus, chapter = _chapter(tmp_path, "C1")
    source = chapter / "qcm/TSPE-X-QCM.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["chapitre"] = "TSPE-AUTRE"
    source.write_text(json.dumps(payload), encoding="utf-8")
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))

    with pytest.raises(ValueError, match="QCM_CHAPTER_MISMATCH"):
        consumers[0].build_report(resolver=resolver, chapters_root=corpus)


def test_composite_mandatory_atom_marks_each_exact_capacity(
    identity, consumers, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    corpus, _chapter_path = _chapter(tmp_path, "REF-C1")
    coverage = tmp_path / "coverage.json"
    coverage.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "mandatory": "YES",
                        "chapter": "TSPE-X",
                        "contract_capacity": "REF-C1 + TSPE-CONCLGN-C1",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))
    monkeypatch.setattr(consumers[0], "COVERAGE", coverage)

    report = consumers[0].build_report(resolver=resolver, chapters_root=corpus)
    missing = report["MANDATORY_ASSESSED_CAPACITY_PAIRS_WITHOUT_QCM"]["pairs"]
    assert [(row["chapter"], row["capacity_code"]) for row in missing] == [
        ("TSPE-X", "C10")
    ]
