# 1NSI Remediation Separation Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** séparer physiquement les neuf corrigés actuellement inclus dans les sources de remédiation 1NSI, sans modifier leur contenu ni toucher à TNSI.

**Architecture:** les objets élèves restent sous `remediation/` avec leurs vérifications Python ; les blocs corrigés sont déplacés à l'identique sous `corriges/` avec des métadonnées résolubles. Le gate élève conserve son comportement global et gagne un filtre de préfixe fail-closed pour prouver séparément que 1NSI est propre.

**Tech Stack:** Python 3.11, pytest, LaTeX, LuaLaTeX, PyMuPDF, gates corpus Nexus.

---

## Chunk 1: Contrat et séparation physique

### Task 1: Écrire le test RED des neuf associations

**Files:**
- Create: `NSI/tests/test_remediation_separation.py`

- [ ] **Step 1: Définir l'inventaire contractuel**

Créer `EXPECTED` avec, pour chaque source, le chemin compagnon, l'ID de
l'environnement exercice et le SHA-256 du bloc `corrige` avant déplacement :

```python
EXPECTED = {
    "1NSI-ALGO-DICHO-GLOUTON-KNN/remediation/1NSI-ADGK-RE-C1.tex": (
        "1NSI-ALGO-DICHO-GLOUTON-KNN/corriges/1NSI-ADGK-RE-C1-CORRIGE.tex",
        "1NSI-ADGK-RE-C1-EX1",
        "38bf1cadf40b1e6d4edf301aeff79f28c12ccf8e423c434c4c948940fdf8510c",
    ),
    "1NSI-ALGO-PARCOURS-TRIS/remediation/1NSI-AGT-RE-C5.tex": (
        "1NSI-ALGO-PARCOURS-TRIS/corriges/1NSI-AGT-RE-C5-CORRIGE.tex",
        "1NSI-AGT-RE-C5-EX1",
        "1b940570a28f3516b319ad22928181987eaa5ff6a80c3acee6f34afca0aa0bfe",
    ),
    "1NSI-ARCHITECTURE-OS/remediation/1NSI-ARCHITECTURE-OS-RE-C5.tex": (
        "1NSI-ARCHITECTURE-OS/corriges/1NSI-ARCHITECTURE-OS-RE-C5-CORRIGE.tex",
        "1NSI-ARCHOS-RE-C5-EX1",
        "1fd440fa840751c3aeef1bf55584673685097a2456c93b552efa56622ea3226c",
    ),
    "1NSI-LANGAGE/remediation/1NSI-LANGAGE-RE-C4.tex": (
        "1NSI-LANGAGE/corriges/1NSI-LANGAGE-RE-C4-CORRIGE.tex",
        "1NSI-LANG-RE-C4-EX1",
        "46a23a39e01974d66875ea58f167ed1b91e9ad5300ed3c1a0d7dafc97dfb275e",
    ),
    "1NSI-PROJET-METHODES/remediation/1NSI-PM-RE-C3.tex": (
        "1NSI-PROJET-METHODES/corriges/1NSI-PM-RE-C3-CORRIGE.tex",
        "1NSI-PM-RE-C3-EX1",
        "6fb8fab1aa6155dcffc4872c8bc8337cedb207a03a61d8ae08ca0f4c7db18e47",
    ),
    "1NSI-RESEAUX/remediation/1NSI-RESEAUX-RE-C1.tex": (
        "1NSI-RESEAUX/corriges/1NSI-RESEAUX-RE-C1-CORRIGE.tex",
        "1NSI-RES-RE-C1-EX1",
        "e4c71b57e92a33a93a9d90ff33431a59aec8773c57e54ea387253aac5d85498f",
    ),
    "1NSI-TABLES/remediation/1NSI-TABLES-RE-C2.tex": (
        "1NSI-TABLES/corriges/1NSI-TABLES-RE-C2-CORRIGE.tex",
        "1NSI-TAB-RE-C2-EX1",
        "b7d1f5b9fe97b2d1ad141c55674e44aead8703474b54230c06e489512f4c0a1c",
    ),
    "1NSI-TYPES-BASE/remediation/1NSI-TYPES-BASE-RE-C3.tex": (
        "1NSI-TYPES-BASE/corriges/1NSI-TYPES-BASE-RE-C3-CORRIGE.tex",
        "1NSI-TB-RE-C3-EX1",
        "9e8590d3c4acb329724df9071e03624d196ed8899ee6b6fabf349ad1533a0ca4",
    ),
    "1NSI-WEB-IHM/remediation/1NSI-WEB-IHM-RE-C9.tex": (
        "1NSI-WEB-IHM/corriges/1NSI-WEB-IHM-RE-C9-CORRIGE.tex",
        "1NSI-WEB-RE-C9-EX1",
        "4869644f9734c9d79a43e66e2aab5b15d955cb9f776773bc3050674c93e5a96a",
    ),
}
```

- [ ] **Step 2: Tester les objets séparés**

Le test doit, pour chaque entrée :

- parser le META de la remédiation et du compagnon ;
- exiger l'absence de `\\begin{corrige}` dans la remédiation ;
- exiger exactement un environnement `exercice` dans la remédiation ;
- exiger exactement un environnement `corrige` dans le compagnon ;
- exiger `companion_meta["id"] == companion.stem` ;
- exiger `chapitre`, `type_objet == "corrige"`, capacité héritée,
  `status == "generated"` et `exercice_ref == source_meta["id"]` ;
- exiger que les IDs des environnements exercice/corrigé soient identiques ;
- recalculer le SHA-256 du bloc corrigé seul et le comparer à `EXPECTED`.

- [ ] **Step 3: Vérifier RED**

Run:

```bash
cd NSI
python3 -m pytest tests/test_remediation_separation.py -q
```

Expected: FAIL, car les neuf compagnons n'existent pas et les neuf remédiations
contiennent encore un bloc `corrige`.

### Task 2: Déplacer les neuf blocs sans réécriture

**Files:**
- Modify: les neuf fichiers `NSI/chapitres/1NSI-*/remediation/*.tex` listés dans `EXPECTED`
- Create: les neuf fichiers `NSI/chapitres/1NSI-*/corriges/*-CORRIGE.tex` listés dans `EXPECTED`
- Test: `NSI/tests/test_remediation_separation.py`

- [ ] **Step 1: Créer chaque compagnon**

Ajouter une ligne META JSON sur une seule ligne, avec ce modèle :

```text
% META: {"id": "<stem-compagnon>", "chapitre": "<chapitre>", "type_objet": "corrige", "exercice_ref": "<id-meta-remediation>", "capacites": [...], "status": "generated"}
```

Copier ensuite le bloc complet `\\begin{corrige}...\\end{corrige}` sans modifier
aucun caractère interne.

- [ ] **Step 2: Retirer le bloc de la remédiation**

Conserver l'en-tête META, l'environnement exercice et le bloc
`BEGIN-VERIFY`/`END-VERIFY`. Ne modifier aucun autre texte.

- [ ] **Step 3: Vérifier GREEN et le code embarqué**

Run:

```bash
cd NSI
python3 -m pytest tests/test_remediation_separation.py -q
PYTHONPATH=scripts python3 - <<'PY'
from pathlib import Path
from verify_python import check_object

for path in sorted(Path("chapitres").glob("1NSI-*/remediation/*.tex")):
    assert check_object(path)["verdict"] != "fail", path
for path in sorted(Path("chapitres").glob("1NSI-*/corriges/*-CORRIGE.tex")):
    assert check_object(path)["verdict"] != "fail", path
PY
```

Expected: PASS ; aucune écriture dans `validations/`.

- [ ] **Step 4: Vérifier le périmètre et committer**

Run:

```bash
git diff --check
git diff --name-only a21b5d7
git status --short
```

Avant commit, aucun chemin `NSI/chapitres/TNSI-` ne doit être modifié.

```bash
git add NSI/tests/test_remediation_separation.py \
  NSI/chapitres/1NSI-*/remediation/*.tex \
  NSI/chapitres/1NSI-*/corriges/*-CORRIGE.tex
git commit -m "[LATEX] separe les corriges de remediation 1NSI"
```

---

## Chunk 2: Gate filtré fail-closed

### Task 3: Tester puis implémenter `--prefix`

**Files:**
- Modify: `NSI/tests/test_gates_corpus.py`
- Modify: `NSI/scripts/gates_corpus/check_eleve_no_corrige.py`

- [ ] **Step 1: Écrire les tests RED**

Extraire une API testable :

```python
checked, violations = scan(root, prefix="1NSI-")
```

Avec un `tmp_path`, tester séparément :

- une fuite 1NSI est détectée ;
- une fuite TNSI est ignorée par `prefix="1NSI-"` mais détectée sans filtre ;
- un fichier `build/` dont le chemin ou le contenu référence `1NSI-` est inspecté ;
- `prefix=""` et `prefix="   "` sont rejetés ;
- un préfixe sans chapitre est rejeté ;
- zéro fichier effectivement inspecté est rejeté.

- [ ] **Step 2: Vérifier RED**

Run:

```bash
cd NSI
python3 -m pytest tests/test_gates_corpus.py -q -k 'prefix or filtered_scan'
```

Expected: FAIL, car `scan` et `--prefix` n'existent pas.

- [ ] **Step 3: Implémenter minimalement**

Dans `check_eleve_no_corrige.py` :

- ajouter `argparse` ;
- implémenter `scan(root: Path, prefix: str | None)` ;
- préserver exactement `FORBIDDEN`, `ALLOWED_DIRS`, `ALLOWED_SUFFIXES` et
  `QCM_DIAG_RE` ;
- filtrer `chapitres/` par nom de chapitre ;
- filtrer `build/` par chemin ou contenu référençant le préfixe ;
- lever `ValueError` pour préfixe vide/blanc, chapitre absent ou zéro fichier ;
- faire retourner `2` au CLI pour un filtre invalide, `1` pour une violation et
  `0` pour un scan propre.

- [ ] **Step 4: Vérifier GREEN et committer**

Run:

```bash
cd NSI
python3 -m pytest tests/test_gates_corpus.py -q
python3 scripts/gates_corpus/check_eleve_no_corrige.py --prefix 1NSI-
python3 -m ruff check scripts/gates_corpus/check_eleve_no_corrige.py
```

Expected: tests verts, gate 1NSI vert et script du gate propre. Tout nouvel import
dans le fichier de test porte un `# noqa: E402` ciblé ; les six violations Ruff
historiques du fichier ne sont ni étendues ni refactorées dans cette passe.

```bash
git add NSI/scripts/gates_corpus/check_eleve_no_corrige.py NSI/tests/test_gates_corpus.py
git commit -m "[TESTS] cible le gate eleve sur le perimetre 1NSI"
```

---

## Chunk 3: Validation intégrée

### Task 4: Prouver la séparation sans toucher TNSI

**Files:**
- Verify: `NSI/build/books/MANUEL_1NSI_v1.pdf`
- Verify: `NSI/build/books/MANUEL_1NSI_v1_remediation.pdf`
- Verify: inventaire et diff Git

- [ ] **Step 1: Exécuter les tests pertinents**

```bash
cd NSI
python3 -m pytest tests/test_remediation_separation.py tests/test_gates_corpus.py \
  tests/test_assemble_book.py tests/test_book_preflight.py tests/test_verify_python.py -q
```

Expected: PASS.

- [ ] **Step 2: Vérifier les gates ciblé et global**

```bash
cd NSI
python3 scripts/gates_corpus/check_eleve_no_corrige.py --prefix 1NSI-
python3 scripts/gates_corpus/check_eleve_no_corrige.py
```

Expected: le premier retourne `0`. Le second retourne `1` et ses seules
violations `begin{corrige}` sous `remediation/` appartiennent aux cinq chemins
`TNSI-*` gelés.

- [ ] **Step 3: Reconstruire et comparer les PDF**

Baselines avant migration :

```text
complet PDF       b8eb0626907c705d91bd0b7a0e747b4fa8f1aca98a920f1a10f37558ce21c604
complet texte     b30c62100f72138e47fdf7a5e23572069100cf701fbeacf293e8a11383c3314f
complet pages     101
remediation PDF   6817b3d67e350f9bf7c8945d9f0d8e74c15b6208a382a735ba7ba5a2aaeaadf6
remediation texte 9e309917a376b4456ed101d0fa50e26f2e130d8261a9d344f684ceab1036d0b2
remediation pages 13
```

Run:

```bash
cd NSI
python3 scripts/assemble.py --book 1NSI --variant complet
python3 scripts/assemble.py --book 1NSI --variant remediation

test "$(pdfinfo build/books/MANUEL_1NSI_v1.pdf | awk '/^Pages:/{print $2}')" = "101"
test "$(sha256sum build/books/MANUEL_1NSI_v1.pdf | cut -d' ' -f1)" = \
  "b8eb0626907c705d91bd0b7a0e747b4fa8f1aca98a920f1a10f37558ce21c604"
test "$(pdftotext -layout build/books/MANUEL_1NSI_v1.pdf - | sha256sum | cut -d' ' -f1)" = \
  "b30c62100f72138e47fdf7a5e23572069100cf701fbeacf293e8a11383c3314f"

test "$(pdfinfo build/books/MANUEL_1NSI_v1_remediation.pdf | awk '/^Pages:/{print $2}')" = "13"
test "$(sha256sum build/books/MANUEL_1NSI_v1_remediation.pdf | cut -d' ' -f1)" = \
  "6817b3d67e350f9bf7c8945d9f0d8e74c15b6208a382a735ba7ba5a2aaeaadf6"
test "$(pdftotext -layout build/books/MANUEL_1NSI_v1_remediation.pdf - | sha256sum | cut -d' ' -f1)" = \
  "9e309917a376b4456ed101d0fa50e26f2e130d8261a9d344f684ceab1036d0b2"
```

Exiger les mêmes nombres de pages et SHA-256 de texte `pdftotext -layout`.
Comparer également les SHA-256 PDF ; toute différence doit être expliquée avant
de continuer. Les preflights automatiques doivent retourner `0`.

- [ ] **Step 4: Régénérer et committer les six artefacts d'inventaire**

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/finalisation-collection-v1
python3 scripts/inventory_collection.py --validate-model --fail-on-new
git status --short
```

Expected: seuls les six artefacts gérés changent :

```text
ETAT_COLLECTION.md
audit/AUDIT_CONSOLIDE.md
audit/ECARTS_ET_CONTRADICTIONS.yaml
audit/INVENTAIRE_COLLECTION.json
audit/INVENTAIRE_COLLECTION.md
audit/MATRICE_LIVRABLES.yaml
```

```bash
git add ETAT_COLLECTION.md audit/AUDIT_CONSOLIDE.md \
  audit/ECARTS_ET_CONTRADICTIONS.yaml audit/INVENTAIRE_COLLECTION.json \
  audit/INVENTAIRE_COLLECTION.md audit/MATRICE_LIVRABLES.yaml
git commit -m "[AUDIT] regenere l inventaire apres separation 1NSI"
```

- [ ] **Step 5: Vérifier l'inventaire et le gel TNSI**

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/finalisation-collection-v1
python3 scripts/inventory_collection.py --check --validate-model --fail-on-new
git diff --name-only a21b5d7..HEAD | rg '^NSI/chapitres/TNSI-' && exit 1 || true
git diff --check
git status --short --branch
```

Expected: les six rendus sont à jour, aucun nouveau `broken_reference`, aucun
chemin TNSI et worktree suivi propre. `--release-strict` n'est pas exécuté et
aucune publication n'est déclarée.

- [ ] **Step 6: Revue finale**

Faire relire le range `a21b5d7..HEAD` en priorité sur : fuite élève, références
META, conservation SHA-256, gate non affaibli, absence de changement TNSI et
preuves PDF.
