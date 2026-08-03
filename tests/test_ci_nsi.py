from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/ci-nsi.yml"
MAKEFILE = ROOT / "NSI/Makefile"


def _workflow_steps() -> list[dict[str, object]]:
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    return workflow["jobs"]["gates"]["steps"]


def _named_step(name: str) -> dict[str, object]:
    matches = [step for step in _workflow_steps() if step.get("name") == name]
    assert len(matches) == 1
    return matches[0]


def test_nsi_makefile_builds_and_preflights_a_specimen():
    makefile = MAKEFILE.read_text(encoding="utf-8")

    assert "specimen" in makefile.splitlines()[0]
    assert "\nspecimen:\n" in makefile
    assert "-output-directory=build/specimen gabarits/specimen.tex" in makefile
    assert "verify_pdf(Path('build/specimen/specimen.pdf')" in makefile
    assert "Path('build/specimen/specimen.log')" in makefile


def test_nsi_workflow_always_builds_a_specimen_and_rejects_an_empty_upload():
    specimen = _named_step("Compilation specimen (gate charte)")
    assert specimen["working-directory"] == "NSI"
    assert specimen["run"] == "make specimen"

    upload = _named_step("Publier les PDF de preuve")
    assert upload["if"] == "always()"
    assert upload["with"]["path"] == "NSI/build/**/*.pdf"
    assert upload["with"]["if-no-files-found"] == "error"


def test_nsi_changed_chapters_are_detected_from_the_git_root():
    compilation = _named_step(
        "Gates d'exécution + compilation des chapitres modifiés"
    )
    command = compilation["run"]

    assert "git diff --name-only" in command
    assert "':(top)NSI/chapitres'" in command
    assert "cut -d/ -f3" in command
    assert '[ -d "chapitres/$chap/." ]' in command
