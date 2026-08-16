# Severity Reassessment Audit

Detailed risk assessment and severity classification of active anomalies.

**KNOWN_MINIMUM_P0**: `15` (`5` broken LaTeX references + `10` LaTeX cycles)

## Severity Definition & Distribution

| Level | Definition | Categories | Active Count |
| --- | --- | --- | --- |
| **P0** | Rupture critique de compilation LaTeX ou cycle circulaire empêchant le build | `broken_latex_references`, `latex_cycles` | **15** |
| **P1** | Rupture de graphe META, collision d'identifiant ou désalignement de contexte | `broken_meta_references`, `duplicate_assembly_objects`, `context_mismatches` | **2809** |
| **P2** | Absence de corrigé, objet non assemblé ou statut non validé pour publication | `blocking_statuses`, `unassembled_objects`, `missing_corrections` | **2907** |
| **P3** | Type non classifié, PDF non attribué ou fichier orphelin | `unclassified_types`, `unattributed_pdfs`, `orphan_files` | **694** |

**Total Reassessed Active**: `6425`
