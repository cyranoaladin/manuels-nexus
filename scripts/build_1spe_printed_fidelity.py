#!/usr/bin/env python3
"""Ce qui est imprime doit etre ce qui etait ecrit — commandes et code.

Deux corruptions ont traverse une campagne entiere de controles geometriques
sans jamais etre vues, parce qu'aucun controle ne LISAIT ce que la page
raconte :

* le fragment `ewpage` imprime en toutes lettres — un `\\newpage` ampute de sa
  barre oblique, tres probablement par une chaine Python non brute ou `\\n`
  s'etait change en saut de ligne ;
* du code Python imprime avec des guillemets typographiques : `print(f”...”)`,
  `”””Renvoie...”””`. Le code affiche n'etait plus du Python. Un eleve qui le
  recopie obtient une erreur de syntaxe.

Ce module regarde donc deux choses que la geometrie ne peut pas voir.

**Fragments de commande.** Une commande LaTeX privee de sa barre oblique laisse
sa queue en clair. Le vocabulaire n'est pas une liste noire arbitraire : il est
LU dans le corpus — toute sequence de controle que les sources emploient
vraiment donne une queue a surveiller. Ce qui est cherche dans la page, ce sont
ces queues-la.

**Fidelite du code imprime.** Le controle ne cherche pas des caracteres
suspects : il COMPARE. Chaque programme publie — bloc `python` ecrit dans un
objet, ou fichier `.py` inclus par `\\lstinputlisting` — est retrouve dans la
couche texte du PDF, caractere par caractere, espaces mis a part. Comparer
plutot que blacklister importe : c'est ainsi qu'on voit aussi bien un
guillemet courbe qu'une ligature `<=` fusionnee ou un programme compose dans
la mauvaise fonte, sans avoir a prevoir chaque deformation possible.

L'indentation n'est pas ce qui est verifie : la couche texte d'un PDF ne
restitue pas fidelement les espaces de tete. C'est dit ici plutot que
sous-entendu. Tout le reste — guillemets, apostrophes, barres obliques
inverses, operateurs, accolades, deux-points — est compare exactement.

Metriques bloquantes : `VISIBLE_MALFORMED_LATEX_FRAGMENT`,
`MALFORMED_FRAGMENT_IN_SOURCE`, `CODE_BLOCK_NOT_FAITHFUL`,
`SMART_QUOTE_IN_CODE_TOKEN`, `UNKNOWN`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import MATH, ROOT  # noqa: E402

JSON_TARGET = ROOT / "audit/1SPE_PRINTED_FIDELITY.json"
MD_TARGET = ROOT / "audit/1SPE_PRINTED_FIDELITY.md"
GENERATED_BY = "scripts/build_1spe_printed_fidelity.py"

CLASS = ROOT / "gabarits/common/nexus-manuel.cls"
VARIANTS = ("eleve", "professeur")

#: Les six manuels canoniques de la collection, avec le repertoire de build et
#: la racine depuis laquelle leurs `\input` se resolvent. La liste n'est pas
#: inventee : elle suit les assembleurs des deux disciplines.
CANONICAL_MANUALS = {
    "1SPE": (MATH / "build/MANUEL_1SPE", MATH),
    "TSPE_2026_2027": (MATH / "build/MANUEL_TSPE_2026-2027", MATH),
    "TCOMPL": (MATH / "build/MANUEL_TCOMPL", MATH),
    "TEXPERTES": (MATH / "build/MANUEL_TEXPERTES", MATH),
    "1NSI": (ROOT / "NSI/build/MANUEL_1NSI", ROOT / "NSI"),
    "TNSI": (ROOT / "NSI/build/MANUEL_TNSI", ROOT / "NSI"),
}

#: Reglee par `--manual` ; le module garde son comportement 1SPE par defaut.
BUILD = CANONICAL_MANUALS["1SPE"][0]
SOURCE_ROOT = MATH
MASTER_STEM = "MANUEL_1SPE"

# Une commande doit etre employee au moins ainsi de fois pour que sa queue
# compte comme un mot surveille : en dessous, une occurrence unique ferait du
# bruit sans rien prouver.
COMMAND_FLOOR = 3
# Une queue trop courte est un mot ordinaire du francais ou du code.
TAIL_FLOOR = 4

MONO_FAMILY = "JetBrainsMono"

# La couche texte arrondit ce que la classe declare : 8,5 pt a 0,89 d'echelle
# se relit 7,54 et non 7,565. La tolerance couvre cet arrondi, rien de plus.
CODE_SIZE_TOLERANCE = 0.98

SMART = {
    "\u201c": '"',
    "\u201d": '"',
    "\u2018": "'",
    "\u2019": "'",
    "\u2013": "-",
    "\u2014": "-",
    "\u2032": "'",
}

INPUT = re.compile(r"\\input\{([^}]+)\}")
PYTHON_BLOCK = re.compile(r"\\begin\{python\}\s*\n(.*?)\\end\{python\}", re.S)
INPUT_LISTING = re.compile(r"\\lstinputlisting(?:\[[^\]]*\])?\{([^}]+)\}")
# Le maitre d'une variante declare lui-meme ce qu'il vide : l'edition eleve
# ecrit `\\RenewDocumentEnvironment{corrige}{m +b}{}{}`, qui avale le corps.
EMPTIED = re.compile(r"\\RenewDocumentEnvironment\{(\w+)\}\{[^}]*\}\{\}\{\}")
LITERATE = re.compile(r"\{(.)\}\{\{(.*?)\}\}\d")


def relative(path: Path) -> str:
    """Le chemin tel qu'on le nomme ici — depuis la racine que ce module lit.

    `manual_source_surface.relative` mesure depuis la racine du depot, figee a
    l'import. Ce module doit pouvoir nommer les objets d'un manuel miniature
    monte ailleurs, sinon rien de ce qu'il fait n'est verifiable.
    """

    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


class FidelityError(RuntimeError):
    """Une preuve manque : la fidelite ne peut pas etre etablie."""


def _fitz() -> Any:
    try:
        import fitz
    except ModuleNotFoundError:  # pragma: no cover - dependance de gate
        raise FidelityError("PyMuPDF (fitz) est requis") from None
    return fitz


# ---------------------------------------------------------------------------
#  Ce que la source dit
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def literate_map() -> dict[str, str]:
    """Les substitutions que `listings` applique, LUES dans la classe.

    `literate={—}{{---}}1` fait qu'un tiret cadratin de la source s'imprime en
    trois traits. Sans cette table, la comparaison accuserait la page d'une
    infidelite qui est en realite une regle declaree.
    """

    text = CLASS.read_text(encoding="utf-8")
    start = text.find("literate=")
    if start < 0:
        raise FidelityError("aucune table `literate` dans la classe")
    body = text[start : text.find("\n}", start)]
    mapping: dict[str, str] = {}
    for source, replacement in LITERATE.findall(body):
        # Une entree qui accentue rend exactement le caractere de depart :
        # `{é}{{\'{e}}}` s'imprime « é ». Toute autre entree remplace vraiment :
        # `{—}{{---}}` s'imprime « --- ». Le premier cas est une identite, et
        # le confondre avec le second ferait accuser la page de dire « e » la
        # ou elle dit « é ».
        if re.search(r"\\['`^\"~=.uvHtcdb]", replacement):
            mapping[source] = source
            continue
        rendered = re.sub(r"\\[a-zA-Z]+|[{}]", "", replacement)
        mapping[source] = rendered if rendered else source
    if not mapping:
        raise FidelityError("table `literate` illisible")
    return mapping


@lru_cache(maxsize=1)
def listing_font_size() -> float:
    """La taille a laquelle la classe compose un programme, LUE dans la classe.

    Sous cette taille, la fonte du code sert a autre chose : les numeros de
    ligne d'un listing, et les annotations de marge de l'edition professeur
    (un identifiant d'objet en `\\texttt`). Ces fragments s'intercalent dans
    l'ordre de lecture au milieu d'un programme ; les garder ferait accuser la
    page de couper un code qu'elle compose parfaitement.

    Ils restent regardes par le controle des guillemets, qui lui ne demande
    aucune continuite : du code en ligne dans une note de marge est du code, et
    un guillemet courbe y serait tout aussi faux.
    """

    text = CLASS.read_text(encoding="utf-8")
    scale = re.search(r"\\setmonofont\{[^}]*\}\[Scale=([0-9.]+)", text)
    size = re.search(r"basicstyle=\\ttfamily\\fontsize\{([0-9.]+)\}", text)
    if scale is None or size is None:
        raise FidelityError("taille de composition du code illisible dans la classe")
    return float(size.group(1)) * float(scale.group(1)) * CODE_SIZE_TOLERANCE


def master_text(variant: str) -> str:
    master = BUILD / f"{MASTER_STEM}_{variant}.tex"
    if not master.is_file():
        raise FidelityError(f"maitre absent : {relative(master)}")
    return master.read_text(encoding="utf-8")


def emptied_environments(variant: str) -> list[str]:
    """Ce que cette variante-ci n'imprime pas, DECLARE par son propre maitre.

    L'edition eleve vide `corrige`. Un programme ecrit dans un corrige n'est
    donc pas absent par accident : il est absent par contrat, et le contrat est
    lisible. Rien n'est suppose ici — ni le nom de l'environnement, ni la
    variante qui le vide.
    """

    return sorted(set(EMPTIED.findall(master_text(variant))))


def emptied_spans(text: str, environments: list[str]) -> list[tuple[int, int]]:
    """Les intervalles du fichier que ces environnements avalent."""

    spans: list[tuple[int, int]] = []
    for name in environments:
        opening = re.compile(r"\\begin\{" + re.escape(name) + r"\}")
        closing = re.compile(r"\\end\{" + re.escape(name) + r"\}")
        for start in opening.finditer(text):
            end = closing.search(text, start.end())
            spans.append((start.start(), end.end() if end else len(text)))
    return spans


def master_inputs(variant: str) -> tuple[list[Path], list[str]]:
    """Les objets que le maitre LaTeX compile — l'autorite est le maitre lui-meme."""

    resolved: list[Path] = []
    unresolved: list[str] = []
    for reference in INPUT.findall(master_text(variant)):
        path = SOURCE_ROOT / reference
        if path.suffix != ".tex":
            path = path.with_suffix(".tex")
        if path.is_file():
            resolved.append(path)
        else:
            unresolved.append(reference)
    return resolved, unresolved


def published_code(variant: str) -> tuple[list[dict[str, Any]], list[str]]:
    """Chaque programme que la variante imprime, avec son texte canonique."""

    sources, unresolved = master_inputs(variant)
    emptied = emptied_environments(variant)
    blocks: list[dict[str, Any]] = []
    for path in sources:
        text = path.read_text(encoding="utf-8")
        swallowed = emptied_spans(text, emptied)

        def typeset(position: int) -> bool:
            return not any(start <= position < end for start, end in swallowed)

        for index, match in enumerate(PYTHON_BLOCK.finditer(text), start=1):
            blocks.append(
                {
                    "kind": "inline_python_environment",
                    "origin": f"{relative(path)}#python-{index}",
                    "code": match.group(1),
                    "typeset": typeset(match.start()),
                }
            )
        for match in INPUT_LISTING.finditer(text):
            included = SOURCE_ROOT / match.group(1)
            if not included.is_file():
                unresolved.append(match.group(1))
                continue
            blocks.append(
                {
                    "kind": "included_python_file",
                    "origin": relative(included),
                    "included_by": relative(path),
                    "code": included.read_text(encoding="utf-8"),
                    "typeset": typeset(match.start()),
                }
            )
    return blocks, unresolved


@lru_cache(maxsize=1)
def latex_sources() -> tuple[Path, ...]:
    """Tout le TeX du depot, et pas seulement celui du manuel 1SPE.

    La barre oblique perdue vient d'un ecrivain Python, pas d'un chapitre :
    restreindre la recherche au perimetre ou le defaut a ete VU laisserait
    intacts les endroits ou il aurait pu se poser aussi. Ce qui est ecarte est
    ecarte pour une raison : `build` ne contient que du derive, et
    `reference-v4` est une maquette historique que rien ne compose.
    """

    sources: list[Path] = []
    for pattern in ("*.tex", "*.sty", "*.cls"):
        sources += sorted(ROOT.rglob(pattern))
    return tuple(
        path
        for path in sources
        if ".git" not in path.parts
        and "build" not in path.parts
        and "reference-v4" not in path.parts
    )


@lru_cache(maxsize=1)
def command_tails() -> dict[str, list[str]]:
    """Les queues de commande a surveiller, LUES dans le corpus."""

    vocabulary: Counter[str] = Counter()
    for path in latex_sources():
        vocabulary.update(
            re.findall(
                r"\\([a-zA-Z]{3,})",
                path.read_text(encoding="utf-8", errors="replace"),
            )
        )
    tails: dict[str, set[str]] = {}
    for name, count in vocabulary.items():
        if count < COMMAND_FLOOR or len(name) - 1 < TAIL_FLOOR:
            continue
        tails.setdefault(name[1:], set()).add(name)
    return {tail: sorted(names) for tail, names in tails.items()}


@lru_cache(maxsize=1)
def plain_words() -> set[str]:
    """Les mots que les sources ecrivent vraiment, commandes retirees.

    « angle » est la queue de `\\rangle` ET un mot francais courant. Sur une
    page, rien ne les distingue. Ce que le corpus permet de dire, c'est
    qu'« ewpage » n'est ecrit nulle part comme mot : sa presence sur une page
    ne peut donc venir que d'une commande amputee.
    """

    words: set[str] = set()
    for path in latex_sources():
        text = re.sub(
            r"\\[a-zA-Z]+", "  ", path.read_text(encoding="utf-8", errors="replace")
        )
        words.update(word.lower() for word in re.findall(r"[a-zA-Z]{4,}", text))
    return words


def malformed_in_sources(tails: dict[str, list[str]]) -> list[dict[str, Any]]:
    """Une queue seule sur sa ligne, dans une source : la barre a saute."""

    found: list[dict[str, Any]] = []
    for path in latex_sources():
        for number, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
        ):
            stripped = line.strip()
            if not stripped or stripped.startswith("%") or "\\" in stripped:
                continue
            if stripped in tails:
                found.append(
                    {
                        "source": relative(path),
                        "line": number,
                        "fragment": stripped,
                        "probably": tails[stripped],
                    }
                )
    return found


# ---------------------------------------------------------------------------
#  Ce que la page montre
# ---------------------------------------------------------------------------


def code_corpus(document: Any) -> tuple[str, list[int]]:
    """La couche texte composee dans la fonte du code, sans les espaces.

    Retourne la chaine continue et, pour chaque caractere, la page d'ou il
    vient : un programme coupe par une fin de page reste ainsi retrouvable, et
    la page ou il apparait reste nommable.
    """

    floor = listing_font_size()
    pieces: list[str] = []
    origin: list[int] = []
    for index in range(document.page_count):
        for block in document[index].get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if MONO_FAMILY not in span.get("font", ""):
                        continue
                    if span["size"] < floor:
                        continue
                    condensed = "".join(span["text"].split())
                    pieces.append(condensed)
                    origin.extend([index + 1] * len(condensed))
    return "".join(pieces), origin


def visible_fragments(
    document: Any, tails: dict[str, list[str]]
) -> list[dict[str, Any]]:
    """La queue d'une commande, VISIBLE sur une page.

    Une queue qui est aussi un mot du corpus n'est pas surveillee ici : la page
    ne permet pas de trancher. C'est la limite de ce controle-ci, et elle est
    couverte par l'autre : dans une SOURCE, une queue seule sur sa ligne est
    reconnaissable meme si c'est un mot ordinaire.
    """

    watched = {
        tail: names for tail, names in tails.items() if tail.lower() not in plain_words()
    }
    found: list[dict[str, Any]] = []
    for index in range(document.page_count):
        words = set(re.findall(r"[a-zA-Z]{4,}", document[index].get_text()))
        for tail in sorted(words & set(watched)):
            found.append(
                {"page": index + 1, "fragment": tail, "probably": watched[tail]}
            )
    return found


def smart_quotes_in_code(document: Any) -> list[dict[str, Any]]:
    """Un guillemet courbe compose dans la fonte du code.

    La typographie francaise du corps garde evidemment les siens : seul ce qui
    est compose comme du code est regarde.
    """

    pages: list[dict[str, Any]] = []
    for index in range(document.page_count):
        offenders: Counter[str] = Counter()
        for block in document[index].get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if MONO_FAMILY not in span.get("font", ""):
                        continue
                    for character in span["text"]:
                        if character in SMART:
                            offenders[character] += 1
        if offenders:
            pages.append(
                {
                    "page": index + 1,
                    "characters": {
                        f"U+{ord(key):04X}": value
                        for key, value in sorted(offenders.items())
                    },
                }
            )
    return pages


# ---------------------------------------------------------------------------
#  La comparaison
# ---------------------------------------------------------------------------


def expected_rendering(code: str, literate: dict[str, str]) -> str:
    """Le texte que la page doit porter pour ce programme, espaces mis a part."""

    rendered = "".join(literate.get(character, character) for character in code)
    return "".join(rendered.split())


def diagnose(expected: str, corpus: str) -> dict[str, Any]:
    """Dire OU la page cesse de dire ce que la source disait.

    Un verdict « absent » n'aide personne. Le plus long prefixe retrouve situe
    la rupture, et les quelques caracteres qui l'entourent montrent ce qui a
    ete substitue.
    """

    low, high = 0, len(expected)
    while low < high:
        middle = (low + high + 1) // 2
        if expected[:middle] in corpus:
            low = middle
        else:
            high = middle - 1
    if low == 0:
        return {
            "matched_prefix": 0,
            "note": "aucun prefixe de ce programme n'apparait dans la fonte du code",
        }
    position = corpus.find(expected[:low])
    return {
        "matched_prefix": low,
        "source_says": expected[max(0, low - 20) : low + 20],
        "page_says": corpus[max(0, position + low - 20) : position + low + 20],
    }


def compare(variant: str, literate: dict[str, str]) -> dict[str, Any]:
    pdf = BUILD / f"{MASTER_STEM}_{variant}.pdf"
    if not pdf.is_file():
        raise FidelityError(f"PDF absent : {relative(pdf)}")
    blocks, unresolved = published_code(variant)
    tails = command_tails()
    fitz = _fitz()
    with fitz.open(pdf) as document:
        corpus, origin = code_corpus(document)
        fragments = visible_fragments(document, tails)
        smart_pages = smart_quotes_in_code(document)
        pages = document.page_count

    faithful: list[dict[str, Any]] = []
    unfaithful: list[dict[str, Any]] = []
    withheld: list[dict[str, Any]] = []
    leaked: list[dict[str, Any]] = []
    for entry in blocks:
        expected = expected_rendering(entry["code"], literate)
        position = corpus.find(expected)
        row = {
            "kind": entry["kind"],
            "origin": entry["origin"],
            "characters_compared": len(expected),
        }
        if not entry["typeset"]:
            # Un corrige dans l'edition eleve : son absence n'est pas un
            # defaut, c'est le contrat. Sa PRESENCE en serait un.
            (leaked if position >= 0 else withheld).append(row)
            continue
        if position >= 0:
            faithful.append(
                {
                    **row,
                    "pages": sorted(set(origin[position : position + len(expected)])),
                }
            )
            continue
        unfaithful.append({**row, "diagnosis": diagnose(expected, corpus)})

    return {
        "variant": variant,
        "pages": pages,
        "code_blocks": len(blocks),
        "emptied_environments": emptied_environments(variant),
        "faithful": faithful,
        "unfaithful": unfaithful,
        "withheld": withheld,
        "leaked": leaked,
        "visible_malformed_fragments": fragments,
        "smart_quote_pages": smart_pages,
        "unresolved_references": sorted(set(unresolved)),
    }


def build() -> dict[str, Any]:
    literate = literate_map()
    variants = [compare(variant, literate) for variant in VARIANTS]
    source_fragments = malformed_in_sources(command_tails())
    return {
        "artifact_type": "printed_fidelity",
        "manual": MASTER_STEM,
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "why_geometry_could_not_see_this": (
            "Une page peut etre parfaitement composee — encre dans le format, "
            "aucun debordement, aucune collision — et raconter print(f”...”) "
            "ou afficher « ewpage » en toutes lettres. La geometrie regarde ou "
            "l'encre se pose ; il fallait lire ce qu'elle dit."
        ),
        "only_what_is_composed_as_a_program_is_compared": (
            "La fonte du code sert aussi aux numeros de ligne et aux "
            "annotations de marge de l'edition professeur, plus petites, qui "
            "s'intercalent dans l'ordre de lecture. La comparaison ne retient "
            "que ce qui est compose a la taille d'un programme, taille lue dans "
            "la classe. Le controle des guillemets, lui, regarde toute la fonte "
            "du code."
        ),
        "code_composition_size_pt": round(listing_font_size(), 3),
        "what_a_variant_withholds_is_declared_not_guessed": (
            "L'edition eleve vide l'environnement `corrige` : elle l'ecrit dans "
            "son propre maitre. Un programme de corrige n'y est donc pas "
            "attendu, et s'il y apparaissait ce serait le defaut."
        ),
        "this_compares_it_does_not_blacklist": (
            "Chaque programme publie est retrouve dans la couche texte du PDF "
            "et compare caractere par caractere a sa source. Comparer plutot "
            "que suspecter fait voir aussi bien un guillemet courbe qu'une "
            "ligature fusionnee ou un programme compose dans la mauvaise fonte."
        ),
        "indentation_is_not_what_is_checked": (
            "La couche texte d'un PDF ne restitue pas fidelement les espaces de "
            "tete. La comparaison porte sur tout le reste, espaces retires."
        ),
        "the_vocabulary_is_read_not_listed": (
            "Les queues de commande surveillees viennent des sequences de "
            "controle que le corpus emploie reellement, pas d'une liste noire "
            "ecrite a la main. Celles qui sont aussi des mots du corpus sont "
            "surveillees dans les sources et non sur la page, ou rien ne "
            "permettrait de les distinguer."
        ),
        "french_typography_keeps_its_quotes": (
            "Le guillemet courbe n'est cherche que dans ce qui est compose avec "
            "la fonte du code. Le corps du texte garde les siens."
        ),
        "literate_substitutions": literate,
        "source_fragments": source_fragments,
        "variants": variants,
        "summary": {
            "CODE_BLOCKS": sum(row["code_blocks"] for row in variants),
            "CODE_BLOCK_FAITHFUL": sum(len(row["faithful"]) for row in variants),
            "CODE_BLOCK_NOT_FAITHFUL": sum(len(row["unfaithful"]) for row in variants),
            "CODE_BLOCK_WITHHELD_AS_DECLARED": sum(
                len(row["withheld"]) for row in variants
            ),
            "WITHHELD_CODE_BLOCK_PRINTED": sum(len(row["leaked"]) for row in variants),
            "SMART_QUOTE_IN_CODE_TOKEN": sum(
                sum(page["characters"].values())
                for row in variants
                for page in row["smart_quote_pages"]
            ),
            "VISIBLE_MALFORMED_LATEX_FRAGMENT": sum(
                len(row["visible_malformed_fragments"]) for row in variants
            ),
            "MALFORMED_FRAGMENT_IN_SOURCE": len(source_fragments),
            "UNKNOWN": sum(len(row["unresolved_references"]) for row in variants),
        },
    }


BLOCKING = (
    "CODE_BLOCK_NOT_FAITHFUL",
    "WITHHELD_CODE_BLOCK_PRINTED",
    "SMART_QUOTE_IN_CODE_TOKEN",
    "VISIBLE_MALFORMED_LATEX_FRAGMENT",
    "MALFORMED_FRAGMENT_IN_SOURCE",
    "UNKNOWN",
)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Fidelite de ce qui est imprime — 1SPE",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"> {payload['why_geometry_could_not_see_this']}",
        "",
        f"> {payload['this_compares_it_does_not_blacklist']}",
        "",
        f"> {payload['what_a_variant_withholds_is_declared_not_guessed']}",
        "",
        f"> {payload['only_what_is_composed_as_a_program_is_compared']}",
        "",
        f"> {payload['indentation_is_not_what_is_checked']}",
        "",
        f"> {payload['the_vocabulary_is_read_not_listed']}",
        "",
        f"> {payload['french_typography_keeps_its_quotes']}",
        "",
        "## Metriques",
        "",
        "| Metrique | Valeur |",
        "|---|---:|",
    ]
    for name, value in payload["summary"].items():
        lines.append(f"| `{name}` | {value} |")
    for row in payload["variants"]:
        lines += [
            "",
            f"## Variante `{row['variant']}` — {row['pages']} pages",
            "",
            f"{len(row['faithful'])} programmes sur {row['code_blocks']} "
            "retrouves a l'identique dans la couche texte ; "
            f"{len(row['withheld'])} retenus comme la variante le declare "
            f"(environnements vides : {', '.join(row['emptied_environments']) or 'aucun'}).",
        ]
        if row["unfaithful"]:
            lines += ["", "Programmes infideles :", ""]
            for entry in row["unfaithful"]:
                diagnosis = entry["diagnosis"]
                lines.append(f"- `{entry['origin']}` ({entry['kind']})")
                if diagnosis["matched_prefix"]:
                    lines += [
                        f"  - rupture apres {diagnosis['matched_prefix']} caracteres",
                        f"  - la source dit : `{diagnosis['source_says']}`",
                        f"  - la page dit&nbsp;: `{diagnosis['page_says']}`",
                    ]
                else:
                    lines.append(f"  - {diagnosis['note']}")
        if row["visible_malformed_fragments"]:
            lines += ["", "Fragments de commande visibles :", ""]
            for entry in row["visible_malformed_fragments"]:
                lines.append(
                    f"- page {entry['page']} : `{entry['fragment']}` "
                    f"(sans doute `\\{entry['probably'][0]}`)"
                )
        if row["smart_quote_pages"]:
            lines += ["", "Guillemets typographiques dans du code :", ""]
            for entry in row["smart_quote_pages"]:
                lines.append(f"- page {entry['page']} : {entry['characters']}")
    if payload["source_fragments"]:
        lines += ["", "## Fragments dans les sources", ""]
        for entry in payload["source_fragments"]:
            lines.append(
                f"- `{entry['source']}` ligne {entry['line']} : `{entry['fragment']}`"
            )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    global BUILD, SOURCE_ROOT, MASTER_STEM, JSON_TARGET, MD_TARGET

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ne rien ecrire")
    parser.add_argument(
        "--manual",
        default="1SPE",
        choices=sorted(CANONICAL_MANUALS),
        help="manuel canonique a controler",
    )
    arguments = parser.parse_args(argv)

    # Le manuel n'est repris de la table QUE s'il est demande explicitement :
    # sans cela, `main` ecraserait un reglage pose par l'appelant -- et un
    # manuel miniature monte pour un test se retrouverait a lire les sources
    # du vrai depot.
    if "--manual" in (argv or sys.argv[1:]):
        BUILD, SOURCE_ROOT = CANONICAL_MANUALS[arguments.manual]
        MASTER_STEM = BUILD.name
        JSON_TARGET = ROOT / f"audit/{arguments.manual}_PRINTED_FIDELITY.json"
        MD_TARGET = ROOT / f"audit/{arguments.manual}_PRINTED_FIDELITY.md"

    try:
        payload = build()
    except FidelityError as error:
        print(f"1SPE-PRINTED-FIDELITY-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"ecrit {JSON_TARGET.name} et {MD_TARGET.name}")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    return 1 if any(payload["summary"][name] for name in BLOCKING) else 0


if __name__ == "__main__":
    raise SystemExit(main())
