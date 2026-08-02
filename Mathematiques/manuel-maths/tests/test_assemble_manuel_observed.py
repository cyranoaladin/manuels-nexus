from __future__ import annotations

import json
import re
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
    ) -> None:
        self.calls: list[tuple[list[str], dict[str, Any]]] = []
        self.events: list[str] = []
        self.failing_lualatex_pass = failing_lualatex_pass
        self.failing_stage = failing_stage
        self.source_commit_exists = source_commit_exists
        self.source_commit_is_ancestor = source_commit_is_ancestor
        self.git_timestamp = git_timestamp
        self.recorder_status = recorder_status
        self.receipt_existed_at_recorder = False

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
            self.events.append("lualatex")
            pass_number = sum(event == "lualatex" for event in self.events)
            if pass_number == self.failing_lualatex_pass:
                return self._completed(returncode=3, stdout="compile failed")
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

    @staticmethod
    def _publish_lualatex_fixture(command: list[str]) -> None:
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
        (build / f"{stem}.pdf").write_bytes(b"%PDF-1.7\nfixture\n")
        (build / f"{stem}.log").write_text(
            f"NEXUS_BUILD_RUN:{run_match.group(1)}\n"
            f"Output written on {stem}.pdf (17 pages).\n",
            encoding="utf-8",
        )
        (build / f"{stem}.fls").write_text(
            f"INPUT {master_path}\nOUTPUT {build / f'{stem}.pdf'}\n",
            encoding="utf-8",
        )


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

    def fake_verify(pdf_path: Path, log_path: Path) -> int:
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

    assert len(professor_paths) == 870
    assert all(
        path.startswith("Mathematiques/manuel-maths/") for path in professor_paths
    )
    assert professor_paths == assembly["included_objects"]


def test_observed_build_runs_three_strict_passes_then_publishes_closed_proofs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manual_root, runner, verify_pass_counts, paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
    )
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "999")
    monkeypatch.setenv("TZ", "Africa/Tunis")
    monkeypatch.setenv("LC_ALL", "host-locale")
    monkeypatch.setenv("PYTHONHASHSEED", "random")
    monkeypatch.setenv("OPENROUTER_API_KEY", "must-not-leak")

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
    expected_command = [
        "lualatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-recorder",
        f"-output-directory={paths['build']}",
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


@pytest.mark.parametrize("failing_pass", [1, 2])
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
    paths["build"].mkdir(parents=True, exist_ok=True)
    paths["receipt"].write_text("stale receipt", encoding="utf-8")
    paths["report"].write_text("stale report", encoding="utf-8")
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
    assert neighbour.read_text(encoding="utf-8") == "keep"


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
    assert not any("--receipt" in command for command, _kwargs in runner.calls)


def test_ordinary_mode_builds_and_preflights_without_writing_or_recording_proofs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _manual_root, runner, verify_pass_counts, paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
    )

    assert assemble_manuel.main(
        "professeur",
        record_observed=False,
        runner=runner,
    ) == 0

    assert verify_pass_counts == [3]
    assert not paths["report"].exists()
    assert not paths["receipt"].exists()
    assert not any("--receipt" in command for command, _kwargs in runner.calls)


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
    manual_root, runner, _verify_calls, _paths = _install_orchestration_fixture(
        tmp_path,
        monkeypatch,
        control_payload=payload,
    )
    del manual_root

    assert assemble_manuel.main("professeur", runner=runner) == 1
    assert not any(command[0] == "lualatex" for command, _kwargs in runner.calls)


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


def test_cli_parser_exposes_record_observed_flag() -> None:
    arguments = assemble_manuel.build_argument_parser().parse_args(
        ["--variant", "professeur", "--record-observed"]
    )

    assert arguments.variant == "professeur"
    assert arguments.record_observed is True


def test_verify_pdf_internal_pdffonts_receives_controlled_environment(
    tmp_path: Path,
) -> None:
    pdf_path = tmp_path / "manual.pdf"
    log_path = tmp_path / "manual.log"
    pdf_path.write_bytes(b"%PDF fixture")
    log_path.write_text("Output written on manual.pdf\n", encoding="utf-8")
    calls: list[tuple[list[str], dict[str, Any]]] = []

    def runner(command: list[str], **kwargs: Any) -> SimpleNamespace:
        calls.append((command, kwargs))
        return SimpleNamespace(
            returncode=0,
            stdout=(
                "name type emb sub uni object ID\n"
                "--------------------------------\n"
                "Fixture Type1 yes yes yes 1 0\n"
            ),
            stderr="",
        )

    environment = {
        "SOURCE_DATE_EPOCH": str(SOURCE_DATE_EPOCH),
        "FORCE_SOURCE_DATE": "1",
        "TZ": "UTC",
        "LC_ALL": "C.UTF-8",
        "PYTHONHASHSEED": "0",
    }

    assert assemble_manuel._verify_pdf_with_environment(
        pdf_path,
        log_path,
        runner=runner,
        environment=environment,
    ) == 0
    assert calls == [
        (["pdffonts", str(pdf_path)], {"capture_output": True, "text": True, "check": True, "env": environment})
    ]


def test_verify_pdf_internal_pdffonts_nonzero_status_is_not_ignored(
    tmp_path: Path,
) -> None:
    pdf_path = tmp_path / "manual.pdf"
    log_path = tmp_path / "manual.log"
    pdf_path.write_bytes(b"%PDF fixture")
    log_path.write_text("Output written on manual.pdf\n", encoding="utf-8")

    def failing_runner(command: list[str], **_kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(
            args=command,
            returncode=6,
            stdout=(
                "name type emb sub uni object ID\n"
                "--------------------------------\n"
                "Fixture Type1 yes yes yes 1 0\n"
            ),
            stderr="pdffonts failed",
        )

    with pytest.raises(subprocess.CalledProcessError) as caught:
        assemble_manuel._verify_pdf_with_environment(
            pdf_path,
            log_path,
            runner=failing_runner,
            environment={"SOURCE_DATE_EPOCH": str(SOURCE_DATE_EPOCH)},
        )

    assert caught.value.returncode == 6
