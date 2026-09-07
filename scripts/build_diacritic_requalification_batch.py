#!/usr/bin/env python3
"""Émet le receipt batch des re-liaisons diacritiques et les applique.

Il ne s'exécute pas par accident : `--approved-by` et `--decision` sont
obligatoires, et la décision doit être exactement celle que le Release Owner a
rendue. Sans `--apply`, rien n'est écrit dans les dispositions.

CE QU'IL VÉRIFIE AVANT D'ÉCRIRE, POUR CHAQUE QUALIFICATION.

  * la file de requalification la déclare périmée ;
  * la version qualifiée est retrouvable dans l'historique par son empreinte ;
  * dépouillées de leurs accents, les deux versions sont identiques au bit
    près — recalculé ici, jamais lu depuis un rapport ;
  * la fiche porte toujours `status: needs_review` : re-lier ne promeut rien ;
  * le packet de revue est intact.

Une seule de ces conditions qui manque, et l'objet sort du lot. Le lot n'est
pas « les 86 » : c'est « ce qui passe les cinq contrôles », et le compte est
constaté après coup.
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

import diacritic_requalification as req  # noqa: E402
import evidence_freshness as freshness  # noqa: E402

DISPOSITIONS = ROOT / "audit/ANOMALY_DISPOSITIONS.yaml"

#: Seule classe de qualifications que la décision batch peut re-lier.
#:
#: La décision du Release Owner autorise la re-liaison des qualifications dont
#: le changement est prouvé diacritique. Trois des qualifications qui
#: remplissent cette condition sont pourtant gouvernées par une décision
#: humaine ANTÉRIEURE et NOMINATIVE — celle du 2026-08-23 sur les extensions
#: facultatives de 1SPE-TRIGONOMETRIE — qui stipule explicitement
#: `invalidate_on_source_change: true`. Les re-lier reviendrait à défaire une
#: décision humaine par une autre, en silence.
#:
#: Le lot ne couvre donc que la décision de classe A4. Les trois autres sont
#: exclues avec leur motif, et remontent au Release Owner.
A4_DECISION_REF = (
    "audit/A4_METHOD_REVIEW_DEBT_POLICY.md"
    "#decision-a4-method-review-debt-2026-08-19"
)
QUEUE = ROOT / "audit/METHOD_REQUALIFICATION_QUEUE.json"
OUTPUT_JSON = ROOT / "audit/DIACRITIC_REQUALIFICATION_BATCH_RECEIPT.json"
OUTPUT_MD = ROOT / "audit/DIACRITIC_REQUALIFICATION_BATCH_RECEIPT.md"


def _blob_with_digest(relative: str, digest: str) -> str | None:
    revisions = subprocess.run(
        ["git", "log", "--all", "--format=%H", "--", relative],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split()
    for revision in revisions:
        blob = subprocess.run(
            ["git", "show", f"{revision}:{relative}"], cwd=ROOT,
            capture_output=True,
        )
        if blob.returncode:
            continue
        text = blob.stdout.decode("utf-8")
        if hashlib.sha256(text.encode("utf-8")).hexdigest() == digest:
            return text
    return None


def assess(root: Path = ROOT) -> dict[str, Any]:
    """Trie les qualifications périmées : couvertes, exclues, et pourquoi."""
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    dispositions = yaml.safe_load(DISPOSITIONS.read_text(encoding="utf-8"))
    records = dispositions["dispositions"]

    covered: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []

    for item in queue["items"]:
        fingerprint = str(item["fingerprint"])
        relative = str(item["source"])
        record = records.get(fingerprint)
        refus: list[str] = []

        if record is None:
            refus.append("aucune disposition ne porte cette empreinte")
        elif record.get("decision_ref") != A4_DECISION_REF:
            refus.append(
                "gouvernée par une autre décision humaine : "
                f"{record.get('decision_ref')}"
            )
        if item.get("state") != "STALE":
            refus.append(f"état {item.get('state')} au lieu de STALE")

        path = root / relative
        current = path.read_text(encoding="utf-8") if path.is_file() else None
        if current is None:
            refus.append("source absente du dépôt")

        before = _blob_with_digest(relative, str(item["qualified_source_sha"]))
        if before is None:
            refus.append("version qualifiée introuvable dans l'historique")

        change_class = None
        if before is not None and current is not None:
            change_class = req.recompute_change_class(before, current)
            if change_class != req.ACCENT_ONLY:
                refus.append(f"changement {change_class}, hors du périmètre")

        if current is not None:
            try:
                meta = json.loads(current.split("\n", 1)[0].split("% META:", 1)[1])
            except (IndexError, ValueError):
                refus.append("META illisible")
                meta = {}
            if meta.get("status") != "needs_review":
                refus.append(
                    f"statut {meta.get('status')} : re-lier ne promeut rien"
                )

        if record is not None:
            packet = record.get("review_packet")
            packet_sha = record.get("review_packet_sha")
            packet_path = root / str(packet) if packet else None
            if not packet or not packet_sha or not packet_path.is_file():
                refus.append("packet de revue absent")
            elif hashlib.sha256(packet_path.read_bytes()).hexdigest() != packet_sha:
                refus.append("packet de revue modifié après qualification")

        entry = {
            "fingerprint": fingerprint,
            "source": relative,
            "manual": item.get("manual"),
            "chapter": item.get("chapter"),
            "previous_method_source_sha": item.get("qualified_source_sha"),
            "current_method_source_sha": item.get("current_source_sha"),
            "recomputed_change_class": change_class,
        }
        if refus:
            entry["refus"] = sorted(set(refus))
            excluded.append(entry)
        else:
            covered.append(entry)

    covered.sort(key=lambda e: e["fingerprint"])
    excluded.sort(key=lambda e: e["fingerprint"])
    return {"covered": covered, "excluded": excluded}


def build_receipt(reviewer: str, decision: str, root: Path = ROOT) -> dict[str, Any]:
    verdict = assess(root)
    covered = verdict["covered"]
    identifiers = [e["fingerprint"] for e in covered]

    receipt = {
        "artifact_type": "diacritic_requalification_batch_receipt",
        "schema_version": 1,
        "generated_by": "scripts/build_diacritic_requalification_batch.py",
        "approves_no_content": True,
        "promotes_no_status": True,
        "REVIEWER_IDENTITY": reviewer,
        "DECISION": decision,
        "QUALIFICATION_COUNT": len(covered),
        "QUALIFICATION_IDS_DIGEST": req.identifiers_digest(identifiers),
        "OLD_PEDAGOGICAL_DIGESTS_DIGEST": req.identifiers_digest(
            e["previous_method_source_sha"] for e in covered
        ),
        "NEW_PEDAGOGICAL_DIGESTS_DIGEST": req.identifiers_digest(
            e["current_method_source_sha"] for e in covered
        ),
        "DIACRITIC_FORENSICS_EVIDENCE_DIGEST": req.payload_digest(covered),
        "scope": (
            "Re-liaison d'une qualification existante au texte courant, "
            "lorsque le seul changement est diacritique. N'approuve aucun "
            "contenu et ne promeut aucun statut : les objets restent "
            "`needs_review` et comptent toujours comme dette de revue."
        ),
        "qualification_ids": identifiers,
        "covered": covered,
        "excluded": verdict["excluded"],
    }
    receipt["freshness"] = freshness.stamp(
        ["audit/METHOD_REQUALIFICATION_QUEUE.json",
         "audit/ANOMALY_DISPOSITIONS.yaml"],
        root=root,
    )
    return receipt


def apply_requalification(receipt: dict[str, Any], root: Path = ROOT) -> int:
    """Réécrit `method_source_sha` pour les seules qualifications couvertes."""
    sys.path.insert(0, str(root / "scripts"))
    from inventory_collection import _control_digest  # noqa: PLC0415

    document = yaml.safe_load(DISPOSITIONS.read_text(encoding="utf-8"))
    records = document["dispositions"]
    applied = 0
    for entry in receipt["covered"]:
        fingerprint = entry["fingerprint"]
        if not req.covered_by(receipt, fingerprint):
            raise ValueError(f"empreinte hors du lot: {fingerprint}")
        record = records[fingerprint]
        record["method_source_sha"] = entry["current_method_source_sha"]
        record["requalification"] = {
            "receipt": "audit/DIACRITIC_REQUALIFICATION_BATCH_RECEIPT.json",
            "decision": receipt["DECISION"],
            "reviewer_identity": receipt["REVIEWER_IDENTITY"],
            "previous_method_source_sha": entry["previous_method_source_sha"],
            "change_class": req.ACCENT_ONLY,
        }
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


def render_markdown(receipt: dict[str, Any]) -> str:
    lines = [
        "# Receipt batch — re-liaison diacritique",
        "",
        f"- `REVIEWER_IDENTITY` : `{receipt['REVIEWER_IDENTITY']}`",
        f"- `DECISION` : `{receipt['DECISION']}`",
        f"- `QUALIFICATION_COUNT` : `{receipt['QUALIFICATION_COUNT']}`",
        f"- `QUALIFICATION_IDS_DIGEST` : `{receipt['QUALIFICATION_IDS_DIGEST']}`",
        f"- `OLD_PEDAGOGICAL_DIGESTS_DIGEST` : `{receipt['OLD_PEDAGOGICAL_DIGESTS_DIGEST']}`",
        f"- `NEW_PEDAGOGICAL_DIGESTS_DIGEST` : `{receipt['NEW_PEDAGOGICAL_DIGESTS_DIGEST']}`",
        f"- `DIACRITIC_FORENSICS_EVIDENCE_DIGEST` : `{receipt['DIACRITIC_FORENSICS_EVIDENCE_DIGEST']}`",
        "",
        receipt["scope"],
        "",
        f"## Qualifications couvertes ({len(receipt['covered'])})",
        "",
        "| Empreinte | Manuel | Chapitre | Source |",
        "|---|---|---|---|",
    ]
    for entry in receipt["covered"]:
        lines.append(
            f"| `{entry['fingerprint']}` | {entry['manual']} | "
            f"{entry['chapter']} | `{entry['source']}` |"
        )
    lines += ["", f"## Exclues ({len(receipt['excluded'])})", ""]
    for entry in receipt["excluded"]:
        lines.append(
            f"- `{entry['fingerprint']}` — `{entry['source']}` : "
            f"{', '.join(entry['refus'])}"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved-by", required=True)
    parser.add_argument("--decision", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if args.decision != req.DECISION:
        print(f"décision non reconnue: {args.decision}")
        return 2

    receipt = build_receipt(args.approved_by, args.decision)
    OUTPUT_JSON.write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    OUTPUT_MD.write_text(render_markdown(receipt), encoding="utf-8")

    applied = apply_requalification(receipt) if args.apply else 0
    print(json.dumps({
        "QUALIFICATION_COUNT": receipt["QUALIFICATION_COUNT"],
        "EXCLUDED": len(receipt["excluded"]),
        "APPLIED": applied,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
