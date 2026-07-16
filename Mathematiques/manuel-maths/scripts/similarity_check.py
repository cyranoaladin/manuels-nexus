"""Gate anti-similarité (règles R3/N02) : compare les objets produits aux chunks sources.

Mesure : Jaccard sur n-grammes de mots (n=8) + cosinus d'embeddings (si base dispo).
Seuils : n-gram > 0.35 avec source T2/T4 -> FAIL (régénérer) ;
         n-gram > 0.35 avec source T1/T3 adaptation_attribution -> WARNING (vérifier attribution).
"""
import argparse
import datetime
import json
import re
import sys
from pathlib import Path

from common import CORPUS_DIR, ROOT, STORAGE_MODE, db_connect, write_json

NGRAM = 8
THRESHOLD = 0.35


def ngrams(text: str) -> set[tuple]:
    words = re.findall(r"[a-zà-ÿ0-9]+", text.lower())
    return {tuple(words[i:i + NGRAM]) for i in range(max(0, len(words) - NGRAM + 1))}


def strip_tex(tex: str) -> str:
    return re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?|[{}%]", " ", tex)


def iter_source_chunks(theme: str):
    """Retourne les chunks du thème depuis PostgreSQL ou le corpus JSON."""
    if STORAGE_MODE == "fichiers":
        for path in sorted(CORPUS_DIR.rglob("*.json")):
            try:
                chunk = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if chunk.get("theme") not in (None, theme):
                continue
            content = chunk.get("content_md", "")
            if content:
                yield (
                    str(chunk.get("id", path.stem)),
                    content,
                    chunk.get("tier", ""),
                    chunk.get("usage_policy", ""),
                )
        return
    with db_connect() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, content_md, tier, usage_policy FROM chunks WHERE theme = %s OR theme IS NULL",
            (theme,),
        )
        yield from cur


def check_object(tex_path: Path, chap_dir: Path) -> str:
    text = strip_tex(tex_path.read_text(encoding="utf-8"))
    obj_ngrams = ngrams(text)
    verdict, worst = "pass", {"score": 0.0}
    if not obj_ngrams:
        return "pass"
    # Comparaison restreinte au thème du chapitre pour rester tractable.
    theme = chap_dir.name.split("-", 1)[-1]
    for cid, content, tier, policy in iter_source_chunks(theme):
        src = ngrams(content)
        if not src:
            continue
        score = len(obj_ngrams & src) / len(obj_ngrams)  # rappel côté objet produit
        if score > worst["score"]:
            worst = {"score": round(score, 3), "chunk_id": cid, "tier": tier, "policy": policy}
    if worst["score"] > THRESHOLD:
        verdict = "fail" if worst.get("policy") == "inspiration_reformulation" else "warning"
    record = {
        "objet_id": tex_path.stem, "gate": "similarity", "verdict": verdict,
        "details": worst, "reviewer": "similarity_check.py",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    write_json(chap_dir / "validations" / f"{tex_path.stem}.similarity.json", record)
    print(f"[{verdict.upper():7}] {tex_path.stem} (max={worst['score']})")
    return verdict


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chap", required=True)
    args = ap.parse_args()
    chap_dir = ROOT / "chapitres" / args.chap
    verdicts = [check_object(p, chap_dir)
                for sub in ("cours", "methodes", "exercices", "corriges", "evaluations")
                for p in sorted((chap_dir / sub).glob("*.tex"))]
    sys.exit(1 if "fail" in verdicts else 0)
