# CI d’audit de la collection — Phase 0

## Contrat branché

Le workflow `.github/workflows/ci-audit-collection.yml` exécute sur le dépôt
complet :

- Ruff sur les scripts et tests de Phase 0 ;
- mypy sur cinq modules explicitement listés ;
- les tests Pytest en mode `importlib`, avec couverture lignes et branches ;
- le parsing réel de tous les JSON et YAML suivis, avec refus des clés YAML
  dupliquées ;
- deux générations dans des clones propres indépendants, puis une comparaison
  octet par octet des six artefacts gérés ;
- `--require-clean`, `--check`, `--validate-model` et `--fail-on-new` avec un
  code de sortie exactement nul ;
- `--release-strict` avec un code exactement égal à 7, une sortie identique sur
  deux exécutions et des dettes réelles d’intégration, de 1SPE et de dimensions
  non couvertes.

Les preuves sont écrites sous `${{ runner.temp }}`, donc hors du worktree avant
`--require-clean`. La CI n’appelle jamais `--update-baseline`. Les actions sont
épinglées par SHA et les dépendances Python directes et transitives sont
épinglées ; l’installation utilise `--no-deps`, puis `pip check`.

## Mesures locales du 30 juillet 2026

| Contrôle | Résultat observé |
|---|---|
| Collecte Pytest complète avec le contrat CI | 2 420 tests |
| Suite complète avec le contrat CI | 2 410 passés, 5 échoués, 5 ignorés, 269,91 s |
| Famille des 5 échecs | hashes PNG de la baseline visuelle, page 1 altérée |
| Raison des 5 tests ignorés | index RAG indisponible en mode fichiers |
| Couverture des scripts racine | 76,73 % lignes + branches |
| Seuil initial | 74 % |
| JSON/YAML suivis parsés | 2 017 |
| Tests ciblés de contrat CI | 29 |

La baseline visuelle n’a pas été modifiée : son évolution exige une approbation
humaine et un diff avant/après.

## Limites et dettes explicites

- `inventory_collection.py`, `inventory_assembly.py` et `build_manifest.py`
  restent hors du périmètre mypy de ce lot. Le diagnostic initial sur les huit
  modules signalait 42 erreurs ; leur correction demande un lot de typage
  autonome pour ne pas mélanger refactorisation des générateurs et branchement
  CI.
- Le runner est fixé à `ubuntu-24.04` et Python à `3.12.11`, mais les paquets
  TeX/Poppler installés par APT ne sont pas verrouillés octet par octet.
- Le workflow restera rouge tant que `--fail-on-new` refuse la baseline
  provisoire. Ce refus est volontaire et n’est ni masqué ni converti en succès.
- `--release-strict` reste rouge de manière contrôlée tant que les 69 dettes
  déterministes observées ne sont pas résolues.
