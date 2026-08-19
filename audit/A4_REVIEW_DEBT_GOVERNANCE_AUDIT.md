# A4 — Audit de gouvernance EXPECTED_REVIEW_DEBT (lot de clôture)

Objet : clarifier ce qui a muté pendant la campagne méthodes, prouver que la
baseline de référence n'a subi AUCUNE mutation, fixer la signification exacte
de `baseline_sha`, et sceller le mécanisme « politique humaine immutable →
qualifications dérivées par prédicat machine ».

Fenêtre mesurée : `2852cb67` (scellement du jeu de cibles) → HEAD de clôture.

## 1. Les quatre objets (§3)

### A. REFERENCE_BASELINE — immutable

| Champ | Valeur |
|---|---|
| path | `audit/ANOMALIES_BASELINE.json` |
| sha256 avant campagne (à `2852cb67`) | `3e9225668121a67c2fdea1248ec420ff16bd3910c8557e3a98df8bb7997250e1` |
| sha256 courant | `3e9225668121a67c2fdea1248ec420ff16bd3910c8557e3a98df8bb7997250e1` |
| **identiques** | **OUI — aucune mutation** (0 commit touchant ce fichier depuis `2852cb67`) |
| mutable | NON (toute update de baseline est interdite par les contraintes permanentes du lot) |
| human_authority | OUI — seule une décision humaine peut la remplacer |
| purpose | jeu figé d'anomalies actives approuvé (ancre `git_sha` interne : `7752988ae7041a7a5de700fcf4609bd47a4fba3a`) contre lequel fail-on-new compare chaque rendu frais |

**RÈGLE ABSOLUE vérifiée : `REFERENCE_BASELINE_SHA_BEFORE == REFERENCE_BASELINE_SHA_AFTER` → PASS.**

### B. HUMAN_POLICY — immutable

| Champ | Valeur |
|---|---|
| path | `audit/A4_METHOD_REVIEW_DEBT_POLICY.md` |
| policy_id | `decision-a4-method-review-debt-2026-08-19` |
| sha256 au scellement (`e910152d`) | `07597ede77c7fce1a167a87227178f05a10faabbad4ca1e04d7bb2048fda12a7` |
| sha256 courant | `07597ede77c7fce1a167a87227178f05a10faabbad4ca1e04d7bb2048fda12a7` |
| identiques | OUI — politique intacte |
| mutable | NON — toute modification invalide immédiatement TOUTES les qualifications dérivées (gate durci, voir §3 ci-dessous) |
| human_authority | OUI (décision humaine du 2026-08-19, 6 conditions strictes) |
| purpose | autorise UNE classe de transitions : fiche méthode canonique + needs_review + packet valide + capacité canonique ⇒ EXPECTED_REVIEW_DEBT (toujours bloquant release) |

### C. DERIVED_EXPECTED_REVIEW_DEBT_REGISTRY — mutable (machine)

| Champ | Valeur |
|---|---|
| path | `audit/ANOMALY_DISPOSITIONS.yaml` |
| sha256 avant campagne | `e481b0b0684af68ece1cb6c40b40d073c2569663fe8e50b35dda9d3c49735aa8` |
| sha256 courant | `cb270fbbb93f62843c4a8b77585a04dc0a086bbe9c14f501a9134f6b5e8e6d84` |
| mutable | OUI — registre DÉRIVÉ : la machine y matérialise les qualifications après vérification du prédicat de la politique de classe |
| human_authority | NON pour les enregistrements A4 (dérivés) ; les autres enregistrements historiques conservent leurs décisions humaines propres |
| purpose | 8289 dispositions au total, dont **85 qualifications A4 dérivées** (les 85 fiches méthodes de campagne) |

### D. CURRENT_ANOMALIES — recalculé, jamais persisté comme vérité

| Champ | Valeur |
|---|---|
| path | aucun (règle permanente : les métriques ne proviennent QUE de rendus frais de `inventory_collection.py`, jamais de JSON committés) |
| mutable | n/a — recalculé à chaque rendu |
| purpose | état observé, comparé à A par fail-on-new |

## 2. Clarification de la formulation fautive du rapport de campagne

Le rapport de checkpoint disait « baseline_sha recalculé » à chaque lot.
**C'est une formulation erronée** : mesure faite, les 85 enregistrements A4
portent tous `baseline_sha = 7752988ae7041a7a5de700fcf4609bd47a4fba3a`, la
valeur **constante copiée** du champ `git_sha` de la REFERENCE_BASELINE
(inchangée). Ce qui était recalculé à chaque lot : `qualification_digest`
(par enregistrement) et `control_digest` (enveloppe du registre C) — jamais
la baseline A.

## 3. Signification exacte de `baseline_sha` (§4)

`baseline_sha` = **ancre vers la REFERENCE_BASELINE immutable** : la valeur
du champ `git_sha` du fichier `audit/ANOMALIES_BASELINE.json` contre lequel
la qualification a été calculée.

- Il ne signifie PAS « nouvelle baseline d'anomalies approuvée ».
- Il n'est ni `campaign_start_sha`, ni `policy_source_sha`, ni
  `observed_tree_sha`.
- Renommage : NON NÉCESSAIRE — le terme désigne un seul objet (la référence
  A) avec une seule sémantique, uniforme sur tous les enregistrements du
  registre (le schéma `anomaly-dispositions.schema.json` l'exige pour toute
  disposition pilotée par politique, toujours avec ce sens d'ancre). Aucun
  autre objet du dépôt n'utilise `baseline_sha` avec un autre sens.

## 4. Mécanisme scellé : politique immutable → dérivation machine (§5)

Constat d'audit initial : les 85 enregistrements portaient
`approved_by: <nom humain>` alors que l'humain a approuvé UNE CLASSE, pas
chaque méthode individuellement. **Corrigé** (commit de clôture) :

- `approved_by` = `policy:decision-a4-method-review-debt-2026-08-19 (décision
  humaine de classe du 2026-08-19 — aucune approbation humaine individuelle
  de la méthode n'est revendiquée)`.
- Chaque enregistrement dérivé porte désormais le quintuplé exigé :
  `policy_id`, `qualification_policy_digest` (= sha256 du fichier de
  politique), `method_source_sha`, `capacity_id` (+ `capacity_ref` du
  contrat), `review_packet` + `review_packet_sha`, `qualification_reason`.
- Schéma `anomaly-dispositions.schema.json` étendu : ces champs deviennent
  OBLIGATOIRES pour tout enregistrement portant le `decision_ref` A4.
- **Approbations humaines fabriquées/implicites restantes : 0** (vérifié par
  test `test_repository_a4_derived_qualifications_reference_class_policy`).

Gate durci (`_a4_method_review_debt_violations`, appelé à CHAQUE rendu
d'inventaire dans `_load_dispositions`) :

| Événement | Comportement vérifié par test |
|---|---|
| Politique modifiée | toutes les qualifications dérivées invalides (`test_a4_review_debt_policy_edit_invalidates_derived_qualifications`) |
| Source de fiche modifiée | qualification STALE (`test_a4_review_debt_method_edit_makes_qualification_stale`) |
| Packet de revue manquant | qualification invalide (`test_a4_review_debt_missing_packet_invalidates_qualification`) |
| Statut promu `approved` sans revue humaine | FAIL (`test_a4_review_debt_status_promotion_without_review_fails`) |

## 5. Dérive de gouvernance annexe détectée et corrigée

`baseline_qualification._canonical_locator` (introduit le 2026-08-16, commit
`94916925`) repliait les alias `ADGK`→`APT` et `AGT`→`APT` dans les locators.
Cette normalisation est **antérieure et contraire** à l'arbitrage humain du
2026-08-19 (`A4_ADGK_CANONICAL_STATUS.md` : ADGK et APT sont deux chapitres
canoniques DISTINCTS, DO_NOT_MERGE) ; elle pouvait rapprocher un locator ADGK
d'une disposition APT dans le chemin de correspondance de secours.
Classée `GOVERNANCE_DRIFT`, supprimée au commit de clôture (la fonction est
désormais une canonicalisation identitaire, sans réécriture).
