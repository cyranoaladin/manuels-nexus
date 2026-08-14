# Architecture technique

## Stack
- **Python ≥ 3.11** (venv `.venv`), dépendances dans `requirements.txt`.
- **PostgreSQL ≥ 16 + pgvector** : base `corpus_manuel_maths`, schéma `db/schema.sql` (4 tables + 1 vue : capacites, chunks, objets, validations, couverture).
- **Embeddings** : BGE-M3 1024d (aligné sur la stack RAG existante) ; **reranker** CrossEncoder MiniLM ; recherche hybride vecteur (0.6) + BM25 tsvector français (0.4) puis rerank.
- **LaTeX** : texlive-full, classe `gabarits/nexus-manuel.cls`, compilation pdflatex ×2.
- **LLM externe** : OpenRouter uniquement, par `POST https://openrouter.ai/api/v1/chat/completions`, authentifié avec `OPENROUTER_API_KEY` et le modèle exact de `OPENROUTER_MODEL`. Aucun endpoint ou modèle de repli n'est implicite. Sans clé, la classification reste locale, déterministe et hors réseau ; une clé sans modèle échoue avant réseau. Les réponses sont consultatives, vérifiées localement et ne valent aucune validation disciplinaire ou humaine. Aucun secret ni donnée personnelle n'est transmis. Tout smoke test reste humain, jamais CI ou automatique.
- **MCP** : 4 serveurs FastMCP en stdio, déclarés dans `.mcp.json` et chargés par l'environnement agentique local à l'ouverture du projet.

## Flux de données
```
registry.yaml -> crawl.py -> raw/{SRC}/{date}/ (+manifest)
             -> ingest.py -> extraction/normalisation -> classification locale
                                               ou OpenRouter explicitement configuré
                        -> corpus/**/chunk-*.json   (schéma chunk.schema.json)
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
- Agents : agent de production local ; les serveurs MCP démarrent en stdio local.
- CI : GitHub Actions (`.github/workflows/ci.yml`), gates légers uniquement (sans embeddings) ; les gates lourds tournent en local/serveur avant push.
