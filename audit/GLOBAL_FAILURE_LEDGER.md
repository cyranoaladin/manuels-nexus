# GLOBAL FAILURE LEDGER — 82 DIAGNOSTICS INDIVIDUELS

- **introduced_by_branch** : `84`  
- **preexisting** : `17`  
- **changed_preexisting** : `34`  
- **remaining** : `101`  

| ID | Suite | NodeID | Fails Main | Introduced | Charter Rel | Content Rel | Root Cause |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `FAIL-001` | `math` | `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_real_professor_order_matches_declared_inventory` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-002` | `math` | `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_real_student_order_keeps_evaluations_and_excludes_teacher_objects` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-003` | `math` | `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_the_bridge_covers_every_box_macro_the_corpus_actually_uses` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-004` | `math` | `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_the_bridge_rewires_every_v41_box_environment[fmbox]` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-005` | `math` | `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_the_bridge_rewires_every_v41_box_environment[nxcard]` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-006` | `math` | `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_the_bridge_rewires_every_v41_box_environment[nxdef]` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-007` | `math` | `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_the_bridge_rewires_every_v41_box_environment[nxerr]` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-008` | `math` | `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_the_bridge_rewires_every_v41_box_environment[nxprop]` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-009` | `math` | `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_the_bridge_rewires_every_v41_box_environment[nxstar]` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-010` | `math` | `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_the_bridge_rewires_every_v41_box_environment[nxthm]` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-011` | `math` | `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_the_bridge_rewires_every_v41_paragraph_macro[contreexemple]` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-012` | `math` | `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_the_bridge_rewires_every_v41_paragraph_macro[demonstration]` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-013` | `math` | `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_the_bridge_rewires_every_v41_paragraph_macro[exemple]` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-014` | `math` | `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_the_charter_loads_the_v6_bridge_and_can_be_asked_not_to` | **NO** | **YES** | YES | NO | Spécification onglets 16mm/padding 6mm |
| `FAIL-015` | `math` | `Mathematiques/manuel-maths/tests/test_legacy_latex_symbols.py::test_nexus_class_loads_amssymb_for_square_symbol` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-016` | `math` | `Mathematiques/manuel-maths/tests/test_legacy_latex_symbols.py::test_nexus_class_loads_amsthm_after_amsmath_for_qed` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-017` | `math` | `Mathematiques/manuel-maths/tests/test_legacy_latex_symbols.py::test_nexus_class_loads_common_assets_from_the_gabarits_directory` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-018` | `math` | `Mathematiques/manuel-maths/tests/test_margin_compositor_pdf.py::test_public_margin_components_use_only_the_shared_rail_adapter` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-019` | `math` | `Mathematiques/manuel-maths/tests/test_margin_ledger.py::test_xobject_links_remap_uri_lines_and_internal_goto_without_duplicates` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-020` | `math` | `Mathematiques/manuel-maths/tests/test_pdf_integrity.py::test_missing_asset_produces_warning_in_real_compilation` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-021` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_chaque_distracteur_porte_un_diagnostic_et_un_renvoi[TCOMPL-CALCULS-AIRES]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-022` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_chaque_distracteur_porte_un_diagnostic_et_un_renvoi[TCOMPL-CORRELATION-CAUSALITE]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-023` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_chaque_distracteur_porte_un_diagnostic_et_un_renvoi[TSPE-DERIVATION-CONVEXITE]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-024` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_chaque_distracteur_porte_un_diagnostic_et_un_renvoi[TSPE-GEOMETRIE-ESPACE]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-025` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_chaque_distracteur_porte_un_diagnostic_et_un_renvoi[TSPE-LOGARITHME]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-026` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_chaque_distracteur_porte_un_diagnostic_et_un_renvoi[TSPE-PRIMITIVES-EQDIFF]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-027` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_chaque_distracteur_porte_un_diagnostic_et_un_renvoi[TSPE-PROBABILITES]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-028` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_chaque_distracteur_porte_un_diagnostic_et_un_renvoi[TSPE-TRIGONOMETRIE]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-029` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_toutes_les_capacites_du_contrat_sont_interrogees[TCOMPL-ECHANTILLONNAGE]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-030` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_toutes_les_capacites_du_contrat_sont_interrogees[TCOMPL-INEGALITES]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-031` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_toutes_les_capacites_du_contrat_sont_interrogees[TCOMPL-INFERENCE-BAYESIENNE]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-032` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_toutes_les_capacites_du_contrat_sont_interrogees[TCOMPL-LOGARITHME-HISTORIQUE]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-033` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_toutes_les_capacites_du_contrat_sont_interrogees[TCOMPL-MODELES-EVOLUTION]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-034` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_toutes_les_capacites_du_contrat_sont_interrogees[TCOMPL-MODELES-FONCTION]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-035` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_toutes_les_capacites_du_contrat_sont_interrogees[TCOMPL-TEMPS-ATTENTE]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-036` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_toutes_les_capacites_du_contrat_sont_interrogees[TEXP-ARITHMETIQUE]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-037` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_toutes_les_capacites_du_contrat_sont_interrogees[TEXP-COMPLEXES-ALGEBRE-GEOMETRIE]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-038` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_toutes_les_capacites_du_contrat_sont_interrogees[TEXP-COMPLEXES-TRIGO-POLYNOMES]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-039` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_toutes_les_capacites_du_contrat_sont_interrogees[TEXP-GRAPHES]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-040` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_toutes_les_capacites_du_contrat_sont_interrogees[TEXP-MATRICES-MARKOV]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-041` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_toutes_les_capacites_du_contrat_sont_interrogees[TSPE-CALCUL-INTEGRAL]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-042` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_toutes_les_capacites_du_contrat_sont_interrogees[TSPE-COMBINATOIRE]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-043` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_toutes_les_capacites_du_contrat_sont_interrogees[TSPE-GEOMETRIE-ESPACE]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-044` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_toutes_les_capacites_du_contrat_sont_interrogees[TSPE-LOGARITHME]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-045` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_toutes_les_capacites_du_contrat_sont_interrogees[TSPE-PRIMITIVES-EQDIFF]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-046` | `math` | `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py::test_toutes_les_capacites_du_contrat_sont_interrogees[TSPE-PROBABILITES]` | **NO** | **YES** | NO | YES | Incomplétude capacités QCM |
| `FAIL-047` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_algorithm_review_receipt_matches_current_sources_before_sealing` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-048` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_all_review_receipts_match_current_governance_before_sealing` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-049` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_build_manifest_governance_uses_current_clean_base` | **YES** | **NO** | NO | NO | Dette gouvernance |
| `FAIL-050` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_cli_exposes_required_modes` | **YES** | **NO** | NO | NO | Dette gouvernance |
| `FAIL-051` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_contract_findings_are_exactly_the_ten_sealed_contract_reviews` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-052` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_counter_review_policy_migration_invalidates_exactly_six_receipts` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-053` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_dependency_graph_contains_bidirectional_help_correction_and_receipt` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-054` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_discover_sources_is_exact_and_1nsi_only` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-055` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_findings_only_differ_on_reattested_payload_or_provenance` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-056` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_historical_contract_receipt_remains_git_sealed` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-057` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_object_findings_exhaustively_cover_all_339_sources` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-058` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_policy_migration_invalidates_only_review_envelopes` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-059` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_policy_pins_official_and_contractual_sources` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-060` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_protocol_mutation_invalidates_all_dependency_digests` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-061` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_receipt_resolution_uses_real_source_stem_for_td[1NSI-TC-TD1-07_td1_station_meteo]` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-062` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_receipt_resolution_uses_real_source_stem_for_td[1NSI-TC-TD2-07_td2_classement_esport]` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-063` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_rejects_missing_and_duplicate_findings` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-064` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_scope_guard_pins_exact_sources_and_immutable_surfaces` | **YES** | **NO** | YES | NO | Spécification onglets 16mm/padding 6mm |
| `FAIL-065` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_verify_scope_rejects_changed_path_outside_allowlist` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-066` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_verify_scope_rejects_every_guard_drift[manifest]` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-067` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_verify_scope_rejects_every_guard_drift[pdf]` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-068` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_verify_scope_rejects_every_guard_drift[source_path]` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-069` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_verify_scope_rejects_every_guard_drift[source_status]` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-070` | `nsi` | `NSI/tests/test_1nsi_content_reviews.py::test_verify_scope_rejects_every_guard_drift[tnsi]` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-071` | `nsi` | `NSI/tests/test_1nsi_status_governance.py::test_1nsi_object_statuses_follow_execution_evidence` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-072` | `nsi` | `NSI/tests/test_assemble_book.py::test_collect_book_chapters_methodes_1nsi` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-073` | `nsi` | `NSI/tests/test_assemble_book.py::test_render_book_master_methodes_contains_one_chapter` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-074` | `nsi` | `NSI/tests/test_assemble_book.py::test_the_bridge_rewires_the_boxes_the_nsi_corpus_uses` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-075` | `nsi` | `NSI/tests/test_assemble_manuel.py::test_runtime_selection_covers_all_professor_objects_and_is_student_safe` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-076` | `nsi` | `NSI/tests/test_gates_corpus.py::test_amenagee_extract_avoids_lstinline_inside_tabular_cells` | **YES** | **NO** | YES | NO | Spécification onglets 16mm/padding 6mm |
| `FAIL-077` | `nsi` | `_` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-078` | `nsi` | `__` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-079` | `nsi` | `____` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-080` | `nsi` | `________` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-081` | `root` | `tests/test_baseline_qualification.py::test_materialization_plan_corrects_policy_entry_drift_after_materialization` | **YES** | **NO** | NO | NO | Dette gouvernance |
| `FAIL-082` | `root` | `tests/test_baseline_qualification.py::test_materialization_plan_preserves_history_and_emits_all_required_fields` | **YES** | **NO** | NO | NO | Dette gouvernance |
| `FAIL-083` | `root` | `tests/test_baseline_qualification.py::test_materialization_refuses_approved_set_drift_without_partial_payload` | **YES** | **NO** | NO | NO | Dette gouvernance |
| `FAIL-084` | `root` | `tests/test_baseline_qualification.py::test_repository_approved_set_has_exact_category_and_owner_counts` | **YES** | **NO** | NO | NO | Dette gouvernance |
| `FAIL-085` | `root` | `tests/test_baseline_qualification.py::test_repository_registry_excludes_prior_policy_from_current_policy` | **YES** | **NO** | NO | NO | Dette gouvernance |
| `FAIL-086` | `root` | `tests/test_build_manifest.py::test_versioned_build_producers_register_exact_1nsi_manual_surface` | **NO** | **YES** | NO | NO | Incompatibilité assertion |
| `FAIL-087` | `root` | `tests/test_charter_tab_spec_compliance.py::test_tab_font_size_is_6_pt[charte_path0]` | **NO** | **YES** | YES | NO | Spécification onglets 16mm/padding 6mm |
| `FAIL-088` | `root` | `tests/test_charter_tab_spec_compliance.py::test_tab_font_size_is_6_pt[charte_path1]` | **NO** | **YES** | YES | NO | Spécification onglets 16mm/padding 6mm |
| `FAIL-089` | `root` | `tests/test_charter_tab_spec_compliance.py::test_tab_length_minimum_is_16mm[charte_path0]` | **NO** | **YES** | YES | NO | Spécification onglets 16mm/padding 6mm |
| `FAIL-090` | `root` | `tests/test_charter_tab_spec_compliance.py::test_tab_length_minimum_is_16mm[charte_path1]` | **NO** | **YES** | YES | NO | Spécification onglets 16mm/padding 6mm |
| `FAIL-091` | `root` | `tests/test_charter_tab_spec_compliance.py::test_tab_length_padding_is_6mm[charte_path0]` | **NO** | **YES** | YES | NO | Spécification onglets 16mm/padding 6mm |
| `FAIL-092` | `root` | `tests/test_charter_tab_spec_compliance.py::test_tab_length_padding_is_6mm[charte_path1]` | **NO** | **YES** | YES | NO | Spécification onglets 16mm/padding 6mm |
| `FAIL-093` | `root` | `tests/test_inventory_collection.py::test_declared_assembler_allowlist_preserves_real_and_planned_engines` | **YES** | **NO** | NO | NO | Dette gouvernance |
| `FAIL-094` | `root` | `tests/test_inventory_collection.py::test_live_1nsi_runtime_selection_matches_declared_manual_assemblies` | **YES** | **NO** | NO | NO | Dette gouvernance |
| `FAIL-095` | `root` | `tests/test_inventory_collection.py::test_live_nsi_manual_declaration_covers_1nsi_and_tnsi` | **NO** | **YES** | NO | NO | Dette gouvernance |
| `FAIL-096` | `root` | `tests/test_inventory_collection.py::test_materialization_revalidations_use_only_the_owned_lock_identity` | **YES** | **NO** | NO | NO | Dette gouvernance |
| `FAIL-097` | `root` | `tests/test_inventory_collection.py::test_materialize_baseline_qualifications_check_is_read_only` | **YES** | **NO** | NO | NO | Dette gouvernance |
| `FAIL-098` | `root` | `tests/test_inventory_collection.py::test_real_harvest_candidates_never_produce_blocking_production_anomalies` | **YES** | **NO** | NO | NO | Dette gouvernance |
| `FAIL-099` | `root` | `tests/test_inventory_collection.py::test_real_reports_expose_known_exercise_contradictions` | **YES** | **NO** | NO | NO | Dette gouvernance |
| `FAIL-100` | `root` | `tests/test_inventory_collection.py::test_repository_baseline_is_frozen_schema_valid_and_gate_green` | **YES** | **NO** | NO | NO | Dette gouvernance |
| `FAIL-101` | `root` | `tests/test_inventory_collection.py::test_repository_build_applies_qualification_view_without_mutating_raw_anomalies` | **YES** | **NO** | NO | NO | Dette gouvernance |
