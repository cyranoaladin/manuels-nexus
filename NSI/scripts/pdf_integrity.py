"""Gates d'intégrité des sorties LuaLaTeX."""

from __future__ import annotations

import subprocess
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any


MISSING_ASSET = "Nexus asset missing:"


def log_has_missing_asset_warning(log: str) -> bool:
    return MISSING_ASSET in log


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
    runner: Callable[..., Any] | None = None,
    environment: Mapping[str, str] | None = None,
) -> int:
    if log_has_missing_asset_warning(log.read_text(encoding="utf-8", errors="replace")):
        print(f"Gabarit Nexus absent : {log}")
        return 1
    try:
        active_runner = subprocess.run if runner is None else runner
        options: dict[str, Any] = {
            "capture_output": True,
            "text": True,
            "check": True,
        }
        if environment is not None:
            options["env"] = dict(environment)
        result = active_runner(["pdffonts", str(pdf)], **options)
    except FileNotFoundError:
        print("Gate polices : pdffonts (poppler-utils) introuvable")
        return 1
    if not fonts_are_embedded(result.stdout):
        print(result.stdout)
        return 1
    return 0
