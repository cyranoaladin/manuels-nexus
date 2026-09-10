"""Les automatismes et la transition 2019 -> 2026, mesures sur le manuel.

Deux affirmations ont ete faites puis corrigees en chemin, et ces tests
verrouillent la version corrigee :

- « le referentiel n'a aucun atome pour les dix-sept automatismes, c'est un
  chantier entier » : la premiere moitie est vraie, la seconde etait fausse.
  Les automatismes sont travailles dans le manuel sans avoir recu de code.
- « la reforme de 2026 ajoute vingt-huit attendus obligatoires » : vrai, mais
  aucun ne demande d'ecrire du contenu neuf.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
AUTOMATISMES = ROOT / "audit" / "1SPE_AUTOMATISMS_AUDIT.json"
TRANSITION = ROOT / "audit" / "1SPE_REFORM_TRANSITION_AUDIT.json"

VERDICTS = {
    "ABSENT",
    "PRESENT_BUT_NOT_DISTRIBUTED",
    "DISTRIBUTED_INSUFFICIENTLY",
    "ADEQUATELY_REINVESTED",
}


@pytest.fixture(scope="module")
def automatismes():
    return json.loads(AUTOMATISMES.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def transition():
    return json.loads(TRANSITION.read_text(encoding="utf-8"))


def test_les_dix_sept_automatismes_du_programme_sont_tous_audites(automatismes):
    lignes = automatismes["automatisms"]
    assert len(lignes) == 17
    assert all(x["verdict"] in VERDICTS for x in lignes)
    assert all(x["reason"] for x in lignes)
    assert automatismes["summary"]["AUTOMATISMS_1SPE_OFFICIAL"] == len(lignes)


def test_l_absence_d_atome_n_est_pas_l_absence_du_manuel(automatismes):
    """Le constat qui a corrige le precedent.

    Aucun des dix-sept automatismes ne porte d'atome interne. Si l'absence
    d'atome valait absence, ils seraient tous a ecrire ; ils sont en fait
    travailles dans les objets, sans avoir jamais recu de code.
    """
    resume = automatismes["summary"]
    assert resume["AUTOMATISMS_1SPE_WITH_AN_INTERNAL_ATOM"] == 0
    assert resume["AUTOMATISMS_1SPE_PRESENT"] == resume["AUTOMATISMS_1SPE_OFFICIAL"]
    for ligne in automatismes["automatisms"]:
        if ligne["verdict"] != "ABSENT":
            assert ligne["occurrence_count"] > 0, ligne["automatism_id"]
            assert ligne["chapters_distribution"], ligne["automatism_id"]


def test_un_automatisme_concentre_dans_un_chapitre_n_est_pas_entretenu(automatismes):
    """Le programme exclut qu'un automatisme fasse l'objet d'un chapitre.

    Le declarer couvert parce qu'il est enseigne quelque part reviendrait a
    ignorer ce que le texte demande : un entretien reparti sur l'annee.
    """
    for ligne in automatismes["automatisms"]:
        if len(ligne["chapters_distribution"]) <= 1 and ligne["occurrence_count"]:
            assert ligne["verdict"] == "PRESENT_BUT_NOT_DISTRIBUTED"
        if ligne["verdict"] == "ADEQUATELY_REINVESTED":
            assert len(ligne["chapters_distribution"]) >= 3
            assert ligne["PRACTICE_EVIDENCE"] or ligne["ASSESSMENT_EVIDENCE"]


def test_la_dette_de_contenu_ne_se_deduit_pas_du_differentiel(transition):
    """Un attendu « ajoute en 2026 » peut etre traite depuis des annees.

    C'est le cas de la totalite d'entre eux : la reforme ne demande aucune
    redaction nouvelle en premiere. Ce qui manquait etait le suivi, pas le
    contenu.
    """
    resume = transition["summary"]
    assert resume["ADDED_TRULY_MISSING"] == 0
    assert (
        resume["ADDED_TRULY_MISSING"]
        + resume["ADDED_ALREADY_PRESENT_WITHOUT_OFFICIAL_MAPPING"]
        + resume["ADDED_ALREADY_FIXED"]
        == resume["ADDED_2026_MANDATORY"]
    )
    for ligne in transition["added_2026"]:
        assert ligne["classification"] != "UNDECIDED", ligne["official_id"]


def test_un_contenu_retire_n_est_fautif_que_s_il_reste_exigible(transition):
    """Un contenu retire peut rester comme approfondissement.

    Ce qui est interdit, c'est qu'il continue d'etre presente comme exigible :
    l'eleve travaillerait pour une epreuve qui ne le lui demandera pas.
    """
    resume = transition["summary"]
    assert resume["REMOVED_2019_CONTENT_STILL_PRESENTED_AS_REQUIRED"] == 0, [
        r["official_wording"]
        for r in transition["removed_2026"]
        if r["classification"] == "STILL_PRESENTED_AS_REQUIRED"
    ]
    total = sum(
        resume[cle]
        for cle in (
            "REMOVED_2019_CONTENT_STILL_PRESENTED_AS_REQUIRED",
            "REMOVED_KEPT_AS_ENRICHMENT",
            "REMOVED_AND_ABSENT",
            "REMOVED_BUT_STILL_IN_PROGRAMME",
            "REMOVED_2019_CONTENT_REQUIRING_EDITORIAL_REVIEW",
        )
    )
    assert total == resume["REMOVED_2026_MANDATORY"]


def test_une_preuve_lexicale_faible_ne_se_donne_pas_pour_une_certitude(transition):
    """Savoir qu'un mot reste au programme ne dit pas que la notion y reste.

    « Cosinus » et « sinus » restent au programme de 2026, mais l'etude des
    fonctions cosinus et sinus en sort. Ces cas doivent rester marques comme
    demandant une lecture, jamais comme tranches.
    """
    faibles = [
        r for r in transition["removed_2026"]
        if r["classification"] == "NOTION_STILL_NAMED_IN_PROGRAMME_REQUIRES_REVIEW"
    ]
    assert faibles, "aucun cas faible : le second filet serait inerte"
    for ligne in faibles:
        assert ligne["evidence_strength"] == "WEAK_LEXICAL"
        assert "a verifier" in ligne["reason"]
        assert ligne["still_in_programme_as"]


@pytest.mark.parametrize(
    "script",
    [
        "scripts/build_1spe_automatisms_audit.py",
        "scripts/build_1spe_reform_transition_audit.py",
    ],
)
def test_les_audits_sont_bien_regeneres_par_leur_generateur(script):
    acheve = subprocess.run(
        [sys.executable, script, "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert acheve.returncode == 0, acheve.stdout + acheve.stderr
