"""Les deux matrices TNSI, et le sens inverse.

Le programme dit ce qui doit etre enseigne ; la definition d'epreuve dit
comment cela sera evalue. Les confondre laisserait l'epreuve ajouter des
notions au programme -- ou reprocher au manuel de ne pas preparer a une
epreuve dont le programme ne parle pas.

La carte inverse pose la question que la couverture ne pose jamais : ce que le
manuel contient EN PLUS. Un manuel a le droit de depasser le programme ; il
n'a pas le droit de le faire sans le dire.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TNSI = ROOT / "audit" / "TNSI_EXAM_PREPARATION_MATRIX.json"
REVERSE = ROOT / "audit" / "OBJECTS_TO_OFFICIAL_REVERSE_MAP.json"


@pytest.fixture(scope="module")
def tnsi():
    return json.loads(TNSI.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def inverse():
    return json.loads(REVERSE.read_text(encoding="utf-8"))


def test_les_deux_autorites_tnsi_restent_distinctes(tnsi):
    assert tnsi["programme_authority"] == "MENE1921247A"
    assert tnsi["exam_authority"] == "MENE2516123N"
    assert tnsi["programme_authority"] != tnsi["exam_authority"]


def test_l_epreuve_n_ajoute_aucune_notion_au_programme(tnsi):
    """C'est la garde principale de cette matrice.

    Un manuel peut, a force de preparer l'epreuve, introduire des attendus que
    le programme ne porte pas. Chaque objet de preparation doit se rattacher a
    une capacite du programme.
    """
    assert tnsi["summary"]["EXAM_ONLY_NOTIONS"] == 0
    garde = next(
        e for e in tnsi["exam_requirements"]
        if e["requirement_id"] == "EXAM_ADDS_NO_NOTION_TO_THE_PROGRAMME"
    )
    assert garde["from_authority"] == tnsi["programme_authority"]
    assert garde["status"] == "COMPLETE"


def test_chaque_exigence_d_epreuve_cite_le_texte_qui_la_fonde(tnsi):
    for exigence in tnsi["exam_requirements"]:
        assert exigence["official_basis"], exigence["requirement_id"]
        assert exigence["from_authority"] in (
            tnsi["exam_authority"],
            tnsi["programme_authority"],
        )
        assert exigence["status"] in {"COMPLETE", "PARTIAL", "MISSING"}


def test_la_matrice_programme_ne_se_declare_pas_verte_avec_un_manque(tnsi):
    """Le verdict programme doit suivre les manques, pas les ignorer."""
    resume = tnsi["summary"]
    manquants = resume["TNSI_PROGRAMME_MANDATORY_MISSING"]
    assert len(tnsi["programme_mandatory_missing"]) == manquants
    assert resume["TNSI_PROGRAMME_MATRIX"] == ("PASS" if manquants == 0 else "FAIL")


def test_chaque_objet_du_manuel_recoit_un_statut(inverse):
    connus = set(inverse["classifications"])
    assert all(o["classification"] in connus for o in inverse["objects"])
    assert all(o["reason"] for o in inverse["objects"])
    assert inverse["summary"]["objects"] == len(inverse["objects"])


def test_un_objet_hors_programme_doit_dire_pourquoi_il_est_la(inverse):
    """Prerequis, enrichissement, entrainement : tous acceptables, tous dits.

    Ce qui ne l'est pas, c'est l'objet sans aucun statut : rien n'explique
    pourquoi l'eleve passe du temps dessus.
    """
    resume = inverse["summary"]
    sans_statut = [
        o for o in inverse["objects"] if o["classification"] == "OFF_TOPIC"
    ]
    assert resume["UNCLASSIFIED_OUT_OF_PROGRAMME_OBJECTS"] == len(sans_statut)
    for objet in sans_statut:
        assert not objet["mandatory_parents"], objet["object_id"]


def test_aucun_objet_ne_travaille_sur_un_programme_hors_annee(inverse):
    """Contamination par un programme qui ne regit pas l'edition."""
    assert inverse["summary"]["WRONG_YEAR_OBJECTS"] == 0
    assert not [
        o for o in inverse["objects"] if o["classification"] == "WRONG_YEAR"
    ]


def test_une_capacite_citee_mais_inexistante_est_signalee(inverse):
    """Un objet qui cite une capacite fantome parait rattache sans l'etre.

    Le defaut est invisible a la lecture : la metadonnee est bien remplie,
    elle designe simplement quelque chose qui n'existe pas.
    """
    pendantes = inverse["dangling_capacity_references"]
    assert inverse["summary"]["UNKNOWN_CAPACITIES_CITED"] == len(pendantes)
    assert pendantes, "aucune reference pendante detectee : le controle serait inerte"
    for atome, objets in pendantes.items():
        assert objets, atome


@pytest.mark.parametrize(
    "script",
    [
        "scripts/build_tnsi_exam_preparation_matrix.py",
        "scripts/build_objects_to_official_reverse_map.py",
    ],
)
def test_les_matrices_sont_bien_regenerees_par_leur_generateur(script):
    acheve = subprocess.run(
        [sys.executable, script, "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert acheve.returncode == 0, acheve.stdout + acheve.stderr
