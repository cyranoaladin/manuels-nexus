import copy
import hashlib
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_maquette_v5 as generator
from build_maquette_v5 import MetaError, load_manifest, parse_meta


def test_canonical_manifest_contract():
    manifest = load_manifest(ROOT / "build/maquette-v5/manifest.json", ROOT)

    assert manifest == {
        "version": 2,
        "source_chapter": "1SPE-DERIVATION-LOCAL",
        "output_pdf": "build/maquette-v5/maquette.pdf",
        "expected_pages": 15,
        "blank_pages": [6, 14],
        "course_files": [
            "chapitres/1SPE-DERIVATION-LOCAL/cours/10_C1_taux_variation.tex",
            "chapitres/1SPE-DERIVATION-LOCAL/cours/11_C2_nombre_derive.tex",
        ],
        "methods": [
            "1SPE-DERLOCAL-ME-001",
            "1SPE-DERLOCAL-ME-002",
            "1SPE-DERLOCAL-ME-003",
            "1SPE-DERLOCAL-ME-004",
        ],
        "rendered_method": {
            "id": "1SPE-DERLOCAL-ME-001",
            "applications": [
                "1SPE-DERLOCAL-EX-001",
                "1SPE-DERLOCAL-EX-002",
                "1SPE-DERLOCAL-EX-005",
            ],
        },
        "exercise_order": [
            "1SPE-DERLOCAL-EX-001",
            "1SPE-DERLOCAL-EX-002",
            "1SPE-DERLOCAL-EX-007",
            "1SPE-DERLOCAL-EX-008",
            "1SPE-DERLOCAL-EX-009",
            "1SPE-DERLOCAL-EX-010",
            "1SPE-DERLOCAL-EX-005",
            "1SPE-DERLOCAL-EX-003",
            "1SPE-DERLOCAL-EX-004",
            "1SPE-DERLOCAL-EX-006",
            "1SPE-DERLOCAL-EX-011",
            "1SPE-DERLOCAL-EX-012",
            "1SPE-DERLOCAL-EX-013",
            "1SPE-DERLOCAL-EX-014",
            "1SPE-DERLOCAL-EX-015",
            "1SPE-DERLOCAL-EX-016",
            "1SPE-DERLOCAL-EX-017",
            "1SPE-DERLOCAL-EX-018",
            "1SPE-DERLOCAL-EX-019",
            "1SPE-DERLOCAL-EX-020",
        ],
        "exercise_page_counts": {"9": 11, "10": 9},
        "pictograms": {
            "1SPE-DERLOCAL-EX-005": "calculatrice",
            "1SPE-DERLOCAL-EX-006": "python",
            "1SPE-DERLOCAL-EX-015": "calculatrice",
        },
        "qcm": {
            "file": (
                "chapitres/1SPE-DERIVATION-LOCAL/qcm/"
                "1SPE-DERIVATION-LOCAL-QCM.tex"
            ),
            "sha256": (
                "cb34cb2351761e1c60d15eb5b95bcbc656c718fb19b6dca"
                "15290e3df3384b9e3"
            ),
        },
        "compact_corrections": [
            "1SPE-DERLOCAL-EX-001",
            "1SPE-DERLOCAL-EX-002",
            "1SPE-DERLOCAL-EX-003",
            "1SPE-DERLOCAL-EX-004",
            "1SPE-DERLOCAL-EX-005",
        ],
        "chapter_toc": [
            ["Ouverture", 1],
            ["Diagnostic", 2],
            ["Activités", 3],
            ["Cours", 5],
            ["Méthodes", 9],
            ["Entraînement", 13],
            ["TD", 23],
            ["Auto-évaluation", 27],
            ["Évaluation", 31],
        ],
        "required_strings": [
            "S'entraîner : ex. 1, 2, 7 p. 9",
            "→ M1 · Corrigé p. 15",
        ],
    }


def _exercise_meta(root: Path, source: Path, correction: Path) -> dict:
    return {
        "id": "1SPE-DERLOCAL-EX-001",
        "type_objet": "exercice",
        "methodes": ["M1"],
        "parcours": 1,
        "duree_min": 5,
        "fichier_tex": source.relative_to(root).as_posix(),
        "corrige_tex": correction.relative_to(root).as_posix(),
    }


def _write_meta(path: Path, meta: dict, *, prefix_lines: int = 0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    prefix = "% commentaire\n" * prefix_lines
    path.write_text(
        f"{prefix}% META: {json.dumps(meta)}\nCORPS QUI NE DOIT PAS ÊTRE ÉMIS\n",
        encoding="utf-8",
    )


def _copy_manifest_fixture(tmp_path: Path, manifest: dict) -> Path:
    root = tmp_path / "repo"
    chapter = manifest["source_chapter"]
    selected_paths = list(manifest["course_files"])
    selected_paths.append(manifest["qcm"]["file"])
    selected_paths.extend(
        f"chapitres/{chapter}/methodes/{object_id}.tex"
        for object_id in manifest["methods"]
    )
    for object_id in manifest["exercise_order"]:
        selected_paths.extend(
            [
                f"chapitres/{chapter}/exercices/{object_id}.tex",
                (
                    f"chapitres/{chapter}/corriges/"
                    f"{object_id.replace('-EX-', '-CO-')}.tex"
                ),
            ]
        )
    for relative in selected_paths:
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination)
    return root


def test_parse_meta_valid_exercise_contract(tmp_path):
    root = tmp_path / "repo"
    source = root / "exercices/exercice.tex"
    correction = root / "corriges/correction.tex"
    correction.parent.mkdir(parents=True)
    correction.write_text("correction", encoding="utf-8")
    meta = _exercise_meta(root, source, correction)
    _write_meta(source, meta)

    assert meta["fichier_tex"] == "exercices/exercice.tex"
    assert meta["corrige_tex"] == "corriges/correction.tex"
    assert parse_meta(source, root) == meta


@pytest.mark.parametrize(
    "case",
    [
        "meta_absent",
        "meta_after_line_10",
        "bad_json",
        "empty_id",
        "wrong_type",
        "methodes_empty",
        "methodes_wrong_type",
        "methodes_bad_code",
        "parcours_zero",
        "parcours_four",
        "parcours_wrong_type",
        "duree_zero",
        "duree_negative",
        "duree_wrong_type",
        "fichier_absolute",
        "fichier_outside",
        "fichier_missing",
        "fichier_mismatch",
        "corrige_absolute",
        "corrige_outside",
        "corrige_missing_path",
        "corrige_missing_field",
    ],
)
def test_parse_meta_exercise_contract(tmp_path, case):
    root = tmp_path / "repo"
    source = root / "objets/exercice.tex"
    correction = root / "corriges/correction.tex"
    correction.parent.mkdir(parents=True)
    correction.write_text("correction", encoding="utf-8")
    meta = _exercise_meta(root, source, correction)

    if case == "meta_absent":
        source.parent.mkdir(parents=True)
        source.write_text("% commentaire\ncorps\n", encoding="utf-8")
    elif case == "meta_after_line_10":
        _write_meta(source, meta, prefix_lines=10)
    elif case == "bad_json":
        source.parent.mkdir(parents=True)
        source.write_text("% META: {JSON invalide\n", encoding="utf-8")
    else:
        if case == "empty_id":
            meta["id"] = ""
        elif case == "wrong_type":
            meta["type_objet"] = "cours"
        elif case == "methodes_empty":
            meta["methodes"] = []
        elif case == "methodes_wrong_type":
            meta["methodes"] = "M1"
        elif case == "methodes_bad_code":
            meta["methodes"] = ["m1"]
        elif case == "parcours_zero":
            meta["parcours"] = 0
        elif case == "parcours_four":
            meta["parcours"] = 4
        elif case == "parcours_wrong_type":
            meta["parcours"] = "1"
        elif case == "duree_zero":
            meta["duree_min"] = 0
        elif case == "duree_negative":
            meta["duree_min"] = -1
        elif case == "duree_wrong_type":
            meta["duree_min"] = 5.0
        elif case == "fichier_absolute":
            meta["fichier_tex"] = str(source)
        elif case == "fichier_outside":
            outside = tmp_path / "outside-exercise.tex"
            outside.write_text("outside", encoding="utf-8")
            meta["fichier_tex"] = "../outside-exercise.tex"
        elif case == "fichier_missing":
            meta["fichier_tex"] = "objets/absent.tex"
        elif case == "fichier_mismatch":
            other = root / "objets/autre.tex"
            other.parent.mkdir(parents=True, exist_ok=True)
            other.write_text("other", encoding="utf-8")
            meta["fichier_tex"] = other.relative_to(root).as_posix()
        elif case == "corrige_absolute":
            meta["corrige_tex"] = str(correction)
        elif case == "corrige_outside":
            outside = tmp_path / "outside-correction.tex"
            outside.write_text("outside", encoding="utf-8")
            meta["corrige_tex"] = "../outside-correction.tex"
        elif case == "corrige_missing_path":
            meta["corrige_tex"] = "corriges/absent.tex"
        elif case == "corrige_missing_field":
            del meta["corrige_tex"]
        _write_meta(source, meta)

    with pytest.raises(MetaError):
        parse_meta(source, root)


def test_parse_meta_method_contract(tmp_path):
    root = tmp_path / "repo"
    source = root / "methodes/methode.tex"
    valid = {
        "id": "1SPE-DERLOCAL-ME-001",
        "type_objet": "methode",
        "methodes": ["M1"],
    }
    _write_meta(source, valid)

    assert parse_meta(source, root) == valid

    invalid_variants = [
        {"type_objet": "methode", "methodes": ["M1"]},
        {"id": "", "type_objet": "methode", "methodes": ["M1"]},
        {"id": valid["id"], "methodes": ["M1"]},
        {"id": valid["id"], "type_objet": "exercice", "methodes": ["M1"]},
        {"id": valid["id"], "type_objet": "methode"},
        {"id": valid["id"], "type_objet": "methode", "methodes": []},
        {"id": valid["id"], "type_objet": "methode", "methodes": ["M01x"]},
    ]
    for invalid in invalid_variants:
        _write_meta(source, invalid)
        with pytest.raises(MetaError):
            parse_meta(source, root)


def test_generator_cli_invalid_json_returns_2_without_traceback(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{JSON invalide", encoding="utf-8")
    output = tmp_path / "renvois.tex"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/build_maquette_v5.py"),
            "--manifest",
            str(manifest),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "META V5:" in result.stderr
    assert "Traceback" not in result.stderr


def test_generator_cli_non_utf8_manifest_returns_2_without_traceback(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_bytes(b"\xff")
    output = tmp_path / "renvois.tex"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/build_maquette_v5.py"),
            "--manifest",
            str(manifest),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "META V5:" in result.stderr
    assert "Traceback" not in result.stderr


def test_generator_cli_invalid_manifest_preserves_existing_output(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{JSON invalide", encoding="utf-8")
    output = tmp_path / "renvois.tex"
    output.write_text("SENTINELLE À CONSERVER\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/build_maquette_v5.py"),
            "--manifest",
            str(manifest),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "META V5:" in result.stderr
    assert "Traceback" not in result.stderr
    assert output.read_text(encoding="utf-8") == "SENTINELLE À CONSERVER\n"


def test_build_reference_table_rejects_duplicate_unknown_and_bad_pairing():
    manifest = load_manifest(ROOT / "build/maquette-v5/manifest.json", ROOT)
    application_ids = manifest["rendered_method"]["applications"]

    for count, fallback in ((0, True), (1, True), (2, False), (3, False)):
        candidate = copy.deepcopy(manifest)
        candidate["rendered_method"]["applications"] = application_ids[:count]

        table = generator.build_reference_table(candidate, ROOT)

        assert table["rendered_method"]["fallback"] is fallback
        assert [record["id"] for record in table["exercises"]] == manifest[
            "exercise_order"
        ]

    table = generator.build_reference_table(manifest, ROOT)
    assert table["methods"] == [
        {
            "id": "1SPE-DERLOCAL-ME-001",
            "method": "M1",
            "source": (
                "chapitres/1SPE-DERIVATION-LOCAL/methodes/"
                "1SPE-DERLOCAL-ME-001.tex"
            ),
        },
        {
            "id": "1SPE-DERLOCAL-ME-002",
            "method": "M2",
            "source": (
                "chapitres/1SPE-DERIVATION-LOCAL/methodes/"
                "1SPE-DERLOCAL-ME-002.tex"
            ),
        },
        {
            "id": "1SPE-DERLOCAL-ME-003",
            "method": "M3",
            "source": (
                "chapitres/1SPE-DERIVATION-LOCAL/methodes/"
                "1SPE-DERLOCAL-ME-003.tex"
            ),
        },
        {
            "id": "1SPE-DERLOCAL-ME-004",
            "method": "M4",
            "source": (
                "chapitres/1SPE-DERIVATION-LOCAL/methodes/"
                "1SPE-DERLOCAL-ME-004.tex"
            ),
        },
    ]
    assert table["exercises"][0] == {
        "id": "1SPE-DERLOCAL-EX-001",
        "number": 1,
        "method": "M1",
        "duration": 5,
        "parcours": 1,
        "picto": None,
        "source": (
            "chapitres/1SPE-DERIVATION-LOCAL/exercices/"
            "1SPE-DERLOCAL-EX-001.tex"
        ),
        "correction": (
            "chapitres/1SPE-DERIVATION-LOCAL/corriges/"
            "1SPE-DERLOCAL-CO-001.tex"
        ),
        "page": 9,
    }
    assert table["exercises"][6]["number"] == 7
    assert table["exercises"][6]["picto"] == "calculatrice"
    assert table["exercises"][10]["page"] == 9
    assert table["exercises"][11]["page"] == 10
    assert [record["number"] for record in table["rendered_method"]["applications"]] == [
        1,
        2,
        7,
    ]

    duplicate = copy.deepcopy(manifest)
    duplicate["exercise_order"][1] = duplicate["exercise_order"][0]
    with pytest.raises(MetaError, match="dupliqué"):
        generator.build_reference_table(duplicate, ROOT)

    unknown = copy.deepcopy(manifest)
    unknown["exercise_order"][0] = "1SPE-DERLOCAL-EX-999"
    with pytest.raises(MetaError, match="inconnu"):
        generator.build_reference_table(unknown, ROOT)

    too_many = copy.deepcopy(manifest)
    too_many["rendered_method"]["applications"].append(
        "1SPE-DERLOCAL-EX-003"
    )
    with pytest.raises(MetaError, match="applications"):
        generator.build_reference_table(too_many, ROOT)


def test_build_reference_table_ignores_unselected_meta_but_rejects_selected(
    tmp_path,
):
    manifest = load_manifest(ROOT / "build/maquette-v5/manifest.json", ROOT)
    root = _copy_manifest_fixture(tmp_path, manifest)
    chapter = manifest["source_chapter"]
    unrelated = (
        root
        / "chapitres"
        / chapter
        / "exercices"
        / "1SPE-DERLOCAL-EX-999.tex"
    )
    unrelated.write_text("% META: {JSON invalide\n", encoding="utf-8")

    table = generator.build_reference_table(manifest, root)

    assert len(table["exercises"]) == 20

    mismatched = (
        root
        / "chapitres"
        / chapter
        / "methodes"
        / "1SPE-DERLOCAL-ME-004.tex"
    )
    _write_meta(
        mismatched,
        {
            "id": "1SPE-DERLOCAL-ME-003",
            "type_objet": "methode",
            "methodes": ["M4"],
        },
    )
    with pytest.raises(MetaError, match="dupliqué|correspond"):
        generator.build_reference_table(manifest, root)

    shutil.copy2(
        ROOT
        / "chapitres"
        / chapter
        / "methodes"
        / "1SPE-DERLOCAL-ME-004.tex",
        mismatched,
    )
    missing = (
        root
        / "chapitres"
        / chapter
        / "exercices"
        / "1SPE-DERLOCAL-EX-020.tex"
    )
    missing.unlink()
    with pytest.raises(MetaError, match="inconnu"):
        generator.build_reference_table(manifest, root)


def test_pairing_rejects_application_from_another_method(tmp_path):
    manifest = load_manifest(ROOT / "build/maquette-v5/manifest.json", ROOT)
    manifest["rendered_method"]["applications"] = ["1SPE-DERLOCAL-EX-007"]

    with pytest.raises(MetaError, match="M1"):
        generator.build_reference_table(manifest, ROOT)

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/build_maquette_v5.py"),
            "--manifest",
            str(manifest_path),
            "--output",
            str(tmp_path / "renvois.tex"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "META V5:" in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize(
    "case",
    [
        "missing_key",
        "extra_key",
        "version",
        "source_chapter",
        "output_absolute",
        "output_suffix",
        "expected_pages_type",
        "expected_pages_value",
        "blank_pages",
        "course_count",
        "course_missing",
        "method_count",
        "method_id",
        "rendered_shape",
        "exercise_count",
        "exercise_id",
        "page_counts",
        "pictogram_count",
        "pictogram_value",
        "pictogram_id",
        "compact_count",
        "toc_count",
        "toc_types",
        "required_count",
        "required_exact",
        "qcm_shape",
        "qcm_file",
        "qcm_hash",
    ],
)
def test_manifest_schema_rejected_by_api_and_cli(tmp_path, case):
    manifest = json.loads(
        (ROOT / "build/maquette-v5/manifest.json").read_text(encoding="utf-8")
    )
    if case == "missing_key":
        del manifest["blank_pages"]
    elif case == "extra_key":
        manifest["unexpected"] = True
    elif case == "version":
        manifest["version"] = 1
    elif case == "source_chapter":
        manifest["source_chapter"] = "../1SPE-DERIVATION-LOCAL"
    elif case == "output_absolute":
        manifest["output_pdf"] = "/tmp/maquette.pdf"
    elif case == "output_suffix":
        manifest["output_pdf"] = "build/maquette-v5/maquette.tex"
    elif case == "expected_pages_type":
        manifest["expected_pages"] = "15"
    elif case == "expected_pages_value":
        manifest["expected_pages"] = 14
    elif case == "blank_pages":
        manifest["blank_pages"] = [6, 13]
    elif case == "course_count":
        manifest["course_files"] = manifest["course_files"][:1]
    elif case == "course_missing":
        manifest["course_files"][0] = (
            "chapitres/1SPE-DERIVATION-LOCAL/cours/absent.tex"
        )
    elif case == "method_count":
        manifest["methods"] = manifest["methods"][:3]
    elif case == "method_id":
        manifest["methods"][3] = "1SPE-DERLOCAL-ME-04"
    elif case == "rendered_shape":
        manifest["rendered_method"]["unexpected"] = True
    elif case == "exercise_count":
        manifest["exercise_order"] = manifest["exercise_order"][:19]
    elif case == "exercise_id":
        manifest["exercise_order"][19] = "1SPE-DERLOCAL-EX-20"
    elif case == "page_counts":
        manifest["exercise_page_counts"] = {"9": 10, "10": 10}
    elif case == "pictogram_count":
        manifest["pictograms"].pop("1SPE-DERLOCAL-EX-015")
    elif case == "pictogram_value":
        manifest["pictograms"]["1SPE-DERLOCAL-EX-005"] = "terminal"
    elif case == "pictogram_id":
        manifest["pictograms"]["1SPE-DERLOCAL-EX-999"] = manifest[
            "pictograms"
        ].pop("1SPE-DERLOCAL-EX-005")
    elif case == "compact_count":
        manifest["compact_corrections"] = manifest["compact_corrections"][:4]
    elif case == "toc_count":
        manifest["chapter_toc"] = manifest["chapter_toc"][:8]
    elif case == "toc_types":
        manifest["chapter_toc"][0] = ["Ouverture", "1"]
    elif case == "required_count":
        manifest["required_strings"] = manifest["required_strings"][:1]
    elif case == "required_exact":
        manifest["required_strings"][1] = "Corrigé p. 15"
    elif case == "qcm_shape":
        del manifest["qcm"]["sha256"]
    elif case == "qcm_file":
        manifest["qcm"]["file"] = (
            "chapitres/1SPE-DERIVATION-LOCAL/qcm/absent.tex"
        )
    elif case == "qcm_hash":
        manifest["qcm"]["sha256"] = "0" * 64

    manifest_path = tmp_path / f"{case}.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    output = tmp_path / f"{case}.tex"

    with pytest.raises(MetaError):
        load_manifest(manifest_path, ROOT)
    with pytest.raises(MetaError):
        generator.build_reference_table(manifest, ROOT)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/build_maquette_v5.py"),
            "--manifest",
            str(manifest_path),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "META V5:" in result.stderr
    assert "Traceback" not in result.stderr
    assert not output.exists()


def test_manifest_and_renderer_reject_latex_unsafe_values(tmp_path):
    canonical = load_manifest(ROOT / "build/maquette-v5/manifest.json", ROOT)
    table = generator.build_reference_table(canonical, ROOT)
    unsafe_ids = [
        r"1SPE-DERLOCAL-EX-020\\evil",
        "1SPE-DERLOCAL-EX-{20}",
        "1SPE-DERLOCAL-EX-%20",
        "1SPE-DERLOCAL-EX-endcsname",
    ]
    for index, unsafe_id in enumerate(unsafe_ids):
        manifest = copy.deepcopy(canonical)
        manifest["exercise_order"][-1] = unsafe_id
        path = tmp_path / f"unsafe-{index}.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        with pytest.raises(MetaError):
            load_manifest(path, ROOT)

        unsafe_table = copy.deepcopy(table)
        unsafe_table["exercises"][0]["id"] = unsafe_id
        with pytest.raises(MetaError):
            generator.render_reference_table(unsafe_table, canonical)

    for index, invalid_pages in enumerate(("15", 15.0, True)):
        manifest = copy.deepcopy(canonical)
        manifest["expected_pages"] = invalid_pages
        path = tmp_path / f"pages-{index}.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        with pytest.raises(MetaError):
            load_manifest(path, ROOT)
        with pytest.raises(MetaError):
            generator.render_reference_table(table, manifest)


def test_generator_cli_unknown_id_returns_2_without_traceback(tmp_path):
    manifest = load_manifest(ROOT / "build/maquette-v5/manifest.json", ROOT)
    manifest["exercise_order"][0] = "1SPE-DERLOCAL-EX-999"
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    output = tmp_path / "renvois.tex"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/build_maquette_v5.py"),
            "--manifest",
            str(manifest_path),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "META V5:" in result.stderr
    assert "1SPE-DERLOCAL-EX-999" in result.stderr
    assert "Traceback" not in result.stderr
    assert not output.exists()


def test_render_reference_table_exact_contract():
    manifest = load_manifest(ROOT / "build/maquette-v5/manifest.json", ROOT)
    table = generator.build_reference_table(manifest, ROOT)

    rendered = generator.render_reference_table(table, manifest)

    for object_id in manifest["exercise_order"]:
        assert rendered.count(f"\\label{{ex:{object_id}}}") == 1
    for object_id in manifest["methods"]:
        assert rendered.count(f"\\label{{meth:{object_id}}}") == 1
    assert rendered.count("\\label{ex:") == 20
    assert rendered.count("\\label{meth:") == 4
    assert rendered.count("\\newcommand{\\nxvCorrectionStartLabel}") == 1
    assert rendered.count("\\label{corr:start}") == 1

    assert (
        "\\csname nxv@difficulty@1SPE-DERLOCAL-EX-001\\endcsname"
        "{\\nxVFullDiamond\\nxVOutlineDiamond\\nxVOutlineDiamond}"
    ) in rendered
    assert (
        "\\csname nxv@difficulty@1SPE-DERLOCAL-EX-009\\endcsname"
        "{\\nxVFullDiamond\\nxVFullDiamond\\nxVOutlineDiamond}"
    ) in rendered
    assert (
        "\\csname nxv@difficulty@1SPE-DERLOCAL-EX-005\\endcsname"
        "{\\nxVFullDiamond\\nxVFullDiamond\\nxVFullDiamond}"
    ) in rendered

    pictogram_declarations = re.findall(
        r"\\csname nxv@picto@[^}]+\\endcsname\{(?:python|calculatrice)\}",
        rendered,
    )
    assert len(pictogram_declarations) == 3
    assert "S'entraîner : ex. 1, 2, 7 p. 9" in rendered
    assert "→ M1 · Corrigé p. 15" in rendered

    assert "Soit $f(x)=x^2+1$" not in rendered
    assert "Calculer un taux de variation" not in rendered
    assert "\\begin{exercice}" not in rendered
    assert "\\input{" not in rendered

    technical_text_removed = rendered
    for object_id in manifest["exercise_order"] + manifest["methods"]:
        technical_text_removed = re.sub(
            rf"\\csname [^}}]*{re.escape(object_id)}\\endcsname",
            "",
            technical_text_removed,
        )
        technical_text_removed = re.sub(
            rf"\\label\{{(?:ex|meth):{re.escape(object_id)}\}}",
            "",
            technical_text_removed,
        )
        assert object_id not in technical_text_removed

    canonical_id = r"(?:1SPE|TSPE)-[A-Z0-9]+(?:-[A-Z0-9]+)*-(?:EX|ME)-[0-9]{3}"
    exercise_id = r"(?:1SPE|TSPE)-[A-Z0-9]+(?:-[A-Z0-9]+)*-EX-[0-9]{3}"
    method_id = r"(?:1SPE|TSPE)-[A-Z0-9]+(?:-[A-Z0-9]+)*-ME-[0-9]{3}"
    lookup = r"\\expandafter\\def\\csname nxv@"
    allowed_lines = [
        r"\\newif\\ifnxvPairingFallback",
        r"\\nxvPairingFallback(?:true|false)",
        rf"{lookup}method-label@({method_id})\\endcsname"
        rf"\{{\\label\{{meth:\1\}}\}}",
        rf"{lookup}(?:number|duration|parcours|page)@{exercise_id}"
        r"\\endcsname\{[0-9]+\}",
        rf"{lookup}method@{exercise_id}\\endcsname\{{M[0-9]+\}}",
        rf"{lookup}difficulty@{exercise_id}\\endcsname"
        r"\{(?:\\nxVFullDiamond){1,3}(?:\\nxVOutlineDiamond){0,2}\}",
        rf"{lookup}picto@{exercise_id}\\endcsname"
        r"\{(?:python|calculatrice)?\}",
        rf"{lookup}reference@{exercise_id}\\endcsname"
        r"\{→ M[0-9]+ · Corrigé p\. 15\}",
        rf"{lookup}label@({exercise_id})\\endcsname"
        rf"\{{\\label\{{ex:\1\}}\}}",
        rf"{lookup}training@M[0-9]+\\endcsname"
        r"\{S'entraîner : ex\. [0-9]+(?:, [0-9]+){0,2} p\. [0-9]+\}",
        r"\\newcommand\{\\nxvCorrectionStartLabel\}"
        r"\{\\label\{corr:start\}\}",
    ]
    for line in rendered.splitlines():
        if line.startswith("%"):
            continue
        assert any(re.fullmatch(pattern, line) for pattern in allowed_lines), line
    assert re.fullmatch(canonical_id, manifest["exercise_order"][0])


def test_generator_cli_success_returns_0(tmp_path):
    output = tmp_path / "generated" / "renvois.tex"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/build_maquette_v5.py"),
            "--manifest",
            str(ROOT / "build/maquette-v5/manifest.json"),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout == "RENVOIS V5: 20 exercices, 1 méthode, 3 pictogrammes\n"
    assert result.stderr == ""
    assert output.is_file()
    manifest = load_manifest(ROOT / "build/maquette-v5/manifest.json", ROOT)
    table = generator.build_reference_table(manifest, ROOT)
    assert output.read_text(encoding="utf-8") == generator.render_reference_table(
        table, manifest
    )


def test_atomic_output_and_failure_cleanup(tmp_path, monkeypatch):
    output = tmp_path / "generated" / "renvois.tex"
    output.parent.mkdir(parents=True)
    output.write_text("STALE", encoding="utf-8")
    replacements = []
    original_replace = Path.replace

    def tracked_replace(source, target):
        replacements.append((source, Path(target)))
        return original_replace(source, target)

    monkeypatch.setattr(Path, "replace", tracked_replace)

    generator._write_atomic_output(output, "FRESH\n")

    assert output.read_text(encoding="utf-8") == "FRESH\n"
    assert len(replacements) == 1
    temporary, target = replacements[0]
    assert temporary.parent == output.parent
    assert target == output
    assert list(output.parent.iterdir()) == [output]

    def failing_replace(source, target):
        del source, target
        raise OSError("remplacement simulé")

    monkeypatch.setattr(Path, "replace", failing_replace)
    with pytest.raises(MetaError, match="sortie impossible"):
        generator._write_atomic_output(output, "NOUVEAU\n")

    assert output.read_text(encoding="utf-8") == "FRESH\n"
    assert list(output.parent.iterdir()) == [output]


def test_pdf_text_helpers_and_margin_log_contract():
    checker = importlib.import_module("check_maquette_v5")
    whitespace_only = " \t\r\n\f\u00a0\u2007\u202f\u2009\ufeff"

    assert checker.normalize_text(whitespace_only) == ""
    assert checker.page_text_is_empty(whitespace_only)
    assert not checker.page_text_is_empty("\u00a0Contenu\f")
    assert checker.normalize_text(
        " S'entraîner\u00a0:  ex. 1,\n 2, 7 p. 9\f"
    ) == "S'entraîner : ex. 1, 2, 7 p. 9"

    extracted = (
        "S'entraîner\u202f: ex. 1, 2, 7 p. 9\n"
        "→ M1 · Corrigé p. 15\f"
    )
    required = [
        "S'entraîner : ex. 1, 2, 7 p. 9",
        "→ M1 · Corrigé p. 15",
    ]
    assert checker.required_strings_present(extracted, required)
    assert not checker.required_strings_present(extracted, required + ["absente"])

    checker.assert_no_two_column_marginnotes(
        "NEXUS-V5-MARGINNOTE-REDIRECTED\nCompilation terminée"
    )
    with pytest.raises(checker.AcceptanceError, match="COLUMNS-EMITTED"):
        checker.assert_no_two_column_marginnotes(
            "NEXUS-V5-MARGINNOTE-COLUMNS-EMITTED"
        )
    checker.assert_no_compact_correction_overfull(
        "NEXUS-V5-COMPACT-CORRECTIONS-START\n"
        "Composition saine\n"
        "NEXUS-V5-COMPACT-CORRECTIONS-END"
    )
    with pytest.raises(checker.AcceptanceError, match="corrigés compacts"):
        checker.assert_no_compact_correction_overfull(
            "NEXUS-V5-COMPACT-CORRECTIONS-START\n"
            "Overfull \\hbox (12.0pt too wide)\n"
            "NEXUS-V5-COMPACT-CORRECTIONS-END"
        )


def test_diagnostics_log_contract():
    checker = importlib.import_module("check_maquette_v5")
    start = "NEXUS-V5-DIAGNOSTICS-START"
    end = "NEXUS-V5-DIAGNOSTICS-END"
    clean_passes = [
        f"passage {number}\n{start}\ncomposition saine {number}\n{end}"
        for number in range(1, 4)
    ]
    clean_log = "\n".join(clean_passes)

    checker.assert_diagnostics_log_clean(clean_log)
    checker.assert_diagnostics_log_clean(
        "Overfull \\hbox hors diagnostics\n"
        + clean_log
        + "\nOverfull \\vbox hors diagnostics"
    )

    invalid_logs = [
        "journal sans marqueur diagnostics",
        clean_log.replace(end, "", 1),
        clean_log + f"\n{start}\nquatrième passage\n{end}",
        clean_log.replace(
            "composition saine 2",
            "NEXUS-V5-DIAGNOSTICS-PARASITE\ncomposition saine 2",
        ),
        f"{start}\n{start}\n{end}\n{end}\n" + "\n".join(clean_passes[2:]),
    ]
    for invalid_log in invalid_logs:
        with pytest.raises(checker.AcceptanceError, match="diagnostics"):
            checker.assert_diagnostics_log_clean(invalid_log)

    for pass_number in range(3):
        for box_kind in ("hbox", "vbox"):
            overfull_passes = clean_passes.copy()
            overfull_passes[pass_number] = overfull_passes[pass_number].replace(
                "composition saine",
                f"Overfull \\{box_kind} (12.0pt too large)\ncomposition saine",
            )
            with pytest.raises(checker.AcceptanceError, match="diagnostics"):
                checker.assert_diagnostics_log_clean("\n".join(overfull_passes))


def test_diagnostics_bbox_contract():
    checker = importlib.import_module("check_maquette_v5")

    def diagnostics_xhtml(
        *,
        table_gap=12.0,
        score_gap=12.0,
        answers_y=None,
        diagnostic_y=None,
        capacities_on_score=False,
        missing_question=None,
        missing_diagnostic=None,
        override=None,
    ):
        lines = []

        def add(key, text, y_min, *, x_min=60.0, x_max=430.0, height=4.0):
            attributes = {
                "xMin": x_min,
                "yMin": y_min,
                "xMax": x_max,
                "yMax": y_min + height,
            }
            if override is not None and override[0] == key:
                attributes[override[1]] = override[2]
            lines.append(
                '<line data-key="{}" xMin="{}" yMin="{}" xMax="{}" yMax="{}">'
                '<word xMin="{}" yMin="{}" xMax="{}" yMax="{}">{}</word>'
                "</line>".format(
                    key,
                    attributes["xMin"],
                    attributes["yMin"],
                    attributes["xMax"],
                    attributes["yMax"],
                    attributes["xMin"],
                    attributes["yMin"],
                    attributes["xMax"],
                    attributes["yMax"],
                    text,
                )
            )

        add("header", "Corrigés", 34.0, x_min=40.0, x_max=120.0, height=6.0)
        add("title", "Correction et diagnostics", 58.0, height=7.0)
        add("table-header-left", "Question", 72.0, x_max=115.0, height=5.0)
        add(
            "table-header-right",
            "Capacité Réponse",
            72.0,
            x_min=125.0,
            x_max=260.0,
            height=5.0,
        )

        slot = 0
        for question in range(1, 16):
            y_min = 84.0 + slot * 6.0
            if question != missing_question:
                add(
                    f"question-{question}",
                    f"Q{question} C{min(5, (question + 2) // 3)} B",
                    y_min,
                )
            slot += 1
            for letter in ("A", "C", "D"):
                y_min = 84.0 + slot * 6.0
                if question == 1 and letter == "A" and diagnostic_y is not None:
                    y_min = diagnostic_y
                if (question, letter) != missing_diagnostic:
                    method = min(5, (question + 2) // 3)
                    detail = f"{letter} : diagnostic QCM — renvoi M{method}"
                    if question == 15 and letter == "D":
                        detail = "D : erreur de placement de la virgule — renvoi M5"
                    add(f"diagnostic-{question}-{letter}", detail, y_min)
                slot += 1

        table_bottom = 84.0 + 59 * 6.0 + 4.0
        responses_y = table_bottom + table_gap
        add("responses-title", "Réponses correctes", responses_y, height=7.0)
        grid_start_y = responses_y + 16.0 if answers_y is None else answers_y
        add(
            "answers-1-5",
            "Q1 B Q2 B Q3 C Q4 A Q5 A",
            grid_start_y,
            height=7.0,
        )
        add(
            "answers-6-10",
            "Q6 B Q7 B Q8 B Q9 C Q10 B",
            grid_start_y + 12.0,
            height=7.0,
        )
        grid_last_y = grid_start_y + 24.0
        add(
            "answers-11-15",
            "Q11 B Q12 B Q13 B Q14 B Q15 B",
            grid_last_y,
            height=7.0,
        )
        score_y = responses_y + 47.0 + score_gap
        add("score", "Score : \x03 \x03 /15", score_y, height=7.0)
        add(
            "capacities",
            "Capacités à retravailler : C1 C2 C3 C4 C5",
            score_y if capacities_on_score else score_y + 13.0,
            height=7.0,
        )
        add(
            "footer-brand",
            "NEXUS RÉUSSITE",
            804.0,
            x_min=38.0,
            x_max=520.0,
            height=7.0,
        )
        add("footer-folio", "13", 804.0, x_min=520.0, x_max=540.0, height=7.0)
        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<html xmlns="http://www.w3.org/1999/xhtml"><body><doc>'
            '<page width="595.276" height="841.89"><flow><block>'
            + "".join(lines)
            + "</block></flow></page></doc></body></html>"
        )

    checker.assert_diagnostics_bbox_layout(diagnostics_xhtml())

    invalid_documents = [
        diagnostics_xhtml(diagnostic_y=84.0),
        diagnostics_xhtml(capacities_on_score=True),
        diagnostics_xhtml(answers_y=100.0),
        diagnostics_xhtml(table_gap=5.0),
        diagnostics_xhtml(score_gap=5.0),
        diagnostics_xhtml(override=("question-1", "xMin", 55.9)),
        diagnostics_xhtml(override=("question-1", "xMax", 459.6)),
        diagnostics_xhtml(override=("question-1", "yMax", 768.1)),
        diagnostics_xhtml(override=("question-1", "xMin", float("nan"))),
        diagnostics_xhtml(override=("question-1", "xMin", 440.0)),
        diagnostics_xhtml(override=("question-1", "yMin", 89.0)),
        diagnostics_xhtml(missing_question=7),
        diagnostics_xhtml(missing_diagnostic=(8, "C")),
    ]
    for invalid_document in invalid_documents:
        with pytest.raises(checker.AcceptanceError):
            checker.assert_diagnostics_bbox_layout(invalid_document)


def _install_fake_maquette_tools(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "tools.log"
    script = """#!/bin/sh
tool=$(basename "$0")
printf '%s\t%s\t%s\n' "$tool" "$PWD" "$*" >> "$NXV_FAKE_LOG"
if [ "$tool" = "python3" ] && [ "$NXV_FAKE_MODE" = "generator_meta" ]; then
  printf '%s\n' 'META V5: erreur synthétique' >&2
  exit 2
fi
if [ "$tool" = "python3" ] && [ "$NXV_FAKE_MODE" = "generator_other" ]; then
  exit 9
fi
if [ "$NXV_FAKE_MODE" = "nonzero" ] && [ "$tool" = "lualatex" ]; then
  exit 7
fi
if [ "$tool" = "lualatex" ]; then
  if [ "$NXV_FAKE_MODE" = "first_pass_undefined" ]; then
    count=0
    if [ -f "$NXV_FAKE_STATE" ]; then read count < "$NXV_FAKE_STATE"; fi
    count=$((count + 1))
    printf '%s' "$count" > "$NXV_FAKE_STATE"
    if [ "$count" -eq 1 ]; then
      printf '%s\n' 'LaTeX Warning: There were undefined references.'
    else
      printf '%s\n' 'LuaLaTeX synthetic success.'
    fi
    exit 0
  fi
  case "$NXV_FAKE_MODE" in
    undefined_control) printf '%s\n' 'Undefined control sequence.' ;;
    bang_line) printf '%s\n' '! LaTeX Error: synthetic failure.' ;;
    undefined_refs) printf '%s\n' 'LaTeX Warning: There were undefined references.' ;;
    citation_undefined) printf '%s\n' "LaTeX Warning: Citation 'nx' undefined." ;;
    *) printf '%s\n' 'LuaLaTeX synthetic success.' ;;
  esac
elif [ "$tool" = "pdfinfo" ]; then
  printf '%s\n' 'Pages: 15'
elif [ "$tool" = "pdftotext" ]; then
  page=''
  wants_page=0
  for arg in "$@"; do
    if [ "$wants_page" -eq 1 ]; then page=$arg; break; fi
    if [ "$arg" = '-f' ]; then wants_page=1; fi
  done
  if [ -z "$page" ]; then
    if [ "$NXV_FAKE_MODE" = "question_marks" ]; then
      printf '%s\n' 'Extraction ?? invalide'
    else
      printf '%s\n' 'Extraction saine sans référence manquante'
    fi
  else
    case "$page" in
      1)
        printf '%s\n' 'OUVERTURE' 'Ouverture .... 1' 'Diagnostic .... 2' \
          'Activités .... 3' 'Cours .... 5' 'Méthodes .... 9' \
          'Entraînement .... 13' 'TD .... 23' 'Auto-évaluation .... 27' \
          'Évaluation .... 31' ;;
      2|3|4|5) printf '%s\n' 'Cours' ;;
      6|14) : ;;
      7) printf '%s\n' 'Méthodes REPÈRES DE RÉSOLUTION S’entraîner : ex. 1, 2, 7 p. 9' ;;
      8) printf '%s\n' 'Méthodes À VOUS DE JOUER' ;;
      9)
        printf '%s\n' 'Exercices → M1 · Corrigé p. 15'
        i=2; while [ "$i" -le 11 ]; do printf '%s\n' 'Corrigé p. 15'; i=$((i + 1)); done ;;
      10)
        printf '%s\n' 'Exercices'
        i=1; while [ "$i" -le 9 ]; do printf '%s\n' 'Corrigé p. 15'; i=$((i + 1)); done ;;
      11) printf '%s\n' 'Auto-évaluation [Q1] [Q2] [Q3] [Q4] [Q5] [Q6] [Q7] [Q8]' ;;
      12) printf '%s\n' 'Auto-évaluation [Q9] [Q10] [Q11] [Q12] [Q13] [Q14] [Q15]' ;;
      13) printf '%s\n' 'Corrigés Correction et diagnostics' ;;
      15) printf '%s\n' 'Corrigés Corrigés Corrigé solution Corrigé solution Corrigé solution Corrigé solution Corrigé solution' ;;
    esac
  fi
elif [ "$tool" = "pdftoppm" ]; then
  for arg in "$@"; do prefix=$arg; done
  i=1
  while [ "$i" -le 15 ]; do
    number=$(printf '%02d' "$i")
    : > "${prefix}-${number}.png"
    i=$((i + 1))
  done
elif [ "$tool" = "identify" ]; then
  printf '%s' '1241 1754'
elif [ "$tool" = "compare" ]; then
  printf '%s' '0' >&2
fi
"""
    for name in (
        "python3",
        "lualatex",
        "pdfinfo",
        "pdftotext",
        "pdftoppm",
        "identify",
        "compare",
    ):
        executable = bin_dir / name
        executable.write_text(script, encoding="utf-8")
        executable.chmod(0o755)
    monkeypatch.setenv("NXV_FAKE_LOG", str(log))
    monkeypatch.setenv("NXV_FAKE_STATE", str(tmp_path / "lualatex.state"))
    monkeypatch.setenv("NXV_FAKE_MODE", "success")
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    return log


def test_compile_maquette_calls_generator_three_lualatex_and_pdfinfo(
    tmp_path, monkeypatch
):
    checker = importlib.import_module("check_maquette_v5")
    log = _install_fake_maquette_tools(tmp_path, monkeypatch)

    result = checker.compile_maquette(
        ROOT / "build/maquette-v5/manifest.json", ROOT
    )

    entries = [line.split("\t", 2) for line in log.read_text().splitlines()]
    names = [entry[0] for entry in entries]
    assert names.count("python3") == 1
    assert names.count("lualatex") == 3
    assert names.count("pdfinfo") == 1
    assert names.count("pdftotext") == 1
    assert all(entry[1] == str(ROOT) for entry in entries)
    assert entries[0][0] == "python3"
    assert "build_maquette_v5.py" in entries[0][2]
    assert result["pdfinfo"] == "Pages: 15\n"
    assert "??" not in result["text"]


def test_compile_maquette_allows_first_pass_undefined_references(
    tmp_path, monkeypatch
):
    checker = importlib.import_module("check_maquette_v5")
    log = _install_fake_maquette_tools(tmp_path, monkeypatch)
    monkeypatch.setenv("NXV_FAKE_MODE", "first_pass_undefined")

    result = checker.compile_maquette(
        ROOT / "build/maquette-v5/manifest.json", ROOT
    )

    entries = [line.split("\t", 1)[0] for line in log.read_text().splitlines()]
    assert entries.count("lualatex") == 3
    assert (tmp_path / "lualatex.state").read_text() == "3"
    assert "undefined references" in result["log"]


@pytest.mark.parametrize(
    "mode",
    [
        "nonzero",
        "undefined_control",
        "bang_line",
        "undefined_refs",
        "citation_undefined",
        "question_marks",
    ],
)
def test_compile_maquette_rejects_tool_and_output_failures(
    tmp_path, monkeypatch, mode
):
    checker = importlib.import_module("check_maquette_v5")
    _install_fake_maquette_tools(tmp_path, monkeypatch)
    monkeypatch.setenv("NXV_FAKE_MODE", mode)

    with pytest.raises(checker.AcceptanceError):
        checker.compile_maquette(
            ROOT / "build/maquette-v5/manifest.json", ROOT
        )


def test_checker_cli_synthetic_exit_codes(tmp_path, monkeypatch):
    _install_fake_maquette_tools(tmp_path, monkeypatch)
    checker_script = ROOT / "scripts/check_maquette_v5.py"
    manifest_data = json.loads(
        (ROOT / "build/maquette-v5/manifest.json").read_text(encoding="utf-8")
    )
    synthetic_root = _copy_manifest_fixture(tmp_path, manifest_data)
    synthetic_manifest = synthetic_root / "build/maquette-v5/manifest.json"
    synthetic_manifest.parent.mkdir(parents=True, exist_ok=True)
    synthetic_manifest.write_text(
        json.dumps(manifest_data, ensure_ascii=False), encoding="utf-8"
    )
    (synthetic_root / manifest_data["output_pdf"]).write_bytes(b"FAKE PDF")
    reference = synthetic_root / "validations/v5-it1/page-13.png"
    reference.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "validations/v5-it1/page-13.png", reference)
    output_cases = []

    invalid_manifest = tmp_path / "invalid.json"
    invalid_manifest.write_text("{JSON invalide", encoding="utf-8")
    output_cases.append(
        subprocess.run(
            [
                sys.executable,
                str(checker_script),
                "--manifest",
                str(invalid_manifest),
            ],
            cwd=synthetic_root,
            capture_output=True,
            text=True,
            check=False,
        )
    )

    monkeypatch.setenv("NXV_FAKE_MODE", "question_marks")
    output_cases.append(
        subprocess.run(
            [
                sys.executable,
                str(checker_script),
                "--manifest",
                str(synthetic_manifest),
            ],
            cwd=synthetic_root,
            capture_output=True,
            text=True,
            check=False,
        )
    )

    monkeypatch.setenv("NXV_FAKE_MODE", "success")
    output_cases.append(
        subprocess.run(
            [
                sys.executable,
                str(checker_script),
                "--manifest",
                str(synthetic_manifest),
            ],
            cwd=synthetic_root,
            capture_output=True,
            text=True,
            check=False,
        )
    )

    invalid, rejected, success = output_cases
    assert invalid.returncode == 2
    assert "META V5:" in invalid.stderr
    assert rejected.returncode == 1
    assert "MAQUETTE V5:" in rejected.stderr
    assert success.returncode == 0
    assert success.stdout == (
        "MAQUETTE V5: PASS — 15 pages; blanches 6,14; "
        "renvois 2/2; marginnote colonnes 0\n"
    )
    for result in output_cases:
        assert "Traceback" not in result.stderr


def test_checker_cli_preserves_generator_meta_exit_code(tmp_path, monkeypatch):
    log = _install_fake_maquette_tools(tmp_path, monkeypatch)
    checker_script = ROOT / "scripts/check_maquette_v5.py"
    command = [
        sys.executable,
        str(checker_script),
        "--manifest",
        str(ROOT / "build/maquette-v5/manifest.json"),
    ]

    monkeypatch.setenv("NXV_FAKE_MODE", "generator_meta")
    meta_result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert meta_result.returncode == 2
    assert meta_result.stderr.startswith("META V5:")
    assert "Traceback" not in meta_result.stderr
    assert "lualatex" not in log.read_text(encoding="utf-8")

    log.write_text("", encoding="utf-8")
    monkeypatch.setenv("NXV_FAKE_MODE", "generator_other")
    other_result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert other_result.returncode == 1
    assert other_result.stderr.startswith("MAQUETTE V5:")
    assert "Traceback" not in other_result.stderr
    assert "lualatex" not in log.read_text(encoding="utf-8")


def test_compile_maquette_classifies_missing_paths(tmp_path):
    checker = importlib.import_module("check_maquette_v5")
    manifest = ROOT / "build/maquette-v5/manifest.json"

    with pytest.raises(checker.AcceptanceError, match="racine"):
        checker.compile_maquette(manifest, tmp_path / "racine-absente")
    with pytest.raises(MetaError, match="manifest"):
        checker.compile_maquette(tmp_path / "manifest-absent.json", ROOT)


def test_navigation_opening_and_blank_source_contract():
    class_source = (ROOT / "gabarits/nexus-manuel-v5.cls").read_text(
        encoding="utf-8"
    )
    maquette_source = (ROOT / "build/maquette-v5/maquette.tex").read_text(
        encoding="utf-8"
    )

    assert r"\newmarks\nxRubriqueMarks" in class_source
    assert r"\marks\nxRubriqueMarks{#1}" in class_source
    assert r"\firstmarks\nxRubriqueMarks" in class_source
    assert r"\newcommand{\nxRubrique}{}" not in class_source
    assert r"\renewcommand{\nxRubrique}" not in class_source
    assert class_source.count(r"\nxRubriquePage") >= 3
    assert r"\newcommand{\ouverturechapitreV}" in class_source

    major_start = class_source.index(r"\newcommand{\nxRubriqueMajeure}")
    major_end = class_source.index("% NX-V5-END-RUBRIQUE-MAJEURE", major_start)
    major = class_source[major_start:major_end]
    assert major.index(r"\clearpage") < major.index(r"\nxPageBlancheDecoree")
    assert major.index(r"\nxPageBlancheDecoree") < major.index(r"\rubrique{#2}")

    blank_start = class_source.index(r"\newcommand{\nxPageBlancheDecoree}")
    blank_end = class_source.index("% NX-V5-END-PAGE-BLANCHE", blank_start)
    blank = class_source[blank_start:blank_end]
    assert r"\thispagestyle{blanche}" in blank
    assert r"\vbox to \textheight{\vfil}" in blank
    assert "remember picture,overlay" in blank
    assert "current page" in blank
    assert "opacity=0.04" in blank
    assert r"\node" not in blank
    assert "diamond" not in blank.lower()
    assert "⋄" not in blank
    assert "◆" not in blank

    toc_start = class_source.index(r"\newcommand{\nxSommaireChapitreV}")
    toc_end = class_source.index("% NX-V5-END-SOMMAIRE", toc_start)
    toc = class_source[toc_start:toc_end]
    expected_toc = [
        ("Ouverture", 1),
        ("Diagnostic", 2),
        ("Activités", 3),
        ("Cours", 5),
        ("Méthodes", 9),
        ("Entraînement", 13),
        ("TD", 23),
        ("Auto-évaluation", 27),
        ("Évaluation", 31),
    ]
    assert toc.count(r"\nxTempsChapitre") == 9
    for title, page in expected_toc:
        assert rf"\nxTempsChapitre{{{title}}}{{{page}}}" in toc

    assert r"\ouverturechapitreV{Dérivation locale}" in maquette_source
    assert r"\ouverturechapitre{Dérivation locale}" not in maquette_source
    for unchanged in (
        "Je sais calculer un taux de variation",
        "Un cycliste roule sur une route vallonnée",
        r"\parcoursUn~12 h",
    ):
        assert unchanged in maquette_source


def test_navigation_blank_fixture_pdf(tmp_path):
    checker = importlib.import_module("check_maquette_v5")
    fixture = tmp_path / "navigation-v5.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel-v5}
\matiere{Mathématiques}\niveau{Première spécialité}
\begin{document}
\pagestyle{scrheadings}
\rubrique{A}
\nxSommaireChapitreV
\vfill\noindent PREMIERE
\newpage
\noindent DEUXIEME\vfill
\nxRubriqueMajeure[blanche]{B}
\noindent TROISIEME\vfill
\newpage
\noindent QUATRIEME\vfill
\end{document}
""",
        encoding="utf-8",
    )
    command = [
        "lualatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={tmp_path}",
        str(fixture),
    ]
    for _ in range(3):
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout[-4000:] + result.stderr

    pdf = tmp_path / "navigation-v5.pdf"
    info = subprocess.run(
        ["pdfinfo", str(pdf)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert re.search(r"(?m)^Pages:\s+5$", info)

    pages = []
    for page in range(1, 6):
        extracted = subprocess.run(
            [
                "pdftotext",
                "-f",
                str(page),
                "-l",
                str(page),
                str(pdf),
                "-",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        pages.append(checker.normalize_text(extracted))

    assert re.search(r"\bA\b", pages[0])
    assert re.search(r"\bA\b", pages[1])
    assert checker.page_text_is_empty(pages[2])
    assert re.search(r"\bB\b", pages[3])
    assert re.search(r"\bB\b", pages[4])
    assert not re.search(r"\bB\b", pages[0] + " " + pages[1])
    assert not re.search(r"\bA\b", pages[3] + " " + pages[4])
    for title in (
        "Ouverture",
        "Diagnostic",
        "Activités",
        "Cours",
        "Méthodes",
        "Entraînement",
        "TD",
        "Auto-évaluation",
        "Évaluation",
    ):
        assert title in pages[0]
    assert "??" not in " ".join(pages)

    opening = tmp_path / "opening-v5.tex"
    opening.write_text(
        r"""\documentclass{gabarits/nexus-manuel-v5}
\matiere{Mathématiques}\niveau{Première spécialité}
\begin{document}
\ouverturechapitreV{Titre fixture}{CAPACITES EXACTES}{ACCROCHE EXACTE}{TEMPS EXACTS}
\end{document}
""",
        encoding="utf-8",
    )
    opening_command = command[:-1] + [str(opening)]
    for _ in range(3):
        result = subprocess.run(
            opening_command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout[-4000:] + result.stderr
    opening_pdf = tmp_path / "opening-v5.pdf"
    opening_info = subprocess.run(
        ["pdfinfo", str(opening_pdf)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert re.search(r"(?m)^Pages:\s+1$", opening_info)
    opening_text = checker.normalize_text(
        subprocess.run(
            ["pdftotext", str(opening_pdf), "-"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )
    for exact_content in (
        "CAPACITES EXACTES",
        "ACCROCHE EXACTE",
        "TEMPS EXACTS",
        "LES 9 TEMPS DU CHAPITRE",
        "Ouverture",
        "Évaluation",
    ):
        assert exact_content in opening_text
    assert "??" not in opening_text


def test_course_source_contract():
    class_source = (ROOT / "gabarits/nexus-manuel-v5.cls").read_text(
        encoding="utf-8"
    )
    maquette_source = (ROOT / "build/maquette-v5/maquette.tex").read_text(
        encoding="utf-8"
    )
    course_start = class_source.index("% NX-V5-COURS-START")
    course_end = class_source.index("% NX-V5-COURS-END", course_start)
    course = class_source[course_start:course_end]

    assert r"\newcommand{\coursVocab}[3]" in course
    assert r"\newcommand{\coursRenvoi}[3]" in course
    assert r"\fontsize{7.5}{10}\selectfont" in course
    assert r"\rule{0.4pt}" in course
    assert r"\vspace{9pt}" in course
    assert "4.5pt" in course
    assert "marginparwidth=3.5cm" in course
    assert "marginparwidth=0" not in course
    assert r"\newcounter{nxErreurPage}" in course
    assert r"\AddToHook{shipout/after}" in course
    assert r"\ifnum\value{nxErreurPage}>2" in course
    assert r"\clearpage" in course
    assert r"\RequirePackage{needspace}" in course
    assert r"\Needspace" in course
    assert r"\baselineskip" in course
    assert r"\newcommand{\nxCoursErreurFrequente}[1]" in course
    assert r"\newcommand{\nxCoursApprofondissement}[1]" in course
    assert r"\let\erreurFrequente\nxCoursErreurFrequente" in course
    assert r"\let\approfondissement\nxCoursApprofondissement" in course
    assert r"\renewcommand{\erreurFrequente}" not in course
    assert r"\renewcommand{\approfondissement}" not in course
    assert r"\flushbottom" in course
    assert r"\vfill" not in course
    assert r"\RequirePackage{placeins}" in course
    assert r"\FloatBarrier" in course
    assert r"\def\nxfigcaption{#2}" in course
    assert r"\renewcommand{\nxcaption}[1]" in course
    assert r"\def\nxfigdetail{##1}" in course
    assert r"\let\nxfigure\nxCoursFigure" in course
    assert r"\let\nxCoursRealClearpage\clearpage" in course

    course_environment = course[
        course.index(r"\NewDocumentEnvironment{coursV}") : course.index(
            r"\newcounter{nxErreurPage}"
        )
    ]
    course_end_block = course_environment[course_environment.rindex(r"}{%") :]
    assert course_end_block.index(r"\FloatBarrier") < course_end_block.index(
        r"\let\clearpage\nxCoursRealClearpage"
    )
    assert course_end_block.index(
        r"\let\clearpage\nxCoursRealClearpage"
    ) < course_end_block.index(r"\restoregeometry")
    assert r"\newtcolorbox{nxerrcoursv}" in course
    assert "unbreakable" in course
    assert r"\begin{nxerrcoursv}" in course

    assert maquette_source.count(r"\coursVocab{") == 2
    assert maquette_source.count(r"\coursRenvoi{") == 1
    assert r"\begin{coursV}" in maquette_source
    assert r"\end{coursV}" in maquette_source
    assert (
        "Il mesure la variation moyenne de $f$ lorsque la variable passe de $a$ à $b$."
        in maquette_source
    )
    assert "On le note $f'(a)$." in maquette_source
    assert r"\coursRenvoi{Taux de variation et sécantes}{M1}{7}" in maquette_source

    expected_hashes = {
        "10_C1_taux_variation.tex": (
            "791af12821c630a0d33b4ab795e9c1340953d8d44bdda01bc1493d9a3b7d57c0"
        ),
        "11_C2_nombre_derive.tex": (
            "d25deaa46b47d3aa1bf5ea64487bfadb365718e7a927c7fd2ff07999b02735cf"
        ),
    }
    for filename, expected in expected_hashes.items():
        path = ROOT / "chapitres/1SPE-DERIVATION-LOCAL/cours" / filename
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected


def test_method_pairing_source_contract():
    class_source = (ROOT / "gabarits/nexus-manuel-v5.cls").read_text(
        encoding="utf-8"
    )
    maquette_source = (ROOT / "build/maquette-v5/maquette.tex").read_text(
        encoding="utf-8"
    )

    assert r"\let\nxVOriginalMarginnote\marginnote" in class_source
    assert r"\NewDocumentEnvironment{methodePairee}" in class_source
    assert r"\newcommand{\separationApplications}" in class_source
    assert r"\newcommand{\nxVMethodLabel}" in class_source
    assert r"\renewcommand{\refExos}[1]" in class_source
    assert r"nxv@training@##1" in class_source
    assert "①" in class_source
    assert "②" in class_source
    assert "③" in class_source
    assert "NEXUS-V5-MARGINNOTE-REDIRECTED" in class_source
    assert "NEXUS-V5-MARGINNOTE-COLUMNS-EMITTED" in class_source
    assert r"\AtBeginEnvironment{multicols}" in class_source
    assert r"\AtEndEnvironment{multicols}" in class_source
    assert "NEXUS-V5-METHOD-PAIRING-FALLBACK" in class_source
    assert r"\let\exercice\nxVApplicationExercise" in class_source
    assert r"\let\endexercice\endnxVApplicationExercise" in class_source
    assert r"\nxVOriginalMarginnote" in class_source[
        class_source.index("% NX-V5-COURS-START") :
        class_source.index("% NX-V5-COURS-END")
    ]

    assert r"\input{build/maquette-v5/renvois.tex}" in maquette_source
    assert r"\begin{methodePairee}{1SPE-DERLOCAL-ME-001}" in maquette_source
    assert r"\nxPageBlancheDecoree" not in maquette_source
    assert r"\separationApplications" in maquette_source
    for object_id in ("001", "002", "005"):
        source = (
            "chapitres/1SPE-DERIVATION-LOCAL/exercices/"
            f"1SPE-DERLOCAL-EX-{object_id}.tex"
        )
        assert rf"\input{{{source}}}" in maquette_source

    expected_hashes = {
        "methodes/1SPE-DERLOCAL-ME-001.tex": (
            "59162739ff49b996ed9734b89fcfc826f89fe7fb36261db40efd88aef6cfab0c"
        ),
        "exercices/1SPE-DERLOCAL-EX-001.tex": (
            "42007b26399a82a5e84278f383dfe2c67d53f551e7a0449b19dc0489400b2e91"
        ),
        "exercices/1SPE-DERLOCAL-EX-002.tex": (
            "e896c34ea006a77c2ff95f7404376ffb37f683163a44c269991bb38accbdf587"
        ),
        "exercices/1SPE-DERLOCAL-EX-005.tex": (
            "824f39b800e1bb39a41300acdc2229039f9dac7ca7d57728fbdc056853da9c0e"
        ),
    }
    chapter = ROOT / "chapitres/1SPE-DERIVATION-LOCAL"
    for relative, expected in expected_hashes.items():
        assert hashlib.sha256((chapter / relative).read_bytes()).hexdigest() == expected


@pytest.mark.parametrize("application_count", [0, 1, 2, 3])
def test_method_pairing_fixtures(tmp_path, application_count):
    builder = importlib.import_module("build_maquette_v5")
    checker = importlib.import_module("check_maquette_v5")
    manifest = json.loads(
        (ROOT / "build/maquette-v5/manifest.json").read_text(encoding="utf-8")
    )
    application_ids = [
        "1SPE-DERLOCAL-EX-001",
        "1SPE-DERLOCAL-EX-002",
        "1SPE-DERLOCAL-EX-005",
    ][:application_count]
    manifest["rendered_method"]["applications"] = application_ids
    records = builder.build_reference_table(manifest, ROOT)
    references = tmp_path / f"renvois-{application_count}.tex"
    references.write_text(
        builder.render_reference_table(records, manifest), encoding="utf-8"
    )

    application_inputs = "\n".join(
        rf"\input{{chapitres/1SPE-DERIVATION-LOCAL/exercices/{object_id}.tex}}"
        for object_id in application_ids
    )
    fixture = tmp_path / f"methode-{application_count}.tex"
    fixture.write_text(
        rf"""\documentclass{{gabarits/nexus-manuel-v5}}
\matiere{{Mathématiques}}\niveau{{Première spécialité}}
\begin{{document}}
\input{{{references}}}
\begin{{methodePairee}}{{1SPE-DERLOCAL-ME-001}}
\input{{chapitres/1SPE-DERIVATION-LOCAL/methodes/1SPE-DERLOCAL-ME-001.tex}}
\marginnote{{NOTE DE BAS DE BLOC}}
\separationApplications
{application_inputs}
\end{{methodePairee}}
\end{{document}}
""",
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            "lualatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={tmp_path}",
            str(fixture),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout[-5000:] + result.stderr
    assert "Missing character" not in result.stdout
    assert "NEXUS-V5-MARGINNOTE-REDIRECTED" in result.stdout
    assert "NEXUS-V5-MARGINNOTE-COLUMNS-EMITTED" not in result.stdout
    if application_count < 2:
        assert "NEXUS-V5-METHOD-PAIRING-FALLBACK" in result.stdout
    else:
        assert "NEXUS-V5-METHOD-PAIRING-FALLBACK" not in result.stdout

    extracted = checker.normalize_text(
        subprocess.run(
            ["pdftotext", str(tmp_path / f"methode-{application_count}.pdf"), "-"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )
    assert "REPÈRES DE RÉSOLUTION" in extracted
    assert "NOTE DE BAS DE BLOC" in extracted
    assert "À VOUS DE JOUER" in extracted
    assert extracted.count("Application") == application_count


def test_multicols_marginnote_is_redirected(tmp_path):
    checker = importlib.import_module("check_maquette_v5")
    fixture = tmp_path / "multicols-marginnote.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel-v5}
\matiere{Mathématiques}\niveau{Première spécialité}
\begin{document}
\begin{multicols}{2}
Texte avant.\marginnote{NOTE MULTICOLONNE} Texte après.
\end{multicols}
\nxVFlushBottomNotes
\end{document}
""",
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            "lualatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={tmp_path}",
            str(fixture),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout[-5000:] + result.stderr
    assert "NEXUS-V5-MARGINNOTE-REDIRECTED" in result.stdout
    assert "NEXUS-V5-MARGINNOTE-COLUMNS-EMITTED" not in result.stdout
    checker.assert_no_two_column_marginnotes(result.stdout)
    extracted = subprocess.run(
        ["pdftotext", str(tmp_path / "multicols-marginnote.pdf"), "-"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "NOTE MULTICOLONNE" in checker.normalize_text(extracted)


def test_exercise_adapter_source_contract():
    class_source = (ROOT / "gabarits/nexus-manuel-v5.cls").read_text(
        encoding="utf-8"
    )
    maquette_source = (ROOT / "build/maquette-v5/maquette.tex").read_text(
        encoding="utf-8"
    )
    manifest = load_manifest(ROOT / "build/maquette-v5/manifest.json", ROOT)

    assert r"\newcommand{\nxVFullDiamond}" in class_source
    assert r"\newcommand{\nxVOutlineDiamond}" in class_source
    assert r"\newenvironment{nxVGridExercise}" in class_source
    assert r"\let\exercice\nxVGridExercise" in class_source
    assert r"\let\endexercice\endnxVGridExercise" in class_source
    for lookup in ("number", "duration", "difficulty", "picto", "reference", "label"):
        assert rf"nxv@{lookup}@#1" in class_source
    assert r"\texttt{#1}" not in class_source
    assert "python" in class_source
    assert "calculatrice" in class_source
    assert r"\icnPython" in class_source
    assert r"\icnCalculatrice" in class_source
    assert r"\setlength{\columnseprule}{0.3pt}" in class_source

    grid = maquette_source.split(r"\begin{grilleExercices}", 1)[1].split(
        r"\end{grilleExercices}", 1
    )[0]
    inputs = re.findall(r"\\input\{([^}]+)\}", grid)
    expected = [
        f"chapitres/1SPE-DERIVATION-LOCAL/exercices/{object_id}.tex"
        for object_id in manifest["exercise_order"]
    ]
    assert inputs == expected
    residual = re.sub(r"\\input\{[^}]+\}", "", grid)
    residual = re.sub(r"(?m)^\s*%.*$", "", residual)
    assert residual.strip() == ""


def test_exercise_grid_fixture_pdf(tmp_path):
    from PIL import Image

    checker = importlib.import_module("check_maquette_v5")
    manifest = load_manifest(ROOT / "build/maquette-v5/manifest.json", ROOT)
    references = ROOT / "build/maquette-v5/renvois.tex"
    subprocess.run(
        [
            "python3",
            str(ROOT / "scripts/build_maquette_v5.py"),
            "--manifest",
            str(ROOT / "build/maquette-v5/manifest.json"),
            "--output",
            str(references),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    exercise_inputs = "\n".join(
        rf"\input{{chapitres/1SPE-DERIVATION-LOCAL/exercices/{object_id}.tex}}"
        for object_id in manifest["exercise_order"]
    )
    fixture = tmp_path / "exercices-v5.tex"
    fixture.write_text(
        rf"""\documentclass{{gabarits/nexus-manuel-v5}}
\matiere{{Mathématiques}}\niveau{{Première spécialité}}
\begin{{document}}
\input{{{references}}}
\begin{{grilleExercices}}
{exercise_inputs}
\end{{grilleExercices}}
\end{{document}}
""",
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            "lualatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={tmp_path}",
            str(fixture),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout[-5000:] + result.stderr
    assert "NEXUS-V5-MARGINNOTE-COLUMNS-EMITTED" not in result.stdout

    pdf = tmp_path / "exercices-v5.pdf"
    info = subprocess.run(
        ["pdfinfo", str(pdf)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert re.search(r"(?m)^Pages:\s+2$", info)

    pages = []
    for page in (1, 2):
        extracted = subprocess.run(
            ["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        pages.append(checker.normalize_text(extracted))
    assert [page.count("Corrigé p. 15") for page in pages] == [11, 9]
    assert "→ M1 · Corrigé p. 15" in pages[0]
    combined = " ".join(pages)
    assert combined.count("Python") == 1
    assert combined.count("Calculatrice") == 2
    for object_id in manifest["exercise_order"]:
        assert object_id not in combined

    raster_prefix = tmp_path / "exercise-grid"
    subprocess.run(
        ["pdftoppm", "-gray", "-r", "150", str(pdf), str(raster_prefix)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    for page in (1, 2):
        image = Image.open(tmp_path / f"exercise-grid-{page}.pgm").convert("L")
        middle = image.width // 2
        vertical_counts = [
            sum(
                1
                for y in range(180, image.height - 150)
                if image.getpixel((x, y)) < 245
            )
            for x in range(middle - 85, middle + 86)
        ]
        assert max(vertical_counts) > 600


def test_qcm_hash_is_immutable():
    manifest = load_manifest(ROOT / "build/maquette-v5/manifest.json", ROOT)
    qcm = ROOT / manifest["qcm"]["file"]
    assert hashlib.sha256(qcm.read_bytes()).hexdigest() == manifest["qcm"]["sha256"]
    reference = ROOT / "validations/v5-it1/page-13.png"
    assert hashlib.sha256(reference.read_bytes()).hexdigest() == (
        "ea1750a0f56ecd3b2761614709f96f9b267569ece45bc4103aa11dc2007dacf1"
    )


def test_qcm_and_corrections_source_contract():
    class_source = (ROOT / "gabarits/nexus-manuel-v5.cls").read_text(
        encoding="utf-8"
    )
    maquette_source = (ROOT / "build/maquette-v5/maquette.tex").read_text(
        encoding="utf-8"
    )

    qcm_start = class_source.index(r"\newenvironment{faireLePoint}")
    corrections_start = class_source.index(r"\newenvironment{corrigesCompacts}")
    qcm_source = class_source[qcm_start:corrections_start]
    corrections_source = class_source[corrections_start:]
    assert r"\let\nxVQcmOriginalDfrac\dfrac" in qcm_source
    assert r"\renewcommand{\dfrac}[2]{\tfrac{##1}{##2}}" in qcm_source
    assert r"\interlinepenalty=10000" in qcm_source
    assert r"\clubpenalty=10000" in qcm_source
    assert r"\widowpenalty=10000" in qcm_source
    assert r"\Needspace{10\baselineskip}" in qcm_source
    assert r"\begin{minipage}{\linewidth}" in qcm_source
    assert r"\renewcommand{\endenumerate}" in qcm_source
    assert r"\let\nxVQcmOriginalNewpage\newpage" in qcm_source
    assert r"\renewcommand{\newpage}" in qcm_source
    assert qcm_source.index(r"\end{multicols}") < qcm_source.index(
        r"\rubrique{Corrigés}"
    )
    assert r"\let\dfrac\nxVQcmOriginalDfrac" in qcm_source
    assert r"\nxRubriqueMajeure[blanche]{Corrigés}" in corrections_source
    assert r"\nxvCorrectionStartLabel" in corrections_source
    assert corrections_source.count(r"\section*{Corrigés}") == 1
    assert r"\newenvironment{nxVCompactCorrection}" in corrections_source
    assert r"\let\corrige\nxVCompactCorrection" in corrections_source
    assert r"\let\endcorrige\endnxVCompactCorrection" in corrections_source
    assert r"\renewcommand{\frac}[2]{\tfrac{##1}{##2}}" in corrections_source
    assert (
        r"\everydisplay{\textstyle\thinmuskip=1mu\medmuskip=2mu\thickmuskip=1mu}"
        in corrections_source
    )
    assert "NEXUS-V5-COMPACT-CORRECTIONS-START" in corrections_source
    assert "NEXUS-V5-COMPACT-CORRECTIONS-END" in corrections_source

    assert maquette_source.count(
        r"\input{chapitres/1SPE-DERIVATION-LOCAL/qcm/1SPE-DERIVATION-LOCAL-QCM.tex}"
    ) == 1
    assert maquette_source.count(r"\begin{corrigesCompacts}") == 1
    assert maquette_source.count(r"\end{corrigesCompacts}") == 1
    assert "corr:start" not in maquette_source


def test_qcm_diagnostics_and_corrections_pdf(tmp_path):
    checker = importlib.import_module("check_maquette_v5")
    subprocess.run(
        [
            "python3",
            str(ROOT / "scripts/build_maquette_v5.py"),
            "--manifest",
            str(ROOT / "build/maquette-v5/manifest.json"),
            "--output",
            str(ROOT / "build/maquette-v5/renvois.tex"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    command = [
        "lualatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-output-directory=build/maquette-v5",
        "build/maquette-v5/maquette.tex",
    ]
    for _ in range(3):
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout[-5000:] + result.stderr
    pdf = ROOT / "build/maquette-v5/maquette.pdf"
    info = subprocess.run(
        ["pdfinfo", str(pdf)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert re.search(r"(?m)^Pages:\s+15$", info)

    page_text = {}
    page_layout = {}
    for page in range(11, 16):
        page_text[page] = checker.normalize_text(
            subprocess.run(
                ["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            ).stdout
        )
        page_layout[page] = subprocess.run(
            [
                "pdftotext",
                "-layout",
                "-f",
                str(page),
                "-l",
                str(page),
                str(pdf),
                "-",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout

    for question in range(1, 9):
        assert f"[Q{question}]" in page_text[11]
        assert f"[Q{question}]" not in page_text[12]
    for question in range(9, 16):
        assert f"[Q{question}]" not in page_text[11]
        assert f"[Q{question}]" in page_text[12]
    assert page_layout[12].index("[Q9]") < page_layout[12].index("A.")
    q12 = page_layout[12].index("[Q12]")
    for answer in (
        "A. Vérifier que",
        "B. Vérifier que",
        "C. Vérifier que",
        "D. Vérifier que",
    ):
        assert q12 < page_layout[12].index(answer)
    assert "= 14" in page_text[11]  # extraction compacte de la fraction 1/4
    assert "Correction et diagnostics" in page_text[13]
    assert checker.page_text_is_empty(page_text[14])
    assert page_text[15].count("Corrigés") == 2  # mark + titre unique
    assert page_text[15].count("Corrigé ") == 5
    assert re.search(r"Corrigé[ \t]{1,3}[0-9]+\s*\.", page_layout[15]) is None
    assert "1SPE-DERLOCAL" not in page_text[15]
    checker.assert_no_compact_correction_overfull(
        (ROOT / "build/maquette-v5/maquette.log").read_text(encoding="utf-8")
    )

    current_page = tmp_path / "page-13.png"
    subprocess.run(
        [
            "pdftoppm",
            "-f",
            "13",
            "-l",
            "13",
            "-png",
            "-r",
            "150",
            "-singlefile",
            str(pdf),
            str(current_page.with_suffix("")),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    comparison = subprocess.run(
        [
            "compare",
            "-metric",
            "AE",
            str(ROOT / "validations/v5-it1/page-13.png"),
            str(current_page),
            "null:",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert comparison.returncode == 0, comparison.stderr
    assert comparison.stderr.strip() == "0"


def test_maquette_v5_acceptance():
    result = subprocess.run(
        [
            "python3",
            "scripts/check_maquette_v5.py",
            "--manifest",
            "build/maquette-v5/manifest.json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == (
        "MAQUETTE V5: PASS — 15 pages; blanches 6,14; "
        "renvois 2/2; marginnote colonnes 0"
    )
    assert result.stderr == ""


def test_course_fixture_pdf(tmp_path):
    checker = importlib.import_module("check_maquette_v5")
    fixture = tmp_path / "cours-v5.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel-v5}
\matiere{Mathématiques}\niveau{Première spécialité}
\begin{document}
\let\nxFixtureErreurBase\erreurFrequente
\let\nxFixtureApprofondissementBase\approfondissement
\ouverturechapitreV{Dérivation locale}{CAPACITÉS COURS}{ACCROCHE COURS}{TEMPS COURS}
\clearpage
\coursVocab{Taux de variation et sécantes}{Taux de variation}{Il mesure la variation moyenne de $f$ lorsque la variable passe de $a$ à $b$.}
\coursRenvoi{Taux de variation et sécantes}{M1}{7}
\coursVocab{Du taux de variation au nombre dérivé}{Nombre dérivé}{Lorsque les taux de variation de $f$ entre $a$ et $a+h$ se rapprochent d'un même nombre lorsque $h$ est très proche de $0$, ce nombre est le \textbf{nombre dérivé} de $f$ en $a$. On le note $f'(a)$.}
\begin{coursV}
\rubrique{Cours}
\input{chapitres/1SPE-DERIVATION-LOCAL/cours/10_C1_taux_variation.tex}
\clearpage
\input{chapitres/1SPE-DERIVATION-LOCAL/cours/11_C2_nombre_derive.tex}
\end{coursV}
\ifx\erreurFrequente\nxFixtureErreurBase
  \typeout{NEXUS-V5-COURS-ERREUR-RESTORED}
\else
  \PackageError{fixture}{erreurFrequente non restauree}{}
\fi
\ifx\approfondissement\nxFixtureApprofondissementBase
  \typeout{NEXUS-V5-COURS-APPROFONDISSEMENT-RESTORED}
\else
  \PackageError{fixture}{approfondissement non restaure}{}
\fi
\clearpage
\noindent HORS COURS AVANT
\erreurFrequente{ERREUR HORS COURS RESTAURÉE}
\approfondissement{APPROFONDISSEMENT HORS COURS RESTAURÉ}
\noindent HORS COURS APRÈS
\end{document}
""",
        encoding="utf-8",
    )
    command = [
        "lualatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={tmp_path}",
        str(fixture),
    ]
    for _ in range(3):
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout[-5000:] + result.stderr
    assert "NEXUS-V5-COURS-ERREUR-RESTORED" in result.stdout
    assert "NEXUS-V5-COURS-APPROFONDISSEMENT-RESTORED" in result.stdout

    pdf = tmp_path / "cours-v5.pdf"
    info = subprocess.run(
        ["pdfinfo", str(pdf)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert re.search(r"(?m)^Pages:\s+6$", info)

    pages = []
    for page in range(1, 7):
        extracted = subprocess.run(
            [
                "pdftotext",
                "-f",
                str(page),
                "-l",
                str(page),
                str(pdf),
                "-",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        pages.append(checker.normalize_text(extracted))

    course_pages = pages[1:5]
    assert sum(page.count("VOCABULAIRE") for page in course_pages) == 2
    assert sum(page.count("RENVOI") for page in course_pages) == 1
    assert sum(page.count("ERREUR FRÉQUENTE") for page in course_pages) == 5
    assert all(page.count("ERREUR FRÉQUENTE") <= 2 for page in course_pages)
    assert all(re.search(r"\bCOURS\b", page) for page in course_pages)
    course_text = " ".join(course_pages)
    assert course_text.count("Figure 1") == 1
    assert course_text.count("Figure 2") == 1
    assert "Sécante à la courbe de la fonction carré" in course_text
    assert "Sécantes convergeant vers la tangente" in course_text
    assert "a pour pente le taux de variation" in course_text
    assert "Les sécantes (pointillés) convergent vers la tangente" in course_text
    assert "Float(s) lost" not in result.stdout
    assert "HORS COURS AVANT" in pages[5]
    assert "ERREUR HORS COURS RESTAURÉE" in pages[5]
    assert "APPROFONDISSEMENT HORS COURS RESTAURÉ" in pages[5]
    assert "HORS COURS APRÈS" in pages[5]

    bbox = subprocess.run(
        ["pdftotext", "-bbox-layout", str(pdf), "-"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    document = ET.fromstring(bbox)
    bbox_pages = document.findall(".//{*}page")
    assert len(bbox_pages) == 6

    course_word_pages = []
    for page in bbox_pages[1:5]:
        words = []
        for word in page.findall(".//{*}word"):
            words.append(
                {
                    "text": "".join(word.itertext()),
                    "x_min": float(word.attrib["xMin"]),
                    "y_min": float(word.attrib["yMin"]),
                    "y_max": float(word.attrib["yMax"]),
                }
            )
        course_word_pages.append(words)

    annotation_labels = [
        word
        for words in course_word_pages
        for word in words
        if word["text"] in {"VOCABULAIRE", "RENVOI"}
    ]
    assert len(annotation_labels) == 3
    assert all(
        word["x_min"] < 125 or word["x_min"] > 465
        for word in annotation_labels
    )

    approfondissement_pages = 0
    for page_number, words in enumerate(course_word_pages, start=2):
        if page_number % 2 == 0:
            main_x_min, main_x_max = 130, 550
        else:
            main_x_min, main_x_max = 45, 470
        title_words = [
            word
            for word in words
            if word["text"] == "POUR" and 55 < word["y_min"] < 785
        ]
        for title in title_words:
            approfondissement_pages += 1
            following_lines = {
                round(word["y_min"], 1)
                for word in words
                if title["y_min"] + 8 < word["y_min"] < title["y_min"] + 135
                and main_x_min < word["x_min"] < main_x_max
            }
            assert len(following_lines) >= 2

            body_words = [
                word
                for word in words
                if 60 < word["y_min"] < 770
                and main_x_min < word["x_min"] < main_x_max
            ]
            prior_word_bottoms = [
                word["y_max"]
                for word in body_words
                if word["y_min"] < title["y_min"] - 2
            ]
            previous_body_bottom = max(prior_word_bottoms, default=60)
            terminal_gap = title["y_min"] - previous_body_bottom
            assert terminal_gap <= 26 * 4.5 + 0.1  # pdftotext bbox rounding

    assert approfondissement_pages == 2

    for page_number, words in enumerate(course_word_pages, start=2):
        if page_number % 2 == 0:
            main_x_min, main_x_max = 130, 550
        else:
            main_x_min, main_x_max = 45, 470
        body_words = [
            word
            for word in words
            if 60 < word["y_min"] < 770
            and main_x_min < word["x_min"] < main_x_max
        ]
        last_body_y = max(word["y_max"] for word in body_words)
        assert (770 - last_body_y) / (770 - 60) < 0.25

    outside_words = [
        {
            "text": "".join(word.itertext()),
            "y_min": float(word.attrib["yMin"]),
        }
        for word in bbox_pages[5].findall(".//{*}word")
    ]
    outside_before_y = min(
        word["y_min"] for word in outside_words if word["text"] == "HORS"
    )
    outside_approfond_y = min(
        word["y_min"]
        for word in outside_words
        if word["text"] == "APPROFONDISSEMENT"
    )
    assert outside_before_y < 150
    assert outside_approfond_y - outside_before_y < 220


def test_course_trailing_float_fixture_pdf(tmp_path):
    checker = importlib.import_module("check_maquette_v5")
    fixture = tmp_path / "cours-float-final-v5.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel-v5}
\matiere{Mathématiques}\niveau{Première spécialité}
\newlength{\nxFixtureTextWidth}
\newlength{\nxFixtureMarginWidth}
\begin{document}
\setlength{\nxFixtureTextWidth}{\textwidth}
\setlength{\nxFixtureMarginWidth}{\marginparwidth}
\begin{coursV}
\rubrique{Cours}
\noindent CORPS COURS AVANT FIGURE
\begin{nxfigure}{TITRE FIGURE FINALE}
\begin{tikzpicture}
  \draw[chapcolor,line width=1pt] (0,0) rectangle (8,5);
\end{tikzpicture}
\nxcaption{DÉTAIL FIGURE FINALE}
\end{nxfigure}
\end{coursV}
\ifdim\textwidth=\nxFixtureTextWidth
  \ifdim\marginparwidth=\nxFixtureMarginWidth
    \typeout{NEXUS-V5-COURS-GEOMETRY-RESTORED}
  \else
    \PackageError{fixture}{marginparwidth non restauree}{}
  \fi
\else
  \PackageError{fixture}{textwidth non restauree}{}
\fi
\noindent HORS COURS APRÈS FIGURE
\end{document}
""",
        encoding="utf-8",
    )
    command = [
        "lualatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={tmp_path}",
        str(fixture),
    ]
    for _ in range(3):
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout[-5000:] + result.stderr

    assert "NEXUS-V5-COURS-GEOMETRY-RESTORED" in result.stdout
    assert "Float(s) lost" not in result.stdout
    assert "Too many unprocessed floats" not in result.stdout
    extracted = checker.normalize_text(
        subprocess.run(
            ["pdftotext", str(tmp_path / "cours-float-final-v5.pdf"), "-"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )
    assert extracted.count("Figure 1") == 1
    assert "TITRE FIGURE FINALE" in extracted
    assert "DÉTAIL FIGURE FINALE" in extracted
    assert extracted.index("TITRE FIGURE FINALE") < extracted.index(
        "HORS COURS APRÈS FIGURE"
    )
