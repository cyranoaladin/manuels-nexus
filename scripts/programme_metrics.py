#!/usr/bin/env python3
"""Source unique des compteurs de couverture programme.

Un compteur recopie a la main dans un rapport cesse d'etre vrai des que
l'artefact qui le produit bouge, et rien ne le signale : le rapport continue
d'afficher un chiffre juste au moment ou il a ete ecrit. C'est arrive -- un
compte rendu annoncait 918 attendus applicables alors que l'inventaire en
publiait deja 932, l'extraction des preambules de NSI en ayant ajoute
quatorze entre-temps.

Ce module est donc le seul endroit ou un compteur se lit. Chaque metrique
declare l'artefact et le chemin JSON dont elle provient, si bien qu'un rapport
ne peut plus citer un nombre sans citer sa source, et qu'une modification d'un
artefact se propage au rapport suivant sans intervention.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

INVENTORY = "audit/OFFICIAL_PROGRAMME_INVENTORY.json"
BINDING = "audit/OFFICIAL_PROGRAMME_BINDING.json"
DIFF_1SPE = "audit/1SPE_PROGRAMME_DIFF_2019_2026.json"
LIBELLE_GATE = "audit/LIBELLE_BO_AUTHORITY_GATE.json"
COVERAGE = "audit/OFFICIAL_TO_MANUAL_COVERAGE.json"
AUTOMATISMS = "audit/1SPE_AUTOMATISMS_AUDIT.json"
TRANSITION = "audit/1SPE_REFORM_TRANSITION_AUDIT.json"
TNSI = "audit/TNSI_EXAM_PREPARATION_MATRIX.json"
REVERSE = "audit/OBJECTS_TO_OFFICIAL_REVERSE_MAP.json"
MULTIPLE = "audit/MULTIPLE_ASSIGNMENT_RESOLUTION.json"
PREREQUIS = "audit/1SPE_PREREQUISITE_SUPPORT.json"
NORMATIVITE = "audit/NORMATIVITY_PROVENANCE_GATE.json"
REPARATIONS = "audit/DANGLING_CAPACITY_REPAIRS.json"
CONTRE_EXPERTISE = "audit/PROGRAMME_COUNTER_EXPERTISE_REPORT.json"
RECUS_APPROBATION = "audit/CONTENT_APPROVAL_RECEIPTS.json"


@dataclass(frozen=True)
class Metrique:
    """Un compteur, son artefact d'origine et le chemin qui l'y designe."""

    name: str
    artifact: str
    pointer: tuple[str, ...]
    value: Any


def _lire(relatif: str) -> dict[str, Any]:
    return json.loads((ROOT / relatif).read_text(encoding="utf-8"))


def _suivre(charge: dict[str, Any], pointer: tuple[str, ...]) -> Any:
    courant: Any = charge
    for cle in pointer:
        courant = courant[cle]
    return courant


#: Les compteurs canoniques, avec leur provenance. Ajouter une metrique ici
#: suffit a la rendre citable par un rapport ; il n'existe pas d'autre voie.
SOURCES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("CANONICAL_OFFICIAL_ITEMS_APPLICABLE", INVENTORY, ("official_items_applicable",)),
    ("CANONICAL_OFFICIAL_ITEMS_MANDATORY", INVENTORY, ("official_items_mandatory",)),
    ("OFFICIAL_REFERENCES_VERIFIED", INVENTORY, ("OFFICIAL_REFERENCES_VERIFIED",)),
    ("INTERNAL_ATOMS", BINDING, ("summary", "internal_atoms")),
    ("INTERNAL_ATOMS_CONFIRMED_PARENT", BINDING, ("summary", "bound_confirmed")),
    (
        "INTERNAL_ATOMS_CONFIRMED_BY_CONTEXT",
        BINDING,
        ("summary", "bound_by_context"),
    ),
    (
        "INTERNAL_ATOMS_AMBIGUOUS_REQUIRES_HUMAN",
        BINDING,
        ("summary", "ambiguous_requires_human"),
    ),
    ("INTERNAL_ATOMS_UNRESOLVED", BINDING, ("summary", "unbound")),
    (
        "INTERNAL_ATOM_WITHOUT_CONFIRMED_PARENT",
        BINDING,
        ("summary", "INTERNAL_ATOM_WITHOUT_OFFICIAL_PARENT"),
    ),
    ("OFFICIAL_REQUIRED_UNMAPPED", BINDING, ("summary", "OFFICIAL_REQUIRED_UNMAPPED")),
    (
        "OFFICIAL_ITEMS_CLAIMED_BY_SEVERAL_THEMES",
        BINDING,
        ("summary", "UNJUSTIFIED_MULTIPLE_ASSIGNMENT"),
    ),
    (
        "UNJUSTIFIED_MULTIPLE_ASSIGNMENT",
        MULTIPLE,
        ("summary", "UNJUSTIFIED_MULTIPLE_ASSIGNMENT"),
    ),
    (
        "JUSTIFIED_DISTRIBUTED_COVERAGE",
        MULTIPLE,
        ("summary", "JUSTIFIED_DISTRIBUTED_COVERAGE"),
    ),
    (
        "WRONG_YEAR_USED_AS_AUTHORITY",
        BINDING,
        ("summary", "WRONG_YEAR_USED_AS_AUTHORITY"),
    ),
    (
        "AUTHORITY_NAMESPACE_VIOLATION",
        BINDING,
        ("summary", "AUTHORITY_NAMESPACE_VIOLATION"),
    ),
    (
        "REFERENTIAL_AUTHORITY_NOT_EXPLICIT",
        BINDING,
        ("summary", "REFERENTIAL_AUTHORITY_NOT_EXPLICIT"),
    ),
    ("DIFF_1SPE_ADDED_2026_MANDATORY", DIFF_1SPE, ("summary", "ADDED_2026_MANDATORY")),
    (
        "DIFF_1SPE_REMOVED_2026_MANDATORY",
        DIFF_1SPE,
        ("summary", "REMOVED_2026_MANDATORY"),
    ),

    (
        "MISLEADING_LIBELLE_BO_FIELDS_USED_AS_AUTHORITY",
        LIBELLE_GATE,
        ("summary", "MISLEADING_LIBELLE_BO_FIELDS_USED_AS_AUTHORITY"),
    ),
    ("LIBELLE_BO_AUTHORITY_GATE", LIBELLE_GATE, ("summary", "LIBELLE_BO_AUTHORITY_GATE")),
    (
        "OFFICIAL_REQUIRED_COMPLETE",
        COVERAGE,
        ("summary", "OFFICIAL_REQUIRED_COMPLETE"),
    ),
    ("OFFICIAL_REQUIRED_PARTIAL", COVERAGE, ("summary", "OFFICIAL_REQUIRED_PARTIAL")),
    ("OFFICIAL_REQUIRED_MISSING", COVERAGE, ("summary", "OFFICIAL_REQUIRED_MISSING")),
    (
        "OFFICIAL_REQUIRED_INSTITUTIONAL",
        COVERAGE,
        ("summary", "OFFICIAL_REQUIRED_INSTITUTIONAL"),
    ),
    (
        "OFFICIAL_REQUIRED_UNDECIDABLE_BY_CONTENT_MATCH",
        COVERAGE,
        ("summary", "OFFICIAL_REQUIRED_UNDECIDABLE_BY_CONTENT_MATCH"),
    ),
    ("MANUAL_OBJECTS_INDEXED", COVERAGE, ("summary", "objects_indexed")),
    (
        "NEXUS_ALGORITHMIC_QUALITY_PARTS_WITHOUT_WORK",
        COVERAGE,
        ("summary", "NEXUS_ALGORITHMIC_QUALITY_PARTS_WITHOUT_WORK"),
    ),
    (
        "NORMATIVITY_CREATED_BY_ATOMIZATION",
        NORMATIVITE,
        ("summary", "NORMATIVITY_CREATED_BY_ATOMIZATION"),
    ),
    ("MANDATORY_COUNT_BEFORE", NORMATIVITE, ("summary", "MANDATORY_COUNT_BEFORE")),
    ("MANDATORY_COUNT_AFTER", NORMATIVITE, ("summary", "MANDATORY_COUNT_AFTER")),
    (
        "CHANGED_NORMATIVITY_ITEMS",
        NORMATIVITE,
        ("summary", "CHANGED_NORMATIVITY_ITEMS"),
    ),
    (
        "AUTOMATISMS_1SPE_ADEQUATELY_REINVESTED",
        AUTOMATISMS,
        ("summary", "AUTOMATISMS_1SPE_ADEQUATELY_REINVESTED"),
    ),
    (
        "AUTOMATISM_NOT_REINVESTED",
        AUTOMATISMS,
        ("summary", "AUTOMATISM_NOT_REINVESTED"),
    ),
    ("ADDED_2026_TRULY_MISSING", TRANSITION, ("summary", "ADDED_TRULY_MISSING")),
    (
        "REMOVED_2019_CONTENT_STILL_PRESENTED_AS_REQUIRED",
        TRANSITION,
        ("summary", "REMOVED_2019_CONTENT_STILL_PRESENTED_AS_REQUIRED"),
    ),
    (
        "REMOVED_2019_CONTENT_REQUIRING_EDITORIAL_REVIEW",
        TRANSITION,
        ("summary", "REMOVED_2019_CONTENT_REQUIRING_EDITORIAL_REVIEW"),
    ),
    ("TNSI_PROGRAMME_MATRIX", TNSI, ("summary", "TNSI_PROGRAMME_MATRIX")),
    (
        "TNSI_EXAM_PREPARATION_MATRIX",
        TNSI,
        ("summary", "TNSI_EXAM_PREPARATION_MATRIX"),
    ),
    ("EXAM_ONLY_NOTIONS", TNSI, ("summary", "EXAM_ONLY_NOTIONS")),
    (
        "WRITTEN_BANK_SPANS_THE_PROGRAMME",
        TNSI,
        ("summary", "WRITTEN_BANK_SPANS_THE_PROGRAMME"),
    ),
    (
        "PROGRAMME_PARTS_MISSING_FROM_WRITTEN_BANK",
        TNSI,
        ("summary", "PROGRAMME_PARTS_MISSING_FROM_WRITTEN_BANK"),
    ),
    (
        "AUTOMATISMS_BELOW_NEXUS_STANDARD",
        AUTOMATISMS,
        ("summary", "AUTOMATISMS_BELOW_NEXUS_STANDARD"),
    ),
    (
        "PREREQUISITES_ASSUMED_WITHOUT_SUPPORT",
        PREREQUIS,
        ("summary", "PREREQUISITES_ASSUMED_WITHOUT_SUPPORT"),
    ),
    (
        "UNCLASSIFIED_OUT_OF_PROGRAMME_OBJECTS",
        REVERSE,
        ("summary", "UNCLASSIFIED_OUT_OF_PROGRAMME_OBJECTS"),
    ),
    ("FUTURE_PROGRAM_CONTAMINATION", REVERSE, ("summary", "WRONG_YEAR_OBJECTS")),
    (
        "OBJECTS_CITING_AN_UNKNOWN_CAPACITY",
        REVERSE,
        ("summary", "OBJECTS_CITING_AN_UNKNOWN_CAPACITY"),
    ),
    # La contre-expertise : ce que sont devenus les attendus non couverts. Un
    # zero ne dit pas s'il vient d'un manuel complete ou d'une mesure
    # assouplie ; ces compteurs-la le disent.
    (
        "FALSE_MISSING_TOOLING",
        CONTRE_EXPERTISE,
        ("summary", "FALSE_MISSING_TOOLING"),
    ),
    (
        "MISSING_FROM_ASSEMBLY",
        CONTRE_EXPERTISE,
        ("summary", "MISSING_FROM_ASSEMBLY"),
    ),
    ("TRUE_CONTENT_GAP", CONTRE_EXPERTISE, ("summary", "TRUE_CONTENT_GAP")),
    (
        "FALSE_PARTIAL_TOOLING",
        CONTRE_EXPERTISE,
        ("summary", "FALSE_PARTIAL_TOOLING"),
    ),
    (
        "TRUE_PARTIAL_PEDAGOGICAL",
        CONTRE_EXPERTISE,
        ("summary", "TRUE_PARTIAL_PEDAGOGICAL"),
    ),
    # Un compteur unique melangeait trois causes que rien n'oblige a
    # confondre : obligation absente, obligation insuffisamment travaillee, et
    # attendu que la mesure n'avait pas pu chercher. Plus l'enrichissement, qui
    # ne repond a aucune obligation.
    (
        "CONTENT_CREATED_FOR_TRUE_MISSING",
        CONTRE_EXPERTISE,
        ("summary", "CONTENT_CREATED_FOR_TRUE_MISSING"),
    ),
    (
        "CONTENT_CREATED_FOR_TRUE_PARTIAL_PEDAGOGICAL",
        CONTRE_EXPERTISE,
        ("summary", "CONTENT_CREATED_FOR_TRUE_PARTIAL_PEDAGOGICAL"),
    ),
    (
        "CONTENT_CREATED_AFTER_UNDECIDABLE_REVIEW",
        CONTRE_EXPERTISE,
        ("summary", "CONTENT_CREATED_AFTER_UNDECIDABLE_REVIEW"),
    ),
    (
        "CONTENT_CREATED_FOR_NEXUS_QUALITY_ENRICHMENT",
        CONTRE_EXPERTISE,
        ("summary", "CONTENT_CREATED_FOR_NEXUS_QUALITY_ENRICHMENT"),
    ),
    (
        "STALE_APPROVAL_AFTER_SEMANTIC_EDIT",
        RECUS_APPROBATION,
        ("summary", "STALE_APPROVAL_AFTER_SEMANTIC_EDIT"),
    ),
    (
        "SEMANTIC_CHANGE_PRESERVES_OLD_HUMAN_APPROVAL",
        RECUS_APPROBATION,
        ("summary", "SEMANTIC_CHANGE_PRESERVES_OLD_HUMAN_APPROVAL"),
    ),
    (
        "SEMANTIC_CHANGE_INVALIDATES_REVIEW_RECEIPT",
        RECUS_APPROBATION,
        ("summary", "SEMANTIC_CHANGE_INVALIDATES_REVIEW_RECEIPT"),
    ),
    (
        "INVALIDATED_APPROVALS_AWAITING_HUMAN_REVIEW",
        RECUS_APPROBATION,
        ("summary", "INVALIDATED_APPROVALS_AWAITING_HUMAN_REVIEW"),
    ),
    (
        "NEXUS_ALGORITHMIC_QUALITY_PARTS_WITHOUT_WORK",
        COVERAGE,
        ("summary", "NEXUS_ALGORITHMIC_QUALITY_PARTS_WITHOUT_WORK"),
    ),
)


def canonical_metrics() -> dict[str, Metrique]:
    caches: dict[str, dict[str, Any]] = {}
    metriques: dict[str, Metrique] = {}
    for nom, artefact, pointer in SOURCES:
        charge = caches.setdefault(artefact, _lire(artefact))
        metriques[nom] = Metrique(
            name=nom,
            artifact=artefact,
            pointer=pointer,
            value=_suivre(charge, pointer),
        )
    return metriques


def value(nom: str) -> Any:
    return canonical_metrics()[nom].value


if __name__ == "__main__":
    for metrique in canonical_metrics().values():
        chemin = " / ".join(metrique.pointer)
        print(f"{metrique.name:42s} = {metrique.value}")
        print(f"{'':44s}({metrique.artifact} :: {chemin})")
