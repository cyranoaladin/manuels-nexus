# Connexion RAG du corpus NSI

## Statut

Le dépôt reste `FINAL_STATUS = NON_RELEASE_READY`. Le RAG peut aider à proposer
des sections candidates, mais il ne valide jamais une capacité. La collection
interne utilisée par le juge de substance est `nsi_corpus`.

## Architecture observée

Lecture locale effectuée dans le checkout RAG voisin autorisé par le cahier des
charges :

- production historique : Streamlit + FastAPI ingestor + ChromaDB + Ollama ;
- endpoint historique : `POST /search` ;
- collections legacy mappées par `services/rag-engine/configs/legacy_collection_mapping.yml` ;
- trajectoire Nexus : `rag-pedago -> pgvector -> retrieval HMAC` via contrat
  `RetrievalRequest -> RetrievalResponse` ;
- modèle historique du corpus NSI : `nomic-embed-text`, dimension `768`,
  distance `cosine`.

`rag_education` peut servir d'inspiration ou de comparaison externe. Cette
collection ne prouve jamais la couverture interne du corpus.

## Variables nécessaires

Le modèle sans secret est `.env.rag.example`. Les valeurs sensibles restent dans
`.env.rag`, ignoré par Git.

```env
RAG_BACKEND=chroma
RAG_API_BASE_URL=https://rag-api.nexusreussite.academy/search
RAG_API_KEY=
RAG_COLLECTION=nsi_corpus
RAG_DISTANCE=cosine
RAG_VECTOR_DIM=768
EMBEDDING_MODEL=nomic-embed-text
LOCAL_LLM_ENGINE=ollama
LOCAL_LLM_MODEL=qwen2.5:7b
```

## Smoke test

Sans `.env.rag`, `scripts/rag_smoke_test.py` n'ouvre pas le réseau et affiche :

```text
RAG_SMOKE_TEST_SKIPPED_NO_CONFIG
```

Avec `.env.rag`, il appelle `/search` en Bearer sur `nsi_corpus`, vérifie la
présence de résultats et exige les métadonnées minimales. Les champs canoniques
des nouveaux chunks sont `section_anchor` et `capacity_ids`. Les anciens champs
`anchor` et `capacities` ne sont tolérés que comme alias de compatibilité.

Observation du 2026-06-29 :

- `https://rag-api.nexusreussite.academy/health` répond `HTTP 200` ;
- `/search` sans token répond `HTTP 401` ;
- `/search` authentifié reste en timeout après authentification sur `nsi_corpus`
  et `rag_education` ;
- le serveur expose des conteneurs `compose-ingestor`, `compose-chroma`,
  `compose-ollama` et `compose-ui` en état `healthy` ;
- aucune connexion RAG fonctionnelle n'est donc déclarée pour le juge tant que
  `/search` authentifié ne retourne pas de hits avec métadonnées conformes.

## Requête de référence

```bash
curl -sS "$RAG_API_BASE_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $RAG_API_KEY" \
  -d '{
    "q": "Importer une table depuis un fichier CSV",
    "collection": "nsi_corpus",
    "k": 5,
    "include_documents": true
  }'
```

Résultat attendu après indexation correcte : hit sur P05 ou une ressource liée
aux tables CSV, avec capacités P-TABLE-01 / P-TABLE-02 si disponibles dans les
métadonnées.

## Ingestion

`scripts/ingest_nsi_corpus.py` prépare des chunks internes avec `source_type =
nsi_corpus`, `proof_scope = internal_coverage_candidate`, `collection =
nsi_corpus`, `section_anchor`, `capacity_ids` et `private_data = false`. Toute
ingestion réelle nécessite un plan, un dry-run et un contrôle des métadonnées.
Aucune donnée élève, aucun fichier `/AUDIT`, `dist/`, `.git/` ou
`Documents_DRIVE/` ne doit être indexé comme corpus pédagogique interne.

Option stricte retenue : `nsi_corpus` ne contient que
`03_progressions/supports/` et `03_progressions/fiches_cours/`. Les dossiers
`premiere/sequences/` et `terminale/sequences/` sont des golden examples ; s'ils
sont indexés un jour, ce sera dans `nsi_golden_examples` avec
`proof_scope = style_reference_only` et `usable_for_coverage = false`.
