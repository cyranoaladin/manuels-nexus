# Réconciliation des branches — 9 septembre 2026

Constat et disposition. Ce document n'approuve aucune publication.

## Règle appliquée

Une branche n'est nettoyée qu'après l'une de ces preuves : elle est ancêtre de
`main` ; son patch y est déjà présent ; son contenu est explicitement remplacé
par une version supérieure ; ses apports utiles ont été portés ; ou son contenu
n'est fait que d'artefacts générés reproductibles.

Le critère n'est jamais la date du commit, mais **quel contenu final est le
plus correct, le plus complet et le plus conforme**.

## État initial

`main` accusait 1 443 commits de retard, 1 526 commits n'existaient sur aucune
ref distante, et la production vivait dans `.worktrees/t3-publish-readiness`.
Toutes les refs ont d'abord été poussées : aucune disposition n'a été prise
avant que le contenu ne soit sauvegardé et vérifié par SHA distant.

## Branches contenues dans `main` (14, supprimées localement)

`production/collection-v2`, `integration/1spe-bo2026-traceability`,
`finalisation/collection-v1`, `codex/t3-publish-readiness-current`,
`codex/t3-branch-b-proof`, `codex/t2-programme-coverage-ox-alpha`,
`codex/t2-current-audit-continue`, `codex/t2-current-10cb5f0`,
`codex/integrite-1spe`, `codex/forensic-761508d9`, `charte/v5-b-it2`,
`backup/pre-remediation-84b5185b`, `audit/pre-a6-a6-context-mismatches`,
`audit/adversarial-reconciliation-2026`.

Supprimées par `git branch -d`, qui refuse toute branche non fusionnée : la
preuve est faite par la commande elle-même. Toutes restent sur `origin`.

`integration/finalisation-2027`, tronc de consolidation temporaire, a été
supprimée localement et sur `origin` une fois `main` avancée sur son état.

## Branches portant des commits uniques (18)

Chacune est archivée par un tag immuable `archive/<branche>-2026-09-09`, en
plus de sa ref sur `origin`.

| Branche | Uniques | Disposition | Preuve |
|---|---:|---|---|
| `codex/urgent-1nsi-content` | 51 | **PORTED** | 60 méthodes/remédiations rédigées récupérées ; INT-005 porté. Ses retraits de clones sont **superseded** : le tronc en avait retiré 419 sur 435 de son côté et **réécrit** les 16 restants en exercices authentiques et distincts, ce qui préserve la couverture au lieu de la réduire. |
| `green/openrouter-only` | 46 | **SUPERSEDED** | Dispositionnée le 31 août (`audit/WORKTREE_RECONCILIATION_2026_08_31.json`) : shims sans corps, zéro consommateur ; politique de fournisseur externe jamais fusionnée en 789 commits, `FORENSIC_ONLY`. `tests/test_programme_registry.py` en a été porté. |
| `feature/1spe-bat-2026` | 34 | **PORTED (partiel)** | Contrôle de chaîne de fabrication porté. Son référentiel programme 1SPE concurrent est **écarté** : `main` porte une autre architecture, déjà consommée par la matrice de couverture. En adopter deux serait installer une source parallèle. |
| `docs/openrouter-only` | 27 | **SUPERSEDED** | N'ajoute face à `main` que le lot de plans/specs du 13 août et trois tests, communs à la famille ci-dessous. |
| `manifest-fix-tspe` | 15 | **SUPERSEDED** | Idem. |
| `green/p0-programme-tspe` | 13 | **ALREADY_IN_CURRENT** | Vérifié valeur par valeur le 31 août. |
| `wave0/p0-green-launch` | 9 | **SUPERSEDED** | Ancêtre imbriqué de la même famille. |
| `green/p0-student-separation` | 9 | **SUPERSEDED** | Dispositionnée le 31 août : tests obsolètes, un test déjà présent. |
| `wave0/p0-red-contracts` | 7 | **SUPERSEDED** | Ancêtre imbriqué de la même famille. |
| `codex/shared-infra-integration` | 4 | **PORTED (partiel)** | INT-005 porté avec son test. INT-006 **écarté** : le test vise une API que `main` a fait évoluer (`AttributeError: HUMAN_REVIEW_ROOT`). Le porter aurait figé une interface superseded. |
| `rescue/stash0-…`, `rescue/stash1-…` | 3, 3 | **ARCHIVED** | Archives des deux stashs du 15 août. 193 fichiers `.tex` qu'ils portaient et qui manquent à `main` sont **tous** supprimés explicitement par un commit de `main` (répertoire `backlog_tspe_v2/`). |
| `rescue/root-wip-2026-09-09` | 2 | **PORTED** | Travail racine du 9 septembre intégré ; `.gitignore` réconcilié par union raisonnée. |
| `codex/t2-inventory-refresh` | 2 | **SUPERSEDED** | Aucun fichier absent de `main`. |
| `rescue/t2-legacy-wip-…` | 1 | **PORTED (partiel)** | 16 fichiers à valeur nette récupérés sur 122, dont le registre des autorités réglementaires 2027 et la matrice de couverture programme. Ses paquets de revue humaine sont **superseded** : `main` les porte déjà sous `superseded/`. |
| `rescue/codex-tnsi-fix-2bcbd09` | 1 | **SUPERSEDED** | Aucun fichier absent de `main`. |
| `rescue/codex-a4-optional-review-…` | 1 | **SUPERSEDED** | Aucun fichier absent de `main`. |
| `codex/nsi-direct-fallback-4835` | 1 | **SUPERSEDED** | Aucun fichier absent de `main`. |

## Ce qui n'a pas été repris, et pourquoi

65 fichiers de chapitres TNSI absents de `main` ne viennent pas d'une branche :
ils existaient à la base commune et c'est **`main` qui les a supprimés**, dans
un retrait argumenté de 610 remplissages synthétiques amenant NSI à
`CLONE_GROUPS 0`. Les réintroduire aurait annulé ce travail.

## Ce que la réconciliation ne prouve pas

Aucune de ces dispositions ne vaut revue humaine, ni validation scientifique,
ni autorisation de publier.
