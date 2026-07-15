"""Gate anti-similarité (R3/N02) — version NSI : le tier T0 (corpus propriétaire) est
EXEMPTÉ ; seules les sources T2/T4 (inspiration_reformulation) déclenchent un fail.
Mode fichiers natif (aucune dépendance PostgreSQL — leçon du run maths)."""
import argparse
import datetime
import json
import re
import sys
from pathlib import Path

from common import CORPUS_DIR, ROOT, write_json

NGRAM, THRESHOLD = 8, 0.35


def ngrams(text: str) -> set[tuple]:
    words = re.findall(r"[a-zà-ÿ0-9_]+", text.lower())
    return {tuple(words[i:i + NGRAM]) for i in range(max(0, len(words) - NGRAM + 1))}


def strip_tex(tex: str) -> str:
    tex = re.sub(r"\\begin\{(python|console)\}.*?\\end\{\1\}", " ", tex, flags=re.S)  # le code T0 est légitime
    return re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?|[{}%]", " ", tex)


def iter_chunks(theme: str):
    for path in sorted(CORPUS_DIR.rglob("*.json")):
        try:
            c = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if c.get("tier") == "T0":            # exemption propriétaire
            continue
        if c.get("theme") not in (None, theme) or not c.get("content_md"):
            continue
        yield str(c.get("id", path.stem)), c["content_md"], c.get("tier", ""), c.get("usage_policy", "")


def check(tex: Path, chap_dir: Path) -> str:
    obj = ngrams(strip_tex(tex.read_text(encoding="utf-8")))
    verdict, worst = "pass", {"score": 0.0}
    if obj:
        theme = chap_dir.name.split("-", 1)[-1]
        for cid, content, tier, policy in iter_chunks(theme):
            src = ngrams(content)
            if not src:
                continue
            s = len(obj & src) / len(obj)
            if s > worst["score"]:
                worst = {"score": round(s, 3), "chunk_id": cid, "tier": tier, "policy": policy}
        if worst["score"] > THRESHOLD:
            verdict = "fail" if worst.get("policy") == "inspiration_reformulation" else "warning"
    write_json(chap_dir / "validations" / f"{tex.stem}.similarity.json", {
        "objet_id": tex.stem, "gate": "similarity", "verdict": verdict, "details": worst,
        "reviewer": "similarity_check.py",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()})
    print(f"[{verdict.upper():7}] {tex.stem} (max={worst['score']})")
    return verdict


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chap", required=True)
    args = ap.parse_args()
    chap_dir = ROOT / "chapitres" / args.chap
    verdicts = [check(p, chap_dir)
                for sub in ("cours", "methodes", "exercices", "corriges", "evaluations", "ece", "projet")
                for p in sorted((chap_dir / sub).glob("*.tex"))]
    sys.exit(1 if "fail" in verdicts else 0)
