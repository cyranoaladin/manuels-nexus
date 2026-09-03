#!/usr/bin/env python3
"""Disposition des artefacts de release dont la provenance etait incomplete.

Le docket est une donnee, pas du code : il vit dans les decisions humaines
`audit/HUMAN_DECISION_*_RELEASE_ARTIFACT_DISPOSITION_*.json`. Ce producteur
n'invente aucune disposition ; il VERIFIE chaque disposition declaree contre
des preuves calculees sur le depot :

* producteur : le champ `generated_by` de l'artefact, plus toute source de
  `scripts/` qui declare litteralement ce chemin comme cible d'ecriture ;
* consommateurs : toutes les references trouvees par `git grep` sur les
  fichiers suivis, classees par role — un consommateur de release est une
  source executable (`.py` hors `tests/`, workflow CI, Makefile) qui lit
  l'artefact ; un compagnon Markdown, une trace de provenance dans un autre
  artefact et un test d'histoire ne sont pas des consommateurs de release ;
* supersession : chaque SHA d'instantane declare doit etre un ancetre de HEAD ;
* histoire : l'artefact reste suivi et son historique Git reste intact.

Metriques bloquantes : ACTIVE_RELEASE_ARTIFACTS_WITHOUT_PRODUCER et
UNKNOWN_DISPOSITIONS.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT, relative  # noqa: E402

JSON_TARGET = ROOT / "audit/RELEASE_ARTIFACT_PROVENANCE_DISPOSITION.json"
MD_TARGET = ROOT / "audit/RELEASE_ARTIFACT_PROVENANCE_DISPOSITION.md"
DOCKET_GLOB = "HUMAN_DECISION_*RELEASE_ARTIFACT_DISPOSITION*.json"
DOCKET_TYPE = "human_decision_release_artifact_disposition"

DISPOSITION_ACTIVE = "ACTIVE_RELEASE_ARTIFACT"
DISPOSITION_OBSOLETE = "HISTORICAL_OBSOLETE"
DISPOSITION_SUPERSEDED = "HISTORICAL_SUPERSEDED"
HISTORICAL = (DISPOSITION_OBSOLETE, DISPOSITION_SUPERSEDED)
KNOWN_DISPOSITIONS = (DISPOSITION_ACTIVE,) + HISTORICAL

ROLE_PRODUCER = "PRODUCER"
ROLE_RELEASE_CONSUMER = "CURRENT_RELEASE_CONSUMER"
ROLE_TEST = "HISTORICAL_TEST_CONSUMER"
ROLE_COMPANION = "MARKDOWN_COMPANION"
ROLE_PROVENANCE = "PROVENANCE_MENTION_IN_ANOTHER_ARTIFACT"
ROLE_DISPOSITION = "DISPOSITION_RECORD"
ROLE_LOG = "ARCHIVED_LOG"


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    )


def is_ancestor_of_head(sha: str) -> bool:
    return _git("merge-base", "--is-ancestor", sha, "HEAD").returncode == 0


def docket_paths() -> list[Path]:
    return sorted((ROOT / "audit").glob(DOCKET_GLOB))


def load_docket() -> tuple[list[dict[str, Any]], list[str]]:
    """Read every human disposition decision, newest file last."""

    entries: list[dict[str, Any]] = []
    sources: list[str] = []
    for path in docket_paths():
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("artifact_type") != DOCKET_TYPE:
            continue
        sources.append(relative(path))
        for entry in payload.get("artifacts", []) or []:
            entries.append({**entry, "decided_by": relative(path)})
    return entries, sources


def _classify_reference(reference: str, producer: str | None, docket: list[str]) -> str:
    if producer is not None and reference == producer:
        return ROLE_PRODUCER
    if reference in docket or reference in {relative(JSON_TARGET), relative(MD_TARGET)}:
        return ROLE_DISPOSITION
    if reference.startswith("tests/"):
        return ROLE_TEST
    if reference.endswith(".log"):
        return ROLE_LOG
    if reference.endswith(".md"):
        return ROLE_COMPANION
    if reference.endswith((".py", ".yml", ".yaml", ".toml", ".cfg", ".ini")) or (
        Path(reference).name in {"Makefile", "makefile"}
    ):
        if reference.startswith("audit/"):
            return ROLE_PROVENANCE
        return ROLE_RELEASE_CONSUMER
    return ROLE_PROVENANCE


def references_to(artifact: str, producer: str | None, docket: list[str]) -> list[dict]:
    """Every tracked file that names the artifact, with its reference role."""

    name = Path(artifact).name
    found: set[str] = set()
    for needle in (artifact, name):
        result = _git("grep", "--full-name", "-l", "-F", needle, "--", ".")
        if result.returncode not in (0, 1):
            raise RuntimeError(f"git grep a echoue pour {needle}")
        found.update(line for line in result.stdout.split("\n") if line)
    found.discard(artifact)
    return [
        {"path": path, "role": _classify_reference(path, producer, docket)}
        for path in sorted(found)
    ]


def declared_producer(artifact: str) -> dict[str, Any]:
    """Producer evidence: the artifact's own claim, then the scripts that write it."""

    path = ROOT / artifact
    claimed: str | None = None
    if path.is_file():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, dict):
            value = payload.get("generated_by")
            if isinstance(value, str) and value.strip():
                claimed = value.strip()
    write_targets: list[str] = []
    for script in sorted((ROOT / "scripts").rglob("*.py")):
        if "__pycache__" in script.parts:
            continue
        if artifact in script.read_text(encoding="utf-8", errors="replace"):
            write_targets.append(relative(script))
    resolved = None
    if claimed is not None:
        candidate = ROOT / claimed.split()[0]
        resolved = relative(candidate) if candidate.is_file() else None
    return {
        "generated_by": claimed,
        "generated_by_resolves": resolved is not None,
        "producer_path": resolved,
        "scripts_declaring_the_target": write_targets,
        "has_producer": resolved is not None or bool(write_targets),
    }


def snapshot_evidence(artifact: str, fields: list[str]) -> dict[str, Any]:
    path = ROOT / artifact
    payload: dict[str, Any] = {}
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            loaded = None
        if isinstance(loaded, dict):
            payload = loaded
    rows = []
    for field in fields:
        value = payload.get(field)
        rows.append(
            {
                "field": field,
                "sha": value if isinstance(value, str) else None,
                "is_ancestor_of_head": (
                    is_ancestor_of_head(value) if isinstance(value, str) else False
                ),
            }
        )
    return {
        "snapshot_shas": rows,
        "all_ancestors_of_head": bool(rows) and all(
            row["is_ancestor_of_head"] for row in rows
        ),
    }


def history_evidence(artifact: str) -> dict[str, Any]:
    tracked = _git("ls-files", "--error-unmatch", artifact).returncode == 0
    commits = [
        line
        for line in _git("log", "--format=%H", "--", artifact).stdout.split("\n")
        if line
    ]
    return {
        "tracked_at_head": tracked,
        "commits_touching_the_artifact": len(commits),
        "preserved_in_git_history": bool(commits),
    }


def collect_evidence(entry: dict[str, Any]) -> dict[str, Any]:
    artifact = entry["path"]
    docket = [relative(path) for path in docket_paths()]
    producer = declared_producer(artifact)
    references = references_to(artifact, producer["producer_path"], docket)
    path = ROOT / artifact
    evidence: dict[str, Any] = {
        "path": artifact,
        "exists": path.is_file(),
        "sha256": (
            hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        ),
        "producer": producer,
        "references": references,
        "reference_counts": {
            role: sum(1 for row in references if row["role"] == role)
            for role in sorted({row["role"] for row in references})
        },
        "CURRENT_RELEASE_CONSUMERS": sum(
            1 for row in references if row["role"] == ROLE_RELEASE_CONSUMER
        ),
        "history": history_evidence(artifact),
    }
    fields = entry.get("snapshot_sha_fields")
    if isinstance(fields, list) and fields:
        evidence["snapshot"] = snapshot_evidence(artifact, fields)
    return evidence


def evaluate(
    entries: list[dict[str, Any]], evidence_by_path: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Check every declared disposition against its computed evidence."""

    rows: list[dict[str, Any]] = []
    for entry in entries:
        artifact = entry["path"]
        evidence = evidence_by_path[artifact]
        disposition = entry.get("disposition")
        failures: list[str] = []
        if disposition not in KNOWN_DISPOSITIONS:
            failures.append(f"DISPOSITION_UNKNOWN:{disposition}")
        if not evidence["exists"]:
            failures.append("ARTIFACT_MISSING")
        if not evidence["history"]["preserved_in_git_history"]:
            failures.append("GIT_HISTORY_NOT_PRESERVED")

        required = entry.get("required_evidence") or {}
        for name, expected in sorted(required.items()):
            if name == "CURRENT_RELEASE_CONSUMERS":
                observed: Any = evidence["CURRENT_RELEASE_CONSUMERS"]
            elif name == "PRODUCERS":
                observed = len(evidence["producer"]["scripts_declaring_the_target"]) + (
                    1 if evidence["producer"]["generated_by_resolves"] else 0
                )
            elif name == "SNAPSHOT_SHAS_ARE_ANCESTORS_OF_HEAD":
                observed = bool(
                    evidence.get("snapshot", {}).get("all_ancestors_of_head")
                )
            elif name == "PROVENANCE":
                observed = "PASS" if evidence["producer"]["has_producer"] else "FAIL"
            else:
                observed = None
                failures.append(f"UNVERIFIABLE_REQUIREMENT:{name}")
            if observed != expected:
                failures.append(f"{name}_EXPECTED_{expected}_OBSERVED_{observed}")

        if disposition == DISPOSITION_ACTIVE and not evidence["producer"]["has_producer"]:
            failures.append("ACTIVE_WITHOUT_PRODUCER")
        if disposition in HISTORICAL and evidence["CURRENT_RELEASE_CONSUMERS"]:
            failures.append("HISTORICAL_BUT_STILL_CONSUMED")

        rows.append(
            {
                "path": artifact,
                "disposition": disposition,
                "decided_by": entry.get("decided_by"),
                "reason": entry.get("reason"),
                "required_evidence": required,
                "evidence": evidence,
                "failures": failures,
                "verdict": "CONFIRMED" if not failures else "REFUTED",
            }
        )
    rows.sort(key=lambda row: row["path"])
    return rows


def build_payload() -> dict[str, Any]:
    entries, sources = load_docket()
    evidence_by_path = {entry["path"]: collect_evidence(entry) for entry in entries}
    rows = evaluate(entries, evidence_by_path)
    active_without_producer = [
        row
        for row in rows
        if row["disposition"] == DISPOSITION_ACTIVE
        and not row["evidence"]["producer"]["has_producer"]
    ]
    unknown = [row for row in rows if row["disposition"] not in KNOWN_DISPOSITIONS]
    refuted = [row for row in rows if row["verdict"] == "REFUTED"]
    preflight = [
        row
        for row in rows
        if row["disposition"] == DISPOSITION_ACTIVE
        and row["evidence"]["producer"]["has_producer"]
    ]
    return {
        "schema_version": 1,
        "artifact_name": "RELEASE_ARTIFACT_PROVENANCE_DISPOSITION",
        "generated_by": "scripts/build_release_artifact_provenance_disposition.py",
        "ancestry_evaluated_against": "HEAD",
        "scope": (
            "les artefacts inscrits au docket de disposition par une decision "
            "humaine ; ce ledger verifie chaque disposition declaree, il n'en "
            "decide aucune"
        ),
        "docket_sources": sources,
        "summary": {
            "DOCKETED_ARTIFACTS": len(rows),
            "ACTIVE_RELEASE_ARTIFACTS_WITHOUT_PRODUCER": len(active_without_producer),
            "UNKNOWN_DISPOSITIONS": len(unknown),
            "REFUTED_DISPOSITIONS": len(refuted),
            "CURRENT_PREFLIGHT_PROVENANCE": "PASS" if preflight and not refuted else "FAIL",
            "DISPOSITIONS": {
                row["path"]: row["disposition"] for row in rows
            },
            "CURRENT_RELEASE_CONSUMERS": {
                row["path"]: row["evidence"]["CURRENT_RELEASE_CONSUMERS"]
                for row in rows
            },
            "GATE": "PASS"
            if not refuted and not active_without_producer and not unknown
            else "FAIL",
        },
        "artifacts": rows,
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Disposition des artefacts de release sans provenance complete",
        "",
        f"Genere par `{payload['generated_by']}`. Ancestralite evaluee "
        f"contre `{payload['ancestry_evaluated_against']}`.",
        "",
        "| METRIC_NAME | VALEUR |",
        "| --- | --- |",
        f"| DOCKETED_ARTIFACTS | {summary['DOCKETED_ARTIFACTS']} |",
        "| ACTIVE_RELEASE_ARTIFACTS_WITHOUT_PRODUCER | "
        f"{summary['ACTIVE_RELEASE_ARTIFACTS_WITHOUT_PRODUCER']} |",
        f"| UNKNOWN_DISPOSITIONS | {summary['UNKNOWN_DISPOSITIONS']} |",
        f"| REFUTED_DISPOSITIONS | {summary['REFUTED_DISPOSITIONS']} |",
        "| CURRENT_PREFLIGHT_PROVENANCE | "
        f"{summary['CURRENT_PREFLIGHT_PROVENANCE']} |",
        f"| GATE | {summary['GATE']} |",
        "",
        "## Artefacts",
        "",
        "| ARTEFACT | DISPOSITION | PRODUCTEUR | CURRENT_RELEASE_CONSUMERS | VERDICT |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["artifacts"]:
        producer = row["evidence"]["producer"]["producer_path"] or "aucun"
        lines.append(
            f"| `{row['path']}` | {row['disposition']} | `{producer}` | "
            f"{row['evidence']['CURRENT_RELEASE_CONSUMERS']} | {row['verdict']} |"
        )
    lines.append("")
    for row in payload["artifacts"]:
        lines.extend(
            [
                f"### `{row['path']}`",
                "",
                f"- disposition : **{row['disposition']}** "
                f"(decidee dans `{row['decided_by']}`)",
                f"- motif : {row['reason']}",
                f"- sha256 : `{row['evidence']['sha256']}`",
                "- conserve dans l'histoire Git : "
                f"{row['evidence']['history']['commits_touching_the_artifact']} commits, "
                "toujours suivi"
                if row["evidence"]["history"]["tracked_at_head"]
                else "- non suivi a HEAD",
                "",
                "| REFERENCE | ROLE |",
                "| --- | --- |",
            ]
        )
        for reference in row["evidence"]["references"]:
            lines.append(f"| `{reference['path']}` | {reference['role']} |")
        if not row["evidence"]["references"]:
            lines.append("| _aucune_ | — |")
        snapshot = row["evidence"].get("snapshot")
        if snapshot:
            lines.extend(
                [
                    "",
                    "| SHA D'INSTANTANE | CHAMP | ANCETRE DE HEAD |",
                    "| --- | --- | --- |",
                ]
            )
            for entry in snapshot["snapshot_shas"]:
                lines.append(
                    f"| `{entry['sha']}` | `{entry['field']}` | "
                    f"{'oui' if entry['is_ancestor_of_head'] else 'non'} |"
                )
        if row["failures"]:
            lines.extend(["", "Echecs :", ""])
            lines.extend(f"- `{failure}`" for failure in row["failures"])
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build_payload()
    expected = {JSON_TARGET: render_json(payload), MD_TARGET: render_markdown(payload)}
    if args.check:
        stale = [
            path
            for path, content in expected.items()
            if not path.exists() or path.read_text(encoding="utf-8") != content
        ]
        for path in stale:
            print(f"STALE_OR_MISSING: {relative(path)}")
        if stale:
            return 1
        summary = payload["summary"]
        print(
            "ACTIVE_RELEASE_ARTIFACTS_WITHOUT_PRODUCER="
            f"{summary['ACTIVE_RELEASE_ARTIFACTS_WITHOUT_PRODUCER']} "
            f"UNKNOWN_DISPOSITIONS={summary['UNKNOWN_DISPOSITIONS']} "
            f"REFUTED_DISPOSITIONS={summary['REFUTED_DISPOSITIONS']}"
        )
        return 0 if summary["GATE"] == "PASS" else 1
    for path, content in expected.items():
        path.write_text(content, encoding="utf-8")
        print(f"wrote {relative(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
