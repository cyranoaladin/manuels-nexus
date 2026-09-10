#!/usr/bin/env python3
"""Chaque exigence officielle est-elle reellement enseignee dans le manuel ?

C'est une question differente de celle du rattachement. Le rattachement demande
si les capacites internes du projet sont correctement raccrochees au BO ; il se
juge sur des referentiels. Celle-ci demande si l'eleve trouve, dans le manuel,
de quoi apprendre ce que le programme exige ; elle se juge sur les OBJETS --
un paragraphe de cours, une demonstration redigee, un exercice, une evaluation.

Un attendu officiel n'a pas besoin d'un atome interne pour etre couvert. Les
referentiels du projet encodent surtout des capacites ; une connaissance peut
etre parfaitement traitee dans un fichier de cours sans avoir jamais recu de
code C*. Exiger un atome par attendu ferait apparaitre comme manquant ce qui
est enseigne, et pousserait a fabriquer des centaines d'atomes vides pour
faire tomber un compteur.

La preuve emprunte donc deux chemins, tous deux publies :

  DECLARED_CAPACITY  l'objet declare la capacite, elle-meme rattachee au BO ;
  CONTENT_MATCH      aucun atome ne porte l'attendu, mais un objet d'un
                     chapitre qui traite cette partie du programme en contient
                     les termes. Le rapprochement est publie avec les termes
                     trouves et ceux qui manquent.

Le verdict depend de la NATURE de l'attendu, pas d'un pourcentage global. Une
demonstration exigible n'est pas couverte par un exercice qui utilise le
resultat : il faut que la preuve soit ecrite. Un automatisme n'est pas couvert
par une seule lecon : le programme demande qu'il soit entretenu sur l'annee.
Un exemple d'algorithme demande un travail algorithmique, pas la copie de cet
exemple-la.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_objects import (
    Objet,
    charger_contrats,
    charger_objets,
    charger_transversaux,
)
from programme_normativity import (
    EXPECTED_CAPACITY,
    PRESCRIBED_ALGORITHMIC_WORK,
    REQUIRED_AUTOMATISM,
    REQUIRED_CONTENT,
    REQUIRED_DEMONSTRATION,
    TRANSVERSAL_REQUIREMENT,
)

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "audit" / "OFFICIAL_PROGRAMME_INVENTORY.json"
BINDING = ROOT / "audit" / "OFFICIAL_PROGRAMME_BINDING.json"
OUT = ROOT / "audit" / "OFFICIAL_TO_MANUAL_COVERAGE.json"

#: Ce que le BO exige d'un automatisme : qu'il ne fasse pas « l'objet d'un
#: chapitre d'enseignement specifique » et soit « entretenu et consolide au
#: cours de l'annee ». Le trouver dans un seul chapitre contredit donc le
#: texte ; le trouver dans deux ne le contredit plus.
#:
#: Exiger davantage -- trois chapitres, de l'entrainement, de l'evaluation --
#: releve de la qualite que la collection se donne, pas de ce que le ministere
#: ecrit. Ce seuil-la porte son nom et se mesure ailleurs :
#: NEXUS_DISTRIBUTED_AUTOMATISM_STANDARD, dans l'audit des automatismes.
CHAPITRES_MINIMAUX_POUR_UN_AUTOMATISME = 2
#: Rapprochement par contenu : part des mots distinctifs qu'un objet doit
#: contenir, et nombre minimal exige. Le plafond compte autant que la part :
#: sans lui, un attendu enonce en une longue phrase -- « Lire un graphique, un
#: histogramme, un diagramme en barres ou circulaire, un diagramme en boite ou
#: toute autre representation... » -- devenait introuvable parce qu'aucun
#: objet ne reprend seize mots sur seize.
PART_DE_TERMES_REQUISE = 0.5
TERMES_MINIMAUX = 2
TERMES_SUFFISANTS = 4
#: Mots trop repandus dans un manuel de mathematiques pour distinguer quoi que
#: ce soit. Les garder ferait « trouver » n'importe quel attendu partout.
BANALS = {
    "fonction", "fonctions", "calcul", "calculer", "nombre", "nombres",
    "utiliser", "determiner", "exemple", "exemples", "probleme", "problemes",
    "point", "points", "valeur", "valeurs", "forme", "cas", "deux", "donnee",
    "donnees", "resoudre", "etudier", "connaitre", "partir", "ensemble",
}



#: Verdicts rendus a la LECTURE, pour les attendus que le rapprochement
#: automatique ne pouvait pas trancher. Trois situations, et il importe de ne
#: pas les confondre :
#:
#:   FALSE_MISSING_TOOLING   le manuel traite l'attendu ; c'est l'outil qui ne
#:                           le voyait pas.
#:   MISSING_FROM_ASSEMBLY   le contenu existe mais n'entre pas dans le manuel
#:                           assemble.
#:   TRUE_CONTENT_GAP        le manuel assemble ne traite pas l'attendu.
#:
#: Chaque entree cite les objets qui la fondent : un verdict sans objet nomme
#: ne serait qu'une opinion.
REVUES_CONTRADICTOIRES: tuple[dict[str, Any], ...] = (
    {
        "manual": "1SPE",
        "wording_prefix": "Calcul de 1 + 2 +",
        "verdict": "FALSE_MISSING_TOOLING",
        "status": "COMPLETE",
        "evidence_objects": ("1SPE-SUITES-CR-013",),
        "cause": (
            "le libelle officiel se reduit a des symboles mathematiques : "
            "aucun mot distinctif, donc aucune recherche possible"
        ),
        "reading": (
            "Le cours sur les sommes redige la demonstration par la methode de "
            "Gauss -- somme ecrite a l'envers, addition membre a membre, "
            "2S = n(n+1) -- dans un bloc titre « Demonstrations exigibles »."
        ),
    },
    {
        "manual": "1SPE",
        "wording_prefix": "Calcul de 1 + 𝑞",
        "verdict": "FALSE_MISSING_TOOLING",
        "status": "COMPLETE",
        "evidence_objects": ("1SPE-SUITES-CR-013",),
        "cause": "meme cause : un libelle sans mot distinctif",
        "reading": (
            "Le meme cours redige la demonstration de la somme geometrique par "
            "multiplication par q et telescopage, jusqu'a "
            "S = (1 - q^{n+1}) / (1 - q)."
        ),
    },
    {
        "manual": "1SPE",
        "wording_prefix": "Utiliser un repère pour étudier une configuration",
        "verdict": "FALSE_MISSING_TOOLING",
        "status": "COMPLETE",
        "evidence_objects": ("1SPE-GEOREP-CR-014", "1SPE-GEOREP-ME-005"),
        "cause": (
            "le mot « configuration » ne figure dans aucun objet, alors que "
            "c'est le seul terme distinctif du libelle avec « repere »"
        ),
        "reading": (
            "Le chapitre de geometrie reperee comporte un cours entier "
            "« Problemes dans un repere » et la fiche methode correspondante, "
            "tous deux rattaches a la capacite C5 du contrat : « resoudre des "
            "problemes geometriques dans un repere orthonorme »."
        ),
    },
    {
        "manual": "1SPE",
        "wording_prefix": "Calcul de cos , sin , cos , sin",
        "verdict": "TRUE_CONTENT_GAP",
        "status": "COMPLETE",
        "evidence_objects": ("1SPE-TRIGO-CR-011",),
        "cause": (
            "le libelle officiel n'a pas survecu a l'extraction du PDF -- il "
            "s'y reduit a « Calcul de cos , sin , cos , sin . 4 4 3 3 » -- et "
            "ne portait donc aucun mot cherchable"
        ),
        "reading": (
            "Le manuel donnait les valeurs remarquables en tableau et indiquait "
            "en une phrase leur origine geometrique, sans les calculer : ce "
            "n'etait pas la demonstration que le programme exige. Elle a ete "
            "redigee -- pi/4 par le complementaire et l'identite fondamentale, "
            "pi/3 par le triangle equilateral, pi/6 par deduction -- et "
            "verifiee exactement en sympy."
        ),
    },
    {
        "manual": "1SPE",
        "wording_prefix": "Équation de la tangente en un point",
        "verdict": "FALSE_PARTIAL_TOOLING",
        "status": "COMPLETE",
        "evidence_objects": ("1SPE-DERIVATION-LOCAL-CR-013",),
        "cause": (
            "la demonstration est redigee dans le chapitre voisin, celui de la "
            "derivation locale, que la recherche n'a pas atteint"
        ),
        "reading": (
            "Le cours sur l'equation de la tangente redige la demonstration "
            "complete : caracterisation d'une droite de pente m passant par A, "
            "identification de m a f'(a), et reciproque."
        ),
    },
    {
        "manual": "1SPE",
        "wording_prefix": "La fonction racine carrée n’est pas dérivable",
        "verdict": "FALSE_PARTIAL_TOOLING",
        "status": "COMPLETE",
        "evidence_objects": ("1SPE-DERGLOBAL-COURS-C1",),
        "cause": (
            "la demonstration est redigee dans un bloc de contre-exemple, que "
            "le detecteur de preuve ne reconnaissait pas"
        ),
        "reading": (
            "Le cours calcule le taux de variation entre 0 et h, montre qu'il "
            "vaut 1/racine(h) et depasse toute borne quand h tend vers 0 : il "
            "n'existe donc pas de nombre derive en 0. La demi-tangente "
            "verticale est mentionnee."
        ),
    },
    {
        "manual": "TCOMPL",
        "wording_prefix": "Équation différentielle y’ = a y + b",
        "verdict": "FALSE_PARTIAL_TOOLING",
        "status": "COMPLETE",
        "evidence_objects": ("TCOMPL-ME-CR-012",),
        "cause": "le cours est dans le theme des modeles d'evolution",
        "reading": (
            "`12_C3_equation_differentielle.tex` traite l'equation y' = ay + b "
            "et sa resolution."
        ),
    },
    {
        "manual": "TCOMPL",
        "wording_prefix": "Étude de fonction.",
        "verdict": "FALSE_PARTIAL_TOOLING",
        "status": "COMPLETE",
        "evidence_objects": ("TCOMPL-MF-CR-010",),
        "cause": (
            "contenu associe a un theme d'etude, enseigne dans le theme voisin "
            "des modeles definis par une fonction"
        ),
        "reading": "`10_C1_etude_fonction.tex` est le cours d'etude de fonction.",
    },
    {
        "manual": "TCOMPL",
        "wording_prefix": "Fonctions de référence.",
        "verdict": "FALSE_PARTIAL_TOOLING",
        "status": "COMPLETE",
        "evidence_objects": ("TCOMPL-MF-CR-010",),
        "cause": "meme cause : contenu associe enseigne dans un autre theme",
        "reading": (
            "Le cours d'etude de fonction traite les fonctions de reference et "
            "leurs variations."
        ),
    },
    {
        "manual": "TCOMPL",
        "wording_prefix": "Représentations graphiques.",
        "verdict": "FALSE_PARTIAL_TOOLING",
        "status": "COMPLETE",
        "evidence_objects": ("TCOMPL-MF-CR-010",),
        "cause": "meme cause",
        "reading": (
            "Le cours d'etude de fonction construit et exploite les "
            "representations graphiques."
        ),
    },
    {
        "manual": "TCOMPL",
        "wording_prefix": "Minimum d’une fonction trinôme.",
        "verdict": "FALSE_PARTIAL_TOOLING",
        "status": "COMPLETE",
        "evidence_objects": ("TCOMPL-MF-CR-010",),
        "cause": "meme cause",
        "reading": (
            "Le cours d'etude de fonction traite la recherche d'un minimum, "
            "trinome compris."
        ),
    },
    {
        "manual": "TCOMPL",
        "wording_prefix": "Présentation de l’intégrale des fonctions continues",
        "verdict": "FALSE_PARTIAL_TOOLING",
        "status": "COMPLETE",
        "evidence_objects": ("TCOMPL-AIR-CR-012",),
        "cause": "le cours de calcul integral n'a pas ete atteint par la recherche",
        "reading": (
            "`12_C3_calcul_integral.tex` presente l'integrale, y compris pour "
            "des fonctions de signe quelconque."
        ),
    },
    {
        "manual": "TCOMPL",
        "wording_prefix": "Interpréter une intégrale, une valeur moyenne",
        "verdict": "FALSE_PARTIAL_TOOLING",
        "status": "COMPLETE",
        "evidence_objects": ("TCOMPL-AIR-CR-012",),
        "cause": "meme cause",
        "reading": (
            "Le meme cours traite la valeur moyenne et son interpretation."
        ),
    },
    {
        "manual": "TEXPERTES",
        "wording_prefix": "Forme trigonométrique.",
        "verdict": "FALSE_PARTIAL_TOOLING",
        "status": "COMPLETE",
        "evidence_objects": ("TEXP-CTP-CR-010",),
        "cause": (
            "le cours s'intitule « forme exponentielle » et traite la forme "
            "trigonometrique dont elle derive"
        ),
        "reading": (
            "`10_C1_forme_exponentielle.tex` introduit module et argument, la "
            "forme trigonometrique, puis la notation exponentielle."
        ),
    },
    {
        "manual": "TSPE",
        "wording_prefix": "Primitives des fonctions de référence",
        "verdict": "FALSE_PARTIAL_TOOLING",
        "status": "COMPLETE",
        "evidence_objects": ("TSPE-PRIMEQ-CR-011",),
        "cause": "le cours dedie n'a pas ete atteint par la recherche",
        "reading": (
            "`11_C1_calcul_primitives.tex` donne les primitives des fonctions "
            "de reference et leur calcul."
        ),
    },
    {
        "manual": "TSPE",
        "wording_prefix": "Appliquer l’inégalité de Bienaymé-Tchebychev",
        "verdict": "FALSE_PARTIAL_TOOLING",
        "status": "COMPLETE",
        "evidence_objects": ("TSPE-PROBA-CR-016",),
        "cause": "le cours dedie n'etait pas rattache a cet attendu",
        "reading": (
            "`16_CONCLGN_bienayme_tchebychev.tex` enonce et applique "
            "l'inegalite."
        ),
    },
    {
        "manual": "1NSI",
        "wording_prefix": "Interaction avec l’utilisateur dans une page Web",
        "verdict": "FALSE_PARTIAL_TOOLING",
        "status": "COMPLETE",
        "evidence_objects": ("1NSI-WEB-COURS-C3",),
        "cause": (
            "le cours du chapitre Web et IHM porte les capacites de la ligne "
            "officielle sans que son intitule reprenne les termes du contenu"
        ),
        "reading": (
            "`1NSI-WEB-COURS-C3` traite l'interaction avec l'utilisateur : "
            "evenements, formulaires, requetes."
        ),
    },
    {
        "manual": "1SPE",
        "wording_prefix": "Transformation de l’expression",
        "verdict": "FALSE_PARTIAL_TOOLING",
        "status": "COMPLETE",
        "evidence_objects": ("1SPE-PRODSCAL-COURS-C4",),
        "cause": (
            "le libelle officiel est illisible apres extraction du PDF -- les "
            "fleches vectorielles y ont disloque les noms de points"
        ),
        "reading": (
            "Le cours d'applications du produit scalaire etablit la "
            "transformation de MA.MB en MI^2 - AB^2/4 et s'en sert pour "
            "caracteriser le cercle de diametre [AB]."
        ),
    },
    {
        "manual": "TSPE",
        "wording_prefix": "Développement de u",
        "verdict": "TRUE_CONTENT_GAP",
        "status": "COMPLETE",
        "evidence_objects": ("TSPE-GEOESPACE-CR-012",),
        "cause": (
            "le cours de produit scalaire dans l'espace s'arretait a la "
            "longueur d'un vecteur : ni le developpement de la norme d'une "
            "somme, ni les formules de polarisation n'y figuraient"
        ),
        "reading": (
            "Le developpement de ||u+v||^2 et ||u-v||^2, leur demonstration par "
            "bilinearite et symetrie, les deux formules de polarisation avec "
            "leur demonstration et un exemple numerique ont ete rediges."
        ),
    },
    {
        "manual": "TEXPERTES",
        "wording_prefix": "Effectuer des calculs sur des nombres complexes",
        "verdict": "FALSE_MISSING_TOOLING",
        "status": "COMPLETE",
        "evidence_objects": (
            "TEXP-CTP-CR-010",
            "TEXP-CTP-ME-001",
            "TEXP-CTP-ME-002",
        ),
        "cause": (
            "les termes du libelle -- « effectuer », « calculs », "
            "« choisissant », « adaptee » -- sont trop generiques pour "
            "designer quoi que ce soit"
        ),
        "reading": (
            "Le cours sur la forme exponentielle et les deux fiches methode "
            "enseignent precisement le choix de la forme : forme exponentielle "
            "pour une puissance, formules d'Euler pour une linearisation, "
            "Moivre pour cos(nt) et sin(nt)."
        ),
    },
)


def _sans_accents(texte: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", texte) if not unicodedata.combining(c)
    )


def termes_distinctifs(libelle: str) -> set[str]:
    mots = re.findall(r"[a-z0-9]+", _sans_accents(libelle).lower())
    return {m for m in mots if len(m) >= 5 and m not in BANALS}


def _slug_preambule(intitule: str) -> str:
    """Forme d'identifiant utilisee par les objets pour citer le preambule."""
    return re.sub(
        r"[^A-Z0-9]+", "-", _sans_accents(intitule).upper()
    ).strip("-")


#: Suffixes francais retires pour ramener un terme a son radical, du plus long
#: au plus court. Tronquer a longueur fixe ne suffisait pas : « derivation » et
#: « derivee » ne partagent que cinq lettres, et le programme ecrit l'un la ou
#: le cours ecrit l'autre.
SUFFIXES = (
    "ations", "ation", "ements", "ement", "ismes", "isme", "ives", "ive",
    "ique", "iques", "elles", "elle", "ites", "ite", "ees", "ee", "aux",
    "als", "al", "es", "s",
)
#: Longueur minimale d'un radical : en deca, le mot ne distingue plus rien.
RADICAL_MINIMAL = 5


def racine(terme: str) -> str:
    """Radical grossier, pour ne pas dependre des flexions ni des derivations.

    Le programme ecrit « Expressions booleennes » la ou le cours ecrit « une
    expression booleenne », et « Continuite et derivation » la ou le cours
    parle de fonction « derivee ». Chercher la forme exacte declarait absent un
    contenu present ; tronquer a longueur fixe manquait encore le second cas.
    """
    for suffixe in SUFFIXES:
        if terme.endswith(suffixe) and len(terme) - len(suffixe) >= RADICAL_MINIMAL:
            return terme[: -len(suffixe)]
    return terme


def charger_lignes_officielles() -> dict[str, list[str]]:
    """Pour chaque attendu, les autres attendus de SA ligne du tableau.

    Le BO de NSI place sur une meme ligne un contenu, les capacites qui le
    mettent en oeuvre et les commentaires qui l'eclairent. C'est une unite
    reglementaire, pas trois enonces voisins.
    """
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    voisins: dict[str, list[str]] = {}
    for entree in index["documents"]:
        charge = json.loads((ROOT / entree["inventory_path"]).read_text(encoding="utf-8"))
        for ligne in charge.get("row_bindings", []):
            tous = (
                ligne["content_items"]
                + ligne["capacity_items"]
                + ligne["commentary_items"]
            )
            for oid in tous:
                voisins[oid] = [autre for autre in tous if autre != oid]
    return voisins


def charger_officiels() -> tuple[list[dict[str, Any]], dict[str, str]]:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    items: list[dict[str, Any]] = []
    autorites: dict[str, str] = {}
    for entree in index["documents"]:
        if not entree["applies_to_edition"]:
            continue
        autorites[entree["manual"]] = entree["authority_ref"]
        charge = json.loads((ROOT / entree["inventory_path"]).read_text(encoding="utf-8"))
        items.extend(charge["items"])
    return items, autorites


def verdict(
    normativity: str,
    roles: Counter[str],
    chapitres_de_reinvestissement: set[str],
    demonstration_redigee: bool,
    travail_algorithmique: bool,
    exemples_travailles: bool = False,
    travail_algorithmique_de_la_partie: bool = False,
    exemple_impose: bool = True,
    chapitres_d_enseignement: set[str] | None = None,
) -> tuple[str, str]:
    """Verdict et motif, selon ce que la nature de l'attendu exige reellement."""
    chapitres_d_enseignement = chapitres_d_enseignement or set()
    enseigne = roles.get("PRIMARY_TEACHING", 0) > 0
    appuye = roles.get("SUPPORTING_EVIDENCE", 0) > 0
    pratique = roles.get("REINVESTMENT", 0) > 0
    evalue = roles.get("ASSESSMENT", 0) > 0
    rien = not any(roles.values())

    if normativity == TRANSVERSAL_REQUIREMENT:
        # Le manuel ne peut pas prouver qu'un etablissement consacrera un quart
        # de l'horaire aux projets, ni que les professeurs veilleront a leur
        # ambition. Declarer ces phrases « couvertes » ou « manquantes » serait
        # deux fois faux : elles ne s'adressent pas au manuel. Ce qui se juge
        # ici est le SOUTIEN qu'il apporte.
        return (
            "INSTITUTIONAL_IMPLEMENTATION_REQUIREMENT",
            (
                "le manuel fournit de quoi conduire cette exigence"
                if (roles.get("PRIMARY_TEACHING", 0) or roles.get("SUPPORTING_EVIDENCE", 0))
                else "aucun objet du manuel n'outille cette exigence"
            ),
        )
        # Un manuel ne peut pas prouver qu'un etablissement consacrera
        # reellement un quart de l'horaire aux projets. Il peut fournir de
        # quoi les conduire ; le declarer « satisfait par le livre » serait
        # une fausse preuve.
        if rien:
            return "MISSING", "aucun objet du manuel n'outille cette exigence"
        if enseigne or appuye:
            return (
                "MANUAL_SUPPORT_PRESENT",
                "le manuel fournit de quoi conduire cette exigence ; sa mise "
                "en oeuvre effective releve de l'etablissement et n'est pas "
                "certifiable par un manuel",
            )
        return "PARTIAL", "objets presents, mais aucun support d'enseignement"

    if normativity == PRESCRIBED_ALGORITHMIC_WORK and not exemple_impose:
        # Le BO intitule cette rubrique « Exemples d'algorithme ». Ce qu'il
        # prescrit est un travail algorithmique sur la partie concernee ; il
        # ne demande pas que ce soit CET algorithme-la. Exiger l'exemple cite
        # transformerait une illustration en obligation que le texte ne porte
        # pas -- et declarerait manquant un chapitre qui fait le travail
        # autrement.
        if travail_algorithmique:
            return (
                "COMPLETE",
                "l'exemple cite par le programme est lui-meme traite",
            )
        if travail_algorithmique_de_la_partie:
            return (
                "COMPLETE",
                "le travail algorithmique prescrit est present dans la partie "
                "concernee ; le programme nomme un exemple, il ne l'impose pas",
            )
        return (
            "MISSING",
            "aucun travail algorithmique dans la partie concernee",
        )

    if rien:
        return "MISSING", "aucun objet du manuel ne porte cet attendu"

    if normativity == REQUIRED_DEMONSTRATION:
        if demonstration_redigee:
            return "COMPLETE", "la demonstration est redigee dans un objet du manuel"
        return (
            "PARTIAL",
            "des objets portent cet attendu, mais aucun ne contient de "
            "demonstration redigee : le nom d'un theoreme ne demontre rien",
        )

    if normativity == PRESCRIBED_ALGORITHMIC_WORK:
        if travail_algorithmique:
            return "COMPLETE", "un objet porte un travail algorithmique effectif"
        return (
            "PARTIAL",
            "des objets portent cet attendu, mais aucun ne comporte "
            "d'algorithme ni de programme",
        )

    if normativity == REQUIRED_AUTOMATISM:
        chapitres = chapitres_de_reinvestissement | chapitres_d_enseignement
        if len(chapitres) >= CHAPITRES_MINIMAUX_POUR_UN_AUTOMATISME:
            return (
                "COMPLETE",
                f"travaille dans {len(chapitres)} chapitres : le programme "
                "exclut qu'un automatisme fasse l'objet d'un chapitre "
                "specifique, cette condition est remplie",
            )
        return (
            "PARTIAL",
            "concentre dans un seul chapitre, ce que le programme exclut "
            "explicitement pour un automatisme",
        )

    if normativity == REQUIRED_CONTENT:
        if enseigne:
            return "COMPLETE", "traite dans un objet de cours"
        return (
            "PARTIAL",
            "aborde par des objets du manuel, mais aucun cours ne l'expose",
        )

    if normativity == EXPECTED_CAPACITY:
        if enseigne and (pratique or appuye or evalue):
            return "COMPLETE", "enseigne et mis en pratique"
        if enseigne and exemples_travailles:
            # Une capacite n'a pas besoin d'une fiche methode pour etre mise en
            # pratique : elle a besoin d'un entrainement adapte. Un exemple
            # travaille dans le corps du cours en est un -- c'est la forme que
            # prennent les pages transversales, qui montrent seize fois la
            # capacite a l'oeuvre sans aucun exercice separe.
            return "COMPLETE", "enseigne et montre a l'oeuvre sur des exemples travailles"
        if enseigne:
            return "PARTIAL", "enseigne, mais sans exercice, methode ni exemple travaille"
        if pratique or appuye or evalue:
            return "PARTIAL", "pratique ou evalue, mais jamais enseigne"
        return "PARTIAL", "objets presents, roles insuffisants"

    return "OUT_OF_SCOPE_ENRICHMENT", "attendu non obligatoire"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    items, autorites = charger_officiels()
    voisins_de_ligne = charger_lignes_officielles()
    par_official_id = {i["official_id"]: i for i in items}

    liaison = json.loads(BINDING.read_text(encoding="utf-8"))
    contrats = charger_contrats()
    objets = charger_objets(contrats) + charger_transversaux()
    par_identifiant = {o.object_id: o for o in objets}
    def revue_de(item: dict[str, Any]) -> dict[str, Any] | None:
        """Verdict declare pour cet attendu, s'il en existe un.

        Le rapprochement se fait sur le debut du libelle officiel : un
        identifiant technique changerait au moindre reformatage du texte.
        """
        for entree in REVUES_CONTRADICTOIRES:
            if entree["manual"] == item["manual"] and item[
                "official_wording"
            ].startswith(entree["wording_prefix"]):
                return entree
        return None

    # atome -> objets qui le servent
    par_atome: dict[str, list[Objet]] = defaultdict(list)
    for objet in objets:
        for atome in objet.atoms:
            par_atome[atome].append(objet)

    # Certains objets citent une capacite du preambule sous la forme
    # « BO-PREAMBULE-DEMARCHE-DE-PROJET ». Cet identifiant n'existe dans aucun
    # referentiel, mais il nomme sans ambiguite une partie du preambule que
    # l'inventaire officiel porte. Le resoudre evite de laisser sans preuve
    # une exigence que le manuel outille reellement.
    objets_par_partie_de_preambule: dict[tuple[str, str], list[Objet]] = defaultdict(
        list
    )
    for objet in objets:
        for atome in objet.atoms:
            if atome.startswith("BO-PREAMBULE-"):
                objets_par_partie_de_preambule[
                    (objet.manual, atome.removeprefix("BO-PREAMBULE-"))
                ].append(objet)

    # attendu officiel -> atomes rattaches de facon etablie
    atomes_par_item: dict[str, list[str]] = defaultdict(list)
    for lien in liaison["bindings"]:
        if lien["binding_method"] not in ("ANCHOR", "VERBATIM", "CONTEXT", "DISPOSED"):
            continue
        for oid in lien.get("official_ids") or [lien["official_id"]]:
            atomes_par_item[oid].append(lien["atom_id"])

    # partie officielle -> chapitres qui la traitent (via la portee des themes)
    chapitres_par_partie: dict[tuple[str, str], set[str]] = defaultdict(set)
    theme_de_chapitre = {c.chapter: (c.manual, c.theme) for c in contrats.values()}
    portee_de_theme: dict[tuple[str, str], list[str]] = {}
    for lien in liaison["bindings"]:
        if lien.get("theme_scope"):
            portee_de_theme[(lien["manual"], lien["theme"])] = lien["theme_scope"]["scopes"]
    for chapitre, (manuel, theme) in theme_de_chapitre.items():
        for partie in portee_de_theme.get((manuel, theme), []):
            chapitres_par_partie[(manuel, partie)].add(chapitre)

    # Une partie du programme fait-elle l'objet d'un travail algorithmique,
    # quel qu'en soit l'exemple ?
    algorithmique_par_partie: dict[tuple[str, str], bool] = {}
    objets_algorithmiques_par_partie: dict[tuple[str, str], list[Objet]] = {}
    objets_par_chapitre_tmp: dict[str, list[Objet]] = defaultdict(list)
    for objet in objets:
        objets_par_chapitre_tmp[objet.chapter].append(objet)
    for (manuel_p, partie), chapitres_p in chapitres_par_partie.items():
        trouves = [
            o
            for chap in sorted(chapitres_p)
            for o in objets_par_chapitre_tmp.get(chap, [])
            if o.shows_algorithmic_work
        ]
        algorithmique_par_partie[(manuel_p, partie)] = bool(trouves)
        objets_algorithmiques_par_partie[(manuel_p, partie)] = trouves

    objets_par_chapitre: dict[str, list[Objet]] = defaultdict(list)
    for objet in objets:
        objets_par_chapitre[objet.chapter].append(objet)
    textes: dict[str, str] = {}

    lignes: list[dict[str, Any]] = []
    for item in items:
        manuel = item["manual"]
        atomes = sorted(set(atomes_par_item.get(item["official_id"], [])))
        servants: dict[str, Objet] = {}
        for atome in atomes:
            for objet in par_atome.get(atome, []):
                servants[objet.object_id] = objet
        if item["official_section"] == "Préambule":
            cle_partie = _slug_preambule(item["official_subsection"] or "")
            for objet in objets_par_partie_de_preambule.get((manuel, cle_partie), []):
                servants[objet.object_id] = objet

        preuve = "DECLARED_CAPACITY" if servants else None
        termes_trouves: list[str] = []
        termes_absents: list[str] = []

        if not servants and voisins_de_ligne.get(item["official_id"]):
            # Preuve par la ligne officielle. Un objet qui prouve une capacite
            # soeur ne prouve PAS le contenu par heritage : il faut que son
            # corps traite reellement le sujet de la ligne. Le vocabulaire
            # examine est celui de la ligne entiere -- contenu, capacites,
            # commentaires --, parce que c'est ce que le BO y a mis ensemble.
            vocabulaire: set[str] = set()
            for autre in [item["official_id"], *voisins_de_ligne[item["official_id"]]]:
                voisin = par_official_id.get(autre)
                if voisin is not None:
                    vocabulaire |= termes_distinctifs(voisin["official_wording"])
            seuil_ligne = min(
                len(vocabulaire),
                TERMES_SUFFISANTS,
                max(TERMES_MINIMAUX, math.ceil(len(vocabulaire) * PART_DE_TERMES_REQUISE)),
            ) if vocabulaire else 0
            candidats: dict[str, Objet] = {}
            for autre in voisins_de_ligne[item["official_id"]]:
                for atome_voisin in atomes_par_item.get(autre, []):
                    for objet in par_atome.get(atome_voisin, []):
                        candidats[objet.object_id] = objet
            for objet in candidats.values():
                texte = textes.get(objet.path)
                if texte is None:
                    texte = _sans_accents(
                        (ROOT / objet.path).read_text(encoding="utf-8", errors="replace")
                    ).lower()
                    textes[objet.path] = texte
                presents = [t for t in vocabulaire if racine(t) in texte]
                if seuil_ligne and len(presents) >= seuil_ligne:
                    servants[objet.object_id] = objet
                    termes_trouves = sorted(set(termes_trouves) | set(presents))
            if servants:
                preuve = "OFFICIAL_ROW_EVIDENCE"
                termes_absents = sorted(vocabulaire - set(termes_trouves))


        # Un automatisme se mesure a sa repartition : le programme exclut
        # qu'il fasse l'objet d'un chapitre specifique. Ne regarder que les
        # objets qui le declarent mesurerait la repartition des declarations,
        # pas celle du travail reel -- une disposition qui rattache
        # l'automatisme a un chapitre le ferait aussitot paraitre « concentre »
        # alors que le manuel le retravaille ailleurs sans le declarer. La
        # recherche par contenu s'ajoute donc aux objets declarants au lieu de
        # les remplacer.
        mesure_par_repartition = item["official_normativity"] == REQUIRED_AUTOMATISM
        declares = set(servants)

        if not servants or mesure_par_repartition:
            # Aucun atome ne porte cet attendu : on cherche dans les chapitres
            # qui traitent cette partie du programme. La recherche est bornee
            # par la portee -- sans cela, un mot suffisamment courant
            # « trouverait » l'attendu dans n'importe quel chapitre.
            partie = item["official_subsection"] or item["official_section"] or ""
            termes = termes_distinctifs(item["official_wording"])
            # Quand aucun chapitre ne se rattache a cette partie, la recherche
            # s'etend a tout le manuel. C'est le cas des automatismes, que le
            # programme veut justement repartis et qui n'ont donc pas de
            # chapitre a eux : borner la recherche a une portee inexistante
            # revenait a ne rien chercher, et a declarer manquant ce qui est
            # peut-etre travaille partout.
            # Le seuil est borne par le nombre de termes disponibles : un
            # attendu qui n'en compte que deux doit pouvoir etre trouve, et
            # exiger un minimum absolu le rendait introuvable par principe.
            # Le seuil est borne par le nombre de termes disponibles : un
            # attendu qui n'en compte que deux doit pouvoir etre trouve, et un
            # minimum absolu le rendait introuvable par principe. Il est aussi
            # plafonne : un attendu enonce en seize mots ne peut pas exiger
            # seize concordances. Entre les deux, la moitie des termes -- deux
            # sur cinq laissaient passer « Demi-vie d'un echantillon de grande
            # taille d'atomes radioactifs » sur les seuls mots « echantillon »,
            # « grande » et « taille ».
            exigence = min(
                len(termes),
                TERMES_SUFFISANTS,
                max(TERMES_MINIMAUX, math.ceil(len(termes) * PART_DE_TERMES_REQUISE)),
            ) if termes else 0
            portee_connue = chapitres_par_partie.get((manuel, partie))
            tous = sorted(
                {c for c, (m, _) in theme_de_chapitre.items() if m == manuel}
                | {o.chapter for o in objets if o.manual == manuel}
            )
            # On cherche d'abord la ou l'attendu devrait etre, puis, si rien
            # n'y repond, dans tout le manuel. Une notion enoncee dans une
            # partie est souvent enseignee dans une autre -- « Limites de
            # suites » figure parmi les contenus mobilises par le theme
            # « Calculs d'aires » mais s'enseigne ailleurs --, et s'arreter a
            # la premiere recherche la declarait absente du manuel entier.
            passes = (
                [(sorted(portee_connue), "CONTENT_MATCH"), (tous, "CONTENT_MATCH_MANUAL_WIDE")]
                if portee_connue
                else [(tous, "CONTENT_MATCH_MANUAL_WIDE")]
            )
            if termes:
                for a_fouiller, etiquette in passes:
                    for chapitre in a_fouiller:
                        for objet in objets_par_chapitre.get(chapitre, []):
                            texte = textes.get(objet.path)
                            if texte is None:
                                texte = _sans_accents(
                                    (ROOT / objet.path).read_text(
                                        encoding="utf-8", errors="replace"
                                    )
                                ).lower()
                                textes[objet.path] = texte
                            presents = [t for t in termes if racine(t) in texte]
                            if len(presents) >= exigence:
                                servants[objet.object_id] = objet
                                termes_trouves = sorted(
                                    set(termes_trouves) | set(presents)
                                )
                    if set(servants) - declares:
                        # La preuve declaree reste la preuve : la recherche par
                        # contenu ne fait ici qu'elargir la mesure.
                        preuve = preuve or etiquette
                        termes_absents = sorted(termes - set(termes_trouves))
                        break
                else:
                    termes_absents = sorted(termes)

        # Quand la prescription algorithmique est satisfaite par le travail
        # de la partie plutot que par l'exemple cite, ce sont ces objets-la qui
        # en portent la preuve : sans eux, la matrice affirmerait une
        # couverture sans designer ce qui la couvre.
        if (
            not servants
            and item["official_normativity"] == "PRESCRIBED_ALGORITHMIC_WORK"
            and not item.get("exact_example_imposed", True)
        ):
            partie_item = item["official_subsection"] or item["official_section"] or ""
            appuis = objets_algorithmiques_par_partie.get((manuel, partie_item), [])
            if appuis:
                servants = {o.object_id: o for o in appuis}
                preuve = "ALGORITHMIC_WORK_IN_THE_SAME_PART"

        indecidable = (
            not servants
            and not atomes
            and not termes_distinctifs(item["official_wording"])
        )
        revue = revue_de(item)
        if revue is not None:
            # Le verdict rendu a la lecture remplace celui du rapprochement,
            # et cite les objets qui le fondent.
            for identifiant in revue["evidence_objects"]:
                cite = par_identifiant.get(identifiant)
                if cite is not None:
                    servants[cite.object_id] = cite
            preuve = "CONTRADICTORY_REVIEW"

        roles: Counter[str] = Counter(o.role for o in servants.values())
        chapitres = {o.chapter for o in servants.values()}
        reinvestissement = {
            o.chapter for o in servants.values()
            if o.role in ("REINVESTMENT", "ASSESSMENT", "SUPPORTING_EVIDENCE")
        }
        if revue is not None:
            statut, motif = revue["status"], revue["reading"]
        elif indecidable:
            # Le libelle ne porte aucun mot distinctif : « Calcul de cos , sin
            # , cos , sin . 4 4 3 3 », ou la notation mathematique n'a pas
            # survecu a l'extraction. Declarer l'attendu absent serait affirmer
            # ce qu'on n'a pas pu chercher.
            statut, motif = (
                "UNDECIDABLE_BY_CONTENT_MATCH",
                "aucun mot distinctif dans le libelle officiel : la recherche "
                "par contenu ne peut ni conclure a la presence ni conclure a "
                "l'absence",
            )
        else:
            statut, motif = verdict(
                item["official_normativity"],
                roles,
                reinvestissement,
                any(o.has_written_proof for o in servants.values()),
                any(o.shows_algorithmic_work for o in servants.values()),
                exemples_travailles=any(
                    o.has_worked_examples for o in servants.values()
                ),
                chapitres_d_enseignement={
                    o.chapter for o in servants.values()
                    if o.role == "PRIMARY_TEACHING"
                },
                travail_algorithmique_de_la_partie=algorithmique_par_partie.get(
                    (
                        manuel,
                        item["official_subsection"] or item["official_section"] or "",
                    ),
                    False,
                ),
                exemple_impose=item.get("exact_example_imposed", True),
            )
        lignes.append({
            "official_id": item["official_id"],
            "manual": manuel,
            "authority_ref": autorites.get(manuel),
            "official_section": item["official_section"],
            "official_subsection": item["official_subsection"],
            "official_heading": item["official_heading"],
            "official_wording": item["official_wording"],
            "official_normativity": item["official_normativity"],
            "mandatory": item["mandatory"],
            "internal_atoms": atomes,
            "evidence_kind": preuve,
            "matched_terms": termes_trouves,
            "missing_terms": termes_absents,
            "chapters": sorted(chapitres),
            "objects_by_role": {
                role: sorted(
                    o.object_id for o in servants.values() if o.role == role
                )
                for role in sorted(roles)
            },
            "object_count": len(servants),
            "coverage_status": statut,
            "coverage_reason": motif,
            "contradictory_review": (
                {
                    "verdict": revue["verdict"],
                    "cause": revue["cause"],
                }
                if revue is not None
                else None
            ),
        })

    obligatoires = [r for r in lignes if r["mandatory"]]
    par_manuel: dict[str, Any] = {}
    for manuel in sorted({r["manual"] for r in lignes}):
        du_manuel = [r for r in obligatoires if r["manual"] == manuel]
        par_nature: dict[str, dict[str, int]] = {}
        for ligne in du_manuel:
            stat = par_nature.setdefault(
                ligne["official_normativity"],
                {"COMPLETE": 0, "PARTIAL": 0, "MISSING": 0, "MANUAL_SUPPORT_PRESENT": 0},
            )
            stat[ligne["coverage_status"]] = stat.get(ligne["coverage_status"], 0) + 1
        par_manuel[manuel] = {
            "authority_ref": autorites[manuel],
            "mandatory_items": len(du_manuel),
            "by_normativity": dict(sorted(par_nature.items())),
        }

    # Exigence de qualite propre a la collection, distincte du programme. Le BO
    # nomme des « Exemples d'algorithme » sans les imposer : ils ne comptent
    # donc pas au denominateur des obligations. Mais une partie du programme
    # que ces exemples accompagnent doit, dans un bon manuel, offrir un travail
    # algorithmique reel -- et cela se controle a part, sous son propre nom,
    # pour qu'aucune exigence maison ne passe pour une exigence ministerielle.
    parties_avec_exemples: dict[tuple[str, str], list[str]] = defaultdict(list)
    for item in items:
        if item["local_kind"] == "ALGORITHM_EXAMPLE":
            parties_avec_exemples[
                (
                    item["manual"],
                    item["official_subsection"] or item["official_section"] or "",
                )
            ].append(item["official_id"])
    # Ce que le controle regarde, ce sont les objets que la matrice designe
    # elle-meme comme preuve des attendus de la partie -- exemples d'algorithme
    # compris. Passer par la portee des themes le rendait aveugle deux fois :
    # quatre parties n'ont recu aucune portee, faute de lien ANCHOR ou VERBATIM
    # qui y atterrisse, et le controle repondait « pas de travail
    # algorithmique » a propos de chapitres qu'il n'avait pas regardes -- les
    # probabilites conditionnelles de premiere portent pourtant une page
    # Monte-Carlo complete. Elargir a tous les chapitres cites aurait produit
    # la faute symetrique : la fonction logarithme aurait ete declaree servie
    # par un algorithme du calcul integral. Les objets cites, eux, traitent la
    # partie.
    objets_de_preuve_par_partie: dict[tuple[str, str], set[str]] = defaultdict(set)
    for ligne in lignes:
        cle_p = (
            ligne["manual"],
            ligne["official_subsection"] or ligne["official_section"] or "",
        )
        for role_p in ligne["objects_by_role"]:
            objets_de_preuve_par_partie[cle_p] |= set(ligne["objects_by_role"][role_p])

    def _exploitable(oid: str) -> bool:
        """Le travail algorithmique est-il exploitable par un eleve ?

        Montrer un programme ne suffit pas. Il faut que l'objet dise ce que
        l'algorithme prend et rend, qu'il demande quelque chose au lecteur,
        qu'il reponde a ce qu'il demande, et qu'un oracle executable engage
        le producteur sur la justesse du code. Un `print` decoratif ne fait
        pas passer un chapitre au vert.
        """
        objet = par_identifiant.get(oid)
        if objet is None or not objet.shows_algorithmic_work:
            return False
        if not (objet.algorithmic_objective and objet.algorithmic_activity):
            return False
        if objet.publishes_python and not objet.has_executable_oracle:
            return False
        # Une correction n'est exigee que si une tache est posee : une demarche
        # a suivre n'a pas de « reponse ».
        return objet.algorithmic_answers or not objet.algorithmic_task

    qualite_algorithmique = []
    for (manuel, partie), ids in sorted(parties_avec_exemples.items()):
        preuves_p = sorted(objets_de_preuve_par_partie.get((manuel, partie), ()))
        travail = [
            oid
            for oid in preuves_p
            if (par_identifiant.get(oid) is not None)
            and par_identifiant[oid].shows_algorithmic_work
        ]
        exploitable = [oid for oid in travail if _exploitable(oid)]
        qualite_algorithmique.append({
            "manual": manuel,
            "official_part": partie,
            "algorithm_examples_cited_by_the_programme": len(ids),
            "objects_examined": len(preuves_p),
            "manual_has_algorithmic_work": bool(travail),
            "algorithmic_work_evidence": travail[:5],
            "ALGORITHMIC_WORK_PEDAGOGICALLY_ACTIONABLE": bool(exploitable),
            "actionable_evidence": exploitable[:5],
            "standard": "NEXUS_ALGORITHMIC_QUALITY_STANDARD",
        })

    resume = {
        "OFFICIAL_REQUIRED_COMPLETE": sum(
            1 for r in obligatoires if r["coverage_status"] == "COMPLETE"
        ),
        "OFFICIAL_REQUIRED_PARTIAL": sum(
            1 for r in obligatoires if r["coverage_status"] == "PARTIAL"
        ),
        "OFFICIAL_REQUIRED_MISSING": sum(
            1 for r in obligatoires if r["coverage_status"] == "MISSING"
        ),
        "OFFICIAL_REQUIRED_INSTITUTIONAL": sum(
            1 for r in obligatoires
            if r["coverage_status"] == "INSTITUTIONAL_IMPLEMENTATION_REQUIREMENT"
        ),
        "OFFICIAL_REQUIRED_UNDECIDABLE_BY_CONTENT_MATCH": sum(
            1 for r in obligatoires
            if r["coverage_status"] == "UNDECIDABLE_BY_CONTENT_MATCH"
        ),
        "mandatory_items": len(obligatoires),
        "evidence_by_declared_capacity": sum(
            1 for r in obligatoires if r["evidence_kind"] == "DECLARED_CAPACITY"
        ),
        "evidence_by_content_match": sum(
            1 for r in obligatoires if r["evidence_kind"] == "CONTENT_MATCH"
        ),
        "evidence_by_content_match_manual_wide": sum(
            1 for r in obligatoires
            if r["evidence_kind"] == "CONTENT_MATCH_MANUAL_WIDE"
        ),
        "objects_indexed": len(objets),
        "statuses_cover_every_mandatory_item": True,
        "NEXUS_ALGORITHMIC_QUALITY_PARTS": len(qualite_algorithmique),
        "NEXUS_ALGORITHMIC_QUALITY_PARTS_WITHOUT_WORK": sum(
            1 for q in qualite_algorithmique if not q["manual_has_algorithmic_work"]
        ),
        "NEXUS_ALGORITHMIC_QUALITY_PARTS_WITHOUT_ACTIONABLE_WORK": sum(
            1 for q in qualite_algorithmique
            if not q["ALGORITHMIC_WORK_PEDAGOGICALLY_ACTIONABLE"]
        ),
    }
    assert (
        resume["OFFICIAL_REQUIRED_COMPLETE"]
        + resume["OFFICIAL_REQUIRED_PARTIAL"]
        + resume["OFFICIAL_REQUIRED_MISSING"]
        + resume["OFFICIAL_REQUIRED_INSTITUTIONAL"]
        + resume["OFFICIAL_REQUIRED_UNDECIDABLE_BY_CONTENT_MATCH"]
        == resume["mandatory_items"]
    ), "un attendu obligatoire sans statut echapperait au compte"

    charge = {
        "artifact_type": "official_to_manual_coverage",
        "schema_version": 1,
        "generated_by": "scripts/build_official_to_manual_coverage.py",
        "question": (
            "Chaque exigence officielle obligatoire est-elle reellement "
            "enseignee dans le manuel ?"
        ),
        "evidence_kinds": {
            "DECLARED_CAPACITY": "l'objet declare une capacite rattachee au BO",
            "CONTENT_MATCH": (
                "aucun atome ne porte l'attendu ; un objet d'un chapitre qui "
                "traite cette partie du programme en contient les termes"
            ),
            "ALGORITHMIC_WORK_IN_THE_SAME_PART": (
                "le programme nomme un exemple d'algorithme sans l'imposer ; "
                "la partie concernee comporte un travail algorithmique, porte "
                "par les objets listes"
            ),
            "OFFICIAL_ROW_EVIDENCE": (
                "un objet qui prouve une capacite de la MEME LIGNE du tableau "
                "officiel traite materiellement le sujet de cette ligne. Le BO "
                "y place ensemble un contenu et les capacites qui le mettent en "
                "oeuvre : les traiter separement fait declarer absent un "
                "contenu que le cours d'a cote enseigne. Ce n'est pas un "
                "heritage : le corps de l'objet doit porter le vocabulaire de "
                "la ligne."
            ),
            "CONTRADICTORY_REVIEW": (
                "verdict rendu a la lecture de l'attendu officiel et des objets "
                "du manuel, la ou le rapprochement automatique ne pouvait pas "
                "conclure. Les objets qui le fondent sont nommes."
            ),
            "CONTENT_MATCH_MANUAL_WIDE": (
                "aucun chapitre ne se rattache a cette partie du programme : "
                "la recherche a porte sur tout le manuel. C'est le cas des "
                "automatismes, que le programme veut repartis et qui n'ont "
                "donc pas de chapitre a eux"
            ),
        },
        "summary": resume,
        "per_manual": par_manuel,
        "nexus_algorithmic_quality_standard": {
            "nature": (
                "exigence de qualite de la collection, PAS une obligation du "
                "programme : le BO nomme des exemples d'algorithme sans les "
                "imposer. Ce controle verifie qu'une partie accompagnee de tels "
                "exemples comporte bien un travail algorithmique dans le manuel."
            ),
            "parts": qualite_algorithmique,
        },
        "rows": lignes,
    }
    texte = json.dumps(charge, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != texte:
            print(f"DIVERGENT : {OUT.relative_to(ROOT)}")
            return 1
        print("Matrice de couverture conforme au generateur.")
        return 0
    OUT.write_text(texte, encoding="utf-8")

    for manuel, detail in par_manuel.items():
        print(f"\n{manuel} ({detail['authority_ref']}) — "
              f"{detail['mandatory_items']} attendus obligatoires")
        for nature, stat in detail["by_normativity"].items():
            morceaux = " ".join(
                f"{cle}={val}" for cle, val in stat.items() if val
            )
            print(f"   {nature:<30s} {morceaux}")
    print()
    for cle, valeur in resume.items():
        print(f"{cle} = {valeur}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
