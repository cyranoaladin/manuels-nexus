# Reconciliation des metriques autoritaires

Toutes les valeurs ci-dessous sont calculees sur **un seul arbre** :
`CANONICAL_SIDE_CAR_SHA = d10c6defde47779ce3fa8002ba058014b8b1829e`.

Aucune valeur calculee sur un autre arbre n'est presentee comme une
contradiction intrinseque. `UNKNOWN = 0`.

| Metrique | Ancien | Nouveau | Reproduit | Cause de l'ecart |
|---|---:|---:|---|---|
| `OFFICIAL_SOURCE_SEGMENTS` | 985 | 985 | oui | aucune divergence : la valeur se reproduit |
| `OFFICIAL_ATOMS` | 919 | 919 | oui | aucune divergence |
| `MANDATORY_ATOMS` | 596 | 596 | oui | mesure inter-arbres presentee a tort comme contradiction |
| `ATOMIZATION_SECOND_PASS_DISAGREEMENT_FAMILIES` | 0 | 0 | oui | aucune divergence |
| `RESIDUAL_13_SET` | 13 | 13 | oui | aucune divergence : l'ensemble exact se reproduit |
| `PREVIOUS_89_SET` | 89 | 89 | oui | deux ensembles distincts designes par un seul libelle |
| `STRICT_TEX_STYLE_FILES` | — | 33 | oui | perimetre le plus etroit |
| `RUNTIME_GRAPHIC_SUPPORT` | 63 | 72 | oui | perimetre incomplet, non contradiction |
| `FULL_PUBLISHING_STYLE_ASSETS` | — | 140 | oui | perimetre le plus large |
| `CHAPTER_CAPACITY_PAIRS_WITHOUT_ANY_QCM` | 70 | 48 | oui | 70 mesure l'arbre perime augmente du WIP, 48 l'arbre canonique. Le libelle 'QCM gaps' recouvrait les deux. |

## Programme

Les trois grandeurs annoncees se reproduisent exactement, avec le generateur
canonique, sur ce SHA :

```
segments  985
atomes    919
obligatoires 596
15 familles de desaccord de seconde passe : 0
```

`build_official_program_coverage.py --check` repond
`official programme coverage current: 596/596`.

L'affirmation precedente de non-reproductibilite de 596 etait une mesure faite
sur l'arbre `761508d9` avec un autre outil. Elle n'invalidait rien.

## Dette : deux ensembles, pas un

Le libelle « sunset 13/89 » melait deux grandeurs distinctes :

| Ensemble | Cardinal | Empreinte | Verdict |
|---|---:|---|---|
| `RESIDUAL_13_SET` | 13 | `sha256:1abe51ad406752b1e09996020c1afb2db3982ac2741cf98ed7b2118f302ace98` | `PENDING_HUMAN_REVIEW_RELEASE_BLOCKING` |
| `PREVIOUS_89_SET` | 89 | `sha256:8daf2b85cecb556daa788056c66060ee6e0c20d00a09c976b9bac9f1bd9d8303` | dette de revue attendue de la transition approuvee |

Les 13 empreintes exactes sont enumerees dans
`audit/BASELINE_QUALIFICATION_POLICY.yaml`, `approved_set.fingerprints`, et
`audit/BASELINE_RESIDUAL_13_EXACT_DIFF.json` porte le verdict `EXACT_MATCH`.

## Style : trois perimetres explicites

| Perimetre | Fichiers | Contenus uniques | Groupes de duplicatas |
|---|---:|---:|---:|
| `STRICT_TEX_STYLE_FILES` | 33 | 23 | 10 |
| `RUNTIME_GRAPHIC_SUPPORT` | 72 | 45 | 21 |
| `FULL_PUBLISHING_STYLE_ASSETS` | 140 | 76 | 39 |

Le chiffre historique **63** correspond a `.sty + .cls + gabarits/*.tex`, un
perimetre qui exclut les modules `.lua` pourtant charges par TeX a l'execution.
Le chiffre **21** correspond exactement aux groupes de duplicatas de
`RUNTIME_GRAPHIC_SUPPORT`. Les deux venaient donc de deux perimetres differents,
et non d'une contradiction. La canonicalisation porte sur
`RUNTIME_GRAPHIC_SUPPORT`.

## QCM : quatre metriques nommees

Le terme « QCM gaps » n'est plus utilise.

| Metrique | Valeur | Objectif contractuel |
|---|---:|---|
| `UNIQUE_CAPACITY_IDS_WITHOUT_ANY_QCM` | 48 | — |
| `CHAPTER_CAPACITY_PAIRS_WITHOUT_ANY_QCM` | 48 | — |
| `MANDATORY_ASSESSED_CAPACITY_PAIRS_WITHOUT_QCM` | 43 | — |
| `PEDAGOGICALLY_REQUIRED_QCM_GAPS` | 43 | **0** |
| `REQUIRED_DISTRACTOR_WITHOUT_DIAGNOSTIC` | 99 | **0** |

L'ecart **70 contre 48** est le meme indicateur mesure sur deux arbres : 70 sur
`761508d9` augmente du WIP, 48 sur l'arbre canonique. Meme definition, meme
generateur, deux sources.

La dette de diagnostic passe de 108 a 99 apres le portage des 11 renvois
valides du WIP.
