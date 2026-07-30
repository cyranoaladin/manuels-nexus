# Décision requise — qualification de la baseline Phase 0

## État observé

Ce dossier ne vaut pas approbation. Il décrit le dernier verrou humain avant le
gel de la baseline de dette.

| Élément | Valeur |
|---|---|
| HEAD observé | `9e3fe7c34a9968c4145d5922afbb3d9818d21ec6` |
| Branche | `finalisation/collection-v1` |
| `source_digest` | `sha256:7160cd1f547a33f39d2e951da46bccd08731c7d000a40468a44d9cfc727e5033` |
| `model_digest` | `sha256:1f20bea5812f4428a9d2c5616df8eb1492e4298f27e8fbb4a9da128fa9e3b846` |
| Baseline actuelle | provisoire |
| Fingerprints actifs | 2 461 |
| Déjà qualifiés par une preuve versionnée | 4 |
| À qualifier | 2 457 |
| `baseline_ready` | 9 contrôles verts sur 10 |
| Seul contrôle rouge | `disposition_coverage` |
| `--fail-on-new` | code 5, baseline provisoire |
| `--release-strict` | code 7, 69 raisons déterministes |

L’identité du lot à qualifier est le SHA-256 du tableau JSON minifié, encodé
en UTF-8, des 2 457 fingerprints non qualifiés triés :

`sha256:ee6220cca262a6d5f331e7e86c514960c859f3b452c46ce24ac714ad521f13e8`

Cette empreinte doit être recalculée et rester identique avant toute
matérialisation de la décision.

## Répartition de la dette

| Catégorie | Fingerprints |
|---|---:|
| `blocking_statuses` | 1 796 |
| `unassembled_objects` | 614 |
| `broken_meta_references` | 24 |
| `unavailable_inspiration_sources` | 15 |
| `chapters_not_in_manual` | 4 |
| `missing_assemblers` | 3 |
| `unattributed_pdfs` | 1 |
| **Total** | **2 457** |

Chaque entrée est actuellement une dette ouverte bloquante. Sa qualification
ne la corrige pas et ne la rend pas publiable : elle autorise uniquement la
comparaison future entre dette nouvelle, inchangée, modifiée, disparue ou
réapparue.

## Décisions à fournir

1. Choisir la représentation :
   - **fichier explicite recommandé** : une disposition `open_debt` versionnée
     par fingerprint ;
   - politique de lot : évolution préalable du schéma et des tests, sans
     qualification implicite par défaut.
2. Valider les libellés de propriétaires pour les dettes Mathématiques, NSI et
   outillage éditorial transversal.
3. Fournir l’identité réelle de l’approbateur et une référence de décision
   durable pour la qualification de ce lot exact.
4. Fournir séparément la raison et l’approbateur du gel définitif passé à
   `--update-baseline`.

## Formulaire de décision

| Champ | Décision humaine attendue |
|---|---|
| Représentation | fichier explicite / politique de lot |
| Propriétaire Mathématiques | à fournir |
| Propriétaire NSI | à fournir |
| Propriétaire outillage transversal | à fournir |
| `approved_by` de la qualification | à fournir |
| `decision_ref` de la qualification | à fournir |
| Raison du gel définitif | à fournir |
| `approved_by` du gel définitif | à fournir |

Après réception, l’exécution doit rester atomique :

1. recalculer le nombre et l’empreinte du jeu encore non qualifié, puis les
   comparer à la décision avant toute écriture ;
2. matérialiser exactement ce jeu ;
3. prouver que les fingerprints dispositionnés sont exactement ceux du jeu
   approuvé ;
4. tester et committer les dispositions, puis revenir à un worktree propre ;
5. exécuter les dix préconditions et seulement alors appeler
   `--update-baseline` ;
6. démontrer `--fail-on-new = 0` et `--release-strict = 7`.

La CI ne met jamais à jour la baseline.
