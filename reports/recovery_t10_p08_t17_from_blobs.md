# Reconstruction depuis blobs — T10/P08/T17

## 1. Contexte

- Base de départ : `origin/main` à `b34c8934a65619de48423b4dc54e9d0f19dc55ab`.
- Branche de récupération : `recovery/t10-p08-t17-from-blobs`.
- Rapport forensique utilisé : copie temporaire du rapport `forensic_recovery_t10_p08_t17.md`.
- Archive forensique hors dépôt, datée du 13 juillet 2026 : `NSI-unreachable-objects.tar.gz` (19 445 786 octets).
- Nombre de fichiers restaurés depuis blobs : 44.
- Nombre d’artefacts régénérés : 18.

## 2. Fichiers restaurés

| Chemin | Blob attendu | Blob restauré | Statut |
|---|---|---|---|
| `03_progressions/fiches_cours/terminale/T10/T10_fiche_cours_sql_insert_update_delete.md` | `3cd19b53c5f10cd5be11a9b017c5a2128a8bbfe8` | `3cd19b53c5f10cd5be11a9b017c5a2128a8bbfe8` | CONFORME |
| `03_progressions/supports/contracts/T10_contract.yml` | `80be7235a9bf10a0d4984f12c641f7c8eb25a13d` | `80be7235a9bf10a0d4984f12c641f7c8eb25a13d` | CONFORME |
| `03_progressions/supports/contracts/T17_contract.yml` | `274723b38f8509642a6de4d05d6dcbee38140a10` | `274723b38f8509642a6de4d05d6dcbee38140a10` | CONFORME |
| `03_progressions/supports/premiere/P08/P08_bareme_html_css_dom.md` | `c705e2093f4fd7673e6e23fc8e849dcf0d7befb9` | `c705e2093f4fd7673e6e23fc8e849dcf0d7befb9` | CONFORME |
| `03_progressions/supports/premiere/P08/P08_bareme_http_get_post_formulaires.md` | `991cca2467748951f0c384dea5ba054087690e02` | `991cca2467748951f0c384dea5ba054087690e02` | CONFORME |
| `03_progressions/supports/premiere/P08/P08_bareme_web_http_dom_formulaires.md` | `0e073bc63de766f568966b4256453395da1211d4` | `0e073bc63de766f568966b4256453395da1211d4` | CONFORME |
| `03_progressions/supports/premiere/P08/P08_corrige_html_css_dom.md` | `1b2104c11c86cc15a62a15dc1d01b23b4e1f29c8` | `1b2104c11c86cc15a62a15dc1d01b23b4e1f29c8` | CONFORME |
| `03_progressions/supports/premiere/P08/P08_corrige_http_get_post_formulaires.md` | `ef26e0b71f30f8c252c4e4fc78e409cb3a3b09f6` | `ef26e0b71f30f8c252c4e4fc78e409cb3a3b09f6` | CONFORME |
| `03_progressions/supports/premiere/P08/P08_corrige_web_http_dom_formulaires.md` | `4f235a5ecb4fcd9a0dc87c2538600dbfe1ebc4f3` | `4f235a5ecb4fcd9a0dc87c2538600dbfe1ebc4f3` | CONFORME |
| `03_progressions/supports/premiere/P08/P08_evaluation_html_css_dom.md` | `fc80058dd2a09a209722249816a9739d9fc997c7` | `fc80058dd2a09a209722249816a9739d9fc997c7` | CONFORME |
| `03_progressions/supports/premiere/P08/P08_evaluation_http_get_post_formulaires.md` | `9ff1c643f2d71c485e1e84a741e802ff1ad1ab40` | `9ff1c643f2d71c485e1e84a741e802ff1ad1ab40` | CONFORME |
| `03_progressions/supports/terminale/T10/T10_TD_sql_insert_update_delete.md` | `808d4cc492b724b051e09051e3ac3dca1a0ae878` | `808d4cc492b724b051e09051e3ac3dca1a0ae878` | CONFORME |
| `03_progressions/supports/terminale/T10/T10_TD_sql_select_where_join.md` | `e9251f4ff7ef1255cbb0f8a835c2f9c18693edd9` | `e9251f4ff7ef1255cbb0f8a835c2f9c18693edd9` | CONFORME |
| `03_progressions/supports/terminale/T10/T10_bareme_sql_select_where_join.md` | `33abbe8045e3975bae9533bdd8c17a2a0065bdbe` | `33abbe8045e3975bae9533bdd8c17a2a0065bdbe` | CONFORME |
| `03_progressions/supports/terminale/T10/T10_corrige_sql_select_where_join.md` | `75facf2984739b4f0226433316ad7536b98c9dab` | `75facf2984739b4f0226433316ad7536b98c9dab` | CONFORME |
| `03_progressions/supports/terminale/T10/T10_cours_sql_select_where_join.md` | `7c942ef29e0d95b3805e29ce68504deae404d375` | `7c942ef29e0d95b3805e29ce68504deae404d375` | CONFORME |
| `03_progressions/supports/terminale/T10/T10_evaluation_sql_insert_update_delete.md` | `13a612ceec4a22bc5a4773edf2777426e3756b68` | `13a612ceec4a22bc5a4773edf2777426e3756b68` | CONFORME |
| `03_progressions/supports/terminale/T10/T10_evaluation_sql_select_where_join.md` | `76465f1c7867bb1d30af606fb87f3b0fb954c560` | `76465f1c7867bb1d30af606fb87f3b0fb954c560` | CONFORME |
| `03_progressions/supports/terminale/T10/T10_remediation_sql_select_where_join.md` | `2e19d9db74bdbd298fceb5bfd74dcd7427b8959c` | `2e19d9db74bdbd298fceb5bfd74dcd7427b8959c` | CONFORME |
| `03_progressions/supports/terminale/T10/T10_tp_sql_select_where_join.md` | `69a3adcf9f21cfd50ae258a4c41e92ebde419eb5` | `69a3adcf9f21cfd50ae258a4c41e92ebde419eb5` | CONFORME |
| `03_progressions/supports/terminale/T10/T10_trace_sql_select_where_join.md` | `aaf9a4607cb23c28ac5fe75c3feafc3f0e84c944` | `aaf9a4607cb23c28ac5fe75c3feafc3f0e84c944` | CONFORME |
| `03_progressions/supports/terminale/T10/T10_version_amenagee_sql_select_where_join.md` | `48f7fb23f04082e9b2c67a449830730df4868829` | `48f7fb23f04082e9b2c67a449830730df4868829` | CONFORME |
| `03_progressions/supports/terminale/T10/code/T10_corrige_professeur_sql_select_where_join.py` | `11459671d306dbf10605b0ff9e64befc47b162e4` | `11459671d306dbf10605b0ff9e64befc47b162e4` | CONFORME |
| `03_progressions/supports/terminale/T10/code/T10_starter_sql_select_where_join.py` | `405713df39d366923a42f28840628774004f72d5` | `405713df39d366923a42f28840628774004f72d5` | CONFORME |
| `03_progressions/supports/terminale/T10/code/T10_tests_attendus_sql_select_where_join.py` | `4f78eccd721b84870bb9bfe58ef2f5ae0f678cd8` | `4f78eccd721b84870bb9bfe58ef2f5ae0f678cd8` | CONFORME |
| `03_progressions/supports/terminale/T17/T17_TD_programmation_dynamique.md` | `8a9c965d8741c1570c5c846276b5818ab3370bea` | `8a9c965d8741c1570c5c846276b5818ab3370bea` | CONFORME |
| `03_progressions/supports/terminale/T17/T17_bareme_programmation_dynamique.md` | `773f9782c4819de4706a6df8021d1b8498407ebb` | `773f9782c4819de4706a6df8021d1b8498407ebb` | CONFORME |
| `03_progressions/supports/terminale/T17/T17_corrige_programmation_dynamique.md` | `e6ebe8718e52bae465b43a9199bd90a7443165c4` | `e6ebe8718e52bae465b43a9199bd90a7443165c4` | CONFORME |
| `03_progressions/supports/terminale/T17/T17_cours_programmation_dynamique.md` | `29a306eefb98763799a601f008ab066cfadc6888` | `29a306eefb98763799a601f008ab066cfadc6888` | CONFORME |
| `03_progressions/supports/terminale/T17/T17_evaluation_programmation_dynamique.md` | `32da00870303e090275e69871c4c2bd01e9c3d17` | `32da00870303e090275e69871c4c2bd01e9c3d17` | CONFORME |
| `03_progressions/supports/terminale/T17/T17_remediation_programmation_dynamique.md` | `cc4078ff0c693093b8b2d25c613833307fdc3b7e` | `cc4078ff0c693093b8b2d25c613833307fdc3b7e` | CONFORME |
| `03_progressions/supports/terminale/T17/T17_tp_programmation_dynamique.md` | `3f1785e7addbcde5cbb3e7f3537798a473900c5a` | `3f1785e7addbcde5cbb3e7f3537798a473900c5a` | CONFORME |
| `03_progressions/supports/terminale/T17/T17_trace_programmation_dynamique.md` | `3a9af21aab3dea2f8f71a53565d0cc3a41b80854` | `3a9af21aab3dea2f8f71a53565d0cc3a41b80854` | CONFORME |
| `03_progressions/supports/terminale/T17/T17_version_amenagee_programmation_dynamique.md` | `bd7a1d95c7eb042375148e00ddf14a6a70a6a5e5` | `bd7a1d95c7eb042375148e00ddf14a6a70a6a5e5` | CONFORME |
| `03_progressions/supports/terminale/T17/code/T17_corrige_professeur_programmation_dynamique.py` | `fd0dbad9d5689312dfbe7a4da6a1c6506ff0813f` | `fd0dbad9d5689312dfbe7a4da6a1c6506ff0813f` | CONFORME |
| `03_progressions/supports/terminale/T17/code/T17_starter_programmation_dynamique.py` | `6a257777edbb3a4831cf07a06b3e44deaa1feeef` | `6a257777edbb3a4831cf07a06b3e44deaa1feeef` | CONFORME |
| `03_progressions/supports/terminale/T17/code/T17_tests_attendus_programmation_dynamique.py` | `563648c25763a22cbcbb61ab2fc7b4b292b103f1` | `563648c25763a22cbcbb61ab2fc7b4b292b103f1` | CONFORME |
| `human_review_register.csv` | `57f753ea261f805c6c1b8011c0f0d11630499e08` | `57f753ea261f805c6c1b8011c0f0d11630499e08` | CONFORME |
| `reports/excellence_editorial_review_nsi.md` | `5eb84b9efc43eaa9dc69151d139644b6f933be14` | `5eb84b9efc43eaa9dc69151d139644b6f933be14` | CONFORME |
| `reports/excellence_remediation_progress.md` | `6fd80fc56d4bc4167dbb76650ece5cf65fbbd789` | `6fd80fc56d4bc4167dbb76650ece5cf65fbbd789` | CONFORME |
| `scripts/check_sql_query_result_consistency.py` | `46acc5893c38b921d44cfa1e8f960629a8b1241b` | `46acc5893c38b921d44cfa1e8f960629a8b1241b` | CONFORME |
| `tests/test_excellence_remediation_regressions.py` | `f4babfd84a674d581f1fab73e80079883c2c7e24` | `f4babfd84a674d581f1fab73e80079883c2c7e24` | CONFORME |
| `tests/test_executable_quality_controls.py` | `781e75ffeb3d89718d73db4049a440f2ed068917` | `781e75ffeb3d89718d73db4049a440f2ed068917` | CONFORME |
| `tests/test_notional_and_disciplinary_controls.py` | `c179322e8f61cd982b21ba1eb56deea0fa684c49` | `c179322e8f61cd982b21ba1eb56deea0fa684c49` | CONFORME |

Les 44 empreintes ont été recalculées avec `git hash-object` après écriture ; aucune divergence n’a été détectée.

## 3. Artefacts régénérés

| Fichier | Statut |
|---|---|
| `INDEX.md` | RÉGÉNÉRÉ |
| `INDEX_BY_AUDIENCE.md` | RÉGÉNÉRÉ |
| `INDEX_BY_CAPACITY.md` | RÉGÉNÉRÉ |
| `INDEX_BY_CHAPTER.md` | RÉGÉNÉRÉ |
| `INDEX_BY_DOCUMENT_TYPE.md` | RÉGÉNÉRÉ |
| `INDEX_BY_DOMAIN.md` | RÉGÉNÉRÉ |
| `INDEX_BY_LEVEL.md` | RÉGÉNÉRÉ |
| `INDEX_BY_RAG_COLLECTION.md` | RÉGÉNÉRÉ |
| `INDEX_BY_SEQUENCE.md` | RÉGÉNÉRÉ |
| `INDEX_BY_SESSION.md` | RÉGÉNÉRÉ |
| `INDEX_BY_THEME.md` | RÉGÉNÉRÉ |
| `coverage.md` | RÉGÉNÉRÉ |
| `coverage_sources.md` | RÉGÉNÉRÉ |
| `inventory_report.md` | RÉGÉNÉRÉ |
| `manifest.csv` | RÉGÉNÉRÉ |
| `manifest_tooling.csv` | RÉGÉNÉRÉ |
| `programme_matrix_premiere.md` | RÉGÉNÉRÉ |
| `programme_matrix_terminale.md` | RÉGÉNÉRÉ |

Les rendus T10, P08 et T17 ont aussi été reconstruits sous `dist/`, qui demeure ignoré et n’est pas ajouté à Git.

## 4. Tests et gates

| Commande | Résultat | Note |
|---|---|---|
| `python -m scripts.rebuild_inventory` | VERT | Inventaires reconstruits sur la base courante et les sources récupérées. |
| `python -m scripts.check_program_coverage` | VERT | Matrices et rapports de couverture régénérés. |
| `python -m scripts.generate_pedagogical_indexes` | VERT | Index pédagogiques régénérés. |
| `python -m scripts.generate_index` | VERT | `INDEX.md` régénéré. |
| `make render-unit U=T10` | VERT | Rendu produit dans `dist/`, non suivi. |
| `make render-unit U=P08` | VERT | Rendu produit dans `dist/`, non suivi. |
| `make render-unit U=T17` | VERT | Rendu produit dans `dist/`, non suivi. |
| `python -m scripts.check_sql_query_result_consistency` | VERT | 13 fichiers T10 contrôlés. |
| `python -m scripts.check_dynamic_programming_recurrence_consistency` | VERT | 10 fichiers T17 contrôlés. |
| `python -m scripts.check_linked_td_substance` | VERT | 37 TD contrôlés. |
| `python -m scripts.check_linked_evaluation_substance` | VERT | 37 évaluations contrôlées. |
| `python -m scripts.check_contract_substance_quality` | VERT | 35 contrats contrôlés, aucun pauvre. |
| `python -m scripts.check_eval_bareme_pairing` | VERT | 43 paires contrôlées. |
| `python -m scripts.check_links` | VERT | Aucun lien invalide signalé. |
| `python -m scripts.check_status_promotion_guard` | VERT | Aucune promotion positive détectée. |
| `python -m scripts.check_no_line_padding` | VERT | Aucun remplissage de lignes détecté. |
| `python -m scripts.check_substance_anchors` | ROUGE | Neuf verdicts antérieurs citent des preuves devenues obsolètes : `T-ALGO-04` et `T-BDD-03A` à `T-BDD-03H`. Aucun JSON n’a été modifié ; re-jugement indépendant requis. |
| `pytest -q` | ROUGE | `2 failed, 452 passed, 2 subtests passed`. Les deux échecs proviennent du même gate d’ancres obsolètes : `test_source_clean_audit_extracted_source_finishes_without_drive_mirror` et `test_substance_anchor_checker_global_mode_and_poisoned_fixture`. |
| `git diff --check` | VERT | Diff non indexé sans erreur d’espacement. |
| `git diff --cached --check` | VERT | Diff indexé sans erreur d’espacement. |

## 5. État Git

- Branche : `recovery/t10-p08-t17-from-blobs`.
- HEAD : `b34c8934a65619de48423b4dc54e9d0f19dc55ab`.
- Fichiers modifiés : 55 attendus (37 sources restaurées et 18 artefacts régénérés).
- Fichiers ajoutés : 7 fichiers restaurés depuis les blobs.
- Fichiers non suivis : ce rapport de récupération uniquement.
- Diff stat avant ajout du présent rapport : 62 fichiers suivis, 5 263 insertions, 1 929 suppressions.

Les 44 fichiers récupérés ont été indexés pour permettre aux générateurs de les voir ; aucun commit n’a été créé. Les 18 artefacts régénérés restent non indexés. Aucun verdict JSON et aucun statut n’ont été modifiés.

## 6. Diagnostic

**B. RECONSTRUCTION COMPLÈTE MAIS TESTS À CORRIGER**

La reconstruction des 44 sources et des 18 artefacts est complète. Les tests encore rouges ne signalent pas une divergence de récupération : ils matérialisent le blocage connu des neuf verdicts devenus obsolètes, qui ne peuvent être révisés par l’auteur des corrections.

## 7. Prochaine action recommandée

Faire réaliser par un juge indépendant le re-jugement des neuf capacités `T-ALGO-04` et `T-BDD-03A` à `T-BDD-03H`, puis relancer `check_substance_anchors` et `pytest -q` avant toute proposition d’intégration.
