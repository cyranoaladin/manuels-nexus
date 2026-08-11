# RAG — État des lieux vérifié

## Schéma déployé (serveur legacy, prouvé par requête)

Commande de preuve (2026-06-30, lecture seule, clé masquée) :
POST /search {q: "CSV", collection: "nsi_corpus", k: 2}
→ hit[0] metadata keys: ['anchor', 'capacities', 'chunk_index', 'collection',
   'document_type', 'level', 'notion', 'path', 'sequence_id', 'sha256',
   'source_type', 'status', 'theme']

Champs legacy observés : anchor, capacities (chaîne).
Champs canoniques absents : section_anchor, capacity_ids (liste).

## Schéma canonique dépôt NSI

Défini dans rag_config.example.yml, 01_charte et ingest_nsi_corpus.py :
- section_anchor (str, obligatoire) : slug de section Markdown
- capacity_ids (list[str], obligatoire) : identifiants capacité programme
- document_type (str) : support, fiche_cours, code, tests_code, corrige_code
- status (str) : needs_review | needs_content | draft
- path (str) : chemin relatif depuis la racine
- level (str) : premiere | terminale
- theme, notion, sequence_id (str) : classification pédagogique
- sha256 (str) : hash du fichier source
- collection (str) : nsi_corpus | rag_education | nsi_golden_examples
- source_type (str) : nsi_corpus | golden_example | excluded
- proof_scope (str) : internal_coverage_candidate | style_reference_only
- private_data (bool) : doit être false

## Schéma Nexus (RAG dépôt, rag_collections.yml)

Complètement différent du schéma legacy :
- domain, audience, niveau, voie, matiere, statut_enseignement, type_doc
- source_kind, rights, review_status, source_label, source_uri
- doc_id, chunk_id, chunk_sha256

Collections Nexus : rag_nexus_education, rag_nexus_official, rag_nexus_exams,
rag_nexus_owned, rag_nexus_web3, rag_nexus_quarantine.

## Modèle d'embedding

nomic-embed-text (dimension 768, distance cosine), via Ollama.

## Topologie conteneurs (serveur korrigo, 88.99.254.59)

- FastAPI ingestor (POST /search, /ingest, /health)
- ChromaDB (stockage vectoriel persistant)
- Ollama (embedding nomic-embed-text + LLM qwen2.5:7b)
- Streamlit UI (rag-ui.nexusreussite.academy)
- Transition vers pgvector documentée mais non déployée

## PR #35 RAG — contenu mergé

29 fichiers dont : admin_api, collection_config, retrieval_contract_adapter,
rag_collections.yml, legacy_collection_mapping.yml, docker-compose.prod.yml,
8 tests. Travail non déployé (serveur utilise le schéma legacy).
