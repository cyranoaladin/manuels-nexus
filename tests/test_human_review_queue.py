from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_human_review_queue.py"
ARTIFACT = ROOT / "audit/HUMAN_REVIEW_QUEUE.json"


def _module():
    spec = importlib.util.spec_from_file_location("build_human_review_queue", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_queue_is_exact_disjoint_and_current() -> None:
    payload = _module().build_queue()

    assert payload["status"] == "HUMAN_REVIEW_ACTION_REQUIRED"
    assert payload["approves_nothing"] is True

    # Les comptes ne sont pas ecrits en dur : ils sont REDERIVES des memes
    # entrees. Un nombre grave dans un test finit par mesurer le test, et non
    # la file -- il faut le recalculer depuis la dette, la preuve QCM et les
    # fermetures, exactement comme le producteur le fait.
    module = _module()
    partition = json.loads(
        (ROOT / "audit/CURRENT_REVIEW_DEBT_PARTITION.json").read_text(encoding="utf-8"))
    evidence = json.loads(
        (ROOT / "audit/QCM_INDEPENDENT_EVIDENCE_V2.json").read_text(encoding="utf-8"))
    reconciliation = json.loads(
        (ROOT / "audit/QCM_REVIEW_PROOF_RECONCILIATION.json").read_text(encoding="utf-8"))
    closure = json.loads(
        (ROOT / "audit/QCM_REVIEW_CLOSURE.json").read_text(encoding="utf-8"))
    renvoi_audit = json.loads(
        (ROOT / "audit/QCM_DIAGNOSTIC_RENVOI_AUDIT.json").read_text(encoding="utf-8"))
    decision = json.loads(
        (ROOT / "audit/TNSI_PROJET_ASSESSMENT_MODE.json").read_text(encoding="utf-8"))

    population_qcm = {
        f"{row['chapter']}/{row['question_id']}"
        for row in evidence["questions"]
        if row["evidence_status"] == "HUMAN_REVIEW_REQUIRED"
    }
    population_renvoi = {
        f"{row['chapter']}/{row['question_id']}"
        for row in reconciliation["proof_field_coverage_gaps"]
    }
    attendu = {
        "OBJECT_REVIEW": partition["current_review_debt_count"],
        "QCM_ANSWER_SEMANTICS": len(
            population_qcm - module._closed_by_machine_proof(closure)),
        "QCM_DIAGNOSTIC_RENVOI_SEMANTICS": len(
            population_renvoi - module._renvois_resolus(renvoi_audit)),
        "EDITORIAL_DECISION": (
            0 if decision.get("status") == "RESOLVED_BY_HUMAN_DECISION" else 1),
    }
    attendu["TOTAL"] = sum(attendu.values())
    assert payload["counts"] == attendu
    assert payload["pairwise_intersections"] == []
    assert payload["unknown_count"] == 0

    all_units: list[str] = []
    for item in payload["items"]:
        assert item["count"] == len(item["unit_ids"]), item["item_id"]
        assert item["set_digest"].startswith("sha256:")
        all_units.extend(item["unit_ids"])
    assert len(all_units) == len(set(all_units)) == payload["counts"]["TOTAL"]

    nsi = {
        item["item_id"]: item
        for item in payload["items"]
        if item["item_id"].startswith("NSI_COUPLED_")
    }
    # Les suffixes numeriques sont le LABEL de la decision d'origine ; les
    # comptes suivent le registre du lot couple. Ce qui est verrouille, c'est
    # que la file couvre EXACTEMENT le registre, sans doublon ni oubli.
    coupled = json.loads(
        (ROOT / "audit/NSI_COUPLED_ALGORITHMICS_REVIEW_DEBT.json").read_text(
            encoding="utf-8"
        )
    )
    assert sum(item["count"] for item in nsi.values()) == coupled["count"]
    assert nsi["NSI_COUPLED_NEW_32"]["count"] == coupled["counts_by_origin"]["CREATED"]
    assert nsi["NSI_COUPLED_REWRITTEN_PREVIOUSLY_MACHINE_VERIFIED_4"]["count"] == (
        coupled["counts_by_origin"]["REWRITTEN_PREVIOUSLY_MACHINE_VERIFIED"]
    )
    assert all(
        item["required_reviewers"] == [
            "EXPERT_NSI",
            "EXPERT_PROGRAMME_PEDAGOGIE",
        ]
        for item in nsi.values()
    )
    allowed_roles = {
        "EXPERT_MATHEMATIQUE",
        "EXPERT_NSI",
        "EXPERT_PROGRAMME_PEDAGOGIE",
    }
    for item in payload["items"]:
        for chapter, roles in item["required_reviewers_by_chapter"].items():
            assert set(roles) <= allowed_roles
            assert len(roles) == 2
            expected = (
                "EXPERT_NSI"
                if chapter.startswith(("1NSI-", "TNSI-"))
                else "EXPERT_MATHEMATIQUE"
            )
            assert roles == [expected, "EXPERT_PROGRAMME_PEDAGOGIE"]


def test_committed_queue_matches_producer() -> None:
    assert json.loads(ARTIFACT.read_text(encoding="utf-8")) == _module().build_queue()


def test_queue_rejects_count_list_divergence_and_duplicate_qcm_identity() -> None:
    module = _module()
    partition = json.loads(
        (ROOT / "audit/CURRENT_REVIEW_DEBT_PARTITION.json").read_text(
            encoding="utf-8"
        )
    )
    evidence = json.loads(
        (ROOT / "audit/QCM_INDEPENDENT_EVIDENCE_V2.json").read_text(
            encoding="utf-8"
        )
    )
    reconciliation = json.loads(
        (ROOT / "audit/QCM_REVIEW_PROOF_RECONCILIATION.json").read_text(
            encoding="utf-8"
        )
    )
    decision = json.loads(
        (ROOT / "audit/TNSI_PROJET_ASSESSMENT_MODE.json").read_text(
            encoding="utf-8"
        )
    )

    broken_partition = copy.deepcopy(partition)
    broken_partition["current_review_debt_count"] += 1
    with pytest.raises(ValueError, match="partition.*count"):
        module.build_queue(
            partition=broken_partition,
            evidence=evidence,
            reconciliation=reconciliation,
            decision=decision,
        )

    broken_evidence = copy.deepcopy(evidence)
    question = next(
        row
        for row in broken_evidence["questions"]
        if row["evidence_status"] == "HUMAN_REVIEW_REQUIRED"
    )
    broken_evidence["questions"].append(copy.deepcopy(question))
    with pytest.raises(ValueError, match="QCM.*dupliquée"):
        module.build_queue(
            partition=partition,
            evidence=broken_evidence,
            reconciliation=reconciliation,
            decision=decision,
        )


def test_queue_fails_closed_on_unknown_or_empty_input_identity() -> None:
    module = _module()
    partition = json.loads(
        (ROOT / "audit/CURRENT_REVIEW_DEBT_PARTITION.json").read_text(
            encoding="utf-8"
        )
    )
    evidence = json.loads(
        (ROOT / "audit/QCM_INDEPENDENT_EVIDENCE_V2.json").read_text(
            encoding="utf-8"
        )
    )
    reconciliation = json.loads(
        (ROOT / "audit/QCM_REVIEW_PROOF_RECONCILIATION.json").read_text(
            encoding="utf-8"
        )
    )
    decision = json.loads(
        (ROOT / "audit/TNSI_PROJET_ASSESSMENT_MODE.json").read_text(
            encoding="utf-8"
        )
    )

    unknown_partition = copy.deepcopy(partition)
    unknown_partition["unknown_count"] = 1
    with pytest.raises(ValueError, match="partition.*unknown"):
        module.build_queue(
            partition=unknown_partition,
            evidence=evidence,
            reconciliation=reconciliation,
            decision=decision,
        )

    unknown_evidence = copy.deepcopy(evidence)
    unknown_evidence["questions"][0]["evidence_status"] = "UNKNOWN"
    with pytest.raises(ValueError, match="statut QCM inconnu"):
        module.build_queue(
            partition=partition,
            evidence=unknown_evidence,
            reconciliation=reconciliation,
            decision=decision,
        )

    empty_identity = copy.deepcopy(evidence)
    empty_identity["questions"][0]["chapter"] = ""
    with pytest.raises(ValueError, match="identité QCM vide"):
        module.build_queue(
            partition=partition,
            evidence=empty_identity,
            reconciliation=reconciliation,
            decision=decision,
        )


# ══════════════════════════════════════════════════════════════════════════
# Fermeture QCM : ce qui sort de la file, et ce qui y reste
# ══════════════════════════════════════════════════════════════════════════
def _entrees_reelles():
    """Les entrees courantes, telles que le producteur les lit."""
    lire = lambda nom: json.loads((ROOT / nom).read_text(encoding="utf-8"))  # noqa: E731
    return {
        "partition": lire("audit/CURRENT_REVIEW_DEBT_PARTITION.json"),
        "evidence": lire("audit/QCM_INDEPENDENT_EVIDENCE_V2.json"),
        "reconciliation": lire("audit/QCM_REVIEW_PROOF_RECONCILIATION.json"),
        "decision": lire("audit/TNSI_PROJET_ASSESSMENT_MODE.json"),
        "closure": lire("audit/QCM_REVIEW_CLOSURE.json"),
        "renvoi_audit": lire("audit/QCM_DIAGNOSTIC_RENVOI_AUDIT.json"),
    }


def test_a_mechanical_proof_removes_the_unit_from_the_human_queue() -> None:
    """Une derivation executee sans voir la cle est une preuve, pas un avis."""
    module = _module()
    payload = module.build_queue()
    item = next(i for i in payload["items"] if i["item_id"] == "QCM_ANSWER_SEMANTICS")
    prouvees = module._closed_by_machine_proof(_entrees_reelles()["closure"])
    assert item["closed_by_machine_proof"] == len(prouvees)
    assert item["population"] == item["count"] + item["closed_by_machine_proof"]
    for unite in item["closed_unit_ids"]:
        assert unite not in item["unit_ids"]


def test_an_agent_review_never_removes_a_unit() -> None:
    """§25 : un agent n'approuve pas. Sa revue est jointe, la file demeure."""
    module = _module()
    payload = module.build_queue()
    item = next(i for i in payload["items"] if i["item_id"] == "QCM_ANSWER_SEMANTICS")
    relues = module._agent_reviewed(_entrees_reelles()["closure"])
    assert item["agent_review_is_not_an_approval"] is True
    assert item["agent_review_attached"] == item["count"]
    assert item["count"] == len(relues)
    assert item["release_blocking"] is True


def test_a_key_disagreement_refuses_to_close_anything() -> None:
    """Une fermeture qui contient un desaccord ne ferme rien du tout."""
    module = _module()
    entrees = _entrees_reelles()
    entrees["closure"] = copy.deepcopy(entrees["closure"])
    entrees["closure"]["summary"]["QCM_KEY_DISAGREEMENTS"] = 1
    with pytest.raises(ValueError, match="desaccord|désaccord"):
        module.build_queue(**entrees)


def test_a_question_without_declared_closure_is_refused() -> None:
    """Une question de la population sans etat de fermeture est un trou."""
    module = _module()
    entrees = _entrees_reelles()
    entrees["closure"] = copy.deepcopy(entrees["closure"])
    entrees["closure"]["questions"] = entrees["closure"]["questions"][:-1]
    with pytest.raises(ValueError, match="sans fermeture"):
        module.build_queue(**entrees)


def test_an_unresolved_renvoi_keeps_its_question_open() -> None:
    """Un seul renvoi non resolu laisse la question dans la file."""
    module = _module()
    entrees = _entrees_reelles()
    entrees["renvoi_audit"] = copy.deepcopy(entrees["renvoi_audit"])
    cible = entrees["renvoi_audit"]["renvois"][0]
    cible["state"] = "UNRESOLVED"
    resolus = module._renvois_resolus(entrees["renvoi_audit"])
    assert f"{cible['chapter']}/{cible['question_id']}" not in resolus


def test_a_broken_reference_refuses_to_close_the_renvois() -> None:
    module = _module()
    entrees = _entrees_reelles()
    entrees["renvoi_audit"] = copy.deepcopy(entrees["renvoi_audit"])
    entrees["renvoi_audit"]["summary"]["BROKEN_REMEDIATION_REFERENCES"] = 1
    with pytest.raises(ValueError, match="casse|cassé"):
        module.build_queue(**entrees)


def test_the_closure_artifacts_are_declared_as_inputs() -> None:
    """Ce qui ferme une unite doit etre tracable depuis la file."""
    payload = _module().build_queue()
    assert "audit/QCM_REVIEW_CLOSURE.json" in payload["source_inputs"]
    assert "audit/QCM_DIAGNOSTIC_RENVOI_AUDIT.json" in payload["source_inputs"]
    for empreinte in payload["source_inputs"].values():
        assert empreinte.startswith("sha256:")
