from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TpPedagogicalAssetsNoHangTest(unittest.TestCase):
    def test_script_terminates_with_buffered_and_unbuffered_python(self) -> None:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        commands = [
            [sys.executable, "-m", "scripts.check_tp_pedagogical_assets"],
            [sys.executable, "-u", "-m", "scripts.check_tp_pedagogical_assets"],
        ]
        for command in commands:
            with self.subTest(command=" ".join(command)):
                completed = subprocess.run(
                    command,
                    cwd=ROOT,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=90,
                )
                self.assertEqual(completed.returncode, 0, completed.stdout)
                self.assertIn("check_tp_pedagogical_assets: PASS", completed.stdout)


if __name__ == "__main__":
    unittest.main()
