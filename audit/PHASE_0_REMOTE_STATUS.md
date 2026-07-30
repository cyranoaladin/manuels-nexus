# État distant de la Phase 0

## Mission

- Branche locale observée : `finalisation/collection-v1`
- SHA local observé : `363c8352695792e532574160873d0f391348667a`
- SHA distant observé : `origin/finalisation/collection-v1` = `363c8352695792e532574160873d0f391348667a`
- `git rev-list --left-right --count origin/finalisation/collection-v1...HEAD` : `0 0`
- Worktree de départ propre.

## Run CI analysé

- `run`: `30546406535`
- `job`: `90883561872`
- URL: <https://github.com/cyranoaladin/manuels-nexus/actions/runs/30546406535>
- Résumé : échec aux deux étapes `Gates Phase 0 aux codes exacts` et `Suite complète avec couverture lignes et branches`.
- Les artefacts du run ont été téléchargés dans `/tmp/manuels-ci-30546406535.*` sans modification du dépôt.

## Sub-gate(s) en cause

- Sous-gate défaillante principale : `check`
- Résultat réel observé en CI : `3`
- Résultat attendu dans le contrat de phase 0 : `0`
- Cause technique : diff détectés dans `audit/ECARTS_ET_CONTRADICTIONS.yaml`, `audit/INVENTAIRE_COLLECTION.json`, `audit/MATRICE_LIVRABLES.yaml`.
- Payload (stdout de gate `check`) extrait de `gate-summary.json` :
  - `exit_code`: `3`
  - `success`: `false`
  - `reasons`: `[
      "diff: audit/ECARTS_ET_CONTRADICTIONS.yaml",
      "diff: audit/INVENTAIRE_COLLECTION.json",
      "diff: audit/MATRICE_LIVRABLES.yaml"
    ]`
  - `blocker_count`: `3`

## Exécution des gates

Ordre d’exécution (CI et local via script) :

1. `require-clean`
2. `check`
3. `validate-model`
4. `fail-on-new`
5. `release-strict`

| Gate | Réel | Attendu |
|---|---|---|
| require-clean | `0` | `0` |
| check | `3` | `0` |
| validate-model | `0` | `0` |
| fail-on-new | `0` | `0` |
| release-strict | `7` | `7` |

`release-strict` en échec contrôlé reste attendu à `7` en phase NO-GO.

### Preuves gate

- `scripts/ci_audit_collection.py run-gates` conserve désormais pour chaque gate : `process_code`, `stdout`, `stderr`, bloc `repeat` pour `release-strict`.
- Le wrapper échoue explicitement si `check` retourne un code différent de `0`.

## Échec pytest en CI (run 30546406535)

Vingt-deux nœuds `FAILED` relevés dans `--log-failed`.

Node IDs (extrait) :
- `Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_checker_cli_synthetic_exit_codes`
- `Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_rubric_tab_dynamic_fixture_pdf`
- `Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_navigation_blank_fixture_pdf`
- `Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_method_pairing_fixtures[0..3]`
- `Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_multicols_marginnote_is_redirected`
- `Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_exercise_grid_fixture_pdf`
- `Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_validation_png_reference_hashes`
- `Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_non_diagnostics_page_hashes_reject_a_changed_page`
- `Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_page13_diagnostics_layout_pdf`
- `Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_qcm_diagnostics_and_corrections_pdf`
- `Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_maquette_v5_acceptance`
- `Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_course_fixture_pdf`
- `Mathematiques/manuel-maths/tests/test_pdf_integrity.py::test_missing_asset_produces_warning_in_real_compilation`
- `Mathematiques/manuel-maths/tests/test_pdf_integrity.py::test_specimen_compiles_with_exit_zero`
- `tests/test_inventory_collection.py::test_update_baseline_cli_rejects_ci_dirty_repo_and_invalid_model`
- `tests/test_inventory_collection.py::test_update_baseline_writes_audited_transition_and_preserves_resolved_history`
- `tests/test_inventory_collection.py::test_update_baseline_rejects_head_change_immediately_before_replace`
- `tests/test_inventory_collection.py::test_update_baseline_recovers_interrupted_write_before_clean_preflight`

## Cinq tests visuels connus

Les cinq nœuds visuels confirmés dans `CI` sont :
1. `test_validation_png_reference_hashes`
2. `test_non_diagnostics_page_hashes_reject_a_changed_page`
3. `test_page13_diagnostics_layout_pdf`
4. `test_qcm_diagnostics_and_corrections_pdf`
5. `test_maquette_v5_acceptance`

Ils correspondent au plan visuel déjà documenté dans `audit/VISUAL_BASELINE_DECISION_REQUIRED.md` (divergences sur les onglets de pages 1, 7, 8, 9, 10, 11, 12, 15) et aux décisions NO-GO déjà en place.

## Checks locaux exécutés après modification

- `python -m pytest tests/test_ci_audit_collection.py -q` ✅ 41 passed
- `python -m pytest tests/test_build_manifest.py tests/test_ci_audit_collection.py tests/test_inventory_collection.py -q` ✅ 539 passed
- `python -m ruff check scripts/ci_audit_collection.py tests/test_ci_audit_collection.py` ✅
- `python -m mypy scripts/ci_audit_collection.py` ✅
- `python scripts/ci_audit_collection.py run-gates --root . --output-dir <tmp> --require-clean --check --validate-model --fail-on-new --release-strict` ❌ en local attendu en dépôt propre (`require-clean=4`) ; les écarts observés viennent du statut local modifié.
