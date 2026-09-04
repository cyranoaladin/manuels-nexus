"""L'arbre DESSINÉ doit dire la même chose que le corrigé qui l'entoure.

Sept exercices de 1SPE-PROBA-COND demandent « Construire l'arbre pondéré ».
Les corrigés y répondent désormais par une figure (`nxarbreproba`, composant
canonique `gabarits/common/nexus-arbres.sty`) et non plus par une description.

Une figure introduit un risque que le texte n'avait pas : une valeur peut être
posée sous la mauvaise branche sans que rien ne proteste. C'est exactement le
défaut P0 SELF_CONFIRMING_AGGREGATE_CHECK, transposé au dessin — la somme des
feuilles resterait 1 après une permutation. Ce module vérifie donc
l'association ÉTIQUETTE -> VALEUR, chemin par chemin :

  * chaque probabilité de branche de l'arbre est comparée à la donnée de
    l'ÉNONCÉ, sous le chemin conditionnel exact où elle est dessinée ;
  * chaque probabilité de feuille est comparée au produit de ses branches ;
  * l'arbre et le corps du corrigé doivent déclarer les mêmes couples
    (étiquette, probabilité) ;
  * une permutation de deux valeurs entre deux étiquettes de l'arbre doit
    faire ÉCHOUER ces contrôles alors que la somme des feuilles vaut toujours 1
    (`test_permuter_deux_valeurs_*`). Sans cette démonstration, la
    vérification ne prouverait rien.

Le rendu est mesuré, pas regardé : `test_rendu_*` compile les sept arbres
publiés plus des cas difficiles, puis compte dans le PDF les tracés hors zone
de texte, les chevauchements d'étiquettes et les corps illisibles.
"""

from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "Mathematiques/manuel-maths"
CHAPTER = MANUAL / "chapitres/1SPE-PROBA-COND"
COMPONENT = ROOT / "gabarits/common/nexus-arbres.sty"
CHARTE = ROOT / "gabarits/common/nexus-charte.sty"

TREE_EXERCISES = ("015", "019", "021", "041", "044", "045", "047")

# --- géométrie de page contractuelle (nexus-manuel.cls, \geometry a4paper) ---
MM = 72.0 / 25.4
PAGE_WIDTH, PAGE_HEIGHT = 210.0 * MM, 297.0 * MM
MARGIN_INNER, MARGIN_OUTER = 20.0 * MM, 44.0 * MM
MARGIN_TOP, MARGIN_BOTTOM = 24.0 * MM, 26.0 * MM

#: En dessous de ce corps, une étiquette de fraction n'est plus lisible à
#: l'impression. \footnotesize vaut environ 7,9 pt dans la maquette.
MIN_READABLE_PT = 5.0


# ===========================================================================
#  Oracle existant (chemins étiquetés) — réutilisé, jamais réimplémenté
# ===========================================================================
def _load_oracle():
    spec = importlib.util.spec_from_file_location(
        "probability_path_oracle", ROOT / "scripts/probability_path_oracle.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ORACLE = _load_oracle()
normalise = ORACLE.normalise_label


# ===========================================================================
#  Lecture des sources
# ===========================================================================
def correction_path(number: str) -> Path:
    return CHAPTER / f"corriges/1SPE-PROBCOND-CO-{number}.tex"


def correction_text(number: str) -> str:
    return correction_path(number).read_text(encoding="utf-8")


TREE_BLOCK = re.compile(
    r"\\begin\{nxarbreproba\}(?:\[[^\]]*\])?(?P<corps>.*?)\\end\{nxarbreproba\}",
    re.S,
)
FRACTION = re.compile(r"\\d?frac\{(-?\d+)\}\{(\d+)\}")
DECIMAL = re.compile(r"^(-?\d+)\{,\}(\d+)$")
BODY_COUPLE = re.compile(
    r"\$(?P<label>[^$]*)\$\s*de probabilité\s*\$(?P<valeur>[^$]*)\$"
)


def parse_probability(raw: str) -> Fraction:
    """`$\\dfrac{27}{50}$` ou `$0{,}0095$` -> Fraction exacte."""
    text = raw.replace("$", "").replace("\\,", "").strip()
    fractions = FRACTION.findall(text)
    if fractions:
        numerator, denominator = fractions[0]
        return Fraction(int(numerator), int(denominator))
    decimal = DECIMAL.match(text)
    if decimal:
        whole, decimals = decimal.groups()
        return Fraction(int(whole)) + Fraction(int(decimals), 10 ** len(decimals))
    if re.fullmatch(r"-?\d+", text):
        return Fraction(int(text))
    raise ValueError(f"probabilité illisible : {raw!r}")


def _arguments(source: str, start: int, count: int) -> tuple[list[str], int]:
    """Extrait `count` arguments entre accolades équilibrées."""
    arguments: list[str] = []
    index = start
    for _ in range(count):
        while index < len(source) and source[index] in " \t\r\n%":
            index += 1
        assert source[index] == "{", f"argument attendu à la position {index}"
        depth, begin = 0, index
        while index < len(source):
            if source[index] == "{":
                depth += 1
            elif source[index] == "}":
                depth -= 1
                if depth == 0:
                    break
            index += 1
        arguments.append(source[begin + 1 : index])
        index += 1
    return arguments, index


class Tree:
    """L'arbre tel qu'il est DÉCLARÉ dans le .tex, sans interprétation."""

    def __init__(self, body: str) -> None:
        self.root: str | None = None
        self.parent: dict[str, str] = {}
        self.label: dict[str, str] = {}
        self.probability: dict[str, Fraction] = {}
        self.event: dict[str, str] = {}
        self.value: dict[str, Fraction] = {}
        self.order: list[str] = []
        self._parse(body)

    def _parse(self, body: str) -> None:
        for match in re.finditer(
            r"\\nxarbre(racine|noeud|feuille)", body
        ):
            kind = match.group(1)
            counts = {"racine": 1, "noeud": 4, "feuille": 6}[kind]
            arguments, _ = _arguments(body, match.end(), counts)
            identifier = arguments[0].strip()
            self.order.append(identifier)
            if kind == "racine":
                self.root = identifier
                continue
            self.parent[identifier] = arguments[1].strip()
            self.label[identifier] = arguments[2].strip()
            self.probability[identifier] = parse_probability(arguments[3])
            if kind == "feuille":
                if arguments[4].strip():
                    self.event[identifier] = arguments[4].strip()
                if arguments[5].strip():
                    self.value[identifier] = parse_probability(arguments[5])

    def children(self, identifier: str) -> list[str]:
        return [n for n in self.order if self.parent.get(n) == identifier]

    def leaves(self) -> list[str]:
        return [n for n in self.order if not self.children(n)]

    def path(self, identifier: str) -> tuple[str, ...]:
        """Chemin d'étiquettes NORMALISÉES de la racine jusqu'au nœud."""
        chain: list[str] = []
        current = identifier
        while current in self.parent:
            chain.append(normalise(self.label[current]))
            current = self.parent[current]
        return tuple(reversed(chain))

    def branch_probabilities(self) -> dict[tuple[str, ...], Fraction]:
        return {self.path(n): self.probability[n] for n in self.parent}

    def branch_couples(self) -> set[tuple[str, Fraction]]:
        return {
            (normalise(self.label[n]), self.probability[n]) for n in self.parent
        }

    def path_probability(self, identifier: str) -> Fraction:
        product = Fraction(1)
        current = identifier
        while current in self.parent:
            product *= self.probability[current]
            current = self.parent[current]
        return product

    def leaf_events(self) -> dict[str, Fraction]:
        """`evenement normalisé -> probabilité de chemin DÉCLARÉE`."""
        return {
            normalise(self.event[n]): self.value[n]
            for n in self.leaves()
            if n in self.event and n in self.value
        }


def tree_of(number: str, text: str | None = None) -> Tree:
    source = correction_text(number) if text is None else text
    match = TREE_BLOCK.search(source)
    assert match, f"CO-{number} ne contient aucun arbre nxarbreproba"
    return Tree(match.group("corps"))


def body_couples(number: str, text: str | None = None) -> set[tuple[str, Fraction]]:
    """Couples (étiquette, probabilité) énoncés en toutes lettres par le corrigé."""
    source = correction_text(number) if text is None else text
    outside = TREE_BLOCK.sub("", source)
    return {
        (normalise(m.group("label")), parse_probability(m.group("valeur")))
        for m in BODY_COUPLE.finditer(outside)
    }


# ===========================================================================
#  Données des ÉNONCÉS — jamais relues dans le corrigé
# ===========================================================================
# Un oracle qui recopierait les valeurs du corrigé ne prouverait rien : ces
# tables viennent des exercices 1SPE-PROBCOND-EX-* correspondants.
F = Fraction

STATEMENTS: dict[str, dict] = {
    "015": {
        "branches": {
            ("R",): F(3, 5),
            ("~R",): F(2, 5),
            ("R", "S"): F(9, 10),
            ("R", "~S"): F(1, 10),
            ("~R", "S"): F(7, 10),
            ("~R", "~S"): F(3, 10),
        },
        "leaves": {
            ("R", "S"): "S&R",
            ("R", "~S"): "~S&R",
            ("~R", "S"): "S&~R",
            ("~R", "~S"): "~S&~R",
        },
        "somme": F(1),
    },
    "019": {
        # Tirages sans remise dans 5 rouges + 3 bleues ; l'énoncé ne demande
        # de développer que la branche rouge aux niveaux 2 et 3.
        "branches": {
            ("R_1",): F(5, 8),
            ("~R_1",): F(3, 8),
            ("R_1", "R_2"): F(4, 7),
            ("R_1", "R_2", "R_3"): F(3, 6),
        },
        "leaves": {("R_1", "R_2", "R_3"): "R_1&R_2&R_3"},
        "somme": None,  # arbre volontairement partiel
    },
    "021": {
        "branches": {
            ("B",): F(2, 5),
            ("~B",): F(3, 5),
            ("B", "A"): F(3, 4),
            ("B", "~A"): F(1, 4),
            ("~B", "A"): F(1, 3),
            ("~B", "~A"): F(2, 3),
        },
        "leaves": {
            ("B", "A"): "A&B",
            ("B", "~A"): "~A&B",
            ("~B", "A"): "A&~B",
            ("~B", "~A"): "~A&~B",
        },
        "somme": F(1),
    },
    "041": {
        # Prévalence 1 %, sensibilité 95 %, spécificité 97 %.
        "branches": {
            ("M",): F(1, 100),
            ("~M",): F(99, 100),
            ("M", "T"): F(95, 100),
            ("M", "~T"): F(5, 100),
            ("~M", "T"): F(3, 100),
            ("~M", "~T"): F(97, 100),
        },
        "leaves": {
            ("M", "T"): "T&M",
            ("M", "~T"): "~T&M",
            ("~M", "T"): "T&~M",
            ("~M", "~T"): "~T&~M",
        },
        "somme": F(1),
    },
    "044": {
        # Deux parents Aa : chaque allèle transmis avec la probabilité 1/2.
        "branches": {
            ("A",): F(1, 2),
            ("a",): F(1, 2),
            ("A", "A"): F(1, 2),
            ("A", "a"): F(1, 2),
            ("a", "A"): F(1, 2),
            ("a", "a"): F(1, 2),
        },
        "leaves": {
            ("A", "A"): "AA",
            ("A", "a"): "Aa",
            ("a", "A"): "aA",
            ("a", "a"): "aa",
        },
        "somme": F(1),
    },
    "045": {
        "branches": {
            ("P_1",): F(2, 5),
            ("~P_1",): F(3, 5),
            ("P_1", "P_2"): F(7, 10),
            ("P_1", "~P_2"): F(3, 10),
            ("~P_1", "P_2"): F(3, 10),
            ("~P_1", "~P_2"): F(7, 10),
        },
        "leaves": {
            ("P_1", "P_2"): "P_2&P_1",
            ("P_1", "~P_2"): "~P_2&P_1",
            ("~P_1", "P_2"): "P_2&~P_1",
            ("~P_1", "~P_2"): "~P_2&~P_1",
        },
        "somme": F(1),
    },
    "047": {
        # Prévalence 5 %, sensibilité 99 %, spécificité 95 %.
        "branches": {
            ("D",): F(5, 100),
            ("~D",): F(95, 100),
            ("D", "T"): F(99, 100),
            ("D", "~T"): F(1, 100),
            ("~D", "T"): F(5, 100),
            ("~D", "~T"): F(95, 100),
        },
        "leaves": {
            ("D", "T"): "T&D",
            ("D", "~T"): "~T&D",
            ("~D", "T"): "T&~D",
            ("~D", "~T"): "~T&~D",
        },
        "somme": F(1),
    },
}


def tree_mismatches(number: str, text: str | None = None) -> dict[str, dict]:
    """Désaccords étiquette par étiquette entre l'arbre dessiné et l'énoncé.

    Vide = accord exact. C'est la fonction que la mutation doit faire parler.
    """
    tree = tree_of(number, text)
    statement = STATEMENTS[number]
    mismatches: dict[str, dict] = {}

    drawn = tree.branch_probabilities()
    for path, expected in statement["branches"].items():
        key = "/".join(path)
        if path not in drawn:
            mismatches[key] = {"attendu": str(expected), "dessiné": None}
        elif drawn[path] != expected:
            mismatches[key] = {
                "attendu": str(expected),
                "dessiné": str(drawn[path]),
            }
    for path, value in drawn.items():
        if path not in statement["branches"]:
            mismatches["/".join(path)] = {
                "attendu": None,
                "dessiné": str(value),
            }

    for identifier in tree.leaves():
        path = tree.path(identifier)
        if path not in statement["leaves"]:
            continue
        key = "feuille " + "/".join(path)
        expected_event = statement["leaves"][path]
        if normalise(tree.event.get(identifier, "")) != expected_event:
            mismatches[key + " (événement)"] = {
                "attendu": expected_event,
                "dessiné": normalise(tree.event.get(identifier, "")),
            }
        product = tree.path_probability(identifier)
        if tree.value.get(identifier) != product:
            mismatches[key + " (valeur)"] = {
                "attendu": str(product),
                "dessiné": str(tree.value.get(identifier)),
            }
    return mismatches


# ===========================================================================
#  1. Le composant est unique et canonique
# ===========================================================================
def test_le_composant_est_unique_et_charge_par_la_charte() -> None:
    assert COMPONENT.is_file(), "le composant canonique doit exister"
    assert "nxRequireCommonModule{nexus-arbres}" in CHARTE.read_text(
        encoding="utf-8"
    ), "la charte doit charger le composant d'arbres"


def test_aucun_corrige_ne_dessine_son_propre_arbre() -> None:
    """Sept dessins artisanaux seraient sept occasions de diverger."""
    artisanal = []
    for number in TREE_EXERCISES:
        text = correction_text(number)
        if r"\begin{tikzpicture}" in text or r"\tikz" in text:
            artisanal.append(number)
    assert artisanal == [], (
        f"ces corrigés contournent le composant canonique : {artisanal}"
    )


@pytest.mark.parametrize("number", TREE_EXERCISES)
def test_aucun_corrige_ne_charge_lui_meme_son_composant(number: str) -> None:
    """Le corrige ne doit PAS rendre son propre composant disponible.

    Il l'a fait un temps : l'enveloppe R6 montait l'objet sans la charte, et
    les sept corriges compensaient par un `\\@ifundefined` et un `\\input` a
    deux chemins. C'etait une bequille, pas une preuve -- un objet qui charge
    lui-meme un `.sty` de la charte compilerait encore si la charte cessait de
    le fournir, et le gate ne verrait plus rien.

    L'enveloppe charge desormais la charte, comme le document assemble.
    """

    text = correction_text(number)
    assert "nexus-arbres.sty" not in text, (
        f"CO-{number} : le corrige recharge un composant de la charte"
    )
    assert "@ifundefined{nxarbreproba}" not in text, (
        f"CO-{number} : reste de chargement de secours"
    )
    assert "\\begin{nxarbreproba}" in text, (
        f"CO-{number} : l'arbre doit toujours etre present"
    )


@pytest.mark.parametrize("number", TREE_EXERCISES)
def test_chaque_corrige_dessine_bien_un_arbre(number: str) -> None:
    tree = tree_of(number)
    assert tree.root is not None
    assert len(tree.leaves()) >= 2


# ===========================================================================
#  2. Science : chaque chemin sous SON événement
# ===========================================================================
@pytest.mark.parametrize("number", TREE_EXERCISES)
def test_l_arbre_dessine_dit_ce_que_l_enonce_impose(number: str) -> None:
    assert tree_mismatches(number) == {}


def _declared_leaf_mass(number: str) -> Fraction:
    """La masse que les feuilles DÉCLARÉES portent, calculée sur l'énoncé.

    Pour un arbre complet elle vaut 1 ; pour un arbre volontairement partiel
    elle vaut le produit des probabilités le long des seuls chemins tracés.
    Elle se calcule, elle ne se recopie pas.
    """

    branches = STATEMENTS[number]["branches"]
    total = Fraction(0)
    for path in STATEMENTS[number]["leaves"]:
        mass = Fraction(1)
        for depth in range(1, len(path) + 1):
            mass *= branches[path[:depth]]
        total += mass
    return total


COMPLETE_TREES = tuple(
    number for number in TREE_EXERCISES if STATEMENTS[number]["somme"] is not None
)
PARTIAL_TREES = tuple(
    number for number in TREE_EXERCISES if STATEMENTS[number]["somme"] is None
)


@pytest.mark.parametrize("number", COMPLETE_TREES)
def test_les_feuilles_somment_a_un_quand_l_arbre_est_complet(number: str) -> None:
    expected = STATEMENTS[number]["somme"]
    tree = tree_of(number)
    total = sum(
        (tree.value[n] for n in tree.leaves() if n in tree.value), Fraction(0)
    )
    assert total == expected


@pytest.mark.parametrize("number", PARTIAL_TREES)
def test_un_arbre_volontairement_partiel_porte_exactement_sa_masse(
    number: str,
) -> None:
    """Un arbre tronqué se VÉRIFIE ; il ne se saute pas.

    EX-019 ne développe la branche rouge qu'aux niveaux 2 et 3 : ses feuilles ne
    somment donc pas à un, et l'ancien contrôle se contentait de passer son
    tour. Or le comportement est parfaitement déterministe -- la masse des
    feuilles tracées se calcule sur l'énoncé -- et un contrôle qui saute ne
    protège rien.
    """

    expected = _declared_leaf_mass(number)
    tree = tree_of(number)
    total = sum(
        (tree.value[n] for n in tree.leaves() if n in tree.value), Fraction(0)
    )

    assert total == expected, f"EX-{number} : masse tracée {total} ≠ {expected}"
    # C'est bien un arbre TRONQUÉ, pas un arbre complet mal déclaré.
    assert total < 1, f"EX-{number} est déclaré partiel mais somme à un"
    # Les feuilles dessinées sont exactement celles que l'énoncé déclare.
    drawn = {
        normalise(tree.event[n]) for n in tree.leaves() if n in tree.event
    }
    assert drawn == {
        normalise(label) for label in STATEMENTS[number]["leaves"].values()
    }
    # Et aucune branche n'a été ajoutée en chemin.
    assert tree_mismatches(number) == {}


@pytest.mark.parametrize("number", TREE_EXERCISES)
def test_l_arbre_et_le_corps_du_corrige_declarent_les_memes_couples(
    number: str,
) -> None:
    """Exigence 4.1 : mêmes couples (étiquette, probabilité) des deux côtés."""
    assert tree_of(number).branch_couples() == body_couples(number)


def test_les_chemins_de_co015_passent_l_oracle_label_sensible() -> None:
    """Non-régression : l'oracle historique reste vert sur le corrigé réécrit."""
    body = correction_text("015").split("\n", 1)[1]
    printed = ORACLE.printed_paths(body)
    expected = ORACLE.expected_paths(
        {"R": F(3, 5), "~R": F(2, 5)},
        {
            "R": {"S": F(9, 10), "~S": F(1, 10)},
            "~R": {"S": F(7, 10), "~S": F(3, 10)},
        },
    )
    assert ORACLE.compare(printed, expected) == {}
    assert ORACLE.sum_of_paths(expected) == 1
    # ... et l'arbre DESSINÉ dit exactement la même chose que le texte imprimé.
    assert tree_of("015").leaf_events() == expected


@pytest.mark.parametrize("number", TREE_EXERCISES)
def test_l_arbre_ne_contredit_aucune_valeur_imprimee_par_le_corrige(
    number: str,
) -> None:
    """Tout chemin que l'arbre ET le texte nomment doit porter la même valeur.

    La comparaison se limite aux étiquettes en forme d'intersection (`&`),
    seules à désigner sans ambiguïté UN chemin de l'arbre. En génétique
    (CO-044) le corrigé imprime aussi $P(Aa)$ au sens du GÉNOTYPE, qui réunit
    les deux feuilles ordonnées $Aa$ et $aA$ : les confondre serait comparer un
    événement à un autre, pas vérifier une valeur. Ce regroupement a son propre
    contrôle, `test_co044_regroupe_correctement_les_deux_feuilles_heterozygotes`.
    """
    body = correction_text(number).split("\n", 1)[1]
    printed = ORACLE.printed_paths(TREE_BLOCK.sub("", body))
    drawn = tree_of(number).leaf_events()
    shared = {key for key in set(printed) & set(drawn) if "&" in key}
    assert {k: printed[k] for k in shared} == {k: drawn[k] for k in shared}


def test_co044_regroupe_correctement_les_deux_feuilles_heterozygotes() -> None:
    """Le génotype $Aa$ réunit DEUX feuilles ordonnées : $1/4 + 1/4 = 1/2$."""
    tree = tree_of("044")
    leaves = tree.leaf_events()
    assert leaves["Aa"] == F(1, 4) and leaves["aA"] == F(1, 4)
    assert leaves["Aa"] + leaves["aA"] == F(1, 2)
    assert leaves["AA"] == F(1, 4) and leaves["aa"] == F(1, 4)
    body = correction_text("044").split("\n", 1)[1]
    printed = ORACLE.printed_paths(TREE_BLOCK.sub("", body))
    assert printed["Aa"] == leaves["Aa"] + leaves["aA"]
    assert printed["AA"] == leaves["AA"]
    assert printed["aa"] == leaves["aa"]


# ===========================================================================
#  3. MUTATION — sans elle, tout ce qui précède ne prouve rien
# ===========================================================================
def _swap_in_tree(number: str, first: str, second: str) -> str:
    """Permute deux valeurs entre deux étiquettes, DANS le bloc arbre."""
    source = correction_text(number)
    match = TREE_BLOCK.search(source)
    assert match
    block = match.group(0)
    assert first in block and second in block, "valeurs absentes de l'arbre"
    mutated = block.replace(first, "\0").replace(second, first).replace("\0", second)
    return source[: match.start()] + mutated + source[match.end() :]


def test_permuter_deux_valeurs_de_feuilles_fait_echouer_le_controle() -> None:
    """LE test de la classe, transposé au dessin.

    On échange 27/50 et 14/50 entre $S \\cap R$ et $S \\cap \\overline{R}$ :
    c'est la faute exacte qui avait été publiée en texte. La somme des quatre
    feuilles vaut toujours 1, donc l'ancien contrôle global passe encore. Le
    contrôle étiquette -> valeur, lui, doit voir la faute.
    """
    mutated = _swap_in_tree("015", r"\dfrac{27}{50}", r"\dfrac{14}{50}")
    tree = tree_of("015", mutated)

    total = sum(
        (tree.value[n] for n in tree.leaves() if n in tree.value), Fraction(0)
    )
    assert total == 1, "la somme reste juste : elle est aveugle à la permutation"

    mismatches = tree_mismatches("015", mutated)
    assert mismatches, "une permutation de feuilles DOIT être détectée"
    assert set(mismatches) == {
        "feuille R/S (valeur)",
        "feuille ~R/S (valeur)",
    }
    assert mismatches["feuille R/S (valeur)"] == {
        "attendu": "27/50",
        "dessiné": "7/25",
    }


def test_permuter_deux_probabilites_de_branches_fait_echouer_le_controle() -> None:
    """Permutation en amont : deux conditionnelles échangées entre étiquettes.

    Les feuilles restent alors sommables à 1 et l'arbre reste « joli » ; seule
    la comparaison chemin par chemin peut le voir.
    """
    mutated = _swap_in_tree("045", r"\dfrac{7}{10}", r"\dfrac{3}{10}")
    tree = tree_of("045", mutated)

    branches = tree.branch_probabilities()
    for parent in (("P_1",), ("~P_1",)):
        children = [v for k, v in branches.items() if k[:-1] == parent]
        assert sum(children) == 1, "chaque nœud somme encore à 1"

    assert tree_mismatches("045", mutated), (
        "une permutation de branches DOIT être détectée"
    )


def test_permuter_deux_valeurs_desaccorde_l_arbre_et_le_corps_du_corrige() -> None:
    """La confrontation arbre <-> texte doit elle aussi être sensible."""
    number = "015"
    mutated = _swap_in_tree(number, r"\dfrac{9}{10}", r"\dfrac{1}{10}")
    assert tree_of(number, mutated).branch_couples() != body_couples(number)


def test_l_oracle_de_chemins_reste_aveugle_a_la_permutation_globale() -> None:
    """Non-régression sur la doctrine : la somme ne prouve jamais l'association."""
    expected = ORACLE.expected_paths(
        {"R": F(3, 5), "~R": F(2, 5)},
        {
            "R": {"S": F(9, 10), "~S": F(1, 10)},
            "~R": {"S": F(7, 10), "~S": F(3, 10)},
        },
    )
    permuted = dict(expected)
    permuted["S&~R"], permuted["~S&R"] = expected["~S&R"], expected["S&~R"]
    assert ORACLE.sum_of_paths(permuted) == ORACLE.sum_of_paths(expected) == 1
    assert set(ORACLE.compare(permuted, expected)) == {"S&~R", "~S&R"}


# ===========================================================================
#  4. RENDU — mesuré dans le PDF, pas regardé
# ===========================================================================
STRESS_CASES: dict[str, str] = {
    # Étiquettes longues et valeurs longues : le pire cas de largeur.
    "etiquettes-longues": r"""
\begin{nxarbreproba}
  \nxarbreracine{o}
  \nxarbrenoeud{a}{o}{$\overline{D_{\text{cont}}}$}{$\dfrac{1234}{9999}$}
  \nxarbrefeuille{aa}{a}{$T_{\text{pos}}$}{$\dfrac{9999}{10000}$}%
    {$\overline{D_{\text{cont}}} \cap T_{\text{pos}}$}{$\dfrac{12338766}{99990000}$}
  \nxarbrefeuille{ab}{a}{$\overline{T_{\text{pos}}}$}{$\dfrac{1}{10000}$}%
    {$\overline{D_{\text{cont}}} \cap \overline{T_{\text{pos}}}$}{$\dfrac{1234}{99990000}$}
  \nxarbrenoeud{b}{o}{$D_{\text{cont}}$}{$\dfrac{8765}{9999}$}
  \nxarbrefeuille{ba}{b}{$T_{\text{pos}}$}{$\dfrac{1}{10000}$}%
    {$D_{\text{cont}} \cap T_{\text{pos}}$}{$\dfrac{8765}{99990000}$}
  \nxarbrefeuille{bb}{b}{$\overline{T_{\text{pos}}}$}{$\dfrac{9999}{10000}$}%
    {$D_{\text{cont}} \cap \overline{T_{\text{pos}}}$}{$\dfrac{87641235}{99990000}$}
\end{nxarbreproba}
""",
    # Quatre niveaux : profondeur maximale plausible dans le manuel.
    "quatre-niveaux": r"""
\begin{nxarbreproba}
  \nxarbreracine{o}
  \nxarbrenoeud{a}{o}{$A_1$}{$\dfrac{1}{2}$}
  \nxarbrenoeud{ab}{a}{$A_2$}{$\dfrac{1}{3}$}
  \nxarbrenoeud{abc}{ab}{$A_3$}{$\dfrac{1}{4}$}
  \nxarbrefeuille{abcd}{abc}{$A_4$}{$\dfrac{1}{5}$}%
    {$A_1 \cap A_2 \cap A_3 \cap A_4$}{$\dfrac{1}{120}$}
  \nxarbrefeuille{abce}{abc}{$\overline{A_4}$}{$\dfrac{4}{5}$}%
    {$A_1 \cap A_2 \cap A_3 \cap \overline{A_4}$}{$\dfrac{1}{30}$}
  \nxarbrefeuille{abf}{ab}{$\overline{A_3}$}{$\dfrac{3}{4}$}%
    {$A_1 \cap A_2 \cap \overline{A_3}$}{$\dfrac{1}{8}$}
  \nxarbrefeuille{ag}{a}{$\overline{A_2}$}{$\dfrac{2}{3}$}%
    {$A_1 \cap \overline{A_2}$}{$\dfrac{1}{3}$}
  \nxarbrefeuille{h}{o}{$\overline{A_1}$}{$\dfrac{1}{2}$}%
    {$\overline{A_1}$}{$\dfrac{1}{2}$}
\end{nxarbreproba}
""",
    # Colonne étroite : le garde-fou de largeur doit réduire, pas déborder.
    "colonne-etroite": r"""
\noindent\begin{minipage}{0.62\linewidth}
\begin{nxarbreproba}
  \nxarbreracine{o}
  \nxarbrenoeud{a}{o}{$\overline{R_1}$}{$\dfrac{3}{8}$}
  \nxarbrefeuille{aa}{a}{$\overline{R_2}$}{$\dfrac{2}{7}$}%
    {$\overline{R_1} \cap \overline{R_2}$}{$\dfrac{3}{28}$}
  \nxarbrefeuille{ab}{a}{$R_2$}{$\dfrac{5}{7}$}%
    {$\overline{R_1} \cap R_2$}{$\dfrac{15}{56}$}
  \nxarbrenoeud{b}{o}{$R_1$}{$\dfrac{5}{8}$}
  \nxarbrefeuille{ba}{b}{$\overline{R_2}$}{$\dfrac{3}{7}$}%
    {$R_1 \cap \overline{R_2}$}{$\dfrac{15}{56}$}
  \nxarbrefeuille{bb}{b}{$R_2$}{$\dfrac{4}{7}$}%
    {$R_1 \cap R_2$}{$\dfrac{5}{14}$}
\end{nxarbreproba}
\end{minipage}
""",
    # Étiquettes minuscules et fractions empilées, sans colonne de droite.
    "etiquettes-minuscules": r"""
\begin{nxarbreproba}[niveau=18, feuille=10]
  \nxarbreracine{o}
  \nxarbrenoeud{a}{o}{$a$}{$\dfrac{1}{7}$}
  \nxarbrefeuille{aa}{a}{$b$}{$\dfrac{2}{9}$}{}{}
  \nxarbrefeuille{ab}{a}{$\overline{b}$}{$\dfrac{7}{9}$}{}{}
  \nxarbrenoeud{b}{o}{$\overline{a}$}{$\dfrac{6}{7}$}
  \nxarbrefeuille{ba}{b}{$b$}{$\dfrac{4}{9}$}{}{}
  \nxarbrefeuille{bb}{b}{$\overline{b}$}{$\dfrac{5}{9}$}{}{}
\end{nxarbreproba}
""",
}

PREAMBLE = r"""\documentclass{gabarits/nexus-manuel-v5}
\matiere{Mathématiques}\niveau{Première spécialité}
\nxVersionProfesseurtrue
\pagestyle{empty}
\nxVSuppressTabtrue
\begin{document}
"""


def _audit_document(pages: list[str]) -> str:
    body = "\n\\clearpage\n".join(f"\\noindent\n{p}" for p in pages)
    return PREAMBLE + body + "\n\\end{document}\n"


def _compile(tmp_path: Path, source: str, stem: str) -> Path:
    tex = tmp_path / f"{stem}.tex"
    tex.write_text(source, encoding="utf-8")
    completed = subprocess.run(
        [
            "lualatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={tmp_path}",
            str(tex),
        ],
        cwd=MANUAL,
        capture_output=True,
        text=True,
        timeout=900,
    )
    pdf = tmp_path / f"{stem}.pdf"
    assert completed.returncode == 0 and pdf.is_file(), completed.stdout[-4000:]
    return pdf


def _text_zone(page_number: int) -> tuple[float, float, float, float]:
    """Zone de texte contractuelle, reliure à gauche sur les pages impaires."""
    if page_number % 2 == 1:
        left, right = MARGIN_INNER, PAGE_WIDTH - MARGIN_OUTER
    else:
        left, right = MARGIN_OUTER, PAGE_WIDTH - MARGIN_INNER
    return left, MARGIN_TOP, right, PAGE_HEIGHT - MARGIN_BOTTOM


def _clusters(boxes: list[tuple[float, float, float, float]]):
    """Regroupe les fragments d'une même étiquette (numérateur, dénominateur…).

    Une fraction est composée de plusieurs fragments empilés : les compter
    comme des étiquettes distinctes ferait crier au chevauchement à tort.

    Le regroupement exige que les fragments soient VOISINS SANS SE RECOUVRIR.
    C'est ce qui empêche la mesure de s'auto-absoudre : deux étiquettes
    écrasées l'une sur l'autre se recouvrent largement, ne fusionnent donc pas,
    et sont comptées comme un chevauchement. Un regroupement par simple
    proximité les aurait avalées dans un seul « label » et aurait rendu
    TREE_OVERLAP structurellement nul — un contrôle qui ne peut pas échouer.
    """
    parents = list(range(len(boxes)))

    def find(index: int) -> int:
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def area(box) -> float:
        return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])

    def near(a, b) -> bool:
        horizontal = max(a[0], b[0]) - min(a[2], b[2])
        vertical = max(a[1], b[1]) - min(a[3], b[3])
        if horizontal > 2.0 or vertical > 4.0:
            return False
        smallest = min(area(a), area(b))
        return smallest <= 0 or _overlap_area(a, b) <= 0.15 * smallest

    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if near(boxes[i], boxes[j]):
                parents[find(i)] = find(j)

    groups: dict[int, list[tuple[float, float, float, float]]] = {}
    for index, box in enumerate(boxes):
        groups.setdefault(find(index), []).append(box)
    return [
        (
            min(b[0] for b in g),
            min(b[1] for b in g),
            max(b[2] for b in g),
            max(b[3] for b in g),
        )
        for g in groups.values()
    ]


def _overlap_area(a, b) -> float:
    width = min(a[2], b[2]) - max(a[0], b[0])
    height = min(a[3], b[3]) - max(a[1], b[1])
    return width * height if width > 0 and height > 0 else 0.0


def _measure(pdf: Path) -> list[dict]:
    fitz = pytest.importorskip("fitz")
    document = fitz.open(pdf)
    report = []
    for index, page in enumerate(document, start=1):
        zone = _text_zone(index)
        spans, sizes = [], []
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    if not span["text"].strip():
                        continue
                    spans.append(tuple(span["bbox"]))
                    sizes.append(span["size"])
        drawings = [tuple(d["rect"]) for d in page.get_drawings()]

        outside = [
            box
            for box in spans + drawings
            if box[0] < zone[0] - 0.5
            or box[1] < zone[1] - 0.5
            or box[2] > zone[2] + 0.5
            or box[3] > zone[3] + 0.5
        ]
        labels = _clusters(spans)
        overlaps = [
            (labels[i], labels[j])
            for i in range(len(labels))
            for j in range(i + 1, len(labels))
            if _overlap_area(labels[i], labels[j]) > 0.5
        ]
        report.append(
            {
                "page": index,
                "etiquettes": len(labels),
                "TREE_CLIPPING": len(outside),
                "TREE_OVERLAP": len(overlaps),
                "TREE_UNREADABLE_LABEL": sum(
                    1 for s in sizes if s < MIN_READABLE_PT
                ),
                "hors_zone": outside[:3],
                "chevauchements": overlaps[:3],
            }
        )
    document.close()
    return report


def _published_trees() -> list[str]:
    pages = []
    for number in TREE_EXERCISES:
        match = TREE_BLOCK.search(correction_text(number))
        assert match
        pages.append(match.group(0))
    return pages


@pytest.fixture(scope="module")
def rendering_report(tmp_path_factory) -> list[dict]:
    pytest.importorskip("fitz")
    tmp_path = tmp_path_factory.mktemp("arbres")
    pages = _published_trees() + list(STRESS_CASES.values())
    pdf = _compile(tmp_path, _audit_document(pages), "audit-arbres")
    return _measure(pdf)


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_rendu_aucun_trace_hors_de_la_zone_de_texte(rendering_report) -> None:
    """TREE_CLIPPING = 0, sur les sept arbres publiés et les cas difficiles."""
    faulty = [p for p in rendering_report if p["TREE_CLIPPING"]]
    assert faulty == [], f"tracés hors zone de texte : {faulty}"


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_rendu_aucun_chevauchement_d_etiquettes(rendering_report) -> None:
    """TREE_OVERLAP = 0."""
    faulty = [p for p in rendering_report if p["TREE_OVERLAP"]]
    assert faulty == [], f"étiquettes qui se chevauchent : {faulty}"


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_rendu_aucune_etiquette_illisible(rendering_report) -> None:
    """TREE_UNREADABLE_LABEL = 0."""
    faulty = [p for p in rendering_report if p["TREE_UNREADABLE_LABEL"]]
    assert faulty == [], f"corps de texte sous {MIN_READABLE_PT} pt : {faulty}"
    assert all(p["etiquettes"] >= 6 for p in rendering_report), (
        "une page d'arbre sans étiquettes signale un rendu vide"
    )


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_chaque_corrige_compile_isole_dans_l_enveloppe_du_gate_r6() -> None:
    """R6 : l'objet doit compiler seul, sous l'enveloppe REELLE du gate.

    Ce test appelait autrefois une copie de l'enveloppe ecrite en dur ici. Il
    ne pouvait donc pas voir que l'enveloppe reelle avait un defaut -- elle ne
    chargeait pas la charte -- ni que sa correction rendait la plomberie des
    corriges inutile. Il passe desormais par `check_latex` lui-meme : la
    verification suit l'enveloppe, elle ne la reinvente pas.
    """

    import sys

    manuel = ROOT / "Mathematiques" / "manuel-maths"
    sys.path.insert(0, str(manuel / "scripts"))
    from check_latex import compile_tex_files  # noqa: E402

    sources = [
        manuel / f"chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-{n}.tex"
        for n in TREE_EXERCISES
    ]
    assert compile_tex_files(sources, manuel) == 0


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_une_colonne_trop_etroite_est_signalee_et_non_subie(tmp_path) -> None:
    """Une réduction silencieuse produirait un arbre propre mais illisible.

    Le composant préfère déborder d'un avertissement que de laisser passer des
    fractions sous le seuil d'impression : il réduit pour ne pas mordre sur la
    marge, ET il nomme la cause dans le journal de compilation.
    """
    pytest.importorskip("fitz")
    etroit = (
        r"\noindent\begin{minipage}{0.30\linewidth}"
        + STRESS_CASES["colonne-etroite"]
        .replace(r"\noindent\begin{minipage}{0.62\linewidth}", "")
        .replace(r"\end{minipage}", "")
        + r"\end{minipage}"
    )
    pdf = _compile(tmp_path, _audit_document([etroit]), "audit-arbre-etroit")
    journal = (tmp_path / "audit-arbre-etroit.log").read_text(
        encoding="utf-8", errors="replace"
    )
    assert "Package nexus-arbres Warning" in journal, (
        "une réduction sous le seuil de lisibilité doit être signalée"
    )
    # Réduit, mais toujours dans la zone de texte : jamais de débordement.
    assert _measure(pdf)[0]["TREE_CLIPPING"] == 0


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_le_controle_de_chevauchement_voit_un_arbre_ecrase(tmp_path) -> None:
    """MUTATION DE RENDU : sans elle, TREE_OVERLAP = 0 ne prouverait rien.

    On resserre l'écart entre feuilles jusqu'à faire collisionner les
    étiquettes. La mesure doit alors compter des chevauchements — c'est ce qui
    établit que le zéro obtenu sur les arbres publiés est une mesure et non une
    constante.
    """
    pytest.importorskip("fitz")
    ecrase = r"""
\begin{nxarbreproba}[feuille=2, niveau=24]
  \nxarbreracine{o}
  \nxarbrenoeud{r}{o}{$R$}{$\dfrac{3}{5}$}
  \nxarbrefeuille{rs}{r}{$S$}{$\dfrac{9}{10}$}{$S \cap R$}{$\dfrac{27}{50}$}
  \nxarbrefeuille{rn}{r}{$\overline{S}$}{$\dfrac{1}{10}$}{$\overline{S} \cap R$}{$\dfrac{3}{50}$}
  \nxarbrenoeud{n}{o}{$\overline{R}$}{$\dfrac{2}{5}$}
  \nxarbrefeuille{ns}{n}{$S$}{$\dfrac{7}{10}$}{$S \cap \overline{R}$}{$\dfrac{14}{50}$}
  \nxarbrefeuille{nn}{n}{$\overline{S}$}{$\dfrac{3}{10}$}{$\overline{S} \cap \overline{R}$}{$\dfrac{6}{50}$}
\end{nxarbreproba}
"""
    pdf = _compile(tmp_path, _audit_document([ecrase]), "audit-arbre-ecrase")
    report = _measure(pdf)
    assert report[0]["TREE_OVERLAP"] > 0, (
        "un arbre écrasé DOIT être vu comme chevauchant : sinon la mesure "
        "est aveugle et le zéro publié ne vaut rien"
    )
