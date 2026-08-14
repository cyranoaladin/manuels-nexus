"""Contrat Red de la migration OpenRouter des juges du corpus NSI.

Les imports des futurs modules partages restent dans les corps de tests afin
que ce jalon Red reste collectable avant toute production Green.
"""

from __future__ import annotations

import ast
import builtins
import copy
import importlib
import inspect
import json
import socket
import sys
import threading
import urllib.request
from collections.abc import Callable
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest


CORPUS_ROOT = Path(__file__).resolve().parents[1]
CHECKOUT_ROOT = Path(__file__).resolve().parents[3]
assert (CORPUS_ROOT / "AGENTS.md").is_file()
assert (CHECKOUT_ROOT / ".git").exists()

API_KEY = "openrouter-corpus-key-sentinel"
MODEL = "vendor/corpus-judge-explicit"
MODEL_REQUESTED = "vendor/requested-model"
MODEL_RETURNED = "provider/returned-model"
CAPACITY_ID = "P-TABLE-01"
CAPACITY_TEXT = "Importer une table depuis un fichier CSV."
ROLE_LABEL = "enseigne"
SECTION_TEXT = "Une phrase de cours utile. " * 80
JUDGED_AT = "2026-08-13T12:00:00Z"


@pytest.fixture(autouse=True)
def _forbid_real_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def blocked(*args: object, **kwargs: object) -> None:
        raise AssertionError("network forbidden by corpus OpenRouter tests")

    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(urllib.request, "urlopen", blocked)
    _prove_network_guard()


def _prove_network_guard() -> None:
    def socket_connect() -> None:
        with socket.socket() as candidate:
            candidate.connect(("127.0.0.1", 9))

    probes: tuple[Callable[[], object], ...] = (
        socket_connect,
        lambda: socket.create_connection(("127.0.0.1", 9)),
        lambda: urllib.request.urlopen("http://127.0.0.1:9"),
    )
    for probe in probes:
        with pytest.raises(AssertionError, match="network forbidden"):
            probe()


def _campaign() -> Any:
    return importlib.import_module("scripts.judge_campaign")


def _substance() -> Any:
    return importlib.import_module("scripts.substance_judge")


def _client() -> Any:
    return importlib.import_module("nexus_external.openrouter_client")


def _completion(
    *,
    content: str = '{"result": "ok"}',
    generation_id: str = "gen-corpus-001",
    model: str = MODEL,
    prompt_tokens: int = 17,
    completion_tokens: int = 5,
    cost: float = 0.004321,
    cached_tokens: int = 7,
    cache_write_tokens: int = 3,
) -> object:
    client = _client()
    usage = client.OpenRouterUsage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        cost=cost,
        cached_tokens=cached_tokens,
        cache_write_tokens=cache_write_tokens,
    )
    return client.OpenRouterCompletion(
        content=content,
        generation_id=generation_id,
        model=model,
        provider="provider-observed",
        usage=usage,
    )


def _campaign_result() -> dict[str, object]:
    absent = {"present": False, "file": None, "anchor": None, "quote": None}
    return {
        "proof_course": copy.deepcopy(absent),
        "proof_practice": copy.deepcopy(absent),
        "proof_correction": copy.deepcopy(absent),
        "comment": "Aucune preuve verifiable n'est retenue pour cette capacite.",
    }


def _programme() -> dict[str, dict[str, str]]:
    return {
        CAPACITY_ID: {
            "id": CAPACITY_ID,
            "intitule": CAPACITY_TEXT,
            "contenu": "Tables",
            "rubrique": "Données",
            "niveau": "premiere",
        }
    }


def _campaign_accounting_policy_errors(source: str) -> list[str]:
    tree = ast.parse(source)
    errors: list[str] = []
    accounting_fields = {
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "cached_tokens",
        "cache_write_tokens",
        "cost_usd",
    }
    accounting_fragments = (
        "token",
        "usage",
        "cost",
        "price",
        "cache",
        "history",
    )
    forbidden_float_coefficients = {0.30, 3.0, 3.75, 15.0}
    forbidden_integer_thresholds = {1_000_000, 1024}

    def functions() -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
        return [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

    def classes() -> list[ast.ClassDef]:
        return [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    def direct_scope_nodes(statements: list[ast.stmt]) -> list[ast.AST]:
        nodes: list[ast.AST] = []

        class DirectScopeVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                return None

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
                return None

            def visit_ClassDef(self, node: ast.ClassDef) -> None:
                return None

            def generic_visit(self, node: ast.AST) -> None:
                nodes.append(node)
                super().generic_visit(node)

        for statement in statements:
            DirectScopeVisitor().visit(statement)
        return nodes

    def references_accounting(node: ast.AST) -> bool:
        references: list[str] = []
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                references.append(child.id)
            elif isinstance(child, ast.Attribute):
                references.append(child.attr)
            elif isinstance(child, ast.Constant) and isinstance(child.value, str):
                references.append(child.value)
        return any(
            fragment in reference.casefold()
            for reference in references
            for fragment in accounting_fragments
        )

    def closed_path_name(name: str) -> bool:
        if any(fragment in name.casefold() for fragment in accounting_fragments):
            return False
        return name == "ROOT" or name.endswith(("_ROOT", "_DIR", "_PATH"))

    def path_expression_is_proven(node: ast.AST, proven_names: set[str]) -> bool:
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "Path"
        ):
            return True
        if isinstance(node, ast.Name):
            return node.id in proven_names or closed_path_name(node.id)
        if (
            isinstance(node, ast.Attribute)
            and node.attr == "output_dir"
            and isinstance(node.value, ast.Name)
            and node.value.id == "args"
        ):
            return True
        return (
            isinstance(node, ast.BinOp)
            and isinstance(node.op, ast.Div)
            and path_expression_is_proven(node.left, proven_names)
        )

    def proven_path_names(
        scope_nodes: list[ast.AST],
        arguments: ast.arguments | None = None,
    ) -> set[str]:
        proven = set()
        if arguments is not None:
            proven.update(
                argument.arg
                for argument in (*arguments.posonlyargs, *arguments.args)
                if isinstance(argument.annotation, ast.Name)
                and argument.annotation.id == "Path"
            )
        assignments: list[tuple[str, ast.AST]] = []
        for node in scope_nodes:
            if isinstance(node, ast.Assign):
                assignments.extend(
                    (target.id, node.value)
                    for target in node.targets
                    if isinstance(target, ast.Name)
                )
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                assignments.append((node.target.id, node.value))
        changed = True
        while changed:
            changed = False
            for name, value in assignments:
                if name not in proven and path_expression_is_proven(value, proven):
                    proven.add(name)
                    changed = True
        return proven

    def is_explicit_path_join(node: ast.BinOp, proven_names: set[str]) -> bool:
        return isinstance(node.op, ast.Div) and path_expression_is_proven(
            node.left, proven_names
        )

    def is_prompt_capacity_estimate(node: ast.BinOp) -> bool:
        return (
            isinstance(node.op, ast.FloorDiv)
            and isinstance(node.left, ast.Call)
            and isinstance(node.left.func, ast.Name)
            and node.left.func.id == "len"
            and len(node.left.args) == 1
            and isinstance(node.left.args[0], ast.Name)
            and node.left.args[0].id == "SYSTEM_TEXT"
            and isinstance(node.right, ast.Constant)
            and node.right.value == 4
        )

    def sum_references_current_entries(node: ast.Call) -> bool:
        return any(
            isinstance(child, ast.Name) and child.id == "current_entries"
            for child in ast.walk(node)
        )

    def direct_attribute_parts(node: ast.AST) -> tuple[str, ...] | None:
        parts: list[str] = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if not isinstance(current, ast.Name):
            return None
        parts.append(current.id)
        return tuple(reversed(parts))

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Constant)
            and (
                (
                    type(node.value) is float
                    and node.value in forbidden_float_coefficients
                )
                or (
                    type(node.value) is int
                    and node.value in forbidden_integer_thresholds
                )
            )
        ):
            errors.append(f"legacy accounting coefficient at line {node.lineno}")
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            upper = node.value.upper()
            if "CACHE MISS" in upper or "CACHE_READ:" in upper or "FRESH_INPUT:" in upper:
                errors.append(f"legacy cache summary at line {node.lineno}")

    def scan_scope_operations(
        scope_name: str,
        scope_nodes: list[ast.AST],
        path_names: set[str],
        scope_is_accounting: bool,
    ) -> None:
        node_ids = {id(node) for node in scope_nodes}
        parents = {
            id(child): parent
            for parent in scope_nodes
            for child in ast.iter_child_nodes(parent)
            if id(child) in node_ids
        }

        def is_accounting_binop(node: ast.AST) -> bool:
            return (
                isinstance(node, ast.BinOp)
                and (references_accounting(node) or scope_is_accounting)
                and not is_explicit_path_join(node, path_names)
                and not is_prompt_capacity_estimate(node)
            )

        accounting_binops = {
            id(node) for node in scope_nodes if is_accounting_binop(node)
        }

        def has_accounting_binop_ancestor(node: ast.AST) -> bool:
            parent = parents.get(id(node))
            while parent is not None:
                if id(parent) in accounting_binops:
                    return True
                parent = parents.get(id(parent))
            return False

        for node in scope_nodes:
            if is_accounting_binop(node) and not has_accounting_binop_ancestor(node):
                errors.append(
                    f"accounting arithmetic in {scope_name} at line {node.lineno}"
                )
            if isinstance(node, ast.AugAssign) and (
                references_accounting(node) or scope_is_accounting
            ):
                errors.append(
                    f"accounting accumulation in {scope_name} at line {node.lineno}"
                )
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "sum"
                and (
                    references_accounting(node)
                    or scope_is_accounting
                    or sum_references_current_entries(node)
                    or scope_name == "current_run_totals"
                )
            ):
                continue
            if scope_name != "current_run_totals":
                errors.append(
                    f"accounting sum outside current_run_totals in {scope_name} "
                    f"at line {node.lineno}"
                )
            elif not sum_references_current_entries(node):
                errors.append(
                    "current_run_totals may sum only current_entries "
                    f"at line {node.lineno}"
                )

    module_nodes = direct_scope_nodes(tree.body)
    scan_scope_operations(
        "module",
        module_nodes,
        proven_path_names(module_nodes),
        False,
    )
    for class_node in classes():
        class_nodes = direct_scope_nodes(class_node.body)
        scan_scope_operations(
            f"class {class_node.name}",
            class_nodes,
            proven_path_names(class_nodes),
            any(
                fragment in class_node.name.casefold()
                for fragment in accounting_fragments
            ),
        )
    for function in functions():
        function_nodes = direct_scope_nodes(function.body)
        scan_scope_operations(
            function.name,
            function_nodes,
            proven_path_names(function_nodes, function.args),
            any(
                fragment in function.name.casefold()
                for fragment in accounting_fragments
            ),
        )

    build_usage = next(
        (function for function in functions() if function.name == "build_usage_v2"),
        None,
    )
    if build_usage is None:
        errors.append("build_usage_v2 missing")
    else:
        usage_aliases: set[str] = set()
        for node in ast.walk(build_usage):
            if not (
                isinstance(node, (ast.Assign, ast.AnnAssign))
                and isinstance(node.value, ast.Attribute)
                and direct_attribute_parts(node.value) == ("completion", "usage")
            ):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            usage_aliases.update(
                target.id for target in targets if isinstance(target, ast.Name)
            )
        observed_fields: dict[str, ast.AST] = {}
        for node in ast.walk(build_usage):
            if not isinstance(node, ast.Dict):
                continue
            for key, value in zip(node.keys, node.values, strict=True):
                if (
                    isinstance(key, ast.Constant)
                    and isinstance(key.value, str)
                    and key.value in accounting_fields
                ):
                    observed_fields[key.value] = value
        if set(observed_fields) != accounting_fields:
            errors.append("build_usage_v2 accounting fields must be exact")
        for field, value in observed_fields.items():
            parts = direct_attribute_parts(value)
            expected_leaf = "cost" if field == "cost_usd" else field
            if parts is None or parts[-1] != expected_leaf or not (
                parts[:-1] == ("completion", "usage")
                or (len(parts) == 2 and parts[0] in usage_aliases)
            ):
                errors.append(
                    f"build_usage_v2 must copy completion usage field {field}"
                )

    main = next(
        (
            node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "main"
        ),
        None,
    )
    if main is None:
        return [*errors, "main missing"]
    totals_calls = [
        node
        for node in ast.walk(main)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "current_run_totals"
    ]
    if len(totals_calls) != 1:
        errors.append("main must call current_run_totals exactly once")
    elif not (
        len(totals_calls[0].args) == 1
        and isinstance(totals_calls[0].args[0], ast.Name)
        and totals_calls[0].args[0].id == "current_entries"
    ):
        errors.append("current_run_totals must receive only current_entries")
    return errors


def _install_campaign_main_doubles(
    monkeypatch: pytest.MonkeyPatch,
    campaign: Any,
    output_dir: Path,
    call_openrouter_judge: Callable[..., object],
) -> None:
    monkeypatch.setattr(campaign, "load_programme", _programme)
    monkeypatch.setattr(campaign, "find_sequences_for_capacity", lambda cap: ["P01"])
    monkeypatch.setattr(campaign, "build_sequence_context", lambda seq, cap: "sequence context")
    monkeypatch.setattr(campaign, "build_capacity_prompt", lambda cap, programme: "capacity prompt")
    monkeypatch.setattr(campaign, "validate_verdict_file", lambda path: [])
    monkeypatch.setattr(campaign, "call_openrouter_judge", call_openrouter_judge)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "judge_campaign.py",
            "--cap-ids",
            CAPACITY_ID,
            "--force",
            "--output-dir",
            str(output_dir),
        ],
    )


def test_campaign_delegates_to_shared_openrouter_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    campaign = _campaign()
    sentinel = object()
    seen: list[dict[str, object]] = []

    def fake_chat_completion(**kwargs: object) -> object:
        seen.append(kwargs)
        return sentinel

    monkeypatch.setattr(campaign, "chat_completion", fake_chat_completion)
    transport = object()
    result = campaign.call_openrouter_judge(
        API_KEY,
        MODEL,
        "contexte exact",
        "prompt exact",
        transport=transport,
    )

    assert result is sentinel
    assert seen == [
        {
            "api_key": API_KEY,
            "model": MODEL,
            "messages": [
                {"role": "system", "content": campaign.SYSTEM_TEXT},
                {"role": "user", "content": "contexte exact\n\nprompt exact"},
            ],
            "max_completion_tokens": 2500,
            "transport": transport,
        }
    ]


def test_campaign_reads_missing_openrouter_values_from_resolved_rag_env(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    campaign = _campaign()
    env_path = tmp_path / ".env.rag"
    env_path.write_text(
        "OPENROUTER_API_KEY=file-key\nOPENROUTER_MODEL=file/model\n"
        "ANTHROPIC_API_KEY=must-be-ignored\n",
        encoding="utf-8",
    )
    resolve_calls: list[Path] = []
    calls: list[tuple[str, str]] = []

    def resolve(root: Path) -> Path:
        resolve_calls.append(root)
        return env_path

    def fake_call(
        api_key: str,
        model: str,
        seq_context: str,
        capacity_prompt: str,
        **kwargs: object,
    ) -> object:
        calls.append((api_key, model))
        return _completion(content=json.dumps(_campaign_result()))

    monkeypatch.setattr(campaign, "resolve_env_file", resolve)
    monkeypatch.setenv("OPENROUTER_API_KEY", "environment-key")
    monkeypatch.setenv("OPENROUTER_MODEL", " ")
    _install_campaign_main_doubles(
        monkeypatch,
        campaign,
        tmp_path / "first",
        fake_call,
    )
    assert campaign.main() == 0

    monkeypatch.setenv("OPENROUTER_API_KEY", " ")
    monkeypatch.setenv("OPENROUTER_MODEL", "environment/model")
    _install_campaign_main_doubles(
        monkeypatch,
        campaign,
        tmp_path / "second",
        fake_call,
    )
    assert campaign.main() == 0

    assert resolve_calls == [CORPUS_ROOT, CORPUS_ROOT]
    assert env_path.name == ".env.rag"
    assert calls == [
        ("environment-key", "file/model"),
        ("file-key", "environment/model"),
    ]


def test_campaign_does_not_read_generic_dotenv(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    campaign = _campaign()
    client = _client()
    generic_env = CORPUS_ROOT / ".env"
    generic_payload = (
        "OPENROUTER_API_KEY=generic-key-sentinel\n"
        "OPENROUTER_MODEL=generic/model-sentinel\n"
    )
    resolve_calls: list[Path] = []
    generic_accesses: list[tuple[str, Path]] = []
    calls: list[tuple[str, str]] = []
    active_rag_env = [tmp_path / "complete" / ".env.rag"]
    original_exists = Path.exists
    original_read_text = Path.read_text
    original_path_open = Path.open
    original_builtin_open = builtins.open

    def reject_generic(operation: str, path: Path) -> None:
        generic_accesses.append((operation, path))
        raise AssertionError(
            f"CORPUS_ROOT/.env access forbidden ({operation}): {generic_payload}"
        )

    def guarded_exists(path: Path) -> bool:
        if path == generic_env:
            reject_generic("exists", path)
        return original_exists(path)

    def guarded_read_text(path: Path, *args: object, **kwargs: object) -> str:
        if path == generic_env:
            reject_generic("read_text", path)
        return original_read_text(path, *args, **kwargs)

    def guarded_path_open(path: Path, *args: object, **kwargs: object) -> Any:
        if path == generic_env:
            reject_generic("Path.open", path)
        return original_path_open(path, *args, **kwargs)

    def guarded_builtin_open(file: object, *args: object, **kwargs: object) -> Any:
        if isinstance(file, (str, Path)) and Path(file) == generic_env:
            reject_generic("open", Path(file))
        return original_builtin_open(file, *args, **kwargs)

    def resolve(root: Path) -> Path:
        resolve_calls.append(root)
        return active_rag_env[0]

    def fake_call(
        api_key: str,
        model: str,
        seq_context: str,
        capacity_prompt: str,
        **kwargs: object,
    ) -> object:
        calls.append((api_key, model))
        return _completion(content=json.dumps(_campaign_result()))

    monkeypatch.setattr(Path, "exists", guarded_exists)
    monkeypatch.setattr(Path, "read_text", guarded_read_text)
    monkeypatch.setattr(Path, "open", guarded_path_open)
    monkeypatch.setattr(builtins, "open", guarded_builtin_open)
    monkeypatch.setattr(campaign, "resolve_env_file", resolve)

    cases = (
        (
            "complete",
            "OPENROUTER_API_KEY=rag-key\nOPENROUTER_MODEL=rag/model\n",
            "",
            "",
            ("rag-key", "rag/model"),
        ),
        (
            "absent",
            None,
            "environment-key",
            "environment/model",
            ("environment-key", "environment/model"),
        ),
        (
            "missing-key",
            "OPENROUTER_MODEL=file/model-only\n",
            "environment-key-only",
            "",
            ("environment-key-only", "file/model-only"),
        ),
        (
            "missing-model",
            "OPENROUTER_API_KEY=file-key-only\n",
            "",
            "environment/model-only",
            ("file-key-only", "environment/model-only"),
        ),
    )
    for label, rag_payload, env_key, env_model, expected in cases:
        rag_env = tmp_path / label / ".env.rag"
        rag_env.parent.mkdir(parents=True)
        if rag_payload is not None:
            rag_env.write_text(rag_payload, encoding="utf-8")
        assert rag_env.name == ".env.rag"
        active_rag_env[0] = rag_env
        if env_key:
            monkeypatch.setenv("OPENROUTER_API_KEY", env_key)
        else:
            monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        if env_model:
            monkeypatch.setenv("OPENROUTER_MODEL", env_model)
        else:
            monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
        _install_campaign_main_doubles(
            monkeypatch,
            campaign,
            tmp_path / f"output-{label}",
            fake_call,
        )
        assert campaign.main() == 0
        assert calls[-1] == expected

    rejected_cases = (
        ("absent-unresolved", None),
        ("key-only-unresolved", "OPENROUTER_API_KEY=file-key-alone\n"),
        ("model-only-unresolved", "OPENROUTER_MODEL=file/model-alone\n"),
    )
    for label, rag_payload in rejected_cases:
        rag_env = tmp_path / label / ".env.rag"
        rag_env.parent.mkdir(parents=True)
        if rag_payload is not None:
            rag_env.write_text(rag_payload, encoding="utf-8")
        active_rag_env[0] = rag_env
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
        before_transport_calls = len(calls)
        _install_campaign_main_doubles(
            monkeypatch,
            campaign,
            tmp_path / f"output-{label}",
            fake_call,
        )
        try:
            result = campaign.main()
        except client.OpenRouterError as error:
            assert error.category == "configuration"
        else:
            assert result == 1
        assert len(calls) == before_transport_calls

    all_cases_count = len(cases) + len(rejected_cases)
    assert resolve_calls == [CORPUS_ROOT] * all_cases_count
    assert generic_accesses == []
    assert calls == [case[-1] for case in cases]
    assert all("generic" not in value for pair in calls for value in pair)


def test_campaign_rejects_key_without_model_before_transport(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    campaign = _campaign()
    client = _client()
    calls = 0

    def forbidden_transport(**kwargs: object) -> object:
        nonlocal calls
        calls += 1
        raise AssertionError(f"transport called: {kwargs}")

    monkeypatch.setattr(campaign, "chat_completion", forbidden_transport)
    with pytest.raises(client.OpenRouterError) as caught:
        campaign.load_openrouter_config(
            {"OPENROUTER_API_KEY": API_KEY, "OPENROUTER_MODEL": "  "},
            tmp_path / ".env.rag",
        )
    assert caught.value.category == "configuration"
    assert calls == 0


def test_campaign_business_retry_count_is_bounded(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    campaign = _campaign()
    client = _client()
    monkeypatch.setenv("OPENROUTER_API_KEY", API_KEY)
    monkeypatch.setenv("OPENROUTER_MODEL", MODEL)
    retryable = ("rate_limit", "timeout", "transport", "unavailable")
    non_retryable = (
        "configuration",
        "authentication",
        "authorization",
        "protocol",
        "payment",
    )
    for category in (*retryable, *non_retryable):
        attempts = 0
        delays: list[float] = []

        class CategorizedError(client.OpenRouterError):
            def __init__(self) -> None:
                Exception.__init__(self, f"sanitized {category}")
                self.category = category

        def fail(*args: object, **kwargs: object) -> object:
            nonlocal attempts
            attempts += 1
            raise CategorizedError

        output_dir = tmp_path / category
        monkeypatch.setattr(campaign.time, "sleep", delays.append)
        _install_campaign_main_doubles(monkeypatch, campaign, output_dir, fail)

        assert campaign.main() == 0
        expected_attempts = 3 if category in retryable else 1
        assert attempts == expected_attempts
        assert delays == ([2, 4] if category in retryable else [])
        usage = json.loads(
            (output_dir / "_usage_log.json").read_text(encoding="utf-8")
        )
        assert usage[-1]["error_category"] == category
        review = json.loads(
            (
                output_dir / f"{CAPACITY_ID}_substance_review.json"
            ).read_text(encoding="utf-8")
        )
        assert review["capacities"][0]["verdict"] == "needs_content"


def test_campaign_records_requested_openrouter_model(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    campaign = _campaign()
    output_dir = tmp_path / "campaign"
    calls: list[str] = []

    def fake_call(
        api_key: str,
        model: str,
        seq_context: str,
        capacity_prompt: str,
        **kwargs: object,
    ) -> object:
        calls.append(model)
        return _completion(
            content=json.dumps(_campaign_result()),
            model=MODEL_RETURNED,
        )

    monkeypatch.setenv("OPENROUTER_API_KEY", API_KEY)
    monkeypatch.setenv("OPENROUTER_MODEL", MODEL_REQUESTED)
    _install_campaign_main_doubles(monkeypatch, campaign, output_dir, fake_call)

    assert campaign.main() == 0

    review = json.loads(
        (output_dir / f"{CAPACITY_ID}_substance_review.json").read_text(
            encoding="utf-8"
        )
    )
    assert calls == [MODEL_REQUESTED]
    assert review["judge_model"] == MODEL_REQUESTED
    assert review["judge_model"] != MODEL_RETURNED
    assert review["judge_model"] != getattr(campaign, "MODEL", None)

    valid_result = _campaign_result()
    serialized = json.dumps(valid_result)
    for accepted in (
        serialized,
        f"```json\n{serialized}\n```",
    ):
        assert campaign.parse_campaign_verdict(accepted) == valid_result
    for rejected in (
        f"```JSON\n{serialized}\n```",
        f"```\n{serialized}\n```",
        f"texte périphérique\n{serialized}",
        f"```json\n{serialized}\n```\ntexte périphérique",
        f"```json\n{serialized}\n```\n```json\n{serialized}\n```",
    ):
        with pytest.raises((json.JSONDecodeError, ValueError)):
            campaign.parse_campaign_verdict(rejected)


def test_campaign_records_each_billed_retry_generation_before_verdict_validation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    campaign = _campaign()
    output_dir = tmp_path / "campaign"
    events: list[str] = []
    first = _completion(content="first", generation_id="gen-first", cost=0.001)
    second = _completion(
        content="second",
        generation_id="gen-second",
        cost=0.009,
    )
    completions = [first, second]
    original_merge = campaign.merge_usage_log

    def fake_call(*args: object, **kwargs: object) -> object:
        completion = completions.pop(0)
        events.append(f"call:{completion.generation_id}")
        return completion

    def traced_merge(
        existing: list[dict[str, object]],
        incoming: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        for entry in incoming:
            generation = entry.get("generation_id")
            if generation:
                events.append(f"journal:{generation}")
        return original_merge(existing, incoming)

    def traced_parse(content: str) -> dict[str, object]:
        persisted = json.loads(
            (output_dir / "_usage_log.json").read_text(encoding="utf-8")
        )
        if content == "first":
            assert [entry["generation_id"] for entry in persisted] == [
                "gen-first"
            ]
            assert [entry["cost_usd"] for entry in persisted] == [0.001]
        else:
            assert [entry["generation_id"] for entry in persisted] == [
                "gen-first",
                "gen-second",
            ]
            assert [entry["cost_usd"] for entry in persisted] == [0.001, 0.009]
        events.append(f"validate:{content}")
        if content == "first":
            raise ValueError("invalid first verdict")
        assert content == "second"
        return {
            "proof_course": {
                "present": True,
                "file": "cours.md",
                "anchor": "#cours",
                "quote": "Preuve de cours qui sera rejetée par le gate.",
            },
            "proof_practice": {
                "present": True,
                "file": "td.md",
                "anchor": "#exercice",
                "quote": "Preuve de pratique distincte qui doit être conservée.",
            },
            "proof_correction": {
                "present": True,
                "file": "corrige.md",
                "anchor": "#correction",
                "quote": "Preuve de correction distincte qui doit être conservée.",
            },
            "comment": "Deux rôles valides doivent survivre à la dégradation ciblée.",
        }

    def validate_candidate(path: Path) -> list[str]:
        review = json.loads(path.read_text(encoding="utf-8"))
        capacity = review["capacities"][0]
        if capacity["proof_course"]["present"]:
            return ["proof_course: citation invalide"]
        return []

    monkeypatch.setenv("OPENROUTER_API_KEY", API_KEY)
    monkeypatch.setenv("OPENROUTER_MODEL", MODEL)
    monkeypatch.setattr(campaign, "merge_usage_log", traced_merge)
    monkeypatch.setattr(campaign, "parse_campaign_verdict", traced_parse)
    _install_campaign_main_doubles(monkeypatch, campaign, output_dir, fake_call)
    monkeypatch.setattr(campaign, "validate_verdict_file", validate_candidate)

    assert campaign.main() == 0
    assert events == [
        "call:gen-first",
        "journal:gen-first",
        "validate:first",
        "call:gen-second",
        "journal:gen-second",
        "validate:second",
    ]
    entries = json.loads((output_dir / "_usage_log.json").read_text(encoding="utf-8"))
    assert [entry["generation_id"] for entry in entries] == ["gen-first", "gen-second"]
    assert [entry["cost_usd"] for entry in entries] == [0.001, 0.009]
    review = json.loads(
        (output_dir / f"{CAPACITY_ID}_substance_review.json").read_text(
            encoding="utf-8"
        )
    )
    capacity = review["capacities"][0]
    assert capacity["proof_course"] == {
        "present": False,
        "file": None,
        "anchor": None,
        "quote": None,
        "teaches": False,
    }
    assert capacity["proof_practice"] == {
        "present": True,
        "file": "td.md",
        "anchor": "#exercice",
        "quote": "Preuve de pratique distincte qui doit être conservée.",
        "teaches": True,
    }
    assert capacity["proof_correction"] == {
        "present": True,
        "file": "corrige.md",
        "anchor": "#correction",
        "quote": "Preuve de correction distincte qui doit être conservée.",
        "teaches": True,
    }
    assert capacity["verdict"] == "needs_review"

    absent_proof = {
        "present": False,
        "file": None,
        "anchor": None,
        "quote": None,
        "teaches": False,
    }
    present_proofs = {
        "proof_course": {
            "present": True,
            "file": "cours.md",
            "anchor": "#cours",
            "quote": "Preuve de cours distincte qui doit être conservée.",
            "teaches": True,
        },
        "proof_practice": {
            "present": True,
            "file": "entrainement.md",
            "anchor": "#exercice",
            "quote": "Preuve d'entraînement distincte qui doit être conservée.",
            "teaches": True,
        },
        "proof_correction": {
            "present": True,
            "file": "corrige.md",
            "anchor": "#correction",
            "quote": "Preuve de correction distincte qui doit être conservée.",
            "teaches": True,
        },
    }

    def complete_judge_result() -> dict[str, object]:
        return {
            role: {
                key: value
                for key, value in proof.items()
                if key != "teaches"
            }
            for role, proof in present_proofs.items()
        } | {
            "comment": "Chaque rôle fournit une preuve indépendante et vérifiable."
        }

    quality_errors: list[str] = []

    def run_gate_scenario(
        label: str,
        first_gate_error: str,
        *,
        expected_failed_role: str | None,
        second_gate_error: str | None = None,
    ) -> None:
        scenario_output = tmp_path / label
        final_path = scenario_output / f"{CAPACITY_ID}_substance_review.json"
        sentinel = b'{"existing":"must survive a red gate"}\n'
        if expected_failed_role is None or second_gate_error is not None:
            scenario_output.mkdir(parents=True, exist_ok=True)
            final_path.write_bytes(sentinel)

        scenario_completions = [
            _completion(
                content=f"invalid-{label}",
                generation_id=f"gen-{label}-first",
            ),
            _completion(
                content=f"candidate-{label}",
                generation_id=f"gen-{label}-second",
            ),
        ]
        validation_snapshots: list[dict[str, object]] = []

        def scenario_call(*args: object, **kwargs: object) -> object:
            return scenario_completions.pop(0)

        def scenario_parse(content: str) -> dict[str, object]:
            if content == f"invalid-{label}":
                raise ValueError("force the billed logical retry")
            assert content == f"candidate-{label}"
            return complete_judge_result()

        def scenario_validate(path: Path) -> list[str]:
            candidate_review = json.loads(path.read_text(encoding="utf-8"))
            validation_snapshots.append(
                copy.deepcopy(candidate_review["capacities"][0])
            )
            if len(validation_snapshots) == 1:
                return [first_gate_error]
            return [second_gate_error] if second_gate_error is not None else []

        result: int | None = None
        raised: Exception | None = None
        with monkeypatch.context() as scenario_patch:
            scenario_patch.setenv("OPENROUTER_API_KEY", API_KEY)
            scenario_patch.setenv("OPENROUTER_MODEL", MODEL)
            _install_campaign_main_doubles(
                scenario_patch,
                campaign,
                scenario_output,
                scenario_call,
            )
            scenario_patch.setattr(campaign, "parse_campaign_verdict", scenario_parse)
            scenario_patch.setattr(campaign, "validate_verdict_file", scenario_validate)
            try:
                result = campaign.main()
            except Exception as error:  # the fail-closed path may be exceptional
                raised = error

        if not validation_snapshots:
            quality_errors.append(f"{label}: original candidate was not validated")
        else:
            for role, expected in present_proofs.items():
                if validation_snapshots[0][role] != expected:
                    quality_errors.append(
                        f"{label}: original tmp changed {role} to "
                        f"{validation_snapshots[0][role]!r}, expected {expected!r}"
                    )
        if expected_failed_role is not None and len(validation_snapshots) >= 2:
            for role, expected in present_proofs.items():
                role_expected = absent_proof if role == expected_failed_role else expected
                if validation_snapshots[1][role] != role_expected:
                    quality_errors.append(
                        f"{label}: degraded tmp changed {role} to "
                        f"{validation_snapshots[1][role]!r}, "
                        f"expected {role_expected!r}"
                    )

        if expected_failed_role is None:
            if final_path.read_bytes() != sentinel:
                quality_errors.append(
                    f"{label}: an unattributable gate error replaced the final verdict"
                )
            return

        if second_gate_error is not None:
            if len(validation_snapshots) != 2:
                quality_errors.append(
                    f"{label}: degraded candidate was not validated a second time"
                )
            if final_path.read_bytes() != sentinel:
                quality_errors.append(
                    f"{label}: a candidate failing its second gate replaced the final verdict"
                )
            return

        if raised is not None or result != 0:
            quality_errors.append(
                f"{label}: a role-attributable candidate did not complete: {raised!r}"
            )
            return
        if len(validation_snapshots) != 2:
            quality_errors.append(
                f"{label}: degraded candidate was not validated a second time"
            )
        if not final_path.is_file():
            quality_errors.append(f"{label}: validated degraded verdict was not promoted")
            return
        final_capacity = json.loads(final_path.read_text(encoding="utf-8"))[
            "capacities"
        ][0]
        for role, expected in present_proofs.items():
            role_expected = absent_proof if role == expected_failed_role else expected
            if final_capacity[role] != role_expected:
                quality_errors.append(
                    f"{label}: {role} changed to {final_capacity[role]!r}, "
                    f"expected {role_expected!r}"
                )

    role_scenarios = (
        ("marker-course", "[cours] citation invalide", "proof_course"),
        (
            "marker-practice-duplicate",
            "[entraînement] citation dupliquée (identique à cours)",
            "proof_practice",
        ),
        (
            "marker-practice-file",
            "[entraînement] present=true mais file manquant",
            "proof_practice",
        ),
        (
            "marker-correction",
            "[correction] ancre introuvable",
            "proof_correction",
        ),
        (
            "exact-proof-practice",
            "proof_practice: citation invalide",
            "proof_practice",
        ),
        (
            "exact-proof-correction",
            "proof_correction: citation invalide",
            "proof_correction",
        ),
    )
    for scenario_label, gate_error, failed_role in role_scenarios:
        run_gate_scenario(
            scenario_label,
            gate_error,
            expected_failed_role=failed_role,
        )

    run_gate_scenario(
        "unattributable-http",
        "erreur globale du protocole HTTP sans rôle attribuable",
        expected_failed_role=None,
    )
    run_gate_scenario(
        "unattributable-stdout",
        "erreur globale stdout illisible sans rôle attribuable",
        expected_failed_role=None,
    )
    run_gate_scenario(
        "second-gate-red",
        "[entraînement] citation invalide",
        expected_failed_role="proof_practice",
        second_gate_error="erreur globale persistante après dégradation",
    )

    assert quality_errors == []


def test_usage_v2_copies_completion_accounting_exactly() -> None:
    campaign = _campaign()
    completion = _completion(
        generation_id="gen-exact",
        prompt_tokens=101,
        completion_tokens=23,
        cost=0.123456789,
        cached_tokens=47,
        cache_write_tokens=13,
    )

    entry = campaign.build_usage_v2(
        cap=CAPACITY_ID,
        seq="P01",
        attempt=2,
        judged_at=JUDGED_AT,
        completion=completion,
    )

    assert set(entry) == {
        "schema_version",
        "provider",
        "cap",
        "seq",
        "attempt",
        "judged_at",
        "model",
        "generation_id",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "cached_tokens",
        "cache_write_tokens",
        "cost_usd",
    }
    assert entry == {
        "schema_version": 2,
        "provider": "openrouter",
        "cap": CAPACITY_ID,
        "seq": "P01",
        "attempt": 2,
        "judged_at": JUDGED_AT,
        "model": MODEL,
        "generation_id": "gen-exact",
        "prompt_tokens": 101,
        "completion_tokens": 23,
        "total_tokens": 124,
        "cached_tokens": 47,
        "cache_write_tokens": 13,
        "cost_usd": 0.123456789,
    }
    assert "run_id" not in entry


def test_usage_upsert_replaces_same_generation_only() -> None:
    campaign = _campaign()
    old = {"schema_version": 2, "generation_id": "gen-same", "cost_usd": 1.0}
    replacement = {"schema_version": 2, "generation_id": "gen-same", "cost_usd": 2.0}

    merged = campaign.merge_usage_log([old], [replacement])

    assert merged == [replacement]
    assert sum(row.get("generation_id") == "gen-same" for row in merged) == 1


def test_usage_upsert_preserves_v1_deeply_and_in_order(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    campaign = _campaign()
    v1 = [
        {
            "cap": CAPACITY_ID,
            "seq": "P01",
            "read": 4,
            "nested": {"values": [1, 2]},
        },
        {
            "cap": CAPACITY_ID,
            "seq": "P01",
            "write": 8,
            "fresh": 3,
            "out": 2,
        },
    ]
    fixture = tmp_path / "usage.json"
    fixture.write_text(json.dumps(v1), encoding="utf-8")
    loaded = json.loads(fixture.read_text(encoding="utf-8"))
    before = copy.deepcopy(loaded)
    new = {
        "schema_version": 2,
        "cap": CAPACITY_ID,
        "seq": "P01",
        "generation_id": "gen-new",
        "cost_usd": 0.3,
    }

    merged = campaign.merge_usage_log(loaded, [new])

    assert loaded == before
    assert merged[: len(before)] == before
    assert merged[-1] == new
    replaced_by_capacity = [
        row for row in before if row.get("cap") != new["cap"]
    ] + [new]
    assert replaced_by_capacity != merged

    journal_errors: list[str] = []

    def run_campaign(
        patch: pytest.MonkeyPatch,
        output_dir: Path,
        *,
        generation_id: str,
    ) -> tuple[int | None, Exception | None, int]:
        calls = 0

        def fake_call(*args: object, **kwargs: object) -> object:
            nonlocal calls
            calls += 1
            return _completion(
                content=json.dumps(_campaign_result()),
                generation_id=generation_id,
            )

        patch.setenv("OPENROUTER_API_KEY", API_KEY)
        patch.setenv("OPENROUTER_MODEL", MODEL)
        _install_campaign_main_doubles(patch, campaign, output_dir, fake_call)
        try:
            return campaign.main(), None, calls
        except Exception as error:  # a protocol stop may be exceptional
            return None, error, calls

    malformed_cases = (
        ("malformed-json", b"{not-json\n"),
        ("non-list", b'{"schema_version":2}\n'),
        ("non-dict-entry", b'[1, {"schema_version":1}]\n'),
    )
    for label, original_bytes in malformed_cases:
        malformed_output = tmp_path / label
        malformed_output.mkdir()
        malformed_log = malformed_output / "_usage_log.json"
        malformed_log.write_bytes(original_bytes)
        with monkeypatch.context() as malformed_patch:
            return_code, raised, calls = run_campaign(
                malformed_patch,
                malformed_output,
                generation_id=f"gen-{label}",
            )
        stopped_as_protocol = (
            return_code not in (None, 0)
            or (
                getattr(raised, "category", None) == "protocol"
                and raised.__class__.__name__ == "OpenRouterError"
            )
        )
        if not stopped_as_protocol:
            journal_errors.append(f"{label}: invalid history did not stop as protocol")
        if calls != 0:
            journal_errors.append(f"{label}: API called after invalid history")
        if malformed_log.read_bytes() != original_bytes:
            journal_errors.append(f"{label}: invalid history was overwritten")

    unreadable_output = tmp_path / "unreadable"
    unreadable_output.mkdir()
    unreadable_log = unreadable_output / "_usage_log.json"
    unreadable_bytes = b'[{"schema_version":1,"opaque":"preserve"}]\n'
    unreadable_log.write_bytes(unreadable_bytes)
    real_read_text = Path.read_text

    def fail_usage_read(path: Path, *args: object, **kwargs: object) -> str:
        if path == unreadable_log:
            raise OSError("simulated unreadable usage journal")
        return real_read_text(path, *args, **kwargs)

    with monkeypatch.context() as unreadable_patch:
        unreadable_patch.setattr(Path, "read_text", fail_usage_read)
        return_code, raised, calls = run_campaign(
            unreadable_patch,
            unreadable_output,
            generation_id="gen-unreadable",
        )
    stopped_as_protocol = (
        return_code not in (None, 0)
        or (
            getattr(raised, "category", None) == "protocol"
            and raised.__class__.__name__ == "OpenRouterError"
        )
    )
    if not stopped_as_protocol:
        journal_errors.append("unreadable: OSError did not stop as protocol")
    if calls != 0:
        journal_errors.append("unreadable: API called after journal read OSError")
    if unreadable_log.read_bytes() != unreadable_bytes:
        journal_errors.append("unreadable: journal was overwritten after read OSError")

    atomic_output = tmp_path / "atomic-success"
    atomic_output.mkdir()
    atomic_log = atomic_output / "_usage_log.json"
    atomic_original = json.dumps(v1, ensure_ascii=False).encode() + b"\n"
    atomic_log.write_bytes(atomic_original)
    real_fsync = campaign.os.fsync
    real_open = campaign.os.open
    real_close = campaign.os.close
    real_replace = campaign.os.replace
    atomic_events: list[tuple[str, Path, int | None]] = []
    flushed_payloads: dict[Path, bytes] = {}
    replaced_payloads: dict[Path, bytes] = {}
    directory_fds: dict[int, Path] = {}
    journal_observation_complete = False

    def fd_path(fd: int) -> Path | None:
        try:
            return Path(campaign.os.readlink(f"/proc/self/fd/{fd}"))
        except OSError:
            return None

    def trace_fsync(fd: int) -> None:
        if fd in directory_fds:
            atomic_events.append(("dir_fsync", directory_fds[fd], fd))
            real_fsync(fd)
            return
        target = fd_path(fd)
        if target is not None and target.parent == atomic_log.parent:
            payload = target.read_bytes()
            try:
                json.loads(payload)
            except (UnicodeDecodeError, json.JSONDecodeError):
                journal_errors.append("atomic-success: payload was not flushed before fsync")
            flushed_payloads[target] = payload
            atomic_events.append(("payload_fsync", target, fd))
        real_fsync(fd)

    def trace_open(
        path: object,
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if dir_fd is None:
            fd = real_open(path, flags, mode)
        else:
            fd = real_open(path, flags, mode, dir_fd=dir_fd)
        if (
            not journal_observation_complete
            and Path(path) == atomic_log.parent
        ):
            directory_fds[fd] = atomic_log.parent
            atomic_events.append(("dir_open", atomic_log.parent, fd))
        return fd

    def trace_close(fd: int) -> None:
        nonlocal journal_observation_complete
        directory = directory_fds.get(fd)
        real_close(fd)
        if directory is not None:
            atomic_events.append(("dir_close", directory, fd))
            directory_fds.pop(fd)
            journal_observation_complete = True

    def trace_replace(source: object, destination: object) -> None:
        source_path = Path(source)
        destination_path = Path(destination)
        if destination_path == atomic_log:
            if source_path == destination_path:
                journal_errors.append("atomic-success: in-place replace is forbidden")
            if source_path.parent != atomic_log.parent:
                journal_errors.append("atomic-success: temp file is not a sibling")
            replaced_payloads[source_path] = source_path.read_bytes()
            atomic_events.append(("replace", source_path, None))
        real_replace(source, destination)

    with monkeypatch.context() as atomic_patch:
        atomic_patch.setattr(campaign.os, "fsync", trace_fsync)
        atomic_patch.setattr(campaign.os, "open", trace_open)
        atomic_patch.setattr(campaign.os, "close", trace_close)
        atomic_patch.setattr(campaign.os, "replace", trace_replace)
        return_code, raised, calls = run_campaign(
            atomic_patch,
            atomic_output,
            generation_id="gen-atomic-success",
        )
    if raised is not None or return_code != 0 or calls != 1:
        journal_errors.append(
            f"atomic-success: campaign did not complete cleanly: {raised!r}"
        )
    usage_replaces = [event for event in atomic_events if event[0] == "replace"]
    if len(usage_replaces) != 1:
        journal_errors.append("atomic-success: usage journal was not replaced atomically")
    else:
        temp_path = usage_replaces[0][1]
        lifecycle = {
            name: [event for event in atomic_events if event[0] == name]
            for name in ("payload_fsync", "replace", "dir_open", "dir_fsync", "dir_close")
        }
        primary_payload_fsync = [
            event for event in lifecycle["payload_fsync"] if event[1] == temp_path
        ]
        recovery_payload_fsync = [
            event
            for event in lifecycle["payload_fsync"]
            if event[1].name.endswith(".recovery.tmp")
        ]
        if not (
            len(primary_payload_fsync) == 1
            and len(recovery_payload_fsync) == 1
            and len(lifecycle["replace"]) == 1
            and len(lifecycle["dir_open"]) == 1
            and len(lifecycle["dir_fsync"]) == 2
            and len(lifecycle["dir_close"]) == 1
        ):
            journal_errors.append(
                f"atomic-success: durability lifecycle differs: {atomic_events!r}"
            )
        else:
            payload_fsync_event = primary_payload_fsync[0]
            recovery_fsync_event = recovery_payload_fsync[0]
            replace_event = lifecycle["replace"][0]
            directory_open_event = lifecycle["dir_open"][0]
            backup_directory_fsync_event = lifecycle["dir_fsync"][0]
            primary_directory_fsync_event = lifecycle["dir_fsync"][1]
            directory_close_event = lifecycle["dir_close"][0]
            directory_fsync_indices = [
                index
                for index, event in enumerate(atomic_events)
                if event[0] == "dir_fsync"
            ]
            if not (
                atomic_events.index(recovery_fsync_event)
                < directory_fsync_indices[0]
                < atomic_events.index(payload_fsync_event)
                < atomic_events.index(replace_event)
                < directory_fsync_indices[1]
                < atomic_events.index(directory_close_event)
            ):
                journal_errors.append(
                    f"atomic-success: durability causal order differs: {atomic_events!r}"
                )
            if atomic_events.index(directory_open_event) >= atomic_events.index(
                backup_directory_fsync_event
            ):
                journal_errors.append(
                    "atomic-success: directory was not opened before its fsync"
                )
            directory_lifecycle_fds = {
                directory_open_event[2],
                backup_directory_fsync_event[2],
                primary_directory_fsync_event[2],
                directory_close_event[2],
            }
            if len(directory_lifecycle_fds) != 1 or None in directory_lifecycle_fds:
                journal_errors.append(
                    "atomic-success: open/fsync/close did not use the same directory fd"
                )
        if directory_fds:
            journal_errors.append("atomic-success: directory descriptor leaked")
        if flushed_payloads.get(temp_path) != replaced_payloads.get(temp_path):
            journal_errors.append("atomic-success: bytes changed between fsync and replace")
        if atomic_log.read_bytes() != replaced_payloads.get(temp_path):
            journal_errors.append("atomic-success: replace did not install complete bytes")
    try:
        atomic_entries = json.loads(atomic_log.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        atomic_entries = []
    if atomic_entries[: len(v1)] != v1 or [
        row.get("generation_id") for row in atomic_entries[len(v1) :]
    ] != ["gen-atomic-success"]:
        journal_errors.append("atomic-success: ordered v1 history was not preserved")

    fault_output = tmp_path / "atomic-fault"
    fault_output.mkdir()
    fault_log = fault_output / "_usage_log.json"
    fault_original = b'[{"schema_version":1,"opaque":{"nested":[1,2]}}]\n'
    fault_log.write_bytes(fault_original)
    fault_triggered = False

    def fail_before_replace(fd: int) -> None:
        nonlocal fault_triggered
        target = fd_path(fd)
        if target is not None and target.parent == fault_log.parent:
            fault_triggered = True
            raise OSError("simulated failure after flush and before replace")
        real_fsync(fd)

    with monkeypatch.context() as fault_patch:
        fault_patch.setattr(campaign.os, "fsync", fail_before_replace)
        return_code, raised, calls = run_campaign(
            fault_patch,
            fault_output,
            generation_id="gen-atomic-fault",
        )
    if not fault_triggered:
        journal_errors.append("atomic-fault: no flush/fsync occurred before replace")
    if raised is None and return_code == 0:
        journal_errors.append("atomic-fault: pre-replace failure did not stop campaign")
    if calls != 1:
        journal_errors.append(f"atomic-fault: expected one billed call, observed {calls}")
    if fault_log.read_bytes() != fault_original:
        journal_errors.append("atomic-fault: original bytes changed before replace")

    directory_fault_output = tmp_path / "directory-fsync-fault"
    directory_fault_output.mkdir()
    directory_fault_log = directory_fault_output / "_usage_log.json"
    directory_fault_log.write_bytes(atomic_original)
    directory_fault_fds: set[int] = set()
    directory_fault_events: list[tuple[str, int]] = []
    directory_fault_primary_replaced = False

    def trace_directory_fault_open(
        path: object,
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if dir_fd is None:
            fd = real_open(path, flags, mode)
        else:
            fd = real_open(path, flags, mode, dir_fd=dir_fd)
        if (
            Path(path) == directory_fault_output
        ):
            directory_fault_fds.add(fd)
            directory_fault_events.append(("open", fd))
        return fd

    def fail_directory_fsync(fd: int) -> None:
        if fd in directory_fault_fds:
            directory_fault_events.append(("fsync", fd))
            if directory_fault_primary_replaced:
                raise OSError("simulated directory fsync failure")
        real_fsync(fd)

    def trace_directory_fault_replace(source: object, destination: object) -> None:
        nonlocal directory_fault_primary_replaced
        if Path(destination) == directory_fault_log:
            directory_fault_primary_replaced = True
        real_replace(source, destination)

    def trace_directory_fault_close(fd: int) -> None:
        tracked = fd in directory_fault_fds
        real_close(fd)
        if tracked:
            directory_fault_fds.remove(fd)
            directory_fault_events.append(("close", fd))

    with monkeypatch.context() as directory_fault_patch:
        directory_fault_patch.setattr(campaign.os, "open", trace_directory_fault_open)
        directory_fault_patch.setattr(campaign.os, "fsync", fail_directory_fsync)
        directory_fault_patch.setattr(
            campaign.os,
            "replace",
            trace_directory_fault_replace,
        )
        directory_fault_patch.setattr(
            campaign.os,
            "close",
            trace_directory_fault_close,
        )
        return_code, raised, calls = run_campaign(
            directory_fault_patch,
            directory_fault_output,
            generation_id="gen-directory-fsync-fault",
        )
    if [event[0] for event in directory_fault_events] != [
        "open",
        "fsync",
        "fsync",
        "fsync",
        "close",
    ]:
        journal_errors.append(
            "directory-fsync-fault: descriptor lifecycle differs: "
            f"{directory_fault_events!r}"
        )
    elif len({event[1] for event in directory_fault_events}) != 1:
        journal_errors.append(
            "directory-fsync-fault: open/fsync/close used different fds"
        )
    if directory_fault_fds:
        journal_errors.append("directory-fsync-fault: directory descriptor leaked")
    if raised is None and return_code == 0:
        journal_errors.append("directory-fsync-fault: failure did not stop campaign")
    if calls != 1:
        journal_errors.append(
            f"directory-fsync-fault: expected one billed call, observed {calls}"
        )
    if directory_fault_log.read_bytes() != atomic_original:
        journal_errors.append(
            "directory-fsync-fault: original journal bytes were not restored"
        )

    assert journal_errors == []


def test_usage_journal_restores_original_bytes_when_directory_fsync_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    campaign = _campaign()
    log_path = tmp_path / "_usage_log.json"
    original_bytes = b'[{"schema_version":1,"opaque":{"ordered":[3,2,1]}}]\n'
    log_path.write_bytes(original_bytes)
    real_open = campaign.os.open
    real_close = campaign.os.close
    real_fsync = campaign.os.fsync
    real_replace = campaign.os.replace
    directory_fds: set[int] = set()
    directory_fsync_calls = 0
    primary_replaced = False

    def traced_open(
        path: object,
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if dir_fd is None:
            fd = real_open(path, flags, mode)
        else:
            fd = real_open(path, flags, mode, dir_fd=dir_fd)
        if Path(path) == tmp_path:
            directory_fds.add(fd)
        return fd

    def fail_first_directory_fsync(fd: int) -> None:
        nonlocal directory_fsync_calls
        if fd in directory_fds:
            directory_fsync_calls += 1
            if primary_replaced and directory_fsync_calls == 2:
                raise OSError("simulated directory fsync failure")
        real_fsync(fd)

    def traced_replace(source: object, destination: object) -> None:
        nonlocal primary_replaced
        if Path(destination) == log_path:
            primary_replaced = True
        real_replace(source, destination)

    def traced_close(fd: int) -> None:
        real_close(fd)
        directory_fds.discard(fd)

    monkeypatch.setattr(campaign.os, "open", traced_open)
    monkeypatch.setattr(campaign.os, "fsync", fail_first_directory_fsync)
    monkeypatch.setattr(campaign.os, "replace", traced_replace)
    monkeypatch.setattr(campaign.os, "close", traced_close)

    with pytest.raises(OSError, match="directory fsync failure"):
        campaign.write_usage_log_atomic(
            log_path,
            [{"schema_version": 2, "generation_id": "gen-new"}],
        )

    assert directory_fsync_calls == 3
    assert directory_fds == set()
    assert log_path.read_bytes() == original_bytes


def test_usage_journal_durably_prepares_recovery_before_primary_replace(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    campaign = _campaign()
    log_path = tmp_path / "_usage_log.json"
    recovery_path = tmp_path / "._usage_log.json.recovery"
    original_bytes = b'[{"schema_version":1,"opaque":"recoverable"}]\n'
    log_path.write_bytes(original_bytes)
    real_open = campaign.os.open
    real_close = campaign.os.close
    real_fsync = campaign.os.fsync
    real_replace = campaign.os.replace
    directory_fds: set[int] = set()
    events: list[tuple[str, Path | None]] = []

    def fd_path(fd: int) -> Path | None:
        try:
            return Path(campaign.os.readlink(f"/proc/self/fd/{fd}"))
        except OSError:
            return None

    def traced_open(
        path: object,
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if dir_fd is None:
            fd = real_open(path, flags, mode)
        else:
            fd = real_open(path, flags, mode, dir_fd=dir_fd)
        if Path(path) == tmp_path:
            directory_fds.add(fd)
        return fd

    def traced_fsync(fd: int) -> None:
        if fd in directory_fds:
            events.append(("directory_fsync", tmp_path))
        else:
            events.append(("file_fsync", fd_path(fd)))
        real_fsync(fd)

    def traced_replace(source: object, destination: object) -> None:
        events.append(("replace", Path(destination)))
        real_replace(source, destination)

    def traced_close(fd: int) -> None:
        real_close(fd)
        directory_fds.discard(fd)

    monkeypatch.setattr(campaign.os, "open", traced_open)
    monkeypatch.setattr(campaign.os, "fsync", traced_fsync)
    monkeypatch.setattr(campaign.os, "replace", traced_replace)
    monkeypatch.setattr(campaign.os, "close", traced_close)

    campaign.write_usage_log_atomic(
        log_path,
        [{"schema_version": 2, "generation_id": "gen-new"}],
    )

    recovery_replace = events.index(("replace", recovery_path))
    primary_replace = events.index(("replace", log_path))
    directory_syncs = [
        index
        for index, event in enumerate(events)
        if event == ("directory_fsync", tmp_path)
    ]
    recovery_fsyncs = [
        index
        for index, event in enumerate(events)
        if event[0] == "file_fsync"
        and event[1] is not None
        and event[1].name.endswith(".recovery.tmp")
    ]
    assert len(recovery_fsyncs) == 1
    assert len(directory_syncs) >= 2
    assert recovery_fsyncs[0] < recovery_replace < directory_syncs[0] < primary_replace
    assert directory_fds == set()
    assert not recovery_path.exists()


def test_campaign_main_refuses_existing_usage_recovery_before_provider_call(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    campaign = _campaign()
    output_dir = tmp_path / "campaign"
    output_dir.mkdir()
    log_path = output_dir / "_usage_log.json"
    recovery_path = output_dir / "._usage_log.json.recovery"
    log_bytes = b'[{"schema_version":1,"opaque":"visible"}]\n'
    recovery_bytes = b'[{"schema_version":1,"opaque":"recoverable"}]\n'
    log_path.write_bytes(log_bytes)
    recovery_path.write_bytes(recovery_bytes)
    provider_calls = 0

    def hostile_provider(*args: object, **kwargs: object) -> object:
        nonlocal provider_calls
        provider_calls += 1
        return _completion(content=json.dumps(_campaign_result()))

    monkeypatch.setenv("OPENROUTER_API_KEY", API_KEY)
    monkeypatch.setenv("OPENROUTER_MODEL", MODEL)
    _install_campaign_main_doubles(
        monkeypatch,
        campaign,
        output_dir,
        hostile_provider,
    )

    result: int | None = None
    raised: Exception | None = None
    try:
        result = campaign.main()
    except Exception as error:  # recovery refusal may be exceptional before Green
        raised = error
    assert provider_calls == 0
    assert result == 1
    assert raised is None
    assert log_path.read_bytes() == log_bytes
    assert recovery_path.read_bytes() == recovery_bytes


@pytest.mark.parametrize(
    "fault",
    (
        pytest.param("rollback-file-fsync", id="rollback-file-fsync"),
        pytest.param("rollback-replace", id="rollback-replace"),
        pytest.param("second-directory-fsync", id="second-directory-fsync"),
    ),
)
def test_usage_journal_keeps_durable_recovery_when_rollback_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    fault: str,
) -> None:
    campaign = _campaign()
    log_path = tmp_path / "_usage_log.json"
    recovery_path = tmp_path / "._usage_log.json.recovery"
    original_bytes = b'[{"schema_version":1,"opaque":{"keep":[1,2,3]}}]\n'
    log_path.write_bytes(original_bytes)
    real_open = campaign.os.open
    real_close = campaign.os.close
    real_fsync = campaign.os.fsync
    real_replace = campaign.os.replace
    directory_fds: set[int] = set()
    primary_replaced = False
    commit_failure_seen = False
    rollback_replaced = False

    def fd_path(fd: int) -> Path | None:
        try:
            return Path(campaign.os.readlink(f"/proc/self/fd/{fd}"))
        except OSError:
            return None

    def traced_open(
        path: object,
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if dir_fd is None:
            fd = real_open(path, flags, mode)
        else:
            fd = real_open(path, flags, mode, dir_fd=dir_fd)
        if Path(path) == tmp_path:
            directory_fds.add(fd)
        return fd

    def faulted_fsync(fd: int) -> None:
        nonlocal commit_failure_seen
        target = fd_path(fd)
        if (
            fault == "rollback-file-fsync"
            and commit_failure_seen
            and target is not None
            and target.name.endswith(".rollback")
        ):
            raise OSError("simulated rollback file fsync failure")
        if fd in directory_fds and primary_replaced:
            if not commit_failure_seen:
                commit_failure_seen = True
                raise OSError("simulated primary directory fsync failure")
            if fault == "second-directory-fsync" and rollback_replaced:
                raise OSError("simulated second directory fsync failure")
        real_fsync(fd)

    def faulted_replace(source: object, destination: object) -> None:
        nonlocal primary_replaced, rollback_replaced
        source_path = Path(source)
        destination_path = Path(destination)
        if destination_path == log_path and source_path.name.endswith(".rollback"):
            if fault == "rollback-replace":
                raise OSError("simulated rollback replace failure")
            rollback_replaced = True
        elif destination_path == log_path:
            primary_replaced = True
        real_replace(source, destination)

    def traced_close(fd: int) -> None:
        real_close(fd)
        directory_fds.discard(fd)

    monkeypatch.setattr(campaign.os, "open", traced_open)
    monkeypatch.setattr(campaign.os, "fsync", faulted_fsync)
    monkeypatch.setattr(campaign.os, "replace", faulted_replace)
    monkeypatch.setattr(campaign.os, "close", traced_close)

    with pytest.raises(OSError):
        campaign.write_usage_log_atomic(
            log_path,
            [{"schema_version": 2, "generation_id": "gen-new"}],
        )

    assert commit_failure_seen is True
    assert recovery_path.read_bytes() == original_bytes
    assert directory_fds == set()
    if fault == "second-directory-fsync":
        assert log_path.read_bytes() == original_bytes

    visible_log_bytes = log_path.read_bytes()
    with pytest.raises(OSError, match="usage journal recovery required"):
        campaign.write_usage_log_atomic(
            log_path,
            [{"schema_version": 2, "generation_id": "gen-retry"}],
        )
    assert log_path.read_bytes() == visible_log_bytes
    assert recovery_path.read_bytes() == original_bytes


def test_usage_journal_with_no_history_removes_failed_first_write(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    campaign = _campaign()
    log_path = tmp_path / "_usage_log.json"
    recovery_path = tmp_path / "._usage_log.json.recovery"
    real_open = campaign.os.open
    real_close = campaign.os.close
    real_fsync = campaign.os.fsync
    real_replace = campaign.os.replace
    directory_fds: set[int] = set()
    primary_replaced = False
    failure_seen = False

    def traced_open(
        path: object,
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if dir_fd is None:
            fd = real_open(path, flags, mode)
        else:
            fd = real_open(path, flags, mode, dir_fd=dir_fd)
        if Path(path) == tmp_path:
            directory_fds.add(fd)
        return fd

    def fail_commit_fsync(fd: int) -> None:
        nonlocal failure_seen
        if fd in directory_fds and primary_replaced and not failure_seen:
            failure_seen = True
            raise OSError("simulated first write directory fsync failure")
        real_fsync(fd)

    def traced_replace(source: object, destination: object) -> None:
        nonlocal primary_replaced
        if Path(destination) == log_path:
            primary_replaced = True
        real_replace(source, destination)

    def traced_close(fd: int) -> None:
        real_close(fd)
        directory_fds.discard(fd)

    monkeypatch.setattr(campaign.os, "open", traced_open)
    monkeypatch.setattr(campaign.os, "fsync", fail_commit_fsync)
    monkeypatch.setattr(campaign.os, "replace", traced_replace)
    monkeypatch.setattr(campaign.os, "close", traced_close)

    with pytest.raises(OSError, match="first write directory fsync failure"):
        campaign.write_usage_log_atomic(
            log_path,
            [{"schema_version": 2, "generation_id": "gen-first"}],
        )

    assert failure_seen is True
    assert not log_path.exists()
    assert not recovery_path.exists()
    assert directory_fds == set()


def test_usage_locked_append_preserves_interleaved_writers_and_releases_lock(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    campaign = _campaign()
    append_locked = getattr(campaign, "append_usage_log_locked", None)
    assert callable(append_locked), "locked usage append helper is missing"
    main_tree = ast.parse(inspect.getsource(campaign.main))
    main_calls = {
        node.func.id
        for node in ast.walk(main_tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "append_usage_log_locked" in main_calls
    assert "write_usage_log_atomic" not in main_calls
    assert "merge_usage_log" not in main_calls

    output_dir = tmp_path / "interleaved"
    output_dir.mkdir()
    log_path = output_dir / "_usage_log.json"
    v1 = {
        "cap": "legacy-v1",
        "read": 7,
        "nested": {"preserve": [1, 2, 3]},
    }
    generation_a = {
        "schema_version": 2,
        "generation_id": "gen-interleaved-a",
        "cost_usd": 1,
    }
    generation_b = {
        "schema_version": 2,
        "generation_id": "gen-interleaved-b",
        "cost_usd": 2,
    }
    original_bytes = json.dumps([v1], ensure_ascii=False).encode() + b"\n"
    log_path.write_bytes(original_bytes)

    error_dir = tmp_path / "writer-error"
    error_dir.mkdir()
    error_log = error_dir / "_usage_log.json"
    error_log.write_bytes(original_bytes)

    real_load = campaign.load_usage_log
    real_merge = campaign.merge_usage_log
    real_write = campaign.write_usage_log_atomic
    real_flock = campaign.fcntl.flock
    real_close = campaign.os.close
    events: list[tuple[str, str, int | None, Path | None]] = []
    event_guard = threading.Lock()
    lock_fds: dict[int, Path] = {}
    loaded_snapshots: dict[str, list[dict[str, object]]] = {}
    thread_errors: list[BaseException] = []
    results: dict[str, list[dict[str, object]]] = {}
    writer_a_acquired = threading.Event()
    writer_b_attempted = threading.Event()

    def record(
        action: str,
        *,
        fd: int | None = None,
        path: Path | None = None,
    ) -> None:
        with event_guard:
            events.append((threading.current_thread().name, action, fd, path))

    def traced_flock(fd: int, operation: int) -> None:
        thread_name = threading.current_thread().name
        if operation & campaign.fcntl.LOCK_EX:
            target = Path(campaign.os.readlink(f"/proc/self/fd/{fd}"))
            lock_fds[fd] = target
            record("lock_attempt", fd=fd, path=target)
            if thread_name == "writer-b":
                writer_b_attempted.set()
            real_flock(fd, operation)
            record("lock_acquired", fd=fd, path=target)
            if thread_name == "writer-a":
                writer_a_acquired.set()
                if not writer_b_attempted.wait(2):
                    raise AssertionError("writer B never attempted the shared lock")
            return
        if operation & campaign.fcntl.LOCK_UN:
            target = lock_fds[fd]
            real_flock(fd, operation)
            record("lock_released", fd=fd, path=target)
            return
        real_flock(fd, operation)

    def traced_close(fd: int) -> None:
        lock_path = lock_fds.get(fd)
        real_close(fd)
        if lock_path is not None:
            record("lock_closed", fd=fd, path=lock_path)
            lock_fds.pop(fd)

    def traced_load(path: Path, *, model: str) -> list[dict[str, object]]:
        loaded = real_load(path, model=model)
        thread_name = threading.current_thread().name
        loaded_snapshots[thread_name] = copy.deepcopy(loaded)
        record("load", path=path)
        return loaded

    def traced_merge(
        existing: list[dict[str, object]],
        incoming: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        record("merge")
        return real_merge(existing, incoming)

    def traced_write(
        path: Path,
        entries: list[dict[str, object]],
    ) -> None:
        record("write_start", path=path)
        if path == error_log:
            raise OSError("simulated append write failure")
        real_write(path, entries)
        record("write_done", path=path)

    def writer(name: str, entry: dict[str, object]) -> None:
        try:
            results[name] = append_locked(log_path, [entry], model=MODEL)
        except BaseException as error:
            thread_errors.append(error)

    with monkeypatch.context() as locked_patch:
        locked_patch.setattr(campaign.fcntl, "flock", traced_flock)
        locked_patch.setattr(campaign.os, "close", traced_close)
        locked_patch.setattr(campaign, "load_usage_log", traced_load)
        locked_patch.setattr(campaign, "merge_usage_log", traced_merge)
        locked_patch.setattr(campaign, "write_usage_log_atomic", traced_write)

        writer_a = threading.Thread(
            target=writer,
            args=("writer-a", generation_a),
            name="writer-a",
        )
        writer_b = threading.Thread(
            target=writer,
            args=("writer-b", generation_b),
            name="writer-b",
        )
        writer_a.start()
        assert writer_a_acquired.wait(2), "writer A never acquired the lock"
        writer_b.start()
        writer_a.join(3)
        writer_b.join(3)
        assert not writer_a.is_alive() and not writer_b.is_alive()

        error_event_start = len(events)
        with pytest.raises(OSError, match="simulated append write failure"):
            append_locked(error_log, [generation_a], model=MODEL)

    assert thread_errors == []
    expected_rows = [v1, generation_a, generation_b]
    assert json.loads(log_path.read_text(encoding="utf-8")) == expected_rows
    assert results["writer-a"] == [v1, generation_a]
    assert results["writer-b"] == expected_rows
    assert loaded_snapshots["writer-b"] == [v1, generation_a]

    success_events = events[:error_event_start]
    success_lock_paths = {
        event[3]
        for event in success_events
        if event[1] == "lock_attempt"
    }
    assert len(success_lock_paths) == 1
    shared_lock_path = success_lock_paths.pop()
    assert shared_lock_path is not None
    assert shared_lock_path.parent == log_path.parent
    assert shared_lock_path != log_path
    for thread_name in ("writer-a", "writer-b"):
        thread_events = [
            event for event in success_events if event[0] == thread_name
        ]
        assert [event[1] for event in thread_events] == [
            "lock_attempt",
            "lock_acquired",
            "load",
            "merge",
            "write_start",
            "write_done",
            "lock_released",
            "lock_closed",
        ]
        lock_lifecycle_fds = {
            event[2]
            for event in thread_events
            if event[1] in {
                "lock_attempt",
                "lock_acquired",
                "lock_released",
                "lock_closed",
            }
        }
        assert len(lock_lifecycle_fds) == 1
        assert None not in lock_lifecycle_fds
    assert success_events.index(
        next(
            event
            for event in success_events
            if event[:2] == ("writer-b", "lock_attempt")
        )
    ) < success_events.index(
        next(
            event
            for event in success_events
            if event[:2] == ("writer-a", "load")
        )
    )

    error_events = events[error_event_start:]
    assert [event[1] for event in error_events] == [
        "lock_attempt",
        "lock_acquired",
        "load",
        "merge",
        "write_start",
        "lock_released",
        "lock_closed",
    ]
    error_lock_fds = {
        event[2]
        for event in error_events
        if event[1].startswith("lock_")
    }
    assert len(error_lock_fds) == 1
    assert None not in error_lock_fds
    assert lock_fds == {}
    assert error_log.read_bytes() == original_bytes


def test_usage_upsert_preserves_other_v2_generations_for_same_capacity() -> None:
    campaign = _campaign()
    first = {"schema_version": 2, "cap": CAPACITY_ID, "generation_id": "gen-a"}
    second = {"schema_version": 2, "cap": CAPACITY_ID, "generation_id": "gen-b"}

    merged = campaign.merge_usage_log([first], [second])

    assert merged == [first, second]


def test_usage_logging_contains_no_local_cost_formula() -> None:
    campaign = _campaign()
    source = (CORPUS_ROOT / "scripts" / "judge_campaign.py").read_text(
        encoding="utf-8"
    )
    assert _campaign_accounting_policy_errors(source) == []
    adversarial_mutations = {
        "renamed coefficient": """
def price(tokens):
    return tokens * 2.0 / 999_999
""",
        "parameter coefficient": """
def price(tokens, coefficient):
    return tokens * coefficient
""",
        "persisted history sum": """
def summarize(history):
    return sum(row.get("cost_usd", 0) for row in history)
""",
        "output-like cost name": """
def divide(output_cost, divisor):
    return output_cost / divisor
""",
        "path-like history name": """
def divide_history(history_path, divisor):
    return history_path / divisor
""",
        "module-level price formula": """
token_count = 100
rate = 2.0
cost_usd = token_count * rate
""",
        "module-level history sum": """
history = []
cost_usd = sum(row.get("cost_usd", 0) for row in history)
""",
        "class-level price formula": """
class Pricing:
    token_count = 100
    rate = 2.0
    cost_usd = token_count * rate
""",
        "nested price formula": """
def container():
    def nested_price(tokens):
        return tokens * 2.0 / 999_999
    return nested_price
""",
    }
    for label, mutation in adversarial_mutations.items():
        policy_errors = _campaign_accounting_policy_errors(source + mutation)
        assert policy_errors, f"accounting mutation accepted: {label}"
        assert any(
            "accounting" in error or "current_run_totals" in error
            for error in policy_errors
        ), (label, policy_errors)

    allowed_non_accounting_operators = source + """
from pathlib import Path
def allowed_examples():
    usage_path = Path("output") / "_usage_log.json"
    prompt_budget = len(SYSTEM_TEXT) // 4
    return usage_path, prompt_budget
def outer():
    def line_number(index):
        return index + 1
    return line_number
"""
    assert _campaign_accounting_policy_errors(allowed_non_accounting_operators) == []
    nested_errors = _campaign_accounting_policy_errors(
        source + adversarial_mutations["nested price formula"]
    )
    assert sum(
        error.startswith("accounting arithmetic in nested_price")
        for error in nested_errors
    ) == 1
    low_tokens = _completion(prompt_tokens=10, completion_tokens=2, cost=0.7654321)
    high_tokens = _completion(prompt_tokens=1000, completion_tokens=200, cost=0.7654321)

    low = campaign.build_usage_v2(
        cap=CAPACITY_ID, seq="P01", attempt=1, judged_at=JUDGED_AT, completion=low_tokens
    )
    high = campaign.build_usage_v2(
        cap=CAPACITY_ID, seq="P01", attempt=1, judged_at=JUDGED_AT, completion=high_tokens
    )

    assert low["cost_usd"] == high["cost_usd"] == 0.7654321


def test_failed_usage_entry_invents_no_accounting() -> None:
    campaign = _campaign()

    entry = campaign.build_failed_usage_v2(
        cap=CAPACITY_ID,
        seq="P01",
        attempt=3,
        judged_at=JUDGED_AT,
        model=MODEL,
        error_category="unavailable",
    )

    assert set(entry) == {
        "schema_version",
        "provider",
        "cap",
        "seq",
        "attempt",
        "judged_at",
        "model",
        "error_category",
    }
    assert entry == {
        "schema_version": 2,
        "provider": "openrouter",
        "cap": CAPACITY_ID,
        "seq": "P01",
        "attempt": 3,
        "judged_at": JUDGED_AT,
        "model": MODEL,
        "error_category": "unavailable",
    }


def test_run_totals_sum_only_current_successful_v2_entries() -> None:
    campaign = _campaign()
    history = [
        {"cap": "old-v1", "read": 9_999, "write": 9_999, "cost_usd": 999.0},
        {
            "schema_version": 2,
            "generation_id": "old-v2",
            "prompt_tokens": 8_000,
            "completion_tokens": 2_000,
            "total_tokens": 10_000,
            "cached_tokens": 4_000,
            "cache_write_tokens": 3_000,
            "cost_usd": 88.0,
        },
        {"schema_version": 2, "error_category": "timeout"},
    ]
    current_entries = [
        {
            "schema_version": 2,
            "generation_id": "current-a",
            "prompt_tokens": 10,
            "completion_tokens": 4,
            "total_tokens": 14,
            "cached_tokens": 3,
            "cache_write_tokens": 2,
            "cost_usd": 0.125,
        },
        {
            "schema_version": 2,
            "generation_id": "current-b",
            "prompt_tokens": 20,
            "completion_tokens": 6,
            "total_tokens": 26,
            "cached_tokens": 5,
            "cache_write_tokens": 1,
            "cost_usd": 0.375,
        },
    ]
    merged_history = campaign.merge_usage_log(history, current_entries)

    totals = campaign.current_run_totals(current_entries)

    assert totals == {
        "prompt_tokens": 30,
        "completion_tokens": 10,
        "total_tokens": 40,
        "cached_tokens": 8,
        "cache_write_tokens": 3,
        "cost_usd": 0.5,
    }
    assert merged_history != current_entries
    history[0]["cost_usd"] = 123_456.0
    assert campaign.current_run_totals(current_entries) == totals
    assert all("run_id" not in row for row in merged_history)

    huge_cost = 10**1000
    huge_entries = [
        {**current_entries[0], "cost_usd": huge_cost},
        {**current_entries[1], "cost_usd": 17},
    ]
    huge_totals = campaign.current_run_totals(huge_entries)
    assert huge_totals["cost_usd"] == huge_cost + 17


def test_substance_llm_delegates_to_shared_openrouter_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    substance = _substance()
    seen: list[dict[str, object]] = []
    expected = {"taught": True, "citation": "phrase", "justification": "preuve"}

    def fake_chat_completion(**kwargs: object) -> object:
        seen.append(kwargs)
        return SimpleNamespace(content=json.dumps(expected))

    monkeypatch.setattr(substance, "chat_completion", fake_chat_completion)
    transport = object()
    result = substance.call_llm(
        {"OPENROUTER_API_KEY": API_KEY, "OPENROUTER_MODEL": MODEL},
        CAPACITY_TEXT,
        "phrase",
        ROLE_LABEL,
        transport=transport,
    )

    assert result == expected
    assert len(seen) == 1
    assert seen[0]["api_key"] == API_KEY
    assert seen[0]["model"] == MODEL
    assert seen[0]["transport"] is transport


@pytest.mark.parametrize(
    ("case", "file_name"),
    (
        pytest.param("parent", "../secret.md", id="parent-traversal"),
        pytest.param("absolute", None, id="absolute-path"),
        pytest.param("symlink", "escape.md", id="symlink-escape"),
    ),
)
def test_substance_section_body_rejects_paths_outside_repository(
    tmp_path: Path,
    case: str,
    file_name: str | None,
) -> None:
    substance = _substance()
    repo_root = tmp_path / "repository"
    repo_root.mkdir()
    outside = tmp_path / "secret.md"
    outside.write_text("# Secret\n\nNEVER SEND THIS CONTENT\n", encoding="utf-8")
    if case == "absolute":
        file_name = str(outside.resolve())
    elif case == "symlink":
        (repo_root / "escape.md").symlink_to(outside)
    assert file_name is not None

    assert substance.section_body(repo_root, file_name, "#secret") is None


def test_substance_section_body_reads_valid_internal_relative_path(
    tmp_path: Path,
) -> None:
    substance = _substance()
    repo_root = tmp_path / "repository"
    source = repo_root / "cours" / "lesson.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Leçon\n\nCONTENU INTERNE VALIDE\n", encoding="utf-8")

    body = substance.section_body(repo_root, "cours/lesson.md", "#leçon")

    assert body is not None
    assert "CONTENU INTERNE VALIDE" in body


def _external_path_hit(
    tmp_path: Path,
    case: str,
) -> tuple[Path, dict[str, object], tuple[str, str]]:
    repo_root = tmp_path / "repository"
    repo_root.mkdir()
    local_secret = "LOCAL_FILE_SECRET_SENTINEL"
    rag_secret = "RAG_DOCUMENT_SECRET_SENTINEL"
    outside = tmp_path / "secret.md"
    outside.write_text(f"# Secret\n\n{local_secret}\n", encoding="utf-8")
    if case == "parent":
        file_name = "../secret.md"
    elif case == "absolute":
        file_name = str(outside.resolve())
    elif case == "symlink":
        file_name = "escape.md"
        (repo_root / file_name).symlink_to(outside)
    else:
        file_name = "secret\x00.md"
    hit: dict[str, object] = {
        "metadata": {
            "source_type": "nsi_corpus",
            "document_type": "cours",
            "path": file_name,
            "section_anchor": "#secret",
        },
        "document": rag_secret,
    }
    return repo_root, hit, (local_secret, rag_secret)


@pytest.mark.parametrize(
    "case",
    (
        pytest.param("parent", id="parent-traversal"),
        pytest.param("absolute", id="absolute-path"),
        pytest.param("symlink", id="symlink-escape"),
        pytest.param("nul", id="nul-byte"),
    ),
)
def test_substance_document_text_rejects_hit_with_unconfined_path(
    tmp_path: Path,
    case: str,
) -> None:
    substance = _substance()
    repo_root, hit, secrets = _external_path_hit(tmp_path, case)

    rendered = substance.document_text_for_hit(repo_root, hit)

    assert rendered == ""
    assert all(secret not in rendered for secret in secrets)


@pytest.mark.parametrize(
    "case",
    (
        pytest.param("parent", id="parent-traversal"),
        pytest.param("absolute", id="absolute-path"),
        pytest.param("symlink", id="symlink-escape"),
        pytest.param("nul", id="nul-byte"),
    ),
)
def test_substance_judge_role_skips_unconfined_hit_before_llm(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    capsys: pytest.CaptureFixture[str],
    case: str,
) -> None:
    substance = _substance()
    repo_root, hit, secrets = _external_path_hit(tmp_path, case)
    llm_calls: list[tuple[object, ...]] = []

    monkeypatch.setattr(substance, "search_rag", lambda *args, **kwargs: [hit])

    def capture_llm(*args: object, **kwargs: object) -> dict[str, object]:
        llm_calls.append((*args, kwargs))
        return {"taught": False, "citation": "", "justification": "rejected"}

    monkeypatch.setattr(substance, "call_llm", capture_llm)
    capacity = {
        "id": CAPACITY_ID,
        "intitule": CAPACITY_TEXT,
        "rubrique": "Données",
        "contenu": "Tables",
        "niveau": "premiere",
    }
    with caplog.at_level("DEBUG"):
        evidence = substance.judge_role(
            {},
            capacity,
            substance.ROLE_SPECS["proof_course"],
            repo_root,
            set(),
        )

    captured = capsys.readouterr()
    observable = "\n".join(
        (json.dumps(llm_calls, default=str), caplog.text, captured.out, captured.err)
    )
    assert evidence["present"] is False
    assert llm_calls == []
    assert all(secret not in observable for secret in secrets)


def test_substance_document_text_preserves_document_only_hit_fallback(
    tmp_path: Path,
) -> None:
    substance = _substance()
    hit = {
        "metadata": {"source_type": "nsi_corpus", "document_type": "cours"},
        "document": "DOCUMENT SANS CHEMIN CONSERVE",
    }

    assert substance.document_text_for_hit(tmp_path, hit) == (
        "DOCUMENT SANS CHEMIN CONSERVE"
    )


def test_substance_main_overlays_only_nonempty_openrouter_environment(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    substance = _substance()
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    rag_env = config_dir / ".env.rag"
    rag_env.write_text(
        "\n".join(
            (
                "RAG_COLLECTION=nsi_corpus",
                "RAG_API_KEY=file-rag-key",
                "OPENROUTER_API_KEY=file-openrouter-key",
                "OPENROUTER_MODEL=file/openrouter-model",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    generic_env = config_dir / ".env"
    generic_env.write_text(
        "OPENROUTER_API_KEY=generic-key-must-never-be-read\n",
        encoding="utf-8",
    )
    capacity = {
        "id": CAPACITY_ID,
        "intitule": CAPACITY_TEXT,
        "rubrique": "Données",
        "contenu": "Tables",
        "niveau": "premiere",
    }
    cases = (
        (
            "missing-environment-falls-back",
            None,
            None,
            "file-openrouter-key",
            "file/openrouter-model",
        ),
        (
            "environment-wins",
            "environment-openrouter-key",
            "environment/openrouter-model",
            "environment-openrouter-key",
            "environment/openrouter-model",
        ),
        (
            "empty-environment-falls-back",
            "   ",
            "",
            "file-openrouter-key",
            "file/openrouter-model",
        ),
        (
            "mixed-key-environment",
            "environment-openrouter-key",
            "  ",
            "environment-openrouter-key",
            "file/openrouter-model",
        ),
        (
            "mixed-model-environment",
            "",
            "environment/openrouter-model",
            "file-openrouter-key",
            "environment/openrouter-model",
        ),
    )
    failures: list[str] = []
    real_read_text = Path.read_text

    for label, env_key, env_model, expected_key, expected_model in cases:
        output = tmp_path / f"{label}.json"
        reads: list[Path] = []
        observed: dict[str, object] = {}

        def guarded_read_text(
            path: Path,
            *args: object,
            **kwargs: object,
        ) -> str:
            reads.append(path)
            if path == generic_env:
                raise AssertionError("generic .env must never be read")
            return real_read_text(path, *args, **kwargs)

        def capture_review(
            env: dict[str, str],
            capacities: list[dict[str, str]],
            **kwargs: object,
        ) -> dict[str, object]:
            observed["env"] = dict(env)
            observed["judge_model"] = kwargs["judge_model"]
            return {
                "schema_version": "1.0.0",
                "unit": kwargs["unit"],
                "level": kwargs["level"],
                "judged_at": JUDGED_AT,
                "judge_model": kwargs["judge_model"],
                "author_model": "test",
                "capacities": [],
            }

        with monkeypatch.context() as scenario_patch:
            scenario_patch.setattr(substance, "ENV_FILE", rag_env)
            scenario_patch.setattr(substance, "load_programme", lambda: [capacity])
            scenario_patch.setattr(
                substance,
                "load_contract_capacity_ids",
                lambda root, unit: [],
            )
            scenario_patch.setattr(substance, "build_review", capture_review)
            scenario_patch.setattr(Path, "read_text", guarded_read_text)
            if env_key is None:
                scenario_patch.delenv("OPENROUTER_API_KEY", raising=False)
            else:
                scenario_patch.setenv("OPENROUTER_API_KEY", env_key)
            if env_model is None:
                scenario_patch.delenv("OPENROUTER_MODEL", raising=False)
            else:
                scenario_patch.setenv("OPENROUTER_MODEL", env_model)
            scenario_patch.setenv("RAG_COLLECTION", "external-environment-collection")
            scenario_patch.setenv("RAG_API_KEY", "environment-rag-key")
            scenario_patch.setattr(
                sys,
                "argv",
                [
                    "substance_judge.py",
                    "--unit",
                    "P01",
                    "--output",
                    str(output),
                ],
            )
            result = substance.main()

        captured_env = observed.get("env", {})
        if result != 0:
            failures.append(f"{label}: main returned {result}")
        if not isinstance(captured_env, dict):
            failures.append(f"{label}: build_review received no environment")
            continue
        if captured_env.get("OPENROUTER_API_KEY") != expected_key:
            failures.append(
                f"{label}: key={captured_env.get('OPENROUTER_API_KEY')!r}"
            )
        if captured_env.get("OPENROUTER_MODEL") != expected_model:
            failures.append(
                f"{label}: model={captured_env.get('OPENROUTER_MODEL')!r}"
            )
        if observed.get("judge_model") != expected_model:
            failures.append(f"{label}: recorded judge model is not effective model")
        if captured_env.get("RAG_COLLECTION") != "nsi_corpus":
            failures.append(f"{label}: process environment replaced RAG_COLLECTION")
        if captured_env.get("RAG_API_KEY") != "file-rag-key":
            failures.append(f"{label}: process environment replaced RAG_API_KEY")
        if reads != [rag_env]:
            failures.append(f"{label}: unexpected env reads {reads!r}")

    assert failures == []


def test_substance_without_key_returns_conservative_result_without_transport(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    substance = _substance()
    calls = 0

    def forbidden(*args: object, **kwargs: object) -> object:
        nonlocal calls
        calls += 1
        raise AssertionError("transport must not run without a key")

    monkeypatch.setattr(substance, "_http_json", forbidden)
    if hasattr(substance, "chat_completion"):
        monkeypatch.setattr(substance, "chat_completion", forbidden)

    result = substance.call_llm({}, CAPACITY_TEXT, SECTION_TEXT, ROLE_LABEL)

    assert result["taught"] is False
    assert result["citation"] == ""
    assert calls == 0


def test_substance_rejects_key_without_model_before_transport(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    substance = _substance()
    client = _client()
    calls = 0

    def forbidden(*args: object, **kwargs: object) -> object:
        nonlocal calls
        calls += 1
        raise AssertionError("transport called before configuration validation")

    monkeypatch.setattr(substance, "_http_json", forbidden)
    if hasattr(substance, "chat_completion"):
        monkeypatch.setattr(substance, "chat_completion", forbidden)
    with pytest.raises(client.OpenRouterError) as caught:
        substance.call_llm(
            {"OPENROUTER_API_KEY": API_KEY, "OPENROUTER_MODEL": " "},
            CAPACITY_TEXT,
            SECTION_TEXT,
            ROLE_LABEL,
        )
    assert caught.value.category == "configuration"
    assert calls == 0


def test_substance_sends_exact_bounded_prompt_and_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    substance = _substance()
    seen: list[dict[str, object]] = []

    def fake_chat_completion(**kwargs: object) -> object:
        seen.append(kwargs)
        return SimpleNamespace(
            content='{"taught": false, "citation": "", "justification": "aucune preuve"}'
        )

    monkeypatch.setattr(substance, "chat_completion", fake_chat_completion)
    substance.call_llm(
        {"OPENROUTER_API_KEY": API_KEY, "OPENROUTER_MODEL": MODEL},
        CAPACITY_TEXT,
        SECTION_TEXT,
        ROLE_LABEL,
        transport=object(),
    )

    user_prompt = (
        f'Capacité NSI : "{CAPACITY_TEXT}"\n'
        f"Rôle : {ROLE_LABEL}\n\n"
        f"Extrait :\n---\n{SECTION_TEXT[:800]}\n---\n\n"
        f"Cette section {ROLE_LABEL}-t-elle cette capacité ?"
    )
    assert len(seen) == 1
    assert seen[0]["model"] == MODEL
    assert seen[0]["max_completion_tokens"] == 800
    assert seen[0]["messages"] == [
        {"role": "system", "content": substance.JUDGE_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def test_substance_accepts_only_exact_closed_json_object(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    substance = _substance()
    valid = {"taught": True, "citation": "phrase exacte", "justification": "preuve exacte"}
    accepted = (json.dumps(valid), f"```json\n{json.dumps(valid)}\n```")
    rejected: tuple[object, ...] = (
        '{"taught": true, "citation": "phrase exacte"}',
        '{"taught": true, "citation": "phrase", "justification": "preuve", "extra": 1}',
        '{"taught": 1, "citation": "phrase", "justification": "preuve"}',
        f"text before\n{json.dumps(valid)}",
        f"```JSON\n{json.dumps(valid)}\n```",
        f"```json\n{json.dumps(valid)}\n```\ntext after",
    )

    def evaluate(content: object) -> dict[str, object]:
        monkeypatch.setattr(
            substance,
            "chat_completion",
            lambda **kwargs: SimpleNamespace(content=content),
        )
        return substance.call_llm(
            {"OPENROUTER_API_KEY": API_KEY, "OPENROUTER_MODEL": MODEL},
            CAPACITY_TEXT,
            SECTION_TEXT,
            ROLE_LABEL,
            transport=object(),
        )

    for content in accepted:
        assert evaluate(content) == valid
    for content in rejected:
        result = evaluate(content)
        assert result["taught"] is False
        assert result["citation"] == ""


def test_substance_rag_keeps_dedicated_http_transport(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    substance = _substance()
    seen: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def fake_http(*args: object, **kwargs: object) -> dict[str, object]:
        seen.append((args, kwargs))
        return {"hits": []}

    monkeypatch.setattr(substance, "_http_json", fake_http)
    if hasattr(substance, "chat_completion"):
        monkeypatch.setattr(
            substance,
            "chat_completion",
            lambda **kwargs: pytest.fail("OpenRouter client used for RAG retrieval"),
        )
    env = {
        "RAG_API_BASE_URL": "https://rag.example.invalid/search",
        "RAG_API_KEY": "rag-bearer-sentinel",
        "RAG_COLLECTION": "nsi_corpus",
    }

    assert substance.search_rag(env, "query", k=3) == []
    assert seen == [
        (
            (env["RAG_API_BASE_URL"],),
            {
                "body": {
                    "q": "query",
                    "collection": "nsi_corpus",
                    "k": 3,
                    "include_documents": True,
                },
                "headers": {"Authorization": "Bearer rag-bearer-sentinel"},
            },
        )
    ]


def test_substance_has_no_configurable_llm_endpoint() -> None:
    source = (CORPUS_ROOT / "scripts" / "substance_judge.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    names = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    rendered = "\n".join(names)
    for forbidden in (
        "LOCAL_LLM_ENGINE",
        "LOCAL_LLM_BASE_URL",
        "LOCAL_LLM_MODEL",
        "LOCAL_LLM_API_KEY",
        "qwen",
    ):
        assert forbidden not in rendered
    assert "/chat/completions" not in rendered


def test_substance_remote_error_is_sanitized_and_never_promotes(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    substance = _substance()
    client = _client()
    prompt_secret = "prompt-secret-sentinel"
    body_secret = "remote-body-secret-sentinel"

    class SanitizedRemoteError(client.OpenRouterError):
        category = "unavailable"

        def __init__(self) -> None:
            Exception.__init__(
                self,
                f"{API_KEY} {prompt_secret} {body_secret}",
            )

    def fail_shared(**kwargs: object) -> object:
        raise SanitizedRemoteError

    def fail_legacy(*args: object, **kwargs: object) -> object:
        raise RuntimeError(f"legacy leaked {prompt_secret} {body_secret}")

    if hasattr(substance, "chat_completion"):
        monkeypatch.setattr(substance, "chat_completion", fail_shared)
    monkeypatch.setattr(substance, "_http_json", fail_legacy)
    with caplog.at_level("DEBUG"):
        result = substance.call_llm(
            {
                "OPENROUTER_API_KEY": API_KEY,
                "OPENROUTER_MODEL": MODEL,
                "LOCAL_LLM_BASE_URL": "https://legacy.invalid",
                "LOCAL_LLM_MODEL": "legacy-model",
            },
            prompt_secret,
            body_secret,
            ROLE_LABEL,
            transport=object(),
        )

    rendered = json.dumps(result, ensure_ascii=False)
    captured = capsys.readouterr()
    observable = "\n".join(
        (rendered, captured.out, captured.err, caplog.text)
    )
    assert result["taught"] is False
    assert result["citation"] == ""
    assert "validated" not in rendered
    for secret in (API_KEY, prompt_secret, body_secret):
        assert secret not in observable


def test_run_substance_judge_imports_no_external_client() -> None:
    source = (CORPUS_ROOT / "scripts" / "run_substance_judge.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")
    assert not any(
        name == "nexus_external" or name.startswith("nexus_external.")
        for name in imports
    )
    assert not any(name in {"httpx", "requests", "urllib", "urllib.request"} for name in imports)


def test_run_substance_judge_uses_honest_deterministic_model() -> None:
    source = (CORPUS_ROOT / "scripts" / "run_substance_judge.py").read_text(encoding="utf-8")
    lowered = source.lower()
    assert "anthropic" not in lowered
    assert "claude" not in lowered
    tree = ast.parse(source)
    defaults = [
        keyword.value.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "add_argument"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and node.args[0].value == "--model"
        for keyword in node.keywords
        if keyword.arg == "default" and isinstance(keyword.value, ast.Constant)
    ]
    assert defaults == ["deterministic-prejudge"]


def test_campaign_discovers_current_checkout_from_unrelated_cwd(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    campaign = importlib.reload(_campaign())
    expected = (CHECKOUT_ROOT / "nexus_external").resolve()
    assert Path(campaign.nexus_external.__file__).resolve().parent == expected
    assert Path(inspect.getfile(campaign.call_openrouter_judge)).resolve().is_relative_to(CORPUS_ROOT)


def test_substance_discovers_current_checkout_from_unrelated_cwd(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    substance = importlib.reload(_substance())
    expected = (CHECKOUT_ROOT / "nexus_external").resolve()
    assert Path(substance.nexus_external.__file__).resolve().parent == expected
    assert Path(inspect.getfile(substance.call_llm)).resolve().is_relative_to(CORPUS_ROOT)


def test_corpus_callers_reload_canonical_external_package_over_shadow(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    shadow = tmp_path / "nexus_external"
    shadow.mkdir()
    (shadow / "__init__.py").write_text("SHADOW = True\n", encoding="utf-8")
    (shadow / "openrouter_client.py").write_text(
        "def chat_completion(**kwargs):\n    raise AssertionError('shadow transport called')\n",
        encoding="utf-8",
    )
    saved = {
        name: module
        for name, module in sys.modules.items()
        if name == "nexus_external" or name.startswith("nexus_external.")
    }
    for name in list(saved):
        sys.modules.pop(name, None)
    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.import_module("nexus_external.openrouter_client")
    try:
        for module_name in ("scripts.judge_campaign", "scripts.substance_judge"):
            sys.modules.pop(module_name, None)
            loaded = importlib.import_module(module_name)
            assert Path(loaded.nexus_external.__file__).resolve().parent == (
                CHECKOUT_ROOT / "nexus_external"
            ).resolve()
            assert loaded.chat_completion.__module__ == (
                "nexus_external.openrouter_client"
            )
    finally:
        for name in list(sys.modules):
            if name == "nexus_external" or name.startswith("nexus_external."):
                sys.modules.pop(name, None)
        sys.modules.update(saved)


@pytest.mark.parametrize(
    "caller_module",
    (
        pytest.param("judge_campaign", id="campaign"),
        pytest.param("substance_judge", id="substance"),
    ),
)
@pytest.mark.parametrize(
    "symlink_kind",
    (
        pytest.param("package", id="package-symlink"),
        pytest.param("module", id="module-symlink"),
    ),
)
def test_corpus_callers_reject_checkout_symlinks_before_external_code(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caller_module: str,
    symlink_kind: str,
) -> None:
    fake_checkout = tmp_path / "checkout"
    fake_corpus = fake_checkout / "NSI" / "corpus_nsi"
    fake_scripts = fake_corpus / "scripts"
    fake_scripts.mkdir(parents=True)
    (fake_checkout / ".git").mkdir()
    caller_path = fake_scripts / f"{caller_module}.py"
    caller_path.write_text(
        (CORPUS_ROOT / "scripts" / f"{caller_module}.py").read_text(
            encoding="utf-8"
        ),
        encoding="utf-8",
    )

    hostile_calls: list[str] = []
    monkeypatch.setattr(
        builtins,
        "_nexus_external_hostile_calls",
        hostile_calls,
        raising=False,
    )
    hostile_prelude = (
        "import builtins\n"
        f"builtins._nexus_external_hostile_calls.append({symlink_kind!r})\n"
    )
    client_body = (
        hostile_prelude
        + "class OpenRouterCompletion:\n    pass\n"
        + "class OpenRouterError(Exception):\n    pass\n"
        + "def chat_completion(**kwargs):\n    return None\n"
    )
    outside_package = tmp_path / "outside" / "nexus_external"
    outside_package.mkdir(parents=True)
    if symlink_kind == "package":
        (outside_package / "__init__.py").write_text(
            hostile_prelude,
            encoding="utf-8",
        )
        (outside_package / "openrouter_client.py").write_text(
            client_body,
            encoding="utf-8",
        )
        (fake_checkout / "nexus_external").symlink_to(
            outside_package,
            target_is_directory=True,
        )
    else:
        package_path = fake_checkout / "nexus_external"
        package_path.mkdir()
        (package_path / "__init__.py").write_text("", encoding="utf-8")
        outside_client = tmp_path / "outside" / "openrouter_client.py"
        outside_client.write_text(client_body, encoding="utf-8")
        (package_path / "openrouter_client.py").symlink_to(outside_client)

    saved_external = {
        name: module
        for name, module in sys.modules.items()
        if name == "nexus_external" or name.startswith("nexus_external.")
    }
    unique_module = f"_nexus_symlink_probe_{caller_module}_{symlink_kind}"
    for name in tuple(saved_external):
        sys.modules.pop(name, None)
    sys.modules.pop(unique_module, None)
    try:
        specification = importlib.util.spec_from_file_location(
            unique_module,
            caller_path,
        )
        assert specification is not None and specification.loader is not None
        loaded = importlib.util.module_from_spec(specification)
        sys.modules[unique_module] = loaded
        rejection: Exception | None = None
        try:
            specification.loader.exec_module(loaded)
        except (ImportError, RuntimeError) as error:
            rejection = error
        assert hostile_calls == []
        assert rejection is not None
    finally:
        sys.modules.pop(unique_module, None)
        for name in tuple(sys.modules):
            if name == "nexus_external" or name.startswith("nexus_external."):
                sys.modules.pop(name, None)
        sys.modules.update(saved_external)


@pytest.mark.parametrize(
    "caller_module",
    (
        pytest.param("scripts.judge_campaign", id="campaign"),
        pytest.param("scripts.substance_judge", id="substance"),
    ),
)
def test_corpus_callers_reload_canonical_preloaded_openrouter_submodule(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caller_module: str,
) -> None:
    monkeypatch.syspath_prepend(str(CHECKOUT_ROOT))
    monkeypatch.syspath_prepend(str(CORPUS_ROOT))
    external_package = importlib.import_module("nexus_external")
    assert Path(external_package.__file__).resolve().parent == (
        CHECKOUT_ROOT / "nexus_external"
    ).resolve()
    authentic_submodule = importlib.import_module("nexus_external.openrouter_client")
    assert Path(authentic_submodule.__file__).resolve() == (
        CHECKOUT_ROOT / "nexus_external" / "openrouter_client.py"
    ).resolve()
    foreign_path = tmp_path / "nexus_external" / "openrouter_client.py"
    foreign_path.parent.mkdir()
    foreign_path.write_text("# foreign preloaded module\n", encoding="utf-8")
    foreign = ModuleType("nexus_external.openrouter_client")
    foreign.__file__ = str(foreign_path)
    foreign.OpenRouterCompletion = type("OpenRouterCompletion", (), {})
    foreign.OpenRouterError = type("OpenRouterError", (Exception,), {})
    foreign.chat_completion = lambda **kwargs: None
    saved_submodule = authentic_submodule
    saved_attribute = external_package.openrouter_client
    saved_caller = sys.modules.pop(caller_module, None)
    sys.modules["nexus_external.openrouter_client"] = foreign
    try:
        loaded = importlib.import_module(caller_module)
        assert Path(loaded._openrouter_client.__file__).resolve() == (
            CHECKOUT_ROOT / "nexus_external" / "openrouter_client.py"
        ).resolve()
        assert loaded.chat_completion is not foreign.chat_completion
    finally:
        sys.modules.pop(caller_module, None)
        sys.modules.pop("nexus_external.openrouter_client", None)
        if saved_submodule is not None:
            sys.modules["nexus_external.openrouter_client"] = saved_submodule
        if saved_attribute is None:
            delattr(external_package, "openrouter_client")
        else:
            external_package.openrouter_client = saved_attribute
        if saved_caller is not None:
            sys.modules[caller_module] = saved_caller


@pytest.mark.parametrize(
    "caller_module",
    (
        pytest.param("scripts.judge_campaign", id="campaign"),
        pytest.param("scripts.substance_judge", id="substance"),
    ),
)
@pytest.mark.parametrize(
    "provenance",
    (
        pytest.param("forged", id="forged-canonical-file"),
        pytest.param("symlink", id="symlink-to-canonical-file"),
        pytest.param("missing", id="missing-file"),
        pytest.param("invalid", id="invalid-file"),
    ),
)
def test_corpus_callers_never_bind_unattestable_preloaded_client(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caller_module: str,
    provenance: str,
) -> None:
    monkeypatch.syspath_prepend(str(CHECKOUT_ROOT))
    monkeypatch.syspath_prepend(str(CORPUS_ROOT))
    external_package = importlib.import_module("nexus_external")
    authentic_submodule = importlib.import_module("nexus_external.openrouter_client")
    canonical_file = (
        CHECKOUT_ROOT / "nexus_external" / "openrouter_client.py"
    ).resolve()
    hostile_calls = 0

    def hostile_chat_completion(**kwargs: object) -> None:
        nonlocal hostile_calls
        hostile_calls += 1
        raise AssertionError(f"hostile transport called: {kwargs}")

    hostile = ModuleType("nexus_external.openrouter_client")
    if provenance == "forged":
        hostile.__file__ = str(canonical_file)
    elif provenance == "symlink":
        linked_file = tmp_path / "openrouter_client.py"
        linked_file.symlink_to(canonical_file)
        hostile.__file__ = str(linked_file)
    elif provenance == "invalid":
        hostile.__file__ = object()
    hostile.OpenRouterCompletion = type("OpenRouterCompletion", (), {})
    hostile.OpenRouterError = type("OpenRouterError", (Exception,), {})
    hostile.chat_completion = hostile_chat_completion
    saved_caller = sys.modules.pop(caller_module, None)
    sys.modules["nexus_external.openrouter_client"] = hostile
    external_package.openrouter_client = hostile
    imported: object | None = None
    try:
        try:
            imported = importlib.import_module(caller_module)
        except (ImportError, RuntimeError):
            pass
        if imported is not None:
            assert getattr(imported, "chat_completion") is not hostile_chat_completion
            assert getattr(imported, "_openrouter_client") is not hostile
        assert hostile_calls == 0
    finally:
        sys.modules.pop(caller_module, None)
        sys.modules["nexus_external.openrouter_client"] = authentic_submodule
        external_package.openrouter_client = authentic_submodule
        if saved_caller is not None:
            sys.modules[caller_module] = saved_caller
