#!/usr/bin/env python3
"""Contrôle reproductible de la chaîne de fabrication d'une release 1SPE.

Le contrôle ne modifie ni n'installe aucun outil. La capacité Tagged PDF est
liée ici au contrat TeX Live 2026 minimum ; la conformité des documents
produits reste ensuite à prouver avec veraPDF et le profil PDF/UA-1.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

import yaml


DEFAULT_REPORT = Path("validations/release-1spe/toolchain.json")


class ManifestError(ValueError):
    """Signale un manifeste incomplet ou incohérent."""


@dataclass(frozen=True)
class ToolchainResult:
    report: dict[str, Any]

    @property
    def status(self) -> str:
        return str(self.report["status"])

    @property
    def exit_code(self) -> int:
        return 0 if self.status == "certified" else 2


def _require_keys(
    value: Any,
    path: str,
    required: set[str],
    *,
    exact: bool = True,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ManifestError(f"{path} doit être un objet")
    missing = sorted(required - set(value))
    if missing:
        raise ManifestError(f"{path}: clé(s) manquante(s): {', '.join(missing)}")
    if exact:
        unexpected = sorted(set(value) - required)
        if unexpected:
            raise ManifestError(
                f"{path}: clé(s) inconnue(s): {', '.join(unexpected)}"
            )
    return value


def _require_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise ManifestError(f"{path} doit être une chaîne non vide")
    return value


def _require_integer(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ManifestError(f"{path} doit être un entier")
    return value


def validate_manifest(data: Any) -> dict[str, Any]:
    root_keys = {
        "schema_version",
        "python",
        "java",
        "latex",
        "verapdf",
        "poppler",
        "ghostscript",
    }
    manifest = _require_keys(data, "racine", root_keys)
    if _require_integer(manifest["schema_version"], "schema_version") != 1:
        raise ManifestError("schema_version doit valoir 1")

    python_pin = _require_string(manifest["python"], "python")
    if not re.fullmatch(r"\d+\.\d+", python_pin):
        raise ManifestError("python doit épingler une version majeure.mineure")
    if python_pin != "3.12":
        raise ManifestError("python doit valoir 3.12")

    java = _require_keys(manifest["java"], "java", {"minimum_major"})
    if _require_integer(java["minimum_major"], "java.minimum_major") != 21:
        raise ManifestError("java.minimum_major doit valoir 21")

    latex = _require_keys(
        manifest["latex"],
        "latex",
        {"engine", "minimum_texlive", "tagged_pdf"},
    )
    if _require_string(latex["engine"], "latex.engine") != "lualatex":
        raise ManifestError("latex.engine doit valoir lualatex")
    if _require_integer(latex["minimum_texlive"], "latex.minimum_texlive") != 2026:
        raise ManifestError("latex.minimum_texlive doit valoir 2026")
    if latex["tagged_pdf"] is not True:
        raise ManifestError("latex.tagged_pdf doit valoir true")

    verapdf = _require_keys(
        manifest["verapdf"],
        "verapdf",
        {"version", "profile", "report_format"},
    )
    if _require_string(verapdf["version"], "verapdf.version") != "1.30.1":
        raise ManifestError("verapdf.version doit valoir 1.30.1")
    if _require_string(verapdf["profile"], "verapdf.profile") != "ua1":
        raise ManifestError("verapdf.profile doit valoir ua1")
    if _require_string(verapdf["report_format"], "verapdf.report_format") != "mrr":
        raise ManifestError("verapdf.report_format doit valoir mrr")

    poppler = _require_keys(
        manifest["poppler"],
        "poppler",
        {"minimum_version", "commands"},
    )
    if (
        _require_string(poppler["minimum_version"], "poppler.minimum_version")
        != "24.02.0"
    ):
        raise ManifestError("poppler.minimum_version doit valoir 24.02.0")
    commands = poppler["commands"]
    expected_commands = ["pdfinfo", "pdffonts", "pdftotext", "pdftoppm"]
    if commands != expected_commands:
        raise ManifestError(
            "poppler.commands doit valoir "
            "[pdfinfo, pdffonts, pdftotext, pdftoppm]"
        )

    ghostscript = _require_keys(
        manifest["ghostscript"],
        "ghostscript",
        {"minimum_version"},
    )
    if (
        _require_string(
            ghostscript["minimum_version"], "ghostscript.minimum_version"
        )
        != "10.02"
    ):
        raise ManifestError("ghostscript.minimum_version doit valoir 10.02")
    return manifest


def load_manifest(path: Path | str) -> dict[str, Any]:
    source = Path(path)
    try:
        data = yaml.safe_load(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ManifestError(f"lecture impossible de {source}: {exc}") from exc
    return validate_manifest(data)


def _version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def _at_least(detected: str, required: str) -> bool:
    actual = _version_tuple(detected)
    minimum = _version_tuple(required)
    width = max(len(actual), len(minimum))
    return actual + (0,) * (width - len(actual)) >= minimum + (0,) * (
        width - len(minimum)
    )


def _check(
    check_id: str,
    required: str,
    detected: str | None,
    ok: bool,
    reason: str,
) -> dict[str, str | None]:
    return {
        "id": check_id,
        "required": required,
        "detected": detected,
        "status": "certified" if ok else "blocked",
        "reason": reason,
    }


def _run_version(
    binary: str,
    arguments: list[str],
    *,
    which: Callable[[str], str | None],
    runner: Callable[..., Any],
) -> tuple[str | None, str | None]:
    if which(binary) is None:
        return None, f"binaire absent: {binary}"
    try:
        process = runner(
            [binary, *arguments],
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return None, f"exécution impossible: {type(exc).__name__}"
    if process.returncode != 0:
        return None, f"commande terminée avec le code {process.returncode}"
    output = "\n".join(
        part for part in (process.stdout, process.stderr) if isinstance(part, str)
    )
    return output, None


def _extract(pattern: str, output: str) -> str | None:
    match = re.search(pattern, output, flags=re.IGNORECASE)
    return match.group(1) if match else None


def check_toolchain(
    manifest: dict[str, Any],
    *,
    which: Callable[[str], str | None] | None = None,
    runner: Callable[..., Any] | None = None,
    python_version: Sequence[int] | None = None,
) -> ToolchainResult:
    """Contrôle tous les prérequis sans installer ni exposer l'environnement."""

    manifest = validate_manifest(manifest)
    binary_locator = which or shutil.which
    command_runner = runner or subprocess.run
    runtime = tuple(python_version or sys.version_info[:3])
    checks: list[dict[str, str | None]] = []

    required_python = manifest["python"]
    detected_python = ".".join(str(part) for part in runtime[:3])
    python_ok = tuple(runtime[:2]) == _version_tuple(required_python)
    checks.append(
        _check(
            "python",
            required_python,
            detected_python,
            python_ok,
            (
                f"Python {required_python}.x détecté"
                if python_ok
                else f"Python {required_python}.x exigé"
            ),
        )
    )

    java_output, java_error = _run_version(
        "java",
        ["-version"],
        which=binary_locator,
        runner=command_runner,
    )
    java_version = (
        _extract(r'version\s+"?(\d+(?:\.\d+){0,3})', java_output)
        if java_output
        else None
    )
    required_java = manifest["java"]["minimum_major"]
    java_ok = java_version is not None and int(java_version.split(".")[0]) >= required_java
    java_reason = java_error or (
        f"Java >= {required_java} détecté"
        if java_ok
        else f"Java >= {required_java} exigé; version illisible ou insuffisante"
    )
    checks.append(
        _check("java", f">={required_java}", java_version, java_ok, java_reason)
    )

    latex_binary = manifest["latex"]["engine"]
    latex_output, latex_error = _run_version(
        latex_binary,
        ["--version"],
        which=binary_locator,
        runner=command_runner,
    )
    texlive_year = (
        _extract(r"TeX Live\s+(\d{4})", latex_output) if latex_output else None
    )
    required_texlive = manifest["latex"]["minimum_texlive"]
    latex_ok = texlive_year is not None and int(texlive_year) >= required_texlive
    latex_detected = f"TeX Live {texlive_year}" if texlive_year else None
    latex_reason = latex_error or (
        f"TeX Live >= {required_texlive} détecté"
        if latex_ok
        else (
            f"TeX Live >= {required_texlive} exigé; version détectée: {texlive_year}"
            if texlive_year is not None
            else f"TeX Live >= {required_texlive} exigé; version illisible"
        )
    )
    checks.append(
        _check(
            "latex.engine",
            f"{latex_binary}, TeX Live >={required_texlive}",
            latex_detected,
            latex_ok,
            latex_reason,
        )
    )
    tagged_reason = (
        "contrat Tagged PDF activé par TeX Live 2026 minimum; "
        "la conformité documentaire reste contrôlée par veraPDF PDF/UA-1"
        if latex_ok
        else "Tagged PDF exige TeX Live 2026 minimum avant validation veraPDF"
    )
    checks.append(
        _check(
            "latex.tagged_pdf",
            "true (TeX Live >=2026 + validation veraPDF PDF/UA-1)",
            "contract-enabled" if latex_ok else None,
            latex_ok,
            tagged_reason,
        )
    )

    verapdf_output, verapdf_error = _run_version(
        "verapdf",
        ["--version"],
        which=binary_locator,
        runner=command_runner,
    )
    verapdf_version = (
        _extract(r"veraPDF(?:\s+CLI)?\s+(\d+\.\d+\.\d+)", verapdf_output)
        if verapdf_output
        else None
    )
    required_verapdf = manifest["verapdf"]["version"]
    verapdf_ok = (
        verapdf_version is not None
        and _version_tuple(verapdf_version) == _version_tuple(required_verapdf)
    )
    verapdf_reason = verapdf_error or (
        f"veraPDF {required_verapdf} détecté"
        if verapdf_ok
        else f"veraPDF {required_verapdf} exigé; version illisible ou différente"
    )
    checks.append(
        _check(
            "verapdf",
            (
                f"{required_verapdf}, profil {manifest['verapdf']['profile']}, "
                f"rapport {manifest['verapdf']['report_format']}"
            ),
            verapdf_version,
            verapdf_ok,
            verapdf_reason,
        )
    )

    required_poppler = manifest["poppler"]["minimum_version"]
    for command in manifest["poppler"]["commands"]:
        output, error = _run_version(
            command,
            ["-v"],
            which=binary_locator,
            runner=command_runner,
        )
        version = _extract(r"version\s+(\d+\.\d+(?:\.\d+)?)", output) if output else None
        ok = version is not None and _at_least(version, required_poppler)
        reason = error or (
            f"{command} >= {required_poppler} détecté"
            if ok
            else f"{command} >= {required_poppler} exigé; version illisible ou insuffisante"
        )
        checks.append(
            _check(command, f">={required_poppler}", version, ok, reason)
        )

    gs_output, gs_error = _run_version(
        "gs",
        ["--version"],
        which=binary_locator,
        runner=command_runner,
    )
    gs_version = _extract(r"(\d+\.\d+(?:\.\d+)?)", gs_output) if gs_output else None
    required_gs = manifest["ghostscript"]["minimum_version"]
    gs_ok = gs_version is not None and _at_least(gs_version, required_gs)
    gs_reason = gs_error or (
        f"Ghostscript >= {required_gs} détecté"
        if gs_ok
        else f"Ghostscript >= {required_gs} exigé; version illisible ou insuffisante"
    )
    checks.append(
        _check("ghostscript", f">={required_gs}", gs_version, gs_ok, gs_reason)
    )

    blockers = [
        {"tool": item["id"], "reason": item["reason"]}
        for item in checks
        if item["status"] == "blocked"
    ]
    report = {
        "schema_version": 1,
        "status": "blocked" if blockers else "certified",
        "checks": checks,
        "blockers": blockers,
    }
    return ToolchainResult(report)


def write_report_atomic(path: Path | str, report: dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_name = stream.name
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, destination)
        temporary_name = None
    finally:
        if temporary_name is not None:
            try:
                Path(temporary_name).unlink()
            except FileNotFoundError:
                pass


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Contrôle la chaîne de fabrication de la release 1SPE."
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        manifest = load_manifest(arguments.manifest)
        result = check_toolchain(manifest)
    except ManifestError as exc:
        print(f"Manifeste invalide: {exc}", file=sys.stderr)
        return 2

    write_report_atomic(arguments.output, result.report)
    print(
        f"toolchain: {result.status} "
        f"({len(result.report['blockers'])} blocage(s)); "
        f"rapport={arguments.output}"
    )
    for blocker in result.report["blockers"]:
        print(f"- {blocker['tool']}: {blocker['reason']}")
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
