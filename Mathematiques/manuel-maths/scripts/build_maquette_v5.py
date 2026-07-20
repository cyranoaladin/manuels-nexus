#!/usr/bin/env python3
"""Validate the isolated v5 mock-up manifest and source metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


class MetaError(ValueError):
    """Report invalid v5 manifest or object metadata."""


def load_manifest(path: Path, root: Path) -> dict[str, Any]:
    """Load a JSON manifest, reporting readable validation errors."""
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MetaError(f"manifest illisible: {exc}") from exc
    if not isinstance(manifest, dict):
        raise MetaError("le manifeste doit être un objet JSON")
    validate_manifest(manifest, root)
    return manifest


def _safe_existing_file(root: Path, value: object, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise MetaError(f"{field} doit être un chemin relatif non vide")
    relative = Path(value)
    if relative.is_absolute():
        raise MetaError(f"{field} doit être relatif")
    try:
        resolved = (root / relative).resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise MetaError(f"{field} est absent ou hors racine: {value}") from exc
    if not resolved.is_file():
        raise MetaError(f"{field} ne désigne pas un fichier: {value}")
    return resolved


_MANIFEST_FIELDS = {
    "version",
    "source_chapter",
    "output_pdf",
    "expected_pages",
    "blank_pages",
    "course_files",
    "methods",
    "rendered_method",
    "exercise_order",
    "exercise_page_counts",
    "pictograms",
    "qcm",
    "compact_corrections",
    "chapter_toc",
    "required_strings",
}
_CHAPTER_ID = re.compile(r"(?:1SPE|TSPE)-[A-Z0-9]+(?:-[A-Z0-9]+)*")
_METHOD_ID = re.compile(
    r"(?:1SPE|TSPE)-[A-Z0-9]+(?:-[A-Z0-9]+)*-ME-[0-9]{3}"
)
_EXERCISE_ID = re.compile(
    r"(?:1SPE|TSPE)-[A-Z0-9]+(?:-[A-Z0-9]+)*-EX-[0-9]{3}"
)
_REQUIRED_STRINGS = [
    "S'entraîner : ex. 1, 2, 7 p. 9",
    "→ M1 · Corrigé p. 15",
]


def _validated_ids(
    value: object,
    field: str,
    pattern: re.Pattern[str],
    count: int | None = None,
) -> list[str]:
    if not isinstance(value, list) or any(
        not isinstance(object_id, str) or pattern.fullmatch(object_id) is None
        for object_id in value
    ):
        raise MetaError(f"{field} contient un ID canonique invalide")
    if count is not None and len(value) != count:
        raise MetaError(f"{field} doit contenir {count} IDs")
    if len(value) != len(set(value)):
        raise MetaError(f"ID dupliqué dans {field}")
    return value


def _safe_output_path(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise MetaError("output_pdf doit être un chemin relatif non vide")
    relative = Path(value)
    if relative.is_absolute() or relative.suffix != ".pdf":
        raise MetaError("output_pdf doit être un chemin PDF relatif")
    try:
        resolved = (root / relative).resolve(strict=False)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise MetaError("output_pdf est hors racine") from exc
    return resolved


def validate_manifest(manifest: dict[str, Any], root: Path) -> None:
    """Validate the complete normative v5 manifest before any aggregation."""
    if set(manifest) != _MANIFEST_FIELDS:
        raise MetaError("champs du manifeste incomplets ou inattendus")
    try:
        safe_root = root.resolve(strict=True)
    except OSError as exc:
        raise MetaError(f"racine absente: {root}") from exc

    if type(manifest["version"]) is not int or manifest["version"] != 2:
        raise MetaError("version doit valoir 2")
    chapter = manifest["source_chapter"]
    if not isinstance(chapter, str) or _CHAPTER_ID.fullmatch(chapter) is None:
        raise MetaError("source_chapter invalide")
    chapter_root = safe_root / "chapitres" / chapter
    if not chapter_root.is_dir():
        raise MetaError(f"chapitre source absent: {chapter}")
    _safe_output_path(safe_root, manifest["output_pdf"])

    expected_pages = manifest["expected_pages"]
    if type(expected_pages) is not int or expected_pages != 15:
        raise MetaError("expected_pages doit être l'entier 15")
    if manifest["blank_pages"] != [6, 14]:
        raise MetaError("blank_pages doit valoir [6, 14]")

    course_files = manifest["course_files"]
    if (
        not isinstance(course_files, list)
        or len(course_files) != 2
        or len(set(course_files)) != 2
    ):
        raise MetaError("course_files doit contenir deux chemins distincts")
    course_root = (chapter_root / "cours").resolve(strict=True)
    for value in course_files:
        course_file = _safe_existing_file(safe_root, value, "course_files")
        try:
            course_file.relative_to(course_root)
        except ValueError as exc:
            raise MetaError("course_files doit rester dans le cours du chapitre") from exc
        if course_file.suffix != ".tex":
            raise MetaError("course_files doit désigner des fichiers TeX")

    method_ids = _validated_ids(manifest["methods"], "methods", _METHOD_ID, 4)
    for object_id in method_ids:
        if not (chapter_root / "methodes" / f"{object_id}.tex").is_file():
            raise MetaError(f"ID de méthode inconnu: {object_id}")
    rendered = manifest["rendered_method"]
    if not isinstance(rendered, dict) or set(rendered) != {"id", "applications"}:
        raise MetaError("rendered_method doit contenir id et applications")
    rendered_id = rendered["id"]
    if (
        not isinstance(rendered_id, str)
        or _METHOD_ID.fullmatch(rendered_id) is None
        or rendered_id not in method_ids
    ):
        raise MetaError("ID de méthode rendue inconnu")

    exercise_ids = _validated_ids(
        manifest["exercise_order"], "exercise_order", _EXERCISE_ID, 20
    )
    for object_id in exercise_ids:
        if not (chapter_root / "exercices" / f"{object_id}.tex").is_file():
            raise MetaError(f"ID d'exercice inconnu: {object_id}")
    applications = _validated_ids(
        rendered["applications"], "applications", _EXERCISE_ID
    )
    if len(applications) > 3:
        raise MetaError("applications doit contenir au plus trois IDs")
    unknown_applications = set(applications) - set(exercise_ids)
    if unknown_applications:
        raise MetaError(
            f"ID d'application inconnu: {sorted(unknown_applications)[0]}"
        )
    if manifest["exercise_page_counts"] != {"9": 11, "10": 9}:
        raise MetaError("exercise_page_counts doit valoir {'9': 11, '10': 9}")

    pictograms = manifest["pictograms"]
    if not isinstance(pictograms, dict) or len(pictograms) != 3:
        raise MetaError("pictograms doit contenir trois entrées")
    for object_id, pictogram in pictograms.items():
        if (
            not isinstance(object_id, str)
            or _EXERCISE_ID.fullmatch(object_id) is None
            or object_id not in exercise_ids
        ):
            raise MetaError(f"ID de pictogramme inconnu: {object_id}")
        if pictogram not in {"python", "calculatrice"}:
            raise MetaError(f"pictogramme invalide: {pictogram}")

    compact = _validated_ids(
        manifest["compact_corrections"],
        "compact_corrections",
        _EXERCISE_ID,
        5,
    )
    unknown_compact = set(compact) - set(exercise_ids)
    if unknown_compact:
        raise MetaError(f"ID de corrigé compact inconnu: {sorted(unknown_compact)[0]}")

    chapter_toc = manifest["chapter_toc"]
    if not isinstance(chapter_toc, list) or len(chapter_toc) != 9:
        raise MetaError("chapter_toc doit contenir neuf entrées")
    for entry in chapter_toc:
        if (
            not isinstance(entry, list)
            or len(entry) != 2
            or not isinstance(entry[0], str)
            or not entry[0]
            or type(entry[1]) is not int
            or entry[1] <= 0
        ):
            raise MetaError("entrée chapter_toc invalide")
    if manifest["required_strings"] != _REQUIRED_STRINGS:
        raise MetaError("required_strings ne respecte pas les deux chaînes normatives")

    qcm = manifest["qcm"]
    if not isinstance(qcm, dict) or set(qcm) != {"file", "sha256"}:
        raise MetaError("qcm doit contenir file et sha256")
    qcm_file = _safe_existing_file(safe_root, qcm["file"], "qcm.file")
    qcm_root = (chapter_root / "qcm").resolve(strict=True)
    try:
        qcm_file.relative_to(qcm_root)
    except ValueError as exc:
        raise MetaError("qcm.file doit rester dans le QCM du chapitre") from exc
    digest = qcm["sha256"]
    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise MetaError("qcm.sha256 invalide")
    actual_digest = hashlib.sha256(qcm_file.read_bytes()).hexdigest()
    if digest != actual_digest:
        raise MetaError("qcm.sha256 ne correspond pas au fichier")


def _validate_common_meta(meta: dict[str, Any]) -> str:
    object_id = meta.get("id")
    if not isinstance(object_id, str) or not object_id.strip():
        raise MetaError("id doit être une chaîne non vide")

    object_type = meta.get("type_objet")
    if object_type not in {"exercice", "methode"}:
        raise MetaError("type_objet doit valoir exercice ou methode")

    methods = meta.get("methodes")
    if (
        not isinstance(methods, list)
        or not methods
        or any(
            not isinstance(method, str) or re.fullmatch(r"M[0-9]+", method) is None
            for method in methods
        )
    ):
        raise MetaError("methodes doit contenir au moins un code M[0-9]+")
    return object_type


def parse_meta(path: Path, root: Path) -> dict[str, Any]:
    """Read and validate the first META line, without consuming object content."""
    try:
        safe_root = root.resolve(strict=True)
        safe_path = path.resolve(strict=True)
        safe_path.relative_to(safe_root)
    except (OSError, ValueError) as exc:
        raise MetaError(f"fichier META absent ou hors racine: {path}") from exc
    if not safe_path.is_file():
        raise MetaError(f"fichier META invalide: {path}")

    meta_line = None
    try:
        with safe_path.open("rb") as handle:
            for _ in range(10):
                raw_line = handle.readline()
                if not raw_line:
                    break
                line = raw_line.decode("utf-8")
                if line.startswith("% META:"):
                    meta_line = line.removeprefix("% META:").strip()
                    break
    except (OSError, UnicodeDecodeError) as exc:
        raise MetaError(f"META illisible dans {path}") from exc

    if meta_line is None:
        raise MetaError(f"META absente des dix premières lignes: {path}")
    try:
        meta = json.loads(meta_line)
    except json.JSONDecodeError as exc:
        raise MetaError(f"JSON META invalide dans {path}: {exc}") from exc
    if not isinstance(meta, dict):
        raise MetaError(f"META doit être un objet JSON: {path}")

    object_type = _validate_common_meta(meta)
    if object_type == "methode":
        return meta

    parcours = meta.get("parcours")
    if type(parcours) is not int or parcours not in {1, 2, 3}:
        raise MetaError("parcours doit être un entier de 1 à 3")
    duration = meta.get("duree_min")
    if type(duration) is not int or duration <= 0:
        raise MetaError("duree_min doit être un entier strictement positif")

    declared_source = _safe_existing_file(
        safe_root, meta.get("fichier_tex"), "fichier_tex"
    )
    if declared_source != safe_path:
        raise MetaError("fichier_tex ne correspond pas au fichier lu")
    _safe_existing_file(safe_root, meta.get("corrige_tex"), "corrige_tex")
    return meta


def _manifest_id_list(manifest: dict[str, Any], field: str) -> list[str]:
    values = manifest.get(field)
    if not isinstance(values, list) or any(
        not isinstance(value, str) or not value for value in values
    ):
        raise MetaError(f"{field} doit être une liste d'IDs non vides")
    if len(values) != len(set(values)):
        raise MetaError(f"ID dupliqué dans {field}")
    return values


def _index_chapter_meta(
    manifest: dict[str, Any],
    root: Path,
    method_ids: list[str],
    exercise_ids: list[str],
) -> dict[str, tuple[dict[str, Any], Path]]:
    chapter = manifest.get("source_chapter")
    if not isinstance(chapter, str) or re.fullmatch(r"[A-Za-z0-9-]+", chapter) is None:
        raise MetaError("source_chapter invalide")
    try:
        safe_root = root.resolve(strict=True)
        chapter_root = (safe_root / "chapitres" / chapter).resolve(strict=True)
        chapter_root.relative_to(safe_root)
    except (OSError, ValueError) as exc:
        raise MetaError(f"chapitre source absent ou hors racine: {chapter}") from exc

    index: dict[str, tuple[dict[str, Any], Path]] = {}
    selected = [
        (object_id, chapter_root / "methodes" / f"{object_id}.tex", "methode")
        for object_id in method_ids
    ]
    selected.extend(
        (object_id, chapter_root / "exercices" / f"{object_id}.tex", "exercice")
        for object_id in exercise_ids
    )
    for expected_id, path, expected_type in selected:
        if not path.is_file():
            raise MetaError(f"ID {expected_type} inconnu: {expected_id}")
        meta = parse_meta(path, safe_root)
        object_id = meta["id"]
        if object_id in index:
            raise MetaError(f"ID META dupliqué: {object_id}")
        if object_id != expected_id:
            raise MetaError(
                f"ID META ne correspond pas au fichier sélectionné: {expected_id}"
            )
        if meta["type_objet"] != expected_type:
            raise MetaError(f"type META incorrect pour {expected_id}")
        index[object_id] = (meta, path)
    return index


def build_reference_table(
    manifest: dict[str, Any], root: Path
) -> dict[str, Any]:
    """Aggregate canonical method/exercise META without reading object bodies."""
    safe_root = root.resolve(strict=True)
    validate_manifest(manifest, safe_root)
    method_ids = _manifest_id_list(manifest, "methods")
    exercise_ids = _manifest_id_list(manifest, "exercise_order")
    index = _index_chapter_meta(manifest, safe_root, method_ids, exercise_ids)

    method_records: list[dict[str, Any]] = []
    for object_id in method_ids:
        indexed = index.get(object_id)
        if indexed is None or indexed[0]["type_objet"] != "methode":
            raise MetaError(f"ID de méthode inconnu: {object_id}")
        meta, source = indexed
        method_records.append(
            {
                "id": object_id,
                "method": meta["methodes"][0],
                "source": source.relative_to(safe_root).as_posix(),
            }
        )

    page_counts = manifest.get("exercise_page_counts")
    if not isinstance(page_counts, dict):
        raise MetaError("exercise_page_counts doit être un objet")
    page_slots: list[int] = []
    try:
        for page, count in sorted(page_counts.items(), key=lambda item: int(item[0])):
            if type(count) is not int or count <= 0:
                raise ValueError
            page_slots.extend([int(page)] * count)
    except (TypeError, ValueError) as exc:
        raise MetaError("exercise_page_counts invalide") from exc
    if len(page_slots) != len(exercise_ids):
        raise MetaError("exercise_page_counts ne couvre pas exercise_order")

    pictograms = manifest.get("pictograms")
    if not isinstance(pictograms, dict):
        raise MetaError("pictograms doit être un objet")
    unknown_pictograms = set(pictograms) - set(exercise_ids)
    if unknown_pictograms:
        raise MetaError(f"ID de pictogramme inconnu: {sorted(unknown_pictograms)[0]}")
    if any(value not in {"python", "calculatrice"} for value in pictograms.values()):
        raise MetaError("pictogramme invalide")

    exercise_records: list[dict[str, Any]] = []
    for number, (object_id, page) in enumerate(
        zip(exercise_ids, page_slots, strict=True), start=1
    ):
        indexed = index.get(object_id)
        if indexed is None or indexed[0]["type_objet"] != "exercice":
            raise MetaError(f"ID d'exercice inconnu: {object_id}")
        meta, source = indexed
        exercise_records.append(
            {
                "id": object_id,
                "number": number,
                "method": meta["methodes"][0],
                "duration": meta["duree_min"],
                "parcours": meta["parcours"],
                "picto": pictograms.get(object_id),
                "source": source.relative_to(safe_root).as_posix(),
                "correction": meta["corrige_tex"],
                "page": page,
            }
        )

    rendered = manifest.get("rendered_method")
    if not isinstance(rendered, dict):
        raise MetaError("rendered_method doit être un objet")
    rendered_id = rendered.get("id")
    method_by_id = {record["id"]: record for record in method_records}
    if rendered_id not in method_by_id:
        raise MetaError(f"ID de méthode rendue inconnu: {rendered_id}")
    applications = rendered.get("applications")
    if not isinstance(applications, list) or any(
        not isinstance(application, str) or not application
        for application in applications
    ):
        raise MetaError("applications doit être une liste d'IDs")
    if len(applications) > 3:
        raise MetaError("applications doit contenir au plus trois IDs")
    if len(applications) != len(set(applications)):
        raise MetaError("ID dupliqué dans applications")
    exercise_by_id = {record["id"]: record for record in exercise_records}
    try:
        application_records = [exercise_by_id[object_id] for object_id in applications]
    except KeyError as exc:
        raise MetaError(f"ID d'application inconnu: {exc.args[0]}") from exc
    rendered_method = method_by_id[rendered_id]
    for application in application_records:
        if application["method"] != rendered_method["method"]:
            raise MetaError(
                f"application {application['id']} incompatible avec "
                f"{rendered_method['method']}"
            )

    compact_corrections = _manifest_id_list(manifest, "compact_corrections")
    unknown_corrections = set(compact_corrections) - set(exercise_by_id)
    if unknown_corrections:
        raise MetaError(
            f"ID de corrigé compact inconnu: {sorted(unknown_corrections)[0]}"
        )

    return {
        "methods": method_records,
        "exercises": exercise_records,
        "rendered_method": {
            "id": rendered_id,
            "method": rendered_method["method"],
            "applications": application_records,
            "fallback": len(application_records) < 2,
        },
    }


def _lookup(name: str, object_id: str, value: str) -> str:
    return f"\\expandafter\\def\\csname nxv@{name}@{object_id}\\endcsname{{{value}}}"


def _validate_reference_records(
    records: dict[str, Any], manifest: dict[str, Any]
) -> None:
    if type(manifest.get("expected_pages")) is not int or manifest["expected_pages"] != 15:
        raise MetaError("expected_pages doit être l'entier 15")
    method_ids = _validated_ids(manifest.get("methods"), "methods", _METHOD_ID, 4)
    exercise_ids = _validated_ids(
        manifest.get("exercise_order"), "exercise_order", _EXERCISE_ID, 20
    )
    if not isinstance(records, dict) or set(records) != {
        "methods",
        "exercises",
        "rendered_method",
    }:
        raise MetaError("table de renvois invalide")

    methods = records["methods"]
    if not isinstance(methods, list) or [
        record.get("id") for record in methods if isinstance(record, dict)
    ] != method_ids:
        raise MetaError("enregistrements de méthodes invalides")
    for record in methods:
        if (
            not isinstance(record, dict)
            or re.fullmatch(r"M[0-9]+", record.get("method", "")) is None
        ):
            raise MetaError("code méthode de rendu invalide")

    exercises = records["exercises"]
    if not isinstance(exercises, list) or [
        record.get("id") for record in exercises if isinstance(record, dict)
    ] != exercise_ids:
        raise MetaError("enregistrements d'exercices invalides")
    for number, record in enumerate(exercises, start=1):
        if (
            not isinstance(record, dict)
            or type(record.get("number")) is not int
            or record["number"] != number
            or type(record.get("duration")) is not int
            or record["duration"] <= 0
            or re.fullmatch(r"M[0-9]+", record.get("method", "")) is None
            or type(record.get("parcours")) is not int
            or record["parcours"] not in {1, 2, 3}
            or record.get("picto") not in {None, "python", "calculatrice"}
            or type(record.get("page")) is not int
            or record["page"] not in {9, 10}
        ):
            raise MetaError(f"enregistrement d'exercice invalide: {number}")

    rendered = records["rendered_method"]
    if not isinstance(rendered, dict) or set(rendered) != {
        "id",
        "method",
        "applications",
        "fallback",
    }:
        raise MetaError("enregistrement de méthode rendue invalide")
    method_by_id = {record["id"]: record for record in methods}
    if (
        rendered["id"] not in method_by_id
        or rendered["method"] != method_by_id[rendered["id"]]["method"]
        or type(rendered["fallback"]) is not bool
    ):
        raise MetaError("méthode rendue invalide")
    applications = rendered["applications"]
    exercise_by_id = {record["id"]: record for record in exercises}
    if not isinstance(applications, list) or len(applications) > 3:
        raise MetaError("applications de rendu invalides")
    for application in applications:
        if (
            not isinstance(application, dict)
            or application.get("id") not in exercise_by_id
            or application != exercise_by_id[application["id"]]
            or application["method"] != rendered["method"]
        ):
            raise MetaError("application de rendu invalide")
    if rendered["fallback"] != (len(applications) < 2):
        raise MetaError("indicateur de fallback invalide")


def render_reference_table(
    records: dict[str, Any], manifest: dict[str, Any]
) -> str:
    """Render metadata-only LaTeX lookups; never copy source object bodies."""
    _validate_reference_records(records, manifest)
    lines = [
        "% Generated by build_maquette_v5.py -- META lookups only.",
        "\\newif\\ifnxvPairingFallback",
    ]
    rendered_method = records["rendered_method"]
    lines.append(
        "\\nxvPairingFallbacktrue"
        if rendered_method["fallback"]
        else "\\nxvPairingFallbackfalse"
    )

    for method in records["methods"]:
        lines.append(
            _lookup(
                "method-label",
                method["id"],
                f"\\label{{meth:{method['id']}}}",
            )
        )

    difficulty = {
        1: "\\nxVFullDiamond\\nxVOutlineDiamond\\nxVOutlineDiamond",
        2: "\\nxVFullDiamond\\nxVFullDiamond\\nxVOutlineDiamond",
        3: "\\nxVFullDiamond\\nxVFullDiamond\\nxVFullDiamond",
    }
    correction_page = manifest.get("expected_pages")
    for exercise in records["exercises"]:
        object_id = exercise["id"]
        lines.extend(
            [
                _lookup("number", object_id, str(exercise["number"])),
                _lookup("duration", object_id, str(exercise["duration"])),
                _lookup("method", object_id, exercise["method"]),
                _lookup("parcours", object_id, str(exercise["parcours"])),
                _lookup("difficulty", object_id, difficulty[exercise["parcours"]]),
                _lookup("picto", object_id, exercise["picto"] or ""),
                _lookup(
                    "reference",
                    object_id,
                    f"→ {exercise['method']} · Corrigé p. {correction_page}",
                ),
                _lookup("page", object_id, str(exercise["page"])),
                _lookup("label", object_id, f"\\label{{ex:{object_id}}}"),
            ]
        )

    applications = rendered_method["applications"]
    if applications:
        visible_numbers = ", ".join(str(record["number"]) for record in applications)
        training = (
            f"S'entraîner : ex. {visible_numbers} p. {applications[0]['page']}"
        )
    else:
        training = ""
    lines.append(_lookup("training", rendered_method["method"], training))
    lines.append("\\newcommand{\\nxvCorrectionStartLabel}{\\label{corr:start}}")
    return "\n".join(lines) + "\n"


def _write_atomic_output(path: Path, rendered: str) -> None:
    temporary: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(rendered)
        temporary.replace(path)
    except OSError as exc:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
        raise MetaError(f"sortie impossible à écrire: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)

    try:
        manifest = load_manifest(args.manifest, Path.cwd())
        records = build_reference_table(manifest, Path.cwd())
        rendered = render_reference_table(records, manifest)
        _write_atomic_output(args.output, rendered)
    except MetaError as exc:
        print(f"META V5: {exc}", file=sys.stderr)
        return 2
    pictogram_count = sum(
        exercise["picto"] is not None for exercise in records["exercises"]
    )
    print(
        f"RENVOIS V5: {len(records['exercises'])} exercices, "
        f"1 méthode, {pictogram_count} pictogrammes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
