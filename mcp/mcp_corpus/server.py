"""MCP corpus : recherche hybride (vecteur + BM25 + rerank) + référentiel capacités.
Lancement : python mcp/mcp_corpus/server.py  (stdio, à déclarer dans .mcp.json)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from common import ROOT, db_connect  # noqa: E402

from fastmcp import FastMCP  # noqa: E402

mcp = FastMCP("mcp-corpus")


@mcp.tool()
def search_corpus(query: str, top_k: int = 10, tiers: list[str] | None = None,
                  chunk_types: list[str] | None = None, niveau: str | None = None,
                  theme: str | None = None) -> list[dict]:
    """Recherche hybride dans le corpus. Retourne les chunks avec métadonnées
    (dont usage_policy, à respecter impérativement en composition)."""
    from FlagEmbedding import BGEM3FlagModel
    vec = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True).encode([query])["dense_vecs"][0]
    where, params = ["TRUE"], []
    if tiers:
        where.append("tier = ANY(%s)"); params.append(tiers)
    if chunk_types:
        where.append("chunk_type = ANY(%s)"); params.append(chunk_types)
    if niveau:
        where.append("niveau = %s"); params.append(niveau)
    if theme:
        where.append("theme = %s"); params.append(theme)
    sql = f"""
      WITH v AS (SELECT id, 1 - (embedding <=> %s::vector) AS s_vec FROM chunks
                 WHERE {' AND '.join(where)} ORDER BY embedding <=> %s::vector LIMIT 50),
           b AS (SELECT id, ts_rank(tsv, plainto_tsquery('french', %s)) AS s_bm25 FROM chunks
                 WHERE {' AND '.join(where)} ORDER BY s_bm25 DESC LIMIT 50)
      SELECT c.id, c.source_id, c.doc_url, c.chunk_type, c.tier, c.usage_policy,
             c.content_md, COALESCE(v.s_vec,0)*0.6 + COALESCE(b.s_bm25,0)*0.4 AS score
      FROM chunks c LEFT JOIN v ON v.id=c.id LEFT JOIN b ON b.id=c.id
      WHERE v.id IS NOT NULL OR b.id IS NOT NULL
      ORDER BY score DESC LIMIT %s"""
    with db_connect() as conn, conn.cursor() as cur:
        cur.execute(sql, [vec, *params, vec, *params, query, *params, top_k * 3])
        rows = cur.fetchall()
    # Rerank CrossEncoder
    from sentence_transformers import CrossEncoder
    ce = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    scored = ce.predict([(query, r[6][:1500]) for r in rows])
    ranked = sorted(zip(rows, scored), key=lambda x: -x[1])[:top_k]
    return [{"chunk_id": r[0], "source_id": r[1], "url": r[2], "type": r[3],
             "tier": r[4], "usage_policy": r[5], "content": r[6],
             "rerank_score": float(s)} for r, s in ranked]


@mcp.tool()
def get_capacites(niveau: str, theme: str | None = None) -> list[dict]:
    """Référentiel officiel des capacités (source de vérité, règle R7)."""
    files = (ROOT / "referentiel").glob(f"capacites_{niveau}_*.json")
    out = []
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        if theme and data["theme"] != theme:
            continue
        out += data["capacites"]
    return out


if __name__ == "__main__":
    mcp.run()
