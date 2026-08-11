#!/usr/bin/env python3
"""Audit de fraîcheur RAG : compare les fichiers du dépôt à la collection Chroma.

Pour chaque .md avec private_data=false, calcule sha256(fichier repo) et le
compare aux métadonnées sha256 de la collection Chroma nsi_corpus_v2.

Requiert le serveur RAG accessible (SSH tunnel). Tourne en --repo-only si
le serveur n'est pas joignable (calcule les hashes repo sans comparaison).

SECRETS : RAG_API_KEY lu depuis .env.rag — jamais affiché.

Usage:
    python -m scripts.check_rag_freshness              # full comparison
    python -m scripts.check_rag_freshness --repo-only  # hashes only, no server
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts._qa_common import ROOT, SUPPORTS_DIR, read_frontmatter  # noqa: E402


def load_env_rag() -> dict[str, str]:
    """Load RAG connection params from .env.rag."""
    env_path = ROOT / ".env.rag"
    env: dict[str, str] = {}
    if not env_path.exists():
        return env
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def sha256_file(path: Path) -> str:
    """Compute sha256 hex digest of a file."""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def collect_repo_files() -> list[dict[str, str]]:
    """Collect all .md files with private_data=false from supports."""
    files = []
    prefix_pattern = re.compile(r"[PT]\d{2}")
    for level_dir in [SUPPORTS_DIR / "premiere", SUPPORTS_DIR / "terminale"]:
        if not level_dir.is_dir():
            continue
        for seq_dir in sorted(level_dir.iterdir()):
            if not seq_dir.is_dir() or not prefix_pattern.fullmatch(seq_dir.name):
                continue
            for md_path in sorted(seq_dir.rglob("*.md")):
                if "contracts" in md_path.parts:
                    continue
                fm = read_frontmatter(md_path)
                if fm.get("private_data") is True:
                    continue
                rel = md_path.relative_to(ROOT).as_posix()
                files.append({
                    "path": rel,
                    "sha256": sha256_file(md_path),
                    "abs_path": str(md_path),
                })
    return files


def query_chroma_hashes(env: dict[str, str]) -> dict[str, str]:
    """Query Chroma collection for all document sha256 hashes.
    Returns {relative_path: sha256}."""
    api_url = env.get("RAG_API_BASE_URL", "")
    api_key = env.get("RAG_API_KEY", "")
    collection = env.get("RAG_COLLECTION", "nsi_corpus_v2")

    if not api_url:
        return {}

    # Try to get all documents metadata
    try:
        body = json.dumps({
            "q": "*",
            "collection": collection,
            "k": 10000,
            "include_documents": False,
        }).encode("utf-8")
        req = urllib.request.Request(
            api_url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        hits = result.get("hits", [])
    except Exception as e:
        print(f"WARNING: Could not query Chroma: {e}", file=sys.stderr)
        return {}

    hashes: dict[str, str] = {}
    for hit in hits:
        meta = hit.get("metadata", {})
        if isinstance(meta, dict):
            path = str(meta.get("path", ""))
            sha = str(meta.get("sha256", ""))
            if path and sha:
                hashes[path] = sha
    return hashes


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit de fraîcheur RAG")
    parser.add_argument("--repo-only", action="store_true",
                        help="Compute repo hashes only, no server comparison")
    args = parser.parse_args()

    repo_files = collect_repo_files()
    print(f"Fichiers repo (private_data≠true): {len(repo_files)}")

    if args.repo_only:
        print("\nMode --repo-only: hashes calculés, pas de comparaison serveur.")
        print(f"  {len(repo_files)} fichiers .md prêts pour comparaison")
        print("  (lancer sans --repo-only quand le tunnel SSH est actif)")
        return 0

    env = load_env_rag()
    if not env.get("RAG_API_BASE_URL"):
        print("ERROR: RAG_API_BASE_URL not found in .env.rag", file=sys.stderr)
        print("  Run with --repo-only for local hashes only", file=sys.stderr)
        return 1

    chroma_hashes = query_chroma_hashes(env)
    if not chroma_hashes:
        print("WARNING: No hashes retrieved from Chroma (server unreachable?)")
        print("  Run with --repo-only for local hashes only")
        return 1

    # Compare
    repo_paths = {f["path"] for f in repo_files}
    chroma_paths = set(chroma_hashes.keys())

    identical = 0
    modified = 0
    absent_from_chroma = 0
    orphan_in_chroma = 0
    modified_list = []
    absent_list = []
    orphan_list = []

    for f in repo_files:
        path = f["path"]
        if path in chroma_hashes:
            if f["sha256"] == chroma_hashes[path]:
                identical += 1
            else:
                modified += 1
                modified_list.append(path)
        else:
            absent_from_chroma += 1
            absent_list.append(path)

    for path in chroma_paths:
        if path not in repo_paths:
            orphan_in_chroma += 1
            orphan_list.append(path)

    print("\n=== Résultat comparaison ===")
    print(f"  Identiques : {identical}")
    print(f"  Modifiés   : {modified}")
    print(f"  Absents de Chroma : {absent_from_chroma}")
    print(f"  Orphelins Chroma  : {orphan_in_chroma}")

    if modified_list:
        print(f"\nFichiers modifiés ({modified}):")
        for p in modified_list[:20]:
            print(f"  - {p}")

    if absent_list:
        print(f"\nAbsents de Chroma ({absent_from_chroma}):")
        for p in absent_list[:20]:
            print(f"  - {p}")

    if orphan_list:
        print(f"\nOrphelins Chroma ({orphan_in_chroma}):")
        for p in orphan_list[:20]:
            print(f"  - {p}")

    print(f"\nCONCLUSION: {modified + absent_from_chroma + orphan_in_chroma} écarts détectés"
          f" sur {len(repo_files)} fichiers repo + {len(chroma_paths)} chunks Chroma.")
    if modified + absent_from_chroma > 0:
        print("  La collection Chroma est en retard par rapport au dépôt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
