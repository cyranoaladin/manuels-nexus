#!/usr/bin/env python3
"""CLI mince pour rendre un verdict de substance en Markdown et HTML."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.substance_report_renderer import SchemaError, build_report_model, load_verdict, write_report_outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Rendre un rapport visuel de substance")
    parser.add_argument("--verdict", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    parser.add_argument("--out-html", type=Path, required=True)
    args = parser.parse_args()

    verdict_path = args.verdict
    if not verdict_path.exists():
        print(f"verdict introuvable: {verdict_path}", file=sys.stderr)
        return 2
    repo_root = args.repo_root.resolve()
    try:
        verdict = load_verdict(verdict_path)
        model = build_report_model(verdict, repo_root)
        write_report_outputs(model, args.out_md, args.out_html)
    except (OSError, SchemaError, ValueError) as exc:
        print(f"schema_error: {exc}", file=sys.stderr)
        return 2
    print(f"substance_report: wrote {args.out_md} {args.out_html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
