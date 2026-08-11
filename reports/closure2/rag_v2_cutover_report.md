# RAG v2 Cutover — Rapport corrige

## Statut : V2_CUTOVER_DONE (perimetre NSI tooling)

## Consommateurs prod de nsi_corpus (section 1)

Enumeration exhaustive (grep dans api.py, app_v2.py, nginx) :
- `COLLECTION_MAP["nsi"] = "nsi_corpus"` dans l'API ingestor — mais AUCUN
  consommateur en prod n'envoie `section=nsi` (app_v2.py n'expose pas de
  section NSI, nginx ne route pas vers nsi)
- app.py (ancien) utilise `ressources_pedagogiques_terminale` (pas nsi_corpus)
  et n'est PAS le processus actif (app_v2.py est l'entrypoint)
- **Conclusion** : nsi_corpus est consomme UNIQUEMENT par le smoke test NSI
  et le juge de substance, via `/tmp/nsi_judge/.env.rag`

Le "cutover" est correctement scope au tooling NSI, pas a l'UI Streamlit
(qui ne sert pas la collection NSI).

## Point de bascule (section 2)

Le fichier `/tmp/nsi_judge/.env.rag` (lu par le smoke test et le juge de
substance) controle la collection cible :
```
RAG_COLLECTION=nsi_corpus_v2
```

Ce fichier est le SEUL point de lecture. Le COLLECTION_MAP de l'API ingestor
accepte `collection=nsi_corpus_v2` en parametre explicite de `/search`,
sans modification du map.

**Limitation** : `/tmp` n'est pas durable au reboot. L'emplacement devrait
etre migre vers un repertoire persistant (action humaine recommandee).

## Code fixes (section 5-7)

- **sys.path** : bootstrap `_REPO_ROOT` dans rag_ingest.py (comme server).
  Prouve : `python3 scripts/rag_ingest.py --help` sans PYTHONPATH = OK
- **--collection** : thread dans build_chunks → extract_metadata
- **source_type** : derive de la collection cible (plus hardcode "nsi_corpus")
- **capacity_ids** : CSV string (representation Chroma). `adapt_metadata`
  en rag_core pour les consommateurs qui veulent une liste. L'API `/search`
  retourne du CSV brut — c'est le format canonique a la frontiere API.

## v2 re-ingere (section 6)

source_type etait "nsi_corpus" au lieu de "nsi_corpus_v2" → re-ingestion.
Resultat : 452 files, 5992 chunks, PII_skipped=0, nomic-embed-text 768d.

Metadata verifiee sur un hit reel :
```
collection='nsi_corpus_v2'
source_type='nsi_corpus_v2'     ← CORRIGE (etait 'nsi_corpus')
private_data=False (bool)
capacity_ids='P-TABLE-01,P-TABLE-02' (str CSV)
section_anchor='p05---tp---tables-csv'
```

## Smoke strict (section 10)

```
RAG_SMOKE_STRICT=1 → RAG_SMOKE_TEST_OK collection=nsi_corpus_v2 hits=5
```

## Collections inchangees (section 11)

| Collection | Avant | Apres |
|---|---|---|
| nsi_corpus | 4716 | 4716 (rollback source) |
| nsi_corpus_v2 | 5992 | 5992 (re-ingere avec source_type corrige) |
| rag_education | 7181 | 7181 |
| rag_francais_premiere | 5948 | 5948 |
| rag_math_correction | 67 | 67 |

Korrigo container IDs identiques. Aucun secret affiche.

## Suppression legacy differee

nsi_corpus (4716 chunks) conserve. Suppression apres soak 14 jours.

## Invariants

```
covered : 0
absent : 22
published : 0
validated_* : 0
FINAL_STATUS = NON_RELEASE_READY
```
