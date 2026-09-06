# Motifs bruts et bloqueurs racines de la release

Dérivé intégralement du gate `release-strict`. Aucun compte n'est écrit en dur.

- Motifs bruts (`RAW_REASON_COUNT`) : `471`
- Bloqueurs racines (`ROOT_BLOCKER_COUNT`) : `20`
- Motifs non classés (`UNMAPPED_RAW_REASONS`) : `0`
- Identifiants dupliqués (`DUPLICATE_REASON_IDS`) : `0`
- Conflits de classification : `0`

| Taxonomie | Bloqueurs racines |
|---|---|
| `PRODUCT_P0` | 0 |
| `PRODUCT_P1` | 8 |
| `PRODUCT_P2` | 1 |
| `CERTIFICATION_BLOCKER` | 9 |
| `RELEASE_POLICY_BLOCKER` | 1 |
| `GOVERNANCE_BLOCKER` | 1 |

## Bloqueurs racines

| ID | Taxonomie | Titre | Motifs dépendants |
|---|---|---|---|
| `ROOT-ASSESSMENT-COVERAGE` | `PRODUCT_P1` | Couverture d'évaluations incomplète | 41 |
| `ROOT-BUILD-RECEIPT-NOT-INTEGRATED` | `CERTIFICATION_BLOCKER` | Reçus de build non intégrés | 1 |
| `ROOT-CONTENT-MATRIX-INCOMPLETE` | `CERTIFICATION_BLOCKER` | Matrice de contenu machine incomplète | 1 |
| `ROOT-COURSE-ASSEMBLY` | `PRODUCT_P1` | Assemblage de cours incomplet | 4 |
| `ROOT-CROSS-DISCIPLINE-AUDIT` | `CERTIFICATION_BLOCKER` | Contenu inter-disciplinaire non audité | 15 |
| `ROOT-DELIVERABLE-NOT-BUILT` | `PRODUCT_P1` | Variantes déclarées jamais construites | 20 |
| `ROOT-DELIVERABLE-NOT-COMPILED` | `PRODUCT_P1` | Livrables déclarés non compilés | 16 |
| `ROOT-DELIVERABLE-NOT-DECLARED` | `PRODUCT_P1` | Assemblages de variantes non déclarés | 8 |
| `ROOT-EXERCISE-CORRECTION-GRAPH` | `PRODUCT_P1` | Graphe exercice/corrigé incomplet | 32 |
| `ROOT-EXERCISE-CORRECTION-GRAPH-NOT-AUDITED` | `CERTIFICATION_BLOCKER` | Graphe exercice/corrigé non audité | 1 |
| `ROOT-HUMAN-REVIEW-QUEUE` | `CERTIFICATION_BLOCKER` | File de revue humaine ouverte | 53 |
| `ROOT-NON-APPROVED-STATUSES` | `GOVERNANCE_BLOCKER` | Objets et contrats non approuvés | 12 |
| `ROOT-ORACLE-EVIDENCE` | `CERTIFICATION_BLOCKER` | Preuve oracle QCM absente | 42 |
| `ROOT-PEDAGOGICAL-RICHNESS` | `PRODUCT_P2` | Richesse pédagogique insuffisante | 34 |
| `ROOT-PEDAGOGICAL-ROLE-COVERAGE` | `PRODUCT_P1` | Rôles pédagogiques non couverts | 42 |
| `ROOT-PRODUCER-STALE` | `CERTIFICATION_BLOCKER` | Producteurs de preuve stale ou rouges | 4 |
| `ROOT-PUBLICATION-SNAPSHOT-UNDECIDED` | `RELEASE_POLICY_BLOCKER` | Snapshots de publication non arbitrés | 1 |
| `ROOT-QCM-COVERAGE` | `PRODUCT_P1` | Couverture QCM incomplète | 13 |
| `ROOT-QUALIFICATION-STALE` | `CERTIFICATION_BLOCKER` | Qualifications dérivées invalidées par une mutation de source | 89 |
| `ROOT-VERTICAL-MACHINE-STATUS` | `CERTIFICATION_BLOCKER` | Chaîne machine verticale incomplète | 42 |
