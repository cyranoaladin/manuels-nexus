"""Crawler responsable : télécharge les documents des sources actives du registre.

Usage : python scripts/crawl.py [--src SRC-0001]
Sortie : raw/{SRC-id}/{date}/... + manifest.json (url, hash, content-type).
Règles : robots.txt respecté, throttling CRAWL_DELAY, User-Agent identifié,
         uniquement les domaines du registre (règle N06 du cahier des charges).
"""
import argparse
import time
import urllib.robotparser
from datetime import date
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from common import CRAWL_DELAY, CRAWL_UA, RAW_DIR, load_registry, sha256, write_json

ALLOWED_EXT = (".pdf", ".html", ".htm", ".tex", ".odt", "")


def robots_ok(url: str, rp_cache: dict) -> bool:
    base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    if base not in rp_cache:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(urljoin(base, "/robots.txt"))
        try:
            rp.read()
        except Exception:
            rp = None
        rp_cache[base] = rp
    rp = rp_cache[base]
    return rp is None or rp.can_fetch(CRAWL_UA, url)


def discover_links(client: httpx.Client, source: dict) -> list[str]:
    """Découverte selon la méthode déclarée dans le registre (page_links | sitemap | manual)."""
    method = source["crawl"]["method"]
    if method == "manual":
        return []
    if method == "sitemap":
        r = client.get(urljoin(source["url"], "/sitemap.xml"))
        soup = BeautifulSoup(r.text, "xml")
        return [loc.text for loc in soup.find_all("loc")]
    # page_links : liens de la page racine du scope
    r = client.get(source["url"])
    soup = BeautifulSoup(r.text, "lxml")
    scope = source["crawl"].get("scope", "")
    links = [urljoin(source["url"], a["href"]) for a in soup.find_all("a", href=True)]
    same_host = [u for u in links if urlparse(u).netloc == urlparse(source["url"]).netloc]
    if scope and scope != "pdf":
        same_host = [u for u in same_host if scope.strip("*") in u]
    if scope == "pdf":
        same_host = [u for u in same_host if u.lower().endswith(".pdf")]
    return sorted(set(same_host))


def crawl_source(source: dict) -> None:
    out_dir = RAW_DIR / source["id"] / date.today().isoformat()
    manifest, rp_cache = [], {}
    headers = {"User-Agent": CRAWL_UA}
    with httpx.Client(headers=headers, timeout=30, follow_redirects=True) as client:
        urls = discover_links(client, source)
        print(f"[{source['id']}] {len(urls)} URLs découvertes")
        for url in urls:
            if not any(url.lower().split("?")[0].endswith(e) for e in ALLOWED_EXT):
                continue
            if not robots_ok(url, rp_cache):
                print(f"  robots.txt interdit : {url}")
                continue
            try:
                r = client.get(url)
                r.raise_for_status()
            except Exception as exc:
                print(f"  échec {url} : {exc}")
                continue
            h = sha256(r.content)
            fname = h[:16] + (".pdf" if "pdf" in r.headers.get("content-type", "") else ".html")
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / fname).write_bytes(r.content)
            manifest.append({"url": url, "hash": h, "file": fname,
                             "content_type": r.headers.get("content-type", "")})
            time.sleep(CRAWL_DELAY)
    write_json(out_dir / "manifest.json", manifest)
    print(f"[{source['id']}] {len(manifest)} documents sauvegardés -> {out_dir}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", help="Crawler une seule source (ex. SRC-0001)")
    args = ap.parse_args()
    for src in load_registry():
        if args.src and src["id"] != args.src:
            continue
        crawl_source(src)
