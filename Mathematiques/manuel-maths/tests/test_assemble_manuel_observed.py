from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest


MANUAL_ROOT = Path(__file__).resolve().parents[1]
GIT_ROOT = MANUAL_ROOT.parents[1]
sys.path.insert(0, str(MANUAL_ROOT / "scripts"))

import assemble_manuel  # noqa: E402
from scripts.build_manifest import _object_trace_token as manifest_trace_token  # noqa: E402


SOURCE_COMMIT = "a" * 40
SOURCE_DATE_EPOCH = 1_720_000_000
CONTROL_RELATIVE = Path(
    "Mathematiques/manuel-maths/config/reproducible-build.json"
)


class FakeProductionRunner:
    def __init__(
        self,
        *,
        failing_lualatex_pass: int | None = None,
        failing_stage: str | None = None,
        source_commit_exists: bool = True,
        source_commit_is_ancestor: bool = True,
        git_timestamp: int = SOURCE_DATE_EPOCH,
        recorder_status: int = 0,
        publish_outputs: bool = True,
        log_has_run_id: bool = True,
        fls_has_master: bool = True,
        hardlink_pdf: bool = False,
        lualatex_unavailable: bool = False,
    ) -> None:
        self.calls: list[tuple[list[str], dict[str, Any]]] = []
        self.events: list[str] = []
        self.failing_lualatex_pass = failing_lualatex_pass
        self.failing_stage = failing_stage
        self.source_commit_exists = source_commit_exists
        self.source_commit_is_ancestor = source_commit_is_ancestor
        self.git_timestamp = git_timestamp
        self.recorder_status = recorder_status
        self.publish_outputs = publish_outputs
        self.log_has_run_id = log_has_run_id
        self.fls_has_master = fls_has_master
        self.hardlink_pdf = hardlink_pdf
        self.lualatex_unavailable = lualatex_unavailable
        self.receipt_existed_at_recorder = False
        self.compile_output_modes: list[int] = []

    def __call__(self, command: list[str], **kwargs: Any) -> SimpleNamespace:
        command = [str(part) for part in command]
        self.calls.append((command, kwargs))

        if command[0] == "git":
            if "ls-files" in command:
                return self._completed(stdout="")
            if "cat-file" in command:
                status = 0 if self.source_commit_exists else 1
                return self._completed(returncode=status)
            if "merge-base" in command:
                status = 0 if self.source_commit_is_ancestor else 1
                return self._completed(returncode=status)
            if "show" in command:
                return self._completed(stdout=f"{self.git_timestamp}\n")
            raise AssertionError(f"commande Git inattendue: {command}")

        if command[0] == "lualatex" and "--version" not in command:
            if self.lualatex_unavailable:
                raise OSError("lualatex unavailable")
            self.events.append("lualatex")
            output_argument = next(
                part
                for part in command
                if part.startswith("-output-directory=")
            )
            output_directory = Path(output_argument.partition("=")[2])
            self.compile_output_modes.append(
                stat.S_IMODE(output_directory.lstat().st_mode)
            )
            pass_number = sum(event == "lualatex" for event in self.events)
            if pass_number == self.failing_lualatex_pass:
                return self._completed(returncode=3, stdout="compile failed")
            if self.publish_outputs:
                self._publish_lualatex_fixture(command)
            return self._completed(stdout="compiled")

        if command == ["lualatex", "--version"]:
            return self._version_result(
                "lualatex_version",
                stdout="LuaHBTeX, Version 1.17.0\nsecondary detail\n",
            )
        if command[0] == "pdfinfo" and command[1:] == ["-v"]:
            return self._version_result(
                "pdfinfo_version",
                stderr="pdfinfo version 24.02.0\nCopyright fixture\n",
            )
        if command[0] == "pdffonts" and command[1:] == ["-v"]:
            return self._version_result(
                "pdffonts_version",
                stderr="pdffonts version 24.02.0\nCopyright fixture\n",
            )
        if command == [sys.executable, "--version"]:
            return self._version_result(
                "python_version",
                stdout="Python 3.12.4\n",
            )
        if command[0] == "pdfinfo":
            if self.failing_stage == "pdfinfo":
                return self._completed(returncode=4, stderr="broken pdf")
            pages = 0 if self.failing_stage == "pdfinfo_zero_pages" else 17
            return self._completed(stdout=f"Title: Fixture\nPages: {pages}\n")
        if command[:2] == [sys.executable, str(Path(command[1]))]:
            self.events.append("recorder")
            self.receipt_existed_at_recorder = Path(command[-1]).is_file()
            return self._completed(returncode=self.recorder_status)
        raise AssertionError(f"commande inattendue: {command}")

    @staticmethod
    def _completed(
        *,
        returncode: int = 0,
        stdout: str = "",
        stderr: str = "",
    ) -> SimpleNamespace:
        return SimpleNamespace(
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
        )

    def _version_result(
        self,
        stage: str,
        *,
        stdout: str = "",
        stderr: str = "",
    ) -> SimpleNamespace:
        if self.failing_stage == stage:
            return self._completed(returncode=5, stderr="version failed")
        return self._completed(stdout=stdout, stderr=stderr)

    def _publish_lualatex_fixture(self, command: list[str]) -> None:
        output_argument = next(
            part for part in command if part.startswith("-output-directory=")
        )
        build = Path(output_argument.partition("=")[2])
        master_path = Path(command[-1])
        run_match = re.search(
            r"NEXUS_BUILD_RUN:([0-9a-f]{32})",
            master_path.read_text(encoding="utf-8"),
        )
        assert run_match is not None
        stem = master_path.stem
        pdf_path = build / f"{stem}.pdf"
        pdf_path.write_bytes(b"%PDF-1.7\nfixture\n")
        run_marker = (
            f"NEXUS_BUILD_RUN:{run_match.group(1)}\n"
            if self.log_has_run_id
            else ""
        )
        (build / f"{stem}.log").write_text(
            run_marker + f"Output written on {stem}.pdf (17 pages).\n",
            encoding="utf-8",
        )
        fls_input = str(master_path) if self.fls_has_master else "/wrong/master.tex"
        (build / f"{stem}.fls").write_text(
            f"INPUT {fls_input}\nOUTPUT {pdf_path}\n",
            encoding="utf-8",
        )
        if self.hardlink_pdf:
            hardlink = pdf_path.with_suffix(".hardlink.pdf")
            hardlink.unlink(missing_ok=True)
            os.link(pdf_path, hardlink)


def _write_control(
    git_root: Path,
    payload: dict[str, object] | None = None,
) -> Path:
    control_path = git_root / CONTROL_RELATIVE
    control_path.parent.mkdir(parents=True, exist_ok=True)
    control_path.write_text(
        json.dumps(
            payload
            if payload is not None
            else {
                "schema_version": 1,
                "source_commit": SOURCE_COMMIT,
                "source_date_epoch": SOURCE_DATE_EPOCH,
            }
        ),
        encoding="utf-8",
    )
    return control_path


def _proof_paths(manual_root: Path) -> dict[str, Path]:
    build = manual_root / "build/MANUEL_1SPE"
    stem = "MANUEL_1SPE_professeur"
    return {
        "build": build,
        "master": build / f"{stem}.tex",
        "pdf": build / f"{stem}.pdf",
        "log": build / f"{stem}.log",
        "fls": build / f"{stem}.fls",
        "report": build / f"{stem}.preflight.json",
        "receipt": build / f"{stem}.receipt.json",
    }


def _seed_prior_canonical_outputs(paths: dict[str, Path]) -> dict[str, bytes]:
    paths["build"].mkdir(parents=True, exist_ok=True)
    previous = {
        "master": b"old canonical master\n",
        "pdf": b"%PDF-1.7\nold canonical pdf\n",
        "log": b"old canonical log\n",
        "fls": b"INPUT /old/canonical/master.tex\n",
        "report": b"old preflight proof\n",
        "receipt": b"old receipt proof\n",
    }
    for role, payload in previous.items():
        paths[role].write_bytes(payload)
    return previous


def _private_run_directories(paths: dict[str, Path]) -> list[Path]:
    return list(paths["build"].glob(".MANUEL_1SPE_professeur.*.run"))


def _install_orchestration_fixture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    runner: FakeProductionRunner | None = None,
    verify_status: int = 0,
    control_payload: dict[str, object] | None = None,
) -> tuple[Path, FakeProductionRunner, list[int], dict[str, Path]]:
    manual_root = tmp_path / "Mathematiques/manuel-maths"
    manual_root.mkdir(parents=True)
    _write_control(tmp_path, control_payload)
    selected_runner = runner or FakeProductionRunner()
    verify_pass_counts: list[int] = []

    def fake_verify(
        pdf_path: Path,
        log_path: Path,
        **_kwargs: Any,
    ) -> int:
        del pdf_path, log_path
        count = sum(
            command[0] == "lualatex" and "--version" not in command
            for command, _kwargs in selected_runner.calls
        )
        verify_pass_counts.append(count)
        selected_runner.events.append("verify_pdf")
        return verify_status

    monkeypatch.setattr(assemble_manuel, "ROOT", manual_root)
    monkeypatch.setattr(
        assemble_manuel,
        "load_tracked_paths",
        lambda *_args, **_kwargs: frozenset(),
    )
    monkeypatch.setattr(
        assemble_manuel,
        "render_master",
        lambda _variant, run_id, **_kwargs: (
            "\\documentclass{article}\n"
            "\\begin{document}\n"
            f"\\typeout{{NEXUS_BUILD_RUN:{run_id}}}\n"
            "fixture\n"
            "\\end{document}\n"
        ),
    )
    monkeypatch.setattr(assemble_manuel, "verify_pdf", fake_verify)
    return (
        manual_root,
        selected_runner,
        verify_pass_counts,
        _proof_paths(manual_root),
    )


def _commit_fixture(repository: Path, *paths: Path) -> None:
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    subprocess.run(
        ["git", "-C", str(repository), "add", "--", *map(str, paths)],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "-c",
            "user.name=Observed Assembler Tests",
            "-c",
            "user.email=observed@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        check=True,
    )


def _professor_paths() -> list[str]:
    return [
        path.relative_to(GIT_ROOT).as_posix()
        for chapter in assemble_manuel.CHAPITRES
        for path in assemble_manuel.collect_chapter(
            MANUAL_ROOT / "chapitres" / chapter,
            "professeur",
        )
    ]


def _student_paths() -> list[str]:
    return [
        path.relative_to(GIT_ROOT).as_posix()
        for chapter in assemble_manuel.CHAPITRES
        for path in assemble_manuel.collect_chapter(
            MANUAL_ROOT / "chapitres" / chapter,
            "eleve",
        )
    ]


def _marked_blocks(master: str) -> list[tuple[str, str, str]]:
    return re.findall(
        r"\\typeout\{NEXUS_OBJECT_BEGIN:([0-9a-f]{40})\}\n"
        r"(\\input\{([^}]+)\})\n"
        r"\\typeout\{NEXUS_OBJECT_END:\1\}",
        master,
    )


def test_resolve_git_root_from_nested_manual_directory() -> None:
    assert assemble_manuel.resolve_git_root(MANUAL_ROOT / "chapitres") == GIT_ROOT


def test_canonical_tracked_path_is_git_relative_and_manual_scoped() -> None:
    canonical = assemble_manuel.canonical_tracked_path(
        "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/00_ouverture.tex",
        GIT_ROOT,
    )

    assert canonical.startswith("Mathematiques/manuel-maths/")
    assert not Path(canonical).is_absolute()


@pytest.mark.parametrize(
    "hostile_path",
    [
        str(
            GIT_ROOT
            / "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/00_ouverture.tex"
        ),
        "Mathematiques/manuel-maths/../manuel-maths/scripts/assemble_manuel.py",
        r"Mathematiques\manuel-maths\scripts\assemble_manuel.py",
    ],
    ids=["absolute", "parent", "backslash"],
)
def test_canonical_tracked_path_rejects_hostile_spelling(hostile_path: str) -> None:
    with pytest.raises(ValueError, match="canonique"):
        assemble_manuel.canonical_tracked_path(hostile_path, GIT_ROOT)


def test_canonical_tracked_path_rejects_tracked_symlink(tmp_path: Path) -> None:
    target = tmp_path / "Mathematiques/manuel-maths/objects/target.tex"
    target.parent.mkdir(parents=True)
    target.write_text("Objet suivi\n", encoding="utf-8")
    link = target.with_name("link.tex")
    link.symlink_to(target.name)
    _commit_fixture(tmp_path, target.relative_to(tmp_path), link.relative_to(tmp_path))

    with pytest.raises(ValueError, match="symbolique"):
        assemble_manuel.canonical_tracked_path(
            link.relative_to(tmp_path).as_posix(),
            tmp_path,
        )


def test_canonical_tracked_path_rejects_untracked_file(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    source = tmp_path / "Mathematiques/manuel-maths/objects/untracked.tex"
    source.parent.mkdir(parents=True)
    source.write_text("Objet non suivi\n", encoding="utf-8")

    with pytest.raises(ValueError, match="non suivi"):
        assemble_manuel.canonical_tracked_path(
            source.relative_to(tmp_path).as_posix(),
            tmp_path,
        )


def test_canonical_tracked_path_treats_git_metacharacters_literally(
    tmp_path: Path,
) -> None:
    tracked = tmp_path / "Mathematiques/manuel-maths/objects/object1.tex"
    tracked.parent.mkdir(parents=True)
    tracked.write_text("Objet suivi\n", encoding="utf-8")
    _commit_fixture(tmp_path, tracked.relative_to(tmp_path))
    untracked_pathspec = tracked.with_name("object?.tex")
    untracked_pathspec.write_text("Objet non suivi\n", encoding="utf-8")

    with pytest.raises(ValueError, match="non suivi"):
        assemble_manuel.canonical_tracked_path(
            untracked_pathspec.relative_to(tmp_path).as_posix(),
            tmp_path,
        )


def test_assembler_trace_token_is_the_manifest_protocol_token() -> None:
    canonical = (
        "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/"
        "cours/00_ouverture.tex"
    )

    assert assemble_manuel.object_trace_token(canonical) == manifest_trace_token(
        canonical
    )


def test_wrap_object_input_uses_exact_balanced_markers() -> None:
    canonical = (
        "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/"
        "cours/00_ouverture.tex"
    )
    token = manifest_trace_token(canonical)

    assert assemble_manuel.wrap_object_input(
        "chapitres/1SPE-SUITES/cours/00_ouverture.tex",
        canonical,
    ) == "\n".join(
        [
            f"\\typeout{{NEXUS_OBJECT_BEGIN:{token}}}",
            "\\input{chapitres/1SPE-SUITES/cours/00_ouverture.tex}",
            f"\\typeout{{NEXUS_OBJECT_END:{token}}}",
        ]
    )


def test_render_master_loads_tracked_inventory_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_loader = assemble_manuel.load_tracked_paths
    calls: list[Path] = []

    def recording_loader(git_root: Path) -> frozenset[str]:
        calls.append(git_root)
        return real_loader(git_root)

    monkeypatch.setattr(assemble_manuel, "load_tracked_paths", recording_loader)

    master = assemble_manuel.render_master("professeur", "b" * 32)

    assert master.count("NEXUS_OBJECT_BEGIN:") > 1
    assert calls == [GIT_ROOT]


def test_render_master_marks_every_object_once_in_collection_order() -> None:
    master = assemble_manuel.render_master("professeur", "a" * 32)
    expected_paths = _professor_paths()
    blocks = _marked_blocks(master)

    assert len(blocks) == len(expected_paths)
    assert [input_path for _, _, input_path in blocks] == [
        path.removeprefix("Mathematiques/manuel-maths/") for path in expected_paths
    ]
    assert [token for token, _, _ in blocks] == [
        manifest_trace_token(path) for path in expected_paths
    ]
    assert master.count("NEXUS_OBJECT_BEGIN:") == len(expected_paths)
    assert master.count("NEXUS_OBJECT_END:") == len(expected_paths)
    assert len(re.findall(r"NEXUS_OBJECT_BEGIN:[0-9a-f]{40}", master)) == len(
        expected_paths
    )
    assert len(re.findall(r"NEXUS_OBJECT_END:[0-9a-f]{40}", master)) == len(
        expected_paths
    )


def test_render_master_has_one_run_marker_and_no_marked_transversal_input() -> None:
    run_id = "0123456789abcdef" * 2
    master = assemble_manuel.render_master("professeur", run_id)

    assert re.findall(r"NEXUS_BUILD_RUN:([0-9a-f]{32})", master) == [run_id]
    assert master.count("NEXUS_BUILD_RUN:") == 1
    marked_inputs = {input_path for _, _, input_path in _marked_blocks(master)}
    for path in (
        "transversal/page_de_garde",
        "transversal/avant_propos",
        "transversal/mode_emploi",
        "transversal/index_capacites",
        "transversal/formulaire",
        "transversal/memo_python",
    ):
        assert master.count(f"\\input{{{path}}}") == 1
        assert path not in marked_inputs
        assert not re.search(
            rf"NEXUS_OBJECT_BEGIN:[^\n]+\n\\input\{{{re.escape(path)}\}}",
            master,
        )


def test_render_master_configures_closed_student_redaction() -> None:
    student = assemble_manuel.render_master("eleve", "1" * 32)
    professor = assemble_manuel.render_master("professeur", "2" * 32)

    assert "\\nxVersionProfesseurfalse" in student
    assert "\\RenewDocumentEnvironment{corrige}{m +b}{}{}" in student
    assert "\\renewcommand{\\baremeIndicatif}[1]{}" in student
    assert "\\nxVersionProfesseurtrue" in professor
    assert "\\RenewDocumentEnvironment{corrige}{m +b}{}{}" not in professor


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Exercice 2 1SPE-SUITES-EX-001", "identifiant interne"),
        ("Corrigé — Évaluation A", "corrigé"),
        ("CORRIGES", "corrigé"),
        ("Barème indicatif : 4 points", "barème enseignant"),
        ("Note professeur : relancer", "note enseignant"),
    ],
)
def test_student_pdf_text_gate_rejects_teacher_leaks(
    text: str,
    expected: str,
) -> None:
    assert expected in assemble_manuel.student_text_violations(text)


def test_student_pdf_text_gate_accepts_student_instructions() -> None:
    assert assemble_manuel.student_text_violations(
        "Compléter le programme. Solution : x appartient à [0 ; 1]."
    ) == []


def test_real_professor_order_matches_declared_inventory() -> None:
    inventory = json.loads(
        (GIT_ROOT / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8")
    )
    assembly = next(
        item
        for item in inventory["assemblies"]
        if item["assembly_id"] == "math:manual:1SPE:professeur"
    )
    professor_paths = _professor_paths()

    assert len(professor_paths) == 1334
    assert all(
        path.startswith("Mathematiques/manuel-maths/") for path in professor_paths
    )
    assert professor_paths == assembly["included_objects"]


def test_real_student_order_keeps_evaluations_and_excludes_teacher_objects() -> None:
    inventory = json.loads(
        (GIT_ROOT / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8")
    )
    assembly = next(
        item
        for item in inventory["assemblies"]
        if item["assembly_id"] == "math:manual:1SPE:eleve"
    )
    student_paths = _student_paths()

    assert len(student_paths) == 852
    assert student_paths == assembly["included_objects"]
    assert sum("/evaluations/" in path for path in student_paths) == 18
    assert all("/corriges/" not in path for path in student_paths)
    assert all(not path.endswith("-corrige.tex") for path in student_paths)
    assert all(
        assemble_manuel.object_type(MANUAL_ROOT / path.removeprefix(
            "Mathematiques/manuel-maths/"
        ))
        in assemble_manuel.ELEVE_ALLOWED_TYPES
        for path in student_paths
    )


def test_student_selection_fails_closed_without_valid_object_metadata(
    tmp_path: Path,
) -> None:
    chapter = tmp_path / "1SPE-TEST"
    course = chapter / "cours/10_C1_test.tex"
    course.parent.mkdir(parents=True)
    course.write_text("Contenu sans META\n", encoding="utf-8")

    with pytest.raises(assemble_manuel.AssemblyError, match="META"):
        assemble_manuel.collect_chapter(chapter, "eleve")


def test_observed_build_runs_three_strict_passes_then_publishes_closed_proofs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manual_root, runner, verify_pass_counts, paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
    )
    previous = _seed_prior_canonical_outputs(paths)
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "999")
    monkeypatch.setenv("TZ", "Africa/Tunis")
    monkeypatch.setenv("LC_ALL", "host-locale")
    monkeypatch.setenv("PYTHONHASHSEED", "random")
    monkeypatch.setenv("OPENROUTER_API_KEY", "must-not-leak")
    monkeypatch.setenv("DATABASE_URL", "postgresql://must-not-leak")
    monkeypatch.setenv("GIT_DIR", "/hostile/git-dir")
    monkeypatch.setenv("GIT_WORK_TREE", "/hostile/work-tree")
    monkeypatch.setenv("GIT_INDEX_FILE", "/hostile/index")

    assert assemble_manuel.main(
        "professeur",
        record_observed=True,
        runner=runner,
    ) == 0

    lualatex_calls = [
        (command, kwargs)
        for command, kwargs in runner.calls
        if command[0] == "lualatex" and "--version" not in command
    ]
    assert len(lualatex_calls) == 3
    output_directories = {
        Path(
            next(
                part.partition("=")[2]
                for part in command
                if part.startswith("-output-directory=")
            )
        )
        for command, _kwargs in lualatex_calls
    }
    assert len(output_directories) == 1
    run_directory = output_directories.pop()
    assert run_directory.parent == paths["build"]
    assert re.fullmatch(
        r"\.MANUEL_1SPE_professeur\.[0-9a-f]{32}\.run",
        run_directory.name,
    )
    assert runner.compile_output_modes == [0o700, 0o700, 0o700]
    expected_command = [
        "lualatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-recorder",
        f"-output-directory={run_directory}",
        str(paths["master"]),
    ]
    assert [command for command, _kwargs in lualatex_calls] == [
        expected_command,
        expected_command,
        expected_command,
    ]
    assert verify_pass_counts == [3]
    assert runner.events[:4] == ["lualatex"] * 3 + ["verify_pdf"]

    controlled = {
        "SOURCE_DATE_EPOCH": str(SOURCE_DATE_EPOCH),
        "FORCE_SOURCE_DATE": "1",
        "TZ": "UTC",
        "LC_ALL": "C.UTF-8",
        "PYTHONHASHSEED": "0",
    }
    subprocess_environments = [kwargs["env"] for _command, kwargs in runner.calls]
    assert all(
        all(environment[key] == value for key, value in controlled.items())
        for environment in subprocess_environments
    )
    assert len({id(environment) for environment in subprocess_environments}) == len(
        subprocess_environments
    )
    allowed_environment = {"PATH", "HOME", *controlled}
    assert all(
        set(environment) <= allowed_environment
        for environment in subprocess_environments
    )
    assert all(
        "OPENROUTER_API_KEY" not in environment
        and "DATABASE_URL" not in environment
        and not any(key.startswith("GIT_") for key in environment)
        for environment in subprocess_environments
    )

    report = json.loads(paths["report"].read_text(encoding="utf-8"))
    receipt = json.loads(paths["receipt"].read_text(encoding="utf-8"))
    reproducibility = {
        "config_path": CONTROL_RELATIVE.as_posix(),
        "source_commit": SOURCE_COMMIT,
        "source_date_epoch": SOURCE_DATE_EPOCH,
        "force_source_date": "1",
        "timezone": "UTC",
        "locale": "C.UTF-8",
        "pythonhashseed": "0",
    }
    tool_versions = {
        "lualatex": "LuaHBTeX, Version 1.17.0",
        "pdfinfo": "pdfinfo version 24.02.0",
        "pdffonts": "pdffonts version 24.02.0",
        "python": "Python 3.12.4",
    }
    git_relative_prefix = "Mathematiques/manuel-maths/build/MANUEL_1SPE"

    assert set(report) == {
        "checks",
        "page_count",
        "passed",
        "pdf_path",
        "pdf_sha256",
        "reproducibility",
        "run_id",
        "tool_versions",
    }
    assert report["passed"] is True
    assert report["page_count"] == 17
    assert report["pdf_path"] == (
        f"{git_relative_prefix}/MANUEL_1SPE_professeur.pdf"
    )
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", report["pdf_sha256"])
    assert report["tool_versions"] == tool_versions
    assert report["reproducibility"] == reproducibility
    assert isinstance(report["checks"], dict)

    assert set(receipt) == {
        "compile_succeeded",
        "evidence_sha256",
        "fls_path",
        "gates",
        "generated_dependencies",
        "log_path",
        "manual",
        "master_path",
        "pdf_path",
        "preflight_report",
        "preflight_succeeded",
        "reproducibility",
        "run_id",
        "tool_versions",
        "variant",
    }
    assert receipt["compile_succeeded"] is True
    assert receipt["preflight_succeeded"] is True
    assert receipt["generated_dependencies"] == []
    assert receipt["manual"] == "1SPE"
    assert receipt["variant"] == "professeur"
    assert receipt["pdf_path"] == report["pdf_path"]
    assert receipt["master_path"] == (
        f"{git_relative_prefix}/MANUEL_1SPE_professeur.tex"
    )
    assert receipt["log_path"] == (
        f"{git_relative_prefix}/MANUEL_1SPE_professeur.log"
    )
    assert receipt["fls_path"] == (
        f"{git_relative_prefix}/MANUEL_1SPE_professeur.fls"
    )
    assert receipt["preflight_report"] == (
        f"{git_relative_prefix}/MANUEL_1SPE_professeur.preflight.json"
    )
    assert receipt["tool_versions"] == tool_versions
    assert receipt["reproducibility"] == reproducibility
    assert receipt["run_id"] == report["run_id"]
    assert re.fullmatch(r"[0-9a-f]{32}", receipt["run_id"])
    assert receipt["run_id"] in paths["master"].read_text(encoding="utf-8")
    assert set(receipt["evidence_sha256"]) == {
        "master",
        "log",
        "fls",
        "pdf",
        "preflight",
    }
    assert all(
        re.fullmatch(r"sha256:[0-9a-f]{64}", digest)
        for digest in receipt["evidence_sha256"].values()
    )
    assert receipt["evidence_sha256"]["pdf"] == report["pdf_sha256"]
    assert paths["pdf"].read_bytes() != previous["pdf"]
    assert paths["pdf"].read_bytes() == b"%PDF-1.7\nfixture\n"
    assert f"INPUT {paths['master']}\n" in paths["fls"].read_text(
        encoding="utf-8"
    )
    assert _private_run_directories(paths) == []

    recorder_command = [
        sys.executable,
        str(tmp_path / "scripts/build_manifest.py"),
        "--receipt",
        str(paths["receipt"]),
    ]
    assert [
        command for command, _kwargs in runner.calls if "--receipt" in command
    ] == [recorder_command]
    assert runner.receipt_existed_at_recorder is True

    proof_text = paths["report"].read_text(encoding="utf-8") + paths[
        "receipt"
    ].read_text(encoding="utf-8")
    assert "OPENROUTER" not in proof_text
    assert "must-not-leak" not in proof_text
    assert ".env" not in proof_text
    assert manual_root == assemble_manuel.ROOT


@pytest.mark.parametrize("failing_pass", [1, 2, 3])
def test_compile_failure_stops_immediately_and_invalidates_only_exact_stale_proofs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failing_pass: int,
) -> None:
    runner = FakeProductionRunner(failing_lualatex_pass=failing_pass)
    _manual_root, runner, verify_pass_counts, paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
        runner=runner,
    )
    previous = _seed_prior_canonical_outputs(paths)
    neighbour = paths["receipt"].with_name("other.receipt.json")
    neighbour.write_text("keep", encoding="utf-8")

    assert assemble_manuel.main(
        "professeur",
        record_observed=True,
        runner=runner,
    ) == 1

    compile_calls = [
        command
        for command, _kwargs in runner.calls
        if command[0] == "lualatex" and "--version" not in command
    ]
    assert len(compile_calls) == failing_pass
    assert verify_pass_counts == []
    assert not any(command[0] == "pdfinfo" for command, _kwargs in runner.calls)
    assert not paths["receipt"].exists()
    assert not paths["report"].exists()
    assert paths["pdf"].read_bytes() == previous["pdf"]
    assert paths["log"].read_bytes() == previous["log"]
    assert paths["fls"].read_bytes() == previous["fls"]
    assert _private_run_directories(paths) == []
    assert neighbour.read_text(encoding="utf-8") == "keep"


def test_missing_lualatex_preserves_previous_canonical_outputs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = FakeProductionRunner(lualatex_unavailable=True)
    _manual_root, runner, verify_pass_counts, paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
        runner=runner,
    )
    previous = _seed_prior_canonical_outputs(paths)

    assert assemble_manuel.main(
        "professeur",
        record_observed=True,
        runner=runner,
    ) == 1

    assert verify_pass_counts == []
    assert paths["pdf"].read_bytes() == previous["pdf"]
    assert paths["log"].read_bytes() == previous["log"]
    assert paths["fls"].read_bytes() == previous["fls"]
    assert not paths["report"].exists()
    assert not paths["receipt"].exists()
    assert _private_run_directories(paths) == []


@pytest.mark.parametrize(
    ("failing_stage", "verify_status"),
    [
        (None, 1),
        ("pdfinfo", 0),
        ("pdfinfo_zero_pages", 0),
        ("lualatex_version", 0),
        ("pdfinfo_version", 0),
        ("pdffonts_version", 0),
        ("python_version", 0),
    ],
    ids=[
        "verify-pdf",
        "pdfinfo",
        "zero-pages",
        "lualatex-version",
        "pdfinfo-version",
        "pdffonts-version",
        "python-version",
    ],
)
def test_preflight_or_version_failure_never_writes_report_or_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failing_stage: str | None,
    verify_status: int,
) -> None:
    runner = FakeProductionRunner(failing_stage=failing_stage)
    _manual_root, runner, verify_pass_counts, paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
        runner=runner,
        verify_status=verify_status,
    )
    previous = _seed_prior_canonical_outputs(paths)

    assert assemble_manuel.main(
        "professeur",
        record_observed=True,
        runner=runner,
    ) == 1

    assert len(
        [
            command
            for command, _kwargs in runner.calls
            if command[0] == "lualatex" and "--version" not in command
        ]
    ) == 3
    assert verify_pass_counts == [3]
    assert not paths["report"].exists()
    assert not paths["receipt"].exists()
    assert paths["pdf"].read_bytes() == previous["pdf"]
    assert paths["log"].read_bytes() == previous["log"]
    assert paths["fls"].read_bytes() == previous["fls"]
    assert _private_run_directories(paths) == []
    assert not any("--receipt" in command for command, _kwargs in runner.calls)


def test_ordinary_mode_builds_and_preflights_without_writing_or_recording_proofs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _manual_root, runner, verify_pass_counts, paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
    )
    paths["build"].mkdir(parents=True, exist_ok=True)
    paths["report"].write_text("stale report", encoding="utf-8")
    paths["receipt"].write_text("stale receipt", encoding="utf-8")

    assert assemble_manuel.main(
        "professeur",
        record_observed=False,
        runner=runner,
    ) == 0

    assert verify_pass_counts == [3]
    assert not paths["report"].exists()
    assert not paths["receipt"].exists()
    assert not any("--receipt" in command for command, _kwargs in runner.calls)


def test_ordinary_compile_failure_invalidates_stale_proofs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = FakeProductionRunner(failing_lualatex_pass=1)
    _manual_root, runner, _verify_calls, paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
        runner=runner,
    )
    previous = _seed_prior_canonical_outputs(paths)

    assert assemble_manuel.main("professeur", runner=runner) == 1
    assert not paths["report"].exists()
    assert not paths["receipt"].exists()
    assert paths["pdf"].read_bytes() == previous["pdf"]
    assert paths["log"].read_bytes() == previous["log"]
    assert paths["fls"].read_bytes() == previous["fls"]
    assert _private_run_directories(paths) == []


def test_recorder_failure_status_is_propagated_and_success_receipt_is_removed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = FakeProductionRunner(recorder_status=9)
    _manual_root, runner, _verify_calls, paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
        runner=runner,
    )

    assert assemble_manuel.main(
        "professeur",
        record_observed=True,
        runner=runner,
    ) == 9

    assert runner.receipt_existed_at_recorder is True
    assert not paths["receipt"].exists()
    assert paths["report"].is_file()
    assert [
        command for command, _kwargs in runner.calls if "--receipt" in command
    ] == [
        [
            sys.executable,
            str(tmp_path / "scripts/build_manifest.py"),
            "--receipt",
            str(paths["receipt"]),
        ]
    ]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {
            "schema_version": 2,
            "source_commit": SOURCE_COMMIT,
            "source_date_epoch": SOURCE_DATE_EPOCH,
        },
        {
            "schema_version": 1,
            "source_commit": "A" * 40,
            "source_date_epoch": SOURCE_DATE_EPOCH,
        },
        {
            "schema_version": 1,
            "source_commit": SOURCE_COMMIT,
            "source_date_epoch": 0,
        },
        {
            "schema_version": 1,
            "source_commit": SOURCE_COMMIT,
            "source_date_epoch": SOURCE_DATE_EPOCH,
            "unexpected": True,
        },
    ],
    ids=["missing-fields", "schema-version", "commit-shape", "epoch", "extra"],
)
def test_invalid_reproducibility_control_is_rejected_before_lualatex(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    payload: dict[str, object],
) -> None:
    manual_root, runner, _verify_calls, paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
        control_payload=payload,
    )
    del manual_root
    previous = _seed_prior_canonical_outputs(paths)

    assert assemble_manuel.main("professeur", runner=runner) == 1
    assert not any(command[0] == "lualatex" for command, _kwargs in runner.calls)
    assert paths["master"].read_bytes() == previous["master"]
    assert paths["pdf"].read_bytes() == previous["pdf"]
    assert paths["log"].read_bytes() == previous["log"]
    assert paths["fls"].read_bytes() == previous["fls"]
    assert not paths["report"].exists()
    assert not paths["receipt"].exists()
    assert _private_run_directories(paths) == []


def test_missing_reproducibility_control_is_rejected_before_any_subprocess(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manual_root, runner, _verify_calls, _paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
    )
    (tmp_path / CONTROL_RELATIVE).unlink()
    assert manual_root == assemble_manuel.ROOT

    assert assemble_manuel.main("professeur", runner=runner) == 1
    assert runner.calls == []


@pytest.mark.parametrize(
    "runner",
    [
        FakeProductionRunner(source_commit_exists=False),
        FakeProductionRunner(source_commit_is_ancestor=False),
        FakeProductionRunner(git_timestamp=SOURCE_DATE_EPOCH + 1),
    ],
    ids=["missing-commit", "non-ancestor", "timestamp-mismatch"],
)
def test_unproved_reproducibility_commit_is_rejected_before_lualatex(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    runner: FakeProductionRunner,
) -> None:
    _install_orchestration_fixture(tmp_path, monkeypatch, runner=runner)

    assert assemble_manuel.main("professeur", runner=runner) == 1
    assert not any(command[0] == "lualatex" for command, _kwargs in runner.calls)


def test_real_lualatex_reproducible_run_id(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()

    def git(*arguments: str, timestamp: int | None = None) -> str:
        environment = assemble_manuel._allowlisted_environment()
        if timestamp is not None:
            git_date = f"{timestamp} +0000"
            environment["GIT_AUTHOR_DATE"] = git_date
            environment["GIT_COMMITTER_DATE"] = git_date
        completed = subprocess.run(
            ["git", "-C", str(repository), *arguments],
            check=True,
            capture_output=True,
            text=True,
            env=environment,
        )
        return completed.stdout.strip()

    git("init", "-q")
    git("config", "user.name", "Observed Assembler Tests")
    git("config", "user.email", "observed@example.invalid")
    source = repository / "source.txt"
    source.write_text("source A\n", encoding="utf-8")
    git("add", "--", source.name)
    source_timestamp = 1_700_000_000
    git("commit", "-qm", "source A", timestamp=source_timestamp)
    source_commit = git("rev-parse", "HEAD")
    assert int(git("show", "-s", "--format=%ct", source_commit)) == source_timestamp

    control = repository / CONTROL_RELATIVE
    control.parent.mkdir(parents=True)
    control.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_commit": source_commit,
                "source_date_epoch": source_timestamp,
            }
        ),
        encoding="utf-8",
    )
    git("add", "--", CONTROL_RELATIVE.as_posix())
    git("commit", "-qm", "reproducibility control", timestamp=source_timestamp + 60)

    run_ids = ("a" * 32, "b" * 32)
    build_directories = (repository / "build-a", repository / "build-b")
    documents: list[Path] = []
    for build_directory, run_id in zip(build_directories, run_ids, strict=True):
        build_directory.mkdir()
        document = build_directory / "document.tex"
        document.write_text(
            "\\documentclass{article}\n"
            "\\begin{document}\n"
            f"\\typeout{{NEXUS_BUILD_RUN:{run_id}}}\n"
            "Deterministic fixture.\n"
            "\\end{document}\n",
            encoding="utf-8",
        )
        documents.append(document)
    normalized_documents = [
        document.read_text(encoding="utf-8").replace(run_id, "<run_id>")
        for document, run_id in zip(documents, run_ids, strict=True)
    ]
    assert normalized_documents[0] == normalized_documents[1]

    def compile_document(
        document: Path,
        output_directory: Path,
        environment: dict[str, str],
    ) -> subprocess.CompletedProcess[str]:
        command = [
            "lualatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-recorder",
            f"-output-directory={output_directory}",
            str(document),
        ]
        return assemble_manuel._run_with_environment(
            subprocess.run,
            environment,
            command,
            capture_output=True,
            text=True,
            cwd=repository,
            errors="replace",
            check=False,
        )

    payload_a, _reproducibility_a, environment_a = (
        assemble_manuel._load_reproducibility_control(
            repository,
            runner=subprocess.run,
        )
    )
    head_a = git("rev-parse", "HEAD")
    head_timestamp_a = int(git("show", "-s", "--format=%ct", head_a))
    result_a = compile_document(documents[0], build_directories[0], environment_a)

    artifact = repository / "artifact.txt"
    artifact.write_text("changes HEAD only\n", encoding="utf-8")
    git("add", "--", artifact.name)
    git("commit", "-qm", "dummy artifact", timestamp=source_timestamp + 120)

    payload_b, _reproducibility_b, environment_b = (
        assemble_manuel._load_reproducibility_control(
            repository,
            runner=subprocess.run,
        )
    )
    head_b = git("rev-parse", "HEAD")
    head_timestamp_b = int(git("show", "-s", "--format=%ct", head_b))
    result_b = compile_document(documents[1], build_directories[1], environment_b)

    assert result_a.returncode == 0, result_a.stdout + result_a.stderr
    assert result_b.returncode == 0, result_b.stdout + result_b.stderr
    assert head_a != head_b
    assert head_timestamp_a != head_timestamp_b
    assert payload_a == payload_b
    assert payload_a["source_commit"] == source_commit
    assert payload_a["source_date_epoch"] == source_timestamp
    assert environment_a["SOURCE_DATE_EPOCH"] == str(source_timestamp)
    assert environment_b["SOURCE_DATE_EPOCH"] == str(source_timestamp)

    logs = [
        build_directory.joinpath("document.log").read_text(
            encoding="utf-8",
            errors="replace",
        )
        for build_directory in build_directories
    ]
    assert run_ids[0] in logs[0] and run_ids[1] not in logs[0]
    assert run_ids[1] in logs[1] and run_ids[0] not in logs[1]

    pdfs = [build_directory / "document.pdf" for build_directory in build_directories]
    pdf_bytes = [pdf.read_bytes() for pdf in pdfs]
    pdf_sha256 = [hashlib.sha256(content).hexdigest() for content in pdf_bytes]
    assert pdf_sha256[0] == pdf_sha256[1]
    assert pdf_bytes[0] == pdf_bytes[1]
    assert all(
        run_id.encode("ascii") not in pdf
        for run_id in run_ids
        for pdf in pdf_bytes
    )

    pdfinfo_results = [
        assemble_manuel._run_with_environment(
            subprocess.run,
            environment,
            ["pdfinfo", str(pdf)],
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
        )
        for pdf, environment in zip(pdfs, (environment_a, environment_b), strict=True)
    ]
    assert all(result.returncode == 0 for result in pdfinfo_results)
    assert pdfinfo_results[0].stdout == pdfinfo_results[1].stdout

    variable_pdf_metadata = re.compile(
        rb"/(?:CreationDate|ModDate)\s*\([^)]*\)|/ID\s*\[[^]]*\]",
        re.DOTALL,
    )
    assert variable_pdf_metadata.findall(pdf_bytes[0]) == (
        variable_pdf_metadata.findall(pdf_bytes[1])
    )


def test_git_root_resolution_strips_hostile_git_environment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[dict[str, str]] = []
    monkeypatch.setenv("OPENROUTER_API_KEY", "secret")
    monkeypatch.setenv("GIT_DIR", "/hostile/git-dir")
    monkeypatch.setenv("GIT_WORK_TREE", "/hostile/work-tree")
    monkeypatch.setenv("GIT_INDEX_FILE", "/hostile/index")

    def runner(_command: list[str], **kwargs: Any) -> SimpleNamespace:
        captured.append(kwargs["env"])
        return SimpleNamespace(returncode=0, stdout=f"{tmp_path}\n", stderr="")

    assert assemble_manuel.resolve_git_root(tmp_path, runner=runner) == tmp_path
    assert len(captured) == 1
    assert "OPENROUTER_API_KEY" not in captured[0]
    assert not any(key.startswith("GIT_") for key in captured[0])


def test_symlinked_build_directory_is_rejected_before_subprocess_or_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manual_root, runner, _verify_calls, _paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
    )
    external = tmp_path / "external-build"
    external.mkdir()
    (manual_root / "build").symlink_to(external, target_is_directory=True)

    assert assemble_manuel.main("professeur", runner=runner) == 1
    assert runner.calls == []
    assert list(external.iterdir()) == []


@pytest.mark.parametrize("existing_kind", ["directory", "symlink"])
def test_preexisting_private_run_directory_is_rejected_without_reuse(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    existing_kind: str,
) -> None:
    _manual_root, runner, _verify_calls, paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
    )
    previous = _seed_prior_canonical_outputs(paths)
    run_id = "0123456789abcdef" * 2
    monkeypatch.setattr(assemble_manuel.secrets, "token_hex", lambda _size: run_id)
    run_directory = (
        paths["build"] / f".MANUEL_1SPE_professeur.{run_id}.run"
    )
    if existing_kind == "directory":
        run_directory.mkdir(mode=0o700)
        sentinel = run_directory / "sentinel"
        sentinel.write_text("do not reuse", encoding="utf-8")
    else:
        external = tmp_path / "external-run"
        external.mkdir()
        sentinel = external / "sentinel"
        sentinel.write_text("do not follow", encoding="utf-8")
        run_directory.symlink_to(external, target_is_directory=True)

    assert assemble_manuel.main(
        "professeur",
        record_observed=True,
        runner=runner,
    ) == 1

    assert not any(
        command[0] == "lualatex" and "--version" not in command
        for command, _kwargs in runner.calls
    )
    assert paths["pdf"].read_bytes() == previous["pdf"]
    assert not paths["report"].exists()
    assert not paths["receipt"].exists()
    assert sentinel.read_text(encoding="utf-8") in {"do not reuse", "do not follow"}


def test_promotion_failure_before_pdf_preserves_previous_pdf_and_cleans_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _manual_root, runner, _verify_calls, paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
    )
    previous = _seed_prior_canonical_outputs(paths)
    promotion_destinations: list[Path] = []

    def fail_before_pdf(source: Path, destination: Path) -> None:
        promotion_destinations.append(destination)
        if destination == paths["fls"]:
            raise OSError("simulated FLS promotion failure")
        destination.write_bytes(source.read_bytes())

    monkeypatch.setattr(
        assemble_manuel,
        "_atomic_promote_file",
        fail_before_pdf,
        raising=False,
    )

    assert assemble_manuel.main(
        "professeur",
        record_observed=True,
        runner=runner,
    ) == 1

    assert promotion_destinations == [paths["log"], paths["fls"]]
    assert paths["pdf"].read_bytes() == previous["pdf"]
    assert not paths["report"].exists()
    assert not paths["receipt"].exists()
    assert _private_run_directories(paths) == []


def test_success_status_without_fresh_compiler_outputs_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = FakeProductionRunner(publish_outputs=False)
    _manual_root, runner, verify_calls, paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
        runner=runner,
    )
    previous = _seed_prior_canonical_outputs(paths)

    assert assemble_manuel.main(
        "professeur",
        record_observed=True,
        runner=runner,
    ) == 1
    assert verify_calls == []
    assert paths["pdf"].read_bytes() == previous["pdf"]
    assert paths["log"].read_bytes() == previous["log"]
    assert paths["fls"].read_bytes() == previous["fls"]
    assert not paths["report"].exists()
    assert not paths["receipt"].exists()
    assert _private_run_directories(paths) == []


@pytest.mark.parametrize(
    "runner",
    [
        FakeProductionRunner(log_has_run_id=False),
        FakeProductionRunner(fls_has_master=False),
        FakeProductionRunner(hardlink_pdf=True),
    ],
    ids=["wrong-run-id", "master-not-in-fls", "hardlinked-pdf"],
)
def test_invalid_compiler_evidence_is_rejected_before_preflight(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    runner: FakeProductionRunner,
) -> None:
    _manual_root, runner, verify_calls, paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
        runner=runner,
    )

    assert assemble_manuel.main(
        "professeur",
        record_observed=True,
        runner=runner,
    ) == 1
    assert verify_calls == []
    assert not paths["report"].exists()
    assert not paths["receipt"].exists()


def test_concurrent_build_lock_refuses_second_build_before_invalidation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _manual_root, runner, _verify_calls, paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
    )
    paths["build"].mkdir(parents=True, exist_ok=True)
    paths["receipt"].write_text("preserve while locked", encoding="utf-8")
    lock_path = paths["build"] / ".MANUEL_1SPE_professeur.lock"
    with lock_path.open("w", encoding="utf-8") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert assemble_manuel.main(
            "professeur",
            record_observed=True,
            runner=runner,
        ) == 1

    assert paths["receipt"].read_text(encoding="utf-8") == "preserve while locked"
    assert runner.calls == []


def test_mutation_during_preflight_invalidates_observed_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _manual_root, runner, _verify_calls, paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
    )

    def mutating_verify(
        _pdf_path: Path,
        log_path: Path,
        **_kwargs: Any,
    ) -> int:
        log_path.write_text(
            log_path.read_text(encoding="utf-8") + "mutated\n",
            encoding="utf-8",
        )
        return 0

    monkeypatch.setattr(assemble_manuel, "verify_pdf", mutating_verify)

    assert assemble_manuel.main(
        "professeur",
        record_observed=True,
        runner=runner,
    ) == 1
    assert not paths["report"].exists()
    assert not paths["receipt"].exists()


def test_pdf_digest_is_recomputed_after_published_preflight_and_before_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _manual_root, runner, _verify_calls, paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
    )
    real_sha256_path = assemble_manuel._sha256_path
    report_states: list[bool] = []

    def recording_sha256(path: Path) -> str:
        if path == paths["pdf"]:
            report_states.append(paths["report"].exists())
        return real_sha256_path(path)

    monkeypatch.setattr(assemble_manuel, "_sha256_path", recording_sha256)

    assert assemble_manuel.main(
        "professeur",
        record_observed=True,
        runner=runner,
    ) == 0
    assert report_states == [False, True]


def test_atomic_json_replace_failure_preserves_old_destination_and_cleans_temp(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "proof.json"
    destination.write_bytes(b"old proof\n")

    def failing_replace(_self: Path, _target: Path) -> Path:
        raise OSError("replace failed")

    monkeypatch.setattr(Path, "replace", failing_replace)

    with pytest.raises(OSError, match="replace failed"):
        assemble_manuel._atomic_write_json(destination, {"passed": True})

    assert destination.read_bytes() == b"old proof\n"
    assert list(tmp_path.glob(".proof.json.*.tmp")) == []


def test_atomic_json_fsyncs_file_then_parent_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_fsync = os.fsync
    synced_modes: list[int] = []

    def recording_fsync(descriptor: int) -> None:
        synced_modes.append(os.fstat(descriptor).st_mode)
        real_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", recording_fsync)
    destination = tmp_path / "proof.json"

    assemble_manuel._atomic_write_json(destination, {"passed": True})

    assert [stat.S_ISREG(mode) for mode in synced_modes] == [True, False]
    assert [stat.S_ISDIR(mode) for mode in synced_modes] == [False, True]


def test_cli_parser_exposes_record_observed_flag() -> None:
    arguments = assemble_manuel.build_argument_parser().parse_args(
        ["--variant", "professeur", "--record-observed"]
    )

    assert arguments.variant == "professeur"
    assert arguments.record_observed is True
