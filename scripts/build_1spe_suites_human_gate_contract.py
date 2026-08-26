#!/usr/bin/env python3
"""Derive the fail-closed human-review gate contract for 1SPE-SUITES."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
JSON_OUTPUT = ROOT / "audit" / "HUMAN_REVIEW_GATE_CONTRACT_1SPE_SUITES.json"
MD_OUTPUT = ROOT / "audit" / "HUMAN_REVIEW_GATE_CONTRACT_1SPE_SUITES.md"
FREEZE = ROOT / "audit" / "1SPE_SUITES_REVIEW_SOURCE_FREEZE.json"
PACKET = ROOT / "audit" / "1SPE_SUITES_HUMAN_REVIEW_PACKET.json"
SUNSET = ROOT / "audit" / "RESIDUAL_13_SUNSET_LEDGER.json"
ALGEBRA = ROOT / "audit" / "CURRENT_ANOMALY_SET_ALGEBRA.json"
QCM_AUDIT = ROOT / "audit" / "QCM_SCIENTIFIC_ANSWER_KEY_AUDIT.json"

EXPECTED_FIVE = {
    "1SPE-SUITES-CR-017": "4b9a00c4ef815951",
    "1SPE-SUITES-EX-051": "85454c002c0a1d6a",
    "1SPE-SUITES-RE-C8": "8ca4f3f2a9212e39",
    "1SPE-SUITES-ME-008": "d6985b17d7cab316",
    "1SPE-SUITES-CO-051": "e8ac154947fefcdb",
}
UNKNOWN_FIELDS = (
    "distinct_human_reviewers",
    "one_human_may_satisfy_two_roles",
    "identity_authentication_requirements",
    "canonical_receipt_schema",
    "canonical_allowed_approval_verdicts",
    "approval_scope_granularity",
    "source_sha_binding",
    "render_pdf_binding",
    "shared_dependency_staleness_policy",
    "bulk_status_transition_authority",
)


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _authority(
    authority_id: str,
    path: str,
    lines: str,
    establishes: list[str],
    does_not_establish: list[str] | None = None,
) -> dict[str, Any]:
    absolute = ROOT / path
    return {
        "authority_id": authority_id,
        "path": path,
        "lines": lines,
        "file_sha256": _sha256(absolute),
        "establishes": establishes,
        "does_not_establish": does_not_establish or [],
    }


def _authorities() -> list[dict[str, Any]]:
    return [
        _authority(
            "CAHIER_TRACEABILITY",
            "CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md",
            "71-79",
            ["human_decision_must_be_dated_justified_attributed"],
            ["identity_authentication", "receipt_schema"],
        ),
        _authority(
            "CAHIER_DOUBLE_REVIEW",
            "CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md",
            "614-623",
            [
                "two_role_reviews_per_chapter",
                "role_expert_mathématique",
                "role_expert_programme_pédagogie",
                "no_agent_self_approval",
            ],
            ["two_distinct_human_identities", "dual_role_policy"],
        ),
        _authority(
            "CAHIER_ARCHIVAL",
            "CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md",
            "1067-1070",
            ["double_disciplinary_review", "human_validations_archived"],
            ["archive_format", "receipt_schema"],
        ),
        _authority(
            "README_RELEASE_INDEPENDENCE",
            "README.md",
            "193-214",
            [
                "science_programme_editorial_pdf_reviews_are_independent",
                "final_human_manual_approval_is_separate",
            ],
            ["chapter_receipt_schema"],
        ),
        _authority(
            "README_REVIEW_CHAIN",
            "README.md",
            "779-802",
            [
                "scientific_then_programme_then_editorial_variant_then_pdf_review",
                "final_human_approver_is_user",
                "visual_baseline_change_requires_explicit_approval",
            ],
            ["chapter_content_receipt_schema", "qcm_gate_owner"],
        ),
        _authority(
            "GENERIC_VALIDATION_SCHEMA",
            "Mathematiques/manuel-maths/schemas/validation.schema.json",
            "6-13",
            [
                "generic_per_object_validation_shape",
                "generic_verdicts_pass_fail_warning_manual_review",
                "reviewer_field_optional",
            ],
            [
                "human_role",
                "reviewer_identity_verification",
                "source_sha_binding",
                "approval_semantics",
            ],
        ),
        _authority(
            "GENERIC_VALIDATION_DATABASE",
            "Mathematiques/manuel-maths/db/schema.sql",
            "64-73",
            ["generic_per_object_validation_storage", "reviewer_nullable"],
            ["campaign_scope", "receipt_signature", "staleness"],
        ),
        _authority(
            "LEGACY_OBJECT_RECEIPT_CONVENTION",
            "Mathematiques/manuel-maths/docs/03_architecture_technique.md",
            "22-26",
            ["manual_per_object_revue_humaine_filename_convention"],
            ["receipt_content_semantics", "chapter_campaign_semantics"],
        ),
        _authority(
            "QCM_MACHINE_AUDIT",
            "scripts/build_qcm_scientific_answer_key_audit.py",
            "165-195,234-258",
            [
                "qcm_machine_rows_are_pending_human_approval",
                "machine_audit_cannot_infer_human_approval",
            ],
            ["qcm_human_owner", "qcm_human_granularity", "qcm_closure_receipt"],
        ),
    ]


def _residual_rows(
    freeze: dict[str, Any], packet: dict[str, Any], sunset: dict[str, Any]
) -> list[dict[str, Any]]:
    frozen = {row["object_id"]: row for row in freeze["objects"]}
    packet_objects = {row["object_id"]: row for row in packet["objects"]}
    sunset_objects = {
        row["object_id"]: row
        for row in sunset["entries"]
        if row.get("chapter") == "1SPE-SUITES"
    }
    if set(sunset_objects) != set(EXPECTED_FIVE):
        raise ValueError("residual13 chapter intersection is not exact")
    rows = []
    for object_id, fingerprint in sorted(EXPECTED_FIVE.items()):
        source = frozen[object_id]
        machine = packet_objects[object_id]
        debt = sunset_objects[object_id]
        states = {
            item["state"] for item in machine["machine_review_dimensions"].values()
        }
        machine_state = "MACHINE_PASS" if states == {"MACHINE_PASS"} else "NOT_PASS"
        sunset_digest = debt["source_sha"].removeprefix("sha256:")
        rows.append(
            {
                "fingerprint": fingerprint,
                "object_id": object_id,
                "path": source["path"],
                "current_source_sha256": "sha256:" + source["source_sha256"],
                "sunset_source_sha256": debt["source_sha"],
                "sunset_source_binding_stale": sunset_digest
                != source["source_sha256"],
                "human_gate_required": True,
                "machine_review_state": machine_state,
                "current_status": source["status"],
                "remaining_required_reviews": debt["required_reviews"],
                "closure_condition": debt["closure_condition"],
                "closure_allowed": False,
            }
        )
    return rows


def _build_raw() -> dict[str, Any]:
    freeze = _load(FREEZE)
    packet = _load(PACKET)
    sunset = _load(SUNSET)
    algebra = _load(ALGEBRA)
    qcm = _load(QCM_AUDIT)
    previous89 = [
        row
        for row in algebra["expected_review_debt_details"]
        if row.get("chapter") == "1SPE-SUITES"
    ]
    residual = _residual_rows(freeze, packet, sunset)
    semantics = {field: "UNKNOWN" for field in UNKNOWN_FIELDS}
    return {
        "artifact_type": "1SPE_SUITES_HUMAN_REVIEW_GATE_CONTRACT",
        "schema_version": 1,
        "chapter": "1SPE-SUITES",
        "review_source_sha": freeze["source_sha"],
        "chapter_object_set_digest": freeze["chapter_object_set_digest"],
        "verdict": "GOVERNANCE_CONTRACT_INCOMPLETE",
        "approval_materialization_allowed": False,
        "status_transition_allowed": False,
        "debt_closure_allowed": False,
        "required_roles": [
            "expert mathématique",
            "expert programme/pédagogie",
        ],
        "required_role_reviews": 2,
        "auto_approval_allowed": False,
        "human_decision_minimum_traceability": ["dated", "justified", "attributed"],
        "human_contract_semantics": semantics,
        "unknown_contract_semantics": len(semantics),
        "generic_validation_verdicts_are_not_approval_verdicts": [
            "pass",
            "fail",
            "warning",
            "manual_review",
        ],
        "requested_reviewer_choices_without_repository_mapping": [
            "APPROVE",
            "REQUEST_CHANGES",
            "REJECT",
        ],
        "qcm_human_gate": {
            "owner": "UNKNOWN",
            "granularity": "UNKNOWN",
            "current_state": qcm["status"],
            "covered_by_math_role": "UNPROVED",
            "covered_by_programme_pedagogy_role": "UNPROVED",
            "distinct_campaign_required": "UNPROVED",
            "closure_materialization_allowed": False,
        },
        "review_separation": {
            "content_science_pedagogy_review": "REQUIRED_PENDING",
            "editorial_variant_review": "SEPARATE_REQUIRED_PENDING",
            "visual_pdf_review": "SEPARATE_REQUIRED_PENDING",
            "d7_final_visual_approval": "SEPARATE_REQUIRED_PENDING",
            "print_release_approval": "SEPARATE_REQUIRED_PENDING",
        },
        "content_review_is_final_visual_or_d7_approval": False,
        "local_packet_role_tokens_are_canonical_authority": False,
        "legacy_receipt_filename_is_sufficient_approval_contract": False,
        "campaign_level_bulk_transition_proved": False,
        "residual13_chapter_intersection": residual,
        "previous89_chapter_intersection": previous89,
        "counts": {
            "residual13_chapter_debts": len(residual),
            "residual13_stale_sunset_source_bindings": sum(
                row["sunset_source_binding_stale"] for row in residual
            ),
            "previous89_chapter_debts": len(previous89),
            "unknown_contract_semantics": len(semantics),
        },
        "authorities": _authorities(),
        "non_applicable_precedent": {
            "path": "audit/schemas/v1/1nsi-content-review.schema.json",
            "reason": "schema is const-bound to artifact_type 1nsi_content_reviews and manual 1NSI",
        },
        "materialization_stop_conditions": [
            "do not record APPROVE/REQUEST_CHANGES/REJECT in a repository receipt",
            "do not assign a QCM gate owner",
            "do not transition any of the 161 object statuses",
            "do not promote any of the 15 atoms to FULL",
            "do not close any of the five residual13 debts",
        ],
    }


def validate_contract(payload: dict[str, Any]) -> None:
    if payload.get("verdict") != "GOVERNANCE_CONTRACT_INCOMPLETE":
        raise ValueError("human contract must remain incomplete")
    if any(
        payload.get(key) is not False
        for key in (
            "approval_materialization_allowed",
            "status_transition_allowed",
            "debt_closure_allowed",
        )
    ):
        raise ValueError("approval, transition, and debt closure must fail closed")
    semantics = payload.get("human_contract_semantics", {})
    if semantics != {field: "UNKNOWN" for field in UNKNOWN_FIELDS}:
        raise ValueError("undefined contract semantics were erased or invented")
    if payload.get("unknown_contract_semantics") != len(UNKNOWN_FIELDS):
        raise ValueError("UNKNOWN count mismatch")
    qcm = payload.get("qcm_human_gate", {})
    if qcm.get("owner") != "UNKNOWN" or qcm.get("granularity") != "UNKNOWN":
        raise ValueError("QCM owner or granularity was invented")
    residual = payload.get("residual13_chapter_intersection", [])
    if {row.get("object_id"): row.get("fingerprint") for row in residual} != EXPECTED_FIVE:
        raise ValueError("five-debt intersection mismatch")
    if any(row.get("closure_allowed") is not False for row in residual):
        raise ValueError("residual debt closure was forged")
    expected = _build_raw()
    if payload != expected:
        raise ValueError("human contract artifact does not match repository authorities")


def build_contract() -> dict[str, Any]:
    payload = _build_raw()
    validate_contract(payload)
    return payload


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# HUMAN REVIEW GATE CONTRACT — 1SPE-SUITES",
        "",
        f"- Source de revue figée : `{payload['review_source_sha']}`",
        f"- Digest du set des 161 objets : `{payload['chapter_object_set_digest']}`",
        f"- Verdict : **{payload['verdict']}**",
        "- Matérialisation d'une approbation : **INTERDITE**",
        "- Transition de statut, promotion FULL et clôture de dette : **INTERDITES**",
        "",
        "## Ce que le dépôt impose",
        "",
        "Deux revues de rôles par chapitre : expert mathématique et expert programme/pédagogie. "
        "Aucun élément ne peut être auto-approuvé par l'agent qui l'a produit. Toute décision humaine doit être datée, justifiée et attribuée.",
        "",
        "## Sémantiques non définies",
        "",
        "| Sémantique | État |",
        "|---|---|",
    ]
    for key, value in payload["human_contract_semantics"].items():
        lines.append(f"| `{key}` | `{value}` |")
    qcm = payload["qcm_human_gate"]
    lines.extend(
        [
            "",
            "## Gate humain QCM",
            "",
            f"- `QCM_HUMAN_GATE_OWNER = {qcm['owner']}`",
            f"- `QCM_HUMAN_GATE_GRANULARITY = {qcm['granularity']}`",
            f"- `QCM_HUMAN_GATE_CURRENT_STATE = {qcm['current_state']}`",
            "- Aucune preuve ne permet de choisir entre couverture par le rôle mathématique, couverture par le rôle programme/pédagogie ou campagne distincte.",
            "",
            "## Autorités et limites",
            "",
            "| ID | Source | Établit | N'établit pas |",
            "|---|---|---|---|",
        ]
    )
    for row in payload["authorities"]:
        establishes = ", ".join(f"`{item}`" for item in row["establishes"])
        limits = ", ".join(f"`{item}`" for item in row["does_not_establish"]) or "—"
        lines.append(
            f"| `{row['authority_id']}` | `{row['path']}:{row['lines']}` | {establishes} | {limits} |"
        )
    lines.extend(
        [
            "",
            "## Cinq dettes residual13 du chapitre",
            "",
            "| Fingerprint | Objet | Statut | Machine | Binding sunset périmé | Condition restante |",
            "|---|---|---|---|---:|---|",
        ]
    )
    for row in payload["residual13_chapter_intersection"]:
        lines.append(
            f"| `{row['fingerprint']}` | `{row['object_id']}` | `{row['current_status']}` | "
            f"`{row['machine_review_state']}` | {'OUI' if row['sunset_source_binding_stale'] else 'NON'} | "
            f"`{row['closure_condition']}` |"
        )
    lines.extend(
        [
            "",
            "`PREVIOUS_89 ∩ 1SPE-SUITES = 0`.",
            "",
            "Les deux revues de contenu ne valent ni revue éditoriale/variante, ni revue PDF, ni D7, ni approbation print/release. Les packets peuvent seulement fournir des entrées neutres aux humains; ils ne constituent pas des receipts exécutables.",
            "",
        ]
    )
    return "\n".join(lines)


def _atomic_write(path: Path, content: str) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(temp_name, path)
    except BaseException:
        Path(temp_name).unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check fixed outputs")
    args = parser.parse_args()
    payload = build_contract()
    rendered_json = render_json(payload)
    rendered_md = render_markdown(payload)
    if args.check:
        if (
            not JSON_OUTPUT.is_file()
            or JSON_OUTPUT.read_text(encoding="utf-8") != rendered_json
            or not MD_OUTPUT.is_file()
            or MD_OUTPUT.read_text(encoding="utf-8") != rendered_md
        ):
            raise SystemExit("STALE human review gate contract artifacts")
        print("PASS GOVERNANCE_CONTRACT_INCOMPLETE: approval materialization blocked")
        return 0
    _atomic_write(JSON_OUTPUT, rendered_json)
    _atomic_write(MD_OUTPUT, rendered_md)
    print("wrote HUMAN_REVIEW_GATE_CONTRACT_1SPE_SUITES.{json,md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
