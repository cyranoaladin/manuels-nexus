# Contrat de revue humaine des chapitres gelés

**Décision** `nexus-human-review-contract-2026-08-26` — gouvernance uniquement.
Cette décision **n'approuve aucun chapitre**. Aucun reviewer n'est assigné,
aucun verdict n'est rendu, aucun statut n'a été modifié.

- Contrat machine : `audit/HUMAN_REVIEW_GOVERNANCE.yaml`
- Schéma du reçu : `audit/schemas/v1/human-review-receipt.schema.json`
- Moteur : `scripts/human_review_governance.py`
- Tests de mutation : `tests/test_human_review_governance.py`

## 1. Deux revues humaines distinctes

| Discipline | Review A | Review B |
|---|---|---|
| Mathématiques (`1SPE`, `TSPE`, `TCOMPL`, `TEXPERTES`) | `EXPERT_MATHEMATIQUE` | `EXPERT_PROGRAMME_PEDAGOGIE` |
| NSI (`1NSI`, `TNSI`) | `EXPERT_NSI` | `EXPERT_PROGRAMME_PEDAGOGIE` |

`audit/schemas/v1/1nsi-content-review.schema.json` ne portait que `reviewer_id`
et `reviewer_model`, pour des revues **machine** sur les dimensions `scientific`
et `pedagogical` de `audit/1NSI_CONTENT_REVIEW_POLICY.yaml` : aucun nom de rôle
humain n'y existait. `EXPERT_NSI` est donc adopté comme nom disciplinaire
canonique et projeté sur la dimension `scientific` existante. Aucun nom de rôle
préexistant n'a été remplacé.

Une machine (Codex, Claude, Copilot, tout autre système automatisé) ne peut
jamais porter un rôle. Elle peut seulement préparer le packet, produire les
contrôles machine et enregistrer fidèlement un verdict humain réellement reçu.

## 2. Granularité : chapitre gelé

La revue couvre un ensemble exact et immuable d'objets, identifié par
`OBJECT_SET_DIGEST` et `object_count`. Aucun objet extérieur n'en bénéficie ;
aucune promotion implicite par proximité de fichier ou de capacité n'est
possible. Un `blocking_finding` visant un objet hors ensemble est refusé.

## 3. Trois verdicts canoniques

`APPROVED`, `CHANGES_REQUESTED`, `REJECTED`. Tout autre verdict échoue, y
compris `AUTO_APPROVED`, `APPROVED_BY_MACHINE`, `ASSUMED_APPROVED`,
`APPROVED_WITHOUT_REVIEW`. Un commentaire accompagnant `APPROVED` doit être
classé `NON_BLOCKING_OBSERVATION` ; une observation scientifique ou pédagogique
réellement non résolue ne peut pas être reclassée en commentaire cosmétique.

## 4-5. Deux bindings disjoints

| Digest | Algorithme | Ce qu'il lie |
|---|---|---|
| `OBJECT_SET_DIGEST` | `NEXUS_OBJECT_SET_DIGEST_V1` | identité des objets : `object_id`, `object_type`, section, chemin |
| `SEMANTIC_REVIEW_DIGEST` | `NEXUS_SEMANTIC_REVIEW_DIGEST_V1` | objets + sources normalisées, contrat, capacités, mapping programme, QCM, remédiations, évaluations, corrections, ordre d'assemblage élève et professeur, règles de variante, autorité programme |
| `REVIEW_RENDER_DIGEST` | `NEXUS_REVIEW_RENDER_DIGEST_V1` | uniquement les rendus examinés (PDF, rasters) |
| `PROGRAMME_AUTHORITY_DIGEST` | `NEXUS_PROGRAMME_AUTHORITY_DIGEST_V1` | `PROGRAMME_D_ENSEIGNEMENT` du manuel |
| `PACKET_DIGEST` | `NEXUS_REVIEW_PACKET_DIGEST_V1` | le packet exact soumis au reviewer |

Sont exclus du digest sémantique : timestamp, cwd, run id, chemin absolu, PDF
binaire, métadonnées de build non sémantiques, rapports auto-référents.
`REPOSITORY_SOURCE_SHA` est conservé dans le reçu pour traçabilité mais n'entre
pas dans le digest sémantique.

Sont également exclus `META.status` et `contrat.statut` : ce sont exactement les
champs que la revue fait évoluer. Les inclure rendrait tout reçu `STALE` au
moment même de la promotion qu'il autorise. Un test verrouille cette exclusion.

## 6. Staleness

Un reçu de contenu devient `HISTORICAL_STALE` dès que change une source
couverte, le contrat, une capacité, un QCM, une correction, une remédiation, une
évaluation, le mapping programme pertinent, l'autorité programme, l'ordre
sémantique d'assemblage ou une règle de variante affectant le contenu visible.

Un changement purement `.cls` / `.sty` / charte / pagination / couleur / police /
composition visuelle ne périme **pas** la review de contenu tant que
`SEMANTIC_REVIEW_DIGEST` reste strictement identique — ce digest couvre déjà le
contenu extrait, l'ordre des objets et la visibilité élève/professeur, donc son
invariance démontre les trois conditions. En revanche, tout changement graphique
qui modifie `REVIEW_RENDER_DIGEST` périme les preuves VISUAL/D7 correspondantes.

**CONTENT REVIEW et VISUAL REVIEW restent deux autorités indépendantes.**

## 9. Gate QCM

Pas de troisième reviewer humain : les 21 questions du chapitre figurent
explicitement dans les deux packets (`qcm_question_ids`). `QCM_HUMAN_APPROVAL`
est `SATISFIED` uniquement si `REVIEW_A = APPROVED` **et** `REVIEW_B = APPROVED`,
tous deux courants et rendus par deux identités distinctes. Sinon `PENDING`.

## 14. Table de transition de statuts

Énumération canonique reprise de
`Mathematiques/manuel-maths/schemas/exercice.schema.json` :
`draft`, `generated`, `verified`, `manual_review`, `needs_review`, `ready`,
`approved`, `rejected`.

| Statut courant | Dimensions machine requises | Reçus humains requis | Statut canonique suivant |
|---|---|---|---|
| `generated` | mapping, content_sufficiency, science, pedagogy, editorial, assessment, year | — | `verified` |
| `manual_review` | science | — | `needs_review` |
| `verified` | les 7 précédentes + semantic_evidence_current | — | `needs_review` (packets émis) |
| `needs_review` | les 7 précédentes + semantic_evidence_current | `review_a_approved_current` **et** `review_b_approved_current` | `approved` |
| `approved` | render_evidence_current | `d7_visual_approved` | `ready` (print/publish ready) |
| n'importe lequel | — | `any_receipt_rejected` | `rejected` |

| Contrat de chapitre | Reçus humains requis | Statut suivant |
|---|---|---|
| `draft` | `review_a_approved_current` **et** `review_b_approved_current` | `valide` |

`approved`, `ready` et `rejected` sont interdits sans reçu humain. Aucune
promotion d'un objet extérieur à l'ensemble gelé.

## 15. Conditions de FULL

`mapping`, `content_sufficiency`, `science_machine`, `pedagogy_machine`,
`editorial_machine`, `assessment`, `year`, `semantic_evidence_current`,
`human_expert_disciplinary_approved`, `human_programme_pedagogy_approved`,
`qcm_human_gate_satisfied`. Un seul critère `pending` interdit `FULL`.

## 16. D7 reste indépendant

`SCIENCE_COMPLETE`, `PEDAGOGY_COMPLETE` et `EDITORIAL_COMPLETE` n'impliquent ni
`VISUAL_COMPLETE`, ni `D7_APPROVED`, ni `PRINT_READY`, ni `PUBLISH_READY`. Le
registre D7 reste `audit/D7_VISUAL_PENDING.json`.

## 17. Tests de mutation

| Id | Mutation | Attendu | Test |
|---|---|---|---|
| A | même humain pour A et B | FAIL | `test_A_same_human_for_both_roles_fails` |
| B | agent IA comme reviewer | FAIL | `test_B_machine_reviewer_is_refused` |
| C | mauvais `object_set_digest` | FAIL | `test_C_wrong_object_set_digest_fails` |
| D | mauvais `semantic_review_digest` | FAIL | `test_D_wrong_semantic_review_digest_fails` |
| E | mauvais `packet_digest` | FAIL | `test_E_wrong_packet_digest_fails` |
| F | `APPROVED` avec `blocking_findings` | FAIL | `test_F_approved_with_blocking_findings_fails` |
| G | source sémantique modifiée après review | STALE | `test_G_semantic_source_change_makes_receipt_stale` |
| H | changement style-only, digest sémantique identique | contenu CURRENT, visuel STALE | `test_H_style_only_change_keeps_content_and_stales_visual` |
| I | QCM ajouté après review | STALE | `test_I_qcm_added_after_review_makes_receipt_stale` |
| J | objet externe à l'ensemble gelé | aucun bénéfice | `test_J_finding_outside_frozen_set_is_refused` |
| K | verdict inconnu | FAIL | `test_K_unknown_verdict_fails` |

## 18. État de 1SPE-SUITES

| Élément | État |
|---|---|
| Review A (`EXPERT_MATHEMATIQUE`) | `PENDING_UNASSIGNED` |
| Review B (`EXPERT_PROGRAMME_PEDAGOGIE`) | `PENDING_UNASSIGNED` |
| Gate QCM humain | `PENDING` |
| FULL | 0 / 15 |
| Statuts des objets | inchangés (`generated`) |
| Contrat | inchangé (`draft`) |

**Blocage ouvert** : l'ensemble gelé déclaré (161 objets,
`sha256:67d80062…`) n'est pas reproductible à partir du dépôt ; la machine
énumère 156 objets, `sha256:9d9ab4b6…`. Voir
`audit/HUMAN_REVIEW_FROZEN_SET_RECONCILIATION.json`. Aucun reviewer ne peut être
assigné tant que cet écart n'est pas tranché par un humain.
