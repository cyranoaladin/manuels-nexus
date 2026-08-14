"""Contrat Red du client OpenRouter partage.

Ce module ne doit jamais ouvrir de socket reel. Les imports du futur paquet
``nexus_external`` restent volontairement dans les corps de tests/helpers
appeles a l'execution afin que la collecte du jalon Red demeure saine.
"""

from __future__ import annotations

import copy
import dataclasses
import importlib
import json
import math
import socket
import time
import traceback
import urllib.request
from collections.abc import Callable
from typing import Any

import httpx
import pytest


ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "openrouter-key-sentinel"
MODEL = "vendor/model-explicit"
MESSAGES = [{"role": "user", "content": "fragment pedagogique"}]
_UNSET = object()


@pytest.fixture(autouse=True)
def _forbid_real_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def blocked(*args: object, **kwargs: object) -> None:
        raise AssertionError("network forbidden by OpenRouter contract tests")

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


def _client_module() -> Any:
    return importlib.import_module("nexus_external.openrouter_client")


def _success_payload() -> dict[str, object]:
    return {
        "id": "gen-openrouter-001",
        "model": MODEL,
        "provider": "provider-observed",
        "choices": [
            {
                "finish_reason": "stop",
                "message": {
                    "role": "assistant",
                    "content": "réponse complète",
                },
            }
        ],
        "usage": {
            "prompt_tokens": 11,
            "completion_tokens": 7,
            "total_tokens": 18,
            "cost": 0.0012345,
            "prompt_tokens_details": {
                "cached_tokens": 3,
                "cache_write_tokens": 2,
            },
        },
    }


def _transport_for(
    payload: object = _UNSET,
    *,
    status_code: int = 200,
    seen: list[httpx.Request] | None = None,
) -> httpx.MockTransport:
    body = _success_payload() if payload is _UNSET else payload

    def handler(request: httpx.Request) -> httpx.Response:
        if seen is not None:
            seen.append(request)
        if body is None:
            return httpx.Response(
                status_code,
                content=b"null",
                headers={"content-type": "application/json"},
            )
        copied_body = copy.deepcopy(body)
        try:
            return httpx.Response(status_code, json=copied_body)
        except ValueError:
            return httpx.Response(
                status_code,
                content=json.dumps(
                    copied_body,
                    allow_nan=True,
                    ensure_ascii=False,
                ).encode("utf-8"),
                headers={"content-type": "application/json"},
            )

    return httpx.MockTransport(handler)


def _call(
    module: Any,
    transport: httpx.MockTransport,
    *,
    api_key: object = API_KEY,
    model: object = MODEL,
    messages: object = _UNSET,
    max_completion_tokens: object = 321,
) -> object:
    selected_messages = MESSAGES if messages is _UNSET else messages
    return module.chat_completion(
        api_key=api_key,
        model=model,
        messages=selected_messages,
        max_completion_tokens=max_completion_tokens,
        transport=transport,
    )


def _assert_error(
    module: Any,
    operation: Callable[[], object],
    *,
    category: str,
    status_code: int | None = None,
) -> BaseException:
    with pytest.raises(module.OpenRouterError) as caught:
        operation()
    error = caught.value
    assert error.category == category
    assert error.status_code == status_code
    return error


def _assert_sanitized(error: BaseException, sentinels: tuple[str, ...]) -> None:
    rendered = "\n".join((str(error), repr(error), repr(error.args)))
    for sentinel in sentinels:
        assert sentinel not in rendered


def test_chat_completion_posts_to_exact_openrouter_endpoint() -> None:
    module = _client_module()
    seen: list[httpx.Request] = []

    _call(module, _transport_for(seen=seen))

    assert len(seen) == 1
    assert seen[0].method == "POST"
    assert str(seen[0].url) == ENDPOINT


def test_chat_completion_sends_bearer_and_json_headers() -> None:
    module = _client_module()
    seen: list[httpx.Request] = []

    _call(module, _transport_for(seen=seen))

    assert len(seen) == 1
    request = seen[0]
    assert request.headers["Authorization"] == f"Bearer {API_KEY}"
    assert request.headers["Content-Type"].split(";", maxsplit=1)[0] == (
        "application/json"
    )
    assert API_KEY not in str(request.url)
    assert API_KEY not in repr(request)


def test_chat_completion_sends_one_model_and_max_completion_tokens() -> None:
    module = _client_module()
    seen: list[httpx.Request] = []
    allowed_messages = [
        {"role": "system", "content": "instruction"},
        {"role": "user", "content": "question"},
        {"role": "assistant", "content": "contexte"},
    ]
    _call(
        module,
        _transport_for(seen=seen),
        messages=allowed_messages,
        max_completion_tokens=16_384,
    )

    assert len(seen) == 1
    body = json.loads(seen[0].content)
    assert set(body) == {"model", "messages", "max_completion_tokens"}
    assert body["model"] == MODEL
    assert body["messages"] == allowed_messages
    assert body["max_completion_tokens"] == 16_384
    assert "models" not in body
    assert "max_tokens" not in body
    assert all("provider" not in key.lower() for key in body)

    calls = 0

    def forbidden_transport(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise AssertionError(f"transport called for invalid input: {request.url}")

    transport = httpx.MockTransport(forbidden_transport)
    invalid_cases: tuple[tuple[str, dict[str, object]], ...] = (
        ("zero-token-sentinel", {"max_completion_tokens": 0}),
        ("boolean-token-sentinel", {"max_completion_tokens": True}),
        ("oversize-token-sentinel", {"max_completion_tokens": 16_385}),
        ("empty-messages-sentinel", {"messages": []}),
        (
            "non-sequence-messages-sentinel",
            {"messages": "non-sequence-messages-sentinel"},
        ),
        (
            "non-map-message-sentinel",
            {"messages": ["non-map-message-sentinel"]},
        ),
        ("missing-role-sentinel", {"messages": [{"content": "valid"}]}),
        (
            "invalid-role-sentinel",
            {
                "messages": [
                    {"role": "invalid-role-sentinel", "content": "valid"}
                ]
            },
        ),
        ("missing-content-sentinel", {"messages": [{"role": "user"}]}),
        (
            "non-string-content-sentinel",
            {"messages": [{"role": "user", "content": 42}]},
        ),
        (
            "blank-content-sentinel",
            {"messages": [{"role": "user", "content": "   "}]},
        ),
        (
            "extra-message-key-sentinel",
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "valid",
                        "extra-message-key-sentinel": "extra-message-key-sentinel",
                    }
                ]
            },
        ),
    )
    for sentinel, overrides in invalid_cases:
        error = _assert_error(
            module,
            lambda overrides=overrides: _call(module, transport, **overrides),
            category="configuration",
        )
        _assert_sanitized(error, (sentinel,))
    assert calls == 0


def test_chat_completion_uses_injected_mock_transport_without_socket() -> None:
    _prove_network_guard()
    module = _client_module()
    seen: list[httpx.Request] = []

    result = _call(module, _transport_for(seen=seen))

    assert len(seen) == 1
    assert result.content == "réponse complète"


def test_chat_completion_caps_timeout_at_thirty_seconds() -> None:
    module = _client_module()
    observed: list[dict[str, float]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request.extensions["timeout"])
        return httpx.Response(200, json=_success_payload())

    _call(module, httpx.MockTransport(handler))

    assert len(observed) == 1
    timeout = observed[0]
    assert set(timeout) == {"connect", "read", "write", "pool"}
    assert all(value is not None and 0 < value <= 30 for value in timeout.values())


def test_chat_completion_does_not_follow_redirects() -> None:
    module = _client_module()
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(str(request.url))
        return httpx.Response(
            307,
            headers={"location": "https://hostile.invalid/steal"},
        )

    error = _assert_error(
        module,
        lambda: _call(module, httpx.MockTransport(handler)),
        category="protocol",
        status_code=307,
    )
    assert seen == [ENDPOINT]
    assert "hostile.invalid" not in str(error)


def test_chat_completion_returns_validated_structured_result() -> None:
    module = _client_module()

    result = _call(module, _transport_for())

    assert isinstance(result, module.OpenRouterCompletion)
    assert tuple(field.name for field in dataclasses.fields(result)) == (
        "content",
        "generation_id",
        "model",
        "provider",
        "usage",
    )
    assert result.content == "réponse complète"
    assert result.generation_id == "gen-openrouter-001"
    assert result.model == MODEL
    assert result.provider == "provider-observed"
    assert isinstance(result.usage, module.OpenRouterUsage)
    assert tuple(field.name for field in dataclasses.fields(result.usage)) == (
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "cost",
        "cached_tokens",
        "cache_write_tokens",
    )
    assert dataclasses.asdict(result.usage) == {
        "prompt_tokens": 11,
        "completion_tokens": 7,
        "total_tokens": 18,
        "cost": 0.0012345,
        "cached_tokens": 3,
        "cache_write_tokens": 2,
    }

    without_provider = _success_payload()
    without_provider.pop("provider")
    result_without_provider = _call(module, _transport_for(without_provider))
    assert result_without_provider.provider is None


def test_completion_and_usage_are_immutable() -> None:
    module = _client_module()
    usage = module.OpenRouterUsage(
        prompt_tokens=11,
        completion_tokens=7,
        total_tokens=18,
        cost=0.0012345,
        cached_tokens=3,
        cache_write_tokens=2,
    )
    completion = module.OpenRouterCompletion(
        content="réponse complète",
        generation_id="gen-openrouter-001",
        model=MODEL,
        provider="provider-observed",
        usage=usage,
    )

    with pytest.raises(dataclasses.FrozenInstanceError):
        completion.content = "altérée"
    with pytest.raises(dataclasses.FrozenInstanceError):
        usage.cost = 999.0
    assert not hasattr(completion, "__dict__")
    assert not hasattr(usage, "__dict__")


def test_http_failure_maps_to_sanitized_error_category() -> None:
    module = _client_module()
    mapping = {
        400: "protocol",
        401: "authentication",
        402: "payment",
        403: "authorization",
        408: "timeout",
        429: "rate_limit",
        500: "unavailable",
        502: "unavailable",
        503: "unavailable",
        529: "unavailable",
    }
    for status, category in mapping.items():
        raw = f"raw-body-{status}-sentinel"
        header = f"response-header-{status}-sentinel"
        calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            return httpx.Response(
                status,
                content=raw,
                headers={"x-sensitive-debug": header},
            )

        error = _assert_error(
            module,
            lambda: _call(module, httpx.MockTransport(handler)),
            category=category,
            status_code=status,
        )
        assert calls == 1
        _assert_sanitized(error, (API_KEY, MESSAGES[0]["content"], raw, header))


def test_http_200_refuses_root_error_object() -> None:
    module = _client_module()
    payload = _success_payload()
    payload["error"] = {"message": "root-error-body-sentinel"}

    error = _assert_error(
        module,
        lambda: _call(module, _transport_for(payload)),
        category="protocol",
        status_code=200,
    )
    _assert_sanitized(error, ("root-error-body-sentinel",))


def test_http_200_refuses_choice_error_object() -> None:
    module = _client_module()
    payload = _success_payload()
    payload["choices"][0]["error"] = {"message": "choice-error-body-sentinel"}

    error = _assert_error(
        module,
        lambda: _call(module, _transport_for(payload)),
        category="protocol",
        status_code=200,
    )
    _assert_sanitized(error, ("choice-error-body-sentinel",))


def test_http_200_refuses_non_stop_finish_reason() -> None:
    module = _client_module()
    for finish_reason in (_UNSET, "error", "length", "content_filter", "", 7):
        payload = _success_payload()
        if finish_reason is _UNSET:
            payload["choices"][0].pop("finish_reason")
        else:
            payload["choices"][0]["finish_reason"] = finish_reason
        _assert_error(
            module,
            lambda payload=payload: _call(module, _transport_for(payload)),
            category="protocol",
            status_code=200,
        )


def test_response_rejects_malformed_envelope_component() -> None:
    module = _client_module()
    malformed: list[object] = [[], None, "not-an-object"]

    payload = _success_payload()
    payload.pop("choices")
    malformed.append(payload)
    for choices in (None, {}, [], ["not-an-object"]):
        payload = _success_payload()
        payload["choices"] = choices
        malformed.append(payload)
    for message in (None, [], "not-an-object"):
        payload = _success_payload()
        payload["choices"][0]["message"] = message
        malformed.append(payload)
    for role in (None, "user", "tool", 3):
        payload = _success_payload()
        if role is None:
            payload["choices"][0]["message"].pop("role")
        else:
            payload["choices"][0]["message"]["role"] = role
        malformed.append(payload)
    for content in (_UNSET, None, 5, "", "   "):
        payload = _success_payload()
        if content is _UNSET:
            payload["choices"][0]["message"].pop("content")
        else:
            payload["choices"][0]["message"]["content"] = content
        malformed.append(payload)
    payload = _success_payload()
    payload["choices"][0]["message"]["name"] = "unexpected"
    malformed.append(payload)
    for provider in ("", "   ", 9, None):
        payload = _success_payload()
        payload["provider"] = provider
        malformed.append(payload)

    for candidate in malformed:
        _assert_error(
            module,
            lambda candidate=candidate: _call(
                module,
                _transport_for(candidate),
            ),
            category="protocol",
            status_code=200,
        )

    def non_json_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"{non-json-envelope-sentinel")

    non_json_error = _assert_error(
        module,
        lambda: _call(module, httpx.MockTransport(non_json_handler)),
        category="protocol",
        status_code=200,
    )
    _assert_sanitized(non_json_error, ("non-json-envelope-sentinel",))

    hostile_second_choice = "hostile-second-choice-secret"
    payload = _success_payload()
    payload["choices"].append(
        {
            "finish_reason": "length",
            "message": {
                "role": "tool",
                "content": hostile_second_choice,
                "extra": "forbidden",
            },
        }
    )
    result = _call(module, _transport_for(payload))
    assert result.content == "réponse complète"
    assert hostile_second_choice not in repr(result)


def test_errors_and_logs_never_expose_secret_prompt_or_raw_body(
    caplog: pytest.LogCaptureFixture,
) -> None:
    module = _client_module()
    key = "key-secret-sentinel"
    prompt = "prompt-secret-sentinel"
    response_header = "header-secret-sentinel"
    raw_body = "raw-body-secret-sentinel"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            500,
            content=raw_body,
            headers={"x-debug-secret": response_header},
        )

    with caplog.at_level("DEBUG"):
        error = _assert_error(
            module,
            lambda: _call(
                module,
                httpx.MockTransport(handler),
                api_key=key,
                messages=[{"role": "user", "content": prompt}],
            ),
            category="unavailable",
            status_code=500,
        )
    sentinels = (key, prompt, response_header, raw_body)
    _assert_sanitized(error, sentinels)
    rendered_traceback = "".join(
        traceback.TracebackException.from_exception(error).format()
    )
    logs = "\n".join(record.getMessage() for record in caplog.records)
    for sentinel in sentinels:
        assert sentinel not in caplog.text
        assert sentinel not in rendered_traceback
        assert sentinel not in logs


def test_client_does_not_retry_failed_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _client_module()

    def forbidden_sleep(delay: float) -> None:
        raise AssertionError(f"client attempted retry sleep: {delay}")

    monkeypatch.setattr(time, "sleep", forbidden_sleep)
    failures: tuple[tuple[type[httpx.HTTPError], str, str], ...] = (
        (httpx.ConnectError, "transport", "connect-raw-secret"),
        (httpx.ReadTimeout, "timeout", "read-timeout-raw-secret"),
        (httpx.TimeoutException, "timeout", "timeout-raw-secret"),
    )
    for exception_type, category, sentinel in failures:
        calls = 0

        def handler(
            request: httpx.Request,
            exception_type: type[httpx.HTTPError] = exception_type,
            sentinel: str = sentinel,
        ) -> httpx.Response:
            nonlocal calls
            calls += 1
            raise exception_type(sentinel, request=request)

        error = _assert_error(
            module,
            lambda: _call(module, httpx.MockTransport(handler)),
            category=category,
        )
        assert calls == 1
        _assert_sanitized(error, (sentinel, API_KEY))


def test_client_rejects_blank_key_before_transport() -> None:
    module = _client_module()
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise AssertionError(f"unexpected transport call: {request.url}")

    transport = httpx.MockTransport(handler)
    for blank in (None, "", "   "):
        _assert_error(
            module,
            lambda blank=blank: _call(module, transport, api_key=blank),
            category="configuration",
        )
    assert calls == 0


def test_client_rejects_blank_model_before_transport() -> None:
    module = _client_module()
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise AssertionError(f"unexpected transport call: {request.url}")

    transport = httpx.MockTransport(handler)
    for blank in (None, "", "   "):
        _assert_error(
            module,
            lambda blank=blank: _call(module, transport, model=blank),
            category="configuration",
        )
    assert calls == 0


def test_usage_rejects_invalid_required_accounting() -> None:
    module = _client_module()
    invalid: list[dict[str, object]] = []

    payload = _success_payload()
    payload.pop("usage")
    invalid.append(payload)
    for usage in (None, [], "non-object-usage-sentinel"):
        payload = _success_payload()
        payload["usage"] = usage
        invalid.append(payload)
    for field in ("prompt_tokens", "completion_tokens", "total_tokens", "cost"):
        payload = _success_payload()
        payload["usage"].pop(field)
        invalid.append(payload)
    for field in ("prompt_tokens", "completion_tokens", "total_tokens"):
        for value in (True, -1, 1.5, "11"):
            payload = _success_payload()
            payload["usage"][field] = value
            invalid.append(payload)
    payload = _success_payload()
    payload["usage"]["total_tokens"] = 19
    invalid.append(payload)
    for value in (True, -0.01, math.nan, math.inf, -math.inf, "0.2"):
        payload = _success_payload()
        payload["usage"]["cost"] = value
        invalid.append(payload)

    for candidate in invalid:
        _assert_error(
            module,
            lambda candidate=candidate: _call(module, _transport_for(candidate)),
            category="protocol",
            status_code=200,
        )


def test_usage_rejects_invalid_cache_details() -> None:
    module = _client_module()
    invalid: list[dict[str, object]] = []
    for details in (None, [], "not-an-object"):
        payload = _success_payload()
        payload["usage"]["prompt_tokens_details"] = details
        invalid.append(payload)
    for field in ("cached_tokens", "cache_write_tokens"):
        for value in (True, -1, 12, 1.5, "2"):
            payload = _success_payload()
            payload["usage"]["prompt_tokens_details"][field] = value
            invalid.append(payload)

    for candidate in invalid:
        _assert_error(
            module,
            lambda candidate=candidate: _call(module, _transport_for(candidate)),
            category="protocol",
            status_code=200,
        )


def test_usage_normalizes_absent_cache_counters_to_zero() -> None:
    module = _client_module()
    cases: tuple[tuple[object, tuple[int, int]], ...] = (
        (_UNSET, (0, 0)),
        ({}, (0, 0)),
        ({"cached_tokens": 3}, (3, 0)),
        ({"cache_write_tokens": 2}, (0, 2)),
    )
    for details, expected in cases:
        payload = _success_payload()
        if details is _UNSET:
            payload["usage"].pop("prompt_tokens_details")
        else:
            payload["usage"]["prompt_tokens_details"] = details
        usage = _call(module, _transport_for(payload)).usage
        assert (usage.cached_tokens, usage.cache_write_tokens) == expected


def test_usage_preserves_exact_openrouter_cost() -> None:
    module = _client_module()
    payload = _success_payload()
    payload["usage"]["cost"] = 0.0012345

    result = _call(module, _transport_for(payload))

    assert result.usage.cost == 0.0012345
    assert math.isclose(result.usage.cost, payload["usage"]["cost"], rel_tol=0.0)


def test_response_rejects_invalid_root_generation_id() -> None:
    module = _client_module()
    for generation_id in (_UNSET, None, 17, "", "   "):
        payload = _success_payload()
        if generation_id is _UNSET:
            payload.pop("id")
        else:
            payload["id"] = generation_id
        _assert_error(
            module,
            lambda payload=payload: _call(module, _transport_for(payload)),
            category="protocol",
            status_code=200,
        )


def test_response_rejects_invalid_returned_model() -> None:
    module = _client_module()
    for returned_model in (_UNSET, None, 17, "", "   "):
        payload = _success_payload()
        if returned_model is _UNSET:
            payload.pop("model")
        else:
            payload["model"] = returned_model
        _assert_error(
            module,
            lambda payload=payload: _call(module, _transport_for(payload)),
            category="protocol",
            status_code=200,
        )
