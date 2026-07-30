# État distant de la Phase 0

Observation arrêtée au `2026-07-30T09:54:05Z`.

Statut global : **branche sauvegardée et draft PR conforme, CI distante
inexécutable — NO-GO CI, NO-GO MERGE, NO-GO RELEASE**.

## Sauvegarde distante

Les commandes imposées ont été exécutées après `git fetch origin --prune`.

| Élément | Valeur observée |
|---|---|
| Branche locale | `finalisation/collection-v1` |
| HEAD local | `d88e0bf752082abd96c738f30285a059b1e249fb` |
| Branche distante | `origin/finalisation/collection-v1` |
| HEAD distant | `d88e0bf752082abd96c738f30285a059b1e249fb` |
| Décompte `origin/finalisation/collection-v1...HEAD` | `0 0` |
| Worktree avant production documentaire | propre |
| Conclusion | sauvegarde distante attestée pour `d88e0bf752082abd96c738f30285a059b1e249fb` |

Aucun push, `--force`, tag, changement de `main`, merge ou release n'a été
exécuté pendant cette reprise.

## Draft PR

| Champ | Valeur observée |
|---|---|
| Dépôt | `cyranoaladin/manuels-nexus` |
| Numéro | `#1` |
| URL | <https://github.com/cyranoaladin/manuels-nexus/pull/1> |
| Titre | `[Draft][Audit] Stabilisation Phase 0 de la collection Nexus` |
| État | `OPEN` |
| Draft | `true` |
| Base | `main` |
| Tête | `finalisation/collection-v1` |
| SHA de tête | `d88e0bf752082abd96c738f30285a059b1e249fb` |

Le corps contient littéralement :

```text
DRAFT — NO-GO MERGE — NO-GO RELEASE
```

Il rappelle aussi que les cinq tests visuels, les cinq tests RAG, les dettes
disciplinaires et `--release-strict` bloquent la publication. La PR satisfait
donc le contrat de gouvernance demandé et doit rester en draft.

## CI distante associée au SHA

### Workflows enregistrés

| Workflow | État GitHub | Déclenchement pour ce SHA | Motif |
|---|---|---|---|
| `.github/workflows/ci-audit-collection.yml` | actif | **oui**, événement `push` | la branche figure explicitement dans `push.branches` |
| `CI manuel mathématiques` | actif | non | aucun des 99 fichiers de la PR ne correspond à ses filtres `paths` |
| `CI manuels NSI` | actif | non | aucun des 99 fichiers de la PR ne correspond à ses filtres `paths` |

Le déclencheur `pull_request` du nouveau workflow d'audit n'a produit aucune
seconde exécution. Le fichier n'existe pas encore sur la branche de base
`main`; seule l'exécution `push` de la branche de tête est observée.

### Exécution déclenchée

| Champ | Valeur |
|---|---|
| Run | `30530258247` |
| URL | <https://github.com/cyranoaladin/manuels-nexus/actions/runs/30530258247> |
| Événement | `push` |
| Création | `2026-07-30T09:19:57Z` |
| Statut | `completed` |
| Conclusion | **failure** |
| Jobs créés | **0** |
| Artefacts | **0** |
| Check-runs GitHub Actions | **0** |
| Check-suite GitHub Actions | `failure` |

GitHub affiche une annotation de configuration unique :

```text
Invalid workflow file: .github/workflows/ci-audit-collection.yml#L1
(Line: 18, Col: 24): Unrecognized named-value: 'runner'.
Located at position 1 within expression: runner.temp,
(Line: 19, Col: 22): Unrecognized named-value: 'runner'.
Located at position 1 within expression: runner.temp
```

Cause racine : le contexte `runner` n'est pas accepté dans
`jobs.audit-phase-0.env` lors de la validation statique du workflow. Le contexte
runner n'est pas accepté dans `jobs.<job_id>.env` lors de la validation statique
du workflow. Les chemins dépendant du runner doivent être initialisés après
attribution du runner.

Les variables `CI_ARTIFACT_DIR` et `COVERAGE_FILE` rendaient ainsi le workflow
invalide avant création du job. Le contrat local est étendu pour interdire
`${{ runner.* }}` dans `jobs.*.env`, imposer l'initialisation via
`$RUNNER_TEMP`, et conserver l'upload des preuves au niveau d'une étape où le
contexte `runner` est disponible.

### Checks et suites externes

| Élément | État observé |
|---|---|
| `GitGuardian Security Checks` | **vert**, `success`, 3 s |
| Check-suite `GitHub Actions` | **rouge**, `failure`, aucun check-run |
| Vercel, Railway App, Cursor, SonarQubeCloud, Greptile Apps, cubic-dev-ai, Claude | suites créées mais sans check-run ni conclusion exploitable au moment du constat |
| Statuts de commit classiques | aucun ; état agrégé API `pending` |

`gh pr checks 1` n'affiche que GitGuardian. L'indication synthétique
« Checks passing » de `gh pr status` est donc incomplète : elle ne reflète pas
la check-suite Actions rouge sans check-run.

## Différence entre CI locale et distante

La commande locale équivalente à l'étape Pytest/couverture du workflow a été
relancée au HEAD :

```text
2 540 tests collectés
2 530 passed
5 failed
5 skipped
couverture lignes + branches : 76,83 %
durée : 712,22 s
```

Les cinq échecs sont exactement les contrôles visuels connus de
`test_maquette_v5.py`; les cinq skips sont exactement les cas RAG de
`test_retrieval.py`.

Le commit documentaire courant a aussi été simulé dans un clone temporaire
propre avant création du vrai commit :

```text
--check --validate-model : code 0
--check --fail-on-new    : code 0
--check --release-strict : code 7, 69 raisons
```

| Preuve | Locale | Distante |
|---|---|---|
| Parsing du workflow par GitHub | non reproduit par les tests de dépôt | **rouge** aux lignes 18–19 |
| Job `audit-phase-0` | logique exercée localement par les tests | absent |
| Pytest | 2 530 verts, 5 rouges, 5 ignorés | non exécuté |
| Couverture | 76,83 %, plancher atteint | non calculée |
| Gates modèle/baseline/release | codes frais `0 / 0 / 7` dans un clone propre simulant le commit | non exécutés |
| Artefacts d'audit | disponibles localement dans le dépôt | aucun artefact CI |

La CI distante ne prouve donc ni les 2 530 tests verts, ni les cinq échecs
attendus, ni la couverture, ni les gates. La correction du contexte
`runner.temp` et un test de régression de syntaxe/contexte GitHub Actions
constituent un prochain lot `[CI]` séparé ; aucune correction du workflow n'est
incluse dans le présent lot documentaire.
