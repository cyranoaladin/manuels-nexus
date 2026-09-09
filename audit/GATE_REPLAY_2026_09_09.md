# Rejeu des gates — 9 septembre 2026

Constat, exécuté **depuis un clone propre** de `origin/main`, avec un
environnement construit à partir du seul `requirements-ci-audit.txt`. Les
résultats du 15 août ne valaient plus rien : ils avaient été obtenus depuis
`.worktrees/t3-publish-readiness`, où le filtre de périmètre excluait la
totalité du dépôt (voir le commit `[GATE] juger le périmètre sur le chemin
relatif`).

## Résultats

| Gate | Attendu | Obtenu | Raisons | Verdict |
|---|---:|---:|---:|---|
| `require-clean` | 0 | **0** | 0 | **VERT** |
| `check` | 0 | 3 | 1 | ROUGE |
| `validate-model` | 0 | 6 | 628 | ROUGE |
| `fail-on-new` | 0 | 5 | 1 263 | ROUGE |
| `release-strict` | 7 | **7** | 127 | rouge **attendu** |

`release-strict` sortant en 7 est le comportement que la CI attend : le contrat
`EXPECTED_GATE_EXIT_CODES` de `scripts/ci_audit_collection.py` prévoit ce code.
Sa rougeur n'est donc pas une régression, c'est son état nominal tant que la
release n'est pas acquise.

## Ce qui bloque `check` : une seule chose, et elle est humaine

```
qualification_invalide:4a32199d0e3b5481
  fiche méthode modifiée après qualification (STALE)
  Mathematiques/manuel-maths/chapitres/TEXP-ARITHMETIQUE/methodes/TEXP-ARI-ME-009.tex
```

La fiche a été modifiée par le commit `3554051e0` — antérieur à cette
consolidation — ce qui a périmé sa qualification. La re-qualifier exige un
`approved_by` appartenant à `APPROVED_OWNERS` : `direction_editoriale_pedagogique`,
`direction_scientifique_programme` ou `ingenierie_build_qualite`. Ce sont des
rôles humains. **Aucune re-qualification n'a été fabriquée.**

Le dépôt porte d'ailleurs la trace d'un arbitrage identique assumé plus tôt :
`371baf9a8 [EDITORIAL] preserver 85 qualifications humaines : accents revoques
sur ces fiches`.

## Ce qui bloque `release-strict` : la revue humaine, pour les 52 chapitres

Familles des 127 raisons :

| Famille | Nombre |
|---|---:|
| `HUMAN_REVIEW_PENDING` | **52** |
| `CONTENT_PRODUCER_STALE_OR_RED` | 14 |
| par manuel (1NSI 15, TNSI 14, 1SPE 8, TSPE 8, …) | reste |

52 pour 52 chapitres : **chaque chapitre du périmètre canonique attend sa revue
humaine**. C'est cohérent avec `audit/PUBLISH_READINESS_CHAPTER_MATRIX.json`,
qui déclare `machine_review_complete: 52` et `human_closed: 0`.

Dimensions couvertes par ce gate : `execution` et `pedagogy` en échec,
`structure` en échec ; `mathematics`, `print`, `regulation` et `visual`
ressortent `not_covered` — elles ne sont pas vertes, elles ne sont pas
mesurées.

## Ce qui bloque les deux autres

`validate-model` : 627 raisons `policy_gate` et la qualification périmée
ci-dessus. `fail-on-new` : 1 263 anomalies nouvelles par rapport à la baseline
d'anomalies. Une partie provient mécaniquement des 60 objets récupérés de
`codex/urgent-1nsi-content`, qui entrent avec le statut `needs_review` et
comptent donc comme nouvelles tant qu'elles ne sont pas revues.

## Ce que ce rejeu établit

Un seul gate est vert : `require-clean`. Aucun seuil n'a été abaissé, aucun
contrôle retiré, aucune anomalie reclassée pour obtenir ces chiffres.

Le blocage dominant n'est pas technique : c'est l'absence de revue humaine sur
les 52 chapitres. Aucune opération machine ne peut la remplacer.
