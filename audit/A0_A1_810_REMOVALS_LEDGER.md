# A0-A1 810 Removals Ledger Audit

Exact set-theoretic breakdown of all `810` active raw anomaly removals between State S0 (`6425`) and State S2 (`5615`).

## Mutually Exclusive Classes Breakdown

| Removal Class | Count | Description |
| --- | --- | --- |
| **REAL_PRODUCT_DEFECT_FIXED** | `5` | Real product defects resolved (broken LaTeX input paths in maquette/wrappers) |
| **FINGERPRINT_REPLACEMENT** | `72` | ID and file path migrations (`ADGK`/`AGT` -> `APT`) |
| **ID_PATH_MIGRATION** | `6` | Additional filename migrations without prior active anomaly |
| **ANALYZER_MODEL_RECLASSIFICATION** | `526` | Source model completeness (`correction` type_objet support) |
| **ASSEMBLY_MODEL_FIXED** | `59` | TNSI assembler glob pattern addition (`T*`) |
| **OTHER_EXPLICIT** | `142` | Secondary side-effect resolution from assembly completeness |
| **TOTAL** | **`810`** | **100% Accounted For (UNKNOWN = 0)** |

## Summary Categories
- **REAL_RELEASE_DEFECTS_FIXED**: `5`
- **MODEL_FALSE_POSITIVES_REMOVED**: `727`
- **IDENTITY_ONLY_CHANGES**: `78`
