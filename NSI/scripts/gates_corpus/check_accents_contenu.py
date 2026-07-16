#!/usr/bin/env python3
"""Gate : les mots pedagogiques imprimes conservent leurs accents.

Le controle cible le prose de ``chapitres/`` et du specimen. Il ignore les
commentaires LaTeX, les environnements ``python``, ``console`` et
``codereference``, ainsi que ``\\lstinline`` : des identifiants Python tels que
``donnees`` y sont volontaires. Les arguments de ``\\label``, ``\\ref`` et
``\\pageref`` sont egalement ignores : ce sont des ancres non imprimees.

La liste est volontairement explicite pour etre relisible. Elle couvre les
termes recurrents du manuel : acces, aout, caracteristique, categorie, chaine,
coherence, completude, comprehension, complexite, cree, decroissant,
deballage, deja, donnee, ecrire, egal, eleve, element, entiere, etape, etre,
evenement, formate, general, identite, inferieur, interet, memoire, methode,
necessaire, noeud, numerique, operation, ordonnee, parallele, prealable,
precedent, prerequis, proprietaire, reponse, resultat, sequence, simplifie,
superieur, theorie, tres, verifie, zero, mutabilite et reference.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCAN_PATHS = (ROOT / "chapitres", ROOT / "gabarits" / "specimen.tex")

# Chaque forme est listee avec sa correction, afin que le message soit
# directement actionnable. Les formes au pluriel sont traitees explicitement
# pour conserver une suggestion exacte.
FORBIDDEN_WORDS: dict[str, str] = {
    "acces": "accès",
    "aout": "août",
    "caracteristique": "caractéristique",
    "caracteristiques": "caractéristiques",
    "categorie": "catégorie",
    "categories": "catégories",
    "chaine": "chaîne",
    "chaines": "chaînes",
    "coherence": "cohérence",
    "completude": "complétude",
    "comprehension": "compréhension",
    "complexite": "complexité",
    "complexites": "complexités",
    "cree": "crée",
    "crees": "créés",
    "creee": "créée",
    "creees": "créées",
    "deballage": "déballage",
    "decroissant": "décroissant",
    "decroissante": "décroissante",
    "deja": "déjà",
    "donnee": "donnée",
    "donnees": "données",
    "ecrire": "écrire",
    "ecrit": "écrit",
    "ecrite": "écrite",
    "egal": "égal",
    "egale": "égale",
    "egaux": "égaux",
    "eleve": "élève",
    "eleves": "élèves",
    "element": "élément",
    "elements": "éléments",
    "entiere": "entière",
    "entieres": "entières",
    "etape": "étape",
    "etapes": "étapes",
    "etre": "être",
    "evenement": "événement",
    "evenements": "événements",
    "formate": "formaté",
    "formatee": "formatée",
    "general": "général",
    "generale": "générale",
    "identite": "identité",
    "inferieur": "inférieur",
    "inferieure": "inférieure",
    "interet": "intérêt",
    "memoire": "mémoire",
    "methodes": "méthodes",
    "methode": "méthode",
    "mutabilite": "mutabilité",
    "necessaire": "nécessaire",
    "necessaires": "nécessaires",
    "noeud": "nœud",
    "noeuds": "nœuds",
    "numerique": "numérique",
    "numeriques": "numériques",
    "operation": "opération",
    "operations": "opérations",
    "ordonnee": "ordonnée",
    "ordonnees": "ordonnées",
    "parallele": "parallèle",
    "prealable": "préalable",
    "precedent": "précédent",
    "precedente": "précédente",
    "prerequis": "prérequis",
    "proprietaire": "propriétaire",
    "reponse": "réponse",
    "reponses": "réponses",
    "reference": "référence",
    "references": "références",
    "resultat": "résultat",
    "resultats": "résultats",
    "sequence": "séquence",
    "sequences": "séquences",
    "simplifie": "simplifié",
    "superieur": "supérieur",
    "superieure": "supérieure",
    "superieurs": "supérieurs",
    "superieures": "supérieures",
    "theorie": "théorie",
    "tres": "très",
    "verifie": "vérifie",
    "verifiee": "vérifiée",
    "verifiees": "vérifiées",
    "zero": "zéro",
}

WORD_RE = re.compile(
    r"(?<![A-Za-zÀ-ÖØ-öø-ÿ_])(?:"
    + "|".join(re.escape(word) for word in sorted(FORBIDDEN_WORDS, key=len, reverse=True))
    + r")(?![A-Za-zÀ-ÖØ-öø-ÿ_])",
    re.IGNORECASE,
)
ENVIRONMENT_RE = re.compile(
    r"\\begin\{(?P<environment>python|console|codereference)\}.*?"
    r"\\end\{(?P=environment)\}",
    re.IGNORECASE | re.DOTALL,
)
LSTINLINE_RE = re.compile(
    r"\\lstinline(?:\[[^\]\n]*\])?(?P<delimiter>[^\sA-Za-z{}])"
    r".*?(?<!\\)(?P=delimiter)",
    re.DOTALL,
)
SENTENCE_INITIAL_DEFINITION_RE = re.compile(
    r"(?:(?<=^)|(?<=[.!?])\s*|"
    r"\\(?:textbf|textit|textsc|emph)\{\s*|\\par\s+|"
    r"\\item(?:\s*\[[^\]\n]*\])?\s+)"
    r"definition(?![A-Za-zÀ-ÖØ-öø-ÿ_])",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class AccentViolation:
    word: str
    replacement: str
    line: int
    column: int


def _mask(text: str, start: int, end: int) -> str:
    """Remplace une zone ignoree par des espaces en preservant les retours ligne."""
    return text[:start] + "".join("\n" if char == "\n" else " " for char in text[start:end]) + text[end:]


def _strip_comments(text: str) -> str:
    """Masque les commentaires LaTeX introduits par un pourcent non echappe."""
    masked = list(text)
    index = 0
    while index < len(text):
        if text[index] != "%":
            index += 1
            continue
        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and text[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2:
            index += 1
            continue
        end = text.find("\n", index)
        if end == -1:
            end = len(text)
        for comment_index in range(index, end):
            masked[comment_index] = " "
        index = end
    return "".join(masked)


def _braced_argument_spans(text: str, command: str) -> list[tuple[int, int]]:
    """Trouve les arguments entre accolades des commandes a ignorer."""
    spans: list[tuple[int, int]] = []
    search_from = 0
    while (start := text.find(command, search_from)) != -1:
        cursor = start + len(command)
        if command == r"\lstinline" and cursor < len(text) and text[cursor] == "[":
            option_end = text.find("]", cursor + 1)
            if option_end == -1:
                search_from = cursor
                continue
            cursor = option_end + 1
        if cursor >= len(text) or text[cursor] != "{":
            search_from = cursor
            continue
        depth = 0
        end = cursor
        while end < len(text):
            if text[end] == "\\":
                end += 2
                continue
            if text[end] == "{":
                depth += 1
            elif text[end] == "}":
                depth -= 1
                if depth == 0:
                    spans.append((start, end + 1))
                    end += 1
                    break
            end += 1
        search_from = end
    return spans


def prose_only(text: str) -> str:
    """Retourne le texte imprimable, les zones de code et commentaires masques."""
    # Cette neutralisation doit preceder la recherche d'environnements : un
    # marqueur \begin dans un commentaire ou un \lstinline ne peut jamais
    # ouvrir un environnement qui masquerait le prose visible qui suit.
    text = _strip_comments(text)
    ignored_argument_spans: list[tuple[int, int]] = []
    for command in (r"\lstinline", r"\label", r"\ref", r"\pageref"):
        ignored_argument_spans.extend(_braced_argument_spans(text, command))
    for start, end in reversed(sorted(ignored_argument_spans)):
        text = _mask(text, start, end)
    for match in reversed(list(LSTINLINE_RE.finditer(text))):
        text = _mask(text, match.start(), match.end())
    for match in reversed(list(ENVIRONMENT_RE.finditer(text))):
        text = _mask(text, match.start(), match.end())
    return text


def _position(text: str, offset: int) -> tuple[int, int]:
    line = text.count("\n", 0, offset) + 1
    previous_newline = text.rfind("\n", 0, offset)
    return line, offset - previous_newline


def find_violations(text: str) -> list[AccentViolation]:
    """Liste les mots interdits dans la seule partie imprimee de ``text``."""
    prose = prose_only(text)
    violations: list[AccentViolation] = []
    for match in WORD_RE.finditer(prose):
        word = match.group(0)
        line, column = _position(prose, match.start())
        violations.append(
            AccentViolation(word, FORBIDDEN_WORDS[word.lower()], line, column)
        )
    for match in SENTENCE_INITIAL_DEFINITION_RE.finditer(prose):
        word_start = match.end() - len("Definition")
        line, column = _position(prose, word_start)
        word = prose[word_start:match.end()]
        violations.append(AccentViolation(word, "Définition", line, column))
    return sorted(violations, key=lambda hit: (hit.line, hit.column))


def iter_tex_sources() -> list[Path]:
    """Retourne uniquement le corpus et le specimen demandes par la charte."""
    sources: list[Path] = []
    chapters = SCAN_PATHS[0]
    if chapters.exists():
        sources.extend(sorted(chapters.rglob("*.tex")))
    specimen = SCAN_PATHS[1]
    if specimen.exists():
        sources.append(specimen)
    return sources


def main() -> int:
    errors: list[str] = []
    checked = 0
    for path in iter_tex_sources():
        checked += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        for hit in find_violations(text):
            errors.append(
                f"  {path.relative_to(ROOT)}:{hit.line}:{hit.column}: "
                f"'{hit.word}' -> '{hit.replacement}'"
            )

    if errors:
        print("ROUGE -- mots pedagogiques sans accent detectes :")
        for error in errors:
            print(error)
        return 1

    print(f"VERT -- accents du contenu verifies dans {checked} fichiers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
