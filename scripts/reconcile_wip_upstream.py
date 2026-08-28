#!/usr/bin/env python3
"""Reconciliation trois voies du WIP non commite face a l'amont autoritaire.

Trois etats sont compares pour chaque fichier :

BASE      version a la base commune du WIP (WIP_BASE_SHA) ;
UPSTREAM  version au dernier arbre autoritaire (UPSTREAM_SHA) ;
WIP       version locale non commitee.

Aucune regle « le plus recent gagne » n'est appliquee. La classification dit ce
que les trois etats montrent ; l'arbitrage editorial reste humain.

Pour les QCM la comparaison est semantique et non textuelle : question par
question, sur l'enonce, les options, la reponse correcte, les diagnostics et la
capacite. Deux versions qui corrigent des questions differentes ne peuvent pas
etre departagees par un diff de texte.

Ce script ne modifie aucun fichier du depot.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

GENERATED_MARKER = re.compile(r"Fichier genere par (\S+)")
GENERATED_META = re.compile(r'"genere_depuis"\s*:\s*"([^"]+)"')

CLASSIFICATIONS = (
    "GENERATED_DERIVATIVE",
    "UPSTREAM_SUPERSEDES_WIP",
    "WIP_ADDS_VALID_DELTA",
    "SEMANTICALLY_EQUIVALENT",
    "TRUE_CONFLICT",
    "WIP_OBSOLETE_OR_WRONG",
    "WIP_ONLY",
    "OTHER_EXPLICIT",
)

QCM_QUESTION_FIELDS = ("enonce", "options", "correcte", "diagnostics", "capacite")


def _git(*args: str, binary: bool = False) -> Any:
    run = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, check=False, text=not binary
    )
    return run.stdout if run.returncode == 0 else None


def blob_id(sha: str, path: str) -> str | None:
    value = _git("rev-parse", f"{sha}:{path}")
    return value.strip() if value else None


def blob_text(sha: str, path: str) -> str | None:
    return _git("show", f"{sha}:{path}")


def digest(text: str | None) -> str | None:
    if text is None:
        return None
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalise(text: str | None) -> str | None:
    """Normalisation typographique : n'efface aucune difference de fond."""

    if text is None:
        return None
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Comparaison semantique des QCM
# --------------------------------------------------------------------------


def _questions(payload: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(payload, dict):
        return {}
    return {
        str(item.get("id")): item
        for item in payload.get("questions", [])
        if isinstance(item, dict)
    }


def qcm_semantic_delta(before: str | None, after: str | None) -> dict[str, Any] | None:
    """Delta question par question entre deux versions d'un QCM canonique."""

    if before is None or after is None:
        return None
    try:
        old, new = _questions(json.loads(before)), _questions(json.loads(after))
    except json.JSONDecodeError:
        return None
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed: dict[str, list[str]] = {}
    for key in sorted(set(old) & set(new)):
        fields = [
            field_name
            for field_name in QCM_QUESTION_FIELDS
            if old[key].get(field_name) != new[key].get(field_name)
        ]
        if fields:
            changed[key] = fields
    if not (added or removed or changed):
        return None
    return {
        "questions_added": added,
        "questions_removed": removed,
        "questions_changed": changed,
        "answer_key_changed": sorted(
            key for key, fields in changed.items() if "correcte" in fields
        ),
        "diagnostics_changed": sorted(
            key for key, fields in changed.items() if "diagnostics" in fields
        ),
    }


def _disjoint(left: dict[str, Any] | None, right: dict[str, Any] | None) -> bool | None:
    """Les deux cotes touchent-ils des questions disjointes ?"""

    if left is None or right is None:
        return None
    def touched(delta: dict[str, Any]) -> set[str]:
        return (
            set(delta["questions_added"])
            | set(delta["questions_removed"])
            | set(delta["questions_changed"])
        )
    return not (touched(left) & touched(right))


# --------------------------------------------------------------------------
# Classification
# --------------------------------------------------------------------------


@dataclass
class FileVerdict:
    path: str
    base_blob: str | None
    upstream_blob: str | None
    wip_blob: str | None
    upstream_changed: bool
    wip_changed: bool
    classification: str
    rationale: str
    semantic_delta: dict[str, Any] = field(default_factory=dict)
    needs_human_editorial_decision: bool = False
    derived_from: str | None = None
    producer: str | None = None


def _generated_origin(text: str | None) -> tuple[str | None, str | None]:
    """Producteur et source canonique d'un fichier genere, s'il l'annonce."""

    if text is None:
        return None, None
    head = "\n".join(text.splitlines()[:5])
    producer = GENERATED_MARKER.search(head)
    origin = GENERATED_META.search(head)
    source = origin.group(1) if origin else None
    if source and not source.startswith("Mathematiques/"):
        source = f"Mathematiques/manuel-maths/{source}"
    return (producer.group(1) if producer else None), source


def qcm_three_way(
    base: str | None, upstream: str | None, wip: str | None
) -> dict[str, Any] | None:
    """Verdict question par question sur les trois etats."""

    if None in (base, upstream, wip):
        return None
    try:
        old = _questions(json.loads(base))
        new = _questions(json.loads(upstream))
        local = _questions(json.loads(wip))
    except json.JSONDecodeError:
        return None

    verdicts: dict[str, dict[str, Any]] = {}
    for key in sorted(set(old) | set(new) | set(local)):
        reference, ahead, here = old.get(key), new.get(key), local.get(key)
        upstream_moved = ahead != reference
        wip_moved = here != reference
        if not upstream_moved and not wip_moved:
            continue
        if upstream_moved and not wip_moved:
            verdict = "UPSTREAM_ONLY"
        elif wip_moved and not upstream_moved:
            verdict = "WIP_ONLY_CHANGE"
        elif ahead == here:
            verdict = "BOTH_CONVERGED"
        else:
            verdict = "BOTH_DIVERGED"
        fields = [
            name
            for name in QCM_QUESTION_FIELDS
            if (ahead or {}).get(name) != (here or {}).get(name)
        ]
        verdicts[key] = {
            "verdict": verdict,
            "upstream_vs_wip_differing_fields": fields,
            "answer_key_disagreement": "correcte" in fields,
        }
    counts: dict[str, int] = {}
    for entry in verdicts.values():
        counts[entry["verdict"]] = counts.get(entry["verdict"], 0) + 1
    return {
        "questions": verdicts,
        "counts": counts,
        "wip_only_changes": sorted(
            key for key, item in verdicts.items() if item["verdict"] == "WIP_ONLY_CHANGE"
        ),
        "diverged": sorted(
            key for key, item in verdicts.items() if item["verdict"] == "BOTH_DIVERGED"
        ),
        "answer_key_disagreements": sorted(
            key for key, item in verdicts.items() if item["answer_key_disagreement"]
        ),
    }


def classify_file(path: str, base_sha: str, upstream_sha: str) -> FileVerdict:
    base = blob_text(base_sha, path)
    upstream = blob_text(upstream_sha, path)
    wip_path = ROOT / path
    wip = wip_path.read_text(encoding="utf-8") if wip_path.is_file() else None

    base_n, upstream_n, wip_n = normalise(base), normalise(upstream), normalise(wip)
    upstream_changed = upstream_n != base_n
    wip_changed = wip_n != base_n

    semantic: dict[str, Any] = {}
    if path.endswith(".json") and "/qcm/" in path:
        semantic = {
            "kind": "qcm_canonical",
            "base_to_upstream": qcm_semantic_delta(base, upstream),
            "base_to_wip": qcm_semantic_delta(base, wip),
        }
        semantic["sides_touch_disjoint_questions"] = _disjoint(
            semantic["base_to_upstream"], semantic["base_to_wip"]
        )
        semantic["three_way"] = qcm_three_way(base, upstream, wip)

    producer, derived_from = _generated_origin(wip or upstream)

    if producer and derived_from:
        classification = "GENERATED_DERIVATIVE"
        rationale = (
            f"fichier genere par {producer} depuis {derived_from} ; il ne se "
            "reconcilie pas directement, il se regenere apres arbitrage de sa source"
        )
        human = False
    elif upstream is None:
        classification = "OTHER_EXPLICIT"
        rationale = "le fichier n'existe pas dans l'arbre amont"
        human = True
    elif not upstream_changed and wip_changed:
        classification = "WIP_ADDS_VALID_DELTA"
        rationale = "seul le WIP a bouge depuis la base ; l'amont n'a pas touche ce fichier"
        human = False
    elif upstream_changed and not wip_changed:
        classification = "UPSTREAM_SUPERSEDES_WIP"
        rationale = "seul l'amont a bouge depuis la base"
        human = False
    elif upstream_n == wip_n:
        classification = "SEMANTICALLY_EQUIVALENT"
        rationale = "l'amont et le WIP ont converge vers le meme contenu"
        human = False
    else:
        classification = "TRUE_CONFLICT"
        rationale = "les deux cotes ont modifie ce fichier differemment depuis la base"
        human = True
        if semantic.get("sides_touch_disjoint_questions") is True:
            rationale += (
                " ; les deux cotes touchent des questions disjointes, "
                "un report cible du delta WIP est possible sans arbitrage editorial"
            )
            human = False

    return FileVerdict(
        derived_from=derived_from,
        producer=producer,
        path=path,
        base_blob=blob_id(base_sha, path),
        upstream_blob=blob_id(upstream_sha, path),
        wip_blob=digest(wip),
        upstream_changed=upstream_changed,
        wip_changed=wip_changed,
        classification=classification,
        rationale=rationale,
        semantic_delta=semantic,
        needs_human_editorial_decision=human,
    )


def wip_paths() -> list[str]:
    listing = _git("diff", "--name-only") or ""
    return sorted(line for line in listing.splitlines() if line)


def build_report(base_sha: str, upstream_sha: str) -> dict[str, Any]:
    upstream_changed_paths = set(
        (_git("diff", "--name-only", base_sha, upstream_sha) or "").splitlines()
    )
    verdicts = [classify_file(path, base_sha, upstream_sha) for path in wip_paths()]
    for verdict in verdicts:
        if verdict.path not in upstream_changed_paths and verdict.classification == (
            "WIP_ADDS_VALID_DELTA"
        ):
            verdict.rationale += " (aucun chevauchement avec l'amont)"

    counts: dict[str, int] = {name: 0 for name in CLASSIFICATIONS}
    for verdict in verdicts:
        counts[verdict.classification] += 1

    overlap = [item for item in verdicts if item.path in upstream_changed_paths]
    return {
        "artifact_type": "wip_upstream_reconciliation",
        "schema_version": 1,
        "generated_by": "scripts/reconcile_wip_upstream.py",
        "modifies_nothing": True,
        "wip_base_sha": base_sha,
        "upstream_sha": upstream_sha,
        "wip_file_count": len(verdicts),
        "wip_overlap_with_upstream": len(overlap),
        "wip_only": len(verdicts) - len(overlap),
        "classification_counts": counts,
        "unknown": 0,
        "needs_human_editorial_decision": sum(
            1 for item in verdicts if item.needs_human_editorial_decision
        ),
        "files": [asdict(item) for item in verdicts],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="WIP_BASE_SHA")
    parser.add_argument("--upstream", required=True, help="LATEST_VALID_SIDE_CAR_HEAD")
    parser.add_argument("--out", help="ecrire le rapport JSON dans ce fichier")
    args = parser.parse_args(argv)

    report = build_report(args.base, args.upstream)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        print(
            f"{report['wip_file_count']} fichiers, "
            f"{report['wip_overlap_with_upstream']} en chevauchement, "
            f"{report['classification_counts']['TRUE_CONFLICT']} vrais conflits, "
            f"{report['needs_human_editorial_decision']} exigeant un arbitrage humain"
        )
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
