from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_ex_co_graph.py"
ARTIFACT = ROOT / "audit" / "EX_CO_GRAPH.json"


def _module():
    spec = importlib.util.spec_from_file_location("build_ex_co_graph", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _source(path: Path, meta: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("% META: " + json.dumps(meta) + "\nCorps.\n", encoding="utf-8")
    return path


def _corpus(tmp_path: Path) -> tuple[Path, Path]:
    corpus = tmp_path / "chapitres"
    chapter = corpus / "1NSI-X"
    chapter.mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        yaml.safe_dump(
            {
                "capacites": [
                    {"code": "C1", "ref_capacite": "P-X-C1"},
                    {"code": "C2", "ref_capacite": "P-X-C2"},
                ]
            }
        ),
        encoding="utf-8",
    )
    return corpus, chapter


def test_graph_classifies_match_mismatch_and_orphan_without_unknown(
    tmp_path: Path,
) -> None:
    module = _module()
    corpus, chapter = _corpus(tmp_path)
    ex1 = _source(
        chapter / "exercices/ex1.tex",
        {
            "id": "EX1",
            "chapitre": chapter.name,
            "type_objet": "exercice",
            "capacites_codes": ["C1"],
        },
    )
    ex2 = _source(
        chapter / "exercices/ex2.tex",
        {
            "id": "EX2",
            "chapitre": chapter.name,
            "type_objet": "exercice",
            "capacites_codes": ["C2"],
        },
    )
    co_match = _source(
        chapter / "corriges/co1.tex",
        {
            "id": "CO1",
            "chapitre": chapter.name,
            "type_objet": "corrige",
            "capacites_codes": ["C1"],
            "exercice_ref": "EX1",
        },
    )
    co_mismatch = _source(
        chapter / "corriges/co2.tex",
        {
            "id": "CO2",
            "chapitre": chapter.name,
            "type_objet": "corrige",
            "capacites_codes": ["C2"],
            "exercice_id": "EX1",
        },
    )

    graph = module.build_graph(
        corpora=(corpus,),
        source_paths=[ex1, ex2, co_match, co_mismatch],
        clone_ledger={
            "objects_on_invalid_credit": [],
            "objects_with_indeterminate_credit": [],
        },
    )
    by_id = {row["correction_id"]: row for row in graph["relations"]}
    assert by_id["CO1"]["classifications"] == ["UNKNOWN"]
    assert by_id["CO1"]["structural_status"] == "MATCH"
    assert by_id["CO2"]["classifications"] == ["MISMATCHED_CAPACITY"]
    exercise = {row["exercise_id"]: row for row in graph["exercise_cardinality"]}
    assert exercise["EX1"]["classification"] == "MATCH"
    assert exercise["EX2"]["classification"] == "ORPHAN_EX"
    assert graph["unknown_count"] == 1


def test_clone_is_visible_even_when_identity_relation_matches(tmp_path: Path) -> None:
    module = _module()
    corpus, chapter = _corpus(tmp_path)
    exercise = _source(
        chapter / "exercices/ex.tex",
        {
            "id": "EX",
            "chapitre": chapter.name,
            "type_objet": "exercice",
            "capacites_codes": ["C1"],
        },
    )
    correction = _source(
        chapter / "corriges/co.tex",
        {
            "id": "CO",
            "chapitre": chapter.name,
            "type_objet": "corrige",
            "exercice_id": "EX",
        },
    )
    graph = module.build_graph(
        corpora=(corpus,),
        source_paths=[exercise, correction],
        clone_ledger={
            "objects_on_invalid_credit": [],
            "objects_with_indeterminate_credit": [str(correction)],
        },
    )
    assert graph["relations"][0]["classifications"] == ["CLONE"]


def test_cross_discipline_ledger_overrides_same_manual_and_chapter(
    tmp_path: Path,
) -> None:
    module = _module()
    corpus, chapter = _corpus(tmp_path)
    exercise = _source(
        chapter / "exercices/ex.tex",
        {
            "id": "EX",
            "chapitre": chapter.name,
            "type_objet": "exercice",
            "capacites_codes": ["C1"],
        },
    )
    correction = _source(
        chapter / "corriges/co.tex",
        {
            "id": "CO",
            "chapitre": chapter.name,
            "type_objet": "corrige",
            "exercice_id": "EX",
        },
    )
    graph = module.build_graph(
        corpora=(corpus,),
        source_paths=[exercise, correction],
        clone_ledger={
            "objects_on_invalid_credit": [],
            "objects_with_indeterminate_credit": [],
        },
        cross_discipline_ledger={"condemned_paths": [str(exercise)]},
    )
    assert graph["relations"][0]["classifications"] == ["CROSS_DISCIPLINE"]


def test_invalid_cross_chapter_link_does_not_satisfy_exercise_cardinality(
    tmp_path: Path,
) -> None:
    module = _module()
    corpus, chapter_a = _corpus(tmp_path)
    chapter_b = corpus / "1NSI-Y"
    chapter_b.mkdir()
    (chapter_b / "contrat.yaml").write_text(
        yaml.safe_dump(
            {"capacites": [{"code": "C1", "ref_capacite": "P-Y-C1"}]}
        ),
        encoding="utf-8",
    )
    exercise = _source(
        chapter_a / "exercices/ex.tex",
        {
            "id": "EX-A",
            "chapitre": chapter_a.name,
            "type_objet": "exercice",
            "capacites_codes": ["C1"],
        },
    )
    correction = _source(
        chapter_b / "corriges/co.tex",
        {
            "id": "CO-B",
            "chapitre": chapter_b.name,
            "type_objet": "corrige",
            "capacites_codes": ["C1"],
            "exercice_id": "EX-A",
        },
    )
    graph = module.build_graph(
        corpora=(corpus,),
        source_paths=[exercise, correction],
        clone_ledger={
            "objects_on_invalid_credit": [],
            "objects_with_indeterminate_credit": [],
        },
        cross_discipline_ledger={"condemned_paths": []},
    )
    assert graph["relations"][0]["classifications"] == ["MISMATCHED_CONTENT"]
    assert graph["exercise_cardinality"][0]["classification"] == "ORPHAN_EX"


def test_committed_graph_is_current_and_has_no_unknown() -> None:
    module = _module()
    expected = module.build_graph()
    assert expected["unknown_count"] == expected["relation_counts"]["UNKNOWN"]
    assert expected["unknown_count"] > 0
    assert json.loads(ARTIFACT.read_text(encoding="utf-8")) == expected


def test_an_optional_extension_pair_declares_no_capacity_by_design(
    tmp_path: Path,
) -> None:
    """Un exercice d'EXTENSION ne sert aucune capacite, et c'est voulu.

    Ces objets portent `programme_alignment: OPTIONAL_EXTENSION` et declarent
    leur identite dans `extension_codes`, pas dans `capacites_codes`. Lire
    « aucune capacite des deux cotes » comme un desaccord de capacite
    fabrique un bloqueur de release la ou le contrat est respecte : la paire
    est coherente, simplement hors du referentiel des capacites.
    """
    module = _module()
    corpus, chapter = _corpus(tmp_path)
    extension = {
        "chapitre": chapter.name,
        "programme_alignment": "OPTIONAL_EXTENSION",
        "extension_codes": ["X4"],
    }
    ex = _source(
        chapter / "exercices/ex1.tex",
        {"id": "EX1", "type_objet": "exercice", **extension},
    )
    co = _source(
        chapter / "corriges/co1.tex",
        {"id": "CO1", "type_objet": "corrige", "exercice_ref": "EX1", **extension},
    )
    graph = module.build_graph(
        corpora=(corpus,),
        source_paths=[ex, co],
        clone_ledger={
            "objects_on_invalid_credit": [],
            "objects_with_indeterminate_credit": [],
        },
    )
    row = graph["relations"][0]
    assert "MISMATCHED_CAPACITY" not in row["classifications"]
    assert row["structural_status"] == "MATCH"


def test_an_extension_never_excuses_a_real_capacity_disagreement(
    tmp_path: Path,
) -> None:
    """La tolerance ne vaut que si les DEUX cotes sont d'accord.

    Une extension face a un objet qui, lui, sert une capacite reste un
    desaccord : c'est exactement le cas qu'il faut continuer d'attraper.
    """
    module = _module()
    corpus, chapter = _corpus(tmp_path)
    ex = _source(
        chapter / "exercices/ex1.tex",
        {
            "id": "EX1",
            "chapitre": chapter.name,
            "type_objet": "exercice",
            "programme_alignment": "OPTIONAL_EXTENSION",
            "extension_codes": ["X4"],
        },
    )
    co = _source(
        chapter / "corriges/co1.tex",
        {
            "id": "CO1",
            "chapitre": chapter.name,
            "type_objet": "corrige",
            "exercice_ref": "EX1",
            "capacites_codes": ["C1"],
        },
    )
    graph = module.build_graph(
        corpora=(corpus,),
        source_paths=[ex, co],
        clone_ledger={
            "objects_on_invalid_credit": [],
            "objects_with_indeterminate_credit": [],
        },
    )
    assert "MISMATCHED_CAPACITY" in graph["relations"][0]["classifications"]


def test_extension_codes_must_agree_on_both_sides(tmp_path: Path) -> None:
    """Deux extensions differentes ne forment pas une paire coherente."""
    module = _module()
    corpus, chapter = _corpus(tmp_path)
    ex = _source(
        chapter / "exercices/ex1.tex",
        {
            "id": "EX1", "chapitre": chapter.name, "type_objet": "exercice",
            "programme_alignment": "OPTIONAL_EXTENSION", "extension_codes": ["X4"],
        },
    )
    co = _source(
        chapter / "corriges/co1.tex",
        {
            "id": "CO1", "chapitre": chapter.name, "type_objet": "corrige",
            "exercice_ref": "EX1",
            "programme_alignment": "OPTIONAL_EXTENSION", "extension_codes": ["X9"],
        },
    )
    graph = module.build_graph(
        corpora=(corpus,),
        source_paths=[ex, co],
        clone_ledger={
            "objects_on_invalid_credit": [],
            "objects_with_indeterminate_credit": [],
        },
    )
    assert "MISMATCHED_CAPACITY" in graph["relations"][0]["classifications"]


def test_the_four_trigonometry_corrections_declare_their_exercise() -> None:
    """Un corrige doit nommer l'exercice qu'il corrige.

    `1SPE-TRIGO-CO-021..024` portaient une META de forme EXERCICE -- avec
    `corrige_tex`, `parcours`, `parametres_sympy` -- et ne declaraient ni
    `exercice_ref` ni `exercice_id`. Ils apparaissaient donc comme des
    corriges orphelins. L'appariement n'est pas devine a partir de la
    numerotation : c'est l'exercice qui, de son cote, declare
    `corrige_tex` vers ce corrige.
    """
    chapter = ROOT / "Mathematiques/manuel-maths/chapitres/1SPE-TRIGONOMETRIE"
    for number in ("021", "022", "023", "024"):
        correction = chapter / f"corriges/1SPE-TRIGO-CO-{number}.tex"
        exercise = chapter / f"exercices/1SPE-TRIGO-EX-{number}.tex"
        co_meta = json.loads(
            correction.read_text(encoding="utf-8").split("META:", 1)[1].split("\n", 1)[0]
        )
        ex_meta = json.loads(
            exercise.read_text(encoding="utf-8").split("META:", 1)[1].split("\n", 1)[0]
        )
        assert co_meta.get("exercice_ref") == ex_meta["id"], correction.name
        # La preuve de l'appariement vient de l'exercice lui-meme.
        assert ex_meta["corrige_tex"].endswith(f"1SPE-TRIGO-CO-{number}.tex")
