# Wave 0 Collection Infrastructure Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Terminer Wave 0 sans perte : rétablir une gouvernance verte, intégrer le référentiel 1SPE 2026 sans régression visuelle, généraliser la traçabilité aux six manuels, réconcilier TNSI, recalculer les audits et produire des builds vérifiés.

**Architecture:** La branche `integration/1spe-bo2026-traceability` reste isolée de `main` pendant toute l'exécution. Les apports de `feature/1spe-bat-2026` sont portés par responsabilité et adaptés aux statuts honnêtes du pipeline actuel ; aucune baseline visuelle ancienne n'est importée. Les matrices et dashboards sont générés depuis les contrats, référentiels, manifests et builds observés.

**Tech Stack:** Python 3.12, pytest, jsonschema Draft 2020-12, PyYAML, LaTeX/LuaLaTeX, Poppler, Git, JSON/YAML, scripts d'audit Nexus.

**Spécification approuvée :** `docs/superpowers/specs/2026-08-12-finalisation-premium-six-manuels-design.md`

**État de départ observé :**

- SHA parent : `a21ff532750cebd156b4a77666f434c40ae9ee20` ;
- conception : `a92a3701` ;
- gouvernance : `15 failed, 973 passed` le 12 août 2026 ;
- causes dominantes : manifeste de build périmé, analyse statique de l'assembleur NSI devenue incompatible avec la sélection multi-manuel et impossibilité pour LuaLaTeX d'écrire ses caches par défaut dans le sandbox ; les échecs de baseline/inventaire sont à requalifier après ces causes amont ;
- collection : 0/51 chapitre READY, 2472/2782 objets `generated` ;
- les 312 capacités sont rattachées, mais la preuve complète `covered_by/assessed_by/remediated_by` n'existe pas encore pour les six manuels.

---

## Cartographie des fichiers

### Fichiers communs à modifier

- `scripts/inventory_collection.py` : inventaire canonique, baseline, assemblages déclarés et gates.
- `scripts/inventory_assembly.py` : analyse AST des assembleurs et sélection déclarative.
- `scripts/build_manifest.py` : manifests observés et traces de compilation.
- `scripts/chapter_readiness.py` : calcul honnête de `READY` par chapitre.
- `scripts/collection_dashboard.py` : agrégation des six manuels.
- `SOURCE_DE_VERITE.md` : état dérivé et cohérent avec l'inventaire courant.
- `audit/BUILD_MANIFEST.json` : enveloppe de build alignée sur le SHA courant.
- `audit/BUILD_PRODUCERS.yaml` : producteurs 1NSI/TNSI et variantes observables.

### Fichiers programme et traçabilité à créer

- `schemas/programme-traceability.schema.json` : contrat commun d'une ligne de matrice.
- `schemas/qcm-source.schema.json` : schéma QCM commun minimal.
- `scripts/programme_traceability.py` : génération et validation des six matrices.
- `scripts/check_programme_registry.py` : contrôle du registre et des sources officielles.
- `tests/test_programmes_2026_2027.py` : invariants temporels et réglementaires.
- `tests/test_programme_traceability.py` : invariant des six matrices.
- `tests/test_contract_status_governance.py` : interdiction des auto-validations.
- `tests/test_qcm_source_governance.py` : source JSON unique et séparation des objets.
- `docs/programmes/matrices/1SPE.json`.
- `docs/programmes/matrices/TSPE_2026_2027.json`.
- `docs/programmes/matrices/TCOMPL.json`.
- `docs/programmes/matrices/TEXPERTES.json`.
- `docs/programmes/matrices/1NSI.json`.
- `docs/programmes/matrices/TNSI.json`.

### Apports 1SPE 2026 à porter puis adapter

- `Mathematiques/manuel-maths/referentiel/programme_1SPE_2026.json`.
- `Mathematiques/manuel-maths/schemas/programme_1spe_2026.schema.json`.
- `Mathematiques/manuel-maths/schemas/programme_1spe_2026.attestation.schema.json`.
- `Mathematiques/manuel-maths/schemas/contrat_chapitre_1spe_2026.schema.json`.
- `Mathematiques/manuel-maths/scripts/check_programme_1spe_2026.py`.
- `Mathematiques/manuel-maths/scripts/extract_official_source.py`.
- `Mathematiques/manuel-maths/tests/test_programme_1spe_2026.py`.
- `Mathematiques/manuel-maths/tests/test_official_source_extraction.py`.
- `Mathematiques/manuel-maths/tests/test_contrat_schema_1spe_2026.py`.
- les dix `contrat.yaml` 1SPE, enrichis sans écraser les corrections de `main`.

### Fichiers explicitement exclus du portage

- `Mathematiques/manuel-maths/scripts/check_maquette_v5.py` depuis la branche historique ;
- `Mathematiques/manuel-maths/tests/test_maquette_v5.py` depuis la branche historique ;
- `Mathematiques/manuel-maths/validations/charte.visual.json` depuis la branche historique ;
- `Mathematiques/manuel-maths/validations/v5/` ;
- `Mathematiques/manuel-maths/validations/v5-it1/` ;
- `Mathematiques/manuel-maths/validations/v5-it2/` ;
- `Mathematiques/manuel-maths/validations/release-1spe/` (la seule revue
  historique retenue est archivée sous `audit/historique/`) ;
- toute ancienne baseline PNG ou configuration visuelle V5.B-it2.

---

## Task 0: Sceller la spécification et le présent plan

**Files:**
- Modify: `docs/superpowers/specs/2026-08-12-finalisation-premium-six-manuels-design.md`
- Create: `docs/superpowers/plans/2026-08-12-wave-0-collection-infrastructure.md`

- [ ] **Step 1: Obtenir l'approbation explicite du plan**

La spécification est couverte par les décisions `HUM-2026-08-11-*` et
`HUM-2026-08-12-FINAL-APPROVER`. Le présent plan détaillé doit être approuvé
avant tout code de Wave 0. Cette approbation autorise l'exécution TDD du plan,
mais ne vaut ni revue scientifique, ni revue programme, ni approbation de
release.

- [ ] **Step 2: Vérifier et committer exactement les deux documents**

```bash
git diff --check
git status --short
git add docs/superpowers/specs/2026-08-12-finalisation-premium-six-manuels-design.md \
  docs/superpowers/plans/2026-08-12-wave-0-collection-infrastructure.md
git diff --cached --check
git diff --cached --name-only
git commit -m "[DOCS] verrouille le plan d implementation Wave 0"
test -z "$(git status --porcelain)"
```

Expected: la liste indexée contient exactement ces deux chemins, puis l'arbre
est propre. Tout autre WIP arrête l'exécution; aucun stash, restore ou nettoyage
automatique.

### Invariant Git de chaque commit du plan

Avant chaque `git add` ou commit, exécuter obligatoirement `git diff --check`
et `git status --short`, inspecter la liste exacte des fichiers, puis exécuter
`git diff --cached --check` après staging. Les blocs ci-dessous répètent ces
contrôles pour rendre le protocole exécutable. Un fichier conditionnel de
baseline, politique, disposition ou inventaire n'est jamais ajouté par glob :
il figure explicitement dans la liste de staging du cas concerné.

## Chunk 1: Rétablir une gouvernance verte avant intégration

### Task 1: Autoriser le rattachement borné d'un manifeste strictement vide

**Files:**
- Modify: `scripts/inventory_collection.py`
- Modify: `scripts/build_manifest.py`
- Test: `tests/test_build_manifest.py`

- [ ] **Step 1: Écrire le test rouge de changement de branche vide**

Ajouter
`test_refresh_empty_manifest_rebinds_empty_ancestor_manifest_to_current_branch`.
La fixture possède `builds: []`, un `head_sha` ancêtre et une branche source
différente. Le test exige le rattachement à la branche courante. Cas négatifs :
build non vide, SHA non ancêtre, HEAD détaché, capability absente ou arbre sale.
Ajouter `test_record_from_receipt_refuses_empty_manifest_from_other_branch` :
le chemin `--receipt` doit rester strict et refuser le changement de branche.

Run:

```bash
python3 -m pytest \
  tests/test_build_manifest.py::test_refresh_empty_manifest_rebinds_empty_ancestor_manifest_to_current_branch \
  -q -p no:cacheprovider
```

Expected: FAIL sur la divergence `finalisation/collection-v1` versus
`integration/1spe-bo2026-traceability`.

- [ ] **Step 2: Implémenter la capability minimale**

Créer une capability distincte `_EMPTY_MANIFEST_BRANCH_REBIND_CAPABILITY` dans
`inventory_collection.py`. `build_manifest.py` ne la transmet que depuis
`_derive_empty_refresh_envelope()` appelé par `--refresh-empty`. La capability
existante `_EMPTY_MANIFEST_REFRESH_CAPABILITY`, également utilisée par
`record_from_receipt()`, conserve la branche stricte. Dans
`_load_observed_build_manifest`, autoriser la divergence seulement avec la
nouvelle capability de rebind et si
`builds == []`, `build_state_digest` est celui du tableau vide, le SHA enregistré
est un ancêtre strict du HEAD, la branche courante est nommée et l'arbre est
propre hors manifeste. Les chemins ordinaires de lecture et les manifests non
vides restent stricts.

- [ ] **Step 3: Vérifier l'unité et les refus**

```bash
python3 -m pytest tests/test_build_manifest.py \
  -k 'refresh_empty_manifest or record_from_receipt_refuses_empty_manifest_from_other_branch' \
  -q -p no:cacheprovider
```

Expected: PASS, sans affaiblissement de la lecture normale.

- [ ] **Step 4: Commit atomique du mécanisme, sans rafraîchir encore**

```bash
git diff --check
git status --short
git add scripts/inventory_collection.py scripts/build_manifest.py \
  tests/test_build_manifest.py
git diff --cached --check
git commit -m "[TESTS] borne le rattachement d un manifeste vide"
```

### Task 2: Réconcilier l'assembleur NSI multi-manuel avec l'inventaire

**Files:**
- Modify: `NSI/scripts/assemble_manuel.py`
- Modify: `scripts/inventory_assembly.py`
- Modify: `scripts/inventory_collection.py`
- Modify: `audit/BUILD_PRODUCERS.yaml`
- Test: `tests/test_inventory_collection.py`
- Test: `NSI/tests/test_assemble_manuel.py`

- [ ] **Step 1: Remplacer les assertions obsolètes avant le code**

Réécrire `test_live_1nsi_manual_declaration_closes_assembly_debt_without_tnsi`
en `test_live_nsi_manual_declaration_covers_1nsi_and_tnsi`. Le test doit exiger
sept assemblages 1NSI, sept assemblages TNSI, les chapitres de chaque manifest
et zéro dette `chapters_not_in_manual`/`unassembled_objects` pour les deux
niveaux. Mettre à jour
`test_supported_manuals_distinguish_nsi_chapter_and_manual_assemblers` pour
attendre `("1NSI", "TNSI")` sur `NSI/scripts/assemble_manuel.py`.

Remplacer le test devenu contraire à la décision
`test_nsi_manual_assembler_cannot_cover_tnsi_chapters` par
`test_manifest_backed_nsi_assembler_declares_two_manuals`, avec une fixture
d'assembleur minimal qui déclare :

```python
BOOK_MANIFESTS = {
    "1NSI": "manifests/books/1NSI.json",
    "TNSI": "manifests/books/TNSI.json",
}
BOOK_ID = "1NSI"
CHAPITRES = []
```

La fixture crée et suit les deux JSON. Le test exige deux assemblages manuels,
lit les chapitres dans chaque manifest et refuse chemins absolus, `..`, fichier
non suivi, `book_id` incohérent, ID dupliqué et divergence entre ordre statique
et ordre runtime. Ajouter des tests nommés distincts pour chacun de ces refus,
avec le préfixe commun `test_manifest_backed_nsi_assembler_rejects_`, afin
qu'une régression n'en masque pas une autre.

- [ ] **Step 2: Vérifier l'échec**

Run:

```bash
python3 -m pytest \
  tests/test_inventory_collection.py::test_live_1nsi_runtime_selection_matches_declared_manual_assemblies \
  tests/test_inventory_collection.py::test_live_nsi_manual_declaration_covers_1nsi_and_tnsi \
  tests/test_inventory_collection.py::test_manifest_backed_nsi_assembler_declares_two_manuals \
  tests/test_inventory_collection.py::test_supported_manuals_distinguish_nsi_chapter_and_manual_assemblers \
  tests/test_inventory_collection.py::test_declared_assembler_allowlist_preserves_real_and_planned_engines \
  -q -p no:cacheprovider
```

Expected: FAIL parce que l'analyse statique ne connaît pas encore
`BOOK_MANIFESTS` et ne déclare pas TNSI.

```bash
python3 -m pytest tests/test_inventory_collection.py \
  -k 'manifest_backed_nsi_assembler' -q -p no:cacheprovider
```

Expected: les cas négatifs nouvellement ajoutés échouent avant l'implémentation.

- [ ] **Step 3: Déclarer les manifests dans l'assembleur**

Ajouter une constante statique auditée :

```python
BOOK_MANIFESTS = {
    "1NSI": "manifests/books/1NSI.json",
    "TNSI": "manifests/books/TNSI.json",
}
LIVRES_CONNUS = tuple(BOOK_MANIFESTS)
```

`select_book()` continue de charger les chapitres depuis le manifest et ne
recopie jamais leur liste dans Python. Ajouter à
`NSI/tests/test_assemble_manuel.py` un test runtime qui sélectionne 1NSI puis
TNSI et compare exactement `CHAPITRES` aux deux JSON.

- [ ] **Step 4: Étendre l'analyse AST sans affaiblir les contrôles**

Dans `scripts/inventory_assembly.py`, ajouter `BOOK_MANIFESTS` à
`_AUDITED_SELECTION_CONSTANTS`. `validate_analysis()` accepte soit un
`CHAPITRES` littéral non vide, soit un `BOOK_MANIFESTS` littéral fermé non vide.
Résoudre et vérifier les JSON dans `add_declared_assemblies()`, qui possède
`root` et `tracked`, puis faire produire les assemblages par
`_build_manual_assemblies()`. Pour chaque paire `manual_id -> chemin`, résoudre
depuis `NSI/`, vérifier confinement, suivi Git, régularité et JSON, puis lire
`chapters[*].id`; ne jamais traiter un chemin comme une liste de chapitres.
`scripts/inventory_collection.py` autorise cet assembleur pour
`("1NSI", "TNSI")`.

- [ ] **Step 5: Enregistrer TNSI comme producteur**

Ajouter dans `audit/BUILD_PRODUCERS.yaml` un producteur `nsi-tnsi-manual`
utilisant le même assembleur et couvrant au minimum :

```yaml
assembly_ids:
  - nsi:manual:TNSI:eleve
  - nsi:manual:TNSI:professeur
```

Inclure aussi les variantes TNSI réellement exposées par `VARIANTS`. Après
édition, recalculer `control_digest` avec l'algorithme canonique, sans copier une
empreinte calculée sur un autre contenu :

```bash
python3 - <<'PY'
from pathlib import Path
import yaml
from scripts.inventory_collection import _control_digest
p = Path("audit/BUILD_PRODUCERS.yaml")
data = yaml.safe_load(p.read_text(encoding="utf-8"))
print(_control_digest(data))
PY
```

Reporter exactement la valeur imprimée dans `control_digest`, puis vérifier
qu'un second calcul produit la même valeur.

- [ ] **Step 6: Rejouer les tests ciblés**

Run:

```bash
python3 -m pytest \
  NSI/tests/test_assemble_manuel.py \
  tests/test_inventory_collection.py::test_live_1nsi_runtime_selection_matches_declared_manual_assemblies \
  tests/test_inventory_collection.py::test_live_nsi_manual_declaration_covers_1nsi_and_tnsi \
  tests/test_inventory_collection.py::test_manifest_backed_nsi_assembler_declares_two_manuals \
  tests/test_inventory_collection.py::test_supported_manuals_distinguish_nsi_chapter_and_manual_assemblers \
  tests/test_inventory_collection.py::test_declared_assembler_allowlist_preserves_real_and_planned_engines \
  -q -p no:cacheprovider
python3 -m pytest tests/test_inventory_collection.py \
  -k 'manifest_backed_nsi_assembler' -q -p no:cacheprovider
```

Expected: PASS, avec 1NSI et TNSI présents. Les artefacts dérivés sont
régénérés en Task 4 avant le gate repository.

- [ ] **Step 7: Commit atomique**

```bash
git diff --check
git status --short
git add NSI/scripts/assemble_manuel.py scripts/inventory_assembly.py \
  scripts/inventory_collection.py audit/BUILD_PRODUCERS.yaml \
  tests/test_inventory_collection.py NSI/tests/test_assemble_manuel.py
git diff --cached --check
git commit -m "[NSI] reconcilie l assembleur TNSI avec l inventaire"
```

### Task 3: Isoler l'environnement TeX du test de trace longue

**Files:**
- Test: `tests/test_build_manifest.py`

- [ ] **Step 1: Reproduire le défaut isolé**

Run:

```bash
python3 -m pytest \
  tests/test_build_manifest.py::test_ordered_object_trace_accepts_real_lualatex_log_for_long_paths \
  -vv -p no:cacheprovider
```

Expected: FAIL au lancement LuaLaTeX faute de cache TeX inscriptible; ne pas
attribuer cet échec au parseur tant que l'exécution isolée n'a pas réussi.

- [ ] **Step 2: Confirmer la cause environnementale**

Run:

```bash
TEXMFVAR=/tmp/nexus-wave0-texmf-var \
TEXMFCONFIG=/tmp/nexus-wave0-texmf-config \
XDG_CACHE_HOME=/tmp/nexus-wave0-xdg-cache \
python3 -m pytest \
  tests/test_build_manifest.py::test_ordered_object_trace_accepts_real_lualatex_log_for_long_paths \
  -vv -p no:cacheprovider
```

Expected: PASS. Cette preuve interdit une modification spéculative du parseur.

- [ ] **Step 3: Donner au subprocess ses caches temporaires**

Dans le test, construire `env = os.environ.copy()`, puis définir `TEXMFVAR`,
`TEXMFCONFIG` et `XDG_CACHE_HOME` sous `tmp_path` avant `subprocess.run(...,
env=env)`. Conserver inchangées les assertions de présence, ordre et
confinement.

- [ ] **Step 4: Vérifier**

Run:

```bash
python3 -m pytest \
  tests/test_build_manifest.py::test_ordered_object_trace_accepts_real_lualatex_log_for_long_paths \
  -q -p no:cacheprovider
```

Expected: PASS dans l'environnement sandbox par défaut.

- [ ] **Step 5: Commit atomique**

```bash
git diff --check
git status --short
git add tests/test_build_manifest.py
git diff --cached --check
git commit -m "[TESTS] isole les caches TeX du test de trace longue"
```

### Task 4: Rejouer la gouvernance avant portage

**Files:**
- Modify: `audit/BUILD_MANIFEST.json`
- Modify generated: `audit/INVENTAIRE_COLLECTION.json`
- Modify generated: `audit/INVENTAIRE_COLLECTION.md`
- Modify generated: `ETAT_COLLECTION.md`
- Modify generated: `audit/AUDIT_CONSOLIDE.md`
- Modify generated: `audit/ECARTS_ET_CONTRADICTIONS.yaml`
- Modify generated: `audit/MATRICE_LIVRABLES.yaml`

- [ ] **Step 1: Réaligner l'enveloppe vide après les commits d'assembleur**

```bash
jq '.builds | length' audit/BUILD_MANIFEST.json
python3 scripts/build_manifest.py --refresh-empty
git diff --check
git status --short
git add audit/BUILD_MANIFEST.json
git diff --cached --check
git commit -m "[AUDIT] realigne le manifeste apres l infrastructure NSI"
```

Expected: `0`, puis seul le manifeste est modifié avant commit.
`--refresh-empty` reste interdit si `builds` n'est plus vide.

- [ ] **Step 2: Régénérer et auditer les six artefacts gérés**

```bash
python3 scripts/inventory_collection.py
git diff --check
git status --short
git add audit/INVENTAIRE_COLLECTION.json audit/INVENTAIRE_COLLECTION.md \
  ETAT_COLLECTION.md audit/AUDIT_CONSOLIDE.md \
  audit/ECARTS_ET_CONTRADICTIONS.yaml audit/MATRICE_LIVRABLES.yaml
git diff --cached --check
git commit -m "[AUDIT] regenere l inventaire apres l assembleur TNSI"
```

Inspecter la dérive avant commit. Toute modification de fingerprints de
baseline est seulement rapportée; aucune baseline n'est changée ici.

- [ ] **Step 3: Rejouer le gate et tous les tests de gouvernance**

Run:

```bash
python3 scripts/inventory_collection.py --check --validate-model
python3 -m pytest tests/ -q -p no:cacheprovider
```

Expected: `0 failed`; consigner le total collecté observé, qui sera supérieur
ou égal aux 988 tests initiaux à cause des nouveaux tests AST.

- [ ] **Step 4: Arrêt de checkpoint en cas de reliquat**

Si le résultat n'est pas exactement vert, arrêter le portage, consigner les
tests rouges et appliquer `superpowers:systematic-debugging`. Chaque nouvelle
cause impose un test rouge dédié, un correctif minimal et un commit séparé.
Interdictions : baseline modifiée pour masquer le défaut, `skip`, `xfail`,
assertion supprimée ou plan poursuivi avec un gate commun rouge.

---

## Chunk 2: Porter le programme 1SPE 2026 sans ancienne baseline

### Task 5: Verrouiller le registre officiel des six programmes et épreuves

**Files:**
- Modify: `docs/programmes/PROGRAMMES_2026_2027.yaml`
- Create: `scripts/check_programme_registry.py`
- Create: `tests/test_programmes_2026_2027.py`
- Create: `Mathematiques/manuel-maths/sources/html/BO2025_EA_MATHS_2027.html`
- Create: `Mathematiques/manuel-maths/sources/html/BO2019_TSPE_SPECIALITE.html`
- Create: `Mathematiques/manuel-maths/sources/html/BO2020_TSPE_EPREUVE.html`
- Create: `Mathematiques/manuel-maths/sources/html/BO2021_TSPE_STRUCTURE.html`
- Create: `Mathematiques/manuel-maths/sources/html/BO2025_CONTROLE_CONTINU.html`
- Create: `NSI/sources/html/BO2025_TNSI_EPREUVE_2026.html`
- Create: `docs/programmes/sources/html/BO2023_PERIMETRE_EPREUVES_SPECIALITES.html`
- Modify: `Mathematiques/manuel-maths/docs/10_perimetre_terminale.md`
- Modify: `Mathematiques/manuel-maths/sources/SOURCES.md`
- Modify: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
- Modify: `ROADMAP_TERMINALE.md`

- [ ] **Step 1: Écrire les tests rouges du registre**

```python
def test_registry_has_exactly_the_six_manuals(registry):
    assert {m["manual_id"] for m in registry["manuels"]} == {
        "1SPE", "TSPE_2026_2027", "TCOMPL", "TEXPERTES", "1NSI", "TNSI"
    }


def test_terminal_2027_programme_is_never_current(registry):
    current = {m["programme_source"] for m in registry["manuels"]}
    assert "SRC-BO2026-TSPE-R2027" not in current


def test_every_exam_reference_has_a_hashed_official_source(registry, root):
    for manual in registry["manuels"]:
        exam = manual.get("exam_reference")
        if exam:
            assert registry["epreuves"][exam]["source_deposee"] is True
```

Ajouter des assertions sur `fichier`, `url`, `sha256`, `date_application`, le
confinement au dépôt, l'absence de symlink et les modalités TNSI exactes
(`3.5`, trois exercices indépendants, `1` heure pratique). Ajouter un test de
concordance `intitule`/`arrete`/NOR dans l'URL/titre du document. Pour TSPE, le
NOR obligatoire est `MENE1921246A`; `MENE1921262A` (Terminale STMG) doit être
explicitement refusé même si le fichier associé possède un SHA-256 valide.
Pour TSPE, exiger la chaîne réglementaire complète et ordonnée : définition
`MENE2001796N`, structure à quatre exercices `MENE2121273N`, puis périmètre
actuel `MENE2323020N` applicable depuis la session 2024. Ce dernier porte sur
le programme de Terminale en vigueur et peut mobiliser les notions de Première.
Tester explicitement que `MENE2227884N`, abrogée par `MENE2323020N`, ne peut
pas être la référence courante. Pour TNSI, la définition et le périmètre
courants proviennent directement de `MENE2516123N`, plus récent et spécifique,
avec écrit 3 h 30, trois exercices indépendants et pratique 1 h à compter de la
session 2026; ne pas lui attribuer artificiellement la note TSPE commune de
2023. Une épreuve n'est complète que si sa définition matérielle, sa structure
et son périmètre examinable applicables sont archivés.

Ajouter les tests de cohérence temporelle de l'épreuve anticipée :
`premiere_session: 2027` décrit la première session d'application générale,
mais la cohorte scolarisée en Première en 2026-2027 passe l'épreuve en juin
2027 par anticipation au titre de `session_baccalaureat_cohorte: 2028`.
Interdire toute confusion entre ces deux champs.

- [ ] **Step 2: Vérifier l'échec**

Run:

```bash
python3 -m pytest tests/test_programmes_2026_2027.py -q -p no:cacheprovider
```

Expected: FAIL pour les modalités encore marquées `source_deposee: false`, le
périmètre examinable absent et le NOR TSPE erroné.

- [ ] **Step 3: Déposer les sept sources officielles exactes**

```bash
mkdir -p Mathematiques/manuel-maths/sources/html NSI/sources/html \
  docs/programmes/sources/html
curl -L --fail --silent --show-error \
  https://www.education.gouv.fr/bo/2025/Hebdo24/MENE2515469N \
  --output Mathematiques/manuel-maths/sources/html/BO2025_EA_MATHS_2027.html
curl -L --fail --silent --show-error \
  https://www.education.gouv.fr/bo/19/Special8/MENE1921246A.htm \
  --output Mathematiques/manuel-maths/sources/html/BO2019_TSPE_SPECIALITE.html
curl -L --fail --silent --show-error \
  https://www.education.gouv.fr/bo/20/Special2/MENE2001796N.htm \
  --output Mathematiques/manuel-maths/sources/html/BO2020_TSPE_EPREUVE.html
curl -L --fail --silent --show-error \
  https://www.education.gouv.fr/bo/21/Hebdo30/MENE2121273N.htm \
  --output Mathematiques/manuel-maths/sources/html/BO2021_TSPE_STRUCTURE.html
curl -L --fail --silent --show-error \
  https://www.education.gouv.fr/bo/2025/Hebdo32/MENE2523744N \
  --output Mathematiques/manuel-maths/sources/html/BO2025_CONTROLE_CONTINU.html
curl -L --fail --silent --show-error \
  https://www.education.gouv.fr/bo/2025/Hebdo31/MENE2516123N \
  --output NSI/sources/html/BO2025_TNSI_EPREUVE_2026.html
curl -L --fail --silent --show-error \
  https://www.education.gouv.fr/bo/2023/Hebdo36/MENE2323020N \
  --output docs/programmes/sources/html/BO2023_PERIMETRE_EPREUVES_SPECIALITES.html
sha256sum \
  Mathematiques/manuel-maths/sources/html/BO2025_EA_MATHS_2027.html \
  Mathematiques/manuel-maths/sources/html/BO2019_TSPE_SPECIALITE.html \
  Mathematiques/manuel-maths/sources/html/BO2020_TSPE_EPREUVE.html \
  Mathematiques/manuel-maths/sources/html/BO2021_TSPE_STRUCTURE.html \
  Mathematiques/manuel-maths/sources/html/BO2025_CONTROLE_CONTINU.html \
  NSI/sources/html/BO2025_TNSI_EPREUVE_2026.html \
  docs/programmes/sources/html/BO2023_PERIMETRE_EPREUVES_SPECIALITES.html
```

Reporter les sept empreintes calculées, URL et chemins dans le registre; six de
ces documents constituent les références d'épreuve, le septième étant la
source du programme TSPE.
Corriger `SRC-BO2019-TSPE.arrete` en `MENE1921246A` et ajouter l'URL officielle
`https://www.education.gouv.fr/bo/19/Special8/MENE1921246A.htm`. Vérifier NOR et
intitulé dans la page HTML réglementaire, puis titre et hash seulement dans
l'annexe TXT/PDF, avec un lien explicite page réglementaire → annexe.
Ajouter les URLs actives manquantes : TCOMPL
`https://www.education.gouv.fr/bo/19/Special8/MENE1921265A.htm`, TEXPERTES
`https://www.education.gouv.fr/bo/19/Special8/MENE1921264A.htm`, 1NSI
`https://www.education.gouv.fr/bo/19/Special1/MENE1901633A.htm` et TNSI
`https://www.education.gouv.fr/bo/19/Special8/MENE1921247A.htm`.
Dans `SRC-BO2026-1SPE`, distinguer
`source_originale: {fichier, sha256}` pour le PDF existant et
`extraction: {fichier, sha256, outil}` pour le TXT existant.
Ajouter aussi l'URL officielle du programme Terminale futur
`https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602919A`, uniquement dans
`SRC-BO2026-TSPE-R2027` avec son interdiction actuelle. Un téléchargement vide,
une redirection hors domaine officiel ou un document sans sa référence BO est
un arrêt, pas une source acceptée.

- [ ] **Step 4: Implémenter le checker**

Le checker vérifie existence, fichier régulier non symlink, confinement,
SHA-256, domaine officiel, unicité des six manuels, dates d'application et
interdiction du programme Terminale 2027-2028 dans l'édition courante. Il
imprime exactement `PROGRAMME_REGISTRY=PASS manuals=6 sources=<N>
exam_sources=6` et sort `0`; toute divergence sort non-zéro. Il vérifie aussi
la chaîne TSPE ordonnée `MENE2001796N` → `MENE2121273N` → `MENE2323020N`, le
périmètre TNSI `MENE2516123N`, et la distinction première session/cohorte.

Corriger dans le même lot les NOR et liens inexacts encore présents dans
`10_perimetre_terminale.md`, `SOURCES.md`, `assemble_manuel.py` et
`ROADMAP_TERMINALE.md`; le test recherche les anciens NOR erronés dans tout le
dépôt suivi et échoue s'ils sont encore présentés comme références courantes.

- [ ] **Step 5: Vérifier et committer**

Run:

```bash
python3 scripts/check_programme_registry.py
python3 -m pytest tests/test_programmes_2026_2027.py -q -p no:cacheprovider
```

Expected: message `PROGRAMME_REGISTRY=PASS ...`, puis tests PASS.

```bash
git diff --check
git status --short
git add docs/programmes/PROGRAMMES_2026_2027.yaml scripts/check_programme_registry.py \
  tests/test_programmes_2026_2027.py \
  Mathematiques/manuel-maths/docs/10_perimetre_terminale.md \
  Mathematiques/manuel-maths/sources/SOURCES.md \
  Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  ROADMAP_TERMINALE.md \
  Mathematiques/manuel-maths/sources/html/BO2025_EA_MATHS_2027.html \
  Mathematiques/manuel-maths/sources/html/BO2019_TSPE_SPECIALITE.html \
  Mathematiques/manuel-maths/sources/html/BO2020_TSPE_EPREUVE.html \
  Mathematiques/manuel-maths/sources/html/BO2021_TSPE_STRUCTURE.html \
  Mathematiques/manuel-maths/sources/html/BO2025_CONTROLE_CONTINU.html \
  NSI/sources/html/BO2025_TNSI_EPREUVE_2026.html \
  docs/programmes/sources/html/BO2023_PERIMETRE_EPREUVES_SPECIALITES.html
git diff --cached --check
git commit -m "[PROGRAMME] scelle les sources officielles de l edition 2026-2027"
```

### Task 6: Porter le référentiel canonique 1SPE et ses gates

**Files:**
- Create from revision `0d6ebd79`:
  `Mathematiques/manuel-maths/referentiel/programme_1SPE_2026.json`
- Create from revision `0d6ebd79`, then adapt:
  `Mathematiques/manuel-maths/schemas/programme_1spe_2026.schema.json`
- Create from revision `0d6ebd79`, then adapt:
  `Mathematiques/manuel-maths/schemas/programme_1spe_2026.attestation.schema.json`
- Create from revision `0d6ebd79`, then adapt:
  `Mathematiques/manuel-maths/scripts/extract_official_source.py`
- Create: `Mathematiques/manuel-maths/scripts/programme_1spe_model.py`
- Create: `Mathematiques/manuel-maths/scripts/programme_1spe_citations.py`
- Create: `Mathematiques/manuel-maths/scripts/check_programme_1spe_2026.py`
- Create: `audit/historique/1spe-bo2026-agent-review-2026-07-27.md`
- Create: `audit/historique/1spe-bo2026-agent-review-2026-07-27.metadata.yaml`
- Create from revision `0d6ebd79`, then adapt:
  `Mathematiques/manuel-maths/tests/test_programme_1spe_2026.py`
- Create from revision `0d6ebd79`, then adapt:
  `Mathematiques/manuel-maths/tests/test_official_source_extraction.py`

- [ ] **Step 1: Extraire uniquement les tests historiques nommés**

Utiliser `git show 0d6ebd79:<chemin>` pour inspecter chacun des deux tests, puis
réécrire seulement les assertions applicables avec `apply_patch`. Ne pas faire
de `cherry-pick`, merge, checkout de répertoire ou extraction globale. Les
tests adaptés exigent : 175 items officiels, 181 enregistrements contrôlés, six
couvertures d'objectifs, cardinalités par thème, citations, hashes PDF/TXT et
`review_status=review_required`. Ils ne dépendent plus de l'ancienne
attestation, de `sources/registry.yaml`, de `CONFORMITE_BO2026.md`, de l'ancien
plan ou de l'ancien rapport de release. Ajouter :

```python
def test_agent_review_cannot_certify_current_release(checker_result):
    assert checker_result["machine_status"] == "programme_consistent"
    assert checker_result["review_status"] == "review_required"
    assert checker_result["release_certified"] is False
```

- [ ] **Step 2: Vérifier le rouge**

Run:

```bash
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_programme_1spe_2026.py \
  Mathematiques/manuel-maths/tests/test_official_source_extraction.py \
  -q -p no:cacheprovider
```

Expected: FAIL car les fichiers canoniques ne sont pas encore présents.

- [ ] **Step 3: Porter les données et décomposer le gate**

Extraire exactement les trois fichiers JSON de données/schéma listés dans
`Files` depuis `0d6ebd79`. Porter les fonctions nécessaires de l'ancien checker
dans deux modules ciblés : modèle/schéma dans `programme_1spe_model.py`, ancres
et citations officielles dans `programme_1spe_citations.py`. Le nouveau
`check_programme_1spe_2026.py` reste un orchestrateur court; il ne reprend pas
aveuglément le checker historique d'environ 4 000 lignes et ne porte ni
toolchain sans appel prouvé ni logique visuelle. Sa sortie sépare :

```json
{
  "machine_status": "programme_consistent",
  "review_status": "review_required",
  "release_certified": false
}
```

Le checker ne doit jamais retourner `certified` sur la seule base d'un rapport
d'agent. Les hashes historiques restent des preuves d'intégrité, pas une
validation humaine actuelle.

Adapter explicitement `source.registry_id` du JSON historique de
`SRC-BO2026-1SPE-MATHS` vers `SRC-BO2026-1SPE`. L'extracteur lit
`docs/programmes/PROGRAMMES_2026_2027.yaml`, enregistre séparément chemins et
hashes de la source officielle et de l'extraction TXT, et le test exige
l'égalité entre l'identifiant du référentiel et celui du registre.
Adapter les deux schémas au même ID. Le schéma d'attestation pointe vers
`docs/programmes/PROGRAMMES_2026_2027.yaml`, supprime toute dépendance à
`sources/registry.yaml`, à l'ancienne conformité et à la revue de release, et
exige tant que la validation humaine manque : `review_status: review_required`
et `release_certified: false`. Ajouter les tests de régression correspondants.

- [ ] **Step 4: Archiver la revue historique octet pour octet**

Extraire uniquement
`0d6ebd79:Mathematiques/manuel-maths/validations/release-1spe/revue-programme.md`
dans `audit/historique/` sans aucune altération. Créer le fichier adjacent
`.metadata.yaml` avec commit source, SHA-256 du Markdown,
`evidence_role: advisory_historical` et
`current_review_status: review_required`.

- [ ] **Step 5: Rejouer les tests et le checker**

```bash
python3 Mathematiques/manuel-maths/scripts/check_programme_1spe_2026.py --json
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_programme_1spe_2026.py \
  Mathematiques/manuel-maths/tests/test_official_source_extraction.py \
  -q -p no:cacheprovider
```

Expected: JSON avec `machine_status=programme_consistent`,
`review_status=review_required`, `release_certified=false`, puis tests PASS.

- [ ] **Step 6: Commit atomique**

```bash
git diff --check
git status --short
git add Mathematiques/manuel-maths/referentiel/programme_1SPE_2026.json \
  Mathematiques/manuel-maths/schemas/programme_1spe_2026.schema.json \
  Mathematiques/manuel-maths/schemas/programme_1spe_2026.attestation.schema.json \
  Mathematiques/manuel-maths/scripts/extract_official_source.py \
  Mathematiques/manuel-maths/scripts/programme_1spe_model.py \
  Mathematiques/manuel-maths/scripts/programme_1spe_citations.py \
  Mathematiques/manuel-maths/scripts/check_programme_1spe_2026.py \
  Mathematiques/manuel-maths/tests/test_programme_1spe_2026.py \
  Mathematiques/manuel-maths/tests/test_official_source_extraction.py \
  audit/historique/1spe-bo2026-agent-review-2026-07-27.md \
  audit/historique/1spe-bo2026-agent-review-2026-07-27.metadata.yaml
git diff --cached --check
git commit -m "[PROGRAMME] porte le referentiel 1SPE 2026 sans auto-validation"
```

### Task 7: Migrer les dix contrats 1SPE vers le schéma enrichi

**Files:**
- Create from revision `0d6ebd79`, then adapt:
  `Mathematiques/manuel-maths/schemas/contrat_chapitre_1spe_2026.schema.json`
- Modify: `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/contrat.yaml`
- Modify: `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/contrat.yaml`
- Modify: `Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/contrat.yaml`
- Modify: `Mathematiques/manuel-maths/chapitres/1SPE-GEOMETRIE-REPEREE/contrat.yaml`
- Modify: `Mathematiques/manuel-maths/chapitres/1SPE-PROBA-COND/contrat.yaml`
- Modify: `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/contrat.yaml`
- Modify: `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/contrat.yaml`
- Modify: `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/contrat.yaml`
- Modify: `Mathematiques/manuel-maths/chapitres/1SPE-TRIGONOMETRIE/contrat.yaml`
- Modify: `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/contrat.yaml`
- Create from revision `0d6ebd79`, then adapt:
  `Mathematiques/manuel-maths/tests/test_contrat_schema_1spe_2026.py`
- Create: `Mathematiques/manuel-maths/tests/test_contrats_1spe_2026.py`
- Create: `audit/integration/1spe-bo2026-portage.json`

- [ ] **Step 1: Écrire les tests rouges**

Chaque capacité doit exiger `ref_capacite`, `obligation_class`,
`proof_object_ids` et `transversal_ids`. Le schéma doit accepter les statuts
normalisés et refuser `valide` sans registre humain.

Ajouter une assertion de programme : aucun ID de capacité trigonométrique retiré
en 2026 ne peut être `mandatory_content`.

- [ ] **Step 2: Vérifier l'échec**

Run:

```bash
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_contrat_schema_1spe_2026.py \
  Mathematiques/manuel-maths/tests/test_contrats_1spe_2026.py \
  -q -p no:cacheprovider
```

- [ ] **Step 3: Migrer contrat par contrat**

La version `a21ff532` de chacun des dix contrats reste la base. Pour chaque
capacité dont le `code` correspond dans `0d6ebd79`, injecter uniquement
`ref_capacite`, `obligation_class`, `proof_object_ids` et `transversal_ids`.
Ne jamais écraser titre, prérequis, progression, objets, enrichissements ou
corrections de `main`. Les dix chemins explicitement énumérés dans `Files` sont
comparés par le test à `MANUAL_CHAPTERS["1SPE"]` extrait statiquement de
`Mathematiques/manuel-maths/scripts/assemble_manuel.py`, afin qu'aucun contrat
ne soit omis ou ajouté silencieusement.

Chaque `proof_object_id` importé doit résoudre exactement un objet actuel,
appartenir au même chapitre et déclarer la capacité locale concernée. Rejeter
les IDs absents, ambigus ou liés à une capacité devenue hors programme; le
contrat reste `SCIENTIFIC_REVIEW_REQUIRED` jusqu'à une revue scientifique
humaine actuelle. Le passage à `PROGRAM_REVIEW_REQUIRED` n'est autorisé
qu'après une approbation scientifique humaine valide, liée au SHA Git, au
digest exact du contrat et à ses preuves. Une revue d'agent, un commentaire ou
une mention historique ne satisfait jamais cette transition.

Utiliser :

```yaml
statut: SCIENTIFIC_REVIEW_REQUIRED
```

jusqu'à preuve de revue actuelle.

Ajouter dans `test_contrats_1spe_2026.py` un test de régression qui refuse
`PROGRAM_REVIEW_REQUIRED` en l'absence d'une entrée d'approbation scientifique
humaine courante, et qui prouve qu'un commentaire `validé`, une revue d'agent
ou un SHA/digest périmé ne permettent pas de sauter l'étape scientifique.

- [ ] **Step 4: Vérifier les dix contrats et les prérequis**

Run:

```bash
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_contrat_schema_1spe_2026.py \
  Mathematiques/manuel-maths/tests/test_contrats_1spe_2026.py \
  Mathematiques/manuel-maths/tests/test_prerequis_conformite.py \
  -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 5: Prouver l'absence de régression visuelle importée**

Run:

```bash
git diff --exit-code a21ff532 -- \
  Mathematiques/manuel-maths/scripts/check_maquette_v5.py \
  Mathematiques/manuel-maths/tests/test_maquette_v5.py \
  Mathematiques/manuel-maths/validations/charte.visual.json \
  Mathematiques/manuel-maths/validations/v5 \
  Mathematiques/manuel-maths/validations/v5-it1 \
  Mathematiques/manuel-maths/validations/v5-it2 \
  Mathematiques/manuel-maths/validations/release-1spe
git diff --exit-code a21ff532 -- \
  'Mathematiques/manuel-maths/validations/**/*.png'
```

Expected: aucune différence de code/baseline et aucun PNG historique ajouté.

Générer `audit/integration/1spe-bo2026-portage.json` avec revision source,
fichiers retenus, fichiers explicitement exclus, SHA parent, décisions humaines
et résultats des tests. Ce manifeste, pas une heuristique de diff, fait foi sur
l'état du portage pour `SOURCE_DE_VERITE.md`.

- [ ] **Step 6: Commit atomique**

```bash
git diff --check
git status --short
git add Mathematiques/manuel-maths/schemas/contrat_chapitre_1spe_2026.schema.json \
  Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/1SPE-GEOMETRIE-REPEREE/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/1SPE-PROBA-COND/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/1SPE-SUITES/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/1SPE-TRIGONOMETRIE/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/contrat.yaml \
  Mathematiques/manuel-maths/tests/test_contrat_schema_1spe_2026.py \
  Mathematiques/manuel-maths/tests/test_contrats_1spe_2026.py \
  audit/integration/1spe-bo2026-portage.json
git diff --cached --check
git commit -m "[PROGRAMME] migre les contrats 1SPE vers la tracabilite BO 2026"
```

---

## Chunk 3: Généraliser traçabilité, statuts et readiness

### Task 8: Générer les six matrices de conformité

**Files:**
- Create: `schemas/programme-traceability.schema.json`
- Create: `schemas/human-approval.schema.json`
- Create: `schemas/chapter-review.schema.json`
- Create: `schemas/finding.schema.json`
- Create: `audit/HUMAN_APPROVALS.yaml`
- Create: `audit/FINDINGS_CANONICAL.json`
- Create: `scripts/programme_traceability.py`
- Create: `tests/test_programme_traceability.py`
- Create: six JSON files under `docs/programmes/matrices/`
- Modify: the thirteen `NSI/referentiel/capacites_*.json` files containing an
  external absolute source path.
- Modify: `NSI/referentiel/capacites_1NSI_TYPES-CONSTRUITS.json`.

- [ ] **Step 1: Écrire le schéma et les tests rouges**

Une ligne exige exactement :

```json
{
  "official_source_id": "SRC-...",
  "official_quote_ref": "path-or-anchor",
  "programme_version": "2019-or-2026",
  "manual_id": "1SPE",
  "chapter_id": "1SPE-SUITES",
  "capability_id": "ANA-SUIT-CAP-001",
  "contract_capability_code": "C1",
  "ref_capacite": "ANA-SUIT-CAP-001",
  "mandatory_or_enrichment": "mandatory",
  "covered_by": [],
  "assessed_by": [],
  "remediated_by": [],
  "proof_object_ids": [],
  "review_status": "review_required"
}
```

Le test exige les six matrices, zéro capacité officielle sans chapitre et
interdit `approved` sans entrée dans un registre humain.

Le registre humain distingue `scope_decision`, `chapter_review` et
`manual_release`. Enregistrer les cinq décisions de cadrage identifiées dans la
spécification (`HUM-2026-08-11-WAVES`, `...-VISUAL-MAIN`,
`...-1SPE-INTEGRATION`, `...-ENRICHMENTS`, `...-BASELINE-WAVE0`) et
`HUM-2026-08-12-FINAL-APPROVER`. Une `scope_decision` ne satisfait jamais un
champ `scientific_review`, `programme_review` ou `manual_release`.

`human-approval.schema.json` référence `chapter-review.schema.json`. Toute
revue exige `approval_id`, `approval_type`, `review_dimension`, `manual_id`,
`chapter_id`, `approver_kind: human`, `approver_name`, `decided_at`,
`reviewed_git_sha`, `reviewed_source_digest`, `decision` et `evidence_paths`.
Refuser preuve absente, approbateur modèle/agent et SHA/digest périmé.
`HUM-2026-08-12-FINAL-APPROVER` reste une `scope_decision`, jamais une release.

`schemas/finding.schema.json` et `audit/FINDINGS_CANONICAL.json` agrègent les
registres existants avec `id`, `chapter_id`, `severity`, `status`,
`source_digest` et preuves. `programme_traceability.py --write/--check` génère
et vérifie aussi ce registre, conserve l'empreinte de chaque registre source et
normalise explicitement les statuts. Source absente, digest divergent ou statut
inconnu donne `P0_STATUS=UNKNOWN`; les tests couvrent ces trois cas et ce statut
ne vaut jamais zéro P0.

- [ ] **Step 2: Vérifier le rouge**

Run:

```bash
python3 -m pytest tests/test_programme_traceability.py -q -p no:cacheprovider
```

- [ ] **Step 3: Implémenter le générateur**

Le dénominateur 1SPE vient exclusivement de
`referentiel/programme_1SPE_2026.json`; les anciens `capacites_1SPE_*.json` ne
sont qu'une correspondance locale. Pour les cinq autres manuels, le générateur
lit les référentiels officiels canoniques, contrats, registre des programmes,
registre humain et métadonnées. Le test exige l'égalité exacte entre ensemble
canonique officiel et les seules lignes `official_capabilities`. Les
`enrichments` vivent dans une section séparée, portent
`excluded_from_mandatory_assessments: true` et n'entrent jamais dans
`OFFICIAL_CAPABILITIES_WITHOUT_MAPPING`. Les anciennes capacités
trigonométriques retirées ne peuvent être que `enrichment`. Un tableau de
preuve vide reste vide et bloque la release.

Dans les treize
fichiers suivants, remplacer la source absolue par
`NSI/corpus_nsi/00_programmes_officiels/programme_nsi_2019.yaml` et une ancre
interne stable, sans changer les capacités :

- `NSI/referentiel/capacites_1NSI_ALGORITHMIQUE.json`
- `NSI/referentiel/capacites_1NSI_ARCHITECTURES-MATERIELLES-ET.json`
- `NSI/referentiel/capacites_1NSI_HISTOIRE-DE-L-INFORMATIQUE.json`
- `NSI/referentiel/capacites_1NSI_INTERACTIONS-ENTRE-L-HOMME-E.json`
- `NSI/referentiel/capacites_1NSI_LANGAGES-ET-PROGRAMMATION.json`
- `NSI/referentiel/capacites_1NSI_REPRESENTATION-DES-DONNEES-T.json`
- `NSI/referentiel/capacites_1NSI_TRAITEMENT-DE-DONNEES-EN-TAB.json`
- `NSI/referentiel/capacites_TNSI_ALGORITHMIQUE.json`
- `NSI/referentiel/capacites_TNSI_ARCHITECTURES-MATERIELLES-SY.json`
- `NSI/referentiel/capacites_TNSI_BASES-DE-DONNEES.json`
- `NSI/referentiel/capacites_TNSI_HISTOIRE-DE-L-INFORMATIQUE.json`
- `NSI/referentiel/capacites_TNSI_LANGAGES-ET-PROGRAMMATION.json`
- `NSI/referentiel/capacites_TNSI_STRUCTURES-DE-DONNEES.json`

Pour `P-BASE-01` à `P-BASE-05`, ajouter les correspondances atomiques :
`P-BASE-01 → [P-DATA-BASE-01]`,
`P-BASE-02 → [P-DATA-BASE-02A, P-DATA-BASE-02B]`,
`P-BASE-03 → [P-DATA-BASE-03]`,
`P-BASE-04 → [P-DATA-BASE-04]`,
`P-BASE-05 → [P-DATA-BASE-05A, P-DATA-BASE-05B]`. Chaque capacité NSI porte
`official_capability_ids` et `official_quote_refs`; zéro chemin absolu et
chaque référence résout exactement une entrée canonique.

Dans `capacites_1NSI_TYPES-CONSTRUITS.json`, mapper
`C1 → [P-DATA-CONSTR-01]`,
`C2 → [P-DATA-CONSTR-02A, P-DATA-CONSTR-02B]`,
`C3 → [P-DATA-CONSTR-02C, P-DATA-CONSTR-02D]`,
`C4 → [P-DATA-CONSTR-03A, P-DATA-CONSTR-03B, P-DATA-CONSTR-03C]`.
`C5` porte `official_capability_ids: []`, `official_quote_refs: []`,
`mandatory_or_enrichment: enrichment`,
`excluded_from_mandatory_assessments: true` et
`review_status: review_required`, sans rattachement officiel inventé.
Le test parcourt tous les référentiels NSI, pas seulement les fichiers ayant eu
un chemin absolu. Il exige des références non vides uniquement pour les
capacités officielles; tout enrichissement reste hors du dénominateur.

- [ ] **Step 4: Générer puis contrôler l'idempotence**

Run:

```bash
python3 scripts/programme_traceability.py --write
python3 scripts/programme_traceability.py --check
python3 -m pytest tests/test_programme_traceability.py -q -p no:cacheprovider
```

Expected: `OFFICIAL_CAPABILITIES_WITHOUT_MAPPING=0`, matrices identiques au
second passage, preuves manquantes conservées comme bloqueurs.

- [ ] **Step 5: Commit atomique**

```bash
git diff --check
git status --short
git add schemas/programme-traceability.schema.json schemas/human-approval.schema.json \
  schemas/chapter-review.schema.json schemas/finding.schema.json \
  audit/HUMAN_APPROVALS.yaml audit/FINDINGS_CANONICAL.json \
  scripts/programme_traceability.py \
  tests/test_programme_traceability.py \
  docs/programmes/matrices/1SPE.json \
  docs/programmes/matrices/TSPE_2026_2027.json \
  docs/programmes/matrices/TCOMPL.json \
  docs/programmes/matrices/TEXPERTES.json \
  docs/programmes/matrices/1NSI.json \
  docs/programmes/matrices/TNSI.json \
  NSI/referentiel/capacites_1NSI_ALGORITHMIQUE.json \
  NSI/referentiel/capacites_1NSI_ARCHITECTURES-MATERIELLES-ET.json \
  NSI/referentiel/capacites_1NSI_HISTOIRE-DE-L-INFORMATIQUE.json \
  NSI/referentiel/capacites_1NSI_INTERACTIONS-ENTRE-L-HOMME-E.json \
  NSI/referentiel/capacites_1NSI_LANGAGES-ET-PROGRAMMATION.json \
  NSI/referentiel/capacites_1NSI_REPRESENTATION-DES-DONNEES-T.json \
  NSI/referentiel/capacites_1NSI_TRAITEMENT-DE-DONNEES-EN-TAB.json \
  NSI/referentiel/capacites_TNSI_ALGORITHMIQUE.json \
  NSI/referentiel/capacites_TNSI_ARCHITECTURES-MATERIELLES-SY.json \
  NSI/referentiel/capacites_TNSI_BASES-DE-DONNEES.json \
  NSI/referentiel/capacites_TNSI_HISTOIRE-DE-L-INFORMATIQUE.json \
  NSI/referentiel/capacites_TNSI_LANGAGES-ET-PROGRAMMATION.json \
  NSI/referentiel/capacites_TNSI_STRUCTURES-DE-DONNEES.json \
  NSI/referentiel/capacites_1NSI_TYPES-CONSTRUITS.json
git diff --cached --check
git commit -m "[PROGRAMME] generalise la tracabilite aux six manuels"
```

### Task 9: Réconcilier les contrats auto-validés

**Files:**
- Create: `tests/test_contract_status_governance.py`
- Modify: exactly the 31 Terminale `contrat.yaml` files currently declaring
  `statut: valide` (9 TCOMPL, 5 TEXPERTES, 11 TSPE, 6 TNSI).

- [ ] **Step 1: Écrire le test rouge**

```python
def test_no_contract_claims_human_validation_without_registry(all_contracts):
    offenders = [
        path for path, data, raw in all_contracts
        if "valide humainement" in raw.lower() and not valid_approval_id(data)
    ]
    assert offenders == []
```

Ajouter un test qui impose le vocabulaire normalisé et conserve le contenu des
contrats lors de la migration. Le test contient l'ensemble attendu des 31
chemins et échoue si l'inventaire réel diffère de cet ensemble.

- [ ] **Step 2: Vérifier l'échec**

```bash
python3 -m pytest tests/test_contract_status_governance.py -q -p no:cacheprovider
```

Expected: FAIL avec exactement les 31 contrats Terminale auto-déclarés.

- [ ] **Step 3: Migrer uniquement le statut**

Pour les 31 contrats, remplacer uniquement la valeur du statut par :

```yaml
statut: SCIENTIFIC_REVIEW_REQUIRED  # aucune preuve de revue humaine enregistrée
```

Cette règle est déterministe : aucune preuve scientifique humaine n'étant
enregistrée, aucun contrat de ce lot ne reçoit un autre statut. Ne modifier ni
les capacités, ni les prérequis, ni les contenus. Le test compare le contenu
YAML normalisé avant/après en ignorant le seul champ `statut`.

- [ ] **Step 4: Vérifier et committer**

```bash
python3 -m pytest tests/test_contract_status_governance.py -q -p no:cacheprovider
git diff --check
git status --short
git add tests/test_contract_status_governance.py \
  Mathematiques/manuel-maths/chapitres/TCOMPL-CALCULS-AIRES/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TCOMPL-CORRELATION-CAUSALITE/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TCOMPL-ECHANTILLONNAGE/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TCOMPL-INEGALITES/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TCOMPL-INFERENCE-BAYESIENNE/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TCOMPL-LOGARITHME-HISTORIQUE/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TCOMPL-MODELES-EVOLUTION/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TCOMPL-MODELES-FONCTION/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TCOMPL-TEMPS-ATTENTE/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TEXP-ARITHMETIQUE/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TEXP-COMPLEXES-ALGEBRE-GEOMETRIE/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TEXP-COMPLEXES-TRIGO-POLYNOMES/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TEXP-GRAPHES/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TEXP-MATRICES-MARKOV/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TSPE-CALCUL-INTEGRAL/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TSPE-COMBINATOIRE/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TSPE-CONTINUITE/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TSPE-GEOMETRIE-ESPACE/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TSPE-LIMITES-FONCTIONS/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TSPE-LOGARITHME/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TSPE-PRIMITIVES-EQDIFF/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TSPE-PROBABILITES/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TSPE-SUITES-LIMITES/contrat.yaml \
  Mathematiques/manuel-maths/chapitres/TSPE-TRIGONOMETRIE/contrat.yaml \
  NSI/chapitres/TNSI-ALGORITHMIQUE/contrat.yaml \
  NSI/chapitres/TNSI-ARCHITECTURES-MATERIELLES-SY/contrat.yaml \
  NSI/chapitres/TNSI-BASES-DE-DONNEES/contrat.yaml \
  NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/contrat.yaml \
  NSI/chapitres/TNSI-LANGAGES-ET-PROGRAMMATION/contrat.yaml \
  NSI/chapitres/TNSI-STRUCTURES-DONNEES/contrat.yaml
git diff --cached --check
git commit -m "[AUDIT] remet les contrats auto-valides en revue requise"
```

### Task 10: Généraliser la source unique QCM

**Files:**
- Create: `schemas/qcm-source.schema.json`
- Create: `scripts/check_qcm_sources.py`
- Create: `tests/test_qcm_source_governance.py`
- Modify: `scripts/chapter_readiness.py`

- [ ] **Step 1: Écrire les tests rouges**

Le schéma `canonical_v1` exige question, options, clé, diagnostics par
distracteur, capacité, remédiation et re-test. Le test interdit qu'un `.tex`
soit déclaré source si un JSON canonique existe et distingue trois états :
`canonical_v1`, `legacy_json_incomplete` et `tex_only_or_missing`.

- [ ] **Step 2: Vérifier le rouge avant création du checker**

```bash
python3 -m pytest tests/test_qcm_source_governance.py -q -p no:cacheprovider
```

Expected: FAIL parce que le schéma/checker n'existe pas encore.

- [ ] **Step 3: Implémenter les deux modes sans migration massive**

`--validate-existing` valide la cohérence interne des JSON déjà présents,
classe les deux JSON sans `enonce/options` et les autres incomplets en
`legacy_json_incomplete`, imprime la dette, puis sort `0` si elle est
correctement classée. Cela ne les qualifie jamais de canoniques.
`--release-strict` exige `canonical_v1` pour les 51 chapitres. Wave 0 n'invente
ni ne convertit massivement les QCM.

- [ ] **Step 4: Raccorder readiness sans faux vert**

Une absence ou un QCM TeX seul bloque `READY`; elle ne bloque pas la génération
du dashboard.

- [ ] **Step 5: Vérifier et committer**

```bash
python3 scripts/check_qcm_sources.py --validate-existing
set +e
python3 scripts/check_qcm_sources.py --release-strict \
  > /tmp/nexus-wave0-qcm-release.txt 2>&1
qcm_status=$?
set -e
test "$qcm_status" -eq 1
grep -Eq '^QCM_RELEASE_STRICT=FAIL debt=[1-9][0-9]*$' \
  /tmp/nexus-wave0-qcm-release.txt
python3 -m pytest tests/test_qcm_source_governance.py -q -p no:cacheprovider
git diff --check
git status --short
git add schemas/qcm-source.schema.json scripts/check_qcm_sources.py \
  tests/test_qcm_source_governance.py scripts/chapter_readiness.py
git diff --cached --check
git commit -m "[TESTS] generalise le contrat de source unique QCM"
```

Expected: premier checker et pytest PASS; `--release-strict` FAIL avec un
compte de dette non nul et documenté. Ce rouge de release est attendu et ne
doit pas être transformé en succès pendant Wave 0.

### Task 11: Rendre le calcul `READY` strict et prouvé

**Files:**
- Modify: `scripts/chapter_readiness.py:143-338`
- Modify: `scripts/collection_dashboard.py:56-165`
- Modify: `scripts/build_manifest.py`
- Modify: `scripts/inventory_collection.py`
- Test: `tests/test_build_manifest.py`
- Test: `tests/test_inventory_collection.py`
- Test: create `tests/test_chapter_readiness.py`

- [ ] **Step 1: Écrire les tests rouges**

Cas synthétiques obligatoires :

```python
def test_no_scientific_review_is_not_ready(chapter): ...
def test_mapping_without_programme_review_is_not_ready(chapter): ...
def test_build_without_pdf_preflight_is_not_ready(chapter): ...
def test_generated_object_is_never_release_ready(chapter): ...
def test_enrichment_never_satisfies_mandatory_assessment(chapter): ...
def test_scope_decision_never_satisfies_chapter_review(chapter): ...
def test_incomplete_nexus_loop_is_not_ready(chapter): ...
def test_non_comparable_assessments_a_b_are_not_ready(chapter): ...
def test_open_or_unknown_p0_is_not_ready(chapter): ...
def test_pdf_present_without_observed_receipt_is_not_a_build(chapter): ...
def test_build_receipt_without_chapter_objects_is_not_ready(chapter): ...
def test_internal_ids_and_placeholders_leak_for_all_six_manuals(chapter): ...
```

- [ ] **Step 2: Vérifier l'échec**

Run:

```bash
python3 -m pytest tests/test_chapter_readiness.py -q -p no:cacheprovider
```

- [ ] **Step 3: Implémenter le minimum strict**

`release_ready` exige explicitement : boucle Nexus complète pour chaque
capacité obligatoire; QCM `canonical_v1`; évaluations A/B présentes avec une
preuve de comparabilité; zéro P0 dans `audit/FINDINGS_CANONICAL.json` courant
(`UNKNOWN` bloque); revue scientifique
et revue programme positives dans `audit/HUMAN_APPROVALS.yaml`; contrat dans un
statut assemblable; aucun objet `generated`; aucune capacité obligatoire sans
`covered_by`, `assessed_by`, `remediated_by` et preuve; builds élève/professeur
présents dans `audit/BUILD_MANIFEST.json`; reçus de séparation et préflight PDF
positifs. Vérifier `source_digest`, `model_digest`, SHA et que les objets
attendus du chapitre figurent dans `included_objects/ordered_trace`; corrections
et barèmes sont exclus élève et inclus professeur. Les gates `compile`,
`preflight` sont positifs; `student_separation` est obligatoire pour les seules
variantes élèves. Les statuts assemblables sont exactement
`READY_FOR_ASSEMBLY`, `ASSEMBLED`, `RELEASE_CANDIDATE`, `PUBLISHED`; refuser
`DRAFT`, `GENERATED`, tous les `*_REVIEW_REQUIRED` et
`HUMAN_REVIEW_REQUIRED`. Le compteur `generated` lit
tous les objets de rôle `production_object`, sans six sous-dossiers codés en
dur. Détection des IDs internes pour 1SPE, 1NSI, TSPE, TCOMPL, TEXP/TEXPERTES
et TNSI, plus placeholders et renvois provisoires.

Un TeX QCM dérivé d'un JSON `canonical_v1`, avec marqueur de génération,
contenu rendu synchronisé et empreinte concordante est seul surchargé
dynamiquement comme `generated_dependency` et exclu du compteur éditorial. Un
QCM TeX seul, legacy ou divergent reste `production_object` bloquant. Cette
logique vit dans l'inventaire; ne pas ajouter de glob QCM général à
`SOURCE_ROLES.yaml`. Les tests couvrent synchronisé, TeX seul, legacy et
divergent.

`collection_dashboard.py` dérive `build_eleve` et `build_professeur` des reçus
observés valides, jamais de la seule présence d'un PDF dans `build/`.

- [ ] **Step 4: Vérifier puis committer le moteur strict**

Run:

```bash
python3 -m pytest tests/test_chapter_readiness.py \
  tests/test_programme_traceability.py \
  tests/test_qcm_source_governance.py \
  tests/test_build_manifest.py \
  tests/test_inventory_collection.py -q -p no:cacheprovider
git diff --check
git status --short
git add scripts/chapter_readiness.py scripts/collection_dashboard.py \
  scripts/build_manifest.py scripts/inventory_collection.py \
  tests/test_build_manifest.py tests/test_inventory_collection.py \
  tests/test_chapter_readiness.py
git diff --cached --check
git commit -m "[AUDIT] rend le calcul readiness strictement prouve"
```

Expected: PASS.

- [ ] **Step 5: Réaligner le manifeste vide et recalculer les rapports**

```bash
jq '.builds | length' audit/BUILD_MANIFEST.json
python3 scripts/build_manifest.py --refresh-empty
python3 scripts/chapter_readiness.py --json audit/CHAPTER_READINESS.json
python3 scripts/collection_dashboard.py
python3 -m pytest tests/test_chapter_readiness.py \
  tests/test_inventory_collection.py \
  tests/test_baseline_qualification.py -q -p no:cacheprovider
git diff --check
git status --short
git add audit/BUILD_MANIFEST.json audit/CHAPTER_READINESS.json \
  ETAT_COLLECTION_2026_2027.json ETAT_COLLECTION_2026_2027.md
git diff --cached --check
git commit -m "[AUDIT] recalcule la preparation des six manuels"
```

Expected: `builds=0`, aucun faux READY; les pourcentages peuvent baisser et
cette baisse est une correction de mesure, pas une régression de contenu.

---

## Chunk 4: Baseline, builds, audits et handoff Wave 0

### Task 12: Mettre à jour la source de vérité depuis les faits recalculés

**Files:**
- Modify: `SOURCE_DE_VERITE.md`
- Create: `scripts/render_source_de_verite.py`
- Create: `tests/test_source_de_verite.py`

- [ ] **Step 1: Écrire les tests rouges**

Délimiter dans le Markdown un bloc
`<!-- BEGIN GENERATED COLLECTION STATE -->` / `<!-- END GENERATED COLLECTION
STATE -->`. Le test appelle le renderer en mémoire et exige : bloc identique au
fichier; exactement six lignes manuels; `chapitres_total`, objets, READY et PDF
égaux à `ETAT_COLLECTION_2026_2027.json` et `audit/BUILD_MANIFEST.json`;
visibilité `PUBLIC`; chaîne interdite `assembleur TNSI manquant` absente; état
de `feature/1spe-bat-2026` dérivé de
`audit/integration/1spe-bo2026-portage.json`, jamais d'un diff implicite.

- [ ] **Step 2: Vérifier l'échec**

Run:

```bash
python3 -m pytest tests/test_source_de_verite.py -q -p no:cacheprovider
```

- [ ] **Step 3: Corriger le document sans modifier les inventaires à la main**

`scripts/render_source_de_verite.py --write` ne remplace que le bloc généré et
lit dashboard, build manifest, manifeste de portage et Git. La visibilité vient
de `gh repo view cyranoaladin/manuels-nexus --json visibility`, encapsulé et
mocké dans les tests; elle ne peut pas être supposée depuis Git local.
Documenter l'assembleur TNSI comme présent; son statut de release vient du
dashboard. Le reste du document historique n'est pas supprimé dans ce lot.

- [ ] **Step 4: Vérifier et committer**

```bash
python3 scripts/render_source_de_verite.py --write
python3 scripts/render_source_de_verite.py --check
python3 -m pytest tests/test_source_de_verite.py -q -p no:cacheprovider
git diff --check
git status --short
git add SOURCE_DE_VERITE.md scripts/render_source_de_verite.py \
  tests/test_source_de_verite.py
git diff --cached --check
git commit -m "[DOCS] realigne la source de verite sur les builds observes"
```

### Task 13: Construire et suivre TNSI élève/professeur

**Files:**
- Modify: `NSI/.gitignore`
- Modify: `NSI/scripts/pdf_integrity.py`
- Add: `NSI/build/MANUEL_TNSI/MANUEL_TNSI_eleve.pdf`
- Add: `NSI/build/MANUEL_TNSI/MANUEL_TNSI_professeur.pdf`
- Test: `NSI/tests/test_book_preflight.py`
- Test: `NSI/tests/test_pdf_integrity.py`
- Test: `tests/test_build_manifest.py`

- [ ] **Step 1: Écrire les tests rouges anti-fuite TNSI**

Ajouter des PDF/texte synthétiques contenant séparément `TNSI-INTERNE`,
`Barème enseignant`, `Réponse professeur` et `Note enseignant`. Chacun doit
produire une fuite élève. Ajouter le cas témoin d'un texte élève légitime.

```bash
python3 -m pytest NSI/tests/test_pdf_integrity.py -q -p no:cacheprovider
```

Expected: FAIL pour les quatre nouvelles formulations.

- [ ] **Step 2: Étendre le gate NSI sans faux positifs**

Étendre la détection des IDs à `(?:1NSI|TNSI)-...` et les formulations
professeur/barème/note, en conservant casse et accents tolérés. Rejouer
`NSI/tests/test_pdf_integrity.py`; expected PASS.

- [ ] **Step 3: Exécuter les tests d'assembleur avant build**

```bash
python3 -m pytest NSI/tests/test_assemble_manuel.py \
  NSI/tests/test_book_preflight.py -q -p no:cacheprovider
```

- [ ] **Step 4: Construire la variante élève**

```bash
python3 NSI/scripts/assemble_manuel.py --book TNSI --variant eleve
```

- [ ] **Step 5: Construire la variante professeur**

```bash
python3 NSI/scripts/assemble_manuel.py --book TNSI --variant professeur
```

- [ ] **Step 6: Vérifier fuite et préflight**

Run:

```bash
python3 -m pytest NSI/tests/test_book_preflight.py tests/test_build_manifest.py \
  -q -p no:cacheprovider
```

Expected: deux builds locaux TNSI, aucun corrigé/barème dans élève et préflight
positif. Un retour non-zéro, une fuite ou un préflight rouge arrête la tâche.

- [ ] **Step 7: Suivre exactement les deux PDF canoniques**

Ajouter à `NSI/.gitignore` les exceptions exactes du dossier TNSI et de ses
deux PDF, sur le modèle 1NSI. Vérifier :

```bash
git check-ignore NSI/build/MANUEL_TNSI/MANUEL_TNSI_eleve.pdf
git check-ignore NSI/build/MANUEL_TNSI/MANUEL_TNSI_professeur.pdf
```

Expected: les deux commandes sortent `1` et n'impriment rien.

- [ ] **Step 8: Commit du gate et des deux PDF reproductibles**

```bash
git diff --check
git status --short
git add NSI/.gitignore NSI/scripts/pdf_integrity.py \
  NSI/tests/test_pdf_integrity.py \
  NSI/build/MANUEL_TNSI/MANUEL_TNSI_eleve.pdf \
  NSI/build/MANUEL_TNSI/MANUEL_TNSI_professeur.pdf
git diff --cached --check
git commit -m "[PDF] suit les builds TNSI eleve et professeur"
```

### Task 14: Construire 1SPE et comparer à la référence `main`

**Files:**
- Create: `scripts/compare_1spe_integration.py`
- Create: `tests/test_compare_1spe_integration.py`
- Modify: `Mathematiques/manuel-maths/scripts/pdf_integrity.py`
- Modify: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
- Test: `Mathematiques/manuel-maths/tests/test_pdf_integrity.py`
- Test: `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py`
- Create: `audit/integration/1spe-bo2026-comparison.json`
- Create visual evidence under: `audit/integration/1spe-bo2026-pages/`
- Modify generated/tracked:
  `Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf`
- Modify generated/tracked:
  `Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf`
- Modify: `audit/BUILD_MANIFEST.json`

- [ ] **Step 1: Capturer la référence sans la modifier**

```bash
mkdir -p /tmp/nexus-wave0-1spe-parent
git show a21ff532:Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf \
  > /tmp/nexus-wave0-1spe-parent/MANUEL_1SPE_eleve.pdf
git show a21ff532:Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf \
  > /tmp/nexus-wave0-1spe-parent/MANUEL_1SPE_professeur.pdf
sha256sum /tmp/nexus-wave0-1spe-parent/*.pdf
pdfinfo /tmp/nexus-wave0-1spe-parent/MANUEL_1SPE_eleve.pdf
pdfinfo /tmp/nexus-wave0-1spe-parent/MANUEL_1SPE_professeur.pdf
```

Enregistrer SHA-256, pages, taille et texte extrait; les fichiers temporaires
ne sont jamais ajoutés au dépôt.

- [ ] **Step 2: Écrire les tests rouges du préflight 1SPE complet**

Ajouter les cas log `Overfull/Underfull`, métadonnée absente, signets/liens
absents et preuve marginale absente. Dans le test d'assembleur observé, refuser
la création du reçu si `require_margin_proof=True` n'est pas satisfait.

```bash
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_pdf_integrity.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  -q -p no:cacheprovider
```

Expected: FAIL sur les nouveaux cas.

- [ ] **Step 3: Raccorder le préflight réel et vérifier**

Étendre `pdf_integrity.py` aux diagnostics de boîte, métadonnées, outlines et
liens. `assemble_manuel.py` génère et transmet les trois preuves
`MarginEvidence` du PDF réel, appelle `verify_pdf(...,
require_margin_proof=True, margin_evidence=...)`, puis seulement crée un reçu
`preflight.passed=true`. Rejouer les deux fichiers de tests, puis toute la suite
mathématique; expected PASS.

- [ ] **Step 4: Construire élève et professeur**

```bash
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  --manual 1SPE --variant eleve
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  --manual 1SPE --variant professeur
```

Tout retour non-zéro arrête la tâche. Ne jamais réintroduire les PNG V5.B-it2.

- [ ] **Step 5: Écrire les tests rouges du comparateur**

Écrire d'abord les tests du comparateur : PDF absent/corrompu, page supprimée,
ID interne ou corrigé visible dans élève, différences de texte et rendu
échantillonné.

```bash
python3 -m pytest tests/test_compare_1spe_integration.py -q -p no:cacheprovider
```

Expected: FAIL car le comparateur n'est pas implémenté.

- [ ] **Step 6: Implémenter et exécuter le comparateur**

Le comparateur reçoit quatre chemins explicites, extrait texte,
pages, métadonnées, objets observés et rend aux pages 1, 2, 3, 10, 25, 50 et
dernière page existante de chaque variante. Il produit le JSON et les PNG de
preuve sans modifier les baselines `validations/v5-it*`.

```bash
python3 -m pytest tests/test_compare_1spe_integration.py -q -p no:cacheprovider
python3 scripts/compare_1spe_integration.py \
  --before-eleve /tmp/nexus-wave0-1spe-parent/MANUEL_1SPE_eleve.pdf \
  --before-professeur /tmp/nexus-wave0-1spe-parent/MANUEL_1SPE_professeur.pdf \
  --after-eleve Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf \
  --after-professeur Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf \
  --output audit/integration/1spe-bo2026-comparison.json \
  --render-dir audit/integration/1spe-bo2026-pages
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_maquette_v5.py \
  Mathematiques/manuel-maths/tests/test_margin_layout.py \
  Mathematiques/manuel-maths/tests/test_margin_compositor_pdf.py \
  -q -p no:cacheprovider
```

Expected: aucune fuite/collision; différences de contenu attendues reliées aux
objets programme dans le JSON. Les planches sont inspectées avant commit; toute
régression non expliquée est un arrêt.

- [ ] **Step 7: Commit séparé**

```bash
git diff --check
git status --short
git add scripts/compare_1spe_integration.py tests/test_compare_1spe_integration.py \
  Mathematiques/manuel-maths/scripts/pdf_integrity.py \
  Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  Mathematiques/manuel-maths/tests/test_pdf_integrity.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  audit/integration/1spe-bo2026-comparison.json \
  audit/integration/1spe-bo2026-pages \
  Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf \
  Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf
git diff --cached --check
git commit -m "[PDF] compare les builds 1SPE apres integration BO 2026"
```

- [ ] **Step 8: Qualifier toute nouvelle dette avant les reçus**

Le commit PDF/code change nécessairement les digests du modèle. Avant toute
capture de baseline, réaligner inconditionnellement l'enveloppe encore vide,
puis régénérer exactement les six artefacts gérés :

```bash
test -z "$(git status --porcelain)"
jq -e '.builds | length == 0' audit/BUILD_MANIFEST.json
python3 scripts/build_manifest.py --refresh-empty
git diff --check
git status --short
git add audit/BUILD_MANIFEST.json
git diff --cached --check
git commit -m "[AUDIT] realigne le manifeste vide avant qualification Wave 0"
python3 scripts/inventory_collection.py
git diff --check
git status --short
git add audit/INVENTAIRE_COLLECTION.json audit/INVENTAIRE_COLLECTION.md \
  ETAT_COLLECTION.md audit/AUDIT_CONSOLIDE.md \
  audit/ECARTS_ET_CONTRADICTIONS.yaml audit/MATRICE_LIVRABLES.yaml
git diff --cached --check
git commit -m "[AUDIT] regenere l inventaire avant qualification Wave 0"
python3 scripts/inventory_collection.py --check --validate-model
test -z "$(git status --porcelain)"
```

Seulement après cette validation des digests, capturer `--fail-on-new` en JSON.
Si
`.comparison.new|length == 0`, poursuivre. Si ce nombre est positif, appliquer
avant les builds observés le protocole approuvé
`HUM-2026-08-11-BASELINE-WAVE0` : produire
`audit/BASELINE_QUALIFICATION_DECISION_WAVE0.md`; inscrire exactement ces
fingerprints, catégories, owners, nombre et digest dans
`audit/BASELINE_QUALIFICATION_POLICY.yaml`; recalculer son `control_digest` avec
`scripts.baseline_qualification.control_digest`; vérifier puis matérialiser :

```bash
python3 scripts/inventory_collection.py \
  --materialize-baseline-qualifications --check
python3 scripts/inventory_collection.py \
  --materialize-baseline-qualifications
python3 scripts/inventory_collection.py \
  --materialize-baseline-qualifications --check
```

Inspecter et committer séparément la décision/politique, puis
`audit/ANOMALY_DISPOSITIONS.yaml`, `audit/UNQUALIFIED_ANOMALIES.json` et
`.md`. Chaque entrée reste `open_debt`, `release_acceptance=false`. Recalculer
les six artefacts d'inventaire, rafraîchir et committer le manifeste encore
vide. Interdictions : fingerprint supplémentaire, dette masquée, extension
sans `HUM-2026-08-11-BASELINE-WAVE0`. Refaire la capture et exiger que `new`
reste exactement égal au jeu scellé (même nombre et digest); la
matérialisation ne le fait pas disparaître.

Les commits conditionnels utilisent deux listes explicites, jamais un glob :

```bash
git diff --check
git status --short
git add audit/BASELINE_QUALIFICATION_DECISION_WAVE0.md \
  audit/BASELINE_QUALIFICATION_POLICY.yaml
git diff --cached --check
git commit -m "[AUDIT] scelle la qualification de dette Wave 0"
git diff --check
git status --short
git add audit/ANOMALY_DISPOSITIONS.yaml \
  audit/UNQUALIFIED_ANOMALIES.json audit/UNQUALIFIED_ANOMALIES.md
git diff --cached --check
git commit -m "[AUDIT] materialise la qualification de dette Wave 0"
```

Après ces commits conditionnels, répéter le réalignement du manifeste vide et
le commit explicite des six artefacts gérés avant la nouvelle capture.

- [ ] **Step 9: Rebuild propre et enregistrement observé des quatre PDF Wave 0**

```bash
python3 NSI/scripts/assemble_manuel.py --book TNSI --variant eleve --record-observed
python3 NSI/scripts/assemble_manuel.py --book TNSI --variant professeur --record-observed
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  --manual 1SPE --variant eleve --record-observed
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  --manual 1SPE --variant professeur --record-observed
git status --short
python3 -m pytest Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  tests/test_build_manifest.py -q -p no:cacheprovider
```

L'enregistreur refuse tout WIP autre que son manifeste. Expected: les quatre
PDF restent bit-à-bit identiques; seul `audit/BUILD_MANIFEST.json` est modifié
et contient les quatre reçus TNSI/1SPE. Sinon arrêt pour non-reproductibilité.

```bash
git diff --check
git status --short
git add audit/BUILD_MANIFEST.json
git diff --cached --check
git commit -m "[AUDIT] enregistre les builds observes Wave 0"
```

### Task 15: Recalculer puis gouverner la baseline après les builds

**Files:**
- Modify conditionally: `audit/BASELINE_QUALIFICATION_POLICY.yaml`
- Modify conditionally: `audit/ANOMALY_DISPOSITIONS.yaml`
- Modify conditionally: `audit/UNQUALIFIED_ANOMALIES.json`
- Modify conditionally: `audit/UNQUALIFIED_ANOMALIES.md`
- Modify conditionally: `audit/BUILD_MANIFEST.json`
- Modify only through the canonical command: `audit/ANOMALIES_BASELINE.json`
- Modify generated: `audit/BASELINE_UPDATE_REPORT.md`
- Modify generated: `audit/BASELINE_FREEZE_REPORT.md`

- [ ] **Step 1: Capturer la comparaison JSON sans écrire**

```bash
set +e
python3 scripts/inventory_collection.py --fail-on-new \
  > /tmp/nexus-wave0-baseline-before.json
baseline_status=$?
set -e
test "$baseline_status" -eq 0 -o "$baseline_status" -eq 5
jq -e '.comparison | has("new") and has("unchanged") and has("resolved")' \
  /tmp/nexus-wave0-baseline-before.json
test -z "$(git status --porcelain)"
```

Expected: JSON valide; la commande ne modifie pas l'arbre. Si le code retour
est autre que succès ou dette nouvelle gouvernée, arrêter.

- [ ] **Step 2: Comparer fingerprint par fingerprint**

Qualifier chaque `new`, `unchanged` et `resolved`; vérifier dispositions,
owners et preuves. L'autorisation applicable est
`HUM-2026-08-11-BASELINE-WAVE0` dans `audit/HUMAN_APPROVALS.yaml`. Elle
n'autorise que ce protocole et ne vaut pas approbation de release. Si un build
a créé une empreinte absente du jeu exact qualifié en Task 14, ne pas l'ajouter
à la baseline : corriger le build/gate et répéter Task 14 Step 9. Les seules
empreintes `new` acceptables sont donc zéro, ou l'ensemble exact déjà scellé et
matérialisé avant les reçus de Task 14.

- [ ] **Step 3: Sceller la transition finale et revalider les reçus**

Si `new > 0`, régénérer dans `approved_transition` depuis le candidat final :
digest de la baseline initiale, comptes actifs initial/final, compte résolu
initial, fingerprints résolus et leur digest, comptes par catégorie, paires
modifiées et leur digest. Recalculer `control_digest`, valider le schéma et
committer la politique. Rematérialiser les dispositions pour le nouveau digest
de politique, vérifier nombre/digest exacts et committer les quatre artefacts
conditionnels.

```bash
git diff --check
git status --short
git add audit/BASELINE_QUALIFICATION_POLICY.yaml
git diff --cached --check
git commit -m "[AUDIT] scelle la transition finale de baseline Wave 0"
git diff --check
git status --short
git add audit/ANOMALY_DISPOSITIONS.yaml \
  audit/UNQUALIFIED_ANOMALIES.json audit/UNQUALIFIED_ANOMALIES.md
git diff --cached --check
git commit -m "[AUDIT] rematerialise les dispositions finales Wave 0"
```

Comme `ANOMALY_DISPOSITIONS.yaml` appartient au digest du modèle, vérifier le
manifeste. S'il devient périmé, conserver les anciens reçus dans Git puis :

```bash
python3 scripts/build_manifest.py --invalidate-stale \
  --reason "HUM-2026-08-11-BASELINE-WAVE0 : politique finale, rebuild identique requis" \
  --approved-by "Alaeddine Ben Rhouma"
git diff --check
git status --short
git add audit/BUILD_MANIFEST.json
git diff --cached --check
git commit -m "[AUDIT] invalide les recus apres politique finale Wave 0"
python3 NSI/scripts/assemble_manuel.py --book TNSI --variant eleve --record-observed
python3 NSI/scripts/assemble_manuel.py --book TNSI --variant professeur --record-observed
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  --manual 1SPE --variant eleve --record-observed
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  --manual 1SPE --variant professeur --record-observed
git diff --check
git status --short
git add audit/BUILD_MANIFEST.json
git diff --cached --check
git commit -m "[AUDIT] regenere les recus apres politique finale Wave 0"
```

Les quatre PDF doivent rester bit-à-bit identiques. Recalculer et committer les
six artefacts d'inventaire, recapturer le candidat et exiger exactement les
mêmes ensembles/digests `new`, `resolved`, `modified` avant de continuer.

- [ ] **Step 4: Mettre à jour via la commande gouvernée**

Si `new == 0` :

```bash
python3 scripts/inventory_collection.py --update-baseline \
  --reason "HUM-2026-08-11-BASELINE-WAVE0 : fermetures prouvees et dette encore reelle" \
  --approved-by "Alaeddine Ben Rhouma"
```

Si `new > 0`, vérifier d'abord que nombre et digest égalent exactement le jeu
qualifié en Task 14, puis :

```bash
python3 scripts/inventory_collection.py --update-baseline \
  --allow-approved-baseline-extension \
  --reason "HUM-2026-08-11-BASELINE-WAVE0 : extension exacte qualifiee et fermetures prouvees" \
  --approved-by "Alaeddine Ben Rhouma"
```

Toute autre situation arrête sans écrire. Comparer le rapport écrit au JSON
candidat : aucune disparition non classée, aucune dette réelle effacée, toute
fermeture prouvée.

- [ ] **Step 5: Vérifier et committer**

```bash
python3 scripts/inventory_collection.py --validate-model
python3 scripts/inventory_collection.py --fail-on-new
python3 -m pytest tests/ -q -p no:cacheprovider
git diff --check
git status --short
git add audit/ANOMALIES_BASELINE.json audit/BASELINE_UPDATE_REPORT.md \
  audit/BASELINE_FREEZE_REPORT.md
git diff --cached --check
git commit -m "[AUDIT] reconcilie la baseline Wave 0 par empreinte"
```

Expected: `GOVERNANCE_TESTS_RED=0`, sans réduction artificielle de dette.

### Task 16: Vérification complète, scans et handoff humain

**Files:**
- Create: `scripts/public_repo_scan.py`
- Create: `tests/test_public_repo_scan.py`
- Create: `audit/PUBLIC_REPO_SCAN.json`
- Create: `audit/WAVE_0_COMPLETION_REPORT.md`
- Modify generated: `SOURCE_DE_VERITE.md`
- Update generated dashboards and manifests if required.

- [ ] **Step 1: Tests complets**

```bash
python3 -m pytest Mathematiques/manuel-maths/tests -q -p no:cacheprovider
python3 -m pytest NSI/tests -q -p no:cacheprovider
python3 -m pytest tests -q -p no:cacheprovider
```

Expected: zéro échec. Consigner les nombres exacts, sans reprendre des nombres
historiques.

- [ ] **Step 2: Gates de collection**

```bash
python3 scripts/inventory_collection.py --check --validate-model
python3 scripts/inventory_collection.py --fail-on-new
python3 scripts/programme_traceability.py --check
python3 scripts/check_programme_registry.py
python3 scripts/check_qcm_sources.py --validate-existing
```

Expected: verts. `--release-strict` peut rester rouge uniquement pour la dette
éditoriale réelle des manuels, jamais pour une incohérence Wave 0.

Exécuter séparément et consigner comme dette attendue, jamais comme gate vert :

```bash
set +e
python3 scripts/check_qcm_sources.py --release-strict \
  > /tmp/nexus-wave0-qcm-release-final.txt 2>&1
qcm_status=$?
python3 scripts/inventory_collection.py --release-strict \
  > /tmp/nexus-wave0-collection-release-final.json 2>&1
collection_status=$?
set -e
test "$qcm_status" -eq 1
grep -Eq '^QCM_RELEASE_STRICT=FAIL debt=[1-9][0-9]*$' \
  /tmp/nexus-wave0-qcm-release-final.txt
test "$collection_status" -eq 7
jq -e '.gate == "release-strict" and .success == false' \
  /tmp/nexus-wave0-collection-release-final.json
```

Expected: non-zéro tant que les chapitres ne satisfont pas les critères de
release; chaque raison doit correspondre au dashboard, sans erreur
d'infrastructure Wave 0.

- [ ] **Step 3: Contrôle visuel anti-collision**

```bash
python3 -m pytest \
  Mathematiques/manuel-maths/tests/test_maquette_v5.py \
  Mathematiques/manuel-maths/tests/test_margin_layout.py \
  Mathematiques/manuel-maths/tests/test_margin_compositor_pdf.py \
  -q -p no:cacheprovider
```

- [ ] **Step 4: Écrire les tests rouges du scan dépôt public**

Les tests rouges créent des fixtures contenant clé API, mail scolaire, CSV de
notes, SQLite, secret en casse mixte, `.env` imbriqué et faux positif
documentaire. Ajouter des PDF, DOCX/ZIP et archives contenant séparément mail
scolaire, champ `Nom de l'élève`, note individuelle et mention de copie
d'élève. Une fixture Git commite un secret puis le supprime sur l'historique
courant; une autre place une donnée sensible uniquement dans une branche ou un
tag distinct. Le scan de tous les objets atteignables doit encore les bloquer
sans jamais imprimer leur valeur. Ajouter des archives surdimensionnées,
imbriquées et à ratio de compression hostile pour prouver les limites de
sécurité sans décompression non bornée.

```bash
python3 -m pytest tests/test_public_repo_scan.py -q -p no:cacheprovider
```

Expected: FAIL car le scanner n'est pas implémenté.

- [ ] **Step 5: Implémenter puis exécuter le scan dépôt public**

Exécuter d'abord `git fetch --all --tags --prune`. `scripts/public_repo_scan.py`
inspecte : fichiers suivis du worktree, fichiers non suivis destinés au commit,
index Git, et tous les blobs atteignables depuis les références locales,
distantes et tags via `git rev-list --objects --all` + `git cat-file`. Il ne
suit pas les symlinks, ne journalise jamais la valeur d'un secret et produit
des chemins/fingerprints redacted. Il classe `.env`, clés/certificats, emails,
CSV, SQLite et extensions de bases.

Pour chaque blob, le scanner inspecte les octets et, sous quotas stricts de
taille totale, nombre de membres, profondeur, ratio de compression et temps,
extrait le texte PDF avec Poppler et inspecte les membres XML/texte des formats
Office (`.docx`, `.xlsx`, `.pptx`), ZIP et archives prises en charge. Une
archive chiffrée, corrompue, dépassant les limites ou de type reconnu mais non
inspectable est un finding bloquant, jamais un succès silencieux.

```bash
git fetch --all --tags --prune
python3 -m pytest tests/test_public_repo_scan.py -q -p no:cacheprovider
python3 scripts/public_repo_scan.py \
  --include-worktree --include-untracked --include-index \
  --all-reachable-refs \
  --output audit/PUBLIC_REPO_SCAN.json
jq -e '.blocking_findings == 0' audit/PUBLIC_REPO_SCAN.json
git ls-files '*.csv' '*.tsv' '*.sqlite' '*.sqlite3' '*.db'
git ls-files ':(glob)**/.env' ':(glob)**/.env.*' '*.pem' '*.key' '*.p12' '*.pfx'
git grep -I -l -E -i '(api[_-]?key|client[_-]?secret|access[_-]?token|password)' -- .
git grep -I -l -E -i '[A-Z0-9._%+-]+@(ac-|lyc|college|eleve|etu)[A-Z0-9.-]*\.[A-Z]{2,}' -- .
```

Les deux `git grep` n'impriment que les noms de fichiers. Toute correspondance
et chaque CSV/SQLite sont qualifiés dans le JSON (`safe_technical_fixture` ou
`blocking`), sans recopier de donnée. Expected: `blocking_findings=0`; sinon
arrêt avant commit/push.

- [ ] **Step 6: Recalculer les états finaux et la source de vérité**

```bash
python3 scripts/chapter_readiness.py --json audit/CHAPTER_READINESS.json
python3 scripts/collection_dashboard.py
python3 scripts/render_source_de_verite.py --write
python3 scripts/render_source_de_verite.py --check
python3 -m pytest tests/test_source_de_verite.py \
  tests/test_chapter_readiness.py -q -p no:cacheprovider
```

Expected: dashboard et source de vérité reflètent les quatre reçus observés,
la visibilité GitHub réelle et le manifeste de portage.

- [ ] **Step 7: Produire le rapport Wave 0**

Le rapport contient : HEAD, branche, origin match, propreté, six manuels,
capacités, objets generated/reviewed, P0/P1, tests, les douze emplacements PDF,
manuels bloqués et prochaine action Wave 1. Pour chaque PDF, utiliser
uniquement `OBSERVED_PREFLIGHT_PASS`, `TRACKED_NOT_REBUILT_WAVE0`, `MISSING` ou
`PREFLIGHT_FAIL`; ne jamais écrire `PASS` pour un PDF seulement présent sur
disque. Recalculer dashboards/manifests avant rédaction.

- [ ] **Step 8: Commit du rapport final**

```bash
git diff --check
git status --short
git add scripts/public_repo_scan.py tests/test_public_repo_scan.py \
  audit/PUBLIC_REPO_SCAN.json audit/WAVE_0_COMPLETION_REPORT.md \
  ETAT_COLLECTION_2026_2027.json ETAT_COLLECTION_2026_2027.md \
  audit/CHAPTER_READINESS.json SOURCE_DE_VERITE.md
python3 scripts/public_repo_scan.py \
  --include-worktree --include-untracked --include-index \
  --all-reachable-refs \
  --output audit/PUBLIC_REPO_SCAN.json
jq -e '.blocking_findings == 0' audit/PUBLIC_REPO_SCAN.json
git diff --check
git status --short
git add audit/PUBLIC_REPO_SCAN.json
git diff --cached --check
git commit -m "[AUDIT] cloture les preuves de Wave 0"
```

- [ ] **Step 9: Préflight Git exécutable et push**

```bash
git diff --check
test -z "$(git status --porcelain)"
test "$(git branch --show-current)" = "integration/1spe-bo2026-traceability"
python3 -m pytest Mathematiques/manuel-maths/tests -q -p no:cacheprovider
python3 -m pytest NSI/tests -q -p no:cacheprovider
python3 -m pytest tests -q -p no:cacheprovider
python3 scripts/inventory_collection.py --check --validate-model
python3 scripts/inventory_collection.py --fail-on-new
python3 scripts/programme_traceability.py --check
python3 scripts/check_programme_registry.py
python3 scripts/check_qcm_sources.py --validate-existing
python3 scripts/render_source_de_verite.py --check
git fetch --all --tags --prune
git merge-base --is-ancestor origin/main HEAD
test "$(gh repo view cyranoaladin/manuels-nexus --json visibility --jq .visibility)" = "PUBLIC"
git push -u origin integration/1spe-bo2026-traceability
git fetch origin integration/1spe-bo2026-traceability
test "$(git rev-parse HEAD)" = \
  "$(git rev-parse origin/integration/1spe-bo2026-traceability)"
```

Avant le push, le worktree doit être propre et `origin/main` doit encore être
le parent réconcilié attendu. S'il a avancé, arrêter et auditer la divergence
sans reset, rebase, merge automatique ni perte. Après le push, vérifier que le
SHA distant de la branche égale le SHA local.

- [ ] **Step 10: Intégration contrôlée déjà autorisée puis démarrage Wave 1**

La décision `HUM-2026-08-11-1SPE-INTEGRATION` autorise explicitement cette
intégration lorsque tous les gates précédents sont verts et qu'aucun contenu
n'est perdu. Vérifier une dernière fois que `main` local et `origin/main` sont
égaux au parent attendu, puis effectuer uniquement un fast-forward de `main`
vers la branche d'intégration et pousser sans force. Vérifier ensuite SHA local
`main` = SHA `origin/main`, worktree propre, puis produire le compte rendu exact
Wave 0 et démarrer Wave 1. Toute divergence ou impossibilité de fast-forward
est un conflit non récupérable automatiquement et déclenche le gate humain.

```bash
test "$(git rev-parse main)" = "$(git rev-parse origin/main)"
git switch main
git merge --ff-only integration/1spe-bo2026-traceability
git push origin main
git fetch origin main
test "$(git rev-parse main)" = "$(git rev-parse origin/main)"
test -z "$(git status --porcelain)"
```

---

## Critères de sortie Wave 0

- [ ] `LOCAL_HEAD` poussé sur la branche dédiée.
- [ ] `WORKTREE_CLEAN=true` après commits.
- [ ] `REPO_VISIBILITY=PUBLIC` vérifié.
- [ ] six programmes et modalités d'épreuves sourcés officiellement.
- [ ] référentiel 1SPE 2026 intégré sans ancienne baseline visuelle.
- [ ] dix contrats 1SPE conformes au schéma enrichi.
- [ ] six matrices générées et `OFFICIAL_CAPABILITIES_WITHOUT_MAPPING=0`.
- [ ] aucun contrat auto-validé sans registre humain.
- [ ] assembleur TNSI reconnu, élève/professeur construits et observés.
- [ ] baseline réconciliée fingerprint par fingerprint.
- [ ] gouvernance : zéro test rouge.
- [ ] tests mathématiques et NSI : zéro test rouge.
- [ ] dashboard et source de vérité recalculés.
- [ ] scans secrets/PII/CSV/SQLite qualifiés.
- [ ] maquette anti-collision de `main` préservée.
- [ ] rapport Wave 0 exact, intégration `main` réalisée sous
  `HUM-2026-08-11-1SPE-INTEGRATION`, puis Wave 1 démarrée.
