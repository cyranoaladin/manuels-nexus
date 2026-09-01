from __future__ import annotations

import importlib.util
import json
from itertools import combinations
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_current_review_debt_partition.py"
ARTIFACT = ROOT / "audit" / "CURRENT_REVIEW_DEBT_PARTITION.json"


def _module():
    spec = importlib.util.spec_from_file_location(
        "build_current_review_debt_partition", SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_partition_is_exact_disjoint_and_keeps_review_provenance() -> None:
    payload = _module().build_partition(ROOT)

    assert payload["current_review_debt_count"] == 2325
    assert payload["unknown_count"] == 0
    assert payload["pairwise_intersections"] == []
    assert payload["union_equals_current_review_debt"] is True

    components = payload["components"]
    assert components["TSPE_GEO_NEW_40"]["count"] == 40
    assert components["TSPE_GEO_REWRITTEN_STALE_APPROVAL_5"]["count"] == 5
    assert components["RESIDUAL_TRUE_NEW_13"]["count"] == 13
    assert components["TRIGO_OPTIONAL_EXTENSION_REQUALIFICATION_STALE_3"][
        "count"
    ] == 3
    # Le suffixe numerique de ces composants est le LABEL de la decision qui
    # les a ouverts, pas un compte vivant. `A4_METHOD_QUALIFIED_CURRENT_3` est
    # tombe a zero : ses trois fiches methodes ADGK ont ete reecrites, donc
    # leur qualification est perimee et elles sont imputees au registre du lot
    # couple -- une seule fois, jamais aux deux.
    assert components["A4_METHOD_QUALIFIED_CURRENT_3"]["count"] == 0
    assert (
        components["A4_METHOD_REQUALIFICATION_STALE_83"]["count"]
        + components["A4_METHOD_QUALIFIED_CURRENT_3"]["count"]
        + components["TRIGO_OPTIONAL_EXTENSION_REQUALIFICATION_STALE_3"]["count"]
        == payload["non_counting_aliases_and_aggregates"][
            "PREVIOUSLY_QUALIFIED_ACTIVE_DEBT_89"
        ]["count"]
    )
    coupled = json.loads(
        (ROOT / "audit/NSI_COUPLED_ALGORITHMICS_REVIEW_DEBT.json").read_text(
            encoding="utf-8"
        )
    )
    assert (
        components["NSI_COUPLED_NEW_32"]["count"]
        + components["NSI_COUPLED_REWRITTEN_PREVIOUSLY_MACHINE_VERIFIED_4"]["count"]
        + components["NSI_COUPLED_REWRITTEN"]["count"]
        + components["NSI_COUPLED_DECLARATION_CHANGED"]["count"]
        == coupled["count"]
    )

    for name, component in components.items():
        assert component["count"] == len(component["fingerprints"]), name
        assert component["count"] == len(component["objects"]), name
        assert component["fingerprints_digest"].startswith("sha256:")
        assert component["object_keys_digest"].startswith("sha256:")
        assert component["object_ids_digest"].startswith("sha256:")

    sets = {
        name: set(component["fingerprints"])
        for name, component in components.items()
    }
    for left, right in combinations(sorted(sets), 2):
        assert sets[left].isdisjoint(sets[right]), (left, right)

    aliases = payload["non_counting_aliases_and_aggregates"]
    assert aliases["PENDING_HUMAN_REVIEW_13"]["alias_of"] == [
        "RESIDUAL_TRUE_NEW_13"
    ]
    assert aliases["PENDING_HUMAN_REVIEW_13"]["contributes_to_union"] is False
    historical = aliases["HISTORICAL_PENDING_UNQUALIFIED_13_LABEL"]
    assert historical["refers_to"] == ["RESIDUAL_TRUE_NEW_13"]
    assert historical["semantic_alias_valid"] is False
    assert historical["current_qualification_state"] == (
        "PENDING_QUALIFIED_OPEN_DEBT"
    )
    # 86 depuis que les trois fiches ADGK sont imputees au lot couple.
    assert aliases["PREVIOUSLY_QUALIFIED_ACTIVE_DEBT_89"]["count"] == 86
    assert aliases["PREVIOUSLY_QUALIFIED_ACTIVE_DEBT_89"]["aggregate_of"] == [
        "A4_METHOD_REQUALIFICATION_STALE_83",
        "A4_METHOD_QUALIFIED_CURRENT_3",
        "TRIGO_OPTIONAL_EXTENSION_REQUALIFICATION_STALE_3",
    ]
    assert aliases["TSPE_GEO_REVIEW_PACKET_45"]["count"] == 45
    assert aliases["TSPE_GEO_REVIEW_PACKET_45"]["aggregate_of"] == [
        "TSPE_GEO_NEW_40",
        "TSPE_GEO_REWRITTEN_STALE_APPROVAL_5",
    ]
    assert aliases["TSPE_GEO_REVIEW_PACKET_45"]["provenance_counts"] == {
        "NEW": 40,
        "REWRITTEN_STALE_APPROVAL": 5,
    }
    assert aliases["NSI_COUPLED_REVIEW_PACKET_36"]["count"] == coupled["count"]
    assert (
        sum(aliases["NSI_COUPLED_REVIEW_PACKET_36"]["provenance_counts"].values())
        == coupled["count"]
    )
    # Le paquet nomme les provenances dans SON vocabulaire (`NEW`), le
    # registre dans le sien (`CREATED`) ; classe par classe, ils comptent la
    # meme chose.
    provenance = aliases["NSI_COUPLED_REVIEW_PACKET_36"]["provenance_counts"]
    origins = coupled["counts_by_origin"]
    assert provenance["NEW"] == origins["CREATED"]
    for shared in (
        "REWRITTEN",
        "REWRITTEN_PREVIOUSLY_MACHINE_VERIFIED",
        "DECLARATION_CHANGED_SEMANTICS_IDENTICAL",
    ):
        assert provenance[shared] == origins[shared], shared
    assert aliases["OTHER_CURRENT_REVIEW_DEBT"]["count"] == 2267


def test_committed_partition_is_reproducible() -> None:
    expected = _module().build_partition(ROOT)
    assert json.loads(ARTIFACT.read_text(encoding="utf-8")) == expected


def _write_ledger_manifest(root: Path, module, *, omit: Path | None = None) -> None:
    for relative in module.LEDGERS:
        if relative == omit:
            continue
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps({"artifact_type": "BLOCKING_REVIEW_DEBT_LEDGER"}),
            encoding="utf-8",
        )


def test_blocking_review_debt_ledger_manifest_fails_closed(tmp_path: Path) -> None:
    module = _module()
    _write_ledger_manifest(tmp_path, module)
    assert module._validated_ledger_manifest(tmp_path) == module.LEDGERS

    unexpected = tmp_path / "audit/UNKNOWN_REVIEW_DEBT_1.json"
    unexpected.write_text(
        json.dumps({"artifact_type": "BLOCKING_REVIEW_DEBT_LEDGER"}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="registre.*inattendu"):
        module._validated_ledger_manifest(tmp_path)

    unexpected.unlink()
    missing = module.LEDGERS[0]
    (tmp_path / missing).unlink()
    with pytest.raises(ValueError, match="registre.*absent"):
        module._validated_ledger_manifest(tmp_path)
