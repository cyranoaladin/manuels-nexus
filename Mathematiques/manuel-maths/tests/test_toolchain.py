import copy
import json
import os
import shlex
import stat
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_toolchain import (  # noqa: E402
    ManifestError,
    check_toolchain,
    load_manifest,
    main,
    validate_manifest,
    write_report_atomic,
)


@pytest.fixture
def toolchain():
    return {
        "schema_version": 1,
        "python": "3.12",
        "java": {"minimum_major": 21},
        "latex": {
            "engine": "lualatex",
            "minimum_texlive": 2026,
            "tagged_pdf": True,
        },
        "verapdf": {
            "version": "1.30.1",
            "profile": "ua1",
            "report_format": "mrr",
        },
        "poppler": {
            "minimum_version": "24.02.0",
            "commands": ["pdfinfo", "pdffonts", "pdftotext", "pdftoppm"],
        },
        "ghostscript": {"minimum_version": "10.02"},
    }


VALID_OUTPUTS = {
    "java": ("", 'openjdk version "21.0.11" 2026-04-21\n'),
    "lualatex": (
        "This is LuaHBTeX, Version 1.22.0 (TeX Live 2026)\n",
        "",
    ),
    "verapdf": ("veraPDF CLI 1.30.1\n", ""),
    "pdfinfo": ("", "pdfinfo version 24.02.0\n"),
    "pdffonts": ("", "pdffonts version 24.02.1\n"),
    "pdftotext": ("", "pdftotext version 25.01.0\n"),
    "pdftoppm": ("", "pdftoppm version 24.02.0\n"),
    "gs": ("10.02.1\n", ""),
}
class ScenarioRunner:
    def __init__(
        self,
        outputs=None,
        *,
        compile_returncode=0,
        create_pdf=True,
        validation_returncode=0,
        binary_aliases=None,
    ):
        self.outputs = VALID_OUTPUTS | (outputs or {})
        self.compile_returncode = compile_returncode
        self.create_pdf = create_pdf
        self.validation_returncode = validation_returncode
        self.binary_aliases = binary_aliases or {}
        self.calls = []
        self.call_records = []
        self.smoke_source = None
        self.smoke_directory = None

    def __call__(self, command, **kwargs):
        self.calls.append(command)
        self.call_records.append((command, kwargs))
        command_name = Path(command[0]).name
        binary = self.binary_aliases.get(command_name, command_name)
        if binary == "lualatex" and "--version" not in command:
            source = Path(command[-1])
            self.smoke_source = source.read_text(encoding="utf-8")
            output_argument = next(
                item for item in command if item.startswith("-output-directory=")
            )
            self.smoke_directory = Path(output_argument.split("=", 1)[1])
            if self.compile_returncode == 0 and self.create_pdf:
                (self.smoke_directory / "tagged-smoke.pdf").write_bytes(b"%PDF-1.7")
            return SimpleNamespace(
                returncode=self.compile_returncode,
                stdout="",
                stderr="",
            )
        if binary == "verapdf" and "--version" not in command:
            return SimpleNamespace(
                returncode=self.validation_returncode,
                stdout="",
                stderr="",
            )
        stdout, stderr = self.outputs[binary]
        return SimpleNamespace(returncode=0, stdout=stdout, stderr=stderr)

    @property
    def smoke_calls(self):
        return [
            command
            for command in self.calls
            if (
                Path(command[0]).name == "lualatex"
                and "--version" not in command
            )
            or (
                Path(command[0]).name == "verapdf"
                and "--version" not in command
            )
        ]

    @property
    def smoke_records(self):
        return [
            record
            for record in self.call_records
            if (
                Path(record[0][0]).name == "lualatex"
                and "--version" not in record[0]
            )
            or (
                Path(record[0][0]).name == "verapdf"
                and "--version" not in record[0]
            )
        ]


def fake_runner(outputs=None, **kwargs):
    return ScenarioRunner(outputs, **kwargs)


def available(binary):
    return f"/opt/nexus-tools/{binary}"


def check_by_id(result, check_id):
    return next(item for item in result.report["checks"] if item["id"] == check_id)


def test_release_manifest_pins_accessibility_validator_and_java():
    toolchain = load_manifest(ROOT / "release" / "toolchain.yaml")

    assert toolchain["schema_version"] == 1
    assert toolchain["python"] == "3.12"
    assert toolchain["java"]["minimum_major"] == 21
    assert toolchain["latex"] == {
        "engine": "lualatex",
        "minimum_texlive": 2026,
        "tagged_pdf": True,
    }
    assert toolchain["verapdf"] == {
        "version": "1.30.1",
        "profile": "ua1",
        "report_format": "mrr",
    }
    assert toolchain["poppler"] == {
        "minimum_version": "24.02.0",
        "commands": ["pdfinfo", "pdffonts", "pdftotext", "pdftoppm"],
    }
    assert toolchain["ghostscript"]["minimum_version"] == "10.02"


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("python",), "3.13"),
        (("java", "minimum_major"), 20),
        (("latex", "minimum_texlive"), 2025),
        (("verapdf", "version"), "1.30.0"),
        (("poppler", "minimum_version"), "23.11.0"),
        (("ghostscript", "minimum_version"), "10.01"),
    ],
)
def test_manifest_rejects_release_contract_drift(path, value, toolchain):
    changed = copy.deepcopy(toolchain)
    target = changed
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value

    with pytest.raises(ManifestError, match="doit valoir"):
        validate_manifest(changed)


@pytest.mark.parametrize(
    "missing",
    [
        "java",
        "lualatex",
        "verapdf",
        "pdfinfo",
        "pdffonts",
        "pdftotext",
        "pdftoppm",
        "gs",
    ],
)
def test_each_missing_blocking_binary_is_reported(missing, toolchain):
    result = check_toolchain(
        toolchain,
        which=lambda binary: None if binary == missing else available(binary),
        runner=fake_runner(),
        python_version=(3, 12, 3),
    )

    assert result.status == "blocked"
    assert result.exit_code == 2
    expected_id = {
        "lualatex": "latex.engine",
        "verapdf": "verapdf",
        "gs": "ghostscript",
    }.get(missing, missing)
    assert check_by_id(result, expected_id)["reason"] == f"binaire absent: {missing}"
    assert any(item["tool"] == expected_id for item in result.report["blockers"])


@pytest.mark.parametrize(
    ("binary", "output", "check_id", "detected", "reason"),
    [
        (
            "java",
            ("", 'openjdk version "20.0.2" 2023-07-18\n'),
            "java",
            "20.0.2",
            "Java >= 21 exigé; version détectée: 20.0.2",
        ),
        (
            "lualatex",
            ("This is LuaHBTeX, Version 1.17.0 (TeX Live 2023/Debian)\n", ""),
            "latex.engine",
            "TeX Live 2023",
            "TeX Live >= 2026 exigé; version détectée: 2023",
        ),
        (
            "verapdf",
            ("veraPDF CLI 1.29.7\n", ""),
            "verapdf",
            "1.29.7",
            "veraPDF 1.30.1 exigé; version détectée: 1.29.7",
        ),
        (
            "pdfinfo",
            ("", "pdfinfo version 23.11.0\n"),
            "pdfinfo",
            "23.11.0",
            "pdfinfo >= 24.02.0 exigé; version détectée: 23.11.0",
        ),
        (
            "pdffonts",
            ("", "pdffonts version 23.11.0\n"),
            "pdffonts",
            "23.11.0",
            "pdffonts >= 24.02.0 exigé; version détectée: 23.11.0",
        ),
        (
            "pdftotext",
            ("", "pdftotext version 23.11.0\n"),
            "pdftotext",
            "23.11.0",
            "pdftotext >= 24.02.0 exigé; version détectée: 23.11.0",
        ),
        (
            "pdftoppm",
            ("", "pdftoppm version 23.11.0\n"),
            "pdftoppm",
            "23.11.0",
            "pdftoppm >= 24.02.0 exigé; version détectée: 23.11.0",
        ),
        (
            "gs",
            ("10.01.2\n", ""),
            "ghostscript",
            "10.01.2",
            "Ghostscript >= 10.02 exigé; version détectée: 10.01.2",
        ),
    ],
)
def test_insufficient_version_cites_detected_value(
    binary, output, check_id, detected, reason, toolchain
):
    result = check_toolchain(
        toolchain,
        which=available,
        runner=fake_runner({binary: output}),
        python_version=(3, 12, 3),
    )

    assert result.status == "blocked"
    assert result.exit_code == 2
    assert check_by_id(result, check_id)["status"] == "blocked"
    assert check_by_id(result, check_id)["detected"] == detected
    assert check_by_id(result, check_id)["reason"] == reason


@pytest.mark.parametrize(
    ("binary", "check_id", "reason"),
    [
        ("java", "java", "Java >= 21 exigé; version illisible"),
        ("verapdf", "verapdf", "veraPDF 1.30.1 exigé; version illisible"),
        ("pdfinfo", "pdfinfo", "pdfinfo >= 24.02.0 exigé; version illisible"),
        ("pdffonts", "pdffonts", "pdffonts >= 24.02.0 exigé; version illisible"),
        (
            "pdftotext",
            "pdftotext",
            "pdftotext >= 24.02.0 exigé; version illisible",
        ),
        ("pdftoppm", "pdftoppm", "pdftoppm >= 24.02.0 exigé; version illisible"),
        (
            "gs",
            "ghostscript",
            "Ghostscript >= 10.02 exigé; version illisible",
        ),
    ],
)
def test_unparseable_version_is_distinct_from_insufficient_version(
    binary, check_id, reason, toolchain
):
    result = check_toolchain(
        toolchain,
        which=available,
        runner=fake_runner({binary: ("not-a-version\n", "")}),
        python_version=(3, 12, 3),
    )

    assert result.status == "blocked"
    assert check_by_id(result, check_id)["detected"] is None
    assert check_by_id(result, check_id)["reason"] == reason


@pytest.mark.parametrize("python_version", [(3, 11, 9), (3, 13, 0)])
def test_python_major_minor_must_match_pin(python_version, toolchain):
    result = check_toolchain(
        toolchain,
        which=available,
        runner=fake_runner(),
        python_version=python_version,
    )

    assert result.status == "blocked"
    assert result.exit_code == 2
    assert check_by_id(result, "python")["status"] == "blocked"


def test_versions_are_parsed_from_realistic_stdout_and_stderr(toolchain):
    result = check_toolchain(
        toolchain,
        which=available,
        runner=fake_runner(),
        python_version=(3, 12, 3),
    )

    assert result.status == "certified"
    assert result.exit_code == 0
    assert check_by_id(result, "java")["detected"] == "21.0.11"
    assert check_by_id(result, "latex.engine")["detected"] == "TeX Live 2026"
    assert check_by_id(result, "pdfinfo")["detected"] == "24.02.0"
    assert check_by_id(result, "ghostscript")["detected"] == "10.02.1"


@pytest.mark.parametrize("prefix", ["veraPDF ", "veraPDF CLI "])
def test_official_verapdf_version_forms_are_accepted(prefix, toolchain):
    result = check_toolchain(
        toolchain,
        which=available,
        runner=fake_runner({"verapdf": (f"{prefix}1.30.1\n", "")}),
        python_version=(3, 12, 3),
    )

    assert check_by_id(result, "verapdf")["status"] == "certified"


@pytest.mark.parametrize(
    "token",
    ["1.30.1-SNAPSHOT", "1.30.1-RC1", "1.30.1.1", "1.30.1+local"],
)
def test_verapdf_rejects_any_non_exact_version_token(token, toolchain):
    runner = fake_runner({"verapdf": (f"veraPDF CLI {token}\n", "")})
    result = check_toolchain(
        toolchain,
        which=available,
        runner=runner,
        python_version=(3, 12, 3),
    )

    verapdf = check_by_id(result, "verapdf")
    assert verapdf["status"] == "blocked"
    assert verapdf["detected"] == token
    assert verapdf["reason"] == (
        f"veraPDF 1.30.1 exigé; version détectée: {token}"
    )
    assert check_by_id(result, "latex.tagged_pdf")["reason"] == (
        "smoke Tagged PDF non exécuté: veraPDF 1.30.1 exigé, "
        f"version détectée: {token}"
    )
    assert runner.smoke_calls == []


def test_tagged_pdf_is_blocked_when_verapdf_is_absent_despite_tex_live_2026(
    toolchain,
):
    runner = fake_runner()
    result = check_toolchain(
        toolchain,
        which=lambda binary: None if binary == "verapdf" else available(binary),
        runner=runner,
        python_version=(3, 12, 3),
    )

    tagged = check_by_id(result, "latex.tagged_pdf")
    assert tagged["status"] == "blocked"
    assert tagged["detected"] is None
    assert tagged["reason"] == "smoke Tagged PDF non exécuté: binaire veraPDF absent"
    assert runner.smoke_calls == []


def test_tagged_pdf_is_blocked_when_verapdf_version_is_wrong(toolchain):
    runner = fake_runner({"verapdf": ("veraPDF CLI 1.29.7\n", "")})
    result = check_toolchain(
        toolchain,
        which=available,
        runner=runner,
        python_version=(3, 12, 3),
    )

    tagged = check_by_id(result, "latex.tagged_pdf")
    assert tagged["status"] == "blocked"
    assert tagged["reason"] == (
        "smoke Tagged PDF non exécuté: veraPDF 1.30.1 exigé, "
        "version détectée: 1.29.7"
    )
    assert runner.smoke_calls == []


@pytest.mark.parametrize(
    ("runner_options", "reason"),
    [
        (
            {"compile_returncode": 1},
            "smoke Tagged PDF: compilation LuaLaTeX échouée (code 1)",
        ),
        (
            {"create_pdf": False},
            "smoke Tagged PDF: PDF absent après compilation LuaLaTeX",
        ),
        (
            {"validation_returncode": 1},
            "smoke Tagged PDF: veraPDF signale un PDF/UA-1 non conforme (code 1)",
        ),
        (
            {"validation_returncode": 2},
            (
                "smoke Tagged PDF: veraPDF rejette le profil ua1 "
                "ou le format mrr (code 2)"
            ),
        ),
    ],
)
def test_tagged_pdf_smoke_failures_are_blocking(runner_options, reason, toolchain):
    runner = fake_runner(**runner_options)
    result = check_toolchain(
        toolchain,
        which=available,
        runner=runner,
        python_version=(3, 12, 3),
    )

    tagged = check_by_id(result, "latex.tagged_pdf")
    assert tagged["status"] == "blocked"
    assert tagged["reason"] == reason
    assert result.status == "blocked"
    assert result.exit_code == 2


def test_tagged_pdf_success_uses_exact_commands_and_official_metadata(toolchain):
    runner = fake_runner()
    result = check_toolchain(
        toolchain,
        which=available,
        runner=runner,
        python_version=(3, 12, 3),
    )

    tagged = check_by_id(result, "latex.tagged_pdf")
    assert tagged == {
        "id": "latex.tagged_pdf",
        "required": (
            "smoke LuaLaTeX TeX Live >=2026 + veraPDF 1.30.1 "
            "-f ua1 --format mrr"
        ),
        "detected": "smoke PDF/UA-1 conforme",
        "status": "certified",
        "reason": "compilation Tagged PDF et validation veraPDF PDF/UA-1 réussies",
    }
    assert len(runner.smoke_calls) == 2
    compile_command, validate_command = runner.smoke_calls
    assert compile_command[:3] == [
        "/opt/nexus-tools/lualatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
    ]
    assert compile_command[3].startswith("-output-directory=")
    smoke_directory = Path(compile_command[3].split("=", 1)[1])
    assert Path(compile_command[4]) == smoke_directory / "tagged-smoke.tex"
    assert validate_command == [
        "/opt/nexus-tools/verapdf",
        "-f",
        "ua1",
        "--format",
        "mrr",
        str(smoke_directory / "tagged-smoke.pdf"),
    ]
    assert runner.smoke_source.startswith("\\DocumentMetadata{")
    assert runner.smoke_source.index("\\DocumentMetadata{") < runner.smoke_source.index(
        "\\documentclass{article}"
    )
    assert "pdfversion=1.7" in runner.smoke_source
    assert "pdfstandard=ua-1" in runner.smoke_source
    assert "tagging=on" in runner.smoke_source
    assert "pdftitle=" in runner.smoke_source
    assert "pdfauthor=" in runner.smoke_source
    compile_record, validate_record = runner.smoke_records
    assert compile_record[1]["cwd"] == smoke_directory
    assert validate_record[1]["cwd"] == smoke_directory
    assert not smoke_directory.exists()


def test_each_binary_is_resolved_once_and_exact_identity_is_executed(toolchain):
    resolutions = {}

    def relative_locator(binary):
        resolutions[binary] = resolutions.get(binary, 0) + 1
        return f"review-toolchain/bin/{binary}"

    runner = fake_runner()
    result = check_toolchain(
        toolchain,
        which=relative_locator,
        runner=runner,
        python_version=(3, 12, 3),
    )

    binaries = [
        "java",
        "lualatex",
        "verapdf",
        "pdfinfo",
        "pdffonts",
        "pdftotext",
        "pdftoppm",
        "gs",
    ]
    assert result.status == "certified"
    assert resolutions == {binary: 1 for binary in binaries}
    expected_paths = {
        binary: str((Path.cwd() / "review-toolchain" / "bin" / binary).resolve())
        for binary in binaries
    }
    for command in runner.calls:
        binary = Path(command[0]).name
        assert command[0] == expected_paths[binary]


def test_symlink_launcher_identity_is_preserved_for_version_and_smoke(
    tmp_path, toolchain
):
    target = tmp_path / "luahbtex"
    launcher = tmp_path / "lualatex"
    target.write_text("#!/bin/sh\n", encoding="utf-8")
    launcher.symlink_to(target.name)

    def locator(binary):
        if binary == "lualatex":
            return str(launcher)
        return available(binary)

    runner = fake_runner(binary_aliases={"luahbtex": "lualatex"})
    result = check_toolchain(
        toolchain,
        which=locator,
        runner=runner,
        python_version=(3, 12, 3),
    )

    assert result.status == "certified"
    latex_calls = [
        command
        for command in runner.calls
        if Path(command[0]).parent == tmp_path
    ]
    assert len(latex_calls) == 2
    assert all(command[0] == str(launcher.absolute()) for command in latex_calls)
    assert all(command[0] != str(target.absolute()) for command in latex_calls)


def test_smoke_environment_is_allowlisted_and_redirected_under_temp(
    monkeypatch, toolchain
):
    hostile_variables = [
        "HOME",
        "TMPDIR",
        "XDG_CACHE_HOME",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
        "TEXFORMATS",
        "TEXMFOUTPUT",
        "TEXMFDBS",
        "WEB2C",
        "TEXINPUTS",
        "TEXMFCNF",
        "LUAINPUTS",
        "TEXMFHOME",
        "TEXMFVAR",
        "TEXMFCONFIG",
        "TEXMFCACHE",
        "VARTEXFONTS",
        "JAVACMD",
        "JAVA_OPTS",
        "JAVA_TOOL_OPTIONS",
        "_JAVA_OPTIONS",
        "NEXUS_HOST_SECRET",
    ]
    for variable in hostile_variables:
        monkeypatch.setenv(variable, f"hostile-{variable}")
    monkeypatch.setenv(
        "PATH",
        "/controlled/bin:/opt/nexus-tools:/controlled/bin",
    )
    monkeypatch.setenv("JAVA_HOME", "/hostile/java17")
    monkeypatch.setenv("LANG", "hostile-locale")
    scenario = fake_runner()
    directory_states = []
    isolated_directories = []

    def observing_runner(command, **kwargs):
        if "env" in kwargs:
            environment = kwargs["env"]
            directory_keys = [
                "HOME",
                "TMPDIR",
                "XDG_CACHE_HOME",
                "XDG_CONFIG_HOME",
                "XDG_DATA_HOME",
                "TEXMFHOME",
                "TEXMFVAR",
                "TEXMFCONFIG",
                "TEXMFCACHE",
                "VARTEXFONTS",
            ]
            options = shlex.split(environment["JAVA_OPTS"])
            java_tmp = Path(options[0].split("=", 1)[1])
            java_home = Path(options[1].split("=", 1)[1])
            directories = [
                *(Path(environment[key]) for key in directory_keys),
                java_tmp,
                java_home,
            ]
            directory_states.append(
                [directory.is_dir() for directory in directories]
            )
            isolated_directories.extend(directories)
        return scenario(command, **kwargs)

    result = check_toolchain(
        toolchain,
        which=available,
        runner=observing_runner,
        python_version=(3, 12, 3),
    )

    assert result.status == "certified"
    assert len(scenario.smoke_records) == 2
    compile_environment = scenario.smoke_records[0][1]["env"]
    validate_environment = scenario.smoke_records[1][1]["env"]
    assert compile_environment == validate_environment
    redirected_keys = {
        "HOME",
        "TMPDIR",
        "XDG_CACHE_HOME",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
        "TEXMFHOME",
        "TEXMFVAR",
        "TEXMFCONFIG",
        "TEXMFCACHE",
        "VARTEXFONTS",
    }
    assert set(compile_environment) == {
        "PATH",
        "JAVACMD",
        "JAVA_OPTS",
        "LANG",
        "LC_ALL",
        "TZ",
        *redirected_keys,
    }
    assert compile_environment["JAVACMD"] == "/opt/nexus-tools/java"
    assert compile_environment["PATH"] == "/opt/nexus-tools:/controlled/bin"
    assert "JAVA_HOME" not in compile_environment
    assert compile_environment["LANG"] == "C"
    assert compile_environment["LC_ALL"] == "C"
    assert compile_environment["TZ"] == "UTC"
    smoke_directory = scenario.smoke_directory
    for key in redirected_keys:
        redirected = Path(compile_environment[key])
        assert redirected.is_relative_to(smoke_directory)
        assert not redirected.exists()
    java_options = shlex.split(compile_environment["JAVA_OPTS"])
    assert len(java_options) == 2
    assert java_options[0].startswith("-Djava.io.tmpdir=")
    assert java_options[1].startswith("-Duser.home=")
    assert all(
        Path(option.split("=", 1)[1]).is_relative_to(smoke_directory)
        for option in java_options
    )
    assert all(all(state) for state in directory_states)
    assert all(not directory.exists() for directory in isolated_directories)
    assert not smoke_directory.exists()
    verapdf_version_records = [
        record
        for record in scenario.call_records
        if Path(record[0][0]).name == "verapdf" and "--version" in record[0]
    ]
    assert len(verapdf_version_records) == 1
    version_environment = verapdf_version_records[0][1]["env"]
    assert version_environment["JAVACMD"] == "/opt/nexus-tools/java"
    assert version_environment["PATH"].startswith("/opt/nexus-tools:")
    assert "JAVA_HOME" not in version_environment
    assert "hostile" not in json.dumps(version_environment)
    java_version_records = [
        record
        for record in scenario.call_records
        if Path(record[0][0]).name == "java" and "-version" in record[0]
    ]
    assert len(java_version_records) == 1
    java_version_environment = java_version_records[0][1]["env"]
    assert java_version_environment["JAVACMD"] == "/opt/nexus-tools/java"
    assert "JAVA_HOME" not in java_version_environment
    assert "hostile" not in json.dumps(java_version_environment)
    serialized_report = json.dumps(result.report, ensure_ascii=False)
    assert str(smoke_directory) not in serialized_report
    assert not any(
        f"hostile-{variable}" in serialized_report
        for variable in hostile_variables
    )


def test_verapdf_wrapper_consumes_certified_java_and_trusted_options(
    tmp_path, monkeypatch, toolchain
):
    java21 = tmp_path / "java21"
    wrapper = tmp_path / "verapdf-wrapper"
    java21.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    wrapper.write_text(
        """#!/bin/sh
if [ -n "${JAVACMD:-}" ]; then
  selected="$JAVACMD"
elif [ -n "${JAVA_HOME:-}" ]; then
  selected="$JAVA_HOME/bin/java"
else
  selected="$(command -v java)"
fi
printf 'SELECTED_JAVA=%s\\n' "$selected"
printf 'USED_JAVA_OPTS=%s\\n' "${JAVA_OPTS:-}"
case " $* " in
  *" --version "*) printf 'veraPDF CLI 1.30.1\\n' ;;
esac
exit 0
""",
        encoding="utf-8",
    )
    java21.chmod(0o755)
    wrapper.chmod(0o755)
    monkeypatch.setenv("JAVACMD", "/hostile/java17")
    monkeypatch.setenv("JAVA_HOME", "/hostile/jdk17")
    monkeypatch.setenv("JAVA_OPTS", "-Duser.home=/hostile/home")
    monkeypatch.setenv("JAVA_TOOL_OPTIONS", "-javaagent:/hostile/agent.jar")
    consumed_java = []
    consumed_options = []
    scenario = fake_runner(binary_aliases={"java21": "java"})

    def locator(binary):
        if binary == "java":
            return str(java21)
        if binary == "verapdf":
            return str(wrapper)
        return available(binary)

    def runner(command, **kwargs):
        if Path(command[0]) == wrapper:
            process = subprocess.run(command, **kwargs)
            for line in process.stdout.splitlines():
                if line.startswith("SELECTED_JAVA="):
                    consumed_java.append(line.split("=", 1)[1])
                if line.startswith("USED_JAVA_OPTS="):
                    consumed_options.append(line.split("=", 1)[1])
            return process
        return scenario(command, **kwargs)

    result = check_toolchain(
        toolchain,
        which=locator,
        runner=runner,
        python_version=(3, 12, 3),
    )

    assert result.status == "certified"
    assert consumed_java == [str(java21.absolute()), str(java21.absolute())]
    assert len(consumed_options) == 2
    for options in consumed_options:
        parsed = shlex.split(options)
        assert len(parsed) == 2
        assert parsed[0].startswith("-Djava.io.tmpdir=")
        assert parsed[1].startswith("-Duser.home=")
        assert "/hostile/" not in options


def test_tagged_smoke_never_runs_when_java_is_insufficient(toolchain):
    runner = fake_runner(
        {"java": ("", 'openjdk version "20.0.2" 2023-07-18\n')}
    )
    result = check_toolchain(
        toolchain,
        which=available,
        runner=runner,
        python_version=(3, 12, 3),
    )

    assert check_by_id(result, "java")["status"] == "blocked"
    assert check_by_id(result, "verapdf")["status"] == "certified"
    assert check_by_id(result, "latex.tagged_pdf")["reason"] == (
        "smoke Tagged PDF non exécuté: Java >= 21 requis, "
        "version détectée: 20.0.2"
    )
    assert runner.smoke_calls == []


def test_verapdf_version_and_smoke_are_skipped_when_java_is_absent(toolchain):
    runner = fake_runner()
    result = check_toolchain(
        toolchain,
        which=lambda binary: None if binary == "java" else available(binary),
        runner=runner,
        python_version=(3, 12, 3),
    )

    assert check_by_id(result, "java")["reason"] == "binaire absent: java"
    assert check_by_id(result, "verapdf")["reason"] == (
        "contrôle veraPDF impossible: binaire Java absent"
    )
    assert "Java absent" in check_by_id(result, "latex.tagged_pdf")["reason"]
    assert all(Path(call[0]).name != "verapdf" for call in runner.calls)
    assert runner.smoke_calls == []


@pytest.mark.parametrize(
    "outputs",
    [
        {
            "lualatex": (
                "This is LuaHBTeX, Version 1.17.0 (TeX Live 2023/Debian)\n",
                "",
            )
        },
        {"verapdf": ("veraPDF CLI 1.29.7\n", "")},
    ],
)
def test_tagged_pdf_smoke_is_not_run_when_version_prerequisite_fails(
    outputs, toolchain
):
    runner = fake_runner(outputs)
    result = check_toolchain(
        toolchain,
        which=available,
        runner=runner,
        python_version=(3, 12, 3),
    )

    assert check_by_id(result, "latex.tagged_pdf")["status"] == "blocked"
    assert runner.smoke_calls == []


def test_insufficient_version_reason_names_the_detected_version(toolchain):
    result = check_toolchain(
        toolchain,
        which=available,
        runner=fake_runner(
            {
                "lualatex": (
                    "This is LuaHBTeX, Version 1.17.0 (TeX Live 2023/Debian)\n",
                    "",
                )
            }
        ),
        python_version=(3, 12, 3),
    )

    reason = check_by_id(result, "latex.engine")["reason"]
    assert reason == "TeX Live >= 2026 exigé; version détectée: 2023"


def test_nonzero_command_and_unparseable_version_are_blocking(toolchain):
    def runner(command, **_kwargs):
        if Path(command[0]).name == "java":
            return SimpleNamespace(returncode=1, stdout="", stderr="java failure")
        return fake_runner()(command)

    result = check_toolchain(
        toolchain,
        which=available,
        runner=runner,
        python_version=(3, 12, 3),
    )

    assert result.status == "blocked"
    assert result.exit_code == 2
    assert check_by_id(result, "java")["status"] == "blocked"
    assert "code 1" in check_by_id(result, "java")["reason"]


def test_aggregate_status_is_never_certified_when_one_check_fails(toolchain):
    result = check_toolchain(
        toolchain,
        which=lambda binary: None if binary == "verapdf" else available(binary),
        runner=fake_runner(),
        python_version=(3, 12, 3),
    )

    assert any(check["status"] == "blocked" for check in result.report["checks"])
    assert result.report["status"] == "blocked"
    assert result.status == "blocked"


def test_report_is_deterministic_structured_and_contains_no_environment_secret(
    monkeypatch, toolchain
):
    monkeypatch.setenv("TOOLCHAIN_TEST_SECRET", "never-copy-this-value")
    first_runner = fake_runner()
    first = check_toolchain(
        toolchain,
        which=available,
        runner=first_runner,
        python_version=(3, 12, 3),
    ).report
    second_runner = fake_runner()
    second = check_toolchain(
        toolchain,
        which=available,
        runner=second_runner,
        python_version=(3, 12, 3),
    ).report
    payload = json.dumps(first, ensure_ascii=False, sort_keys=True)

    assert first == second
    assert list(first) == ["schema_version", "status", "checks", "blockers"]
    assert "never-copy-this-value" not in payload
    assert "timestamp" not in payload.lower()
    assert str(first_runner.smoke_directory) not in payload
    assert str(second_runner.smoke_directory) not in payload
    assert all(set(check) == {"id", "required", "detected", "status", "reason"}
               for check in first["checks"])


def test_write_report_is_atomic(tmp_path, monkeypatch):
    destination = tmp_path / "nested" / "toolchain.json"
    observed = {}
    real_replace = os.replace

    def spy_replace(source, target):
        observed["source"] = Path(source)
        observed["target"] = Path(target)
        assert Path(source).exists()
        assert Path(source).parent == destination.parent
        real_replace(source, target)

    monkeypatch.setattr(os, "replace", spy_replace)
    write_report_atomic(destination, {"schema_version": 1, "status": "blocked"})

    assert destination.exists()
    assert observed["target"] == destination
    assert not observed["source"].exists()
    assert json.loads(destination.read_text(encoding="utf-8"))["status"] == "blocked"
    assert stat.S_IMODE(destination.stat().st_mode) == 0o644


def test_cli_writes_blocked_report_and_returns_2(tmp_path, toolchain, monkeypatch):
    manifest = tmp_path / "toolchain.yaml"
    report = tmp_path / "reports" / "toolchain.json"
    manifest.write_text(
        (ROOT / "release" / "toolchain.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    monkeypatch.setattr("check_toolchain.shutil.which", lambda _binary: None)

    code = main(["--manifest", str(manifest), "--output", str(report)])

    assert code == 2
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["status"] == "blocked"
    assert payload["blockers"]


@pytest.mark.parametrize(
    ("invalid_yaml", "expected_reason"),
    [
        (
            ":\n",
            (
                "manifeste YAML invalide; corriger la syntaxe du "
                "manifeste d'outillage"
            ),
        ),
        (
            "schema_version: 2\n",
            (
                "contrat d'outillage invalide; corriger les clés "
                "et valeurs épinglées"
            ),
        ),
        (
            None,
            (
                "manifeste inaccessible; vérifier sa présence "
                "et ses permissions"
            ),
        ),
    ],
)
def test_invalid_manifest_replaces_stale_certified_report_deterministically(
    tmp_path, invalid_yaml, expected_reason, capsys, monkeypatch
):
    manifest = tmp_path / "invalid.yaml"
    report = tmp_path / "report.json"
    if invalid_yaml is not None:
        manifest.write_text(invalid_yaml, encoding="utf-8")
    report.write_text('{"status":"certified"}\n', encoding="utf-8")
    monkeypatch.setenv("MANIFEST_REPORT_SECRET", "do-not-copy")

    code = main(["--manifest", str(manifest), "--output", str(report)])
    first_bytes = report.read_bytes()
    payload = json.loads(first_bytes)

    assert code == 2
    assert "manifeste invalide" in capsys.readouterr().err.lower()
    assert payload == {
        "schema_version": 1,
        "status": "blocked",
        "checks": [
            {
                "id": "manifest",
                "required": "manifeste d'outillage valide (schema_version 1)",
                "detected": None,
                "status": "blocked",
                "reason": expected_reason,
            }
        ],
        "blockers": [{"tool": "manifest", "reason": expected_reason}],
    }
    serialized = first_bytes.decode("utf-8")
    assert str(tmp_path) not in serialized
    assert "do-not-copy" not in serialized
    assert "timestamp" not in serialized.lower()
    assert stat.S_IMODE(report.stat().st_mode) == 0o644

    second_code = main(["--manifest", str(manifest), "--output", str(report)])

    assert second_code == 2
    assert report.read_bytes() == first_bytes


def test_non_string_yaml_key_replaces_stale_report_without_traceback(
    tmp_path, capsys, monkeypatch
):
    manifest = tmp_path / "numeric-key.yaml"
    report = tmp_path / "report.json"
    manifest.write_text(
        (ROOT / "release" / "toolchain.yaml").read_text(encoding="utf-8")
        + "\n1: unexpected\n",
        encoding="utf-8",
    )
    report.write_text('{"status":"certified"}\n', encoding="utf-8")
    monkeypatch.setenv("NON_STRING_KEY_SECRET", "never-copy")

    code = main(["--manifest", str(manifest), "--output", str(report)])
    captured = capsys.readouterr()
    payload = json.loads(report.read_text(encoding="utf-8"))

    assert code == 2
    assert "manifeste invalide" in captured.err.lower()
    assert "traceback" not in captured.err.lower()
    assert payload["status"] == "blocked"
    assert payload["checks"][0]["id"] == "manifest"
    assert payload["checks"][0]["reason"] == (
        "contrat d'outillage invalide; corriger les clés et valeurs épinglées"
    )
    serialized = json.dumps(payload, ensure_ascii=False)
    assert str(tmp_path) not in serialized
    assert "never-copy" not in serialized
    assert stat.S_IMODE(report.stat().st_mode) == 0o644
