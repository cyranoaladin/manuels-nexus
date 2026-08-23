"""Chargement isole des modules siblings pour les CLI NSI directs."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType


def load_sibling_module(
    *,
    anchor: str,
    filename: str,
    private_name: str,
) -> ModuleType:
    sibling_path = Path(anchor).resolve().with_name(filename)
    cached = sys.modules.get(private_name)
    if cached is not None:
        cached_path = Path(getattr(cached, "__file__", "")).resolve()
        if cached_path != sibling_path:
            raise ImportError(
                f"Module prive {private_name} deja charge depuis {cached_path}"
            )
        return cached

    spec = importlib.util.spec_from_file_location(private_name, sibling_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Chargement du module NSI impossible : {sibling_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[private_name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        if sys.modules.get(private_name) is module:
            del sys.modules[private_name]
        raise
    return module
