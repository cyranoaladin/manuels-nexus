# État distant de la Phase 0

Date de l'observation : 3 août 2026.

## Mission

- Branche observée : `finalisation/collection-v1`.
- SHA local observé : `e92e0e844716e535d8eaf0b84fc6910d22ad1c3d`.
- SHA distant observé : `origin/finalisation/collection-v1` =
  `e92e0e844716e535d8eaf0b84fc6910d22ad1c3d`.
- `git rev-list --left-right --count
  origin/finalisation/collection-v1...HEAD` : `0 0`.
- Worktree propre au moment de l'observation.

## PR et checks observés

- PR : [#1](https://github.com/cyranoaladin/manuels-nexus/pull/1),
  `OPEN`, `isDraft: true`, `headRefOid: e92e0e844716e535d8eaf0b84fc6910d22ad1c3d`.
- État de fusion GitHub : `CLEAN`.

| Workflow | Événement | Run | Job | Conclusion |
|---|---|---:|---:|---|
| CI audit collection Phase 0 | `push` | [30811442247](https://github.com/cyranoaladin/manuels-nexus/actions/runs/30811442247) | `91678884377` | `success` |
| CI audit collection Phase 0 | `pull_request` | [30811445088](https://github.com/cyranoaladin/manuels-nexus/actions/runs/30811445088) | `91678894525` | `success` |
| CI manuel mathématiques | `pull_request` | [30811445079](https://github.com/cyranoaladin/manuels-nexus/actions/runs/30811445079) | `91678895512` | `success` |
| CI manuels NSI | `pull_request` | [30811445083](https://github.com/cyranoaladin/manuels-nexus/actions/runs/30811445083) | `91678894712` | `success` |
| GitGuardian Security Checks | externe | — | — | `neutral` |

La PR présente donc quatre checks GitHub Actions réussis, aucun check en
échec ou en attente, et un contrôle externe neutre.

## Attestation Phase 0 canonique

Le run `push` `30811442247`, attaché directement au SHA de branche, est retenu
comme preuve canonique. Son artefact
`audit-collection-e92e0e844716e535d8eaf0b84fc6910d22ad1c3d`
(`id: 8855233280`, 1 551 655 octets compressés) a été téléchargé et inspecté.
Il expire le 17 août 2026.

Ordre observé des sous-gates : `require-clean`, `check`, `validate-model`,
`fail-on-new`, `release-strict`.

| Gate | Code observé | Code attendu | Erreurs de contrat | Bloqueurs |
|---|---:|---:|---:|---:|
| `require-clean` | `0` | `0` | `0` | `0` |
| `check` | `0` | `0` | `0` | `0` |
| `validate-model` | `0` | `0` | `0` | `0` |
| `fail-on-new` | `0` | `0` | `0` | `0` |
| `release-strict` | `7` | `7` | `0` | `64` |

Le fichier `gate-summary.json` porte `failure_count: 0` : le code `7` de
`release-strict` est attendu par le contrat CI et correspond à des dettes
réelles, non à une publication autorisée.

Autres preuves observées dans le run canonique :

- Ruff : succès ;
- mypy : succès sur les six fichiers du périmètre ;
- suite complète : 2 951 tests réussis, 5 ignorés ;
- couverture lignes + branches : 78,64 %, pour un seuil de 76,83 % ;
- parsing des JSON et YAML suivis : succès ;
- génération double : six artefacts comparés, aucune différence ;
- baseline Phase 0 : aucune mise à jour exécutée.

## Attestation du run NSI

Le run [30811445083](https://github.com/cyranoaladin/manuels-nexus/actions/runs/30811445083)
est attaché au SHA de tête
`e92e0e844716e535d8eaf0b84fc6910d22ad1c3d`. Toutes ses étapes ont réussi,
y compris l'upload final.

Preuves de reproductibilité et d'exécution observées dans le journal du job :

- dépendances installées avec `--no-deps` depuis
  `requirements-ci-audit.txt` ;
- Ruff `0.6.9` ;
- `pip check` : `No broken requirements found` ;
- tests NSI : 214 réussis ;
- accents : 173 fichiers vérifiés ;
- specimen : 9 pages ;
- gate d'exécution et couverture F01 du chapitre
  `1NSI-TYPES-CONSTRUITS` : succès ;
- assemblage `complet` du chapitre : succès ;
- occurrences `Missing character:` dans le journal : `0`.

## Artefact PDF NSI observé

L'artefact `pdf-nsi-5f076e52a496225ad5cc239cf747930eaafde87e`
(`id: 8855027784`, 287 980 octets compressés) a été téléchargé depuis le run
NSI. Le suffixe correspond au SHA de fusion synthétique du contexte
`pull_request`, tandis que le run déclare bien le SHA de tête `e92e0e8`.
L'artefact expire le 1er novembre 2026.

| Chemin dans l'artefact | Taille | Pages | Format | SHA-256 | Polices |
|---|---:|---:|---|---|---|
| `specimen/specimen.pdf` | 61 775 octets | 9 | A4, PDF 1.5 | `0c13fc28801221d3da40c59459191df32ff8d9cc7c20146318f89ccb78e18fdd` | 11/11 incorporées |
| `1NSI-TYPES-CONSTRUITS/1NSI-TYPES-CONSTRUITS_complet.pdf` | 238 816 octets | 36 | A4, PDF 1.5 | `1a384d56346c02c7915193df3bf09d0912c44f0b2a4d53a449b62a9ce9d2941b` | 12/12 incorporées |

Les deux fichiers ont été ouverts avec `pdfinfo`, inspectés avec `pdffonts` et
hachés après téléchargement. Cet artefact atteste un specimen et un chapitre
NSI assemblé ; il ne constitue pas un manuel NSI complet prêt à publier.

## Gouvernance de publication

- La réussite de la CI atteste le contrat de non-régression de Phase 0.
- `release-strict` reste rouge avec 64 bloqueurs réels.
- `release_acceptance=false` demeure applicable.
- La collection et le manuel de Mathématiques Première restent `NO-GO`
  publication.
- Aucune baseline visuelle n'a été modifiée ou approuvée par cette attestation.
