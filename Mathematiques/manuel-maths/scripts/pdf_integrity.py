"""Gates d'intégrité des sorties LuaLaTeX."""

from __future__ import annotations

import subprocess
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any


MISSING_ASSET = "Nexus asset missing:"
MISSING_CHARACTER = "Missing character:"
COMMAND_TIMEOUT_SECONDS = 20


@dataclass(frozen=True)
class MarginEvidence:
    """The three closed artefacts required by the composed margin gate."""

    capture_inventory: Mapping[str, Any] | str | Path
    stable_layout: Mapping[str, Any] | str | Path
    ledger: Mapping[str, Any] | str | Path


def log_has_missing_asset_warning(log: str) -> bool:
    return MISSING_ASSET in log


def log_has_missing_character_warning(log: str) -> bool:
    return MISSING_CHARACTER in log


def fonts_are_embedded(output: str) -> bool:
    lines = [line.split() for line in output.splitlines()[2:] if line.strip()]
    for fields in lines:
        if len(fields) < 5 or fields[-5] != "yes":
            return False
        if fields[-4] != "yes":
            print(f"Avertissement : police non sous-ensemblée ({' '.join(fields[:-5])}).")
    return bool(lines)


def verify_pdf(
    pdf: Path,
    log: Path,
    *,
    require_margin_proof: bool = False,
    margin_evidence: MarginEvidence | None = None,
    runner: Callable[..., Any] | None = None,
    environment: Mapping[str, str] | None = None,
) -> int:
    log_text = log.read_text(encoding="utf-8", errors="replace")
    if log_has_missing_asset_warning(log_text):
        print(f"Gabarit Nexus absent : {log}")
        return 1
    if log_has_missing_character_warning(log_text):
        print(f"Glyphe manquant dans le PDF : {log}")
        return 1
    try:
        active_runner = subprocess.run if runner is None else runner
        options: dict[str, Any] = {
            "capture_output": True,
            "text": True,
            "check": True,
            "timeout": COMMAND_TIMEOUT_SECONDS,
        }
        if environment is not None:
            options["env"] = dict(environment)
        result = active_runner(["pdffonts", str(pdf)], **options)
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
        print("Gate polices : pdffonts (poppler-utils) introuvable")
        return 1
    if not fonts_are_embedded(result.stdout):
        print(result.stdout)
        return 1
    if margin_evidence is None:
        if require_margin_proof:
            print("Gate marges : preuve marginale requise mais absente")
            return 1
        return 0

    for value, label in (
        (margin_evidence.capture_inventory, "inventaire de capture marginal absent"),
        (margin_evidence.stable_layout, "placement marginal stable absent"),
        (margin_evidence.ledger, "ledger marginal absent"),
    ):
        if isinstance(value, (str, Path)) and not Path(value).is_file():
            print(f"Gate marges : {label}")
            return 1
    try:
        margin_ledger = import_module("margin_ledger")
    except ModuleNotFoundError as exc:
        if exc.name == "pikepdf" or "pikepdf" in str(exc):
            print("Gate marges : parseur PDF pikepdf indisponible")
        else:
            print(f"Gate marges : vérificateur indisponible ({exc})")
        return 1
    try:
        result = margin_ledger.verify_margin_layout(
            pdf,
            margin_evidence.capture_inventory,
            margin_evidence.stable_layout,
            margin_evidence.ledger,
            runner=runner,
            environment=environment,
        )
    except (margin_ledger.MarginLedgerError, OSError, ValueError) as exc:
        print(f"Gate marges : {exc}")
        return 1
    if not result.passed:
        print("Gate marges : résultat structuré non passant")
        return 1
    return 0
