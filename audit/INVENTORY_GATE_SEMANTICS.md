# Inventory Gate Semantics

This document details the precise operational meaning of each test in `tests/test_inventory_collection.py` and `tests/test_baseline_qualification.py`.

## Semantics Matrix

| NodeID | Purpose | What Failure Means | Regression Gate | Release Gate | Depends on Baseline | Can Be Green with Open Debt |
| --- | --- | --- | --- | --- | --- | --- |
| `tests/test_inventory_collection.py::test_repository_baseline_is_frozen_schema_valid_and_gate_green` | Verifies baseline integrity & schema validity | The baseline is corrupted or diverges from observed anomalies | YES | NO | YES | YES |
| `tests/test_inventory_collection.py::test_live_nsi_manual_declaration_covers_1nsi_and_tnsi` | Validates NSI manual declarations | NSI manual configuration is incomplete | YES | YES | NO | NO |
| `tests/test_inventory_collection.py::test_materialize_baseline_qualifications_check_is_read_only` | Ensures materialization check does not mutate state | Materialization modified repository state during read-only check | YES | NO | YES | YES |
| `tests/test_inventory_collection.py::test_materialization_revalidations_use_only_the_owned_lock_identity` | Validates lock ownership in baseline materialization | Generation lock key mismatch | YES | NO | YES | YES |
| `tests/test_baseline_qualification.py::test_repository_approved_set_has_exact_category_and_owner_counts` | Audits category and owner counts against baseline policy | Active anomalies shifted count/category relative to policy | YES | NO | YES | YES |
| `tests/test_baseline_qualification.py::test_materialization_plan_preserves_history_and_emits_all_required_fields` | Verifies baseline history preservation | Historical disposition field missing or corrupted | YES | NO | YES | YES |
| `tests/test_baseline_qualification.py::test_repository_registry_excludes_prior_policy_from_current_policy` | Verifies isolation between policy generations | Prior policy rule leaked into active set | YES | NO | YES | YES |
| `tests/test_baseline_qualification.py::test_materialization_plan_corrects_policy_entry_drift_after_materialization` | Validates drift correction during materialization | Materialization plan failed to normalize drift | YES | NO | YES | YES |
| `tests/test_baseline_qualification.py::test_materialization_refuses_approved_set_drift_without_partial_payload` | Refuses materialization when approved set drifts without explicit payload | Unapproved anomaly count drift detected | YES | NO | YES | YES |

## Critical Distinction

- A **PASS** on `--fail-on-new` or baseline tests indicates **no regression relative to a known baseline**.
- A **PASS** on `--release-strict` indicates **publication readiness (0 release debt)**.
- Updating the baseline to make regression gates GREEN **must never** be used to mask release debt.
