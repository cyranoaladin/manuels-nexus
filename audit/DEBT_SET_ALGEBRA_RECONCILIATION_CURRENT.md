# Algèbre des ensembles de dette — état courant

Les ensembles, pas les nombres. Chaque classe porte son cardinal et le
digest de son ensemble d'empreintes ; leur union est exactement
l'actif courant, sans recouvrement et sans inconnu.

## Pourquoi la soustraction naïve échoue

`6541 - 5371 = 1170` — et non 2232.

951 des 5371 empreintes archivees n'ont jamais appartenu a la baseline de reference.

Expression correcte : `|REFERENCE_BASELINE| - |RESOLVED_REFERENCE| + |POST_REFERENCE_ACTIVE| = 6541 - 4420 + 111 = 2232`.

## Ensembles

| Ensemble | Cardinal | Digest |
|---|---:|---|
| `REFERENCE_BASELINE` | 6541 | `sha256:3757764ead6d1a4f…` |
| `RESOLVED_REFERENCE` | 4420 | `sha256:6afe2c9222e17668…` |
| `SURVIVING_REFERENCE` | 2121 | `sha256:2e34cc80ac659d42…` |
| `REFERENCE_UNTRACED` | 0 | `sha256:4f53cda18c2baa0c…` |
| `RESOLVED_PRE_REFERENCE` | 951 | `sha256:e3446ae1871fc650…` |
| `POST_REFERENCE_ACTIVE` | 111 | `sha256:ccac6002f6792f75…` |
| `A4_METHOD_REVIEW_DEBT` | 86 | `sha256:efd51c1aa6186d77…` |
| `TRIGO_OPTIONAL_EXTENSION_DEBT` | 3 | `sha256:55ae8601afda2e8a…` |
| `RESIDUAL_QUALIFIED_REVIEW_DEBT` | 13 | `sha256:1abe51ad406752b1…` |
| `NSI_STATUS_GOVERNANCE_DEBT` | 9 | `sha256:6bbc27478ab13ccf…` |
| `OTHER_CURRENT_DEBT` | 0 | `sha256:4f53cda18c2baa0c…` |
| `CURRENT_ACTIVE` | 2232 | `sha256:fe10197d9af6d566…` |

## Partition de l'actif courant

`2232 = 2121 + 86 + 13 + 9 + 3`

Les classes restent **distinctes** : fondre les treize résiduelles ou
les extensions optionnelles TRIGO dans la classe A4 rendrait leur
sunset inauditable.

## Renommage de métrique

Le champ `resolved` de la baseline vaut 5371 : ce n'est **pas** `REFERENCE_BASELINE_RESOLVED` (4420), mais `RESOLVED_ARCHIVE_ALL_GENERATIONS`. Le champ lui-même n'est pas
renommé : aucune mise à jour de baseline n'est autorisée.

## Ambiguïté d'ancre

deux versions distinctes du fichier de baseline portent le meme git_sha 7752988a (2866 puis 6541 actives) : l'ancre par git_sha ne designe pas un ensemble unique, le blob si.
