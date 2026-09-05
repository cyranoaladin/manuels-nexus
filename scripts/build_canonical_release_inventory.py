#!/usr/bin/env python3
"""Prouver que « six manuels » veut dire six, et que rien d'autre ne se publie.

L'asymetrie qui a laisse passer onze mille guillemets courbes dans le code NSI
n'etait pas une erreur de mesure : c'etait un perimetre. Un manuel etait tenu
sous controle, cinq autres vivaient a cote sans que rien ne les regarde. Un
inventaire qui se contente de reciter la liste attendue ne protege de rien --
il repete l'angle mort au lieu de le fermer.

Ce module part donc du DEPOT, pas du registre. Il cherche toutes les racines
TeX, tous les repertoires de build, tous les PDF, toutes les variantes que les
assembleurs savent produire, et confronte cette recolte au registre canonique.
Chaque cible trouvee doit tomber dans l'une des deux familles, jamais entre les
deux : `CANONICAL_RELEASE_TARGET`, ou `EXPLICITLY_NON_RELEASE` avec un motif
structure.

Une cible que personne n'a classee est bloquante. C'est exactement la forme
qu'avait le defaut : quelque chose qui existe, que rien ne declare, et que
personne ne regarde.

Metriques bloquantes : `UNREGISTERED_RELEASE_TARGET`,
`MISSING_CANONICAL_TARGET`, `AMBIGUOUS_CURRENT_ARTIFACT`, `UNKNOWN`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT  # noqa: E402

JSON_TARGET = ROOT / "audit/CANONICAL_RELEASE_INVENTORY.json"
MD_TARGET = ROOT / "audit/CANONICAL_RELEASE_INVENTORY.md"
GENERATED_BY = "scripts/build_canonical_release_inventory.py"

COLLECTION_STATE = ROOT / "ETAT_COLLECTION_2026_2027.json"
PUBLICATION_DIR = ROOT / "MANUELS_PDF_PUBLICATION"

#: Les deux variantes qui se publient. Les assembleurs savent en produire
#: d'autres ; elles ne sont pas des cibles de release.
RELEASE_VARIANTS = ("eleve", "professeur")

#: Ou chaque manuel canonique se construit, et sous quel nom.
CANONICAL_BUILDS = {
    "1SPE": "Mathematiques/manuel-maths/build/MANUEL_1SPE",
    "TSPE_2026_2027": "Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027",
    "TCOMPL": "Mathematiques/manuel-maths/build/MANUEL_TCOMPL",
    "TEXPERTES": "Mathematiques/manuel-maths/build/MANUEL_TEXPERTES",
    "1NSI": "NSI/build/MANUEL_1NSI",
    "TNSI": "NSI/build/MANUEL_TNSI",
}

#: Ce qui porte un `\documentclass` sans etre un manuel, avec la raison. Le
#: motif n'est pas decoratif : il dit pourquoi cette racine ne se publie pas.
NON_RELEASE_ROOTS = {
    "gabarits/common/chapitre_master.tex": "gabarit de compilation d'un chapitre isole",
    "Mathematiques/manuel-maths/gabarits/chapitre_master.tex": "gabarit de compilation d'un chapitre isole",
    "Mathematiques/manuel-maths/gabarits/objet_standalone.tex": "gabarit de compilation d'un objet isole",
    "Mathematiques/manuel-maths/gabarits/specimen.tex": "specimen de charte, jamais diffuse",
    "Mathematiques/manuel-maths/gabarits/specimen-v6.tex": "specimen de charte, jamais diffuse",
    "Mathematiques/manuel-maths/gabarits/specimen-pont-v6.tex": "specimen de charte, jamais diffuse",
    "NSI/gabarits/chapitre_master.tex": "gabarit de compilation d'un chapitre isole",
    "NSI/gabarits/objet_standalone.tex": "gabarit de compilation d'un objet isole",
    "NSI/gabarits/book_master.tex": "gabarit d'assemblage, instancie par l'assembleur",
    "NSI/gabarits/specimen.tex": "specimen de charte, jamais diffuse",
}

#: Un repertoire de build transitoire porte le nom d'une execution ; il est
#: efface a la fin d'une construction reussie et n'est jamais une cible.
TRANSIENT_RUN = re.compile(r"(^|/)\.[A-Za-z0-9_.-]+-[a-z0-9]{8}(/|$)")

#: Des familles entieres de racines TeX ne sont pas des manuels. Les classer
#: par regle plutot qu'une par une evite qu'un fichier ajoute demain se
#: retrouve non classe pour la seule raison qu'on n'a pas pense a lui.
NON_RELEASE_RULES = (
    (
        re.compile(r"^NSI/corpus_nsi/02_modeles_documents/"),
        "modele de document du corpus NSI : gabarit d'auteur, jamais assemble",
    ),
    (
        re.compile(r"^NSI/corpus_nsi/latex/packs/"),
        "pack NSI autonome : chaine de production distincte des manuels",
    ),
    (
        re.compile(r"^Mathematiques/manuel-maths/build/maquette-v5/"),
        "maquette de charte : sert au controle visuel, ne se diffuse pas",
    ),
    (
        re.compile(r"^(?:Mathematiques/manuel-maths|NSI)/build/(?!MANUEL_)"),
        "construction d'un chapitre isole : artefact de travail, pas un manuel",
    ),
)


class InventoryError(RuntimeError):
    """Une preuve manque : l'inventaire ne peut pas etre etabli."""


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def declared_manuals() -> list[str]:
    if not COLLECTION_STATE.is_file():
        raise InventoryError(f"registre de collection absent : {COLLECTION_STATE}")
    payload = json.loads(COLLECTION_STATE.read_text(encoding="utf-8"))
    return sorted(payload["manuels"])


def tex_roots() -> list[Path]:
    """Toute racine TeX du depot : ce que le compilateur pourrait lancer."""

    found: list[Path] = []
    for path in sorted(ROOT.rglob("*.tex")):
        if ".git" in path.parts or "reference-v4" in path.parts:
            continue
        head = path.read_text(encoding="utf-8", errors="replace")[:4000]
        if re.search(r"^\\documentclass", head, re.M):
            found.append(path)
    return found


def assembler_variants() -> dict[str, list[str]]:
    """Les variantes que chaque assembleur sait produire, lues chez eux."""

    variants: dict[str, list[str]] = {}
    for name, module_dir in (
        ("maths", ROOT / "Mathematiques/manuel-maths/scripts"),
        ("nsi", ROOT / "NSI/scripts"),
    ):
        source = (module_dir / "assemble_manuel.py").read_text(encoding="utf-8")
        match = re.search(r"^VARIANTS\s*=\s*[\[(](.*?)[\])]", source, re.M | re.S)
        if match:
            variants[name] = re.findall(r"[\"']([a-z_]+)[\"']", match.group(1))
        else:
            variants[name] = list(RELEASE_VARIANTS)
    return variants


def build() -> dict[str, Any]:
    manuals = declared_manuals()
    roots = tex_roots()
    variants = assembler_variants()

    targets: list[dict[str, Any]] = []
    unregistered: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []

    canonical_masters: set[str] = set()
    for manual, build_dir in CANONICAL_BUILDS.items():
        stem = Path(build_dir).name
        for variant in RELEASE_VARIANTS:
            master = ROOT / build_dir / f"{stem}_{variant}.tex"
            pdf = ROOT / build_dir / f"{stem}_{variant}.pdf"
            canonical_masters.add(relative(master))
            row = {
                "manual_id": manual,
                "variant": variant,
                "classification": "CANONICAL_RELEASE_TARGET",
                "master": relative(master),
                "pdf": relative(pdf),
                "master_present": master.is_file(),
                "pdf_present": pdf.is_file(),
                "pdf_tracked": bool(pdf.is_file()),
            }
            targets.append(row)
            if not pdf.is_file():
                missing.append(
                    {"manual_id": manual, "variant": variant, "why": "PDF absent"}
                )

    non_release: list[dict[str, Any]] = []
    for root in roots:
        key = relative(root)
        if key in canonical_masters:
            continue
        if TRANSIENT_RUN.search(key):
            non_release.append(
                {
                    "path": key,
                    "classification": "EXPLICITLY_NON_RELEASE",
                    "why": "repertoire de construction transitoire, efface en fin de build",
                }
            )
            continue
        reason = NON_RELEASE_ROOTS.get(key)
        if reason is None:
            reason = next(
                (why for pattern, why in NON_RELEASE_RULES if pattern.search(key)),
                None,
            )
        if reason is None:
            unregistered.append({"path": key, "why": "racine TeX non classee"})
            continue
        non_release.append(
            {"path": key, "classification": "EXPLICITLY_NON_RELEASE", "why": reason}
        )

    # Les variantes que les assembleurs savent produire au-dela des deux
    # publiees : elles existent, elles ne se publient pas, et le dire evite
    # qu'on les prenne un jour pour des cibles.
    extra_variants = [
        {
            "assembler": name,
            "variant": variant,
            "classification": "EXPLICITLY_NON_RELEASE",
            "why": "variante de travail : la release ne diffuse que eleve et professeur",
        }
        for name, declared in variants.items()
        for variant in declared
        if variant not in RELEASE_VARIANTS
    ]

    # Les PDF deposes pour publication doivent correspondre, un pour un, aux
    # cibles canoniques. Un PDF de plus serait un artefact courant ambigu.
    published = sorted(PUBLICATION_DIR.glob("*.pdf")) if PUBLICATION_DIR.is_dir() else []
    if len(published) != len(targets):
        ambiguous.append(
            {
                "directory": relative(PUBLICATION_DIR),
                "published": len(published),
                "canonical_targets": len(targets),
                "why": "le depot de publication ne compte pas autant de PDF que de cibles",
            }
        )

    declared_set = set(manuals)
    if declared_set != set(CANONICAL_BUILDS):
        missing.append(
            {
                "why": "le registre de collection et la table des builds divergent",
                "declared": sorted(declared_set),
                "built": sorted(CANONICAL_BUILDS),
            }
        )

    return {
        "artifact_type": "canonical_release_inventory",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "the_inventory_starts_from_the_repository": (
            "Les cibles sont cherchees dans le depot -- racines TeX, "
            "repertoires de build, PDF, variantes que les assembleurs savent "
            "produire -- puis confrontees au registre. Reciter la liste "
            "attendue repeterait l'angle mort au lieu de le fermer."
        ),
        "why_this_matters": (
            "Un manuel etait tenu sous controle, cinq vivaient a cote sans que "
            "rien ne les regarde. C'est cette asymetrie qui a laisse passer "
            "onze mille guillemets courbes dans le code imprime de NSI."
        ),
        "release_variants": list(RELEASE_VARIANTS),
        "declared_manuals": manuals,
        "canonical_targets": targets,
        "canonical_release_roots": sorted(list(canonical_masters)),
        "explicit_non_release_roots": non_release,
        "extra_assembler_variants": extra_variants,
        "non_release_targets": non_release + extra_variants,
        "unregistered_release_targets": unregistered,
        "missing_canonical_targets": missing,
        "ambiguous_current_artifacts": ambiguous,
        "summary": {
            "CANONICAL_MANUALS": len(CANONICAL_BUILDS),
            "CANONICAL_PDFS": len(targets),
            "CANONICAL_RELEASE_ROOTS": len(canonical_masters),
            "EXPLICIT_NON_RELEASE_ROOTS": len(non_release),
            "TOTAL_TEX_ROOTS": len(roots),
            "TEX_ROOTS_FOUND": len(roots),
            "UNCLASSIFIED_TEX_ROOTS": len(unregistered),
            "EXTRA_ASSEMBLER_VARIANTS": len(extra_variants),
            "NON_RELEASE_TARGETS": len(non_release) + len(extra_variants),
            "UNREGISTERED_RELEASE_TARGET": len(unregistered),
            "MISSING_CANONICAL_TARGET": len(missing),
            "AMBIGUOUS_CURRENT_ARTIFACT": len(ambiguous),
            "UNKNOWN": 0,
        },
    }


BLOCKING = (
    "UNREGISTERED_RELEASE_TARGET",
    "MISSING_CANONICAL_TARGET",
    "AMBIGUOUS_CURRENT_ARTIFACT",
    "UNKNOWN",
)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Inventaire canonique de publication",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"> {payload['the_inventory_starts_from_the_repository']}",
        "",
        f"> {payload['why_this_matters']}",
        "",
        "## Métriques",
        "",
        "| Métrique | Valeur |",
        "|---|---:|",
    ]
    for name, value in payload["summary"].items():
        lines.append(f"| `{name}` | {value} |")
    lines += [
        "",
        "## Cibles canoniques",
        "",
        "| Manuel | Variante | Maître | PDF |",
        "|---|---|---|---|",
    ]
    for row in payload["canonical_targets"]:
        lines.append(
            f"| `{row['manual_id']}` | {row['variant']} | "
            f"{'présent' if row['master_present'] else 'ABSENT'} | "
            f"{'présent' if row['pdf_present'] else 'ABSENT'} |"
        )
    lines += ["", "## Cibles explicitement hors release", ""]
    for row in payload["non_release_targets"]:
        label = row.get("path") or f"{row.get('assembler')}:{row.get('variant')}"
        lines.append(f"- `{label}` — {row['why']}")
    for title, rows in (
        ("Cibles non enregistrées", payload["unregistered_release_targets"]),
        ("Cibles canoniques manquantes", payload["missing_canonical_targets"]),
        ("Artefacts courants ambigus", payload["ambiguous_current_artifacts"]),
    ):
        if rows:
            lines += ["", f"## {title}", ""]
            lines += [f"- `{json.dumps(row, ensure_ascii=False)}`" for row in rows]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ne rien ecrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build()
    except InventoryError as error:
        print(f"CANONICAL-INVENTORY-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"ecrit {JSON_TARGET.name} et {MD_TARGET.name}")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    return 1 if any(payload["summary"][name] for name in BLOCKING) else 0


if __name__ == "__main__":
    raise SystemExit(main())
