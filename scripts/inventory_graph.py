"""Pure helpers for the collection reference graph."""

from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Mapping


METHOD_ALIAS_RE = re.compile(r"M[1-9]\d*")
METHOD_ID_SUFFIX_RE = re.compile(r"(?:^|-)(?:ME-0*|M0*)([1-9]\d*)$")


def method_aliases(item: Mapping[str, Any]) -> list[str]:
    """Return declared aliases, or a verified ID-suffix fallback."""

    declared = item["metadata"].get("methodes")
    if isinstance(declared, list):
        aliases = sorted(
            {
                value
                for value in declared
                if isinstance(value, str) and METHOD_ALIAS_RE.fullmatch(value)
            }
        )
        if aliases:
            return aliases
    match = METHOD_ID_SUFFIX_RE.search(item["id"])
    return [f"M{int(match.group(1))}"] if match else []


def index_method_aliases(
    methods: list[dict[str, Any]],
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    """Index aliases by physical chapter without inventing positional numbers."""

    index: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for method in methods:
        for alias in method_aliases(method):
            index[method["path_chapter"]][alias].append(method)
    return {
        chapter: {alias: candidates for alias, candidates in aliases.items()}
        for chapter, aliases in index.items()
    }


def strip_latex_comment(line: str) -> str:
    for index, character in enumerate(line):
        if character != "%":
            continue
        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and line[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2 == 0:
            return line[:index]
    return line


def latex_inputs(source: str) -> list[tuple[str, str]]:
    uncommented = "\n".join(strip_latex_comment(line) for line in source.splitlines())
    references = [
        (match.group(1), match.group(2).strip())
        for match in re.finditer(r"\\(input|include)\s*\{([^{}]+)\}", uncommented)
        if not any(token in match.group(2) for token in ("\\", "%", "#"))
    ]
    references.extend(
        ("input_if_exists", match.group(1).strip())
        for match in re.finditer(r"\\InputIfFileExists\s*\{([^{}]+)\}", uncommented)
    )
    references.extend(
        (
            "documentclass",
            match.group(1).strip()
            if PurePosixPath(match.group(1).strip()).suffix
            else match.group(1).strip() + ".cls",
        )
        for match in re.finditer(
            r"\\documentclass(?:\[[^]]*\])?\s*\{([^{}]+)\}", uncommented
        )
    )
    return references


def source_digest(root: Path, paths: tuple[str, ...]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        encoded_path = path.encode("utf-8", errors="surrogateescape")
        digest.update(len(encoded_path).to_bytes(8, "big"))
        digest.update(encoded_path)
        source = root / path
        if source.is_file():
            digest.update(b"F")
            content = source.read_bytes()
            digest.update(len(content).to_bytes(8, "big"))
            digest.update(content)
        else:
            digest.update(b"M")
            digest.update((0).to_bytes(8, "big"))
    return "sha256:" + digest.hexdigest()


def reachable_latex_files(
    reference_graph: list[dict[str, Any]],
    roots: set[str],
) -> set[str]:
    """Compute reachability only from production roots and assembly inputs."""

    adjacency: dict[str, list[str]] = defaultdict(list)
    for edge in reference_graph:
        if edge["kind"] == "latex" and edge["resolved"]:
            adjacency[edge["source"]].append(edge["cible"])
    reachable = set(roots)
    pending = list(sorted(roots, reverse=True))
    while pending:
        source = pending.pop()
        for target in adjacency.get(source, []):
            if target in reachable:
                continue
            reachable.add(target)
            pending.append(target)
    return reachable


def _anomaly(source: str, target: str, field: str, reason: str) -> dict[str, str]:
    return {
        "champ": field,
        "cible": target,
        "raison": reason,
        "source": source,
    }


def add_latex_graph(
    inventory: dict[str, Any],
    root: Path,
    tracked: frozenset[str],
    *,
    is_relevant_tex: Any,
    resolve_latex_target: Any,
) -> None:
    """Scan all production TeX/class sources and append their dependency edges."""

    for source in sorted(path for path in tracked if is_relevant_tex(path)):
        try:
            tex = (root / source).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for command, raw_target in latex_inputs(tex):
            target = resolve_latex_target(source, raw_target, tracked)
            resolved = target in tracked
            if command == "documentclass" and "/" not in raw_target and not resolved:
                continue
            inventory["reference_graph"].append(
                {
                    "champ": command,
                    "cible": target,
                    "kind": "latex",
                    "resolved": resolved,
                    "source": source,
                }
            )
            if not resolved:
                inventory["anomalies"]["broken_latex_references"].append(
                    _anomaly(
                        source,
                        target,
                        command,
                        "cible LaTeX absente des sources suivies",
                    )
                )


def add_static_latex_assemblies(
    inventory: dict[str, Any],
    root: Path,
    tracked: frozenset[str],
    *,
    is_relevant_tex: Any,
    chapter_id_from_source: Any,
    manual_for_chapter: Any,
) -> None:
    """Build deterministic static assemblies by traversing the LaTeX graph."""

    objects_by_path = {
        item["path"]: item
        for manual in inventory["manuals"].values()
        for chapter in manual["chapters"].values()
        for item in chapter["objects"]
    }
    adjacency: dict[str, list[str]] = defaultdict(list)
    for edge in inventory["reference_graph"]:
        if edge["kind"] == "latex" and edge["resolved"]:
            adjacency[edge["source"]].append(edge["cible"])

    roots: list[str] = []
    for path in sorted(
        item for item in tracked if is_relevant_tex(item) and item.endswith(".tex")
    ):
        try:
            source = (root / path).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        if re.search(r"\\documentclass(?:\[[^]]*\])?\s*\{", source):
            roots.append(path)

    for static_root in roots:
        reachable: list[str] = []
        object_occurrences: list[str] = []
        project = "nsi" if static_root.startswith("NSI/") else "math"
        assembly_id = f"{project}:static:{static_root}"
        traversal: list[tuple[str, tuple[str, ...], int]] = [
            (static_root, (static_root,), 0)
        ]
        reported_cycles: set[tuple[str, str]] = set()
        while traversal:
            source, path_stack, edge_index = traversal[-1]
            targets = adjacency.get(source, [])
            if edge_index >= len(targets):
                traversal.pop()
                continue
            target = targets[edge_index]
            traversal[-1] = (source, path_stack, edge_index + 1)
            reachable.append(target)
            if target in objects_by_path:
                object_occurrences.append(target)
            if target not in adjacency:
                continue
            if target in path_stack:
                cycle_key = (source, target)
                if cycle_key not in reported_cycles:
                    inventory["anomalies"]["latex_cycles"].append(
                        _anomaly(
                            source,
                            target,
                            assembly_id,
                            "cycle de references LaTeX dans l'assemblage statique",
                        )
                    )
                    reported_cycles.add(cycle_key)
                continue
            traversal.append((target, path_stack + (target,), 0))
        included_objects = list(dict.fromkeys(object_occurrences))
        included_files = list(dict.fromkeys(reachable))
        chapters = sorted(
            {
                chapter_id_from_source(path)
                for path in included_objects
                if chapter_id_from_source(path) is not None
            }
        )
        manuals = sorted(
            {
                manual
                for chapter in chapters
                if (manual := manual_for_chapter(chapter)) is not None
            }
        )
        variant = "maquette-v5" if "/maquette-v5/" in static_root else None
        inventory["assemblies"].append(
            {
                "assembler": static_root,
                "assembly_id": assembly_id,
                "chapters": chapters,
                "excluded_source_types": [],
                "included_files": included_files,
                "included_objects": included_objects,
                "manual": manuals[0] if len(manuals) == 1 else None,
                "scope": "static",
                "variant": variant,
            }
        )
        for path, count in sorted(Counter(object_occurrences).items()):
            if count > 1:
                inventory["anomalies"]["duplicate_assembly_objects"].append(
                    _anomaly(
                        static_root,
                        path,
                        assembly_id,
                        f"objet inclus {count} fois dans le meme assemblage LaTeX",
                    )
                )


def add_orphan_files(
    inventory: dict[str, Any],
    root: Path,
    tracked: frozenset[str],
    *,
    is_relevant_tex: Any,
    is_known_latex_root: Any,
    chapter_context: Any,
) -> None:
    """Report only files outside the closure of genuine production roots."""

    object_paths = {
        item["path"]
        for manual in inventory["manuals"].values()
        for chapter in manual["chapters"].values()
        for item in chapter["objects"]
    }
    assembly_roots = {
        path
        for assembly in inventory["assemblies"]
        for path in assembly.get("included_files", assembly["included_objects"])
    }
    production_roots = {
        path
        for path in tracked
        if is_relevant_tex(path) and is_known_latex_root(root, path)
    }
    reachable = reachable_latex_files(
        inventory["reference_graph"], assembly_roots | production_roots
    )
    for path in sorted(
        item for item in tracked if is_relevant_tex(item) and item.endswith(".tex")
    ):
        if path in object_paths or path in reachable:
            continue
        role = (
            "chapter_source_without_meta"
            if chapter_context(path) is not None
            else "latex_source"
        )
        item = _anomaly(
            path,
            path,
            "reachability",
            "fichier LaTeX suivi sans META, non reference et hors assemblage",
        )
        item["role"] = role
        inventory["anomalies"]["orphan_files"].append(item)
