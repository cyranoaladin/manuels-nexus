# Gate — completude professeur du manuel 1SPE

Genere par `scripts/build_1spe_teacher_completeness_metrics.py`.

| METRIC_NAME | EXPECTED | OBSERVED | GAP | STATUS |
| --- | --- | --- | --- | --- |
| TEACHER_CORRECTION_PER_CORRECTABLE_OBJECT | 502 | 502 | 0 | PASS |
| TEACHER_QCM_ANSWER_KEY_PER_DECLARED_QUESTION | 168 | 168 | 0 | PASS |
| TEACHER_BAREME_PER_GRADED_OBJECT | 20 | 18 | 2 | FAIL |
| STUDENT_VARIANT_CORRECTION_OBJECTS | 0 | 0 | 0 | PASS |
| STUDENT_VARIANT_BAREME_CARRIERS | 0 | 0 | 0 | PASS |
| STUDENT_VARIANT_QCM_ANSWER_KEYS | 0 | 0 | 0 | PASS |

| METRIC_NAME | VALEUR |
| --- | --- |
| TEACHER_MISSING_REQUIRED_CONTENT | 2 |
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

- `1SPE-GEOREP-EV-A` — NO_CHARTER_BAREME_CARRIER_IN_CORRECTION
- `1SPE-GEOREP-EV-B` — NO_CHARTER_BAREME_CARRIER_IN_CORRECTION

## Verification secondaire sur les PDF candidats

Role de preuve : `SECONDARY_NON_AUTHORITATIVE` (statut `READ`).

| PDF | sha256 | pages | occurrences « bareme » | titres reserves professeur |
| --- | --- | --- | --- | --- |
| `Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf` | `39c6a8541f4b35d8da9f4cc18810f79bc364d00dab08c0c50261c387d0d42259` | 355 | 0 | 0 |
| `Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf` | `dc5f2575f5f7cd0bd9e5654ac20291e6c3b03410caa150959e28ab6cdd3d059c` | 627 | 122 | 10 |
