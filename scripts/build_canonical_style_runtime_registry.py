#!/usr/bin/env python3
"""Build the factual registry of Nexus LaTeX charter/runtime sources.

The registry deliberately separates three kinds of evidence:

* physical source files and their byte digests;
* direct source references made by assemblers or LaTeX entry points;
* observed ``.fls`` inputs, with an explicit freshness classification.

It does not migrate, delete, compile, or approve any charter source.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "audit" / "CANONICAL_STYLE_RUNTIME_REGISTRY.json"
DEFAULT_MD = ROOT / "audit" / "CANONICAL_STYLE_RUNTIME_REGISTRY.md"
DEFAULT_GRAPH_JSON = ROOT / "audit" / "STYLE_CONSUMER_GRAPH.json"
DEFAULT_GRAPH_MD = ROOT / "audit" / "STYLE_CONSUMER_GRAPH.md"
DEFAULT_DUPLICATES_JSON = ROOT / "audit" / "STYLE_DUPLICATE_FORENSICS.json"
DEFAULT_DUPLICATES_MD = ROOT / "audit" / "STYLE_DUPLICATE_FORENSICS.md"

CANONICAL_CLASS = "gabarits/common/nexus-manuel.cls"
CANONICAL_STYLE = "gabarits/common/nexus-charte.sty"
CANONICAL_PREFIXES = ("gabarits/common/", "gabarits/maths/", "gabarits/nsi/")
EXCLUDED_PARTS = {".git", ".worktrees", "build", "node_modules", "tmp"}
REFERENCE_SUFFIXES = {".py", ".tex", ".cls", ".sty", ".lua"}
LEGACY_REFERENCE_DIR = "reference-" + "v4"

MATHS_PREFIX = "Mathematiques/manuel-maths/gabarits/"
NSI_PREFIX = "NSI/gabarits/"

MATHS_FINAL_CONSUMERS = tuple(
    f"{manual}:{variant}"
    for manual in ("1SPE", "TSPE", "TCOMPL", "TEXPERTES")
    for variant in ("eleve", "professeur")
)
NSI_FINAL_CONSUMERS = tuple(
    f"{manual}:{variant}"
    for manual in ("1NSI", "TNSI")
    for variant in ("eleve", "professeur")
)
FINAL_CONSUMERS = MATHS_FINAL_CONSUMERS + NSI_FINAL_CONSUMERS

ACTIVE_WRAPPERS = {
    f"{prefix}{name}"
    for prefix in (MATHS_PREFIX, NSI_PREFIX)
    for name in ("nexus-manuel.cls", "nexus-manuel-v5.cls", "nexus-charte-v6.sty")
}
DORMANT_WRAPPERS = {
    f"{prefix}{name}"
    for prefix in (MATHS_PREFIX, NSI_PREFIX)
    for name in (
        "nexus-boites-v6.sty",
        "nexus-couverture.sty",
        "nexus-decor.sty",
        "nexus-exercices-v6.sty",
        "nexus-figures-bib.sty",
        "nexus-pages-froides.sty",
        "nexus-pont-v6.sty",
    )
}
VISUAL_FIXTURES = {
    f"{MATHS_PREFIX}specimen.tex",
    f"{MATHS_PREFIX}specimen-v6.tex",
    f"{MATHS_PREFIX}specimen-pont-v6.tex",
    f"{NSI_PREFIX}specimen.tex",
}
REFERENCE_ONLY = {"NSI/corpus_nsi/02_modeles_documents/nsi-preamble.sty"}

LOCAL_RUNTIME_NAMES = (
    "nexus-code.tex",
    "nexus-figures.tex",
    "nexus-figures-nsi.tex",
    "nexus-icons.tex",
    "nexus-margin-rail.tex",
    "nexus-margin-shipout.lua",
    "nexus-margin-json.lua",
    "nexus-margin-layout.lua",
    "nexus-signatures.tex",
    "logo_nexus.png",
)
NONCANONICAL_PRODUCTION_INPUTS = {
    f"{MATHS_PREFIX}chapitre_master.tex",
    f"{NSI_PREFIX}book_master.tex",
    f"{NSI_PREFIX}chapitre_master.tex",
    *ACTIVE_WRAPPERS,
    *(f"{prefix}{name}" for prefix in (MATHS_PREFIX, NSI_PREFIX) for name in LOCAL_RUNTIME_NAMES),
}

LATEX_REFERENCE_RE = re.compile(
    r"\\(?:documentclass|usepackage|RequirePackage|input|include|IfFileExists|"
    r"nxRequireCommonModule)(?:\[[^\]]*\])?\{([^}]+)\}"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_excluded(path: Path, root: Path, *, allow_build: bool = False) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return True
    for part in parts:
        if part.startswith("."):
            return True
        if part in EXCLUDED_PARTS and not (allow_build and part == "build"):
            return True
    return False


def source_files(root: Path) -> list[Path]:
    """Return every physical class, style, and TeX file under a gabarit tree."""

    found: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or is_excluded(path, root):
            continue
        rel = path.relative_to(root)
        if path.suffix in {".cls", ".sty"}:
            found.append(path)
        elif path.suffix == ".tex" and "gabarits" in rel.parts:
            found.append(path)
    return sorted(set(found), key=lambda item: relative(item, root))


def asset_files(root: Path) -> list[Path]:
    """Return the closed style/runtime asset scope used by T3 forensics."""

    found = set(source_files(root))
    for path in root.rglob("*"):
        if not path.is_file() or is_excluded(path, root):
            continue
        rel = path.relative_to(root)
        if "gabarits" not in rel.parts:
            continue
        if path.suffix in {".lua", ".otf"} or path.name == "logo_nexus.png":
            found.add(path)
    return sorted(found, key=lambda item: relative(item, root))


def _digest_groups(paths: Iterable[Path], root: Path) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for path in paths:
        groups[sha256(path)].append(relative(path, root))
    return {digest: sorted(members) for digest, members in sorted(groups.items())}


def role_for(path: str, text: str) -> str:
    pure = PurePosixPath(path)
    historical = LEGACY_REFERENCE_DIR in pure.parts or "archive" in pure.parts
    wrapper = "Redirection canonique" in text or "Wrapper Compatibilite" in text

    if historical:
        return "HISTORICAL_REFERENCE"
    if pure.suffix == ".cls":
        if path == CANONICAL_CLASS:
            return "CANONICAL_CLASS_IMPLEMENTATION"
        if wrapper:
            return "COMPATIBILITY_CLASS_WRAPPER"
        return "NONCANONICAL_CLASS_IMPLEMENTATION"
    if pure.suffix == ".sty":
        if path == CANONICAL_STYLE:
            return "CANONICAL_STYLE_IMPLEMENTATION"
        if path.startswith("gabarits/maths/") or path.startswith("gabarits/nsi/"):
            return "CANONICAL_DISCIPLINE_ADAPTER"
        if path.startswith("gabarits/common/"):
            return "CANONICAL_SUPPORT_STYLE"
        if wrapper:
            return "COMPATIBILITY_STYLE_WRAPPER"
        if pure.name == "nsi-preamble.sty":
            return "REFERENCE_MODEL_STYLE"
        return "NONCANONICAL_SUPPORT_STYLE"
    if pure.name == "book_master.tex":
        return "BOOK_RUNTIME_TEMPLATE"
    if pure.name == "chapitre_master.tex":
        return "CHAPTER_RUNTIME_TEMPLATE"
    if pure.name == "objet_standalone.tex":
        return "OBJECT_RUNTIME_TEMPLATE"
    if "specimen" in pure.stem:
        return "VISUAL_SPECIMEN_TEMPLATE"
    if pure.name.startswith("nexus-"):
        return "RUNTIME_SUPPORT_TEMPLATE"
    return "GABARIT_TEMPLATE"


def is_canonical(path: str) -> bool:
    return path.startswith(CANONICAL_PREFIXES)


def _project_prefix(path: str) -> str | None:
    if path.startswith("Mathematiques/manuel-maths/"):
        return "Mathematiques/manuel-maths/"
    if path.startswith("NSI/"):
        return "NSI/"
    return None


def _normalise_target(raw: str) -> str:
    value = raw.strip().replace("\\", "/")
    value = re.sub(r"^\./", "", value)
    while "/../" in f"/{value}/":
        normalised = os.path.normpath(value).replace("\\", "/")
        if normalised == value:
            break
        value = normalised
    return value


def _target_matches_entry(raw: str, entry_path: str, consumer_path: str) -> bool:
    """Conservatively link a literal LaTeX/script target to a source entry."""

    target = _normalise_target(raw)
    target_no_ext = target.removesuffix(".cls").removesuffix(".sty").removesuffix(".tex")
    entry_no_ext = entry_path.rsplit(".", 1)[0]
    if target_no_ext == entry_no_ext:
        return True

    project = _project_prefix(consumer_path)
    if project and target_no_ext.startswith("gabarits/"):
        if f"{project}{target_no_ext}" == entry_no_ext:
            return True
    if target_no_ext.startswith("gabarits/common/"):
        return target_no_ext == entry_no_ext

    # Wrapper sources use ../../gabarits/common/... while compiled from the
    # project root.  The suffix is unambiguous and is retained as evidence.
    if "/gabarits/common/" in f"/{target_no_ext}":
        suffix = target_no_ext.split("gabarits/common/", 1)[1]
        return entry_no_ext == f"gabarits/common/{suffix}"

    # Bare package names are only attributed inside the same project tree.
    if "/" not in target_no_ext and project:
        return PurePosixPath(entry_no_ext).stem == target_no_ext and entry_path.startswith(project)
    return False


def direct_references(root: Path, entries: Iterable[str]) -> dict[str, list[dict[str, Any]]]:
    entry_paths = tuple(entries)
    found: dict[str, list[dict[str, Any]]] = {path: [] for path in entry_paths}
    candidates = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in REFERENCE_SUFFIXES:
            continue
        if is_excluded(path, root):
            continue
        rel = relative(path, root)
        if rel.startswith(("audit/", "docs/")) or "/tests/" in f"/{rel}":
            continue
        if rel == "scripts/build_canonical_style_runtime_registry.py":
            continue
        candidates.append(path)

    for consumer in sorted(candidates, key=lambda item: relative(item, root)):
        consumer_rel = relative(consumer, root)
        for line_number, line in enumerate(
            consumer.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1
        ):
            stripped = line.strip()
            if not stripped or stripped.startswith(("%", "#")):
                continue
            targets = LATEX_REFERENCE_RE.findall(line)
            kind = "LATEX_COMMAND"
            if consumer.suffix == ".py":
                kind = "ASSEMBLER_LITERAL"
                targets.extend(
                    match.group(1)
                    for match in re.finditer(
                        r"[\"']([^\"']+(?:\.cls|\.sty|_master\.tex|book_master\.tex|"
                        r"chapitre_master\.tex|objet_standalone\.tex))[\"']",
                        line,
                    )
                )
            for target in dict.fromkeys(targets):
                for entry_path in entry_paths:
                    if consumer_rel == entry_path:
                        continue
                    if not _target_matches_entry(target, entry_path, consumer_rel):
                        continue
                    proof = {
                        "path": consumer_rel,
                        "line": line_number,
                        "kind": kind,
                        "target_literal": target,
                    }
                    if proof not in found[entry_path]:
                        found[entry_path].append(proof)
    return found


def _logical_pwd(recorded_pwd: str, root: Path) -> tuple[Path | None, bool]:
    """Map a recorder PWD to this checkout while retaining worktree identity."""

    pwd = Path(recorded_pwd)
    try:
        pwd.relative_to(root)
        return pwd, True
    except ValueError:
        pass
    text = pwd.as_posix()
    for suffix in ("/Mathematiques/manuel-maths", "/NSI"):
        if text.endswith(suffix):
            return root / suffix.removeprefix("/"), False
    return None, False


def _attestation_sha_for(fls: Path, root: Path) -> str | None:
    cursor = fls.parent
    while cursor != root.parent:
        manifest = cursor / "manifest.json"
        if manifest.is_file():
            try:
                payload = json.loads(manifest.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return None
            value = payload.get("git_sha")
            return value if isinstance(value, str) and value else None
        if cursor == root:
            break
        cursor = cursor.parent
    return None


def _current_git_sha(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _classify_fls_freshness(
    attested_sha: str | None, current_sha: str | None
) -> tuple[str, bool | None]:
    if not attested_sha:
        return "UNATTESTED_IGNORED", None
    if current_sha and attested_sha == current_sha:
        return "ATTESTED_CURRENT", False
    return "STALE_ATTESTED_OTHER_SHA", True


def _fls_identity(path: Path) -> tuple[str, str]:
    name = path.name.lower()
    joined = path.as_posix().upper()
    variant = "professeur" if "professeur" in name else "eleve" if "eleve" in name else "maquette"
    if "MANUEL_1SPE" in joined:
        return "1SPE", variant
    if "MANUEL_TSPE" in joined:
        return "TSPE", variant
    if "MANUEL_TCOMPL" in joined:
        return "TCOMPL", variant
    if "MANUEL_TEXPERTES" in joined:
        return "TEXPERTES", variant
    if "MANUEL_1NSI" in joined:
        return "1NSI", variant
    if "MANUEL_TNSI" in joined:
        return "TNSI", variant
    return "D7_MAQUETTE", variant


def fls_observations(root: Path, entries: Iterable[str]) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    entry_set = set(entries)
    observations: dict[str, list[dict[str, Any]]] = {path: [] for path in entry_set}
    recorders: list[dict[str, Any]] = []

    # Canonical reports must not depend on ignored, mutable build directories.
    # A recorder becomes evidence only after it is copied below audit/ beside
    # a manifest carrying an explicit source SHA.  Stale attestations remain
    # useful forensic evidence; unattested build products are ignored.
    audit_root = root / "audit"
    fls_files = sorted(
        (
            path
            for path in audit_root.rglob("*.fls")
            if path.is_file()
            and not is_excluded(path, root, allow_build=True)
            and _attestation_sha_for(path, root)
        ),
        key=lambda item: relative(item, root),
    ) if audit_root.is_dir() else []
    current_sha = _current_git_sha(root)
    for fls in fls_files:
        lines = fls.read_text(encoding="utf-8", errors="ignore").splitlines()
        pwd_line = next((line[4:].strip() for line in lines if line.startswith("PWD ")), "")
        logical_pwd, _ = _logical_pwd(pwd_line, root)
        attested_sha = _attestation_sha_for(fls, root)
        freshness, stale = _classify_fls_freshness(attested_sha, current_sha)

        manual, variant = _fls_identity(fls)
        recorder = {
            "fls_path": relative(fls, root),
            "manual": manual,
            "variant": variant,
            "recorded_pwd": pwd_line,
            "freshness": freshness,
            "stale": stale,
            "attested_git_sha": attested_sha,
            "matched_registry_inputs": 0,
        }
        if logical_pwd is not None:
            for line in lines:
                if not line.startswith("INPUT "):
                    continue
                raw = line[6:].strip()
                raw_path = Path(raw)
                resolved = raw_path if raw_path.is_absolute() else logical_pwd / raw_path
                try:
                    rel = resolved.resolve(strict=False).relative_to(root.resolve()).as_posix()
                except ValueError:
                    continue
                if rel not in entry_set:
                    continue
                proof = {
                    "fls_path": recorder["fls_path"],
                    "manual": manual,
                    "variant": variant,
                    "recorded_input": raw,
                    "freshness": freshness,
                    "stale": stale,
                }
                if proof not in observations[rel]:
                    observations[rel].append(proof)
                    recorder["matched_registry_inputs"] += 1
        recorders.append(recorder)
    return observations, recorders


def _literal_assignment(path: Path, name: str) -> Any:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError(f"Affectation littérale {name} absente de {path}")


def current_manifest_chapters(root: Path) -> dict[str, dict[str, Any]]:
    maths_source = root / "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
    maths_chapters = _literal_assignment(maths_source, "CHAPITRES")
    maths_digest = sha256(maths_source)
    chapters: dict[str, dict[str, Any]] = {}
    for manual, prefix in (
        ("1SPE", "1SPE-"),
        ("TSPE", "TSPE-"),
        ("TCOMPL", "TCOMPL-"),
        ("TEXPERTES", "TEXP-"),
    ):
        selected = [chapter for chapter in maths_chapters if chapter.startswith(prefix)]
        chapters[manual] = {
            "count": len(selected),
            "chapters": selected,
            "source_path": relative(maths_source, root),
            "source_sha256": maths_digest,
            "source_kind": "ASSEMBLER_LITERAL_SOURCE_OF_TRUTH",
            "consumed_by": relative(maths_source, root),
        }

    nsi_consumer = root / "NSI/scripts/assemble_manuel.py"
    for manual in ("1NSI", "TNSI"):
        manifest = root / f"NSI/manifests/books/{manual}.json"
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        selected = [entry["id"] for entry in payload["chapters"]]
        chapters[manual] = {
            "count": len(selected),
            "chapters": selected,
            "source_path": relative(manifest, root),
            "source_sha256": sha256(manifest),
            "source_kind": "BOOK_MANIFEST_CONSUMED_BY_ASSEMBLER",
            "consumed_by": relative(nsi_consumer, root),
        }
    return chapters


def build_registry(root: Path = ROOT) -> dict[str, Any]:
    paths = source_files(root)
    entry_paths = [relative(path, root) for path in paths]
    refs = direct_references(root, entry_paths)
    fls, recorders = fls_observations(root, entry_paths)

    digest_groups: dict[str, list[str]] = defaultdict(list)
    for path, rel in zip(paths, entry_paths, strict=True):
        digest_groups[sha256(path)].append(rel)

    duplicate_of: dict[str, str | None] = {}
    duplicate_groups = []
    for digest, group in sorted(digest_groups.items()):
        ordered = sorted(group, key=lambda item: (not is_canonical(item), item))
        primary = ordered[0]
        for item in ordered:
            duplicate_of[item] = None if item == primary else primary
        if len(ordered) > 1:
            duplicate_groups.append(
                {"sha256": digest, "primary": primary, "files": ordered}
            )

    files = []
    for path, rel in zip(paths, entry_paths, strict=True):
        text = path.read_text(encoding="utf-8", errors="ignore")
        historical = LEGACY_REFERENCE_DIR in PurePosixPath(rel).parts or "archive" in PurePosixPath(rel).parts
        role = role_for(rel, text)
        files.append(
            {
                "path": rel,
                "role": role,
                "canonical": is_canonical(rel),
                "runtime_consumers": {
                    "direct_references": refs[rel],
                    "fls_observations": fls[rel],
                },
                "sha256": sha256(path),
                "duplicate_of": duplicate_of[rel],
                "deprecated": historical,
                "historical_only": historical,
            }
        )

    potential = []
    current_wrappers = []
    for entry in files:
        if entry["historical_only"] or entry["canonical"]:
            continue
        consumers = entry["runtime_consumers"]
        has_direct_runtime = any(
            ref["kind"] in {"LATEX_COMMAND", "ASSEMBLER_LITERAL"}
            for ref in consumers["direct_references"]
        )
        has_observation = bool(consumers["fls_observations"])
        if has_direct_runtime or has_observation:
            potential.append(entry["path"])
        if entry["role"].startswith("COMPATIBILITY_") and any(
            observation["freshness"] in {"CURRENT_WORKTREE_UNATTESTED", "ATTESTED_CURRENT"}
            for observation in consumers["fls_observations"]
        ):
            current_wrappers.append(entry["path"])

    class_implementations = [
        entry["path"] for entry in files if entry["role"] == "CANONICAL_CLASS_IMPLEMENTATION"
    ]
    style_implementations = [
        entry["path"] for entry in files if entry["role"] == "CANONICAL_STYLE_IMPLEMENTATION"
    ]
    exact_duplicate_files = sum(len(group["files"]) - 1 for group in duplicate_groups)
    return {
        "artifact_type": "CANONICAL_STYLE_RUNTIME_REGISTRY",
        "schema_version": 1,
        "methodology": {
            "source_scope": "Physical source *.cls/*.sty and *.tex below a gabarits directory; build/tmp/node_modules excluded",
            "direct_reference_scope": "Executable LaTeX commands and assembler literals; docs/tests excluded",
            "fls_policy": "Only .fls copied below audit/ beside a manifest git_sha are evidence; ignored build products and unattested recorders are omitted, and ATTESTED_CURRENT requires an exact HEAD SHA match",
            "no_build_or_charter_mutation": True,
        },
        "canonical_targets": {
            "class": CANONICAL_CLASS,
            "style": CANONICAL_STYLE,
            "support_styles": sorted(
                entry["path"]
                for entry in files
                if entry["role"] in {"CANONICAL_SUPPORT_STYLE", "CANONICAL_DISCIPLINE_ADAPTER"}
            ),
        },
        "summary": {
            "physical_files": len(files),
            "unique_contents": len(digest_groups),
            "exact_duplicate_files": exact_duplicate_files,
            "exact_duplicate_groups": len(duplicate_groups),
            "canonical_files": sum(entry["canonical"] for entry in files),
            "noncanonical_runtime_potential": len(potential),
            "noncanonical_runtime_potential_paths": sorted(potential),
            "compatibility_wrappers_observed_current": sorted(current_wrappers),
            "one_canonical_class_implementation_achieved": class_implementations == [CANONICAL_CLASS],
            "one_canonical_style_implementation_achieved": style_implementations == [CANONICAL_STYLE],
            # Fail closed: absence of an observed wrapper is not proof of a
            # clean runtime while noncanonical runtime candidates still exist.
            "runtime_clean_without_compatibility_wrappers_achieved": (
                not current_wrappers and not potential
            ),
        },
        "fls_recorders": recorders,
        "exact_duplicate_groups": duplicate_groups,
        "current_canonical_manifest_chapters": current_manifest_chapters(root),
        "files": files,
    }


CANONICAL_FINAL_RUNTIME = {
    "gabarits/common/nexus-manuel.cls",
    "gabarits/common/nexus-charte.sty",
    "gabarits/common/nexus-boites.sty",
    "gabarits/common/nexus-couverture.sty",
    "gabarits/common/nexus-decor.sty",
    "gabarits/common/nexus-exercices.sty",
    "gabarits/common/nexus-figures-bib.sty",
    "gabarits/common/nexus-pages-froides.sty",
    "gabarits/common/nexus-pont.sty",
}


def _canonical_target(path: str) -> str | None:
    if is_canonical(path):
        return path
    pure = PurePosixPath(path)
    prefix = _project_prefix(path)
    if prefix is None:
        return None
    name = pure.name
    direct = {
        "chapitre_master.tex": "gabarits/common/chapitre_master.tex"
        if path.startswith(MATHS_PREFIX)
        else None,
        "nexus-manuel.cls": CANONICAL_CLASS,
        "nexus-manuel-v5.cls": CANONICAL_CLASS,
        "nexus-charte-v6.sty": CANONICAL_STYLE,
        "nexus-boites-v6.sty": "gabarits/common/nexus-boites.sty",
        "nexus-couverture.sty": "gabarits/common/nexus-couverture.sty",
        "nexus-decor.sty": "gabarits/common/nexus-decor.sty",
        "nexus-exercices-v6.sty": "gabarits/common/nexus-exercices.sty",
        "nexus-figures-bib.sty": "gabarits/common/nexus-figures-bib.sty",
        "nexus-pages-froides.sty": "gabarits/common/nexus-pages-froides.sty",
        "nexus-pont-v6.sty": "gabarits/common/nexus-pont.sty",
        "nexus-code.tex": "gabarits/common/nexus-code.tex",
        "nexus-figures.tex": "gabarits/maths/nexus-maths.sty",
        "nexus-figures-nsi.tex": "gabarits/nsi/nexus-nsi.sty",
        "nexus-icons.tex": "gabarits/common/nexus-icons.tex",
        "nexus-margin-rail.tex": "gabarits/common/nexus-margin-rail.tex",
        "nexus-margin-shipout.lua": "gabarits/common/nexus-margin-shipout.lua",
        "nexus-margin-json.lua": "gabarits/common/nexus-margin-json.lua",
        "nexus-margin-layout.lua": "gabarits/common/nexus-margin-layout.lua",
        "nexus-signatures.tex": "gabarits/common/nexus-signatures.tex",
        "logo_nexus.png": "gabarits/common/logo_nexus.png",
    }
    if pure.suffix == ".otf" and "fonts" in pure.parts:
        return f"gabarits/common/fonts/{name}"
    return direct.get(name)


def _asset_lifecycle(path: str, role: str) -> str:
    pure = PurePosixPath(path)
    if LEGACY_REFERENCE_DIR in pure.parts or "archive" in pure.parts:
        return "HISTORICAL_ONLY"
    if path in VISUAL_FIXTURES:
        return "VISUAL_FIXTURE"
    if path in REFERENCE_ONLY:
        return "REFERENCE_ONLY"
    if path in ACTIVE_WRAPPERS:
        return "ACTIVE_COMPATIBILITY_WRAPPER"
    if path in DORMANT_WRAPPERS:
        return "DORMANT_COMPATIBILITY_WRAPPER"
    if path in NONCANONICAL_PRODUCTION_INPUTS:
        if pure.name in {"book_master.tex", "chapitre_master.tex"}:
            return "ACTIVE_BUILD_TEMPLATE"
        return "ACTIVE_LOCAL_RUNTIME"
    if pure.name == "objet_standalone.tex" and _project_prefix(path):
        return "ACTIVE_TOOL_TEMPLATE"
    if is_canonical(path):
        return "CANONICAL_SOURCE"
    if pure.suffix == ".otf":
        if pure.name.startswith("JetBrainsMono-") and _project_prefix(path):
            return "FONT_PROVISION_SOURCE"
        return "DORMANT_FONT_SOURCE"
    if role == "REFERENCE_MODEL_STYLE":
        return "REFERENCE_ONLY"
    return "DORMANT_UNPROVED"


def _asset_consumers(path: str) -> list[str]:
    name = PurePosixPath(path).name
    consumers: list[str] = []
    if path in CANONICAL_FINAL_RUNTIME:
        consumers.extend(FINAL_CONSUMERS)
    if path == CANONICAL_CLASS:
        consumers.extend(("MATH_CHAPTER_RUNTIME", "MATH_LIVRET_RUNTIME", "NSI_CHAPTER_RUNTIME"))
    if path.startswith(MATHS_PREFIX):
        if name in {"nexus-manuel-v5.cls", "nexus-charte-v6.sty", *LOCAL_RUNTIME_NAMES}:
            consumers.extend(MATHS_FINAL_CONSUMERS)
        if name == "nexus-manuel.cls":
            consumers.extend(("MATH_CHAPTER_RUNTIME", "MATH_LIVRET_RUNTIME"))
        if name == "chapitre_master.tex":
            consumers.append("MATH_CHAPTER_BUILDER")
        if name == "objet_standalone.tex":
            consumers.append("MATH_MCP_OBJECT_COMPILER")
        if name.startswith("JetBrainsMono-") and name.endswith(".otf"):
            consumers.append("MATH_FONT_PROVISIONING")
    if path.startswith(NSI_PREFIX):
        if name in {"nexus-manuel-v5.cls", "nexus-charte-v6.sty", *LOCAL_RUNTIME_NAMES}:
            consumers.extend(NSI_FINAL_CONSUMERS)
        if name == "nexus-manuel.cls":
            consumers.append("NSI_CHAPTER_RUNTIME")
        if name == "book_master.tex":
            consumers.append("NSI_BOOK_BUILDER")
        if name == "chapitre_master.tex":
            consumers.append("NSI_CHAPTER_BUILDER")
        if name == "objet_standalone.tex":
            consumers.append("NSI_MCP_OBJECT_COMPILER")
        if name.startswith("JetBrainsMono-") and name.endswith(".otf"):
            consumers.append("NSI_FONT_PROVISIONING")
    if path in REFERENCE_ONLY:
        consumers.append("NSI_REFERENCE_CORPUS_P13")
    return sorted(set(consumers))


def _line_proof(root: Path, path: str, needle: str) -> dict[str, Any]:
    """Return a current, line-addressable proof without hard-coding line numbers."""

    source = root / path
    for line_number, line in enumerate(
        source.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1
    ):
        if needle in line:
            return {"path": path, "line": line_number, "needle": needle}
    raise ValueError(f"preuve statique absente: {path}: {needle}")


def _noncanonical_production_evidence(root: Path, path: str) -> dict[str, Any]:
    """Explain why one noncanonical path is part of the production surface."""

    name = PurePosixPath(path).name
    maths = path.startswith(MATHS_PREFIX)
    proof: list[dict[str, Any]] = []
    if name == "chapitre_master.tex":
        producer = (
            "Mathematiques/manuel-maths/scripts/assemble.py"
            if maths
            else "NSI/scripts/assemble.py"
        )
        proof.append(_line_proof(root, producer, '"chapitre_master.tex"'))
        return {
            "path": path,
            "reason_code": "ACTIVE_BUILD_TEMPLATE",
            "reason": "Le producteur de chapitre lit directement ce gabarit local.",
            "production_consumers": _asset_consumers(path),
            "proof": proof,
        }
    if name == "book_master.tex":
        proof.append(_line_proof(root, "NSI/scripts/assemble.py", '"book_master.tex"'))
        return {
            "path": path,
            "reason_code": "ACTIVE_BUILD_TEMPLATE",
            "reason": "Le producteur de manuel NSI lit directement ce gabarit local.",
            "production_consumers": _asset_consumers(path),
            "proof": proof,
        }

    if name == "nexus-manuel.cls":
        template = f"{MATHS_PREFIX if maths else NSI_PREFIX}chapitre_master.tex"
        proof.append(_line_proof(root, template, r"\documentclass{gabarits/nexus-manuel}"))
        reason_code = "ACTIVE_COMPATIBILITY_WRAPPER"
        reason = "Le gabarit de chapitre charge explicitement le wrapper de classe local."
    elif name == "nexus-manuel-v5.cls":
        if maths:
            proof.append(
                _line_proof(
                    root,
                    "Mathematiques/manuel-maths/scripts/assemble_manuel.py",
                    r"\documentclass{{gabarits/nexus-manuel-v5}}",
                )
            )
        else:
            proof.append(
                _line_proof(root, f"{NSI_PREFIX}book_master.tex", r"\documentclass{gabarits/nexus-manuel-v5}")
            )
        reason_code = "ACTIVE_COMPATIBILITY_WRAPPER"
        reason = "Le producteur de manuel charge explicitement le wrapper de classe local."
    elif name == "nexus-charte-v6.sty":
        if maths:
            proof.append(
                _line_proof(
                    root,
                    "Mathematiques/manuel-maths/scripts/assemble_manuel.py",
                    r"\usepackage{{gabarits/nexus-charte-v6}}",
                )
            )
        else:
            proof.append(
                _line_proof(root, f"{NSI_PREFIX}book_master.tex", r"\usepackage{gabarits/nexus-charte-v6}")
            )
        reason_code = "ACTIVE_COMPATIBILITY_WRAPPER"
        reason = "Le producteur de manuel charge explicitement le wrapper de charte local."
    else:
        resolver_path = CANONICAL_CLASS
        resolver_needles = {
            "nexus-icons.tex": r"\input{gabarits/nexus-icons.tex}",
            "nexus-figures.tex": r"\input{gabarits/nexus-figures.tex}",
            "nexus-figures-nsi.tex": r"\input{gabarits/nexus-figures-nsi.tex}",
            "nexus-signatures.tex": r"\input{gabarits/nexus-signatures.tex}",
            "nexus-code.tex": r"\input{gabarits/nexus-code.tex}",
            "nexus-margin-rail.tex": r"\input{gabarits/nexus-margin-rail.tex}",
            "logo_nexus.png": r"{gabarits/logo_nexus.png}",
            "nexus-margin-shipout.lua": 'or "gabarits/nexus-margin-shipout.lua"',
            "nexus-margin-json.lua": 'load_sibling("nexus-margin-json.lua")',
            "nexus-margin-layout.lua": 'load_sibling("nexus-margin-layout.lua")',
        }
        if name == "logo_nexus.png":
            resolver_path = "gabarits/common/nexus-couverture.sty"
        elif name == "nexus-margin-shipout.lua":
            resolver_path = f"{MATHS_PREFIX if maths else NSI_PREFIX}nexus-margin-rail.tex"
        elif name in {"nexus-margin-json.lua", "nexus-margin-layout.lua"}:
            resolver_path = f"{MATHS_PREFIX if maths else NSI_PREFIX}nexus-margin-shipout.lua"
        proof.append(_line_proof(root, resolver_path, resolver_needles[name]))
        reason_code = "ACTIVE_PROJECT_LOCAL_RUNTIME"
        reason = (
            "La résolution relative au répertoire projet sélectionne cet asset local "
            "pendant les builds de la famille concernée."
        )
    return {
        "path": path,
        "reason_code": reason_code,
        "reason": reason,
        "production_consumers": _asset_consumers(path),
        "proof": proof,
    }


def _asset_role(path: str, text: str) -> str:
    pure = PurePosixPath(path)
    if pure.suffix in {".cls", ".sty", ".tex"}:
        return role_for(path, text)
    if pure.suffix == ".lua":
        return "RUNTIME_LUA_MODULE"
    if pure.suffix == ".otf":
        return "FONT_BINARY"
    if pure.name == "logo_nexus.png":
        return "LOGO_ASSET"
    raise ValueError(f"type d'asset non classé: {path}")


def _consumer_edges(asset_paths: set[str]) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []

    def add(source: str, target: str, kind: str, scope: str) -> None:
        if source in asset_paths and target in asset_paths:
            edges.append({"source": source, "target": target, "kind": kind, "scope": scope})

    for path in sorted(ACTIVE_WRAPPERS | DORMANT_WRAPPERS):
        target = _canonical_target(path)
        if target:
            add(path, target, "CANONICAL_REDIRECT", "SOURCE")
    add(f"{MATHS_PREFIX}chapitre_master.tex", f"{MATHS_PREFIX}nexus-manuel.cls", "LATEX_CLASS", "MATH_CHAPTER")
    add(f"{NSI_PREFIX}book_master.tex", f"{NSI_PREFIX}nexus-manuel-v5.cls", "LATEX_CLASS", "NSI_BOOK")
    add(f"{NSI_PREFIX}book_master.tex", f"{NSI_PREFIX}nexus-charte-v6.sty", "LATEX_PACKAGE", "NSI_BOOK")
    add(f"{NSI_PREFIX}chapitre_master.tex", f"{NSI_PREFIX}nexus-manuel.cls", "LATEX_CLASS", "NSI_CHAPTER")
    for module in (
        "nexus-couverture.sty",
        "nexus-pages-froides.sty",
        "nexus-figures-bib.sty",
        "nexus-boites.sty",
        "nexus-exercices.sty",
        "nexus-decor.sty",
        "nexus-pont.sty",
    ):
        add(CANONICAL_STYLE, f"gabarits/common/{module}", "LATEX_PACKAGE", "ALL_BOOKS")
    for prefix, scope in ((MATHS_PREFIX, "MATH"), (NSI_PREFIX, "NSI")):
        for module in (
            "nexus-icons.tex",
            "nexus-figures.tex",
            "nexus-figures-nsi.tex",
            "nexus-signatures.tex",
            "nexus-code.tex",
            "nexus-margin-rail.tex",
        ):
            add(CANONICAL_CLASS, f"{prefix}{module}", "LATEX_FALLBACK_RESOLVED", scope)
        add("gabarits/common/nexus-couverture.sty", f"{prefix}logo_nexus.png", "GRAPHIC_ASSET", scope)
        add(f"{prefix}nexus-margin-rail.tex", f"{prefix}nexus-margin-shipout.lua", "LUA_LOAD", scope)
        add(f"{prefix}nexus-margin-shipout.lua", f"{prefix}nexus-margin-json.lua", "LUA_SIBLING", scope)
        add(f"{prefix}nexus-margin-shipout.lua", f"{prefix}nexus-margin-layout.lua", "LUA_SIBLING", scope)
    return sorted(edges, key=lambda edge: (edge["source"], edge["target"], edge["kind"], edge["scope"]))


def build_consumer_graph(root: Path, registry: dict[str, Any]) -> dict[str, Any]:
    paths = asset_files(root)
    groups = _digest_groups(paths, root)
    primary_for = {
        member: sorted(members, key=lambda item: (not is_canonical(item), item))[0]
        for members in groups.values()
        for member in members
    }
    assets = []
    for source in paths:
        path = relative(source, root)
        text = source.read_text(encoding="utf-8", errors="ignore") if source.suffix in {".cls", ".sty", ".tex", ".lua"} else ""
        role = _asset_role(path, text)
        lifecycle = _asset_lifecycle(path, role)
        runtime = lifecycle in {"ACTIVE_COMPATIBILITY_WRAPPER", "ACTIVE_LOCAL_RUNTIME"} or path in CANONICAL_FINAL_RUNTIME
        assets.append(
            {
                "path": path,
                "kind": source.suffix.removeprefix(".").upper() if source.suffix else "FILE",
                "role": role,
                "sha256": sha256(source),
                "canonical_path": _canonical_target(path),
                "duplicate_of": None if primary_for[path] == path else primary_for[path],
                "lifecycle": lifecycle,
                "runtime": runtime,
                "runtime_state": "STATIC_PRODUCTION" if runtime else "NOT_COMPILE_RUNTIME",
                "production_consumers": _asset_consumers(path),
            }
        )
    lifecycle_sets: dict[str, list[str]] = defaultdict(list)
    for asset in assets:
        lifecycle_sets[asset["lifecycle"]].append(asset["path"])
    lifecycle_sets["OBSOLETE_PROVED"] = []
    for values in lifecycle_sets.values():
        values.sort()
    final_consumer_names = set(FINAL_CONSUMERS)
    fresh_attested_final_fls = sum(
        recorder["freshness"] == "ATTESTED_CURRENT"
        and f"{recorder['manual']}:{recorder['variant']}" in final_consumer_names
        for recorder in registry["fls_recorders"]
    )
    noncanonical_evidence = [
        _noncanonical_production_evidence(root, path)
        for path in sorted(NONCANONICAL_PRODUCTION_INPUTS)
    ]
    legacy_potential = set(registry["summary"]["noncanonical_runtime_potential_paths"])
    graph = {
        "artifact_type": "STYLE_CONSUMER_GRAPH",
        "schema_version": 1,
        "methodology": {
            "compile_runtime": "Static producer/include resolution; observed FLS retained only when audit-attested",
            "final_consumers": list(FINAL_CONSUMERS),
            "no_style_source_mutation": True,
        },
        "summary": {
            "physical_assets": len(paths),
            "unique_asset_contents": len(groups),
            "noncanonical_production_inputs": len(NONCANONICAL_PRODUCTION_INPUTS),
            "final_pdf_consumers": len(FINAL_CONSUMERS),
            "fresh_attested_final_fls": fresh_attested_final_fls,
            "unknown_lifecycle": 0,
            "graph_complete_for_static_sources": True,
            "graph_complete_for_final_observed_runtime": False,
        },
        "noncanonical_production_inputs": sorted(NONCANONICAL_PRODUCTION_INPUTS),
        "noncanonical_production_evidence": noncanonical_evidence,
        "legacy_registry_reconciliation": {
            "confirmed_production_inputs": sorted(
                legacy_potential & NONCANONICAL_PRODUCTION_INPUTS
            ),
            "reference_only_false_positives": sorted(
                legacy_potential - NONCANONICAL_PRODUCTION_INPUTS
            ),
            "newly_explicit_production_inputs": sorted(
                NONCANONICAL_PRODUCTION_INPUTS - legacy_potential
            ),
        },
        "lifecycle_sets": dict(sorted(lifecycle_sets.items())),
        "assets": assets,
        "edges": _consumer_edges({asset["path"] for asset in assets}),
        "attested_fls_recorders": registry["fls_recorders"],
        "font_runtime": {
            "configured_by": "gabarits/common/nexus-manuel.cls:58-70",
            "families": ["TeX Gyre Pagella", "TeX Gyre Pagella Math", "TeX Gyre Heros", "JetBrains Mono"],
            "repository_otf_compile_inputs": [],
            "repository_otf_provision_sources": sorted(
                asset["path"] for asset in assets if asset["lifecycle"] == "FONT_PROVISION_SOURCE"
            ),
        },
    }
    validate_consumer_graph(graph)
    return graph


def validate_consumer_graph(graph: dict[str, Any]) -> None:
    paths = {asset["path"] for asset in graph["assets"]}
    for edge in graph["edges"]:
        if edge["source"] not in paths:
            raise ValueError(f"source absente du graphe: {edge['source']}")
        if edge["target"] not in paths:
            raise ValueError(f"cible absente du graphe: {edge['target']}")
    if graph["summary"]["unknown_lifecycle"]:
        raise ValueError("cycle de vie UNKNOWN interdit")
    noncanonical = set(graph["noncanonical_production_inputs"])
    explained = {entry["path"] for entry in graph["noncanonical_production_evidence"]}
    if explained != noncanonical:
        missing = sorted(noncanonical - explained)
        unexpected = sorted(explained - noncanonical)
        raise ValueError(
            f"preuves runtime non canoniques non closes: missing={missing}, unexpected={unexpected}"
        )
    for entry in graph["noncanonical_production_evidence"]:
        if not entry["reason_code"] or not entry["reason"] or not entry["proof"]:
            raise ValueError(f"explication runtime incomplète: {entry['path']}")


def build_duplicate_forensics(graph: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for asset in graph["assets"]:
        grouped[asset["sha256"]].append(asset)
    groups = []
    for digest, members in sorted(grouped.items()):
        if len(members) < 2:
            continue
        ordered = sorted(members, key=lambda item: (not is_canonical(item["path"]), item["path"]))
        groups.append(
            {
                "sha256": digest,
                "primary": ordered[0]["path"],
                "members": [
                    {
                        "path": member["path"],
                        "lifecycle": member["lifecycle"],
                        "runtime": member["runtime"],
                        "safe_to_delete": False,
                        "disposition": "KEEP_PENDING_EXHAUSTIVE_CONSUMER_MIGRATION",
                    }
                    for member in ordered
                ],
            }
        )
    duplicate_files = sum(len(group["members"]) - 1 for group in groups)
    payload = {
        "artifact_type": "STYLE_DUPLICATE_FORENSICS",
        "schema_version": 1,
        "summary": {
            "legacy_physical_files": registry["summary"]["physical_files"],
            "legacy_unique_contents": registry["summary"]["unique_contents"],
            "legacy_duplicate_files": registry["summary"]["exact_duplicate_files"],
            "legacy_duplicate_groups": registry["summary"]["exact_duplicate_groups"],
            "extended_physical_assets": len(graph["assets"]),
            "extended_unique_contents": graph["summary"]["unique_asset_contents"],
            "extended_duplicate_files": duplicate_files,
            "extended_duplicate_groups": len(groups),
            "runtime_safe_to_delete": 0,
            "obsolete_proved": 0,
        },
        "obsolete_proved": [],
        "groups": groups,
    }
    validate_duplicate_forensics(payload)
    return payload


def validate_duplicate_forensics(payload: dict[str, Any]) -> None:
    for group in payload["groups"]:
        for member in group["members"]:
            if member["runtime"] and member["safe_to_delete"]:
                raise ValueError(f"duplicata runtime déclaré supprimable: {member['path']}")


def build_artifacts(root: Path = ROOT) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    registry = build_registry(root)
    graph = build_consumer_graph(root, registry)
    duplicates = build_duplicate_forensics(graph, registry)
    return registry, graph, duplicates


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Registre factuel de la charte et du runtime Nexus",
        "",
        "Ce registre inventorie les sources physiques et les preuves de consommation ; il ne modifie ni la charte ni les builds.",
        "",
        "## Synthèse",
        "",
        f"- Fichiers physiques : **{summary['physical_files']}**",
        f"- Contenus uniques : **{summary['unique_contents']}**",
        f"- Duplicatas exacts au-delà du premier exemplaire : **{summary['exact_duplicate_files']}** dans **{summary['exact_duplicate_groups']}** groupes",
        f"- Cible de classe canonique : `{payload['canonical_targets']['class']}`",
        f"- Cible de style canonique : `{payload['canonical_targets']['style']}`",
        f"- Potentiels runtime non canoniques : **{summary['noncanonical_runtime_potential']}**",
        f"- Une implémentation canonique de classe : **{str(summary['one_canonical_class_implementation_achieved']).upper()}**",
        f"- Une implémentation canonique de charte : **{str(summary['one_canonical_style_implementation_achieved']).upper()}**",
        f"- Runtime sans wrapper de compatibilité observé : **{str(summary['runtime_clean_without_compatibility_wrappers_achieved']).upper()}**",
        "",
        "La présence d'une cible canonique unique n'implique pas encore un runtime sans wrappers. Les `.fls` non attestés ne valent pas preuve d'un build final au SHA courant.",
        "",
        "## CURRENT_CANONICAL_MANIFEST_CHAPTERS",
        "",
        "| Manuel | Chapitres | Source réellement consommée |",
        "|---|---:|---|",
    ]
    for manual, record in payload["current_canonical_manifest_chapters"].items():
        lines.append(f"| {manual} | {record['count']} | `{record['source_path']}` |")

    lines.extend(
        [
            "",
            "## Enregistreurs `.fls` disponibles",
            "",
            "| FLS | Manuel | Variante | Fraîcheur | Entrées du registre |",
            "|---|---|---|---|---:|",
        ]
    )
    for recorder in payload["fls_recorders"]:
        lines.append(
            f"| `{recorder['fls_path']}` | {recorder['manual']} | {recorder['variant']} | "
            f"{recorder['freshness']} | {recorder['matched_registry_inputs']} |"
        )

    lines.extend(
        [
            "",
            "## Fichiers",
            "",
            "| Chemin | Rôle | Canonique | SHA-256 | Duplicata de | Références directes | `.fls` | Déprécié | Historique |",
            "|---|---|:---:|---|---|---:|---:|:---:|:---:|",
        ]
    )
    for entry in payload["files"]:
        consumers = entry["runtime_consumers"]
        duplicate = f"`{entry['duplicate_of']}`" if entry["duplicate_of"] else "—"
        lines.append(
            f"| `{entry['path']}` | {entry['role']} | {'YES' if entry['canonical'] else 'NO'} | "
            f"`{entry['sha256']}` | {duplicate} | {len(consumers['direct_references'])} | "
            f"{len(consumers['fls_observations'])} | {'YES' if entry['deprecated'] else 'NO'} | "
            f"{'YES' if entry['historical_only'] else 'NO'} |"
        )

    lines.extend(["", "## Duplicatas exacts", ""])
    if not payload["exact_duplicate_groups"]:
        lines.append("Aucun.")
    for group in payload["exact_duplicate_groups"]:
        lines.append(f"- `{group['sha256']}` : " + ", ".join(f"`{path}`" for path in group["files"]))
    return "\n".join(lines).rstrip() + "\n"


def serialise(payload: dict[str, Any]) -> tuple[bytes, bytes]:
    json_bytes = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    md_bytes = render_markdown(payload).encode("utf-8")
    return json_bytes, md_bytes


def render_consumer_graph_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Graphe des consommateurs de la charte Nexus",
        "",
        "Cartographie read-only des sources, assets et consommateurs. Aucun chemin n'est redirigé ou supprimé par ce rapport.",
        "",
        "## Synthèse",
        "",
        f"- Assets physiques : **{summary['physical_assets']}**",
        f"- Contenus uniques : **{summary['unique_asset_contents']}**",
        f"- Entrées de production non canoniques : **{summary['noncanonical_production_inputs']}**",
        f"- Consommateurs PDF finaux : **{summary['final_pdf_consumers']}**",
        f"- `.fls` finaux frais et attestés : **{summary['fresh_attested_final_fls']}**",
        f"- UNKNOWN lifecycle : **{summary['unknown_lifecycle']}**",
        "",
        "## Entrées de production non canoniques",
        "",
    ]
    for entry in payload["noncanonical_production_evidence"]:
        proofs = ", ".join(
            f"`{proof['path']}:{proof['line']}`" for proof in entry["proof"]
        )
        consumers = ", ".join(entry["production_consumers"])
        lines.append(
            f"- `{entry['path']}` — {entry['reason_code']} — {entry['reason']} "
            f"Preuve : {proofs}. Consommateurs : {consumers}."
        )
    reconciliation = payload["legacy_registry_reconciliation"]
    lines.extend(
        [
            "",
            "## Réconciliation avec la métrique historique des 16 chemins",
            "",
            f"- Confirmés production : **{len(reconciliation['confirmed_production_inputs'])}**",
            f"- Faux positif de référence : **{len(reconciliation['reference_only_false_positives'])}**",
            f"- Entrées production désormais explicites : **{len(reconciliation['newly_explicit_production_inputs'])}**",
            "",
        ]
    )
    for path in reconciliation["reference_only_false_positives"]:
        lines.append(f"- Référence seule : `{path}`")
    lines.extend(["", "## Ensembles de cycle de vie", ""])
    for lifecycle, paths in payload["lifecycle_sets"].items():
        lines.append(f"### {lifecycle}")
        lines.append("")
        if paths:
            lines.extend(f"- `{path}`" for path in paths)
        else:
            lines.append("Aucun.")
        lines.append("")
    lines.extend(["## Assets", "", "| Chemin | Rôle | Lifecycle | Runtime | Canonique | Consommateurs |", "|---|---|---|:---:|---|---|"])
    for asset in payload["assets"]:
        canonical = f"`{asset['canonical_path']}`" if asset["canonical_path"] else "—"
        consumers = ", ".join(asset["production_consumers"]) or "—"
        lines.append(
            f"| `{asset['path']}` | {asset['role']} | {asset['lifecycle']} | "
            f"{'YES' if asset['runtime'] else 'NO'} | {canonical} | {consumers} |"
        )
    return "\n".join(lines) + "\n"


def serialise_consumer_graph(payload: dict[str, Any]) -> tuple[bytes, bytes]:
    json_bytes = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return json_bytes, render_consumer_graph_markdown(payload).encode("utf-8")


def render_duplicate_forensics_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Forensic des duplicatas de charte Nexus",
        "",
        "## Synthèse",
        "",
        f"- Scope historique : **{summary['legacy_duplicate_files']}** copies dans **{summary['legacy_duplicate_groups']}** groupes",
        f"- Scope étendu : **{summary['extended_duplicate_files']}** copies dans **{summary['extended_duplicate_groups']}** groupes",
        f"- Runtime `safe_to_delete` : **{summary['runtime_safe_to_delete']}**",
        f"- `OBSOLETE_PROVED` : **{summary['obsolete_proved']}**",
        "",
        "Aucun duplicata runtime n'est déclaré supprimable avant migration et preuve exhaustive des consommateurs.",
        "",
        "## Groupes exacts",
        "",
    ]
    for group in payload["groups"]:
        lines.append(f"### `{group['sha256']}`")
        lines.append("")
        lines.append(f"Primaire : `{group['primary']}`")
        lines.append("")
        for member in group["members"]:
            lines.append(
                f"- `{member['path']}` — {member['lifecycle']} — runtime="
                f"{'YES' if member['runtime'] else 'NO'} — safe_to_delete=NO"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def serialise_duplicate_forensics(payload: dict[str, Any]) -> tuple[bytes, bytes]:
    json_bytes = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return json_bytes, render_duplicate_forensics_markdown(payload).encode("utf-8")


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if committed reports differ")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--md-output", type=Path)
    parser.add_argument("--graph-json-output", type=Path)
    parser.add_argument("--graph-md-output", type=Path)
    parser.add_argument("--duplicates-json-output", type=Path)
    parser.add_argument("--duplicates-md-output", type=Path)
    args = parser.parse_args(argv)

    custom_registry_outputs = args.json_output is not None or args.md_output is not None
    json_output = args.json_output or DEFAULT_JSON
    md_output = args.md_output or DEFAULT_MD
    graph_json_output = args.graph_json_output or (
        json_output.with_name("STYLE_CONSUMER_GRAPH.json")
        if custom_registry_outputs
        else DEFAULT_GRAPH_JSON
    )
    graph_md_output = args.graph_md_output or (
        md_output.with_name("STYLE_CONSUMER_GRAPH.md")
        if custom_registry_outputs
        else DEFAULT_GRAPH_MD
    )
    duplicates_json_output = args.duplicates_json_output or (
        json_output.with_name("STYLE_DUPLICATE_FORENSICS.json")
        if custom_registry_outputs
        else DEFAULT_DUPLICATES_JSON
    )
    duplicates_md_output = args.duplicates_md_output or (
        md_output.with_name("STYLE_DUPLICATE_FORENSICS.md")
        if custom_registry_outputs
        else DEFAULT_DUPLICATES_MD
    )

    payload, graph, duplicates = build_artifacts(ROOT)
    json_bytes, md_bytes = serialise(payload)
    graph_json_bytes, graph_md_bytes = serialise_consumer_graph(graph)
    duplicates_json_bytes, duplicates_md_bytes = serialise_duplicate_forensics(duplicates)
    outputs = (
        (json_output, json_bytes),
        (md_output, md_bytes),
        (graph_json_output, graph_json_bytes),
        (graph_md_output, graph_md_bytes),
        (duplicates_json_output, duplicates_json_bytes),
        (duplicates_md_output, duplicates_md_bytes),
    )
    if args.check:
        mismatches = []
        for path, expected in outputs:
            if not path.is_file() or path.read_bytes() != expected:
                mismatches.append(path)
        if mismatches:
            print("Registre charte/runtime périmé : " + ", ".join(str(path) for path in mismatches))
            return 1
        print("Registre charte/runtime déterministe et à jour.")
        return 0

    for path, content in outputs:
        atomic_write(path, content)
    print(
        f"Registre charte/runtime généré : {payload['summary']['physical_files']} fichiers, "
        f"{payload['summary']['unique_contents']} contenus uniques ; "
        f"{graph['summary']['physical_assets']} assets étendus."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
