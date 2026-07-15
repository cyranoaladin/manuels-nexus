"""Ingestion : raw/ -> corpus/ (chunks JSON normalisés Markdown+LaTeX).

Étapes : extraction (pymupdf/trafilatura) -> découpage sémantique par unité
pédagogique -> classification LLM (Haiku) -> métadonnées héritées du registre.
Les formules cassées par l'extraction PDF sont reconverties en LaTeX par
fallback vision (Claude) — voir latex_fallback().
"""
import json
import re
from pathlib import Path

import fitz  # pymupdf
import trafilatura
from jsonschema import validate

from common import CORPUS_DIR, RAW_DIR, ROOT, load_registry, write_json

CHUNK_SCHEMA = json.loads((ROOT / "schemas" / "chunk.schema.json").read_text(encoding="utf-8"))

# Découpage par unité pédagogique : en-têtes d'exercices/parties, jamais par fenêtre fixe.
SPLIT_PATTERN = re.compile(
    r"(?im)^(?:exercice|exercise|activit[ée]|probl[èe]me|partie|d[ée]finition|"
    r"th[ée]or[èe]me|propri[ée]t[ée]|m[ée]thode|correction|corrig[ée])\b[^\n]*$"
)


def extract_text(path: Path) -> str:
    if path.suffix == ".pdf":
        with fitz.open(path) as doc:
            return "\n\n".join(page.get_text("text") for page in doc)
    html = path.read_text(encoding="utf-8", errors="replace")
    return trafilatura.extract(html, include_formatting=True) or ""


def latex_fallback(text: str) -> str:
    """Point d'extension : détecter les zones mathématiques mal extraites et les
    reconvertir en LaTeX via un appel vision Claude sur l'image de la zone PDF.
    Implémentation différée (LOT 1) — marquer les zones suspectes en attendant."""
    return text


def split_chunks(text: str) -> list[str]:
    positions = [m.start() for m in SPLIT_PATTERN.finditer(text)] or [0]
    if positions[0] != 0:
        positions.insert(0, 0)
    positions.append(len(text))
    chunks = [text[a:b].strip() for a, b in zip(positions, positions[1:])]
    return [c for c in chunks if len(c) >= 40]


def classify(chunk: str) -> dict:
    """Classification LLM (Haiku) : type, niveau, thème, capacités probables, difficulté.
    Sans clé API, heuristique lexicale de repli."""
    import os
    if not os.getenv("ANTHROPIC_API_KEY"):
        low = chunk.lower()
        ctype = ("exercice" if low.startswith(("exercice", "probl")) else
                 "corrige" if low.startswith(("correction", "corrig")) else
                 "methode" if low.startswith("méthode") else
                 "cours" if low.startswith(("définition", "théorème", "propriété")) else
                 "activite" if low.startswith("activit") else "autre")
        return {"chunk_type": ctype, "niveau": None, "theme": None,
                "capacites": [], "difficulte": None}
    from anthropic import Anthropic
    client = Anthropic()
    prompt = (
        "Classe ce fragment de ressource de mathématiques (lycée français). "
        "Réponds UNIQUEMENT en JSON: {\"chunk_type\": cours|methode|exercice|corrige|activite|"
        "evaluation|erreur_type|autre, \"niveau\": 2GT|1SPE|TSPE|TEXP|null, "
        "\"theme\": mot-clé majuscule ou null, \"capacites\": [], \"difficulte\": 1|2|3|null}\n\n"
        f"FRAGMENT:\n{chunk[:3000]}"
    )
    msg = client.messages.create(model="claude-haiku-4-5-20251001", max_tokens=200,
                                 messages=[{"role": "user", "content": prompt}])
    raw = msg.content[0].text.strip().removeprefix("```json").removesuffix("```").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"chunk_type": "autre", "niveau": None, "theme": None,
                "capacites": [], "difficulte": None}


def ingest_source(source: dict) -> int:
    n = 0
    src_dir = RAW_DIR / source["id"]
    if not src_dir.exists():
        return 0
    for manifest_path in src_dir.rglob("manifest.json"):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for entry in manifest:
            fpath = manifest_path.parent / entry["file"]
            text = latex_fallback(extract_text(fpath))
            for i, chunk in enumerate(split_chunks(text)):
                meta = classify(chunk)
                record = {
                    "source_id": source["id"], "doc_url": entry["url"],
                    "doc_hash": entry["hash"], "content_md": chunk,
                    "usage_policy": source["usage_policy"], "tier": source["tier"],
                    **meta,
                }
                validate(record, CHUNK_SCHEMA)
                out = CORPUS_DIR / source["id"] / entry["hash"][:16] / f"chunk-{i:04d}.json"
                write_json(out, record)
                n += 1
    return n


if __name__ == "__main__":
    total = sum(ingest_source(s) for s in load_registry())
    print(f"{total} chunks normalisés -> {CORPUS_DIR}")
