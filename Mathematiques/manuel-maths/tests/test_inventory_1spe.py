import hashlib
import json
import subprocess
from pathlib import Path

import jsonschema

from scripts.inventory_1spe import inventory
from scripts.run_baseline_build import run_build


ROOT = Path(__file__).resolve().parents[1]


def _write(path: Path, content: str = "contenu\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _fixture_tree(tmp_path: Path) -> Path:
    chapter = tmp_path / "chapitres" / "1SPE-TEST"
    statement = _write(
        chapter / "exercices" / "1SPE-TEST-EX-001.tex",
        '% META: {"id":"1SPE-TEST-EX-001","corrige_tex":'
        '"chapitres/1SPE-TEST/corriges/1SPE-TEST-CO-001.tex"}\n'
        '\\begin{exercice}{1SPE-TEST-EX-001}{1}{5}Énoncé\\end{exercice}\n',
    )
    _write(chapter / "corriges" / "1SPE-TEST-CO-001.tex")
    _write(chapter / "exercices" / "1SPE-TEST-EX-002.tex")
    _write(chapter / "exercices" / "1SPE-TEST-EX-001-CDP.tex")
    _write(chapter / "cours" / "10_C1_test.tex")
    _write(chapter / "methodes" / "1SPE-TEST-ME-001.tex")
    _write(chapter / "qcm" / "1SPE-TEST-QCM.tex")
    _write(chapter / "qcm" / "1SPE-TEST-QCM.json", "{}\n")
    _write(chapter / "evaluations" / "1SPE-TEST-EV-A.tex")
    _write(chapter / "evaluations" / "1SPE-TEST-EV-A-bareme.tex")
    _write(chapter / "remediation" / "1SPE-TEST-RE-C1.tex")
    object_sha = hashlib.sha256(statement.read_bytes()).hexdigest()
    _write(
        chapter / "validations" / "1SPE-TEST-EX-001.sympy.json",
        json.dumps(
            {
                "objet_id": "1SPE-TEST-EX-001",
                "object_sha256": object_sha,
                "verdict": "pass",
            }
        ),
    )
    _write(tmp_path / "transversal" / "formulaire.tex")
    _write(tmp_path / "figures" / "1SPE-TEST-figure.pdf", "%PDF fixture\n")
    _write(tmp_path / "gabarits" / "fonts" / "Fixture.otf", "font\n")
    _write(
        tmp_path / "validations" / "release-1spe" / "baseline-build-eleve.json",
        json.dumps({"variant": "eleve", "status": "failed"}),
    )
    return tmp_path


def test_inventory_matches_independent_filesystem_count(tmp_path):
    tree = _fixture_tree(tmp_path)
    report = inventory(tree)
    expected = len(
        [
            path
            for path in (tree / "chapitres" / "1SPE-TEST" / "exercices").glob(
                "*-EX-*.tex"
            )
            if not path.name.endswith("-CDP.tex")
        ]
    )
    assert report["chapters"]["1SPE-TEST"]["exercise_count"] == expected


def test_proof_is_current_iff_declared_sha_matches_current_object(tmp_path):
    report = inventory(_fixture_tree(tmp_path))
    assert report["proofs"]
    assert all(
        proof["current"]
        == (proof["object_sha256"] == proof["current_object_sha256"])
        for proof in report["proofs"]
    )
    assert any(proof["current"] for proof in report["proofs"])


def test_fifty_exercise_gate_is_explicit(tmp_path):
    report = inventory(_fixture_tree(tmp_path))
    assert report["chapters"]["1SPE-TEST"]["exercise_gate"] in {
        "certified",
        "needs_fix",
    }
    assert report["chapters"]["1SPE-TEST"]["exercise_gate"] == "needs_fix"
    assert report["exercise_threshold"] == 50


def test_inventory_lists_required_families_and_classifies_every_candidate(tmp_path):
    report = inventory(_fixture_tree(tmp_path))
    families = {item["family"] for item in report["objects"]}
    assert {
        "course",
        "method",
        "exercise",
        "aid",
        "solution",
        "qcm_tex",
        "qcm_json",
        "assessment",
        "grading_scale",
        "remediation",
        "transversal",
        "figure",
        "font",
        "validation",
    } <= families
    assert report["unclassified_1spe_files"] == []
    assert all(item["sha256"] and item["canonical_id"] for item in report["objects"])
    assert all(item["status"] in report["allowed_object_statuses"] for item in report["objects"])


def test_missing_solution_and_invalid_metadata_have_controlled_reasons(tmp_path):
    report = inventory(_fixture_tree(tmp_path))
    by_name = {Path(item["path"]).name: item for item in report["objects"]}
    missing = by_name["1SPE-TEST-EX-002.tex"]
    assert missing["status"] == "fix"
    assert "missing_solution" in missing["reasons"]
    assert "invalid_metadata" in missing["reasons"]
    build = by_name["baseline-build-eleve.json"]
    assert build["status"] == "review_required"
    assert "compilation_failure" in build["reasons"]


def test_build_report_is_written_on_failure(tmp_path):
    _write(tmp_path / "scripts" / "assemble_manuel.py", "# fixture\n")
    report_path = tmp_path / "report.json"

    def failed_runner(command, **kwargs):
        return subprocess.CompletedProcess(
            command,
            1,
            stdout="! Undefined control sequence.\nLaTeX Warning: Reference `x' undefined.\n",
            stderr="Overfull \\hbox (2.0pt too wide)\n",
        )

    exit_code = run_build(tmp_path, "eleve", report_path, runner=failed_runner)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert exit_code == 2
    assert report["status"] == "failed"
    assert report["command"] == [
        str(tmp_path / ".venv" / "bin" / "python"),
        "scripts/assemble_manuel.py",
        "--variant",
        "eleve",
    ]
    assert report["errors"]
    assert report["warnings"]
    assert report["references"]
    assert report["overflows"]
    assert report["pages"] == 0


def test_build_report_is_written_on_timeout(tmp_path):
    _write(tmp_path / "scripts" / "assemble_manuel.py", "# fixture\n")
    report_path = tmp_path / "timeout.json"

    def timed_out_runner(command, **kwargs):
        raise subprocess.TimeoutExpired(command, kwargs["timeout"], output="partial log")

    exit_code = run_build(tmp_path, "professeur", report_path, runner=timed_out_runner)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert exit_code == 2
    assert report["status"] == "failed"
    assert report["invocation_error"].startswith("TimeoutExpired:")
    assert report["invocation_error"] in report["errors"]


def test_build_starts_without_stale_variant_artifacts(tmp_path):
    _write(tmp_path / "scripts" / "assemble_manuel.py", "# fixture\n")
    stale = _write(tmp_path / "build" / "MANUEL_1SPE" / "MANUEL_1SPE_eleve.aux")

    def successful_runner(command, **kwargs):
        assert not stale.exists()
        build = tmp_path / "build" / "MANUEL_1SPE"
        _write(build / "MANUEL_1SPE_eleve.pdf", "%PDF fixture\n")
        _write(build / "MANUEL_1SPE_eleve.log", "Output written on fixture.pdf (12 pages).\n")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    report_path = tmp_path / "success.json"
    assert run_build(tmp_path, "eleve", report_path, runner=successful_runner) == 0
    assert json.loads(report_path.read_text(encoding="utf-8"))["pages"] == 12


def test_repository_baseline_enrichment_matches_schema_and_tree():
    baseline = json.loads(
        (ROOT / "validations" / "release-1spe" / "baseline.json").read_text(
            encoding="utf-8"
        )
    )
    schema = json.loads(
        (ROOT / "schemas" / "baseline_1spe.schema.json").read_text(encoding="utf-8")
    )
    jsonschema.validate(baseline, schema)
    enriched = baseline["historical_build_baseline"]
    assert len(enriched["chapters"]) == 10
    assert enriched["unclassified_1spe_files"] == []
    assert set(enriched["builds"]) == {"eleve", "professeur"}
    for chapter_id, chapter in enriched["chapters"].items():
        expected = len(
            [
                path
                for path in (ROOT / "chapitres" / chapter_id / "exercices").glob(
                    "*-EX-*.tex"
                )
                if not path.name.endswith("-CDP.tex")
            ]
        )
        assert chapter["exercise_count"] == expected
        assert chapter["exercise_gate"] == (
            "certified" if expected >= enriched["exercise_threshold"] else "needs_fix"
        )
