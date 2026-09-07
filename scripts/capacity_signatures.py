#!/usr/bin/env python3
"""Ce qu'un exercice doit CONTENIR pour servir une capacite donnee.

Une capacite n'est pas un code : c'est un geste mathematique. « Je sais
determiner les diviseurs d'un entier et le PGCD de deux entiers » demande des
entiers, une divisibilite, un algorithme d'Euclide. Un exercice sur la
convexite de `1/(1+x)` ne la sert pas, quel que soit le code inscrit dans son
META.

Ce module declare, capacite par capacite, les MARQUEURS MATHEMATIQUES dont la
presence est necessaire. Ce ne sont pas des mots-cles de rapprochement flou :
chaque signature est ecrite a la main, lisible, et contestable ligne a ligne.
Un marqueur est une expression reguliere appliquee au corps LaTeX et au bloc
oracle -- ce que l'eleve lit et ce que la machine verifie.

`REQUIRED` : au moins un marqueur de CHAQUE groupe doit apparaitre. Les
groupes expriment une conjonction de natures ; les alternatives a l'interieur
d'un groupe expriment les ecritures acceptables d'une meme notion.

`FORBIDDEN` : des marqueurs dont la presence, seule, revele un contenu d'un
autre domaine. On les emploie avec parcimonie -- un exercice d'arithmetique a
parfaitement le droit de deriver une fonction en chemin.

Une capacite sans signature n'est pas declaree alignee : elle est declaree
NON VERIFIEE, et le registre le dit.
"""

from __future__ import annotations

#: chapitre -> code de capacite -> {"required": [[alternatives], ...],
#:                                  "forbidden": [marqueurs]}
SIGNATURES: dict[str, dict[str, dict[str, list]]] = {
    "TEXP-ARITHMETIQUE": {
        "C1": {
            "required": [
                [r"\bdiviseur", r"\bdivisibilit", r"\bdivise\b", r"\bPGCD\b",
                 r"\bpgcd\b", r"\bgcd\b"],
                [r"\b\d{2,}\b", r"\bentier"],
            ],
        },
        "C2": {
            "required": [
                [r"\bcongruen", r"\bmodulo\b", r"\\equiv", r"\\bmod\b"],
                [r"\binvers", r"\bcongruen", r"\\equiv", r"\\bmod\b"],
            ],
        },
        "C3": {
            "required": [
                [r"\bdivisibilit", r"\bpremier", r"\bprimalit", r"\bchiffr",
                 r"\bcrypt"],
            ],
            "forbidden": [r"\\ln\b", r"convexit", r"tableau de variations"],
        },
        "C4": {
            # Une equation diophantienne se reconnait a sa FORME : deux
            # inconnues entieres, coefficients entiers, second membre entier.
            # Exiger le mot « diophantienne » dans l'enonce reviendrait a
            # demander a l'exercice de se nommer lui-meme.
            "required": [
                [
                    r"\bdiophantienne\b",
                    r"\bB[ée]zout\b",
                    r"\d+\s*x\s*\+\s*\d+\s*y\s*=",
                    r"a\s*x\s*\+\s*b\s*y",
                ],
                # « entieres » porte un accent : un marqueur qui l'ignore ne
                # verrait pas la moitie des enonces du corpus.
                [r"enti[eèé]r", r"\\mathbb\{Z\}"],
            ],
        },
        "C5": {
            "required": [
                [r"\bB[ée]zout\b", r"au\s*\+\s*bv", r"\bPGCD\b"],
                [r"D[ée]montrer|Montrer|Prouver|d[ée]duire"],
            ],
        },
        "C6": {"required": [[r"\bGauss\b"], [r"D[ée]montrer|Montrer|Prouver"]]},
        "C7": {
            "required": [
                [r"\bpremiers?\b"],
                [r"\binfini", r"d[ée]composition", r"facteurs premiers"],
            ],
        },
        "C8": {"required": [[r"\bFermat\b"]]},
        "C9": {
            "required": [
                [r"\bdef\b", r"\bPython\b", r"\\begin\{python\}", r"\btexttt\b"],
                [r"Euclide", r"crible", r"[ÉE]ratosth", r"facteurs premiers",
                 r"\bB[ée]zout\b"],
            ],
        },
    },
    "TEXP-GRAPHES": {
        "C1": {
            "required": [
                [r"\bsommet", r"\bar[êe]te", r"\bdegr[ée]", r"\bgraphe\b"],
                [r"\bdegr[ée]", r"\bconnexe", r"\bcomplet", r"\bordre\b",
                 r"\bcha[îi]ne"],
            ],
            "forbidden": [r"convexit", r"tableau de variations"],
        },
        "C2": {
            "required": [
                [r"\bmod[ée]lis", r"\bgraphe\b"],
                [r"\bsommet", r"\bar[êe]te", r"\brencontre", r"\bliaison"],
            ],
        },
        "C3": {
            "required": [
                [r"matrice d'adjacence", r"\bmatrice\b"],
                [r"\badjacen", r"\bgraphe\b", r"\bsommet"],
            ],
        },
        "C4": {
            "required": [
                [r"\bchemins?\b", r"\blongueur\b"],
                [r"\bM\^?\{?[23n]", r"puissance", r"\bM\^2", r"matrice"],
            ],
        },
        "C5": {
            # Le corpus dit « chaine » aussi bien que « chemin », et note le
            # coefficient $(M^n)_{ij}$ sans employer le mot. Exiger le mot
            # reviendrait a refuser la notation mathematique.
            "required": [
                [r"D[ée]montrer|Montrer|r[ée]currence|V[ée]rifier"],
                [r"\bchemins?\b", r"\bcha[îi]nes?\b", r"coefficient",
                 r"\(M\^\{?\d*n?\}?\)_"],
            ],
        },
    },
}


def signature_for(chapter: str, capacity: str) -> dict[str, list] | None:
    return SIGNATURES.get(chapter, {}).get(capacity)


def declared_chapters() -> list[str]:
    return sorted(SIGNATURES)
