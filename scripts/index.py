"""Indexation : corpus/ -> PostgreSQL/pgvector (embeddings + tsvector auto)."""
import json

from common import CORPUS_DIR, db_connect

BATCH = 64


def embed(texts: list[str]):
    from FlagEmbedding import BGEM3FlagModel
    model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)
    return model.encode(texts, batch_size=BATCH)["dense_vecs"]


def main() -> None:
    records = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(CORPUS_DIR.rglob("chunk-*.json"))]
    if not records:
        print("Corpus vide : lancer ingest d'abord.")
        return
    vectors = embed([r["content_md"] for r in records])
    with db_connect() as conn, conn.cursor() as cur:
        for rec, vec in zip(records, vectors):
            cur.execute(
                """INSERT INTO chunks (source_id, doc_url, doc_hash, chunk_type, niveau, theme,
                       capacites, difficulte, usage_policy, tier, content_md, embedding)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (rec["source_id"], rec["doc_url"], rec["doc_hash"], rec["chunk_type"],
                 rec.get("niveau"), rec.get("theme"), rec.get("capacites", []),
                 rec.get("difficulte"), rec["usage_policy"], rec["tier"],
                 rec["content_md"], vec))
        conn.commit()
    print(f"{len(records)} chunks indexés.")


if __name__ == "__main__":
    main()
