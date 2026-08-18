# A0-A2 Anomaly State Transition Ledger

Detailed state transition metrics across Phase A0 (Model Completeness), Phase A1 (Governance & Wrapper Canonicalization), and Phase A2 (LaTeX SCC Cycle Remediation).

## Anomaly Metric Transitions

| Metric | S0 Baseline | S1 Post-A0 | S2 Post-A1 | S3 Post-A2 |
| --- | --- | --- | --- | --- |
| **TOTAL_RAW_ANOMALIES** | `6425` | `5630` | `5615` | `5615` |
| **TOTAL_RELEASE_BLOCKING** | `6425` | `5630` | `5615` | `5615` |
| **TOTAL_P0** | `15` | `15` | `0` | **`0`** |
| **broken_latex** | `5` | `5` | `0` | **`0`** |
| **latex_cycles** | `10` | `10` | `0` | **`0`** |
| **A1_SCOPED_REAL_DEFECTS** | `5` | `5` | `0` | **`0`** |

## Key Milestones

- **Phase A0**: Resolved 795 false positives & identity migrations.
- **Phase A1**: Resolved 15 anomalies (5 real `broken_latex` defects + 2 broken meta side effects + 8 secondary metadata disappearances). `broken_latex` = 0. La suppression du fallback auto-référentiel `\input{nexus-manuel.cls}` dans les 2 wrappers (commit `fed6d28a`) a également résolu les 10 `latex_cycles` — d'où `latex_cycles = 0` dans toute analyse fraîche dès S2.
- **Phase A2**: Lot de vérification et documentation (aucun changement de source LaTeX). Confirme `latex_cycles` = 0 et `P0` = 0 par reproduction hermétique.

> Correction de provenance (2026-08-18) : S3 affichait `RAW 5605` par double
> soustraction arithmétique des 10 cycles. Valeur reproduite hermétiquement à
> `9ddcffee` (deux worktrees frais, artefacts byte-identiques) : **5615**.
> Voir `audit/PROVENANCE_CORRECTION_1361cf37.md`.
