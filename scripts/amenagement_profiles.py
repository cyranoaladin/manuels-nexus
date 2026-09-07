#!/usr/bin/env python3
"""Profils d'amenagement : ce qu'on a le droit de changer, et ce qu'on doit garder.

Une version amenagee n'est pas une version facile. Elle s'adresse a des eleves
dont un plan d'accompagnement prevoit des amenagements — consignes sequencees,
supports aeres, temps majore. Ce qui change est le CHEMIN vers la reponse ;
ce qui ne change pas est la CAPACITE evaluee.

La faute a eviter porte un nom : baisser l'exigence en croyant amenager. Un
exercice dont on retire la capacite visee n'est pas amenage, il est vide. Le
producteur verifie donc que chaque objet amenage :

  * declare l'objet canonique dont il derive, et cet objet existe ;
  * ne travaille aucune capacite absente de sa source — l'amenagement ne
    deplace pas la cible ;
  * travaille au moins une capacite de sa source — sinon il n'en derive plus ;
  * declare au moins un profil connu, et chaque profil declare laisse une
    trace observable dans le texte.

Ce dernier point est le seul qui empeche un objet de se declarer amenage sans
l'etre. Un profil sans marque dans le fichier est une etiquette, pas un
amenagement.
"""

from __future__ import annotations

import re

# profil -> (ce qu'il change, marque observable dans le texte)
PROFILES: dict[str, tuple[str, re.Pattern[str]]] = {
    "SEQUENCAGE": (
        "L'enonce est decoupe en etapes numerotees, une consigne par etape. "
        "L'eleve n'a jamais a tenir plusieurs consignes en memoire.",
        re.compile(r"\\textbf\{[EÉ]tape\s*\d+"),
    ),
    "ALLEGEMENT_ENONCE": (
        "Les phrases sont courtes et portent une information chacune. Le "
        "contexte narratif non necessaire a la tache est retire.",
        re.compile(r"\\subsection\*\{"),
    ),
    "REPONSE_FERMEE": (
        "La production libre devient un choix entre reponses proposees, un "
        "texte a trous ou un tableau a completer. Ce qui est evalue reste la "
        "meme decision ; c'est sa forme d'expression qui est allegee.",
        re.compile(r"\\fbox\{|\\dotfill|______"),
    ),
    "AERATION": (
        "Espacement vertical explicite, une tache par bloc visuel, tableaux "
        "plutot que paragraphes.",
        re.compile(r"\\bigskip|\\medskip"),
    ),
    "AMORCE_FOURNIE": (
        "Le debut du code ou du raisonnement est donne. L'eleve poursuit au "
        "lieu de demarrer sur une page blanche.",
        None,   # marque composite : voir `_amorce_fournie`
    ),
    "RETRAIT_DOUBLE_TACHE": (
        "Une seule operation cognitive a la fois : on ne demande pas de lire "
        "un programme ET de le modifier dans la meme question.",
        re.compile(r"\\textbf\{[EÉ]tape\s*\d+"),
    ),
}

# La contrainte de rendu est reelle : `\lstinline{...}` juste avant un `&` casse
# la compilation d'un tabular. Elle est verifiee ici pour que l'auteur le
# sache a l'ecriture, pas a la compilation du livret.
FRAGILE_IN_TABULAR = re.compile(r"\\lstinline\{[^}]+\}\s*&")


CODE_WITH_BLANK = re.compile(
    r"\\begin\{(?:python|console)\}(?:(?!\\end\{)[\s\S])*?______",
)
TABULAR = re.compile(r"\\begin\{tabular\}[\s\S]*?\\end\{tabular\}")


def _amorce_fournie(text: str) -> bool:
    """Un debut est-il reellement donne ?

    Une amorce prend deux formes dans ce corpus, et la premiere version de ce
    marqueur n'en voyait qu'une. Ecrire `\\begin{python}` ne suffit pas : un
    bloc de code complet, sans trou, n'amorce rien — c'est un enonce. Et un
    extrait aere sans une seule ligne de Python peut tres bien amorcer, par la
    premiere ligne d'un tableau remplie comme modele.

    Les deux formes reconnues, toutes deux constatees sur le fichier :

      * un bloc `python` ou `console` qui contient un trou : le debut est
        ecrit, la suite est a completer ;
      * un tableau dont au moins une ligne de donnees est entierement remplie
        alors qu'une autre porte un trou : la ligne pleine sert de modele.
    """
    if CODE_WITH_BLANK.search(text):
        return True
    for table in TABULAR.findall(text):
        rows = [
            row.strip() for row in table.split(r"\\")
            if row.strip() and "&" in row
        ]
        filled = [r for r in rows if "\\dotfill" not in r and "______" not in r]
        blanks = [r for r in rows if "\\dotfill" in r or "______" in r]
        # la ligne d'en-tete est pleine par nature : il en faut une seconde
        if len(filled) >= 2 and blanks:
            return True
    return False


def observed_profiles(text: str) -> set[str]:
    """Profils dont la marque est effectivement presente dans le texte."""
    observed = {
        name for name, (_, mark) in PROFILES.items()
        if mark is not None and mark.search(text)
    }
    if _amorce_fournie(text):
        observed.add("AMORCE_FOURNIE")
    return observed
