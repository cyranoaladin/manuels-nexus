# RAG v2 reconstruit — Rapport

## Statut : V2_REBUILT_CLEAN_READY_FOR_CUTOVER

## Factorisation (section 1)

Module partage `scripts/rag_core.py` : frontmatter, chunking, github_slug
(Unicode), PII guard, metadata canoniques. `rag_ingest.py` (local) et
`rag_ingest_server.py` (REST+ollama) importent ce module. Anti-divergence.

## PII guard (section 2)

`rag_ingest_server.py` appelle `rag_core.file_has_pii()` avant embedding.
Resultat rebuild : `PII_skipped=0` (aucun PII dans le corpus).

## Slugger Unicode (section 3)

`rag_core.github_slug()` = `check_substance_anchors.github_slug()`.
Ancres accentuees prouvees dans v2 : `barème`, `à-savoir`, `réponses-rapides`,
`évaluation` (pas les versions ASCII tronquees).

## Smoke v2-capable (section 4)

`os.environ` override `.env.rag`. Allowlist : `{nsi_corpus, nsi_corpus_v2}`.

```
RAG_COLLECTION=nsi_corpus_v2  → RAG_SMOKE_TEST_OK hits=5
RAG_COLLECTION=nsi_corpus     → RAG_SMOKE_TEST_FAILED (schema legacy)
```

## v2 reconstruit (section 6)

L'ancien nsi_corpus_v2 (suspect : sans PII guard, sans slug Unicode) a ete
supprime. Un nouveau nsi_corpus_v2 a ete construit avec le script corrige.

- Files: 452, Chunks: 5992, PII_skipped: 0
- Embed: nomic-embed-text 768d via ollama
- Ancres Unicode preservees
- capacity_ids reelles (P-TABLE, T-ALGO, P-ALGO, P-LANG, P-IHM)
- 5/5 requetes pertinentes
- Smoke : RAG_SMOKE_TEST_OK hits=5

## Runbook (section 7)

0 commande `python -m scripts.rag_ingest` (MiniLM) dans le corps.
Toutes les etapes utilisent `scripts/rag_ingest_server.py` + ollama.

## Collections live intactes (section 8)

| Collection | Avant | Apres |
|---|---|---|
| nsi_corpus | 4716 | 4716 |
| nsi_corpus_v2 | 5992 (suspect) | 5992 (reconstruit propre) |
| rag_education | 7181 | 7181 |
| rag_francais_premiere | 5948 | 5948 |
| rag_math_correction | 67 | 67 |

Korrigo container IDs identiques — INCHANGE. Aucun secret affiche.

## Reste pour le cutover

1. Bascule UI config : nsi_corpus → nsi_corpus_v2
2. Smoke post-bascule VERT
3. Rollback documentee
4. Suppression differee legacy

## Invariants

covered=0, absent=22, published=0, validated_*=0, FINAL_STATUS=NON_RELEASE_READY.
