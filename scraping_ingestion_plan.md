# Plan d'ingestion des sources scrapées

## Étapes obligatoires

1. Déclarer la source dans `sources_catalog.yml`.
2. Vérifier licence, statut RGPD, collection cible et politique de réutilisation.
3. Préparer un dry-run avec `scripts/prepare_scraped_docs_for_rag.py --dry-run`.
4. Vérifier les métadonnées avec `scripts/check_sources_catalog.py` et
   `scripts/check_rag_index_metadata.py`.
5. Soumettre le plan à revue humaine avant toute ingestion réelle.

## Décisions de routage

- `nsi_corpus` : seulement les supports internes produits et non sensibles.
- `rag_education` : inspiration, Drive audité, ressources ouvertes non internes.
- `nsi_official` : textes institutionnels.
- `nsi_annales` : annales publiques.

## Rollback

Toute ingestion réelle doit documenter l'identifiant de lot, les chemins sources,
les hash SHA-256 des documents préparés et la collection cible. En l'absence de
ces informations, l'ingestion est bloquée.
