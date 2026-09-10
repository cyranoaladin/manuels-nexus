"""Regression : un QCM doit avoir une cle, des diagnostics, et ne pas diverger.

Defaut d'origine : la revue de contenu 1NSI a classe en P1 les QCM livres sans
cle de correction, sans diagnostic par distracteur et sans renvoi de
remediation. S'y ajoute un risque structurel : quand le .tex imprime et le
.json exploitable sont maintenus a la main en parallele, ils divergent.

Ces tests s'appliquent a tout chapitre disposant d'un QCM au format JSON. Les
chapitres dont le QCM n'existe qu'en .tex ne sont pas encore couverts : ils le
deviendront a mesure de leur migration vers la source unique.
"""

from __future__ import annotations

import json
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

import _qcm_par_contenu as _par_contenu

RACINE = Path(__file__).resolve().parents[1]
GENERATEUR = RACINE / "scripts" / "build_qcm_tex.py"
DEBT_BUILDER = RACINE.parents[1] / "scripts" / "build_qcm_capacity_coverage_debt.py"
DEBT_LEDGER = RACINE.parents[1] / "audit" / "QCM_CAPACITY_COVERAGE_DEBT.json"
COLLECTION_CHAPTER_ROOTS = (
    RACINE / "chapitres",
    RACINE.parents[1] / "NSI" / "chapitres",
)


def _sources_qcm() -> dict[str, Path]:
    """Les noms de fichiers utilisent des prefixes courts (1SPE-SECDEG pour
    1SPE-SECOND-DEGRE) : on decouvre le fichier au lieu de deduire son nom."""
    trouves: dict[str, Path] = {}
    for chemin in sorted(RACINE.glob("chapitres/*/qcm/*-QCM.json")):
        trouves[chemin.parent.parent.name] = chemin
    return trouves


SOURCES = _sources_qcm()
CHAPITRES = sorted(SOURCES)
MARQUE_SOURCE_UNIQUE = "genere par scripts/build_qcm_tex.py"
CHAPITRES_SOURCE_UNIQUE = sorted(
    nom
    for nom, chemin in SOURCES.items()
    if chemin.with_suffix(".tex").exists()
    and MARQUE_SOURCE_UNIQUE in chemin.with_suffix(".tex").read_text(encoding="utf-8")
)


def _question(chapitre: str, question_id: str) -> dict:
    donnees = json.loads(SOURCES[chapitre].read_text(encoding="utf-8"))
    return next(item for item in donnees["questions"] if item["id"] == question_id)


def _debt_ledger() -> dict:
    return json.loads(DEBT_LEDGER.read_text(encoding="utf-8"))


def _independent_collection_inventory() -> dict[str, int]:
    qcm_sources = sorted(
        path
        for root in COLLECTION_CHAPTER_ROOTS
        for path in root.glob("*/qcm/*-QCM.json")
    )
    contracts = sorted(
        path
        for root in COLLECTION_CHAPTER_ROOTS
        for path in root.glob("*/contrat.yaml")
    )
    questions = sum(
        len(json.loads(path.read_text(encoding="utf-8"))["questions"])
        for path in qcm_sources
    )
    return {
        "qcm_files": len(qcm_sources),
        "chapters": len(contracts),
        "questions": questions,
    }


def _assert_debt_status_is_derived(ledger: dict) -> None:
    expected = (
        "PENDING_CONTENT_LOT"
        if ledger["total_missing"] or ledger["total_distractor_gaps"]
        else "CLOSED_OBJECTIVE_ZERO"
    )
    assert ledger["status"] == expected
    assert ledger["objective_zero"] is (expected == "CLOSED_OBJECTIVE_ZERO")
    assert ledger["human_approval_complete"] is False


def test_le_renderer_ne_forge_pas_un_renvoi_m1_absent() -> None:
    rendre = runpy.run_path(str(GENERATEUR))["rendre"]
    donnees = {
        "_source": "chapitres/TSPE-TEST/qcm/TSPE-TEST-QCM.json",
        "chapitre": "TSPE-TEST",
        "titre": "Test des renvois",
        "questions": [
            {
                "id": "Q1",
                "capacite": "C1",
                "enonce": "Une question de test.",
                "options": {"A": "exact", "B": "faux", "C": "faux", "D": "faux"},
                "correcte": "A",
                "diagnostics": {
                    "B": {"erreur": "Erreur B sans renvoi."},
                    "C": {"erreur": "Erreur C avec renvoi.", "renvoi": "C1"},
                    "D": {"erreur": "Erreur D avec renvoi vide.", "renvoi": "  "},
                },
            }
        ],
    }

    rendu = rendre(donnees)

    assert "Erreur B sans renvoi." in rendu
    assert "Erreur D avec renvoi vide." in rendu
    assert rendu.count("Renvoi : C1.") == 1
    assert "Renvoi : M1." not in rendu


def test_second_degre_q16_est_retiree_et_son_calcul_reste_dans_le_td() -> None:
    """La question Q16 a ete retiree le 2026-09-08, et pour une raison.

    Elle demandait l'image $V(4)$ d'un volume $x(30-2x)(20-2x)$ : une
    expression du TROISIEME degre, dans le chapitre du second degre. Elle
    testait donc le prerequis R3 -- evaluer une expression -- et non la
    capacite C6 qu'elle declarait. La disposition QCM-B4-002 l'enregistre :
    « Removed from current chapter auto-evaluation without renumbering ;
    volume calculation remains in TD fil rouge. No filler replacement. »

    Ce test gardait auparavant la cle de cette question. Il gardait donc une
    exigence que le depot avait remplacee, et faisait echouer la suite sur un
    contrat perime. Il garde desormais la decision elle-meme : la question
    absente, la numerotation inchangee, et le calcul de volume toujours
    travaille -- ailleurs, et au bon endroit.
    """
    donnees = json.loads(
        SOURCES["1SPE-SECOND-DEGRE"].read_text(encoding="utf-8")
    )
    identifiants = [q["id"] for q in donnees["questions"]]
    assert "Q16" not in identifiants
    # Retiree SANS renumerotation : les autres questions gardent leur identite.
    assert identifiants == [f"Q{n}" for n in range(1, 21) if n != 16]

    # Le calcul de volume n'a pas disparu du chapitre : il est traite dans le
    # TD fil rouge, ou il sert la modelisation au lieu de tester un prerequis.
    td = (
        RACINE
        / "chapitres/1SPE-SECOND-DEGRE/cours/07_td_fil_rouge.tex"
    ).read_text(encoding="utf-8")
    assert "V(x) = x(30 - 2x)(20 - 2x)" in td
    # L'aire de la base, elle, est bien un trinome : c'est ce que le chapitre
    # doit travailler.
    ouverture = (
        RACINE / "chapitres/1SPE-SECOND-DEGRE/cours/00_ouverture.tex"
    ).read_text(encoding="utf-8")
    assert "4x^2 - 100x + 600" in ouverture


def test_primitives_q2_a_une_unique_reponse_correcte() -> None:
    """Deux primitives diffèrent d'une constante, pas d'une affine non constante."""
    question = _question("TSPE-PRIMITIVES-EQDIFF", "Q2")

    bonne = _par_contenu.lettre_de_option(question, "$F-G$ est constante.")
    assert question["correcte"] == bonne
    assert _par_contenu.lettre_de_option(question, "pente non nulle")
    assert set(question["diagnostics"]) == set(question["options"]) - {bonne}
    assert _par_contenu.diagnostic_unique_contenant(
        question, "differer d'une constante"
    )
    assert _par_contenu.diagnostic_unique_contenant(question, "$(F-G)'=f-f=0$")


def test_suites_q11_distracteurs_correspondent_aux_erreurs_annoncees() -> None:
    """La somme vaut 121 ; 242 oublie /2 et 10 additionne les indices."""
    question = _question("1SPE-SUITES", "Q11")
    valeur_attendue = sum(3**k for k in range(5))

    assert valeur_attendue == 121
    matching = [
        lettre
        for lettre, option in question["options"].items()
        if option == f"${valeur_attendue}$"
    ]
    assert matching == [question["correcte"]]
    assert question["options"]["C"] == "$242$"
    assert "oublie de diviser" in question["diagnostics"]["C"]["erreur"]
    assert question["options"]["D"] == "$10$"
    assert "0 + 1 + 2 + 3 + 4 = 10" in question["diagnostics"]["D"]["erreur"]


def test_continuite_q12_exclut_explicitement_un_troisieme_point_fixe() -> None:
    question = _question("TSPE-CONTINUITE", "Q12")

    assert "exactement deux points fixes" in question["enonce"]
    assert question["correcte"] == _par_contenu.lettre_de_option(
        question, "vaut $0$ ou $2$"
    )


def test_limites_fonctions_q7_diagnostic_de_x_zero_est_exact() -> None:
    question = _question("TSPE-LIMITES-FONCTIONS", "Q7")
    diagnostic = _par_contenu.diagnostic_unique_contenant(
        question, "n'annule pas le denominateur"
    )

    assert "annule le numerateur" not in diagnostic


def test_limites_fonctions_q13_q14_ont_un_critere_de_reponse_unique() -> None:
    q13 = _question("TSPE-LIMITES-FONCTIONS", "Q13")
    q14 = _question("TSPE-LIMITES-FONCTIONS", "Q14")

    assert "utilise directement la limite usuelle" in q13["enonce"]
    assert q13["correcte"] == _par_contenu.lettre_de_option(
        q13, "Factoriser par $\\mathrm{e}^x$"
    )
    assert _par_contenu.diagnostic_unique_contenant(q13, "egalement valide")
    assert "méthode au programme" in q14["enonce"]
    assert q14["correcte"] == _par_contenu.lettre_de_option(
        q14, "$g(x) = \\mathrm{e}^x - 1 - x$"
    )


def test_suites_limites_q4_presente_une_seule_heredite_complete() -> None:
    question = _question("TSPE-SUITES-LIMITES", "Q4")

    assert question["correcte"] == "A"
    assert "2^{n+1} = 2\\times 2^n > 2n" in question["options"]["A"]
    assert "n \\geqslant 1" in question["options"]["A"]
    assert set(question["diagnostics"]) == {"B", "C", "D"}


def test_suites_limites_q9_enonce_les_hypotheses_et_une_seule_conclusion() -> None:
    question = _question("TSPE-SUITES-LIMITES", "Q9")

    assert "a \\geqslant -1" in question["enonce"]
    assert "n \\in \\mathbb{N}" in question["enonce"]
    assert question["correcte"] == "B"
    assert question["options"]["D"] == "$(1+a)^n \\geqslant 1+n^2a$"


def test_convexite_q11_definit_inflexion_par_changement_de_convexite() -> None:
    question = _question("TSPE-DERIVATION-CONVEXITE", "Q11")

    assert question["correcte"] == _par_contenu.lettre_de_option(
        question, "convexité change"
    )
    assert all(
        diagnostic["erreur"] != "Consulter le cours correspondant"
        for diagnostic in question["diagnostics"].values()
    )


def test_geometrie_reperee_q15_ecarte_le_trapeze_inclusif() -> None:
    question = _question("1SPE-GEOMETRIE-REPEREE", "Q15")

    assert question["correcte"] == _par_contenu.lettre_de_option(
        question, "un rectangle"
    )
    trapeze = _par_contenu.lettre_de_option(question, "non parallelogramme")
    assert "définition inclusive" in question["diagnostics"][trapeze]["erreur"]


def test_proba_conditionnelle_q18_decrit_les_donnees_qui_appellent_bayes() -> None:
    question = _question("1SPE-PROBA-COND", "Q18")

    assert "parts de production" in question["enonce"]
    assert "sachant qu'une piece est defectueuse" in question["enonce"]
    assert question["correcte"] == _par_contenu.lettre_de_option(
        question, "formule de Bayes"
    )


def test_correlation_causalite_q7_couvre_le_point_moyen_sans_ambiguite() -> None:
    question = _question("TCOMPL-CORRELATION-CAUSALITE", "Q7")

    assert question["capacite"] == "C1"
    assert "représente correctement le nuage" in question["enonce"]
    # A place un nuage errone avec le meme point moyen : la bonne option est
    # identifiee par la CONJONCTION nuage exact + point moyen exact.
    bonne = _par_contenu.lettre_de_option(
        question, "A(1 ; 2), B(3 ; 4), C(5 ; 0) ; le point moyen est $G(3 ; 2)$"
    )
    assert question["correcte"] == bonne
    assert all("le point moyen est" in option for option in question["options"].values())
    assert all("Le nuage contient" not in option for option in question["options"].values())
    assert "A(1 ; 2), B(3 ; 4), C(5 ; 0)" in question["options"][bonne]
    assert set(question["diagnostics"]) == set(question["options"]) - {bonne}
    for fragment in ("sommes", "interverties", "ne respecte pas les couples"):
        assert _par_contenu.diagnostic_unique_contenant(question, fragment)
    assert all(
        diagnostic["renvoi"] == "C1"
        for diagnostic in question["diagnostics"].values()
    )


@pytest.mark.parametrize(
    ("chapitre", "question_id", "renvoi"),
    [
        ("TSPE-DERIVATION-CONVEXITE", "Q1", "C1"),
        ("TSPE-DERIVATION-CONVEXITE", "Q3", "C1"),
        ("TSPE-PROBABILITES", "Q1", "C5"),
    ],
)
def test_renvois_tspe_pointent_vers_la_remediation_precise(
    chapitre: str, question_id: str, renvoi: str
) -> None:
    question = _question(chapitre, question_id)

    assert all(
        diagnostic.get("renvoi") == renvoi
        for diagnostic in question["diagnostics"].values()
    )


def test_suites_q3_evalue_l_absence_de_limite_sans_formalisation() -> None:
    question = _question("1SPE-SUITES", "Q3")

    assert question["capacite"] == "C8"
    assert question["correcte"] == _par_contenu.lettre_de_option(
        question, "ne pas avoir de limite"
    )
    assert _par_contenu.diagnostic_unique_contenant(question, "continue d'osciller")


def test_suites_q14_demande_un_critere_objectif() -> None:
    question = _question("1SPE-SUITES", "Q14")

    assert "utilise directement la raison" in question["enonce"]
    assert question["correcte"] == _par_contenu.lettre_de_option(
        question, "comparer le quotient $u_{n+1}/u_n$ a $1$"
    )
    assert _par_contenu.diagnostic_unique_contenant(question, "fonctionne aussi")


@pytest.mark.parametrize(
    ("chapitre", "question_id", "option", "fragments"),
    [
        ("1SPE-DERIVATION-GLOBAL", "Q3", "D", ("recopie la fonction", "sans la deriver")),
        ("1SPE-DERIVATION-GLOBAL", "Q14", "A", ("hors de l'intervalle",)),
        ("1SPE-DERIVATION-GLOBAL", "Q14", "B", ("120 - 3x", "x=40")),
        ("1SPE-DERIVATION-GLOBAL", "Q14", "D", ("60 - 6x", "x=10")),
        ("1SPE-DERIVATION-LOCAL", "Q4", "B", ("correct est $x-a$",)),
        ("1SPE-DERIVATION-LOCAL", "Q5", "B", ("$f(2+h)$", "sans former le taux")),
        ("1SPE-DERIVATION-LOCAL", "Q5", "C", ("$f(2)=4$",)),
        ("1SPE-DERIVATION-LOCAL", "Q9", "A", ("ordonnee a l'origine", "coefficient directeur")),
        ("1SPE-DERIVATION-LOCAL", "Q9", "B", ("abscisse du point", "coefficient directeur")),
        ("1SPE-DERIVATION-LOCAL", "Q12", "C", ("passe par l'origine",)),
        ("1SPE-DERIVATION-LOCAL", "Q12", "D", ("pente $f'(a)$", "ordonnee a l'origine")),
        ("1SPE-GEOMETRIE-REPEREE", "Q1", "C", ("vecteur normal $(2;1)$", "$2x+y-5=0$")),
        ("1SPE-GEOMETRIE-REPEREE", "Q1", "D", ("vecteur normal $(1;2)$", "$x+2y-7=0$")),
        ("1SPE-GEOMETRIE-REPEREE", "Q13", "D", ("multiplie par $2$", "$48$")),
        ("1SPE-PROBA-COND", "Q1", "D", ("complementaire", "$2/3$")),
        ("1SPE-PROBA-COND", "Q3", "A", ("facteur $2$", "$3/20$")),
        ("1SPE-PROBA-COND", "Q3", "D", ("denominateur $4$", "$6/5$")),
        ("1SPE-PROBA-COND", "Q9", "D", ("serait strictement superieure a 1",)),
        ("1SPE-PROBA-COND", "Q12", "B", ("borne", "$P(A\\cap B)\\leqslant",)),
        ("1SPE-PROBA-COND", "Q18", "A", ("taux de defaut dependent", "Bayes")),
        ("1SPE-PROBA-COND", "Q18", "C", ("$P(M_i\\mid D)$", "conditionnelles")),
        ("1SPE-PRODUIT-SCALAIRE", "Q1", "B", ("$3-(-2)=5$",)),
        ("1SPE-PRODUIT-SCALAIRE", "Q1", "C", ("$-3-8=-11$",)),
        ("1SPE-PRODUIT-SCALAIRE", "Q1", "D", ("$3+8=11$",)),
        ("1SPE-PRODUIT-SCALAIRE", "Q2", "D", ("$\\cos(\\pi/4)=\\sqrt{2}/2$",)),
        ("1SPE-PRODUIT-SCALAIRE", "Q5", "C", ("additionne deux normes",)),
        ("1SPE-PRODUIT-SCALAIRE", "Q6", "C", ("inegalite triangulaire",)),
        ("1SPE-PRODUIT-SCALAIRE", "Q7", "B", ("angle obtus",)),
        ("1SPE-PRODUIT-SCALAIRE", "Q9", "A", ("$\\tan(\\theta)=1/\\sqrt{3}$",)),
        ("1SPE-PRODUIT-SCALAIRE", "Q9", "C", ("$\\tan(\\theta)=\\sqrt{3}$",)),
        ("1SPE-PRODUIT-SCALAIRE", "Q14", "D", ("$(8-5)^2=9$",)),
        # Le diagnostic doit dire d'ou vient 2bc : l'eleve a annule le mauvais
        # membre de la formule d'Al-Kashi.
        (
            "1SPE-PRODUIT-SCALAIRE",
            "Q15",
            "C",
            ("terme $2bc", "annule le mauvais membre"),
        ),
        ("1SPE-SECOND-DEGRE", "Q1", "D", ("exposants entiers naturels",)),
        ("1SPE-SECOND-DEGRE", "Q15", "B", ("$4-2k=0$", "$k=2$")),
        # La cause de t = 1 doit etre nommee : une division par 4a au lieu de
        # 2a. Elle l'est sans ecrire la formule elle-meme, que le chapitre
        # n'enseigne pas -- il enseigne la forme canonique.
        (
            "1SPE-SECOND-DEGRE",
            "Q18",
            "B",
            ("$t=1$", "$4 \\times 5$", "$2 \\times 5$"),
        ),
        ("1SPE-SUITES", "Q2", "C", ("oublie le $-2$", "$v_1=3\\times4=12$", "$v_2=3\\times12-2=34$")),
        ("1SPE-SUITES", "Q2", "D", ("soustrait $v_0=4$", "$v_2=3\\times8-2=22$")),
        ("1SPE-SUITES", "Q5", "B", ("quatre accroissements", "$8+4\\times(-3)=-4$")),
        ("1SPE-SUITES", "Q10", "A", ("$n^2/2$", "$20^2/2=200$")),
        ("1SPE-SUITES", "Q12", "D", ("ajoute $2$", "$16$")),
        ("1SPE-SUITES", "Q20", "C", ("aucun test de seuil", "100 iterations")),
    ],
)
def test_diagnostic_1spe_explique_exactement_son_distracteur(
    chapitre: str, question_id: str, option: str, fragments: tuple[str, ...]
) -> None:
    """Les fragments doivent designer UN diagnostic de distracteur, et un seul.

    La lettre de la table est historique : la politique de distribution des
    cles permute les options en emportant leur diagnostic. L'invariant
    scientifique est que la preuve attendue existe et n'est pas ambigue --
    le garde d'unicite echoue si deux diagnostics la portent.
    """

    question = _question(chapitre, question_id)
    assert _par_contenu.diagnostic_unique_contenant_tous(question, fragments), (
        f"{chapitre}/{question_id} (jadis {option})"
    )


@pytest.mark.parametrize("chapitre", CHAPITRES)
def test_chaque_distracteur_porte_un_diagnostic_et_un_renvoi(chapitre: str) -> None:
    """Diagnostics/renvois de distracteurs sous contrat de dette declare.

    Les lacunes sont dérivées question par question dans le registre. Vert si
    et seulement si l'écart observé est EXACTEMENT l'écart déclaré ; toute
    nouvelle lacune ou clôture non recalculée échoue.
    """
    donnees = json.loads(SOURCES[chapitre].read_text(encoding="utf-8"))
    ledger = _debt_ledger()
    _assert_debt_status_is_derived(ledger)
    declarees = ledger.get("distractor_gaps_by_chapter", {}).get(chapitre, {})

    observees: dict[str, list[str]] = {}
    for question in donnees["questions"]:
        if "options" not in question:
            # Schema reduit hérité (id / capacite / correcte / diagnostics) : les
            # enonces et les options vivent alors dans le .tex. Ces chapitres sont
            # couverts par les autres controles mais pas par celui-ci tant qu'ils
            # n'ont pas migre vers la source unique.
            continue
        correcte = question["correcte"]
        assert correcte in question["options"], (
            f"{chapitre}/{question['id']} : la reponse correcte ne figure pas parmi les options"
        )
        lacunes: list[str] = []
        for lettre in question["options"]:
            if lettre == correcte:
                assert lettre not in question["diagnostics"], (
                    f"{chapitre}/{question['id']} : la bonne reponse porte un diagnostic d'erreur"
                )
                continue
            diagnostic = question["diagnostics"].get(lettre)
            if not diagnostic:
                lacunes.append(f"{lettre}:absent")
                continue
            if not diagnostic.get("erreur", "").strip():
                lacunes.append(f"{lettre}:erreur-vide")
            if not diagnostic.get("renvoi", "").strip():
                lacunes.append(f"{lettre}:renvoi-vide")
        if lacunes:
            observees[question["id"]] = sorted(lacunes)

    assert observees == declarees, (
        f"{chapitre} : lacunes de distracteurs hors du registre de dette "
        f"declare (nouvelles ou resorbees) — observees={observees} "
        f"declarees={declarees}"
    )


@pytest.mark.parametrize("chapitre", CHAPITRES)
def test_identifiants_de_questions_uniques(chapitre: str) -> None:
    donnees = json.loads(SOURCES[chapitre].read_text(encoding="utf-8"))
    identifiants = [question["id"] for question in donnees["questions"]]
    assert len(identifiants) == len(set(identifiants)), f"{chapitre} : identifiants de questions en double"


@pytest.mark.parametrize("chapitre", CHAPITRES)
def test_toutes_les_capacites_du_contrat_sont_interrogees(chapitre: str) -> None:
    """Couverture QCM x capacites sous contrat de dette declare (cloture A4).

    Le registre est recalculé depuis les contrats et les sources QCM. Le test
    est vert si et seulement si l'écart observé est exactement l'écart
    déclaré : toute nouvelle lacune et toute ligne résolue mais périmée font
    échouer le gate.
    """
    import yaml

    contrat = yaml.safe_load(
        (RACINE / "chapitres" / chapitre / "contrat.yaml").read_text(encoding="utf-8")
    )
    attendues = {capacite["code"] for capacite in (contrat.get("capacites") or [])}
    donnees = json.loads(SOURCES[chapitre].read_text(encoding="utf-8"))
    interrogees = {question["capacite"] for question in donnees["questions"]}
    manquantes = attendues - interrogees

    ledger = _debt_ledger()
    _assert_debt_status_is_derived(ledger)
    declarees = set(ledger["missing_by_chapter"].get(chapitre, []))

    nouvelles = manquantes - declarees
    assert not nouvelles, (
        f"{chapitre} : capacites absentes du QCM HORS dette declaree : "
        f"{sorted(nouvelles)}"
    )
    resorbees = declarees - manquantes
    assert not resorbees, (
        f"{chapitre} : capacites desormais couvertes mais encore au registre "
        f"de dette (registre perime) : {sorted(resorbees)}"
    )


@pytest.mark.parametrize("chapitre", CHAPITRES_SOURCE_UNIQUE)
def test_le_tex_ne_diverge_pas_de_sa_source_json(chapitre: str) -> None:
    resultat = subprocess.run(
        [sys.executable, str(GENERATEUR), "--chap", chapitre, "--check"],
        capture_output=True,
        text=True,
    )
    assert resultat.returncode == 0, (
        f"{chapitre} : le .tex a diverge de son .json. "
        f"Regenerer avec build_qcm_tex.py --chap {chapitre}.\n{resultat.stderr}"
    )


@pytest.mark.parametrize("chapitre", CHAPITRES_SOURCE_UNIQUE)
def test_la_cle_generee_est_conditionnee_a_la_variante_professeur(chapitre: str) -> None:
    tex = SOURCES[chapitre].with_suffix(".tex").read_text(encoding="utf-8")
    debut = tex.index("\\ifnxVersionProfesseur")
    cle = tex.index("Clé de correction")
    fin = tex.rindex("\\fi")

    assert debut < cle < fin


def test_le_gate_des_cles_couvre_exactement_les_35_qcm() -> None:
    assert len(SOURCES) == 35
    assert len(CHAPITRES_SOURCE_UNIQUE) == 35
    assert set(CHAPITRES_SOURCE_UNIQUE) == set(SOURCES)


def test_le_total_de_dette_diagnostique_est_derive_des_lignes() -> None:
    ledger = _debt_ledger()
    observed = sum(
        len(gaps)
        for questions in ledger["distractor_gaps_by_chapter"].values()
        for gaps in questions.values()
    )
    assert ledger["total_distractor_gaps"] == observed


def test_le_total_de_capacites_manquantes_est_derive_des_lignes() -> None:
    ledger = _debt_ledger()
    observed = sum(len(capacities) for capacities in ledger["missing_by_chapter"].values())
    assert ledger["total_missing"] == observed


def test_le_registre_de_dette_est_courant_et_reproductible() -> None:
    result = subprocess.run(
        [sys.executable, str(DEBT_BUILDER), "--check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    ledger = _debt_ledger()
    expected_inventory = _independent_collection_inventory()
    assert ledger["inventory"] == expected_inventory
    assert len(ledger["source_inputs"]) == expected_inventory["chapters"]
    _assert_debt_status_is_derived(ledger)


@pytest.mark.parametrize(
    "chapitre",
    [
        chapitre
        for chapitre in CHAPITRES_SOURCE_UNIQUE
        if "\\neq" in SOURCES[chapitre].read_text(encoding="utf-8")
    ],
)
def test_la_generation_preserve_les_commandes_neq(chapitre: str) -> None:
    source = SOURCES[chapitre].read_text(encoding="utf-8")
    tex = SOURCES[chapitre].with_suffix(".tex").read_text(encoding="utf-8")

    assert tex.count("\\neq") == source.count("\\\\neq")


def test_les_sauts_de_ligne_python_sont_des_newlines_json_reels() -> None:
    donnees = json.loads(SOURCES["1SPE-SUITES"].read_text(encoding="utf-8"))
    q19 = next(question for question in donnees["questions"] if question["id"] == "Q19")
    q20 = next(question for question in donnees["questions"] if question["id"] == "Q20")
    q21 = next(question for question in donnees["questions"] if question["id"] == "Q21")

    assert "\ndef terme(n):" in q19["enonce"]
    # La lettre est mobile : le contrat porte sur la PRESENCE de vrais sauts
    # de ligne dans chaque option de code, pas sur la position du while.
    assert all("\nn = 0\n" in option for option in q20["options"].values())
    assert any("\nwhile" in option for option in q20["options"].values())
    assert "\nS = 0\nfor" in q21["enonce"]

    tex = SOURCES["1SPE-SUITES"].with_suffix(".tex").read_text(encoding="utf-8")
    for invalid_command in ("\\ndef", "\\nQuelle", "\\nn", "\\nwhile", "\\nfor", "\\nS"):
        assert invalid_command not in tex
