#!/usr/bin/env python3
"""Analyse differentielle complete du commit de remplissage `533d1919`.

Un detecteur de clones voit les copies. Il ne voit pas un objet authentique
dont le corps a ete remplace par un contenu different : rien ne se duplique,
et pourtant du contenu a disparu. C'est cet angle mort que ce module ferme.

Chaque objet pedagogique touche par le commit recoit exactement une
classification, et tout ecrasement authentique est confronte a l'etat courant
pour dire s'il a ete recupere depuis.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
JSON_TARGET = ROOT / "audit/FILLER_COMMIT_FORENSICS.json"
MD_TARGET = ROOT / "audit/FILLER_COMMIT_FORENSICS.md"
GENERATED_BY = "scripts/build_filler_commit_forensics.py"

FILLER_COMMIT = "533d19198eb7810699a41a7b5275744691420859"
PEDAGOGICAL = re.compile(r"(^|/)chapitres/[^/]+/[^/]+/.*\.tex$")
MIN_BODY_CHARS = 80

MACRO = re.compile(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?")
BRACES = re.compile(r"[{}]")
WS = re.compile(r"\s+")


def _git(args: list[str], root: Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    ).stdout


def _body(text: str) -> str:
    return "\n".join(line for line in text.splitlines()[1:] if line.strip())


def _payload(text: str) -> str:
    """Le texte que l'eleve lit, debarrasse de l'habillage de charte.

    Deux versions qui ne different que par des macros de mise en forme ont le
    meme payload : le changement est alors de charte, pas de contenu.
    """

    stripped = "\n".join(
        line for line in text.splitlines()[1:] if not line.lstrip().startswith("%")
    )
    stripped = MACRO.sub(" ", stripped)
    stripped = BRACES.sub(" ", stripped)
    return WS.sub(" ", stripped).strip()


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def build(root: Path) -> dict[str, Any]:
    status = _git(["diff", "--name-status", f"{FILLER_COMMIT}^", FILLER_COMMIT], root)
    touched: list[tuple[str, str]] = []
    for line in status.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        code, path = parts[0], parts[-1]
        if PEDAGOGICAL.search(path):
            touched.append((code, path))

    # Corps presents AVANT le commit, pour reconnaitre une copie.
    before_bodies: dict[str, str] = {}
    for line in _git(
        ["ls-tree", "-r", f"{FILLER_COMMIT}^", "--", "NSI", "Mathematiques"], root
    ).splitlines():
        parts = line.split(maxsplit=3)
        if len(parts) < 4 or parts[1] != "blob":
            continue
        path = parts[3].strip()
        if not PEDAGOGICAL.search(path):
            continue
        content = _git(["cat-file", "-p", parts[2]], root)
        body = _body(content)
        if len(body) >= MIN_BODY_CHARS:
            before_bodies.setdefault(_digest(body), path)

    records: list[dict[str, Any]] = []
    for code, path in touched:
        after = _git(["show", f"{FILLER_COMMIT}:{path}"], root)
        before = (
            "" if code.startswith("A")
            else _git(["show", f"{FILLER_COMMIT}^:{path}"], root)
        )
        after_body, before_body = _body(after), _body(before)
        after_payload, before_payload = _payload(after), _payload(before)

        if code.startswith("A"):
            if len(after_body) < MIN_BODY_CHARS:
                verdict = "FORMAT_ONLY"
                why = "objet cree vide ou quasi vide"
            elif _digest(after_body) in before_bodies:
                verdict = "FILLER_CREATION"
                why = f"cree en recopiant {before_bodies[_digest(after_body)]}"
            else:
                verdict = "OTHER_SUBSTANTIVE_CHANGE"
                why = "objet cree avec un contenu inedit"
        elif code.startswith("D"):
            verdict = "OTHER_SUBSTANTIVE_CHANGE"
            why = "objet supprime par le commit"
        elif before_body == after_body:
            verdict = "METADATA_ONLY"
            why = "seule la ligne d'identite change"
        elif before_payload == after_payload:
            verdict = "LEGITIMATE_CHARTE_ONLY"
            why = "meme texte lu par l'eleve, habillage de charte different"
        elif len(before_payload) >= MIN_BODY_CHARS and _digest(after_body) in before_bodies:
            verdict = "AUTHENTIC_CONTENT_OVERWRITE"
            why = (
                "un objet qui portait deja un contenu propre a ete remplace par la "
                f"copie de {before_bodies[_digest(after_body)]}"
            )
        elif len(before_payload) < MIN_BODY_CHARS:
            verdict = "FILLER_CREATION"
            why = "objet auparavant vide, rempli par ce commit"
        else:
            verdict = "OTHER_SUBSTANTIVE_CHANGE"
            why = "contenu substantiel modifie sans recopie identifiee"

        # `OTHER_SUBSTANTIVE_CHANGE` ne doit pas etre un seau opaque : on dit
        # de quoi il est fait, et surtout si du contenu a pu se perdre.
        subclass = None
        if verdict == "OTHER_SUBSTANTIVE_CHANGE":
            if code.startswith("A"):
                subclass = "NEW_AUTHORED_CONTENT"
            elif "genere_depuis" in after.split("\n", 1)[0]:
                subclass = "REGENERATED_FROM_DECLARED_SOURCE"
            elif len(after_payload) > len(before_payload):
                subclass = "CONTENT_ENRICHED"
            else:
                subclass = "CONTENT_REDUCED"

        record = {
            "path": path,
            "change": code,
            "verdict": verdict,
            "subclass": subclass,
            "why": why,
            "before_payload_chars": len(before_payload),
            "after_payload_chars": len(after_payload),
        }
        if verdict == "AUTHENTIC_CONTENT_OVERWRITE":
            current = (root / path)
            current_body = _body(current.read_text(encoding="utf-8", errors="ignore")) if current.is_file() else None
            record["recovered"] = (
                current_body is None  # objet retire depuis : la copie ne subsiste pas
                or _digest(current_body) == _digest(before_body)
            )
            record["still_present"] = current.is_file()
            record["overwritten_payload_preview"] = before_payload[:160]
        records.append(record)

    by_verdict = collections.Counter(r["verdict"] for r in records)
    overwrites = [r for r in records if r["verdict"] == "AUTHENTIC_CONTENT_OVERWRITE"]
    unrecovered = [r for r in overwrites if not r.get("recovered")]

    return {
        "artifact_type": "filler_commit_forensics",
        "schema_version": "1.0.0",
        "generated_by": GENERATED_BY,
        "commit": FILLER_COMMIT,
        "records": records,
        "authentic_overwrites": overwrites,
        "unrecovered_overwrites": unrecovered,
        "summary": {
            "PEDAGOGICAL_MUTATIONS": len(records),
            "FILLER_CREATION": by_verdict["FILLER_CREATION"],
            "AUTHENTIC_CONTENT_OVERWRITE": by_verdict["AUTHENTIC_CONTENT_OVERWRITE"],
            "LEGITIMATE_CHARTE_ONLY": by_verdict["LEGITIMATE_CHARTE_ONLY"],
            "METADATA_ONLY": by_verdict["METADATA_ONLY"],
            "FORMAT_ONLY": by_verdict["FORMAT_ONLY"],
            "OTHER_SUBSTANTIVE_CHANGE": by_verdict["OTHER_SUBSTANTIVE_CHANGE"],
            "UNCLASSIFIED_CONTENT_MUTATIONS": len(records) - sum(by_verdict.values()),
            "UNRECOVERED_AUTHENTIC_OVERWRITES": len(unrecovered),
            "OTHER_SUBSTANTIVE_SUBCLASSES": dict(
                collections.Counter(
                    r["subclass"] for r in records if r.get("subclass")
                )
            ),
            "CONTENT_REDUCED": sum(
                1 for r in records if r.get("subclass") == "CONTENT_REDUCED"
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = build(args.root)
    JSON_TARGET.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [f"# Forensique du commit {FILLER_COMMIT[:12]}", ""]
    for key, value in report["summary"].items():
        lines.append(f"- **{key}** : `{value}`")
    MD_TARGET.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
