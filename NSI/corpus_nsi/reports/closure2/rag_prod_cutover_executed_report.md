# RAG Prod Cutover — Rapport d'execution

## Statut : BLOCKED

## Sas d'armement (5/5 VERT)

| Precondition | Resultat | Detail |
|---|---|---|
| (a) SSH korrigo | VERT | SSH_OK, host=korrigo, user=root |
| (b) Docker | VERT | DOCKER_OK |
| (c) .env.rag | VERT | /tmp/nsi_judge/.env.rag, RAG_API_KEY present |
| (d) Depots | VERT | RAG repo OK, PR #35 MERGED (677fd0a) |
| (e) NSI propre | VERT | arbre propre, branche rag-cutover/exec |

## Preflight (section 1)

### Pile serveur

- **RAG** : compose-ui-1 (healthy), compose-ingestor-1 (healthy),
  compose-ollama-1 (healthy), compose-chroma-1 (healthy), compose-autoheal-1
- **Korrigo** : docker-nginx-1, docker-backend-1, docker-celery-1,
  docker-celery-beat-1, docker-redis-1, docker-db-1 — tous healthy, IDs notes
- **Espace disque** : 188G disponibles (suffisant)

### Collections Chroma live

| Collection | Chunks |
|---|---|
| nsi_corpus | 4716 |
| rag_education | present |
| rag_francais_premiere | present |
| rag_maths_premiere | present |
| rag_math_correction | present |
| ressources_pedagogiques_terminale | present |

### Schema legacy prouve

```
POST /search {q: "CSV", collection: "nsi_corpus", k: 2}
→ anchor=True section_anchor=False capacities=True capacity_ids=False
```

## Backup (section 2)

- Chemin : `/root/backups/chroma_pre_cutover_2026-07-01.tgz`
- Taille : 119M
- Archive verifiee (tar -tzf : contenu non vide)
- Restauration : `docker run --rm -v compose_rag_ui_chroma_data:/data -v /root/backups:/backup busybox sh -c "cd / && tar xzf /backup/chroma_pre_cutover_2026-07-01.tgz"`

## Embedding parity (section 3) — BLOQUANT

### Constat

Le serveur prod utilise ollama `nomic-embed-text` (768 dimensions) pour
l'embedding des documents. Le modele est disponible sur le serveur :
```
nomic-embed-text:latest    0a109f422b47    274 MB
```

### Mismatch

`scripts/rag_ingest.py` utilise le client Chroma Python directement, qui
emploie par defaut `all-MiniLM-L6-v2` (384 dimensions). Ce n'est PAS le
meme espace d'embedding. Une collection v2 ingeree avec MiniLM ne serait
PAS interrogeable par des requetes utilisant nomic-embed-text.

### Solution requise (non implementee)

L'ingestor FastAPI (`compose-ingestor-1`) expose `POST /ingest` qui gere
l'embedding via ollama. L'ingestion doit passer par cette API :
1. Adapter `scripts/rag_ingest.py` pour envoyer les chunks via
   `POST /ingest` au lieu d'ecrire directement dans Chroma
2. Ou configurer un embedding function ollama pour le client Chroma Python

Cela requiert du NOUVEAU CODE + PR + CI, pas un simple deployment.

### Decision

**STOP au gate §3.** Aucune ingestion, aucun cutover. L'index live
`nsi_corpus` (legacy) reste intact. Le backup est conserve.

## Korrigo : INCHANGE

Container IDs avant et apres identiques (aucune mutation Korrigo).

## Secrets : aucun affiche

Les tokens INGESTOR_API_TOKEN et RAG_API_KEY n'apparaissent jamais
dans les sorties.

## Actions requises pour debloquer

1. Adapter `scripts/rag_ingest.py` pour utiliser l'API ingestor
   (`POST /ingest` sur 127.0.0.1:18001) avec le token
   INGESTOR_API_TOKEN, OU implementer un embedding function ollama
   pour le client Chroma Python
2. Prouver la parite d'embedding (meme modele, meme dimension) sur
   une collection staging
3. Reprendre le cutover a partir du §4

## Invariants depot

```
covered : 0
absent : 22
published : 0
validated_* : 0
FINAL_STATUS = NON_RELEASE_READY
```

## Dette residuelle

Inchangee : doublon P08, backlog Drive 3+7+5, 22 capacites absentes,
cutover RAG prod (BLOQUE par embedding mismatch).
