# Six P0 1NSI Governance And Build Manifest Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rafraichir le manifeste vide, migrer une seule fois la gouvernance 1NSI, reattester independamment les 349 revues et reconstruire leurs sorties canoniques apres les six P0 corriges.

**Architecture:** Le `BUILD_MANIFEST` est traite dans un commit atomique avant la policy parce que son SHA est scelle par le protocole de revue. Une base Git propre est ensuite epinglee dans la policy ; six reviewers distincts reattestent les six lots, leurs recus sont scelles ensemble, puis les findings sont reconstruits exclusivement depuis ces blobs immuables.

**Tech Stack:** Python 3.12, pytest, PyYAML, JSON Schema Draft 2020-12, Git, scripts d'inventaire Nexus.

---

## Chunk 1: BUILD_MANIFEST Separe Et Base Propre

### Task 1: Fermer le registre de schemas

**Files:**
- Modify: `scripts/inventory_collection.py`
- Test: `tests/test_inventory_collection.py`

- [ ] **Step 1: Confirmer le rouge existant**

Run: `pytest -q tests/test_inventory_collection.py::test_v1_schema_directory_contains_exactly_the_registered_contracts`

Expected: FAIL parce que `1nsi-p0-correction-attestation.schema.json` est present mais non enregistre.

- [ ] **Step 2: Enregistrer le schema sans modifier son contrat**

Ajouter l'artifact type `1nsi_p0_correction_attestation`, version `1`, vers `audit/schemas/v1/1nsi-p0-correction-attestation.schema.json` dans `SCHEMA_REGISTRY`.

- [ ] **Step 3: Verifier et committer**

Run: `pytest -q tests/test_inventory_collection.py::test_v1_schema_directory_contains_exactly_the_registered_contracts NSI/tests/test_1nsi_p0_attestations.py`.

Commit: `[CI] enregistre le schema des attestations P0 1NSI`.

### Task 2: Rafraichir le manifeste vide et l'inventaire

**Files:**
- Modify: `audit/BUILD_MANIFEST.json`
- Modify if generated: `ETAT_COLLECTION.md`
- Modify if generated: `audit/ECARTS_ET_CONTRADICTIONS.yaml`
- Modify if generated: `audit/INVENTAIRE_COLLECTION.json`
- Modify if generated: `audit/INVENTAIRE_COLLECTION.md`
- Modify if generated: `audit/MATRICE_LIVRABLES.yaml`

- [ ] **Step 1: Exiger une base propre puis rafraichir uniquement l'enveloppe vide**

Run: `python scripts/build_manifest.py --refresh-empty`.

Expected: `builds` reste `[]`; seuls provenance, `source_digest` et `model_digest` derivables changent.

- [ ] **Step 2: Verifier et committer le manifeste seul**

Run: `python -m json.tool audit/BUILD_MANIFEST.json`, puis les tests `build_manifest`/inventaire cibles.

Commit: `[AUDIT] rafraichit le manifeste vide apres les six P0 1NSI`.

- [ ] **Step 3: Resynchroniser l'inventaire de facon bornee**

Run d'abord `python scripts/inventory_collection.py --check`. N'autoriser la generation que pour des raisons `diff:` ou `manquant:` et uniquement pour les six sorties gerees listees ci-dessus. Executer ensuite `python scripts/inventory_collection.py`, inspecter le diff, puis `--check`, `--validate-model` et `--fail-on-new`.

Commit eventuel: `[AUDIT] resynchronise l inventaire apres les six P0 1NSI`.

- [ ] **Step 4: Capturer la base propre**

Exiger `git status --porcelain` vide. Conserver le HEAD comme `GOVERNANCE_BASE_SHA`, le SHA-256 du manifeste, les sept hashes PDF et le fingerprint TNSI.

## Chunk 2: Migration De La Policy

### Task 3: Migrer et borner la premiere transition

**Files:**
- Modify: `NSI/tests/test_1nsi_content_reviews.py`
- Modify: `audit/1NSI_CONTENT_REVIEW_POLICY.yaml`

- [ ] **Step 1: Ecrire les tests rouges**

Epingler `GOVERNANCE_BASE_SHA`, le nouveau hash du manifeste et le futur digest. Ajouter une preuve historique qui charge les six recus depuis le parent du futur commit policy et derive exactement les champs perimes : protocole et dependances pour tous, source/faits seulement pour les lots affectes.

- [ ] **Step 2: Observer le rouge**

Run: `pytest -q NSI/tests/test_1nsi_content_reviews.py -k 'scope or policy_migration or build_manifest_governance'`.

- [ ] **Step 3: Migrer minimalement**

Modifier seulement `scope_guard.implementation_base_sha`, `scope_guard.build_manifest.sha256` et `protocol_digest` recalcule par `compute_protocol_digest`.

- [ ] **Step 4: Verifier et committer**

Run les tests policy cibles et `python scripts/review_1nsi_content.py --verify-scope`.

Commit: `[AUDIT] migre la gouvernance apres les six P0 1NSI`.

## Chunk 3: Six Reattestations Independantes

### Task 4: Reattester et sceller les 349 revues

**Files:**
- Modify: `NSI/tests/test_1nsi_content_reviews.py`
- Modify: `audit/reviews/1nsi/runs/2026-08-10-contracts.yaml`
- Modify: `audit/reviews/1nsi/runs/2026-08-10-algorithms.yaml`
- Modify: `audit/reviews/1nsi/runs/2026-08-10-systems-web.yaml`
- Modify: `audit/reviews/1nsi/runs/2026-08-10-language-project.yaml`
- Modify: `audit/reviews/1nsi/runs/2026-08-10-data-basics-tables.yaml`
- Modify: `audit/reviews/1nsi/runs/2026-08-10-types-construits.yaml`

- [ ] **Step 1: Mandater six reviewers distincts en lecture seule**

Un reviewer par lot. Exiger des IDs et runs nouveaux, deux a deux distincts, distincts de l'integrateur et des identites historiques. Chaque reviewer controle son affectation complete, les sources, dependances, faits, anomalies et executions applicables ; aucune ancienne anomalie n'est supprimee sans constat explicite.

- [ ] **Step 2: Ecrire et observer le test rouge de pre-scellement**

Le test exige schema ferme, protocole/outils/manifeste courants, couverture exacte 349/349, faits valides, executions fraiches, absence TNSI et nouveaux horodatages.

- [ ] **Step 3: Integrer fidelement les six avis**

Reconstruire chaque enveloppe et manifeste depuis l'etat courant. Conserver un ancien payload seulement si le reviewer le confirme ; retirer les six IDs P0 corriges et tout autre finding uniquement sur preuve independante.

- [ ] **Step 4: Verifier et sceller ensemble**

Run les tests de pre-scellement et la preuve historique de migration.

Commit: `[AUDIT] rescelle les 349 revues apres les six P0`.

Conserver `RECEIPTS_COMMIT` et les six SHA-256.

## Chunk 4: Findings Canoniques

### Task 5: Reconstruire les 349 findings depuis les recus scelles

**Files:**
- Modify: `NSI/tests/test_1nsi_content_reviews.py`
- Modify: `audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml`
- Modify: `audit/1NSI_CONTENT_REVIEWS.json`
- Modify: `audit/1NSI_CONTENT_REVIEW_SUMMARY.md`

- [ ] **Step 1: Ecrire la transition bornee**

Verifier les six blobs par `git show`, les 349 identites immuables et borner les differences aux payloads/provenances reattestes.

- [ ] **Step 2: Reconstruire et regenerer**

Recopier exactement les payloads scelles, deriver les champs de source courants et la provenance du commit commun. Regenerer JSON et resume avec `scripts/review_1nsi_content.py`.

- [ ] **Step 3: Verifier les deltas**

Exiger 349 entries, absence des six IDs P0 corriges, totaux derives et aucune reference TNSI.

- [ ] **Step 4: Committer**

Commit: `[AUDIT] rattache les 349 qualifications apres les six P0`.

## Chunk 5: Verification Finale Sans Publication

### Task 6: Executer tous les gates

**Files:** aucun attendu.

- [ ] **Step 1: Suites completes**

Run `pytest -q NSI/tests`, `pytest -q tests/test_inventory_collection.py tests/test_build_manifest.py`, les trois modes `review_1nsi_content.py`, puis `inventory_collection.py --check --validate-model --fail-on-new` separement.

- [ ] **Step 2: Refus de release attendu**

Run `python scripts/inventory_collection.py --release-strict`; exiger le code 7, `success: false`, des blocages reels et aucune raison `inventaire_indisponible:`.

- [ ] **Step 3: Gardes finales**

Exiger `git diff --check`, worktree propre, aucune modification TNSI depuis `93c3c726`, policy scope verte, six recus scelles et 349 findings coherents.
