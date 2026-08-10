# Dix P0 scientifiques 1NSI Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corriger séparément dix P0 scientifiques 1NSI avec dix cycles TDD, dix commits source atomiques et dix attestations indépendantes, puis restaurer entièrement la gouvernance des 349 qualifications.

**Architecture:** Un test de régression ciblé et, lorsque du Python est publié, un fichier `.py` canonique sont ajoutés avec chaque correction minimale. Chaque commit source est relu avant un commit d'attestation séparé. Une fois les dix unités closes, le manifeste vide, la policy, les six reçus et les sorties dérivées sont migrés suivant deux transitions rouges bornées.

**Tech Stack:** Python 3.12, pytest, runpy/importlib, LaTeX/LuaLaTeX, PyYAML, JSON Schema Draft 2020-12, Git.

**Design:** `docs/superpowers/specs/2026-08-10-dix-p0-scientifiques-1nsi-design.md`

---

## Chunk 0: Outillage non destructif et contrat des attestations

### Task 0A: Ajouter le mode lecture seule au gate Python

**Files:**
- Modify: `NSI/tests/test_verify_python.py`
- Modify: `NSI/scripts/verify_python.py`

- [ ] **Step 1: Écrire le test rouge**

Ajouter un test qui crée un chapitre temporaire avec un objet et un reçu existant,
appelle `main(..., check=True)`, puis exige que le verdict soit calculé mais qu'aucun
fichier ne soit créé ou modifié. Ajouter aussi `--check` au test de CLI.

- [ ] **Step 2: Observer le rouge**

Run: `cd NSI && pytest -q tests/test_verify_python.py -k check`

Expected: FAIL car le paramètre et l'option n'existent pas.

- [ ] **Step 3: Implémenter**

Ajouter `--check` et séparer le calcul des records de leur écriture. En mode check,
afficher les mêmes verdicts, ne jamais appeler `write_json` et retourner un code non nul
uniquement pour un échec d'exécution réel.

- [ ] **Step 4: Vérifier et committer**

Run: `cd NSI && pytest -q tests/test_verify_python.py` puis vérifier que
`python scripts/verify_python.py --chap 1NSI-LANGAGE --check` laisse
`git status --porcelain` inchangé.

Commit: `[PYTHON] ajoute le mode lecture seule au gate NSI`

### Task 0B: Fermer le schéma des attestations unitaires

**Files:**
- Create: `audit/schemas/v1/1nsi-p0-correction-attestation.schema.json`
- Create: `NSI/tests/test_1nsi_p0_attestations.py`

- [ ] **Step 1: Écrire le schéma fermé**

Le schéma Draft 2020-12 exige : `artifact_type`, `schema_version`, `manual`, `p0_id`,
`source_commit_sha`, `source_files` avec chemins et SHA-256, `reviewer_id`,
`reviewer_model`, `review_run_id`, `session_id`, `generation_id`, `cache_status`,
`commands`, `verdict` et `reviewed_at`. `verdict` vaut uniquement `approved` ou
`changes_required`; `cache_status` vaut `not_applicable`, `miss` ou `hit`. Chaque entrée
de `commands` est un objet fermé qui exige `command`, `cwd`, `exit_code`,
`stdout_sha256`, `stderr_sha256` et `result_summary`. Les résultats observés restent
séparés des métadonnées de génération et de cache.

- [ ] **Step 2: Écrire les tests rouges du contrat**

Les tests valident le schéma fermé, puis tous les reçus présents sous
`audit/reviews/1nsi/p0/2026-08-10-*.yaml`. Ils vérifient les SHA des fichiers au commit
source par `git show`. Pour tout reçu, y compris non suivi, la phase pré-commit vérifie
schéma, SHA source, résultats de commandes, absence de secret et unicité des
reviewers/runs. Pour les reçus suivis seulement, la phase post-commit dérive par Git le
commit d'ajout et exige que son parent direct soit `source_commit_sha`. Les tests
incluent un reçu temporaire non suivi et un reçu suivi dans un dépôt temporaire afin
d'épingler les deux phases. Un test final, activé par la présence du résumé consolidé,
exige exactement dix reçus et dix P0 IDs attendus.

- [ ] **Step 3: Observer le rouge puis créer le schéma**

Run: `cd NSI && pytest -q tests/test_1nsi_p0_attestations.py`.

- [ ] **Step 4: Committer**

Commit: `[AUDIT] definit le contrat des attestations P0 1NSI`

### Task 0C: Ajouter un build de validation sans promotion

**Files:**
- Modify: `NSI/tests/test_assemble_manuel.py`
- Modify: `NSI/scripts/assemble_manuel.py`

- [ ] **Step 1: Écrire les tests rouges**

Ajouter un test succès et un test échec pour `build_manual(..., staging_only=True)`.
Dans les deux cas, calculer avant l'appel les octets et le SHA-256 du PDF canonique,
interdire tout appel à `_promote_book_artifacts`, puis exiger les octets et le digest
strictement inchangés. Le succès doit néanmoins compiler et exécuter le préflight.
Ajouter le test de transmission CLI de `--staging-only` et refuser sa combinaison avec
`--record-observed`.

- [ ] **Step 2: Observer le rouge**

Run: `cd NSI && pytest -q tests/test_assemble_manuel.py -k staging_only`.

- [ ] **Step 3: Implémenter le chemin non promoteur**

Ajouter l'option positive `--staging-only`. La faire parvenir à `_build_local`, qui
retourne le résultat après compilation et préflight sans promouvoir aucun artefact.
Le chemin canonique existant conserve son comportement par défaut.

- [ ] **Step 4: Vérifier et committer**

Run: `cd NSI && pytest -q tests/test_assemble_manuel.py tests/test_gates_corpus.py`.
Vérifier `git diff --check` et l'absence de modification TNSI.

Commit: `[PDF] ajoute la validation sans promotion au livre 1NSI`

## Chunk 1: Dix corrections atomiques

### Convention commune TDD et revue

**Files:**
- Create progressively: `NSI/tests/test_1nsi_scientific_p0_regressions.py`
- Create per correction: `audit/reviews/1nsi/p0/2026-08-10-<p0-slug>.yaml`

Pour chaque task ci-dessous, appliquer strictement cet ordre :

- [ ] Ajouter uniquement le test du comportement ciblé.
- [ ] Exécuter son node pytest et observer un échec causé par le P0, pas par une erreur de test.
- [ ] Appliquer la correction minimale et, si indiqué, créer la source `.py` canonique.
- [ ] Exécuter le node ciblé, tous les tests du fichier et `python scripts/verify_python.py --chap <CHAP> --check` depuis `NSI/`.
- [ ] Vérifier `git diff --check`, `git status --short` et le garde TNSI depuis le SHA initial `bdd3285b75aeedf2c23382c58aacb0d99070a1b9`.
- [ ] Committer uniquement le test, la source `.py` éventuelle et les sources LaTeX de l'unité avec le message prévu.
- [ ] Mandater un relecteur indépendant en lecture seule. Il vérifie le commit, les fichiers complets, les cas limites, l'exécution, la cohérence des variantes et l'absence de TNSI.
- [ ] Créer le reçu YAML de l'unité avec `artifact_type`, `p0_id`, `source_commit_sha`, chemins et SHA-256, `reviewer_id`, `reviewer_model`, `review_run_id`, `session_id`, `generation_id`, `cache_status`, commandes, résultats fermés et verdict.
- [ ] Exécuter le test complet des attestations avant commit ; il valide la phase pré-commit et ignore uniquement la parenté Git du reçu encore non suivi. Exiger aussi que `git rev-parse HEAD` égale `source_commit_sha`.
- [ ] Committer uniquement le reçu avec `[AUDIT] atteste <objet> 1NSI`, puis réexécuter immédiatement le test complet afin de valider la phase post-commit et la parenté directe.

Chaque `review_run_id` et chaque `reviewer_id` est unique parmi les dix unités. Pour un reviewer local, inscrire `cache_status: not_applicable`. Si un LLM externe est utilisé, conserver un préfixe invariant et un `session_id` stable par lot, activer `cache_control` lorsque le modèle l'exige et consigner le hit/miss ; un hit ne remplace jamais un run indépendant. Un verdict autre que `approved` ou un échec post-commit interdit de passer à la task suivante.

### Task 1: Maximum initialisé à zéro

**P0:** `1NSI-REV-LANG-COURS-C4-MAXIMUM-ZERO`

**Files:**
- Modify: `NSI/tests/test_1nsi_scientific_p0_regressions.py`
- Create: `NSI/chapitres/1NSI-LANGAGE/code/maximum_bugue.py`
- Modify: `NSI/chapitres/1NSI-LANGAGE/cours/1NSI-LANG-COURS-C4.tex`
- Create after review: `audit/reviews/1nsi/p0/2026-08-10-maximum-zero.yaml`

- [ ] **Step 1: Écrire le test rouge**

Ajouter `test_maximum_zero_condition_includes_zero_for_nonempty_lists`. Il importe et
exécute `maximum_bugue.py`, compare sa sortie publiée, vérifie les deux listes limites,
exige le hash de dépendance Python et l'égalité exacte entre le contenu du bloc Python
publié et le fichier `.py` canonique après retrait des seuls délimiteurs LaTeX, puis
contrôle dans le bloc `\erreurFrequente` :

```python
assert "pour une liste non vide" in block
assert "valeur positive ou nulle" in block
assert "[-5, 0, -8]" in source
assert "[-5, -1, -8]" in source
assert "si et seulement si la liste contient au moins une valeur positive :" not in block
```

- [ ] **Step 2: Observer le rouge**

Run: `cd NSI && pytest -q tests/test_1nsi_scientific_p0_regressions.py::test_maximum_zero_condition_includes_zero_for_nonempty_lists`

Expected: FAIL sur l'ancienne condition « valeur positive ».

- [ ] **Step 3: Corriger minimalement**

Créer `maximum_bugue.py` avec le code publié et son appel nominal, puis ajouter
`% PYTHON-SOURCE: code/maximum_bugue.py` avant le bloc correspondant. Préciser que,
pour une liste non vide, l'initialisation à zéro est correcte si et seulement si le
maximum est positif ou nul. Ajouter les deux listes de régression : l'une contient
zéro et l'autre seulement des valeurs strictement négatives. Supprimer le commentaire
de sortie `# 7 -- semble correct`, conserver l'appel `print` sans sortie saisie dans le
bloc Python, puis ajouter un bloc console exact `7` et un `BEGIN-TRACE/EXPECTED` qui
exécute la source canonique. Le test capture cette exécution et compare la console et la
trace à la sortie générée.

- [ ] **Step 4: Vérifier et committer**

Run: node ciblé, fichier complet, `cd NSI && python scripts/verify_python.py --chap 1NSI-LANGAGE --check`.

Commit: `[PEDAGOGIE] corrige le critere du maximum initialise a zero`

- [ ] **Step 5: Revue et reçu indépendant**

Le reviewer doit exécuter la source `.py`, calculer les sorties de
`maximum_bugue([-5, 0, -8])` et `maximum_bugue([-5, -1, -8])`, puis approuver la
condition nécessaire et suffisante. Commit du reçu :
`[AUDIT] atteste le critere du maximum 1NSI`.

### Task 2: Corrigé du minimum sur liste vide

**P0:** `1NSI-REV-LANGAGE-RE-C4-CORRIGE-LISTE-VIDE`

**Files:**
- Modify: `NSI/tests/test_1nsi_scientific_p0_regressions.py`
- Create: `NSI/chapitres/1NSI-LANGAGE/code/minimum.py`
- Modify: `NSI/chapitres/1NSI-LANGAGE/corriges/1NSI-LANGAGE-RE-C4-CORRIGE.tex`
- Create after review: `audit/reviews/1nsi/p0/2026-08-10-minimum-corrige-liste-vide.yaml`

- [ ] **Step 1: Écrire le test rouge**

Ajouter `test_minimum_canonical_source_rejects_empty_list_and_matches_correction`. Le test exige le fichier canonique, l'importe, vérifie `minimum([5, 3, 8]) == 3`, exige `AssertionError` sur `[]` et compare exactement son code au bloc Python du corrigé.

- [ ] **Step 2: Observer le rouge**

Expected: FAIL car le fichier `.py` n'existe pas et le corrigé n'annonce pas la précondition.

- [ ] **Step 3: Créer la source canonique et synchroniser le corrigé**

Contenu fonctionnel attendu :

```python
def minimum(liste):
    """Renvoie le plus petit élément de `liste`.

    Précondition : `liste` est non vide.
    """
    assert len(liste) > 0, "liste doit etre non vide"
    mini = liste[0]
    for x in liste[1:]:
        if x < mini:
            mini = x
    return mini
```

Le fichier source reste ASCII dans son code publié (`element`, `Precondition`) si le gate Ruff l'exige ; le texte LaTeX peut conserver les accents hors code.
Ajouter `% PYTHON-SOURCE: code/minimum.py` dans le corrigé avant le bloc synchronisé.

- [ ] **Step 4: Vérifier et committer**

Commit: `[PYTHON] protege le minimum 1NSI contre la liste vide`

- [ ] **Step 5: Revue et reçu indépendant**

Le reviewer exécute le `.py`, contrôle le couple docstring/assertion et vérifie que le corrigé reste professeur-only. Commit : `[AUDIT] atteste le minimum corrige 1NSI`.

### Task 3: Énoncé de remédiation du minimum

**P0:** `1NSI-REV-LANGAGE-RE-C4-LISTE-VIDE`

**Files:**
- Modify: `NSI/tests/test_1nsi_scientific_p0_regressions.py`
- Modify: `NSI/chapitres/1NSI-LANGAGE/remediation/1NSI-LANGAGE-RE-C4.tex`
- Create after review: `audit/reviews/1nsi/p0/2026-08-10-minimum-remediation-liste-vide.yaml`

- [ ] **Step 1: Écrire le test rouge**

Ajouter `test_minimum_remediation_states_nonempty_precondition_and_matches_answer`. Exiger « liste non vide » dans la consigne, le cas `[]` explicitement classé hors précondition, et la cohérence avec la source canonique créée à la Task 2.

- [ ] **Step 2: Observer le rouge**

Expected: FAIL sur la précondition absente.

- [ ] **Step 3: Corriger l'énoncé et son bloc VERIFY**

Annoncer la précondition avant le code, demander sa justification dans les questions et faire vérifier par le bloc caché que `minimum([])` lève `AssertionError`.
Déclarer aussi `% PYTHON-SOURCE: code/minimum.py` pour sceller la dépendance du couple.

- [ ] **Step 4: Vérifier le couple et committer**

Exécuter les tests des Tasks 2 et 3 ensemble et le gate du chapitre.

Commit: `[PEDAGOGIE] explicite la liste non vide en remediation 1NSI`

- [ ] **Step 5: Revue et reçu indépendant**

Le reviewer vérifie simultanément remédiation et corrigé. Commit : `[AUDIT] atteste la remediation minimum 1NSI`.

### Task 4: Avancement sans jalon

**P0:** `1NSI-REV-PM-COURS-C2-JALONS-VIDES`

**Files:**
- Modify: `NSI/tests/test_1nsi_scientific_p0_regressions.py`
- Create: `NSI/chapitres/1NSI-PROJET-METHODES/code/avancement.py`
- Modify: `NSI/chapitres/1NSI-PROJET-METHODES/cours/1NSI-PM-COURS-C2.tex`
- Create after review: `audit/reviews/1nsi/p0/2026-08-10-avancement-jalons-vides.yaml`

- [ ] **Step 1: Écrire le test rouge**

Ajouter `test_avancement_canonical_source_rejects_empty_milestones`. Importer le `.py`, vérifier `40.0`, `0.0`, `100.0`, puis `AssertionError` sur `[]`. Comparer le code TeX à la source et la sortie capturée à un bloc console exact.

- [ ] **Step 2: Observer le rouge**

Expected: FAIL sur fichier absent et `ZeroDivisionError` dans l'ancien code.

- [ ] **Step 3: Implémenter**

Ajouter dans `avancement` :

```python
assert len(jalons) > 0, "au moins un jalon est requis"
```

La docstring énonce la précondition. La démonstration conserve les cinq jalons et génère `40.0`.
Ajouter `% PYTHON-SOURCE: code/avancement.py`; remplacer les sorties commentées par un
bloc console comparé à la sortie capturée.

- [ ] **Step 4: Vérifier et committer**

Commit: `[PYTHON] protege avancement contre les jalons vides`

- [ ] **Step 5: Revue et reçu indépendant**

Commit : `[AUDIT] atteste avancement sur jalons non vides 1NSI`.

### Task 5: Poids négatifs ou de somme nulle

**P0:** `1NSI-REV-PM-COURS-C3-POIDS-NEGATIFS`

**Files:**
- Modify: `NSI/tests/test_1nsi_scientific_p0_regressions.py`
- Create: `NSI/chapitres/1NSI-PROJET-METHODES/code/moyenne_ponderee.py`
- Modify: `NSI/chapitres/1NSI-PROJET-METHODES/cours/1NSI-PM-COURS-C3.tex`
- Create after review: `audit/reviews/1nsi/p0/2026-08-10-moyenne-poids-negatifs.yaml`

- [ ] **Step 1: Écrire le test rouge**

Ajouter `test_weighted_mean_rejects_negative_and_zero_sum_weights`. Vérifier le cas nominal, les longueurs différentes, `[1, -0.5]`, `[0, 0]` et les listes vides. Comparer le bloc publié à la source `.py`.

- [ ] **Step 2: Observer le rouge**

Expected: FAIL car les poids négatifs sont acceptés et la somme nulle divise par zéro.

- [ ] **Step 3: Implémenter les trois préconditions**

```python
assert len(valeurs) == len(poids), "valeurs et poids doivent avoir la meme longueur"
assert all(poids_i >= 0 for poids_i in poids), "les poids doivent etre non negatifs"
assert sum(poids) > 0, "la somme des poids doit etre strictement positive"
```

Calculer ensuite la somme pondérée. Le texte explique que ces hypothèses placent le résultat dans l'intervalle des valeurs.
Ajouter `% PYTHON-SOURCE: code/moyenne_ponderee.py` avant le bloc publié.

- [ ] **Step 4: Vérifier et committer**

Commit: `[PYTHON] valide les poids de la moyenne ponderee 1NSI`

- [ ] **Step 5: Revue et reçu indépendant**

Le reviewer note explicitement si le P0 antérieur `1NSI-REV-PM-COURS-C3-DENOMINATEUR` est aussi fermé. Commit : `[AUDIT] atteste la moyenne ponderee 1NSI`.

### Task 6: Collision des colonnes de fusion

**P0:** `1NSI-REV-TAB-COURS-C4-COLLISION-COLONNES`

**Files:**
- Modify: `NSI/tests/test_1nsi_scientific_p0_regressions.py`
- Create: `NSI/chapitres/1NSI-TABLES/code/fusionner.py`
- Modify: `NSI/chapitres/1NSI-TABLES/cours/1NSI-TAB-COURS-C4.tex`
- Create after review: `audit/reviews/1nsi/p0/2026-08-10-fusion-collision-colonnes.yaml`

- [ ] **Step 1: Écrire le test rouge**

Ajouter `test_table_join_rejects_overlapping_nonkey_columns`. Vérifier le résultat nominal et exiger `AssertionError` lorsque `table1` et `table2` contiennent toutes deux une colonne non-clé `age`. Comparer code et sortie publiés à la source exécutée.

- [ ] **Step 2: Observer le rouge**

Expected: FAIL car `table2` écrase silencieusement `age`.

- [ ] **Step 3: Implémenter la précondition**

Calculer l'union des noms de colonnes non-clés de chaque table et exiger leur disjonction avant de construire `index2`. Documenter ce contrat. Ne pas modifier dans cette unité la stratégie existante sur les clés dupliquées ; cette dette déjà attestée reste visible jusqu'à une correction séparée.
Ajouter `% PYTHON-SOURCE: code/fusionner.py` et comparer la sortie générée au bloc
console publié.

- [ ] **Step 4: Vérifier et committer**

Commit: `[PYTHON] refuse les collisions de colonnes en fusion 1NSI`

- [ ] **Step 5: Revue et reçu indépendant**

Commit : `[AUDIT] atteste la fusion sans collision 1NSI`.

### Task 7: Visibilité du code serveur

**P0:** `1NSI-REV-WEB-SERVER-VISIBILITY-COURSE`

**Files:**
- Modify: `NSI/tests/test_1nsi_scientific_p0_regressions.py`
- Modify: `NSI/chapitres/1NSI-WEB-IHM/cours/1NSI-WEB-COURS-C2.tex`
- Create after review: `audit/reviews/1nsi/p0/2026-08-10-code-serveur-visibilite.yaml`

- [ ] **Step 1: Écrire le test rouge**

Ajouter `test_server_code_is_normally_not_sent_in_http_response`. Exiger les expressions « s'exécute côté serveur », « n'est normalement pas transmis » et « réponse HTTP destinée au navigateur », et interdire « l'utilisateur ne voit jamais ce code ».

- [ ] **Step 2: Observer le rouge**

Expected: FAIL sur la formulation absolue.

- [ ] **Step 3: Corriger et committer**

Commit: `[PEDAGOGIE] precise la visibilite du code serveur 1NSI`

- [ ] **Step 4: Revue et reçu indépendant**

Le reviewer distingue absence de transmission protocolaire et accès éventuel au code par une autre voie. Commit : `[AUDIT] atteste la visibilite du code serveur 1NSI`.

### Task 8: Cours sur la copie de grille

**P0:** `1NSI-REV-TC-COURS-C5-COPIE-PROFONDE-INCOMPLETE`

**Files:**
- Modify: `NSI/tests/test_1nsi_scientific_p0_regressions.py`
- Create: `NSI/chapitres/1NSI-TYPES-CONSTRUITS/code/copier_grille_deux_niveaux.py`
- Modify: `NSI/chapitres/1NSI-TYPES-CONSTRUITS/cours/1NSI-TC-COURS-C5.tex`
- Create after review: `audit/reviews/1nsi/p0/2026-08-10-cours-copie-deux-niveaux.yaml`

- [ ] **Step 1: Écrire le test rouge**

Ajouter `test_grid_course_names_two_level_copy_and_states_atomic_cell_contract`.
Importer et exécuter la source canonique sur une grille numérique et le contre-exemple
mutable, exiger le hash de dépendance Python et l'égalité exacte entre le contenu du
bloc Python publié et le fichier `.py` canonique après retrait des seuls délimiteurs
LaTeX, puis vérifier « copie des deux premiers niveaux », les cellules scalaires
atomiques autorisées, l'interdiction des conteneurs imbriqués et `[[[1]]]`. Interdire
l'affirmation que la compréhension est une copie profonde générale.

- [ ] **Step 2: Observer le rouge**

Expected: FAIL sur « Pour une copie profonde ».

- [ ] **Step 3: Créer la source canonique et corriger le cours**

```python
def copier_grille_deux_niveaux(grille):
    """Copie la liste externe et chaque ligne.

    Precondition : les cellules sont des valeurs scalaires atomiques non mutables,
    sans conteneur imbrique.
    """
    return [list(ligne) for ligne in grille]
```

Le cours prouve que les lignes sont distinctes pour une grille numérique et montre que, hors contrat, une cellule-liste reste partagée.
Ajouter `% PYTHON-SOURCE: code/copier_grille_deux_niveaux.py` avant le bloc synchronisé.

- [ ] **Step 4: Vérifier et committer**

Commit: `[PEDAGOGIE] qualifie la copie de grille a deux niveaux 1NSI`

- [ ] **Step 5: Revue et reçu indépendant**

Commit : `[AUDIT] atteste le cours de copie a deux niveaux 1NSI`.

### Task 9: Exercice et corrigé 053

**P0:** `1NSI-REV-TC-CO-053-COPIE-PROFONDE-INCOMPLETE`

**Files:**
- Modify: `NSI/tests/test_1nsi_scientific_p0_regressions.py`
- Modify: `NSI/chapitres/1NSI-TYPES-CONSTRUITS/exercices/1NSI-TC-EX-053.tex`
- Modify: `NSI/chapitres/1NSI-TYPES-CONSTRUITS/corriges/1NSI-TC-CO-053.tex`
- Create after review: `audit/reviews/1nsi/p0/2026-08-10-corrige-053-copie-deux-niveaux.yaml`

- [ ] **Step 1: Écrire le test rouge**

Ajouter `test_grid_exercise_053_and_answer_share_two_level_contract`. Exiger le même nom, la même précondition et la même limite dans l'énoncé et le corrigé ; comparer le code du corrigé à la source de la Task 8.

- [ ] **Step 2: Observer le rouge**

Expected: FAIL sur « copie profonde » et « aucune modification ».

- [ ] **Step 3: Aligner l'énoncé et le corrigé**

Demander une copie des deux premiers niveaux d'une grille à cellules scalaires atomiques. Limiter la garantie aux modifications de structure, de lignes et aux réaffectations de cellules. Ajouter le contre-exemple hors contrat.
Déclarer `% PYTHON-SOURCE: code/copier_grille_deux_niveaux.py` dans l'énoncé et le
corrigé.

- [ ] **Step 4: Vérifier et committer**

Commit: `[PEDAGOGIE] aligne l exercice 053 sur la copie a deux niveaux`

- [ ] **Step 5: Revue et reçu indépendant**

Commit : `[AUDIT] atteste l exercice 053 de copie 1NSI`.

### Task 10: Exercice et corrigé 054

**P0:** `1NSI-REV-TC-CO-054-COPIE-PROFONDE-INCOMPLETE`

**Files:**
- Modify: `NSI/tests/test_1nsi_scientific_p0_regressions.py`
- Modify: `NSI/chapitres/1NSI-TYPES-CONSTRUITS/exercices/1NSI-TC-EX-054.tex`
- Modify: `NSI/chapitres/1NSI-TYPES-CONSTRUITS/corriges/1NSI-TC-CO-054.tex`
- Create after review: `audit/reviews/1nsi/p0/2026-08-10-corrige-054-copie-deux-niveaux.yaml`

- [ ] **Step 1: Écrire le test rouge**

Ajouter `test_grid_exercise_054_uses_two_level_function_name_and_contract`. Exiger
`copier_grille_deux_niveaux`, interdire `copie_profonde_grille`, vérifier les cellules
autorisées, le contre-exemple mutable, la non-divergence avec le `.py` canonique et la
sortie `1` réellement capturée pour les deux objets.

- [ ] **Step 2: Observer le rouge**

Expected: FAIL sur le nom et la garantie générale.

- [ ] **Step 3: Aligner la paire**

Renommer la fonction, corriger docstring, consigne, preuve et bloc VERIFY. Les tests numériques montrent l'indépendance des lignes ; le cas `[[[1]]]` montre la limite hors contrat.
Déclarer `% PYTHON-SOURCE: code/copier_grille_deux_niveaux.py` dans l'énoncé et le
corrigé. Supprimer `# doit afficher 1` et `# affiche 1`, laisser les appels `print` sans
sortie saisie dans les blocs Python, puis ajouter dans chaque objet un bloc console exact
`1` et un `BEGIN-TRACE/EXPECTED`. Le code de trace reprend la fonction canonique et le
scénario publié ; le test l'exécute et compare les sorties au lieu de les accepter comme
texte manuel.

- [ ] **Step 4: Vérifier et committer**

Commit: `[PYTHON] aligne l exercice 054 sur la copie a deux niveaux`

- [ ] **Step 5: Revue et reçu indépendant**

Commit : `[AUDIT] atteste l exercice 054 de copie 1NSI`.

## Chunk 2: Variantes, compilation et clôture disciplinaire

### Task 11: Vérifier les variantes affectées

**Files:**
- Modify if required by missing coverage only: `NSI/tests/test_assemble_manuel.py`

- [ ] **Step 1: Épingler les sélections**

Ajouter ou étendre un test qui exige : cours dans les livres `eleve` et `professeur`, remédiation dans `remediation` et `professeur`, corrigés uniquement dans `professeur`, exercices 053/054 dans `eleve` et `professeur`.

- [ ] **Step 2: Exécuter les sélections**

Run: `cd NSI && pytest -q tests/test_assemble_manuel.py tests/test_gates_corpus.py`.

- [ ] **Step 3: Construire les variantes canoniques affectées**

Run depuis `NSI/` :

```bash
python scripts/assemble_manuel.py --variant eleve --staging-only
python scripts/assemble_manuel.py --variant professeur --staging-only
python scripts/assemble_manuel.py --variant remediation --staging-only
```

Exiger le code 0 des trois commandes et vérifier par le test de sélection que les cinq
chapitres affectés appartiennent aux variantes attendues. Ne pas utiliser
`--record-observed` et ne pas indexer de sortie de build.

- [ ] **Step 4: Vérifier les objets et le Python**

Run pour chacun de `1NSI-LANGAGE`, `1NSI-PROJET-METHODES`, `1NSI-TABLES`,
`1NSI-TYPES-CONSTRUITS`, `1NSI-WEB-IHM` :
`python scripts/verify_python.py --chap <CHAP> --check`.

- [ ] **Step 5: Commit éventuel de test seulement**

Si un test de sélection était nécessaire : `[TESTS] epingle les variantes des dix P0 1NSI`. Aucun commit si la couverture existante suffit.

### Task 12: Audit disciplinaire consolidé

**Files:**
- Create: `audit/reviews/1nsi/p0/2026-08-10-dix-p0-summary.md`

- [ ] **Step 1: Vérifier les dix cycles**

Le résumé liste chaque P0, commit source, commit de reçu, reviewer, run, test rouge observé, test vert et verdict.

- [ ] **Step 2: Vérifier la couverture**

Exiger dix IDs, dix commits source distincts, dix reviewer IDs distincts et dix verdicts `approved`.

- [ ] **Step 3: Committer**

Commit: `[AUDIT] consolide les dix revues P0 1NSI`.

## Chunk 3: Gouvernance BUILD_MANIFEST et 349 qualifications

### Task 13: Rafraîchir le manifeste vide et fixer la nouvelle base

**Files:**
- Modify: `audit/BUILD_MANIFEST.json`
- Modify if generated: `ETAT_COLLECTION.md`
- Modify if generated: `audit/ECARTS_ET_CONTRADICTIONS.yaml`
- Modify if generated: `audit/INVENTAIRE_COLLECTION.json`
- Modify if generated: `audit/MATRICE_LIVRABLES.yaml`

- [ ] **Step 1: Exiger un worktree propre après les corrections**

Run: `git status --short --branch`, `git diff --check`, tests ciblés complets.

- [ ] **Step 2: Rafraîchir uniquement le manifeste vide**

Run: `python scripts/build_manifest.py --refresh-empty`.

Expected: manifeste toujours vide, nouvelle provenance et nouveau `source_digest`.

- [ ] **Step 3: Committer le manifeste**

Commit: `[AUDIT] rafraichit le manifeste vide apres les dix P0`

- [ ] **Step 4: Resynchroniser l'inventaire si `--check` le demande**

Calculer d'abord les SHA-256 des six sorties gérées : `ETAT_COLLECTION.md`,
`audit/AUDIT_CONSOLIDE.md`, `audit/ECARTS_ET_CONTRADICTIONS.yaml`,
`audit/INVENTAIRE_COLLECTION.json`, `audit/INVENTAIRE_COLLECTION.md` et
`audit/MATRICE_LIVRABLES.yaml`. Run ensuite :
`python scripts/inventory_collection.py --check`.

Accepter le code 0 si rien n'est périmé. Pour le code 3, exiger une liste `reasons` non
vide dont chaque entrée correspond exactement à `^(diff|manquant): (.+)$`; rejeter
notamment `check_error:` et toute raison non conforme avant d'extraire un chemin. Exiger
ensuite que chaque chemin extrait appartienne à l'allowlist ci-dessous. Vérifier que les
six hashes et `git status --porcelain` sont inchangés après ce contrôle. Arrêter sans
générer au moindre motif ou chemin hors périmètre. Seulement alors, run :
`python scripts/inventory_collection.py`, puis
`python scripts/inventory_collection.py --check`.

N'indexer que `ETAT_COLLECTION.md`, `audit/ECARTS_ET_CONTRADICTIONS.yaml`,
`audit/INVENTAIRE_COLLECTION.json` et `audit/MATRICE_LIVRABLES.yaml`. Commit éventuel :
`[AUDIT] resynchronise l inventaire apres les dix P0 1NSI`.

- [ ] **Step 5: Capturer la base propre**

Le HEAD propre devient `GOVERNANCE_BASE_SHA`. Calculer le SHA-256 du manifeste et conserver les hashes PDF et le fingerprint TNSI inchangés.

### Task 14: Migrer la policy et borner la première transition

**Files:**
- Modify: `NSI/tests/test_1nsi_content_reviews.py`
- Modify: `audit/1NSI_CONTENT_REVIEW_POLICY.yaml`

- [ ] **Step 1: Écrire les tests rouges**

Épingler la nouvelle base, le hash du manifeste et le futur protocole. Vérifier par
`git show` que les six reçus précédents restent historiquement valides. La transition
rouge doit détecter exactement six reçus périmés et dériver les champs obsolètes lot par
lot : protocole et dépendances pour les six, `source_sha256` pour les quatre lots dont
les sources ont été modifiées, et hash de l'outil `verify_python.py` pour les six. Ne pas
borner artificiellement les différences à une liste plus étroite que ces valeurs dérivées.

- [ ] **Step 2: Observer le rouge puis migrer**

Mettre à jour uniquement `implementation_base_sha`, `scope_guard.build_manifest.sha256` et `protocol_digest` calculé.

- [ ] **Step 3: Vérifier `--verify-scope` et committer**

Commit: `[AUDIT] migre la gouvernance apres les dix P0 1NSI`.

### Task 15: Réattester et sceller les six lots

**Files:**
- Modify: `NSI/tests/test_1nsi_content_reviews.py`
- Modify: six fichiers `audit/reviews/1nsi/runs/2026-08-10-*.yaml`

- [ ] **Step 1: Mandater six reviewers indépendants**

Un reviewer par lot : `contracts`, `algorithms`, `systems-web`, `language-project`, `data-basics-tables`, `types-construits`. Les six IDs et runs sont nouveaux, distincts entre eux, distincts de l'intégrateur et des reçus remplacés.

- [ ] **Step 2: Réattester les 349 sources**

Les reviewers relisent les sources et dépendances courantes, exécutent les contrôles applicables et dérivent tous les deltas sans forcer les totaux. Les dix P0 ciblés doivent être absents ; toute autre ouverture ou fermeture est justifiée.

- [ ] **Step 3: Tester avant scellement**

Exiger protocole, manifests, ancres, faits, exécutions et couverture exacte 349/349.

- [ ] **Step 4: Sceller ensemble**

Commit: `[AUDIT] rescelle les 349 revues apres les dix P0`

Conserver `RECEIPTS_COMMIT` et les six SHA-256.

### Task 16: Reconstruire les findings et sorties canoniques

**Files:**
- Modify: `NSI/tests/test_1nsi_content_reviews.py`
- Modify: `audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml`
- Modify: `audit/1NSI_CONTENT_REVIEWS.json`
- Modify: `audit/1NSI_CONTENT_REVIEW_SUMMARY.md`

- [ ] **Step 1: Écrire le test de seconde transition**

Vérifier les six blobs par `git show`, les 349 identités immuables et borner les différences aux payloads/provenances réattestés.

- [ ] **Step 2: Reconstruire depuis les blobs scellés**

Recopier exactement payload et provenance ; dériver les identités depuis la découverte courante. Regénérer JSON et résumé avec `scripts/review_1nsi_content.py`.

- [ ] **Step 3: Vérifier les deltas**

Exiger l'absence des dix IDs ciblés. Ne pas épingler de total avant de l'avoir dérivé des six reçus.

- [ ] **Step 4: Committer**

Commit: `[AUDIT] rattache les 349 qualifications apres les dix P0`

### Task 17: Gates finaux et refus de publication

- [ ] **Step 1: Suites complètes**

```bash
cd NSI && pytest -q tests
cd .. && pytest -q tests/test_inventory_collection.py
python scripts/review_1nsi_content.py --findings audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml --output-json audit/1NSI_CONTENT_REVIEWS.json --output-summary audit/1NSI_CONTENT_REVIEW_SUMMARY.md --check
python scripts/review_1nsi_content.py --verify-scope
python scripts/inventory_collection.py --check
python scripts/inventory_collection.py --validate-model
python scripts/inventory_collection.py --fail-on-new
```

- [ ] **Step 2: Refus de release attendu**

Run depuis la racine :

```bash
python scripts/inventory_collection.py --release-strict
test $? -eq 7
```

Exiger le code 7, `success: false`, au moins un blocage réel et aucune raison
`inventaire_indisponible:`.

- [ ] **Step 3: Garde TNSI et état final**

Run depuis la racine :

```bash
git diff --exit-code bdd3285b75aeedf2c23382c58aacb0d99070a1b9 -- \
  'NSI/chapitres/TNSI-*' \
  'NSI/referentiel/capacites_TNSI_*' \
  NSI/docs/11_perimetre_terminale.md \
  NSI/sources/txt/BO2019_NSI_terminale.txt \
  'NSI/build/MANUEL_TNSI*'
git ls-files --others --exclude-standard -- \
  'NSI/chapitres/TNSI-*' \
  'NSI/referentiel/capacites_TNSI_*' \
  NSI/docs/11_perimetre_terminale.md \
  NSI/sources/txt/BO2019_NSI_terminale.txt \
  'NSI/build/MANUEL_TNSI*'
```

La première commande doit sortir avec 0 et la seconde sans sortie. Exiger aussi
`git diff --check` et un worktree propre.

- [ ] **Step 4: Revue finale indépendante**

Faire relire la plage complète depuis le SHA initial, avec findings classés P0/P1/P2. Aucun P0/P1 du mécanisme ou des dix corrections ne peut rester ouvert avant clôture.
