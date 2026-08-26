"""Régressions scientifiques sur la définition des suites géométriques."""

from __future__ import annotations

import json
import re
from pathlib import Path


CHAPTER = Path(__file__).resolve().parents[1] / "chapitres" / "1SPE-SUITES"


def source(relative_path: str) -> str:
    text = (CHAPTER / relative_path).read_text(encoding="utf-8")
    return re.sub(r"\s+", " ", text)


def test_definition_par_recurrence_accepte_raison_et_termes_nuls() -> None:
    course = source("cours/12_C3_suites_geometriques.tex")

    assert "s'il existe un réel $q$, appelé" in course
    assert "La valeur $q=0$ est autorisée" in course
    assert "La suite nulle est donc géométrique" in course
    assert "une suite géométrique ne peut pas avoir de terme nul" not in course


def test_formule_explicite_ne_restreint_pas_artificiellement_u0_ou_q() -> None:
    course = source("cours/12_C3_suites_geometriques.tex")

    assert "de premier terme $u_0$ et de raison $q$" in course
    assert "Pour $n=0$, le terme $u_0$ reste la donnée initiale" in course
    assert "pour tout entier $n\\geq1$" in course
    assert "si $n=p$, l'égalité $u_n=u_p$ est immédiate" in course
    assert "Si $n>p$" in course
    assert "Si $q\\neq 0$, cette dernière égalité" in course


def test_quotient_est_une_caracterisation_conditionnelle_pas_la_definition() -> None:
    method = source("methodes/1SPE-SUITES-ME-003.tex")
    remediation = source("remediation/1SPE-SUITES-RE-C3.tex")
    evaluations = " ".join(
        source(path)
        for path in (
            "evaluations/1SPE-SUITES-EV-A-corrige.tex",
            "evaluations/1SPE-SUITES-EV-B-corrige.tex",
        )
    )

    assert "Méthode A — relation multiplicative" in method
    assert "Méthode B — quotient, si les termes sont non nuls" in method
    assert "caractérisation par quotient valable ici" in remediation
    assert "c'est la définition d'une suite géométrique" not in remediation
    assert "Caractérisation applicable ici" in evaluations
    assert "Définition : une suite est géométrique si le quotient" not in evaluations


def test_aucun_objet_du_chapitre_ne_presente_le_quotient_comme_definition() -> None:
    offenders = []
    for path in sorted(CHAPTER.rglob("*.tex")):
        text = source(str(path.relative_to(CHAPTER)))
        if "c'est la définition d'une suite géométrique" in text:
            offenders.append(str(path.relative_to(CHAPTER)))
        if "Définition : une suite est géométrique si le quotient" in text:
            offenders.append(str(path.relative_to(CHAPTER)))

    assert offenders == []


def test_un_prefixe_fini_ne_suffit_pas_a_prouver_une_suite_geometrique() -> None:
    remediation = source("remediation/1SPE-SUITES-RE-C3.tex")

    assert "Ces trois quotients ne suffisent pas" in remediation
    assert "$v_4=55$" in remediation
    assert "On ajoute maintenant l'information" in remediation
    assert "$v_{n+1}=3v_n$ pour tout $n\\in\\mathbb{N}$" in remediation


def test_moins_un_puissance_n_est_bien_geometrique() -> None:
    sums = source("cours/13_C4_sommes.tex")

    assert "La suite $(u_n)$ définie par $u_n=(-1)^n$ est géométrique" in sums
    assert "$u_n=(-1)^n$ n'est ni arithmétique ni géométrique" not in sums


def test_notation_fonctionnelle_u_de_n_n_est_pas_declaree_fausse() -> None:
    general = source("cours/10_C1_generalites_suites.tex")

    assert "La notation fonctionnelle $u(n)$ est mathématiquement correcte" in general
    assert "jamais $u(n)$" not in general


def test_brief_de_curation_distingue_definition_et_test_par_quotient() -> None:
    dossier = json.loads(
        (CHAPTER / "dossier_curation.json").read_text(encoding="utf-8")
    )
    brief = dossier["capacites"]["C3"]["brief"]

    assert "Definition : u(n+1) = q*u(n), avec q reel eventuellement nul." in brief
    assert "Le quotient est seulement une caracterisation" in brief


def test_cas_zero_et_moins_un_sont_mathematiquement_coherents() -> None:
    u0 = 7
    q = 0
    values = [u0]
    for _ in range(3):
        values.append(q * values[-1])
    assert values == [7, 0, 0, 0]

    zero_sequence = [0, 0, 0, 0]
    for candidate_reason in (-3, 0, 1, 7):
        assert all(
            zero_sequence[n + 1] == candidate_reason * zero_sequence[n]
            for n in range(3)
        )

    alternating = [(-1) ** n for n in range(8)]
    assert all(alternating[n + 1] == -alternating[n] for n in range(7))
    assert sum(alternating[: 2 * 3 + 1]) == 1


def test_les_syntheses_generiques_ne_reintroduisent_pas_zero_puissance_zero() -> None:
    expected_guards = {
        "cours/11_C2_suites_arithmetiques.tex": "si $q=0$, on garde $u_0$ comme donnée initiale",
        "cours/12_C3_suites_geometriques.tex": "si $q=0$, la formule s'utilise pour $n\\geq1$",
        "cours/15_C6_modelisation.tex": "Pour $q=0$, le terme initial reste donné séparément",
        "cours/16_C7_algorithmique.tex": "si $q=0$ et $n=0$, retourner directement $u_0$",
        "methodes/1SPE-SUITES-ME-006.tex": "Si $q=0$, traiter $n=0$ séparément",
    }

    for relative_path, guard in expected_guards.items():
        assert guard in source(relative_path), relative_path


def test_formule_depuis_u1_traite_q_nul_sans_zero_puissance_zero() -> None:
    course = source("cours/12_C3_suites_geometriques.tex")

    assert "si $q=0$, on conserve $u_1$ au rang $1$" in course
    assert "et on utilise cette formule pour $n>1$" in course


def test_generalisation_co048_traite_r_nul_sans_zero_puissance_zero() -> None:
    correction = source("corriges/1SPE-SUITES-CO-048.tex")

    assert "Pour $n=0$, on conserve la donnée initiale $u_0$" in correction
    assert r"pour $n\geq1$, on a $u_n=u_0\times r^n$" in correction


def test_brief_de_curation_garde_le_cas_q_nul_dans_la_formule_explicite() -> None:
    dossier = json.loads(
        (CHAPTER / "dossier_curation.json").read_text(encoding="utf-8")
    )
    brief = dossier["capacites"]["C3"]["brief"]

    assert "pour n >= 1 si q = 0" in brief
