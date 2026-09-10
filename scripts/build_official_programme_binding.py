#!/usr/bin/env python3
"""Rattache chaque atome du referentiel interne a l'item officiel dont il releve.

L'inventaire officiel dit ce que le programme exige. Le referentiel interne dit
ce que les manuels declarent travailler. Tant que les deux ne sont pas relies
objet par objet, aucune affirmation de couverture n'est verifiable : compter
les atomes internes reviendrait a mesurer le manuel avec sa propre regle.

Le rattachement est etabli, jamais suppose, et son MODE est publie avec lui :

  ANCHOR   l'atome cite ses coordonnees dans le texte officiel (partie,
           rubrique, rang de la puce). Le lien est alors exact et rejouable.
  VERBATIM l'atome reprend mot pour mot le libelle officiel.
  PROPOSED aucun des deux : le rapprochement le mieux note est publie comme
           PROPOSITION, avec sa mesure et ses concurrents, et ne vaut pas
           couverture tant qu'un humain ne l'a pas tranche.

Cette distinction n'est pas une precaution de forme. Le champ `libelle_bo` du
referentiel interne porte un nom qui laisse croire au texte du BO, mais il en
est une reformulation dans la grande majorite des cas -- et le referentiel
decoupe parfois en deux atomes ce que le programme enonce en une seule capacite
(« Calculer la taille et la hauteur d'un arbre »). Traiter ces libelles comme
officiels ferait passer une reecriture pour une preuve, et le decoupage interne
pour une couverture plus large que le programme.
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
INDEX = ROOT / "audit" / "OFFICIAL_PROGRAMME_INVENTORY.json"
OUT = ROOT / "audit" / "OFFICIAL_PROGRAMME_BINDING.json"

REFERENTIELS = (
    ROOT / "Mathematiques" / "manuel-maths" / "referentiel",
    ROOT / "NSI" / "referentiel",
)
#: Coordonnees citees par un ancrage : « sous-partie / rubrique / puce N ».
ANCHOR = re.compile(r"^(?P<sub>.+?)\s*/\s*(?P<rub>[^/]+?)\s*/\s*puce\s*(?P<n>\d+)\s*$")
#: Mots-outils du francais : leur presence ne rapproche pas deux libelles.
VIDES = {
    "les", "des", "une", "der", "aux", "que", "qui", "pour", "dans", "sur",
    "avec", "par", "son", "sont", "est", "ont", "the", "and", "leur", "leurs",
    "ses", "cette", "aussi", "plus", "moins", "entre", "deux", "elle", "ils",
}
#: En dessous, le rapprochement n'a pas de sens : on ne propose rien.
PLANCHER = 0.18


def strip_accents(texte: str) -> str:
    sans = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in sans if not unicodedata.combining(c))


def normalise(texte: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", texte)).strip()


#: Equivalences typographiques. Le BO compose ses apostrophes en courbe, ses
#: variables en italique mathematique et son f de fonction en U+0192 ; le
#: referentiel interne saisit les memes phrases au clavier. Comparer les deux
#: caractere pour caractere faisait passer pour des reformulations des libelles
#: rigoureusement identiques -- « Resoudre un probleme d'optimisation. » n'y
#: differait de l'officiel que par la forme de son apostrophe.
TYPOGRAPHIE = {
    "\u2019": "'", "\u2018": "'", "\u201b": "'", "\u2032": "'",
    "\u201c": '"', "\u201d": '"', "\u00ab": '"', "\u00bb": '"',
    "\u0192": "f", "\u2212": "-", "\u2013": "-", "\u2014": "-",
    "\u00a0": " ", "\u202f": " ", "\u2009": " ",
}


def forme_typographique(texte: str) -> str:
    """Cle de comparaison : meme phrase, quelle que soit sa composition.

    Les blancs sont retires : « f(a+h) » et « f (a + h) » sont le meme
    attendu. Le risque de collision entre deux phrases distinctes est nul a
    cette longueur, alors que le risque de manquer une identite reelle, lui,
    etait avere.
    """
    texte = unicodedata.normalize("NFKC", texte)
    texte = "".join(TYPOGRAPHIE.get(c, c) for c in texte)
    # Les accents sont replies eux aussi. Plusieurs referentiels sont saisis
    # sans accents (« Ecrire la definition d'une classe »), et deux phrases
    # francaises distinctes ne different jamais par les seuls accents : a
    # l'echelle d'un enonce entier, le risque de collision est nul, alors que
    # le risque de manquer une identite reelle, lui, etait avere.
    texte = "".join(
        c for c in unicodedata.normalize("NFKD", texte)
        if not unicodedata.combining(c)
    )
    return re.sub(r"\s+", "", texte).lower()


def jetons(texte: str) -> set[str]:
    mots = re.findall(r"[a-z0-9]+", strip_accents(texte).lower())
    return {m for m in mots if len(m) >= 3 and m not in VIDES}


def proximite(a: set[str], b: set[str]) -> float:
    """Recouvrement de Jaccard : mesure simple, publiee, et donc contestable."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def charger_officiels() -> tuple[dict[str, list[dict[str, Any]]], dict[str, str]]:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    par_manuel: dict[str, list[dict[str, Any]]] = defaultdict(list)
    autorites: dict[str, str] = {}
    for entree in index["documents"]:
        if not entree["applies_to_edition"]:
            continue
        autorites[entree["manual"]] = entree["authority_ref"]
        charge = json.loads((ROOT / entree["inventory_path"]).read_text(encoding="utf-8"))
        par_manuel[entree["manual"]].extend(charge["items"])
    return par_manuel, autorites


def charger_atomes() -> list[dict[str, Any]]:
    atomes: list[dict[str, Any]] = []
    for dossier in REFERENTIELS:
        for chemin in sorted(dossier.glob("capacites_*.json")):
            charge = json.loads(chemin.read_text(encoding="utf-8"))
            for capacite in charge.get("capacites", []):
                atomes.append({
                    "atom_id": capacite["id"],
                    "manual": charge.get("niveau"),
                    "theme": charge.get("theme"),
                    "referential_path": str(chemin.relative_to(ROOT)),
                    "bo_reference": charge.get("bo_reference", ""),
                    "declared_authority": (charge.get("authority") or {}).get("nor"),
                    # `libelle_bo` est deprecie : son nom affirme un texte
                    # officiel qu'il ne porte pas dans la plupart des cas. On
                    # lit la formulation interne sous son vrai nom, et on
                    # transporte le verdict d'authenticite avec elle.
                    "libelle_interne": capacite.get(
                        "libelle_interne", capacite.get("libelle_bo", "")
                    ),
                    "libelle_bo_is_verbatim": capacite.get(
                        "libelle_bo_is_verbatim", False
                    ),
                    "contenu_bo": capacite.get("contenu_bo"),
                    "source_anchor": capacite.get("source_anchor"),
                })
    return atomes


def resoudre_ancrage(
    ancrage: str, items: list[dict[str, Any]]
) -> dict[str, Any] | None:
    m = ANCHOR.match(normalise(ancrage))
    if not m:
        return None
    sub = strip_accents(m["sub"]).lower()
    rub = strip_accents(m["rub"]).lower()
    rang = int(m["n"])
    for item in items:
        contexte = item["official_subsection"] or item["official_section"] or ""
        if (
            strip_accents(contexte).lower() == sub
            and strip_accents(item["official_rubric"]).lower() == rub
            and item["official_rubric_index"] == rang
        ):
            return item
    return None


def lier(atome: dict[str, Any], items: list[dict[str, Any]]) -> dict[str, Any]:
    if atome["source_anchor"]:
        cible = resoudre_ancrage(atome["source_anchor"], items)
        if cible is not None:
            return {
                "binding_method": "ANCHOR",
                "official_id": cible["official_id"],
                "official_ids": [cible["official_id"]],
                "official_wording": cible["official_wording"],
                "official_kind": cible["kind"],
                "binding_score": 1.0,
                "review_status": "CONFIRMED_BY_SOURCE_ANCHOR",
                "candidates": [],
            }
        return {
            "binding_method": "ANCHOR_UNRESOLVABLE",
            "official_id": None,
            "official_wording": None,
            "official_kind": None,
            "binding_score": 0.0,
            "review_status": "ANCHOR_DOES_NOT_RESOLVE_IN_THE_OFFICIAL_TEXT",
            "candidates": [],
        }

    libelle = normalise(atome["libelle_interne"])
    if libelle:
        cle = forme_typographique(libelle)
        for item in items:
            if forme_typographique(item["official_wording"]) == cle:
                return {
                    "binding_method": "VERBATIM",
                    "official_id": item["official_id"],
                    "official_ids": [item["official_id"]],
                    "official_wording": item["official_wording"],
                    "official_kind": item["kind"],
                    "binding_score": 1.0,
                    "review_status": "CONFIRMED_BY_VERBATIM_OFFICIAL_WORDING",
                    "candidates": [],
                }

    reference = jetons(libelle) | jetons(
        " ".join(atome["contenu_bo"])
        if isinstance(atome["contenu_bo"], list)
        else (atome["contenu_bo"] or "")
    )
    # Les candidats ne sont pas limites aux attendus obligatoires. Un atome
    # peut relever legitimement d'un « Probleme possible » ou d'un
    # approfondissement : l'ecarter d'office le laissait sans parent et faisait
    # passer un enrichissement assume pour une invention interne.
    notes = sorted(
        ((proximite(reference, jetons(i["official_wording"])), i) for i in items),
        key=lambda t: (-t[0], t[1]["official_id"]),
    )[:3]
    if not notes or notes[0][0] < PLANCHER:
        return {
            "binding_method": "NONE",
            "official_id": None,
            "official_wording": None,
            "official_kind": None,
            "binding_score": round(notes[0][0], 3) if notes else 0.0,
            "review_status": "NO_OFFICIAL_PARENT_FOUND",
            "candidates": [],
        }
    return {
        "binding_method": "PROPOSED",
        "official_id": None,
        "official_wording": None,
        "official_kind": None,
        "binding_score": round(notes[0][0], 3),
        "review_status": "PROPOSED_REQUIRES_HUMAN_CONFIRMATION",
        "candidates": [
            {
                "official_id": i["official_id"],
                "official_wording": i["official_wording"],
                "kind": i["kind"],
                "score": round(s, 3),
            }
            for s, i in notes
        ],
    }



#: Seconde passe : au-dela de ce recouvrement, et avec cette avance sur le
#: concurrent immediat, un rapprochement pris DANS la partie officielle du
#: chapitre n'est plus une conjecture. Le contexte fait le plus gros du
#: travail : il ne reste a departager que des attendus voisins d'une meme
#: sous-partie.
SEUIL_CONTEXTE = 0.30
MARGE_CONTEXTE = 0.10
#: Rapprochement d'un nom de theme interne avec un intitule officiel.
SEUIL_NOM_DE_THEME = 0.45
#: Portees officielles qui designent un savoir-faire, par opposition a un
#: contenu a connaitre. Le referentiel interne est un referentiel de
#: capacites : a egalite, son parent est du cote du faire.
NORMATIVITES_DE_SAVOIR_FAIRE = frozenset({
    "EXPECTED_CAPACITY",
    "REQUIRED_DEMONSTRATION",
    "REQUIRED_AUTOMATISM",
    "PRESCRIBED_ALGORITHMIC_WORK",
})


def portee(item: dict[str, Any]) -> str:
    """Partie officielle a laquelle un attendu appartient."""
    return item["official_subsection"] or item["official_section"] or ""


def portees_de_theme(
    liens: list[dict[str, Any]], officiels: dict[str, list[dict[str, Any]]]
) -> dict[tuple[str, str], dict[str, Any]]:
    """Determine, pour chaque theme interne, la ou les parties qu'il traite.

    Un chapitre ne se promene pas dans tout le programme. Etablir la partie
    qu'il traite permet de trancher des dizaines de rapprochements qui, pris
    isolement, se ressemblaient tous : « Calculer la derivee d'une somme » et
    « Calculer la derivee d'un produit » ne se departagent pas au recouvrement
    de mots, mais ne posent aucun probleme une fois la sous-partie connue.

    La portee est un ENSEMBLE, pas une partie unique. Un chapitre couvre
    parfois deux parties du programme -- « Nombres complexes, trigonometrie et
    polynomes » en recouvre trois a lui seul -- et le forcer sur une seule
    laissait sans parent tout ce qui relevait des autres.

    Trois preuves concourent, et chacune est publiee avec la partie qu'elle
    designe : une portee sans preuve ne vaudrait pas mieux qu'une supposition.
    """
    resultat: dict[tuple[str, str], dict[str, Any]] = {}
    themes = sorted({(x["manual"], x["theme"]) for x in liens if x["manual"]})
    par_theme: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for lien in liens:
        if lien["manual"]:
            par_theme[(lien["manual"], lien["theme"])].append(lien)

    index: dict[str, dict[str, dict[str, Any]]] = {
        manuel: {i["official_id"]: i for i in items}
        for manuel, items in officiels.items()
    }

    for manuel, theme in themes:
        items = officiels.get(manuel, [])
        if not items:
            continue
        atomes = par_theme[(manuel, theme)]
        preuves: list[dict[str, str]] = []
        cibles: set[str] = set()

        # 1. La ou les liens deja etablis atterrissent.
        atterrissages = Counter(
            portee(index[manuel][a["official_id"]])
            for a in atomes
            if a["binding_method"] in ("ANCHOR", "VERBATIM") and a["official_id"]
        )
        # Ordre fixe : l'iteration d'un ensemble de chaines varie d'un
        # processus a l'autre, et l'artefact cesserait d'etre reproductible.
        for cible, n in sorted(atterrissages.items()):
            cibles.add(cible)
            preuves.append({
                "scope": cible,
                "method": "ESTABLISHED_BINDINGS_LAND_HERE",
                "evidence": f"{n} lien(s) etabli(s) de ce theme y atterrissent",
            })

        # 2. Un contenu du BO recopie mot pour mot designe sa partie.
        formes = {forme_typographique(i["official_wording"]): i for i in items}
        for atome in atomes:
            contenus = atome["contenu_bo"]
            textes = contenus if isinstance(contenus, list) else [contenus or ""]
            for texte in textes:
                cible_item = formes.get(forme_typographique(texte or ""))
                if cible_item is not None and portee(cible_item) not in cibles:
                    cibles.add(portee(cible_item))
                    preuves.append({
                        "scope": portee(cible_item),
                        "method": "CONTENU_BO_QUOTED_VERBATIM",
                        "evidence": (
                            f"l'atome {atome['atom_id']} recopie mot pour mot "
                            f"un contenu de cette partie"
                        ),
                    })

        # 3. Le nom du theme recoupe l'intitule d'une partie officielle.
        #    L'inclusion compte autant que le recouvrement : « SUITES » est
        #    contenu dans « Suites numeriques, modeles discrets » sans lui
        #    ressembler beaucoup, et « DERIVATION-GLOBAL » contient
        #    « Derivation ».
        jt = jetons(theme.replace("-", " "))
        for cible in sorted({portee(i) for i in items if portee(i)}):
            js = jetons(cible)
            if not js or cible in cibles:
                continue
            inclus = jt <= js or js <= jt
            note = proximite(jt, js)
            if inclus or note >= SEUIL_NOM_DE_THEME:
                cibles.add(cible)
                preuves.append({
                    "scope": cible,
                    "method": "THEME_NAME_MATCHES_OFFICIAL_HEADING",
                    "evidence": (
                        f"« {theme} » et « {cible} » "
                        + ("s'incluent l'un l'autre" if inclus
                           else f"se recouvrent a {note:.2f}")
                    ),
                })

        if cibles:
            resultat[(manuel, theme)] = {
                "scopes": sorted(cibles),
                "evidence": preuves,
            }
    return resultat


def relire_par_contexte(
    lien: dict[str, Any],
    items: list[dict[str, Any]],
    portee_theme: dict[str, Any] | None,
) -> dict[str, Any]:
    """Seconde passe sur un rapprochement reste en suspens.

    CONFIRMED_BY_CONTEXT n'est pas HUMAN_APPROVED : c'est un rattachement
    etabli objectivement par la structure des deux sources -- la partie du
    programme que le chapitre traite, et le libelle de l'attendu a
    l'interieur de cette partie. La preuve est publiee avec le verdict.
    """
    if portee_theme is None:
        return {
            "review_status": "AMBIGUOUS_REQUIRES_HUMAN",
            "context_reason": "la partie officielle traitee par ce theme n'est pas etablie",
            "rejected_candidates": [],
        }
    cibles = set(portee_theme["scopes"])
    reference = jetons(lien["libelle_interne"]) | jetons(
        " ".join(lien["contenu_bo"])
        if isinstance(lien["contenu_bo"], list)
        else (lien["contenu_bo"] or "")
    )
    dedans = sorted(
        (
            (proximite(reference, jetons(i["official_wording"])), i)
            for i in items
            if portee(i) in cibles
        ),
        key=lambda t: (-t[0], t[1]["official_id"]),
    )
    # Un candidat propose hors de la partie traitee par le chapitre est un
    # mauvais rapprochement : il ferait migrer un attendu d'un chapitre a
    # l'autre sans que personne ne l'ait decide.
    rejetes = [
        {
            "official_id": c["official_id"],
            "official_wording": c["official_wording"],
            "score": c["score"],
            "reason": "REJECTED_WRONG_MATCH",
            "explanation": (
                "hors de "
                + ", ".join(f"« {c} »" for c in sorted(cibles))
                + " : la ou les parties que ce theme traite"
            ),
        }
        for c in lien.get("candidates", [])
        if c["official_id"] not in {i["official_id"] for _, i in dedans}
    ]
    if not dedans:
        return {
            "review_status": "AMBIGUOUS_REQUIRES_HUMAN",
            "context_reason": (
                "aucun attendu officiel dans "
                + ", ".join(f"« {c} »" for c in sorted(cibles))
            ),
            "rejected_candidates": rejetes,
        }
    # Un atome interne est souvent PLUS ETROIT que l'attendu officiel : le
    # referentiel decoupe « Parcourir un arbre de differentes facons (ordres
    # infixe, prefixe ou suffixe ; ordre en largeur d'abord) » en un atome par
    # parcours. Quand tous les mots pleins de l'atome se retrouvent dans un
    # seul attendu de la partie, le rattachement n'est plus une conjecture :
    # c'est une subdivision, et le recouvrement de Jaccard la sous-estimait
    # justement parce que l'attendu officiel dit davantage.
    # Le test d'inclusion porte sur le seul libelle de l'atome, pas sur
    # l'union avec son `contenu_bo` : ce dernier recopie parfois des pans
    # entiers du programme, et l'ensemble ainsi grossi n'est jamais inclus
    # nulle part.
    propre = jetons(lien["libelle_interne"])
    if len(propre) >= 3:
        englobants = [
            (sc, i) for sc, i in dedans if propre <= jetons(i["official_wording"])
        ]
        if len(englobants) == 1:
            sc, item = englobants[0]
            return {
                "binding_method": "CONTEXT",
                "official_id": item["official_id"],
                "official_ids": [item["official_id"]],
                "official_wording": item["official_wording"],
                "official_kind": item["kind"],
                "binding_score": round(sc, 3),
                "review_status": "CONFIRMED_BY_CONTEXT",
                "context_reason": (
                    "tous les mots pleins de l'atome figurent dans le seul "
                    f"attendu « {item['official_wording'][:70]} » de "
                    + ", ".join(f"« {c} »" for c in sorted(cibles))
                    + " : l'atome en est une subdivision"
                ),
                "rejected_candidates": rejetes,
                "candidates": [
                    {
                        "official_id": i["official_id"],
                        "official_wording": i["official_wording"],
                        "kind": i["kind"],
                        "score": round(s2, 3),
                    }
                    for s2, i in dedans[:3]
                ],
            }

    # Cas inverse : l'atome est PLUS LARGE que les attendus officiels et en
    # recouvre plusieurs. « Representer un nuage de points. Calculer les
    # coordonnees d'un point moyen. » fusionne trois enonces du BO. Le
    # programme ne s'en trouve pas mieux couvert -- le denominateur reste le
    # sien --, mais l'atome a bien plusieurs parents, et lui en imposer un
    # seul aurait laisse les autres orphelins.
    recouverts = [
        (sc, i) for sc, i in dedans
        if jetons(i["official_wording"]) and jetons(i["official_wording"]) <= propre
    ]
    if len(recouverts) >= 2:
        return {
            "binding_method": "CONTEXT",
            "official_id": recouverts[0][1]["official_id"],
            "official_ids": [i["official_id"] for _, i in recouverts],
            "official_wording": recouverts[0][1]["official_wording"],
            "official_kind": recouverts[0][1]["kind"],
            "binding_score": round(recouverts[0][0], 3),
            "review_status": "CONFIRMED_BY_CONTEXT",
            "context_reason": (
                f"l'atome recouvre {len(recouverts)} attendus de "
                + ", ".join(f"« {c} »" for c in sorted(cibles))
                + " : "
                + " / ".join(f"« {i['official_wording'][:44]} »" for _, i in recouverts)
            ),
            "rejected_candidates": rejetes,
            "candidates": [
                {
                    "official_id": i["official_id"],
                    "official_wording": i["official_wording"],
                    "kind": i["kind"],
                    "score": round(sc, 3),
                }
                for sc, i in dedans[:3]
            ],
        }

    meilleur, item = dedans[0]
    suivant = dedans[1][0] if len(dedans) > 1 else 0.0

    # Quasi-egalite entre un « Contenu » et la « Capacite attendue » qui le met
    # en oeuvre : le referentiel interne est un referentiel de CAPACITES, et
    # c'est donc la capacite qui est son parent. Sans cette regle, « Utiliser
    # un vecteur normal a une droite pour determiner son equation » restait
    # indecidable entre l'enonce du vecteur normal et la capacite de
    # determiner l'equation -- alors que seul le second est un savoir-faire.
    if (
        len(dedans) > 1
        and meilleur - suivant < MARGE_CONTEXTE
        and meilleur >= SEUIL_CONTEXTE
    ):
        agissants = [
            (sc, i) for sc, i in dedans
            if abs(sc - meilleur) < MARGE_CONTEXTE
            and i["official_normativity"] in NORMATIVITES_DE_SAVOIR_FAIRE
        ]
        if len(agissants) == 1:
            sc, item = agissants[0]
            return {
                "binding_method": "CONTEXT",
                "official_id": item["official_id"],
                "official_ids": [item["official_id"]],
                "official_wording": item["official_wording"],
                "official_kind": item["kind"],
                "binding_score": round(sc, 3),
                "review_status": "CONFIRMED_BY_CONTEXT",
                "context_reason": (
                    "a egalite de recouvrement, le seul attendu de la partie "
                    f"qui soit un savoir-faire est « {item['official_wording'][:66]} » "
                    f"({item['official_normativity']})"
                ),
                "rejected_candidates": rejetes,
                "candidates": [
                    {
                        "official_id": i["official_id"],
                        "official_wording": i["official_wording"],
                        "kind": i["kind"],
                        "score": round(s2, 3),
                    }
                    for s2, i in dedans[:3]
                ],
            }

    if meilleur >= SEUIL_CONTEXTE and meilleur - suivant >= MARGE_CONTEXTE:
        return {
            "binding_method": "CONTEXT",
            "official_id": item["official_id"],
            "official_ids": [item["official_id"]],
            "official_wording": item["official_wording"],
            "official_kind": item["kind"],
            "binding_score": round(meilleur, 3),
            "review_status": "CONFIRMED_BY_CONTEXT",
            "context_reason": (
                "parties traitees par ce theme : "
                + ", ".join(f"« {c} »" for c in sorted(cibles))
                + f" ; « {item['official_wording'][:70]} » l'y emporte "
                f"({meilleur:.2f} contre {suivant:.2f})"
            ),
            "rejected_candidates": rejetes,
            "candidates": [
                {
                    "official_id": i["official_id"],
                    "official_wording": i["official_wording"],
                    "kind": i["kind"],
                    "score": round(sc, 3),
                }
                for sc, i in dedans[:3]
            ],
        }
    return {
        "review_status": "AMBIGUOUS_REQUIRES_HUMAN",
        "context_reason": (
            "dans "
            + ", ".join(f"« {c} »" for c in sorted(cibles))
            + f", aucun attendu ne se detache ({meilleur:.2f} contre {suivant:.2f})"
        ),
        "rejected_candidates": rejetes,
        "candidates": [
            {
                "official_id": i["official_id"],
                "official_wording": i["official_wording"],
                "kind": i["kind"],
                "score": round(sc, 3),
            }
            for sc, i in dedans[:3]
        ],
    }



#: Statuts du residu. Aucun atome ne doit rester « sans parent » tout court :
#: cette mention ne dit pas si l'atome est une subdivision pedagogique d'un
#: attendu, un enrichissement assume, un reste de programme perime, ou une
#: invention interne -- et ces quatre situations n'appellent pas la meme suite.
def classer_residu(
    lien: dict[str, Any],
    officiels: dict[str, list[dict[str, Any]]],
    hors_edition: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    propre = jetons(lien["libelle_interne"])
    items = officiels.get(lien["manual"] or "", [])
    candidats = lien.get("candidates") or []

    # Un atome mieux servi par un programme qui ne regit plus l'edition est un
    # reste de l'ancien programme, pas un attendu du programme applicable.
    meilleur_hors = max(
        (
            proximite(propre, jetons(i["official_wording"]))
            for i in hors_edition.get(lien["manual"] or "", [])
        ),
        default=0.0,
    )
    meilleur_dans = candidats[0]["score"] if candidats else 0.0
    if meilleur_hors >= SEUIL_CONTEXTE and meilleur_hors > meilleur_dans + MARGE_CONTEXTE:
        return {
            "residual_classification": "WRONG_YEAR",
            "residual_evidence": (
                f"recouvre mieux un attendu d'un programme non applicable "
                f"({meilleur_hors:.2f}) que le programme en vigueur "
                f"({meilleur_dans:.2f})"
            ),
        }

    if candidats and not any(
        i["mandatory"]
        for i in items
        if i["official_id"] in {c["official_id"] for c in candidats}
    ):
        return {
            "residual_classification": "ENRICHMENT",
            "residual_evidence": (
                "ses seuls rapprochements possibles portent sur des attendus "
                "que le programme ne rend pas obligatoires"
            ),
        }

    if candidats and len(candidats) > 1 and abs(
        candidats[0]["score"] - candidats[1]["score"]
    ) < MARGE_CONTEXTE:
        return {
            "residual_classification": "PEDAGOGICAL_SUBDIVISION",
            "residual_evidence": (
                "l'atome recoupe a egalite plusieurs attendus de la partie : "
                "il en decoupe une facette sans en epouser un seul"
            ),
        }

    if not candidats:
        return {
            "residual_classification": "OBSOLETE_INTERNAL_ATOM",
            "residual_evidence": (
                "aucun attendu du programme applicable ne lui repond, "
                "meme partiellement"
            ),
        }

    return {
        "residual_classification": "OFFICIAL_CHILD",
        "residual_evidence": (
            "releve d'un attendu de la partie traitee, sans qu'un candidat se "
            "detache assez pour trancher mecaniquement"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    officiels, autorites = charger_officiels()
    atomes = charger_atomes()
    liens: list[dict[str, Any]] = []
    for atome in atomes:
        items = officiels.get(atome["manual"] or "", [])
        lien = lier(atome, items) if items else {
            "binding_method": "NONE",
            "official_id": None,
            "official_wording": None,
            "official_kind": None,
            "binding_score": 0.0,
            "review_status": "MANUAL_HAS_NO_OFFICIAL_INVENTORY",
            "candidates": [],
        }
        liens.append({**atome, **lien})

    # Seconde passe : les rapprochements restes en suspens sont relus dans le
    # contexte de la partie officielle que leur chapitre traite.
    portees = portees_de_theme(liens, officiels)
    for lien in liens:
        if lien["binding_method"] in ("ANCHOR", "VERBATIM"):
            lien["theme_scope"] = None
            lien["rejected_candidates"] = []
            continue
        cle = (lien["manual"], lien["theme"])
        portee_theme = portees.get(cle)
        lien["theme_scope"] = portee_theme
        lien.update(relire_par_contexte(lien, officiels.get(lien["manual"] or "", []), portee_theme))

    hors_edition: dict[str, list[dict[str, Any]]] = defaultdict(list)
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    for entree in index["documents"]:
        if entree["applies_to_edition"]:
            continue
        charge = json.loads((ROOT / entree["inventory_path"]).read_text(encoding="utf-8"))
        hors_edition[entree["manual"]].extend(charge["items"])
    for lien in liens:
        if lien["review_status"] == "AMBIGUOUS_REQUIRES_HUMAN":
            lien.update(classer_residu(lien, officiels, hors_edition))

    ETABLIS = ("ANCHOR", "VERBATIM", "CONTEXT")
    confirmes = [lien for lien in liens if lien["binding_method"] in ETABLIS]
    # Un atome peut avoir plusieurs parents officiels : il arrive qu'il
    # fusionne des attendus que le BO enonce separement. Ne compter que le
    # premier laisserait les autres orphelins.
    revendiques = {
        oid for lien in confirmes for oid in (lien.get("official_ids") or [lien["official_id"]])
    }

    # Un item officiel revendique par des atomes de plusieurs chapitres n'est
    # pas une anomalie en soi -- une capacite peut se travailler a plusieurs
    # endroits -- mais tant que rien ne le justifie, il ne doit pas etre compte
    # deux fois : ce serait gonfler la couverture avec le meme attendu.
    par_item: dict[str, set[str]] = defaultdict(set)
    for lien in confirmes:
        for oid in lien.get("official_ids") or [lien["official_id"]]:
            par_item[oid].add(f"{lien['manual']}/{lien['theme']}")
    multiples = {k: sorted(v) for k, v in par_item.items() if len(v) > 1}

    # Un referentiel ne doit invoquer que l'autorite applicable a son manuel.
    mauvaise_annee = []
    espace_viole = []
    for lien in liens:
        cite = set(re.findall(r"MENE\d{7}[A-Z]", lien["bo_reference"] or ""))
        if lien["declared_authority"]:
            cite.add(lien["declared_authority"])
        attendue = autorites.get(lien["manual"] or "")
        for nor in cite:
            if nor == "MENE2516123N":
                espace_viole.append({"atom_id": lien["atom_id"], "cited": nor})
            elif attendue and nor != attendue:
                mauvaise_annee.append(
                    {"atom_id": lien["atom_id"], "cited": nor, "expected": attendue}
                )

    # Un referentiel qui cite un bulletin sans nommer l'arrete ne designe pas
    # son autorite : le meme bulletin porte plusieurs programmes, et rien n'y
    # distingue celui dont le referentiel se reclame. C'est une preuve sans
    # source, meme quand la reference se trouve etre la bonne.
    autorite_implicite = sorted(
        {
            lien["referential_path"]
            for lien in liens
            if autorites.get(lien["manual"] or "")
            and autorites[lien["manual"]] not in (lien["bo_reference"] or "")
            and lien["declared_authority"] != autorites[lien["manual"]]
        }
    )

    resume_par_manuel: dict[str, dict[str, Any]] = {}
    for manuel, items in sorted(officiels.items()):
        obligatoires = [i for i in items if i["mandatory"]]
        couverts = [i for i in obligatoires if i["official_id"] in revendiques]
        atomes_manuel = [lien for lien in liens if lien["manual"] == manuel]
        # Le denominateur se ventile par nature, faute de quoi il ne veut rien
        # dire. Le referentiel interne est un referentiel de CAPACITES : il ne
        # peut pas, et n'a pas a, porter les « Contenus » du programme, dont la
        # trace se cherche dans le cours et non dans une capacite. Les compter
        # ensemble ferait passer pour un defaut de couverture ce qui n'est
        # qu'une difference de nature entre les deux objets.
        par_nature: dict[str, dict[str, int]] = {}
        for item in obligatoires:
            stat = par_nature.setdefault(
                item["kind"], {"mandatory": 0, "bound_confirmed": 0}
            )
            stat["mandatory"] += 1
            if item["official_id"] in revendiques:
                stat["bound_confirmed"] += 1
        resume_par_manuel[manuel] = {
            "authority_ref": autorites[manuel],
            "official_items": len(items),
            "official_mandatory": len(obligatoires),
            "official_mandatory_bound_confirmed": len(couverts),
            "OFFICIAL_REQUIRED_UNMAPPED": len(obligatoires) - len(couverts),
            "internal_atoms": len(atomes_manuel),
            "internal_atoms_confirmed": sum(
                1 for a in atomes_manuel
                if a["binding_method"] in ETABLIS
            ),
            "INTERNAL_ATOM_WITHOUT_OFFICIAL_PARENT": sum(
                1 for a in atomes_manuel
                if a["binding_method"] not in ETABLIS
            ),
            "by_official_kind": dict(sorted(par_nature.items())),
        }

    charge = {
        "artifact_type": "official_programme_binding",
        "schema_version": 1,
        "generated_by": "scripts/build_official_programme_binding.py",
        "edition": json.loads(INDEX.read_text(encoding="utf-8"))["edition"],
        "binding_methods": {
            "ANCHOR": "coordonnees citees dans le texte officiel ; exact et rejouable",
            "VERBATIM": "libelle repris mot pour mot du texte officiel",
            "PROPOSED": "rapprochement mesure, soumis a arbitrage humain ; ne vaut pas couverture",
            "NONE": "aucun parent officiel trouve",
        },
        "summary": {
            "internal_atoms": len(liens),
            "bound_confirmed": len(confirmes),
            "bound_by_context": sum(
                1 for lien in liens if lien["binding_method"] == "CONTEXT"
            ),
            "ambiguous_requires_human": sum(
                1 for lien in liens
                if lien["review_status"] == "AMBIGUOUS_REQUIRES_HUMAN"
            ),
            "residual_classification_counts": dict(
                sorted(
                    Counter(
                        lien["residual_classification"]
                        for lien in liens
                        if "residual_classification" in lien
                    ).items()
                )
            ),
            "rejected_wrong_match_candidates": sum(
                len(lien.get("rejected_candidates", [])) for lien in liens
            ),
            "unbound": sum(
                1 for lien in liens
                if lien["binding_method"]
                in ("NONE", "PROPOSED", "ANCHOR_UNRESOLVABLE",
                    "MANUAL_HAS_NO_OFFICIAL_INVENTORY")
            ),
            "INTERNAL_ATOM_WITHOUT_OFFICIAL_PARENT": len(liens) - len(confirmes),
            "OFFICIAL_REQUIRED_UNMAPPED": sum(
                r["OFFICIAL_REQUIRED_UNMAPPED"] for r in resume_par_manuel.values()
            ),
            "UNJUSTIFIED_MULTIPLE_ASSIGNMENT": len(multiples),
            "WRONG_YEAR_USED_AS_AUTHORITY": len(mauvaise_annee),
            "AUTHORITY_NAMESPACE_VIOLATION": len(espace_viole),
            "REFERENTIAL_AUTHORITY_NOT_EXPLICIT": len(autorite_implicite),
            "binding_method_counts": dict(
                sorted(Counter(lien["binding_method"] for lien in liens).items())
            ),
        },
        "per_manual": resume_par_manuel,
        "multiple_assignment": multiples,
        "wrong_year_citations": mauvaise_annee,
        "authority_namespace_violations": espace_viole,
        "referentials_not_naming_their_authority": autorite_implicite,
        "bindings": liens,
    }
    texte = json.dumps(charge, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != texte:
            print(f"DIVERGENT : {OUT.relative_to(ROOT)}")
            return 1
        print("Rattachement conforme au generateur.")
        return 0
    OUT.write_text(texte, encoding="utf-8")

    s = charge["summary"]
    print(f"atomes internes                          {s['internal_atoms']:5d}")
    print(f"  rattaches de facon etablie             {s['bound_confirmed']:5d}")
    print(f"  dont etablis par contexte              {s['bound_by_context']:5d}")
    print(f"  ambigus, arbitrage humain requis       {s['ambiguous_requires_human']:5d}")
    print(f"  candidats ecartes (mauvais rapprochement) {s['rejected_wrong_match_candidates']:4d}")
    print()
    for manuel, r in resume_par_manuel.items():
        print(f"{manuel:>10} {r['authority_ref']}  obligatoires {r['official_mandatory']:4d}"
              f"  rattaches {r['official_mandatory_bound_confirmed']:4d}")
        for nature, stat in r["by_official_kind"].items():
            print(f"             {nature:<22s} {stat['bound_confirmed']:3d} / "
                  f"{stat['mandatory']:3d}")
    print()
    for compteur in (
        "INTERNAL_ATOM_WITHOUT_OFFICIAL_PARENT",
        "OFFICIAL_REQUIRED_UNMAPPED",
        "UNJUSTIFIED_MULTIPLE_ASSIGNMENT",
        "WRONG_YEAR_USED_AS_AUTHORITY",
        "AUTHORITY_NAMESPACE_VIOLATION",
        "REFERENTIAL_AUTHORITY_NOT_EXPLICIT",
    ):
        print(f"{compteur} = {s[compteur]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
