#!/usr/bin/env python3
"""Matrice de périmètre des livrables de release, et autorité de chaque exigence.

`DELIVERABLE_SPECS` déclare 28 variantes alors que la release est certifiée sur
12 PDF. Avant d'exiger 28 produits finis, il faut savoir d'où vient chaque
exigence — un script qui attend un fichier n'est pas une autorité.

Chaque spécification cite `MISSION_PRIORITAIRE §8..§11`. **Aucun document de ce
nom n'existe dans le dépôt** : la chaîne a été introduite le 2026-07-20 par
`f5001666 [AUDIT][P0] etablit la source de verite de la collection`. La
substance, elle, est bien traçable : `PROMPT_MISSION_COLLECTION.md` §6 énumère
« les déclinaisons (méthodes, remédiation, livret professeur, version aménagée
NSI, banque ECE) », et `DIRECTIVES_COLLECTION.md` J7 exige « assemblages,
livrets professeur et gates ».

Ce producteur sépare donc deux populations que la certification confondait :

    CANONICAL_MANUAL_TARGETS       les manuels élève/professeur
    REQUIRED_RELEASE_DELIVERABLES  tout ce que le contrat rend obligatoire

Un tableau 12/12 ne doit plus masquer les autres.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GATE_SOURCE = ROOT / "scripts/inventory_collection.py"
INVENTORY = ROOT / "audit/INVENTAIRE_COLLECTION.json"
OUTPUT_JSON = ROOT / "audit/RELEASE_DELIVERABLE_SCOPE_MATRIX.json"
OUTPUT_MD = ROOT / "audit/RELEASE_DELIVERABLE_SCOPE_MATRIX.md"

MISSION = "PROMPT_MISSION_COLLECTION.md#6-budget-et-livrables-finaux"
DIRECTIVES = "DIRECTIVES_COLLECTION.md#J7"
PERIMETER_DOCS = {
    "TCOMPL": "Mathematiques/manuel-maths/docs/11_perimetre_terminale_complementaires.md",
    "TEXPERTES": "Mathematiques/manuel-maths/docs/12_perimetre_terminale_expertes.md",
}
INTRODUCED_AT = "f5001666 (2026-07-20) [AUDIT][P0] etablit la source de verite de la collection"

#: Les quatre manuels couverts par la mission d'origine. TCOMPL et TEXPERTES
#: sont des ajouts ultérieurs, dont les documents de périmètre ne déclarent que
#: les variantes élève et professeur.
MISSION_MANUALS = frozenset({"1SPE", "TSPE_2026_2027", "1NSI", "TNSI"})

CANONICAL_VARIANTS = frozenset({"manuel_eleve", "manuel_professeur"})

#: Assembleur canonique par manuel, et préfixe d'identifiant d'assemblage.
ASSEMBLY_ENGINES = {
    "1SPE": ("math", "Mathematiques/manuel-maths/scripts/assemble_manuel.py"),
    "TSPE_2026_2027": ("math", "Mathematiques/manuel-maths/scripts/assemble_manuel.py"),
    "TCOMPL": ("math", "Mathematiques/manuel-maths/scripts/assemble_manuel.py"),
    "TEXPERTES": ("math", "Mathematiques/manuel-maths/scripts/assemble_manuel.py"),
    "1NSI": ("nsi", "NSI/scripts/assemble_manuel.py"),
    "TNSI": ("nsi", "NSI/scripts/assemble_manuel.py"),
}

#: Variante du livrable telle que la nomme l'assembleur.
VARIANT_ALIAS = {
    "manuel_eleve": "eleve",
    "manuel_professeur": "professeur",
    "livret_methodes": "methodes",
    "livret_remediation": "remediation",
    "remediations": "remediation",
    "version_amenagee": "amenagee",
    "evaluations": "evaluations",
    "livret_evaluations": "evaluations",
    "projets": "projets",
    "banque_evaluations": "evaluations",
    # Ces deux livrables visaient `ece` et `ece_pratique`, des creneaux
    # d'assemblage jamais pourvus. L'epreuve de specialite TNSI n'est pas une
    # ECE : MENE2516123N definit un ecrit de 3 h 30 en trois exercices
    # independants et une epreuve pratique d'une heure. Les deux variantes
    # portent desormais le nom de ce qu'elles assemblent.
    "banque_ecrite": "banque_ecrite",
    "banque_pratique": "banque_pratique",
}

#: Rattachement de chaque variante à la clause qui la rend obligatoire.
#: `None` == aucune clause trouvée : la variante ne devient pas requise parce
#: qu'un script l'attend.
MISSION_CLAUSE = {
    "manuel_eleve": "MANUEL_*_v1.pdf",
    "manuel_professeur": "livret professeur",
    "livret_methodes": "méthodes",
    "livret_remediation": "remédiation",
    "remediations": "remédiation",
    "version_amenagee": "version aménagée NSI",
    "banque_ecrite": "banque ECE",
    "banque_pratique": "banque ECE",
    "evaluations": "banque ECE",
    "banque_evaluations": None,
    "projets": None,
}

#: Variantes propres à NSI dans la clause de mission.
NSI_ONLY_CLAUSES = {"version aménagée NSI", "banque ECE"}
NSI_MANUALS = frozenset({"1NSI", "TNSI"})


def _deliverable_specs() -> dict[str, Any]:
    tree = ast.parse(GATE_SOURCE.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        targets = node.targets if isinstance(node, ast.Assign) else (
            [node.target] if isinstance(node, ast.AnnAssign) else []
        )
        for target in targets:
            if isinstance(target, ast.Name) and target.id == "DELIVERABLE_SPECS":
                return ast.literal_eval(node.value)
    raise SystemExit("DELIVERABLE_SPECS introuvable")


def _classify(manual: str, variant: str) -> dict[str, Any]:
    clause = MISSION_CLAUSE.get(variant, "__missing__")

    if clause == "__missing__":
        return {
            "requirement_status": "UNKNOWN_ORIGIN",
            "source_of_requirement": None,
            "canonical_release_product": False,
            "required_auxiliary_product": False,
            "optional": False,
            "internal_only": False,
            "a_valider_humain": True,
        }

    if manual not in MISSION_MANUALS:
        # TCOMPL / TEXPERTES : autorité = document de périmètre, qui ne déclare
        # que les deux manuels.
        canonical = variant in CANONICAL_VARIANTS
        return {
            "requirement_status": "AUTHORITATIVE_CURRENT_REQUIREMENT" if canonical
            else "PROPOSED_NOT_APPROVED",
            "source_of_requirement": PERIMETER_DOCS.get(manual, "inconnu"),
            "canonical_release_product": canonical,
            "required_auxiliary_product": False,
            "optional": not canonical,
            "internal_only": False,
            "a_valider_humain": not canonical,
        }

    if clause is None:
        # La variante est attendue par le gate mais aucune clause de mission ne
        # la nomme. §8-B : elle ne devient pas requise pour autant.
        return {
            "requirement_status": "PROPOSED_NOT_APPROVED",
            "source_of_requirement": f"{INTRODUCED_AT} (aucune clause de mission correspondante)",
            "canonical_release_product": False,
            "required_auxiliary_product": False,
            "optional": True,
            "internal_only": False,
            "a_valider_humain": True,
        }

    if clause in NSI_ONLY_CLAUSES and manual not in NSI_MANUALS:
        return {
            "requirement_status": "PROPOSED_NOT_APPROVED",
            "source_of_requirement": f"{MISSION} « {clause} » (clause restreinte à NSI)",
            "canonical_release_product": False,
            "required_auxiliary_product": False,
            "optional": True,
            "internal_only": False,
            "a_valider_humain": True,
        }

    canonical = variant in CANONICAL_VARIANTS
    return {
        "requirement_status": "AUTHORITATIVE_CURRENT_REQUIREMENT",
        "source_of_requirement": f"{MISSION} « {clause} »"
        + ("" if canonical else f" ; {DIRECTIVES}"),
        "canonical_release_product": canonical,
        "required_auxiliary_product": not canonical,
        "optional": False,
        "internal_only": False,
        "a_valider_humain": False,
    }


def build() -> dict[str, Any]:
    specs = _deliverable_specs()
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    matrix = inventory.get("deliverable_matrix", {}).get("manuals", {})
    observed = inventory.get("observed_build_coverage", {})
    declared_assemblies = {
        str(a.get("assembly_id"))
        for a in inventory.get("declared_assemblies", [])
        if a.get("scope") == "manual"
    }

    rows: list[dict[str, Any]] = []
    for manual, spec in sorted(specs.items()):
        manual_observed = observed.get(manual, {}) if isinstance(observed, dict) else {}
        variant_coverage = manual_observed.get("variants", {}) if isinstance(manual_observed, dict) else {}
        subject = "NSI" if manual in NSI_MANUALS else "Mathematiques"
        level = "Premiere" if manual.startswith("1") else "Terminale"

        for variant in sorted(spec.get("variants", {})):
            coverage = variant_coverage.get(variant, {}) if isinstance(variant_coverage, dict) else {}
            classification = _classify(manual, variant)
            project, engine = ASSEMBLY_ENGINES.get(manual, (None, None))
            alias = VARIANT_ALIAS.get(variant, variant)
            assembly_id = f"{project}:manual:{manual}:{alias}" if project else None
            rows.append({
                "build_profile": {
                    "engine": engine,
                    "assembly_id": assembly_id,
                    "variant_argument": alias,
                    "output": f"MANUEL_{manual}_{alias}.pdf",
                },
                # Une cible de build existe dès que le moteur sait produire la
                # variante ; un reçu de build est une autre affaire, et il ne
                # doit pas en exister tant que le contenu bouge.
                "build_target_declared": assembly_id in declared_assemblies,
                "deliverable_id": f"{manual}::{variant}",
                "type": "MANUEL" if variant in CANONICAL_VARIANTS else "DECLINAISON",
                "subject": subject,
                "level": level,
                "audience": "professeur" if "professeur" in variant else (
                    "eleve" if "eleve" in variant else "mixte"
                ),
                "format": "PDF",
                "introduced_at": INTRODUCED_AT,
                "cited_authority_in_code": spec.get("directive"),
                "cited_authority_exists_in_repo": False,
                "build_target": variant,
                "expected_output": f"{manual}_{variant}",
                "declared_assembly": assembly_id in declared_assemblies,
                "current_build_receipt": bool(coverage.get("observed_variants")),
                **classification,
            })

    status = Counter(r["requirement_status"] for r in rows)
    canonical = [r for r in rows if r["canonical_release_product"]]
    auxiliary = [r for r in rows if r["required_auxiliary_product"]]
    required = canonical + auxiliary

    summary = {
        "DECLARED_DELIVERABLE_VARIANTS": len(rows),
        "CANONICAL_MANUAL_TARGETS": len(canonical),
        "REQUIRED_RELEASE_DELIVERABLES": len(required),
        "REQUIRED_AUXILIARY_PRODUCTS": len(auxiliary),
        "OPTIONAL_DELIVERABLES": sum(1 for r in rows if r["optional"]),
        "INTERNAL_ONLY_DELIVERABLES": sum(1 for r in rows if r["internal_only"]),
        "UNKNOWN_DELIVERABLE_REQUIREMENT_ORIGIN": status.get("UNKNOWN_ORIGIN", 0),
        "REQUIRED_DELIVERABLES_WITHOUT_ASSEMBLY": sum(
            1 for r in required if not r["declared_assembly"]
        ),
        # Deux notions distinctes. « Sans cible de build » signifie qu'aucun
        # moteur ne sait produire ce livrable — c'est un défaut. « Sans reçu de
        # build courant » est l'état normal tant que le contenu bouge : la
        # gouvernance interdit d'enregistrer des reçus avant le gel de release.
        "REQUIRED_DELIVERABLES_WITHOUT_BUILD_TARGET": sum(
            1 for r in required if not r["build_target_declared"]
        ),
        "REQUIRED_DELIVERABLES_WITHOUT_CURRENT_BUILD_RECEIPT": sum(
            1 for r in required if not r["current_build_receipt"]
        ),
        "CURRENT_BUILD_RECEIPTS_EXPECTED_THIS_PHASE": False,
        "REQUIREMENT_STATUS_COUNTS": dict(status),
        "APPROVES_NOTHING": True,
    }
    return {
        "artifact_type": "release_deliverable_scope_matrix",
        "schema_version": 1,
        "generated_by": "scripts/build_release_deliverable_scope_matrix.py",
        "authority_note": (
            "MISSION_PRIORITAIRE §8..§11 est cité par DELIVERABLE_SPECS mais aucun "
            "document de ce nom n'existe dans le dépôt. Chaque exigence est ici "
            "rattachée à une clause réellement présente, ou déclarée "
            "PROPOSED_NOT_APPROVED."
        ),
        "summary": summary,
        "deliverables": rows,
    }


def render_md(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Matrice de périmètre des livrables de release",
        "",
        payload["authority_note"],
        "",
        f"- `CANONICAL_MANUAL_TARGETS` : `{s['CANONICAL_MANUAL_TARGETS']}`",
        f"- `REQUIRED_RELEASE_DELIVERABLES` : `{s['REQUIRED_RELEASE_DELIVERABLES']}`",
        f"- `REQUIRED_AUXILIARY_PRODUCTS` : `{s['REQUIRED_AUXILIARY_PRODUCTS']}`",
        f"- `OPTIONAL_DELIVERABLES` : `{s['OPTIONAL_DELIVERABLES']}`",
        f"- `UNKNOWN_DELIVERABLE_REQUIREMENT_ORIGIN` : `{s['UNKNOWN_DELIVERABLE_REQUIREMENT_ORIGIN']}`",
        f"- `REQUIRED_DELIVERABLES_WITHOUT_ASSEMBLY` : `{s['REQUIRED_DELIVERABLES_WITHOUT_ASSEMBLY']}`",
        f"- `REQUIRED_DELIVERABLES_WITHOUT_BUILD_TARGET` : "
        f"`{s['REQUIRED_DELIVERABLES_WITHOUT_BUILD_TARGET']}`",
        f"- `REQUIRED_DELIVERABLES_WITHOUT_CURRENT_BUILD_RECEIPT` : "
        f"`{s['REQUIRED_DELIVERABLES_WITHOUT_CURRENT_BUILD_RECEIPT']}` "
        "(attendu tant que le contenu bouge)",
        "",
        "| Livrable | Statut d'exigence | Canonique | Auxiliaire requis | Assemblé | Cible de build |",
        "|---|---|---|---|---|---|",
    ]
    for row in payload["deliverables"]:
        lines.append(
            f"| `{row['deliverable_id']}` | `{row['requirement_status']}` | "
            f"{'oui' if row['canonical_release_product'] else '—'} | "
            f"{'oui' if row['required_auxiliary_product'] else '—'} | "
            f"{'oui' if row['declared_assembly'] else '**non**'} | "
            f"{'oui' if row['build_target_declared'] else '**non**'} |"
        )
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
            print("RELEASE_DELIVERABLE_SCOPE_MATRIX check: OK")
            return 0
        print("RELEASE_DELIVERABLE_SCOPE_MATRIX check: STALE")
        return 1
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
