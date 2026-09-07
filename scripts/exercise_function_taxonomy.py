#!/usr/bin/env python3
"""La FONCTION pedagogique d'un exercice, lue dans ce qu'il demande.

Compter les exercices ne dit rien ; compter les competences declarees ne dit
guere plus. La question qui decide est celle-ci : l'eleve dispose-t-il
d'assez de SITUATIONS DIFFERENTES pour transferer la competence, ou repete-t-il
une procedure ?

Huit fonctions, lues sur des marqueurs du corpus -- ce que l'enonce demande,
le parcours declare, la competence declaree. Un exercice en porte souvent
plusieurs : appliquer une formule dans un contexte concret est a la fois une
application et une modelisation.

`DIRECT_APPLICATION`  appliquer une formule ou une methode sur des donnees
                      nues, sans habillage.
`CONTEXT_VARIATION`   le meme geste dans une situation concrete nommee --
                      une usine, un lot, un trajet.
`METHOD_TRANSFER`     l'enonce impose un chemin different de celui de la
                      fiche methode : « de deux facons », « sans utiliser ».
`REASONING`           demontrer, justifier, prouver, deduire.
`PROBLEM_SOLVING`     plusieurs etapes enchainees vers un resultat non donne.
`SYNTHESIS`           croiser plusieurs capacites ou plusieurs chapitres.
`EDGE_CASE`           cas limite, contre-exemple, condition de validite,
                      degenerescence.
`MODELLING`           traduire une situation en objet mathematique.

LA SUFFISANCE N'EST PAS UN QUOTA. Une capacite est suffisamment entrainee
lorsqu'elle dispose d'au moins une application directe ET d'au moins une
fonction de TRANSFERT -- raisonnement, transfert de methode, resolution de
probleme, synthese, cas limite, modelisation ou variation de contexte. Un
exercice direct et un exercice de raisonnement suffisent ; deux exercices
directs ne suffisent pas, quel qu'en soit le nombre.
"""

from __future__ import annotations

import re
from typing import Any

DIRECT = "DIRECT_APPLICATION"
CONTEXT = "CONTEXT_VARIATION"
TRANSFER = "METHOD_TRANSFER"
REASONING = "REASONING"
PROBLEM = "PROBLEM_SOLVING"
SYNTHESIS = "SYNTHESIS"
EDGE = "EDGE_CASE"
MODELLING = "MODELLING"

FUNCTIONS = (DIRECT, CONTEXT, TRANSFER, REASONING, PROBLEM, SYNTHESIS, EDGE, MODELLING)

#: Les fonctions qui font TRANSFERER plutot que repeter.
TRANSFER_FUNCTIONS = frozenset(
    {CONTEXT, TRANSFER, REASONING, PROBLEM, SYNTHESIS, EDGE, MODELLING}
)

#: Les verbes ont ete releves sur le corpus, pas devines : « montrer » y
#: apparait cent-quatre-vingt-quinze fois, « expliquer » vingt-six,
#: « interpreter » vingt-quatre. N'en reconnaitre qu'une partie faisait voir
#: des chapitres sans raisonnement la ou l'enonce en demandait un.
_RAISONNER = re.compile(
    r"\bd[ée]montrer\b|\bmontrer\b|\bprouver\b|\bjustifier\b|"
    r"\ben d[ée]duire\b|\br[ée]currence\b|\bconclure\b|\bexpliquer\b|"
    r"\binterpr[ée]ter\b|\bpourquoi\b|\bcomparer\b|\bcommenter\b|"
    r"\bargumenter\b|\bcritiquer\b",
    re.I,
)
_TRANSFERT = re.compile(
    r"de deux (?:fa[çc]ons|mani[èe]res)|sans utiliser|autrement|"
    r"retrouver (?:le|la|ce) r[ée]sultat|v[ée]rifier le r[ée]sultat|"
    r"comparer les deux",
    re.I,
)
_LIMITE = re.compile(
    r"cas limite|contre-exemple|\bimpossible\b|n'existe pas|"
    r"condition (?:de validit|n[ée]cessaire)|\bd[ée]g[ée]n[ée]r|"
    r"pourquoi (?:ne|n')|\bechoue\b|\b[ée]choue\b|pire cas",
    re.I,
)
_CONTEXTE = re.compile(
    r"\busine\b|\bmagasin\b|\bentrep[ôo]t\b|\bville\b|\bpopulation\b|"
    r"\bclub\b|\bh[ôo]pital\b|\b[ée]quipe\b|\bfleuriste\b|\bcapital\b|"
    r"\bplacement\b|\bbillet|\bproduction\b|\babonn|\bpatient|\bmachine\b|"
    r"\bv[ée]lo\b|\blot\b|\bpi[èe]ces?\b|\bstock\b|\bstandard\b|\bcomposant\b|"
    r"\bpolluant\b|\bbact[ée]rie|\bd[ée]bit\b|\btournoi\b|\bcarrefour\b|"
    r"\bservices?\b|\bdossiers?\b|\bgrande roue\b|\bfour\b|\bco[ûu]t\b",
    re.I,
)
_MODELISER = re.compile(
    r"\bmod[ée]lis|\btraduire\b|\bexprimer\b.{0,40}\ben fonction d[eu]\b|"
    r"\ben fonction d[eu]\b.{0,30}\b(?:temps|instant|nombre|quantit)|"
    r"\b[ée]crire\b.{0,30}\bsous la forme\b",
    re.I,
)
_DIRECT = re.compile(
    r"\bcalculer\b|\bd[ée]terminer\b|\bdonner (?:la|le|les|l')|"
    r"que (?:renvoie|vaut|retourne)|\bappliquer\b|\beffectuer\b|"
    r"\bsimplifier\b|\bd[ée]velopper\b|\bfactoriser\b|\bd[ée]river\b|"
    r"\bex[ée]cuter\b|\b[ée]valuer\b|\bcompl[ée]ter\b|\bdresser\b|"
    r"\br[ée]soudre\b|\b[ée]crire\b|\btraduire\b|\br[ée]diger\b|"
    r"\bconvertir\b|\bcodera?\b|\bd[ée]nombrer\b|\bd[ée]composer\b|"
    r"\bconstruire\b|\btracer\b|\bplacer\b|\brepr[ée]senter\b|"
    r"\bv[ée]rifier\b|\bencadrer\b|\bmajorer\b|\bminorer\b|"
    r"\bint[ée]grer\b|\bsimuler\b|\bexprimer\b|\b[ée]tudier\b|"
    r"\bidentifier\b|\btester\b|\br[ée]{1,2}crire\b|\bestimer\b|"
    r"\breconna[îi]tre\b|\brappeler\b|\besquisser\b|\bmodifier\b|"
    r"\bmettre\b.{0,25}\bsous (?:la|cette) forme\b",
    re.I,
)
_ETAPES = re.compile(r"\\item", re.I)
#: Les blocs oracle sont du code de verification, pas un enonce ; les lire
#: comme du texte pedagogique ferait dire n'importe quoi au classifieur.
_ORACLE = re.compile(r"^%.*$", re.M)


def functions_of(body: str, meta: dict[str, Any]) -> list[str]:
    """Les fonctions pedagogiques que cet exercice remplit reellement."""

    body = _ORACLE.sub("", body)
    competences = set(meta.get("competences") or [])
    parcours = meta.get("parcours")
    etapes = len(_ETAPES.findall(body))
    trouvees: set[str] = set()

    if _RAISONNER.search(body) or "raisonner" in competences:
        trouvees.add(REASONING)
    if _TRANSFERT.search(body):
        trouvees.add(TRANSFER)
    if _LIMITE.search(body):
        trouvees.add(EDGE)
    if _CONTEXTE.search(body):
        trouvees.add(CONTEXT)
    if _MODELISER.search(body) or "modeliser" in competences:
        trouvees.add(MODELLING)
    if etapes >= 3 and parcours and parcours >= 2:
        trouvees.add(PROBLEM)
    if len(meta.get("capacites_codes") or []) >= 2:
        trouvees.add(SYNTHESIS)
    # Une application directe se LIT : l'enonce demande d'executer un geste
    # -- calculer, determiner, appliquer, ecrire la fonction. Elle n'est pas
    # seulement un residu : un exercice contextualise qui demande d'abord de
    # calculer entraine bel et bien le geste de base, et le classer « pas
    # d'application directe » ferait voir une lacune la ou il n'y en a pas.
    # Le residu reste, pour l'enonce nu qui ne porte aucun marqueur.
    if _DIRECT.search(body) or "calculer" in competences or not (trouvees - {SYNTHESIS}):
        trouvees.add(DIRECT)
    return sorted(trouvees)


#: Une capacite dont l'enonce EST un raisonnement -- « je sais demontrer des
#: inegalites », « je sais expliquer pourquoi » -- n'a pas d'application
#: directe separee : le geste de base y est la demonstration. Exiger un
#: exercice calculatoire en plus ferait voir une lacune la ou le programme
#: n'en demande pas.
_CAPACITE_RAISONNEMENT = re.compile(
    r"\bd[ée]montrer\b|\bprouver\b|\bjustifier\b|\bexpliquer\b|"
    r"\b[ée]tablir\b|\binterpr[ée]ter\b|\bcritiquer\b",
    re.I,
)
#: Une capacite qui nomme UN resultat precis -- le theoreme de Gauss, le petit
#: theoreme de Fermat -- n'a qu'une instance. Lui reclamer une seconde
#: situation serait un quota, pas une exigence de diversite.
_CAPACITE_SINGULIERE = re.compile(
    r"le (?:petit )?th[ée]or[èe]me d[eu]\b|la propri[ée]t[ée] d[eu]\b|"
    r"l'?identit[ée] d[eu]\b|le lemme d[eu]\b|la formule d[eu]\b|"
    r"le crit[èe]re d[eu]\b|l'?algorithme d'Euclide\b",
    re.I,
)


def capacity_entry_function(libelle: str) -> str:
    """Le geste de base de CETTE capacite, lu dans son enonce officiel."""

    return REASONING if _CAPACITE_RAISONNEMENT.search(libelle or "") else DIRECT


def is_singular_capacity(libelle: str) -> bool:
    """La capacite ne porte-t-elle que sur un unique resultat nomme ?"""

    return bool(_CAPACITE_SINGULIERE.search(libelle or ""))


def diversity_verdict(
    par_exercice: list[list[str]], libelle: str = ""
) -> dict[str, Any]:
    """Une capacite est-elle suffisamment entrainee ?

    Deux conditions, et AUCUNE n'est un effectif :

    1. le GESTE DE BASE de la capacite est present -- application directe pour
       une capacite calculatoire, demonstration pour une capacite de
       raisonnement, selon ce que l'enonce officiel reclame ;
    2. au moins une AUTRE fonction pedagogique est presente, faute de quoi
       l'eleve repete un seul mode.

    On a essaye d'y ajouter « au moins deux exercices », au motif qu'une
    variation entre une seule situation n'existe pas. C'etait la regle « une
    capacite -> deux exercices » deguisee : elle declarait une lacune sur un
    exercice en cinq questions qui installait le geste, changeait de contexte,
    imposait un autre chemin et demandait une justification. Ce que compte ce
    contrat, ce sont les fonctions, pas les fichiers.

    Une capacite servie par deux exercices bien choisis le satisfait ; une
    capacite servie par dix applications directes ne le satisfait pas.
    """

    entree = capacity_entry_function(libelle)
    singuliere = is_singular_capacity(libelle)
    presentes = {f for fonctions in par_exercice for f in fonctions}
    a_entree = entree in presentes
    autres = sorted(presentes - {entree})
    transferts = sorted(presentes & TRANSFER_FUNCTIONS)
    manque = []
    if not a_entree:
        manque.append(
            "aucune demonstration" if entree == REASONING
            else "aucune application directe"
        )
    if not autres:
        manque.append("un seul mode d'exercice")

    return {
        "functions_present": sorted(presentes),
        "entry_function": entree,
        "singular_capacity": singuliere,
        "transfer_functions": transferts,
        "verdict": "DIVERSITY_SUFFICIENT" if not manque else "REAL_DIVERSITY_GAP",
        "missing": manque,
    }
