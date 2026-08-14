from __future__ import annotations

import ast
import re
import socket
import subprocess
import urllib.request
from collections.abc import Iterable, Mapping
from pathlib import Path

import pytest


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
    "NSI/CAHIER_DES_CHARGES.md",
    "NSI/docs/02_workflow_production.md",
    "NSI/docs/03_architecture_technique.md",
    "NSI/corpus_nsi/README.md",
    "NSI/corpus_nsi/rag_connection.md",
    "NSI/corpus_nsi/substance_pipeline.md",
    "NSI/corpus_nsi/docs/enrichment_roadmap.md",
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
    "NSI/corpus_nsi/scripts/rag_ingest_server.py",
    "NSI/corpus_nsi/scripts/rag_query_example.py",
    "NSI/corpus_nsi/scripts/rag_smoke_test.py",
)

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

DISCOVERY_HISTORICAL_PREFIXES = (
    "audit/",
    "docs/codex/",
    "docs/superpowers/plans/",
    "docs/superpowers/specs/",
    "NSI/corpus_nsi/reports/",
    "NSI/corpus_nsi/substance_reviews/",
)

DISCOVERY_HISTORICAL_PATHS = {
    "NSI/corpus_nsi/docs/judge_campaign_plan.md",
}

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

RAG_TRANSPORT_CONTRACT = {
    "NSI/corpus_nsi/scripts/check_rag_freshness.py": {
        "imports": (("urllib.request", "urllib.request"),),
        "functions": {
            "query_chroma_hashes": {
                "calls": {
                    "urllib.request.Request": 1,
                    "urllib.request.urlopen": 1,
                },
                "roots": {"RAG_API_BASE_URL"},
            },
        },
    },
    "NSI/corpus_nsi/scripts/ingest_nsi_corpus.py": {
        "imports": (("urllib.request", "urllib.request"),),
        "functions": {
            "main": {
                "calls": {
                    "urllib.request.Request": 7,
                    "urllib.request.urlopen": 7,
                },
                "roots": {"EMBEDDING_BASE_URL", "VECTOR_DB_URL"},
            },
        },
    },
    "NSI/corpus_nsi/scripts/rag_diagnose_search_timeout.py": {
        "imports": (("urllib.request", "urllib.request"),),
        "functions": {
            "run_probe": {
                "calls": {
                    "urllib.request.Request": 1,
                    "urllib.request.urlopen": 1,
                },
                "roots": {"RAG_API_BASE_URL"},
            },
        },
    },
    "NSI/corpus_nsi/scripts/rag_ingest_server.py": {
        "imports": (("urllib.request", "urllib.request"),),
        "functions": {
            "_http": {
                "calls": {
                    "urllib.request.Request": 1,
                    "urllib.request.urlopen": 1,
                },
                "roots": {"EMBEDDING_BASE_URL", "VECTOR_DB_URL"},
            },
            "embed": {
                "calls": {"_http": 1},
                "roots": {"EMBEDDING_BASE_URL"},
            },
            "get_or_create_collection": {
                "calls": {"_http": 2},
                "roots": {"VECTOR_DB_URL"},
            },
            "collection_count": {
                "calls": {"urllib.request.urlopen": 1},
                "roots": {"VECTOR_DB_URL"},
            },
            "upsert": {
                "calls": {"_http": 1},
                "roots": {"VECTOR_DB_URL"},
            },
            "delete_collection": {
                "calls": {"_http": 1},
                "roots": {"VECTOR_DB_URL"},
            },
        },
    },
    "NSI/corpus_nsi/scripts/rag_query_example.py": {
        "imports": (),
        "functions": {
            "main": {"calls": {}, "roots": set()},
        },
    },
    "NSI/corpus_nsi/scripts/rag_smoke_test.py": {
        "imports": (("urllib.request", "urllib.request"),),
        "functions": {
            "smoke_search": {
                "calls": {
                    "urllib.request.Request": 1,
                    "urllib.request.urlopen": 1,
                },
                "roots": {"RAG_API_BASE_URL"},
            },
        },
    },
    SUBSTANCE_RAG_PATH: {
        "imports": (("urllib.request", "urllib.request"),),
        "functions": {
            "_http_json": {
                "calls": {
                    "urllib.request.Request": 1,
                    "urllib.request.urlopen": 1,
                },
                "roots": {"RAG_API_BASE_URL"},
            },
            "search_rag": {
                "calls": {"_http_json": 1},
                "roots": {"RAG_API_BASE_URL"},
            },
        },
    },
}

PROVIDER_SDK_PREFIXES = (
    "anthropic",
    "chutes",
    "cohere",
    "google.generativeai",
    "groq",
    "mistralai",
    "openai",
)

HTTP_STACK_PREFIXES = (
    "aiohttp",
    "http.client",
    "httpx",
    "requests",
    "urllib.request",
    "urllib3",
)


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


def _is_protected_historical_path(path: str) -> bool:
    return path in DISCOVERY_HISTORICAL_PATHS or path.startswith(
        DISCOVERY_HISTORICAL_PREFIXES
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
    queue = list(CANONICAL_PROVIDER_SURFACES)
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
        if not source or not path.endswith(".py"):
            continue
        try:
            new_edges, import_issues = _import_edges(path, source, available)
        except SyntaxError as exc:
            issues.append(f"syntax error in active surface {path}:{exc.lineno}")
            continue
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


def _provider_sdk_used(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(_is_provider_sdk_name(alias.name) for alias in node.names):
                return True
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if _is_provider_sdk_name(module):
                return True
        elif isinstance(node, ast.Call):
            name = _dotted_name(node.func)
            if _is_provider_sdk_name(name):
                return True
    return False


def _http_stack_imports(tree: ast.AST) -> list[tuple[str, str]]:
    imports: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if any(
                    alias.name == prefix or alias.name.startswith(f"{prefix}.")
                    for prefix in HTTP_STACK_PREFIXES
                ):
                    imports.append((alias.name, alias.asname or alias.name))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "urllib":
                for alias in node.names:
                    if alias.name == "request":
                        imports.append(
                            ("urllib.request", alias.asname or alias.name)
                        )
                continue
            if any(
                module == prefix or module.startswith(f"{prefix}.")
                for prefix in HTTP_STACK_PREFIXES
            ):
                for alias in node.names:
                    imports.append((module, alias.asname or alias.name))
    return imports


def _is_http_call(call: ast.Call) -> bool:
    name = _dotted_name(call.func)
    direct_calls = {
        "_http_json",
        "_http",
        "httpx.Client",
        "httpx.get",
        "httpx.patch",
        "httpx.post",
        "httpx.put",
        "httpx.request",
        "requests.Session",
        "requests.delete",
        "requests.get",
        "requests.patch",
        "requests.post",
        "requests.put",
        "requests.request",
        "urllib.request.Request",
        "urllib.request.urlopen",
    }
    method = name.rsplit(".", maxsplit=1)[-1]
    receiver = name.rsplit(".", maxsplit=1)[0].casefold()
    generic_method = method in {"delete", "patch", "post", "put", "request"}
    client_get = method == "get" and any(
        marker in receiver for marker in ("client", "http", "session", "transport")
    )
    aliased_urllib = method in {"Request", "urlopen"}
    return name in direct_calls or generic_method or client_get or aliased_urllib


def _network_destination(call: ast.Call) -> ast.AST | None:
    name = _dotted_name(call.func)
    if name in {"httpx.Client", "requests.Session"}:
        for keyword in call.keywords:
            if keyword.arg in {"base_url", "url"}:
                return keyword.value
        return None
    if name == "_http":
        return call.args[1] if len(call.args) > 1 else None
    if name in {"requests.request", "httpx.request"} or name.endswith(".request"):
        return call.args[1] if len(call.args) > 1 else None
    if call.args:
        return call.args[0]
    for keyword in call.keywords:
        if keyword.arg in {"base_url", "url"}:
            return keyword.value
    return None


def _scope_assignments(tree: ast.AST) -> dict[str | None, dict[str, list[ast.AST]]]:
    parents = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }
    assignments: dict[str | None, dict[str, list[ast.AST]]] = {None: {}}
    for node in ast.walk(tree):
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
        scope = _enclosing_function(node, parents)
        scope_assignments = assignments.setdefault(scope, {})
        for target in targets:
            if isinstance(target, ast.Name):
                scope_assignments.setdefault(target.id, []).append(value)
    return assignments


def _canonical_root(path: str, root: str) -> str:
    if path == "NSI/corpus_nsi/scripts/rag_ingest_server.py":
        aliases = {
            "OLLAMA_URL": "EMBEDDING_BASE_URL",
            "CHROMA_URL": "VECTOR_DB_URL",
        }
        return aliases.get(root, root)
    return root


def _destination_provenance(
    node: ast.AST,
    *,
    path: str,
    scope: str | None,
    assignments: Mapping[str | None, Mapping[str, list[ast.AST]]],
    seen: frozenset[tuple[str | None, str]] = frozenset(),
) -> tuple[set[str], set[str]]:
    if isinstance(node, ast.Name):
        key = (scope, node.id)
        values = assignments.get(scope, {}).get(node.id, ())
        if not values and scope is not None:
            key = (None, node.id)
            values = assignments.get(None, {}).get(node.id, ())
        if values and key not in seen:
            roots: set[str] = set()
            free: set[str] = set()
            for value in values:
                value_roots, value_free = _destination_provenance(
                    value,
                    path=path,
                    scope=key[0],
                    assignments=assignments,
                    seen=seen | {key},
                )
                roots.update(value_roots)
                free.update(value_free)
            return roots, free
        return set(), {node.id}
    if isinstance(node, ast.Subscript):
        owner = _dotted_name(node.value)
        if owner in {"env", "os.environ"}:
            key_node = node.slice
            if isinstance(key_node, ast.Constant) and isinstance(key_node.value, str):
                return {_canonical_root(path, key_node.value)}, set()
    if isinstance(node, ast.Call):
        name = _dotted_name(node.func)
        if name in {"env.get", "os.environ.get", "os.getenv"} and node.args:
            key_node = node.args[0]
            if isinstance(key_node, ast.Constant) and isinstance(key_node.value, str):
                return {_canonical_root(path, key_node.value)}, set()
        destination = _network_destination(node) if _is_http_call(node) else None
        children = (
            (destination,)
            if destination is not None
            else (*node.args, *(keyword.value for keyword in node.keywords))
        )
    else:
        children = tuple(ast.iter_child_nodes(node))
    roots: set[str] = set()
    free: set[str] = set()
    for child in children:
        child_roots, child_free = _destination_provenance(
            child,
            path=path,
            scope=scope,
            assignments=assignments,
            seen=seen,
        )
        roots.update(child_roots)
        free.update(child_free)
    return roots, free


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


def _enclosing_function(
    node: ast.AST,
    parents: Mapping[ast.AST, ast.AST],
) -> str | None:
    current = parents.get(node)
    while current is not None:
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return current.name
        current = parents.get(current)
    return None


def _diagnose_rag_chain_is_closed(tree: ast.AST) -> bool:
    search_assignment = False
    builds_from_search = False
    runs_probe = False
    request_uses_probe_url = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "search_url"
            for target in node.targets
        ):
            value = node.value
            search_assignment = (
                isinstance(value, ast.Call)
                and _dotted_name(value.func) == "env.get"
                and bool(value.args)
                and isinstance(value.args[0], ast.Constant)
                and value.args[0].value == "RAG_API_BASE_URL"
            )
        if not isinstance(node, ast.Call):
            continue
        name = _dotted_name(node.func)
        if name == "build_probes" and node.args:
            builds_from_search = isinstance(node.args[0], ast.Name) and (
                node.args[0].id == "search_url"
            )
        elif name == "run_probe" and node.args:
            runs_probe = isinstance(node.args[0], ast.Name) and (
                node.args[0].id == "probe"
            )
        elif name == "urllib.request.Request" and node.args:
            destination = node.args[0]
            request_uses_probe_url = (
                isinstance(destination, ast.Attribute)
                and destination.attr == "url"
                and isinstance(destination.value, ast.Name)
                and destination.value.id == "probe"
            )
    return all(
        (
            search_assignment,
            builds_from_search,
            runs_probe,
            request_uses_probe_url,
        )
    )


def _environment_keys(tree: ast.AST) -> set[str]:
    keys: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and _dotted_name(node.value) in {
            "env",
            "os.environ",
        }:
            if isinstance(node.slice, ast.Constant) and isinstance(
                node.slice.value, str
            ):
                keys.add(node.slice.value)
        elif isinstance(node, ast.Call) and _dotted_name(node.func) in {
            "env.get",
            "os.environ.get",
            "os.getenv",
        }:
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(
                node.args[0].value, str
            ):
                keys.add(node.args[0].value)
    return keys


def _rag_network_violations(path: str, source: str) -> list[str]:
    tree = ast.parse(source)
    parents = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }
    assignments = _scope_assignments(tree)
    contract = RAG_TRANSPORT_CONTRACT[path]
    expected_functions = contract["functions"]
    present_functions = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    violations: list[str] = []
    observed_imports = tuple(sorted(_http_stack_imports(tree)))
    expected_imports = tuple(sorted(contract["imports"]))
    if observed_imports != expected_imports:
        violations.append(
            f"imports={observed_imports}:expected={expected_imports}"
        )
    missing_functions = set(expected_functions) - present_functions
    if missing_functions:
        violations.append(f"missing_functions={sorted(missing_functions)}")

    observed_calls: dict[str, dict[str, int]] = {}
    observed_roots: dict[str, set[str]] = {}
    helper_roots: dict[str, set[str]] = {"_http": set(), "_http_json": set()}
    for call in (
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and _is_http_call(node)
    ):
        function = _enclosing_function(call, parents) or "<module>"
        call_name = _dotted_name(call.func)
        function_calls = observed_calls.setdefault(function, {})
        function_calls[call_name] = function_calls.get(call_name, 0) + 1
        destination = _network_destination(call)
        if destination is None:
            observed_roots.setdefault(function, set()).add("<unresolved>")
            continue
        roots, free = _destination_provenance(
            destination,
            path=path,
            scope=function,
            assignments=assignments,
        )
        if (
            path == "NSI/corpus_nsi/scripts/rag_diagnose_search_timeout.py"
            and function == "run_probe"
            and free <= {"probe", "request"}
            and _diagnose_rag_chain_is_closed(tree)
        ):
            roots = {"RAG_API_BASE_URL"}
            free = set()
        if call_name in helper_roots:
            helper_roots[call_name].update(roots)
        if roots:
            observed_roots.setdefault(function, set()).update(roots)
        elif not (function in helper_roots and free == {"url"}):
            observed_roots.setdefault(function, set()).add("<unresolved>")

    for helper, roots in helper_roots.items():
        if helper in expected_functions:
            observed_roots[helper] = set(roots)

    observed_functions = set(observed_calls)
    expected_function_names = set(expected_functions)
    extra_functions = observed_functions - expected_function_names
    if extra_functions:
        violations.append(f"extra_functions={sorted(extra_functions)}")
    for function, expected in expected_functions.items():
        calls = observed_calls.get(function, {})
        if calls != expected["calls"]:
            violations.append(
                f"{function}:calls={calls}:expected={expected['calls']}"
            )
        roots = observed_roots.get(function, set())
        if roots != expected["roots"]:
            violations.append(
                f"{function}:roots={sorted(roots)}:"
                f"expected={sorted(expected['roots'])}"
            )
    return violations


def _test_guard_call_is_allowed(
    path: str,
    function: str | None,
    call: ast.Call,
) -> bool:
    if path not in TEST_PATHS or _dotted_name(call.func) != "urllib.request.urlopen":
        return False
    if function not in {
        "_forbid_network",
        "_forbid_real_network",
        "_prove_network_guard",
        "test_math_network_guard_mutation_is_effective",
        "test_nsi_network_guard_mutation_is_effective",
        "test_policy_rejects_unlisted_provider_transport",
    }:
        return False
    destination = _network_destination(call)
    return (
        isinstance(destination, ast.Constant)
        and destination.value == "http://127.0.0.1:9"
    )


def _unlisted_transport_violations(sources: Mapping[str, str]) -> list[str]:
    violations: list[str] = []
    llm_destination_markers = (
        "api.anthropic.com",
        "/chat/completions",
        "/v1/messages",
    )
    for logical_path, source in sources.items():
        if not source or logical_path == SHARED_CLIENT_PATH:
            continue
        if not logical_path.endswith(".py"):
            if any(marker in source.casefold() for marker in llm_destination_markers):
                violations.append(logical_path)
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            violations.append(logical_path)
            continue
        if _provider_sdk_used(tree):
            violations.append(logical_path)
            continue
        if logical_path in RAG_TRANSPORT_CONTRACT:
            if _rag_network_violations(logical_path, source):
                violations.append(logical_path)
            continue
        http_imports = _http_stack_imports(tree)
        parents = {
            child: parent
            for parent in ast.walk(tree)
            for child in ast.iter_child_nodes(parent)
        }
        network_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and _is_http_call(node)
        ]
        unexpected_calls = [
            call
            for call in network_calls
            if not _test_guard_call_is_allowed(
                logical_path,
                _enclosing_function(call, parents),
                call,
            )
        ]
        if logical_path in TEST_PATHS:
            allowed_test_imports = {"httpx", "urllib.request"}
            unexpected_imports = [
                (imported, alias)
                for imported, alias in http_imports
                if imported not in allowed_test_imports or alias != imported
            ]
        else:
            unexpected_imports = http_imports
        if unexpected_imports or unexpected_calls:
            violations.append(logical_path)
            continue
    return sorted(set(violations))


def _chutes_violations(sources: Mapping[str, bytes]) -> list[str]:
    historical_prefixes = (
        "audit/",
        "docs/codex/",
        "docs/superpowers/plans/",
        "docs/superpowers/specs/",
        "NSI/corpus_nsi/reports/",
        "NSI/corpus_nsi/substance_reviews/",
    )
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
        if logical_path.startswith(historical_prefixes):
            continue
        for line_number, line in enumerate(raw.decode("utf-8").splitlines(), start=1):
            lowered = line.casefold()
            if "chutes" not in lowered:
                continue
            if any(pattern.fullmatch(line) for pattern in approved_negative_lines):
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
            if not (_is_http_call(node) or _dotted_name(node.func) in shell_calls):
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
    _assert_paths_exist_and_are_tracked(CANONICAL_ACTIVE_PATHS)


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

    rag_mutation = tmp_path / "substance_rag_only.py"
    rag_mutation.write_text(
        """import urllib.request

def _http_json(url):
    request = urllib.request.Request(url)
    return urllib.request.urlopen(request)

def search_rag(env):
    return _http_json(env["RAG_API_BASE_URL"])
""",
        encoding="utf-8",
    )
    rag_source = rag_mutation.read_text(encoding="utf-8")
    assert _rag_network_violations(SUBSTANCE_RAG_PATH, rag_source) == []
    assert _unlisted_transport_violations({SUBSTANCE_RAG_PATH: rag_source}) == []

    assert len(CANONICAL_PROVIDER_SURFACES) == len(
        set(CANONICAL_PROVIDER_SURFACES)
    )
    real_sources, real_edges, discovery_issues = _discover_provider_surfaces()
    canonical_surfaces = set(CANONICAL_PROVIDER_SURFACES)
    assert canonical_surfaces <= set(real_sources)
    assert {target for _importer, target in real_edges} <= set(real_sources)
    discovered_extensions = set(real_sources) - canonical_surfaces
    imported_extensions = {
        target
        for _importer, target in real_edges
        if target not in canonical_surfaces
    }
    assert discovered_extensions == imported_extensions
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


def test_policy_preserves_non_llm_rag_transport_allowlist(tmp_path: Path) -> None:
    sources = _tracked_sources(RAG_TRANSPORT_PATHS)
    assert set(sources) == set(RAG_TRANSPORT_PATHS)
    assert set(RAG_TRANSPORT_PATHS) <= set(RAG_TRANSPORT_CONTRACT)
    for path, source in sources.items():
        assert _rag_network_violations(path, source) == [], (
            path,
            _rag_network_violations(path, source),
        )

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
    removed_transport = tmp_path / "check_rag_freshness-no-transport.py"
    removed_transport.write_text(
        ast.unparse(ast.fix_missing_locations(removed_tree)) + "\n",
        encoding="utf-8",
    )
    assert _rag_network_violations(
        mutated_path,
        removed_transport.read_text(encoding="utf-8"),
    )

    alias_mutation = tmp_path / "check_rag_freshness-alias.py"
    alias_mutation.write_text(
        sources[mutated_path]
        + "\nimport urllib.request as u\n"
        + "u.urlopen(env['OTHER_PROVIDER_URL'])\n",
        encoding="utf-8",
    )
    assert _rag_network_violations(
        mutated_path,
        alias_mutation.read_text(encoding="utf-8"),
    )

    import_from_mutation = tmp_path / "check_rag_freshness-import-from.py"
    import_from_mutation.write_text(
        sources[mutated_path]
        + "\nfrom urllib import request as u\n"
        + "u.urlopen(env['OTHER_PROVIDER_URL'])\n",
        encoding="utf-8",
    )
    assert _rag_network_violations(
        mutated_path,
        import_from_mutation.read_text(encoding="utf-8"),
    )

    model_mutation = tmp_path / "check_rag_freshness-model.py"
    model_mutation.write_text(
        sources[mutated_path]
        + "\nimport httpx\nimport os\n"
        + "MODEL_URL = os.environ['OTHER_PROVIDER_URL']\n"
        + "httpx.post(MODEL_URL)\n",
        encoding="utf-8",
    )
    mutated_source = model_mutation.read_text(encoding="utf-8")
    assert "RAG_API_BASE_URL" in _environment_keys(ast.parse(mutated_source))
    assert _rag_network_violations(mutated_path, mutated_source)


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
    source_path = ROOT / "audit/chutes/2026-07-21-mcp-smoke-test.md"
    _assert_paths_exist_and_are_tracked((str(source_path.relative_to(ROOT)),))
    before = source_path.read_bytes()
    copied = tmp_path / source_path.name
    copied.write_bytes(before)

    logical_path = f"audit/chutes/{copied.name}"
    assert _chutes_violations({logical_path: copied.read_bytes()}) == []
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
        present = sorted(key for key in local_keys if key in source)
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
