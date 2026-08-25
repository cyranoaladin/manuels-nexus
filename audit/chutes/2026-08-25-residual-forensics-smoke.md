# Chutes — smoke test forensics résiduels

- Date : 2026-08-25
- Périmètre : second regard consultatif sur la sémantique du ledger résiduel
- Données transmises : uniquement des cardinalités et règles abstraites de gouvernance ; aucun secret ni donnée personnelle
- Décision locale ou baseline déléguée : aucune

## Smoke test

- `list_models` : PASS, 14 modèles annoncés disponibles.
- Modèle tenté : `Qwen/Qwen3-32B-TEE`.
- `chat_complete` : FAIL HTTP 402 (`quota exceeded`).
- Expertise distante obtenue : aucune.

## Conséquence

Chutes reste consultatif et indisponible pour ce lot faute de quota. Les preuves
retenues sont les tests locaux, les artefacts forensiques versionnés et les
revues contradictoires locales. Aucune validation humaine, scientifique,
pédagogique ou de publication n'est inférée de ce smoke test.
