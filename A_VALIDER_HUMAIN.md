# Points en attente de validation humaine

Ce fichier centralise tout ce qu'un humain devra re-verifier avant commercialisation.

## Referentiel / B.O.
- [ ] Toutes les formulations `libelle_bo` dans `referentiel/capacites_1SPE_*.json` sont a verifier mot a mot contre le B.O. en vigueur (note R7 presente dans chaque fichier).
- [ ] Harmoniser au LOT FINAL les chapitres Suites et Second degré, produits à partir du programme 2019, avec le programme de première publié au BO n° 14 du 2 avril 2026 et applicable à la rentrée 2026-2027.

## Modes degrades
- [ ] MODE FICHIERS : la production est realisee sans base PostgreSQL/pgvector. Le corpus et la recherche se font par lecture directe des fichiers JSON. A migrer vers la base en production.
- [ ] PostgreSQL : le port local 5432 est déjà occupé par un service externe qui n'accepte pas les identifiants du projet ; l'instance Docker dédiée n'a donc pas été conservée. Prévoir une base dédiée (port libre ou réseau Docker) avant la mise en production.
- [ ] GENERATION EX NIHILO : pas de collecte web realisee. Tous les contenus sont generes depuis les connaissances du modele + referentiel. A croiser avec les vraies sources eduscol/APMEP.
