"""Client minimal pour les chat completions OpenRouter."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math
from typing import Literal, TypeAlias

import httpx


OPENROUTER_CHAT_COMPLETIONS_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

ErrorCategory: TypeAlias = Literal[
    "configuration",
    "payment",
    "authentication",
    "authorization",
    "rate_limit",
    "timeout",
    "transport",
    "unavailable",
    "protocol",
]


@dataclass(frozen=True, slots=True)
class OpenRouterUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float
    cached_tokens: int
    cache_write_tokens: int


@dataclass(frozen=True, slots=True)
class OpenRouterCompletion:
    content: str
    generation_id: str
    model: str
    provider: str | None
    usage: OpenRouterUsage


class OpenRouterError(RuntimeError):
    def __init__(
        self,
        category: ErrorCategory,
        *,
        model: str,
        status_code: int | None = None,
    ) -> None:
        self.category = category
        self.status_code = status_code
        self.model = model
        status = f" status={status_code}" if status_code is not None else ""
        super().__init__(
            f"OpenRouter {category}{status} "
            f"endpoint={OPENROUTER_CHAT_COMPLETIONS_URL} model={model}"
        )


def _category_for_status(status: int) -> ErrorCategory:
    if status == 402:
        return "payment"
    if status == 401:
        return "authentication"
    if status == 403:
        return "authorization"
    if status == 429:
        return "rate_limit"
    if status == 408:
        return "timeout"
    if status >= 500:
        return "unavailable"
    return "protocol"


def _protocol_error(*, model: str, status_code: int) -> OpenRouterError:
    return OpenRouterError("protocol", model=model, status_code=status_code)


def _required_non_negative_int(
    value: object,
    *,
    model: str,
    status_code: int,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise _protocol_error(model=model, status_code=status_code)
    return value


def _cache_counter(
    details: Mapping[str, object],
    field: str,
    *,
    prompt_tokens: int,
    model: str,
    status_code: int,
) -> int:
    if field not in details:
        return 0
    value = _required_non_negative_int(
        details[field],
        model=model,
        status_code=status_code,
    )
    if value > prompt_tokens:
        raise _protocol_error(model=model, status_code=status_code)
    return value


def _parse_usage(
    value: object,
    *,
    model: str,
    status_code: int,
) -> OpenRouterUsage:
    if not isinstance(value, Mapping):
        raise _protocol_error(model=model, status_code=status_code)

    try:
        prompt_value = value["prompt_tokens"]
        completion_value = value["completion_tokens"]
        total_value = value["total_tokens"]
        cost_value = value["cost"]
    except KeyError:
        raise _protocol_error(model=model, status_code=status_code) from None

    prompt_tokens = _required_non_negative_int(
        prompt_value,
        model=model,
        status_code=status_code,
    )
    completion_tokens = _required_non_negative_int(
        completion_value,
        model=model,
        status_code=status_code,
    )
    total_tokens = _required_non_negative_int(
        total_value,
        model=model,
        status_code=status_code,
    )
    if total_tokens != prompt_tokens + completion_tokens:
        raise _protocol_error(model=model, status_code=status_code)
    if (
        isinstance(cost_value, bool)
        or not isinstance(cost_value, (int, float))
        or (isinstance(cost_value, float) and not math.isfinite(cost_value))
        or cost_value < 0
    ):
        raise _protocol_error(model=model, status_code=status_code)

    details_value = value.get("prompt_tokens_details", {})
    if not isinstance(details_value, Mapping):
        raise _protocol_error(model=model, status_code=status_code)
    cached_tokens = _cache_counter(
        details_value,
        "cached_tokens",
        prompt_tokens=prompt_tokens,
        model=model,
        status_code=status_code,
    )
    cache_write_tokens = _cache_counter(
        details_value,
        "cache_write_tokens",
        prompt_tokens=prompt_tokens,
        model=model,
        status_code=status_code,
    )
    return OpenRouterUsage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        cost=cost_value,
        cached_tokens=cached_tokens,
        cache_write_tokens=cache_write_tokens,
    )


def _parse_completion(
    value: object,
    *,
    status_code: int,
    requested_model: str,
) -> OpenRouterCompletion:
    if not isinstance(value, Mapping) or "error" in value:
        raise _protocol_error(model=requested_model, status_code=status_code)

    generation_id = value.get("id")
    returned_model = value.get("model")
    if not isinstance(generation_id, str) or not generation_id.strip():
        raise _protocol_error(model=requested_model, status_code=status_code)
    if not isinstance(returned_model, str) or not returned_model.strip():
        raise _protocol_error(model=requested_model, status_code=status_code)

    provider: str | None = None
    if "provider" in value:
        provider_value = value["provider"]
        if not isinstance(provider_value, str) or not provider_value.strip():
            raise _protocol_error(model=requested_model, status_code=status_code)
        provider = provider_value

    choices = value.get("choices")
    if not isinstance(choices, list) or not choices:
        raise _protocol_error(model=requested_model, status_code=status_code)
    choice = choices[0]
    if not isinstance(choice, Mapping) or "error" in choice:
        raise _protocol_error(model=requested_model, status_code=status_code)
    if choice.get("finish_reason") != "stop":
        raise _protocol_error(model=requested_model, status_code=status_code)
    message = choice.get("message")
    if not isinstance(message, Mapping) or set(message) != {"role", "content"}:
        raise _protocol_error(model=requested_model, status_code=status_code)
    if message["role"] != "assistant":
        raise _protocol_error(model=requested_model, status_code=status_code)
    content = message["content"]
    if not isinstance(content, str) or not content.strip():
        raise _protocol_error(model=requested_model, status_code=status_code)

    usage = _parse_usage(
        value.get("usage"),
        model=requested_model,
        status_code=status_code,
    )
    return OpenRouterCompletion(
        content=content,
        generation_id=generation_id,
        model=returned_model,
        provider=provider,
        usage=usage,
    )


def chat_completion(
    *,
    api_key: str,
    model: str,
    messages: Sequence[Mapping[str, str]],
    max_completion_tokens: int,
    transport: httpx.BaseTransport | None = None,
) -> OpenRouterCompletion:
    error_model = model if isinstance(model, str) and model.strip() else "<invalid>"
    if not isinstance(api_key, str) or not api_key.strip():
        raise OpenRouterError("configuration", model=error_model)
    if not isinstance(model, str) or not model.strip():
        raise OpenRouterError("configuration", model=error_model)
    if (
        isinstance(max_completion_tokens, bool)
        or not isinstance(max_completion_tokens, int)
        or not 1 <= max_completion_tokens <= 16_384
    ):
        raise OpenRouterError("configuration", model=model)
    if (
        not isinstance(messages, Sequence)
        or isinstance(messages, (str, bytes))
        or not messages
    ):
        raise OpenRouterError("configuration", model=model)
    for message in messages:
        if not isinstance(message, Mapping) or set(message) != {"role", "content"}:
            raise OpenRouterError("configuration", model=model)
        role = message["role"]
        content = message["content"]
        if not isinstance(role, str) or role not in {"system", "user", "assistant"}:
            raise OpenRouterError("configuration", model=model)
        if not isinstance(content, str) or not content.strip():
            raise OpenRouterError("configuration", model=model)

    request_messages = [dict(message) for message in messages]
    try:
        with httpx.Client(
            timeout=httpx.Timeout(30.0),
            follow_redirects=False,
            trust_env=False,
            transport=transport,
        ) as client:
            response = client.post(
                OPENROUTER_CHAT_COMPLETIONS_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": request_messages,
                    "max_completion_tokens": max_completion_tokens,
                },
            )
    except httpx.TimeoutException:
        raise OpenRouterError("timeout", model=model) from None
    except httpx.TransportError:
        raise OpenRouterError("transport", model=model) from None

    if not response.is_success:
        raise OpenRouterError(
            _category_for_status(response.status_code),
            model=model,
            status_code=response.status_code,
        )
    try:
        payload = response.json()
    except ValueError:
        raise _protocol_error(
            model=model,
            status_code=response.status_code,
        ) from None
    return _parse_completion(
        payload,
        status_code=response.status_code,
        requested_model=model,
    )
