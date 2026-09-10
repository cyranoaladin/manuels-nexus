"""Un attendu revendique par deux chapitres : faute ou transversalite ?

Le compteur brut ne sait pas repondre, et supprimer arbitrairement un des deux
liens detruirait une vraie transversalite pedagogique. La reponse se lit dans
les objets : qui ENSEIGNE l'attendu, qui le reinvestit, qui se declare sans
rien avoir derriere.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RESOLUTION = ROOT / "audit" / "MULTIPLE_ASSIGNMENT_RESOLUTION.json"
COVERAGE = ROOT / "audit" / "OFFICIAL_TO_MANUAL_COVERAGE.json"
BINDING = ROOT / "audit" / "OFFICIAL_PROGRAMME_BINDING.json"


@pytest.fixture(scope="module")
def resolution():
    return json.loads(RESOLUTION.read_text(encoding="utf-8"))


def test_chaque_attendu_partage_est_tranche(resolution):
    liaison = json.loads(BINDING.read_text(encoding="utf-8"))
    assert len(resolution["resolutions"]) == len(liaison["multiple_assignment"])
    for ligne in resolution["resolutions"]:
        assert ligne["resolution"], ligne["official_id"]
        assert ligne["reason"], ligne["official_id"]
        assert ligne["claiming_themes"] and len(ligne["claiming_themes"]) > 1


def test_une_couverture_distribuee_est_reellement_enseignee_deux_fois(resolution):
    """Sinon « transversalite » servirait a couvrir une declaration vide."""
    for ligne in resolution["resolutions"]:
        if ligne["resolution"] == "JUSTIFIED_DISTRIBUTED_COVERAGE":
            assert len(ligne["PRIMARY_TEACHING"]) >= 2, ligne["official_id"]
            for chapitre in ligne["PRIMARY_TEACHING"]:
                assert ligne["objects_by_chapter"].get(chapitre), chapitre


def test_un_attendu_partage_ne_compte_qu_une_fois_dans_la_couverture(resolution):
    """Deux chapitres ne couvrent pas deux fois le meme programme."""
    lignes = json.loads(COVERAGE.read_text(encoding="utf-8"))["rows"]
    for ligne in resolution["resolutions"]:
        occurrences = [r for r in lignes if r["official_id"] == ligne["official_id"]]
        assert len(occurrences) == 1, ligne["official_id"]
        assert ligne["counted_once_in_coverage"] is True


def test_le_compteur_publie_ne_retient_que_le_non_justifie(resolution):
    resume = resolution["summary"]
    non_justifies = [
        r for r in resolution["resolutions"]
        if r["resolution"] in (
            "UNJUSTIFIED_DUPLICATE_BINDING",
            "PRACTISED_BUT_NEVER_TAUGHT",
        )
    ]
    assert resume["UNJUSTIFIED_MULTIPLE_ASSIGNMENT"] == len(non_justifies)
    assert resume["SHARED_OFFICIAL_ITEMS"] == len(resolution["resolutions"])


def test_la_resolution_est_bien_regeneree_par_son_generateur():
    acheve = subprocess.run(
        [sys.executable, "scripts/build_multiple_assignment_resolution.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert acheve.returncode == 0, acheve.stdout + acheve.stderr
