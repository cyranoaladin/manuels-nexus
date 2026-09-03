"""Gate « une extension ne credite pas le programme obligatoire » : mutations.

Le gate ne vaut que s'il rougit quand un atome obligatoire n'est plus tenu
que par des objets d'extension optionnelle.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_mandatory_coverage_extension_independence as gate  # noqa: E402


def _reader(alignments: dict[str, str]):
    def read(source: str) -> tuple[str, str | None]:
        path = source.split("#", 1)[0]
        alignment = alignments.get(path, gate.ALIGNMENT_ORDINARY)
        return alignment, "fixture" if alignment == gate.ALIGNMENT_EXTENSION else None

    return read


# ---------------------------------------------------------------------------
# Verite courante
# ---------------------------------------------------------------------------
def test_no_mandatory_atom_is_credited_by_extension_only() -> None:
    payload = gate.build_payload()
    assert payload["summary"]["MANDATORY_COVERAGE_FROM_EXTENSION_ONLY"] == 0
    assert payload["extension_only_atoms"] == []
    assert payload["summary"]["MANDATORY_ATOMS"] > 0


def test_every_credited_source_resolves_on_disk() -> None:
    payload = gate.build_payload()
    assert payload["summary"]["CREDITED_SOURCES_MISSING_ON_DISK"] == 0
    assert payload["credited_sources_missing_on_disk"] == []


def test_the_two_coverage_artifacts_describe_the_same_mandatory_set() -> None:
    """`coverage_rows` refuse de travailler si les deux artefacts divergent."""

    rows = gate.coverage_rows()
    aggregate = json.loads(gate.COVERAGE_AGGREGATE.read_text(encoding="utf-8"))
    assert len(rows) == aggregate["summary"]["by_manual"][gate.MANUAL][
        "mandatory_atoms"
    ]


def test_the_extension_ledger_is_read_from_the_human_decision() -> None:
    declared = gate.declared_extension_sources()
    assert declared, "au moins une decision humaine declare une extension"
    for source, origin in declared.items():
        assert (ROOT / source).is_file()
        assert origin.startswith("audit/HUMAN_DECISION_")


def test_the_published_artifact_is_reproducible() -> None:
    payload = gate.build_payload()
    assert gate.JSON_TARGET.read_text(encoding="utf-8") == gate.render_json(payload)
    assert gate.MD_TARGET.read_text(encoding="utf-8") == gate.render_markdown(payload)
    assert gate.main(["--check"]) == 0


# ---------------------------------------------------------------------------
# Mutations
# ---------------------------------------------------------------------------
def test_mutation_an_atom_held_only_by_extensions_turns_the_gate_red() -> None:
    row = {
        "atom_id": "FIXTURE-001",
        "obligation_type": "MANDATORY_CAPACITY",
        "chapter": "FIXTURE",
        "contract_capacity": "FIXTURE-C1",
        "course_sources": ["a.tex"],
        "exercise_sources": ["b.tex"],
    }
    green = gate.evaluate([row], _reader({"a.tex": gate.ALIGNMENT_EXTENSION}))
    assert green["extension_only"] == []
    assert green["atoms"][0]["verdict"] == "CREDITED_BY_BOTH"

    red = gate.evaluate(
        [row],
        _reader(
            {
                "a.tex": gate.ALIGNMENT_EXTENSION,
                "b.tex": gate.ALIGNMENT_EXTENSION,
            }
        ),
    )
    assert len(red["extension_only"]) == 1
    assert red["atoms"][0]["verdict"] == "CREDITED_BY_EXTENSION_ONLY"


def test_mutation_flipping_a_real_credit_to_extension_turns_the_gate_red() -> None:
    """Sur la couverture reelle : si tout ce qui credite un atome devient une
    extension, l'atome bascule."""

    target = next(row for row in gate.coverage_rows() if gate.credited_sources(row))
    sources = {source.split("#", 1)[0] for _, source in gate.credited_sources(target)}
    flipped = gate.evaluate(
        [target], _reader({source: gate.ALIGNMENT_EXTENSION for source in sources})
    )
    assert len(flipped["extension_only"]) == 1


def test_mutation_an_uncredited_atom_is_never_counted_as_extension_only() -> None:
    """Une dette de contenu ne doit pas etre maquillee en violation."""

    row = {"atom_id": "FIXTURE-002", "course_sources": []}
    result = gate.evaluate([row], _reader({}))
    assert result["extension_only"] == []
    assert result["atoms"][0]["verdict"] == "NO_CREDITING_SOURCE"


def test_mutation_a_missing_credited_source_is_reported_not_swallowed() -> None:
    row = {"atom_id": "FIXTURE-003", "course_sources": ["nowhere/absent.tex"]}
    result = gate.evaluate([row], gate.alignment_reader({}))
    assert result["atoms"][0]["missing_credit_count"] == 1
    assert result["extension_only"] == []


def test_meta_alignment_alone_is_enough_to_mark_a_credit_as_extension() -> None:
    read = gate.alignment_reader({})
    declared = json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))
    assert declared["inputs"]["declared_extension_sources"] > 0
    for source in gate.declared_extension_sources():
        alignment, origin = read(source)
        assert alignment == gate.ALIGNMENT_EXTENSION
        assert origin
