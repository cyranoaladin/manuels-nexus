"""Frontiere partagee des services externes Nexus."""

from .openrouter_client import (
    OpenRouterCompletion,
    OpenRouterError,
    OpenRouterUsage,
    chat_completion,
)

__all__ = [
    "OpenRouterCompletion",
    "OpenRouterError",
    "OpenRouterUsage",
    "chat_completion",
]
