#!/usr/bin/env python3
"""Check Git repository initialization and clean worktree."""

from __future__ import annotations

from typing import List
import subprocess
import sys

sys.dont_write_bytecode = True

from scripts._qa_common import ROOT, print_result


def run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)


def main() -> None:
    errors: List[str] = []
    inside = run_git(["rev-parse", "--is-inside-work-tree"])
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        errors.append("dépôt Git non initialisé")
        print_result("check_git_clean", errors)
        return

    status = run_git(["status", "--short"])
    if status.returncode != 0:
        errors.append(status.stderr.strip() or "git status impossible")
    elif status.stdout.strip():
        errors.append("worktree non propre:\n" + status.stdout.rstrip())

    log = run_git(["log", "--oneline", "-1"])
    if log.returncode != 0:
        errors.append("aucun commit Git détecté")

    print_result("check_git_clean", errors)


if __name__ == "__main__":
    main()
