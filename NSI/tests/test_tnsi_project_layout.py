"""Régression de composition pour l'unité de projet Terminale NSI."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


NSI_ROOT = Path(__file__).resolve().parents[1]
PROJECT = NSI_ROOT / "chapitres/TNSI-PROJET/projet/TNSI-PROJET-ANNUEL.tex"
BOX_DIAGNOSTIC = re.compile(r"(?:Over|Under)full \\hbox")


def test_tnsi_project_tables_render_without_horizontal_box_diagnostics(tmp_path):
    source = PROJECT.read_text(encoding="utf-8")
    forbidden_workarounds = {
        r"\sloppy",
        r"\emergencystretch",
        r"\hbadness",
        r"\hfuzz",
        r"\resizebox",
        r"\scalebox",
    }
    assert sorted(token for token in forbidden_workarounds if token in source) == []

    master = tmp_path / "tnsi-project-layout.tex"
    master.write_text(
        r"""\documentclass{gabarits/nexus-manuel-v5}
\usepackage{gabarits/nexus-charte-v6}
\nxVSuppressTabtrue
\nxVersionProfesseurfalse
\RenewDocumentEnvironment{corrige}{m +b}{}{}
\matiere{NSI}\niveau{Terminale}
\title{Test de composition du projet TNSI}
\begin{document}
\chapter{Démarche de projet}
\input{chapitres/TNSI-PROJET/projet/TNSI-PROJET-ANNUEL.tex}
\end{document}
""",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment.update(
        {
            "TEXINPUTS": f"./gabarits/:{environment.get('TEXINPUTS', '')}",
            "SOURCE_DATE_EPOCH": "1785962466",
            "FORCE_SOURCE_DATE": "1",
            "TZ": "UTC",
        }
    )
    completed = subprocess.run(
        [
            "lualatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={tmp_path}",
            str(master),
        ],
        cwd=NSI_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout[-4000:]

    log = (tmp_path / "tnsi-project-layout.log").read_text(
        encoding="utf-8", errors="replace"
    )
    diagnostics = BOX_DIAGNOSTIC.findall(log)
    assert diagnostics == []
