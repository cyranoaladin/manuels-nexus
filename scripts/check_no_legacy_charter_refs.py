#!/usr/bin/env python3
"""
Gate CI : interdiction de CHARGER l'ancien moteur (charte V4/V4.1 heritee) ou un
fork non autorise dans les chemins de compilation de production.

Ce que le gate juge est un chargement, jamais une mention. Les scripts qui
surveillent la charte heritee doivent la nommer pour l'exclure ou la detecter :
les signaler obligeait a maintenir une liste blanche de leurs propres noms de
fichiers, c'est-a-dire une exemption accordee par identite plutot que par
raison. La regle porte donc sur les directives de chargement LaTeX, y compris
celles qu'un assembleur ecrit dans un master.

Le filtre de perimetre porte sur le chemin RELATIF a la racine. Applique aux
segments du chemin absolu, il excluait la totalite d'un depot situe sous un
repertoire nomme `.worktrees` -- le cas de `.worktrees/t3-publish-readiness`,
ou vivait toute la production : le gate analysait alors zero fichier et
concluait SUCCESS.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Cibles heritees dont le chargement est interdit en production.
LEGACY_TARGETS = r"(?:nexus-manuel-v4|nexus-charte-v4|reference-v4|gabarits/v4)"

#: Directives qui font reellement entrer un fichier dans la compilation.
LOAD_DIRECTIVES = r"(?:documentclass|LoadClass(?:WithOptions)?|usepackage|RequirePackage(?:WithOptions)?|input|include(?:only)?)"

#: Une directive de chargement dont l'argument nomme une cible heritee. Le
#: `\\{1,2}` accepte la contre-oblique echappee d'un assembleur Python qui ecrit
#: la directive dans un master : le fichier produit chargerait la charte v4.
LEGACY_LOAD = re.compile(
    r"\\{1,2}" + LOAD_DIRECTIVES + r"\s*(?:\[[^\]]*\])?\s*\{[^}]*" + LEGACY_TARGETS + r"[^}]*\}",
    re.IGNORECASE,
)

#: Repertoires hors du perimetre de production.
EXCLUDED_PARTS = {
    ".worktrees", ".git", "archive", "build",
    # Collections etrangeres : leurs scripts ne sont pas des chemins de
    # production de Maths/NSI, et `**/scripts/*.py` les attrapait.
    "HLP", "HGGSP", "_SAUVEGARDES_HGGSP",
}

# Fichiers inspectes : assembleurs, classes, styles, masters, workflows CI.
TARGET_PATTERNS = [
    "**/scripts/*.py",
    "**/gabarits/*.cls",
    "**/gabarits/*.sty",
    "**/*.master.tex",
    "**/*_master.tex",
    ".github/workflows/*.yml",
]


def is_in_scope(path: Path, root: Path) -> bool:
    """True si aucun segment INTERIEUR au depot n'est hors perimetre."""
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return False
    return EXCLUDED_PARTS.isdisjoint(parts)


def check_legacy_refs_detail() -> tuple[list[str], int]:
    """Retourne les violations et le nombre de fichiers reellement analyses."""
    violations: list[str] = []
    scanned: set[Path] = set()

    for pattern in TARGET_PATTERNS:
        for file_path in ROOT.glob(pattern):
            if not file_path.is_file() or not is_in_scope(file_path, ROOT):
                continue
            if file_path in scanned:
                continue
            scanned.add(file_path)
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            for match in LEGACY_LOAD.finditer(content):
                line_no = content[: match.start()].count("\n") + 1
                violations.append(
                    f"{file_path.relative_to(ROOT)}:{line_no} — chargement d'une "
                    f"cible heritee : {match.group(0)!r}"
                )

    return violations, len(scanned)


def check_legacy_refs() -> int:
    violations, scanned = check_legacy_refs_detail()
    print(f"CHECK NO LEGACY CHARTER REFS: {scanned} fichiers analysés.")
    if not scanned:
        print(
            "ERREUR: aucun fichier analysé — un gate qui ne voit rien ne prouve rien.",
            file=sys.stderr,
        )
        return 1
    if violations:
        print(
            "ERREUR: chargement d'une charte héritée dans un chemin de production :",
            file=sys.stderr,
        )
        for v in violations:
            print(f"  ❌ {v}", file=sys.stderr)
        return 1
    print("SUCCESS: aucun chargement de charte héritée dans les chemins de production.")
    return 0


if __name__ == "__main__":
    sys.exit(check_legacy_refs())
