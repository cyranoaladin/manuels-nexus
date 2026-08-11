# Inventaire sécurité archives

Voir `reports/lot3/archive_extraction_inventory.md`.

Résumé : aucune occurrence directe de `extractall` ne reste dans le code de production ; les extractions métier passent par `safe_extract_zip` ou `safe_extract_tar`.
