"""Valide les en-têtes % META de tous les .tex contre les schémas JSON."""
import json
import re
from pathlib import Path

import pytest
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
EX_SCHEMA = json.loads((ROOT / "schemas" / "exercice.schema.json").read_text(encoding="utf-8"))
META = re.compile(r"% META: (\{.*\})")

tex_files = sorted(
    f for f in (ROOT / "chapitres").rglob("*.tex")
    if "_harvest" not in f.parts and not f.name.endswith(".candidate.tex")
)


@pytest.mark.parametrize("tex", tex_files, ids=lambda p: str(p.relative_to(ROOT)))
def test_meta_valid(tex):
    m = META.search(tex.read_text(encoding="utf-8"))
    assert m, f"{tex} : en-tête % META manquant (règle R4)"
    meta = json.loads(m.group(1))
    if meta.get("type_objet") == "exercice":
        validate(meta, EX_SCHEMA)


def test_contrats_schema():
    import yaml
    from jsonschema import validate as v
    schema = json.loads((ROOT / "schemas" / "contrat_chapitre.schema.json").read_text(encoding="utf-8"))
    for c in (ROOT / "chapitres").glob("*/contrat.yaml"):
        v(yaml.safe_load(c.read_text(encoding="utf-8")), schema)
