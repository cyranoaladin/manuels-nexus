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
def manual_of(chapter: str) -> str:
    for prefix, manual in MANUAL_PREFIXES:
        if chapter.startswith(prefix):
            return manual
    return "UNKNOWN"


#: Champs de META qui portent une IDENTITE et non du contenu : celle de
#: l'objet lui-meme, et celle de l'objet qu'il sert. Un corrige nomme son
#: exercice ; une correction d'evaluation nomme son evaluation. Les
#: references au programme, elles, sont du contenu et restent.
IDENTITY_FIELDS = ("id", "exercice_ref", "evaluation_ref")

#: Ce que devient une identite une fois neutralisee dans le corps.
IDENTITY_PLACEHOLDER = "{OBJECT_IDENTITY}"


def identity_tokens(meta: dict[str, Any]) -> list[str]:
    """Les identifiants portes par l'objet, du plus long au plus court.

    L'ordre importe : `X-EX-001-CDP` doit etre neutralise avant `X-EX-001`,
    sinon le suffixe survivrait seul et distinguerait deux copies.
    """

    tokens = set()
    for field in IDENTITY_FIELDS:
        value = meta.get(field)
        if isinstance(value, str) and value.strip():
            tokens.add(value.strip())
    return sorted(tokens, key=len, reverse=True)


def pedagogical_body(text: str) -> str:
    """Le corps pedagogique, identite retiree.

    L'identite ne tient pas dans la seule ligne `% META:`. Le corps la porte
    une seconde fois, dans l'argument de `\\begin{exercice}{<id>}` ou de
    `\\begin{corrige}{<ref>}`. Tant qu'elle y restait, deux copies
    rigoureusement identiques logees dans deux chapitres differents portaient
    deux digests differents : le detecteur ne pouvait structurellement pas
    voir un clone inter-chapitre, alors que c'est exactement ce qu'il declare
    mesurer. On neutralise donc les identifiants declares par l'objet -- les
    siens, jamais ceux qu'il cite, qui sont du contenu.
    """

    body = "\n".join(
        line.rstrip() for line in text.splitlines() if not META_LINE.match(line)
    )
    for token in identity_tokens(read_meta(text)):
        body = body.replace(token, IDENTITY_PLACEHOLDER)
    return body.strip()


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


def _set_digest(values: set[str] | list[str]) -> str:
    return digest(
        json.dumps(sorted(values), ensure_ascii=False, separators=(",", ":"))
    )


def read_meta(text: str) -> dict[str, Any]:
    if "META:" not in text:
        return {}
    raw = text.split("META:", 1)[1].splitlines()[0].strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


_RESOLVER = None


def _resolver(corpora: tuple[Path, ...] | None = None):
    """Table d'identite des capacites, chargee une fois."""

    global _RESOLVER
    selected_corpora = tuple(corpora or CORPORA)
    signature = tuple(str(path.resolve()) for path in selected_corpora)
    if _RESOLVER is None or _RESOLVER[0] != signature:
        spec = importlib.util.spec_from_file_location(
            "capacity_identity", ROOT / "scripts/capacity_identity.py"
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        _RESOLVER = (
            signature,
            module,
            module.CapacityIdentityResolver.from_corpora(selected_corpora),
        )
    return _RESOLVER[1], _RESOLVER[2]


def declared_capacities(
    meta: dict[str, Any],
    *,
    chapter: str | None = None,
) -> tuple[str, ...]:
    """Codes locaux credites, resolus dans la portee du chapitre.

    Cette fonction coupait autrefois la chaine a son dernier tiret :
    `TSPE-CONCLGN-C1` devenait `C1`, et le credit d'une capacite passait a sa
    voisine. La resolution est desormais une egalite exacte, portee par le
    contrat du chapitre.
    """

    identity, resolver = _resolver()
    scope = chapter or identity.normalise(meta.get("chapitre"))
    if scope not in resolver.chapters:
        raise identity.UnresolvedCapacityIdentity(
            f"chapitre sans contrat pour declaration de capacite: {scope or '<vide>'}"
        )
    return tuple(sorted(resolver.resolve_meta_codes(scope, meta)))


#: Champs de lien deja normalises dans le depot : un objet satellite designe
#: par eux l'objet hote qu'il assiste. Les deux noms coexistent dans le corpus
#: et sont lus comme une seule reference.
HOST_LINK_FIELDS = ("exercice_id", "exercice_ref")


def host_references(meta: dict[str, Any]) -> list[str]:
    """References d'hote portees par le META, dedupliquees et triees."""

    return sorted(
        {
            str(meta[field]).strip()
            for field in HOST_LINK_FIELDS
            if isinstance(meta.get(field), str) and str(meta[field]).strip()
        }
    )


def _path_key(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def scan() -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    records: list[dict[str, Any]] = []
    blockers: list[dict[str, str]] = []
    identity, resolver = _resolver(CORPORA)
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
            try:
                declared = tuple(sorted(resolver.resolve_meta_codes(chapter, meta)))
            except identity.CapacityIdentityError as exc:
                declared = ()
                blockers.append(
                    {
                        "classification": (
                            "AMBIGUOUS_CAPACITY_IDENTITY"
                            if isinstance(exc, identity.AmbiguousCapacityIdentity)
                            else "UNRESOLVED_CAPACITY_IDENTITY"
                        ),
                        "path": _path_key(path),
                        "object_id": str(meta.get("id") or ""),
                        "reason": str(exc),
                    }
                )
            manual = manual_of(chapter)
            records.append(
                {
                    "path": _path_key(path),
                    "object_id": meta.get("id"),
                    "chapter": chapter,
                    "manual": manual,
                    "source_type": path.parts[index + 1],
                    "status": meta.get("status"),
                    "declared_capacity": list(declared),
                    "declared_capacity_uids": [
                        f"{manual}::{chapter}::{code}" for code in declared
                    ],
                    "exact_body_digest": digest(body),
                    "normalized_body_digest": digest(normalized_body(body)),
                    "payload_chars": len(payload_only(body)),
                    "payload_empty": not bool(payload_only(body)),
                    "host_refs": host_references(meta),
                }
            )
    # Le lien vers l'hote est RESOLU ici, pendant le scan, et materialise dans
    # le record : la selection canonique ne relit jamais le disque.
    object_ids_by_chapter: dict[str, set[str]] = collections.defaultdict(set)
    for row in records:
        if row["object_id"]:
            object_ids_by_chapter[row["chapter"]].add(str(row["object_id"]))
    for row in records:
        refs = row["host_refs"]
        host = refs[0] if len(refs) == 1 else None
        row["resolved_host_uid"] = (
            f"{row['manual']}::{row['chapter']}::{host}"
            if host is not None and host in object_ids_by_chapter[row["chapter"]]
            else None
        )
    return records, sorted(
        blockers, key=lambda row: (row["path"], row["object_id"], row["reason"])
    )


def disposition_of(members: list[dict[str, Any]]) -> str:
    """Chaque groupe recoit exactement une disposition."""

    capacity_at_stake = any(
        row.get("declared_capacity_uids") or row.get("declared_capacity")
        for row in members
    )
    if all(row.get("payload_empty") is True for row in members) and not capacity_at_stake:
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
OWNERSHIP_EVIDENCE_FIELDS = {
    "chapter_ownership",
    "capacity_alignment",
    "official_programme_alignment",
    "canonical_assembly",
    "source_provenance",
    "contract_role",
}


class CloneEvidenceError(RuntimeError):
    """Une preuve de propriété est incomplète ou contradictoire."""


def _all_satellites_of_distinct_hosts(members: list[dict[str, Any]]) -> bool:
    """Tous les membres assistent un hôte propre, résolu et sans crédit.

    Les trois conditions sont exigées de CHAQUE membre, et la troisième du
    groupe entier :

    1. aucune capacité résolue n'est déclarée — aucun crédit n'est en jeu, donc
       aucun ne peut être ni usurpé ni perdu ;
    2. exactement une référence d'hôte est portée par les champs de lien
       normalisés — zéro ou deux ne désignent pas un hôte ;
    3. l'hôte est résolu, c'est-à-dire qu'il existe réellement et appartient au
       chapitre du satellite, et deux membres n'en partagent jamais un.

    Le champ `resolved_host_uid` est posé par `scan()` : cette fonction ne lit
    jamais le disque et ne dépend d'aucun identifiant particulier.
    """

    hosts = []
    for row in members:
        if row.get("declared_capacity"):
            return False
        if len(row.get("host_refs") or []) != 1:
            return False
        host = row.get("resolved_host_uid")
        if not host:
            return False
        # L'hote resolu doit etre celui du satellite lui-meme : meme manuel,
        # meme chapitre, et l'identifiant qu'il designe. Un hote d'un autre
        # chapitre ne blanchit rien.
        own_scope = f"{row.get('manual')}::{row.get('chapter')}::{row['host_refs'][0]}"
        if host != own_scope:
            return False
        hosts.append(host)
    return bool(hosts) and len(set(hosts)) == len(hosts)


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

    `NO_CAPACITY_AT_STAKE`
        Le corps est du gabarit sans contenu pedagogique.

    `SATELLITE_WITH_DISTINCT_HOST`
        Chaque membre est un satellite : il ne credite aucune capacite et
        assiste EXACTEMENT UN objet hote, existant et loge dans son propre
        chapitre ; et deux membres n'assistent jamais le meme hote. Aucun
        credit n'est alors en jeu -- donc aucun ne peut etre usurpe -- et
        retirer un membre priverait un hote reel de son assistance. Le partage
        du corps est legitime, tous les membres sont canoniques.

    Une occurrence textuelle `C<n>` n'est jamais une preuve : elle peut être
    une variable Python, un renvoi ou un identifiant interne. En l'absence
    d'une ownership map autoritaire fondée sur programme, contrat, assemblage
    et provenance, le statut est `AMBIGUOUS` et le groupe part en revue.
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

    ownership = group.get("ownership_evidence")
    if ownership is not None:
        canonical = sorted(set(ownership.get("canonical_paths") or []))
        authority = ownership.get("authority") or {}
        if len(canonical) != 1 or not set(canonical) <= set(paths):
            raise CloneEvidenceError(
                "ownership_evidence: un chemin canonique unique du groupe est requis"
            )
        missing = sorted(
            field
            for field in OWNERSHIP_EVIDENCE_FIELDS
            if not authority.get(field)
        )
        if missing:
            raise CloneEvidenceError(
                "ownership_evidence incomplet: " + ", ".join(missing)
            )
        return {
            "status": "SEMANTIC_CANONICAL",
            "evidence_rule": "AUTHORITATIVE_OWNERSHIP_MAP",
            "canonical_paths": canonical,
            "false_copy_paths": [path for path in paths if path not in set(canonical)],
            "authority": {key: authority[key] for key in sorted(authority)},
            "reason": (
                "le propriétaire est démontré par ownership, capacité, programme, "
                "assemblage, provenance et rôle contractuel"
            ),
        }

    if _all_satellites_of_distinct_hosts(members):
        return {
            "status": "LEGITIMATE_SHARED_CANONICAL",
            "evidence_rule": "SATELLITE_WITH_DISTINCT_HOST",
            "canonical_paths": paths,
            "false_copy_paths": [],
            "reason": (
                "chaque membre est un satellite sans capacité déclarée, "
                "rattaché à un hôte unique, existant, de son propre chapitre, "
                "et deux membres n'assistent jamais le même hôte : aucun "
                "crédit n'est en jeu et aucun hôte ne serait privé"
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
    records, capacity_identity_blockers = scan()
    by_body: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in records:
        by_body[row["exact_body_digest"]].append(row)

    groups = []
    for index, (body_digest, members) in enumerate(
        sorted((k, v) for k, v in by_body.items() if len(v) > 1)
    ):
        members = sorted(members, key=lambda row: row["path"])
        disposition = disposition_of(members)
        groups.append(
            {
                "clone_group_id": f"CG-{index + 1:04d}",
                "canonical_body_digest": body_digest,
                "normalized_body_digest": members[0]["normalized_body_digest"],
                "object_count": len(members),
                "excess_object_count": len(members) - 1,
                "disposition": disposition,
                "same_capacity": len(
                    {tuple(r["declared_capacity_uids"]) for r in members}
                )
                == 1,
                "same_chapter": len({r["chapter"] for r in members}) == 1,
                "same_manual": len({r["manual"] for r in members}) == 1,
                "members": members,
            }
        )

    invalid_credit: set[str] = set()
    indeterminate_credit: set[str] = set()
    for group in groups:
        selection = select_canonical(group)
        group["canonical_selection"] = selection
        canonical = set(selection["canonical_paths"])
        false_copies = set(selection["false_copy_paths"])
        for row in group["members"]:
            if selection["status"] == "LEGITIMATE_SHARED_CANONICAL":
                row["canonical_object_status"] = "LEGITIMATE_SHARED_CANONICAL"
            elif selection["status"] == "AMBIGUOUS":
                row["canonical_object_status"] = "AMBIGUOUS"
            elif selection["status"] == "UNKNOWN":
                row["canonical_object_status"] = "UNKNOWN"
            elif row["path"] in canonical:
                row["canonical_object_status"] = "SEMANTIC_CANONICAL"
            elif row["path"] in false_copies:
                row["canonical_object_status"] = "FALSE_COPY"
            else:
                row["canonical_object_status"] = "UNKNOWN"
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
    # Les deux ensembles doivent rester disjoints. Une simple occurrence
    # lexicale dans le corps ne peut jamais rendre un crédit invalide.
    indeterminate_credit -= invalid_credit
    # Une déclaration de capacité non résolue ne peut jamais conserver un
    # crédit. Le ledger continue à mesurer les clones, mais rend ce blocker
    # explicite et place l'objet en revue indéterminée.
    indeterminate_credit.update(
        row["path"] for row in capacity_identity_blockers
    )
    indeterminate_credit -= invalid_credit

    per_manual: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    per_chapter: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    unattributed_excess = 0
    for group in groups:
        selection = group["canonical_selection"]
        if selection["status"] in {"AMBIGUOUS", "UNKNOWN"}:
            unattributed_excess += group["excess_object_count"]
        for row in group["members"]:
            if row["canonical_object_status"] != "FALSE_COPY":
                continue
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
            "excluded": [
                "% META: identity line",
                "declared object identity inside the body (id, exercice_ref, "
                "evaluation_ref)",
                "trailing and edge whitespace",
            ],
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
            "boilerplate_rule": (
                "payload structurel strictement vide ET aucune capacite declaree; "
                "la longueur courte ne prouve jamais l'absence de contenu"
            ),
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
            "capacity_identity_blockers": len(capacity_identity_blockers),
        },
        "dispositions": {
            name: {"groups": dispositions[name], "excess_objects": excess[name]}
            for name in sorted(dispositions)
        },
        "unknown": sum(
            1
            for group in groups
            if group["canonical_selection"]["status"] == "UNKNOWN"
        ),
        "unattributed_excess_objects": unattributed_excess,
        "per_manual": {k: dict(v) for k, v in sorted(per_manual.items())},
        "per_chapter": {
            k: dict(v)
            for k, v in sorted(
                per_chapter.items(), key=lambda kv: (-kv[1]["TOTAL"], kv[0])
            )
        },
        "canonical_selection_rule": (
            "le proprietaire semantique est etabli par une ownership map "
            "autoritaire couvrant programme, contrat, assemblage et provenance ; "
            "un groupe dont tous les membres sont des satellites sans capacite "
            "declaree, rattaches chacun a un hote unique, existant et du meme "
            "chapitre, et deux a deux distincts, est un partage legitime ; "
            "l'ordre des chemins n'intervient jamais"
        ),
        "canonical_selection_counts": {
            status: sum(
                1 for g in groups if g["canonical_selection"]["status"] == status
            )
            for status in CANONICAL_STATUSES
        },
        "objects_on_invalid_credit": sorted(invalid_credit),
        "objects_with_indeterminate_credit": sorted(indeterminate_credit),
        "capacity_identity_blockers": capacity_identity_blockers,
        "capacity_identity_blockers_digest": _set_digest(
            {
                f"{row['classification']}::{row['path']}::{row['object_id']}::{row['reason']}"
                for row in capacity_identity_blockers
            }
        ),
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
