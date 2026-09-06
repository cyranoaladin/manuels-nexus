#!/usr/bin/env python3
"""Forensique des qualifications dérivées devenues invalides.

Le gate signale `qualification_invalide` pour chaque qualification humaine
dérivée dont la source a bougé depuis la qualification. Réécrire les SHA
attendus ferait disparaître le symptôme sans rien prouver. Ce producteur
reconstitue, pour chaque qualification, ce qui a *réellement* changé.

Méthode : on retrouve dans l'historique git le blob dont le sha256 est
exactement le `method_source_sha` enregistré — c'est la version que l'humain a
qualifiée — puis on compare son corps (hors ligne `% META:`) au corps courant.

Trois classes (§8) :

* `GOVERNANCE_METADATA_ONLY_CHANGE` — corps identique, seule la ligne META a
  bougé. La qualification peut être rebasée si le protocole lie la
  qualification à une empreinte sémantique.
* `DIACRITICS_ONLY_CHANGE`          — corps identique une fois les signes
  diacritiques repliés : campagne éditoriale d'accentuation, sans effet
  sémantique. Même traitement, sous la même condition.
* `PEDAGOGICAL_CONTENT_CHANGE`      — le corps a réellement changé. La
  qualification est stale ; l'objet doit être réaudité.
* `UNKNOWN_CHANGE`                  — la version qualifiée est introuvable
  dans l'historique. Bloquant.

Aucune re-revue n'est fabriquée ici : ce producteur classe, il n'approuve rien.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DISPOSITIONS = ROOT / "audit/ANOMALY_DISPOSITIONS.yaml"
OUTPUT_JSON = ROOT / "audit/QUALIFICATION_STALENESS_FORENSICS.json"
OUTPUT_MD = ROOT / "audit/QUALIFICATION_STALENESS_FORENSICS.md"

TRACKED_DECISIONS = ("A4_METHOD_REVIEW_DEBT", "OPTIONAL_EXTENSION")


def _deaccent(text: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFD", text) if not unicodedata.combining(ch)
    )


def _body(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].startswith("% META:"):
        return "\n".join(lines[1:])
    return text


def _find_qualified_blob(source: str, expected_sha: str) -> tuple[str | None, bytes | None]:
    """Commit et contenu de la version que l'humain a effectivement qualifiée."""
    revisions = subprocess.run(
        ["git", "log", "--format=%H", "--", source],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split()
    for revision in revisions:
        blob = subprocess.run(
            ["git", "show", f"{revision}:{source}"], cwd=ROOT, capture_output=True
        )
        if blob.returncode == 0 and hashlib.sha256(blob.stdout).hexdigest() == expected_sha:
            return revision, blob.stdout
    return None, None


def _classify(qualified_body: str, current_body: str) -> str:
    if qualified_body == current_body:
        return "GOVERNANCE_METADATA_ONLY_CHANGE"
    if _deaccent(qualified_body) == _deaccent(current_body):
        return "DIACRITICS_ONLY_CHANGE"
    return "PEDAGOGICAL_CONTENT_CHANGE"


def _semantic_diff(qualified_body: str, current_body: str, limit: int = 40) -> list[str]:
    """Diff insensible aux diacritiques : ne montre que ce qui change vraiment."""
    diff = difflib.unified_diff(
        _deaccent(qualified_body).splitlines(),
        _deaccent(current_body).splitlines(),
        lineterm="", n=0,
    )
    return [line for line in list(diff)[2:]][:limit]


def build() -> dict[str, Any]:
    payload = yaml.safe_load(DISPOSITIONS.read_text(encoding="utf-8")) or {}
    dispositions = payload.get("dispositions") or {}

    records: list[dict[str, Any]] = []
    for fingerprint, record in sorted(dispositions.items()):
        if not isinstance(record, dict):
            continue
        decision_ref = str(record.get("decision_ref", ""))
        if not any(token in decision_ref for token in TRACKED_DECISIONS):
            continue
        source = str(record.get("source", ""))
        expected_sha = str(record.get("method_source_sha", ""))
        source_path = ROOT / source
        if not source_path.is_file():
            records.append({
                "fingerprint": str(fingerprint),
                "source": source,
                "classification": "UNKNOWN_CHANGE",
                "detail": "source introuvable",
            })
            continue

        current_bytes = source_path.read_bytes()
        current_sha = hashlib.sha256(current_bytes).hexdigest()
        if current_sha == expected_sha:
            continue  # qualification fraîche : rien à expliquer

        revision, qualified_bytes = _find_qualified_blob(source, expected_sha)
        if revision is None:
            records.append({
                "fingerprint": str(fingerprint),
                "source": source,
                "decision_ref": decision_ref,
                "qualified_source_sha": expected_sha,
                "current_source_sha": current_sha,
                "classification": "UNKNOWN_CHANGE",
                "detail": "version qualifiée absente de l'historique git",
            })
            continue

        qualified_body = _body(qualified_bytes.decode("utf-8", "replace"))
        current_body = _body(current_bytes.decode("utf-8", "replace"))
        classification = _classify(qualified_body, current_body)

        entry: dict[str, Any] = {
            "fingerprint": str(fingerprint),
            "source": source,
            "decision_ref": decision_ref,
            "qualified_source_sha": expected_sha,
            "current_source_sha": current_sha,
            "qualified_at_commit": revision,
            "raw_bytes_changed": True,
            "classification": classification,
            "requires_re_audit": classification in {
                "PEDAGOGICAL_CONTENT_CHANGE", "UNKNOWN_CHANGE",
            },
        }
        if classification == "PEDAGOGICAL_CONTENT_CHANGE":
            entry["semantic_diff"] = _semantic_diff(qualified_body, current_body)
        records.append(entry)

    counts = Counter(record["classification"] for record in records)
    summary = {
        "QUALIFICATIONS_ANALYZED": len(records),
        "GOVERNANCE_METADATA_ONLY_CHANGE": counts.get("GOVERNANCE_METADATA_ONLY_CHANGE", 0),
        "DIACRITICS_ONLY_CHANGE": counts.get("DIACRITICS_ONLY_CHANGE", 0),
        "PEDAGOGICAL_CONTENT_CHANGE": counts.get("PEDAGOGICAL_CONTENT_CHANGE", 0),
        "QUALIFICATION_INVALID_UNKNOWN": counts.get("UNKNOWN_CHANGE", 0),
        "REQUIRES_RE_AUDIT": sum(1 for r in records if r.get("requires_re_audit")),
        "APPROVES_NOTHING": True,
    }
    return {
        "artifact_type": "qualification_staleness_forensics",
        "schema_version": 1,
        "generated_by": "scripts/build_qualification_staleness_forensics.py",
        "summary": summary,
        "records": records,
    }


def render_md(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Forensique des qualifications invalidées",
        "",
        "Chaque qualification est comparée à la version que l'humain a réellement",
        "qualifiée, retrouvée dans l'historique git par son sha256.",
        "",
        f"- Qualifications analysées : `{s['QUALIFICATIONS_ANALYZED']}`",
        f"- Changement de métadonnée seule : `{s['GOVERNANCE_METADATA_ONLY_CHANGE']}`",
        f"- Changement diacritique seul : `{s['DIACRITICS_ONLY_CHANGE']}`",
        f"- Changement pédagogique réel : `{s['PEDAGOGICAL_CONTENT_CHANGE']}`",
        f"- `QUALIFICATION_INVALID_UNKNOWN` : `{s['QUALIFICATION_INVALID_UNKNOWN']}`",
        f"- À réauditer : `{s['REQUIRES_RE_AUDIT']}`",
        "",
        "## Objets exigeant une vraie réaudition",
        "",
        "| Empreinte | Source | Qualifiée au commit |",
        "|---|---|---|",
    ]
    for record in payload["records"]:
        if record.get("requires_re_audit"):
            lines.append(
                f"| `{record['fingerprint']}` | `{record['source']}` | "
                f"`{str(record.get('qualified_at_commit', ''))[:12]}` |"
            )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = build()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if OUTPUT_JSON.is_file() and OUTPUT_JSON.read_text(encoding="utf-8") == rendered:
            print("QUALIFICATION_STALENESS_FORENSICS check: OK")
            return 0
        print("QUALIFICATION_STALENESS_FORENSICS check: STALE")
        return 1

    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
