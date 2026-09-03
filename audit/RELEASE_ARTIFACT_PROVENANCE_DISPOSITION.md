# Disposition des artefacts de release sans provenance complete

Genere par `scripts/build_release_artifact_provenance_disposition.py`. Ancestralite evaluee contre `HEAD`.

| METRIC_NAME | VALEUR |
| --- | --- |
| DOCKETED_ARTIFACTS | 3 |
| ACTIVE_RELEASE_ARTIFACTS_WITHOUT_PRODUCER | 0 |
| UNKNOWN_DISPOSITIONS | 0 |
| REFUTED_DISPOSITIONS | 0 |
| CURRENT_PREFLIGHT_PROVENANCE | PASS |
| GATE | PASS |

## Artefacts

| ARTEFACT | DISPOSITION | PRODUCTEUR | CURRENT_RELEASE_CONSUMERS | VERDICT |
| --- | --- | --- | --- | --- |
| `audit/PUBLISH_STATUS_DEBT_CLASSIFICATION.json` | HISTORICAL_OBSOLETE | `aucun` | 0 | CONFIRMED |
| `audit/STUDENT_PDF_PUBLISH_PREFLIGHT_CURRENT_HEAD.json` | ACTIVE_RELEASE_ARTIFACT | `scripts/build_math_student_teacher_key_audit.py` | 0 | CONFIRMED |
| `audit/WIP_UPSTREAM_RECONCILIATION.json` | HISTORICAL_SUPERSEDED | `scripts/reconcile_wip_upstream.py` | 0 | CONFIRMED |

### `audit/PUBLISH_STATUS_DEBT_CLASSIFICATION.json`

- disposition : **HISTORICAL_OBSOLETE** (decidee dans `audit/HUMAN_DECISION_RELEASE_ARTIFACT_DISPOSITION_2026-09-03.json`)
- motif : cartographie de dette de statut emise sans producteur reproductible et sans aucun consommateur ; elle ne peut plus etre reemise ni verifiee, elle sort de la surface de release courante
- sha256 : `bdce8dab57c2a6fc8247b7075a635182d8798f594076bf73438715f982bb57b1`
- conserve dans l'histoire Git : 1 commits, toujours suivi

| REFERENCE | ROLE |
| --- | --- |
| `audit/PUBLISH_STATUS_DEBT_CLASSIFICATION.md` | MARKDOWN_COMPANION |

### `audit/STUDENT_PDF_PUBLISH_PREFLIGHT_CURRENT_HEAD.json`

- disposition : **ACTIVE_RELEASE_ARTIFACT** (decidee dans `audit/HUMAN_DECISION_RELEASE_ARTIFACT_DISPOSITION_2026-09-03.json`)
- motif : le producteur existe et declare cette cible ; le champ generated_by manquait, il a ete ajoute via le producteur et l'artefact a ete reemis
- sha256 : `f61723ea688b5d4c332d68b0771e3a378031e9fc250bd8ee035e8a4c20b514df`
- conserve dans l'histoire Git : 16 commits, toujours suivi

| REFERENCE | ROLE |
| --- | --- |
| `audit/test_matrix_logs/root_audit_tests.before-fixes.log` | ARCHIVED_LOG |
| `scripts/build_math_student_teacher_key_audit.py` | PRODUCER |
| `tests/test_math_student_teacher_key_audit.py` | HISTORICAL_TEST_CONSUMER |

### `audit/WIP_UPSTREAM_RECONCILIATION.json`

- disposition : **HISTORICAL_SUPERSEDED** (decidee dans `audit/HUMAN_DECISION_RELEASE_ARTIFACT_DISPOSITION_2026-09-03.json`)
- motif : instantane d'une reconciliation trois voies parametree par deux SHA ; ces deux SHA sont desormais des ancetres de HEAD, donc l'etat decrit est integre et supersede
- sha256 : `f79a442ae1a877e27cfe0e9491091409c5340eb4faf1b0e1760a8e80904e3229`
- conserve dans l'histoire Git : 2 commits, toujours suivi

| REFERENCE | ROLE |
| --- | --- |
| `audit/WIP_DROPPED_DELTA_LEDGER.json` | PROVENANCE_MENTION_IN_ANOTHER_ARTIFACT |
| `audit/WIP_UPSTREAM_RECONCILIATION.md` | MARKDOWN_COMPANION |
| `tests/test_wip_upstream_reconciliation.py` | HISTORICAL_TEST_CONSUMER |

| SHA D'INSTANTANE | CHAMP | ANCETRE DE HEAD |
| --- | --- | --- |
| `28d2cac7a3ccc44c49543f35086db08b8771715e` | `upstream_sha` | oui |
| `761508d923d74fd3d93fc055b3f3b1857fb251e1` | `wip_base_sha` | oui |
