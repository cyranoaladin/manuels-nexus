# Index des pré-jugements de substance

Ces verdicts sont des pré-jugements outillés. Ils vérifient des ancres et citations, mais ne remplacent pas une revue humaine.

## Périmètre pilote

| Unité | Verdict | Capacités pilotes | État attendu |
| --- | --- | --- | --- |
| P05 | `03_progressions/supports/premiere/P05/_substance_review.json` | P-TABLE-01, P-TABLE-02 | `needs_content` |
| P06 | `03_progressions/supports/premiere/P06/_substance_review.json` | P-TABLE-03, P-TABLE-04 | `needs_content` |
| T06 | `03_progressions/supports/terminale/T06/_substance_review.json` | T-ALGO-01E, T-ALGO-01F | `needs_content` |
| T07 | `03_progressions/supports/terminale/T07/_substance_review.json` | T-STRUCT-05A, T-STRUCT-05B, T-STRUCT-05C, T-STRUCT-05D | `needs_content` |
| T08 | `03_progressions/supports/terminale/T08/_substance_review.json` | T-ALGO-02A, T-ALGO-02B, T-ALGO-02C, T-ALGO-02D | `needs_content` |
| T10 | `03_progressions/supports/terminale/T10/_substance_review.json` | T-BDD-03A, T-BDD-03B, T-BDD-03C, T-BDD-03D, T-BDD-03E, T-BDD-03F, T-BDD-03G, T-BDD-03H | `needs_content` |
| T17 | `03_progressions/supports/terminale/T17/_substance_review.json` | T-ALGO-04 | `needs_content` |
| T18 | `03_progressions/supports/terminale/T18/_substance_review.json` | T-ALGO-05 | `needs_content` |

## Garde-fou adverse

Le fichier `substance_reviews/_adversarial/poisoned.verdict.json` doit être refusé par `scripts/check_substance_anchors.py`.

## Statut

Aucun verdict ne promeut une ressource. Les statuts restent `needs_review`, `covered = 0`, `validated_* = 0`, `published = 0`.
