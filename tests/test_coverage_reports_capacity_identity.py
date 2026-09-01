"""Les deux rapports historiques utilisent l'identité canonique, jamais un suffixe."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
REPORTS = (
    ROOT / "Mathematiques/manuel-maths/scripts/coverage_report.py",
    ROOT / "NSI/scripts/coverage_report.py",
)


def _load_report(path: Path, data_root: Path):
    common = ModuleType("common")
    common.ROOT = data_root
    previous = sys.modules.get("common")
    sys.modules["common"] = common
    try:
        spec = importlib.util.spec_from_file_location(
            f"coverage_report_{path.parts[-3]}", path
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if previous is None:
            sys.modules.pop("common", None)
        else:
            sys.modules["common"] = previous


def _fixture(tmp_path: Path) -> tuple[Path, str]:
    data_root = tmp_path / "manual"
    chapter = "TSPE-PROBABILITES"
    directory = data_root / "chapitres" / chapter
    (directory / "cours").mkdir(parents=True)
    (directory / "contrat.yaml").write_text(
        yaml.safe_dump(
            {
                "capacites": [
                    {"code": "C1", "ref_capacite": "TSPE-PROBA-C1"},
                    {"code": "C10", "ref_capacite": "TSPE-CONCLGN-C1"},
                ]
            }
        ),
        encoding="utf-8",
    )
    return data_root, chapter


@pytest.mark.parametrize("report_path", REPORTS)
def test_fully_qualified_reference_credits_contract_owner_not_suffix_twin(
    report_path: Path, tmp_path: Path
) -> None:
    data_root, chapter = _fixture(tmp_path)
    directory = data_root / "chapitres" / chapter
    (directory / "cours" / "objet.tex").write_text(
        "% META: "
        + json.dumps(
            {
                "id": "OBJ",
                "chapitre": chapter,
                "type_objet": "cours",
                "capacites": ["TSPE-CONCLGN-C1"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    report = _load_report(report_path, data_root)
    resolver = report.CapacityIdentityResolver.from_corpora(
        (data_root / "chapitres",)
    )

    coverage = report.collect_coverage(chapter, directory, resolver)

    assert coverage["have"]["C10"] == {"cours"}
    assert coverage["have"].get("C1", set()) == set()


@pytest.mark.parametrize("report_path", REPORTS)
def test_conflicting_meta_capacity_fields_fail_closed(
    report_path: Path, tmp_path: Path
) -> None:
    data_root, chapter = _fixture(tmp_path)
    directory = data_root / "chapitres" / chapter
    (directory / "cours" / "objet.tex").write_text(
        "% META: "
        + json.dumps(
            {
                "id": "OBJ",
                "chapitre": chapter,
                "type_objet": "cours",
                "capacites_codes": ["C1"],
                "capacites": ["TSPE-CONCLGN-C1"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    report = _load_report(report_path, data_root)
    resolver = report.CapacityIdentityResolver.from_corpora(
        (data_root / "chapitres",)
    )

    with pytest.raises(report.AmbiguousCapacityIdentity):
        report.collect_coverage(chapter, directory, resolver)


@pytest.mark.parametrize("report_path", REPORTS)
def test_qcm_json_reference_credits_only_its_exact_contract_owner(
    report_path: Path, tmp_path: Path
) -> None:
    data_root, chapter = _fixture(tmp_path)
    directory = data_root / "chapitres" / chapter
    qcm = directory / "qcm"
    qcm.mkdir()
    (qcm / "x-QCM.json").write_text(
        json.dumps(
            {
                "chapitre": chapter,
                "questions": [
                    {"id": "Q1", "capacite": "TSPE-CONCLGN-C1"}
                ],
            }
        ),
        encoding="utf-8",
    )
    # Le `.tex` généré ne porte aucune capacité et ne doit pas être la source
    # de vérité du rôle QCM.
    (qcm / "x-QCM.tex").write_text(
        "% META: "
        + json.dumps(
            {"id": "QCM", "chapitre": chapter, "type_objet": "qcm"}
        )
        + "\n",
        encoding="utf-8",
    )
    report = _load_report(report_path, data_root)
    resolver = report.CapacityIdentityResolver.from_corpora(
        (data_root / "chapitres",)
    )

    coverage = report.collect_coverage(chapter, directory, resolver)

    assert "qcm" not in coverage["have"].get("C1", set())
    assert "qcm" in coverage["have"]["C10"]


@pytest.mark.parametrize("report_path", REPORTS)
def test_legacy_report_is_explicitly_non_authoritative_and_multiple_qcm_blocks(
    report_path: Path, tmp_path: Path
) -> None:
    data_root, chapter = _fixture(tmp_path)
    directory = data_root / "chapitres" / chapter
    qcm = directory / "qcm"
    qcm.mkdir()
    payload = {"chapitre": chapter, "questions": []}
    for name in ("a-QCM.json", "b-QCM.json"):
        (qcm / name).write_text(json.dumps(payload), encoding="utf-8")
    report = _load_report(report_path, data_root)
    resolver = report.CapacityIdentityResolver.from_corpora(
        (data_root / "chapitres",)
    )
    assert report.AUTHORITATIVE is False
    with pytest.raises(ValueError, match="MULTIPLE_QCM_SOURCES"):
        report.collect_coverage(chapter, directory, resolver)
