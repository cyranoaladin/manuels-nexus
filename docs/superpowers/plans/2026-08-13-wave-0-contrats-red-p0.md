# Wave 0 — Contrats Red des P0 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ajouter, sans aucun correctif de production, trois familles de tests volontairement rouges qui contractualisent les fuites élève, les débordements Mathématiques et la provenance TSPE.

**Architecture:** Chaque famille combine une assertion unitaire sur le gate et une assertion sur les artefacts ou données suivis. Les commits restent séparés par lane ; les nouveaux échecs sont prouvés par leur message et distingués de la dette historique déjà présente.

**Tech Stack:** Python 3.12, Pytest 9, PyYAML, Poppler `pdftotext`, LuaLaTeX, Git.

**Spécification approuvée :** `docs/superpowers/specs/2026-08-13-wave-0-contrats-red-p0-design.md`

---

## Cartographie des fichiers

### Conception et plan

- Existing: `docs/superpowers/specs/2026-08-13-wave-0-contrats-red-p0-design.md`
- Create: `docs/superpowers/plans/2026-08-13-wave-0-contrats-red-p0.md`

### Famille 1 — séparation élève

- Modify: `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py`
  — contrat du filtre local Mathématiques.
- Modify: `tests/test_build_manifest.py`
  — contrat du filtre indépendant du recorder global.
- Create: `Mathematiques/manuel-maths/tests/test_p0_student_artifacts.py`
  — extraction déterministe des deux PDF élèves suivis.

### Famille 2 — débordements

- Modify: `Mathematiques/manuel-maths/tests/test_pdf_integrity.py`
  — contrat unitaire du préflight Mathématiques.
- Create: `Mathematiques/manuel-maths/tests/test_p0_overflow_artifact.py`
  — compilation réelle du master 1SPE élève en temporaire.

### Famille 3 — provenance TSPE

- Create: `tests/test_programme_registry.py`
  — cohérence du NOR entre registre canonique, manuel et table de sources.

### Fichiers interdits dans les commits de tests

- `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
- `Mathematiques/manuel-maths/scripts/pdf_integrity.py`
- `scripts/build_manifest.py`
- `docs/programmes/PROGRAMMES_2026_2027.yaml`
- `Mathematiques/manuel-maths/sources/SOURCES.md`
- tous les `.tex`, PDF, logs, manifests, baselines et dispositions

## État de départ et dette séparée

- Worktree : `.worktrees/wave0-p0-red-contracts`.
- Branche : `wave0/p0-red-contracts`.
- Base : `ff55af2e07a35c559802a536f92a7bb12a73b3e3`.
- Spécification : commit `dc1a1ed3`.
- Dette historique hors lot :
  `tests/test_build_manifest.py::test_versioned_build_producers_register_exact_1nsi_manual_surface`
  attend deux producteurs tandis que le registre courant en déclare six.

---

## Chunk 1: Préflight et plan versionné

### Task 1: Verrouiller le contexte d'exécution

**Files:**

- Read: `AGENTS.md`
- Read: `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md`
- Read: `audit/AUDIT_ETAT_PROJET_2026-08-13.md`
- Read: `docs/codex/QUALITY_GATES.md`
- Read: `docs/superpowers/specs/2026-08-13-wave-0-contrats-red-p0-design.md`

- [ ] **Step 1: Relever l'état Git obligatoire dans le worktree**

Run:

```bash
git status --short --branch
git rev-parse HEAD
git log --oneline --decorate -15
git diff --stat
git diff --check
```

Expected: branche `wave0/p0-red-contracts`, seulement le plan non suivi, aucun
WIP inattendu.

- [ ] **Step 2: Vérifier les outils contractuels**

Run:

```bash
python3 --version
python3 -m pytest --version
pdftotext -v
lualatex --version | head -1
```

Expected: les quatre commandes existent ; aucune absence n'est transformée en
skip.

- [ ] **Step 3: Vérifier les artefacts suivis**

Run:

```bash
git ls-files --error-unmatch \
  Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf
git ls-files --error-unmatch \
  Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf
```

Expected: deux chemins imprimés, code 0.

- [ ] **Step 4: Versionner le plan seul**

Run:

```bash
set -e
git add docs/superpowers/plans/2026-08-13-wave-0-contrats-red-p0.md
git diff --cached --check
git diff --cached --stat
git commit -m "[DOCS] planifie les contrats Red des P0 Wave 0"
git status --short --branch
```

Expected: un commit contenant uniquement le plan, puis arbre propre.

---

## Chunk 2: Contrat Red de séparation élève

### Task 2: Contractualiser les filtres de texte élève

**Files:**

- Modify: `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py`
- Modify: `tests/test_build_manifest.py`
- Test: les deux fichiers ci-dessus

- [ ] **Step 1: Ajouter les fixtures P0 au filtre Mathématiques**

Ajouter près des tests existants de `student_text_violations` :

```python
@pytest.mark.parametrize(
    ("texts", "expected"),
    [
        (("Correction et diagnostics", "CORRECTION ET DIAGNOSTICS"), "corrigé"),
        (("Réponses correctes", "Reponses correctes"), "corrigé"),
        (("Bareme : 6 points", "Barème : 6 points"), "barème enseignant"),
        (("Cle de correction", "clé de correction", "Clé de correction"), "corrigé"),
        (("TSPE-DERIVATION-CONVEXITE", "tspe-derivation-convexite"), "identifiant interne"),
        (("(renvois exercices M1)", "(RENVOIS EXERCICES M1)"), "renvoi provisoire"),
    ],
)
def test_p0_student_pdf_text_gate_rejects_observed_leaks(
    texts: tuple[str, ...],
    expected: str,
) -> None:
    missing = [
        text
        for text in texts
        if expected not in assemble_manuel.student_text_violations(text)
    ]
    assert not missing
```

Renforcer aussi le test existant
`test_student_pdf_text_gate_accepts_student_instructions` sans créer de cas
Pytest supplémentaire : évaluer les six phrases du recorder plus le texte
historique `Compléter le programme. Solution : x appartient à [0 ; 1].`,
collecter tous les faux positifs, puis exiger une collection vide. Ce contrat
est attendu rouge sur quatre consignes dans cette tranche.

- [ ] **Step 2: Vérifier le Red Mathématiques**

Run:

```bash
python3 -m pytest -q \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_p0_student_pdf_text_gate_rejects_observed_leaks
```

Expected: 6 échecs d'assertion ; les listes `missing` exposent toutes les
graphies non reconnues.

- [ ] **Step 3: Ajouter le même contrat au recorder global**

Ajouter près des tests existants de `_student_text_violations` :

```python
@pytest.mark.parametrize(
    ("texts", "expected"),
    [
        (("Correction et diagnostics", "CORRECTION ET DIAGNOSTICS"), "corrigé"),
        (("Réponses correctes", "Reponses correctes"), "corrigé"),
        (("Bareme : 6 points", "Barème : 6 points"), "barème enseignant"),
        (("Cle de correction", "clé de correction", "Clé de correction"), "corrigé"),
        (("TSPE-DERIVATION-CONVEXITE", "tspe-derivation-convexite"), "identifiant interne"),
        (("(renvois exercices M1)", "(RENVOIS EXERCICES M1)"), "renvoi provisoire"),
    ],
)
def test_p0_recorder_student_gate_rejects_observed_leaks(
    manifest_module,
    texts: tuple[str, ...],
    expected: str,
) -> None:
    missing = [
        text
        for text in texts
        if expected not in manifest_module._student_text_violations(text)
    ]
    assert not missing
```

- [ ] **Step 4: Vérifier le Red du recorder**

Run:

```bash
python3 -m pytest -q \
  tests/test_build_manifest.py::test_p0_recorder_student_gate_rejects_observed_leaks
```

Expected: 6 échecs d'assertion ; les listes `missing` exposent toutes les
graphies non reconnues.

### Task 3: Contractualiser les PDF élèves suivis

**Files:**

- Create: `Mathematiques/manuel-maths/tests/test_p0_student_artifacts.py`
- Test: ce fichier

- [ ] **Step 1: Créer l'extracteur strict et les deux assertions d'artefact**

Créer exactement cette structure :

```python
"""Contrats Red des fuites réellement présentes dans les PDF élèves suivis."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


MANUAL_ROOT = Path(__file__).resolve().parents[1]


def _student_pdf_text(relative_path: str) -> str:
    pdf = MANUAL_ROOT / relative_path
    assert pdf.is_file(), f"PDF élève suivi absent : {pdf}"
    completed = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        check=False,
        capture_output=True,
        text=True,
        errors="replace",
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip(), "extraction PDF élève vide"
    return completed.stdout


def test_p0_1spe_student_pdf_contains_no_teacher_pages_or_provisional_refs() -> None:
    text = _student_pdf_text("build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf")
    forbidden = [
        marker
        for marker in (
            "Correction et diagnostics",
            "Réponses correctes",
            "(renvois exercices M",
        )
        if marker in text
    ]
    assert not forbidden, f"fuites 1SPE élève détectées : {forbidden}"


def test_p0_tspe_student_pdf_contains_no_teacher_key_bareme_or_internal_id() -> None:
    text = _student_pdf_text(
        "build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf"
    )
    patterns = {
        "clé de correction": r"\bcl[eé]\s+de\s+correction\b",
        "barème enseignant": r"\bbar[èe]me\b",
        "identifiant interne": r"\bTSPE-[A-Z0-9]+(?:-[A-Z0-9]+)*\b",
    }
    found = [
        reason
        for reason, pattern in patterns.items()
        if re.search(pattern, text, re.IGNORECASE)
    ]
    assert not found, f"fuites TSPE élève détectées : {found}"
```

- [ ] **Step 2: Vérifier le Red des deux PDF**

Run:

```bash
python3 -m pytest -q \
  Mathematiques/manuel-maths/tests/test_p0_student_artifacts.py
```

Expected: 2 échecs ; le premier nomme correction/renvois, le second clé,
barème et identifiant.

- [ ] **Step 3: Vérifier la divergence des contre-exemples sans la corriger**

Run:

```bash
python3 -m pytest -q \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_student_pdf_text_gate_accepts_student_instructions \
  tests/test_build_manifest.py::test_recorder_student_text_gate_allows_correction_instructions
```

Expected: 1 échec Mathématiques listant les quatre faux positifs et 6 tests
recorder passés. Aucun regex de production n'est corrigé dans ce jalon.

- [ ] **Step 4: Faire les revues conformité puis qualité**

Dispatch un reviewer de spécification avec le diff non committé et la spec. Il
doit répondre `✅ Spec compliant` ou donner fichiers/lignes. Après approbation,
dispatch un autre reviewer de qualité qui contrôle précision des regex,
messages, déterminisme et absence de faux positifs. Toute correction est faite
par l'implémenteur puis revue de nouveau avant commit.

- [ ] **Step 5: Versionner le correctif documentaire issu du Red**

Run:

```bash
set -e
git add \
  docs/superpowers/specs/2026-08-13-wave-0-contrats-red-p0-design.md \
  docs/superpowers/plans/2026-08-13-wave-0-contrats-red-p0.md
git diff --cached --check
git diff --cached --stat
git commit -m "[DOCS] étend le contrat Red aux faux positifs élève"
```

Expected: seulement la spec et le plan ; le nouveau total de 20 Red et la
divergence Mathématiques/recorder sont versionnés avant les tests.

- [ ] **Step 6: Contrôler et committer seulement la famille élève**

Run:

```bash
set -e
git diff --check
git add \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  Mathematiques/manuel-maths/tests/test_p0_student_artifacts.py \
  tests/test_build_manifest.py
git diff --cached --check
git diff --cached --stat
git commit -m "[TESTS] caractérise les fuites de la variante élève"
```

Expected: uniquement trois fichiers de tests dans le commit.

---

## Chunk 3: Contrat Red des débordements

### Task 4: Faire refuser les diagnostics Overfull par contrat

**Files:**

- Modify: `Mathematiques/manuel-maths/tests/test_pdf_integrity.py`
- Test: ce fichier

- [ ] **Step 1: Ajouter le test unitaire paramétré**

Ajouter avant les tests LuaLaTeX réels :

```python
@pytest.mark.parametrize(
    "diagnostic",
    [
        "Overfull \\hbox (163.04901pt too wide)",
        "Overfull \\vbox (110.95308pt too high)",
    ],
)
def test_p0_math_pdf_preflight_rejects_overfull_diagnostics(
    tmp_path,
    diagnostic: str,
) -> None:
    import pdf_integrity

    pdf = tmp_path / "manual.pdf"
    log = tmp_path / "manual.log"
    pdf.write_bytes(b"%PDF fixture")
    log.write_text(diagnostic + "\n", encoding="utf-8")

    def runner(_command, **_kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout=(
                "name type emb sub uni object ID\n"
                "--------------------------------\n"
                "Fixture Type1 yes yes yes 1 0\n"
            ),
            stderr="",
        )

    assert pdf_integrity.verify_pdf(pdf, log, runner=runner) == 1
```

- [ ] **Step 2: Vérifier le Red unitaire**

Run:

```bash
python3 -m pytest -q \
  Mathematiques/manuel-maths/tests/test_pdf_integrity.py::test_p0_math_pdf_preflight_rejects_overfull_diagnostics
```

Expected: 2 échecs, valeur actuelle `0` au lieu de `1`.

### Task 5: Recompiler le vrai master et exiger zéro overflow

**Files:**

- Create: `Mathematiques/manuel-maths/tests/test_p0_overflow_artifact.py`
- Test: ce fichier

- [ ] **Step 1: Créer le test d'intégration sans skip**

Créer :

```python
"""Contrat Red des débordements produits par le master élève 1SPE réel."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


MANUAL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MANUAL_ROOT / "scripts"))

import assemble_manuel  # noqa: E402


def test_p0_real_1spe_student_master_produces_no_overfull(tmp_path) -> None:
    master = assemble_manuel.render_master("eleve", "0" * 32)
    tex_path = tmp_path / "MANUEL_1SPE_eleve.tex"
    tex_path.write_text(master, encoding="utf-8")
    environment = os.environ.copy()
    environment["TEXMFVAR"] = str(tmp_path / "texmf-var")
    command = [
        "lualatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={tmp_path}",
        str(tex_path),
    ]

    try:
        for pass_number in range(1, 4):
            completed = subprocess.run(
                command,
                cwd=MANUAL_ROOT,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
                errors="replace",
                timeout=300,
            )
            assert completed.returncode == 0, (
                f"LuaLaTeX passe {pass_number} en échec :\n"
                f"{completed.stdout[-3000:]}\n{completed.stderr[-3000:]}"
            )
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        pytest.fail(f"compilation contractuelle indisponible : {error}")

    log_path = tmp_path / "MANUEL_1SPE_eleve.log"
    assert log_path.is_file(), "journal contractuel absent"
    log = log_path.read_text(encoding="utf-8", errors="replace")
    counts = {
        "Overfull \\hbox": log.count("Overfull \\hbox"),
        "Overfull \\vbox": log.count("Overfull \\vbox"),
    }
    assert not any(counts.values()), f"débordements 1SPE élève : {counts}"
```

- [ ] **Step 2: Vérifier la compilation et le Red d'artefact**

Run:

```bash
python3 -m pytest -q -s \
  Mathematiques/manuel-maths/tests/test_p0_overflow_artifact.py
```

Expected: compilation réussie, puis 1 échec d'assertion avec des comptes
`Overfull` strictement positifs. Un échec de compilation impose de corriger la
fixture de test, pas les sources métier.

- [ ] **Step 3: Vérifier les tests historiques ciblés du préflight**

Run:

```bash
python3 -m pytest -q \
  Mathematiques/manuel-maths/tests/test_pdf_integrity.py \
  --ignore=Mathematiques/manuel-maths/tests/test_p0_overflow_artifact.py \
  -k 'not test_p0_math_pdf_preflight_rejects_overfull_diagnostics'
```

Expected: tests historiques du fichier passés.

- [ ] **Step 4: Faire les revues conformité puis qualité**

Faire relire le diff non committé par deux agents distincts, spécification
avant qualité. La revue qualité vérifie particulièrement : pas de skip,
sorties seulement en temporaire, trois passes, timeout borné et test du vrai
master. Toute correction précède le commit et repasse les deux revues utiles.

- [ ] **Step 5: Contrôler et committer seulement la famille overflow**

Run:

```bash
set -e
git diff --check
git add \
  Mathematiques/manuel-maths/tests/test_pdf_integrity.py \
  Mathematiques/manuel-maths/tests/test_p0_overflow_artifact.py
git diff --cached --check
git diff --cached --stat
git commit -m "[TESTS] caractérise les débordements du préflight mathématiques"
```

Expected: deux fichiers de tests seulement.

---

## Chunk 4: Contrat Red de provenance TSPE

### Task 6: Verrouiller le NOR officiel dans les deux sources locales

**Files:**

- Create: `tests/test_programme_registry.py`
- Test: ce fichier

- [ ] **Step 1: Créer les deux tests de provenance**

Créer :

```python
"""Contrats réglementaires minimaux de la collection 2026-2027."""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/programmes/PROGRAMMES_2026_2027.yaml"
MATH_SOURCES = ROOT / "Mathematiques/manuel-maths/sources/SOURCES.md"
CORRECT_TSPE_NOR = "MENE1921246A"
STMG_NOR = "MENE1921262A"


def test_p0_tspe_registry_uses_the_official_mathematics_nor() -> None:
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    source = registry["sources"]["SRC-BO2019-TSPE"]
    manual = next(
        item
        for item in registry["manuels"]
        if item["manual_id"] == "TSPE_2026_2027"
    )

    assert manual["programme_source"] == "SRC-BO2019-TSPE"
    assert source["arrete"] == CORRECT_TSPE_NOR
    assert source["arrete"] != STMG_NOR


def test_p0_tspe_sources_table_uses_the_official_mathematics_nor() -> None:
    lines = MATH_SOURCES.read_text(encoding="utf-8").splitlines()
    row = next(line for line in lines if "`BO2019_TSPE_specialite.pdf`" in line)

    assert CORRECT_TSPE_NOR in row
    assert STMG_NOR not in row
```

- [ ] **Step 2: Vérifier le Red réglementaire**

Run:

```bash
python3 -m pytest -q tests/test_programme_registry.py
```

Expected: 2 échecs ; les sorties montrent `MENE1921262A` présent et
`MENE1921246A` absent.

- [ ] **Step 3: Faire les revues conformité puis qualité**

Faire relire le diff non committé par deux agents distincts. La conformité
compare à la source officielle décidée ; la qualité vérifie chargement YAML
réel, sélection non ambiguë du manuel et test de la ligne exacte de
`SOURCES.md`. Toute correction est revue avant commit.

- [ ] **Step 4: Contrôler et committer seulement le contrat programme**

Run:

```bash
set -e
git diff --check
git add tests/test_programme_registry.py
git diff --cached --check
git diff --cached --stat
git commit -m "[TESTS] verrouille la provenance officielle TSPE"
```

Expected: un seul nouveau fichier de test.

---

## Chunk 5: Preuve consolidée du jalon Red

### Task 7: Prouver les nouveaux rouges sans masquer la dette historique

**Files:**

- Test: les six fichiers de tests modifiés ou créés
- Read: historique Git et spécification

- [ ] **Step 1: Collecter seulement les nouveaux contrats**

Run:

```bash
python3 -m pytest --collect-only -q \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_p0_student_pdf_text_gate_rejects_observed_leaks \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_student_pdf_text_gate_accepts_student_instructions \
  tests/test_build_manifest.py::test_p0_recorder_student_gate_rejects_observed_leaks \
  Mathematiques/manuel-maths/tests/test_p0_student_artifacts.py \
  Mathematiques/manuel-maths/tests/test_pdf_integrity.py::test_p0_math_pdf_preflight_rejects_overfull_diagnostics \
  Mathematiques/manuel-maths/tests/test_p0_overflow_artifact.py \
  tests/test_programme_registry.py
```

Expected: exactement 20 tests collectés : 15 séparation, 3 overflow,
2 programme.

- [ ] **Step 2: Exécuter les contrats rapides et relever leur matrice Red**

Run:

```bash
set +e
python3 -m pytest -q \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_p0_student_pdf_text_gate_rejects_observed_leaks \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py::test_student_pdf_text_gate_accepts_student_instructions \
  tests/test_build_manifest.py::test_p0_recorder_student_gate_rejects_observed_leaks \
  Mathematiques/manuel-maths/tests/test_p0_student_artifacts.py \
  Mathematiques/manuel-maths/tests/test_pdf_integrity.py::test_p0_math_pdf_preflight_rejects_overfull_diagnostics \
  tests/test_programme_registry.py
quick_status=$?
set -e
test "$quick_status" -ne 0
```

Expected: 19 échecs contractuels, code Pytest non nul conservé et vérifié.

- [ ] **Step 3: Exécuter séparément le contrat de compilation**

Run:

```bash
set +e
python3 -m pytest -q -s \
  Mathematiques/manuel-maths/tests/test_p0_overflow_artifact.py
overflow_status=$?
set -e
test "$overflow_status" -ne 0
```

Expected: 1 échec contractuel après trois passes réussies.

- [ ] **Step 4: Rejouer les contre-exemples historiques verts**

Run:

```bash
python3 -m pytest -q \
  tests/test_build_manifest.py::test_recorder_student_text_gate_allows_correction_instructions \
  Mathematiques/manuel-maths/tests/test_pdf_integrity.py \
  -k 'not test_p0_math_pdf_preflight_rejects_overfull_diagnostics'
```

Expected: les 6 contre-exemples du recorder et les tests historiques du
préflight passent. Le contre-exemple Mathématiques est désormais un Red
contractuel et n'est pas masqué dans cette commande.

- [ ] **Step 5: Reproduire la dette historique séparément**

Run:

```bash
set +e
python3 -m pytest -q \
  tests/test_build_manifest.py::test_versioned_build_producers_register_exact_1nsi_manual_surface
legacy_status=$?
set -e
test "$legacy_status" -ne 0
```

Expected: un échec sur 2 producteurs attendus contre 6 réels, sans mélange avec
les 20 contrats Red.

- [ ] **Step 6: Vérifier qu'aucun test n'est neutralisé**

Run:

```bash
python3 - <<'PY'
from __future__ import annotations

import re
import subprocess

paths = (
    "Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py",
    "Mathematiques/manuel-maths/tests/test_p0_student_artifacts.py",
    "tests/test_build_manifest.py",
    "Mathematiques/manuel-maths/tests/test_pdf_integrity.py",
    "Mathematiques/manuel-maths/tests/test_p0_overflow_artifact.py",
    "tests/test_programme_registry.py",
)
diff = subprocess.run(
    ["git", "diff", "ff55af2e..HEAD", "--unified=0", "--", *paths],
    check=True,
    capture_output=True,
    text=True,
).stdout
added = "\n".join(
    line[1:]
    for line in diff.splitlines()
    if line.startswith("+") and not line.startswith("+++")
)
pattern = r"pytest\.mark\.(?:skip|skipif|xfail)|pytest\.(?:skip|xfail)"
assert re.search(pattern, added) is None, added
PY
```

Expected: code 0 ; aucune ligne ajoutée dans les six fichiers ne neutralise un
test. Les marqueurs historiques non ajoutés ne créent pas de faux positif.

- [ ] **Step 7: Vérifier le périmètre des sept commits du jalon**

Run:

```bash
git diff --check
git status --short --branch
git diff ff55af2e..HEAD --name-only
git log --oneline --decorate ff55af2e..HEAD
```

Expected: deux documents et six fichiers de tests seulement ; sept commits
atomiques (dont deux correctifs documentaires), arbre propre.

- [ ] **Step 8: Faire la revue finale du jalon**

Dispatch un reviewer final en lecture seule avec la spec, le plan, les sept
commits et les sorties Red. Il doit confirmer : 20 tests contractuels, échecs pour
les bonnes raisons, zéro production modifiée, dette historique séparée et
aucun gate affaibli.

- [ ] **Step 9: Relever les gates sans prétendre au vert**

Run dans le checkout d'intégration principal, dont la branche correspond à la
provenance versionnée du manifeste :

```bash
integration_checkout=$(
  python3 - <<'PY'
import subprocess

lines = subprocess.run(
    ["git", "worktree", "list", "--porcelain"],
    check=True,
    capture_output=True,
    text=True,
).stdout.splitlines()
path = None
for line in lines:
    if line.startswith("worktree "):
        path = line.removeprefix("worktree ")
    elif line == "branch refs/heads/integration/1spe-bo2026-traceability":
        assert path is not None
        print(path)
        break
PY
)
test -n "$integration_checkout"
git -C "$integration_checkout" status --short --branch
(cd "$integration_checkout" && \
  python3 scripts/inventory_collection.py --check --require-clean)
set +e
(cd "$integration_checkout" && \
  python3 scripts/inventory_collection.py --check --release-strict --require-clean)
release_status=$?
set -e
test "$release_status" -eq 7
```

Expected: structure verte, release toujours rouge code 7. Les tests Red ne
modifient ni inventaire ni baseline.

Puis relever la contrainte de provenance propre au worktree :

```bash
set +e
worktree_output=$(python3 scripts/inventory_collection.py --check --require-clean 2>&1)
worktree_status=$?
set -e
test "$worktree_status" -eq 3
printf '%s\n' "$worktree_output" | python3 -c '
import json
import sys

payload = json.loads(sys.stdin.read().splitlines()[-1])
assert payload["gate"] == "check"
assert payload["exit_code"] == 3
assert payload["reasons"] == [
    "check_error:branche de provenance du manifeste incohérente"
]
'
```

Expected: code 3 avec pour unique cause la branche du worktree différente de
la branche attestée par `audit/BUILD_MANIFEST.json`. Ne jamais réécrire le
manifeste pour rendre ce contrôle vert.

## Définition de terminé

Le jalon est terminé seulement si :

- spécification et plan sont approuvés et versionnés ;
- exactement 20 cas Pytest contractuels sont collectés ;
- 20 cas échouent sur les symptômes P0 attendus ;
- les six contre-exemples du recorder restent verts et la divergence du filtre
  Mathématiques reste rouge ;
- la dette des producteurs est reproduite et rapportée séparément ;
- aucun test n'est `skip`, `xfail` ou soustrait à la collecte ;
- aucun fichier de production, contenu, PDF, registre ou baseline n'a changé ;
- les trois familles de tests ont leurs commits atomiques et leurs deux revues ;
- l'arbre final du worktree est propre ;
- le checkout d'intégration attesté garde le gate structurel vert et
  `--release-strict` rouge code 7 ;
- le worktree rapporte séparément le code 3 de provenance de branche, sans
  modification du manifeste.
