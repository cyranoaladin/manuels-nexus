"""Une approbation suit un contenu, jamais un chemin de fichier.

Un objet qui garde `status: approved` apres avoir ete reecrit affirme qu'un
humain a relu ce que l'eleve lira. Rien ne le signale : le champ n'a pas
bouge. Vingt-neuf objets etaient dans ce cas.

Les deux gates demandes portent des noms explicites :
`SEMANTIC_CHANGE_PRESERVES_OLD_HUMAN_APPROVAL` doit valoir PASS -- c'est-a-dire
qu'aucun changement semantique ne conserve une vieille approbation --, et
`SEMANTIC_CHANGE_INVALIDATES_REVIEW_RECEIPT` doit valoir PASS.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RECUS = ROOT / "audit" / "CONTENT_APPROVAL_RECEIPTS.json"
NEUF = [
    "Mathematiques/manuel-maths/chapitres/1SPE-TRIGONOMETRIE/cours/11_C2_cosinus_sinus.tex",
    "Mathematiques/manuel-maths/chapitres/TCOMPL-INEGALITES/cours/10_C0_dispersion.tex",
    "Mathematiques/manuel-maths/chapitres/TSPE-GEOMETRIE-ESPACE/cours/12_C7_produit_scalaire.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-051.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-051.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-052.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-052.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-055.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-055.tex",
]


@pytest.fixture(scope="module")
def recus():
    return json.loads(RECUS.read_text(encoding="utf-8"))


def test_les_deux_gates_demandes_sont_publies_et_verts(recus):
    resume = recus["summary"]
    assert resume["SEMANTIC_CHANGE_PRESERVES_OLD_HUMAN_APPROVAL"] == "PASS"
    assert resume["SEMANTIC_CHANGE_INVALIDATES_REVIEW_RECEIPT"] == "PASS"
    assert resume["STALE_APPROVAL_AFTER_SEMANTIC_EDIT"] == 0
    assert recus["approves_no_content"] is True
    assert recus["promotes_no_status"] is True


def test_la_perte_d_une_approbation_reste_visible(recus):
    """Une approbation retiree n'est pas une approbation qui n'a jamais existe.

    La fondre dans le lot des objets `generated` effacerait une regression
    assumee ; elle reste comptee a part, et attend une relecture humaine.
    """
    resume = recus["summary"]
    assert resume["INVALIDATED_APPROVALS_AWAITING_HUMAN_REVIEW"] > 0
    for entree in recus["invalidated_awaiting_human_review"]:
        assert entree["status"] == "needs_review"
        assert entree["approval_state"] == "STALE_AFTER_SEMANTIC_EDIT"
        assert (ROOT / entree["path"]).exists()


def test_aucun_des_neuf_contenus_de_phase_4_ne_garde_une_vieille_approbation():
    """La verification porte sur les neuf, pas seulement sur C7."""
    for chemin in NEUF:
        texte = (ROOT / chemin).read_text(encoding="utf-8")
        meta = json.loads(texte.split("\n", 1)[0][len("% META:"):].strip())
        assert meta.get("status") != "approved", chemin


def test_un_bloc_de_verification_ne_perime_pas_une_approbation():
    """Ajouter un oracle ne change pas une ligne de ce qui est imprime."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from content_approval import jetons_visibles

    avant = '% META: {"id": "X"}\n\\section{A}\nTexte.\n'
    apres = (
        '% META: {"id": "X"}\n\\section{A}\nTexte.\n'
        "% BEGIN-VERIFY\n% assert 1 == 1\n% END-VERIFY\n"
    )
    assert jetons_visibles(avant) == jetons_visibles(apres)


def test_une_reecriture_reelle_perime_l_approbation():
    """Mutation : le controle doit distinguer une reecriture d'un accent."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from content_approval import jetons_visibles, reparation_de_sequence_latex

    origine = '% META: {"id": "X"}\nLe resultat vaut $3$.\n'
    accentue = '% META: {"id": "X"}\nLe résultat vaut $3$.\n'
    reecrit = '% META: {"id": "X"}\nLe resultat vaut $4$.\n'
    assert jetons_visibles(origine) == jetons_visibles(accentue)
    assert jetons_visibles(origine) != jetons_visibles(reecrit)
    assert not reparation_de_sequence_latex(
        jetons_visibles(origine), jetons_visibles(reecrit)
    )
    # La reparation d'une sequence de controle cassee, elle, reste neutre.
    casse = jetons_visibles('% META: {"id": "X"}\nComme $x\neq 0$.\n')
    repare = jetons_visibles('% META: {"id": "X"}\nComme $x\n\\neq 0$.\n')
    assert casse != repare
    assert reparation_de_sequence_latex(casse, repare)


def test_approval_state_ne_deplace_pas_l_empreinte_pedagogique():
    """Constater qu'un contenu n'a pas bouge ne doit pas le faire bouger."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from release_digests import GOVERNANCE_META_KEYS

    assert "approval_state" in GOVERNANCE_META_KEYS


def test_les_recus_sont_bien_regeneres_par_leur_generateur():
    acheve = subprocess.run(
        [sys.executable, "scripts/build_content_approval_receipts.py", "--check"],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    assert acheve.returncode == 0, acheve.stdout + acheve.stderr
