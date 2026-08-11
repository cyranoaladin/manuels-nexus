# Rapport de finalisation — chore/reorg-latex-kit

## Phase 1 — Décision LaTeX : FAIT
- Option A (kit pdflatex canonique) actée.
- `render_sequence.py` marqué LEGACY.
- Règle `.tex = artefacts générés` documentée.

## Phase 2 — Suppression nsi-enseignement/ : FAIT
- 0 commits non poussés vérifié.
- 159 Mo supprimés (clone imbriqué, jamais tracké).

## Phase 3 — Propreté : FAIT
- 9 rapports non-référencés déplacés sous `reports/`.
- 24 rapports référencés laissés en racine (scripts dépendants).
- `.gitignore` couvre `.env`, `Cahier des charges*`, data dirs.
- 0 fichier data lourd tracké.

## Phase 4 — Fichiers générés : FAIT
- `IGNORED_DIRS` étendu (scrapping_NSI, Documents_DRIVE, nsi-enseignement).
- `check_links.py`, `check_no_placeholders_docs.py`, `check_no_placeholders_code.py` patchés.
- `make generate-reports` + `make check-generated-freshness` PASS.

## Phase 5 — Validation

| Gate | Résultat |
|------|---------|
| `ruff check .` | **PASS** |
| `pytest` | **262 passed** |
| `cd latex && ./build.sh` | **EXIT 0** (8 PDF) |
| `git ls-files \| grep data` | **0 fichier** |
| `make audit-local` | **KO** (pré-existant, non régression) |

### Note sur make audit-local

Le `check_no_placeholders_code` échoue sur `substance_report_renderer.py` (ellipsis `...`
en Python). Ce problème est **pré-existant** — il échoue aussi sur `main` (vérifié).
Il n'est PAS causé par la réorganisation.

La CI GitHub (`ci.yml`) ne lance pas `make audit` — elle exécute ruff + pytest +
guards spécifiques, qui passent tous. Le `make audit` local scanne le filesystem
(incluant `scrapping_NSI/` non cloné en CI) et a des faux positifs pré-existants.

## Phase 6 — Merge : PRÊT

Branche prête à merger dans main après push et CI verte sur GitHub.

## Commits sur la branche

1. `556a3b0` — Source unique templates LaTeX dans 02_modeles_documents/
2. `8e48843` — Réorganiser latex/ (packs/premiere/P13/) + docs/ + chemins
3. `340db14` — Rapport de réorganisation (anomalies préexistantes)
4. `305545e` — Dispatcher build.sh + source unique nsi-preamble.sty
5. `de5200c` — Décision LaTeX — deux systèmes
6. `9268014` — .gitignore data lourds + rapport nsi-enseignement/
7. `c056c38` — Acter décision LaTeX Option A
8. `1687d02` — Supprimer nsi-enseignement/
9. `2a93a62` — Déplacer 9 rapports non-référencés sous reports/
10. `e771ce5` — IGNORED_DIRS + regen manifests
11. `c96abf8` — PDF P13 recompilés
12. `3176cca` — Regen privacy_report.md
13. `199cdfa` — Exclure data dirs (placeholders docs)
14. `e0873b4` — Exclure data dirs (placeholders code)
15. `827fc01` — Exclure data dirs (links + inventory)
