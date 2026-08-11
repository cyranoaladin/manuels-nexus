# RAG Embedding Parity — Rapport

## Statut : PARITY_PROVEN_STAGING

## Architecture d'ingestion (section 1)

L'API ingestor (`POST /ingest`) attend un fichier source (URL/chemin), pas du
texte pre-chunke. Elle ne permet pas de pousser des chunks avec metadonnees
canoniques directement.

**Decision** : ecriture directe dans Chroma via l'API REST v2, avec embedding
par appel HTTP a ollama (`POST /api/embed`, modele `nomic-embed-text`, 768d).
L'ingestor est utilise uniquement pour `/search` (retrieval).

## Parite d'embedding (section 5) — PROUVEE

### Dimension

```
curl POST http://127.0.0.1:11434/api/embed {"model":"nomic-embed-text","input":["test"]}
→ DIM=768
```

Identique a la prod (nsi_corpus live embed par le meme modele).

### Schema canonique sur v2

5 requetes, 100% des hits portent :
- `section_anchor` (pas `anchor`)
- `capacity_ids` REELLES non vides (P-TABLE-01, T-ALGO-01E, P-ALGO-02A, P-LANG-01, P-IHM-03A)
- `level`, `theme`, `status=needs_review`

### Pertinence (5/5)

| Requete | Top hit | Level | Capacites |
|---|---|---|---|
| CSV import | P05_fiche_cours_tables_csv | premiere | P-TABLE-01,P-TABLE-02 |
| arbre binaire recherche | T06_TD_arbres_binaires | terminale | T-ALGO-01E,T-ALGO-01F |
| tri par selection | P12_cours_tris | premiere | P-ALGO-02A,P-ALGO-02B |
| fonction Python def | P07_fiche_cours_fonctions | premiere | P-LANG-01,P-LANG-02 |
| protocole HTTP | P08_fiche_cours_http | premiere | P-IHM-03A,P-IHM-03B |

### Filtrage

`level=terminale` filtre correctement (seuls resultats terminale).

## Collections live intactes

| Collection | Avant | Apres |
|---|---|---|
| nsi_corpus | 4716 | 4716 (INCHANGE) |
| rag_education | 7181 | 7181 |
| rag_francais_premiere | 5948 | 5948 |
| rag_math_correction | 67 | 67 |
| nsi_corpus_v2 | - | 5992 (NOUVEAU) |

## Korrigo

Container IDs identiques avant/apres — INCHANGE.

## Secrets

Aucun affiche. INGESTOR_API_TOKEN utilise via `docker exec printenv`,
jamais echo dans les sorties.

## Honnetete Phase B

La preuve locale (5992 chunks, passe 4-5) validait la MECANIQUE (walk,
chunking, metadonnees, round-trip CSV). Elle NE validait PAS le retrieval
prod car l'embedder local (all-MiniLM-L6-v2, 384d) differe du prod
(nomic-embed-text, 768d). La parite est desormais prouvee via ingestion
sur le serveur avec le meme modele.

## Reste pour le cutover

- Bascule UI de nsi_corpus vers nsi_corpus_v2 (changement config)
- Validation rag-smoke-required sur v2
- Rollback documentee (rebascule vers nsi_corpus)
- Suppression differee de l'ancienne collection

## Invariants depot

covered=0, absent=22, published=0, validated_*=0, FINAL_STATUS=NON_RELEASE_READY.
