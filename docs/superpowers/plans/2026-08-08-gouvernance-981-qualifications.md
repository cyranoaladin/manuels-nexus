# Plan d'implémentation - Gouvernance des 981 qualifications

> **Pour l'agent d'exécution :** utiliser `superpowers:subagent-driven-development`,
> un implémenteur neuf par tâche, puis une revue de conformité et une revue de
> qualité avant de passer à la tâche suivante.

**Objectif :** enregistrer le lot exact de 981 anomalies comme `open_debt`
bloquantes, réconcilier exactement 642 anciennes empreintes dans l'historique
résolu et rendre `--validate-model` et `--fail-on-new` verts sans rendre la
collection publiable.

**Conception :**
`docs/superpowers/specs/2026-08-08-gouvernance-981-qualifications-design.md`

**Architecture :** étendre le contrat one-shot de
`BASELINE_QUALIFICATION_POLICY.yaml` avec `approved_transition`. Le
matérialisateur conserve les décisions antérieures et produit 981 nouvelles
dispositions. La garde existante `--allow-approved-baseline-extension` accepte
ensuite uniquement la réunion de deux transitions approuvées : les 981 ajouts
ouverts/bloquants et l'archivage exact des 642 empreintes absentes, dont trois
remplacements appariés. Toute autre dérive reste refusée.

**Stack :** Python 3, pytest, YAML, JSON Schema Draft 2020-12, Git, rapports
Markdown/JSON/YAML déterministes.

**Point de départ :** `dbb9a6fd4744e6205adbc68c79e12c297520a32b`

---

## Tâche 1 - Verrouiller le contrat, les règles et la réconciliation

**Fichiers :**

- Modifier : `tests/test_baseline_qualification.py`
- Modifier : `tests/test_inventory_collection.py`
- Modifier : `scripts/inventory_collection.py`
- Modifier : `audit/BASELINE_QUALIFICATION_DECISION.md`
- Modifier : `audit/BASELINE_QUALIFICATION_POLICY.yaml`
- Modifier : `audit/schemas/v1/baseline-qualification-policy.schema.json`

### Étape 1 - Écrire les tests RED du contrat de politique

Dans `test_qualification_policy_schema_and_approved_contract`, remplacer le
contrat de 186 par :

- décision `baseline-debt-extension-collection-2026-08-08` et ancre associée ;
- `baseline_sha` égal à
  `a48e8e41fc3f6ef9274e564722d5155c8df401b7` ;
- 981 empreintes et digest
  `sha256:e2ec8130f85f690eda663ac556b61e63ffd7d98e422c71f0245b10112161887f` ;
- catégories 875/82/15/2/7 ;
- propriétaires 752/98/131 ;
- digests source et modèle observés dans la conception ;
- objet `approved_transition` avec 2 647 actifs avant, 2 005 conservés, 642
  résolus, 2 986 actifs après, digest des 642, catégories des 642, trois paires
  et digest des paires.

Ajouter les cas du classifieur :

- `algorithme` et `experimentation` sous `blocking_statuses` vers
  `direction_scientifique_programme` ;
- `unclassified_types` vers `ingenierie_build_qualite` ;
- tous en `open_debt`, `release_blocking: true`.

Commande RED :

```bash
pytest -q tests/test_baseline_qualification.py \
  -k 'approved_contract or classifier_routes_contractual_samples'
```

Attendu : échec sur l'ancienne décision, le compte 186 et l'absence des deux
règles.

### Étape 2 - Écrire les tests RED de la garde de baseline

Créer des fixtures synthétiques avec un ancien jeu actif, un jeu ajouté
approuvé, un jeu résolu approuvé et une paire modifiée approuvée. Tester que
`_approved_baseline_extension_diagnosis` :

- accepte leur combinaison exacte ;
- refuse un ajout supplémentaire ;
- refuse une résolution supplémentaire ;
- refuse une paire différente ;
- refuse une réapparition depuis `resolved` ;
- refuse une altération d'un fingerprint conservé ;
- refuse un ajout non `open_debt` ou non bloquant ;
- conserve son comportement historique d'extension pure lorsque le contrat de
  transition est absent ou vide dans les fixtures existantes.

Commande RED :

```bash
pytest -q tests/test_inventory_collection.py \
  -k 'approved_baseline_extension_diagnosis'
```

Attendu : le cas de réconciliation exacte échoue parce que la garde refuse
actuellement toute résolution et toute paire modifiée.

### Étape 3 - Implémenter la garde minimale

Dans `_approved_baseline_extension_diagnosis` :

1. Charger et valider `approved_transition`.
2. Recalculer indépendamment les ensembles courant, précédent, ajouté, résolu
   et conservé.
3. Comparer les comptes, digests et catégories au contrat.
4. Comparer exactement les paires `modified`, dans leur ordre canonique, et
   leur digest.
5. Refuser toute régression, aggravation, croissance, changement de
   disposition ou de qualification sur une empreinte conservée.
6. Autoriser comme seuls échecs de comparaison les 978 anomalies nouvelles et
   les trois remplacements contractuels.
7. Continuer de vérifier chaque ajout contre la disposition matérialisée :
   `open_debt`, bloquant, propriétaire concordant, digest de politique courant.

Ne pas ajouter de nouveau flag CLI. Mettre à jour l'aide de
`--allow-approved-baseline-extension` pour mentionner la réconciliation exacte
lorsqu'un `approved_transition` est présent.

### Étape 4 - Mettre à jour décision, schéma et politique

Ajouter au registre la décision humaine approuvée, sans déclaration de
publication. Étendre le schéma avec un `$defs/approved_transition` fermé
(`additionalProperties: false`) et des constantes exactes pour cette décision.

Dans la politique :

- remplacer l'ancien jeu approuvé par le lot de 981 ;
- ajouter `approved_transition` ;
- ajouter les règles terminales d'ordres 17 et 18 ;
- conserver `release_acceptance: false` et les sorties prohibées ;
- recalculer `control_digest` avec la fonction canonique du dépôt.

Commande de calcul en lecture seule :

```bash
python3 - <<'PY'
from pathlib import Path
import yaml
from scripts.baseline_qualification import control_digest
path = Path('audit/BASELINE_QUALIFICATION_POLICY.yaml')
print(control_digest(yaml.safe_load(path.read_text(encoding='utf-8'))))
PY
```

Reporter la valeur obtenue avec `apply_patch`, jamais par une réécriture YAML
automatique.

### Étape 5 - Vérifier GREEN et les rouges transitoires

```bash
pytest -q tests/test_baseline_qualification.py \
  -k 'approved_contract or classifier_routes_contractual_samples'
pytest -q tests/test_inventory_collection.py \
  -k 'approved_baseline_extension_diagnosis'
python3 scripts/inventory_collection.py \
  --materialize-baseline-qualifications --check
git diff --check
git status --short
```

Attendu : tests unitaires verts ; la vérification de matérialisation sort `3`
et ne cite que les trois artefacts de la tâche 2. Les gates repository-level
peuvent rester rouges dans ce commit transitoire car les dispositions portent
encore l'ancienne politique ; ne pas les masquer ni les affaiblir.

### Étape 6 - Commit atomique

```bash
git add tests/test_baseline_qualification.py \
  tests/test_inventory_collection.py \
  scripts/inventory_collection.py \
  audit/BASELINE_QUALIFICATION_DECISION.md \
  audit/BASELINE_QUALIFICATION_POLICY.yaml \
  audit/schemas/v1/baseline-qualification-policy.schema.json
git commit -m "[AUDIT] verrouille les 981 qualifications de dette"
```

---

## Tâche 2 - Matérialiser les 981 dispositions

**Fichiers générés :**

- Modifier : `audit/ANOMALY_DISPOSITIONS.yaml`
- Modifier : `audit/UNQUALIFIED_ANOMALIES.json`
- Modifier : `audit/UNQUALIFIED_ANOMALIES.md`

### Étape 1 - Observer le diff attendu sans écriture

```bash
python3 scripts/inventory_collection.py \
  --materialize-baseline-qualifications --check
```

Attendu : code `3`, 981 approuvées, zéro non qualifiée, diff limité aux trois
artefacts ci-dessus.

### Étape 2 - Matérialiser

```bash
python3 scripts/inventory_collection.py \
  --materialize-baseline-qualifications
```

Inspecter le diff. Vérifier que les décisions antérieures sont conservées comme
historique et que les 981 nouvelles entrées portent la nouvelle décision.

### Étape 3 - Vérifier

```bash
pytest -q tests/test_baseline_qualification.py
pytest -q tests/test_inventory_collection.py \
  -k 'materializ or qualification_policy or approved_baseline_extension'
python3 scripts/inventory_collection.py \
  --materialize-baseline-qualifications --check
python3 scripts/inventory_collection.py --validate-model
git diff --check
git status --short
```

Attendu : zéro non qualifiée, matérialisation idempotente et modèle vert. Le
gate `--fail-on-new` reste rouge jusqu'à la tâche 3, sans affaiblissement.

### Étape 4 - Commit atomique

```bash
git add audit/ANOMALY_DISPOSITIONS.yaml \
  audit/UNQUALIFIED_ANOMALIES.json \
  audit/UNQUALIFIED_ANOMALIES.md
git commit -m "[AUDIT] materialise les 981 qualifications ouvertes"
```

---

## Tâche 3 - Étendre et réconcilier la baseline

**Fichiers générés :**

- Modifier : `audit/ANOMALIES_BASELINE.json`
- Modifier : `audit/BASELINE_UPDATE_REPORT.md`
- Modifier : `audit/BASELINE_FREEZE_REPORT.md`

### Étape 1 - Exiger un arbre propre

```bash
git status --short
python3 scripts/inventory_collection.py --validate-model
```

Attendu : aucun fichier modifié et modèle vert. Ne pas lancer l'écriture de
baseline si cette précondition n'est pas satisfaite.

### Étape 2 - Exécuter la transition approuvée

```bash
python3 scripts/inventory_collection.py \
  --update-baseline \
  --allow-approved-baseline-extension \
  --reason "Qualification ouverte des 981 dettes et reconciliation historique exacte des 642 empreintes approuvees le 2026-08-08" \
  --approved-by "Alaeddine Ben Rhouma"
```

La commande doit réévaluer deux fois le contrat, avant et pendant l'écriture,
et échouer si HEAD ou la baseline change entre les deux.

### Étape 3 - Inspecter et vérifier

```bash
python3 scripts/inventory_collection.py --validate-model
python3 scripts/inventory_collection.py --fail-on-new
python3 scripts/inventory_collection.py --release-strict
git diff --check
git status --short
```

Attendu :

- baseline active : 2 986 ;
- historique résolu : 642 ;
- transition : 978 `new`, 639 `resolved`, trois `modified`, aucune régression ;
- `--validate-model` : `0` ;
- `--fail-on-new` : `0` ;
- `--release-strict` : non nul, normalement `7`, avec `release_acceptance`
  toujours faux et TNSI toujours incomplet.

### Étape 4 - Commit atomique

```bash
git add audit/ANOMALIES_BASELINE.json \
  audit/BASELINE_UPDATE_REPORT.md \
  audit/BASELINE_FREEZE_REPORT.md
git commit -m "[AUDIT] reconcilie la baseline des qualifications"
```

---

## Tâche 4 - Régénérer l'inventaire canonique si nécessaire

**Fichiers potentiels :**

- `ETAT_COLLECTION.md`
- `audit/AUDIT_CONSOLIDE.md`
- `audit/ECARTS_ET_CONTRADICTIONS.yaml`
- `audit/INVENTAIRE_COLLECTION.json`
- `audit/INVENTAIRE_COLLECTION.md`
- `audit/MATRICE_LIVRABLES.yaml`

### Étape 1 - Vérifier avant écriture

```bash
python3 scripts/inventory_collection.py --check
```

Si le résultat est `0`, ne créer aucun commit vide. S'il est `3`, vérifier que
les diffs annoncés sont limités aux six rapports canoniques.

### Étape 2 - Régénérer et contrôler l'idempotence

```bash
python3 scripts/inventory_collection.py
python3 scripts/inventory_collection.py --check
```

Attendu : second appel `0`.

### Étape 3 - Commit conditionnel

```bash
git add ETAT_COLLECTION.md \
  audit/AUDIT_CONSOLIDE.md \
  audit/ECARTS_ET_CONTRADICTIONS.yaml \
  audit/INVENTAIRE_COLLECTION.json \
  audit/INVENTAIRE_COLLECTION.md \
  audit/MATRICE_LIVRABLES.yaml
git commit -m "[AUDIT] regenere l inventaire apres qualification"
```

Ne committer que les fichiers effectivement modifiés.

---

## Tâche 5 - Vérification finale et revue globale

### Étape 1 - Tests complets affectés

```bash
pytest -q tests/test_baseline_qualification.py tests/test_inventory_collection.py
python3 scripts/inventory_collection.py \
  --materialize-baseline-qualifications --check
python3 scripts/inventory_collection.py --check
python3 scripts/inventory_collection.py --validate-model
python3 scripts/inventory_collection.py --fail-on-new
```

### Étape 2 - Prouver le NO-GO release et le gel TNSI

```bash
python3 scripts/inventory_collection.py --release-strict
git diff dbb9a6fd4744e6205adbc68c79e12c297520a32b..HEAD \
  --name-only -- 'NSI/chapitres/TNSI-*'
```

Attendu : `--release-strict` rouge ; aucun chemin TNSI dans le diff.

### Étape 3 - Contrôles Git

```bash
git diff --check dbb9a6fd4744e6205adbc68c79e12c297520a32b..HEAD
git status --short --branch
git log --oneline --decorate -8
```

### Étape 4 - Revues indépendantes

Faire relire chaque tâche dans l'ordre : conformité à la spécification, puis
qualité de code. Après toutes les tâches, faire une revue du range complet
`dbb9a6f..HEAD`, corriger chaque constat et relancer les gates concernés.

### Critère de fin

Terminer uniquement avec :

- 981 qualifications courantes `open_debt` et bloquantes ;
- 642 anciennes empreintes conservées dans `resolved` ;
- zéro anomalie non qualifiée ;
- modèle et non-régression verts ;
- release strictement rouge ;
- aucun changement de source TNSI ;
- arbre Git propre.
