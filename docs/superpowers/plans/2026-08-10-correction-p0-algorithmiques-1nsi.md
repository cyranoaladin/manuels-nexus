# Correction des P0 algorithmiques 1NSI Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corriger trois P0 algorithmiques 1NSI avec regressions TDD, seconde revue independante et preuves d'audit coherentes.

**Architecture:** Un premier commit atomique porte les trois tests et les trois corrections de sources. Un second relecteur reatteste ensuite le lot canonique de 40 objets dans le recu algorithmique existant, sans elargir le protocole. Un commit suivant resynchronise les 40 findings et les artefacts de revue, puis l'inventaire est regenere seulement s'il est obsolete.

**Tech Stack:** Python 3.12, pytest, LaTeX, YAML/JSON, scripts de revue et d'inventaire Nexus.

---

## Chunk 1: Corrections TDD

### Task 1: Corriger les trois sources algorithmiques

**Files:**
- Create: `NSI/tests/test_1nsi_algorithmic_p0_regressions.py`
- Modify: `NSI/chapitres/1NSI-ALGO-DICHO-GLOUTON-KNN/cours/1NSI-ADGK-COURS-C2.tex`
- Modify: `NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/cours/1NSI-AGT-COURS-C2.tex`
- Modify: `NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/qcm/1NSI-ALGO-PARCOURS-TRIS-QCM.tex`

- [ ] **Step 1: Ecrire les trois tests de regression**

Le fichier de test lit les sources publiees. Il verifie exactement :

- l'introduction et la docstring gloutonnes sans promesse de minimalite ;
- `max(n - 1, 0)`, le cas `n <= 1`, le variant positif `j + 1`, la valeur terminale `j = -1` et la conclusion conditionnelle `n >= 2` ;
- les quatre options exactes de Q2, dans l'ordre, dont le nouveau distracteur `le nombre d'éléments du tableau.`.

Pour Q2, extraire le bloc entre `[Q2]` et `\bigskip`, puis comparer la liste issue de `re.findall(r"^\s*\\item\s+(.+)$", q2, flags=re.MULTILINE)` a :

```python
[
    "la valeur $0$.",
    "le premier élément du tableau.",
    "la plus grande valeur possible.",
    "le nombre d'éléments du tableau.",
]
```

- [ ] **Step 2: Observer le rouge**

```bash
cd NSI
pytest -q tests/test_1nsi_algorithmic_p0_regressions.py
```

Expected: trois echecs causes par les trois formulations actuelles, sans erreur de collecte.

- [ ] **Step 3: Corriger la formulation gloutonne**

Remplacer l'exemple par :

```latex
\exemple{Le \textbf{rendu de monnaie} : pour tenter d'obtenir un rendu avec peu de
pièces, on choisit à chaque étape la plus grande pièce (ou billet) ne dépassant
pas le montant restant.}
```

Remplacer la docstring par :

```python
"""Construit un rendu en choisissant d'abord les plus grandes pieces disponibles."""
```

- [ ] **Step 4: Corriger toute la preuve de terminaison**

Dans la propriete, dire que la boucle externe execute `max(n - 1, 0)` tours et que les tableaux de taille `n <= 1` sont deja tries. Pour la boucle interne, etablir qu'avant chaque tour execute `j >= 0`, donc que le variant entier `j + 1` est strictement positif et decroit de 1 ; lorsque `j = -1`, la condition est fausse.

Dans la demonstration, distinguer les cas `n <= 1`, sans iteration, et `n >= 2`, ou la derniere iteration a bien `i = n - 1`. Ne laisser aucune affirmation `n - 1 iterations` ou `derniere iteration i = n - 1` sans cette condition.

- [ ] **Step 5: Corriger le distracteur Q2**

Remplacer exactement la reponse D `la dernière valeur du tableau.` par :

```latex
\item le nombre d'éléments du tableau.
```

- [ ] **Step 6: Observer le vert cible et verifier les 40 objets sans ecriture**

```bash
cd NSI
pytest -q tests/test_1nsi_algorithmic_p0_regressions.py
PYTHONPATH=scripts python - <<'PY'
import json
from pathlib import Path

from scripts.verify_python import check_object

receipt = json.loads(
    Path("../audit/reviews/1nsi/runs/2026-08-10-algorithms.yaml").read_text(
        encoding="utf-8"
    )
)
entries = receipt["source_manifest"]["entries"]
assert len(entries) == 40
for entry in entries:
    result = check_object(Path("..") / entry["path"])
    assert result["verdict"] in {"verified", "manual_review"}, (entry, result)
PY
```

Expected: 3 tests passes; 40 objets inspectes; aucun verdict `fail`; aucun recu d'execution reecrit.

- [ ] **Step 7: Executer les gates reellement cibles des deux chapitres**

```bash
cd "$(git rev-parse --show-toplevel)"
python - <<'PY'
import subprocess

chapters = (
    "1NSI-ALGO-DICHO-GLOUTON-KNN",
    "1NSI-ALGO-PARCOURS-TRIS",
)
checks = (
    ("scripts/gates_corpus/check_td_corrige_alignment.py", "--strict"),
    ("scripts/gates_corpus/check_differentiation_quality.py",),
    ("scripts/gates_corpus/check_console_trace.py",),
)
for chapter in chapters:
    for check in checks:
        completed = subprocess.run(
            ["python", *check, "--chap", chapter],
            cwd="NSI",
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, (chapter, check, completed.stdout, completed.stderr)
        assert "WARN --" not in completed.stdout, (chapter, check, completed.stdout)
PY
git diff --check
git status --short
```

Ne pas appeler `gates-corpus-strict` : sa fuite eleve/professeur balaie TNSI. Ne
pas appeler non plus `check_qcm_schema.py` sur ces chapitres : son parseur
historique ne reconnait pas le format `[Qn]`. Le test de regression compare ici
les quatre options de Q2 exactement.

- [ ] **Step 8: Committer atomiquement les corrections**

```bash
git add \
  NSI/tests/test_1nsi_algorithmic_p0_regressions.py \
  NSI/chapitres/1NSI-ALGO-DICHO-GLOUTON-KNN/cours/1NSI-ADGK-COURS-C2.tex \
  NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/cours/1NSI-AGT-COURS-C2.tex \
  NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/qcm/1NSI-ALGO-PARCOURS-TRIS-QCM.tex
git diff --cached --check
git commit -m "[PEDAGOGIE] corrige trois P0 algorithmiques 1NSI"
```

Conserver le SHA obtenu comme `SOURCE_COMMIT`.

## Chunk 2: Seconde revue independante

### Task 2: Reattester et sceller le lot algorithmique canonique

**Files:**
- Modify: `NSI/tests/test_1nsi_content_reviews.py`
- Modify: `audit/reviews/1nsi/runs/2026-08-10-algorithms.yaml`

- [ ] **Step 1: Mandater le second relecteur et capturer son identite**

Creer un agent distinct et conserver l'ID retourne par l'orchestrateur comme
`SECOND_REVIEWER_ID`. A ce stade, lui interdire explicitement toute ecriture et
lui demander seulement d'attendre le signal apres le rouge TDD. Cette barriere
garantit que l'ancien recu reste intact pendant les Steps 2 et 3.

- [ ] **Step 2: Ecrire le test de pre-scellement**

Ajouter un test canonique `test_algorithm_review_receipt_matches_current_sources_before_sealing`. Il doit charger le recu du worktree puis verifier :

- le schema ferme avec `Draft202012Validator` et
  `format_checker=review_module.FORMAT_CHECKER` ;
- `receipt["protocol_digest"] == policy["protocol_digest"]` ;
- l'affectation exacte et ordonnee des 40 sources `object` des deux chapitres ;
- les hashes courants de `review_1nsi_content.py`, `verify_python.py` et `common.py` ;
- pour chaque source, l'ID, le chemin, le SHA-256 et le `dependency_digest` courants ;
- les IDs, chapitres et scopes ordonnes des 40 reviews ;
- la validite de chaque fait via `review_module._validate_fact`, ainsi que la coherence verdict/anomalies ;
- des observations normalisees non dupliquees dans chaque chapitre et l'absence de TNSI ;
- `receipt["reviewer_id"] == SECOND_REVIEWER_ID`, cet ID etant aussi distinct
  de `019feb71-27c9-7530-ab01-ce74cea1b4a2` et de
  `policy["integrator_id"]` ;
- un `review_run_id` distinct de `1nsi-objects-algorithms-2026-08-10-bernoulli-v1` ;
- pour chaque source executable, un appel frais a
  `review_module.execution_observation(source, ROOT)`, un
  `fresh_verdict == "pass"`, et au moins un fait `computed_result` contenant le
  `check_digest` frais ; les hashes du manifeste scellent le contexte exact de
  cette execution.

- [ ] **Step 3: Observer le rouge de provenance**

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py \
  -k algorithm_review_receipt_matches_current_sources_before_sealing
```

Expected: echec sur les hashes/dependances obsoletes du recu initial, apres le commit source.

- [ ] **Step 4: Autoriser puis integrer la seconde revue**

Apres le rouge observe, donner au relecteur `SOURCE_COMMIT`, les quatre
anomalies attendues comme resolues et la liste des 40 objets. Exiger une
relecture scientifique et pedagogique independante, une execution fraiche sans
ecriture des objets executables, de nouvelles ancres et un nouveau
`review_run_id`.

Le relecteur prepare uniquement
`audit/reviews/1nsi/runs/2026-08-10-algorithms.yaml`. Il retire un constat
seulement si la source courante le justifie et signale toute anomalie nouvelle
au lieu de forcer les anciens totaux.

- [ ] **Step 5: Valider le recu avant scellement**

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py \
  -k algorithm_review_receipt_matches_current_sources_before_sealing
git diff --check
git status --short
```

Expected: test vert et seulement le test canonique plus le recu modifies depuis `SOURCE_COMMIT`.

- [ ] **Step 6: Sceller le nouveau recu**

```bash
git add \
  NSI/tests/test_1nsi_content_reviews.py \
  audit/reviews/1nsi/runs/2026-08-10-algorithms.yaml
git diff --cached --check
git commit -m "[AUDIT] rescelle la revue algorithmique 1NSI"
```

Verifier que le parent direct de ce commit est `SOURCE_COMMIT`. Conserver le SHA obtenu comme `RECEIPT_COMMIT` et le SHA-256 du blob comme `RECEIPT_SHA256`.

Le registre est temporairement rouge apres ce commit, car les 40 findings referencent encore l'ancien blob. Cette transition bornee est attendue. Un nouveau chemin de recu est interdit ici : son ajout a l'allowlist changerait le digest du protocole et invaliderait les 349 revues.

## Chunk 3: Registre probant

### Task 3: Resynchroniser les findings et les artefacts derives

**Files:**
- Modify: `NSI/tests/test_1nsi_content_reviews.py`
- Modify: `audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml`
- Modify: `audit/1NSI_CONTENT_REVIEWS.json`
- Modify: `audit/1NSI_CONTENT_REVIEW_SUMMARY.md`

- [ ] **Step 1: Ecrire le test d'acceptation metier**

Ajouter un test canonique qui verifie, dans les findings YAML, le registre JSON et la synthese Markdown, l'absence des IDs :

```text
1NSI-REV-ADGK-C2-DOCSTRING-OPTIMALITE
1NSI-REV-AGT-C2-BORNE-TERMINAISON
1NSI-REV-AGT-QCM-Q2-AMBIGU
1NSI-REV-ADGK-C2-CONTRADICTION
```

Le test doit aussi verifier les totaux exacts issus du nouveau recu independant. Si aucune anomalie nouvelle n'est relevee, les attendus sont 349 entrees, 260 anomalies, dont 141 P0 et 116 P1. Ne pas imposer ces nombres si le second relecteur a justifie un nouveau constat : arreter et faire auditer l'ecart.
Il construit enfin le document courant et exige
`review_module.release_gate_allows(document, policy) is False`.

Ajouter egalement un test de scellement avec les constantes `SOURCE_COMMIT`,
`RECEIPT_COMMIT` et `RECEIPT_SHA256`. Il doit verifier par `git show` que le
blob scelle est identique au recu courant et que le parent direct de
`RECEIPT_COMMIT` est exactement `SOURCE_COMMIT`.

- [ ] **Step 2: Observer le rouge d'acceptation**

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py \
  -k algorithm_review_resolved_anomalies_are_absent_from_canonical_outputs
```

Expected: echec tant que les findings et sorties derivees contiennent les anomalies resolues.

- [ ] **Step 3: Integrer les 40 payloads rescelles**

Pour les 40 objets du recu algorithmique, recopier les payloads du nouveau recu et reconstruire leur provenance avec `RECEIPT_SHA256` et `RECEIPT_COMMIT`. Deriver l'identite, le chemin, le statut et les capacites des sources courantes. Ne modifier aucun finding TNSI ni aucun statut.

- [ ] **Step 4: Regenerer et verifier les artefacts**

```bash
python scripts/review_1nsi_content.py \
  --findings audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml \
  --output-json audit/1NSI_CONTENT_REVIEWS.json \
  --output-summary audit/1NSI_CONTENT_REVIEW_SUMMARY.md
python scripts/review_1nsi_content.py \
  --findings audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml \
  --output-json audit/1NSI_CONTENT_REVIEWS.json \
  --output-summary audit/1NSI_CONTENT_REVIEW_SUMMARY.md --check
pytest -q NSI/tests/test_1nsi_content_reviews.py
git diff --check
git status --short
```

- [ ] **Step 5: Committer les preuves derivees**

```bash
git add \
  NSI/tests/test_1nsi_content_reviews.py \
  audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml \
  audit/1NSI_CONTENT_REVIEWS.json \
  audit/1NSI_CONTENT_REVIEW_SUMMARY.md
git diff --cached --check
git commit -m "[AUDIT] actualise la revue algorithmique 1NSI"
```

## Chunk 4: Inventaire et verification finale

### Task 4: Resynchroniser la source de verite collection

**Files:**
- Modify if generated: `ETAT_COLLECTION.md`
- Modify if generated: `audit/AUDIT_CONSOLIDE.md`
- Modify if generated: `audit/ECARTS_ET_CONTRADICTIONS.yaml`
- Modify if generated: `audit/INVENTAIRE_COLLECTION.json`
- Modify if generated: `audit/INVENTAIRE_COLLECTION.md`
- Modify if generated: `audit/MATRICE_LIVRABLES.yaml`

- [ ] **Step 1: Interroger l'inventaire sans masquer les erreurs**

Capturer le code de sortie et le JSON, puis regenerer seulement pour des sorties
obsoletes :

```bash
python - <<'PY'
import json
import subprocess

command = ["python", "scripts/inventory_collection.py", "--check"]
completed = subprocess.run(command, capture_output=True, text=True)
payload = json.loads(completed.stdout)
assert payload["gate"] == "check"
assert payload["exit_code"] == completed.returncode
if completed.returncode == 0:
    assert payload["success"] is True
    assert payload["reasons"] == []
elif completed.returncode == 3:
    assert payload["success"] is False
    assert payload["reasons"]
    assert all(
        reason.startswith(("diff:", "manquant:"))
        for reason in payload["reasons"]
    ), payload
    subprocess.run(
        ["python", "scripts/inventory_collection.py"],
        check=True,
    )
else:
    raise AssertionError((completed.returncode, payload, completed.stderr))
PY
```

Toute raison `check_error:` est ainsi un echec a diagnostiquer, jamais une
autorisation de regeneration.

- [ ] **Step 2: Executer les suites completes affectees**

```bash
cd NSI && pytest -q tests
cd .. && pytest -q tests/test_inventory_collection.py
python scripts/review_1nsi_content.py \
  --findings audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml \
  --output-json audit/1NSI_CONTENT_REVIEWS.json \
  --output-summary audit/1NSI_CONTENT_REVIEW_SUMMARY.md --check
python scripts/inventory_collection.py --check
python scripts/inventory_collection.py --validate-model
python scripts/inventory_collection.py --fail-on-new
```

Expected: codes 0 pour `--check`, `--validate-model` et `--fail-on-new`.

- [ ] **Step 3: Verifier les refus de publication attendus**

Capturer separement les codes et sorties avec des assertions executables :

```bash
python - <<'PY'
import json
import subprocess

source_paths = (
    "NSI/chapitres/1NSI-ALGO-DICHO-GLOUTON-KNN/cours/1NSI-ADGK-COURS-C2.tex",
    "NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/cours/1NSI-AGT-COURS-C2.tex",
    "NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/qcm/1NSI-ALGO-PARCOURS-TRIS-QCM.tex",
)
scope = subprocess.run(
    ["python", "scripts/review_1nsi_content.py", "--verify-scope"],
    capture_output=True,
    text=True,
)
scope_output = scope.stdout + scope.stderr
assert scope.returncode == 2, (scope.returncode, scope_output)
assert "allowlist violee:" in scope_output, scope_output
assert all(path in scope_output for path in source_paths), scope_output

release = subprocess.run(
    ["python", "scripts/inventory_collection.py", "--release-strict"],
    capture_output=True,
    text=True,
)
payload = json.loads(release.stdout)
assert release.returncode == 7, (release.returncode, payload, release.stderr)
assert payload["gate"] == "release-strict"
assert payload["success"] is False
assert payload["exit_code"] == 7
assert payload["reasons"]
assert payload["blocker_count"] > 0
assert not any(
    reason.startswith("inventaire_indisponible:")
    for reason in payload["reasons"]
), payload
PY
```

Le code 2 de la revue est attendu car `verify_scope` precede la decision du
CLI `--release-gate`. Le refus metier de `release_gate_allows` est deja exige
par le test d'acceptation du Chunk 3.

- [ ] **Step 4: Committer l'inventaire regenere, si necessaire**

Avant tout commit :

```bash
git diff --check
git status --short
```

S'il existe un diff genere, ajouter uniquement les six sorties gerees presentes dans le diff et committer :

```bash
git add \
  ETAT_COLLECTION.md \
  audit/AUDIT_CONSOLIDE.md \
  audit/ECARTS_ET_CONTRADICTIONS.yaml \
  audit/INVENTAIRE_COLLECTION.json \
  audit/INVENTAIRE_COLLECTION.md \
  audit/MATRICE_LIVRABLES.yaml
git diff --cached --check
git commit -m "[AUDIT] resynchronise l inventaire apres correction 1NSI"
```

Ne pas creer de commit vide.

- [ ] **Step 5: Controle final**

```bash
git status --short --branch
git rev-parse HEAD
git log --oneline --decorate -8
git diff --check
```
