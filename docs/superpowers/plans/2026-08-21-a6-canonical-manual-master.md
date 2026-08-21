# A6 Canonical Manual Master Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve unique observed-build run evidence while making all Math and NSI canonical manual masters byte-independent from `run_id`.

**Architecture:** Both observed producers render a constant master hook that reads a compile-only `NEXUS_BUILD_RUN` environment value and writes it exclusively to the LuaTeX log. The common manifest validator proves the constant hook in the master, the concrete token in the log/preflight/receipt, and the canonical master in the FLS; no receipt shape or durable manifest schema changes.

**Tech Stack:** Python 3.12, pytest, LuaHBTeX/LuaLaTeX 1.17, JSON receipts, Git, SHA-256.

**Authority:** `docs/superpowers/specs/2026-08-21-a6-canonical-manual-master-design.md`.

---

## Chunk 1: Protocole de master indépendant du run

### Task 1: Cycles RED→GREEN Math, un comportement à la fois

**Files:**
- Modify: `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py`
- Modify: `tests/test_pdf_reproducibility.py`
- Modify: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`

Chaque Step ci-dessous est un micro-cycle complet : écrire un seul test,
l'exécuter seul et observer l'échec métier exact, écrire le minimum de code
dans le producteur Math, puis rejouer ce même nœud jusqu'au PASS avant le Step
suivant. Ne pas accumuler plusieurs tests rouges.

- [ ] **Step 1: Ajouter le RED du renderer et de l'orchestrateur**

Premier micro-cycle : créer
`test_run_independent_master_is_pure_for_all_math_targets` : le renderer
pur est appelé sans `run_id` pour les quatre manuels et les deux variantes ; il
doit produire le hook constant unique et aucun token concret ; observer le RED,
implémenter le hook/renderer minimal, puis PASS. Deuxième micro-cycle : créer
séparément
`test_observed_build_keeps_master_identical_for_distinct_run_ids` : deux
orchestrations, dont `secrets.token_hex` est contrôlé pour rendre deux IDs
distincts, doivent publier des masters byte-identiques ; observer le RED,
implémenter la séparation d'identité minimale, puis PASS. Après correction,
vérifier également par inspection de signature que le renderer n'accepte plus
`run_id` ; ne pas conserver un argument ignoré.

- [ ] **Step 2: Ajouter le RED orchestration/environnement**

Faire exécuter deux builds factices avec deux tokens générés distincts. Exiger
que le master canonique soit identique, que seuls les trois appels LuaLaTeX
reçoivent `NEXUS_BUILD_RUN`, que les autres subprocess ne le voient pas et
qu'une valeur hôte hostile soit écrasée.

- [ ] **Step 3: Ajouter le RED LuaHBTeX réel puis les caractérisations fermées**

Compiler deux fois le même master constant avec deux environnements de run.
Exiger : logs distincts et exacts, PDF byte-identiques, master byte-identique,
Le vrai RED est l'égalité du master/PDF sous deux runs distincts avec le token
encore sérialisé. Après son GREEN, ajouter les quatre caractérisations
paramétrées `absent`, `uppercase`, `short` et `long` ; elles doivent être
vertes immédiatement si le hook minimal est déjà correctement fermé, sinon
elles guident un GREEN additionnel. Chacune exige l'erreur exacte
`NEXUS_BUILD_RUN invalide`.
Comparer aussi l'ancien `\typeout` au nouveau hook et exiger le même PDF.

- [ ] **Step 4: Journaliser chaque RED puis chaque GREEN**

Exécuter d'abord chaque nouveau nœud explicitement, sans `-k`, et archiver pour
chacun le message d'assertion attendu. Les noms canoniques à créer sont :

```bash
python -m pytest -q Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_run_independent_master_is_pure_for_all_math_targets
python -m pytest -q Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_observed_build_keeps_master_identical_for_distinct_run_ids
python -m pytest -q Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_run_environment_is_compile_only_and_overwrites_hostile_host_value
python -m pytest -q Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_real_lualatex_distinct_runs_keep_master_and_pdf_identical
python -m pytest -q 'Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_real_lualatex_rejects_invalid_final_run_environment[absent]'
python -m pytest -q 'Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_real_lualatex_rejects_invalid_final_run_environment[uppercase]'
python -m pytest -q 'Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_real_lualatex_rejects_invalid_final_run_environment[short]'
python -m pytest -q 'Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_real_lualatex_rejects_invalid_final_run_environment[long]'
```

Chaque vrai RED doit échouer sur l'invariant métier visé, jamais sur collecte,
fixture ou import. Ne jamais affaiblir temporairement une validation pour
fabriquer un RED : toute mutation déjà rejetée est consignée comme
caractérisation verte. Le test historique
`test_pdf2_identity_is_independent_of_run_and_path` est renommé
`test_pdf2_identity_is_independent_of_path` et conserve une vraie racine
miroir ; la dépendance au run est désormais couverte par l'orchestrateur et
l'environnement compile-only, jamais par une boucle sur un argument ignoré.

### Task 2: Cycles RED→GREEN NSI, un comportement à la fois

**Files:**
- Modify: `NSI/tests/test_assemble_manuel.py`
- Modify: `NSI/scripts/assemble_manuel.py`

Comme Task 1, chaque nouveau nœud NSI suit RED isolé → échec exact → minimum
de code NSI → GREEN isolé avant le nœud suivant.

- [ ] **Step 1: Ajouter le RED NSI**

Premier micro-cycle : créer
`test_run_independent_master_is_pure_for_all_nsi_targets` sur le renderer pur
sans `run_id` pour 1NSI/TNSI, élève/professeur ; observer le RED, implémenter le
hook/renderer minimal, puis PASS. Deuxième micro-cycle : créer séparément
`test_observed_build_keeps_nsi_master_identical_for_distinct_run_ids` sur deux
orchestrations aux tokens contrôlés. Exiger masters identiques, hook constant,
aucun token concret et signature sans `run_id`. Tester enfin les vrais modes
`--record-observed` pour 1NSI et TNSI, avec l'environnement de run transmis
uniquement aux passes LuaLaTeX.

- [ ] **Step 2: Vérifier chaque RED puis chaque GREEN NSI**

Exécuter chaque RED isolément et vérifier le message exact :

```bash
(cd NSI && python -m pytest -q tests/test_assemble_manuel.py::test_run_independent_master_is_pure_for_all_nsi_targets)
(cd NSI && python -m pytest -q tests/test_assemble_manuel.py::test_observed_build_keeps_nsi_master_identical_for_distinct_run_ids)
(cd NSI && python -m pytest -q tests/test_assemble_manuel.py::test_observed_run_environment_is_compile_only)
```

Chaque RED doit atteindre le protocole visé. Le vrai mode
`--record-observed` est ajouté comme dernier cycle NSI après le GREEN du helper
sous le nœud paramétré `test_record_observed_real_run_protocol` :

```bash
(cd NSI && python -m pytest -q 'tests/test_assemble_manuel.py::test_record_observed_real_run_protocol[1NSI-eleve]')
(cd NSI && python -m pytest -q 'tests/test_assemble_manuel.py::test_record_observed_real_run_protocol[1NSI-professeur]')
(cd NSI && python -m pytest -q 'tests/test_assemble_manuel.py::test_record_observed_real_run_protocol[TNSI-eleve]')
(cd NSI && python -m pytest -q 'tests/test_assemble_manuel.py::test_record_observed_real_run_protocol[TNSI-professeur]')
```

Chaque cas exerce le vrai chemin observed avec runner/toolchain réel ou sa
capabilité d'intégration existante, puis le validator commun ; aucun simple
appel au renderer ne satisfait ce contrat.

### Task 3: Cycle RED→GREEN du validator commun

**Files:**
- Modify: `tests/test_build_manifest.py`
- Modify: `scripts/build_manifest.py`

- [ ] **Step 1: RED acceptation du nouveau protocole**

Adapter une fixture de receipt avec hook constant, log concret et FLS ouvrant
le master. Ajouter
`test_receipt_accepts_constant_master_run_hook_and_concrete_log_token`, le
faire échouer seul sur l'ancien validator, implémenter le minimum d'acceptation
dans `build_manifest.py`, puis exiger PASS.

- [ ] **Step 2: RED→GREEN rejets du hook**

Créer `test_receipt_rejects_master_run_hook_protocol_mutations`, paramétré
`missing`, `duplicate`, `altered`, `foreign-concrete`. Recalculer les digests.
Ces cas sont des caractérisations vertes si le validator courant les rejette
déjà ; ne jamais le desserrer pour les rendre rouges. Seule l'acceptation du
hook exact constitue le RED de Step 1.

- [ ] **Step 3: RED→GREEN ancien protocole et preuves liées**

Créer le vrai RED
`test_receipt_rejects_legacy_concrete_master_marker_with_recomputed_digests`,
puis ajouter les paramètres log `missing`, `duplicate`, `foreign` et preflight
`mismatch` comme caractérisations vertes lorsqu'ils sont déjà rejetés. Exécuter
chaque nœud isolément. Ne changer aucun shape de receipt/preflight/manifest.

- [ ] **Step 4: Commandes isolées du validator**

```bash
python -m pytest -q tests/test_build_manifest.py::test_receipt_accepts_constant_master_run_hook_and_concrete_log_token
python -m pytest -q tests/test_build_manifest.py::test_receipt_rejects_master_run_hook_protocol_mutations
python -m pytest -q tests/test_build_manifest.py::test_receipt_rejects_legacy_concrete_master_marker_with_recomputed_digests
```

### Task 4: Refactor minimal et régressions croisées

**Files:**
- Modify: les sept fichiers de code/tests des Tasks 1–3 uniquement si le
  refactor supprime une duplication née pendant les micro-cycles.

- [ ] **Step 1: Vérifier le protocole final commun**

Les deux producteurs contiennent la même ligne fermée, lisent uniquement un
run ID `[0-9a-f]{32}` dans une copie d'environnement et le validator exige le
hook exact. Si une constante/helper Python locale évite une duplication au
sein d'un producteur, l'extraire maintenant sans créer de source TeX runtime.

- [ ] **Step 2: Conserver les autres preuves et rejeter l'historique**

Ne changer ni `_RECEIPT_FIELDS`, ni `_EVIDENCE_FIELDS`, ni le schéma du build
manifest. Continuer à exiger le digest du master et sa présence parmi les
`INPUT` du FLS.

- [ ] **Step 3: Vérifier GREEN ciblé**

Run intégral des quatre surfaces après le GREEN ciblé :

```bash
python -m pytest -q \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  NSI/tests/test_assemble_manuel.py \
  tests/test_build_manifest.py \
  tests/test_pdf_reproducibility.py
```

Expected: PASS. Capturer le résumé de warnings et le comparer au snapshot
précédent ; ne pas les masquer.

### Task 5: Documenter, vérifier et faire relire

**Files:**
- Modify: `audit/PDF_TRAILER_ID_PREIMAGE_CONTRACT.md`

- [ ] **Step 1: Mettre à jour le contrat courant**

Documenter le base environment fermé, l'exception compile-only, l'absence du
token concret dans le master et la chaîne de preuve hook/master/FLS/log.
Ne pas réécrire l'attestation A4 historique.

- [ ] **Step 2: Rejouer les suites d'autorité**

```bash
python -m pytest -q tests/test_pdf_reproducibility.py
python -m pytest -q tests/test_build_manifest.py
python -m pytest -q Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py
(cd NSI && python -m pytest -q tests/test_assemble_manuel.py)
python -m py_compile \
  Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  NSI/scripts/assemble_manuel.py \
  scripts/build_manifest.py
git diff --check
```

- [ ] **Step 3: Revue specification puis qualité**

Faire relire le diff par deux agents distincts. Toute finding P0/P1/P2 doit
être corrigée et relue avant commit.

- [ ] **Step 4: Commit atomique source**

```bash
git add -- \
  Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  NSI/scripts/assemble_manuel.py \
  NSI/tests/test_assemble_manuel.py \
  scripts/build_manifest.py \
  tests/test_build_manifest.py \
  tests/test_pdf_reproducibility.py \
  audit/PDF_TRAILER_ID_PREIMAGE_CONTRACT.md
git commit -m "[PDF] make canonical manual masters run-independent"
```

Le présent plan est committé séparément avant toute implémentation et ne doit
donc pas faire partie de ce commit source.

## Chunk 2: Scellement A6 après migration du protocole

### Task 6: Preuve réelle avant régénération

**Files:** aucun edit source.

- [ ] **Step 1: Créer deux vrais clones sans hardlinks au commit source**

Utiliser exactement :

```bash
SOURCE_REPO="$(git rev-parse --show-toplevel)"
A_PARENT="$(mktemp -d /tmp/nexus-a6-master-proof-a.XXXXXX)"
B_PARENT="$(mktemp -d /tmp/nexus-a6-master-proof-b.XXXXXX)"
git clone --no-hardlinks --branch audit/adversarial-reconciliation-2026 "$SOURCE_REPO" "$A_PARENT/repo"
git clone --no-hardlinks --branch audit/adversarial-reconciliation-2026 "$SOURCE_REPO" "$B_PARENT/repo"
```

Exiger dans chaque clone le SHA candidat exact,
branche attachée, absence d'alternate, zéro inode Git partagé avec la source,
porcelain vide et `git diff --check` rc0.

- [ ] **Step 2: Compiler et enregistrer TCOMPL élève/professeur**

Dans chaque clone, sous l'environnement A4 exact, exécuter deux fois :

```bash
python Mathematiques/manuel-maths/scripts/assemble_manuel.py --manual TCOMPL --variant eleve --record-observed
python Mathematiques/manuel-maths/scripts/assemble_manuel.py --manual TCOMPL --variant professeur --record-observed
```

Copier les preuves de chaque run avant le suivant. Exiger deux IDs distincts,
chacun exactement une fois dans log/préflight/receipt, absent du master ;
exiger le master dans les `INPUT` FLS et faire accepter chaque receipt par le
validator commun. Le deuxième run ne doit pas réutiliser le premier ID.

- [ ] **Step 3: Compiler et enregistrer les smokes 1NSI élève/professeur**

Depuis le CWD du clone :

```bash
python NSI/scripts/assemble_manuel.py --book 1NSI --variant eleve --record-observed
python NSI/scripts/assemble_manuel.py --book 1NSI --variant professeur --record-observed
```

Appliquer les mêmes assertions run/log/préflight/receipt/master/FLS. Les
manifests et inventaires observés rendent volontairement ces clones de preuve
sales ; ils restent confinés aux clones jetables, ne sont jamais copiés dans
le worktree source et ne servent pas au scellement Fresh final.

- [ ] **Step 4: Comparer A == B**

Comparer byte à byte, pour chaque cible : master, PDF, page count, texte,
trailer ID, graphe de sources canonique, classe et charte. Comparer aussi les
résultats du validator ; seuls les run IDs/logs/preflights/receipts peuvent
différer, avec les liens internes exacts prouvés.

- [ ] **Step 5: Exiger les quatre SHA PDF canoniques de la spécification**
- [ ] **Step 6: Exiger zéro staging/backup/writer/lock actif, HEAD inchangé et aucun diff source hors sorties observées attendues**
- [ ] **Step 7: STOP au premier écart**

### Task 7: Rafraîchir les artefacts gérés par commits dédiés

**Files:**
- Modify: `audit/BUILD_MANIFEST.json` si stale
- Modify: les six sorties gérées d'inventaire si stale

- [ ] **Step 1: Depuis un arbre clean, exécuter `python -B scripts/build_manifest.py --refresh-empty`**
- [ ] **Step 2: Prouver `builds=[]` et delta manifest uniquement**
- [ ] **Step 3: Commit atomique du manifest**
- [ ] **Step 4: Après commit du manifest et arbre clean, exécuter `python scripts/inventory_collection.py`**
- [ ] **Step 5: Prouver le set delta : aucun fingerprint ajouté/reclassifié**
- [ ] **Step 6: Exiger exactement les six sorties gérées (`ETAT_COLLECTION.md`,
  `audit/AUDIT_CONSOLIDE.md`, `audit/ECARTS_ET_CONTRADICTIONS.yaml`,
  `audit/INVENTAIRE_COLLECTION.json`, `audit/INVENTAIRE_COLLECTION.md`,
  `audit/MATRICE_LIVRABLES.yaml`) puis commit atomique**

### Task 8: Rejouer les validations globales

**Files:** aucun edit.

- [ ] **Step 1: Suites globales sans exclusion, avec leurs CWD contractuels**

```bash
python -m pytest -q tests/
python -m pytest -q Mathematiques/manuel-maths/tests/
(cd NSI && python -m pytest -q tests/)
```

Exiger rc0, failed/skipped/xfail/xpass tous à zéro ; archiver les résumés
exacts et les warnings de dépendances sans les masquer.

- [ ] **Step 2: Gates ciblés A6, PRE-A6, A5**

```bash
python -m pytest -q tests/test_inventory_collection.py -k 'a6_context'
python -m pytest -q tests/test_inventory_collection.py -k 'pre_a6 or validate_model'
python -m pytest -q tests/test_inventory_collection.py -k 'canonical_object_type_ontology'
```

- [ ] **Step 3: Régressions A1–A4 : exactement 28 nœuds**

Utiliser littéralement la même liste pour `--collect-only` puis pour le run :

```bash
python -m pytest -q \
  tests/test_inventory_collection.py::test_a1_broken_latex_references_resolved \
  tests/test_inventory_collection.py::test_static_latex_cycle_is_reported_and_deep_chain_is_iterative \
  tests/test_inventory_collection.py::test_latex_cycle_detection_mutation_2_and_3_nodes \
  tests/test_inventory_collection.py::test_recursive_static_latex_assembly_counts_duplicates_and_assembles_correction \
  tests/test_inventory_collection.py::test_declared_assembly_reuse_is_not_flagged_as_duplicate \
  tests/test_inventory_collection.py::test_declared_reuse_occurrence_mismatch_is_flagged \
  tests/test_inventory_collection.py::test_reuse_expected_count_follows_manifest_changes \
  tests/test_inventory_collection.py::test_reuse_annotation_for_absent_manifest_id_fails \
  tests/test_inventory_collection.py::test_reuse_registry_rejects_invalid_entries \
  tests/test_inventory_collection.py::test_repository_duplicate_assembly_objects_is_zero \
  tests/test_inventory_collection.py::test_maquette_reuse_contracts_match_manifest_authority \
  tests/test_inventory_collection.py::test_capacity_resolver_accepts_chapter_scoped_ids \
  tests/test_inventory_collection.py::test_capacity_resolver_rejects_foreign_and_absent_references \
  tests/test_inventory_collection.py::test_capacity_resolver_normalization_is_injective \
  tests/test_inventory_collection.py::test_legacy_meth_suffix_derives_method_alias \
  tests/test_inventory_collection.py::test_legacy_meth_alias_stays_strict \
  tests/test_inventory_collection.py::test_prerequisite_codes_resolve_without_origin \
  tests/test_inventory_collection.py::test_repository_prerequisite_references_are_declared \
  tests/test_inventory_collection.py::test_expected_review_debt_policy_gates_exactly \
  tests/test_inventory_collection.py::test_a4_review_debt_valid_record_has_no_violation \
  tests/test_inventory_collection.py::test_a4_review_debt_policy_edit_invalidates_derived_qualifications \
  tests/test_inventory_collection.py::test_a4_review_debt_method_edit_makes_qualification_stale \
  tests/test_inventory_collection.py::test_a4_review_debt_missing_packet_invalidates_qualification \
  tests/test_inventory_collection.py::test_a4_review_debt_status_promotion_without_review_fails \
  tests/test_inventory_collection.py::test_repository_a4_derived_qualifications_reference_class_policy \
  tests/test_inventory_collection.py::test_repository_fail_on_new_accepts_only_declared_review_debt \
  tests/test_inventory_collection.py::test_repository_method_aliases_are_unambiguous \
  tests/test_inventory_collection.py::test_trigonometrie_contract_covers_bo_referentiel
```

Vérifier exactement 28 nœuds collectés ; ne pas remplacer ce gate par un
filtre `-k` approximatif.

- [ ] **Step 4: Gates inventory exacts**

```bash
python scripts/inventory_collection.py --check --require-clean
python scripts/inventory_collection.py --validate-model
python scripts/inventory_collection.py --fail-on-new
python scripts/inventory_collection.py --release-strict
```

Attendus A6 : rc0, rc0, rc0, puis rc7 avec la même liste de raisons que le
snapshot courant de ce lot. Calculer le digest des raisons par JSON compact
canonique trié et prouver `added=[]`, `removed=[]` tant que le correctif
COLLECTION suivant n'a pas commencé.

- [ ] **Step 5: Scanner les 89 bindings/packets**

Exiger 89 sources, 89 packets, tous deux `needs_review`, SHA source et packet
liés, stale/missing/mismatch zéro, digest de binding documenté.

- [ ] **Step 6: Vérifier l'inventaire et l'hygiène finale**

Recalculer RAW/BLOCKING/NONBLOCKING, toutes les catégories, P0,
NEW_UNQUALIFIED, EXPECTED_REVIEW_DEBT, digests source/model/fingerprints et
object count. Vérifier les 36 PDF suivis pathwise, `git diff --check`, staged
et unstaged vides, writers=0, staging/backup=0, locks actifs=0.

### Task 9: Fresh A / Fresh B définitifs et attestation

**Files:**
- Modify: `audit/A6_FINAL_ATTESTATION.json`
- Modify: `audit/A6_FINAL_ATTESTATION.md`

- [ ] **Step 1: Créer deux nouveaux clones de zéro depuis `SOURCE_REPO="$(git rev-parse --show-toplevel)"` vers deux destinations `mktemp`, avec exactement les commandes de Task 6 ; vérifier SHA exact, absence d'alternate/hardlink, branche attachée et clean**
- [ ] **Step 2: Rejouer Task 8 puis les mêmes builds de Task 6 sans `--record-observed` dans A puis B, sans réutiliser aucun ancien clone/cache de build**
- [ ] **Step 3: Après tous les gates propres et builds locaux, exécuter aussi les quatre builds observés TCOMPL/1NSI de Task 6 dans A et B ; ces dernières commandes peuvent salir seulement les sorties observées, mais doivent exercer hook, environnement compile-only et validator commun au SHA final**
- [ ] **Step 4: Exiger A == B pour les résumés et rc de chaque suite/gate, la liste/digest release, les 89 bindings, tous les compteurs d'inventaire, les digests source/model/fingerprints, masters/PDF/pages/texte/trailers/graphes/classes/chartes ; pour les builds observés, exiger des run IDs distincts mais des liens log/préflight/receipt valides dans les deux clones**
- [ ] **Step 5: Mettre à jour l'attestation avec les preuves observées seulement**
- [ ] **Step 6: Revue indépendante de l'attestation et commit**
- [ ] **Step 7: Déclarer A6 PASS uniquement si A == B et aucun nouveau P0**

Le correctif `release-strict` COLLECTION constitue le lot atomique suivant ;
il ne doit pas être mélangé à ce commit PDF.

## Commit préalable du plan

Avant Task 1, faire relire ce document, corriger tout P0/P1/P2, puis :

```bash
git add -- docs/superpowers/plans/2026-08-21-a6-canonical-manual-master.md
git commit -m "[DOCS] plan run-independent canonical masters"
```

Le SHA de ce commit est l'autorité de départ de l'implémentation TDD.
