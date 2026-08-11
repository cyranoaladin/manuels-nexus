from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_no_private_data as privacy


class PrivateDataDetectionTest(unittest.TestCase):
    def test_year_range_is_not_tunisian_phone(self) -> None:
        text = "Documents_DRIVE/9_NSI_2025-2026/sequence.pdf"
        matches = [match.group(0) for match in privacy.TN_PHONE_RE.finditer(text)]

        self.assertTrue(all(privacy.YEAR_RANGE_RE.fullmatch(value) for value in matches))

    def test_hash_fragment_is_not_tunisian_phone(self) -> None:
        text = "242224f04a4ae0efd8ed2a17e8d74b054f8d53e33eb1e33ae163c62f" + "24" + "170779,non"

        self.assertEqual(list(privacy.TN_PHONE_RE.finditer(text)), [])

    def test_standalone_tunisian_phone_is_detected(self) -> None:
        value = "24" + "170779"
        text = "Contact temporaire " + value

        self.assertEqual([match.group(0) for match in privacy.TN_PHONE_RE.finditer(text)], [value])

    def test_population_context_is_not_tunisian_phone(self) -> None:
        text = 'Espagne,Madrid,Europe,46754778 ; int(row["POPULATION"]) donne 46754778.'
        matches = list(privacy.TN_PHONE_RE.finditer(text))

        self.assertTrue(matches)
        self.assertTrue(all(privacy.is_population_context(text, match.start(), match.end()) for match in matches))

    def test_sha256_hash_is_not_french_phone(self) -> None:
        text = "270881f4b45a8cd741ddad93bf7ed63adcf668455847c7ea71311f0946533745,non"
        matches = list(privacy.FR_PHONE_RE.finditer(text))
        self.assertTrue(matches, "regex should match the digit sequence")
        self.assertTrue(
            all(privacy.is_hex_hash_context(text, m.start(), m.end()) for m in matches),
            "hex hash context should suppress the false positive",
        )

    def test_real_french_phone_still_detected(self) -> None:
        # Build the fixture number by concatenation so the scanner does not
        # flag this source file itself as containing PII.
        phone = "06 12" + " 34 56 78"
        text = f"Appelez le {phone} pour plus d'infos."
        matches = list(privacy.FR_PHONE_RE.finditer(text))
        self.assertTrue(matches, "real phone number should be detected")
        self.assertFalse(
            any(privacy.is_hex_hash_context(text, m.start(), m.end()) for m in matches),
            "real phone should not be suppressed by hex hash heuristic",
        )

    def test_phone_near_hash_on_same_line_still_detected(self) -> None:
        phone = "06 12" + " 34 56 78"
        text = f"sha256=270881f4b45a8cd741ddad93bf7ed63adcf668455847c7ea71311f0946533745; tel={phone}"
        matches = list(privacy.FR_PHONE_RE.finditer(text))
        self.assertTrue(matches, "regex should match the phone number")
        not_suppressed = [
            m for m in matches
            if not privacy.is_hex_hash_context(text, m.start(), m.end())
        ]
        self.assertTrue(not_suppressed, "phone near hash must NOT be suppressed")

    def test_build_reports_are_not_source_privacy_scope(self) -> None:
        self.assertIn("01_build_reports", privacy.EXCLUDED_PARTS)


if __name__ == "__main__":
    unittest.main()
