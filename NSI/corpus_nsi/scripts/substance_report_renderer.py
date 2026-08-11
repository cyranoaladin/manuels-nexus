#!/usr/bin/env python3
"""Rendu charté des verdicts de substance System A.

Ce module est un miroir de `check_substance_anchors.py` : il ne décide aucun
statut et ne modifie aucun fichier de suivi du dépôt. Il rend uniquement le
verdict déclaré et le verdict effectif recalculé par le System A.
"""

from __future__ import annotations

import html
import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.check_substance_anchors import (
    CapacityResult,
    ProofCheck,
    check_capacity,
    load_official_labels,
    validate_schema,
)


NON_VALIDATION_BANNER = "pré-jugement outillé, non validation humaine"
REPORT_META_TAG = '<meta name="nsi-report-kind" content="substance-audit">'


class SchemaError(ValueError):
    """Le verdict source ne respecte pas le schéma de substance."""


@dataclass(frozen=True)
class ProofReport:
    role: str
    present: bool
    teaches: bool
    verified: bool
    quote_method: str
    messages: Sequence[str]


@dataclass(frozen=True)
class CapacityReport:
    capacity_id: str
    declared_verdict: str
    effective_verdict: str
    downgraded: bool
    label_ok: bool
    proofs: Sequence[ProofReport]
    reasons: Sequence[str]
    scientific_flags: Sequence[str]
    justification: str


@dataclass(frozen=True)
class ReportModel:
    unit: str
    level: str
    judged_at: str
    judge_model: str
    capacities: Sequence[CapacityReport]
    schema_errors: Sequence[str] = ()

    @property
    def effective_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for capacity in self.capacities:
            counts[capacity.effective_verdict] = counts.get(capacity.effective_verdict, 0) + 1
        return counts

    @property
    def downgraded_count(self) -> int:
        return sum(1 for capacity in self.capacities if capacity.downgraded)


def load_verdict(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SchemaError(f"{path}: verdict JSON non objet")
    return payload


def _schema_errors(verdict: dict[str, Any], repo_root: Path) -> list[str]:
    errors = validate_schema(verdict, repo_root / "substance_verdict.schema.json")
    return [error for error in errors if error.startswith("schéma @") or "introuvable" in error]


def _proof_report(proof: ProofCheck) -> ProofReport:
    return ProofReport(
        role=proof.role,
        present=proof.present,
        teaches=proof.teaches,
        verified=proof.verified,
        quote_method=proof.quote_method or "absent",
        messages=tuple(proof.messages),
    )


def _capacity_report(result: CapacityResult, raw_capacity: dict[str, Any]) -> CapacityReport:
    flags = raw_capacity.get("scientific_flags") or []
    if not isinstance(flags, list):
        flags = [str(flags)]
    return CapacityReport(
        capacity_id=result.capacity_id,
        declared_verdict=result.declared_verdict,
        effective_verdict=result.effective_verdict,
        downgraded=result.downgraded,
        label_ok=result.label_ok,
        proofs=tuple(_proof_report(proof) for proof in result.proofs),
        reasons=tuple(result.reasons),
        scientific_flags=tuple(str(flag) for flag in flags),
        justification=str(raw_capacity.get("justification", "")),
    )


def build_report_model(verdict: dict[str, Any], repo_root: Path) -> ReportModel:
    errors = _schema_errors(verdict, repo_root)
    if errors:
        raise SchemaError("; ".join(errors))

    official = load_official_labels(repo_root)
    section_cache: dict[Path, dict[str, Any]] = {}
    capacities: list[CapacityReport] = []
    for raw_capacity in verdict.get("capacities", []):
        if not isinstance(raw_capacity, dict):
            raise SchemaError("capacité non objet")
        result = check_capacity(raw_capacity, repo_root, official, section_cache)
        capacities.append(_capacity_report(result, raw_capacity))

    return ReportModel(
        unit=str(verdict.get("unit", "")),
        level=str(verdict.get("level", "")),
        judged_at=str(verdict.get("judged_at", "")),
        judge_model=str(verdict.get("judge_model", "")),
        capacities=tuple(capacities),
    )


def _verdict_line(capacity: CapacityReport) -> str:
    suffix = " (DÉGRADÉ)" if capacity.downgraded else ""
    return (
        f"Verdict déclaré: {capacity.declared_verdict} / "
        f"Verdict effectif: {capacity.effective_verdict}{suffix}"
    )


def render_markdown(model: ReportModel) -> str:
    lines = [
        f"# Audit de substance NSI — {model.unit}",
        "",
        f"**Bandeau** : {NON_VALIDATION_BANNER}",
        "",
        f"- Niveau : `{model.level}`",
        f"- Juge : `{model.judge_model}`",
        f"- Date : `{model.judged_at}`",
        "- `covered = 0`",
        "- `published = 0`",
        "",
        "## Capacités",
        "",
    ]
    for capacity in model.capacities:
        lines.extend(
            [
                f"### {capacity.capacity_id}",
                "",
                f"- {_verdict_line(capacity)}",
                f"- Justification : {capacity.justification}",
            ]
        )
        if capacity.scientific_flags:
            lines.append("- Drapeaux scientifiques :")
            lines.extend(f"  - `{flag}`" for flag in capacity.scientific_flags)
        if capacity.reasons:
            lines.append("- Raisons System A :")
            lines.extend(f"  - {reason}" for reason in capacity.reasons)
        lines.append("- Preuves :")
        for proof in capacity.proofs:
            lines.append(
                f"  - {proof.role}: present={proof.present}, "
                f"teaches={proof.teaches}, verified={proof.verified}, méthode={proof.quote_method}"
            )
            lines.extend(f"    - {message}" for message in proof.messages)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _css() -> str:
    return """
:root { color-scheme: light; font-family: system-ui, sans-serif; }
body { margin: 0; background: #f7f7f4; color: #1d252c; }
main { max-width: 1040px; margin: 0 auto; padding: 32px 24px 48px; }
header { background: #12343b; color: #fff; padding: 24px; border-bottom: 5px solid #d6a33d; }
h1, h2, h3 { line-height: 1.2; }
.banner { font-weight: 700; margin-top: 8px; color: #ffe5a6; }
.capacity { background: #fff; border: 1px solid #d5d8d8; border-radius: 6px; padding: 18px; margin: 18px 0; }
.status-line { font-weight: 700; }
.status-downgraded { border-left: 6px solid #b3261e; background: #fff7f5; }
.status-needs_content { border-left: 6px solid #b56a00; }
.status-needs_review { border-left: 6px solid #6b7f00; }
.scientific-flags { background: #fff0d6; border: 1px solid #e0a83c; padding: 10px 14px; margin: 12px 0; }
.proofs { display: grid; gap: 10px; }
.proof { border-top: 1px solid #e3e5e5; padding-top: 10px; }
code { background: #eef0f0; padding: 1px 4px; border-radius: 3px; }
""".strip()


def _status_class(capacity: CapacityReport) -> str:
    if capacity.downgraded:
        return "status-downgraded"
    return f"status-{capacity.effective_verdict}"


def render_html(model: ReportModel) -> str:
    cards: list[str] = []
    for capacity in model.capacities:
        flag_html = ""
        if capacity.scientific_flags:
            flags = "".join(f"<li><code>{html.escape(flag)}</code></li>" for flag in capacity.scientific_flags)
            flag_html = f'<div class="scientific-flags"><strong>Drapeaux scientifiques</strong><ul>{flags}</ul></div>'

        reasons = ""
        if capacity.reasons:
            items = "".join(f"<li>{html.escape(reason)}</li>" for reason in capacity.reasons)
            reasons = f"<h4>Raisons System A</h4><ul>{items}</ul>"

        proofs = []
        for proof in capacity.proofs:
            messages = "".join(f"<li>{html.escape(message)}</li>" for message in proof.messages)
            proofs.append(
                "<section class=\"proof\">"
                f"<strong>{html.escape(proof.role)}</strong> — "
                f"present={str(proof.present).lower()}, "
                f"teaches={str(proof.teaches).lower()}, "
                f"verified={str(proof.verified).lower()}, "
                f"méthode={html.escape(proof.quote_method)}"
                f"<ul>{messages}</ul>"
                "</section>"
            )

        cards.append(
            f'<article class="capacity {_status_class(capacity)}">'
            f"<h3>{html.escape(capacity.capacity_id)}</h3>"
            f'<p class="status-line">{html.escape(_verdict_line(capacity))}</p>'
            f"<p>{html.escape(capacity.justification)}</p>"
            f"{flag_html}"
            f"{reasons}"
            f'<div class="proofs">{"".join(proofs)}</div>'
            "</article>"
        )

    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="fr">',
            "<head>",
            '<meta charset="utf-8">',
            REPORT_META_TAG,
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>Audit de substance NSI — {html.escape(model.unit)}</title>",
            f"<style>{_css()}</style>",
            "</head>",
            "<body>",
            "<header>",
            f"<h1>Audit de substance NSI — {html.escape(model.unit)}</h1>",
            f'<p class="banner">{NON_VALIDATION_BANNER}</p>',
            "</header>",
            "<main>",
            f"<p>Niveau : <code>{html.escape(model.level)}</code></p>",
            "<p><code>covered = 0</code> · <code>published = 0</code></p>",
            "<h2>Capacités</h2>",
            *cards,
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def write_report_outputs(model: ReportModel, markdown_path: Path, html_path: Path) -> None:
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_markdown(model), encoding="utf-8")
    html_path.write_text(render_html(model), encoding="utf-8")
