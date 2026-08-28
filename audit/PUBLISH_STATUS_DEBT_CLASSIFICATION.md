# Classification de la dette de statut publication

Classification conservative des 2 222 blocages du snapshot d'inventaire. Aucun statut source n'est promu et aucune approbation scientifique, pédagogique ou humaine n'est inférée.

## Provenance

- Inventaire source : `audit/INVENTAIRE_COLLECTION.json` (`709d99abf713ad86f24356018674ec66fabd5036`)
- Provenance de l'inventaire : `STALE_BUILD_MANIFEST`; seule sa tranche des statuts bloquants est reclassée ici.
- Les valeurs `current_status` demandées ne sont **pas** certifiées au HEAD courant tant que la tranche n'est pas recalculée depuis les sources.
- La campagne 1NSI scellée est utilisée uniquement pour identifier les reçus devenus périmés.

## Résultat

- Classés : **2222 / 2222**
- UNKNOWN : **0**
- Promotion de statut : **aucune**

### Par cluster

- `PROGRAM_REVIEW_PENDING` : 122
- `SCIENTIFIC_REVIEW_PENDING` : 0
- `PEDAGOGICAL_REVIEW_PENDING` : 0
- `EDITORIAL_REVIEW_PENDING` : 0
- `GENERATED_NOT_REVIEWED` : 1756
- `DRAFT_NOT_REVIEWED` : 7
- `STALE_RECEIPT` : 337
- `HUMAN_APPROVAL_PENDING` : 0
- `NON_PUBLISHABLE_BUT_IN_RELEASE_GRAPH` : 0
- `OTHER_EXPLICIT` : 0

### Par manuel

- `1NSI` : 342 — PROGRAM_REVIEW_PENDING=5, STALE_RECEIPT=337
- `1SPE` : 1414 — PROGRAM_REVIEW_PENDING=14, GENERATED_NOT_REVIEWED=1393, DRAFT_NOT_REVIEWED=7
- `TCOMPL` : 209 — PROGRAM_REVIEW_PENDING=59, GENERATED_NOT_REVIEWED=150
- `TEXPERTES` : 131 — PROGRAM_REVIEW_PENDING=38, GENERATED_NOT_REVIEWED=93
- `TNSI` : 115 — PROGRAM_REVIEW_PENDING=6, GENERATED_NOT_REVIEWED=109
- `TSPE` : 11 — GENERATED_NOT_REVIEWED=11

## Interprétation

`STALE_RECEIPT` regroupe 330 objets recoupés avec la campagne de revue 1NSI scellée et 7 objets dont l'identité AGT→APT a rompu la liaison de preuve. `PROGRAM_REVIEW_PENDING` est un classement conservateur de fermeture : il ne vaut pas validation du programme.

Le détail ligne par ligne, incluant les neuf champs réglementaires demandés, est dans `audit/PUBLISH_STATUS_DEBT_CLASSIFICATION.json`.
