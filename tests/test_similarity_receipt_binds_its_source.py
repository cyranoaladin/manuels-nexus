"""Un reçu de similarité doit dire de quelle source il parle.

Le gate de similarité écrivait un reçu sans `source_path` ni `source_sha256`.
Ces reçus -- 1 425 sur les 4 855 du dépôt -- ne peuvent donc être rattachés à
aucun contenu : ils forment l'essentiel du compteur VALIDATION_STALE, non
parce qu'une source aurait changé, mais parce qu'aucune source n'est nommée.

Une preuve qui ne nomme pas ce qu'elle a examiné ne périme jamais, et c'est
précisément le problème : elle survit indéfiniment à la réécriture de l'objet.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

MANUELS = {
    "maths": Path("Mathematiques/manuel-maths/scripts/similarity_check.py"),
    "nsi": Path("NSI/scripts/similarity_check.py"),
}
ROOT = Path(__file__).resolve().parents[1]


def load(name: str, manual_root: Path):
    """Charge le gate avec CORPUS_DIR/ROOT pointés sur une racine de test."""
    path = ROOT / MANUELS[name]
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(f"similarity_{name}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = manual_root
    module.CORPUS_DIR = manual_root / "corpus_vide"
    (manual_root / "corpus_vide").mkdir(exist_ok=True)
    return module


@pytest.fixture
def manual(tmp_path: Path) -> tuple[Path, Path, Path]:
    chap = tmp_path / "chapitres" / "1SPE-SECOND-DEGRE"
    (chap / "cours").mkdir(parents=True)
    (chap / "validations").mkdir()
    tex = chap / "cours" / "00_ouverture.tex"
    # Assez long pour former des 8-grammes : le gate maths sort sans ecrire de
    # recu si l'objet n'en produit aucun.
    tex.write_text(
        "% META: {\"id\": \"x\"}\n"
        "Un polynome du second degre s ecrit sous forme developpee, canonique ou "
        "factorisee, et son discriminant decide du nombre de racines reelles.\n",
        encoding="utf-8")
    return tmp_path, chap, tex


@pytest.mark.parametrize("name", ["maths", "nsi"])
def test_the_receipt_names_the_source_it_examined(name, manual, monkeypatch):
    root, chap, tex = manual
    module = load(name, root)
    monkeypatch.setattr(module, "iter_source_chunks", lambda theme: iter(()), raising=False)
    monkeypatch.setattr(module, "iter_chunks", lambda theme: iter(()), raising=False)
    (getattr(module, "check_object", None) or module.check)(tex, chap)

    receipt = json.loads((chap / "validations" / "00_ouverture.similarity.json").read_text(encoding="utf-8"))
    assert receipt["source_path"] == "chapitres/1SPE-SECOND-DEGRE/cours/00_ouverture.tex"
    expected = "sha256:" + hashlib.sha256(tex.read_bytes()).hexdigest()
    assert receipt["source_sha256"] == expected


@pytest.mark.parametrize("name", ["maths", "nsi"])
def test_rewriting_the_object_makes_the_receipt_stale(name, manual, monkeypatch):
    """Le but du rattachement : qu'une réécriture invalide la preuve."""
    root, chap, tex = manual
    module = load(name, root)
    monkeypatch.setattr(module, "iter_source_chunks", lambda theme: iter(()), raising=False)
    monkeypatch.setattr(module, "iter_chunks", lambda theme: iter(()), raising=False)
    (getattr(module, "check_object", None) or module.check)(tex, chap)
    receipt = json.loads((chap / "validations" / "00_ouverture.similarity.json").read_text(encoding="utf-8"))

    tex.write_text(
        "% META: {\"id\": \"x\"}\n"
        "Un polynome du second degre s ecrit sous forme developpee, canonique ou "
        "factorisee, et son discriminant decide du nombre de racines REECRIT.\n",
        encoding="utf-8")
    current = "sha256:" + hashlib.sha256(tex.read_bytes()).hexdigest()
    assert receipt["source_sha256"] != current
