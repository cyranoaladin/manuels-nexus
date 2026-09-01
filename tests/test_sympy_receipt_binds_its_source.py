"""Un recu doit pouvoir PERIMER.

P0_VERIFICATION_INVARIANT_BLINDNESS, meme famille : une preuve insensible a
la faute qu'elle devrait voir. Les recus SymPy ne nommaient pas la source
verifiee. Un « pass » date du 29 juillet continuait donc de certifier un
contenu modifie depuis, sans que rien ne puisse le detecter.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "Mathematiques/manuel-maths/chapitres"


def _premiere_chapters() -> list[Path]:
    return sorted(p for p in CHAPTERS.iterdir() if p.name.startswith("1SPE-"))


def test_every_receipt_names_the_source_it_attests() -> None:
    unbound: list[str] = []
    for chapter in _premiere_chapters():
        for receipt in sorted((chapter / "validations").glob("*.sympy.json")):
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            if not payload.get("source_path") or not payload.get("source_sha256"):
                unbound.append(str(receipt.relative_to(ROOT)))
    assert unbound == [], f"recus sans source attestee : {len(unbound)}"


def test_a_receipt_goes_stale_when_its_source_changes() -> None:
    """Le controle qui manquait : comparer le digest, pas seulement lire un
    verdict."""
    stale: list[str] = []
    for chapter in _premiere_chapters():
        for receipt in sorted((chapter / "validations").glob("*.sympy.json")):
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            declared = payload.get("source_path")
            if not declared:
                continue
            source = ROOT / "Mathematiques/manuel-maths" / declared
            if not source.is_file():
                stale.append(f"{declared} (source absente)")
                continue
            digest = "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()
            if digest != payload.get("source_sha256"):
                stale.append(declared)
    assert stale == [], f"recus perimes : {stale[:10]} (total {len(stale)})"


def test_no_receipt_attests_an_object_that_no_longer_exists() -> None:
    """Un recu doit mourir avec l'objet qu'il atteste.

    Le commit 8ecd58e0 a retire les capacites C3/C4/C5 de 1SPE-TRIGONOMETRIE
    pour conformite au BO 2026. Le contenu est bien parti ; ses recus sont
    restes. Le chapitre annoncait alors 140 recus dont 108 « pass », quand 67
    d'entre eux -- 58 « pass » -- n'attestaient plus rien.

    C'est la meme cecite que le P0 : un COMPTE presente comme une preuve. Un
    nombre eleve de verifications ne prouve rien si ces verifications portent
    sur des fichiers disparus.
    """
    orphans: list[str] = []
    for chapter in _premiere_chapters():
        validations = chapter / "validations"
        if not validations.is_dir():
            continue
        for receipt in sorted(validations.glob("*.sympy.json")):
            stem = receipt.name[: -len(".sympy.json")]
            if not list(chapter.rglob(f"{stem}.tex")):
                orphans.append(str(receipt.relative_to(ROOT)))
    assert orphans == [], (
        f"recus attestant un objet disparu : {len(orphans)}"
    )
