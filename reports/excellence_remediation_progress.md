# Remédiation excellence éditoriale — suivi

## Contexte

- Branche initiale : `main`
- HEAD initial : `a6e7736a66a03f8e34e836d2a29f3fed3867cf1f`
- Rapport source : `reports/excellence_editorial_review_nsi.md`
- Lots traités : 1 — T10 SQL ; 2 — séparation des évaluations P08 ; 3 — pilote T17 programmation dynamique.
- Date de consolidation : 2026-07-12.
- Aucun commit, aucune modification de verdict JSON et aucune promotion de statut.

## Lots corrigés

| Lot | Constats couverts | Fichiers modifiés | Validation | Suite documentée |
|---|---|---|---|---|
| 1 — T10 SQL | RVW-001 ; contributions à RVW-008 à RVW-012, RVW-016 et RVW-017 | Cours, 2 TD, TP, 2 évaluations, corrigé, barème, trace, remédiation, version aménagée, contrat, fiche, 3 assets Python, gate et tests SQL | Cohérence SQL, profondeur des supports, TD, évaluations, contrat, liens et assets : PASS ; rendus régénérés | Re-juger indépendamment `T-BDD-03A` à `T-BDD-03H` |
| 2 — P08 évaluations | RVW-002 | 2 évaluations réécrites ; 2 corrigés et 2 barèmes distincts créés ; anciens corrigé/barème transversaux réorientés | Séparation, profondeur, appariement, liens, inventaire, registre humain et rendu : PASS | Lot volontairement partiel : cours, TD, TP, trace, remédiation et version aménagée restent à reprendre |
| 3 — T17 pilote transversal | RVW-007 ; pilote pour RVW-003, RVW-004, RVW-008 à RVW-012 et RVW-016 à RVW-018 | Cours, TD à 6 tâches, TP, évaluation, corrigé, barème, trace, remédiation, version aménagée, contrat, 3 assets Python | Récurrence, profondeur, substance TD/évaluation, contrat, liens et assets : PASS ; rendus régénérés | Re-juger indépendamment `T-ALGO-04`, puis généraliser le niveau aux autres séquences |

## Détail par constat

| RVW | Statut | Preuve de correction | Fichiers |
|---|---|---|---|
| RVW-001 | CORRIGÉ — sources | Base T10 stable ; opérations strictement séparées ; requêtes, résultats, pièges et critères alignés ; deux TD avec six tâches et corrigés intégrés ; gate SQL vert. | Lot T10, `scripts/check_sql_query_result_consistency.py` |
| RVW-002 | CORRIGÉ — lot évaluations | Sujet HTML/CSS/DOM fondé sur un vote interactif ; sujet HTTP fondé sur une médiathèque ; stimuli, capacités, corrigés et barèmes distincts. | `P08_evaluation_*`, `P08_corrige_{html_css_dom,http_get_post_formulaires}.md`, `P08_bareme_{html_css_dom,http_get_post_formulaires}.md` |
| RVW-003 | PARTIEL | T17 ne contient plus `alpha…theta` et propose lecture, trace, contre-exemple, code, débogage et transfert. Les autres banques P06–P14/T06–T19 restent à traiter. | `T17_TD_programmation_dynamique.md` |
| RVW-004 | PARTIEL | Corrections T10 et T17 avec requêtes, tables, états, invariants, raisonnements et erreurs typiques. | Corrigés et TD T10/T17 |
| RVW-005 | HORS PÉRIMÈTRE DU LOT | Aucun lot dédié aux cours P00–P05/T00–T05. | — |
| RVW-006 | HORS PÉRIMÈTRE DU LOT | Compléments hors des trois séquences non traités. | — |
| RVW-007 | CORRIGÉ — sources | Évaluation T17 sur données inédites `[1,4,6]`, table, reconstruction, écriture d'algorithme, impossible et complexité. | `T17_evaluation_programmation_dynamique.md` |
| RVW-008 | PARTIEL | Barèmes observables T10, P08 et T17 avec points partiels et plafonds structurants. | Barèmes des trois lots |
| RVW-009 | PARTIEL | Corrigés détaillés T10, P08 et T17 ; le reste du corpus demeure à reprendre. | Corrigés des trois lots |
| RVW-010 | PARTIEL | T10 et T17 proposent trois diagnostics et une tâche isomorphe sans aide. | Remédiations T10/T17 |
| RVW-011 | PARTIEL | Versions aménagées T10 et T17 segmentées, sans requête, table ou résultat final fourni. | Versions aménagées T10/T17 |
| RVW-012 | PARTIEL | Traces T10 et T17 devenues fiches de révision avec méthode, exemple, pièges, cas limites et auto-vérification. | Traces T10/T17 |
| RVW-013 | HORS PÉRIMÈTRE DU LOT | Évaluation T19 non traitée. | — |
| RVW-014 | PARTIEL | Différenciation réelle ajoutée à T10 et T17 seulement. | Cours/TD T10/T17 |
| RVW-015 | PARTIEL | Situations-problèmes et activités d'entrée réelles ajoutées à T10 et T17 seulement. | Cours T10/T17 |
| RVW-016 | PARTIEL | TP T10 et T17 dotés de durée, signatures, livrables, commandes, cas nominaux/limites/invalides, exemples corrigés et prolongement. | TP et assets T10/T17 |
| RVW-017 | PARTIEL | Contrats T10 et T17 rendus disciplinaires et testables. | `T10_contract.yml`, `T17_contract.yml` |
| RVW-018 | PARTIEL | T17 sépare les données cours, TD et évaluation ; P08 utilise deux contextes d'évaluation distincts. | Lots P08/T17 |

## Stabilisation des lots 1–3

| Point | Statut | Preuve |
|---|---|---|
| Fichiers nouveaux suivis ou documentés | PASS | 7 ajouts dans l'index Git : 4 documents P08, le test de régression et 2 rapports ; `git ls-files --others --exclude-standard` est vide. |
| T10 vérifié source par source | PASS — réserve verdicts | Mini-revue ci-dessous ; gates SQL, cours, profondeur, TD, évaluations, contrats et assets verts. |
| P08 évaluations vérifiées | PASS PARTIEL | Deux stimuli, corrigés et barèmes distincts ; réserve explicite sur le reste de la séquence P08. |
| T17 vérifié source par source | PASS PILOTE — réserve verdict | Mini-revue ci-dessous ; gates de récurrence, cours, profondeur, TD, évaluations, contrats et assets verts. |
| Rendus régénérés | PASS TECHNIQUE — réserve PDF | `dist/rendered_units/{T10,P08,T17}` contient les HTML complets élève/professeur et les PDF minimaux d'audit prévus par `render_unit.py` ; `dist/` reste ignoré. |
| Tests ciblés | PASS | Test de régression : 6/6 ; tous les gates demandés hors ancres : PASS. |
| Tests globaux | BLOQUÉ EXPLIQUÉ | Les seuls blocages fonctionnels restants sont les verdicts obsolètes ; le test réseau passe hors bac à sable. |
| Verdicts obsolètes identifiés | PASS | 9 fichiers : `T-ALGO-04` et `T-BDD-03A` à `T-BDD-03H`. Aucun JSON modifié. |
| Limites restantes | DOCUMENTÉES | Re-jugement indépendant, réserve P08 hors évaluations et autres RVW transversaux. |

## Mini-revue de validation source

| Lot | Élément | Statut | Preuve / réserve |
|---|---|---|---|
| T10 | Cours | CONFORME | Situation-problème, activité d'entrée, définitions, méthode générale, trois exemples corrigés, cas limites, erreurs spécifiques et critères de révision. |
| T10 | TD | CONFORME | Deux banques de six exercices non cycliques ; lecture, trace, écriture, débogage, transfert ; corrigés intégrés avec résultats exacts et contrôles. |
| T10 | TP | CONFORME | 75 min, livrables, quatre signatures, commande de test, cas nominal/frontière/vide/invalide, exemples corrigés et prolongement. |
| T10 | Évaluations | CONFORME | Deux sujets de 40 min, bases fournies, questions graduées, données différentes du cours, repères enseignants, critères, cas limites et erreurs fréquentes. |
| T10 | Barème | CONFORME | Critères par question : projection, table, condition, jointure, clé, `WHERE`, résultat ; crédits partiels et plafonds. |
| T10 | Corrigé | CONFORME | Requêtes complètes, rôle des clauses, tableaux de résultats, méthodes, pièges et cas limites. |
| T10 | Trace | CONFORME | Définitions, choix de l'opération, méthode numérotée, exemples, pièges, cas limites et auto-vérification. |
| T10 | Remédiation | CONFORME | Diagnostics SELECT/UPDATE, oubli de `WHERE`, mauvaise jointure ; autre représentation, réparation et transfert sans aide. |
| T10 | Version aménagée | CONFORME | Segmentation et aides graduées ; clauses à choisir/compléter ; aucune requête finale fournie. |
| P08 | Évaluations | CONFORME — PÉRIMÈTRE DU LOT | HTML/CSS/DOM : arbre, sélecteurs, événement, trace et modification ; HTTP : GET, POST, ordre client/serveur, stockage, HTTPS et confidentialité. |
| P08 | Barèmes/corrigés | CONFORME | Deux paires distinctes, critères observables, réponses partielles, raisonnement, pièges et cas limites. |
| P08 | Cours/TD/TP/trace/remédiation/version aménagée | RÉSERVE | Hors lot 2 ; les TD `alpha…theta` et la version aménagée commune restent notamment à reprendre. |
| T17 | Cours | CONFORME | Situation-problème non gloutonne, activité d'entrée, état/récurrence, trois exemples corrigés, reconstruction, cas limites, erreurs et complexité. |
| T17 | TD | CONFORME | Six tâches distinctes : lecture, trace, contre-exemple, code, débogage, transfert grille ; corrections et cas limites. |
| T17 | TP | CONFORME | 75 min, signatures, fichiers, commande, cas nominaux/impossible/invalides, exemples de validation et prolongement. |
| T17 | Évaluation | CONFORME | 45 min, données `[1,4,6]` inédites, modélisation, calcul, code, impossible, complexité et critères observables. |
| T17 | Barème/corrigé | CONFORME | Points de modèle, initialisation, récurrence, calcul, reconstruction et code ; raisonnements, erreurs structurantes et réponses partielles. |
| T17 | Trace | CONFORME | État, méthode numérotée, table, reconstruction, impossible, complexité, pièges et auto-vérification. |
| T17 | Remédiation | CONFORME | Trois diagnostics, schéma de dépendances, réparation guidée et tâche isomorphe sans aide. |
| T17 | Version aménagée | CONFORME | Table segmentée, aides successives, objectif conservé, valeurs finales masquées. |

## État Git consolidé

- 62 entrées dans `git status --short` : 55 fichiers suivis modifiés et 7 ajouts indexés.
- 37 sources/ressources pédagogiques et assets dans les trois lots, dont 4 nouveaux documents P08.
- 18 artefacts suivis régénérés : `INDEX.md`, dix `INDEX_BY_*`, `coverage.md`, `coverage_sources.md`, `inventory_report.md`, deux manifests et deux matrices programme.
- 1 registre de gouvernance mis à jour : quatre lignes `pending` dans `human_review_register.csv` ; aucune validation.
- 3 fichiers de tests modifiés ou ajoutés et 1 gate SQL modifié.
- 12 rendus ignorés régénérés : HTML élève/professeur complets et PDF minimaux d'audit pour T10, P08 et T17.
- Aucun fichier non suivi restant ; aucun commit créé.

## Re-jugement nécessaire

| Capacité | Ancienne preuve obsolète | Source corrigée | Action requise |
|---|---|---|---|
| T-ALGO-04 | Ancres `#méthodes` et `#exercice-2` ; citations de l'ancienne fiche T17. | Cours, TD et corrigé T17 réécrits. | Nouveau jugement indépendant sur les trois rôles, puis veto d'ancres et revue humaine. |
| T-BDD-03A | `#à-savoir`, `#exercice-1` ; liste de mots-clés et ancien exercice générique. | Cours, TD lecture et corrigé T10. | Re-sélectionner une preuve qui fait identifier le rôle des clauses. |
| T-BDD-03B | `#à-savoir`, `#exercice-2` ; citation mêlant filtre et JOIN. | Exemple de projection, TD exercice 3 et corrigé. | Re-juger exclusivement la construction `SELECT`/`FROM`. |
| T-BDD-03C | `#méthodes`, `#exercice-3` ; ancienne correction parlant d'`UPDATE`. | Méthode `WHERE`, table de trace et corrigés T10. | Re-juger le filtrage avec preuve verbatim pertinente. |
| T-BDD-03D | `#méthodes`, `#exercice-4` ; ancienne correction parlant de `DELETE`. | Méthode de jointure, TD exercices 4–5 et corrigés. | Re-juger `JOIN ... ON` et la clé de jointure. |
| T-BDD-03E | `#à-savoir`, `#exercice-5` ; ancienne projection générique. | Exemples de tri, TD exercices 1, 2, 3 et 6. | Re-juger `ORDER BY` sur une production et son résultat exact. |
| T-BDD-03F | `#à-savoir`, `#exercice-6` ; citation de correction introuvable et JOIN hors sujet. | Cours INSERT, TD modification exercice 2, évaluation et corrigé. | Re-juger INSERT ; refuser toute citation non verbatim. |
| T-BDD-03G | `#à-savoir`, `#exercice-7` ; ancien exercice générique et ancre supprimée. | Cours UPDATE, TD exercices 3 et 5, évaluation et corrigé. | Re-juger UPDATE avec `WHERE` et contrôles avant/après. |
| T-BDD-03H | `#à-savoir`, exercice 3 sur UPDATE et correction 4 ancienne. | Cours DELETE, TD exercice 4, évaluation et corrigé. | Re-juger DELETE avec cible, résultat vide et portée. |

Procédure prévue par le dépôt, à exécuter par un juge distinct de l'auteur :

1. Vérifier la sélection sans écriture : `python -m scripts.judge_campaign --cap-ids T-ALGO-04,T-BDD-03A,T-BDD-03B,T-BDD-03C,T-BDD-03D,T-BDD-03E,T-BDD-03F,T-BDD-03G,T-BDD-03H --dry-run` ; résultat observé : 9 capacités, T10 et T17.
2. Produire les candidats hors du dossier de campagne : `python -m scripts.judge_campaign --cap-ids ... --force --output-dir /tmp/nsi-rejudgment-2026-07-12` avec `ANTHROPIC_API_KEY` fourni au processus.
3. Vérifier séparément chaque candidat : `python -m scripts.check_substance_anchors /tmp/nsi-rejudgment-2026-07-12/<CAP>_substance_review.json --repo-root .` ; refuser les citations non verbatim, hors rôle ou hors libellé.
4. Faire relire les neuf jugements par un humain ; conserver `needs_review` et `human_review_required`. Aucun `validated_*`, `covered` ou `published` ne peut être produit par cette campagne seule.
5. Remplacer les verdicts de campagne uniquement par la procédure de promotion prévue après validation, jamais par édition manuelle, puis relancer le gate global.

## Gates / tests

| Commande | Résultat | Note |
|---|---|---|
| `python -m pytest tests/test_excellence_remediation_regressions.py` | PASS — 6/6 | Non-régressions T10, P08 et T17. |
| `python -m scripts.check_sql_query_result_consistency` | PASS — 13 fichiers | Jeu stable, types d'opérations et résultats SQL. |
| `python -m scripts.check_dynamic_programming_recurrence_consistency` | PASS — 10 fichiers | État, initialisation, récurrence et tables. |
| `python -m scripts.check_linked_td_substance` | PASS — 37 TD | Corrigés intégrés disciplinaires, dont les deux TD T10 consolidés. |
| `python -m scripts.check_linked_evaluation_substance` | PASS — 37 évaluations | Sujets et repères enseignants substantiels. |
| `python -m scripts.check_first_batch_alignment` | PASS | Alignement documentaire. |
| `python -m scripts.check_contract_substance_quality` | PASS — 35 contrats | T10/T17 compris. |
| `python -m scripts.check_eval_bareme_pairing` | PASS — 43 paires | Les deux nouveaux couples P08 sont visibles dans l'archive Git. |
| `python -m scripts.check_links` | PASS | Aucun lien source rompu. |
| `python -m scripts.check_status_promotion_guard` | PASS — 0 promotion | Statuts inchangés. |
| `python -m scripts.check_course_explanatory_quality` | PASS — 41 cours | Les lacunes T10/T17 révélées par l'audit d'archive ont été corrigées. |
| `python -m scripts.check_support_pedagogical_depth` | PASS — 173 supports | Les lacunes de profondeur révélées par l'audit d'archive ont été corrigées. |
| `python -m scripts.check_human_review_register` | PASS — 533/533 | Quatre nouvelles lignes P08, toutes `pending`. |
| `make render-unit U=T10`, `U=P08`, `U=T17` | PASS TECHNIQUE | 12 artefacts régénérés ; les PDF sont les prototypes d'audit d'une page produits par `minimal_pdf`, pas des exports de classe. |
| `git diff --check` | PASS | Aucun espace fautif ni marqueur de conflit. |
| `python -m scripts.check_substance_anchors` | FAIL ATTENDU — 9 verdicts | Anciennes ancres/citations T10 et T17 ; JSON laissés inchangés. |
| Audit de l'archive source | FAIL ATTENDU au gate d'ancres | Tous les gates précédents, dont profondeur et registre humain, passent dans l'archive. |
| Test réseau ciblé, bac à sable | FAIL ENVIRONNEMENTAL | La création de socket est interdite avant la fixture : `PermissionError`. |
| Même test réseau hors bac à sable | PASS — 1/1 | Confirme que la fixture bloque bien `connect` avec l'exception attendue. |
| `python -m pytest -q` | 452 PASS, 2 FAIL, 2 sous-tests PASS | Les deux échecs proviennent du même blocage documenté : gate d'ancres direct et audit de l'archive arrêté à ce gate. Aucun autre échec global restant. |

## Limites

- Au 2026-07-12, les neuf verdicts listés ci-dessus sont techniquement obsolètes et ne doivent pas être utilisés comme preuves valides ; le chantier n'est pas terminé tant que le re-jugement indépendant n'a pas été mené.
- Au 2026-07-12, P08 est validé seulement pour le lot des deux évaluations, de leurs deux barèmes et de leurs deux corrigés. Le cours, les TD, les TP, la trace, la remédiation et la version aménagée commune restent à auditer et réécrire dans un lot ultérieur.
- Les lots P06/P11/P12/T16, T19 et les autres banques P06–P14/T06–T19 restent à traiter ; RVW-003, RVW-004 et RVW-008 à RVW-018 ne sont donc pas soldés transversalement.
- Au 2026-07-12, les HTML de `dist/` sont complets, mais les PDF de 663 octets sont les artefacts minimaux d'audit explicitement produits par `scripts/render_unit.py::minimal_pdf`. Un moteur de composition réel reste nécessaire avant livraison de PDF élèves/professeurs ; `dist/` demeure ignoré par Git.
- Aucun statut n'a été promu et aucun verdict JSON n'a été modifié.

## Recommandation pour le lot suivant

Priorité : **T19**, après re-jugement T10/T17. Son évaluation bac/oral/projet est P1 et non autosuffisante : elle touche directement la préparation certificative, alors que P11/P12/T16 peuvent ensuite réutiliser le standard algorithmique stabilisé avec T17.

## État prêt pour re-jugement indépendant

- Branche : `remediation/excellence-lots-1-3`
- HEAD : `a6e7736a66a03f8e34e836d2a29f3fed3867cf1f`
- Fichiers indexés : 62, dont 55 modifications et 7 ajouts ; aucun fichier non suivi ni changement non indexé.
- Tests verts : 452 tests globaux, 2 sous-tests et tous les gates documentaires ciblés hors ancres ; régressions excellence 6/6.
- Gates encore rouges : `check_substance_anchors`, directement et dans l'audit de l'archive source.
- Verdicts à re-juger : `T-ALGO-04` et `T-BDD-03A` à `T-BDD-03H`.
- Interdiction de merge avant re-jugement : ne pas merger tant que le jugement indépendant n'a pas produit des preuves valides et que `python -m scripts.check_substance_anchors` n'est pas vert.
