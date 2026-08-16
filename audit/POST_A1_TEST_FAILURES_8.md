# Post-A1 Test Failures Audit (8 Remaining Failures)

Detailed classification and root cause analysis of all 8 remaining test failures.

## Classified Test Failures

| NodeID | Failure Message | Category | Product Defect | Governance Staleness | Baseline Ref Issue | Manifest Prov Issue | Expected Phase | Must Fix Before A2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `tests/test_baseline_qualification.py::test_repository_approved_set_has_exact_category_and_owner_counts` | `QualificationError: count, fingerprint digest or category counts drift` | Governance / Baseline | NO | YES | YES | NO | Baseline Materialization Phase | NO |
| `tests/test_baseline_qualification.py::test_materialization_plan_preserves_history_and_emits_all_required_fields` | `QualificationError: count, fingerprint digest or category counts drift` | Governance / Baseline | NO | YES | YES | NO | Baseline Materialization Phase | NO |
| `tests/test_baseline_qualification.py::test_repository_registry_excludes_prior_policy_from_current_policy` | `QualificationError: count, fingerprint digest or category counts drift` | Governance / Baseline | NO | YES | YES | NO | Baseline Materialization Phase | NO |
| `tests/test_baseline_qualification.py::test_materialization_plan_corrects_policy_entry_drift_after_materialization` | `QualificationError: count, fingerprint digest or category counts drift` | Governance / Baseline | NO | YES | YES | NO | Baseline Materialization Phase | NO |
| `tests/test_baseline_qualification.py::test_materialization_refuses_approved_set_drift_without_partial_payload` | `QualificationError: count, fingerprint digest or category counts drift` | Governance / Baseline | NO | YES | YES | NO | Baseline Materialization Phase | NO |
| `tests/test_inventory_collection.py::test_materialize_baseline_qualifications_check_is_read_only` | `KeyError: 'approved_fingerprint_count'` | Governance / Baseline | NO | YES | YES | NO | Baseline Materialization Phase | NO |
| `tests/test_inventory_collection.py::test_materialization_revalidations_use_only_the_owned_lock_identity` | `AssertionError: assert ['jeu approuvé...counts drift'] == []` | Governance / Baseline | NO | YES | YES | NO | Baseline Materialization Phase | NO |
| `tests/test_inventory_collection.py::test_repository_baseline_is_frozen_schema_valid_and_gate_green` | `assert False is True (frozen baseline drift)` | Governance / Baseline | NO | YES | YES | NO | Baseline Materialization Phase | NO |

## Summary
All 8 test failures are **100% governance-only baseline reference issues** caused by the strict user directive prohibiting baseline policy updates while debt burndown occurs (`6425 -> 5615`). There are **ZERO product defects** among the 8 failures.
