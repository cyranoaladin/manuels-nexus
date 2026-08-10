# Correction du P0 C3 1NSI Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corriger le cas limite de la preuve de terminaison du tri par selection C3 avec regression TDD et nouvelle revue independante du lot algorithmique.

**Architecture:** Le test lit la source LaTeX canonique et impose une preuve totale pour `n <= 1` et `n >= 2`. La correction disciplinaire est committee avant la revue ; un nouveau relecteur reatteste ensuite les 40 objets algorithmiques dans un recu scelle, puis les findings et l'inventaire sont resynchronises sans toucher a TNSI.

**Tech Stack:** Python 3.12, pytest, LaTeX, PyYAML, JSON Schema, Git.

**Design:** `docs/superpowers/specs/2026-08-10-c3-build-manifest-governance-design.md`

---

## Preflight obligatoire

Avant Task 1, committer atomiquement les deux plans approuves, puis exiger :

```bash
git status --short --branch
git diff --check
```

Le worktree doit etre propre. Aucun test d'inventaire ne doit etre lance avec
les plans encore non suivis.

## Chunk 1: Regression et correction

### Task 1: Rendre la preuve C3 totale

**Files:**
- Modify: `NSI/tests/test_1nsi_algorithmic_p0_regressions.py`
- Modify: `NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/cours/1NSI-AGT-COURS-C3.tex`

- [ ] **Step 1: Ajouter le test de regression**

Ajouter le chemin `SELECTION_COURSE`, puis un test
`test_selection_sort_termination_covers_empty_and_singleton_arrays`. Il exige
dans la propriete et la demonstration normalisees :

```text
$\max(n-1,0)$ itérations
Si $n\leqslant1$, la boucle externe ne s'exécute pas
le tableau est déjà trié
Si $n\geqslant2$, la dernière itération a $i=n-2$
le tableau entier est donc trié
```

Le test interdit aussi une conclusion non conditionnelle commencant par
`Après la dernière itération ($i=n-2$)`.

Le test extrait separement la propriete entre
`\propriete[Terminaison et coût]{` et `\demonstration{`, puis la demonstration
entre `\demonstration{` et le prochain `% BEGIN-VERIFY`. Une occurrence dans
un commentaire ou une autre rubrique ne doit jamais satisfaire l'assertion.

- [ ] **Step 2: Observer le rouge**

```bash
cd NSI
pytest -q tests/test_1nsi_algorithmic_p0_regressions.py \
  -k selection_sort_termination_covers_empty_and_singleton_arrays
```

Expected: un echec d'assertion sur les formulations absentes, sans erreur de
collecte.

- [ ] **Step 3: Corriger minimalement la propriete**

Preciser que `range(n - 1)` execute `max(n-1,0)` iterations. Distinguer
explicitement `n <= 1`, sans iteration et deja trie, de `n >= 2`. Conserver le
cout quadratique comme comportement asymptotique, sans affirmer un nombre de
tours negatif ou une execution pour les petits tableaux.

- [ ] **Step 4: Corriger minimalement la demonstration**

Remplacer la terminaison inconditionnelle par deux cas :

```latex
\textbf{Terminaison.} Si $n\leqslant1$, la boucle externe ne s'exécute pas et
le tableau est déjà trié. Si $n\geqslant2$, la dernière itération a $i=n-2$.
Apres sa conservation, l'invariant donne que
\lstinline{tableau[0:n-1]} est trié et que son dernier élément est inférieur ou
égal à l'unique élément de \lstinline{tableau[n-1:n]} : le tableau entier est
donc trié.
```

Adapter les accents a la convention deja presente dans la source.

- [ ] **Step 5: Observer le vert et verifier les 40 objets sans ecriture**

```bash
cd NSI
pytest -q tests/test_1nsi_algorithmic_p0_regressions.py
PYTHONPATH=scripts python - <<'PY'
import json
from pathlib import Path

from scripts.verify_python import check_object

receipt = json.loads(json.dumps(__import__("yaml").safe_load(
    Path("../audit/reviews/1nsi/runs/2026-08-10-algorithms.yaml").read_text(
        encoding="utf-8"
    )
)))
entries = receipt["source_manifest"]["entries"]
assert len(entries) == 40
for entry in entries:
    result = check_object(Path("..") / entry["path"])
    assert result["verdict"] in {"verified", "manual_review"}, (entry, result)
PY
```

Expected: quatre regressions vertes et 40 objets sans verdict `fail`.

- [ ] **Step 6: Executer les gates du chapitre affecte**

```bash
python - <<'PY'
import subprocess

chapter = "1NSI-ALGO-PARCOURS-TRIS"
checks = (
    ("scripts/gates_corpus/check_td_corrige_alignment.py", "--strict"),
    ("scripts/gates_corpus/check_differentiation_quality.py",),
    ("scripts/gates_corpus/check_console_trace.py",),
)
for check in checks:
    completed = subprocess.run(
        ["python", *check, "--chap", chapter],
        cwd="NSI",
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, (check, completed.stdout, completed.stderr)
    assert "WARN --" not in completed.stdout, completed.stdout
PY
```

- [ ] **Step 7: Compiler le chapitre sans remplacer les PDF canoniques**

```bash
cd NSI
python scripts/assemble.py --chap 1NSI-ALGO-PARCOURS-TRIS --variant complet
cd ..
git status --short
```

Expected: code 0 et aucun PDF sous `NSI/build/MANUEL_1NSI/` modifie. Les
artefacts de chapitre restent ignores et ne sont pas promus comme livrables
canoniques.

- [ ] **Step 8: Committer la correction**

```bash
git diff --check
git status --short
git add \
  NSI/tests/test_1nsi_algorithmic_p0_regressions.py \
  NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/cours/1NSI-AGT-COURS-C3.tex
git diff --cached --check
git commit -m "[PEDAGOGIE] corrige le P0 de terminaison C3 1NSI"
```

Conserver le SHA comme `C3_SOURCE_COMMIT`.

## Chunk 2: Nouvelle revue independante

### Task 2: Reattester le lot algorithmique

**Files:**
- Modify: `NSI/tests/test_1nsi_content_reviews.py`
- Modify: `audit/reviews/1nsi/runs/2026-08-10-algorithms.yaml`

- [ ] **Step 1: Mandater un nouveau relecteur**

Creer un agent distinct, sans droit d'ecriture initial. Capturer son identite
comme `C3_REVIEWER_ID`. Elle doit differer de l'integrateur, du reviewer
historique et de tous les reviewers deja presents dans les six recus. Son run
doit aussi differer des six runs courants et du run algorithmique historique.
Capturer avant modification ces ensembles dans des constantes de regression.
Lui transmettre `C3_SOURCE_COMMIT`, le lot exact de 40 sources et le P0 a
verifier.

Le relecteur relit les 40 objets, valide les ancres, relance sans ecriture les
objets executables et indique toute anomalie nouvelle. Il ne modifie pas les
sources et ne force pas les totaux attendus.

- [ ] **Step 2: Durcir le test de pre-scellement**

Mettre a jour le test
`test_algorithm_review_receipt_matches_current_sources_before_sealing` pour
exiger `C3_REVIEWER_ID`, un nouveau `review_run_id`, les 40 hashes et digests
courants, les preuves valides et les observations d'execution fraiches.

- [ ] **Step 3: Observer le rouge de provenance**

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py \
  -k algorithm_review_receipt_matches_current_sources_before_sealing
```

Expected: echec sur l'ancien reviewer, l'ancien run et le manifeste obsolete.

- [ ] **Step 4: Integrer fidelement la revue independante**

Mettre a jour le recu avec l'identite et le run du relecteur, le manifeste
courant et ses payloads relus. Retirer
`1NSI-REV-AGT-C3-CAS-LIMITE-TERMINAISON` uniquement si le relecteur confirme
que les deux cas sont prouves. Conserver toute anomalie nouvelle signalee.

- [ ] **Step 5: Valider et sceller le recu**

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py \
  -k algorithm_review_receipt_matches_current_sources_before_sealing
git diff --check
git status --short
git add \
  NSI/tests/test_1nsi_content_reviews.py \
  audit/reviews/1nsi/runs/2026-08-10-algorithms.yaml
git diff --cached --check
git commit -m "[AUDIT] rescelle la revue C3 1NSI"
```

Conserver `C3_RECEIPT_COMMIT` et le SHA-256 du blob.

## Chunk 3: Registre et inventaire

### Task 3: Fermer le P0 dans les sorties canoniques

**Files:**
- Modify: `NSI/tests/test_1nsi_content_reviews.py`
- Modify: `audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml`
- Modify: `audit/1NSI_CONTENT_REVIEWS.json`
- Modify: `audit/1NSI_CONTENT_REVIEW_SUMMARY.md`
- Modify if generated: `ETAT_COLLECTION.md`
- Modify if generated: `audit/AUDIT_CONSOLIDE.md`
- Modify if generated: `audit/ECARTS_ET_CONTRADICTIONS.yaml`
- Modify if generated: `audit/INVENTAIRE_COLLECTION.json`
- Modify if generated: `audit/INVENTAIRE_COLLECTION.md`
- Modify if generated: `audit/MATRICE_LIVRABLES.yaml`

- [ ] **Step 1: Ecrire puis observer le test d'acceptation rouge**

Exiger l'absence du P0 C3 dans les findings, le JSON et la synthese, la
provenance exacte du nouveau recu et, en l'absence de nouveau constat, 349
entrees et 260 anomalies reparties en 141 P0, 116 P1 et 3 P2.

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py \
  -k algorithm_review_resolved_anomalies_are_absent_from_canonical_outputs
```

Expected: echec tant que les sorties portent encore le P0.

- [ ] **Step 2: Resynchroniser les 40 findings et regenerer**

Recopier exactement les payloads du recu scelle et reconstruire leur
provenance avec `C3_RECEIPT_COMMIT` et son SHA-256. Regenerer ensuite :

```bash
python scripts/review_1nsi_content.py \
  --findings audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml \
  --output-json audit/1NSI_CONTENT_REVIEWS.json \
  --output-summary audit/1NSI_CONTENT_REVIEW_SUMMARY.md
python scripts/review_1nsi_content.py \
  --findings audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml \
  --output-json audit/1NSI_CONTENT_REVIEWS.json \
  --output-summary audit/1NSI_CONTENT_REVIEW_SUMMARY.md --check
pytest -q NSI/tests/test_1nsi_content_reviews.py \
  --deselect NSI/tests/test_1nsi_content_reviews.py::test_scope_guard_pins_exact_sources_and_immutable_surfaces \
  --deselect NSI/tests/test_1nsi_content_reviews.py::test_verify_scope_rejects_changed_path_outside_allowlist \
  --deselect NSI/tests/test_1nsi_content_reviews.py::test_cli_exposes_required_modes
```

- [ ] **Step 3: Committer le registre C3**

```bash
git diff --check
git status --short
git add \
  NSI/tests/test_1nsi_content_reviews.py \
  audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml \
  audit/1NSI_CONTENT_REVIEWS.json \
  audit/1NSI_CONTENT_REVIEW_SUMMARY.md
git diff --cached --check
git commit -m "[AUDIT] actualise la revue C3 1NSI"
```

- [ ] **Step 4: Regenerer l'inventaire seulement s'il est obsolete**

Executer `python scripts/inventory_collection.py --check`. Le code 0 exige
aucune action. Le code 3 n'est acceptable que pour des raisons `diff:` ou
`manquant:` ; dans ce cas executer `python scripts/inventory_collection.py`,
reverifier `--check`, puis committer uniquement les sorties generees avec :

```bash
git status --short
git add \
  ETAT_COLLECTION.md \
  audit/AUDIT_CONSOLIDE.md \
  audit/ECARTS_ET_CONTRADICTIONS.yaml \
  audit/INVENTAIRE_COLLECTION.json \
  audit/INVENTAIRE_COLLECTION.md \
  audit/MATRICE_LIVRABLES.yaml
git diff --cached --name-only
git diff --cached --check
git commit -m "[AUDIT] resynchronise l inventaire apres C3 1NSI"
```

N'ajouter que les chemins effectivement modifies parmi ces six sorties et
verifier qu'aucun autre chemin n'est indexe.

- [ ] **Step 5: Verifier la cloture C3**

```bash
cd NSI && pytest -q tests \
  --deselect NSI/tests/test_1nsi_content_reviews.py::test_scope_guard_pins_exact_sources_and_immutable_surfaces \
  --deselect NSI/tests/test_1nsi_content_reviews.py::test_verify_scope_rejects_changed_path_outside_allowlist \
  --deselect NSI/tests/test_1nsi_content_reviews.py::test_cli_exposes_required_modes
cd .. && pytest -q tests/test_inventory_collection.py
python scripts/inventory_collection.py --check
python scripts/inventory_collection.py --validate-model
python scripts/inventory_collection.py --fail-on-new
git diff --quiet 5fa8946872e3263049be1b3c0cdf78203596e581 -- \
  'NSI/chapitres/TNSI-*' 'NSI/referentiel/capacites_TNSI_*' \
  NSI/docs/11_perimetre_terminale.md \
  NSI/sources/txt/BO2019_NSI_terminale.txt 'NSI/build/MANUEL_TNSI*'
git status --porcelain -- \
  'NSI/chapitres/TNSI-*' 'NSI/referentiel/capacites_TNSI_*' \
  NSI/docs/11_perimetre_terminale.md \
  NSI/sources/txt/BO2019_NSI_terminale.txt 'NSI/build/MANUEL_TNSI*'
```

Verifier separement le rouge attendu :

```bash
python - <<'PY'
import subprocess

completed = subprocess.run(
    ["python", "scripts/review_1nsi_content.py", "--verify-scope"],
    capture_output=True,
    text=True,
)
output = (completed.stdout + completed.stderr).strip()
assert completed.returncode == 2, (completed.returncode, output)
assert output.endswith("scope drift: BUILD_MANIFEST"), output
assert output.count("scope drift:") == 1, output
PY
```

Les autres commandes retournent 0 et les deux controles TNSI ne produisent
aucune sortie.
