# Plan séparé de correction serveur RAG

Statut : plan proposé, non exécuté. Aucune modification serveur n'est appliquée
dans cette passe de consolidation dépôt.

## Hypothèses de correction

- Hypothèse timeout app : le handler `/search` bloque sans timeout interne assez
  court ni log par étape.
- Hypothèse endpoint `/search` bloque dans Chroma : la requête collection ou la
  query vectorielle ne retourne pas.
- Hypothèse mauvais appel embedding : le service appelle un modèle ou endpoint
  différent du smoke direct Ollama.
- Hypothèse collection trop lente ou absente : l'initialisation ou la query de
  collection dépasse le timeout client.
- Hypothèse logs insuffisants : les logs actuels ne permettent pas de localiser
  la phase bloquante sans instrumentation.

## Diagnostic proposé

1. Ajouter temporairement un `request_id` par appel `/search`.
2. Journaliser sans secret les temps : validation payload, auth, embedding,
   lookup collection, query Chroma, formatage réponse.
3. Tester `k=1` avec `include_documents=false`, puis `true`.
4. Tester `nsi_corpus`, `rag_education`, puis une collection minimale connue.
5. Capturer les logs ingestor/Ollama/Chroma filtrés.

## Commandes de test proposées

```bash
curl -sS -m 5 "$RAG_API_BASE_URL/../health"
python scripts/rag_diagnose_search_timeout.py
make rag-smoke-required
```

Les commandes utilisant un token doivent masquer la valeur de `RAG_API_KEY` et
ne jamais afficher l'en-tête `Authorization`.

## Rollback

- Ne modifier qu'un fichier applicatif à la fois.
- Conserver une copie de la configuration courante.
- Redémarrer uniquement le service concerné.
- Si le smoke `/health` ou `/search` régresse, revenir au commit/config serveur
  précédent et documenter le SHA ou l'image.

## Impact utilisateur

Tant que le timeout persiste, le juge de substance ne peut pas s'appuyer sur le
RAG réel. Les statuts restent `needs_review` ou `needs_content`; aucune
couverture interne n'est validée par RAG.
