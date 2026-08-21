# PDF Artifact Attribution Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Attribuer exactement les 22 PDF aujourd'hui sans attribution, sans inventer de producteur ni de preuve de compilation, tout en conservant les 12 instantanés de publication comme dette release explicite.

**Architecture:** Une autorité NSI réparée précède un registre fermé (`audit/PDF_ARTIFACT_REGISTRY.yaml`). Le registre complète l'attribution canonique seulement après son échec, vérifie chemin, rôle, audience éventuelle, provenance, SHA-256 et pagination sur le même snapshot, et dérive un blocker collection unique pour les 12 instantanés.

**Tech Stack:** Python 3.12, PyYAML, JSON Schema, pytest, Git object database, Poppler (`pdfinfo`), générateur d'inventaire Nexus.

---

## Task 1 — Sceller le design

**Files:**

- Add: `docs/superpowers/specs/2026-08-21-pdf-artifact-attribution-design.md`
- Add: `docs/superpowers/plans/2026-08-21-pdf-artifact-attribution.md`

- [ ] Vérifier les trois seuls rôles : `HISTORICAL_PUBLICATION_SNAPSHOT`, `OFFICIAL_PROGRAM_AUTHORITY`, `HARVEST_NON_PUBLISHABLE_HISTORICAL_RENDER`.
- [ ] Vérifier l'absence de rôle inconnu/fixture, faux producteur, qualification de baseline et preuve de compilation.
- [ ] Vérifier que `SOURCE_ROLES.yaml` et `BUILD_PRODUCERS.yaml` ne changent pas.
- [ ] Exécuter `git diff --check`.
- [ ] Commit :

  ```bash
  git add docs/superpowers/specs/2026-08-21-pdf-artifact-attribution-design.md \
    docs/superpowers/plans/2026-08-21-pdf-artifact-attribution.md
  git commit -m "[DOCS] define exact PDF artifact attribution"
  ```

## Task 2 — Réparer l'autorité NSI avant sa consommation

**Files:**

- Add: `tests/test_nsi_program_authority_bindings.py`
- Modify: `docs/programmes/PROGRAMMES_2026_2027.yaml`
- Modify: `NSI/sources/SOURCES.md`

### RED

- [ ] Tester les deux bindings complets : chemin suivi réel, SHA-256 du PDF, code `MENE1901633A`/`MENE1921247A`, clé `SRC-BO2019-NSI-PREMIERE`/`SRC-BO2019-NSI-TERMINALE`, page BO et URL d'annexe exactes.
- [ ] Exiger que les chemins soient `NSI/corpus_nsi/00_programmes_officiels/programme_nsi_premiere.pdf` et `programme_nsi_terminale.pdf`, et que `NSI/sources/SOURCES.md` cite les mêmes fichiers.
- [ ] CWD `<repo-root>`, lancer et archiver le RED causé par les deux chemins
  documentaires absents actuels :

  ```bash
  python -m pytest -q tests/test_nsi_program_authority_bindings.py
  ```

  RED attendu : rc non nul.

### GREEN

- [ ] Corriger seulement les deux entrées NSI du YAML canonique et les lignes correspondantes de `NSI/sources/SOURCES.md`; ne conclure ni applicabilité ni couverture T2.
- [ ] CWD `<repo-root>`, rejouer la même commande (GREEN attendu : rc0), parser
  le YAML et exécuter `git diff --check` (rc0).
- [ ] Commit autonome :

  ```bash
  git add tests/test_nsi_program_authority_bindings.py \
    docs/programmes/PROGRAMMES_2026_2027.yaml NSI/sources/SOURCES.md
  git commit -m "[PROGRAMME] bind NSI authority copies to official records"
  ```

Le loader du registre ne commence qu'après ce commit vert et lit cette autorité réparée.

## Task 3 — Ajouter le registre, son schéma et le dispatch exact

**Files:**

- Add: `audit/PDF_ARTIFACT_REGISTRY.yaml`
- Add: `audit/schemas/v1/pdf-artifact-registry.schema.json`
- Modify: `audit/schemas/v1/inventory-collection.schema.json`
- Modify: `scripts/inventory_graph.py`
- Modify: `scripts/inventory_pdf.py`
- Modify: `scripts/inventory_collection.py`
- Modify: `tests/test_inventory_collection.py`

### Microcycle A — Schéma, lecture stable et activation inconditionnelle

- [ ] RED fixtures : schéma fermé, contrôle digesté, ordre/chemin exacts,
  doublons et suppression simultanée registre+schéma+PDF. Le build doit exiger
  les deux contrôles par les références code/`SCHEMA_REGISTRY`, même sans PDF.
- [ ] RED sécurité : pour chacun de registre, schéma et YAML programme, tester
  séparément leaf symlink, leaf hardlink, parent symlink, substitution de
  parent, remplacement concurrent pendant la lecture et remplacement après
  lecture mais avant `_source_digest`.
- [ ] RED digest : appeler la fonction canonique avec des overrides contenant
  exactement les mêmes octets que les fichiers et exiger le digest historique
  bit-identique ; aucune seconde implémentation du préimage n'est permise.
- [ ] CWD `<repo-root>`, commande littérale RED puis GREEN :

  ```bash
  python -m pytest -q tests/test_inventory_collection.py -k 'pdf_artifact_registry_schema or pdf_artifact_registry_loader or stable_tracked_control'
  ```

  RED attendu : rc non nul sur les nouvelles assertions ; GREEN attendu : rc0.
- [ ] GREEN minimal : ouvrir racine et parents par `dir_fd` avec
  `O_DIRECTORY|O_NOFOLLOW`, ancrer dev/ino/mode/nlink, ouvrir le leaf avec
  `O_NOFOLLOW`, puis garder tous les fds jusqu'après validation et calcul des
  digests. `_source_digest` reçoit les bytes/digests épinglés par overrides et
  ne rouvre aucune des trois surfaces ; parents et leaf sont revalidés à la
  fin.
- [ ] Modifier uniquement `inventory_graph.source_digest()` pour accepter les
  overrides épinglés tout en conservant exactement le préimage historique ; le
  wrapper de `inventory_collection.py` délègue à cette fonction canonique.

### Microcycle B — Provenance des trois rôles

- [ ] RED fixtures snapshots : exiger `canonical_origin_path` et
  `canonical_origin_blob_oid`; à `e630c5ad...`, les deux chemins existent, les
  blobs sont identiques et `attribute_pdf(origin)` dérive le manual/variant du
  record.
- [ ] RED fixtures officiels/P13 : autorité NSI réparée, PDF et `build.sh`
  déclarés à `10a15746...`, sans source/préambule comme preuve ; tester aussi
  rôle, portée, manuel, chapitre, variante, release et audience.
- [ ] Tester les audiences exactes : `PROFESSOR_ONLY` pour corrige/td/tp et
  `STUDENT_FACING` pour aides/cours/evaluation/fiche_methode/trace.
- [ ] CWD `<repo-root>`, commande littérale RED puis GREEN :

  ```bash
  python -m pytest -q tests/test_inventory_collection.py -k 'pdf_artifact_registry_provenance or pdf_artifact_registry_audience'
  ```

  RED attendu : rc non nul ; GREEN attendu : rc0.
- [ ] GREEN minimal : créer les 22 records et valider les mutations de
  SHA/pages/blob, origine canonique, code/clé/URL, audience et recette déclarée.

### Microcycle C — Dispatch exact et TOCTOU PDF

- [ ] RED fixtures : lookup exact après échec de `attribute_pdf`, basename
  négatif, aucune attribution fuzzy, hash/pages issus du même snapshot PDF.
- [ ] RED fixtures : propagation `audience` sur P13 seulement et absence de
  compilation evidence pour les 22 records.
- [ ] CWD `<repo-root>`, commande littérale RED puis GREEN :

  ```bash
  python -m pytest -q tests/test_inventory_collection.py -k 'pdf_artifact_dispatch or pdf_artifact_toctou'
  ```

  RED attendu : rc non nul ; GREEN attendu : rc0.
- [ ] GREEN minimal : fallback exact, une seule inspection PDF, réutilisation
  du digest et des pages, puis projection des champs de registre.

### Microcycle D — Schéma inventaire et blocker

- [ ] RED fixtures : fermer `pdfs[]`, imposer `sha256` et `registry_digest`,
  imposer les huit audiences P13 et les interdire sur snapshots/officiels/
  non-registry.
- [ ] RED fixtures : dériver un seul blocker
  `COLLECTION:publication_snapshots:stale_undecided:12`; une égalité simulée
  avec le PDF canonique actuel ne ferme jamais l'état.
- [ ] CWD `<repo-root>`, commande littérale RED puis GREEN :

  ```bash
  python -m pytest -q tests/test_inventory_collection.py -k 'pdf_artifact_inventory_schema or publication_snapshots_blocker'
  ```

  RED attendu : rc non nul ; GREEN attendu : rc0.
- [ ] GREEN minimal : inclure registre, schéma et YAML programme dans
  `source_files`, et dériver le blocker depuis `pdfs` sans liste redondante,
  anomalie, qualification ou baseline.
- [ ] Écrire aussi
  `test_repository_pdf_artifact_registry_attribution`. Avant le commit partagé,
  l'exécuter seulement dans le clone temporaire explicitement rafraîchi
  ci-dessous ; dans le worktree partagé, attendre Task 8 après les commits
  manifest et inventaire.

### Frontière des artefacts gérés et commit

- [ ] Pendant ces microcycles, utiliser uniquement des fixtures ou des clones
  temporaires. Tout clone de forme dépôt doit recevoir explicitement le
  refresh manifest puis inventaire et des commits locaux avant un test avec
  `--require-clean`. Ne pas lancer d'assertion dépôt réel dans le worktree
  partagé avant les commits Tasks 6 et 7.
- [ ] Dans un tel clone, appliquer exactement le diff Task 3 et le committer
  localement, puis, CWD `<temp-clone-root>`, appliquer exactement :

  ```bash
  python -B scripts/build_manifest.py --refresh-empty
  git add audit/BUILD_MANIFEST.json
  git commit -m "[TEST] refresh temporary manifest"
  python scripts/inventory_collection.py
  git add ETAT_COLLECTION.md audit/AUDIT_CONSOLIDE.md audit/ECARTS_ET_CONTRADICTIONS.yaml audit/INVENTAIRE_COLLECTION.json audit/INVENTAIRE_COLLECTION.md audit/MATRICE_LIVRABLES.yaml
  git commit -m "[TEST] refresh temporary inventory"
  python -m pytest -q tests/test_inventory_collection.py::test_repository_pdf_artifact_registry_attribution
  ```

  Chaque commande Python, le test dépôt réel et chaque commit attend rc0 ; ces
  commits restent exclusivement dans le clone temporaire. Ce test rc0 est une
  précondition au commit Task 3 dans le worktree partagé.
- [ ] CWD `<repo-root>`, vérifications avant commit :

  ```bash
  python -m py_compile scripts/inventory_graph.py scripts/inventory_pdf.py scripts/inventory_collection.py
  git diff --check
  ```

  Les deux commandes attendent rc0. Vérifier aussi 36 PDF inchangés et
  `SOURCE_ROLES.yaml`/`BUILD_PRODUCERS.yaml` inchangés.
- [ ] Commit :

  ```bash
  git add audit/PDF_ARTIFACT_REGISTRY.yaml \
    audit/schemas/v1/pdf-artifact-registry.schema.json \
    audit/schemas/v1/inventory-collection.schema.json \
    scripts/inventory_graph.py scripts/inventory_pdf.py \
    scripts/inventory_collection.py \
    tests/test_inventory_collection.py
  git commit -m "[AUDIT] attribute historical and official PDF artifacts"
  ```

## Task 4 — Corriger uniquement les en-têtes P13

**Files:**

- Add: `tests/test_p13_pack_contracts.py`
- Modify: `NSI/corpus_nsi/latex/packs/premiere/P13/P13_aides.tex`
- Modify: `NSI/corpus_nsi/latex/packs/premiere/P13/P13_corrige.tex`
- Modify: `NSI/corpus_nsi/latex/packs/premiere/P13/P13_cours.tex`
- Modify: `NSI/corpus_nsi/latex/packs/premiere/P13/P13_evaluation.tex`
- Modify: `NSI/corpus_nsi/latex/packs/premiere/P13/P13_fiche_methode.tex`
- Modify: `NSI/corpus_nsi/latex/packs/premiere/P13/P13_td.tex`
- Modify: `NSI/corpus_nsi/latex/packs/premiere/P13/P13_td_eleve.tex`
- Modify: `NSI/corpus_nsi/latex/packs/premiere/P13/P13_tp.tex`
- Modify: `NSI/corpus_nsi/latex/packs/premiere/P13/P13_tp_eleve.tex`
- Modify: `NSI/corpus_nsi/latex/packs/premiere/P13/P13_trace.tex`

- [ ] RED : le test root exige `\\nsiheader{...}` et rejette `siheader{...}` sans antislash dans les dix sources. CWD `<repo-root>` :

  ```bash
  python -m pytest -q tests/test_p13_pack_contracts.py
  ```

  RED attendu : rc non nul.
- [ ] GREEN : ajouter seulement les dix antislashs, sans modifier préambule ou contenu pédagogique.
- [ ] CWD `<repo-root>`, compiler littéralement dans une racine temporaire et
  exiger dix PDF, sans toucher le worktree :

  ```bash
  set -euo pipefail
  nexus_p13_tmp="$(mktemp -d)"
  cleanup_nexus_p13_tmp() {
    if [ -n "${nexus_p13_tmp:-}" ] && [ -d "$nexus_p13_tmp" ]; then
      rm -rf -- "$nexus_p13_tmp"
    fi
  }
  trap cleanup_nexus_p13_tmp EXIT
  nexus_p13_status_before="$(git status --short -- NSI/corpus_nsi/latex/packs/premiere/P13)"
  nexus_p13_pdf_before="$(sha256sum NSI/corpus_nsi/latex/packs/premiere/P13/*.pdf)"
  mkdir -p "$nexus_p13_tmp/corpus_nsi/latex/packs/premiere" \
    "$nexus_p13_tmp/corpus_nsi/02_modeles_documents"
  cp -a NSI/corpus_nsi/latex/packs/premiere/P13 \
    "$nexus_p13_tmp/corpus_nsi/latex/packs/premiere/"
  cp -a NSI/corpus_nsi/02_modeles_documents/nsi-preamble.sty \
    "$nexus_p13_tmp/corpus_nsi/02_modeles_documents/"
  (cd "$nexus_p13_tmp/corpus_nsi/latex/packs/premiere/P13" && ./build.sh)
  test "$(find "$nexus_p13_tmp/corpus_nsi/latex/packs/premiere/P13" -maxdepth 1 -type f -name '*.pdf' | wc -l)" -eq 10
  test "$(git status --short -- NSI/corpus_nsi/latex/packs/premiere/P13)" = "$nexus_p13_status_before"
  test "$(sha256sum NSI/corpus_nsi/latex/packs/premiere/P13/*.pdf)" = "$nexus_p13_pdf_before"
  cleanup_nexus_p13_tmp
  trap - EXIT
  ```

  Le build et chaque assertion attendent rc0. Cette vérification ne
  reconstitue pas le graphe historique, ne vaut pas receipt pour les huit PDF
  suivis et garantit qu'aucune source/PDF suivi n'a changé pendant le build.
- [ ] CWD `<repo-root>`, rejouer `python -m pytest -q tests/test_p13_pack_contracts.py` (rc0), puis `git diff --check` (rc0). Les tests NSI globaux sont différés à Task 8.
- [ ] Commit LaTeX autonome :

  ```bash
  git add tests/test_p13_pack_contracts.py \
    NSI/corpus_nsi/latex/packs/premiere/P13/P13_aides.tex \
    NSI/corpus_nsi/latex/packs/premiere/P13/P13_corrige.tex \
    NSI/corpus_nsi/latex/packs/premiere/P13/P13_cours.tex \
    NSI/corpus_nsi/latex/packs/premiere/P13/P13_evaluation.tex \
    NSI/corpus_nsi/latex/packs/premiere/P13/P13_fiche_methode.tex \
    NSI/corpus_nsi/latex/packs/premiere/P13/P13_td.tex \
    NSI/corpus_nsi/latex/packs/premiere/P13/P13_td_eleve.tex \
    NSI/corpus_nsi/latex/packs/premiere/P13/P13_tp.tex \
    NSI/corpus_nsi/latex/packs/premiere/P13/P13_tp_eleve.tex \
    NSI/corpus_nsi/latex/packs/premiere/P13/P13_trace.tex
  git commit -m "[LATEX] restore P13 pack headers"
  ```

## Task 5 — Corriger le ledger sans anticiper l'inventaire

**Files:**

- Modify: `audit/UNATTRIBUTED_PDFS_LEDGER.md`

- [ ] Remplacer la fausse histoire de fixtures par les trois rôles, les audiences P13 et les preuves versionnées.
- [ ] Distinguer attribution technique et décision humaine de cycle de vie P13.
- [ ] Ne pas prétendre que l'inventaire généré vaut déjà zéro avant Task 7.
- [ ] Exécuter `git diff --check` puis commit :

  ```bash
  git add audit/UNATTRIBUTED_PDFS_LEDGER.md
  git commit -m "[AUDIT] correct unattributed PDF evidence ledger"
  ```

## Task 6 — Rafraîchir le manifest depuis un arbre propre

**Files:**

- Modify: `audit/BUILD_MANIFEST.json`

- [ ] Exiger un worktree propre au HEAD des cinq commits précédents.
- [ ] CWD `<repo-root>`, exécuter :

  ```bash
  python -B scripts/build_manifest.py --refresh-empty
  ```

  Résultat attendu : rc0.
- [ ] Vérifier que seul le manifest change, reste `empty`, et reflète les nouveaux contrôles, l'autorité réparée et P13.
- [ ] Exécuter `git diff --check` (rc0), puis :

  ```bash
  git add audit/BUILD_MANIFEST.json
  git commit -m "[AUDIT] refresh empty manifest after PDF attribution"
  ```

## Task 7 — Régénérer l'inventaire géré

**Files:**

- Modify: `ETAT_COLLECTION.md`
- Modify: `audit/AUDIT_CONSOLIDE.md`
- Modify: `audit/ECARTS_ET_CONTRADICTIONS.yaml`
- Modify: `audit/INVENTAIRE_COLLECTION.json`
- Modify: `audit/INVENTAIRE_COLLECTION.md`
- Modify: `audit/MATRICE_LIVRABLES.yaml`

- [ ] Depuis l'arbre propre, CWD `<repo-root>`, exécuter le générateur canonique :

  ```bash
  python scripts/inventory_collection.py
  ```

  Résultat attendu : rc0.
- [ ] Exiger seulement ces six deltas gérés.
- [ ] Exiger `unattributed_pdfs=0`, `RAW=2286`, statuts 2222, unassembled 52, orphans 12, autres catégories structurelles zéro.
- [ ] Exiger 22 fingerprints retirés, zéro ajouté, aucune qualification/baseline et 36 PDF inchangés.
- [ ] Vérifier registre, schéma et autorité dans `source_files`; mesurer et consigner `source_file_count >= 6285` sans le prédire plus précisément.
- [ ] Commit avec seulement les six fichiers :

  ```bash
  git add ETAT_COLLECTION.md audit/AUDIT_CONSOLIDE.md \
    audit/ECARTS_ET_CONTRADICTIONS.yaml \
    audit/INVENTAIRE_COLLECTION.json audit/INVENTAIRE_COLLECTION.md \
    audit/MATRICE_LIVRABLES.yaml
  git commit -m "[AUDIT] regenerate inventory after PDF attribution"
  ```

## Task 8 — Rejouer les gates et faire relire

**Files:** Aucun edit attendu.

Les assertions sur les 22 fichiers du dépôt réel commencent ici, après les
commits manifest et inventaire. Toutes les commandes ci-dessous sont
littérales.

- [ ] Clusters ciblés, CWD `<repo-root>`, rc0 chacun :

  ```bash
  python -m pytest -q tests/test_nsi_program_authority_bindings.py tests/test_p13_pack_contracts.py
  python -m pytest -q tests/test_inventory_collection.py -k 'pdf_artifact_registry or stable_tracked_control or pdf_artifact_dispatch or pdf_artifact_toctou or publication_snapshots_blocker'
  python -m pytest -q tests/test_inventory_collection.py::test_repository_pdf_artifact_registry_attribution
  python -m pytest -q tests/test_inventory_collection.py -k 'release or deliverable or qualification'
  ```

  Le test dépôt réel exige 22/22 attribués, les huit audiences P13 exactes,
  zéro `unattributed_pdfs`, un seul blocker snapshot et 36 PDF inchangés.
- [ ] Suites complètes, CWD `<repo-root>`. Chaque commande attend rc0 ; la
  troisième fixe littéralement le CWD NSI :

  ```bash
  python -m pytest -q tests/
  python -m pytest -q Mathematiques/manuel-maths/tests/
  (cd NSI && python -m pytest -q tests/)
  ```

- [ ] Gates, CWD `<repo-root>` :

  ```bash
  python scripts/inventory_collection.py --check --require-clean
  python scripts/inventory_collection.py --check --validate-model --require-clean
  python scripts/inventory_collection.py --check --fail-on-new --require-clean
  python scripts/inventory_collection.py --check --release-strict --require-clean
  ```

  Résultats attendus dans l'ordre : rc0, rc0, rc0, rc7. Release reste rouge
  et, si aucune autre dette ne varie, contient 67 raisons avec remplacement
  unique de l'ancienne raison unattributed par
  `COLLECTION:publication_snapshots:stale_undecided:12`.
- [ ] Recalculer seulement alors la liste et son digest ; ne pas figer un digest prédit.
- [ ] Vérifier aucune promotion de statut, baseline, qualification ou preuve de compilation, aucune auto-clôture des snapshots et aucune modification de `SOURCE_ROLES.yaml`/`BUILD_PRODUCERS.yaml`.
- [ ] Faire une revue spécification et une revue qualité. Toute divergence retourne au RED/GREEN concerné.
- [ ] Terminer propre, sans push, merge ni déclaration de publication.
