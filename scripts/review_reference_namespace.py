#!/usr/bin/env python3
"""Resoudre un renvoi de QCM dans le bon espace de noms.

Les diagnostics du QCM renvoient l'eleve vers ce qui l'aidera. Ces renvois
melangent DEUX espaces de noms distincts, et le code seul ne dit pas lequel :

    `M7`  une METHODE du chapitre        -> methodes/<CHAP>-ME-007.tex
    `R5`  un PREREQUIS du contrat        -> remediation/<CHAP>-FR-R5.tex

`R5` n'est ni une capacite (`C5`) ni l'identifiant d'un objet de remediation
(`RE-C5`). Presente a un expert sous le seul intitule « remediation_reference »,
la lettre R se lit comme un objet de remediation, et le lecteur ne peut pas
savoir qu'il s'agit du prerequis « Python : variables, boucle for, boucle while »
herite de SNT. Un dossier de relecture qui aplatit deux espaces de noms fait
signer une chose pour une autre.

Les deux espaces sont derives du chapitre lui-meme -- prerequis du contrat,
fichiers de methodes et de remediation presents -- jamais d'une table figee
dans le code. Un renvoi qu'aucun des deux espaces ne reconnait sort en
`UNKNOWN` : il reste visible, il n'est pas devine.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

METHODE = "METHODE"
PREREQUIS = "PREREQUIS"
UNKNOWN = "UNKNOWN"

TOKEN = re.compile(r"\b([MR])(\d+)\b")


def _contract_prerequisites(chapter_dir: Path) -> dict[str, str]:
    contract = chapter_dir / "contrat.yaml"
    if not contract.is_file():
        return {}
    data = yaml.safe_load(contract.read_text(encoding="utf-8")) or {}
    return {
        str(item["code"]): str(item.get("libelle", ""))
        for item in (data.get("prerequis") or [])
        if isinstance(item, dict) and item.get("code")
    }


def resolve(renvoi: str, chapter_dir: Path) -> list[dict[str, Any]]:
    """Chaque code d'un renvoi, avec l'espace de noms qui lui donne son sens."""

    chapter = chapter_dir.name
    prerequisites = _contract_prerequisites(chapter_dir)
    resolved: list[dict[str, Any]] = []
    seen: set[str] = set()
    for letter, number in TOKEN.findall(renvoi or ""):
        code = f"{letter}{number}"
        if code in seen:
            continue
        seen.add(code)
        if letter == "M":
            target = chapter_dir / "methodes" / f"{chapter}-ME-{int(number):03d}.tex"
            resolved.append(
                {
                    "code": code,
                    "namespace": METHODE if target.is_file() else UNKNOWN,
                    "label": "methode du chapitre",
                    "object_id": target.stem if target.is_file() else None,
                }
            )
        else:
            sheet = chapter_dir / "remediation" / f"{chapter}-FR-{code}.tex"
            known = code in prerequisites
            resolved.append(
                {
                    "code": code,
                    "namespace": PREREQUIS if known else UNKNOWN,
                    "label": prerequisites.get(code, ""),
                    "object_id": sheet.stem if sheet.is_file() else None,
                    "note": (
                        "prerequis du contrat, pas une capacite : "
                        f"{code} n'est pas C{code[1:]}"
                    )
                    if known
                    else "code non reconnu dans les deux espaces de noms",
                }
            )
    return resolved
