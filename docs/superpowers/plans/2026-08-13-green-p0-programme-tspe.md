# Green P0 Programme TSPE Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corriger la provenance réglementaire active du manuel TSPE vers le programme de mathématiques `MENE1921246A`, en conservant la preuve officielle suivie, les historiques et les autres lots Wave 0 intacts.

**Architecture:** Une branche indépendante part de la pointe propre de `wave0/p0-green-launch`, capturée dynamiquement seulement après le versionnement des trois plans Green et de leurs spécifications. Un unique fichier de tests porte le contrat réglementaire complet et les mutations adversariales ; le correctif Green reste un remplacement ciblé dans le registre, la table de sources, trois contextes actifs et les deux passages obsolètes du README.

**Tech Stack:** Git worktrees, Python 3, Pytest, PyYAML, SHA-256, Markdown, YAML.

---

## Périmètre et carte des fichiers

Spécification faisant autorité :
`docs/superpowers/specs/2026-08-13-green-p0-programme-tspe-design.md`.

Fichiers autorisés dans le diff de la branche Green :

- Modify: `tests/test_programme_registry.py` — contrat machine du NOR, de
  l'URL, du BO, de la source suivie, des documents actifs et du README ;
- Modify: `docs/programmes/PROGRAMMES_2026_2027.yaml` — source canonique
  `SRC-BO2019-TSPE` ;
- Modify: `Mathematiques/manuel-maths/sources/SOURCES.md` — ligne de preuve
  `BO2019_TSPE_specialite.pdf` ;
- Modify: `Mathematiques/manuel-maths/docs/10_perimetre_terminale.md` —
  référence du périmètre TSPE ;
- Modify: `ROADMAP_TERMINALE.md` — ligne TSPE de la roadmap ;
- Modify: `Mathematiques/manuel-maths/scripts/assemble_manuel.py` — commentaire
  réglementaire TSPE uniquement ;
- Modify: `README.md` — état courant du registre et liste des P0 ouverts.

Tous les fichiers sous `audit/`, les extraits officiels, PDF, contrats,
chapitres, manifests observés et baselines sont hors périmètre. Le PDF local
ignoré `Mathematiques/manuel-maths/sources/BO2019_TSPE_specialite.pdf` est une
preuve externe complémentaire : son absence d'un clone ou du worktree n'est
ni réparée ni contournée.

Dans toutes les étapes ci-dessous, chaque commande `Run` fixe explicitement son
worktree par un chemin absolu avant d'agir. Chaque instruction `apply_patch`
s'exécute avec le workdir
`/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe`
et cible exclusivement les chemins relatifs nommés dans l'étape.

## Conditions d'arrêt

- Arrêter si `wave0/p0-green-launch` n'est pas propre, si sa pointe n'est pas
  capturable sans ambiguïté ou si elle ne contient pas les trois plans Green
  et leurs quatre spécifications applicables.
- Arrêter si la branche ou le worktree cible existe déjà sans provenance
  explicitement vérifiée ; ne jamais le supprimer, le nettoyer ou l'écraser.
- Arrêter si l'extrait suivi ne porte plus le SHA-256
  `65eb5a55df14a2b3025a96db72fbcb1d917b55e8da7feb13669e28b903712210`.
- Arrêter si une source officielle applicable contredit `MENE1921246A`, le BO
  spécial n° 8 du 25 juillet 2019 ou l'application à la rentrée 2020.
- Ne pas remplacer la source officielle par une source secondaire si l'URL
  officielle répond encore HTTP 403.
- Arrêter si un fichier étranger aux sept chemins autorisés entre dans le diff.
- Arrêter si un gate exige une réécriture d'audit, de manifeste ou de baseline.
- Le statut de publication reste **NO-GO** ; ce lot ne prétend pas résoudre les
  autres P0 ni les 67 bloqueurs `release-strict`.

## Chunk 1: Isoler le lot et étendre le contrat Red

### Task 1: Créer la branche et le worktree dédiés

**Files:**
- Read: `AGENTS.md`
- Read: `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md`
- Read: `audit/AUDIT_ETAT_PROJET_2026-08-13.md`
- Read: `docs/codex/QUALITY_GATES.md`
- Read: `docs/codex/CI_AUDIT_PHASE_0.md`
- Read: `docs/superpowers/specs/2026-08-13-wave-0-green-p0-launch-design.md`
- Read: `docs/superpowers/specs/2026-08-13-green-p0-programme-tspe-design.md`
- Verify tracked: `docs/superpowers/specs/2026-08-13-green-p0-overflow-preflight-design.md`
- Verify tracked: `docs/superpowers/specs/2026-08-13-green-p0-separation-eleve-design.md`
- Verify tracked: `docs/superpowers/plans/2026-08-13-green-p0-overflow-preflight.md`
- Verify tracked: `docs/superpowers/plans/2026-08-13-green-p0-programme-tspe.md`
- Verify tracked: `docs/superpowers/plans/2026-08-13-green-p0-separation-eleve.md`

- [ ] **Step 1: Contrôler le dépôt et les worktrees sans rien modifier**

Run depuis `/home/alaeddine/Documents/Manuels_Nexus` :

```bash
set -euo pipefail
repo=/home/alaeddine/Documents/Manuels_Nexus
launch=$repo/.worktrees/wave0-p0-green-launch
target=$repo/.worktrees/green-p0-programme-tspe
cd "$launch"

git -C "$repo" status --short --branch
git -C "$launch" status --short --branch
git -C "$launch" rev-parse HEAD
git -C "$launch" log --oneline --decorate -15
git -C "$launch" diff --stat
git -C "$launch" diff --check
git -C "$repo" worktree list --porcelain
git -C "$repo" branch --list green/p0-programme-tspe
test "$(git -C "$launch" symbolic-ref --short HEAD)" = \
  wave0/p0-green-launch
test -z "$(git -C "$launch" status --porcelain)"
base=$(git -C "$launch" rev-parse HEAD)
for path in \
  docs/superpowers/plans/2026-08-13-green-p0-overflow-preflight.md \
  docs/superpowers/plans/2026-08-13-green-p0-programme-tspe.md \
  docs/superpowers/plans/2026-08-13-green-p0-separation-eleve.md \
  docs/superpowers/specs/2026-08-13-wave-0-green-p0-launch-design.md \
  docs/superpowers/specs/2026-08-13-green-p0-overflow-preflight-design.md \
  docs/superpowers/specs/2026-08-13-green-p0-programme-tspe-design.md \
  docs/superpowers/specs/2026-08-13-green-p0-separation-eleve-design.md
do
  git -C "$launch" cat-file -e "$base:$path"
done
printf '%s\n' "$base"
test ! -e "$target"
test -z "$(git -C "$repo" branch --list green/p0-programme-tspe)"
```

Expected: le worktree de lancement est propre sur `wave0/p0-green-launch` ; la
pointe affichée contient les trois plans versionnés et les quatre
spécifications ; le chemin et la branche Green n'existent pas. Aucun plan non
suivi ne subsiste au moment de capturer la base.

- [ ] **Step 2: Créer le worktree depuis la pointe propre capturée**

Run :

```bash
set -euo pipefail
repo=/home/alaeddine/Documents/Manuels_Nexus
launch=$repo/.worktrees/wave0-p0-green-launch
target=$repo/.worktrees/green-p0-programme-tspe
cd "$launch"
test -z "$(git -C "$launch" status --porcelain)"
base=$(git -C "$launch" rev-parse HEAD)
git -C "$repo" worktree add \
  -b green/p0-programme-tspe \
  "$target" \
  "$base"
cd "$target"
git -C "$target" status --short --branch
test "$(git -C "$target" rev-parse HEAD)" = "$base"
test -z "$(git -C "$target" status --porcelain)"
```

Expected: branche `green/p0-programme-tspe`, arbre propre, HEAD exactement égal
à la pointe propre de lancement observée dans la commande.

- [ ] **Step 3: Relire les instructions et les deux spécifications du lot**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
cat AGENTS.md
cat docs/superpowers/specs/2026-08-13-wave-0-green-p0-launch-design.md
cat docs/superpowers/specs/2026-08-13-green-p0-programme-tspe-design.md
python3 - <<'PY'
from pathlib import Path

text = Path(
    "docs/superpowers/specs/2026-08-13-green-p0-programme-tspe-design.md"
).read_text(encoding="utf-8")
for expected in (
    "MENE1921246A",
    "https://www.education.gouv.fr/bo/19/Special8/MENE1921246A.htm",
    "application : rentrée 2020, encore applicable à l'édition 2026-2027",
    "eb8369e7c1611e90f51491fecc5a7c2081a9c57f9c7fbb08d0414677b56ce16f",
    "65eb5a55df14a2b3025a96db72fbcb1d917b55e8da7feb13669e28b903712210",
):
    assert expected in text, expected
print("programme spec authority: OK")
PY
```

Expected: `programme spec authority: OK` ; NOR, URL, application et les deux
empreintes sont explicites ; aucun PDF ou audit n'est à modifier et la
publication reste NO-GO.

- [ ] **Step 4: Relire l'audit daté sans le réinterpréter comme état futur**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
cat audit/AUDIT_ETAT_PROJET_2026-08-13.md
python3 - <<'PY'
from pathlib import Path

text = Path("audit/AUDIT_ETAT_PROJET_2026-08-13.md").read_text(encoding="utf-8")
assert "`MENE1921246A`" in text
assert "https://www.education.gouv.fr/bo/19/Special8/MENE1921246A.htm" in text
assert "### 4. Référence officielle TSPE erronée" in text
assert "`MENE1921262A`" in text
print("dated audit evidence: OK")
PY
```

Expected: `dated audit evidence: OK`. L'audit prouve l'erreur historique et la
bonne référence, mais demeure hors périmètre du correctif.

- [ ] **Step 5: Lire le premier tiers du cahier des charges**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
sed -n '1,400p' CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md
```

Expected: autorité des textes officiels, traçabilité des sources et exigences
de conformité lues ; aucune modification.

- [ ] **Step 6: Lire le deuxième tiers du cahier des charges**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
sed -n '401,800p' CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md
```

Expected: contrats pédagogiques, scientifiques et de variantes lus ; aucune
extension du périmètre Programme.

- [ ] **Step 7: Lire la fin du cahier des charges**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
sed -n '801,1141p' CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md
```

Expected: gates, validation et gouvernance de publication lus ; le lot reste
NO-GO et ne réécrit aucun artefact observé.

- [ ] **Step 8: Lire la grille des gates et borner la fermeture du lot**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
sed -n '1,138p' docs/codex/QUALITY_GATES.md
python3 - <<'PY'
from pathlib import Path

text = Path("docs/codex/QUALITY_GATES.md").read_text(encoding="utf-8")
assert "## Gate G3 — Programme" in text
assert "matrice officielle complète" in text
assert "validation humaine" in text
assert "## Gate G10 — Release" in text
assert "`--validate-model` vert" in text
assert "`--fail-on-new` vert" in text
assert "`--release-strict` vert" in text
print("G3/G10 contracts: read")
PY
```

Expected: `G3/G10 contracts: read`. Ce lot ferme seulement le P0 de provenance
TSPE. Il ne ferme ni le gate Programme G3 complet ni le gate Release G10, qui
restent rouges jusqu'à satisfaction de toutes leurs cases et validations.

- [ ] **Step 9: Lire le contrat CI et conserver ses dettes explicites**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
sed -n '1,56p' docs/codex/CI_AUDIT_PHASE_0.md
python3 - <<'PY'
from pathlib import Path

text = Path("docs/codex/CI_AUDIT_PHASE_0.md").read_text(encoding="utf-8")
assert "`--release-strict` avec un code exactement égal à 7" in text
assert "La CI n’appelle jamais `--update-baseline`" in text
assert "ne vaut ni acceptation scientifique" in text
print("phase-0 CI debt: read")
PY
```

Expected: `phase-0 CI debt: read`. Le correctif de provenance ne revendique
aucune acceptation scientifique, éditoriale ou de publication et ne change pas
le contrat rouge contrôlé de `release-strict`.

### Task 2: Prouver le Red existant et l'archive officielle suivie

**Files:**
- Test: `tests/test_programme_registry.py`
- Read: `Mathematiques/manuel-maths/sources/txt/BO2019_TSPE_specialite.txt`

- [ ] **Step 1: Rejouer les deux contrats Red approuvés**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
python3 -m pytest tests/test_programme_registry.py -q
```

Expected: `2 failed`; l'un affiche `MENE1921262A != MENE1921246A`, l'autre
montre la même attribution STMG dans la ligne `BO2019_TSPE_specialite.pdf`.

- [ ] **Step 2: Vérifier que la preuve reproductible est suivie et intacte**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
source_txt=Mathematiques/manuel-maths/sources/txt/BO2019_TSPE_specialite.txt
git ls-files --error-unmatch "$source_txt"
test "$(sha256sum "$source_txt" | cut -d' ' -f1)" = \
  65eb5a55df14a2b3025a96db72fbcb1d917b55e8da7feb13669e28b903712210
```

Expected: le chemin est suivi par Git et son empreinte est exacte. Ne pas
copier le PDF ignoré dans le worktree et ne pas télécharger de substitut.

### Task 3: Étendre le contrat réglementaire avant la correction

**Files:**
- Modify: `tests/test_programme_registry.py`

- [ ] **Step 1: Remplacer le test minimal par le contrat complet**

Depuis le worktree cible absolu défini dans le préambule, appliquer ce contenu
exclusivement à `tests/test_programme_registry.py` avec `apply_patch` :

```python
"""Contrats réglementaires minimaux de la collection 2026-2027."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/programmes/PROGRAMMES_2026_2027.yaml"
MATH_SOURCES = ROOT / "Mathematiques/manuel-maths/sources/SOURCES.md"
TSPE_TEXT = (
    ROOT
    / "Mathematiques/manuel-maths/sources/txt/BO2019_TSPE_specialite.txt"
)
PERIMETER = ROOT / "Mathematiques/manuel-maths/docs/10_perimetre_terminale.md"
ROADMAP = ROOT / "ROADMAP_TERMINALE.md"
ASSEMBLER = ROOT / "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
README = ROOT / "README.md"

CORRECT_TSPE_NOR = "MENE1921246A"
STMG_NOR = "MENE1921262A"
TNSI_NOR = "MENE1921247A"
CORRECT_TSPE_BO = "BO spécial n° 8 du 25 juillet 2019"
CORRECT_TSPE_URL = (
    "https://www.education.gouv.fr/bo/19/Special8/MENE1921246A.htm"
)
CORRECT_TSPE_TEXT_PATH = (
    "Mathematiques/manuel-maths/sources/txt/BO2019_TSPE_specialite.txt"
)
CORRECT_TSPE_TEXT_SHA256 = (
    "65eb5a55df14a2b3025a96db72fbcb1d917b55e8da7feb13669e28b903712210"
)
CORRECT_PROGRAMME_VERSION = "2019"
CORRECT_APPLICATION_DATE = "2020-09-01"
CORRECT_SOURCES_BO = "BO special n 8 du 25-07-2019"
CORRECT_SOURCES_APPLICATION = "Rentree 2020"
CORRECT_TSPE_PDF_SHA256 = (
    "eb8369e7c1611e90f51491fecc5a7c2081a9c57f9c7fbb08d0414677b56ce16f"
)


def _assert_official_tspe_source(source: dict[str, object]) -> None:
    assert source["reference_bo"] == CORRECT_TSPE_BO
    assert source["arrete"] == CORRECT_TSPE_NOR
    assert source["url"] == CORRECT_TSPE_URL
    assert source["fichier"] == CORRECT_TSPE_TEXT_PATH
    assert source["sha256"] == CORRECT_TSPE_TEXT_SHA256


def test_p0_tspe_registry_uses_the_complete_official_reference() -> None:
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    source = registry["sources"]["SRC-BO2019-TSPE"]
    manuals = [
        item
        for item in registry["manuels"]
        if item["manual_id"] == "TSPE_2026_2027"
    ]

    assert len(manuals) == 1
    assert manuals[0]["programme_source"] == "SRC-BO2019-TSPE"
    assert manuals[0]["programme_version"] == CORRECT_PROGRAMME_VERSION
    assert manuals[0]["date_application"] == CORRECT_APPLICATION_DATE
    _assert_official_tspe_source(source)


def test_p0_tspe_sources_table_uses_the_official_mathematics_nor() -> None:
    lines = MATH_SOURCES.read_text(encoding="utf-8").splitlines()
    rows = [
        line for line in lines if "`BO2019_TSPE_specialite.pdf`" in line
    ]

    assert len(rows) == 1
    row = rows[0]
    cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
    assert cells == [
        "`BO2019_TSPE_specialite.pdf`",
        CORRECT_TSPE_NOR,
        CORRECT_SOURCES_BO,
        CORRECT_SOURCES_APPLICATION,
        f"`{CORRECT_TSPE_PDF_SHA256}`",
    ]


def test_p0_tspe_tracked_extract_keeps_the_archived_digest() -> None:
    assert TSPE_TEXT.is_file()
    digest = hashlib.sha256(TSPE_TEXT.read_bytes()).hexdigest()
    assert digest == CORRECT_TSPE_TEXT_SHA256


def test_p0_tspe_active_documents_use_the_mathematics_nor() -> None:
    expectations = (
        (
            ROADMAP,
            "Maths specialite Terminale (TSPE) | 2019, arrete MENE1921246A",
            "Maths specialite Terminale (TSPE) | 2019, arrete MENE1921262A",
        ),
        (
            PERIMETER,
            "arrete du 19-07-2019, MENE1921246A",
            "arrete du 19-07-2019, MENE1921247A",
        ),
        (
            ASSEMBLER,
            "programme 2019 MENE1921246A",
            "programme 2019 MENE1921247A",
        ),
    )

    for path, expected, stale in expectations:
        text = path.read_text(encoding="utf-8")
        assert expected in text, path
        assert stale not in text, path

    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "NSI Terminale (TNSI) | 2019, arrete MENE1921247A" in roadmap


def test_p0_tspe_readme_reports_the_current_fixed_provenance() -> None:
    text = README.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert CORRECT_TSPE_URL in text
    assert "Registre et table des sources alignés" in text
    assert (
        "Le registre canonique et la table des sources attribuent désormais "
        "à TSPE le NOR `MENE1921246A`"
    ) in normalized
    assert "Le registre courant attribue encore à TSPE" not in text
    assert "**Provenance TSPE.** Le registre porte" not in text
    assert "La provenance TSPE est corrigée et n'est plus un P0 ouvert." in text


@pytest.mark.parametrize("wrong_nor", [STMG_NOR, TNSI_NOR])
def test_p0_tspe_contract_rejects_another_terminal_nor(
    wrong_nor: str,
) -> None:
    fixture = {
        "reference_bo": CORRECT_TSPE_BO,
        "arrete": wrong_nor,
        "url": CORRECT_TSPE_URL,
        "fichier": CORRECT_TSPE_TEXT_PATH,
        "sha256": CORRECT_TSPE_TEXT_SHA256,
    }

    with pytest.raises(AssertionError):
        _assert_official_tspe_source(fixture)
```

- [ ] **Step 2: Vérifier la syntaxe et le diff du test**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
python3 -m py_compile tests/test_programme_registry.py
git diff --check -- tests/test_programme_registry.py
git diff -- tests/test_programme_registry.py
```

Expected: compilation Python et whitespace verts ; seul le test réglementaire
est modifié.

- [ ] **Step 3: Rejouer le contrat étendu en Red**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
set +e
python3 -m pytest tests/test_programme_registry.py -q \
  > /tmp/green-p0-programme-red.log 2>&1
status=$?
set -e
cat /tmp/green-p0-programme-red.log
test "$status" -eq 1
grep -F "4 failed, 3 passed" /tmp/green-p0-programme-red.log
```

Expected: quatre échecs causés par le registre, la table des sources, les
contextes actifs et le README ; trois succès prouvent l'empreinte archivée et
les deux mutations adversariales. Les sept cas verrouillent aussi
`programme_version == "2019"`, `date_application == "2020-09-01"` et les
colonnes BO/date/SHA-256 PDF externe de `SOURCES.md`, sans créer de huitième
cas. Aucun `skip`, `xfail` ou erreur de collecte.

- [ ] **Step 4: Committer uniquement le contrat Red étendu**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
git status --short
git add tests/test_programme_registry.py
test "$(git diff --cached --name-only)" = tests/test_programme_registry.py
set +e
python3 -m pytest tests/test_programme_registry.py -q \
  > /tmp/green-p0-programme-red-before-commit.log 2>&1
red_status=$?
set -e
test "$red_status" -eq 1
grep -F "4 failed, 3 passed" /tmp/green-p0-programme-red-before-commit.log
git diff --cached --check
git diff --cached --stat
git commit -m "[TESTS] étend le contrat de provenance TSPE"
```

Expected: un commit atomique de test, volontairement rouge avant le correctif.

## Chunk 2: Appliquer le correctif Green minimal

### Task 4: Aligner le registre et les sources actives

**Files:**
- Modify: `docs/programmes/PROGRAMMES_2026_2027.yaml`
- Modify: `Mathematiques/manuel-maths/sources/SOURCES.md`
- Modify: `Mathematiques/manuel-maths/docs/10_perimetre_terminale.md`
- Modify: `ROADMAP_TERMINALE.md`
- Modify: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`

- [ ] **Step 1: Corriger l'entrée canonique du registre**

Depuis le worktree cible absolu défini dans le préambule, utiliser
`apply_patch` exclusivement sur
`docs/programmes/PROGRAMMES_2026_2027.yaml` pour remplacer uniquement le champ
`arrete` de `SRC-BO2019-TSPE` et ajouter l'URL immédiatement après :

```yaml
  SRC-BO2019-TSPE:
    intitule: "Programme de spécialité mathématiques, classe terminale, voie générale"
    reference_bo: "BO spécial n° 8 du 25 juillet 2019"
    arrete: "MENE1921246A"
    url: "https://www.education.gouv.fr/bo/19/Special8/MENE1921246A.htm"
    fichier: "Mathematiques/manuel-maths/sources/txt/BO2019_TSPE_specialite.txt"
    sha256: "65eb5a55df14a2b3025a96db72fbcb1d917b55e8da7feb13669e28b903712210"
```

Expected: `fichier`, `sha256`, version du programme, date d'application et
liaison du manuel sont inchangés.

- [ ] **Step 2: Corriger la ligne TSPE de la table de sources**

Depuis le même worktree cible, utiliser `apply_patch` exclusivement sur
`Mathematiques/manuel-maths/sources/SOURCES.md` pour remplacer uniquement
`MENE1921262A` par `MENE1921246A` dans la ligne
`BO2019_TSPE_specialite.pdf` de
`Mathematiques/manuel-maths/sources/SOURCES.md`.

Expected: le nom de fichier, le BO, la date et le SHA-256 PDF restent
identiques.

- [ ] **Step 3: Corriger les trois contextes actifs ciblés**

Depuis le même worktree cible, utiliser `apply_patch` exclusivement sur les
trois chemins nommés ci-dessous :

- dans `Mathematiques/manuel-maths/docs/10_perimetre_terminale.md`, remplacer
  `arrete du 19-07-2019, MENE1921247A` par
  `arrete du 19-07-2019, MENE1921246A` ;
- dans la ligne TSPE de `ROADMAP_TERMINALE.md`, remplacer
  `arrete MENE1921262A` par `arrete MENE1921246A` ;
- dans le commentaire TSPE de
  `Mathematiques/manuel-maths/scripts/assemble_manuel.py`, remplacer
  `programme 2019 MENE1921247A` par `programme 2019 MENE1921246A`.

Expected: la ligne TNSI de la roadmap conserve `MENE1921247A`; aucun code
exécutable de l'assembleur ne change.

- [ ] **Step 4: Parser le YAML avant de toucher au README**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
python3 - <<'PY'
from pathlib import Path

import yaml

path = Path("docs/programmes/PROGRAMMES_2026_2027.yaml")
payload = yaml.safe_load(path.read_text(encoding="utf-8"))
source = payload["sources"]["SRC-BO2019-TSPE"]
manuals = [
    item
    for item in payload["manuels"]
    if item["manual_id"] == "TSPE_2026_2027"
]
assert source["reference_bo"] == "BO spécial n° 8 du 25 juillet 2019"
assert source["arrete"] == "MENE1921246A"
assert source["url"] == (
    "https://www.education.gouv.fr/bo/19/Special8/MENE1921246A.htm"
)
assert source["sha256"] == (
    "65eb5a55df14a2b3025a96db72fbcb1d917b55e8da7feb13669e28b903712210"
)
assert len(manuals) == 1
assert manuals[0]["programme_source"] == "SRC-BO2019-TSPE"
assert manuals[0]["programme_version"] == "2019"
assert manuals[0]["date_application"] == "2020-09-01"
print("TSPE registry: OK")
PY
```

Expected: `TSPE registry: OK`.

### Task 5: Actualiser exclusivement les affirmations TSPE obsolètes du README

**Files:**
- Modify: `README.md:363-395`
- Modify: `README.md:875-890`

- [ ] **Step 1: Mettre à jour la réserve de la ligne TSPE**

Depuis le worktree cible absolu défini dans le préambule, utiliser
`apply_patch` exclusivement sur `README.md` pour remplacer dans la ligne
`TSPE_2026_2027` :

```text
Registre local erroné, voir ci-dessous
```

par :

```text
Registre et table des sources alignés
```

- [ ] **Step 2: Remplacer le paragraphe d'erreur courante**

Depuis le même worktree cible, utiliser `apply_patch` exclusivement sur
`README.md` pour remplacer le paragraphe commençant par « Le registre courant
attribue encore » par exactement :

```markdown
Le registre canonique et la table des sources attribuent désormais à TSPE le
NOR `MENE1921246A`, en cohérence avec le programme de spécialité mathématiques
de Terminale. Les rapports datés conservent la trace de l'erreur antérieure.
```

- [ ] **Step 3: Retirer le quatrième P0 désormais corrigé**

Depuis le même worktree cible, utiliser `apply_patch` exclusivement sur
`README.md` pour supprimer uniquement les deux lignes de l'item
`4. **Provenance TSPE.**`, puis ajouter juste après la liste des trois P0 :

```markdown
La provenance TSPE est corrigée et n'est plus un P0 ouvert.
```

Expected: les fuites, débordements et renvois restent déclarés ouverts ; le
README ne transforme pas Wave 0 en GO publication.

- [ ] **Step 4: Vérifier que seuls les sept fichiers autorisés ont changé**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
git diff --check
git diff --name-only | sort > /tmp/green-p0-programme-files.txt
cat /tmp/green-p0-programme-files.txt
diff -u <(cat <<'EOF'
Mathematiques/manuel-maths/docs/10_perimetre_terminale.md
Mathematiques/manuel-maths/scripts/assemble_manuel.py
Mathematiques/manuel-maths/sources/SOURCES.md
README.md
ROADMAP_TERMINALE.md
docs/programmes/PROGRAMMES_2026_2027.yaml
EOF
) /tmp/green-p0-programme-files.txt
```

Expected: exactement les six fichiers de production réglementaire et de
documentation ; le test est déjà committé et n'apparaît donc pas dans le diff
non indexé.

### Task 6: Obtenir le Green ciblé et committer le correctif

**Files:**
- Test: `tests/test_programme_registry.py`
- Modify: les six fichiers de production/documentation listés ci-dessus

- [ ] **Step 1: Rejouer la famille réglementaire**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
python3 -m pytest tests/test_programme_registry.py -q
```

Expected: `7 passed`; aucun skip, xfail, warning de collecte ou erreur.

- [ ] **Step 2: Vérifier les références ciblées et l'exception TNSI**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
rg -n \
  'MENE1921246A|MENE1921262A|MENE1921247A' \
  docs/programmes/PROGRAMMES_2026_2027.yaml \
  Mathematiques/manuel-maths/sources/SOURCES.md \
  Mathematiques/manuel-maths/docs/10_perimetre_terminale.md \
  ROADMAP_TERMINALE.md \
  Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  README.md
```

Expected: `MENE1921246A` dans tous les contextes TSPE ; `MENE1921262A`
absent des contextes TSPE actifs ; `MENE1921247A` demeure dans les contextes
1SPE 2019 ou TNSI légitimes. Les audits historiques ne sont pas recherchés ni
modifiés.

- [ ] **Step 3: Committer le correctif réglementaire atomique**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
git status --short
python3 -m pytest tests/test_programme_registry.py -q
git add \
  docs/programmes/PROGRAMMES_2026_2027.yaml \
  Mathematiques/manuel-maths/sources/SOURCES.md \
  Mathematiques/manuel-maths/docs/10_perimetre_terminale.md \
  ROADMAP_TERMINALE.md \
  Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  README.md
git diff --cached --name-only | sort > /tmp/green-p0-programme-commit-files.txt
diff -u <(cat <<'EOF'
Mathematiques/manuel-maths/docs/10_perimetre_terminale.md
Mathematiques/manuel-maths/scripts/assemble_manuel.py
Mathematiques/manuel-maths/sources/SOURCES.md
README.md
ROADMAP_TERMINALE.md
docs/programmes/PROGRAMMES_2026_2027.yaml
EOF
) /tmp/green-p0-programme-commit-files.txt
git diff --cached --check
git diff --cached --stat
git commit -m "[PROGRAMME] corrige le NOR officiel TSPE"
```

Expected: deuxième commit atomique ; aucun test, PDF, audit, manifeste ou
baseline dans ce commit.

## Chunk 3: Vérifier, revoir et remettre la branche

### Task 7: Exécuter les preuves finales sans réécrire les artefacts observés

**Files:**
- Verify: `tests/test_programme_registry.py`
- Verify: `docs/programmes/PROGRAMMES_2026_2027.yaml`
- Verify: `Mathematiques/manuel-maths/sources/txt/BO2019_TSPE_specialite.txt`

- [ ] **Step 1: Rejouer les tests et la preuve d'empreinte**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
python3 -m pytest tests/test_programme_registry.py -q \
  | tee /tmp/green-p0-programme-final-tests.log
python3 - <<'PY'
from pathlib import Path
import re

lines = Path("/tmp/green-p0-programme-final-tests.log").read_text(
    encoding="utf-8"
).splitlines()
assert lines, "résumé pytest absent"
assert re.fullmatch(r"7 passed in [0-9]+(?:\.[0-9]+)?s", lines[-1]), lines[-1]
print(lines[-1])
PY
source_txt=Mathematiques/manuel-maths/sources/txt/BO2019_TSPE_specialite.txt
test "$(sha256sum "$source_txt" | cut -d' ' -f1)" = \
  65eb5a55df14a2b3025a96db72fbcb1d917b55e8da7feb13669e28b903712210
```

Expected: sept cas verts et empreinte suivie inchangée.

- [ ] **Step 2: Effectuer la mutation adversariale sans modifier la production**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
python3 -m pytest \
  tests/test_programme_registry.py::test_p0_tspe_contract_rejects_another_terminal_nor \
  -q
```

Expected: `2 passed`; les fixtures STMG et TNSI sont toutes deux rejetées par
le contrat exact.

- [ ] **Step 3: Vérifier le gate d'inventaire dans le worktree**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
set +e
inventory_output=$(
  python3 scripts/inventory_collection.py --check --require-clean 2>&1
)
inventory_status=$?
set -euo pipefail
printf '%s\n' "$inventory_output" \
  | tee /tmp/green-p0-programme-inventory.log
test "$inventory_status" -eq 3
printf '%s\n' "$inventory_output" | python3 -c '
import json
import sys

payload = json.loads(sys.stdin.read().splitlines()[-1])
assert payload["gate"] == "check"
assert payload["exit_code"] == 3
assert payload["reasons"] == [
    "check_error:source_digest du manifeste de build incohérent"
]
'
```

Expected: code 3 pour l'unique motif prioritaire
`check_error:source_digest du manifeste de build incohérent`, conséquence
attendue du diff réglementaire par rapport au manifeste observé. Toute raison
différente ou supplémentaire arrête le lot. Consigner ce motif dans le compte
rendu ; ne jamais réécrire `audit/BUILD_MANIFEST.json` pour rendre ce gate vert.

- [ ] **Step 4: Relever le gate de release sur son checkout attesté**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
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
set +e
(cd "$integration_checkout" && \
  python3 scripts/inventory_collection.py \
    --check --release-strict --require-clean)
release_status=$?
set -e
test "$release_status" -eq 7
```

Expected: `release-strict` reste rouge code 7 sur le checkout attesté. Ce
relevé est un état de gouvernance, pas une preuve d'intégration du correctif.

- [ ] **Step 5: Vérifier l'arbre, les commits et le périmètre cumulé**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
git status --short --branch
git diff --check
git log --oneline --decorate -3
base=$(git merge-base HEAD wave0/p0-green-launch)
test -n "$base"
git diff --check "$base..HEAD"
git diff --name-only "$base..HEAD" \
  | sort > /tmp/green-p0-programme-final-files.txt
diff -u <(cat <<'EOF'
Mathematiques/manuel-maths/docs/10_perimetre_terminale.md
Mathematiques/manuel-maths/scripts/assemble_manuel.py
Mathematiques/manuel-maths/sources/SOURCES.md
README.md
ROADMAP_TERMINALE.md
docs/programmes/PROGRAMMES_2026_2027.yaml
tests/test_programme_registry.py
EOF
) /tmp/green-p0-programme-final-files.txt
test -z "$(git status --porcelain)"
mapfile -t lot_commits < <(git rev-list --reverse "$base..HEAD")
test "${#lot_commits[@]}" -ge 2
test "$(git show -s --format=%s "${lot_commits[0]}")" = \
  "[TESTS] étend le contrat de provenance TSPE"
test "$(git show -s --format=%s "${lot_commits[1]}")" = \
  "[PROGRAMME] corrige le NOR officiel TSPE"
for commit in "${lot_commits[@]:2}"
do
  subject=$(git show -s --format=%s "$commit")
  case "$subject" in
    "[TESTS] corrige la revue provenance TSPE")
      test "$(git diff-tree --no-commit-id --name-only -r "$commit")" = \
        tests/test_programme_registry.py
      ;;
    "[PROGRAMME] corrige la revue provenance TSPE")
      while IFS= read -r path
      do
        case "$path" in
          Mathematiques/manuel-maths/docs/10_perimetre_terminale.md|\
          Mathematiques/manuel-maths/scripts/assemble_manuel.py|\
          Mathematiques/manuel-maths/sources/SOURCES.md|\
          README.md|ROADMAP_TERMINALE.md|\
          docs/programmes/PROGRAMMES_2026_2027.yaml) ;;
          *) printf 'fichier de revue interdit: %s %s\n' "$commit" "$path" >&2; exit 1 ;;
        esac
      done < <(git diff-tree --no-commit-id --name-only -r "$commit")
      ;;
    *) printf 'commit de revue interdit: %s %s\n' "$commit" "$subject" >&2; exit 1 ;;
  esac
done
```

Expected: arbre propre et exactement sept fichiers depuis la base dynamique.
Les deux premiers commits du lot sont présents dans l'ordre avec leurs messages
verrouillés. D'éventuels commits ultérieurs sont exclusivement des corrections
atomiques de revue portant l'un des deux messages autorisés et respectant le
périmètre de leur lane.

### Task 8: Obtenir les deux revues indépendantes

**Files:**
- Review: diff calculé par
  `base=$(git merge-base HEAD wave0/p0-green-launch); git diff "$base..HEAD"`
- Review: `docs/superpowers/specs/2026-08-13-green-p0-programme-tspe-design.md`

- [ ] **Step 1: Demander la revue de conformité réglementaire**

Avec `superpowers:subagent-driven-development`, déléguer une revue en lecture
seule à un reviewer qui n'a écrit ni les tests ni le correctif. Lui demander de
vérifier : NOR, intitulé, BO, URL, règle temporelle 2026-2027, empreinte suivie,
exception TNSI, README, absence de modification des audits et respect exact de
la spécification.

Expected: `✅ Approved`. En cas de finding, le responsable d'implémentation ne
réécrit ni n'amende les deux commits de base. Il ajoute un commit atomique
`[TESTS] corrige la revue provenance TSPE` ou
`[PROGRAMME] corrige la revue provenance TSPE` selon le lane, rejoue Task 7 et
redemande la revue. Tout commit correctif doit rester dans les sept chemins
autorisés et recevoir `✅ Approved` avant la remise.

- [ ] **Step 2: Demander la revue de qualité du diff**

Déléguer à un second reviewer indépendant une revue en lecture seule portant
sur : robustesse des tests, absence de faux positif global sur `MENE1921247A`,
TDD, mutations, périmètre de sept fichiers, cohérence README, absence de
`skip`/`xfail`, gates non affaiblis et historique Git atomique.

Expected: `✅ Approved`. Ne pas passer à la remise si un finding reste ouvert.

- [ ] **Step 3: Encadrer tout commit correctif demandé par une revue**

Avant de corriger, conserver dans l'échange avec le reviewer le finding, le
lane, le nœud pytest exact et son attendu Red/Green ; ne créer aucun nouveau
fichier dans le dépôt. Ne jamais amender les deux commits de base. Pour un
finding de test, exécuter dans cet ordre :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
git status --short
test "$(git diff --name-only)" = tests/test_programme_registry.py
python3 -m py_compile tests/test_programme_registry.py
git diff --check -- tests/test_programme_registry.py
set +e
python3 -m pytest tests/test_programme_registry.py -q \
  > /tmp/green-p0-programme-review-red.log 2>&1
review_red_status=$?
set -e
cat /tmp/green-p0-programme-review-red.log
test "$review_red_status" -eq 1
git add tests/test_programme_registry.py
test "$(git diff --cached --name-only)" = tests/test_programme_registry.py
git diff --cached --check
git diff --cached --stat
git commit -m "[TESTS] corrige la revue provenance TSPE"
```

Expected: seul le contrat réglementaire est committé. Le nœud exact conservé
dans l'échange de revue a été observé Red avant ce commit ; passer ensuite au
correctif de production correspondant, sans laisser ce nouveau Red comme état
final et sans ajouter de fichier de compte rendu.

Pour un finding de production/documentation, exécuter après son test Red :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
git status --short
python3 -m pytest tests/test_programme_registry.py -q
git diff --check
git add \
  docs/programmes/PROGRAMMES_2026_2027.yaml \
  Mathematiques/manuel-maths/sources/SOURCES.md \
  Mathematiques/manuel-maths/docs/10_perimetre_terminale.md \
  ROADMAP_TERMINALE.md \
  Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  README.md
test -n "$(git diff --cached --name-only)"
while IFS= read -r path
do
  case "$path" in
    Mathematiques/manuel-maths/docs/10_perimetre_terminale.md|\
    Mathematiques/manuel-maths/scripts/assemble_manuel.py|\
    Mathematiques/manuel-maths/sources/SOURCES.md|\
    README.md|ROADMAP_TERMINALE.md|\
    docs/programmes/PROGRAMMES_2026_2027.yaml) ;;
    *) printf 'fichier de revue interdit: %s\n' "$path" >&2; exit 1 ;;
  esac
done < <(git diff --cached --name-only)
git diff --cached --check
git diff --cached --stat
git commit -m "[PROGRAMME] corrige la revue provenance TSPE"
```

Expected: les tests réglementaires sont verts avant le commit ; le staging est
non vide et borné aux six fichiers de production/documentation. Si un finding
touche tests et production, effectuer les deux commits dans cet ordre. Rejouer
Task 7 et demander de nouveau les deux revues après chaque série de corrections.

- [ ] **Step 4: Exécuter la vérification finale fraîche après les revues**

Run :

```bash
set -euo pipefail
target=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-programme-tspe
cd "$target"
python3 -m pytest tests/test_programme_registry.py -q
base=$(git merge-base HEAD wave0/p0-green-launch)
git diff --check "$base..HEAD"
test -z "$(git status --porcelain)"
git rev-parse HEAD
```

Expected: `7 passed`, diff propre, arbre propre et SHA final relevé après toute
correction de revue.

### Task 9: Remettre la branche sans intégration implicite

**Files:**
- Report only; no new file required

- [ ] **Step 1: Produire le compte rendu contractuel**

Rendre exactement cette structure avec les valeurs observées :

```text
ÉTAT <SHA final>
Branche : green/p0-programme-tspe
Phase : Wave 0 — Green P0 provenance TSPE
Commits : <liste des commits atomiques>
Tests : 7 tests réglementaires verts, dont 2 mutations adversariales
Gates verts : parse YAML, empreinte suivie, diff-check, deux revues
Gates rouges : G3 Programme incomplet ; G10 Release incomplet ; release-strict code 7 ; worktree inventory code 3 pour source_digest du manifeste incohérent, manifeste non réécrit
P0 ouverts : fuites élève, renvois/IDs et débordements ; autres dettes release
Décisions humaines : jalon Red et approche A approuvés ; aucune décision visuelle requise
PR : aucune sauf instruction humaine ultérieure
Prochaine action : intégrer ce lot dans la branche d'intégration après validation humaine
```

- [ ] **Step 2: Conserver la branche isolée**

Ne pas merger, rebaser, pousser, ouvrir une PR, modifier `main`, supprimer le
worktree ou mettre à jour un tag sans instruction humaine explicite.

## Définition de terminé

Le lot Programme TSPE est terminé seulement si :

- la branche part exactement de la pointe propre de `wave0/p0-green-launch`
  capturée après versionnement des trois plans et de leurs spécifications ;
- les deux commits de base attendus sont présents, atomiques, dans l'ordre et
  portent leurs messages exacts ; tout commit ultérieur est une correction de
  revue autorisée, atomique, rejouée et approuvée ;
- les sept cas réglementaires sont verts ;
- `reference_bo`, `arrete`, `url`, `programme_source`,
  `programme_version == "2019"`, `date_application == "2020-09-01"`, unicité
  du manuel, chemin et SHA-256 de l'extrait sont verrouillés ;
- l'unique ligne `BO2019_TSPE_specialite.pdf` verrouille son BO, sa date et le
  SHA-256 PDF externe
  `eb8369e7c1611e90f51491fecc5a7c2081a9c57f9c7fbb08d0414677b56ce16f`,
  sans faire de ce PDF ignoré une dépendance du gate ;
- les trois contextes TSPE actifs et le README sont cohérents ;
- seul le P0 de provenance TSPE est déclaré fermé ; G3 Programme et G10
  Release restent explicitement rouges ;
- le contexte TNSI légitime conserve `MENE1921247A` ;
- l'extrait suivi garde son empreinte et le PDF ignoré n'est pas une dépendance ;
- les audits datés, PDF, manifests et baselines sont intacts ;
- le seul échec du gate d'inventaire du worktree est
  `check_error:source_digest du manifeste de build incohérent`, documenté sans
  réécriture du manifeste ;
- `release-strict` reste rouge et n'est pas présenté comme une régression du lot ;
- les deux revues indépendantes sont approuvées ;
- l'arbre final est propre et aucune intégration n'a été effectuée implicitement.
