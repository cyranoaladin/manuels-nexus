# Baseline immuable 1SPE

## Deux vues distinctes

- Origine immuable : `41eaa745d000953654f7f07f6760c675cdae91d5` — 7 failed, 1873 passed, 5 skipped (historical_observation, historique non rejoué).
- État courant préflight : `ca16edbb51d7f0122fcbbfea5cccfa7e2066cd63` — 1946 passed, 5 skipped (direct_execution).
- Arbre de travail au moment de la capture : `clean` (politique `record`).
- HEAD matériel de capture : `dd7a5f95f5ae9211da18b090dae6aeaa214a1f42`.

L'état courant n'est jamais présenté comme l'état initial intact.

## Remédiations ordonnées

| Commit | Classe | Date déterministe | Sujet |
|---|---|---|---|
| `11dd43705915a24920e552af695de88998bad5f4` | `baseline_remediation` | 2026-07-26T14:13:20+01:00 | [CHARTE][V5.B-it2] ferme la baseline des onglets |
| `44904f4fcf75c5ca25b3af97d1390f3c28c9c647` | `baseline_remediation` | 2026-07-26T14:56:18+01:00 | [CHARTE][V5.B-it2] respecte la longueur mathematique |
| `91dd5c9304af567ff577a8211a41d20afbead097` | `baseline_remediation` | 2026-07-26T15:16:21+01:00 | [CHARTE][V5.B-it2] aligne le plan de validation |
| `16f6840fb47e15a7bba045e12965f5e4c4efb203` | `baseline_remediation` | 2026-07-26T15:46:58+01:00 | [CHARTE][V5.B-it2] unifie le rendu des onglets |
| `b8347890b57d7211cc22aedf0487483f8407a636` | `baseline_remediation` | 2026-07-26T16:03:05+01:00 | [CHARTE][V5.B-it2] enregistre la revue independante |
| `2386d4deb2d82d380a0d5bab3310b5ecc6cbe3f8` | `release_preflight` | 2026-07-26T16:15:52+01:00 | [1SPE][BAT] epingle la chaine de fabrication |
| `b4ed701e81f0ba03e558eee92b78f9bc61d54375` | `release_preflight` | 2026-07-26T16:37:05+01:00 | [1SPE][BAT] prouve le Tagged PDF |
| `02a130ea1b8c865ad8d5e453b06d27779b5ab39c` | `release_preflight` | 2026-07-26T17:04:50+01:00 | [1SPE][BAT] durcit le preflight de release |
| `d9ebe046ff7dda5e66b71758fc96efad08b938b3` | `release_preflight` | 2026-07-26T17:21:46+01:00 | [1SPE][BAT] isole le smoke Tagged PDF |
| `c698dfaac8879adcec7caf68c6848e02bff9fbcc` | `release_preflight` | 2026-07-26T17:47:44+01:00 | [1SPE][BAT] verrouille Java et les caches du smoke |
| `ca16edbb51d7f0122fcbbfea5cccfa7e2066cd63` | `release_preflight` | 2026-07-26T18:05:10+01:00 | [1SPE][BAT] securise les options Java du smoke |

## Inventaires

| Vue | Entrées | SHA-256 inventaire | Tags 1SPE |
|---|---:|---|---:|
| Origine | 3176 | `43d033a9a2857355ba4b4c6defd75feb24d224ad5c383a280783a64a62873bd4` | 13 |
| Courant | 3194 | `191b11571d8ad1aa282705cc465331635b633e7ab5758d26efe9443afb08a5dd` | 13 |

## Attestations

| Vue | Réutilisables | Périmées | Revue requise |
|---|---:|---:|---:|
| Origine | 0 | 0 | 1537 |
| Courant | 0 | 0 | 1552 |

Zéro chemin du périmètre non classé, zéro double classement et zéro pollution hors univers.
