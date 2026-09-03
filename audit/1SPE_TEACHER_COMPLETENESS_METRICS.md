# Gate — completude professeur du manuel 1SPE

Genere par `scripts/build_1spe_teacher_completeness_metrics.py`.

| METRIC_NAME | EXPECTED | OBSERVED | GAP | STATUS |
| --- | --- | --- | --- | --- |
| TEACHER_CORRECTION_PER_CORRECTABLE_OBJECT | 502 | 502 | 0 | PASS |
| TEACHER_QCM_ANSWER_KEY_PER_DECLARED_QUESTION | 168 | 168 | 0 | PASS |
| TEACHER_BAREME_PER_GRADED_OBJECT | 20 | 8 | 12 | FAIL |
| STUDENT_VARIANT_CORRECTION_OBJECTS | 0 | 0 | 0 | PASS |
| STUDENT_VARIANT_BAREME_CARRIERS | 0 | 0 | 0 | PASS |
| STUDENT_VARIANT_QCM_ANSWER_KEYS | 0 | 0 | 0 | PASS |

| METRIC_NAME | VALEUR |
| --- | --- |
| TEACHER_MISSING_REQUIRED_CONTENT | 12 |
| STUDENT_TEACHER_ONLY_LEAKS | 0 |
| GATE | FAIL |

## Derivation de chaque EXPECTED

- `TEACHER_CORRECTION_PER_CORRECTABLE_OBJECT` : objets publies dont le type est declare corrigeable par le corpus (evaluation, exercice)
- `TEACHER_QCM_ANSWER_KEY_PER_DECLARED_QUESTION` : questions declarant leur reponse dans le JSON canonique du QCM publie
- `TEACHER_BAREME_PER_GRADED_OBJECT` : objets publies dont la META declare un total de points numerique
- `STUDENT_VARIANT_CORRECTION_OBJECTS` : la variante eleve ne publie aucun objet de correction
- `STUDENT_VARIANT_BAREME_CARRIERS` : aucun porteur de bareme de la charte hors zone gardee professeur dans la variante eleve
- `STUDENT_VARIANT_QCM_ANSWER_KEYS` : aucune ligne de cle de correction hors zone gardee professeur dans la variante eleve

## Ecarts

### TEACHER_BAREME_PER_GRADED_OBJECT

- `1SPE-DERLOCAL-EV-A` — NO_CHARTER_BAREME_CARRIER_IN_CORRECTION
- `1SPE-DERLOCAL-EV-B` — NO_CHARTER_BAREME_CARRIER_IN_CORRECTION
- `1SPE-DERGLOBAL-EV-A` — NO_CHARTER_BAREME_CARRIER_IN_CORRECTION
- `1SPE-DERGLOBAL-EV-B` — NO_CHARTER_BAREME_CARRIER_IN_CORRECTION
- `1SPE-EXPO-EV-A` — NO_CHARTER_BAREME_CARRIER_IN_CORRECTION
- `1SPE-EXPO-EV-B` — NO_CHARTER_BAREME_CARRIER_IN_CORRECTION
- `1SPE-PRODSCAL-EV-A` — NO_CHARTER_BAREME_CARRIER_IN_CORRECTION
- `1SPE-PRODSCAL-EV-B` — NO_CHARTER_BAREME_CARRIER_IN_CORRECTION
- `1SPE-GEOREP-EV-A` — NO_CHARTER_BAREME_CARRIER_IN_CORRECTION
- `1SPE-GEOREP-EV-B` — NO_CHARTER_BAREME_CARRIER_IN_CORRECTION
- `1SPE-PROBCOND-EV-A` — NO_CHARTER_BAREME_CARRIER_IN_CORRECTION
- `1SPE-PROBCOND-EV-B` — NO_CHARTER_BAREME_CARRIER_IN_CORRECTION

## Verification secondaire sur les PDF candidats

Role de preuve : `SECONDARY_NON_AUTHORITATIVE` (statut `READ`).

| PDF | sha256 | pages | occurrences « bareme » | titres reserves professeur |
| --- | --- | --- | --- | --- |
| `Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf` | `ff0c263bf01480a49e0037dd81b3765534853b236b1dd04311dc1555ddf36953` | 357 | 0 | 0 |
| `Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf` | `35b502fa925c7d4003fe7f7f2d8257d335b82e164b27757a0ebe0e86f3456662` | 629 | 77 | 10 |
