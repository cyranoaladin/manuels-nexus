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
import importlib.util
import json
import re
import sys
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


_RESOLVER = None


def _resolver():
    """Table d'identite des capacites, chargee une fois."""

    global _RESOLVER
    if _RESOLVER is None:
        spec = importlib.util.spec_from_file_location(
            "capacity_identity", ROOT / "scripts/capacity_identity.py"
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        _RESOLVER = (module, module.CapacityIdentityResolver.from_corpora())
    return _RESOLVER


def declared_capacities(meta: dict[str, Any]) -> tuple[str, ...]:
    """Codes locaux credites, resolus dans la portee du chapitre.

    Cette fonction coupait autrefois la chaine a son dernier tiret :
    `TSPE-CONCLGN-C1` devenait `C1`, et le credit d'une capacite passait a sa
    voisine. La resolution est desormais une egalite exacte, portee par le
    contrat du chapitre.
    """

    values = meta.get("capacites_codes") or meta.get("capacites") or []
    identity, resolver = _resolver()
    chapter = str(meta.get("chapitre") or "").strip()
    raws = [identity.normalise(value) for value in values]
    raws = [value for value in raws if value]
    if chapter in resolver.chapters:
        return tuple(sorted(set(resolver.resolve_codes(chapter, raws))))
    # Hors contrat connu, la chaine est conservee TELLE QUELLE : la reduire a
    # un jeton reintroduirait exactement le defaut repare ici.
    return tuple(sorted(set(raws)))


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


CANONICAL_STATUSES = (
    "SEMANTIC_CANONICAL",
    "LEGITIMATE_SHARED_CANONICAL",
    "AMBIGUOUS",
    "UNKNOWN",
)


def select_canonical(group: dict[str, Any]) -> dict[str, Any]:
    """Le proprietaire semantique d'un corps, etabli par PREUVE.

    Cette selection retenait autrefois `members[0]` -- le premier chemin par
    ordre alphabetique -- quand aucun corps ne s'attestait lui-meme. Le
    resultat etait alors juste par chance : dans le groupe des cours 1NSI, le
    fichier authentique se trouvait s'appeler `1NSI-ADGK-...`, donc trier
    avant ses copies `1NSI-ALGO-PARCOURS-TRIS-...`. Renommer un fichier
    aurait deplace l'authenticite. L'identite canonique ne peut pas dependre
    de l'ordre du systeme de fichiers.

    Les preuves sont examinees dans cet ordre, et chacune ne conclut que si
    elle designe un proprietaire UNIQUE :

    `BODY_SELF_ATTESTATION`
        Le corps nomme lui-meme la capacite qu'un seul de ses porteurs
        declare. C'est la preuve la plus forte : le contenu temoigne.

    `CHAPTER_SELF_DUPLICATION`
        Un chapitre qui detient le meme corps sous plusieurs capacites
        distinctes le represente faussement, quelle que soit son anciennete.
        Si un seul autre chapitre le detient sous une capacite unique, c'est
        lui le proprietaire.

    `IDENTICAL_CAPACITY_CREDIT`
        Tous les porteurs creditent la meme capacite. Le choix d'un canonique
        n'a alors aucun effet sur le credit : la duplication est physique, pas
        semantique.

    `NO_CAPACITY_AT_STAKE`
        Le corps est du gabarit sans contenu pedagogique.

    Sans preuve concluante, le statut est `AMBIGUOUS` et le groupe part en
    revue humaine. On ne tranche pas.
    """

    members = group["members"]
    paths = sorted(row["path"] for row in members)

    if group["disposition"] == "BOILERPLATE_ONLY":
        return {
            "status": "LEGITIMATE_SHARED_CANONICAL",
            "evidence_rule": "NO_CAPACITY_AT_STAKE",
            "canonical_paths": paths,
            "false_copy_paths": [],
            "reason": "gabarit sans contenu pedagogique : aucun credit en jeu",
        }

    # 1. Le corps temoigne pour lui-meme.
    aligned = sorted(
        row["path"]
        for row in members
        if row["body_attested_capacity"]
        and set(row["declared_capacity"]) & set(row["body_attested_capacity"])
    )
    if aligned:
        attested = {
            tuple(sorted(set(row["declared_capacity"]) & set(row["body_attested_capacity"])))
            for row in members
            if row["path"] in set(aligned)
        }
        if len(attested) == 1:
            return {
                "status": "SEMANTIC_CANONICAL",
                "evidence_rule": "BODY_SELF_ATTESTATION",
                "canonical_paths": aligned,
                "false_copy_paths": [p for p in paths if p not in set(aligned)],
                "reason": (
                    "le corps nomme la capacite que ces porteurs declarent ; "
                    "les autres la revendiquent sans la servir"
                ),
            }
        return {
            "status": "AMBIGUOUS",
            "evidence_rule": "BODY_SELF_ATTESTATION",
            "canonical_paths": [],
            "false_copy_paths": [],
            "reason": (
                "plusieurs porteurs sont attestes par le corps pour des "
                "capacites differentes : le corps ne designe pas un proprietaire"
            ),
        }

    # 2. Un chapitre qui se duplique lui-meme represente faussement.
    by_chapter: dict[str, set[str]] = collections.defaultdict(set)
    for row in members:
        by_chapter[row["chapter"]].update(row["declared_capacity"])
    duplicating = {c for c, caps in by_chapter.items() if len(caps) > 1}
    single = sorted(set(by_chapter) - duplicating)
    if duplicating and len(single) == 1:
        owner = single[0]
        canonical = sorted(row["path"] for row in members if row["chapter"] == owner)
        return {
            "status": "SEMANTIC_CANONICAL",
            "evidence_rule": "CHAPTER_SELF_DUPLICATION",
            "canonical_paths": canonical,
            "false_copy_paths": [p for p in paths if p not in set(canonical)],
            "reason": (
                f"{sorted(duplicating)} detiennent ce corps sous plusieurs "
                f"capacites distinctes et le representent faussement ; "
                f"{owner} le detient sous une capacite unique"
            ),
        }

    # 3. Tous creditent la meme capacite : le canonique est sans effet.
    #
    # La comparaison porte sur l'identite PLEINEMENT QUALIFIEE, pas sur le
    # code local. `C1` de TSPE-DERIVATION-CONVEXITE et `C1` de
    # 1NSI-ALGO-PARCOURS-TRIS ne sont pas la meme capacite -- c'est le
    # principe meme du resolveur, et le comparer sur le code nu le violait :
    # une methode de mathematiques logee dans un chapitre de NSI etait
    # blanchie comme « duplication physique sans usurpation ».
    identities = {
        (row["manual"], row["chapter"], tuple(row["declared_capacity"]))
        for row in members
    }
    if len(identities) == 1:
        return {
            "status": "LEGITIMATE_SHARED_CANONICAL",
            "evidence_rule": "IDENTICAL_CAPACITY_CREDIT",
            "canonical_paths": paths,
            "false_copy_paths": [],
            "reason": (
                "tous les porteurs creditent la meme capacite : la duplication "
                "est physique, le credit n'est pas usurpe"
            ),
        }

    return {
        "status": "AMBIGUOUS",
        "evidence_rule": "NONE_CONCLUSIVE",
        "canonical_paths": [],
        "false_copy_paths": [],
        "reason": (
            "aucune preuve ne designe le proprietaire : le corps ne s'atteste "
            "pas, aucun chapitre ne se duplique, et les capacites declarees "
            "different. Choisir ici reviendrait a tirer au sort"
        ),
    }


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

    invalid_credit: set[str] = set()
    indeterminate_credit: set[str] = set()
    for group in groups:
        selection = select_canonical(group)
        group["canonical_selection"] = selection
        if selection["status"] == "LEGITIMATE_SHARED_CANONICAL":
            continue
        if selection["status"] == "AMBIGUOUS":
            # Aucune source authentique n'est demontrable. Choisir malgre tout
            # rendrait le resultat dependant de l'ordre des chemins ; tout
            # invalider fabriquerait des lacunes pour un contenu present.
            # Le credit est donc INDETERMINE, ce qui n'est ni un credit ni une
            # lacune, et le groupe part en revue.
            indeterminate_credit.update(row["path"] for row in group["members"])
            continue
        keep = set(selection["canonical_paths"])
        for row in group["members"]:
            if row["path"] not in keep:
                invalid_credit.add(row["path"])
    for row in records:
        declared, attested = set(row["declared_capacity"]), set(
            row["body_attested_capacity"]
        )
        if declared and attested and not (declared & attested):
            invalid_credit.add(row["path"])
    # Un objet dementi par son PROPRE corps est invalide, pas indetermine :
    # la contradiction est une preuve, et elle est plus forte que l'absence
    # de proprietaire demontrable dans son groupe. Les deux ensembles doivent
    # rester disjoints, sinon le meme objet serait compte deux fois.
    indeterminate_credit -= invalid_credit

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
            "objects_with_indeterminate_credit": len(indeterminate_credit),
            "ambiguous_canonical_groups": sum(
                1 for g in groups if g["canonical_selection"]["status"] == "AMBIGUOUS"
            ),
            "unknown_canonical_groups": sum(
                1 for g in groups if g["canonical_selection"]["status"] == "UNKNOWN"
            ),
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
        "canonical_selection_rule": (
            "le proprietaire semantique est etabli par preuve ; l'ordre des "
            "chemins n'intervient jamais"
        ),
        "canonical_selection_counts": {
            status: sum(
                1 for g in groups if g["canonical_selection"]["status"] == status
            )
            for status in CANONICAL_STATUSES
        },
        "objects_on_invalid_credit": sorted(invalid_credit),
        "objects_with_indeterminate_credit": sorted(indeterminate_credit),
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
