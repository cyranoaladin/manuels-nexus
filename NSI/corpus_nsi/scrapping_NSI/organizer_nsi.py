# -*- coding: utf-8 -*-
"""Centralise, extrait et classe les ressources NSI scrapées.

Le script préserve les répertoires bruts et travaille dans un transit temporaire.
Les ZIP sont supprimés uniquement dans le transit après extraction validée.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import unicodedata
import zipfile
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT_DIR = Path(__file__).resolve().parents[1]

from scripts.archive_security import ArchiveSecurityError, safe_extract_zip

SOURCE_DIRS = [Path("ressources_nsi_extraites"), Path("ressources_nsi_extraites_v2")]
DRIVE_DIR = Path(os.getenv("NSI_DOCUMENTS_DRIVE_ROOT", str(ROOT_DIR / "Documents_DRIVE")))
TRANSIT_DIR = Path(os.getenv("NSI_TRANSIT_DIR", "/tmp/nsi_transit"))
FINAL_DIR = Path(os.getenv("NSI_FINAL_DIR", "ressources_nsi_centralisees"))
REGISTRY_FILE = Path(os.getenv("NSI_MIGRATION_REGISTRY", "migration_registry.json"))
RUN_SUMMARY_FILE = Path(os.getenv("NSI_LAST_RUN_SUMMARY", "last_run_summary.log"))
EXTRACTED_ZIP_DIR = "_extracted_zips"
ARCHIVE_PROCESSED_DESTINATION = "__archive_processed_in_transit__"
DUPLICATE_DRIVE_DIR = Path("_doublons_drive")
SKIPPED_DRIVE_DIR = Path("_skipped_drive")

LEVEL_PREMIERE = Path("01_Premiere_NSI")
LEVEL_TERMINALE = Path("02_Terminale_NSI")
LEVEL_PROGRAMMES = Path("00_Programmes_et_Informations")
LEVEL_TRANSVERSAL = Path("03_Autres_et_Transversal")

TYPE_DIRS = {
    "cours": Path("01_Cours"),
    "fiche": Path("02_Fiches_et_Syntheses"),
    "td": Path("03_TD"),
    "tp": Path("04_TP"),
    "programmation": Path("05_Programmation"),
    "projet": Path("06_Projets"),
    "evaluation": Path("07_Evaluations"),
}

EVALUATION_MARKERS = (
    "sujet bac",
    "sujet_bac",
    "sujet-bac",
    "bns",
    "devoir",
    "evaluation",
    "controle",
    "eval",
    "ds",
    "annales",
)
TP_MARKERS = (" tp", "_tp", "-tp", "lab", "activite", "pratique")
TD_MARKERS = (" td", "_td", "-td", "exercice", "exercices", "fiche_ex", "exo", "exos")

TECHNICAL_PARTS = {
    "__pycache__",
    ".git",
    ".venv",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "__macosx",
}

SKIP_SUFFIXES = {".pyc", ".pyo", ".tmp", ".part", ".crdownload", ".ds_store"}
JUNK_FILENAMES = {".ds_store", "thumbs.db"}
INTERNAL_FINAL_DIRS = {str(DUPLICATE_DRIVE_DIR), str(SKIPPED_DRIVE_DIR)}
ASSET_SUFFIXES = {
    ".css",
    ".js",
    ".json",
    ".xml",
    ".html",
    ".htm",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".ico",
    ".mp3",
    ".mp4",
    ".ogg",
    ".webm",
    ".txt",
    ".md",
    ".tex",
    ".csv",
    ".db",
    ".sqlite",
    ".sql",
}

ASSET_DIR_MARKERS = {
    "asset",
    "assets",
    "css",
    "data",
    "donnees",
    "fichier",
    "fichiers",
    "img",
    "image",
    "images",
    "js",
    "media",
    "ressource",
    "ressources",
    "static",
}


@dataclass
class OrganizationResult:
    status: str
    source: Path
    destination: Path | None = None
    duplicate_of: Path | None = None
    sha256: str | None = None


MigrationEntry = dict[str, str]
MigrationRegistry = dict[str, MigrationEntry]
SourceCacheEntry = dict[str, str]
SourceCache = dict[str, SourceCacheEntry]
SnapshotEntry = dict[str, str]


def current_utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def registry_snapshot_dir(registry_path: Path) -> Path:
    return registry_path.parent / "migration_snapshots"


def normalize_registry_entry(key: str, value: object) -> MigrationEntry | None:
    if not isinstance(value, dict):
        return None
    hash_sha256 = value.get("hash_sha256", key)
    source = value.get("chemin_source_original", "")
    destination = value.get("chemin_destination_final", "")
    timestamp = value.get("timestamp_integration", "")
    if not isinstance(hash_sha256, str) or not isinstance(source, str):
        return None
    if not isinstance(destination, str) or not isinstance(timestamp, str):
        return None
    if not hash_sha256 or not destination:
        return None
    return {
        "hash_sha256": hash_sha256,
        "chemin_source_original": source,
        "chemin_destination_final": destination,
        "timestamp_integration": timestamp,
    }


def load_migration_registry(registry_path: Path) -> MigrationRegistry:
    if not registry_path.exists():
        return {}
    try:
        raw: object = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    entries_object = raw.get("entries", raw)
    if not isinstance(entries_object, dict):
        return {}

    registry: MigrationRegistry = {}
    for key, value in entries_object.items():
        entry = normalize_registry_entry(key, value)
        if entry is not None:
            registry[entry["hash_sha256"]] = entry
    return registry


def load_source_cache(registry_path: Path) -> SourceCache:
    if not registry_path.exists():
        return {}
    try:
        raw: object = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    source_cache_object = raw.get("source_cache", {})
    if not isinstance(source_cache_object, dict):
        return {}

    source_cache: SourceCache = {}
    for key, value in source_cache_object.items():
        if not isinstance(key, str) or not isinstance(value, dict):
            continue
        hash_sha256 = value.get("hash_sha256", "")
        size = value.get("size", "")
        mtime_ns = value.get("mtime_ns", "")
        if all(isinstance(item, str) and item for item in (hash_sha256, size, mtime_ns)):
            source_cache[key] = {
                "hash_sha256": hash_sha256,
                "size": size,
                "mtime_ns": mtime_ns,
            }
    return source_cache


def save_migration_registry(
    registry_path: Path,
    registry: MigrationRegistry,
    source_cache: SourceCache | None = None,
) -> None:
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "updated_at": current_utc_timestamp(),
        "entries": dict(sorted(registry.items())),
        "source_cache": dict(sorted((source_cache or {}).items())),
    }
    registry_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def clone_registry(registry: MigrationRegistry) -> MigrationRegistry:
    return {key: dict(value) for key, value in registry.items()}


def clone_source_cache(source_cache: SourceCache) -> SourceCache:
    return {key: dict(value) for key, value in source_cache.items()}


def source_manifest_entries(roots: list[Path]) -> list[SnapshotEntry]:
    entries: list[SnapshotEntry] = []
    for root in roots:
        if not root.exists():
            continue
        for source in sorted(path for path in root.rglob("*") if path.is_file()):
            entries.append(
                {
                    "hash_sha256": compute_sha256(source),
                    "chemin_source_original": str(source),
                }
            )
    return entries


def write_pre_action_snapshot(
    snapshot_dir: Path,
    roots: list[Path],
    *,
    dry_run: bool,
) -> Path | None:
    entries = source_manifest_entries(roots)
    if not entries:
        return None
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    created_at = current_utc_timestamp()
    stem = created_at.replace(":", "").replace("-", "")
    snapshot_path = snapshot_dir / f"{stem}.json"
    counter = 2
    while snapshot_path.exists():
        snapshot_path = snapshot_dir / f"{stem}_{counter}.json"
        counter += 1
    payload = {
        "version": 1,
        "created_at": created_at,
        "dry_run": dry_run,
        "files": entries,
    }
    snapshot_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return snapshot_path


def registry_live_destination(registry: MigrationRegistry | None, sha256: str) -> Path | None:
    if registry is None:
        return None
    entry = registry.get(sha256)
    if entry is None:
        return None
    destination = Path(entry["chemin_destination_final"])
    return destination if destination.is_file() else None


def registry_source_is_known(registry: MigrationRegistry | None, sha256: str) -> bool:
    if registry is None:
        return False
    entry = registry.get(sha256)
    if entry is None:
        return False
    if entry["chemin_destination_final"] == ARCHIVE_PROCESSED_DESTINATION:
        return True
    return Path(entry["chemin_destination_final"]).is_file()


def source_cache_hit(
    source: Path,
    registry: MigrationRegistry | None,
    source_cache: SourceCache | None,
) -> bool:
    if source_cache is None:
        return False
    entry = source_cache.get(str(source))
    if entry is None:
        return False
    stat = source.stat()
    if entry.get("size") != str(stat.st_size):
        return False
    if entry.get("mtime_ns") != str(stat.st_mtime_ns):
        return False
    return registry_source_is_known(registry, entry["hash_sha256"])


def update_source_cache(source_cache: SourceCache | None, source: Path, sha256: str) -> None:
    if source_cache is None:
        return
    stat = source.stat()
    source_cache[str(source)] = {
        "hash_sha256": sha256,
        "size": str(stat.st_size),
        "mtime_ns": str(stat.st_mtime_ns),
    }


def record_migration(
    registry: MigrationRegistry | None,
    sha256: str,
    source: Path,
    destination: Path,
) -> None:
    if registry is None:
        return
    registry[sha256] = {
        "hash_sha256": sha256,
        "chemin_source_original": str(source),
        "chemin_destination_final": str(destination),
        "timestamp_integration": current_utc_timestamp(),
    }


def record_processed_archive(
    registry: MigrationRegistry | None,
    sha256: str,
    archive: Path,
) -> None:
    if registry is None:
        return
    registry[sha256] = {
        "hash_sha256": sha256,
        "chemin_source_original": str(archive),
        "chemin_destination_final": ARCHIVE_PROCESSED_DESTINATION,
        "timestamp_integration": current_utc_timestamp(),
    }


def seed_registry_from_final(registry: MigrationRegistry, final_root: Path) -> None:
    initialize_state_from_final(final_root, registry)


def normalize_text(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    lowered = ascii_value.lower()
    for separator in ("_", "-", "/", "\\"):
        lowered = lowered.replace(separator, " ")
    return " ".join(lowered.split())


def safe_filename(name: str) -> str:
    original = Path(name)
    suffix = original.suffix
    stem = original.stem if suffix else name
    ascii_value = unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode("ascii")
    cleaned = []
    for char in ascii_value:
        if char.isalnum() or char in {".", "-", "_"}:
            cleaned.append(char)
        elif char.isspace() or char in {"[", "]", "(", ")", "'", '"'}:
            cleaned.append("_")
    compact = "_".join(part for part in "".join(cleaned).split("_") if part)
    return f"{compact or 'ressource'}{suffix}"


def safe_stem(value: str) -> str:
    return Path(safe_filename(value)).stem or "source"


def safe_relative_path(path: Path) -> Path:
    return Path(*(safe_filename(part) for part in path.parts))


def should_skip(path: Path) -> bool:
    lowered_parts = {part.lower() for part in path.parts}
    if lowered_parts & TECHNICAL_PARTS:
        return True
    if path.name.lower().endswith(".zip.failed"):
        return True
    if path.name.startswith(".") and path.name not in {".nojekyll"}:
        return True
    return path.suffix.lower() in SKIP_SUFFIXES


def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify_level(path: Path) -> Path:
    text = normalize_text(" ".join(path.parts))
    tokens = set(text.split())
    official_markers = (
        "eduscol",
        "boen",
        "bulletin officiel",
        "referentiel",
        "programme",
        "competence",
        "epreuve",
        "specialite-nsi",
    )
    if any(marker in text for marker in official_markers):
        return LEVEL_PROGRAMMES

    transversal_markers = ("swinnen", "apprendre_python", "manuel", "global", "wikibooks")
    if any(marker in text for marker in transversal_markers):
        return LEVEL_TRANSVERSAL

    terminale_markers = (
        "terminale",
        "terminales",
        "tle",
        "tnsi",
        "t nsi",
        "bac",
        "bns",
        "tale",
        "sujet_b",
    )
    premiere_markers = (
        "premiere",
        "premieres",
        "1ere",
        "1re",
        "1nsi",
        "p_nsi",
        "prem",
        "nsi 1",
        "nsi1",
    )
    if (
        any(marker in tokens for marker in terminale_markers)
        or "t nsi" in text
        or "sujet bac" in text
    ):
        return LEVEL_TERMINALE
    if any(marker in tokens for marker in premiere_markers) or "p nsi" in text or "nsi 1" in text:
        return LEVEL_PREMIERE
    return LEVEL_TRANSVERSAL


def classify_type(path: Path) -> Path | None:
    text = normalize_text(" ".join(path.parts))
    suffix = path.suffix.lower()

    if any(marker in text for marker in EVALUATION_MARKERS):
        return TYPE_DIRS["evaluation"]
    if any(marker in text for marker in ("projet", "mini-projet", "mini_projet", "dm")):
        return TYPE_DIRS["projet"]
    if suffix == ".ipynb" or any(marker in text for marker in TP_MARKERS):
        return TYPE_DIRS["tp"]
    if any(marker in text for marker in TD_MARKERS):
        return TYPE_DIRS["td"]
    if any(marker in text for marker in ("fiche", "synthese", "memo", "resume", "bilan")):
        return TYPE_DIRS["fiche"]
    if any(marker in text for marker in ("cours", "lecon", "chapitre", "slides", "polycopie")):
        return TYPE_DIRS["cours"]
    if suffix == ".py":
        return TYPE_DIRS["programmation"]
    return None


def classify_destination(path: Path) -> Path:
    level = classify_level(path)
    if level in {LEVEL_PROGRAMMES, LEVEL_TRANSVERSAL}:
        return level
    doc_type = classify_type(path)
    if doc_type is None:
        return LEVEL_TRANSVERSAL
    return level / doc_type


def origin_name(path: Path, transit_root: Path) -> str:
    try:
        relative = path.relative_to(transit_root)
    except ValueError:
        return "source"
    parts = list(relative.parts)
    if not parts:
        return "source"
    if parts[0] in {source.name for source in SOURCE_DIRS} and len(parts) > 1:
        return parts[1]
    if parts[0] == EXTRACTED_ZIP_DIR and len(parts) > 1:
        return parts[1]
    return parts[0]


def drive_origin_name(path: Path, drive_root: Path) -> str:
    try:
        relative = path.relative_to(drive_root)
    except ValueError:
        return "Documents_DRIVE"
    return relative.parts[0] if relative.parts else "Documents_DRIVE"


def unique_destination(destination_dir: Path, filename: str, origin: str) -> tuple[Path, bool]:
    destination = destination_dir / safe_filename(filename)
    if not destination.exists():
        return destination, False

    suffix = destination.suffix
    stem = destination.stem
    candidate = destination_dir / f"{stem}_{safe_stem(origin)}{suffix}"
    counter = 2
    while candidate.exists():
        candidate = destination_dir / f"{stem}_{safe_stem(origin)}_{counter}{suffix}"
        counter += 1
    return candidate, True


def unique_nested_destination(
    base_dir: Path,
    relative_path: Path,
    origin: str,
) -> tuple[Path, bool]:
    destination = base_dir / safe_relative_path(relative_path)
    if not destination.exists():
        return destination, False

    suffix = destination.suffix
    stem = destination.stem
    parent = destination.parent

    candidate = parent / f"{stem}_{safe_stem(origin)}{suffix}"
    counter = 2
    while candidate.exists():
        candidate = parent / f"{stem}_{safe_stem(origin)}_{counter}{suffix}"
        counter += 1
    return candidate, True


def is_structured_drive_asset(path: Path, drive_root: Path) -> bool:
    try:
        relative = path.relative_to(drive_root)
    except ValueError:
        relative = path
    normalized_parts = {normalize_text(part) for part in relative.parts[:-1]}
    if normalized_parts & ASSET_DIR_MARKERS:
        return True
    return path.suffix.lower() in ASSET_SUFFIXES and len(relative.parts) > 1


def drive_asset_container(path: Path, drive_root: Path) -> Path | None:
    asset_parent = None
    for parent in path.parents:
        if parent == drive_root:
            break
        if normalize_text(parent.name) in ASSET_DIR_MARKERS:
            asset_parent = parent.parent
    if asset_parent and asset_parent != drive_root:
        return asset_parent
    return None


def prune_empty_parents(start: Path, stop: Path) -> None:
    current = start
    while current != stop and stop in current.parents:
        try:
            current.rmdir()
        except OSError:
            return
        current = current.parent


def move_drive_duplicate(source: Path, drive_root: Path, final_root: Path) -> Path:
    relative = source.relative_to(drive_root)
    destination, _ = unique_nested_destination(
        final_root / DUPLICATE_DRIVE_DIR,
        relative,
        drive_origin_name(source, drive_root),
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))
    prune_empty_parents(source.parent, drive_root)
    return destination


def is_junk_file(path: Path) -> bool:
    return path.name.lower() in JUNK_FILENAMES


def evacuate_skipped_drive_file(
    source: Path,
    drive_root: Path,
    final_root: Path,
) -> OrganizationResult:
    if is_junk_file(source):
        source.unlink()
        prune_empty_parents(source.parent, drive_root)
        return OrganizationResult("drive_junk_deleted", source)

    relative = source.relative_to(drive_root)
    destination, _ = unique_nested_destination(
        final_root / SKIPPED_DRIVE_DIR,
        relative,
        drive_origin_name(source, drive_root),
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))
    prune_empty_parents(source.parent, drive_root)
    return OrganizationResult("drive_skipped", source, destination)


def move_drive_file(
    source: Path,
    drive_root: Path,
    final_root: Path,
    seen_hashes: dict[str, Path],
    category_counts: dict[str, int] | Counter[str],
    registry: MigrationRegistry | None = None,
) -> OrganizationResult:
    if should_skip(source) or source.suffix.lower() == ".zip":
        return evacuate_skipped_drive_file(source, drive_root, final_root)

    sha256 = compute_sha256(source)
    known_destination = registry_live_destination(registry, sha256)
    if known_destination is not None:
        seen_hashes.setdefault(sha256, known_destination)
        duplicate_destination = move_drive_duplicate(source, drive_root, final_root)
        return OrganizationResult(
            "drive_registry_known",
            source,
            duplicate_destination,
            duplicate_of=known_destination,
            sha256=sha256,
        )

    if sha256 in seen_hashes:
        duplicate_destination = move_drive_duplicate(source, drive_root, final_root)
        return OrganizationResult(
            "drive_duplicate",
            source,
            duplicate_destination,
            duplicate_of=seen_hashes[sha256],
            sha256=sha256,
        )

    asset_parent = (
        drive_asset_container(source, drive_root)
        if is_structured_drive_asset(source, drive_root)
        else None
    )
    if asset_parent:
        destination_relative = classify_destination(asset_parent)
        sub_relative_path = source.relative_to(asset_parent)
        destination_dir = final_root / destination_relative
        destination, renamed = unique_nested_destination(
            destination_dir,
            sub_relative_path,
            drive_origin_name(source, drive_root),
        )
    else:
        destination_relative = classify_destination(source)
        destination_dir = final_root / destination_relative
        destination, renamed = unique_destination(
            destination_dir,
            source.name,
            drive_origin_name(source, drive_root),
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))
    prune_empty_parents(source.parent, drive_root)
    seen_hashes[sha256] = destination
    record_migration(registry, sha256, source, destination)
    category_key = str(destination_relative)
    category_counts[category_key] = category_counts.get(category_key, 0) + 1
    return OrganizationResult(
        "drive_moved_renamed" if renamed else "drive_moved",
        source,
        destination,
        sha256=sha256,
    )


def organize_file(
    source: Path,
    transit_root: Path,
    final_root: Path,
    seen_hashes: dict[str, Path],
    category_counts: dict[str, int] | Counter[str],
    registry: MigrationRegistry | None = None,
) -> OrganizationResult:
    if should_skip(source) or source.suffix.lower() == ".zip":
        return OrganizationResult("skipped", source)

    sha256 = compute_sha256(source)
    known_destination = registry_live_destination(registry, sha256)
    if known_destination is not None:
        seen_hashes.setdefault(sha256, known_destination)
        return OrganizationResult(
            "registry_known",
            source,
            known_destination,
            duplicate_of=known_destination,
            sha256=sha256,
        )

    if sha256 in seen_hashes:
        return OrganizationResult(
            "duplicate",
            source,
            duplicate_of=seen_hashes[sha256],
            sha256=sha256,
        )

    destination_relative = classify_destination(source)
    destination_dir = final_root / destination_relative
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination, renamed = unique_destination(
        destination_dir,
        source.name,
        origin_name(source, transit_root),
    )
    shutil.copy2(source, destination)
    seen_hashes[sha256] = destination
    record_migration(registry, sha256, source, destination)
    category_key = str(destination_relative)
    category_counts[category_key] = category_counts.get(category_key, 0) + 1
    return OrganizationResult(
        "copied_renamed" if renamed else "copied",
        source,
        destination,
        sha256=sha256,
    )


def reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_sources_to_transit(
    source_dirs: list[Path],
    transit_root: Path,
    registry: MigrationRegistry | None = None,
    copy_counts: Counter[str] | None = None,
    source_cache: SourceCache | None = None,
    purge_source_files: bool = False,
) -> int:
    copied = 0
    for source_root in source_dirs:
        if not source_root.exists():
            print(f"[SOURCE ABSENTE] {source_root}", flush=True)
            continue
        target_root = transit_root / source_root.name
        source_files = sorted(path for path in source_root.rglob("*") if path.is_file())
        for source in source_files:
            if not source.exists():
                continue
            if not source.is_file() or should_skip(source):
                continue
            if source_cache_hit(source, registry, source_cache):
                if copy_counts is not None:
                    copy_counts["source_registry_known"] += 1
                purge_source_file(source, source_root, purge_source_files)
                continue
            sha256 = compute_sha256(source)
            update_source_cache(source_cache, source, sha256)
            if registry_source_is_known(registry, sha256):
                if copy_counts is not None:
                    copy_counts["source_registry_known"] += 1
                purge_source_file(source, source_root, purge_source_files)
                continue
            relative = source.relative_to(source_root)
            destination = target_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                base = destination.with_suffix("")
                suffix = destination.suffix
                counter = 2
                while destination.exists():
                    destination = base.with_name(f"{base.name}_{counter}").with_suffix(suffix)
                    counter += 1
            shutil.copy2(source, destination)
            purge_source_file(source, source_root, purge_source_files)
            copied += 1
    return copied


def purge_source_file(source: Path, source_root: Path, purge_source_files: bool) -> None:
    if not purge_source_files:
        return
    if source.suffix.lower() == ".zip":
        return
    try:
        source.unlink()
    except FileNotFoundError:
        return
    prune_empty_parents(source.parent, source_root)


def extract_zip_to_transit(
    archive: Path,
    transit_root: Path,
    registry: MigrationRegistry | None = None,
) -> int:
    archive_hash = compute_sha256(archive)
    if not zipfile.is_zipfile(archive):
        print(f"[ZIP INVALIDE] {archive}", flush=True)
        record_processed_archive(registry, archive_hash, archive)
        return 0

    extract_base = transit_root / EXTRACTED_ZIP_DIR / safe_stem(archive.stem)
    counter = 2
    while extract_base.exists():
        extract_base = transit_root / EXTRACTED_ZIP_DIR / f"{safe_stem(archive.stem)}_{counter}"
        counter += 1
    try:
        safe_extract_zip(archive, extract_base)
    except (ArchiveSecurityError, zipfile.BadZipFile, OSError, RuntimeError) as exc:
        print(f"[ZIP ERREUR] {archive}: {exc}", flush=True)
        shutil.rmtree(extract_base, ignore_errors=True)
        record_processed_archive(registry, archive_hash, archive)
        return 0

    record_processed_archive(registry, archive_hash, archive)
    archive.unlink()
    return 1


def extract_all_zips(
    transit_root: Path,
    registry: MigrationRegistry | None = None,
) -> tuple[int, int]:
    extracted = 0
    failed = 0
    while True:
        archives = [path for path in transit_root.rglob("*.zip") if path.is_file()]
        if not archives:
            return extracted, failed
        progressed = False
        for archive in archives:
            count = extract_zip_to_transit(archive, transit_root, registry=registry)
            if count:
                extracted += count
                progressed = True
            else:
                failed += 1
                failed_target = archive.with_suffix(archive.suffix + ".failed")
                archive.rename(failed_target)
        if not progressed:
            return extracted, failed


def ensure_final_tree(final_root: Path) -> None:
    for level in (LEVEL_PREMIERE, LEVEL_TERMINALE):
        for doc_type in TYPE_DIRS.values():
            (final_root / level / doc_type).mkdir(parents=True, exist_ok=True)
    (final_root / LEVEL_PROGRAMMES).mkdir(parents=True, exist_ok=True)
    (final_root / LEVEL_TRANSVERSAL).mkdir(parents=True, exist_ok=True)
    (final_root / DUPLICATE_DRIVE_DIR).mkdir(parents=True, exist_ok=True)
    (final_root / SKIPPED_DRIVE_DIR).mkdir(parents=True, exist_ok=True)


def is_internal_final_path(path: Path, final_root: Path) -> bool:
    try:
        relative_parts = path.relative_to(final_root).parts
    except ValueError:
        return False
    return bool(relative_parts and relative_parts[0] in INTERNAL_FINAL_DIRS)


def normalized_category_key(path: Path, final_root: Path) -> str | None:
    try:
        rel_dir = path.parent.relative_to(final_root)
    except ValueError:
        return None
    parts = rel_dir.parts
    if not parts:
        return None
    if parts[0] in INTERNAL_FINAL_DIRS:
        return None
    if parts[0] in {str(LEVEL_PREMIERE), str(LEVEL_TERMINALE)}:
        if len(parts) >= 2:
            return str(Path(parts[0]) / parts[1])
        return str(rel_dir)
    if parts[0] in {str(LEVEL_PROGRAMMES), str(LEVEL_TRANSVERSAL)}:
        return parts[0]
    return str(rel_dir)


def initialize_state_from_final(
    final_root: Path,
    registry: MigrationRegistry,
) -> tuple[dict[str, Path], Counter[str]]:
    seen_hashes: dict[str, Path] = {}
    category_counts: Counter[str] = Counter()
    if not final_root.exists():
        return seen_hashes, category_counts

    dest_to_hash: dict[str, str] = {}
    for entry in registry.values():
        destination = entry["chemin_destination_final"]
        if destination == ARCHIVE_PROCESSED_DESTINATION:
            continue
        dest_to_hash.setdefault(destination, entry["hash_sha256"])

    for source in sorted(final_root.rglob("*")):
        if not source.is_file() or should_skip(source):
            continue
        if is_internal_final_path(source, final_root):
            continue
        category_key = normalized_category_key(source, final_root)
        if category_key:
            category_counts[category_key] += 1
        source_key = str(source)
        sha256 = dest_to_hash.get(source_key)
        if sha256 is None:
            sha256 = compute_sha256(source)
            record_migration(registry, sha256, source, source)
            dest_to_hash.setdefault(source_key, sha256)
        seen_hashes.setdefault(sha256, source)
    return seen_hashes, category_counts


def seed_existing_hashes(final_root: Path) -> tuple[dict[str, Path], Counter[str]]:
    return initialize_state_from_final(final_root, {})


def seed_existing_from_registry(
    final_root: Path,
    registry: MigrationRegistry,
) -> tuple[dict[str, Path], Counter[str]]:
    return initialize_state_from_final(final_root, registry)


def seed_hashes_from_final(final_root: Path, seen_hashes: dict[str, Path]) -> None:
    existing_hashes, _ = initialize_state_from_final(final_root, {})
    for sha256, path in existing_hashes.items():
        seen_hashes.setdefault(sha256, path)


def organize_transit(
    transit_root: Path,
    final_root: Path,
    seen_hashes: dict[str, Path] | None = None,
    category_counts: Counter[str] | None = None,
    registry: MigrationRegistry | None = None,
) -> tuple[Counter[str], Counter[str], dict[str, Path]]:
    ensure_final_tree(final_root)
    if seen_hashes is None or category_counts is None:
        existing_hashes, existing_category_counts = seed_existing_hashes(final_root)
        if seen_hashes is None:
            seen_hashes = existing_hashes
        else:
            for sha256, path in existing_hashes.items():
                seen_hashes.setdefault(sha256, path)
        if category_counts is None:
            category_counts = existing_category_counts
    status_counts: Counter[str] = Counter()

    for source in sorted(transit_root.rglob("*")):
        if not source.is_file():
            continue
        result = organize_file(
            source,
            transit_root,
            final_root,
            seen_hashes,
            category_counts,
            registry=registry,
        )
        status_counts[result.status] += 1
    return category_counts, status_counts, seen_hashes


def integrate_drive_dir(
    drive_root: Path,
    final_root: Path,
    seen_hashes: dict[str, Path],
    category_counts: dict[str, int] | Counter[str],
    registry: MigrationRegistry | None = None,
) -> Counter[str]:
    drive_counts: Counter[str] = Counter()
    if not drive_root.exists():
        print(f"[DRIVE ABSENT] {drive_root}", flush=True)
        drive_counts["drive_missing"] = 1
        return drive_counts

    if not seen_hashes:
        if registry:
            registry_hashes, _ = seed_existing_from_registry(final_root, registry)
            for sha256, destination in registry_hashes.items():
                seen_hashes.setdefault(sha256, destination)
        else:
            seed_hashes_from_final(final_root, seen_hashes)
    drive_files = sorted(p for p in drive_root.rglob("*") if p.is_file())
    for source in drive_files:
        if not source.exists():
            continue
        result = move_drive_file(
            source,
            drive_root,
            final_root,
            seen_hashes,
            category_counts,
            registry=registry,
        )
        if result.status in {"drive_moved", "drive_moved_renamed"}:
            drive_counts["drive_moved"] += 1
            if result.status == "drive_moved_renamed":
                drive_counts["drive_moved_renamed"] += 1
        else:
            drive_counts[result.status] += 1
    return drive_counts


def cleanup_transit(transit_root: Path, keep_transit: bool | None = None) -> None:
    if keep_transit is None:
        keep_transit = os.getenv("NSI_KEEP_TRANSIT", "").lower() in {"1", "true", "yes", "oui"}
    if keep_transit:
        print(f"Transit conservé : {transit_root}", flush=True)
        return
    shutil.rmtree(transit_root, ignore_errors=True)
    print(f"Transit nettoyé : {transit_root}", flush=True)


def final_resource_files(final_root: Path) -> list[Path]:
    files = []
    for source in final_root.rglob("*"):
        if not source.is_file():
            continue
        if is_internal_final_path(source, final_root):
            continue
        files.append(source)
    return files


def print_report(
    category_counts: Counter[str],
    status_counts: Counter[str],
    drive_counts: Counter[str],
    final_root: Path,
) -> None:
    print("\nRAPPORT ORGANISATION NSI", flush=True)
    print("=" * 72, flush=True)
    for category_key in sorted(category_counts):
        if category_counts[category_key]:
            print(f"{category_key} | {category_counts[category_key]}", flush=True)
    print("-" * 72, flush=True)
    print(f"copied={status_counts['copied']}", flush=True)
    print(f"copied_renamed={status_counts['copied_renamed']}", flush=True)
    print(f"registry_known={status_counts['registry_known']}", flush=True)
    print(f"duplicates_eliminated={status_counts['duplicate']}", flush=True)
    print(f"skipped={status_counts['skipped']}", flush=True)
    print(f"drive_moved={drive_counts['drive_moved']}", flush=True)
    print(f"drive_moved_renamed={drive_counts['drive_moved_renamed']}", flush=True)
    print(f"drive_registry_known={drive_counts['drive_registry_known']}", flush=True)
    print(f"drive_duplicates_eliminated={drive_counts['drive_duplicate']}", flush=True)
    print(f"drive_skipped={drive_counts['drive_skipped']}", flush=True)
    print(f"drive_junk_deleted={drive_counts['drive_junk_deleted']}", flush=True)
    print(f"drive_missing={drive_counts['drive_missing']}", flush=True)
    duplicate_quarantine_files = [
        p for p in (final_root / DUPLICATE_DRIVE_DIR).rglob("*") if p.is_file()
    ]
    skipped_quarantine_files = [
        p for p in (final_root / SKIPPED_DRIVE_DIR).rglob("*") if p.is_file()
    ]
    print(f"drive_duplicate_quarantine_files={len(duplicate_quarantine_files)}", flush=True)
    print(f"drive_skipped_quarantine_files={len(skipped_quarantine_files)}", flush=True)
    print(f"total_final_resource_files={len(final_resource_files(final_root))}", flush=True)
    print("=" * 72, flush=True)


def write_run_summary(
    summary_path: Path,
    copied_to_transit: int,
    extracted_archives: int,
    failed_archives: int,
    status_counts: Counter[str],
    drive_counts: Counter[str],
    copy_counts: Counter[str],
    final_root: Path,
) -> None:
    new_integrated = (
        status_counts["copied"]
        + status_counts["copied_renamed"]
        + drive_counts["drive_moved"]
    )
    known_ignored = (
        copy_counts["source_registry_known"]
        + status_counts["registry_known"]
        + drive_counts["drive_registry_known"]
    )
    duplicate_count = status_counts["duplicate"] + drive_counts["drive_duplicate"]
    skipped_count = status_counts["skipped"] + drive_counts["drive_skipped"]
    error_count = failed_archives + drive_counts["drive_missing"]
    lines = [
        "LAST_RUN_SUMMARY_NSI",
        f"timestamp={current_utc_timestamp()}",
        f"copied_to_transit={copied_to_transit}",
        f"source_registry_known={copy_counts['source_registry_known']}",
        f"zip_extracted={extracted_archives}",
        f"zip_failed={failed_archives}",
        f"new_integrated={new_integrated}",
        f"known_ignored={known_ignored}",
        f"duplicates_eliminated={duplicate_count}",
        f"skipped={skipped_count}",
        f"errors={error_count}",
        f"final_resource_files={len(final_resource_files(final_root))}",
    ]
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _copy_dry_run_roots(source_dirs: list[Path], scratch_root: Path) -> list[Path]:
    copied_dirs: list[Path] = []
    for index, source_root in enumerate(source_dirs):
        destination = scratch_root / f"{index:02d}_{safe_filename(source_root.name)}"
        if source_root.exists():
            shutil.copytree(source_root, destination)
        copied_dirs.append(destination)
    return copied_dirs


def _copy_dry_run_drive(drive_dir: Path, scratch_root: Path) -> Path:
    destination = scratch_root / safe_filename(drive_dir.name)
    if drive_dir.exists():
        shutil.copytree(drive_dir, destination)
    return destination


def _run_organization(
    selected_source_dirs: list[Path],
    selected_drive_dir: Path,
    selected_transit_dir: Path,
    selected_final_dir: Path,
    selected_registry_path: Path,
    selected_summary_path: Path,
    keep_transit: bool | None,
    purge_source_files: bool,
) -> None:
    reset_dir(selected_transit_dir)
    registry = load_migration_registry(selected_registry_path)
    source_cache = load_source_cache(selected_registry_path)
    original_registry = clone_registry(registry)
    original_source_cache = clone_source_cache(source_cache)
    seen_hashes, category_counts = initialize_state_from_final(selected_final_dir, registry)

    copy_counts: Counter[str] = Counter()
    copied_to_transit = copy_sources_to_transit(
        selected_source_dirs,
        selected_transit_dir,
        registry=registry,
        copy_counts=copy_counts,
        source_cache=source_cache,
        purge_source_files=purge_source_files,
    )
    print(f"Fichiers copiés vers transit : {copied_to_transit}", flush=True)

    extracted, failed = extract_all_zips(selected_transit_dir, registry=registry)
    print(f"Archives ZIP extraites : {extracted}", flush=True)
    print(f"Archives ZIP en échec : {failed}", flush=True)

    category_counts, status_counts, seen_hashes = organize_transit(
        selected_transit_dir,
        selected_final_dir,
        seen_hashes,
        category_counts,
        registry=registry,
    )
    drive_counts = integrate_drive_dir(
        selected_drive_dir,
        selected_final_dir,
        seen_hashes,
        category_counts,
        registry=registry,
    )
    if registry != original_registry or source_cache != original_source_cache:
        save_migration_registry(selected_registry_path, registry, source_cache)
    write_run_summary(
        selected_summary_path,
        copied_to_transit,
        extracted,
        failed,
        status_counts,
        drive_counts,
        copy_counts,
        selected_final_dir,
    )
    print_report(category_counts, status_counts, drive_counts, selected_final_dir)
    cleanup_transit(selected_transit_dir, keep_transit)


def main(
    source_dirs: list[Path] | None = None,
    drive_dir: Path | None = None,
    transit_dir: Path | None = None,
    final_dir: Path | None = None,
    registry_path: Path | None = None,
    summary_path: Path | None = None,
    keep_transit: bool | None = None,
    purge_source_files: bool = False,
    dry_run: bool = False,
) -> None:
    selected_source_dirs = source_dirs if source_dirs is not None else SOURCE_DIRS
    selected_drive_dir = drive_dir if drive_dir is not None else DRIVE_DIR
    selected_transit_dir = transit_dir if transit_dir is not None else TRANSIT_DIR
    selected_final_dir = final_dir if final_dir is not None else FINAL_DIR
    selected_registry_path = registry_path if registry_path is not None else REGISTRY_FILE
    selected_summary_path = summary_path if summary_path is not None else RUN_SUMMARY_FILE

    print("INITIALISATION ORGANISATION NSI", flush=True)
    print(f"Transit : {selected_transit_dir}", flush=True)
    print(f"Final : {selected_final_dir}", flush=True)
    print(f"Drive : {selected_drive_dir}", flush=True)
    print(f"Registre : {selected_registry_path}", flush=True)
    if dry_run:
        print("Mode dry-run : aucune source réelle ne sera déplacée", flush=True)

    write_pre_action_snapshot(
        registry_snapshot_dir(selected_registry_path),
        [*selected_source_dirs, selected_drive_dir],
        dry_run=dry_run,
    )
    if dry_run:
        with TemporaryDirectory(prefix="nsi_organizer_dry_run_") as scratch:
            scratch_root = Path(scratch)
            simulated_source_dirs = _copy_dry_run_roots(
                selected_source_dirs,
                scratch_root / "sources",
            )
            simulated_drive_dir = _copy_dry_run_drive(
                selected_drive_dir,
                scratch_root / "drive",
            )
            simulated_registry = scratch_root / "migration_registry.json"
            if selected_registry_path.exists():
                simulated_registry.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(selected_registry_path, simulated_registry)
            _run_organization(
                simulated_source_dirs,
                simulated_drive_dir,
                scratch_root / "transit",
                scratch_root / "final",
                simulated_registry,
                scratch_root / "last_run_summary.log",
                keep_transit=True,
                purge_source_files=False,
            )
        return

    _run_organization(
        selected_source_dirs,
        selected_drive_dir,
        selected_transit_dir,
        selected_final_dir,
        selected_registry_path,
        selected_summary_path,
        keep_transit,
        purge_source_files,
    )


if __name__ == "__main__":
    main()
