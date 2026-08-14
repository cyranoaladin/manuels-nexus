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
import urllib.request
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
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
        return _campaign_result()

    monkeypatch.setenv("OPENROUTER_API_KEY", API_KEY)
    monkeypatch.setenv("OPENROUTER_MODEL", MODEL)
    monkeypatch.setattr(campaign, "merge_usage_log", traced_merge)
    monkeypatch.setattr(campaign, "parse_campaign_verdict", traced_parse)
    _install_campaign_main_doubles(monkeypatch, campaign, output_dir, fake_call)

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


def test_usage_upsert_preserves_v1_deeply_and_in_order(tmp_path: Path) -> None:
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


def test_corpus_callers_reject_shadowed_external_package(
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
            with pytest.raises((ImportError, RuntimeError), match="nexus_external|checkout|shadow"):
                importlib.import_module(module_name)
    finally:
        for name in list(sys.modules):
            if name == "nexus_external" or name.startswith("nexus_external."):
                sys.modules.pop(name, None)
        sys.modules.update(saved)
