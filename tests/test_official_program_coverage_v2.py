from __future__ import annotations

import json
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ATOMS_PATH = ROOT / "audit" / "OFFICIAL_PROGRAM_ATOMS_2026_2027.json"
MATRIX_ROOT = ROOT / "audit" / "official_program_coverage"
SCRIPT = ROOT / "scripts" / "build_official_program_coverage.py"
REGISTRY = ROOT / "audit" / "OFFICIAL_PROGRAM_COVERAGE_2026_2027.json"
MANUALS = ("1SPE", "TSPE", "TCOMPL", "TEXPERTES", "1NSI", "TNSI")
STATES = {
    "UNMAPPED",
    "STRUCTURALLY_MAPPED",
    "CONTENT_REVIEW_PENDING",
    "SCIENTIFIC_PASS",
    "PEDAGOGICAL_PASS",
    "FULL",
}
SOURCE_FIELDS = (
    "course_sources",
    "method_sources",
    "exercise_sources",
    "correction_sources",
    "assessment_sources",
    "remediation_sources",
)


def _producer():
    spec = importlib.util.spec_from_file_location("official_coverage", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _declared_dead_paths() -> set[tuple[str, str]]:
    """Les chemins morts que l'agregat declare, atome par atome."""

    payload = json.loads(
        (ROOT / "audit" / "OFFICIAL_PROGRAM_COVERAGE_2026_2027.json").read_text(
            encoding="utf-8"
        )
    )
    return {
        (row["atom_id"], row["path"])
        for row in payload["coverage_evidence_paths_missing"]
    }


def test_every_dead_evidence_path_is_enumerated() -> None:
    """Le compteur et la liste disent la meme chose, et rien n'est efface."""

    payload = json.loads(
        (ROOT / "audit" / "OFFICIAL_PROGRAM_COVERAGE_2026_2027.json").read_text(
            encoding="utf-8"
        )
    )
    morts = payload["coverage_evidence_paths_missing"]
    assert payload["summary"]["COVERAGE_EVIDENCE_PATHS_MISSING"] == len(morts)
    assert morts, "l'artefact doit enumerer les chemins morts tant qu'il y en a"
    for entree in morts:
        assert not (ROOT / entree["path"]).exists(), entree
        assert entree["atom_id"] and entree["chapter"] and entree["field"]


def _rows() -> list[dict]:
    return [
        row
        for manual in MANUALS
        for row in json.loads(
            (MATRIX_ROOT / f"{manual}.json").read_text(encoding="utf-8")
        )["rows"]
    ]


def test_six_current_official_programme_matrices_exist() -> None:
    assert {path.stem for path in MATRIX_ROOT.glob("*.json")} == set(MANUALS)


def test_official_programme_coverage_registry_is_current() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_every_mandatory_atom_has_exactly_one_coverage_row() -> None:
    atoms = json.loads(ATOMS_PATH.read_text(encoding="utf-8"))["atoms"]
    mandatory_ids = {
        atom["atom_id"] for atom in atoms if atom["mandatory"] == "YES"
    }
    rows = _rows()

    assert len(rows) == len(mandatory_ids)
    assert {row["atom_id"] for row in rows} == mandatory_ids
    assert len({row["atom_id"] for row in rows}) == len(rows)


def test_producer_itself_rejects_missing_or_duplicate_mandatory_atoms() -> None:
    producer = _producer()
    atoms = [
        {"atom_id": "A", "mandatory": "YES"},
        {"atom_id": "B", "mandatory": "YES"},
        {"atom_id": "N", "mandatory": "NO"},
    ]
    producer._validate_mandatory_bijection(atoms, [{"atom_id": "A"}, {"atom_id": "B"}])
    for rows in ([{"atom_id": "A"}], [{"atom_id": "A"}, {"atom_id": "A"}, {"atom_id": "B"}]):
        try:
            producer._validate_mandatory_bijection(atoms, rows)
        except ValueError as exc:
            assert "MANDATORY_ATOM_BIJECTION" in str(exc)
        else:  # pragma: no cover - assertion message is more useful than pytest magic here
            raise AssertionError("a missing or duplicate mandatory atom must fail closed")


def test_coverage_rows_are_traceable_and_do_not_fake_full() -> None:
    atoms = {
        atom["atom_id"]: atom
        for atom in json.loads(ATOMS_PATH.read_text(encoding="utf-8"))["atoms"]
    }
    for row in _rows():
        atom = atoms[row["atom_id"]]
        assert row["official_document_id"] == atom["atom_id"]
        assert row["NOR"] == atom["authority_NOR"]
        assert row["official_section"] == atom["official_section"]
        assert row["official_page_or_anchor"] == atom["official_page_or_anchor"]
        assert row["official_wording_or_short_paraphrase"] == atom[
            "short_official_wording_or_paraphrase"
        ]
        assert row["obligation_type"] == atom["type"]
        assert row["mandatory"] == "YES"
        assert row["manual"] == atom["manual"]
        assert row["coverage_status"] in STATES
        assert row["review_status"] in {
            "NOT_REVIEWED",
            "PROGRAM_REVIEWED",
            "SCIENTIFIC_REVIEWED",
            "PEDAGOGICAL_REVIEWED",
            "HUMAN_APPROVAL_PENDING",
        }
        assert row["programme_state"] in {"PASS", "PENDING"}
        assert row["scientific_state"] in {"PASS", "PENDING"}
        assert row["pedagogical_state"] in {"PASS", "PENDING"}
        assert row["assessment_alignment_state"] in {"PASS", "PENDING"}

        if row["coverage_status"] != "UNMAPPED":
            assert row["chapter"]
            assert row["contract_capacity"]

        if row["coverage_status"] in {
            "CONTENT_REVIEW_PENDING",
            "SCIENTIFIC_PASS",
            "PEDAGOGICAL_PASS",
            "FULL",
        }:
            for field in SOURCE_FIELDS:
                assert row[field], (row["atom_id"], field)
            assert row["evidence_paths"]
            # UN CHEMIN MORT N'EST PAS UNE PREUVE. Vingt-cinq sources nommees
            # par la revue de programme designent des fichiers renommes ou
            # supprimes depuis. Le producteur les enumere dans
            # `coverage_evidence_paths_missing` ; les reparer suppose de
            # retrouver le fichier qui a remplace chacun, ce qui est un
            # jugement editorial et non une derivation. Le test exige donc que
            # CHAQUE chemin mort soit nomme dans l'artefact -- jamais qu'il
            # soit taise.
            for relative in row["evidence_paths"]:
                if (ROOT / relative).exists():
                    continue
                assert (row["atom_id"], relative) in _declared_dead_paths(), (
                    row["atom_id"],
                    relative,
                )

        if row["coverage_status"] == "FULL":
            assert row["programme_state"] == "PASS"
            assert row["scientific_state"] == "PASS"
            assert row["pedagogical_state"] == "PASS"
            assert row["assessment_alignment_state"] == "PASS"


def test_every_mandatory_atom_is_structurally_mapped() -> None:
    rows = _rows()

    assert all(row["coverage_status"] != "UNMAPPED" for row in rows)


def test_every_structural_mapping_names_a_real_contract_capacity() -> None:
    rows = _rows()
    # `contract_capacity` nomme une capacite du CONTRAT, c'est-a-dire le
    # couple chapitre + code local. Pour presque tous les chapitres ce couple
    # coincide avec `ref_capacite`, et la comparaison passait ; le second
    # degre, dont les references officielles portent un segment `-2026-`, a
    # montre que les deux ne sont pas la meme chose. On accepte donc les deux
    # ecritures, et la lecture de `ref_capacite` tolere son absence : trois
    # capacites n'en ont pas, et lire la cle sans defaut faisait planter le
    # test avant qu'il ne verifie rien.
    contract_refs: set[str | None] = set()
    for base in (
        ROOT / "Mathematiques" / "manuel-maths" / "chapitres",
        ROOT / "NSI" / "chapitres",
    ):
        for path in base.glob("*/contrat.yaml"):
            chapter = path.parent.name
            for capacity in yaml.safe_load(
                path.read_text(encoding="utf-8")
            ).get("capacites", []):
                contract_refs.add(f"{chapter}-{capacity['code']}")
                if capacity.get("ref_capacite"):
                    contract_refs.add(capacity["ref_capacite"])
    contract_refs.update(
        capacity["ref_capacite"]
        for path in (ROOT / "audit" / "official_program_contracts").glob("*.yaml")
        for capacity in yaml.safe_load(path.read_text(encoding="utf-8")).get(
            "capacites", []
        )
    )

    for row in rows:
        if row["coverage_status"] == "UNMAPPED":
            continue
        refs = re.split(r"\s*(?:/|\+)\s*", row["contract_capacity"])
        assert all(ref in contract_refs for ref in refs), (
            row["atom_id"],
            row["contract_capacity"],
        )


def test_coverage_summary_is_derived_from_rows() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    rows = _rows()
    summary = payload["summary"]

    assert summary["mandatory_atoms"] == len(rows)
    assert summary["mapped_mandatory_atoms"] == sum(
        row["coverage_status"] != "UNMAPPED" for row in rows
    )
    assert summary["unmapped_mandatory_atoms"] == sum(
        row["coverage_status"] == "UNMAPPED" for row in rows
    )
    assert summary["full_atoms"] == sum(
        row["coverage_status"] == "FULL" for row in rows
    )


def test_1spe_suites_c8_atoms_reference_the_existing_qcm_assessment() -> None:
    rows = {
        row["atom_id"]: row
        for row in json.loads(
            (MATRIX_ROOT / "1SPE.json").read_text(encoding="utf-8")
        )["rows"]
    }
    qcm_path = (
        "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/"
        "qcm/1SPE-SUITES-QCM.json"
    )

    for atom_id in ("1SPE-OFFICIAL-053", "1SPE-OFFICIAL-059"):
        row = rows[atom_id]
        assert row["contract_capacity"] == "1SPE-SUITES-C8"
        assert row["assessment_sources"] == [f"{qcm_path}#Q3"]
        assert qcm_path in row["evidence_paths"]
        assert row["coverage_status"] == "CONTENT_REVIEW_PENDING"
        assert row["gap_type"] is None
        assert row["assessment_alignment_state"] == "PENDING"
        assert row["scientific_state"] == "PENDING"
        assert row["pedagogical_state"] == "PENDING"
