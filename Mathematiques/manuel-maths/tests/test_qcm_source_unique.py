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
import subprocess
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
GENERATEUR = RACINE / "scripts" / "build_qcm_tex.py"


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


def test_second_degre_q16_cle_correspond_au_calcul_independant() -> None:
    """Régression SCIENTIFIC_P0 : la clé doit désigner l'unique valeur V(4)."""
    question = _question("1SPE-SECOND-DEGRE", "Q16")
    valeur_attendue = 4 * (30 - 2 * 4) * (20 - 2 * 4)
    options_correctes = [
        lettre
        for lettre, option in question["options"].items()
        if option.strip() == f"$V(4) = {valeur_attendue}$"
    ]

    assert valeur_attendue == 1056
    assert question["enonce"].endswith("Quelle est la valeur de $V(4)$ ?")
    assert options_correctes == ["D"]
    assert question["correcte"] == options_correctes[0]
    assert set(question["diagnostics"]) == set(question["options"]) - {"D"}
    assert "1664" in question["diagnostics"]["A"]["erreur"]
    assert "2400" in question["diagnostics"]["B"]["erreur"]
    assert "264" in question["diagnostics"]["C"]["erreur"]


def test_primitives_q2_a_une_unique_reponse_correcte() -> None:
    """Deux primitives diffèrent d'une constante, pas d'une affine non constante."""
    question = _question("TSPE-PRIMITIVES-EQDIFF", "Q2")

    assert question["correcte"] == "C"
    assert "constante" in question["options"]["C"]
    assert "pente non nulle" in question["options"]["B"]
    assert set(question["diagnostics"]) == {"A", "B", "D"}
    assert "differer d'une constante" in question["diagnostics"]["A"]["erreur"]
    assert "$(F-G)'=f-f=0$" in question["diagnostics"]["B"]["erreur"]


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
    assert question["correcte"] == "C"


def test_limites_fonctions_q7_diagnostic_de_x_zero_est_exact() -> None:
    question = _question("TSPE-LIMITES-FONCTIONS", "Q7")
    diagnostic = question["diagnostics"]["D"]["erreur"]

    assert "n'annule pas le denominateur" in diagnostic
    assert "annule le numerateur" not in diagnostic


def test_limites_fonctions_q13_q14_ont_un_critere_de_reponse_unique() -> None:
    q13 = _question("TSPE-LIMITES-FONCTIONS", "Q13")
    q14 = _question("TSPE-LIMITES-FONCTIONS", "Q14")

    assert "utilise directement la limite usuelle" in q13["enonce"]
    assert q13["correcte"] == "B"
    assert "egalement valide" in q13["diagnostics"]["C"]["erreur"]
    assert "methode au programme" in q14["enonce"]
    assert q14["correcte"] == "B"


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

    assert question["correcte"] == "B"
    assert "convexite change" in question["options"]["B"]
    assert all(
        diagnostic["erreur"] != "Consulter le cours correspondant"
        for diagnostic in question["diagnostics"].values()
    )


def test_geometrie_reperee_q15_ecarte_le_trapeze_inclusif() -> None:
    question = _question("1SPE-GEOMETRIE-REPEREE", "Q15")

    assert question["correcte"] == "B"
    assert "non parallelogramme" in question["options"]["D"]
    assert "definition inclusive" in question["diagnostics"]["D"]["erreur"]


def test_proba_conditionnelle_q18_decrit_les_donnees_qui_appellent_bayes() -> None:
    question = _question("1SPE-PROBA-COND", "Q18")

    assert "parts de production" in question["enonce"]
    assert "sachant qu'une piece est defectueuse" in question["enonce"]
    assert question["correcte"] == "B"


def test_suites_q3_evalue_l_absence_de_limite_sans_formalisation() -> None:
    question = _question("1SPE-SUITES", "Q3")

    assert question["capacite"] == "C8"
    assert question["correcte"] == "C"
    assert "ne pas avoir de limite" in question["options"]["C"]
    assert "continue d'osciller" in question["diagnostics"]["D"]["erreur"]


def test_suites_q14_demande_un_critere_objectif() -> None:
    question = _question("1SPE-SUITES", "Q14")

    assert "utilise directement la raison" in question["enonce"]
    assert question["correcte"] == "B"
    assert "fonctionne aussi" in question["diagnostics"]["A"]["erreur"]


@pytest.mark.parametrize(
    ("chapitre", "question_id", "option", "fragments"),
    [
        ("1SPE-DERIVATION-GLOBAL", "Q3", "D", ("primitive", "pas la derivee")),
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
        ("1SPE-GEOMETRIE-REPEREE", "Q1", "C", ("ajuste la constante", "point $A$", "point $B$")),
        ("1SPE-GEOMETRIE-REPEREE", "Q1", "D", ("vecteur normal $(1;2)$", "point $B$")),
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
        ("1SPE-PRODUIT-SCALAIRE", "Q15", "C", ("terme $2bc", "pas $a^2$")),
        ("1SPE-SECOND-DEGRE", "Q1", "D", ("exposants entiers naturels",)),
        ("1SPE-SECOND-DEGRE", "Q15", "B", ("$4-2k=0$", "$k=2$")),
        ("1SPE-SECOND-DEGRE", "Q18", "B", ("$-b/(4a)$", "$t=1$")),
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
    diagnostic = _question(chapitre, question_id)["diagnostics"][option]["erreur"]

    for fragment in fragments:
        assert fragment in diagnostic, (
            f"{chapitre}/{question_id}/{option}: le diagnostic ne prouve pas "
            f"le distracteur par le fragment attendu {fragment!r}"
        )


@pytest.mark.parametrize("chapitre", CHAPITRES)
def test_chaque_distracteur_porte_un_diagnostic_et_un_renvoi(chapitre: str) -> None:
    """Diagnostics/renvois de distracteurs sous contrat de dette declare.

    Les lacunes P1 anterieures (distracteurs livres sans diagnostic ou sans
    renvoi de remediation) sont FIGEES question par question dans
    audit/QCM_CAPACITY_COVERAGE_DEBT.json (status PENDING_CONTENT_LOT). Vert
    si et seulement si l'ecart observe est EXACTEMENT l'ecart declare ; toute
    nouvelle lacune, ou lacune resorbee sans mise a jour du registre, echoue.
    Le NO-GO reste porte par release-strict.
    """
    donnees = json.loads(SOURCES[chapitre].read_text(encoding="utf-8"))
    ledger = json.loads(
        (RACINE.parents[1] / "audit" / "QCM_CAPACITY_COVERAGE_DEBT.json").read_text(
            encoding="utf-8"
        )
    )
    assert ledger["status"] == "PENDING_CONTENT_LOT"
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

    Les trous de couverture anterieurs a la campagne sont FIGES dans
    audit/QCM_CAPACITY_COVERAGE_DEBT.json (status PENDING_CONTENT_LOT,
    production de questions = lot QCM non demarre). Le test est VERT si et
    seulement si l'ecart observe est EXACTEMENT l'ecart declare : toute
    nouvelle capacite non interrogee echoue, et toute capacite couverte
    depuis doit sortir du registre. Le NO-GO reste porte par release-strict.
    """
    import yaml

    contrat = yaml.safe_load(
        (RACINE / "chapitres" / chapitre / "contrat.yaml").read_text(encoding="utf-8")
    )
    attendues = {capacite["code"] for capacite in (contrat.get("capacites") or [])}
    donnees = json.loads(SOURCES[chapitre].read_text(encoding="utf-8"))
    interrogees = {question["capacite"] for question in donnees["questions"]}
    manquantes = attendues - interrogees

    ledger_path = RACINE.parents[1] / "audit" / "QCM_CAPACITY_COVERAGE_DEBT.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert ledger["status"] == "PENDING_CONTENT_LOT"
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
    cle = tex.index("Cle de correction")
    fin = tex.rindex("\\fi")

    assert debut < cle < fin


def test_le_gate_des_cles_couvre_exactement_les_35_qcm() -> None:
    assert len(SOURCES) == 35
    assert len(CHAPITRES_SOURCE_UNIQUE) == 35
    assert set(CHAPITRES_SOURCE_UNIQUE) == set(SOURCES)


def test_le_total_de_dette_diagnostique_est_derive_des_lignes() -> None:
    ledger = json.loads(
        (RACINE.parents[1] / "audit/QCM_CAPACITY_COVERAGE_DEBT.json").read_text(
            encoding="utf-8"
        )
    )
    observed = sum(
        len(gaps)
        for questions in ledger["distractor_gaps_by_chapter"].values()
        for gaps in questions.values()
    )
    assert ledger["total_distractor_gaps"] == observed


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
    assert "\nn = 0\nwhile" in q20["options"]["B"]
    assert "\nS = 0\nfor" in q21["enonce"]

    tex = SOURCES["1SPE-SUITES"].with_suffix(".tex").read_text(encoding="utf-8")
    for invalid_command in ("\\ndef", "\\nQuelle", "\\nn", "\\nwhile", "\\nfor", "\\nS"):
        assert invalid_command not in tex
