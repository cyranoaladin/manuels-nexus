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

_RAISONNER = re.compile(
    r"\bd[ée]montrer\b|\bmontrer que\b|\bprouver\b|\bjustifier\b|"
    r"\ben d[ée]duire\b|\br[ée]currence\b|\bconclure\b",
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
    r"\bmod[ée]lis|\btraduire\b|\bexprimer\b.{0,40}\ben fonction de\b|"
    r"\b[ée]crire\b.{0,30}\bsous la forme\b",
    re.I,
)
_DIRECT = re.compile(
    r"\bcalculer\b|\bd[ée]terminer\b|\bdonner (?:la|le|les|l')|"
    r"que (?:renvoie|vaut|retourne)|\bappliquer\b|\beffectuer\b|"
    r"\bsimplifier\b|\bd[ée]velopper\b|\bfactoriser\b|\bd[ée]river\b|"
    r"\bex[ée]cuter\b|\b[ée]valuer\b|\bcompl[ée]ter\b|\bdresser\b|"
    r"r[ée]soudre (?:l'|l’)?(?:[ée]quation|in[ée]quation|le syst)|"
    r"[ée]crire (?:la|une|le) (?:fonction|programme|script|proc[ée]dure)|"
    r"\br[ée]diger\b|\bconvertir\b|\bcodera?\b|\bd[ée]nombrer\b",
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


def diversity_verdict(par_exercice: list[list[str]]) -> dict[str, Any]:
    """Une capacite est-elle suffisamment entrainee ?

    Il faut une application directe ET au moins une fonction de transfert.
    Le nombre d'exercices n'entre pas dans la regle : c'est ce que la cible
    de cinquante avait fait croire, et c'est ce qu'on ne refera pas.
    """

    presentes = {f for fonctions in par_exercice for f in fonctions}
    a_direct = DIRECT in presentes
    transferts = sorted(presentes & TRANSFER_FUNCTIONS)
    suffisant = bool(a_direct and transferts)
    manque = []
    if not a_direct:
        manque.append("aucune application directe")
    if not transferts:
        manque.append("aucune situation de transfert")
    return {
        "functions_present": sorted(presentes),
        "transfer_functions": transferts,
        "verdict": "DIVERSITY_SUFFICIENT" if suffisant else "REAL_DIVERSITY_GAP",
        "missing": manque,
    }
