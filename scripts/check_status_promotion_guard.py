#!/usr/bin/env python3
"""Block status promotion without System A verdict and human confirmation."""

from __future__ import annotations

from dataclasses import dataclass, field
import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from scripts.check_substance_anchors import (
    Section,
    check_capacity,
    load_official_labels,
    validate_schema,
)


ROOT = Path(__file__).resolve().parents[1]
SUBSTANCE_SCHEMA = ROOT / "substance_verdict.schema.json"
CONFIRMATION_SCHEMA = ROOT / "reviewer_confirmation.schema.json"
CAPACITY_RE = re.compile(r"\b[PT]-[A-Z0-9-]+\b")
POSITIVE_COUNT_RE = re.compile(r"\b(covered|published)\s*[:=]\s*([1-9][0-9]*)\b", re.I)


@dataclass(frozen=True)
class Promotion:
    source: Path
    kind: str
    capacity_id: str | None
    line_number: int
    line: str


@dataclass
class StatusPromotionResult:
    errors: list[str] = field(default_factory=list)
    promotions: list[Promotion] = field(default_factory=list)


def canonical_verdict_hash(verdict: dict[str, Any]) -> str:
    payload = json.dumps(verdict, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def status_files(root: Path) -> list[Path]:
    candidates = [
        root / "coverage.md",
        root / "INDEX.md",
        root / "manifest.csv",
    ]
    candidates.extend(sorted(root.glob("substance_review*.json")))
    candidates.extend(sorted(root.glob("substance_report*.md")))
    candidates.extend(sorted(root.glob("**/_substance_review.json")))
    return [path for path in candidates if path.exists() and path.is_file()]


def verdict_files(root: Path) -> list[Path]:
    files = sorted(root.glob("substance_review*.json"))
    files.extend(sorted(root.glob("substance_reviews/**/*review*.json")))
    files.extend(sorted(root.glob("**/_substance_review.json")))
    return [path for path in files if path.exists() and path.is_file()]


def confirmation_files(root: Path) -> list[Path]:
    return [
        path
        for path in sorted(root.glob("**/reviewer_confirmation*.json"))
        if path.exists() and path.is_file()
    ]


def first_capacity_id(text: str) -> str | None:
    match = CAPACITY_RE.search(text)
    return match.group(0) if match else None


def scan_text_status_file(path: Path, root: Path) -> list[Promotion]:
    promotions: list[Promotion] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if "validated_pedagogy" in line:
            promotions.append(
                Promotion(
                    source=path.relative_to(root),
                    kind="validated_pedagogy",
                    capacity_id=first_capacity_id(line),
                    line_number=line_number,
                    line=line.strip(),
                )
            )
        for match in POSITIVE_COUNT_RE.finditer(line):
            promotions.append(
                Promotion(
                    source=path.relative_to(root),
                    kind=f"{match.group(1).lower()} > 0",
                    capacity_id=first_capacity_id(line),
                    line_number=line_number,
                    line=line.strip(),
                )
            )
    return promotions


def positive_int(value: str) -> bool:
    try:
        return int(value.strip()) > 0
    except ValueError:
        return False


def scan_manifest_csv(path: Path, root: Path) -> list[Promotion]:
    promotions: list[Promotion] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for line_number, row in enumerate(reader, 2):
            capacity_id = (
                row.get("capacity_id")
                or row.get("capacite_id")
                or row.get("capacity")
                or first_capacity_id(",".join(row.values()))
            )
            for column in ("covered", "published"):
                if column in row and positive_int(row.get(column, "")):
                    promotions.append(
                        Promotion(
                            source=path.relative_to(root),
                            kind=f"{column} > 0",
                            capacity_id=capacity_id,
                            line_number=line_number,
                            line=str(row),
                        )
                    )
            status = row.get("status") or row.get("statut") or ""
            if status == "validated_pedagogy":
                promotions.append(
                    Promotion(
                        source=path.relative_to(root),
                        kind="validated_pedagogy",
                        capacity_id=capacity_id,
                        line_number=line_number,
                        line=str(row),
                    )
                )
    return promotions


def scan_status_promotions(root: Path) -> list[Promotion]:
    promotions: list[Promotion] = []
    for path in status_files(root):
        if path.name == "manifest.csv":
            promotions.extend(scan_manifest_csv(path, root))
        else:
            promotions.extend(scan_text_status_file(path, root))
    return promotions


def schema_has_hard_error(messages: list[str]) -> bool:
    return any(message.startswith("schema @") or message.startswith("schéma @") for message in messages)


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def validated_system_a_hashes(root: Path) -> dict[str, str]:
    official = load_official_labels(root)
    section_cache: dict[Path, dict[str, Section]] = {}
    hashes: dict[str, str] = {}
    for path in verdict_files(root):
        verdict = load_json(path)
        if verdict is None:
            continue
        if schema_has_hard_error(validate_schema(verdict, SUBSTANCE_SCHEMA)):
            continue
        capacities = verdict.get("capacities", [])
        if not isinstance(capacities, list):
            continue
        for capacity in capacities:
            if not isinstance(capacity, dict):
                continue
            result = check_capacity(capacity, root, official, section_cache)
            if result.effective_verdict == "validated_pedagogy" and not result.downgraded:
                hashes[result.capacity_id] = canonical_verdict_hash(capacity)
    return hashes


def confirmation_schema_errors(payload: dict[str, Any]) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return []
    schema = json.loads(CONFIRMATION_SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    return [error.message for error in validator.iter_errors(payload)]


def reviewer_confirmations(root: Path) -> dict[str, str]:
    confirmations: dict[str, str] = {}
    for path in confirmation_files(root):
        payload = load_json(path)
        if payload is None or confirmation_schema_errors(payload):
            continue
        capacity_id = payload.get("capacite_id")
        verdict_hash = payload.get("verdict_hash")
        if isinstance(capacity_id, str) and isinstance(verdict_hash, str):
            confirmations[capacity_id] = verdict_hash
    return confirmations


def analyze_status_promotions(root: Path = ROOT) -> StatusPromotionResult:
    root = root.resolve()
    result = StatusPromotionResult(promotions=scan_status_promotions(root))
    if not result.promotions:
        return result

    system_a_hashes = validated_system_a_hashes(root)
    confirmations = reviewer_confirmations(root)
    for promotion in result.promotions:
        location = f"{promotion.source}:{promotion.line_number}"
        if not promotion.capacity_id:
            result.errors.append(
                f"{location}: {promotion.kind} sans capacity_id traçable -> confirmation impossible"
            )
            continue
        expected_hash = system_a_hashes.get(promotion.capacity_id)
        if expected_hash is None:
            result.errors.append(
                f"{location}: {promotion.kind} pour {promotion.capacity_id} sans verdict System A valide"
            )
            continue
        confirmed_hash = confirmations.get(promotion.capacity_id)
        if confirmed_hash != expected_hash:
            result.errors.append(
                f"{location}: {promotion.kind} pour {promotion.capacity_id} sans confirmation humaine concordante"
            )
    return result


def main() -> int:
    result = analyze_status_promotions(ROOT)
    if result.errors:
        print("check_status_promotion_guard: KO")
        for error in result.errors:
            print(f"- {error}")
        return 1
    print(f"check_status_promotion_guard: PASS ({len(result.promotions)} promotion positive)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
