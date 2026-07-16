"""Vérifie l'identité du tronc commun de la charte Nexus."""

from __future__ import annotations

import hashlib
from pathlib import Path


COMMON_FILES = (
    Path("gabarits/nexus-manuel.cls"),
    Path("gabarits/nexus-icons.tex"),
    Path("gabarits/nexus-figures.tex"),
    Path("gabarits/nexus-signatures.tex"),
    Path("docs/06_charte_graphique.md"),
    Path("docs/07_ligne_editoriale.md"),
)


def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_mismatches(maths_root: Path, nsi_root: Path) -> list[Path]:
    """Retourne les fichiers du tronc commun absents ou divergents côté NSI."""
    mismatches = []
    for relative in COMMON_FILES:
        source = maths_root / relative
        destination = nsi_root / relative
        if not source.is_file() or not destination.is_file() or checksum(source) != checksum(destination):
            mismatches.append(relative)
    return mismatches


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    mismatches = find_mismatches(root / "Mathematiques/manuel-maths", root / "NSI")
    if not mismatches:
        print("Charte Nexus synchronisée : 6/6 fichiers identiques.")
        return 0
    print("Dérive de charte détectée :")
    for relative in mismatches:
        print(f"- {relative}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
