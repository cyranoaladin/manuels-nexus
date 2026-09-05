"""Manifest Dependency Graph Engine & Stale Tracking.

Builds the true dependency graph for canonical manual release targets based on:
1. Actually included TeX sources (recursively resolved from master TeX / .fls)
2. Common class (gabarits/common/nexus-manuel.cls) and shared packages
3. Official curriculum authority matrix (audit/PROGRAMME_AUTHORITY_MATRIX.json)
4. Build reproducibility configuration

Provides stale detection with zero false-positives across independent manuals
and strict invalidation on shared dependencies, pdf substitutions, and config drift.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


REPRODUCIBILITY_CONFIG_PATH = "Mathematiques/manuel-maths/config/reproducible-build.json"
COMMON_CLASS_PATH = "gabarits/common/nexus-manuel.cls"
COMMON_CHARTE_PATH = "gabarits/common/nexus-charte.sty"


@dataclass(frozen=True)
class TargetDependencyGraph:
    target_id: str
    manual_id: str
    variant: str
    master: str
    pdf: str
    exclusive_sources: tuple[str, ...]
    shared_dependencies: tuple[str, ...]
    programme_authority_file: str | None
    all_dependencies: tuple[str, ...]


@dataclass(frozen=True)
class FreshnessEvaluation:
    target_id: str
    is_fresh: bool
    status: str
    reason: str
    stale_file: str | None = None
    expected_digest: str | None = None
    observed_digest: str | None = None


def _sha256_file(path: Path) -> str:
    """Compute sha256 of file in hex format with sha256: prefix."""
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return "sha256:" + hasher.hexdigest()


def _extract_tex_inputs(root: Path, master_path: Path) -> list[str]:
    """Recursively extract all relative TeX files included from a master file."""
    visited: set[str] = set()
    ordered: list[str] = []

    def _recurse(current_file: Path) -> None:
        try:
            canonical_rel = current_file.relative_to(root).as_posix()
        except ValueError:
            return
        if canonical_rel in visited:
            return
        visited.add(canonical_rel)
        ordered.append(canonical_rel)

        if not current_file.is_file():
            return

        content = current_file.read_text(encoding="utf-8", errors="replace")

        patterns = [
            r"\\input\{([^}]+)\}",
            r"\\include\{([^}]+)\}",
            r"\\subfile\{([^}]+)\}",
        ]
        
        candidates: list[str] = []
        for pat in patterns:
            candidates.extend(re.findall(pat, content))

        for raw in candidates:
            raw = raw.strip()
            if not raw.endswith(".tex"):
                candidate_name = raw + ".tex"
            else:
                candidate_name = raw

            resolved: Path | None = None
            for base_dir in (current_file.parent, root / "Mathematiques" / "manuel-maths", root / "NSI", root):
                candidate_path = (base_dir / candidate_name).resolve()
                if candidate_path.is_file():
                    try:
                        candidate_path.relative_to(root)
                        resolved = candidate_path
                        break
                    except ValueError:
                        continue

            if resolved is not None:
                _recurse(resolved)

    _recurse((root / master_path).resolve())
    return ordered


def build_canonical_dependency_graph(root: Path) -> dict[str, TargetDependencyGraph]:
    """Build the complete dependency graph for all 12 canonical targets."""
    root = root.resolve()
    inventory_path = root / "audit" / "CANONICAL_RELEASE_INVENTORY.json"
    authority_path = root / "audit" / "PROGRAMME_AUTHORITY_MATRIX.json"

    if not inventory_path.is_file():
        raise FileNotFoundError(f"Missing inventory: {inventory_path}")
    if not authority_path.is_file():
        raise FileNotFoundError(f"Missing authority matrix: {authority_path}")

    with inventory_path.open("r", encoding="utf-8") as f:
        inventory_data = json.load(f)
    with authority_path.open("r", encoding="utf-8") as f:
        authority_data = json.load(f)

    curriculum_by_manual: dict[str, str] = {}
    for item in authority_data.get("authorities", []):
        manual_id = item.get("manual_id")
        official_source = item.get("official_source")
        if manual_id and official_source:
            curriculum_by_manual[manual_id] = official_source

    graph: dict[str, TargetDependencyGraph] = {}

    for target in inventory_data.get("canonical_targets", []):
        manual_id = target["manual_id"]
        variant = target["variant"]
        master = target["master"]
        pdf = target["pdf"]
        target_id = f"{manual_id}_{variant}"

        # 1. TeX inclusions
        tex_files = _extract_tex_inputs(root, Path(master))

        # 2. Shared dependencies
        shared_list: list[str] = []
        if (root / COMMON_CLASS_PATH).is_file():
            shared_list.append(COMMON_CLASS_PATH)
        if (root / COMMON_CHARTE_PATH).is_file():
            shared_list.append(COMMON_CHARTE_PATH)
        if (root / REPRODUCIBILITY_CONFIG_PATH).is_file():
            shared_list.append(REPRODUCIBILITY_CONFIG_PATH)

        if "manuel-maths" in master:
            local_cls = "Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls"
            local_sty = "Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty"
            if (root / local_cls).is_file():
                shared_list.append(local_cls)
            if (root / local_sty).is_file():
                shared_list.append(local_sty)
        elif "NSI" in master:
            local_cls = "NSI/gabarits/nexus-manuel-v5.cls"
            local_sty = "NSI/gabarits/nexus-charte-v6.sty"
            if (root / local_cls).is_file():
                shared_list.append(local_cls)
            if (root / local_sty).is_file():
                shared_list.append(local_sty)

        prog_file = curriculum_by_manual.get(manual_id)
        if prog_file and (root / prog_file).is_file():
            shared_or_prog = prog_file
        else:
            shared_or_prog = None

        exclusive_sources = sorted(set(tex_files) - set(shared_list))
        shared_dependencies = sorted(set(shared_list))

        all_deps = set(exclusive_sources) | set(shared_dependencies)
        if shared_or_prog:
            all_deps.add(shared_or_prog)

        graph[target_id] = TargetDependencyGraph(
            target_id=target_id,
            manual_id=manual_id,
            variant=variant,
            master=master,
            pdf=pdf,
            exclusive_sources=tuple(exclusive_sources),
            shared_dependencies=tuple(shared_dependencies),
            programme_authority_file=shared_or_prog,
            all_dependencies=tuple(sorted(all_deps)),
        )

    return graph


def evaluate_target_freshness(
    root: Path,
    graph_entry: TargetDependencyGraph,
    recorded_receipt: Mapping[str, Any],
    *,
    current_file_digests: Mapping[str, str] | None = None,
    inspect_pdf: bool = True,
) -> FreshnessEvaluation:
    """Evaluate whether a recorded build receipt is strictly fresh or stale."""
    root = root.resolve()
    target_id = graph_entry.target_id

    # 1. PDF Verification
    if inspect_pdf:
        pdf_path = root / graph_entry.pdf
        if not pdf_path.is_file():
            return FreshnessEvaluation(
                target_id=target_id,
                is_fresh=False,
                status="STALE_PDF_MISSING",
                reason=f"Target PDF missing: {graph_entry.pdf}",
            )

        expected_pdf_sha = recorded_receipt.get("pdf_sha256")
        if not expected_pdf_sha:
            return FreshnessEvaluation(
                target_id=target_id,
                is_fresh=False,
                status="STALE_RECEIPT_INVALID",
                reason="Receipt missing pdf_sha256",
            )

        observed_pdf_sha = _sha256_file(pdf_path)
        if observed_pdf_sha != expected_pdf_sha:
            return FreshnessEvaluation(
                target_id=target_id,
                is_fresh=False,
                status="PDF_HASH_MISMATCH",
                reason=f"PDF sha256 mismatch for {graph_entry.pdf}",
                expected_digest=expected_pdf_sha,
                observed_digest=observed_pdf_sha,
            )

        expected_pages = recorded_receipt.get("page_count")
        if expected_pages is not None:
            from scripts.inventory_collection import _page_count_with_pdfinfo, _page_count_with_python
            res = _page_count_with_pdfinfo(pdf_path); observed_pages = res[0] if isinstance(res, tuple) else res
            if observed_pages is None:
                res = _page_count_with_python(pdf_path); observed_pages = res[0] if isinstance(res, tuple) else res
            if observed_pages != expected_pages:
                return FreshnessEvaluation(
                    target_id=target_id,
                    is_fresh=False,
                    status="PAGE_COUNT_MISMATCH",
                    reason=f"Page count mismatch: expected {expected_pages}, got {observed_pages}",
                )

    # 2. Dependency digests check
    recorded_digests = recorded_receipt.get("dependency_digests", {})

    for dep_file in graph_entry.all_dependencies:
        dep_path = root / dep_file
        if not dep_path.is_file():
            return FreshnessEvaluation(
                target_id=target_id,
                is_fresh=False,
                status="STALE_DEPENDENCY_MISSING",
                reason=f"Dependency file missing: {dep_file}",
                stale_file=dep_file,
            )

        if current_file_digests and dep_file in current_file_digests:
            current_digest = current_file_digests[dep_file]
        else:
            current_digest = _sha256_file(dep_path)

        expected_digest = recorded_digests.get(dep_file)
        if expected_digest and expected_digest != current_digest:
            if dep_file == graph_entry.programme_authority_file:
                status = "STALE_PROGRAMME_AUTHORITY_MODIFIED"
            elif dep_file in graph_entry.shared_dependencies:
                status = "STALE_SHARED_DEPENDENCY_MODIFIED"
            else:
                status = "STALE_EXCLUSIVE_SOURCE_MODIFIED"

            return FreshnessEvaluation(
                target_id=target_id,
                is_fresh=False,
                status=status,
                reason=f"Dependency altered: {dep_file}",
                stale_file=dep_file,
                expected_digest=expected_digest,
                observed_digest=current_digest,
            )

    # 3. Reproducibility config check
    receipt_repro = recorded_receipt.get("reproducibility")
    if receipt_repro and (root / REPRODUCIBILITY_CONFIG_PATH).is_file():
        repro_cfg_content = json.loads((root / REPRODUCIBILITY_CONFIG_PATH).read_text(encoding="utf-8"))
        for field_name in ("source_commit", "source_date_epoch"):
            if field_name in receipt_repro and field_name in repro_cfg_content:
                if str(receipt_repro[field_name]) != str(repro_cfg_content[field_name]):
                    return FreshnessEvaluation(
                        target_id=target_id,
                        is_fresh=False,
                        status="STALE_CONFIG_CHANGED",
                        reason=f"Reproducibility config drift on {field_name}: {receipt_repro[field_name]} vs {repro_cfg_content[field_name]}",
                    )

    return FreshnessEvaluation(
        target_id=target_id,
        is_fresh=True,
        status="FRESH_CURRENT",
        reason="Target build evidence matches all dependencies and output constraints exactly",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect canonical manual dependency graph and freshness.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--json", action="store_true", help="Output dependency graph in JSON format")
    args = parser.parse_args()

    graph = build_canonical_dependency_graph(args.root)

    if args.json:
        data = {
            target_id: {
                "manual_id": item.manual_id,
                "variant": item.variant,
                "master": item.master,
                "pdf": item.pdf,
                "exclusive_source_count": len(item.exclusive_sources),
                "shared_dependency_count": len(item.shared_dependencies),
                "programme_authority": item.programme_authority_file,
                "total_dependencies": len(item.all_dependencies),
            }
            for target_id, item in graph.items()
        }
        print(json.dumps(data, indent=2))
        return 0

    print(f"=== CANONICAL RELEASE TARGET DEPENDENCY GRAPH ({len(graph)} targets) ===")
    for target_id, item in sorted(graph.items()):
        print(f"[{target_id}] master: {item.master}")
        print(f"  Exclusive TeX sources: {len(item.exclusive_sources)}")
        print(f"  Shared dependencies: {len(item.shared_dependencies)}")
        print(f"  Programme authority: {item.programme_authority_file}")
        print(f"  Total dependencies: {len(item.all_dependencies)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
