#!/usr/bin/env python3
"""Solveur independant de QCM : il ne voit JAMAIS la reponse declaree.

Independance STRUCTURELLE, pas declarative. `SolverInput` n'a pas de champ
capable de porter la cle : la construire depuis une question canonique passe
par `sanitize`, qui REFUSE toute charge utile contenant `correcte`,
`declared_answer`, `key`, un verdict ou une preuve historique. Le verificateur,
lui, ne s'execute qu'apres le solveur et charge la cle separement.

    question canonique
          | sanitize  (retire et interdit la cle)
          v
    SolverInput  --->  famille generique  --->  vecteur de verite des options
                                                        |
    cle canonique -------------------------------------+--->  verificateur

Le routage se fait sur une FAMILLE mathematique generique deduite de l'enonce,
jamais sur un identifiant de question : aucun `if question_id == ...`, aucune
table de reponses. Un identifiant de question du corpus ne doit pas apparaitre
dans ce fichier ; un test le verifie.

Le solveur ne dit pas "la cle est B". Il rend d'abord la verite mathematique de
chaque option ; l'unicite et la comparaison a la cle sont l'affaire du
verificateur.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))

from latex_arith import UnsupportedExpression, evaluate  # noqa: E402

SOLVER_VERSION = "1.0.0"

#: Tout champ qui trahirait la reponse. Leur presence rend l'entree invalide.
FORBIDDEN_INPUT_FIELDS = frozenset(
    {
        "correcte",
        "correct_answer",
        "declared_answer",
        "declared_answer_current_source",
        "declared_key",
        "key",
        "answer",
        "answer_key_status",
        "independent_solution",
        "verdict",
        "review_evidence",
        "diagnostics",
        "diagnostic_details",
    }
)


class DeclaredAnswerLeak(ValueError):
    """Levee quand une entree de solveur porte la reponse declaree."""


@dataclass(frozen=True)
class SolverInput:
    """Ce que le solveur a le droit de voir, et rien d'autre."""

    question_id: str
    statement: str
    options: dict[str, str]
    capacity: str | None = None

    def __post_init__(self) -> None:
        if not self.statement.strip():
            raise ValueError("enonce vide")
        if not self.options:
            raise ValueError("aucune option")

    def payload(self) -> dict[str, Any]:
        return {
            "question_id": self.question_id,
            "statement": self.statement,
            "options": dict(self.options),
            "capacity": self.capacity,
        }

    def digest(self) -> str:
        blob = json.dumps(
            self.payload(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def sanitize(question: dict[str, Any], *, question_id: str | None = None) -> SolverInput:
    """Construit l'entree du solveur en refusant toute fuite de la cle."""

    leaked = sorted(FORBIDDEN_INPUT_FIELDS & set(question))
    if leaked:
        raise DeclaredAnswerLeak(
            "champs interdits dans l'entree du solveur: " + ", ".join(leaked)
        )
    identifier = question_id or question.get("id") or question.get("question_id")
    if not identifier:
        raise ValueError("identifiant de question absent")
    statement = question.get("enonce") or question.get("statement")
    options = question.get("options")
    if not isinstance(options, dict):
        raise ValueError("options absentes ou mal formees")
    return SolverInput(
        question_id=str(identifier),
        statement=str(statement),
        options={str(k): str(v) for k, v in options.items()},
        capacity=question.get("capacite") or question.get("capacity"),
    )


def sanitize_canonical(question: dict[str, Any]) -> SolverInput:
    """Comme `sanitize`, mais depuis une question canonique complete.

    Les champs interdits sont retires AVANT construction : le solveur ne les
    recoit pas, et l'appelant ne peut pas les lui transmettre par inadvertance.
    """

    stripped = {
        key: value
        for key, value in question.items()
        if key not in FORBIDDEN_INPUT_FIELDS
    }
    return sanitize(stripped, question_id=question.get("id"))


# ---------------------------------------------------------------------------
# Lecture des valeurs
# ---------------------------------------------------------------------------


def _plain(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", str(text))
    stripped = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", stripped).strip().lower()


def _math_text(text: str) -> str:
    """Enonce comparable : accents retires, delimiteurs TeX enleves."""

    return _plain(str(text).replace("$", " "))


def _numbers(text: str) -> list[Fraction]:
    """Toutes les valeurs numeriques lisibles d'un fragment LaTeX."""

    found: list[Fraction] = []
    for token in re.findall(r"-?\d+(?:\{,\}\d+)?", str(text)):
        try:
            found.append(evaluate(token))
        except UnsupportedExpression:
            continue
    return found


def option_value(raw: str) -> Fraction | None:
    """Valeur exacte d'une option, ou None si elle n'est pas numerique."""

    text = str(raw).strip()
    text = re.sub(r"~?(euros?|%)\b", "", text)
    text = text.replace(r"\,\%", "").replace(r"\%", "")
    text = re.sub(r"\\text\{[^}]*\}", "", text)
    text = text.replace("$", "").strip()
    text = re.sub(r"\s*(euros?)\s*$", "", text, flags=re.I).strip()
    if not text:
        return None
    try:
        return evaluate(text)
    except UnsupportedExpression:
        return None


def option_values(options: dict[str, str]) -> dict[str, Fraction | None]:
    return {letter: option_value(raw) for letter, raw in options.items()}


# ---------------------------------------------------------------------------
# Resultat
# ---------------------------------------------------------------------------


@dataclass
class SolverResult:
    status: str
    family: str | None
    option_truths: dict[str, bool] = field(default_factory=dict)
    computed_value: str | None = None
    independent_evidence: str = ""
    reason: str | None = None

    @property
    def true_options(self) -> list[str]:
        return sorted(letter for letter, truth in self.option_truths.items() if truth)

    @property
    def true_option_count(self) -> int:
        return len(self.true_options)

    @property
    def unique_answer(self) -> str | None:
        options = self.true_options
        return options[0] if len(options) == 1 else None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "solver_family": self.family,
            "solver_version": SOLVER_VERSION,
            "computed_option_truths": dict(sorted(self.option_truths.items())),
            "true_option_count": self.true_option_count,
            "computed_unique_answer": self.unique_answer,
            "computed_value": self.computed_value,
            "independent_evidence": self.independent_evidence,
            "reason": self.reason,
        }

    def digest(self) -> str:
        blob = json.dumps(
            self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _numeric_truths(
    options: dict[str, str], expected: Fraction
) -> dict[str, bool] | None:
    """Verite de chaque option face a une constante calculee independamment.

    Une option qui ne denote aucune valeur determinee ne peut pas etre egale a
    la constante cherchee : elle est fausse, et non indecidable. Il faut
    toutefois qu'au moins une option soit lisible, sinon la famille ne
    s'applique pas.
    """

    values = option_values(options)
    if all(value is None for value in values.values()):
        return None
    return {letter: value == expected for letter, value in values.items()}


def _resolved(
    family: str, options: dict[str, str], expected: Fraction, evidence: str
) -> SolverResult | None:
    truths = _numeric_truths(options, expected)
    if truths is None:
        return None
    return SolverResult(
        status="MACHINE_RESOLVED",
        family=family,
        option_truths=truths,
        computed_value=str(expected),
        independent_evidence=evidence,
    )


# ---------------------------------------------------------------------------
# Familles generiques
# ---------------------------------------------------------------------------


def _uniform_outcome_probability(inp: SolverInput) -> SolverResult | None:
    """Espace uniforme fini, evenement elementaire : P = 1 / cardinal."""

    text = _plain(inp.statement)
    if "de equilibre" not in text and "de non truque" not in text:
        return None
    if not re.search(r"p\s*\(\s*x\s*=", text):
        return None
    faces = Fraction(6)
    return _resolved(
        "UNIFORM_DISCRETE_PROBABILITY",
        inp.options,
        Fraction(1) / faces,
        "Espace uniforme a 6 issues equiprobables ; un evenement elementaire "
        "a pour probabilite 1/6.",
    )


def _distribution_total_mass(inp: SolverInput) -> SolverResult | None:
    """Axiome : la somme des probabilites d'une loi vaut 1."""

    text = _plain(inp.statement)
    if "somme des probabilites" not in text:
        return None
    return _resolved(
        "PROBABILITY_DISTRIBUTION_TOTAL_MASS",
        inp.options,
        Fraction(1),
        "Axiome de normalisation : la somme des probabilites d'une loi vaut 1.",
    )


def _bernoulli_repetition(inp: SolverInput) -> SolverResult | None:
    """n epreuves independantes de parametre p, exactement k succes."""

    text = _plain(inp.statement)
    words = {"un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5}

    trials: int | None = None
    probability: Fraction | None = None
    successes: int | None = None

    coin = re.search(r"lance (\w+) pieces?", text)
    if coin and coin.group(1) in words and "pile" in text:
        trials = words[coin.group(1)]
        probability = Fraction(1, 2)
        exact = re.search(r"p\s*\(\s*x\s*=\s*(\d+)", text)
        if exact is None:
            return None
        successes = int(exact.group(1))
    else:
        repeat = re.search(r"repete (\w+) fois", text)
        if repeat is None or repeat.group(1) not in words:
            return None
        if "independant" not in text:
            return None
        trials = words[repeat.group(1)]
        fractions = re.findall(r"\\frac\{(\d+)\}\{(\d+)\}", inp.statement)
        if len(fractions) != 1:
            return None
        probability = Fraction(int(fractions[0][0]), int(fractions[0][1]))
        # Ancre sur l'evenement demande : "dont le succes a probabilite" precede
        # l'enonce et ne doit jamais etre lu comme le nombre de succes.
        asked = re.search(r"obtenir (?:exactement )?(\w+) succes", text)
        if asked is None or asked.group(1) not in words:
            return None
        successes = words[asked.group(1)]

    if trials is None or probability is None or successes is None:
        return None
    if not 0 <= successes <= trials:
        return None

    from math import comb

    expected = (
        comb(trials, successes)
        * probability**successes
        * (1 - probability) ** (trials - successes)
    )
    return _resolved(
        "INDEPENDENT_BERNOULLI_REPETITION",
        inp.options,
        Fraction(expected),
        f"Schema de Bernoulli : C({trials},{successes}) * p^{successes} * "
        f"(1-p)^{trials - successes} avec p = {probability}.",
    )


def _uniform_expectation(inp: SolverInput) -> SolverResult | None:
    """Esperance d'une loi uniforme sur 1..s."""

    text = _plain(inp.statement)
    if "de equilibre" not in text or "esperance" not in text:
        return None
    faces = 6
    expected = Fraction(sum(range(1, faces + 1)), faces)
    return _resolved(
        "UNIFORM_DISCRETE_EXPECTATION",
        inp.options,
        expected,
        f"Loi uniforme sur 1..{faces} : E(X) = (1+...+{faces})/{faces}.",
    )


def _standard_deviation_from_variance(inp: SolverInput) -> SolverResult | None:
    """sigma = racine carree de la variance."""

    text = _math_text(inp.statement)
    if not re.search(r"v\s*\(\s*x\s*\)", text) or "sigma" not in inp.statement:
        return None
    if re.search(r"e\s*\(\s*x\s*\)", text):
        return None
    match = re.search(
        r"v\s*\(\s*x\s*\)\s*=\s*(-?\d+(?:\{,\}\d+)?)", inp.statement, re.I
    )
    if match is None:
        return None
    variance = evaluate(match.group(1))
    if variance < 0:
        return None
    root = Fraction(variance) ** Fraction(1, 2)
    exact = Fraction(root) if float(root).is_integer() else None
    if exact is None:
        import math

        value = math.isqrt(variance.numerator) if variance.denominator == 1 else None
        if value is None or value * value != variance.numerator:
            return None
        exact = Fraction(value)
    return _resolved(
        "STANDARD_DEVIATION_FROM_VARIANCE",
        inp.options,
        exact,
        f"sigma(X) = sqrt(V(X)) = sqrt({variance}) = {exact}.",
    )


def _koenig_huygens(inp: SolverInput) -> SolverResult | None:
    """E(X^2) = V(X) + E(X)^2."""

    if "E(X^2)" not in inp.statement.replace(" ", ""):
        return None
    mean = re.search(r"E\s*\(\s*X\s*\)\s*=\s*(-?\d+(?:\{,\}\d+)?)", inp.statement)
    variance = re.search(r"V\s*\(\s*X\s*\)\s*=\s*(-?\d+(?:\{,\}\d+)?)", inp.statement)
    if mean is None or variance is None:
        return None
    expectation = evaluate(mean.group(1))
    var = evaluate(variance.group(1))
    expected = var + expectation**2
    return _resolved(
        "KOENIG_HUYGENS_SECOND_MOMENT",
        inp.options,
        expected,
        f"Koenig-Huygens : E(X^2) = V(X) + E(X)^2 = {var} + {expectation}^2.",
    )


def _binary_tree_paths(inp: SolverInput) -> SolverResult | None:
    """Arbre a deux issues repete n fois : 2^n chemins terminaux."""

    text = _plain(inp.statement)
    if "chemins terminaux" not in text or "deux issues" not in text:
        return None
    words = {"une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5}
    repeat = re.search(r"repete (\w+) fois", text)
    if repeat is None or repeat.group(1) not in words:
        return None
    trials = words[repeat.group(1)]
    return _resolved(
        "BINARY_TREE_TERMINAL_PATHS",
        inp.options,
        Fraction(2**trials),
        f"Deux issues repetees {trials} fois : 2^{trials} chemins terminaux.",
    )


def _linear_expectation(inp: SolverInput) -> SolverResult | None:
    """Linearite : Y = aX + b implique E(Y) = a E(X) + b."""

    compact = inp.statement.replace(" ", "")
    mean = re.search(r"E\(X\)=(-?\d+(?:\{,\}\d+)?)", compact)
    affine = re.search(r"Y=(-?\d*)X([+-]\d+(?:\{,\}\d+)?)", compact)
    if mean is None or affine is None:
        return None
    if "E(Y)" not in compact:
        return None
    slope_text = affine.group(1)
    slope = Fraction(-1) if slope_text == "-" else (
        Fraction(1) if slope_text in ("", "+") else evaluate(slope_text)
    )
    intercept = evaluate(affine.group(2))
    expectation = evaluate(mean.group(1))
    expected = slope * expectation + intercept
    return _resolved(
        "LINEAR_EXPECTATION",
        inp.options,
        expected,
        f"Linearite de l'esperance : E(aX+b) = a E(X) + b = "
        f"{slope}*{expectation} + {intercept}.",
    )


def _algebraic_gain(inp: SolverInput) -> SolverResult | None:
    """Gain algebrique = ce que l'on recoit moins ce que l'on paie."""

    text = _plain(inp.statement)
    if "gain algebrique" not in text:
        return None
    paid = re.search(r"paie (\d+(?:\{,\}\d+)?)", inp.statement)
    received = re.search(r"recoit (\d+(?:\{,\}\d+)?)", _plain(inp.statement))
    if paid is None or received is None:
        return None
    expected = evaluate(received.group(1)) - evaluate(paid.group(1))
    return _resolved(
        "ALGEBRAIC_GAIN",
        inp.options,
        expected,
        f"Gain algebrique = recu - mise = {received.group(1)} - {paid.group(1)}.",
    )


def _insurance_expected_profit(inp: SolverInput) -> SolverResult | None:
    """Benefice moyen d'un contrat : prime - sinistre * probabilite."""

    text = _math_text(inp.statement)
    if "benefice moyen" not in text or "prime" not in text:
        return None
    premium = re.search(r"prime\s*c?\s*=\s*(\d+)", text)
    loss = re.search(r"sinistre\s*(\d+)", text)
    probability = re.search(r"probabilite\s*(\d+)\s*/\s*(\d+)", text)
    if premium is None or loss is None or probability is None:
        return None
    expected = Fraction(int(premium.group(1))) - Fraction(int(loss.group(1))) * Fraction(
        int(probability.group(1)), int(probability.group(2))
    )
    return _resolved(
        "EXPECTED_PROFIT_OF_A_CONTRACT",
        inp.options,
        expected,
        f"Benefice moyen = prime - sinistre * p = {premium.group(1)} - "
        f"{loss.group(1)} * {probability.group(1)}/{probability.group(2)}.",
    )


def _expectation_sign_interpretation(inp: SolverInput) -> SolverResult | None:
    """Regle generique : le signe de E(G) qualifie un jeu.

    E(G) < 0 defavorable au joueur, E(G) = 0 equitable, E(G) > 0 favorable.
    La regle ne depend d'aucun enonce particulier : elle se lit sur le signe.
    """

    text = _math_text(inp.statement)
    if "gain moyen" not in text and "esperance de gain" not in text:
        return None
    match = re.search(
        r"e\s*\(\s*g\s*\)\s*=\s*(-?\d+(?:\{,\}\d+)?)", inp.statement, re.I
    )
    if match is None:
        return None
    expectation = evaluate(match.group(1))
    if expectation < 0:
        verdict = "defavorable"
    elif expectation > 0:
        verdict = "favorable"
    else:
        verdict = "equitable"

    truths: dict[str, bool] = {}
    for letter, raw in inp.options.items():
        label = _plain(raw)
        if "defavorable" in label:
            truths[letter] = verdict == "defavorable"
        elif "favorable" in label:
            truths[letter] = verdict == "favorable"
        elif "equitable" in label:
            truths[letter] = verdict == "equitable"
        elif "determiner" in label or "impossible" in label:
            # Le signe de E(G) est donne : la question est decidable.
            truths[letter] = False
        else:
            return None
    return SolverResult(
        status="MACHINE_RESOLVED",
        family="EXPECTATION_SIGN_INTERPRETATION",
        option_truths=truths,
        computed_value=verdict,
        independent_evidence=(
            f"E(G) = {expectation} ; le signe de l'esperance de gain qualifie le "
            f"jeu : negatif defavorable, nul equitable, positif favorable."
        ),
    )


def _sample_mean_fluctuation_scale(inp: SolverInput) -> SolverResult | None:
    """Echelle de fluctuation de la moyenne empirique : 2 sigma / racine(n)."""

    compact = inp.statement.replace(" ", "")
    if "2\\sigma" not in compact or "\\sqrt{n}" not in compact:
        return None
    sigma = re.search(r"\\sigma=(-?\d+(?:\{,\}\d+)?)", compact)
    size = re.search(r"n=(\d+)", compact)
    if sigma is None or size is None:
        return None
    import math

    root = math.isqrt(int(size.group(1)))
    if root * root != int(size.group(1)):
        return None
    expected = 2 * evaluate(sigma.group(1)) / root
    return _resolved(
        "SAMPLE_MEAN_FLUCTUATION_SCALE",
        inp.options,
        expected,
        f"2*sigma/sqrt(n) = 2*{sigma.group(1)}/sqrt({size.group(1)}).",
    )


def _sample_mean_fluctuation_monotonicity(inp: SolverInput) -> SolverResult | None:
    """sigma/sqrt(n) est strictement decroissante en n : identite generique."""

    text = _plain(inp.statement)
    if "ecart typique" not in text or "de plus en plus grande" not in text:
        return None
    if "moyenne" not in text:
        return None
    import math

    sigma = Fraction(1)
    scale = [sigma / Fraction(math.isqrt(n * n)) for n in (10, 100, 1000)]
    if not (scale[0] > scale[1] > scale[2]):  # pragma: no cover - identite
        return None
    truths: dict[str, bool] = {}
    for letter, raw in inp.options.items():
        label = _plain(raw)
        if "diminue" in label or "decroit" in label:
            truths[letter] = True
        elif "augmente" in label or "croit" in label or "reste constant" in label:
            truths[letter] = False
        elif "nul" in label:
            truths[letter] = False
        else:
            return None
    return SolverResult(
        status="MACHINE_RESOLVED",
        family="SAMPLE_MEAN_FLUCTUATION_MONOTONICITY",
        option_truths=truths,
        computed_value="decroissante",
        independent_evidence=(
            "L'ecart typique de la moyenne empirique vaut sigma/sqrt(n) ; cette "
            "quantite est strictement decroissante en n et ne s'annule pour "
            "aucun n fini."
        ),
    )


def _two_sigma_coverage(inp: SolverInput) -> SolverResult | None:
    """Proportion d'echantillons dans l'intervalle a deux ecarts types."""

    compact = inp.statement.replace(" ", "")
    text = _plain(inp.statement)
    if "2\\sigma" not in compact or "\\sqrt{n}" not in compact:
        return None
    if "proportion" not in text:
        return None
    expected = Fraction(95, 100)
    truths: dict[str, bool] = {}
    for letter, raw in inp.options.items():
        percent = re.search(r"(\d+)\s*\\?,?\\?%", raw)
        if percent is None:
            return None
        truths[letter] = Fraction(int(percent.group(1)), 100) == expected
    return SolverResult(
        status="MACHINE_RESOLVED",
        family="TWO_SIGMA_COVERAGE_PROPORTION",
        option_truths=truths,
        computed_value="95/100",
        independent_evidence=(
            "L'intervalle de fluctuation a deux ecarts types de la moyenne "
            "empirique couvre environ 95 % des echantillons."
        ),
    )


def _inverse_transform_sampling(inp: SolverInput) -> SolverResult | None:
    """Partition cumulative de [0;1[ : u tombe dans le palier de sa valeur."""

    text = inp.statement
    if "0\\,;1" not in text.replace(" ", "") and "[0" not in text:
        return None
    pairs = re.findall(
        r"P\(X\s*=\s*(-?\d+(?:\{,\}\d+)?)\)\s*=\s*(\d+\{,\}\d+|\d+)", text
    )
    draw = re.search(r"u\s*=\s*(\d+\{,\}\d+|\d+)", text)
    if len(pairs) < 2 or draw is None:
        return None
    uniform = evaluate(draw.group(1))
    cumulative = Fraction(0)
    chosen: Fraction | None = None
    for value_text, mass_text in pairs:
        mass = evaluate(mass_text)
        upper = cumulative + mass
        if cumulative <= uniform < upper:
            chosen = evaluate(value_text)
            break
        cumulative = upper
    if chosen is None:
        return None
    return _resolved(
        "INVERSE_TRANSFORM_SAMPLING",
        inp.options,
        chosen,
        f"Partition cumulative de [0;1[ dans l'ordre donne : u = {uniform} tombe "
        f"dans le palier de la valeur {chosen}.",
    )


def _sample_mean_definition(inp: SolverInput) -> SolverResult | None:
    """Identite : moyenne d'un echantillon = somme / taille."""

    text = _plain(inp.statement)
    if "moyenne" not in text or "somme" not in text:
        return None
    if "taille" not in text:
        return None
    truths: dict[str, bool] = {}
    for letter, raw in inp.options.items():
        code = _plain(raw).replace("\\code{", "").replace("}", "")
        expression = code.replace("return", "").strip()
        normalised = expression.replace(" ", "")
        if normalised == "somme/n":
            truths[letter] = True
        elif normalised in {"somme", "n/somme"} or normalised.startswith("somme/len"):
            truths[letter] = False
        else:
            return None
    return SolverResult(
        status="MACHINE_RESOLVED",
        family="SAMPLE_MEAN_DEFINITION",
        option_truths=truths,
        computed_value="somme/n",
        independent_evidence=(
            "La moyenne d'un echantillon de taille n est le quotient de la somme "
            "de ses termes par n."
        ),
    )


def _polynomial_local_extrema(inp: SolverInput) -> SolverResult | None:
    """Extrema locaux d'un polynome, par la derivee et ses changements de signe."""

    text = _plain(inp.statement)
    if "extrema locaux" not in text and "extremum local" not in text:
        return None
    match = re.search(r"f\s*\(\s*x\s*\)\s*=\s*([^$]+)\$", inp.statement)
    if match is None:
        return None
    try:
        import sympy
    except ImportError:  # pragma: no cover - dependance declaree
        return None
    x = sympy.Symbol("x", real=True)
    expression = match.group(1).replace("^", "**").strip()
    from sympy.parsing.sympy_parser import (  # noqa: PLC0415
        implicit_multiplication_application,
        parse_expr,
        standard_transformations,
    )

    transformations = standard_transformations + (
        implicit_multiplication_application,
    )
    try:
        polynomial = parse_expr(
            expression, local_dict={"x": x}, transformations=transformations
        )
    except (sympy.SympifyError, TypeError, SyntaxError, ValueError):
        return None
    derivative = sympy.diff(polynomial, x)
    second = sympy.diff(derivative, x)
    try:
        roots = sorted(
            root for root in sympy.solve(sympy.Eq(derivative, 0), x) if root.is_real
        )
    except (NotImplementedError, TypeError):
        return None
    maxima = {sympy.nsimplify(r) for r in roots if second.subs(x, r) < 0}
    minima = {sympy.nsimplify(r) for r in roots if second.subs(x, r) > 0}
    if not maxima and not minima:
        return None

    def _claim(raw: str) -> tuple[set, set] | None:
        label = _plain(raw)
        if "aucun extremum" in label:
            return (set(), set())
        claimed_max: set = set()
        claimed_min: set = set()
        for kind, value in re.findall(
            r"(maximum|minimum) local en \$?x\s*=\s*(-?\d+)", label
        ):
            target = claimed_max if kind == "maximum" else claimed_min
            target.add(sympy.nsimplify(int(value)))
        if not claimed_max and not claimed_min:
            return None
        return (claimed_max, claimed_min)

    truths: dict[str, bool] = {}
    for letter, raw in inp.options.items():
        claim = _claim(raw)
        if claim is None:
            return None
        claimed_max, claimed_min = claim
        if not claimed_max and not claimed_min:
            truths[letter] = not maxima and not minima
            continue
        truths[letter] = claimed_max == maxima and claimed_min == minima
    return SolverResult(
        status="MACHINE_RESOLVED",
        family="POLYNOMIAL_LOCAL_EXTREMA",
        option_truths=truths,
        computed_value=(
            f"maxima={sorted(map(str, maxima))} minima={sorted(map(str, minima))}"
        ),
        independent_evidence=(
            f"f'(x) = {sympy.srepr(derivative) if False else derivative} ; points "
            f"critiques {sorted(map(str, roots))} ; le signe de f'' y donne "
            f"maxima {sorted(map(str, maxima))} et minima {sorted(map(str, minima))}."
        ),
    )


#: Familles generiques, dans l'ordre d'essai. Aucune n'est liee a une question.
FAMILIES: tuple[Callable[[SolverInput], SolverResult | None], ...] = (
    _distribution_total_mass,
    _koenig_huygens,
    _standard_deviation_from_variance,
    _linear_expectation,
    _uniform_expectation,
    _uniform_outcome_probability,
    _bernoulli_repetition,
    _binary_tree_paths,
    _algebraic_gain,
    _insurance_expected_profit,
    _expectation_sign_interpretation,
    _sample_mean_fluctuation_scale,
    _sample_mean_fluctuation_monotonicity,
    _two_sigma_coverage,
    _inverse_transform_sampling,
    _sample_mean_definition,
    _polynomial_local_extrema,
)


def solve(inp: SolverInput) -> SolverResult:
    """Resout la question sans jamais avoir vu la reponse declaree."""

    for family in FAMILIES:
        try:
            result = family(inp)
        except (UnsupportedExpression, ValueError, ZeroDivisionError):
            result = None
        if result is not None:
            return result
    return SolverResult(
        status="NOT_MACHINE_RESOLVABLE",
        family=None,
        reason=(
            "aucune famille mathematique generique ne modelise cet enonce sans "
            "ecrire une derivation propre a la question"
        ),
    )
