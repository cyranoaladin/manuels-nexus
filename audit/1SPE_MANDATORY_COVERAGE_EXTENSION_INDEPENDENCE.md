# Gate — une extension optionnelle ne credite pas le programme obligatoire

Manuel `1SPE`. Genere par `scripts/build_1spe_mandatory_coverage_extension_independence.py`.

| METRIC_NAME | VALEUR |
| --- | --- |
| MANDATORY_ATOMS | 133 |
| MANDATORY_COVERAGE_FROM_EXTENSION_ONLY | 0 |
| MANDATORY_ATOMS_WITH_ANY_EXTENSION_CREDIT | 0 |
| CREDITED_SOURCES_MISSING_ON_DISK | 0 |
| GATE | PASS |

## Verdict par atome

| VERDICT | ATOMES |
| --- | --- |
| CREDITED_WITHOUT_EXTENSION | 107 |
| NO_CREDITING_SOURCE | 26 |

`NO_CREDITING_SOURCE` est une dette de contenu deja enregistree par la couverture officielle ; ce gate ne la traite pas, il interdit seulement qu'une extension la referme.

## Entrees

- couverture par manuel : `audit/official_program_coverage/1SPE.json`
- couverture agregee : `audit/OFFICIAL_PROGRAM_COVERAGE_2026_2027.json`
- objets declares en extension : 3 via `audit/HUMAN_DECISION_1SPE_TRIGO_OPTIONAL_EXTENSIONS_2026-08-23.json` et les META `programme_alignment` des sources creditees

Aucun atome obligatoire n'est couvert uniquement par des objets d'extension optionnelle.
