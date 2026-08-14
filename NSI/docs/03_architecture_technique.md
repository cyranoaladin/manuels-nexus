# Architecture technique

## Stack
- **Python ≥ 3.11** (venv `.venv`), dépendances dans `requirements.txt`.
- **PostgreSQL ≥ 16 + pgvector** : base `corpus_manuel_maths`, schéma `db/schema.sql` (4 tables + 1 vue : capacites, chunks, objets, validations, couverture).
- **Embeddings** : BGE-M3 1024d (aligné sur la stack RAG existante) ; **reranker** CrossEncoder MiniLM ; recherche hybride vecteur (0.6) + BM25 tsvector français (0.4) puis rerank.
- **LaTeX** : texlive-full, classe `gabarits/nexus-manuel.cls`, compilation pdflatex ×2.
- **LLM externe** : OpenRouter uniquement, via `nexus_external/openrouter_client.py` et son endpoint fixe `https://openrouter.ai/api/v1/chat/completions`. Les seuls paramètres sont `OPENROUTER_API_KEY` et `OPENROUTER_MODEL` ; aucun modèle, endpoint alternatif, service de traitement par lots ou repli fournisseur n'est implicite.
- **MCP** : 4 serveurs FastMCP en stdio, déclarés dans `.mcp.json` et démarrés localement par l'orchestrateur de travail.

## Séparation des transports

- **Extraction** : `pymupdf`, `trafilatura` et OCR fonctionnent localement ; aucune image ou donnée source n'est envoyée automatiquement à un LLM.
- **Classification** : sans clé OpenRouter, l'heuristique locale est utilisée sans réseau ; une clé sans modèle provoque une erreur avant réseau.
- **Embeddings et stockage vectoriel** : BGE-M3, PostgreSQL et pgvector utilisent leur propre configuration, indépendante du client LLM.
- **Recherche RAG** : `RAG_API_BASE_URL` reste réservé au transport RAG et ne peut pas devenir un endpoint de complétion.

Avant toute consultation externe, les données doivent être autorisées,
anonymisées si nécessaire et exemptes de secret. Une réponse LLM reste
consultative : les gates locaux et la validation humaine demeurent obligatoires.

## Flux de données
```
registry.yaml -> crawl.py -> raw/{SRC}/{date}/ (+manifest)
             -> ingest.py -> corpus/**/chunk-*.json   (schéma chunk.schema.json)
                         -> classification locale ou OpenRouter explicite
             -> index.py  -> table chunks (embedding + tsv)
contrat.yaml + search_corpus -> dossier_curation.json
prompts/* + curation -> chapitres/{CHAP}/{type}/*.tex  (en-tête % META + bloc % VERIFY)
verify_sympy / similarity_check / coverage_report -> chapitres/{CHAP}/validations/*.json
assemble.py -> build/{CHAP}/{CHAP}_{variant}.pdf
```

## Conventions de fichiers
- ID d'objet : `{CHAP}-{TYPE}-{NNN}` (EX, ME, CO, QCM, EV, RE, FR). Fichier = `{ID}.tex`.
- En-tête obligatoire de chaque .tex : `% META: {...}` (JSON une ligne, schéma selon type).
- Bloc de vérification : `% BEGIN-VERIFY ... % END-VERIFY` (lignes préfixées `% `).
- Verdicts : `chapitres/{CHAP}/validations/{ID}.{gate}.json` (schéma validation.schema.json). Revue humaine : `{ID}.revue_humaine.json` écrit MANUELLEMENT uniquement.

## Déploiement
- Base + éventuellement MCP corpus : serveur Hetzner existant (tunnel SSH ou exposition privée).
- Agents : orchestrateur local à la racine du dépôt ; les serveurs MCP démarrent en stdio local.
- CI : GitHub Actions (`.github/workflows/ci.yml`), gates légers uniquement (sans embeddings) ; les gates lourds tournent en local/serveur avant push.
- Réseau LLM : aucune consultation OpenRouter ni aucun smoke LLM n'est lancé automatiquement par les tests ou la CI.
