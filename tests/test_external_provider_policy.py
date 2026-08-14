from __future__ import annotations

import ast
import hashlib
import posixpath
import re
import shlex
import socket
import subprocess
import tomllib
import urllib.request
from collections.abc import Iterable, Mapping
from pathlib import Path, PurePosixPath

import pytest
import yaml
from packaging.requirements import InvalidRequirement, Requirement


ROOT = Path(__file__).resolve().parents[1]

CODE_PATHS = (
    "nexus_external/__init__.py",
    "nexus_external/openrouter_client.py",
    "nexus_external/classification.py",
    "Mathematiques/manuel-maths/scripts/ingest.py",
    "NSI/scripts/ingest.py",
    "NSI/corpus_nsi/scripts/judge_campaign.py",
    "NSI/corpus_nsi/scripts/substance_judge.py",
    "NSI/corpus_nsi/scripts/run_substance_judge.py",
    "NSI/corpus_nsi/scripts/check_rag_config.py",
    "NSI/corpus_nsi/scripts/rebuild_inventory.py",
    "NSI/corpus_nsi/scripts/check_rag_freshness.py",
    "NSI/corpus_nsi/scripts/ingest_nsi_corpus.py",
    "NSI/corpus_nsi/scripts/rag_diagnose_search_timeout.py",
    "NSI/corpus_nsi/scripts/rag_ingest_server.py",
    "NSI/corpus_nsi/scripts/rag_query_example.py",
    "NSI/corpus_nsi/scripts/rag_smoke_test.py",
)

CONFIGURATION_PATHS = (
    "Mathematiques/manuel-maths/.env.example",
    "NSI/.env.example",
    "NSI/corpus_nsi/.env.rag.example",
    "NSI/corpus_nsi/rag_config.example.yml",
    "Mathematiques/manuel-maths/requirements.txt",
    "NSI/requirements.txt",
    "NSI/corpus_nsi/requirements.txt",
    "requirements-ci-audit.txt",
    "pyproject.toml",
    "Mathematiques/manuel-maths/Makefile",
    "NSI/Makefile",
    "NSI/corpus_nsi/Makefile",
    ".github/workflows/ci-audit-collection.yml",
    ".github/workflows/ci-mathematiques.yml",
    ".github/workflows/ci-nsi.yml",
    "NSI/corpus_nsi/.github/workflows/ci.yml",
)

TEST_PATHS = (
    "tests/test_openrouter_client.py",
    "tests/test_openrouter_classification.py",
    "tests/test_external_provider_policy.py",
    "Mathematiques/manuel-maths/tests/test_ingest_openrouter.py",
    "NSI/tests/test_ingest_openrouter.py",
    "NSI/corpus_nsi/tests/test_openrouter_judges.py",
    "NSI/corpus_nsi/tests/test_manifest_separation.py",
    "NSI/corpus_nsi/tests/test_rag_governance_and_indexes.py",
    "NSI/corpus_nsi/tests/test_secret_guard.py",
    "NSI/corpus_nsi/tests/test_substance_judge_pipeline.py",
    "NSI/corpus_nsi/tests/test_substance_hardened.py",
    "NSI/corpus_nsi/tests/test_judge_collection_barriers.py",
    "NSI/corpus_nsi/tests/test_policy_checker_ast.py",
)

AUTHORITY_AND_GUIDE_PATHS = (
    "AGENTS.md",
    ".agents/skills/nexus-manual-quality/SKILL.md",
    "CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md",
    "README.md",
    "Mathematiques/PROMPT_MISSION_AUTONOME.md",
    "Mathematiques/workflow_production_manuel.md",
    "Mathematiques/manuel-maths/README.md",
    "Mathematiques/manuel-maths/CAHIER_DES_CHARGES.md",
    "Mathematiques/manuel-maths/docs/02_workflow_production.md",
    "Mathematiques/manuel-maths/docs/03_architecture_technique.md",
    "Mathematiques/manuel-maths/CLAUDE.md",
    "Mathematiques/manuel-maths/docs/04_guide_agents.md",
    "Mathematiques/manuel-maths/.claude/commands/verifier.md",
    "NSI/CAHIER_DES_CHARGES.md",
    "NSI/docs/02_workflow_production.md",
    "NSI/docs/03_architecture_technique.md",
    "NSI/docs/04_guide_agents.md",
    "NSI/.claude/commands/verifier.md",
    "NSI/corpus_nsi/README.md",
    "NSI/corpus_nsi/rag_connection.md",
    "NSI/corpus_nsi/substance_pipeline.md",
    "NSI/corpus_nsi/docs/enrichment_roadmap.md",
    "docs/superpowers/specs/2026-08-13-openrouter-only-external-provider-design.md",
)

ACTIVE_AGENT_GUIDE_PATHS = (
    "Mathematiques/manuel-maths/CLAUDE.md",
    "Mathematiques/manuel-maths/docs/04_guide_agents.md",
    "Mathematiques/manuel-maths/.claude/commands/verifier.md",
    "NSI/docs/04_guide_agents.md",
    "NSI/.claude/commands/verifier.md",
)

INVENTORY_PATHS = (
    "NSI/corpus_nsi/manifest.csv",
    "NSI/corpus_nsi/manifest_tooling.csv",
    "NSI/corpus_nsi/inventory_report.md",
    "NSI/corpus_nsi/duplicates_report.md",
)

CANONICAL_ACTIVE_PATHS = (
    *CODE_PATHS,
    *CONFIGURATION_PATHS,
    *TEST_PATHS,
    *AUTHORITY_AND_GUIDE_PATHS,
    *INVENTORY_PATHS,
)

RAG_TRANSPORT_PATHS = (
    "NSI/corpus_nsi/scripts/check_rag_freshness.py",
    "NSI/corpus_nsi/scripts/ingest_nsi_corpus.py",
    "NSI/corpus_nsi/scripts/rag_diagnose_search_timeout.py",
    "NSI/corpus_nsi/scripts/rag_ingest.py",
    "NSI/corpus_nsi/scripts/rag_ingest_server.py",
    "NSI/corpus_nsi/scripts/rag_smoke_test.py",
    "NSI/corpus_nsi/scripts/substance_judge.py",
)

APPROVED_LLM_CONFIGURATION_CONTRACT = {
    "Mathematiques/manuel-maths/.env.example": {
        "EMBEDDING_MODEL=BAAI/bge-m3",
        "OPENROUTER_API_KEY=",
        "OPENROUTER_MODEL=",
        "RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2",
    },
    "NSI/.env.example": {
        "EMBEDDING_MODEL=BAAI/bge-m3",
        "OPENROUTER_API_KEY=",
        "OPENROUTER_MODEL=",
        "RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2",
    },
    "NSI/corpus_nsi/.env.rag.example": {
        "EMBEDDING_API_KEY=",
        "EMBEDDING_BASE_URL=",
        "EMBEDDING_MODEL=nomic-embed-text",
        "OPENROUTER_API_KEY=",
        "OPENROUTER_MODEL=",
        "RAG_API_BASE_URL=https://rag-api.nexusreussite.academy/search",
        "RAG_API_KEY=",
        "VECTOR_DB_API_KEY=",
        "VECTOR_DB_URL=",
    },
    "NSI/corpus_nsi/rag_config.example.yml": {
        'base_url: "https://rag-api.nexusreussite.academy/search"',
        "base_url_env: EMBEDDING_BASE_URL",
        "model: nomic-embed-text",
    },
}

APPROVED_LLM_STRUCTURED_CONTRACT = {
    "NSI/corpus_nsi/rag_config.example.yml": {
        "api.base_url='https://rag-api.nexusreussite.academy/search'",
        "embedding.base_url_env='EMBEDDING_BASE_URL'",
        "embedding.model='nomic-embed-text'",
    },
}

SUBSTANCE_RAG_PATH = "NSI/corpus_nsi/scripts/substance_judge.py"

CALLER_PATHS = (
    "Mathematiques/manuel-maths/scripts/ingest.py",
    "NSI/scripts/ingest.py",
    "NSI/corpus_nsi/scripts/judge_campaign.py",
    "NSI/corpus_nsi/scripts/substance_judge.py",
    "NSI/corpus_nsi/scripts/run_substance_judge.py",
)

CANONICAL_PROVIDER_SURFACES = tuple(
    dict.fromkeys((*CODE_PATHS, *CONFIGURATION_PATHS, *TEST_PATHS))
)

HISTORICAL_NAMESPACE_PREFIXES = (
    "audit/",
    "docs/codex/",
    "docs/superpowers/plans/",
    "docs/superpowers/specs/",
    "NSI/corpus_nsi/reports/",
    "NSI/corpus_nsi/substance_reviews/",
)

HISTORICAL_EXPLICIT_PATHS = {
    "NSI/corpus_nsi/docs/judge_campaign_plan.md",
}

CURRENT_OPENROUTER_SPEC_PATH = (
    "docs/superpowers/specs/"
    "2026-08-13-openrouter-only-external-provider-design.md"
)
CURRENT_OPENROUTER_PLAN_PATH = (
    "docs/superpowers/plans/"
    "2026-08-13-openrouter-only-external-provider.md"
)
HISTORICAL_ACTIVE_EXCLUSIONS = frozenset(
    {CURRENT_OPENROUTER_PLAN_PATH, CURRENT_OPENROUTER_SPEC_PATH}
)
CURRENT_SPEC_LOCAL_LLM_HISTORICAL_LINES = {
    "partir de `LOCAL_LLM_BASE_URL` et peut donc atteindre une URL arbitraire.",
    (
        "Les variables `LOCAL_LLM_ENGINE`, `LOCAL_LLM_BASE_URL`, "
        "`LOCAL_LLM_MODEL` et"
    ),
    "`LOCAL_LLM_API_KEY` disparaissent de la configuration active. Aucun endpoint",
}
CURRENT_SPEC_SECTION_9_CHUTES_LINES = {
    "- `audit/chutes/**` ;",
    "`audit/openrouter/`. Aucun nouvel artefact n'est écrit sous `audit/chutes/`.",
}
HISTORICAL_SNAPSHOT_COUNT = 389
HISTORICAL_SNAPSHOT_SHA256 = (
    "71358d1f796a8fc83f2e94a681d313ef81d95a0034c17bdc43a97d458ff7f7d5"
)
HISTORICAL_BASELINE_COMMIT = "89a87253aef6ddea07d5639e5910330ebbf5c358"


def _historical_tree_at_commit(revision: str) -> dict[str, str]:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "ls-tree", "-r", "-z", revision],
        check=True,
        capture_output=True,
    )
    tree: dict[str, str] = {}
    for raw in completed.stdout.split(b"\0"):
        if not raw:
            continue
        metadata, raw_path = raw.split(b"\t", maxsplit=1)
        _mode, object_type, object_id = metadata.split(b" ", maxsplit=2)
        path = raw_path.decode("utf-8")
        if object_type != b"blob":
            continue
        if path in HISTORICAL_EXPLICIT_PATHS or path.startswith(
            HISTORICAL_NAMESPACE_PREFIXES
        ):
            tree[path] = object_id.decode("ascii")
    return tree


HISTORICAL_BASELINE_BLOBS = _historical_tree_at_commit(
    HISTORICAL_BASELINE_COMMIT
)
DISCOVERY_HISTORICAL_PATH_SNAPSHOT = frozenset(HISTORICAL_BASELINE_BLOBS)

TARGETED_SCAN_PATHS = (
    *CALLER_PATHS,
    "NSI/corpus_nsi/scripts/check_rag_config.py",
    *CONFIGURATION_PATHS,
    *AUTHORITY_AND_GUIDE_PATHS,
    *INVENTORY_PATHS,
)

CATALOG_AUTOMATION_PATHS = tuple(
    dict.fromkeys(
        (
            *CALLER_PATHS,
            "NSI/corpus_nsi/scripts/check_rag_config.py",
            "NSI/corpus_nsi/scripts/rebuild_inventory.py",
            *RAG_TRANSPORT_PATHS,
            "Mathematiques/manuel-maths/Makefile",
            "NSI/Makefile",
            "NSI/corpus_nsi/Makefile",
            ".github/workflows/ci-audit-collection.yml",
            ".github/workflows/ci-mathematiques.yml",
            ".github/workflows/ci-nsi.yml",
            "NSI/corpus_nsi/.github/workflows/ci.yml",
            *TEST_PATHS,
        )
    )
)

LOCAL_LLM_SCAN_PATHS = (
    *CALLER_PATHS,
    "NSI/corpus_nsi/scripts/check_rag_config.py",
    "NSI/corpus_nsi/.env.rag.example",
    "NSI/corpus_nsi/rag_config.example.yml",
    *AUTHORITY_AND_GUIDE_PATHS,
)

SHARED_CLIENT_PATH = "nexus_external/openrouter_client.py"

PROVIDER_SDK_PREFIXES = (
    "anthropic",
    "chutes",
    "cohere",
    "google.generativeai",
    "groq",
    "mistralai",
    "openai",
)

FORBIDDEN_PROVIDER_PACKAGES = frozenset(
    {
        "anthropic",
        "chutes",
        "cohere",
        "google-generativeai",
        "groq",
        "mistralai",
        "openai",
    }
)

HTTP_STACK_PREFIXES = (
    "aiohttp",
    "http.client",
    "httpx",
    "requests",
    "urllib.request",
    "urllib3",
)

NETWORK_IMPORT_PREFIXES = (
    *HTTP_STACK_PREFIXES,
    "socket",
    "urllib.robotparser",
)

NETWORK_SURFACE_REGISTRY = {
    "Mathematiques/manuel-maths/scripts/crawl.py": {
        "reason": "crawler limité aux sources enregistrées et robots.txt",
        "endpoints": ("sources/registry.yaml", "robots.txt"),
        "ast_sha256": "5a053ab897f218afa4f61eb99cc01044e9fd64f8c85ce154a69260ed4d5d7730",
    },
    "Mathematiques/manuel-maths/tests/test_ingest_openrouter.py": {
        "reason": "tests hors ligne et garde socket de l'ingestion",
        "endpoints": ("loopback interdit", "mocks OpenRouter"),
        "ast_sha256": "e18a2eafb60656ce6f1a79dd548e370feb29ec0dee7d272bf91504eb23f2df94",
    },
    "NSI/corpus_nsi/scrapping_NSI/netpolicy.py": {
        "reason": "politique réseau du scraper pédagogique",
        "endpoints": ("sources autorisées", "robots.txt"),
        "ast_sha256": "ec398d271a4057acfdb08e32a95c6619a6487e08b134d6b22c4c840f9349130e",
    },
    "NSI/corpus_nsi/scrapping_NSI/scraper_nsi_v2.py": {
        "reason": "scraper pédagogique via netpolicy",
        "endpoints": ("sources autorisées",),
        "ast_sha256": "125475f29dc513b1f49b3c3d75a68637b619e60003b30649614cfff92cfddead",
    },
    "NSI/corpus_nsi/scrapping_NSI/test_netpolicy.py": {
        "reason": "tests hors ligne de netpolicy",
        "endpoints": ("mocks requests",),
        "ast_sha256": "b2fd29b12ac159e70dc25adba81bd74f329588143747c3b71c927cc48c8fb394",
    },
    "NSI/corpus_nsi/scrapping_NSI/test_scraper_nsi_v2.py": {
        "reason": "tests hors ligne du scraper",
        "endpoints": ("mocks requests",),
        "ast_sha256": "288efb49091366474fe0a94f32d5037fade478cf761cd70e64a369bde355f7fa",
    },
    "NSI/corpus_nsi/scripts/check_rag_freshness.py": {
        "reason": "contrôle de fraîcheur RAG",
        "endpoints": ("RAG_API_BASE_URL",),
        "ast_sha256": "aca937ca5112e80fbf6835a4eeff8a92ef1a49c01c3bb4688b55a9145f74e14a",
    },
    "NSI/corpus_nsi/scripts/ingest_nsi_corpus.py": {
        "reason": "ingestion embeddings et base vectorielle RAG",
        "endpoints": ("EMBEDDING_BASE_URL", "VECTOR_DB_URL"),
        "ast_sha256": "141ce28e5fe94ce071574408613a7046b6b693977054408b2775a89956286cf5",
    },
    "NSI/corpus_nsi/scripts/rag_diagnose_search_timeout.py": {
        "reason": "diagnostic borné du service RAG",
        "endpoints": ("RAG_API_BASE_URL",),
        "ast_sha256": "f190cdc3c8f099afb56b96c8e841e9287cbfb626e44d647eb3f2ac5e2bc7a35a",
    },
    "NSI/corpus_nsi/scripts/rag_ingest.py": {
        "reason": "client de collection vectorielle RAG",
        "endpoints": ("VECTOR_DB_URL",),
        "ast_sha256": "91456f9d437f96f7da47ef1577cffb29a72d4aff3bb6f6a674d7f94e8edd9f0d",
    },
    "NSI/corpus_nsi/scripts/rag_ingest_server.py": {
        "reason": "transport explicite embeddings et base vectorielle",
        "endpoints": ("EMBEDDING_BASE_URL", "VECTOR_DB_URL"),
        "ast_sha256": "68f02862d523058ee36b86539271340f2745e204db2155abf5e37b88d7bb7a59",
    },
    "NSI/corpus_nsi/scripts/rag_smoke_test.py": {
        "reason": "smoke RAG manuel et séparé",
        "endpoints": ("RAG_API_BASE_URL",),
        "ast_sha256": "6dbb04549879ed79084ca6e1d5688e4649fb5e68cbacb73f16c20d944b383a01",
    },
    "NSI/corpus_nsi/scripts/substance_judge.py": {
        "reason": "recherche RAG; LLM délégué au client partagé",
        "endpoints": ("RAG_API_BASE_URL",),
        "ast_sha256": "ccab44f6454a177cf24b17ec04ae70061ea5e05ea048ac5301d51016a1a6e1ff",
    },
    "NSI/corpus_nsi/tests/conftest.py": {
        "reason": "garde réseau globale des tests corpus",
        "endpoints": ("tout réseau interdit",),
        "ast_sha256": "6e20f29e3fee687d104a1681115e1d58bdcd106654476fdba2b25f519920c0f8",
    },
    "NSI/corpus_nsi/tests/test_manifest_separation.py": {
        "reason": "tests hors ligne avec garde socket",
        "endpoints": ("loopback interdit",),
        "ast_sha256": "cabac80e01b9cb180d74d2b98282b79fa309d513c0c01a751e565dd8b749ee6c",
    },
    "NSI/corpus_nsi/tests/test_openrouter_judges.py": {
        "reason": "tests hors ligne des juges et garde socket",
        "endpoints": ("loopback interdit", "mocks OpenRouter/RAG"),
        "ast_sha256": "5a1e554312c344bb260e4da13f23ab88f09d219f38121c7a243372971d6e0b99",
    },
    "NSI/corpus_nsi/tests/test_substance_judge_pipeline.py": {
        "reason": "tests hors ligne du pipeline substance",
        "endpoints": ("loopback interdit", "mocks RAG"),
        "ast_sha256": "457310f46aac5533c2f4748255d7784ffa66d487dc54f0e6fe43ae1c1b36ed66",
    },
    "NSI/scripts/crawl.py": {
        "reason": "crawler limité aux sources enregistrées et robots.txt",
        "endpoints": ("sources/registry.yaml", "robots.txt"),
        "ast_sha256": "5a053ab897f218afa4f61eb99cc01044e9fd64f8c85ce154a69260ed4d5d7730",
    },
    "NSI/tests/test_ingest_openrouter.py": {
        "reason": "tests hors ligne et garde socket de l'ingestion",
        "endpoints": ("loopback interdit", "mocks OpenRouter"),
        "ast_sha256": "5888753f547699ec3afbfb4ea98080946e3851078aa63a8f30176a370b493d5c",
    },
    "nexus_external/openrouter_client.py": {
        "reason": "unique transport LLM externe partagé",
        "endpoints": ("https://openrouter.ai/api/v1/chat/completions",),
        "ast_sha256": "f9725c0e72bfa63c7f4c6ed8a061229b01a7c0db298141aeac45e559fefe6098",
    },
    "tests/test_external_provider_policy.py": {
        "reason": "garde réseau et mutations hors ligne de la politique",
        "endpoints": ("loopback interdit", "fixtures uniquement"),
        "ast_sha256": "df559caae7d5583b6e46cb868aa4b7208c45497929b8b43efeb087118953368f",
    },
    "tests/test_openrouter_classification.py": {
        "reason": "tests hors ligne de classification OpenRouter",
        "endpoints": ("loopback interdit", "MockTransport"),
        "ast_sha256": "41b86c06f5c9a837f1aacd18539e11e49e58f5f2005f2bb7ba481e4a8f94623c",
    },
    "tests/test_openrouter_client.py": {
        "reason": "tests hors ligne du client OpenRouter",
        "endpoints": ("loopback interdit", "MockTransport"),
        "ast_sha256": "fbc8ac42009ffd0dd75adb61563cc454bf9dbbb10a0b14fc81b4fe5bf5d37db2",
    },
}


def _blocked_network(*args: object, **kwargs: object) -> None:
    raise AssertionError("network forbidden by external-provider policy tests")


@pytest.fixture(autouse=True)
def _forbid_network(monkeypatch: pytest.MonkeyPatch) -> Iterable[None]:
    monkeypatch.setattr(socket.socket, "connect", _blocked_network)
    monkeypatch.setattr(socket, "create_connection", _blocked_network)
    monkeypatch.setattr(urllib.request, "urlopen", _blocked_network)

    with socket.socket() as probe:
        with pytest.raises(AssertionError):
            probe.connect(("127.0.0.1", 9))
    with pytest.raises(AssertionError):
        socket.create_connection(("127.0.0.1", 9))
    with pytest.raises(AssertionError):
        urllib.request.urlopen("http://127.0.0.1:9")
    yield


def _path_issues(paths: Iterable[str]) -> tuple[list[str], list[str]]:
    requested = tuple(paths)
    missing = [path for path in requested if not (ROOT / path).is_file()]
    untracked = [
        path
        for path in requested
        if (ROOT / path).is_file()
        and subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "--error-unmatch", "--", path],
            check=False,
            capture_output=True,
            text=True,
        ).returncode
        != 0
    ]
    return missing, untracked


def _assert_paths_exist_and_are_tracked(paths: Iterable[str]) -> None:
    missing, untracked = _path_issues(paths)
    assert not missing, f"canonical active surfaces missing: {missing}"
    assert not untracked, f"canonical active surfaces not tracked: {untracked}"


def _tracked_sources(paths: Iterable[str]) -> dict[str, str]:
    requested = tuple(paths)
    _assert_paths_exist_and_are_tracked(requested)
    return {
        path: (ROOT / path).read_text(encoding="utf-8")
        for path in requested
    }


def _working_tree_sources(paths: Iterable[str]) -> dict[str, str]:
    requested = tuple(paths)
    return {
        path: (
            (ROOT / path).read_text(encoding="utf-8")
            if (ROOT / path).is_file()
            else ""
        )
        for path in requested
    }


def _git_tracked_paths() -> set[str]:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return {
        path.decode("utf-8")
        for path in completed.stdout.split(b"\0")
        if path
    }


def _historical_snapshot_digest(paths: Iterable[str]) -> str:
    payload = "\n".join(sorted(paths)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _git_blob_oid(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def _is_protected_historical_path(path: str) -> bool:
    if path in HISTORICAL_ACTIVE_EXCLUSIONS:
        return False
    snapshot_matches = (
        len(DISCOVERY_HISTORICAL_PATH_SNAPSHOT) == HISTORICAL_SNAPSHOT_COUNT
        and _historical_snapshot_digest(DISCOVERY_HISTORICAL_PATH_SNAPSHOT)
        == HISTORICAL_SNAPSHOT_SHA256
    )
    return snapshot_matches and path in DISCOVERY_HISTORICAL_PATH_SNAPSHOT


def _historical_blob_drift(path: str, raw: bytes) -> bool:
    if not _is_protected_historical_path(path):
        return False
    return _git_blob_oid(raw) != HISTORICAL_BASELINE_BLOBS[path]


def _is_new_historical_executable(path: str) -> bool:
    candidate = Path(path)
    return (
        path.startswith(HISTORICAL_NAMESPACE_PREFIXES)
        and path not in DISCOVERY_HISTORICAL_PATH_SNAPSHOT
        and (
            candidate.suffix in {".py", ".sh", ".toml", ".yaml", ".yml"}
            or candidate.name == "Makefile"
        )
    )


def _is_active_discovery_candidate(path: str) -> bool:
    if _is_protected_historical_path(path):
        return False
    candidate = Path(path)
    return (
        candidate.suffix in {".py", ".sh", ".toml", ".yaml", ".yml"}
        or candidate.name == "Makefile"
        or candidate.name.startswith(".env")
        or (
            candidate.name.startswith("requirements")
            and candidate.suffix == ".txt"
        )
    )


def _module_path_candidates(importer: str, node: ast.AST) -> tuple[str, ...]:
    importer_dir = Path(importer).parent
    module = ""
    level = 0
    if isinstance(node, ast.Import):
        return ()
    if isinstance(node, ast.ImportFrom):
        module = node.module or ""
        level = node.level
    if not module and level == 0:
        return ()
    module_path = Path(*module.split(".")) if module else Path()
    bases: list[Path] = []
    if level:
        base = importer_dir
        for _ in range(level - 1):
            base = base.parent
        bases.append(base)
    else:
        base = importer_dir
        while str(base) not in {"", "."}:
            bases.append(base)
            base = base.parent
        bases.append(Path())
    candidates: list[str] = []
    for base in bases:
        target = base / module_path
        candidates.extend((f"{target}.py", str(target / "__init__.py")))
    return tuple(dict.fromkeys(candidates))


def _import_edges(
    importer: str,
    source: str,
    available_paths: set[str],
) -> tuple[set[tuple[str, str]], list[str]]:
    tree = ast.parse(source)
    edges: set[tuple[str, str]] = set()
    issues: list[str] = []
    local_roots = {"common", "nexus_external", "scripts"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                synthetic = ast.ImportFrom(module=alias.name, names=[], level=0)
                candidates = _module_path_candidates(importer, synthetic)
                resolved = next(
                    (candidate for candidate in candidates if candidate in available_paths),
                    None,
                )
                if resolved is not None:
                    edges.add((importer, resolved))
                elif parts[0] in local_roots:
                    issues.append(f"unresolved local import {importer}:{alias.name}")
        elif isinstance(node, ast.ImportFrom):
            candidates = _module_path_candidates(importer, node)
            resolved = next(
                (candidate for candidate in candidates if candidate in available_paths),
                None,
            )
            if resolved is not None:
                edges.add((importer, resolved))
                if resolved.endswith("/__init__.py"):
                    package_root = Path(resolved).parent
                    for alias in node.names:
                        if alias.name == "*":
                            continue
                        alias_path = package_root / Path(*alias.name.split("."))
                        submodule_candidates = (
                            f"{alias_path}.py",
                            str(alias_path / "__init__.py"),
                        )
                        submodule = next(
                            (
                                candidate
                                for candidate in submodule_candidates
                                if candidate in available_paths
                            ),
                            None,
                        )
                        if submodule is not None:
                            edges.add((importer, submodule))
            else:
                root = (node.module or "").split(".", maxsplit=1)[0]
                if node.level or root in local_roots:
                    issues.append(
                        f"unresolved local import {importer}:{node.module or '.'}"
                    )
    return edges, issues


def _is_requirement_entrypoint(path: str) -> bool:
    candidate = PurePosixPath(path)
    return candidate.suffix == ".txt" and candidate.name.startswith(
        "requirements"
    )


def _requirement_include_reference(line: str) -> tuple[bool, str | None]:
    try:
        tokens = shlex.split(line, comments=True, posix=True)
    except ValueError:
        stripped = line.lstrip()
        return stripped.startswith(("-r", "--requirement")), None
    if not tokens:
        return False, None
    option = tokens[0]
    if option in {"-r", "--requirement"}:
        return True, tokens[1] if len(tokens) == 2 else None
    for prefix in ("--requirement=", "-r="):
        if option.startswith(prefix):
            return True, option[len(prefix) :] if len(tokens) == 1 else None
    if option.startswith("-r") and len(option) > 2:
        return True, option[2:] if len(tokens) == 1 else None
    return False, None


def _resolve_requirement_include(path: str, reference: str) -> str | None:
    if not reference or "\0" in reference or "\\" in reference:
        return None
    included = PurePosixPath(reference)
    if included.is_absolute():
        return None
    normalized = posixpath.normpath(
        str(PurePosixPath(path).parent / included)
    )
    if normalized == ".." or normalized.startswith("../"):
        return None
    return normalized


def _discover_provider_surfaces(
    *,
    source_overrides: Mapping[str, str] | None = None,
    tracked_paths: set[str] | None = None,
) -> tuple[dict[str, str], set[tuple[str, str]], list[str]]:
    overrides = dict(source_overrides or {})
    tracked = set(tracked_paths) if tracked_paths is not None else _git_tracked_paths()
    available = tracked | set(overrides) | {
        path
        for path in CANONICAL_PROVIDER_SURFACES
        if (ROOT / path).is_file()
    }
    active_candidates = {
        path for path in tracked | set(overrides) if _is_active_discovery_candidate(path)
    }
    requirement_files = {
        path for path in active_candidates if _is_requirement_entrypoint(path)
    }
    queue = sorted(set(CANONICAL_PROVIDER_SURFACES) | active_candidates)
    discovered: dict[str, str] = {}
    edges: set[tuple[str, str]] = set()
    issues: list[str] = []
    while queue:
        path = queue.pop(0)
        if path in discovered:
            continue
        if _is_protected_historical_path(path):
            issues.append(f"active discovery reached protected history: {path}")
            continue
        if path in overrides:
            source = overrides[path]
        elif (ROOT / path).is_file():
            source = (ROOT / path).read_text(encoding="utf-8")
        else:
            source = ""
            issues.append(f"missing active surface: {path}")
        discovered[path] = source
        if path not in tracked:
            issues.append(f"untracked active surface: {path}")
        if _is_new_historical_executable(path):
            issues.append(f"new executable in historical namespace: {path}")
        if path in requirement_files:
            for line_number, line in enumerate(source.splitlines(), start=1):
                is_include, reference = _requirement_include_reference(line)
                if not is_include:
                    continue
                target = (
                    _resolve_requirement_include(path, reference)
                    if reference is not None
                    else None
                )
                if target is None:
                    issues.append(
                        f"invalid requirement include {path}:{line_number}"
                    )
                    continue
                if target not in available:
                    issues.append(
                        f"missing requirement include {path}:{line_number}:{target}"
                    )
                    continue
                requirement_files.add(target)
                if target not in discovered and target not in queue:
                    queue.append(target)
        if not source or not path.endswith(".py"):
            continue
        try:
            new_edges, import_issues = _import_edges(path, source, available)
        except SyntaxError as exc:
            issues.append(f"syntax error in active surface {path}:{exc.lineno}")
            continue
        if path in CANONICAL_PROVIDER_SURFACES:
            issues.extend(import_issues)
        for edge in new_edges:
            edges.add(edge)
            imported = edge[1]
            if _is_protected_historical_path(imported):
                issues.append(f"active import reached protected history: {edge}")
            elif imported not in discovered:
                queue.append(imported)
    return discovered, edges, issues


def _dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _dotted_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def _constant_strings(tree: ast.AST) -> dict[str, set[str]]:
    constants: dict[str, set[str]] = {}
    for node in getattr(tree, "body", ()):
        target: ast.AST | None = None
        value: ast.AST | None = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            value = node.value
        elif isinstance(node, ast.AnnAssign):
            target = node.target
            value = node.value
        if isinstance(target, ast.Name) and value is not None:
            constants[target.id] = set(_string_fragments(value, {}))
    return constants


def _string_fragments(
    node: ast.AST,
    constants: Mapping[str, set[str]],
) -> Iterable[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        yield node.value
        return
    if isinstance(node, ast.Name):
        yield from constants.get(node.id, ())
        return
    for child in ast.iter_child_nodes(node):
        yield from _string_fragments(child, constants)


def _is_provider_sdk_name(name: str) -> bool:
    return any(
        name == prefix or name.startswith(f"{prefix}.")
        for prefix in PROVIDER_SDK_PREFIXES
    )


def _canonical_network_ast_digest(source: str) -> str:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values, strict=True):
            if (
                isinstance(key, ast.Constant)
                and key.value == "ast_sha256"
                and isinstance(value, ast.Constant)
                and isinstance(value.value, str)
            ):
                value.value = "<normalized-network-contract-digest>"
    canonical = ast.dump(tree, annotate_fields=True, include_attributes=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _network_surface_signals(tree: ast.AST) -> set[str]:
    signals: set[str] = set()
    constants = _constant_strings(tree)
    unsafe_methods = {"delete", "patch", "post", "put", "request"}
    network_prefixes = (*NETWORK_IMPORT_PREFIXES, *PROVIDER_SDK_PREFIXES)
    importlib_aliases = {"importlib"}
    import_module_aliases: set[str] = set()
    subprocess_aliases = {"subprocess"}
    os_aliases = {"os"}
    shell_call_aliases: set[str] = set()
    subprocess_calls = {
        "call",
        "check_call",
        "check_output",
        "Popen",
        "run",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "importlib":
                    importlib_aliases.add(alias.asname or alias.name)
                elif alias.name == "subprocess":
                    subprocess_aliases.add(alias.asname or alias.name)
                elif alias.name == "os":
                    os_aliases.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module == "importlib":
                for alias in node.names:
                    if alias.name == "import_module":
                        import_module_aliases.add(alias.asname or alias.name)
            elif node.module == "subprocess":
                shell_call_aliases.update(
                    alias.asname or alias.name
                    for alias in node.names
                    if alias.name in subprocess_calls
                )
            elif node.module == "os":
                shell_call_aliases.update(
                    alias.asname or alias.name
                    for alias in node.names
                    if alias.name == "system"
                )

    receiver_markers = {"client", "gateway", "transport"}
    network_receivers: set[str] = set()
    mapping_receivers: set[str] = set()
    assignments: list[tuple[str, ast.AST]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for argument in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs):
                if argument.arg.casefold() in receiver_markers:
                    network_receivers.add(argument.arg)
        targets: tuple[ast.AST, ...] = ()
        value: ast.AST | None = None
        if isinstance(node, ast.Assign):
            targets = tuple(node.targets)
            value = node.value
        elif isinstance(node, ast.AnnAssign):
            targets = (node.target,)
            value = node.value
        if value is None:
            continue
        for target in targets:
            if not isinstance(target, ast.Name):
                continue
            assignments.append((target.id, value))
            if isinstance(value, ast.Dict) or (
                isinstance(value, ast.Call) and _dotted_name(value.func) == "dict"
            ):
                mapping_receivers.add(target.id)
            elif target.id.casefold() in receiver_markers:
                network_receivers.add(target.id)

    changed = True
    while changed:
        changed = False
        for target, value in assignments:
            if target in mapping_receivers or not isinstance(value, ast.Name):
                continue
            if value.id in network_receivers and target not in network_receivers:
                network_receivers.add(target)
                changed = True

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if any(
                    alias.name == prefix or alias.name.startswith(f"{prefix}.")
                    for prefix in network_prefixes
                ):
                    signals.add(f"import:{alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imported_names = {
                f"{module}.{alias.name}" for alias in node.names if module
            }
            if any(
                module == prefix or module.startswith(f"{prefix}.")
                for prefix in network_prefixes
            ) or any(
                imported == prefix or imported.startswith(f"{prefix}.")
                for imported in imported_names
                for prefix in network_prefixes
            ):
                signals.add(f"import:{module}")
        elif isinstance(node, ast.Attribute):
            dotted = _dotted_name(node)
            if any(
                dotted == prefix or dotted.startswith(f"{prefix}.")
                for prefix in network_prefixes
            ):
                signals.add(f"reference:{dotted}")
        elif isinstance(node, ast.Call):
            call_name = _dotted_name(node.func)
            shell_execution = call_name in shell_call_aliases
            if isinstance(node.func, ast.Attribute):
                receiver = _dotted_name(node.func.value)
                shell_execution = shell_execution or (
                    receiver in subprocess_aliases
                    and node.func.attr in subprocess_calls
                ) or (
                    receiver in os_aliases and node.func.attr == "system"
                )
            if shell_execution:
                fragments = tuple(
                    fragment
                    for candidate in (
                        *node.args,
                        *(keyword.value for keyword in node.keywords),
                    )
                    for fragment in _string_fragments(candidate, constants)
                )
                command = " ".join(fragments)
                has_provider_destination = any(
                    marker in fragment.casefold()
                    for fragment in fragments
                    for marker in (
                        "api.anthropic.com",
                        "openrouter",
                        "other_provider",
                        "provider.invalid",
                        "provider_url",
                        "/chat/completions",
                        "/v1/messages",
                    )
                )
                if (
                    _shell_command_has_network_primitive(command)
                    and has_provider_destination
                ):
                    signals.add("shell-provider-transport")
            if isinstance(node.func, ast.Name) and node.func.id == "__import__":
                if node.args and isinstance(node.args[0], ast.Constant):
                    imported = node.args[0].value
                    if isinstance(imported, str) and any(
                        imported == prefix or imported.startswith(f"{prefix}.")
                        for prefix in network_prefixes
                    ):
                        signals.add(f"dynamic-import:{imported}")
            dynamic_import = (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "import_module"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in importlib_aliases
            ) or (
                isinstance(node.func, ast.Name)
                and node.func.id in import_module_aliases
            )
            if dynamic_import and node.args and isinstance(
                node.args[0], ast.Constant
            ):
                imported = node.args[0].value
                if isinstance(imported, str) and any(
                    imported == prefix or imported.startswith(f"{prefix}.")
                    for prefix in network_prefixes
                ):
                    signals.add(f"dynamic-import:{imported}")
            if isinstance(node.func, ast.Attribute):
                method = node.func.attr
                if method in unsafe_methods:
                    signals.add(f"http-verb:{method}")
                elif method == "get":
                    receiver = _dotted_name(node.func.value)
                    receiver_root = receiver.split(".", maxsplit=1)[0]
                    receiver_leaf = receiver.rsplit(".", maxsplit=1)[-1].casefold()
                    is_network_receiver = (
                        receiver_root in network_receivers
                        or receiver_leaf in receiver_markers
                    ) and receiver_root not in mapping_receivers
                    has_network_destination = _call_has_destination(
                        node,
                        {},
                        (
                            "http://",
                            "https://",
                            "other_provider",
                            "provider_url",
                            "service_url",
                        ),
                    )
                    if is_network_receiver or has_network_destination:
                        signals.add("http-verb:get")
    return signals


def _call_has_destination(
    call: ast.Call,
    constants: Mapping[str, set[str]],
    markers: Iterable[str],
) -> bool:
    candidates = (*call.args, *(keyword.value for keyword in call.keywords))
    return any(
        marker in fragment.casefold()
        for candidate in candidates
        for fragment in _string_fragments(candidate, constants)
        for marker in markers
    )


def _configuration_assignment(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    matched = re.match(
        r"^([A-Za-z0-9_.-]+)\s*(?::|\?=|:=|\+=|=)\s*(.*?)\s*$",
        stripped,
    )
    if matched is None:
        return None
    return matched.group(1), stripped


def _is_llm_configuration_key(key: str) -> bool:
    lowered = key.casefold()
    if any(marker in lowered for marker in ("endpoint", "llm", "model", "provider")):
        return True
    if lowered in {"api_url", "base_url", "base_url_env"}:
        return True
    if lowered.endswith(("_api_url", "_base_url", "_endpoint")):
        return True
    return lowered.startswith(
        ("embedding_", "openrouter_", "rag_", "reranker_", "vector_db_")
    ) and lowered.endswith(("api_key", "base_url", "url"))


def _forbidden_provider_requirement(requirement: str) -> str | None:
    try:
        package = Requirement(requirement).name
    except InvalidRequirement:
        matched = re.match(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)", requirement)
        if matched is None:
            return None
        package = matched.group(1)
    normalized = package.casefold().replace("_", "-").replace(".", "-")
    if normalized in FORBIDDEN_PROVIDER_PACKAGES:
        return normalized
    return None


def _shell_command_has_network_primitive(command: str) -> bool:
    try:
        tokens = shlex.split(command, comments=True, posix=True)
    except ValueError:
        return bool(
            re.search(
                r"(?<![A-Za-z0-9_.-])"
                r"(?:curl|http|httpie|https|nc|netcat|wget)"
                r"(?![A-Za-z0-9_.-])",
                command,
            )
        )
    network_commands = {"curl", "http", "httpie", "https", "nc", "netcat", "wget"}
    if any(Path(token).name.casefold() in network_commands for token in tokens):
        return True
    for index, token in enumerate(tokens[:-2]):
        if Path(token).name.casefold() not in {"bash", "sh"}:
            continue
        if tokens[index + 1] == "-c" and _shell_command_has_network_primitive(
            tokens[index + 2]
        ):
            return True
    return False


def _configuration_provider_violations(path: str, source: str) -> list[str]:
    candidate = Path(path)
    structured_findings: set[str] = set()
    parsed: object | None = None
    try:
        if candidate.suffix in {".yaml", ".yml"}:
            parsed = yaml.safe_load(source)
        elif candidate.suffix == ".toml":
            parsed = tomllib.loads(source)
    except (tomllib.TOMLDecodeError, yaml.YAMLError) as exc:
        return [f"invalid structured configuration: {type(exc).__name__}"]

    def visit(value: object, trail: tuple[str, ...] = ()) -> None:
        if isinstance(value, Mapping):
            poetry_dependencies = (
                len(trail) >= 3
                and trail[:2] == ("tool", "poetry")
                and trail[-1]
                in {"dependencies", "dev-dependencies", "optional-dependencies"}
            )
            for raw_key, child in value.items():
                key = str(raw_key)
                child_trail = (*trail, key)
                if poetry_dependencies and _forbidden_provider_requirement(key):
                    structured_findings.add(
                        f"{'.'.join(child_trail)}={child!r}"
                    )
                if _is_llm_configuration_key(key):
                    structured_findings.add(
                        f"{'.'.join(child_trail)}={child!r}"
                    )
                if (
                    key.casefold() in {"command", "run", "script", "shell"}
                    and isinstance(child, str)
                    and _shell_command_has_network_primitive(child)
                ):
                    structured_findings.add(
                        f"{'.'.join(child_trail)}={child!r}"
                    )
                visit(child, child_trail)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, (*trail, f"[{index}]"))
        elif isinstance(value, str):
            provider_requirement = _forbidden_provider_requirement(value)
            if provider_requirement is not None or any(
                marker in value.casefold()
                for marker in (
                    "api.anthropic.com",
                    "other_provider",
                    "/chat/completions",
                    "/v1/messages",
                )
            ):
                structured_findings.add(f"{'.'.join(trail)}={value!r}")

    if parsed is not None:
        visit(parsed)
    observed = {
        normalized
        for line in source.splitlines()
        if (assignment := _configuration_assignment(line)) is not None
        for key, normalized in (assignment,)
        if _is_llm_configuration_key(key)
    }
    expected = APPROVED_LLM_CONFIGURATION_CONTRACT.get(path)
    if expected is None:
        findings = sorted(observed | structured_findings)
        return [f"unapproved provider configuration: {item}" for item in findings]
    if observed != expected:
        return [
            f"configuration={sorted(observed)}:expected={sorted(expected)}"
        ]
    expected_structured = APPROVED_LLM_STRUCTURED_CONTRACT.get(path, set())
    if structured_findings != expected_structured:
        return [
            f"structured={sorted(structured_findings)}:"
            f"expected={sorted(expected_structured)}"
        ]
    return []


def _requirements_graph_violations(
    sources: Mapping[str, str],
) -> dict[str, list[str]]:
    violations: dict[str, list[str]] = {}

    def visit(root: str, path: str, stack: tuple[str, ...]) -> None:
        if path in stack:
            violations.setdefault(root, []).append(
                f"requirement include cycle: {' -> '.join((*stack, path))}"
            )
            return
        source = sources.get(path)
        if source is None:
            violations.setdefault(root, []).append(
                f"missing requirement include: {path}"
            )
            return
        for line_number, line in enumerate(source.splitlines(), start=1):
            is_include, reference = _requirement_include_reference(line)
            if is_include:
                target = (
                    _resolve_requirement_include(path, reference)
                    if reference is not None
                    else None
                )
                if target is None:
                    violations.setdefault(root, []).append(
                        f"invalid requirement include: {path}:{line_number}"
                    )
                    continue
                visit(root, target, (*stack, path))
                continue
            requirement = line.split("#", maxsplit=1)[0].strip()
            if (
                requirement
                and _forbidden_provider_requirement(requirement) is not None
            ):
                violations.setdefault(root, []).append(
                    f"{path}:{line_number}:{requirement}"
                )

    for root in sorted(path for path in sources if _is_requirement_entrypoint(path)):
        visit(root, root, ())
    return violations


def _shell_network_violations(path: str, source: str) -> list[str]:
    candidate = Path(path)
    if candidate.suffix != ".sh" and candidate.name != "Makefile":
        return []
    violations: list[str] = []
    for line_number, line in enumerate(source.splitlines(), start=1):
        if candidate.name == "Makefile" and not line.startswith("\t"):
            continue
        if _shell_command_has_network_primitive(line.strip()):
            violations.append(f"{path}:{line_number}:network primitive")
    return violations


def _unlisted_transport_violations(sources: Mapping[str, str]) -> list[str]:
    violations: list[str] = []
    requirements_graph_violations = _requirements_graph_violations(sources)
    llm_destination_markers = (
        "api.anthropic.com",
        "/chat/completions",
        "/v1/messages",
    )
    for logical_path, source in sources.items():
        if not source:
            continue
        if not logical_path.endswith(".py"):
            is_active_candidate = _is_active_discovery_candidate(logical_path)
            config_violations = (
                _configuration_provider_violations(logical_path, source)
                if is_active_candidate
                else []
            )
            requirements_violations = requirements_graph_violations.get(
                logical_path,
                [],
            )
            shell_violations = _shell_network_violations(logical_path, source)
            has_llm_destination = is_active_candidate and any(
                marker in source.casefold() for marker in llm_destination_markers
            )
            if (
                config_violations
                or requirements_violations
                or shell_violations
                or has_llm_destination
            ):
                violations.append(logical_path)
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            violations.append(logical_path)
            continue
        signals = _network_surface_signals(tree)
        registered = NETWORK_SURFACE_REGISTRY.get(logical_path)
        if registered is not None:
            if (
                not signals
                or _canonical_network_ast_digest(source)
                != registered["ast_sha256"]
            ):
                violations.append(logical_path)
            continue
        if signals:
            violations.append(logical_path)
    return sorted(set(violations))


def _chutes_violations(sources: Mapping[str, bytes]) -> list[str]:
    approved_negative_lines = (
        re.compile(
            r"^\s*(?:[-*]\s*)?aucun nouvel appel (?:à )?chutes[.!]?\s*$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^\s*(?:[-*]\s*)?ne jamais utiliser chutes[.!]?\s*$",
            re.IGNORECASE,
        ),
    )
    violations: list[str] = []
    for logical_path, raw in sources.items():
        if _is_protected_historical_path(logical_path):
            if _historical_blob_drift(logical_path, raw):
                violations.append(f"{logical_path}:historical blob drift")
            continue
        in_spec_history = False
        lines = raw.decode("utf-8").splitlines()
        for line_number, line in enumerate(lines, start=1):
            if logical_path == CURRENT_OPENROUTER_SPEC_PATH:
                if line.startswith("## 9. "):
                    in_spec_history = True
                elif in_spec_history and line.startswith("## 10. "):
                    in_spec_history = False
                if (
                    in_spec_history
                    and line.strip() in CURRENT_SPEC_SECTION_9_CHUTES_LINES
                ):
                    continue
            lowered = line.casefold()
            if "chutes" not in lowered:
                continue
            if any(pattern.fullmatch(line) for pattern in approved_negative_lines):
                continue
            if any(
                marker in lowered
                for marker in (
                    "aucune consultation chutes",
                    "absence de chutes",
                    "consultations chutes cessent",
                    "n'ordonnent plus chutes",
                    "preuves historiques chutes",
                )
            ):
                continue
            violations.append(f"{logical_path}:{line_number}:{line.strip()}")
    return violations


def _catalog_violations(sources: Mapping[str, str]) -> list[str]:
    marker = "/api/v1/models"
    violations: list[str] = []
    shell_calls = {
        "os.system",
        "subprocess.call",
        "subprocess.check_call",
        "subprocess.check_output",
        "subprocess.Popen",
        "subprocess.run",
    }
    for path, source in sources.items():
        if marker not in source.casefold():
            continue
        if not path.endswith(".py"):
            violations.append(path)
            continue
        tree = ast.parse(source)
        constants = _constant_strings(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            call_name = _dotted_name(node.func)
            method = call_name.rsplit(".", maxsplit=1)[-1]
            is_network_call = "." in call_name and method in {
                "delete",
                "get",
                "open",
                "patch",
                "post",
                "put",
                "request",
                "urlopen",
            }
            if not (is_network_call or call_name in shell_calls):
                continue
            if _call_has_destination(node, constants, (marker,)):
                violations.append(path)
                break
    return sorted(set(violations))


def _expected_env_keys(source: str) -> set[str]:
    tree = ast.parse(source)
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        target = node.targets[0] if isinstance(node, ast.Assign) else node.target
        if not isinstance(target, ast.Name) or target.id != "EXPECTED_ENV":
            continue
        value = node.value
        if isinstance(value, ast.Dict):
            return {
                key.value
                for key in value.keys
                if isinstance(key, ast.Constant) and isinstance(key.value, str)
            }
    return set()


def test_policy_requires_every_canonical_active_surface() -> None:
    assert len(CANONICAL_ACTIVE_PATHS) == len(set(CANONICAL_ACTIVE_PATHS))
    assert len(AUTHORITY_AND_GUIDE_PATHS) == 23
    _assert_paths_exist_and_are_tracked(CANONICAL_ACTIVE_PATHS)


def test_active_agent_guides_prescribe_only_explicit_openrouter_model() -> None:
    assert set(ACTIVE_AGENT_GUIDE_PATHS) <= set(AUTHORITY_AND_GUIDE_PATHS)
    sources = _tracked_sources(ACTIVE_AGENT_GUIDE_PATHS)
    legacy_model = re.compile(
        r"\b(?:claude(?:-[a-z0-9._-]+)?|sonnet|opus|haiku|fable)\b",
        re.IGNORECASE,
    )
    violations: dict[str, list[str]] = {}
    for path, source in sources.items():
        lowered = source.casefold()
        missing = []
        if "openrouter" not in lowered:
            missing.append("OpenRouter")
        if "`openrouter_model`" not in lowered:
            missing.append("OPENROUTER_MODEL")
        if not re.search(r"aucun mod[eè]le[^\n]*implicit", lowered):
            missing.append("no implicit model")
        if "consultativ" not in lowered or "vérifi" not in lowered or "localement" not in lowered:
            missing.append("consultative/local verification")
        if "secret" not in lowered or "donnée personnelle" not in lowered:
            missing.append("no secret/PII")
        legacy = sorted(set(legacy_model.findall(source)))
        if missing or legacy:
            violations[path] = [*missing, *legacy]
    assert not violations, violations


def test_discovery_scans_tracked_standalone_provider_surface() -> None:
    standalone_path = "scripts/standalone_provider.py"
    standalone_source = (
        "import httpx\n"
        "httpx.post('https://provider.invalid/v1/chat/completions')\n"
    )
    simulated_sources, _edges, simulated_issues = _discover_provider_surfaces(
        source_overrides={standalone_path: standalone_source},
        tracked_paths=_git_tracked_paths() | {standalone_path},
    )
    assert standalone_path in simulated_sources
    assert standalone_path in _unlisted_transport_violations(simulated_sources)
    assert not simulated_issues, simulated_issues


def test_policy_rejects_injected_http_receiver_without_direct_import() -> None:
    standalone_path = "scripts/injected_client.py"
    standalone_source = (
        "def send(client):\n"
        "    return client.post('https://provider.invalid/v1/chat/completions')\n"
    )
    simulated_sources, _edges, simulated_issues = _discover_provider_surfaces(
        source_overrides={standalone_path: standalone_source},
        tracked_paths=_git_tracked_paths() | {standalone_path},
    )
    assert standalone_path in simulated_sources
    assert standalone_path in _unlisted_transport_violations(simulated_sources)
    assert not simulated_issues, simulated_issues


def test_policy_rejects_aliased_http_transport_inside_allowed_test() -> None:
    test_path = "tests/test_openrouter_client.py"
    aliased_source = (
        "import httpx as transport\n"
        "transport.post('https://provider.invalid/v1/chat/completions')\n"
    )
    assert test_path in TEST_PATHS
    assert test_path in _unlisted_transport_violations(
        {test_path: aliased_source}
    )


@pytest.mark.parametrize(
    ("suffix", "config_source"),
    (
        (
            "yml",
            "endpoint: https://provider.invalid/v1/generate\n"
            "model: forbidden-model\n",
        ),
        (
            "toml",
            'endpoint = "https://provider.invalid/v1/generate"\n'
            'model = "forbidden-model"\n',
        ),
    ),
)
def test_discovery_rejects_unlisted_llm_configuration(
    suffix: str,
    config_source: str,
) -> None:
    config_path = f"config/standalone_provider.{suffix}"
    simulated_sources, _edges, simulated_issues = _discover_provider_surfaces(
        source_overrides={config_path: config_source},
        tracked_paths=_git_tracked_paths() | {config_path},
    )
    assert config_path in simulated_sources
    assert config_path in _unlisted_transport_violations(simulated_sources)
    assert not simulated_issues, simulated_issues


def test_policy_rejects_dynamic_network_aliases_without_registry() -> None:
    mutations = {
        "scripts/dynamic_gateway.py": (
            "import os\n"
            "gateway = __import__('httpx')\n"
            "gateway.post(os.environ['OTHER_PROVIDER_URL'])\n"
        ),
        "scripts/call_alias.py": (
            "import os\n"
            "send = httpx.post\n"
            "send(os.environ['OTHER_PROVIDER_URL'])\n"
        ),
        "scripts/parent_import_alias.py": (
            "from http import client as transport\n"
            "transport.HTTPConnection('provider.invalid')\n"
        ),
        "scripts/importlib_gateway.py": (
            "import importlib\nimport os\n"
            "gateway = importlib.import_module('httpx')\n"
            "client = gateway.Client()\n"
            "client.get(os.environ['OTHER_PROVIDER_URL'])\n"
        ),
        "scripts/injected_get_client.py": (
            "import os\n"
            "def fetch(client):\n"
            "    return client.get(os.environ['SERVICE_URL'])\n"
        ),
        "scripts/aliased_get_gateway.py": (
            "def fetch(gateway, url):\n"
            "    receiver = gateway\n"
            "    return receiver.get(url)\n"
        ),
        "scripts/subprocess_provider.py": (
            "import os\nimport subprocess\n"
            "subprocess.run(['curl', os.environ['OTHER_PROVIDER_URL']], check=True)\n"
        ),
        "scripts/os_system_provider.py": (
            "import os\n"
            "os.system('wget https://provider.invalid/v1/chat/completions')\n"
        ),
        "scripts/subprocess_httpie.py": (
            "from subprocess import check_call\n"
            "check_call(['httpie', 'https://api.anthropic.com/v1/messages'])\n"
        ),
        "scripts/subprocess_nc.py": (
            "import subprocess as process\n"
            "process.Popen(['nc', 'provider.invalid', '443'])\n"
        ),
    }
    assert set(mutations) <= set(_unlisted_transport_violations(mutations))
    assert _unlisted_transport_violations(
        {"scripts/dict_lookup.py": "mapping = {}\nmapping.get('url')\n"}
    ) == []
    assert _unlisted_transport_violations(
        {
            "scripts/local_processes.py": (
                "import os\nimport subprocess\n"
                "subprocess.run(['python3', '--version'], check=True)\n"
                "subprocess.run(['curl', 'README.md'], check=True)\n"
                "os.system('printf local-only')\n"
            )
        }
    ) == []


def test_policy_rejects_registered_network_surface_repurpose() -> None:
    paths = (
        "NSI/corpus_nsi/scrapping_NSI/netpolicy.py",
        "NSI/corpus_nsi/scripts/substance_judge.py",
    )
    sources = _tracked_sources(paths)
    mutations = {
        path: source
        + "\nOTHER_PROVIDER_URL = 'https://provider.invalid/v1/generate'\n"
        for path, source in sources.items()
    }
    assert set(paths) <= set(_unlisted_transport_violations(mutations))


def test_policy_parses_nested_configs_and_provider_requirements() -> None:
    mutations = {
        "config/providers.yml": (
            "providers:\n"
            "  - name: hidden\n"
            "    endpoint: https://provider.invalid/v1/generate\n"
            "    models: [forbidden-model]\n"
        ),
        "config/providers.toml": (
            "[runtime]\n"
            '"provider" = "hidden"\n'
            '"endpoint" = "https://provider.invalid/v1/generate"\n'
        ),
        "requirements-provider.txt": "anthropic==1.2.3\n",
        "requirements-pep508.txt": (
            "openai @ https://provider.invalid/openai.whl\n"
        ),
        "pyproject-provider.toml": (
            "[project]\n"
            'dependencies = ["anthropic==1.2.3"]\n'
            "[project.optional-dependencies]\n"
            'audit = ["openai @ https://provider.invalid/openai.whl"]\n'
        ),
        "poetry-provider.toml": (
            "[tool.poetry.dependencies]\n"
            'anthropic = "^1.2"\n'
            "[tool.poetry.group.audit.dependencies]\n"
            'openai = {version = "^2.0", optional = true}\n'
            "[tool.poetry.optional-dependencies]\n"
            'chutes = "*"\n'
        ),
    }
    assert set(mutations) <= set(_unlisted_transport_violations(mutations))

    recursive_provider_graph = {
        "requirements-root.txt": "--requirement deps/provider-deps.lock\n",
        "deps/provider-deps.lock": "anthropic==1.2.3\n",
    }
    discovered_requirements, _edges, discovery_issues = (
        _discover_provider_surfaces(
            source_overrides=recursive_provider_graph,
            tracked_paths=_git_tracked_paths() | set(recursive_provider_graph),
        )
    )
    assert set(recursive_provider_graph) <= set(discovered_requirements)
    assert not discovery_issues, discovery_issues
    discovered_violations = _unlisted_transport_violations(
        discovered_requirements
    )
    assert "requirements-root.txt" in discovered_violations
    assert "deps/provider-deps.lock" not in discovered_violations
    assert _unlisted_transport_violations(
        {
            "requirements-root.txt": "-r deps/runtime.lock\n",
            "deps/runtime.lock": "httpx==0.28.1\n",
        }
    ) == []

    invalid_graphs = (
        {"requirements-root.txt": "-r ../outside.lock\n"},
        {"requirements-root.txt": "--requirement missing.lock\n"},
        {
            "requirements-root.txt": "-r deps/runtime.lock\n",
            "deps/runtime.lock": "--requirement ../requirements-root.txt\n",
        },
    )
    for graph in invalid_graphs:
        assert "requirements-root.txt" in _unlisted_transport_violations(graph)


def test_new_executables_under_historical_namespaces_are_active() -> None:
    provider_path = "audit/run_provider.py"
    workflow_path = "docs/codex/run-provider.yml"
    shell_path = "scripts/run_provider.sh"
    nested_shell_path = "scripts/nested_provider.sh"
    makefile_path = "provider/Makefile"
    active_workflow_path = "ci/provider.yml"
    overrides = {
        provider_path: (
            "gateway = __import__('httpx')\n"
            "gateway.post('https://provider.invalid/v1/generate')\n"
        ),
        workflow_path: (
            "name: hidden provider\n"
            "jobs:\n"
            "  run:\n"
            "    steps:\n"
            "      - run: python audit/run_provider.py\n"
        ),
        shell_path: 'curl "$OTHER_PROVIDER_URL"\n',
        nested_shell_path: "bash -c 'curl \"$SERVICE_URL\"'\n",
        makefile_path: "probe:\n\tcurl \"$SERVICE_URL\"\n",
        active_workflow_path: (
            "name: provider probe\n"
            "jobs:\n"
            "  probe:\n"
            "    steps:\n"
            "      - run: curl \"$SERVICE_URL\"\n"
        ),
    }
    simulated, _edges, issues = _discover_provider_surfaces(
        source_overrides=overrides,
        tracked_paths=_git_tracked_paths() | set(overrides),
    )
    assert set(overrides) <= set(simulated)
    assert provider_path in _unlisted_transport_violations(simulated)
    assert shell_path in _unlisted_transport_violations(simulated)
    assert nested_shell_path in _unlisted_transport_violations(simulated)
    assert makefile_path in _unlisted_transport_violations(simulated)
    assert active_workflow_path in _unlisted_transport_violations(simulated)
    assert any(workflow_path in issue for issue in issues)


def test_current_spec_rejects_new_chutes_prescription() -> None:
    spec_path = (
        "docs/superpowers/specs/"
        "2026-08-13-openrouter-only-external-provider-design.md"
    )
    source = _tracked_sources((spec_path,))[spec_path]
    outside_mutation = source + "\nUtiliser Chutes pour les prochaines revues.\n"
    section_nine_heading = next(
        line for line in source.splitlines() if line.startswith("## 9. ")
    )
    section_nine_mutation = source.replace(
        section_nine_heading,
        section_nine_heading + "\n\nUtiliser Chutes pour les prochaines revues.",
        1,
    )
    for mutation in (outside_mutation, section_nine_mutation):
        assert _chutes_violations({spec_path: mutation.encode("utf-8")})


def test_policy_rejects_unlisted_provider_transport(tmp_path: Path) -> None:
    with socket.socket() as probe:
        with pytest.raises(AssertionError):
            probe.connect(("127.0.0.1", 9))
    with pytest.raises(AssertionError):
        socket.create_connection(("127.0.0.1", 9))
    with pytest.raises(AssertionError):
        urllib.request.urlopen("http://127.0.0.1:9")

    rejected_mutations = {
        "mutations/requests_client.py": (
            'import requests\nrequests.post("https://provider.invalid/v1/chat/completions")\n'
        ),
        "mutations/urllib_client.py": (
            'import urllib.request\nurllib.request.urlopen("https://provider.invalid/v1/chat/completions")\n'
        ),
        "mutations/httpx_client.py": (
            'import httpx\nhttpx.post("https://provider.invalid/v1/chat/completions")\n'
        ),
        "mutations/opaque_httpx_client.py": (
            "import httpx\nimport os\n"
            "httpx.post(os.environ['OTHER_PROVIDER_URL'])\n"
        ),
        "mutations/provider_sdk.py": "from anthropic import Anthropic\nAnthropic()\n",
        "mutations/google_provider_sdk.py": (
            "import google.generativeai as genai\n"
            "genai.GenerativeModel('provider-model')\n"
        ),
    }
    mutation_sources: dict[str, str] = {}
    for relative_path, source in rejected_mutations.items():
        mutation_path = tmp_path / Path(relative_path).name
        mutation_path.write_text(source, encoding="utf-8")
        mutation_sources[relative_path] = mutation_path.read_text(encoding="utf-8")

    assert len(CANONICAL_PROVIDER_SURFACES) == len(
        set(CANONICAL_PROVIDER_SURFACES)
    )
    real_sources, real_edges, discovery_issues = _discover_provider_surfaces()
    canonical_surfaces = set(CANONICAL_PROVIDER_SURFACES)
    assert canonical_surfaces <= set(real_sources)
    assert {target for _importer, target in real_edges} <= set(real_sources)
    active_candidates = {
        path
        for path in _git_tracked_paths()
        if _is_active_discovery_candidate(path)
    }
    assert active_candidates <= set(real_sources)
    detected_network_paths = {
        path
        for path, source in real_sources.items()
        if path.endswith(".py")
        and source
        and _network_surface_signals(ast.parse(source))
    }
    assert len(NETWORK_SURFACE_REGISTRY) == 23
    assert detected_network_paths == set(NETWORK_SURFACE_REGISTRY)
    for path, contract in NETWORK_SURFACE_REGISTRY.items():
        assert path in real_sources
        assert contract["reason"]
        assert contract["endpoints"]
        assert re.fullmatch(r"[0-9a-f]{64}", contract["ast_sha256"])
        assert (
            _canonical_network_ast_digest(real_sources[path])
            == contract["ast_sha256"]
        ), f"network surface changed; explicit registry review required: {path}"
    complete_sources = {**real_sources, **mutation_sources}
    violations = set(_unlisted_transport_violations(complete_sources))
    assert set(rejected_mutations).issubset(violations), violations

    caller_path = SUBSTANCE_RAG_PATH
    provider_path = "NSI/corpus_nsi/scripts/other_provider.py"
    provider_mutation = tmp_path / "other_provider.py"
    provider_mutation.write_text(
        """import httpx

def complete():
    return httpx.post("https://provider.invalid/generate")
""",
        encoding="utf-8",
    )
    simulated_tracked = _git_tracked_paths() | {provider_path}
    import_forms = {
        "qualified": (
            "from scripts.other_provider import complete\ncomplete()\n"
        ),
        "package": (
            "from scripts import other_provider\nother_provider.complete()\n"
        ),
        "relative": (
            "from . import other_provider\nother_provider.complete()\n"
        ),
    }
    for label, import_source in import_forms.items():
        caller_mutation = tmp_path / f"substance_judge-{label}.py"
        caller_mutation.write_text(
            real_sources[caller_path] + "\n" + import_source,
            encoding="utf-8",
        )
        simulated_sources, simulated_edges, simulated_issues = (
            _discover_provider_surfaces(
                source_overrides={
                    caller_path: caller_mutation.read_text(encoding="utf-8"),
                    provider_path: provider_mutation.read_text(encoding="utf-8"),
                },
                tracked_paths=simulated_tracked,
            )
        )
        assert (caller_path, provider_path) in simulated_edges, (
            label,
            simulated_edges,
        )
        assert provider_path in simulated_sources
        simulated_violations = set(
            _unlisted_transport_violations(simulated_sources)
        )
        assert provider_path in simulated_violations, (
            label,
            simulated_edges,
            simulated_violations,
            simulated_issues,
        )

    real_violations = sorted(violations & set(real_sources))
    assert not (real_violations or discovery_issues), (
        "unlisted active provider integration: "
        f"violations={real_violations}, discovery={discovery_issues}"
    )


def test_policy_allows_only_openrouter_client_to_define_llm_endpoint() -> None:
    sources = _tracked_sources(CODE_PATHS)
    endpoint_paths = {
        path
        for path, source in sources.items()
        if any(
            marker in source
            for marker in (
                "/chat/completions",
                "/v1/messages",
                "api.anthropic.com",
            )
        )
    }
    assert endpoint_paths == {SHARED_CLIENT_PATH}, endpoint_paths
    shared_source = sources[SHARED_CLIENT_PATH]
    endpoint = "https://openrouter.ai/api/v1/chat/completions"
    assert shared_source.count(endpoint) == 1


def test_policy_preserves_non_llm_rag_transport_allowlist() -> None:
    sources = _tracked_sources(RAG_TRANSPORT_PATHS)
    assert set(sources) == set(RAG_TRANSPORT_PATHS)
    assert set(RAG_TRANSPORT_PATHS) <= set(NETWORK_SURFACE_REGISTRY)
    for path, source in sources.items():
        assert _unlisted_transport_violations({path: source}) == []

    mutated_path = "NSI/corpus_nsi/scripts/check_rag_freshness.py"
    removed_tree = ast.parse(sources[mutated_path])
    for node in removed_tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "query_chroma_hashes":
            node.body = [
                ast.Return(
                    value=ast.Dict(
                        keys=[],
                        values=[],
                    )
                )
            ]
    mutations = (
        ast.unparse(ast.fix_missing_locations(removed_tree)) + "\n",
        sources[mutated_path]
        + "\nimport urllib.request as u\n"
        + "u.urlopen(env['OTHER_PROVIDER_URL'])\n",
        sources[mutated_path]
        + "\nfrom urllib import request as u\n"
        + "u.urlopen(env['OTHER_PROVIDER_URL'])\n",
        sources[mutated_path]
        + "\nimport httpx\nimport os\n"
        + "MODEL_URL = os.environ['OTHER_PROVIDER_URL']\n"
        + "httpx.post(MODEL_URL)\n",
    )
    for mutation in mutations:
        assert _unlisted_transport_violations(
            {mutated_path: mutation}
        ) == [mutated_path]

    substance_path = "NSI/corpus_nsi/scripts/substance_judge.py"
    substance_mapping_mutation = sources[substance_path].replace(
        '"RAG_API_BASE_URL"',
        '"OTHER_PROVIDER_URL"',
        1,
    )
    assert substance_mapping_mutation != sources[substance_path]
    assert _unlisted_transport_violations(
        {substance_path: substance_mapping_mutation}
    ) == [substance_path]


def test_policy_fixed_non_llm_transport_allowlist_is_exact() -> None:
    fixed_paths = (
        "Mathematiques/manuel-maths/scripts/crawl.py",
        "NSI/scripts/crawl.py",
        "NSI/corpus_nsi/scrapping_NSI/netpolicy.py",
        "NSI/corpus_nsi/scrapping_NSI/scraper_nsi_v2.py",
    )
    sources = _tracked_sources(fixed_paths)
    assert set(fixed_paths) <= set(NETWORK_SURFACE_REGISTRY)
    assert _unlisted_transport_violations(sources) == []

    crawler_path = "Mathematiques/manuel-maths/scripts/crawl.py"
    provider_mutation = (
        sources[crawler_path]
        + "\nclient.post('https://provider.invalid/v1/chat/completions')\n"
    )
    assert _unlisted_transport_violations(
        {crawler_path: provider_mutation}
    ) == [crawler_path]

    destination_needle = (
        'client.get(urljoin(source["url"], "/sitemap.xml"))'
    )
    assert destination_needle in sources[crawler_path]
    destination_mutation = sources[crawler_path].replace(
        destination_needle,
        'client.get("https://provider.invalid/v1/chat/completions")',
        1,
    )
    assert _unlisted_transport_violations(
        {crawler_path: destination_mutation}
    ) == [crawler_path]

    loop_needle = "            try:\n                r = client.get(url)"
    assert loop_needle in sources[crawler_path]
    reassigned_url_mutation = sources[crawler_path].replace(
        loop_needle,
        "            url = 'https://provider.invalid/v1/chat/completions'\n"
        + loop_needle,
        1,
    )
    assert _unlisted_transport_violations(
        {crawler_path: reassigned_url_mutation}
    ) == [crawler_path]

    source_needle = '    method = source["crawl"]["method"]'
    assert source_needle in sources[crawler_path]
    reassigned_source_mutation = sources[crawler_path].replace(
        source_needle,
        "    source['url'] = 'https://provider.invalid/v1/chat/completions'\n"
        + source_needle,
        1,
    )
    assert _unlisted_transport_violations(
        {crawler_path: reassigned_source_mutation}
    ) == [crawler_path]

    urls_needle = "        urls = discover_links(client, source)"
    assert urls_needle in sources[crawler_path]
    append_mutation = sources[crawler_path].replace(
        urls_needle,
        urls_needle
        + "\n        urls.append('https://provider.invalid/v1/chat/completions')",
        1,
    )
    assert _unlisted_transport_violations(
        {crawler_path: append_mutation}
    ) == [crawler_path]

    update_mutation = sources[crawler_path].replace(
        source_needle,
        "    source.update({'url': "
        "'https://provider.invalid/v1/chat/completions'})\n"
        + source_needle,
        1,
    )
    assert _unlisted_transport_violations(
        {crawler_path: update_mutation}
    ) == [crawler_path]


def test_policy_rejects_chutes_in_active_authority(tmp_path: Path) -> None:
    sources = {
        path: (ROOT / path).read_bytes()
        for path in AUTHORITY_AND_GUIDE_PATHS
    }
    _assert_paths_exist_and_are_tracked(sources)
    approved = {"AGENTS.md": b"- Aucun nouvel appel Chutes.\n"}
    assert _chutes_violations(approved) == []

    mutation = tmp_path / "active-authority.md"
    mutation.write_text(
        "Ce workflow historique doit prescrire : Utiliser Chutes pour tout audit.\n",
        encoding="utf-8",
    )
    mutation_sources = {
        "active/authority.md": mutation.read_bytes(),
    }
    assert _chutes_violations(mutation_sources), mutation_sources
    assert not _chutes_violations(sources), _chutes_violations(sources)


def test_policy_ignores_protected_historical_chutes_artifacts(tmp_path: Path) -> None:
    assert HISTORICAL_BASELINE_COMMIT == (
        "89a87253aef6ddea07d5639e5910330ebbf5c358"
    )
    assert len(DISCOVERY_HISTORICAL_PATH_SNAPSHOT) == HISTORICAL_SNAPSHOT_COUNT
    assert (
        _historical_snapshot_digest(DISCOVERY_HISTORICAL_PATH_SNAPSHOT)
        == HISTORICAL_SNAPSHOT_SHA256
    )
    assert CURRENT_OPENROUTER_SPEC_PATH in DISCOVERY_HISTORICAL_PATH_SNAPSHOT
    assert HISTORICAL_ACTIVE_EXCLUSIONS == frozenset(
        {CURRENT_OPENROUTER_PLAN_PATH, CURRENT_OPENROUTER_SPEC_PATH}
    )
    assert all(
        not _is_protected_historical_path(path)
        for path in HISTORICAL_ACTIVE_EXCLUSIONS
    )
    assert {
        path
        for path in DISCOVERY_HISTORICAL_PATH_SNAPSHOT
        if not _is_protected_historical_path(path)
    } == set(HISTORICAL_ACTIVE_EXCLUSIONS)
    protected_paths = DISCOVERY_HISTORICAL_PATH_SNAPSHOT.difference(
        HISTORICAL_ACTIVE_EXCLUSIONS
    )
    assert protected_paths <= _git_tracked_paths()
    current_blob_drift = {
        path: _git_blob_oid((ROOT / path).read_bytes())
        for path in protected_paths
        if _historical_blob_drift(path, (ROOT / path).read_bytes())
    }
    assert not current_blob_drift, current_blob_drift

    source_path = ROOT / "audit/chutes/2026-07-21-mcp-smoke-test.md"
    _assert_paths_exist_and_are_tracked((str(source_path.relative_to(ROOT)),))
    before = source_path.read_bytes()
    copied = tmp_path / source_path.name
    copied.write_bytes(before)

    logical_path = f"audit/chutes/{copied.name}"
    assert _chutes_violations({logical_path: copied.read_bytes()}) == []
    mutation = copied.read_bytes() + b"\ntrace historique modifiee\n"
    assert _chutes_violations({logical_path: mutation}) == [
        f"{logical_path}:historical blob drift"
    ]
    assert copied.read_bytes() == before
    assert source_path.read_bytes() == before


def test_policy_rejects_model_catalog_endpoint_in_automation(tmp_path: Path) -> None:
    helper_mutation = tmp_path / "catalog_helper.py"
    helper_mutation.write_text(
        """import httpx

CATALOG_URL = "https://openrouter.ai/api/v1/models"

def probe_catalog():
    return httpx.get(CATALOG_URL)
""",
        encoding="utf-8",
    )
    active_test_mutation = tmp_path / "test_catalog_probe.py"
    active_test_mutation.write_text(
        """import urllib.request

def test_catalog_probe():
    return urllib.request.urlopen("https://openrouter.ai/api/v1/models")
""",
        encoding="utf-8",
    )
    mutation_sources = {
        "mutations/catalog_helper.py": helper_mutation.read_text(encoding="utf-8"),
        "tests/test_catalog_probe.py": active_test_mutation.read_text(encoding="utf-8"),
    }
    assert _catalog_violations(mutation_sources) == sorted(mutation_sources)

    assert len(CATALOG_AUTOMATION_PATHS) == len(set(CATALOG_AUTOMATION_PATHS))
    assert set(TEST_PATHS).issubset(CATALOG_AUTOMATION_PATHS)
    sources = _working_tree_sources(CATALOG_AUTOMATION_PATHS)
    assert set(sources) == set(CATALOG_AUTOMATION_PATHS)
    assert not _catalog_violations(sources), _catalog_violations(sources)


def test_policy_rejects_new_nsi_ingest_make_target() -> None:
    paths = ("NSI/Makefile", "NSI/scripts/ingest.py")
    sources = _tracked_sources(paths)
    makefile = sources["NSI/Makefile"]
    assert re.search(r"(?m)^ingest\s*:", makefile) is None
    assert (ROOT / "NSI/scripts/ingest.py").is_file()


def test_targeted_surfaces_exist_before_negative_scans() -> None:
    assert len(TARGETED_SCAN_PATHS) == len(set(TARGETED_SCAN_PATHS))
    _assert_paths_exist_and_are_tracked(TARGETED_SCAN_PATHS)
    for path in TARGETED_SCAN_PATHS:
        assert (ROOT / path).read_bytes(), f"empty targeted surface: {path}"


def test_policy_rejects_anthropic_in_active_callers() -> None:
    sources = _tracked_sources(CALLER_PATHS)
    forbidden = (
        "ANTHROPIC_API_KEY",
        "api.anthropic.com",
        "from anthropic import",
        "import anthropic",
        "Anthropic(",
        "claude-",
    )
    violations = {
        path: [marker for marker in forbidden if marker in source]
        for path, source in sources.items()
        if any(marker in source for marker in forbidden)
    }
    assert not violations, violations


def test_policy_rejects_local_llm_configuration_in_active_surfaces() -> None:
    sources = _tracked_sources(LOCAL_LLM_SCAN_PATHS)
    checker_path = "NSI/corpus_nsi/scripts/check_rag_config.py"
    local_keys = {
        "LOCAL_LLM_ENGINE",
        "LOCAL_LLM_BASE_URL",
        "LOCAL_LLM_MODEL",
        "LOCAL_LLM_API_KEY",
    }
    violations: dict[str, object] = {}
    for path, source in sources.items():
        if path == checker_path:
            unexpected = _expected_env_keys(source) & local_keys
            if unexpected:
                violations[path] = sorted(unexpected)
            continue
        policy_source = source
        if path == CURRENT_OPENROUTER_SPEC_PATH:
            policy_source = "\n".join(
                line
                for line in source.splitlines()
                if line.strip() not in CURRENT_SPEC_LOCAL_LLM_HISTORICAL_LINES
            )
        present = sorted(key for key in local_keys if key in policy_source)
        if present:
            violations[path] = present
    assert not violations, violations


def test_ci_no_deps_requirements_close_httpx_runtime_dependencies() -> None:
    path = "requirements-ci-audit.txt"
    source = _tracked_sources((path,))[path]
    lines = [
        line.strip()
        for line in source.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    required = {
        "httpx==0.28.1",
        "anyio==4.9.0",
        "certifi==2026.7.22",
        "httpcore==1.0.9",
        "h11==0.16.0",
        "idna==3.6",
        "sniffio==1.3.1",
        "typing_extensions==4.15.0",
    }
    counts = {pin: lines.count(pin) for pin in required}
    assert counts == {pin: 1 for pin in required}, counts
    provider_prefixes = ("anthropic", "openai", "chutes")
    provider_sdks = [
        line for line in lines if line.casefold().startswith(provider_prefixes)
    ]
    assert not provider_sdks, provider_sdks
