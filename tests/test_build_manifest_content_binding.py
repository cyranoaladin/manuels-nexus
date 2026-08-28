"""L'identite du manifeste est adressee par le CONTENU, jamais par la branche.

Decision humaine du 2026-08-28 : BRANCH_NAME_BINDING = FORBIDDEN. La liaison de
provenance v1 couplait l'identite du manifeste au nom de branche observe ; a
sources strictement identiques, la seule creation d'une branche faisait echouer
seize tests racine. La v2 lie par source_digest, model_digest,
build_state_digest et ascendance Git.

Cas couverts, dans l'ordre de la decision :

A meme commit, branche A                 -> binding stable
B meme commit, branche B                 -> binding stable
C memes sources, deux worktrees          -> binding identique
D HEAD detachee, memes sources           -> binding stable et deterministe
E source de chapitre modifiee            -> binding change
F classe/style canonique modifie         -> binding change
G producteur modifie                     -> attestation du generateur changee
H regle de variante modifiee             -> binding change
I seul observed_branch differe           -> binding inchange
J seul un rapport derive change          -> binding inchange (hors source set)
K BUILD_MANIFEST remplace                -> pas d'auto-rebind
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

CHAPTER_SOURCE = (
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/"
    "10_C1_generalites_suites.tex"
)
CANONICAL_CLASS = "gabarits/common/nexus-manuel.cls"
VARIANT_RULES = "audit/SOURCE_ROLES.yaml"
DERIVED_REPORT = "audit/DEBT_BURNDOWN.md"


def _load_inventory_module(scripts_root: Path):
    spec = importlib.util.spec_from_file_location(
        f"inventory_content_binding_{scripts_root.parent.name}",
        scripts_root / "inventory_collection.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def inventory():
    return _load_inventory_module(ROOT / "scripts")


@pytest.fixture(scope="module")
def repo(tmp_path_factory: pytest.TempPathFactory) -> Path:
    destination = tmp_path_factory.mktemp("manifest-binding") / "repository"
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
    subprocess.run(
        ["git", "-C", str(repo), "checkout", "--quiet", "codex/t3-publish-readiness-current"],
        check=False,
    )


def _source_files(repo: Path) -> tuple[str, ...]:
    payload = json.loads((repo / INVENTORY).read_text(encoding="utf-8"))
    return tuple(payload["source_files"])


def _binding(inventory_module, repo: Path) -> str:
    """L'identite de contenu du manifeste, telle que le producteur la calcule."""

    return inventory_module._source_digest(repo, _source_files(repo))


def _append(repo: Path, relative: str, text: str) -> None:
    path = repo / relative
    path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")


# ---------------------------------------------------------------- A, B, D ---


def test_a_binding_is_stable_on_the_reference_branch(inventory, clean_repo: Path) -> None:
    published = json.loads((clean_repo / INVENTORY).read_text(encoding="utf-8"))

    assert _binding(inventory, clean_repo) == published["source_digest"]
    provenance = json.loads((clean_repo / MANIFEST).read_text(encoding="utf-8"))["provenance"]
    assert provenance["provenance_binding_version"] == 2
    assert provenance["branch_binding"] == "NON_BINDING"
    assert "branch" not in provenance


def test_b_binding_is_identical_on_another_branch(inventory, clean_repo: Path) -> None:
    before = _binding(inventory, clean_repo)
    subprocess.run(
        ["git", "-C", str(clean_repo), "checkout", "--quiet", "-b", "toute/autre/branche"],
        check=True,
    )

    assert _binding(inventory, clean_repo) == before


def test_d_detached_head_keeps_the_binding_and_stays_deterministic(
    inventory, clean_repo: Path
) -> None:
    before = _binding(inventory, clean_repo)
    subprocess.run(
        ["git", "-C", str(clean_repo), "switch", "--detach", "-q"], check=True
    )

    assert _binding(inventory, clean_repo) == before
    head, branch, dirty = inventory._observed_git_state(clean_repo)
    assert len(head) == 40
    assert branch == ""  # constatee vide, jamais refusee
    assert dirty is False


# ------------------------------------------------------------------- C -----


def test_c_two_worktrees_with_the_same_sources_share_the_binding(
    inventory, clean_repo: Path, tmp_path: Path
) -> None:
    second = tmp_path / "second-worktree"
    subprocess.run(
        ["git", "clone", "-q", "--no-hardlinks", str(clean_repo), str(second)],
        check=True,
        timeout=600,
    )

    assert str(second) != str(clean_repo)
    assert _binding(inventory, second) == _binding(inventory, clean_repo)


# ------------------------------------------------------------- E, F, G, H ---


def test_e_chapter_source_change_changes_the_binding(inventory, clean_repo: Path) -> None:
    before = _binding(inventory, clean_repo)
    _append(clean_repo, CHAPTER_SOURCE, "\n% derive de contenu\n")

    assert _binding(inventory, clean_repo) != before


def test_f_canonical_class_change_changes_the_binding(inventory, clean_repo: Path) -> None:
    assert CANONICAL_CLASS in _source_files(clean_repo)
    before = _binding(inventory, clean_repo)
    _append(clean_repo, CANONICAL_CLASS, "\n% derive de classe\n")

    assert _binding(inventory, clean_repo) != before


def test_g_producer_change_changes_the_generator_attestation(
    inventory, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Un producteur n'est pas une source : il est lie par son attestation.

    source_digest ne couvre que les sources editoriales ; c'est l'attestation
    du generateur qui lie les producteurs. Editer un producteur doit donc
    changer cette attestation, et c'est ce que --validate-model controle.
    """

    scripts = tmp_path / "scripts"
    shutil.copytree(ROOT / "scripts", scripts)
    monkeypatch.setattr(inventory, "_SCRIPTS_ROOT", scripts)
    before = inventory._generator_sha256()
    producer = scripts / "build_manifest.py"
    producer.write_text(
        producer.read_text(encoding="utf-8") + "\n# derive\n", encoding="utf-8"
    )

    assert "build_manifest.py" in inventory.GENERATOR_COMPONENT_PATHS
    assert "scripts/inventory_collection.py" not in _source_files(ROOT)
    assert inventory._generator_sha256() != before


def test_h_variant_rule_change_changes_the_binding(inventory, clean_repo: Path) -> None:
    assert VARIANT_RULES in _source_files(clean_repo)
    before = _binding(inventory, clean_repo)
    _append(clean_repo, VARIANT_RULES, "\n# derive de regle de variante\n")

    assert _binding(inventory, clean_repo) != before


# ---------------------------------------------------------------- I, J, K ---


def test_i_only_the_observed_branch_differs_leaves_the_binding_untouched(
    inventory, clean_repo: Path
) -> None:
    before = _binding(inventory, clean_repo)
    manifest = clean_repo / MANIFEST
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["provenance"]["observed_branch"] = "un/nom/entierement/different"
    manifest.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    assert _binding(inventory, clean_repo) == before


def test_j_a_derived_report_change_leaves_the_binding_untouched(
    inventory, clean_repo: Path
) -> None:
    assert DERIVED_REPORT not in _source_files(clean_repo)
    before = _binding(inventory, clean_repo)
    _append(clean_repo, DERIVED_REPORT, "\n<!-- rapport derive -->\n")

    assert _binding(inventory, clean_repo) == before


def test_k_replacing_the_manifest_never_rebinds_it(inventory, clean_repo: Path) -> None:
    """Pas d'auto-reference : le manifeste n'entre jamais dans son propre digest."""

    assert MANIFEST not in _source_files(clean_repo)
    before = _binding(inventory, clean_repo)
    (clean_repo / MANIFEST).write_text("{}\n", encoding="utf-8")

    assert _binding(inventory, clean_repo) == before


# ------------------------------------------------- contrats de schema v1/v2 ---


def _contract_payload(provenance: dict, *, schema_version: int, schema_ref: str) -> dict:
    return {
        "artifact_type": "build_manifest",
        "build_state_digest": "sha256:" + "4" * 64,
        "builds": [],
        "generated_by": "build_manifest.py",
        "model_digest": "sha256:" + "3" * 64,
        "provenance": provenance,
        "schema_ref": schema_ref,
        "schema_version": schema_version,
        "source_digest": "sha256:" + "5" * 64,
    }


V1_REF = "audit/schemas/v1/build-manifest.schema.json"
V2_REF = "audit/schemas/v1/build-manifest-provenance-v2.schema.json"


def test_the_v2_contract_accepts_a_non_binding_branch_and_a_detached_head() -> None:
    import jsonschema

    schema = json.loads((ROOT / V2_REF).read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for observed_branch in ("codex/une-branche", None):
        validator.validate(
            _contract_payload(
                {
                    "branch_binding": "NON_BINDING",
                    "dirty": False,
                    "head_sha": "2" * 40,
                    "observed_branch": observed_branch,
                    "provenance_binding_version": 2,
                },
                schema_version=2,
                schema_ref=V2_REF,
            )
        )


def test_the_v2_contract_refuses_the_deprecated_branch_coupled_provenance() -> None:
    import jsonschema

    schema = json.loads((ROOT / V2_REF).read_text(encoding="utf-8"))
    payload = _contract_payload(
        {"branch": "codex/une-branche", "dirty": False, "head_sha": "2" * 40},
        schema_version=2,
        schema_ref=V2_REF,
    )

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)


def test_the_v1_contract_is_kept_only_as_deprecated(inventory) -> None:
    schema = json.loads((ROOT / V1_REF).read_text(encoding="utf-8"))

    assert "DEPRECIE" in schema["$defs"]["provenance"]["description"]
    assert inventory.SCHEMA_REGISTRY["build_manifest"][1] == V1_REF
    assert inventory.SCHEMA_REGISTRY["build_manifest"][2] == V2_REF
    assert inventory._PROVENANCE_BINDING_VERSION == 2


def test_no_runtime_producer_still_writes_the_deprecated_provenance() -> None:
    producer = (ROOT / "scripts" / "build_manifest.py").read_text(encoding="utf-8")

    assert '"branch": branch' not in producer
    assert '"observed_branch": branch or None' in producer
    assert '"branch_binding": "NON_BINDING"' in producer
