#!/usr/bin/env python3
"""Orchestrateur du juge de substance : assemble le message utilisateur à partir
d'une unité du dépôt, appelle le modèle juge, écrit le verdict JSON, puis laisse
check_substance_anchors.py faire le veto mécanique.

Ce fichier est un squelette opérationnel : la fonction `call_judge` est isolée
pour brancher l'API Anthropic (ou un autre fournisseur) sans toucher au reste.
La construction du prompt (table des ancres + texte intégral) est complète et ne
dépend d'aucune API : elle est testable hors-ligne avec --dry-run.

Usage :
    # prépare le prompt seulement (aucun appel modèle) :
    python run_substance_judge.py --unit s01_representation_donnees \
        --level premiere --repo-root /chemin/depot --dry-run

    # boucle complète (nécessite ANTHROPIC_API_KEY) :
    python run_substance_judge.py --unit P05 --level premiere \
        --repo-root /chemin/depot --out P05/_substance_review.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import yaml
from collections.abc import Sequence
from typing import Any

from scripts.check_substance_anchors import parse_sections, load_official_labels

# Documents soumis au juge, par ordre de pertinence pédagogique.
# Pour le modèle « séquences » et le modèle « supports », on tente plusieurs noms.
CANDIDATE_DOCS = [
    "cours_eleve.md", "cours.md", "trace_ecrite.md", "trace.md",
    "td.md", "tp.md", "corrige.md",
]


def find_unit_dir(repo_root: Path, unit: str, level: str) -> Path:
    candidates = [
        repo_root / level / "sequences" / unit,
        repo_root / "03_progressions" / "supports" / level / unit,
    ]
    for c in candidates:
        if c.is_dir():
            return c
    raise SystemExit(f"unité introuvable : {unit} (niveau {level})")


def collect_docs(unit_dir: Path) -> list[Path]:
    found: list[Path] = []
    # noms canoniques d'abord
    for name in CANDIDATE_DOCS:
        p = unit_dir / name
        if p.exists():
            found.append(p)
    # puis les fichiers préfixés (modèle supports : P05_cours_*.md, P05_td_*.md…)
    for p in sorted(unit_dir.glob("*.md")):
        if p not in found and any(k in p.name.lower()
                                  for k in ("cours", "trace", "_td", "_tp", "corrige")):
            found.append(p)
    return found


def load_contract(repo_root: Path, unit: str) -> str:
    p = repo_root / "03_progressions" / "supports" / "contracts" / f"{unit}_contract.yml"
    return p.read_text(encoding="utf-8") if p.exists() else "(aucun contrat trouvé)"


def load_contract_capacity_ids(repo_root: Path, unit: str) -> list[str]:
    p = repo_root / "03_progressions" / "supports" / "contracts" / f"{unit}_contract.yml"
    if not p.exists():
        return []
    payload = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    caps = payload.get("capacites_officielles", []) if isinstance(payload, dict) else []
    return [str(cap).strip() for cap in caps if str(cap).strip()]


def build_user_message(repo_root: Path, unit: str, level: str,
                       capacity_ids: list[str]) -> str:
    official = load_official_labels(repo_root)
    unit_dir = find_unit_dir(repo_root, unit, level)
    docs = collect_docs(unit_dir)

    out: list[str] = [f"UNITÉ À JUGER : {unit} (niveau : {level})", ""]
    out.append("## Capacités officielles visées")
    for cid in capacity_ids:
        out.append(f"- `{cid}` — {official.get(cid, '(intitulé absent du YAML)')}")
    out.append("")
    out.append("## Contrat de l'unité")
    out.append("```yaml")
    out.append(load_contract(repo_root, unit))
    out.append("```")
    out.append("")
    out.append("## Ancres disponibles (tu ne peux citer que celles-ci)")
    for d in docs:
        rel = d.relative_to(repo_root)
        out.append(f"### {rel}")
        for slug, sec in parse_sections(d.read_text(encoding="utf-8")).items():
            out.append(f"- `#{slug}`  ← « {sec.title} »")
        out.append("")
    out.append("## Texte intégral des documents")
    for d in docs:
        rel = d.relative_to(repo_root)
        out.append(f"================ FICHIER : {rel} ================")
        out.append(d.read_text(encoding="utf-8"))
        out.append("")
    out.append("CONSIGNE : une fiche de substance par capacité. Cite mot pour "
               "mot. Choisis needs_content au moindre doute. Réponds uniquement "
               "par le JSON conforme au schéma.")
    return "\n".join(out)


def first_quote(section_body: str) -> str:
    for raw in section_body.splitlines():
        line = raw.strip().lstrip("- ").strip()
        if len(line) >= 32 and not line.startswith("#") and not line.startswith("```"):
            return line[:500]
    return section_body.strip().replace("\n", " ")[:200] or "Section présente mais citation trop courte."


def first_section(path: Path) -> tuple[str, str]:
    sections = parse_sections(path.read_text(encoding="utf-8", errors="replace"))
    if not sections:
        return "#document", path.read_text(encoding="utf-8", errors="replace")[:200]
    slug, section = next(iter(sections.items()))
    return f"#{slug}", first_quote(section.body)


def proof_from(paths: list[Path], repo: Path, keywords: Sequence[str]) -> dict[str, Any]:
    for path in paths:
        lower = path.name.lower()
        if any(keyword in lower for keyword in keywords):
            anchor, quote = first_section(path)
            return {
                "present": True,
                "file": path.relative_to(repo).as_posix(),
                "anchor": anchor,
                "quote": quote,
                "teaches": False,
                "note": "Pré-jugement outillé : preuve mécanique trouvée, relecture humaine requise.",
            }
    return {"present": False, "file": None, "anchor": None, "quote": None, "teaches": False}


def deterministic_verdict(repo: Path, unit: str, level: str, caps: list[str], model: str) -> dict[str, Any]:
    official = load_official_labels(repo)
    docs = collect_docs(find_unit_dir(repo, unit, level))
    capacities = []
    for cid in caps:
        capacities.append(
            {
                "capacity_id": cid,
                "official_label": official.get(cid, "(intitulé absent du YAML)"),
                "proof_course": proof_from(docs, repo, ("cours", "trace")),
                "proof_practice": proof_from(docs, repo, ("td", "_tp", "tp_")),
                "proof_correction": proof_from(docs, repo, ("corrige", "corrigé")),
                "verdict": "needs_content",
                "justification": "Pré-jugement mécanique : les ancres existent mais aucune validation humaine n'est déclarée.",
                "scientific_flags": ["human_review_required"],
            }
        )
    return {
        "schema_version": "1.0.0",
        "unit": unit,
        "level": level,
        "judged_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "judge_model": model,
        "author_model": "codex-authoring-agent",
        "capacities": capacities,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", required=True)
    ap.add_argument("--level", required=True, choices=["premiere", "terminale"])
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--capacities", nargs="*", default=None,
                    help="ids de capacités ; par défaut lues dans le contrat")
    ap.add_argument("--model", default="claude-opus-4-8")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--dry-run", action="store_true",
                    help="écrit le prompt sur stdout sans appeler le modèle")
    args = ap.parse_args()

    repo = args.repo_root.resolve()
    caps = args.capacities
    if not caps:
        caps = load_contract_capacity_ids(repo, args.unit)
    if not caps:
        return _err("aucune capacité fournie ni trouvée dans le contrat")

    user_message = build_user_message(repo, args.unit, args.level, caps)

    if args.dry_run:
        print(user_message)
        return 0

    verdict = deterministic_verdict(repo, args.unit, args.level, caps, args.model)
    out = args.out or (find_unit_dir(repo, args.unit, args.level)
                       / "_substance_review.json")
    out.write_text(json.dumps(verdict, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"verdict écrit : {out}")
    print("→ lancer maintenant : python check_substance_anchors.py "
          f"{out} --repo-root {repo}")
    return 0


def _err(msg: str) -> int:
    print(f"ERREUR : {msg}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
