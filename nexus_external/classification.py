"""Classification pedagogique partagee, locale ou via OpenRouter."""

from __future__ import annotations

from collections.abc import Mapping
import json

from .openrouter_client import OpenRouterError, chat_completion


CLASSIFICATION_KEYS = frozenset(
    {"chunk_type", "niveau", "theme", "capacites", "difficulte"}
)
CHUNK_TYPES = frozenset(
    {
        "cours",
        "methode",
        "exercice",
        "corrige",
        "activite",
        "evaluation",
        "erreur_type",
        "autre",
    }
)
LEVELS = frozenset({"2GT", "1SPE", "TSPE", "TEXP"})
CONSERVATIVE_CLASSIFICATION = {
    "chunk_type": "autre",
    "niveau": None,
    "theme": None,
    "capacites": [],
    "difficulte": None,
}
CLASSIFICATION_PROMPT = (
    "Classe ce fragment de ressource de mathématiques (lycée français). "
    "Réponds UNIQUEMENT en JSON: {\"chunk_type\": "
    "cours|methode|exercice|corrige|activite|evaluation|erreur_type|autre, "
    "\"niveau\": 2GT|1SPE|TSPE|TEXP|null, \"theme\": mot-clé majuscule "
    "ou null, \"capacites\": [], \"difficulte\": 1|2|3|null}"
)


def _conservative_classification() -> dict[str, object]:
    return {
        "chunk_type": "autre",
        "niveau": None,
        "theme": None,
        "capacites": [],
        "difficulte": None,
    }


def classify_locally(chunk: str) -> dict[str, object]:
    """Classifie un fragment par la cascade lexicale historique."""

    lowered = chunk.lower()
    if lowered.startswith(("exercice", "probl")):
        chunk_type = "exercice"
    elif lowered.startswith(("correction", "corrig")):
        chunk_type = "corrige"
    elif lowered.startswith("méthode"):
        chunk_type = "methode"
    elif lowered.startswith(("définition", "théorème", "propriété")):
        chunk_type = "cours"
    elif lowered.startswith("activit"):
        chunk_type = "activite"
    else:
        chunk_type = "autre"

    result = _conservative_classification()
    result["chunk_type"] = chunk_type
    return result


def parse_remote_classification(content: str) -> dict[str, object]:
    """Valide integralement un objet de classification distant ferme."""

    if not isinstance(content, str):
        return _conservative_classification()
    encoded = content.strip()
    fence_start = "```json\n"
    fence_end = "\n```"
    if encoded.startswith(fence_start) and encoded.endswith(fence_end):
        encoded = encoded[len(fence_start) : -len(fence_end)]

    try:
        candidate = json.loads(encoded)
    except (json.JSONDecodeError, TypeError):
        return _conservative_classification()

    if not isinstance(candidate, dict) or set(candidate) != CLASSIFICATION_KEYS:
        return _conservative_classification()
    if (
        not isinstance(candidate["chunk_type"], str)
        or candidate["chunk_type"] not in CHUNK_TYPES
    ):
        return _conservative_classification()
    if candidate["niveau"] is not None and (
        not isinstance(candidate["niveau"], str)
        or candidate["niveau"] not in LEVELS
    ):
        return _conservative_classification()
    if candidate["theme"] is not None and not isinstance(candidate["theme"], str):
        return _conservative_classification()

    capacities = candidate["capacites"]
    if not isinstance(capacities, list) or not all(
        isinstance(capacity, str) for capacity in capacities
    ):
        return _conservative_classification()

    difficulty = candidate["difficulte"]
    if difficulty is not None and (
        isinstance(difficulty, bool)
        or not isinstance(difficulty, int)
        or difficulty not in {1, 2, 3}
    ):
        return _conservative_classification()

    return {
        "chunk_type": candidate["chunk_type"],
        "niveau": candidate["niveau"],
        "theme": candidate["theme"],
        "capacites": list(capacities),
        "difficulte": difficulty,
    }


def classify_chunk(
    chunk: str,
    *,
    environ: Mapping[str, str],
    transport: object | None = None,
) -> dict[str, object]:
    """Classifie localement sans cle, sinon par un unique appel OpenRouter."""

    api_key = environ.get("OPENROUTER_API_KEY", "")
    if not api_key.strip():
        return classify_locally(chunk)

    model = environ.get("OPENROUTER_MODEL", "")
    if not model.strip():
        raise OpenRouterError("configuration", model="")

    fragment = chunk[:3000]
    completion = chat_completion(
        api_key=api_key,
        model=model,
        messages=[
            {
                "role": "user",
                "content": f"{CLASSIFICATION_PROMPT}\n\nFRAGMENT:\n{fragment}",
            }
        ],
        max_completion_tokens=200,
        transport=transport,
    )
    return parse_remote_classification(completion.content)
