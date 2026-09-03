#!/usr/bin/env python3
"""Contrat des notes de marge 1SPE : ce qui doit se voir doit être dessiné.

Le compositeur CAPTURE des notes de marge et, dans la construction de
production, n'en DESSINE aucune : 952 côté élève, 3 038 côté professeur, zéro
rendue. Un contenu attendu mais jamais affiché est une perte silencieuse, et
elle ne se voit dans aucun journal.

Ce producteur établit d'abord le contrat, classe par classe, avant toute
correction. Pour chaque rôle de note :

* le producteur qui l'émet, cité par son fichier et sa ligne ;
* son rôle pédagogique ;
* sa visibilité attendue ;
* la variante à laquelle elle s'applique ;
* son consommateur d'assemblage.

La partition est fermée : `EXPECTED_VISIBLE_MARGIN_CONTENT`,
`NON_RENDERING_INTERNAL_ANCHOR`, `OBSOLETE`, `UNKNOWN`. `UNKNOWN` doit valoir
zéro — un rôle observé dans un journal sans être déclaré ici rend le contrat
incomplet, et le dit.

La classe n'est jamais déduite du mot « note de marge » : elle vient du
producteur, du cahier des charges et de la charte, cités dans l'artefact.

Puis le producteur MESURE, sur les PDF construits : combien de notes de chaque
rôle sont capturées, combien sont réellement dessinées, et combien ont disparu
en silence.

Métriques bloquantes : `UNKNOWN_ROLES`, `SILENTLY_DROPPED_MARGIN_ITEMS`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT, relative  # noqa: E402

JSON_TARGET = ROOT / "audit/1SPE_MARGIN_CONTENT_CONTRACT.json"
MD_TARGET = ROOT / "audit/1SPE_MARGIN_CONTENT_CONTRACT.md"
GENERATED_BY = "scripts/build_1spe_margin_content_contract.py"

BUILD = ROOT / "Mathematiques/manuel-maths/build/MANUEL_1SPE"
VARIANTS = ("eleve", "professeur")

EXPECTED_VISIBLE = "EXPECTED_VISIBLE_MARGIN_CONTENT"
INTERNAL_ANCHOR = "NON_RENDERING_INTERNAL_ANCHOR"
OBSOLETE = "OBSOLETE"
UNKNOWN = "UNKNOWN"

CAPTURE = re.compile(r"NEXUS-MARGIN-CAPTURE:nxm:([a-z]+):([a-z-]+):(\d{8})")

# Le contrat, classe par classe. Chaque ligne cite le producteur qui l'émet :
# la classe se lit dans le code qui la fabrique, pas dans son nom.
CONTRACT: tuple[dict[str, Any], ...] = (
    {
        "role": "appui",
        "producer": "gabarits/common/nexus-manuel.cls:245 — \\margeAppui",
        "pedagogical_role": (
            "note d'appui : un rappel court qui accompagne le texte courant "
            "sans l'interrompre"
        ),
        "expected_visibility": "VISIBLE",
        "applies_to": ["eleve", "professeur"],
        "assembly_consumer": "corps de chapitre (cours, méthodes, exercices)",
        "classification": EXPECTED_VISIBLE,
        "authority": (
            "AGENTS.md — « Les notes marginales doivent avoir un fallback dans "
            "le flux principal » : une note de marge est du contenu affiché, "
            "sinon la question du repli ne se poserait pas"
        ),
    },
    {
        "role": "commentaire",
        "producer": "gabarits/common/nexus-manuel.cls:249 — \\commentaireMarge",
        "pedagogical_role": (
            "commentaire de marge : une remarque de l'auteur sur le passage "
            "en regard"
        ),
        "expected_visibility": "VISIBLE",
        "applies_to": ["eleve", "professeur"],
        "assembly_consumer": "corps de chapitre",
        "classification": EXPECTED_VISIBLE,
        "authority": "même autorité que la note d'appui",
    },
    {
        "role": "vocab",
        "producer": "gabarits/common/nexus-manuel.cls:255 — \\margeVocab",
        "pedagogical_role": "définition de vocabulaire en marge",
        "expected_visibility": "VISIBLE",
        "applies_to": ["eleve", "professeur"],
        "assembly_consumer": "corps de chapitre",
        "classification": EXPECTED_VISIBLE,
        "authority": "même autorité que la note d'appui",
    },
    {
        "role": "chrono",
        "producer": (
            "gabarits/common/nexus-manuel.cls:433 — environnement exercice, "
            "durée estimée"
        ),
        "pedagogical_role": (
            "durée estimée de l'exercice, en regard de son énoncé : l'élève "
            "s'en sert pour organiser son travail"
        ),
        "expected_visibility": "VISIBLE",
        "applies_to": ["eleve", "professeur"],
        "assembly_consumer": "environnement exercice",
        "classification": EXPECTED_VISIBLE,
        "authority": (
            "docs/01_conception_manuel.md — les parcours annoncent un temps ; "
            "la durée par exercice est ce qui rend ce temps opérationnel"
        ),
    },
    {
        "role": "professor-id",
        "producer": (
            "gabarits/common/nexus-manuel.cls:436 et :448 — exercice et "
            "corrigé, sous \\ifnxVersionProfesseur"
        ),
        "pedagogical_role": (
            "identifiant interne de l'objet, en marge du manuel professeur : "
            "il relie la page imprimée à la source et sert la correction"
        ),
        "expected_visibility": "VISIBLE",
        "applies_to": ["professeur"],
        "assembly_consumer": "environnements exercice et corrigé",
        "classification": EXPECTED_VISIBLE,
        "authority": (
            "AGENTS.md — « La version élève ne doit contenir aucun "
            "identifiant interne 1SPE-* visible » : l'interdiction ne vise que "
            "l'élève, et la garde \\ifnxVersionProfesseur la respecte"
        ),
    },
)

BY_ROLE = {entry["role"]: entry for entry in CONTRACT}


class ContractError(RuntimeError):
    """Une preuve manque : le contrat ne peut pas être établi."""


def _reject(message: str) -> None:
    raise ContractError(message)


def captured_by_role(variant: str) -> dict[str, int]:
    log = BUILD / f"MANUEL_1SPE_{variant}.log"
    if not log.is_file():
        _reject(f"journal absent : {relative(log)}")
    counts: dict[str, int] = {}
    seen: set[str] = set()
    for match in CAPTURE.finditer(log.read_text(encoding="utf-8", errors="replace")):
        _emitted_variant, role, order = match.groups()
        key = f"{role}:{order}"
        if key in seen:
            continue
        seen.add(key)
        counts[role] = counts.get(role, 0) + 1
    return counts


def rendered_by_role(variant: str) -> dict[str, int]:
    """Les notes réellement dessinées, lues dans le PDF.

    Chaque note rendue est un Form XObject marqué `/NXMarginID` et
    `/NXMarginRole` : c'est le compositeur lui-même qui les étiquette, donc le
    comptage ne dépend d'aucune heuristique sur le texte.
    """

    try:
        import pikepdf
    except ModuleNotFoundError:  # pragma: no cover - dependance de gate
        _reject("pikepdf est requis pour compter les notes rendues")
    pdf = BUILD / f"MANUEL_1SPE_{variant}.pdf"
    if not pdf.is_file():
        _reject(f"PDF absent : {relative(pdf)}")
    counts: dict[str, int] = {}
    seen: set[str] = set()
    with pikepdf.Pdf.open(pdf) as document:
        for page in document.pages:
            resources = page.obj.get("/Resources") or {}
            xobjects = resources.get("/XObject") or {}
            for name in xobjects:
                form = xobjects[name]
                if "/NXMarginID" not in form:
                    continue
                identifier = str(form["/NXMarginID"])
                if identifier in seen:
                    continue
                seen.add(identifier)
                role = str(form.get("/NXMarginRole", "")).strip("()")
                counts[role] = counts.get(role, 0) + 1
    return counts


def build() -> dict[str, Any]:
    variants = []
    unknown_roles: set[str] = set()
    for variant in VARIANTS:
        captured = captured_by_role(variant)
        rendered = rendered_by_role(variant)
        rows = []
        for role in sorted(set(captured) | set(rendered)):
            entry = BY_ROLE.get(role)
            if entry is None:
                unknown_roles.add(role)
            classification = entry["classification"] if entry else UNKNOWN
            expected_visible = (
                classification == EXPECTED_VISIBLE
                and (entry is None or variant in entry["applies_to"])
            )
            captured_count = captured.get(role, 0)
            rendered_count = rendered.get(role, 0)
            rows.append(
                {
                    "role": role,
                    "classification": classification,
                    "captured": captured_count,
                    "rendered": rendered_count,
                    "expected_visible_here": expected_visible,
                    "silently_dropped": (
                        max(0, captured_count - rendered_count)
                        if expected_visible
                        else 0
                    ),
                }
            )
        variants.append(
            {
                "variant": variant,
                "roles": rows,
                "CAPTURED": sum(row["captured"] for row in rows),
                "RENDERED": sum(row["rendered"] for row in rows),
                "EXPECTED_VISIBLE_MARGIN_ITEMS": sum(
                    row["captured"] for row in rows if row["expected_visible_here"]
                ),
                "RENDERED_VISIBLE_MARGIN_ITEMS": sum(
                    row["rendered"] for row in rows if row["expected_visible_here"]
                ),
                "SILENTLY_DROPPED_MARGIN_ITEMS": sum(
                    row["silently_dropped"] for row in rows
                ),
            }
        )
    return {
        "artifact_type": "1spe_margin_content_contract",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "partition_is_closed": [
            EXPECTED_VISIBLE,
            INTERNAL_ANCHOR,
            OBSOLETE,
            UNKNOWN,
        ],
        "class_is_read_from_the_producer_not_the_name": True,
        "contract": list(CONTRACT),
        "variants": variants,
        "summary": {
            "DECLARED_ROLES": len(CONTRACT),
            "UNKNOWN_ROLES": len(unknown_roles),
            "unknown_roles": sorted(unknown_roles),
            "EXPECTED_VISIBLE_MARGIN_ITEMS": sum(
                row["EXPECTED_VISIBLE_MARGIN_ITEMS"] for row in variants
            ),
            "RENDERED_VISIBLE_MARGIN_ITEMS": sum(
                row["RENDERED_VISIBLE_MARGIN_ITEMS"] for row in variants
            ),
            "SILENTLY_DROPPED_MARGIN_ITEMS": sum(
                row["SILENTLY_DROPPED_MARGIN_ITEMS"] for row in variants
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Contrat des notes de marge — 1SPE",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        "Partition fermée : "
        + ", ".join(f"`{name}`" for name in payload["partition_is_closed"])
        + ".",
        "",
        "## Métriques",
        "",
        "| Métrique | Valeur |",
        "|---|---:|",
    ]
    for name, value in payload["summary"].items():
        if isinstance(value, list):
            continue
        lines.append(f"| `{name}` | {value} |")
    lines += [
        "",
        "## Contrat, classe par classe",
        "",
        "| Rôle | Classe | Visibilité | Variantes | Producteur |",
        "|---|---|---|---|---|",
    ]
    for entry in payload["contract"]:
        lines.append(
            f"| `{entry['role']}` | {entry['classification']} | "
            f"{entry['expected_visibility']} | "
            f"{', '.join(entry['applies_to'])} | `{entry['producer']}` |"
        )
    for entry in payload["contract"]:
        lines += [
            "",
            f"### `{entry['role']}`",
            "",
            f"- rôle pédagogique : {entry['pedagogical_role']}",
            f"- consommateur d'assemblage : {entry['assembly_consumer']}",
            f"- autorité : {entry['authority']}",
        ]
    for row in payload["variants"]:
        lines += [
            "",
            f"## Variante `{row['variant']}`",
            "",
            "| Rôle | Classe | Capturées | Rendues | Perdues en silence |",
            "|---|---|---:|---:|---:|",
        ]
        for entry in row["roles"]:
            lines.append(
                f"| `{entry['role']}` | {entry['classification']} | "
                f"{entry['captured']} | {entry['rendered']} | "
                f"{entry['silently_dropped']} |"
            )
        lines.append(
            f"\n**{row['RENDERED_VISIBLE_MARGIN_ITEMS']} / "
            f"{row['EXPECTED_VISIBLE_MARGIN_ITEMS']}** notes attendues visibles "
            f"sont dessinées."
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ne rien écrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build()
    except ContractError as error:
        print(f"1SPE-MARGIN-CONTRACT-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"écrit {relative(JSON_TARGET)} et {relative(MD_TARGET)}")
    for name, value in payload["summary"].items():
        if not isinstance(value, list):
            print(f"{name}={value}")
    blocking = ("UNKNOWN_ROLES", "SILENTLY_DROPPED_MARGIN_ITEMS")
    return 1 if any(payload["summary"][name] for name in blocking) else 0


if __name__ == "__main__":
    raise SystemExit(main())
