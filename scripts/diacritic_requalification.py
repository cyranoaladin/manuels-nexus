#!/usr/bin/env python3
"""Re-liaison batch des qualifications dont le changement est strictement diacritique.

DÉCISION HUMAINE COUVERTE. Release Owner `abenrhouma` :
`ACCEPT_SEMANTICALLY_NEUTRAL_DIACRITIC_REQUALIFICATION`. Elle autorise UNE
classe de re-liaisons — celles dont l'audit démontre que rien d'autre qu'un
accent n'a bougé — et rien d'autre.

CE QUE CE MODULE NE FAIT PAS. Il n'approuve aucun contenu. Une re-liaison
rattache une qualification existante au texte courant ; elle ne transforme pas
`needs_review` en `approved`, et le gate continue de compter ces objets comme
dette de revue ouverte.

POURQUOI UN SEUL RECEIPT. Fabriquer 86 receipts humains individuels ferait
croire à 86 lectures humaines. Il y en a une : celle de la classe. Le receipt
unique porte la liste exhaustive des qualifications couvertes, et un objet
absent de cette liste n'hérite de rien.

LA NEUTRALITÉ EST RECALCULÉE, PAS LUE. `change_class` déposé dans la file de
requalification n'est pas cru : les deux versions sont retrouvées, dépouillées
de leurs signes diacritiques, et comparées octet à octet. Toute autre
différence — un chiffre, une formule, un identifiant, une phrase ajoutée, une
négation, une lettre de base — sort l'objet du lot.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from typing import Any, Iterable, Mapping

ACCENT_ONLY = "ACCENT_ONLY"
SUBSTANTIVE = "SUBSTANTIVE_CHANGE"
UNCHANGED = "UNCHANGED"

DECISION = "ACCEPT_SEMANTICALLY_NEUTRAL_DIACRITIC_REQUALIFICATION"

#: Champs que la décision humaine exige dans le receipt batch.
RECEIPT_FIELDS = (
    "REVIEWER_IDENTITY",
    "DECISION",
    "QUALIFICATION_COUNT",
    "QUALIFICATION_IDS_DIGEST",
    "OLD_PEDAGOGICAL_DIGESTS_DIGEST",
    "NEW_PEDAGOGICAL_DIGESTS_DIGEST",
    "DIACRITIC_FORENSICS_EVIDENCE_DIGEST",
)


def strip_accents(text: str) -> str:
    """Le texte privé de ses seuls signes diacritiques.

    La décomposition NFD sépare la lettre de base de son signe ; on retire les
    catégories `Mn` (marques sans chasse) et rien d'autre. Une lettre de base
    changée survit donc à ce dépouillement et sera vue comme une différence.
    """
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def recompute_change_class(before: str, after: str) -> str:
    """Classe du changement, recalculée sur les deux textes eux-mêmes."""
    if before == after:
        return UNCHANGED
    if strip_accents(before) == strip_accents(after):
        return ACCENT_ONLY
    return SUBSTANTIVE


def eligible(items: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """Les seuls items que la décision couvre.

    Filtre positif : on ne retire pas les inéligibles, on ne garde que les
    éligibles. Une classe nouvelle ou inattendue reste donc dehors.
    """
    return [item for item in items if item.get("change_class") == ACCENT_ONLY]


def identifiers_digest(identifiers: Iterable[str]) -> str:
    """Empreinte d'un ensemble d'identifiants, indépendante de leur ordre.

    Le compte seul ne distinguerait pas deux lots différents de même taille :
    c'est la liste qui est engagée, pas son cardinal.
    """
    payload = "\n".join(sorted(set(str(i) for i in identifiers)))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def covered_by(receipt: Mapping[str, Any], fingerprint: str) -> bool:
    """L'autorisation batch couvre-t-elle cette qualification ?"""
    return str(fingerprint) in set(receipt.get("qualification_ids") or [])


def payload_digest(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()
