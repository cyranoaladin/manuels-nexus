# Lot 0 — revue des suppressions ruff --fix

Contexte : le commit `f4fb845` a appliqué `ruff check --fix` puis des corrections
manuelles. Cette note vérifie que les suppressions d'import ou de variable ne
cassent pas une API réexportée, un accès dynamique ou un effet de bord attendu.

Commande de recherche dynamique utilisée :

```bash
rg -n "__all__|getattr\(|globals\(|import \*" <fichiers touchés>
```

Résultat : seul `scripts/_course_sheets_common.py` expose un réexport explicite.
Le réexport `read_frontmatter` a été restauré et documenté par `__all__`.

| fichier | changement ruff | revue |
| --- | --- | --- |
| `scripts/_course_sheets_common.py` | restauration de `read_frontmatter` | réexport API nécessaire, couvert par `tests/test_course_sheets.py` |
| `scripts/_inventory_utils.py` | import `dataclass` retiré | aucun réexport ni usage dynamique détecté |
| `scripts/_supports_evidence.py` | imports `re`, `Path` retirés | aucun réexport ni usage dynamique détecté |
| `scripts/build_all.py` | import `sys` retiré | aucun réexport ni usage dynamique détecté |
| `scripts/check_content_tree_policy.py` | import `Path` retiré | aucun réexport ni usage dynamique détecté |
| `scripts/check_contract_substance_quality.py` | import `Path` retiré | aucun réexport ni usage dynamique détecté |
| `scripts/check_course_sheets_no_template_abuse.py` | import `re` retiré | aucun réexport ni usage dynamique détecté |
| `scripts/check_gate_policy_consistency.py` | imports `Path`, `re` retirés | aucun réexport ni usage dynamique détecté |
| `scripts/check_missing_register_actionability.py` | import `defaultdict` retiré | aucun réexport ni usage dynamique détecté |
| `scripts/check_no_placeholders_docs.py` | import `Path` retiré | aucun réexport ni usage dynamique détecté |
| `scripts/check_no_sensitive_drive_in_source_clean.py` | import `re` retiré | aucun réexport ni usage dynamique détecté |
| `scripts/check_no_teacher_content_in_student_export.py` | import `Path` retiré | aucun réexport ni usage dynamique détecté |
| `scripts/check_paper_tp_contract.py` | variable locale inutilisée retirée | aucun effet de bord : la lecture utile est faite dans l'analyse |
| `scripts/check_register_no_hidden_operational_debt.py` | import `re` retiré | aucun réexport ni usage dynamique détecté |
| `scripts/check_rendered_unit_artifacts.py` | import `ROOT` retiré | aucun réexport ni usage dynamique détecté |
| `scripts/check_session_referenced_files_exist.py` | import `sys` retiré | aucun réexport ni usage dynamique détecté |
| `scripts/check_tp_executable_opportunity.py` | import `read_frontmatter` retiré | aucun réexport ni usage dynamique détecté |
| `scripts/check_validated_documents_quality_gates.py` | import `re` retiré | aucun réexport ni usage dynamique détecté |
| `scripts/generate_qa_report.py` | f-string constante simplifiée | pas de changement fonctionnel |
| `scripts/ingest_nsi_corpus.py` | variables mortes et `pass` retirés | script non promu en Lot 0 ; comportement de sortie conservé hors suppression de placeholders |
| `scripts/rag_smoke_test.py` | fonctions `test_*` renommées `smoke_*` | évite la collecte pytest de scripts, main conservé |
| `scripts/rebuild_inventory.py` | imports inutilisés retirés | aucun réexport ni usage dynamique détecté |
| `scripts/render_unit.py` | import `sys` retiré | aucun réexport ni usage dynamique détecté |
| `scripts/substance_judge.py` | variable morte `intitule_emb` retirée | pas d'autre changement fonctionnel Lot 0 ; Lot 1 traitera la doctrine du juge |
| `tests/test_drive_portable_and_manifest.py` | import `csv` retiré | test inchangé fonctionnellement |
| `tests/test_final_quality_hardening.py` | import `csv` retiré | test inchangé fonctionnellement |

Modules sans test unitaire dédié au niveau module : plusieurs checks historiques
sont vérifiés par les audits agrégés (`pytest`, `check_quality_gates.py`,
`audit-extracted-source`) plutôt que par un test ciblé par module. Cela concerne
notamment les scripts de métriques et de reporting listés ci-dessus. Aucune
suppression supplémentaire n'est supposée couverte au-delà des commandes de
vérification exécutées.
