"""Gate « completude professeur » : verite courante, derivation, mutations.

Chaque metrique doit rougir quand on lui retire ce qu'elle pretend compter :
un corrige attendu, une cle de QCM, un bareme, l'etancheite eleve.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_teacher_completeness_metrics as gate  # noqa: E402


@pytest.fixture(scope="module")
def surface() -> gate.Surface:
    return gate.Surface(gate.MANUAL)


@pytest.fixture(scope="module")
def carriers() -> frozenset[str]:
    return gate.bareme_carrier_macros()


def clone(surface: gate.Surface) -> gate.Surface:
    other = copy.copy(surface)
    other.teacher = list(surface.teacher)
    other.student = list(surface.student)
    other.text = dict(surface.text)
    other.meta = {path: dict(meta) for path, meta in surface.meta.items()}
    other.student_set = set(surface.student)
    return other


def metric(payload: dict, name: str) -> dict:
    return next(row for row in payload["metrics"] if row["METRIC_NAME"] == name)


# ---------------------------------------------------------------------------
# Derivation
# ---------------------------------------------------------------------------
def test_the_correctable_types_are_derived_from_the_corpus(surface) -> None:
    types = surface.correctable_types()
    assert types
    for declared in types:
        assert any(
            surface.object_type(path) == declared
            and (
                surface.meta[path].get(gate.FORWARD_LINK)
                or surface.correction_of(path) is not None
            )
            for path in surface.teacher
        )


def test_the_bareme_carrier_is_resolved_in_the_charter(carriers) -> None:
    assert carriers
    charter = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in gate.CHARTER_ROOT.rglob("*")
        if path.suffix in {".cls", ".sty"}
    )
    for name in carriers:
        assert f"\\newcommand{{\\{name}}}" in charter


def test_no_expected_count_is_written_by_hand(surface, carriers) -> None:
    """Chaque EXPECTED se recalcule a partir de la surface publiee."""

    corrections = gate.correction_metric(surface)
    assert corrections["EXPECTED"] == sum(
        1
        for path in surface.teacher
        if surface.object_type(path) in surface.correctable_types()
    )
    baremes = gate.bareme_metric(surface, carriers)
    assert baremes["EXPECTED"] == len(gate.graded_objects(surface))


# ---------------------------------------------------------------------------
# Verite courante
# ---------------------------------------------------------------------------
def test_every_correctable_object_has_a_teacher_only_correction(surface) -> None:
    result = gate.correction_metric(surface)
    assert result["EXPECTED"] == result["OBSERVED"]
    assert result["gaps"] == []


def test_every_declared_qcm_answer_is_in_the_teacher_zone(surface) -> None:
    result = gate.qcm_key_metric(surface)
    assert result["EXPECTED"] == result["OBSERVED"]
    assert result["gaps"] == []


def test_the_student_variant_leaks_nothing(surface, carriers) -> None:
    for result in gate.student_leak_metrics(surface, carriers):
        assert result["OBSERVED"] == 0, result["METRIC_NAME"]


def test_the_bareme_debt_is_named_and_enumerated() -> None:
    """La dette de bareme est ouverte : elle doit rester visible et rouge."""

    payload = json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))
    result = metric(payload, "TEACHER_BAREME_PER_GRADED_OBJECT")
    assert result["GAP"] == result["EXPECTED"] - result["OBSERVED"]
    assert len(result["gaps"]) == result["GAP"]
    assert payload["summary"]["TEACHER_MISSING_REQUIRED_CONTENT"] == result["GAP"]
    assert payload["summary"]["GATE"] == ("PASS" if result["GAP"] == 0 else "FAIL")


def test_the_published_artifact_is_reproducible() -> None:
    payload = gate.build_payload()
    assert gate.JSON_TARGET.read_text(encoding="utf-8") == gate.render_json(payload)
    assert gate.MD_TARGET.read_text(encoding="utf-8") == gate.render_markdown(payload)


def test_the_pdf_is_only_secondary_evidence_and_is_bound_by_sha256() -> None:
    payload = json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))
    evidence = payload["pdf_secondary_evidence"]
    assert evidence["evidence_role"] == "SECONDARY_NON_AUTHORITATIVE"
    for document in evidence["documents"]:
        assert len(document["sha256"]) == 64
        assert (ROOT / document["path"]).is_file()


# ---------------------------------------------------------------------------
# Mutations
# ---------------------------------------------------------------------------
def test_mutation_removing_an_expected_correction_turns_the_gate_red(
    surface,
) -> None:
    """Retirer un corrige attendu doit faire rougir le gate."""

    mutated = clone(surface)
    target = next(
        path
        for path in mutated.teacher
        if mutated.object_type(path) in mutated.correctable_types()
        and mutated.correction_of(path) is not None
    )
    correction = mutated.correction_of(target)
    mutated.teacher = [path for path in mutated.teacher if path != correction]
    mutated.meta[target].pop(gate.FORWARD_LINK, None)
    result = gate.correction_metric(mutated)
    assert result["OBSERVED"] == result["EXPECTED"] - 1
    assert [gap["gap"] for gap in result["gaps"]] == ["NO_CORRECTION"]


def test_mutation_a_correction_published_to_students_turns_the_gate_red(
    surface, carriers
) -> None:
    mutated = clone(surface)
    correction = next(path for path in mutated.teacher if mutated.is_correction(path))
    mutated.student.append(correction)
    mutated.student_set.add(correction)
    leaks = gate.student_leak_metrics(mutated, carriers)
    corrections = next(
        row
        for row in leaks
        if row["METRIC_NAME"] == "STUDENT_VARIANT_CORRECTION_OBJECTS"
    )
    assert corrections["OBSERVED"] == 0, "is_correction ignore un objet cote eleve"
    result = gate.correction_metric(mutated)
    assert any(gap["gap"] == "CORRECTION_LEAKS_TO_STUDENT" for gap in result["gaps"])


def test_mutation_a_divergent_qcm_key_turns_the_gate_red(surface) -> None:
    mutated = clone(surface)
    target = next(
        path
        for path in mutated.teacher
        if sorted(path.parent.glob(f"{path.stem}.json"))
        and gate._QCM_KEY_ROW.search(gate._teacher_zone(mutated.text[path]))
    )
    text = mutated.text[target]
    row = gate._QCM_KEY_ROW.search(gate._teacher_zone(text))
    flipped = row.group(0).replace(
        f"\\textbf{{{row.group(2)}}}", "\\textbf{ZZ}"
    )
    mutated.text[target] = text.replace(row.group(0), flipped, 1)
    result = gate.qcm_key_metric(mutated)
    assert result["OBSERVED"] == result["EXPECTED"] - 1
    assert result["gaps"][0]["gap"] == "KEY_MISSING_OR_DIVERGENT"


def test_mutation_removing_a_bareme_carrier_turns_the_gate_red(
    surface, carriers
) -> None:
    mutated = clone(surface)
    baseline = gate.bareme_metric(mutated, carriers)
    target = next(
        path
        for path in gate.graded_objects(mutated)
        if any(
            f"\\{name}" in mutated.text[mutated.correction_of(path)]
            for name in carriers
            if mutated.correction_of(path) is not None
        )
    )
    correction = mutated.correction_of(target)
    text = mutated.text[correction]
    for name in carriers:
        text = text.replace(f"\\{name}", "\\textit")
    mutated.text[correction] = text
    result = gate.bareme_metric(mutated, carriers)
    assert result["OBSERVED"] == baseline["OBSERVED"] - 1


def test_mutation_a_bareme_carrier_visible_to_students_turns_the_gate_red(
    surface, carriers
) -> None:
    mutated = clone(surface)
    student = mutated.student[0]
    name = sorted(carriers)[0]
    mutated.text[student] = mutated.text[student] + f"\n\\{name}{{Q1 : 1 pt}}\n"
    leaks = gate.student_leak_metrics(mutated, carriers)
    result = next(
        row for row in leaks if row["METRIC_NAME"] == "STUDENT_VARIANT_BAREME_CARRIERS"
    )
    assert result["OBSERVED"] == 1


# ---------------------------------------------------------------------------
# Decoupage des zones conditionnelles
# ---------------------------------------------------------------------------
def test_the_teacher_zone_is_removed_from_the_student_view() -> None:
    text = (
        "avant\n\\ifnxVersionProfesseur\nsecret\n\\fi\napres\n"
    )
    assert "secret" not in gate.strip_teacher_zones(text)
    assert "avant" in gate.strip_teacher_zones(text)
    assert "apres" in gate.strip_teacher_zones(text)
    assert "secret" in gate._teacher_zone(text)


def test_a_nested_conditional_does_not_close_the_teacher_zone_early() -> None:
    text = (
        "avant\n\\ifnxVersionProfesseur\n\\ifnum1=1 x\\fi\nsecret\n\\fi\napres\n"
    )
    visible = gate.strip_teacher_zones(text)
    assert "secret" not in visible
    assert "apres" in visible
