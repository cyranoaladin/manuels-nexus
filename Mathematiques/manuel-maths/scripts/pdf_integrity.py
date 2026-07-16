"""Gates d'intégrité des sorties LuaLaTeX."""

from __future__ import annotations

import subprocess
from pathlib import Path


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


def verify_pdf(pdf: Path, log: Path) -> int:
    if log_has_missing_asset_warning(log.read_text(encoding="utf-8", errors="replace")):
        print(f"Gabarit Nexus absent : {log}")
        return 1
    try:
        result = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True, check=True)
    except FileNotFoundError:
        print("Gate polices : pdffonts (poppler-utils) introuvable")
        return 1
    if not fonts_are_embedded(result.stdout):
        print(result.stdout)
        return 1
    return 0
