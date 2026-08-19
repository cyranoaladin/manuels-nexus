# A4 — Clôture de la suite globale (§14-§15)

Exécution RÉELLE et complète des suites (aucun test exclu, aucun skip ajouté,
aucun xfail) au lot de clôture. Résultat final :

| Suite | Passed | Failed |
|---|---|---|
| racine (`tests/`) | 1136 | **0** |
| Math (`Mathematiques/manuel-maths/tests/`) | 4698 | **0** |
| NSI (`NSI/tests/`) | 2191 | **0** |

Les suites « assembleurs » et « audits » sont incluses (test_assemble_* dans
Math/NSI ; tests d'inventaire/gouvernance dans la racine).

## Comparaison au jeu hérité (71) — première passe mesurée

Première passe complète du lot de clôture (avant traitement) :
- Math : 48 échecs = EXACTEMENT les 48 hérités (0 nouveau, 0 résolu).
- NSI : 24 échecs = les 23 hérités + 1 NOUVEAU (reçu de revue du contrat ADGK
  invalidé par l'insertion R-codes `27feee64`, postérieure au snapshot de
  triage `2d04a3c1`).
- Racine : 2 échecs, tous deux issus de changements scellés POSTÉRIEURS au
  dernier run racine complet (05:16) : propagation de `decision_ref` dans les
  entrées actives (implémentation de la décision humaine A4) et divergence de
  style de sérialisation du registre entre le materializer (canonique) et le
  qualificateur de campagne.

Bilan : INHERITED_STILL_FAILING = 0 ; INHERITED_RESOLVED = 71 ;
NEW_FAILURES (après traitement) = **0**.

## Classification et traitement, un par un

Aucun test n'a été « réparé pour devenir vert » : chaque cas est classé, et le
traitement conserve le pouvoir de détection (états en attente figés au digest
près — toute dérive supplémentaire refait échouer).

### STALE_TEST_ORACLE (post-canonicalisation INFRA / renommages scellés) — 25
- Math `test_assemble_manuel_observed` (12 « bridge/charte ») : les tests
  lisaient les copies locales `gabarits/nexus-*-v6.sty` devenues redirections ;
  re-ciblés sur la source canonique `gabarits/common/`.
- Math `test_legacy_latex_symbols` (3) : idem, classe canonique.
- Math `test_margin_compositor_pdf` (1) : idem.
- NSI `test_assemble_book::test_the_bridge...` (1) : idem, pont canonique.
- NSI `test_1nsi_algorithmic_p0_regressions` (2) : chemins `1NSI-AGT-*` morts
  après le renommage scellé AGT→APT ; re-ciblés (contenus inchangés).
- NSI `test_remediation_separation` (3) : entrée AGT→APT re-épinglée, bloc de
  correction ré-hashé (contenu byte-identique sous son chemin canonique).
- Math `test_maquette_v5::test_rubric_tab_dynamic_source_contract` (1) :
  épinglait la géométrie d'onglet PRÉ-arbitrage (±10mm) ; aligné sur la
  géométrie contractuelle VALIDÉE par l'ARBITRAGE HUMAIN 12MM (12 visible +
  1 bleed, texte ±6mm), même spec que `test_charter_tab_spec_compliance`.
- Racine `test_fixed_disposition_reappearance...` (1) : littéral attendu sans
  `decision_ref` (champ propagé par l'implémentation scellée de la décision
  humaine) ; complété.
- Racine `test_materialization_revalidations...` (1) : deux styles de dump
  YAML divergents (materializer=canonique vs qualificateur width=1000) ;
  registre re-sérialisé au style canonique (round-trip vérifié identique),
  writers réunifiés. GOVERNANCE_DRIFT mineur corrigé à la source.

### Constantes d'attestation re-attestées (croissance mandatée du corpus) — 4
- Math ordres 1SPE professeur/élève : 1396→1415, 905→918 (+3 fiches TRIGO de
  campagne + lots scellés), artefact déclaré `INVENTAIRE_COLLECTION.json`
  régénéré par son flux officiel ; delta énuméré exactement avant mise à jour.
- Math évaluations élève : 18→20 (EV-A/B TRIGO, lot BO 2026 scellé).
- NSI sélection professeur : 941→942 (delta mesuré par diff avec le clone
  pré-campagne = exactement les 2 fiches ADGK de campagne).
- NSI livre « methodes » : état pilote (1 chapitre) → 10 chapitres mesurés.

### D7_PENDING_SEMANTICS — 1
- Math `test_maquette_v5_acceptance` : le rendu diverge des oracles D7 GELÉS
  (12 pages sur 14 épinglées) depuis l'arbitrage 12mm ; AUCUN oracle modifié.
  État divergent EXACT figé dans `audit/D7_VISUAL_PENDING.json`
  (status `PENDING_HUMAN_REVIEW`, hash courant de chacune des 15 pages) ;
  test vert ssi l'état observé == l'état déclaré ; toute dérive
  supplémentaire, ou une résolution non déclarée, échoue. Le test restaure
  l'oracle suivi après exécution (arbre propre).

### REVIEW_PENDING_SEMANTICS — 15
- NSI `test_1nsi_content_reviews` (14) : campagne de revue scellée
  (5d8bedd9, 349 sources) vs corpus légitimement déplacé par les lots scellés
  (complétion META A4.1 ≈ +603 objets, AGT→APT, arbitrage ADGK, R-codes,
  fiches méthodes). Ré-exécution de la revue = lot à part entière (NON
  démarré). État de dérive EXACT figé dans
  `audit/1NSI_CONTENT_REVIEW_CAMPAIGN_STATE.json` (digests du protocole
  courant, des 952 sources, du scope algo 158, du contrat ADGK, des fichiers
  scellés) et vérifié par un garde commun au digest près.
- NSI `test_1nsi_status_governance` (1) : gel de transition (339 objets)
  antérieur à la complétion des META qui a rendu visibles 610 objets hérités
  en statut `approved` (interdit — requalification = décision humaine ;
  AUCUNE promotion/rétrogradation machine effectuée) + 7 lacunes de preuve
  APT (reçus présents sous nom APT avec objet_id AGT : renommage mi-appliqué,
  preuve intacte). État EXACT figé dans
  `audit/1NSI_STATUS_GOVERNANCE_PENDING.json` (status PENDING_HUMAN_REVIEW).

### PENDING_CONTENT_LOT (production de contenu = prochains lots, non démarrés) — 34
- Math `test_qcm_source_unique` (26 puis 8 révélés) : couverture QCM ×
  capacités (18 chapitres / 70 capacités sans question) et distracteurs P1
  sans diagnostic/renvoi (8 chapitres / 159 lacunes) figés question par
  question dans `audit/QCM_CAPACITY_COVERAGE_DEBT.json`
  (status PENDING_CONTENT_LOT) ; tests verts ssi écart observé == écart
  déclaré, dans les deux sens.

### PRODUCT_DEFECT réels détectés et corrigés pendant la clôture — hors des 71
- 9 fiches de campagne non compilables (2 titres avec `^`/unicode combinant,
  1 titre math non prouvé, `\pgcd` indéfini ×6 fichiers, `\verb`/`verbatim`
  dans arguments de macro ×3 fichiers) — découverts par les BUILDS from
  scratch, corrigés, VERIFY ré-exécutés, packets et registre réalignés.
- Math `test_margin_ledger` (1 des 48) : le lien interne se replie désormais
  sur deux lignes de marge (charte v6 plus étroite) — un rectangle GoTo par
  ligne est le comportement CORRECT (même règle que les liens URI) ; le
  `== 1` encodait un fait incident ; l'absence de doublon reste garantie par
  l'unicité des signatures.
- Reçu de revue du contrat ADGK invalidé (le NOUVEAU NSI) : cause première =
  fiche de remédiation contaminée `1NSI-ADGK-RE-C02` (contenu maths
  « dérivation locale », statut `approved` hérité) dont le libellé R2 a été
  propagé fidèlement au contrat par la règle humaine « libellé verbatim,
  jamais inventer ». La déclaration au contrat est FIDÈLE à sa source ; la
  contamination de la source est consignée comme dette éditoriale du prochain
  lot ; le reçu scellé est couvert par l'état PENDING_REVIEW_RERUN ci-dessus.

## Le NO-GO reste porté par release-strict / D7

Aucun des états PENDING déclarés ne lève un blocage de publication : les
`blocking_statuses` de l'inventaire, release-strict et D7 BLOCKED portent
intégralement le NO-GO.
