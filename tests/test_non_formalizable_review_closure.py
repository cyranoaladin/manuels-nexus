"""La dimension `mathematics` doit refuser ce qu'elle n'a pas examiné.

Un oracle prouve ce qui se calcule. Quatre cent dix-sept objets n'en portent
pas et ne peuvent pas en porter. Une dimension qui passe en les déclarant
`NOT_APPLICABLE` ne prouve rien à leur sujet : ces tests exigent qu'elle le
dise, et qu'elle sache redevenir verte quand la revue est faite.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_non_formalizable_review_closure as closure  # noqa: E402
import non_formalizable_reviews as declarations  # noqa: E402

ARTEFACT = ROOT / "audit/NON_FORMALIZABLE_REVIEW_CLOSURE.json"
DIMENSION = ROOT / "audit/DIMENSION_MATHEMATICS.json"


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(ARTEFACT.read_text(encoding="utf-8"))


# ══════════════════════════════════════════════════════════════════════════
# La fermeture elle-même
# ══════════════════════════════════════════════════════════════════════════
ETATS = (
    "PENDING",
    "SEMANTICALLY_REVIEWED",
    "REVIEW_INHERITED_BY_IDENTICAL_CONTENT",
    "COVERED_BY_QCM_PROOF_CHAIN",
    "TRULY_NOT_REQUIRING_MATHEMATICAL_REVIEW",
)


def test_the_population_is_partitioned_without_loss(payload: dict) -> None:
    """Cinq etats, leur somme vaut la population, et rien ne tombe en OTHER."""

    resume = payload["summary"]
    assert resume["STATES_SUM_EQUALS_TOTAL"] is True
    assert resume["MATHEMATICAL_NON_FORMALIZABLE_TOTAL"] == len(payload["objects"])
    assert (
        resume["MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING"]
        + resume["COVERED_BY_QCM_EVIDENCE"]
        + resume["SEMANTICALLY_REVIEWED"]
        + resume["REVIEW_INHERITED_BY_IDENTICAL_CONTENT"]
        + resume["TRULY_NOT_REQUIRING_MATHEMATICAL_REVIEW"]
        == resume["MATHEMATICAL_NON_FORMALIZABLE_TOTAL"]
    )
    assert resume["OTHER"] == 0
    assert resume["NON_FORMALIZABLE_POPULATION_UNRECONCILED"] == 0
    assert {ligne["state"] for ligne in payload["objects"]} <= set(ETATS)


def test_an_object_freed_of_review_names_the_proof_that_frees_it(
    payload: dict,
) -> None:
    """Aucun etat de sortie ne se donne sans dire ce qui le fonde.

    `TRULY_NOT_REQUIRING_MATHEMATICAL_REVIEW` n'est pas une dispense mais une
    preuve de contenance ; `REVIEW_INHERITED_BY_IDENTICAL_CONTENT` nomme
    l'objet dont il herite et le condense qui le prouve.
    """

    for ligne in payload["objects"]:
        if ligne["state"] == "PENDING":
            continue
        assert ligne["evidence"], ligne["object_id"]
        if ligne["state"] == "REVIEW_INHERITED_BY_IDENTICAL_CONTENT":
            assert ligne["evidence"].startswith("SEMANTIC_DIGEST_IDENTICAL:")
            assert "identique a" in (ligne["detail"] or "")


def test_only_a_satellite_can_be_freed_by_containment(payload: dict) -> None:
    """Un cours ou une methode enonce ; il ne peut pas etre couvert par autrui."""

    for ligne in payload["objects"]:
        if ligne["state"] == "TRULY_NOT_REQUIRING_MATHEMATICAL_REVIEW":
            assert ligne["type_objet"] in {"coup_de_pouce", "amenagee"}, (
                ligne["object_id"]
            )


def test_the_closure_approves_nothing(payload: dict) -> None:
    assert payload["summary"]["APPROVES_NOTHING"] is True
    assert "VALIDATED_BY_EVIDENCE" in payload["authority_note"]
    assert "approved" not in json.dumps(payload["objects"], ensure_ascii=False)


def test_the_qcm_objects_reuse_the_existing_proof_instead_of_duplicating_it(
    payload: dict,
) -> None:
    """§13 : ne pas dupliquer une revue qui existe déjà."""
    couverts = [
        ligne for ligne in payload["objects"]
        if ligne["state"] == "COVERED_BY_QCM_PROOF_CHAIN"
    ]
    assert couverts
    for ligne in couverts:
        assert ligne["type_objet"] in ("qcm", "qcm_diagnostics")
        assert ligne["evidence"] == "audit/QCM_REVIEW_CLOSURE.json"
        assert "toutes établies" in ligne["detail"]


def test_a_single_unproven_question_closes_the_door(monkeypatch) -> None:
    """Un QCM dont une question n'est pas établie n'est pas couvert."""
    reels = closure._qcm_question_states()
    premiere_source = sorted(reels)[0]
    abime = copy.deepcopy(reels)
    identifiant = sorted(abime[premiere_source])[0]
    abime[premiere_source][identifiant] = "HUMAN_REVIEW_REQUIRED"
    monkeypatch.setattr(closure, "_qcm_question_states", lambda: abime)
    resultat = closure.build()
    concernes = [
        ligne for ligne in resultat["objects"]
        if ligne["type_objet"] in ("qcm", "qcm_diagnostics")
        and premiere_source.rsplit("/", 1)[0] in ligne["path"]
    ]
    assert concernes
    assert all(ligne["state"] == "PENDING" for ligne in concernes)
    assert all("sans preuve" in (ligne["detail"] or "") for ligne in concernes)


# ══════════════════════════════════════════════════════════════════════════
# La table de déclaration refuse une revue qui n'en est pas une
# ══════════════════════════════════════════════════════════════════════════
def test_a_review_field_too_short_is_refused() -> None:
    with pytest.raises(ValueError, match="trop court"):
        declarations.revue(
            "chemin/fictif.tex",
            science="trop court",
            programme="La capacité C1 du contrat de chapitre, telle qu'elle est écrite.",
            pedagogy="Ce que l'objet fait pour l'élève, décrit assez pour être discutable.",
            editorial="Notations et renvois vérifiés, conformes aux conventions du manuel.",
        )


def test_a_duplicate_review_is_refused() -> None:
    chemin = "chemin/unique-pour-ce-test.tex"
    champs = {
        "science": "L'affirmation mathématique est exacte, et voici pourquoi elle l'est.",
        "programme": "La capacité C1 du contrat de chapitre, telle qu'elle est écrite.",
        "pedagogy": "Ce que l'objet fait pour l'élève, décrit assez pour être discutable.",
        "editorial": "Notations et renvois vérifiés, conformes aux conventions du manuel.",
    }
    declarations.revue(chemin, **champs)
    try:
        with pytest.raises(ValueError, match="déjà déclarée"):
            declarations.revue(chemin, **champs)
    finally:
        declarations.REVIEWS.pop(chemin, None)


# ══════════════════════════════════════════════════════════════════════════
# La quatrième condition de la dimension
# ══════════════════════════════════════════════════════════════════════════
def test_the_dimension_declares_its_four_conditions() -> None:
    dimension = json.loads(DIMENSION.read_text(encoding="utf-8"))
    assert dimension["summary"]["PASS_CONDITIONS"] == [
        "MATHEMATICAL_ASSERTION_FAILURES = 0",
        "MISSING_ORACLE = 0",
        "MATHEMATICS_UNKNOWN = 0",
        "MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING = 0",
    ]


def test_the_dimension_fails_while_reviews_are_pending() -> None:
    """Le rouge est sain : il dit ce qui reste, au lieu de le taire."""
    dimension = json.loads(DIMENSION.read_text(encoding="utf-8"))
    pending = dimension["summary"]["MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING"]
    codes = {constat["code"] for constat in dimension["findings"]}
    if pending:
        assert dimension["status"] == "failed"
        assert "MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING" in codes
    else:
        assert "MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING" not in codes


def test_a_closed_review_removes_the_blocking_finding(tmp_path, monkeypatch) -> None:
    """Mutation : si la fermeture ne laisse rien en attente, le constat tombe."""
    import build_dimension_mathematics as maths

    ferme = json.loads(ARTEFACT.read_text(encoding="utf-8"))
    ferme["summary"]["MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING"] = 0
    faux = tmp_path / "closure.json"
    faux.write_text(json.dumps(ferme, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(maths, "NON_FORMALIZABLE_CLOSURE", faux)
    payload = maths.build()
    codes = {constat["code"] for constat in payload["findings"]}
    assert "MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING" not in codes
    assert payload["summary"]["MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING"] == 0


def test_an_incoherent_closure_is_itself_a_finding(tmp_path, monkeypatch) -> None:
    import build_dimension_mathematics as maths

    incoherent = json.loads(ARTEFACT.read_text(encoding="utf-8"))
    incoherent["summary"]["STATES_SUM_EQUALS_TOTAL"] = False
    faux = tmp_path / "closure.json"
    faux.write_text(json.dumps(incoherent, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(maths, "NON_FORMALIZABLE_CLOSURE", faux)
    codes = {constat["code"] for constat in maths.build()["findings"]}
    assert "NON_FORMALIZABLE_CLOSURE_INCOHERENT" in codes


def test_a_missing_closure_is_never_silent(tmp_path, monkeypatch) -> None:
    """Absence de preuve n'est pas preuve d'absence de dette."""
    import build_dimension_mathematics as maths

    monkeypatch.setattr(
        maths, "NON_FORMALIZABLE_CLOSURE", tmp_path / "absent.json"
    )
    payload = maths.build()
    codes = {constat["code"] for constat in payload["findings"]}
    assert "NON_FORMALIZABLE_CLOSURE_MISSING" in codes
    assert payload["status"] == "failed"
