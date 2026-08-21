# Plan — projeter les bloqueurs globaux dans release-strict

> Plan TDD du design `2026-08-21-release-strict-collection-blockers-design.md`.

## Task 1 — Sceller le contrat par des tests rouges

**Fichier :** `tests/test_inventory_collection.py`

1. Ajouter des helpers de fixture minimaux qui produisent une matrice release
   intégrée et un inventaire d'anomalies/qualifications explicite.
2. Ajouter les mutations du design : portée globale/manuelle, catégorie future,
   ancienne allowlist, qualification absente ou mal typée, exemption booléenne,
   ordre stable, éligibilité manuelle et éligibilité chapitre. Paramétrer
   explicitement les valeurs `blocking` trompeuses `0`, `""`, `"false"`,
   `[]`, `{}` et `None`, puis contrôler séparément le booléen exact `False`.
   Pour la catégorie future portée chapitre, verrouiller à la fois
   `_chapter_publication_eligible` et
   `_calculate_claim(..., "completude")`.
   Pour le nouveau `and not blockers`, rendre explicitement toutes les autres
   dimensions de `PUBLICATION_GATE_TEMPLATE` vraies, toutes les variantes
   compilées et tous les critères structurels satisfaits ; prouver l'état
   `publication_eligible=True` sans blocker, puis son unique transition à
   `False` après ajout du blocker.
3. Lancer uniquement les nouveaux tests et archiver le RED exact. Le RED doit
   démontrer l'absence actuelle de raison `COLLECTION` ou l'éligibilité
   incorrecte, sans modifier la production.

## Task 2 — Implémentation minimale GREEN

**Fichier :** `scripts/inventory_collection.py`

1. Extraire `_qualification_blocks_release(anomaly, category,
   qualifications)` ; seule la valeur booléenne exacte `False` exempte.
2. Faire déléguer `_anomaly_is_blocking` à ce prédicat après la vérification de
   portée manuelle.
3. Remplacer les parcours release de l'ancienne allowlist par un parcours trié
   de toutes les catégories présentes dans `inventory["anomalies"]`, y compris
   dans `_chapter_publication_eligible`.
4. Ajouter `_collection_blockers(inventory)` avec partition exclusive
   `_anomaly_manual(...) is None` et agrégation stable par catégorie.
5. Ajouter les raisons `COLLECTION` au gate et faire échouer sa dimension
   structure en leur présence.
6. Considérer chaque blocker `anomalie:*` manuel comme structural et ajouter
   `and not blockers` à `publication_eligible`.
7. Supprimer `STRUCTURAL_ANOMALY_CATEGORIES`, devenu sans consommateur et sans
   autorité légitime ; conserver `BLOCKING_ANOMALY_CATEGORIES` uniquement pour
   ses contrôles historiques de corpus, jamais pour une décision release.
8. Rejouer les nouveaux tests jusqu'au GREEN, puis refactorer seulement les
   duplications réellement apparues.

## Task 3 — Régressions et preuve du delta réel

**Fichiers :** aucun autre edit attendu.

1. Rejouer les tests release, deliverable et qualification existants.
2. Lancer la suite ciblée de `tests/test_inventory_collection.py` couvrant le
   lot.
3. Sur le dépôt réel, exécuter `--release-strict`, recalculer la liste et son
   digest ; exiger 67 raisons, exactement deux ajouts et aucune suppression.
4. Exécuter `--validate-model` et `--fail-on-new` ; exiger rc0.
5. Prouver que RAW, fingerprints, source/model digests, qualifications,
   baseline, dispositions, politiques et statuts sont inchangés. Prouver
   séparément le changement attendu de provenance : `head_sha`, hash du
   générateur `scripts/inventory_collection.py` et `generator_sha256`.
6. Faire relire le diff par une revue spécification et une revue qualité.

## Task 4 — Commits et artefacts dérivés

1. Commit atomique du design/plan après revue.
2. Commit atomique code+tests après GREEN et double revue.
3. Depuis l'arbre propre, rafraîchir le manifest vide si les digests du modèle
   l'exigent ; contrôler le delta, puis commit dédié.
4. Depuis le nouveau HEAD propre, régénérer les six artefacts d'inventaire ;
   contrôler le delta et commit dédié.
5. Rejouer les quatre gates sur arbre propre. `release-strict` doit rester
   rouge avec le delta exact documenté.

## Task 5 — Continuer T1

Après scellement, commencer la classification déterministe des 22 PDF selon
le mandat T1.2. Conserver les 12 snapshots de publication divergents comme
dettes release explicites ; toute décision de remplacement, déplacement ou
suppression du hub reste un gate humain distinct.
