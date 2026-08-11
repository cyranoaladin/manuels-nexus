#!/usr/bin/env python3
"""Write a conservative RAG coherence report from local configuration only."""

from __future__ import annotations

from scripts._qa_common import ROOT


REPORT = ROOT / "rag_coherence_report.md"


def main() -> int:
    REPORT.write_text(
        "\n".join(
            [
                "# Rapport de cohérence RAG",
                "",
                "Statut : rapport local conservateur.",
                "",
                "- Collection interne de jugement : `nsi_corpus`.",
                "- `rag_education` : inspiration externe, pas preuve de couverture interne.",
                "- Smoke réel 2026-06-29 : `/health` public répond `HTTP 200`, `/search` sans token répond `HTTP 401`, mais `/search` authentifié time out sur `nsi_corpus` comme sur `rag_education`.",
                "- Ingestion réelle : bloquée sans plan, dry-run, validation métadonnées et revue humaine.",
                "",
                "Aucune validation pédagogique n'est produite par ce rapport.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"rag_coherence_report: wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
