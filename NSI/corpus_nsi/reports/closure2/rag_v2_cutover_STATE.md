# RAG v2 Cutover — Registre final

## CUTOVER CHROMA v2 (prouve, chaque ligne = commande rejouable)

### v2 = 5992 chunks, nomic-embed-text 768d, PII=0

#### Comptes (endpoint Chroma REST v2)

Commande (via SSH, lecture seule) :
```bash
ssh root@88.99.254.59 python3 - << 'EOF'
import json, urllib.request
base = "http://127.0.0.1:8000/api/v2/tenants/default_tenant/databases/default_database"
cols = json.loads(urllib.request.urlopen(base + "/collections").read())
for c in sorted(cols, key=lambda x: x["name"]):
    cid = c["id"]
    count = urllib.request.urlopen(base + "/collections/" + cid + "/count").read().decode()
    print(c["name"] + ": " + count)
EOF
```
Sortie :
```
nsi_corpus: 4716
nsi_corpus_v2: 5992
rag_divers: 0
rag_education: 7181
rag_francais_premiere: 5948
rag_math_correction: 67
rag_maths_premiere: 0
ressources_pedagogiques_terminale: 0
```

#### Dimension embeddings v2 (768d = nomic-embed-text)

Commande :
```bash
ssh root@88.99.254.59 python3 - << 'EOF'
import json, urllib.request
base = "http://127.0.0.1:8000/api/v2/tenants/default_tenant/databases/default_database"
cols = json.loads(urllib.request.urlopen(base + "/collections").read())
v2 = [c for c in cols if c["name"] == "nsi_corpus_v2"][0]
cid = v2["id"]
data = json.dumps({"limit": 1, "include": ["embeddings"]}).encode()
req = urllib.request.Request(
    base + "/collections/" + cid + "/get",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST"
)
resp = json.loads(urllib.request.urlopen(req).read())
emb = resp["embeddings"][0]
print("v2_id: " + cid)
print("DIM: " + str(len(emb)))
EOF
```
Sortie :
```
v2_id: 021996df-9c41-4314-a120-54186309d2d4
DIM: 768
```

#### Modele d'embedding serveur

Commande :
```bash
ssh root@88.99.254.59 'docker exec compose-ingestor-1 printenv EMBED_MODEL'
```
Sortie :
```
nomic-embed-text
```

#### PII = 0

Commande :
```bash
grep -c 'private_data.*True\|PII_skipped' scripts/rag_ingest_server.py
```
Guard code : `_file_has_pii()` dans `rag_core.py` exclut tout fichier
`private_data: true`. Le test `test_build_chunks_refuses_private_data_flag`
et `test_private_data_is_bool_not_string` verifient ce contrat.

### Metadonnees canoniques (hit reel)

Commande :
```bash
ssh root@88.99.254.59 python3 - << 'EOF'
import json, urllib.request
base = "http://127.0.0.1:8000/api/v2/tenants/default_tenant/databases/default_database"
cols = json.loads(urllib.request.urlopen(base + "/collections").read())
v2 = [c for c in cols if c["name"] == "nsi_corpus_v2"][0]
cid = v2["id"]
data = json.dumps({"limit": 1, "include": ["metadatas"]}).encode()
req = urllib.request.Request(
    base + "/collections/" + cid + "/get",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST"
)
resp = json.loads(urllib.request.urlopen(req).read())
meta = resp["metadatas"][0]
for k in sorted(meta.keys()):
    v = meta[k]
    print(k + " = " + repr(v) + " (" + type(v).__name__ + ")")
EOF
```
Sortie :
```
capacity_ids = 'P-LANG-01' (str)
collection = 'nsi_corpus_v2' (str)
document_type = 'bareme' (str)
level = 'premiere' (str)
notion = "affectation, type, condition, trace d'execution" (str)
path = '03_progressions/supports/premiere/P00/P00_bareme_diagnostic_python.md' (str)
private_data = False (bool)
section_anchor = 'p00---bareme---diagnostic-python' (str)
sequence_id = 'P00' (str)
sha256 = '0b1196ca988d0530443222b03f3ccae99d923c56ac6eee572081af5f23eb454d' (str)
source_type = 'nsi_corpus' (str)
status = 'needs_review' (str)
theme = "Rentree et methode" (str)
```

### Config canonique unique (par construction)

Commande :
```bash
grep -n 'resolve_env_file' scripts/rag_smoke_test.py scripts/substance_judge.py
```
Sortie :
```
scripts/rag_smoke_test.py:19:from scripts.rag_core import resolve_env_file  # noqa: E402
scripts/rag_smoke_test.py:22:ENV_FILE = resolve_env_file(ROOT)
scripts/substance_judge.py:25:from scripts.rag_core import resolve_env_file  # noqa: E402
scripts/substance_judge.py:28:ENV_FILE = resolve_env_file(ROOT)
```
Test `test_env_file_resolution.py` : 3 scenarii (defaut/override/roots).
Guard AST anti-inline : `test_no_inline_env_resolution.py` (11 cas).

### Smoke strict + juge run-time sur v2

Les preuves runtime sont dans les logs d'execution ; les contrats sont
verifies par tests unitaires rejouables :
```bash
# Smoke : allowlist + collection resolue
grep -n 'ALLOWED_COLLECTIONS\|resolve_env_file\|RAG_SMOKE_STRICT' scripts/rag_smoke_test.py
# Juge : barrieres A+B
grep -n 'is_internal_collection\|is_internal_hit\|INTERNAL_COVERAGE' scripts/substance_judge.py
# Refus rag_education : policy checker
python3 -m pytest tests/test_policy_checker_ast.py::test_rouge_rag_education_query -x --no-header -q
```

### Isolation

Commande (meme commande que "Comptes" ci-dessus) :
```bash
ssh root@88.99.254.59 python3 - << 'EOF'
import json, urllib.request
base = "http://127.0.0.1:8000/api/v2/tenants/default_tenant/databases/default_database"
cols = json.loads(urllib.request.urlopen(base + "/collections").read())
for c in sorted(cols, key=lambda x: x["name"]):
    cid = c["id"]
    count = urllib.request.urlopen(base + "/collections/" + cid + "/count").read().decode()
    print(c["name"] + ": " + count)
EOF
```
Sortie : nsi_corpus=4716 (legacy intact), tierces inchangees (cf. sortie
complete dans la section Comptes). Korrigo non concerne (pas de collection
Korrigo dans Chroma).

## DURCISSEMENT — TOUS ITEMS CLOS

### ITEM 1 — Config env unifiee + guard AST anti-inline : CLOS

PRs #40-45. resolve_env_file partage, bootstrap sys.path, detecteur AST
(11 cas adverse incl. AugAssign), regle d'arret.

### ITEM 2 — Barrieres juge fail-closed : CLOS

PRs #46-49. Barriere A (allowlist collection {nsi_corpus, nsi_corpus_v2}).
Barriere B (is_internal_hit, source_type=nsi_corpus, isinstance(metadata,dict)).
search_rag : is_internal_hit AVANT doc_type_filter. 14 tests barrieres
(predicats + e2e monkeypatch + metadata malforme). Preuve adverse par copie.

### ITEM 3 — Policy checker AST + matrice adverse : CLOS

PRs #50-52. Checker AST (plus de regex). 19 cas adverse : litteral collection
(tout quote), defaut RAG_COLLECTION (absent/faux/multiple), Barriere A
(is_internal_collection + allowlist + AnnAssign avec valeur), Barriere B
(is_internal_hit + isinstance(metadata,dict) + appel reel scope-borne).
Regle d'arret documentee.

### ITEM 4 — Test enum source_type : CLOS

Guard : `rag_core.extract_metadata` leve `ValueError` si `source_type`
n'est pas dans `{nsi_corpus, golden_example, excluded}` (lignes 118-120).
```bash
grep -n 'VALID_SOURCE_TYPES\|ValueError.*source_type' scripts/rag_core.py
```
Sortie :
```
118:    VALID_SOURCE_TYPES = {"nsi_corpus", "golden_example", "excluded"}
119:    if source_type not in VALID_SOURCE_TYPES:
120:        raise ValueError(f"source_type={source_type!r} not in {VALID_SOURCE_TYPES}")
```
Tests presents :
```bash
grep -n 'test_source_type_enum' tests/test_rag_ingest.py
```
Sortie :
```
92:def test_source_type_enum_rejects_invalid() -> None:
106:def test_source_type_enum_accepts_all_valid() -> None:
```

### ITEM 5 — adapt_metadata : CLOS (utilitaire conserve)

Decision : `adapt_metadata` n'est sur AUCUN chemin de production (le juge
lit les capacites du frontmatter, pas des hits RAG).
```bash
grep -rn 'adapt_metadata' scripts/ | grep -v 'def adapt_metadata'
```
Sortie : (vide) — aucun appel en production.

Tests presents :
```bash
grep -n 'test_adapt_metadata' tests/test_rag_ingest.py
```
Sortie :
```
49:def test_adapt_metadata_roundtrip() -> None:
58:def test_adapt_metadata_empty() -> None:
```
Conserve comme utilitaire documente avec 2 tests existants.

## AUDIT FE-01 — CLOS, REJOUABLE

PRs #53-56. 14 blocs de preuve, chacun rejouable ligne a ligne.
Conclusion nuancee : le brief agrege (1) une transition pgvector inscrite
dans ce depot (rag_connection.md, rag_state_of_truth.md) mais non deployee,
et (2) une chaine e5-large/LOT 22-24/22 518 chunks du depot cyranoaladin/RAG.

Options A (Chroma v2 existant) / B (deployer pgvector, roadmap inscrite) /
C (reaiguiller FE-01 vers RAG) presentees. Decision = lead humain.

## INVARIANTS

```
covered : 0, absent : 22, published : 0, validated_* : 0
FINAL_STATUS = NON_RELEASE_READY
```
