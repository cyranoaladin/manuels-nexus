#!/usr/bin/env python3
"""Print the controlled RAG indexing plan for the NSI corpus."""

from __future__ import annotations

from scripts._qa_common import ROOT


def main() -> int:
    print("RAG_INDEX_PLAN")
    print("collection=nsi_corpus")
    print("source_roots=03_progressions/supports,03_progressions/fiches_cours")
    print("excluded=AUDIT,dist,.git,Documents_DRIVE,rendus_eleves,NotesEleves.csv,Fichier_Eleves.csv")
    print("dry_run_command=python scripts/ingest_nsi_corpus.py --dry-run")
    print("metadata_check=python scripts/check_rag_index_metadata.py")
    print(f"config={(ROOT / 'rag_config.example.yml').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
