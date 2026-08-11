from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_tp_text_asset_alignment as tp_alignment


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TpTextAssetAlignmentTest(unittest.TestCase):
    def test_p04_tp_mentions_new_functions_but_assets_keep_old_scenario(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            base = root / "03_progressions" / "supports" / "premiere" / "P04"
            write(base / "P04_tp_types_construits.md", "TP : coder `milieu`, `stations_chaudes`, `moyenne_notes`.")
            code = base / "code"
            write(code / "P04_starter_types_construits.py", "def resume_mesures(mesures):\n    return {}\n")
            write(code / "P04_corrige_professeur_types_construits.py", "def resume_mesures(mesures):\n    return {}\n")
            write(code / "P04_tests_attendus_types_construits.py", "from P04_starter_types_construits import resume_mesures\n")

            result = tp_alignment.analyze_tp_text_asset_alignment(root, prefixes=["P04"])

            self.assertTrue(any("milieu" in error for error in result.errors))
            self.assertTrue(any("ancien scénario" in error for error in result.errors))

    def test_p05_assets_must_cover_csv_functions_and_dictreader(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            base = root / "03_progressions" / "supports" / "premiere" / "P05"
            write(
                base / "P05_tp_tables_csv.md",
                "TP : utiliser `charger_pays_csv`, `filtrer_par_continent`, `convertir_populations`, "
                "`trier_par_continent_population` et `csv.DictReader`.",
            )
            code = base / "code"
            for label in ["starter", "corrige_professeur", "tests_attendus"]:
                write(code / f"P05_{label}_tables_csv.py", "def filtrer_par_continent(rows, continent):\n    return []\n")

            result = tp_alignment.analyze_tp_text_asset_alignment(root, prefixes=["P05"])

            self.assertTrue(any("charger_pays_csv" in error for error in result.errors))
            self.assertTrue(any("csv.DictReader" in error for error in result.errors))

    def test_t18_requires_trace_table_when_no_python_assets(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            base = root / "03_progressions" / "supports" / "terminale" / "T18"
            write(base / "T18_TD_boyer_moore.md", "TD : table mauvais caractère, trace complète, pseudo-code.")

            result = tp_alignment.analyze_tp_text_asset_alignment(root, prefixes=["T18"])

            self.assertTrue(any("table de trace" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
