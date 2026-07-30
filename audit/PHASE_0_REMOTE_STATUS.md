# État distant de la Phase 0

## Mission

- Branche locale observée : `finalisation/collection-v1`
- SHA local observé : `e6c2f70d4b12e1eb80cd37177874e986abf95a1a`
- SHA distant observé : `origin/finalisation/collection-v1` = `e6c2f70d4b12e1eb80cd37177874e986abf95a1a`
- `git rev-list --left-right --count origin/finalisation/collection-v1...HEAD` : `0 0`
- Worktree propre.

## PR et run analysé

- PR : [#1](https://github.com/cyranoaladin/manuels-nexus/pull/1), `OPEN`, `isDraft: true`, `headRefOid: e6c2f70d4b12e1eb80cd37177874e986abf95a1a`
- Run CI ciblé : `30555858436`
- Job: `90916003021`
- SHA: `e6c2f70d4b12e1eb80cd37177874e986abf95a1a`
- Événement: `push`
- Statut: `completed`, conclusion: `failure`
- Artefacts téléchargés dans `/tmp/manuels-ci-30555858436.6hfPBb`

## Sous-gates Phase 0 aux codes exacts

Ordre observé: `require-clean`, `check`, `validate-model`, `fail-on-new`, `release-strict`.

| Gate | Réel | Attendu |
|---|---:|---:|
| require-clean | `0` | `0` |
| check | `3` | `0` |
| validate-model | `6` | `0` |
| fail-on-new | `0` | `0` |
| release-strict | `7` | `7` |

Cause globale: `failure_count = 12` dans `gate-summary.json`.

- `check` (`3`) : `diff: audit/ECARTS_ET_CONTRADICTIONS.yaml`, `diff: audit/INVENTAIRE_COLLECTION.json`, `diff: audit/MATRICE_LIVRABLES.yaml`
  - confirmée identique au run précédent (artifact `30546406535`, `check.json` inchangé).
- `validate-model` (`6`) :
  - `inventaire:generator_files différent du générateur courant`
  - `inventaire:generator_sha256 différent du générateur courant`

`release-strict` reste au contrat attendu (`7`) sans régression de ce poste.

## Preuves observées (run 30555858436)

- `gates/check.json`
- `gates/validate-model.json`
- `gates/require-clean.json`
- `gates/fail-on-new.json`
- `gates/release-strict.json`
- `gates/release-strict.repeat.json`
- `gates/gate-summary.json`
- `coverage.xml`
- `generation/generated-a/...` et `generation/generated-b/...`
- `manuels-nexus/manuels-nexus/audit/BUILD_MANIFEST.json`

`release-strict.json` = `7` (contrat), `gate-summary.json` encode bien le mode non conforme.

## Tool versions / preuve runtime

- Versions runtime observées dans artefacts de génération, ex. `generation/generated-a/audit/INVENTAIRE_COLLECTION.json -> provenance.tool_versions` :
  - `python: Python 3.12.11`
  - `git: git version 2.54.0`
  - `texlive: pdfTeX ... TeX Live 2023/Debian`
  - `pdfinfo: pdfinfo version 24.02.0`
- `audit/BUILD_MANIFEST.json` ne contient pas de champ explicite `canonical_tool_versions` / `observed_runtime_tool_versions`.
- Le test `_reuse_stored_generation_provenance` a bien permis la réutilisation de `generator_files` + `generator_sha256`, mais la séparation canonique/runtime n’est pas encore formalisée en champ séparé.

## Résultats pytest CI (22 échecs)

| Catégorie | Nombre | Node IDs | Cause |
|---|---:|---|---|
| visuel connu | 5 | `Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_validation_png_reference_hashes` ; `...::test_non_diagnostics_page_hashes_reject_a_changed_page` ; `...::test_page13_diagnostics_layout_pdf` ; `...::test_qcm_diagnostics_and_corrections_pdf` ; `...::test_maquette_v5_acceptance` | Écarts visuels attendus déjà suivis |
| PDF/LaTeX | 13 | `Mathematiques/manuel-maths/tests/test_maquette_v5.py::test_checker_cli_synthetic_exit_codes` ; `...::test_rubric_tab_dynamic_fixture_pdf` ; `...::test_navigation_blank_fixture_pdf` ; `...::test_method_pairing_fixtures[0]` ; `...::test_method_pairing_fixtures[1]` ; `...::test_method_pairing_fixtures[2]` ; `...::test_method_pairing_fixtures[3]` ; `...::test_multicols_marginnote_is_redirected` ; `...::test_exercise_grid_fixture_pdf` ; `...::test_course_fixture_pdf` ; `...::test_course_trailing_float_fixture_pdf` ; `...::test_pdf_integrity.py::test_missing_asset_produces_warning_in_real_compilation` ; `...::test_pdf_integrity.py::test_specimen_compiles_with_exit_zero` | `lualatex` échoue (TeX Gyre Pagella non trouvable), production PDF non conforme |
| inventaire/check | 0 | *(none)* | — |
| transactions/baseline | 4 | `tests/test_inventory_collection.py::test_update_baseline_cli_rejects_ci_dirty_repo_and_invalid_model` ; `...::test_update_baseline_writes_audited_transition_and_preserves_resolved_history` ; `...::test_update_baseline_rejects_head_change_immediately_before_replace` ; `...::test_update_baseline_recovers_interrupted_write_before_clean_preflight` | Vérifications d’update baseline en erreur |
| environnement CI | 0 | *(none)* | — |
| autre | 0 | *(none)* | — |

Les 22 échecs ne sont donc pas limités aux 5 visuels connus.

## Remarque de gouvernance

Le run valide donc :
- `check` toujours `3` (cause résiduelle)
- `validate-model` désormais bloquant (`6`)
- gates déjà non exploitables pour release.

Tests RAG ignorés : `5`.
