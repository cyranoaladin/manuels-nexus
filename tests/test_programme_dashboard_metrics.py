"""Un rapport ne doit plus pouvoir citer un compteur devenu faux.

Un chiffre recopie a la main cesse d'etre vrai des que l'artefact qui le
produit bouge, et rien ne le signale. C'est arrive : un compte rendu annoncait
918 attendus applicables alors que l'inventaire en publiait deja 932,
l'extraction des preambules de NSI en ayant ajoute quatorze entre-temps.

Ces tests verifient que le tableau de bord est bien DERIVE, et non redige.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "audit" / "PROGRAMME_DASHBOARD.json"
DASHBOARD_MD = ROOT / "audit" / "PROGRAMME_DASHBOARD.md"


@pytest.fixture(scope="module")
def tableau():
    return json.loads(DASHBOARD.read_text(encoding="utf-8"))


def test_report_metrics_match_canonical_artifacts(tableau):
    """REPORT_METRICS_MATCH_CANONICAL_ARTIFACTS.

    Chaque compteur publie est relu dans l'artefact qu'il designe. Un ecart
    signifie que le tableau de bord affiche un chiffre que plus aucun
    producteur ne soutient.
    """
    for nom, detail in tableau["metrics"].items():
        charge = json.loads((ROOT / detail["artifact"]).read_text(encoding="utf-8"))
        courant = charge
        for cle in detail["pointer"]:
            assert cle in courant, (nom, detail["pointer"])
            courant = courant[cle]
        assert courant == detail["value"], nom


def test_chaque_compteur_cite_sa_source(tableau):
    """Un compteur sans provenance ne peut pas etre verifie par un lecteur."""
    assert tableau["metrics"], "un tableau de bord vide ne prouve rien"
    for nom, detail in tableau["metrics"].items():
        assert detail["artifact"].startswith("audit/"), nom
        assert detail["pointer"], nom
        assert (ROOT / detail["artifact"]).is_file(), nom


def test_le_tableau_de_bord_est_bien_regenere_par_son_generateur():
    acheve = subprocess.run(
        [sys.executable, "scripts/build_programme_dashboard.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert acheve.returncode == 0, acheve.stdout + acheve.stderr


def test_le_tableau_publie_n_affiche_que_des_valeurs_canoniques(tableau):
    """Tout nombre du tableau doit provenir d'une metrique canonique.

    Sans cette regle, une ligne ajoutee au fil de l'eau reintroduirait
    exactement le probleme que ce tableau evite. Le controle porte sur les
    lignes de tableau, ou vivent les compteurs ; les paragraphes d'explication
    peuvent citer une annee de programme sans que ce soit un chiffre mesure.
    """
    import re

    texte = DASHBOARD_MD.read_text(encoding="utf-8")
    connus = {str(d["value"]) for d in tableau["metrics"].values()}
    for valeur in list(connus):
        connus.update(re.findall(r"\d+", valeur))
    lignes = [ligne for ligne in texte.splitlines() if ligne.startswith("|")]
    trouves = set(re.findall(r"(?<![\w/.-])\d+(?![\w/.-])", "\n".join(lignes)))
    assert trouves <= connus, sorted(trouves - connus)


def test_une_valeur_qui_bouge_dans_l_artefact_bouge_dans_le_rapport(tmp_path):
    """Mutation : le tableau de bord lit-il vraiment les artefacts ?

    S'il portait ses propres chiffres, il resterait identique alors que
    l'inventaire a change -- exactement la panne qu'il est cense empecher.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    import programme_metrics

    avant = programme_metrics.canonical_metrics()
    original = programme_metrics._lire

    def lecture_mutante(relatif: str):
        charge = original(relatif)
        if relatif == programme_metrics.INVENTORY:
            charge["official_items_applicable"] = 999999
        return charge

    programme_metrics._lire = lecture_mutante  # type: ignore[assignment]
    try:
        apres = programme_metrics.canonical_metrics()
    finally:
        programme_metrics._lire = original  # type: ignore[assignment]

    assert avant["CANONICAL_OFFICIAL_ITEMS_APPLICABLE"].value != 999999
    assert apres["CANONICAL_OFFICIAL_ITEMS_APPLICABLE"].value == 999999
