#!/usr/bin/env python3
"""Revues mathématiques des objets qu'aucun oracle ne peut trancher.

Un bloc `% BEGIN-VERIFY` prouve ce qui se calcule. Quatre cent dix-sept objets
du corpus n'en portent pas et ne peuvent pas en porter : un coup de pouce
reformule une étape, une fiche méthode décrit une démarche, une version
aménagée allège un énoncé. Leur exactitude mathématique existe pourtant, et
personne ne l'a établie.

Ce fichier la déclare, objet par objet. Chaque revue dit quatre choses, et le
producteur vérifie que les quatre sont là :

  `science`     ce qui est mathématiquement affirmé, et pourquoi c'est vrai ;
  `programme`   la capacité du contrat que l'objet sert ;
  `pedagogy`    ce que l'objet fait pour l'élève, et pourquoi c'est adapté ;
  `editorial`   ce qui a été vérifié dans la forme — notations, renvois.

Une revue qui se contente de paraphraser le titre n'est pas une revue : le
producteur refuse les champs trop courts, et refuse une revue qui ne nomme
aucune source. Ce qui reste sans revue reste `PENDING` et compte.

AUCUNE REVUE ICI N'APPROUVE. Elle établit `VALIDATED_BY_EVIDENCE` ; le
sign-off humain porte sur le corpus gelé, et lui seul.
"""

from __future__ import annotations

from typing import Any

#: chemin relatif de l'objet -> revue.
REVIEWS: dict[str, dict[str, Any]] = {}

#: Longueur en dessous de laquelle un champ ne dit rien d'utile.
MINIMUM = 60


def revue(
    chemin: str,
    *,
    science: str,
    programme: str,
    pedagogy: str,
    editorial: str,
    defect: str | None = None,
) -> None:
    """Déclare la revue d'un objet non formalisable.

    `defect` nomme un défaut trouvé pendant la revue. Une revue qui trouve un
    défaut et le tait ne vaut rien : le champ existe pour que la correction
    soit tracée à côté du constat.
    """
    if chemin in REVIEWS:
        raise ValueError(f"revue déjà déclarée : {chemin}")
    for nom, valeur in (
        ("science", science), ("programme", programme),
        ("pedagogy", pedagogy), ("editorial", editorial),
    ):
        if len(valeur.strip()) < MINIMUM:
            raise ValueError(f"{chemin}: champ {nom} trop court pour être une revue")
    REVIEWS[chemin] = {
        "science": science.strip(),
        "programme": programme.strip(),
        "pedagogy": pedagogy.strip(),
        "editorial": editorial.strip(),
        "defect": defect,
    }
