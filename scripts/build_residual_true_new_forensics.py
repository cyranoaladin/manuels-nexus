#!/usr/bin/env python3
"""Build the residual TRUE_NEW ledger without touching anomaly governance.

The builder is deliberately downstream-only: it reads the frozen initial
forensics and the current canonical inventory, then projects the still-open
review debt.  It never updates the inventory, manifest, baseline, policy or
oracle.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
INITIAL_JSON_REL = Path("audit/TRUE_NEW_18_FORENSICS.json")
INITIAL_MD_REL = Path("audit/TRUE_NEW_18_FORENSICS.md")
INVENTORY_REL = Path("audit/INVENTAIRE_COLLECTION.json")

FROZEN_SHA256 = {
    INITIAL_JSON_REL: "2b5b752530feae760ac687781133e0b6dbf21757e39b7f79c8025cee00c3a460",
    INITIAL_MD_REL: "e94a464d5f0ad12b8f6fe7ecb75449619670baa675b037426d8562ca8cb5d977",
}
X3_FINGERPRINT = "65b5b9f56ca8900a"
X3_ID = "1SPE-VARALEA-CR-X3"
X3_PATH = (
    "Mathematiques/manuel-maths/chapitres/"
    "1SPE-VARIABLES-ALEATOIRES/cours/13_X3_variance_affine.tex"
)

OUTPUT_NAMES = {
    "residual_forensics": {
        "json": "RESIDUAL_TRUE_NEW_FORENSICS.json",
        "md": "RESIDUAL_TRUE_NEW_FORENSICS.md",
    },
    "residual_algebra": {
        "json": "CURRENT_ANOMALY_SET_ALGEBRA_RESIDUAL.json",
        "md": "CURRENT_ANOMALY_SET_ALGEBRA_RESIDUAL.md",
    },
}

COUNTS = {
    "TRUE_NEW_INITIAL": 18,
    "ACTIVE_FINGERPRINTS_CLOSED": 0,
    "REMOVED": 0,
    "REVIEW_CLOSED": 0,
    "CONTENT_FINDINGS_FIXED": 8,
    "NEW_AFTER_TRIAGE": 1,
    "RESIDUAL_TRUE_NEW": 19,
}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _source_sha(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"source résiduelle absente: {path}")
    return f"sha256:{_sha256_bytes(path.read_bytes())}"


def _git_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    head = result.stdout.strip()
    if len(head) != 40 or any(character not in "0123456789abcdef" for character in head):
        raise ValueError(f"SHA Git forensique invalide: {head!r}")
    return head


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"JSON illisible: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"racine JSON non objet: {path}")
    return value


def _validate_frozen_inputs(root: Path) -> tuple[Path, Path]:
    paths = (root / INITIAL_JSON_REL, root / INITIAL_MD_REL)
    for path in paths:
        expected = FROZEN_SHA256[path.relative_to(root)]
        try:
            observed = _sha256_bytes(path.read_bytes())
        except OSError as exc:
            raise ValueError(f"artefact initial figé illisible: {path}") from exc
        if observed != expected:
            raise ValueError(
                "artefact initial figé modifié: "
                f"{path.relative_to(root)} attendu={expected} observé={observed}"
            )
    return paths


def _active_unqualified(qualifications: Mapping[str, Any]) -> set[str]:
    return {
        str(fingerprint)
        for fingerprint, qualification in qualifications.items()
        if isinstance(qualification, Mapping)
        and qualification.get("qualified") is False
        and qualification.get("disposition") == "open_debt"
    }


def _current_anomaly(
    inventory: Mapping[str, Any],
    *,
    category: str,
    path: str,
) -> Mapping[str, Any]:
    anomalies = inventory.get("anomalies")
    if not isinstance(anomalies, Mapping):
        raise ValueError("inventaire sans anomalies")
    values = anomalies.get(category)
    if not isinstance(values, list):
        raise ValueError(f"catégorie d'anomalie absente: {category}")
    matches = [
        item
        for item in values
        if isinstance(item, Mapping) and item.get("path") == path
    ]
    if len(matches) != 1:
        raise ValueError(
            f"anomalie courante non univoque: {category} {path} ({len(matches)})"
        )
    return matches[0]


def _initial_entry(
    *,
    root: Path,
    entry: Mapping[str, Any],
    inventory: Mapping[str, Any],
) -> dict[str, Any]:
    fingerprint = str(entry["fingerprint"])
    category = str(entry["anomaly_category"])
    path = str(entry["path"])
    anomaly = _current_anomaly(inventory, category=category, path=path)
    qualification = inventory["anomaly_qualifications"][fingerprint]
    current_sha = _source_sha(root / path)
    content_fixed = (
        entry.get("triage_class") == "FIX_NOW"
        and current_sha != entry.get("source_sha")
    )
    if entry.get("triage_class") == "FIX_NOW" and not content_fixed:
        raise ValueError(
            f"finding FIX_NOW sans correction source prouvée: {fingerprint}"
        )

    if content_fixed:
        why_legitimate = (
            "Le finding de contenu initial est corrigé dans la source courante; "
            "le fingerprint subsiste légitimement comme dette de revue du statut source."
        )
    else:
        why_legitimate = (
            "Le triage initial prouve une dette de revue éditoriale ou humaine "
            "légitime, toujours portée par le statut source courant."
        )

    return {
        "fingerprint": fingerprint,
        "object_id": str(entry["object_id"]),
        "path": path,
        "category": category,
        "manual": str(entry["manual"]),
        "chapter": str(entry["chapter"]),
        "object_type": str(entry["object_type"]),
        "source_status": str(anomaly.get("status", entry.get("status", ""))),
        "source_sha": current_sha,
        "initial_source_sha": str(entry["source_sha"]),
        "content_finding_fixed": content_fixed,
        "reason_created": str(entry["reason_created"]),
        "original_triage_class": str(entry["triage_class"]),
        "triage_class": "LEGITIMATE_REVIEW_DEBT",
        "why_legitimate": why_legitimate,
        "why_cannot_close": (
            "Aucune revue ou qualification courante ne clôt ce fingerprint: "
            f"disposition={qualification['disposition']}, "
            f"qualified={str(qualification['qualified']).lower()}."
        ),
        "current_review_state": "PENDING_UNQUALIFIED",
        "owner": str(entry["owner"]),
        "closure_phase": str(entry["intended_closure_phase"]),
        "release_acceptance": False,
    }


def _x3_entry(*, root: Path, inventory: Mapping[str, Any]) -> dict[str, Any]:
    anomaly = _current_anomaly(
        inventory,
        category="blocking_statuses",
        path=X3_PATH,
    )
    if anomaly.get("id") != X3_ID or anomaly.get("status") != "generated":
        raise ValueError("identité/statut courant X3 inattendu")
    qualification = inventory["anomaly_qualifications"][X3_FINGERPRINT]
    return {
        "fingerprint": X3_FINGERPRINT,
        "object_id": X3_ID,
        "path": X3_PATH,
        "category": "blocking_statuses",
        "manual": "1SPE",
        "chapter": "1SPE-VARIABLES-ALEATOIRES",
        "object_type": "cours",
        "source_status": "generated",
        "source_sha": _source_sha(root / X3_PATH),
        "initial_source_sha": None,
        "content_finding_fixed": False,
        "reason_created": "OTHER_PROVED_EDITORIAL_NEED",
        "original_triage_class": "NEW_AFTER_TRIAGE",
        "triage_class": "LEGITIMATE_REVIEW_DEBT",
        "why_legitimate": (
            "L'extension correcte sur la variance affine est conservée hors socle "
            "avec un besoin éditorial prouvé et un étiquetage explicite."
        ),
        "why_cannot_close": (
            "La source X3 reste generated et aucune revue ou qualification courante "
            "ne la clôt: "
            f"disposition={qualification['disposition']}, "
            f"qualified={str(qualification['qualified']).lower()}."
        ),
        "current_review_state": "PENDING_UNQUALIFIED",
        "owner": "direction_scientifique_programme",
        "closure_phase": "PROGRAM_SCIENTIFIC_PEDAGOGICAL_REVIEW",
        "release_acceptance": False,
    }


def build_reports(
    root: Path = ROOT,
    *,
    inventory_path: Path | None = None,
) -> dict[str, dict[str, Any]]:
    """Return both deterministic residual reports without writing files."""

    root = root.resolve()
    initial_json_path, initial_md_path = _validate_frozen_inputs(root)
    inventory_path = (
        inventory_path.resolve()
        if inventory_path is not None
        else root / INVENTORY_REL
    )
    initial = _read_json(initial_json_path)
    inventory = _read_json(inventory_path)

    initial_entries = initial.get("entries")
    if not isinstance(initial_entries, list) or len(initial_entries) != 18:
        raise ValueError("le ledger initial doit contenir exactement 18 lignes")
    initial_fingerprints = {
        str(entry.get("fingerprint"))
        for entry in initial_entries
        if isinstance(entry, Mapping)
    }
    if len(initial_fingerprints) != 18 or initial.get("true_new_initial") != 18:
        raise ValueError("les 18 fingerprints initiaux ne sont pas univoques")
    if initial.get("counts") != {
        "FIX_NOW": 8,
        "LEGITIMATE_REVIEW_DEBT": 10,
        "SHOULD_NOT_EXIST": 0,
    }:
        raise ValueError("triage initial 8/10/0 inattendu")

    qualifications = inventory.get("anomaly_qualifications")
    if not isinstance(qualifications, Mapping):
        raise ValueError("inventaire sans qualifications d'anomalies")
    active_unqualified = _active_unqualified(qualifications)
    expected = initial_fingerprints | {X3_FINGERPRINT}
    if active_unqualified != expected:
        missing_set = expected - active_unqualified
        extra_set = active_unqualified - expected
        missing = sorted(missing_set)
        extra = sorted(extra_set)
        if missing_set & initial_fingerprints:
            raise ValueError(
                "les 18 fingerprints initiaux doivent rester actifs non qualifiés: "
                f"absents={missing}"
            )
        raise ValueError(
            "ensemble actif non qualifié inattendu: "
            f"absents={missing} supplémentaires={extra}"
        )

    entries = [
        _initial_entry(root=root, entry=entry, inventory=inventory)
        for entry in initial_entries
    ]
    entries.append(_x3_entry(root=root, inventory=inventory))
    entries.sort(key=lambda entry: entry["fingerprint"])
    if sum(bool(entry["content_finding_fixed"]) for entry in entries) != 8:
        raise ValueError("CONTENT_FINDINGS_FIXED doit valoir exactement 8")

    initial_bytes = initial_json_path.read_bytes()
    inventory_bytes = inventory_path.read_bytes()
    input_digest = "sha256:" + _sha256_bytes(
        initial_bytes + b"\0" + initial_md_path.read_bytes() + b"\0" + inventory_bytes
    )
    forensic_source_sha = _git_head(root)
    evidence = {
        "frozen_initial_json": str(INITIAL_JSON_REL),
        "frozen_initial_json_sha256": "sha256:" + FROZEN_SHA256[INITIAL_JSON_REL],
        "frozen_initial_md": str(INITIAL_MD_REL),
        "frozen_initial_md_sha256": "sha256:" + FROZEN_SHA256[INITIAL_MD_REL],
        "inventory": str(inventory_path.relative_to(root))
        if inventory_path.is_relative_to(root)
        else str(inventory_path),
        "inventory_sha256": "sha256:" + _sha256_bytes(inventory_bytes),
        "inventory_source_digest": inventory.get("source_digest"),
        "input_digest": input_digest,
    }
    residual_set = [entry["fingerprint"] for entry in entries]
    residual_forensics = {
        "schema_version": 1,
        "artifact_type": "residual_true_new_forensics",
        "baseline_modified": False,
        "policy_modified": False,
        "release_acceptance": False,
        "forensic_source_sha": forensic_source_sha,
        "counts": dict(COUNTS),
        "evidence": evidence,
        "entries": entries,
    }
    residual_algebra = {
        "schema_version": 1,
        "artifact_type": "current_anomaly_set_algebra_residual",
        "baseline_modified": False,
        "policy_modified": False,
        "release_acceptance": False,
        "forensic_source_sha": forensic_source_sha,
        "counts": dict(COUNTS),
        "equation": (
            "RESIDUAL_TRUE_NEW = TRUE_NEW_INITIAL - ACTIVE_FINGERPRINTS_CLOSED "
            "- REMOVED - REVIEW_CLOSED + NEW_AFTER_TRIAGE"
        ),
        "cardinality_equation": "19 = 18 - 0 - 0 - 0 + 1",
        "equalities": {
            "initial_still_active_unqualified": True,
            "new_after_triage_is_exactly_x3": True,
            "residual_equation": True,
        },
        "sets": {
            "TRUE_NEW_INITIAL": sorted(initial_fingerprints),
            "ACTIVE_FINGERPRINTS_CLOSED": [],
            "REMOVED": [],
            "REVIEW_CLOSED": [],
            "NEW_AFTER_TRIAGE": [X3_FINGERPRINT],
            "RESIDUAL_TRUE_NEW": residual_set,
        },
        "evidence": evidence,
    }
    return {
        "residual_forensics": residual_forensics,
        "residual_algebra": residual_algebra,
    }


def _json_text(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _md_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _forensics_markdown(payload: Mapping[str, Any]) -> str:
    lines = [
        "# Residual TRUE_NEW forensics",
        "",
        "Projection déterministe de la dette de revue active. Cette preuve ne modifie "
        "ni baseline, ni policy, ni oracle et n'accorde aucune acceptation release.",
        "",
        f"`FORENSIC_SOURCE_SHA = {payload['forensic_source_sha']}`",
        "",
        "## Counts",
        "",
    ]
    for key, value in payload["counts"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Residual entries",
            "",
            "| fingerprint | object_id | path | category | source status | source SHA | "
            "why legitimate | why cannot close | review state | owner | closure phase | "
            "release acceptance |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for entry in payload["entries"]:
        cells = [
            entry["fingerprint"],
            entry["object_id"],
            entry["path"],
            entry["category"],
            entry["source_status"],
            entry["source_sha"],
            entry["why_legitimate"],
            entry["why_cannot_close"],
            entry["current_review_state"],
            entry["owner"],
            entry["closure_phase"],
            str(entry["release_acceptance"]).lower(),
        ]
        lines.append("| " + " | ".join(_md_cell(value) for value in cells) + " |")
    return "\n".join(lines) + "\n"


def _algebra_markdown(payload: Mapping[str, Any]) -> str:
    lines = [
        "# Current anomaly set algebra — residual",
        "",
        f"`FORENSIC_SOURCE_SHA = {payload['forensic_source_sha']}`",
        "",
        f"`{payload['equation']}`",
        "",
        f"`{payload['cardinality_equation']}`",
        "",
        "## Counts",
        "",
    ]
    for key, value in payload["counts"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Sets", ""])
    for key, values in payload["sets"].items():
        rendered = ", ".join(f"`{value}`" for value in values) or "∅"
        lines.append(f"- `{key}`: {rendered}")
    lines.extend(
        [
            "",
            "`release_acceptance = false` — les 19 lignes restent une dette de revue.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_reports(reports: Mapping[str, Mapping[str, Any]]) -> dict[str, str]:
    return {
        OUTPUT_NAMES["residual_forensics"]["json"]: _json_text(
            reports["residual_forensics"]
        ),
        OUTPUT_NAMES["residual_forensics"]["md"]: _forensics_markdown(
            reports["residual_forensics"]
        ),
        OUTPUT_NAMES["residual_algebra"]["json"]: _json_text(
            reports["residual_algebra"]
        ),
        OUTPUT_NAMES["residual_algebra"]["md"]: _algebra_markdown(
            reports["residual_algebra"]
        ),
    }


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def write_reports(
    reports: Mapping[str, Mapping[str, Any]], output_dir: Path
) -> None:
    for name, content in sorted(render_reports(reports).items()):
        _atomic_write(output_dir / name, content)


def check_reports(
    reports: Mapping[str, Mapping[str, Any]], output_dir: Path
) -> list[str]:
    stale = []
    for name, content in sorted(render_reports(reports).items()):
        path = output_dir / name
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            stale.append(name)
    return stale


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir is not None
        else root / "audit"
    )
    reports = build_reports(root)
    if args.check:
        stale = check_reports(reports, output_dir)
        if stale:
            print("stale: " + ", ".join(stale))
            return 1
        print("current: residual TRUE_NEW forensics")
        return 0
    write_reports(reports, output_dir)
    print("written: " + ", ".join(sorted(render_reports(reports))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
