# Audit infrastructure RAG — verite terrain rejouable (2026-07-03)

## Statut : BLOCKED_PREFLIGHT — decision du lead requise

## Ambiguite de perimetre (tranchee par preuve rejouable)

Le brief FE-01 reference pgvector, e5-large 1024d, 16 892 chunks,
resolve_collection_v2, LOT 24. Certains de ces termes existent dans
ce depot, d'autres non.

### pgvector — PRESENT (transition documentee, non deployee)

Commande :
```bash
grep -rn pgvector --include='*.md' --include='*.py' --include='*.yml' . \
  | grep -v __pycache__ | grep -v AUDIT_FRONTEND
```
Sortie :
```
./rag_connection.md:17: trajectoire Nexus : rag-pedago -> pgvector -> retrieval HMAC
./reports/closure2/rag_state_of_truth.md:50: Transition vers pgvector documentee mais non deployee
```
pgvector est une roadmap inscrite dans CE depot, jamais executee.

### e5-large — ABSENT du depot originel

Commande :
```bash
grep -rnE 'e5[-_. ]?large' --include='*.md' --include='*.py' --include='*.yml' . \
  | grep -v __pycache__ | grep -v AUDIT_FRONTEND
```
Sortie : (vide)

### resolve_collection_v2 — ABSENT

Commande :
```bash
grep -rn resolve_collection_v2 --include='*.md' --include='*.py' --include='*.yml' . \
  | grep -v __pycache__ | grep -v AUDIT_FRONTEND
```
Sortie : (vide)

### 16 892 / 22 518 — ABSENTS

Commande :
```bash
grep -rnE '16.?892|22.?518' --include='*.md' --include='*.py' . \
  | grep -v __pycache__ | grep -v AUDIT_FRONTEND
```
Sortie : (vide)

Le "16 892" du brief ne correspond a aucun compte reel verifie :
ni Chroma (4716 / 5992) ni pgvector LOT 22 (22 518). Chiffre non source.

### LOT 24 / rag_nexus_nsi — ABSENTS

Commande :
```bash
grep -rnE 'LOT[ ._-]?24' --include='*.md' . | grep -v AUDIT_FRONTEND
grep -rn rag_nexus_nsi --include='*.md' --include='*.py' . | grep -v AUDIT_FRONTEND
```
Sortie : (vide) pour les deux.

Present dans cyranoaladin/RAG (ADR-0013, LOT 22).

### Conclusion nuancee

Le brief FE-01 agrege DEUX realites :
1. **pgvector** : transition documentee dans CE depot (2 occurrences
   originales) mais JAMAIS deployee sur le serveur.
2. **e5-large 1024d / LOT 22-24 / 22 518 chunks / resolve_collection_v2 /
   rag_nexus_nsi_*** : chaine qui vit dans cyranoaladin/RAG, absente ici.

## Etat reel du serveur (commandes rejouables)

### Backend = Chroma (pas pgvector)

Commande :
```bash
docker exec compose-ingestor-1 printenv CHROMA_HOST CHROMA_PORT
```
Sortie : `chroma` `8000`

Commande :
```bash
docker exec compose-ingestor-1 printenv EMBED_MODEL
```
Sortie : `nomic-embed-text` (PAS e5-large)

### database.py NON cable (grep large couvrant toutes les formes d'import)

Commande :
```bash
docker exec compose-ingestor-1 grep -nE \
  'import +database|from +database +import|RagDatabase|from +\.database' /app/api.py
```
Sortie : (vide, exit=1). database.py present dans le conteneur, NON importe.

### pgvector : aucune table RAG

psql est fonctionnel (tables applicatives listees), mais aucune table rag_.

Commande :
```bash
docker exec infra-postgres-1 psql -U nsi -d nsi -c "\dt" | grep -E 'rag_' \
  || echo "NO_RAG_TABLES (psql OK, grep rag_ = 0)"
docker exec nexus-postgres-db psql -U nexus_admin -d nexus_prod -c "\dt" | grep -E 'rag_' \
  || echo "NO_RAG_TABLES (psql OK, grep rag_ = 0)"
```
Sortie : `NO_RAG_TABLES (psql OK, grep rag_ = 0)` pour les deux.

Note : psql repond (tables Attempt/Bilan/TeacherCoverage dans infra,
CoachAvailability/SessionBooking dans nexus), confirmant que la connexion
fonctionne et que l'absence de rag_ n'est pas un masquage d'erreur.

### Collections Chroma (commande rejouable)

Commande :
```bash
python3 -c "
import json, urllib.request
base='http://127.0.0.1:8000/api/v2/tenants/default_tenant/databases/default_database'
cols=json.loads(urllib.request.urlopen(f'{base}/collections').read())
for c in sorted(cols,key=lambda x:x['name']):
    count=urllib.request.urlopen(f'{base}/collections/{c[\"id\"]}/count').read().decode()
    print(f'{c[\"name\"]}: {count}')
"
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

### UI app_v2.py → Chroma

Commande :
```bash
docker inspect compose-ui-1 --format "{{.Config.Cmd}}"
```
Sortie : `[streamlit run app_v2.py ...]`

Commande :
```bash
docker exec compose-ui-1 printenv INGEST_API_BASE
```
Sortie : `http://ingestor:8001` (Chroma backend)

## Options et decision requise (lead/humain)

### Option A — Raccorder l'UI au Chroma v2 EXISTANT

Cible : nsi_corpus_v2 (5992 chunks, nomic 768d, schema canonique).
Valide par smoke + juge + barrieres ITEM 1-3.

- Cout : faible (config UI)
- Risque : faible (meme stack Chroma)
- Limite : ne fournit PAS e5-large/rerank/22 518 chunks. Pas de F-01
  (citabilite source_label/doc_id au sens du LOT 22).

### Option B — Deployer l'infra pgvector (roadmap inscrite ici)

Ce n'est PAS hors sujet : la transition pgvector est documentee
dans rag_connection.md et rag_state_of_truth.md de CE depot. La deployer
serait la CONCRETISATION d'une roadmap existante.

- Cout : eleve (tables, migration, cablage api.py, modele d'embedding).
  La chaine e5-large/rerank/22 518 chunks vient du depot RAG et
  necessiterait un pont entre les deux projets.
- Risque : eleve (volume partage, Korrigo colocalise)

### Option C — Reaiguiller FE-01 vers cyranoaladin/RAG

La partie e5-large/LOT 22-24/22 518 chunks vit dans le depot RAG.
Le raccordement UI vers cette chaine devrait etre pilote depuis CE projet.
Sur CE depot, le Chroma v2 est pret (option A).

- La partie pgvector a un pied dans ce depot (roadmap documentee).
- La partie e5-large/LOT est entierement dans l'autre.

## Invariants (ce depot, inchanges)

```
covered : 0, absent : 22, published : 0, validated_* : 0
FINAL_STATUS = NON_RELEASE_READY
```

Aucune ecriture effectuee. Aucun secret affiche. Korrigo inchange.
