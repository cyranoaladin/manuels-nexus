# Rapport de cloture

## Statut : CLOSED_CLEAN

## main

- SHA HEAD : 3080147e6047ab1f59c6a41879c3d41fa7772fc2
- CI RUN_ID : 28431130867, headSha=3080147, conclusion=**success**

## Incident force-push

Deux incidents de processus documentés dans `process_incidents.md` :
1. Push direct sur main (passe 1) : commit documentation `be73955`
2. Amend + force-push (passe 2) : branche audit-verification/report
3. Push direct sur main (passe 3) : commit regen `3080147`

Politique adoptée : commit poussé = immuable. Corrections par nouveau commit.

## PR #2

- `gh pr view 2 --json state` → **CLOSED**. Conforme.

## PR #35 RAG

- `gh pr view 35 --repo cyranoaladin/RAG --json state` → **MERGED** (2026-06-29)
- Contenu : 29 fichiers (CI, config, code ingestor, tests, infra docker)
- Non deploye (serveur utilise toujours le schema legacy)
- Recommandation : audit du code merge dans un lot RAG dedie
- Detail dans `rag_pr35_status.md`

## RAG : derive OBSERVEE (passe 3, 2026-06-30 ~09h)

```
POST /search {q: "CSV", collection: "nsi_corpus", k: 2}
HITS_COUNT=2
hit[0] metadata keys: ['anchor', 'capacities', 'chunk_index', 'collection',
  'document_type', 'level', 'notion', 'path', 'sequence_id', 'sha256',
  'source_type', 'status', 'theme']
anchor=True section_anchor=False capacities=True capacity_ids=False
```

Le serveur retourne `anchor`/`capacities` (legacy). Le depot attend
`section_anchor`/`capacity_ids` (canonique). Plan dans `rag_reindex_plan.md`.
`make rag-smoke-required` : echec attendu.

## Non-determinisme rapports

**Cause racine** : `manifest.csv` incluait des fichiers config/generes racine
(ci.yml, pyproject.toml, privacy_report.md, manifest_tooling.csv) dont les
hashes changent a chaque modification d'outillage.

**Correctif** :
- Fichiers config/generes exclus de `manifest.csv` (seuls les dirs pedagogiques restent)
- `manifest_tooling.csv` et `01_build_reports` exclus de `iter_files()` (auto-reference circulaire)
- `01_build_reports` ajoute a `IGNORED_DIRS`

**Preuve** : `make audit-idempotence` PASS (double audit, `git status --short` vide).
Test `test_manifest_idempotent_after_rebuild` : deux rebuilds consecutifs = sortie byte-identical.

## manifest config racine

Fichiers config racine (pyproject.toml, ci.yml, Makefile, privacy_allowlist.yml,
etc.) deplaces dans `manifest_tooling.csv`. `manifest.csv` ne contient plus que
les dirs pedagogiques (`00_programmes_officiels/`, `02_modeles_documents/`,
`03_progressions/`, `premiere/`, `terminale/`).

Test : `test_pedagogical_manifest_contains_only_pedagogical_content`.

## mypy

Compte reel en venv propre : **74 erreurs dans 23 fichiers** (208 verifies).

Progression : 557 → 112 → 90 → 74.

Gains passe 3 (+16) :
- `Dict[str, object]` → `Dict[str, Any]` dans `_inventory_utils.py`, `_session_checks.py`,
  `check_session_*.py` (5 fichiers)

Cliquet prouve :
```
# +1 erreur fictive → rouge :
FAILED tests/test_mypy_strict_debt.py::test_mypy_ratchet - 1 NEW mypy error(s)
# retrait → vert :
1 passed in 0.19s
```

Cliquet en CI : `ci.yml` → `pytest` → inclut `test_mypy_ratchet` → prouve par
run 28430548092 (quality=pass, head=860215e, inclut le test ratchet).

Reliquat justifie dans `mypy_debt.md` par lib (yaml.safe_load → Any, csv.DictReader → str|None).

## Validations venv propre

| Check | Resultat |
|-------|----------|
| pytest | 331 passed |
| ruff | All checks passed |
| mypy | 74 erreurs = baseline (ratchet vert) |
| check_no_private_data | PASS |
| audit-core | PASS |
| audit-metrics | PASS |
| audit-idempotence | PASS |
| deliver-pedagogical-archive | PASS |
| deliver-source-zip | PASS |
| package-audit | PASS |
| audit-extracted-source | PASS |
| verify-delivery-archive | PASS |
| rag-smoke-required | echec attendu (RAG non fonctionnel) |
| release-audit | echec = backlog Drive (deferred=3, missing=7, rejected=5) |

## Invariants reprouves

```
covered : 0
absent : 22
published : 0
validated_* : 0
FINAL_STATUS = NON_RELEASE_READY
```

## Dette residuelle

| Item | Statut | Detail |
|------|--------|--------|
| mypy 74 erreurs | Documente + cliquet | yaml.safe_load/csv.DictReader typing |
| RAG schema drift | Documente + plan | Execution interdite cette passe |
| Drive backlog 15 items | Documente | 3 deferred, 7 missing, 5 rejected |
| Push directs sur main | Documente | 3 incidents, politique adoptee |

## Lot 4 contenu : non

FINAL_STATUS=NON_RELEASE_READY.
needs_review partout ; covered=0 ; published=0 ; validated_*=0.
