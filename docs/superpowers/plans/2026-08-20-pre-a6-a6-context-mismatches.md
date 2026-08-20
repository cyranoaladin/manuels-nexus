# Plan d’implémentation PRE-A6 / A6 `context_mismatches`

> Design autorisé par le GO PRE-A6/A6 du 20 août 2026. Exécution TDD stricte,
> revues indépendantes, commits atomiques, aucun push/merge/baseline update.

## Tâche 1 — sceller le snapshot et la forensique PRE-A6

Fichiers :

- `audit/PRE_A6_VALIDATE_MODEL_FORENSICS.json`
- `audit/PRE_A6_VALIDATE_MODEL_FORENSICS.md`

1. Rejouer l’inventaire et `--validate-model` au SHA de départ attaché à la
   branche autoritaire.
2. Extraire les neuf erreurs exactes et les neuf records historiques.
3. Prouver la bijection AGT→APT, le premier commit fautif et l’absence de
   décision humaine nouvelle.
4. Renseigner tous les champs demandés, `UNKNOWN=0`, et classifier les neuf
   cas `ID_MIGRATION_FINGERPRINT_DRIFT`.
5. Vérifier les hashes complets baseline, politiques et sources.
6. Faire relire les preuves, puis committer l’audit seul.

## Tâche 2 — résolution mécanique des neuf identités en TDD

Fichiers :

- `tests/test_inventory_collection.py`
- `scripts/inventory_collection.py`
- `audit/ANOMALY_IDENTITY_MIGRATIONS.yaml`
- `audit/schemas/v1/anomaly-identity-migrations.schema.json`

1. Ajouter les tests rouges d’un registre exact : succès des neuf couples et
   rejet des doublons, mapping absent, alias fuzzy/global, ADGK↔APT, hash ou
   transformation source invalide, statut/type/catégorie/politique/décision/
   digest divergents et disposition historique absente.
2. Exécuter les tests et constater les neuf qualifications courantes encore
   incomplètes.
3. Créer le schéma et le registre versionné des neuf migrations bijectives,
   avec hashes/transformations exactes et `control_digest`.
4. Enregistrer l’artifact type dans `SCHEMA_REGISTRY`, imposer YAML à clés
   uniques et `additionalProperties: false`, et inclure le registre dans
   `_is_model_source`, `source_digest` et la détection de drift.
5. Charger ce registre depuis le dépôt cible et projeter en mémoire le record
   historique, sans écrire de record courant dans les dispositions. Le schéma
   ne peut contenir aucun champ décisionnel.
6. Rejeter explicitement ancien record non qualifié/absent de la baseline,
   cible déjà dotée d’une disposition et toute mutation inter-dépôts ; ajouter
   une fixture prouvant que deux dépôts cibles utilisent leurs propres registres.
7. Remplacer le fallback `.replace("ADGK", "APT").replace("AGT", "APT")`
   de `fail-on-new` par ce même résolveur exact.
8. Exécuter les tests ciblés, les tests de politique et `--validate-model` sur
   un candidat cohérent ; exiger zéro qualification incomplète.
9. Vérifier qu’une mutation du registre rend les artefacts stale, puis vérifier
   byte-identiques baseline, dispositions et politique, promotions 0,
   statuts 2222, dette méthodes 89 et packets stale 0.
10. Faire les revues spécification puis qualité et committer atomiquement.

Commande ciblée :

```bash
python -m pytest -q tests/test_inventory_collection.py -k 'pre_a6 or validate_model'
```

## Tâche 3 — note et test de non-confusion `correction`

Fichiers :

- `audit/A5_CORRECTION_TYPE_SEMANTICS.md`
- `tests/test_inventory_collection.py`

1. Documenter les champs A0/A5, la même dimension `% META.type_objet`, les
   responsabilités différentes et le rôle source orthogonal.
2. Ajouter un test d’intégration avec `correction` et `corrige` qui vérifie
   valeur brute, type canonique, rôle `production_object`, liens de correction
   et rejet fail-closed d’une confusion de dimensions.
3. Prouver que le test détecte la régression en retirant l’alias uniquement
   dans la fixture temporaire, puis rétablir l’autorité canonique.
4. Exécuter les tests A0/A5 concernés, faire relire et committer séparément.

## Tâche 4 — fermer PRE-A6 avant autorisation A6

1. Rafraîchir l’enveloppe du manifeste vide dans un commit dédié.
2. Régénérer les sorties gérées d’inventaire dans un commit dédié.
3. Exécuter `--check --require-clean`, `--validate-model`, `--fail-on-new` et
   `--release-strict`.
4. Exiger `--validate-model=0`, `NEW_UNQUALIFIED=0`, statuts=2222,
   `EXPECTED_REVIEW_DEBT=89`, baseline/policy inchangées et promotion=0.
5. Si une décision humaine apparaît nécessaire, STOP sans démarrer la tâche 5.

## Tâche 5 — forensique A6 après gate vert

Fichiers :

- `audit/A6_CONTEXT_MISMATCH_FORENSICS.json`
- `audit/A6_CONTEXT_MISMATCH_FORENSICS.md`

1. Mesurer frais `A6_START_CONTEXT_MISMATCHES` et exiger 3.
2. Renseigner tous les contextes demandés pour les trois fingerprints.
3. Prouver contrats, programme, identités, références entrantes/sortantes,
   assemblages, capacités et absence de reviews liées.
4. Classer exactement les trois cas `PATH_CONTEXT_DRIFT` et sceller l’action
   de suppression des seules copies redondantes.
5. Faire relire les artefacts et committer l’audit seul.

## Tâche 6 — tests rouges A6

Fichier : `tests/test_inventory_collection.py`

1. Ajouter l’invariant dépôt reproduisant les trois mismatches courants.
2. Ajouter une fixture de copie exacte avec jumeau canonique.
3. Ajouter les mutations : mauvais chapitre, manuel incohérent dérivé du
   contrat, variante/assemblage incohérent, archive atteignable en production,
   basename proche sans correspondance fuzzy.
4. Exécuter les tests et constater le rouge avant la correction réelle.
5. Ne modifier ni l’ontologie ni l’analyseur pour rendre génériquement valide
   une valeur inconnue.

Commande ciblée :

```bash
python -m pytest -q tests/test_inventory_collection.py -k 'a6_context'
```

## Tâche 7 — correction minimale A6 et delta exact

Fichiers supprimés :

- `Mathematiques/manuel-maths/chapitres/TCOMPL-CALCULS-AIRES/cours/10_C1_derivee_composee.tex`
- `Mathematiques/manuel-maths/chapitres/TCOMPL-CALCULS-AIRES/cours/07_td_fil_rouge.tex`
- `Mathematiques/manuel-maths/chapitres/TCOMPL-CALCULS-AIRES/cours/07_td_contextualise.tex`

1. Vérifier une dernière fois les six SHA des copies et jumeaux canoniques et
   l’absence de référence/review entrante.
2. Supprimer exactement les trois copies TCOMPL via patch, sans toucher aux
   sources TSPE.
3. Exécuter les tests A6 jusqu’au vert.
4. Construire un inventaire read-only et exiger : removed=3, added=0,
   reclassified=0, `context_mismatches=0`.
5. Exiger zéro fingerprint ajouté/reclassifié, zéro nouvelle anomalie primaire
   et `NEW_UNQUALIFIED=0`; sinon STOP. Accepter seulement les changements de
   modèle attendus `sections_cours -1` et `td -2`, sans forcer RAW=2308.
6. Vérifier les invariants A1–A5, les 89 packets et les promotions nulles.
7. Faire les revues spécification puis qualité et committer atomiquement.

## Tâche 8 — manifeste et inventaire canonique

1. Sur un arbre propre et committé, exécuter
   `python -B scripts/build_manifest.py --refresh-empty`.
2. Exiger que seul `audit/BUILD_MANIFEST.json` change, que `builds=[]` demeure,
   puis committer.
3. Exécuter `python scripts/inventory_collection.py`.
4. Vérifier les six sorties gérées, le delta exact et les compteurs finaux,
   puis committer.
5. Exécuter `--check --require-clean`, `--validate-model`, `--fail-on-new` et
   `--release-strict`; exiger zéro nouveau reason id.

## Tâche 9 — tests globaux, régressions et builds

1. Exécuter les tests ciblés A6 et inventory/context.
2. Rejouer les gates exacts A1–A5.
3. Exécuter `python -m pytest -q tests/`.
4. Exécuter `python -m pytest -q Mathematiques/manuel-maths/tests/`.
5. Exécuter `(cd NSI && python -m pytest -q tests/)`.
6. Exiger zéro échec et aucun skip/xfail ajouté.
7. Hash les 36 PDF Git avant compilation.
8. Rebuilder TCOMPL chapitre `complet`/`parcours1` et manuel
   `eleve`/`professeur`, puis un smoke NSI représentatif, sans receipt.
9. Vérifier les sorties produites et les 36 PDF Git byte-identiques avant/après.

## Tâche 10 — scellement et herméticité

1. Sceller l’attestation A6 et committer pour obtenir `A6_SOURCE_SHA`.
2. Exiger worktree clean, diff-check=0, writers/verrous=0.
3. Créer deux clones frais attachés exactement à ce SHA.
4. Rejouer inventaire, validate-model, A6, A1–A5, suites globales, fail-on-new,
   release-strict et builds requis dans A et B.
5. Comparer fingerprints, compteurs, reason IDs, hashes de politiques, bindings
   des 89 packets et hashes PDF ; exiger A == B.
6. Rapporter A6 puis STOP. Ne commencer aucun autre lot.
