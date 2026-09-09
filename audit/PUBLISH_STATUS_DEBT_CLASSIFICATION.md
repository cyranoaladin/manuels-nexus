# Classification de la dette de statut publication

Classification conservative des 2 222 blocages du snapshot d'inventaire. Aucun statut source n'est promu et aucune approbation scientifique, pédagogique ou humaine n'est inférée.

## Provenance

- Inventaire source : `audit/INVENTAIRE_COLLECTION.json` (`aa2fc74d006abb0843fc7af44d495d0cc79b0b9c`)
- Provenance de l'inventaire : `STALE_BUILD_MANIFEST`; seule sa tranche des statuts bloquants est reclassée ici.
- Les valeurs `current_status` demandées ne sont **pas** certifiées au HEAD courant tant que la tranche n'est pas recalculée depuis les sources.
- La campagne 1NSI scellée est utilisée uniquement pour identifier les reçus devenus périmés.

## Résultat

- Classés : **2714 / 2222**
- UNKNOWN : **0**
- Promotion de statut : **aucune**

### Par cluster

- `PROGRAM_REVIEW_PENDING` : 203
- `SCIENTIFIC_REVIEW_PENDING` : 0
- `PEDAGOGICAL_REVIEW_PENDING` : 0
- `EDITORIAL_REVIEW_PENDING` : 0
- `GENERATED_NOT_REVIEWED` : 2173
- `DRAFT_NOT_REVIEWED` : 8
- `STALE_RECEIPT` : 330
- `HUMAN_APPROVAL_PENDING` : 0
- `NON_PUBLISHABLE_BUT_IN_RELEASE_GRAPH` : 0
- `OTHER_EXPLICIT` : 0

### Par manuel

- `1NSI` : 423 — PROGRAM_REVIEW_PENDING=46, GENERATED_NOT_REVIEWED=47, STALE_RECEIPT=330
- `1SPE` : 1440 — PROGRAM_REVIEW_PENDING=20, GENERATED_NOT_REVIEWED=1413, DRAFT_NOT_REVIEWED=7
- `TCOMPL` : 327 — PROGRAM_REVIEW_PENDING=76, GENERATED_NOT_REVIEWED=251
- `TEXPERTES` : 248 — PROGRAM_REVIEW_PENDING=38, GENERATED_NOT_REVIEWED=210
- `TNSI` : 199 — PROGRAM_REVIEW_PENDING=20, GENERATED_NOT_REVIEWED=178, DRAFT_NOT_REVIEWED=1
- `TSPE` : 77 — PROGRAM_REVIEW_PENDING=3, GENERATED_NOT_REVIEWED=74

## Interprétation

`STALE_RECEIPT` regroupe 330 objets recoupés avec la campagne de revue 1NSI scellée et 7 objets dont l'identité AGT→APT a rompu la liaison de preuve. `PROGRAM_REVIEW_PENDING` est un classement conservateur de fermeture : il ne vaut pas validation du programme.

Le détail ligne par ligne, incluant les neuf champs réglementaires demandés, est dans `audit/PUBLISH_STATUS_DEBT_CLASSIFICATION.json`.
