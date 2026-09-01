#!/usr/bin/env python3
"""Ou va chaque objet que l'oracle a laisse en revue manuelle.

L'oracle SymPy rend `manual_review` pour une seule et meme raison : l'objet ne
porte pas de bloc VERIFY. Ce motif unique melange des situations qui n'ont rien
a voir -- un coup de pouce qui ne contient aucun calcul, un QCM dont la science
vit dans un JSON autoritaire, un cours qui enonce une formule que rien ne
verifie. Envoyer les 249 a un expert, c'est lui demander de trier a la main ce
que la machine sait trier.

Ce registre les route. Il ne rend AUCUN objet vert : il dit, pour chacun, ce
que la machine peut affirmer et ce qu'elle ne peut pas.

    AUCUNE_AFFIRMATION_CALCULABLE
        l'objet ne contient aucune relation portant sur des nombres. Le silence
        de l'oracle est alors la bonne reponse, pas une lacune.

    DERIVE_D_UNE_SOURCE_AUTORITAIRE
        le .tex est engendre depuis un JSON autoritaire et lui est synchrone
        (build_qcm_tex --check). Cela prouve la TRANSCRIPTION, jamais que la
        reponse designee soit la bonne : la science reste a relire.

    SCIENCE_HUMAINE_REQUISE
        l'objet affirme des choses calculables que rien ne verifie. C'est la
        seule classe qui demande vraiment un mathematicien.

Aucune disposition n'est attachee a un identifiant d'objet : chacune se deduit
de ce que l'objet CONTIENT. Un registre qui nommerait des objets un a un
serait une liste blanche, pas une mesure.

L'objectif n'est pas MANUAL_REVIEW = 0 -- une revue humaine est un resultat
legitime -- mais MACHINE_UNCLASSIFIED = 0.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
OUTPUT = ROOT / "audit/1SPE_MANUAL_REVIEW_DISPOSITION_LEDGER.json"
CHAPTERS = ROOT / "Mathematiques" / "manuel-maths" / "chapitres"
SCOPE_PREFIX = "1SPE-"

MATH = re.compile(r"\$[^$]+\$|\\\[.*?\\\]", re.S)
RELATION = re.compile(r"(=|\\leq|\\geq|\\neq|\\approx|<|>)")
DIGIT = re.compile(r"\d")

NO_CLAIM = "AUCUNE_AFFIRMATION_CALCULABLE"
AUTHORITATIVE = "DERIVE_D_UNE_SOURCE_AUTORITAIRE"
HUMAN = "SCIENCE_HUMAINE_REQUISE"


def computable_claims(body: str) -> list[str]:
    """Les affirmations calculables : une relation portant sur des nombres."""

    return [
        segment.strip()
        for segment in MATH.findall(body)
        if RELATION.search(segment) and DIGIT.search(segment)
    ]


def _meta(text: str) -> dict[str, Any]:
    try:
        return json.loads(text.split("META:", 1)[1].split("\n", 1)[0])
    except (IndexError, json.JSONDecodeError):
        return {}


def build_ledger() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    unclassified: list[str] = []
    for chapter in sorted(p for p in CHAPTERS.iterdir() if p.name.startswith(SCOPE_PREFIX)):
        validations = chapter / "validations"
        if not validations.is_dir():
            continue
        for receipt_path in sorted(validations.glob("*.sympy.json")):
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            if receipt.get("verdict") != "manual_review":
                continue
            stem = receipt_path.name[: -len(".sympy.json")]
            source = next((p for p in chapter.rglob(stem + ".tex")), None)
            if source is None:
                # Un recu qui survit a son objet : c'est un defaut de preuve,
                # pas une disposition.
                unclassified.append(stem)
                continue
            text = source.read_text(encoding="utf-8")
            meta = _meta(text)
            body = text.split("\n", 1)[1] if "\n" in text else ""
            kind = meta.get("type_objet")
            claims = computable_claims(body)
            if kind == "qcm":
                disposition = AUTHORITATIVE
                because = (
                    "engendre depuis le JSON autoritaire du chapitre et "
                    "synchrone avec lui ; la transcription est prouvee, la "
                    "science des reponses reste a relire"
                )
            elif not claims:
                disposition = NO_CLAIM
                because = "aucune relation portant sur des nombres"
            else:
                disposition = HUMAN
                because = f"{len(claims)} affirmations calculables sans preuve machine"
            rows.append(
                {
                    "chapter": chapter.name,
                    "object_id": meta.get("id", stem),
                    "type_objet": kind,
                    "path": str(source.relative_to(ROOT)),
                    "disposition": disposition,
                    "because": because,
                    "computable_claims": len(claims),
                    "capacites": meta.get("capacites_codes") or [],
                }
            )

    rows.sort(key=lambda row: (row["chapter"], str(row["object_id"])))
    by_disposition = collections.Counter(row["disposition"] for row in rows)
    by_chapter: dict[str, dict[str, int]] = collections.defaultdict(
        lambda: collections.defaultdict(int)
    )
    for row in rows:
        by_chapter[row["chapter"]][row["disposition"]] += 1
    digest = hashlib.sha256(
        "\n".join(f"{r['object_id']}:{r['disposition']}" for r in rows).encode("utf-8")
    ).hexdigest()
    return {
        "artifact_type": "manual_review_disposition_ledger",
        "schema_version": 1,
        "scope": "1SPE",
        "machine_unclassified": len(unclassified),
        "machine_unclassified_ids": sorted(unclassified),
        "totals": dict(sorted(by_disposition.items())),
        "human_queue_size": by_disposition[HUMAN] + by_disposition[AUTHORITATIVE],
        "per_chapter": {k: dict(sorted(v.items())) for k, v in sorted(by_chapter.items())},
        "object_set_digest": "sha256:" + digest,
        "objects": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    ledger = build_ledger()
    payload = json.dumps(ledger, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
        if current != payload:
            print("1SPE_MANUAL_REVIEW_DISPOSITION_LEDGER stale")
            return 1
        print("1SPE_MANUAL_REVIEW_DISPOSITION_LEDGER a jour")
        return 0
    OUTPUT.write_text(payload, encoding="utf-8")
    print(
        f"wrote {OUTPUT.name}: {ledger['totals']}, "
        f"non classes {ledger['machine_unclassified']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
