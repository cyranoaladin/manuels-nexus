# DÉCISION HUMAINE — A4 METHOD REVIEW DEBT (EXPECTED_REVIEW_DEBT)

Décision rendue le 2026-08-19 par le responsable de projet (Alaeddine Ben
Rhouma), applicable UNIQUEMENT dans le cadre de la campagne A4.

## Portée

Sont qualifiables comme EXPECTED_REVIEW_DEBT les fingerprints
`blocking_statuses` créés EXCLUSIVEMENT par de nouvelles fiches méthodes
répondant SIMULTANÉMENT aux conditions :

1. la fiche correspond à une capacité canonique existante ;
2. elle est requise par le contrat éditorial C_i ↔ M_i ;
3. son statut reste `needs_review` ;
4. son source SHA est enregistré ;
5. un packet de revue scientifique/pédagogique est créé
   (`audit/reviews/methods/...`) ;
6. aucune autre catégorie d'anomalie nouvelle n'est introduite.

## Limites expresses

Cette qualification :

- NE vaut PAS approbation du contenu ;
- NE vaut PAS revue scientifique ;
- NE vaut PAS validation pédagogique ;
- NE vaut PAS autorisation de publication ;
- NE permet PAS une promotion automatique vers `approved`/`release_ready`.

Les fingerprints ainsi qualifiés RESTENT des blockers de release
(`release_blocking = true`) jusqu'à revue. Toute nouvelle anomalie ne
satisfaisant pas exactement cette politique doit continuer à faire échouer
le gate. Aucune baseline n'est modifiée.

## Application mécanique

Chaque qualification est enregistrée dans `audit/ANOMALY_DISPOSITIONS.yaml`
avec `decision_ref =
audit/A4_METHOD_REVIEW_DEBT_POLICY.md#decision-a4-method-review-debt-2026-08-19`,
`disposition = open_debt`, `release_blocking = true`, owner et policy_rule
routés par la règle `blocking-scientific-object` (objets `methode`), et les
digests calculés par `scripts/baseline_qualification.qualification_digest`.
Le qualificateur vérifie programmatiquement les 6 conditions AVANT toute
écriture et refuse tout fingerprint hors périmètre.
