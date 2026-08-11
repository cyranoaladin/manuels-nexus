export PYTHONDONTWRITEBYTECODE=1
DELIVERED_ARCHIVE ?= dist/source_clean.tar.gz

audit: audit-core audit-metrics deliver-pedagogical-archive deliver-source-zip package-audit audit-extracted-source verify-delivery-archive

audit-idempotence:
	$(MAKE) audit
	test -z "$$(git status --short)"
	$(MAKE) audit
	test -z "$$(git status --short)"

generate-reports:
	python -m scripts.rebuild_inventory
	python -m scripts.check_program_coverage
	python -m scripts.generate_pedagogical_indexes
	python -m scripts.check_no_private_data
	python -m scripts.generate_qa_report
	python -m scripts.rebuild_inventory

check-generated-freshness:
	$(MAKE) generate-reports
	@echo "--- Freshness: git diff --exit-code on generated files ---"
	git diff --exit-code

check-legacy-freshness:
	python -m scripts.check_build_reports_freshness
	python -m scripts.check_qa_report_freshness
	python -m scripts.check_manifest_source_integrity

audit-core:
	python -m scripts.check_git_clean
	python -m scripts.check_repo_topology
	python -m scripts.check_audit_folder_policy
	python -m scripts.check_content_tree_policy
	python -m scripts.check_metadata
	python -m scripts.check_links
	python -m scripts.check_rag_config
	RAG_ENV_FILE=.env.rag.audit-core-missing python -m scripts.rag_smoke_test
	RAG_ENV_FILE=.env.rag.audit-core-missing python -m scripts.rag_diagnose_search_timeout
	python -m scripts.check_rag_collection_policy
	python -m scripts.check_rag_golden_examples_policy
	python -m scripts.check_rag_metadata_canonical_fields
	python -m scripts.check_no_secret_file_mutation_policy
	python -m scripts.check_agents_governance
	python -m scripts.check_skills_governance
	python -m scripts.check_program_coverage
	python -m scripts.generate_coverage_gap_action_plan
	python -m scripts.check_coverage_gap_action_plan
	python -m scripts.check_sources_catalog
	python -m scripts.check_sources_catalog_schema
	python -m scripts.generate_pedagogical_indexes
	python -m scripts.check_pedagogical_indexes
	python -m scripts.check_makefile_audit_policy
	python -m scripts.check_reports_policy
	python -m scripts.check_substance_anchors
	python -m scripts.check_contract_substance_quality
	python -m scripts.check_differentiation_distinctness
	python -m scripts.check_rendered_unit_artifacts --unit P05
	python -m scripts.check_rendered_unit_artifacts --unit T10
	python -m scripts.check_status_promotion_guard
	python -m scripts.check_drive_enrichment_traceability_portable
	python -m scripts.check_drive_action_plan_completeness
	python -m scripts.check_no_coverage_from_sheets_only
	python -m scripts.check_no_private_data
	python -m scripts.check_no_committed_secrets
	python -m scripts.check_no_placeholders_docs
	python -m scripts.check_no_placeholders_code
	python -m scripts.check_closed_error_classes
	python -m scripts.check_eval_bareme_pairing
	python -m scripts.run_python_tests

audit-metrics:
	-python -m scripts.check_required_sections
	-python -m scripts.check_document_depth
	-python -m scripts.check_document_style
	python -m scripts.check_full_sequence_resource_matrix
	python -m scripts.check_full_notional_resource_matrix
	python -m scripts.check_official_program_capacity_coverage_matrix
	python -m scripts.check_session_level_planning
	python -m scripts.check_session_duration_consistency
	python -m scripts.check_session_monthly_total
	python -m scripts.check_session_project_hours
	python -m scripts.check_session_week_calendar_consistency
	python -m scripts.check_session_specificity

rag-smoke-required:
	RAG_SMOKE_STRICT=1 python -m scripts.rag_smoke_test

audit-local:
	python -m scripts.check_git_clean
	python -m scripts.check_audit_folder_policy
	python -m scripts.check_content_tree_policy
	python -m scripts.check_gate_policy_consistency
	python -m scripts.check_metadata
	python -m scripts.check_links
	python -m scripts.check_no_private_data
	python -m scripts.check_no_committed_secrets
	python -m scripts.check_no_placeholders_docs
	python -m scripts.check_no_placeholders_code
	python -m scripts.cleanup_python_artifacts
	python -m scripts.check_no_build_artifacts_in_index
	python -m scripts.check_uploaded_archive_policy
	python -m scripts.check_no_global_archive_in_delivery_context
	-python -m scripts.check_required_sections
	-python -m scripts.check_document_depth
	python -m scripts.check_qcm_schema
	-python -m scripts.check_document_style
	python -m scripts.check_progression_calendar_alignment
	python -m scripts.check_project_quarter_requirement
	python -m scripts.check_progression_project_consistency
	python -m scripts.check_monthly_load_balance
	python -m scripts.check_session_level_planning
	python -m scripts.check_session_duration_consistency
	python -m scripts.check_session_monthly_total
	python -m scripts.check_session_project_hours
	python -m scripts.check_session_week_calendar_consistency
	python -m scripts.check_session_specificity
	python -m scripts.check_session_referenced_files_exist
	python -m scripts.check_missing_register_actionability
	python -m scripts.check_missing_register_semantic_consistency
	python -m scripts.check_register_no_hidden_operational_debt
	python -m scripts.check_document_naming_conventions
	python -m scripts.check_first_batch_document_quality
	python -m scripts.check_first_batch_alignment
	python -m scripts.check_first_batch_tp_assets
	python -m scripts.check_support_substance
	python -m scripts.check_no_line_padding
	python -m scripts.check_full_sequence_resource_matrix
	python -m scripts.check_full_notional_resource_matrix
	python -m scripts.check_official_program_capacity_coverage_matrix
	python -m scripts.check_program_coverage
	python -m scripts.check_capacity_status_ladder
	python -m scripts.check_course_explanatory_quality
	python -m scripts.check_sequence_pedagogical_coherence
	python -m scripts.check_paper_tp_justification
	MAX_EXECUTABLE_TP_OPPORTUNITIES=8 python -m scripts.check_tp_executable_opportunity
	python -m scripts.check_session_to_resource_alignment
	python -m scripts.check_session_classroom_operationality
	python -m scripts.check_human_review_register
	python -m scripts.check_human_review_wave_plan
	python -m scripts.check_sql_query_result_consistency
	python -m scripts.check_graph_algorithm_trace_consistency
	python -m scripts.check_tree_bst_invariant_consistency
	python -m scripts.check_network_packet_trace_consistency
	python -m scripts.check_dynamic_programming_recurrence_consistency
	python -m scripts.check_boyer_moore_trace_consistency
	python -m scripts.check_generated_template_residue
	python -m scripts.check_question_capacity_alignment
	python -m scripts.check_support_pedagogical_depth
	python -m scripts.check_substance_anchors
	python -m scripts.check_contract_substance_quality
	python -m scripts.check_differentiation_distinctness
	python -m scripts.check_rendered_unit_artifacts --unit P05
	python -m scripts.check_rendered_unit_artifacts --unit T10
	python -m scripts.check_session_operationalization_plan
	python -m scripts.check_sequence_pack_consistency
	python -m scripts.check_csv_numeric_fields_are_parseable
	python -m scripts.check_p05_pipeline_consistency
	python -m scripts.check_p05_semantic_consistency
	python -m scripts.check_p05_expected_outputs_are_explicit
	python -m scripts.check_course_sheet_exercise_answer_count
	python -m scripts.check_no_duplicate_capacity_lines
	python -m scripts.check_p04_key_consistency
	python -m scripts.check_t18_trace_table_quality
	python -m scripts.check_paper_tp_contract
	python -m scripts.check_no_token_only_validation
	python -m scripts.check_no_generic_scaffold_overuse
	python -m scripts.check_student_supports_no_scaffold_language
	python -m scripts.check_corrected_answers_are_concrete
	python -m scripts.check_tp_text_asset_alignment
	python -m scripts.check_sequence_capacity_alignment
	timeout 90 python -m scripts.check_tp_pedagogical_assets_runtime
	python -m scripts.check_sequence_contracts
	python -m scripts.check_local_drive_traceability
	python -m scripts.check_drive_integration_plan
	python -m scripts.check_drive_action_plan_completeness
	python -m scripts.check_drive_enrichment_traceability
	python -m scripts.check_ready_supports_required_sections
	python -m scripts.check_ready_supports_depth
	python -m scripts.check_ready_session_operationality
	python -m scripts.check_course_sheets_coverage
	python -m scripts.check_course_sheets_quality
	python -m scripts.check_course_sheets_alignment
	python -m scripts.check_course_sheets_substance
	python -m scripts.check_course_sheet_linked_resources_exist
	python -m scripts.check_course_sheets_no_template_abuse
	python -m scripts.check_course_sheet_readiness
	python -m scripts.check_course_sheet_readiness_strict
	python -m scripts.check_linked_td_quality
	python -m scripts.check_linked_td_substance
	python -m scripts.check_linked_evaluation_quality
	python -m scripts.check_linked_evaluation_substance
	python -m scripts.check_no_operational_scope_hardcoding
	python -m scripts.check_operational_supports_no_indicative_debt
	python -m scripts.check_operational_readiness_quality_coupling
	python -m scripts.check_evaluation_distribution
	python -m scripts.check_teacher_docs_depth
	python -m scripts.check_validated_documents_quality_gates
	python -m scripts.check_program_yaml_atomicity
	$(MAKE) check-legacy-freshness
	python -m scripts.check_archive_portability
	python -m scripts.check_sequence_completeness
	python -m scripts.check_course_internal_coherence
	python -m scripts.check_td_corrige_alignment
	python -m scripts.check_tp_test_alignment
	python -m scripts.check_evaluation_bareme_alignment
	python -m scripts.check_learning_objectives_assessed
	python -m scripts.check_differentiation_quality
	python -m scripts.check_scientific_claims_review
	python -m scripts.check_program_capacity_evidence_depth
	python -m scripts.check_teacher_corrections_alignment
	python -m scripts.check_coverage_evidence
	python -m scripts.check_no_coverage_from_sheets_only
	python -m scripts.run_python_tests
	python -m scripts.check_quality_gates
	python -m scripts.check_git_clean

audit-source:
	python -m scripts.cleanup_python_artifacts
	python -m scripts.check_archive_portability
	python -m scripts.check_session_duration_consistency
	python -m scripts.check_session_monthly_total
	python -m scripts.check_session_project_hours
	python -m scripts.check_session_referenced_files_exist
	python -m scripts.check_missing_register_actionability
	python -m scripts.check_missing_register_semantic_consistency
	python -m scripts.check_register_no_hidden_operational_debt
	python -m scripts.check_document_naming_conventions
	python -m scripts.check_session_specificity
	python -m scripts.check_session_week_calendar_consistency
	python -m scripts.check_evaluation_distribution
	python -m scripts.check_metadata
	python -m scripts.check_links
	python -m scripts.check_no_private_data
	python -m scripts.check_no_committed_secrets
	python -m scripts.check_no_placeholders_docs
	python -m scripts.check_no_placeholders_code
	python -m scripts.check_no_build_artifacts_in_index
	-python -m scripts.check_required_sections
	-python -m scripts.check_document_depth
	python -m scripts.check_qcm_schema
	-python -m scripts.check_document_style

audit-extracted-source:
	@if test -d .git; then PYTHONDONTWRITEBYTECODE=1 python -m scripts.run_audit_extracted_source; else $(MAKE) audit-extracted-source-local; fi

audit-extracted-source-local:
	python -m scripts.cleanup_python_artifacts
	python -m scripts.check_audit_folder_policy
	python -m scripts.check_content_tree_policy
	python -m scripts.check_gate_policy_consistency
	python -m scripts.check_metadata
	python -m scripts.check_qcm_schema
	timeout 30 python -m scripts.check_session_referenced_files_exist
	timeout 30 python -m scripts.check_first_batch_document_quality
	timeout 30 python -m scripts.check_first_batch_alignment
	python -m scripts.check_first_batch_tp_assets
	timeout 30 python -m scripts.check_support_substance
	python -m scripts.check_no_line_padding
	timeout 30 python -m scripts.check_full_sequence_resource_matrix
	timeout 30 python -m scripts.check_full_notional_resource_matrix
	timeout 30 python -m scripts.check_official_program_capacity_coverage_matrix
	timeout 30 python -m scripts.check_program_coverage
	timeout 30 python -m scripts.check_capacity_status_ladder
	timeout 30 python -m scripts.check_course_explanatory_quality
	timeout 30 python -m scripts.check_sequence_pedagogical_coherence
	timeout 30 python -m scripts.check_paper_tp_justification
	MAX_EXECUTABLE_TP_OPPORTUNITIES=8 timeout 30 python -m scripts.check_tp_executable_opportunity
	timeout 30 python -m scripts.check_session_to_resource_alignment
	timeout 30 python -m scripts.check_session_classroom_operationality
	timeout 30 python -m scripts.check_human_review_register
	timeout 30 python -m scripts.check_human_review_wave_plan
	python -m scripts.check_sql_query_result_consistency
	python -m scripts.check_graph_algorithm_trace_consistency
	python -m scripts.check_tree_bst_invariant_consistency
	python -m scripts.check_network_packet_trace_consistency
	python -m scripts.check_dynamic_programming_recurrence_consistency
	python -m scripts.check_boyer_moore_trace_consistency
	python -m scripts.check_generated_template_residue
	python -m scripts.check_question_capacity_alignment
	timeout 30 python -m scripts.check_support_pedagogical_depth
	timeout 30 python -m scripts.check_substance_anchors
	timeout 30 python -m scripts.check_contract_substance_quality
	timeout 30 python -m scripts.check_differentiation_distinctness
	timeout 30 python -m scripts.check_rendered_unit_artifacts --unit P05
	timeout 30 python -m scripts.check_session_operationalization_plan
	python -m scripts.check_sequence_pack_consistency
	python -m scripts.check_csv_numeric_fields_are_parseable
	python -m scripts.check_p05_pipeline_consistency
	python -m scripts.check_p05_semantic_consistency
	python -m scripts.check_p05_expected_outputs_are_explicit
	python -m scripts.check_course_sheet_exercise_answer_count
	python -m scripts.check_no_duplicate_capacity_lines
	python -m scripts.check_p04_key_consistency
	python -m scripts.check_t18_trace_table_quality
	python -m scripts.check_paper_tp_contract
	python -m scripts.check_no_token_only_validation
	python -m scripts.check_no_generic_scaffold_overuse
	python -m scripts.check_student_supports_no_scaffold_language
	python -m scripts.check_corrected_answers_are_concrete
	python -m scripts.check_tp_text_asset_alignment
	python -m scripts.check_sequence_capacity_alignment
	timeout 90 python -m scripts.check_tp_pedagogical_assets_runtime
	python -m scripts.check_sequence_contracts
	python -m scripts.check_drive_enrichment_traceability_portable
	python -m scripts.check_drive_action_plan_completeness
	python -m scripts.check_drive_trace_no_absolute_local_paths
	timeout 30 python -m scripts.check_ready_supports_required_sections
	timeout 30 python -m scripts.check_ready_supports_depth
	timeout 30 python -m scripts.check_ready_session_operationality
	python -m scripts.check_course_sheets_coverage
	python -m scripts.check_course_sheets_quality
	python -m scripts.check_course_sheets_alignment
	python -m scripts.check_course_sheets_substance
	python -m scripts.check_course_sheet_linked_resources_exist
	python -m scripts.check_course_sheets_no_template_abuse
	python -m scripts.check_course_sheet_readiness
	python -m scripts.check_course_sheet_readiness_strict
	python -m scripts.check_linked_td_quality
	python -m scripts.check_linked_td_substance
	python -m scripts.check_linked_evaluation_quality
	python -m scripts.check_linked_evaluation_substance
	python -m scripts.check_no_operational_scope_hardcoding
	python -m scripts.check_operational_supports_no_indicative_debt
	timeout 30 python -m scripts.check_operational_readiness_quality_coupling
	python -m scripts.check_no_private_data
	python -m scripts.check_no_placeholders_docs
	python -m scripts.check_no_build_artifacts_in_index
	python -m scripts.check_no_sensitive_drive_in_source_clean
	python -m scripts.check_no_coverage_from_sheets_only

package-audit:
	python -m scripts.cleanup_python_artifacts
	python -m scripts.build_source_archive
	python -m scripts.check_packaging_mode
	python -m scripts.check_archive_portability
	python -m scripts.check_no_build_artifacts_in_index
	python -m scripts.check_uploaded_archive_policy
	python -m scripts.check_no_sensitive_drive_in_source_clean
	python -m scripts.check_no_global_archive_in_delivery_context

verify-delivery-archive:
	DELIVERED_ARCHIVE="$(DELIVERED_ARCHIVE)" python -m scripts.check_delivered_archive_exactly_source_clean

deliver-pedagogical-archive:
	python -m scripts.build_source_archive
	python -m scripts.check_packaging_mode
	DELIVERED_ARCHIVE=dist/source_clean.tar.gz python -m scripts.check_delivered_archive_exactly_source_clean
	python -m scripts.check_no_global_archive_in_delivery_context
	@echo "LIVRABLE_PEDAGOGIQUE=dist/source_clean.tar.gz"

deliver-source-zip:
	python -m scripts.build_source_zip
	@echo "ZIP_EXPLOITABLE=dist/nsi-enseignement_source_clean.zip"

render-s01:
	python -m scripts.render_sequence premiere/sequences/s01_representation_donnees

render-unit:
	python -m scripts.render_unit --unit "$(U)"

judge:
	test -n "$(U)"
	python -m scripts.substance_judge --unit "$(U)" --level premiere --offline-fixture "tests/fixtures/substance_judge/$(U).json" --output "01_build_reports/$(U)_substance_review.json"
	python -m scripts.check_substance_anchors "01_build_reports/$(U)_substance_review.json" --repo-root .

render-substance-report:
	test -n "$(V)"
	mkdir -p 01_build_reports/substance_reports
	python -m scripts.render_substance_report --verdict "$(V)" --repo-root . --out-md 01_build_reports/substance_reports/$$(basename "$(V)" .json).md --out-html 01_build_reports/substance_reports/$$(basename "$(V)" .json).html

release-audit:
	python -m scripts.cleanup_python_artifacts
	python -m scripts.check_git_clean
	python -m scripts.check_drive_mapping_release
	python -m scripts.check_no_needs_review_for_release
	python -m scripts.check_no_absent_coverage_for_release
	python -m scripts.check_no_teacher_content_in_student_export
	python -m scripts.check_validated_statuses

pre-release-audit:
	python -m scripts.check_git_clean
	python -m scripts.check_quality_gates
	python -m scripts.check_archive_portability
	@echo "qualité interne contrôlée"
	@echo "publication bloquée tant que make release-audit échoue"
