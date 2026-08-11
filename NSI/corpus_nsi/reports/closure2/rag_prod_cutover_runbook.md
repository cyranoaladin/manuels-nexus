# Runbook de cutover production RAG

## Statut : PLAN SEULEMENT

## Prerequis

- Acces SSH au serveur (88.99.254.59, host korrigo)
- INGESTOR_API_TOKEN disponible (via docker exec compose-ingestor-1 printenv)
- Pipeline d'ingestion valide (`scripts/rag_ingest_server.py`)
- Backup Chroma verifie
- Approbation du chef de projet

## Etape 1 : Backup

```bash
ssh korrigo "docker run --rm -v compose_rag_ui_chroma_data:/data -v /root/backups:/backup \
  busybox tar czf /backup/chroma_pre_cutover_$(date +%Y-%m-%d).tgz /data"
```

Jamais de drop de collection. Le backup est le prerequis absolu.

## Etape 2 : Ingestion dans collection NEUVE (nsi_corpus_v2)

```bash
cd /tmp/nsi_ingest && git pull
NSI_ROOT=/tmp/nsi_ingest TARGET_COLLECTION=nsi_corpus_v2 \
  python3 scripts/rag_ingest_server.py
```

Utilise ollama nomic-embed-text (768d). JAMAIS `python -m scripts.rag_ingest`
(MiniLM 384d incompatible).

## Etape 3 : Validation staging

```bash
RAG_COLLECTION=nsi_corpus_v2 python -m scripts.rag_smoke_test
```

Critere : RAG_SMOKE_TEST_OK, metadonnees canoniques sur tous les hits.
Comptes a verifier (live nsi_corpus=4716 chunks, v2 attendu ~5992 chunks).

## Etape 4 : Cutover UI

Basculer la collection par defaut dans rag-ui.nexusreussite.academy de
nsi_corpus vers nsi_corpus_v2 (changement de config UI uniquement).

## Etape 5 : Verification post-cutover

```bash
RAG_COLLECTION=nsi_corpus_v2 make rag-smoke-required
python -m scripts.rag_diagnose_search_timeout
```

## Rollback

1. Rebasculer config UI vers nsi_corpus (legacy)
2. Si volume corrompu : restaurer le backup tgz
3. Verifier : `curl -sS http://127.0.0.1:18001/health`

## Retention

Conserver nsi_corpus (legacy) + backup pendant 14 jours minimum.
Suppression differee apres validation en conditions reelles.
