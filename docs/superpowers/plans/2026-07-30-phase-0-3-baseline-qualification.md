# Phase 0.3 Baseline Qualification Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Qualifier individuellement la dette active par une politique déterministe approuvée, geler une baseline de non-régression et rendre `--fail-on-new` vert sans rendre la dette acceptable pour une release.

**Architecture:** Un module pur charge et interprète la politique, sans jamais
l’appliquer automatiquement pendant `build_inventory`. Le générateur principal
orchestre la matérialisation ponctuelle du lot approuvé avec son infrastructure
FD-confinée, verrouillée, journalisée et récupérable. Il contrôle ensuite la
cohérence politique/dispositions/rapports non qualifiés. Le gel reste une
opération distincte, explicite, interdite en CI et transactionnelle.

**Tech Stack:** Python 3.12, PyYAML, JSON Schema 2020-12, pytest, générateur `inventory_collection.py`, Git.

---

## Frontières de digest et jeu approuvé

La politique enregistre des preuves d’entrée nommées
`observed_source_digest_before_materialization` et
`observed_model_digest_before_materialization`. Elles ne sont vérifiées qu’au
préflight read-only du lot initial et ne sont jamais interprétées comme des
digests post-matérialisation.

Le fingerprint set approuvé est recalculé depuis les anomalies brutes et les
seules quatre dispositions historiques. Son digest ne dépend ni des nouvelles
dispositions ni des rapports générés. Après matérialisation, la chaîne est
unidirectionnelle :

```text
policy.control_digest
  → disposition.qualification_policy_digest
  → ANOMALY_DISPOSITIONS.control_digest
  → qualification_digest individuel
  → model_digest
  → baseline_digest
```

La policy ne référence jamais le digest futur des dispositions, du modèle
post-politique ou de la baseline. Les rapports `UNQUALIFIED_*` sont des sorties
gérées et ne sont jamais des sources du modèle qu’ils décrivent.

## Matrice exhaustive du lot initial

| Catégorie | Nombre | Disposition | Règle propriétaire |
|---|---:|---|---|
| `blocking_statuses` | 1 796 | `open_debt` | type canonique de l’objet ; contrat → ingénierie |
| `unassembled_objects` | 614 | `open_debt` | ingénierie, car le contenu existe et l’assemblage manque |
| `broken_meta_references` | 24 | `open_debt` | ingénierie |
| `unavailable_inspiration_sources` | 15 | `open_debt` | éditorial/pédagogique |
| `chapters_not_in_manual` | 4 | `open_debt` | éditorial/pédagogique |
| `missing_assemblers` | 3 | `open_debt` | ingénierie |
| `unattributed_pdfs` | 1 | `open_debt` | ingénierie |
| **Total** | **2 457** | | |

Le routage par types canoniques doit produire exactement :

- `direction_scientifique_programme` : 1 473 ;
- `direction_editoriale_pedagogique` : 328 ;
- `ingenierie_build_qualite` : 656.

Ces nombres portent uniquement sur les 2 457 décisions créées par la politique.
Après normalisation des quatre preuves historiques, le registre complet de
2 461 dispositions doit compter respectivement `1 473/331/657`.

Les trois contrats au statut `complete`, non `approved`, appartiennent à la
dernière répartition et restent `open_debt`. Zéro ou plusieurs règles
applicables à un fingerprint entraînent son inscription comme non qualifié et
interdisent toute écriture des dispositions.

## Chunk 1: Contrat et matérialisation de la politique

### Task 0: Consigner le plan approuvé

**Files:**
- Modify: `audit/BASELINE_QUALIFICATION_DECISION.md`
- Create: `docs/superpowers/plans/2026-07-30-phase-0-3-baseline-qualification.md`

- [ ] **Step 1: Vérifier et committer les deux documents**

La décision précise le statut strict des trois contrats `complete` non
`approved`. Vérifier le diff puis stage uniquement les deux chemins :

```bash
git status --short
git diff --check
git add -- \
  audit/BASELINE_QUALIFICATION_DECISION.md \
  docs/superpowers/plans/2026-07-30-phase-0-3-baseline-qualification.md
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "[AUDIT][P0.3] verrouille le plan de qualification"
```

### Task 1: Versionner le schéma de politique

**Files:**
- Create: `audit/schemas/v1/baseline-qualification-policy.schema.json`
- Create: `audit/BASELINE_QUALIFICATION_POLICY.yaml`
- Modify: `scripts/inventory_collection.py`
- Test: `tests/test_inventory_collection.py`

- [ ] **Step 1: Écrire les tests de schéma en échec**

Ajouter des tests exigeant :

- les trois propriétaires et leurs scopes exacts ;
- la décision `baseline-debt-regression-control-2026-07-30` ;
- le SHA, les digests et le nombre `2457` approuvés ;
- les sept dispositions autorisées, dont `harvest_candidate` ;
- des règles ordonnées avec identifiant unique ;
- l’interdiction de `accepted_exception` dans les sorties de la politique
  initiale ;
- les décomptes exacts par catégorie et propriétaire ;
- un `control_digest` cohérent.

- [ ] **Step 2: Vérifier RED**

Run:

```bash
python -m pytest tests/test_inventory_collection.py \
  -q -k 'qualification_policy_schema or harvest_candidate_disposition'
```

Expected: FAIL parce que le schéma, le fichier et la disposition
`harvest_candidate` n’existent pas.

- [ ] **Step 3: Ajouter le contrat minimal**

Enregistrer le nouveau schéma dans `SCHEMA_REGISTRY`. Ajouter
`harvest_candidate` de bout en bout aux constantes, au mapping de blocage et
aux schémas dispositions/baseline, tout en testant qu’aucun des 2 457
fingerprints actifs ne reçoit cette disposition : les candidats harvest
restent des sources séparées et non publiables. Créer ensuite la politique
approuvée. Le fichier doit contenir l’empreinte du jeu approuvé :

```yaml
approved_set:
  baseline_sha: 27082043c45fc405299e335f6eb7475f01288e27
  fingerprint_count: 2457
  fingerprint_digest: sha256:ee6220cca262a6d5f331e7e86c514960c859f3b452c46ce24ac714ad521f13e8
```

- [ ] **Step 4: Vérifier GREEN**

Run the same targeted test command.

Expected: PASS.

### Task 2: Définir l’API pure de classification

**Files:**
- Create: `scripts/baseline_qualification.py`
- Modify: `pyproject.toml`
- Test: `tests/test_baseline_qualification.py`

- [ ] **Step 1: Écrire les tests de classification en échec**

Construire de petites anomalies réelles couvrant :

- statuts de production et contrat ;
- cours/exercice/QCM/corrigé mathématique ;
- activité/remédiation/variante ;
- assemblage, META, LaTeX, PDF et référence technique ;
- chapitre manquant ;
- assembleur seul manquant ;
- correction absente ;
- `_harvest/**/*.candidate.tex` ;
- dépendance générée avec et sans producteur prouvé ;
- réutilisation avec et sans preuve éditoriale ;
- catégorie inconnue.

Ajouter un test dépôt verrouillant les sept catégories, leurs nombres et les
comptes propriétaires `1473/328/656`. Les trois contrats `complete` doivent
matcher uniquement la règle contrat non approuvé.

L’API souhaitée :

```python
decision = classify_anomaly(policy, category, anomaly)
```

Une décision contient `policy_rule`, `disposition`, `owner`,
`release_blocking` et `reason`; une absence de règle retourne `None`.

- [ ] **Step 2: Vérifier RED**

Run:

```bash
python -m pytest tests/test_baseline_qualification.py -q
```

Expected: ERROR/FAIL parce que le module n’existe pas.

- [ ] **Step 3: Implémenter le classifieur minimal**

Implémenter des règles explicites sans priorité cachée. Un candidat doit
matcher exactement une règle. Ne pas ajouter de règle catch-all : une
catégorie ou un type canonique inconnu doit rester non qualifié. Les règles
doivent être pilotées par le fichier YAML et les champs stables de l’anomalie,
pas par un numéro de ligne ou un texte de rapport généré.

- [ ] **Step 4: Vérifier GREEN et typer**

Run:

```bash
python -m pytest tests/test_baseline_qualification.py -q
python -m mypy scripts/baseline_qualification.py
python -m ruff check scripts/baseline_qualification.py \
  tests/test_baseline_qualification.py
```

Expected: PASS.

### Task 3: Matérialiser les dispositions et les non-qualifiées

**Files:**
- Modify: `scripts/baseline_qualification.py`
- Modify: `scripts/inventory_collection.py`
- Modify: `audit/schemas/v1/anomaly-dispositions.schema.json`
- Create: `audit/schemas/v1/unqualified-anomalies.schema.json`
- Test: `tests/test_baseline_qualification.py`
- Test: `tests/test_inventory_collection.py`

- [ ] **Step 1: Écrire les tests de matérialisation en échec**

Exiger :

- vérification count/digest avant écriture ;
- une entrée individuelle par fingerprint ;
- conservation et normalisation des quatre décisions prouvées existantes ;
- absence de doublons et de fingerprints inconnus ;
- champs `fingerprint_schema_version`, `category`, `severity`, `manual`,
  `chapter`, `source`, `disposition`, `owner`, `release_blocking`,
  `policy_rule`, `reason`, `approved_by`, `baseline_sha`, `decision_ref` et
  `justification` ;
- égalité contractuelle entre `release_blocking` et le caractère `blocking`
  dérivé : `open_debt=true`, `harvest_candidate=false`,
  `generated_dependency=false`, `intentional_reuse=false` ;
- propriétaires parmi les trois valeurs approuvées ;
- aucune `false_positive` sans preuve ;
- aucune `accepted_exception` produite ;
- aucune `fixed` active ;
- production déterministe de `UNQUALIFIED_ANOMALIES.json` et `.md` ;
- refus transactionnel d’une variation du jeu approuvé.

- [ ] **Step 2: Vérifier RED**

Run:

```bash
python -m pytest tests/test_baseline_qualification.py \
  tests/test_inventory_collection.py -q \
  -k 'materialize or unqualified or policy_generated_disposition'
```

Expected: FAIL parce que la matérialisation n’existe pas.

- [ ] **Step 3: Implémenter la matérialisation minimale**

Garder `scripts/baseline_qualification.py` pur. Ajouter l’orchestration à la
CLI existante :

```bash
python scripts/inventory_collection.py \
  --materialize-baseline-qualifications --check
python scripts/inventory_collection.py \
  --materialize-baseline-qualifications
```

L’orchestrateur planifie tout en mémoire, revalide HEAD/count/digests juste
avant l’écriture, puis réutilise `_lock_generation`,
`_recover_repository_transactions` et `_apply_atomic_payloads` pour les trois
sorties. Ajouter les attaques symlink, hardlink, substitution de répertoire,
crash journalisé, HEAD modifié et digest modifié. Aucun import inverse depuis
le module pur vers `inventory_collection.py` n’est autorisé.

- [ ] **Step 4: Vérifier GREEN et la mutation**

Muter temporairement une fixture en :

- owner inconnu ;
- `accepted_exception` ;
- fingerprint dupliqué ;
- fingerprint supplémentaire à total constant.

Chaque mutation doit échouer. Retirer les mutations et conserver les tests.

## Chunk 2: Gates, génération réelle et commit de qualification

### Task 4: Brancher la politique aux gates

**Files:**
- Modify: `scripts/inventory_collection.py`
- Modify: `scripts/ci_audit_collection.py`
- Modify: `audit/ANOMALIES_BASELINE.json`
- Modify: `docs/codex/QUALITY_GATES.md`
- Modify: `pyproject.toml`
- Test: `tests/test_inventory_collection.py`
- Test: `tests/test_ci_audit_collection.py`

- [ ] **Step 1: Écrire les tests de gate en échec**

Exiger que `--validate-model` et `baseline_ready` refusent :

- politique ou digest invalide ;
- registre matérialisé différent de la politique ;
- rapport non qualifié absent ou non vide ;
- owner/disposition inconnus ;
- `accepted_exception` issue de la politique initiale.

Ajouter `qualification_digest` à chaque qualification active et à la baseline.
Ce digest canonique couvre owner, justification/reason, approbateur,
decision_ref, preuve, rule id et policy digest. `--fail-on-new` doit échouer si
ce digest change, même lorsque le fingerprint brut reste identique.

L'égalité stricte entre le jeu brut approuvé et les 2 457 décisions de
politique ne s'applique qu'au preflight one-shot de matérialisation. Après le
gel, une disposition dont l'anomalie brute a disparu reste un historique
valide : `--validate-model` reste vert, `--fail-on-new` la signale comme
amélioration sans échouer, et sa réapparition échoue comme régression.

- [ ] **Step 2: Vérifier RED**

Run:

```bash
python -m pytest tests/test_inventory_collection.py \
  tests/test_ci_audit_collection.py -q \
  -k 'policy_gate or disposition_coverage or validate_model'
```

Expected: FAIL sur les nouveaux contrôles.

- [ ] **Step 3: Implémenter les contrôles minimaux**

Étendre le check `disposition_coverage` sans ajouter un onzième nom de
précondition. Inclure `baseline_qualification.py` dans le fingerprint du
générateur. Propager `qualification_digest` dans `_current_active_debt` et
dans la comparaison baseline. Migrer les quatre entrées de la baseline
provisoire avec ce digest, sans modifier leur jeu actif ni son état
`provisional: true`. Ne jamais lancer l’option de matérialisation depuis la CI.
Documenter ces invariants dans `QUALITY_GATES.md`.

- [ ] **Step 4: Vérifier GREEN**

Run:

```bash
python -m pytest tests/test_baseline_qualification.py \
  tests/test_inventory_collection.py tests/test_ci_audit_collection.py -q
```

Expected: PASS.

### Task 5: Matérialiser le lot réel

**Files:**
- Modify: `audit/ANOMALY_DISPOSITIONS.yaml`
- Create: `audit/UNQUALIFIED_ANOMALIES.json`
- Create: `audit/UNQUALIFIED_ANOMALIES.md`
- Modify: generated audit artifacts if required by `--check`

- [ ] **Step 1: Vérifier le lot avant écriture**

Run:

```bash
python scripts/inventory_collection.py \
  --materialize-baseline-qualifications --check
```

Expected before materialization: non-zero with exactly 2457 missing
dispositions and the approved digest.

- [ ] **Step 2: Matérialiser**

Run:

```bash
python scripts/inventory_collection.py \
  --materialize-baseline-qualifications
```

Expected: 2461 total dispositions, 2457 produced by policy, 0 unqualified,
owner counts `1473/328/656` pour le lot et `1473/331/657` pour le registre
complet, and all 2457 new entries `open_debt` with `release_blocking: true`.

- [ ] **Step 3: Régénérer et vérifier**

Run:

```bash
python scripts/inventory_collection.py
python scripts/inventory_collection.py --check
python scripts/inventory_collection.py --validate-model
python scripts/inventory_collection.py --fail-on-new
```

Expected: `--check` and `--validate-model` green; `--fail-on-new` remains code
5 because the baseline is still provisional.

- [ ] **Step 4: Commit atomique**

Avant staging :

```bash
git status --short
git diff --check
git diff --stat
```

Stage explicit paths only :

```bash
git add -- \
  audit/BASELINE_QUALIFICATION_POLICY.yaml \
  audit/ANOMALY_DISPOSITIONS.yaml \
  audit/ANOMALIES_BASELINE.json \
  audit/UNQUALIFIED_ANOMALIES.json \
  audit/UNQUALIFIED_ANOMALIES.md \
  audit/schemas/v1/baseline-qualification-policy.schema.json \
  audit/schemas/v1/anomaly-dispositions.schema.json \
  audit/schemas/v1/unqualified-anomalies.schema.json \
  audit/schemas/v1/anomalies-baseline.schema.json \
  scripts/baseline_qualification.py \
  scripts/inventory_collection.py \
  scripts/ci_audit_collection.py \
  tests/test_baseline_qualification.py \
  tests/test_inventory_collection.py \
  tests/test_ci_audit_collection.py \
  pyproject.toml \
  docs/codex/QUALITY_GATES.md
```

Ajouter explicitement les six artefacts gérés seulement s’ils ont changé.
Inspecter ensuite :

```bash
git diff --cached --check
git diff --cached --stat
git diff --cached
```

Commit:

```bash
git commit -m \
  "[AUDIT][P0.3] qualifie la dette initiale par politique approuvee"
```

Do not run `--update-baseline` in this commit.

## Chunk 3: Gel explicite et preuves finales

### Task 6: Produire le rapport de gel transactionnel

**Files:**
- Modify: `scripts/inventory_collection.py`
- Modify: `audit/schemas/v1/anomalies-baseline.schema.json`
- Modify: `audit/ANOMALIES_BASELINE.json`
- Test: `tests/test_inventory_collection.py`

- [ ] **Step 1: Écrire le test de rapport en échec**

Exiger que la transaction `--update-baseline` produise aussi
`audit/BASELINE_FREEZE_REPORT.md` avec :

- SHA Git ;
- comptes par catégorie, disposition et propriétaire, en distinguant le lot
  politique `1473/328/656` du registre complet `1473/331/657` ;
- bloquants/non bloquants ;
- non qualifiés ;
- anciennes/nouvelles empreintes ;
- raison et approbateur ;
- `release_acceptance: false`.

Exiger également dans `ANOMALIES_BASELINE.json`, au niveau racine :

```json
{
  "baseline_purpose": "debt_regression_control",
  "release_acceptance": false
}
```

Les deux champs sont requis par le schéma avec `const`, validés au chargement
et par `--validate-model`. Une mutation à `release_acceptance: true` doit
échouer avant toute comparaison de dette.

Le test doit prouver qu’une erreur d’écriture restaure baseline et rapports.

- [ ] **Step 2: Vérifier RED**

Run:

```bash
python -m pytest tests/test_inventory_collection.py -q \
  -k 'baseline_freeze_report or update_baseline'
```

Expected: FAIL parce que le rapport de gel n’est pas produit.

- [ ] **Step 3: Implémenter le rendu minimal**

Calculer les décomptes depuis le payload final et ajouter le rapport à la même
transaction atomique que `ANOMALIES_BASELINE.json` et
`BASELINE_UPDATE_REPORT.md`. Écrire les deux champs contractuels dans les
baselines provisoire et finale. Régénérer explicitement la baseline
provisoire après l'ajout de ces champs, sans changer son jeu actif, son
approbation ni son état `provisional: true`.

- [ ] **Step 4: Vérifier GREEN**

Run the same targeted command.

Expected: PASS.

- [ ] **Step 5: Committer le code du rapport avant le gel**

```bash
git status --short
git diff --check
git add -- \
  scripts/inventory_collection.py \
  audit/schemas/v1/anomalies-baseline.schema.json \
  audit/ANOMALIES_BASELINE.json \
  tests/test_inventory_collection.py
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "[AUDIT][P0.3] prepare le rapport transactionnel de gel"
```

### Task 7: Geler depuis un commit propre

**Files:**
- Modify: `audit/ANOMALIES_BASELINE.json`
- Modify: `audit/BASELINE_UPDATE_REPORT.md`
- Create: `audit/BASELINE_FREEZE_REPORT.md`

- [ ] **Step 1: Vérifier le commit de préparation**

Le worktree doit être propre avant le gel et le dernier commit doit contenir le
code du rapport, jamais la baseline générée.

- [ ] **Step 2: Exécuter les préconditions**

Run:

```bash
python scripts/inventory_collection.py --validate-model
python scripts/inventory_collection.py --require-clean
```

Expected: codes 0.

- [ ] **Step 3: Exécuter la commande explicite**

Run:

```bash
python scripts/inventory_collection.py \
  --update-baseline \
  --reason "État initial qualifié de la dette existante après stabilisation de la Phase 0, utilisé exclusivement pour détecter les régressions et les nouvelles anomalies." \
  --approved-by "Alaeddine Ben Rhouma"
```

Expected: code 0, `provisional: false`, `release_acceptance: false`.

- [ ] **Step 4: Vérifier les gates**

Run:

```bash
python scripts/inventory_collection.py --validate-model
python scripts/inventory_collection.py --fail-on-new
python scripts/inventory_collection.py --release-strict
```

Expected: 0, 0, 7. La liste `release-strict` reste triée et déterministe.

Exécuter `--release-strict` deux fois, exiger 69 raisons identiques et calculer
leur digest JSON canonique. Vérifier aussi que
`ANOMALIES_BASELINE.json.release_acceptance` est strictement `false`.

- [ ] **Step 5: Commit atomique**

Avant staging :

```bash
git status --short
git diff --check
git diff --stat
```

Stage uniquement :

```bash
git add -- \
  audit/ANOMALIES_BASELINE.json \
  audit/BASELINE_UPDATE_REPORT.md \
  audit/BASELINE_FREEZE_REPORT.md
git diff --cached --check
git diff --cached --stat
git diff --cached
```

Commit:

```bash
git commit -m "[AUDIT][P0.3] gele la baseline de non-regression"
```

### Task 8: Vérification complète

**Files:**
- No new files expected

- [ ] **Step 1: Exécuter les tests ciblés et complets**

```bash
python -m pytest tests/test_baseline_qualification.py \
  tests/test_inventory_collection.py tests/test_ci_audit_collection.py -q
python -m pytest -q --import-mode=importlib
```

Expected: tests structurels verts ; les éventuels rouges visuels restent
séparés et non masqués.

- [ ] **Step 2: Vérifier déterminisme et données structurées**

```bash
python scripts/ci_audit_collection.py validate-data \
  --root . --output /tmp/nexus-structured-data.json
```

Après commit et worktree propre, exécuter aussi la double génération.

Capturer deux sorties `--release-strict`, vérifier :

- code processus et payload égaux à 7 ;
- exactement 69 raisons ;
- listes et octets identiques ;
- présence de la dette d’intégration build et des dimensions non couvertes ;
- `release_acceptance: false` dans la baseline et le rapport de gel.

- [ ] **Step 3: Revue indépendante**

Faire relire les invariants, le diff du registre matérialisé et les gates. Ne
pas auto-approuver un affaiblissement de gate.
