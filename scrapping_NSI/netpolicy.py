# -*- coding: utf-8 -*-
"""
Politique réseau pour le scraping NSI.

Gère le respect de robots.txt, les délais de politesse par domaine,
les retries avec backoff, le plafonnement de Retry-After,
et l'identification honnête du scraper.
"""

from __future__ import annotations

import logging
import os
import time
import urllib.request
from typing import Any, Protocol, cast
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = os.getenv(
    "NSI_USER_AGENT",
    "NSI-corpus-bot/1.0 (+https://github.com/cyranoaladin/NSI)",
)
DEFAULT_MIN_DELAY: float = float(os.getenv("NSI_SCRAPER_DELAY", "0.5"))
DEFAULT_TIMEOUT: int = int(os.getenv("NSI_SCRAPER_TIMEOUT", "20"))
ROBOTS_ON_ERROR: str = os.getenv("NSI_ROBOTS_ON_ERROR", "allow").lower()
MAX_RETRY_AFTER: int = int(os.getenv("NSI_MAX_RETRY_AFTER", "60"))
ROBOTS_ERROR_DELAY_FACTOR: float = 2.0


class RobotsCache:
    """Cache robots.txt par domaine, avec politique configurable sur erreur."""

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        on_error: str = ROBOTS_ON_ERROR,
        session: requests.Session | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self._user_agent = user_agent
        self._on_error = on_error  # "allow" ou "deny"
        self._cache: dict[str, RobotFileParser | None] = {}
        self._session = session
        self._timeout = timeout

    def _domain_key(self, url: str) -> str:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _fetch_robots(self, domain_key: str) -> RobotFileParser | None:
        robots_url = f"{domain_key}/robots.txt"
        rp = RobotFileParser()
        rp.set_url(robots_url)
        try:
            if self._session:
                resp = self._session.get(robots_url, timeout=self._timeout)
                if resp.status_code == 200:
                    rp.parse(resp.text.splitlines())
                else:
                    rp.parse([])
            else:
                req = urllib.request.Request(
                    robots_url, headers={"User-Agent": self._user_agent},
                )
                with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                    raw = resp.read().decode("utf-8", errors="replace")
                    rp.parse(raw.splitlines())
        except Exception:
            logger.warning("Impossible de récupérer %s", robots_url)
            return None
        return rp

    def _get_parser(self, url: str) -> RobotFileParser | None:
        key = self._domain_key(url)
        if key not in self._cache:
            self._cache[key] = self._fetch_robots(key)
        return self._cache[key]

    def can_fetch(self, url: str) -> bool:
        """Vérifie si l'URL est autorisée par robots.txt.

        Si robots.txt est inaccessible, applique la politique on_error.
        """
        parser = self._get_parser(url)
        if parser is None:
            return self._on_error == "allow"
        return parser.can_fetch(self._user_agent, url)

    def crawl_delay(self, url: str) -> float | None:
        """Retourne le crawl-delay du domaine, ou None si non spécifié."""
        parser = self._get_parser(url)
        if parser is None:
            return ROBOTS_ERROR_DELAY_FACTOR * DEFAULT_MIN_DELAY
        delay = parser.crawl_delay(self._user_agent)
        if delay is not None:
            return float(delay)
        return None


class CappedRetry(Retry):
    """Retry avec plafonnement de Retry-After.

    urllib3 honore Retry-After sans borne : un serveur envoyant
    Retry-After: 86400 bloquerait 24 h. Cette sous-classe plafonne
    la valeur à max_retry_after secondes.
    """

    def __init__(self, *, max_retry_after: int = MAX_RETRY_AFTER, **kwargs: Any) -> None:
        self.max_retry_after = max_retry_after
        super().__init__(**kwargs)

    def get_retry_after(self, response: Any) -> float | None:
        retry_after = super().get_retry_after(response)
        if retry_after is not None and retry_after > self.max_retry_after:
            return float(self.max_retry_after)
        return retry_after

    def new(self, **kw: Any) -> CappedRetry:
        kw.setdefault("max_retry_after", self.max_retry_after)
        return super().new(**kw)


def build_session(
    user_agent: str = DEFAULT_USER_AGENT,
    total_retries: int = 3,
    backoff_factor: float = 0.5,
    max_retry_after: int = MAX_RETRY_AFTER,
) -> requests.Session:
    """Construit une Session requests avec retry/backoff, cap Retry-After et UA honnête."""
    session = requests.Session()
    session.headers["User-Agent"] = user_agent

    retry = CappedRetry(
        max_retry_after=max_retry_after,
        total=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist={429, 500, 502, 503, 504},
        respect_retry_after_header=True,
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


class ThrottleClock(Protocol):
    def monotonic(self) -> float:
        raise RuntimeError("Protocol method")

    def sleep(self, seconds: float) -> None:
        raise RuntimeError("Protocol method")


class DomainThrottle:
    """Maintient une carte domaine → dernier_fetch sur horloge monotone."""

    def __init__(self, clock: ThrottleClock | None = None) -> None:
        self._last_fetch: dict[str, float] = {}
        self._clock: ThrottleClock = clock or cast(ThrottleClock, time)

    def wait(self, domain: str, delay: float) -> None:
        """Attend le délai requis depuis le dernier fetch sur ce domaine."""
        now = self._clock.monotonic()
        last = self._last_fetch.get(domain, 0.0)
        remaining = delay - (now - last)
        if remaining > 0:
            self._clock.sleep(remaining)
        self._last_fetch[domain] = self._clock.monotonic()


def polite_get(
    session: requests.Session,
    url: str,
    *,
    robots: RobotsCache,
    throttle: DomainThrottle,
    min_delay: float = DEFAULT_MIN_DELAY,
    timeout: int = DEFAULT_TIMEOUT,
    stream: bool = False,
) -> tuple[requests.Response | None, str | None, bool]:
    """GET poli : vérifie robots, applique le délai, retourne (response, error, robots_blocked).

    Retourne un triplet :
    - response : la réponse HTTP si succès, None sinon
    - error : message d'erreur le cas échéant, None sinon
    - robots_blocked : True si l'URL a été refusée par robots.txt
    """
    if not robots.can_fetch(url):
        msg = f"Refusé par robots.txt : {url}"
        logger.info(msg)
        return None, msg, True

    domain = urlparse(url).netloc.lower()
    crawl = robots.crawl_delay(url)
    effective_delay = max(crawl or 0.0, min_delay)
    throttle.wait(domain, effective_delay)

    try:
        response = session.get(url, timeout=timeout, stream=stream)
        return response, None, False
    except requests.RequestException as exc:
        msg = f"Exception requête pour {url}: {exc}"
        return None, msg, False
