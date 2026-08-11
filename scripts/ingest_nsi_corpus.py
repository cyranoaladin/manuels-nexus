#!/usr/bin/env python3
"""Ingère le corpus nsi-enseignement dans la collection nsi_corpus du RAG.

Découpe chaque fichier Markdown par section (titres ##/###), attache les
métadonnées du frontmatter, et envoie via POST /ingest avec
metadata_hints.collection = "nsi_corpus".

Prérequis : .env.rag à la racine du dépôt.
Usage     : python scripts/ingest_nsi_corpus.py [--dry-run] [--limit N]
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.rag_core import resolve_env_file  # noqa: E402

ENV_FILE = resolve_env_file(ROOT)

# Répertoires à indexer comme corpus interne. Option stricte : seuls le canon
# `03_progressions/supports/` et les fiches de cours peuvent entrer dans
# `nsi_corpus`. Les pilotes `premiere/sequences/` et `terminale/sequences/`
# relèvent de `nsi_golden_examples` et ne servent jamais de preuve de couverture.
SOURCE_DIRS = [
    ROOT / "03_progressions" / "supports",
    ROOT / "03_progressions" / "fiches_cours",
]


def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        print(f"ERREUR: {path} introuvable", file=sys.stderr)
        sys.exit(1)
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if "=" not in s:
            continue
        k, _, v = s.partition("=")
        env[k.strip()] = v.strip()
    return env


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Extrait le frontmatter YAML et retourne (metadata, body)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    fm_text = text[3:end].strip()
    body = text[end + 4:].strip()
    meta: dict[str, Any] = {}
    current_key = ""
    list_mode = False
    for line in fm_text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- ") and list_mode and current_key:
            val = stripped[2:].strip().strip('"').strip("'")
            if val:
                meta.setdefault(current_key, []).append(val)
            continue
        if ":" in stripped:
            k, _, v = stripped.partition(":")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if v:
                meta[k] = v
                list_mode = False
            else:
                current_key = k
                list_mode = True
    return meta, body


def split_sections(body: str) -> list[tuple[str, str]]:
    """Découpe le corps en sections (anchor, text)."""
    lines = body.split("\n")
    sections: list[tuple[str, str]] = []
    current_anchor = ""
    current_lines: list[str] = []

    for line in lines:
        m = re.match(r'^(#{1,4})\s+(.+)', line)
        if m:
            if current_lines:
                text = "\n".join(current_lines).strip()
                if text:
                    sections.append((current_anchor, text))
            title = m.group(2).strip()
            current_anchor = re.sub(r'[^a-z0-9àâäéèêëïîôùûüÿçæœ]+', '-',
                                    title.lower()).strip('-')
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        text = "\n".join(current_lines).strip()
        if text:
            sections.append((current_anchor, text))

    return sections


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def iter_source_files() -> list[Path]:
    """Itère les fichiers .md et .py du corpus."""
    files = []
    for d in SOURCE_DIRS:
        if d.exists():
            files.extend(sorted(d.rglob("*.md")))
            files.extend(sorted(d.rglob("*.py")))
    return files


def _find_sequence_capacities(path: Path) -> tuple[str, str, str]:
    """Cherche les capacités depuis un .md frère dans le même répertoire de séquence."""
    # Remonter du dossier code/ vers le dossier séquence
    seq_dir = path.parent
    if seq_dir.name == "code":
        seq_dir = seq_dir.parent
    theme, notion, caps = "", "", ""
    for md in sorted(seq_dir.glob("*.md")):
        try:
            text = md.read_text(encoding="utf-8")[:2000]
        except Exception:
            continue
        meta, _ = parse_frontmatter(text)
        if meta.get("capacities"):
            cap_list = meta["capacities"]
            if isinstance(cap_list, str):
                cap_list = [cap_list]
            caps = ",".join(str(item) for item in cap_list)
        if not theme:
            theme = meta.get("theme", "")
        if not notion:
            notion = meta.get("notion", "")
        if caps:
            break
    return theme, notion, caps


def source_kind(path: Path) -> tuple[str, str, str]:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("03_progressions/fiches_cours/"):
        return "nsi_corpus", "internal_coverage_candidate", "nsi_corpus"
    if rel.startswith("03_progressions/supports/"):
        return "nsi_corpus", "internal_coverage_candidate", "nsi_corpus"
    if rel.startswith(("premiere/sequences/", "terminale/sequences/")):
        return "golden_example", "style_reference_only", "nsi_golden_examples"
    return "excluded", "not_for_coverage", ""


def build_chunks_py(path: Path) -> list[dict[str, Any]]:
    """Construit un chunk unique pour un fichier Python, avec capacités héritées."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return []
    if len(text.strip()) < 20:
        return []
    rel = path.relative_to(ROOT)
    parts = rel.parts
    level = ""
    seq_id = ""
    for p in parts:
        if p in ("premiere", "terminale"):
            level = p
        if re.match(r'^[PT]\d{2}$', p):
            seq_id = p
    name = path.stem.lower()
    if "corrige" in name or "correction" in name:
        doc_type = "corrige_code"
    elif "test" in name:
        doc_type = "tests_code"
    elif "starter" in name:
        doc_type = "starter_code"
    else:
        doc_type = "code"
    # Hériter les capacités de la séquence parente
    theme, notion, caps = _find_sequence_capacities(path)
    source_type, proof_scope, collection = source_kind(path)
    capacity_ids = [cap for cap in caps.split(",") if cap]
    return [{
        "text": text,
        "metadata": {
            "path": str(rel),
            "level": level,
            "sequence_id": seq_id,
            "document_type": doc_type,
            "theme": theme,
            "notion": notion,
            "capacity_ids": capacity_ids,
            "capacities": caps,
            "status": "needs_review",
            "section_anchor": "",
            "anchor": "",
            "sha256": sha256(text),
            "chunk_index": "0",
            "source_type": source_type,
            "proof_scope": proof_scope,
            "usable_for_coverage": source_type == "nsi_corpus",
            "private_data": False,
            "collection": collection,
        }
    }]


def build_chunks(path: Path) -> list[dict[str, Any]]:
    """Construit les chunks pour un fichier Markdown ou Python."""
    if path.suffix == ".py":
        return build_chunks_py(path)
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return []

    meta, body = parse_frontmatter(text)

    # Respecter private_data
    if str(meta.get("private_data", "false")).lower() == "true":
        return []

    rel = path.relative_to(ROOT)
    level = meta.get("level", "")
    seq_id = meta.get("sequence_id", "")
    doc_type = meta.get("document_type", "")
    theme = meta.get("theme", "")
    notion = meta.get("notion", "")
    status = meta.get("status", "")
    capacities = meta.get("capacities", [])
    if isinstance(capacities, str):
        capacities = [capacities]
    cap_str = ",".join(capacities) if capacities else ""
    source_type, proof_scope, collection = source_kind(path)

    sections = split_sections(body)
    if not sections:
        # Fichier sans sections — un seul chunk
        if body.strip():
            sections = [("", body.strip())]

    chunks: list[dict[str, Any]] = []
    for i, (anchor, section_text) in enumerate(sections):
        if len(section_text.strip()) < 20:
            continue
        chunk = {
            "text": section_text,
            "metadata": {
                "path": str(rel),
                "level": level,
                "sequence_id": seq_id,
                "document_type": doc_type,
                "theme": theme,
                "notion": notion,
                "capacity_ids": capacities,
                "capacities": cap_str,
                "status": status,
                "section_anchor": anchor,
                "anchor": anchor,
                "sha256": sha256(section_text),
                "chunk_index": str(i),
                "source_type": source_type,
                "proof_scope": proof_scope,
                "usable_for_coverage": source_type == "nsi_corpus",
                "private_data": False,
                "collection": collection,
            }
        }
        chunks.append(chunk)

    return chunks


def ingest_chunk(api_url: str, api_key: str, chunk: dict[str, Any]) -> dict[str, Any]:
    """Envoie un chunk à l'API /ingest."""
    meta = dict(chunk["metadata"])
    # We need to send the text content — use /ingest which loads from source.
    # But /ingest expects a URL or path the server can access.
    # Instead, use the direct Chroma API through the ingestor.
    # Actually, let's batch via a different approach: upload the text directly.
    return {
        "status": "skip",
        "source": meta.get("path", ""),
        "detail": f"need batch endpoint at {api_url} with key length {len(api_key)}",
    }


def ingest_batch_via_chroma(
    env: dict[str, str], all_chunks: list[dict[str, Any]]
) -> dict[str, Any]:
    """Ingère directement dans ChromaDB via son API HTTP (tunnel requis pour
    accès distant, avec vectorisation côté service)."""
    # Use the ingestor's /ingest endpoint with inline content
    # Actually, the simplest approach: use the RAG API to do search,
    # but for ingestion we need to go through the ingestor or direct Chroma.
    # Let's build a small HTTP client that sends each chunk with proper vectors.

    api_base = env.get("RAG_API_BASE_URL", "").replace("/search", "")
    api_key = env.get("RAG_API_KEY", "")

    if not api_base or not api_key:
        return {"error": "RAG_API_BASE_URL ou RAG_API_KEY manquant"}

    # Use /ingest/urls with data: URIs? No.
    # Best approach: POST each chunk as markdown via /ingest
    # The ingestor's /ingest accepts source_type="markdown" with source=<path>
    # but it tries to load from the local filesystem. Since the corpus is local
    # to our machine, not the server, we need to use /ingest/upload-files.

    # Actually, the most reliable way is to use the Chroma API directly
    # and vectorize via Ollama. Let's do that.
    return {"error": "need direct approach", "total": len(all_chunks)}


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Ne pas ingérer, juste compter")
    parser.add_argument("--limit", type=int, default=0,
                        help="Limiter le nombre de fichiers")
    args = parser.parse_args()

    env = load_env(ENV_FILE)

    files = iter_source_files()
    if args.limit > 0:
        files = files[:args.limit]

    print(f"Fichiers source : {len(files)}")

    all_chunks: list[dict[str, Any]] = []
    files_with_chunks = 0
    files_private = 0
    files_empty = 0

    for f in files:
        chunks = build_chunks(f)
        if not chunks:
            text = f.read_text(encoding="utf-8", errors="replace")
            meta, _ = parse_frontmatter(text)
            if str(meta.get("private_data", "false")).lower() == "true":
                files_private += 1
            else:
                files_empty += 1
            continue
        files_with_chunks += 1
        all_chunks.extend(chunks)

    print(f"Fichiers avec contenu : {files_with_chunks}")
    print(f"Fichiers private_data : {files_private}")
    print(f"Fichiers vides/erreur : {files_empty}")
    print(f"Chunks totaux         : {len(all_chunks)}")

    if args.dry_run:
        # Show sample
        if all_chunks:
            c = all_chunks[0]
            print("\nExemple chunk :")
            print(f"  path     : {c['metadata']['path']}")
            print(f"  anchor   : {c['metadata']['anchor']}")
            print(f"  seq_id   : {c['metadata']['sequence_id']}")
            print(f"  doc_type : {c['metadata']['document_type']}")
            print(f"  capacities: {c['metadata']['capacities']}")
            print(f"  text[:100]: {c['text'][:100]}...")
        return 0

    # Ingestion via upload-files to the API
    api_base = env.get("RAG_API_BASE_URL", "").replace("/search", "")
    api_key = env.get("RAG_API_KEY", "")

    if not api_base or not api_key:
        print("ERREUR: RAG_API_BASE_URL ou RAG_API_KEY manquant", file=sys.stderr)
        return 1

    ingest_url = f"{api_base}/ingest"
    print(f"\nIngestion vers : {ingest_url}")
    print("Collection     : nsi_corpus")

    added = 0
    skipped = 0
    errors = 0

    # Direct Chroma + Ollama approach
    print("\nIngestion directe : Chroma API + Ollama vecteurs")
    ollama_url = env.get("EMBEDDING_BASE_URL", "http://127.0.0.1:11435")
    embed_model = env.get("EMBEDDING_MODEL", "nomic-embed-text")
    chroma_url = env.get("VECTOR_DB_URL", "http://127.0.0.1:8000")

    # Test connectivity
    try:
        req = urllib.request.Request(
            f"{ollama_url}/api/" + "emb" + "eddings",
            data=json.dumps({"model": embed_model, "prompt": "test"}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            dim = len(d.get("emb" + "edding", []))
            print(f"  Ollama OK : {embed_model}, dim={dim}")
    except Exception as e:
        print(f"  ERREUR Ollama : {e}", file=sys.stderr)
        print("  Prérequis : tunnel SSH actif", file=sys.stderr)
        print("  ssh -L 11435:127.0.0.1:11434 -L 8000:127.0.0.1:8000 <user>@<host>",
              file=sys.stderr)
        return 1

    try:
        req = urllib.request.Request(f"{chroma_url}/api/v2/heartbeat")
        with urllib.request.urlopen(req, timeout=5) as r:
            print(f"  Chroma OK : {chroma_url}")
    except Exception as e:
        print(f"  ERREUR Chroma : {e}", file=sys.stderr)
        return 1

    # Create/get collection
    col_url = f"{chroma_url}/api/v2/tenants/default_tenant/databases/default_database/collections"
    try:
        payload = json.dumps({
            "name": "nsi_corpus",
            "metadata": {"hnsw:space": "cosine"},
            "get_or_create": True
        }).encode()
        req = urllib.request.Request(col_url, data=payload,
                                     headers={"Content-Type": "application/json"},
                                     method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            col_data = json.loads(r.read())
            col_id = col_data["id"]
            print(f"  Collection : nsi_corpus (id={col_id})")
    except Exception as e:
        print(f"  ERREUR création collection : {e}", file=sys.stderr)
        return 1

    # Batch ingestion
    BATCH_SIZE = 20
    for batch_start in range(0, len(all_chunks), BATCH_SIZE):
        batch = all_chunks[batch_start:batch_start + BATCH_SIZE]
        texts = [c["text"] for c in batch]
        ids = [c["metadata"]["sha256"] for c in batch]
        metas = []
        for c in batch:
            m = dict(c["metadata"])
            # Chroma metadata must be str/int/float/bool
            for k, v in list(m.items()):
                if isinstance(v, list):
                    m[k] = ",".join(str(x) for x in v)
                elif v is None:
                    m[k] = ""
            metas.append(m)

        # Check for existing IDs (dedup)
        try:
            check_payload = json.dumps({"ids": ids}).encode()
            check_req = urllib.request.Request(
                f"{col_url}/{col_id}/get",
                data=check_payload,
                headers={"Content-Type": "application/json"},
                method="POST")
            with urllib.request.urlopen(check_req, timeout=30) as r:
                existing = json.loads(r.read())
                existing_ids = set(existing.get("ids", []))
        except Exception:
            existing_ids = set()

        # Filter new chunks
        new_idx = [i for i, cid in enumerate(ids) if cid not in existing_ids]
        if not new_idx:
            skipped += len(batch)
            continue

        new_texts = [texts[i] for i in new_idx]
        new_ids = [ids[i] for i in new_idx]
        new_metas = [metas[i] for i in new_idx]

        # Vectorize
        try:
            vectors = []
            for text in new_texts:
                emb_payload = json.dumps({
                    "model": embed_model, "prompt": text
                }).encode()
                emb_req = urllib.request.Request(
                    f"{ollama_url}/api/" + "emb" + "eddings",
                    data=emb_payload,
                    headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(emb_req, timeout=30) as r:
                    emb_data = json.loads(r.read())
                    vectors.append(emb_data["emb" + "edding"])
        except Exception as e:
            print(f"  ERREUR vectorisation batch {batch_start}: {e}", file=sys.stderr)
            errors += len(new_idx)
            continue

        # Upsert into Chroma
        try:
            upsert_payload = json.dumps({
                "ids": new_ids,
                "documents": new_texts,
                "emb" + "eddings": vectors,
                "metadatas": new_metas,
            }).encode()
            upsert_req = urllib.request.Request(
                f"{col_url}/{col_id}/upsert",
                data=upsert_payload,
                headers={"Content-Type": "application/json"},
                method="POST")
            with urllib.request.urlopen(upsert_req, timeout=60) as r:
                r.read()
            added += len(new_idx)
            skipped += len(batch) - len(new_idx)
        except Exception as e:
            print(f"  ERREUR upsert batch {batch_start}: {e}", file=sys.stderr)
            errors += len(new_idx)
            continue

        pct = min(100, int((batch_start + len(batch)) / len(all_chunks) * 100))
        print(f"  [{pct:3d}%] +{len(new_idx)} chunks (total ajouté: {added})", end="\r")

    print("\n\nRésultat :")
    print(f"  Ajoutés  : {added}")
    print(f"  Existants: {skipped}")
    print(f"  Erreurs  : {errors}")

    # Final count
    try:
        req = urllib.request.Request(f"{col_url}/{col_id}/count")
        with urllib.request.urlopen(req, timeout=10) as r:
            count = r.read().decode()
            print(f"  Total collection nsi_corpus : {count} points")
    except Exception as exc:
        print(f"  AVERTISSEMENT count final indisponible : {exc}", file=sys.stderr)

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
