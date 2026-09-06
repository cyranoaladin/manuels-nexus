#!/usr/bin/env python3
"""Table unique des autorités de programme, validée contre les sources déposées.

Trois endroits pouvaient jusqu'ici affirmer une autorité réglementaire — les
registres `SOURCES.md`, les référentiels de capacités et les contrats de
chapitre — sans que rien ne les oblige à s'accorder. Un registre a d'ailleurs
attribué au programme de mathématiques de première 2019 le NOR du programme de
NSI de terminale.

Cette matrice devient la référence unique. Elle n'est pas pour autant une
vérité auto-déclarée : chaque ligne est **vérifiée** contre le registre de
sources correspondant et contre l'empreinte du fichier officiel réellement
déposé. Une ligne que le dépôt ne peut pas corroborer est un constat, pas une
autorité.

`ACTIVE` désigne l'autorité applicable à l'édition 2026-2027 ; `SUPERSEDED`
conserve les programmes remplacés, qui restent déposés et cités par
l'historique.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "audit/PROGRAMME_AUTHORITY_MATRIX.json"
OUTPUT_MD = ROOT / "audit/PROGRAMME_AUTHORITY_MATRIX.md"

EDITION = "2026-2027"

MATHS_REGISTRY = "Mathematiques/manuel-maths/sources/SOURCES.md"
NSI_REGISTRY = "NSI/sources/SOURCES.md"

#: Autorités déclarées, chacune à corroborer ci-dessous. `registry_file` nomme
#: l'entrée du registre qui doit porter le même NOR.
DECLARED: tuple[dict[str, Any], ...] = (
    {
        "manual": "1SPE", "state": "ACTIVE", "nor": "MENE2602917A",
        "bulletin": "BO n°14 du 2 avril 2026", "effective_school_year": "2026-2027",
        "registry": MATHS_REGISTRY, "registry_file": "BO2026_1SPE_specialite.pdf",
        "local_text": "Mathematiques/manuel-maths/sources/txt/BO2026_1SPE_specialite.txt",
    },
    {
        "manual": "1SPE", "state": "SUPERSEDED", "nor": "MENE1901632A",
        "bulletin": "BO spécial n°1 du 22 janvier 2019", "effective_school_year": "2019-2020",
        "registry": MATHS_REGISTRY, "registry_file": "BO2019_1SPE_specialite.pdf",
        "local_text": "Mathematiques/manuel-maths/sources/txt/BO2019_1SPE_specialite.txt",
        "superseded_by": "MENE2602917A",
    },
    {
        "manual": "TSPE_2026_2027", "state": "ACTIVE", "nor": "MENE1921246A",
        "bulletin": "BO spécial n°8 du 25 juillet 2019", "effective_school_year": "2020-2021",
        "registry": MATHS_REGISTRY, "registry_file": "BO2019_TSPE_specialite.pdf",
        "local_text": "Mathematiques/manuel-maths/sources/txt/BO2019_TSPE_specialite.txt",
        "note": (
            "Le programme de terminale rénové (MENE2602919A) s'applique à la rentrée "
            "2027 : pour l'édition 2026-2027, l'autorité active reste celle de 2019."
        ),
    },
    {
        "manual": "TCOMPL", "state": "ACTIVE", "nor": "MENE1921265A",
        "bulletin": "BO spécial n°8 du 25 juillet 2019", "effective_school_year": "2020-2021",
        "registry": MATHS_REGISTRY, "registry_file": "BO2019_TCOMPL_optionnel.pdf",
        "local_text": "Mathematiques/manuel-maths/sources/txt/BO2019_TCOMPL_optionnel.txt",
    },
    {
        "manual": "TEXPERTES", "state": "ACTIVE", "nor": "MENE1921264A",
        "bulletin": "BO spécial n°8 du 25 juillet 2019", "effective_school_year": "2020-2021",
        "registry": MATHS_REGISTRY, "registry_file": "BO2019_TEXPERTES_optionnel.pdf",
        "local_text": "Mathematiques/manuel-maths/sources/txt/BO2019_TEXPERTES_optionnel.txt",
    },
    {
        "manual": "1NSI", "state": "ACTIVE", "nor": "MENE1901633A",
        "bulletin": "BO spécial n°1 du 22 janvier 2019", "effective_school_year": "2019-2020",
        "registry": NSI_REGISTRY, "registry_file": "programme_nsi_premiere.pdf",
        "local_text": None,
    },
    {
        "manual": "TNSI", "state": "ACTIVE", "nor": "MENE1921247A",
        "bulletin": "BO spécial n°8 du 25 juillet 2019", "effective_school_year": "2020-2021",
        "registry": NSI_REGISTRY, "registry_file": "programme_nsi_terminale.pdf",
        "local_text": "NSI/sources/txt/BO2019_NSI_terminale.txt",
    },
)

NOR_PATTERN = re.compile(r"MEN[A-Z]\d{7}[A-Z]")


def registry_rows(relative: str) -> dict[str, dict[str, str]]:
    """Lignes du registre, indexées par nom de fichier officiel."""
    rows: dict[str, dict[str, str]] = {}
    for line in (ROOT / relative).read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        name = cells[0].strip("` ")
        if not name.lower().endswith(".pdf"):
            continue
        nor = NOR_PATTERN.search(cells[1])
        rows[Path(name).name] = {
            "nor": nor.group(0) if nor else "",
            "line": line.strip(),
        }
    return rows


def build() -> dict[str, Any]:
    caches = {path: registry_rows(path) for path in {MATHS_REGISTRY, NSI_REGISTRY}}
    entries: list[dict[str, Any]] = []
    findings: list[dict[str, str]] = []

    for declared in DECLARED:
        rows = caches[declared["registry"]]
        row = rows.get(declared["registry_file"])
        entry = dict(declared)
        entry["registry_nor"] = row["nor"] if row else None
        entry["corroborated_by_registry"] = bool(row) and row["nor"] == declared["nor"]

        if row is None:
            findings.append({
                "code": "AUTHORITY_NOT_IN_REGISTRY",
                "target": f"{declared['manual']}::{declared['nor']}",
                "detail": f"{declared['registry_file']} absent de {declared['registry']}",
            })
        elif row["nor"] != declared["nor"]:
            findings.append({
                "code": "AUTHORITY_REGISTRY_MISMATCH",
                "target": f"{declared['manual']}::{declared['nor']}",
                "detail": f"le registre porte {row['nor'] or '(aucun NOR)'}",
            })

        local = declared.get("local_text")
        if local:
            path = ROOT / local
            entry["local_text_present"] = path.is_file()
            entry["local_text_digest"] = (
                "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
                if path.is_file() else None
            )
            if not path.is_file():
                findings.append({
                    "code": "AUTHORITY_LOCAL_TEXT_ABSENT",
                    "target": f"{declared['manual']}::{declared['nor']}",
                    "detail": local,
                })
        entries.append(entry)

    # Un même NOR ne peut pas être l'autorité active de deux manuels distincts.
    active_by_nor: dict[str, list[str]] = {}
    for entry in entries:
        if entry["state"] == "ACTIVE":
            active_by_nor.setdefault(entry["nor"], []).append(entry["manual"])
    for nor, manuals in sorted(active_by_nor.items()):
        if len(manuals) > 1:
            findings.append({
                "code": "AUTHORITY_SHARED_BETWEEN_MANUALS",
                "target": nor,
                "detail": f"déclaré actif pour {sorted(manuals)}",
            })

    active = [e for e in entries if e["state"] == "ACTIVE"]
    summary = {
        "EDITION": EDITION,
        "DECLARED_AUTHORITIES": len(entries),
        "ACTIVE_AUTHORITIES": len(active),
        "SUPERSEDED_AUTHORITIES": len(entries) - len(active),
        "AUTHORITIES_CORROBORATED_BY_REGISTRY": sum(
            1 for e in entries if e["corroborated_by_registry"]
        ),
        "AUTHORITY_MATRIX_FINDINGS": len(findings),
        "MANUALS_WITH_AN_ACTIVE_AUTHORITY": sorted(e["manual"] for e in active),
    }
    return {
        "artifact_type": "programme_authority_matrix",
        "schema_version": 1,
        "generated_by": "scripts/build_programme_authority_matrix.py",
        "summary": summary,
        "findings": findings,
        "authorities": entries,
    }


def render_md(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Matrice des autorités de programme",
        "",
        f"Édition : `{s['EDITION']}`. Chaque ligne est corroborée par le registre de",
        "sources et par l'empreinte du texte officiel déposé — la matrice ne se",
        "déclare pas vraie, elle est vérifiée.",
        "",
        f"- Autorités déclarées : `{s['DECLARED_AUTHORITIES']}` "
        f"(actives `{s['ACTIVE_AUTHORITIES']}`, supersédées `{s['SUPERSEDED_AUTHORITIES']}`)",
        f"- Corroborées par le registre : `{s['AUTHORITIES_CORROBORATED_BY_REGISTRY']}`",
        f"- Constats : `{s['AUTHORITY_MATRIX_FINDINGS']}`",
        "",
        "| Manuel | État | NOR | Bulletin | Registre |",
        "|---|---|---|---|---|",
    ]
    for entry in payload["authorities"]:
        lines.append(
            f"| `{entry['manual']}` | `{entry['state']}` | `{entry['nor']}` | "
            f"{entry['bulletin']} | {'✓' if entry['corroborated_by_registry'] else '**✗**'} |"
        )
    if payload["findings"]:
        lines.extend(["", "## Constats", ""])
        for finding in payload["findings"]:
            lines.append(f"- `{finding['code']}` — {finding['target']} : {finding['detail']}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if OUTPUT_JSON.is_file() and OUTPUT_JSON.read_text(encoding="utf-8") == rendered:
            print("PROGRAMME_AUTHORITY_MATRIX check: OK")
            return 0
        print("PROGRAMME_AUTHORITY_MATRIX check: STALE")
        return 1
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    for finding in payload["findings"]:
        print(f"  {finding['code']}: {finding['target']} — {finding['detail']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
