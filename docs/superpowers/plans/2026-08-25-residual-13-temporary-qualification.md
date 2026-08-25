# Residual 13 Temporary Qualification Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Matérialiser exactement les treize dettes autorisées comme dette ouverte de non-régression, sans approbation release, puis rétablir les gates techniques.

**Architecture:** Étendre le workflow canonique existant sans script de matérialisation parallèle. Séparer le vrai nouveau set des migrations d'identité déjà approuvées, verrouiller les mutations, générer les artefacts, puis vérifier indépendamment la publication toujours bloquée.

**Tech Stack:** Python 3.12, pytest, JSON Schema, YAML, Git, LaTeX/PDF gates.

---

## Chunk 1: Contrat exact et TDD

### Task 1: Verrouiller les treize empreintes

**Files:**
- Modify: `tests/test_baseline_qualification.py`
- Modify: `tests/test_inventory_collection.py`
- Modify: `audit/schemas/v1/baseline-qualification-policy.schema.json`
- Modify: `scripts/baseline_qualification.py`
- Modify: `scripts/inventory_collection.py`

- [ ] Ajouter les tests du set nominatif, du digest et de l'absence de wildcard.
- [ ] Exécuter les tests et constater RED sur le contrat historique à 189.
- [ ] Ajouter les mutations quatorzième, omission, source différente et catégorie structurelle.
- [ ] Exécuter les tests et constater RED sur la séparation transition/vrai nouveau.
- [ ] Implémenter le contrôle minimal de liste exacte et comparer `approved_set` au vrai nouveau hors migrations.
- [ ] Rejouer les tests ciblés jusqu'à GREEN.
- [ ] Commit `[TESTS] Verrouiller la qualification exacte des treize dettes`.

## Chunk 2: Décision et matérialisation canonique

### Task 2: Enregistrer la décision approuvée

**Files:**
- Modify: `audit/BASELINE_QUALIFICATION_DECISION.md`
- Modify: `audit/BASELINE_QUALIFICATION_POLICY.yaml`
- Modify: `audit/schemas/v1/baseline-qualification-policy.schema.json`

- [ ] Enregistrer le SHA source, la date, le scope, les treize empreintes et le digest.
- [ ] Calculer les neuf paires, les résolutions, comptes et digests de transition.
- [ ] Recalculer le `control_digest` canonique.
- [ ] Vérifier la politique et constater en mode `--check` le code 3 et les
  seuls diffs attendus avant matérialisation, puis le code 0 après.
- [ ] Commit `[AUDIT] Autoriser exactement treize dettes résiduelles`.

### Task 3: Générer qualifications et baseline

**Files:**
- Modify generated: `audit/ANOMALY_DISPOSITIONS.yaml`
- Modify generated: `audit/UNQUALIFIED_ANOMALIES.{json,md}`
- Modify generated: `audit/INVENTAIRE_COLLECTION.json`
- Modify generated: `audit/ANOMALIES_BASELINE.json`
- Modify generated: `audit/BASELINE_UPDATE_REPORT.md`
- Modify generated: `audit/BASELINE_FREEZE_REPORT.md`

- [ ] Matérialiser avec `--materialize-baseline-qualifications`.
- [ ] Vérifier les treize dispositions `open_debt` et `release_blocking=true`.
- [ ] Commit atomique de qualification générée.
- [ ] Rafraîchir l'inventaire canonique et le committer séparément si requis par le producteur.
- [ ] Revalider le SHA, le `source_digest`, le set exact et son digest après
  matérialisation, immédiatement avant l'extension.
- [ ] Exécuter `--update-baseline --allow-approved-baseline-extension` depuis
  un worktree propre, avec `--reason` et `--approved-by` explicites.
- [ ] Commit atomique de baseline générée, sans contenu métier.

## Chunk 3: Preuves et technical trust

### Task 4: Produire les preuves exactes

**Files:**
- Create: `audit/BASELINE_RESIDUAL_13_EXACT_DIFF.json`
- Create: `audit/BASELINE_RESIDUAL_13_EXACT_DIFF.md`
- Create: `audit/RESIDUAL_13_SUNSET_LEDGER.json`
- Create: `audit/RESIDUAL_13_SUNSET_LEDGER.md`
- Test: `tests/test_residual_13_qualification.py`

- [ ] Écrire le test des comptes/diffs/sunset et constater RED.
- [ ] Produire les quatre artefacts avec les champs contractuels.
- [ ] Vérifier `authorized=materialized=13` et toutes les dérives à zéro.
- [ ] Vérifier la relation release bloquante des treize objets.
- [ ] Commit `[AUDIT] Prouver la qualification temporaire des treize dettes`.

### Task 5: Sceller les gates

- [ ] A : après extension, set exact des 13, `--fail-on-new` code 0 ; avant
  extension, la matérialisation seule laisse logiquement le code 5.
- [ ] B : ajout d'un 14e fingerprint, `--fail-on-new` code 5 et extension code 8.
- [ ] C : retrait d'une qualification, `--validate-model` code 6 et résultat
  déterministe.
- [ ] D : mutation produisant un fingerprint différent, `--fail-on-new` code
  5 ; mutation source sans nouveau fingerprint, extension code 8 par le verrou
  `source_digest`.
- [ ] E : `release_acceptance=true`, `--validate-model` code 6.
- [ ] F : statut approved sans reçu, matérialisation/extension refusée par la
  dérive du set ou le verrou `source_digest` (codes 3 ou 8 selon la phase).
- [ ] G : anomalie structurelle injectée dans la classe, `--fail-on-new` code 5
  et extension code 8.
- [ ] H : wildcard, validation de schéma ou `--validate-model` code 6.
- [ ] Exécuter `--validate-model` et exiger 0.
- [ ] Exécuter `--fail-on-new` et exiger 0.
- [ ] Exécuter `--release-strict` et exiger un blocage explicite.
- [ ] Exécuter les suites root, Math et NSI avec leurs dénominateurs courants.
- [ ] Exécuter les tests import/cwd et les invariants T1.
- [ ] Rejouer les quatre builds TNSI A/B et comparer les sorties.
- [ ] Demander une revue indépendante de la totalité du diff.

## Chunk 4: Démarrage des fermetures réelles

### Task 6: Ouvrir les lanes de contenu

- [ ] Recalculer les QCM manquants et préparer des lots indépendants.
- [ ] Recalculer les renvois TSPE manquants et préparer des lots indépendants.
- [ ] Rattacher les treize sunset aux campagnes programme/science/pédagogie.
- [ ] Ne promouvoir aucun statut et ne créer aucune nouvelle baseline.
