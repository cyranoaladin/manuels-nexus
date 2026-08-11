# Inventaire des extractions d'archives

Commande :

```bash
rg -n "extractall|extract\(|unpack_archive|shutil\.unpack|tarfile\.open|zipfile\.ZipFile" .
```

## Synthèse

Aucune occurrence directe de `extractall` ne reste dans le code de production.

Les occurrences restantes relèvent de quatre catégories :

- extraction sûre via `safe_extract_zip` / `safe_extract_tar` ;
- lecture d'archive sans extraction ;
- génération d'archive livrable ;
- fixtures ou tests négatifs.

## Tableau

| Fichier | Ligne | Usage | Risque | Décision | Test associé |
| --- | ---: | --- | --- | --- | --- |
| scrapping_NSI/safe_archive.py | 53 | `zipfile.ZipFile` puis extraction manuelle dans staging | surface centrale | autorisé via `safe_extract_zip` | tests/test_lot3_archive_security.py |
| scrapping_NSI/safe_archive.py | 95 | `tarfile.open` puis extraction manuelle dans staging | surface centrale | autorisé via `safe_extract_tar` | tests/test_lot3_archive_security.py |
| scrapping_NSI/scraper_eduscol.py | 64 | appel `safe_extract_zip` | ZIP externe | autorisé via wrapper | tests/test_archive_integration_wrappers.py |
| scrapping_NSI/organizer_nsi.py | 853 | appel `safe_extract_zip` | ZIP Drive/transit | autorisé via wrapper | tests/test_archive_integration_wrappers.py |
| scripts/check_archive_portability.py | 54 | appel `safe_extract_tar` | source_clean | autorisé via wrapper | tests/test_archive_integration_wrappers.py |
| scripts/check_audit_extracted_runtime_budget.py | 121 | appel `safe_extract_tar` | source_clean | autorisé via wrapper | tests/test_archive_integration_wrappers.py |
| scripts/run_audit_extracted_source.py | 25 | wrapper vers `scripts.archive_security.safe_extract_tar` | source_clean | autorisé, pas de `extractall` | tests/test_audit_extracted_source_no_hang.py |
| scripts/build_source_archive.py | 85 | génération `source_clean.tar.gz` | écriture archive | autorisé, pas extraction | tests/test_source_archive_policy.py |
| scripts/build_source_zip.py | 20 | génération ZIP livrable | écriture archive | autorisé, pas extraction | tests/test_source_zip_delivery.py |
| scripts/check_uploaded_archive_policy.py | 48-51 | lecture de noms d'archives uploadées | lecture seule | autorisé | tests/test_uploaded_archive_policy.py |
| scripts/check_audit_folder_policy.py | 31-34 | lecture de noms d'archives | lecture seule | autorisé | audit-core |
| scripts/check_delivered_archive_exactly_source_clean.py | 36 | lecture de noms TAR | lecture seule | autorisé | tests/test_delivered_archive_exactly_source_clean.py |
| scripts/check_packaging_mode.py | 23 | lecture de noms TAR | lecture seule | autorisé | tests/test_packaging_modes.py |
| scripts/check_no_sensitive_drive_in_source_clean.py | 23 | lecture de noms TAR | lecture seule | autorisé | audit-source |
| scripts/check_repo_topology.py | 78-81 | lecture de noms d'archives livrables | lecture seule | autorisé | tests/test_repo_topology.py |
| scrapping_NSI/test_scraper_eduscol.py | 560-569 | ancien test patchant `ZipFile.extractall` | test historique | autorisé comme test, hors production | test exclu du scan production |
| tests/test_lot3_archive_security.py | multiples | fixtures ZIP/TAR et tests négatifs | test | autorisé | lui-même |
| tests/test_archive_integration_wrappers.py | 27, 33 | fixtures ZIP/TAR | test | autorisé | lui-même |
| tests/test_source_archive_policy.py | 71 | lecture de l'archive générée | test | autorisé | lui-même |
| tests/test_audit_extracted_source_no_hang.py | multiples | fixtures TAR et lecture test | test | autorisé | lui-même |

## Résultat

Décision : aucune extraction directe interdite à corriger après cette passe.
