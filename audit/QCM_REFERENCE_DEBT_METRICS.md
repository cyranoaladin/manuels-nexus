# QCM — deux dettes de renvoi, jamais un seul « 108 »

Les deux metriques sont distinctes et ne doivent plus jamais etre designees par le seul nombre 108 : l'une compte des renvois presents mais non resolus, l'autre des distracteurs dont le renvoi ou le diagnostic manque.

| Métrique | Cardinal | Digest |
|---|---:|---|
| `TSPE_BROKEN_REMEDIATION_REFERENCES` | 0 | `sha256:4f53cda18c2baa0c…` |
| `GLOBAL_BROKEN_REMEDIATION_REFERENCES` | 0 | `sha256:4f53cda18c2baa0c…` |
| `GLOBAL_DISTRACTORS_MISSING_DIAGNOSTIC_OR_REFERENCE` | 108 | `sha256:9b8abee3f8f85590…` |
| `MISSING_DIAGNOSTIC_ONLY` | 0 | `sha256:4f53cda18c2baa0c…` |
| `MISSING_REFERENCE_ONLY` | 108 | `sha256:9b8abee3f8f85590…` |
| `MISSING_BOTH` | 0 | `sha256:4f53cda18c2baa0c…` |
| `REQUIRED_DISTRACTOR_DIAGNOSTIC_MISSING` | 0 | `sha256:4f53cda18c2baa0c…` |
| `REQUIRED_REMEDIATION_REFERENCE_MISSING` | 108 | `sha256:9b8abee3f8f85590…` |

## Décomposition du OU

Le `OU` de la métrique globale se décompose en trois classes disjointes ;
la dette contractuellement obligatoire est nommée séparément, avec un
objectif de zéro pour chacune.

## Distribution

- `GLOBAL_DISTRACTORS_MISSING_DIAGNOSTIC_OR_REFERENCE` : TSPE-DERIVATION-CONVEXITE 36, TSPE-GEOMETRIE-ESPACE 15, TSPE-LOGARITHME 15, TSPE-PRIMITIVES-EQDIFF 12, TSPE-PROBABILITES 15, TSPE-TRIGONOMETRIE 15
- `MISSING_REFERENCE_ONLY` : TSPE-DERIVATION-CONVEXITE 36, TSPE-GEOMETRIE-ESPACE 15, TSPE-LOGARITHME 15, TSPE-PRIMITIVES-EQDIFF 12, TSPE-PROBABILITES 15, TSPE-TRIGONOMETRIE 15
- `REQUIRED_REMEDIATION_REFERENCE_MISSING` : TSPE-DERIVATION-CONVEXITE 36, TSPE-GEOMETRIE-ESPACE 15, TSPE-LOGARITHME 15, TSPE-PRIMITIVES-EQDIFF 12, TSPE-PROBABILITES 15, TSPE-TRIGONOMETRIE 15
