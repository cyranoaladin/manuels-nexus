# Motifs bruts et bloqueurs racines de la release

Dérivé intégralement du gate `release-strict`. Aucun compte n'est écrit en dur.

- Motifs bruts (`RAW_REASON_COUNT`) : `147`
- Bloqueurs racines (`ROOT_BLOCKER_COUNT`) : `13`
- Motifs non classés (`UNMAPPED_RAW_REASONS`) : `1`
- Identifiants dupliqués (`DUPLICATE_REASON_IDS`) : `0`
- Conflits de classification : `0`

| Taxonomie | Bloqueurs racines |
|---|---|
| `PRODUCT_P0` | 0 |
| `PRODUCT_P1` | 1 |
| `PRODUCT_P2` | 0 |
| `CERTIFICATION_BLOCKER` | 9 |
| `RELEASE_POLICY_BLOCKER` | 2 |
| `GOVERNANCE_BLOCKER` | 1 |

## Bloqueurs racines

| ID | Taxonomie | Titre | Motifs dépendants |
|---|---|---|---|
| `ROOT-BUILD-RECEIPT-NOT-INTEGRATED` | `CERTIFICATION_BLOCKER` | Reçus de build non intégrés | 1 |
| `ROOT-CONTENT-MATRIX-INCOMPLETE` | `CERTIFICATION_BLOCKER` | Matrice de contenu machine incomplète | 1 |
| `ROOT-COURSE-ASSEMBLY` | `PRODUCT_P1` | Assemblage de cours incomplet | 1 |
| `ROOT-CROSS-DISCIPLINE-AUDIT` | `CERTIFICATION_BLOCKER` | Contenu inter-disciplinaire non audité | 15 |
| `ROOT-DIMENSION-NOT-COVERED` | `CERTIFICATION_BLOCKER` | Dimensions de certification sans preuve | 2 |
| `ROOT-EXERCISE-CORRECTION-GRAPH-NOT-AUDITED` | `CERTIFICATION_BLOCKER` | Graphe exercice/corrigé non audité | 1 |
| `ROOT-FINAL-RELEASE-BUILD-EVIDENCE` | `CERTIFICATION_BLOCKER` | Preuve de build final absente (attend le gel) | 36 |
| `ROOT-HUMAN-REVIEW-QUEUE` | `CERTIFICATION_BLOCKER` | File de revue humaine ouverte | 53 |
| `ROOT-NON-APPROVED-STATUSES` | `GOVERNANCE_BLOCKER` | Objets et contrats non approuvés | 12 |
| `ROOT-OPTIONAL-DELIVERABLE-NOT-APPROVED` | `RELEASE_POLICY_BLOCKER` | Livrable facultatif seulement proposé | 4 |
| `ROOT-PRODUCER-STALE` | `CERTIFICATION_BLOCKER` | Producteurs de preuve stale ou rouges | 5 |
| `ROOT-PUBLICATION-SNAPSHOT-UNDECIDED` | `RELEASE_POLICY_BLOCKER` | Snapshots de publication non arbitrés | 1 |
| `ROOT-VERTICAL-MACHINE-STATUS` | `CERTIFICATION_BLOCKER` | Chaîne machine verticale incomplète | 15 |
