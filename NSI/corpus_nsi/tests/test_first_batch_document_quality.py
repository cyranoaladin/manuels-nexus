from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_first_batch_document_quality as first_batch


def write_doc(path: Path, title: str, extra: str = "") -> None:
    path.write_text(
        f"""---
title: "{title}"
level: "premiere"
sequence_id: "P00"
document_type: "cours"
status: "needs_review"
version: "0.1.0"
source: "test"
theme: "test"
notion: "test"
objectifs: ["tester"]
---

# {title}

## Objectifs
Comprendre la notion et vérifier une production.

## Capacités officielles
P-LANG-01 est travaillée explicitement.

## Exemple
Exemple guidé avec une donnée, une réponse et une justification.

## Exercices
Exercice 1. Répondre et justifier.

## Corrigé
Réponse attendue avec justification.

## Erreurs fréquentes
Confondre la donnée et son interprétation.

## Remédiation
Reprendre la méthode sur un cas plus court.

## Différenciation
Socle, standard et approfondissement.

{extra}
""",
        encoding="utf-8",
    )


class FirstBatchQualityTest(unittest.TestCase):
    def test_missing_required_document_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            result = first_batch.analyze_first_batch(root)
            self.assertTrue(any("absent" in error for error in result.errors))

    def test_short_minimal_batch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for prefix in first_batch.FIRST_BATCH_PREFIXES:
                directory = root / prefix
                directory.mkdir(parents=True)
                for kind in first_batch.REQUIRED_KINDS:
                    write_doc(directory / f"{prefix}_{kind}_test.md", f"{prefix} {kind}", "Capacité officielle : test.")
            result = first_batch.analyze_first_batch(root)
            self.assertTrue(any("profondeur insuffisante" in error for error in result.errors))

    def test_unknown_program_capacity_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            directory = root / "P00"
            directory.mkdir(parents=True)
            path = directory / "P00_cours_test.md"
            long_body = "\n".join(f"Ligne utile {i}" for i in range(200))
            write_doc(path, "P00 cours", f"\nCapacité officielle : P-UNKNOWN-99\n{long_body}")
            errors = first_batch.analyze_file(path, "P00", "cours", {"P-LANG-01"})
            self.assertTrue(any("capacité inconnue" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
