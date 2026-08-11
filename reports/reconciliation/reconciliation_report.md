# Rapport de réconciliation

## Statut : RECONCILED_MAIN_GREEN

## SHA

| Branche | SHA avant | SHA après |
|---------|-----------|-----------|
| main | 0d886e0 | 8f1c0bf |
| lot1/substance-gouvernance | e06eb2b | 0e3484c (ff lot3) |
| lot3-post-merge-hardening | 0e3484c | — (intégré) |
| merge PR #3 (lots 1-3) | — | 069eabf |
| merge PR #4 (dette+rapports) | — | 8f1c0bf |

## CI main

- RUN_ID : 28412829616
- headSha : 8f1c0bf474af7fc8210924cf4c0d4321caffa92e
- conclusion : success
- jobs : quality=success

## PR #2 (fermée)

- Branche : lot3-post-merge-hardening → main
- Action : fermée comme redondante (contenu intégré via lot1 fast-forward)
- Commentaire de clôture posté

## PR #35 RAG (déjà mergée)

- Dépôt : cyranoaladin/RAG
- État : MERGED (avant cette passe)
- Branche : lot-19-audit-prod-collections → main
- Action : aucune fermeture nécessaire, documentée dans rag_pr35_status.md

## RAG

- Diagnostic : endpoint `/search` authentifié time out (constaté lots précédents)
- Dérive schéma prouvée : index déployé utilise `anchor`/`capacities`, dépôt attend
  `section_anchor`/`capacity_ids` (documenté dans rag_reindex_plan.md)
- Plan réindex : rédigé (rag_reindex_plan.md), exécution interdite cette passe
- Statut : **NON fonctionnel**
- `make rag-smoke-required` : échec attendu (métadonnées minimales absentes)

## Dette technique

### 5.1 mypy strict

- Configuration : `[tool.mypy]` strict=true, explicit_package_bases=true dans pyproject.toml
- Convention : `python -m scripts.<module>` (Makefile, check_quality_gates.py, tests)
- sys.path.insert + `# noqa: E402` retirés (147 scripts + 53 tests + 2 scrapping_NSI)
- Résultat : 112 erreurs résiduelles (type annotations) dans 29 fichiers
- Détail : reports/reconciliation/mypy_debt.md
- Test xfail : tests/test_mypy_strict_debt.py

### 5.2 Manifeste

- Séparation : `manifest.csv` (pédagogie, 663 entrées) / `manifest_tooling.csv` (outillage, 293 entrées)
- Aucun fichier scripts/, tests/, reports/, scrapping_NSI/ dans manifest.csv
- Test : tests/test_manifest_separation.py (3 assertions)
- Churn regen+amend : résolu (modifications de code ne salissent plus le manifeste pédagogique)

### 5.3 Privacy

- `check_no_private_data.py` : PASS (0 alerte bloquante)
- Allowlist structurée : `privacy_allowlist.yml` (motifs institutionnels, année scolaire)
- Faux positifs : noms propres en revue (non bloquants), décimaux techniques non détectés
- Test existant : tests/test_private_data_detection.py

### 5.4 Gates audit-core / check_quality_gates.py

- `check_gate_policy_consistency.py` : PASS (38 gates bloquants hors tests)
- Divergence documentée dans qa_gate_policy.md (check_metadata, check_links,
  check_no_build_artifacts_in_index, check_uploaded_archive_policy en plus dans
  check_quality_gates.py pour compatibilité CI)

### 5.5 Reports lot*

- Politique : `reports_policy.md` (2 MB cap, fichiers interdits, hors couverture)
- Vérification : `check_reports_policy.py` dans audit-core
- Lots présents : reports/lot1/, reports/lot2/, reports/lot3/

## Backlog Drive (3+7+5)

Documenté dans reports/reconciliation/drive_integration_plan.md :
- deferred=3 (planifiés lots ultérieurs)
- missing_local_copy=7 (URL connues, fichiers locaux absents)
- rejected_sensitive=5 (données personnelles, jamais intégrés)
- release-audit : échec attendu

## Couverture

- covered=0
- absent=22
- needs_review=variable (ressources documentaires)
- Inchangé par cette passe

## Validations

| Vérification | Résultat |
|--------------|----------|
| pytest | 328 passed, 1 xfailed |
| ruff | All checks passed |
| mypy --strict | 112 erreurs (dette documentée, test xfail) |
| check_no_private_data | PASS |
| audit-core | PASS (sauf check_git_clean sur branche de travail) |
| rag-smoke-required | ÉCHEC attendu (RAG non fonctionnel) |
| release-audit | ÉCHEC attendu (Drive non soldé) |

## Blocages restants

1. RAG non fonctionnel (timeout `/search`, dérive schéma)
2. Drive non soldé (7 copies locales absentes, 3 différés)
3. Couverture covered=0 (revue humaine absente)
4. mypy --strict : 112 erreurs résiduelles (annotations de type)

## Lot 4 contenu autorisé : non

FINAL_STATUS=NON_RELEASE_READY
needs_review partout ; covered=0 ; published=0 ; validated_*=0.
