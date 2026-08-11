#!/usr/bin/env python3
"""Check Makefile audit targets against qa_gate_policy.md."""

from __future__ import annotations

import re


from scripts import check_quality_gates
from scripts._qa_common import ROOT, print_result


MAKEFILE = ROOT / "Makefile"
POLICY = ROOT / "qa_gate_policy.md"


def target_body(text: str, target: str) -> str:
    match = re.search(rf"^{re.escape(target)}:.*?\n(.*?)(?=\n[A-Za-z0-9_-]+:|\Z)", text, re.S | re.M)
    return match.group(1) if match else ""


def python_scripts(body: str) -> set[str]:
    scripts: set[str] = set()
    for match in re.finditer(r"(?:^|\s)(?:[A-Z_]+=[^\s]+\s+)*-?python\s+-m\s+(scripts\.\w+)", body):
        scripts.add(match.group(1))
    return scripts


def documented_scripts(policy_text: str) -> set[str]:
    found: set[str] = set()
    for m in re.findall(r"scripts/([A-Za-z0-9_]+)\.py", policy_text):
        found.add(f"scripts.{m}")
    return found


def main() -> None:
    errors: list[str] = []
    text = MAKEFILE.read_text(encoding="utf-8")
    policy = POLICY.read_text(encoding="utf-8")
    # audit must chain at least audit-core and audit-metrics as EXACT prerequisites
    audit_line = re.search(r"^audit:(.+)", text, re.M)
    if audit_line:
        prereqs = audit_line.group(1).split()
        if "audit-core" not in prereqs:
            errors.append("audit: audit-core manquant comme prérequis exact")
        if "audit-metrics" not in prereqs:
            errors.append("audit: audit-metrics manquant comme prérequis exact")
    else:
        errors.append("cible audit absente")
    core = target_body(text, "audit-core")
    metrics = target_body(text, "audit-metrics")
    required = target_body(text, "rag-smoke-required")
    if not core:
        errors.append("cible audit-core absente")
    if not metrics:
        errors.append("cible audit-metrics absente")
    if "RAG_ENV_FILE=.env.rag.audit-core-missing python -m scripts.rag_smoke_test" not in core:
        errors.append("audit-core doit forcer le smoke RAG en mode clone-propre")
    if "python -m scripts.rag_smoke_test" not in required or "RAG_ENV_FILE" in required:
        errors.append("rag-smoke-required doit utiliser .env.rag réel")
    docs = documented_scripts(policy)
    core_set = python_scripts(core)
    # Forward: every gate executed in audit-core must be documented
    for script in sorted(core_set):
        if script not in docs:
            errors.append(f"{script}: gate audit-core non documenté dans qa_gate_policy.md")
    # Reverse: every documented blocking gate must be executed somewhere.
    # Drive-required gates (explicitly listed in the policy) may be in
    # audit-local only, not in audit-core (clone-clean mode).
    audit_local = target_body(text, "audit-local")
    audit_extracted = target_body(text, "audit-extracted-source-local")
    pkg_audit = target_body(text, "package-audit")
    all_executed = core_set | python_scripts(audit_local) | python_scripts(audit_extracted) | python_scripts(pkg_audit)
    # Gates only callable with a Drive mirror — not required in audit-core
    drive_only = {"scripts.drive_local_inventory", "scripts.drive_resource_triage"}
    for script in sorted(docs - drive_only):
        if script not in all_executed:
            errors.append(f"{script}: gate documenté bloquant mais absent des cibles audit")
    if "Divergence documentée check_quality_gates.py / audit-core" not in policy:
        quality_scripts = {" ".join(command) for command in check_quality_gates.CORE_CHECKS}
        core_scripts = python_scripts(core)
        missing_in_quality = {script for script in core_scripts if script not in quality_scripts}
        if missing_in_quality:
            errors.append(f"check_quality_gates.py diverge de audit-core: {sorted(missing_in_quality)}")
    print_result("check_makefile_audit_policy", errors)


if __name__ == "__main__":
    main()
