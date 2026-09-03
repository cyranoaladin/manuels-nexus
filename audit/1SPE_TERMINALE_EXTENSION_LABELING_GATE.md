# Gate — contenu de niveau Terminale etiquete (manuel 1SPE)

Genere par `scripts/build_1spe_terminale_extension_labeling_gate.py`.

| METRIC_NAME | VALEUR |
| --- | --- |
| PUBLISHED_WRONG_LEVEL_OCCURRENCES | 98 |
| UNLABELED_WRONG_LEVEL_TERMINALE_CONTENT | 0 |
| GATE | PASS |

## Repartition

| CLASSIFICATION | OCCURRENCES |
| --- | --- |
| CHARTER_OUT_OF_TRACK_MACRO | 1 |
| EXPLICIT_LEVEL_DEFERRAL_PARENTHETICAL | 2 |
| INLINE_DECLARED_EXTENSION_LABEL | 6 |
| META_PROGRAMME_ALIGNMENT | 89 |

## Derivation

- surface publiee : `Mathematiques/manuel-maths/scripts/assemble_manuel.py::collect_chapter` (1436 fichiers)
- sources portant une occurrence : 94
- empreinte de ces sources : `sha256:45fe99459089abdfdef3937271a9e7db2e8d846ea8ce2f2cdcb94e0586bd6a0c`
- niveaux etrangers derives de l'assembleur : « Terminale spécialité », « Terminale — maths complémentaires », « Terminale — maths expertes »
- etiquettes d'extension derivees des META : « Approfondissement — Vers la Terminale »
- macros hors parcours derivees de la charte : `\approfondissement`

Aucune occurrence publiee de niveau etranger hors extension optionnelle declaree ou hors renvoi de niveau explicite.
