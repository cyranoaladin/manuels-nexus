"""Un tag annoté et le commit qu'il référence ne portent pas le même SHA.

`RELEASE_TAG_SHA` confondait quatre choses : le nom du tag, l'objet tag,
le commit référencé et l'arbre publié. On ne pouvait pas dire lequel était
cité. Et si plusieurs `release/*` désignaient le même candidat, prendre le
premier revenait à choisir la release au hasard de l'ordre alphabétique.
"""
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evidence_freshness.py"


def load():
    spec = importlib.util.spec_from_file_location("evidence_freshness_tag", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def depot(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    for cle, valeur in (("user.email", "t@example.invalid"), ("user.name", "t")):
        subprocess.run(["git", "config", cle, valeur], cwd=tmp_path, check=True)
    (tmp_path / "manuel.tex").write_text("Un manuel.\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "socle"], cwd=tmp_path, check=True)
    return tmp_path


def rev(depot: Path, expression: str) -> str:
    return subprocess.run(["git", "rev-parse", expression], cwd=depot,
                          capture_output=True, text=True, check=True).stdout.strip()


def test_without_a_release_tag_every_field_is_none(depot: Path) -> None:
    identite = load().release_tag_identity(depot)
    assert set(identite) == {
        "RELEASE_TAG_NAME", "RELEASE_TAG_OBJECT_SHA",
        "RELEASE_COMMIT_SHA", "RELEASE_TREE_SHA",
    }
    assert all(valeur is None for valeur in identite.values())


def test_an_annotated_tag_object_is_not_its_commit(depot: Path) -> None:
    """Le cas qui rendait `RELEASE_TAG_SHA` ambigu."""
    subprocess.run(["git", "tag", "-a", "release/v1", "-m", "release 1"],
                   cwd=depot, check=True)
    identite = load().release_tag_identity(depot)
    assert identite["RELEASE_TAG_NAME"] == "release/v1"
    assert identite["RELEASE_COMMIT_SHA"] == rev(depot, "HEAD")
    assert identite["RELEASE_TAG_OBJECT_SHA"] != identite["RELEASE_COMMIT_SHA"]
    assert identite["RELEASE_TREE_SHA"] == rev(depot, "HEAD^{tree}")


def test_a_lightweight_tag_declares_no_tag_object(depot: Path) -> None:
    subprocess.run(["git", "tag", "release/leger"], cwd=depot, check=True)
    identite = load().release_tag_identity(depot)
    assert identite["RELEASE_TAG_NAME"] == "release/leger"
    assert identite["RELEASE_TAG_OBJECT_SHA"] is None
    assert identite["RELEASE_COMMIT_SHA"] == rev(depot, "HEAD")


def test_two_release_tags_fail_instead_of_choosing_silently(depot: Path) -> None:
    subprocess.run(["git", "tag", "-a", "release/v1", "-m", "a"], cwd=depot, check=True)
    subprocess.run(["git", "tag", "-a", "release/v2", "-m", "b"], cwd=depot, check=True)
    module = load()
    with pytest.raises(module.AmbiguousReleaseTag, match="AMBIGUOUS_RELEASE_TAG"):
        module.release_tag_identity(depot)


def test_provenance_reports_the_ambiguity_instead_of_hiding_it(depot: Path) -> None:
    subprocess.run(["git", "tag", "-a", "release/v1", "-m", "a"], cwd=depot, check=True)
    subprocess.run(["git", "tag", "-a", "release/v2", "-m", "b"], cwd=depot, check=True)
    identite = load().provenance(root=depot)
    assert "AMBIGUOUS_RELEASE_TAG" in identite["RELEASE_TAG_IDENTITY_ERROR"]


def test_the_report_provenance_no_longer_claims_a_commit_that_does_not_exist() -> None:
    """Le rapport se génère AVANT le commit qui le contiendra."""
    identite = load().provenance()
    assert "REPORT_COMMIT_SHA" not in identite, "nom trompeur restauré"
    assert len(identite["REPORT_GENERATED_FROM_SHA"]) == 40
    assert set(identite) >= {
        "AUDITED_SOURCE_SHA", "REPORT_GENERATED_FROM_SHA",
        "CONTENT_SEMANTIC_DIGEST", "RENDER_SOURCE_DIGEST", "TOOLCHAIN_DIGEST",
    }
