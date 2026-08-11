# Validation post-Lot 3 hardening

## Tests rouges puis verts

Sous-ensemble TDD initial :

```text
$ python -m pytest -q tests/test_lot3_archive_security.py tests/test_archive_security_imports.py tests/test_source_archive_policy.py tests/test_repo_topology.py
15 failed, 28 passed in 1.30s
```

Échecs rouges observés :

- ZIP `"."` non refusé avant ouverture ;
- ZIP symlink via `external_attr` non refusé ;
- doublons de chemin cible non refusés ;
- `extractall` encore présent dans `scripts/run_audit_extracted_source.py` ;
- imports directs `scrapping_NSI.safe_archive` dans des modules de production ;
- docs `docs/archive_security_policy.md`, `docs/source_archive_policy.md`, `docs/repo_topology.md` absentes ;
- API `build_source_tar(root=..., target=...)` absente ;
- fallback archive source sans Git muet.

Sous-ensemble après implémentation :

```text
$ python -m pytest -q tests/test_lot3_archive_security.py tests/test_archive_security_imports.py tests/test_source_archive_policy.py tests/test_repo_topology.py
...........................................                              [100%]
43 passed in 1.17s

$ python -m pytest -q tests/test_archive_integration_wrappers.py tests/test_lot3_archive_security.py tests/test_archive_security_imports.py tests/test_source_archive_policy.py tests/test_repo_topology.py
..................................................                       [100%]
50 passed in 1.24s

$ python -m pytest -q tests/test_audit_extracted_source_no_hang.py tests/test_archive_portability_modes.py tests/test_final_quality_hardening.py::FinalQualityHardeningTest::test_runtime_budget_requires_source_archive_extraction tests/test_final_quality_hardening.py::FinalQualityHardeningTest::test_runtime_budget_runs_in_extracted_source_mode_without_archive tests/test_archive_integration_wrappers.py
............                                                        [100%]
17 passed in 53.49s
```

## Ruff ciblé

```text
$ python -m ruff check <fichiers modifiés>
All checks passed!
```

## Privacy

```text
$ python scripts/check_no_private_data.py
check_no_private_data: PASS
```

## Validation complète

Venv neuf :

```text
$ rm -rf dist 01_build_reports .pytest_cache .ruff_cache .mypy_cache .coverage /tmp/nsi_post_lot3_venv
$ find . -name __pycache__ -type d -prune -exec rm -rf {} +
$ python3 -m venv /tmp/nsi_post_lot3_venv
$ /tmp/nsi_post_lot3_venv/bin/python -m pip install --upgrade pip
Successfully installed pip-26.1.2
$ /tmp/nsi_post_lot3_venv/bin/python -m pip install -r requirements.txt
Successfully installed ... jsonschema-4.26.0 ... pytest-9.0.2 ... ruff-0.6.9 ... mypy-2.1.0
```

Collecte finale :

```text
$ /tmp/nsi_post_lot3_venv/bin/python -m pytest --collect-only -q
324 tests collected in 0.55s
```

Suite finale :

```text
$ /tmp/nsi_post_lot3_venv/bin/python -m pytest -q
324 passed, 2 subtests passed in 68.58s (0:01:08)
```

Ruff :

```text
$ /tmp/nsi_post_lot3_venv/bin/ruff check .
All checks passed!
```

Mypy strict :

```text
$ /tmp/nsi_post_lot3_venv/bin/mypy --strict scripts/archive_security.py scripts/check_archive_portability.py scripts/check_audit_extracted_runtime_budget.py scripts/build_source_archive.py scripts/build_source_zip.py scrapping_NSI/scraper_eduscol.py scrapping_NSI/organizer_nsi.py scripts/check_repo_topology.py
Success: no issues found in 8 source files
```

Couverture archive :

```text
$ PYTHONPATH=. /tmp/nsi_post_lot3_venv/bin/coverage run --branch -m pytest -q tests/test_lot3_archive_security.py
35 passed in 0.96s

$ /tmp/nsi_post_lot3_venv/bin/coverage report -m scripts/archive_security.py scrapping_NSI/safe_archive.py
Name                            Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------------------
scrapping_NSI/safe_archive.py     183      0     48      0   100%
scripts/archive_security.py         3      0      0      0   100%
---------------------------------------------------------------------------
TOTAL                             186      0     48      0   100%
```

Privacy et Grep-Garde :

```text
$ python scripts/check_no_private_data.py
check_no_private_data: PASS

$ grep -rn -E "embed_text|cosine_distance|SEMANTIC_SIMILARITY_THRESHOLD|intitule_embeddings|cosinus|embedding|sémantique" scripts/ tests/; printf 'grep_exit=%s\n' "$?"
grep_exit=1
```

Non-modification pédagogique :

```text
$ git diff -- 03_progressions premiere terminale 02_modeles_documents
```

Sortie vide.

## Cibles Makefile

Exécution groupée après commit propre, depuis la branche `lot3-post-merge-hardening` :

```text
$ make audit-idempotence
$ make deliver-pedagogical-archive
$ make deliver-source-zip
$ make package-audit
$ env -u NSI_DOCUMENTS_DRIVE_ROOT timeout 180 make audit-extracted-source
$ DELIVERED_ARCHIVE=dist/source_clean.tar.gz make verify-delivery-archive
```

Résultat de processus : code de sortie 0.

Extraits significatifs de la sortie :

```text
check_quality_gates: PASS
check_no_private_data: PASS
check_delivered_archive_exactly_source_clean: PASS
```

La sortie complète est très volumineuse car `audit-idempotence` exécute deux audits. Le dernier contrôle visible de la chaîne est :

```text
DELIVERED_ARCHIVE="dist/source_clean.tar.gz" python scripts/check_delivered_archive_exactly_source_clean.py
check_delivered_archive_exactly_source_clean: PASS
```

## RAG requis

```text
$ make rag-smoke-required || true
python scripts/rag_smoke_test.py
RAG_SMOKE_TEST_FAILED
- hit 4: métadonnées minimales absentes
make: *** [Makefile:73: rag-smoke-required] Error 1
```

Interprétation : échec attendu et bloquant pour déclarer le RAG fonctionnel. La cause constatée sur cette exécution est l'absence de métadonnées minimales sur un hit, pas un succès RAG.

## Release audit

```text
$ make release-audit || true
python scripts/cleanup_python_artifacts.py
cleanup_python_artifacts: removed 0 path(s)
python scripts/check_git_clean.py
check_git_clean: PASS
python scripts/check_drive_mapping_release.py
check_drive_mapping_release: KO
- Drive partiellement intégré: deferred=3, missing_local_copy=7, rejected_sensitive=5
make: *** [Makefile:359: release-audit] Error 1
```

Interprétation : échec attendu. Le dépôt reste `NON_RELEASE_READY`.

## État Git après livrables

```text
$ git status -sb --short
## lot3-post-merge-hardening

$ git status --ignored --short dist 01_build_reports .coverage .pytest_cache .ruff_cache .mypy_cache
!! 01_build_reports/
!! dist/
```

Interprétation : aucun fichier suivi modifié ; seuls les livrables ignorés sont présents.

## Correction CI post-PR

Premier run PR distant :

```text
$ gh run view --repo cyranoaladin/NSI 28408192759 --job 84175269789 --log
FAILED tests/test_repo_topology.py::test_check_repo_topology_passes_current_workspace
AssertionError: check_repo_topology: KO
- dépôt canonique inattendu: <github_actions_checkout>
```

Cause racine : le garde topologie couplait l'identité du dépôt canonique au nom
local `nsi-enseignement`, alors que GitHub Actions extrait le dépôt
`cyranoaladin/NSI` dans un répertoire nommé `NSI`.

Test rouge ajouté :

```text
$ python -m pytest -q tests/test_repo_topology.py::test_check_repo_topology_accepts_github_actions_checkout_name
FAILED tests/test_repo_topology.py::test_check_repo_topology_accepts_github_actions_checkout_name
AssertionError: assert 'dépôt canonique inattendu' not in ...
```

Après correction, l'identité canonique accepte le nom local `nsi-enseignement`
ou un remote Git contenant `cyranoaladin/NSI`.

Sorties vertes :

```text
$ python -m pytest -q tests/test_repo_topology.py::test_check_repo_topology_accepts_github_actions_checkout_name
1 passed in 0.12s

$ python -m pytest -q tests/test_repo_topology.py
4 passed in 0.31s

$ python scripts/check_repo_topology.py
check_repo_topology: PASS

$ python -m pytest -q
325 passed, 2 subtests passed in 72.29s (0:01:12)

$ ruff check scripts/check_repo_topology.py tests/test_repo_topology.py
All checks passed!

$ /tmp/nsi_post_lot3_venv/bin/mypy --strict scripts/check_repo_topology.py
Success: no issues found in 1 source file
```
