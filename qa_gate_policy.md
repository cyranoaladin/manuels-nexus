# Politique des gates QA

## Principe

Les gates bloquants doivent rester bornés, explicites et défendables. Le noyau
peut dépasser l'ancien seuil historique de 20 scripts lorsque le cahier des
charges impose des verrous structurels supplémentaires, mais il doit rester sous
un plafond documenté de 40 gates bloquants hors tests. Les scripts de comptage,
de longueur, de présence de sections ou de métrique documentaire restent utiles,
mais ils ne doivent pas remplacer le jugement de substance.

## Classes

| Script | Classe | Rôle |
| --- | --- | --- |
| scripts/check_git_clean.py | blocking_structure | dépôt propre avant audit |
| scripts/check_repo_topology.py | blocking_structure | topologie canonique, miroirs locaux et archives livrables |
| scripts/check_audit_folder_policy.py | blocking_structure | `/AUDIT` hors corpus pédagogique |
| scripts/check_content_tree_policy.py | blocking_structure | arbre canonique `supports/` |
| scripts/check_rag_config.py | blocking_structure | configuration RAG sans secret et cible `nsi_corpus` |
| scripts/rag_smoke_test.py | blocking_structure | skip propre sans config, smoke réel avec `.env.rag` |
| scripts/rag_diagnose_search_timeout.py | blocking_structure | diagnostic timeout RAG sans secret, skip propre sans config |
| scripts/check_rag_collection_policy.py | blocking_structure | séparation stricte `nsi_corpus` / `rag_education` |
| scripts/check_rag_golden_examples_policy.py | blocking_structure | pilotes hors preuves internes |
| scripts/check_rag_metadata_canonical_fields.py | blocking_structure | métadonnées RAG canoniques `section_anchor` / `capacity_ids` |
| scripts/check_no_secret_file_mutation_policy.py | blocking_privacy | interdit les mutations directes de fichiers secrets locaux |
| scripts/check_agents_governance.py | blocking_structure | doctrine AGENTS minimale |
| scripts/check_skills_governance.py | blocking_structure | compétences SKILLS minimales |
| scripts/check_metadata.py | blocking_structure | métadonnées minimales |
| scripts/check_links.py | blocking_structure | liens internes |
| scripts/check_no_private_data.py | blocking_privacy | données personnelles |
| scripts/check_no_committed_secrets.py | blocking_privacy | secrets ou clés committés |
| scripts/check_no_placeholders_docs.py | blocking_structure | placeholders documents |
| scripts/check_no_placeholders_code.py | blocking_structure | placeholders code |
| scripts/check_no_build_artifacts_in_index.py | blocking_structure | artefacts suivis |
| scripts/check_uploaded_archive_policy.py | blocking_structure | politique archives |
| scripts/check_program_coverage.py | blocking_structure | indicateur central de couverture documentaire |
| scripts/generate_coverage_gap_action_plan.py | blocking_structure | régénère le plan d'écarts depuis les absences réelles |
| scripts/check_coverage_gap_action_plan.py | blocking_structure | chaque absence a une action |
| scripts/check_sources_catalog.py | blocking_structure | sources classées avant usage |
| scripts/check_sources_catalog_schema.py | blocking_structure | schéma actionnable du catalogue sources |
| scripts/generate_pedagogical_indexes.py | blocking_structure | régénère les index pédagogiques |
| scripts/check_pedagogical_indexes.py | blocking_structure | index pédagogiques générés |
| scripts/check_makefile_audit_policy.py | blocking_structure | cohérence Makefile / politique QA |
| scripts/check_reports_policy.py | blocking_structure | rapports `reports/lot*/` hors corpus et sous seuil |
| scripts/check_substance_anchors.py | blocking_substance | garde-fou mécanique du juge de substance |
| scripts/check_status_promotion_guard.py | blocking_substance | interdit toute promotion sans verdict A et confirmation humaine |
| scripts/check_contract_substance_quality.py | blocking_substance | contrats de séquence |
| scripts/check_differentiation_distinctness.py | blocking_substance | différenciation non copiée |
| scripts/check_rendered_unit_artifacts.py | blocking_structure | rendu charté pilote |
| scripts/check_drive_enrichment_traceability_portable.py | blocking_privacy | traçabilité Drive portable |
| scripts/check_drive_action_plan_completeness.py | blocking_privacy | plan Drive restant |
| scripts/check_no_coverage_from_sheets_only.py | blocking_structure | pas de fausse couverture |
| scripts/check_closed_error_classes.py | blocking_substance | classes d'erreur fermées (TCO non terminal, localStorage domaine, glouton trivial, rotation Q/R) |
| scripts/check_eval_bareme_pairing.py | blocking_substance | appariement évaluation↔barème par slug ou capacités frontmatter |
| scripts/run_python_tests.py | blocking_tests | tests Python |

## Informational Metrics

Les scripts de matrices, comptages de lignes, sections requises, profondeur approximative, ratios TP papier/exécutable et listes de séances sont des `informational_metric` sauf lorsqu'un autre gate bloquant s'appuie explicitement sur une preuve de substance.

## Cibles Makefile

`make audit-core` exécute le noyau bloquant documenté ci-dessus. Il peut s'exécuter
en clone propre : si `.env.rag` est absent, le smoke RAG doit afficher
`RAG_SMOKE_TEST_SKIPPED_NO_CONFIG` et ne pas ouvrir le réseau.

`make rag-smoke-required` exécute le smoke RAG réel avec `.env.rag`. Cette cible
doit échouer tant que `/search` authentifié time out ; elle ne fait pas partie du
mode clone-propre.

`make audit-metrics` exécute les métriques indicatives et rapports de profondeur.
Ces métriques peuvent signaler une dette documentaire, mais elles ne prouvent pas
une validation pédagogique.

`make audit` exécute `audit-core` puis `audit-metrics`.

## Divergence documentée check_quality_gates.py / audit-core

`scripts/check_quality_gates.py` conserve quelques contrôles historiques
supplémentaires (`check_metadata.py`, `check_links.py`,
`check_no_build_artifacts_in_index.py`, `check_uploaded_archive_policy.py`) pour
compatibilité CI. Cette divergence est volontaire : elle renforce le noyau, mais
ne change pas la règle pédagogique principale (`covered = 0`, pas de promotion
sans revue humaine).

## Frontière clone-propre / Drive local

### Gates clone-propre

Les gates de clone-propre doivent fonctionner dans une archive source ou un checkout CI sans miroir Drive local. Ils ne déréférencent pas `Documents_DRIVE` et s'appuient uniquement sur les traces publiables suivies dans Git. Sont notamment classés clone-propre : `scripts/check_drive_enrichment_traceability_portable.py`, `scripts/check_drive_action_plan_completeness.py`, `scripts/check_status_promotion_guard.py`, `scripts/check_substance_anchors.py` et l'agrégateur `scripts/check_quality_gates.py`.

### Gates Drive-requis

Les gates Drive-requis exigent explicitement un miroir `Documents_DRIVE` réel, non vide, adjacent au dépôt ou désigné par `NSI_DOCUMENTS_DRIVE_ROOT`. Ils doivent échouer bruyamment si ce dossier est absent ou vide afin d'éviter un passage au vert par vacuité. Sont classés Drive local : `scripts/check_drive_enrichment_traceability.py`, `scripts/check_local_drive_traceability.py`, `scripts/drive_local_inventory.py` et `scripts/drive_resource_triage.py`.

## Legacy

Les anciens scripts `check_required_sections.py`, `check_document_depth.py` et `check_document_style.py` restent consultables, mais ne sont pas des preuves de validation pédagogique.
