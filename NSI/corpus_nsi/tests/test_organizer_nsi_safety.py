from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
ORGANIZER_PATH = ROOT / "scrapping_NSI" / "organizer_nsi.py"


def load_organizer() -> ModuleType:
    assert ORGANIZER_PATH.exists(), f"missing organizer module: {ORGANIZER_PATH}"
    spec = importlib.util.spec_from_file_location("organizer_nsi_safety", ORGANIZER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_dry_run_preserves_source_and_drive_files(tmp_path: Path) -> None:
    organizer = load_organizer()
    source_root = tmp_path / "ressources_nsi_extraites"
    drive_root = tmp_path / "Documents_DRIVE"
    final_root = tmp_path / "ressources_nsi_centralisees"
    transit_root = tmp_path / "transit"
    registry_path = tmp_path / "migration_registry.json"
    summary_path = tmp_path / "last_run_summary.log"

    scraped_file = source_root / "Site A" / "premiere" / "cours.pdf"
    drive_file = drive_root / "Algo_Premiere" / "Cours drive.pdf"
    scraped_file.parent.mkdir(parents=True)
    drive_file.parent.mkdir(parents=True)
    scraped_file.write_bytes(b"cours scrape")
    drive_file.write_bytes(b"cours drive")

    organizer.main(
        source_dirs=[source_root],
        drive_dir=drive_root,
        transit_dir=transit_root,
        final_dir=final_root,
        registry_path=registry_path,
        summary_path=summary_path,
        keep_transit=True,
        dry_run=True,
    )

    assert scraped_file.read_bytes() == b"cours scrape"
    assert drive_file.read_bytes() == b"cours drive"
    assert not list(final_root.rglob("*"))
    assert not transit_root.exists()


def test_snapshot_is_persisted_before_real_relocation(tmp_path: Path) -> None:
    organizer = load_organizer()
    drive_root = tmp_path / "Documents_DRIVE"
    final_root = tmp_path / "ressources_nsi_centralisees"
    transit_root = tmp_path / "transit"
    registry_path = tmp_path / "migration_registry.json"
    summary_path = tmp_path / "last_run_summary.log"
    drive_file = drive_root / "Algo_Premiere" / "Cours drive.pdf"
    drive_file.parent.mkdir(parents=True)
    drive_file.write_bytes(b"contenu drive premiere")

    organizer.main(
        source_dirs=[],
        drive_dir=drive_root,
        transit_dir=transit_root,
        final_dir=final_root,
        registry_path=registry_path,
        summary_path=summary_path,
        keep_transit=True,
    )

    snapshots = sorted((tmp_path / "migration_snapshots").glob("*.json"))
    assert len(snapshots) == 1
    payload = json.loads(snapshots[0].read_text(encoding="utf-8"))
    assert payload["files"] == [
        {
            "hash_sha256": organizer.compute_sha256(
                final_root / "01_Premiere_NSI" / "01_Cours" / "Cours_drive.pdf"
            ),
            "chemin_source_original": str(drive_file),
        }
    ]


def test_second_run_is_noop_and_keeps_original_registry_source(tmp_path: Path) -> None:
    organizer = load_organizer()
    drive_root = tmp_path / "Documents_DRIVE"
    final_root = tmp_path / "ressources_nsi_centralisees"
    transit_root = tmp_path / "transit"
    registry_path = tmp_path / "migration_registry.json"
    summary_path = tmp_path / "last_run_summary.log"
    drive_file = drive_root / "Algo_Premiere" / "Cours drive.pdf"
    drive_file.parent.mkdir(parents=True)
    drive_file.write_bytes(b"contenu drive premiere")

    kwargs = {
        "source_dirs": [],
        "drive_dir": drive_root,
        "transit_dir": transit_root,
        "final_dir": final_root,
        "registry_path": registry_path,
        "summary_path": summary_path,
        "keep_transit": True,
    }
    organizer.main(**kwargs)
    registry_after_first = registry_path.read_text(encoding="utf-8")
    organizer.main(**kwargs)

    assert registry_path.read_text(encoding="utf-8") == registry_after_first
    entries = json.loads(registry_after_first)["entries"]
    [entry] = [
        entry
        for entry in entries.values()
        if entry["chemin_destination_final"].endswith("Cours_drive.pdf")
    ]
    assert entry["chemin_source_original"] == str(drive_file)
    assert len(list((tmp_path / "migration_snapshots").glob("*.json"))) == 1
