# -*- coding: utf-8 -*-
"""
Traçabilité de provenance des ressources téléchargées.

Écrit un enregistrement JSONL pour chaque téléchargement réussi et
génère un NOTICE_SOURCES.md récapitulatif.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TextIO


def compute_sha256(file_path: Path) -> str:
    """Calcule le sha256 d'un fichier."""
    h = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def guess_license(page_html: str | None) -> str:
    """Heuristique best-effort pour deviner la licence depuis le HTML source.

    Retourne "unknown" si rien n'est détecté. Ne jamais inventer.
    """
    if not page_html:
        return "unknown"

    text = page_html.lower()

    # Creative Commons
    cc_pattern = re.compile(r"creative\s*commons|creativecommons\.org|cc\s+by", re.IGNORECASE)
    if cc_pattern.search(text):
        # Essayer d'extraire la variante
        variant = re.search(
            r"(cc\s+by[-\s]?(?:sa|nc|nd|nc[-\s]?sa|nc[-\s]?nd)?(?:\s+\d\.\d)?)",
            text,
            re.IGNORECASE,
        )
        if variant:
            return variant.group(1).strip().upper().replace("  ", " ")
        return "Creative Commons (variante non déterminée)"

    # Licence explicite
    if re.search(r"\blicen[cs]e\s+mit\b", text, re.IGNORECASE):
        return "MIT"
    if re.search(r"\bgpl\b", text, re.IGNORECASE):
        return "GPL (variante non déterminée)"

    # Lien LICENSE
    if re.search(r'href\s*=\s*["\'][^"\']*licen[cs]e', text, re.IGNORECASE):
        return "licence détectée (lien, contenu non vérifié)"

    return "unknown"


def write_provenance_record(
    output: Path | TextIO,
    *,
    sha256: str,
    filename: str,
    source_url: str,
    site_name: str,
    page_url: str,
    http_status: int,
    content_type: str,
    byte_count: int,
    robots_allowed: bool,
    license_guess: str = "unknown",
    duplicate_of: str | None = None,
) -> None:
    """Écrit un enregistrement de provenance en JSONL (append)."""
    record = {
        "sha256": sha256,
        "filename": filename,
        "source_url": source_url,
        "site_name": site_name,
        "page_url": page_url,
        "http_status": http_status,
        "content_type": content_type,
        "bytes": byte_count,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "license_guess": license_guess,
        "robots_allowed": robots_allowed,
    }
    if duplicate_of is not None:
        record["duplicate_of"] = duplicate_of

    line = json.dumps(record, ensure_ascii=False) + "\n"

    if isinstance(output, Path):
        with output.open("a", encoding="utf-8") as f:
            f.write(line)
    else:
        output.write(line)


PROVENANCE_REQUIRED_KEYS = {
    "sha256", "filename", "source_url", "site_name", "page_url",
    "http_status", "content_type", "bytes", "retrieved_at",
    "license_guess", "robots_allowed",
}

PROVENANCE_OPTIONAL_KEYS = {"duplicate_of"}

PROVENANCE_ALLOWED_KEYS = PROVENANCE_REQUIRED_KEYS | PROVENANCE_OPTIONAL_KEYS


def validate_provenance_record(record: dict[str, object]) -> bool:
    """Vérifie qu'un enregistrement contient toutes les clés requises et aucune clé inconnue."""
    keys = set(record.keys())
    return PROVENANCE_REQUIRED_KEYS.issubset(keys) and keys.issubset(PROVENANCE_ALLOWED_KEYS)


def generate_notice_sources(provenance_path: Path, output_path: Path) -> None:
    """Génère NOTICE_SOURCES.md depuis le fichier provenance.jsonl."""
    sites: dict[str, dict[str, Any]] = {}
    downloaded_hashes: set[str] = set()
    duplicate_content = 0

    if not provenance_path.exists():
        output_path.write_text(
            "# Sources des ressources\n\nAucune provenance enregistrée.\n",
            encoding="utf-8",
        )
        return

    with provenance_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            site = record.get("site_name", "inconnu")
            if site not in sites:
                sites[site] = {
                    "urls": set(),
                    "licenses": set(),
                    "count": 0,
                }
            sites[site]["urls"].add(record.get("page_url", ""))
            sites[site]["licenses"].add(record.get("license_guess", "unknown"))
            sha = record.get("sha256", "")
            if record.get("duplicate_of"):
                duplicate_content += 1
                continue
            if sha and sha not in downloaded_hashes:
                downloaded_hashes.add(sha)
                sites[site]["count"] += 1

    lines = [
        "# Notice des sources",
        "",
        "> **Usage** : matière première de réécriture, jamais republication telle quelle.",
        "> Cf. METHODE_PRODUCTION_REELLE.md §9/§5 sur la quarantaine.",
        "",
        "## Résumé",
        "",
        f"- files_downloaded: {len(downloaded_hashes)}",
        "- files_skipped: 0",
        f"- files_duplicate_content: {duplicate_content}",
        "",
        "| Site | URL(s) exemple | Licence détectée | Fichiers | À vérifier |",
        "|------|---------------|-----------------|----------|------------|",
    ]

    for site_name, info in sorted(sites.items()):
        url_example = sorted(info["urls"])[0] if info["urls"] else ""
        licenses = ", ".join(sorted(info["licenses"]))
        needs_check = "oui" if "unknown" in info["licenses"] else "non"
        lines.append(
            f"| {site_name} | {url_example} | {licenses} | {info['count']} | {needs_check} |"
        )

    lines.append("")
    lines.append(f"*Généré automatiquement depuis `{provenance_path.name}`.*")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
