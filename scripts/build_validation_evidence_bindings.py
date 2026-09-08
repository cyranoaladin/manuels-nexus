#!/usr/bin/env python3
"""Forensic source binding of chapter validation JSON, including historical receipts.

This reports evidence provenance; a binding is not a scientific or human approval.
The optional snapshot is read through Git, never checked out or restored.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path
import subprocess
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORPORA = ('Mathematiques/manuel-maths/chapitres', 'NSI/chapitres')
RETIREMENT_COMMIT = 'b4e3998a1'
REMOVED_RECEIPTS_COMMIT = '0c7a470fc'


def sha(data: bytes) -> str:
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def git(root: Path, *args) -> bytes:
    return subprocess.check_output(['git', *args], cwd=root)


def source_meta(data: bytes) -> dict[str, Any]:
    first = data.decode('utf-8').split('\n', 1)[0]
    return json.loads(first[len('% META:'):]) if first.startswith('% META:') else {}


def snapshot_files(root: Path, snapshot: str | None):
    if snapshot:
        names = git(root, 'ls-tree', '-r', '-z', '--name-only', snapshot, '--', *CORPORA).decode().split('\0')
    else:
        names = [p.relative_to(root).as_posix() for corpus in CORPORA
                 for p in (root / corpus).rglob('*') if p.is_file()]
    names = sorted(p for p in names if p and (
        p.endswith('.tex') or '/validations/' in p and p.endswith('.json')
        or Path(p).name in {'contrat.yaml', 'dossier_curation.json'}))
    if not snapshot:
        return {p: (root / p).read_bytes() for p in names}
    request = ''.join(f'{snapshot}:{p}\n' for p in names).encode()
    stream = io.BytesIO(subprocess.run(['git', 'cat-file', '--batch'], cwd=root,
                                     input=request, capture_output=True, check=True).stdout)
    result = {}
    for path in names:
        header = stream.readline().decode().split()
        if len(header) != 3 or header[1] != 'blob':
            raise ValueError(f'historical blob unavailable: {path}')
        result[path] = stream.read(int(header[2]))
        if stream.read(1) != b'\n':
            raise ValueError('invalid git batch separator')
    return result


def historical_sources(root: Path):
    paths = git(root, 'diff-tree', '--no-commit-id', '--name-only', '--diff-filter=D',
                '-r', RETIREMENT_COMMIT, '--', '*/cours/*.tex').decode().splitlines()
    return {path: git(root, 'show', f'{RETIREMENT_COMMIT}^:{path}') for path in paths}


def classify(files: dict[str, bytes], removed: dict[str, bytes]):
    by_id = defaultdict(set)
    by_stem = defaultdict(set)
    for path, data in files.items():
        if not path.endswith('.tex'):
            continue
        chapter = path.split('/chapitres/')[1].split('/')[0]
        meta = source_meta(data)
        if meta.get('id'):
            by_id[(chapter, meta['id'])].add(path)
        by_stem[(chapter, Path(path).stem)].add(path)
    rows = []
    for path in sorted(files):
        if '/validations/' not in path or not path.endswith('.json'):
            continue
        data = files[path]
        record = json.loads(data)
        chapter_dir = path.split('/validations/')[0]
        chapter = chapter_dir.rsplit('/', 1)[1]
        manual = chapter_dir.split('/chapitres/')[0]
        identity = record.get('object_id') or record.get('objet_id')
        expected = record.get('source_sha256')
        declared = record.get('source_path')
        candidates = set()
        binding = 'UNBOUND'
        if declared:
            candidates = {p for p in (declared, manual + '/' + declared)
                          if p in files and p.startswith(chapter_dir + '/')}
            binding = 'EXPLICIT_SOURCE_PATH'
        if not declared and not candidates:
            candidates = by_id[(chapter, identity)]
            binding = 'INTERNAL_CANONICAL_OBJECT_ID'
        if not declared and not candidates:
            # The similarity producers explicitly store source.stem as objet_id.
            candidates = by_stem[(chapter, identity)]
            binding = 'INTERNAL_SOURCE_ID_GENERATOR_CONTRACT'
        if not declared and not candidates and identity == chapter + '-CONTRAT':
            candidates = {chapter_dir + '/contrat.yaml'} & files.keys()
            binding = 'INTERNAL_CONTRACT_ID_AND_REVIEW_SCOPE'
        if not declared and not candidates and identity == chapter + '-CURATION':
            candidates = {chapter_dir + '/dossier_curation.json'} & files.keys()
            binding = 'INTERNAL_CURATION_ID_AND_REVIEW_SCOPE'
        state, reason = 'VALIDATION_UNBOUND', 'NO_UNIQUE_SOURCE_BINDING'
        sources = []
        if len(candidates) == 1:
            source = next(iter(candidates))
            actual = sha(files[source])
            canonical = source_meta(files[source]).get('id') if source.endswith('.tex') else identity
            sources = [{'path': source, 'canonical_object_id': canonical, 'source_sha256': actual}]
            if identity not in {canonical, Path(source).stem}:
                state, reason = 'VALIDATION_STALE', 'SOURCE_IDENTITY_MISMATCH'
            elif expected == actual and declared:
                state, reason = 'VALIDATION_BOUND_CURRENT', 'EXPLICIT_SOURCE_AND_DIGEST_IDENTICAL'
            else:
                state, reason = 'VALIDATION_STALE', ('SOURCE_DIGEST_CHANGED' if expected else 'NO_RECORDED_SOURCE_DIGEST')
        if not candidates and not declared:
            historical = [p for p in removed if p.startswith(chapter_dir + '/')
                          and identity in {source_meta(removed[p]).get('id'), Path(p).stem}]
            if len(historical) == 1:
                source = historical[0]
                state, reason = 'VALIDATION_HISTORICAL', 'SOURCE_REMOVED_AT_DOCUMENTED_COMMIT'
                binding = 'INTERNAL_SOURCE_ID_AND_GIT_REMOVAL_HISTORY'
                sources = [{'path': source, 'canonical_object_id': source_meta(removed[source]).get('id'),
                            'source_sha256': sha(removed[source]), 'historical_commit': RETIREMENT_COMMIT + '^'}]
        rows.append({'path': path, 'receipt_sha256': sha(data), 'object_id': identity,
                     'declared_source_path': declared, 'recorded_source_sha256': expected,
                     'status': state, 'reason': reason, 'binding': binding, 'sources': sources,
                     'verdict': record.get('verdict'), 'current_binding_valid': state == 'VALIDATION_BOUND_CURRENT'})
    return rows


def build(root=ROOT, snapshot=None):
    head = git(root, 'rev-parse', snapshot or 'HEAD').decode().strip()
    files = snapshot_files(root, snapshot)
    rows = classify(files, historical_sources(root))
    counts = Counter(row['status'] for row in rows)
    removed = []
    paths = git(root, 'diff-tree', '--no-commit-id', '--name-only', '--diff-filter=D',
                '-r', REMOVED_RECEIPTS_COMMIT, '--', '*/validations/*.sympy.json').decode().splitlines()
    for path in paths:
        data = git(root, 'show', f'{REMOVED_RECEIPTS_COMMIT}^:{path}')
        record = json.loads(data)
        reused = [r['path'] for r in rows if r['recorded_source_sha256'] == record['source_sha256']]
        removed.append({'path': path, 'historical_commit': REMOVED_RECEIPTS_COMMIT + '^',
                        'receipt_sha256': sha(data), 'object_id': record['objet_id'],
                        'recorded_source_path': record['source_path'],
                        'recorded_source_sha256': record['source_sha256'],
                        'present_in_observed_source_set': path in files,
                        'receipt_evidence_reused_by': reused})
    if not snapshot:
        if git(root, 'rev-parse', 'HEAD').decode().strip() != head or snapshot_files(root, None) != files:
            raise ValueError('source set changed during validation observation')
    status = [] if snapshot else git(root, 'status', '--porcelain=v1', '--untracked-files=all').decode().splitlines()
    return {'artifact_type': 'validation_evidence_binding_forensics', 'schema_version': 1,
            'observation': {'base_head': head, 'worktree_status': status, 'worktree_dirty': bool(status),
                            'scope': 'IMMUTABLE_GIT_SNAPSHOT' if snapshot else ('WORKTREE_BOUND_BY_INPUT_DIGESTS' if status else 'HEAD_BOUND_BY_INPUT_DIGESTS')},
            'observation_head': head, 'observation_mode': 'IMMUTABLE_GIT_SNAPSHOT' if snapshot else 'CURRENT_WORKTREE',
            'approves_nothing': True, 'generated_by': 'scripts/build_validation_evidence_bindings.py',
            'population': 'All chapter validations/*.json, all six manuals; visual PNG excluded.',
            'classification_note': 'A current binding authenticates scope and bytes; it does not turn manual_review into pass or an agent into a human.',
            'source_set_digest': sha(json.dumps({p: sha(b) for p,b in sorted(files.items())}, sort_keys=True).encode()),
            'summary': {'VALIDATION_ARTIFACTS_TOTAL': len(rows),
                        **{s: counts[s] for s in ('VALIDATION_BOUND_CURRENT', 'VALIDATION_HISTORICAL', 'VALIDATION_STALE', 'VALIDATION_UNBOUND')},
                        'ORIGINAL_FOUR_CURRENT_RECEIPTS_REFERENCING_RETIRED_OBJECTS': sum(r['present_in_observed_source_set'] for r in removed),
                        'ORIGINAL_FOUR_HISTORICAL_RECEIPTS_FOR_RETIRED_OBJECTS': len(removed),
                        'RECEIPT_EVIDENCE_REUSED_FOR_REPLACEMENT_CONTENT': sum(bool(r['receipt_evidence_reused_by']) for r in removed)},
            'entries': rows, 'original_four_historical_receipts': removed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = build(snapshot=args.snapshot)
    if args.output:
        args.output.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    print(json.dumps(result['summary'], sort_keys=True))


if __name__ == '__main__':
    main()
