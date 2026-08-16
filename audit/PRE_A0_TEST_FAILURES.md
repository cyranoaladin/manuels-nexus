# Pre-A0 Test Failures Ledger

Exact freezing of the 9 baseline test failures prior to A0 execution.

| NodeID | Suite | Failure Type | Category | Governance Only | Product Defect | Unexpected |
| --- | --- | --- | --- | --- | --- | --- |
| `tests/test_inventory_collection.py::test_repository_baseline_is_frozen_schema_valid_and_gate_green` | `inventory_collection` | `QualificationError` | `baseline_count_drift` | `True` | `False` | `False` |
| `tests/test_inventory_collection.py::test_materialize_baseline_qualifications_check_is_read_only` | `inventory_collection` | `QualificationError` | `baseline_count_drift` | `True` | `False` | `False` |
| `tests/test_inventory_collection.py::test_materialization_revalidations_use_only_the_owned_lock_identity` | `inventory_collection` | `QualificationError` | `baseline_count_drift` | `True` | `False` | `False` |
| `tests/test_inventory_collection.py::test_live_nsi_manual_declaration_covers_1nsi_and_tnsi` | `inventory_collection` | `QualificationError` | `baseline_count_drift` | `True` | `False` | `False` |
| `tests/test_baseline_qualification.py::test_repository_approved_set_has_exact_category_and_owner_counts` | `baseline_qualification` | `QualificationError` | `baseline_count_drift` | `True` | `False` | `False` |
| `tests/test_baseline_qualification.py::test_materialization_plan_preserves_history_and_emits_all_required_fields` | `baseline_qualification` | `QualificationError` | `baseline_count_drift` | `True` | `False` | `False` |
| `tests/test_baseline_qualification.py::test_repository_registry_excludes_prior_policy_from_current_policy` | `baseline_qualification` | `QualificationError` | `baseline_count_drift` | `True` | `False` | `False` |
| `tests/test_baseline_qualification.py::test_materialization_plan_corrects_policy_entry_drift_after_materialization` | `baseline_qualification` | `QualificationError` | `baseline_count_drift` | `True` | `False` | `False` |
| `tests/test_baseline_qualification.py::test_materialization_refuses_approved_set_drift_without_partial_payload` | `baseline_qualification` | `QualificationError` | `baseline_count_drift` | `True` | `False` | `False` |
