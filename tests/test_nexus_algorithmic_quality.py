"""Un chapitre ne passe pas au vert parce qu'il contient un `print`.

L'exigence de la collection -- NEXUS_ALGORITHMIC_QUALITY_STANDARD -- ne
demande pas seulement qu'un algorithme soit visible : elle demande qu'il soit
exploitable. Un bloc de code sans objectif enonce, sans activite ni
interpretation, ou publie sans oracle executable, ne fait pas travailler
l'eleve.

Ce n'est pas une obligation ministerielle : le BO NOMME des exemples
d'algorithme sans les imposer. Le standard, lui, est une decision editoriale,
et il porte son nom.
"""
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COUVERTURE = ROOT / "audit" / "OFFICIAL_TO_MANUAL_COVERAGE.json"
BLOC_VERIFY = re.compile(r"% BEGIN-VERIFY\n(.*?)% END-VERIFY", re.S)


@pytest.fixture(scope="module")
def standard():
    return json.loads(COUVERTURE.read_text(encoding="utf-8"))[
        "nexus_algorithmic_quality_standard"
    ]


def test_le_standard_dit_qu_il_n_est_pas_une_obligation_ministerielle(standard):
    assert "PAS une obligation du programme" in standard["nature"]


def test_toute_partie_citant_un_exemple_offre_un_travail_visible(standard):
    manquantes = [
        p for p in standard["parts"] if not p["manual_has_algorithmic_work"]
    ]
    assert not manquantes, [(p["manual"], p["official_part"]) for p in manquantes]


def test_ce_travail_est_exploitable_par_un_eleve(standard):
    """Visible ne suffit pas : il faut un objectif, une activite, un oracle."""
    inexploitables = [
        p for p in standard["parts"]
        if not p["ALGORITHMIC_WORK_PEDAGOGICALLY_ACTIONABLE"]
    ]
    assert not inexploitables, [
        (p["manual"], p["official_part"]) for p in inexploitables
    ]
    for partie in standard["parts"]:
        assert partie["actionable_evidence"], partie["official_part"]


def test_un_bloc_de_code_decoratif_ne_suffit_pas():
    """Mutation : un objet qui ne montre qu'un `print` echoue au controle."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from manual_objects import (
        ACTIVITE_ALGORITHMIQUE,
        ALGORITHME_MONTRE,
        OBJECTIF_ALGORITHMIQUE,
    )

    decoratif = "\\begin{python}\nprint(2 + 2)\n\\end{python}\n"
    assert ALGORITHME_MONTRE.search(decoratif)
    assert not OBJECTIF_ALGORITHMIQUE.search(decoratif)
    assert not ACTIVITE_ALGORITHMIQUE.search(decoratif)


def test_un_bloc_de_verification_seul_ne_montre_aucun_algorithme():
    sys.path.insert(0, str(ROOT / "scripts"))
    from manual_objects import ALGORITHME_MONTRE

    assert not ALGORITHME_MONTRE.search("% BEGIN-VERIFY\n% assert 1\n% END-VERIFY")


def test_les_preuves_exploitables_publient_du_code_verifie(standard):
    """Chaque preuve retenue publie un oracle, et cet oracle s'execute."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from manual_objects import charger_contrats, charger_objets, charger_transversaux

    contrats = charger_contrats()
    par_id = {
        o.object_id: o for o in charger_objets(contrats) + charger_transversaux()
    }
    examines = 0
    for partie in standard["parts"]:
        for oid in partie["actionable_evidence"]:
            objet = par_id[oid]
            assert objet.shows_algorithmic_work, oid
            assert objet.algorithmic_objective, oid
            assert objet.algorithmic_activity, oid
            if objet.publishes_python:
                assert objet.has_executable_oracle, oid
                texte = (ROOT / objet.path).read_text(encoding="utf-8")
                assert BLOC_VERIFY.search(texte), oid
            if objet.algorithmic_task:
                assert objet.algorithmic_answers, oid
            examines += 1
    assert examines >= len(standard["parts"])
