# LOT 1 — Corpus du chapitre 1SPE-DERIVATION-LOCAL

## Exécution

- `make crawl SRC=SRC-0001` : 0 URL PDF découverte sur la page Éduscol active ; robots et périmètre du registre respectés.
- `make ingest` : 0 chunk normalisé.
- `make index` non exécuté : MODE FICHIERS, sans PostgreSQL dédié.

## Verdict

- Aucun brief de corpus n'est disponible : angle mort documenté pour C1 à C5.
- Passage en génération ex nihilo pour la curation, en s'appuyant exclusivement sur le référentiel extrait du BO 2026.
- Aucun contenu source n'est repris ; la similarité restera contrôlée contre les éventuels chunks JSON ultérieurs.

## Coût API estimé

0 $.
