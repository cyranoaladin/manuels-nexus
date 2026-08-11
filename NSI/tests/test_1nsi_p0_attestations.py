"""Contrat executable des attestations atomiques de correction P0 1NSI."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = (
    ROOT / "audit" / "schemas" / "v1" / "1nsi-p0-correction-attestation.schema.json"
)
SUMMARY_FILENAME = "2026-08-10-dix-p0-summary.md"
EXPECTED_P0_IDS = {
    "1NSI-REV-LANG-COURS-C4-MAXIMUM-ZERO",
    "1NSI-REV-LANGAGE-RE-C4-CORRIGE-LISTE-VIDE",
    "1NSI-REV-LANGAGE-RE-C4-LISTE-VIDE",
    "1NSI-REV-PM-COURS-C2-JALONS-VIDES",
    "1NSI-REV-PM-COURS-C3-POIDS-NEGATIFS",
    "1NSI-REV-TAB-COURS-C4-COLLISION-COLONNES",
    "1NSI-REV-WEB-SERVER-VISIBILITY-COURSE",
    "1NSI-REV-TC-COURS-C5-COPIE-PROFONDE-INCOMPLETE",
    "1NSI-REV-TC-CO-053-COPIE-PROFONDE-INCOMPLETE",
    "1NSI-REV-TC-CO-054-COPIE-PROFONDE-INCOMPLETE",
    "1NSI-REV-ADGK-C2-TERMINAISON-PIECE-NULLE",
    "1NSI-REV-ADGK-C2-RENDU-PARTIEL",
    "1NSI-REV-ADGK-C3-DOMAINE-K",
    "1NSI-REV-TAB-COURS-C4-COLLISION-OPTIMISATION",
}
SECRET_PATTERNS = (
    re.compile(r"sk-or-v1-", re.IGNORECASE),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"OPENROUTER_API_KEY\s*[:=]\s*[^\s#]+", re.IGNORECASE),
    re.compile(r"Authorization\s*:\s*Bearer\s+\S+", re.IGNORECASE),
    re.compile(r"\bghp_"),
    re.compile(r"\bgithub_pat_"),
)
CREDENTIAL_ASSIGNMENT = re.compile(
    r"^\s*(?:export\s+)?(?P<name>x-api-key|(?:[A-Z][A-Z0-9_]*_)?(?:API_KEY|TOKEN|SECRET|PASSWORD))"
    r"\s*(?:=|:)\s*(?P<value>\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'|[^#\n]+?)"
    r"\s*(?:#.*)?$",
    re.IGNORECASE | re.MULTILINE,
)
SAFE_CREDENTIAL_SENTINELS = {"not_applicable", "redacted", "none", "null"}
RFC3339_DATETIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
FORMAT_CHECKER = FormatChecker()


@FORMAT_CHECKER.checks("date-time")
def _is_rfc3339_datetime(value: object) -> bool:
    if not isinstance(value, str) or not RFC3339_DATETIME.fullmatch(value):
        return False
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None
    except ValueError:
        return False


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _run_git(root: Path, *args: str, text: bool = True) -> str | bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=text,
    )
    return result.stdout


def _is_tracked(root: Path, path: Path) -> bool:
    relative = path.relative_to(root).as_posix()
    return (
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", relative],
            cwd=root,
            capture_output=True,
            text=True,
        ).returncode
        == 0
    )


def _receipt_paths(root: Path) -> list[Path]:
    return sorted((root / "audit" / "reviews" / "1nsi" / "p0").glob("*.yaml"))


def _valid_receipt(source_path: str = "source.txt", source: bytes = b"source\n") -> dict:
    digest = _sha256(source)
    stdout = "sortie de test\n"
    stderr = "erreur de test\n"
    return {
        "artifact_type": "1nsi_p0_correction_attestation",
        "schema_version": 1,
        "manual": "1NSI",
        "p0_id": "1NSI-REV-UNIT-TEST",
        "source_commit_sha": "a" * 40,
        "source_files": [{"path": source_path, "sha256": digest}],
        "reviewer_id": "reviewer-unit",
        "reviewer_model": "unit-model",
        "review_run_id": "unit-run",
        "session_id": "unit-session",
        "generation_id": "unit-generation",
        "cache_status": "not_applicable",
        "commands": [
            {
                "command": "pytest -q tests/test_unit.py",
                "cwd": "NSI",
                "exit_code": 0,
                "stdout": stdout,
                "stderr": stderr,
                "stdout_sha256": _sha256(stdout.encode("utf-8")),
                "stderr_sha256": _sha256(stderr.encode("utf-8")),
                "result_summary": "Le test cible est vert.",
            }
        ],
        "verdict": "approved",
        "reviewed_at": "2026-08-10T12:00:00+00:00",
    }


def _load_schema() -> dict:
    assert SCHEMA_PATH.is_file(), "le schema d'attestation P0 doit etre cree"
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _assert_no_secret(raw: str, path: Path) -> None:
    def replace_sentinel(match: re.Match[str]) -> str:
        value = match["value"].strip()
        if value[:1] == value[-1:] and value[:1] in {"\"", "'"}:
            value = value[1:-1]
        value = value.strip().lower()
        assert value in SAFE_CREDENTIAL_SENTINELS, (
            f"secret ou credential interdit dans {path}"
        )
        return match["name"]

    redacted = CREDENTIAL_ASSIGNMENT.sub(replace_sentinel, raw)
    for pattern in SECRET_PATTERNS:
        assert not pattern.search(redacted), f"secret ou credential interdit dans {path}"


def _assert_command_output_hashes(commands: list[dict]) -> None:
    for command in commands:
        assert _sha256(command["stdout"].encode("utf-8")) == command["stdout_sha256"], (
            "le digest stdout doit correspondre aux octets UTF-8 exacts"
        )
        assert _sha256(command["stderr"].encode("utf-8")) == command["stderr_sha256"], (
            "le digest stderr doit correspondre aux octets UTF-8 exacts"
        )


def _assert_source_hashes(root: Path, receipt: dict) -> None:
    source_commit = receipt["source_commit_sha"]
    for source_file in receipt["source_files"]:
        source = _run_git(
            root,
            "show",
            f"{source_commit}:{source_file['path']}",
            text=False,
        )
        assert isinstance(source, bytes)
        assert _sha256(source) == source_file["sha256"]


def _assert_post_commit_parent(root: Path, path: Path, receipt: dict) -> None:
    if not _is_tracked(root, path):
        return
    relative = path.relative_to(root).as_posix()
    additions = _run_git(root, "log", "--format=%H", "--diff-filter=A", "--", relative)
    assert isinstance(additions, str)
    commits = [commit for commit in additions.splitlines() if commit]
    assert len(commits) == 1, f"un seul commit d'ajout attendu pour {relative}"
    parent = _run_git(root, "rev-parse", f"{commits[0]}^")
    assert isinstance(parent, str)
    assert parent.strip() == receipt["source_commit_sha"], (
        f"le parent du commit d'ajout de {relative} doit etre la source revue"
    )


def _validate_receipts(root: Path = ROOT) -> list[dict]:
    schema = _load_schema()
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FORMAT_CHECKER)
    receipts = []
    for path in _receipt_paths(root):
        raw = path.read_text(encoding="utf-8")
        _assert_no_secret(raw, path)
        receipt = yaml.safe_load(raw)
        validator.validate(receipt)
        _assert_command_output_hashes(receipt["commands"])
        _assert_source_hashes(root, receipt)
        _assert_post_commit_parent(root, path, receipt)
        receipts.append(receipt)

    for key in ("reviewer_id", "review_run_id"):
        values = [receipt[key] for receipt in receipts]
        duplicates = [value for value, count in Counter(values).items() if count > 1]
        assert not duplicates, f"{key} doit etre unique: {duplicates}"

    if (root / "audit" / "reviews" / "1nsi" / "p0" / SUMMARY_FILENAME).is_file():
        assert len(receipts) == 14
        assert {receipt["p0_id"] for receipt in receipts} == EXPECTED_P0_IDS
    return receipts


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def test_schema_is_closed_and_accepts_a_complete_fixture() -> None:
    schema = _load_schema()
    Draft202012Validator.check_schema(schema)
    assert schema["additionalProperties"] is False
    assert schema["$defs"]["source_file"]["additionalProperties"] is False
    assert schema["$defs"]["command"]["additionalProperties"] is False
    Draft202012Validator(schema, format_checker=FORMAT_CHECKER).validate(_valid_receipt())


def test_schema_rejects_unknown_properties_and_incomplete_command_results() -> None:
    schema = _load_schema()
    document = _valid_receipt()
    document["unexpected"] = "forbidden"
    document["source_files"][0]["unexpected"] = "forbidden"
    document["source_files"].append(copy.deepcopy(document["source_files"][0]))
    del document["commands"][0]["stderr_sha256"]
    document["commands"][0]["exit_code"] = "zero"
    errors = list(
        Draft202012Validator(schema, format_checker=FORMAT_CHECKER).iter_errors(document)
    )
    assert len(errors) >= 5


def test_schema_enforces_formats_and_enumerations() -> None:
    schema = _load_schema()
    document = _valid_receipt()
    document["source_commit_sha"] = "A" * 40
    document["reviewed_at"] = "2026-13-99T25:99:99+00:00"
    document["cache_status"] = "cached"
    errors = list(
        Draft202012Validator(schema, format_checker=FORMAT_CHECKER).iter_errors(document)
    )
    assert len(errors) >= 3


def test_date_time_requires_an_rfc3339_minute_precision_offset() -> None:
    assert _is_rfc3339_datetime("2026-08-10T12:00:00+00:00")
    assert not _is_rfc3339_datetime("2026-08-10T12:00:00+00:00:01")


def test_command_output_digest_rejects_altered_stdout() -> None:
    command = _valid_receipt()["commands"][0]
    command["stdout"] = "sortie falsifiee"
    with pytest.raises(AssertionError, match="stdout"):
        _assert_command_output_hashes([command])


def test_receipt_secret_detector_rejects_fake_credential_only() -> None:
    path = Path("fixture.yaml")
    _assert_no_secret("reviewer_id: unit-reviewer", path)
    with pytest.raises(AssertionError, match="secret ou credential"):
        _assert_no_secret("Authorization: Bearer sk-" + "x" * 24, path)


@pytest.mark.parametrize(
    "raw",
    [
        "GITHUB_TOKEN=fake-token",
        "ghp_" + "x" * 36,
        "github_pat_" + "x" * 24,
        "x-api-key: fake-key",
        "API_KEY=fake-key",
        "TOKEN: fake-token",
        "SECRET=fake-secret",
        "PASSWORD: fake-password",
    ],
)
def test_receipt_secret_detector_rejects_additional_fake_credentials(raw: str) -> None:
    with pytest.raises(AssertionError, match="secret ou credential"):
        _assert_no_secret(raw, Path("fixture.yaml"))


@pytest.mark.parametrize(
    "raw",
    [
        "GITHUB_TOKEN",
        "API_KEY=not_applicable",
        "TOKEN: redacted",
        "SECRET=none",
        "PASSWORD: null",
    ],
)
def test_receipt_secret_detector_allows_names_and_sentinels(raw: str) -> None:
    _assert_no_secret(raw, Path("fixture.yaml"))


@pytest.mark.parametrize(
    "raw",
    [
        'API_KEY: "secret-value" # documented',
        "x-api-key: secret value # documented",
    ],
)
def test_receipt_secret_detector_rejects_yaml_values_with_comments(raw: str) -> None:
    with pytest.raises(AssertionError, match="secret ou credential"):
        _assert_no_secret(raw, Path("fixture.yaml"))


@pytest.mark.parametrize(
    "raw",
    [
        "TOKEN: redacted # commentaire",
        'API_KEY: "not_applicable" # commentaire',
    ],
)
def test_receipt_secret_detector_allows_yaml_sentinels_with_comments(raw: str) -> None:
    _assert_no_secret(raw, Path("fixture.yaml"))


def test_existing_receipts_validate_when_present() -> None:
    _validate_receipts()


def test_untracked_receipt_skips_parent_check_then_commit_enforces_it(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.name", "Unit Reviewer")
    _git(tmp_path, "config", "user.email", "unit-reviewer@example.test")
    (tmp_path / "source.txt").write_bytes(b"source\n")
    _git(tmp_path, "add", "source.txt")
    _git(tmp_path, "commit", "-m", "source")
    source_commit = _run_git(tmp_path, "rev-parse", "HEAD")
    assert isinstance(source_commit, str)

    # The receipt remains pre-commit: its source is valid but no parent exists yet.
    receipt = _valid_receipt()
    receipt["source_commit_sha"] = source_commit.strip()
    receipt_path = tmp_path / "audit" / "reviews" / "1nsi" / "p0" / "2026-08-10-unit.yaml"
    receipt_path.parent.mkdir(parents=True)
    receipt_path.write_text(yaml.safe_dump(receipt, sort_keys=False), encoding="utf-8")
    _validate_receipts(tmp_path)

    # An intervening commit makes the later receipt's direct parent incorrect.
    (tmp_path / "intermediate.txt").write_text("intermediate\n", encoding="utf-8")
    _git(tmp_path, "add", "intermediate.txt")
    _git(tmp_path, "commit", "-m", "intermediate")
    _git(tmp_path, "add", receipt_path.relative_to(tmp_path).as_posix())
    _git(tmp_path, "commit", "-m", "attestation")
    with pytest.raises(AssertionError, match="parent du commit d'ajout"):
        _validate_receipts(tmp_path)
