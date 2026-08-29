"""Les deux versions d'une meme evaluation doivent etre interchangeables.

Defaut d'origine : EV-A evaluait C1, C2, C3, C5, C6, C7 et EV-B ajoutait C4.
Deux versions A et B d'un meme controle sont donnees a des eleves differents
dans les memes conditions : une capacite evaluee d'un cote et pas de l'autre
rend les deux notes non comparables. L'anciennete du defaut n'en est pas une
justification.

Le test compare les jeux de capacites REELLEMENT evaluees, exige leur egalite
et verifie que la tache C4 est bien une tache de linearite de l'esperance dans
chaque version, et non un simple retag d'une question existante.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
CHAPITRE = RACINE / "chapitres" / "1SPE-VARIABLES-ALEATOIRES"
EVALUATIONS = CHAPITRE / "evaluations"
META = re.compile(r"^%\s*META:\s*(\{.*\})\s*$", re.M)


def _meta(nom: str) -> dict:
    trouve = META.search((EVALUATIONS / nom).read_text(encoding="utf-8"))
    assert trouve, f"{nom} : META absent"
    return json.loads(trouve.group(1))


def _corps(nom: str) -> str:
    texte = (EVALUATIONS / nom).read_text(encoding="utf-8")
    return re.sub(r"^%.*$", "", texte, flags=re.M)


def test_les_deux_versions_evaluent_le_meme_jeu_de_capacites() -> None:
    blueprint_a = set(_meta("1SPE-VARALEA-EV-A.tex")["capacites_codes"])
    blueprint_b = set(_meta("1SPE-VARALEA-EV-B.tex")["capacites_codes"])

    contrat = yaml.safe_load((CHAPITRE / "contrat.yaml").read_text(encoding="utf-8"))
    attendu = {capacite["code"] for capacite in contrat["capacites"]}

    assert blueprint_a == attendu, f"EV-A n'evalue pas {sorted(attendu - blueprint_a)}"
    assert blueprint_b == attendu, f"EV-B n'evalue pas {sorted(attendu - blueprint_b)}"
    assert blueprint_a ^ blueprint_b == set(), "difference symetrique A/B non vide"


def test_la_tache_c4_est_une_vraie_linearite_de_l_esperance() -> None:
    """Un retag ne suffit pas : la question doit poser E(aX+b)."""
    motif = re.compile(
        r"On pose \$Y = -?\d*X\s*[+-]\s*\d+\$\..{0,120}?"
        r"linéarité de l['’]espérance",
        re.S,
    )
    for nom in ("1SPE-VARALEA-EV-A.tex", "1SPE-VARALEA-EV-B.tex"):
        corps = _corps(nom)
        assert motif.search(corps), f"{nom} : aucune tache C4 de linearite identifiee"
        assert "C4" in _meta(nom)["capacites_codes"], f"{nom} : C4 non declaree"


def test_les_deux_versions_gardent_le_format_historique() -> None:
    for nom in ("1SPE-VARALEA-EV-A.tex", "1SPE-VARALEA-EV-B.tex"):
        meta = _meta(nom)
        corps = _corps(nom)
        assert meta["bareme_total"] == 20, f"{nom} : bareme {meta['bareme_total']}"
        assert meta["duree_min"] == 55, f"{nom} : duree {meta['duree_min']}"

        sections = [
            (int(numero), int(points))
            for numero, points in re.findall(
                r"Exercice (\d) \\hfill \((\d+) points\)", corps
            )
        ]
        assert len(sections) == 4, f"{nom} : {len(sections)} exercices"
        assert sum(points for _, points in sections) == 20

        questions = [
            float(valeur.replace("{,}", "."))
            for valeur in re.findall(r"\\textit\{\((\d+(?:\{,\}\d+)?) ?pts? —", corps)
        ]
        assert sum(questions) == 20, f"{nom} : somme des questions {sum(questions)}"


def test_les_deux_versions_ont_la_meme_structure_de_questions() -> None:
    structures = {}
    for nom in ("1SPE-VARALEA-EV-A.tex", "1SPE-VARALEA-EV-B.tex"):
        blocs = re.split(r"\\section\*", _corps(nom))[1:]
        structures[nom] = [len(re.findall(r"\\item ", bloc)) for bloc in blocs]
    a, b = structures.values()
    assert a == b, f"structures differentes : {structures}"
    assert a == [4, 5, 3, 4], f"structure inattendue : {a}"


def test_c6_et_c7_restent_evaluees_dans_les_deux_versions() -> None:
    for nom in ("1SPE-VARALEA-EV-A.tex", "1SPE-VARALEA-EV-B.tex"):
        corps = _corps(nom)
        assert re.search(r"renvoie la moyenne de cet échantillon", corps), f"{nom} : C6"
        assert re.search(r"\\dfrac\{2\\sigma\}\{\\sqrt\{n\}\}", corps), f"{nom} : C7"
