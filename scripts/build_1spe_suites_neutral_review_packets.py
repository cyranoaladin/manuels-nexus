#!/usr/bin/env python3
"""Build neutral, non-executable human-review inputs for 1SPE-SUITES."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
FREEZE_PATH = AUDIT / "1SPE_SUITES_REVIEW_SOURCE_FREEZE.json"
CONTRACT_PATH = AUDIT / "HUMAN_REVIEW_GATE_CONTRACT_1SPE_SUITES.json"
MACHINE_PACKET_PATH = AUDIT / "1SPE_SUITES_HUMAN_REVIEW_PACKET.json"
PROGRAMME_PATH = AUDIT / "official_program_coverage" / "1SPE.json"
P0_PATH = AUDIT / "1SPE_SUITES_WRONG_YEAR_P0_FORENSICS.json"
QCM_AUDIT_PATH = AUDIT / "QCM_SCIENTIFIC_ANSWER_KEY_AUDIT.json"

#: Gel courant du chapitre. Le precedent, c667f12b, est conserve intact sous
#: audit/reviews/human/1SPE-SUITES/superseded/ et marque HISTORICAL_SUPERSEDED.
SOURCE_SHA = "41b68da867a085a550dd733d6e3dfb64fa7bc6d7"
OBJECT_SET_DIGEST = (
    "sha256:60335a3580412b04b3563335e96a430346d6d662faf41aa9f34af81a2b5cff18"
)
ROLES = ("EXPERT_MATHEMATIQUE", "EXPERT_PROGRAMME_PEDAGOGIE")
OUTPUTS = {
    "EXPERT_MATHEMATIQUE": (
        AUDIT / "1SPE_SUITES_EXPERT_MATHEMATIQUE_NEUTRAL_REVIEW_PACKET.json",
        AUDIT / "1SPE_SUITES_EXPERT_MATHEMATIQUE_NEUTRAL_REVIEW_PACKET.md",
    ),
    "EXPERT_PROGRAMME_PEDAGOGIE": (
        AUDIT
        / "1SPE_SUITES_EXPERT_PROGRAMME_PEDAGOGIE_NEUTRAL_REVIEW_PACKET.json",
        AUDIT
        / "1SPE_SUITES_EXPERT_PROGRAMME_PEDAGOGIE_NEUTRAL_REVIEW_PACKET.md",
    ),
}
FORBIDDEN_EXECUTABLE_KEYS = {
    "approval",
    "approved",
    "assigned_reviewer",
    "receipt",
    "receipt_path",
    "reviewer_identity",
    "status_transition",
    "new_status",
    "full_promotion",
}


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _git_diff(old_sha: str, new_sha: str, path: str) -> str:
    run = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--unified=3", old_sha, new_sha, "--", path],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return run.stdout


def _chapter_pdfs(machine: dict[str, Any]) -> list[dict[str, Any]]:
    paths = {
        "complet": "Mathematiques/manuel-maths/build/1SPE-SUITES/1SPE-SUITES_complet.pdf",
        "methodes": "Mathematiques/manuel-maths/build/1SPE-SUITES/1SPE-SUITES_methodes.pdf",
        "parcours1": "Mathematiques/manuel-maths/build/1SPE-SUITES/1SPE-SUITES_parcours1.pdf",
        "remediation": "Mathematiques/manuel-maths/build/1SPE-SUITES/1SPE-SUITES_remediation.pdf",
    }
    variants = machine["machine_review_campaign"]["render_qa"]["variants"]
    rows = []
    for variant in ("complet", "methodes", "parcours1", "remediation"):
        evidence = variants[variant]
        rows.append(
            {
                "variant": variant,
                "path": paths[variant],
                "sha256": "sha256:" + evidence["pdf_sha256"],
                "pages": evidence["pages"],
                "use": "CONTENT_REVIEW_AID_ONLY",
                "tracked_in_git": False,
                "object_to_page_exact_index": "NOT_ESTABLISHED",
                "render_evidence_source_sha": machine["review_source_sha"],
                "freeze_content_equivalence_basis": (
                    "all 161 object path/source SHA-256 pairs match the current freeze"
                ),
            }
        )
    return rows


def _programme_rows() -> list[dict[str, Any]]:
    programme = _load(PROGRAMME_PATH)
    rows = [
        row
        for row in programme["rows"]
        if row.get("chapter") == "1SPE-SUITES" and row.get("mandatory") == "YES"
    ]
    rows.sort(key=lambda row: row["atom_id"])
    keep = (
        "atom_id",
        "NOR",
        "official_section",
        "official_page_or_anchor",
        "official_wording_or_short_paraphrase",
        "obligation_type",
        "contract_capacity",
        "course_sources",
        "method_sources",
        "exercise_sources",
        "correction_sources",
        "assessment_sources",
        "remediation_sources",
        "coverage_status",
        "review_status",
        "programme_state",
        "scientific_state",
        "pedagogical_state",
        "assessment_alignment_state",
        "reason",
    )
    return [{key: row.get(key) for key in keep} for row in rows]


def _p0_history(freeze: dict[str, Any]) -> dict[str, Any]:
    source = _load(P0_PATH)
    frozen = {row["object_id"]: row for row in freeze["objects"]}
    oracles = {row["object_id"]: row for row in source["technical_oracles"]}
    rows = []
    for historical in sorted(source["objects"], key=lambda row: row["object_id"]):
        current = frozen[historical["object_id"]]
        patch = _git_diff(historical["source_sha"], SOURCE_SHA, historical["path"])
        if not patch:
            raise ValueError(f"missing before/after patch for {historical['object_id']}")
        rows.append(
            {
                "object_id": historical["object_id"],
                "path": historical["path"],
                "object_type": historical["object_type"],
                "student_teacher": historical["student_teacher"],
                "capacities": historical["capacities"],
                "official_atoms": historical["official_atoms"],
                "set_membership": historical["set_membership"],
                "before_source_sha": historical["source_sha"],
                "before_source_sha256": historical["source_digest"],
                "before_claims": historical["claims"],
                "current_freeze_source_sha": SOURCE_SHA,
                "current_frozen_source_sha256": "sha256:" + current["source_sha256"],
                "current_source_commit_sha": current["source_commit_sha"],
                "before_after_unified_patch": patch,
                "before_after_patch_digest": "sha256:"
                + hashlib.sha256(patch.encode("utf-8")).hexdigest(),
                "current_technical_oracle": oracles.get(historical["object_id"]),
            }
        )
    return {
        "forensics_path": str(P0_PATH.relative_to(ROOT)),
        "forensics_sha256": _sha256(P0_PATH),
        "pre_rewrite_sha": source["source_freeze"]["PRE_P0_REWRITE_SHA"],
        "current_freeze_sha": SOURCE_SHA,
        "object_count": source["summary"]["union_count"],
        "claim_count": source["summary"]["rendered_claim_count"],
        "rewritten_claim_count": source["summary"]["rewrite_to_1spe_count"],
        "kept_claim_count": source["summary"]["keep_as_is_count"],
        "technical_oracle_count": source["summary"]["technical_oracle_count"],
        "objects": rows,
    }


def _other_corrections() -> list[dict[str, Any]]:
    chapter = "Mathematiques/manuel-maths/chapitres/1SPE-SUITES"
    return [
        {
            "class_id": "Q_ZERO_IS_ALLOWED",
            "review_question": "La définition autorise-t-elle une raison q=0 sans imposer une non-nullité indue ?",
            "evidence_paths": [
                f"{chapter}/cours/12_C3_suites_geometriques.tex",
                "audit/manual_1spe/DEFECT_REGISTER.yaml",
                "tests/test_1spe_suites_course_evaluation_deterministic_fixes.py",
            ],
        },
        {
            "class_id": "ZERO_POWER_ZERO_AVOIDED",
            "review_question": "Le terme initial est-il conservé séparément quand q=0, sans demander d'évaluer 0^0 ?",
            "evidence_paths": [
                f"{chapter}/cours/12_C3_suites_geometriques.tex",
                f"{chapter}/cours/16_C7_algorithmique.tex",
                "tests/test_1spe_suites_course_evaluation_deterministic_fixes.py",
            ],
        },
        {
            "class_id": "QUOTIENT_IS_CONDITIONAL_CHARACTERIZATION",
            "review_question": "Le quotient est-il utilisé seulement après preuve que le dénominateur est non nul ?",
            "evidence_paths": [
                f"{chapter}/cours/12_C3_suites_geometriques.tex",
                f"{chapter}/methodes/1SPE-SUITES-ME-003.tex",
                "tests/test_1spe_suites_001_025_deterministic_fixes.py",
            ],
        },
        {
            "class_id": "ZERO_SEQUENCE_AND_ZERO_TERMS_ALLOWED",
            "review_question": "La suite nulle et les suites géométriques contenant des termes nuls restent-elles reconnues ?",
            "evidence_paths": [
                f"{chapter}/cours/12_C3_suites_geometriques.tex",
                f"{chapter}/qcm/1SPE-SUITES-QCM.json",
                "tests/test_1spe_suites_course_evaluation_deterministic_fixes.py",
            ],
        },
        {
            "class_id": "MINUS_ONE_POWER_N_IS_GEOMETRIC",
            "review_question": "La suite (-1)^n est-elle correctement reconnue géométrique de raison -1 ?",
            "evidence_paths": [
                f"{chapter}/cours/13_C4_sommes.tex",
                f"{chapter}/remediation/1SPE-SUITES-RE-C8.tex",
                "tests/test_1spe_suites_026_051_deterministic_fixes.py",
            ],
        },
        {
            "class_id": "FINITE_PREFIX_DOES_NOT_PROVE_UNIVERSAL_PROPERTY",
            "review_question": "Les préfixes finis conduisent-ils seulement à une conjecture, jamais à une propriété pour tout n ?",
            "evidence_paths": [
                f"{chapter}/remediation/1SPE-SUITES-RE-C3.tex",
                "tests/test_1spe_suites_remediation_legacy_closure.py",
                "tests/test_1spe_suites_programme_boundary.py",
            ],
        },
        {
            "class_id": "U_OF_N_IS_VALID_FUNCTION_NOTATION",
            "review_question": "La notation fonctionnelle u(n) est-elle reconnue valide tout en enseignant la convention u_n ?",
            "evidence_paths": [
                f"{chapter}/cours/10_C1_generalites_suites.tex",
                f"{chapter}/qcm/1SPE-SUITES-QCM.json",
                "tests/test_1spe_suites_course_evaluation_deterministic_fixes.py",
            ],
        },
    ]


def _qcm_material(contract: dict[str, Any]) -> dict[str, Any]:
    audit = _load(QCM_AUDIT_PATH)
    rows = [row for row in audit["questions"] if row.get("chapter") == "1SPE-SUITES"]
    rows.sort(key=lambda row: int(row["question_id"].removeprefix("Q")))
    gate = contract["qcm_human_gate"]
    return {
        "audit_path": str(QCM_AUDIT_PATH.relative_to(ROOT)),
        "audit_sha256": _sha256(QCM_AUDIT_PATH),
        "canonical_source_path": rows[0]["source_path"],
        "canonical_source_sha256": "sha256:" + rows[0]["source_sha256"],
        "questions_count": len(rows),
        "questions": rows,
        "human_state": gate["current_state"],
        "human_gate_owner": gate["owner"],
        "human_gate_granularity": gate["granularity"],
        "coverage_by_chapter_roles": "UNPROVED",
        "decision_capture": "DISABLED",
    }


def _remediation_material(freeze: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_count": len(freeze["remediation"]["sources"]),
        "sources": freeze["remediation"]["sources"],
        "aggregate_digest": freeze["remediation"]["aggregate_digest"],
        "required_capacity_loops": 8,
        "machine_validated_capacity_loops": 8,
        "exercise_correction_pairs": 44,
        "machine_evidence_only": True,
        "evidence_refs": [
            "tests/test_1spe_suites_remediation_legacy_closure.py",
            "tests/test_1spe_suites_remediation_c8.py",
            "tests/test_1spe_suites_remediation_qcm_closure.py",
            "audit/1SPE_SUITES_HUMAN_REVIEW_PACKET.json",
        ],
        "review_focus": [
            "diagnostic de la cause",
            "rappel ciblé",
            "aide graduée",
            "activité guidée",
            "exercice autonome et correction",
            "revalidation",
        ],
    }


def _checklist(role: str) -> list[dict[str, Any]]:
    common = {
        "current": ["CURRENT_CONTENT_TO_REVIEW", "SOURCE_INVENTORY_161", "CHAPTER_PDFS"],
        "programme": ["PROGRAMME_MAPPING_15", "MENE2602917A"],
        "p0": ["P0_19_BEFORE_AFTER", "audit/1SPE_SUITES_WRONG_YEAR_P0_FORENSICS.json"],
        "qcm": ["QCM_21", "audit/QCM_SCIENTIFIC_ANSWER_KEY_AUDIT.json"],
        "remediation": ["REMEDIATION_8_CAPACITY_LOOPS", "SOURCE_INVENTORY_161"],
    }
    if role == "EXPERT_MATHEMATIQUE":
        items = [
            ("MATH-01", "Examiner toutes les définitions et leurs domaines de validité.", "current"),
            ("MATH-02", "Vérifier chaque propriété, hypothèse et quantificateur.", "current"),
            ("MATH-03", "Rejouer les raisonnements et calculs des exercices.", "current"),
            ("MATH-04", "Comparer chaque question d'exercice à sa correction.", "current"),
            ("MATH-05", "Vérifier les calculs numériques, unités et arrondis.", "current"),
            ("MATH-06", "Résoudre indépendamment les 21 QCM et leurs distracteurs.", "qcm"),
            ("MATH-07", "Vérifier les diagnostics associés à chaque distracteur QCM.", "qcm"),
            ("MATH-08", "Vérifier les huit boucles de remédiation et leurs corrections.", "remediation"),
            ("MATH-09", "Exécuter mentalement ou contrôler les algorithmes de termes, sommes et seuils.", "current"),
            ("MATH-10", "Contrôler axes, valeurs et cohérence des graphiques/tableaux.", "current"),
            ("MATH-11", "Vérifier la minimalité de chaque seuil par deux rangs frontières.", "current"),
            ("MATH-12", "Distinguer observation, conjecture intuitive et preuve.", "programme"),
            ("MATH-13", "Rechercher tout logarithme utilisé comme méthode en parcours obligatoire.", "p0"),
            ("MATH-14", "Rechercher tout formalisme de limite ou théorème de convergence de Terminale.", "p0"),
            ("MATH-15", "Comparer le contenu courant aux 19 patches avant/après P0.", "p0"),
            ("MATH-16", "Contre-vérifier les sept autres classes de corrections scientifiques.", "p0"),
            ("MATH-17", "Examiner le contenu courant complet, sans substituer l'historique à la revue.", "current"),
        ]
    else:
        items = [
            ("PED-01", "Vérifier l'autorité MENE2602917A et les quinze atomes obligatoires.", "programme"),
            ("PED-02", "Contrôler le mapping de chaque capacité vers ses atomes officiels.", "programme"),
            ("PED-03", "Vérifier l'absence de contenu wrong-year dans le parcours exigible.", "p0"),
            ("PED-04", "Contrôler les prérequis et l'ordre d'introduction des notions.", "current"),
            ("PED-05", "Examiner la qualité des diagnostics initiaux.", "current"),
            ("PED-06", "Évaluer le cours et l'institutionnalisation des notions.", "current"),
            ("PED-07", "Évaluer l'accessibilité et la progressivité des méthodes.", "current"),
            ("PED-08", "Évaluer diversité, difficulté et autonomie des exercices.", "current"),
            ("PED-09", "Vérifier la couverture et l'utilité didactique des QCM.", "qcm"),
            ("PED-10", "Vérifier que chaque distracteur représente une erreur plausible.", "qcm"),
            ("PED-11", "Vérifier que les remédiations traitent la cause de l'erreur.", "remediation"),
            ("PED-12", "Évaluer l'alignement des évaluations avec l'enseignement.", "current"),
            ("PED-13", "Évaluer charge cognitive, langage et niveau Première.", "current"),
            ("PED-14", "Évaluer authenticité et pertinence des contextes.", "current"),
            ("PED-15", "Contrôler progressivité, différenciation et prise d'initiative.", "current"),
            ("PED-16", "Contrôler la cohérence didactique du chapitre entier.", "current"),
            ("PED-17", "Examiner le contenu courant complet, sans substituer l'historique à la revue.", "current"),
        ]
    return [
        {"item_id": item_id, "review_question": question, "evidence_refs": common[group]}
        for item_id, question, group in items
    ]


def _authority_navigation(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "authority_id": row["authority_id"],
            "path": row["path"],
            "lines": row["lines"],
            "file_sha256": row["file_sha256"],
            "establishes": row["establishes"],
            "does_not_establish": row["does_not_establish"],
        }
        for row in contract["authorities"]
    ]


def _build_common() -> dict[str, Any]:
    freeze = _load(FREEZE_PATH)
    contract = _load(CONTRACT_PATH)
    machine = _load(MACHINE_PACKET_PATH)
    machine_objects = {row["object_id"]: row for row in machine["objects"]}
    for row in freeze["objects"]:
        observed = machine_objects.get(row["object_id"])
        if not observed or observed["path"] != row["path"] or observed["source_sha256"] != row["source_sha256"]:
            raise ValueError("render evidence object inventory differs from the current freeze")
    programme = _programme_rows()
    p0 = _p0_history(freeze)
    qcm = _qcm_material(contract)
    remediation = _remediation_material(freeze)
    pdfs = _chapter_pdfs(machine)
    return {
        "schema_version": "1SPE_SUITES_NEUTRAL_REVIEW_PACKET.v1",
        "artifact_type": "NEUTRAL_HUMAN_REVIEW_INPUT",
        "chapter": "1SPE-SUITES",
        "source_freeze": {
            "source_sha": freeze["source_sha"],
            "chapter_object_set_digest": freeze["chapter_object_set_digest"],
            "freeze_path": str(FREEZE_PATH.relative_to(ROOT)),
            "freeze_sha256": _sha256(FREEZE_PATH),
            "object_count": freeze["counts"]["chapter_objects"],
            "source_change_invalidates_packet": True,
        },
        "governance": {
            "contract_path": str(CONTRACT_PATH.relative_to(ROOT)),
            "contract_sha256": _sha256(CONTRACT_PATH),
            "contract_state": contract["verdict"],
            "decision_capture": "DISABLED",
            "human_review_state": "PENDING_UNASSIGNED",
            "qcm_human_state": contract["qcm_human_gate"]["current_state"],
            "qcm_gate_owner": contract["qcm_human_gate"]["owner"],
            "qcm_gate_granularity": contract["qcm_human_gate"]["granularity"],
            "unknown_contract_semantics": contract["human_contract_semantics"],
            "authority_navigation": _authority_navigation(contract),
        },
        "neutrality_invariants": {
            "executable_receipt_zone": False,
            "prechecked_decision": False,
            "status_or_full_transition": False,
            "debt_closure": False,
            "d7_or_visual_final_decision": False,
        },
        "current_content_to_review": {
            "scope": "CURRENT_CONTENT_TO_REVIEW",
            "objects": freeze["objects"],
            "contract": freeze["contract"],
            "qcm_sources": freeze["qcm"],
            "remediation_sources": freeze["remediation"],
            "chapter_pdfs": pdfs,
            "pdf_limitations": {
                "release_proof": False,
                "d7_or_final_visual_proof": False,
                "global_manual_layout_proof": False,
                "tracked_publication_artifacts": False,
                "exact_object_to_pdf_page_mapping": "NOT_ESTABLISHED",
                "note": (
                    "Les quatre PDF locaux sont des aides de lecture dérivées. "
                    "Leur inventaire objet correspond au gel, mais ils ne constituent "
                    "ni preuve release, ni D7, ni préflight global du manuel."
                ),
            },
        },
        "programme_mapping": {
            "authority_path": str(PROGRAMME_PATH.relative_to(ROOT)),
            "authority_sha256": _sha256(PROGRAMME_PATH),
            "nor": "MENE2602917A",
            "mandatory_atoms_count": len(programme),
            "full_atoms_count": 0,
            "full_transition_allowed": False,
            "mandatory_atoms": programme,
        },
        "change_history_fix_evidence": {
            "scope": "CHANGE_HISTORY_FIX_EVIDENCE_NOT_CURRENT_CONTENT",
            "warning": (
                "L'historique aide à contrôler les corrections ; il ne remplace jamais "
                "l'examen des 161 sources courantes."
            ),
            "wrong_year_p0": p0,
            "other_scientific_corrections": _other_corrections(),
        },
        "qcm_review_material": qcm,
        "remediation_review_material": remediation,
        "machine_evidence_context": {
            "path": str(MACHINE_PACKET_PATH.relative_to(ROOT)),
            "sha256": _sha256(MACHINE_PACKET_PATH),
            "machine_content_review": "PASS",
            "human_content_review": "PENDING",
            "render_pages_inspected": machine["machine_review_campaign"]["render_qa"]["pages_inspected"],
            "targeted_tests_passed": machine["machine_review_campaign"]["targeted_tests"]["passed"],
            "limitations": [
                "machine evidence is advisory to the human reviewer",
                "machine PASS is not an instruction to accept",
                "chapter content review is separate from final visual, D7, print and release review",
            ],
        },
        "navigation": {
            "source_inventory": "current_content_to_review.objects",
            "pdfs": "current_content_to_review.chapter_pdfs",
            "programme": "programme_mapping.mandatory_atoms",
            "p0_before_after": "change_history_fix_evidence.wrong_year_p0.objects",
            "qcm": "qcm_review_material.questions",
            "remediation": "remediation_review_material.sources",
            "history_is_not_current_content": True,
        },
        "counts": {
            "objects": len(freeze["objects"]),
            "chapter_pdfs": len(pdfs),
            "chapter_pdf_pages": sum(row["pages"] for row in pdfs),
            "mandatory_atoms": len(programme),
            "wrong_year_p0_objects": p0["object_count"],
            "qcm_questions": qcm["questions_count"],
            "remediation_sources": remediation["source_count"],
        },
    }


def build_packets() -> dict[str, dict[str, Any]]:
    common = _build_common()
    packets = {}
    for role in ROLES:
        packet = copy.deepcopy(common)
        packet["packet_id"] = f"1SPE-SUITES-{role}-NEUTRAL-{SOURCE_SHA[:8]}"
        packet["review_role"] = role
        packet["role_checklist"] = _checklist(role)
        validate_packet(packet)
        packets[role] = packet
    return packets


def _walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def validate_packet(packet: dict[str, Any]) -> None:
    freeze = _load(FREEZE_PATH)
    if packet.get("review_role") not in ROLES:
        raise ValueError("packet role is not exact")
    source = packet.get("source_freeze", {})
    if source.get("source_sha") != SOURCE_SHA or source.get("chapter_object_set_digest") != OBJECT_SET_DIGEST:
        raise ValueError("packet is not bound to the current 161-object freeze")
    objects = packet.get("current_content_to_review", {}).get("objects", [])
    if objects != freeze["objects"] or len(objects) != 161:
        raise ValueError("packet object inventory differs from exact freeze")
    governance = packet.get("governance", {})
    if governance.get("contract_state") != "GOVERNANCE_CONTRACT_INCOMPLETE":
        raise ValueError("governance contract must remain incomplete")
    if governance.get("decision_capture") != "DISABLED":
        raise ValueError("packet may not capture a decision")
    if governance.get("human_review_state") != "PENDING_UNASSIGNED":
        raise ValueError("packet may not assign or complete human review")
    if governance.get("qcm_gate_owner") != "UNKNOWN" or governance.get("qcm_gate_granularity") != "UNKNOWN":
        raise ValueError("packet may not invent the QCM human gate")
    invariants = packet.get("neutrality_invariants", {})
    if invariants != {
        "executable_receipt_zone": False,
        "prechecked_decision": False,
        "status_or_full_transition": False,
        "debt_closure": False,
        "d7_or_visual_final_decision": False,
    }:
        raise ValueError("neutrality invariants changed")
    if set(_walk_keys(packet)) & FORBIDDEN_EXECUTABLE_KEYS:
        raise ValueError("packet contains an executable governance key")
    programme = packet.get("programme_mapping", {})
    atom_ids = {row.get("atom_id") for row in programme.get("mandatory_atoms", [])}
    if atom_ids != {f"1SPE-OFFICIAL-{number:03d}" for number in range(48, 63)}:
        raise ValueError("mandatory programme set is not exact")
    if programme.get("full_atoms_count") != 0 or programme.get("full_transition_allowed") is not False:
        raise ValueError("packet may not promote FULL")
    qcm = packet.get("qcm_review_material", {})
    if qcm.get("questions_count") != 21 or len(qcm.get("questions", [])) != 21:
        raise ValueError("QCM review set is not exact")
    if qcm.get("human_gate_owner") != "UNKNOWN" or qcm.get("human_gate_granularity") != "UNKNOWN":
        raise ValueError("QCM gate semantics must remain UNKNOWN")
    p0 = packet.get("change_history_fix_evidence", {}).get("wrong_year_p0", {})
    if p0.get("object_count") != 19 or len(p0.get("objects", [])) != 19:
        raise ValueError("P0 history set is not exact")
    if len(packet.get("role_checklist", [])) < 15:
        raise ValueError("role checklist is incomplete")


def render_json(packet: dict[str, Any]) -> str:
    return json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _md_escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def render_markdown(packet: dict[str, Any]) -> str:
    source = packet["source_freeze"]
    governance = packet["governance"]
    current = packet["current_content_to_review"]
    lines = [
        f"# Packet neutre 1SPE-SUITES — {packet['review_role']}",
        "",
        "> Entrée de revue uniquement. Ce document ne contient aucune zone de décision,",
        "> ne matérialise aucun reçu, ne change aucun statut, aucun atom FULL, aucune dette,",
        "> et ne vaut ni D7, ni validation visuelle finale, ni autorisation de publication.",
        "",
        "## Liaison et gouvernance",
        "",
        f"- SHA gelé : `{source['source_sha']}`",
        f"- Ensemble : `{source['chapter_object_set_digest']}` — 161 objets",
        f"- Contrat : `{governance['contract_state']}`",
        f"- Capture de décision : `{governance['decision_capture']}`",
        f"- État humain : `{governance['human_review_state']}`",
        f"- QCM owner/granularity : `{governance['qcm_gate_owner']}` / `{governance['qcm_gate_granularity']}`",
        "",
        "## Index",
        "",
        "1. CURRENT CONTENT TO REVIEW — 161 sources et PDF dérivés",
        "2. Programme MENE2602917A — 15 atomes obligatoires",
        "3. QCM — 21 questions",
        "4. Remédiation — 8 boucles / 13 sources",
        "5. CHANGE HISTORY / FIX EVIDENCE — 19 objets P0 et 7 classes scientifiques",
        "6. Checklist de rôle",
        "",
        "## CURRENT CONTENT TO REVIEW",
        "",
        "### PDF dérivés disponibles",
        "",
        "| Variante | Chemin | Pages | SHA-256 | Usage |",
        "|---|---|---:|---|---|",
    ]
    for row in current["chapter_pdfs"]:
        lines.append(
            f"| `{row['variant']}` | `{row['path']}` | {row['pages']} | `{row['sha256']}` | `{row['use']}` |"
        )
    lines.extend(
        [
            "",
            "Limites : ces PDF sont des aides locales non suivies, sans index exact objet→page,",
            "et ne prouvent ni release, ni D7, ni layout global du manuel. Le contenu source courant",
            "reste l'autorité de revue.",
            "",
            "### Inventaire exact des 161 sources",
            "",
            "| Objet | Type | Statut courant | Chemin | SHA-256 source | Blob Git |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in current["objects"]:
        lines.append(
            f"| `{row['object_id']}` | `{row['object_type']}` | `{row['status']}` | "
            f"`{row['path']}` | `sha256:{row['source_sha256']}` | `{row['git_blob_sha1']}` |"
        )
    lines.extend(
        [
            "",
            "## Programme MENE2602917A — 15 atomes obligatoires",
            "",
            "FULL reste `0/15` : ce packet n'autorise aucune transition.",
            "",
            "| Atom | Capacité | Ancre officielle | Formulation | État contenu | Science | Pédagogie | Assessment |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in packet["programme_mapping"]["mandatory_atoms"]:
        lines.append(
            f"| `{row['atom_id']}` | `{row['contract_capacity']}` | `{row['official_page_or_anchor']}` | "
            f"{_md_escape(row['official_wording_or_short_paraphrase'])} | `{row['coverage_status']}` | "
            f"`{row['scientific_state']}` | `{row['pedagogical_state']}` | `{row['assessment_alignment_state']}` |"
        )
    lines.extend(
        [
            "",
            "## QCM — contenu courant à revoir",
            "",
            f"État humain source : `{packet['qcm_review_material']['human_state']}`. Owner et granularité : `UNKNOWN`.",
            "",
            "| Q | Capacité | Difficulté | Clé déclarée | Solution indépendante | Source |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in packet["qcm_review_material"]["questions"]:
        lines.append(
            f"| `{row['question_id']}` | `{row['capacity']}` | `{row['difficulty']}` | "
            f"`{row['declared_answer']}` | {_md_escape(row['independent_solution'])} | "
            f"`{row['source_path']}` / `sha256:{row['source_sha256']}` |"
        )
    remediation = packet["remediation_review_material"]
    lines.extend(
        [
            "",
            "## Remédiation — contenu courant à revoir",
            "",
            f"- Boucles requises/machine-validées : `{remediation['required_capacity_loops']}/{remediation['machine_validated_capacity_loops']}`",
            f"- Sources : `{remediation['source_count']}`",
            f"- Couples exercice/correction internes : `{remediation['exercise_correction_pairs']}`",
            "- Ces nombres sont des preuves machine, pas une conclusion humaine.",
            "",
            "| Objet | Chemin | SHA-256 |",
            "|---|---|---|",
        ]
    )
    for row in remediation["sources"]:
        lines.append(
            f"| `{row['object_id']}` | `{row['path']}` | `sha256:{row['source_sha256']}` |"
        )
    history = packet["change_history_fix_evidence"]
    p0 = history["wrong_year_p0"]
    lines.extend(
        [
            "",
            "## CHANGE HISTORY / FIX EVIDENCE",
            "",
            "Cette section facilite la contre-vérification des corrections. Elle ne remplace pas",
            "la revue du contenu courant ci-dessus.",
            "",
            f"### P0 wrong-year — {p0['object_count']} objets / {p0['claim_count']} passages",
            "",
            "| Objet | Chemin | Avant | Courant gelé | Claims réécrits/conservés | Patch |",
            "|---|---|---|---|---:|---|",
        ]
    )
    for row in p0["objects"]:
        rewrites = sum(
            claim["classification"] == "REWRITE_TO_1SPE" for claim in row["before_claims"]
        )
        kept = sum(
            claim["classification"] == "KEEP_AS_IS" for claim in row["before_claims"]
        )
        lines.append(
            f"| `{row['object_id']}` | `{row['path']}` | `{row['before_source_sha256']}` | "
            f"`{row['current_frozen_source_sha256']}` | {rewrites}/{kept} | `{row['before_after_patch_digest']}` |"
        )
    lines.extend(["", "### Sept autres classes scientifiques", ""])
    for row in history["other_scientific_corrections"]:
        refs = "; ".join(f"`{path}`" for path in row["evidence_paths"])
        lines.append(f"- `{row['class_id']}` — {row['review_question']} Preuves : {refs}")
    lines.extend(["", f"## Checklist — {packet['review_role']}", ""])
    for item in packet["role_checklist"]:
        refs = "; ".join(f"`{ref}`" for ref in item["evidence_refs"])
        lines.append(f"{item['item_id']}. {item['review_question']} Références : {refs}")
    lines.extend(
        [
            "",
            "## Fin du packet neutre",
            "",
            "La décision et son éventuelle matérialisation restent hors de ce packet tant que le",
            "contrat de gouvernance est incomplet. Aucun champ de signature, choix ou transition",
            "n'est fourni ici.",
        ]
    )
    return "\n".join(lines) + "\n"


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    packets = build_packets()
    expected = {}
    for role, packet in packets.items():
        json_path, md_path = OUTPUTS[role]
        expected[json_path] = render_json(packet)
        expected[md_path] = render_markdown(packet)
    if args.check:
        stale = [
            str(path.relative_to(ROOT))
            for path, content in expected.items()
            if not path.exists() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            raise SystemExit("stale neutral packet outputs: " + ", ".join(stale))
        print("two neutral packets current")
        return 0
    for path, content in expected.items():
        _atomic_write(path, content)
    print("wrote two neutral packets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
