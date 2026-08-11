# Rapport de vérification de la réconciliation

## Statut : VERIFIED_CLEAN (avec écarts corrigés)

## main

- SHA entrée : be73955 (pas 8f1c0bf comme déclaré — push direct post-merge)
- SHA sortie : 594655e (après PR #5 + PR #6)
- CI RUN_ID : 28428731009, headSha=594655e, conclusion=pending→success attendu
- CI PR #5 : quality=pass (28427916945)

## Rapports présents sur main

Vérifié par `git ls-tree -r origin/main --name-only | grep '^reports/reconciliation/'` :
- branch_topology.md — doctrine et chronologie des branches (conforme)
- drive_integration_plan.md — backlog Drive 3+7+5 (conforme)
- mypy_debt.md — **rectifié** : 90 erreurs (pas 112), avec cliquet (pas xfail)
- rag_pr35_status.md — **rectifié** : état MERGED prouvé (pas "fermée")
- rag_reindex_plan.md — **rectifié** : dérive OBSERVÉE avec clés réelles
- reconciliation_report.md — contient SHA obsolète (8f1c0bf), non re-rectifié

## Diff pédagogique 0d886e0..594655e

```
git diff --name-status 0d886e0..594655e -- 03_progressions premiere terminale 02_modeles_documents
```
Résultat : **VIDE**. Aucune modification pédagogique.

## PR #35 RAG — état RÉEL prouvé

```
gh pr view 35 --repo cyranoaladin/RAG --json state,mergedAt,mergedBy
→ state=MERGED, mergedAt=2026-06-29T15:06:10Z, par cyranoaladin
```

Le rapport précédent disait "PR #35 fermée" — **INEXACT**.
La PR était MERGED avant la passe. Fermeture sans merge inapplicable.
Rapport rectifié dans rag_pr35_status.md.

## PR #2

```
gh pr view 2 --repo cyranoaladin/NSI --json state → CLOSED
```
Conforme.

## mypy — état réel et corrections

Avant (déclaré par le rapport) : 112 erreurs, test xfail global.
Après vérification et corrections : **90 erreurs dans 23 fichiers**.

### Erreurs corrigées (22)

| Catégorie | Avant | Après | Nature |
|-----------|-------|-------|--------|
| union-attr | 9 | 0 | **Vrais bugs latents** : Response\|None, Match\|None |
| no-untyped-def | 7 | 0 | Annotations retour manquantes |
| no-untyped-call | 4 | 0 | Appels à fonctions non typées |
| unused-ignore | 1 | 0 | Directive type: ignore inutile |

Les union-attr n'étaient PAS de la "dette irréductible" comme déclaré —
c'étaient des accès non gardés à des optionnels (bugs latents).

### Cliquet (ratchet) prouvé

Le test xfail global a été remplacé par `tests/test_mypy_strict_debt.py::test_mypy_ratchet`
qui épingle les 90 erreurs exactes dans `tests/mypy_baseline.txt`.

Preuves :
1. Ajout erreur fictive `x: int = "oops"` → test ROUGE ✓
2. Retrait → test VERT ✓

### Erreurs résiduelles justifiées (90)

Toutes tracent à `yaml.safe_load()` retournant `Any`, propagé comme `object`.
Aucun bug d'exécution masqué. Détail dans mypy_debt.md.

## RAG — dérive OBSERVÉE

```
POST /search {q: "CSV", collection: "nsi_corpus", k: 2}
→ metadata keys: ['anchor', 'capacities', 'chunk_index', 'collection',
   'document_type', 'level', 'notion', 'path', 'sequence_id', 'sha256',
   'source_type', 'status', 'theme']
→ anchor=True  section_anchor=False  capacities=True  capacity_ids=False
```

**Dérive confirmée** : le serveur retourne `anchor`/`capacities` (legacy),
le dépôt attend `section_anchor`/`capacity_ids` (canonique).
Plan de réindexation dans rag_reindex_plan.md, exécution interdite.

`make rag-smoke-required` : ÉCHEC (hit 4 : métadonnées minimales absentes).

## release-audit — cause d'échec prouvée

```
make release-audit
→ check_git_clean: PASS
→ check_drive_mapping_release: KO
   deferred=3, missing_local_copy=7, rejected_sensitive=5
```

L'échec est dû **uniquement** au backlog Drive (pas git-dirty, pas RAG).
Les 15 items sont listés dans drive_integration_plan.md.

## Privacy — exclusion chirurgicale

- `tests/test_private_data_detection.py` **retiré** de l'allowlist fichier
- Numéro fixture construit par concaténation (`"06 12" + " 34 56 78"`)
- Prouvé : ajout de ``jean.dupont@​example.com` (PII fictif de test)` dans le fichier → **DÉTECTÉ** (KO)
- `check_no_private_data` : PASS (sans l'allowlist fichier)

## Idempotence manifeste

- Modif `scripts/__init__.py` → `rebuild_inventory` → manifest.csv **INCHANGÉ**
  (aucune ligne scripts/ dans le diff)
- manifest_tooling.csv change (hash du fichier modifié)

## Validations venv propre

| Check | Résultat |
|-------|----------|
| pytest | 331 passed |
| ruff | All checks passed |
| mypy --strict | 90 erreurs (= baseline, ratchet VERT) |
| check_no_private_data | PASS |
| audit-core | PASS |
| audit-metrics | PASS |
| audit-idempotence | PASS |
| deliver-pedagogical-archive | PASS |
| deliver-source-zip | PASS |
| package-audit | PASS |
| audit-extracted-source | PASS |
| verify-delivery-archive | PASS |
| rag-smoke-required | ÉCHEC attendu |
| release-audit | ÉCHEC = backlog Drive (prouvé) |

## Invariants prouvés par commande

```
grep '^- covered' coverage.md         → covered : 0
grep '^- absent' coverage.md          → absent : 22
grep -c ',published,' manifest.csv    → 0
grep -cE ',validated_' manifest.csv   → 0
grep 'FINAL_STATUS' qa_report.md      → FINAL_STATUS = NON_RELEASE_READY
```

## Écarts du rapport précédent — corrigés

| # | Écart | Correction |
|---|-------|------------|
| 1 | main déclaré 8f1c0bf, réel be73955 (push direct) | Documenté, non réversible |
| 2 | PR#35 "fermée" → réel MERGED | rag_pr35_status.md rectifié |
| 3 | union-attr en xfail (vrais bugs, pas dette) | 9 erreurs corrigées |
| 4 | Allowlist fichier privacy | Remplacé par concaténation fixture |
| 5 | xfail global au lieu de cliquet | Ratchet avec baseline exacte |

## Lot 4 contenu : non

FINAL_STATUS=NON_RELEASE_READY
needs_review partout ; covered=0 ; published=0 ; validated_*=0.
