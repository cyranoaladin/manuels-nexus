"""Un producteur doit etre lie cryptographiquement, pas seulement declare.

audit/BUILD_PRODUCERS.yaml nomme les assembleurs mais ne porte aucun condense
de leur code. La question posee est donc legitime : editer un producteur
change-t-il une identite gouvernee ? Ces tests le prouvent par mutation, dans
les deux sens, pour les deux familles de producteurs :

* les assembleurs de manuel (Math et NSI) appartiennent au jeu de sources et
  sont donc lies par source_digest ;
* l'enregistreur et le generateur d'inventaire n'appartiennent pas aux sources
  mais sont lies par l'attestation du generateur.

Si l'un des deux mecanismes ne bougeait pas, ce serait un angle mort P0 de
provenance.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = "audit/INVENTAIRE_COLLECTION.json"
MANIFEST = "audit/BUILD_MANIFEST.json"

MATH_PRODUCER = "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
NSI_PRODUCER = "NSI/scripts/assemble_manuel.py"
NSI_SHARED_HELPER = "NSI/scripts/assemble.py"
RECORDER = "scripts/build_manifest.py"


@pytest.fixture(scope="module")
def inventory():
    spec = importlib.util.spec_from_file_location(
        "inventory_producer_binding", ROOT / "scripts" / "inventory_collection.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def repo(tmp_path_factory: pytest.TempPathFactory) -> Path:
    destination = tmp_path_factory.mktemp("producer-binding") / "repository"
    subprocess.run(
        ["git", "clone", "-q", "--no-hardlinks", str(ROOT), str(destination)],
        check=True,
        timeout=600,
    )
    return destination


@pytest.fixture()
def clean_repo(repo: Path):
    yield repo
    subprocess.run(["git", "-C", str(repo), "checkout", "--quiet", "--", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "clean", "-qfd"], check=True)


def _source_files(repo: Path) -> tuple[str, ...]:
    return tuple(json.loads((repo / INVENTORY).read_text(encoding="utf-8"))["source_files"])


def _content_identity(inventory_module, repo: Path) -> str:
    return inventory_module._source_digest(repo, _source_files(repo))


def _mutate(repo: Path, relative: str) -> None:
    path = repo / relative
    path.write_text(path.read_text(encoding="utf-8") + "\n# mutation\n", encoding="utf-8")


def _restore(repo: Path, relative: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), "checkout", "--quiet", "--", relative], check=True
    )


@pytest.mark.parametrize(
    "producer", [MATH_PRODUCER, NSI_PRODUCER, NSI_SHARED_HELPER]
)
def test_editing_a_manual_producer_changes_the_governed_identity(
    inventory, clean_repo: Path, producer: str
) -> None:
    """A puis B, C/D, F puis G : mutation et restauration du producteur."""

    assert producer in _source_files(clean_repo), (
        f"{producer} hors du jeu de sources : angle mort de provenance"
    )

    before = _content_identity(inventory, clean_repo)  # A
    _mutate(clean_repo, producer)  # B
    mutated = _content_identity(inventory, clean_repo)  # C/D

    assert mutated != before

    _restore(clean_repo, producer)  # F

    assert _content_identity(inventory, clean_repo) == before  # G


def test_editing_a_manual_producer_invalidates_an_earlier_build_proof(
    inventory, clean_repo: Path
) -> None:
    """E : la preuve de build anterieure devient refusee, pas seulement suspecte."""

    recorded = json.loads((clean_repo / MANIFEST).read_text(encoding="utf-8"))
    _mutate(clean_repo, MATH_PRODUCER)
    recomputed = _content_identity(inventory, clean_repo)

    assert recorded["source_digest"] != recomputed

    with pytest.raises(inventory.InventoryError, match="source_digest"):
        inventory._load_observed_build_manifest(
            clean_repo,
            source_digest=recomputed,
            model_digest=recorded["model_digest"],
            declared_assemblies=[],
            pdfinfo_counter=lambda _path: (7, None),
            python_counter=lambda _path: (None, "unused"),
        )


def test_editing_the_recorder_changes_the_generator_attestation(
    inventory, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """L'enregistreur n'est pas une source : il est lie par l'attestation."""

    scripts = tmp_path / "scripts"
    shutil.copytree(ROOT / "scripts", scripts)
    monkeypatch.setattr(inventory, "_SCRIPTS_ROOT", scripts)
    before = inventory._generator_sha256()

    assert Path(RECORDER).name in inventory.GENERATOR_COMPONENT_PATHS
    assert RECORDER not in _source_files(ROOT)

    target = scripts / Path(RECORDER).name
    target.write_text(target.read_text(encoding="utf-8") + "\n# mutation\n", encoding="utf-8")
    mutated = inventory._generator_sha256()

    assert mutated != before

    shutil.copyfile(ROOT / RECORDER, target)

    assert inventory._generator_sha256() == before


def test_every_declared_producer_is_covered_by_one_of_the_two_mechanisms(
    inventory,
) -> None:
    """Aucun producteur declare ne doit echapper aux deux liaisons."""

    import yaml

    registry = yaml.safe_load(
        (ROOT / "audit" / "BUILD_PRODUCERS.yaml").read_text(encoding="utf-8")
    )
    sources = set(_source_files(ROOT))
    generator = {f"scripts/{name}" for name in inventory.GENERATOR_COMPONENT_PATHS}

    unbound: list[str] = []
    for producer in registry["producers"]:
        for role in ("assembler", "recorder"):
            path = producer[role]
            if path not in sources and path not in generator:
                unbound.append(f"{producer['producer_id']}:{role}:{path}")

    assert not unbound, f"producteurs non lies cryptographiquement : {unbound}"
