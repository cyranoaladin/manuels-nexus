# Plan d’implémentation A5 `unclassified_types`

> Design autorisé par le GO A5 du 20 août 2026. Exécution TDD stricte,
> changements atomiques, aucun push/merge.

## Tâche 1 — preuves PRE-A5

Fichiers :

- `audit/A4_FINAL_CATEGORY_BALANCE.json`
- `audit/A4_FINAL_CATEGORY_BALANCE.md`
- `audit/A5_UNCLASSIFIED_TYPES_FORENSICS.json`
- `audit/A5_UNCLASSIFIED_TYPES_FORENSICS.md`

1. Mesurer l’inventaire frais au SHA source A4.
2. Prouver la somme 2971 et les 25 fingerprints omis.
3. Recalculer les 660 fingerprints et les trois clusters réels.
4. Faire relire indépendamment les artefacts.
5. Committer séparément balance puis forensique.

État : terminé par les commits `f2efed01` et `cc95edd0`.

## Tâche 2 — cluster `correction` : ontologie, test rouge, correction

Fichiers :

- `tests/test_inventory_collection.py`
- `audit/CANONICAL_OBJECT_TYPE_ONTOLOGY.yaml`
- `audit/CANONICAL_OBJECT_TYPE_ONTOLOGY.md`
- `audit/schemas/v1/canonical-object-type-ontology.schema.json`
- `scripts/inventory_collection.py`

Pour chaque cluster, les gates complets sont joués avant le commit principal
dans un clone de validation éphémère contenant le patch candidat, un commit
temporaire, le `--refresh-empty` du manifeste et les sorties gérées régénérées.
Le clone est jetable et ne publie rien ; le commit atomique final est créé dans
le worktree principal seulement après le vert de ce replay.

1. Ajouter les tests rouges de l’alias exact, de l’ambiguïté, des fautes, de la
   mauvaise section, du mauvais rôle et du sous-type interdit.
2. Créer le schéma et l’ontologie exécutable avec tous les types déjà reconnus,
   puis le seul alias A5 `correction -> corrige`.
3. Faire consommer ce registre à l’analyseur et retirer la table parallèle.
4. Exécuter les tests ciblés jusqu’au vert.
5. Exécuter un inventaire read-only et prouver `660 -> 7`, avec exactement les
   653 fingerprints `correction` retirés et aucun ajouté.
6. Vérifier `NEW_UNQUALIFIED=0`, dette attendue 89, packets stale 0,
   `fail-on-new`, `release-strict`, diff-check et les deux hashes immuables.
7. Vérifier qu’aucune méthode, aucun packet et aucun fichier source n’a changé.
8. Committer ce cluster atomiquement.

Commande :

```bash
python -m pytest -q tests/test_inventory_collection.py -k 'a5_object_type_correction'
```

## Tâche 3 — cluster `algorithme`

Fichiers :

- `audit/CANONICAL_OBJECT_TYPE_ONTOLOGY.yaml`
- `audit/CANONICAL_OBJECT_TYPE_ONTOLOGY.md`
- `scripts/inventory_collection.py`
- `tests/test_inventory_collection.py`

1. Ajouter les tests rouges du type canonique et de ses contraintes.
2. Ajouter uniquement `algorithme` à l’ontologie exécutable.
3. Exécuter les tests ciblés jusqu’au vert.
4. Exécuter l’inventaire read-only et prouver `7 -> 4`, exactement trois
   fingerprints retirés, aucun ajouté.
5. Rejouer `NEW_UNQUALIFIED`, dette 89, packet SHA scan, `fail-on-new`,
   `release-strict`, diff-check et hashes immuables.
6. Exiger zéro source/méthode/packet modifié et committer atomiquement.

## Tâche 4 — cluster `experimentation`

Fichiers :

- `audit/CANONICAL_OBJECT_TYPE_ONTOLOGY.yaml`
- `audit/CANONICAL_OBJECT_TYPE_ONTOLOGY.md`
- `tests/test_inventory_collection.py`

1. Ajouter les tests rouges du type canonique et de ses contraintes.
2. Ajouter uniquement `experimentation` à l’ontologie exécutable.
3. Exécuter les tests ciblés jusqu’au vert.
4. Exécuter l’inventaire read-only et prouver `4 -> 0`, exactement quatre
   fingerprints retirés, aucun ajouté.
5. Rejouer `NEW_UNQUALIFIED`, dette 89, packet SHA scan, `fail-on-new`,
   `release-strict`, diff-check et hashes immuables.
6. Exiger zéro source/méthode/packet modifié et committer atomiquement.

## Tâche 5 — ledger, manifeste et inventaire canonique

Fichiers :

- `audit/BUILD_MANIFEST.json`
- les six sorties gérées de `inventory_collection.py`.

1. Sceller le dry-run et vérifier `expected source changes = actual = 0`.
2. Ventiler : analyzer/schema 660 ; structured migration 0 ; invalid source
   corrections 0 ; legacy aliases 653 ; other explicit 7.
3. Vérifier un arbre propre et `builds=[]`.
4. Exécuter `python -B scripts/build_manifest.py --refresh-empty`.
5. Vérifier que seul le manifeste a changé et qu’il reste vide.
6. Committer le manifeste.
7. Régénérer l’inventaire canonique.
8. Vérifier le delta cumulé exact : 660 retirés, zéro ajouté.
9. Vérifier `unclassified_types=0`, les compteurs techniques et les 89 dettes.
10. Committer les six sorties gérées.

## Tâche 6 — gates ciblés et régressions

1. Jouer les tests A5.
2. Jouer les tests de régression A1, A2, A3 et A4.
3. Jouer inventory read-only, diff-check et packet SHA scan.
4. Jouer `--fail-on-new` et exiger zéro nouveau fingerprint.
5. Jouer `--release-strict`, exiger rc 7, 66 raisons, zéro raison ajoutée.
6. Jouer `--validate-model` et consigner séparément les neuf raisons APT
   préexistantes, sans toucher aux statuts.
7. Recalculer les SHA256 complets de `REFERENCE_BASELINE` et `HUMAN_POLICY`.
8. Vérifier zéro diff dans les 89 méthodes et packets face au SHA de départ.
9. Committer l’attestation A5 si tous les invariants de lot sont satisfaits.

## Tâche 7 — tests globaux et smoke builds

1. Exécuter `python -m pytest -q tests/`.
2. Exécuter `python -m pytest -q Mathematiques/manuel-maths/tests/`.
3. Exécuter `python -m pytest -q NSI/tests/`.
4. Exiger zéro échec et aucun skip/xfail ajouté.
5. Vérifier les 12 PDF suivis contre `A4_BUILD_MATRIX_EVIDENCE.json`.
6. Construire 1SPE élève/professeur et 1NSI élève/professeur sans enregistrement
   observé.
7. Vérifier qu’aucun PDF suivi n’a changé.

## Tâche 8 — scellement hermétique

1. Committer l’attestation finale et figer `A5_SOURCE_SHA`.
2. Exiger worktree propre, `git diff --check`, aucun writer/verrou actif.
3. Créer deux clones frais attachés à la branche et au SHA exact.
4. Rejouer inventaire, tests A1–A5, suites globales, gates et smokes dans A/B.
5. Comparer ensembles de fingerprints, sorties de gates et SHA256 des PDF.
6. Recalculer encore les deux hashes immuables et vérifier les 89 sources et
   packets inchangés/frais.
7. Exiger A == B et worktrees propres.
8. Rapporter A5 puis STOP ; ne commencer aucun autre lot.
