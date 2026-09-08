#!/usr/bin/env python3
"""Evaluation exacte d'une expression arithmetique LaTeX elementaire.

Sert aux controles machine qui doivent comparer une valeur affirmee dans le
texte a la valeur reellement calculable. Le sous-langage est volontairement
minimal et ferme : tout ce qui n'est pas reconnu leve UnsupportedExpression,
jamais une valeur approchee silencieuse.

Reconnu : entiers, decimaux francais (3{,}14 et 3,14), \\frac et \\dfrac,
\\sqrt (uniquement lorsque sa valeur est rationnelle exacte), \\times \\cdot \\div,
+ - * / ^, parentheses, \\left \\right, \\, et espaces.
"""

from __future__ import annotations

import re
import math
from fractions import Fraction

__all__ = ["UnsupportedExpression", "evaluate"]


class UnsupportedExpression(ValueError):
    """L'expression sort du sous-langage ferme reconnu."""


_STRIP = (
    (r"\\left", ""),
    (r"\\right", ""),
    (r"\\!", ""),
    (r"\\,", ""),
    (r"\\;", ""),
    (r"\\ ", ""),
    (r"\\qquad", ""),
    (r"\\quad", ""),
    (r"\{,\}", "."),
)


def _normalise(source: str) -> str:
    text = source.strip()
    for pattern, replacement in _STRIP:
        text = re.sub(pattern, replacement, text)
    text = re.sub(r"(?<=\d),(?=\d)", ".", text)
    text = text.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    text = text.replace("\\cdot", "*").replace("\\times", "*").replace("\\div", "/")
    return text.strip()


class _Parser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.index = 0

    # -- outillage ---------------------------------------------------------
    def _skip(self) -> None:
        while self.index < len(self.text) and self.text[self.index].isspace():
            self.index += 1

    def _peek(self) -> str:
        self._skip()
        return self.text[self.index] if self.index < len(self.text) else ""

    def _eat(self, char: str) -> bool:
        if self._peek() == char:
            self.index += 1
            return True
        return False

    def _group(self) -> Fraction:
        """Lit un groupe {...} ou un unique jeton.

        Sans accolades, TeX ne consomme qu'UN caractere : \\frac34 vaut 3/4,
        et non 34 divise par ce qui suit.
        """

        self._skip()
        if self._eat("{"):
            depth, start = 1, self.index
            while self.index < len(self.text) and depth:
                if self.text[self.index] == "{":
                    depth += 1
                elif self.text[self.index] == "}":
                    depth -= 1
                self.index += 1
            if depth:
                raise UnsupportedExpression("accolade non fermee")
            return _Parser(self.text[start : self.index - 1]).parse()
        if self.index < len(self.text) and self.text[self.index].isdigit():
            digit = self.text[self.index]
            self.index += 1
            return Fraction(digit)
        return self._atom()

    # -- grammaire ---------------------------------------------------------
    def parse(self) -> Fraction:
        value = self._sum()
        self._skip()
        if self.index != len(self.text):
            raise UnsupportedExpression(f"reste non consomme : {self.text[self.index:]!r}")
        return value

    def _sum(self) -> Fraction:
        value = self._product()
        while True:
            if self._eat("+"):
                value += self._product()
            elif self._eat("-"):
                value -= self._product()
            else:
                return value

    def _product(self) -> Fraction:
        value = self._unary()
        while True:
            char = self._peek()
            if char == "*":
                self.index += 1
                value *= self._unary()
            elif char == "/":
                self.index += 1
                divisor = self._unary()
                if divisor == 0:
                    raise UnsupportedExpression("division par zero")
                value /= divisor
            else:
                return value

    def _power(self) -> Fraction:
        base = self._atom()
        if self._eat("^"):
            exponent = self._group()
            if exponent.denominator != 1:
                raise UnsupportedExpression("exposant non entier")
            if base == 0 and exponent == 0:
                raise UnsupportedExpression("zero puissance zero exige une convention explicite")
            return base ** int(exponent)
        return base

    def _unary(self) -> Fraction:
        if self._eat("-"):
            return -self._unary()
        if self._eat("+"):
            return self._unary()
        return self._power()

    def _atom(self) -> Fraction:
        self._skip()
        if self.index >= len(self.text):
            raise UnsupportedExpression("expression vide")
        char = self.text[self.index]
        if char == "(":
            self.index += 1
            value = self._sum()
            if not self._eat(")"):
                raise UnsupportedExpression("parenthese non fermee")
            return value
        if char == "{":
            return self._group()
        if char == "\\":
            return self._command()
        match = re.match(r"\d+(?:\.\d+)?", self.text[self.index :])
        if not match:
            raise UnsupportedExpression(f"jeton inconnu : {self.text[self.index:][:12]!r}")
        self.index += match.end()
        return Fraction(match.group(0))

    def _command(self) -> Fraction:
        match = re.match(r"\\([A-Za-z]+)", self.text[self.index :])
        if not match:
            raise UnsupportedExpression("commande LaTeX illisible")
        name = match.group(1)
        self.index += match.end()
        if name == "frac":
            numerator = self._group()
            denominator = self._group()
            if denominator == 0:
                raise UnsupportedExpression("fraction de denominateur nul")
            return numerator / denominator
        if name == "sqrt":
            radicand = self._group()
            if radicand < 0:
                raise UnsupportedExpression("racine d'un nombre negatif")
            numerator = math.isqrt(radicand.numerator)
            denominator = math.isqrt(radicand.denominator)
            if (numerator * numerator != radicand.numerator
                    or denominator * denominator != radicand.denominator):
                raise UnsupportedExpression("racine non rationnelle : aucune approximation exacte")
            return Fraction(numerator, denominator)
        raise UnsupportedExpression(f"commande non supportee : \\{name}")


def evaluate(source: str) -> Fraction:
    """Valeur exacte de l'expression, ou UnsupportedExpression."""

    return _Parser(_normalise(source)).parse()
