# Gouvernance BUILD_MANIFEST 1NSI Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rendre la portee de revue 1NSI coherente avec le `BUILD_MANIFEST` courant et reattester honnetement les 349 qualifications sous le nouveau protocole.

**Architecture:** Le HEAD propre apres cloture C3 devient la nouvelle base de portee. La policy et ses tests migrent d'abord, ce qui ouvre une transition rouge bornee ; six relecteurs independants reattestent ensuite les six lots et leurs recus sont scelles ensemble, puis les 349 findings sont reconstruits depuis ces blobs immuables pour refermer la transition.

**Tech Stack:** Python 3.12, pytest, PyYAML, JSON Schema Draft 2020-12, Git.

**Design:** `docs/superpowers/specs/2026-08-10-c3-build-manifest-governance-design.md`

---

## Chunk 1: Nouvelle base et policy

### Task 1: Migrer le garde de portee

**Files:**
- Modify: `NSI/tests/test_1nsi_content_reviews.py`
- Modify: `audit/1NSI_CONTENT_REVIEW_POLICY.yaml`

- [ ] **Step 1: Capturer la base propre**

Apres la cloture complete du plan C3 :

```bash
git status --short --branch
git diff --check
git rev-parse HEAD
```

Exiger un worktree propre. Conserver le SHA complet comme
`GOVERNANCE_BASE_SHA`. Verifier que `audit/BUILD_MANIFEST.json` est valide et
calculer son SHA-256 courant comme `BUILD_MANIFEST_SHA256`.

- [ ] **Step 2: Ecrire le test rouge de migration**

Ajouter un test `test_build_manifest_governance_uses_current_clean_base` qui
exige :

- `scope_guard.implementation_base_sha == GOVERNANCE_BASE_SHA` ;
- le chemin et le SHA-256 courant de `audit/BUILD_MANIFEST.json` ;
- le `protocol_digest` recalcule exact ;
- les sept hashes PDF et le fingerprint TNSI inchanges ;
- `review_module.verify_scope(ROOT, policy)` sans exception.

Ajouter un test de transition
`test_policy_migration_invalidates_only_review_envelopes`. Pour chacun des six
anciens recus, il valide le schema, l'affectation, les sources, les ancres et
les payloads, puis exige que les seules differences avec la policy migree
soient `protocol_digest` et les `dependency_digest` qui en dependent.

- [ ] **Step 3: Observer le rouge**

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py \
  -k 'build_manifest_governance_uses_current_clean_base or policy_migration_invalidates_only_review_envelopes'
```

Expected: echec sur l'ancien SHA de base, l'ancien hash du manifeste et le
digest de protocole obsolete.

- [ ] **Step 4: Migrer la policy**

Mettre a jour uniquement :

```yaml
scope_guard:
  implementation_base_sha: <GOVERNANCE_BASE_SHA>
  build_manifest:
    path: audit/BUILD_MANIFEST.json
    sha256: <BUILD_MANIFEST_SHA256>
```

Recalculer ensuite `protocol_digest` avec
`review_module.compute_protocol_digest(ROOT, policy)`, puis inscrire exactement
le resultat. Mettre a jour `BASE_SHA` dans le test. Ne modifier ni la decision
humaine, ni les sources officielles, ni les PDF, ni TNSI, ni l'allowlist.

- [ ] **Step 5: Verifier la premiere transition bornee**

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py \
  -k 'policy or scope or build_manifest_governance or policy_migration_invalidates_only_review_envelopes'
python scripts/review_1nsi_content.py --verify-scope
```

Expected: les tests cibles et `--verify-scope` retournent 0. La suite complete
reste temporairement rouge uniquement parce que les six recus et les findings
portent l'ancien protocole.

- [ ] **Step 6: Committer la policy migree**

```bash
git diff --check
git status --short
git add NSI/tests/test_1nsi_content_reviews.py \
  audit/1NSI_CONTENT_REVIEW_POLICY.yaml
git diff --cached --check
git commit -m "[AUDIT] migre la gouvernance BUILD_MANIFEST 1NSI"
```

Conserver le SHA comme `POLICY_COMMIT` et verifier que son parent direct est
`GOVERNANCE_BASE_SHA`.

## Chunk 2: Six reattestations independantes

### Task 2: Reattester et sceller les six lots

**Files:**
- Modify: `NSI/tests/test_1nsi_content_reviews.py`
- Modify: `audit/reviews/1nsi/runs/2026-08-10-contracts.yaml`
- Modify: `audit/reviews/1nsi/runs/2026-08-10-algorithms.yaml`
- Modify: `audit/reviews/1nsi/runs/2026-08-10-systems-web.yaml`
- Modify: `audit/reviews/1nsi/runs/2026-08-10-language-project.yaml`
- Modify: `audit/reviews/1nsi/runs/2026-08-10-data-basics-tables.yaml`
- Modify: `audit/reviews/1nsi/runs/2026-08-10-types-construits.yaml`

- [ ] **Step 1: Mandater six relecteurs distincts**

Creer en parallele un agent en lecture seule pour chacun des six lots. Capturer
les six IDs d'orchestrateur. Exiger qu'ils soient deux a deux distincts,
differents de `policy.integrator_id` et absents des six recus precedents.

Chaque relecteur recoit la policy migree, son affectation exacte et son ancien
recu comme point de comparaison, mais doit verifier lui-meme les sources,
ancres, verdicts, anomalies et controles executables. Il rend une attestation
par objet et signale toute anomalie nouvelle ; il ne modifie aucune source.

- [ ] **Step 2: Ecrire le test rouge de pre-scellement**

Ajouter `test_all_review_receipts_match_current_governance_before_sealing`. Le
test exige :

- six IDs et six runs nouveaux, deux a deux distincts ;
- reviewers distincts de l'integrateur et des six anciens reviewers ;
- couverture exacte et sans doublon des 349 sources ;
- schema ferme, protocole, hashes d'outils, sources et digests courants ;
- faits et ancres valides, coherence verdict/anomalies ;
- executions fraiches vertes pour les objets executables ;
- un `reviewed_at` strictement posterieur a celui du recu remplace pour chaque
  lot ;
- absence de toute reference TNSI.

- [ ] **Step 3: Observer le rouge des six enveloppes**

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py \
  -k all_review_receipts_match_current_governance_before_sealing
```

Expected: echec sur le protocole, les digests, les identites et les runs des
six anciens recus.

- [ ] **Step 4: Integrer les six reattestations**

Pour chaque lot, enregistrer fidelement l'identite de l'agent, un run nouveau,
le protocole courant, le manifeste courant et les payloads reattestes. Ne
conserver un ancien payload que si le nouveau relecteur l'a explicitement
confirme apres verification. Arreter sur toute anomalie nouvelle au lieu de
forcer les totaux historiques.

- [ ] **Step 5: Verifier les recus avant scellement**

Avant le commit, convertir
`test_policy_migration_invalidates_only_review_envelopes` en preuve historique :
il charge les six anciens blobs par
`git show POLICY_COMMIT^:<receipt_path>` et verifie qu'ils n'etaient invalides
que par le nouveau protocole et ses digests. Le test ne doit plus inspecter les
recus courants pour cette transition.

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py \
  -k 'all_review_receipts_match_current_governance_before_sealing or policy_migration_invalidates_only_review_envelopes'
git diff --check
git status --short
```

Expected: test vert ; seuls le test et les six recus sont modifies.

- [ ] **Step 6: Sceller les six recus ensemble**

```bash
git add NSI/tests/test_1nsi_content_reviews.py \
  audit/reviews/1nsi/runs/2026-08-10-contracts.yaml \
  audit/reviews/1nsi/runs/2026-08-10-algorithms.yaml \
  audit/reviews/1nsi/runs/2026-08-10-systems-web.yaml \
  audit/reviews/1nsi/runs/2026-08-10-language-project.yaml \
  audit/reviews/1nsi/runs/2026-08-10-data-basics-tables.yaml \
  audit/reviews/1nsi/runs/2026-08-10-types-construits.yaml
git diff --cached --check
git commit -m "[AUDIT] rescelle les 349 revues sous BUILD_MANIFEST"
```

Conserver `RECEIPTS_COMMIT` et le SHA-256 de chacun des six blobs. Verifier que
le parent direct est `POLICY_COMMIT`.

## Chunk 3: Provenance des 349 qualifications

### Task 3: Reconstruire le registre depuis les recus scelles

**Files:**
- Modify: `NSI/tests/test_1nsi_content_reviews.py`
- Modify: `audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml`
- Modify: `audit/1NSI_CONTENT_REVIEWS.json`
- Modify: `audit/1NSI_CONTENT_REVIEW_SUMMARY.md`

- [ ] **Step 1: Ecrire le test de seconde transition**

Ajouter les constantes `RECEIPTS_COMMIT` et les six hashes. Verifier par
`git show` que chaque blob courant est identique au blob scelle. Avant la mise
a jour des findings, comparer chaque entree au recu scelle et exiger que les
seules differences restantes soient les anciens payloads reattestes et/ou les
champs de provenance de l'ancien recu. Toute difference de couverture,
d'identite de source, de chemin, de statut ou de capacite est interdite.

Remplacer explicitement les constantes et assertions speciales historiques des
recus `contracts` et `algorithms` par une table uniforme des six recus courants.
Conserver les preuves historiques C3 et contrats via `git show` sans exiger que
leurs anciens blobs soient encore les fichiers courants. Le test uniforme
verifie les six hashes, le commit commun, les identites, runs et 349 payloads.

- [ ] **Step 2: Observer la transition rouge bornee**

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py \
  -k 'sealed_current_governance_receipts or findings_only_differ_on_reattested_payload_or_provenance'
```

Expected: blobs scelles verts ; findings signales uniquement pour payload
reatteste et/ou provenance obsolete.

- [ ] **Step 3: Reconstruire les 349 findings**

Pour chaque review des six recus, recopier exactement son payload. Deriver les
champs de source depuis la decouverte courante et reconstruire la provenance
avec reviewer, run, modele, integrateur, chemin du recu, SHA-256 du blob et
`RECEIPTS_COMMIT`. Mettre aussi a jour l'en-tete global des findings :
`review_run_id`, `review_receipt_path`, `review_receipt_sha256` et
`sealing_commit_sha` prennent exactement les valeurs du nouveau recu
`contracts`. Ne modifier aucun statut.

Regenerer deterministement :

```bash
python scripts/review_1nsi_content.py \
  --findings audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml \
  --output-json audit/1NSI_CONTENT_REVIEWS.json \
  --output-summary audit/1NSI_CONTENT_REVIEW_SUMMARY.md
python scripts/review_1nsi_content.py \
  --findings audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml \
  --output-json audit/1NSI_CONTENT_REVIEWS.json \
  --output-summary audit/1NSI_CONTENT_REVIEW_SUMMARY.md --check
```

- [ ] **Step 4: Fermer la transition et committer**

Mettre le test de transition dans son etat final : zero provenance obsolete,
349 findings egaux aux payloads scelles, totaux issus des recus. Puis :

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py
git diff --check
git status --short
git add NSI/tests/test_1nsi_content_reviews.py \
  audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml \
  audit/1NSI_CONTENT_REVIEWS.json \
  audit/1NSI_CONTENT_REVIEW_SUMMARY.md
git diff --cached --check
git commit -m "[AUDIT] rattache les 349 qualifications aux recus courants"
```

## Chunk 4: Gates finaux

### Task 4: Verifier la gouvernance sans publier

**Files:**
- Modify if generated: `ETAT_COLLECTION.md`
- Modify if generated: `audit/ECARTS_ET_CONTRADICTIONS.yaml`
- Modify if generated: `audit/INVENTAIRE_COLLECTION.json`
- Modify if generated: `audit/MATRICE_LIVRABLES.yaml`

- [ ] **Step 1: Executer les suites completes**

```bash
cd NSI && pytest -q tests
cd .. && pytest -q tests/test_inventory_collection.py
python scripts/review_1nsi_content.py \
  --findings audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml \
  --output-json audit/1NSI_CONTENT_REVIEWS.json \
  --output-summary audit/1NSI_CONTENT_REVIEW_SUMMARY.md --check
python scripts/review_1nsi_content.py --verify-scope
python scripts/inventory_collection.py --check
python scripts/inventory_collection.py --validate-model
python scripts/inventory_collection.py --fail-on-new
```

Expected: toutes les commandes retournent 0.

- [ ] **Step 2: Verifier le refus de release attendu**

Executer `python scripts/inventory_collection.py --release-strict`, parser le
JSON et exiger le code 7, `success: false`, au moins un blocage reel et aucune
raison `inventaire_indisponible:`.

- [ ] **Step 3: Regenerer l'inventaire uniquement si necessaire**

Si `--check` retourne 3 uniquement pour `diff:` ou `manquant:`, executer le
generateur puis inspecter le diff. Arreter et diagnostiquer si
`audit/AUDIT_CONSOLIDE.md`, `audit/INVENTAIRE_COLLECTION.md` ou tout autre
chemin absent de l'allowlist a change. Sinon, reverifier puis committer seulement
les quatre sorties autorisees effectivement modifiees avec :

```bash
git add \
  ETAT_COLLECTION.md \
  audit/ECARTS_ET_CONTRADICTIONS.yaml \
  audit/INVENTAIRE_COLLECTION.json \
  audit/MATRICE_LIVRABLES.yaml
git diff --cached --name-only
git diff --cached --check
git commit -m "[AUDIT] resynchronise l inventaire apres BUILD_MANIFEST"
```

- [ ] **Step 4: Verifier TNSI et l'etat final**

```bash
git diff --quiet 5fa8946872e3263049be1b3c0cdf78203596e581 -- \
  'NSI/chapitres/TNSI-*' 'NSI/referentiel/capacites_TNSI_*' \
  NSI/docs/11_perimetre_terminale.md \
  NSI/sources/txt/BO2019_NSI_terminale.txt 'NSI/build/MANUEL_TNSI*'
git status --porcelain -- \
  'NSI/chapitres/TNSI-*' 'NSI/referentiel/capacites_TNSI_*' \
  NSI/docs/11_perimetre_terminale.md \
  NSI/sources/txt/BO2019_NSI_terminale.txt 'NSI/build/MANUEL_TNSI*'
git diff --check
git status --short --branch
git rev-parse HEAD
git log --oneline --decorate -12
```

Expected: aucun diff ni fichier TNSI, aucun WIP final et `--verify-scope` vert.
