import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "audit" / "PROGRAMME_COVERAGE_MATRIX_2026_2027.json"
MANUALS = {"1SPE", "TSPE", "TCOMPL", "TEXPERTES", "1NSI", "TNSI"}


def test_candidate_crosswalk_never_claims_official_matrix_completion():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert set(payload["manuals"]) == MANUALS
    assert payload["summary"]["official_authorities"] == "6/6"
    assert payload["status"] == "REJECTED_AS_PROGRAMME_COVERAGE_MATRIX"
    assert payload["summary"]["programme_coverage_complete"] is False
    assert payload["summary"]["official_atoms_uninventoried"] is True
    # Le nombre d'atomes internes suit le programme applicable : le figer ferait
    # echouer le test a chaque evolution reglementaire legitime, et inviterait a
    # ajuster le chiffre plutot qu'a examiner la cause. Ce qui doit tenir est la
    # coherence entre le compteur publie et le contenu reellement publie.
    mandatory = [atom for atom in payload["atoms"] if atom["mandatory_for_coverage"] == "YES"]
    assert payload["summary"]["candidate_internal_atoms"] == len(mandatory)
    assert mandatory, "une matrice sans aucun atome obligatoire ne prouve rien"
    assert payload["summary"]["mandatory_missing"] is None
    assert payload["summary"]["unsupported_claim"] == 0
    assert payload["summary"]["out_of_scope_with_proof"] == 3
    assert payload["summary"]["wrong_year"] == 2

    required = {
        "official_document_id",
        "NOR",
        "official_section",
        "official_page_or_anchor",
        "official_wording_or_short_paraphrase",
        "obligation_type",
        "mandatory",
        "manual",
        "chapter",
        "contract_capacity",
        "course_sources",
        "method_sources",
        "exercise_sources",
        "assessment_sources",
        "remediation_sources",
        "coverage_status",
        "evidence_paths",
        "review_status",
    }
    assert all(required <= atom.keys() for atom in payload["atoms"])
    assert all(atom["official_page_or_anchor"].startswith("UNVERIFIED_CANDIDATE:") for atom in payload["atoms"])
    assert all(atom["coverage_status"] != "FULL" for atom in payload["atoms"])
    assert all(atom["review_status"] == "OFFICIAL_ATOM_REDERIVATION_REQUIRED" for atom in payload["atoms"])


def test_exam_or_assessment_alignment_is_present_for_every_manual():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    alignment = payload["exam_or_assessment_alignment"]
    assert set(alignment) == MANUALS
    assert alignment["1SPE"]["calculator"] == "forbidden"
    assert alignment["TNSI"]["written_raw_scale"] == 20
    assert alignment["TNSI"]["practical_raw_scale"] == 20
    assert alignment["TNSI"]["written_weight"] == 0.75
    assert alignment["TNSI"]["practical_weight"] == 0.25
    assert alignment["TCOMPL"]["ASSESSMENT_REGIME"] == "optional_subject_regime"
    assert alignment["TEXPERTES"]["ASSESSMENT_REGIME"] == "optional_subject_regime"


def test_programme_coverage_artifacts_match_generator():
    completed = subprocess.run(
        [sys.executable, "scripts/build_programme_coverage_matrix.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_the_second_degree_atoms_follow_the_2026_programme_nomenclature():
    """Verrou BO 2026 : 1SPE applique le programme du 2 avril 2026 des 2026-2027.

    Les atomes hérités `1SPE-SECOND-DEGRE-C*`, issus de la baseline 2019, ne
    doivent plus figurer : les laisser auditerait le chapitre contre un
    programme qui ne lui est plus applicable.
    """
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    second_degree = [
        atom["atom_id"] for atom in payload["atoms"]
        if atom["atom_id"].startswith("1SPE-SECOND-DEGRE")
    ]
    assert second_degree
    assert all("-2026-" in atom_id for atom_id in second_degree), second_degree


def test_a_facet_is_declared_but_never_counted_as_an_official_atom():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    facets = payload["contract_facets_without_official_alias"]
    assert facets, "les facettes sans alias officiel doivent rester visibles"
    atom_ids = {atom["atom_id"] for atom in payload["atoms"]}
    for facet in facets:
        assert facet["facet_of"] in atom_ids
        assert facet["contract_capacity"] not in atom_ids
        assert facet["carried_by"] != facet["contract_capacity"]
