# Receipts de requalification — ADGK

Preuves de régression : `tests/test_adgk_method_regression.py` — vertes.

## `1NSI-ADGK-ME-001`

- `REVIEWER_IDENTITY` : `abenrhouma`
- `CURRENT_PEDAGOGICAL_CONTENT_DIGEST` : `sha256:e5971fa5293c0daed6cdf02344476e528b1d01fb29d4b61d82d949c0ca50ef44`
- `PREVIOUS_QUALIFICATION_DIGEST` : `sha256:a1d9f7f86aa92ebe761c930ebfb54164ec5f868505e6460e5cbdc3ec3f0918ac`
- `SCIENTIFIC_EVIDENCE_DIGEST` : `28e85a14d3a4a13561e1a9533ad329f360966bb63f0056e286e59c77e7869df9`
- `REGRESSION_TEST_DIGEST` : `sha256:fd4e2cebe8752a5d67f78d4a48659af0cc59ad05cb7c398f5cfd73aab09fc3e9`
- Contrat : élément absent -> -1

Preuves couvertes :

  - tableau vide
  - élément absent
  - élément présent
  - doublons
  - bornes (première et dernière case)
  - 4 000 cas contre oracle
  - variant d-g strictement décroissant et positif ou nul

## `1NSI-ADGK-ME-002`

- `REVIEWER_IDENTITY` : `abenrhouma`
- `CURRENT_PEDAGOGICAL_CONTENT_DIGEST` : `sha256:961a76c92e38942a37d155b792de61f69dda4a5b34bcb684cb3ac591c62870b7`
- `PREVIOUS_QUALIFICATION_DIGEST` : `sha256:0bee3bc3e58acd659d21134642e388fc44f5a9069b6ea6592804df09e8d3902a`
- `SCIENTIFIC_EVIDENCE_DIGEST` : `f526d4c7518399e0f3af9c5ce0e0a1ea1ce0e9c3c6367ec64fb8026fc0b949d4`
- `REGRESSION_TEST_DIGEST` : `sha256:fd4e2cebe8752a5d67f78d4a48659af0cc59ad05cb7c398f5cfd73aab09fc3e9`
- Contrat : rendu exact dans le domaine revendiqué, ou refus explicite

Preuves couvertes :

  - exactitude dans le domaine revendiqué (système euro)
  - comparaison par programmation dynamique sur les cas testés
  - contre-exemple {1,3,4} réfutant l'optimalité GÉNÉRALE uniquement

**Limite de portée.** Le contre-exemple {1,3,4} ne doit jamais être transformé en preuve d'une assertion plus large : il réfute l'optimalité générale, il ne dit rien de l'exactitude ni du système euro.

## `1NSI-ADGK-ME-003`

- `REVIEWER_IDENTITY` : `abenrhouma`
- `CURRENT_PEDAGOGICAL_CONTENT_DIGEST` : `sha256:e537285f2d49f0d6359dda52ec0eaff2a6e91f7e38fdabfc21355defdf040ac0`
- `PREVIOUS_QUALIFICATION_DIGEST` : `sha256:6db1bec7ba0de560cb2c8867882c49ee5bce30f0f9fca577acfefa051f6005cd`
- `SCIENTIFIC_EVIDENCE_DIGEST` : `6d680e0fdcfd2fab5bf7cb539b8bfa2077129e938eada551c0af574e5e302189`
- `REGRESSION_TEST_DIGEST` : `sha256:fd4e2cebe8752a5d67f78d4a48659af0cc59ad05cb7c398f5cfd73aab09fc3e9`
- Contrat : classe majoritaire, égalité tranchée par le voisin le plus proche

Preuves couvertes :

  - règle de départage courante
  - 20 000 multisets
  - égalités
  - k = 1
  - k = n
  - k > n
  - cohérence prose/code
