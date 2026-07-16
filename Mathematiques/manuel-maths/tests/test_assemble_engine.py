import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import assemble  # noqa: E402


def test_assemble_uses_lualatex_for_the_nexus_v3_class(tmp_path, monkeypatch):
    (tmp_path / "gabarits").mkdir()
    (tmp_path / "gabarits" / "chapitre_master.tex").write_text(
        "%%OPENING%%\n%%CONTENT%%\n%%CHAP%%", encoding="utf-8"
    )
    source = tmp_path / "chapitres" / "CHAP" / "cours" / "objet.tex"
    source.parent.mkdir(parents=True)
    source.write_text("Objet", encoding="utf-8")
    (source.parents[1] / "contrat.yaml").write_text(
        "titre: Chapitre test\ncapacites: []\n", encoding="utf-8"
    )
    calls = []

    def successful_runner(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(assemble, "ROOT", tmp_path)
    monkeypatch.setattr(assemble, "collect", lambda *_: [source])
    monkeypatch.setattr(assemble.subprocess, "run", successful_runner)
    monkeypatch.setattr(assemble, "verify_pdf", lambda *_: 0)

    assert assemble.main("CHAP", "complet") == 0
    assert calls[0][0][0] == "lualatex"
