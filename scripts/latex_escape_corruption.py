#!/usr/bin/env python3
r"""Detecte les macros LaTeX detruites par une sequence d'echappement Python.

Une macro ecrite dans une chaine Python non-brute perd son antislash et son
initiale : ``"$\nearrow$"`` devient ``"$"``, un saut de ligne, puis
``"earrow$"``. Le document compile SANS ERREUR et imprime les lettres
« earrow » a la place de la fleche. Aucune verification de compilation ne peut
donc voir ce defaut : il faut lire la source.

Les initiales dangereuses sont celles que Python interprete : \n \t \r \b \f
\v \a. ``\searrow`` survit parce que ``\s`` n'est pas une sequence
d'echappement -- ce qui explique les tableaux de variations ou une fleche sur
deux etait correcte.

Le detecteur ne signale un fragment que s'il DEBUTE une ligne alors que le
mode mathematique est ouvert : en mode mathematique, un mot francais isole en
debut de ligne n'a pas de sens, ce qui elimine les faux positifs du type
« ne sont pas coplanaires ».
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Queues de macros LaTeX privees de leur initiale par une sequence Python.
TAILS: dict[str, str] = {
    "n": "earrow ewline ode eq abla onumber oindent olimits ot u e",
    "t": "imes extbf extit extrm ext an heta frac ag riangle op o",
    "r": "ightarrow ight ho ef angle m",
    "f": "orall rac box ootnotesize rown",
    "b": "egin oxed igcup inom ullet ar f",
    "v": "arepsilon arphi arnothing dots space ec",
    "a": "pprox lpha ngle rccos rcsin rctan rray lign st",
}
MINIMUM_TAIL = 2  # une seule lettre ("f", "e") est une cellule legitime
FRAGMENT = re.compile(
    "^(" + "|".join(sorted((t for tails in TAILS.values() for t in tails.split()
                            if len(t) >= MINIMUM_TAIL),
                           key=len, reverse=True)) + r")\b"
)
CONTROL = re.compile(rb"[\x00-\x08\x0b\x0c\x0e-\x1f]")

# TikZ compose `\node` : ampute, le fragment « ode {...}; » n'est plus une
# commande et TikZ le pose comme du texte litteral, sans fonte selectionnee --
# le lecteur voit un cadre vide. Ces environnements sont donc, eux aussi, des
# contextes ou un fragment en debut de ligne denonce une macro detruite.
GRAPHICS_ENVIRONMENTS = {"tikzpicture", "axis", "scope"}
MATH_ENVIRONMENTS = {
    "align", "align*", "array", "aligned", "equation", "equation*",
    "gather", "gather*", "cases", "matrix", "bmatrix", "pmatrix", "vmatrix",
}
OPEN_ENV = re.compile(r"\\begin\{([a-z*]+)\}")
CLOSE_ENV = re.compile(r"\\end\{([a-z*]+)\}")


def _missing_initial(fragment: str) -> str:
    for initial, tails in TAILS.items():
        if fragment in [x for x in tails.split() if len(x) >= MINIMUM_TAIL]:
            return initial
    raise KeyError(fragment)


def scan(text: str) -> list[tuple[int, str, str]]:
    """Rend (numero de ligne, fragment, macro reconstituee)."""
    inline_open = False
    display_depth = 0
    environments: list[str] = []
    findings: list[tuple[int, str, str]] = []

    for number, line in enumerate(text.split("\n"), start=1):
        in_math = inline_open or display_depth > 0 or any(
            e in MATH_ENVIRONMENTS or e in GRAPHICS_ENVIRONMENTS for e in environments
        )
        if in_math:
            match = FRAGMENT.match(line)
            if match:
                fragment = match.group(1)
                findings.append(
                    (number, fragment, "\\" + _missing_initial(fragment) + fragment)
                )

        stripped = re.sub(r"\\[\[\]$]", "", line)  # \$ \[ \] echappes
        inline_open ^= len(re.findall(r"(?<!\\)\$", stripped)) % 2 == 1
        display_depth += len(re.findall(r"(?<!\\)\\\[", line))
        display_depth -= len(re.findall(r"(?<!\\)\\\]", line))
        display_depth = max(display_depth, 0)
        for name in OPEN_ENV.findall(line):
            environments.append(name)
        for name in CLOSE_ENV.findall(line):
            if name in environments:
                environments.remove(name)
    return findings


def scan_tree(root: Path) -> dict[str, list[tuple[int, str, str]]]:
    report: dict[str, list[tuple[int, str, str]]] = {}
    for path in sorted(root.rglob("*.tex")):
        if "/build/" in str(path):
            continue
        raw = path.read_bytes()
        entries = list(scan(raw.decode("utf-8", "replace")))
        if CONTROL.search(raw):
            entries.append((0, "<caractere de controle>", "<illisible>"))
        if entries:
            report[str(path)] = entries
    return report


if __name__ == "__main__":
    base = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    found = scan_tree(base)
    for path, entries in found.items():
        for number, fragment, macro in entries:
            print(f"{path}:{number}: '{fragment}' -> {macro}")
    print(f"{sum(len(v) for v in found.values())} occurrences dans {len(found)} fichiers")
    sys.exit(1 if found else 0)
