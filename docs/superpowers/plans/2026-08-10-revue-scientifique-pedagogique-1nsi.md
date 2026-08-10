# 1NSI Scientific and Pedagogical Review Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** produire une revue scientifique et pedagogique tracable des 339 objets et 10 contrats 1NSI, sans modifier leurs statuts, sans auto-approbation et sans toucher a TNSI.

**Architecture:** une politique YAML ferme les sources officielles, la matrice de capacites et les regles de verdict. Des constats de relecture structures, produits en lecture seule par chapitre, alimentent un generateur deterministe qui enrichit chaque entree avec le chemin, le statut et le digest observes, puis emet un registre JSON valide et une synthese Markdown. Les tests comparent les 349 entrees aux sources reelles et interdisent toute approbation implicite.

**Tech Stack:** Python 3.12, pytest, PyYAML, JSON Schema Draft 2020-12, LaTeX source inspection, Git.

**Design:** `docs/superpowers/specs/2026-08-10-revue-scientifique-pedagogique-1nsi-design.md`

---

## Preflight obligatoire

Avant Task 1, enregistrer les sorties de :

```bash
git status --short --branch
git rev-parse HEAD
git log --oneline --decorate -15
git diff --stat
git diff --check
```

Ne pas poursuivre si un WIP non audite apparait. Le HEAD propre qui suit le
commit de ce plan devient `implementation_base_sha` dans la politique.

## Chunk 1: Contrat executable de revue

### Task 1: Verrouiller la politique, le schema et le generateur

**Files:**
- Create: `NSI/tests/test_1nsi_content_reviews.py`
- Create: `scripts/review_1nsi_content.py`
- Create: `audit/1NSI_CONTENT_REVIEW_POLICY.yaml`
- Create: `audit/schemas/v1/1nsi-content-review.schema.json`
- Create: `audit/sources/1nsi/programme-premiere-nsi.pdf`
- Create: `audit/sources/1nsi/legifrance-arrete-17-janvier-2019.html`
- Create: `audit/sources/1nsi/eduscol-programmes-nsi.html`

- [ ] **Step 1: Write failing policy and discovery tests**

Tester que la politique porte `manual: 1NSI`, la decision humaine du
10 aout 2026, les trois sources officielles, le digest du PDF, les quatre
verdicts admis, `publication_approval: false`,
`human_confirmation_required: true` et les transitions prohibees. Exiger une
matrice fermant toutes les references des dix contrats et signalant toute
reference locale ou tout enrichissement non etiquete.

Figer localement les octets effectivement consultes des trois sources
officielles. Inclure leurs SHA-256 et ceux des cinq documents contractuels
locaux dans un `protocol_digest` : `NSI/docs/01_conception_manuel.md`,
`NSI/docs/02_workflow_production.md`, `NSI/docs/05_conventions_latex.md`,
`docs/codex/QUALITY_GATES.md` et
`docs/codex/ISSUE_REGISTER_TEMPLATE.md`. Tester qu'une mutation de l'une de ces
huit sources invalide les 349 revues.

Tester ensuite `discover_sources()` : exactement 339 objets META et 10
contrats, chemins uniquement `NSI/chapitres/1NSI-*`, identifiants uniques,
statuts observes 163/169/7 et 10 `draft`, aucun TNSI.

Figer dans `scope_guard` la table canonique exacte
`ID -> chemin -> statut`, et non ses seuls comptes, ainsi que les SHA-256 de
`audit/BUILD_MANIFEST.json`, des sept PDF canoniques et l'empreinte agregee de
tous les fichiers Git suivis sous les chapitres TNSI. Tester toute permutation
de statuts, modification de chemin, derive TNSI/PDF/manifeste et tout fichier
modifie hors allowlist depuis `implementation_base_sha`.

- [ ] **Step 2: Run tests and verify RED**

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py -k 'policy or discover'
```

Expected: FAIL because the files and module do not exist.

- [ ] **Step 3: Implement the minimal closed policy and discovery API**

Ecrire une politique sans verdict de contenu. Rattacher chaque reference
contractuelle a une rubrique et une capacite du programme officiel ; marquer
explicitement les references locales de `1NSI-TYPES-CONSTRUITS` et les ajouts
transversaux qui exigent une decision. Dans le script, parser les META avec la
meme convention que les tests NSI, charger les contrats YAML et calculer les
SHA-256 a partir des octets lus.

- [ ] **Step 4: Write failing schema and generation tests**

Exiger un schema ferme (`additionalProperties: false`) couvrant les 349
entrees, les deux dimensions, les constats, les anomalies, la provenance, les
digests, `publication_approval: false` et
`human_confirmation_required: true`. Tester que le generateur refuse : entree
manquante, doublon, digest fourni par le relecteur, verdict sans justification,
`pass` avec anomalie dans la meme dimension, chemin TNSI, approbation vraie et
reference contractuelle inconnue.

Exiger pour chaque dimension une preuve structuree composee d'un chemin, de
lignes debut/fin, d'un SHA-256 des octets ancres, d'un type de fait ferme et
d'une observation propre a l'objet. Rejeter les preuves qui ne pointent pas sur
la source ou une dependance declaree, les observations normalisees dupliquees
dans un chapitre, un digest d'extrait faux, un relecteur identique a
l'integrateur et une provenance sans `reviewer_id`, `review_run_id` et
`reviewer_model`.

- [ ] **Step 5: Run tests and verify RED**

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py -k 'schema or reject or generate'
```

Expected: FAIL because validation and generation are not implemented.

- [ ] **Step 6: Implement validation and deterministic rendering**

Ajouter des fonctions pures pour charger les constats, verifier leur couverture,
enrichir les 349 sources et rendre le JSON/Markdown. Ajouter une CLI
`--findings`, `--output-json`, `--output-summary`, `--check`,
`--verify-scope` et `--release-gate`. Les sorties sont ordonnees par chapitre,
scope et identifiant ; `--check` compare les octets sans reecrire.

Le generateur calcule aussi, pour chaque entree, un digest agrege ferme du
`protocol_digest` et de tout
ce qui a ete lu : source, contrat, objet lie dans les deux sens, aide, corrige,
receipt d'execution et fichier Python reference. Tester qu'une mutation de
chaque classe de dependance invalide l'entree. Les pages officielles sont
referencees avec date de consultation et leurs snapshots, dont le PDF officiel,
sont controles contre les octets et les SHA-256 figes dans la politique.

Pour chaque objet contenant `BEGIN-VERIFY`, `BEGIN-TRACE` ou un environnement
Python, reexecuter `NSI/scripts/verify_python.py::check_object` sans ecrire de
receipt, comparer les sorties et enregistrer le verdict frais ainsi que le
digest du controle. Un echec ou une divergence avec le receipt existant devient
une anomalie scientifique bloquante.

- [ ] **Step 7: Verify and commit**

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py -k 'policy or discover or schema or reject or generate'
git diff --check
git status --short
git add NSI/tests/test_1nsi_content_reviews.py scripts/review_1nsi_content.py audit/1NSI_CONTENT_REVIEW_POLICY.yaml audit/schemas/v1/1nsi-content-review.schema.json audit/sources/1nsi
git commit -m "[AUDIT] verrouille le protocole de revue 1NSI"
```

## Chunk 2: Revue des contrats et du programme

### Task 2: Examiner les dix contrats 1NSI

**Files:**
- Create: `audit/reviews/1nsi/runs/<run-id>-contrats.yaml`
- Create: `audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml`
- Modify: `NSI/tests/test_1nsi_content_reviews.py`

- [ ] **Step 1: Write the failing contract-review test**

Exiger exactement dix constats `scope: contract`, chacun avec relecteur,
date, digest de protocole, verdict scientifique, verdict pedagogique,
preuves localisees distinctes par dimension et liste d'anomalies. Exiger qu'une
reference locale ou une capacite sans rattachement officiel exact ne puisse
obtenir un `pass` scientifique silencieux. Verifier que le relecteur est
distinct de l'integrateur et que sa provenance de run est complete. Les
constats doivent etre derives d'un recu de run scelle dont le digest est
enregistre, jamais saisis directement par l'integrateur.

- [ ] **Step 2: Run the test and verify RED**

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py -k 'contract_findings'
```

Expected: FAIL because no findings file exists.

- [ ] **Step 3: Perform independent contract and curriculum review**

Faire relire en lecture seule les dix contrats contre le PDF officiel et les
documents contractuels locaux. Consigner pour chaque capacite la source, la
portee obligatoire ou enrichissement, et toute discordance. Ne modifier aucun
contrat et ne resoudre aucune ambiguite disciplinaire par auto-approbation.

Enregistrer la reponse brute structuree du relecteur dans un recu de run avec
l'assignation, l'identite d'agent, le modele, le `protocol_digest`, la liste des
sources et une preuve ancree par dimension et contrat. Verifier les ancres puis
committer ce recu avant de produire les constats integres ; son SHA-256 devient
immuable pour la suite de la passe.

```bash
git add audit/reviews/1nsi/runs/<run-id>-contrats.yaml
git diff --cached --check
git commit -m "[AUDIT] scelle la revue des contrats 1NSI"
```

- [ ] **Step 4: Record the ten contract findings**

Creer le fichier de constats avec les dix entrees de contrat seulement. Toute
anomalie comporte un identifiant stable `1NSI-REV-*`, une severite, une
dimension, un emplacement, une preuve, une consequence et une action attendue.
Chaque constat reference le SHA-256 du recu et le SHA Git du commit de scellement.

- [ ] **Step 5: Verify and commit**

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py -k 'contract_findings or policy'
git diff --check
git add audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml NSI/tests/test_1nsi_content_reviews.py
git commit -m "[PROGRAMME] consigne la revue des contrats 1NSI"
```

## Chunk 3: Revue exhaustive des objets

### Task 3: Examiner les 339 objets par lots independants

**Files:**
- Create: `audit/reviews/1nsi/runs/<run-id>-<lot>.yaml`
- Modify: `audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml`
- Modify: `NSI/tests/test_1nsi_content_reviews.py`

- [ ] **Step 1: Write the failing exhaustive-coverage test**

Exiger exactement une entree `scope: object` pour chaque objet decouvert, soit
339 entrees sans doublon. Chaque entree porte deux verdicts justifies. Une
anomalie scientifique ou pedagogique impose `issue` dans sa dimension ; un
point sensible non tranche impose `human_confirmation_required`.

Exiger au moins une preuve localisee distincte par dimension, interdire les
observations normalisees recopiees dans un meme chapitre, verifier le SHA-256
des extraits ancres et verifier que les preuves appartiennent au graphe de
dependances ferme de l'objet. Chaque constat doit pointer vers un recu de run
deja scelle et au digest exact.

- [ ] **Step 2: Run the test and verify RED**

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py -k 'object_findings or exhaustive'
```

Expected: FAIL with 339 object findings missing.

- [ ] **Step 3: Dispatch read-only chapter reviews**

Repartir les dix chapitres entre relecteurs independants. Isoler
`1NSI-TYPES-CONSTRUITS` dans un lot dedie. Chaque relecteur lit tous les `.tex`
du lot, les contrats, les liens exercice/aide/corrige, les recus Python et les
regles eleve/professeur, puis rend une ligne structuree par objet avec type de
fait, lignes, digest de l'extrait et observation specifique. Les
relecteurs ne modifient aucun fichier et ne declarent aucune approbation.

Materialiser leurs reponses en recus de run disjoints, verifier toutes les
ancres, puis committer les recus avant integration dans le fichier de constats.
Un constat integre sans recu scelle ou dont le digest diverge est refuse.

```bash
git add audit/reviews/1nsi/runs/<run-id>-*.yaml
git diff --cached --check
git commit -m "[AUDIT] scelle les revues des objets 1NSI"
```

- [ ] **Step 4: Integrate findings without blanket verdicts**

Ajouter les 339 constats. Une justification doit citer un fait propre a l'objet
ou son role verifie dans une chaine pedagogique ; interdire une justification
generique recopiee sur tout un chapitre. Conserver les anomalies avec leur
preuve localisee. Tracer `reviewer_id`, `review_run_id`, `reviewer_model` et
`integrator_id` ; le relecteur et l'integrateur doivent etre differents. Ne
corriger aucun contenu dans ce commit. Chaque constat reference le SHA-256 du
recu et le SHA Git du commit de scellement.

- [ ] **Step 5: Verify chapter counts and invariants**

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py -k 'object_findings or exhaustive or no_tnsi or no_approval'
git diff --check
git status --short
```

Expected: PASS with 339 object findings and 10 contract findings.

- [ ] **Step 6: Commit**

```bash
git add audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml NSI/tests/test_1nsi_content_reviews.py
git commit -m "[PEDAGOGIE] consigne la revue exhaustive des objets 1NSI"
```

## Chunk 4: Registre probant et gates

### Task 4: Generer, verifier et publier les preuves d'audit

**Files:**
- Create: `audit/1NSI_CONTENT_REVIEWS.json`
- Create: `audit/1NSI_CONTENT_REVIEW_SUMMARY.md`

- [ ] **Step 1: Generate the canonical artifacts**

```bash
python3 scripts/review_1nsi_content.py \
  --findings audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml \
  --output-json audit/1NSI_CONTENT_REVIEWS.json \
  --output-summary audit/1NSI_CONTENT_REVIEW_SUMMARY.md
```

Inspecter les comptes par chapitre, type et verdict. Verifier que chaque
anomalie de la synthese existe dans le registre et que la synthese n'emploie ni
`approved`, ni une formulation de publication.

- [ ] **Step 2: Prove idempotence and schema validity**

```bash
python3 scripts/review_1nsi_content.py \
  --findings audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml \
  --output-json audit/1NSI_CONTENT_REVIEWS.json \
  --output-summary audit/1NSI_CONTENT_REVIEW_SUMMARY.md --check --verify-scope
pytest -q NSI/tests/test_1nsi_content_reviews.py
```

Expected: PASS, exactly 349 entries, no stale digest and no output diff.

- [ ] **Step 3: Commit the generated evidence**

```bash
git add audit/1NSI_CONTENT_REVIEWS.json audit/1NSI_CONTENT_REVIEW_SUMMARY.md
git diff --cached --check
git commit -m "[AUDIT] publie les preuves de revue 1NSI"
```

- [ ] **Step 4: Run affected suites and collection gates**

```bash
pytest -q NSI/tests/test_1nsi_content_reviews.py NSI/tests/test_1nsi_status_governance.py NSI/tests/test_meta_schemas.py
pytest -q NSI/tests
pytest -q tests/test_inventory_collection.py
python3 scripts/inventory_collection.py --check
python3 scripts/inventory_collection.py --validate-model
python3 scripts/inventory_collection.py --fail-on-new
python3 scripts/inventory_collection.py --release-strict
python3 scripts/review_1nsi_content.py \
  --findings audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml \
  --output-json audit/1NSI_CONTENT_REVIEWS.json \
  --output-summary audit/1NSI_CONTENT_REVIEW_SUMMARY.md \
  --check --verify-scope --release-gate
git diff --check
git status --short --branch
```

Expected: targeted and full tests green ; `--check`, `--validate-model` et
`--fail-on-new` verts. Ne pas pretendre que ces gates connaissent les nouvelles
anomalies de revue. `--release-strict` reste exit 7 sur ses bloqueurs reels
existants. Le gate dedie `--release-gate` reste rouge tant qu'une anomalie de
revue ou une confirmation humaine requise subsiste. Si les artefacts rendent un
des trois gates collection verts attendu rouge, arreter avant finalisation et
corriger leur integration sans modifier de source, section ou build TNSI. Ne
pas modifier les dispositions, baselines, build manifests ou PDF pour forcer un
resultat vert.

- [ ] **Step 5: Obtain final independent review**

Faire controler le diff complet contre la conception : exhaustivite 349/349,
exactitude des comptes, preuves localisees, absence de TNSI, absence de
transition de statut et absence d'auto-approbation. Toute correction de contenu
decouverte devient une prochaine action separee.

- [ ] **Step 6: Emit the mandatory session report**

Terminer avec le SHA observe et les rubriques exactes exigees par `AGENTS.md` :

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
