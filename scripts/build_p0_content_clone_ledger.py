#!/usr/bin/env python3
"""Registre canonique du P0 de clonage pedagogique.

P0_PEDAGOGICAL_CONTENT_CLONING_AND_CAPACITY_MISREPRESENTATION.

Des centaines d'objets pedagogiques partagent un corps rigoureusement
identique tout en declarant des capacites differentes. Le cas le plus net :
dix-sept fiches de remediation de TSPE-GEOMETRIE-ESPACE declarees C1 a C16
portent toutes le meme corps, dont l'en-tete annonce « FICHE DE REMEDIATION
-- C7 : produit scalaire ». Un eleve en echec sur C1 recevait la fiche C7.

Ce producteur mesure le defaut ; il ne le corrige pas.

DEFINITION DU CORPS PEDAGOGIQUE. Seule la ligne d'identite `% META:` est
retiree, plus les blancs de fin de ligne et les blancs de bord. Rien d'autre :
enonce, mathematiques, code, methode, solution, diagnostic, remediation,
consigne et bloc de verification appartiennent tous au corps. Deux objets dont
seul le META differe sont donc detectes.

PERIMETRE. Tout `.tex` sous `chapitres/`, hors `_harvest/` qui est declare non
publie par la politique diacritiques et ne rejoint aucun assemblage.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORPORA = (
    ROOT / "Mathematiques/manuel-maths/chapitres",
    ROOT / "NSI/chapitres",
)
UNPUBLISHED = ("_harvest",)
OUTPUT_JSON = ROOT / "audit/P0_CONTENT_CLONE_LEDGER.json"
OUTPUT_MD = ROOT / "audit/P0_CONTENT_CLONE_LEDGER.md"

MANUAL_PREFIXES = (
    ("1SPE-", "1SPE"),
    ("TSPE-", "TSPE"),
    ("TCOMPL-", "TCOMPL"),
    ("TEXP-", "TEXPERTES"),
    ("1NSI-", "1NSI"),
    ("TNSI-", "TNSI"),
)

META_LINE = re.compile(r"^\s*%\s*META:")

#: Un corps dont il ne reste rien une fois les lignes purement structurelles
#: retirees est un gabarit, pas du contenu clone : il ne fonde aucun P0.
STRUCTURAL = re.compile(
    r"^\s*(?:%|\\(?:begin|end|section|subsection|input|include|clearpage"
    r"|newpage|vspace|hspace|noindent|par)\b|\s*$)"
)
BOILERPLATE_PAYLOAD_LIMIT = 120

#: Le corps s'auto-designe : en-tete « FICHE DE REMEDIATION -- C7 »,
#: identifiants internes « ...-RE-C7-EX1 ». Quand le corps nomme une capacite,
#: c'est une preuve directe de ce qu'il traite, independante du META.
BODY_CAPACITY = re.compile(r"\b(?:RE-)?C0*(\d{1,2})[A-Z]?\b")


def manual_of(chapter: str) -> str:
    for prefix, manual in MANUAL_PREFIXES:
        if chapter.startswith(prefix):
            return manual
    return "UNKNOWN"


def pedagogical_body(text: str) -> str:
    return "\n".join(
        line.rstrip() for line in text.splitlines() if not META_LINE.match(line)
    ).strip()


def payload_only(body: str) -> str:
    return "\n".join(
        line for line in body.splitlines() if not STRUCTURAL.match(line)
    ).strip()


def _strip_accents(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value)
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def normalized_body(body: str) -> str:
    """Projection quasi-clone : casse, diacritiques, espaces."""

    return " ".join(_strip_accents(body).lower().split())


def digest(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_meta(text: str) -> dict[str, Any]:
    if "META:" not in text:
        return {}
    raw = text.split("META:", 1)[1].splitlines()[0].strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def declared_capacities(meta: dict[str, Any]) -> tuple[str, ...]:
    values = meta.get("capacites_codes") or meta.get("capacites") or []
    codes = set()
    for value in values:
        code = str(value).strip()
        codes.add(code.rsplit("-", 1)[-1] if "-" in code else code)
    return tuple(sorted(codes))


def body_attested_capacities(body: str) -> tuple[str, ...]:
    return tuple(sorted({f"C{int(m)}" for m in BODY_CAPACITY.findall(body)}))


def scan() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for corpus in CORPORA:
        if not corpus.is_dir():
            continue
        for path in sorted(corpus.rglob("*.tex")):
            if any(part in UNPUBLISHED for part in path.parts):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            body = pedagogical_body(text)
            meta = read_meta(text)
            index = path.parts.index("chapitres") + 1
            chapter = path.parts[index]
            records.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "object_id": meta.get("id"),
                    "chapter": chapter,
                    "manual": manual_of(chapter),
                    "source_type": path.parts[index + 1],
                    "status": meta.get("status"),
                    "declared_capacity": list(declared_capacities(meta)),
                    "body_attested_capacity": list(body_attested_capacities(body)),
                    "exact_body_digest": digest(body),
                    "normalized_body_digest": digest(normalized_body(body)),
                    "payload_chars": len(payload_only(body)),
                }
            )
    return records


def disposition_of(members: list[dict[str, Any]]) -> str:
    """Chaque groupe recoit exactement une disposition."""

    if max(row["payload_chars"] for row in members) < BOILERPLATE_PAYLOAD_LIMIT:
        return "BOILERPLATE_ONLY"
    if len({row["manual"] for row in members}) > 1:
        return "CROSS_MANUAL_CONTAMINATION"
    if len({row["chapter"] for row in members}) > 1:
        return "CROSS_CHAPTER_CONTAMINATION"
    if len({tuple(row["declared_capacity"]) for row in members}) > 1:
        return "CAPACITY_MISREPRESENTING_CLONE"
    return "REDUNDANT_SAME_CAPACITY"


def build_ledger() -> dict[str, Any]:
    records = scan()
    by_body: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in records:
        by_body[row["exact_body_digest"]].append(row)

    groups = []
    for index, (body_digest, members) in enumerate(
        sorted((k, v) for k, v in by_body.items() if len(v) > 1)
    ):
        members = sorted(members, key=lambda row: row["path"])
        disposition = disposition_of(members)
        # Le membre dont le CORPS atteste sa propre capacite garde le credit ;
        # les autres le revendiquent sans le servir.
        aligned = [
            row
            for row in members
            if row["body_attested_capacity"]
            and set(row["declared_capacity"]) & set(row["body_attested_capacity"])
        ]
        groups.append(
            {
                "clone_group_id": f"CG-{index + 1:04d}",
                "canonical_body_digest": body_digest,
                "normalized_body_digest": members[0]["normalized_body_digest"],
                "object_count": len(members),
                "excess_object_count": len(members) - 1,
                "disposition": disposition,
                "same_capacity": len(
                    {tuple(r["declared_capacity"]) for r in members}
                )
                == 1,
                "same_chapter": len({r["chapter"] for r in members}) == 1,
                "same_manual": len({r["manual"] for r in members}) == 1,
                "body_aligned_member_paths": [row["path"] for row in aligned],
                "members": members,
            }
        )

    invalid_credit = set()
    for group in groups:
        if group["disposition"] in {"BOILERPLATE_ONLY", "REDUNDANT_SAME_CAPACITY"}:
            continue
        # Un corps clone credite UNE capacite, pas n. Le membre dont le corps
        # atteste sa propre capacite garde le credit ; a defaut d'auto-mention
        # -- un enonce ne se nomme pas toujours -- le premier par chemin fait
        # foi. Ne rien garder invaliderait l'original avec ses copies et
        # fabriquerait des lacunes : le chapitre paraitrait depourvu d'un
        # contenu qu'il possede reellement.
        aligned = group["body_aligned_member_paths"]
        keep = {aligned[0] if aligned else group["members"][0]["path"]}
        for row in group["members"]:
            if row["path"] not in keep:
                invalid_credit.add(row["path"])
    for row in records:
        declared, attested = set(row["declared_capacity"]), set(
            row["body_attested_capacity"]
        )
        if declared and attested and not (declared & attested):
            invalid_credit.add(row["path"])

    per_manual: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    per_chapter: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    for group in groups:
        for row in group["members"][1:]:
            per_manual[row["manual"]][group["disposition"]] += 1
            per_manual[row["manual"]]["TOTAL"] += 1
            per_chapter[row["chapter"]][group["disposition"]] += 1
            per_chapter[row["chapter"]]["TOTAL"] += 1

    dispositions = collections.Counter(g["disposition"] for g in groups)
    excess = collections.Counter()
    for group in groups:
        excess[group["disposition"]] += group["excess_object_count"]

    return {
        "artifact_type": "p0_content_clone_ledger",
        "schema_version": 1,
        "generated_by": "scripts/build_p0_content_clone_ledger.py",
        "finding": "P0_PEDAGOGICAL_CONTENT_CLONING_AND_CAPACITY_MISREPRESENTATION",
        "publication_blocker": True,
        "body_definition": {
            "excluded": ["% META: identity line", "trailing and edge whitespace"],
            "retained": [
                "enonce",
                "mathematiques",
                "code",
                "methode",
                "solution",
                "diagnostic",
                "remediation",
                "consigne",
                "verify block",
            ],
            "unpublished_directories_excluded": list(UNPUBLISHED),
        },
        "inventory": {
            "objects_scanned": len(records),
            "distinct_bodies": len(by_body),
            "clone_groups": len(groups),
            "excess_objects": sum(g["excess_object_count"] for g in groups),
            "objects_on_invalid_credit": len(invalid_credit),
        },
        "dispositions": {
            name: {"groups": dispositions[name], "excess_objects": excess[name]}
            for name in sorted(dispositions)
        },
        "unknown": 0,
        "per_manual": {k: dict(v) for k, v in sorted(per_manual.items())},
        "per_chapter": {
            k: dict(v)
            for k, v in sorted(
                per_chapter.items(), key=lambda kv: (-kv[1]["TOTAL"], kv[0])
            )
        },
        "objects_on_invalid_credit": sorted(invalid_credit),
        "groups": groups,
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_md(payload: dict[str, Any]) -> str:
    inventory = payload["inventory"]
    lines = [
        "# P0 — clonage pédagogique et fausse déclaration de capacité",
        "",
        "Des objets pédagogiques partagent un corps rigoureusement identique tout",
        "en déclarant des capacités différentes. Le cas le plus net : dix-sept",
        "fiches de remédiation de `TSPE-GEOMETRIE-ESPACE`, déclarées `C1` à `C16`,",
        "portent le même corps, dont l'en-tête annonce « FICHE DE REMEDIATION —",
        "C7 : produit scalaire ». Un élève en échec sur `C1` recevait la fiche `C7`.",
        "",
        "## Mesure",
        "",
        f"- objets analysés : `{inventory['objects_scanned']}`",
        f"- groupes de corps identiques : `{inventory['clone_groups']}`",
        f"- objets excédentaires : `{inventory['excess_objects']}`",
        f"- objets à crédit invalide : `{inventory['objects_on_invalid_credit']}`",
        f"- UNKNOWN : `{payload['unknown']}`",
        "",
        "## Dispositions",
        "",
        "| Disposition | Groupes | Objets excédentaires |",
        "|---|---:|---:|",
    ]
    for name, values in payload["dispositions"].items():
        lines.append(
            f"| `{name}` | {values['groups']} | {values['excess_objects']} |"
        )
    lines += ["", "## Par manuel", "", "| Manuel | Objets excédentaires |", "|---|---:|"]
    for manual, counts in payload["per_manual"].items():
        lines.append(f"| `{manual}` | {counts.get('TOTAL', 0)} |")
    lines += [
        "",
        "Le corps pédagogique est le fichier moins sa seule ligne d'identité",
        "`% META:`. Énoncé, mathématiques, code, méthode, solution, diagnostic,",
        "remédiation, consigne et bloc de vérification en font partie : deux objets",
        "dont seul le META diffère sont donc détectés.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="comparer sans écrire ; sortie non nulle si un artefact a dérivé",
    )
    arguments = parser.parse_args(argv)

    payload = build_ledger()
    targets = ((OUTPUT_JSON, render_json(payload)), (OUTPUT_MD, render_md(payload)))
    stale = []
    for path, rendered in targets:
        if arguments.check:
            current = path.read_text(encoding="utf-8") if path.is_file() else ""
            if current != rendered:
                stale.append(str(path.relative_to(ROOT)))
            continue
        path.write_text(rendered, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    for name in stale:
        print(f"STALE: {name}")
    return 1 if stale else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
