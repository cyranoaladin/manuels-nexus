# État de départ audité — reprise Phase 0.1

Date de constat : 2026-07-29

Worktree : `/home/alaeddine/.config/superpowers/worktrees/Manuels_Nexus/finalisation-collection-v1`

Branche : `finalisation/collection-v1`

HEAD réel : `20679de69a25d694196a2153f6f4d16fe4c4aa91`

Jalon historique : `f500166605d0891e148511a9c124fda9769c5f85`

Le jalon historique est un ancêtre du HEAD réel. Sept commits le séparent du
HEAD de départ. La branche n'est pas `main`. Aucun fichier n'était indexé au
moment du constat.

## Environnement

- Python : `3.12.3`
- pytest : `9.0.2`
- Git : `2.43.0`
- Système : Linux `6.8.0-136-generic`, x86_64

## WIP suivi préservé

Le WIP réel observé est plus large que les deux scripts annoncés lors du dernier
contrôle humain. Tous les fichiers ci-dessous ont été conservés sans
restauration, nettoyage, stash ni staging :

| Fichier | Ajouts | Suppressions |
|---|---:|---:|
| `ETAT_COLLECTION.md` | 1 | 1 |
| `audit/ECARTS_ET_CONTRADICTIONS.yaml` | 11 | 14 |
| `audit/INVENTAIRE_COLLECTION.json` | 13 | 16 |
| `audit/MATRICE_LIVRABLES.yaml` | 11 | 14 |
| `scripts/inventory_collection.py` | 245 | 21 |
| `scripts/inventory_reports.py` | 1 | 0 |
| `tests/test_inventory_collection.py` | 344 | 0 |

## Sauvegarde binaire hors dépôt

La totalité du diff suivi par rapport à
`20679de69a25d694196a2153f6f4d16fe4c4aa91` est sauvegardée hors dépôt :

- patch : `/tmp/nexus-phase0-start.HUzZ3q/tracked-wip-20679de.patch`
- taille : `36 846` octets
- SHA-256 :
  `eb98c671d9dedc8405527cd78404a03245dd48f8d6bb3db8d0fb4a8730f531af`
- format : `git diff --binary --full-index`

Cette copie sous `/tmp` est une protection de session, pas une archive
pérenne. Le patch n'inclut pas les fichiers non suivis, inventoriés ci-dessous.

## Fichiers non suivis et empreintes

| Fichier | SHA-256 |
|---|---|
| `.agents/skills/nexus-manual-quality/SKILL.md` | `a64cac91e70a09e2247a2e8d489c3a8c5033d394dacee17ad983e4acd54602a8` |
| `.codex/rules/manuals.rules` | `7d2a15963ca09f06a0b232e30dea272bd1f9adea34ec89db3214c2db74a32569` |
| `AGENTS.md` | `17bdd4ebabdb94f9a97dd460ad6fff950cca116f37a91bda19d6bfa61db7ec1d` |
| `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md` | `f300f08b439c96d1f316ff9e40711dd7c41f9522a5fdaaf26b8bdf8c1782bb25` |
| `docs/codex/ISSUE_REGISTER_TEMPLATE.md` | `3768d699ef4158bc0f8212c7b5fc797ad3412ce9f55f3935644e48e882cdda93` |
| `docs/codex/PROGRAMME_2026_MATRIX_TEMPLATE.md` | `3a39360607368c955c327035d84079bed91663e8c79668be61730957dff45cad` |
| `docs/codex/QUALITY_GATES.md` | `3240ce9f2eb3e2ff1b25d85eb2eaddf0a1e4e11a44fccbf1197dc35c5cedbdb5` |
| `docs/codex/README_INSTALLATION_CODEX.md` | `849bccdc7caa657d90460c6fcfadc2a15d1316ea41a95ab67f657094850d24ee` |

## Instructions applicables

Un seul `AGENTS.md` a été trouvé dans le dépôt, à la racine. Aucun
`AGENTS.override.md` ni `AGENTS.md` imbriqué ne modifie les règles pour les
fichiers actuellement concernés.

Les sources contractuelles, audits courants, directives Mathématiques et NSI,
états historiques et workflows GitHub Actions ont été lus avant la première
modification du dépôt. `audit/PHASE_0_1_PLAN.md` n'existe pas au moment du
constat.

## Décision de protection

Le WIP est attribué à la poursuite de Phase 0.1 tant que le diff, les tests et
l'historique ne prouvent pas un autre périmètre. Aucun bloc ne sera jeté ou
écrasé. Les artefacts générés resteront non indexés séparément des commits de
code, sauf lorsqu'un commit prévu exige explicitement leur mise à jour.
