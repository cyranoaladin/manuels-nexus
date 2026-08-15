# GLOBAL TEST BASELINE — MAIN (a21ff532750cebd156b4a77666f434c40ae9ee20)

- **Total Tests** : 4920
- **Passed** : 4897
- **Failed** : 18
- **Skipped** : 5

## Failing Tests on MAIN

| Suite | NodeID | Failure Class | Message |
| :--- | :--- | :--- | :--- |
| `root` | `tests/test_baseline_qualification.py::test_repository_approved_set_has_exact_category_and_owner_counts` | `Other` | `FAILED [  2%]` |
| `root` | `tests/test_baseline_qualification.py::test_materialization_plan_preserves_history_and_emits_all_required_fields` | `Other` | `FAILED [  2%]` |
| `root` | `tests/test_baseline_qualification.py::test_repository_registry_excludes_prior_policy_from_current_policy` | `Other` | `FAILED [  2%]` |
| `root` | `tests/test_baseline_qualification.py::test_materialization_plan_corrects_policy_entry_drift_after_materialization` | `Other` | `FAILED [  5%]` |
| `root` | `tests/test_baseline_qualification.py::test_materialization_refuses_approved_set_drift_without_partial_payload` | `Other` | `FAILED [  5%]` |
| `root` | `tests/test_inventory_collection.py::test_real_harvest_candidates_never_produce_blocking_production_anomalies` | `Other` | `FAILED [ 42%]` |
| `root` | `tests/test_inventory_collection.py::test_materialize_baseline_qualifications_check_is_read_only` | `Other` | `FAILED [ 49%]` |
| `root` | `tests/test_inventory_collection.py::test_materialization_revalidations_use_only_the_owned_lock_identity` | `Other` | `FAILED [ 49%]` |
| `root` | `tests/test_inventory_collection.py::test_repository_build_applies_qualification_view_without_mutating_raw_anomalies` | `Other` | `FAILED [ 54%]` |
| `root` | `tests/test_inventory_collection.py::test_repository_baseline_is_frozen_schema_valid_and_gate_green` | `Other` | `FAILED [ 58%]` |
| `root` | `tests/test_inventory_collection.py::test_live_1nsi_runtime_selection_matches_declared_manual_assemblies` | `Other` | `FAILED [ 80%]` |
| `root` | `tests/test_inventory_collection.py::test_live_1nsi_manual_declaration_closes_assembly_debt_without_tnsi` | `Other` | `FAILED [ 80%]` |
| `root` | `tests/test_inventory_collection.py::test_declared_assembler_allowlist_preserves_real_and_planned_engines` | `Other` | `FAILED [ 86%]` |
| `root` | `tests/test_inventory_collection.py::test_real_reports_expose_known_exercise_contradictions` | `Other` | `FAILED [ 99%]` |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_scope_guard_pins_exact_sources_and_immutable_surfaces` | `Other` | `FAILED [  3%]` |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_build_manifest_governance_uses_current_clean_base` | `Other` | `FAILED [  3%]` |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_cli_exposes_required_modes` | `Other` | `FAILED [ 20%]` |
| `nsi` | `NSI/tests/test_gates_corpus.py::test_amenagee_extract_avoids_lstinline_inside_tabular_cells` | `Other` | `FAILED [ 48%]` |
