# OpenRouter-only External Provider Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Faire d’OpenRouter l’unique passerelle LLM externe active du dépôt, sans réseau dans les tests/CI, sans altérer les transports RAG ni les preuves historiques.

**Architecture:** Un paquet racine non ambigu, `nexus_external`, porte le seul client HTTP LLM et la classification partagée. Les deux ingestions et les deux juges du corpus découvrent le checkout depuis `__file__`, prouvent la provenance de l’import, puis délèguent au client commun ; le pré-jugement déterministe reste hors réseau. Le travail suit quatre commits atomiques Red, Green, documentation et inventaire, sur une branche isolée de Wave 0.

**Tech Stack:** Python 3.12, `httpx==0.28.1`, dataclasses gelées, Pytest 9 en mode importlib, JSON/YAML, Git worktrees, scripts d’inventaire Nexus.

---

## Contrat d’exécution

- Spécification approuvée : `docs/superpowers/specs/2026-08-13-openrouter-only-external-provider-design.md`.
- Base documentaire attendue : le commit qui contient la présente spécification et ce plan.
- Worktree d’implémentation : `/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only`.
- Branche d’implémentation : `green/openrouter-only`.
- Aucun appel réseau LLM, Chutes, OpenRouter ou catalogue `/api/v1/models` n’est lancé automatiquement.
- Chaque commande Bash commence par `set -euo pipefail`, fixe un répertoire de travail absolu et écrit ses preuves temporaires hors dépôt.
- Toute commande qui produit un code rouge attendu est entourée de `set +e`/capture/`set -e`, puis son code et sa cause sont assertés.
- `HARD STOP` signifie : ne pas corriger, ne pas assouplir un test, ne pas poursuivre au commit suivant ; consigner le SHA, la commande, le code et la sortie, puis demander une décision humaine.
- Les imports futurs sont placés dans le corps des tests au jalon Red. Une erreur de collecte n’est jamais un Red acceptable.
- Ne jamais transformer un test en `skip`, `xfail`, filtre permissif ou recherche négative sur un fichier dont la présence n’a pas été prouvée.
- Ne pas modifier `docs/codex/QUALITY_GATES.md`, `docs/codex/CI_AUDIT_PHASE_0.md`, les workflows ou les Makefiles : ils sont lus et scannés uniquement.
- Les anciens plans, spécifications, audits, rapports et verdicts restent des preuves historiques ; une occurrence historique de Chutes ou Anthropic n’est pas réécrite.
- Le smoke test humain OpenRouter est hors plan automatique. S’il est demandé séparément, il reçoit un commit `[AUDIT] consigne le smoke OpenRouter` sous `audit/openrouter/`; sinon aucun artefact de smoke n’est créé.

## Cartographie des fichiers

**Créations Red :**

- `tests/test_openrouter_client.py` — protocole HTTP, erreurs expurgées, enveloppe et usage stricts.
- `tests/test_openrouter_classification.py` — matrice clé/modèle, parseur fermé et barrière de métadonnées.
- `tests/test_external_provider_policy.py` — inventaire fail-closed des transports, configurations, autorités et historiques.
- `Mathematiques/manuel-maths/tests/test_ingest_openrouter.py` — adaptateur Mathématiques et commande sans extraction/réseau.
- `NSI/tests/test_ingest_openrouter.py` — adaptateur NSI et commande sans extraction/réseau.
- `NSI/corpus_nsi/tests/test_openrouter_judges.py` — juges, provenance, journal v2 et compatibilité v1.

**Adaptations Red :**

- `NSI/corpus_nsi/tests/test_manifest_separation.py` — garde ses trois tests et ferme l’inventaire OpenRouter.
- `NSI/corpus_nsi/tests/test_rag_governance_and_indexes.py` — remplace le contrat LLM local par les deux variables OpenRouter.
- `NSI/corpus_nsi/tests/test_secret_guard.py` — clé OpenRouter d’exemple vide et vraies clés refusées.
- `NSI/corpus_nsi/tests/test_substance_judge_pipeline.py` — mode conservateur, zéro réseau et non-promotion.
- `NSI/corpus_nsi/tests/test_substance_hardened.py` — préservation sur erreurs OpenRouter expurgées.
- `NSI/corpus_nsi/tests/test_judge_collection_barriers.py` — transport RAG séparé inchangé.
- `NSI/corpus_nsi/tests/test_policy_checker_ast.py` — barrières existantes inchangées face à la migration.

**Créations Green :**

- `nexus_external/__init__.py` — export public fermé.
- `nexus_external/openrouter_client.py` — seul endpoint et seul client HTTP LLM.
- `nexus_external/classification.py` — heuristique, classification configurée et parseur distant pur.

**Modifications Green :**

- `Mathematiques/manuel-maths/scripts/ingest.py` et `NSI/scripts/ingest.py` — imports d’extraction paresseux et délégation de `classify()`.
- `NSI/corpus_nsi/scripts/judge_campaign.py` — Chat Completions, journal v2 et configuration `.env.rag`.
- `NSI/corpus_nsi/scripts/substance_judge.py` — seul transport LLM migré ; `_http_json()` RAG conservé.
- `NSI/corpus_nsi/scripts/run_substance_judge.py` — libellé et modèle déterministes honnêtes.
- `NSI/corpus_nsi/scripts/check_rag_config.py`, `.env.rag.example`, `rag_config.example.yml` — autorité OpenRouter unique, RAG préservé.
- `Mathematiques/manuel-maths/.env.example`, `NSI/.env.example` — `OPENROUTER_API_KEY` et `OPENROUTER_MODEL` vides.
- `Mathematiques/manuel-maths/requirements.txt`, `NSI/requirements.txt` — retrait d’`anthropic`.
- `NSI/corpus_nsi/requirements.txt` — ajout exact de `httpx==0.28.1`.
- `requirements-ci-audit.txt` — fermeture `--no-deps` avec les pins de la spécification.

**Modifications documentation, et elles seules :**

- Les quatre autorités : `AGENTS.md`, `.agents/skills/nexus-manual-quality/SKILL.md`, `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md`, `README.md`.
- Les treize guides actifs de la section 8.4 de la spécification : `Mathematiques/PROMPT_MISSION_AUTONOME.md`, `Mathematiques/workflow_production_manuel.md`, `Mathematiques/manuel-maths/README.md`, `Mathematiques/manuel-maths/CAHIER_DES_CHARGES.md`, `Mathematiques/manuel-maths/docs/02_workflow_production.md`, `Mathematiques/manuel-maths/docs/03_architecture_technique.md`, `NSI/CAHIER_DES_CHARGES.md`, `NSI/docs/02_workflow_production.md`, `NSI/docs/03_architecture_technique.md`, `NSI/corpus_nsi/README.md`, `NSI/corpus_nsi/rag_connection.md`, `NSI/corpus_nsi/substance_pipeline.md`, `NSI/corpus_nsi/docs/enrichment_roadmap.md` si sa campagne reste prescriptive.

**Sorties générées du commit Audit :**

- `NSI/corpus_nsi/manifest_tooling.csv`.
- `NSI/corpus_nsi/inventory_report.md`.

## Chunk 1: Isolation et baselines attestées

### Task 1: Créer le worktree d’implémentation sans déplacer le WIP

**Files:**

- Read: `AGENTS.md`
- Read: `NSI/corpus_nsi/AGENTS.md`
- Read: `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md`
- Read: `docs/codex/QUALITY_GATES.md`
- Read: `docs/codex/CI_AUDIT_PHASE_0.md`
- Read: `docs/superpowers/specs/2026-08-13-openrouter-only-external-provider-design.md`

- [ ] **Step 1: Relever l’état du worktree documentaire**

```bash
set -euo pipefail
DOC_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/openrouter-only
cd "$DOC_ROOT"
git status --short --branch
git rev-parse HEAD
git log --oneline --decorate -15
git diff --stat
git diff --check
test -z "$(git status --short)"
test "$(git branch --show-current)" = "docs/openrouter-only"
```

Expected: worktree propre, HEAD contient le plan et la spécification approuvée. Sinon `HARD STOP`.

- [ ] **Step 2: Relire visiblement chaque autorité applicable**

```bash
set -euo pipefail
DOC_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/openrouter-only
cd "$DOC_ROOT"
test -s AGENTS.md
sed -n '1,$p' AGENTS.md
test -s NSI/corpus_nsi/AGENTS.md
sed -n '1,$p' NSI/corpus_nsi/AGENTS.md
test -s CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md
sed -n '1,$p' CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md
test -s docs/codex/QUALITY_GATES.md
sed -n '1,$p' docs/codex/QUALITY_GATES.md
test -s docs/codex/CI_AUDIT_PHASE_0.md
sed -n '1,$p' docs/codex/CI_AUDIT_PHASE_0.md
test -s docs/superpowers/specs/2026-08-13-openrouter-only-external-provider-design.md
sed -n '1,$p' docs/superpowers/specs/2026-08-13-openrouter-only-external-provider-design.md
```

Expected: six fichiers présents et lus intégralement. Le plus proche `NSI/corpus_nsi/AGENTS.md` s’ajoute aux règles racine pour tout fichier du corpus.

- [ ] **Step 3: Relever les contraintes d’exécution**

Consigner avant action : branche dédiée et WIP préservé ; TDD sans `skip`/`xfail` ; quatre processus Pytest ; règles corpus plus proches ; aucun nouvel appel Chutes ; historiques immuables ; aucun réseau LLM automatique ; `release-strict` reste rouge ; Makefiles, workflows, `QUALITY_GATES` et `CI_AUDIT` en lecture seule ; commits atomiques ; revues indépendantes.

- [ ] **Step 4: Vérifier que branche et cible d’implémentation n’existent pas**

```bash
set -euo pipefail
DOC_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/openrouter-only
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$DOC_ROOT"
test ! -e "$IMPL_ROOT"
if git show-ref --verify --quiet refs/heads/green/openrouter-only; then
  printf '%s\n' 'HARD STOP: branche green/openrouter-only déjà présente' >&2
  exit 1
fi
```

Expected: cible absente et nom de branche libre. Ne supprimer ni branche ni dossier pour forcer le passage.

- [ ] **Step 5: Créer la branche depuis le SHA documentaire exact**

```bash
set -euo pipefail
DOC_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/openrouter-only
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$DOC_ROOT"
PLAN_SHA=$(git rev-parse HEAD)
git worktree add -b green/openrouter-only "$IMPL_ROOT" "$PLAN_SHA"
git -C "$IMPL_ROOT" rev-parse HEAD | grep -Fx "$PLAN_SHA"
test "$(git -C "$IMPL_ROOT" branch --show-current)" = "green/openrouter-only"
test -e "$IMPL_ROOT/.git"
```

Expected: le worktree est créé sur le commit documentaire exact ; `.git.exists()` est vrai même si `.git` est un fichier de worktree.

- [ ] **Step 6: Relever l’état obligatoire du nouveau worktree**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
git status --short --branch
git rev-parse HEAD
git log --oneline --decorate -15
git diff --stat
git diff --check
test -z "$(git status --short)"
```

Expected: branche `green/openrouter-only`, aucun WIP, aucun diff.

### Task 2: Sceller les baselines et les catégories historiques

**Files:**

- Read only: `.github/workflows/*.yml`
- Read only: `NSI/corpus_nsi/.github/workflows/ci.yml`
- Read only: `audit/**`, `docs/codex/**`, anciens `docs/superpowers/**`
- Read only: `NSI/corpus_nsi/substance_reviews/campaign/_usage_log.json`

- [ ] **Step 1: Créer un dossier de preuves temporaire hors dépôt**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
EVIDENCE_ROOT=$(mktemp -d /tmp/nexus-openrouter-baseline.XXXXXX)
mapfile -t ACTIVE_POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-baseline-pointer.*' ! -name '*.complete' -print)
test "${#ACTIVE_POINTERS[@]}" -eq 0
POINTER=$(mktemp /tmp/nexus-openrouter-baseline-pointer.XXXXXX)
chmod 600 "$POINTER"
printf '%s\n' "$EVIDENCE_ROOT" > "$POINTER"
test -O "$POINTER"
test ! -L "$POINTER"
test "$(stat -c '%a' "$POINTER")" = 600
printf '%s\n' "$EVIDENCE_ROOT"
test "${EVIDENCE_ROOT#${IMPL_ROOT}/}" = "$EVIDENCE_ROOT"
```

Expected: chemin sous `/tmp`, jamais inventorié ni committé. Le conserver pour les comparaisons finales de cette session.

- [ ] **Step 2: Capturer l’inventaire suivi avant modification**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-baseline-pointer.*' ! -name '*.complete' -print)
test "${#POINTERS[@]}" -eq 1
POINTER=${POINTERS[0]}
test -O "$POINTER"; test ! -L "$POINTER"; test "$(stat -c '%a' "$POINTER")" = 600
EVIDENCE_ROOT=$(cat "$POINTER")
case "$EVIDENCE_ROOT" in /tmp/nexus-openrouter-baseline.*) ;; *) exit 1 ;; esac
test -d "$EVIDENCE_ROOT"
cd "$IMPL_ROOT"
git ls-files -z | sort -z > "$EVIDENCE_ROOT/git-ls-files.before.zlist"
sha256sum "$EVIDENCE_ROOT/git-ls-files.before.zlist" > "$EVIDENCE_ROOT/git-ls-files.before.sha256"
```

Expected: snapshot NUL-safe de la surface suivie.

- [ ] **Step 3: Empreinter les catégories historiques protégées**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-baseline-pointer.*' ! -name '*.complete' -print)
test "${#POINTERS[@]}" -eq 1
POINTER=${POINTERS[0]}
test -O "$POINTER"; test ! -L "$POINTER"; test "$(stat -c '%a' "$POINTER")" = 600
EVIDENCE_ROOT=$(cat "$POINTER")
case "$EVIDENCE_ROOT" in /tmp/nexus-openrouter-baseline.*) ;; *) exit 1 ;; esac
test -d "$EVIDENCE_ROOT"
cd "$IMPL_ROOT"
git ls-files -z -- \
  audit/chutes \
  audit \
  docs/codex \
  docs/superpowers/plans \
  docs/superpowers/specs \
  NSI/corpus_nsi/reports \
  NSI/corpus_nsi/docs/judge_campaign_plan.md \
  NSI/corpus_nsi/substance_reviews \
| sort -z > "$EVIDENCE_ROOT/protected-paths.zlist"
while IFS= read -r -d '' path; do
  printf '%s  %s\n' "$(git hash-object -- "$path")" "$path"
done < "$EVIDENCE_ROOT/protected-paths.zlist" \
  > "$EVIDENCE_ROOT/protected.before.hashes"
```

Expected: liste triée et hashes de blobs. Au contrôle final, autoriser uniquement le nouveau plan déjà dans la base et, si le journal a réellement été utilisé par un test sur copie temporaire, aucune modification du journal suivi.

- [ ] **Step 4: Sceller profondément les objets v1 du journal historique**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-baseline-pointer.*' ! -name '*.complete' -print)
test "${#POINTERS[@]}" -eq 1
POINTER=${POINTERS[0]}
test -O "$POINTER"; test ! -L "$POINTER"; test "$(stat -c '%a' "$POINTER")" = 600
EVIDENCE_ROOT=$(cat "$POINTER")
case "$EVIDENCE_ROOT" in /tmp/nexus-openrouter-baseline.*) ;; *) exit 1 ;; esac
test -d "$EVIDENCE_ROOT"
cd "$IMPL_ROOT"
python3 - "$EVIDENCE_ROOT/usage-v1.before.json" <<'PY'
import json
import sys
from pathlib import Path

source = Path("NSI/corpus_nsi/substance_reviews/campaign/_usage_log.json")
payload = json.loads(source.read_text(encoding="utf-8"))
assert isinstance(payload, list)
v1 = [row for row in payload if isinstance(row, dict) and row.get("schema_version") != 2]
Path(sys.argv[1]).write_text(
    json.dumps(v1, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
PY
sha256sum "$EVIDENCE_ROOT/usage-v1.before.json" > "$EVIDENCE_ROOT/usage-v1.before.sha256"
```

Expected: copie temporaire ordonnée des entrées v1 ; aucun fichier du dépôt écrit.

- [ ] **Step 5: Scanner les workflows et confirmer que le workflow corpus est dormant pour la racine**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
test -s .github/workflows/ci-audit-collection.yml
test -s .github/workflows/ci-mathematiques.yml
test -s .github/workflows/ci-nsi.yml
test -s NSI/corpus_nsi/.github/workflows/ci.yml
rg -n 'pytest|requirements-ci-audit|--no-deps' \
  .github/workflows/ci-audit-collection.yml \
  .github/workflows/ci-mathematiques.yml \
  .github/workflows/ci-nsi.yml \
  NSI/corpus_nsi/.github/workflows/ci.yml
```

Expected: le corpus possède son workflow interne, mais Pytest racine ne collecte que les trois `testpaths` de `pyproject.toml`. Ne pas prétendre que le nouveau contrat corpus est déjà branché dans la CI racine.

### Task 3: Reproduire les baselines sans modifier le worktree

**Files:**

- Read only: `pyproject.toml`
- Read only: `scripts/inventory_collection.py`
- Read only: `NSI/corpus_nsi/tests/**`

- [ ] **Step 1: Reproduire la collecte racine historique**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-baseline-pointer.*' ! -name '*.complete' -print)
test "${#POINTERS[@]}" -eq 1
POINTER=${POINTERS[0]}
test -O "$POINTER"; test ! -L "$POINTER"; test "$(stat -c '%a' "$POINTER")" = 600
EVIDENCE_ROOT=$(cat "$POINTER")
case "$EVIDENCE_ROOT" in /tmp/nexus-openrouter-baseline.*) ;; *) exit 1 ;; esac
test -d "$EVIDENCE_ROOT"
cd "$IMPL_ROOT"
set +e
python3 -m pytest --collect-only -q -p no:cacheprovider \
  > "$EVIDENCE_ROOT/root-collect.out" 2>&1
ROOT_COLLECT_RC=$?
set -e
test "$ROOT_COLLECT_RC" -eq 2
rg -F '5032 tests collected' "$EVIDENCE_ROOT/root-collect.out"
test "$(grep -c '^ERROR collecting ' "$EVIDENCE_ROOT/root-collect.out")" -eq 1
rg -F 'assemble.BOOK_VARIANTS' "$EVIDENCE_ROOT/root-collect.out"
```

Expected: 5 032 tests découverts et échec historique de collecte exclusivement lié à la collision `assemble.BOOK_VARIANTS`. Tout autre motif est `HARD STOP`. Cette dette n’est ni corrigée ni utilisée pour masquer les quatre processus ciblés.

- [ ] **Step 2: Reproduire la suite corpus indépendante**

```bash
set -euo pipefail
CORPUS_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-baseline-pointer.*' ! -name '*.complete' -print)
test "${#POINTERS[@]}" -eq 1
POINTER=${POINTERS[0]}
test -O "$POINTER"; test ! -L "$POINTER"; test "$(stat -c '%a' "$POINTER")" = 600
EVIDENCE_ROOT=$(cat "$POINTER")
case "$EVIDENCE_ROOT" in /tmp/nexus-openrouter-baseline.*) ;; *) exit 1 ;; esac
test -d "$EVIDENCE_ROOT"
cd "$CORPUS_ROOT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest --collect-only -q -p no:cacheprovider \
    tests/test_rag_governance_and_indexes.py \
    tests/test_secret_guard.py \
    tests/test_substance_judge_pipeline.py \
    tests/test_substance_hardened.py \
    tests/test_judge_collection_barriers.py \
    tests/test_policy_checker_ast.py \
  | sed -n '/^tests\//p' | sort > "$EVIDENCE_ROOT/corpus-baseline-85.nodeids"
test "$(wc -l < "$EVIDENCE_ROOT/corpus-baseline-85.nodeids")" -eq 85
test "$(sort -u "$EVIDENCE_ROOT/corpus-baseline-85.nodeids" | wc -l)" -eq 85
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
    tests/test_rag_governance_and_indexes.py \
    tests/test_secret_guard.py \
    tests/test_substance_judge_pipeline.py \
    tests/test_substance_hardened.py \
    tests/test_judge_collection_barriers.py \
    tests/test_policy_checker_ast.py \
  | tee "$EVIDENCE_ROOT/corpus-baseline.out"
rg -F '85 passed' "$EVIDENCE_ROOT/corpus-baseline.out"
```

Expected: ensemble trié exact de 85 nodeids et `85 passed`, aucun accès réseau. Ce fichier de preuve est la source indépendante comparée littéralement aux 27 nouveaux juges et trois manifest en Tasks 7 et 19. Sinon `HARD STOP` avant Red.

- [ ] **Step 3: Reproduire l’inventaire direct sur la branche dédiée**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-baseline-pointer.*' ! -name '*.complete' -print)
test "${#POINTERS[@]}" -eq 1
POINTER=${POINTERS[0]}
test -O "$POINTER"; test ! -L "$POINTER"; test "$(stat -c '%a' "$POINTER")" = 600
EVIDENCE_ROOT=$(cat "$POINTER")
case "$EVIDENCE_ROOT" in /tmp/nexus-openrouter-baseline.*) ;; *) exit 1 ;; esac
test -d "$EVIDENCE_ROOT"
cd "$IMPL_ROOT"
set +e
python3 scripts/inventory_collection.py --check --require-clean \
  > "$EVIDENCE_ROOT/inventory-direct.json" 2> "$EVIDENCE_ROOT/inventory-direct.err"
INVENTORY_RC=$?
set -e
test "$INVENTORY_RC" -eq 3
python3 - "$EVIDENCE_ROOT/inventory-direct.json" <<'PY'
import json
import sys

payload = json.load(open(sys.argv[1], encoding="utf-8"))
assert payload["gate"] == "check"
assert payload["success"] is False
assert payload["exit_code"] == 3
assert payload["reasons"] == [
    "check_error:branche de provenance du manifeste incohérente"
]
PY
```

Expected: code 3 attribuable à la provenance de branche/digest de la base, sans réécriture d’inventaire. Une autre cause est `HARD STOP`.

- [ ] **Step 4: Reproduire `release-strict` dans un clone local temporaire portant le nom de branche attendu**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-baseline-pointer.*' ! -name '*.complete' -print)
test "${#POINTERS[@]}" -eq 1
POINTER=${POINTERS[0]}
test -O "$POINTER"; test ! -L "$POINTER"; test "$(stat -c '%a' "$POINTER")" = 600
EVIDENCE_ROOT=$(cat "$POINTER")
case "$EVIDENCE_ROOT" in /tmp/nexus-openrouter-baseline.*) ;; *) exit 1 ;; esac
test -d "$EVIDENCE_ROOT"
cd "$IMPL_ROOT"
RELEASE_CLONE=$(mktemp -d /tmp/nexus-openrouter-release.XXXXXX)
HEAD_SHA=$(git rev-parse HEAD)
git clone --shared --no-checkout "$IMPL_ROOT" "$RELEASE_CLONE/repo"
if git -C "$RELEASE_CLONE/repo" show-ref --verify --quiet \
  refs/heads/integration/1spe-bo2026-traceability
then
  printf '%s\n' 'HARD STOP: branche locale temporaire déjà présente' >&2
  exit 1
fi
git -C "$RELEASE_CLONE/repo" branch integration/1spe-bo2026-traceability "$HEAD_SHA"
git -C "$RELEASE_CLONE/repo" symbolic-ref HEAD refs/heads/integration/1spe-bo2026-traceability
git -C "$RELEASE_CLONE/repo" read-tree -mu HEAD
test "$(git -C "$RELEASE_CLONE/repo" rev-parse HEAD)" = "$HEAD_SHA"
set +e
(
  cd "$RELEASE_CLONE/repo"
  python3 scripts/inventory_collection.py \
    --release-strict \
    --audit-dir "$RELEASE_CLONE/audit" \
    --etat-path "$RELEASE_CLONE/ETAT_COLLECTION.md"
) > "$EVIDENCE_ROOT/release-strict.json" 2> "$EVIDENCE_ROOT/release-strict.err"
RELEASE_RC=$?
set -e
test "$RELEASE_RC" -eq 7
python3 - "$EVIDENCE_ROOT/release-strict.json" <<'PY'
import json
import sys

payload = json.load(open(sys.argv[1], encoding="utf-8"))
assert payload["gate"] == "release-strict"
assert payload["success"] is False
assert payload["blocker_count"] == 67
PY
test -z "$(git status --short)"
```

Expected: code 7 et exactement 67 bloqueurs réels, sorties sous `/tmp`, worktree inchangé. Le `NO-GO` reste vrai.

## Chunk 2: Red du client OpenRouter partagé

### Task 4: Écrire le contrat Red du client partagé

**Files:**

- Create: `tests/test_openrouter_client.py`
- Create: `tests/test_openrouter_classification.py`

- [ ] **Step 1: Installer et prouver les barrières réseau autouse racine**

Créer les deux fichiers par `apply_patch` avec leurs chemins absolus. Chacun contient sa propre fixture, sans import de production au niveau module :

```python
@pytest.fixture(autouse=True)
def _forbid_real_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def blocked(*args: object, **kwargs: object) -> None:
        raise AssertionError("network forbidden by OpenRouter contract tests")

    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(urllib.request, "urlopen", blocked)
```

Dans chaque fixture, après les trois monkeypatches, boucler immédiatement sur trois lambdas qui appellent réellement `socket.socket().connect(("127.0.0.1", 9))`, `socket.create_connection(("127.0.0.1", 9))` et `urllib.request.urlopen("http://127.0.0.1:9")`, chacune sous `pytest.raises(AssertionError)`. Cette mutation prouve le garde sans créer de node supplémentaire ni paramétrisation.

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
XML=$(mktemp /tmp/nexus-openrouter-red-root-blockers.XXXXXX.xml)
cd "$IMPL_ROOT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest --collect-only -q -p no:cacheprovider \
    tests/test_openrouter_client.py tests/test_openrouter_classification.py \
    --junitxml "$XML"
python3 - "$XML" <<'PY'
import xml.etree.ElementTree as ET
import sys
r = ET.parse(sys.argv[1]).getroot()
s = r.findall(".//testsuite") or [r]
got = {k: sum(int(x.get(k, "0")) for x in s) for k in ("tests", "failures", "errors", "skipped")}
assert got == {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}, got
PY
```

- [ ] **Step 2: Écrire les fixtures HTTP communes dans le test client**

Utiliser `apply_patch` sur le chemin absolu `/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/tests/test_openrouter_client.py`. Les imports de `nexus_external.openrouter_client` sont dans chaque test ou dans une fonction appelée pendant l’exécution, jamais au niveau module. Une fixture de succès doit retourner :

```python
{
    "id": "gen-openrouter-001",
    "model": "vendor/model-explicit",
    "provider": "provider-observed",
    "choices": [{
        "finish_reason": "stop",
        "message": {"role": "assistant", "content": "réponse complète"},
    }],
    "usage": {
        "prompt_tokens": 11,
        "completion_tokens": 7,
        "total_tokens": 18,
        "cost": 0.0012345,
        "prompt_tokens_details": {"cached_tokens": 3, "cache_write_tokens": 2},
    },
}
```

Le handler `httpx.MockTransport` capture requête et compteur d’appels ; tout transport inattendu lève immédiatement.

- [ ] **Step 3: Écrire `test_chat_completion_posts_to_exact_openrouter_endpoint`**

Dans le corps du test, importer le futur client, injecter `httpx.MockTransport`, appeler une fois la complétion et exiger l’URL exacte `https://openrouter.ai/api/v1/chat/completions`, méthode `POST` et un seul appel.

- [ ] **Step 4: Écrire `test_chat_completion_sends_bearer_and_json_headers`**

Dans le corps du test, importer le futur client et exiger `Authorization: Bearer <sentinelle>` et `Content-Type: application/json`; la clé ne doit apparaître ni dans l’URL ni dans une représentation expurgée de la requête.

- [ ] **Step 5: Écrire `test_chat_completion_sends_one_model_and_max_completion_tokens`**

Exiger d'abord un corps JSON portant exactement le modèle demandé et `max_completion_tokens`, sans `max_tokens`, second modèle, fournisseur direct ni URL de repli. Dans le même node, boucler ensuite avec un transport sentinelle non appelable sur la matrice fermée suivante : `max_completion_tokens` égal à `0`, `True` ou `16_385` ; messages vides ou non séquentiels ; message non objet ; rôle absent ou hors de `system|user|assistant` ; contenu absent, non chaîne ou blanc ; clé supplémentaire en plus de `role` et `content`. Chaque cas lève `OpenRouterError(category="configuration")` avant transport et aucune valeur entrante n'apparaît dans l'exception.

- [ ] **Step 6: Écrire `test_chat_completion_uses_injected_mock_transport_without_socket`**

Prouver d’abord la fixture autouse en appelant réellement, dans une boucle interne, les trois primitives bloquées sous `pytest.raises(AssertionError)`, puis exiger qu’un transport injecté rende la réponse factice sans socket. Ce node est la mutation positive du garde réseau du module.

- [ ] **Step 7: Collecter puis observer le Red des quatre requêtes HTTP**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
XML=$(mktemp /tmp/nexus-openrouter-client-request.XXXXXX.xml)
OUT=$(mktemp /tmp/nexus-openrouter-client-request.XXXXXX.out)
COLLECT=$(mktemp /tmp/nexus-openrouter-client-request.XXXXXX.collect)
cd "$IMPL_ROOT"
NODES=(
  tests/test_openrouter_client.py::test_chat_completion_posts_to_exact_openrouter_endpoint
  tests/test_openrouter_client.py::test_chat_completion_sends_bearer_and_json_headers
  tests/test_openrouter_client.py::test_chat_completion_sends_one_model_and_max_completion_tokens
  tests/test_openrouter_client.py::test_chat_completion_uses_injected_mock_transport_without_socket
)
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest --collect-only -q -p no:cacheprovider "${NODES[@]}" > "$COLLECT"
test "$(sed -n '/^tests\//p' "$COLLECT" | wc -l)" -eq 4
for node in "${NODES[@]}"; do rg -Fx -- "$node" "$COLLECT"; done
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider "${NODES[@]}" --junitxml "$XML" > "$OUT" 2>&1
RC=$?
set -e
test "$RC" -eq 1
! rg -F 'ERROR collecting' "$OUT"
rg -F 'nexus_external' "$OUT"
python3 - "$XML" "${NODES[@]##*::}" <<'PY'
import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
suites = root.findall(".//testsuite") or [root]
got = {key: sum(int(s.get(key, "0")) for s in suites) for key in ("tests", "failures", "errors", "skipped")}
expected_failed = set(sys.argv[2:])
failed = {case.get("name", "") for case in root.findall(".//testcase") if case.find("failure") is not None}
assert got == {"tests": 4, "failures": len(expected_failed), "errors": 0, "skipped": 0}, got
assert failed == expected_failed, (failed, expected_failed)
PY
```

Expected: collecte exacte de quatre IDs, puis quatre failures causées par le paquet futur absent ; le garde réseau a été exercé avant l’import futur dans le quatrième node.

- [ ] **Step 8: Écrire `test_chat_completion_caps_timeout_at_thirty_seconds`**

Importer le futur client dans le corps du test et inspecter `request.extensions["timeout"]` dans le handler : chaque borne connect/read/write/pool configurée doit être positive et inférieure ou égale à 30 secondes.

- [ ] **Step 9: Écrire `test_chat_completion_does_not_follow_redirects`**

Faire répondre le transport par une redirection 307 vers une sentinelle hostile ; exiger une erreur expurgée, un seul appel et aucune seconde requête vers la cible.

- [ ] **Step 10: Écrire `test_chat_completion_returns_validated_structured_result`**

Exiger un `OpenRouterCompletion` validé portant contenu, `generation_id`, modèle retourné, fournisseur optionnel et un objet usage structuré dont tous les champs correspondent à la fixture.

- [ ] **Step 11: Écrire `test_completion_and_usage_are_immutable`**

Construire directement un futur `OpenRouterUsage`, puis un futur `OpenRouterCompletion` qui le contient, sans appeler `chat_completion`. Exiger `dataclasses.FrozenInstanceError` pour toute tentative de mutation de la complétion et de son usage, sans exposer le dictionnaire brut mutable. Le Red initial reste causé exclusivement par l'absence du paquet futur ; dès que les deux dataclasses existent, ce node peut devenir vert indépendamment du transport.

- [ ] **Step 12: Collecter puis observer le Red sûreté/résultat**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
XML=$(mktemp /tmp/nexus-openrouter-client-safety.XXXXXX.xml)
OUT=$(mktemp /tmp/nexus-openrouter-client-safety.XXXXXX.out)
COLLECT=$(mktemp /tmp/nexus-openrouter-client-safety.XXXXXX.collect)
cd "$IMPL_ROOT"
NODES=(
  tests/test_openrouter_client.py::test_chat_completion_caps_timeout_at_thirty_seconds
  tests/test_openrouter_client.py::test_chat_completion_does_not_follow_redirects
  tests/test_openrouter_client.py::test_chat_completion_returns_validated_structured_result
  tests/test_openrouter_client.py::test_completion_and_usage_are_immutable
)
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest --collect-only -q -p no:cacheprovider "${NODES[@]}" > "$COLLECT"
test "$(sed -n '/^tests\//p' "$COLLECT" | wc -l)" -eq 4
for node in "${NODES[@]}"; do rg -Fx -- "$node" "$COLLECT"; done
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider "${NODES[@]}" --junitxml "$XML" > "$OUT" 2>&1
RC=$?
set -e
test "$RC" -eq 1
! rg -F 'ERROR collecting' "$OUT"
rg -F 'nexus_external' "$OUT"
python3 - "$XML" "${NODES[@]##*::}" <<'PY'
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot(); suites = root.findall(".//testsuite") or [root]
got = {k: sum(int(s.get(k, "0")) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
expected = set(sys.argv[2:]); failed = {c.get("name", "") for c in root.findall(".//testcase") if c.find("failure") is not None}
assert got == {"tests": 4, "failures": len(expected), "errors": 0, "skipped": 0}, got
assert failed == expected, (failed, expected)
PY
```

Expected: quatre nodes collectés et quatre failures `nexus_external` d’exécution, sans redirection suivie ni socket.

- [ ] **Step 13: Écrire `test_http_failure_maps_to_sanitized_error_category`**

Boucler dans ce seul node sur 400, 401, 402, 403, 408, 429, 500, 502, 503 et 529 ; exiger pour chaque statut la catégorie fermée attendue, un appel unique et aucun corps, prompt, header ou secret dans l’exception.

- [ ] **Step 14: Écrire `test_http_200_refuses_root_error_object`**

Retourner HTTP 200 avec un champ racine `error`; exiger une erreur de protocole expurgée plutôt qu’une complétion partielle.

- [ ] **Step 15: Écrire `test_http_200_refuses_choice_error_object`**

Retourner HTTP 200 avec `choices[0].error`; exiger le même refus fail-closed et aucun contenu brut dans exception/logs.

- [ ] **Step 16: Écrire `test_http_200_refuses_non_stop_finish_reason`**

Boucler en interne sur `error`, `length`, `content_filter`, chaîne vide et valeur non chaîne ; aucune de ces fins ne doit produire une complétion publiable.

- [ ] **Step 17: Collecter puis observer le Red HTTP/enveloppe**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
XML=$(mktemp /tmp/nexus-openrouter-client-http.XXXXXX.xml)
OUT=$(mktemp /tmp/nexus-openrouter-client-http.XXXXXX.out)
COLLECT=$(mktemp /tmp/nexus-openrouter-client-http.XXXXXX.collect)
cd "$IMPL_ROOT"
NODES=(
  tests/test_openrouter_client.py::test_http_failure_maps_to_sanitized_error_category
  tests/test_openrouter_client.py::test_http_200_refuses_root_error_object
  tests/test_openrouter_client.py::test_http_200_refuses_choice_error_object
  tests/test_openrouter_client.py::test_http_200_refuses_non_stop_finish_reason
)
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest --collect-only -q -p no:cacheprovider "${NODES[@]}" > "$COLLECT"
test "$(sed -n '/^tests\//p' "$COLLECT" | wc -l)" -eq 4
for node in "${NODES[@]}"; do rg -Fx -- "$node" "$COLLECT"; done
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider "${NODES[@]}" --junitxml "$XML" > "$OUT" 2>&1
RC=$?
set -e
test "$RC" -eq 1
! rg -F 'ERROR collecting' "$OUT"
rg -F 'nexus_external' "$OUT"
python3 - "$XML" "${NODES[@]##*::}" <<'PY'
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot(); suites = root.findall(".//testsuite") or [root]
got = {k: sum(int(s.get(k, "0")) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
expected = set(sys.argv[2:]); failed = {c.get("name", "") for c in root.findall(".//testcase") if c.find("failure") is not None}
assert got == {"tests": 4, "failures": len(expected), "errors": 0, "skipped": 0}, got
assert failed == expected, (failed, expected)
PY
```

Expected: quatre failures d’implémentation et des matrices internes non paramétrées ; aucun statut/enveloppe invalide n’est compensé.

- [ ] **Step 18: Écrire `test_response_rejects_malformed_envelope_component`**

Boucler dans ce node sur racine non objet, `choices` absent/non liste/vide, premier choix non objet, message non objet, rôle autre qu’`assistant`, contenu absent/non chaîne/vide, clé de message supplémentaire, ainsi que `provider` présent mais vide ou non chaîne ; chaque cas doit être refusé globalement. Ajouter un cas positif avec deux choix valides distincts et exiger que seul le premier soit consommé : la présence de choix supplémentaires n'est pas une erreur si le premier choix est entièrement valide.

- [ ] **Step 19: Écrire `test_errors_and_logs_never_expose_secret_prompt_or_raw_body`**

Placer quatre sentinelles distinctes dans clé, prompt, headers et corps de réponse ; exiger leur absence de `str(exc)`, `repr(exc)`, `exc.args` et de tous les messages `caplog`.

- [ ] **Step 20: Écrire `test_client_does_not_retry_failed_request`**

Faire échouer le transport dès le premier appel et exiger compteur exact `1`, aucune temporisation et une erreur expurgée. Les retries métier restent la responsabilité des juges.

- [ ] **Step 21: Collecter puis observer le Red du protocole expurgé**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
XML=$(mktemp /tmp/nexus-openrouter-client-protocol.XXXXXX.xml)
OUT=$(mktemp /tmp/nexus-openrouter-client-protocol.XXXXXX.out)
COLLECT=$(mktemp /tmp/nexus-openrouter-client-protocol.XXXXXX.collect)
cd "$IMPL_ROOT"
NODES=(
  tests/test_openrouter_client.py::test_response_rejects_malformed_envelope_component
  tests/test_openrouter_client.py::test_errors_and_logs_never_expose_secret_prompt_or_raw_body
  tests/test_openrouter_client.py::test_client_does_not_retry_failed_request
)
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest --collect-only -q -p no:cacheprovider "${NODES[@]}" > "$COLLECT"
test "$(sed -n '/^tests\//p' "$COLLECT" | wc -l)" -eq 3
for node in "${NODES[@]}"; do rg -Fx -- "$node" "$COLLECT"; done
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider "${NODES[@]}" --junitxml "$XML" > "$OUT" 2>&1
RC=$?
set -e
test "$RC" -eq 1
! rg -F 'ERROR collecting' "$OUT"
rg -F 'nexus_external' "$OUT"
python3 - "$XML" "${NODES[@]##*::}" <<'PY'
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot(); suites = root.findall(".//testsuite") or [root]
got = {k: sum(int(s.get(k, "0")) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
expected = set(sys.argv[2:]); failed = {c.get("name", "") for c in root.findall(".//testcase") if c.find("failure") is not None}
assert got == {"tests": 3, "failures": len(expected), "errors": 0, "skipped": 0}, got
assert failed == expected, (failed, expected)
PY
```

Expected: trois failures sur le client absent, aucun secret dans la preuve et aucun retry implicite.

- [ ] **Step 22: Écrire `test_client_rejects_blank_key_before_transport`**

Boucler sur `None`, absence, chaîne vide et espaces ; le transport sentinelle lève s’il est appelé et le test exige une erreur de configuration expurgée avant transport.

- [ ] **Step 23: Écrire `test_client_rejects_blank_model_before_transport`**

Avec une clé non vide, boucler sur modèle absent/vide/espaces ; exiger le même refus avant transport et aucune valeur par défaut implicite.

- [ ] **Step 24: Collecter puis observer le Red de configuration**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
XML=$(mktemp /tmp/nexus-openrouter-client-config.XXXXXX.xml)
OUT=$(mktemp /tmp/nexus-openrouter-client-config.XXXXXX.out)
COLLECT=$(mktemp /tmp/nexus-openrouter-client-config.XXXXXX.collect)
cd "$IMPL_ROOT"
NODES=(
  tests/test_openrouter_client.py::test_client_rejects_blank_key_before_transport
  tests/test_openrouter_client.py::test_client_rejects_blank_model_before_transport
)
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest --collect-only -q -p no:cacheprovider "${NODES[@]}" > "$COLLECT"
test "$(sed -n '/^tests\//p' "$COLLECT" | wc -l)" -eq 2
for node in "${NODES[@]}"; do rg -Fx -- "$node" "$COLLECT"; done
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider "${NODES[@]}" --junitxml "$XML" > "$OUT" 2>&1
RC=$?
set -e
test "$RC" -eq 1
! rg -F 'ERROR collecting' "$OUT"
rg -F 'nexus_external' "$OUT"
python3 - "$XML" "${NODES[@]##*::}" <<'PY'
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot(); suites = root.findall(".//testsuite") or [root]
got = {k: sum(int(s.get(k, "0")) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
expected = set(sys.argv[2:]); failed = {c.get("name", "") for c in root.findall(".//testcase") if c.find("failure") is not None}
assert got == {"tests": 2, "failures": len(expected), "errors": 0, "skipped": 0}, got
assert failed == expected, (failed, expected)
PY
```

Expected: deux failures d’API absente ; le double de transport n’a reçu aucun appel.

- [ ] **Step 25: Écrire `test_usage_rejects_invalid_required_accounting`**

Boucler en interne sur tokens requis absents, booléens, négatifs ou incohérents (`prompt + completion != total`) et coût absent, booléen, négatif, NaN ou infini ; chaque réponse entière est refusée.

- [ ] **Step 26: Écrire `test_usage_rejects_invalid_cache_details`**

Boucler sur `prompt_tokens_details` non objet et compteurs cache booléens, négatifs ou supérieurs aux tokens de prompt ; aucun usage partiel n’est accepté.

- [ ] **Step 27: Écrire `test_usage_normalizes_absent_cache_counters_to_zero`**

Avec l’usage requis valide mais les détails cache absents, exiger `cached_tokens == 0` et `cache_write_tokens == 0` dans l’objet immuable.

- [ ] **Step 28: Collecter puis observer le Red de validation d’usage**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
XML=$(mktemp /tmp/nexus-openrouter-client-usage-validation.XXXXXX.xml)
OUT=$(mktemp /tmp/nexus-openrouter-client-usage-validation.XXXXXX.out)
COLLECT=$(mktemp /tmp/nexus-openrouter-client-usage-validation.XXXXXX.collect)
cd "$IMPL_ROOT"
NODES=(
  tests/test_openrouter_client.py::test_usage_rejects_invalid_required_accounting
  tests/test_openrouter_client.py::test_usage_rejects_invalid_cache_details
  tests/test_openrouter_client.py::test_usage_normalizes_absent_cache_counters_to_zero
)
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest --collect-only -q -p no:cacheprovider "${NODES[@]}" > "$COLLECT"
test "$(sed -n '/^tests\//p' "$COLLECT" | wc -l)" -eq 3
for node in "${NODES[@]}"; do rg -Fx -- "$node" "$COLLECT"; done
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider "${NODES[@]}" --junitxml "$XML" > "$OUT" 2>&1
RC=$?
set -e
test "$RC" -eq 1
! rg -F 'ERROR collecting' "$OUT"
rg -F 'nexus_external' "$OUT"
python3 - "$XML" "${NODES[@]##*::}" <<'PY'
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot(); suites = root.findall(".//testsuite") or [root]
got = {k: sum(int(s.get(k, "0")) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
expected = set(sys.argv[2:]); failed = {c.get("name", "") for c in root.findall(".//testcase") if c.find("failure") is not None}
assert got == {"tests": 3, "failures": len(expected), "errors": 0, "skipped": 0}, got
assert failed == expected, (failed, expected)
PY
```

Expected: trois failures sur la future validation stricte et aucune paramétrisation collectée.

- [ ] **Step 29: Écrire `test_usage_preserves_exact_openrouter_cost`**

Fournir `cost: 0.0012345` et exiger cette valeur retournée par OpenRouter sans table tarifaire, arrondi, recalcul ni conversion destructive.

- [ ] **Step 30: Écrire `test_response_rejects_invalid_root_generation_id`**

Boucler en interne sur identifiant racine absent, non chaîne et blanc ; refuser toute complétion sans identifiant de génération facturable.

- [ ] **Step 31: Écrire `test_response_rejects_invalid_returned_model`**

Boucler en interne sur modèle retourné absent, non chaîne et blanc ; le modèle demandé ne doit jamais masquer une réponse dépourvue de modèle observé.

- [ ] **Step 32: Collecter puis observer le Red coût/identifiants**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
XML=$(mktemp /tmp/nexus-openrouter-client-identifiers.XXXXXX.xml)
OUT=$(mktemp /tmp/nexus-openrouter-client-identifiers.XXXXXX.out)
COLLECT=$(mktemp /tmp/nexus-openrouter-client-identifiers.XXXXXX.collect)
cd "$IMPL_ROOT"
NODES=(
  tests/test_openrouter_client.py::test_usage_preserves_exact_openrouter_cost
  tests/test_openrouter_client.py::test_response_rejects_invalid_root_generation_id
  tests/test_openrouter_client.py::test_response_rejects_invalid_returned_model
)
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest --collect-only -q -p no:cacheprovider "${NODES[@]}" > "$COLLECT"
test "$(sed -n '/^tests\//p' "$COLLECT" | wc -l)" -eq 3
for node in "${NODES[@]}"; do rg -Fx -- "$node" "$COLLECT"; done
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider "${NODES[@]}" --junitxml "$XML" > "$OUT" 2>&1
RC=$?
set -e
test "$RC" -eq 1
! rg -F 'ERROR collecting' "$OUT"
rg -F 'nexus_external' "$OUT"
python3 - "$XML" "${NODES[@]##*::}" <<'PY'
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot(); suites = root.findall(".//testsuite") or [root]
got = {k: sum(int(s.get(k, "0")) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
expected = set(sys.argv[2:]); failed = {c.get("name", "") for c in root.findall(".//testcase") if c.find("failure") is not None}
assert got == {"tests": 3, "failures": len(expected), "errors": 0, "skipped": 0}, got
assert failed == expected, (failed, expected)
PY
```

Expected: exactement trois failures ; le client compte désormais 23 noms littéraux et aucune valeur comptable n’est inventée.

## Chunk 3: Red de la classification et de la policy

Dans `tests/test_openrouter_classification.py` et `tests/test_external_provider_policy.py`, tout import futur reste dans le corps du test. Chaque module possède sa fixture réseau autouse et un node de la matrice ci-dessous exerce réellement les trois primitives bloquées ; aucune paramétrisation Pytest n’est créée.

- [ ] **Step 33: Écrire `test_classification_without_key_uses_local_heuristic_without_transport`**

Créer le fichier par `apply_patch`, installer la fixture autouse, invoquer les trois primitives sous `pytest.raises(AssertionError)`, puis appeler la classification sans clé : exiger l’objet conservateur/heuristique fermé et zéro invocation du transport sentinelle. Ce node prouve le garde réseau du module.

- [ ] **Step 34: Écrire `test_classification_with_key_without_model_fails_before_transport`**

Boucler sur modèle absent/vide/espaces avec clé présente ; exiger l’erreur explicite avant transport, sans modèle par défaut.

- [ ] **Step 35: Écrire `test_classification_with_key_and_model_forwards_exact_model`**

Injecter un faux client partagé et exiger un appel unique avec le modèle exact, sans normalisation ni substitution fournisseur.

- [ ] **Step 36: Écrire `test_classification_sends_only_first_3000_fragment_characters`**

Utiliser un fragment de plus de 3 000 caractères suivi d’une sentinelle ; exiger présence exacte du préfixe `fragment[:3000]` et absence du suffixe, des variables d’environnement et des métadonnées source.

- [ ] **Step 37: Collecter puis observer le Red de la matrice clé/modèle**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
XML=$(mktemp /tmp/nexus-openrouter-classification-config.XXXXXX.xml)
OUT=$(mktemp /tmp/nexus-openrouter-classification-config.XXXXXX.out)
COLLECT=$(mktemp /tmp/nexus-openrouter-classification-config.XXXXXX.collect)
cd "$IMPL_ROOT"
NODES=(
  tests/test_openrouter_classification.py::test_classification_without_key_uses_local_heuristic_without_transport
  tests/test_openrouter_classification.py::test_classification_with_key_without_model_fails_before_transport
  tests/test_openrouter_classification.py::test_classification_with_key_and_model_forwards_exact_model
  tests/test_openrouter_classification.py::test_classification_sends_only_first_3000_fragment_characters
)
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest --collect-only -q -p no:cacheprovider "${NODES[@]}" > "$COLLECT"
test "$(sed -n '/^tests\//p' "$COLLECT" | wc -l)" -eq 4
for node in "${NODES[@]}"; do rg -Fx -- "$node" "$COLLECT"; done
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider "${NODES[@]}" --junitxml "$XML" > "$OUT" 2>&1
RC=$?
set -e
test "$RC" -eq 1
! rg -F 'ERROR collecting' "$OUT"
rg -F 'nexus_external' "$OUT"
python3 - "$XML" "${NODES[@]##*::}" <<'PY'
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot(); suites = root.findall(".//testsuite") or [root]
got = {k: sum(int(s.get(k, "0")) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
expected = set(sys.argv[2:]); failed = {c.get("name", "") for c in root.findall(".//testcase") if c.find("failure") is not None}
assert got == {"tests": 4, "failures": len(expected), "errors": 0, "skipped": 0}, got
assert failed == expected, (failed, expected)
PY
```

Expected: quatre failures dues à `nexus_external` absent ; les imports futurs n’ont pas cassé la collecte et le premier test a prouvé le garde.

- [ ] **Step 38: Écrire `test_classification_requests_200_completion_tokens`**

Capturer l’appel partagé et exiger exactement `max_completion_tokens=200`, sans ancien `max_tokens`.

- [ ] **Step 39: Écrire `test_local_heuristic_preserves_existing_chunk_type_contract`**

Boucler en interne sur les préfixes cours, méthode, exercice/problème, corrigé, activité et autre ; exiger les types historiques et les quatre autres clés conservatrices exactes.

- [ ] **Step 40: Écrire `test_remote_classification_accepts_exact_closed_object`**

Faire retourner JSON nu puis un unique fence exact `json`; exiger exactement les cinq clés `chunk_type`, `niveau`, `theme`, `capacites`, `difficulte`, types et valeurs autorisés.

- [ ] **Step 41: Écrire `test_remote_classification_rejects_invalid_closed_object_as_a_whole`**

Boucler sur racine non objet, clé absente, clé supplémentaire, enum/type invalide, fence multiple ou autre langage ; chaque cas rend l’unique objet conservateur global, jamais un mélange partiel.

- [ ] **Step 42: Collecter puis observer le Red prompt/objet fermé**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
XML=$(mktemp /tmp/nexus-openrouter-classification-object.XXXXXX.xml)
OUT=$(mktemp /tmp/nexus-openrouter-classification-object.XXXXXX.out)
COLLECT=$(mktemp /tmp/nexus-openrouter-classification-object.XXXXXX.collect)
cd "$IMPL_ROOT"
NODES=(
  tests/test_openrouter_classification.py::test_classification_requests_200_completion_tokens
  tests/test_openrouter_classification.py::test_local_heuristic_preserves_existing_chunk_type_contract
  tests/test_openrouter_classification.py::test_remote_classification_accepts_exact_closed_object
  tests/test_openrouter_classification.py::test_remote_classification_rejects_invalid_closed_object_as_a_whole
)
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest --collect-only -q -p no:cacheprovider "${NODES[@]}" > "$COLLECT"
test "$(sed -n '/^tests\//p' "$COLLECT" | wc -l)" -eq 4
for node in "${NODES[@]}"; do rg -Fx -- "$node" "$COLLECT"; done
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider "${NODES[@]}" --junitxml "$XML" > "$OUT" 2>&1
RC=$?
set -e
test "$RC" -eq 1
! rg -F 'ERROR collecting' "$OUT"
rg -F 'nexus_external' "$OUT"
python3 - "$XML" "${NODES[@]##*::}" <<'PY'
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot(); suites = root.findall(".//testsuite") or [root]
got = {k: sum(int(s.get(k, "0")) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
expected = set(sys.argv[2:]); failed = {c.get("name", "") for c in root.findall(".//testcase") if c.find("failure") is not None}
assert got == {"tests": 4, "failures": len(expected), "errors": 0, "skipped": 0}, got
assert failed == expected, (failed, expected)
PY
```

Expected: quatre failures d’implémentation, objet fermé atomique et matrice interne sans multiplication des nodes.

- [ ] **Step 43: Écrire `test_remote_classification_rejects_boolean_difficulty`**

Tester `True` et `False` dans une boucle interne : bien que `bool` soit un sous-type d’`int`, les deux valeurs doivent rejeter l’objet entier.

- [ ] **Step 44: Écrire `test_invalid_remote_classification_returns_global_conservative_result`**

Fournir un objet partiellement plausible avec un seul champ invalide ; exiger l’objet conservateur complet, sans conserver aucun champ distant.

- [ ] **Step 45: Écrire `test_remote_metadata_cannot_override_trusted_record_fields`**

Boucler sur `source_id`, `doc_url`, `doc_hash`, `content_md`, `usage_policy` et `tier` ajoutés au JSON distant ; chacun invalide la réponse entière et les métadonnées source originales restent inchangées.

- [ ] **Step 46: Écrire `test_prompt_does_not_append_environment_or_provenance_metadata`**

Placer des sentinelles dans environnement et six métadonnées de confiance ; exiger qu’aucune n’apparaisse dans le prompt, qui ne contient que l’instruction fixe et `fragment[:3000]`.

- [ ] **Step 47: Collecter puis observer le Red conservateur/confiance**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
XML=$(mktemp /tmp/nexus-openrouter-classification-trust.XXXXXX.xml)
OUT=$(mktemp /tmp/nexus-openrouter-classification-trust.XXXXXX.out)
COLLECT=$(mktemp /tmp/nexus-openrouter-classification-trust.XXXXXX.collect)
cd "$IMPL_ROOT"
NODES=(
  tests/test_openrouter_classification.py::test_remote_classification_rejects_boolean_difficulty
  tests/test_openrouter_classification.py::test_invalid_remote_classification_returns_global_conservative_result
  tests/test_openrouter_classification.py::test_remote_metadata_cannot_override_trusted_record_fields
  tests/test_openrouter_classification.py::test_prompt_does_not_append_environment_or_provenance_metadata
)
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest --collect-only -q -p no:cacheprovider "${NODES[@]}" > "$COLLECT"
test "$(sed -n '/^tests\//p' "$COLLECT" | wc -l)" -eq 4
for node in "${NODES[@]}"; do rg -Fx -- "$node" "$COLLECT"; done
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider "${NODES[@]}" --junitxml "$XML" > "$OUT" 2>&1
RC=$?
set -e
test "$RC" -eq 1
! rg -F 'ERROR collecting' "$OUT"
rg -F 'nexus_external' "$OUT"
python3 - "$XML" "${NODES[@]##*::}" <<'PY'
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot(); suites = root.findall(".//testsuite") or [root]
got = {k: sum(int(s.get(k, "0")) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
expected = set(sys.argv[2:]); failed = {c.get("name", "") for c in root.findall(".//testcase") if c.find("failure") is not None}
assert got == {"tests": 4, "failures": len(expected), "errors": 0, "skipped": 0}, got
assert failed == expected, (failed, expected)
PY
```

Expected: quatre failures d’implémentation, exactement douze nodes classification au total et aucune fuite de métadonnée de confiance.

### Task 5: Écrire le contrat Red de la policy et des adaptateurs

**Files:**

- Create: `tests/test_external_provider_policy.py`
- Create: `Mathematiques/manuel-maths/tests/test_ingest_openrouter.py`
- Create: `NSI/tests/test_ingest_openrouter.py`

- [ ] **Step 48: Installer la barrière réseau autouse policy**

Créer `tests/test_external_provider_policy.py` par `apply_patch` absolu. La fixture autouse bloque `socket.socket.connect`, `socket.create_connection` et `urllib.request.urlopen`; le node `test_policy_rejects_unlisted_provider_transport` les invoque réellement avant sa mutation de surface. Le scanner pur du test reçoit toujours une liste explicite de chemins suivis ; il ne masque jamais un fichier absent.

- [ ] **Step 49: Écrire `test_policy_requires_every_canonical_active_surface`**

Définir littéralement la liste des sections 8.1 à 8.5, dont `manifest.csv`, `manifest_tooling.csv`, `inventory_report.md` et `duplicates_report.md`; pour chaque chemin, exiger `is_file()` puis `git ls-files --error-unmatch`. Le Red attendu est la surface future `nexus_external` absente.

- [ ] **Step 50: Écrire `test_policy_rejects_unlisted_provider_transport`**

Prouver d’abord les trois bloqueurs réseau autouse. Dans une boucle interne, créer sous `tmp_path` une surface active utilisant `requests`, `urllib`, `httpx` ou un SDK fournisseur et exiger le rejet ; sur le dépôt courant, exiger le rejet des transports LLM directs encore actifs.

- [ ] **Step 51: Écrire `test_policy_allows_only_openrouter_client_to_define_llm_endpoint`**

Exiger que le seul littéral `/chat/completions` et le seul endpoint LLM externe autorisés résident dans `nexus_external/openrouter_client.py`; l’absence actuelle de ce fichier et les appelants directs rendent le node rouge.

- [ ] **Step 52: Écrire `test_policy_preserves_non_llm_rag_transport_allowlist`**

Autoriser exactement les six scripts RAG de la spécification seulement lorsque leur destination provient de `RAG_API_BASE_URL`, `EMBEDDING_BASE_URL` ou `VECTOR_DB_URL` et qu’ils n’appellent ni chat, ni messages, ni completions. Ce node est un invariant historique vert.

- [ ] **Step 53: Collecter puis observer la première famille policy**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
XML=$(mktemp /tmp/nexus-openrouter-policy-transport.XXXXXX.xml)
OUT=$(mktemp /tmp/nexus-openrouter-policy-transport.XXXXXX.out)
COLLECT=$(mktemp /tmp/nexus-openrouter-policy-transport.XXXXXX.collect)
cd "$IMPL_ROOT"
NODES=(
  tests/test_external_provider_policy.py::test_policy_requires_every_canonical_active_surface
  tests/test_external_provider_policy.py::test_policy_rejects_unlisted_provider_transport
  tests/test_external_provider_policy.py::test_policy_allows_only_openrouter_client_to_define_llm_endpoint
  tests/test_external_provider_policy.py::test_policy_preserves_non_llm_rag_transport_allowlist
)
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest --collect-only -q -p no:cacheprovider "${NODES[@]}" > "$COLLECT"
test "$(sed -n '/^tests\//p' "$COLLECT" | wc -l)" -eq 4
for node in "${NODES[@]}"; do rg -Fx -- "$node" "$COLLECT"; done
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider "${NODES[@]}" --junitxml "$XML" > "$OUT" 2>&1
RC=$?
set -e
test "$RC" -eq 1
! rg -F 'ERROR collecting' "$OUT"
rg -e 'nexus_external|transport|endpoint' "$OUT"
python3 - "$XML" <<'PY'
import xml.etree.ElementTree as ET
import sys
root = ET.parse(sys.argv[1]).getroot(); suites = root.findall(".//testsuite") or [root]
expected = {"test_policy_requires_every_canonical_active_surface", "test_policy_rejects_unlisted_provider_transport", "test_policy_allows_only_openrouter_client_to_define_llm_endpoint"}
failed = {c.get("name", "") for c in root.findall(".//testcase") if c.find("failure") is not None}
got = {k: sum(int(s.get(k, "0")) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
assert got == {"tests": 4, "failures": len(expected), "errors": 0, "skipped": 0}, got
assert failed == expected, (failed, expected)
PY
```

Expected: trois failures littérales et l’invariant RAG vert ; le node transport a prouvé la fixture réseau.

- [ ] **Step 54: Écrire `test_policy_rejects_chutes_in_active_authority`**

Scanner seulement les autorités/guides actifs de la spécification, prouver leur présence suivie et refuser le mot Chutes hors contexte explicitement historique ; les autorités actuelles rendent ce node rouge.

- [ ] **Step 55: Écrire `test_policy_ignores_protected_historical_chutes_artifacts`**

Passer au scanner une copie `tmp_path` d’un audit historique contenant Chutes et exiger qu’il reste ignoré et byte-stable. Ce node est un invariant vert et ne réécrit aucune preuve.

- [ ] **Step 56: Écrire `test_policy_rejects_model_catalog_endpoint_in_automation`**

Refuser `/api/v1/models` et tout appel catalogue dans scripts/tests automatisés actifs ; une mutation `tmp_path` doit être détectée par le scanner pur. Le dépôt courant ne possède aucun appel catalogue actif : ce node est donc un invariant vert dès le jalon Red, indépendamment du ménage des autorités Chutes.

- [ ] **Step 57: Écrire `test_policy_rejects_new_nsi_ingest_make_target`**

Exiger l’absence de cible `ingest` ajoutée au Makefile NSI et la conservation de la commande contractuelle `python3 scripts/ingest.py`. Ce node est un invariant vert.

- [ ] **Step 58: Collecter puis observer autorités/historique policy**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
XML=$(mktemp /tmp/nexus-openrouter-policy-authority.XXXXXX.xml)
OUT=$(mktemp /tmp/nexus-openrouter-policy-authority.XXXXXX.out)
COLLECT=$(mktemp /tmp/nexus-openrouter-policy-authority.XXXXXX.collect)
cd "$IMPL_ROOT"
NODES=(
  tests/test_external_provider_policy.py::test_policy_rejects_chutes_in_active_authority
  tests/test_external_provider_policy.py::test_policy_ignores_protected_historical_chutes_artifacts
  tests/test_external_provider_policy.py::test_policy_rejects_model_catalog_endpoint_in_automation
  tests/test_external_provider_policy.py::test_policy_rejects_new_nsi_ingest_make_target
)
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest --collect-only -q -p no:cacheprovider "${NODES[@]}" > "$COLLECT"
test "$(sed -n '/^tests\//p' "$COLLECT" | wc -l)" -eq 4
for node in "${NODES[@]}"; do rg -Fx -- "$node" "$COLLECT"; done
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider "${NODES[@]}" --junitxml "$XML" > "$OUT" 2>&1
RC=$?
set -e
test "$RC" -eq 1
! rg -F 'ERROR collecting' "$OUT"
rg -e 'Chutes|api/v1/models|catalog' "$OUT"
python3 - "$XML" <<'PY'
import xml.etree.ElementTree as ET
import sys
root = ET.parse(sys.argv[1]).getroot(); suites = root.findall(".//testsuite") or [root]
expected = {"test_policy_rejects_chutes_in_active_authority"}
failed = {c.get("name", "") for c in root.findall(".//testcase") if c.find("failure") is not None}
got = {k: sum(int(s.get(k, "0")) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
assert got == {"tests": 4, "failures": len(expected), "errors": 0, "skipped": 0}, got
assert failed == expected, (failed, expected)
PY
```

Expected: une failure active Chutes et trois invariants verts (historique, absence de catalogue et commande NSI).

- [ ] **Step 59: Écrire `test_targeted_surfaces_exist_before_negative_scans`**

Pour chaque appelant, configuration, autorité, guide et sortie générée canonique, exiger fichier suivi et lisible avant toute recherche négative. Ce node est vert sur la base et rend impossible une réussite par chemin manquant.

- [ ] **Step 60: Écrire `test_policy_rejects_anthropic_in_active_callers`**

Refuser import SDK, endpoint Messages, `ANTHROPIC_API_KEY` et modèle direct dans les quatre appelants actifs ; les scripts actuels rendent ce node rouge. Les preuves historiques protégées sont exclues par chemin, jamais par suppression de texte.

- [ ] **Step 61: Écrire `test_policy_rejects_local_llm_configuration_in_active_surfaces`**

Refuser `LOCAL_LLM_*` dans configurations, appelants et guides actifs ; tolérer ces littéraux seulement dans le tableau de rejet futur de `check_rag_config.py` et dans les tests qui prouvent ce rejet. La configuration actuelle rend le node rouge.

- [ ] **Step 62: Écrire `test_ci_no_deps_requirements_close_httpx_runtime_dependencies`**

Parser statiquement `requirements-ci-audit.txt`; exiger une occurrence exacte de `httpx==0.28.1`, `anyio==4.9.0`, `certifi==2026.7.22`, `httpcore==1.0.9`, `h11==0.16.0`, `idna==3.6`, `sniffio==1.3.1`, conserver l’unique `typing_extensions==4.15.0` et refuser tout SDK fournisseur. Ne consulter ni distributions installées ni réseau.

- [ ] **Step 63: Collecter puis observer fournisseurs/dépendances policy**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
XML=$(mktemp /tmp/nexus-openrouter-policy-deps.XXXXXX.xml)
OUT=$(mktemp /tmp/nexus-openrouter-policy-deps.XXXXXX.out)
COLLECT=$(mktemp /tmp/nexus-openrouter-policy-deps.XXXXXX.collect)
cd "$IMPL_ROOT"
NODES=(
  tests/test_external_provider_policy.py::test_targeted_surfaces_exist_before_negative_scans
  tests/test_external_provider_policy.py::test_policy_rejects_anthropic_in_active_callers
  tests/test_external_provider_policy.py::test_policy_rejects_local_llm_configuration_in_active_surfaces
  tests/test_external_provider_policy.py::test_ci_no_deps_requirements_close_httpx_runtime_dependencies
)
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest --collect-only -q -p no:cacheprovider "${NODES[@]}" > "$COLLECT"
test "$(sed -n '/^tests\//p' "$COLLECT" | wc -l)" -eq 4
for node in "${NODES[@]}"; do rg -Fx -- "$node" "$COLLECT"; done
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider "${NODES[@]}" --junitxml "$XML" > "$OUT" 2>&1
RC=$?
set -e
test "$RC" -eq 1
! rg -F 'ERROR collecting' "$OUT"
rg -e 'ANTHROPIC|LOCAL_LLM|httpx|anyio|certifi|httpcore|h11|idna|sniffio' "$OUT"
python3 - "$XML" <<'PY'
import xml.etree.ElementTree as ET
import sys
root = ET.parse(sys.argv[1]).getroot(); suites = root.findall(".//testsuite") or [root]
expected = {"test_policy_rejects_anthropic_in_active_callers", "test_policy_rejects_local_llm_configuration_in_active_surfaces", "test_ci_no_deps_requirements_close_httpx_runtime_dependencies"}
failed = {c.get("name", "") for c in root.findall(".//testcase") if c.find("failure") is not None}
got = {k: sum(int(s.get(k, "0")) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
assert got == {"tests": 4, "failures": len(expected), "errors": 0, "skipped": 0}, got
assert failed == expected, (failed, expected)
PY
```

Expected: trois failures actives, le node de présence vert et exactement douze nodes policy au total.

## Chunk 4: Red des deux adaptateurs d’ingestion

- [ ] **Step 64: Installer la fixture réseau autouse Mathématiques**

Créer par `apply_patch` `Mathematiques/manuel-maths/tests/test_ingest_openrouter.py`. Tous les imports futurs sont dans les corps. La fixture bloque les trois primitives ; un `sitecustomize.py` temporaire écrit `sitecustomize-loaded` dans `NEXUS_NETWORK_GUARD_MARKER`, bloque les mêmes primitives dans le sous-processus et n’est injecté via `PYTHONPATH` que pour ce sous-processus.

- [ ] **Step 65: Écrire `test_math_ingest_classify_delegates_to_shared_classifier`**

Injecter le classifieur partagé futur, appeler `classify()` et exiger un appel unique avec le fragment exact ainsi que le retour inchangé de l’objet fermé.

- [ ] **Step 66: Écrire `test_math_ingest_preserves_trusted_metadata_against_hostile_classifier`**

Faire retourner au double les six clés de confiance hostiles et exiger que `ingest_source()` conserve les valeurs registre/manifest originales ; aucune clé distante ne les écrase.

- [ ] **Step 67: Écrire `test_math_ingest_command_runs_without_source_key_or_network`**

Lancer réellement `make ingest` depuis le CWD Mathématiques absolu, avec les quatre variables retirées et le `sitecustomize`; exiger code 0, marker exact et zéro tentative réseau. Ce comportement de commande est un invariant vert avant migration.

- [ ] **Step 68: Écrire `test_math_network_guard_mutation_is_effective`**

Appeler réellement les trois primitives dans une boucle interne sous `pytest.raises(AssertionError)`; ce node vert prouve la fixture autouse du module.

- [ ] **Step 69: Collecter puis observer la première famille Mathématiques**

```bash
set -euo pipefail
MATH_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/Mathematiques/manuel-maths
XML=$(mktemp /tmp/nexus-openrouter-math-functional.XXXXXX.xml)
OUT=$(mktemp /tmp/nexus-openrouter-math-functional.XXXXXX.out)
COLLECT=$(mktemp /tmp/nexus-openrouter-math-functional.XXXXXX.collect)
cd "$MATH_ROOT"
NODES=(
  tests/test_ingest_openrouter.py::test_math_ingest_classify_delegates_to_shared_classifier
  tests/test_ingest_openrouter.py::test_math_ingest_preserves_trusted_metadata_against_hostile_classifier
  tests/test_ingest_openrouter.py::test_math_ingest_command_runs_without_source_key_or_network
  tests/test_ingest_openrouter.py::test_math_network_guard_mutation_is_effective
)
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest --collect-only -q -p no:cacheprovider "${NODES[@]}" > "$COLLECT"
test "$(sed -n '/^tests\//p' "$COLLECT" | wc -l)" -eq 4
for node in "${NODES[@]}"; do rg -Fx -- "$node" "$COLLECT"; done
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider "${NODES[@]}" --junitxml "$XML" > "$OUT" 2>&1
RC=$?
set -e
test "$RC" -eq 1
! rg -F 'ERROR collecting' "$OUT"
python3 - "$XML" <<'PY'
import xml.etree.ElementTree as ET
import sys
root = ET.parse(sys.argv[1]).getroot(); suites = root.findall(".//testsuite") or [root]
expected = {"test_math_ingest_classify_delegates_to_shared_classifier", "test_math_ingest_preserves_trusted_metadata_against_hostile_classifier"}
failed = {c.get("name", "") for c in root.findall(".//testcase") if c.find("failure") is not None}
got = {k: sum(int(s.get(k, "0")) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
assert got == {"tests": 4, "failures": len(expected), "errors": 0, "skipped": 0}, got
assert failed == expected, (failed, expected)
PY
```

Expected: deux failures de délégation/confiance et deux invariants verts, dont la vraie commande protégée par marker.

- [ ] **Step 70: Écrire `test_math_ingest_discovers_current_checkout_from_unrelated_cwd`**

Changer vers `tmp_path`, charger l’appelant et exiger que le paquet résolu soit exactement `<CHECKOUT_ROOT>/nexus_external`, découvert depuis `__file__`.

- [ ] **Step 71: Écrire `test_math_ingest_prioritizes_current_checkout_over_shadow_package`**

Créer un faux paquet dans un répertoire prioritaire et exiger que l’adaptateur choisisse malgré tout le paquet du checkout courant.

- [ ] **Step 72: Écrire `test_math_ingest_rejects_nexus_external_loaded_outside_checkout`**

Précharger un module empoisonné dans `sys.modules`; exiger une erreur explicite avant classifieur/transport plutôt qu’une réutilisation silencieuse.

- [ ] **Step 73: Écrire `test_math_no_source_command_does_not_import_extraction_backends`**

Bloquer `fitz` et `trafilatura` via `builtins.__import__`, exécuter le chemin sans source et exiger code 0 : les backends deviennent paresseux au Green.

- [ ] **Step 74: Collecter puis observer provenance/extraction Mathématiques**

```bash
set -euo pipefail
MATH_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/Mathematiques/manuel-maths
XML=$(mktemp /tmp/nexus-openrouter-math-provenance.XXXXXX.xml)
OUT=$(mktemp /tmp/nexus-openrouter-math-provenance.XXXXXX.out)
COLLECT=$(mktemp /tmp/nexus-openrouter-math-provenance.XXXXXX.collect)
cd "$MATH_ROOT"
NODES=(
  tests/test_ingest_openrouter.py::test_math_ingest_discovers_current_checkout_from_unrelated_cwd
  tests/test_ingest_openrouter.py::test_math_ingest_prioritizes_current_checkout_over_shadow_package
  tests/test_ingest_openrouter.py::test_math_ingest_rejects_nexus_external_loaded_outside_checkout
  tests/test_ingest_openrouter.py::test_math_no_source_command_does_not_import_extraction_backends
)
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest --collect-only -q -p no:cacheprovider "${NODES[@]}" > "$COLLECT"
test "$(sed -n '/^tests\//p' "$COLLECT" | wc -l)" -eq 4
for node in "${NODES[@]}"; do rg -Fx -- "$node" "$COLLECT"; done
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider "${NODES[@]}" --junitxml "$XML" > "$OUT" 2>&1
RC=$?
set -e
test "$RC" -eq 1
! rg -F 'ERROR collecting' "$OUT"
rg -e 'nexus_external|fitz|trafilatura' "$OUT"
python3 - "$XML" "${NODES[@]##*::}" <<'PY'
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot(); suites = root.findall(".//testsuite") or [root]
expected = set(sys.argv[2:]); failed = {c.get("name", "") for c in root.findall(".//testcase") if c.find("failure") is not None}
got = {k: sum(int(s.get(k, "0")) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
assert got == {"tests": 4, "failures": len(expected), "errors": 0, "skipped": 0}, got
assert failed == expected, (failed, expected)
PY
```

Expected: quatre failures littérales de provenance/lazy import ; exactement huit nodes Mathématiques au total.

- [ ] **Step 75: Installer la fixture réseau autouse NSI**

Créer par `apply_patch` `NSI/tests/test_ingest_openrouter.py`, imports futurs uniquement dans les corps. Réutiliser le même contrat `sitecustomize`/marker limité au sous-processus ; la commande reste `python3 scripts/ingest.py` depuis `NSI/` et aucune cible Make n’est créée.

- [ ] **Step 76: Écrire `test_nsi_ingest_classify_delegates_to_shared_classifier`**

Injecter le classifieur futur et exiger un appel unique avec le fragment exact et le retour fermé inchangé.

- [ ] **Step 77: Écrire `test_nsi_ingest_preserves_trusted_metadata_against_hostile_classifier`**

Faire retourner les six clés de confiance hostiles et exiger les valeurs registre/manifest originales dans le record final.

- [ ] **Step 78: Écrire `test_nsi_ingest_command_runs_without_source_key_or_network`**

Lancer réellement `python3 scripts/ingest.py` depuis le CWD NSI absolu, quatre variables retirées, `sitecustomize` injecté ; exiger code 0 et marker exact. Ce node est un invariant vert.

- [ ] **Step 79: Écrire `test_nsi_network_guard_mutation_is_effective`**

Appeler les trois primitives bloquées dans une boucle interne sous `pytest.raises(AssertionError)` ; ce node vert prouve la fixture du module.

- [ ] **Step 80: Collecter puis observer la première famille NSI**

```bash
set -euo pipefail
NSI_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI
XML=$(mktemp /tmp/nexus-openrouter-nsi-functional.XXXXXX.xml)
OUT=$(mktemp /tmp/nexus-openrouter-nsi-functional.XXXXXX.out)
COLLECT=$(mktemp /tmp/nexus-openrouter-nsi-functional.XXXXXX.collect)
cd "$NSI_ROOT"
NODES=(
  tests/test_ingest_openrouter.py::test_nsi_ingest_classify_delegates_to_shared_classifier
  tests/test_ingest_openrouter.py::test_nsi_ingest_preserves_trusted_metadata_against_hostile_classifier
  tests/test_ingest_openrouter.py::test_nsi_ingest_command_runs_without_source_key_or_network
  tests/test_ingest_openrouter.py::test_nsi_network_guard_mutation_is_effective
)
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest --collect-only -q -p no:cacheprovider "${NODES[@]}" > "$COLLECT"
test "$(sed -n '/^tests\//p' "$COLLECT" | wc -l)" -eq 4
for node in "${NODES[@]}"; do rg -Fx -- "$node" "$COLLECT"; done
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider "${NODES[@]}" --junitxml "$XML" > "$OUT" 2>&1
RC=$?
set -e
test "$RC" -eq 1
! rg -F 'ERROR collecting' "$OUT"
python3 - "$XML" <<'PY'
import xml.etree.ElementTree as ET
import sys
root = ET.parse(sys.argv[1]).getroot(); suites = root.findall(".//testsuite") or [root]
expected = {"test_nsi_ingest_classify_delegates_to_shared_classifier", "test_nsi_ingest_preserves_trusted_metadata_against_hostile_classifier"}
failed = {c.get("name", "") for c in root.findall(".//testcase") if c.find("failure") is not None}
got = {k: sum(int(s.get(k, "0")) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
assert got == {"tests": 4, "failures": len(expected), "errors": 0, "skipped": 0}, got
assert failed == expected, (failed, expected)
PY
```

Expected: deux failures de délégation/confiance et deux invariants verts, dont la vraie commande NSI protégée.

- [ ] **Step 81: Écrire `test_nsi_ingest_discovers_current_checkout_from_unrelated_cwd`**

Depuis `tmp_path`, exiger que le paquet résolu soit exactement celui du checkout découvert depuis `__file__`.

- [ ] **Step 82: Écrire `test_nsi_ingest_prioritizes_current_checkout_over_shadow_package`**

Créer un paquet d’ombre prioritaire et exiger la résolution du checkout courant.

- [ ] **Step 83: Écrire `test_nsi_ingest_rejects_nexus_external_loaded_outside_checkout`**

Précharger un module empoisonné et exiger l’échec explicite avant transport.

- [ ] **Step 84: Écrire `test_nsi_no_source_command_does_not_import_extraction_backends`**

Bloquer `fitz`/`trafilatura` dans `builtins.__import__`, exécuter le chemin sans source et exiger code 0 après imports rendus paresseux.

- [ ] **Step 85: Collecter puis observer provenance/extraction NSI**

```bash
set -euo pipefail
NSI_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI
XML=$(mktemp /tmp/nexus-openrouter-nsi-provenance.XXXXXX.xml)
OUT=$(mktemp /tmp/nexus-openrouter-nsi-provenance.XXXXXX.out)
COLLECT=$(mktemp /tmp/nexus-openrouter-nsi-provenance.XXXXXX.collect)
cd "$NSI_ROOT"
NODES=(
  tests/test_ingest_openrouter.py::test_nsi_ingest_discovers_current_checkout_from_unrelated_cwd
  tests/test_ingest_openrouter.py::test_nsi_ingest_prioritizes_current_checkout_over_shadow_package
  tests/test_ingest_openrouter.py::test_nsi_ingest_rejects_nexus_external_loaded_outside_checkout
  tests/test_ingest_openrouter.py::test_nsi_no_source_command_does_not_import_extraction_backends
)
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest --collect-only -q -p no:cacheprovider "${NODES[@]}" > "$COLLECT"
test "$(sed -n '/^tests\//p' "$COLLECT" | wc -l)" -eq 4
for node in "${NODES[@]}"; do rg -Fx -- "$node" "$COLLECT"; done
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider "${NODES[@]}" --junitxml "$XML" > "$OUT" 2>&1
RC=$?
set -e
test "$RC" -eq 1
! rg -F 'ERROR collecting' "$OUT"
rg -e 'nexus_external|fitz|trafilatura' "$OUT"
python3 - "$XML" "${NODES[@]##*::}" <<'PY'
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot(); suites = root.findall(".//testsuite") or [root]
expected = set(sys.argv[2:]); failed = {c.get("name", "") for c in root.findall(".//testcase") if c.find("failure") is not None}
got = {k: sum(int(s.get(k, "0")) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
assert got == {"tests": 4, "failures": len(expected), "errors": 0, "skipped": 0}, got
assert failed == expected, (failed, expected)
PY
```

Expected: quatre failures littérales et exactement huit nodes NSI au total.

- [ ] **Step 86: Vérifier les collectes isolées Mathématiques, NSI et policy**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
python3 -m pytest --collect-only -q -p no:cacheprovider tests/test_external_provider_policy.py
cd "$IMPL_ROOT/Mathematiques/manuel-maths"
python3 -m pytest --collect-only -q -p no:cacheprovider tests/test_ingest_openrouter.py
cd "$IMPL_ROOT/NSI"
python3 -m pytest --collect-only -q -p no:cacheprovider tests/test_ingest_openrouter.py
```

Expected: trois processus de collecte verts : exactement 12 policy, 8 Mathématiques et 8 NSI ; aucune paramétrisation, zéro skip et zéro import futur à la collecte.

- [ ] **Step 87: Observer séparément les Reds policy, Mathématiques et NSI**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-baseline-pointer.*' ! -name '*.complete' -print)
test "${#POINTERS[@]}" -eq 1
POINTER=${POINTERS[0]}
test -O "$POINTER"; test ! -L "$POINTER"; test "$(stat -c '%a' "$POINTER")" = 600
EVIDENCE_ROOT=$(cat "$POINTER")
case "$EVIDENCE_ROOT" in /tmp/nexus-openrouter-baseline.*) ;; *) exit 1 ;; esac
test -d "$EVIDENCE_ROOT"
cd "$IMPL_ROOT"
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
python3 -m pytest -q -p no:cacheprovider tests/test_external_provider_policy.py \
  --junitxml "$EVIDENCE_ROOT/red-policy.xml" \
  > "$EVIDENCE_ROOT/red-policy.out" 2>&1
RC_POLICY=$?
cd "$IMPL_ROOT/Mathematiques/manuel-maths"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
python3 -m pytest -q -p no:cacheprovider tests/test_ingest_openrouter.py \
  --junitxml "$EVIDENCE_ROOT/red-math.xml" \
  > "$EVIDENCE_ROOT/red-math.out" 2>&1
RC_MATH=$?
cd "$IMPL_ROOT/NSI"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
python3 -m pytest -q -p no:cacheprovider tests/test_ingest_openrouter.py \
  --junitxml "$EVIDENCE_ROOT/red-nsi.xml" \
  > "$EVIDENCE_ROOT/red-nsi.out" 2>&1
RC_NSI=$?
set -e
test "$RC_POLICY" -eq 1
test "$RC_MATH" -eq 1
test "$RC_NSI" -eq 1
! rg -F 'ERROR collecting' \
  "$EVIDENCE_ROOT/red-policy.out" \
  "$EVIDENCE_ROOT/red-math.out" \
  "$EVIDENCE_ROOT/red-nsi.out"
python3 - "$EVIDENCE_ROOT" <<'PY'
import sys, xml.etree.ElementTree as ET
from pathlib import Path
root = Path(sys.argv[1])
expected = {
    "policy": {"tests": 12, "failures": 7, "errors": 0, "skipped": 0},
    "math": {"tests": 8, "failures": 6, "errors": 0, "skipped": 0},
    "nsi": {"tests": 8, "failures": 6, "errors": 0, "skipped": 0},
}
for label, wanted in expected.items():
    r = ET.parse(root / f"red-{label}.xml").getroot()
    s = r.findall(".//testsuite") or [r]
    got = {k: sum(int(x.get(k, "0")) for x in s) for k in wanted}
    assert got == wanted, (label, got, wanted)
PY
```

Expected: policy rouge sur les autorités/configurations actives, adaptateurs rouges sur l’absence de délégation/provenance. Toute erreur de collecte est `HARD STOP`.

## Chunk 5: Red du corpus et commit tests-only

### Task 6: Écrire le contrat Red séparé du corpus NSI

**Files:**

- Create: `NSI/corpus_nsi/tests/test_openrouter_judges.py`
- Modify: `NSI/corpus_nsi/tests/test_manifest_separation.py`
- Modify: `NSI/corpus_nsi/tests/test_rag_governance_and_indexes.py`
- Modify: `NSI/corpus_nsi/tests/test_secret_guard.py`
- Modify: `NSI/corpus_nsi/tests/test_substance_judge_pipeline.py`
- Modify: `NSI/corpus_nsi/tests/test_substance_hardened.py`
- Modify: `NSI/corpus_nsi/tests/test_judge_collection_barriers.py`
- Modify: `NSI/corpus_nsi/tests/test_policy_checker_ast.py`

- [ ] **Step 1: Distinguer `CORPUS_ROOT` et `CHECKOUT_ROOT` dans les tests**

Dans `/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi/tests/test_openrouter_judges.py`, définir :

```python
CORPUS_ROOT = Path(__file__).resolve().parents[1]
CHECKOUT_ROOT = Path(__file__).resolve().parents[3]
assert (CORPUS_ROOT / "AGENTS.md").is_file()
assert (CHECKOUT_ROOT / ".git").exists()
```

Les imports de `scripts.judge_campaign`, `scripts.substance_judge` et `nexus_external` surviennent dans les tests. Les tests ne changent jamais `ROOT` du corpus en racine du checkout.

- [ ] **Step 2: Écrire `test_campaign_delegates_to_shared_openrouter_client`**

Importer l’appelant dans le corps, injecter un double du client et exiger un appel unique avec les messages exacts.

- [ ] **Step 3: Écrire `test_campaign_reads_missing_openrouter_values_from_resolved_rag_env`**

Créer un `.env.rag` sous `tmp_path` et exiger la résolution champ par champ des seules valeurs absentes.

- [ ] **Step 4: Écrire `test_campaign_does_not_read_generic_dotenv`**

Placer des sentinelles uniquement dans `.env` et exiger qu’elles ne soient jamais lues.

- [ ] **Step 5: Écrire `test_campaign_rejects_key_without_model_before_transport`**

Fournir une clé avec modèle blanc et un transport qui lève s’il est appelé ; exiger l’erreur avant transport.

- [ ] **Step 6: Observer le Red de configuration campagne**

Exécuter ces quatre IDs dans un bloc Bash autonome : `set -euo pipefail`, CWD corpus absolu, quatre `env -u`, capture `rc=1` et JUnit exact `tests=4`, `failures=4`, `errors=0`, `skipped=0`, avec égalité de l’ensemble des nodeids échoués.

- [ ] **Step 7: Écrire `test_campaign_business_retry_count_is_bounded`**

Injecter des erreurs retentables et exiger le nombre total et les délais exacts.

- [ ] **Step 8: Écrire `test_campaign_records_requested_openrouter_model`**

Exiger que le modèle demandé soit celui consigné dans le verdict.

- [ ] **Step 9: Écrire `test_campaign_records_each_billed_retry_generation_before_verdict_validation`**

Retourner deux complétions aux générations/coûts distincts, la première au verdict invalide et la seconde valide ; exiger les deux écritures dans l’ordre avant validation/retry.

- [ ] **Step 10: Observer le Red retry/modèle/facturation**

Exécuter ces trois IDs dans un bloc Bash autonome avec quatre `env -u` ; exiger `rc=1`, JUnit `3/3/0/0` et l’ensemble exact des nodeids échoués.

- [ ] **Step 11: Écrire `test_usage_v2_copies_completion_accounting_exactly`**

Muter coût et compteurs et exiger leur copie exacte, sans formule. Le test exige l'ensemble fermé des clés de succès `schema_version`, `provider`, `cap`, `seq`, `attempt`, `judged_at`, `model`, `generation_id`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `cached_tokens`, `cache_write_tokens`, `cost_usd`, avec `schema_version == 2` et `provider == "openrouter"`.

- [ ] **Step 12: Écrire `test_usage_upsert_replaces_same_generation_only`**

Inclure un doublon de génération et exiger une seule entrée après remplacement.

- [ ] **Step 13: Écrire `test_usage_upsert_preserves_v1_deeply_and_in_order`**

Utiliser une copie `tmp_path` et comparer profondément valeurs et ordre.

- [ ] **Step 14: Écrire `test_usage_upsert_preserves_other_v2_generations_for_same_capacity`**

Exiger que les autres générations d’une même capacité restent présentes.

- [ ] **Step 15: Observer le Red du journal v2**

Exécuter ces quatre IDs dans un bloc Bash autonome ; exiger `rc=1`, JUnit `4/4/0/0` et l’ensemble exact des nodeids.

- [ ] **Step 16: Écrire `test_usage_logging_contains_no_local_cost_formula`**

Scanner l’AST et muter les tokens pour interdire tout calcul tarifaire.

- [ ] **Step 17: Écrire `test_failed_usage_entry_invents_no_accounting`**

Injecter une erreur sans complétion et exiger exactement les clés `schema_version`, `provider`, `cap`, `seq`, `attempt`, `judged_at`, `model`, `error_category`, avec `schema_version == 2`, `provider == "openrouter"` et absence de génération, tokens et coût.

- [ ] **Step 18: Écrire `test_run_totals_sum_only_current_successful_v2_entries`**

Construire d'une part un historique fusionné contenant v1, anciennes générations v2 et échec, et d'autre part une liste en mémoire `current_entries` contenant uniquement les succès v2 produits pendant l'invocation courante. Appeler `current_run_totals(current_entries)` et exiger la somme de ces succès seulement ; muter l'historique séparé et prouver qu'il n'entre jamais dans l'argument. Aucun champ `run_id` n'est ajouté au journal.

- [ ] **Step 19: Observer le Red de comptabilité**

Exécuter ces trois IDs dans un bloc autonome ; exiger `rc=1`, JUnit `3/3/0/0` et les nodeids exacts.

- [ ] **Step 20: Écrire `test_substance_llm_delegates_to_shared_openrouter_client`**

Exiger la délégation du seul transport LLM, sans modifier `_http_json()`.

- [ ] **Step 21: Écrire `test_substance_without_key_returns_conservative_result_without_transport`**

Caractérisation verte : sans clé, exiger `taught=False`, citation vide et zéro transport.

- [ ] **Step 22: Écrire `test_substance_rejects_key_without_model_before_transport`**

Fournir une clé et un modèle blanc ; exiger l’erreur avant le double transport.

- [ ] **Step 23: Écrire `test_substance_sends_exact_bounded_prompt_and_limit`**

Préserver capacité, rôle et `section_text[:800]`; exiger le modèle exact et `max_completion_tokens=800`.

- [ ] **Step 24: Écrire `test_substance_accepts_only_exact_closed_json_object`**

Accepter JSON nu ou un seul fence `json`; refuser clés manquantes/supplémentaires et types invalides.

- [ ] **Step 25: Observer le Red substance**

Exécuter les cinq IDs dans un bloc Bash autonome avec quatre `env -u`; exiger exactement quatre failures (tous sauf le mode sans clé), zéro error/skip et l’ensemble littéral des quatre nodeids.

- [ ] **Step 26: Écrire `test_substance_rag_keeps_dedicated_http_transport`**

Invariant vert : exiger l’URL/Bearer RAG existants et jamais le client OpenRouter.

- [ ] **Step 27: Écrire `test_substance_has_no_configurable_llm_endpoint`**

Exiger la disparition des `LOCAL_LLM_*` et de la concaténation d’URL de chat.

- [ ] **Step 28: Écrire `test_substance_remote_error_is_sanitized_and_never_promotes`**

Injecter des sentinelles dans une erreur et exiger un verdict conservateur expurgé.

- [ ] **Step 29: Observer la séparation RAG/LLM**

Exécuter ces trois IDs ; exiger l’invariant RAG vert, les deux autres rouges, zéro error/skip.

- [ ] **Step 30: Écrire `test_run_substance_judge_imports_no_external_client`**

Invariant vert : inspecter l’AST et exiger l’absence de client HTTP.

- [ ] **Step 31: Écrire `test_run_substance_judge_uses_honest_deterministic_model`**

Exiger le défaut `deterministic-prejudge` et aucune mention fournisseur active.

- [ ] **Step 32: Observer le Red du pré-jugement**

Exécuter ces deux IDs ; exiger le premier vert, le second rouge, zéro error/skip.

- [ ] **Step 33: Écrire `test_campaign_discovers_current_checkout_from_unrelated_cwd`**

Changer de CWD et exiger le paquet du checkout découvert depuis `__file__`.

- [ ] **Step 34: Écrire `test_substance_discovers_current_checkout_from_unrelated_cwd`**

Répéter la preuve tout en gardant `CORPUS_ROOT` séparé de `CHECKOUT_ROOT`.

- [ ] **Step 35: Écrire `test_corpus_callers_reject_shadowed_external_package`**

Précharger un paquet homonyme extérieur et exiger l’échec avant transport.

- [ ] **Step 36: Observer le Red de provenance corpus**

Exécuter ces trois IDs dans un bloc autonome ; exiger trois failures exactes, zéro error/skip. À ce stade les 27 noms sont présents.

- [ ] **Step 37: Adapter exactement la gouvernance RAG**

Modifier par `apply_patch` le seul chemin absolu `tests/test_rag_governance_and_indexes.py`. Dans `test_rag_env_example_uses_internal_corpus_without_real_secret`, exiger `OPENROUTER_API_KEY=` et `OPENROUTER_MODEL=` vides une fois, refuser les quatre `LOCAL_LLM_*`, et comparer byte pour byte les valeurs RAG/embedding/vector attendues. Exécuter ce node seul sous les quatre `env -u`, avec JUnit : Red exact `tests=1, failures=1, errors=0, skipped=0`.

- [ ] **Step 38: Adapter exactement le secret guard**

Modifier par `apply_patch` le seul chemin absolu `tests/test_secret_guard.py`. Dans `test_detects_token_like_assignments_without_flagging_examples`, ajouter une vraie clé OpenRouter sentinelle qui doit être détectée et les trois exemples `.env*` suivis dont les assignments vides doivent rester acceptés. Exécuter le node seul sous les quatre `env -u`, JUnit exact `tests=1, failures=1, errors=0, skipped=0` sur les exemples encore anciens.

- [ ] **Step 39: Adapter exactement le pipeline substance**

Modifier par `apply_patch` le seul chemin absolu `tests/test_substance_judge_pipeline.py`. `test_judge_never_promotes_to_validated_pedagogy` injecte l’objet conservateur sans clé et exige statut non promu ; `test_network_calls_are_blocked_by_test_fixture` invoque réellement les trois primitives bloquées par le `conftest.py` corpus. Ces deux propriétés existent déjà indépendamment de la migration fournisseur : exécuter les deux nodes et exiger JUnit exact `tests=2, failures=0, errors=0, skipped=0`.

- [ ] **Step 40: Adapter exactement le veto hardened**

Modifier par `apply_patch` le seul chemin absolu `tests/test_substance_hardened.py`. `TestSubstanceHardened::test_api_error_preserves_existing_valid_verdict` injecte une erreur OpenRouter expurgée et vérifie égalité profonde du verdict suivi avant/après. Exécuter ce node sous les quatre `env -u`; JUnit exact `tests=1, failures=1, errors=0, skipped=0` avant migration.

- [ ] **Step 41: Adapter exactement la barrière de collection**

Modifier par `apply_patch` le seul chemin absolu `tests/test_judge_collection_barriers.py`. `test_search_rag_with_doc_type_filter_excludes_non_matching` capture l’URL et exige qu’elle dérive exclusivement de `RAG_API_BASE_URL`, jamais de l’endpoint OpenRouter ; conserver ses assertions de filtrage. Exécuter ce node : JUnit exact `tests=1, failures=0, errors=0, skipped=0`, invariant vert explicitement conservé dans le jalon Red.

- [ ] **Step 42: Adapter exactement le checker AST**

Modifier par `apply_patch` le seul chemin absolu `tests/test_policy_checker_ast.py`. `test_valid_judge_passes` construit un appelant utilisant les deux variables OpenRouter et un transport partagé ; `test_real_judge_passes` vérifie le fichier réel encore rouge. Toutes les mutations historiques restent inchangées. Exécuter ces deux nodes : JUnit exact `tests=2, failures=1, errors=0, skipped=0`.

- [ ] **Step 43: Fermer les trois tests manifest sans changer leurs noms**

Modifier par `apply_patch` le seul chemin absolu `tests/test_manifest_separation.py` et conserver exactement ses trois noms. `test_pedagogical_manifest_contains_only_pedagogical_content` exige simultanément que `tests/test_openrouter_judges.py` soit absent de `manifest.csv` et présent dans `manifest_tooling.csv` : il échoue sur le tooling périmé. `test_manifests_cover_all_inventoried_resources` compare `git ls-files` aux deux manifests : il reste vert avant staging puisque le nouveau test n'est pas encore suivi, puis devient rouge dès `git add`, où l'index le rend inventoriable. `test_manifest_idempotent_after_rebuild` copie le corpus sous `tmp_path`, exécute un premier `runpy.run_module("scripts.rebuild_inventory", run_name="__main__")` avec les trois primitives monkeypatchées, compare les deux sorties reconstruites aux sorties suivies périmées et échoue sur ce delta ; il exécute néanmoins un second rebuild dans la copie et exige son idempotence. Avant staging, ces trois nodes donnent exactement deux failures ; après staging, exactement trois.

- [ ] **Step 44: Vérifier la collecte corpus isolée**

```bash
set -euo pipefail
CORPUS_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
cd "$CORPUS_ROOT"
python3 -m pytest --collect-only -q -p no:cacheprovider \
  tests/test_rag_governance_and_indexes.py \
  tests/test_secret_guard.py \
  tests/test_openrouter_judges.py \
  tests/test_substance_judge_pipeline.py \
  tests/test_substance_hardened.py \
  tests/test_judge_collection_barriers.py \
  tests/test_policy_checker_ast.py \
  tests/test_manifest_separation.py
```

Expected: collecte verte, aucun import futur au niveau module.

- [ ] **Step 45: Observer le Red corpus pour les causes attendues**

```bash
set -euo pipefail
CORPUS_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-baseline-pointer.*' ! -name '*.complete' -print)
test "${#POINTERS[@]}" -eq 1
POINTER=${POINTERS[0]}
test -O "$POINTER"; test ! -L "$POINTER"; test "$(stat -c '%a' "$POINTER")" = 600
EVIDENCE_ROOT=$(cat "$POINTER")
case "$EVIDENCE_ROOT" in /tmp/nexus-openrouter-baseline.*) ;; *) exit 1 ;; esac
test -d "$EVIDENCE_ROOT"
cd "$CORPUS_ROOT"
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
    tests/test_rag_governance_and_indexes.py \
    tests/test_secret_guard.py \
    tests/test_openrouter_judges.py \
    tests/test_substance_judge_pipeline.py \
    tests/test_substance_hardened.py \
    tests/test_judge_collection_barriers.py \
    tests/test_policy_checker_ast.py \
    tests/test_manifest_separation.py \
    --junitxml "$EVIDENCE_ROOT/red-corpus.xml" \
    > "$EVIDENCE_ROOT/red-corpus.out" 2>&1
RED_CORPUS_RC=$?
set -e
test "$RED_CORPUS_RC" -eq 1
rg -e 'ANTHROPIC_API_KEY|LOCAL_LLM|nexus_external|OpenRouter' "$EVIDENCE_ROOT/red-corpus.out"
! rg -F 'ERROR collecting' "$EVIDENCE_ROOT/red-corpus.out"
python3 - "$EVIDENCE_ROOT/red-corpus.xml" <<'PY'
import sys, xml.etree.ElementTree as ET
r=ET.parse(sys.argv[1]).getroot();s=r.findall(".//testsuite") or [r]
got={k:sum(int(x.get(k,"0")) for x in s) for k in ("tests","failures","errors","skipped")}
new = """test_campaign_delegates_to_shared_openrouter_client
test_campaign_reads_missing_openrouter_values_from_resolved_rag_env
test_campaign_does_not_read_generic_dotenv
test_campaign_rejects_key_without_model_before_transport
test_campaign_business_retry_count_is_bounded
test_campaign_records_requested_openrouter_model
test_campaign_records_each_billed_retry_generation_before_verdict_validation
test_usage_v2_copies_completion_accounting_exactly
test_usage_upsert_replaces_same_generation_only
test_usage_upsert_preserves_v1_deeply_and_in_order
test_usage_upsert_preserves_other_v2_generations_for_same_capacity
test_usage_logging_contains_no_local_cost_formula
test_failed_usage_entry_invents_no_accounting
test_run_totals_sum_only_current_successful_v2_entries
test_substance_llm_delegates_to_shared_openrouter_client
test_substance_rejects_key_without_model_before_transport
test_substance_sends_exact_bounded_prompt_and_limit
test_substance_accepts_only_exact_closed_json_object
test_substance_has_no_configurable_llm_endpoint
test_substance_remote_error_is_sanitized_and_never_promotes
test_run_substance_judge_uses_honest_deterministic_model
test_campaign_discovers_current_checkout_from_unrelated_cwd
test_substance_discovers_current_checkout_from_unrelated_cwd
test_corpus_callers_reject_shadowed_external_package""".splitlines()
expected = {f"tests/test_openrouter_judges.py::{name}" for name in new}
expected |= {
 "tests/test_rag_governance_and_indexes.py::test_rag_env_example_uses_internal_corpus_without_real_secret",
 "tests/test_secret_guard.py::test_detects_token_like_assignments_without_flagging_examples",
 "tests/test_substance_hardened.py::TestSubstanceHardened::test_api_error_preserves_existing_valid_verdict",
 "tests/test_policy_checker_ast.py::test_real_judge_passes",
 "tests/test_manifest_separation.py::test_pedagogical_manifest_contains_only_pedagogical_content",
 "tests/test_manifest_separation.py::test_manifest_idempotent_after_rebuild",
}
failed=set()
for case in r.findall('.//testcase'):
    if case.find('failure') is None:
        continue
    parts=case.get('classname','').split('.')
    if parts and parts[-1].startswith('Test'):
        failed.add(f"{'/'.join(parts[:-1])}.py::{parts[-1]}::{case.get('name','')}")
    else:
        failed.add(f"{'/'.join(parts)}.py::{case.get('name','')}")
assert got=={"tests":115,"failures":len(expected),"errors":0,"skipped":0},got
assert failed == expected, (failed - expected, expected - failed)
PY
```

Expected: 115 nodes littéraux : 85 historiques, 27 nouveaux OpenRouter et 3 manifest ; ensemble exact des 30 failures métier avant staging, zéro collecte cassée, zéro skip et zéro réseau. Le troisième Red manifest n'apparaît qu'après indexation dans Task 7.

### Task 7: Sceller et committer le jalon Red

**Files:** tous les tests créés/modifiés dans les Tasks 4 à 6, aucun fichier de production.

- [ ] **Step 1: Rejouer exactement les quatre Reds et vérifier leurs causes**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-baseline-pointer.*' ! -name '*.complete' -print)
test "${#POINTERS[@]}" -eq 1
POINTER=${POINTERS[0]}
test -O "$POINTER"; test ! -L "$POINTER"; test "$(stat -c '%a' "$POINTER")" = 600
EVIDENCE_ROOT=$(cat "$POINTER")
case "$EVIDENCE_ROOT" in /tmp/nexus-openrouter-baseline.*) ;; *) exit 1 ;; esac
test -d "$EVIDENCE_ROOT"
cd "$IMPL_ROOT"
test -z "$(git diff --cached --name-only)"
python3 - "$IMPL_ROOT" "$EVIDENCE_ROOT/corpus-baseline-85.nodeids" <<'PY'
import os, subprocess, sys
from pathlib import Path
root = Path(sys.argv[1])
baseline85 = set(Path(sys.argv[2]).read_text(encoding="utf-8").splitlines())
client = (
"test_chat_completion_posts_to_exact_openrouter_endpoint test_chat_completion_sends_bearer_and_json_headers "
"test_chat_completion_sends_one_model_and_max_completion_tokens test_chat_completion_uses_injected_mock_transport_without_socket "
"test_chat_completion_caps_timeout_at_thirty_seconds test_chat_completion_does_not_follow_redirects "
"test_chat_completion_returns_validated_structured_result test_completion_and_usage_are_immutable "
"test_http_failure_maps_to_sanitized_error_category "
"test_http_200_refuses_root_error_object test_http_200_refuses_choice_error_object test_http_200_refuses_non_stop_finish_reason "
"test_response_rejects_malformed_envelope_component test_errors_and_logs_never_expose_secret_prompt_or_raw_body "
"test_client_does_not_retry_failed_request test_client_rejects_blank_key_before_transport test_client_rejects_blank_model_before_transport "
"test_usage_rejects_invalid_required_accounting test_usage_rejects_invalid_cache_details "
"test_usage_normalizes_absent_cache_counters_to_zero test_usage_preserves_exact_openrouter_cost "
"test_response_rejects_invalid_root_generation_id test_response_rejects_invalid_returned_model"
).split()
classification = (
"test_classification_without_key_uses_local_heuristic_without_transport test_classification_with_key_without_model_fails_before_transport "
"test_classification_with_key_and_model_forwards_exact_model test_classification_sends_only_first_3000_fragment_characters "
"test_classification_requests_200_completion_tokens test_local_heuristic_preserves_existing_chunk_type_contract "
"test_remote_classification_accepts_exact_closed_object test_remote_classification_rejects_invalid_closed_object_as_a_whole "
"test_remote_classification_rejects_boolean_difficulty test_invalid_remote_classification_returns_global_conservative_result "
"test_remote_metadata_cannot_override_trusted_record_fields test_prompt_does_not_append_environment_or_provenance_metadata"
).split()
policy = (
"test_policy_requires_every_canonical_active_surface test_policy_rejects_unlisted_provider_transport "
"test_policy_allows_only_openrouter_client_to_define_llm_endpoint test_policy_preserves_non_llm_rag_transport_allowlist "
"test_policy_rejects_chutes_in_active_authority test_policy_ignores_protected_historical_chutes_artifacts "
"test_policy_rejects_model_catalog_endpoint_in_automation test_policy_rejects_new_nsi_ingest_make_target "
"test_targeted_surfaces_exist_before_negative_scans test_policy_rejects_anthropic_in_active_callers "
"test_policy_rejects_local_llm_configuration_in_active_surfaces test_ci_no_deps_requirements_close_httpx_runtime_dependencies"
).split()
assert (len(client), len(classification), len(policy)) == (23, 12, 12)
expected_core = {f"tests/test_openrouter_client.py::{name}" for name in client}
expected_core |= {f"tests/test_openrouter_classification.py::{name}" for name in classification}
expected_core |= {f"tests/test_external_provider_policy.py::{name}" for name in policy}
clean_env = {k: v for k, v in os.environ.items() if k not in {"OPENROUTER_API_KEY", "OPENROUTER_MODEL", "ANTHROPIC_API_KEY", "LOCAL_LLM_BASE_URL"}}
out = subprocess.check_output([sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", "tests/test_openrouter_client.py", "tests/test_openrouter_classification.py", "tests/test_external_provider_policy.py"], cwd=root, text=True, env=clean_env)
actual = {line for line in out.splitlines() if line.startswith("tests/")}
assert actual == expected_core, (actual - expected_core, expected_core - actual)
assert len(actual) == 47
for prefix, cwd in (("math", root / "Mathematiques/manuel-maths"), ("nsi", root / "NSI")):
    names = (
        f"test_{prefix}_ingest_classify_delegates_to_shared_classifier",
        f"test_{prefix}_ingest_preserves_trusted_metadata_against_hostile_classifier",
        f"test_{prefix}_ingest_command_runs_without_source_key_or_network",
        f"test_{prefix}_ingest_discovers_current_checkout_from_unrelated_cwd",
        f"test_{prefix}_ingest_prioritizes_current_checkout_over_shadow_package",
        f"test_{prefix}_ingest_rejects_nexus_external_loaded_outside_checkout",
        f"test_{prefix}_no_source_command_does_not_import_extraction_backends",
        f"test_{prefix}_network_guard_mutation_is_effective",
    )
    expected = {f"tests/test_ingest_openrouter.py::{name}" for name in names}
    out = subprocess.check_output([sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", "tests/test_ingest_openrouter.py"], cwd=cwd, text=True, env=clean_env)
    actual = {line for line in out.splitlines() if line.startswith("tests/")}
    assert actual == expected, (prefix, actual - expected, expected - actual)
    assert len(actual) == 8
corpus_new = (
"test_campaign_delegates_to_shared_openrouter_client test_campaign_reads_missing_openrouter_values_from_resolved_rag_env "
"test_campaign_does_not_read_generic_dotenv test_campaign_rejects_key_without_model_before_transport "
"test_campaign_business_retry_count_is_bounded test_campaign_records_requested_openrouter_model "
"test_campaign_records_each_billed_retry_generation_before_verdict_validation test_usage_v2_copies_completion_accounting_exactly "
"test_usage_upsert_replaces_same_generation_only test_usage_upsert_preserves_v1_deeply_and_in_order "
"test_usage_upsert_preserves_other_v2_generations_for_same_capacity test_usage_logging_contains_no_local_cost_formula "
"test_failed_usage_entry_invents_no_accounting test_run_totals_sum_only_current_successful_v2_entries "
"test_substance_llm_delegates_to_shared_openrouter_client test_substance_without_key_returns_conservative_result_without_transport "
"test_substance_rejects_key_without_model_before_transport test_substance_sends_exact_bounded_prompt_and_limit "
"test_substance_accepts_only_exact_closed_json_object test_substance_rag_keeps_dedicated_http_transport "
"test_substance_has_no_configurable_llm_endpoint test_substance_remote_error_is_sanitized_and_never_promotes "
"test_run_substance_judge_imports_no_external_client test_run_substance_judge_uses_honest_deterministic_model "
"test_campaign_discovers_current_checkout_from_unrelated_cwd test_substance_discovers_current_checkout_from_unrelated_cwd "
"test_corpus_callers_reject_shadowed_external_package"
).split()
corpus_files = ("test_rag_governance_and_indexes.py", "test_secret_guard.py", "test_openrouter_judges.py", "test_substance_judge_pipeline.py", "test_substance_hardened.py", "test_judge_collection_barriers.py", "test_policy_checker_ast.py", "test_manifest_separation.py")
manifest = {
"tests/test_manifest_separation.py::test_pedagogical_manifest_contains_only_pedagogical_content",
"tests/test_manifest_separation.py::test_manifests_cover_all_inventoried_resources",
"tests/test_manifest_separation.py::test_manifest_idempotent_after_rebuild",
}
out = subprocess.check_output([sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", *(f"tests/{name}" for name in corpus_files)], cwd=root / "NSI/corpus_nsi", text=True, env=clean_env)
actual = {line for line in out.splitlines() if line.startswith("tests/")}
expected_new = {f"tests/test_openrouter_judges.py::{name}" for name in corpus_new}
expected_corpus = baseline85 | expected_new | manifest
assert len(baseline85) == 85 and len(expected_new) == 27 and len(manifest) == 3
assert actual == expected_corpus, (actual - expected_corpus, expected_corpus - actual)
assert len(actual) == 115
PY
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_client.py \
  tests/test_openrouter_classification.py \
  tests/test_external_provider_policy.py \
  --junitxml "$EVIDENCE_ROOT/red-final-core.xml" \
  > "$EVIDENCE_ROOT/red-final-core.out" 2>&1
RC_CORE=$?
cd "$IMPL_ROOT/Mathematiques/manuel-maths"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
python3 -m pytest -q -p no:cacheprovider tests/test_ingest_openrouter.py \
  --junitxml "$EVIDENCE_ROOT/red-final-math.xml" \
  > "$EVIDENCE_ROOT/red-final-math.out" 2>&1
RC_MATH=$?
cd "$IMPL_ROOT/NSI"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
python3 -m pytest -q -p no:cacheprovider tests/test_ingest_openrouter.py \
  --junitxml "$EVIDENCE_ROOT/red-final-nsi.xml" \
  > "$EVIDENCE_ROOT/red-final-nsi.out" 2>&1
RC_NSI=$?
cd "$IMPL_ROOT/NSI/corpus_nsi"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
python3 -m pytest -q -p no:cacheprovider \
  tests/test_rag_governance_and_indexes.py tests/test_secret_guard.py \
  tests/test_openrouter_judges.py tests/test_substance_judge_pipeline.py \
  tests/test_substance_hardened.py tests/test_judge_collection_barriers.py \
  tests/test_policy_checker_ast.py tests/test_manifest_separation.py \
  --junitxml "$EVIDENCE_ROOT/red-final-corpus.xml" \
  > "$EVIDENCE_ROOT/red-final-corpus.out" 2>&1
RC_CORPUS=$?
set -e
test "$RC_CORE" -eq 1
test "$RC_MATH" -eq 1
test "$RC_NSI" -eq 1
test "$RC_CORPUS" -eq 1
! rg -F 'ERROR collecting' "$EVIDENCE_ROOT"/red-final-*.out
rg -e 'nexus_external|OpenRouter|ANTHROPIC_API_KEY|LOCAL_LLM' \
  "$EVIDENCE_ROOT"/red-final-*.out
python3 - "$EVIDENCE_ROOT" <<'PY'
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

evidence = Path(sys.argv[1])
expected_totals = {
    "core": {"tests": 47, "failures": 42, "errors": 0, "skipped": 0},
    "math": {"tests": 8, "failures": 6, "errors": 0, "skipped": 0},
    "nsi": {"tests": 8, "failures": 6, "errors": 0, "skipped": 0},
    "corpus": {"tests": 115, "failures": 30, "errors": 0, "skipped": 0},
}
for label, expected in expected_totals.items():
    tree = ET.parse(evidence / f"red-final-{label}.xml")
    suites = tree.findall(".//testsuite") or [tree.getroot()]
    got = {key: sum(int(s.attrib.get(key, "0")) for s in suites) for key in expected}
    assert got == expected, (label, got, expected)
PY
```

Expected: quatre Reds exacts, causes contractuelles et index vide. Si un processus passe déjà ou échoue autrement, `HARD STOP`.

- [ ] **Step 2: Vérifier l’allowlist du diff Red**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
git status --short
git diff --name-only | sort
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL python3 - <<'PY'
import subprocess

allowed = {
    "tests/test_openrouter_client.py",
    "tests/test_openrouter_classification.py",
    "tests/test_external_provider_policy.py",
    "Mathematiques/manuel-maths/tests/test_ingest_openrouter.py",
    "NSI/tests/test_ingest_openrouter.py",
    "NSI/corpus_nsi/tests/test_openrouter_judges.py",
    "NSI/corpus_nsi/tests/test_manifest_separation.py",
    "NSI/corpus_nsi/tests/test_rag_governance_and_indexes.py",
    "NSI/corpus_nsi/tests/test_secret_guard.py",
    "NSI/corpus_nsi/tests/test_substance_judge_pipeline.py",
    "NSI/corpus_nsi/tests/test_substance_hardened.py",
    "NSI/corpus_nsi/tests/test_judge_collection_barriers.py",
    "NSI/corpus_nsi/tests/test_policy_checker_ast.py",
}
actual = set(subprocess.check_output(
    ["git", "status", "--porcelain=v1"], text=True
).splitlines())
paths = {line[3:] for line in actual}
assert paths == allowed, (paths - allowed, allowed - paths)
PY
git diff --check
```

Expected: exactement treize fichiers de tests, aucune production, documentation, sortie générée ou preuve historique.

- [ ] **Step 3: Indexer explicitement les tests et inspecter le staged diff**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
git add -- \
  tests/test_openrouter_client.py \
  tests/test_openrouter_classification.py \
  tests/test_external_provider_policy.py \
  Mathematiques/manuel-maths/tests/test_ingest_openrouter.py \
  NSI/tests/test_ingest_openrouter.py \
  NSI/corpus_nsi/tests/test_openrouter_judges.py \
  NSI/corpus_nsi/tests/test_manifest_separation.py \
  NSI/corpus_nsi/tests/test_rag_governance_and_indexes.py \
  NSI/corpus_nsi/tests/test_secret_guard.py \
  NSI/corpus_nsi/tests/test_substance_judge_pipeline.py \
  NSI/corpus_nsi/tests/test_substance_hardened.py \
  NSI/corpus_nsi/tests/test_judge_collection_barriers.py \
  NSI/corpus_nsi/tests/test_policy_checker_ast.py
git diff --cached --name-only | sort
git diff --cached --check
git diff --cached --stat
```

Expected: même allowlist, tests Red lisibles, aucun secret ni marqueur temporaire.

- [ ] **Step 4: Rejouer le Red staged, manifest inclus, immédiatement avant revue**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
RUN_TMP=$(mktemp -d /tmp/nexus-openrouter-red-staged.XXXXXX)
cd "$IMPL_ROOT"; set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL python3 -m pytest -q -p no:cacheprovider tests/test_openrouter_client.py tests/test_openrouter_classification.py tests/test_external_provider_policy.py --junitxml "$RUN_TMP/core.xml"; RC_CORE=$?
cd "$IMPL_ROOT/Mathematiques/manuel-maths"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL python3 -m pytest -q -p no:cacheprovider tests/test_ingest_openrouter.py --junitxml "$RUN_TMP/math.xml"; RC_MATH=$?
cd "$IMPL_ROOT/NSI"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL python3 -m pytest -q -p no:cacheprovider tests/test_ingest_openrouter.py --junitxml "$RUN_TMP/nsi.xml"; RC_NSI=$?
cd "$IMPL_ROOT/NSI/corpus_nsi"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL python3 -m pytest -q -p no:cacheprovider tests/test_rag_governance_and_indexes.py tests/test_secret_guard.py tests/test_openrouter_judges.py tests/test_substance_judge_pipeline.py tests/test_substance_hardened.py tests/test_judge_collection_barriers.py tests/test_policy_checker_ast.py tests/test_manifest_separation.py --junitxml "$RUN_TMP/corpus.xml"; RC_CORPUS=$?
set -e
test "$RC_CORE" -eq 1; test "$RC_MATH" -eq 1; test "$RC_NSI" -eq 1; test "$RC_CORPUS" -eq 1
python3 - "$RUN_TMP" <<'PY'
import sys, xml.etree.ElementTree as ET
from pathlib import Path
expected={"core":(47,42),"math":(8,6),"nsi":(8,6),"corpus":(115,31)}
for label,(tests,failures) in expected.items():
 r=ET.parse(Path(sys.argv[1])/f"{label}.xml").getroot();s=r.findall(".//testsuite") or [r]
 got={k:sum(int(x.get(k,"0")) for x in s) for k in ("tests","failures","errors","skipped")}
 assert got=={"tests":tests,"failures":failures,"errors":0,"skipped":0},(label,got)

def nodeids(tree):
 result=set()
 for case in tree.findall(".//testcase"):
  if case.find("failure") is None:
   continue
  parts=case.get("classname","").split(".")
  if parts and parts[-1].startswith("Test"):
   result.add(f"{'/'.join(parts[:-1])}.py::{parts[-1]}::{case.get('name','')}")
  else:
   result.add(f"{'/'.join(parts)}.py::{case.get('name','')}")
 return result

client="""test_chat_completion_posts_to_exact_openrouter_endpoint
test_chat_completion_sends_bearer_and_json_headers
test_chat_completion_sends_one_model_and_max_completion_tokens
test_chat_completion_uses_injected_mock_transport_without_socket
test_chat_completion_caps_timeout_at_thirty_seconds
test_chat_completion_does_not_follow_redirects
test_chat_completion_returns_validated_structured_result
test_completion_and_usage_are_immutable
test_http_failure_maps_to_sanitized_error_category
test_http_200_refuses_root_error_object
test_http_200_refuses_choice_error_object
test_http_200_refuses_non_stop_finish_reason
test_response_rejects_malformed_envelope_component
test_errors_and_logs_never_expose_secret_prompt_or_raw_body
test_client_does_not_retry_failed_request
test_client_rejects_blank_key_before_transport
test_client_rejects_blank_model_before_transport
test_usage_rejects_invalid_required_accounting
test_usage_rejects_invalid_cache_details
test_usage_normalizes_absent_cache_counters_to_zero
test_usage_preserves_exact_openrouter_cost
test_response_rejects_invalid_root_generation_id
test_response_rejects_invalid_returned_model""".splitlines()
classification="""test_classification_without_key_uses_local_heuristic_without_transport
test_classification_with_key_without_model_fails_before_transport
test_classification_with_key_and_model_forwards_exact_model
test_classification_sends_only_first_3000_fragment_characters
test_classification_requests_200_completion_tokens
test_local_heuristic_preserves_existing_chunk_type_contract
test_remote_classification_accepts_exact_closed_object
test_remote_classification_rejects_invalid_closed_object_as_a_whole
test_remote_classification_rejects_boolean_difficulty
test_invalid_remote_classification_returns_global_conservative_result
test_remote_metadata_cannot_override_trusted_record_fields
test_prompt_does_not_append_environment_or_provenance_metadata""".splitlines()
policy="""test_policy_requires_every_canonical_active_surface
test_policy_rejects_unlisted_provider_transport
test_policy_allows_only_openrouter_client_to_define_llm_endpoint
test_policy_rejects_chutes_in_active_authority
test_policy_rejects_anthropic_in_active_callers
test_policy_rejects_local_llm_configuration_in_active_surfaces
test_ci_no_deps_requirements_close_httpx_runtime_dependencies""".splitlines()
expected_core={f"tests/test_openrouter_client.py::{x}" for x in client}
expected_core|={f"tests/test_openrouter_classification.py::{x}" for x in classification}
expected_core|={f"tests/test_external_provider_policy.py::{x}" for x in policy}
adapter_failures={
 "math": {
  "test_math_ingest_classify_delegates_to_shared_classifier",
  "test_math_ingest_preserves_trusted_metadata_against_hostile_classifier",
  "test_math_ingest_discovers_current_checkout_from_unrelated_cwd",
  "test_math_ingest_prioritizes_current_checkout_over_shadow_package",
  "test_math_ingest_rejects_nexus_external_loaded_outside_checkout",
  "test_math_no_source_command_does_not_import_extraction_backends",
 },
 "nsi": {
  "test_nsi_ingest_classify_delegates_to_shared_classifier",
  "test_nsi_ingest_preserves_trusted_metadata_against_hostile_classifier",
  "test_nsi_ingest_discovers_current_checkout_from_unrelated_cwd",
  "test_nsi_ingest_prioritizes_current_checkout_over_shadow_package",
  "test_nsi_ingest_rejects_nexus_external_loaded_outside_checkout",
  "test_nsi_no_source_command_does_not_import_extraction_backends",
 },
}
corpus_new="""test_campaign_delegates_to_shared_openrouter_client
test_campaign_reads_missing_openrouter_values_from_resolved_rag_env
test_campaign_does_not_read_generic_dotenv
test_campaign_rejects_key_without_model_before_transport
test_campaign_business_retry_count_is_bounded
test_campaign_records_requested_openrouter_model
test_campaign_records_each_billed_retry_generation_before_verdict_validation
test_usage_v2_copies_completion_accounting_exactly
test_usage_upsert_replaces_same_generation_only
test_usage_upsert_preserves_v1_deeply_and_in_order
test_usage_upsert_preserves_other_v2_generations_for_same_capacity
test_usage_logging_contains_no_local_cost_formula
test_failed_usage_entry_invents_no_accounting
test_run_totals_sum_only_current_successful_v2_entries
test_substance_llm_delegates_to_shared_openrouter_client
test_substance_rejects_key_without_model_before_transport
test_substance_sends_exact_bounded_prompt_and_limit
test_substance_accepts_only_exact_closed_json_object
test_substance_has_no_configurable_llm_endpoint
test_substance_remote_error_is_sanitized_and_never_promotes
test_run_substance_judge_uses_honest_deterministic_model
test_campaign_discovers_current_checkout_from_unrelated_cwd
test_substance_discovers_current_checkout_from_unrelated_cwd
test_corpus_callers_reject_shadowed_external_package""".splitlines()
expected_corpus={f"tests/test_openrouter_judges.py::{x}" for x in corpus_new}
expected_corpus|={
 "tests/test_rag_governance_and_indexes.py::test_rag_env_example_uses_internal_corpus_without_real_secret",
 "tests/test_secret_guard.py::test_detects_token_like_assignments_without_flagging_examples",
 "tests/test_substance_hardened.py::TestSubstanceHardened::test_api_error_preserves_existing_valid_verdict",
 "tests/test_policy_checker_ast.py::test_real_judge_passes",
 "tests/test_manifest_separation.py::test_pedagogical_manifest_contains_only_pedagogical_content",
 "tests/test_manifest_separation.py::test_manifests_cover_all_inventoried_resources",
 "tests/test_manifest_separation.py::test_manifest_idempotent_after_rebuild",
}
trees={label:ET.parse(Path(sys.argv[1])/f"{label}.xml").getroot() for label in expected}
assert nodeids(trees["core"])==expected_core
for label,names in adapter_failures.items():
 assert nodeids(trees[label])=={f"tests/test_ingest_openrouter.py::{x}" for x in names}
assert nodeids(trees["corpus"])==expected_corpus
PY
```

Expected: staging rend les trois tests manifest rouges exactement `3/3`; aucun autre compte ne dérive. Tout écart est `HARD STOP`.

- [ ] **Step 5: Faire relire le lot Red avant commit**

L’agent principal lance un implementer frais pour vérifier les causes Red, puis un reviewer conformité-spécification et un reviewer qualité distincts. Leur mandat interdit toute correction de production. Après toute correction test-only, réindexer exactement les treize chemins, exiger zéro unstaged et réexécuter intégralement le bloc autonome Step 4 : il réaffirme à la fois l'allowlist des quatre suites, leurs comptes et l'ensemble littéral de chaque nodeid échoué. Re-dispatcher ensuite les deux reviewers sur le nouveau staged diff ; boucler correction → restaging exact → replay exact → double re-revue jusqu'à deux verdicts `✅ Approved`, puis rejouer une dernière fois Step 4 immédiatement avant le commit. `HARD STOP` sur test tautologique, réseau possible, import de collecte futur, affaiblissement d’un gate ou surface de spec non testée.

- [ ] **Step 6: Committer le contrat Red**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
git commit -m "[TESTS] verrouille la passerelle OpenRouter"
git status --short
test -z "$(git status --short)"
```

Expected: un commit tests-only atomique. Aucun Green avant validation humaine explicite du jalon Red si celle-ci est demandée par le responsable.

## Chunk 6: Green du client, de la classification et des ingestions

### Task 8: Implémenter le client OpenRouter partagé

**Files:**

- Create: `nexus_external/__init__.py`
- Create: `nexus_external/openrouter_client.py`
- Test: `tests/test_openrouter_client.py`

- [ ] **Step 1: Confier ce Task à un implementer frais**

L’agent reçoit uniquement la spécification approuvée, le plan, le commit Red et ces deux fichiers de production. Il ne modifie ni tests, ni appelants, ni documentation. Avant édition, il relit `AGENTS.md`, vérifie le SHA Red et reproduit le processus `tests/test_openrouter_client.py` rouge sans erreur de collecte.

- [ ] **Step 2: Créer seulement les types publics immuables**

Utiliser `apply_patch` sur les chemins absolus sous `/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/nexus_external/`. `__init__.py` réexporte seulement :

```python
from .openrouter_client import (
    OpenRouterCompletion,
    OpenRouterError,
    OpenRouterUsage,
    chat_completion,
)

__all__ = [
    "OpenRouterCompletion",
    "OpenRouterError",
    "OpenRouterUsage",
    "chat_completion",
]
```

Dans `openrouter_client.py`, fixer sans variable d’environnement :

```python
OPENROUTER_CHAT_COMPLETIONS_URL = "https://openrouter.ai/api/v1/chat/completions"
```

Créer exactement :

```python
@dataclass(frozen=True, slots=True)
class OpenRouterUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float
    cached_tokens: int
    cache_write_tokens: int


@dataclass(frozen=True, slots=True)
class OpenRouterCompletion:
    content: str
    generation_id: str
    model: str
    provider: str | None
    usage: OpenRouterUsage


class OpenRouterError(RuntimeError):
    def __init__(
        self,
        category: str,
        *,
        model: str,
        status_code: int | None = None,
    ) -> None:
        self.category = category
        self.status_code = status_code
        self.model = model
        status = f" status={status_code}" if status_code is not None else ""
        super().__init__(
            f"OpenRouter {category}{status} endpoint={OPENROUTER_CHAT_COMPLETIONS_URL} model={model}"
        )
```

Les catégories sont l’union fermée `configuration`, `payment`, `authentication`, `authorization`, `rate_limit`, `timeout`, `transport`, `unavailable`, `protocol`. Ajouter une signature `chat_completion` minimale qui lève `NotImplementedError`. Le test Red est déjà scellé et construit directement un `OpenRouterUsage` puis un `OpenRouterCompletion` avant de tenter de muter chacun ; ne pas modifier ce test au Green. Puis exécuter autonomement :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_client.py::test_completion_and_usage_are_immutable
```

Expected: `1 passed`; aucun autre node n’est requis vert à cette micro-étape.

- [ ] **Step 3: Implémenter seulement les validations de configuration**

Par `apply_patch` sur le chemin absolu `nexus_external/openrouter_client.py`, valider avant tout transport : clé et modèle non vides après `strip()` ; `max_completion_tokens` entier non booléen dans `[1, 16_384]` ; séquence non vide de messages ; chaque message contient exactement `role` et `content`, rôle parmi `system`, `user`, `assistant`, contenu chaîne non vide. Les erreurs sont `OpenRouterError("configuration")` et aucune valeur entrante ne paraît dans le message. La matrice Red scellée dans `test_chat_completion_sends_one_model_and_max_completion_tokens` doit rejeter exactement `0`, `True`, `16_385`, messages vides/non séquentiels, objet message invalide, rôle invalide, contenu invalide et clé supplémentaire avant le premier appel transport. Puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_client.py::test_client_rejects_blank_key_before_transport \
  tests/test_openrouter_client.py::test_client_rejects_blank_model_before_transport
```

Expected: `2 passed`, transport non appelé.

- [ ] **Step 4: Implémenter seulement la requête HTTP fermée**

La signature reste exactement `chat_completion(*, api_key: str, model: str, messages: Sequence[Mapping[str, str]], max_completion_tokens: int, transport: httpx.BaseTransport | None = None) -> OpenRouterCompletion`.

Par `apply_patch` sur le chemin absolu du client, créer un `httpx.Client` synchrone avec `timeout=httpx.Timeout(30.0)`, `follow_redirects=False`, transport injecté, puis effectuer exactement un `POST`. Envoyer uniquement `model`, `messages`, `max_completion_tokens`, ainsi que `Authorization: Bearer <clé injectée>` et `Content-Type: application/json`. Ne jamais envoyer `models`, `max_tokens`, clé de fournisseur, fallback ou retry. Puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_client.py::test_chat_completion_posts_to_exact_openrouter_endpoint \
  tests/test_openrouter_client.py::test_chat_completion_sends_bearer_and_json_headers \
  tests/test_openrouter_client.py::test_chat_completion_sends_one_model_and_max_completion_tokens \
  tests/test_openrouter_client.py::test_chat_completion_uses_injected_mock_transport_without_socket \
  tests/test_openrouter_client.py::test_chat_completion_caps_timeout_at_thirty_seconds \
  tests/test_openrouter_client.py::test_chat_completion_does_not_follow_redirects
```

Expected: `6 passed`, exactement un POST par invocation.

- [ ] **Step 5: Mapper seulement les échecs transport et HTTP**

Par `apply_patch` sur le chemin absolu du client, ajouter la table minimale :

```python
def _category_for_status(status: int) -> str:
    if status == 402:
        return "payment"
    if status == 401:
        return "authentication"
    if status == 403:
        return "authorization"
    if status == 429:
        return "rate_limit"
    if status == 408:
        return "timeout"
    if status >= 500:
        return "unavailable"
    return "protocol"
```

Mapper `httpx.TimeoutException` vers `timeout`, les autres `httpx.TransportError` vers `transport`. Ne concaténer ni `response.text`, ni exception de bas niveau, ni requête, ni prompt. Ne journaliser aucun payload.

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_client.py::test_http_failure_maps_to_sanitized_error_category \
  tests/test_openrouter_client.py::test_errors_and_logs_never_expose_secret_prompt_or_raw_body \
  tests/test_openrouter_client.py::test_client_does_not_retry_failed_request
```

Expected: `3 passed`, aucune seconde requête.

- [ ] **Step 6: Valider seulement l’enveloppe de complétion**

Par `apply_patch` sur le chemin absolu du client, refuser toute réponse non-2xx avant parsing, JSON non objet, `error` racine, `choices` absente/non liste/vide, premier choix mal typé ou porteur d’`error`, `finish_reason != "stop"`, message/content non textuel ou vide, rôle autre qu'`assistant`, clé message supplémentaire, `id`/`model` manquant, non chaîne ou vide après `strip()`, `provider` présent mais vide ou non chaîne. Si plusieurs choix sont présents et que le premier est valide, consommer seulement ce premier choix et ignorer les suivants : ne jamais exiger une longueur exactement égale à un. Laisser l’usage à un helper encore minimal. Puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_client.py::test_http_200_refuses_root_error_object \
  tests/test_openrouter_client.py::test_http_200_refuses_choice_error_object \
  tests/test_openrouter_client.py::test_http_200_refuses_non_stop_finish_reason \
  tests/test_openrouter_client.py::test_response_rejects_malformed_envelope_component \
  tests/test_openrouter_client.py::test_response_rejects_invalid_root_generation_id \
  tests/test_openrouter_client.py::test_response_rejects_invalid_returned_model
```

Expected: `6 passed`.

- [ ] **Step 7: Valider seulement l’usage OpenRouter**

Par `apply_patch` sur le chemin absolu du client, rendre `usage` obligatoire :

- les trois tokens sont des `int` non booléens, positifs ou nuls ;
- `total_tokens == prompt_tokens + completion_tokens` ;
- `cost` est un `int`/`float` non booléen, fini et non négatif ;
- `prompt_tokens_details`, s’il existe, est un objet ;
- `cached_tokens` et `cache_write_tokens`, s’ils manquent, valent 0 ; présents, ce sont des entiers non booléens entre 0 et `prompt_tokens`.

Retourner l’objet gelé complet et ne jamais effectuer `/generation` pour compléter l’usage.

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_client.py::test_chat_completion_returns_validated_structured_result \
  tests/test_openrouter_client.py::test_usage_rejects_invalid_required_accounting \
  tests/test_openrouter_client.py::test_usage_rejects_invalid_cache_details \
  tests/test_openrouter_client.py::test_usage_normalizes_absent_cache_counters_to_zero \
  tests/test_openrouter_client.py::test_usage_preserves_exact_openrouter_cost
```

Expected: `5 passed`; `bool`, NaN, valeur négative et total incohérent restent rejetés.

- [ ] **Step 8: Passer le test client puis faire deux revues**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider tests/test_openrouter_client.py
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m ruff check nexus_external/openrouter_client.py
```

Expected: tous les nodes client verts, un seul appel observé par mutation, Ruff vert. L’agent principal lance ensuite un reviewer spécification puis un reviewer qualité distinct ; l’implementer corrige les constats validés avant Task 9.

- [ ] **Step 9: Passer les deux nodes de bord déjà scellés au Red**

Sans modifier `tests/test_openrouter_client.py`, les deux nodes ont déjà été exécutés Step 6 puis toute la suite Step 8. Les validations rôles, clé fermée des messages et borne 16 384 restent des matrices internes aux nodes audit. Toute nécessité d’éditer un test ici est `HARD STOP` et retourne au commit Red.

### Task 9: Implémenter la classification partagée

**Files:**

- Create: `nexus_external/classification.py`
- Test: `tests/test_openrouter_classification.py`

- [ ] **Step 1: Confier ce Task à un nouvel implementer**

Reproduire uniquement `tests/test_openrouter_classification.py` rouge sur le commit contenant le client vert. Le nouvel agent ne modifie ni le client validé, ni les ingestions.

- [ ] **Step 2: Définir seulement le contrat fermé et l’heuristique pure**

Créer des constantes immuables pour les cinq clés, les huit `chunk_type`, les quatre niveaux et :

```python
CONSERVATIVE_CLASSIFICATION = {
    "chunk_type": "autre",
    "niveau": None,
    "theme": None,
    "capacites": [],
    "difficulte": None,
}
```

`classify_locally(chunk)` reprend exactement la cascade, dans cet ordre : préfixe `exercice` ou `probl` → `exercice`; `correction` ou `corrig` → `corrige`; `méthode` → `methode`; `définition`, `théorème` ou `propriété` → `cours`; `activit` → `activite`; sinon `autre`. La casse est abaissée une fois. Chaque retour construit un dictionnaire neuf afin qu’un appelant ne puisse muter la constante globale.

Appliquer ce seul comportement avec `apply_patch` sur `/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/nexus_external/classification.py`, puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_classification.py::test_local_heuristic_preserves_existing_chunk_type_contract
```

Expected: `1 passed`.

- [ ] **Step 3: Écrire le parseur distant pur et globalement conservateur**

`parse_remote_classification(content)` accepte soit un objet JSON nu après `strip()`, soit exactement un fence enveloppant composé de la ligne ```` ```json ````, du corps JSON, puis de la ligne ```` ``` ```` sans texte avant/après ; aucun autre langage de fence n’est retiré. Exiger exactement les cinq clés ; refuser clé supplémentaire/manquante, enum inconnu, thème non chaîne/non-null, capacités non-liste ou élément non chaîne, difficulté hors 1/2/3/null et explicitement tout `bool`. Une seule anomalie retourne une copie de `CONSERVATIVE_CLASSIFICATION`, jamais les champs valides partiels.

Appliquer uniquement ce parseur pur par `apply_patch` sur le chemin absolu de classification, puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_classification.py::test_remote_classification_accepts_exact_closed_object \
  tests/test_openrouter_classification.py::test_remote_classification_rejects_invalid_closed_object_as_a_whole \
  tests/test_openrouter_classification.py::test_remote_classification_rejects_boolean_difficulty \
  tests/test_openrouter_classification.py::test_invalid_remote_classification_returns_global_conservative_result
```

Expected: `4 passed`.

- [ ] **Step 4: Écrire seulement l’intégration clé/modèle et prompt**

La signature est exactement `classify_chunk(chunk: str, *, environ: Mapping[str, str], transport: httpx.BaseTransport | None = None) -> dict[str, object]`.

Lire seulement `OPENROUTER_API_KEY` et `OPENROUTER_MODEL` depuis la vue injectée. Sans clé : heuristique et zéro appel. Clé présente/modèle vide : `OpenRouterError(category="configuration", model="")` avant transport. Clé+modèle : un appel `chat_completion`, modèle exact, fragment `chunk[:3000]`, limite 200. Les messages contiennent exactement un objet rôle `user` dont le contenu est la chaîne statique de classification déjà présente dans l’ingestion, suivie de `\n\nFRAGMENT:\n` et du fragment tronqué ; aucun message system, environnement, chemin, URL, hash ou métadonnée n’est ajouté.

Appliquer uniquement cette orchestration avec `apply_patch` sur le chemin absolu de classification, puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_classification.py::test_classification_without_key_uses_local_heuristic_without_transport \
  tests/test_openrouter_classification.py::test_classification_with_key_without_model_fails_before_transport \
  tests/test_openrouter_classification.py::test_classification_with_key_and_model_forwards_exact_model \
  tests/test_openrouter_classification.py::test_classification_sends_only_first_3000_fragment_characters \
  tests/test_openrouter_classification.py::test_classification_requests_200_completion_tokens \
  tests/test_openrouter_classification.py::test_prompt_does_not_append_environment_or_provenance_metadata
```

Expected: `6 passed`.

- [ ] **Step 5: Fermer l’intégration classification/métadonnées**

Par `apply_patch` sur le même chemin absolu, s’assurer que le dictionnaire distant validé reste neuf et ne transporte aucune métadonnée source. Puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_classification.py::test_remote_metadata_cannot_override_trusted_record_fields
```

Expected: `1 passed`.

- [ ] **Step 6: Passer la classification et les non-régressions client**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_client.py \
  tests/test_openrouter_classification.py
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m ruff check nexus_external
```

Expected: client et classification verts. Revue spécification puis revue qualité par deux agents frais avant Task 10.

### Task 10: Migrer les deux ingestions et préserver leurs commandes

**Files:**

- Modify: `Mathematiques/manuel-maths/scripts/ingest.py`
- Modify: `NSI/scripts/ingest.py`
- Test: les deux `tests/test_ingest_openrouter.py`

- [ ] **Step 1: Confier les deux adaptateurs identiques à un implementer frais**

L’agent relit `AGENTS.md`, les deux scripts complets et reproduit séparément les deux Reds. Il n’ajoute pas de troisième abstraction ni de cible Makefile.

- [ ] **Step 2: Ajouter la découverte déterministe à l’adaptateur Mathématiques**

Utiliser `apply_patch` sur le chemin absolu `/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/Mathematiques/manuel-maths/scripts/ingest.py`. Avant import de `nexus_external`, appliquer cette logique locale minimale :

```python
def _discover_checkout_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("checkout Git Nexus introuvable depuis __file__")


CHECKOUT_ROOT = _discover_checkout_root()
root_text = str(CHECKOUT_ROOT)
sys.path[:] = [item for item in sys.path if item != root_text]
sys.path.insert(0, root_text)
import nexus_external  # noqa: E402

expected_package = (CHECKOUT_ROOT / "nexus_external").resolve()
loaded_package = Path(nexus_external.__file__).resolve().parent
if loaded_package != expected_package:
    raise RuntimeError("nexus_external chargé hors du checkout courant")
```

Si `nexus_external` est déjà présent dans `sys.modules` depuis un autre chemin, l’import puis la vérification échouent ; ne pas supprimer silencieusement ce module pour contourner l’empoisonnement.

- [ ] **Step 3: Passer les trois nodes de provenance Mathématiques**

```bash
set -euo pipefail
MATH_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/Mathematiques/manuel-maths
cd "$MATH_ROOT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_ingest_openrouter.py::test_math_ingest_discovers_current_checkout_from_unrelated_cwd \
  tests/test_ingest_openrouter.py::test_math_ingest_prioritizes_current_checkout_over_shadow_package \
  tests/test_ingest_openrouter.py::test_math_ingest_rejects_nexus_external_loaded_outside_checkout
```

Expected: trois verts avant de toucher à NSI.

- [ ] **Step 4: Ajouter puis tester seulement la provenance NSI**

Appliquer exactement la logique Step 2 avec `apply_patch` sur `/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/scripts/ingest.py`, puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_ingest_openrouter.py::test_nsi_ingest_discovers_current_checkout_from_unrelated_cwd \
  tests/test_ingest_openrouter.py::test_nsi_ingest_prioritizes_current_checkout_over_shadow_package \
  tests/test_ingest_openrouter.py::test_nsi_ingest_rejects_nexus_external_loaded_outside_checkout
```

Expected: `3 passed`.

- [ ] **Step 5: Déléguer `classify()` dans l’adaptateur Mathématiques**

Avec `apply_patch` sur le chemin Mathématiques absolu, `classify(chunk)` appelle `classify_chunk(chunk, environ=os.environ)`. Dans `ingest_source`, construire explicitement :

```python
classification = classify(chunk)
record = {
    "chunk_type": classification["chunk_type"],
    "niveau": classification["niveau"],
    "theme": classification["theme"],
    "capacites": classification["capacites"],
    "difficulte": classification["difficulte"],
    "source_id": source["id"],
    "doc_url": entry["url"],
    "doc_hash": entry["hash"],
    "content_md": chunk,
    "usage_policy": source["usage_policy"],
    "tier": source["tier"],
}
```

Ainsi, même un double de test hostile ne peut écraser les six métadonnées de confiance.

- [ ] **Step 6: Passer délégation et métadonnées Mathématiques**

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/Mathematiques/manuel-maths
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_ingest_openrouter.py::test_math_ingest_classify_delegates_to_shared_classifier \
  tests/test_ingest_openrouter.py::test_math_ingest_preserves_trusted_metadata_against_hostile_classifier
```

Expected: `2 passed`.

- [ ] **Step 7: Déléguer et tester `classify()` dans l’adaptateur NSI**

Appliquer le même dictionnaire explicite avec `apply_patch` au chemin NSI absolu, puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_ingest_openrouter.py::test_nsi_ingest_classify_delegates_to_shared_classifier \
  tests/test_ingest_openrouter.py::test_nsi_ingest_preserves_trusted_metadata_against_hostile_classifier
```

Expected: `2 passed`.

- [ ] **Step 8: Rendre les imports d’extraction Mathématiques paresseux**

Avec `apply_patch` sur le chemin Mathématiques absolu, retirer `fitz` et `trafilatura` du niveau module. Dans `extract_text`, importer `fitz` seulement pour `.pdf` et `trafilatura` seulement pour HTML. Neutraliser dans les docstrings actives les promesses Haiku/Claude : `latex_fallback()` reste une extension locale non implémentée. Puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/Mathematiques/manuel-maths
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_ingest_openrouter.py::test_math_no_source_command_does_not_import_extraction_backends
```

Expected: `1 passed`.

- [ ] **Step 9: Rendre les imports d’extraction NSI paresseux**

Appliquer la même modification au chemin NSI absolu, puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_ingest_openrouter.py::test_nsi_no_source_command_does_not_import_extraction_backends
```

Expected: `1 passed`.

- [ ] **Step 10: Passer les deux processus et commandes sans source**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT/Mathematiques/manuel-maths"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider tests/test_ingest_openrouter.py
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL make ingest
cd "$IMPL_ROOT/NSI"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider tests/test_ingest_openrouter.py
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL python3 scripts/ingest.py
```

Expected: deux suites vertes ; commandes terminent sans source, clé, backend d’extraction ni réseau. Faire suivre par une revue spécification et une revue qualité distinctes.

## Chunk 7: Green des juges, de la configuration et du commit de production

### Task 11: Migrer les deux juges et neutraliser le pré-jugement

**Files:**

- Modify: `NSI/corpus_nsi/scripts/judge_campaign.py`
- Modify: `NSI/corpus_nsi/scripts/substance_judge.py`
- Modify: `NSI/corpus_nsi/scripts/run_substance_judge.py`
- Test: `NSI/corpus_nsi/tests/test_openrouter_judges.py`
- Test: six tests corpus historiques ciblés

- [ ] **Step 1: Confier ce Task à un implementer corpus frais**

L’agent relit intégralement les deux `AGENTS.md`, maintient `CORPUS_ROOT` distinct de `CHECKOUT_ROOT`, et reproduit le Red corpus. Aucun fichier sous `substance_reviews/` n’est ouvert en écriture pendant les tests.

- [ ] **Step 2: Installer seulement la provenance de `judge_campaign.py`**

Utiliser `apply_patch` sur `/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi/scripts/judge_campaign.py`. Conserver :

```python
CORPUS_ROOT = Path(__file__).resolve().parents[1]
```

Chercher `CHECKOUT_ROOT` dans les parents jusqu’au premier `.git.exists()`, le placer en tête de `sys.path`, importer et vérifier `nexus_external` exactement sous cette racine. Ensuite retirer les deux chemins et réinsérer `CORPUS_ROOT` à l’index 0 et `CHECKOUT_ROOT` à l’index 1 avant les imports `scripts.*`. Ainsi le paquet externe provient du checkout et les modules métier du corpus. `ROOT = CORPUS_ROOT`. Puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_judges.py::test_campaign_discovers_current_checkout_from_unrelated_cwd
```

Expected: `1 passed`; le node de shadow commun couvre les deux appelants et attend donc la migration de `substance_judge.py` à l'étape suivante.

- [ ] **Step 3: Installer seulement la provenance de `substance_judge.py`**

Appliquer la même séquence avec `apply_patch` sur `/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi/scripts/substance_judge.py`, puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_judges.py::test_substance_discovers_current_checkout_from_unrelated_cwd \
  tests/test_openrouter_judges.py::test_corpus_callers_reject_shadowed_external_package
```

Expected: `2 passed`.

- [ ] **Step 4: Écrire seulement le chargeur de configuration campagne**

Par `apply_patch` sur le chemin campagne absolu, ajouter un parseur local des lignes `KEY=value` de la seule valeur retournée par `resolve_env_file(CORPUS_ROOT)`. `load_openrouter_config(environ, env_path)` lit d’abord chaque valeur non blanche dans `environ`; le fichier remplit seulement une valeur absente/blanche, clé par clé. Il ignore toute autre clé et ne lit jamais `.env`. Retour exact `(api_key, model)` ; clé présente/modèle blanc lève `OpenRouterError(configuration)` avant transport. Puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_judges.py::test_campaign_reads_missing_openrouter_values_from_resolved_rag_env \
  tests/test_openrouter_judges.py::test_campaign_does_not_read_generic_dotenv \
  tests/test_openrouter_judges.py::test_campaign_rejects_key_without_model_before_transport
```

Expected: `3 passed`.

- [ ] **Step 5: Implémenter seulement le transport campagne**

La signature exacte est :

```python
def call_openrouter_judge(
    api_key: str,
    model: str,
    seq_context: str,
    capacity_prompt: str,
    *,
    transport: httpx.BaseTransport | None = None,
) -> OpenRouterCompletion:
```

Par `apply_patch` sur le chemin campagne absolu, construire deux messages : `SYSTEM_TEXT` en rôle `system`; un rôle `user` égal à `seq_context + "\n\n" + capacity_prompt` quand le contexte existe, sinon le prompt. Appeler `chat_completion` avec les clé, modèle, messages et transport reçus, et `max_completion_tokens=2500`. `call_openrouter_judge` retourne la `OpenRouterCompletion` brute validée au niveau transport : aucun parsing, retry, journal ou calcul de coût dans ce helper. Puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_judges.py::test_campaign_delegates_to_shared_openrouter_client \
  tests/test_openrouter_judges.py::test_campaign_records_requested_openrouter_model
```

Expected: `2 passed`; le modèle demandé est propagé sans substitution.

- [ ] **Step 6: Implémenter seulement les builders d’usage v2**

Par `apply_patch` sur le chemin campagne absolu, créer exactement :

```python
def build_usage_v2(
    *, cap: str, seq: str, attempt: int, judged_at: str,
    completion: OpenRouterCompletion,
) -> dict[str, object]: ...


def build_failed_usage_v2(
    *, cap: str, seq: str, attempt: int, judged_at: str,
    model: str, error_category: str,
) -> dict[str, object]: ...
```

Le succès porte exactement les clés `schema_version`, `provider`, `cap`, `seq`, `attempt`, `judged_at`, `model`, `generation_id`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `cached_tokens`, `cache_write_tokens`, `cost_usd`, avec `schema_version == 2`, `provider == "openrouter"` et toutes les valeurs comptables copiées directement de la complétion. L'échec porte exactement `schema_version`, `provider`, `cap`, `seq`, `attempt`, `judged_at`, `model`, `error_category` et n'invente ni génération, ni token, ni coût. `test_usage_v2_copies_completion_accounting_exactly` et `test_failed_usage_entry_invents_no_accounting` assertent l'égalité exacte de ces ensembles de clés, pas seulement leur sous-ensemble. Aucun tarif local. Puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_judges.py::test_usage_v2_copies_completion_accounting_exactly \
  tests/test_openrouter_judges.py::test_usage_logging_contains_no_local_cost_formula \
  tests/test_openrouter_judges.py::test_failed_usage_entry_invents_no_accounting
```

Expected: `3 passed`.

- [ ] **Step 7: Implémenter seulement fusion et totaux du journal**

Par `apply_patch` sur le chemin campagne absolu, ajouter `merge_usage_log` puis exactement :

```python
def current_run_totals(
    current_entries: Sequence[Mapping[str, object]],
) -> dict[str, int | float]: ...
```

`merge_usage_log` préserve profondément et dans l’ordre toute ligne v1, remplace seulement la même `generation_id` v2, préserve les autres générations et ajoute les nouvelles dans l’ordre. `current_run_totals` reçoit uniquement la liste en mémoire des entrées de succès v2 produites pendant l'invocation courante ; il ne relit jamais le journal fusionné et ne filtre pas sur un champ `run_id` inexistant. Il somme les cinq compteurs de tokens et `cost_usd` de cet argument fermé. Puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_judges.py::test_usage_upsert_replaces_same_generation_only \
  tests/test_openrouter_judges.py::test_usage_upsert_preserves_v1_deeply_and_in_order \
  tests/test_openrouter_judges.py::test_usage_upsert_preserves_other_v2_generations_for_same_capacity \
  tests/test_openrouter_judges.py::test_run_totals_sum_only_current_successful_v2_entries
```

Expected: `4 passed`.

- [ ] **Step 8: Isoler seulement le parseur pur de verdict campagne**

Par `apply_patch` sur le chemin campagne absolu, extraire un parseur pur qui reçoit `completion.content` et retourne le verdict validé ou un échec métier, sans transport, attente, journalisation ou mutation de fichier. Il ne peut ni consommer ni perdre la `OpenRouterCompletion`. Conserver les invariants historiques de verdict et les parseurs existants ; aucune tolérance JSON nouvelle. Puis exécuter le node d’import/transport scellé, seul node Red qui puisse rester vert avant l’orchestration :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_judges.py::test_campaign_delegates_to_shared_openrouter_client
```

Expected: `1 passed`; l’extraction du parseur ne contamine pas le helper transport. Le comportement du parseur est volontairement scellé par le node d’intégration exact de Step 9, sans ajouter ni modifier de test Green.

- [ ] **Step 9: Intégrer seulement journal immédiat et retry métier**

Par `apply_patch` sur le chemin campagne absolu, initialiser une liste locale `current_entries` au début de l'invocation, faire recevoir au `main` chaque `OpenRouterCompletion`, construire son usage v2, l'ajouter immédiatement à cette liste et le fusionner au journal, puis seulement appeler le parseur pur de Step 8. Un verdict invalide déclenche au plus un second appel logique : la première génération facturée et la seconde restent toutes deux journalisées avant la décision. Les totaux finaux reçoivent exclusivement `current_entries`, jamais le journal historique fusionné. Puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_judges.py::test_campaign_records_each_billed_retry_generation_before_verdict_validation
```

Expected: `1 passed`; l’invalidation du premier verdict ne perd ni sa génération ni son coût, et le second est également préservé.

- [ ] **Step 10: Borner seulement les retries de transport**

Par `apply_patch` sur le chemin campagne absolu, envelopper un appel logique sans modifier son parseur : au maximum trois transports, indices 1, 2, 3, avec délais injectables `[0, 2, 4]` secondes avant les tentatives correspondantes. Seules les catégories `rate_limit`, `timeout`, `transport`, `unavailable` sont retentées ; les autres échouent immédiatement. Avec les deux appels logiques maximum de Step 8, le plafond absolu est six complétions. Puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_judges.py::test_campaign_business_retry_count_is_bounded
```

Expected: `1 passed`; le plafond transport/métier est prouvé sans redéplacer le parsing dans le helper réseau.

- [ ] **Step 11: Propager seulement le modèle explicite au verdict campagne**

Par `apply_patch` sur le chemin campagne absolu, modifier `_write_verdict_json(path, cap_id, verdict, programme, *, judge_model)` et tous ses appels ; `judge_model` reçoit la valeur demandée `OPENROUTER_MODEL`, jamais le modèle observé ni une constante. Puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_judges.py::test_campaign_records_requested_openrouter_model
```

Expected: `1 passed`.

- [ ] **Step 12: Migrer seulement le transport LLM de `substance_judge.py`**

Conserver `_http_json()` et `search_rag()` sur `RAG_API_BASE_URL` et `RAG_API_KEY`. Par `apply_patch` sur le chemin substance absolu, `call_llm(env, capacity_text, section_text, role_label, *, transport=None)` lit les deux variables OpenRouter dans `env`, retourne exactement `{"taught": False, "citation": "", "justification": "LLM non configuré"}` sans clé et zéro transport, refuse clé sans modèle, puis appelle le client partagé avec exactement deux messages. Le system reste byte-identique à la valeur actuelle de `JUDGE_SYSTEM_PROMPT`. Le user reste byte-identique au template actuel : `Capacité NSI : "{capacity_text}"\nRôle : {role_label}\n\nExtrait :\n---\n{section_text[:800]}\n---\n\nCette section {role_label}-t-elle cette capacité ?`. Aucun environnement ni provenance n’est ajouté. Le modèle est exactement la valeur fixe demandée par `OPENROUTER_MODEL` pour cet appel et `max_completion_tokens=800`. Puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_judges.py::test_substance_llm_delegates_to_shared_openrouter_client \
  tests/test_openrouter_judges.py::test_substance_without_key_returns_conservative_result_without_transport \
  tests/test_openrouter_judges.py::test_substance_rejects_key_without_model_before_transport \
  tests/test_openrouter_judges.py::test_substance_sends_exact_bounded_prompt_and_limit
```

Expected: `4 passed`.

- [ ] **Step 13: Fermer seulement le parseur substance**

Par `apply_patch` sur le chemin substance absolu, le parseur pur accepte seulement un JSON nu après `strip()` ou un unique fence dont les lignes d’ouverture/fermeture sont exactement ```` ```json ```` et ```` ``` ````, sans texte périphérique. Exiger exactement `taught` booléen, `citation` chaîne, `justification` chaîne ; refuser clés supplémentaires, types et tout autre fence par verdict conservateur expurgé. L’erreur distante utilise uniquement sa catégorie. Supprimer `LOCAL_LLM_*`, qwen et URL LLM ; ne pas réutiliser OpenRouter pour le RAG. Puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_judges.py::test_substance_accepts_only_exact_closed_json_object
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_judges.py::test_substance_rag_keeps_dedicated_http_transport \
  tests/test_openrouter_judges.py::test_substance_has_no_configurable_llm_endpoint \
  tests/test_openrouter_judges.py::test_substance_remote_error_is_sanitized_and_never_promotes
```

Expected: parseur pur `1 passed`, puis intégration RAG/erreur `3 passed` ; chaque comportement reste prouvé par son processus exact.

- [ ] **Step 14: Rendre seulement `run_substance_judge.py` honnêtement déterministe**

Par `apply_patch` sur `/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi/scripts/run_substance_judge.py`, faire décrire à la docstring un pré-jugement local sans appel modèle. Retirer Anthropic et tout fournisseur. Conserver l’option `--model` pour compatibilité CLI avec défaut exact `deterministic-prejudge`; `judge_model` reçoit cette valeur. Le fichier n’importe ni `nexus_external`, ni client HTTP. Puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_judges.py::test_run_substance_judge_imports_no_external_client \
  tests/test_openrouter_judges.py::test_run_substance_judge_uses_honest_deterministic_model
```

Expected: `2 passed`.

- [ ] **Step 15: Passer le corpus ciblé sans réseau**

```bash
set -euo pipefail
CORPUS_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
cd "$CORPUS_ROOT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
    tests/test_rag_governance_and_indexes.py \
    tests/test_secret_guard.py \
    tests/test_openrouter_judges.py \
    tests/test_substance_judge_pipeline.py \
    tests/test_substance_hardened.py \
    tests/test_judge_collection_barriers.py \
    tests/test_policy_checker_ast.py
```

Expected: tous les tests verts, fixture autouse bloquant socket/urllib toujours active, aucune écriture de verdict suivi. Revue spécification puis qualité distinctes avant Task 12.

### Task 12: Fermer configuration et dépendances actives

**Files:**

- Modify: `Mathematiques/manuel-maths/.env.example`
- Modify: `NSI/.env.example`
- Modify: `NSI/corpus_nsi/.env.rag.example`
- Modify: `NSI/corpus_nsi/rag_config.example.yml`
- Modify: `Mathematiques/manuel-maths/requirements.txt`
- Modify: `NSI/requirements.txt`
- Modify: `NSI/corpus_nsi/requirements.txt`
- Modify: `requirements-ci-audit.txt`
- Modify: `NSI/corpus_nsi/scripts/check_rag_config.py`
- Test: `tests/test_external_provider_policy.py`
- Test: `NSI/corpus_nsi/tests/test_rag_governance_and_indexes.py`
- Test: `NSI/corpus_nsi/tests/test_secret_guard.py`

- [ ] **Step 1: Confier configuration et pins à un implementer frais**

Le mandat interdit Makefiles, workflows, `QUALITY_GATES` et `CI_AUDIT`. L’agent reproduit les nodes de policy/config rouges restants.

- [ ] **Step 2: Retirer seulement le fournisseur direct des surfaces manuelles**

Utiliser `apply_patch` sur les chemins absolus de `Mathematiques/manuel-maths/.env.example`, `NSI/.env.example`, `Mathematiques/manuel-maths/requirements.txt` et `NSI/requirements.txt`. Dans les deux exemples, écrire exactement des valeurs vides :

```dotenv
OPENROUTER_API_KEY=
OPENROUTER_MODEL=
```

Retirer `ANTHROPIC_API_KEY` et les deux occurrences `anthropic>=0.40`. Préserver `DATABASE_URL`, embedding et toutes les autres dépendances/variables. Puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_external_provider_policy.py::test_policy_rejects_anthropic_in_active_callers
```

Expected: `1 passed` ; les historiques protégés ne sont pas scannés par ce node.

- [ ] **Step 3: Fermer seulement la configuration RAG/LLM du corpus**

Avec `apply_patch` sur les chemins absolus `NSI/corpus_nsi/.env.rag.example`, `NSI/corpus_nsi/rag_config.example.yml` et `NSI/corpus_nsi/scripts/check_rag_config.py`, remplacer `LOCAL_LLM_*` par `OPENROUTER_API_KEY=` et `OPENROUTER_MODEL=`. Préserver `RAG_API_BASE_URL`, embedding, vector DB et SSH. Dans YAML, supprimer `llm` sans créer `external_llm` ni endpoint OpenRouter.

Dans le checker, `EXPECTED_ENV` attend les deux clés OpenRouter vides. `validate_env_example()` exige que la clé reste vide et refuse explicitement les quatre anciens littéraux `LOCAL_LLM_*`, unique exception du denylist car elle matérialise leur rejet. `validate_yaml()` refuse `llm`, `external_llm` et toute valeur d’endpoint chat/messages/completions, tout en conservant les validations RAG. Puis :

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_rag_governance_and_indexes.py::test_rag_env_example_uses_internal_corpus_without_real_secret \
  tests/test_rag_governance_and_indexes.py::test_rag_config_and_smoke_scripts_are_safe_without_local_config
```

Expected: `2 passed`. La commande `python3 -m scripts.check_rag_config` est couverte par le second node et sera rejouée au final sous garde réseau.

- [ ] **Step 4: Fermer seulement les pins HTTP statiques**

Avec `apply_patch` sur les chemins absolus `NSI/corpus_nsi/requirements.txt` et `requirements-ci-audit.txt`, ajouter exactement `httpx==0.28.1` une fois au corpus et les pins racine suivants en conservant `typing_extensions==4.15.0` :

```text
anyio==4.9.0
certifi==2026.7.22
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
idna==3.6
sniffio==1.3.1
```

Ne pas laisser un second pin contradictoire et ne pas ajouter de SDK LLM. La preuve est exclusivement statique : aucun `pip check`, aucune métadonnée de l’environnement Python global, aucun install.

```bash
set -euo pipefail
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_external_provider_policy.py::test_ci_no_deps_requirements_close_httpx_runtime_dependencies
```

Expected: `1 passed` par lecture des fichiers suivis seulement.

- [ ] **Step 5: Passer policy, configuration et analyse statique affectée**

Sans `apply_patch` supplémentaire, fermer d'abord l'allowlist Green et l'indexer : `test_policy_requires_every_canonical_active_surface` exige à juste titre que les trois nouveaux modules soient visibles par `git ls-files`, ce qui n'est vrai qu'après `git add`. L'index doit être vide avant cette opération et contenir ensuite exactement les 17 chemins Green, sans changement non indexé. Exécuter alors le bloc autonome de preuve des seules productions/configurations. Ne pas exiger les deux nodes d’autorités Chutes avant le commit DOCS du chunk suivant.

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
CORPUS_ROOT=$IMPL_ROOT/NSI/corpus_nsi
cd "$IMPL_ROOT"
test -z "$(git diff --cached --name-only)"
git add -- \
  nexus_external/__init__.py \
  nexus_external/openrouter_client.py \
  nexus_external/classification.py \
  Mathematiques/manuel-maths/scripts/ingest.py \
  NSI/scripts/ingest.py \
  NSI/corpus_nsi/scripts/judge_campaign.py \
  NSI/corpus_nsi/scripts/substance_judge.py \
  NSI/corpus_nsi/scripts/run_substance_judge.py \
  NSI/corpus_nsi/scripts/check_rag_config.py \
  Mathematiques/manuel-maths/.env.example \
  NSI/.env.example \
  NSI/corpus_nsi/.env.rag.example \
  NSI/corpus_nsi/rag_config.example.yml \
  Mathematiques/manuel-maths/requirements.txt \
  NSI/requirements.txt \
  NSI/corpus_nsi/requirements.txt \
  requirements-ci-audit.txt
test -z "$(git diff --name-only)"
python3 - <<'PY'
import subprocess
expected = {
    "nexus_external/__init__.py",
    "nexus_external/openrouter_client.py",
    "nexus_external/classification.py",
    "Mathematiques/manuel-maths/scripts/ingest.py",
    "NSI/scripts/ingest.py",
    "NSI/corpus_nsi/scripts/judge_campaign.py",
    "NSI/corpus_nsi/scripts/substance_judge.py",
    "NSI/corpus_nsi/scripts/run_substance_judge.py",
    "NSI/corpus_nsi/scripts/check_rag_config.py",
    "Mathematiques/manuel-maths/.env.example",
    "NSI/.env.example",
    "NSI/corpus_nsi/.env.rag.example",
    "NSI/corpus_nsi/rag_config.example.yml",
    "Mathematiques/manuel-maths/requirements.txt",
    "NSI/requirements.txt",
    "NSI/corpus_nsi/requirements.txt",
    "requirements-ci-audit.txt",
}
actual = set(subprocess.check_output(
    ["git", "diff", "--cached", "--name-only"], text=True
).splitlines())
assert actual == expected, (actual - expected, expected - actual)
PY
git diff --cached --check
cd "$CORPUS_ROOT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL python3 -m scripts.check_rag_config
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
    tests/test_rag_governance_and_indexes.py \
    tests/test_secret_guard.py
cd "$IMPL_ROOT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL python3 -m pytest -q -p no:cacheprovider \
  tests/test_external_provider_policy.py::test_policy_requires_every_canonical_active_surface \
  tests/test_external_provider_policy.py::test_policy_rejects_unlisted_provider_transport \
  tests/test_external_provider_policy.py::test_policy_allows_only_openrouter_client_to_define_llm_endpoint \
  tests/test_external_provider_policy.py::test_policy_preserves_non_llm_rag_transport_allowlist \
  tests/test_external_provider_policy.py::test_policy_rejects_model_catalog_endpoint_in_automation \
  tests/test_external_provider_policy.py::test_policy_rejects_new_nsi_ingest_make_target \
  tests/test_external_provider_policy.py::test_targeted_surfaces_exist_before_negative_scans \
  tests/test_external_provider_policy.py::test_policy_rejects_anthropic_in_active_callers \
  tests/test_external_provider_policy.py::test_policy_rejects_local_llm_configuration_in_active_surfaces
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m ruff check \
  nexus_external \
  Mathematiques/manuel-maths/scripts/ingest.py \
  NSI/scripts/ingest.py \
  NSI/corpus_nsi/scripts/judge_campaign.py \
  NSI/corpus_nsi/scripts/substance_judge.py \
  NSI/corpus_nsi/scripts/run_substance_judge.py \
  NSI/corpus_nsi/scripts/check_rag_config.py
```

Expected: 17 chemins Green explicitement indexés, puis gates verts. Faire relire le staged diff par un reviewer spécification et un reviewer qualité distincts ; toute correction est réindexée sur la même allowlist avant Task 13.

### Task 13: Vérifier et committer tout le Green de production

**Files:** toutes les productions/configurations/requirements des Tasks 8 à 12 ; aucun document §8.4 ni inventaire généré.

- [ ] **Step 1: Exécuter les quatre processus Pytest séparés**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
test -z "$(git diff --name-only)"
test "$(git diff --cached --name-only | wc -l)" -eq 17
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_client.py \
  tests/test_openrouter_classification.py \
  tests/test_external_provider_policy.py::test_policy_requires_every_canonical_active_surface \
  tests/test_external_provider_policy.py::test_policy_rejects_unlisted_provider_transport \
  tests/test_external_provider_policy.py::test_policy_allows_only_openrouter_client_to_define_llm_endpoint \
  tests/test_external_provider_policy.py::test_policy_preserves_non_llm_rag_transport_allowlist \
  tests/test_external_provider_policy.py::test_policy_rejects_model_catalog_endpoint_in_automation \
  tests/test_external_provider_policy.py::test_policy_rejects_new_nsi_ingest_make_target \
  tests/test_external_provider_policy.py::test_targeted_surfaces_exist_before_negative_scans \
  tests/test_external_provider_policy.py::test_policy_rejects_anthropic_in_active_callers \
  tests/test_external_provider_policy.py::test_policy_rejects_local_llm_configuration_in_active_surfaces
cd "$IMPL_ROOT/Mathematiques/manuel-maths"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider tests/test_ingest_openrouter.py
cd "$IMPL_ROOT/NSI"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider tests/test_ingest_openrouter.py
cd "$IMPL_ROOT/NSI/corpus_nsi"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
    tests/test_rag_governance_and_indexes.py \
    tests/test_secret_guard.py \
    tests/test_openrouter_judges.py \
    tests/test_substance_judge_pipeline.py \
    tests/test_substance_hardened.py \
    tests/test_judge_collection_barriers.py \
    tests/test_policy_checker_ast.py
```

Expected: quatre processus verts. Ne pas agréger le corpus au Pytest racine et ne pas prétendre la collecte globale verte tant que la collision historique `assemble.BOOK_VARIANTS` existe.

- [ ] **Step 2: Compiler et scanner les surfaces actives**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m py_compile \
  nexus_external/__init__.py \
  nexus_external/openrouter_client.py \
  nexus_external/classification.py \
  Mathematiques/manuel-maths/scripts/ingest.py \
  NSI/scripts/ingest.py \
  NSI/corpus_nsi/scripts/judge_campaign.py \
  NSI/corpus_nsi/scripts/substance_judge.py \
  NSI/corpus_nsi/scripts/run_substance_judge.py \
  NSI/corpus_nsi/scripts/check_rag_config.py
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m ruff check \
  nexus_external \
  Mathematiques/manuel-maths/scripts/ingest.py \
  NSI/scripts/ingest.py \
  NSI/corpus_nsi/scripts/judge_campaign.py \
  NSI/corpus_nsi/scripts/substance_judge.py \
  NSI/corpus_nsi/scripts/run_substance_judge.py \
  NSI/corpus_nsi/scripts/check_rag_config.py
```

Expected: syntaxe et Ruff verts. Les éventuels `__pycache__` sont ignorés et ne sont pas ajoutés.

- [ ] **Step 3: Vérifier l’allowlist Green exacte**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 - <<'PY'
import subprocess

allowed = {
    "nexus_external/__init__.py",
    "nexus_external/openrouter_client.py",
    "nexus_external/classification.py",
    "Mathematiques/manuel-maths/scripts/ingest.py",
    "NSI/scripts/ingest.py",
    "NSI/corpus_nsi/scripts/judge_campaign.py",
    "NSI/corpus_nsi/scripts/substance_judge.py",
    "NSI/corpus_nsi/scripts/run_substance_judge.py",
    "NSI/corpus_nsi/scripts/check_rag_config.py",
    "Mathematiques/manuel-maths/.env.example",
    "NSI/.env.example",
    "NSI/corpus_nsi/.env.rag.example",
    "NSI/corpus_nsi/rag_config.example.yml",
    "Mathematiques/manuel-maths/requirements.txt",
    "NSI/requirements.txt",
    "NSI/corpus_nsi/requirements.txt",
    "requirements-ci-audit.txt",
}
lines = subprocess.check_output(["git", "status", "--porcelain=v1"], text=True).splitlines()
paths = {line[3:] for line in lines}
assert paths == allowed, (paths - allowed, allowed - paths)
PY
git diff --check
git diff --cached --check
git diff --cached --stat
```

Expected: exactement 17 fichiers Green déjà indexés ; aucun changement non indexé, test réécrit après Red, document actif, Makefile, workflow ou inventaire.

- [ ] **Step 4: Réaffirmer l’allowlist Green et inspecter le staged diff**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
test -z "$(git diff --name-only)"
git add -- \
  nexus_external/__init__.py \
  nexus_external/openrouter_client.py \
  nexus_external/classification.py \
  Mathematiques/manuel-maths/scripts/ingest.py \
  NSI/scripts/ingest.py \
  NSI/corpus_nsi/scripts/judge_campaign.py \
  NSI/corpus_nsi/scripts/substance_judge.py \
  NSI/corpus_nsi/scripts/run_substance_judge.py \
  NSI/corpus_nsi/scripts/check_rag_config.py \
  Mathematiques/manuel-maths/.env.example \
  NSI/.env.example \
  NSI/corpus_nsi/.env.rag.example \
  NSI/corpus_nsi/rag_config.example.yml \
  Mathematiques/manuel-maths/requirements.txt \
  NSI/requirements.txt \
  NSI/corpus_nsi/requirements.txt \
  requirements-ci-audit.txt
git diff --cached --check
git diff --cached --stat
```

Expected: 17 fichiers indexés, aucune vraie clé, endpoint fournisseur direct, `LOCAL_LLM_*` ou prix local.

- [ ] **Step 5: Lancer la revue holistique Green avant commit**

Un reviewer spécification frais vérifie les cinq propriétés de la section 15, puis un reviewer qualité frais cherche fuite de secret, erreur de provenance, transport RAG détourné, coût recalculé, réponse partielle acceptée ou test affaibli. Corriger seulement les constats validés. Réindexer explicitement les 17 chemins Green après correction, exiger `git diff --name-only` vide (zéro changement non indexé), rejouer immédiatement les quatre processus, `py_compile`, Ruff et `git diff --cached --check`. `HARD STOP` si un reviewer a modifié un test Red ou un chemin hors allowlist.

- [ ] **Step 6: Committer le Green minimal**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
test -z "$(git diff --name-only)"
git diff --cached --check
git commit -m "[PYTHON] centralise les appels LLM via OpenRouter"
git status --short
test -z "$(git status --short)"
```

Expected: commit Green atomique après le commit Red, worktree propre. Les sorties d’inventaire restent volontairement périmées jusqu’au commit Audit dédié.

## Chunk 8: Autorités actives et inventaire canonique du corpus

### Task 14: Aligner les quatre autorités sans falsifier l’historique

**Files:**

- Modify: `AGENTS.md`
- Modify: `.agents/skills/nexus-manual-quality/SKILL.md`
- Modify: `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md`
- Modify: `README.md`
- Test: `tests/test_external_provider_policy.py`

- [ ] **Step 1: Confier les autorités à un implementer documentaire frais**

L’agent relit la section 8.4 et la section 9 de la spécification, puis les quatre documents complets. Il reproduit uniquement `test_policy_rejects_chutes_in_active_authority` rouge. Il ne modifie aucun audit daté, ancien plan, ancienne spécification ou fichier sous `docs/codex/`.

- [ ] **Step 2: Remplacer la règle active Chutes dans `AGENTS.md`**

Utiliser `apply_patch` sur `/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/AGENTS.md`. Le bloc actif prescrit :

- OpenRouter est l’unique destination LLM externe ;
- endpoint exact et variables `OPENROUTER_API_KEY`/`OPENROUTER_MODEL` ;
- absence de clé = mode local déterministe quand disponible ; clé sans modèle = erreur ;
- aucun secret ni donnée personnelle, vérification locale et caractère consultatif ;
- aucune nouvelle consultation Chutes ; anciennes preuves sous `audit/chutes/` immuables ; nouvelles preuves optionnelles sous `audit/openrouter/` ;
- smoke humain uniquement, jamais automatique ni en CI.

Ne pas changer la hiérarchie d’autorité, le `NO-GO`, les gates, les règles Git ou les P0.

- [ ] **Step 3: Aligner la skill sans déclencher de réseau automatique**

Dans `.agents/skills/nexus-manual-quality/SKILL.md`, remplacer l’étape active Chutes par une étape OpenRouter conditionnelle : une expertise externe n’est lancée que sur instruction humaine, avec modèle explicitement configuré et smoke séparé. Conserver reproduction locale, double revue, baseline et stop conditions.

- [ ] **Step 4: Aligner le cahier des charges par amendement explicite**

Dans `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md`, remplacer la prescription active de la section 14 et de l’annexe de démarrage. Mentionner que l’amendement du 13 août 2026 remplace les anciennes instructions Chutes pour les opérations futures, sans prétendre que les anciennes consultations utilisaient OpenRouter. Ne modifier aucun objectif éditorial ou critère de réalisation.

- [ ] **Step 5: Aligner le README autosuffisant**

Mettre à jour seulement les parties opératoires : configuration, architecture des appels externes, historique/traçabilité, état d’avancement et commandes hors réseau. Le README emploie uniquement la formulation durable : « OpenRouter est l’unique passerelle LLM externe active si et seulement si les cinq propriétés OpenRouter passent sur le SHA courant ». Il ne contient pas la phrase transitoire « migration en cours sur la branche dédiée ». Préserver les 67 bloqueurs, le `NO-GO` et les P0 ouverts.

- [ ] **Step 6: Passer la policy ciblée sur les quatre autorités**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
python3 -m pytest -q -p no:cacheprovider \
  tests/test_external_provider_policy.py::test_policy_rejects_chutes_in_active_authority \
  tests/test_external_provider_policy.py::test_policy_ignores_protected_historical_chutes_artifacts
```

Expected: les autorités actives passent, les catégories historiques restent volontairement ignorées par la migration textuelle et protégées par hash.

### Task 15: Aligner les guides opérationnels exacts de la section 8.4

**Files:** exactement `Mathematiques/PROMPT_MISSION_AUTONOME.md`, `Mathematiques/workflow_production_manuel.md`, `Mathematiques/manuel-maths/README.md`, `Mathematiques/manuel-maths/CAHIER_DES_CHARGES.md`, `Mathematiques/manuel-maths/docs/02_workflow_production.md`, `Mathematiques/manuel-maths/docs/03_architecture_technique.md`, `NSI/CAHIER_DES_CHARGES.md`, `NSI/docs/02_workflow_production.md`, `NSI/docs/03_architecture_technique.md`, `NSI/corpus_nsi/README.md`, `NSI/corpus_nsi/rag_connection.md`, `NSI/corpus_nsi/substance_pipeline.md`, `NSI/corpus_nsi/docs/enrichment_roadmap.md`.

- [ ] **Step 1: Aligner `Mathematiques/PROMPT_MISSION_AUTONOME.md`**

Un implementer documentaire frais modifie par `apply_patch` ce seul chemin absolu. Remplacer seulement les instructions actives de client, clé, modèle, endpoint ou consultation. Documenter le mode sans clé et l’absence de modèle par défaut. Ne promettre ni Batch API, remise, disponibilité permanente, vision différée ni validation disciplinaire par LLM.

- [ ] **Step 2: Aligner `Mathematiques/workflow_production_manuel.md`**

Modifier ce seul chemin par `apply_patch` absolu avec le même contrat.

- [ ] **Step 3: Aligner `Mathematiques/manuel-maths/README.md`**

Modifier ce seul chemin par `apply_patch` absolu ; conserver `make ingest`.

- [ ] **Step 4: Aligner `Mathematiques/manuel-maths/CAHIER_DES_CHARGES.md`**

Modifier ce seul chemin par `apply_patch` absolu ; aucune exigence scolaire ne change.

- [ ] **Step 5: Aligner `Mathematiques/manuel-maths/docs/02_workflow_production.md`**

Modifier ce seul chemin par `apply_patch` absolu ; distinguer classification, extraction et stockage.

- [ ] **Step 6: Aligner `Mathematiques/manuel-maths/docs/03_architecture_technique.md`**

Modifier ce seul chemin par `apply_patch` absolu avec la même séparation.

- [ ] **Step 7: Vérifier le delta des six guides Mathématiques**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
git diff -- \
  Mathematiques/PROMPT_MISSION_AUTONOME.md \
  Mathematiques/workflow_production_manuel.md \
  Mathematiques/manuel-maths/README.md \
  Mathematiques/manuel-maths/CAHIER_DES_CHARGES.md \
  Mathematiques/manuel-maths/docs/02_workflow_production.md \
  Mathematiques/manuel-maths/docs/03_architecture_technique.md
```

Expected: seulement prescriptions futures ; aucune preuve datée ou promesse métier réécrite.

- [ ] **Step 8: Aligner `NSI/CAHIER_DES_CHARGES.md`**

Un autre implementer modifie ce seul chemin par `apply_patch` absolu. Conserver les commandes NSI ; ne pas inventer `make ingest`. Distinguer appel LLM OpenRouter, extraction/embedding et RAG.

- [ ] **Step 9: Aligner `NSI/docs/02_workflow_production.md`**

Modifier ce seul chemin par `apply_patch` absolu avec le même contrat.

- [ ] **Step 10: Aligner `NSI/docs/03_architecture_technique.md`**

Modifier par `apply_patch` le chemin absolu `NSI/docs/03_architecture_technique.md`, puis vérifier le diff des trois guides NSI.

- [ ] **Step 11: Aligner `NSI/corpus_nsi/README.md`**

Le même implementer relit le proche `AGENTS.md`, puis modifie ce seul chemin par `apply_patch` absolu. Documenter `.env.rag`, les deux variables OpenRouter, la séparation `RAG_API_BASE_URL` et le mode conservateur sans clé.

- [ ] **Step 12: Aligner `NSI/corpus_nsi/rag_connection.md`**

Modifier ce seul chemin par `apply_patch` absolu avec le même contrat RAG/LLM.

- [ ] **Step 13: Aligner `NSI/corpus_nsi/substance_pipeline.md`**

Modifier ce seul chemin par `apply_patch` absolu ; documenter entrées v2 et non-promotion.

- [ ] **Step 14: Aligner `NSI/corpus_nsi/docs/enrichment_roadmap.md`**

Modifier obligatoirement ce seul chemin par `apply_patch` absolu ; la roadmap est prescriptive aux lignes observées 14 et 47. Documenter le workflow corpus dormant sans prétendre un branchement CI racine.

- [ ] **Step 15: Scanner les guides actifs et protéger les historiques**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
python3 -m pytest -q -p no:cacheprovider tests/test_external_provider_policy.py
git diff --check
```

Expected: policy complète verte ; des occurrences peuvent rester dans les catégories historiques exclues et ne constituent pas un échec.

### Task 16: Revoir et committer la documentation active

**Files:** exactement les quatre autorités de Task 14 et les treize chemins explicitement énumérés dans Task 15 ; aucun autre document.

- [ ] **Step 1: Confier la fermeture documentaire à un implementer frais**

Cet implementer n’a rédigé aucun des dix-sept deltas. Il relit la section 8.4, exige les commits Red et Green comme parents, puis assume seulement l’allowlist, les deux revues et le commit documentaire de ce Task.

- [ ] **Step 2: Vérifier l’allowlist documentaire**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
python3 - <<'PY'
import subprocess

allowed = {
    "AGENTS.md",
    ".agents/skills/nexus-manual-quality/SKILL.md",
    "CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md",
    "README.md",
    "Mathematiques/PROMPT_MISSION_AUTONOME.md",
    "Mathematiques/workflow_production_manuel.md",
    "Mathematiques/manuel-maths/README.md",
    "Mathematiques/manuel-maths/CAHIER_DES_CHARGES.md",
    "Mathematiques/manuel-maths/docs/02_workflow_production.md",
    "Mathematiques/manuel-maths/docs/03_architecture_technique.md",
    "NSI/CAHIER_DES_CHARGES.md",
    "NSI/docs/02_workflow_production.md",
    "NSI/docs/03_architecture_technique.md",
    "NSI/corpus_nsi/README.md",
    "NSI/corpus_nsi/rag_connection.md",
    "NSI/corpus_nsi/substance_pipeline.md",
    "NSI/corpus_nsi/docs/enrichment_roadmap.md",
}
paths = set(subprocess.check_output(
    ["git", "diff", "--name-only"], text=True
).splitlines())
assert paths <= allowed, paths - allowed
assert allowed == paths, (paths - allowed, allowed - paths)
PY
git diff --check
```

Expected: exactement les dix-sept surfaces §8.4 ; la roadmap est obligatoire car prescriptive.

- [ ] **Step 3: Vérifier que les autorités ne changent aucun gate métier**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
git diff -U0 -- \
  AGENTS.md \
  .agents/skills/nexus-manual-quality/SKILL.md \
  CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md \
  README.md \
| rg -n 'NO-GO|release-strict|validate-model|fail-on-new|P0|OpenRouter|Chutes'
```

Expected: `NO-GO` et gates préservés, seul le fournisseur futur est aligné.

- [ ] **Step 4: Faire deux revues documentaires indépendantes**

Le reviewer spécification vérifie chaque fichier §8.4 et l’honnêteté historique. Le reviewer qualité vérifie contradictions, seconde source de configuration, modèle implicite, promesse réseau/CI ou affaiblissement des validations humaines. Corriger les constats validés et rejouer la policy complète.

- [ ] **Step 5: Indexer uniquement la documentation active**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
git add -- \
  AGENTS.md \
  .agents/skills/nexus-manual-quality/SKILL.md \
  CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md \
  README.md \
  Mathematiques/PROMPT_MISSION_AUTONOME.md \
  Mathematiques/workflow_production_manuel.md \
  Mathematiques/manuel-maths/README.md \
  Mathematiques/manuel-maths/CAHIER_DES_CHARGES.md \
  Mathematiques/manuel-maths/docs/02_workflow_production.md \
  Mathematiques/manuel-maths/docs/03_architecture_technique.md \
  NSI/CAHIER_DES_CHARGES.md \
  NSI/docs/02_workflow_production.md \
  NSI/docs/03_architecture_technique.md \
  NSI/corpus_nsi/README.md \
  NSI/corpus_nsi/rag_connection.md \
  NSI/corpus_nsi/substance_pipeline.md \
  NSI/corpus_nsi/docs/enrichment_roadmap.md
git diff --cached --check
git diff --cached --stat
```

Expected: documentation seulement, exactement dix-sept chemins, aucun fichier historique ou généré. Le README formule durablement l’exclusivité comme vraie seulement si les gates OpenRouter passent sur le SHA courant ; il ne nécessitera pas un commit documentaire ultérieur après inventaire.

- [ ] **Step 6: Committer l’alignement documentaire**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
git commit -m "[DOCS] aligne les autorites sur OpenRouter"
git status --short
test -z "$(git status --short)"
```

Expected: troisième commit atomique. Tous les nouveaux fichiers corpus sont désormais suivis, condition nécessaire au rebuild.

### Task 17: Préparer le rebuild d’inventaire fermé

**Files:**

- Read only: `NSI/corpus_nsi/scripts/rebuild_inventory.py`
- Snapshot read only: `manifest.csv`, `manifest_tooling.csv`, `inventory_report.md`, `duplicates_report.md`, `coverage.md`, `_usage_log.json`

- [ ] **Step 1: Confier l’audit d’inventaire à un implementer frais**

L’agent relit les deux `AGENTS.md`, la section 8.5 et la Task 17 entière. Il n’édite pas le générateur ni les tests. Il travaille uniquement après les trois commits précédents et exige un worktree propre.

- [ ] **Step 2: Prouver que chaque nouveau fichier corpus est suivi**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
CORPUS_ROOT=$IMPL_ROOT/NSI/corpus_nsi
cd "$IMPL_ROOT"
test -z "$(git status --short)"
git ls-files --error-unmatch \
  NSI/corpus_nsi/tests/test_openrouter_judges.py \
  NSI/corpus_nsi/scripts/judge_campaign.py \
  NSI/corpus_nsi/scripts/substance_judge.py \
  NSI/corpus_nsi/scripts/run_substance_judge.py \
  NSI/corpus_nsi/scripts/check_rag_config.py
test -e "$IMPL_ROOT/.git"
test -d "$CORPUS_ROOT"
```

Expected: tous les chemins sont dans l’index Git du checkout racine.

- [ ] **Step 3: Créer les snapshots hors dépôt**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
CORPUS_ROOT=$IMPL_ROOT/NSI/corpus_nsi
cd "$CORPUS_ROOT"
AUDIT_TMP=$(mktemp -d /tmp/nexus-openrouter-inventory.XXXXXX)
mapfile -t ACTIVE_POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-inventory-pointer.*' ! -name '*.complete' -print)
test "${#ACTIVE_POINTERS[@]}" -eq 0
POINTER=$(mktemp /tmp/nexus-openrouter-inventory-pointer.XXXXXX)
chmod 600 "$POINTER"
printf '%s\n' "$AUDIT_TMP" > "$POINTER"
test -O "$AUDIT_TMP"; test ! -L "$AUDIT_TMP"; test "$(stat -c '%a' "$AUDIT_TMP")" = 700
case "$AUDIT_TMP" in /tmp/nexus-openrouter-inventory.*) ;; *) exit 1 ;; esac
test -O "$POINTER"; test ! -L "$POINTER"
test "$(stat -c '%a' "$POINTER")" = 600
mapfile -t POINTER_CONTENT < "$POINTER"
test "${#POINTER_CONTENT[@]}" -eq 1
test "${POINTER_CONTENT[0]}" = "$AUDIT_TMP"
for file in \
  manifest.csv \
  manifest_tooling.csv \
  inventory_report.md \
  duplicates_report.md \
  coverage.md \
  substance_reviews/campaign/_usage_log.json
do
  test -f "$file"
  sha256sum "$file"
  mkdir -p "$AUDIT_TMP/before/$(dirname "$file")"
  cp -- "$file" "$AUDIT_TMP/before/$file"
done > "$AUDIT_TMP/before.sha256"
git ls-files -z | sort -z > "$AUDIT_TMP/git-ls-files.zlist"
printf 'AUDIT_TMP=%s\nPOINTER=%s\n' "$AUDIT_TMP" "$POINTER"
```

Expected: snapshots et liste suivie sous `/tmp`; répertoire mode 700 et pointeur unique mode 600, tous deux appartenant à l’utilisateur, non-liens et sous le préfixe fermé. Un rejeu n’emploie jamais un pointeur `.complete` : après correction/revue, il recommence Task 17 et crée un nouveau couple répertoire/pointeur. Les temporaires restent récupérables ; aucune suppression automatique.

- [ ] **Step 4: Vérifier les trois tests manifest avant rebuild**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
CORPUS_ROOT=$IMPL_ROOT/NSI/corpus_nsi
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-inventory-pointer.*' ! -name '*.complete' -print)
test "${#POINTERS[@]}" -eq 1
POINTER=${POINTERS[0]}
test -O "$POINTER"
test ! -L "$POINTER"
test "$(stat -c '%a' "$POINTER")" = 600
AUDIT_TMP=$(cat "$POINTER")
case "$AUDIT_TMP" in /tmp/nexus-openrouter-inventory.*) ;; *) exit 1 ;; esac
test -d "$AUDIT_TMP"; test -O "$AUDIT_TMP"; test ! -L "$AUDIT_TMP"; test "$(stat -c '%a' "$AUDIT_TMP")" = 700
BEFORE_STATUS=$(git -C "$IMPL_ROOT" status --porcelain=v1)
sha256sum \
  "$CORPUS_ROOT/manifest.csv" \
  "$CORPUS_ROOT/manifest_tooling.csv" \
  "$CORPUS_ROOT/inventory_report.md" \
  "$CORPUS_ROOT/duplicates_report.md" > "$AUDIT_TMP/original-before-red.sha256"
SOURCE_SHA=$(git -C "$IMPL_ROOT" rev-parse HEAD)
test "$(git -C "$IMPL_ROOT" rev-parse "$SOURCE_SHA^{commit}")" = "$SOURCE_SHA"
printf '%s\n' "$SOURCE_SHA" > "$AUDIT_TMP/source.sha"
RED_CLONE=$(mktemp -d /tmp/nexus-openrouter-manifest-red.XXXXXX)
git clone --shared --no-checkout "$IMPL_ROOT" "$RED_CLONE/repo"
git -C "$RED_CLONE/repo" branch manifest-red "$SOURCE_SHA"
git -C "$RED_CLONE/repo" symbolic-ref HEAD refs/heads/manifest-red
git -C "$RED_CLONE/repo" read-tree -mu HEAD
test "$(git -C "$RED_CLONE/repo" rev-parse HEAD)" = "$SOURCE_SHA"
test "$(cat "$AUDIT_TMP/source.sha")" = "$SOURCE_SHA"
cd "$RED_CLONE/repo/NSI/corpus_nsi"
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider tests/test_manifest_separation.py \
  --junitxml "$AUDIT_TMP/manifest-red.xml" > "$AUDIT_TMP/manifest-red.out" 2>&1
MANIFEST_RED_RC=$?
set -e
test "$MANIFEST_RED_RC" -eq 1
python3 - "$AUDIT_TMP/manifest-red.xml" <<'PY'
import sys
import xml.etree.ElementTree as ET
tree = ET.parse(sys.argv[1])
suites = tree.findall(".//testsuite") or [tree.getroot()]
got = {key: sum(int(s.attrib.get(key, "0")) for s in suites) for key in ("tests", "failures", "errors", "skipped")}
assert got == {"tests": 3, "failures": 3, "errors": 0, "skipped": 0}, got
PY
sha256sum -c "$AUDIT_TMP/original-before-red.sha256"
test "$(git -C "$IMPL_ROOT" status --porcelain=v1)" = "$BEFORE_STATUS"
```

Expected: clone créé sans checkout initial, branche locale non forcée, `symbolic-ref` puis `read-tree -mu`, au `SOURCE_SHA` attesté avant exécution ; JUnit exact `3 tests / 3 failures / 0 error / 0 skip`. Le worktree et ses quatre hashes restent inchangés malgré les effets de bord possibles du test historique.

### Task 18: Reconstruire, vérifier l’idempotence et committer exactement deux sorties

**Files:**

- Modify generated: `NSI/corpus_nsi/manifest_tooling.csv`
- Modify generated: `NSI/corpus_nsi/inventory_report.md`
- Must remain byte-identical: `manifest.csv`, `duplicates_report.md`, `coverage.md`, `_usage_log.json`

- [ ] **Step 1: Confier le rebuild à un nouvel implementer frais**

Cet implementer relit le proche `AGENTS.md`, la section 8.5 et les preuves de Task 17. Il vérifie le pointeur et les snapshots sans les recréer, n’édite jamais une sortie générée à la main et s’arrête si le worktree n’est pas propre au début du Task.

- [ ] **Step 2: Exécuter le premier rebuild canonique**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
CORPUS_ROOT=$IMPL_ROOT/NSI/corpus_nsi
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-inventory-pointer.*' ! -name '*.complete' -print)
test "${#POINTERS[@]}" -eq 1
POINTER=${POINTERS[0]}
test -O "$POINTER"; test ! -L "$POINTER"; test "$(stat -c '%a' "$POINTER")" = 600
AUDIT_TMP=$(cat "$POINTER")
case "$AUDIT_TMP" in /tmp/nexus-openrouter-inventory.*) ;; *) exit 1 ;; esac
test -d "$AUDIT_TMP"; test -O "$AUDIT_TMP"; test ! -L "$AUDIT_TMP"; test "$(stat -c '%a' "$AUDIT_TMP")" = 700
test -z "$(git -C "$IMPL_ROOT" status --porcelain=v1)"
SOURCE_SHA=$(cat "$AUDIT_TMP/source.sha")
test "$(git -C "$IMPL_ROOT" rev-parse HEAD)" = "$SOURCE_SHA"
test "$(git -C "$IMPL_ROOT" rev-parse "$SOURCE_SHA^{commit}")" = "$SOURCE_SHA"
cd "$CORPUS_ROOT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 - <<'PY'
import runpy
import socket
import urllib.request

def blocked(*args: object, **kwargs: object) -> None:
    raise AssertionError("network forbidden during inventory rebuild")

socket.create_connection = blocked
socket.socket.connect = blocked
urllib.request.urlopen = blocked
runpy.run_module("scripts.rebuild_inventory", run_name="__main__")
PY
for file in manifest.csv manifest_tooling.csv inventory_report.md duplicates_report.md; do
  sha256sum "$file"
done > "$AUDIT_TMP/after-first.sha256"
```

Expected: le worktree est propre et toujours exactement au SHA capturé par Task 17 avant toute reconstruction ; reconstruction locale, aucun transport externe. Toute divergence impose un nouveau run Task 17, pas la réutilisation du pointeur.

- [ ] **Step 3: Fermer le delta aux deux sorties autorisées**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
CORPUS_ROOT=$IMPL_ROOT/NSI/corpus_nsi
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-inventory-pointer.*' ! -name '*.complete' -print)
test "${#POINTERS[@]}" -eq 1
POINTER=${POINTERS[0]}
test -O "$POINTER"; test ! -L "$POINTER"; test "$(stat -c '%a' "$POINTER")" = 600
AUDIT_TMP=$(cat "$POINTER")
case "$AUDIT_TMP" in /tmp/nexus-openrouter-inventory.*) ;; *) exit 1 ;; esac
test -d "$AUDIT_TMP"; test -O "$AUDIT_TMP"; test ! -L "$AUDIT_TMP"; test "$(stat -c '%a' "$AUDIT_TMP")" = 700
cd "$IMPL_ROOT"
mapfile -t CHANGED < <(git status --short | cut -c4- | sort)
test "${#CHANGED[@]}" -eq 2
test "${CHANGED[0]}" = "NSI/corpus_nsi/inventory_report.md"
test "${CHANGED[1]}" = "NSI/corpus_nsi/manifest_tooling.csv"
cmp "$AUDIT_TMP/before/manifest.csv" "$CORPUS_ROOT/manifest.csv"
cmp "$AUDIT_TMP/before/duplicates_report.md" "$CORPUS_ROOT/duplicates_report.md"
cmp "$AUDIT_TMP/before/coverage.md" "$CORPUS_ROOT/coverage.md"
cmp "$AUDIT_TMP/before/substance_reviews/campaign/_usage_log.json" \
  "$CORPUS_ROOT/substance_reviews/campaign/_usage_log.json"
```

Expected: exactement deux sorties modifiées ; les quatre snapshots protégés sont octet-identiques. Sinon `HARD STOP` sans restaurer automatiquement.

- [ ] **Step 4: Rebuild une deuxième fois et comparer les quatre sorties canoniques**

```bash
set -euo pipefail
CORPUS_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-inventory-pointer.*' ! -name '*.complete' -print)
test "${#POINTERS[@]}" -eq 1
POINTER=${POINTERS[0]}
test -O "$POINTER"; test ! -L "$POINTER"; test "$(stat -c '%a' "$POINTER")" = 600
AUDIT_TMP=$(cat "$POINTER")
case "$AUDIT_TMP" in /tmp/nexus-openrouter-inventory.*) ;; *) exit 1 ;; esac
test -d "$AUDIT_TMP"; test -O "$AUDIT_TMP"; test ! -L "$AUDIT_TMP"; test "$(stat -c '%a' "$AUDIT_TMP")" = 700
cd "$CORPUS_ROOT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 - <<'PY'
import runpy
import socket
import urllib.request

def blocked(*args: object, **kwargs: object) -> None:
    raise AssertionError("network forbidden during inventory rebuild")

socket.create_connection = blocked
socket.socket.connect = blocked
urllib.request.urlopen = blocked
runpy.run_module("scripts.rebuild_inventory", run_name="__main__")
PY
for file in manifest.csv manifest_tooling.csv inventory_report.md duplicates_report.md; do
  sha256sum "$file"
done > "$AUDIT_TMP/after-second.sha256"
cmp "$AUDIT_TMP/after-first.sha256" "$AUDIT_TMP/after-second.sha256"
cmp "$AUDIT_TMP/before/manifest.csv" "$CORPUS_ROOT/manifest.csv"
cmp "$AUDIT_TMP/before/duplicates_report.md" "$CORPUS_ROOT/duplicates_report.md"
cmp "$AUDIT_TMP/before/coverage.md" "$CORPUS_ROOT/coverage.md"
cmp "$AUDIT_TMP/before/substance_reviews/campaign/_usage_log.json" \
  "$CORPUS_ROOT/substance_reviews/campaign/_usage_log.json"
```

Expected: hashes identiques après deux builds.

- [ ] **Step 5: Passer les trois tests manifest sans réseau**

```bash
set -euo pipefail
CORPUS_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
cd "$CORPUS_ROOT"
MANIFEST_OUT=$(mktemp /tmp/nexus-openrouter-manifest-green.XXXXXX)
MANIFEST_XML=$(mktemp /tmp/nexus-openrouter-manifest-green.XXXXXX.xml)
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider tests/test_manifest_separation.py \
  --junitxml "$MANIFEST_XML" \
  | tee "$MANIFEST_OUT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 - "$MANIFEST_XML" <<'PY'
import sys, xml.etree.ElementTree as ET
r=ET.parse(sys.argv[1]).getroot();s=r.findall(".//testsuite") or [r]
got={k:sum(int(x.get(k,"0")) for x in s) for k in ("tests","failures","errors","skipped")}
assert got=={"tests":3,"failures":0,"errors":0,"skipped":0},got
PY
```

Expected: exactement `3 passed`.

- [ ] **Step 6: Vérifier les nouvelles entrées tooling**

```bash
set -euo pipefail
CORPUS_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
cd "$CORPUS_ROOT"
rg -F 'tests/test_openrouter_judges.py' manifest_tooling.csv inventory_report.md
! rg -F 'tests/test_openrouter_judges.py' manifest.csv
git diff --check
```

Expected: nouveau test dans l’inventaire d’outillage seulement.

- [ ] **Step 7: Faire deux revues du delta généré**

Le reviewer spécification vérifie la section 8.5, les snapshots et l’idempotence. Le reviewer qualité vérifie l’absence de changement pédagogique, historique, couverture ou journal. Aucun correctif manuel des CSV/Markdown générés : toute anomalie est `HARD STOP` et se corrige dans une tâche autonome approuvée.

- [ ] **Step 8: Indexer et committer exactement les deux sorties**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
CANONICAL='[AUDIT] resynchronise l inventaire outillage OpenRouter'
COUNT=$(git log --format=%s | grep -Fxc "$CANONICAL" || true)
test "$COUNT" -le 1
mapfile -t ALL_DELTA < <(git status --short | cut -c4- | sort)
if test "${#ALL_DELTA[@]}" -eq 0; then
  test "$COUNT" -eq 1
else
  test "${#ALL_DELTA[@]}" -eq 2
  test "${ALL_DELTA[0]}" = "NSI/corpus_nsi/inventory_report.md"
  test "${ALL_DELTA[1]}" = "NSI/corpus_nsi/manifest_tooling.csv"
git add -- \
  NSI/corpus_nsi/manifest_tooling.csv \
  NSI/corpus_nsi/inventory_report.md
test "$(git diff --cached --name-only | wc -l)" -eq 2
git diff --cached --name-only | sort | diff -u - <(printf '%s\n' \
  NSI/corpus_nsi/inventory_report.md \
  NSI/corpus_nsi/manifest_tooling.csv)
git diff --cached --check
  if test "$COUNT" -eq 0; then
    git commit -m "$CANONICAL"
  else
    git commit -m "[AUDIT] resynchronise l inventaire outillage OpenRouter apres revue"
  fi
fi
git status --short
test -z "$(git status --short)"
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-inventory-pointer.*' ! -name '*.complete' -print)
test "${#POINTERS[@]}" -eq 1
POINTER=${POINTERS[0]}
test -O "$POINTER"; test ! -L "$POINTER"; test "$(stat -c '%a' "$POINTER")" = 600
AUDIT_TMP=$(cat "$POINTER"); case "$AUDIT_TMP" in /tmp/nexus-openrouter-inventory.*) ;; *) exit 1 ;; esac
test -d "$AUDIT_TMP"; test -O "$AUDIT_TMP"; test ! -L "$AUDIT_TMP"; test "$(stat -c '%a' "$AUDIT_TMP")" = 700
mv -- "$POINTER" "$POINTER.complete"
test -f "$POINTER.complete"; test -O "$POINTER.complete"; test ! -L "$POINTER.complete"; test "$(stat -c '%a' "$POINTER.complete")" = 600
mapfile -t ACTIVE_AFTER < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-inventory-pointer.*' ! -name '*.complete' -print)
test "${#ACTIVE_AFTER[@]}" -eq 0
```

Expected: si le sujet canonique est absent, le delta exact de deux fichiers produit ce quatrième commit ; s’il existe déjà, il n’est jamais dupliqué et un delta exact de deux fichiers produit seulement le commit `... apres revue`; si le delta est nul, aucun commit. Dans tous les cas le pointeur du run devient `.complete` après les preuves. Toute nouvelle exécution recommence Task 17 avec un pointeur unique neuf.

## Chunk 9: Vérification adversariale, gates et remise auditable

### Task 19: Rejouer le contrat OpenRouter complet en quatre processus

**Files:** aucune modification attendue.

- [ ] **Step 1: Relever le SHA et exiger un worktree propre**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
git status --short --branch
git rev-parse HEAD
git log --oneline --decorate -8
git diff --stat
git diff --check
test -z "$(git status --short)"
mapfile -t ACTIVE_POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print)
test "${#ACTIVE_POINTERS[@]}" -eq 0
VERIFY_ROOT=$(mktemp -d /tmp/nexus-openrouter-verify.XXXXXX)
test -O "$VERIFY_ROOT"; test ! -L "$VERIFY_ROOT"; test "$(stat -c '%a' "$VERIFY_ROOT")" = 700
GUARD_ROOT="$VERIFY_ROOT/guard"
mkdir -m 700 "$GUARD_ROOT"
test -O "$GUARD_ROOT"; test ! -L "$GUARD_ROOT"; test "$(stat -c '%a' "$GUARD_ROOT")" = 700
install -m 600 /dev/stdin "$GUARD_ROOT/sitecustomize.py" <<'PY'
import os, socket, urllib.request
from pathlib import Path
marker = Path(os.environ["NEXUS_NETWORK_GUARD_MARKER"])
marker.parent.mkdir(parents=True, exist_ok=True)
with marker.open("a", encoding="utf-8") as handle:
    handle.write(f"sitecustomize-loaded:{os.getpid()}\n")
def blocked(*args: object, **kwargs: object) -> None:
    raise AssertionError("network forbidden by final OpenRouter verification")
socket.socket.connect = blocked
socket.create_connection = blocked
urllib.request.urlopen = blocked
PY
POINTER=$(mktemp /tmp/nexus-openrouter-verify-pointer.XXXXXX)
chmod 600 "$POINTER"; printf '%s\n' "$VERIFY_ROOT" > "$POINTER"
test -O "$POINTER"; test ! -L "$POINTER"; test "$(stat -c '%a' "$POINTER")" = 600
export PYTHONPATH="$GUARD_ROOT"
export NEXUS_NETWORK_GUARD_MARKER="$VERIFY_ROOT/sitecustomize.marker"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 - <<'PY'
import subprocess

canonical = [
    "[TESTS] verrouille la passerelle OpenRouter",
    "[PYTHON] centralise les appels LLM via OpenRouter",
    "[DOCS] aligne les autorites sur OpenRouter",
    "[AUDIT] resynchronise l inventaire outillage OpenRouter",
]
rows = subprocess.check_output(["git", "log", "--format=%H%x09%s"], text=True).splitlines()
subjects = [row.split("\t", 1)[1] for row in rows]
for subject in canonical:
    assert subjects.count(subject) == 1, (subject, subjects.count(subject))
positions = [subjects.index(subject) for subject in canonical]
assert positions == sorted(positions, reverse=True), positions
PY
test -s "$NEXUS_NETWORK_GUARD_MARKER"
```

Expected: garde global chargé et marker non vide dès le début de Task 19 ; exactement un exemplaire de chacun des quatre sujets canoniques dans l’ordre TESTS, PYTHON, DOCS, AUDIT. Des commits de correction ciblés peuvent s’intercaler ; ils ne dupliquent jamais un sujet canonique.

- [ ] **Step 2: Inventorier exactement les nodes et paramètres avant exécution**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
NODE_TMP=$(mktemp -d /tmp/nexus-openrouter-nodes.XXXXXX)
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print)
test "${#POINTERS[@]}" -eq 1
VERIFY_ROOT=$(cat "${POINTERS[0]}"); case "$VERIFY_ROOT" in /tmp/nexus-openrouter-verify.*) ;; *) exit 1 ;; esac
GUARD_ROOT="$VERIFY_ROOT/guard"; MARKER="$VERIFY_ROOT/sitecustomize.marker"
cd "$IMPL_ROOT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL PYTHONPATH="$GUARD_ROOT" NEXUS_NETWORK_GUARD_MARKER="$MARKER" python3 -m pytest --collect-only -q -p no:cacheprovider \
  tests/test_openrouter_client.py tests/test_openrouter_classification.py \
  tests/test_external_provider_policy.py > "$NODE_TMP/core.nodes"
cd "$IMPL_ROOT/Mathematiques/manuel-maths"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL PYTHONPATH="$GUARD_ROOT" NEXUS_NETWORK_GUARD_MARKER="$MARKER" python3 -m pytest --collect-only -q -p no:cacheprovider \
  tests/test_ingest_openrouter.py > "$NODE_TMP/math.nodes"
cd "$IMPL_ROOT/NSI"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL PYTHONPATH="$GUARD_ROOT" NEXUS_NETWORK_GUARD_MARKER="$MARKER" python3 -m pytest --collect-only -q -p no:cacheprovider \
  tests/test_ingest_openrouter.py > "$NODE_TMP/nsi.nodes"
cd "$IMPL_ROOT/NSI/corpus_nsi"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL PYTHONPATH="$GUARD_ROOT" NEXUS_NETWORK_GUARD_MARKER="$MARKER" python3 -m pytest --collect-only -q -p no:cacheprovider \
  tests/test_rag_governance_and_indexes.py tests/test_secret_guard.py \
  tests/test_openrouter_judges.py tests/test_substance_judge_pipeline.py \
  tests/test_substance_hardened.py tests/test_judge_collection_barriers.py \
  tests/test_policy_checker_ast.py tests/test_manifest_separation.py \
  > "$NODE_TMP/corpus.nodes"
mapfile -t BASELINE_POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-baseline-pointer.*' ! -name '*.complete' -print)
test "${#BASELINE_POINTERS[@]}" -eq 1
BASELINE_POINTER=${BASELINE_POINTERS[0]}
test -O "$BASELINE_POINTER"; test ! -L "$BASELINE_POINTER"; test "$(stat -c '%a' "$BASELINE_POINTER")" = 600
BASELINE_ROOT=$(cat "$BASELINE_POINTER"); case "$BASELINE_ROOT" in /tmp/nexus-openrouter-baseline.*) ;; *) exit 1 ;; esac
test -f "$BASELINE_ROOT/corpus-baseline-85.nodeids"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  PYTHONPATH="$GUARD_ROOT" NEXUS_NETWORK_GUARD_MARKER="$MARKER" \
  python3 - "$NODE_TMP" "$BASELINE_ROOT/corpus-baseline-85.nodeids" <<'PY'
import sys
from pathlib import Path

node_root = Path(sys.argv[1])
baseline85 = set(Path(sys.argv[2]).read_text(encoding="utf-8").splitlines())

def collected(name: str) -> set[str]:
    return {
        line for line in node_root.joinpath(f"{name}.nodes").read_text(encoding="utf-8").splitlines()
        if line.startswith("tests/")
    }

client = (
"test_chat_completion_posts_to_exact_openrouter_endpoint test_chat_completion_sends_bearer_and_json_headers "
"test_chat_completion_sends_one_model_and_max_completion_tokens test_chat_completion_uses_injected_mock_transport_without_socket "
"test_chat_completion_caps_timeout_at_thirty_seconds test_chat_completion_does_not_follow_redirects "
"test_chat_completion_returns_validated_structured_result test_completion_and_usage_are_immutable "
"test_http_failure_maps_to_sanitized_error_category test_http_200_refuses_root_error_object "
"test_http_200_refuses_choice_error_object test_http_200_refuses_non_stop_finish_reason "
"test_response_rejects_malformed_envelope_component test_errors_and_logs_never_expose_secret_prompt_or_raw_body "
"test_client_does_not_retry_failed_request test_client_rejects_blank_key_before_transport "
"test_client_rejects_blank_model_before_transport test_usage_rejects_invalid_required_accounting "
"test_usage_rejects_invalid_cache_details test_usage_normalizes_absent_cache_counters_to_zero "
"test_usage_preserves_exact_openrouter_cost test_response_rejects_invalid_root_generation_id "
"test_response_rejects_invalid_returned_model"
).split()
classification = (
"test_classification_without_key_uses_local_heuristic_without_transport "
"test_classification_with_key_without_model_fails_before_transport "
"test_classification_with_key_and_model_forwards_exact_model "
"test_classification_sends_only_first_3000_fragment_characters test_classification_requests_200_completion_tokens "
"test_local_heuristic_preserves_existing_chunk_type_contract test_remote_classification_accepts_exact_closed_object "
"test_remote_classification_rejects_invalid_closed_object_as_a_whole "
"test_remote_classification_rejects_boolean_difficulty test_invalid_remote_classification_returns_global_conservative_result "
"test_remote_metadata_cannot_override_trusted_record_fields test_prompt_does_not_append_environment_or_provenance_metadata"
).split()
policy = (
"test_policy_requires_every_canonical_active_surface test_policy_rejects_unlisted_provider_transport "
"test_policy_allows_only_openrouter_client_to_define_llm_endpoint test_policy_preserves_non_llm_rag_transport_allowlist "
"test_policy_rejects_chutes_in_active_authority test_policy_ignores_protected_historical_chutes_artifacts "
"test_policy_rejects_model_catalog_endpoint_in_automation test_policy_rejects_new_nsi_ingest_make_target "
"test_targeted_surfaces_exist_before_negative_scans test_policy_rejects_anthropic_in_active_callers "
"test_policy_rejects_local_llm_configuration_in_active_surfaces test_ci_no_deps_requirements_close_httpx_runtime_dependencies"
).split()
expected_core = {f"tests/test_openrouter_client.py::{name}" for name in client}
expected_core |= {f"tests/test_openrouter_classification.py::{name}" for name in classification}
expected_core |= {f"tests/test_external_provider_policy.py::{name}" for name in policy}
assert len(expected_core) == 47
assert collected("core") == expected_core, (collected("core") - expected_core, expected_core - collected("core"))

for prefix in ("math", "nsi"):
    names = (
        f"test_{prefix}_ingest_classify_delegates_to_shared_classifier",
        f"test_{prefix}_ingest_preserves_trusted_metadata_against_hostile_classifier",
        f"test_{prefix}_ingest_command_runs_without_source_key_or_network",
        f"test_{prefix}_ingest_discovers_current_checkout_from_unrelated_cwd",
        f"test_{prefix}_ingest_prioritizes_current_checkout_over_shadow_package",
        f"test_{prefix}_ingest_rejects_nexus_external_loaded_outside_checkout",
        f"test_{prefix}_no_source_command_does_not_import_extraction_backends",
        f"test_{prefix}_network_guard_mutation_is_effective",
    )
    expected = {f"tests/test_ingest_openrouter.py::{name}" for name in names}
    assert len(expected) == 8
    assert collected(prefix) == expected, (prefix, collected(prefix) - expected, expected - collected(prefix))

corpus_new = (
"test_campaign_delegates_to_shared_openrouter_client test_campaign_reads_missing_openrouter_values_from_resolved_rag_env "
"test_campaign_does_not_read_generic_dotenv test_campaign_rejects_key_without_model_before_transport "
"test_campaign_business_retry_count_is_bounded test_campaign_records_requested_openrouter_model "
"test_campaign_records_each_billed_retry_generation_before_verdict_validation test_usage_v2_copies_completion_accounting_exactly "
"test_usage_upsert_replaces_same_generation_only test_usage_upsert_preserves_v1_deeply_and_in_order "
"test_usage_upsert_preserves_other_v2_generations_for_same_capacity test_usage_logging_contains_no_local_cost_formula "
"test_failed_usage_entry_invents_no_accounting test_run_totals_sum_only_current_successful_v2_entries "
"test_substance_llm_delegates_to_shared_openrouter_client test_substance_without_key_returns_conservative_result_without_transport "
"test_substance_rejects_key_without_model_before_transport test_substance_sends_exact_bounded_prompt_and_limit "
"test_substance_accepts_only_exact_closed_json_object test_substance_rag_keeps_dedicated_http_transport "
"test_substance_has_no_configurable_llm_endpoint test_substance_remote_error_is_sanitized_and_never_promotes "
"test_run_substance_judge_imports_no_external_client test_run_substance_judge_uses_honest_deterministic_model "
"test_campaign_discovers_current_checkout_from_unrelated_cwd test_substance_discovers_current_checkout_from_unrelated_cwd "
"test_corpus_callers_reject_shadowed_external_package"
).split()
manifest = {
    "tests/test_manifest_separation.py::test_pedagogical_manifest_contains_only_pedagogical_content",
    "tests/test_manifest_separation.py::test_manifests_cover_all_inventoried_resources",
    "tests/test_manifest_separation.py::test_manifest_idempotent_after_rebuild",
}
expected_new = {f"tests/test_openrouter_judges.py::{name}" for name in corpus_new}
expected_corpus = baseline85 | expected_new | manifest
assert (len(baseline85), len(expected_new), len(manifest), len(expected_corpus)) == (85, 27, 3, 115)
assert collected("corpus") == expected_corpus, (
    collected("corpus") - expected_corpus, expected_corpus - collected("corpus")
)
PY
test -s "$MARKER"
```

Expected: égalité d’ensembles exacte, pas seulement des comptes : 47 littéraux core, 8 math, 8 NSI et l’union littérale `85 baseline capturés + 27 nouveaux + 3 manifest = 115`. Toute différence de nodeid ou paramétrisation arrête la suite.

- [ ] **Step 3: Exécuter le processus core racine**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print); test "${#POINTERS[@]}" -eq 1
VERIFY_ROOT=$(cat "${POINTERS[0]}"); GUARD_ROOT="$VERIFY_ROOT/guard"; MARKER="$VERIFY_ROOT/sitecustomize.marker"
cd "$IMPL_ROOT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  PYTHONPATH="$GUARD_ROOT" NEXUS_NETWORK_GUARD_MARKER="$MARKER" python3 -m pytest -q -p no:cacheprovider \
    tests/test_openrouter_client.py \
    tests/test_openrouter_classification.py \
    tests/test_external_provider_policy.py
```

Expected: vert. Les fixtures autouse de chaque nouveau module bloquent `socket.socket.connect`, `socket.create_connection` et `urllib.request.urlopen`; seul `httpx.MockTransport` peut satisfaire un appel LLM.

- [ ] **Step 4: Exécuter le processus Mathématiques**

```bash
set -euo pipefail
MATH_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/Mathematiques/manuel-maths
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print); test "${#POINTERS[@]}" -eq 1
VERIFY_ROOT=$(cat "${POINTERS[0]}"); GUARD_ROOT="$VERIFY_ROOT/guard"; MARKER="$VERIFY_ROOT/sitecustomize.marker"
cd "$MATH_ROOT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  PYTHONPATH="$GUARD_ROOT" NEXUS_NETWORK_GUARD_MARKER="$MARKER" python3 -m pytest -q -p no:cacheprovider tests/test_ingest_openrouter.py
```

Expected: vert depuis le CWD contractuel du manuel.

- [ ] **Step 5: Exécuter le processus NSI manuel**

```bash
set -euo pipefail
NSI_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print); test "${#POINTERS[@]}" -eq 1
VERIFY_ROOT=$(cat "${POINTERS[0]}"); GUARD_ROOT="$VERIFY_ROOT/guard"; MARKER="$VERIFY_ROOT/sitecustomize.marker"
cd "$NSI_ROOT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  PYTHONPATH="$GUARD_ROOT" NEXUS_NETWORK_GUARD_MARKER="$MARKER" python3 -m pytest -q -p no:cacheprovider tests/test_ingest_openrouter.py
```

Expected: vert depuis le CWD contractuel NSI.

- [ ] **Step 6: Exécuter le processus corpus indépendant**

```bash
set -euo pipefail
CORPUS_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print); test "${#POINTERS[@]}" -eq 1
VERIFY_ROOT=$(cat "${POINTERS[0]}"); GUARD_ROOT="$VERIFY_ROOT/guard"; MARKER="$VERIFY_ROOT/sitecustomize.marker"
cd "$CORPUS_ROOT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  PYTHONPATH="$GUARD_ROOT" NEXUS_NETWORK_GUARD_MARKER="$MARKER" python3 -m pytest -q -p no:cacheprovider \
    tests/test_rag_governance_and_indexes.py \
    tests/test_secret_guard.py \
    tests/test_openrouter_judges.py \
    tests/test_substance_judge_pipeline.py \
    tests/test_substance_hardened.py \
    tests/test_judge_collection_barriers.py \
    tests/test_policy_checker_ast.py \
    tests/test_manifest_separation.py
test -s "$MARKER"
```

Expected: vert, trois tests manifest inclus. Ce résultat n’est pas présenté comme un branchement CI racine.

### Task 20: Exécuter les mutations adversariales sans toucher au worktree

**Files:** copies temporaires uniquement.

- [ ] **Step 1: Muter un transport fournisseur hors allowlist**

Exécuter le node nommé `test_policy_rejects_unlisted_provider_transport`, dont le corps boucle sur les mutations `requests`, `urllib`, `httpx` et SDK fournisseur sans paramétrisation :

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
mapfile -t VP < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print); test "${#VP[@]}" -eq 1
VR=$(cat "${VP[0]}"); export PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_external_provider_policy.py::test_policy_rejects_unlisted_provider_transport
```

Expected: le test est vert parce que chacune des quatre injections temporaires est refusée.

- [ ] **Step 2: Muter les erreurs protocole et comptabilité**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
mapfile -t VP < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print); test "${#VP[@]}" -eq 1
VR=$(cat "${VP[0]}"); export PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_client.py::test_http_200_refuses_non_stop_finish_reason \
  tests/test_openrouter_client.py::test_usage_rejects_invalid_required_accounting \
  tests/test_openrouter_client.py::test_usage_rejects_invalid_cache_details \
  tests/test_openrouter_client.py::test_errors_and_logs_never_expose_secret_prompt_or_raw_body
```

Expected: les mutations `length`, tokens booléens/incohérents, coûts non finis, cache hors bornes et sentinelles secrètes sont toutes détectées.

- [ ] **Step 3: Muter le contrat de classification fermé**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
mapfile -t VP < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print); test "${#VP[@]}" -eq 1
VR=$(cat "${VP[0]}"); export PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_classification.py::test_remote_classification_rejects_invalid_closed_object_as_a_whole \
  tests/test_openrouter_classification.py::test_remote_classification_rejects_boolean_difficulty \
  tests/test_openrouter_classification.py::test_remote_metadata_cannot_override_trusted_record_fields
```

Expected: toute mutation devient l’objet conservateur global et les six champs de confiance restent intacts.

- [ ] **Step 4: Muter coût, génération et compatibilité v1 du journal**

```bash
set -euo pipefail
CORPUS_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only/NSI/corpus_nsi
cd "$CORPUS_ROOT"
mapfile -t VP < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print); test "${#VP[@]}" -eq 1
VR=$(cat "${VP[0]}"); export PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_judges.py::test_usage_v2_copies_completion_accounting_exactly \
  tests/test_openrouter_judges.py::test_usage_upsert_replaces_same_generation_only \
  tests/test_openrouter_judges.py::test_usage_upsert_preserves_v1_deeply_and_in_order \
  tests/test_openrouter_judges.py::test_usage_upsert_preserves_other_v2_generations_for_same_capacity \
  tests/test_openrouter_judges.py::test_usage_logging_contains_no_local_cost_formula
```

Expected: le coût OpenRouter est copié exactement, l’identité est `generation_id`, les v1 et leurs ordres restent inchangés, toute formule locale échoue.

- [ ] **Step 5: Vérifier que les mutations n’ont écrit aucun fichier**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
git status --short
test -z "$(git status --short)"
```

Expected: worktree propre.

### Task 21: Vérifier dépendances, commandes et historique protégé

**Files:** aucune modification attendue.

- [ ] **Step 1: Vérifier les pins et l’absence de SDK fournisseur actif**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
mapfile -t VP < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print); test "${#VP[@]}" -eq 1
VR=$(cat "${VP[0]}"); export PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker"
for pin in \
  'httpx==0.28.1' \
  'anyio==4.9.0' \
  'certifi==2026.7.22' \
  'httpcore==1.0.9' \
  'h11==0.16.0' \
  'idna==3.6' \
  'sniffio==1.3.1'
do
  test "$(grep -Fxc "$pin" requirements-ci-audit.txt)" -eq 1
done
! rg -n '^anthropic([<=>]|$)' \
  Mathematiques/manuel-maths/requirements.txt \
  NSI/requirements.txt \
  NSI/corpus_nsi/requirements.txt \
  requirements-ci-audit.txt
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL python3 - <<'PY'
from pathlib import Path
pins = {
    "httpx==0.28.1", "anyio==4.9.0", "certifi==2026.7.22",
    "httpcore==1.0.9", "h11==0.16.0", "idna==3.6",
    "sniffio==1.3.1", "typing_extensions==4.15.0",
}
lines = [line.strip() for line in Path("requirements-ci-audit.txt").read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]
for pin in pins:
    assert lines.count(pin) == 1, (pin, lines.count(pin))
assert not any(line.lower().startswith(("anthropic", "openai", "chutes")) for line in lines)
PY
```

Expected: fermeture `--no-deps` statique exacte déjà prouvée au Red, aucune dépendance à l’environnement Python global, aucun install ni SDK fournisseur actif.

- [ ] **Step 2: Rejouer les commandes sans source ni clé**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
mapfile -t VP < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print); test "${#VP[@]}" -eq 1
VR=$(cat "${VP[0]}"); export PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker"
cd "$IMPL_ROOT/Mathematiques/manuel-maths"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_ingest_openrouter.py::test_math_ingest_command_runs_without_source_key_or_network \
  tests/test_ingest_openrouter.py::test_math_no_source_command_does_not_import_extraction_backends
cd "$IMPL_ROOT/NSI"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_ingest_openrouter.py::test_nsi_ingest_command_runs_without_source_key_or_network \
  tests/test_ingest_openrouter.py::test_nsi_no_source_command_does_not_import_extraction_backends
cd "$IMPL_ROOT/NSI/corpus_nsi"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_judges.py::test_campaign_business_retry_count_is_bounded \
  tests/test_openrouter_judges.py::test_substance_without_key_returns_conservative_result_without_transport
```

Expected: les tests de CLI créent sous `tmp_path` un `sitecustomize.py` qui bloque `socket.socket.connect`, `socket.create_connection` et `urllib.request.urlopen` jusque dans les sous-processus `make ingest`/`python3 scripts/ingest.py`; aucun socket, backend d’extraction ou fournisseur. Le dry-run campagne est exercé sous le même bloqueur dans son test, jamais par une commande réseau nue.

- [ ] **Step 3: Recalculer les hashes historiques depuis une preuve finale**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
VERIFY_TMP=$(mktemp -d /tmp/nexus-openrouter-history.XXXXXX)
mapfile -t VP < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print); test "${#VP[@]}" -eq 1
VR=$(cat "${VP[0]}"); export PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL python3 - "$VERIFY_TMP" <<'PY'
import subprocess
import sys
from pathlib import Path

rows = subprocess.check_output(["git", "log", "--format=%H%x09%s"], text=True).splitlines()
matches = [row.split("\t", 1)[0] for row in rows if row.split("\t", 1)[1] == "[TESTS] verrouille la passerelle OpenRouter"]
assert len(matches) == 1, matches
base = subprocess.check_output(["git", "rev-parse", f"{matches[0]}^"], text=True).strip()
prefixes = (
    "audit/", "docs/codex/", "docs/superpowers/plans/", "docs/superpowers/specs/",
    "NSI/corpus_nsi/reports/", "NSI/corpus_nsi/docs/judge_campaign_plan.md",
    "NSI/corpus_nsi/substance_reviews/",
)
def selected(path: str) -> bool:
    return any(path == prefix or path.startswith(prefix) for prefix in prefixes)
base_paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "-z", base]).decode().split("\0")
current_paths = subprocess.check_output(["git", "ls-files", "-z"]).decode().split("\0")
before = {
    path: subprocess.check_output(["git", "rev-parse", f"{base}:{path}"], text=True).strip()
    for path in base_paths if path and selected(path)
}
after = {
    path: subprocess.check_output(["git", "hash-object", "--", path], text=True).strip()
    for path in current_paths if path and selected(path)
}
root = Path(sys.argv[1])
root.joinpath("protected.before.hashes").write_text(
    "".join(f"{digest}  {path}\n" for path, digest in sorted(before.items())), encoding="utf-8"
)
root.joinpath("protected.final.hashes").write_text(
    "".join(f"{digest}  {path}\n" for path, digest in sorted(after.items())), encoding="utf-8"
)
assert before == after, {
    "added": sorted(after.keys() - before.keys()),
    "deleted": sorted(before.keys() - after.keys()),
    "changed": sorted(path for path in before.keys() & after.keys() if before[path] != after[path]),
}
PY
cmp "$VERIFY_TMP/protected.before.hashes" "$VERIFY_TMP/protected.final.hashes"
```

Expected: comparaison machine exacte de la liste triée chemin/hash entre l’unique parent Red et le SHA final, y compris ajouts et suppressions ; aucun historique protégé ne change.

- [ ] **Step 4: Comparer profondément les entrées v1 suivies**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
mapfile -t VP < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print); test "${#VP[@]}" -eq 1
VR=$(cat "${VP[0]}"); export PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL python3 - <<'PY'
import json
import subprocess

rows = subprocess.check_output(
    ["git", "log", "--format=%H%x09%s"], text=True,
).splitlines()
red_sha = next(
    row.split("\t", 1)[0]
    for row in rows
    if row.split("\t", 1)[1] == "[TESTS] verrouille la passerelle OpenRouter"
)
base_sha = subprocess.check_output(
    ["git", "rev-parse", f"{red_sha}^"], text=True,
).strip()
base = subprocess.check_output(
    ["git", "show", f"{base_sha}:NSI/corpus_nsi/substance_reviews/campaign/_usage_log.json"],
    text=True,
)
current = open(
    "NSI/corpus_nsi/substance_reviews/campaign/_usage_log.json",
    encoding="utf-8",
).read()
before = json.loads(base)
after = json.loads(current)
before_v1 = [row for row in before if row.get("schema_version") != 2]
after_v1 = [row for row in after if row.get("schema_version") != 2]
assert after_v1 == before_v1
PY
```

Expected: égalité profonde et ordre identique, y compris si une correction de revue a ajouté un commit après les quatre commits canoniques.

### Task 22: Qualifier les gates connus sans modifier leurs autorités

**Files:** sorties temporaires seulement.

- [ ] **Step 1: Reproduire la collecte racine et son unique collision connue**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
COLLECT_TMP=$(mktemp -d /tmp/nexus-openrouter-collect.XXXXXX)
cd "$IMPL_ROOT"
mapfile -t VP < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print); test "${#VP[@]}" -eq 1
VR=$(cat "${VP[0]}"); export PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker"
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL python3 -m pytest --collect-only -q -p no:cacheprovider \
  > "$COLLECT_TMP/root.out" 2>&1
COLLECT_RC=$?
set -e
test "$COLLECT_RC" -eq 2
test "$(grep -c '^ERROR collecting ' "$COLLECT_TMP/root.out")" -eq 1
rg -F 'assemble.BOOK_VARIANTS' "$COLLECT_TMP/root.out"
! rg -e 'ERROR collecting .*test_openrouter|ModuleNotFoundError.*nexus_external' \
  "$COLLECT_TMP/root.out"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL python3 - "$COLLECT_TMP/root.out" <<'PY'
import re
import sys
text = open(sys.argv[1], encoding="utf-8").read()
match = re.search(r"(\d+) tests collected", text)
assert match and int(match.group(1)) > 5032, match.group(0) if match else text[-500:]
PY
```

Expected: la collecte globale reste rouge uniquement sur la collision historique ; les quatre processus ciblés sont les preuves du lot. Le nombre découvert est supérieur à la baseline 5 032 du nombre de nouveaux nodes, mais ne vaut pas suite complète verte.

- [ ] **Step 2: Exécuter l’inventaire direct et qualifier le code 3**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
GATE_TMP=$(mktemp -d /tmp/nexus-openrouter-gates.XXXXXX)
test -O "$GATE_TMP"; test ! -L "$GATE_TMP"; test "$(stat -c '%a' "$GATE_TMP")" = 700
mapfile -t ACTIVE_POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-gates-pointer.*' ! -name '*.complete' -print)
test "${#ACTIVE_POINTERS[@]}" -eq 0
POINTER=$(mktemp /tmp/nexus-openrouter-gates-pointer.XXXXXX)
chmod 600 "$POINTER"
printf '%s\n' "$GATE_TMP" > "$POINTER"
test -O "$POINTER"; test ! -L "$POINTER"; test "$(stat -c '%a' "$POINTER")" = 600
mapfile -t POINTER_CONTENT < "$POINTER"; test "${#POINTER_CONTENT[@]}" -eq 1; test "${POINTER_CONTENT[0]}" = "$GATE_TMP"
printf 'GATE_TMP=%s\nPOINTER=%s\n' "$GATE_TMP" "$POINTER"
cd "$IMPL_ROOT"
mapfile -t VP < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print); test "${#VP[@]}" -eq 1
VR=$(cat "${VP[0]}"); export PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker"
set +e
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL python3 scripts/inventory_collection.py --check --require-clean \
  > "$GATE_TMP/inventory-direct.json" 2> "$GATE_TMP/inventory-direct.err"
DIRECT_RC=$?
set -e
test "$DIRECT_RC" -eq 3
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL python3 - "$GATE_TMP/inventory-direct.json" <<'PY'
import json
import sys

payload = json.load(open(sys.argv[1], encoding="utf-8"))
assert payload["gate"] == "check"
assert payload["success"] is False
assert payload["exit_code"] == 3
assert payload["reasons"] == [
    "check_error:branche de provenance du manifeste incohérente"
]
PY
```

Expected: code 3 connu de provenance/digest sur branche dédiée. Ne pas régénérer, invalider ou relier un manifeste observé dans ce lot.

- [ ] **Step 3: Construire un clone temporaire attesté sans forcer une branche**

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-gates-pointer.*' ! -name '*.complete' -print)
test "${#POINTERS[@]}" -eq 1
POINTER=${POINTERS[0]}
test -O "$POINTER"; test ! -L "$POINTER"; test "$(stat -c '%a' "$POINTER")" = 600
GATE_TMP=$(cat "$POINTER")
case "$GATE_TMP" in /tmp/nexus-openrouter-gates.*) ;; *) exit 1 ;; esac
test -d "$GATE_TMP"; test -O "$GATE_TMP"; test ! -L "$GATE_TMP"; test "$(stat -c '%a' "$GATE_TMP")" = 700
cd "$IMPL_ROOT"
mapfile -t VP < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print); test "${#VP[@]}" -eq 1
VR=$(cat "${VP[0]}"); export PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker"
FINAL_SHA=$(git rev-parse HEAD)
RELEASE_CLONE=$(mktemp -d /tmp/nexus-openrouter-release-final.XXXXXX)
git clone --shared --no-checkout "$IMPL_ROOT" "$RELEASE_CLONE/repo"
if git -C "$RELEASE_CLONE/repo" show-ref --verify --quiet \
  refs/heads/integration/1spe-bo2026-traceability
then
  printf '%s\n' 'HARD STOP: branche locale temporaire déjà présente' >&2
  exit 1
fi
git -C "$RELEASE_CLONE/repo" branch integration/1spe-bo2026-traceability "$FINAL_SHA"
git -C "$RELEASE_CLONE/repo" symbolic-ref HEAD refs/heads/integration/1spe-bo2026-traceability
git -C "$RELEASE_CLONE/repo" read-tree -mu HEAD
test "$(git -C "$RELEASE_CLONE/repo" rev-parse HEAD)" = "$FINAL_SHA"
printf '%s\n' "$RELEASE_CLONE" > "$GATE_TMP/release-clone-path"
mapfile -t BASELINE_POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-baseline-pointer.*' ! -name '*.complete' -print)
test "${#BASELINE_POINTERS[@]}" -eq 1
BASELINE_POINTER=${BASELINE_POINTERS[0]}
test -O "$BASELINE_POINTER"; test ! -L "$BASELINE_POINTER"
BASELINE_ROOT=$(cat "$BASELINE_POINTER")
test -d "$BASELINE_ROOT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL python3 - "$BASELINE_ROOT/release-strict.json" "$GATE_TMP/release-baseline-reasons.json" <<'PY'
import json
import sys
payload = json.load(open(sys.argv[1], encoding="utf-8"))
reasons = payload.get("reasons") or payload.get("blockers")
assert isinstance(reasons, list) and len(reasons) == 67
with open(sys.argv[2], "w", encoding="utf-8") as handle:
    json.dump(sorted(reasons, key=lambda row: json.dumps(row, sort_keys=True, ensure_ascii=False)), handle, ensure_ascii=False, indent=2)
PY
```

Expected: clone partagé temporaire au SHA exact, branche locale créée sans `-f`, aucun changement dans le worktree d’implémentation.

- [ ] **Step 4: Rejouer `release-strict` dans le clone temporaire**

```bash
set -euo pipefail
mapfile -t POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-gates-pointer.*' ! -name '*.complete' -print)
test "${#POINTERS[@]}" -eq 1
POINTER=${POINTERS[0]}
test -O "$POINTER"; test ! -L "$POINTER"; test "$(stat -c '%a' "$POINTER")" = 600
GATE_TMP=$(cat "$POINTER")
case "$GATE_TMP" in /tmp/nexus-openrouter-gates.*) ;; *) exit 1 ;; esac
test -d "$GATE_TMP"; test -O "$GATE_TMP"; test ! -L "$GATE_TMP"; test "$(stat -c '%a' "$GATE_TMP")" = 700
mapfile -t VP < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print); test "${#VP[@]}" -eq 1
VR=$(cat "${VP[0]}"); export PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker"
RELEASE_CLONE=$(cat "$GATE_TMP/release-clone-path")
test -d "$RELEASE_CLONE/repo"
set +e
(
  cd "$RELEASE_CLONE/repo"
  env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL python3 scripts/inventory_collection.py \
    --release-strict \
    --audit-dir "$RELEASE_CLONE/audit" \
    --etat-path "$RELEASE_CLONE/ETAT_COLLECTION.md"
) > "$GATE_TMP/release-strict.json" 2> "$GATE_TMP/release-strict.err"
RELEASE_RC=$?
set -e
test "$RELEASE_RC" -eq 7
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL python3 - "$GATE_TMP/release-strict.json" "$GATE_TMP/release-current-reasons.json" <<'PY'
import json
import sys

payload = json.load(open(sys.argv[1], encoding="utf-8"))
assert payload["gate"] == "release-strict"
assert payload["success"] is False
assert payload["blocker_count"] == 67
reasons = payload.get("reasons") or payload.get("blockers")
assert isinstance(reasons, list) and len(reasons) == 67
with open(sys.argv[2], "w", encoding="utf-8") as handle:
    json.dump(sorted(reasons, key=lambda row: json.dumps(row, sort_keys=True, ensure_ascii=False)), handle, ensure_ascii=False, indent=2)
PY
cmp "$GATE_TMP/release-baseline-reasons.json" "$GATE_TMP/release-current-reasons.json"
mv -- "$POINTER" "$POINTER.complete"
test -f "$POINTER.complete"; test -O "$POINTER.complete"; test ! -L "$POINTER.complete"; test "$(stat -c '%a' "$POINTER.complete")" = 600
mapfile -t ACTIVE_GATES_AFTER < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-gates-pointer.*' ! -name '*.complete' -print)
test "${#ACTIVE_GATES_AFTER[@]}" -eq 0
mapfile -t BASELINE_POINTERS < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-baseline-pointer.*' ! -name '*.complete' -print)
test "${#BASELINE_POINTERS[@]}" -eq 1
```

Expected: code 7 et 67 bloqueurs réels inchangés. Le pointeur gates propre à ce run devient `.complete`, donc un rejeu crée un nouveau pointeur ; le pointeur baseline reste actif jusqu’à la preuve finale de Task 23. Une variation de compte ou de cause est `HARD STOP` et doit être auditée, pas requalifiée.

### Task 23: Revue finale et compte rendu de session

**Files:** aucune modification attendue.

- [ ] **Step 1: Lancer une revue conformité holistique**

Un agent frais retrouve le parent du commit `[TESTS] verrouille la passerelle OpenRouter`, compare la totalité de `<parent>..HEAD` à la spécification approuvée, fichier par fichier, et vérifie : unicité réseau, unicité transport, mode local, séparation RAG/LLM, traçabilité honnête, quatre commits canoniques atomiques, éventuels commits de revue ciblés, aucune surface §8.4 oubliée et aucun gate affaibli.

- [ ] **Step 2: Lancer une revue qualité/sécurité holistique**

Un second agent frais cherche défauts de validation, fuite de clé/prompt, redirection, retry caché, type `bool`, NaN, réponse partielle, shadow import, données de confiance écrasables, transport RAG migré par erreur, journal v1 altéré, formule tarifaire ou écriture historique. Corriger tout constat validé dans un commit ciblé supplémentaire dont le sujet n’est jamais l’un des quatre sujets canoniques. Si la correction touche un fichier corpus suivi, reprendre Tasks 17–18 : le run précédent est `.complete`, donc Task 17 crée un nouveau pointeur ; Task 18 ne crée le commit `[AUDIT] ... apres revue` que pour un delta exact de deux sorties et ne committe rien pour un delta nul.

Avant de reprendre Task 19 après une correction, fermer de façon récupérable le pointeur de vérification du run invalidé : exiger l’unique pointeur actif, propriétaire/non-lien/mode 600 et une racine `/tmp/nexus-openrouter-verify.*` propriétaire/non-lien/mode 700, puis `mv -- "$POINTER" "$POINTER.complete"`. Task 19 crée alors un nouveau garde/pointeur. Reprendre Tasks 19–22 et les deux revues jusqu’à zéro constat. Sans correction, conserver le pointeur actif courant pour Step 3.

- [ ] **Step 3: Vérifier le statut final**

Après les revues et leurs éventuelles corrections, rejouer obligatoirement Tasks 19 Step 2 à 6 puis Tasks 20 à 22 sous le dernier `sitecustomize`. Même si aucun fichier n’a été corrigé, exécuter ensuite ce bloc final autonome, sans modification de test :

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
mapfile -t VP < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print); test "${#VP[@]}" -eq 1
VR=$(cat "${VP[0]}"); export PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker" \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_openrouter_client.py tests/test_openrouter_classification.py tests/test_external_provider_policy.py
cd "$IMPL_ROOT/Mathematiques/manuel-maths"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker" \
  python3 -m pytest -q -p no:cacheprovider tests/test_ingest_openrouter.py
cd "$IMPL_ROOT/NSI"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker" \
  python3 -m pytest -q -p no:cacheprovider tests/test_ingest_openrouter.py
cd "$IMPL_ROOT/NSI/corpus_nsi"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker" \
  python3 -m pytest -q -p no:cacheprovider \
  tests/test_rag_governance_and_indexes.py tests/test_secret_guard.py \
  tests/test_openrouter_judges.py tests/test_substance_judge_pipeline.py \
  tests/test_substance_hardened.py tests/test_judge_collection_barriers.py \
  tests/test_policy_checker_ast.py tests/test_manifest_separation.py
cd "$IMPL_ROOT"
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker" \
  python3 -m py_compile \
  nexus_external/__init__.py nexus_external/openrouter_client.py nexus_external/classification.py \
  Mathematiques/manuel-maths/scripts/ingest.py NSI/scripts/ingest.py \
  NSI/corpus_nsi/scripts/judge_campaign.py NSI/corpus_nsi/scripts/substance_judge.py \
  NSI/corpus_nsi/scripts/run_substance_judge.py NSI/corpus_nsi/scripts/check_rag_config.py
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker" \
  python3 -m ruff check \
  nexus_external Mathematiques/manuel-maths/scripts/ingest.py NSI/scripts/ingest.py \
  NSI/corpus_nsi/scripts/judge_campaign.py NSI/corpus_nsi/scripts/substance_judge.py \
  NSI/corpus_nsi/scripts/run_substance_judge.py NSI/corpus_nsi/scripts/check_rag_config.py
env -u OPENROUTER_API_KEY -u OPENROUTER_MODEL -u ANTHROPIC_API_KEY -u LOCAL_LLM_BASE_URL \
  PYTHONPATH="$VR/guard" NEXUS_NETWORK_GUARD_MARKER="$VR/sitecustomize.marker" \
  python3 - <<'PY'
import subprocess
canonical = (
    "[TESTS] verrouille la passerelle OpenRouter",
    "[PYTHON] centralise les appels LLM via OpenRouter",
    "[DOCS] aligne les autorites sur OpenRouter",
    "[AUDIT] resynchronise l inventaire outillage OpenRouter",
)
subjects = subprocess.check_output(["git", "log", "--format=%s"], text=True).splitlines()
for subject in canonical:
    assert subjects.count(subject) == 1, (subject, subjects.count(subject))
PY
test -s "$VR/sitecustomize.marker"
VERIFY_POINTER=${VP[0]}
test -O "$VERIFY_POINTER"; test ! -L "$VERIFY_POINTER"; test "$(stat -c '%a' "$VERIFY_POINTER")" = 600
mv -- "$VERIFY_POINTER" "$VERIFY_POINTER.complete"
test -f "$VERIFY_POINTER.complete"; test -O "$VERIFY_POINTER.complete"; test ! -L "$VERIFY_POINTER.complete"
mapfile -t BP < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-baseline-pointer.*' ! -name '*.complete' -print); test "${#BP[@]}" -eq 1
BASELINE_POINTER=${BP[0]}; test -O "$BASELINE_POINTER"; test ! -L "$BASELINE_POINTER"; test "$(stat -c '%a' "$BASELINE_POINTER")" = 600
mv -- "$BASELINE_POINTER" "$BASELINE_POINTER.complete"
mapfile -t ACTIVE_VERIFY < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-verify-pointer.*' ! -name '*.complete' -print); test "${#ACTIVE_VERIFY[@]}" -eq 0
mapfile -t ACTIVE_BASELINE < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-baseline-pointer.*' ! -name '*.complete' -print); test "${#ACTIVE_BASELINE[@]}" -eq 0
mapfile -t ACTIVE_GATES < <(find /tmp -maxdepth 1 -user "$(id -u)" -type f -name 'nexus-openrouter-gates-pointer.*' ! -name '*.complete' -print); test "${#ACTIVE_GATES[@]}" -eq 0
```

Expected: quatre suites exactes vertes, policy complète incluse dans les 47 nodes core, `py_compile` et Ruff verts, marker non vide, quatre sujets canoniques présents exactement une fois. Les pointeurs verification et baseline deviennent `.complete` seulement après toutes les preuves ; aucun pointeur gates actif ne reste.

```bash
set -euo pipefail
IMPL_ROOT=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-openrouter-only
cd "$IMPL_ROOT"
git status --short --branch
git diff --check
test -z "$(git status --short)"
git log --oneline --decorate -8
```

Expected: worktree propre. Ne pas pousser, fusionner, rebaser ou intégrer à Wave 0 sans nouvelle instruction humaine.

- [ ] **Step 4: Produire le compte rendu contractuel**

Renseigner avec les valeurs réellement observées, sans écrire « terminé » si une preuve manque :

```text
ÉTAT <SHA>
Branche : green/openrouter-only
Phase : migration OpenRouter exclusive — implémentation isolée
Commits : <liste SHA/messages>
Tests : <quatre processus ciblés + corpus manifest + mutations>
Gates verts : <policy, Ruff, py_compile, inventaire corpus, historique>
Gates rouges : collecte racine assemble.BOOK_VARIANTS ; inventaire direct code 3 provenance/digest ; release-strict code 7 avec 67 bloqueurs
P0 ouverts : inchangés ; ce lot ne corrige aucun P0 Wave 0
Décisions humaines : approche B approuvée ; smoke OpenRouter réel non exécuté ; intégration non autorisée
PR : non ouverte
Prochaine action : décision humaine sur intégration de la branche ou smoke séparé
```

Plan complete and saved to `docs/superpowers/plans/2026-08-13-openrouter-only-external-provider.md`. Ready to execute with `superpowers:subagent-driven-development` using a fresh implementer per task and two-stage review.
