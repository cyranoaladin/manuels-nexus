# Plan de réindexation RAG

## Statut : PLAN SEULEMENT — exécution interdite cette passe

## Dérive de schéma — OBSERVÉE ET PROUVÉE

Commande de preuve (lecture seule, sans secret affiché, confirmée passe 3, 2026-06-30 ~09h) :
```
POST /search {q: "CSV", collection: "nsi_corpus", k: 2}
→ HITS_COUNT=2
→ hit[0] metadata keys: ['anchor', 'capacities', 'chunk_index', 'collection',
   'document_type', 'level', 'notion', 'path', 'sequence_id', 'sha256',
   'source_type', 'status', 'theme']
→ anchor=True  section_anchor=False  capacities=True  capacity_ids=False
→ hit[1] metadata keys: identiques
```

L'index `nsi_corpus` déployé sur le serveur (88.99.254.59, host korrigo) utilise
les champs legacy :
- `anchor` (slug de section) — **observé dans les hits réels**
- `capacities` (chaîne séparée par virgules) — **observé dans les hits réels**

Le dépôt NSI attend désormais les champs canoniques :
- `section_anchor` (remplace `anchor`) — **absent des hits réels**
- `capacity_ids` (liste de chaînes, remplace `capacities`) — **absent des hits réels**

Le smoke test (`scripts/rag_smoke_test.py`) accepte les deux variantes pour
rétrocompatibilité, mais la validation stricte
(`scripts/check_rag_metadata_canonical_fields.py`) exige les champs canoniques.

## Mapping ancien → nouveau

| Champ déployé | Champ canonique | Transformation |
|---------------|-----------------|----------------|
| anchor | section_anchor | Renommage direct |
| capacities | capacity_ids | Split(",") → liste |
| (absent) | proof_scope | Ajouter "internal_coverage_candidate" pour nsi_corpus |
| (absent) | usable_for_coverage | Ajouter true pour nsi_corpus |
| (absent) | collection | Ajouter "nsi_corpus" |

## Étapes (à exécuter Lot 4+)

1. **Sauvegarde** : `chromadb.PersistentClient` export de la collection
   `nsi_corpus` vers `backup_nsi_corpus_YYYYMMDD.json`
2. **Dry-run** : `scripts/ingest_nsi_corpus.py --dry-run` pour vérifier le
   mapping sur tous les documents source
3. **Réindexation** : `scripts/ingest_nsi_corpus.py` avec les champs canoniques
4. **Vérification métadonnées** : `scripts/check_rag_metadata_canonical_fields.py`
   doit passer sur un hit réel
5. **Smoke test** : `make rag-smoke-required` doit passer
6. **Rollback si échec** : restaurer `backup_nsi_corpus_YYYYMMDD.json`

## Impact utilisateur

- Pendant la réindexation (~5 min estimées), `/search` retourne 0 résultats
- Aucun impact sur les utilisateurs finaux (RAG non exposé publiquement)
- Les requêtes existantes restent compatibles (mêmes embeddings nomic-embed-text)

## Prérequis

- Accès SSH au serveur (88.99.254.59)
- `.env.rag` avec RAG_API_KEY valide
- Timeout `/search` résolu (actuellement le endpoint time out)
- Décision explicite du chef de projet
