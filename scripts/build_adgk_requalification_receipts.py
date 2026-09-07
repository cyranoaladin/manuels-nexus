#!/usr/bin/env python3
"""Receipts nominatifs des trois requalifications ADGK, sur contenu courant.

DÉCISION HUMAINE COUVERTE. Le Release Owner autorise la requalification de
`1NSI-ADGK-ME-001`, `-002` et `-003` sur leur contenu COURANT, sous réserve
stricte que l'objet soit exactement celui qu'ont audité les preuves annoncées.

Un receipt par objet, et non un lot : ces trois changements sont des
modifications pédagogiques réelles, pas une neutralité orthographique. Les
assimiler au lot diacritique effacerait précisément ce qui les distingue.

LA RÉSERVE EST MÉCANIQUE. Chaque receipt lie l'empreinte du contenu courant à
l'empreinte du fichier de preuves qui l'a testé. Si le contenu diffère de
celui soumis aux tests, l'objet n'est pas requalifié — le producteur refuse,
il ne signale pas.

CE QUE CHAQUE DÉCISION COUVRE, ET RIEN DE PLUS. Le périmètre est recopié de la
décision humaine, pas déduit. Pour le glouton en particulier, le
contre-exemple `{1,3,4}` sert uniquement à réfuter l'optimalité générale ; il
ne doit jamais être transformé en preuve d'une assertion plus large.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import evidence_freshness as freshness  # noqa: E402

DISPOSITIONS = ROOT / "audit/ANOMALY_DISPOSITIONS.yaml"
REGRESSION_TESTS = ROOT / "tests/test_adgk_method_regression.py"
OUTPUT_JSON = ROOT / "audit/ADGK_REQUALIFICATION_RECEIPTS.json"
OUTPUT_MD = ROOT / "audit/ADGK_REQUALIFICATION_RECEIPTS.md"

DECISION = "ACCEPT_EVIDENCE_BACKED_CONTENT_REQUALIFICATION"

#: Périmètre exact de la décision humaine, objet par objet. Recopié, pas déduit.
SCOPE: dict[str, dict[str, Any]] = {
    "1NSI-ADGK-ME-001": {
        "fingerprint": "ed9e59a472a9e4a5",
        "source": (
            "NSI/chapitres/1NSI-ALGO-DICHO-GLOUTON-KNN/methodes/"
            "1NSI-ADGK-ME-001.tex"
        ),
        "contract": "élément absent -> -1",
        "covered_evidence": [
            "tableau vide",
            "élément absent",
            "élément présent",
            "doublons",
            "bornes (première et dernière case)",
            "4 000 cas contre oracle",
            "variant d-g strictement décroissant et positif ou nul",
        ],
    },
    "1NSI-ADGK-ME-002": {
        "fingerprint": "74aacd756bac15f4",
        "source": (
            "NSI/chapitres/1NSI-ALGO-DICHO-GLOUTON-KNN/methodes/"
            "1NSI-ADGK-ME-002.tex"
        ),
        "contract": "rendu exact dans le domaine revendiqué, ou refus explicite",
        "covered_evidence": [
            "exactitude dans le domaine revendiqué (système euro)",
            "comparaison par programmation dynamique sur les cas testés",
            "contre-exemple {1,3,4} réfutant l'optimalité GÉNÉRALE uniquement",
        ],
        "scope_limit": (
            "Le contre-exemple {1,3,4} ne doit jamais être transformé en "
            "preuve d'une assertion plus large : il réfute l'optimalité "
            "générale, il ne dit rien de l'exactitude ni du système euro."
        ),
    },
    "1NSI-ADGK-ME-003": {
        "fingerprint": "b0b81c9742c416e1",
        "source": (
            "NSI/chapitres/1NSI-ALGO-DICHO-GLOUTON-KNN/methodes/"
            "1NSI-ADGK-ME-003.tex"
        ),
        "contract": "classe majoritaire, égalité tranchée par le voisin le plus proche",
        "covered_evidence": [
            "règle de départage courante",
            "20 000 multisets",
            "égalités",
            "k = 1",
            "k = n",
            "k > n",
            "cohérence prose/code",
        ],
    },
}


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _run_regression() -> tuple[bool, str]:
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "--import-mode=importlib", "-q",
         str(REGRESSION_TESTS.relative_to(ROOT))],
        cwd=ROOT, capture_output=True, text=True,
    )
    tail = completed.stdout.strip().split("\n")[-1] if completed.stdout else ""
    return completed.returncode == 0, tail


def build(reviewer: str, root: Path = ROOT) -> dict[str, Any]:
    dispositions = yaml.safe_load(DISPOSITIONS.read_text(encoding="utf-8"))
    records = dispositions["dispositions"]
    passed, summary = _run_regression()
    regression_digest = _sha256(REGRESSION_TESTS)

    receipts: list[dict[str, Any]] = []
    for object_id, scope in sorted(SCOPE.items()):
        fingerprint = scope["fingerprint"]
        record = records.get(fingerprint)
        source = root / scope["source"]
        refus: list[str] = []
        if record is None:
            refus.append("aucune disposition ne porte cette empreinte")
        if not source.is_file():
            refus.append("source absente du dépôt")
        if not passed:
            refus.append(f"preuves de régression en échec : {summary}")
        current = _sha256(source) if source.is_file() else None
        previous = (
            "sha256:" + str(record.get("method_source_sha"))
            if record and record.get("method_source_sha") else None
        )
        if record is not None:
            meta_line = source.read_text(encoding="utf-8").split("\n", 1)[0]
            try:
                meta = json.loads(meta_line.split("% META:", 1)[1])
            except (IndexError, ValueError):
                refus.append("META illisible")
                meta = {}
            if meta.get("id") != object_id:
                refus.append(f"identifiant META {meta.get('id')} inattendu")
            if meta.get("status") != "needs_review":
                refus.append(
                    f"statut {meta.get('status')} : requalifier ne promeut rien"
                )

        receipts.append({
            "OBJECT_ID": object_id,
            "REVIEWER_IDENTITY": reviewer,
            "DECISION": DECISION,
            "CURRENT_PEDAGOGICAL_CONTENT_DIGEST": current,
            "PREVIOUS_QUALIFICATION_DIGEST": previous,
            "SCIENTIFIC_EVIDENCE_DIGEST": hashlib.sha256(
                json.dumps(scope["covered_evidence"], ensure_ascii=False,
                           sort_keys=True).encode("utf-8")
            ).hexdigest(),
            "REGRESSION_TEST_DIGEST": regression_digest,
            "fingerprint": fingerprint,
            "source": scope["source"],
            "contract": scope["contract"],
            "covered_evidence": scope["covered_evidence"],
            "scope_limit": scope.get("scope_limit"),
            "regression_summary": summary,
            "refus": sorted(set(refus)),
        })

    payload = {
        "artifact_type": "adgk_requalification_receipts",
        "schema_version": 1,
        "generated_by": "scripts/build_adgk_requalification_receipts.py",
        "approves_no_content_beyond_the_named_evidence": True,
        "promotes_no_status": True,
        "regression_tests": str(REGRESSION_TESTS.relative_to(root)),
        "regression_passed": passed,
        "receipts": receipts,
        "summary": {
            "RECEIPTS": len(receipts),
            "ELIGIBLE": sum(1 for r in receipts if not r["refus"]),
            "REFUSED": sum(1 for r in receipts if r["refus"]),
        },
    }
    payload["freshness"] = freshness.stamp(
        [scope["source"] for scope in SCOPE.values()]
        + ["tests/test_adgk_method_regression.py"],
        root=root,
    )
    return payload


def apply_requalification(payload: dict[str, Any], root: Path = ROOT) -> int:
    sys.path.insert(0, str(root / "scripts"))
    from inventory_collection import _control_digest  # noqa: PLC0415

    document = yaml.safe_load(DISPOSITIONS.read_text(encoding="utf-8"))
    records = document["dispositions"]
    applied = 0
    for receipt in payload["receipts"]:
        if receipt["refus"]:
            continue
        record = records[receipt["fingerprint"]]
        courant = receipt["CURRENT_PEDAGOGICAL_CONTENT_DIGEST"].removeprefix("sha256:")
        record["requalification"] = {
            "receipt": "audit/ADGK_REQUALIFICATION_RECEIPTS.json",
            "decision": payload["receipts"][0]["DECISION"],
            "reviewer_identity": receipt["REVIEWER_IDENTITY"],
            "previous_method_source_sha": record.get("method_source_sha"),
            "change_class": "SUBSTANTIVE_CHANGE",
            "regression_test_digest": receipt["REGRESSION_TEST_DIGEST"],
            "scientific_evidence_digest": receipt["SCIENTIFIC_EVIDENCE_DIGEST"],
        }
        record["method_source_sha"] = courant
        applied += 1

    document["control_digest"] = "sha256:" + "0" * 64
    text = yaml.safe_dump(document, allow_unicode=True, sort_keys=True, width=100)
    reparsed = yaml.safe_load(text)
    reparsed["control_digest"] = _control_digest(reparsed)
    DISPOSITIONS.write_text(
        yaml.safe_dump(reparsed, allow_unicode=True, sort_keys=True, width=100),
        encoding="utf-8",
    )
    return applied


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Receipts de requalification — ADGK",
        "",
        f"Preuves de régression : `{payload['regression_tests']}` — "
        f"{'vertes' if payload['regression_passed'] else 'EN ÉCHEC'}.",
        "",
    ]
    for receipt in payload["receipts"]:
        lines += [
            f"## `{receipt['OBJECT_ID']}`",
            "",
            f"- `REVIEWER_IDENTITY` : `{receipt['REVIEWER_IDENTITY']}`",
            f"- `CURRENT_PEDAGOGICAL_CONTENT_DIGEST` : `{receipt['CURRENT_PEDAGOGICAL_CONTENT_DIGEST']}`",
            f"- `PREVIOUS_QUALIFICATION_DIGEST` : `{receipt['PREVIOUS_QUALIFICATION_DIGEST']}`",
            f"- `SCIENTIFIC_EVIDENCE_DIGEST` : `{receipt['SCIENTIFIC_EVIDENCE_DIGEST']}`",
            f"- `REGRESSION_TEST_DIGEST` : `{receipt['REGRESSION_TEST_DIGEST']}`",
            f"- Contrat : {receipt['contract']}",
            "",
            "Preuves couvertes :",
            "",
        ]
        lines += [f"  - {e}" for e in receipt["covered_evidence"]]
        if receipt.get("scope_limit"):
            lines += ["", f"**Limite de portée.** {receipt['scope_limit']}"]
        if receipt["refus"]:
            lines += ["", f"**Refusé** : {', '.join(receipt['refus'])}"]
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved-by", required=True)
    parser.add_argument("--decision", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.decision != DECISION:
        print(f"décision non reconnue: {args.decision}")
        return 2

    payload = build(args.approved_by)
    OUTPUT_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    OUTPUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    applied = apply_requalification(payload) if args.apply else 0
    print(json.dumps({**payload["summary"], "APPLIED": applied}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
