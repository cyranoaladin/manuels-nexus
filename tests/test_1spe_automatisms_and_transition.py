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

#: Le seul verdict qui contredise le PROGRAMME est celui d'un automatisme
#: cantonne a un chapitre. Les autres ecarts relevent du standard que la
#: collection se donne, et portent un nom qui le dit.
VERDICTS = {
    "ABSENT",
    "PRESENT_BUT_NOT_DISTRIBUTED",
    "MEETS_OFFICIAL_MINIMUM_BELOW_NEXUS_STANDARD",
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

    Presque aucun des dix-sept automatismes ne porte d'atome interne. Si
    l'absence d'atome valait absence, ils seraient a ecrire ; ils sont en fait
    travailles dans les objets, sans avoir jamais recu de code. Ce que ce test
    verrouille n'est donc pas le nombre d'automatismes codes -- un arbitrage
    de rattachement peut legitimement en coder un -- mais l'invariant : un
    automatisme SANS atome doit quand meme etre trouve dans le manuel.
    """
    resume = automatismes["summary"]
    assert resume["AUTOMATISMS_1SPE_PRESENT"] == resume["AUTOMATISMS_1SPE_OFFICIAL"]
    sans_atome = [x for x in automatismes["automatisms"] if not x["internal_atoms"]]
    assert sans_atome, "un corpus ou tout serait code ne testerait plus rien"
    for ligne in sans_atome:
        assert ligne["verdict"] != "ABSENT", ligne["automatism_id"]
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


def test_le_seuil_de_trois_chapitres_est_nomme_comme_exigence_maison(automatismes):
    """Le BO ne dit nulle part « au moins trois chapitres ».

    Il dit qu'un automatisme ne doit pas faire l'objet d'un chapitre
    specifique et doit etre entretenu sur l'annee. Presenter le seuil de la
    collection comme une obligation ministerielle ferait passer une exigence
    maison pour du droit.
    """
    resume = automatismes["summary"]
    assert "collection" in resume["NEXUS_DISTRIBUTED_AUTOMATISM_STANDARD"]
    assert "pas du programme" in resume["NEXUS_DISTRIBUTED_AUTOMATISM_STANDARD"]
    # Ce que le programme exige est tenu : aucun automatisme n'est cantonne.
    assert resume["AUTOMATISM_NOT_REINVESTED"] == 0
    assert resume["AUTOMATISMS_1SPE_PRESENT"] == resume["AUTOMATISMS_1SPE_OFFICIAL"]


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
            # Les trois issues d'une lecture rendue, qui remplacent le
            # verdict lexical faible.
            "REMOVED_STILL_REQUIRED_UNDER_2026_WORDING",
            "REMOVED_OPTIONAL_BUT_USEFUL",
            "REMOVED_TRULY_REMOVED",
        )
    )
    assert total == resume["REMOVED_2026_MANDATORY"]


def test_une_preuve_lexicale_faible_ne_se_donne_pas_pour_une_certitude(transition):
    """Savoir qu'un mot reste au programme ne dit pas que la notion y reste.

    « Cosinus » et « sinus » restent au programme de 2026, mais l'etude des
    fonctions cosinus et sinus en sort. Tant qu'aucune lecture n'a ete rendue,
    ces cas restent marques comme demandant une lecture, jamais comme
    tranches. Une fois la lecture rendue, elle prend leur place -- et elle
    porte alors une force de preuve differente.
    """
    faibles = [
        r for r in transition["removed_2026"]
        if r["classification"] == "NOTION_STILL_NAMED_IN_PROGRAMME_REQUIRES_REVIEW"
    ]
    for ligne in faibles:
        assert ligne["evidence_strength"] == "WEAK_LEXICAL"
        assert "a verifier" in ligne["reason"]
        assert ligne["still_in_programme_as"]

    lues = [
        r for r in transition["removed_2026"]
        if r["evidence_strength"] == "DECLARED_READING_OF_THE_2026_TEXT"
    ]
    assert lues, "aucune lecture rendue : le second filet serait inerte"
    for ligne in lues:
        assert ligne["classification"] in {
            "STILL_REQUIRED_UNDER_2026_WORDING",
            "OPTIONAL_BUT_USEFUL",
            "TRULY_REMOVED",
        }
        # Une lecture cite le texte de 2026 ; elle ne se contente pas de
        # renvoyer a un identifiant.
        assert len(ligne["reason"]) > 120, ligne["official_wording"]
        assert ligne["still_in_programme_as"] is None
        # Un contenu declare retire ne doit plus etre enseigne ni evalue.
        if ligne["classification"] == "TRULY_REMOVED":
            assert not ligne["surviving_in_course_or_assessment"], ligne[
                "official_wording"
            ]


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


def test_le_socle_suppose_acquis_est_reactive_ou_signale():
    """« Les automatismes travailles en seconde doivent etre entretenus. »

    Un chapitre qui suppose un prerequis sans rien offrir pour le reprendre
    laisse l'eleve sans recours : il ne saura pas ce qui lui manque.
    """
    charge = json.loads(
        (ROOT / "audit" / "1SPE_PREREQUISITE_SUPPORT.json").read_text(encoding="utf-8")
    )
    lignes = charge["prerequisites"]
    assert lignes
    assert charge["summary"]["PREREQUISITES_DECLARED"] == len(lignes)
    for ligne in lignes:
        assert ligne["status"] in {
            "DIAGNOSED_AND_REMEDIATED",
            "REMEDIATED_ONLY",
            "DIAGNOSED_ONLY",
            "ASSUMED_WITHOUT_SUPPORT",
        }
        if ligne["status"] != "ASSUMED_WITHOUT_SUPPORT":
            assert ligne["diagnostic_evidence"] or ligne["remediation_evidence"]


def test_la_matrice_des_prerequis_est_bien_regeneree():
    acheve = subprocess.run(
        [sys.executable, "scripts/build_1spe_prerequisite_support.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert acheve.returncode == 0, acheve.stdout + acheve.stderr
