from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_tp_pedagogical_assets_runtime as tp_runtime


class TpPedagogicalAssetsRuntimeTest(unittest.TestCase):
    def test_slow_prefix_is_reported_with_timeout_budget(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            code = Path(raw) / "P01" / "code"
            code.mkdir(parents=True)
            (code / "P01_starter_demo.py").write_text(
                "def convert_base(value):\n    raise NotImplementedError('à compléter')\n",
                encoding="utf-8",
            )
            (code / "P01_corrige_professeur_demo.py").write_text(
                "def convert_base(value):\n"
                "    if value is None:\n"
                "        raise ValueError('invalid')\n"
                "    return bin(value)[2:]\n",
                encoding="utf-8",
            )
            (code / "P01_tests_attendus_demo.py").write_text(
                "import importlib, os, time\n"
                "module = importlib.import_module(os.environ['TP_MODULE'])\n"
                "def test_nominal():\n    time.sleep(0.15)\n    assert module.convert_base(5) == '101'\n"
                "def test_cas_limite_zero():\n    assert module.convert_base(0) == '0'\n"
                "def test_invalid():\n"
                "    try:\n"
                "        module.convert_base(None)\n"
                "    except (ValueError, NotImplementedError):\n"
                "        return\n"
                "    raise AssertionError('invalid attendu')\n"
                "if __name__ == '__main__':\n"
                "    test_nominal()\n"
                "    test_cas_limite_zero()\n"
                "    test_invalid()\n",
                encoding="utf-8",
            )

            result = tp_runtime.analyze_tp_runtime(Path(raw), prefixes=["P01"], total_timeout_seconds=0.05)

            self.assertTrue(any("durée totale" in error for error in result.errors))
            self.assertIn("P01", result.prefix_durations)


if __name__ == "__main__":
    unittest.main()
