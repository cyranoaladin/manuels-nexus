import copy
import json
import os
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


def fake_runner(outputs=None):
    resolved = VALID_OUTPUTS | (outputs or {})

    def run(command, **_kwargs):
        stdout, stderr = resolved[command[0]]
        return SimpleNamespace(returncode=0, stdout=stdout, stderr=stderr)

    return run


def available(binary):
    return f"/usr/bin/{binary}"


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
    ("binary", "output", "check_id"),
    [
        ("java", ("", 'openjdk version "20.0.2" 2023-07-18\n'), "java"),
        (
            "lualatex",
            ("This is LuaHBTeX, Version 1.17.0 (TeX Live 2023/Debian)\n", ""),
            "latex.engine",
        ),
        ("verapdf", ("veraPDF CLI 1.29.7\n", ""), "verapdf"),
        ("pdfinfo", ("", "pdfinfo version 23.11.0\n"), "pdfinfo"),
        ("gs", ("10.01.2\n", ""), "ghostscript"),
    ],
)
def test_insufficient_or_wrong_version_blocks(binary, output, check_id, toolchain):
    result = check_toolchain(
        toolchain,
        which=available,
        runner=fake_runner({binary: output}),
        python_version=(3, 12, 3),
    )

    assert result.status == "blocked"
    assert result.exit_code == 2
    assert check_by_id(result, check_id)["status"] == "blocked"
    assert "exig" in check_by_id(result, check_id)["reason"]


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


def test_tagged_pdf_gate_is_tied_to_tex_live_2026_and_verapdf(toolchain):
    old_tex = check_toolchain(
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
    current_tex = check_toolchain(
        toolchain,
        which=available,
        runner=fake_runner(),
        python_version=(3, 12, 3),
    )

    assert check_by_id(old_tex, "latex.tagged_pdf")["status"] == "blocked"
    assert "TeX Live 2026" in check_by_id(old_tex, "latex.tagged_pdf")["reason"]
    assert check_by_id(current_tex, "latex.tagged_pdf")["status"] == "certified"
    assert "veraPDF" in check_by_id(current_tex, "latex.tagged_pdf")["reason"]


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
        if command[0] == "java":
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
    first = check_toolchain(
        toolchain,
        which=available,
        runner=fake_runner(),
        python_version=(3, 12, 3),
    ).report
    second = check_toolchain(
        toolchain,
        which=available,
        runner=fake_runner(),
        python_version=(3, 12, 3),
    ).report
    payload = json.dumps(first, ensure_ascii=False, sort_keys=True)

    assert first == second
    assert list(first) == ["schema_version", "status", "checks", "blockers"]
    assert "never-copy-this-value" not in payload
    assert "timestamp" not in payload.lower()
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
    "invalid_yaml",
    [
        "schema_version: 2\n",
        "schema_version: 1\npython: 3.12\n",
        "schema_version: 1\npython: '3.12'\njava: {}\n",
        "[]\n",
        ":\n",
    ],
)
def test_invalid_manifest_returns_2_with_diagnostic(
    tmp_path, invalid_yaml, capsys
):
    manifest = tmp_path / "invalid.yaml"
    report = tmp_path / "report.json"
    manifest.write_text(invalid_yaml, encoding="utf-8")

    code = main(["--manifest", str(manifest), "--output", str(report)])

    assert code == 2
    assert "manifeste invalide" in capsys.readouterr().err.lower()
    assert not report.exists()
