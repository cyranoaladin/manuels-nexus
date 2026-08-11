# RAG v2 versionne — Rapport

## Statut : V2_REPRODUCIBLE_READY_FOR_CUTOVER

## Ingestion versionnee (section 1)

`scripts/rag_ingest_server.py` committe dans le depot :
- Embedding via ollama nomic-embed-text (768d), JAMAIS MiniLM
- Chroma REST API v2 (aucun pip chromadb requis)
- URL/token/collection parametrables par ENV, token jamais logge
- Metadonnees canoniques (section_anchor, capacity_ids CSV reelles)
- 0 PII / 0 Drive sensible (private_data guard)
- mypy --strict + ruff verts

/tmp/nsi_ingest/ingest_v2.py supprime du serveur (CONFIRMED_GONE).

## Smoke v2-capable (section 2)

`rag_smoke_test.py` : collection parametrable via `RAG_COLLECTION` env.

```
RAG_COLLECTION=nsi_corpus_v2 → RAG_SMOKE_TEST_OK collection=nsi_corpus_v2 hits=5
RAG_COLLECTION=nsi_corpus    → RAG_SMOKE_TEST_FAILED (hit 4: metadonnees absentes)
```

Le gate distingue correctement v2 (canonique, VERT) de legacy (incomplet, ECHEC).

## Runbook neutralise (section 3)

`rag_prod_cutover_runbook.md` marque BLOQUE avec avertissement :
"NE PAS utiliser python -m scripts.rag_ingest pour la prod (MiniLM 384d incompatible)."

## Reproductibilite prouvee (section 4)

Collection jetable `nsi_corpus_v2_repro` creee depuis le script committe :
- Files: 452, Chunks: 5992 (= v2)
- 5/5 requetes pertinentes (memes resultats que v2)
- Collection supprimee apres preuve

## Collections live intactes (section 6)

| Collection | Avant | Apres |
|---|---|---|
| nsi_corpus | 4716 | 4716 |
| nsi_corpus_v2 | 5992 | 5992 |
| rag_education | 7181 | 7181 |
| rag_francais_premiere | 5948 | 5948 |
| rag_math_correction | 67 | 67 |
| nsi_corpus_v2_repro | - | supprimee |

Korrigo container IDs identiques — INCHANGE. Aucun secret affiche.

## Reste pour le cutover (passe suivante)

1. Bascule UI : config nsi_corpus → nsi_corpus_v2
2. Validation rag-smoke-required post-bascule
3. Rollback documentee (rebascule vers nsi_corpus)
4. Suppression differee ancienne collection

## Invariants

covered=0, absent=22, published=0, validated_*=0, FINAL_STATUS=NON_RELEASE_READY.
