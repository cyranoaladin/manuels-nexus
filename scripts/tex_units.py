#!/usr/bin/env python3
"""Couper du LaTeX sans casser ce qu'il ouvre.

Un barème extrait d'un corrigé est un morceau de LaTeX, et un morceau de LaTeX
n'est pas une chaîne de caractères comme une autre : `\\[` promet `\\]`,
`\\begin{align*}` promet sa fin, une accolade promet la sienne. Couper à quatre
cents caractères ne demande l'avis de personne, et rend des choses comme :

    \\[ ... = 10x - 11        (sans \\])
    \\end{align*} \\[         (une fermeture sans ouverture, une ouverture sans fin)

Un enseignant à qui l'on montre ça ne lit pas un attendu : il lit un accident.
Ce module donne donc les deux seules opérations dont l'extraction a besoin --
dire si un fragment tient debout, et le raccourcir en s'arrêtant à une
frontière où il tient encore debout.

Le vocabulaire des environnements n'est pas listé : il est LU dans le texte.
Ce qui compte n'est pas de connaître `align*` mais de constater que ce qui est
ouvert est refermé.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterator

BEGIN = re.compile(r"\\begin\{([^}]*)\}")
END = re.compile(r"\\end\{([^}]*)\}")


def _scan(text: str) -> Iterator[tuple[int, str, str]]:
    """Parcourt le texte en rendant (position, sorte, valeur) pour chaque jeton.

    Une séquence de contrôle est consommée d'un bloc : `\\%` n'ouvre pas de
    commentaire, `\\{` n'ouvre pas de groupe, et `\\[` n'est pas la barre
    oblique suivie d'un crochet.
    """

    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char == "\\" and index + 1 < length:
            following = text[index + 1]
            if following == "[":
                yield index, "display", "open"
                index += 2
                continue
            if following == "]":
                yield index, "display", "close"
                index += 2
                continue
            if following == "(":
                yield index, "inline_paren", "open"
                index += 2
                continue
            if following == ")":
                yield index, "inline_paren", "close"
                index += 2
                continue
            if following.isalpha():
                match = re.match(r"\\([a-zA-Z]+)", text[index:])
                name = match.group(1)
                if name == "begin":
                    environment = BEGIN.match(text[index:])
                    if environment:
                        yield index, "environment", "open:" + environment.group(1)
                        index += environment.end()
                        continue
                if name == "end":
                    environment = END.match(text[index:])
                    if environment:
                        yield index, "environment", "close:" + environment.group(1)
                        index += environment.end()
                        continue
                index += match.end()
                continue
            # `\%`, `\{`, `\$`, `\_` : un caractère échappé, rien de plus.
            index += 2
            continue
        if char == "%":
            # Un commentaire court jusqu'au bout de la ligne.
            newline = text.find("\n", index)
            index = length if newline < 0 else newline + 1
            continue
        if char == "$":
            if text.startswith("$$", index):
                yield index, "display_dollar", "toggle"
                index += 2
                continue
            yield index, "math", "toggle"
            index += 1
            continue
        if char == "{":
            yield index, "group", "open"
            index += 1
            continue
        if char == "}":
            yield index, "group", "close"
            index += 1
            continue
        index += 1


def imbalances(text: str) -> list[str]:
    """Ce que le fragment laisse ouvert ou ferme en trop, nommé.

    Rendre une liste plutôt qu'un booléen : quand un contrôle échoue, il doit
    pouvoir dire ce qui manque, pas seulement que quelque chose manque.
    """

    math = False
    display_dollar = False
    displays = 0
    parens = 0
    groups = 0
    environments: Counter[str] = Counter()
    faults: list[str] = []

    for _, kind, value in _scan(text):
        if kind == "math":
            math = not math
        elif kind == "display_dollar":
            display_dollar = not display_dollar
        elif kind == "display":
            displays += 1 if value == "open" else -1
            if displays < 0:
                faults.append("\\] sans \\[")
                displays = 0
        elif kind == "inline_paren":
            parens += 1 if value == "open" else -1
            if parens < 0:
                faults.append("\\) sans \\(")
                parens = 0
        elif kind == "group":
            groups += 1 if value == "open" else -1
            if groups < 0:
                faults.append("} sans {")
                groups = 0
        elif kind == "environment":
            state, name = value.split(":", 1)
            environments[name] += 1 if state == "open" else -1
            if environments[name] < 0:
                faults.append(f"\\end{{{name}}} sans \\begin")
                environments[name] = 0

    if math:
        faults.append("$ non refermé")
    if display_dollar:
        faults.append("$$ non refermé")
    if displays:
        faults.append("\\[ sans \\]")
    if parens:
        faults.append("\\( sans \\)")
    if groups:
        faults.append("{ sans }")
    for name, depth in environments.items():
        if depth:
            faults.append(f"\\begin{{{name}}} sans \\end")
    if re.search(r"(?<!\\)\\$", text):
        faults.append("barre oblique en fin de fragment")
    return faults


def is_balanced(text: str) -> bool:
    return not imbalances(text)


def _resting_points(text: str) -> Iterator[int]:
    """Les positions où le fragment, coupé là, tiendrait debout.

    Une position ne convient que si rien n'est ouvert -- ni mode
    mathématique, ni environnement, ni groupe -- et si l'on n'est pas au
    milieu d'un mot ou d'une commande.
    """

    math = False
    display_dollar = False
    displays = 0
    parens = 0
    groups = 0
    environments: Counter[str] = Counter()
    consumed = 0

    for position, kind, value in _scan(text):
        # Tout ce qui sépare deux jetons est du texte ordinaire : on peut s'y
        # arrêter à chaque blanc, à condition que rien ne soit ouvert.
        if not (
            math
            or display_dollar
            or displays
            or parens
            or groups
            or any(environments.values())
        ):
            for offset in range(consumed, position):
                if text[offset].isspace():
                    yield offset
        consumed = position

        if kind == "math":
            math = not math
        elif kind == "display_dollar":
            display_dollar = not display_dollar
        elif kind == "display":
            displays = max(0, displays + (1 if value == "open" else -1))
        elif kind == "inline_paren":
            parens = max(0, parens + (1 if value == "open" else -1))
        elif kind == "group":
            groups = max(0, groups + (1 if value == "open" else -1))
        elif kind == "environment":
            state, name = value.split(":", 1)
            environments[name] = max(
                0, environments[name] + (1 if state == "open" else -1)
            )

    if not (
        math
        or display_dollar
        or displays
        or parens
        or groups
        or any(environments.values())
    ):
        for offset in range(consumed, len(text) + 1):
            if offset == len(text) or text[offset].isspace():
                yield offset


def truncate(text: str, limit: int) -> str:
    """Le plus long début du texte qui tienne debout et n'excède pas `limit`.

    S'il n'existe aucune frontière sûre sous la limite, le fragment est rendu
    vide : mieux vaut un dossier qui dit « rien à montrer ici » qu'un dossier
    qui montre une formule coupée en deux.
    """

    if len(text) <= limit and is_balanced(text):
        return text
    best = 0
    for position in _resting_points(text):
        if position > limit:
            break
        best = position
    return text[:best].rstrip()


def sentences(text: str) -> list[str]:
    """Les phrases du fragment, sans jamais couper dans une unité TeX.

    Un point à l'intérieur de `\\[ ... u_{n+1} = 1{,}05\\,u_n. \\]` ne termine
    aucune phrase : c'est la ponctuation de la formule. Découper dessus est
    exactement ce qui produisait des attendus commençant par `\\end{align*}`.
    """

    cuts = set(_resting_points(text))
    parts: list[str] = []
    start = 0
    for index, char in enumerate(text):
        if char not in ".;":
            continue
        after = index + 1
        if after < len(text) and not text[after].isspace():
            continue
        if after not in cuts and after != len(text):
            continue
        piece = text[start:after].strip()
        if piece:
            parts.append(piece)
        start = after
    tail = text[start:].strip()
    if tail:
        parts.append(tail)
    return parts
