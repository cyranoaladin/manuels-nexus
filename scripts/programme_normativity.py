#!/usr/bin/env python3
"""Portee normative des rubriques du BO, fondee sur ce que le BO en dit.

Un type interne ne doit jamais pouvoir relever silencieusement le niveau
d'obligation d'un attendu. Appeler « capacite algorithmique » ce que le
programme intitule « Exemples d'algorithme » transformerait un exemple propose
en obligation d'implementer exactement cet exemple-la ; a l'inverse, ranger
parmi les options une rubrique que le texte dit devoir etre entretenue toute
l'annee ferait disparaitre un attendu du denominateur.

Chaque rubrique porte donc trois choses, et les trois voyagent avec l'item :

  official_heading      l'intitule exact du BO, tel qu'il est imprime
  official_normativity  la portee, prise dans le vocabulaire commun ci-dessous
  local_kind            l'etiquette interne, utile au pipeline

et une quatrieme qui les arbitre : `normativity_basis`, la phrase du programme
sur laquelle la portee s'appuie. La ou le BO ecrit « en aucun cas
obligatoires », la portee n'est pas discutable. La ou il ecrit « propose
quelques demonstrations exemplaires », la base le dit aussi, et personne ne
peut lire dans l'etiquette une exigence que le texte ne porte pas.

La normativite ne se deduit pas de la presence d'une puce : la chaine
intitule -> sous-intitule -> puce -> portee reste tracable de bout en bout.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

#: Vocabulaire commun de portee normative.
REQUIRED_CONTENT = "REQUIRED_CONTENT"
EXPECTED_CAPACITY = "EXPECTED_CAPACITY"
REQUIRED_DEMONSTRATION = "REQUIRED_DEMONSTRATION"
REQUIRED_AUTOMATISM = "REQUIRED_AUTOMATISM"
PRESCRIBED_ALGORITHMIC_WORK = "PRESCRIBED_ALGORITHMIC_WORK"
TRANSVERSAL_REQUIREMENT = "TRANSVERSAL_REQUIREMENT"
OBJECTIVE_OR_INTENT = "OBJECTIVE_OR_INTENT"
ILLUSTRATIVE_EXAMPLE = "ILLUSTRATIVE_EXAMPLE"
OPTIONAL_ENRICHMENT = "OPTIONAL_ENRICHMENT"
COMMENTARY = "COMMENTARY"

NORMATIVITIES = frozenset({
    REQUIRED_CONTENT,
    EXPECTED_CAPACITY,
    REQUIRED_DEMONSTRATION,
    REQUIRED_AUTOMATISM,
    PRESCRIBED_ALGORITHMIC_WORK,
    TRANSVERSAL_REQUIREMENT,
    OBJECTIVE_OR_INTENT,
    ILLUSTRATIVE_EXAMPLE,
    OPTIONAL_ENRICHMENT,
    COMMENTARY,
})

#: Portees qui engagent le manuel. Elles seules entrent au denominateur.
MANDATORY_NORMATIVITIES = frozenset({
    REQUIRED_CONTENT,
    EXPECTED_CAPACITY,
    REQUIRED_DEMONSTRATION,
    REQUIRED_AUTOMATISM,
    PRESCRIBED_ALGORITHMIC_WORK,
    TRANSVERSAL_REQUIREMENT,
})


@dataclass(frozen=True)
class Portee:
    normativity: str
    local_kind: str
    basis: str
    #: Vrai quand le BO impose un travail mais pas l'exemple par lequel il
    #: l'illustre. Le manuel doit traiter le sujet, pas necessairement cet
    #: algorithme-la.
    exact_example_imposed: bool = True

    @property
    def mandatory(self) -> bool:
        return self.normativity in MANDATORY_NORMATIVITIES


#: Motif d'intitule -> portee. Les motifs sont compares sur l'intitule
#: desaccentue et minuscule, sans ponctuation finale.
RULES: tuple[tuple[str, Portee], ...] = (
    (
        r"contenus?( associes?)?",
        Portee(
            REQUIRED_CONTENT,
            "KNOWLEDGE",
            "rubrique « Contenus » : ce que le programme donne a etudier.",
        ),
    ),
    (
        r"capacites? attendues?( et commentaires)?",
        Portee(
            EXPECTED_CAPACITY,
            "EXPECTED_CAPACITY",
            "rubrique « Capacites attendues » : le BO les dit attendues des eleves.",
        ),
    ),
    (
        r"demonstrations? possibles?",
        Portee(
            ILLUSTRATIVE_EXAMPLE,
            "DEMONSTRATION_SUGGESTED",
            "rubrique « Demonstrations possibles » : le mot « possibles » "
            "designe une proposition faite au professeur, non un attendu.",
            exact_example_imposed=False,
        ),
    ),
    (
        r"demonstrations?( attendues?| exigibles?)?",
        Portee(
            REQUIRED_DEMONSTRATION,
            "DEMONSTRATION",
            "« Le programme propose quelques demonstrations exemplaires, que "
            "les eleves decouvrent selon des modalites variees » : le "
            "programme prescrit qu'elles soient traitees, sans imposer la "
            "modalite ni exiger que l'eleve les restitue.",
        ),
    ),
    (
        r"exemples? d[’\']?algorithmes?",
        Portee(
            ILLUSTRATIVE_EXAMPLE,
            "ALGORITHM_EXAMPLE",
            "rubrique « Exemples d'algorithme ». Le programme nomme des "
            "EXEMPLES, et aucun passage du texte -- ni l'organisation du "
            "programme, ni la partie « Algorithmique et programmation » -- ne "
            "les rend exigibles. Ils n'entrent donc pas au denominateur des "
            "obligations. Que la partie concernee comporte un travail "
            "algorithmique suffisant releve d'une exigence de qualite propre a "
            "la collection, controlee separement.",
            exact_example_imposed=False,
        ),
    ),
    (
        r"approfondissements? possibles?|problemes? possibles?",
        Portee(
            OPTIONAL_ENRICHMENT,
            "OPTIONAL_ENRICHMENT",
            "« Le programme propose un certain nombre d'approfondissements "
            "possibles, mais en aucun cas obligatoires. »",
        ),
    ),
    (
        r"histoire des mathematiques|histoire de l[’']?informatique",
        Portee(
            COMMENTARY,
            "HISTORY_CONTEXT",
            "« Les items Histoire des mathematiques identifient quelques "
            "possibilites en ce sens. Pour les etayer, les professeurs "
            "pourront, s'ils le desirent... »",
        ),
    ),
    (
        r"objectifs?",
        Portee(
            OBJECTIVE_OR_INTENT,
            "OBJECTIVE",
            "rubrique « Objectifs » : intention pedagogique de la partie, "
            "sans attendu opposable.",
        ),
    ),
    (
        r"commentaires?",
        Portee(
            COMMENTARY,
            "COMMENTARY",
            "colonne « Commentaires » du programme de NSI : elle eclaire la "
            "mise en oeuvre et n'ajoute pas d'attendu.",
        ),
    ),
)

#: Portee des puces d'une partie entiere, quand la partie prime sur la rubrique.
SECTION_RULES: tuple[tuple[str, Portee], ...] = (
    (
        r"automatismes",
        Portee(
            REQUIRED_AUTOMATISM,
            "AUTOMATISM",
            "« Les capacites attendues enoncees ci-dessous [...] doivent etre "
            "entretenues et consolidees au cours de l'annee. » La partie est "
            "obligatoire ; c'est sa modalite, repartie sur l'annee, qui la "
            "distingue d'un chapitre.",
        ),
    ),
)

#: Portee d'une liste d'attendus que le BO n'a pas intitulee.
DEFAULT = Portee(
    EXPECTED_CAPACITY,
    "EXPECTED_CAPACITY",
    "liste d'attendus enoncee sans intitule de rubrique : le BO la place au "
    "meme rang que ses capacites attendues.",
)

#: Portee des passages du preambule, declaree passage par passage sur la foi
#: de ce que le texte fait. Le programme DECRIT les competences que
#: l'enseignement developpe (« Il permet de developper des competences : »,
#: « Cet enseignement a vocation a multiplier les occasions... ») ; il PRESCRIT
#: en revanche la demarche de projet (« Un quart au moins de l'horaire [...]
#: est reserve »). Les compter ensemble ferait entrer une intention pedagogique
#: dans le denominatur des obligations du manuel.
PREAMBLE_PASSAGE_SCOPES: dict[str, "Portee"] = {}  # rempli plus bas

PROJECT_REQUIREMENT = Portee(
    TRANSVERSAL_REQUIREMENT,
    "TRANSVERSAL_REQUIREMENT",
    "partie prescriptive du preambule : « Un quart au moins de l'horaire "
    "total de la specialite est reserve a la conception et a l'elaboration "
    "de projets conduits par les eleves. »",
)


PREAMBLE_INTENT = Portee(
    OBJECTIVE_OR_INTENT,
    "OBJECTIVE",
    "passage du preambule qui DECRIT ce que l'enseignement developpe, sans "
    "imposer d'attendu au manuel : « Il permet de developper des competences », "
    "« Cet enseignement a vocation a multiplier les occasions... », « cette "
    "specialite contribue au developpement des competences orales ».",
)


def for_preamble_passage(slug: str) -> Portee:
    """Portee d'un passage du preambule, d'apres ce que le texte y fait."""
    return PREAMBLE_PASSAGE_SCOPES.get(slug, PREAMBLE_INTENT)


def _cle(intitule: str) -> str:
    sans = unicodedata.normalize("NFKD", intitule)
    sans = "".join(c for c in sans if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sans).strip().lower().rstrip(" :.")


def for_section(section: str | None) -> Portee | None:
    if not section:
        return None
    cle = _cle(section)
    for motif, portee in SECTION_RULES:
        if re.fullmatch(motif, cle):
            return portee
    return None


def for_heading(heading: str | None) -> Portee | None:
    if not heading:
        return None
    cle = _cle(heading)
    for motif, portee in RULES:
        if re.fullmatch(motif, cle):
            return portee
    return None


def resolve(section: str | None, heading: str | None) -> Portee:
    """Portee d'une puce, de la partie la plus englobante a la rubrique.

    La partie prime sur la rubrique : dans « Automatismes », le BO intitule
    ses listes « Capacites attendues » tout en precisant qu'elles relevent
    d'un entrainement reparti sur l'annee et non d'un chapitre. Lire la
    rubrique seule effacerait cette difference.
    """
    return for_section(section) or for_heading(heading) or DEFAULT
