# WORKTREE PROVENANCE AUDIT

Generated: 2026-08-15
Branch: audit/adversarial-reconciliation-2026

## 1. Git State & Lineage

| Parameter | Value |
| :--- | :--- |
| **Current Branch** | `audit/adversarial-reconciliation-2026` |
| **HEAD SHA** | `81f00693eb0f898886a158e41ed8891081194cf8` |
| **Merge Base with main** | `a21ff532750cebd156b4a77666f434c40ae9ee20` |
| **Commits Ahead of main** | `49` |
| **Commits Behind main** | `0` |
| **Upstream Remote** | `origin/integration/1spe-bo2026-traceability` (base branch origin) |
| **Worktree Status** | `DIRTY` (Uncommitted local modifications from Phase C forensic fix) |

## 2. Uncommitted Modified Files

- `Mathematiques/manuel-maths/build/maquette-v5/manifest.json`
- `Mathematiques/manuel-maths/build/maquette-v5/maquette.tex`
- `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/cours/13_C4_extremums.tex`
- `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/cours/14_C5_optimisation.tex`
- `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/cours/10_C1_taux_variation.tex`
- `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/cours/11_C2_nombre_derive.tex`
- `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/cours/12_C3_tangente.tex`
- `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/cours/13_C4_equation_tangente.tex`
- `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/cours/14_C5_approximation_lineaire.tex`
- `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/qcm/1SPE-DERIVATION-LOCAL-QCM.tex`
- `Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty`
- `Mathematiques/manuel-maths/scripts/check_maquette_v5.py`
- `Mathematiques/manuel-maths/scripts/pdf_integrity.py`
- `Mathematiques/manuel-maths/tests/test_maquette_v5.py`
- `Mathematiques/manuel-maths/transversal/mode_emploi.tex`
- `Mathematiques/manuel-maths/validations/v5-it2/page-13.png`
- `Mathematiques/manuel-maths/validations/v5/page-01.png` to `page-15.png`
- `NSI/gabarits/nexus-charte-v6.sty`
- `audit/V5_15_TO_16_ROOT_CAUSE.md` (Untracked)
- `scripts/analyze_v5_page_shift.py` (Untracked)
- `scripts/find_15_page_commit.py` (Untracked)
- `scripts/run_forensic_experiments.py` (Untracked)

## 3. Mission Phase Milestone SHAs

| Phase | SHA / Marker | Description |
| :--- | :--- | :--- |
| **Phase A SHA** | `ff0cdbdb` | Audit, registre des rôles, matrices de styles et rapports |
| **Phase B SHA** | `81f00693` | Tests de conformité des spécifications onglets (20/07/2026) |
| **Phase C SHA** | `81f00693` + local fixes | Investigation forensique 15→16 pages & résolution racine |
| **Root Cause Fix SHA** | Local WIP | Restauration QCM 4 colonnes, nxcaption backslashes & onglets 16mm |
