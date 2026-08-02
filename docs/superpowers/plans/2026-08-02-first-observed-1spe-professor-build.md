# First Observed 1SPE Professor Build Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Instrumenter l'assembleur réel du manuel 1SPE professeur, produire un
PDF localement déterministe et une preuve post-préflight liée au journal et au
`.fls`, puis versionner séparément le PDF et son build observé sans modifier la
baseline visuelle ni rendre la collection publiable.

**Architecture:** L'assembleur génère un maître LaTeX marqué par le protocole
Phase 0 existant, compile trois fois avec `-recorder`, effectue le préflight et
écrit atomiquement un rapport puis un reçu liés par `run_id` et digests. Le
recorder racine revalide toutes les preuves, versions d'outils et états Git,
puis remplace en une transaction le manifeste vide périmé par l'enveloppe
courante et le premier build. Le chargeur accepte ensuite le SHA source comme
ancêtre de HEAD uniquement si branche, digests, PDF et dépendances sont restés
identiques.

**Tech Stack:** Python 3.12, pytest, LuaLaTeX, Poppler (`pdfinfo`, `pdffonts`),
JSON Schema, Git.

**Design approuvé :**
`docs/superpowers/specs/2026-08-02-first-observed-1spe-professor-build-design.md`

**Contraintes absolues :**

- aucun fichier PNG, oracle ou baseline visuelle ne doit changer ;
- aucun gate n'est supprimé, assoupli ou converti en `skip`/`xfail` ;
- `observed_build_integration.status` reste `not_integrated` ;
- `release-strict` doit rester rouge pour les dettes réelles ;
- le PDF et le manifeste sont deux commits distincts ;
- toute étape de production part d'un worktree propre ;
- le secret OpenRouter reste dans `.env`, ignoré, et n'entre dans aucun test,
  reçu, log ou commit.

---

## Chunk 1: Producteur instrumenté et preuves atomiques

### Task 0: Consigner le plan revu

**Files:**
- Create: `docs/superpowers/plans/2026-08-02-first-observed-1spe-professor-build.md`

- [ ] **Step 1: Vérifier le document et l'état Git**

Run:

```bash
git status --short --branch
git diff --check
git diff --stat
```

Expected: seul le présent plan est nouveau ; aucune baseline visuelle n'est
modifiée.

- [ ] **Step 2: Committer le plan seul**

```bash
git add docs/superpowers/plans/2026-08-02-first-observed-1spe-professor-build.md
git diff --cached --check
git diff --cached --stat
git commit -m "[DOCS] planifie le premier build observé 1SPE"
```

Expected: commit documentaire atomique.

### Task 1: Contractualiser le maître marqué

**Files:**
- Modify: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
- Create: `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py`
- Test: `tests/test_build_manifest.py`

- [ ] **Step 1: Écrire les tests RED du protocole**

Charger l'assembleur par son chemin réel et construire une fixture de petit
manuel. Tester :

- le chemin hashé est relatif à la racine Git et commence par
  `Mathematiques/manuel-maths/` ;
- le token produit par l'assembleur est exactement celui de
  `scripts.build_manifest._object_trace_token` ;
- chaque objet possède exactement un
  `NEXUS_OBJECT_BEGIN:<40 hex>` puis un `NEXUS_OBJECT_END:<même token>` ;
- le maître porte un unique `NEXUS_BUILD_RUN:<32 hex>` ;
- les objets restent dans l'ordre de `collect_chapter` ;
- la collecte réelle professeur contient 870 objets et son ordre est identique
  à `math:manual:1SPE:professeur` dans l'inventaire ;
- un chemin absolu, `..`, un backslash ou un lien symbolique est refusé.

- [ ] **Step 2: Vérifier RED**

```bash
python -m pytest \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  tests/test_build_manifest.py \
  -q -k 'master or marker or trace_token or declared_professor_order'
```

Expected: FAIL car l'assembleur n'émet aucun marqueur ni `run_id`.

- [ ] **Step 3: Extraire des fonctions pures minimales**

Dans `assemble_manuel.py`, ajouter des fonctions testables pour :

- résoudre la racine Git par `git rev-parse --show-toplevel` ;
- canoniser un chemin suivi sous cette racine sans symlink ;
- calculer `sha256(path_utf8)[:40]` ;
- envelopper un `\input` avec les deux `\typeout` contractuels ;
- rendre le maître complet à partir du variant et du `run_id`.

Ne pas modifier le contenu éditorial ni l'ordre actuel. Les `\input` transversaux
ne sont pas des objets de l'assemblage déclaré et ne reçoivent pas de marqueur
d'objet.

- [ ] **Step 4: Vérifier GREEN ciblé**

Relancer la commande de l'étape 2.

Expected: PASS.

- [ ] **Step 5: Committer le protocole seul**

```bash
git diff --check
git add \
  Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py
git diff --cached --check
git commit -m "[LATEX] trace les objets du manuel 1SPE"
```

### Task 2: Arrêter correctement les passes et produire les preuves

**Files:**
- Modify: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
- Modify: `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py`

- [ ] **Step 1: Écrire les tests RED d'orchestration**

Avec un runner de subprocess factice, tester :

- trois appels réussis et `-recorder` dans chacun ;
- l'arrêt après la première ou la deuxième passe rouge ;
- aucun préflight et aucun reçu après un échec ;
- suppression au démarrage d'un ancien reçu de succès ;
- `verify_pdf` exécuté après les trois passes ;
- absence de reçu si `verify_pdf`, `pdfinfo` ou `pdffonts` échoue ;
- collecte déterministe des versions de LuaLaTeX, `pdfinfo`, `pdffonts` et
  Python ;
- le mode sans `--record-observed` ne lance jamais le recorder racine.

- [ ] **Step 2: Vérifier RED**

```bash
python -m pytest \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  -q -k 'recorder or pass or preflight or tool_versions'
```

Expected: FAIL, notamment parce que l'assembleur actuel poursuit après les deux
premiers retours non nuls et omet `-recorder`.

- [ ] **Step 3: Implémenter l'orchestration minimale**

Ajouter `--record-observed` à la CLI et propager un booléen à `main`. Pour
chaque passe :

```python
command = [
    "lualatex",
    "-interaction=nonstopmode",
    "-halt-on-error",
    "-recorder",
    f"-output-directory={build}",
    str(tex_path),
]
```

Retourner immédiatement `1` sur tout échec. Ne créer le rapport et le reçu que
si les trois passes et le préflight ont réussi.

- [ ] **Step 4: Écrire les tests RED du rapport et du reçu atomiques**

Tester les formes exactes :

```json
{
  "run_id": "<32 hex>",
  "pdf_path": "<chemin Git>",
  "pdf_sha256": "sha256:<64 hex>",
  "page_count": 0,
  "passed": true,
  "checks": {},
  "tool_versions": {}
}
```

et le reçu étendu par :

```json
{
  "run_id": "<32 hex>",
  "master_path": "<chemin Git>",
  "evidence_sha256": {
    "master": "sha256:<64 hex>",
    "log": "sha256:<64 hex>",
    "fls": "sha256:<64 hex>",
    "pdf": "sha256:<64 hex>",
    "preflight": "sha256:<64 hex>"
  }
}
```

Ajouter des tests simulant un échec de `Path.replace` : l'ancien fichier doit
rester intact, le temporaire doit être supprimé et aucun demi-JSON ne doit être
visible.

- [ ] **Step 5: Vérifier RED puis implémenter l'écriture atomique**

```bash
python -m pytest \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  -q -k 'atomic or receipt or evidence or preflight_report'
```

Implémenter l'écriture dans un temporaire du même répertoire, `flush`, `fsync`,
`Path.replace`, puis nettoyage garanti. Hasher le rapport seulement après sa
publication atomique ; écrire ensuite le reçu.

- [ ] **Step 6: Tester la frontière CLI du recorder**

Le test doit exiger une commande de la forme :

```text
<python courant> <racine-git>/scripts/build_manifest.py --receipt <reçu exact>
```

Un retour non nul est propagé. Le test doit également vérifier que la clé API et
les variables `.env` ne sont jamais sérialisées.

- [ ] **Step 7: Vérifier GREEN et lint ciblé**

```bash
python -m pytest \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py -q
python -m ruff check \
  Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py
```

Expected: PASS.

- [ ] **Step 8: Committer l'orchestration**

```bash
git diff --check
git add \
  Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py
git commit -m "[PDF] produit le reçu post-préflight 1SPE"
```

---

## Chunk 2: Recorder sécurisé et provenance durable

### Task 3: Étendre et revérifier le contrat du reçu

**Files:**
- Modify: `scripts/build_manifest.py`
- Modify: `tests/test_build_manifest.py`

- [ ] **Step 1: Mettre les fixtures au nouveau contrat et écrire les tests RED**

Étendre `_RECEIPT_FIELDS` et la fixture `_receipt()` avec `run_id`,
`master_path` et `evidence_sha256`. Ajouter les rejets suivants :

- clé absente ou supplémentaire ;
- `run_id` mal formé ;
- ensemble de clés digest incomplet ou ouvert ;
- digest master/log/FLS/PDF/préflight faux ;
- `run_id` différent dans le maître, le journal ou le rapport ;
- maître absent des `INPUT` du `.fls` ;
- maître, preuve ou objet via symlink / `..` / chemin absolu ;
- version d'outil manquante, forgée ou différente du recalcul local ;
- entrée TeX Live absolue supplémentaire ignorée ;
- preuve modifiée pendant la validation finale.

Utiliser les helpers de fichiers confinés existants, pas des lectures libres par
`Path.read_bytes()` dans le recorder.

- [ ] **Step 2: Vérifier RED**

```bash
python -m pytest tests/test_build_manifest.py -q \
  -k 'receipt and (run_id or evidence or tool_versions or master or texlive or revalidate)'
```

Expected: FAIL car le contrat actuel ne possède pas ces liaisons.

- [ ] **Step 3: Implémenter la validation cryptographique**

Ajouter des helpers purs pour :

- valider `run_id` et les SHA-256 préfixés ;
- hasher les octets ouverts par `_read_proof_file` ;
- collecter localement les quatre versions d'outils avec timeouts ;
- valider la forme fermée du préflight ;
- vérifier le marqueur `NEXUS_BUILD_RUN` du maître et du journal ;
- exiger `master_path` dans les entrées Git-canoniques du `.fls` ;
- capturer les digests initiaux de toutes les preuves et les recalculer dans le
  callback `validator` avant publication du manifeste.

Les entrées absolues externes du `.fls` restent ignorées. Un objet déclaré, le
maître ou une dépendance générée revendiquée ne peut jamais être externe.

- [ ] **Step 4: Vérifier GREEN et la non-régression du recorder**

```bash
python -m pytest tests/test_build_manifest.py -q
python -m ruff check scripts/build_manifest.py tests/test_build_manifest.py
```

Expected: tous les tests du module passent.

- [ ] **Step 5: Committer le contrat du reçu**

```bash
git diff --check
git add scripts/build_manifest.py tests/test_build_manifest.py
git commit -m "[AUDIT] lie le reçu aux preuves de compilation"
```

### Task 4: Activer la première transaction observée

**Files:**
- Modify: `scripts/build_manifest.py`
- Modify: `tests/test_build_manifest.py`

- [ ] **Step 1: Remplacer le test sentinelle par les tests RED de succès**

Le test historique
`test_receipt_entrypoint_refuses_publication_without_build_wrapper` devient une
famille qui exige :

- refus si le dépôt est sale avant la commande ;
- succès depuis un dépôt propre et un manifeste valide vide mais périmé ;
- enveloppe proposée au HEAD courant avec `dirty=false` ;
- ajout exact d'un seul build ;
- refus d'une enveloppe périmée si le manifeste contient déjà un build ;
- rollback octet exact en cas de validation ou remplacement simulé en échec ;
- rejet d'un doublon manuel/variante ;
- message CLI `build manifest enregistré` et code `0` au succès.

- [ ] **Step 2: Vérifier RED**

```bash
python -m pytest tests/test_build_manifest.py -q \
  -k 'receipt_entrypoint or first_observed or refreshes_empty or dirty_repository'
```

Expected: FAIL sur la sentinelle « intégration assembleur non activée ».

- [ ] **Step 3: Implémenter la transaction minimale**

Dans `record_from_receipt()` :

1. résoudre la racine et refuser un état Git sale ;
2. lire et valider le reçu ;
3. dériver enveloppe, build et validateur ;
4. appeler `record_successful_build()` avec une capacité interne explicite qui
   autorise uniquement le remplacement d'un manifeste valide et vide ;
5. pour tout manifeste non vide, conserver `_same_envelope` strict ;
6. ne jamais exposer cette capacité dans la CLI.

La vérification propreté intervient avant toute écriture. La transaction doit
continuer à épingler l'état Git et le fingerprint des preuves.

- [ ] **Step 4: Vérifier GREEN et le rollback complet**

```bash
python -m pytest tests/test_build_manifest.py -q \
  -k 'receipt or record_successful_build or transaction or rollback'
```

Expected: PASS.

- [ ] **Step 5: Committer l'activation**

```bash
git diff --check
git add scripts/build_manifest.py tests/test_build_manifest.py
git commit -m "[AUDIT] active le premier build observé"
```

### Task 5: Autoriser une provenance ancêtre sans l'affaiblir

**Files:**
- Modify: `scripts/inventory_collection.py`
- Modify: `tests/test_build_manifest.py`
- Modify: `tests/test_inventory_collection.py` seulement si un test de gate
  généré exige une adaptation explicite.

- [ ] **Step 1: Écrire les tests RED de cycle Git**

Dans de vrais dépôts Git temporaires, couvrir :

- build enregistré au commit B puis manifeste commité au commit C : accepté ;
- commit D ne modifiant qu'un rapport géré : accepté ;
- SHA de provenance ou `build.git_sha` non ancêtre : rejeté ;
- branche différente : rejetée ;
- manifeste déclarant `dirty=true` : rejeté pour un build réel ;
- source, modèle, PDF, pagination ou dépendance modifiés : rejetés ;
- HEAD remplacé pendant la validation : rejeté ;
- `observed_build_integration.status` reste exactement `not_integrated` et le
  release gate conserve `build_receipt_producteurs_non_intégrés`.

- [ ] **Step 2: Vérifier RED**

```bash
python -m pytest tests/test_build_manifest.py tests/test_inventory_collection.py \
  -q -k 'ancestor or committed_manifest or observed_build_integration or build_receipt_producteurs'
```

Expected: FAIL car le chargeur exige actuellement le HEAD exact pour un
manifeste non vide.

- [ ] **Step 3: Implémenter le prédicat d'ascendance centralisé**

Créer un helper qui appelle :

```text
git merge-base --is-ancestor <sha-enregistré> <head-courant>
```

Exiger le code `0`, l'existence d'un SHA à 40 hex, la branche exacte et
`provenance.dirty == false`. Appliquer ce contrôle au SHA de provenance et à
chaque `build.git_sha`. Ne toucher ni aux contrôles de digests, ni au PDF, ni
aux dépendances, ni aux revalidations TOCTOU.

- [ ] **Step 4: Vérifier GREEN et les gates ciblés**

```bash
python -m pytest tests/test_build_manifest.py tests/test_inventory_collection.py -q
python -m ruff check \
  scripts/build_manifest.py scripts/inventory_collection.py \
  tests/test_build_manifest.py tests/test_inventory_collection.py
```

Expected: PASS ; le statut d'intégration et la raison release restent
inchangés.

- [ ] **Step 5: Committer la provenance**

```bash
git diff --check
git add \
  scripts/inventory_collection.py \
  tests/test_build_manifest.py \
  tests/test_inventory_collection.py
git commit -m "[AUDIT] accepte la provenance Git ancestrale"
```

### Task 6: Vérifier l'intégration avant production réelle

**Files:** aucun attendu.

- [ ] **Step 1: Lancer les suites ciblées complètes**

```bash
python -m pytest \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  tests/test_build_manifest.py \
  tests/test_inventory_collection.py -q
```

Expected: PASS.

- [ ] **Step 2: Lancer lint, données et diff**

```bash
python -m ruff check \
  scripts \
  Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  tests/test_build_manifest.py tests/test_inventory_collection.py
python scripts/ci_audit_collection.py validate-data \
  --root . --output /tmp/nexus-observed-build-structured-data.json
git diff --check
git status --short
```

Expected: PASS et worktree propre. Si un test impose une correction, appliquer
TDD et créer un commit de code ciblé avant le build réel.

---

## Chunk 3: PDF versionné puis manifeste observé

### Task 7: Produire et committer le PDF professeur

**Files:**
- Create (force-add):
  `Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf`

- [ ] **Step 1: Refaire le préflight Git obligatoire**

```bash
git status --short --branch
git rev-parse HEAD
git log --oneline --decorate -15
git diff --stat
git diff --check
```

Expected: worktree propre sur `finalisation/collection-v1`.

- [ ] **Step 2: Compiler sans enregistrer le manifeste**

```bash
python Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  --variant professeur
```

Expected: code `0`, trois passes réussies, préflight PDF vert, aucun changement
de `audit/BUILD_MANIFEST.json`.

- [ ] **Step 3: Inspecter le PDF et sa taille**

```bash
pdfinfo Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf
pdffonts Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf
sha256sum Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf
stat --format='%s' Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf
```

Expected: PDF lisible, polices incorporées et taille strictement inférieure à
94 371 840 octets (90 Mio). Au-delà, arrêter et demander une décision humaine.

- [ ] **Step 4: Ajouter uniquement le PDF ignoré et committer**

```bash
git add -f -- \
  Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf
git diff --cached --check
git diff --cached --stat
git status --short
git commit -m "[PDF] versionne le manuel 1SPE professeur"
```

Expected: un commit contenant exactement le PDF. Aucun `.log`, `.fls`, maître,
reçu ou rapport de préflight n'est suivi.

### Task 8: Rebuilder à l'identique et enregistrer le manifeste

**Files:**
- Modify: `audit/BUILD_MANIFEST.json`

- [ ] **Step 1: Capturer l'identité versionnée et lancer le build observé**

```bash
git status --short --branch
git rev-parse HEAD
git hash-object \
  Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf
python Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  --variant professeur --record-observed
```

Expected: code `0`; le recorder accepte le reçu et modifie uniquement le
manifeste suivi. Les artefacts techniques restent ignorés.

- [ ] **Step 2: Prouver l'identité du second PDF**

```bash
git diff --exit-code -- \
  Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf
git hash-object \
  Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf
```

Expected: aucun diff et même object ID Git qu'avant le build. En cas de dérive,
ne modifier aucune baseline ; diagnostiquer le déterminisme avant de continuer.

- [ ] **Step 3: Vérifier le manifeste observé**

```bash
python -m json.tool audit/BUILD_MANIFEST.json >/dev/null
python - <<'PY'
import json
from pathlib import Path

payload = json.loads(Path("audit/BUILD_MANIFEST.json").read_text(encoding="utf-8"))
assert len(payload["builds"]) == 1
build = payload["builds"][0]
assert (build["manual"], build["variant"]) == ("1SPE", "professeur")
assert len(build["ordered_trace"]) == 870
assert build["ordered_trace"] == build["included_objects"]
PY
git diff --check
git status --short
```

Expected: le manifeste contient exactement un build `1SPE/professeur`, 870
objets dans l'ordre, le digest et la pagination du PDF courant. Aucun fichier
visuel n'est modifié. Les gates dérivés sont exécutés après régénération des
rapports, afin que `--check` ne compare pas volontairement un modèle nouveau à
des sorties encore anciennes.

- [ ] **Step 4: Committer le manifeste seul**

```bash
git add audit/BUILD_MANIFEST.json
git diff --cached --check
git diff --cached --stat
git diff --cached --name-only
git commit -m "[AUDIT] atteste le build professeur 1SPE"
```

Expected: commit atomique du manifeste uniquement.

### Task 9: Régénérer les rapports dérivés sans baseline visuelle

**Files:**
- Modify only if generated:
  `ETAT_COLLECTION.md`
- Modify only if generated: `audit/INVENTAIRE_COLLECTION.json`
- Modify only if generated: `audit/INVENTAIRE_COLLECTION.md`
- Modify only if generated: `audit/ECARTS_ET_CONTRADICTIONS.yaml`
- Modify only if generated: `audit/MATRICE_LIVRABLES.yaml`
- Modify only if generated: `audit/AUDIT_CONSOLIDE.md`

- [ ] **Step 1: Générer depuis le nouveau manifeste**

```bash
python scripts/inventory_collection.py
git diff --check
git status --short
```

Expected: seules les sorties d'inventaire prévues peuvent changer. Le statut
`not_integrated` et `release_acceptance=false` demeurent.

- [ ] **Step 2: Refuser tout changement visuel**

```bash
git diff --name-only | rg \
  '(^|/)(validations?|visual|baselines?)/|\.png$|\.jpg$|\.jpeg$'
```

Expected: aucune sortie. Si la commande trouve un chemin, arrêter sans le
restaurer automatiquement et investiguer.

- [ ] **Step 3: Committer les rapports gérés si nécessaire**

Stage uniquement les sorties réellement modifiées, vérifier le diff, puis :

```bash
git commit -m "[AUDIT] publie l'état du build observé 1SPE"
```

Si aucun rapport ne change, ne créer aucun commit vide.

---

## Chunk 4: Gates, revue, push et état NO-GO

### Task 10: Exécuter les vérifications finales

**Files:** aucun attendu.

- [ ] **Step 1: Tests ciblés et suite complète**

```bash
python -m pytest \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  tests/test_build_manifest.py tests/test_inventory_collection.py -q
python -m pytest --import-mode=importlib
```

Expected: tests ciblés verts ; suite complète verte hors skips documentés. Ne
pas masquer une régression par `skip` ou `xfail`.

- [ ] **Step 2: Lint, typage et données**

```bash
python -m ruff check \
  scripts \
  Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  tests/test_build_manifest.py tests/test_inventory_collection.py
python -m mypy --cache-dir /tmp/nexus-observed-build-mypy
python scripts/ci_audit_collection.py validate-data \
  --root . --output /tmp/nexus-observed-build-structured-data-final.json
```

Expected: PASS.

- [ ] **Step 3: Gates Phase 0 et release rouge contrôlé**

```bash
python scripts/ci_audit_collection.py run-gates \
  --root . \
  --output-dir /tmp/nexus-observed-build-gates \
  --require-clean \
  --check \
  --validate-model \
  --fail-on-new \
  --release-strict
```

Expected: orchestrateur code `0` parce qu'il exige les codes contractuels ;
`--check`, `--validate-model` et `--fail-on-new` sont verts ;
`--release-strict` produit exactement le code interne `7` avec les dettes
réelles, dont `build_receipt_producteurs_non_intégrés`. Le manuel reste NO-GO.

- [ ] **Step 4: Vérification finale du PDF et du diff**

```bash
python -m json.tool audit/BUILD_MANIFEST.json >/dev/null
pdfinfo Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf
pdffonts Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf
git diff --check
git status --short --branch
git log --oneline --decorate -15
```

Expected: worktree propre, PDF suivi, manifeste valide, aucune baseline
visuelle modifiée.

### Task 11: Revue indépendante et publication de branche

**Files:** aucune modification fonctionnelle attendue.

- [ ] **Step 1: Demander une revue de code indépendante**

Faire vérifier : sécurité des chemins, marqueurs, `.fls`, liaison des preuves,
TOCTOU, provenance ancêtre, atomicité, absence d'affaiblissement des gates et
absence de baseline visuelle. Corriger tout P0/P1 en TDD puis relancer Task 10.

- [ ] **Step 2: Pousser la branche autorisée**

```bash
git push origin finalisation/collection-v1
```

Expected: push non forcé réussi.

- [ ] **Step 3: Mettre à jour la PR existante**

La PR doit indiquer :

- le SHA du PDF et sa pagination ;
- les 870 objets croisés journal/FLS ;
- le second build octet-identique ;
- les tests et gates verts ;
- les limites de reproductibilité même hôte ;
- `release-strict` rouge, 69 bloqueurs à réévaluer après régénération ;
- aucune baseline visuelle modifiée ;
- aucune annonce « prêt à imprimer » ou « GO publication ».

- [ ] **Step 4: Compte rendu contractuel**

Terminer avec le format exact :

```text
ÉTAT <SHA>
Branche :
Phase :
Commits :
Tests :
Gates verts :
Gates rouges :
P0 ouverts :
Décisions humaines :
PR :
Prochaine action :
```
