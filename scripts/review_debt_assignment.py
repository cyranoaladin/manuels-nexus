#!/usr/bin/env python3
"""Qui, aujourd'hui, doit relire cet objet -- et une seule fois.

Plusieurs consommateurs revendiquaient le meme objet. Trois fiches methodes
ADGK etaient simultanement « qualifiees et courantes » dans la file A4,
« qualifications suspendues » dans la file de requalification, et entrees du
registre de dette du lot couple. Chaque consommateur portait sa propre garde
de disjonction, et chacune cassait separement -- trois corrections
independantes pour un seul defaut.

La regle est donc posee UNE fois, ici.

PRECEDENCE. Un registre de dette EXPLICITE et courant l'emporte sur toute
file derivee d'une qualification. Ce n'est pas un arbitrage esthetique : le
registre explicite est le paquet dans lequel un humain verra reellement
l'objet. Laisser l'objet aussi dans une file derivee le ferait compter deux
fois sans que personne ne le relise deux fois.

Ce que la precedence ne fait PAS : elle ne referme aucune dette, ne requalifie
rien et n'approuve rien. L'etat « suspendu » ou « perime » reste vrai sur le
disque ; il cesse seulement d'etre une seconde imputation.

ORDRE. L'attribution ne depend ni de l'ordre de lecture des registres, ni de
l'ordre des cles YAML, ni du nom des fichiers : la precedence porte sur la
CLASSE du porteur, et deux registres d'une meme classe doivent etre disjoints
-- une violation est une erreur, jamais un depart au plus offrant.
"""

from __future__ import annotations

from typing import Mapping


#: Classes de porteurs, de la plus forte a la plus faible.
EXPLICIT_CURRENT_REVIEW_LEDGER = "EXPLICIT_CURRENT_REVIEW_LEDGER"
DERIVED_QUALIFICATION_QUEUE = "DERIVED_QUALIFICATION_QUEUE"
PRECEDENCE = (EXPLICIT_CURRENT_REVIEW_LEDGER, DERIVED_QUALIFICATION_QUEUE)


class DuplicateAttribution(ValueError):
    """Deux porteurs de MEME classe revendiquent le meme objet."""


def assign(
    explicit_ledgers: Mapping[str, set[str]],
    derived_queues: Mapping[str, set[str]],
) -> dict[str, str]:
    """Un proprietaire de dette de revue par objet, et un seul.

    Renvoie `{empreinte: nom du porteur}`. Une empreinte revendiquee par deux
    porteurs de la meme classe leve `DuplicateAttribution` : a l'interieur
    d'une classe il n'y a pas de precedence a appliquer, donc pas de choix
    legitime a faire.
    """

    owner: dict[str, str] = {}
    for klass, carriers in (
        (EXPLICIT_CURRENT_REVIEW_LEDGER, explicit_ledgers),
        (DERIVED_QUALIFICATION_QUEUE, derived_queues),
    ):
        claimed_in_class: dict[str, str] = {}
        for name in sorted(carriers):
            for fingerprint in sorted(carriers[name]):
                previous = claimed_in_class.get(fingerprint)
                if previous is not None:
                    raise DuplicateAttribution(
                        f"{fingerprint} revendique par {previous} et {name} "
                        f"dans la meme classe {klass}"
                    )
                claimed_in_class[fingerprint] = name
                owner.setdefault(fingerprint, name)
    return owner


def owned_by_class(
    explicit_ledgers: Mapping[str, set[str]],
    derived_queues: Mapping[str, set[str]],
) -> dict[str, set[str]]:
    """Les empreintes retenues pour chaque porteur, apres precedence."""

    owner = assign(explicit_ledgers, derived_queues)
    result: dict[str, set[str]] = {
        name: set() for name in (*explicit_ledgers, *derived_queues)
    }
    for fingerprint, name in owner.items():
        result[name].add(fingerprint)
    return result


def demoted_by_precedence(
    explicit_ledgers: Mapping[str, set[str]],
    derived_queues: Mapping[str, set[str]],
) -> set[str]:
    """Empreintes qu'un registre explicite retire d'une file derivee.

    Elles ne sont NI resolues NI approuvees : elles changent d'imputation.
    """

    explicit = set().union(*explicit_ledgers.values()) if explicit_ledgers else set()
    derived = set().union(*derived_queues.values()) if derived_queues else set()
    return derived & explicit
