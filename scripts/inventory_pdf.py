"""PDF attribution and bounded page-count helpers."""

from __future__ import annotations

import re
import subprocess
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping


def page_count_with_pdfinfo(
    path: Path,
    *,
    runner: Callable[..., Any],
    timeout_seconds: int,
) -> tuple[int | None, str | None]:
    try:
        completed = runner(
            ["pdfinfo", str(path)],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return None, f"pdfinfo timeout ({timeout_seconds}s)"
    except OSError as exc:
        return None, f"pdfinfo indisponible: {type(exc).__name__}"
    if completed.returncode != 0:
        return None, f"pdfinfo en echec (code {completed.returncode})"
    match = re.search(r"(?m)^Pages:\s*(\d+)\s*$", completed.stdout)
    if match is None:
        return None, "pdfinfo ne fournit pas le nombre de pages"
    return int(match.group(1)), None


def attribute_pdf(path: str, inventory: Mapping[str, Any]) -> dict[str, Any]:
    pure = PurePosixPath(path)
    stem = pure.stem
    for manual_id, manual_model in inventory["manuals"].items():
        for chapter_id in manual_model["chapters"]:
            if chapter_id in pure.parts or stem.startswith(chapter_id + "_"):
                prefix = chapter_id + "_"
                return {
                    "chapter": chapter_id,
                    "manual": manual_id,
                    "scope": "chapter",
                    "variant": stem[len(prefix) :] if stem.startswith(prefix) else None,
                }
    aliases = (
        ("MANUEL_TSPE_2026-2027", "TSPE_2026_2027"),
        ("MANUEL_TSPE_2026_2027", "TSPE_2026_2027"),
        ("MANUEL_1SPE", "1SPE"),
        ("MANUEL_1NSI", "1NSI"),
        ("MANUEL_TNSI", "TNSI"),
    )
    for prefix, manual_id in aliases:
        if stem == prefix or stem.startswith(prefix + "_"):
            return {
                "chapter": None,
                "manual": manual_id,
                "scope": "manual",
                "variant": (
                    stem[len(prefix) + 1 :] if stem.startswith(prefix + "_") else None
                ),
            }
    return {"chapter": None, "manual": None, "scope": None, "variant": None}


def aggregate_artifacts(inventory: dict[str, Any]) -> None:
    manual_variants: dict[tuple[str, str], set[str]] = defaultdict(set)
    chapter_variants: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for artifact in inventory["pdfs"]:
        manual_id = artifact["manual"]
        if manual_id is None or manual_id not in inventory["manuals"]:
            continue
        manual = inventory["manuals"][manual_id]
        manual["compiled_artifacts"].append(dict(artifact))
        scope = artifact["scope"]
        if artifact["variant"] and scope in {"chapter", "manual", "static"}:
            manual_variants[(manual_id, scope)].add(artifact["variant"])
        chapter_id = artifact["chapter"]
        if chapter_id is None or chapter_id not in manual["chapters"]:
            continue
        chapter = manual["chapters"][chapter_id]
        chapter["compiled_artifacts"].append(dict(artifact))
        if artifact["variant"] and scope in {"chapter", "manual", "static"}:
            chapter_variants[(manual_id, chapter_id, scope)].add(artifact["variant"])
    for manual_id, manual in inventory["manuals"].items():
        for scope in ("chapter", "manual", "static"):
            manual["compiled_variants"][scope] = sorted(
                manual_variants[(manual_id, scope)]
            )
        for chapter_id, chapter in manual["chapters"].items():
            for scope in ("chapter", "manual", "static"):
                chapter["compiled_variants"][scope] = sorted(
                    chapter_variants[(manual_id, chapter_id, scope)]
                )


def inventory_pdfs(
    root: Path,
    tracked: tuple[str, ...],
    inventory: dict[str, Any],
    *,
    pdfinfo_counter: Callable[[Path], tuple[int | None, str | None]],
    python_counter: Callable[[Path], tuple[int | None, str | None]],
) -> list[dict[str, Any]]:
    """Attribute and count every tracked PDF with bounded fallbacks."""

    artifacts: list[dict[str, Any]] = []
    for path in (path for path in tracked if path.lower().endswith(".pdf")):
        attribution = attribute_pdf(path, inventory)
        base = {
            "chapter": attribution["chapter"],
            "manual": attribution["manual"],
            "path": path,
            "scope": attribution["scope"],
            "variant": attribution["variant"],
        }
        if attribution["manual"] is None:
            inventory["anomalies"]["unattributed_pdfs"].append(
                {
                    "champ": "attribution",
                    "cible": path,
                    "raison": "PDF suivi sans attribution fiable a un livrable",
                    "source": path,
                }
            )
        if not (root / path).is_file():
            artifacts.append(
                base
                | {
                    "page_count": None,
                    "page_count_method": None,
                    "reason": "fichier PDF suivi absent du checkout",
                    "status": "page_count_unavailable",
                }
            )
            continue
        count, pdfinfo_reason = pdfinfo_counter(root / path)
        if count is not None:
            artifacts.append(
                base
                | {
                    "page_count": count,
                    "page_count_method": "pdfinfo",
                    "reason": None,
                    "status": "counted",
                }
            )
            continue
        count, python_reason = python_counter(root / path)
        if count is not None:
            artifacts.append(
                base
                | {
                    "page_count": count,
                    "page_count_method": "python",
                    "reason": None,
                    "status": "counted",
                }
            )
            continue
        reasons = [reason for reason in (pdfinfo_reason, python_reason) if reason]
        artifacts.append(
            base
            | {
                "page_count": None,
                "page_count_method": None,
                "reason": "; ".join(reasons) or "aucun lecteur PDF disponible",
                "status": "page_count_unavailable",
            }
        )
    return artifacts
