# Rapport de cohérence RAG

Statut : rapport local conservateur.

- Collection interne de jugement : `nsi_corpus`.
- `rag_education` : inspiration externe, pas preuve de couverture interne.
- Smoke réel 2026-06-29 : `/health` public répond `HTTP 200`, `/search` sans
  token répond `HTTP 401`, mais `/search` authentifié time out sur `nsi_corpus`
  comme sur `rag_education`.
- Ingestion réelle : bloquée sans plan, dry-run, validation métadonnées et revue humaine.

Aucune validation pédagogique n'est produite par ce rapport.
