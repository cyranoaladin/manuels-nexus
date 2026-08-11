# Lot 2 validation log
date: 2026-06-29T10:46:32+01:00
head: a22dca9

## pytest -q
........................................................................ [ 29%]
........................................................................ [ 59%]
........................................................................ [ 89%]
..........................                                             [100%]
=============================== warnings summary ===============================
tests/test_archive_portability_modes.py::ArchivePortabilityModesTest::test_source_clean_mode_does_not_require_git_bundle
  /usr/lib/python3.12/tarfile.py:2274: DeprecationWarning: Python 3.14 will, by default, filter extracted tar archives and reject files or modify their metadata. Use the filter argument to control this behavior.
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
242 passed, 1 warning, 2 subtests passed in 61.47s (0:01:01)

## coverage scraper_nsi_v2.py provenance.py
........................................................................ [ 98%]
.                                                                        [100%]
73 passed in 1.16s
Name                Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------
provenance.py          80      0     32      0   100%
scraper_nsi_v2.py     413      0    142      0   100%
---------------------------------------------------------------
TOTAL                 493      0    174      0   100%

## ruff check .
All checks passed!

## grep-garde lot 1
GREP-GARDE: aucune occurrence

## diff pédagogique interdit
DIFF_PEDAGOGIQUE: vide
