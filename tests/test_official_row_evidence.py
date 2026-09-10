"""Une ligne du tableau officiel est une unite reglementaire, pas trois colonnes.

Le BO de NSI place sur une meme ligne un contenu, les capacites qui le mettent
en oeuvre et les commentaires qui l'eclairent. Les traiter separement fait
declarer absent un contenu que le cours d'a cote enseigne : c'est ce qui est
arrive a « Utilisation de bibliotheques » et a « Securisation des
communications », tous deux enseignes et tous deux comptes manquants.

La preuve par ligne n'est PAS un heritage. Une capacite soeur ne prouve le
contenu que si le corps de l'objet traite reellement le sujet.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COVERAGE = ROOT / "audit" / "OFFICIAL_TO_MANUAL_COVERAGE.json"
INDEX = ROOT / "audit" / "OFFICIAL_PROGRAMME_INVENTORY.json"


@pytest.fixture(scope="module")
def couverture():
    return json.loads(COVERAGE.read_text(encoding="utf-8"))


def _ligne(couverture, debut):
    trouvees = [
        r for r in couverture["rows"] if r["official_wording"].startswith(debut)
    ]
    assert len(trouvees) == 1, (debut, len(trouvees))
    return trouvees[0]


def test_les_lignes_du_tableau_officiel_sont_conservees():
    """Sans elles, rien ne relie un contenu aux capacites qui le realisent."""
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    tableaux = 0
    for entree in index["documents"]:
        charge = json.loads((ROOT / entree["inventory_path"]).read_text(encoding="utf-8"))
        for ligne in charge.get("row_bindings", []):
            tableaux += 1
            assert set(ligne) >= {
                "official_table",
                "official_row",
                "content_items",
                "capacity_items",
                "commentary_items",
            }
            assert isinstance(ligne["official_table"], int)
    assert tableaux > 0, "aucune ligne de tableau conservee"


def test_utilisation_de_bibliotheques_est_enseignee_par_le_cours_de_sa_ligne(couverture):
    """Cas de non-regression nomme par la contre-expertise.

    Le BO porte, sur une meme ligne : « Utilisation de bibliotheques » et
    « Utiliser la documentation d'une bibliotheque ». Le manuel possede
    `1NSI-LANG-COURS-C5`, dont la section s'intitule « Utiliser une
    bibliotheque » et qui traite import, documentation, prototype, help() et
    module math. Il n'y avait rien a reecrire.
    """
    ligne = _ligne(couverture, "Utilisation de bibliothèques")
    assert ligne["manual"] == "1NSI"
    assert ligne["coverage_status"] == "COMPLETE"
    assert ligne["evidence_kind"] == "OFFICIAL_ROW_EVIDENCE"
    enseignement = ligne["objects_by_role"].get("PRIMARY_TEACHING", [])
    assert "1NSI-LANG-COURS-C5" in enseignement, enseignement
    assert "bibliotheque" in ligne["matched_terms"]
    assert "documentation" in ligne["matched_terms"]


def test_securisation_des_communications_est_enseignee_par_le_cours_de_sa_ligne(couverture):
    """Second cas de non-regression nomme par la contre-expertise.

    Le BO porte, sur une meme ligne : « Securisation des communications » et
    les capacites de decrire les chiffrements symetrique et asymetrique puis
    l'echange d'une clef. Le manuel possede `TNSI-ARCH-CR-013`
    (`13_C04_chiffrement.tex`), qui enseigne exactement cela, jusqu'a HTTPS.
    Aucun second cours de chiffrement n'etait a ecrire.
    """
    ligne = _ligne(couverture, "Sécurisation des communications")
    assert ligne["manual"] == "TNSI"
    assert ligne["coverage_status"] == "COMPLETE"
    assert ligne["evidence_kind"] == "OFFICIAL_ROW_EVIDENCE"
    enseignement = ligne["objects_by_role"].get("PRIMARY_TEACHING", [])
    assert "TNSI-ARCH-CR-013" in enseignement, enseignement
    assert "chiffrement" in ligne["matched_terms"]
    assert "asymetrique" in ligne["matched_terms"]


def test_la_preuve_par_ligne_n_est_pas_un_heritage(couverture):
    """Une capacite soeur ne suffit pas : le corps de l'objet doit traiter le sujet.

    Sans cette exigence, tout contenu deviendrait couvert des qu'une capacite
    voisine l'est, et la matrice ne mesurerait plus rien.
    """
    par_ligne = [
        r for r in couverture["rows"]
        if r["evidence_kind"] == "OFFICIAL_ROW_EVIDENCE"
    ]
    assert par_ligne, "la preuve par ligne n'est jamais utilisee"
    for ligne in par_ligne:
        assert ligne["matched_terms"], ligne["official_id"]
        assert ligne["object_count"] > 0, ligne["official_id"]
    nature = couverture["evidence_kinds"]["OFFICIAL_ROW_EVIDENCE"]
    assert "n'est pas un heritage" in nature
