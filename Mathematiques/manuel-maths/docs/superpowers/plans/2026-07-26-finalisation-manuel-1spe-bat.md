# Finalisation du manuel 1SPE pour bon à tirer Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produire les ouvrages élève et professeur de mathématiques de première spécialité, conformes au programme applicable à la rentrée 2026, contrôlés de bout en bout et livrés sous forme de candidats numériques et de paquets imprimeur traçables.

**Architecture:** Un référentiel B.O. canonique et un manifeste d'objets pilotent tous les contrôles. Le manuel élève est composé en premier et exporte ses folios ; le livre du professeur consomme cette table, puis exporte la table croisée. Les PDF écran accessibles, les masters d'impression, les preuves de validation et les données physiques de l'imprimeur restent des sorties séparées afin qu'aucun jalon numérique ne soit confondu avec le BAT signé.

**Tech Stack:** Python 3.12, pytest 8, jsonschema, PyYAML, SymPy, LuaLaTeX/LaTeX Tagged PDF, TikZ/PGFPlots, PyMuPDF, Poppler 24.02, Ghostscript, veraPDF CLI 1.30.1, SHA-256, Make.

---

**Conception de référence :** `docs/superpowers/specs/2026-07-26-finalisation-manuel-1spe-bat-design.md`

**Règles d'exécution :**

- @superpowers:test-driven-development pour chaque évolution logicielle et chaque défaut reproductible ;
- @superpowers:subagent-driven-development avec un agent neuf par tâche, puis revue de conformité et revue de qualité ;
- @superpowers:systematic-debugging dès qu'un test, un build ou un préflight échoue ;
- @superpowers:verification-before-completion avant tout statut `certified` ou annonce de réussite ;
- aucun contenu n'est déclaré exact sur la seule foi de l'agent rédacteur : calcul indépendant, preuve ou revue contradictoire obligatoire ;
- les validations d'adresse, d'imprimeur, d'épreuve, de prototype et de signature sont enregistrées `blocked` tant que la preuve externe n'existe pas.

## Chunk 1: Référentiel, baseline et contrats de preuve

### Task 1: Épingler l'environnement de release et les commandes d'entrée

**Files:**
- Create: `release/toolchain.yaml`
- Create: `scripts/check_toolchain.py`
- Create: `tests/test_toolchain.py`
- Create: `validations/release-1spe/toolchain.json`
- Modify: `Makefile`
- Modify: `README.md`

- [x] **Step 1: écrire les tests rouges du contrat d'outillage**

```python
def test_toolchain_pins_accessibility_validator(toolchain):
    assert toolchain["verapdf"]["version"] == "1.30.1"
    assert toolchain["verapdf"]["profile"] == "ua1"
    assert toolchain["java"]["minimum_major"] == 21

def test_missing_blocking_binary_fails(monkeypatch, toolchain):
    monkeypatch.setattr("shutil.which", lambda _: None)
    result = check_toolchain(toolchain)
    assert result.status == "blocked"
    assert result.exit_code != 0
```

- [x] **Step 2: vérifier l'échec ciblé**

Run: `.venv/bin/python -m pytest tests/test_toolchain.py -q`

Expected: FAIL car `release/toolchain.yaml` et `scripts/check_toolchain.py` n'existent pas.

- [x] **Step 3: créer le manifeste d'outillage**

```yaml
schema_version: 1
python: "3.12"
java:
  minimum_major: 21
latex:
  engine: lualatex
  minimum_texlive: 2026
  tagged_pdf: true
verapdf:
  version: "1.30.1"
  profile: ua1
  report_format: mrr
poppler:
  minimum_version: "24.02.0"
  commands: [pdfinfo, pdffonts, pdftotext, pdftoppm]
ghostscript:
  minimum_version: "10.02"
```

- [x] **Step 4: implémenter `check_toolchain.py`**

Le contrôleur lit les versions réelles, y compris `java -version`, refuse une
version inférieure au contrat, produit
`validations/release-1spe/toolchain.json` et ne tente aucune installation
implicite. Un état `blocked` retourne le code 2.

La capacité Tagged PDF n'est jamais déduite de la seule année TeX Live : après
validation des versions, le contrôleur compile un document éphémère avec
`\DocumentMetadata{lang=fr,pdfversion=1.7,pdfstandard=ua-1,tagging=on}`, exige
le PDF puis obtient le code 0 de `verapdf -f ua1 --format mrr`. Tout autre
résultat reste `blocked` et le répertoire temporaire est supprimé.
Les binaires sont résolus une seule fois en chemins absolus sans suivre le
dernier lien symbolique, puis le lanceur exact est réutilisé pour les versions
et le smoke-test. Celui-ci s'exécute depuis son répertoire temporaire avec une
liste blanche d'environnement : seuls `PATH` et l'éventuel `JAVA_HOME`
proviennent du parent ; locale et fuseau sont fixés, tandis que HOME, TMP, XDG
et les caches TeX sont redirigés sous le répertoire éphémère. Un manifeste
inaccessible ou invalide remplace lui aussi atomiquement tout ancien rapport
par un rapport déterministe `blocked` en mode `0644`.

- [x] **Step 5: ajouter les cibles Make**

```make
release-toolchain:
	$(PY) scripts/check_toolchain.py --manifest release/toolchain.yaml

release-test:
	$(PY) -m pytest tests/ -q
```

- [x] **Step 6: documenter l'installation reproductible**

`README.md` doit distinguer l'environnement courant de l'environnement exigé pour une release, y compris Java 21 et veraPDF 1.30.1.

- [x] **Step 7: exécuter les tests et le contrôleur**

Run: `.venv/bin/python -m pytest tests/test_toolchain.py -q`

Expected: PASS.

Run: `make release-toolchain`

Expected: code 0 et `certified`, ou code 2 et `blocked` avec la liste exacte
des outils à installer ; jamais un faux PASS.

- [x] **Step 8: commit**

```bash
git add release/toolchain.yaml scripts/check_toolchain.py tests/test_toolchain.py validations/release-1spe/toolchain.json Makefile README.md
git commit -m "[1SPE][BAT] epingle la chaine de fabrication"
```

### Task 1B: Capturer l'état initial immuable

**Files:**
- Create: `schemas/baseline_1spe.schema.json`
- Create: `scripts/capture_initial_state_1spe.py`
- Create: `tests/test_capture_initial_state_1spe.py`
- Create: `validations/release-1spe/baseline.json`
- Create: `validations/release-1spe/baseline.md`

- [ ] **Step 1: écrire le test rouge de capture**

Le test exige l'inventaire et les SHA-256 des sources 1SPE, référentiels,
contrats, directives, rapports, tags Git et attestations. Chaque attestation
reçoit `reusable`, `stale` ou `review_required` avec justification et empreintes.

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_capture_initial_state_1spe.py -q`

Expected: FAIL car le capteur et le schéma n'existent pas.

- [ ] **Step 3: implémenter et exécuter avant toute correction**

Run: `.venv/bin/python scripts/capture_initial_state_1spe.py --root . --json validations/release-1spe/baseline.json --markdown validations/release-1spe/baseline.md`

Expected: code 0, état `initial_snapshot`, zéro fichier 1SPE, directive, rapport,
tag ou validation non classé.

- [ ] **Step 4: tester et commit**

Run: `.venv/bin/python -m pytest tests/test_capture_initial_state_1spe.py -q`

Expected: PASS.

```bash
git add schemas/baseline_1spe.schema.json scripts/capture_initial_state_1spe.py tests/test_capture_initial_state_1spe.py validations/release-1spe/baseline.json validations/release-1spe/baseline.md
git commit -m "[1SPE][BAT] capture l etat initial immuable"
```

### Task 2: Construire le référentiel B.O. 2026 canonique

**Files:**
- Create: `schemas/programme_1spe_2026.schema.json`
- Create: `referentiel/programme_1SPE_2026.json`
- Create: `scripts/extract_official_source.py`
- Create: `scripts/check_programme_1spe_2026.py`
- Create: `tests/test_official_source_extraction.py`
- Create: `tests/test_programme_1spe_2026.py`
- Modify: `referentiel/CONFORMITE_BO2026.md`
- Modify: `sources/registry.yaml`
- Regenerate: `sources/txt/BO2026_1SPE_specialite.txt`
- Create: `validations/release-1spe/revue-programme.md`

- [ ] **Step 1: écrire les tests rouges de provenance et de cardinalité**

```python
def test_every_program_item_is_traceable(programme):
    for item in programme["items"]:
        assert item["bo_page"] >= 1
        assert item["bo_quote"].strip()
        assert item["obligation_class"] in {
            "mandatory_content", "prescribed_teaching",
            "optional_extension", "contextual_guidance",
        }

def test_official_experiments_are_present(programme):
    ids = {item["id"] for item in programme["items"]}
    assert {
        "VA-EXP-SIMULER",
        "VA-EXP-FONCTION-MOYENNE",
        "VA-EXP-DISTANCE-MOYENNE-ESPERANCE",
        "VA-EXP-PROPORTION-2SIGMA",
    } <= ids
    assert all(
        item["obligation_class"] == "mandatory_content"
        for item in programme["items"]
        if item["id"].startswith("VA-EXP-")
    )

def test_expected_cardinalities_are_exact(programme, expected_counts):
    assert counts_by_type_and_class(programme) == expected_counts
```

- [ ] **Step 2: vérifier l'échec ciblé**

Run: `.venv/bin/python -m pytest tests/test_official_source_extraction.py tests/test_programme_1spe_2026.py -q`

Expected: FAIL par absence du schéma, de l'extracteur et du référentiel.

- [ ] **Step 3: écrire et tester l'extracteur de source**

`extract_official_source.py` exécute `pdftotext -layout` sur
`sources/BO2026_1SPE_specialite.pdf`, normalise uniquement les fins de ligne et
écrit atomiquement `sources/txt/BO2026_1SPE_specialite.txt`. Le test compare le
SHA-256 du PDF au registre, vérifie que les quatre lignes d'expérimentation sont
présentes et que deux extractions consécutives sont identiques.

Run: `.venv/bin/python -m pytest tests/test_official_source_extraction.py -q`

Expected: PASS après implémentation de l'extracteur.

- [ ] **Step 4: écrire le schéma fermé**

Le schéma impose `additionalProperties: false`, l'unicité des identifiants, les quatre thèmes, les types `contenu|capacite|demonstration|algorithme|approfondissement|transversal`, les citations, pages, classes d'obligation et affectations de chapitre.

- [ ] **Step 5: figer les cardinalités officielles attendues**

Une fixture versionnée dans `tests/test_programme_1spe_2026.py` donne le nombre
exact d'items par `type × obligation_class`, obtenu par double lecture
indépendante du PDF. Le test compare l'égalité stricte, pas un minimum.

- [ ] **Step 6: transcrire exhaustivement le PDF officiel**

`referentiel/programme_1SPE_2026.json` reprend sans reformulation les contenus, capacités, démonstrations, algorithmes, expérimentations et approfondissements possibles de `sources/BO2026_1SPE_specialite.pdf`. Chaque citation est contrôlée contre `sources/txt/BO2026_1SPE_specialite.txt`.

- [ ] **Step 7: encoder les choix éditoriaux sans les confondre avec le B.O.**

```json
{
  "id": "VA-EXP-PROPORTION-2SIGMA",
  "type": "algorithme",
  "obligation_class": "mandatory_content",
  "assigned_chapters": ["1SPE-VARIABLES-ALEATOIRES"],
  "editorial_verdict": "included"
}
```

- [ ] **Step 8: implémenter le contrôleur**

`check_programme_1spe_2026.py` valide le schéma, les identifiants, la source SHA-256, la présence de chaque citation dans le texte officiel normalisé et l'affectation unique ou explicitement distribuée.

- [ ] **Step 9: mettre à jour la documentation et le registre**

La documentation doit nommer l'arrêté du 26 février 2026, son NOR, sa date d'application et le SHA-256 local du PDF. Le registre ne conserve le PDF 2019 qu'en archive non normative.

- [ ] **Step 10: exécuter les tests**

Run: `.venv/bin/python -m pytest tests/test_official_source_extraction.py tests/test_programme_1spe_2026.py -q`

Expected: PASS, cardinalités exactes et 0 citation orpheline.

- [ ] **Step 11: revue réglementaire indépendante**

Un agent distinct compare chaque entrée au PDF officiel, consigne ses écarts dans `validations/release-1spe/revue-programme.md`, et n'édite pas le référentiel pendant sa revue.

- [ ] **Step 12: commit**

```bash
git add schemas/programme_1spe_2026.schema.json referentiel/programme_1SPE_2026.json scripts/extract_official_source.py scripts/check_programme_1spe_2026.py tests/test_official_source_extraction.py tests/test_programme_1spe_2026.py referentiel/CONFORMITE_BO2026.md sources/registry.yaml sources/txt/BO2026_1SPE_specialite.txt validations/release-1spe/revue-programme.md
git commit -m "[1SPE][BAT] canonise le programme officiel 2026"
```

### Task 3: Enrichir la baseline initiale par les builds historiques

**Files:**
- Modify: `schemas/baseline_1spe.schema.json`
- Create: `scripts/inventory_1spe.py`
- Create: `scripts/run_baseline_build.py`
- Create: `tests/test_inventory_1spe.py`
- Modify: `validations/release-1spe/baseline.json`
- Modify: `validations/release-1spe/baseline.md`
- Create: `validations/release-1spe/baseline-build-eleve.json`
- Create: `validations/release-1spe/baseline-build-professeur.json`

- [ ] **Step 1: écrire les tests rouges d'inventaire**

```python
def test_inventory_matches_independent_filesystem_count(tmp_path):
    tree = make_fixture_tree(tmp_path)
    report = inventory(tree)
    expected = len(list((tree / "1SPE-TEST" / "exercices").glob("*-EX-*.tex")))
    assert report["chapters"]["1SPE-TEST"]["exercise_count"] == expected

def test_stale_validation_is_not_current(report):
    assert all(
        proof["current"]
        == (proof["object_sha256"] == proof["current_object_sha256"])
        for proof in report["proofs"]
    )

def test_fifty_exercise_gate_is_explicit(report):
    assert report["chapters"]["1SPE-TEST"]["exercise_gate"] in {
        "certified", "needs_fix"
    }
```

- [ ] **Step 2: vérifier l'échec ciblé**

Run: `.venv/bin/python -m pytest tests/test_inventory_1spe.py -q`

Expected: FAIL car l'inventaire structuré n'existe pas.

- [ ] **Step 3: inventorier chaque objet**

Le script recense cours, méthodes, exercices, aides, corrigés, QCM TeX et JSON,
évaluations, barèmes, remédiations, transversaux, figures, polices, validations,
identifiants canoniques, empreintes, dépendances, folios courants et diagnostics
LaTeX. Il calcule les nombres depuis l'arbre source, sans constante historique.

- [ ] **Step 4: classifier l'état initial**

Chaque objet reçoit `keep`, `fix`, `replace`, `remove_from_release` ou
`review_required`, avec raisons contrôlables : hors programme, preuve périmée,
corrigé absent, doublon, métadonnée invalide ou compilation en échec.

- [ ] **Step 5: construire les deux assemblages historiques**

Run: `.venv/bin/python scripts/run_baseline_build.py --variant eleve --report validations/release-1spe/baseline-build-eleve.json`

Expected: code 0 si le build historique réussit, code 2 s'il échoue ; dans les
deux cas le rapport est écrit avec nombre de pages, erreurs, avertissements,
références, débordements et commande exacte.

Run: `.venv/bin/python scripts/run_baseline_build.py --variant professeur --report validations/release-1spe/baseline-build-professeur.json`

Expected: même contrat dans
`validations/release-1spe/baseline-build-professeur.json`.

- [ ] **Step 6: générer JSON et synthèse**

Run: `.venv/bin/python scripts/inventory_1spe.py --json validations/release-1spe/baseline.json --markdown validations/release-1spe/baseline.md`

Expected: code 0 ; 10 chapitres, tous les objets listés, pagination historique,
diagnostics des deux builds, compte réel des exercices, verdict du seuil 50 et
zéro fichier 1SPE non classé.

- [ ] **Step 7: contrôler le schéma**

Run: `.venv/bin/python -m pytest tests/test_inventory_1spe.py -q`

Expected: PASS.

- [ ] **Step 8: revue contradictoire de baseline**

Un agent de revue vérifie les comptes, les statuts et dix échantillons par
famille ; ses constats sont ajoutés à
`validations/release-1spe/baseline.md`.

- [ ] **Step 9: commit**

```bash
git add schemas/baseline_1spe.schema.json scripts/inventory_1spe.py scripts/run_baseline_build.py tests/test_inventory_1spe.py validations/release-1spe/baseline.json validations/release-1spe/baseline.md validations/release-1spe/baseline-build-eleve.json validations/release-1spe/baseline-build-professeur.json
git commit -m "[1SPE][BAT] fige la baseline exhaustive"
```

### Task 4A: Versionner le schéma des contrats 1SPE

**Files:**
- Create: `schemas/contrat_chapitre_1spe_2026.schema.json`
- Create: `tests/test_contrat_schema_1spe_2026.py`

- [ ] **Step 1: écrire le test rouge du schéma fermé**

```python
def test_contract_schema_requires_official_lineage(schema):
    capacity = schema["$defs"]["capacity"]
    assert {
        "ref_capacite", "obligation_class",
        "proof_object_ids", "transversal_ids",
    } <= set(capacity["required"])
    assert schema["additionalProperties"] is False
```

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_contrat_schema_1spe_2026.py -q`

Expected: FAIL car le schéma versionné n'existe pas.

- [ ] **Step 3: créer le schéma sans modifier le schéma partagé**

Le schéma propre à 1SPE 2026 impose la filiation au référentiel canonique et les
emplacements de preuves ; `schemas/contrat_chapitre.schema.json` reste inchangé
pour ne pas affecter TSPE.

- [ ] **Step 4: exécuter le test et commit**

Run: `.venv/bin/python -m pytest tests/test_contrat_schema_1spe_2026.py -q`

Expected: PASS.

```bash
git add schemas/contrat_chapitre_1spe_2026.schema.json tests/test_contrat_schema_1spe_2026.py
git commit -m "[1SPE][BAT] versionne le contrat de chapitre"
```

### Task 4B: Migrer les contrats Algèbre et Analyse

**Files:**
- Modify: `referentiel/capacites_1SPE_SUITES.json`
- Modify: `referentiel/capacites_1SPE_SECOND_DEGRE.json`
- Modify: `referentiel/capacites_1SPE_DERIVATION_LOCAL.json`
- Modify: `referentiel/capacites_1SPE_DERIVATION_GLOBAL.json`
- Modify: `referentiel/capacites_1SPE_EXPONENTIELLE.json`
- Modify: `referentiel/capacites_1SPE_TRIGONOMETRIE.json`
- Modify: `chapitres/1SPE-SUITES/contrat.yaml`
- Modify: `chapitres/1SPE-SECOND-DEGRE/contrat.yaml`
- Modify: `chapitres/1SPE-DERIVATION-LOCAL/contrat.yaml`
- Modify: `chapitres/1SPE-DERIVATION-GLOBAL/contrat.yaml`
- Modify: `chapitres/1SPE-EXPONENTIELLE/contrat.yaml`
- Modify: `chapitres/1SPE-TRIGONOMETRIE/contrat.yaml`
- Create: `tests/test_contrats_1spe_algebre_analyse.py`

- [ ] **Step 1: écrire les tests rouges de filiation**

```python
def test_analysis_contract_refs_are_official(analysis_contracts, programme):
    official_ids = {item["id"] for item in programme["items"]}
    assert not {
        cap["ref_capacite"]
        for contract in analysis_contracts
        for cap in contract["capacites"]
        if cap["ref_capacite"] not in official_ids
    }

def test_all_six_contracts_match_release_schema(analysis_contracts, schema):
    for contract in analysis_contracts:
        jsonschema.validate(contract, schema)

def test_trigonometry_contract_has_no_removed_content(trigo_contract):
    labels = " ".join(c["libelle_eleve"] for c in trigo_contract["capacites"])
    assert "formules d'addition" not in labels.lower()
    assert "équations trigonométriques" not in labels.lower()
```

- [ ] **Step 2: vérifier l'échec ciblé**

Run: `.venv/bin/python -m pytest tests/test_contrats_1spe_algebre_analyse.py -q`

Expected: FAIL sur les références BO2019 et la trigonométrie.

- [ ] **Step 3: migrer les six paires référentiel/contrat**

Les libellés B.O. restent exacts, les libellés élève sont séparés et chaque item
reçoit ses objets de preuve prévus. Le chapitre 6 ne couvre obligatoirement que
l'enroulement sur le cercle et sinus/cosinus d'un réel.

- [ ] **Step 4: vérifier les six contrats**

Run: `.venv/bin/python -m pytest tests/test_contrats_1spe_algebre_analyse.py -q`

Expected: PASS pour les six chapitres.

- [ ] **Step 5: commit**

```bash
git add referentiel/capacites_1SPE_SUITES.json referentiel/capacites_1SPE_SECOND_DEGRE.json referentiel/capacites_1SPE_DERIVATION_LOCAL.json referentiel/capacites_1SPE_DERIVATION_GLOBAL.json referentiel/capacites_1SPE_EXPONENTIELLE.json referentiel/capacites_1SPE_TRIGONOMETRIE.json chapitres/1SPE-SUITES/contrat.yaml chapitres/1SPE-SECOND-DEGRE/contrat.yaml chapitres/1SPE-DERIVATION-LOCAL/contrat.yaml chapitres/1SPE-DERIVATION-GLOBAL/contrat.yaml chapitres/1SPE-EXPONENTIELLE/contrat.yaml chapitres/1SPE-TRIGONOMETRIE/contrat.yaml tests/test_contrats_1spe_algebre_analyse.py
git commit -m "[1SPE][BAT] migre les contrats algebre analyse"
```

### Task 4C: Migrer les contrats Géométrie et Probabilités

**Files:**
- Modify: `referentiel/capacites_1SPE_PRODUIT_SCALAIRE.json`
- Modify: `referentiel/capacites_1SPE_GEOMETRIE_REPEREE.json`
- Modify: `referentiel/capacites_1SPE_PROBA_COND.json`
- Modify: `referentiel/capacites_1SPE_VARIABLES_ALEATOIRES.json`
- Modify: `chapitres/1SPE-PRODUIT-SCALAIRE/contrat.yaml`
- Modify: `chapitres/1SPE-GEOMETRIE-REPEREE/contrat.yaml`
- Modify: `chapitres/1SPE-PROBA-COND/contrat.yaml`
- Modify: `chapitres/1SPE-VARIABLES-ALEATOIRES/contrat.yaml`
- Create: `tests/test_contrats_1spe_geometrie_probabilites.py`

- [ ] **Step 1: écrire puis vérifier les tests rouges**

Les tests valident chacun des quatre contrats contre
`schemas/contrat_chapitre_1spe_2026.schema.json`, vérifient chaque
`ref_capacite`, exigent toutes les affectations officielles du groupe et
interdisent les références orphelines.

Run: `.venv/bin/python -m pytest tests/test_contrats_1spe_geometrie_probabilites.py -q`

Expected: FAIL sur les références BO2019, la loi binomiale et les quatre
expérimentations manquantes.

- [ ] **Step 2: migrer les quatre paires référentiel/contrat**

Le chapitre 10 couvre séparément les quatre expérimentations `VA-EXP-*`. La loi
binomiale et ses paramètres ne sont pas des capacités obligatoires de première.

- [ ] **Step 3: exécuter le test et commit**

Run: `.venv/bin/python -m pytest tests/test_contrats_1spe_geometrie_probabilites.py -q`

Expected: PASS pour les quatre chapitres.

```bash
git add referentiel/capacites_1SPE_PRODUIT_SCALAIRE.json referentiel/capacites_1SPE_GEOMETRIE_REPEREE.json referentiel/capacites_1SPE_PROBA_COND.json referentiel/capacites_1SPE_VARIABLES_ALEATOIRES.json chapitres/1SPE-PRODUIT-SCALAIRE/contrat.yaml chapitres/1SPE-GEOMETRIE-REPEREE/contrat.yaml chapitres/1SPE-PROBA-COND/contrat.yaml chapitres/1SPE-VARIABLES-ALEATOIRES/contrat.yaml tests/test_contrats_1spe_geometrie_probabilites.py
git commit -m "[1SPE][BAT] migre les contrats geometrie probabilites"
```

### Task 4D: Prouver l'affectation exhaustive des items officiels

**Files:**
- Create: `scripts/check_contract_coverage.py`
- Create: `tests/test_contract_coverage.py`
- Create: `tests/test_all_contracts_1spe_2026.py`
- Create: `validations/release-1spe/contract-coverage.json`

- [ ] **Step 1: écrire les tests rouges de couverture exacte**

```python
def test_every_required_item_is_assigned_once_or_declared_distributed(matrix):
    assert matrix.unassigned_required == []
    assert matrix.unjustified_multiple_assignments == []

def test_every_transversal_has_introduction_reinvestment_and_reference(matrix):
    assert matrix.incomplete_transversals == []

def test_all_ten_contracts_match_schema(contracts, release_schema):
    assert len(contracts) == 10
    for contract in contracts:
        jsonschema.validate(contract, release_schema)
```

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_contract_coverage.py tests/test_all_contracts_1spe_2026.py -q`

Expected: FAIL tant que le contrôleur et la matrice n'existent pas.

- [ ] **Step 3: implémenter et exécuter le contrôleur**

Run: `.venv/bin/python scripts/check_contract_coverage.py --programme referentiel/programme_1SPE_2026.json --output validations/release-1spe/contract-coverage.json`

Expected: code 0, 100 % des items `mandatory_content|prescribed_teaching`
affectés, aucun doublon injustifié et tous les transversaux structurés.

- [ ] **Step 4: exécuter le test et commit**

Run: `.venv/bin/python -m pytest tests/test_contract_coverage.py tests/test_all_contracts_1spe_2026.py -q`

Expected: PASS.

```bash
git add scripts/check_contract_coverage.py tests/test_contract_coverage.py tests/test_all_contracts_1spe_2026.py validations/release-1spe/contract-coverage.json
git commit -m "[1SPE][BAT] prouve la couverture des contrats"
```

### Task 5: Rendre les preuves et statuts 1SPE infalsifiables

**Files:**
- Create: `schemas/release_validation_1spe.schema.json`
- Create: `schemas/release_manifest.schema.json`
- Create: `release/object_types_1spe.yaml`
- Create: `scripts/validate_release_proofs.py`
- Create: `tests/test_release_proofs.py`
- Create: `tests/test_gate_policy_coverage.py`
- Create: `release/1spe-2026.yaml`

- [ ] **Step 1: écrire les tests rouges des états**

```python
def test_only_three_object_states_are_allowed(schema):
    assert schema["properties"]["status"]["enum"] == [
        "certified", "needs_fix", "blocked"
    ]

def test_stale_hash_can_never_certify(proof, current_hashes):
    proof["object_sha256"] = "0" * 64
    assert validate_proof(proof, current_hashes).status == "needs_fix"
```

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_release_proofs.py -q`

Expected: FAIL car le schéma versionné 1SPE n'existe pas.

- [ ] **Step 3: créer le contrat de preuve versionné**

Chaque preuve contient `object_id`, `object_type`, empreintes de l'objet et des dépendances, `gate_id`, `gate_version`, `programme_sha256`, `command`, `actor`, `created_at`, `status`, `findings`, `evidence_paths`.

- [ ] **Step 4: définir les gates par type**

```yaml
release_id: 1SPE-RC0
programme: referentiel/programme_1SPE_2026.json
variants: [eleve, professeur]
gate_policy:
  exercise: [programme, metadata, mathematics, pedagogy, language, similarity]
  course: [programme, metadata, mathematics, pedagogy, language, similarity]
  method: [programme, metadata, mathematics, pedagogy, language, similarity]
  activity: [programme, metadata, mathematics, pedagogy, language, similarity]
  diagnostic: [programme, metadata, mathematics, pedagogy, language, similarity]
  aid: [metadata, mathematics, pedagogy, language, similarity]
  solution: [metadata, mathematics, language, similarity, statement_consistency]
  qcm: [programme, metadata, mathematics, pedagogy, language, similarity]
  assessment: [programme, metadata, mathematics, pedagogy, language, similarity]
  grading_scale: [metadata, mathematics, assessment_consistency, language]
  remediation: [programme, metadata, mathematics, pedagogy, language, similarity]
  td: [programme, metadata, mathematics, pedagogy, language, similarity]
  figure: [metadata, mathematics, language, visual, rights]
  transversal: [programme, metadata, mathematics, pedagogy, language, similarity]
  chapter_opening: [programme, metadata, pedagogy, language, visual, rights]
  front_matter: [metadata, language, visual, rights]
  appendix: [programme, metadata, mathematics, pedagogy, language, similarity]
  index: [metadata, language, folios]
  legal_page: [metadata, language, publication]
  cover: [metadata, language, visual, rights, publication]
  chapter: [programme, compilation, cardinality, transversals]
  assembly: [compilation, folios, visual]
  screen_pdf: [integrity, accessibility]
  print_master: [integrity, prepress]
  release: [programme, metadata, mathematics, pedagogy, language,
            similarity, compilation, folios, visual, accessibility, prepress]
```

- [ ] **Step 5: implémenter l'agrégation hiérarchique**

Le script applique la politique du type d'objet, puis agrège objets → chapitres
→ assemblages → release. Il refuse `certified` si une preuve applicable manque,
si une empreinte diffère, si le programme diffère, si une dépendance est
modifiée ou si un statut numérique vaut `needs_fix|blocked`. Tout `object_type`
absent de `gate_policy` est rejeté, jamais ignoré.

`release/object_types_1spe.yaml` énumère les types canoniques ci-dessus et leur
correspondance avec chaque ancien `type_objet`. Le test paramétré compare cette
énumération aux types réellement produits par la baseline et exige au minimum
`metadata`, ainsi que `mathematics`, `language`, `similarity|rights` pour chaque
objet de contenu auquel ces gates s'appliquent.

- [ ] **Step 6: exécuter les tests**

Run: `.venv/bin/python -m pytest tests/test_release_proofs.py tests/test_gate_policy_coverage.py -q`

Expected: PASS.

- [ ] **Step 7: commit**

```bash
git add schemas/release_validation_1spe.schema.json schemas/release_manifest.schema.json release/object_types_1spe.yaml scripts/validate_release_proofs.py tests/test_release_proofs.py tests/test_gate_policy_coverage.py release/1spe-2026.yaml
git commit -m "[1SPE][BAT] verrouille les preuves de certification"
```

## Chunk 2: Reconstruction mathématique, pédagogique et éditoriale

### Task 6: Auditer automatiquement les métadonnées et les strates de contenu

**Files:**
- Create: `schemas/object_meta_1spe.schema.json`
- Create: `scripts/content_audit/__init__.py`
- Create: `scripts/content_audit/models.py`
- Create: `scripts/content_audit/metadata.py`
- Create: `scripts/content_audit/notation.py`
- Create: `scripts/content_audit/chapter.py`
- Create: `scripts/audit_content_1spe.py`
- Create: `tests/test_audit_content_1spe.py`
- Create: `chapitres/1SPE-SUITES/objects.yaml`
- Create: `chapitres/1SPE-SECOND-DEGRE/objects.yaml`
- Create: `chapitres/1SPE-DERIVATION-LOCAL/objects.yaml`
- Create: `chapitres/1SPE-DERIVATION-GLOBAL/objects.yaml`
- Create: `chapitres/1SPE-EXPONENTIELLE/objects.yaml`
- Create: `chapitres/1SPE-TRIGONOMETRIE/objects.yaml`
- Create: `chapitres/1SPE-PRODUIT-SCALAIRE/objects.yaml`
- Create: `chapitres/1SPE-GEOMETRIE-REPEREE/objects.yaml`
- Create: `chapitres/1SPE-PROBA-COND/objects.yaml`
- Create: `chapitres/1SPE-VARIABLES-ALEATOIRES/objects.yaml`
- Modify: `scripts/check_latex.py`
- Modify: `docs/05_conventions_latex.md`
- Create: `validations/release-1spe/content-audit.json`
- Create: `validations/release-1spe/content-audit.md`

- [ ] **Step 1: écrire les tests rouges**

```python
def test_visible_object_has_unique_id(audit):
    assert audit["duplicate_ids"] == []
    assert audit["missing_ids"] == []

def test_sequence_notation_is_contextual():
    from content_audit.notation import notation_ok
    assert notation_ok(r"\texttt{u(n)}", context="python")
    assert notation_ok(r"$u_n$", context="mathematics")
    assert not notation_ok(r"$u(n)$", context="mathematics")
```

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_audit_content_1spe.py -q`

Expected: FAIL, puis lister les doublons, objets sans identifiant et notations non conformes.

- [ ] **Step 3: définir les métadonnées minimales**

Les dix fichiers `objects.yaml` sont les sidecars canoniques. Chaque objet
visible déclare son chemin exact, identifiant, chapitre, strate, capacité
officielle, parcours, compétences, difficulté, dépendances, visibilité
`eleve|professeur|both`, date de création, source d'inspiration, titulaire des
droits, licence, `creator_actor_id`, `last_editor_actor_id` et empreinte.
`content_audit.metadata` est l'unique API de lecture/validation ; le schéma
refuse un acteur vide et le validateur de preuves interdit l'auto-revue.

- [ ] **Step 4: implémenter l'audit de structure**

Le script contrôle les neuf temps de chapitre, au moins 50 exercices hors aides, les trois parcours, le QCM, les évaluations A/B, les corrigés, barèmes et remédiations.

- [ ] **Step 5: renforcer le linter LaTeX**

Ajouter les contrôles de notations, accents, identifiants techniques visibles, marqueurs provisoires, références saisies en dur et contenus officiellement retirés dans une strate obligatoire.

- [ ] **Step 6: générer le rapport initial**

Run: `.venv/bin/python scripts/audit_content_1spe.py --release release/1spe-2026.yaml`

Expected: code 2 et statut déterministe `needs_fix` si la baseline contient des
écarts ; code 0 seulement si tous les contrôles sont `certified`. Dans les deux
cas, zéro objet non classé et un JSON conforme au schéma.

- [ ] **Step 7: mettre à jour la convention `u(n)` / `u_n`**

La règle écrite et le test doivent accepter la notation fonctionnelle dans le code Python et préférer `u_n` dans le discours mathématique.

- [ ] **Step 8: exécuter les tests**

Run: `.venv/bin/python -m pytest tests/test_audit_content_1spe.py tests/test_check_latex.py -q`

Expected: PASS.

- [ ] **Step 9: commit**

```bash
git add schemas/object_meta_1spe.schema.json scripts/content_audit scripts/audit_content_1spe.py tests/test_audit_content_1spe.py chapitres/1SPE-SUITES/objects.yaml chapitres/1SPE-SECOND-DEGRE/objects.yaml chapitres/1SPE-DERIVATION-LOCAL/objects.yaml chapitres/1SPE-DERIVATION-GLOBAL/objects.yaml chapitres/1SPE-EXPONENTIELLE/objects.yaml chapitres/1SPE-TRIGONOMETRIE/objects.yaml chapitres/1SPE-PRODUIT-SCALAIRE/objects.yaml chapitres/1SPE-GEOMETRIE-REPEREE/objects.yaml chapitres/1SPE-PROBA-COND/objects.yaml chapitres/1SPE-VARIABLES-ALEATOIRES/objects.yaml scripts/check_latex.py docs/05_conventions_latex.md validations/release-1spe/content-audit.json validations/release-1spe/content-audit.md
git commit -m "[1SPE][BAT] automatise l'audit editorial"
```

### Task 7A: Outiller les migrations et revues de chapitre

**Files:**
- Create: `schemas/chapter_migration.schema.json`
- Create: `schemas/review_bundle_1spe.schema.json`
- Create: `scripts/check_chapter_migration.py`
- Create: `scripts/check_chapter_release.py`
- Modify: `scripts/validate_release_proofs.py`
- Create: `tests/test_chapter_migration.py`
- Create: `tests/test_chapter_release.py`
- Create: `publication/migrations/1spe-suites.yaml`
- Create: `publication/migrations/1spe-second-degre.yaml`
- Create: `publication/migrations/1spe-trigonometrie.yaml`

- [ ] **Step 1: écrire le test rouge du manifeste**

Le premier test impose une liste exhaustive de chemins existants ou à créer, une action
`keep|modify|create|remove_from_release`, la raison, l'identifiant canonique et
les preuves invalidées. Les chemins génériques et globs sont interdits. Le
second test exige couverture officielle, ≥50 exercices, cardinalité
`1+1+2+2+2+1+1` par capacité, triplets, six compétences, trois parcours et
preuves courantes applicables à chaque objet.

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_chapter_migration.py tests/test_chapter_release.py -q`

Expected: FAIL car les manifestes, schémas et contrôleurs n'existent pas.

- [ ] **Step 3: générer puis relire les trois manifestes depuis la baseline**

Chaque manifeste énumère exactement les `.tex`, QCM `.json`, sidecars et
validations touchés. L'agent de chapitre n'édite aucun chemin absent de son
manifeste. `review_bundle_1spe` contient un enregistrement conforme à
`release_validation_1spe` pour chaque `object_id × gate_id` applicable.
`check_chapter_release.py` refuse une preuve manquante, périmée ou signée par le
`creator_actor_id` ou `last_editor_actor_id` de l'objet.
Les tests CLI couvrent `check_chapter_release.py CHAPTER`, `--all`,
`validate_release_proofs.py --scope CHAPTER|all-content` et
`check_chapter_migration.py --paths0`; ce dernier doit émettre des chemins
terminés par NUL et aucun autre texte sur stdout.

- [ ] **Step 4: exécuter le contrôleur et commit**

Run: `.venv/bin/python scripts/check_chapter_migration.py publication/migrations/1spe-suites.yaml publication/migrations/1spe-second-degre.yaml publication/migrations/1spe-trigonometrie.yaml && .venv/bin/python -m pytest tests/test_chapter_migration.py tests/test_chapter_release.py -q`

Expected: code 0, zéro glob, zéro objet de baseline oublié.

```bash
git add schemas/chapter_migration.schema.json schemas/review_bundle_1spe.schema.json scripts/check_chapter_migration.py scripts/check_chapter_release.py scripts/validate_release_proofs.py tests/test_chapter_migration.py tests/test_chapter_release.py publication/migrations/1spe-suites.yaml publication/migrations/1spe-second-degre.yaml publication/migrations/1spe-trigonometrie.yaml
git commit -m "[1SPE][BAT] outille les migrations de chapitre"
```

### Task 7B: Reconstruire Suites

**Files:**
- Modify/Create/Remove from release: exact paths in `publication/migrations/1spe-suites.yaml`
- Create: `tests/test_chapter_suites_2026.py`
- Create: `validations/release-1spe/reviews/suites-mathematics.json`
- Create: `validations/release-1spe/reviews/suites-pedagogy.json`
- Create: `validations/release-1spe/reviews/suites-language.json`
- Create: `validations/release-1spe/reviews/suites-adversarial.json`

- [ ] **Step 1: écrire et observer les tests rouges**

Les tests importent `content_audit.chapter.audit_chapter` et exigent au moins
50 exercices admissibles après migration. Pour chaque capacité :
`1 cours + 1 méthode + 2 exercices parcours 1 + 2 parcours 2 + 2 parcours 3 +
1 item QCM + 1 remédiation`.

Run: `.venv/bin/python -m pytest tests/test_chapter_suites_2026.py -q`

Expected: FAIL avec la liste exacte des objets manquants.

- [ ] **Step 2: appliquer le manifeste**

Conserver, corriger, remplacer ou créer uniquement les chemins énumérés, avec
aide, corrigé et métadonnée pour chaque exercice retenu.

- [ ] **Step 3: résoudre et relire indépendamment**

Quatre agents distincts produisent des bundles conformes à
`schemas/review_bundle_1spe.schema.json`, contenant une preuve par objet et gate
applicable ; aucun `actor` ne peut égaler `creator_actor_id` ou
`last_editor_actor_id`.

- [ ] **Step 4: vérifier le chapitre**

Run: `.venv/bin/python -m pytest tests/test_chapter_suites_2026.py -q && make verify CHAP=1SPE-SUITES && make similarity CHAP=1SPE-SUITES && make chapter CHAP=1SPE-SUITES && .venv/bin/python scripts/check_chapter_release.py 1SPE-SUITES && .venv/bin/python scripts/validate_release_proofs.py --scope 1SPE-SUITES`

Expected: code 0, ≥50 exercices admissibles, 0 erreur mathématique, similarité,
référence ou débordement.

- [ ] **Step 5: commit**

```bash
.venv/bin/python scripts/check_chapter_migration.py publication/migrations/1spe-suites.yaml --paths0 | git add --pathspec-from-file=- --pathspec-file-nul
git add publication/migrations/1spe-suites.yaml tests/test_chapter_suites_2026.py validations/release-1spe/reviews/suites-mathematics.json validations/release-1spe/reviews/suites-pedagogy.json validations/release-1spe/reviews/suites-language.json validations/release-1spe/reviews/suites-adversarial.json
git commit -m "[1SPE][BAT] reconstruit le chapitre suites"
```

### Task 7C: Reconstruire Second degré

**Files:**
- Modify/Create/Remove from release: exact paths in `publication/migrations/1spe-second-degre.yaml`
- Create: `tests/test_chapter_second_degre_2026.py`
- Create: `validations/release-1spe/reviews/second-degre-mathematics.json`
- Create: `validations/release-1spe/reviews/second-degre-pedagogy.json`
- Create: `validations/release-1spe/reviews/second-degre-language.json`
- Create: `validations/release-1spe/reviews/second-degre-adversarial.json`

- [ ] **Step 1: écrire et observer les tests rouges**

Exiger ≥50 exercices admissibles et, pour chaque capacité, la cardinalité
`1+1+2+2+2+1+1` définie en Task 7B.

Run: `.venv/bin/python -m pytest tests/test_chapter_second_degre_2026.py -q`

Expected: FAIL avec la liste exacte des objets manquants.

- [ ] **Step 2: appliquer le manifeste et reconstruire les triplets**

Chaque énoncé retenu possède aide, corrigé, métadonnée et, s'il est évaluatif,
barème cohérent.

- [ ] **Step 3: obtenir quatre bundles indépendants structurés**

Chaque fichier mathématiques, pédagogie, langue ou adversarial est conforme à
`schemas/review_bundle_1spe.schema.json` et contient les enregistrements
`object_id × gate_id` dont il est responsable. Les quatre acteurs diffèrent de
l'auteur de la correction.

- [ ] **Step 4: vérifier et commit**

Run: `.venv/bin/python -m pytest tests/test_chapter_second_degre_2026.py -q && make verify CHAP=1SPE-SECOND-DEGRE && make similarity CHAP=1SPE-SECOND-DEGRE && make chapter CHAP=1SPE-SECOND-DEGRE && .venv/bin/python scripts/check_chapter_release.py 1SPE-SECOND-DEGRE && .venv/bin/python scripts/validate_release_proofs.py --scope 1SPE-SECOND-DEGRE`

Expected: code 0 et tous les gates du chapitre `certified`.

```bash
.venv/bin/python scripts/check_chapter_migration.py publication/migrations/1spe-second-degre.yaml --paths0 | git add --pathspec-from-file=- --pathspec-file-nul
git add publication/migrations/1spe-second-degre.yaml tests/test_chapter_second_degre_2026.py validations/release-1spe/reviews/second-degre-mathematics.json validations/release-1spe/reviews/second-degre-pedagogy.json validations/release-1spe/reviews/second-degre-language.json validations/release-1spe/reviews/second-degre-adversarial.json
git commit -m "[1SPE][BAT] reconstruit le chapitre second degre"
```

### Task 7D: Reconstruire Trigonométrie

**Files:**
- Modify/Create/Remove from release: exact paths in `publication/migrations/1spe-trigonometrie.yaml`
- Create: `tests/test_chapter_trigonometrie_2026.py`
- Create: `validations/release-1spe/reviews/trigonometrie-mathematics.json`
- Create: `validations/release-1spe/reviews/trigonometrie-pedagogy.json`
- Create: `validations/release-1spe/reviews/trigonometrie-language.json`
- Create: `validations/release-1spe/reviews/trigonometrie-adversarial.json`

- [ ] **Step 1: écrire et observer les tests rouges**

Exiger ≥50 exercices admissibles, la cardinalité `1+1+2+2+2+1+1` par capacité
et zéro formule d'addition, équation trigonométrique générale ou fonction
trigonométrique dans la strate obligatoire.

Run: `.venv/bin/python -m pytest tests/test_chapter_trigonometrie_2026.py -q`

Expected: FAIL avec les manques et reliquats hors périmètre exacts.

- [ ] **Step 2: appliquer le manifeste sans duplication artificielle**

Varier cercle, mesure en radians, images, antécédents, repérage, preuve,
algorithmique et géométrie tout en restant dans les deux capacités officielles.

- [ ] **Step 3: obtenir quatre bundles indépendants structurés**

Les quatre JSON de revue suivent `schemas/review_bundle_1spe.schema.json`,
contiennent les enregistrements `object_id × gate_id` applicables, les empreintes
courantes et la séparation auteur/relecteur.

- [ ] **Step 4: vérifier et commit**

Run: `.venv/bin/python -m pytest tests/test_chapter_trigonometrie_2026.py -q && make verify CHAP=1SPE-TRIGONOMETRIE && make similarity CHAP=1SPE-TRIGONOMETRIE && make chapter CHAP=1SPE-TRIGONOMETRIE && .venv/bin/python scripts/check_chapter_release.py 1SPE-TRIGONOMETRIE && .venv/bin/python scripts/validate_release_proofs.py --scope 1SPE-TRIGONOMETRIE`

Expected: code 0 et tous les gates du chapitre `certified`.

```bash
.venv/bin/python scripts/check_chapter_migration.py publication/migrations/1spe-trigonometrie.yaml --paths0 | git add --pathspec-from-file=- --pathspec-file-nul
git add publication/migrations/1spe-trigonometrie.yaml tests/test_chapter_trigonometrie_2026.py validations/release-1spe/reviews/trigonometrie-mathematics.json validations/release-1spe/reviews/trigonometrie-pedagogy.json validations/release-1spe/reviews/trigonometrie-language.json validations/release-1spe/reviews/trigonometrie-adversarial.json
git commit -m "[1SPE][BAT] reconstruit le chapitre trigonometrie"
```

### Task 8: Reconstruire Variables aléatoires et ses expérimentations

**Files:**
- Create: `publication/migrations/1spe-variables-aleatoires.yaml`
- Modify/Create/Remove from release: exact paths in `publication/migrations/1spe-variables-aleatoires.yaml`
- Create: `chapitres/1SPE-VARIABLES-ALEATOIRES/cours/15_experimentations.tex`
- Modify: `chapitres/1SPE-VARIABLES-ALEATOIRES/methodes/1SPE-VARALEA-ME-004.tex`
- Modify: `chapitres/1SPE-VARIABLES-ALEATOIRES/qcm/1SPE-VARALEA-QCM.json`
- Create: `scripts/extract_python_blocks.py`
- Create: `tests/test_variables_aleatoires_2026.py`
- Create: `validations/release-1spe/reviews/variables-aleatoires.md`
- Create: `validations/release-1spe/reviews/variables-aleatoires-mathematics.json`
- Create: `validations/release-1spe/reviews/variables-aleatoires-pedagogy.json`
- Create: `validations/release-1spe/reviews/variables-aleatoires-language.json`
- Create: `validations/release-1spe/reviews/variables-aleatoires-adversarial.json`

- [ ] **Step 1: écrire les tests rouges du nouveau périmètre**

```python
def test_binomial_law_is_not_mandatory_content():
    from content_audit.chapter import mandatory_hits
    assert mandatory_hits("1SPE-VARIABLES-ALEATOIRES", [
        r"\\mathcal\\{B\\}", r"E\\(X\\)\\s*=\\s*np", r"np\\(1-p\\)"
    ]) == []

def test_all_four_mandatory_experiments_have_objects(programme, object_index):
    ids = {
        "VA-EXP-SIMULER", "VA-EXP-FONCTION-MOYENNE",
        "VA-EXP-DISTANCE-MOYENNE-ESPERANCE",
        "VA-EXP-PROPORTION-2SIGMA",
    }
    assert all(object_index.coverage(item_id) for item_id in ids)

def test_each_capacity_has_required_strata(chapter_audit):
    for capacity in chapter_audit.capacities:
        minima = {
            "course": 1, "method": 1,
            "exercise_p1": 2, "exercise_p2": 2, "exercise_p3": 2,
            "qcm_item": 1, "remediation": 1,
        }
        assert all(capacity.counts[key] >= minimum
                   for key, minimum in minima.items())
```

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_variables_aleatoires_2026.py -q`

Expected: FAIL sur les cours, méthodes, exercices 2026 et anciennes évaluations binomiales.

- [ ] **Step 3: établir le tableau de migration**

Générer `publication/migrations/1spe-variables-aleatoires.yaml` depuis la
baseline, puis classer chaque chemin exact : conserver s'il traite loi finie,
espérance, variance ou écart-type dans le périmètre ; réécrire s'il repose sur
Bernoulli/binomiale ; exclure de la release s'il ne peut être adapté sans
dénaturer l'objectif.

Run: `.venv/bin/python scripts/check_chapter_migration.py publication/migrations/1spe-variables-aleatoires.yaml`

Expected: code 0, zéro glob et zéro objet de baseline oublié avant modification.

- [ ] **Step 4: reconstruire cours et méthodes**

La progression couvre variable aléatoire finie, loi, espérance, variance, écart-type, échantillons de variables identiquement distribuées, moyenne d'échantillon et interprétation expérimentale.

- [ ] **Step 5: intégrer les quatre expérimentations**

Le module contient quatre objets distincts : simulation d'une variable ; lecture
et écriture d'une fonction de moyenne ; étude de la distance moyenne/espérance ;
simulation de `N` échantillons et proportion vérifiant
`|m-μ| ≤ 2σ/√n`.

- [ ] **Step 6: tester le code Python publié**

`extract_python_blocks.py` extrait les environnements `pythoncode` identifiés.
Les tests exécutent les graines `[1729, 2026, 314159]`, avec `n=100`,
`N=1000`, une variable de référence fixée par fixture et une tolérance
déterministe de `1e-12` pour les résultats calculés. Les proportions simulées
sont comparées à la même séquence pseudo-aléatoire consommée par une
implémentation indépendante.

- [ ] **Step 7: reconstruire les exercices, QCM et évaluations**

Conserver au moins 50 exercices hors aides, sans loi binomiale obligatoire. Chaque énoncé, aide, corrigé et barème doit partager le même domaine, les mêmes données et la même convention d'arrondi.

- [ ] **Step 8: résolution indépendante et contrôle statistique**

Un agent résout tous les objets reconstruits. Les trois graines fixées sont
rejouées ; les affirmations probabilistes sont distinguées des constats
empiriques.

- [ ] **Step 9: produire les quatre bundles de revue**

Quatre agents distincts de l'auteur produisent les bundles mathématique,
pédagogique, linguistique et adversarial conformes à
`schemas/review_bundle_1spe.schema.json`. Chaque bundle contient une preuve par
`object_id × gate_id` dont il est responsable ; le Markdown n'est qu'une
synthèse.

- [ ] **Step 10: exécuter les contrôles**

Run: `.venv/bin/python -m pytest tests/test_variables_aleatoires_2026.py -q`

Expected: PASS.

Run: `make verify CHAP=1SPE-VARIABLES-ALEATOIRES && make similarity CHAP=1SPE-VARIABLES-ALEATOIRES && make chapter CHAP=1SPE-VARIABLES-ALEATOIRES && .venv/bin/python scripts/check_chapter_release.py 1SPE-VARIABLES-ALEATOIRES && .venv/bin/python scripts/validate_release_proofs.py --scope 1SPE-VARIABLES-ALEATOIRES`

Expected: 0 erreur, 0 référence non résolue, 0 débordement.

- [ ] **Step 11: commit**

```bash
.venv/bin/python scripts/check_chapter_migration.py publication/migrations/1spe-variables-aleatoires.yaml --paths0 | git add --pathspec-from-file=- --pathspec-file-nul
git add publication/migrations/1spe-variables-aleatoires.yaml scripts/extract_python_blocks.py tests/test_variables_aleatoires_2026.py validations/release-1spe/reviews/variables-aleatoires.md validations/release-1spe/reviews/variables-aleatoires-mathematics.json validations/release-1spe/reviews/variables-aleatoires-pedagogy.json validations/release-1spe/reviews/variables-aleatoires-language.json validations/release-1spe/reviews/variables-aleatoires-adversarial.json
git commit -m "[1SPE][BAT] reconstruit variables aleatoires 2026"
```

### Task 9A: Figer les six manifestes de migration restants

**Files:**
- Create: `publication/migrations/1spe-derivation-local.yaml`
- Create: `publication/migrations/1spe-derivation-global.yaml`
- Create: `publication/migrations/1spe-exponentielle.yaml`
- Create: `publication/migrations/1spe-produit-scalaire.yaml`
- Create: `publication/migrations/1spe-geometrie-reperee.yaml`
- Create: `publication/migrations/1spe-proba-cond.yaml`

- [ ] **Step 1: générer les six manifestes depuis la baseline**

Chaque manifeste énumère sans glob les `.tex`, QCM `.json`, sidecars et preuves
à conserver, modifier, créer ou retirer de la release.

- [ ] **Step 2: valider les six manifestes**

Run: `.venv/bin/python scripts/check_chapter_migration.py publication/migrations/1spe-derivation-local.yaml publication/migrations/1spe-derivation-global.yaml publication/migrations/1spe-exponentielle.yaml publication/migrations/1spe-produit-scalaire.yaml publication/migrations/1spe-geometrie-reperee.yaml publication/migrations/1spe-proba-cond.yaml`

Expected: code 0, zéro glob et zéro objet de baseline oublié.

- [ ] **Step 3: commit**

```bash
git add publication/migrations/1spe-derivation-local.yaml publication/migrations/1spe-derivation-global.yaml publication/migrations/1spe-exponentielle.yaml publication/migrations/1spe-produit-scalaire.yaml publication/migrations/1spe-geometrie-reperee.yaml publication/migrations/1spe-proba-cond.yaml
git commit -m "[1SPE][BAT] fige les migrations restantes"
```

### Task 9B: Certifier Dérivation locale

**Files:**
- Modify/Create/Remove from release: exact paths in `publication/migrations/1spe-derivation-local.yaml`
- Create: `validations/release-1spe/reviews/derivation-local-mathematics.json`
- Create: `validations/release-1spe/reviews/derivation-local-pedagogy.json`
- Create: `validations/release-1spe/reviews/derivation-local-language.json`
- Create: `validations/release-1spe/reviews/derivation-local-adversarial.json`

- [ ] **Step 1: appliquer le manifeste et obtenir les quatre bundles indépendants**

Corriger tous les écarts de baseline. Chaque fichier de revue suit
`review_bundle_1spe`, contient une preuve par `object_id × gate_id` applicable
avec empreintes, commande et statut, et utilise un acteur distinct de l'auteur.

- [ ] **Step 2: exécuter les cinq commandes**

Run: `make verify CHAP=1SPE-DERIVATION-LOCAL && make similarity CHAP=1SPE-DERIVATION-LOCAL && make chapter CHAP=1SPE-DERIVATION-LOCAL && .venv/bin/python scripts/check_chapter_release.py 1SPE-DERIVATION-LOCAL && .venv/bin/python scripts/validate_release_proofs.py --scope 1SPE-DERIVATION-LOCAL`

Expected: cinq codes 0, zéro défaut connu et chapitre `certified`.

- [ ] **Step 3: commit**

```bash
.venv/bin/python scripts/check_chapter_migration.py publication/migrations/1spe-derivation-local.yaml --paths0 | git add --pathspec-from-file=- --pathspec-file-nul
git add publication/migrations/1spe-derivation-local.yaml validations/release-1spe/reviews/derivation-local-mathematics.json validations/release-1spe/reviews/derivation-local-pedagogy.json validations/release-1spe/reviews/derivation-local-language.json validations/release-1spe/reviews/derivation-local-adversarial.json
git commit -m "[1SPE][BAT] certifie derivation locale"
```

### Task 9C: Certifier Dérivation globale

**Files:**
- Modify/Create/Remove from release: exact paths in `publication/migrations/1spe-derivation-global.yaml`
- Create: `validations/release-1spe/reviews/derivation-global-mathematics.json`
- Create: `validations/release-1spe/reviews/derivation-global-pedagogy.json`
- Create: `validations/release-1spe/reviews/derivation-global-language.json`
- Create: `validations/release-1spe/reviews/derivation-global-adversarial.json`

- [ ] **Step 1: appliquer le manifeste et obtenir les quatre bundles indépendants**

Corriger couverture, raisonnement global, variations, extremums, évaluations,
langue et remédiations signalés.
Chaque bundle suit `review_bundle_1spe` et couvre ses
`object_id × gate_id` applicables.

- [ ] **Step 2: exécuter les cinq commandes**

Run: `make verify CHAP=1SPE-DERIVATION-GLOBAL && make similarity CHAP=1SPE-DERIVATION-GLOBAL && make chapter CHAP=1SPE-DERIVATION-GLOBAL && .venv/bin/python scripts/check_chapter_release.py 1SPE-DERIVATION-GLOBAL && .venv/bin/python scripts/validate_release_proofs.py --scope 1SPE-DERIVATION-GLOBAL`

Expected: cinq codes 0 et chapitre `certified`.

- [ ] **Step 3: commit**

```bash
.venv/bin/python scripts/check_chapter_migration.py publication/migrations/1spe-derivation-global.yaml --paths0 | git add --pathspec-from-file=- --pathspec-file-nul
git add publication/migrations/1spe-derivation-global.yaml validations/release-1spe/reviews/derivation-global-mathematics.json validations/release-1spe/reviews/derivation-global-pedagogy.json validations/release-1spe/reviews/derivation-global-language.json validations/release-1spe/reviews/derivation-global-adversarial.json
git commit -m "[1SPE][BAT] certifie derivation globale"
```

### Task 9D: Certifier Fonction exponentielle

**Files:**
- Modify/Create/Remove from release: exact paths in `publication/migrations/1spe-exponentielle.yaml`
- Create: `validations/release-1spe/reviews/exponentielle-mathematics.json`
- Create: `validations/release-1spe/reviews/exponentielle-pedagogy.json`
- Create: `validations/release-1spe/reviews/exponentielle-language.json`
- Create: `validations/release-1spe/reviews/exponentielle-adversarial.json`

- [ ] **Step 1: appliquer le manifeste et obtenir les quatre bundles indépendants**

Contrôler définition, propriétés, dérivation, variations, modélisations,
domaines, unités, arrondis, QCM et évaluations.
Chaque bundle suit `review_bundle_1spe` et couvre ses
`object_id × gate_id` applicables.

- [ ] **Step 2: exécuter les cinq commandes**

Run: `make verify CHAP=1SPE-EXPONENTIELLE && make similarity CHAP=1SPE-EXPONENTIELLE && make chapter CHAP=1SPE-EXPONENTIELLE && .venv/bin/python scripts/check_chapter_release.py 1SPE-EXPONENTIELLE && .venv/bin/python scripts/validate_release_proofs.py --scope 1SPE-EXPONENTIELLE`

Expected: cinq codes 0 et chapitre `certified`.

- [ ] **Step 3: commit**

```bash
.venv/bin/python scripts/check_chapter_migration.py publication/migrations/1spe-exponentielle.yaml --paths0 | git add --pathspec-from-file=- --pathspec-file-nul
git add publication/migrations/1spe-exponentielle.yaml validations/release-1spe/reviews/exponentielle-mathematics.json validations/release-1spe/reviews/exponentielle-pedagogy.json validations/release-1spe/reviews/exponentielle-language.json validations/release-1spe/reviews/exponentielle-adversarial.json
git commit -m "[1SPE][BAT] certifie fonction exponentielle"
```

### Task 9E: Certifier Produit scalaire

**Files:**
- Modify/Create/Remove from release: exact paths in `publication/migrations/1spe-produit-scalaire.yaml`
- Create: `validations/release-1spe/reviews/produit-scalaire-mathematics.json`
- Create: `validations/release-1spe/reviews/produit-scalaire-pedagogy.json`
- Create: `validations/release-1spe/reviews/produit-scalaire-language.json`
- Create: `validations/release-1spe/reviews/produit-scalaire-adversarial.json`

- [ ] **Step 1: appliquer le manifeste et obtenir les quatre bundles indépendants**

Contrôler les formulations géométriques et analytiques, orthogonalité, Al-Kashi,
projections, figures, preuves et cohérence des unités.
Chaque bundle suit `review_bundle_1spe` et couvre ses
`object_id × gate_id` applicables.

- [ ] **Step 2: exécuter les cinq commandes**

Run: `make verify CHAP=1SPE-PRODUIT-SCALAIRE && make similarity CHAP=1SPE-PRODUIT-SCALAIRE && make chapter CHAP=1SPE-PRODUIT-SCALAIRE && .venv/bin/python scripts/check_chapter_release.py 1SPE-PRODUIT-SCALAIRE && .venv/bin/python scripts/validate_release_proofs.py --scope 1SPE-PRODUIT-SCALAIRE`

Expected: cinq codes 0 et chapitre `certified`.

- [ ] **Step 3: commit**

```bash
.venv/bin/python scripts/check_chapter_migration.py publication/migrations/1spe-produit-scalaire.yaml --paths0 | git add --pathspec-from-file=- --pathspec-file-nul
git add publication/migrations/1spe-produit-scalaire.yaml validations/release-1spe/reviews/produit-scalaire-mathematics.json validations/release-1spe/reviews/produit-scalaire-pedagogy.json validations/release-1spe/reviews/produit-scalaire-language.json validations/release-1spe/reviews/produit-scalaire-adversarial.json
git commit -m "[1SPE][BAT] certifie produit scalaire"
```

### Task 9F: Certifier Géométrie repérée

**Files:**
- Modify/Create/Remove from release: exact paths in `publication/migrations/1spe-geometrie-reperee.yaml`
- Create: `validations/release-1spe/reviews/geometrie-reperee-mathematics.json`
- Create: `validations/release-1spe/reviews/geometrie-reperee-pedagogy.json`
- Create: `validations/release-1spe/reviews/geometrie-reperee-language.json`
- Create: `validations/release-1spe/reviews/geometrie-reperee-adversarial.json`

- [ ] **Step 1: appliquer le manifeste et obtenir les quatre bundles indépendants**

Contrôler équations cartésiennes, vecteurs directeurs/normaux, intersections,
distances, cercles, figures, cas limites et remédiations.
Chaque bundle suit `review_bundle_1spe` et couvre ses
`object_id × gate_id` applicables.

- [ ] **Step 2: exécuter les cinq commandes**

Run: `make verify CHAP=1SPE-GEOMETRIE-REPEREE && make similarity CHAP=1SPE-GEOMETRIE-REPEREE && make chapter CHAP=1SPE-GEOMETRIE-REPEREE && .venv/bin/python scripts/check_chapter_release.py 1SPE-GEOMETRIE-REPEREE && .venv/bin/python scripts/validate_release_proofs.py --scope 1SPE-GEOMETRIE-REPEREE`

Expected: cinq codes 0 et chapitre `certified`.

- [ ] **Step 3: commit**

```bash
.venv/bin/python scripts/check_chapter_migration.py publication/migrations/1spe-geometrie-reperee.yaml --paths0 | git add --pathspec-from-file=- --pathspec-file-nul
git add publication/migrations/1spe-geometrie-reperee.yaml validations/release-1spe/reviews/geometrie-reperee-mathematics.json validations/release-1spe/reviews/geometrie-reperee-pedagogy.json validations/release-1spe/reviews/geometrie-reperee-language.json validations/release-1spe/reviews/geometrie-reperee-adversarial.json
git commit -m "[1SPE][BAT] certifie geometrie reperee"
```

### Task 9G: Certifier Probabilités conditionnelles

**Files:**
- Modify/Create/Remove from release: exact paths in `publication/migrations/1spe-proba-cond.yaml`
- Create: `validations/release-1spe/reviews/proba-cond-mathematics.json`
- Create: `validations/release-1spe/reviews/proba-cond-pedagogy.json`
- Create: `validations/release-1spe/reviews/proba-cond-language.json`
- Create: `validations/release-1spe/reviews/proba-cond-adversarial.json`

- [ ] **Step 1: appliquer le manifeste et obtenir les quatre bundles indépendants**

Contrôler conditionnement, arbres, partitions, probabilités totales,
indépendance, répétitions prescrites, Monte-Carlo, hypothèses et cas limites.
Chaque bundle suit `review_bundle_1spe` et couvre ses
`object_id × gate_id` applicables.

- [ ] **Step 2: exécuter les cinq commandes**

Run: `make verify CHAP=1SPE-PROBA-COND && make similarity CHAP=1SPE-PROBA-COND && make chapter CHAP=1SPE-PROBA-COND && .venv/bin/python scripts/check_chapter_release.py 1SPE-PROBA-COND && .venv/bin/python scripts/validate_release_proofs.py --scope 1SPE-PROBA-COND`

Expected: cinq codes 0 et chapitre `certified`.

- [ ] **Step 3: commit**

```bash
.venv/bin/python scripts/check_chapter_migration.py publication/migrations/1spe-proba-cond.yaml --paths0 | git add --pathspec-from-file=- --pathspec-file-nul
git add publication/migrations/1spe-proba-cond.yaml validations/release-1spe/reviews/proba-cond-mathematics.json validations/release-1spe/reviews/proba-cond-pedagogy.json validations/release-1spe/reviews/proba-cond-language.json validations/release-1spe/reviews/proba-cond-adversarial.json
git commit -m "[1SPE][BAT] certifie probabilites conditionnelles"
```

### Task 10: Finaliser les transversaux, automatismes et matrices pédagogiques

**Files:**
- Create: `referentiel/transversaux_1SPE_2026.yaml`
- Create: `publication/migrations/1spe-transversaux.yaml`
- Modify: `transversal/avant_propos.tex`
- Modify: `transversal/formulaire.tex`
- Modify: `transversal/memo_python.tex`
- Modify: `transversal/mode_emploi.tex`
- Modify: `chapitres/1SPE-SUITES/objects.yaml`
- Modify: `chapitres/1SPE-SECOND-DEGRE/objects.yaml`
- Modify: `chapitres/1SPE-DERIVATION-LOCAL/objects.yaml`
- Modify: `chapitres/1SPE-DERIVATION-GLOBAL/objects.yaml`
- Modify: `chapitres/1SPE-EXPONENTIELLE/objects.yaml`
- Modify: `chapitres/1SPE-TRIGONOMETRIE/objects.yaml`
- Modify: `chapitres/1SPE-PRODUIT-SCALAIRE/objects.yaml`
- Modify: `chapitres/1SPE-GEOMETRIE-REPEREE/objects.yaml`
- Modify: `chapitres/1SPE-PROBA-COND/objects.yaml`
- Modify: `chapitres/1SPE-VARIABLES-ALEATOIRES/objects.yaml`
- Create: `transversal/logique_ensembliste.tex`
- Create: `transversal/automatismes.tex`
- Create: `transversal/progression_annuelle.tex`
- Create: `transversal/tableau_competences.tex`
- Create: `tests/test_transversal_coverage.py`
- Create: `validations/release-1spe/reviews/transversaux.md`
- Create: `validations/release-1spe/reviews/transversaux-mathematics.json`
- Create: `validations/release-1spe/reviews/transversaux-pedagogy.json`
- Create: `validations/release-1spe/reviews/transversaux-language.json`
- Create: `validations/release-1spe/reviews/transversaux-adversarial.json`

- [ ] **Step 1: écrire les tests rouges**

```python
def test_every_transversal_item_is_distributed(matrix):
    assert matrix.missing_transversal() == []

def test_every_item_has_three_distinct_roles(matrix):
    for item in matrix.items:
        assert item.introduction_object_id
        assert item.reinvestment_object_id
        assert item.reference_object_id
        assert item.introduction_object_id != item.reinvestment_object_id

def test_all_transversal_families_are_covered(matrix):
    assert matrix.missing_by_family == {
        "logic_sets": [], "algorithms_lists": [],
        "automatisms": [], "experiments": [],
    }
    assert len(matrix.experiment_ids) == 4
```

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_transversal_coverage.py -q`

Expected: FAIL sur les transversaux non encore tracés.

- [ ] **Step 3: figer et valider le manifeste avant toute rédaction**

Créer `publication/migrations/1spe-transversaux.yaml` à partir de la baseline :
il énumère sans glob tous les chemins exacts qui seront créés ou modifiés dans
les modules communs et les dix chapitres.

Run: `.venv/bin/python scripts/check_chapter_migration.py publication/migrations/1spe-transversaux.yaml`

Expected: code 0 avant toute modification, zéro glob et zéro objet oublié.

- [ ] **Step 4: rédiger les modules communs et injecter les liens**

Le référentiel et les modules synthétisent logique, ensembles, vocabulaire,
algorithmique/Python, listes, automatismes et les quatre expérimentations sans
créer de onzième chapitre ni répéter les cours. Chaque item possède une
introduction, un réinvestissement dans un objet distinct et un renvoi vers une
banque ou un mémo. Ne toucher qu'aux chemins figés à la Step 3.

- [ ] **Step 5: reconstruire formulaire et matrices**

Le formulaire ne contient que les résultats admis au niveau. La matrice
transversale est complète ; l'index à folios est volontairement généré après le
manifeste d'assemblage en Chunk 3.

- [ ] **Step 6: revue pédagogique annuelle**

Quatre agents distincts contrôlent mathématiques/algorithmique, prérequis,
absence de dépendance circulaire, charge, alternance des thèmes, six
compétences, faisabilité annuelle, langue et robustesse adversariale. Chaque
bundle contient une preuve par objet et gate applicable.

- [ ] **Step 7: exécuter les tests**

Run: `.venv/bin/python -m pytest tests/test_transversal_coverage.py -q`

Expected: PASS.

- [ ] **Step 8: commit**

```bash
.venv/bin/python scripts/check_chapter_migration.py publication/migrations/1spe-transversaux.yaml --paths0 | git add --pathspec-from-file=- --pathspec-file-nul
git add referentiel/transversaux_1SPE_2026.yaml publication/migrations/1spe-transversaux.yaml tests/test_transversal_coverage.py validations/release-1spe/reviews/transversaux.md validations/release-1spe/reviews/transversaux-mathematics.json validations/release-1spe/reviews/transversaux-pedagogy.json validations/release-1spe/reviews/transversaux-language.json validations/release-1spe/reviews/transversaux-adversarial.json
git commit -m "[1SPE][BAT] finalise les dimensions transversales"
```

### Task 10B: Fermer l'audit éditorial du Chunk 2

**Files:**
- Modify: `tests/test_audit_content_1spe.py`
- Regenerate: `validations/release-1spe/content-audit.json`
- Regenerate: `validations/release-1spe/content-audit.md`
- Create: `validations/release-1spe/content-proof-closure.json`

- [ ] **Step 1: écrire le test rouge de fraîcheur**

Le test recalcule les empreintes des dix sidecars, de tous les chemins qu'ils
référencent et des transversaux ; il refuse tout verdict périmé, `needs_fix` ou
`blocked` numérique.

- [ ] **Step 2: exécuter le test avant fermeture**

Run: `.venv/bin/python -m pytest tests/test_audit_content_1spe.py -q`

Expected: FAIL si une preuve manque ou ne correspond pas à l'empreinte courante.

- [ ] **Step 3: régénérer l'audit en mode bloquant**

Run: `.venv/bin/python scripts/audit_content_1spe.py --release release/1spe-2026.yaml --require-certified --proof validations/release-1spe/content-proof-closure.json`

Expected: code 0, dix chapitres et transversaux `certified`, zéro preuve
périmée, zéro `needs_fix|blocked` numérique.

- [ ] **Step 4: exécuter la suite de Chunk 2 et commit**

Run: `.venv/bin/python -m pytest tests/test_audit_content_1spe.py tests/test_chapter_release.py tests/test_chapter_suites_2026.py tests/test_chapter_second_degre_2026.py tests/test_chapter_trigonometrie_2026.py tests/test_variables_aleatoires_2026.py tests/test_transversal_coverage.py -q`

Expected: PASS.

Run: `.venv/bin/python scripts/check_chapter_release.py --all && .venv/bin/python scripts/validate_release_proofs.py --scope all-content`

Expected: dix chapitres et transversaux `certified` sur leurs empreintes
courantes.

```bash
git add tests/test_audit_content_1spe.py validations/release-1spe/content-audit.json validations/release-1spe/content-audit.md validations/release-1spe/content-proof-closure.json
git commit -m "[1SPE][BAT] ferme la certification editoriale"
```

## Chunk 3: Maquette V5, métadonnées, couvertures et double assemblage

### Task 11A: Créer la géométrie de release 195 × 270 mm

**Files:**
- Create: `gabarits/nexus-manuel-1spe-2026.cls`
- Create: `gabarits/nexus-components-1spe-2026.tex`
- Create: `gabarits/specimen-1spe-2026.tex`
- Create: `scripts/build_specimen_1spe_2026.py`
- Create: `scripts/check_specimen_1spe_2026.py`
- Create: `tests/test_nexus_1spe_2026_class.py`
- Create: `tests/test_specimen_1spe_2026.py`
- Create: `build/maquette-1spe-2026/specimen-1spe-2026.pdf`
- Create: `build/maquette-1spe-2026/specimen-1spe-2026.log`
- Create: `build/maquette-1spe-2026/specimen-1spe-2026-report.json`

- [ ] **Step 1: écrire les tests rouges du format**

```python
def test_compiled_specimen_has_finished_trim(report):
    assert report["trim_mm"] == [195, 270]
    assert report["safe_zone_mm"] >= 5
    assert report["inner_margin_mm"] > report["outer_margin_mm"]

def test_compiled_specimen_is_clean(report):
    assert report["body_font_pt"] >= 9.5
    assert report["technical_line_pt"] >= 0.25
    assert report["unembedded_fonts"] == []
    assert report["overfull_hbox"] == 0
    assert report["overfull_vbox"] == 0
```

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_nexus_1spe_2026_class.py tests/test_specimen_1spe_2026.py -q`

Expected: FAIL car la classe, le compilateur et le PDF final n'existent pas.

- [ ] **Step 3: créer une classe de release dédiée**

La classe charge `nexus-manuel-v5`, fixe le format fini, la zone de sécurité, la
marge intérieure renforcée, `fr-FR`, auteur et variantes. Tous les ajustements
restent dans `nexus-manuel-1spe-2026.cls` et
`nexus-components-1spe-2026.tex` ; aucun fichier partagé TSPE n'est modifié.

- [ ] **Step 4: implémenter le compilateur exécutable**

`build_specimen_1spe_2026.py` compile trois passes LuaLaTeX et écrit exactement
les trois artefacts listés. `check_specimen_1spe_2026.py` utilise PyMuPDF,
`pdffonts` et le journal LaTeX pour calculer les métriques.

- [ ] **Step 5: compiler et vérifier le spécimen**

Run: `.venv/bin/python scripts/build_specimen_1spe_2026.py --source gabarits/specimen-1spe-2026.tex --output-dir build/maquette-1spe-2026`

Expected: code 0 et PDF
`build/maquette-1spe-2026/specimen-1spe-2026.pdf`.

Run: `.venv/bin/python scripts/check_specimen_1spe_2026.py build/maquette-1spe-2026/specimen-1spe-2026.pdf --log build/maquette-1spe-2026/specimen-1spe-2026.log --output build/maquette-1spe-2026/specimen-1spe-2026-report.json`

Expected: code 0, TrimBox 195 × 270 mm, sécurité ≥5 mm, corps ≥9,5 pt, traits
≥0,25 pt, toutes polices incorporées et aucun débordement.

- [ ] **Step 6: exécuter les tests**

Run: `.venv/bin/python -m pytest tests/test_nexus_1spe_2026_class.py tests/test_specimen_1spe_2026.py tests/test_maquette_v5.py -q`

Expected: PASS, sans régression V5.

- [ ] **Step 7: commit**

```bash
git add gabarits/nexus-manuel-1spe-2026.cls gabarits/nexus-components-1spe-2026.tex gabarits/specimen-1spe-2026.tex scripts/build_specimen_1spe_2026.py scripts/check_specimen_1spe_2026.py tests/test_nexus_1spe_2026_class.py tests/test_specimen_1spe_2026.py
git commit -m "[1SPE][BAT] fixe la geometrie de release"
```

### Task 11B: Adapter et approuver les familles de pages V5

**Files:**
- Modify: `gabarits/nexus-components-1spe-2026.tex`
- Modify: `gabarits/specimen-1spe-2026.tex`
- Create: `schemas/visual_witness.schema.json`
- Create: `scripts/render_visual_witnesses.py`
- Create: `gabarits/reference-1spe-2026/pages-temoins.yaml`
- Create: `gabarits/reference-1spe-2026/images/01-ouverture.png`
- Create: `gabarits/reference-1spe-2026/images/02-activite.png`
- Create: `gabarits/reference-1spe-2026/images/03-cours-dense.png`
- Create: `gabarits/reference-1spe-2026/images/04-methode.png`
- Create: `gabarits/reference-1spe-2026/images/05-exercices.png`
- Create: `gabarits/reference-1spe-2026/images/06-qcm.png`
- Create: `gabarits/reference-1spe-2026/images/07-evaluation.png`
- Create: `gabarits/reference-1spe-2026/images/08-remediation.png`
- Create: `gabarits/reference-1spe-2026/images/09-corrige.png`
- Create: `gabarits/reference-1spe-2026/images/10-annexe.png`
- Create: `gabarits/reference-1spe-2026/images/11-page-legale.png`
- Create: `gabarits/reference-1spe-2026/images/12-index.png`
- Create: `tests/test_visual_witnesses.py`
- Create: `validations/release-1spe/visual-witness-comparison.json`
- Create: `validations/release-1spe/reviews/maquette.json`
- Create: `validations/release-1spe/reviews/maquette.md`

- [ ] **Step 1: écrire les tests rouges des douze familles**

Le test impose les familles `ouverture`, `activite`, `cours_dense`, `methode`,
`exercices`, `qcm`, `evaluation`, `remediation`, `corrige`, `annexe`,
`page_legale`, `index`. Chaque entrée porte page exacte, image de référence,
SHA-256, seuils, approbateur et statut.

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_visual_witnesses.py -q`

Expected: FAIL car le schéma, les témoins et le verdict n'existent pas.

- [ ] **Step 3: adapter chaque famille**

Recalibrer dans le fichier 1SPE dédié grilles, onglets, ouvertures, tableaux,
encadrés, appels de corrigés, folios et figures. Après chaque famille, compiler
le spécimen et refuser toute réduction locale du corps.

- [ ] **Step 4: produire des candidats sans muter les témoins**

Run: `.venv/bin/python scripts/render_visual_witnesses.py --mode candidate --pdf build/maquette-1spe-2026/specimen-1spe-2026.pdf --manifest gabarits/reference-1spe-2026/pages-temoins.yaml --output-dir build/maquette-1spe-2026/witness-candidates --dpi 180`

Expected: douze PNG candidats ; le script refuse une page hors bornes et ne
modifie ni le manifeste de référence, ni ses douze PNG, ni leurs SHA-256.

Un agent UI/UX inspecte ensuite les douze pages exactes à taille lisible, contrôle
densité, hiérarchie, contraste, espaces, tableaux, légendes et accessibilité
visuelle, puis écrit le verdict structuré et sa synthèse.

- [ ] **Step 5: promouvoir une fois, puis vérifier en mode non mutatif**

Après verdict `certified` d'un approbateur distinct de l'auteur :

Run: `.venv/bin/python scripts/render_visual_witnesses.py --mode promote --candidate-dir build/maquette-1spe-2026/witness-candidates --approval validations/release-1spe/reviews/maquette.json --manifest gabarits/reference-1spe-2026/pages-temoins.yaml --output-dir gabarits/reference-1spe-2026/images`

Expected: les douze PNG exacts de `Files` et leurs SHA-256 sont écrits une seule
fois. Toute mise à jour ultérieure exige un nouveau verdict distinct et un mode
`promote` explicite.

Run: `.venv/bin/python scripts/render_visual_witnesses.py --mode verify --pdf build/maquette-1spe-2026/specimen-1spe-2026.pdf --manifest gabarits/reference-1spe-2026/pages-temoins.yaml --reference-dir gabarits/reference-1spe-2026/images --output validations/release-1spe/visual-witness-comparison.json --dpi 180`

Expected: code 0 et douze comparaisons conformes sans aucune mutation des
références. Les tests rendent une régression volontaire, exigent code 2, puis
vérifient que manifeste, PNG et SHA-256 de référence sont inchangés.

- [ ] **Step 6: exécuter les tests**

Run: `.venv/bin/python -m pytest tests/test_visual_witnesses.py tests/test_specimen_1spe_2026.py tests/test_maquette_v5.py -q`

Expected: PASS et douze familles `certified`.

- [ ] **Step 7: commit**

```bash
git add gabarits/nexus-components-1spe-2026.tex gabarits/specimen-1spe-2026.tex schemas/visual_witness.schema.json scripts/render_visual_witnesses.py gabarits/reference-1spe-2026/pages-temoins.yaml gabarits/reference-1spe-2026/images/01-ouverture.png gabarits/reference-1spe-2026/images/02-activite.png gabarits/reference-1spe-2026/images/03-cours-dense.png gabarits/reference-1spe-2026/images/04-methode.png gabarits/reference-1spe-2026/images/05-exercices.png gabarits/reference-1spe-2026/images/06-qcm.png gabarits/reference-1spe-2026/images/07-evaluation.png gabarits/reference-1spe-2026/images/08-remediation.png gabarits/reference-1spe-2026/images/09-corrige.png gabarits/reference-1spe-2026/images/10-annexe.png gabarits/reference-1spe-2026/images/11-page-legale.png gabarits/reference-1spe-2026/images/12-index.png tests/test_visual_witnesses.py validations/release-1spe/visual-witness-comparison.json validations/release-1spe/reviews/maquette.json validations/release-1spe/reviews/maquette.md
git commit -m "[1SPE][BAT] porte clarte nexus au format fini"
```

### Task 12: Finaliser les métadonnées, la page légale et le protocole tunisien

**Files:**
- Create: `schemas/publication_metadata.schema.json`
- Create: `schemas/legal_deposit_tracking.schema.json`
- Create: `publication/1spe-2026.yaml`
- Create: `publication/suivi-depot-legal-1spe-2026.yaml`
- Create: `transversal/mentions_legales_eleve.tex`
- Create: `transversal/mentions_legales_professeur.tex`
- Create: `gabarits/legal-page-proof.tex`
- Create: `scripts/render_legal_page.py`
- Create: `scripts/check_publication_metadata.py`
- Create: `tests/test_publication_metadata.py`
- Create: `docs/publication/protocole-depot-legal-tunisie.md`

- [ ] **Step 1: écrire les tests rouges des données imposées**

```python
def test_author_is_exact(metadata):
    assert metadata["author"] == "Alaeddine BEN RHOUMA"

def test_no_isbn_is_printed(metadata, legal_text):
    assert metadata["isbn"] is None
    assert "ISBN" not in legal_text

def test_missing_legal_address_blocks_bat(metadata):
    metadata["legal_publisher"]["address"] = None
    assert publication_status(metadata).digital_content == "certified"
    assert publication_status(metadata).physical_completion == "blocked"

def test_each_variant_has_complete_identity(metadata):
    assert metadata["books"]["eleve"]["title"] == "Mathématiques"
    assert metadata["books"]["eleve"]["variant"] == "Manuel élève"
    assert metadata["books"]["professeur"]["variant"] == "Professeur"
    for book in metadata["books"].values():
        assert book["programme_year"] == "2026-2027"
        assert book["edition_number"] == 1
```

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_publication_metadata.py -q`

Expected: FAIL car le contrat n'existe pas.

- [ ] **Step 3: créer le schéma et les données certaines**

```yaml
author: Alaeddine BEN RHOUMA
copyright:
  holder: M&M ACADEMY SUARL
  year: 2026
legal_publisher:
  name: M&M ACADEMY SUARL
brand: Nexus Réussite
territory: Tunisie
isbn: null
books:
  eleve:
    title: Mathématiques
    variant: Manuel élève
    programme_year: 2026-2027
    edition_number: 1
    deposit_copies: 4
  professeur:
    title: Mathématiques
    variant: Professeur
    programme_year: 2026-2027
    edition_number: 1
    deposit_copies: 4
```

- [ ] **Step 4: représenter les données externes sans faux contenu**

Adresse légale, lieu/pays d'impression, imprimeur, adresse imprimeur, tirage,
date d'impression, profil accepté et largeur du dos portent `value: null`,
`status: blocked`, `required_by` et `evidence_path` jusqu'à réception d'une
preuve. `suivi-depot-legal-1spe-2026.yaml` suit séparément chaque ouvrage :
numéro/date d'inscription, date de mise à disposition, échéance calculée à un
mois, quatre exemplaires, dates de dépôt et chemins des récépissés.

Chaque objet légal expose deux statuts sans ambiguïté :
`digital_content_status`, certifiable si les données certaines et l'absence
d'ISBN sont exactes, et `physical_completion_status`, bloqué jusqu'aux données
imprimeur. Seuls `LEGAL-ELEVE` et `LEGAL-PROFESSEUR` peuvent entrer dans un
candidat numérique avec le premier `certified` et le second `blocked`.

- [ ] **Step 5: générer la page légale**

Le générateur produit « Édité par M&M ACADEMY SUARL sous la marque Nexus
Réussite », titre/variante, droit d'auteur/année, édition, lieu/pays, impression,
tirage et dépôt légal. Il refuse le mode `--stage bat` si un champ légal
obligatoire reste bloqué. En mode `proof`, il omet entièrement les mentions
physiques non prouvées, sans libellé vide ni faux contenu, et marque
`digital_content_status=certified`,
`physical_completion_status=blocked`.

- [ ] **Step 6: exécuter les CLI et compiler la preuve**

Run: `.venv/bin/python scripts/check_publication_metadata.py --metadata publication/1spe-2026.yaml --deposit-tracking publication/suivi-depot-legal-1spe-2026.yaml --stage digital`

Expected: code 0 pour les données numériques certaines et liste structurée des
bloqueurs physiques.

Run: `.venv/bin/python scripts/render_legal_page.py --metadata publication/1spe-2026.yaml --variant eleve --stage proof --output transversal/mentions_legales_eleve.tex && .venv/bin/python scripts/render_legal_page.py --metadata publication/1spe-2026.yaml --variant professeur --stage proof --output transversal/mentions_legales_professeur.tex`

Expected: code 0 et deux fichiers TeX sans ISBN ni champ factice ; le premier
contient exclusivement « Manuel élève » comme variante, le second
exclusivement « Professeur ».

Run: `TEXINPUTS=gabarits: lualatex -interaction=nonstopmode -halt-on-error -output-directory=build/maquette-1spe-2026 gabarits/legal-page-proof.tex`

Expected: code 0 et texte légal sélectionnable dans
`build/maquette-1spe-2026/legal-page-proof.pdf`.

- [ ] **Step 7: documenter le protocole**

Le protocole liste l'enregistrement, quatre exemplaires de chaque livre, le délai d'un mois après mise à disposition, les responsables, les dates et l'archivage des récépissés.

- [ ] **Step 8: exécuter les tests**

Run: `.venv/bin/python -m pytest tests/test_publication_metadata.py -q`

Expected: PASS ; contenu numérique légal `certified`, achèvement physique
`blocked` tant que les données externes manquent. La Task 20 régénère en mode
`bat` et exige les deux statuts `certified` avant le candidat final imprimable.

- [ ] **Step 9: commit**

```bash
git add schemas/publication_metadata.schema.json schemas/legal_deposit_tracking.schema.json publication/1spe-2026.yaml publication/suivi-depot-legal-1spe-2026.yaml transversal/mentions_legales_eleve.tex transversal/mentions_legales_professeur.tex gabarits/legal-page-proof.tex scripts/render_legal_page.py scripts/check_publication_metadata.py tests/test_publication_metadata.py docs/publication/protocole-depot-legal-tunisie.md
git commit -m "[1SPE][BAT] formalise la publication tunisienne"
```

### Task 13: Créer les couvertures « Courbes signature »

**Files:**
- Create: `gabarits/nexus-couverture-1spe-2026.tex`
- Create: `scripts/build_covers_1spe.py`
- Create: `tests/test_covers_1spe.py`
- Create: `publication/couvertures-1spe-2026.yaml`
- Create: `validations/release-1spe/reviews/couvertures.md`
- Create: `validations/release-1spe/reviews/couvertures.json`
- Create: `build/covers-1spe-2026/eleve-proof.pdf`
- Create: `build/covers-1spe-2026/professeur-proof.pdf`
- Create: `build/covers-1spe-2026/report.json`

- [ ] **Step 1: écrire les tests rouges**

```python
def test_front_cover_identity(cover_text):
    assert "Alaeddine BEN RHOUMA" in cover_text
    assert "Mathématiques" in cover_text
    assert "Première · spécialité" in cover_text
    assert "Programme applicable à la rentrée 2026-2027" in cover_text
    assert "Nexus Réussite" in cover_text

def test_variants_and_forbidden_claims(covers):
    assert covers["eleve"].variant == "Manuel élève"
    assert covers["professeur"].variant == "Professeur"
    forbidden = {"manuel officiel", "homologué", "agréé par le ministère"}
    assert not any(term in covers.all_text.lower() for term in forbidden)

def test_spine_is_computed_not_guessed(spec):
    assert spec["spine"]["source"] == "printer_template"

def test_cover_proof_geometry(report):
    assert report["trim_mm"] == [195, 270]
    assert report["safe_zone_mm"] >= 5
```

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_covers_1spe.py -q`

Expected: FAIL par absence des couvertures.

- [ ] **Step 3: construire le système commun**

Créer recto, dos et quatrième à plat avec courbes signature, hiérarchie Nexus, distinction élève/professeur, CMJN et fonds perdus pilotés par le YAML.

- [ ] **Step 4: interdire tout dos inventé**

Le mode `proof` produit exactement un PDF de deux pages par variante : page 1
recto, page 2 quatrième, aux chemins listés. Le mode `printer-flat` produit une
planche à plat avec 3 mm de fond perdu et sécurité de 5 mm, mais reste `blocked`
tant que le gabarit imprimeur et la largeur du dos ne sont pas renseignés.

- [ ] **Step 5: compiler les épreuves**

Run: `.venv/bin/python scripts/build_covers_1spe.py --mode proof --variants eleve professeur --output-dir build/covers-1spe-2026 --report build/covers-1spe-2026/report.json`

Expected: les deux PDF de deux pages listés, TrimBox 195 × 270 mm, sécurité
≥5 mm, auteur exact, variantes exactes, zéro ISBN, zéro formulation interdite et
zéro ressource manquante.

- [ ] **Step 6: revue visuelle indépendante**

Un agent indépendant contrôle lisibilité en vignette, différenciation des
versions, alignements, contraste, absence de promesse invérifiable et cohérence
avec l'intérieur, puis produit `couvertures.json` conforme au schéma de preuve.

- [ ] **Step 7: exécuter les tests**

Run: `.venv/bin/python -m pytest tests/test_covers_1spe.py -q`

Expected: PASS ; `printer-flat` reste bloqué si le gabarit externe manque.

- [ ] **Step 8: commit**

```bash
git add gabarits/nexus-couverture-1spe-2026.tex scripts/build_covers_1spe.py tests/test_covers_1spe.py publication/couvertures-1spe-2026.yaml validations/release-1spe/reviews/couvertures.md validations/release-1spe/reviews/couvertures.json
git commit -m "[1SPE][BAT] cree les couvertures courbes signature"
```

### Task 14: Assembler d'abord l'élève, puis le professeur

**Files:**
- Create: `scripts/release_manifest.py`
- Create: `scripts/folio_map.py`
- Create: `scripts/check_legal_page_in_pdf.py`
- Rewrite: `scripts/assemble_manuel.py`
- Modify: `scripts/pdf_integrity.py`
- Create: `schemas/folio_map.schema.json`
- Create: `schemas/build_report.schema.json`
- Create: `tests/test_release_manifest.py`
- Create: `tests/test_folio_map.py`
- Create: `tests/test_legal_page_in_pdf.py`
- Create: `tests/fixtures/legal-page-with-isbn.tex`
- Create: `tests/test_build_artifact_freshness.py`
- Modify: `tests/test_pdf_integrity.py`
- Modify: `tests/test_assemble_engine.py`
- Regenerate: `transversal/index_capacites.tex`
- Create: `build/MANUEL_1SPE/eleve/MANUEL_1SPE_eleve.pdf`
- Create: `build/MANUEL_1SPE/eleve/MANUEL_1SPE_eleve.log`
- Create: `build/MANUEL_1SPE/eleve/manifest.json`
- Create: `build/MANUEL_1SPE/eleve/references.json`
- Create: `build/MANUEL_1SPE/eleve/pdf-report.json`
- Create: `build/MANUEL_1SPE/eleve/SHA256SUMS`
- Create: `build/MANUEL_1SPE/folios-eleve.json`
- Create: `build/MANUEL_1SPE/professeur/MANUEL_1SPE_professeur.pdf`
- Create: `build/MANUEL_1SPE/professeur/MANUEL_1SPE_professeur.log`
- Create: `build/MANUEL_1SPE/professeur/manifest.json`
- Create: `build/MANUEL_1SPE/professeur/references.json`
- Create: `build/MANUEL_1SPE/professeur/pdf-report.json`
- Create: `build/MANUEL_1SPE/professeur/SHA256SUMS`
- Create: `build/MANUEL_1SPE/folios-professeur.json`
- Create: `build/MANUEL_1SPE/table-correspondance.json`
- Create: `build/MANUEL_1SPE/build-session.json`

- [ ] **Step 1: écrire les tests rouges du graphe d'objets**

```python
def test_every_student_object_has_one_student_folio(crosswalk):
    for obj in crosswalk.student_objects:
        assert obj.folio_eleve is not None
        assert obj.student_occurrences == 1

def test_teacher_references_are_explicit(crosswalk):
    assert all(ref.rendered.startswith(("Élève p. ", "Prof. p. "))
               for ref in crosswalk.references)

def test_non_certified_object_is_rejected(manifest):
    manifest.objects[0].status = "needs_fix"
    assert buildable(manifest) is False

def test_digital_stage_allows_only_incomplete_physical_legal_objects(manifest):
    assert buildable(manifest, stage="digital") is True
    manifest.object("COURSE-001").physical_completion_status = "blocked"
    assert buildable(manifest, stage="digital") is False

def test_variant_boundaries(manifest):
    assert manifest.student.evaluation_statements
    assert not manifest.student.solutions
    assert not manifest.student.grading_scales
    assert manifest.teacher.solutions
    assert manifest.teacher.grading_scales
    assert manifest.teacher.pedagogical_notes

def test_folio_ranges(crosswalk, page_counts):
    for obj in crosswalk.objects:
        assert obj.first_page <= obj.last_page <= page_counts[obj.variant]
        assert obj.canonical_folio == obj.first_page
        if obj.visibility == "professor_only":
            assert obj.folio_eleve is None
```

`test_legal_page_in_pdf.py` compile réellement
`tests/fixtures/legal-page-with-isbn.tex` dans un répertoire temporaire, appelle
la CLI sur le PDF obtenu et exige `returncode == 2` avec `ISBN` dans le
diagnostic. `test_build_artifact_freshness.py` produit deux sessions temporaires
distinctes et remplace dans la seconde un PDF ainsi que ses anciennes sommes
par ceux de la première ; le contrôleur doit les rejeter.

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_release_manifest.py tests/test_folio_map.py tests/test_legal_page_in_pdf.py tests/test_build_artifact_freshness.py -q`

Expected: FAIL car l'assembleur ne produit aucun folio canonique.

- [ ] **Step 3: générer un manifeste commun**

Le manifeste ordonne uniquement les objets certifiés sur leurs empreintes
courantes, définit variantes, dépendances et labels LaTeX. Au stage `digital`,
les deux objets légaux exigent `digital_content_status=certified` et peuvent
seuls conserver `physical_completion_status=blocked`; au stage `print`, les
deux statuts sont obligatoirement `certified`. L'élève inclut les énoncés
d'évaluation mais exclut corrigés et barèmes ; le professeur inclut corrigés,
barèmes, intentions, erreurs fréquentes et différenciation.

- [ ] **Step 4: instrumenter les débuts et fins d'objet**

Chaque objet écrit dans un fichier auxiliaire son identifiant et son folio de
début/fin. `folio_map.py` valide unicité, complétude, `canonical_folio ==
first_page`, `last_page >= first_page` et bornes du PDF. Les seules macros de
renvoi sont `\renvoiEleve{OBJECT_ID}` et `\renvoiProf{OBJECT_ID}` ; un linter
refuse un argument numérique dans ces macros.

- [ ] **Step 5: construire l'élève**

Run: `.venv/bin/python scripts/assemble_manuel.py --variant eleve --release 1SPE-RC0 --stage digital --new-build-session build/MANUEL_1SPE/build-session.json`

Expected: les six artefacts élève et `folios-eleve.json` aux chemins listés.
Statut pagination : `target` pour 448–480, `below_target` sous 448,
`blocked_over_maximum` au-dessus de 480 ; aucune compression typographique.

- [ ] **Step 6: construire le professeur en injectant les folios élève**

Run: `.venv/bin/python scripts/assemble_manuel.py --variant professeur --release 1SPE-RC0 --stage digital --build-session build/MANUEL_1SPE/build-session.json --student-folios build/MANUEL_1SPE/folios-eleve.json`

Expected: les six artefacts professeur, `folios-professeur.json` et table
croisée. Statut pagination : `target` pour 512–544,
`within_release_maximum` pour 545–560, `below_target` sous 512 et
`blocked_over_maximum` au-dessus de 560.

- [ ] **Step 7: vérifier tous les renvois**

Le contrôle refuse doublon, objet élève absent du professeur, objet
`professor_only` avec folio élève, folio non entier/hors bornes, plage invalide,
référence non résolue ou argument numérique des deux macros de renvoi.

- [ ] **Step 8: exécuter les tests**

Run: `.venv/bin/python -m pytest tests/test_release_manifest.py tests/test_folio_map.py tests/test_assemble_engine.py tests/test_pdf_integrity.py tests/test_legal_page_in_pdf.py tests/test_build_artifact_freshness.py -q`

Expected: PASS. Pour chaque variante, `SHA256SUMS` contient et vérifie le PDF,
le journal, le manifeste, les références et le rapport ; les six artefacts
portent le `build_id` courant : métadonnée XMP `nexus:BuildID` du PDF, ligne
`NEXUS_BUILD_ID=` du journal, champ racine des trois JSON et commentaire
`# build_id=` de `SHA256SUMS`. `build-session.json`, créé avant toute
compilation, lie ce même identifiant à l'heure de départ, au commit Git, au
SHA-256 du manifeste d'entrée et aux deux variantes. Chaque variante est bâtie
dans un répertoire temporaire neuf puis publiée atomiquement. Les tests
remplacent un PDF et son ancien `SHA256SUMS` par une paire d'une session
antérieure et exigent un rejet pour différence avec la session courante.

- [ ] **Step 9: vérifier les deux PDF**

`pdf_integrity.py` reçoit une CLI `PDF --log LOG --output REPORT`. Elle contrôle
polices, assets, références et avertissements LaTeX et retourne 2 en cas de
défaut.

Run: `.venv/bin/python scripts/pdf_integrity.py build/MANUEL_1SPE/eleve/MANUEL_1SPE_eleve.pdf --log build/MANUEL_1SPE/eleve/MANUEL_1SPE_eleve.log --output build/MANUEL_1SPE/eleve/pdf-report.json && .venv/bin/python scripts/pdf_integrity.py build/MANUEL_1SPE/professeur/MANUEL_1SPE_professeur.pdf --log build/MANUEL_1SPE/professeur/MANUEL_1SPE_professeur.log --output build/MANUEL_1SPE/professeur/pdf-report.json`

Expected: 0 police manquante, 0 asset absent, 0 référence non résolue.

- [ ] **Step 10: vérifier la page légale et l'index dans les deux PDF**

Run: `.venv/bin/python -m pytest tests/test_legal_page_in_pdf.py::test_rejects_real_pdf_containing_isbn -q`

Expected: PASS uniquement si un vrai PDF contenant `ISBN` a été compilé et si
`check_legal_page_in_pdf.py` l'a rejeté avec code 2.

Run: `.venv/bin/python scripts/check_legal_page_in_pdf.py --pdf build/MANUEL_1SPE/eleve/MANUEL_1SPE_eleve.pdf --folios build/MANUEL_1SPE/folios-eleve.json --object-id LEGAL-ELEVE --required "Édité par M&M ACADEMY SUARL sous la marque Nexus Réussite" --required "Manuel élève" --forbidden "Professeur" --forbidden "ISBN" && .venv/bin/python scripts/check_legal_page_in_pdf.py --pdf build/MANUEL_1SPE/professeur/MANUEL_1SPE_professeur.pdf --folios build/MANUEL_1SPE/folios-professeur.json --object-id LEGAL-PROFESSEUR --required "Édité par M&M ACADEMY SUARL sous la marque Nexus Réussite" --required "Professeur" --forbidden "Manuel élève" --forbidden "ISBN"`

Expected: deux codes 0 ; variante correcte sur chaque page légale et chaîne
`ISBN` absente de l'intégralité de chaque PDF.

- [ ] **Step 11: commit**

```bash
git add scripts/release_manifest.py scripts/folio_map.py scripts/check_legal_page_in_pdf.py scripts/assemble_manuel.py scripts/pdf_integrity.py schemas/folio_map.schema.json schemas/build_report.schema.json tests/test_release_manifest.py tests/test_folio_map.py tests/test_legal_page_in_pdf.py tests/fixtures/legal-page-with-isbn.tex tests/test_build_artifact_freshness.py tests/test_assemble_engine.py tests/test_pdf_integrity.py transversal/index_capacites.tex
git commit -m "[1SPE][BAT] assemble les deux ouvrages par manifeste"
```

## Chunk 4: Accessibilité, prépresse, inspection intégrale et remise

### Task 15A: Inventorier et corriger les objets pour l'accessibilité

**Files:**
- Create: `schemas/accessibility_inventory.schema.json`
- Create: `schemas/accessibility_migration.schema.json`
- Create: `publication/migrations/1spe-accessibility.yaml`
- Create: `scripts/build_accessibility_inventory.py`
- Create: `scripts/check_accessibility_contrast.py`
- Create: `scripts/build_reading_order_expectations.py`
- Create: `tests/test_accessibility_inventory.py`
- Modify/Create: exact paths in `publication/migrations/1spe-accessibility.yaml`
- Create: `validations/release-1spe/accessibility-inventory.json`
- Create: `validations/release-1spe/reading-order-expected.json`

- [ ] **Step 1: écrire les tests rouges de couverture**

Les tests exigent un chemin exact pour chaque figure informative, tableau,
formule importante, lien et élément décoratif. Chaque entrée porte rôle,
alternative ou artefact, associations d'en-têtes, séquence logique et SHA-256.
Le test de contraste impose 4,5:1 pour le texte courant, 3:1 pour le grand texte
et les graphiques porteurs d'information.

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_accessibility_inventory.py -q`

Expected: FAIL avec les objets non inventoriés et contrastes insuffisants.

- [ ] **Step 3: générer et valider le manifeste de migration**

Run: `.venv/bin/python scripts/build_accessibility_inventory.py --release release/1spe-2026.yaml --migration publication/migrations/1spe-accessibility.yaml --inventory validations/release-1spe/accessibility-inventory.json`

Expected: code 2 tant qu'un objet manque ; manifeste sans glob et chemins
exacts des sources à modifier.

- [ ] **Step 4: appliquer les corrections listées**

Ajouter alternatives pertinentes, en-têtes de tableaux, représentation
accessible des formules, noms de liens, rôles de titres/listes et marquage des
décors uniquement sur les chemins du manifeste.

- [ ] **Step 5: régénérer puis contrôler contraste et inventaires**

Run: `.venv/bin/python scripts/build_accessibility_inventory.py --release release/1spe-2026.yaml --migration publication/migrations/1spe-accessibility.yaml --inventory validations/release-1spe/accessibility-inventory.json && .venv/bin/python scripts/build_reading_order_expectations.py --release release/1spe-2026.yaml --inventory validations/release-1spe/accessibility-inventory.json --output validations/release-1spe/reading-order-expected.json && .venv/bin/python scripts/check_accessibility_contrast.py --inventory validations/release-1spe/accessibility-inventory.json && .venv/bin/python -m pytest tests/test_accessibility_inventory.py -q`

Expected: code 0 après les corrections, 100 % des objets inventoriés et tous les
seuils respectés. Les tests recalculent les SHA-256 des sources courantes et
refusent tout inventaire ou ordre de lecture antérieur aux corrections.

- [ ] **Step 6: commit exact**

```bash
.venv/bin/python scripts/check_chapter_migration.py publication/migrations/1spe-accessibility.yaml --paths0 | git add --pathspec-from-file=- --pathspec-file-nul
git add schemas/accessibility_inventory.schema.json schemas/accessibility_migration.schema.json publication/migrations/1spe-accessibility.yaml scripts/build_accessibility_inventory.py scripts/check_accessibility_contrast.py scripts/build_reading_order_expectations.py tests/test_accessibility_inventory.py validations/release-1spe/accessibility-inventory.json validations/release-1spe/reading-order-expected.json
git commit -m "[1SPE][BAT] rend les objets accessibles"
```

### Task 15B: Construire et valider automatiquement les PDF écran PDF/UA-1

**Files:**
- Create: `gabarits/nexus-accessibility.tex`
- Create: `schemas/reading_order.schema.json`
- Create: `scripts/build_screen_pdf.py`
- Create: `scripts/check_pdfua.py`
- Create: `scripts/audit_reading_order.py`
- Create: `tests/test_pdfua.py`
- Create: `tests/fixtures/pdfua/valid-minimal.tex`
- Create: `tests/fixtures/pdfua/invalid-untagged.tex`
- Create: `build/release/1SPE-RC0/screen/manuel-1spe-eleve-screen.pdf`
- Create: `build/release/1SPE-RC0/screen/manuel-1spe-professeur-screen.pdf`
- Create: `build/release/1SPE-RC0/screen/verapdf-mrr.xml`
- Create: `build/release/1SPE-RC0/screen/reading-order.json`

- [ ] **Step 1: écrire les tests rouges d'accessibilité**

```python
def test_metadata_are_accessible(screen_pdf):
    assert screen_pdf.lang == "fr-FR"
    assert screen_pdf.author == "Alaeddine BEN RHOUMA"
    assert screen_pdf.title
    assert screen_pdf.is_tagged

def test_verapdf_ua1_has_zero_failures(verapdf_report):
    assert verapdf_report.profile == "ua1"
    assert verapdf_report.failed_checks == 0

def test_accessibility_inventory_is_exhaustive(inventory, manifest):
    assert inventory.figure_ids == manifest.informative_figure_ids
    assert inventory.table_ids == manifest.table_ids
    assert inventory.formula_ids == manifest.important_formula_ids
    assert inventory.missing_alt == []
    assert inventory.unmarked_decorations == []
```

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_pdfua.py -q`

Expected: FAIL sur les PDF actuels non certifiés PDF/UA.

- [ ] **Step 3: activer la production balisée**

Initialiser le document avec le support Tagged PDF de LaTeX, déclarer langue, titre, auteur, structure, titres, listes, tableaux, figures, liens, artefacts et formules accessibles.

- [ ] **Step 4: contrôler structure, signets et navigation**

`check_pdfua.py` contrôle langue, titre, auteur, hiérarchie de titres, signets
cohérents, liens nommés, annotations balisées et absence de piège clavier
détectable. Il rapproche le PDF de l'inventaire complet produit en Task 15A.

- [ ] **Step 5: construire les deux PDF écran**

Run: `.venv/bin/python scripts/build_screen_pdf.py --variants eleve professeur --release 1SPE-RC0`

Expected: les deux PDF aux chemins listés, balisés, sélectionnables,
recherchables, avec signets, liens nommés, titres, listes, tableaux, figures,
formules accessibles et métadonnées.

- [ ] **Step 6: valider avec veraPDF épinglé**

Run: `.venv/bin/python scripts/check_pdfua.py --verapdf-version 1.30.1 --profile ua1 --output build/release/1SPE-RC0/screen/verapdf-mrr.xml build/release/1SPE-RC0/screen/manuel-1spe-eleve-screen.pdf build/release/1SPE-RC0/screen/manuel-1spe-professeur-screen.pdf`

Expected: version 1.30.1 consignée, 2 documents conformes, 0 échec machine.

- [ ] **Step 7: contrôler l'ordre de lecture sur toutes les pages**

Run: `.venv/bin/python scripts/audit_reading_order.py --expected validations/release-1spe/reading-order-expected.json --pdf build/release/1SPE-RC0/screen/manuel-1spe-eleve-screen.pdf --pdf build/release/1SPE-RC0/screen/manuel-1spe-professeur-screen.pdf --output build/release/1SPE-RC0/screen/reading-order.json`

Expected: schéma valide ; pour chaque variante et page, empreinte PDF,
`expected_sequence`, `extracted_sequence` et verdict ; 100 % des séquences
égales, 0 texte essentiel absent.

- [ ] **Step 8: exécuter les tests machine**

Run: `.venv/bin/python -m pytest tests/test_pdfua.py -q`

Expected: PASS uniquement si veraPDF, structure, signets, titres, liens,
inventaire et ordre de lecture sont complets.

- [ ] **Step 9: commit**

```bash
git add gabarits/nexus-accessibility.tex schemas/reading_order.schema.json scripts/build_screen_pdf.py scripts/check_pdfua.py scripts/audit_reading_order.py tests/test_pdfua.py tests/fixtures/pdfua/valid-minimal.tex tests/fixtures/pdfua/invalid-untagged.tex
git commit -m "[1SPE][BAT] valide les pdfua automatiquement"
```

### Task 15C: Certifier les contrôles humains d'accessibilité

**Files:**
- Create: `schemas/accessibility_manual.schema.json`
- Create: `tests/test_accessibility_manual.py`
- Create: `validations/release-1spe/accessibility-manual.md`
- Create: `validations/release-1spe/accessibility-manual.json`

- [ ] **Step 1: écrire le test rouge du protocole humain**

Le schéma exige les douze familles de pages, PDF et SHA-256 courants, outil et
version de lecteur d'écran, navigation clavier, formules, tableaux, liens,
signets, constats, acteur et statut. Aucun champ vide ni preuve périmée ne passe.

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_accessibility_manual.py -q`

Expected: FAIL tant que le contrôle humain n'est pas consigné.

- [ ] **Step 3: exécuter les contrôles non automatisables**

Tester au clavier et avec lecteur d'écran les douze familles, la prononciation
des formules représentatives, tableaux, liens et signets, puis renseigner JSON et
synthèse.

- [ ] **Step 4: agréger le gate accessible**

Run: `.venv/bin/python -m pytest tests/test_accessibility_manual.py tests/test_pdfua.py tests/test_accessibility_inventory.py -q && .venv/bin/python scripts/validate_release_proofs.py --scope accessibility`

Expected: code 0 et gate `accessibility=certified` uniquement si le JSON humain
est courant, conforme et `certified`.

- [ ] **Step 5: commit**

```bash
git add schemas/accessibility_manual.schema.json tests/test_accessibility_manual.py validations/release-1spe/accessibility-manual.md validations/release-1spe/accessibility-manual.json
git commit -m "[1SPE][BAT] certifie l accessibilite humaine"
```

### Task 16: Produire les candidats PDF/X-4 et le préflight local

**Files:**
- Create: `publication/profiles/README.md`
- Create: `publication/profiles/profiles.yaml`
- Create: `publication/profiles/PSOuncoated_v3_FOGRA52.icc`
- Create: `publication/profiles/PSOcoated_v3_FOGRA51.icc`
- Create: `scripts/build_print_master.py`
- Create: `scripts/preflight_pdf.py`
- Create: `scripts/check_ink_coverage.py`
- Create: `scripts/check_print_color.py`
- Create: `schemas/preflight_1spe.schema.json`
- Create: `tests/test_print_master.py`
- Create: `tests/test_preflight_pdf.py`
- Modify: `scripts/pdf_integrity.py`
- Create: `validations/release-1spe/preflight.json`
- Create: `validations/release-1spe/preflight.md`
- Create: `build/release/1SPE-RC0/print/manuel-1spe-eleve-interieur-pdfx4.pdf`
- Create: `build/release/1SPE-RC0/print/manuel-1spe-professeur-interieur-pdfx4.pdf`
- Create: `build/release/1SPE-RC0/print/eleve-preflight.json`
- Create: `build/release/1SPE-RC0/print/professeur-preflight.json`
- Create: `build/release/1SPE-RC0/print/color-report.json`

- [ ] **Step 1: écrire les tests rouges du master**

```python
def test_interior_master_contract(report):
    assert report.trim_mm == [195, 270]
    assert report.output_intent == "PSO Uncoated v3 (FOGRA52)"
    assert report.unembedded_fonts == []
    assert report.rgb_objects == []
    assert report.bleed_mm == 3
    assert report.safe_zone_mm >= 5
    assert report.max_ink_percent <= 300
    assert report.low_resolution_images == []
    assert report.thin_technical_lines == []
    assert report.pdfx_claim == "PDF/X-4"
    assert report.text_not_k_only == []
    assert report.unexpected_rich_black == []
    assert report.unreviewed_overprints == []
    assert report.profile_incompatible_transparency == []
    assert report.local_status == "generated_pdfx4_candidate"
    assert report.independent_pdfx_validation == "blocked"

def test_preflight_rejects_overfull_logs(report):
    assert report.overfull_hbox == 0
    assert report.overfull_vbox == 0
```

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_print_master.py tests/test_preflight_pdf.py -q`

Expected: FAIL car les masters normalisés n'existent pas.

- [ ] **Step 3: implémenter la sortie impression séparée**

L'intérieur est généré comme candidat PDF/X-4 avec PSO Uncoated v3 / FOGRA52 ; la couverture à plat
vise PDF/X-4 avec PSO Coated v3 / FOGRA51. `profiles.yaml` fixe source,
licence, nom, version et SHA-256 des deux ICC ; le build refuse toute empreinte
différente et ne télécharge rien silencieusement.

- [ ] **Step 4: contrôler géométrie et ressources**

Vérifier MediaBox, TrimBox, BleedBox, pages déclarées blanches, polices, images
continues ≥300 ppp, traits ≥0,25 pt, couleurs gérées, noir de texte K seul,
noir enrichi réservé aux grands aplats de couverture, taux d'encrage ≤300 %,
surimpressions révisées et transparences conformes au profil accepté.

- [ ] **Step 5: contrôler les journaux LaTeX**

Refuser `Overfull \hbox`, `Overfull \vbox`, références/citations non résolues, ressources manquantes et substitutions de police.

- [ ] **Step 6: construire les deux intérieurs**

Run: `.venv/bin/python scripts/build_print_master.py --variants eleve professeur --release 1SPE-RC0 --profiles publication/profiles/profiles.yaml --output-dir build/release/1SPE-RC0/print`

Expected: les deux intérieurs PDF/X-4 et deux rapports aux chemins listés ;
MediaBox/BleedBox 201 × 276 mm, TrimBox 195 × 270 mm, fonds perdus 3 mm,
sécurité ≥5 mm. Les couvertures à plat restent bloquées sans dos imprimeur.

- [ ] **Step 7: exécuter le préflight local**

Run: `.venv/bin/python scripts/check_ink_coverage.py --max 300 build/release/1SPE-RC0/print/manuel-1spe-eleve-interieur-pdfx4.pdf build/release/1SPE-RC0/print/manuel-1spe-professeur-interieur-pdfx4.pdf && .venv/bin/python scripts/check_print_color.py --profiles publication/profiles/profiles.yaml --text-black k-only --output build/release/1SPE-RC0/print/color-report.json build/release/1SPE-RC0/print/manuel-1spe-eleve-interieur-pdfx4.pdf build/release/1SPE-RC0/print/manuel-1spe-professeur-interieur-pdfx4.pdf`

Expected: code 0, encrage ≤300 %, noir de texte K seul, zéro RVB non géré,
surimpressions et transparences listées et contrôlées.

Run: `.venv/bin/python scripts/preflight_pdf.py --release 1SPE-RC0 --input-dir build/release/1SPE-RC0/print --output validations/release-1spe/preflight.json --markdown validations/release-1spe/preflight.md`

Expected: 0 défaut numérique local et statut
`generated_pdfx4_candidate`; la conformité complète au standard et
`independent_printer_preflight` restent `blocked` tant qu'un préflight certifié
de l'imprimeur ou pdfToolbox avec version consignée ne les a pas prouvés. Le seul
champ `GTS_PDFXVersion` ne peut jamais certifier.

- [ ] **Step 8: exécuter les tests**

Run: `.venv/bin/python -m pytest tests/test_print_master.py tests/test_preflight_pdf.py tests/test_pdf_integrity.py -q`

Expected: PASS.

- [ ] **Step 9: commit**

```bash
git add publication/profiles/README.md publication/profiles/profiles.yaml publication/profiles/PSOuncoated_v3_FOGRA52.icc publication/profiles/PSOcoated_v3_FOGRA51.icc scripts/build_print_master.py scripts/preflight_pdf.py scripts/check_ink_coverage.py scripts/check_print_color.py schemas/preflight_1spe.schema.json tests/test_print_master.py tests/test_preflight_pdf.py scripts/pdf_integrity.py validations/release-1spe/preflight.json validations/release-1spe/preflight.md
git commit -m "[1SPE][BAT] produit les masters generiques pdfx4"
```

### Task 17: Inspecter visuellement 100 % des pages

**Files:**
- Create: `scripts/render_release_pages.py`
- Create: `scripts/check_page_geometry.py`
- Create: `scripts/build_contact_sheets.py`
- Create: `scripts/check_visual_references.py`
- Create: `scripts/merge_visual_audit.py`
- Create: `scripts/rebuild_after_visual_fix.py`
- Create: `schemas/visual_audit.schema.json`
- Create: `schemas/visual_signatory.schema.json`
- Create: `tests/test_visual_release_audit.py`
- Create: `validations/release-1spe/visual-audit.json`
- Create: `validations/release-1spe/visual-audit.md`
- Create: `validations/release-1spe/visual-signatory.yaml`
- Create: `validations/release-1spe/visual-geometry.json`
- Create: `validations/release-1spe/visual-reference-comparison.json`
- Create: `validations/release-1spe/visual-impact.json`
- Create: `validations/release-1spe/contact-sheets/`
- Create: `validations/release-1spe/contact-sheets/manifest.json`
- Create: `build/release/1SPE-RC0/renders/render-manifest.json`

- [ ] **Step 1: écrire les tests rouges d'exhaustivité**

```python
def test_every_pdf_page_has_a_render(audit):
    assert audit.rendered_pages == audit.pdf_pages

def test_every_page_has_agent_visual_verdict(audit):
    assert all(page.agent_verdict for page in audit.pages)

def test_missing_signatory_verdict_blocks_only_physical_stage(status):
    assert status.digital_candidate == "certified"
    assert status.prototype_approved == "blocked"
```

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_visual_release_audit.py -q`

Expected: FAIL car aucun inventaire intégral n'existe.

- [ ] **Step 3: rasteriser toutes les pages**

Run: `.venv/bin/python scripts/render_release_pages.py --release 1SPE-RC0 --dpi 150 --output-dir build/release/1SPE-RC0/renders --manifest build/release/1SPE-RC0/renders/render-manifest.json`

Expected: une image par page et par variante, nommée par index et SHA-256.

- [ ] **Step 4: contrôler automatiquement la géométrie**

Run: `.venv/bin/python scripts/check_page_geometry.py --render-manifest build/release/1SPE-RC0/renders/render-manifest.json --folios build/MANUEL_1SPE/table-correspondance.json --output validations/release-1spe/visual-geometry.json`

Expected: code 0 ; contenu hors sécurité, coupure, collision, page anormalement
vide, folio absent/dupliqué, format différent et pixels proches du bord tous à
zéro ou explicitement déclarés.

- [ ] **Step 5: produire des planches-contact lisibles**

Run: `.venv/bin/python scripts/build_contact_sheets.py --render-manifest build/release/1SPE-RC0/renders/render-manifest.json --pages-per-sheet 4 --output-dir validations/release-1spe/contact-sheets --manifest validations/release-1spe/contact-sheets/manifest.json`

Expected: quatre pages maximum par planche, une entrée par page et lien vers
chaque rendu pleine taille.

- [ ] **Step 6: effectuer la première passe visuelle**

Un agent inspecte chaque page pleine taille, renseigne `certified|needs_fix`,
catégorie, description, SHA-256 et preuve dans `visual-audit.json`. Aucun
verdict par simple échantillonnage. Le schéma exige exactement une entrée par
page du manifeste de rendu.

- [ ] **Step 7: corriger puis rerendre chaque page affectée**

Chaque correction écrit `visual-impact.json` avec chemins sources exacts,
anciennes/nouvelles empreintes, gates invalidés et preuves dérivées à réécrire,
puis exécute :

Run: `.venv/bin/python scripts/rebuild_after_visual_fix.py --impact validations/release-1spe/visual-impact.json --apply --rerun assembly,folios,accessibility-inventory,reading-order,pdfua,pdfx-local,preflight,render,hashes --invalidate accessibility-manual`

Expected: code 0 pour la reconstruction automatisée ; assemblages, folios,
inventaire, ordre de lecture, PDF/UA, candidat PDF/X-4, préflight, rendus et
empreintes sont rejoués. Si une famille inspectée ou un PDF écran change,
`accessibility-manual.json` passe à `needs_review` et ne peut pas conserver son
ancien SHA-256.

À chaque reconstruction d'au moins un PDF écran, repasser sans transfert de
preuve les contrôles humains de la Task 15C Step 3 sur les douze familles et les
deux PDF, mettre à jour toutes les entrées et empreintes des deux preuves
d'accessibilité, puis exécuter :

Run: `.venv/bin/python -m pytest tests/test_accessibility_manual.py tests/test_pdfua.py tests/test_accessibility_inventory.py -q && .venv/bin/python scripts/validate_release_proofs.py --scope accessibility && .venv/bin/python scripts/rebuild_after_visual_fix.py --impact validations/release-1spe/visual-impact.json --verify-complete`

Expected: code 0 uniquement lorsque toutes les preuves automatisées et humaines
portent les nouvelles empreintes, puis toutes les pages affectées sont revues
sur leur rendu courant. L'option `--paths0` retourne ensuite l'union exacte des
sources corrigées et des preuves dérivées effectivement réécrites.

- [ ] **Step 8: préparer la seconde passe humaine**

Le signataire du BAT dispose d'une liste exhaustive et d'une épreuve.
`visual-signatory.yaml` enregistre ses verdicts réels ; tant qu'ils ne sont pas
consignés, `prototype_approved` et `bat_signed` restent `blocked`, sans dégrader
le gate numérique déjà prouvé.
Le test exige exactement une entrée signataire par page et par empreinte du
candidat physique ; aucune validation partielle ne certifie le prototype.

- [ ] **Step 9: comparer les familles aux témoins V5**

Run: `.venv/bin/python scripts/check_visual_references.py --release 1SPE-RC0 --render-manifest build/release/1SPE-RC0/renders/render-manifest.json --references gabarits/reference-1spe-2026/pages-temoins.yaml --output validations/release-1spe/visual-reference-comparison.json && .venv/bin/python scripts/merge_visual_audit.py --pages validations/release-1spe/visual-audit.json --geometry validations/release-1spe/visual-geometry.json --references validations/release-1spe/visual-reference-comparison.json --output validations/release-1spe/visual-audit.json`

Expected: fusion atomique préservant les verdicts page par page ; 100 % des
familles représentées et 0 régression bloquante.

- [ ] **Step 10: exécuter les tests**

Run: `.venv/bin/python -m pytest tests/test_visual_release_audit.py -q`

Expected: PASS pour l'exhaustivité agent ; statut physique distinct tant que non signé.

- [ ] **Step 11: commit**

```bash
.venv/bin/python scripts/rebuild_after_visual_fix.py --impact validations/release-1spe/visual-impact.json --paths0 | git add --pathspec-from-file=- --pathspec-file-nul
git add scripts/render_release_pages.py scripts/check_page_geometry.py scripts/build_contact_sheets.py scripts/check_visual_references.py scripts/merge_visual_audit.py scripts/rebuild_after_visual_fix.py schemas/visual_audit.schema.json schemas/visual_signatory.schema.json tests/test_visual_release_audit.py validations/release-1spe/visual-audit.json validations/release-1spe/visual-audit.md validations/release-1spe/visual-signatory.yaml validations/release-1spe/visual-geometry.json validations/release-1spe/visual-reference-comparison.json validations/release-1spe/visual-impact.json validations/release-1spe/contact-sheets
git commit -m "[1SPE][BAT] inspecte integralement les pages"
```

### Task 18: Générer la matrice B.O., les rapports finaux et le candidat immuable

**Files:**
- Create: `schemas/bo_matrix.schema.json`
- Create: `schemas/release_candidate.schema.json`
- Create: `scripts/build_bo_matrix.py`
- Create: `scripts/build_release_candidate.py`
- Create: `scripts/check_release_candidate.py`
- Create: `tests/test_bo_matrix.py`
- Create: `tests/test_release_candidate.py`
- Create: `validations/release-1spe/matrice-bo.json`
- Create: `validations/release-1spe/matrice-bo.csv`
- Create: `validations/release-1spe/rapport-final.md`
- Create: `validations/release-1spe/final-compliance-review.json`
- Create: `validations/release-1spe/final-quality-review.json`
- Create: `validations/release-1spe/final-review-impact.json`
- Create: `build/release/1SPE-RC1/screen/manuel-1spe-eleve-screen.pdf`
- Create: `build/release/1SPE-RC1/screen/manuel-1spe-professeur-screen.pdf`
- Create: `build/release/1SPE-RC1/print/manuel-1spe-eleve-interieur-pdfx4-candidate.pdf`
- Create: `build/release/1SPE-RC1/print/manuel-1spe-professeur-interieur-pdfx4-candidate.pdf`
- Create: `build/release/1SPE-RC1/covers/eleve-proof.pdf`
- Create: `build/release/1SPE-RC1/covers/professeur-proof.pdf`
- Create: `build/release/1SPE-RC1/reports/matrice-bo.json`
- Create: `build/release/1SPE-RC1/reports/rapport-final.md`
- Create: `build/release/1SPE-RC1/reports/accessibility.json`
- Create: `build/release/1SPE-RC1/reports/preflight-local.json`
- Create: `build/release/1SPE-RC1/reports/visual-audit.json`
- Create: `build/release/1SPE-RC1/sources/source-manifest.json`
- Create: `build/release/1SPE-RC1/manifest.json`
- Create: `build/release/1SPE-RC1/SHA256SUMS`
- Create: `build/release/current.json`

- [ ] **Step 1: écrire les tests rouges de matrice**

```python
def test_mandatory_programme_is_fully_covered(matrix):
    assert matrix.coverage("mandatory_content") == 1.0
    assert matrix.coverage("prescribed_teaching") == 1.0
    assert matrix.missing_mandatory == []

def test_release_id_binds_commit_and_hashes(manifest):
    assert manifest["release_id"] == "1SPE-RC1"
    assert manifest["git_commit"]
    assert all(item["sha256"] for item in manifest["artifacts"])
```

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_bo_matrix.py tests/test_release_candidate.py -q`

Expected: FAIL car la matrice finale et RC1 n'existent pas.

- [ ] **Step 3: implémenter et construire la matrice B.O.**

Chaque ligne contient `obligation_class`, `bo_page`, `bo_quote`, `manual_object_ids`, `student_folios`, `teacher_folios`, `verdict` et preuves. Les options valent `included`, `excluded_with_rationale` ou `not_applicable`.

Run: `.venv/bin/python scripts/build_bo_matrix.py --programme referentiel/programme_1SPE_2026.json --student-folios build/MANUEL_1SPE/folios-eleve.json --teacher-folios build/MANUEL_1SPE/folios-professeur.json --json validations/release-1spe/matrice-bo.json --csv validations/release-1spe/matrice-bo.csv`

Expected: code 0, schéma valide et 100 % de couverture obligatoire.

- [ ] **Step 4: agréger les rapports**

Le rapport final sépare conformité, mathématiques, pédagogie, langue, visuel, accessibilité, prépresse local et bloqueurs externes. Il ne transforme jamais un `blocked` externe en réussite.

- [ ] **Step 5: tester et committer l'outillage avant de construire RC1**

Run: `.venv/bin/python -m pytest tests/test_bo_matrix.py tests/test_release_candidate.py -q`

Expected: PASS sur fixtures et matrice courante.

```bash
git add schemas/bo_matrix.schema.json schemas/release_candidate.schema.json scripts/build_bo_matrix.py scripts/build_release_candidate.py scripts/check_release_candidate.py tests/test_bo_matrix.py tests/test_release_candidate.py validations/release-1spe/matrice-bo.json validations/release-1spe/matrice-bo.csv validations/release-1spe/rapport-final.md
git commit -m "[1SPE][BAT] prepare le candidat numerique"
```

- [ ] **Step 6: réaliser les deux revues finales avant le gel**

Deux agents distincts examinent le diff complet, la spec, les rapports et les
artefacts RC0, puis écrivent les deux verdicts JSON. Chaque point bloquant est
corrigé, inscrit avec ses chemins exacts et gates invalidés dans
`final-review-impact.json`, puis retesté. Les deux agents relisent les nouvelles
empreintes jusqu'à produire chacun un verdict `certified`.

- [ ] **Step 7: committer revues et corrections**

Run: `.venv/bin/python scripts/rebuild_after_visual_fix.py --impact validations/release-1spe/final-review-impact.json --apply --rerun assembly,folios,accessibility-inventory,reading-order,pdfua,pdfx-local,preflight,render,hashes --invalidate accessibility-manual`

Si au moins un PDF écran est reconstruit, refaire les contrôles humains de la
Task 15C Step 3 sur les douze familles et les deux PDF, sans transférer de
preuve, puis actualiser toutes les entrées et empreintes avant les commandes
suivantes :

Run: `.venv/bin/python -m pytest tests/test_accessibility_manual.py tests/test_pdfua.py tests/test_accessibility_inventory.py -q && .venv/bin/python scripts/validate_release_proofs.py --scope accessibility && .venv/bin/python scripts/rebuild_after_visual_fix.py --impact validations/release-1spe/final-review-impact.json --verify-complete`

Expected: code 0 ; `--paths0` retourne ensuite les sources corrigées et toutes
les preuves dépendantes réécrites.

```bash
.venv/bin/python scripts/rebuild_after_visual_fix.py --impact validations/release-1spe/final-review-impact.json --paths0 | git add --pathspec-from-file=- --pathspec-file-nul
git add validations/release-1spe/final-compliance-review.json validations/release-1spe/final-quality-review.json validations/release-1spe/final-review-impact.json
git commit -m "[1SPE][BAT] archive les revues finales"
```

- [ ] **Step 8: construire RC1 depuis le commit final propre**

Run: `test -z "$(git status --porcelain)" && .venv/bin/python scripts/build_release_candidate.py --release-id 1SPE-RC1`

Expected: refus si le worktree est sale ; sinon tous les artefacts exacts listés,
manifestes et sommes SHA-256 sous `build/release/1SPE-RC1`.

- [ ] **Step 9: vérifier RC1 sans le promouvoir**

Run: `.venv/bin/python scripts/check_release_candidate.py build/release/1SPE-RC1 --require-head`

Expected: tous les artefacts présents, toutes les empreintes exactes, zéro preuve
périmée et commit du candidat égal à `HEAD` ; `current.json` n'est pas encore
modifié.

- [ ] **Step 10: exécuter la suite complète sur RC1**

Run: `make release-test && make check-latex && .venv/bin/python -m pytest tests/test_bo_matrix.py tests/test_release_candidate.py -q`

Expected: PASS.

- [ ] **Step 11: promouvoir RC1 seulement après la suite complète**

Run: `.venv/bin/python scripts/check_release_candidate.py build/release/1SPE-RC1 --write-current build/release/current.json --require-head && .venv/bin/python scripts/check_release_candidate.py --current build/release/current.json --require-head`

Expected: `current.json` pointe sur RC1, son commit et son manifeste seulement
après toutes les vérifications vertes.

- [ ] **Step 12: interdire toute mutation postérieure**

Toute correction ultérieure d'une source, d'un outil de build ou d'une preuve
numérique est committée, génère obligatoirement `1SPE-RC2`, repasse Steps 8–11
et met `current.json` à jour ; RC1 reste immuable. Les preuves externes
postérieures utilisent un registre séparé lié au SHA-256 de RC et ne mutent
jamais le répertoire immuable du candidat.

Run: `.venv/bin/python scripts/check_release_candidate.py --current build/release/current.json --require-head`

Expected: code 0 uniquement si le commit du candidat courant égale `HEAD`;
sinon code 2 exigeant un nouvel identifiant RC.

### Task 19: Outiller le paquet imprimeur sans anticiper les validations physiques

**Files:**
- Create: `schemas/printer_inputs.schema.json`
- Create: `schemas/printer_package.schema.json`
- Create: `schemas/physical_milestone.schema.json`
- Create: `publication/printer-inputs.yaml`
- Create: `publication/printer-package.yaml`
- Create: `validations/release-1spe/printer-acceptance.yaml`
- Create: `validations/release-1spe/prototype-approval.yaml`
- Create: `validations/release-1spe/bat-signature.yaml`
- Create: `scripts/build_printer_package.py`
- Create: `tests/test_printer_inputs.py`
- Create: `tests/test_printer_package.py`
- Create: `docs/publication/cahier-technique-imprimeur.md`
- Create: `docs/publication/proces-verbal-bat.md`
- Create: `docs/publication/checklist-prototype.md`
- Create: `build/printer-package/README.md`
- Create: `build/printer-package/manifest.json`
- Create: `build/printer-package/SHA256SUMS`
- Create: `build/printer-package/blocking-inputs.json`
- Create: `build/printer-package/masters/manuel-1spe-eleve-interieur.pdf`
- Create: `build/printer-package/masters/manuel-1spe-professeur-interieur.pdf`
- Create: `build/printer-package/masters/manuel-1spe-eleve-couverture-a-plat.pdf`
- Create: `build/printer-package/masters/manuel-1spe-professeur-couverture-a-plat.pdf`
- Create conditionally: `build/printer-package/masters/manuel-1spe-eleve-interieur-pdfx1a.pdf`
- Create conditionally: `build/printer-package/masters/manuel-1spe-professeur-interieur-pdfx1a.pdf`
- Create conditionally: `build/printer-package/masters/manuel-1spe-eleve-couverture-a-plat-pdfx1a.pdf`
- Create conditionally: `build/printer-package/masters/manuel-1spe-professeur-couverture-a-plat-pdfx1a.pdf`

- [ ] **Step 1: écrire les tests rouges des jalons**

```python
def test_digital_candidate_does_not_imply_bat_signed(status):
    assert status["digital_candidate"] == "certified"
    assert status["bat_signed"] == "blocked"

def test_flat_cover_requires_printer_spine(package):
    package["spine_width_mm"] = None
    assert validate_printer_package(package).status == "blocked"

def test_generic_package_can_precede_printer_acceptance(status):
    assert status["printer_package"] == "certified"
    assert status["printer_accepted"] == "blocked"

def test_pdfx1a_requires_explicit_acceptance(package):
    package["accepted_pdf_formats"] = ["PDF/X-4"]
    assert build_pdfx1a(package).status == "blocked"

def test_printer_inputs_do_not_claim_final_acceptance(status):
    assert status["printer_inputs"] == "certified"
    assert status["printer_accepted"] == "blocked"
```

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_printer_inputs.py tests/test_printer_package.py -q`

Expected: FAIL car le paquet physique n'est pas formalisé.

- [ ] **Step 3: créer le dossier technique**

Documenter format, papier intérieur, papier couverture, pelliculage, reliure, sens du papier, profils, fonds perdus, traits, encrage, cahiers, tolérances, contrôle des premières feuilles et repli imprimeur.

- [ ] **Step 4: implémenter et générer le paquet générique RC1**

Run: `.venv/bin/python scripts/build_printer_package.py --current build/release/current.json --mode generic --output-dir build/printer-package`

Expected: paquet générique, intérieurs candidats, couvertures de contrôle,
rapports, manifeste, SHA-256,
cahier technique et `blocking-inputs.json` listant exactement les données
externes encore bloquées ; `printer_package=certified` et
`printer_accepted=blocked`.

- [ ] **Step 5: implémenter les branches imprimeur et PDF/X-1a sur fixtures**

Le mode `printer` exige raison sociale, adresse, gabarits, dos, profils,
contraintes de façonnage, `accepted_pdf_formats` et préflight indépendant. Les
tests de fixture vérifient les deux branches exactes :

Run: `.venv/bin/python -m pytest tests/test_printer_package.py -q`

Expected: avec une fixture n'acceptant que `PDF/X-4`, l'appel
`--mode printer --compatibility pdfx1a` retourne code 2 et ne crée aucun des
quatre chemins `*-pdfx1a.pdf`. Avec une fixture qui accepte `PDF/X-1a`, la même
commande retourne code 0 et crée exactement :

```text
build/printer-package/masters/manuel-1spe-eleve-interieur-pdfx1a.pdf
build/printer-package/masters/manuel-1spe-professeur-interieur-pdfx1a.pdf
build/printer-package/masters/manuel-1spe-eleve-couverture-a-plat-pdfx1a.pdf
build/printer-package/masters/manuel-1spe-professeur-couverture-a-plat-pdfx1a.pdf
```

Le mode réel n'est pas exécuté sur RC1 : aucune acceptation, épreuve, prototype
ou signature ne doit précéder le gel final RC2.

- [ ] **Step 6: commit de l'outillage uniquement**

```bash
git add schemas/printer_inputs.schema.json schemas/printer_package.schema.json schemas/physical_milestone.schema.json publication/printer-inputs.yaml publication/printer-package.yaml validations/release-1spe/printer-acceptance.yaml validations/release-1spe/prototype-approval.yaml validations/release-1spe/bat-signature.yaml scripts/build_printer_package.py tests/test_printer_inputs.py tests/test_printer_package.py docs/publication/cahier-technique-imprimeur.md docs/publication/proces-verbal-bat.md docs/publication/checklist-prototype.md build/printer-package/README.md
git commit -m "[1SPE][BAT] outille le paquet imprimeur"
```

### Task 20: Geler RC2, obtenir le BAT physique, puis archiver le dépôt légal

**Files:**
- Modify: `schemas/release_candidate.schema.json`
- Modify: `scripts/build_release_candidate.py`
- Modify: `tests/test_release_candidate.py`
- Create: `schemas/final_release_gate.schema.json`
- Create: `schemas/external_milestones.schema.json`
- Create: `schemas/legal_deposit_gate.schema.json`
- Create: `scripts/final_release_gate.py`
- Create: `tests/test_final_release_gate.py`
- Create: `validations/release-1spe/reviews/final-conformity.json`
- Create: `validations/release-1spe/reviews/final-mathematics.json`
- Create: `validations/release-1spe/reviews/final-editorial.json`
- Create: `validations/release-1spe/reviews/final-prepress.json`
- Modify: `publication/1spe-2026.yaml`
- Modify: `publication/printer-inputs.yaml`
- Modify: `publication/couvertures-1spe-2026.yaml`
- Regenerate: `transversal/mentions_legales_eleve.tex`
- Regenerate: `transversal/mentions_legales_professeur.tex`
- Create: `validations/release-1spe/printer-inputs-impact.json`
- Create: `validations/release-1spe/terminal-review-impact.json`
- Create: `validations/release-1spe/external-milestones.json`
- Create: `validations/release-1spe/legal-deposit-gate.json`
- Create externally: `validations/release-1spe/external/printer-inputs.pdf`
- Create externally: `validations/release-1spe/external/printer-preflight.pdf`
- Create externally: `validations/release-1spe/external/prototype-approval-signed.pdf`
- Create externally: `validations/release-1spe/external/bat-signed.pdf`
- Create: `docs/publication/checklist-depot-legal.md`
- Modify: `publication/suivi-depot-legal-1spe-2026.yaml`
- Create externally: `validations/release-1spe/legal-deposit-eleve.pdf`
- Create externally: `validations/release-1spe/legal-deposit-professeur.pdf`
- Create: `build/release/1SPE-RC2/screen/manuel-1spe-eleve-screen.pdf`
- Create: `build/release/1SPE-RC2/screen/manuel-1spe-professeur-screen.pdf`
- Create: `build/release/1SPE-RC2/print/manuel-1spe-eleve-interieur-pdfx4-candidate.pdf`
- Create: `build/release/1SPE-RC2/print/manuel-1spe-professeur-interieur-pdfx4-candidate.pdf`
- Create: `build/release/1SPE-RC2/covers/eleve-proof.pdf`
- Create: `build/release/1SPE-RC2/covers/professeur-proof.pdf`
- Create: `build/release/1SPE-RC2/reports/matrice-bo.json`
- Create: `build/release/1SPE-RC2/reports/rapport-final.md`
- Create: `build/release/1SPE-RC2/reports/accessibility.json`
- Create: `build/release/1SPE-RC2/reports/preflight-local.json`
- Create: `build/release/1SPE-RC2/reports/visual-audit.json`
- Create: `build/release/1SPE-RC2/reports/final-gate.json`
- Create: `build/release/1SPE-RC2/sources/source-manifest.json`
- Create: `build/release/1SPE-RC2/manifest.json`
- Create: `build/release/1SPE-RC2/SHA256SUMS`
- Modify: `build/release/current.json`
- Modify: `RAPPORT_FINAL_1SPE.md`
- Modify: `ETAT_COLLECTION.md`
- Modify: `MISSION_LOG.md`

- [ ] **Step 1: écrire les tests rouges des trois registres**

```python
def test_no_known_digital_defect_can_pass(release):
    release["proofs"][0]["status"] = "needs_fix"
    assert final_gate(release, stage="digital").digital_candidate == "needs_fix"

def test_immutable_digital_gate_does_not_claim_external_milestones(report):
    assert report["scope"] == "digital_immutable"
    assert "printer_accepted" not in report["statuses"]
    assert "bat_signed" not in report["statuses"]

def test_external_milestones_bind_exact_release_sha(external, current):
    assert external["release_id"] == current["release_id"]
    assert external["release_manifest_sha256"] == current["manifest_sha256"]

def test_external_merge_preserves_unmentioned_statuses(previous, publication_update):
    updated = merge_external(previous, publication_update)
    assert updated["printer_accepted"] == previous["printer_accepted"]
    assert updated["prototype_approved"] == previous["prototype_approved"]
    assert updated["bat_signed"] == previous["bat_signed"]

def test_changed_package_hash_invalidates_downstream_milestones(external):
    changed = merge_external(external, package_sha256="different")
    assert changed["printer_accepted"] == "blocked"
    assert changed["prototype_approved"] == "blocked"
    assert changed["bat_signed"] == "blocked"

def test_legal_deposit_needs_four_copies_and_receipt_per_book(release):
    release["deposit"]["eleve"] = {"copies": 4, "receipt_path": None}
    release["deposit"]["professeur"] = {"copies": 4, "receipt_path": None}
    assert final_gate(release, stage="legal-deposit").legal_deposit_completed == "blocked"
```

- [ ] **Step 2: vérifier l'échec**

Run: `.venv/bin/python -m pytest tests/test_final_release_gate.py -q`

Expected: FAIL car les trois schémas et le gate n'existent pas.

- [ ] **Step 3: implémenter le gate numérique et les registres dynamiques**

Le mode `digital` vérifie programme, preuves, commit, sommes, deux variantes,
couvertures, accessibilité, prépresse local, pages et mentions légales. Son
rapport immuable ne prétend jamais connaître le paquet imprimeur. Les modes
`physical`, `publication` et `legal-deposit` mettent à jour des preuves
distinctes, toujours liées à `release_id` et au SHA-256 du manifeste courant.
Tout statut appartient à `certified|needs_fix|blocked`.

Chaque écriture de `external-milestones.json` relit l'état précédent, valide la
transition, conserve les jalons non concernés tant que release et paquet sont
identiques, écrit dans un fichier temporaire, `fsync`, puis remplace
atomiquement la cible. Un changement de SHA du paquet invalide automatiquement
`printer_accepted`, `prototype_approved`, `bat_signed` et `made_available`. Les
tests interrompent une écriture simulée et prouvent que le dernier JSON valide
reste intact.

Le manifeste RC2 exclut uniquement l'allowlist postrelease exacte suivante et
en consigne la liste dans `postrelease_excluded_paths` :

```text
validations/release-1spe/printer-acceptance.yaml
validations/release-1spe/prototype-approval.yaml
validations/release-1spe/bat-signature.yaml
validations/release-1spe/visual-signatory.yaml
validations/release-1spe/external-milestones.json
validations/release-1spe/external/printer-preflight.pdf
validations/release-1spe/external/prototype-approval-signed.pdf
validations/release-1spe/external/bat-signed.pdf
publication/suivi-depot-legal-1spe-2026.yaml
validations/release-1spe/legal-deposit-eleve.pdf
validations/release-1spe/legal-deposit-professeur.pdf
validations/release-1spe/legal-deposit-gate.json
```

Le schéma et `tests/test_release_candidate.py` exigent cette égalité exacte,
interdisent glob et chemin supplémentaire. `publication/printer-package.yaml`
reste immuable et inclus dans le manifeste source numérique.
`publication/printer-inputs.yaml` et sa preuve
`validations/release-1spe/external/printer-inputs.pdf` ne sont pas dans
l'allowlist : ils doivent être figés avant RC2 et figurent dans son manifeste
source.

- [ ] **Step 4: figer les données préproduction avant la revue finale**

Obtenir de l'imprimeur raison sociale, adresse, lieu/pays d'impression, gabarits,
dos, profils, façonnage, tirage, date d'impression prévue et formats acceptés,
avec une pièce datée archivée au chemin exact listé. Renseigner
`publication/printer-inputs.yaml`, `publication/1spe-2026.yaml` et le YAML des
couvertures ; le statut `printer_inputs=certified` ne vaut pas acceptation du
paquet final.

Run: `.venv/bin/python scripts/check_publication_metadata.py --metadata publication/1spe-2026.yaml --printer-inputs publication/printer-inputs.yaml --deposit-tracking publication/suivi-depot-legal-1spe-2026.yaml --stage bat && .venv/bin/python scripts/render_legal_page.py --metadata publication/1spe-2026.yaml --printer-inputs publication/printer-inputs.yaml --variant eleve --stage bat --output transversal/mentions_legales_eleve.tex && .venv/bin/python scripts/render_legal_page.py --metadata publication/1spe-2026.yaml --printer-inputs publication/printer-inputs.yaml --variant professeur --stage bat --output transversal/mentions_legales_professeur.tex && .venv/bin/python scripts/build_covers_1spe.py --mode printer-flat --variants eleve professeur --printer-inputs publication/printer-inputs.yaml --output-dir build/covers-1spe-2026 --report build/covers-1spe-2026/report.json`

Expected: deux pages légales complètes, sans ISBN, avec
`digital_content_status=certified` et
`physical_completion_status=certified`, plus deux couvertures à plat utilisant
le dos prouvé. `printer_accepted`, `prototype_approved` et `bat_signed` restent
`blocked`.

Inscrire les chemins et gates affectés dans `printer-inputs-impact.json`, puis
exécuter :

Run: `.venv/bin/python scripts/rebuild_after_visual_fix.py --impact validations/release-1spe/printer-inputs-impact.json --apply --rerun assembly,folios,accessibility-inventory,reading-order,pdfua,pdfx-local,preflight,render,hashes --invalidate accessibility-manual`

Refaire ensuite les contrôles humains de la Task 15C Step 3 sur les douze
familles et les deux PDF reconstruits, mettre à jour toutes les empreintes, puis
exécuter :

Run: `.venv/bin/python scripts/rebuild_after_visual_fix.py --impact validations/release-1spe/printer-inputs-impact.json --verify-complete`

Expected: code 0 et aucune preuve numérique antérieure aux données imprimeur.

- [ ] **Step 5: faire la dernière revue indépendante et fermer ses impacts**

Un agent de conformité, un agent mathématique, un agent éditorial et un agent
prépresse vérifient chacun leur périmètre et produisent les quatre JSON listés.
Aucun ne valide une correction qu'il a lui-même produite. Toute correction est
inscrite avec chemins exacts et gates invalidés dans
`terminal-review-impact.json`, reconstruite par
`rebuild_after_visual_fix.py`, puis relue sur les nouvelles empreintes jusqu'à
quatre verdicts `certified`. L'impact recense également chaque preuve dépendante
réécrite afin que `--paths0` puisse tout ajouter au commit.

- [ ] **Step 6: mettre à jour les rapports de collection**

Remplacer les anciennes affirmations contradictoires par les statuts prouvés,
les bloqueurs externes éventuels et la procédure suivante.

- [ ] **Step 7: tester et committer le dernier état éditorial**

Run: `.venv/bin/python scripts/rebuild_after_visual_fix.py --impact validations/release-1spe/terminal-review-impact.json --apply --rerun assembly,folios,accessibility-inventory,reading-order,pdfua,pdfx-local,preflight,render,hashes --invalidate accessibility-manual`

Si au moins un PDF écran est reconstruit, refaire la Task 15C Step 3 sur les
douze familles et les deux PDF, sans transfert de preuve, actualiser toutes ses
entrées et empreintes, puis continuer.

Run: `.venv/bin/python scripts/rebuild_after_visual_fix.py --impact validations/release-1spe/terminal-review-impact.json --verify-complete && make release-test && git diff --check`

Expected: PASS et aucune preuve périmée.

```bash
.venv/bin/python scripts/rebuild_after_visual_fix.py --impact validations/release-1spe/printer-inputs-impact.json --paths0 | git add --pathspec-from-file=- --pathspec-file-nul
.venv/bin/python scripts/rebuild_after_visual_fix.py --impact validations/release-1spe/terminal-review-impact.json --paths0 | git add --pathspec-from-file=- --pathspec-file-nul
git add schemas/release_candidate.schema.json scripts/build_release_candidate.py tests/test_release_candidate.py schemas/final_release_gate.schema.json schemas/external_milestones.schema.json schemas/legal_deposit_gate.schema.json scripts/final_release_gate.py tests/test_final_release_gate.py publication/1spe-2026.yaml publication/printer-inputs.yaml publication/couvertures-1spe-2026.yaml transversal/mentions_legales_eleve.tex transversal/mentions_legales_professeur.tex validations/release-1spe/printer-inputs-impact.json validations/release-1spe/external/printer-inputs.pdf validations/release-1spe/reviews/final-conformity.json validations/release-1spe/reviews/final-mathematics.json validations/release-1spe/reviews/final-editorial.json validations/release-1spe/reviews/final-prepress.json validations/release-1spe/terminal-review-impact.json docs/publication/checklist-depot-legal.md RAPPORT_FINAL_1SPE.md ETAT_COLLECTION.md MISSION_LOG.md
git commit -m "[1SPE][BAT] clot la verification editoriale"
```

- [ ] **Step 8: construire RC2 et son gate numérique immuable**

Run: `test -z "$(git status --porcelain)" && .venv/bin/python scripts/build_release_candidate.py --release-id 1SPE-RC2 --stage print --run-digital-gate --digital-gate-output build/release/1SPE-RC2/reports/final-gate.json`

Expected: refus si le worktree est sale ; sinon l'arborescence RC2 contient
exactement les deux PDF écran, deux intérieurs, deux couvertures de contrôle,
six rapports dont `final-gate.json`, le manifeste source, `manifest.json` et
`SHA256SUMS` listés ci-dessus. Le gate porte `scope=digital_immutable` et
`digital_candidate=certified`, sans statut physique.

- [ ] **Step 9: vérifier intégralement RC2 avant promotion**

Run: `.venv/bin/python scripts/check_release_candidate.py build/release/1SPE-RC2 --require-head && make release-test && make check-latex && .venv/bin/python -m pytest tests/test_final_release_gate.py tests/test_release_candidate.py -q`

Expected: tous les artefacts exacts présents, empreintes correctes, commit égal
à `HEAD`, zéro preuve périmée et suite complète verte.

- [ ] **Step 10: promouvoir RC2 seulement après les contrôles**

Run: `.venv/bin/python scripts/check_release_candidate.py build/release/1SPE-RC2 --write-current build/release/current.json --require-head && .venv/bin/python scripts/check_release_candidate.py --current build/release/current.json --require-head`

Expected: `current.json` pointe sur RC2 et son SHA-256. RC2 devient immuable ;
toute correction numérique impose RC3 et invalide par défaut les jalons
externes. Les seuls commits autorisés sans RC3 sont les preuves externes et le
suivi postpublication explicitement listés aux Steps 11–14 ; le gate vérifie que
le manifeste source de RC2 est inchangé.

- [ ] **Step 11: reconstruire le paquet générique pour RC2**

Run: `.venv/bin/python scripts/build_printer_package.py --current build/release/current.json --mode generic --output-dir build/printer-package && .venv/bin/python scripts/final_release_gate.py --current build/release/current.json --stage physical --printer-package build/printer-package/manifest.json --output validations/release-1spe/external-milestones.json`

Expected: paquet lié au SHA-256 de RC2,
`printer_package=certified`, puis `printer_accepted=blocked`,
`prototype_approved=blocked` et `bat_signed=blocked`. Ce registre dynamique ne
modifie ni RC2 ni son `final-gate.json`.

- [ ] **Step 12: intégrer l'acceptation et le préflight réels de l'imprimeur**

Renseigner `printer-acceptance.yaml` avec raison sociale, adresse, gabarits,
dos, profils, façonnage, `accepted_pdf_formats`, acteur, date, SHA-256 de RC2 et
du paquet, puis archiver le préflight indépendant reçu au chemin exact listé.
Ces champs doivent être strictement égaux aux `printer-inputs` figés ; tout
écart bloque l'acceptation et impose RC3.

Run: `.venv/bin/python scripts/build_printer_package.py --current build/release/current.json --mode printer --output-dir build/printer-package`

Expected: les quatre masters PDF/X-4 exacts listés en Task 19 et
`printer_accepted=certified` uniquement si toutes les données et le préflight
indépendant sont prouvés.

Uniquement si `accepted_pdf_formats` contient `PDF/X-1a`, exécuter :

Run: `.venv/bin/python scripts/build_printer_package.py --current build/release/current.json --mode printer --compatibility pdfx1a --output-dir build/printer-package`

Expected: code 0 et exactement les quatre masters `*-pdfx1a.pdf` listés en
Task 19. Sans acceptation explicite, ne pas lancer cette branche ; le test de
Task 19 garantit code 2 et absence de sortie.

Run: `.venv/bin/python scripts/final_release_gate.py --current build/release/current.json --stage physical --printer-package build/printer-package/manifest.json --output validations/release-1spe/external-milestones.json`

Expected: registre lié à RC2 ; aucun statut non prouvé n'est promu.

- [ ] **Step 13: approuver le prototype puis signer le BAT sur RC2**

Contrôler 100 % de l'épreuve avec `checklist-prototype.md`, compléter
`visual-signatory.yaml` sur chaque page et empreinte, archiver le scan signé du
prototype, puis renseigner `prototype-approval.yaml`. Ensuite seulement,
compléter le procès-verbal, archiver le BAT signé et renseigner
`bat-signature.yaml`, tous liés au même SHA-256 de paquet.

Run: `.venv/bin/python scripts/final_release_gate.py --current build/release/current.json --stage physical --printer-package build/printer-package/manifest.json --output validations/release-1spe/external-milestones.json && .venv/bin/python -m pytest tests/test_printer_package.py tests/test_final_release_gate.py tests/test_visual_release_audit.py -q`

Expected: `prototype_approved=certified` puis `bat_signed=certified` uniquement
avec les scans réels, signataires habilités, contrôle visuel exhaustif et
empreintes RC2 identiques. Sinon le jalon reste `blocked`.

```bash
git add validations/release-1spe/printer-acceptance.yaml validations/release-1spe/prototype-approval.yaml validations/release-1spe/bat-signature.yaml validations/release-1spe/visual-signatory.yaml validations/release-1spe/external-milestones.json validations/release-1spe/external/printer-preflight.pdf validations/release-1spe/external/prototype-approval-signed.pdf validations/release-1spe/external/bat-signed.pdf
git commit -m "[1SPE][BAT] archive les validations physiques de RC2"
```

- [ ] **Step 14: enregistrer la mise à disposition et le dépôt légal**

Le mode `publication` n'accepte la mise à disposition à Nexus Réussite qu'avec
`bat_signed=certified` sur RC2 :

Run: `.venv/bin/python scripts/final_release_gate.py --current build/release/current.json --stage publication --printer-package build/printer-package/manifest.json --output validations/release-1spe/external-milestones.json`

Après cette date, déposer dans le délai légal quatre exemplaires élève et quatre
professeur. Renseigner séparément copies, dates, SHA-256 et chemins des deux
récépissés dans `publication/suivi-depot-legal-1spe-2026.yaml`, puis exécuter :

Run: `.venv/bin/python scripts/final_release_gate.py --current build/release/current.json --deposit-tracking publication/suivi-depot-legal-1spe-2026.yaml --stage legal-deposit --output validations/release-1spe/legal-deposit-gate.json`

Expected: `legal_deposit_completed=certified` uniquement après les deux dépôts
de quatre exemplaires et les deux récépissés ; le verdict archivé contient leurs
SHA-256 et celui du manifeste RC2.

```bash
git add validations/release-1spe/external-milestones.json publication/suivi-depot-legal-1spe-2026.yaml validations/release-1spe/legal-deposit-eleve.pdf validations/release-1spe/legal-deposit-professeur.pdf validations/release-1spe/legal-deposit-gate.json
git commit -m "[1SPE][LEGAL] archive le depot legal"
```

- [ ] **Step 15: appliquer @superpowers:verification-before-completion**

Conserver les sorties fraîches de tests, builds, préflights, revues et sommes ;
annoncer précisément le plus haut jalon réellement atteint, sans assimiler
`digital_candidate`, `printer_package`, `printer_accepted`,
`prototype_approved`, `bat_signed`, `made_available` et
`legal_deposit_completed`.
