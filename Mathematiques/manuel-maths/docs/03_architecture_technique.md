# Architecture technique

## Stack
- **Python ≥ 3.11** (venv `.venv`), dépendances dans `requirements.txt`.
- **PostgreSQL ≥ 16 + pgvector** : base `corpus_manuel_maths`, schéma `db/schema.sql` (4 tables + 1 vue : capacites, chunks, objets, validations, couverture).
- **Embeddings** : BGE-M3 1024d (aligné sur la stack RAG existante) ; **reranker** CrossEncoder MiniLM ; recherche hybride vecteur (0.6) + BM25 tsvector français (0.4) puis rerank.
- **LaTeX** : texlive-full, classe `gabarits/nexus-manuel.cls`, compilation pdflatex ×2.
- **LLM** : Anthropic — Haiku (classification de chunks), Sonnet (production de masse), Opus/Fable (strate ★, ◆◆◆, adversarial). Batch API pour les lots non interactifs (coûts ÷2).
- **MCP** : 4 serveurs FastMCP en stdio, déclarés dans `.mcp.json` (chargés automatiquement par Claude Code à l'ouverture du projet).

## Flux de données
```
registry.yaml -> crawl.py -> raw/{SRC}/{date}/ (+manifest)
             -> ingest.py -> corpus/**/chunk-*.json   (schéma chunk.schema.json)
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
- Agents : Claude Code local (`claude` à la racine du dépôt) ; les serveurs MCP démarrent en stdio local.
- CI : GitHub Actions (`.github/workflows/ci.yml`), gates légers uniquement (sans embeddings) ; les gates lourds tournent en local/serveur avant push.
