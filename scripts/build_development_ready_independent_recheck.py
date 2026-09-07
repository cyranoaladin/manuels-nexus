#!/usr/bin/env python3
"""Seconde vérification, indépendante, de `DEVELOPMENT_READY`.

`scripts/build_release_deliverable_readiness.py` conclut `DEVELOPMENT_READY =
24/24`. Un compteur qui se vérifie lui-même ne prouve rien : ses six axes se
lisent tous dans des artefacts déjà déposés (`INVENTAIRE_COLLECTION.json`,
`RELEASE_DELIVERABLE_SCOPE_MATRIX.json`, `DIMENSION_*.json`) et un artefact
périmé se relit sans bruit. Ce producteur refait le constat par un **autre
chemin de preuve**, puis compare.

Chemins de preuve, primaire → indépendant :

`CONTENT`
    primaire : `declared_assemblies[…].included_files` de l'inventaire.
    ici : on appelle la fonction de collecte de l'assembleur lui-même
    (`collect_variant_objects` côté NSI, `collect_chapter` côté maths) sur le
    système de fichiers courant. C'est ce que le PDF recevrait aujourd'hui,
    pas ce qu'un inventaire a enregistré un jour. L'écart avec l'inventaire est
    publié comme `INVENTORY_DIVERGENCE`.

`ASSEMBLY`
    primaire : le booléen `declared_assembly` de la matrice de périmètre.
    ici : la variante est réellement connue du moteur qui la construirait.

`BUILD_TARGET`
    primaire : le booléen `build_target_declared`.
    ici : le nom de sortie déclaré est bien celui que le moteur produirait, en
    appliquant la normalisation `-`/`_` que la collection documente déjà.

`DEVELOPMENT_BUILD`
    primaire : un `glob` `*/*_<variante>.pdf` sous les racines de build.
    ici : le chemin exact déduit du nommage du moteur, ouvert et validé comme
    PDF (en-tête, `%%EOF`, pagination lue par `pypdf` — pas `pdfinfo`, dont le
    moteur se sert déjà —, et texte extractible sur la première page).

`PROGRAMME`
    primaire : absence de constat bloquant dans `DIMENSION_REGULATION.json`.
    ici : chaque chapitre du manuel a un mappage de programme complet et aucune
    lacune pédagogique réelle dans `PUBLISH_READINESS_CHAPTER_MATRIX.json`.

`SCIENCE`
    primaire : absence de constat bloquant dans `DIMENSION_MATHEMATICS.json`.
    ici : **on ré-exécute** les blocs `% BEGIN-VERIFY` des objets du manuel, au
    contenu courant, avec un exécuteur écrit ici. Zéro échec exigé, et aucun
    objet mathématique d'un type outillable sans oracle.

Ce producteur ne lit `RELEASE_DELIVERABLE_READINESS.json` qu'**après** avoir
conclu, et seulement pour publier l'accord ou le désaccord. Il n'approuve rien
et ne remplace aucune décision humaine.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib
import importlib.util
import io
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_auxiliary_rubric_applicability as applicability  # noqa: E402

SCOPE = ROOT / "audit/RELEASE_DELIVERABLE_SCOPE_MATRIX.json"
INVENTORY = ROOT / "audit/INVENTAIRE_COLLECTION.json"
CHAPTER_MATRIX = ROOT / "audit/PUBLISH_READINESS_CHAPTER_MATRIX.json"
PRIMARY = ROOT / "audit/RELEASE_DELIVERABLE_READINESS.json"
OUTPUT_JSON = ROOT / "audit/DEVELOPMENT_READY_INDEPENDENT_RECHECK.json"
OUTPUT_MD = ROOT / "audit/DEVELOPMENT_READY_INDEPENDENT_RECHECK.md"

#: Rubriques dont l'absence dans un chapitre peut être pédagogiquement motivée.
#: Ce n'est pas une mesure de maturité mais le contrat d'applicabilité de la
#: collection : le rejouer ici à l'identique est délibéré, l'assouplir
#: fabriquerait du remplissage.
EXCUSABLE_RUBRICS = {"methodes", "remediation", "banque_ecrite", "banque_pratique"}

VERIFY_BLOCK = re.compile(r"^% BEGIN-VERIFY\s*$(.*?)^% END-VERIFY\s*$", re.S | re.M)
COMMENT_LINE = re.compile(r"^%[ \t]?(.*)$")
MATH_NOTATION = re.compile(
    r"\$|\\dfrac|\\frac|\\sqrt|\\int|\\sum|\\lim|\\vec|\\begin\{align"
)
MATHS_MANUALS = frozenset({"1SPE", "TSPE_2026_2027", "TCOMPL", "TEXPERTES"})
#: Types dont un objet mathématique devrait porter un bloc de vérification.
ORACLE_CAPABLE_TYPES = frozenset({
    "cours", "exercice", "corrige", "evaluation", "corrige_evaluation",
})


# --------------------------------------------------------------------------
# Moteurs d'assemblage
# --------------------------------------------------------------------------
def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"module illisible : {relative}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _maths_engine():
    """L'assembleur maths, chargé sous un nom distinct de celui de NSI.

    Les deux projets ont un module `assemble_manuel` ; les charger sous le même
    nom mesurerait un corpus avec le moteur de l'autre.
    """
    scripts = ROOT / "Mathematiques" / "manuel-maths" / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    return _load("recheck_maths_assemble_manuel",
                 "Mathematiques/manuel-maths/scripts/assemble_manuel.py")


def _nsi_engine():
    return importlib.import_module("NSI.scripts.assemble_manuel")


def _engine_objects(manual: str, variant: str) -> dict[str, list[str]]:
    """Objets réellement collectés, par chapitre, pour ce livrable.

    Rien n'est lu dans l'inventaire : on interroge le moteur qui assemblerait
    le PDF, sur l'arbre courant.
    """
    if manual in MATHS_MANUALS:
        engine = _maths_engine()
        chapters = engine.MANUAL_CHAPTERS[manual]
        by_chapter: dict[str, list[str]] = {}
        for chapter in chapters:
            directory = engine.ROOT / "chapitres" / chapter
            if not directory.is_dir():
                by_chapter[chapter] = []
                continue
            by_chapter[chapter] = [
                str(path.resolve().relative_to(ROOT))
                for path in engine.collect_chapter(directory, variant)
            ]
        return by_chapter
    engine = _nsi_engine()
    try:
        engine.select_book(manual)
        chapters = list(engine.CHAPITRES)
        by_chapter = {chapter: [] for chapter in chapters}
        for path in engine.collect_variant_objects(variant):
            chapter = path.resolve().relative_to(
                (engine.ROOT / "chapitres").resolve()).parts[0]
            by_chapter.setdefault(chapter, []).append(
                str(path.resolve().relative_to(ROOT)))
    finally:
        engine.select_book("1NSI")
    return by_chapter


def _engine_variants(manual: str) -> set[str]:
    """Variantes que le moteur du manuel sait réellement assembler."""
    if manual in MATHS_MANUALS:
        engine = _maths_engine()
        return set(engine.VARIANT_ORDERS) | {"eleve", "professeur"}
    return set(_nsi_engine().VARIANTS)


def _engine_pdf_path(manual: str, variant: str) -> Path:
    """Chemin exact du PDF que le moteur écrirait, déduit de son nommage."""
    if manual in MATHS_MANUALS:
        engine = _maths_engine()
        stem = f"{engine.MANUAL_TEX_NAMES[manual]}_{variant}"
        return (engine.ROOT / "build" / engine.MANUAL_TEX_NAMES[manual]
                / f"{stem}.pdf")
    engine = _nsi_engine()
    try:
        engine.select_book(manual)
        directory = engine.build_dir_name()
        stem = engine.output_stem(variant)
    finally:
        engine.select_book("1NSI")
    return engine.ROOT / "build" / directory / f"{stem}.pdf"


# --------------------------------------------------------------------------
# Axes
# --------------------------------------------------------------------------
def _normalise(name: str) -> str:
    return name.replace("-", "_").upper()


def _content_axis(manual: str, variant: str, assembly_id: str | None,
                  inventory: dict[str, Any]) -> dict[str, Any]:
    by_chapter = _engine_objects(manual, variant)
    chapters = set(by_chapter)
    if variant in EXCUSABLE_RUBRICS:
        chapters = applicability.applicable_chapters(manual, variant, chapters)
    covered = {c for c in chapters if by_chapter.get(c)}
    total = sum(len(v) for v in by_chapter.values())

    assemblies = {a["assembly_id"]: a
                  for a in inventory.get("declared_assemblies", [])}
    declared = set(assemblies.get(assembly_id or "", {}).get("included_files", []))
    observed = {p for paths in by_chapter.values() for p in paths}
    # La comparaison ne porte que sur les objets de chapitre : un assemblage
    # déclare aussi son appareil transversal (avant-propos, formulaire, mémo
    # Python…), que la collecte par chapitre ne voit pas — et ne doit pas voir.
    # Compter cet écart comme une divergence ferait crier douze livrables sains.
    chapter_scoped = {path for path in declared
                      if "/chapitres/" in path and path.endswith(".tex")}
    transversal = sorted(path for path in declared - chapter_scoped
                         if path.endswith(".tex"))
    inventory_only = sorted(chapter_scoped - observed)
    engine_only = sorted(observed - declared)
    return {
        "verdict": bool(chapters) and covered == chapters and total > 0,
        "objects_collected_by_engine": total,
        "chapters_expected": len(chapters),
        "chapters_covered": len(covered),
        "chapters_uncovered": sorted(chapters - covered),
        "declared_outside_chapters": transversal,
        "inventory_divergence": {
            "declared_not_collected": inventory_only[:20],
            "declared_not_collected_count": len(inventory_only),
            "collected_not_declared": engine_only[:20],
            "collected_not_declared_count": len(engine_only),
        },
    }


def _assembly_axis(manual: str, variant: str, assembly_id: str | None,
                   inventory: dict[str, Any]) -> dict[str, Any]:
    known = variant in _engine_variants(manual)
    declared = any(a["assembly_id"] == assembly_id
                   for a in inventory.get("declared_assemblies", []))
    return {"verdict": known and declared,
            "variant_known_to_engine": known,
            "assembly_declared_in_inventory": declared}


def _build_target_axis(manual: str, variant: str,
                       declared_output: str) -> dict[str, Any]:
    engine_pdf = _engine_pdf_path(manual, variant)
    agrees = _normalise(engine_pdf.name) == _normalise(declared_output)
    return {
        "verdict": agrees,
        "engine_output": engine_pdf.name,
        "declared_output": declared_output,
        # Le périmètre écrit `TSPE_2026_2027`, le moteur `TSPE_2026-2027` :
        # divergence de graphie déjà documentée, pas de cible manquante.
        "naming_normalisation_applied": engine_pdf.name != declared_output,
    }


def _shown(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def _pdf_evidence(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"verdict": False, "reason": "PDF absent", "path": _shown(path)}
    raw = path.read_bytes()
    record: dict[str, Any] = {
        "path": _shown(path),
        "bytes": len(raw),
        "header_ok": raw.startswith(b"%PDF-"),
        "trailer_ok": b"%%EOF" in raw[-2048:],
    }
    try:
        import pypdf  # noqa: PLC0415

        reader = pypdf.PdfReader(io.BytesIO(raw))
        record["pages"] = len(reader.pages)
        record["first_page_has_text"] = bool(
            reader.pages[0].extract_text().strip()) if reader.pages else False
    except Exception as error:  # noqa: BLE001 - on rapporte, on ne masque pas
        record["pages"] = 0
        record["first_page_has_text"] = False
        record["reader_error"] = f"{type(error).__name__}: {error}"
    record["verdict"] = bool(
        record["header_ok"] and record["trailer_ok"]
        and record["pages"] > 0 and record["first_page_has_text"]
    )
    return record


def _programme_axis(manual: str, matrix: dict[str, Any]) -> dict[str, Any]:
    rows = [c for c in matrix["chapters"] if c["manual"] == manual]
    incomplete = sorted(c["chapter"] for c in rows
                        if c["programme"].get("status") != "COMPLETE")
    unmapped = sum(int(c["programme"].get("missing", 0)) for c in rows)
    wrong_year = sum(int(c["programme"].get("wrong_year", 0)) for c in rows)
    real_gaps = sum(int(c["pedagogical_role_coverage"].get("missing", 0))
                    for c in rows)
    return {
        "verdict": bool(rows) and not incomplete and unmapped == 0
        and wrong_year == 0 and real_gaps == 0,
        "chapters_examined": len(rows),
        "chapters_incomplete": incomplete,
        "unmapped_official_atoms": unmapped,
        "wrong_year_atoms": wrong_year,
        "real_pedagogical_gaps": real_gaps,
    }


def _run_verify(program: str) -> tuple[bool, str, int]:
    """Exécute un bloc de vérification dans un espace de noms isolé."""
    import ast  # noqa: PLC0415
    import sympy  # noqa: PLC0415

    try:
        tree = ast.parse(program)
    except SyntaxError as error:
        return False, f"SyntaxError: {error}", 0
    assertions = sum(1 for node in ast.walk(tree)
                     if isinstance(node, ast.Assert))
    namespace: dict[str, Any] = {"__builtins__": __builtins__}
    namespace.update({name: getattr(sympy, name) for name in dir(sympy)
                      if not name.startswith("_")})
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(program, "<verify>", "exec"), namespace)  # noqa: S102
    except AssertionError as error:
        return False, f"assertion fausse : {error}" or "assertion fausse", assertions
    except Exception as error:  # noqa: BLE001 - on rapporte, on ne masque pas
        return False, f"{type(error).__name__}: {error}", assertions
    return True, "", assertions


def _science_axis(manual: str, inventory: dict[str, Any]) -> dict[str, Any]:
    """Ré-exécution des oracles du manuel, au contenu courant."""
    objects = 0
    assertions = 0
    failures: list[dict[str, str]] = []
    missing_oracle: list[str] = []
    for chapter in inventory["manuals"].get(manual, {}).get("chapters", {}).values():
        for obj in chapter.get("objects", []):
            path = ROOT / str(obj.get("path", ""))
            if not path.is_file():
                continue
            body = path.read_text(encoding="utf-8")
            block = VERIFY_BLOCK.search(body)
            if block is None:
                mathematical = manual in MATHS_MANUALS or bool(
                    MATH_NOTATION.search(body))
                if mathematical and obj.get("type_objet") in ORACLE_CAPABLE_TYPES:
                    missing_oracle.append(str(obj["path"]))
                continue
            objects += 1
            lines = [match.group(1)
                     for match in map(COMMENT_LINE.match,
                                      block.group(1).splitlines())
                     if match is not None]
            ok, reason, count = _run_verify("\n".join(lines))
            assertions += count
            if not ok:
                failures.append({"path": str(obj["path"]), "reason": reason})
    return {
        "verdict": not failures and not missing_oracle,
        "objects_with_oracle": objects,
        "assertions_executed": assertions,
        "assertion_failures": failures,
        "missing_oracle": missing_oracle,
    }


# --------------------------------------------------------------------------
def build() -> dict[str, Any]:
    scope = json.loads(SCOPE.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    matrix = json.loads(CHAPTER_MATRIX.read_text(encoding="utf-8"))

    required = [entry for entry in scope["deliverables"]
                if entry["canonical_release_product"]
                or entry["required_auxiliary_product"]]

    # Les deux axes de manuel ne dépendent pas de la variante : on les calcule
    # une fois par manuel, une ré-exécution d'oracles par livrable coûterait
    # vingt-quatre fois le même travail sans rien prouver de plus.
    programme = {}
    science = {}
    for manual in sorted({e["deliverable_id"].split("::", 1)[0] for e in required}):
        programme[manual] = _programme_axis(manual, matrix)
        science[manual] = _science_axis(manual, inventory)

    rows: list[dict[str, Any]] = []
    for entry in required:
        manual = entry["deliverable_id"].split("::", 1)[0]
        profile = entry["build_profile"]
        variant = profile["variant_argument"]
        content = _content_axis(manual, variant, profile["assembly_id"], inventory)
        assembly = _assembly_axis(manual, variant, profile["assembly_id"], inventory)
        target = _build_target_axis(manual, variant, profile["output"])
        build_pdf = _pdf_evidence(_engine_pdf_path(manual, variant))
        axes = {
            "content": content["verdict"],
            "assembly": assembly["verdict"],
            "build_target": target["verdict"],
            "development_build": build_pdf["verdict"],
            "programme": programme[manual]["verdict"],
            "science": science[manual]["verdict"],
        }
        rows.append({
            "deliverable_id": entry["deliverable_id"],
            "manual": manual,
            "variant": variant,
            "axes": axes,
            "content": content,
            "assembly": assembly,
            "build_target": target,
            "development_build": build_pdf,
            "development_ready_independent": all(axes.values()),
        })
    rows.sort(key=lambda row: row["deliverable_id"])

    ready = sum(1 for row in rows if row["development_ready_independent"])
    summary = {
        "REQUIRED_RELEASE_DELIVERABLES": len(rows),
        "DEVELOPMENT_READY_INDEPENDENT_RECHECK": ready,
        "RECHECK_SATISFIED": ready == len(rows) == 24,
        "OBJECTS_COLLECTED_BY_ENGINE_TOTAL": sum(
            row["content"]["objects_collected_by_engine"] for row in rows),
        "ORACLE_ASSERTIONS_RE_EXECUTED": sum(
            axis["assertions_executed"] for axis in science.values()),
        "ORACLE_FAILURES": sum(len(axis["assertion_failures"])
                               for axis in science.values()),
        "MISSING_ORACLE": sum(len(axis["missing_oracle"])
                              for axis in science.values()),
        "INVENTORY_DIVERGENCE_DELIVERABLES": sum(
            1 for row in rows
            if row["content"]["inventory_divergence"]["declared_not_collected_count"]
            or row["content"]["inventory_divergence"]["collected_not_declared_count"]),
        "NAMING_NORMALISATION_DELIVERABLES": sum(
            1 for row in rows if row["build_target"]["naming_normalisation_applied"]),
        "APPROVES_NOTHING": True,
    }

    payload = {
        "artifact_type": "development_ready_independent_recheck",
        "schema_version": 1,
        "generated_by": "scripts/build_development_ready_independent_recheck.py",
        "authority_note": (
            "Vérification indépendante de `DEVELOPMENT_READY`. Ne vaut ni "
            "approbation humaine, ni reçu de build, ni `RELEASE_READY`."
        ),
        "summary": summary,
        "per_manual": {manual: {"programme": programme[manual],
                                "science": science[manual]}
                       for manual in programme},
        "deliverables": rows,
    }
    payload["agreement_with_primary"] = _agreement(rows)
    return payload


def _agreement(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Comparaison au compteur primaire — **après** conclusion, jamais avant."""
    if not PRIMARY.is_file():
        return {"primary_artifact_present": False}
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    by_id = {row["deliverable_id"]: row for row in primary["deliverables"]}
    disagreements = []
    for row in rows:
        other = by_id.get(row["deliverable_id"])
        if other is None:
            disagreements.append({"deliverable_id": row["deliverable_id"],
                                  "reason": "absent du compteur primaire"})
            continue
        if other["development_ready"] != row["development_ready_independent"]:
            disagreements.append({
                "deliverable_id": row["deliverable_id"],
                "primary": other["development_ready"],
                "independent": row["development_ready_independent"],
                "axes_primary": other["axes"],
                "axes_independent": row["axes"],
            })
    return {
        "primary_artifact_present": True,
        "PRIMARY_DEVELOPMENT_READY": primary["summary"]["DEVELOPMENT_READY"],
        "INDEPENDENT_DEVELOPMENT_READY": sum(
            1 for row in rows if row["development_ready_independent"]),
        "DISAGREEMENTS": len(disagreements),
        "disagreements": disagreements,
    }


def render_md(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    a = payload["agreement_with_primary"]
    lines = [
        "# Vérification indépendante de `DEVELOPMENT_READY`",
        "",
        "Le compteur primaire lit des artefacts déposés. Cette seconde",
        "vérification interroge les moteurs d'assemblage, ouvre les PDF et",
        "**ré-exécute** les oracles au contenu courant, puis compare.",
        "",
        f"- `DEVELOPMENT_READY_INDEPENDENT_RECHECK` : "
        f"`{s['DEVELOPMENT_READY_INDEPENDENT_RECHECK']}/"
        f"{s['REQUIRED_RELEASE_DELIVERABLES']}`",
        f"- Assertions ré-exécutées : `{s['ORACLE_ASSERTIONS_RE_EXECUTED']}` "
        f"(échecs : `{s['ORACLE_FAILURES']}`)",
        f"- `MISSING_ORACLE` : `{s['MISSING_ORACLE']}`",
        f"- Désaccords avec le compteur primaire : `{a.get('DISAGREEMENTS', 'n/a')}`",
        "",
        "| Livrable | Contenu | Assemblage | Cible | Build dev | Programme | "
        "Science | Prêt (indépendant) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in payload["deliverables"]:
        axes = row["axes"]
        mark = lambda value: "oui" if value else "**non**"  # noqa: E731
        lines.append(
            f"| `{row['deliverable_id']}` | {mark(axes['content'])} | "
            f"{mark(axes['assembly'])} | {mark(axes['build_target'])} | "
            f"{mark(axes['development_build'])} | {mark(axes['programme'])} | "
            f"{mark(axes['science'])} | "
            f"{mark(row['development_ready_independent'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if arguments.check:
        if (OUTPUT_JSON.is_file()
                and OUTPUT_JSON.read_text(encoding="utf-8") == rendered):
            print("DEVELOPMENT_READY_INDEPENDENT_RECHECK check: OK")
            return 0
        print("DEVELOPMENT_READY_INDEPENDENT_RECHECK check: STALE")
        return 1
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    print(json.dumps(payload["agreement_with_primary"].get("DISAGREEMENTS"),
                     ensure_ascii=False))
    return 0 if payload["summary"]["RECHECK_SATISFIED"] else 1


if __name__ == "__main__":
    sys.exit(main())
