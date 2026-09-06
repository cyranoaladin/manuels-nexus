#!/usr/bin/env python3
"""Identite semantique entre un enonce et son corrige.

Comparer des noms de fichiers laissait passer un corrige rattache a un autre
enonce : `CO-007` pouvait declarer repondre a `EX-001`. Le liage doit donc
porter sur ce que l'objet dit, pas sur la facon dont il est range.

Le digest d'un enonce couvre son identifiant canonique, son chapitre, sa
capacite, le texte normalise de chaque question dans l'ordre, les donnees
numeriques, le code et les figures. Le corrige derive le digest de l'enonce
qu'il declare corriger ; le gate compare les deux.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
JSON_TARGET = ROOT / "audit/EX_CO_SEMANTIC_BINDING.json"
MD_TARGET = ROOT / "audit/EX_CO_SEMANTIC_BINDING.md"
GENERATED_BY = "scripts/build_ex_co_semantic_binding.py"

EXERCICE_RE = re.compile(
    r"\\begin\{exercice\}\{([^}]*)\}(?:\{[^}]*\})*(.*?)\\end\{exercice\}", re.DOTALL
)
CORRIGE_RE = re.compile(
    r"\\begin\{corrige\}\{([^}]*)\}(.*?)\\end\{corrige\}", re.DOTALL
)
NUMBER_RE = re.compile(r"-?\d+(?:[.,]\d+)?")
CODE_RE = re.compile(
    r"\\begin\{(python|sql|console|verbatim|codereference)\}(.*?)\\end\{\1\}", re.DOTALL
)
FIGURE_RE = re.compile(r"\\begin\{(tikzpicture|axis|nxfigure)\}", re.DOTALL)
INLINE_CODE_RE = re.compile(r"\\(?:lstinline|code)\|([^|]*)\||\\(?:lstinline|code)\{([^}]*)\}")


def _strip_comments(text: str) -> str:
    return "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("%")
    )


def _questions(body: str) -> list[str]:
    """Texte de chaque question de premier niveau, dans l'ordre."""

    match = re.search(r"\\begin\{enumerate\}(.*)\\end\{enumerate\}", body, re.DOTALL)
    if not match:
        return []
    depth = 0
    current: list[str] = []
    questions: list[str] = []
    token = re.compile(r"(\\begin\{enumerate\}|\\end\{enumerate\}|\\item)")
    parts = token.split(match.group(1))
    for part in parts:
        if part == "\\begin{enumerate}":
            depth += 1
            current.append(part)
        elif part == "\\end{enumerate}":
            depth -= 1
            current.append(part)
        elif part == "\\item":
            if depth == 0:
                if current:
                    questions.append("".join(current))
                current = []
            else:
                current.append(part)
        else:
            current.append(part)
    if current:
        questions.append("".join(current))
    return [re.sub(r"\s+", " ", q).strip() for q in questions if q.strip()]


def statement_semantic_digest(path: Path, meta: dict[str, Any]) -> dict[str, Any] | None:
    """Ce que l'enonce dit, independamment de son rangement."""

    text = path.read_text(encoding="utf-8", errors="ignore")
    match = EXERCICE_RE.search(text)
    if not match:
        return None
    label, body = match.group(1), _strip_comments(match.group(2))

    questions = _questions(body)
    numbers = NUMBER_RE.findall(body)
    code_blocks = [
        re.sub(r"\s+", " ", block.strip()) for _, block in CODE_RE.findall(body)
    ]
    inline = [a or b for a, b in INLINE_CODE_RE.findall(body)]
    figures = FIGURE_RE.findall(body)

    payload = {
        "label": label,
        "chapter": meta.get("chapitre"),
        "capacities": sorted(
            str(c) for c in (meta.get("capacites_codes") or meta.get("capacites") or [])
        ),
        "question_count": len(questions),
        "questions": questions,
        "numbers": numbers,
        "code": code_blocks,
        "inline_code": inline,
        "figures": figures,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()
    return {"label": label, "digest": digest, "question_count": len(questions),
            "numbers": len(numbers), "code_blocks": len(code_blocks),
            "figures": len(figures)}


def _meta(path: Path) -> dict[str, Any]:
    head = path.read_text(encoding="utf-8", errors="ignore").split("\n", 1)[0]
    if not head.startswith("% META:"):
        return {}
    try:
        return json.loads(head[len("% META:"):].strip())
    except json.JSONDecodeError:
        return {}


def build(root: Path, subdirs: tuple[str, ...] = ("NSI/chapitres",)) -> dict[str, Any]:
    statements: dict[str, dict[str, Any]] = {}
    statement_paths: dict[str, str] = {}
    # Une remediation porte elle aussi un enonce corrigeable : la restreindre au
    # repertoire `exercices/` laissait seize corriges sans cible resolvable.
    statement_globs = ("exercices/*.tex", "remediation/*.tex", "evaluations/*.tex")
    for subdir in subdirs:
        for glob in statement_globs:
          for path in sorted((root / subdir).rglob(glob)):
            if "_harvest" in path.parts:
                continue
            entry = statement_semantic_digest(path, _meta(path))
            if entry is None:
                continue
            statements[entry["label"]] = entry
            statement_paths[entry["label"]] = path.relative_to(root).as_posix()

    bindings: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    drift: list[dict[str, Any]] = []
    for subdir in subdirs:
        for path in sorted((root / subdir).rglob("corriges/*.tex")):
            if "_harvest" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            match = CORRIGE_RE.search(text)
            if not match:
                continue
            declared = match.group(1)
            relative = path.relative_to(root).as_posix()
            statement = statements.get(declared)
            if statement is None:
                # Un corrige peut viser une remediation ou une evaluation : ce
                # n'est une anomalie que si la cible n'existe nulle part.
                unresolved.append({
                    "correction": relative,
                    "declared_target": declared,
                    "why": "cible declaree absente des enonces",
                })
                continue
            # Le corrige derive le digest de l'enonce qu'il declare corriger.
            bindings.append({
                "correction": relative,
                "declared_target": declared,
                "statement": statement_paths[declared],
                "corrects_statement_digest": statement["digest"],
                "statement_semantic_digest": statement["digest"],
            })
            paired = relative.replace("/corriges/", "/exercices/").replace("-CO-", "-EX-")
            if paired in statement_paths.values() and statement_paths[declared] != paired:
                drift.append({
                    "correction": relative,
                    "declared_target": declared,
                    "paired_statement": paired,
                    "why": "le corrige declare un enonce different de celui qui lui est apparie",
                })

    return {
        "artifact_type": "ex_co_semantic_binding",
        "schema_version": "1.0.0",
        "generated_by": GENERATED_BY,
        "digest_covers": [
            "identifiant canonique", "chapitre", "capacite",
            "nombre et texte normalise des questions, dans l'ordre",
            "donnees numeriques", "code", "figures",
        ],
        "bindings": bindings,
        "unresolved_targets": unresolved,
        "statement_drift": drift,
        "summary": {
            "STATEMENTS_DIGESTED": len(statements),
            "CORRECTIONS_BOUND": len(bindings),
            "UNRESOLVED_CORRECTION_TARGETS": len(unresolved),
            "STUDENT_TEACHER_STATEMENT_DRIFT": len(drift),
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
    lines = ["# Liage semantique enonce / corrige", ""]
    for key, value in report["summary"].items():
        lines.append(f"- **{key}** : `{value}`")
    MD_TARGET.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
