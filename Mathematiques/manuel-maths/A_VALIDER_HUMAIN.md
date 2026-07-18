# Points en attente de validation humaine

Ce fichier centralise tout ce qu'un humain devra re-verifier avant commercialisation.

## Referentiel / B.O. (BLOQUANT COMMERCIALISATION)
- [ ] **Texte BO 2026 absent du depot** : fournir `sources/bo_2026_maths_1spe.pdf`
- [ ] Toutes les formulations `libelle_bo` dans `referentiel/capacites_1SPE_*.json` sont a verifier mot a mot contre le B.O. en vigueur (note R7 presente dans chaque fichier).
- [ ] Harmoniser les chapitres Suites et Second degre (ancres BO 2019) avec le BO n 14 du 2 avril 2026.
- [ ] Voir `referentiel/CONFORMITE_BO2026.md` pour le detail par chapitre (10/10 A_VALIDER_HUMAIN).

## 6. Terminale (TSPE)
- [ ] Fournir le texte BO Terminale dans `sources/bo_tspe_maths.pdf`
- [ ] Valider la liste des 13 chapitres provisoires (`docs/10_perimetre_terminale.md`)
- [ ] Creer les referentiels `capacites_TSPE_*.json` depuis le BO

## Modes degrades
- [ ] MODE FICHIERS : la production est realisee sans base PostgreSQL/pgvector. Le corpus et la recherche se font par lecture directe des fichiers JSON. A migrer vers la base en production.
- [ ] PostgreSQL : le port local 5432 est déjà occupé par un service externe qui n'accepte pas les identifiants du projet ; l'instance Docker dédiée n'a donc pas été conservée. Prévoir une base dédiée (port libre ou réseau Docker) avant la mise en production.
- [ ] GENERATION EX NIHILO : pas de collecte web realisee. Tous les contenus sont generes depuis les connaissances du modele + referentiel. A croiser avec les vraies sources eduscol/APMEP.
- [ ] Dérivation locale : le crawler Éduscol a découvert 0 document exploitable le 15 juillet 2026 ; enrichir le corpus avec les ressources d'accompagnement officielles et des analyses didactiques avant commercialisation.
