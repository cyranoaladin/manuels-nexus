# PR #35 du dépôt RAG — Statut vérifié

## État réel (vérifié par `gh pr view 35 --repo cyranoaladin/RAG`)

- Dépôt : cyranoaladin/RAG
- PR #35 : état **MERGED** (pas closed-without-merge)
- Branche : lot-19-audit-prod-collections → main
- Head SHA : 677fd0a1c54a12a7e040d65fe2fb6f3f4c7c672a
- Mergée le : 2026-06-29T15:06:10Z
- Par : cyranoaladin
- URL : https://github.com/cyranoaladin/RAG/pull/35

## Correction du rapport précédent

Le rapport de réconciliation disait "PR #35 fermée" en titre. C'est **inexact** :
la PR est MERGED, pas fermée sans merge. Le brief demandait une fermeture sans
merge, mais la PR était déjà mergée avant le début de la passe. L'opération
demandée était inapplicable.

## Contenu introduit dans RAG/main (évalué passe 3)

```
gh api repos/cyranoaladin/RAG/pulls/35/files --jq '.[].filename'
```

29 fichiers introduits, dont :
- CI : `.github/workflows/ci.yml`
- Documentation : `docs/rag_dual_engine_transition.md`, 5 rapports Lot 19
- Config : `services/rag-engine/configs/rag_collections.yml`, `legacy_collection_mapping.yml`
- Code : `services/rag-engine/src/ingestor/` (admin_api, collection_config, retrieval_contract_adapter)
- Tests : 8 fichiers de test
- Infrastructure : `docker-compose.prod.yml`

## Évaluation d'impact

Le contenu mergé n'est PAS un lot vide : c'est un travail substantiel d'audit
des collections de production, avec configuration, code d'ingestion et tests.
Le code est dans le dépôt RAG (pas NSI) et n'affecte pas le dépôt NSI directement.

**Risque** : le code mergé peut être incomplet ou non testé en production.
Le serveur RAG (88.99.254.59) utilise toujours le schéma legacy
(`anchor`/`capacities`), ce qui suggère que le code mergé n'a pas été déployé.

**Recommandation** : audit du code mergé dans RAG/main lors d'un lot RAG dédié.
Aucun revert cette passe (interdit). Pas d'impact sur le dépôt NSI.

## Action

Aucune action sur le dépôt NSI. Impact documenté. Revert non recommandé
sans audit préalable du code introduit.
