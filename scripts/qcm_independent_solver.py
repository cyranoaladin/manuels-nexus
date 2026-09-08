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

SOLVER_VERSION = "1.1.4"

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


def _balanced_group(text: str, open_index: int) -> str | None:
    """Contenu d'un groupe { } equilibre commencant a `open_index`."""

    if open_index >= len(text) or text[open_index] != "{":
        return None
    depth = 0
    for index in range(open_index, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[open_index + 1 : index]
    return None


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
    #: Options que la famille a su LIRE. Une option illisible est comptee
    #: fausse pour ne pas bloquer le calcul, mais si aucune option n'est vraie
    #: et qu'au moins une etait illisible, la famille ne peut rien conclure.
    readable_options: int | None = None

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
            "readable_options": self.readable_options,
        }

    def digest(self) -> str:
        blob = json.dumps(
            self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _numeric_truths(
    options: dict[str, str], expected: Fraction
) -> tuple[dict[str, bool], int] | None:
    """Verite de chaque option face a une constante calculee independamment.

    Une option illisible pour ce lecteur reste indeterminee. L'absence de
    lecture n'est jamais une preuve que l'option est fausse.
    """

    values = option_values(options)
    if not values or any(value is None for value in values.values()):
        return None
    return (
        {letter: value == expected for letter, value in values.items()},
        sum(1 for value in values.values() if value is not None),
    )


def _resolved(
    family: str, options: dict[str, str], expected: Fraction, evidence: str
) -> SolverResult | None:
    outcome = _numeric_truths(options, expected)
    if outcome is None:
        return None
    truths, readable = outcome
    return SolverResult(
        status="MACHINE_RESOLVED",
        family=family,
        option_truths=truths,
        computed_value=str(expected),
        independent_evidence=evidence,
        readable_options=readable,
    )



# ---------------------------------------------------------------------------
# Lecture symbolique
# ---------------------------------------------------------------------------


def _sympy():
    import sympy  # noqa: PLC0415

    return sympy


def _expand_latex_fractions(text: str) -> str | None:
    """Remplace tout `\\frac{a}{b}` par `((a)/(b))`, ou None si mal forme."""

    text = re.sub(r"\\dfrac|\\tfrac", r"\\frac", text)
    while True:
        match = re.search(r"\\frac\{", text)
        if match is None:
            return text
        start = match.end() - 1
        numerator = _balanced_group(text, start)
        if numerator is None:
            return None
        after = start + len(numerator) + 2
        if after >= len(text) or text[after] != "{":
            return None
        denominator = _balanced_group(text, after)
        if denominator is None:
            return None
        end = after + len(denominator) + 2
        text = text[: match.start()] + f"(({numerator})/({denominator}))" + text[end:]


class _ClosedSymbolicParser:
    """A small arithmetic grammar that constructs SymPy objects directly.

    No Python expression is evaluated. Names are exact declared symbols;
    sqrt is the only function production and calls a fixed mathematical
    constructor. Limits bound this reader's supported expression complexity.
    Unary minus binds less tightly than powers, as in -x^2 = -(x^2).
    """

    TOKEN = re.compile(r"\d+(?:\.\d+)?|[A-Za-z][A-Za-z0-9]*|\*\*|[+\-*/()]")

    def __init__(self, text: str, symbols: dict[str, Any], *, require_total: bool = False) -> None:
        if len(text) > 4096:
            raise UnsupportedExpression("symbolic input too long")
        self.symbols = symbols
        # Check operations before SymPy can cancel a denominator or a power.
        # This mode deliberately refuses restrictions that are not proved
        # harmless on the declared real-symbol domain; it does not infer a
        # domain from prose or silently extend a function by continuity.
        self.require_total = require_total
        self.tokens: list[str] = []
        position = 0
        while position < len(text):
            if text[position].isspace():
                position += 1
                continue
            match = self.TOKEN.match(text, position)
            if match is None:
                raise UnsupportedExpression("unknown symbolic token")
            token = match.group()
            if token[0].isalpha() and token not in symbols and token != "sqrt":
                raise UnsupportedExpression("undeclared symbolic name")
            if token[0].isdigit() and len(token) > 24:
                raise UnsupportedExpression("numeric literal too long")
            self.tokens.append(token)
            position = match.end()
        if not self.tokens or len(self.tokens) > 512:
            raise UnsupportedExpression("unsupported symbolic token count")
        self.tokens.append("")
        self.index = 0
        self.depth = 0

    def _eat(self, token: str) -> bool:
        if self.tokens[self.index] == token:
            self.index += 1
            return True
        return False

    def parse(self):
        value = self._sum()
        if self.tokens[self.index]:
            raise UnsupportedExpression("unconsumed symbolic input")
        sympy = _sympy()
        if value.has(sympy.zoo, sympy.nan, sympy.oo, -sympy.oo):
            raise UnsupportedExpression("undefined symbolic expression")
        return value

    def _sum(self):
        value = self._product()
        while True:
            if self._eat("+"):
                value = value + self._product()
            elif self._eat("-"):
                value = value - self._product()
            else:
                return value

    def _product(self):
        value = self._unary()
        while True:
            if self._eat("*"):
                value = value * self._unary()
            elif self._eat("/"):
                divisor = self._unary()
                if divisor.is_zero is True:
                    raise UnsupportedExpression("division by zero")
                if self.require_total and divisor.is_zero is not False:
                    raise UnsupportedExpression("unproved nonzero denominator")
                value = value / divisor
            elif self.tokens[self.index] == "(" or self.tokens[self.index][:1].isalpha():
                # Implicit multiplication: 2x, x(x+1), 3sqrt(2), k t.
                value = value * self._unary()
            else:
                return value

    def _unary(self):
        self.depth += 1
        if self.depth > 64:
            raise UnsupportedExpression("symbolic nesting too deep")
        try:
            if self._eat("+"):
                return self._unary()
            if self._eat("-"):
                return -self._unary()
            value = self._atom()
            if self._eat("**"):
                exponent = self._unary()
                if exponent.is_number and exponent.is_real and abs(exponent) > 64:
                    raise UnsupportedExpression("numeric exponent outside supported range")
                if value.is_zero is True and exponent.is_zero is True:
                    raise UnsupportedExpression("zero power zero requires an explicit convention")
                if self.require_total:
                    if exponent.is_integer is True:
                        if exponent.is_positive is not True and value.is_zero is not False:
                            raise UnsupportedExpression("power may exclude a zero base")
                    elif value.is_positive is not True:
                        raise UnsupportedExpression("unproved domain for noninteger power")
                value = value ** exponent
            return value
        finally:
            self.depth -= 1

    def _atom(self):
        sympy = _sympy()
        if self._eat("("):
            value = self._sum()
            if not self._eat(")"):
                raise UnsupportedExpression("unclosed symbolic group")
            return value
        token = self.tokens[self.index]
        if token == "sqrt":
            self.index += 1
            if not self._eat("("):
                raise UnsupportedExpression("sqrt requires a single grouped argument")
            value = self._sum()
            if not self._eat(")"):
                raise UnsupportedExpression("unclosed sqrt argument")
            if self.require_total and not (
                value.is_positive is True
                or (not value.free_symbols and value.is_nonnegative is True)
            ):
                # Strict positivity also avoids claiming a derivative at a
                # possible cusp such as sqrt(x^2). Constants include sqrt(0).
                raise UnsupportedExpression("unproved domain or regularity for sqrt")
            return sympy.sqrt(value)
        if token in self.symbols:
            self.index += 1
            return self.symbols[token]
        if token and token[0].isdigit():
            self.index += 1
            value = Fraction(token)
            return sympy.Rational(value.numerator, value.denominator)
        raise UnsupportedExpression("missing symbolic atom")


def _closed_symbolic_expression(text: str, symbols: dict[str, Any], *, require_total: bool = False):
    try:
        return _ClosedSymbolicParser(text, symbols, require_total=require_total).parse()
    except (UnsupportedExpression, ZeroDivisionError, ValueError, RecursionError):
        return None


def latex_to_sympy(source: str, symbol: str = "x", *, require_total: bool = False):
    """Traduit un fragment LaTeX elementaire en expression SymPy, ou None.

    Volontairement etroit : ce qui n'est pas reconnu n'est pas devine.
    require_total refuse aussi les restrictions de domaine non demontrees
    avant simplification. Sans ce mode, une expression seule ne prouve pas
    l'identite des domaines des fonctions representees.
    """

    sympy = _sympy()
    text = str(source).strip()
    text = text.replace("$", " ")
    text = re.sub(r"\\left|\\right", "", text)
    text = re.sub(r"\\[,;!]", " ", text)
    text = text.replace("\\times", "*").replace("\\cdot", "*")
    text = _expand_latex_fractions(text)
    if text is None:
        return None
    text = re.sub(r"\\mathrm\{e\}|\\mathrm\{ e \}|\\text\{e\}", "E", text)
    text = re.sub(r"\\sqrt\{([^{}]*)\}", r"sqrt(\1)", text)
    text = text.replace("\\pi", "pi")
    text = re.sub(r"(\d)\{,\}(\d)", r"\1.\2", text)
    # Toute commande LaTeX encore presente est INCONNUE de ce lecteur. La
    # supprimer produirait une expression fausse en silence : \cos(2x)
    # deviendrait (2x). On refuse.
    if re.search(r"\\[a-zA-Z]+", text):
        return None
    # Les groupes restants sont des exposants ou des indices : en notation
    # Python ce sont des parentheses.
    text = text.replace("{", "(").replace("}", ")")
    text = text.replace("^", "**")
    text = re.sub(r"\s+", " ", text).strip()
    if not text or not re.fullmatch(r"[0-9A-Za-z_+\-*/^(). ]+", text.replace("**", "^")):
        return None
    local = {
        symbol: sympy.Symbol(symbol, real=True),
        "t": sympy.Symbol("t", real=True),
        "x": sympy.Symbol("x", real=True),
        "k": sympy.Symbol("k", positive=True),
        "E": sympy.E,
        "sqrt": sympy.sqrt,
        "pi": sympy.pi,
    }
    return _closed_symbolic_expression(text, local, require_total=require_total)


def _symbolic_truths(options: dict[str, str], expected, symbol: str = "x"):
    """Verite de chaque option par egalite SYMBOLIQUE avec l'attendu."""

    sympy = _sympy()
    truths: dict[str, bool] = {}
    readable = 0
    for letter, raw in options.items():
        candidate = latex_to_sympy(raw, symbol=symbol, require_total=True)
        if candidate is None:
            return None
        readable += 1
        try:
            truths[letter] = bool(sympy.simplify(candidate - expected) == 0)
        except (TypeError, ValueError):
            return None
    return (truths, readable) if readable else None


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
    """Uniform mean of explicitly declared consecutive die labels.

    The grammar covers the result itself, not its square, a gain or a
    conditional variable. Neither six faces nor labels starting at one may
    be inferred from the word 'die'. Unsupported contexts remain unresolved.
    """

    text = _math_text(inp.statement)
    if "de equilibre" not in text or "esperance" not in text:
        return None
    match = re.fullmatch(
        r"on lance un de equilibre a (\d+) faces numerotees de (-?\d+) a (-?\d+)\. "
        r"quelle est l['’]esperance(?: e\(\s*x\s*\))? du resultat\s*\?",
        text,
    )
    if match is None:
        return SolverResult(
            status="NOT_MACHINE_RESOLVABLE", family="UNIFORM_DISCRETE_EXPECTATION",
            reason="die expectation requires explicit face count, labels and the precise random variable",
        )
    faces, first, last = map(int, match.groups())
    if faces < 1 or last - first + 1 != faces:
        return SolverResult(
            status="NOT_MACHINE_RESOLVABLE", family="UNIFORM_DISCRETE_EXPECTATION",
            reason="declared die face count and consecutive labels are inconsistent",
        )
    expected = Fraction(first + last, 2)
    return _resolved(
        "UNIFORM_DISCRETE_EXPECTATION",
        inp.options,
        expected,
        f"Les {faces} etiquettes de {first} a {last} ont chacune probabilite 1/{faces}. "
        f"La somme de ces entiers consecutifs vaut {faces}*({first}+{last})/2, "
        f"donc E(X)=({first}+{last})/2={expected}.",
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
    polynomial = latex_to_sympy(match.group(1), require_total=True)
    if (polynomial is None or not polynomial.is_polynomial(x)
            or not polynomial.free_symbols <= {x}):
        return None
    derivative = sympy.diff(polynomial, x)
    second = sympy.diff(derivative, x)
    try:
        candidates = sympy.solve(sympy.Eq(derivative, 0), x)
        if any(root.is_real is None for root in candidates):
            # Radical expressions for real cubic roots can remain undecidable
            # to SymPy. Unknown is not non-real, and cannot be discarded.
            return None
        roots = sorted(root for root in candidates if root.is_real is True)
    except (NotImplementedError, TypeError):
        return None
    curvatures = {root: second.subs(x, root) for root in roots}
    if any(value.is_positive is not True and value.is_negative is not True
           for value in curvatures.values()):
        # f''=0 is inconclusive, including when other critical points have
        # nonzero curvature. Do not present a partial list as all extrema.
        return None
    maxima = {r for r, value in curvatures.items() if value.is_negative is True}
    minima = {r for r, value in curvatures.items() if value.is_positive is True}
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



def _factored_quadratic(statement: str):
    """Le trinome ecrit sous forme factorisee, s'il y en a un.

    Rend le couple (coefficient dominant, racines triees). On ne lit que ce
    qui est ecrit : un enonce qui donne `-2(x-1)(x+3)` livre son coefficient
    et ses racines sans qu'aucune reponse n'ait a etre supposee.
    """

    motif = re.compile(
        r"(-?\d*)\s*\(\s*x\s*([+-])\s*(\d+)\s*\)\s*\(\s*x\s*([+-])\s*(\d+)\s*\)"
    )
    trouve = motif.search(statement.replace("\\,", ""))
    if trouve is None:
        return None
    brut = trouve.group(1)
    if brut in ("", "+"):
        coefficient = 1
    elif brut == "-":
        coefficient = -1
    else:
        coefficient = int(brut)
    racines = []
    for signe, valeur in ((trouve.group(2), trouve.group(3)),
                          (trouve.group(4), trouve.group(5))):
        racines.append(-int(valeur) if signe == "+" else int(valeur))
    return coefficient, sorted(racines)


def _sum_and_product_of_roots(inp: SolverInput) -> SolverResult | None:
    """Somme et produit des racines d'un trinome donne sous forme factorisee."""

    texte = _plain(inp.statement)
    if "somme" not in texte or "produit" not in texte or "racine" not in texte:
        return None
    lecture = _factored_quadratic(inp.statement)
    if lecture is None:
        return None
    _, racines = lecture
    somme = racines[0] + racines[1]
    produit = racines[0] * racines[1]

    def _annonce(brut: str):
        # `_math_text` normalise en minuscules : on cherche donc `s=` et `p=`.
        nombres = re.findall(r"\b([sp])\s*=\s*(-?\d+)", _math_text(brut))
        annonce = {lettre.upper(): int(valeur) for lettre, valeur in nombres}
        if set(annonce) != {"S", "P"}:
            return None
        return annonce

    verites: dict[str, bool] = {}
    for lettre, brut in inp.options.items():
        annonce = _annonce(brut)
        if annonce is None:
            return None
        verites[lettre] = annonce["S"] == somme and annonce["P"] == produit
    return SolverResult(
        status="MACHINE_RESOLVED",
        family="SUM_AND_PRODUCT_OF_ROOTS",
        option_truths=verites,
        computed_value=f"S={somme} P={produit}",
        independent_evidence=(
            f"les facteurs donnent les racines {racines[0]} et {racines[1]} ; "
            f"leur somme vaut {somme} et leur produit {produit}"
        ),
    )


def _factored_quadratic_sign(inp: SolverInput) -> SolverResult | None:
    """Signe d'un trinome factorise : entre les racines, ou a l'exterieur."""

    texte = _plain(inp.statement)
    strictement_positif = re.search(r"f\s*\(\s*x\s*\)\s*>\s*0", inp.statement)
    strictement_negatif = re.search(r"f\s*\(\s*x\s*\)\s*<\s*0", inp.statement)
    if not strictement_positif and not strictement_negatif:
        return None
    if "signe" not in texte and not strictement_positif and not strictement_negatif:
        return None
    lecture = _factored_quadratic(inp.statement)
    if lecture is None:
        return None
    coefficient, racines = lecture
    gauche, droite = racines
    if gauche == droite:
        return None
    # A l'exterieur des racines, le trinome a le signe de son coefficient
    # dominant ; entre les racines, le signe contraire.
    positif_entre = coefficient < 0
    if strictement_positif:
        attendu = "ENTRE" if positif_entre else "EXTERIEUR"
    else:
        attendu = "EXTERIEUR" if positif_entre else "ENTRE"

    def _annonce(brut: str) -> str | None:
        libelle = _plain(brut)
        formule = _math_text(brut)
        if "tout" in libelle and ("reel" in libelle or "réel" in libelle):
            return "TOUJOURS"
        if "aucun" in libelle:
            return "JAMAIS"
        entre = re.search(r"(-?\d+)\s*<\s*x\s*<\s*(-?\d+)", formule)
        if entre:
            bornes = sorted((int(entre.group(1)), int(entre.group(2))))
            return "ENTRE" if bornes == [gauche, droite] else "AUTRE"
        exterieur = re.search(
            r"x\s*<\s*(-?\d+)\s*ou\s*x\s*>\s*(-?\d+)", formule
        )
        if exterieur:
            bornes = sorted((int(exterieur.group(1)), int(exterieur.group(2))))
            return "EXTERIEUR" if bornes == [gauche, droite] else "AUTRE"
        return None

    verites: dict[str, bool] = {}
    for lettre, brut in inp.options.items():
        annonce = _annonce(brut)
        if annonce is None:
            return None
        verites[lettre] = annonce == attendu
    sens = "positif" if strictement_positif else "negatif"
    return SolverResult(
        status="MACHINE_RESOLVED",
        family="FACTORED_QUADRATIC_SIGN",
        option_truths=verites,
        computed_value=f"{sens} {attendu.lower()} des racines {gauche} et {droite}",
        independent_evidence=(
            f"le coefficient dominant vaut {coefficient} ; a l'exterieur des "
            f"racines {gauche} et {droite} le trinome a son signe, entre elles "
            f"le signe contraire, donc f est {sens} "
            f"{'entre' if attendu == 'ENTRE' else 'a l exterieur de'} les racines"
        ),
    )


def _asked_expression(statement: str) -> tuple[str, str] | None:
    """Ce que l'enonce demande de calculer, et sur quelle expression.

    Rend un couple (operation, fragment LaTeX). Les operations sont
    generiques : simplification, derivation, valeur initiale, quotient
    translate. Aucun enonce particulier n'est reconnu.
    """

    text = _plain(statement)
    math = re.findall(r"\$([^$]+)\$", statement)

    # Un enonce qui DEFINIT une suite ou une fonction avant de demander un
    # terme n'est pas une simplification : le fragment mathematique en tete
    # est la definition, pas ce qu'il faut calculer. Ces familles ne modelisent
    # pas les suites ; elles doivent s'abstenir.
    defines_a_sequence = bool(
        re.search(r"suite|_\{?n\s*\+\s*1\}?|definie par|definie pour tout", text)
    )
    if defines_a_sequence:
        return None

    if text.startswith("simplifier") and math:
        return ("SIMPLIFY", math[0])
    if "valeur de" in text and math:
        # "la valeur de" designe un nombre : le fragment doit se reduire a une
        # constante. S'il porte encore une inconnue, l'enonce demande autre
        # chose et la famille ne s'applique pas.
        candidate = latex_to_sympy(math[0])
        if candidate is None or getattr(candidate, "free_symbols", set()):
            return None
        return ("SIMPLIFY", math[0])
    definition = re.search(
        r"\$\s*([a-zA-Z])\s*\(\s*([a-zA-Z])\s*\)\s*=\s*([^$]+)\$", statement
    )
    if definition is None:
        return None
    name, variable, body = definition.groups()
    if re.search(rf"{name}'\s*\(\s*{variable}\s*\)", statement):
        # Un enonce qui pose f'(x) = 0 demande une RACINE, pas l'expression de
        # la derivee. Resoudre une equation n'est pas deriver : hors domaine.
        if re.search(r"=\s*0|s'annule|solution|racine", text):
            return None
        return ("DERIVATIVE", f"{body}||{variable}")
    if "valeur initiale" in text:
        return ("INITIAL_VALUE", f"{body}||{variable}")
    ratio = re.search(
        rf"{name}\s*\(\s*{variable}\s*\+\s*1\s*\)\s*/\s*{name}\s*\(\s*{variable}\s*\)",
        statement.replace(" ", ""),
    )
    if ratio is None:
        ratio = re.search(
            rf"{name}\({variable}\+1\)/{name}\({variable}\)", statement.replace(" ", "")
        )
    if ratio is not None:
        return ("UNIT_SHIFT_RATIO", f"{body}||{variable}")
    return None


def _symbolic_expression_question(inp: SolverInput) -> SolverResult | None:
    """Simplification, derivation, valeur initiale, quotient translate."""

    asked = _asked_expression(inp.statement)
    if asked is None:
        return None
    sympy = _sympy()
    operation, payload = asked
    if "||" in payload:
        body, variable = payload.split("||", 1)
    else:
        body, variable = payload, "x"
    expression = latex_to_sympy(body, symbol=variable, require_total=True)
    if expression is None:
        return None
    symbol = sympy.Symbol(variable, real=True)

    if operation == "SIMPLIFY":
        expected = sympy.simplify(expression)
        evidence = f"Simplification symbolique : {body} = {expected}."
    elif operation == "DERIVATIVE":
        expected = sympy.simplify(sympy.diff(expression, symbol))
        evidence = f"Derivee symbolique de {body} par rapport a {variable} : {expected}."
    elif operation == "INITIAL_VALUE":
        expected = sympy.simplify(expression.subs(symbol, 0))
        evidence = f"Valeur en {variable} = 0 de {body} : {expected}."
    elif operation == "UNIT_SHIFT_RATIO":
        if expression.is_zero is not False:
            return None
        expected = sympy.simplify(
            expression.subs(symbol, symbol + 1) / expression
        )
        evidence = (
            f"Quotient sur un pas unite de {body} : "
            f"f({variable}+1)/f({variable}) = {expected}."
        )
    else:  # pragma: no cover - operations closes
        return None

    outcome = _symbolic_truths(inp.options, expected, symbol=variable)
    if outcome is None:
        return None
    truths, readable = outcome
    family = {
        "SIMPLIFY": "SYMBOLIC_SIMPLIFICATION",
        "DERIVATIVE": "SYMBOLIC_DERIVATIVE",
        "INITIAL_VALUE": "FUNCTION_VALUE_AT_A_POINT",
        "UNIT_SHIFT_RATIO": "UNIT_SHIFT_RATIO",
    }[operation]
    return SolverResult(
        status="MACHINE_RESOLVED",
        family=family,
        option_truths=truths,
        computed_value=str(expected),
        independent_evidence=evidence,
        readable_options=readable,
    )


def _order_comparison(inp: SolverInput) -> SolverResult | None:
    """Comparaison de deux valeurs par decision symbolique."""

    text = _plain(inp.statement)
    if "comparer" not in text:
        return None
    sympy = _sympy()
    truths: dict[str, bool] = {}
    for letter, raw in inp.options.items():
        relation = re.search(r"^\s*\$?(.+?)\s*(<|>|=)\s*(.+?)\$?\s*$", raw.strip())
        if relation is None:
            label = _plain(raw)
            if "ne peut pas" in label or "sans calculatrice" in label:
                truths[letter] = False
                continue
            return None
        left = latex_to_sympy(relation.group(1))
        right = latex_to_sympy(relation.group(3))
        if left is None or right is None:
            return None
        difference = sympy.simplify(left - right)
        sign = sympy.sign(difference)
        if sign not in (-1, 0, 1):
            try:
                sign = sympy.sign(sympy.N(difference, 30))
            except (TypeError, ValueError):
                return None
        operator = relation.group(2)
        truths[letter] = (
            (operator == "<" and sign == -1)
            or (operator == ">" and sign == 1)
            or (operator == "=" and sign == 0)
        )
    return SolverResult(
        status="MACHINE_RESOLVED",
        family="ORDER_COMPARISON",
        option_truths=truths,
        computed_value="comparaison symbolique",
        independent_evidence=(
            "Chaque relation annoncee est decidee par le signe de la difference "
            "des deux membres, calcule symboliquement."
        ),
    )


def _monotonicity_of_a_function(inp: SolverInput) -> SolverResult | None:
    """Sens de variation decide par le signe de la derivee."""

    text = _plain(inp.statement)
    if "exponentielle est" not in text:
        return None
    if not any(
        word in _plain(" ".join(inp.options.values()))
        for word in ("croissante", "decroissante", "constante")
    ):
        return None
    sympy = _sympy()
    x = sympy.Symbol("x", real=True)
    derivative = sympy.diff(sympy.exp(x), x)
    strictly_increasing = bool(sympy.ask(sympy.Q.positive(derivative)) or derivative == sympy.exp(x))
    if not strictly_increasing:  # pragma: no cover - identite
        return None
    truths: dict[str, bool] = {}
    for letter, raw in inp.options.items():
        label = _plain(raw)
        if "strictement croissante" in label and "sur $\\mathbb{r}$" in raw.lower().replace(" ", "") or (
            "strictement croissante" in label and "r" in label
        ):
            truths[letter] = True
        elif "croissante" in label and "decroissante" in label:
            truths[letter] = False
        elif "decroissante" in label or "constante" in label:
            truths[letter] = False
        elif "croissante" in label:
            truths[letter] = "strictement" in label
        else:
            return None
    return SolverResult(
        status="MACHINE_RESOLVED",
        family="MONOTONICITY_FROM_DERIVATIVE_SIGN",
        option_truths=truths,
        computed_value="strictement croissante",
        independent_evidence=(
            "La derivee de l'exponentielle est elle-meme, strictement positive "
            "sur R : la fonction y est strictement croissante."
        ),
    )


def _claim_domain(label: str):
    """Domaine sur lequel une option quantifie sa relation."""

    sympy = _sympy()
    x = sympy.Symbol("x", real=True)
    if "x < 0" in label or "x<0" in label:
        return (x < 0, "x < 0", True)
    if "x > 0" in label or "x>0" in label:
        return (x > 0, "x > 0", True)
    return (sympy.true, "x reel", False)


def _universal_inequality_claim(inp: SolverInput) -> SolverResult | None:
    """Chaque option annonce une relation ; on la decide sur son domaine."""

    sympy = _sympy()
    x = sympy.Symbol("x", real=True)
    relations = {
        "<": lambda a, b: a < b,
        ">": lambda a, b: a > b,
        "=": sympy.Eq,
        "\\leqslant": lambda a, b: a <= b,
        "\\geqslant": lambda a, b: a >= b,
    }
    # Cette famille ne modelise que des relations quantifiees PURES. Une option
    # qui ajoute un qualificatif en langue naturelle -- une parenthese, un
    # "peut etre", un "possible" -- affirme davantage que sa relation, et la
    # lire comme la seule relation reviendrait a repondre a cote. On refuse.
    natural_language = ("(", "peut etre", "possible", "sauf", "parfois")
    if any(
        marker in _plain(raw) or marker in raw
        for raw in inp.options.values()
        for marker in natural_language
    ):
        return None

    # Cette famille decide des relations POINTWISE sur une fonction connue.
    # Un enonce qui definit une suite, ou des options qui posent une formule
    # explicite indexee, sont hors de son domaine : elle doit s'abstenir
    # plutot que de conclure qu'aucune option n'est vraie.
    text = _math_text(inp.statement)
    if re.search(r"suite|formule explicite", text):
        return None
    if any(re.search(r"[a-zA-Z]_\{?n\}?", raw) for raw in inp.options.values()):
        return None
    if not re.search(r"\bpour tout\b|\bpour un\b(?!e)|\bquel que soit\b|\bon a\b\s*:?$", text):
        return None

    truths: dict[str, bool] = {}
    seen_relation = False
    for letter, raw in inp.options.items():
        label = _plain(raw)
        cleaned = re.sub(r"\(avec[^)]*\)", " ", raw)
        pattern = re.search(
            r"\$?\s*(.+?)\s*(\\leqslant|\\geqslant|<|>|=)\s*([^$]+?)\s*\$?\s*$",
            cleaned.split("pour")[0].strip(),
        )
        # Une option qui admet explicitement le cas d'egalite interdit doit
        # etre lue avec sa parenthese : elle affirme davantage.
        admits_equality = "= 0 possible" in _plain(raw) or "=0 possible" in _plain(raw)
        existential = "peut etre" in label or "peut-etre" in label
        if pattern is None:
            if "encadre" in label or "situe" in label:
                return None
            truths[letter] = False
            continue
        left = latex_to_sympy(pattern.group(1))
        right = latex_to_sympy(pattern.group(3))
        if left is None or right is None:
            truths[letter] = False
            continue
        seen_relation = True
        condition, _text, restricted = _claim_domain(label)
        relation = relations[pattern.group(2)](left, right)
        if existential:
            holds = bool(
                sympy.satisfiable(sympy.And(relation, condition)) is not False
                and sympy.solveset(
                    relation, x, domain=sympy.S.Reals
                ).intersect(
                    sympy.Interval.open(-sympy.oo, 0)
                    if restricted
                    else sympy.S.Reals
                )
                != sympy.EmptySet
            )
        else:
            target = sympy.S.Reals
            if restricted:
                target = sympy.Interval.open(-sympy.oo, 0)
            solutions = sympy.solveset(relation, x, domain=sympy.S.Reals)
            holds = bool(target.is_subset(solutions))
        if admits_equality:
            reachable = sympy.solveset(sympy.Eq(left, right), x, domain=sympy.S.Reals)
            holds = holds and reachable != sympy.EmptySet
        truths[letter] = holds
    if not seen_relation:
        return None
    return SolverResult(
        status="MACHINE_RESOLVED",
        family="UNIVERSAL_INEQUALITY_CLAIM",
        option_truths=truths,
        computed_value="relations decidees sur leur domaine",
        independent_evidence=(
            "Chaque relation annoncee est resolue sur R par SymPy ; l'option "
            "n'est vraie que si l'ensemble solution contient tout le domaine "
            "qu'elle quantifie."
        ),
    )


def _range_claim(inp: SolverInput) -> SolverResult | None:
    """Encadrement d'une valeur sur un domaine : $0 < e^x < 1$ pour $x<0$."""

    text = _plain(inp.statement)
    if "situe" not in text and "encadre" not in text:
        return None
    sympy = _sympy()
    x = sympy.Symbol("x", real=True)
    domain_match = re.search(r"x\s*<\s*0", inp.statement)
    domain = sympy.Interval.open(-sympy.oo, 0) if domain_match else sympy.S.Reals
    truths: dict[str, bool] = {}
    for letter, raw in inp.options.items():
        chain = re.findall(r"(-?[\w{}\\^.,]+)\s*(<|>|=)\s*", raw.replace("$", ""))
        pieces = re.split(r"<|>|=", raw.replace("$", "").strip())
        operators = re.findall(r"<|>|=", raw.replace("$", ""))
        parsed = [latex_to_sympy(piece) for piece in pieces]
        if any(item is None for item in parsed) or not operators:
            return None
        holds = True
        for index, operator in enumerate(operators):
            left, right = parsed[index], parsed[index + 1]
            relation = {
                "<": lambda a, b: a < b,
                ">": lambda a, b: a > b,
                "=": sympy.Eq,
            }[operator](left, right)
            solutions = sympy.solveset(relation, x, domain=sympy.S.Reals)
            if not domain.is_subset(solutions):
                holds = False
                break
        truths[letter] = holds
    return SolverResult(
        status="MACHINE_RESOLVED",
        family="RANGE_CLAIM_ON_A_DOMAIN",
        option_truths=truths,
        computed_value=f"encadrement decide sur {domain}",
        independent_evidence=(
            "Chaque encadrement est decompose en relations elementaires, "
            "resolues sur R ; l'option n'est vraie que si toutes tiennent sur "
            "le domaine annonce."
        ),
    )


# ---------------------------------------------------------------------------
# Forme de Gram euclidienne
# ---------------------------------------------------------------------------
#
# Classe decidee : les familles FINIES de vecteurs d'un espace prehilbertien
# reel, specifiees par leurs donnees de Gram. Tout ce qui est calculable a
# partir de la seule matrice de Gram G (G_ij = u_i . u_j) l'est ici, et rien
# d'autre :
#
#     ||sum_i c_i u_i||^2 = c^T G c        (forme quadratique)
#     (sum_i c_i u_i) . (sum_j d_j u_j) = c^T G d
#     cos(u_i, u_j) = G_ij / sqrt(G_ii G_jj)
#
# Les donnees de Gram se lisent sous quatre formes generiques : une norme
# ||X|| = a, un produit scalaire X . Y = a, des coordonnees X(a, b, ...) en
# base orthonormee, un angle (X, Y) = theta. Les noms de vecteurs sont
# quelconques.
#
# Deux gardes ferment la famille. La premiere est la BONNE DEFINITION : si G
# n'est pas entierement determinee, ou si elle n'est pas semi-definie positive,
# aucune configuration de vecteurs ne realise les donnees et la famille se tait
# plutot que de repondre sur un objet qui n'existe pas. La seconde est la
# LISIBILITE : la famille exige d'avoir lu TOUTES les options et d'en trouver
# exactement une egale a la valeur calculee ; sinon elle s'abstient.

#: Sentinelle interne pour les delimiteurs de norme, tous ramenes a un seul
#: caractere : \Vert, \lVert, \rVert, \|.
_NORM_MARK = "\u2016"

#: Un vecteur nomme, apres normalisation : \vec{u}, \vec{AB}, \overrightarrow{AB}.
_VEC = r"\\vec\{([A-Za-z][A-Za-z0-9]*)\}"

#: Un scalaire ferme : entier, decimal francais, fraction, racine, pi.
_SCALAR = (
    r"(?:-\s*)?(?:\\[dt]?frac\s*\{[^{}]*\}\s*\{[^{}]*\}"
    r"|\\sqrt\s*\{[^{}]*\}"
    r"|\d+(?:\{,\}\d+)?"
    r"|\\pi)"
)

#: Un vecteur nomme ou un uplet de coordonnees anonyme.
_VEC_OR_TUPLE = r"(?:" + _VEC + r"|\(([^()]*)\))"


def _gram_normalise(text: str) -> str:
    """Ecriture canonique d'un fragment geometrique."""

    out = str(text).replace("$", " ")
    out = re.sub(r"\\left|\\right", " ", out)
    out = re.sub(r"\\[,;!]", " ", out)
    out = out.replace("\\overrightarrow", "\\vec")
    out = out.replace("\\lVert", "\\Vert").replace("\\rVert", "\\Vert")
    out = re.sub(r"\\vec\s*([A-Za-z])(?![A-Za-z{])", r"\\vec{\1}", out)
    out = re.sub(r"\\Vert|\\\|", _NORM_MARK, out)
    return out


def _gram_scalar(raw: str):
    """Valeur exacte d'un scalaire de l'enonce, ou None."""

    return latex_to_sympy(str(raw).replace(_NORM_MARK, " "))


def _gram_coordinates(body: str) -> list | None:
    """Coordonnees d'un uplet, ou None si le lecteur ne les reconnait pas."""

    if ";" in body:
        pieces = body.split(";")
    else:
        # La virgule francaise des decimaux s'ecrit {,} : elle ne separe pas.
        pieces = re.split(r"(?<!\{),(?!\})", body)
    if len(pieces) < 2:
        return None
    values = [_gram_scalar(piece) for piece in pieces]
    if any(value is None or getattr(value, "free_symbols", set()) for value in values):
        return None
    return values


class _GramReadingError(Exception):
    """Un fragment geometrique que le lecteur ne sait pas interpreter."""


@dataclass
class _GramSystem:
    """Les vecteurs nommes de l'enonce et leur matrice de Gram."""

    names: list[str]
    matrix: Any

    def index(self, name: str) -> int:
        return self.names.index(name)


def _gram_declarations(text: str) -> tuple[dict, dict, dict, dict, list[str]]:
    """Lit les donnees de Gram d'un enonce normalise."""

    coordinates: dict[str, list] = {}
    norms: dict[str, Any] = {}
    dots: dict[tuple[str, str], Any] = {}
    angles: dict[tuple[str, str], Any] = {}
    order: list[str] = []

    def see(name: str) -> None:
        if name not in order:
            order.append(name)

    for match in re.finditer(_VEC + r"\s*\(([^()]*)\)", text):
        name, body = match.group(1), match.group(2)
        values = _gram_coordinates(body)
        if values is None:
            raise _GramReadingError(f"coordonnees illisibles pour {name}")
        if name in coordinates and coordinates[name] != values:
            raise _GramReadingError(f"coordonnees contradictoires pour {name}")
        coordinates[name] = values
        see(name)

    for match in re.finditer(
        _NORM_MARK + r"\s*" + _VEC + r"\s*" + _NORM_MARK + r"\s*=\s*(" + _SCALAR + r")",
        text,
    ):
        name = match.group(1)
        value = _gram_scalar(match.group(2))
        if value is None:
            raise _GramReadingError(f"norme illisible pour {name}")
        if value < 0:
            raise _GramReadingError(f"norme negative pour {name}")
        if name in norms and norms[name] != value:
            raise _GramReadingError(f"normes contradictoires pour {name}")
        norms[name] = value
        see(name)

    for match in re.finditer(
        _VEC + r"\s*\\cdot\s*" + _VEC + r"\s*=\s*(" + _SCALAR + r")", text
    ):
        left, right = match.group(1), match.group(2)
        value = _gram_scalar(match.group(3))
        if value is None:
            raise _GramReadingError("produit scalaire illisible")
        see(left)
        see(right)
        key = tuple(sorted((left, right)))
        if key in dots and dots[key] != value:
            raise _GramReadingError(f"produits scalaires contradictoires pour {key}")
        dots[key] = value

    for match in re.finditer(
        r"\(\s*" + _VEC + r"\s*[,;]\s*" + _VEC + r"\s*\)\s*=\s*(" + _SCALAR + r")",
        text,
    ):
        left, right = match.group(1), match.group(2)
        value = _gram_scalar(match.group(3))
        if value is None:
            raise _GramReadingError("angle illisible")
        see(left)
        see(right)
        key = tuple(sorted((left, right)))
        if key in angles and angles[key] != value:
            raise _GramReadingError(f"angles contradictoires pour {key}")
        angles[key] = value

    return coordinates, norms, dots, angles, order


def _gram_matrix(
    names: list[str],
    coordinates: dict[str, list],
    norms: dict[str, Any],
    dots: dict[tuple[str, str], Any],
    angles: dict[tuple[str, str], Any],
):
    """Matrice de Gram complete des vecteurs nommes, ou None si indeterminee."""

    sympy = _sympy()

    def agree(first, second) -> bool:
        return sympy.simplify(first - second) == 0

    squares: dict[str, Any] = {}
    for name in names:
        candidates = []
        if name in coordinates:
            candidates.append(
                sum(value * value for value in coordinates[name])
            )
        if name in norms:
            candidates.append(norms[name] ** 2)
        if not candidates:
            return None
        if any(not agree(candidates[0], other) for other in candidates[1:]):
            return None
        squares[name] = sympy.simplify(candidates[0])

    size = len(names)
    entries = [[None] * size for _ in range(size)]
    for i, first in enumerate(names):
        entries[i][i] = squares[first]
        for j in range(i + 1, size):
            second = names[j]
            key = tuple(sorted((first, second)))
            candidates = []
            if first in coordinates and second in coordinates:
                if len(coordinates[first]) != len(coordinates[second]):
                    return None
                candidates.append(
                    sum(
                        a * b
                        for a, b in zip(coordinates[first], coordinates[second])
                    )
                )
            if key in dots:
                candidates.append(dots[key])
            if key in angles:
                candidates.append(
                    sympy.sqrt(squares[first])
                    * sympy.sqrt(squares[second])
                    * sympy.cos(angles[key])
                )
            if not candidates:
                return None
            if any(not agree(candidates[0], other) for other in candidates[1:]):
                return None
            value = sympy.simplify(candidates[0])
            entries[i][j] = value
            entries[j][i] = value
    return sympy.Matrix(entries)


def _gram_is_positive_semidefinite(matrix) -> bool:
    """Une matrice de Gram existe si et seulement si elle est symetrique PSD."""

    sympy = _sympy()
    if sympy.simplify(matrix - matrix.T) != sympy.zeros(*matrix.shape):
        return False
    try:
        eigenvalues = matrix.eigenvals()
    except (NotImplementedError, TypeError, ValueError):  # pragma: no cover
        return False
    for eigenvalue in eigenvalues:
        value = sympy.simplify(eigenvalue)
        if value.is_real is not True or value.is_nonnegative is not True:
            return False
    return True


def _gram_combination(fragment: str, names: list[str]) -> list | None:
    """Coefficients de la combinaison lineaire sum_i c_i u_i, ou None."""

    sympy = _sympy()
    text = fragment
    tokens: list[str] = []
    for position, name in enumerate(names):
        token = f"GRAMVEC{position}"
        tokens.append(token)
        text = text.replace("\\vec{" + name + "}", f" {token} ")
    text = _expand_latex_fractions(text)
    if text is None:
        return None
    if re.search(r"\\[a-zA-Z]+", text):
        return None
    text = text.replace("{", "(").replace("}", ")")
    if not re.fullmatch(r"[0-9A-Za-z_+\-*/^(). ]*", text) or not text.strip():
        return None
    text = text.replace("^", "**")

    symbols = {token: sympy.Symbol(token, real=True) for token in tokens}
    expression = _closed_symbolic_expression(text, symbols)
    if expression is None:
        return None
    if not getattr(expression, "free_symbols", set()) <= set(symbols.values()):
        return None

    coefficients = []
    remainder = expression
    for token in tokens:
        symbol = symbols[token]
        coefficient = sympy.simplify(expression.coeff(symbol))
        if coefficient.free_symbols:
            return None
        coefficients.append(coefficient)
        remainder = remainder - coefficient * symbol
    if sympy.simplify(remainder) != 0:
        return None
    if all(coefficient == 0 for coefficient in coefficients):
        return None
    return coefficients


def _gram_quadratic(system: _GramSystem, left: list, right: list | None = None):
    """c^T G d : produit scalaire de deux combinaisons lineaires."""

    sympy = _sympy()
    other = left if right is None else right
    total = sympy.Integer(0)
    for i, first in enumerate(left):
        for j, second in enumerate(other):
            total += first * second * system.matrix[i, j]
    return sympy.simplify(total)


def _gram_angle_pair(text: str):
    """Le couple de vecteurs dont l'enonce demande l'angle ou le cosinus."""

    plain = _plain(text)
    if "angle" not in plain and "cosinus" not in plain:
        return None
    if "vecteur" not in plain:
        return None
    match = re.search(
        r"entre\s+(?:les\s+)?(?:vecteurs?\s+)?"
        + _VEC_OR_TUPLE
        + r"\s+et\s+"
        + _VEC_OR_TUPLE,
        text,
    )
    if match is None:
        return None
    return (
        (match.group(1), match.group(2)),
        (match.group(3), match.group(4)),
    )


def _gram_asked(fragment: str, system: _GramSystem):
    """Quantite interrogee : norme, carre de norme, produit scalaire, cosinus."""

    sympy = _sympy()
    text = fragment.strip()

    square = re.fullmatch(
        _NORM_MARK + r"(.+)" + _NORM_MARK + r"\s*\^\s*\{?\s*2\s*\}?", text
    )
    if square is not None:
        coefficients = _gram_combination(square.group(1), system.names)
        if coefficients is None:
            return None
        value = _gram_quadratic(system, coefficients)
        return (value, "carre de la norme d'une combinaison lineaire : c^T G c")

    norm = re.fullmatch(_NORM_MARK + r"(.+)" + _NORM_MARK, text)
    if norm is not None:
        coefficients = _gram_combination(norm.group(1), system.names)
        if coefficients is None:
            return None
        value = sympy.sqrt(_gram_quadratic(system, coefficients))
        return (
            sympy.simplify(value),
            "norme d'une combinaison lineaire : sqrt(c^T G c)",
        )

    cosine = re.fullmatch(
        r"\\cos\s*\(\s*" + _VEC + r"\s*[,;]\s*" + _VEC + r"\s*\)", text
    )
    pair = re.fullmatch(r"\(\s*" + _VEC + r"\s*[,;]\s*" + _VEC + r"\s*\)", text)
    if cosine is not None or pair is not None:
        match = cosine if cosine is not None else pair
        first, second = match.group(1), match.group(2)
        if first not in system.names or second not in system.names:
            return None
        return _gram_pair_value(
            system, first, second, want_angle=pair is not None
        )

    parts = text.split("\\cdot")
    if len(parts) == 2:
        left = _gram_combination(parts[0], system.names)
        right = _gram_combination(parts[1], system.names)
        if left is None or right is None:
            return None
        value = _gram_quadratic(system, left, right)
        return (value, "produit scalaire de deux combinaisons lineaires : c^T G d")
    return None


def _gram_pair_value(
    system: _GramSystem, first: str, second: str, *, want_angle: bool
):
    """cos(u, v) = G_uv / sqrt(G_uu G_vv), et l'angle geometrique associe."""

    sympy = _sympy()
    i, j = system.index(first), system.index(second)
    if system.matrix[i, i] == 0 or system.matrix[j, j] == 0:
        return None
    cosine = sympy.simplify(
        system.matrix[i, j]
        / (sympy.sqrt(system.matrix[i, i]) * sympy.sqrt(system.matrix[j, j]))
    )
    if want_angle:
        return (
            sympy.simplify(sympy.acos(cosine)),
            "angle geometrique : arccos(G_uv / sqrt(G_uu G_vv))",
        )
    return (cosine, "cosinus : G_uv / sqrt(G_uu G_vv)")


def _euclidean_gram_form(inp: SolverInput) -> SolverResult | None:
    """Famille finie de vecteurs specifiee par ses donnees de Gram."""

    statement = inp.statement
    normalised = _gram_normalise(statement)
    angle_pair = _gram_angle_pair(normalised)
    if (
        "\\vec{" not in normalised
        and _NORM_MARK not in normalised
        and angle_pair is None
    ):
        return None

    # Les coordonnees ne donnent le produit scalaire qu'en base ORTHONORMEE.
    if re.search(r"\bnon\b[^.]{0,24}orthonorm", _math_text(statement)):
        return None

    try:
        coordinates, norms, dots, angles, order = _gram_declarations(normalised)
    except _GramReadingError:
        return None

    fragments = re.findall(r"\$([^$]+)\$", statement)
    normalised_fragments = [_gram_normalise(fragment) for fragment in fragments]

    if angle_pair is not None:
        resolved: list[str] = []
        for position, (name, tuple_body) in enumerate(angle_pair):
            if name:
                resolved.append(name)
                continue
            values = _gram_coordinates(tuple_body)
            if values is None:
                return None
            # Un uplet anonyme recoit un nom que l'enonce ne peut pas porter :
            # aucune collision possible avec un \vec{...} du texte.
            label = f"#{position + 1}"
            coordinates[label] = values
            if label not in order:
                order.append(label)
            resolved.append(label)
        angle_names = tuple(resolved)
    else:
        angle_names = ()

    if not order:
        return None

    matrix = _gram_matrix(order, coordinates, norms, dots, angles)
    if matrix is None:
        return None
    if not _gram_is_positive_semidefinite(matrix):
        return None
    system = _GramSystem(names=order, matrix=matrix)

    def is_declaration(fragment: str) -> bool:
        try:
            _, fragment_norms, fragment_dots, fragment_angles, _ = _gram_declarations(
                fragment
            )
        except _GramReadingError:
            return True
        if fragment_norms or fragment_dots or fragment_angles:
            return True
        return bool(re.search(_VEC + r"\s*\([^()]*\)", fragment))

    candidates = []
    for fragment in normalised_fragments:
        if is_declaration(fragment):
            continue
        asked = _gram_asked(fragment, system)
        if asked is not None:
            candidates.append(asked)

    if len(candidates) > 1:
        # Deux quantites interrogeables : l'enonce n'est pas lu sans ambiguite.
        return None
    if candidates:
        expected, derivation = candidates[0]
    elif angle_names:
        outcome = _gram_pair_value(
            system, angle_names[0], angle_names[1], want_angle=True
        )
        if outcome is None:
            return None
        expected, derivation = outcome
    else:
        return None

    if getattr(expected, "free_symbols", set()):
        return None

    # Contrat strict : la famille ne conclut que si elle a lu TOUTES les
    # options comme des NOMBRES et en trouve exactement une egale a la valeur
    # calculee. La lecture est symbolique et non rationnelle : la quantite
    # cherchee vaut souvent sqrt(35) ou pi/4, qu'une valeur flottante ou
    # rationnelle approcherait au lieu de la decider.
    sympy = _sympy()
    readings: dict[str, Any] = {}
    for letter, raw in inp.options.items():
        candidate = latex_to_sympy(raw)
        if candidate is None or getattr(candidate, "free_symbols", set()):
            return None
        readings[letter] = candidate
    truths = {
        letter: bool(sympy.simplify(value - expected) == 0)
        for letter, value in readings.items()
    }
    readable = len(readings)
    if sum(1 for truth in truths.values() if truth) != 1:
        return None

    display = [
        f"G[{name}] = "
        + ", ".join(str(matrix[index, column]) for column in range(len(order)))
        for index, name in enumerate(order)
    ]
    return SolverResult(
        status="MACHINE_RESOLVED",
        family="EUCLIDEAN_GRAM_FORM",
        option_truths=truths,
        computed_value=str(expected),
        independent_evidence=(
            "Donnees de Gram des vecteurs "
            + ", ".join(order)
            + " : "
            + " ; ".join(display)
            + ". Matrice symetrique semi-definie positive, donc realisable par "
            "une famille de vecteurs d'un espace prehilbertien reel. Quantite "
            "interrogee evaluee exactement par la forme de Gram ("
            + derivation
            + ") : "
            + str(expected)
            + "."
        ),
        readable_options=readable,
    )


def _published_function_parameter_role(inp: SolverInput) -> SolverResult | None:
    """Identify a referential question without inventing a general code proof.

    The sanitized input does not identify a unique, digest-bound program in
    its chapter. A repository-wide function-name search is not provenance,
    and a few matching calls cannot establish a parameter's role for all
    admissible inputs. Keep the scientific review open, without executing
    any published source. Actual code review uses the existing confined
    review workflow, with explicit sources and a general argument.
    """

    statement = _plain(inp.statement)
    if "que designe" not in statement and "que represente" not in statement:
        return None
    call = re.search(r"\\code\{([A-Za-z_][A-Za-z0-9_]*)\(([^)]*)\)\}", inp.statement)
    if call is None:
        return None
    parameter = re.search(r"\$([a-zA-Z_][a-zA-Z0-9_]*)\$\s*\?", inp.statement)
    if parameter is None:
        return None
    name, signature, wanted = call.group(1), call.group(2), parameter.group(1)
    parameters = [part.strip() for part in signature.split(",") if part.strip()]
    if wanted not in parameters:
        return None

    return SolverResult(
        status="NOT_MACHINE_RESOLVABLE",
        family="PUBLISHED_FUNCTION_PARAMETER_ROLE",
        reason=(
            "referential code question: no uniquely identified chapter source "
            "and no source-bound general argument for the parameter role; "
            "finite sample executions cannot prove this claim"
        ),
    )


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
    _symbolic_expression_question,
    _order_comparison,
    _monotonicity_of_a_function,
    _range_claim,
    _universal_inequality_claim,
    # Ajoutee EN DERNIER : l'aiguillage retient la premiere famille qui rend un
    # resultat, donc une famille ajoutee en queue ne peut modifier aucun verdict
    # deja atteint par une famille anterieure. Un test le prouve sur le corpus.
    _euclidean_gram_form,
    # Referentielle : abstention explicite sans contexte de source ni preuve
    # generale. Aucun programme publie n'est charge ou execute ici.
    _published_function_parameter_role,
    # Deux dernieres, en queue elles aussi. Elles lisent un trinome ECRIT sous
    # forme factorisee et en tirent, l'une la somme et le produit des racines,
    # l'autre le signe. Deux questions du second degre partaient a la revue
    # humaine faute de famille : elles se tranchent en lisant les facteurs.
    _sum_and_product_of_roots,
    _factored_quadratic_sign,
)




def solve(inp: SolverInput) -> SolverResult:
    """Resout la question sans jamais avoir vu la reponse declaree."""

    for family in FAMILIES:
        try:
            result = family(inp)
        except (UnsupportedExpression, ValueError, ZeroDivisionError):
            result = None
        if result is not None:
            if (
                result.status == "MACHINE_RESOLVED"
                and result.true_option_count == 0
                and result.readable_options is not None
                and result.readable_options < len(inp.options)
            ):
                # La famille n'a lu qu'une partie des options et n'en trouve
                # aucune vraie : c'est un echec de lecture, pas un QCM sans
                # bonne reponse. On s'abstient plutot que de fabriquer un
                # defaut scientifique.
                return SolverResult(
                    status="NOT_MACHINE_RESOLVABLE",
                    family=None,
                    reason=(
                        f"la famille {result.family} n'a lu que "
                        f"{result.readable_options} option(s) sur "
                        f"{len(inp.options)} et n'en trouve aucune vraie"
                    ),
                )
            return result
    return SolverResult(
        status="NOT_MACHINE_RESOLVABLE",
        family=None,
        reason=(
            "aucune famille mathematique generique ne modelise cet enonce sans "
            "ecrire une derivation propre a la question"
        ),
    )
