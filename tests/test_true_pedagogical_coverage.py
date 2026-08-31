"""La couverture pedagogique se mesure sur les corps, jamais sur les META.

Le P0 de clonage a montre ce qu'un compteur naif credite : dix-sept fiches
identiques declarees C1 a C16 creditaient seize capacites alors qu'une seule,
C7, etait traitee. Ce producteur retire les credits invalides avant de
compter.

Ces tests protegent surtout la mesure elle-meme contre deux erreurs qui
FABRIQUENT des lacunes inexistantes -- et une lacune inventee coute aussi cher
qu'une lacune ignoree : elle envoie reecrire du contenu qui va tres bien.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COVERAGE = ROOT / "audit/TRUE_PEDAGOGICAL_COVERAGE.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "true_coverage", ROOT / "scripts/build_true_pedagogical_coverage.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(COVERAGE.read_text(encoding="utf-8"))


def test_the_committed_coverage_matches_the_producer(producer) -> None:
    assert producer.main(["--check"]) == 0


def test_the_backlog_is_exact_and_counted_in_authoring_units(payload: dict) -> None:
    inventory = payload["inventory"]
    backlog = payload["authoring_backlog"]

    assert len(backlog) == inventory["authoring_units_required"]
    # Trois etats, pas deux : une cellule servie uniquement par des clones
    # dont le proprietaire n'est pas demontrable n'est ni pourvue ni vide.
    # La compter comme vide enverrait reecrire un contenu qui existe ; la
    # compter comme pourvue crediterait une capacite au hasard.
    assert (
        inventory["cells_with_valid_content"]
        + inventory["cells_with_indeterminate_credit"]
        + len(backlog)
        == inventory["cells"]
    )
    assert all(row["valid_objects"] == 0 for row in backlog)
    assert all(row["state"] == "MISSING" for row in backlog)
    # Une unite d'ecriture est un couple (capacite, role), jamais un fichier.
    assert len({(r["chapter"], r["capacity"], r["role"]) for r in backlog}) == len(
        backlog
    )


def test_a_correction_inherits_the_capacity_of_its_exercise(producer) -> None:
    """Sans cet heritage, 1SPE affichait vingt lacunes qui n'existent pas.

    Les corriges de 1SPE ne declarent pas de capacite : ils la tiennent de
    l'exercice qu'ils corrigent, via META.exercice_id. Un compteur qui
    l'ignore condamne un chapitre entier pour un defaut de mesure.
    """

    chapter = ROOT / "Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL"
    clone = producer._clone_module()
    sample = sorted((chapter / "corriges").glob("*.tex"))[0]
    meta = clone.read_meta(sample.read_text(encoding="utf-8"))

    assert not clone.declared_capacities(meta), "ce corrige ne declare pas de capacite"
    exercise_id = meta.get("exercice_id")
    assert exercise_id, "mais il nomme l'exercice dont il herite"

    # L'exercice nomme existe et porte, lui, une capacite : c'est elle que le
    # corrige doit se voir attribuer.
    inherited = None
    for path in (chapter / "exercices").glob("*.tex"):
        other = clone.read_meta(path.read_text(encoding="utf-8"))
        if other.get("id") == exercise_id:
            inherited = clone.declared_capacities(other)
            break
    assert inherited, f"{exercise_id} doit exister et porter une capacite"

    # Et le producteur doit effectivement la lui attribuer.
    covered = {
        (row["chapter"], row["capacity"])
        for row in producer.build_coverage()["authoring_backlog"]
        if row["role"] == "corriges"
    }
    assert (chapter.name, inherited[0]) not in covered, (
        "la capacite heritee ne doit pas etre comptee comme lacune de corrige"
    )


def test_1spe_has_no_gap_once_inheritance_is_applied(payload: dict) -> None:
    """Le controle de non-regression de la mesure elle-meme."""

    assert "1SPE" not in payload["per_manual"], (
        "1SPE ne doit porter aucune lacune : ses corriges heritent de leurs "
        "exercices, et l'oublier fabriquerait vingt fausses lacunes"
    )


def test_qcm_and_assessments_are_measured_by_their_own_producer(
    payload: dict,
) -> None:
    """Les mesurer ici produirait un chiffre faux, pas une lacune."""

    assert "qcm" not in payload["measured_roles"]
    assert "evaluations" not in payload["measured_roles"]
    assert set(payload["excluded_roles"]) == {"qcm", "evaluations"}
    assert (ROOT / "audit/QCM_GAP_METRICS.json").is_file()


def test_the_credit_rule_refuses_meta_only_claims(payload: dict, producer) -> None:
    """Aucun objet a credit invalide ne compte dans la couverture."""

    ledger = json.loads(
        (ROOT / "audit/P0_CONTENT_CLONE_LEDGER.json").read_text(encoding="utf-8")
    )
    invalid = set(ledger["objects_on_invalid_credit"])
    assert invalid, "le P0 reste ouvert ailleurs dans la collection"
    assert "META" in payload["credit_rule"]

    # La regle vaut partout ou des clones subsistent : aucune copie ne
    # conserve le credit d'une capacite qu'elle n'enseigne pas. Ce test
    # n'exige plus la presence du defaut dans un chapitre precis -- il
    # deviendrait faux le jour ou ce chapitre serait repare.
    indeterminate = set(ledger["objects_with_indeterminate_credit"])
    misrepresenting = [
        group
        for group in ledger["groups"]
        if group["disposition"] == "CAPACITY_MISREPRESENTING_CLONE"
    ]
    assert misrepresenting
    for group in misrepresenting:
        # Un corps ne credite jamais plus d'une capacite. Les membres d'un
        # groupe sans proprietaire demontrable ne creditent rien du tout :
        # ils ne sont ni credites ni declares manquants.
        credited = {row["path"] for row in group["members"]} - invalid - indeterminate
        capacities = {
            tuple(row["declared_capacity"])
            for row in group["members"]
            if row["path"] in credited
        }
        # L'invariant porte sur les CAPACITES creditees, pas sur le nombre de
        # fichiers : deux objets attestes par leur corps pour la meme capacite
        # la creditent une fois, pas deux.
        assert len(capacities) <= 1
