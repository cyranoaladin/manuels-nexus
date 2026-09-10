"""Un champ nomme `libelle_bo` ne doit pas valoir certificat d'authenticite.

Le nom du champ affirme le Bulletin officiel. La comparaison avec les
programmes reels montre qu'il n'en est le plus souvent qu'une reformulation
pedagogique : sur 313 capacites internes, 154 s'ecartent du texte. Tant que ce
nom survit sans garde-fou, sa valeur finira par etre citee comme preuve.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "audit" / "LIBELLE_BO_AUTHORITY_GATE.json"
REFERENTIELS = (
    ROOT / "Mathematiques" / "manuel-maths" / "referentiel",
    ROOT / "NSI" / "referentiel",
)


@pytest.fixture(scope="module")
def gate():
    return json.loads(GATE.read_text(encoding="utf-8"))


def test_aucun_champ_ne_se_donne_pour_officiel_sans_l_avoir_verifie(gate):
    assert gate["summary"]["MISLEADING_LIBELLE_BO_FIELDS_USED_AS_AUTHORITY"] == 0, (
        gate["violations"][:5]
    )
    assert gate["summary"]["LIBELLE_BO_AUTHORITY_GATE"] == "PASS"


def test_chaque_capacite_interne_dit_si_son_libelle_vient_du_bo():
    """Sans ce drapeau, le nom du champ reste la seule indication, et il ment."""
    total = declarees = verbatim = 0
    for dossier in REFERENTIELS:
        for chemin in sorted(dossier.glob("capacites_*.json")):
            charge = json.loads(chemin.read_text(encoding="utf-8"))
            for capacite in charge.get("capacites", []):
                total += 1
                if "libelle_bo_is_verbatim" in capacite:
                    declarees += 1
                    verbatim += bool(capacite["libelle_bo_is_verbatim"])
                assert "libelle_interne" in capacite, capacite["id"]
    assert total == declarees == 313
    # Le chiffre exact suivra l'evolution des referentiels ; ce qui doit tenir
    # est que le champ ne soit pas verbatim partout -- sinon le probleme
    # n'existerait pas et ce garde-fou serait un decor.
    assert 0 < verbatim < total


def test_la_barriere_est_bien_regeneree_par_son_generateur():
    acheve = subprocess.run(
        [sys.executable, "scripts/check_libelle_bo_authority.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert acheve.returncode == 0, acheve.stdout + acheve.stderr


def test_une_archive_ne_passe_pas_au_travers_par_son_seul_emplacement():
    """Sinon il suffirait de deposer un fichier dans `historique/`.

    Une archive est toleree parce qu'elle annonce elle-meme que ses libelles
    restent a verifier, pas parce qu'elle est rangee la.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    import check_libelle_bo_authority as barriere

    faux = Path("audit/historique/quelconque.json")
    assert barriere._archive_declaree(faux, {"note": "a re-verifier mot a mot"})
    assert not barriere._archive_declaree(faux, {"note": "tout est conforme"})
    assert not barriere._archive_declaree(faux, {})
    assert not barriere._archive_declaree(
        Path("audit/courant.json"), {"note": "a re-verifier"}
    )
