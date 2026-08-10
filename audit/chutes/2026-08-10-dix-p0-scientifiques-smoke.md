# Smoke Chutes - dix P0 scientifiques 1NSI

- Date : 2026-08-10
- Périmètre : disponibilité consultative avant correction des dix P0 1NSI
- Données transmises : aucune source du manuel, aucun secret, aucune donnée personnelle

## Résultat

La découverte des modèles a répondu et a notamment annoncé les modèles TEE suivants :

- `Qwen/Qwen3-32B-TEE` ;
- `Qwen/Qwen3.5-397B-A17B-TEE` ;
- `google/gemma-4-31B-turbo-TEE` ;
- `zai-org/GLM-5.1-TEE` ;
- `deepseek-ai/DeepSeek-V3.2-TEE`.

La lecture du quota n'a pas pu accéder à l'empreinte d'authentification locale. Un appel
minimal à `Qwen/Qwen3-32B-TEE`, sans contenu du dépôt, a ensuite échoué avec `HTTP 402`
(`Quota exceeded`). Aucune expertise Chutes n'a donc été utilisée.

## Décision

Poursuivre avec les tests locaux et les relecteurs indépendants orchestrés. Chutes reste
consultatif et son indisponibilité n'est pas interprétée comme une validation disciplinaire.
