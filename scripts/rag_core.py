"""Shared RAG logic: env resolution, frontmatter, chunking, slug, PII guard, metadata.

Both rag_ingest.py (local Chroma) and rag_ingest_server.py (REST+ollama)
import this module. They differ ONLY by backend.
smoke_test and substance_judge import resolve_env_file for config resolution.
"""
from __future__ import annotations

import hashlib
import os
import re
import unicodedata
from pathlib import Path
from typing import Any


def resolve_env_file(repo_root: Path) -> Path:
    """Canonical .env.rag resolution, shared by smoke test and substance judge.

    Honors RAG_ENV_FILE env override, defaults to repo_root/.env.rag.
    Both consumers MUST use this function so they cannot diverge.
    """
    default = repo_root / ".env.rag"
    return Path(os.getenv("RAG_ENV_FILE", str(default)))


def github_slug(title: str) -> str:
    """Unicode-safe slug matching check_substance_anchors.github_slug.

    Preserves accented characters: "À savoir" -> "à-savoir".
    """
    s = unicodedata.normalize("NFC", title).strip().lower().replace("`", "")
    kept = [ch for ch in s if ch.isalnum() or ch in (" ", "-", "_")]
    return "".join(kept).replace(" ", "-")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    import yaml
    try:
        meta = yaml.safe_load(text[3:end]) or {}
    except Exception:
        meta = {}
    return (meta if isinstance(meta, dict) else {}), text[end + 4:].strip()


def split_sections(body: str) -> list[tuple[str, str]]:
    """Split body into (section_anchor, text) at ## / ### boundaries."""
    sections: list[tuple[str, str]] = []
    anchor = ""
    lines: list[str] = []
    for line in body.split("\n"):
        m = re.match(r"^(#{1,4})\s+(.+)", line)
        if m:
            if lines:
                t = "\n".join(lines).strip()
                if t:
                    sections.append((anchor, t))
            anchor = github_slug(m.group(2).strip())
            lines = [line]
        else:
            lines.append(line)
    if lines:
        t = "\n".join(lines).strip()
        if t:
            sections.append((anchor, t))
    return sections


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_has_pii(path: Path, text: str, root: Path) -> bool:
    """Return True if the file triggers a hard privacy alert."""
    from scripts.check_no_private_data import (
        EMAIL_RE, FR_PHONE_RE, TN_PHONE_RE, ADDRESS_RE,
        ISO_DATE_RE, YEAR_RANGE_RE,
        is_hex_hash_context, is_population_context,
        load_allowlist, allowed,
    )
    allowlist = load_allowlist()
    for regex in [EMAIL_RE, FR_PHONE_RE, TN_PHONE_RE, ADDRESS_RE]:
        for match in regex.finditer(text):
            value = match.group(0)
            if regex in (FR_PHONE_RE, TN_PHONE_RE):
                if ISO_DATE_RE.fullmatch(value) or YEAR_RANGE_RE.fullmatch(value):
                    continue
                if is_population_context(text, match.start(), match.end()):
                    continue
                if is_hex_hash_context(text, match.start(), match.end()):
                    continue
            try:
                rel = str(path.relative_to(root))
            except ValueError:
                rel = str(path)
            if not allowed(value, allowlist) and not allowed(rel, allowlist):
                return True
    return False


def extract_metadata(
    path: Path,
    root: Path,
    collection: str = "nsi_corpus",
    source_type: str = "nsi_corpus",
) -> tuple[list[dict[str, Any]], bool]:
    """Build chunks from a source file.

    Returns (chunks, skipped_pii). Each chunk has 'id', 'text', 'metadata'.
    source_type is a KIND enum {nsi_corpus, golden_example, excluded},
    orthogonal to collection (the physical Chroma collection name).
    """
    VALID_SOURCE_TYPES = {"nsi_corpus", "golden_example", "excluded"}
    if source_type not in VALID_SOURCE_TYPES:
        raise ValueError(f"source_type={source_type!r} not in {VALID_SOURCE_TYPES}")
    text = path.read_text(encoding="utf-8", errors="replace")

    # PII guard
    if file_has_pii(path, text, root):
        return [], True

    meta, body = parse_frontmatter(text)
    if meta.get("private_data") is True:
        return [], True

    rel = path.relative_to(root).as_posix()
    fhash = sha256_file(path)

    # Frontmatter priority, path fallback for code files
    level = str(meta.get("level", ""))
    if not level:
        level = "premiere" if "premiere" in rel else ("terminale" if "terminale" in rel else "")
    theme = str(meta.get("theme", ""))
    notion = str(meta.get("notion", ""))
    seq_id = str(meta.get("sequence_id", ""))
    if not seq_id:
        sm = re.search(r"[PT]\d{2}", rel)
        if sm:
            seq_id = sm.group(0)

    # capacity_ids from official_program.capacities
    official = meta.get("official_program")
    raw_caps: Any = (
        official.get("capacities", []) if isinstance(official, dict)
        else meta.get("capacity_ids") or meta.get("capacities") or []
    )
    if isinstance(raw_caps, str):
        caps = [c.strip() for c in raw_caps.split(",") if c.strip()]
    elif isinstance(raw_caps, list):
        caps = [str(c) for c in raw_caps]
    else:
        caps = []
    caps_csv = ",".join(caps)

    sections = split_sections(body) or [("", body)]
    chunks: list[dict[str, Any]] = []
    for idx, (anch, txt) in enumerate(sections):
        chunks.append({
            "id": f"{rel}#{anch or 'chunk'}-{idx}",
            "text": txt,
            "metadata": {
                "path": rel, "section_anchor": anch, "capacity_ids": caps_csv,
                "document_type": str(meta.get("document_type", path.suffix.lstrip("."))),
                "status": str(meta.get("status") or "needs_review"),
                "level": level, "theme": theme, "notion": notion,
                "sequence_id": seq_id, "sha256": fhash,
                "collection": collection, "source_type": source_type,
                "private_data": False,
            },
        })
    return chunks, False


def adapt_metadata(raw: dict[str, Any]) -> dict[str, Any]:
    """Convert stored scalar metadata back to canonical types.

    Chroma stores capacity_ids as CSV string; the adapter returns a list.
    """
    out = dict(raw)
    csv_val = out.get("capacity_ids", "")
    if isinstance(csv_val, str):
        out["capacity_ids"] = [c for c in csv_val.split(",") if c] if csv_val else []
    return out


EXCLUSIONS = {".git", ".venv", "__pycache__", "dist", "AUDIT", "Documents_DRIVE"}
EXCLUDED_FILES = {"NotesEleves.csv", "Fichier_Eleves.csv"}


def iter_source_files(root: Path) -> list[Path]:
    source_dirs = [
        root / "03_progressions" / "supports",
        root / "03_progressions" / "fiches_cours",
    ]
    files: list[Path] = []
    for d in source_dirs:
        if d.exists():
            for p in sorted(d.rglob("*")):
                if p.is_file() and p.suffix in {".md", ".py"}:
                    if not any(part in EXCLUSIONS for part in p.parts):
                        if p.name not in EXCLUDED_FILES:
                            files.append(p)
    return files
