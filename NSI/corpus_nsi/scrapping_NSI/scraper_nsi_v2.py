# -*- coding: utf-8 -*-
"""
Scraper NSI v2 : extraction récursive bornée des ressources pédagogiques.

Améliorations par rapport à scraper_nsi.py :
- normalisation des antislashs dans les href avant urljoin ;
- exploration profondeur 1 des pages HTML internes ;
- prise en charge des annuaires en ajoutant les sites externes découverts ;
- limites explicites pour éviter les boucles et respecter la politesse réseau ;
- conformité robots.txt et traçabilité de provenance (netpolicy + provenance).
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from urllib.parse import urldefrag, urljoin, urlparse, unquote

import requests
from bs4 import BeautifulSoup

from scrapping_NSI.netpolicy import (
    DEFAULT_USER_AGENT,
    DomainThrottle,
    RobotsCache,
    build_session,
    polite_get,
)
from scrapping_NSI.provenance import compute_sha256, guess_license, write_provenance_record


CSV_FILE = os.getenv("NSI_SCRAPER_CSV", "urls_a_scraper.csv")
OUTPUT_ROOT = Path("ressources_nsi_extraites_v2")
DEFAULT_DUPLICATE_ROOTS = os.pathsep.join([str(OUTPUT_ROOT), "ressources_nsi_extraites"])
EXTENSIONS_CIBLES = (".pdf", ".ipynb", ".py", ".zip", ".docx", ".xlsx")
NON_HTML_EXTENSIONS = (
    ".css",
    ".js",
    ".json",
    ".xml",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".ico",
    ".mp3",
    ".mp4",
    ".ogg",
    ".webm",
    ".txt",
)
MAX_DEPTH = int(os.getenv("NSI_SCRAPER_MAX_DEPTH", "1"))
MAX_SUBPAGES_PER_SITE = int(os.getenv("NSI_SCRAPER_MAX_SUBPAGES", "75"))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("NSI_SCRAPER_TIMEOUT", "20"))
POLITE_DELAY_SECONDS = float(os.getenv("NSI_SCRAPER_DELAY", "0.5"))
DUPLICATE_SCAN_ROOTS = tuple(
    Path(path)
    for path in os.getenv("NSI_SCRAPER_DUPLICATE_ROOTS", DEFAULT_DUPLICATE_ROOTS).split(os.pathsep)
    if path.strip()
)

OUT_OF_SCOPE_SCRAPE_TARGETS: dict[str, str] = {
    "Éduscol STI - Hub Spécialité NSI": (
        "plateforme institutionnelle traitée par scraper_eduscol.py et non par le crawler HTML V2"
    ),
    "Éduscol STI - Référentiels NSI": (
        "plateforme institutionnelle traitée par scraper_eduscol.py et non par le crawler HTML V2"
    ),
    "Wikibooks - Communauté NSI": (
        "wiki exportable par outil dédié MediaWiki, hors périmètre du crawler statique V2"
    ),
}


@dataclass
class ExtractedLinks:
    target_files: list[str] = field(default_factory=list)
    internal_pages: list[str] = field(default_factory=list)
    external_sites: list[str] = field(default_factory=list)


@dataclass
class SiteStats:
    site_name: str
    base_url: str
    discovered_from_annuaire: bool = False
    pages_seen: int = 0
    files_downloaded: int = 0
    files_skipped: int = 0
    files_duplicate_content: int = 0
    robots_blocked: int = 0
    errors: list[str] = field(default_factory=list)
    external_sites_discovered: int = 0


@dataclass
class DuplicateIndex:
    """In-memory guard against duplicate URLs and duplicate file contents.

    Bootstrap order is deliberate: `provenance.jsonl` is the durable source of
    truth across scraper runs. A bounded disk scan of `DUPLICATE_SCAN_ROOTS` is
    only a fallback when provenance is absent or structurally incomplete.
    """

    urls: set[str] = field(default_factory=set)
    content_hashes: set[str] = field(default_factory=set)
    bootstrap_source: str = "empty"
    disk_scan_performed: bool = False

    @staticmethod
    def _valid_sha256(value: object) -> bool:
        return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None

    @classmethod
    def from_roots(
        cls,
        roots: Iterable[Path],
        *,
        provenance_path: Path | None = None,
    ) -> "DuplicateIndex":
        index = cls()
        provenance_complete = False
        if provenance_path is not None and provenance_path.exists():
            provenance_complete = index._load_from_provenance(provenance_path)
            if provenance_complete:
                index.bootstrap_source = "provenance"
                return index

        index._scan_content_hashes(roots)
        if provenance_path is not None and provenance_path.exists():
            index.bootstrap_source = "provenance+disk"
        else:
            index.bootstrap_source = "disk"
        return index

    def _load_from_provenance(self, provenance_path: Path) -> bool:
        complete = True
        saw_record = False
        with provenance_path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                saw_record = True
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    complete = False
                    continue
                if not isinstance(record, dict):
                    complete = False
                    continue
                sha = record.get("sha256")
                source_url = record.get("source_url")
                if not self._valid_sha256(sha):
                    complete = False
                else:
                    self.content_hashes.add(str(sha))
                if isinstance(source_url, str) and source_url:
                    self.urls.add(canonicalize_url(source_url))
                else:
                    complete = False
        return complete and saw_record

    def _scan_content_hashes(self, roots: Iterable[Path]) -> None:
        self.disk_scan_performed = True
        for root in roots:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if path.is_file() and not path.name.endswith(".part"):
                    self.content_hashes.add(compute_sha256(path))

    def has_url(self, url: str) -> bool:
        return canonicalize_url(url) in self.urls

    def has_content_hash(self, content_hash: str) -> bool:
        return content_hash in self.content_hashes

    def register_url(self, url: str) -> None:
        self.urls.add(canonicalize_url(url))

    def register_file(
        self,
        url: str,
        file_path: Path,
        *,
        content_hash: str | None = None,
    ) -> None:
        self.register_url(url)
        if content_hash is None and file_path.exists():
            content_hash = compute_sha256(file_path)
        if content_hash is not None:
            self.content_hashes.add(content_hash)


def normalize_href(href: str) -> str:
    """Normalize raw href before resolving it as an URL."""
    return href.strip().replace("\\", "/")


def canonicalize_url(url: str) -> str:
    """Remove fragments and normalize trailing duplicates enough for visited sets."""
    clean, _fragment = urldefrag(url)
    return clean


def clean_filename(filename: str) -> str:
    decoded = unquote(filename)
    keepcharacters = (".", "_", "-", " ")
    cleaned = "".join(c for c in decoded if c.isalnum() or c in keepcharacters).strip()
    return cleaned or "ressource"


def filename_from_url(url: str) -> str:
    parsed_url = urlparse(url)
    github_archive = re.fullmatch(
        r"/([^/]+)/([^/]+)/archive/refs/heads/(.+)\.zip",
        parsed_url.path,
    )
    if parsed_url.netloc.lower() == "github.com" and github_archive:
        owner, repo, branch = github_archive.groups()
        return clean_filename(f"{owner}_{repo}_{branch}.zip")

    base_name = os.path.basename(parsed_url.path)
    return clean_filename(base_name) if base_name else ""


def clean_folder_name(name: str) -> str:
    keepcharacters = (".", "_", "-", " ")
    cleaned = "".join(c for c in name if c.isalnum() or c in keepcharacters).strip()
    return cleaned or "site"


def is_http_url(url: str) -> bool:
    return urlparse(url).scheme in {"http", "https"}


def is_target_file_url(url: str) -> bool:
    return urlparse(url).path.lower().endswith(EXTENSIONS_CIBLES)


def same_domain(url: str, base_url: str) -> bool:
    return urlparse(url).netloc.lower() == urlparse(base_url).netloc.lower()


def is_html_like_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    path = parsed.path.lower()
    if not path or path.endswith("/"):
        return True
    if path.endswith(EXTENSIONS_CIBLES) or path.endswith(NON_HTML_EXTENSIONS):
        return False
    suffix = Path(path).suffix
    return suffix in {"", ".html", ".htm", ".php", ".asp", ".aspx"}


def internal_scope_prefix(base_url: str) -> str:
    """Return the internal path prefix allowed for depth-1 crawling."""
    path = urlparse(base_url).path or "/"
    if path.endswith("/"):
        return path
    suffix = Path(path).suffix.lower()
    if suffix in {".html", ".htm", ".php", ".asp", ".aspx"}:
        parent = str(Path(path).parent).replace("\\", "/")
        return parent.rstrip("/") + "/"
    return path.rstrip("/") + "/"


def is_internal_html_url(url: str, base_url: str, scope_prefix: str | None = None) -> bool:
    if not same_domain(url, base_url) or not is_html_like_url(url):
        return False
    if scope_prefix is None:
        return True
    path = urlparse(url).path or "/"
    return path == scope_prefix.rstrip("/") or path.startswith(scope_prefix)


def is_annuaire_site(site_name: str, type_structure: str, discovered: bool = False) -> bool:
    if discovered:
        return False
    marker = f"{site_name} {type_structure}".lower()
    return "annuaire" in marker or "méta-index" in marker or "meta-index" in marker


def should_ignore_external_domain(url: str) -> bool:
    domain = urlparse(url).netloc.lower()
    ignored_parts = (
        "facebook.",
        "twitter.",
        "x.com",
        "linkedin.",
        "youtube.",
        "youtu.be",
        "instagram.",
        "creativecommons.",
        "w3.org",
        "schema.org",
    )
    return any(part in domain for part in ignored_parts)


def dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def extract_links_from_html(
    html: str,
    base_url: str,
    annuaire: bool = False,
    scope_prefix: str | None = None,
) -> ExtractedLinks:
    soup = BeautifulSoup(html, "html.parser")
    target_files: list[str] = []
    internal_pages: list[str] = []
    external_sites: list[str] = []

    for link in soup.find_all("a", href=True):
        href_value = link.get("href", "")
        raw_href = normalize_href(href_value if isinstance(href_value, str) else "")
        if not raw_href or raw_href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue

        absolute_url = canonicalize_url(urljoin(base_url, raw_href))
        if not is_http_url(absolute_url):
            continue

        if is_target_file_url(absolute_url):
            target_files.append(absolute_url)
        elif is_internal_html_url(absolute_url, base_url, scope_prefix=scope_prefix):
            internal_pages.append(absolute_url)
        elif (
            annuaire
            and not same_domain(absolute_url, base_url)
            and is_html_like_url(absolute_url)
            and not should_ignore_external_domain(absolute_url)
        ):
            external_sites.append(absolute_url)

    return ExtractedLinks(
        target_files=dedupe_preserve_order(target_files),
        internal_pages=dedupe_preserve_order(internal_pages),
        external_sites=dedupe_preserve_order(external_sites),
    )


def github_archive_urls(repo_url: str, html: str) -> list[str]:
    parsed = urlparse(repo_url)
    if parsed.netloc.lower() != "github.com":
        return []

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 2:
        return []

    owner, repo = parts
    branch_pattern = re.compile(
        rf'href=["\']/{re.escape(owner)}/{re.escape(repo)}/tree/([^"\'?#/]+)'
    )
    branches = dedupe_preserve_order(
        unquote(match.group(1)) for match in branch_pattern.finditer(html)
    )
    branch = branches[0] if branches else "main"
    return [f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"]


def fetch_html(
    url: str,
    *,
    session: requests.Session,
    robots: RobotsCache,
    throttle: DomainThrottle,
) -> tuple[str | None, str | None, bool]:
    """Récupère une page HTML via polite_get.

    Retourne (html, error, robots_blocked).
    """
    response, error, blocked = polite_get(
        session, url, robots=robots, throttle=throttle,
        min_delay=POLITE_DELAY_SECONDS, timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if blocked:
        return None, error, True
    if error or response is None:
        return None, error or f"Pas de réponse pour {url}", False
    if response.status_code != 200:
        return None, f"Statut {response.status_code} pour {url}", False
    content_type = response.headers.get("content-type", "").lower()
    if "html" not in content_type and content_type:
        return None, f"Contenu non HTML ({content_type}) pour {url}", False
    return response.text, None, False


def download_file(
    url: str,
    folder_destination: Path,
    stats: SiteStats,
    *,
    session: requests.Session,
    robots: RobotsCache,
    throttle: DomainThrottle,
    duplicate_index: DuplicateIndex | None = None,
    provenance_path: Path | None = None,
    site_name: str = "",
    page_url: str = "",
    page_html: str | None = None,
) -> bool:
    partial_path: Path | None = None
    try:
        filename = filename_from_url(url)
        if not filename:
            stats.errors.append(f"Nom de fichier absent pour {url}")
            return False

        file_path = folder_destination / filename

        if duplicate_index and duplicate_index.has_url(url):
            print(f"    [Sauté] URL déjà traitée : {filename}", flush=True)
            stats.files_skipped += 1
            return True

        folder_destination.mkdir(parents=True, exist_ok=True)
        if file_path.exists():
            print(f"    [Sauté] Déjà présent : {filename}", flush=True)
            stats.files_skipped += 1
            if duplicate_index:
                duplicate_index.register_file(url, file_path)
            return True

        print(f"    [Téléchargement] {url} -> {filename}", flush=True)
        response, error, blocked = polite_get(
            session, url, robots=robots, throttle=throttle, stream=True,
            min_delay=POLITE_DELAY_SECONDS, timeout=REQUEST_TIMEOUT_SECONDS,
        )

        if blocked:
            print(f"    [Robots] {error}", flush=True)
            stats.robots_blocked += 1
            return True

        if error or response is None:
            print(f"    [Erreur] {error}", flush=True)
            stats.errors.append(error or f"Pas de réponse pour {url}")
            return False

        if response.status_code == 200:
            partial_path = file_path.with_name(file_path.name + ".part")
            if partial_path.exists():
                partial_path.unlink()
            with partial_path.open("wb") as output:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        output.write(chunk)
            sha = compute_sha256(partial_path)
            byte_count = partial_path.stat().st_size
            content_type = response.headers.get("content-type", "")

            if duplicate_index and duplicate_index.has_content_hash(sha):
                partial_path.unlink()
                partial_path = None
                duplicate_index.register_url(url)
                stats.files_duplicate_content += 1
                if provenance_path:
                    write_provenance_record(
                        provenance_path,
                        sha256=sha,
                        filename=filename,
                        source_url=url,
                        site_name=site_name,
                        page_url=page_url,
                        http_status=200,
                        content_type=content_type,
                        byte_count=byte_count,
                        robots_allowed=True,
                        license_guess=guess_license(page_html),
                        duplicate_of=sha,
                    )
                print(f"    [Doublon contenu] {url} -> sha256={sha}", flush=True)
                return True

            partial_path.replace(file_path)
            partial_path = None
            stats.files_downloaded += 1
            if duplicate_index:
                duplicate_index.register_file(url, file_path, content_hash=sha)

            if provenance_path:
                write_provenance_record(
                    provenance_path,
                    sha256=sha,
                    filename=filename,
                    source_url=url,
                    site_name=site_name,
                    page_url=page_url,
                    http_status=200,
                    content_type=content_type,
                    byte_count=byte_count,
                    robots_allowed=True,
                    license_guess=guess_license(page_html),
                )
            return True

        message = f"Statut {response.status_code} pour {url}"
        print(f"    [Erreur] {message}", flush=True)
        stats.errors.append(message)
        return False
    except (requests.RequestException, OSError) as exc:
        if partial_path and partial_path.exists():
            partial_path.unlink()
        message = f"Exception téléchargement pour {url}: {exc}"
        print(f"    [Exception] {message}", flush=True)
        stats.errors.append(message)
        return False


def site_output_folder(site_name: str) -> Path:
    return OUTPUT_ROOT / clean_folder_name(site_name)


def process_target_files(
    files: list[str],
    site_folder: Path,
    stats: SiteStats,
    *,
    session: requests.Session,
    robots: RobotsCache,
    throttle: DomainThrottle,
    duplicate_index: DuplicateIndex | None = None,
    provenance_path: Path | None = None,
    site_name: str = "",
    page_url: str = "",
    page_html: str | None = None,
) -> None:
    for file_url in files:
        ext = urlparse(file_url).path.rsplit(".", 1)[-1].lower()
        download_file(
            file_url,
            site_folder / ext,
            stats,
            session=session,
            robots=robots,
            throttle=throttle,
            duplicate_index=duplicate_index,
            provenance_path=provenance_path,
            site_name=site_name,
            page_url=page_url,
            page_html=page_html,
        )


def scrape_site(
    site_name: str,
    base_url: str,
    type_structure: str,
    *,
    session: requests.Session,
    robots: RobotsCache,
    throttle: DomainThrottle,
    discovered: bool = False,
    duplicate_index: DuplicateIndex | None = None,
    provenance_path: Path | None = None,
) -> tuple[SiteStats, list[str]]:
    annuaire = is_annuaire_site(site_name, type_structure, discovered=discovered)
    stats = SiteStats(site_name=site_name, base_url=base_url, discovered_from_annuaire=discovered)
    site_folder = site_output_folder(site_name)
    scope_prefix = internal_scope_prefix(base_url)

    print(f"\n=== Analyse v2 : {site_name} ({base_url}) ===", flush=True)
    if annuaire:
        print("  Mode annuaire : collecte des sites externes activée.", flush=True)

    queue: deque[tuple[str, int]] = deque([(canonicalize_url(base_url), 0)])
    visited: set[str] = set()
    queued_internal: set[str] = {canonicalize_url(base_url)}
    discovered_external: list[str] = []
    subpages_queued = 0

    while queue:
        current_url, depth = queue.popleft()
        if current_url in visited:
            continue
        visited.add(current_url)
        stats.pages_seen += 1

        print(f"  [Page depth={depth}] {current_url}", flush=True)
        html, error, blocked = fetch_html(
            current_url, session=session, robots=robots, throttle=throttle,
        )
        if blocked:
            print(f"    [Robots] {error}", flush=True)
            stats.robots_blocked += 1
            continue
        if error:
            print(f"    [Erreur page] {error}", flush=True)
            stats.errors.append(error)
            continue
        if html is None:
            continue

        links = extract_links_from_html(
            html,
            current_url,
            annuaire=annuaire,
            scope_prefix=scope_prefix,
        )
        target_files = dedupe_preserve_order(
            [*links.target_files, *github_archive_urls(current_url, html)]
        )
        print(
            f"    Liens fichiers={len(target_files)}, internes={len(links.internal_pages)}, "
            f"externes_annuaire={len(links.external_sites)}",
            flush=True,
        )
        process_target_files(
            target_files,
            site_folder,
            stats,
            session=session,
            robots=robots,
            throttle=throttle,
            duplicate_index=duplicate_index,
            provenance_path=provenance_path,
            site_name=site_name,
            page_url=current_url,
            page_html=html,
        )

        if annuaire:
            discovered_external.extend(links.external_sites)

        if depth < MAX_DEPTH:
            for internal_url in links.internal_pages:
                if internal_url in queued_internal or internal_url in visited:
                    continue
                if subpages_queued >= MAX_SUBPAGES_PER_SITE:
                    continue
                queued_internal.add(internal_url)
                queue.append((internal_url, depth + 1))
                subpages_queued += 1

    external_unique = dedupe_preserve_order(discovered_external)
    stats.external_sites_discovered = len(external_unique)
    print(
        f"=== Fin v2 : {site_name} | pages={stats.pages_seen}, "
        f"téléchargés={stats.files_downloaded}, sautés={stats.files_skipped}, "
        f"doublons_contenu={stats.files_duplicate_content}, "
        f"robots_bloqués={stats.robots_blocked}, "
        f"erreurs={len(stats.errors)}, sites_annuaire={stats.external_sites_discovered} ===",
        flush=True,
    )
    return stats, external_unique


def load_csv_sites(csv_file: str) -> list[tuple[str, str, str]]:
    if not os.path.exists(csv_file):
        print(f"Erreur : fichier '{csv_file}' introuvable.", flush=True)
        sys.exit(1)

    sites: list[tuple[str, str, str]] = []
    with open(csv_file, mode="r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for line_number, row in enumerate(reader, start=2):
            name = (row.get("Nom_Site") or "").strip()
            url = (row.get("URL") or "").strip()
            structure = (row.get("Type_Structure") or "").strip()
            if name and url:
                sites.append((name, canonicalize_url(url), structure))
            else:
                print(
                    f"[CSV IGNORÉ] ligne {line_number} incomplète : "
                    f"Nom_Site={name!r}, URL={url!r}",
                    flush=True,
                )
    return sites


def dynamic_site_name(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_")
    suffix = f" - {path}" if path else ""
    return f"Annuaire - {parsed.netloc}{suffix}"[:150]


def main() -> None:
    print("=" * 72, flush=True)
    print("DÉMARRAGE DU SCRAPER NSI v2 - PROFONDEUR 1 + ANNUAIRES", flush=True)
    print("=" * 72, flush=True)
    print(f"Dossier de sortie : {OUTPUT_ROOT}", flush=True)
    print(f"Limites : profondeur={MAX_DEPTH}, sous-pages/site={MAX_SUBPAGES_PER_SITE}", flush=True)
    provenance_path = Path(os.getenv("NSI_PROVENANCE_FILE", "provenance.jsonl"))
    duplicate_index = DuplicateIndex.from_roots(
        DUPLICATE_SCAN_ROOTS,
        provenance_path=provenance_path,
    )
    print(
        f"Anti-doublons : {len(duplicate_index.urls)} URLs, "
        f"{len(duplicate_index.content_hashes)} empreintes sha256 "
        f"(amorçage={duplicate_index.bootstrap_source}) depuis "
        f"{', '.join(str(root) for root in DUPLICATE_SCAN_ROOTS)}",
        flush=True,
    )

    session = build_session(user_agent=DEFAULT_USER_AGENT)
    robots = RobotsCache(user_agent=DEFAULT_USER_AGENT, session=session)
    throttle = DomainThrottle()

    sites_queue: deque[tuple[str, str, str, bool]] = deque(
        (name, url, structure, False) for name, url, structure in load_csv_sites(CSV_FILE)
    )
    scheduled_site_urls: set[str] = {url for _name, url, _structure, _discovered in sites_queue}
    all_stats: list[SiteStats] = []
    dynamic_sites_added = 0

    while sites_queue:
        site_name, url, structure, discovered = sites_queue.popleft()
        stats, external_sites = scrape_site(
            site_name,
            url,
            structure,
            session=session,
            robots=robots,
            throttle=throttle,
            discovered=discovered,
            duplicate_index=duplicate_index,
            provenance_path=provenance_path,
        )
        all_stats.append(stats)

        for external_url in external_sites:
            if external_url in scheduled_site_urls:
                continue
            scheduled_site_urls.add(external_url)
            sites_queue.append(
                (dynamic_site_name(external_url), external_url, "Découvert via annuaire", True)
            )
            dynamic_sites_added += 1

    print("\n" + "=" * 72, flush=True)
    print("RÉSUMÉ SCRAPER NSI v2", flush=True)
    print("=" * 72, flush=True)
    print(f"Sites traités : {len(all_stats)}", flush=True)
    print(f"Sites ajoutés via annuaire : {dynamic_sites_added}", flush=True)
    print(f"Pages HTML visitées : {sum(s.pages_seen for s in all_stats)}", flush=True)
    print(f"Fichiers téléchargés : {sum(s.files_downloaded for s in all_stats)}", flush=True)
    print(f"Fichiers déjà présents sautés : {sum(s.files_skipped for s in all_stats)}", flush=True)
    print(
        f"Fichiers doublons de contenu : {sum(s.files_duplicate_content for s in all_stats)}",
        flush=True,
    )
    print(f"Robots bloqués : {sum(s.robots_blocked for s in all_stats)}", flush=True)
    print(f"Erreurs : {sum(len(s.errors) for s in all_stats)}", flush=True)
    for stat in all_stats:
        print(
            f"- {stat.site_name}: pages={stat.pages_seen}, téléchargés={stat.files_downloaded}, "
            f"sautés={stat.files_skipped}, doublons_contenu={stat.files_duplicate_content}, "
            f"robots={stat.robots_blocked}, "
            f"erreurs={len(stat.errors)}, "
            f"annuaire={stat.external_sites_discovered}",
            flush=True,
        )
    print("=" * 72, flush=True)
    print(f"PROCESSUS TERMINÉ. Consultez '{OUTPUT_ROOT}/'.", flush=True)


if __name__ == "__main__":  # pragma: no cover
    main()
