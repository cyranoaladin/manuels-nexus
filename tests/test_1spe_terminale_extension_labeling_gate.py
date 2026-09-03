"""Gate « niveau Terminale etiquete » : verite courante et mutations.

Le gate ne vaut que s'il rougit quand on lui retire l'etiquette qu'il pretend
verifier. Chaque mecanisme de declaration reconnu a donc ici sa mutation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_terminale_extension_labeling_gate as gate  # noqa: E402
from manual_source_surface import (  # noqa: E402
    object_meta,
    published_union,
    read_meta,
    relative,
)


@pytest.fixture(scope="module")
def vocabulary() -> dict:
    return {
        "labels": gate.declared_extension_labels(gate.MANUAL),
        "macros": gate.optional_extension_macros(),
        "pattern": gate.wrong_level_pattern(gate.MANUAL),
    }


def classify(text: str, vocabulary: dict) -> list[dict]:
    return gate.classify_text(
        "fixture.tex",
        text,
        labels=vocabulary["labels"],
        macros=vocabulary["macros"],
        pattern=vocabulary["pattern"],
    )


def unlabeled(rows: list[dict]) -> list[dict]:
    return [row for row in rows if row["classification"] == gate.CLASS_UNLABELED]


# ---------------------------------------------------------------------------
# Le vocabulaire est derive, pas ecrit
# ---------------------------------------------------------------------------
def test_the_foreign_level_comes_from_the_assembler(vocabulary) -> None:
    pattern = vocabulary["pattern"]
    assert pattern.search("Vers la Terminale")
    assert not pattern.search("Première spécialité")


def test_the_out_of_track_macro_is_resolved_through_the_charter(vocabulary) -> None:
    assert vocabulary["macros"], "la charte doit exposer au moins un conteneur"
    for name in vocabulary["macros"]:
        assert f"\\{name}" in (
            ROOT / "gabarits/common/nexus-manuel.cls"
        ).read_text(encoding="utf-8")


def test_the_extension_labels_come_from_published_meta(vocabulary) -> None:
    declared = {
        read_meta(path).get("extension_label")
        for path in published_union(gate.MANUAL)
    }
    assert set(vocabulary["labels"]) <= {
        label.strip() for label in declared if isinstance(label, str) and label.strip()
    }


# ---------------------------------------------------------------------------
# Verite courante
# ---------------------------------------------------------------------------
def test_no_published_occurrence_is_unlabeled() -> None:
    payload = gate.build_payload()
    assert payload["summary"]["UNLABELED_WRONG_LEVEL_TERMINALE_CONTENT"] == 0
    assert payload["summary"]["PUBLISHED_WRONG_LEVEL_OCCURRENCES"] > 0
    assert payload["unlabeled_occurrences"] == []


def test_the_published_artifact_is_reproducible() -> None:
    payload = gate.build_payload()
    assert gate.JSON_TARGET.read_text(encoding="utf-8") == gate.render_json(payload)
    assert gate.MD_TARGET.read_text(encoding="utf-8") == gate.render_markdown(payload)
    assert gate.main(["--check"]) == 0


def test_every_declared_extension_object_is_traced_to_its_source() -> None:
    payload = json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))
    published = {relative(path) for path in published_union(gate.MANUAL)}
    for row in payload["occurrences"]:
        assert row["source_path"] in published


# ---------------------------------------------------------------------------
# Mutations
# ---------------------------------------------------------------------------
def test_mutation_an_occurrence_outside_every_block_turns_the_gate_red(
    vocabulary,
) -> None:
    """Une occurrence ajoutee hors de toute portee declaree doit rougir."""

    source = ROOT / (
        "Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/cours/"
        "10_C1_definition_exponentielle.tex"
    )
    text = source.read_text(encoding="utf-8")
    assert unlabeled(classify(text, vocabulary)) == []
    mutated = text + "\nCe critere est exigible en Terminale et evalue ici.\n"
    assert len(unlabeled(classify(mutated, vocabulary))) == 1


def test_mutation_content_pushed_just_after_a_labelled_block_turns_red(
    vocabulary,
) -> None:
    """Sortir le contenu d'un bloc etiquete, meme d'une ligne, doit rougir."""

    source = ROOT / (
        "Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/cours/"
        "10_C1_definition_exponentielle.tex"
    )
    text = source.read_text(encoding="utf-8")
    spans = gate.label_spans(text, vocabulary["labels"])
    assert spans and all(span["scope_resolved"] for span in spans)
    first = min(spans, key=lambda span: span["start"])
    inside = (
        text[: first["end"] - 1]
        + " On admet la limite de Terminale."
        + text[first["end"] - 1 :]
    )
    assert unlabeled(classify(inside, vocabulary)) == []
    outside = (
        text[: first["end"]]
        + "\n\nOn admet la limite de Terminale.\n"
        + text[first["end"] :]
    )
    assert len(unlabeled(classify(outside, vocabulary))) == 1


def test_mutation_removing_the_object_level_alignment_turns_red(vocabulary) -> None:
    """Le meme corps, avec et sans `programme_alignment`, ne se classe pas pareil."""

    declared = vocabulary["labels"][0]
    body = "On admet ici la limite etudiee en Terminale.\n"
    header = (
        '% META: {{"id": "X", "type_objet": "corrige", '
        '"programme_alignment": "{alignment}", "extension_label": "{label}"}}\n'
    )
    labelled = header.format(alignment="OPTIONAL_EXTENSION", label=declared) + body
    assert [row["classification"] for row in classify(labelled, vocabulary)] == [
        gate.MECHANISM_META
    ]
    stripped = header.format(alignment="MANDATORY_PROGRAMME", label=declared) + body
    assert len(unlabeled(classify(stripped, vocabulary))) == 1


def test_the_two_object_declarations_are_redundant_in_the_current_corpus(
    vocabulary,
) -> None:
    """Aucune occurrence courante ne repose sur la seule META de l'objet.

    Le mecanisme objet et le mecanisme bloc se recouvrent : c'est une defense
    en profondeur, et cela se prouve plutot que de se supposer.
    """

    for path in published_union(gate.MANUAL):
        text = path.read_text(encoding="utf-8")
        if object_meta(text).get("programme_alignment") != "OPTIONAL_EXTENSION":
            continue
        mask = gate.comment_mask(text)
        spans = gate.macro_spans(text, vocabulary["macros"]) + gate.label_spans(
            text, vocabulary["labels"]
        )
        for match in vocabulary["pattern"].finditer(text):
            if mask[match.start()]:
                continue
            assert any(
                span["start"] <= match.start() < span["end"] for span in spans
            ), f"{relative(path)}:{gate.line_of(text, match.start())}"


def test_mutation_removing_the_charter_macro_turns_red(vocabulary) -> None:
    """Sortir un paragraphe de la boite hors parcours doit rougir."""

    source = ROOT / (
        "Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/cours/"
        "13_C4_extremums.tex"
    )
    text = source.read_text(encoding="utf-8")
    assert [row["classification"] for row in classify(text, vocabulary)] == [
        gate.MECHANISM_MACRO
    ]
    mutated = text.replace("\\approfondissement{", "{", 1)
    assert len(unlabeled(classify(mutated, vocabulary))) == 1


def test_mutation_a_parenthetical_that_carries_content_is_not_a_deferral(
    vocabulary,
) -> None:
    """Le renvoi de niveau ne couvre que la parenthese qui s'y arrete."""

    deferral = "Le maximum exact (par derivation en Terminale) vaut $3$.\n"
    assert unlabeled(classify(deferral, vocabulary)) == []
    smuggled = (
        "Le maximum exact (par derivation en Terminale : on pose $f'(x)=0$ "
        "puis on resout) vaut $3$.\n"
    )
    assert len(unlabeled(classify(smuggled, vocabulary))) == 1


def test_mutation_an_undeclared_label_does_not_open_a_scope(vocabulary) -> None:
    """Une etiquette inventee, absente des META, n'ouvre aucune portee."""

    declared = vocabulary["labels"][0]
    template = (
        "\\begin{center}\\textbf{%s}\\end{center}\n"
        "\\demonstration{On admet le theoreme de Terminale.}\n"
    )
    assert unlabeled(classify(template % declared, vocabulary)) == []
    assert len(unlabeled(classify(template % "Pour aller plus loin", vocabulary))) == 1


def test_latex_comments_are_never_counted(vocabulary) -> None:
    assert classify("% Ceci parle de Terminale\n", vocabulary) == []
    assert len(classify("Ceci parle de Terminale\n", vocabulary)) == 1
