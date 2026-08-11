# Politique des rapports de validation

## Statut

Les dossiers `reports/lot*/` peuvent contenir des journaux de validation, des
preuves de commandes et des rapports de clôture techniques. Ils ne sont pas des
ressources pédagogiques et ne prouvent aucune couverture du programme.

## Règles

- `reports/lot*/` ne doit pas apparaître dans `manifest.csv` comme ressource pédagogique.
- `reports/lot*/` ne doit pas être indexé dans le RAG.
- `reports/lot*/` ne doit pas apparaître dans `coverage.md` ni dans `coverage_sources.md`.
- `reports/lot*/` peut être inclus dans `dist/source_clean.tar.gz` si la taille cumulée reste inférieure ou égale à 2 Mo.
- Aucun fichier `.env`, token, clé privée, donnée élève, `NotesEleves.csv` ou `Fichier_Eleves.csv` ne doit être présent sous `reports/lot*/`.

## Décision

Seuls les rapports de validation versionnés et non sensibles sont conservés. Les
rapports ne changent aucun statut : toutes les ressources restent `needs_review`
tant qu'une revue humaine conforme n'est pas tracée.
