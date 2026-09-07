#!/usr/bin/env python3
"""Classe chaque bloqueur de build sur PREUVE, et non sur son libellé.

Quarante motifs de la taxonomie disaient `PRODUCT_P1` : « variante déclarée
jamais construite », « livrable déclaré non compilé ». Or les vingt-quatre
livrables ont un build de développement qui existe, s'ouvre et porte du texte.
Ce que ces motifs constatent réellement, c'est qu'aucun REÇU DE BUILD FINAL
n'a été intégré — et le protocole interdit précisément d'en produire un avant
le gel. Un blocage produit qu'aucun travail produit ne peut lever n'est pas un
blocage produit : c'est une exigence de certification.

Ce producteur tranche motif par motif, sur quatre constats recalculés :

`DEVELOPMENT_BUILD_EXISTS`
    le PDF que le moteur d'assemblage nommerait existe sur le disque ;

`DEVELOPMENT_BUILD_PASS`
    il s'ouvre, porte au moins une page et du texte extractible ;

`FINAL_RELEASE_RECEIPT_EXISTS`
    un reçu de build est intégré à l'inventaire pour cette variante ;

`CLASSIFICATION`
    `DEVELOPMENT_BUILD` si le build de développement manque ou échoue — cela
    reste un blocage produit, que du travail produit peut lever ;
    `FINAL_RELEASE_BUILD_EVIDENCE` s'il passe et que seul le reçu final
    manque — cela relève de la certification, et attend le gel.

Reclassifier sur preuve, jamais pour réduire un compte : un livrable sans
build de développement valide reste `PRODUCT_P1`, et le dirait.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import build_development_ready_independent_recheck as recheck  # noqa: E402
import evidence_freshness as freshness  # noqa: E402

INVENTORY = ROOT / "audit/INVENTAIRE_COLLECTION.json"
RAW_REASONS = ROOT / "audit/RELEASE_RAW_REASONS.json"
SCOPE = ROOT / "audit/RELEASE_DELIVERABLE_SCOPE_MATRIX.json"
OUTPUT_JSON = ROOT / "audit/BUILD_BLOCKER_CLASSIFICATION.json"
OUTPUT_MD = ROOT / "audit/BUILD_BLOCKER_CLASSIFICATION.md"

#: Racines de build, avant et après reclassification. Les deux premières sont
#: celles que le gate produit ; les trois suivantes celles que la preuve
#: assigne. Le rapport doit voir les deux, sans quoi il perdrait de vue les
#: motifs le jour où la taxonomie les a déjà rangés.
BUILD_ROOTS = (
    "ROOT-DELIVERABLE-NOT-BUILT",
    "ROOT-DELIVERABLE-NOT-COMPILED",
    "ROOT-DEVELOPMENT-BUILD-MISSING",
    "ROOT-FINAL-RELEASE-BUILD-EVIDENCE",
    "ROOT-OPTIONAL-DELIVERABLE-NOT-APPROVED",
)

NOT_BUILT = re.compile(r"^(?P<manual>[A-Z0-9_]+):build_observé_absent:(?P<variant>.+)$")
NOT_COMPILED = re.compile(
    r"^(?P<manual>[A-Z0-9_]+):livrable_non_compile:"
    r"deliverable_matrix\.(?P=manual)\.variants\.(?P<variant>[^:]+):(?P<detail>.*)$"
)

DEVELOPMENT_BUILD = "DEVELOPMENT_BUILD"
FINAL_RELEASE_BUILD_EVIDENCE = "FINAL_RELEASE_BUILD_EVIDENCE"
OPTIONAL_NOT_APPROVED = "OPTIONAL_DELIVERABLE_NOT_APPROVED"

#: Taxonomie qu'appelle chaque classification. Un blocage que du travail
#: produit peut lever reste produit ; un blocage qui attend le gel relève de
#: la certification ; un livrable seulement PROPOSÉ relève du périmètre.
TAXONOMY = {
    DEVELOPMENT_BUILD: "PRODUCT_P1",
    FINAL_RELEASE_BUILD_EVIDENCE: "CERTIFICATION_BLOCKER",
    OPTIONAL_NOT_APPROVED: "RELEASE_POLICY_BLOCKER",
}


def _deliverable_scope() -> dict[tuple[str, str], dict[str, Any]]:
    """(manuel, nom de livrable) -> variante d'assemblage et statut de périmètre."""
    scope = json.loads(SCOPE.read_text(encoding="utf-8"))
    table: dict[tuple[str, str], dict[str, Any]] = {}
    for entree in scope["deliverables"]:
        manuel, livrable = str(entree["deliverable_id"]).split("::", 1)
        table[(manuel, livrable)] = {
            "variant": str(entree["build_profile"]["variant_argument"]),
            "required": bool(
                entree.get("canonical_release_product")
                or entree.get("required_auxiliary_product")
            ),
            "optional": bool(entree.get("optional")),
            "requirement_status": entree.get("requirement_status"),
        }
    return table


def _observed_receipts() -> dict[tuple[str, str], bool]:
    """(manuel, livrable) -> un reçu de build est-il intégré ?"""
    inventaire = json.loads(INVENTORY.read_text(encoding="utf-8"))
    couverture = inventaire.get("observed_build_coverage") or {}
    presence: dict[tuple[str, str], bool] = {}
    for manuel, valeur in couverture.items():
        for livrable, detail in (valeur.get("variants") or {}).items():
            presence[(manuel, livrable)] = bool(detail.get("observed_variants"))
    return presence


def parse_build_reason(evidence: str) -> tuple[str, str] | None:
    """(manuel, livrable) d'un motif de build, ou `None` si ce n'en est pas un."""
    correspondance = NOT_BUILT.match(evidence) or NOT_COMPILED.match(evidence)
    if correspondance is None:
        return None
    return correspondance.group("manual"), correspondance.group("variant")


def classification_for(manuel: str, livrable: str) -> dict[str, Any]:
    """Les quatre constats et la classification, recalculés depuis le disque.

    Cette fonction ne lit PAS la taxonomie : elle en est la source. C'est ce
    qui permet au producteur de motifs bruts de l'appeler sans créer de cycle,
    et à ce rapport de comparer ensuite ce que la taxonomie déclare à ce que
    la preuve établit.
    """
    entree_perimetre = _deliverable_scope().get((manuel, livrable))
    if entree_perimetre is None:
        raise ValueError(f"livrable inconnu du périmètre : {manuel}::{livrable}")
    variante = entree_perimetre["variant"]
    pdf = recheck._engine_pdf_path(manuel, variante)
    preuve = recheck._pdf_evidence(pdf)
    existe = pdf.is_file()
    passe = bool(preuve.get("verdict"))
    recu = _observed_receipts().get((manuel, livrable), False)

    if not entree_perimetre["required"]:
        # Un livrable seulement PROPOSÉ n'est pas dû : l'absence de son build
        # ne peut pas être une dette produit. C'est le raisonnement déjà rendu
        # sur les banques d'évaluation facultatives ; il est ici constaté, et
        # la ligne dit son statut de périmètre pour que ce soit lisible.
        classification = OPTIONAL_NOT_APPROVED
    elif existe and passe and not recu:
        classification = FINAL_RELEASE_BUILD_EVIDENCE
    else:
        classification = DEVELOPMENT_BUILD

    return {
        "manual": manuel,
        "deliverable": livrable,
        "variant": variante,
        "required": entree_perimetre["required"],
        "optional": entree_perimetre["optional"],
        "requirement_status": entree_perimetre["requirement_status"],
        "DEVELOPMENT_BUILD_EXISTS": existe,
        "DEVELOPMENT_BUILD_PASS": passe,
        "FINAL_RELEASE_RECEIPT_EXISTS": recu,
        "CLASSIFICATION": classification,
        "expected_taxonomy": TAXONOMY[classification],
        "development_build": preuve,
    }


def classify() -> list[dict[str, Any]]:
    reasons = json.loads(RAW_REASONS.read_text(encoding="utf-8"))
    lignes: list[dict[str, Any]] = []

    for reason in reasons["raw_reasons"]:
        if reason.get("root_cause_id") not in BUILD_ROOTS:
            continue
        evidence = str(reason.get("evidence", ""))
        couple = parse_build_reason(evidence)
        if couple is None:
            raise ValueError(f"motif de build non reconnu : {evidence}")
        manuel, livrable = couple
        lignes.append(dict(
            classification_for(manuel, livrable),
            reason_id=reason["reason_id"],
            declared_taxonomy=reason.get("category"),
        ))

    lignes.sort(key=lambda ligne: (ligne["manual"], ligne["deliverable"]))
    return lignes


def build() -> dict[str, Any]:
    lignes = classify()
    developpement = [
        ligne for ligne in lignes if ligne["CLASSIFICATION"] == DEVELOPMENT_BUILD
    ]
    finaux = [
        ligne for ligne in lignes
        if ligne["CLASSIFICATION"] == FINAL_RELEASE_BUILD_EVIDENCE
    ]
    optionnels = [
        ligne for ligne in lignes
        if ligne["CLASSIFICATION"] == OPTIONAL_NOT_APPROVED
    ]
    mal_classes = [
        ligne for ligne in lignes
        if ligne.get("expected_taxonomy")
        and ligne["declared_taxonomy"] != ligne["expected_taxonomy"]
    ]
    resume = {
        "BUILD_REASONS_TOTAL": len(lignes),
        "DEVELOPMENT_BUILD_BLOCKERS": len(developpement),
        "FINAL_RELEASE_BUILD_EVIDENCE_BLOCKERS": len(finaux),
        "OPTIONAL_NOT_APPROVED_BLOCKERS": len(optionnels),
        "BUILD_BLOCKER_MISCLASSIFICATION": len(mal_classes),
        "CLASSES_SUM_EQUALS_TOTAL": (
            len(developpement) + len(finaux) + len(optionnels) == len(lignes)
        ),
        "APPROVES_NOTHING": True,
    }
    return {
        "artifact_type": "build_blocker_classification",
        "schema_version": 1,
        "generated_by": "scripts/build_build_blocker_classification.py",
        "authority_note": (
            "Reclassification sur preuve : un livrable sans build de "
            "développement valide reste un blocage produit. Aucun reçu de "
            "build final n'est produit ici."
        ),
        "summary": resume,
        "misclassified_reason_ids": [ligne["reason_id"] for ligne in mal_classes],
        "reasons": lignes,
        "freshness": freshness.stamp(
            ["audit/RELEASE_RAW_REASONS.json", "audit/INVENTAIRE_COLLECTION.json",
             "audit/RELEASE_DELIVERABLE_SCOPE_MATRIX.json"],
            root=ROOT,
        ),
    }


def render_md(payload: dict[str, Any]) -> str:
    resume = payload["summary"]
    lignes = [
        "# Classification des bloqueurs de build",
        "",
        "Un blocage que du travail produit peut lever reste produit ; un",
        "blocage qui attend le gel relève de la certification.",
        "",
        f"- `DEVELOPMENT_BUILD_BLOCKERS` : `{resume['DEVELOPMENT_BUILD_BLOCKERS']}`",
        f"- `FINAL_RELEASE_BUILD_EVIDENCE_BLOCKERS` : "
        f"`{resume['FINAL_RELEASE_BUILD_EVIDENCE_BLOCKERS']}`",
        f"- `BUILD_BLOCKER_MISCLASSIFICATION` : "
        f"`{resume['BUILD_BLOCKER_MISCLASSIFICATION']}`",
        "",
        "| Manuel | Livrable | Build dev | Passe | Reçu final | Classification |",
        "|---|---|---|---|---|---|",
    ]
    for ligne in payload["reasons"]:
        marque = lambda valeur: "oui" if valeur else "**non**"  # noqa: E731
        lignes.append(
            f"| {ligne['manual']} | {ligne['deliverable']} | "
            f"{marque(ligne['DEVELOPMENT_BUILD_EXISTS'])} | "
            f"{marque(ligne['DEVELOPMENT_BUILD_PASS'])} | "
            f"{marque(ligne['FINAL_RELEASE_RECEIPT_EXISTS'])} | "
            f"{ligne['CLASSIFICATION']} |"
        )
    lignes.append("")
    return "\n".join(lignes)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    payload = build()
    rendu = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if arguments.check:
        if OUTPUT_JSON.is_file() and OUTPUT_JSON.read_text(encoding="utf-8") == rendu:
            print("BUILD_BLOCKER_CLASSIFICATION check: OK")
            return 0
        print("BUILD_BLOCKER_CLASSIFICATION check: STALE")
        return 1
    OUTPUT_JSON.write_text(rendu, encoding="utf-8")
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
