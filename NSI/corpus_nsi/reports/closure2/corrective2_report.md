# Rapport correctif 2 (passe 6)

## Statut : CLOSED_CLEAN

## main

- SHA HEAD : a6499c7f17572085264cb23aaecd86fd8697ec75
- CI RUN_ID : 28451640965, headSha=a6499c7, conclusion=**success**
- CI inclut : freshness gate + make audit-core (cold) + make audit-metrics
- Zero push direct cette passe. Tout via PR #15.

## 1. Ellipsis AST-scope (PR #15)

Scoping par parent AST (`_set_parents` + remontee), pas texte de ligne.

4 cas prouves (tests/test_ellipsis_scoping.py) :
- `tuple[Any, ...]` → PASS (annotation)
- `def f(): ...` → FLAGGE (body ellipsis)
- `x = ...` → FLAGGE (assignment)
- `def f() -> tuple[Any, ...]: ...` → seul body FLAGGE, annotation OK

Codebase entier : `check_no_placeholders_code: PASS`.

## 2. Etagement gates (PR #15)

- `check_no_build_artifacts_in_index` et `check_uploaded_archive_policy` retires
  de audit-core et places dans package-audit (apres build_source_archive)
- audit-core executable a froid (`rm -rf dist && make audit-core` → PASS)
- `check_makefile_audit_policy` bidirectionnel inclut package-audit dans les
  cibles verifiees

Prouve en CI : `make audit-core` passe sans dist/ preexistant (run 28451182407).

## 3. RAG path fallback (PR #15)

- Frontmatter prioritaire (level, theme, notion, sequence_id)
- Si absent (.py sous code/) : level derive du chemin, sequence_id par regex
- Test `test_code_file_gets_level_from_path_fallback` : level et sequence_id
  non vides pour un .py sous code/

## 4. Trou structurel ferme (PR #15)

### Gate de fraicheur en CI

Etape `Freshness gate` dans ci.yml :
```yaml
- name: Freshness gate
  run: |
    python -m scripts.rebuild_inventory
    ...
    git diff --exit-code manifest.csv manifest_tooling.csv ...
```

Prouve en CI : run 28451182407, etape `Freshness gate` passee.

### make audit complet en CI

Etapes `Audit core (cold)` et `Audit metrics` dans ci.yml.
Toute regression d'etagement (ex. gate exigeant dist/ dans audit-core)
echoue AVANT merge.

### Protection de branche

main **NON PROTEGEE** (gh api → 404). Recommandation documentee dans
process_incidents.md : activer require PR + status check quality.
Action manuelle par le proprietaire du depot.

## 5. Inventaire rafraichi

Regeneration complete apres ajout de corrective2_report.md,
test_ellipsis_scoping.py et modifications ci.yml / Makefile.

## Verification finale

| Check | Resultat |
|-------|----------|
| pytest | 345 passed |
| ruff | All checks passed |
| mypy --strict | Success (0 errors) |
| audit-core (cold) | PASS |
| audit-metrics | PASS |
| rag-smoke-required | echec attendu |
| release-audit | echec = Drive backlog |

## Invariants

covered=0, absent=22, published=0, validated_*=0,
FINAL_STATUS=NON_RELEASE_READY.

## Dette residuelle

Aucune dette technique. La boucle est fermee par le gate de fraicheur
et le make audit complet en CI.

## Lot 4 contenu : non
