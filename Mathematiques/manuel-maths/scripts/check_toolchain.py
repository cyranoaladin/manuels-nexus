#!/usr/bin/env python3
"""Contrôle reproductible de la chaîne de fabrication d'une release 1SPE.

Le contrôle ne modifie ni n'installe aucun outil. La capacité Tagged PDF est
prouvée par la compilation isolée d'un document minimal puis par sa validation
veraPDF PDF/UA-1 ; la seule présence de LuaLaTeX ne peut pas la certifier.
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
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

import yaml


DEFAULT_REPORT = Path("validations/release-1spe/toolchain.json")
TEX_ENVIRONMENT_OVERRIDES = {
    "TEXINPUTS",
    "LUAINPUTS",
    "TEXMFCNF",
    "TEXMFHOME",
    "TEXMFVAR",
    "TEXMFCONFIG",
    "BIBINPUTS",
    "BSTINPUTS",
    "MFINPUTS",
    "MPINPUTS",
    "TFMFONTS",
    "VFFONTS",
    "T1FONTS",
    "OPENTYPEFONTS",
    "TTFONTS",
    "LUA_PATH",
    "LUA_CPATH",
}
TAGGED_PDF_SMOKE_SOURCE = r"""\DocumentMetadata{
  lang=fr,
  pdfversion=1.7,
  pdfstandard=ua-1,
  tagging=on
}
\documentclass{article}
\usepackage{hyperref}
\hypersetup{
  pdftitle={Contrôle Tagged PDF Nexus Réussite},
  pdfauthor={Nexus Réussite}
}
\title{Contrôle Tagged PDF}
\author{Nexus Réussite}
\begin{document}
\maketitle
\section{Contenu}
Ce document minimal contrôle la production PDF/UA-1.
\end{document}
"""


class ManifestError(ValueError):
    """Signale un manifeste incomplet ou incohérent."""

    def __init__(self, message: str, *, category: str = "contract"):
        super().__init__(message)
        self.category = category


@dataclass(frozen=True)
class ToolchainResult:
    report: dict[str, Any]

    @property
    def status(self) -> str:
        return str(self.report["status"])

    @property
    def exit_code(self) -> int:
        return 0 if self.status == "certified" else 2


@dataclass(frozen=True)
class SmokeResult:
    ok: bool
    reason: str


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
        serialized = source.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ManifestError(
            f"lecture impossible de {source}: {exc}",
            category="access",
        ) from exc
    try:
        data = yaml.safe_load(serialized)
    except yaml.YAMLError as exc:
        raise ManifestError(
            f"syntaxe YAML invalide dans {source}: {exc}",
            category="yaml",
        ) from exc
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


def _resolve_binary(
    binary: str,
    *,
    which: Callable[[str], str | None],
) -> tuple[str | None, str | None]:
    try:
        located = which(binary)
    except (OSError, TypeError, ValueError) as exc:
        return None, f"résolution impossible: {type(exc).__name__}"
    if located is None:
        return None, f"binaire absent: {binary}"
    try:
        resolved = Path(located).expanduser().resolve(strict=False)
    except (OSError, TypeError, ValueError) as exc:
        return None, f"résolution impossible: {type(exc).__name__}"
    return str(resolved), None


def _run_version(
    binary: str | None,
    arguments: list[str],
    *,
    resolution_error: str | None,
    runner: Callable[..., Any],
) -> tuple[str | None, str | None]:
    if binary is None:
        return None, resolution_error or "binaire non résolu"
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


def _smoke_environment(
    environ: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Copie l'environnement en neutralisant les entrées TeX configurables."""

    sanitized = dict(os.environ if environ is None else environ)
    for variable in TEX_ENVIRONMENT_OVERRIDES:
        sanitized.pop(variable, None)
    return sanitized


def run_tagged_pdf_smoke(
    *,
    latex_binary: str,
    verapdf_binary: str,
    profile: str,
    report_format: str,
    runner: Callable[..., Any],
) -> SmokeResult:
    """Compile et valide un PDF/UA-1 éphémère, sans exposer son chemin."""

    try:
        with tempfile.TemporaryDirectory(prefix="nexus-tagged-pdf-") as directory:
            smoke_directory = Path(directory)
            source = smoke_directory / "tagged-smoke.tex"
            pdf = smoke_directory / "tagged-smoke.pdf"
            smoke_environment = _smoke_environment()
            source.write_text(TAGGED_PDF_SMOKE_SOURCE, encoding="utf-8")

            compile_process = runner(
                [
                    latex_binary,
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    f"-output-directory={smoke_directory}",
                    str(source),
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
                cwd=smoke_directory,
                env=smoke_environment,
            )
            if compile_process.returncode != 0:
                return SmokeResult(
                    False,
                    (
                        "smoke Tagged PDF: compilation LuaLaTeX échouée "
                        f"(code {compile_process.returncode})"
                    ),
                )
            if not pdf.is_file():
                return SmokeResult(
                    False,
                    "smoke Tagged PDF: PDF absent après compilation LuaLaTeX",
                )

            validation_process = runner(
                [
                    verapdf_binary,
                    "-f",
                    profile,
                    "--format",
                    report_format,
                    str(pdf),
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
                cwd=smoke_directory,
                env=smoke_environment,
            )
            if validation_process.returncode == 0:
                return SmokeResult(
                    True,
                    (
                        "compilation Tagged PDF et validation veraPDF "
                        "PDF/UA-1 réussies"
                    ),
                )
            if validation_process.returncode == 1:
                return SmokeResult(
                    False,
                    (
                        "smoke Tagged PDF: veraPDF signale un PDF/UA-1 "
                        "non conforme (code 1)"
                    ),
                )
            if validation_process.returncode == 2:
                return SmokeResult(
                    False,
                    (
                        "smoke Tagged PDF: veraPDF rejette le profil ua1 "
                        "ou le format mrr (code 2)"
                    ),
                )
            return SmokeResult(
                False,
                (
                    "smoke Tagged PDF: validation veraPDF échouée "
                    f"(code {validation_process.returncode})"
                ),
            )
    except (OSError, subprocess.SubprocessError) as exc:
        return SmokeResult(
            False,
            f"smoke Tagged PDF: exécution impossible ({type(exc).__name__})",
        )


def _tagged_prerequisite_reason(
    *,
    latex_binary: str,
    latex_error: str | None,
    texlive_year: str | None,
    required_texlive: int,
    verapdf_error: str | None,
    verapdf_version: str | None,
    required_verapdf: str,
) -> str:
    failures: list[str] = []
    if latex_error == f"binaire absent: {latex_binary}":
        failures.append(f"binaire {latex_binary} absent")
    elif latex_error is not None:
        failures.append("commande LuaLaTeX indisponible")
    elif texlive_year is None:
        failures.append("version TeX Live illisible")
    elif int(texlive_year) < required_texlive:
        failures.append(
            f"TeX Live {required_texlive} requis, version détectée: {texlive_year}"
        )

    if verapdf_error == "binaire absent: verapdf":
        failures.append("binaire veraPDF absent")
    elif verapdf_error is not None:
        failures.append("commande veraPDF indisponible")
    elif verapdf_version is None:
        failures.append("version veraPDF illisible")
    elif verapdf_version != required_verapdf:
        failures.append(
            f"veraPDF {required_verapdf} exigé, version détectée: {verapdf_version}"
        )
    return "smoke Tagged PDF non exécuté: " + "; ".join(failures)


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

    java_binary, java_resolution_error = _resolve_binary(
        "java",
        which=binary_locator,
    )
    java_output, java_error = _run_version(
        java_binary,
        ["-version"],
        resolution_error=java_resolution_error,
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
        else (
            f"Java >= {required_java} exigé; version détectée: {java_version}"
            if java_version is not None
            else f"Java >= {required_java} exigé; version illisible"
        )
    )
    checks.append(
        _check("java", f">={required_java}", java_version, java_ok, java_reason)
    )

    latex_engine = manifest["latex"]["engine"]
    latex_binary, latex_resolution_error = _resolve_binary(
        latex_engine,
        which=binary_locator,
    )
    latex_output, latex_error = _run_version(
        latex_binary,
        ["--version"],
        resolution_error=latex_resolution_error,
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
            f"{latex_engine}, TeX Live >={required_texlive}",
            latex_detected,
            latex_ok,
            latex_reason,
        )
    )
    verapdf_binary, verapdf_resolution_error = _resolve_binary(
        "verapdf",
        which=binary_locator,
    )
    verapdf_output, verapdf_error = _run_version(
        verapdf_binary,
        ["--version"],
        resolution_error=verapdf_resolution_error,
        runner=command_runner,
    )
    verapdf_version = (
        _extract(r"veraPDF(?:\s+CLI)?\s+([^\s]+)", verapdf_output)
        if verapdf_output
        else None
    )
    required_verapdf = manifest["verapdf"]["version"]
    verapdf_ok = (
        verapdf_version is not None
        and verapdf_version == required_verapdf
    )
    verapdf_reason = verapdf_error or (
        f"veraPDF {required_verapdf} détecté"
        if verapdf_ok
        else (
            (
                f"veraPDF {required_verapdf} exigé; "
                f"version détectée: {verapdf_version}"
            )
            if verapdf_version is not None
            else f"veraPDF {required_verapdf} exigé; version illisible"
        )
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

    if latex_ok and verapdf_ok:
        assert latex_binary is not None
        assert verapdf_binary is not None
        tagged_smoke = run_tagged_pdf_smoke(
            latex_binary=latex_binary,
            verapdf_binary=verapdf_binary,
            profile=manifest["verapdf"]["profile"],
            report_format=manifest["verapdf"]["report_format"],
            runner=command_runner,
        )
        tagged_detected = "smoke PDF/UA-1 conforme" if tagged_smoke.ok else None
        tagged_reason = tagged_smoke.reason
        tagged_ok = tagged_smoke.ok
    else:
        tagged_detected = None
        tagged_reason = _tagged_prerequisite_reason(
            latex_binary=latex_engine,
            latex_error=latex_error,
            texlive_year=texlive_year,
            required_texlive=required_texlive,
            verapdf_error=verapdf_error,
            verapdf_version=verapdf_version,
            required_verapdf=required_verapdf,
        )
        tagged_ok = False
    checks.append(
        _check(
            "latex.tagged_pdf",
            (
                "smoke LuaLaTeX TeX Live >=2026 + veraPDF 1.30.1 "
                "-f ua1 --format mrr"
            ),
            tagged_detected,
            tagged_ok,
            tagged_reason,
        )
    )

    required_poppler = manifest["poppler"]["minimum_version"]
    for command in manifest["poppler"]["commands"]:
        resolved_command, command_resolution_error = _resolve_binary(
            command,
            which=binary_locator,
        )
        output, error = _run_version(
            resolved_command,
            ["-v"],
            resolution_error=command_resolution_error,
            runner=command_runner,
        )
        version = _extract(r"version\s+(\d+\.\d+(?:\.\d+)?)", output) if output else None
        ok = version is not None and _at_least(version, required_poppler)
        reason = error or (
            f"{command} >= {required_poppler} détecté"
            if ok
            else (
                (
                    f"{command} >= {required_poppler} exigé; "
                    f"version détectée: {version}"
                )
                if version is not None
                else f"{command} >= {required_poppler} exigé; version illisible"
            )
        )
        checks.append(
            _check(command, f">={required_poppler}", version, ok, reason)
        )

    gs_binary, gs_resolution_error = _resolve_binary(
        "gs",
        which=binary_locator,
    )
    gs_output, gs_error = _run_version(
        gs_binary,
        ["--version"],
        resolution_error=gs_resolution_error,
        runner=command_runner,
    )
    gs_version = _extract(r"(\d+\.\d+(?:\.\d+)?)", gs_output) if gs_output else None
    required_gs = manifest["ghostscript"]["minimum_version"]
    gs_ok = gs_version is not None and _at_least(gs_version, required_gs)
    gs_reason = gs_error or (
        f"Ghostscript >= {required_gs} détecté"
        if gs_ok
        else (
            f"Ghostscript >= {required_gs} exigé; version détectée: {gs_version}"
            if gs_version is not None
            else f"Ghostscript >= {required_gs} exigé; version illisible"
        )
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
            os.fchmod(stream.fileno(), 0o644)
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


def _blocked_manifest_report(error: ManifestError) -> dict[str, Any]:
    reasons = {
        "access": (
            "manifeste inaccessible; vérifier sa présence et ses permissions"
        ),
        "yaml": (
            "manifeste YAML invalide; corriger la syntaxe du "
            "manifeste d'outillage"
        ),
        "contract": (
            "contrat d'outillage invalide; corriger les clés "
            "et valeurs épinglées"
        ),
    }
    reason = reasons.get(error.category, reasons["contract"])
    check = {
        "id": "manifest",
        "required": "manifeste d'outillage valide (schema_version 1)",
        "detected": None,
        "status": "blocked",
        "reason": reason,
    }
    return {
        "schema_version": 1,
        "status": "blocked",
        "checks": [check],
        "blockers": [{"tool": "manifest", "reason": reason}],
    }


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        manifest = load_manifest(arguments.manifest)
        result = check_toolchain(manifest)
    except ManifestError as exc:
        write_report_atomic(arguments.output, _blocked_manifest_report(exc))
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
