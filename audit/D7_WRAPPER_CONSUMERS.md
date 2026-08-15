# AUDIT D7 — MAP DES WRAPPERS & CONSUMERS

## 1. Map des Wrappers Compatibilité

### Wrapper 1 : `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls`
- **wrapper_path**: `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls`
- **canonical_target**: `gabarits/common/nexus-manuel.cls`
- **all_static_consumers**:
  - `Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls`
  - `Mathematiques/manuel-maths/build/maquette-v5/maquette.tex`
  - `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
  - `Mathematiques/manuel-maths/tests/test_maquette_v5.py`
- **all_runtime_consumers**:
  - `Mathematiques/manuel-maths/build/maquette-v5/maquette.pdf`
  - Builds d'assemblage local Mathématiques Première Spécialité
- **producer**: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
- **manual**: `1SPE`, `TSPE_2026_2027`, `TCOMPL`, `TEXPERTES`
- **variant**: `élève`, `pro`
- **loaded_in_fls**: `Yes` (redirection transparente vers `gabarits/common/nexus-manuel.cls`)
- **reason_temporarily_required**: Préservation de la résolution relative des chemins LaTeX dans les scripts d'assemblage et tests locaux du sous-dossier Mathématiques.
- **planned_removal**: **Phase D15** (Release finale)

---

### Wrapper 2 : `Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty`
- **wrapper_path**: `Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty`
- **canonical_target**: `gabarits/common/nexus-charte.sty`
- **all_static_consumers**:
  - `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
  - `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py`
  - `Mathematiques/manuel-maths/gabarits/specimen-v6.tex`
  - `Mathematiques/manuel-maths/gabarits/specimen-pont-v6.tex`
- **all_runtime_consumers**:
  - Compilations de chapitres Mathématiques Première et Terminale
- **producer**: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
- **manual**: `1SPE`, `TSPE_2026_2027`, `TCOMPL`, `TEXPERTES`
- **variant**: `élève`, `pro`
- **loaded_in_fls**: `Yes` (redirection transparente vers `gabarits/common/nexus-charte.sty`)
- **reason_temporarily_required**: Compatibilité avec le nom d'extension legacy `nexus-charte-v6` utilisé dans certains gabarits de la branche Mathématiques.
- **planned_removal**: **Phase D15** (Release finale)

---

### Wrapper 3 : `NSI/gabarits/nexus-manuel.cls`
- **wrapper_path**: `NSI/gabarits/nexus-manuel.cls`
- **canonical_target**: `gabarits/common/nexus-manuel.cls`
- **all_static_consumers**:
  - `NSI/gabarits/book_master.tex`
  - `NSI/scripts/assemble.py`
  - `NSI/tests/test_assemble_book.py`
  - `NSI/build/test_prof.tex`
- **all_runtime_consumers**:
  - Compilations masters NSI (`MANUEL_1NSI_eleve.pdf`, `MANUEL_TNSI_professeur.pdf`)
- **producer**: `NSI/scripts/assemble.py`
- **manual**: `1NSI`, `TNSI`
- **variant**: `élève`, `pro`
- **loaded_in_fls**: `Yes` (redirection transparente vers `gabarits/common/nexus-manuel.cls`)
- **reason_temporarily_required**: Prise en charge des compilations NSI exécutées depuis le répertoire `NSI/`.
- **planned_removal**: **Phase D15** (Release finale)

---

### Wrapper 4 : `NSI/gabarits/nexus-charte-v6.sty`
- **wrapper_path**: `NSI/gabarits/nexus-charte-v6.sty`
- **canonical_target**: `gabarits/common/nexus-charte.sty`
- **all_static_consumers**:
  - `NSI/gabarits/book_master.tex`
  - `NSI/scripts/assemble.py`
  - `NSI/tests/test_assemble_book.py`
  - `NSI/build/MANUEL_TNSI/MANUEL_TNSI_professeur.tex`
- **all_runtime_consumers**:
  - Compilations de chapitres NSI
- **producer**: `NSI/scripts/assemble.py`
- **manual**: `1NSI`, `TNSI`
- **variant**: `élève`, `pro`
- **loaded_in_fls**: `Yes` (redirection transparente vers `gabarits/common/nexus-charte.sty`)
- **reason_temporarily_required**: Compatibilité avec le nom d'extension legacy dans la suite d'assemblage NSI.
- **planned_removal**: **Phase D15** (Release finale)

---

## 2. Verdict Explicite

```text
NON_PILOT_MANUALS_ALREADY_AFFECTED_BY_COMMON_ENGINE = YES
```

### Manuels concernés :
1. `TSPE_2026_2027` (Mathématiques Terminale Spécialité)
2. `TCOMPL` (Mathématiques Terminale Complémentaires)
3. `TEXPERTES` (Mathématiques Terminale Expertes)
4. `1NSI` (Numérique et Sciences Informatiques Première)
5. `TNSI` (Numérique et Sciences Informatiques Terminale)

### Justification de la Phase D8 = NOT_STARTED :
Grâce aux redirections wrappers v6.0 scellées en D0-D6, toute modification apportée à `gabarits/common/` s'applique déjà immédiatement à l'ensemble des 6 manuels.

Cependant, la **Phase D8 (Généralisation et validation formelle des 5 manuels non-pilotes)** exige le passage réussi des 12 builds complets (élève + pro pour les 6 manuels), le contrôle strict des invariants de diffusion (absence totale de corrigés ou barèmes en version élève), et le franchissement des gates de release sur chaque discipline. Tant que cette attestation formelle 12/12 n'a pas été exécutée sous le protocole D8, **D8 est considéré stricto sensu comme non commencé (NOT_STARTED)**.
