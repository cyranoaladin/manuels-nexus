# Smoke OpenRouter - dix P0 scientifiques 1NSI

- Date : 2026-08-10
- Périmètre : tentative de consultation indépendante après indisponibilité Chutes
- Données transmises : aucune source du manuel, aucun secret dans le dépôt

## Résultat

L'endpoint public des modèles a confirmé la disponibilité de plusieurs modèles adaptés,
dont `openai/gpt-oss-120b`. La clé fournie pour la consultation a été lue uniquement par
une saisie masquée en mémoire. L'appel de chat a échoué avec `HTTP 401 Unauthorized`.
Aucune réponse de modèle et aucune expertise OpenRouter n'ont été obtenues.

## Cache prévu

Pour une éventuelle nouvelle clé valide, les appels utiliseront un `session_id` stable par
lot et un contexte invariant placé avant la question variable afin de favoriser le cache de
prompt. Les directives `cache_control` seront ajoutées pour les modèles qui l'exigent. Le
cache de réponse ne sera utilisé que pour une requête strictement identique.

## Décision

Ne pas réutiliser la clé rejetée et poursuivre avec les relecteurs indépendants orchestrés.
L'échec OpenRouter ne vaut pas validation disciplinaire.
