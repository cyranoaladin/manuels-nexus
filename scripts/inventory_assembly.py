"""Pure selection and validation helpers for declared assemblers."""

from __future__ import annotations

import ast
import fnmatch
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping

try:
    from scripts import inventory_graph
except ModuleNotFoundError:  # direct execution through inventory_collection.py
    import inventory_graph


class AssemblyAnalysisError(RuntimeError):
    """Raised when an assembler cannot be inspected safely."""


def _canonicalize_literal(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _canonicalize_literal(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (set, frozenset)):
        return sorted(_canonicalize_literal(item) for item in value)
    if isinstance(value, (list, tuple)):
        return [_canonicalize_literal(item) for item in value]
    return value


def _ast_latex_inputs(tree: ast.AST) -> list[tuple[str, str]]:
    inputs: set[tuple[str, str]] = set()
    for node in ast.walk(tree):
        text: str | None = None
        if isinstance(node, ast.JoinedStr):
            text = "".join(
                part.value
                for part in node.values
                if isinstance(part, ast.Constant) and isinstance(part.value, str)
            )
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            text = node.value
        if text:
            inputs.update(inventory_graph.latex_inputs(text))
    return sorted(inputs)


def analyze_assembler(path: Path | str) -> dict[str, Any]:
    """Read assembler declarations and generated LaTeX without importing code."""

    source = Path(path)
    try:
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=source.name)
    except SyntaxError as exc:
        detail = exc.msg + (f" (ligne {exc.lineno})" if exc.lineno else "")
        raise AssemblyAnalysisError(f"assembleur Python invalide: {detail}") from exc
    except (OSError, UnicodeError) as exc:
        raise AssemblyAnalysisError(
            f"assembleur Python illisible: {type(exc).__name__}"
        ) from exc

    constants: dict[str, Any] = {}
    accepted_names = {
        "CHAPITRES",
        "ELEVE_EXCLUDES",
        "ORDER",
        "VARIANTS",
        "VARIANTES",
    }
    for node in tree.body:
        name: str | None = None
        value_node: ast.AST | None = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                name = target.id
                value_node = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
            value_node = node.value
        if name not in accepted_names or value_node is None:
            continue
        try:
            constants[name] = _canonicalize_literal(ast.literal_eval(value_node))
        except (ValueError, TypeError):
            continue

    variants: set[str] = set()
    for name in ("VARIANTS", "VARIANTES"):
        value = constants.get(name, [])
        if isinstance(value, list):
            variants.update(item for item in value if isinstance(item, str))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "add_argument":
            continue
        option_names: list[str] = []
        for argument in node.args:
            try:
                literal = ast.literal_eval(argument)
            except (ValueError, TypeError):
                continue
            if isinstance(literal, str):
                option_names.append(literal)
        if "--variant" not in option_names:
            continue
        choices = next(
            (keyword.value for keyword in node.keywords if keyword.arg == "choices"),
            None,
        )
        if choices is None:
            continue
        if isinstance(choices, ast.Name) and choices.id in constants:
            literal_choices = constants[choices.id]
        else:
            try:
                literal_choices = ast.literal_eval(choices)
            except (ValueError, TypeError):
                continue
        if isinstance(literal_choices, (list, tuple, set, frozenset)):
            variants.update(item for item in literal_choices if isinstance(item, str))

    return {
        "constants": dict(sorted(constants.items())),
        "latex_inputs": _ast_latex_inputs(tree),
        "variants": sorted(variants),
    }


def valid_order(value: Any) -> list[list[str]]:
    if not isinstance(value, list):
        return []
    return [
        [item[0], item[1]]
        for item in value
        if isinstance(item, list)
        and len(item) == 2
        and all(isinstance(part, str) for part in item)
    ]


def validate_analysis(
    path: str,
    analysis: Mapping[str, Any],
) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    order = analysis["constants"].get("ORDER")
    if (
        not isinstance(order, list)
        or not order
        or len(valid_order(order)) != len(order)
    ):
        errors.append(("ORDER", "ORDER absent ou invalide"))
    variants = analysis.get("variants")
    if not isinstance(variants, list) or not variants:
        errors.append(("variants", "aucune variante litterale resolue"))
    if path.endswith("/scripts/assemble_manuel.py"):
        chapters = analysis["constants"].get("CHAPITRES")
        if (
            not isinstance(chapters, list)
            or not chapters
            or not all(isinstance(chapter, str) and chapter for chapter in chapters)
        ):
            errors.append(("CHAPITRES", "CHAPITRES absent ou invalide"))
    return errors


def select_items(
    objects: list[dict[str, Any]],
    order: Any,
    variant: str,
    *,
    exclusions: Any,
) -> tuple[list[dict[str, Any]], Counter[str]]:
    if variant == "methodes":
        rules: list[list[str]] = [["methodes", "*"]]
    elif variant == "remediation":
        rules = [["remediation", "*"]]
    elif variant == "amenagee":
        rules = [["amenagee", "*"]]
    else:
        rules = valid_order(order)
    excluded_directories = (
        {item for item in exclusions if isinstance(item, str)}
        if isinstance(exclusions, list)
        else set()
    )
    selected_candidates: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    for directory, pattern in rules:
        if directory in excluded_directories:
            continue
        filename_pattern = pattern + ".tex"
        matches = sorted(
            (
                item
                for item in objects
                if PurePosixPath(item["path"]).parent.name == directory
                and fnmatch.fnmatchcase(
                    PurePosixPath(item["path"]).name, filename_pattern
                )
            ),
            key=lambda item: item["path"],
        )
        if directory == "exercices":
            matches = [
                item for item in matches if not item["path"].endswith("-CDP.tex")
            ] + [item for item in matches if item["path"].endswith("-CDP.tex")]
        selected_candidates.extend(matches)
        counts.update(item["path"] for item in matches)
    seen: set[str] = set()
    selected: list[dict[str, Any]] = []
    for item in selected_candidates:
        if item["path"] in seen:
            continue
        seen.add(item["path"])
        selected.append(item)
    duplicates = Counter({path: count for path, count in counts.items() if count > 1})
    return selected, duplicates


def _anomaly(source: str, target: str, field: str, reason: str) -> dict[str, str]:
    return {
        "champ": field,
        "cible": target,
        "raison": reason,
        "source": source,
    }


def _all_objects(inventory: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        (
            item
            for manual in inventory["manuals"].values()
            for chapter in manual["chapters"].values()
            for item in chapter["objects"]
        ),
        key=lambda item: item["path"],
    )


def _append_assembly(
    inventory: dict[str, Any],
    *,
    assembly_id: str,
    assembler_path: str,
    manual: str,
    scope: str,
    variant: str,
    chapters: list[str],
    eligible_objects: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    duplicates: Counter[str],
) -> None:
    selected_paths = [item["path"] for item in selected]
    selected_set = set(selected_paths)
    excluded_types = sorted(
        {
            item["source_type"]
            for item in eligible_objects
            if item["path"] not in selected_set
        }
    )
    inventory["assemblies"].append(
        {
            "assembler": assembler_path,
            "assembly_id": assembly_id,
            "chapters": list(chapters),
            "excluded_source_types": excluded_types,
            "included_files": list(selected_paths),
            "included_objects": list(selected_paths),
            "manual": manual,
            "scope": scope,
            "variant": variant,
        }
    )
    for path, count in sorted(duplicates.items()):
        inventory["anomalies"]["duplicate_assembly_objects"].append(
            _anomaly(
                assembler_path,
                path,
                assembly_id,
                f"{count} regles de glob selectionnent le meme objet; "
                "l'assembleur le deduplique",
            )
        )


def _build_chapter_assemblies(
    inventory: dict[str, Any],
    assembler_path: str,
    analysis: dict[str, Any],
    manual: str,
    chapter: str,
    objects: list[dict[str, Any]],
    *,
    assembly_project_name: Callable[[str], str],
) -> None:
    for variant in analysis["variants"]:
        assembly_id = f"{assembly_project_name(manual)}:chapter:{chapter}:{variant}"
        selected, duplicates = select_items(
            objects,
            analysis["constants"].get("ORDER", []),
            variant,
            exclusions=(),
        )
        _append_assembly(
            inventory,
            assembly_id=assembly_id,
            assembler_path=assembler_path,
            manual=manual,
            scope="chapter",
            variant=variant,
            chapters=[chapter],
            eligible_objects=objects,
            selected=selected,
            duplicates=duplicates,
        )


def _build_manual_assemblies(
    inventory: dict[str, Any],
    assembler_path: str,
    analysis: dict[str, Any],
    manual: str,
    chapters: list[str],
    objects_by_chapter: Mapping[str, list[dict[str, Any]]],
    *,
    assembly_project_name: Callable[[str], str],
) -> None:
    constants = analysis["constants"]
    student_excludes = constants.get("ELEVE_EXCLUDES", [])
    for variant in analysis["variants"]:
        selected: list[dict[str, Any]] = []
        duplicate_counts: Counter[str] = Counter()
        inclusion_counts: Counter[str] = Counter()
        eligible: list[dict[str, Any]] = []
        exclusions = student_excludes if variant == "eleve" else []
        for chapter in chapters:
            chapter_objects = objects_by_chapter.get(chapter, [])
            eligible.extend(chapter_objects)
            chapter_selected, chapter_duplicates = select_items(
                chapter_objects,
                constants.get("ORDER", []),
                variant,
                exclusions=exclusions,
            )
            selected.extend(chapter_selected)
            inclusion_counts.update(item["path"] for item in chapter_selected)
            duplicate_counts.update(chapter_duplicates)
        assembly_id = f"{assembly_project_name(manual)}:manual:{manual}:{variant}"
        _append_assembly(
            inventory,
            assembly_id=assembly_id,
            assembler_path=assembler_path,
            manual=manual,
            scope="manual",
            variant=variant,
            chapters=chapters,
            eligible_objects=eligible,
            selected=selected,
            duplicates=duplicate_counts,
        )
        for selected_path, count in sorted(inclusion_counts.items()):
            if count > 1:
                inventory["anomalies"]["duplicate_assembly_objects"].append(
                    _anomaly(
                        assembler_path,
                        selected_path,
                        assembly_id,
                        f"objet inclus {count} fois car CHAPITRES contient un "
                        "chapitre duplique",
                    )
                )


def _add_dynamic_dependencies(
    inventory: dict[str, Any],
    root: Path,
    tracked: frozenset[str],
    *,
    project_for_manual: Callable[[str], str],
    resolve_latex_target: Callable[[str, str, frozenset[str]], str],
) -> None:
    analyses: dict[str, dict[str, Any]] = {}
    for assembly in inventory["assemblies"]:
        if assembly["scope"] not in {"chapter", "manual"}:
            continue
        dependencies: list[str] = []
        project = project_for_manual(assembly["manual"])
        for chapter in assembly["chapters"]:
            dependencies.append(f"{project}/chapitres/{chapter}/contrat.yaml")
        if assembly["scope"] == "chapter":
            dependencies.append(f"{project}/gabarits/chapitre_master.tex")
        else:
            assembler_path = assembly["assembler"]
            if assembler_path not in analyses:
                try:
                    analyses[assembler_path] = analyze_assembler(root / assembler_path)
                except AssemblyAnalysisError:
                    analyses[assembler_path] = {"latex_inputs": []}
            for _command, raw_target in analyses[assembler_path].get(
                "latex_inputs", []
            ):
                dependencies.append(
                    resolve_latex_target(assembler_path, raw_target, tracked)
                )
        for dependency in dict.fromkeys(dependencies):
            if dependency in tracked and (root / dependency).is_file():
                if dependency not in assembly["included_files"]:
                    assembly["included_files"].append(dependency)
                continue
            inventory["anomalies"]["broken_assembly_references"].append(
                _anomaly(
                    assembly["assembler"],
                    dependency,
                    assembly["assembly_id"],
                    "dependance dynamique d'assemblage absente",
                )
            )


def add_declared_assemblies(
    inventory: dict[str, Any],
    root: Path,
    tracked: frozenset[str],
    *,
    manual_ids: tuple[str, ...],
    manual_for_chapter: Callable[[str], str | None],
    supported_manuals: Callable[[str], tuple[str, ...]],
    project_for_manual: Callable[[str], str],
    assembly_project_name: Callable[[str], str],
    chapter_directory: Callable[[str, str], str],
    resolve_latex_target: Callable[[str, str, frozenset[str]], str],
) -> None:
    """Discover assemblers, build variants and compute actual manual coverage."""

    anomalies = inventory["anomalies"]
    objects = _all_objects(inventory)
    objects_by_chapter: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in objects:
        objects_by_chapter[item["path_chapter"]].append(item)
    for chapter_objects in objects_by_chapter.values():
        chapter_objects.sort(key=lambda item: item["path"])

    assembler_paths = sorted(
        path
        for path in tracked
        if path.endswith("/scripts/assemble.py")
        or path.endswith("/scripts/assemble_manuel.py")
    )
    analyses: dict[str, dict[str, Any]] = {}
    for path in assembler_paths:
        try:
            analysis = analyze_assembler(root / path)
        except AssemblyAnalysisError as exc:
            anomalies["assembler_invalid"].append(_anomaly(path, path, "AST", str(exc)))
            continue
        validation_errors = validate_analysis(path, analysis)
        if validation_errors:
            anomalies["assembler_invalid"].extend(
                _anomaly(path, path, field, reason)
                for field, reason in validation_errors
            )
            continue
        analyses[path] = analysis

    manual_engine_manuals: set[str] = set()
    chapter_engine_manuals: set[str] = set()
    for path, analysis in sorted(analyses.items()):
        if path.endswith("/scripts/assemble_manuel.py"):
            chapters = analysis["constants"].get("CHAPITRES", [])
            if not isinstance(chapters, list):
                continue
            chapters = [item for item in chapters if isinstance(item, str)]
            grouped: dict[str, list[str]] = defaultdict(list)
            declared_manuals: set[str] = set()
            for index, chapter in enumerate(chapters):
                manual = manual_for_chapter(chapter)
                if manual is None:
                    anomalies["broken_assembly_references"].append(
                        _anomaly(
                            path,
                            chapter,
                            f"CHAPITRES[{index}]",
                            "prefixe de chapitre inconnu dans CHAPITRES",
                        )
                    )
                    continue
                declared_manuals.add(manual)
                if chapter not in inventory["manuals"][manual]["chapters"]:
                    anomalies["broken_assembly_references"].append(
                        _anomaly(
                            path,
                            chapter,
                            f"CHAPITRES[{index}]",
                            "chapitre declare par l'assembleur absent des sources suivies",
                        )
                    )
                    continue
                grouped[manual].append(chapter)
            manual_engine_manuals.update(declared_manuals)
            for manual, manual_chapters in sorted(grouped.items()):
                _build_manual_assemblies(
                    inventory,
                    path,
                    analysis,
                    manual,
                    manual_chapters,
                    objects_by_chapter,
                    assembly_project_name=assembly_project_name,
                )
        else:
            supported = supported_manuals(path)
            chapter_engine_manuals.update(supported)
            for manual in supported:
                for chapter in sorted(inventory["manuals"][manual]["chapters"]):
                    _build_chapter_assemblies(
                        inventory,
                        path,
                        analysis,
                        manual,
                        chapter,
                        objects_by_chapter.get(chapter, []),
                        assembly_project_name=assembly_project_name,
                    )

    _add_dynamic_dependencies(
        inventory,
        root,
        tracked,
        project_for_manual=project_for_manual,
        resolve_latex_target=resolve_latex_target,
    )
    manual_covered_chapters: dict[str, set[str]] = defaultdict(set)
    for assembly in inventory["assemblies"]:
        if assembly["scope"] == "manual" and assembly["manual"] in manual_ids:
            manual_covered_chapters[assembly["manual"]].update(assembly["chapters"])

    for manual in sorted(manual_ids):
        project = project_for_manual(manual)
        if manual not in chapter_engine_manuals:
            anomalies["missing_assemblers"].append(
                _anomaly(
                    f"{project}/scripts/assemble.py",
                    manual,
                    "chapitre",
                    "aucun assembleur de chapitre suivi",
                )
            )
        if manual not in manual_engine_manuals:
            anomalies["missing_assemblers"].append(
                _anomaly(
                    f"{project}/scripts/assemble_manuel.py",
                    manual,
                    "manuel",
                    "aucun assembleur de manuel suivi",
                )
            )
        for chapter in sorted(inventory["manuals"][manual]["chapters"]):
            if chapter not in manual_covered_chapters[manual]:
                chapter_model = inventory["manuals"][manual]["chapters"][chapter]
                anomalies["chapters_not_in_manual"].append(
                    _anomaly(
                        chapter_model["contract_path"]
                        or chapter_directory(manual, chapter),
                        chapter,
                        "CHAPITRES",
                        "chapitre absent de tout assemblage de manuel",
                    )
                )


def add_unassembled_objects(inventory: dict[str, Any]) -> None:
    assembled = {
        path
        for assembly in inventory["assemblies"]
        for path in assembly["included_objects"]
    }
    for item in _all_objects(inventory):
        if item["path"] not in assembled:
            inventory["anomalies"]["unassembled_objects"].append(
                _anomaly(
                    item["path"],
                    item["path"],
                    "assemblages_declares",
                    "objet META exclu de tous les assemblages declares",
                )
            )
