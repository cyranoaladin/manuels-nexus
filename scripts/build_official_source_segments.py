#!/usr/bin/env python3
"""Extract reviewed official-programme segments without atom dependencies."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pdfplumber
import yaml
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
AUTHORITY_PATH = AUDIT / "OFFICIAL_PROGRAM_AUTHORITY_2026_2027.yaml"
JSON_TARGET = AUDIT / "OFFICIAL_SOURCE_SEGMENTS_2026_2027.json"
MD_TARGET = AUDIT / "OFFICIAL_SOURCE_SEGMENTS_2026_2027.md"
MANUAL_ORDER = ("1SPE", "TSPE", "TCOMPL", "TEXPERTES", "1NSI", "TNSI")
CANDIDATE_MATCH_MINIMUM = 0.45

STOP_WORDS = {
    "a", "au", "aux", "avec", "ce", "ces", "comme", "d", "dans", "de",
    "des", "du", "en", "est", "et", "l", "la", "le", "les", "ne", "ou",
    "par", "pas", "plus", "pour", "que", "qui", "sa", "sans", "se", "ses",
    "son", "sont", "sur", "un", "une",
}

LIMITATION_MARKERS = (
    "aucune connaissance", "n est pas exigible", "ne sont pas exigibles",
    "n est pas un attendu", "ne donne pas lieu", "on se limite", "se limite a",
    "n est pas aborde", "ne sont pas abordes", "n est cependant pas un objectif",
    "il ne s agit pas", "sans formalisme theorique",
)

# Reviewed source→atom links for terse formula/table labels whose lexical
# overlap is necessarily weak.  Keys are literal normalisations of extracted
# official source items; they do not create source population.
SOURCE_MAPPING_OVERRIDES: dict[tuple[str, str], tuple[str, ...]] = {
    ("1SPE", "appliquer un taux d evolution pour calculer une valeur finale ou initiale"): ("1SPE-ATOM-073",),
    ("1SPE", "calculer le taux d evolution equivalent a plusieurs evolutions successives"): ("1SPE-ATOM-073",),
    ("1SPE", "proposer modeliser une situation permettant de generer une suite de nombres determiner une relation explicite ou une relation de recurrence pour une suite definie par un motif geometrique par une question de denombrement"): ("1SPE-ATOM-006",),
    ("1SPE", "transformation de l expression m b a m"): ("1SPE-ATOM-051",),
    ("TSPE", "principe additif nombre d elements d une reunion d ensembles deux a deux disjoints"): ("TSPE-ATOM-005",),
    ("TSPE", "nombre des parties d un ensemble a n elements lien avec les n uplets de 0 1 les mots de longueur n sur un alphabet a deux elements les chemins dans un arbre les issues dans une succession de n epreuves de bernoulli"): ("TSPE-ATOM-005",),
    ("TSPE", "droites de l espace vecteurs directeurs d une droite vecteurs colineaires"): ("TSPE-ATOM-009", "TSPE-ATOM-018"),
    ("TSPE", "plans de l espace direction d un plan de l espace"): ("TSPE-ATOM-009", "TSPE-ATOM-019"),
    ("TSPE", "comportement d une suite geometrique qn ou q est un nombre reel"): ("TSPE-ATOM-024", "TSPE-ATOM-028"),
    ("TSPE", "recherche de seuils 1 5"): ("TSPE-ATOM-024",),
    ("TSPE", "recherche de valeurs approchees de e 2 ln 2 etc 2"): ("TSPE-ATOM-024",),
    ("TSPE", "simulation de la planche de galton"): ("TSPE-ATOM-076",),
    ("TSPE", "manipuler des elements d une liste ajouter supprimer et leurs indices"): ("TSPE-ATOM-088",),
    ("TCOMPL", "theoreme des valeurs intermediaires admis cas des fonctions strictement monotones"): ("TCOMPL-ATOM-039",),
    ("TCOMPL", "approximation d une integrale par la methode des rectangles"): ("TCOMPL-ATOM-055",),
    ("TCOMPL", "schema de bernoulli representation par un arbre"): ("TCOMPL-ATOM-012", "TCOMPL-ATOM-023"),
    ("TCOMPL", "dans le cadre de la resolution de probleme utiliser l esperance des lois precedentes"): ("TCOMPL-ATOM-017",),
    ("TCOMPL", "simulation d une variable de bernoulli ou d un lancer de de ou d une variable uniforme sur un ensemble fini a partir d une variable aleatoire de loi uniforme sur 0 1"): ("TCOMPL-ATOM-016", "TCOMPL-ATOM-055"),
    ("TCOMPL", "dans le cadre d une resolution de probleme utiliser un ajustement pour interpoler extrapoler"): ("TCOMPL-ATOM-010",),
    ("TEXPERTES", "arguments d un nombre complexe non nul interpretation geometrique"): ("TEXPERTES-ATOM-004",),
    ("TEXPERTES", "formules d euler cos 2 ei e i sin 2i ei e i"): ("TEXPERTES-ATOM-009",),
    ("TEXPERTES", "congruences dans z compatibilite des congruences avec les operations"): ("TEXPERTES-ATOM-017",),
}

SOURCE_ANCHOR_MAPPING_OVERRIDES: dict[tuple[str, str], tuple[str, ...]] = {
    ("1NSI", "pdf-page:2;lines:28-31"): ("1NSI-ATOM-052",),
    ("TNSI", "pdf-page:2;lines:28-31"): ("TNSI-ATOM-060",),
}

KNOWN_DUPLICATE_GROUPS = (
    {
        "manual": "TCOMPL",
        "atom_ids": ("TCOMPL-ATOM-003", "TCOMPL-ATOM-022"),
        "official_source_anchor": "lines:665-668",
        "reason": "same integration capacity duplicated between theme-derived and second-volet atoms",
    },
    {
        "manual": "TCOMPL",
        "atom_ids": ("TCOMPL-ATOM-007", "TCOMPL-ATOM-043"),
        "official_source_anchor": "lines:774-776",
        "reason": "same two-variable-statistics capacity duplicated between theme-derived and second-volet atoms",
    },
    {
        "manual": "TCOMPL",
        "atom_ids": ("TCOMPL-ATOM-021", "TCOMPL-ATOM-042"),
        "official_source_anchor": "lines:644",
        "reason": "same convexity capacity duplicated between theme-derived and second-volet atoms",
    },
)

KNOWN_FALSE_MANDATORY_ATOMS = (
    {"atom_id": "TCOMPL-ATOM-017", "source_anchor": "lines:735-739", "reason": "Démonstration possible, not exigible"},
    {"atom_id": "TCOMPL-ATOM-018", "source_anchor": "lines:323-331", "reason": "Problèmes possibles in first thematic volet"},
    {"atom_id": "TCOMPL-ATOM-019", "source_anchor": "lines:323-331", "reason": "Problèmes possibles in first thematic volet"},
    {"atom_id": "TCOMPL-ATOM-020", "source_anchor": "lines:323-331", "reason": "Problèmes possibles in first thematic volet"},
    {"atom_id": "TCOMPL-ATOM-026", "source_anchor": "lines:356-361", "reason": "Problèmes possibles in first thematic volet"},
    {"atom_id": "TCOMPL-ATOM-027", "source_anchor": "lines:356-361", "reason": "Problèmes possibles in first thematic volet"},
    {"atom_id": "TNSI-ATOM-025", "source_anchor": "pdf-page:6;table:1;row:1;column:commentaires;item:1;part:guidance", "reason": "ORDER BY is only in the official Commentaires column (implementation guidance)"},
)

KNOWN_WRONG_OBLIGATION_TYPES = (
    {
        "atom_id": "1NSI-ATOM-052",
        "current_type": "EXPLICIT_LIMITATION",
        "correct_type": "OTHER_OFFICIAL",
        "source_anchor": "pdf-page:2;lines:28-31",
        "reason": "the mandatory one-quarter project quota is an organisational requirement, not a limitation",
    },
    {
        "atom_id": "1NSI-ATOM-025",
        "current_type": "MANDATORY_CAPACITY",
        "correct_type": "IMPLEMENTATION_GUIDANCE",
        "source_anchor": "pdf-page:6;table:1;row:7;column:commentaires;item:1",
        "reason": "the item occurs in the official Commentaires column",
    },
)

KNOWN_AMBIGUOUS_OBLIGATIONS = (
    {
        "atom_id": "1NSI-ATOM-025",
        "source_anchor": "pdf-page:6;table:1;row:7;column:commentaires;item:1",
        "reason": "Commentaires-column placement suggests guidance, but the imperative 'Discuter…' requires an explicit mandatory_for_coverage decision",
    },
)

KNOWN_COMPOUND_ATOMS = (
    {
        "atom_ids": ("1NSI-ATOM-003",),
        "capacity_count": 2,
        "reason": "bit-count evaluation and two's-complement conversion are separate expected capacities",
    },
    {
        "atom_ids": ("1NSI-ATOM-006",),
        "capacity_count": 2,
        "reason": "identify encoding-system value and convert a text file are separate expected capacities",
    },
    {
        "atom_ids": ("1NSI-ATOM-009", "1NSI-ATOM-010", "1NSI-ATOM-011"),
        "capacity_count": 6,
        "reason": "six table/list/dictionary expected capacities are compressed into three atoms",
    },
)

KNOWN_MISLEADING_ATOM_WORDING = (
    {
        "atom_id": "1SPE-ATOM-039",
        "source_anchor": "lines:497-501",
        "reason": "only the demonstrations are optional; exp(x+y), positivity and growth themselves are mandatory contents at lines 481-484",
        "required_rewording": "Approfondissements possibles : démonstration de l'unicité, de exp(x+y)=exp(x)exp(y), et de la positivité/croissance stricte",
    },
)



# ---------------------------------------------------------------------------
#  Fractions empilees : rendre a la formule sa structure
# ---------------------------------------------------------------------------

#: Ligne dont le contenu a ete replie dans sa voisine. Elle reste presente pour
#: que les numeros de ligne -- donc les ancres de source -- ne bougent pas.
FOLDED_INTO_NEIGHBOUR = "\x00FOLDED"

#: Un numerateur ou un denominateur isole tient en peu de signes. Au-dela, la
#: ligne raconte quelque chose et n'est pas un etage de fraction.
STACKED_TERM_MAX_LENGTH = 12
#: La ligne de texte doit menager un vide a l'endroit de la barre. Trois
#: espaces suffisent a distinguer ce vide d'une simple separation de mots.
FRACTION_GAP_MIN_WIDTH = 3


def _is_stacked_term(raw: str) -> bool:
    """Un etage de fraction : court, isole, sans ponctuation de phrase."""

    stripped = raw.strip()
    if not stripped or len(stripped) > STACKED_TERM_MAX_LENGTH:
        return False
    if re.match(r"^[\s]*(?:\u2212|\uf0ad|-|\u2022)", raw):
        return False
    # Une phrase se termine ; un etage de fraction, non.
    if stripped.endswith((".", ";", ":", ",")):
        return False
    return not re.search(r"[a-zA-Z\u00e0-\u00ff]{4,}", stripped)


def _column(raw: str) -> int:
    return len(raw) - len(raw.lstrip())


def fold_stacked_fractions(lines: list[str]) -> tuple[list[str], list[dict[str, Any]]]:
    """Recompose les fractions que l'extraction du PDF a mises a plat.

    Le programme officiel ecrit certaines conditions sous forme de fraction.
    Le texte extrait du PDF conserve la disposition, pas la structure : le
    numerateur se retrouve sur la ligne du dessus, le denominateur sur celle du
    dessous, et la ligne de texte garde un blanc a l'endroit de la barre.

        ... d'ecart type sigma. Si m
                                                    2sigma
           designe la moyenne ..., inferieur ou egal a        .
                                                    racine(n)

    Joindre ces lignes dans l'ordre de lecture donne « Si m 2sigma designe ...
    inferieur ou egal a . racine(n) » -- une phrase qui ne veut rien dire et
    qui ne peut pas etre attestee fidele au programme.

    Ce qui identifie la fraction n'est pas devine : c'est l'ALIGNEMENT. Les
    deux etages commencent a la meme colonne, et cette colonne tombe dans un
    blanc de la ligne de texte qu'ils encadrent. Cet alignement EST la barre de
    fraction ; le reconstituer ne reformule rien.

    Les lignes repliees ne sont pas supprimees mais neutralisees : les numeros
    de ligne, donc les ancres de source, restent ceux du document officiel.
    """

    folded = list(lines)
    records: list[dict[str, Any]] = []
    for index in range(1, len(folded) - 1):
        above, middle, below = folded[index - 1], folded[index], folded[index + 1]
        if not (_is_stacked_term(above) and _is_stacked_term(below)):
            continue
        column = _column(above)
        if column != _column(below):
            continue
        gap = next(
            (
                match
                for match in re.finditer(r" {%d,}" % FRACTION_GAP_MIN_WIDTH, middle)
                if match.start() <= column < match.end()
            ),
            None,
        )
        if gap is None:
            continue
        numerator, denominator = above.strip(), below.strip()
        fraction = f"{numerator}/{denominator}"
        folded[index] = (
            middle[: gap.start()].rstrip() + " " + fraction + middle[gap.end() :].lstrip()
        )
        folded[index - 1] = FOLDED_INTO_NEIGHBOUR
        folded[index + 1] = FOLDED_INTO_NEIGHBOUR
        records.append(
            {
                "numerator": numerator,
                "denominator": denominator,
                "fraction": fraction,
                "numerator_line": index,
                "text_line": index + 1,
                "denominator_line": index + 2,
                "shared_column": column,
            }
        )
    return folded, records

# Direct source-review units that the generic rubric/bullet state machine
# cannot infer safely.  The archived authorities are digest-pinned, so exact
# physical line anchors are deterministic.  Each entry records a substantive
# official unit; atom wording and fuzzy matching play no role in population.
REVIEWED_MATH_SOURCE_UNITS: dict[str, tuple[tuple[int, int, str, str, str], ...]] = {
    "1SPE": (
        # Vocabulaire ensembliste et logique.
        (192, 194, "IMPLEMENTATION_GUIDANCE", "NO", "Vocabulaire ensembliste et logique — mise en œuvre transversale"),
        (195, 201, "CONTENTS", "YES", "Vocabulaire ensembliste et logique — connaissances"),
        (203, 203, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — capacités"),
        (204, 204, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — capacités"),
        (205, 205, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — capacités"),
        (206, 206, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — capacités"),
        (207, 207, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — capacités"),
        (208, 208, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — capacités"),
        (209, 210, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — capacités"),
        (211, 211, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — capacités"),
        (212, 213, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — raisonnements"),
        # Automatismes : les intertitres thématiques interrompaient à tort la
        # catégorie après « Évolutions et variations ».
        (268, 268, "AUTOMATISMS", "YES", "Automatismes — calcul numérique et algébrique"),
        (269, 269, "AUTOMATISMS", "YES", "Automatismes — calcul numérique et algébrique"),
        (270, 270, "AUTOMATISMS", "YES", "Automatismes — calcul numérique et algébrique"),
        (273, 273, "AUTOMATISMS", "YES", "Automatismes — fonctions et représentations"),
        (274, 274, "AUTOMATISMS", "YES", "Automatismes — fonctions et représentations"),
        (275, 275, "AUTOMATISMS", "YES", "Automatismes — fonctions et représentations"),
        (276, 276, "AUTOMATISMS", "YES", "Automatismes — fonctions et représentations"),
        (277, 277, "AUTOMATISMS", "YES", "Automatismes — fonctions et représentations"),
        (280, 281, "AUTOMATISMS", "YES", "Automatismes — statistiques"),
        (282, 282, "AUTOMATISMS", "YES", "Automatismes — statistiques"),
        (283, 283, "AUTOMATISMS", "YES", "Automatismes — statistiques"),
        (286, 287, "AUTOMATISMS", "YES", "Automatismes — probabilités"),
        (288, 288, "AUTOMATISMS", "YES", "Automatismes — probabilités"),
        # Dérivation : les intertitres « Point de vue local/global » avaient
        # interrompu à tort la rubrique Contenus.
        (435, 435, "CONTENTS", "YES", "Dérivation — point de vue local"),
        (436, 436, "CONTENTS", "YES", "Dérivation — point de vue local"),
        (437, 438, "CONTENTS", "YES", "Dérivation — point de vue local"),
        (439, 439, "CONTENTS", "YES", "Dérivation — point de vue local"),
        (441, 441, "CONTENTS", "YES", "Dérivation — point de vue global"),
        (442, 442, "CONTENTS", "YES", "Dérivation — point de vue global"),
        (443, 443, "CONTENTS", "YES", "Dérivation — point de vue global"),
        (444, 444, "CONTENTS", "YES", "Dérivation — point de vue global"),
        (445, 445, "CONTENTS", "YES", "Dérivation — point de vue global"),
    ),
    "TSPE": (
        # Objectifs et notions structurantes de combinatoire/dénombrement.
        (204, 205, "EXPECTED_CAPACITIES", "YES", "Algèbre et géométrie — objectifs de combinatoire"),
        (206, 208, "EXPECTED_CAPACITIES", "YES", "Algèbre et géométrie — objectifs de combinatoire"),
        (259, 262, "CONTENTS", "YES", "Combinatoire et dénombrement — notions ensemblistes"),
        # Vocabulaire ensembliste et logique.
        (985, 988, "IMPLEMENTATION_GUIDANCE", "NO", "Vocabulaire ensembliste et logique — mise en œuvre transversale"),
        (989, 995, "CONTENTS", "YES", "Vocabulaire ensembliste et logique — connaissances"),
        (996, 1004, "IMPLEMENTATION_GUIDANCE", "NO", "Vocabulaire ensembliste et logique — articulation avec les fonctions"),
        (1005, 1007, "EXPLICIT_LIMITATIONS", "NO", "Vocabulaire ensembliste et logique — limitation sur le symbole de somme"),
        (1009, 1010, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — capacités"),
        (1011, 1011, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — capacités"),
        (1012, 1013, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — capacités"),
        (1014, 1014, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — capacités"),
        (1015, 1016, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — capacités"),
        (1017, 1017, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — capacités"),
        (1018, 1019, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — capacités"),
        (1020, 1020, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — capacités"),
        (1021, 1021, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — capacités"),
        (1022, 1022, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — capacités"),
        (1023, 1023, "EXPECTED_CAPACITIES", "YES", "Vocabulaire ensembliste et logique — capacités"),
    ),
}

# Peer-reviewed omissions found by reading MENE2602917A from source to atom.
# These anchors must stay unmapped until a dedicated atom represents the
# substantive official item.  In particular, lexical proximity to an atom in
# another chapter/capacity must not turn a real omission into a false green.
KNOWN_UNPARSED_SOURCE_ANCHORS: dict[tuple[str, str], str] = {
    ("1SPE", "lines:486"): "missing atom for the explicit exponential-expression transformation capacity",
    ("1SPE", "lines:488"): "missing atom for the explicit graphing capacity t↦e^(-kt) and t↦e^(kt)",
    ("1SPE", "lines:643-644"): "missing atom for event notation and natural-language/symbolic register conversion",
    ("1SPE", "lines:646"): "missing atom for the explicit capacity to determine a probability law",
    ("1SPE", "lines:657-659"): "missing atom for the mandatory experimentation objective",
    ("1SPE", "lines:660"): "missing atom for simulating a random variable",
    ("1SPE", "lines:661"): "missing atom for reading, understanding and writing the sample-mean function",
    ("1SPE", "lines:662-663"): "missing atom for studying simulated sample-mean distance to expectation",
    ("1SPE", "lines:664-667"): "missing atom for the N-sample 2σ/√n experimentation",
}

for _anchor in (
    "lines:316", "lines:317", "lines:318", "lines:319", "lines:320",
    "lines:321-322", "lines:323", "lines:349", "lines:350", "lines:351",
    "lines:352-354", "lines:355", "lines:356-357", "lines:358-360",
    "lines:361", "lines:390", "lines:391", "lines:494-496",
    "lines:497-498", "lines:499", "lines:500", "lines:501",
    "lines:502-503", "lines:669-672", "lines:673-675",
    "lines:676-677", "lines:708-710", "lines:713-715",
    "lines:719-720", "lines:721", "lines:722-723", "lines:724",
    "lines:725", "lines:726", "lines:876-877", "lines:878-880",
    "lines:881", "lines:882-884",
):
    KNOWN_UNPARSED_SOURCE_ANCHORS[("TSPE", _anchor)] = (
        "mandatory official content is absent as a dedicated atom; an unrelated or capacity-only atom must not mask it"
    )

for _anchor in (
    "lines:343", "lines:368", "lines:369", "lines:437",
    "lines:647", "lines:648", "lines:649", "lines:650", "lines:651-655",
):
    KNOWN_UNPARSED_SOURCE_ANCHORS[("TEXPERTES", _anchor)] = (
        "mandatory official proof/capacity is absent as a dedicated atom; lexical proximity is insufficient"
    )

for _anchor in (
    "lines:167-186",
    "lines:564-566", "lines:567-568", "lines:569-570", "lines:571-572", "lines:573",
    "lines:576-578", "lines:614", "lines:615-616", "lines:617-619",
    "lines:630", "lines:631-633", "lines:634", "lines:635",
    "lines:652-654", "lines:655-656", "lines:657", "lines:658", "lines:659-661", "lines:662-664",
    "lines:666", "lines:667", "lines:668", "lines:669-670",
    "lines:711", "lines:712", "lines:713", "lines:714-715", "lines:716-718", "lines:719-720",
    "lines:722-723", "lines:724", "lines:725-727", "lines:728-729", "lines:730", "lines:731-732", "lines:733-734",
    "lines:747-748", "lines:749", "lines:750-751", "lines:752-753",
):
    KNOWN_UNPARSED_SOURCE_ANCHORS[("TCOMPL", _anchor)] = (
        "mandatory second-volet content/capacity or organisational requirement is absent as a dedicated atom"
    )


@dataclass
class Segment:
    manual: str
    authority_nor: str
    source_path: str
    source_anchor: str
    source_wording_short: str
    classification: str
    mandatory: str
    official_section: str
    atom_ids: list[str]
    candidate_atom_ids: list[str] | None = None
    non_atomic_justification: str | None = None
    best_atom_score: float | None = None


def _sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _composite_digest(paths: Iterable[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: str(item.relative_to(ROOT))):
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _normalise(value: str) -> str:
    value = re.sub(r"[’']", " ", value)
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def _stem(token: str) -> str:
    if len(token) > 4 and token.endswith("s") and not token.endswith("us"):
        return token[:-1]
    return token


def _tokens(value: str) -> frozenset[str]:
    return frozenset(_stem(token) for token in _normalise(value).split() if token not in STOP_WORDS)


def _compact(value: str, limit: int = 520) -> str:
    value = " ".join(value.split())
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def _score(source_wording: str, atom_wording: str) -> float:
    source, atom = _tokens(source_wording), _tokens(atom_wording)
    overlap = len(source & atom)
    source_coverage = overlap / max(1, len(source))
    atom_coverage = overlap / max(1, len(atom))
    jaccard = overlap / max(1, len(source | atom))
    return 0.45 * source_coverage + 0.45 * atom_coverage + 0.10 * jaccard


def _section_compatible(segment: Segment, atom: dict[str, Any]) -> bool:
    """Reject automatic cross-section matches when the source heading is reliable.

    PDF-to-text line wrapping occasionally produces a long prose fragment as a
    pseudo-heading.  Such fragments are not used as section evidence; all
    short, substantive headings must overlap the atom's official section.
    Reviewed overrides remain the only way around this guard.
    """
    if segment.manual in {"1NSI", "TNSI"}:
        return True
    if len(segment.official_section) > 90:
        return True
    generic = {"programme", "analyse", "algebre", "geometrie", "probabilite", "statistique", "mathematique"}
    source_tokens = set(_tokens(segment.official_section)) - generic
    atom_tokens = set(_tokens(atom.get("official_section", ""))) - generic
    if not source_tokens or not atom_tokens:
        return True
    return bool(source_tokens & atom_tokens)


def _type_compatible(segment: Segment, atom: dict[str, Any]) -> bool:
    atom_type = atom["type"]
    exact = {
        "HISTORY_CONTEXT": "HISTORY_CONTEXT",
        "OPTIONAL_EXTENSION": "OPTIONAL_EXTENSIONS",
        "EXPLICIT_LIMITATION": "EXPLICIT_LIMITATIONS",
        "IMPLEMENTATION_GUIDANCE": "IMPLEMENTATION_GUIDANCE",
    }
    if atom_type in exact:
        return segment.classification == exact[atom_type]
    if segment.mandatory == "NO":
        return False
    return segment.classification in {
        "CONTENTS", "EXPECTED_CAPACITIES", "MANDATORY_PROOFS",
        "ALGORITHMS", "AUTOMATISMS", "OTHER_OFFICIAL",
    }


def _authorities() -> dict[str, dict[str, Any]]:
    raw = yaml.safe_load(AUTHORITY_PATH.read_text(encoding="utf-8"))["programme_d_enseignement"]
    result = {("TSPE" if key == "TSPE_2026_2027" else key): value for key, value in raw.items()}
    if set(result) != set(MANUAL_ORDER):
        raise ValueError(f"unexpected authorities: {sorted(result)}")
    return result


def _math_category(line: str) -> tuple[str, str] | None:
    normal = _normalise(line)
    exact: tuple[tuple[str, str, str], ...] = (
        ("contenus", "CONTENTS", "YES"),
        ("contenus associes", "IMPLEMENTATION_GUIDANCE", "NO"),
        ("capacites attendues", "EXPECTED_CAPACITIES", "YES"),
        ("demonstration", "MANDATORY_PROOFS", "YES"),
        ("demonstrations", "MANDATORY_PROOFS", "YES"),
        ("demonstration exigible", "MANDATORY_PROOFS", "YES"),
        ("demonstrations exigibles", "MANDATORY_PROOFS", "YES"),
        ("demonstration possible", "MANDATORY_PROOFS", "NO"),
        ("demonstrations possibles", "MANDATORY_PROOFS", "NO"),
        # The wording is explicitly illustrative ("Exemple(s)"); retain the
        # official segment but do not mechanically turn each suggestion into
        # a mandatory coverage atom.
        ("exemple d algorithme", "ALGORITHMS", "NO"),
        ("exemples d algorithme", "ALGORITHMS", "NO"),
        ("exemples d algorithmes", "ALGORITHMS", "NO"),
        ("experimentations", "ALGORITHMS", "YES"),
        ("approfondissement possible", "OPTIONAL_EXTENSIONS", "NO"),
        ("approfondissements possibles", "OPTIONAL_EXTENSIONS", "NO"),
        ("problemes possibles", "OPTIONAL_EXTENSIONS", "NO"),
        ("histoire des mathematiques", "HISTORY_CONTEXT", "NO"),
        ("competences mathematiques", "CROSS_CUTTING_COMPETENCIES", "NO"),
        ("evaluation des eleves", "IMPLEMENTATION_GUIDANCE", "NO"),
        # TCOMPL's first thematic volet gives possible problem contexts.  The
        # official text says the second volet alone specifies the complete
        # set of contents and expected capacities (lines 167-186).
        ("descriptif", "IMPLEMENTATION_GUIDANCE", "NO"),
        ("automatismes", "AUTOMATISMS", "YES"),
        ("algorithmique et programmation", "ALGORITHMS", "YES"),
        ("notion de liste", "ALGORITHMS", "YES"),
        ("vocabulaire ensembliste et logique", "CROSS_CUTTING_COMPETENCIES", "YES"),
    )
    for label, classification, mandatory in exact:
        if normal == label:
            return classification, mandatory
    return None


def _looks_like_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) > 95 or stripped.endswith((".", ";", ":")):
        return False
    if line[:1].isspace():
        return False
    return not stripped.startswith(("−", "", "-", "•", "", "©"))


def _reviewed_math_segments(
    manual: str,
    authority: dict[str, Any],
    lines: list[str],
) -> list[Segment]:
    """Extract peer-reviewed units missed by the generic rubric state machine.

    The source files are digest-pinned in the authority registry.  Exact line
    anchors are therefore stable evidence, and wording is always reread from
    the official file rather than copied into this extractor.
    """
    relative = authority["local_archival_file"]
    result: list[Segment] = []
    for start, end, classification, mandatory, section in REVIEWED_MATH_SOURCE_UNITS.get(manual, ()):
        if start < 1 or end > len(lines) or start > end:
            raise ValueError(f"invalid reviewed source range for {manual}: {start}-{end}")
        parts: list[str] = []
        for raw in lines[start - 1 : end]:
            if raw == FOLDED_INTO_NEIGHBOUR:
                continue
            stripped = raw.strip().lstrip("\f").strip()
            if not stripped or stripped.startswith("© Ministère"):
                continue
            stripped = re.sub(r"^(?:−||-|•|)\s*", "", stripped)
            parts.append(stripped)
        wording = _compact(" ".join(parts))
        if len(_tokens(wording)) < 2:
            raise ValueError(f"empty reviewed source unit for {manual}: {start}-{end}")
        result.append(
            Segment(
                manual,
                authority["official_ref"],
                relative,
                f"lines:{start}" if start == end else f"lines:{start}-{end}",
                wording,
                classification,
                mandatory,
                section,
                [],
            )
        )
    return result


def _math_anchor_bounds(anchor: str) -> tuple[int, int] | None:
    match = re.fullmatch(r"lines:(\d+)(?:-(\d+))?", anchor)
    if not match:
        return None
    start = int(match.group(1))
    return start, int(match.group(2) or start)


def _math_segment_source_order(segment: Segment) -> tuple[int, int, int, str]:
    bounds = _math_anchor_bounds(segment.source_anchor)
    if bounds is None:
        return (10**9, 10**9, 10**9, segment.classification)
    priority = {
        "IMPLEMENTATION_GUIDANCE": 0,
        "HISTORY_CONTEXT": 1,
        "CONTENTS": 2,
        "EXPECTED_CAPACITIES": 3,
        "MANDATORY_PROOFS": 4,
        "AUTOMATISMS": 5,
        "ALGORITHMS": 6,
        "OPTIONAL_EXTENSIONS": 7,
        "CROSS_CUTTING_COMPETENCIES": 8,
        "OTHER_OFFICIAL": 9,
        "EXPLICIT_LIMITATIONS": 10,
    }
    return bounds[0], priority.get(segment.classification, 99), bounds[1], segment.classification


def _extract_math_segments(manual: str, authority: dict[str, Any]) -> list[Segment]:
    relative = authority["local_archival_file"]
    path = ROOT / relative
    # La disposition du PDF est lue AVANT le decoupage : une fraction empilee
    # doit redevenir une fraction pendant qu'on a encore les colonnes.
    lines, _folds = fold_stacked_fractions(
        path.read_text(encoding="utf-8").split("\n")
    )
    segments: list[Segment] = []
    category: tuple[str, str] | None = None
    section = "Programme"
    current: list[str] = []
    current_start = 0

    def flush(end_line: int) -> None:
        nonlocal current, current_start
        if not current or category is None:
            current = []
            return
        wording = _compact(" ".join(current))
        if wording:
            segments.append(
                Segment(
                    manual, authority["official_ref"], relative,
                    f"lines:{current_start}" if current_start == end_line else f"lines:{current_start}-{end_line}",
                    wording, category[0], category[1], section, [],
                )
            )
        current = []

    for line_number, raw in enumerate(lines, start=1):
        if raw == FOLDED_INTO_NEIGHBOUR:
            # Repliee dans sa voisine : ni contenu, ni coupure. La traiter
            # comme une ligne vide fermerait l'unite en cours et couperait en
            # deux une phrase que le programme officiel ecrit d'un trait.
            continue
        stripped = raw.strip().replace("\uf0ad", "−")
        new_category = _math_category(stripped)
        if new_category is not None:
            flush(line_number - 1)
            category = new_category
            continue
        bullet = re.match(r"^[\s]*(?:−||-)\s+(.*)$", raw)
        if bullet and category is not None:
            flush(line_number - 1)
            current = [bullet.group(1).strip()]
            current_start = line_number
            continue
        if not stripped:
            flush(line_number - 1)
            continue
        if stripped.startswith("© Ministère"):
            flush(line_number - 1)
            continue
        if "enseignement optionnel, classe terminale" in stripped:
            flush(line_number - 1)
            continue
        if _looks_like_heading(raw):
            flush(line_number - 1)
            section = stripped
            # A domain title closes an old bullet category until a regulatory
            # category header establishes the next one.
            if category and _math_category(stripped) is None:
                category = None
            continue
        if current:
            current.append(stripped)
        elif category and category[0] in {"IMPLEMENTATION_GUIDANCE", "HISTORY_CONTEXT", "CONTENTS", "ALGORITHMS"}:
            # Narrative regulatory blocks (notably TCOMPL theme descriptifs)
            # are source units too; they are not inferred from atom wording.
            current = [stripped]
            current_start = line_number
    flush(len(lines))

    segments = [
        segment
        for segment in segments
        if len(_tokens(segment.source_wording_short)) >= 2
        and _normalise(segment.source_wording_short)
        not in {"exemple d algorithme", "exemples d algorithme", "exemples d algorithmes", "integration"}
        and not re.fullmatch(r"\d+ generale", _normalise(segment.source_wording_short))
    ]

    segments.extend(_reviewed_math_segments(manual, authority, lines))

    if manual == "TCOMPL":
        # This source-first organisational requirement sits outside the
        # recurring content/capacity rubrics: all nine themes must be treated,
        # while the listed problems inside each theme remain choices.
        segments.append(
            Segment(
                manual, authority["official_ref"], relative, "lines:167-186",
                "Le programme comporte neuf thèmes d'étude à tous aborder ; le second volet précise l'ensemble des contenus et capacités attendues, les problèmes possibles restant au choix du professeur.",
                "OTHER_OFFICIAL", "YES", "Organisation du programme", [],
            )
        )

    # Limitations can occur in narrative prose rather than a bullet/table.
    for index, raw in enumerate(lines, start=1):
        normal = _normalise(raw)
        if any(marker in normal for marker in LIMITATION_MARKERS):
            wording = _compact(raw)
            already_reviewed = any(
                item.classification == "EXPLICIT_LIMITATIONS"
                and (bounds := _math_anchor_bounds(item.source_anchor)) is not None
                and bounds[0] <= index <= bounds[1]
                for item in segments
            )
            if (wording and not already_reviewed
                    and not any(_normalise(item.source_wording_short) == normal for item in segments)):
                segments.append(
                    Segment(
                        manual, authority["official_ref"], relative, f"lines:{index}", wording,
                        "EXPLICIT_LIMITATIONS", "NO", "Limitation explicite", [],
                    )
                )
    if manual in REVIEWED_MATH_SOURCE_UNITS:
        segments.sort(key=_math_segment_source_order)
    return segments


def _split_cell(cell: str | None) -> list[str]:
    if not cell:
        return []
    compact = " ".join(cell.split())
    if not compact:
        return []
    parts = re.split(r"(?<=[.;!?])\s+(?=[A-ZÀ-ÖØ-ÞÉÈÊÎÔÙÛÇ])", compact)
    return [_compact(part) for part in parts if part.strip()]


def _extract_pdf_cross_cutting(
    manual: str, authority: dict[str, Any], path: Path
) -> list[Segment]:
    relative = authority["local_archival_file"]
    segments: list[Segment] = []
    for page_number, page in enumerate(PdfReader(path).pages, start=1):
        lines = (page.extract_text() or "").splitlines()
        current: list[str] = []
        start = 0
        for line_number, raw in enumerate(lines, start=1):
            bullet = re.match(r"^[\s]*(?:−||[-•])\s+(.*)$", raw)
            if bullet:
                if current:
                    segments.append(
                        Segment(
                            manual, authority["official_ref"], relative,
                            f"pdf-page:{page_number};lines:{start}-{line_number - 1}",
                            _compact(" ".join(current)), "CROSS_CUTTING_COMPETENCIES", "NO",
                            "Préambule — compétences transversales", [],
                        )
                    )
                current, start = [bullet.group(1).strip()], line_number
            elif current and raw.strip():
                current.append(raw.strip())
            elif current:
                segments.append(
                    Segment(
                        manual, authority["official_ref"], relative,
                        f"pdf-page:{page_number};lines:{start}-{line_number - 1}",
                        _compact(" ".join(current)), "CROSS_CUTTING_COMPETENCIES", "NO",
                        "Préambule — compétences transversales", [],
                    )
                )
                current = []
        if current:
            segments.append(
                Segment(
                    manual, authority["official_ref"], relative,
                    f"pdf-page:{page_number};lines:{start}-{len(lines)}",
                    _compact(" ".join(current)), "CROSS_CUTTING_COMPETENCIES", "NO",
                    "Préambule — compétences transversales", [],
                )
            )
    return segments


def _extract_nsi_segments(manual: str, authority: dict[str, Any]) -> list[Segment]:
    relative = authority["local_archival_file"]
    path = ROOT / relative
    segments: list[Segment] = []
    with pdfplumber.open(path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            for table_number, table in enumerate(page.extract_tables(), start=1):
                if not table:
                    continue
                header = [(_normalise(cell or "")) for cell in table[0]]
                has_header = header[:3] == ["contenus", "capacites attendues", "commentaires"]
                rows = table[1:] if has_header else table
                for row_number, row in enumerate(rows, start=1):
                    padded = list(row) + [None] * (3 - len(row))
                    for column, classification, mandatory, cell in (
                        ("contenus", "CONTENTS", "YES", padded[0]),
                        ("capacites", "EXPECTED_CAPACITIES", "YES", padded[1]),
                        ("commentaires", "IMPLEMENTATION_GUIDANCE", "NO", padded[2]),
                    ):
                        for item_number, wording in enumerate(_split_cell(cell), start=1):
                            if _normalise(wording) in {"contenus", "capacites attendues", "commentaires"}:
                                continue
                            item_classification = classification
                            if any(marker in _normalise(wording) for marker in LIMITATION_MARKERS):
                                item_classification = "EXPLICIT_LIMITATIONS"
                            anchor = f"pdf-page:{page_number};table:{table_number};row:{row_number};column:{column};item:{item_number}"
                            if (manual == "TNSI" and column == "commentaires"
                                    and "group by" in _normalise(wording)
                                    and "having" in _normalise(wording)):
                                segments.extend((
                                    Segment(
                                        manual, authority["official_ref"], relative,
                                        anchor + ";part:guidance",
                                        "On peut utiliser DISTINCT, ORDER BY ou les fonctions d’agrégation.",
                                        "IMPLEMENTATION_GUIDANCE", "NO",
                                        f"Table réglementaire page {page_number}", [],
                                    ),
                                    Segment(
                                        manual, authority["official_ref"], relative,
                                        anchor + ";part:limitation",
                                        "Les clauses GROUP BY et HAVING ne sont pas utilisées.",
                                        "EXPLICIT_LIMITATIONS", "NO",
                                        f"Table réglementaire page {page_number}", [],
                                    ),
                                ))
                            else:
                                segments.append(
                                    Segment(
                                        manual, authority["official_ref"], relative,
                                        anchor, wording, item_classification, mandatory,
                                        f"Table réglementaire page {page_number}", [],
                                    )
                                )

    # The mandatory project quota is outside the tables and must remain
    # discoverable even if its atom is removed.
    for page_number, page in enumerate(PdfReader(path).pages, start=1):
        lines = (page.extract_text() or "").splitlines()
        for line_number, raw in enumerate(lines, start=1):
            if "quart" not in _normalise(raw) or "horaire" not in _normalise(raw):
                continue
            start = max(1, line_number - 1)
            end = min(len(lines), line_number + 2)
            wording = _compact(" ".join(lines[start - 1 : end]))
            segments.append(
                Segment(
                    manual, authority["official_ref"], relative,
                    f"pdf-page:{page_number};lines:{start}-{end}", wording,
                    "OTHER_OFFICIAL" if manual == "1NSI" else "IMPLEMENTATION_GUIDANCE",
                    "YES", "Démarche de projet", [],
                )
            )
    segments.extend(_extract_pdf_cross_cutting(manual, authority, path))
    return segments


def extract_source_segments(authorities: dict[str, dict[str, Any]]) -> list[Segment]:
    segments: list[Segment] = []
    for manual in MANUAL_ORDER:
        authority = authorities[manual]
        if Path(authority["local_archival_file"]).suffix.casefold() == ".pdf":
            segments.extend(_extract_nsi_segments(manual, authority))
        else:
            segments.extend(_extract_math_segments(manual, authority))
    # Stable order comes from source path + physical anchor, never atom order.
    for manual in MANUAL_ORDER:
        sequence = 0
        for segment in (item for item in segments if item.manual == manual):
            sequence += 1
            setattr(segment, "segment_id", f"{manual}-SOURCE-SEG-{sequence:03d}")
    return segments


def _map_atoms(segments: list[Segment], atoms: list[dict[str, Any]]) -> None:
    by_manual_atoms = defaultdict(list)
    for atom in atoms:
        by_manual_atoms[atom["manual"]].append(atom)
    available_atom_ids = {atom["atom_id"] for atom in atoms}

    # Only peer-reviewed, explicit mappings are proof.  Fuzzy matching below
    # produces candidates and can never populate atom_ids.
    for segment in segments:
        if (segment.manual, segment.source_anchor) in KNOWN_UNPARSED_SOURCE_ANCHORS:
            continue
        override = SOURCE_ANCHOR_MAPPING_OVERRIDES.get((segment.manual, segment.source_anchor))
        if override is None:
            override = SOURCE_MAPPING_OVERRIDES.get(
                (segment.manual, _normalise(segment.source_wording_short))
            )
        if override:
            segment.atom_ids.extend(
                atom_id for atom_id in override if atom_id in available_atom_ids
            )
            segment.best_atom_score = 1.0

    for segment in segments:
        if segment.atom_ids:
            continue
        ranked = sorted(
            (
                (_score(segment.source_wording_short, atom["short_official_wording_or_paraphrase"]), atom)
                for atom in by_manual_atoms[segment.manual]
                if _section_compatible(segment, atom) and _type_compatible(segment, atom)
            ),
            key=lambda pair: (-pair[0], pair[1]["atom_id"]),
        )
        candidates = [pair for pair in ranked if pair[0] >= CANDIDATE_MATCH_MINIMUM][:3]
        segment.candidate_atom_ids = [atom["atom_id"] for _, atom in candidates]
        if candidates:
            segment.best_atom_score = round(candidates[0][0], 6)

    for segment in segments:
        segment.atom_ids = sorted(set(segment.atom_ids))
        segment.candidate_atom_ids = sorted(set(segment.candidate_atom_ids or []))
        if not segment.atom_ids and segment.mandatory == "NO":
            segment.non_atomic_justification = {
                "CROSS_CUTTING_COMPETENCIES": "TRANSVERSAL_FRAMEWORK_NOT_A_SEPARATE_COVERAGE_ATOM",
                "IMPLEMENTATION_GUIDANCE": "PEDAGOGICAL_IMPLEMENTATION_GUIDANCE_NOT_A_COVERAGE_ATOM",
                "EXPLICIT_LIMITATIONS": "SCOPE_BOUNDARY; mandatory_for_coverage=NO",
                "OPTIONAL_EXTENSIONS": "OPTIONAL_OFFICIAL_SUGGESTION; mandatory_for_coverage=NO",
                "HISTORY_CONTEXT": "HISTORY_CONTEXT; mandatory_for_coverage=NO",
                "MANDATORY_PROOFS": "OFFICIAL_DEMONSTRATION_MARKED_POSSIBLE_NOT_EXIGIBLE",
            }.get(segment.classification, "OTHER_OFFICIAL_NON_ATOMIC_CONTEXT")


def _duplicate_groups(atoms: list[dict[str, Any]], segments: list[Segment]) -> list[dict[str, Any]]:
    available = {atom["atom_id"] for atom in atoms}
    return [
        {
            "manual": group["manual"],
            "atom_ids": list(group["atom_ids"]),
            "official_source_anchor": group["official_source_anchor"],
            "reason": group["reason"],
        }
        for group in KNOWN_DUPLICATE_GROUPS
        if set(group["atom_ids"]).issubset(available)
    ]


def build_registry() -> dict[str, Any]:
    authorities = _authorities()
    source_documents: dict[str, dict[str, Any]] = {}
    source_paths: list[Path] = []
    for manual in MANUAL_ORDER:
        authority = authorities[manual]
        relative = authority["local_archival_file"]
        path = ROOT / relative
        digest = _sha256(path)
        expected = authority["local_archival_digest"]
        if digest != expected:
            raise ValueError(f"authority digest mismatch for {manual}: {digest} != {expected}")
        source_paths.append(path)
        source_documents[manual] = {
            "authority_NOR": authority["official_ref"],
            "effective_from": authority["effective_from"],
            "effective_until": authority.get("effective_until"),
            "applicable_school_year": "2026-2027",
            "official_url": authority["authority_url"],
            "source_path": relative,
            "source_format": path.suffix.lstrip(".").upper(),
            "digest": digest,
            "authority_registry_digest": expected,
            "digest_matches_authority_registry": True,
            # Ce que la lecture a du recomposer pour rendre au texte officiel
            # sa structure : chaque fraction empilee, avec les lignes et la
            # colonne qui l'ont identifiee. Rien n'est reformule ; on rend
            # lisible une barre de fraction que le PDF n'avait laissee que
            # sous forme d'alignement.
            "stacked_fractions_recomposed": (
                fold_stacked_fractions(
                    path.read_text(encoding="utf-8").split("\n")
                )[1]
                if path.suffix == ".txt"
                else []
            ),
        }
    segments = extract_source_segments(authorities)
    serialised_segments = [
        {
            "segment_id": getattr(segment, "segment_id"),
            "manual": segment.manual,
            "authority_NOR": segment.authority_nor,
            "official_section": segment.official_section,
            "source_path": segment.source_path,
            "source_anchor": segment.source_anchor,
            "source_wording_short": segment.source_wording_short,
            "classification": segment.classification,
            "mandatory": segment.mandatory,
        }
        for segment in segments
    ]
    by_manual = {
        manual: {
            "source_segments": sum(item.manual == manual for item in segments),
            "mandatory_source_segments": sum(item.manual == manual and item.mandatory == "YES" for item in segments),
        }
        for manual in MANUAL_ORDER
    }
    return {
        "schema_version": 3,
        "artifact_name": "OFFICIAL_SOURCE_SEGMENTS_2026_2027",
        "namespace": "PROGRAMME_D_ENSEIGNEMENT",
        "applicable_school_year": "2026-2027",
        "source_digest": _composite_digest([AUTHORITY_PATH, *source_paths]),
        "methodology": {
            "official_files_are_source": True,
            "internal_capacities_are_source": False,
            "coverage_matrices_are_source": False,
            "population_order": "official sources only; atom mapping is a separate downstream artifact",
            "math_segmentation": "each official bullet under regulatory category plus explicit narrative limitations",
            "nsi_segmentation": "each substantive PDF table cell item plus project quota and cross-cutting bullets",
            "atom_registry_dependency": False,
            "fuzzy_mapping": False,
        },
        "source_documents": source_documents,
        "summary": {
            "source_extraction_status": "REVIEWED",
            "official_authorities": 6,
            "source_segments": len(segments),
            "mandatory_source_segments": sum(item.mandatory == "YES" for item in segments),
            "by_manual": by_manual,
        },
        "segments": serialised_segments,
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# OFFICIAL SOURCE SEGMENTS — 2026-2027", "",
        "Population purement **source-first** des six TXT/PDF officiels. Le registre d'atoms et les matrices de couverture sont des consommateurs en aval et ne participent ni à l'extraction ni à son digest.", "",
        "## Compteurs", "",
        f"- authorities: {summary['official_authorities']}/6",
        f"- source segments: {summary['source_segments']} ({summary['mandatory_source_segments']} mandatory)",
        f"- source extraction: **{summary['source_extraction_status']}**", "",
        "## Sources", "", "| Manuel | NOR | Source | Digest |", "|---|---|---|---|",
    ]
    for manual in MANUAL_ORDER:
        source = payload["source_documents"][manual]
        lines.append(f"| {manual} | {source['authority_NOR']} | `{source['source_path']}` | `{source['digest']}` |")
    lines.append("")
    for manual in MANUAL_ORDER:
        lines.extend([
            f"## {manual}", "",
            "| Segment | Ancre | Classe | Mandatory | Wording source |",
            "|---|---|---|---|---|",
        ])
        for segment in payload["segments"]:
            if segment["manual"] != manual:
                continue
            lines.append("| " + " | ".join(_cell(value) for value in (
                segment["segment_id"], segment["source_anchor"], segment["classification"],
                segment["mandatory"], segment["source_wording_short"],
            )) + " |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_registry()
    expected = {JSON_TARGET: render_json(payload), MD_TARGET: render_markdown(payload)}
    if args.check:
        stale = [path for path, content in expected.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"STALE_OR_MISSING: {path.relative_to(ROOT)}")
            return 1
        print(f"official source segments current: {payload['summary']['source_segments']} source-first segments")
        return 0
    for path, content in expected.items():
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
