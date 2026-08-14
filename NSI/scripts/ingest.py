"""Ingestion : raw/ -> corpus/ (chunks JSON normalisés Markdown+LaTeX).

Étapes : extraction (pymupdf/trafilatura) -> découpage sémantique par unité
pédagogique -> classification partagée -> métadonnées héritées du registre.
Les formules cassées par l'extraction PDF pourront être traitées par
l'extension locale latex_fallback().
"""
import json
import os
import re
import sys
from pathlib import Path

from jsonschema import validate


def _discover_checkout_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("checkout Git Nexus introuvable depuis __file__")


CHECKOUT_ROOT = _discover_checkout_root()
root_text = str(CHECKOUT_ROOT)
sys.path[:] = [item for item in sys.path if item != root_text]
sys.path.insert(0, root_text)
import nexus_external  # noqa: E402

expected_package = (CHECKOUT_ROOT / "nexus_external").resolve()
loaded_package = Path(nexus_external.__file__).resolve().parent
if loaded_package != expected_package:
    raise RuntimeError("nexus_external chargé hors du checkout courant")

from nexus_external.classification import classify_chunk  # noqa: E402

from common import CORPUS_DIR, RAW_DIR, ROOT, load_registry, write_json  # noqa: E402

CHUNK_SCHEMA = json.loads((ROOT / "schemas" / "chunk.schema.json").read_text(encoding="utf-8"))

# Découpage par unité pédagogique : en-têtes d'exercices/parties, jamais par fenêtre fixe.
SPLIT_PATTERN = re.compile(
    r"(?im)^(?:exercice|exercise|activit[ée]|probl[èe]me|partie|d[ée]finition|"
    r"th[ée]or[èe]me|propri[ée]t[ée]|m[ée]thode|correction|corrig[ée])\b[^\n]*$"
)


def extract_text(path: Path) -> str:
    if path.suffix == ".pdf":
        import fitz  # pymupdf

        with fitz.open(path) as doc:
            return "\n\n".join(page.get_text("text") for page in doc)
    import trafilatura

    html = path.read_text(encoding="utf-8", errors="replace")
    return trafilatura.extract(html, include_formatting=True) or ""


def latex_fallback(text: str) -> str:
    """Point d'extension : détecter les zones mathématiques mal extraites et les
    reconvertir localement en LaTeX. Implémentation différée (LOT 1) : les
    zones suspectes restent inchangées en attendant."""
    return text


def split_chunks(text: str) -> list[str]:
    positions = [m.start() for m in SPLIT_PATTERN.finditer(text)] or [0]
    if positions[0] != 0:
        positions.insert(0, 0)
    positions.append(len(text))
    chunks = [text[a:b].strip() for a, b in zip(positions, positions[1:])]
    return [c for c in chunks if len(c) >= 40]


def classify(chunk: str) -> dict:
    """Classifie un fragment via la passerelle partagée ou son mode local."""

    return classify_chunk(chunk, environ=os.environ)


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
                classification = classify(chunk)
                record = {
                    "chunk_type": classification["chunk_type"],
                    "niveau": classification["niveau"],
                    "theme": classification["theme"],
                    "capacites": classification["capacites"],
                    "difficulte": classification["difficulte"],
                    "source_id": source["id"],
                    "doc_url": entry["url"],
                    "doc_hash": entry["hash"],
                    "content_md": chunk,
                    "usage_policy": source["usage_policy"],
                    "tier": source["tier"],
                }
                validate(record, CHUNK_SCHEMA)
                out = CORPUS_DIR / source["id"] / entry["hash"][:16] / f"chunk-{i:04d}.json"
                write_json(out, record)
                n += 1
    return n


if __name__ == "__main__":
    total = sum(ingest_source(s) for s in load_registry())
    print(f"{total} chunks normalisés -> {CORPUS_DIR}")
