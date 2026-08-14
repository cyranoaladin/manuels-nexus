"""Contrat Red de la classification pedagogique partagee OpenRouter."""

from __future__ import annotations

import importlib
import importlib.util
import json
import socket
import sys
import traceback
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx
import pytest


CHECKOUT_ROOT = Path(__file__).resolve().parents[1]
MODEL = "vendor/model-explicit"
API_KEY = "classification-key-sentinel"
CLASSIFICATION_KEYS = {
    "chunk_type",
    "niveau",
    "theme",
    "capacites",
    "difficulte",
}
CONSERVATIVE = {
    "chunk_type": "autre",
    "niveau": None,
    "theme": None,
    "capacites": [],
    "difficulte": None,
}
VALID_REMOTE = {
    "chunk_type": "cours",
    "niveau": "1SPE",
    "theme": "ALGEBRE",
    "capacites": ["resoudre une equation"],
    "difficulte": 2,
}


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


def _classification_module() -> Any:
    return importlib.import_module("nexus_external.classification")


def _client_module() -> Any:
    return importlib.import_module("nexus_external.openrouter_client")


def _remote_payload(content: str) -> dict[str, object]:
    return {
        "id": "gen-classification-001",
        "model": MODEL,
        "provider": "provider-observed",
        "choices": [
            {
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": content},
            }
        ],
        "usage": {
            "prompt_tokens": 20,
            "completion_tokens": 10,
            "total_tokens": 30,
            "cost": 0.00042,
            "prompt_tokens_details": {
                "cached_tokens": 0,
                "cache_write_tokens": 0,
            },
        },
    }


def _transport_returning(
    content: str,
    *,
    seen: list[httpx.Request] | None = None,
) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        if seen is not None:
            seen.append(request)
        return httpx.Response(200, json=_remote_payload(content))

    return httpx.MockTransport(handler)


def _remote_environ(**extra: str) -> dict[str, str]:
    return {
        "OPENROUTER_API_KEY": API_KEY,
        "OPENROUTER_MODEL": MODEL,
        **extra,
    }


def _request_prompt(request: httpx.Request) -> str:
    body = json.loads(request.content)
    messages = body["messages"]
    assert isinstance(messages, list)
    assert len(messages) == 1
    message = messages[0]
    assert isinstance(message, dict)
    assert set(message) == {"role", "content"}
    assert message["role"] == "user"
    assert isinstance(message["content"], str)
    return message["content"]


def _load_ingest_module(path: Path, name: str) -> Any:
    """Charge l'adaptateur courant sans modifier ses sources."""

    previous_path = list(sys.path)
    previous_common = sys.modules.pop("common", None)
    try:
        sys.path.insert(0, str(path.parent))
        spec = importlib.util.spec_from_file_location(name, path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = previous_path
        sys.modules.pop("common", None)
        if previous_common is not None:
            sys.modules["common"] = previous_common


def test_classification_without_key_uses_local_heuristic_without_transport() -> None:
    _prove_network_guard()
    module = _classification_module()
    calls = 0

    def forbidden(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise AssertionError(f"transport called in local mode: {request.url}")

    expected = {
        "chunk_type": "exercice",
        "niveau": None,
        "theme": None,
        "capacites": [],
        "difficulte": None,
    }
    for key_state in (None, "", "   "):
        for model_state in (None, "", "  ", MODEL):
            environ = {
                "ANTHROPIC_API_KEY": "anthropic-key-must-be-ignored",
                "LOCAL_LLM_API_KEY": "local-key-must-be-ignored",
                "LOCAL_LLM_BASE_URL": "https://local-endpoint-must-be-ignored.invalid",
            }
            if key_state is not None:
                environ["OPENROUTER_API_KEY"] = key_state
            if model_state is not None:
                environ["OPENROUTER_MODEL"] = model_state
            result = module.classify_chunk(
                "Exercice 1 — Résoudre une équation.",
                environ=environ,
                transport=httpx.MockTransport(forbidden),
            )
            assert result == expected
            assert set(result) == CLASSIFICATION_KEYS
            assert calls == 0
    assert calls == 0


def test_classification_with_key_without_model_fails_before_transport(
    caplog: pytest.LogCaptureFixture,
) -> None:
    module = _classification_module()
    client = _client_module()
    calls = 0

    def forbidden(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise AssertionError(f"transport called without model: {request.url}")

    transport = httpx.MockTransport(forbidden)
    for model in (None, "", "   "):
        environ = {"OPENROUTER_API_KEY": API_KEY}
        if model is not None:
            environ["OPENROUTER_MODEL"] = model
        caplog.clear()
        with caplog.at_level("DEBUG"):
            with pytest.raises(client.OpenRouterError) as caught:
                module.classify_chunk(
                    "Définition d'une suite.",
                    environ=environ,
                    transport=transport,
                )
        error = caught.value
        assert error.category == "configuration"
        assert API_KEY not in str(error)
        assert API_KEY not in repr(error)
        assert all(API_KEY not in str(argument) for argument in error.args)
        formatted_traceback = "".join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )
        assert API_KEY not in formatted_traceback
        assert API_KEY not in caplog.text
        assert calls == 0
    assert calls == 0


def test_classification_with_key_and_model_forwards_exact_model() -> None:
    module = _classification_module()
    seen: list[httpx.Request] = []
    result = module.classify_chunk(
        "Définition d'une fonction affine.",
        environ=_remote_environ(),
        transport=_transport_returning(json.dumps(VALID_REMOTE), seen=seen),
    )

    assert result == VALID_REMOTE
    assert len(seen) == 1
    body = json.loads(seen[0].content)
    assert body["model"] == MODEL
    assert "models" not in body


def test_classification_sends_only_first_3000_fragment_characters() -> None:
    module = _classification_module()
    suffix = "suffix-beyond-limit-sentinel"
    fragment = "α" * 3_000 + suffix
    seen: list[httpx.Request] = []
    environ = _remote_environ(
        SOURCE_PATH="environment-path-sentinel",
        ANTHROPIC_API_KEY="legacy-key-sentinel",
    )

    module.classify_chunk(
        fragment,
        environ=environ,
        transport=_transport_returning(json.dumps(VALID_REMOTE), seen=seen),
    )

    assert len(seen) == 1
    prompt = _request_prompt(seen[0])
    assert fragment[:3_000] in prompt
    assert prompt.count(fragment[:3_000]) == 1
    assert suffix not in prompt
    assert "environment-path-sentinel" not in prompt
    assert "legacy-key-sentinel" not in prompt


def test_classification_requests_200_completion_tokens() -> None:
    module = _classification_module()
    seen: list[httpx.Request] = []

    module.classify_chunk(
        "Méthode pour factoriser.",
        environ=_remote_environ(),
        transport=_transport_returning(json.dumps(VALID_REMOTE), seen=seen),
    )

    assert len(seen) == 1
    body = json.loads(seen[0].content)
    assert body["max_completion_tokens"] == 200
    assert "max_tokens" not in body


def test_local_heuristic_preserves_existing_chunk_type_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _classification_module()
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    math_ingest = _load_ingest_module(
        CHECKOUT_ROOT / "Mathematiques/manuel-maths/scripts/ingest.py",
        "contract_math_ingest",
    )
    nsi_ingest = _load_ingest_module(
        CHECKOUT_ROOT / "NSI/scripts/ingest.py",
        "contract_nsi_ingest",
    )
    cases = {
        "Définition d'une suite numérique.": "cours",
        "Théorème des valeurs intermédiaires.": "cours",
        "Propriété de la fonction carré.": "cours",
        "Méthode pour résoudre une équation.": "methode",
        "Exercice 4 — Calculer une image.": "exercice",
        "Problème de modélisation.": "exercice",
        "Correction de l'exercice 4.": "corrige",
        "Corrigé détaillé.": "corrige",
        "Activité de découverte.": "activite",
        "Document de référence.": "autre",
    }
    for chunk, expected_type in cases.items():
        expected = {
            "chunk_type": expected_type,
            "niveau": None,
            "theme": None,
            "capacites": [],
            "difficulte": None,
        }
        assert math_ingest.classify(chunk) == expected
        assert nsi_ingest.classify(chunk) == expected
        assert module.classify_locally(chunk) == expected


def test_remote_classification_accepts_exact_closed_object() -> None:
    module = _classification_module()
    valid_objects = [VALID_REMOTE]
    for chunk_type in (
        "cours",
        "methode",
        "exercice",
        "corrige",
        "activite",
        "evaluation",
        "erreur_type",
        "autre",
    ):
        valid_objects.append(dict(VALID_REMOTE, chunk_type=chunk_type))
    for niveau in ("2GT", "1SPE", "TSPE", "TEXP", None):
        valid_objects.append(dict(VALID_REMOTE, niveau=niveau))
    for difficulte in (1, 2, 3, None):
        valid_objects.append(dict(VALID_REMOTE, difficulte=difficulte))
    valid_objects.extend(
        (
            dict(VALID_REMOTE, theme=None),
            dict(VALID_REMOTE, capacites=[]),
            dict(VALID_REMOTE, capacites=["une", "deux"]),
        )
    )

    for candidate in valid_objects:
        encoded = json.dumps(candidate, ensure_ascii=False)
        for text in (encoded, f"```json\n{encoded}\n```"):
            result = module.parse_remote_classification(text)
            assert result == candidate
            assert set(result) == CLASSIFICATION_KEYS


def test_remote_classification_rejects_invalid_closed_object_as_a_whole() -> None:
    module = _classification_module()
    invalid: list[str] = [
        "[]",
        "not-json",
        f"prefix {json.dumps(VALID_REMOTE)}",
        f"```python\n{json.dumps(VALID_REMOTE)}\n```",
        (
            f"```json\n{json.dumps(VALID_REMOTE)}\n```\n"
            f"```json\n{json.dumps(VALID_REMOTE)}\n```"
        ),
    ]
    mutations: list[dict[str, object]] = []
    candidate = dict(VALID_REMOTE)
    candidate.pop("theme")
    mutations.append(candidate)
    candidate = dict(VALID_REMOTE, extra="forbidden")
    mutations.append(candidate)
    mutations.extend(
        [
            dict(VALID_REMOTE, chunk_type="inconnu"),
            dict(VALID_REMOTE, chunk_type=7),
            dict(VALID_REMOTE, niveau="TERMINALE"),
            dict(VALID_REMOTE, niveau=1),
            dict(VALID_REMOTE, theme=7),
            dict(VALID_REMOTE, capacites="pas-une-liste"),
            dict(VALID_REMOTE, capacites=["valide", 4]),
            dict(VALID_REMOTE, difficulte=4),
            dict(VALID_REMOTE, difficulte=1.0),
            dict(VALID_REMOTE, difficulte="2"),
        ]
    )
    invalid.extend(json.dumps(candidate) for candidate in mutations)

    for text in invalid:
        result = module.parse_remote_classification(text)
        assert result == CONSERVATIVE
        assert set(result) == CLASSIFICATION_KEYS


def test_remote_classification_rejects_boolean_difficulty() -> None:
    module = _classification_module()
    for value in (True, False):
        candidate = dict(VALID_REMOTE, difficulte=value)
        result = module.parse_remote_classification(json.dumps(candidate))
        assert result == CONSERVATIVE
        assert set(result) == CLASSIFICATION_KEYS


def test_invalid_remote_classification_returns_global_conservative_result() -> None:
    module = _classification_module()
    partly_plausible = dict(VALID_REMOTE, niveau="niveau-invalide")
    seen: list[httpx.Request] = []

    result = module.classify_chunk(
        "Cours dont la réponse distante est invalide.",
        environ=_remote_environ(),
        transport=_transport_returning(json.dumps(partly_plausible), seen=seen),
    )

    assert len(seen) == 1
    assert result == CONSERVATIVE
    assert result["chunk_type"] != partly_plausible["chunk_type"]
    assert result["theme"] != partly_plausible["theme"]


def test_remote_metadata_cannot_override_trusted_record_fields() -> None:
    module = _classification_module()
    trusted = {
        "source_id": "trusted-source",
        "doc_url": "https://trusted.invalid/document",
        "doc_hash": "trusted-hash",
        "content_md": "trusted-content",
        "usage_policy": "trusted-policy",
        "tier": "trusted-tier",
    }
    for field, trusted_value in trusted.items():
        hostile = dict(VALID_REMOTE, **{field: f"hostile-{field}"})
        encoded = json.dumps(hostile)
        parsed = module.parse_remote_classification(encoded)
        assert parsed == CONSERVATIVE
        assert set(parsed) == CLASSIFICATION_KEYS

        classification = module.classify_chunk(
            "Fragment autorisé.",
            environ=_remote_environ(),
            transport=_transport_returning(encoded),
        )
        assert classification == CONSERVATIVE
        record = {**trusted, **classification}
        assert record[field] == trusted_value
        assert set(classification) == CLASSIFICATION_KEYS
        assert not (set(classification) & set(trusted))


def test_prompt_does_not_append_environment_or_provenance_metadata() -> None:
    module = _classification_module()
    provenance = {
        "source_id": "source-id-sentinel",
        "doc_url": "doc-url-sentinel",
        "doc_hash": "doc-hash-sentinel",
        "content_md": "content-md-sentinel",
        "usage_policy": "usage-policy-sentinel",
        "tier": "tier-sentinel",
    }
    environ = _remote_environ(
        **{key.upper(): value for key, value in provenance.items()},
        MACHINE_PATH="machine-path-sentinel",
        EXTRA_SECRET="extra-secret-sentinel",
    )
    seen: list[httpx.Request] = []

    module.classify_chunk(
        "Fragment public de test.",
        environ=environ,
        transport=_transport_returning(json.dumps(VALID_REMOTE), seen=seen),
    )

    assert len(seen) == 1
    prompt = _request_prompt(seen[0])
    forbidden = tuple(provenance.values()) + (
        "machine-path-sentinel",
        "extra-secret-sentinel",
    )
    for sentinel in forbidden:
        assert sentinel not in prompt
