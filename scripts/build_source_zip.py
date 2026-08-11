#!/usr/bin/env python3
"""Build an exploitable ZIP archive of the repository without VCS artifacts."""

from __future__ import annotations

from pathlib import Path
import sys
import zipfile


from scripts.build_source_archive import DIST, ROOT, excluded, iter_source_paths

ZIP_PATH = DIST / "nsi-enseignement_source_clean.zip"
STABLE_ZIP_DATETIME = (1980, 1, 1, 0, 0, 0)


def build_zip(root: Path = ROOT, target: Path = ZIP_PATH) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.unlink()
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in iter_source_paths(root):
            rel = path.relative_to(root)
            if excluded(rel):
                continue
            if path == target:
                continue
            arcname = Path("nsi-enseignement") / rel
            if path.is_file():
                info = zipfile.ZipInfo(arcname.as_posix(), date_time=STABLE_ZIP_DATETIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (0o644 & 0xFFFF) << 16
                archive.writestr(info, path.read_bytes())
    return target


def main() -> int:
    target = build_zip()
    print(f"build_source_zip: wrote {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
