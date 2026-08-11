#!/usr/bin/env python3
"""Runtime guard for TP pedagogical asset checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import time

from scripts._qa_common import ROOT
from scripts.check_first_batch_document_quality import FIRST_BATCH_PREFIXES
from scripts.check_tp_pedagogical_assets import analyze_tp_pedagogy


@dataclass
class TpRuntimeResult:
    errors: list[str] = field(default_factory=list)
    prefix_durations: dict[str, float] = field(default_factory=dict)
    total_duration: float = 0.0


def analyze_tp_runtime(
    root: Path = ROOT,
    prefixes: list[str] | None = None,
    total_timeout_seconds: float = 60.0,
    prefix_timeout_seconds: float = 20.0,
) -> TpRuntimeResult:
    if prefixes is None:
        discovered = sorted(
            {
                path.name
                for path in (root / "03_progressions" / "supports").glob("*/*")
                if (path / "code").exists()
            }
        )
        prefixes = list(dict.fromkeys([*FIRST_BATCH_PREFIXES, "P06", *discovered]))
    started = time.monotonic()
    pedagogy = analyze_tp_pedagogy(
        root,
        prefixes=list(prefixes),
        prefix_timeout_seconds=prefix_timeout_seconds,
        total_timeout_seconds=total_timeout_seconds,
    )
    total = time.monotonic() - started
    result = TpRuntimeResult(
        errors=list(pedagogy.errors),
        prefix_durations=dict(pedagogy.prefix_durations),
        total_duration=total,
    )
    if total > total_timeout_seconds and not any("durée totale" in error for error in result.errors):
        result.errors.append(f"durée totale trop longue ({total:.2f}s > {total_timeout_seconds:.2f}s)")
    return result


def main() -> int:
    result = analyze_tp_runtime()
    print(f"Durée totale check_tp_pedagogical_assets : {result.total_duration:.2f}s")
    for prefix, duration in sorted(result.prefix_durations.items()):
        print(f"- {prefix}: {duration:.2f}s")
    if result.errors:
        print("check_tp_pedagogical_assets_runtime: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print("check_tp_pedagogical_assets_runtime: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
