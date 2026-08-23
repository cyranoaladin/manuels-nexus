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
import tempfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "audit" / "CANONICAL_STYLE_RUNTIME_REGISTRY.json"
DEFAULT_MD = ROOT / "audit" / "CANONICAL_STYLE_RUNTIME_REGISTRY.md"

CANONICAL_CLASS = "gabarits/common/nexus-manuel.cls"
CANONICAL_STYLE = "gabarits/common/nexus-charte.sty"
CANONICAL_PREFIXES = ("gabarits/common/", "gabarits/maths/", "gabarits/nsi/")
EXCLUDED_PARTS = {".git", ".worktrees", "build", "node_modules", "tmp"}
REFERENCE_SUFFIXES = {".py", ".tex", ".cls", ".sty", ".lua"}
LEGACY_REFERENCE_DIR = "reference-" + "v4"

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

    fls_files = sorted(
        (path for path in root.rglob("*.fls") if path.is_file() and not is_excluded(path, root, allow_build=True)),
        key=lambda item: relative(item, root),
    )
    for fls in fls_files:
        lines = fls.read_text(encoding="utf-8", errors="ignore").splitlines()
        pwd_line = next((line[4:].strip() for line in lines if line.startswith("PWD ")), "")
        logical_pwd, same_worktree = _logical_pwd(pwd_line, root)
        attested_sha = _attestation_sha_for(fls, root)
        if same_worktree and attested_sha:
            freshness, stale = "ATTESTED_CURRENT", False
        elif same_worktree:
            freshness, stale = "CURRENT_WORKTREE_UNATTESTED", None
        elif attested_sha:
            freshness, stale = "STALE_ATTESTED_OTHER_SHA", True
        else:
            freshness, stale = "STALE_DIFFERENT_WORKTREE", True

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
            "fls_policy": "Observed inputs are evidence only; other-worktree records are stale and current-worktree records without an attested SHA remain unverified",
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
            "runtime_clean_without_compatibility_wrappers_achieved": not current_wrappers,
        },
        "fls_recorders": recorders,
        "exact_duplicate_groups": duplicate_groups,
        "current_canonical_manifest_chapters": current_manifest_chapters(root),
        "files": files,
    }


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
    return "\n".join(lines) + "\n"


def serialise(payload: dict[str, Any]) -> tuple[bytes, bytes]:
    json_bytes = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    md_bytes = render_markdown(payload).encode("utf-8")
    return json_bytes, md_bytes


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
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-output", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)

    payload = build_registry(ROOT)
    json_bytes, md_bytes = serialise(payload)
    if args.check:
        mismatches = []
        for path, expected in ((args.json_output, json_bytes), (args.md_output, md_bytes)):
            if not path.is_file() or path.read_bytes() != expected:
                mismatches.append(path)
        if mismatches:
            print("Registre charte/runtime périmé : " + ", ".join(str(path) for path in mismatches))
            return 1
        print("Registre charte/runtime déterministe et à jour.")
        return 0

    atomic_write(args.json_output, json_bytes)
    atomic_write(args.md_output, md_bytes)
    print(
        f"Registre charte/runtime généré : {payload['summary']['physical_files']} fichiers, "
        f"{payload['summary']['unique_contents']} contenus uniques."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
