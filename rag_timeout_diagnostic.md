# Diagnostic timeout RAG /search

Statut : blocage actif. Le dépôt ne déclare pas le RAG fonctionnel tant que
`POST /search` authentifié ne retourne pas de réponse exploitable sur
`nsi_corpus`.

## Observations

- Diagnostic public du 2026-06-29 :
  - `GET /health public`: `HTTP=200`, `duration=0.255s`.
  - `POST /search sans token`: `HTTP=401`, `duration=0.319s`.
  - `POST /search token nsi_corpus include_documents=false`: timeout `20.276s`.
  - `POST /search token rag_education include_documents=false`: timeout `20.269s`.
  - `POST /search token nsi_corpus include_documents=true`: timeout `20.203s`.
- Diagnostic serveur local en lecture seule :
  - hostname : `korrigo`.
  - `local_health HTTP 200 time=0.001246`.
  - `local_search_unauth HTTP 401 time=0.001356`.
  - `local_search_auth_nsi_corpus HTTP 000` après environ 20 secondes.
  - conteneurs `compose-ingestor-1`, `compose-chroma-1`, `compose-ollama-1`
    et `compose-ui-1` en état `healthy`.
- Un appel embedding Ollama direct a répondu, donc le moteur local n'est pas
  prouvé globalement indisponible.
- Les logs ingestor tail montrent les `GET /health` et les `POST /search`
  non authentifiés `401`, mais aucun succès de recherche authentifiée dans la
  fenêtre observée.

## Hypothèses

### hypothèse 1 : timeout embedding

Preuve actuelle : Ollama répond à ses health checks et tags, mais les recherches
authentifiées time out avant réponse. L'appel embedding applicatif reste une
phase plausible si l'ingestor appelle un endpoint/modèle différent du test
direct.

Action suivante : journaliser un `request_id`, la durée avant/après appel
embedding et le modèle réellement appelé.

### hypothèse 2 : timeout Chroma query

Preuve actuelle : Chroma est annoncé healthy, mais `nsi_corpus` et
`rag_education` time out après authentification, même avec `k=1` et
`include_documents=false`. Une requête vectorielle ou un accès collection peut
bloquer après l'embedding.

Action suivante : journaliser la durée de récupération collection, le nombre de
vecteurs et la durée de query Chroma pour `k=1`.

### hypothèse 3 : endpoint /search attend un mauvais payload

Preuve actuelle : le payload `q/collection/k/include_documents` obtient un
`401` rapide sans token, puis time out avec token. L'endpoint reçoit donc une
requête structurée, mais peut bloquer après authentification si le contrat réel
attend un format legacy ou un champ supplémentaire.

Action suivante : comparer le contrat réel du service avec l'appel UI et ajouter
un rejet `HTTP 4xx` rapide si le payload est invalide au lieu d'un timeout.

### hypothèse 4 : collection absente ou volumétrie problématique

Preuve actuelle : les deux collections testées time out avec `k=1`; cela peut
signaler une collection absente traitée lentement, une collection trop
volumineuse, ou une initialisation paresseuse coûteuse.

Action suivante : lister les collections côté serveur en lecture seule et
mesurer une query `k=1` par collection avec chronométrage applicatif.

### hypothèse 5 : proxy public non responsable, car local /search authentifié time out aussi

Preuve actuelle : le test local serveur
`http://127.0.0.1:18001/search` avec token sur `nsi_corpus` a time out après
environ 20 secondes (`HTTP 000`). Le reverse proxy public n'est donc pas la cause
unique.

Action suivante : reproduire avec `scripts/rag_diagnose_search_timeout.py`, puis
inspecter les logs ingestor/Ollama/Chroma sans afficher de secret.

## Conclusion

Blocage maintenu : `rag-smoke-required` doit échouer tant que l'endpoint
authentifié `/search` time out.
