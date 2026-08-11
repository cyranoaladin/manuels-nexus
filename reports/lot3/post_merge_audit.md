# Audit post-Lot 3

## Statut

POST_LOT3_REQUIRES_FIXES

Lot 4 autorisé : non.

## SHA

Sorties collectées :

```text
$ git rev-parse HEAD
e06eb2b93ea7e744ee94ee71962ed0667b2c2a36

$ git rev-parse origin/main
0d886e0ff9b0a83515c3fa0fc79c0aed2854157e

$ git rev-parse origin/lot1/substance-gouvernance
e06eb2b93ea7e744ee94ee71962ed0667b2c2a36
```

Branche locale de travail créée pour les corrections : `lot3-post-merge-hardening`.

Dernier commit de durcissement avant mise à jour finale de ce rapport :

```text
$ git log --oneline -3
ede87c0 Durcir la securite archives post Lot 3
e06eb2b Merge remote-tracking branch 'origin/lot1/substance-gouvernance' into lot1/substance-gouvernance
f852256 Consolider les gardes RAG et QA

$ git status -sb --short
## lot3-post-merge-hardening
```

Le SHA final poussé est fourni par `git log -1` après le commit de clôture, car un rapport ne peut pas contenir de manière stable le hash du commit qui le modifie.

## Méthode de mise à jour de main

Sorties collectées :

```text
$ gh pr list --repo cyranoaladin/NSI --state all --limit 20
1	Lot 1 : sécuriser la substance et les gardes	lot1/substance-gouvernance	MERGED	2026-06-28T20:57:14Z

$ gh pr view 1 --repo cyranoaladin/NSI --json number,title,state,isDraft,mergedAt,mergeCommit,headRefName,headRefOid,baseRefName,url
{"baseRefName":"main","headRefName":"lot1/substance-gouvernance","headRefOid":"0d886e0ff9b0a83515c3fa0fc79c0aed2854157e","isDraft":true,"mergeCommit":{"oid":"0d886e0ff9b0a83515c3fa0fc79c0aed2854157e"},"mergedAt":"2026-06-29T10:37:15Z","number":1,"state":"MERGED","title":"Lot 1 : sécuriser la substance et les gardes","url":"https://github.com/cyranoaladin/NSI/pull/1"}
```

Constat : `origin/main` pointe sur `0d886e0`, qui correspond au `mergeCommit` de la PR #1. Aucun merge commit séparé n'apparaît pour cette mise à jour ; le SHA de merge est identique au SHA de tête de PR. La branche `origin/lot1/substance-gouvernance` pointe ensuite sur `e06eb2b`, donc elle est en avance sur `origin/main`.

Écart de processus restant : le rappel annonçait `main`, `origin/main` et `origin/lot1/substance-gouvernance` au même SHA après Lot 3. La vérification locale contredit ce rappel : `origin/main=0d886e0` et `origin/lot1/substance-gouvernance=e06eb2b`.

## GitHub Actions main

Sorties collectées :

```text
$ MAIN_SHA="$(git rev-parse origin/main)"; echo "$MAIN_SHA"; gh run list --repo cyranoaladin/NSI --branch main --limit 3
0d886e0ff9b0a83515c3fa0fc79c0aed2854157e
completed	success	Actualiser les rapports de validation Lot 3	CI	main	push	28366005584	1m42s	2026-06-29T10:37:16Z
completed	success	Ajuster la config après restructuration du dépôt distant	CI	main	push	28334022625	1m29s	2026-06-28T19:51:46Z
completed	success	Corriger les gardes CI : archive propre, faux positif téléphone, robu…	CI	main	push	28333739043	1m30s	2026-06-28T19:40:39Z

$ gh run view --repo cyranoaladin/NSI 28366005584 --json status,conclusion,headSha,jobs,url
{"conclusion":"success","headSha":"0d886e0ff9b0a83515c3fa0fc79c0aed2854157e","jobs":[{"conclusion":"success","name":"quality","status":"completed","url":"https://github.com/cyranoaladin/NSI/actions/runs/28366005584/job/84031919771"}],"status":"completed","url":"https://github.com/cyranoaladin/NSI/actions/runs/28366005584"}

$ gh run view --repo cyranoaladin/NSI 28366005584
✓ main CI · 28366005584
JOBS
✓ quality in 1m40s (ID 84031919771)
```

Conclusion CI main : `success` prouvé sur `origin/main=0d886e0`.

Limite : cette CI ne prouve pas le SHA `e06eb2b` de `origin/lot1/substance-gouvernance`, ni la branche de durcissement post-Lot 3.

## Topologie dépôt

Dépôt canonique : `nsi-enseignement/`, clone Git autonome.

Dépôt parent local : espace de travail pouvant contenir `scrapping_NSI/` et des miroirs, mais `nsi-enseignement/` ne doit pas y être suivi par Git.

Sorties collectées, avec préfixe local personnel masqué sous `<workspace_parent>` :

```text
$ git -C <workspace_parent> ls-files nsi-enseignement

$ git -C <workspace_parent> ls-files scrapping_NSI/ressources_nsi_centralisees scrapping_NSI/ressources_nsi_extraites scrapping_NSI/ressources_nsi_extraites_v2 scrapping_NSI/sqlite_data

$ python scripts/check_repo_topology.py
check_repo_topology: PASS
```

Risque corrigé dans cette passe : les exclusions parent étaient présentes uniquement dans `.git/info/exclude`. La doctrine versionnée est maintenant dans `docs/repo_topology.md` et `docs/local_excludes_required.md`.

## Sécurité archive

Durcissements ajoutés :

- rejet ZIP des chemins absolus Unix, Windows et UNC ;
- rejet ZIP des séparateurs mixtes sortants ;
- rejet ZIP des membres `"."` ;
- rejet ZIP des symlinks via `external_attr` ;
- rejet ZIP des doublons de chemin cible ;
- limite de membres testée au-delà de 10 000 ;
- dépassement de flux réel testé malgré métadonnées faibles ;
- TAR symlink, hardlink et linkname dangereux testés ;
- staging `.part` nettoyé ;
- destination officielle préexistante non modifiée en cas d'échec.

Sortie ciblée :

```text
$ python -m pytest -q tests/test_archive_integration_wrappers.py tests/test_lot3_archive_security.py tests/test_archive_security_imports.py tests/test_source_archive_policy.py tests/test_repo_topology.py
..................................................                       [100%]
50 passed in 1.24s
```

## Archive source

Décision vérifiée : `source_clean` utilise `git ls-files`; le fallback hors Git affiche un avertissement et n'est pas une base release.

Sortie ciblée :

```text
$ python -m pytest -q tests/test_audit_extracted_source_no_hang.py tests/test_archive_portability_modes.py tests/test_final_quality_hardening.py::FinalQualityHardeningTest::test_runtime_budget_requires_source_archive_extraction tests/test_final_quality_hardening.py::FinalQualityHardeningTest::test_runtime_budget_runs_in_extracted_source_mode_without_archive tests/test_archive_integration_wrappers.py
............                                                        [100%]
17 passed in 53.49s
```

## Validations locales

Sorties collectées :

```text
$ python -m ruff check <fichiers modifiés>
All checks passed!

$ python scripts/check_no_private_data.py
check_no_private_data: PASS
```

Validation complète à compléter dans `reports/lot3/lot3_hardening_validation_log.md`.

## RAG smoke requis

Sortie collectée :

```text
$ make rag-smoke-required || true
python scripts/rag_smoke_test.py
RAG_SMOKE_TEST_FAILED
- hit 4: métadonnées minimales absentes
make: *** [Makefile:73: rag-smoke-required] Error 1
```

Conclusion : le RAG réel n'est pas déclaré fonctionnel. Le blocage courant n'est plus un timeout `/search` sur cette exécution ; l'API répond, mais le smoke échoue sur les métadonnées minimales attendues.

## Release audit

Sortie collectée :

```text
$ make release-audit || true
python scripts/check_drive_mapping_release.py
check_drive_mapping_release: KO
- Drive partiellement intégré: deferred=3, missing_local_copy=7, rejected_sensitive=5
make: *** [Makefile:359: release-audit] Error 1
```

Conclusion : échec attendu et conforme au statut `NON_RELEASE_READY`.

## Décision

Lot 4 autorisé : non.

Raison : `origin/main` est prouvé vert sur `0d886e0`, mais la branche Lot 3 réelle `e06eb2b` et les corrections post-merge doivent être passées par une PR dédiée `lot3-post-merge-hardening`.

## Blocages restants

- Prouver la CI GitHub sur le HEAD de `lot3-post-merge-hardening` après push.
- Ne pas merger sans revue explicite.
