# -*- coding: utf-8 -*-
"""Tests pour netpolicy.py — réseau entièrement mocké, aucun sleep réel."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from scrapping_NSI.netpolicy import (
    DEFAULT_MIN_DELAY,
    ROBOTS_ERROR_DELAY_FACTOR,
    CappedRetry,
    DomainThrottle,
    RobotsCache,
    build_session,
    polite_get,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fake_clock(start: float = 1000.0):
    """Horloge monotone simulée : avance automatiquement après sleep."""
    state = {"now": start}

    class FakeClock:
        def monotonic(self):
            return state["now"]

        def sleep(self, seconds):
            state["now"] += seconds

    return FakeClock()


def _robots_txt_allow_all() -> str:
    return "User-agent: *\nAllow: /\n"


def _robots_txt_deny_all() -> str:
    return "User-agent: *\nDisallow: /\n"


def _robots_txt_with_delay(delay: int = 3) -> str:
    return f"User-agent: *\nAllow: /\nCrawl-delay: {delay}\n"


def _mock_session_for_robots(text: str, status: int = 200):
    """Retourne une Session mockée dont .get() retourne le texte donné."""
    session = MagicMock(spec=requests.Session)
    resp = MagicMock()
    resp.status_code = status
    resp.text = text
    session.get.return_value = resp
    return session


# ---------------------------------------------------------------------------
# RobotsCache
# ---------------------------------------------------------------------------

class TestRobotsCache:

    def test_can_fetch_allowed(self):
        session = _mock_session_for_robots(_robots_txt_allow_all())
        cache = RobotsCache(user_agent="TestBot", session=session)
        assert cache.can_fetch("https://example.com/page") is True

    def test_can_fetch_denied(self):
        session = _mock_session_for_robots(_robots_txt_deny_all())
        cache = RobotsCache(user_agent="TestBot", session=session)
        assert cache.can_fetch("https://example.com/page") is False

    def test_robots_404_allow_by_default(self):
        session = _mock_session_for_robots("", status=404)
        cache = RobotsCache(user_agent="TestBot", on_error="allow", session=session)
        assert cache.can_fetch("https://example.com/page") is True

    def test_robots_error_allow_policy(self):
        session = MagicMock(spec=requests.Session)
        session.get.side_effect = requests.ConnectionError("connection refused")
        cache = RobotsCache(user_agent="TestBot", on_error="allow", session=session)
        assert cache.can_fetch("https://unreachable.example.com/page") is True

    def test_robots_error_deny_policy(self):
        session = MagicMock(spec=requests.Session)
        session.get.side_effect = requests.ConnectionError("connection refused")
        cache = RobotsCache(user_agent="TestBot", on_error="deny", session=session)
        assert cache.can_fetch("https://unreachable.example.com/page") is False

    def test_crawl_delay_parsed(self):
        session = _mock_session_for_robots(_robots_txt_with_delay(5))
        cache = RobotsCache(user_agent="TestBot", session=session)
        assert cache.crawl_delay("https://example.com/page") == 5.0

    def test_crawl_delay_none_when_absent(self):
        session = _mock_session_for_robots(_robots_txt_allow_all())
        cache = RobotsCache(user_agent="TestBot", session=session)
        assert cache.crawl_delay("https://example.com/page") is None

    def test_crawl_delay_on_error_returns_majorated(self):
        session = MagicMock(spec=requests.Session)
        session.get.side_effect = requests.Timeout("timeout")
        cache = RobotsCache(user_agent="TestBot", on_error="allow", session=session)
        expected = ROBOTS_ERROR_DELAY_FACTOR * DEFAULT_MIN_DELAY
        assert cache.crawl_delay("https://broken.example.com/page") == expected

    def test_cache_reuses_parser(self):
        session = _mock_session_for_robots(_robots_txt_allow_all())
        cache = RobotsCache(user_agent="TestBot", session=session)
        cache.can_fetch("https://example.com/a")
        cache.can_fetch("https://example.com/b")
        assert session.get.call_count == 1

    def test_different_domains_fetch_separately(self):
        session = _mock_session_for_robots(_robots_txt_allow_all())
        cache = RobotsCache(user_agent="TestBot", session=session)
        cache.can_fetch("https://alpha.example.com/a")
        cache.can_fetch("https://beta.example.com/b")
        assert session.get.call_count == 2

    def test_without_session_uses_urlopen_with_timeout_and_ua(self):
        """Sans session, utilise urllib.request.urlopen avec timeout borné et UA identifiable."""
        cache = RobotsCache(user_agent="TestBot/1.0", session=None, timeout=5)
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"User-agent: *\nAllow: /\n"
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("netpolicy.urllib.request.urlopen", return_value=mock_resp) as mock_urlopen:
            result = cache.can_fetch("https://test.example.com/page")

        mock_urlopen.assert_called_once()
        call_args = mock_urlopen.call_args
        # Le premier argument est un Request (pas une string URL)
        req_obj = call_args[0][0]
        assert req_obj.get_header("User-agent") == "TestBot/1.0"
        # Timeout passé
        assert call_args[1]["timeout"] == 5
        assert result is True

    def test_without_session_timeout_error_applies_on_error_policy(self):
        """Sans session, timeout urllib → on_error = deny → refusé."""
        cache = RobotsCache(user_agent="TestBot", session=None, on_error="deny")
        with patch("netpolicy.urllib.request.urlopen", side_effect=TimeoutError("slow")):
            assert cache.can_fetch("https://slow.example.com/page") is False

    def test_without_session_timeout_error_allows_with_allow_policy(self):
        """Sans session, timeout urllib → on_error = allow → autorisé."""
        cache = RobotsCache(user_agent="TestBot", session=None, on_error="allow")
        with patch("netpolicy.urllib.request.urlopen", side_effect=TimeoutError("slow")):
            assert cache.can_fetch("https://slow.example.com/page") is True


# ---------------------------------------------------------------------------
# CappedRetry
# ---------------------------------------------------------------------------

class TestCappedRetry:

    def test_get_retry_after_clamps_large_value(self):
        """Retry-After: 86400 → plafonné à max_retry_after (ex. 60)."""
        retry = CappedRetry(max_retry_after=60, total=3, status_forcelist={429})
        mock_response = MagicMock()
        mock_response.headers = {"Retry-After": "86400"}
        mock_response.getheader.return_value = "86400"

        result = retry.get_retry_after(mock_response)
        assert result is not None
        assert result <= 60

    def test_get_retry_after_preserves_small_value(self):
        """Retry-After: 5 → conservé tel quel (< plafond)."""
        retry = CappedRetry(max_retry_after=60, total=3, status_forcelist={429})
        mock_response = MagicMock()
        mock_response.headers = {"Retry-After": "5"}
        mock_response.getheader.return_value = "5"

        result = retry.get_retry_after(mock_response)
        assert result == pytest.approx(5.0)

    def test_get_retry_after_none_when_absent(self):
        """Pas de header Retry-After → retourne None."""
        retry = CappedRetry(max_retry_after=60, total=3, status_forcelist={429})
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_response.getheader.return_value = None

        result = retry.get_retry_after(mock_response)
        assert result is None

    def test_new_preserves_max_retry_after(self):
        """CappedRetry.new() conserve le plafond."""
        retry = CappedRetry(max_retry_after=42, total=3)
        new_retry = retry.new(total=2)
        assert isinstance(new_retry, CappedRetry)
        assert new_retry.max_retry_after == 42
        assert new_retry.total == 2

    def test_build_session_uses_capped_retry(self):
        """build_session utilise CappedRetry, pas Retry standard."""
        session = build_session(max_retry_after=30)
        adapter = session.get_adapter("https://example.com")
        assert isinstance(adapter.max_retries, CappedRetry)
        assert adapter.max_retries.max_retry_after == 30

    def test_capped_retry_sleep_never_exceeds_cap(self):
        """Preuve que Retry-After: 86400 → sleep ≤ max_retry_after, aucun sleep réel."""
        retry = CappedRetry(max_retry_after=60, total=3, status_forcelist={429})
        mock_response = MagicMock()
        mock_response.headers = {"Retry-After": "86400"}
        mock_response.getheader.return_value = "86400"

        capped_value = retry.get_retry_after(mock_response)
        # Le sleep effectif sera cette valeur — vérifier qu'elle est plafonnée
        assert capped_value == 60.0


# ---------------------------------------------------------------------------
# build_session
# ---------------------------------------------------------------------------

class TestBuildSession:

    def test_returns_session_with_user_agent(self):
        session = build_session(user_agent="MyBot/1.0")
        assert session.headers["User-Agent"] == "MyBot/1.0"

    def test_retry_adapter_mounted(self):
        session = build_session()
        adapter = session.get_adapter("https://example.com")
        assert adapter.max_retries.total == 3
        assert 429 in adapter.max_retries.status_forcelist
        assert adapter.max_retries.respect_retry_after_header is True

    def test_custom_backoff(self):
        session = build_session(backoff_factor=1.0)
        adapter = session.get_adapter("https://example.com")
        assert adapter.max_retries.backoff_factor == 1.0


# ---------------------------------------------------------------------------
# DomainThrottle
# ---------------------------------------------------------------------------

class TestDomainThrottle:

    def test_first_request_no_wait(self):
        clock = _make_fake_clock(1000.0)
        throttle = DomainThrottle(clock=clock)
        throttle.wait("example.com", 1.0)
        assert clock.monotonic() == 1000.0

    def test_second_request_waits(self):
        clock = _make_fake_clock(1000.0)
        throttle = DomainThrottle(clock=clock)
        throttle.wait("example.com", 2.0)
        throttle.wait("example.com", 2.0)
        assert clock.monotonic() == 1002.0

    def test_different_domains_independent(self):
        clock = _make_fake_clock(1000.0)
        throttle = DomainThrottle(clock=clock)
        throttle.wait("alpha.com", 5.0)
        throttle.wait("beta.com", 5.0)
        assert clock.monotonic() == 1000.0

    def test_sufficient_elapsed_no_wait(self):
        clock = _make_fake_clock(1000.0)
        throttle = DomainThrottle(clock=clock)
        throttle.wait("example.com", 1.0)
        clock.sleep(5.0)
        throttle.wait("example.com", 1.0)
        assert clock.monotonic() == 1005.0


# ---------------------------------------------------------------------------
# polite_get
# ---------------------------------------------------------------------------

class TestPoliteGet:

    def _setup(self, *, robots_allow: bool = True):
        clock = _make_fake_clock(1000.0)
        throttle = DomainThrottle(clock=clock)

        robots = MagicMock(spec=RobotsCache)
        robots.can_fetch.return_value = robots_allow
        robots.crawl_delay.return_value = None

        session = MagicMock(spec=requests.Session)
        resp = MagicMock()
        resp.status_code = 200
        resp.headers = {"content-type": "text/html"}
        resp.text = "<html></html>"
        session.get.return_value = resp

        return session, robots, throttle, clock

    def test_allowed_url_fetched(self):
        session, robots, throttle, _ = self._setup(robots_allow=True)
        response, error, blocked = polite_get(
            session, "https://example.com/page",
            robots=robots, throttle=throttle,
        )
        assert response is not None
        assert error is None
        assert blocked is False
        session.get.assert_called_once()

    def test_blocked_url_never_fetched(self):
        session, robots, throttle, _ = self._setup(robots_allow=False)
        response, error, blocked = polite_get(
            session, "https://example.com/secret",
            robots=robots, throttle=throttle,
        )
        assert response is None
        assert blocked is True
        assert "robots.txt" in error
        session.get.assert_not_called()

    def test_request_exception_returns_error(self):
        session, robots, throttle, _ = self._setup(robots_allow=True)
        session.get.side_effect = requests.ConnectionError("refused")
        response, error, blocked = polite_get(
            session, "https://example.com/page",
            robots=robots, throttle=throttle,
        )
        assert response is None
        assert blocked is False
        assert "Exception" in error

    def test_timeout_returns_error(self):
        session, robots, throttle, _ = self._setup(robots_allow=True)
        session.get.side_effect = requests.Timeout("timeout")
        response, error, blocked = polite_get(
            session, "https://example.com/page",
            robots=robots, throttle=throttle,
        )
        assert response is None
        assert blocked is False

    def test_crawl_delay_respected(self):
        session, robots, throttle, clock = self._setup(robots_allow=True)
        robots.crawl_delay.return_value = 5.0

        polite_get(
            session, "https://example.com/a",
            robots=robots, throttle=throttle, min_delay=1.0,
        )
        t1 = clock.monotonic()

        polite_get(
            session, "https://example.com/b",
            robots=robots, throttle=throttle, min_delay=1.0,
        )
        t2 = clock.monotonic()
        assert t2 - t1 == pytest.approx(5.0)

    def test_min_delay_when_no_crawl_delay(self):
        session, robots, throttle, clock = self._setup(robots_allow=True)
        robots.crawl_delay.return_value = None

        polite_get(
            session, "https://example.com/a",
            robots=robots, throttle=throttle, min_delay=2.0,
        )
        t1 = clock.monotonic()

        polite_get(
            session, "https://example.com/b",
            robots=robots, throttle=throttle, min_delay=2.0,
        )
        t2 = clock.monotonic()
        assert t2 - t1 == pytest.approx(2.0)

    def test_stream_parameter_forwarded(self):
        session, robots, throttle, _ = self._setup(robots_allow=True)
        polite_get(
            session, "https://example.com/file.pdf",
            robots=robots, throttle=throttle, stream=True,
        )
        _, kwargs = session.get.call_args
        assert kwargs["stream"] is True
