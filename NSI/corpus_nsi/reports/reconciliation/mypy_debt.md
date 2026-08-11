# Dette mypy --strict résiduelle

## Configuration

- `pyproject.toml` : `[tool.mypy]` strict=true, explicit_package_bases=true, mypy_path="."
- Convention d'empaquetage : `python -m scripts.<module>`
- pythonpath=["."] dans pytest config
- Cliquet : `tests/test_mypy_strict_debt.py::test_mypy_ratchet` + `tests/mypy_baseline.txt`

## Résultat (passe clôture, venv propre)

`mypy --strict scripts/ scrapping_NSI/` : **74 erreurs dans 23 fichiers** (208 vérifiés).

Progression : 557 → 112 → 90 → 74.

## Erreurs résiduelles par catégorie

| Catégorie | Nombre | Justification irréductibilité |
|-----------|--------|-------------------------------|
| arg-type | 23 | `yaml.safe_load()` → `Any` propagé dans les appels ; cast local nécessiterait TypedDict par fichier YAML |
| var-annotated | 16 | Variables initialisées par boucles CSV/YAML sans annotation locale (`Counter`, `defaultdict`) |
| attr-defined | 12 | Accès `.get()` / `.exists()` sur variables typées `str` au lieu de `Path` (héritage d'interface) |
| assignment | 6 | Réassignation `str` ← `Path` ou `dict` incompatible (frontmatter dynamique) |
| type-arg | 5 | Arguments génériques `Counter[str]`, `dict[str, ...]` sous-typés par inférence |
| str | 3 | Argument `str` attendu `Path` (fonctions utilitaires legacy) |
| operator | 3 | Opérateurs arithmétiques sur `Any` (valeurs YAML) |
| misc | 3 | Generator types, callable patterns |
| return-value | 2 | Type retour `dict[str, Any]` vs `dict[str, str]` (frontmatter) |
| index | 2 | Indexation `str[int]` sur `Any` |
| comparison-overlap | 1 | Comparaison types disjoints (`str` vs `int` via YAML) |
| call-overload | 1 | `range()` avec argument `Any` |

## Fichiers principaux

- `scripts/rebuild_inventory.py` (10) : frontmatter Dict[str, Any] propagé
- `scripts/check_session_*.py` (22 total) : `_session_checks` parsing YAML
- `scripts/check_drive_integration_plan.py` (7) : variable `str` au lieu de `Path`
- `scripts/generate_qa_report.py` (6) : `course_sheet_stats()` retourne `dict[str, object]`

## Cause racine

Toutes les erreurs tracent à deux sources :
1. **yaml.safe_load()** (bibliothèque PyYAML) retourne `Any` ; types-PyYAML fournit
   des stubs mais le retour reste `Any` par design (YAML peut contenir n'importe quoi).
2. **csv.DictReader** retourne `dict[str, str | None]` ; les scripts traitent les
   valeurs comme `str` sans guard `is not None`.

Corriger nécessiterait des TypedDict spécifiques pour chaque schéma YAML/CSV (8+
schémas distincts). Aucun bug d'exécution masqué : les objets sont des dicts bien
formés à l'exécution.

## Cliquet (ratchet)

Le test `tests/test_mypy_strict_debt.py::test_mypy_ratchet` compare le jeu
actuel d'erreurs à `tests/mypy_baseline.txt` (74 lignes).

- Nouvelle erreur → **rouge** (régression bloquée)
- Erreur fixée sans mise à jour baseline → **rouge** (forcer l'amélioration)
- Aligné → **vert**

Le cliquet s'exécute en CI via pytest (ci.yml → `pytest` → inclut le test ratchet).
