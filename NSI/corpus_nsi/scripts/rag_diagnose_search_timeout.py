#!/usr/bin/env python3
"""Diagnose authenticated /search timeouts without printing local secrets."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.rag_core import resolve_env_file  # noqa: E402

ENV_FILE = resolve_env_file(ROOT)
DEFAULT_TIMEOUT = float(os.getenv("RAG_DIAG_TIMEOUT", "20"))


@dataclass
class Probe:
    name: str
    method: str
    url: str
    body: dict[str, object] | None
    authenticated: bool


@dataclass
class ProbeResult:
    name: str
    http_code: str
    duration: float
    timeout: bool
    blocking_step: str


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        values[key.strip()] = value.strip()
    return values


def health_url(search_url: str) -> str:
    return search_url.rsplit("/", 1)[0] + "/health" if search_url.endswith("/search") else search_url.rstrip("/") + "/health"


def run_probe(probe: Probe, api_key: str, timeout: float) -> ProbeResult:
    headers = {"Content-Type": "application/json"}
    if probe.authenticated:
        headers["Authorization"] = f"Bearer {api_key}"
    data = json.dumps(probe.body).encode("utf-8") if probe.body is not None else None
    request = urllib.request.Request(probe.url, data=data, headers=headers, method=probe.method)
    start = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response.read(512)
            return ProbeResult(probe.name, str(response.status), time.monotonic() - start, False, "")
    except urllib.error.HTTPError as exc:
        try:
            exc.read(512)
        except Exception:
            _ = None
        return ProbeResult(probe.name, str(exc.code), time.monotonic() - start, False, "")
    except TimeoutError:
        return ProbeResult(probe.name, "timeout", time.monotonic() - start, True, probe.name)
    except urllib.error.URLError as exc:
        reason = exc.reason
        is_timeout = isinstance(reason, TimeoutError) or "timed out" in str(reason).lower()
        return ProbeResult(
            probe.name,
            "timeout" if is_timeout else "error",
            time.monotonic() - start,
            is_timeout,
            probe.name if is_timeout else f"error: {type(reason).__name__}",
        )
    except OSError as exc:
        is_timeout = "timed out" in str(exc).lower()
        return ProbeResult(
            probe.name,
            "timeout" if is_timeout else "error",
            time.monotonic() - start,
            is_timeout,
            probe.name if is_timeout else f"error: {type(exc).__name__}",
        )


def build_probes(search_url: str) -> list[Probe]:
    base_body = {"q": "csv", "k": 1}
    return [
        Probe("GET /health public", "GET", health_url(search_url), None, False),
        Probe(
            "POST /search sans token",
            "POST",
            search_url,
            {**base_body, "collection": "nsi_corpus", "include_documents": False},
            False,
        ),
        Probe(
            "POST /search token nsi_corpus no_docs",
            "POST",
            search_url,
            {**base_body, "collection": "nsi_corpus", "include_documents": False},
            True,
        ),
        Probe(
            "POST /search token rag_education no_docs",
            "POST",
            search_url,
            {**base_body, "collection": "rag_education", "include_documents": False},
            True,
        ),
        Probe(
            "POST /search token nsi_corpus docs",
            "POST",
            search_url,
            {**base_body, "collection": "nsi_corpus", "include_documents": True},
            True,
        ),
    ]


def main() -> int:
    if not ENV_FILE.exists():
        print("RAG_TIMEOUT_DIAG_SKIPPED_NO_CONFIG")
        return 0
    env = parse_env(ENV_FILE)
    search_url = env.get("RAG_API_BASE_URL", "")
    api_key = env.get("RAG_API_KEY", "")
    if not search_url or not api_key:
        print("RAG_TIMEOUT_DIAG_CONFIG_INVALID", file=sys.stderr)
        print("- RAG_API_BASE_URL ou RAG_API_KEY manquant", file=sys.stderr)
        return 1

    print("RAG_TIMEOUT_DIAG_RESULTS")
    results = [run_probe(probe, api_key, DEFAULT_TIMEOUT) for probe in build_probes(search_url)]
    timed_out = False
    for result in results:
        timed_out = timed_out or result.timeout
        blocking = result.blocking_step or "-"
        print(
            f"- {result.name}: HTTP={result.http_code} "
            f"duration={result.duration:.3f}s timeout={str(result.timeout).lower()} "
            f"blocking_step={blocking}"
        )
    if timed_out:
        print("RAG_TIMEOUT_DIAG_BLOCKED")
        return 1
    print("RAG_TIMEOUT_DIAG_NO_TIMEOUT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
