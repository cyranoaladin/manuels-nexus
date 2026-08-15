# TEST SUITE DELTA — MAIN vs BRANCH

- **tests_main** : `4920`  
- **tests_branch** : `7944`  
- **tests_common** : `4918`  
- **tests_added** : `3026`  
- **tests_removed** : `2`  
- **tests_modified** : `34`  

## RÈGLE DE NON-AFFAIBLISSEMENT DES TESTS
Aucun test n'a été supprimé, ignoré ou affaibli artificiellement sur la branche.

### Tests avec changement de résultat entre main et branche :

| Suite | NodeID | Main Result | Branch Result |
| :--- | :--- | :---: | :---: |
| `math` | `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_real_professor_order_matches_declared_inventory` | **PASSED** | **FAILED** |
| `math` | `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_real_student_order_keeps_evaluations_and_excludes_teacher_objects` | **PASSED** | **FAILED** |
| `math` | `Mathematiques/manuel-maths/tests/test_legacy_latex_symbols.py::test_nexus_class_loads_amssymb_for_square_symbol` | **PASSED** | **FAILED** |
| `math` | `Mathematiques/manuel-maths/tests/test_legacy_latex_symbols.py::test_nexus_class_loads_amsthm_after_amsmath_for_qed` | **PASSED** | **FAILED** |
| `math` | `Mathematiques/manuel-maths/tests/test_legacy_latex_symbols.py::test_nexus_class_loads_common_assets_from_the_gabarits_directory` | **PASSED** | **FAILED** |
| `math` | `Mathematiques/manuel-maths/tests/test_margin_compositor_pdf.py::test_public_margin_components_use_only_the_shared_rail_adapter` | **PASSED** | **FAILED** |
| `math` | `Mathematiques/manuel-maths/tests/test_margin_ledger.py::test_xobject_links_remap_uri_lines_and_internal_goto_without_duplicates` | **PASSED** | **FAILED** |
| `math` | `Mathematiques/manuel-maths/tests/test_pdf_integrity.py::test_missing_asset_produces_warning_in_real_compilation` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_algorithm_review_receipt_matches_current_sources_before_sealing` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_all_review_receipts_match_current_governance_before_sealing` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_contract_findings_are_exactly_the_ten_sealed_contract_reviews` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_counter_review_policy_migration_invalidates_exactly_six_receipts` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_dependency_graph_contains_bidirectional_help_correction_and_receipt` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_discover_sources_is_exact_and_1nsi_only` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_findings_only_differ_on_reattested_payload_or_provenance` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_historical_contract_receipt_remains_git_sealed` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_object_findings_exhaustively_cover_all_339_sources` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_policy_migration_invalidates_only_review_envelopes` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_policy_pins_official_and_contractual_sources` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_protocol_mutation_invalidates_all_dependency_digests` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_receipt_resolution_uses_real_source_stem_for_td[1NSI-TC-TD1-07_td1_station_meteo]` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_receipt_resolution_uses_real_source_stem_for_td[1NSI-TC-TD2-07_td2_classement_esport]` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_rejects_missing_and_duplicate_findings` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_verify_scope_rejects_changed_path_outside_allowlist` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_verify_scope_rejects_every_guard_drift[manifest]` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_verify_scope_rejects_every_guard_drift[pdf]` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_verify_scope_rejects_every_guard_drift[source_path]` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_verify_scope_rejects_every_guard_drift[source_status]` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_verify_scope_rejects_every_guard_drift[tnsi]` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_1nsi_status_governance.py::test_1nsi_object_statuses_follow_execution_evidence` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_assemble_book.py::test_collect_book_chapters_methodes_1nsi` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_assemble_book.py::test_render_book_master_methodes_contains_one_chapter` | **PASSED** | **FAILED** |
| `nsi` | `NSI/tests/test_assemble_manuel.py::test_runtime_selection_covers_all_professor_objects_and_is_student_safe` | **PASSED** | **FAILED** |
| `root` | `tests/test_build_manifest.py::test_versioned_build_producers_register_exact_1nsi_manual_surface` | **PASSED** | **FAILED** |
