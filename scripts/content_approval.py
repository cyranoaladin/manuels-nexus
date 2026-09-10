#!/usr/bin/env python3
"""Ce qu'une approbation humaine couvre exactement, et jusqu'a quand.

Une approbation ne suit pas un chemin de fichier : elle suit un contenu. Un
objet qui porte `status: approved` alors que son texte a change depuis
l'approbation affirme une chose fausse -- qu'un humain a valide ce que l'eleve
lira. Ce module etablit, pour chaque objet, le contenu qui a REELLEMENT ete
approuve, en remontant l'historique jusqu'au commit ou le statut approbatif a
ete pose.

Deux familles de changements ne remettent rien en cause, et elles sont
declarees ici plutot que devinees :

- ce que l'eleve ne voit pas : les lignes de commentaire, blocs
  « BEGIN-VERIFY » compris. Un bloc de verification prouve au producteur que
  le contenu est juste ; il ne modifie pas une ligne de ce qui est imprime ;
- les differences purement typographiques : diacritiques, apostrophes,
  guillemets, tirets, espaces. Le depot a deja tranche ce point par un recu
  humain de requalification diacritique.

Une troisieme famille est declaree explicitement, parce qu'elle a une cause
identifiee : la reparation d'une sequence de controle LaTeX cassee. La
campagne de diacritiques avait coupe des `\\neq` en un saut de ligne suivi de
« eq », qui s'imprimait tel quel. Retablir `\\neq` restitue le sens que
l'approbation visait ; ce n'est pas une reecriture.

Tout le reste invalide l'approbation.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import re
import subprocess
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

#: Statuts qui affirment une validation humaine du contenu. `verified` en est
#: exclu a dessein : il atteste une verification machine, pas une relecture.
STATUTS_PORTANT_APPROBATION = frozenset({"approved"})

#: Statut de repli quand une approbation est invalidee. Il ne fabrique aucun
#: humain : il dit que l'objet attend une relecture.
STATUT_APRES_INVALIDATION = "needs_review"

#: Valeur du champ `approval_state` d'un objet dont l'approbation a ete
#: invalidee par une edition semantique.
APPROBATION_PERIMEE = "STALE_AFTER_SEMANTIC_EDIT"

_ESPACES = re.compile(r"\s+")
_TYPOGRAPHIE = (
    ("œ", "oe"), ("Œ", "OE"),
    ("’", "'"), ("‘", "'"),
    ("—", "-"), ("–", "-"),
    (" ", " "), (" ", " "),
    ("«", '"'), ("»", '"'),
)


def meta_de(texte: str) -> dict[str, Any]:
    premiere = texte.split("\n", 1)[0]
    if not premiere.startswith("% META:"):
        return {}
    try:
        charge = json.loads(premiere[len("% META:"):].strip())
    except json.JSONDecodeError:
        return {}
    return charge if isinstance(charge, dict) else {}


def jetons_visibles(texte: str) -> list[str]:
    """Les mots que l'eleve lira, replies typographiquement."""
    corps = "\n".join(
        ligne for ligne in texte.split("\n")[1:] if not ligne.lstrip().startswith("%")
    )
    plie = "".join(
        c for c in unicodedata.normalize("NFD", corps) if not unicodedata.combining(c)
    )
    for avant, apres in _TYPOGRAPHIE:
        plie = plie.replace(avant, apres)
    return _ESPACES.sub(" ", plie).strip().split(" ")


def empreinte_visible(texte: str) -> str:
    return "sha256:" + hashlib.sha256(
        " ".join(jetons_visibles(texte)).encode("utf-8")
    ).hexdigest()


def reparation_de_sequence_latex(avant: list[str], apres: list[str]) -> bool:
    """Le seul ecart est-il la reparation d'un `\\neq` coupe par la campagne ?

    La campagne de diacritiques a remplace des `\\neq` par un saut de ligne
    suivi de « eq ». Le mot imprime devenait « eq ». Retablir la sequence de
    controle ne change pas ce que l'objet enonce : cela restitue ce qu'il
    enoncait deja avant d'etre casse.
    """
    comparateur = difflib.SequenceMatcher(a=avant, b=apres, autojunk=False)
    ecarts = 0
    for operation, i1, i2, j1, j2 in comparateur.get_opcodes():
        if operation == "equal":
            continue
        if operation != "replace" or (i2 - i1) != (j2 - j1):
            return False
        for ancien, nouveau in zip(avant[i1:i2], apres[j1:j2]):
            if not (ancien.startswith("eq") and nouveau == "\\n" + ancien):
                return False
            ecarts += 1
    return ecarts > 0


def historique_des_objets() -> dict[str, list[tuple[str, str]]]:
    """chemin -> [(commit, blob), ...], du plus recent au plus ancien.

    Un seul appel a git : parcourir l'historique fichier par fichier prendrait
    des milliers de processus pour la meme information.
    """
    sortie = subprocess.run(
        ["git", "log", "--format=@%H", "--raw", "--no-abbrev", "--no-renames",
         "--", "*.tex"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    histoire: dict[str, list[tuple[str, str]]] = defaultdict(list)
    commit = ""
    for ligne in sortie.splitlines():
        if ligne.startswith("@"):
            commit = ligne[1:]
        elif ligne.startswith(":"):
            gauche, chemin = ligne.split("\t", 1)
            apres = gauche.split()[3]
            if set(apres) != {"0"}:
                histoire[chemin].append((commit, apres))
    return histoire


def lire_blobs(blobs: set[str]) -> dict[str, str]:
    if not blobs:
        return {}
    processus = subprocess.Popen(
        ["git", "cat-file", "--batch"], cwd=ROOT,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    )
    brut, _ = processus.communicate(("\n".join(sorted(blobs)) + "\n").encode())
    contenu: dict[str, str] = {}
    curseur = 0
    while curseur < len(brut):
        fin = brut.index(b"\n", curseur)
        entete = brut[curseur:fin].split()
        if len(entete) == 2:  # « <sha> missing »
            curseur = fin + 1
            continue
        sha, _type, taille = entete
        n = int(taille)
        contenu[sha.decode()] = brut[fin + 1:fin + 1 + n].decode("utf-8", "replace")
        curseur = fin + 1 + n + 1
    return contenu
