# Matrice programme ↔ manuel — 1NSI (édition 2026-2027)

Autorité programme : `MENE1901633A`, BO spécial n° 1 du 22 janvier 2019. Texte officiel archivé : `NSI/corpus_nsi/00_programmes_officiels/programme_nsi_premiere.pdf` (`sha256:7ca9a32e1823be6c1120cb0417324c3cb01688d1d194c7614a88ea851ccc60b0`).

Le détail ligne par ligne est dans `audit/PROGRAM_COVERAGE_MATRIX_1NSI.json`.

## État courant

- Lignes : 52.
- Atoms obligatoires : 50/50 mappés.
- `STRUCTURALLY_MAPPED` : 49.
- `TRANSVERSAL_NOT_CHAPTER_SCOPED` : 1, histoire de l'informatique.
- `FULL` : 0, dans l'attente des audits scientifique et pédagogique.
- Non obligatoires : 1 `OUT_OF_SCOPE_WITH_PROOF` et 1 `AUDIT_METADATA_ONLY`.
- `WRONG_YEAR` : 0.
- `UNSUPPORTED_CLAIM` : 0.

## Mutabilité Python

La distinction mutable/immuable et les effets d'alias ne constituent pas un atom officiel autonome de MENE1901633A. Ce contenu est néanmoins utile pour réaliser correctement les capacités officielles sur les p-uplets, tableaux et dictionnaires. Le contrat marque donc explicitement la capacité locale C5 `METHODOLOGY`, `mandatory_for_coverage=false`, sans `official_atom_ids`.

La ligne historique `1NSI-MATRIX-012` reste sous `AUDIT_METADATA_ONLY` et est exclue du registre des atoms officiels. Aucun arbitrage humain ne reste ouvert sur ce point.

## Points à auditer en qualité

Le placement des capteurs/actionneurs dans le chapitre Réseaux est une décision de découpage, pas un gap. Le quota officiel d'au moins un quart de l'horaire consacré aux projets doit être contrôlé dans l'audit pédagogique. Les snippets Python, leurs cas limites et leur sémantique doivent encore passer l'audit scientifique NSI exhaustif.
