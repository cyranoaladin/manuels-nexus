# Points en attente de validation humaine

Ce fichier centralise tout ce qu'un humain devra re-verifier avant commercialisation.

## Referentiel / B.O. (BLOQUANT COMMERCIALISATION)
- [x] Texte BO 2026 depose : `sources/BO2026_1SPE_specialite.pdf` (SHA-256 verifie)
- [x] Conformite verifiee sur texte officiel le 18/07/2026 — voir `referentiel/CONFORMITE_BO2026.md`
- [x] TRIGO C3/C4/C5 retires (backlog TSPE v2), chapitre recompile 16p
- [ ] **Validation humaine finale** de `CONFORMITE_BO2026.md` requise avant commercialisation
- [ ] Reformuler les `libelle_bo` comme citations exactes du BO 2026 (actuellement formulations agent)
- [x] Ajouts produits : paires/impaires + valeur absolue + x^n Z dans DERIVATION-GLOBAL (EX-051 a 053), Konig-Huygens deja present

## 6. Terminale (TSPE v1, programme 2019)
- [x] Texte BO 2019 depose : `sources/BO2019_TSPE_specialite.pdf`
- [ ] Valider la liste des 12 chapitres (`docs/10_perimetre_terminale.md`)
- [x] Referentiels `capacites_TSPE_*.json` en cours de creation depuis le BO 2019

## 7. Hotfix SymPy du 29/07/2026 (relecture pedagogique recommandee)
- [ ] `1SPE-SUITES/cours/07_td_fil_rouge.tex` : le TD original affirmait un seuil de depassement a n=167 mois, jamais verifie par calcul reel (l'algorithme decrit ne l'atteignait jamais). Recalcul : vrai seuil n=1415 mois (~118 ans). Le TD a ete entierement reecrit (enonce, algorithme corrige, conclusion). Relecture pedagogique recommandee avant publication : le nouveau resultat ("118 ans, hors de portee pratique") change la portee didactique de l'exercice par rapport a l'original.
- [ ] `1SPE-SUITES/cours/07_td_contextualise.tex` : toutes les valeurs numeriques de decroissance radioactive (M_10, M_50, M_55, M_57/58, M_100, demi-vie) etaient fausses. Recalculees et corrigees (demi-vie reelle du modele : 57 siecles, et non 58). Relecture pedagogique recommandee.
- [x] 14 autres corrections sont des corrections de fond mineures (assertion VERIFY erronee) ou de compatibilite sympy 1.14 (comparaison float/Rational) sans impact sur le contenu imprime deja correct — pas de relecture necessaire.

## Modes degrades
- [ ] MODE FICHIERS : la production est realisee sans base PostgreSQL/pgvector. Le corpus et la recherche se font par lecture directe des fichiers JSON. A migrer vers la base en production.
- [ ] PostgreSQL : le port local 5432 est déjà occupé par un service externe qui n'accepte pas les identifiants du projet ; l'instance Docker dédiée n'a donc pas été conservée. Prévoir une base dédiée (port libre ou réseau Docker) avant la mise en production.
- [ ] GENERATION EX NIHILO : pas de collecte web realisee. Tous les contenus sont generes depuis les connaissances du modele + referentiel. A croiser avec les vraies sources eduscol/APMEP.
- [ ] Dérivation locale : le crawler Éduscol a découvert 0 document exploitable le 15 juillet 2026 ; enrichir le corpus avec les ressources d'accompagnement officielles et des analyses didactiques avant commercialisation.
