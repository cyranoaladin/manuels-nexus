# Stratégie des banques

## Décision

Option A retenue : les dossiers `sequences/...` sont la source unique.

Les dossiers `banques/...` ne doivent contenir aucun duplicat manuel de cours, TD, TP, évaluation, corrigé, QCM ou fichier Python. Ils contiennent seulement des index qui référencent les ressources sources.

## Règles

- Les ressources pédagogiques sont écrites et relues dans `premiere/sequences/...` ou `terminale/sequences/...`.
- Les banques sont des vues d'orientation, pas des copies.
- Toute copie de contenu pédagogique dans `banques/` est une dette technique.
- Si un export de banque est nécessaire, il doit être généré par script avec traçabilité de la source.
- Les corrigés et guides professeurs restent référencés séparément des ressources élèves.

## Etat actuel

- Les copies exactes précédentes ont été supprimées des banques.
- Les index de banque restent à générer à partir du manifeste.
- Les doublons par hash doivent être interprétés comme incidents sauf s'il s'agit d'un export généré documenté ou d'un lien symbolique assumé.
