from __future__ import annotations

import builtins
import importlib.util
import json
import os
import socket
import subprocess
import sys
import types
import urllib.request
from collections.abc import Iterable
from pathlib import Path

import pytest


MANUAL_ROOT = Path(__file__).resolve().parents[1]
CHECKOUT_ROOT = MANUAL_ROOT.parents[1]
INGEST_PATH = MANUAL_ROOT / "scripts/ingest.py"
SCRIPT_ROOT = INGEST_PATH.parent
MODULE_NAME = "nexus_math_ingest_under_test"
NETWORK_VARIABLES = (
    "OPENROUTER_API_KEY",
    "OPENROUTER_MODEL",
    "ANTHROPIC_API_KEY",
    "LOCAL_LLM_BASE_URL",
)
SUBPROCESS_LOADED_MARKER_ENV = "NEXUS_NETWORK_GUARD_LOADED_MARKER"
SUBPROCESS_ATTEMPT_MARKER_ENV = "NEXUS_NETWORK_GUARD_ATTEMPT_MARKER"


def _blocked_network(*args: object, **kwargs: object) -> None:
    raise AssertionError("network forbidden by Math ingest tests")


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


def _load_ingest(
    *,
    extra_import_path: Path | None = None,
    preloaded_external: types.ModuleType | None = None,
    preloaded_classification: types.ModuleType | None = None,
    stub_extraction_backends: bool = True,
) -> types.ModuleType:
    saved_path = list(sys.path)
    managed_exact = {"common", MODULE_NAME}
    if stub_extraction_backends:
        managed_exact.update({"fitz", "trafilatura"})
    managed_names = {
        name
        for name in sys.modules
        if name in managed_exact
        or name == "nexus_external"
        or name.startswith("nexus_external.")
    }
    saved_modules = {name: sys.modules[name] for name in managed_names}
    for name in managed_names:
        sys.modules.pop(name, None)
    if preloaded_external is not None:
        sys.modules["nexus_external"] = preloaded_external
    if preloaded_classification is not None:
        sys.modules["nexus_external.classification"] = preloaded_classification
    if stub_extraction_backends:
        sys.modules["fitz"] = types.ModuleType("fitz")
        sys.modules["trafilatura"] = types.ModuleType("trafilatura")
    if extra_import_path is not None:
        sys.path.insert(0, str(extra_import_path))
    sys.path.insert(0, str(SCRIPT_ROOT))

    try:
        spec = importlib.util.spec_from_file_location(MODULE_NAME, INGEST_PATH)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[MODULE_NAME] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = saved_path
        for name in list(sys.modules):
            if (
                name in managed_exact
                or name == "nexus_external"
                or name.startswith("nexus_external.")
            ):
                sys.modules.pop(name, None)
        sys.modules.update(saved_modules)


def _write_subprocess_network_guard(tmp_path: Path) -> tuple[Path, Path, Path]:
    guard_root = tmp_path / "network-guard"
    guard_root.mkdir(mode=0o700)
    loaded_marker = tmp_path / "sitecustomize.loaded"
    attempt_marker = tmp_path / "network.attempted"
    guard_root.joinpath("sitecustomize.py").write_text(
        """import os
import socket
import sys
import types
import urllib.request
from pathlib import Path

Path(os.environ["NEXUS_NETWORK_GUARD_LOADED_MARKER"]).write_text(
    "sitecustomize-loaded\\n", encoding="utf-8"
)

def blocked(*args, **kwargs):
    descriptor = os.open(
        os.environ["NEXUS_NETWORK_GUARD_ATTEMPT_MARKER"],
        os.O_WRONLY | os.O_CREAT | os.O_APPEND,
        0o600,
    )
    try:
        os.write(descriptor, b"network-attempted\\n")
    finally:
        os.close(descriptor)
    raise AssertionError("network forbidden by subprocess sitecustomize")

socket.socket.connect = blocked
socket.create_connection = blocked
urllib.request.urlopen = blocked
sys.modules["fitz"] = types.ModuleType("fitz")
sys.modules["trafilatura"] = types.ModuleType("trafilatura")
""",
        encoding="utf-8",
    )
    return guard_root, loaded_marker, attempt_marker


def _guarded_subprocess_env(
    guard_root: Path,
    loaded_marker: Path,
    attempt_marker: Path,
) -> dict[str, str]:
    environment = {
        key: value
        for key, value in os.environ.items()
        if key not in NETWORK_VARIABLES
    }
    existing_pythonpath = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = str(guard_root) + (
        os.pathsep + existing_pythonpath if existing_pythonpath else ""
    )
    environment[SUBPROCESS_LOADED_MARKER_ENV] = str(loaded_marker)
    environment[SUBPROCESS_ATTEMPT_MARKER_ENV] = str(attempt_marker)
    return environment


def _assert_checkout_package(module: types.ModuleType) -> None:
    checkout_root = Path(module.CHECKOUT_ROOT).resolve()
    assert checkout_root == CHECKOUT_ROOT.resolve()
    package_path = Path(module.nexus_external.__file__).resolve().parent
    assert package_path == (CHECKOUT_ROOT / "nexus_external").resolve()
    classification_path = Path(module.nexus_classification.__file__).resolve()
    assert classification_path == (
        CHECKOUT_ROOT / "nexus_external/classification.py"
    ).resolve()
    assert module.classify_chunk is module.nexus_classification.classify_chunk
    assert (checkout_root / ".git").exists()


def test_math_ingest_classify_delegates_to_shared_classifier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_ingest()
    fragment = "Exercice de classification transmis sans altération."
    expected = {
        "chunk_type": "exercice",
        "niveau": "1SPE",
        "theme": "SUITES",
        "capacites": ["calculer"],
        "difficulte": 2,
    }
    calls: list[tuple[str, object]] = []

    def fake_classify_chunk(
        chunk: str,
        *,
        environ: object,
        transport: object | None = None,
    ) -> dict[str, object]:
        assert transport is None
        calls.append((chunk, environ))
        return dict(expected)

    monkeypatch.setattr(module, "classify_chunk", fake_classify_chunk, raising=False)
    for variable in NETWORK_VARIABLES:
        monkeypatch.delenv(variable, raising=False)

    result = module.classify(fragment)

    assert calls == [(fragment, os.environ)]
    assert result == expected


def test_math_ingest_preserves_trusted_metadata_against_hostile_classifier(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_ingest()
    raw_root = tmp_path / "raw"
    corpus_root = tmp_path / "corpus"
    source = {
        "id": "SRC-0001",
        "usage_policy": "verbatim",
        "tier": "T1",
    }
    entry = {
        "file": "resource.pdf",
        "url": "https://example.invalid/original.pdf",
        "hash": "0123456789abcdef0123456789abcdef",
    }
    source_root = raw_root / source["id"]
    source_root.mkdir(parents=True)
    source_root.joinpath("manifest.json").write_text(
        json.dumps([entry]), encoding="utf-8"
    )
    trusted_chunk = "Contenu original suffisamment long pour former un chunk fiable."
    hostile = {
        "chunk_type": "cours",
        "niveau": "1SPE",
        "theme": "SUITES",
        "capacites": [],
        "difficulte": 1,
        "source_id": "SRC-9999",
        "doc_url": "https://attacker.invalid/overwrite",
        "doc_hash": "hostile-hash",
        "content_md": "contenu distant hostile qui ne doit pas remplacer la source",
        "usage_policy": "inspiration_reformulation",
        "tier": "T5",
    }
    captured: list[dict[str, object]] = []

    monkeypatch.setattr(module, "RAW_DIR", raw_root)
    monkeypatch.setattr(module, "CORPUS_DIR", corpus_root)
    monkeypatch.setattr(module, "extract_text", lambda path: trusted_chunk)
    monkeypatch.setattr(module, "latex_fallback", lambda text: text)
    monkeypatch.setattr(module, "split_chunks", lambda text: [trusted_chunk])
    monkeypatch.setattr(module, "classify", lambda chunk: dict(hostile))
    monkeypatch.setattr(module, "validate", lambda record, schema: None)
    monkeypatch.setattr(
        module,
        "write_json",
        lambda path, record: captured.append(dict(record)),
    )

    assert module.ingest_source(source) == 1
    assert len(captured) == 1
    record = captured[0]
    assert record["source_id"] == source["id"]
    assert record["doc_url"] == entry["url"]
    assert record["doc_hash"] == entry["hash"]
    assert record["content_md"] == trusted_chunk
    assert record["usage_policy"] == source["usage_policy"]
    assert record["tier"] == source["tier"]


def test_math_ingest_command_runs_without_source_key_or_network(
    tmp_path: Path,
) -> None:
    guard_root, loaded_marker, attempt_marker = _write_subprocess_network_guard(
        tmp_path
    )
    completed = subprocess.run(
        ["make", "ingest"],
        cwd=MANUAL_ROOT,
        env=_guarded_subprocess_env(guard_root, loaded_marker, attempt_marker),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert loaded_marker.read_text(encoding="utf-8") == "sitecustomize-loaded\n"
    assert loaded_marker.stat().st_size > 0
    assert not attempt_marker.exists()


def test_math_network_guard_mutation_is_effective() -> None:
    calls = (
        lambda: socket.socket().connect(("127.0.0.1", 9)),
        lambda: socket.create_connection(("127.0.0.1", 9)),
        lambda: urllib.request.urlopen("http://127.0.0.1:9"),
    )
    for call in calls:
        with pytest.raises(AssertionError):
            call()


def test_math_ingest_discovers_current_checkout_from_unrelated_cwd(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    module = _load_ingest()
    _assert_checkout_package(module)


def test_math_ingest_prioritizes_current_checkout_over_shadow_package(
    tmp_path: Path,
) -> None:
    shadow_root = tmp_path / "shadow"
    shadow_package = shadow_root / "nexus_external"
    shadow_package.mkdir(parents=True)
    shadow_package.joinpath("__init__.py").write_text(
        'ORIGIN = "shadow"\n', encoding="utf-8"
    )

    module = _load_ingest(extra_import_path=shadow_root)

    _assert_checkout_package(module)
    assert Path(module.nexus_external.__file__).resolve().parent != shadow_package


@pytest.mark.parametrize(
    "origin_kind",
    ("foreign", "missing", "invalid", "symlink", "forged"),
)
def test_math_ingest_reloads_preloaded_nexus_external(
    tmp_path: Path,
    origin_kind: str,
) -> None:
    poison_path = tmp_path / "poison/nexus_external/__init__.py"
    poison_path.parent.mkdir(parents=True)
    poison_path.write_text('ORIGIN = "poison"\n', encoding="utf-8")
    poisoned = types.ModuleType("nexus_external")

    if origin_kind == "foreign":
        poisoned.__file__ = str(poison_path)
    elif origin_kind == "invalid":
        poisoned.__file__ = object()
    elif origin_kind == "symlink":
        poison_path.unlink()
        poison_path.symlink_to(CHECKOUT_ROOT / "nexus_external/__init__.py")
        poisoned.__file__ = str(poison_path)
    elif origin_kind == "forged":
        poisoned.__file__ = str(CHECKOUT_ROOT / "nexus_external/__init__.py")
    poisoned.__path__ = [str(CHECKOUT_ROOT / "nexus_external")]

    module = _load_ingest(preloaded_external=poisoned)

    _assert_checkout_package(module)
    assert module.nexus_external is not poisoned


@pytest.mark.parametrize(
    "origin_kind",
    ("foreign", "missing", "invalid", "symlink", "forged"),
)
def test_math_ingest_reloads_preloaded_classification(
    tmp_path: Path,
    origin_kind: str,
) -> None:
    poison_path = tmp_path / "poison/nexus_external/classification.py"
    poison_path.parent.mkdir(parents=True)
    poison_path.write_text("# foreign classification sentinel\n", encoding="utf-8")
    poisoned = types.ModuleType("nexus_external.classification")

    if origin_kind == "foreign":
        poisoned.__file__ = str(poison_path)
    elif origin_kind == "invalid":
        poisoned.__file__ = object()
    elif origin_kind == "symlink":
        poison_path.unlink()
        poison_path.symlink_to(CHECKOUT_ROOT / "nexus_external/classification.py")
        poisoned.__file__ = str(poison_path)
    elif origin_kind == "forged":
        poisoned.__file__ = str(CHECKOUT_ROOT / "nexus_external/classification.py")
    calls = 0

    def poisoned_classify_chunk(*args: object, **kwargs: object) -> dict:
        nonlocal calls
        calls += 1
        raise AssertionError("foreign classifier called")

    poisoned.classify_chunk = poisoned_classify_chunk

    module = _load_ingest(preloaded_classification=poisoned)

    _assert_checkout_package(module)
    assert module.nexus_classification is not poisoned
    assert calls == 0


def test_math_ingest_reloads_legitimate_preloaded_canonical_namespace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.syspath_prepend(str(CHECKOUT_ROOT))
    canonical_external = importlib.import_module("nexus_external")
    canonical_classification = importlib.import_module(
        "nexus_external.classification"
    )

    module = _load_ingest(
        preloaded_external=canonical_external,
        preloaded_classification=canonical_classification,
    )

    _assert_checkout_package(module)
    assert module.nexus_external is not canonical_external
    assert module.nexus_classification is not canonical_classification


def test_math_no_source_command_does_not_import_extraction_backends(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_import = builtins.__import__

    def guarded_import(
        name: str,
        globals: object | None = None,
        locals: object | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> object:
        if name.split(".", 1)[0] in {"fitz", "trafilatura"}:
            raise ImportError(f"eager extraction backend import: {name}")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    module = _load_ingest(stub_extraction_backends=False)
    monkeypatch.setattr(module, "RAW_DIR", tmp_path / "raw-empty")

    assert module.ingest_source({"id": "SRC-4040"}) == 0
