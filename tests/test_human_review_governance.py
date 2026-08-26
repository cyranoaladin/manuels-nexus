"""Tests de mutation du contrat de revue humaine (audit/HUMAN_REVIEW_GOVERNANCE.yaml).

Les identifiants A a K reprennent exactement la section 17 de la decision de
gouvernance. Chaque test prouve qu'une machine ne peut ni rendre un verdict, ni
faire beneficier un objet d'une approbation qui ne le couvre pas.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import human_review_governance as g  # noqa: E402

CHAPTER = "1SPE-SUITES"


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def policy() -> dict:
    return g.load_policy(ROOT)


@pytest.fixture(scope="module")
def scope() -> g.ChapterScope:
    return g.build_scope(CHAPTER, ROOT)


@pytest.fixture(scope="module")
def packets(scope: g.ChapterScope, policy: dict) -> dict[str, dict]:
    review_a, review_b = g.roles_for(scope.discipline, policy)
    return {
        review_a: g.build_packet(scope, review_a, policy, [], ROOT),
        review_b: g.build_packet(scope, review_b, policy, [], ROOT),
    }


def make_receipt(
    scope: g.ChapterScope,
    packet: dict,
    policy: dict,
    *,
    role: str,
    reviewer_name: str,
    identity: str,
    verdict: str = "APPROVED",
    blocking_findings: list | None = None,
    comments: list | None = None,
) -> dict:
    """Construit un recu conforme : c'est le transcript d'un verdict humain."""

    findings = blocking_findings or []
    attestation = policy["attestation"]["machine_format"].format(
        chapter_id=scope.chapter_id,
        object_set_digest=scope.object_set_digest,
        packet_digest=packet["packet_digest"],
        review_role=role,
        verdict=verdict,
    )
    return {
        "human_review_receipt_schema_version": 1,
        "review_id": f"{scope.chapter_id}-{role}-0001",
        "chapter_id": scope.chapter_id,
        "manual_id": scope.manual_id,
        "review_role": role,
        "reviewer_name": reviewer_name,
        "reviewer_identity_reference": identity,
        "reviewer_is_human": True,
        "review_timestamp": "2026-08-26T10:00:00+02:00",
        "verdict": verdict,
        "repository_source_sha": g.repository_source_sha(ROOT),
        "semantic_review_digest": scope.semantic_review_digest,
        "review_render_digest": packet["review_render_digest"],
        "object_set_digest": scope.object_set_digest,
        "object_count": scope.object_count,
        "programme_authority_digest": scope.programme_authority_digest,
        "packet_digest": packet["packet_digest"],
        "comments": comments or [],
        "blocking_findings": findings,
        "attestation_text": " ".join(attestation.split()),
    }


@pytest.fixture
def receipt_pair(scope: g.ChapterScope, packets: dict, policy: dict) -> tuple[dict, dict]:
    review_a, review_b = g.roles_for(scope.discipline, policy)
    first = make_receipt(
        scope,
        packets[review_a],
        policy,
        role=review_a,
        reviewer_name="Nadia Belhadj",
        identity="personne:ert-1042",
    )
    second = make_receipt(
        scope,
        packets[review_b],
        policy,
        role=review_b,
        reviewer_name="Yann Ferreira",
        identity="personne:ert-2087",
    )
    second["review_id"] = f"{scope.chapter_id}-{review_b}-0001"
    return first, second


# --------------------------------------------------------------------------
# Fondations deterministes
# --------------------------------------------------------------------------


def test_digests_are_deterministic(scope: g.ChapterScope) -> None:
    other = g.build_scope(CHAPTER, ROOT)
    assert other.object_set_digest == scope.object_set_digest
    assert other.semantic_review_digest == scope.semantic_review_digest
    assert other.programme_authority_digest == scope.programme_authority_digest


def test_semantic_payload_excludes_non_semantic_noise(scope: g.ChapterScope) -> None:
    blob = g.canonical_json(scope.semantic_payload())
    assert str(ROOT) not in blob, "aucun chemin absolu dans le digest semantique"
    for forbidden in ("run_id", "generated_at", "timestamp", "cwd"):
        assert forbidden not in blob
    for entry in scope.objects:
        assert "status" not in entry.meta
    assert "statut" not in scope.contract


def test_assembly_replication_matches_real_assembler(scope: g.ChapterScope) -> None:
    """L'ordre d'assemblage du digest est celui de l'assembleur reel."""

    scripts_dir = ROOT / "Mathematiques" / "manuel-maths" / "scripts"
    spec = importlib.util.spec_from_file_location(
        "_real_assembler", scripts_dir / "assemble_manuel.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(scripts_dir))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(scripts_dir))

    chapter_dir = g.chapter_directory(CHAPTER, ROOT)
    types = {
        chapter_dir / entry.path.split(f"{CHAPTER}/", 1)[1]: entry.object_type
        for entry in scope.objects
    }
    for variant in ("eleve", "professeur"):
        replicated = g.assembly_sequence(chapter_dir, scope.rules, variant, types)
        assert replicated == module.collect_chapter(chapter_dir, variant)


def test_valid_receipt_pair_is_accepted(
    scope: g.ChapterScope, packets: dict, policy: dict, receipt_pair: tuple[dict, dict]
) -> None:
    first, second = receipt_pair
    g.validate_receipt(first, scope, packets[first["review_role"]], policy, ROOT)
    g.validate_receipt(second, scope, packets[second["review_role"]], policy, ROOT)
    g.assert_independent_reviews(first, second)


# --------------------------------------------------------------------------
# A : meme humain pour A et B => FAIL
# --------------------------------------------------------------------------


def test_A_same_human_for_both_roles_fails(receipt_pair: tuple[dict, dict]) -> None:
    first, second = receipt_pair
    second["reviewer_name"] = first["reviewer_name"]
    second["reviewer_identity_reference"] = first["reviewer_identity_reference"]
    with pytest.raises(g.HumanReviewViolation, match="meme identite humaine"):
        g.assert_independent_reviews(first, second)


def test_A_same_role_twice_is_not_two_reviews(receipt_pair: tuple[dict, dict]) -> None:
    first, second = receipt_pair
    second["review_role"] = first["review_role"]
    with pytest.raises(g.HumanReviewViolation, match="meme role"):
        g.assert_independent_reviews(first, second)


# --------------------------------------------------------------------------
# B : agent IA comme reviewer => FAIL
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "identity"),
    [
        ("Codex", "agent:codex"),
        ("Claude", "assistant:claude-opus"),
        ("GitHub Copilot", "copilot:workspace"),
        ("Nadia Belhadj", "bot:review-runner"),
        ("automation service", "personne:ert-1042"),
        ("GPT-5 reviewer", "personne:ert-1042"),
    ],
)
def test_B_machine_reviewer_is_refused(
    scope: g.ChapterScope, packets: dict, policy: dict, name: str, identity: str
) -> None:
    role, _ = g.roles_for(scope.discipline, policy)
    receipt = make_receipt(
        scope, packets[role], policy, role=role, reviewer_name=name, identity=identity
    )
    with pytest.raises(g.HumanReviewViolation, match="non humaine"):
        g.validate_receipt(receipt, scope, packets[role], policy, ROOT)


def test_B_reviewer_is_human_flag_cannot_be_false(
    scope: g.ChapterScope, packets: dict, policy: dict
) -> None:
    role, _ = g.roles_for(scope.discipline, policy)
    receipt = make_receipt(
        scope,
        packets[role],
        policy,
        role=role,
        reviewer_name="Nadia Belhadj",
        identity="personne:ert-1042",
    )
    receipt["reviewer_is_human"] = False
    with pytest.raises(g.HumanReviewViolation):
        g.validate_receipt(receipt, scope, packets[role], policy, ROOT)


# --------------------------------------------------------------------------
# C : mauvais object_set_digest => FAIL
# --------------------------------------------------------------------------


def test_C_wrong_object_set_digest_fails(
    scope: g.ChapterScope, packets: dict, policy: dict, receipt_pair: tuple[dict, dict]
) -> None:
    receipt, _ = receipt_pair
    receipt["object_set_digest"] = "sha256:" + "0" * 64
    with pytest.raises(g.HumanReviewViolation, match="object_set_digest"):
        g.validate_receipt(receipt, scope, packets[receipt["review_role"]], policy, ROOT)


def test_C_wrong_object_count_fails(
    scope: g.ChapterScope, packets: dict, policy: dict, receipt_pair: tuple[dict, dict]
) -> None:
    receipt, _ = receipt_pair
    receipt["object_count"] = scope.object_count + 5
    with pytest.raises(g.HumanReviewViolation, match="object_count"):
        g.validate_receipt(receipt, scope, packets[receipt["review_role"]], policy, ROOT)


# --------------------------------------------------------------------------
# D : mauvaise semantic_review_digest => FAIL
# --------------------------------------------------------------------------


def test_D_wrong_semantic_review_digest_fails(
    scope: g.ChapterScope, packets: dict, policy: dict, receipt_pair: tuple[dict, dict]
) -> None:
    receipt, _ = receipt_pair
    receipt["semantic_review_digest"] = "sha256:" + "1" * 64
    with pytest.raises(g.HumanReviewViolation, match="semantic_review_digest"):
        g.validate_receipt(receipt, scope, packets[receipt["review_role"]], policy, ROOT)


# --------------------------------------------------------------------------
# E : mauvais packet digest => FAIL
# --------------------------------------------------------------------------


def test_E_wrong_packet_digest_fails(
    scope: g.ChapterScope, packets: dict, policy: dict, receipt_pair: tuple[dict, dict]
) -> None:
    receipt, _ = receipt_pair
    receipt["packet_digest"] = "sha256:" + "2" * 64
    with pytest.raises(g.HumanReviewViolation, match="packet_digest"):
        g.validate_receipt(receipt, scope, packets[receipt["review_role"]], policy, ROOT)


def test_E_packet_digest_covers_controls(
    scope: g.ChapterScope, packets: dict, policy: dict
) -> None:
    role, _ = g.roles_for(scope.discipline, policy)
    mutated = copy.deepcopy(packets[role])
    mutated["minimum_controls"] = mutated["minimum_controls"][:-1]
    assert g.packet_digest(mutated, policy) != packets[role]["packet_digest"]


def test_E_packet_digest_ignores_non_semantic_provenance(
    scope: g.ChapterScope, packets: dict, policy: dict
) -> None:
    role, _ = g.roles_for(scope.discipline, policy)
    mutated = copy.deepcopy(packets[role])
    mutated["repository_source_sha"] = "0" * 40
    assert g.packet_digest(mutated, policy) == packets[role]["packet_digest"]


# --------------------------------------------------------------------------
# F : APPROVED avec blocking_findings => FAIL
# --------------------------------------------------------------------------


def test_F_approved_with_blocking_findings_fails(
    scope: g.ChapterScope, packets: dict, policy: dict
) -> None:
    role, _ = g.roles_for(scope.discipline, policy)
    receipt = make_receipt(
        scope,
        packets[role],
        policy,
        role=role,
        reviewer_name="Nadia Belhadj",
        identity="personne:ert-1042",
        blocking_findings=[
            {
                "finding_id": "F-001",
                "object_ref": scope.object_ids[0],
                "severity": "P0",
                "description": "Arrondi incoherent.",
            }
        ],
    )
    with pytest.raises(g.HumanReviewViolation, match="APPROVED interdit"):
        g.validate_receipt(receipt, scope, packets[role], policy, ROOT)


def test_F_changes_requested_requires_identifiable_findings(
    scope: g.ChapterScope, packets: dict, policy: dict
) -> None:
    role, _ = g.roles_for(scope.discipline, policy)
    receipt = make_receipt(
        scope,
        packets[role],
        policy,
        role=role,
        reviewer_name="Nadia Belhadj",
        identity="personne:ert-1042",
        verdict="CHANGES_REQUESTED",
        blocking_findings=[],
    )
    with pytest.raises(g.HumanReviewViolation, match="CHANGES_REQUESTED"):
        g.validate_receipt(receipt, scope, packets[role], policy, ROOT)


def test_F_changes_requested_with_findings_is_accepted(
    scope: g.ChapterScope, packets: dict, policy: dict
) -> None:
    role, _ = g.roles_for(scope.discipline, policy)
    receipt = make_receipt(
        scope,
        packets[role],
        policy,
        role=role,
        reviewer_name="Nadia Belhadj",
        identity="personne:ert-1042",
        verdict="CHANGES_REQUESTED",
        blocking_findings=[
            {
                "finding_id": "F-001",
                "object_ref": scope.object_ids[0],
                "severity": "P1",
                "description": "Hypothese manquante.",
            }
        ],
    )
    g.validate_receipt(receipt, scope, packets[role], policy, ROOT)


# --------------------------------------------------------------------------
# G / I : mutation reelle des sources => STALE
# --------------------------------------------------------------------------


@pytest.fixture
def mutable_root(tmp_path: Path) -> Path:
    """Racine isolee : chapitre copie, outillage partage par lien symbolique."""

    root = tmp_path / "repo"
    (root / "Mathematiques" / "manuel-maths" / "chapitres").mkdir(parents=True)
    (root / "audit").mkdir(parents=True)
    manual = root / "Mathematiques" / "manuel-maths"
    (manual / "scripts").symlink_to(ROOT / "Mathematiques" / "manuel-maths" / "scripts")
    # Le referentiel est copie et non lie : les tests de mapping programme
    # doivent pouvoir le muter sans toucher au depot.
    shutil.copytree(
        ROOT / "Mathematiques" / "manuel-maths" / "referentiel",
        manual / "referentiel",
    )
    for name in (
        "OFFICIAL_PROGRAM_AUTHORITY_2026_2027.yaml",
        "OFFICIAL_AUTHORITIES_2026_2027.json",
        "HUMAN_REVIEW_GOVERNANCE.yaml",
    ):
        if (ROOT / "audit" / name).exists():
            (root / "audit" / name).symlink_to(ROOT / "audit" / name)
    (root / "audit" / "schemas").symlink_to(ROOT / "audit" / "schemas")
    shutil.copytree(
        g.chapter_directory(CHAPTER, ROOT), manual / "chapitres" / CHAPTER
    )
    return root


def test_G_semantic_source_change_makes_receipt_stale(
    mutable_root: Path, policy: dict
) -> None:
    before = g.build_scope(CHAPTER, mutable_root)
    packet = g.build_packet(before, g.roles_for(before.discipline, policy)[0], policy, [], ROOT)
    receipt = make_receipt(
        before,
        packet,
        policy,
        role=packet["review_role"],
        reviewer_name="Nadia Belhadj",
        identity="personne:ert-1042",
    )
    assert g.receipt_freshness(receipt, before)["content_state"] == g.CONTENT_CURRENT

    target = mutable_root / before.objects[0].path
    target.write_text(
        target.read_text(encoding="utf-8") + "\n% correction scientifique\n",
        encoding="utf-8",
    )

    after = g.build_scope(CHAPTER, mutable_root)
    assert after.object_set_digest == before.object_set_digest
    assert after.semantic_review_digest != before.semantic_review_digest
    assert g.receipt_freshness(receipt, after)["content_state"] == g.CONTENT_STALE


def test_G_status_promotion_alone_does_not_invalidate_the_receipt(
    mutable_root: Path,
) -> None:
    before = g.build_scope(CHAPTER, mutable_root)
    target = mutable_root / before.objects[0].path
    text = target.read_text(encoding="utf-8")
    target.write_text(
        text.replace('"status": "generated"', '"status": "verified"', 1), encoding="utf-8"
    )
    after = g.build_scope(CHAPTER, mutable_root)
    assert after.semantic_review_digest == before.semantic_review_digest


def test_I_qcm_added_after_review_makes_receipt_stale(
    mutable_root: Path, policy: dict
) -> None:
    before = g.build_scope(CHAPTER, mutable_root)
    packet = g.build_packet(before, g.roles_for(before.discipline, policy)[0], policy, [], ROOT)
    receipt = make_receipt(
        before,
        packet,
        policy,
        role=packet["review_role"],
        reviewer_name="Nadia Belhadj",
        identity="personne:ert-1042",
    )

    qcm_path = mutable_root / "Mathematiques/manuel-maths/chapitres" / CHAPTER / "qcm" / f"{CHAPTER}-QCM.json"
    payload = json.loads(qcm_path.read_text(encoding="utf-8"))
    payload["questions"].append(
        {
            "id": "Q99",
            "capacite": "C1",
            "enonce": "Question ajoutee apres la revue.",
            "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
            "correcte": "A",
            "diagnostics": {},
        }
    )
    qcm_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    after = g.build_scope(CHAPTER, mutable_root)
    assert after.semantic_review_digest != before.semantic_review_digest
    assert g.receipt_freshness(receipt, after)["content_state"] == g.CONTENT_STALE
    assert "Q99" in " ".join(g.qcm_question_ids(CHAPTER, mutable_root))


# --------------------------------------------------------------------------
# H : changement style-only => contenu CURRENT, visuel STALE
# --------------------------------------------------------------------------


def test_H_style_only_change_keeps_content_and_stales_visual(
    scope: g.ChapterScope, packets: dict, policy: dict
) -> None:
    role, _ = g.roles_for(scope.discipline, policy)
    receipt = make_receipt(
        scope,
        packets[role],
        policy,
        role=role,
        reviewer_name="Nadia Belhadj",
        identity="personne:ert-1042",
    )
    assert g.classify_change(["gabarits/nexus-charte-v6.sty"]) == "STYLE_ONLY"
    assert g.classify_change(["gabarits/nexus.cls", "gabarits/a.sty"]) == "STYLE_ONLY"

    freshness = g.receipt_freshness(receipt, scope, current_render_digest="sha256:" + "3" * 64)
    assert freshness["content_state"] == g.CONTENT_CURRENT
    assert freshness["visual_state"] == g.RENDER_STALE


def test_H_a_tex_change_is_never_classified_style_only() -> None:
    assert g.classify_change(["gabarits/x.sty", "chapitres/1SPE-SUITES/cours/a.tex"]) == (
        "SEMANTIC_CANDIDATE"
    )


def test_render_digest_is_independent_from_semantic_digest(
    scope: g.ChapterScope, policy: dict
) -> None:
    with_render = g.build_packet(
        scope, g.roles_for(scope.discipline, policy)[0], policy, ["logo.png"], ROOT
    )
    without_render = g.build_packet(
        scope, g.roles_for(scope.discipline, policy)[0], policy, [], ROOT
    )
    assert with_render["review_render_digest"] != without_render["review_render_digest"]
    assert with_render["semantic_review_digest"] == without_render["semantic_review_digest"]
    assert with_render["render_evidence"] == "PRESENT"
    assert without_render["render_evidence"] == "ABSENT"


# --------------------------------------------------------------------------
# J : objet externe au frozen set => aucun benefice
# --------------------------------------------------------------------------


def test_J_finding_outside_frozen_set_is_refused(
    scope: g.ChapterScope, packets: dict, policy: dict
) -> None:
    role, _ = g.roles_for(scope.discipline, policy)
    receipt = make_receipt(
        scope,
        packets[role],
        policy,
        role=role,
        reviewer_name="Nadia Belhadj",
        identity="personne:ert-1042",
        verdict="CHANGES_REQUESTED",
        blocking_findings=[
            {
                "finding_id": "F-001",
                "object_ref": "1SPE-EXPONENTIELLE-EX-001",
                "severity": "P0",
                "description": "Objet d'un autre chapitre.",
            }
        ],
    )
    with pytest.raises(g.HumanReviewViolation, match="hors ensemble gele"):
        g.validate_receipt(receipt, scope, packets[role], policy, ROOT)


def test_J_foreign_chapter_object_is_absent_from_the_packet(
    scope: g.ChapterScope, packets: dict
) -> None:
    identifiers = set(scope.object_ids)
    for packet in packets.values():
        listed = {entry["object_id"] for entry in packet["objects"]}
        assert listed == identifiers
        assert all(entry["path"].split("/")[-3] == CHAPTER for entry in packet["objects"])


def test_J_a_new_object_changes_the_object_set_digest(
    mutable_root: Path,
) -> None:
    before = g.build_scope(CHAPTER, mutable_root)
    added = (
        mutable_root
        / "Mathematiques/manuel-maths/chapitres"
        / CHAPTER
        / "exercices"
        / f"{CHAPTER}-EX-900.tex"
    )
    meta = {
        "id": f"{CHAPTER}-EX-900",
        "chapitre": CHAPTER,
        "type_objet": "exercice",
        "capacites_codes": ["C1"],
        "status": "generated",
    }
    added.write_text(
        "% META: " + json.dumps(meta) + "\n\\begin{exercice}{X}{1}{5}\nA\n\\end{exercice}\n",
        encoding="utf-8",
    )
    after = g.build_scope(CHAPTER, mutable_root)
    assert after.object_count == before.object_count + 1
    assert after.object_set_digest != before.object_set_digest
    assert after.semantic_review_digest != before.semantic_review_digest


# --------------------------------------------------------------------------
# K : verdict inconnu => FAIL
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "verdict",
    [
        "AUTO_APPROVED",
        "APPROVED_BY_MACHINE",
        "ASSUMED_APPROVED",
        "APPROVED_WITHOUT_REVIEW",
        "pass",
        "ok",
    ],
)
def test_K_unknown_verdict_fails(
    scope: g.ChapterScope, packets: dict, policy: dict, verdict: str
) -> None:
    role, _ = g.roles_for(scope.discipline, policy)
    receipt = make_receipt(
        scope,
        packets[role],
        policy,
        role=role,
        reviewer_name="Nadia Belhadj",
        identity="personne:ert-1042",
    )
    receipt["verdict"] = verdict
    with pytest.raises(g.HumanReviewViolation):
        g.validate_receipt(receipt, scope, packets[role], policy, ROOT)


def test_K_forbidden_verdicts_are_declared_in_the_policy(policy: dict) -> None:
    assert set(policy["verdicts"]) == {"APPROVED", "CHANGES_REQUESTED", "REJECTED"}
    for forbidden in policy["forbidden_verdicts"]:
        assert forbidden not in policy["verdicts"]


# --------------------------------------------------------------------------
# Gate QCM et etat du chapitre
# --------------------------------------------------------------------------


def test_qcm_gate_requires_both_roles_approved(
    scope: g.ChapterScope, policy: dict, receipt_pair: tuple[dict, dict]
) -> None:
    first, second = receipt_pair
    pending = g.evaluate_state(CHAPTER, policy, ROOT, scope=scope, receipts=[first])
    assert pending["qcm_human_approval"] == "PENDING"
    assert pending["human_content_approval"] == "PENDING"

    satisfied = g.evaluate_state(
        CHAPTER, policy, ROOT, scope=scope, receipts=[first, second]
    )
    assert satisfied["qcm_human_approval"] == "SATISFIED"
    assert satisfied["independence"] is True


def test_qcm_gate_stays_pending_when_one_role_requests_changes(
    scope: g.ChapterScope, policy: dict, receipt_pair: tuple[dict, dict]
) -> None:
    first, second = receipt_pair
    second["verdict"] = "CHANGES_REQUESTED"
    state = g.evaluate_state(CHAPTER, policy, ROOT, scope=scope, receipts=[first, second])
    assert state["qcm_human_approval"] == "PENDING"
    assert state["human_content_approval"] == "PENDING"


def test_qcm_questions_are_listed_in_both_packets(
    scope: g.ChapterScope, packets: dict
) -> None:
    expected = g.qcm_question_ids(CHAPTER, ROOT)
    assert expected
    for packet in packets.values():
        assert packet["qcm_question_ids"] == expected


def test_state_is_pending_unassigned_without_any_receipt(policy: dict) -> None:
    state = g.evaluate_state(CHAPTER, policy, ROOT, receipts=[])
    assert state["review_a"]["state"] == "PENDING_UNASSIGNED"
    assert state["review_b"]["state"] == "PENDING_UNASSIGNED"
    assert state["qcm_human_approval"] == "PENDING"
    assert state["human_content_approval"] == "PENDING"
    assert state["publication_approval"] is False


def test_stale_receipt_never_counts_as_approved(
    scope: g.ChapterScope, policy: dict, receipt_pair: tuple[dict, dict]
) -> None:
    first, second = receipt_pair
    second["semantic_review_digest"] = "sha256:" + "4" * 64
    state = g.evaluate_state(CHAPTER, policy, ROOT, scope=scope, receipts=[first, second])
    assert state["review_b"]["state"] == g.CONTENT_STALE
    assert state["human_content_approval"] == "PENDING"


def test_content_approval_never_implies_visual_or_publication(
    scope: g.ChapterScope, policy: dict, receipt_pair: tuple[dict, dict]
) -> None:
    first, second = receipt_pair
    state = g.evaluate_state(CHAPTER, policy, ROOT, scope=scope, receipts=[first, second])
    assert state["human_content_approval"] == "APPROVED"
    assert state["visual_authority"] == "INDEPENDENT_D7_GATE"
    assert state["publication_approval"] is False


# --------------------------------------------------------------------------
# Section 18 : 1SPE-SUITES reste PENDING
# --------------------------------------------------------------------------


def test_1SPE_SUITES_has_no_recorded_receipt(policy: dict) -> None:
    assert g.load_receipts(CHAPTER, ROOT) == []
    state = g.evaluate_state(CHAPTER, policy, ROOT)
    assert state["review_a"]["state"] == "PENDING_UNASSIGNED"
    assert state["review_b"]["state"] == "PENDING_UNASSIGNED"


def test_1SPE_SUITES_objects_all_remain_generated(scope: g.ChapterScope) -> None:
    chapter_dir = g.chapter_directory(CHAPTER, ROOT)
    statuses = {
        g._read_meta(path)["status"] for path in sorted(chapter_dir.rglob("*.tex"))
    }
    assert statuses == {"generated"}
    assert scope.object_count == 161


def test_1SPE_SUITES_contract_remains_draft() -> None:
    import yaml

    contract = yaml.safe_load(
        (g.chapter_directory(CHAPTER, ROOT) / "contrat.yaml").read_text(encoding="utf-8")
    )
    assert contract["statut"] == "draft"


# --------------------------------------------------------------------------
# Roles et acteurs
# --------------------------------------------------------------------------


def test_math_and_nsi_roles_are_declared(policy: dict) -> None:
    assert g.roles_for("MATH", policy) == (
        "EXPERT_MATHEMATIQUE",
        "EXPERT_PROGRAMME_PEDAGOGIE",
    )
    assert g.roles_for("NSI", policy) == ("EXPERT_NSI", "EXPERT_PROGRAMME_PEDAGOGIE")


def test_role_outside_the_discipline_contract_is_refused(
    scope: g.ChapterScope, packets: dict, policy: dict
) -> None:
    role, _ = g.roles_for(scope.discipline, policy)
    receipt = make_receipt(
        scope,
        packets[role],
        policy,
        role=role,
        reviewer_name="Nadia Belhadj",
        identity="personne:ert-1042",
    )
    receipt["review_role"] = "EXPERT_NSI"
    with pytest.raises(g.HumanReviewViolation, match="hors contrat"):
        g.validate_receipt(receipt, scope, packets[role], policy, ROOT)


def test_attestation_must_bind_chapter_object_set_and_packet(
    scope: g.ChapterScope, packets: dict, policy: dict, receipt_pair: tuple[dict, dict]
) -> None:
    receipt, _ = receipt_pair
    receipt["attestation_text"] = "Je valide ce chapitre."
    with pytest.raises(g.HumanReviewViolation, match="attestation_text"):
        g.validate_receipt(receipt, scope, packets[receipt["review_role"]], policy, ROOT)


def test_packet_carries_the_minimum_controls_of_the_contract(
    packets: dict, policy: dict
) -> None:
    disciplinary = packets["EXPERT_MATHEMATIQUE"]
    pedagogical = packets["EXPERT_PROGRAMME_PEDAGOGIE"]
    assert disciplinary["minimum_controls"] == policy["packet_a_controls"]["minimum_controls"]
    assert pedagogical["minimum_controls"] == policy["packet_b_controls"]["minimum_controls"]
    assert disciplinary["verdict"] is None
    assert pedagogical["verdict"] is None
    assert disciplinary["reviewer_assignment"] == "PENDING_UNASSIGNED"


# --------------------------------------------------------------------------
# Conformite du contrat lui-meme
# --------------------------------------------------------------------------


def test_policy_matches_its_declared_schema(policy: dict) -> None:
    from jsonschema import Draft202012Validator, FormatChecker

    schema = json.loads(
        (ROOT / policy["schema_ref"]).read_text(encoding="utf-8")
    )
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(policy),
        key=lambda error: list(error.path),
    )
    assert not errors, "; ".join(f"{list(e.path)}: {e.message}" for e in errors)


def test_every_mutation_test_of_the_contract_has_a_test_here(policy: dict) -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    for entry in policy["mutation_tests"]:
        assert f"def test_{entry['id']}_" in source, entry


def test_status_transitions_never_promote_without_a_human_receipt(policy: dict) -> None:
    transitions = policy["status_transitions"]
    prohibited = set(transitions["prohibited_without_human_receipt"])
    for row in transitions["table"]:
        if row["next_canonical_status"] in prohibited:
            assert row["required_human_receipts"], row
    for row in transitions["contract_transitions"]:
        assert row["required_human_receipts"], row


def test_full_requires_both_human_approvals_and_the_qcm_gate(policy: dict) -> None:
    criteria = set(policy["full_atom_criteria"])
    assert {
        "human_expert_disciplinary_approved",
        "human_programme_pedagogy_approved",
        "qcm_human_gate_satisfied",
    } <= criteria
    assert policy["any_pending_criterion_forbids_full"] is True


# --------------------------------------------------------------------------
# Reconciliation de l'ensemble gele declare par l'humain
# --------------------------------------------------------------------------


RECONCILIATION_PATH = ROOT / "audit" / "HUMAN_REVIEW_FROZEN_SET_RECONCILIATION.json"


@pytest.fixture(scope="module")
def reconciliation() -> dict:
    return json.loads(RECONCILIATION_PATH.read_text(encoding="utf-8"))


def test_reconciliation_records_the_real_machine_values(
    scope: g.ChapterScope, reconciliation: dict
) -> None:
    """L'artefact supersede garde ses chiffres d'origine, sans etre reecrit."""

    computed = reconciliation["computed_by_machine"]
    assert computed["object_count"] == 156, "l'artefact garde ses chiffres d'origine"
    assert computed["repository_source_sha"].startswith("761508d9")
    assert scope.object_count == 161, "l'arbre courant porte le gel canonique"
    assert reconciliation["correction_notice"]


def test_declared_frozen_set_does_not_reproduce(
    scope: g.ChapterScope, reconciliation: dict
) -> None:
    """La valeur humaine declaree n'est pas reproductible : l'ecart reste ouvert."""

    declared = reconciliation["declared_by_human"]
    assert declared["object_count"] == scope.object_count == 161, (
        "la valeur declaree se reproduit desormais sur l'arbre canonique"
    )
    assert reconciliation["status"] == "SUPERSEDED_ROOT_CAUSE_FOUND"
    assert reconciliation["superseded_by"] == (
        "audit/1SPE_SUITES_REVIEW_FREEZE_CORRECTION_DECISION.json"
    )
    assert reconciliation["correction_notice"]


def test_no_receipt_may_be_recorded_while_the_frozen_set_is_unreconciled(
    reconciliation: dict,
) -> None:
    resolved = {"RESOLVED", "CURRENT_FROZEN_SET"}
    if reconciliation["status"] not in resolved:
        assert g.load_receipts(CHAPTER, ROOT) == [], (
            "un recu a ete enregistre alors que l'ensemble gele n'est pas reconcilie"
        )


def test_emitted_packets_match_the_current_scope(policy: dict) -> None:
    """Les packets emis sur l'arbre courant doivent en refleter l'etat exact."""

    chapter = "1SPE-VARIABLES-ALEATOIRES"
    scope = g.build_scope(chapter, ROOT)
    directory = g.chapter_review_dir(chapter, ROOT)
    for letter, role in (("A", "EXPERT_MATHEMATIQUE"), ("B", "EXPERT_PROGRAMME_PEDAGOGIE")):
        stored = json.loads(
            (directory / f"packet-{letter}-{role}.json").read_text(encoding="utf-8")
        )
        assert stored["object_set_digest"] == scope.object_set_digest
        assert stored["semantic_review_digest"] == scope.semantic_review_digest
        assert stored["reviewer_assignment"] == "PENDING_UNASSIGNED"
        assert stored["verdict"] is None


def test_two_approvals_from_the_same_identity_never_satisfy_the_gate(
    scope: g.ChapterScope, policy: dict, receipt_pair: tuple[dict, dict]
) -> None:
    """Le gate derive doit refuser l'auto-approbation par une seule personne."""

    first, second = receipt_pair
    second["reviewer_name"] = first["reviewer_name"]
    second["reviewer_identity_reference"] = first["reviewer_identity_reference"]
    state = g.evaluate_state(CHAPTER, policy, ROOT, scope=scope, receipts=[first, second])
    assert state["independence"] is False
    assert state["qcm_human_approval"] == "PENDING"
    assert state["human_content_approval"] == "PENDING"


def test_only_the_latest_receipt_of_a_role_is_authoritative(
    scope: g.ChapterScope, policy: dict, receipt_pair: tuple[dict, dict]
) -> None:
    """Un recu corrige ne mute pas l'ancien : le plus recent fait autorite."""

    first, second = receipt_pair
    superseded = copy.deepcopy(first)
    superseded["review_id"] = first["review_id"] + "-bis"
    superseded["review_timestamp"] = "2026-08-20T09:00:00+02:00"
    superseded["verdict"] = "CHANGES_REQUESTED"
    superseded["blocking_findings"] = [
        {
            "finding_id": "F-001",
            "object_ref": scope.object_ids[0],
            "severity": "P1",
            "description": "corrigee depuis",
        }
    ]
    state = g.evaluate_state(
        CHAPTER, policy, ROOT, scope=scope, receipts=[superseded, first, second]
    )
    assert state["review_a"]["review_id"] == first["review_id"]
    assert state["review_a"]["state"] == "APPROVED"


def test_a_chapter_without_qcm_reports_the_gate_as_not_applicable(
    scope: g.ChapterScope, policy: dict, receipt_pair: tuple[dict, dict], monkeypatch
) -> None:
    """Sans question de QCM, le gate n'est pas eternellement PENDING."""

    monkeypatch.setattr(g, "qcm_question_ids", lambda *args, **kwargs: [])
    first, second = receipt_pair
    state = g.evaluate_state(CHAPTER, policy, ROOT, scope=scope, receipts=[first, second])
    assert state["qcm_human_approval"] == "NOT_APPLICABLE"
    assert state["human_content_approval"] == "APPROVED"


def test_loading_an_assembler_leaves_no_shared_module_cached(scope: g.ChapterScope) -> None:
    """Les assembleurs importent `common` par nom court : ce nom est partage.

    Le laisser en cache ferait resoudre l'assembleur NSI vers le `common` des
    mathematiques, et le manifeste 1NSI serait cherche sous manuel-maths.
    """

    for name in ("common", "pdf_integrity", "assemble"):
        sys.modules.pop(name, None)
    g.build_scope(CHAPTER, ROOT)
    for name in ("common", "pdf_integrity", "assemble"):
        assert name not in sys.modules, name


def test_transitively_included_objects_belong_to_the_frozen_set() -> None:
    """Un objet insere par \\input est publie : il doit etre couvert.

    1SPE-VARIABLES-ALEATOIRES porte 5 objets sous cours/experimentations/ qui
    n'entrent dans le manuel que par l'\\input d'un objet de premier niveau.
    Les omettre laisserait du contenu publie hors du perimetre approuve.
    """

    varalea = g.build_scope("1SPE-VARIABLES-ALEATOIRES", ROOT)
    nested = [entry for entry in varalea.objects if entry.included_by]
    assert len(nested) == 5
    assert {entry.object_type for entry in nested} == {"experimentation", "algorithme"}
    for entry in nested:
        assert "cours/experimentations/" in entry.path
        assert entry.teacher_visible, entry.object_id
    assert varalea.unassembled_object_ids() == []
    assert varalea.object_count == 155


def test_an_object_reachable_by_no_assembly_path_is_reported(
    mutable_root: Path,
) -> None:
    """Un objet ni assemble ni inclus doit apparaitre comme non assemble."""

    orphan = (
        mutable_root
        / "Mathematiques/manuel-maths/chapitres"
        / CHAPTER
        / "cours"
        / "annexes"
        / "99_orphelin.tex"
    )
    orphan.parent.mkdir(parents=True, exist_ok=True)
    meta = {
        "id": f"{CHAPTER}-CR-999",
        "chapitre": CHAPTER,
        "type_objet": "cours",
        "status": "generated",
    }
    orphan.write_text("% META: " + json.dumps(meta) + "\nOrphelin.\n", encoding="utf-8")
    scope = g.build_scope(CHAPTER, mutable_root)
    assert f"{CHAPTER}-CR-999" in scope.unassembled_object_ids()


# --------------------------------------------------------------------------
# Section 5 : l'exclusion est une allowlist fermee, verrouillee par le schema
# --------------------------------------------------------------------------


def test_the_exclusion_allowlist_is_declared_in_the_contract(policy: dict) -> None:
    allowlist = policy["digests"]["semantic_review_digest"][
        "governance_exclusion_allowlist"
    ]
    assert allowlist["meta_fields"] == ["status"]
    assert allowlist["contract_fields"] == ["statut"]
    assert allowlist["closed"] is True
    assert allowlist["widening_requires"]


def test_the_code_excludes_exactly_the_allowlisted_fields(policy: dict) -> None:
    """Le code ne peut pas exclure un champ que le contrat n'a pas declare."""

    allowlist = policy["digests"]["semantic_review_digest"][
        "governance_exclusion_allowlist"
    ]
    assert g.GOVERNANCE_META_FIELDS == frozenset(allowlist["meta_fields"])
    assert g.GOVERNANCE_CONTRACT_FIELDS == frozenset(allowlist["contract_fields"])


def test_the_schema_forbids_widening_the_allowlist() -> None:
    """Ajouter une exclusion exige de modifier le schema, pas seulement le code."""

    from jsonschema import Draft202012Validator

    schema = json.loads(
        (ROOT / "audit/schemas/v1/human-review-governance.schema.json").read_text(
            encoding="utf-8"
        )
    )
    widened = copy.deepcopy(g.load_policy(ROOT))
    widened["digests"]["semantic_review_digest"]["governance_exclusion_allowlist"][
        "meta_fields"
    ] = ["status", "capacites_codes"]
    assert list(Draft202012Validator(schema).iter_errors(widened))


def test_no_meta_field_outside_the_allowlist_is_silently_dropped(
    scope: g.ChapterScope, policy: dict
) -> None:
    """Toute autre donnee de META doit peser sur le digest semantique."""

    excluded = g.GOVERNANCE_META_FIELDS
    entry = next(item for item in scope.objects if item.object_type == "exercice")
    raw = json.loads(
        g.META_RE.search(
            (ROOT / entry.path).read_text(encoding="utf-8")
        ).group(1)
    )
    reference = scope.semantic_review_digest
    for key in raw:
        mutated = copy.deepcopy(scope)
        mutated.objects = [copy.deepcopy(item) for item in scope.objects]
        target = next(item for item in mutated.objects if item.object_id == entry.object_id)
        if key in excluded:
            assert key not in target.meta, key
            continue
        assert key in target.meta, f"{key} absent du digest sans etre allowlist"
        target.meta = {**target.meta, key: "___mutation___"}
        assert mutated.semantic_review_digest != reference, key


def test_status_only_change_keeps_the_semantic_digest(mutable_root: Path) -> None:
    before = g.build_scope(CHAPTER, mutable_root)
    target = mutable_root / before.objects[0].path
    text = target.read_text(encoding="utf-8")
    target.write_text(
        text.replace('"status": "generated"', '"status": "approved"', 1), encoding="utf-8"
    )
    assert g.build_scope(CHAPTER, mutable_root).semantic_review_digest == (
        before.semantic_review_digest
    )


def test_contract_status_only_change_keeps_the_semantic_digest(
    mutable_root: Path,
) -> None:
    before = g.build_scope(CHAPTER, mutable_root)
    contract = mutable_root / "Mathematiques/manuel-maths/chapitres" / CHAPTER / "contrat.yaml"
    contract.write_text(
        contract.read_text(encoding="utf-8").replace("statut: draft", "statut: valide", 1),
        encoding="utf-8",
    )
    assert g.build_scope(CHAPTER, mutable_root).semantic_review_digest == (
        before.semantic_review_digest
    )


def test_capacity_change_changes_the_semantic_digest(mutable_root: Path) -> None:
    before = g.build_scope(CHAPTER, mutable_root)
    target = mutable_root / next(
        item.path for item in before.objects if item.capabilities
    )
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace('"C3"', '"C5"', 1), encoding="utf-8")
    assert g.build_scope(CHAPTER, mutable_root).semantic_review_digest != (
        before.semantic_review_digest
    )


def test_programme_mapping_change_changes_the_semantic_digest(
    mutable_root: Path,
) -> None:
    before = g.build_scope(CHAPTER, mutable_root)
    assert before.programme_mapping, "le chapitre doit porter un mapping programme"
    referentiel = (
        mutable_root / "Mathematiques/manuel-maths/referentiel/capacites_1SPE_SUITES.json"
    )
    payload = json.loads(referentiel.read_text(encoding="utf-8"))
    payload["capacites"][0]["libelle_bo"] += " (reformulation)"
    referentiel.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    assert g.build_scope(CHAPTER, mutable_root).semantic_review_digest != (
        before.semantic_review_digest
    )


def test_visibility_change_changes_the_semantic_digest(scope: g.ChapterScope) -> None:
    """Rendre un corrige visible par l'eleve doit periment toute review."""

    reference = scope.semantic_review_digest
    mutated = copy.deepcopy(scope)
    target = next(item for item in mutated.objects if item.object_type == "corrige")
    assert target.student_visible is False
    target.student_visible = True
    assert mutated.semantic_review_digest != reference


def test_correction_change_changes_the_semantic_digest(mutable_root: Path) -> None:
    before = g.build_scope(CHAPTER, mutable_root)
    correction = mutable_root / next(
        item.path for item in before.objects if item.object_type == "corrige"
    )
    correction.write_text(
        correction.read_text(encoding="utf-8") + "\n% valeur numerique corrigee\n",
        encoding="utf-8",
    )
    assert g.build_scope(CHAPTER, mutable_root).semantic_review_digest != (
        before.semantic_review_digest
    )


def test_the_nsi_role_carries_its_human_authorisation(policy: dict) -> None:
    entry = policy["roles"]["NSI"]
    authorisation = entry["human_authorisation"]
    assert authorisation["authorised"] is True
    assert authorisation["constitutes_no_nsi_review"] is True
    assert entry["review_a"] == "EXPERT_NSI"
    assert entry["review_b"] == "EXPERT_PROGRAMME_PEDAGOGIE"


# --------------------------------------------------------------------------
# Gel 1SPE-SUITES : la premisse du double comptage est refutee
# --------------------------------------------------------------------------


FREEZE_DECISION_PATH = (
    ROOT / "audit" / "1SPE_SUITES_REVIEW_FREEZE_CORRECTION_DECISION.json"
)


def _meta_ids_at(sha: str) -> dict[str, str]:
    import subprocess

    listing = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", sha, "--",
         "Mathematiques/manuel-maths/chapitres/1SPE-SUITES"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split()
    found: dict[str, str] = {}
    for path in listing:
        if not path.endswith(".tex"):
            continue
        blob = subprocess.run(
            ["git", "show", f"{sha}:{path}"], cwd=ROOT, capture_output=True, text=True
        ).stdout
        for line in blob.splitlines():
            if line.startswith("% META: "):
                found[json.loads(line[8:])["id"]] = path
                break
    return found


def test_the_five_fr_r_sheets_appear_exactly_once(scope: g.ChapterScope) -> None:
    """Aucun double comptage : chaque FR-R est un objet unique de l'ensemble."""

    sheets = [item for item in scope.object_ids if "-FR-R" in item]
    assert sorted(sheets) == [f"1SPE-SUITES-FR-R{index}" for index in range(1, 6)]
    assert len(sheets) == len(set(sheets)) == 5
    assert len(scope.object_ids) == len(set(scope.object_ids))


def test_an_object_id_seen_through_two_roles_is_counted_once(
    scope: g.ChapterScope,
) -> None:
    """Un objet visible en eleve ET en professeur ne compte qu'une fois."""

    both = [
        item for item in scope.objects if item.student_visible and item.teacher_visible
    ]
    assert both, "le chapitre doit porter des objets visibles dans les deux variantes"
    identifiers = [item.object_id for item in both]
    assert len(identifiers) == len(set(identifiers))
    assert scope.object_count == len(set(scope.object_ids))


def test_the_declared_161_freeze_is_not_a_double_count() -> None:
    """161 et 156 comptent le meme chapitre a deux commits, pas deux fois les memes objets."""

    decision = json.loads(FREEZE_DECISION_PATH.read_text(encoding="utf-8"))
    assert decision["root_cause"]["double_counting"] is False
    assert decision["status"] == "RESOLVED_FREEZE_161_CANONICAL"

    head = _meta_ids_at("761508d923d74fd3d93fc055b3f3b1857fb251e1")
    declared = _meta_ids_at("c667f12b1792f31981b6b5894c8c604df1bce634")
    assert len(head) == 156
    assert len(declared) == 161
    assert set(head) < set(declared), "l'ecart doit etre strictement additif"

    added = sorted(set(declared) - set(head))
    assert added == [
        "1SPE-SUITES-CO-051",
        "1SPE-SUITES-CR-017",
        "1SPE-SUITES-EX-051",
        "1SPE-SUITES-ME-008",
        "1SPE-SUITES-RE-C8",
    ]
    recorded = {
        entry["object_id"]
        for entry in decision["evidence"][
            "objects_present_at_c667f12b_and_absent_at_761508d9"
        ]
    }
    assert recorded == set(added)


def test_no_receipt_exists_for_the_canonical_freeze() -> None:
    """Le gel est etabli ; la revue humaine reste entierement a faire."""

    assert g.load_receipts(CHAPTER, ROOT) == []
    state = json.loads(
        (
            ROOT
            / "audit/reviews/human/1SPE-SUITES/freeze-161-c667f12b/REVIEW_STATE.json"
        ).read_text(encoding="utf-8")
    )
    assert state["review_a"]["state"] == "PENDING_UNASSIGNED"
    assert state["review_b"]["state"] == "PENDING_UNASSIGNED"
    assert state["human_content_approval"] == "PENDING"


def test_capacity_c8_is_present_on_the_canonical_freeze(scope: g.ChapterScope) -> None:
    """Le gel canonique a 161 couvre la capacite C8 du programme 2026."""

    codes = {entry["code"] for entry in scope.contract["capacites"]}
    assert codes == {f"C{index}" for index in range(1, 9)}
    assert "C8" in codes
    covered = {
        capability
        for entry in scope.objects
        for capability in entry.capabilities
    }
    assert "C8" in covered
    implementing = {
        entry.object_id for entry in scope.objects if "C8" in entry.capabilities
    }
    # Les cinq objets de l'ecart 156 -> 161 portent tous C8 ; d'autres objets
    # deja presents ont ete rattaches a la capacite par la meme vague.
    assert {
        "1SPE-SUITES-CO-051",
        "1SPE-SUITES-CR-017",
        "1SPE-SUITES-EX-051",
        "1SPE-SUITES-ME-008",
        "1SPE-SUITES-RE-C8",
    } <= implementing
