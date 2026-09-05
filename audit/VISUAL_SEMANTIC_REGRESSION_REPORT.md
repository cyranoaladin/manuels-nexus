# VISUAL_SEMANTIC_REGRESSION_REPORT — Contrôle de Régression Visuelle & Sémantique

- **Diffs Visuels Inattendus** : `UNEXPECTED_VISUAL_DIFF = 0`
- **Diffs Sémantiques Inexpliqués** : `UNEXPLAINED_SEMANTIC_DIFF = 0`
- **Verdict Global** : `REGRESSION_GATE = PASS`

## Modifications Délibérées Justifiées (EXPECTED_FIX)

### [EXPECTED_FIX] 1NSI_professeur (python_comments)
- **Description** : Preceded markdown file reference with comment marker (# readme.md) preventing Python syntax error in printed teacher listings
- **Fichiers impactés** : NSI/chapitres/1NSI-ARCHOS-CO-004.tex, NSI/chapitres/1NSI-ARCHOS-CO-011.tex, NSI/chapitres/1NSI-ARCHOS-CO-017.tex, NSI/chapitres/1NSI-ARCHOS-CO-023.tex, NSI/chapitres/1NSI-ARCHOS-CO-029.tex
- **Justifié** : OUI

### [EXPECTED_FIX] TSPE_2026_2027_eleve (student_separation_internal_id)
- **Description** : Replaced internal ID string 'TSPE-DERIVATION-CONVEXITE' in evaluation header with clean public chapter title 'Dérivation et convexité'
- **Fichiers impactés** : Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/evaluations/TSPE-DERIVATION-CONVEXITE-EV-A.tex, Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/evaluations/TSPE-DERIVATION-CONVEXITE-EV-B.tex
- **Justifié** : OUI

### [EXPECTED_REBUILD_NORMALIZATION] ALL_12_TARGETS (clean_reproducible_rebuild)
- **Description** : Deterministic compilation under controlled FORCE_SOURCE_DATE=1, TZ=UTC, LC_ALL=C.UTF-8, PYTHONHASHSEED=0
- **Fichiers impactés** : audit/BUILD_MANIFEST.json
- **Justifié** : OUI

