# SÉMANTIQUE DÉFINITIVE DES MÉTRIQUES D'ANOMALIES

Taxonomie normative (arbitrage PRE-A4, 2026-08-19). Tout rapport, dashboard
ou gate doit employer ces quatre compteurs — le compteur ambigu
`release_blocking` utilisé comme synonyme de RAW est interdit.

## Taxonomie

| métrique | définition | source de calcul |
| --- | --- | --- |
| **RAW_ANOMALY_FINGERPRINTS** | tous les fingerprints actifs produits par l'inventaire (dette active) | `_current_active_debt(build_inventory(root))` |
| **BLOCKING_ANOMALY_FINGERPRINTS** | fingerprints actifs dont la sévérité qualifiée est bloquante (`release_blocking = true`) | idem, `severity == "blocking"` |
| **NONBLOCKING_ANOMALY_FINGERPRINTS** | fingerprints actifs non bloquants (`release_blocking = false`, ex. dispositions `intentional_reuse`) | idem, `severity != "blocking"` |
| **RELEASE_STRICT_REASON_IDS** | raisons déterministes rapportées par `--release-strict` (groupes par manuel/catégorie/livrable) | sortie du gate `release-strict` |

Invariant permanent :

```
RAW_ANOMALY_FINGERPRINTS = BLOCKING + NONBLOCKING
```

`RELEASE_STRICT_REASON_IDS` est un compteur de GROUPES de dette, pas de
fingerprints : il ne varie pas linéairement avec RAW.

## Valeurs recalculées au SHA PRE-A4 (`f0cc4586`)

```
RAW_ANOMALY_FINGERPRINTS      = 5612
BLOCKING_ANOMALY_FINGERPRINTS = 5612
NONBLOCKING_ANOMALY_FINGERPRINTS = 0
RELEASE_STRICT_REASON_IDS     = 76
invariant : 5612 = 5612 + 0  ✔
```

## Relecture correcte de l'effet A3

Les 3 `duplicate_assembly_objects` retirés par A3 étaient qualifiés
`intentional_reuse` (`release_blocking = false`, sévérité `warning`) :

```
                        avant A3 (018a0adb)   après A3 (f0cc4586)
RAW                     5615                  5612   (−3)
BLOCKING                5612                  5612   (inchangé)
NONBLOCKING             3                     0      (−3)
RELEASE_STRICT_REASONS  76                    76     (inchangé, diff exact vide)
```

L'ancienne formulation « TOTAL_RELEASE_BLOCKING 5615 → 5612 » était donc
sémantiquement fausse : A3 n'a retiré AUCUN blocker.

## Corrections d'usage

- `audit/A0_A1_STATE_TRANSITIONS.md/.json` (snapshot historique) : la ligne
  `TOTAL_RELEASE_BLOCKING` y égalait RAW par construction — annotée comme
  telle, valeurs historiques non réécrites.
- `audit/CURRENT_ANOMALIES_RAW.json` : dump ponctuel du 2026-08-16
  (6425 entrées, pré-A1-final) sans producteur dans le pipeline courant —
  reclassé **HISTORICAL_SNAPSHOT** ; ne jamais le lire comme vérité
  courante. La vérité courante des fingerprints actifs est recalculée
  depuis l'inventaire.
- Les rapports de session doivent désormais utiliser les quatre compteurs
  ci-dessus (§18 du protocole A4).

Aucune baseline n'est modifiée par cette clarification.
