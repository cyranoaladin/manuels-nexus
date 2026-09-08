"""Bind a machine receipt to its actual current source, never to a filename alone."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


def usable(binding: dict[str, Any]) -> bool:
    return binding.get("state") == "CURRENT_BOUND" and binding.get("method_state") == "CURRENT_TRUSTED"


def _method_state(receipt: dict[str, Any], chapter: Path, root: Path, source: Path) -> str:
    # Load only the local, side-effect-free binding helper, never source code
    # from a textbook or its execution verifier.
    if (chapter.resolve().is_relative_to((root / "NSI/chapitres").resolve())
            or receipt.get("reviewer") == "verify_python.py"):
        helper = Path(__file__).resolve().parents[1] / "NSI/scripts/execution_protocol.py"
        spec = importlib.util.spec_from_file_location("nexus_nsi_receipt_protocol", helper)
        if spec is None or spec.loader is None:
            return "UNTRUSTED_CURRENT_VERIFIER_UNAVAILABLE"
        protocol = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(protocol)
        return protocol.current_evidence(receipt, source, chapter.parent.parent, root)
    if receipt.get("verification_protocol") != "EXECUTED_ASSERTIONS_PER_BLOCK_V1":
        return "UNTRUSTED_VERIFICATION_PROTOCOL"
    verifier = root / "Mathematiques/manuel-maths/scripts/verify_sympy.py"
    if not verifier.is_file():
        return "UNTRUSTED_CURRENT_VERIFIER_UNAVAILABLE"
    actual = "sha256:" + hashlib.sha256(verifier.read_bytes()).hexdigest()
    if receipt.get("verifier_sha256") != actual:
        return "STALE_VERIFIER_DIGEST"
    return "CURRENT_TRUSTED"


def bind(receipt: dict[str, Any], chapter: Path, root: Path) -> dict[str, Any]:
    declared = receipt.get('source_path')
    expected = receipt.get('source_sha256')
    result = {'state': 'UNBOUND', 'declared_source_path': declared,
              'expected_source_sha256': expected}
    # The canonical math and NSI execution writers both use gate=sympy
    # under the shared receipt schema. Similarity is never science evidence.
    if receipt.get('gate') != 'sympy':
        return {**result, 'reason': 'UNSUPPORTED_SCIENTIFIC_GATE'}
    if receipt.get('verdict') not in {'pass', 'fail', 'manual_review'}:
        return {**result, 'reason': 'UNSUPPORTED_SCIENTIFIC_VERDICT'}
    if not isinstance(declared, str) or not declared:
        return {**result, 'reason': 'MISSING_SOURCE_REFERENCE'}
    if not isinstance(expected, str) or not expected:
        return {**result, 'reason': 'MISSING_SOURCE_DIGEST'}
    candidates = {(base / declared).resolve() for base in (root, chapter.parent.parent)}
    candidates = {p for p in candidates if p.is_relative_to(chapter.resolve())}
    present = {p for p in candidates if p.is_file()}
    if len(present) != 1:
        return {**result, 'state': 'STALE', 'reason': 'SOURCE_MISSING_OR_AMBIGUOUS'}
    source = present.pop()
    data = source.read_bytes()
    actual = 'sha256:' + hashlib.sha256(data).hexdigest()
    relative = source.relative_to(root.resolve()) if source.is_relative_to(root.resolve()) else source.relative_to(chapter.parent.parent.resolve())
    result.update(source_path=relative.as_posix(), current_source_sha256=actual,
                  source_path_base="repository" if source.is_relative_to(root.resolve()) else "manual")
    if actual != expected:
        return {**result, 'state': 'STALE', 'reason': 'SOURCE_DIGEST_CHANGED'}
    first = data.decode('utf-8').split('\n', 1)[0]
    try:
        meta = json.loads(first.removeprefix('% META:')) if first.startswith('% META:') else {}
    except json.JSONDecodeError:
        return {**result, 'state': 'STALE', 'reason': 'SOURCE_IDENTITY_UNREADABLE'}
    identity = receipt.get('object_id') or receipt.get('objet_id')
    # Existing generators put either the canonical META id or the source stem
    # into objet_id. Both require the explicit source path AND byte digest.
    if not identity or identity not in {meta.get('id'), source.stem}:
        return {**result, 'state': 'STALE', 'reason': 'SOURCE_IDENTITY_MISMATCH'}
    method = _method_state(receipt, chapter, root, source)
    return {**result, 'state': 'CURRENT_BOUND', 'method_state': method,
            'reason': None if method == 'CURRENT_TRUSTED' else method,
            'canonical_object_id': meta.get('id'), 'receipt_object_id': identity}
