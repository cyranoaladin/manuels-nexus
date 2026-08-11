# Politique des archives source

L'archive source canonique est construite depuis `git ls-files`.

Conséquences :

- un fichier suivi par Git est inclus sauf exclusion explicite ;
- un fichier non suivi n'est pas inclus ;
- un gros miroir local non suivi n'est pas inclus ;
- le fallback sans Git utilise `rglob` uniquement pour audit de portabilité et
  doit afficher un avertissement ;
- aucune release réelle ne doit être produite depuis le fallback sans Git sans
  revue humaine explicite.

Exclusions obligatoires :

```text
dist/
.git/
nsi-enseignement/.git
__pycache__/
.pytest_cache/
.ruff_cache/
.mypy_cache/
.venv/
01_build_reports/
build/
```

Les miroirs locaux et les sources Drive brutes sont exclus du périmètre de
livraison par leur absence de suivi Git et par `docs/repo_topology.md`.
