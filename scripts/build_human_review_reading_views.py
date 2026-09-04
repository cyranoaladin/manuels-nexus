#!/usr/bin/env python3
"""Vues de lecture humaine des dossiers de revue 1SPE, une par (chapitre, role).

Les packets JSON de `audit/reviews/human/<CHAPITRE>/` sont la SEULE autorite
machine. Ils sont exacts et complets ; ils ne sont pas lisibles. Un expert qui
doit rendre UN verdict sur UN chapitre y trouve 161 objets a plat, 371 cellules
capacite x role reparties sur dix fichiers, et aucune trace de l'ordre dans
lequel le lecteur du manuel rencontrera ces objets.

Ce producteur derive de ces memes sources une vue Markdown par role :

`EXPERT_MATHEMATIQUE`
    les objets `SCIENCE_HUMAINE_REQUISE` du chapitre, groupes par FAMILLE
    SCIENTIFIQUE puis par type d'objet. La famille n'est pas inventee ici :
    c'est la capacite du referentiel du depot
    (`Mathematiques/manuel-maths/referentiel/capacites_<CHAPITRE>.json`), avec
    son libelle BO. Un objet qui ne declare aucune capacite -- un coup de pouce,
    par exemple -- herite de celle de l'exercice qu'il aide ; s'il n'en herite
    aucune, il reste visible dans une famille residuelle, il n'est pas devine.

`EXPERT_PROGRAMME_PEDAGOGIE`
    les cellules capacite x role consolidees PAR CAPACITE : les roles
    pedagogiques concernes, les objets contributeurs, la richesse declaree
    (occasions, gestes de raisonnement, progression de difficulte) et la raison
    pour laquelle la machine a route la cellule vers l'humain.

Aucune vue ne porte de verdict ni d'identite de relecteur : les deux roles sont
definis, les noms humains seront renseignes a l'assignation.

L'ordre d'assemblage n'est pas l'ordre alphabetique des repertoires : il est lu
chez l'assembleur lui-meme (`collect_chapter`), c'est-a-dire l'ordre que le
lecteur du PDF recoit.
"""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
REVIEWS = AUDIT / "reviews" / "human"
CHAPTERS_DIR = ROOT / "Mathematiques" / "manuel-maths" / "chapitres"
REFERENTIEL = ROOT / "Mathematiques" / "manuel-maths" / "referentiel"

DISPOSITION_LEDGER = AUDIT / "1SPE_MANUAL_REVIEW_DISPOSITION_LEDGER.json"
SEMANTIC_LEDGER = AUDIT / "SEMANTIC_ALIGNMENT_LEDGER.json"
RICHNESS_MATRIX = AUDIT / "CHAPTER_RICHNESS_MATRIX.json"
PUBLISH_READINESS = AUDIT / "PUBLISH_READINESS_CHAPTER_MATRIX.json"
QCM_EVIDENCE = AUDIT / "QCM_INDEPENDENT_EVIDENCE_V2.json"
PDF_REGISTRY = AUDIT / "PDF_ARTIFACT_REGISTRY.yaml"
PRINT_RECEIPT = AUDIT / "1SPE_PRINT_CANDIDATE_BUILD_RECEIPT.json"

ROLE_A = "EXPERT_MATHEMATIQUE"
ROLE_B = "EXPERT_PROGRAMME_PEDAGOGIE"
ROLES = {ROLE_A: "A", ROLE_B: "B"}
COMMON_DOCUMENT = REVIEWS / "ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md"

HUMAN_SCIENCE = "SCIENCE_HUMAINE_REQUISE"
RESIDUAL_FAMILY = "CAPACITE_NON_DECLAREE_PAR_L_OBJET"
NO_BO_WORDING = (
    "aucun libelle BO : le referentiel du depot ne declare pas cette capacite"
)
ROUTING_DOCTRINE = (
    "Seul le META rattache les corps a une capacite ; l'identite declaree est "
    "resolue par egalite exacte, et la couverture de reponses n'etablit qu'une "
    "COUVERTURE. Etablir qu'un corps SERT la capacite est un jugement "
    "pedagogique, pas un calcul : c'est un resultat terminal, pas une lacune de "
    "mesure. C'est pourquoi chaque cellule de ce chapitre est routee vers vous."
)

#: Mentions imposees, reproduites a l'identique dans chaque vue.
MENTION_BASELINE = (
    "Aucun humain n'a encore approuve ce chapitre : REVIEW_DELTA_BASELINE = NONE. "
    "Le perimetre de revue est le CHAPITRE COURANT ENTIER. Les listes ci-dessous "
    "dirigent l'attention, elles ne reduisent pas le perimetre."
)
MENTION_DERIVED = (
    "Cette vue est derivee et sans autorite. L'autorite machine reste le packet "
    "JSON canonique."
)
MENTION_DECISION_UNIT = (
    "L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, "
    "pas des centaines de signatures objet par objet."
)

CHECKLISTS = {
    ROLE_A: (
        "exactitude scientifique",
        "hypotheses",
        "definitions",
        "notations",
        "demonstrations et raisonnements",
        "calculs",
        "fidelite exercice/corrige",
        "verite des QCM",
        "verite des evaluations",
        "items de science humaine requise",
        "concepts d'une autre annee",
    ),
    ROLE_B: (
        "completude du programme officiel",
        "alignement des capacites",
        "progression",
        "prerequis",
        "methodes",
        "diversite des exercices",
        "difficulte",
        "richesse",
        "remediation",
        "conception des evaluations",
        "pertinence pedagogique des QCM",
        "coherence du chapitre",
        "coherence au niveau du manuel",
    ),
}

PEDAGOGICAL_ROLE_LABELS = {
    "corriges": "corriges",
    "cours": "cours",
    "evaluations": "evaluations",
    "exercices": "exercices",
    "methodes": "methodes",
    "qcm": "QCM",
    "remediation": "remediation",
}

META = re.compile(r"^% META: (\{.*\})\s*$", re.MULTILINE)
TRAILING_NUMBER = re.compile(r"^(?P<prefix>.*?)(?P<number>\d+)(?P<suffix>\D*)$")


# --------------------------------------------------------------------------
# lecture des sources
# --------------------------------------------------------------------------


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_assembler():
    """L'assembleur Mathematiques, charge sous un nom qui lui est propre.

    Les manuels Maths et NSI ont chacun un module `assemble_manuel` : les
    charger sous le meme nom ferait mesurer un corpus avec l'assembleur de
    l'autre.
    """

    scripts = CHAPTERS_DIR.parent / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    relative = "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
    spec = importlib.util.spec_from_file_location(
        "maths_assemble_manuel_reading_views", ROOT / relative
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["maths_assemble_manuel_reading_views"] = module
    spec.loader.exec_module(module)
    return module


def _object_meta(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    match = META.search(path.read_text(encoding="utf-8"))
    if not match:
        return {}
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}


def chapter_ids() -> list[str]:
    """Les chapitres qui portent un dossier de revue complet."""

    found = []
    for directory in sorted(p for p in REVIEWS.iterdir() if p.is_dir()):
        packets = [
            directory / f"packet-{letter}-{role}.json"
            for role, letter in ROLES.items()
        ]
        if all(packet.is_file() for packet in packets):
            found.append(directory.name)
    return found


# --------------------------------------------------------------------------
# mise en forme
# --------------------------------------------------------------------------


def compact_ids(identifiers: list[str]) -> str:
    """Comprime des identifiants numerotes en intervalles lisibles.

    Un expert ne lit pas quatre-vingt-huit identifiants a la file. Les suites
    consecutives d'un meme prefixe deviennent `...-031..042-CDP` ; ce qui ne
    suit aucune numerotation reste ecrit tel quel.
    """

    families: dict[tuple[str, str, int], list[int]] = defaultdict(list)
    plain: list[str] = []
    for identifier in identifiers:
        match = TRAILING_NUMBER.match(identifier)
        if not match:
            plain.append(identifier)
            continue
        number = match.group("number")
        families[(match.group("prefix"), match.group("suffix"), len(number))].append(
            int(number)
        )
    pieces: list[str] = []
    for (prefix, suffix, width), numbers in sorted(families.items()):
        for run in _consecutive_runs(sorted(set(numbers))):
            first, last = run[0], run[-1]
            head = f"{prefix}{first:0{width}d}"
            if first == last:
                pieces.append(f"`{head}{suffix}`")
            else:
                pieces.append(f"`{head}..{last:0{width}d}{suffix}`")
    pieces.extend(f"`{item}`" for item in sorted(plain))
    return ", ".join(pieces)


def _consecutive_runs(numbers: list[int]) -> list[list[int]]:
    runs: list[list[int]] = []
    for number in numbers:
        if runs and number == runs[-1][-1] + 1:
            runs[-1].append(number)
        else:
            runs.append([number])
    return runs


def _plural(count: int, singular: str, plural: str | None = None) -> str:
    return f"{count} {singular if count <= 1 else (plural or singular + 's')}"


# --------------------------------------------------------------------------
# faits par chapitre
# --------------------------------------------------------------------------


def chapter_facts(chapter: str, sources: dict[str, Any]) -> dict[str, Any]:
    """Tout ce qu'une vue peut dire du chapitre, lu une seule fois."""

    directory = CHAPTERS_DIR / chapter
    contract = yaml.safe_load((directory / "contrat.yaml").read_text(encoding="utf-8"))
    referential = _load_json(REFERENTIEL / f"capacites_{chapter.replace('-', '_')}.json")
    packets = {
        role: _load_json(REVIEWS / chapter / f"packet-{letter}-{role}.json")
        for role, letter in ROLES.items()
    }
    review_state = _load_json(REVIEWS / chapter / "REVIEW_STATE.json")

    assembler = sources["assembler"]
    assembly = {
        variant: assembler.collect_chapter(directory, variant)
        for variant in ("professeur", "eleve")
    }
    segments = {
        variant: [
            (rubric, len(list(group)))
            for rubric, group in itertools.groupby(
                assembler.rubrique_libelle(path) for path in paths
            )
        ]
        for variant, paths in assembly.items()
    }
    assembled = {
        path.relative_to(ROOT).as_posix() for path in assembly["professeur"]
    }
    packet_paths = {obj["path"] for obj in packets[ROLE_A]["objects"]}

    capacities = _capacities(chapter, contract, referential, sources)
    return {
        "chapter": chapter,
        "directory": directory,
        "contract": contract,
        "packets": packets,
        "review_state": review_state,
        "capacities": capacities,
        "assembly": assembly,
        "segments": segments,
        "not_assembled": sorted(packet_paths - assembled),
        "families": _science_families(chapter, capacities, sources),
        "cells": _cells_by_capacity(chapter, sources),
        "richness": sources["richness"]["chapters"].get(chapter, {}),
        "readiness": sources["readiness_by_chapter"].get(chapter, {}),
        "qcm": _qcm_facts(chapter, sources),
    }


def _capacities(
    chapter: str,
    contract: dict[str, Any],
    referential: dict[str, Any],
    sources: dict[str, Any],
) -> list[dict[str, Any]]:
    """Les capacites du chapitre, avec leur libelle eleve et leur libelle BO."""

    bo_by_id = {item["id"]: item for item in referential["capacites"]}
    atoms = sources["atoms_by_capacity"]
    capacities = []
    for item in contract["capacites"]:
        code = str(item["code"])
        reference = str(item.get("ref_capacite") or f"{chapter}-{code}")
        bo = bo_by_id.get(reference, {})
        capacities.append(
            {
                "code": code,
                "reference": reference,
                "libelle_eleve": str(item.get("libelle_eleve", "")),
                "libelle_bo": str(bo.get("libelle_bo", "")),
                "demonstration_exigible": bool(bo.get("demonstration_exigible")),
                "demonstration": str(bo.get("demonstration", "")),
                "official_atoms": atoms.get((chapter, code), []),
            }
        )
    return capacities


def _science_families(
    chapter: str, capacities: list[dict[str, Any]], sources: dict[str, Any]
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    """Objets `SCIENCE_HUMAINE_REQUISE`, par famille scientifique puis par type."""

    known = {capacity["code"] for capacity in capacities}
    families: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for entry in sources["disposition"]["objects"]:
        if entry["chapter"] != chapter or entry["disposition"] != HUMAN_SCIENCE:
            continue
        codes = [code for code in (entry.get("capacites") or []) if code in known]
        if not codes:
            codes = _inherited_codes(entry, known)
        for code in codes or [RESIDUAL_FAMILY]:
            families[code][entry["type_objet"]].append(entry)
    return {
        code: {
            object_type: sorted(entries, key=lambda item: item["object_id"])
            for object_type, entries in sorted(types.items())
        }
        for code, types in families.items()
    }


def _inherited_codes(entry: dict[str, Any], known: set[str]) -> list[str]:
    """La capacite d'un objet muet : celle qu'il declare, sinon celle qu'il sert."""

    meta = _object_meta(ROOT / entry["path"])
    codes = [code for code in (meta.get("capacites_codes") or []) if code in known]
    if codes:
        return sorted(codes)
    parent_id = meta.get("exercice_id")
    if not parent_id:
        return []
    parent = (ROOT / entry["path"]).parent / f"{parent_id}.tex"
    parent_meta = _object_meta(parent)
    return sorted(
        code
        for code in (parent_meta.get("capacites_codes") or [])
        if code in known
    )


def _cells_by_capacity(
    chapter: str, sources: dict[str, Any]
) -> dict[str, list[dict[str, Any]]]:
    cells: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in sources["semantic"]["records"]:
        if record["chapter"] != chapter:
            continue
        cells[record["official_capacity"]["local_code"]].append(record)
    return {
        code: sorted(records, key=lambda item: item["pedagogical_role"])
        for code, records in cells.items()
    }


def _qcm_facts(chapter: str, sources: dict[str, Any]) -> dict[str, Any]:
    questions = [
        question
        for question in sources["qcm_evidence"]["questions"]
        if question["chapter"] == chapter
    ]
    statuses: dict[str, int] = defaultdict(int)
    for question in questions:
        statuses[question["evidence_status"]] += 1
    human = sorted(
        (question for question in questions if question["human_review_required"]),
        key=lambda item: item["question_id"],
    )
    return {
        "count": len(questions),
        "statuses": dict(sorted(statuses.items())),
        "human": [_qcm_detail(question) for question in human],
    }


def _qcm_detail(question: dict[str, Any]) -> dict[str, Any]:
    """L'enonce et les options de la question, sans sa cle declaree.

    La cle n'est pas reproduite : l'expert etablit la reponse par lui-meme, et
    la source canonique la porte deja. Le contrat d'independance du solveur
    interdit de faire circuler la cle avec l'enonce.
    """

    source = ROOT / question["source_path"]
    statement = ""
    options: list[tuple[str, str]] = []
    if source.is_file():
        payload = _load_json(source)
        for item in payload.get("questions", []):
            if item.get("id") == question["question_id"]:
                statement = str(item.get("enonce", ""))
                options = sorted(
                    (str(key), str(value))
                    for key, value in (item.get("options") or {}).items()
                )
                break
    return {
        "question_id": question["question_id"],
        "capacity": question["capacity"],
        "source_path": question["source_path"],
        "statement": statement,
        "options": options,
        "reason": question["reason"],
        "release_blocking": question["release_blocking"],
        "semantic_question_digest": question["semantic_question_digest"],
    }


# --------------------------------------------------------------------------
# blocs communs aux deux vues
# --------------------------------------------------------------------------


def _header(facts: dict[str, Any], role: str) -> list[str]:
    chapter = facts["chapter"]
    packet = facts["packets"][role]
    letter = ROLES[role]
    authority = packet["programme_authority"]["PROGRAMME_D_ENSEIGNEMENT"]
    return [
        f"# Vue de lecture — {facts['contract']['titre']} — {role}",
        "",
        f"Chapitre `{chapter}` · manuel `{packet['manual_id']}` "
        f"({authority['niveau']}, {authority['enseignement']}) · "
        f"packet {letter} · role `{role}`.",
        "",
        f"> **{MENTION_DERIVED}**",
        ">",
        f"> Packet canonique : `audit/reviews/human/{chapter}/"
        f"packet-{letter}-{role}.json`",
        f"> Etat de revue : `audit/reviews/human/{chapter}/REVIEW_STATE.json`",
        "> Producteur de cette vue : `scripts/build_human_review_reading_views.py`",
        ">",
        "> Toute divergence entre cette vue et le packet se tranche en faveur du "
        "packet. Cette vue ne cree, ne ferme et ne reduit aucune obligation.",
        "",
    ]


def _decision_block(facts: dict[str, Any], role: str) -> list[str]:
    packet = facts["packets"][role]
    verdicts = " / ".join(f"`{value}`" for value in packet["permitted_verdicts"])
    return [
        "## 1. Ce que vous decidez",
        "",
        f"- {MENTION_DECISION_UNIT}",
        f"- {MENTION_BASELINE}",
        f"- CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST "
        f"(`{packet['semantic_review_digest']}`) ; l'approbation graphique releve "
        "de la porte D7, independante.",
        f"- Verdicts autorises, a rendre dans le packet JSON canonique et jamais "
        f"dans cette vue : {verdicts}.",
        "- Cette vue ne porte aucune decision et ne nomme personne : l'assignation "
        f"du role reste `{packet['reviewer_assignment']}`, l'etat du packet reste "
        f"`{packet['verdict_state']}`.",
        "",
        "| Perimetre | Valeur |",
        "| --- | --- |",
        f"| Objets du chapitre dans le packet | {packet['object_count']} |",
        f"| Empreinte de l'ensemble d'objets | `{packet['object_set_digest']}` |",
        f"| Empreinte semantique liee a l'approbation | "
        f"`{packet['semantic_review_digest']}` |",
        f"| Empreinte du packet | `{packet['packet_digest']}` |",
        f"| Revision du depot gelee dans le packet | "
        f"`{packet['repository_source_sha']}` |",
        f"| Preuve de rendu portee par le packet | `{packet['render_evidence']}` |",
        "",
    ]


def _programme_block(facts: dict[str, Any], role: str) -> list[str]:
    authority = facts["packets"][role]["programme_authority"][
        "PROGRAMME_D_ENSEIGNEMENT"
    ]
    contract = facts["contract"]
    lines = [
        "## 2. Le chapitre et ses capacites du programme officiel",
        "",
        f"**{contract['titre']}** — programme applicable "
        f"{authority['effective_from']}, {authority['official_ref']}, "
        f"BO n° {authority['bo_number']} du {authority['bo_date']}.",
        f"Source officielle : {authority['authority_url']}",
        "",
    ]
    accroche = str(contract.get("situation_accroche") or "").strip()
    if accroche:
        lines += [f"Situation d'accroche declaree : {accroche}", ""]
    hours = contract.get("temps_estime_h") or {}
    if hours:
        rendered = " · ".join(
            f"parcours {key[-1]} : {value} h" for key, value in sorted(hours.items())
        )
        lines += [f"Temps estime declare : {rendered}.", ""]
    lines += [
        "| Code | Libelle eleve | Libelle BO | Demonstration exigible |",
        "| --- | --- | --- | --- |",
    ]
    for capacity in facts["capacities"]:
        demonstration = "non"
        if capacity["demonstration_exigible"]:
            demonstration = "oui"
            if capacity["demonstration"]:
                demonstration = f"oui — {capacity['demonstration']}"
        lines.append(
            f"| `{capacity['code']}` | {capacity['libelle_eleve']} | "
            f"{capacity['libelle_bo'] or NO_BO_WORDING} | {demonstration} |"
        )
    lines.append("")
    lines += _atoms_block(facts)
    prerequisites = contract.get("prerequis") or []
    if prerequisites:
        lines += [
            "**Prerequis declares par le contrat du chapitre**",
            "",
            "| Code | Libelle | Chapitre d'origine |",
            "| --- | --- | --- |",
        ]
        for item in prerequisites:
            lines.append(
                f"| `{item['code']}` | {item.get('libelle', '')} | "
                f"{item.get('chapitre_origine', '')} |"
            )
        lines.append("")
    return lines


def _atoms_block(facts: dict[str, Any]) -> list[str]:
    lines = ["**Attendus officiels rattaches, capacite par capacite**", ""]
    for capacity in facts["capacities"]:
        atoms = capacity["official_atoms"]
        if not atoms:
            lines.append(
                f"- `{capacity['code']}` : aucun attendu officiel rattache dans "
                "`audit/SEMANTIC_ALIGNMENT_LEDGER.json`."
            )
            continue
        lines.append(f"- `{capacity['code']}` — {_plural(len(atoms), 'attendu')} :")
        for atom in atoms:
            lines.append(
                f"    - `{atom['atom_id']}` ({atom['obligation_type']}, "
                f"{atom['official_section']}) : "
                f"{atom['official_wording_or_short_paraphrase']}"
            )
    lines.append("")
    return lines


def _assembly_block(facts: dict[str, Any]) -> list[str]:
    segments = facts["segments"]
    teacher = facts["assembly"]["professeur"]
    student = facts["assembly"]["eleve"]
    lines = [
        "## 3. Structure reelle et ordre d'assemblage courant",
        "",
        "L'ordre ci-dessous n'est pas l'ordre alphabetique des repertoires : il "
        "est lu chez l'assembleur du manuel "
        "(`Mathematiques/manuel-maths/scripts/assemble_manuel.py`, "
        "`collect_chapter`). C'est la sequence que le lecteur du PDF recoit.",
        "",
        "| Rang | Rubrique imprimee | Objets (professeur) |",
        "| --- | --- | --- |",
    ]
    for rank, (rubric, count) in enumerate(segments["professeur"], start=1):
        lines.append(f"| {rank} | {rubric} | {count} |")
    lines += [
        "",
        f"Total assemble : {len(teacher)} objets en variante professeur, "
        f"{len(student)} en variante eleve "
        "(la variante eleve exclut les corriges et les corriges d'evaluation).",
        "",
        "La page d'ouverture du chapitre est composee par l'assembleur a partir "
        "de `contrat.yaml` (titre, capacites, situation d'accroche, temps "
        "estime) : elle n'apparait donc pas comme un objet de la sequence.",
        "",
    ]
    lines += _placement_block(facts)
    if facts["not_assembled"]:
        lines += [
            "**Objets du perimetre de revue absents de la sequence assemblee**",
            "",
            f"{_plural(len(facts['not_assembled']), 'objet')} du packet "
            "n'apparaissent dans aucune rubrique assemblee : le perimetre de "
            "revue les couvre, le PDF ne les imprime pas.",
            "",
        ]
        for path in facts["not_assembled"]:
            lines.append(f"- `{path}`")
        lines.append("")
    return lines


def _placement_block(facts: dict[str, Any]) -> list[str]:
    """Le placement des temps pedagogiques, dit en toutes lettres."""

    order = [rubric for rubric, _ in facts["segments"]["professeur"]]
    positions = {rubric: index + 1 for index, rubric in enumerate(order)}
    lines = ["**Placement des temps pedagogiques dans la progression**", ""]
    for rubric, sentence in (
        ("Diagnostic", "le diagnostic ouvre le chapitre"),
        ("Cours", "le cours precede les methodes"),
        ("Méthodes", "les methodes sont regroupees avant les exercices"),
        ("Exercices", "les exercices suivent les methodes en un seul bloc"),
        ("TD", "le TD est place apres les exercices"),
        ("Auto-évaluation", "le QCM d'auto-evaluation suit le TD"),
        ("Évaluation", "les evaluations viennent apres le QCM"),
        ("Remédiation", "la remediation est placee apres les evaluations"),
        ("Corrigés", "les corriges ferment la variante professeur"),
    ):
        if rubric in positions:
            lines.append(f"- rang {positions[rubric]} — {sentence}.")
        else:
            lines.append(
                f"- rubrique « {rubric} » : aucun objet assemble dans ce chapitre."
            )
    lines += [
        "",
        "Cet ordre est un fait d'assemblage, pas un jugement : sa pertinence "
        "pedagogique fait partie de ce que vous evaluez.",
        "",
    ]
    return lines


def _checklist_block(role: str, index: int) -> list[str]:
    lines = [f"## {index}. Checklist du role `{role}`", ""]
    for position, item in enumerate(CHECKLISTS[role], start=1):
        lines.append(f"{position}. {item}")
    lines += [
        "",
        "Cette checklist est celle du role. Elle s'applique au CHAPITRE COURANT "
        "ENTIER, y compris aux objets qu'aucune section de cette vue ne cite.",
        "",
    ]
    return lines


def _pdf_block(facts: dict[str, Any], sources: dict[str, Any], index: int) -> list[str]:
    manual = facts["packets"][ROLE_A]["manual_id"]
    records = sorted(
        (
            record
            for record in sources["pdf_registry"]["records"]
            if record.get("manual") == manual
        ),
        key=lambda item: item["path"],
    )
    if not records:
        raise SystemExit(
            f"aucun PDF declare pour le manuel {manual} dans "
            "audit/PDF_ARTIFACT_REGISTRY.yaml"
        )
    receipt = sources["print_receipt"]
    lines = [
        f"## {index}. Reference de lecture : le PDF candidat",
        "",
        "Le PDF sert a lire le chapitre dans l'ordre ou l'eleve le recevra. Il "
        "n'est pas une preuve : le packet ne porte aucune preuve de rendu "
        f"(`render_evidence = {facts['packets'][ROLE_A]['render_evidence']}`), et "
        "aucun index page-objet n'est etabli.",
        "",
        "| Fichier | Variante | Pages | Role declare | Etat declare |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in records:
        lines.append(
            f"| `{record['path']}` | {record['variant']} | "
            f"{record['page_count']} | {record['role']} | "
            f"{record['release_state']} |"
        )
    lines += [
        "",
        f"Ces instantanes sont declares `{records[0]['release_state']}` dans "
        "`audit/PDF_ARTIFACT_REGISTRY.yaml` : ils ne sont pas garantis identiques "
        "au contenu courant. Le candidat d'impression courant se reconstruit par "
        f"`{receipt['build_command']}` "
        f"(recu : `audit/1SPE_PRINT_CANDIDATE_BUILD_RECEIPT.json`, statut "
        f"`{receipt['status']}`).",
        "",
        f"Rappel du recu : {receipt['not_final']}",
        "",
        "En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources "
        "du chapitre qui font foi : "
        f"`Mathematiques/manuel-maths/chapitres/{facts['chapter']}/`.",
        "",
    ]
    return lines


def _qcm_human_block(facts: dict[str, Any], index: int) -> list[str]:
    qcm = facts["qcm"]
    lines = [
        f"## {index}. Question de QCM routee vers l'humain",
        "",
    ]
    if not qcm["human"]:
        lines += [
            "Aucune question de ce chapitre n'est routee vers une revue humaine "
            "par `audit/QCM_INDEPENDENT_EVIDENCE_V2.json`.",
            "",
        ]
        return lines
    lines += [
        f"{_plural(len(qcm['human']), 'question')} sur {qcm['count']} n'a pas pu "
        "recevoir de preuve independante de la machine. Elle est reproduite ici "
        "en entier pour qu'elle ne se perde pas dans la masse.",
        "",
    ]
    for question in qcm["human"]:
        lines += [
            f"### `{facts['chapter']}` / `{question['question_id']}` "
            f"(capacite `{question['capacity']}`)",
            "",
            "**Enonce**, reproduit tel quel depuis la source canonique, "
            "notations LaTeX comprises :",
            "",
            f"> {question['statement']}",
            "",
            "**Options proposees**",
            "",
        ]
        for key, value in question["options"]:
            lines.append(f"- **{key}.** {value}")
        lines += [
            "",
            f"**Pourquoi la machine a route vers l'humain** — {question['reason']}",
            "",
            f"- bloquant pour la publication : "
            f"{'oui' if question['release_blocking'] else 'non'} ;",
            f"- source canonique : `{question['source_path']}` ;",
            f"- empreinte semantique de la question : "
            f"`{question['semantic_question_digest']}` ;",
            "- la cle declaree n'est pas reproduite dans cette vue : elle figure "
            "dans la source canonique, et le contrat d'independance du depot "
            "interdit de faire circuler la cle avec l'enonce. Etablissez la "
            "reponse par vous-meme, puis comparez.",
            "",
        ]
    return lines


# --------------------------------------------------------------------------
# vue du role EXPERT_MATHEMATIQUE
# --------------------------------------------------------------------------


def _family_block(facts: dict[str, Any], index: int) -> list[str]:
    families = facts["families"]
    placements = sum(
        len(entries)
        for types in families.values()
        for entries in types.values()
    )
    total = len(
        {
            entry["object_id"]
            for types in families.values()
            for entries in types.values()
            for entry in entries
        }
    )
    lines = [
        f"## {index}. Points d'attention scientifiques, par famille",
        "",
        "Le registre `audit/1SPE_MANUAL_REVIEW_DISPOSITION_LEDGER.json` classe "
        "chaque objet du manuel. Ceux qui portent la disposition "
        f"`{HUMAN_SCIENCE}` contiennent des affirmations calculables qu'aucune "
        "preuve machine n'etablit : ce sont eux que la lecture scientifique doit "
        "atteindre en priorite.",
        "",
        f"{_plural(total, 'objet')} pour ce chapitre, regroupes par famille "
        "scientifique — la capacite du referentiel du depot, avec son libelle BO "
        "— puis par type d'objet.",
        "",
    ]
    if placements != total:
        lines += [
            "Un objet qui declare plusieurs capacites apparait dans plusieurs "
            f"familles : {total} objets distincts pour {placements} "
            "rattachements.",
            "",
        ]
    if not families:
        lines += [
            "Aucun objet de ce chapitre ne porte cette disposition.",
            "",
        ]
        return lines
    by_code = {capacity["code"]: capacity for capacity in facts["capacities"]}
    for code in sorted(families, key=lambda item: (item == RESIDUAL_FAMILY, item)):
        types = families[code]
        entries = [entry for group in types.values() for entry in group]
        claims = sum(int(entry.get("computable_claims") or 0) for entry in entries)
        capacity = by_code.get(code)
        if capacity:
            title = (
                f"### Famille `{code}` — {capacity['libelle_bo'] or capacity['libelle_eleve']}"
            )
            subtitle = f"Capacite eleve : « {capacity['libelle_eleve']} »"
        else:
            title = f"### Famille `{RESIDUAL_FAMILY}`"
            subtitle = (
                "Objets dont ni le META ni l'exercice servi ne declare de "
                "capacite du chapitre. Rien n'est devine ici : la famille reste "
                "a etablir par lecture."
            )
        lines += [
            title,
            "",
            subtitle,
            "",
            f"{_plural(len(entries), 'objet')} · "
            f"{_plural(claims, 'affirmation calculable', 'affirmations calculables')} "
            "sans preuve machine.",
            "",
        ]
        for object_type, group in types.items():
            lines += _type_lines(object_type, group)
        lines.append("")
    return lines


def _type_lines(object_type: str, entries: list[dict[str, Any]]) -> list[str]:
    claims = sum(int(entry.get("computable_claims") or 0) for entry in entries)
    header = (
        f"- **`{object_type}`** — {_plural(len(entries), 'objet')}, "
        f"{_plural(claims, 'affirmation', 'affirmations')} a verifier :"
    )
    if len(entries) > 6:
        directories = sorted(
            {Path(entry["path"]).parent.as_posix() for entry in entries}
        )
        lines = [header, f"    - {compact_ids([e['object_id'] for e in entries])}"]
        for directory in directories:
            lines.append(f"    - repertoire : `{directory}`")
        return lines
    lines = [header]
    for entry in sorted(entries, key=lambda item: item["object_id"]):
        lines.append(
            f"    - `{entry['object_id']}` "
            f"({_plural(int(entry.get('computable_claims') or 0), 'affirmation')}) "
            f"— `{entry['path']}`"
        )
    return lines


def _machine_signals_block(facts: dict[str, Any], index: int) -> list[str]:
    readiness = facts["readiness"]
    if not readiness:
        return []
    oracle = readiness.get("oracle", {})
    programme = readiness.get("programme", {})
    qcm = readiness.get("qcm", {})
    assessments = readiness.get("assessments", {})
    ex_co = readiness.get("ex_co_graph", {})
    classifications = " · ".join(
        f"{key} : {value}"
        for key, value in sorted((ex_co.get("classifications") or {}).items())
    )
    lines = [
        f"## {index}. Ce que la machine a deja etabli, et ce qu'elle n'etablit pas",
        "",
        "Ces mesures viennent de `audit/PUBLISH_READINESS_CHAPTER_MATRIX.json`. "
        "Elles ne reduisent pas le perimetre de votre lecture : une dimension "
        "`COMPLETE` signifie que la machine a fini de mesurer, pas que le contenu "
        "est juste.",
        "",
        "| Mesure | Valeur |",
        "| --- | --- |",
        f"| Etat machine vertical | `{readiness.get('vertical_machine_status')}` |",
        f"| Cloture humaine | `{readiness.get('human_closure_status')}` |",
        f"| Objets passes par l'oracle | {oracle.get('pass', 0)} reussites, "
        f"{oracle.get('fail', 0)} echecs, "
        f"{oracle.get('human_science_required', 0)} en science humaine requise, "
        f"{oracle.get('manual_review', 0)} en revue manuelle |",
        f"| Attendus officiels obligatoires | {programme.get('mapped', 0)} "
        f"rattaches sur {programme.get('mandatory_atoms', 0)}, "
        f"{programme.get('missing', 0)} manquants, "
        f"{programme.get('wrong_year', 0)} hors annee |",
        f"| Sujets d'evaluation | "
        f"{len(assessments.get('subjects', []))} sujets, "
        f"{len(assessments.get('corrections', []))} corriges, "
        f"statut `{assessments.get('status')}` |",
        f"| QCM | {len(qcm.get('question_identities', []))} questions, "
        f"capacites evaluees {', '.join(qcm.get('capacities_assessed', [])) or '—'} |",
        f"| Relation exercice/corrige | {classifications or '—'} ; "
        f"{ex_co.get('cardinality_failures', 0)} echecs de cardinalite |",
        "",
        "La relation exercice/corrige n'est etablie que structurellement : une "
        "COUVERTURE de reponses n'atteste pas qu'un corrige corrige bien son "
        "exercice. Cette fidelite est un point de votre checklist.",
        "",
    ]
    debts = readiness.get("declared_review_debt") or []
    if debts:
        lines += [
            "Dettes de revue declarees pour ce chapitre :",
            "",
        ]
        for debt in sorted(debts, key=lambda item: item["ledger_id"]):
            lines.append(
                f"- `{debt['ledger_id']}` — {_plural(debt['count'], 'unite')}, "
                "categorie "
                f"`{debt['category']}`, bloquant : "
                f"{'oui' if debt.get('release_blocking') else 'non'}."
            )
        lines.append("")
    return lines


def view_expert_mathematique(facts: dict[str, Any], sources: dict[str, Any]) -> str:
    lines: list[str] = []
    lines += _header(facts, ROLE_A)
    lines += _decision_block(facts, ROLE_A)
    lines += _programme_block(facts, ROLE_A)
    lines += _assembly_block(facts)
    lines += _family_block(facts, 4)
    lines += _qcm_human_block(facts, 5)
    lines += _machine_signals_block(facts, 6)
    lines += _checklist_block(ROLE_A, 7)
    lines += _pdf_block(facts, sources, 8)
    lines += _closing(facts, ROLE_A)
    return "\n".join(lines).rstrip("\n") + "\n"


# --------------------------------------------------------------------------
# vue du role EXPERT_PROGRAMME_PEDAGOGIE
# --------------------------------------------------------------------------


def _bareme_block(facts: dict[str, Any], index: int) -> list[str]:
    """Le barème commenté que ce chapitre soumet au jugement.

    Les propositions machine et les items qui demandent un jugement sont
    GROUPÉS par évaluation puis par question, et les deux barèmes GEOREP --
    décision humaine obligatoire -- passent en tête. Les rassembler ailleurs
    reviendrait à demander une signature sur un contenu que le relecteur
    n'aurait pas vu.

    Les formules restent le LaTeX canonique : aucune seconde version textuelle
    n'est fabriquée, et un lecteur Markdown qui rend les mathématiques les
    affiche telles que le manuel les imprime.
    """

    proposal = _load_json(ROOT / "audit/1SPE_BAREME_COMMENTARY_PROPOSAL.json")
    mandatory = _load_json(
        ROOT / "audit/1SPE_ASSESSMENT_BAREME_TRANSCRIPTION.json"
    )
    if proposal is None:
        return []
    chapter = facts["chapter"]
    assessments = [
        row for row in proposal["assessments"] if row["chapter"] == chapter
    ]
    if not assessments:
        return []

    human_ids = {
        row["object_id"]
        for row in (mandatory or {}).get("human_decision_packet", [])
    }
    lines = [
        f"## {index}. Barème commenté — propositions à juger",
        "",
        "La politique est fixée : pour chaque question évaluée, des POINTS, un "
        "ATTENDU ESSENTIEL, et un CRÉDIT PARTIEL seulement lorsqu'une "
        "décomposition objective le justifie. Le corrigé scientifique reste "
        "séparé et complet ; le barème ne le remplace pas.",
        "",
        "Ces propositions sont **machine** et ne valent aucune approbation. "
        "Elles sont le contenu candidat que votre verdict de chapitre couvre.",
        "",
    ]
    # Les décisions obligatoires d'abord.
    ordered = sorted(
        assessments, key=lambda row: (row["object_id"] not in human_ids,)
    )
    for assessment in ordered:
        obligatory = assessment["object_id"] in human_ids
        lines += [
            f"### {assessment['object_id']}"
            + (" — **DÉCISION HUMAINE OBLIGATOIRE**" if obligatory else ""),
            "",
        ]
        if obligatory:
            lines += [
                "Le sujet ne value aucune question individuellement : "
                "répartir son total est un jugement pédagogique, et il vous "
                "revient. Le dossier complet — contraintes du sujet, geste de "
                "raisonnement, indicateurs observables, proposition et sa "
                "justification — est dans "
                "`audit/1SPE_ASSESSMENT_BAREME_TRANSCRIPTION.json`.",
                "",
            ]
        for exercise in assessment["exercises"]:
            waiting = [
                row
                for row in exercise["questions"]
                if row["verdict"] != "PROPOSED"
            ]
            lines += [
                f"**Exercice {exercise['exercise']}** — "
                f"{exercise['declared_total']} points "
                f"({exercise['capacities'] or '—'})"
                + (
                    f" · {len(waiting)} question(s) en attente de jugement"
                    if waiting
                    else ""
                ),
                "",
            ]
            for question in exercise["questions"]:
                if question["verdict"] != "PROPOSED":
                    lines.append(
                        f"- **{question['question']}** — "
                        f"`JUGEMENT PÉDAGOGIQUE REQUIS` : {question['why']}"
                    )
                    continue
                entry = (
                    f"- **{question['question']}** — {question['points']} — "
                    f"Attendu : {question['expected']}."
                )
                if question["partial_credit"]:
                    entry += f" *Crédit partiel : {question['partial_credit']}.*"
                lines.append(entry)
            lines.append("")
    total = sum(
        len(exercise["questions"])
        for assessment in assessments
        for exercise in assessment["exercises"]
    )
    waiting = sum(
        1
        for assessment in assessments
        for exercise in assessment["exercises"]
        for question in exercise["questions"]
        if question["verdict"] != "PROPOSED"
    )
    lines += [
        f"Ce chapitre porte {total} question(s) évaluée(s), dont {waiting} "
        "attendent votre jugement. Ce ne sont pas autant de signatures : votre "
        "verdict porte sur le chapitre.",
        "",
    ]
    return lines


def _capacity_block(facts: dict[str, Any], index: int) -> list[str]:
    cells = facts["cells"]
    capacities = facts["richness"].get("capacities", {})
    total_cells = sum(len(records) for records in cells.values())
    lines = [
        f"## {index}. Capacite par capacite : cellules, contributeurs, richesse",
        "",
        "`audit/SEMANTIC_ALIGNMENT_LEDGER.json` decoupe le manuel en cellules "
        "capacite x role pedagogique. Ce chapitre en porte "
        f"{total_cells}. Elles sont regroupees ici par capacite : une checklist "
        "cellule par cellule ne se lit pas.",
        "",
        f"**Pourquoi ces cellules arrivent chez vous.** {ROUTING_DOCTRINE}",
        "",
        "Chaque capacite rappelle ensuite ce qui lui est propre : le nombre de "
        "cellules, leur disposition, les preuves eventuellement attachees et "
        "l'etat de sa richesse.",
        "",
    ]
    for capacity in facts["capacities"]:
        code = capacity["code"]
        lines += [
            f"### Capacite `{code}` — « {capacity['libelle_eleve']} »",
            "",
        ]
        if capacity["libelle_bo"]:
            lines += [f"Libelle BO : {capacity['libelle_bo']}", ""]
        else:
            lines += [
                f"Libelle BO : {NO_BO_WORDING} "
                f"(`Mathematiques/manuel-maths/referentiel/"
                f"capacites_{facts['chapter'].replace('-', '_')}.json`). "
                "Le contrat du chapitre la declare, le referentiel ne lui donne "
                "aucun attendu officiel : la rattacher au programme fait partie "
                "de votre jugement.",
                "",
            ]
        lines += _capacity_cells(cells.get(code, []))
        lines += _capacity_richness(capacities.get(code, {}))
        lines += _capacity_routing(cells.get(code, []), capacities.get(code, {}))
    return lines


def _capacity_cells(records: list[dict[str, Any]]) -> list[str]:
    if not records:
        return [
            "Aucune cellule capacite x role n'est declaree pour cette capacite.",
            "",
        ]
    lines = [
        "**Roles pedagogiques concernes et objets contributeurs**",
        "",
        "| Role pedagogique | Corps rattaches | Objets contributeurs |",
        "| --- | --- | --- |",
    ]
    for record in records:
        role = record["pedagogical_role"]
        bodies = record["actual_body"]
        identifiers = [
            body.get("question_id") or body["object_id"] for body in bodies
        ]
        lines.append(
            f"| {PEDAGOGICAL_ROLE_LABELS.get(role, role)} | {len(bodies)} | "
            f"{compact_ids(identifiers) or '—'} |"
        )
    lines.append("")
    return lines


def _capacity_richness(richness: dict[str, Any]) -> list[str]:
    if not richness:
        return [
            "Aucune mesure de richesse n'est declaree pour cette capacite dans "
            "`audit/CHAPTER_RICHNESS_MATRIX.json`.",
            "",
        ]
    opportunities = richness.get("opportunities", {})
    rendered = " · ".join(
        f"{key} : {value}" for key, value in sorted(opportunities.items())
    )
    paths = richness.get("reasoning_paths") or []
    lines = [
        "**Richesse declaree**",
        "",
        f"- type de capacite : `{richness.get('capacity_type')}` ; "
        f"occasions distinctes : {richness.get('distinct_opportunities')} ; "
        f"statut declaratif : `{richness.get('declarative_status')}`.",
        f"- occasions existantes : {rendered or '—'}.",
        "- gestes de raisonnement declares : "
        + (
            ", ".join(f"`{path}`" for path in paths) + "."
            if paths
            else "aucun geste distinct declare ; la diversite du raisonnement "
            "est a juger a la lecture."
        ),
        f"- evaluee par : {compact_ids(richness.get('assessed_by') or []) or '—'}.",
    ]
    missing = richness.get("missing_function") or []
    if missing:
        lines.append(
            "- fonctions manquantes declarees : "
            + ", ".join(f"`{item}`" for item in sorted(missing))
            + "."
        )
    lines.append("")
    lines += _difficulty_lines(richness.get("practice") or [])
    return lines


def _difficulty_lines(practice: list[dict[str, Any]]) -> list[str]:
    """La progression de difficulte telle que les parcours la declarent."""

    if not practice:
        return [
            "- progression de difficulte : aucun exercice cible declare.",
            "",
        ]
    by_parcours: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for item in practice:
        by_parcours[item.get("parcours")].append(item)
    lines = ["**Progression de difficulte declaree**", ""]
    for parcours in sorted(by_parcours, key=lambda value: (value is None, value)):
        items = by_parcours[parcours]
        durations = sorted(
            int(item["duree_min"])
            for item in items
            if item.get("duree_min") is not None
        )
        span = (
            f"{durations[0]}–{durations[-1]} min"
            if durations
            else "duree non declaree"
        )
        label = f"parcours {parcours}" if parcours is not None else "parcours non declare"
        lines.append(
            f"- {label} : {_plural(len(items), 'exercice')} ({span}) — "
            f"{compact_ids([item['id'] for item in items])}"
        )
    absent = [level for level in (1, 2, 3) if level not in by_parcours]
    if absent:
        lines.append(
            "- palier sans exercice cible : "
            + ", ".join(f"parcours {level}" for level in absent)
            + "."
        )
    lines.append("")
    return lines


def _capacity_routing(
    records: list[dict[str, Any]], richness: dict[str, Any]
) -> list[str]:
    if not records:
        return []
    dispositions = sorted({r["semantic_alignment"]["disposition"] for r in records})
    evidenced = [r for r in records if r["semantic_alignment"].get("evidence")]
    lines = [
        "**Routage de cette capacite vers l'humain**",
        "",
        f"- les {len(records)} cellules portent "
        + ", ".join(f"`{item}`" for item in dispositions)
        + ".",
    ]
    if evidenced:
        lines.append(
            "- preuves attachees a des cellules de cette capacite : "
            + ", ".join(
                f"`{r['cell_id']}`" for r in sorted(evidenced, key=lambda x: x["cell_id"])
            )
            + "."
        )
    else:
        lines.append(
            "- aucun artefact de preuve ne contredit ces cellules, et aucun "
            "n'atteste non plus qu'elles soient servies."
        )
    if richness:
        lines.append(
            "- richesse : statut `"
            f"{richness.get('status')}`, validation semantique "
            f"`{richness.get('semantic_validation_status')}`."
        )
    lines.append("")
    return lines


def _manual_coherence_block(facts: dict[str, Any], index: int) -> list[str]:
    richness = facts["richness"]
    readiness = facts["readiness"]
    programme = readiness.get("programme", {}) if readiness else {}
    contract = facts["contract"]
    origins = sorted(
        {
            str(item.get("chapitre_origine", "")).strip()
            for item in (contract.get("prerequis") or [])
            if str(item.get("chapitre_origine", "")).strip()
        }
    )
    lines = [
        f"## {index}. Coherence du chapitre et coherence au niveau du manuel",
        "",
        f"- diversite des gestes de raisonnement au niveau du chapitre : "
        f"`{richness.get('diversity_status')}` "
        f"(declaratif : `{richness.get('declarative_diversity_status')}`).",
    ]
    profile = richness.get("diversity_profile") or {}
    if profile:
        lines.append(
            "- profil de diversite declare : "
            + " · ".join(f"{key} : {value}" for key, value in sorted(profile.items()))
            + "."
        )
    else:
        lines.append(
            "- aucun profil de diversite declare pour ce chapitre : les gestes de "
            "raisonnement ne sont pas mesures, ils restent a juger."
        )
    lines += [
        f"- capacites routees vers l'humain : {richness.get('routed_to_human')} sur "
        f"{len(richness.get('capacities') or {})}.",
        f"- attendus officiels obligatoires rattaches : "
        f"{programme.get('mapped', 0)} sur {programme.get('mandatory_atoms', 0)} ; "
        f"manquants : {programme.get('missing', 0)} ; hors annee : "
        f"{programme.get('wrong_year', 0)}.",
    ]
    if origins:
        lines.append(
            "- chapitres dont ce chapitre depend par ses prerequis : "
            + ", ".join(f"`{origin}`" for origin in origins)
            + ". La coherence au niveau du manuel se juge avec eux."
        )
    lines += [
        "",
        "La regle du depot : « la richesse se mesure en occasions distinctes et en "
        "gestes de raisonnement declares ; jamais en nombre de fichiers ».",
        "",
    ]
    return lines


def view_expert_programme(facts: dict[str, Any], sources: dict[str, Any]) -> str:
    lines: list[str] = []
    lines += _header(facts, ROLE_B)
    lines += _decision_block(facts, ROLE_B)
    lines += _programme_block(facts, ROLE_B)
    lines += _assembly_block(facts)
    lines += _capacity_block(facts, 4)
    lines += _qcm_human_block(facts, 5)
    lines += _manual_coherence_block(facts, 6)
    lines += _bareme_block(facts, 7)
    lines += _checklist_block(ROLE_B, 8)
    lines += _pdf_block(facts, sources, 9)
    lines += _closing(facts, ROLE_B)
    return "\n".join(lines).rstrip("\n") + "\n"


def _closing(facts: dict[str, Any], role: str) -> list[str]:
    chapter = facts["chapter"]
    letter = ROLES[role]
    return [
        "---",
        "",
        f"{MENTION_DERIVED} Le packet de ce role est "
        f"`audit/reviews/human/{chapter}/packet-{letter}-{role}.json`. "
        f"{MENTION_DECISION_UNIT}",
        "",
        "Marche a suivre commune aux deux roles : "
        "`audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.",
        "",
    ]


# --------------------------------------------------------------------------
# document commun
# --------------------------------------------------------------------------


def common_document(chapters: list[str]) -> str:
    lines = [
        "# Assignation et instructions de revue — manuel 1SPE",
        "",
        f"> **{MENTION_DERIVED}**",
        "",
        "Ce document est commun aux dix chapitres et aux deux roles. Il ne nomme "
        "personne : les noms humains seront renseignes a l'assignation.",
        "",
        "## 1. Ce qui est decide, et par qui",
        "",
        f"- {MENTION_DECISION_UNIT}",
        f"- rappel porte par chacune des vingt vues : « {MENTION_BASELINE} »",
        "- CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST : l'approbation porte sur "
        "l'empreinte semantique du chapitre, rappelee en tete de chaque vue ; "
        "l'approbation graphique releve de la porte D7, independante.",
        "- Les deux roles sont independants. Un role ne conclut pas pour l'autre.",
        "",
        "## 2. Les deux roles",
        "",
        "| Packet | Role | Objet du jugement |",
        "| --- | --- | --- |",
        f"| A | `{ROLE_A}` | exactitude scientifique du contenu |",
        f"| B | `{ROLE_B}` | conformite au programme et qualite pedagogique |",
        "",
        "## 3. Modele d'assignation",
        "",
        "Un enregistrement d'assignation par (chapitre, role). Les champs "
        "d'identite restent vides tant qu'aucune personne n'est nommee ; ils sont "
        "renseignes hors de cette vue, dans le packet canonique.",
        "",
        "```yaml",
        "assignation:",
        "  manuel: 1SPE",
        "  chapitre: <CHAPITRE>            # un identifiant de la liste ci-dessous",
        "  role: <EXPERT_MATHEMATIQUE | EXPERT_PROGRAMME_PEDAGOGIE>",
        "  packet_canonique: audit/reviews/human/<CHAPITRE>/packet-<A|B>-<ROLE>.json",
        "  vue_de_lecture: audit/reviews/human/<CHAPITRE>/view-<A|B>-<ROLE>.md",
        "  empreinte_ensemble_objets: <object_set_digest du packet>",
        "  empreinte_semantique: <semantic_review_digest du packet>",
        "  etat: PENDING_UNASSIGNED       # inchange tant que personne n'est nommee",
        "  assigne_a: null                # renseigne a l'assignation, hors de cette vue",
        "  assigne_le: null",
        "  rendu_le: null",
        "  verdict: null                  # rendu dans le packet canonique, jamais ici",
        "```",
        "",
        "## 4. Instructions de revue",
        "",
        "1. Lire le chapitre entier dans l'ordre d'assemblage donne par la vue, "
        "PDF a l'appui. Le perimetre est le chapitre courant entier.",
        "2. Traiter la checklist de son role, point par point.",
        "3. Utiliser les listes consolidees de la vue pour diriger l'attention : "
        "objets de science humaine requise pour le role A, cellules capacite x "
        "role et richesse pour le role B. Ces listes ne bornent pas la lecture.",
        "4. Verifier que l'empreinte semantique rappelee par la vue est bien celle "
        "du packet : si le contenu du chapitre a change, le dossier est perime et "
        "la revue doit repartir du gel courant.",
        "5. Consigner chaque constat avec l'identifiant d'objet concerne et le "
        "point de checklist correspondant.",
        "6. Rendre un verdict unique pour le chapitre, dans le packet JSON "
        "canonique. Verdicts autorises : `APPROVED` / `CHANGES_REQUESTED` / "
        "`REJECTED`.",
        "7. Ne rien approuver sur la base de cette vue seule : elle est derivee.",
        "",
        "## 5. Ce qu'une vue ne fait pas",
        "",
        "- elle ne porte aucun verdict ;",
        "- elle ne nomme aucun relecteur et ne cree aucun identifiant de "
        "relecteur ;",
        "- elle ne reduit aucun perimetre ;",
        "- elle ne reproduit pas les cles declarees des QCM : l'expert etablit la "
        "reponse par lui-meme, puis la compare a la source canonique ;",
        "- elle ne remplace jamais le packet JSON canonique.",
        "",
        "## 6. Les vingt dossiers",
        "",
        "| Chapitre | Vue du role A | Vue du role B |",
        "| --- | --- | --- |",
    ]
    for chapter in chapters:
        lines.append(
            f"| `{chapter}` | `audit/reviews/human/{chapter}/"
            f"view-A-{ROLE_A}.md` | `audit/reviews/human/{chapter}/"
            f"view-B-{ROLE_B}.md` |"
        )
    lines += [
        "",
        f"{len(chapters)} chapitres x 2 roles = {len(chapters) * 2} verdicts.",
        "",
    ]
    return "\n".join(lines).rstrip("\n") + "\n"


# --------------------------------------------------------------------------
# assemblage
# --------------------------------------------------------------------------


def load_sources() -> dict[str, Any]:
    semantic = _load_json(SEMANTIC_LEDGER)
    atoms_by_capacity: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for record in semantic["records"]:
        key = (record["chapter"], record["official_capacity"]["local_code"])
        atoms_by_capacity.setdefault(
            key, record["official_capacity"].get("official_atoms") or []
        )
    readiness = _load_json(PUBLISH_READINESS)
    return {
        "assembler": _load_assembler(),
        "disposition": _load_json(DISPOSITION_LEDGER),
        "semantic": semantic,
        "atoms_by_capacity": atoms_by_capacity,
        "richness": _load_json(RICHNESS_MATRIX),
        "readiness_by_chapter": {
            record["chapter"]: record for record in readiness["chapters"]
        },
        "qcm_evidence": _load_json(QCM_EVIDENCE),
        "pdf_registry": _load_json(PDF_REGISTRY),
        "print_receipt": _load_json(PRINT_RECEIPT),
    }


def render_all() -> dict[Path, str]:
    """Le contenu de chaque fichier produit, sans rien ecrire."""

    sources = load_sources()
    chapters = chapter_ids()
    rendered: dict[Path, str] = {}
    for chapter in chapters:
        facts = chapter_facts(chapter, sources)
        rendered[REVIEWS / chapter / f"view-A-{ROLE_A}.md"] = view_expert_mathematique(
            facts, sources
        )
        rendered[REVIEWS / chapter / f"view-B-{ROLE_B}.md"] = view_expert_programme(
            facts, sources
        )
    rendered[COMMON_DOCUMENT] = common_document(chapters)
    return rendered


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="ne rien ecrire ; echouer si une vue sur disque differe",
    )
    args = parser.parse_args(argv)
    rendered = render_all()
    drift = []
    for path, content in sorted(rendered.items()):
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                drift.append(path.relative_to(ROOT).as_posix())
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    if args.check and drift:
        for path in drift:
            print(f"vue perimee : {path}")
        return 1
    if not args.check:
        print(f"{len(rendered)} fichiers ecrits sous audit/reviews/human/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
