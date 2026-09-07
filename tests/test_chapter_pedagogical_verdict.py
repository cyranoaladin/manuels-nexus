"""La revue pedagogique derive ses verdicts, elle ne les affirme pas.

Le nombre d'exercices ne dit rien : c'est la lecon du remplissage. Ce que ce
producteur mesure, ce sont les quatre couvertures que le critere qualitatif
exige -- application directe, variation, raisonnement, synthese -- lues sur
les competences et les parcours que chaque exercice DECLARE.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "audit/CHAPTER_PEDAGOGICAL_VERDICT.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "pedagogical_verdict", ROOT / "scripts/build_chapter_pedagogical_verdict.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["pedagogical_verdict"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_every_chapter_receives_a_verdict(payload: dict) -> None:
    assert payload["summary"]["CHAPTERS_AUDITED"] == 52
    for row in payload["chapters"]:
        assert row["PEDAGOGICAL_VERDICT"] in {
            "STRONG", "ADEQUATE", "WEAK", "UNUSABLE"
        }


def test_the_verdict_is_the_worst_axis_not_an_average(payload: dict) -> None:
    """Une moyenne noierait un axe faible dans cinq axes forts.

    Un chapitre dont les corriges manquent n'est pas « globalement adequat » :
    il est inutilisable sur ce point, et c'est ce point qui decide.
    """

    ordre = {"STRONG": 3, "ADEQUATE": 2, "WEAK": 1, "UNUSABLE": 0}
    for row in payload["chapters"]:
        valeurs = [v for v in row.values() if isinstance(v, str) and v in ordre]
        # Le verdict lui-meme est l'une de ces valeurs : on le retire avant de
        # recalculer, sinon on comparerait le resultat a lui-meme.
        valeurs.remove(row["PEDAGOGICAL_VERDICT"])
        attendu = min(valeurs, key=lambda v: ordre[v])
        assert row["PEDAGOGICAL_VERDICT"] == attendu, row["CHAPTER_ID"]


def test_full_coverage_alone_never_earns_a_strong_verdict(producer) -> None:
    """Une capacite servie par un seul exercice n'est pas entrainee.

    C'est la regle qui empeche de relire « chaque capacite a un exercice »
    comme « le chapitre est riche ».
    """

    for row in json.loads(ARTIFACT.read_text(encoding="utf-8"))["chapters"]:
        if row["EXERCISE_DIVERSITY"] == "NOT_APPLICABLE_PROJECT_ASSESSMENT":
            continue
        if row["coverage"]["CAPACITIES_WITH_REAL_DIVERSITY_GAP"]:
            assert row["EXERCISE_DIVERSITY"] in {"WEAK", "UNUSABLE"}, row["CHAPTER_ID"]


def test_the_weak_chapters_are_named_with_their_uncovered_capacities(
    payload: dict,
) -> None:
    """Un verdict sans la liste de ce qui manque n'est pas actionnable."""

    for row in payload["chapters"]:
        if row["PEDAGOGICAL_VERDICT"] in {"WEAK", "UNUSABLE"}:
            actionnable = (
                any(row["uncovered"].values())
                or row["coverage"]["CAPACITIES_WITH_REAL_DIVERSITY_GAP"]
                or row["coverage"]["CAPACITY_ASSIGNMENT_MISSING"]
            )
            assert actionnable, row["CHAPTER_ID"]


def test_the_committed_verdict_matches_the_producer(producer) -> None:
    assert producer.main(["--check"]) == 0


def test_every_capacity_gap_names_what_is_missing(payload: dict) -> None:
    """Un `REAL_DIVERSITY_GAP` sans motif serait un quota deguise.

    Le mandat refuse la regle implicite « une capacite -> deux nouveaux
    exercices ». La seule justification recevable est la FONCTION absente.
    """

    for row in payload["chapters"]:
        for analyse in row["per_capacity"]:
            if not analyse["REAL_DIVERSITY_GAP"]:
                continue
            assert analyse["MISSING_FUNCTIONS"], (
                row["CHAPTER_ID"], analyse["CAPACITY_ID"]
            )
            assert analyse["RATIONALE"], (row["CHAPTER_ID"], analyse["CAPACITY_ID"])


def test_a_capacity_can_be_sufficient_with_two_exercises(producer) -> None:
    """La suffisance est qualitative : un effectif ne la decide pas.

    Deux exercices -- une application, un raisonnement -- suffisent. Dix
    applications directes ne suffisent pas. C'est la difference entre un
    contrat de diversite et une cible de volume.
    """

    from exercise_function_taxonomy import diversity_verdict, functions_of

    deux = [
        functions_of("Calculer $f'(x)$.", {"competences": ["calculer"]}),
        functions_of(
            "Demontrer que $f$ est croissante sur $I$.",
            {"competences": ["raisonner"]},
        ),
    ]
    assert diversity_verdict(deux)["verdict"] == "DIVERSITY_SUFFICIENT"

    dix = [functions_of("Calculer $f'(x)$.", {"competences": ["calculer"]})] * 10
    assert diversity_verdict(dix)["verdict"] == "REAL_DIVERSITY_GAP"


def test_a_project_assessed_chapter_is_measured_on_its_project(payload: dict) -> None:
    """L'exemption change ce qu'on mesure, elle n'annule pas l'exigence."""

    projet = next(
        r for r in payload["chapters"] if r["ASSESSMENT_MODE"] == "PROJECT_ASSESSMENT"
    )
    assert projet["EXERCISE_DIVERSITY"] == "NOT_APPLICABLE_PROJECT_ASSESSMENT"
    for axe in (
        "PROJECT_BRIEF", "PROJECT_CRITERIA_GRID",
        "PROJECT_KNOWLEDGE_CHECK", "PROJECT_ADAPTED_VERSION",
    ):
        assert axe in projet, axe
    # Un chapitre projet sans grille criteriee doit rester bloquant : on le
    # verifie en mutant l'axe, faute de quoi l'exemption serait un blanc-seing.
    ordre = {"STRONG": 3, "ADEQUATE": 2, "WEAK": 1, "UNUSABLE": 0}
    mute = dict(projet, PROJECT_CRITERIA_GRID="WEAK")
    valeurs = [
        v for k, v in mute.items()
        if isinstance(v, str) and v in ordre and k != "PEDAGOGICAL_VERDICT"
    ]
    assert min(valeurs, key=lambda v: ordre[v]) == "WEAK"


def test_a_programme_reference_counts_as_a_capacity_attachment(payload: dict) -> None:
    """Deux cles nomment la meme chose, et n'en lire qu'une invente des lacunes.

    Les chapitres NSI rattachent leurs exercices par la reference du
    programme (`P-BASE-01`), les chapitres de mathematiques par le code local
    du contrat (`C1`). Un lecteur qui n'ouvre que `capacites_codes` voit neuf
    chapitres « sans aucun rattachement » alors qu'ils sont rattaches a cent
    pour cent -- et enverrait ecrire des exercices la ou il n'en manque
    aucun. Le producteur doit resoudre les deux.
    """

    nsi = [
        r for r in payload["chapters"]
        if r["CHAPTER_ID"].endswith(
            ("TYPES-BASE", "RESEAUX", "TABLES", "WEB-IHM", "ARCHITECTURE-OS")
        )
    ]
    assert nsi, "les chapitres NSI de reference doivent etre audites"
    for row in nsi:
        assert not row["coverage"]["CAPACITY_ASSIGNMENT_MISSING"], row["CHAPTER_ID"]
        assert row["coverage"]["EXERCISES_WITHOUT_CAPACITY"] == 0, row["CHAPTER_ID"]
        assert any(
            a["CURRENT_EXERCISES"] for a in row["per_capacity"]
        ), row["CHAPTER_ID"]


def test_the_pooled_reading_activates_when_the_attachment_is_mostly_absent(
    producer, tmp_path, monkeypatch,
) -> None:
    """Le repli existe, meme si le corpus n'en a plus besoin aujourd'hui.

    Une population vide ne prouve pas qu'un detecteur fonctionne : on le
    verifie donc sur un chapitre fabrique, ou la majorite des exercices ne
    declare aucune capacite. La diversite doit alors se lire sur le vivier
    entier et le rattachement etre signale a part -- jamais l'inverse.
    """

    chapitre = tmp_path / "corpus" / "TEST-RATTACHEMENT"
    (chapitre / "exercices").mkdir(parents=True)
    (chapitre / "contrat.yaml").write_text(
        "capacites:\n"
        "  - { code: C1, ref_capacite: P-T-01, libelle_eleve: \"Je sais calculer.\" }\n",
        encoding="utf-8",
    )
    enonces = [
        ('{"id": "T-EX-1", "capacites_codes": ["C1"], "parcours": 1}',
         "Calculer $2+2$."),
        ('{"id": "T-EX-2", "parcours": 1}', "Calculer $3+3$."),
        ('{"id": "T-EX-3", "parcours": 2}',
         "Une usine produit des pieces. Demontrer que la cadence est stable."),
    ]
    for index, (meta, corps) in enumerate(enonces, start=1):
        (chapitre / "exercices" / f"T-EX-{index}.tex").write_text(
            f"% META: {meta}\n{corps}\n", encoding="utf-8"
        )

    monkeypatch.setattr(producer, "ROOT", tmp_path)
    monkeypatch.setattr(producer, "CORPORA", ("corpus",))
    row = producer.audit("TEST-RATTACHEMENT")

    assert row["coverage"]["CAPACITY_ASSIGNMENT_MISSING"] is True
    assert row["coverage"]["EXERCISES_WITHOUT_CAPACITY"] == 2
    assert row["CAPACITY_ASSIGNMENT"] == "WEAK"
    # Le vivier entier porte une application directe ET une situation de
    # transfert : la diversite ne doit donc PAS etre declaree en defaut.
    assert [a["CAPACITY_ID"] for a in row["per_capacity"]] == ["CHAPTER_POOL"]
    assert row["per_capacity"][0]["REAL_DIVERSITY_GAP"] is False
    assert row["EXERCISE_DIVERSITY"] in {"STRONG", "ADEQUATE"}
