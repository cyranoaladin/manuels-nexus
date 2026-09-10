"""Ce qu'une mesure regarde vaut autant que ce qu'elle conclut.

Quatre cecites de producteur ont ete corrigees ensemble, parce qu'elles ont
la meme forme : le controle repondait « non » a propos d'un perimetre qu'il
n'avait pas regarde.

- un automatisme n'etait mesure que sur les objets qui le declarent, si bien
  qu'un rattachement suffisait a le faire paraitre concentre dans un chapitre ;
- un QCM n'inscrivait les capacites qu'il evalue que la ou le champ existait
  deja, laissant quarante-deux QCM muets ;
- un objet cite comme preuve d'un attendu officiel NON obligatoire etait
  compte parmi les objets sans justification ;
- « faire de l'algorithmique » etait atteste par un bloc BEGIN-VERIFY, que le
  lecteur ne voit jamais : trois mille objets sur trois mille cinq cents
  passaient le controle.
"""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COVERAGE = ROOT / "audit" / "OFFICIAL_TO_MANUAL_COVERAGE.json"
REVERSE = ROOT / "audit" / "OBJECTS_TO_OFFICIAL_REVERSE_MAP.json"
AUTOMATISMS = ROOT / "audit" / "1SPE_AUTOMATISMS_AUDIT.json"


@pytest.fixture(scope="module")
def couverture():
    return json.loads(COVERAGE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def carte_inverse():
    return json.loads(REVERSE.read_text(encoding="utf-8"))


def test_un_bloc_de_verification_ne_vaut_pas_un_algorithme_montre():
    """BEGIN-VERIFY prouve au producteur, il n'enseigne pas a l'eleve.

    Le distinguer n'est pas cosmetique : sans cette distinction, la quasi
    totalite du manuel « faisait de l'algorithmique », et n'importe quelle
    partie du programme paraissait servie par un algorithme qu'elle n'expose
    pas.
    """
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from manual_objects import ALGORITHME_MONTRE

    assert not ALGORITHME_MONTRE.search("% BEGIN-VERIFY\n% assert 1 == 1\n% END-VERIFY")
    assert ALGORITHME_MONTRE.search(r"\begin{python}print(1)\end{python}")
    assert ALGORITHME_MONTRE.search(r"\begin{sql}SELECT 1\end{sql}")


def test_le_standard_algorithmique_publie_ce_qu_il_a_regarde(couverture):
    """Un verdict dont on ignore le perimetre ne vaut rien.

    Il a d'abord ete rendu sur la portee des themes : quatre parties n'en ont
    aucune, et le controle repondait « pas de travail algorithmique » a propos
    de chapitres qu'il n'avait pas ouverts -- dont les probabilites
    conditionnelles de premiere, qui portent une page Monte-Carlo complete.
    Elargir a tous les chapitres cites aurait produit la faute symetrique.
    """
    standard = couverture["nexus_algorithmic_quality_standard"]
    assert "PAS une obligation du programme" in standard["nature"]
    parties = standard["parts"]
    assert parties
    for partie in parties:
        assert partie["standard"] == "NEXUS_ALGORITHMIC_QUALITY_STANDARD"
        assert partie["algorithm_examples_cited_by_the_programme"] >= 1
        assert "objects_examined" in partie
        if partie["manual_has_algorithmic_work"]:
            assert partie["algorithmic_work_evidence"]
        else:
            assert partie["algorithmic_work_evidence"] == []

    monte_carlo = [
        p for p in parties
        if p["manual"] == "1SPE"
        and p["official_part"].startswith("Probabilités conditionnelles")
    ]
    assert len(monte_carlo) == 1
    assert monte_carlo[0]["manual_has_algorithmic_work"]
    assert "1SPE-PROBCOND-ALG-001" in monte_carlo[0]["algorithmic_work_evidence"]


def test_les_deux_exemples_d_algorithme_de_terminale_sont_desormais_traites(couverture):
    """Planche de Galton et marche aleatoire : enrichissement assume.

    Le BO les NOMME sans les imposer. Ils ne comptent donc a aucun
    denominateur d'obligation ; ce test verifie seulement qu'ils sont
    effectivement traites, et par des objets qui montrent un algorithme.
    """
    parties = {
        (p["manual"], p["official_part"]): p
        for p in couverture["nexus_algorithmic_quality_standard"]["parts"]
    }
    for nom in (
        "Succession d’épreuves indépendantes, schéma de Bernoulli",
        "Concentration, loi des grands nombres",
    ):
        partie = parties[("TSPE", nom)]
        assert partie["manual_has_algorithmic_work"], nom
    galton = ROOT / (
        "Mathematiques/manuel-maths/chapitres/TSPE-PROBABILITES/cours/"
        "17_ALG_planche_de_galton.tex"
    )
    marche = ROOT / (
        "Mathematiques/manuel-maths/chapitres/TSPE-PROBABILITES/cours/"
        "18_ALG_marche_aleatoire.tex"
    )
    for chemin in (galton, marche):
        texte = chemin.read_text(encoding="utf-8")
        meta = json.loads(texte.split("\n", 1)[0].removeprefix("% META: "))
        # Le libelle du BO est un exemple, et l'objet le dit.
        assert meta["programme_alignment"] == "OFFICIAL_ALGORITHM_EXAMPLE"
        assert r"\begin{python}" in texte
        assert "% BEGIN-VERIFY" in texte


def test_un_automatisme_se_mesure_sur_tout_le_manuel(couverture):
    """Le programme exclut qu'un automatisme fasse l'objet d'un chapitre.

    Mesurer sa repartition sur les seuls objets qui le declarent revient a
    mesurer la repartition des declarations. Une disposition rattachant deux
    capacites de « probabilites conditionnelles » a l'automatisme des tableaux
    croises l'a fait basculer, seul, en PARTIAL -- alors que le manuel le
    retravaille dans les suites et les variables aleatoires.
    """
    automatismes = [
        r for r in couverture["rows"]
        if r["official_normativity"] == "REQUIRED_AUTOMATISM"
    ]
    assert automatismes
    concentres = [
        r for r in automatismes
        if r["coverage_status"] == "PARTIAL" and len(r["chapters"]) <= 1
    ]
    assert not concentres, [r["official_id"] for r in concentres]
    croise = [
        r for r in automatismes
        if r["official_wording"].startswith("Calculer des probabilités conditionnelles")
    ]
    assert len(croise) == 1
    assert len(croise[0]["chapters"]) >= 2, croise[0]["chapters"]


def test_chaque_qcm_dit_les_capacites_qu_il_evalue():
    """Le resolveur les etablit exactement : les taire etait un choix, pas une
    limite technique. Cinq QCM de terminale NSI en devenaient introuvables."""
    muets = []
    for chemin in sorted(ROOT.glob("*/chapitres/*/qcm/*-QCM.tex")) + sorted(
        ROOT.glob("*/*/chapitres/*/qcm/*-QCM.tex")
    ):
        premiere = chemin.read_text(encoding="utf-8").split("\n", 1)[0]
        meta = json.loads(premiere.removeprefix("% META: "))
        if not (meta.get("capacites") or meta.get("capacites_codes")):
            muets.append(meta.get("id"))
    assert not muets, muets


def test_aucun_objet_ne_reste_sans_statut(carte_inverse):
    """Un objet cite comme preuve d'un attendu officiel non obligatoire a un
    statut : le programme le nomme, il ne l'impose pas. Le declarer « sans
    justification » contredisait l'artefact qui le nomme."""
    resume = carte_inverse["summary"]
    assert resume["UNCLASSIFIED_OUT_OF_PROGRAMME_OBJECTS"] == 0
    sans_statut = [
        o for o in carte_inverse["objects"] if o["classification"] == "OFF_TOPIC"
    ]
    assert not sans_statut, [o["object_id"] for o in sans_statut]
    # La page d'algorithmes de l'exponentielle etait le temoin de ce defaut :
    # elle mettait en oeuvre les deux « Exemples d'algorithme » du BO et
    # passait pour un objet sans justification. Elle declare depuis les
    # capacites qu'elle sert, et releve donc du programme -- ce qui est mieux
    # encore. Ce que le test verrouille est qu'elle ait un statut et des
    # parents officiels, non lequel des deux chemins l'y conduit.
    exponentielle = [
        o for o in carte_inverse["objects"]
        if o["object_id"] == "1SPE-EXPO-COURS-C5-ALGORITHMES"
    ]
    assert len(exponentielle) == 1
    assert exponentielle[0]["classification"] != "OFF_TOPIC"
    assert exponentielle[0]["official_parents"]


def test_le_hors_annee_garde_la_priorite_sur_l_enrichissement():
    """Un objet qui traite un programme perime ne se rachete pas en croisant
    au passage un exemple facultatif du programme en vigueur."""
    source = (ROOT / "scripts" / "build_objects_to_official_reverse_map.py").read_text(
        encoding="utf-8"
    )
    position_hors_annee = source.index('classement = "WRONG_YEAR"')
    position_enrichissement = source.index("elif facultatifs_prouves:")
    assert position_hors_annee < position_enrichissement


def test_le_seuil_maison_reste_nomme_comme_tel():
    """Aucune exigence de la collection ne doit passer pour du droit."""
    automatismes = json.loads(AUTOMATISMS.read_text(encoding="utf-8"))
    standard = automatismes["summary"]["NEXUS_DISTRIBUTED_AUTOMATISM_STANDARD"]
    assert "exigence de la collection" in standard
    assert "pas du programme" in standard
    assert re.search(r"\bNEXUS_", standard) is None
