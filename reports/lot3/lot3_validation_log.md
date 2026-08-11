# Lot 3 - Validation Zip-Slip / Zip-Bomb

Date: 2026-06-29  
Branche: `lot1/substance-gouvernance`  
Base annoncée: `570eeb2 Implémenter la déduplication forte par sha256`

## Résumé technique

- Garde canonique ajouté: `scrapping_NSI/safe_archive.py`.
- Compatibilité scripts: `scripts/archive_security.py` réexporte le garde canonique.
- Appels `extractall` remplacés dans:
  - `scrapping_NSI/scraper_eduscol.py`;
  - `scrapping_NSI/organizer_nsi.py`;
  - `scripts/check_archive_portability.py`;
  - `scripts/check_audit_extracted_runtime_budget.py`.
- Extraction atomique via répertoire sibling `.part`, supprimé sur échec.
- Seuils appliqués: 500 Mo décompressés, 10 000 membres, ratio 100x pour contenus décompressés > 1 Mo.
- Le clone imbriqué `nsi-enseignement` est explicitement exclu de pytest, ruff et coverage.

## TDD rouge initial

Commande:

```text
.venv/bin/pytest -q tests/test_lot3_archive_security.py
```

Sortie:

```text
FFFFFF                                                                   [100%]
FAILED tests/test_lot3_archive_security.py::test_eduscol_zip_slip_is_rejected_and_writes_nothing_outside
FAILED tests/test_lot3_archive_security.py::test_eduscol_zip_bomb_metadata_is_rejected_before_extraction
FAILED tests/test_lot3_archive_security.py::test_eduscol_archive_failure_is_atomic
FAILED tests/test_lot3_archive_security.py::test_safe_tar_extraction_rejects_tar_slip
FAILED tests/test_lot3_archive_security.py::test_safe_zip_extraction_rejects_suspicious_compression_ratio
FAILED tests/test_lot3_archive_security.py::test_safe_tar_extraction_accepts_clean_archive
6 failed in 0.18s
```

Interprétation: le rouge prouvait que l'ancien `ZipFile.extractall` ne levait pas d'exception sécurité et qu'aucun module commun de garde TAR/ZIP n'existait encore.

## pytest --collect-only

Commande:

```text
.venv/bin/pytest --collect-only
```

Sortie pertinente:

```text
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0
rootdir: <repo>
configfile: pyproject.toml
testpaths: tests
collected 262 items

<Module test_lot3_archive_security.py>
  <Function test_safe_archive_module_is_canonical>
  <Function test_zip_slip_vulnerability>
  <Function test_zip_bomb_volume_limit>
  <Function test_extraction_atomicity_on_failure>
  <Function test_zip_bomb_ratio_uses_uncompressed_size_threshold>
  <Function test_eduscol_zip_slip_is_rejected_and_writes_nothing_outside>
  <Function test_eduscol_zip_bomb_metadata_is_rejected_before_extraction>
  <Function test_eduscol_archive_failure_is_atomic>
  <Function test_safe_tar_extraction_rejects_tar_slip>
  <Function test_safe_zip_extraction_rejects_suspicious_compression_ratio>
  <Function test_safe_zip_extraction_accepts_large_metadata_with_normal_ratio>
  <Function test_safe_tar_extraction_accepts_clean_archive>
  <Function test_safe_zip_extraction_accepts_directory_and_removes_stale_part>
  <Function test_safe_zip_rejects_absolute_member_and_file_count_limit>
  <Function test_safe_tar_rejects_unsupported_members_in_preflight_and_stream>
  <Function test_safe_tar_rejects_unreadable_regular_member>
  <Function test_invalid_archives_propagate_and_cleanup>
  <Function test_copy_stream_enforces_runtime_limit>
<Module test_lot3_topological_isolation.py>
  <Function test_root_pytest_ruff_and_coverage_exclude_nested_clone>
  <Function test_root_pytest_collect_only_omits_nested_clone>

========================= 262 tests collected in 0.45s =========================
```

## pytest -q

Commande:

```text
.venv/bin/pytest -q
```

Sortie:

```text
...................................................................... [ 27%]
........................................................................ [ 54%]
........................................................................ [ 82%]
..............................................                         [100%]
262 passed, 2 subtests passed in 63.89s (0:01:03)
```

## Couverture du garde archive

Commande:

```text
rm -f .coverage && .venv/bin/coverage erase && .venv/bin/coverage run --source=scrapping_NSI -m pytest -q tests/test_lot3_archive_security.py && .venv/bin/coverage report -m scrapping_NSI/safe_archive.py
```

Sortie:

```text
..................                                                       [100%]
18 passed in 1.03s
Name                            Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------------------
scrapping_NSI/safe_archive.py     154      0     42      0   100%
---------------------------------------------------------------------------
TOTAL                             154      0     42      0   100%
```

## ruff

Commande:

```text
.venv/bin/ruff check . && cd scrapping_NSI && ../.venv/bin/ruff check .
```

Sortie:

```text
All checks passed!
All checks passed!
```

## mypy strict

Commande:

```text
MYPYPATH=scrapping_NSI .venv/bin/mypy --strict --follow-imports=skip scrapping_NSI/safe_archive.py scripts/archive_security.py scripts/check_archive_portability.py scripts/check_audit_extracted_runtime_budget.py scrapping_NSI/scraper_eduscol.py scrapping_NSI/organizer_nsi.py
```

Sortie:

```text
Success: no issues found in 6 source files
```

Note: un lancement sans `--follow-imports=skip` en passant simultanément `scrapping_NSI/netpolicy.py` comme chemin et `scraper_eduscol.py` déclenche un doublon de nom mypy (`scrapping_NSI.netpolicy` vs `netpolicy`). Le contrôle ci-dessus cible les fichiers Lot 3 et ne masque pas ce problème de topologie d'import.

## Privacy

Commande:

```text
.venv/bin/python scripts/check_no_private_data.py
```

Sortie:

```text
check_no_private_data: PASS
```

## Grep-Garde

Commande:

```text
grep -rn -E "embed_text|cosine_distance|SEMANTIC_SIMILARITY_THRESHOLD|intitule_embeddings|cosinus|embedding|sémantique" scripts/ tests/
```

Sortie:

```text

```

Exit code: `1`, interprété `0` car aucune occurrence interdite n'a été trouvée.

## git diff --check

Commande:

```text
git diff --check
```

Sortie:

```text

```

Exit code: `0`.

## git status -sb

Commande:

```text
git status -sb
```

Sortie:

```text
## lot1/substance-gouvernance...origin/lot1/substance-gouvernance
 M pyproject.toml
 M scrapping_NSI/netpolicy.py
 M scrapping_NSI/organizer_nsi.py
 M scrapping_NSI/ruff.toml
 M scrapping_NSI/scraper_eduscol.py
 M scripts/check_archive_portability.py
 M scripts/check_audit_extracted_runtime_budget.py
?? .coveragerc
?? 00_programmes_officiels/programme_nsi_premiere.pdf
?? 00_programmes_officiels/programme_nsi_premiere.txt
?? 00_programmes_officiels/programme_nsi_terminale.pdf
?? 00_programmes_officiels/programme_nsi_terminale.txt
?? scrapping_NSI/__init__.py
?? scrapping_NSI/safe_archive.py
?? scripts/__init__.py
?? scripts/archive_security.py
?? tests/test_lot3_archive_security.py
?? tests/test_lot3_topological_isolation.py
```

Note de périmètre: les quatre fichiers `00_programmes_officiels/programme_nsi_*` apparaissent non suivis dans l'arbre de travail et ne sont pas nécessaires au correctif Lot 3. Ils n'ont pas été supprimés.

## Verdict

Statut Lot 3: `READY_FOR_REVIEW`.

Lot 4 non ouvert.
