"""Disposition des clones : la categorie doit venir des faits, pas d'un hash.

La contamination historique est reproduite ici comme fixture : le commit
533d1919 a rempli 986 fichiers vides en recopiant quelques corps canoniques,
avec un cycle d'exercices de periode 5 et un cycle de corriges de periode 6.
C'est ce decalage qui a produit les 180 derives.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
LEDGER_JSON = ROOT / "audit/CLONE_DISPOSITION_LEDGER.json"

CANONICAL_BODIES = 5
CORRECTION_CYCLE = 6


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def ledger_module():
    return _load("clone_ledger", "scripts/build_clone_disposition_ledger.py")


@pytest.fixture(scope="module")
def ledger():
    assert LEDGER_JSON.is_file(), "le registre doit exister"
    return json.loads(LEDGER_JSON.read_text(encoding="utf-8"))


def test_every_group_has_exactly_one_disposition(ledger):
    dispositions = {
        "EXPECTED_STUDENT_TEACHER_MIRROR",
        "INTENTIONAL_REUSE",
        "ACCIDENTAL_RENDER_DUPLICATION",
        "SOURCE_CLONE_WITH_DISTINCT_IDS",
        "ASSEMBLY_DUPLICATION",
    }
    for group in ledger["groups"]:
        assert group["disposition"] in dispositions, group["digest"]
    counted = sum(
        ledger["summary"][name] for name in dispositions
    )
    assert counted == ledger["summary"]["CLONE_GROUPS_TOTAL"]


def test_student_teacher_presence_is_never_counted_as_a_clone(ledger):
    """La presence normale eleve/professeur ne doit jamais gonfler la dette."""

    mirrors = [
        g for g in ledger["groups"]
        if g["disposition"] == "EXPECTED_STUDENT_TEACHER_MIRROR"
    ]
    excess = ledger["summary"]["EXCESS_BY_DISPOSITION"]
    assert "EXPECTED_STUDENT_TEACHER_MIRROR" not in excess or not mirrors


def test_true_product_clones_exclude_mirrors_and_declared_reuse(ledger):
    excess = ledger["summary"]["EXCESS_BY_DISPOSITION"]
    expected = (
        excess.get("SOURCE_CLONE_WITH_DISTINCT_IDS", 0)
        + excess.get("ACCIDENTAL_RENDER_DUPLICATION", 0)
        + excess.get("ASSEMBLY_DUPLICATION", 0)
    )
    assert ledger["summary"]["TRUE_PRODUCT_CLONES_OPEN"] == expected


def _write(root: Path, relative: str, meta_id: str, body: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    meta = json.dumps({"id": meta_id, "chapitre": "CH", "type_objet": "exercice"})
    path.write_text(f"% META: {meta}\n{body}\n", encoding="utf-8")


def _fixture_root(tmp_path: Path, *, copies: int) -> Path:
    """Rejoue la contamination : un corps canonique recopie sous N identites."""

    root = tmp_path / "root"
    body = "\\begin{exercice}{CH-EX-001}{1}{10}\n" + ("Enonce authentique. " * 12) + "\n\\end{exercice}"
    for index in range(1, copies + 1):
        _write(root, f"chapitres/CH/exercices/CH-EX-{index:03d}.tex", f"CH-EX-{index:03d}", body)
    inventory = {
        "canonical_targets": [
            {
                "manual_id": "1NSI",
                "variant": "eleve",
                "master": "build/master.tex",
                "pdf": "build/master.pdf",
            }
        ]
    }
    (root / "audit").mkdir(parents=True, exist_ok=True)
    (root / "audit/CANONICAL_RELEASE_INVENTORY.json").write_text(
        json.dumps(inventory), encoding="utf-8"
    )
    master = root / "build/master.tex"
    master.parent.mkdir(parents=True, exist_ok=True)
    master.write_text(
        "".join(
            f"\\input{{chapitres/CH/exercices/CH-EX-{i:03d}.tex}}\n"
            for i in range(1, copies + 1)
        ),
        encoding="utf-8",
    )
    return root


def test_fixture_synthetic_filler_is_classified_as_a_source_clone(
    ledger_module, tmp_path, monkeypatch
):
    root = _fixture_root(tmp_path, copies=10)
    monkeypatch.setitem(ledger_module.SOURCE_ROOTS, "1NSI", ".")
    report = ledger_module.build(root, with_history=False)
    assert report["summary"]["CLONE_GROUPS_TOTAL"] == 1
    group = report["groups"][0]
    assert group["disposition"] == "SOURCE_CLONE_WITH_DISTINCT_IDS"
    assert group["excess_objects"] == 9
    assert report["summary"]["TRUE_PRODUCT_CLONES_OPEN"] == 9


def test_fixture_a_single_authentic_object_produces_no_group(
    ledger_module, tmp_path, monkeypatch
):
    root = _fixture_root(tmp_path, copies=1)
    monkeypatch.setitem(ledger_module.SOURCE_ROOTS, "1NSI", ".")
    report = ledger_module.build(root, with_history=False)
    assert report["summary"]["CLONE_GROUPS_TOTAL"] == 0
    assert report["summary"]["TRUE_PRODUCT_CLONES_OPEN"] == 0


def test_fixture_reproduces_the_historical_off_by_one_drift():
    """Cycle d'exercices de periode 5 contre cycle de corriges de periode 6.

    C'est la mecanique exacte du remplissage de 533d1919 : a partir du 6e slot,
    chaque corrige repond a un autre enonce que celui imprime au-dessus.
    """

    slots = range(1, 51)
    exercise_label = {n: f"EX-{((n - 1) % CANONICAL_BODIES) + 1:03d}" for n in slots}
    correction_target = {
        n: f"EX-{((n - 1) % CORRECTION_CYCLE) + 1:03d}" for n in slots
    }
    drifted = [n for n in slots if exercise_label[n] != correction_target[n]]
    assert len(drifted) == 40
    assert min(drifted) == 6, "les cinq premiers slots restent alignes"


def test_committed_ledger_matches_the_producer(ledger_module, ledger):
    recomputed = ledger_module.build(ROOT, with_history=False)
    assert recomputed["summary"] == ledger["summary"]


def test_no_true_product_clone_remains_open(ledger):
    """Gate produit : il doit rester rouge tant que des clones sont ouverts.

    Ne pas le neutraliser en `xfail` : un gate desarme ne signale plus rien.
    Il repassera au vert par la recuperation du contenu canonique, pas par un
    assouplissement de l'assertion.
    """

    assert ledger["summary"]["TRUE_PRODUCT_CLONES_OPEN"] == 0
