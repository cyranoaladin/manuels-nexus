"""Utilitaires partagés du pipeline manuel-maths."""
import hashlib
import json
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "raw"
CORPUS_DIR = ROOT / "corpus"
REGISTRY_PATH = ROOT / "sources" / "registry.yaml"

DATABASE_URL = os.getenv("DATABASE_URL", "")
CRAWL_UA = os.getenv("CRAWL_USER_AGENT", "NexusManuelBot/1.0")
CRAWL_DELAY = float(os.getenv("CRAWL_DELAY_SECONDS", "2"))
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1024"))
STORAGE_MODE = os.getenv("MANUEL_STORAGE_MODE", "postgres").lower()


def load_registry(active_only: bool = True) -> list[dict]:
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    sources = data["sources"]
    return [s for s in sources if s.get("active", False)] if active_only else sources


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def db_connect():
    import psycopg
    from pgvector.psycopg import register_vector
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn
