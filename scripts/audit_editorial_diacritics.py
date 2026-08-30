#!/usr/bin/env python3
"""Dette editoriale des diacritiques, mesuree en contexte.

Accentuer aveuglement est un defaut, pas une correction : `capacites`,
`duree`, `competences` sont des CLES de la ligne META, `corrige_tex` un nom de
champ, et plusieurs mots francais existent dans les deux graphies -- `corrige`
(present) et `corrige` accentue (participe), `des` (article) et `des` accentue
(cubes), `passe`, `calcule`, `utilise`, `applique`. Un remplacement mecanique
corromprait du code ou changerait le sens.

Cet auditeur ne signale donc que ce qu'il peut justifier :

* il retire d'abord du texte tout ce qui n'est pas de la prose : ligne META,
  bloc BEGIN-VERIFY, mode mathematique, environnements de code, arguments de
  macros structurelles, noms de macros et identifiants d'objets ;
* il ne cherche ensuite que des formes NON AMBIGUES, c'est-a-dire celles dont
  la graphie sans accent n'est pas un mot francais.

Ce qui reste ambigu n'est jamais corrige automatiquement : il est compte a
part, pour arbitrage.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "Mathematiques" / "manuel-maths" / "chapitres"
NSI_CHAPTERS = ROOT / "NSI" / "chapitres"

#: Formes dont la graphie sans accent n'est pas un mot francais : les corriger
#: ne peut pas changer le sens. La cle est la forme fautive, la valeur la forme
#: correcte.
UNAMBIGUOUS: dict[str, str] = {
    "algebrique": "algébrique",
    "algebriques": "algébriques",
    "apres": "après",
    "carree": "carrée",
    "coherence": "cohérence",
    "consequent": "conséquent",
    "decimale": "décimale",
    "decimales": "décimales",
    "decroissance": "décroissance",
    "decroissante": "décroissante",
    "decroissantes": "décroissantes",
    "definie": "définie",
    "definies": "définies",
    "definition": "définition",
    "definitions": "définitions",
    "demonstration": "démonstration",
    "demonstrations": "démonstrations",
    "dependance": "dépendance",
    "derivable": "dérivable",
    "derivee": "dérivée",
    "derivees": "dérivées",
    "derivation": "dérivation",
    "deuxieme": "deuxième",
    "different": "différent",
    "differente": "différente",
    "differentes": "différentes",
    "differents": "différents",
    "echantillon": "échantillon",
    "echantillons": "échantillons",
    "egal": "égal",
    "egale": "égale",
    "egales": "égales",
    "egalite": "égalité",
    "egaux": "égaux",
    "elementaire": "élémentaire",
    "elementaires": "élémentaires",
    "energie": "énergie",
    "enonce": "énoncé",
    "enonces": "énoncés",
    "equation": "équation",
    "equations": "équations",
    "equilibre": "équilibré",
    "equivalent": "équivalent",
    "equivalente": "équivalente",
    "esperance": "espérance",
    "etape": "étape",
    "etapes": "étapes",
    "evenement": "événement",
    "evenements": "événements",
    "experience": "expérience",
    "experimentation": "expérimentation",
    "geometrique": "géométrique",
    "geometriques": "géométriques",
    "immediatement": "immédiatement",
    "inegalite": "inégalité",
    "inegalites": "inégalités",
    "interet": "intérêt",
    "lineaire": "linéaire",
    "linearite": "linéarité",
    "mediane": "médiane",
    "meme": "même",
    "memes": "mêmes",
    "methode": "méthode",
    "modelisation": "modélisation",
    "modelise": "modélisé",
    "modelisee": "modélisée",
    "necessaire": "nécessaire",
    "negatif": "négatif",
    "negative": "négative",
    "negatives": "négatives",
    "negatifs": "négatifs",
    "numerique": "numérique",
    "numeriques": "numériques",
    "parametre": "paramètre",
    "parametres": "paramètres",
    "particuliere": "particulière",
    "periode": "période",
    "phenomene": "phénomène",
    "precedent": "précédent",
    "precedente": "précédente",
    "precis": "précis",
    "precise": "précise",
    "premiere": "première",
    "probabilite": "probabilité",
    "probabilites": "probabilités",
    "problematique": "problématique",
    "proprietes": "propriétés",
    "propriete": "propriété",
    "reel": "réel",
    "reelle": "réelle",
    "reelles": "réelles",
    "reels": "réels",
    "reciproque": "réciproque",
    "reference": "référence",
    "regle": "règle",
    "regles": "règles",
    "remediation": "remédiation",
    "remediations": "remédiations",
    "represente": "représente",
    "representer": "représenter",
    "representation": "représentation",
    "resolution": "résolution",
    "resoudre": "résoudre",
    "resultat": "résultat",
    "resultats": "résultats",
    "scenario": "scénario",
    "strategie": "stratégie",
    "systeme": "système",
    "systemes": "systèmes",
    "theoreme": "théorème",
    "troisieme": "troisième",
    "verifier": "vérifier",
    "verifie": "vérifie",
    "verification": "vérification",
    "defini": "défini",
    "definis": "définis",
    "definit": "définit",
    "differentielle": "différentielle",
    "differentielles": "différentielles",
    "annee": "année",
    "annees": "années",
    "arete": "arête",
    "aretes": "arêtes",
    "arithmetique": "arithmétique",
    "boite": "boîte",
    "boites": "boîtes",
    "capacite": "capacité",
    "completer": "compléter",
    "concavite": "concavité",
    "controle": "contrôle",
    "controler": "contrôler",
    "controles": "contrôles",
    "convexite": "convexité",
    "coordonnee": "coordonnée",
    "coordonnees": "coordonnées",
    "cout": "coût",
    "couts": "coûts",
    "decroit": "décroît",
    "degre": "degré",
    "degres": "degrés",
    "demontre": "démontré",
    "demontrer": "démontrer",
    "determine": "déterminé",
    "determinee": "déterminée",
    "determiner": "déterminer",
    "element": "élément",
    "elements": "éléments",
    "etude": "étude",
    "etudes": "études",
    "extremite": "extrémité",
    "extremites": "extrémités",
    "hypothese": "hypothèse",
    "hypotheses": "hypothèses",
    "independance": "indépendance",
    "independant": "indépendant",
    "independante": "indépendante",
    "independantes": "indépendantes",
    "independants": "indépendants",
    "integrale": "intégrale",
    "integrales": "intégrales",
    "interpretation": "interprétation",
    "interpreter": "interpréter",
    "majore": "majoré",
    "majoree": "majorée",
    "materiel": "matériel",
    "materielle": "matérielle",
    "minore": "minoré",
    "minoree": "minorée",
    "operation": "opération",
    "operations": "opérations",
    "ordonnee": "ordonnée",
    "ordonnees": "ordonnées",
    "periodicite": "périodicité",
    "piege": "piège",
    "pieges": "pièges",
    "polynome": "polynôme",
    "polynomes": "polynômes",
    "priorite": "priorité",
    "quantite": "quantité",
    "quantites": "quantités",
    "recurrence": "récurrence",
    "succes": "succès",
    "temperature": "température",
    "trigonometrie": "trigonométrie",
    "trigonometrique": "trigonométrique",
    "trigonometriques": "trigonométriques",
    "caracterisation": "caractérisation",
    "caracterise": "caractérise",
    "caracteriser": "caractériser",
    "decrit": "décrit",
    "deduire": "déduire",
    "denominateur": "dénominateur",
    "deriver": "dériver",
    "disparait": "disparaît",
    "divisee": "divisée",
    "ecrire": "écrire",
    "ete": "été",
    "etre": "être",
    "etudier": "étudier",
    "evaluation": "évaluation",
    "exterieur": "extérieur",
    "inequation": "inéquation",
    "inequations": "inéquations",
    "modele": "modèle",
    "modeles": "modèles",
    "multipliee": "multipliée",
    "numerateur": "numérateur",
    "positivite": "positivité",
    "representative": "représentative",
    "tres": "très",
    "trinome": "trinôme",
    "unite": "unité",
    "unites": "unités",
}

#: Formes ambigues isolees, mais decidables dans une locution : apres l'article
#: elide, `eleve` est le nom `eleve` accentue en e-grave, jamais le participe.
CONTEXTUAL: dict[str, str] = {
    "l'eleve": "l'élève",
    "L'eleve": "L'élève",
    "un eleve": "un élève",
    "les eleves": "les élèves",
}

#: Formes que l'on ne corrige JAMAIS automatiquement : les deux graphies sont
#: des mots francais et seul le contexte tranche.
AMBIGUOUS = frozenset(
    {
        "applique",
        "calcule",
        "conserve",
        "corrige",
        "des",
        "donne",
        "eleve",
        "etudie",
        "factorise",
        "multiplie",
        "note",
        "passe",
        "pose",
        "resume",
        "simplifie",
        "trace",
        "utilise",
        "augmente",
        "cherche",
        "compte",
        "demande",
        "derive",
        "divise",
        "fixe",
        "forme",
        "indique",
        "inverse",
        "justifie",
        "montre",
        "observe",
        "oublie",
        "remplace",
        "situe",
        "suppose",
        "teste",
    }
)

#: Ce qui n'est pas de la prose et ne doit jamais etre touche.
_META_LINE = re.compile(r"^%\s*META:.*$", re.M)
_VERIFY_BLOCK = re.compile(r"^% BEGIN-VERIFY.*?^% END-VERIFY\s*$", re.M | re.S)
_COMMENT = re.compile(r"^%.*$", re.M)
_DISPLAY_MATH = re.compile(r"\\\[.*?\\\]", re.S)
_INLINE_MATH = re.compile(r"\$[^$]*\$")
#: Environnements de code. Les manuels NSI en emploient d'autres que les
#: manuels de mathematiques : accentuer un identifiant Python ou une requete
#: SQL casserait le code publie.
_CODE_ENV = re.compile(
    r"\\begin\{(verbatim|lstlisting|minted|algorithme|python|sql|console|pseudocode)\}.*?"
    r"\\end\{\1\}",
    re.S,
)
_CODE_MACRO = re.compile(r"\\(code|texttt|verb|url|href|lstinline)\s*\{[^{}]*\}")
#: \verb et \lstinline acceptent un delimiteur libre : \lstinline|code|.
#: Sans cette forme, un identifiant Python inline etait lu comme de la prose.
_CODE_DELIMITED = re.compile(r"\\(?:verb|lstinline)\s*([^A-Za-z0-9\s{])(.*?)\1", re.S)
_STRUCTURAL_MACRO = re.compile(r"\\(label|ref|input|include|includegraphics)\s*\{[^{}]*\}")
#: `\begin{corrige}` nomme un environnement, pas un participe passe.
_ENVIRONMENT_NAME = re.compile(r"\\(begin|end)\s*\{[^{}]*\}")
_MACRO_NAME = re.compile(r"\\[a-zA-Z@]+")
_OBJECT_ID = re.compile(r"\b[0-9A-Z][0-9A-Z-]{4,}\b")


def prose_only(text: str) -> str:
    """Retire du source tout ce qui n'est pas de la prose francaise."""

    for pattern in (
        _VERIFY_BLOCK,
        _META_LINE,
        _CODE_ENV,
        _DISPLAY_MATH,
        _INLINE_MATH,
        _CODE_MACRO,
        _CODE_DELIMITED,
        _STRUCTURAL_MACRO,
        _COMMENT,
        _ENVIRONMENT_NAME,
        _OBJECT_ID,
    ):
        text = pattern.sub(" ", text)
    return _MACRO_NAME.sub(" ", text)


assert all(
    wrong != right for wrong, right in UNAMBIGUOUS.items()
), "une entree identite signalerait une faute inexistante"


def _strip(word: str) -> str:
    decomposed = unicodedata.normalize("NFD", word)
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def scan_text(text: str) -> tuple[Counter, Counter]:
    """Occurrences fautives non ambigues, et occurrences ambigues."""

    prose = prose_only(text)
    wrong: Counter = Counter()
    ambiguous: Counter = Counter()
    for word in re.findall(r"[A-Za-zÀ-ÿ]{3,}", prose):
        lowered = word.lower()
        if lowered != _strip(lowered):
            continue
        if lowered in AMBIGUOUS:
            ambiguous[lowered] += 1
        elif lowered in UNAMBIGUOUS:
            wrong[lowered] += 1
    return wrong, ambiguous


#: Repertoires hors perimetre PUBLIE. `_harvest` contient des candidats de
#: recuperation qu'aucun assembleur ne reference : les corriger changerait des
#: fichiers morts et la dette publiee n'en dependrait pas.
UNPUBLISHED_DIRECTORIES = ("_harvest",)


def is_published(path: Path) -> bool:
    return not any(part in UNPUBLISHED_DIRECTORIES for part in path.parts)


def scan_paths(paths: list[Path]) -> dict[str, Any]:
    paths = [path for path in paths if is_published(path)]
    wrong: Counter = Counter()
    ambiguous: Counter = Counter()
    by_file: dict[str, dict[str, int]] = defaultdict(dict)
    for path in paths:
        found, unsure = scan_text(path.read_text(encoding="utf-8", errors="replace"))
        if found:
            by_file[path.relative_to(ROOT).as_posix()] = dict(found)
        wrong.update(found)
        ambiguous.update(unsure)
    return {
        "scanned_files": len(paths),
        "UNAMBIGUOUS_DIACRITICS_DEBT": sum(wrong.values()),
        "distinct_forms": len(wrong),
        "AMBIGUOUS_REQUIRING_CONTEXT": sum(ambiguous.values()),
        "ambiguous_forms": dict(sorted(ambiguous.items())),
        "forms": dict(sorted(wrong.items(), key=lambda item: (-item[1], item[0]))),
        "files": dict(sorted(by_file.items())),
    }


def chapter_paths(chapter: str) -> list[Path]:
    for root in (CHAPTERS, NSI_CHAPTERS):
        directory = root / chapter
        if directory.is_dir():
            return sorted(directory.rglob("*.tex"))
    raise SystemExit(f"chapitre inconnu: {chapter}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapter", action="append", help="limiter a un chapitre")
    parser.add_argument("--out", help="ecrire le rapport JSON")
    parser.add_argument("--fix", action="store_true", help="corriger les formes non ambigues")
    args = parser.parse_args(argv)

    if args.chapter:
        paths = [path for chapter in args.chapter for path in chapter_paths(chapter)]
    else:
        paths = sorted(CHAPTERS.rglob("*.tex")) + sorted(NSI_CHAPTERS.rglob("*.tex"))

    if args.fix:
        changed = 0
        for path in paths:
            text = path.read_text(encoding="utf-8")
            updated = text
            for phrase, corrected in CONTEXTUAL.items():
                updated = _replace_in_prose(updated, phrase, corrected)
            for wrong_form, right_form in UNAMBIGUOUS.items():
                if wrong_form == right_form:
                    continue
                # minuscules, Capitalise, et CAPITALES : le manuel emploie les
                # trois, par exemple "un MEME intervalle".
                for candidate, replacement in (
                    (wrong_form, right_form),
                    (wrong_form.capitalize(), right_form.capitalize()),
                    (wrong_form.upper(), right_form.upper()),
                ):
                    updated = _replace_in_prose(updated, candidate, replacement)
            if updated != text:
                path.write_text(updated, encoding="utf-8")
                changed += 1
        print(f"fichiers corriges: {changed}")
        return 0

    report = scan_paths(paths)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
    print(
        f"fichiers {report['scanned_files']} | dette non ambigue "
        f"{report['UNAMBIGUOUS_DIACRITICS_DEBT']} sur {report['distinct_forms']} formes "
        f"| ambigus a arbitrer {report['AMBIGUOUS_REQUIRING_CONTEXT']}"
    )
    return 0


def _replace_in_prose(text: str, wrong_form: str, right_form: str) -> str:
    """Remplace `wrong_form` uniquement hors META, math, code et macros."""

    protected: list[str] = []

    def _hide(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"\x00{len(protected) - 1}\x00"

    guarded = text
    for pattern in (
        _VERIFY_BLOCK,
        _META_LINE,
        _CODE_ENV,
        _DISPLAY_MATH,
        _INLINE_MATH,
        _CODE_MACRO,
        _CODE_DELIMITED,
        _STRUCTURAL_MACRO,
        _ENVIRONMENT_NAME,
        # Un commentaire LaTeX n'est pas compte par le scanner : le protéger
        # ici garde la mesure et la correction sur le meme perimetre.
        _COMMENT,
        # Un nom de macro N'EST PAS de la prose. Sans cette protection, la
        # correction produit \theoreme accentue, \definition accentue,
        # \propriete accentue : des macros qui n'existent pas et un manuel
        # qui ne compile plus.
        _MACRO_NAME,
        _OBJECT_ID,
    ):
        guarded = pattern.sub(_hide, guarded)
    guarded = re.sub(rf"\b{re.escape(wrong_form)}\b", right_form, guarded)
    for index, original in enumerate(protected):
        guarded = guarded.replace(f"\x00{index}\x00", original)
    return guarded


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
