# Green P0 Overflow and PDF Preflight Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rendre bloquant tout `Overfull \hbox`/`Overfull \vbox`, attribuer chaque diagnostic à une source traçable, corriger chaque cause minimale dans les quatre éditions Mathématiques, puis versionner uniquement les quatre PDF approuvés visuellement.

**Architecture:** Empiler `green/p0-overflow` sur la branche séparation approuvée, faire déléguer l'assembleur et la matrice à un helper local reproductible unique, puis faire précéder `pdffonts` par le gate strict. Le master émet des marqueurs objet/ouverture/shipout sans exposer les chemins ; un parseur résout les tokens SHA-256 tronqués à 40 hex via une table versionnée et pilote les corrections et la revue visuelle. Les PDF intermédiaires restent l'état « avant », les candidats finaux restent temporaires jusqu'à l'approbation humaine, et aucune baseline ni preuve observée n'est modifiée.

**Tech Stack:** Python 3.12, pytest, LuaLaTeX (3 passes et `-recorder`), KOMA-Script/tcolorbox, Poppler (`pdffonts`, `pdftoppm`, `pdfinfo`), qpdf, Pillow, JSON/SHA-256, Git worktrees.

**Design:** `docs/superpowers/specs/2026-08-13-green-p0-overflow-preflight-design.md`

**Mesure Red approuvée avant séparation:** `1SPE/élève = 17 hbox + 2 vbox`,
`1SPE/professeur = 20 + 2`, `TSPE/élève = 7 + 2`,
`TSPE/professeur = 9 + 2`. Le premier replay après séparation mesure de
nouveau la matrice ; aucun compte non nul, ancien ou frais, n'est une baseline.

Chaque bloc `Run` ci-dessous commence par son `cd` absolu. Aucun bloc ne
dépend du répertoire courant ou de variables shell d'un bloc antérieur.

---

## Chunk 1: Isoler la lane et verrouiller les contrats Red

### Task 1: Créer le worktree empilé seulement après la séparation

**Files:**
- Read: `AGENTS.md`
- Read: `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md`
- Read: `docs/superpowers/specs/2026-08-13-wave-0-green-p0-launch-design.md`
- Read: `docs/superpowers/specs/2026-08-13-green-p0-overflow-preflight-design.md`
- Read: `docs/superpowers/specs/2026-08-13-green-p0-separation-eleve-design.md`
- Read: `docs/codex/QUALITY_GATES.md`
- Read: `docs/codex/CI_AUDIT_PHASE_0.md`
- Read: `audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json`

- [ ] **Step 1: Verrouiller la base launch propre et versionnée**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus
launch=/home/alaeddine/Documents/Manuels_Nexus/.worktrees/wave0-p0-green-launch
git -C "$launch" status --short --branch
git -C "$launch" diff --stat
git -C "$launch" diff --check
test -z "$(git -C "$launch" status --porcelain)"
git -C "$launch" ls-files --error-unmatch \
  docs/superpowers/plans/2026-08-13-green-p0-overflow-preflight.md \
  docs/superpowers/plans/2026-08-13-green-p0-programme-tspe.md \
  docs/superpowers/plans/2026-08-13-green-p0-separation-eleve.md
git -C "$launch" rev-parse HEAD
git show-ref --verify refs/heads/green/p0-student-separation
launch_base=$(git -C "$launch" rev-parse HEAD)
separation_base=$(git rev-parse green/p0-student-separation)
git merge-base --is-ancestor "$launch_base" "$separation_base"
git log --oneline --decorate "$launch_base..$separation_base"
```

Expected: le worktree launch est strictement propre, les trois plans sont
suivis par Git à son HEAD dynamique, et ce HEAD est ancêtre de la pointe
séparation. Le log ne contient que les commits approuvés/versionnés de la
lane séparation. Ne pas stasher, restaurer, nettoyer ou rebaser.

- [ ] **Step 2: Valider l'identité de l'entrée intermédiaire**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus
python3 - <<'PY'
import hashlib
import json
import subprocess
from pathlib import Path

root = Path('/home/alaeddine/Documents/Manuels_Nexus')
branch = 'green/p0-student-separation'
manifest_relative = 'audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json'

tracked = subprocess.run(
    ['git', 'ls-tree', '-r', '--name-only', branch, '--', manifest_relative],
    cwd=root, check=True, capture_output=True, text=True,
).stdout.splitlines()
assert tracked == [manifest_relative]

def committed(relative: str) -> bytes:
    return subprocess.run(
        ['git', 'show', f'{branch}:{relative}'], cwd=root,
        check=True, capture_output=True,
    ).stdout

manifest = json.loads(committed(manifest_relative).decode('utf-8'))
assert manifest['schema_version'] == 1
assert manifest['artifact_identity'] == 'wave0-separation-intermediate'
assert manifest['decision']['status'] == 'approved'
assert manifest['decision']['approved_by'].strip()
assert manifest['decision']['approved_at'].strip()
assert manifest['decision']['scope'] == 'visual-separation-only'
assert isinstance(manifest['tool_versions'], dict) and manifest['tool_versions']
expected = {
    '1SPE:eleve': 'Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf',
    '1SPE:professeur': 'Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf',
    'TSPE_2026_2027:eleve': 'Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf',
    'TSPE_2026_2027:professeur': 'Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.pdf',
}
assert set(manifest['artifacts']) == set(expected)
for build_id, relative in expected.items():
    item = manifest['artifacts'][build_id]
    assert item['path'] == relative
    assert len(item['before_sha256']) == 64
    assert len(item['after_sha256']) == 64
    assert item['page_count'] > 0
    assert isinstance(item['affected_pages'], list)
    assert item['page_evidence']
    assert item['contact_sheet']
    digest = hashlib.sha256(committed(relative)).hexdigest()
    assert item['after_sha256'] == digest
    assert item['overfull_debt']['hbox'] >= 0
    assert item['overfull_debt']['vbox'] >= 0
print('4 PDF wave0-separation-intermediate approuves et intacts')
PY
```

Expected: `4 PDF wave0-separation-intermediate approuves et intacts`. Le
manifeste intermédiaire approuvé/versionné est une précondition contractuelle,
pas une baseline à réécrire. Toute divergence arrête le lot.

- [ ] **Step 3: Créer la branche et le worktree empilés**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus
separation_base=$(git rev-parse green/p0-student-separation)
git worktree add .worktrees/green-p0-overflow -b green/p0-overflow "$separation_base"
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
test "$(git rev-parse HEAD)" = "$separation_base"
git status --short --branch
git diff --check
```

Expected: branche `green/p0-overflow`, HEAD identique à la pointe séparation,
worktree propre. Si la branche ou le dossier existe déjà, l'inspecter et
réutiliser uniquement l'instance humaine approuvée ; ne rien supprimer.

- [ ] **Step 4: Lire intégralement AGENTS et la spécification orchestratrice**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
sed -n '1,228p' AGENTS.md
sed -n '1,164p' docs/superpowers/specs/2026-08-13-wave-0-green-p0-launch-design.md
```

Expected: autorité, interdictions Git, TDD, topologie des trois branches,
workflow PDF et NO-GO lus avant toute modification.

- [ ] **Step 5: Lire intégralement les deux spécifications de dépendance**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
sed -n '1,254p' docs/superpowers/specs/2026-08-13-green-p0-overflow-preflight-design.md
sed -n '1,312p' docs/superpowers/specs/2026-08-13-green-p0-separation-eleve-design.md
python3 - <<'PY'
from pathlib import Path

overflow = Path('docs/superpowers/specs/2026-08-13-green-p0-overflow-preflight-design.md').read_text(encoding='utf-8')
separation = Path('docs/superpowers/specs/2026-08-13-green-p0-separation-eleve-design.md').read_text(encoding='utf-8')
for needle in ('sans tolérance ni baseline', 'NEXUS_OBJECT_BEGIN/END', 'baseline_updated: false', '--release-strict'):
    assert needle in overflow, needle
for needle in ('wave0-separation-intermediate', 'approbation visuelle', 'Overfull'):
    assert needle in separation, needle
print('overflow/separation contracts: read')
PY
```

Expected: `overflow/separation contracts: read`; hashes intermédiaires,
fail-fast, attribution, revue visuelle et dette non baselinée compris.

- [ ] **Step 6: Lire le premier tiers du cahier des charges**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
sed -n '1,400p' CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md
```

Expected: hiérarchie des sources, P0 et non-destruction lus.

- [ ] **Step 7: Lire le deuxième tiers du cahier des charges**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
sed -n '401,800p' CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md
```

Expected: architecture, reproductibilité, visuel et baseline lus.

- [ ] **Step 8: Lire la fin du cahier des charges**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
sed -n '801,1141p' CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md
```

Expected: gates, commits, CI et définition de terminé lus ; aucun GO implicite.

- [ ] **Step 9: Lire l'audit courant et borner les dettes historiques**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
sed -n '1,254p' audit/AUDIT_ETAT_PROJET_2026-08-13.md
python3 - <<'PY'
from pathlib import Path

text = Path('audit/AUDIT_ETAT_PROJET_2026-08-13.md').read_text(encoding='utf-8')
for needle in ('check_charte_sync.py', 'code 1', 'code 7, 67 bloqueurs', 'NO-GO'):
    assert needle in text, needle
print('dated audit boundaries: read')
PY
```

Expected: l'audit reste historique et hors écriture ; dettes hors lot connues.

- [ ] **Step 10: Lire G3/G10 et borner la fermeture du lot**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
sed -n '1,138p' docs/codex/QUALITY_GATES.md
python3 - <<'PY'
from pathlib import Path

text = Path('docs/codex/QUALITY_GATES.md').read_text(encoding='utf-8')
for needle in (
    '## Gate G3 — Programme', 'matrice officielle complète',
    'validation humaine', '## Gate G10 — Release',
    '`--validate-model` vert', '`--fail-on-new` vert',
    '`--release-strict` vert',
):
    assert needle in text, needle
print('G3/G10 remain globally open')
PY
```

Expected: ce lot ferme uniquement Overflow/préflight ; G3 et G10 restent
rouges et aucune case non couverte n'est revendiquée.

- [ ] **Step 11: Lire le contrat CI et conserver son rouge contrôlé**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
sed -n '1,56p' docs/codex/CI_AUDIT_PHASE_0.md
python3 - <<'PY'
from pathlib import Path

text = Path('docs/codex/CI_AUDIT_PHASE_0.md').read_text(encoding='utf-8')
for needle in (
    '`--release-strict` avec un code exactement égal à 7',
    'La CI n’appelle jamais `--update-baseline`',
    'ne vaut ni acceptation scientifique',
):
    assert needle in text, needle
print('phase-0 CI release debt: read')
PY
```

Expected: le code 7 reste attendu hors lot ; aucune baseline ni acceptation
scientifique/éditoriale n'est inférée de ce Green.

- [ ] **Step 12: Capturer l'état de départ et le rouge charte exact**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
git rev-parse HEAD
git log --oneline --decorate -15
python3 - <<'PY'
import subprocess

completed = subprocess.run(
    ['python3', 'scripts/check_charte_sync.py'],
    check=False, capture_output=True, text=True,
)
assert completed.returncode == 1
assert completed.stderr == ''
assert completed.stdout.splitlines() == [
    'Dérive de charte détectée :',
    '- gabarits/nexus-manuel.cls',
    '- scripts/pdf_integrity.py',
]
print(completed.stdout, end='')
PY
git status --short --branch
```

Expected: `check_charte_sync.py` reste rouge (`1`) exactement sur
`gabarits/nexus-manuel.cls` et `scripts/pdf_integrity.py`, dette antérieure
connue. Noter le SHA de départ ; ne synchroniser ni classe ni gate vers NSI.

### Task 2: Étendre le contrat réel aux quatre éditions avant le Green

**Files:**
- Modify: `Mathematiques/manuel-maths/tests/test_p0_overflow_artifact.py`
- Read: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
- Read: `Mathematiques/manuel-maths/config/reproducible-build.json`

- [ ] **Step 1: Paramétrer la matrice contractuelle**

Dans `test_p0_overflow_artifact.py`, importer `pytest`, nommer le test
`test_p0_real_manual_produces_no_overfull` et remplacer le cas unique par
exactement :

```python
MATRIX = (
    pytest.param("1SPE", "eleve", "MANUEL_1SPE_eleve", id="1SPE-eleve"),
    pytest.param(
        "1SPE", "professeur", "MANUEL_1SPE_professeur",
        id="1SPE-professeur",
    ),
    pytest.param(
        "TSPE_2026_2027", "eleve", "MANUEL_TSPE_2026-2027_eleve",
        id="TSPE_2026_2027-eleve",
    ),
    pytest.param(
        "TSPE_2026_2027", "professeur",
        "MANUEL_TSPE_2026-2027_professeur",
        id="TSPE_2026_2027-professeur",
    ),
)
```

Conserver trois passes réelles, ajouter `-recorder`, vérifier `.log`, `.fls`
et PDF, puis exiger zéro occurrence des deux diagnostics. Absence LuaLaTeX,
timeout, configuration manquante ou passe non nulle font `pytest.fail`, jamais
`skip`, `skipif` ou `xfail`. Les comptes frais sont affichés, pas acceptés.

- [ ] **Step 2: Observer le Red `1SPE-eleve`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[1SPE-eleve]' -vv -p no:cacheprovider
```

Expected: FAIL sur un compte frais non nul ; infrastructure indisponible =
blocage distinct, jamais skip.

- [ ] **Step 3: Observer le Red `1SPE-professeur`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[1SPE-professeur]' -vv -p no:cacheprovider
```

Expected: FAIL si la dette intermédiaire est non nulle, avec comptes affichés.

- [ ] **Step 4: Observer le Red `TSPE_2026_2027-eleve`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[TSPE_2026_2027-eleve]' -vv -p no:cacheprovider
```

Expected: FAIL si la dette intermédiaire est non nulle, avec comptes affichés.

- [ ] **Step 5: Observer le Red `TSPE_2026_2027-professeur`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[TSPE_2026_2027-professeur]' -vv -p no:cacheprovider
```

Expected: FAIL si la dette intermédiaire est non nulle, avec comptes affichés.

- [ ] **Step 6: Vérifier l'absence d'affaiblissement**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
rg -n "skip|skipif|xfail|overfull_debt|whitelist|threshold|tolerance" \
  Mathematiques/manuel-maths/tests/test_p0_overflow_artifact.py
git diff --check
git diff -- Mathematiques/manuel-maths/tests/test_p0_overflow_artifact.py
```

Expected: aucune tolérance, liste blanche, dette acceptée ou marque de skip.

- [ ] **Step 7: Committer le contrat Red seul**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
git status --short
set +e
python3 -m pytest Mathematiques/manuel-maths/tests/test_p0_overflow_artifact.py -q -p no:cacheprovider
red_status=$?
set -e
test "$red_status" -eq 1
git add Mathematiques/manuel-maths/tests/test_p0_overflow_artifact.py
test "$(git diff --cached --name-only)" = \
  Mathematiques/manuel-maths/tests/test_p0_overflow_artifact.py
git diff --cached --check
git diff --cached --stat
git commit -m "[TESTS] étend le contrat de débordement aux quatre éditions"
```

Expected: commit de test seul, sans production, PDF, audit ou baseline.

### Task 3: Faire échouer le préflight avant `pdffonts`

**Files:**
- Modify: `Mathematiques/manuel-maths/tests/test_pdf_integrity.py`
- Modify: `Mathematiques/manuel-maths/scripts/pdf_integrity.py`

- [ ] **Step 1: Préciser les quatre assertions unitaires Red**

Créer deux tests distincts `hbox`/`vbox` exigeant code `1`, type exact et
chemin exact du `.log` dans stdout ; leur faux runner lève s'il est appelé.
Ajouter un cas propre où `pdffonts` est appelé exactement une fois et retourne
`0`. Conserver les tests Red déjà approuvés, sans les remplacer par un wrapper.

- [ ] **Step 2: Observer la cause attendue**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_pdf_integrity.py \
  -k 'overfull or clean_log_continues_to_pdffonts' -vv -p no:cacheprovider
```

Expected: `hbox`/`vbox` rouges parce que le runner interdit est appelé ; le cas
propre passe.

- [ ] **Step 3: Implémenter le fail-fast minimal**

Définir les deux littéraux fermés et un helper pur qui retourne les types
rencontrés. Dans `verify_pdf()`, après assets/glyphes mais avant le `try` de
`pdffonts`, imprimer puis retourner `1` :

```text
Débordement LaTeX Overfull \hbox : {log_path}
Débordement LaTeX Overfull \vbox : {log_path}
```

Ne pas compter, filtrer, tronquer, accepter un seuil ou ajouter une option.

- [ ] **Step 4: Rendre toute la famille PDF verte**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_pdf_integrity.py -q -p no:cacheprovider
```

Expected: tous les tests du fichier passent, y compris polices et marges.

- [ ] **Step 5: Exécuter la mutation runner isolée**

Le test pytest crée avec `tmp_path` un `.log` minimal contenant
`Overfull \hbox (0.01pt too wide)`, fournit un faux runner qui lève s'il est
appelé, puis exige code `1`, type/chemin exacts et zéro appel `pdffonts`.

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_pdf_integrity.py \
  -k overfull_mutation_stops_before_pdffonts -vv -p no:cacheprovider
```

Expected: PASS ; la mutation ne touche aucun fichier suivi et ne demande
aucune restauration.

- [ ] **Step 6: Committer le gate PDF**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
git status --short
python3 -m pytest Mathematiques/manuel-maths/tests/test_pdf_integrity.py -q -p no:cacheprovider
git add Mathematiques/manuel-maths/scripts/pdf_integrity.py \
  Mathematiques/manuel-maths/tests/test_pdf_integrity.py
test "$(git diff --cached --name-only | sort)" = "$(printf '%s\n' \
  Mathematiques/manuel-maths/scripts/pdf_integrity.py \
  Mathematiques/manuel-maths/tests/test_pdf_integrity.py | sort)"
git diff --cached --check
git diff --cached --stat
git commit -m "[PDF] refuse les overfull au préflight mathématiques"
```

Expected: gate Mathématiques et tests seulement ; NSI reste intact et
`check_charte_sync.py` encore rouge.

## Chunk 2: Unifier le build et attribuer tous les diagnostics

### Task 4: Émettre la traçabilité objet, ouverture et shipout

**Files:**
- Modify: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
- Modify: `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py`
- Read: `scripts/build_manifest.py`
- Read: `tests/test_build_manifest.py`

- [ ] **Step 1: Écrire les tests Red des tokens et de la table**

Exiger pour chaque objet un token `^[0-9a-f]{40}$`, exactement égal à
`scripts.build_manifest._object_trace_token(chemin_canonique)`. Exiger une
table JSON version 1 contenant `algorithm: sha256`, `token_length: 40` et le
marqueur `trace-token-40-hex`, puis le dictionnaire trié
`token -> chemin canonique suivi`. Tester refus d'une
collision simulée, d'un token inconnu et d'une divergence avec le recorder.

- [ ] **Step 2: Écrire le test Red du master instrumenté**

Le test exige les séquences exactes :

```text
NEXUS_OBJECT_BEGIN:{token_40_hex}
NEXUS_OBJECT_END:{same_token_40_hex}
NEXUS_OPENING_BEGIN:{chapter_id}
{opening ending with \clearpage}
NEXUS_OPENING_END:{chapter_id}
NEXUS_PAGE_SHIPOUT:{absolute_page}:{chapter_id}:{rubric_id}:{context_id}
```

Le hook incrémente une page absolue indépendante du folio. Chapitre, rubrique
et contexte sont des identifiants ASCII Python ; aucun chemin n'apparaît dans
le TeX/log.

- [ ] **Step 3: Observer le Red des ouvertures/shipout**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_assemble_manuel_observed.py \
  -k 'trace_token or trace_table or opening_trace or page_shipout_trace' \
  -vv -p no:cacheprovider
```

Expected: tokens objet historiques verts ; table/ouverture/shipout rouges.

- [ ] **Step 4: Instrumenter le master sans effet visuel**

Étendre `render_master()` avec un collecteur optionnel. Autour de chaque
ouverture : poser chapitre/rubrique/contexte, émettre BEGIN, appeler
`ouverture_depuis_contrat()` (incluant `\clearpage`), puis END. Autour de
chaque objet, conserver strictement token et marqueurs existants, contexte
`object:{token}`, puis `pending` après END. Ajouter un hook `shipout/after` qui
émet page absolue/chapitre/rubrique/contexte. `render_master()` retourne le
master et la table sérialisable sans compiler ni dépendre du futur helper ;
Task 5 sera responsable de les écrire ensemble avant compilation.

- [ ] **Step 5: Vérifier l'absence de dérive recorder**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_assemble_manuel_observed.py ../../tests/test_build_manifest.py \
  -k 'trace or ordered_object' -q -p no:cacheprovider
```

Expected: tout vert, tokens inchangés, chemins absents des marqueurs, table
complète et sans collision.

### Task 5: Extraire le helper reproductible commun sans second chemin

**Files:**
- Modify: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`
- Modify: `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py`
- Modify: `Mathematiques/manuel-maths/tests/test_p0_overflow_artifact.py`

- [ ] **Step 1: Écrire les contrats Red du helper et du délai**

Attendre une `LocalBuildResult` avec `master_path`, `log_path`, `fls_path`,
`pdf_path`, `preflight_path`, `trace_table_path`, `environment`,
`lualatex_command`, `passes`, `preflight_returncode` et `passed`. Avec
`FakeProductionRunner`, exiger config chargée, table de trace déjà écrite,
`TEXMFVAR` sous le run, trois commandes `-recorder`, sorties conservées et
préflight. Un second test compare exactement master normalisé, environnement,
arguments et résultat via appel direct et `_main_locked()`.

Ajouter un test dont le runner lève `subprocess.TimeoutExpired`. Exiger
`timeout=300` à chaque passe, `passed=False`, le message exact
`LuaLaTeX timeout 300s`, et la conservation de master/log/fls/PDF/preflight/
table dans `tmp_path` quand ils existent. Espionner promotion, receipt et
record observed : zéro appel et aucun chemin canonique modifié.

- [ ] **Step 2: Observer les Red du helper absent et du timeout**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_assemble_manuel_observed.py \
  -k 'local_build_helper or orchestration_delegates_to_local_build_helper or timeout_retains_artifacts_without_promotion' \
  -vv -p no:cacheprovider
```

Expected: FAIL sur API/délai/délégation, pas sur la fixture Git.

- [ ] **Step 3: Implémenter l'API fermée du helper**

`build_local_candidate()` charge `_load_reproducibility_control()` et les
chemins suivis, écrit master et table, isole `texmf-var`, puis exécute trois
passes avec la commande existante, `-recorder` et `timeout=300` par appel. Il
vérifie fraîcheur/run-id, appelle `verify_pdf`, séparation élève, `pdfinfo` et
versions, puis écrit atomiquement le preflight JSON.

`TimeoutExpired` devient un résultat rouge explicite sans supprimer les
artefacts temporaires. Tout gate rouge donne `passed=False`; le helper ne
promeut rien, n'écrit ni receipt ni preuve observée et n'appelle jamais
`--record-observed`.

L'environnement exact est : éventuels `PATH`/`HOME` allowlistés,
`FORCE_SOURCE_DATE=1`, `TZ=UTC`, `LC_ALL=C.UTF-8`, `PYTHONHASHSEED=0`,
`SOURCE_DATE_EPOCH` depuis le JSON, plus `TEXMFVAR={run}/texmf-var`.

- [ ] **Step 4: Faire déléguer `_main_locked()`**

Conserver verrou, répertoire privé, fingerprints, promotion, receipt et
recorder dans `_main_locked()`, mais remplacer sa compilation/préflight par un
appel unique au helper. `passed=False`, timeout compris, lève
`AssemblyError("préflight PDF en échec")` avant toute promotion.

- [ ] **Step 5: Basculer la matrice vers le même helper**

Supprimer sa boucle LuaLaTeX locale. Appeler le helper avec `tmp_path` et
exiger trois passes, master/log/fls/PDF/preflight/table, code `0`, `passed` et
zéro diagnostic. Toute indisponibilité reste un échec.

- [ ] **Step 6: Vérifier les deux orchestrations**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_assemble_manuel_observed.py \
  -k 'local_build_helper or orchestration_delegates_to_local_build_helper or exact_three_pass_order or controlled_environment' \
  -q -p no:cacheprovider
```

Expected: tout vert et aucune seconde boucle LuaLaTeX dans le test matriciel.

- [ ] **Step 7: Prouver qu'un timeout interdit toute promotion**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_assemble_manuel_observed.py \
  -k timeout_retains_artifacts_without_promotion -vv -p no:cacheprovider
```

Expected: PASS ; délai transmis exactement `300`, artefacts temporaires
conservés, zéro promotion/receipt/observed et canoniques byte-identiques.

- [ ] **Step 8: Rejouer l'historique assembleur complet**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_assemble_manuel_observed.py -q -p no:cacheprovider
```

Expected: historique et nouveaux tests passent, sans régression
sécurité/reproductibilité/atomicité/receipt.

### Task 6: Parser les diagnostics différés avec attribution bloquante

**Files:**
- Create: `Mathematiques/manuel-maths/scripts/overflow_diagnostics.py`
- Create: `Mathematiques/manuel-maths/tests/test_overflow_diagnostics.py`
- Modify: `Mathematiques/manuel-maths/scripts/assemble_manuel.py`

- [ ] **Step 1: Écrire les fixtures Red des quatre priorités**

Tester : diagnostic dans un objet ; dans une ouverture ; `Overfull \vbox`
après `NEXUS_OBJECT_END` puis shipout ; repli final ligne TeX/page absolue.
Ajouter `127.74112pt` de `TSPE-GEOMETRIE-ESPACE`. Le cas différé va au prochain
shipout, jamais à l'objet terminé. Tester collision, token inconnu et absence
de shipout/ligne/page comme erreurs bloquantes. Avec un faux helper, tester que
`capture-one` n'accepte qu'un build id et l'appelle exactement une fois ;
`finalize` ne compile jamais, refuse fragment manquant/dupliqué et exige les
quatre ids/hashes intermédiaires exacts. Tester aussi `build-final-one` : un
seul appel helper, refus d'une ligne `open`, preflight rouge ou diagnostic ;
`verify-final` ne compile pas et exige exactement quatre candidats verts sans
promotion canonique.

Tester aussi le registre ligne par ligne : `annotate` cible un fingerprint
unique et ne modifie que `cause`, `fix`, `test`; fingerprint/build/variante/
type/attribution/old_page/extrait restent identiques. `reconcile` compare un
replay d'un seul build, renseigne `new_page` depuis ce replay et passe `fixed`
seulement si le diagnostic a disparu. Il conserve `open` s'il persiste et
refuse disparition sans cause/fix/test, diagnostic nouveau, ligne perdue,
doublon ou transition `fixed -> open` silencieuse.

- [ ] **Step 2: Observer le Red du parseur absent**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_overflow_diagnostics.py -vv -p no:cacheprovider
```

Expected: API absente ; aucune fixture n'est xfail ou tolérée.

- [ ] **Step 3: Implémenter le modèle fermé**

Créer dataclasses immuables et parseur conservant type, magnitude, lignes,
page absolue, chapitre, rubrique, contexte, token résolu et extrait brut.
Appliquer objet → ouverture → attente vers prochain shipout → repli ligne/page.
Le fingerprint est le SHA-256 du JSON canonique incluant build, type,
magnitude, attribution et lignes. Chaque ligne porte explicitement
`canonical_path`, résolu depuis la table versionnée token → chemin suivi pour
un objet, ou le chemin source canonique du repli/ouverture. `unknown`,
collision ou token non résolu
lève `OverflowAttributionError` et donne code CLI `2`.

Implémenter `annotate` et `reconcile` comme transformations atomiques du JSON
et de sa vue Markdown. Chaque transition porte `transition_from`,
`transition_to`, `replay_build_id`, `replay_sha256` et `verified_at`; aucune
édition manuelle de `state` ou `new_page` n'est acceptée par `verify`.

- [ ] **Step 4: Définir la preuve versionnée**

Le CLI expose `capture-one`, qui compile exactement un `build_id` dans son
workdir et écrit un fragment fermé, puis `finalize`, qui exige les quatre
fragments et écrit `audit/wave0-green-p0-overflow-diagnostics.json` et sa vue
`.md` sans compiler. Le JSON fermé porte version, SHA de base, manifeste
intermédiaire et quatre hashes, outils, tables tokens par build, puis les champs
`fingerprint`, `variant`, `type`, `object_or_opening`, `old_page`, `new_page`,
`canonical_path`, `cause`, `fix`, `test`, `state`. Initialement `new_page`,
`cause`, `fix` et
`test` sont `null`, `state=open`, jamais `ignored`.

`build-final-one` réutilise le même helper pour exactement un build id, exige
table entièrement `fixed`, preflight `0` et zéro diagnostic, puis conserve le
candidat temporaire sans promouvoir. `verify-final` exige les quatre ids et
recalcule leurs hashes/preflights sans lancer LuaLaTeX.

- [ ] **Step 5: Rendre les tests verts et muter le vbox dans `tmp_path`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_overflow_diagnostics.py -q -p no:cacheprovider
```

Expected: tout vert. Le test de mutation construit une copie sous `tmp_path`,
déplace le vbox entre END et le marqueur suivant et prouve qu'il reste
attribué au prochain shipout ; aucun fichier suivi n'est édité.

- [ ] **Step 6: Rejouer les familles Python affectées**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_pdf_integrity.py \
  tests/test_assemble_manuel_observed.py \
  tests/test_overflow_diagnostics.py -q -p no:cacheprovider
git diff --check
```

Expected: tout vert ; la matrice réelle reste rouge avant corrections layout.

- [ ] **Step 7: Committer helper et attribution sans LaTeX de production**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
git status --short
python3 -m pytest Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  Mathematiques/manuel-maths/tests/test_overflow_diagnostics.py \
  Mathematiques/manuel-maths/tests/test_pdf_integrity.py -q -p no:cacheprovider
git add Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  Mathematiques/manuel-maths/scripts/overflow_diagnostics.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  Mathematiques/manuel-maths/tests/test_p0_overflow_artifact.py \
  Mathematiques/manuel-maths/tests/test_overflow_diagnostics.py
test "$(git diff --cached --name-only | sort)" = "$(printf '%s\n' \
  Mathematiques/manuel-maths/scripts/assemble_manuel.py \
  Mathematiques/manuel-maths/scripts/overflow_diagnostics.py \
  Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py \
  Mathematiques/manuel-maths/tests/test_overflow_diagnostics.py \
  Mathematiques/manuel-maths/tests/test_p0_overflow_artifact.py | sort)"
git diff --cached --check
git diff --cached --stat
git commit -m "[PYTHON] unifie le helper reproductible et attribue les diagnostics"
```

Expected: aucun `.cls`, `.sty`, contenu, PDF, audit visuel ou baseline.

### Task 7: Rejouer les quatre builds séparés et figer l'état avant

**Files:**
- Create: `Mathematiques/manuel-maths/scripts/overflow_visual_review.py`
- Create: `Mathematiques/manuel-maths/tests/test_overflow_visual_review.py`
- Create: `audit/wave0-green-p0-overflow-diagnostics.json`
- Create: `audit/wave0-green-p0-overflow-diagnostics.md`
- Create: `audit/visual-wave0-green-p0-overflow-2026-08-13/manifest.json`
- Create: `audit/visual-wave0-green-p0-overflow-2026-08-13/before/`

- [ ] **Step 1: Écrire Red le schéma et le producteur de preuve initiale**

Dans `test_overflow_visual_review.py`, exiger pour `prepare-initial` : lecture
des quatre fragments et du manifeste séparation ; exactement quatre artefacts ;
raster 150 dpi de chaque `old_page` et des pages QCM pilotées par la table ;
hashes PDF/images ; versions Poppler/Pillow/polices ; et ce schéma fermé :
`schema_version=1`, `artifact_identity=wave0-overflow-final`, quatre ids,
`diagnostic_pages`, `tool_versions`, `resolution_dpi=150`,
`decision={status: pending, approved_by: null, approved_at: null, role: null,
reservations: null}`, `baseline_updated=false`. Refuser fragment/hit/page
manquant, path hors racine, hash incohérent et statut pré-approuvé.

- [ ] **Step 2: Observer le Red du producteur absent**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_overflow_visual_review.py \
  -k 'initial_manifest or prepare_initial' -vv -p no:cacheprovider
```

Expected: FAIL sur module/sous-commande absents, pas sur une dépendance cachée.

- [ ] **Step 3: Implémenter `prepare-initial` et `verify-initial`**

Implémenter un seul producteur reproductible : chemins résolus sous les
racines autorisées, `pdftoppm` argumenté sans shell, Pillow pour les hashes,
JSON canonique écrit par temporaire puis `os.replace`. `prepare-initial`
rasterise et scelle le schéma ci-dessus ; `verify-initial` recalcule tous les
hashes et refuse tout champ/artefact non déclaré. Aucun build, approbation,
promotion, baseline ou preuve observée dans ces sous-commandes.

- [ ] **Step 4: Rendre le contrat initial vert**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_overflow_visual_review.py \
  -k 'initial_manifest or prepare_initial' -q -p no:cacheprovider
```

Expected: PASS, y compris mutations hash/path/page/statut.

- [ ] **Step 5: Committer le producteur avant toute preuve produite**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
git status --short
python3 -m pytest Mathematiques/manuel-maths/tests/test_overflow_visual_review.py \
  -k 'initial_manifest or prepare_initial' -q -p no:cacheprovider
git add Mathematiques/manuel-maths/scripts/overflow_visual_review.py \
  Mathematiques/manuel-maths/tests/test_overflow_visual_review.py
test "$(git diff --cached --name-only | sort)" = "$(printf '%s\n' \
  Mathematiques/manuel-maths/scripts/overflow_visual_review.py \
  Mathematiques/manuel-maths/tests/test_overflow_visual_review.py | sort)"
git diff --cached --check
git diff --cached --stat
git commit -m "[PYTHON] verrouille la preuve visuelle overflow initiale"
```

Expected: outil/tests seuls, arbre hors preuves inchangé.

- [ ] **Step 6: Capturer `1SPE:eleve` par le helper commun**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py capture-one \
  --build-id '1SPE:eleve' \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --work-dir build/wave0-overflow-diagnostics/1SPE-eleve \
  --fragment build/wave0-overflow-diagnostics/1SPE-eleve.json
```

Expected: une compilation à trois passes ; préflight rouge avant `pdffonts`,
artefacts conservés et PDF au `after_sha256` intermédiaire exact.

- [ ] **Step 7: Capturer `1SPE:professeur`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py capture-one \
  --build-id '1SPE:professeur' \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --work-dir build/wave0-overflow-diagnostics/1SPE-professeur \
  --fragment build/wave0-overflow-diagnostics/1SPE-professeur.json
```

Expected: une compilation, dette attribuée, artefacts conservés et hash exact.

- [ ] **Step 8: Capturer `TSPE_2026_2027:eleve`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py capture-one \
  --build-id 'TSPE_2026_2027:eleve' \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --work-dir build/wave0-overflow-diagnostics/TSPE_2026_2027-eleve \
  --fragment build/wave0-overflow-diagnostics/TSPE_2026_2027-eleve.json
```

Expected: une compilation, dette attribuée, artefacts conservés et hash exact.

- [ ] **Step 9: Capturer `TSPE_2026_2027:professeur`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py capture-one \
  --build-id 'TSPE_2026_2027:professeur' \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --work-dir build/wave0-overflow-diagnostics/TSPE_2026_2027-professeur \
  --fragment build/wave0-overflow-diagnostics/TSPE_2026_2027-professeur.json
```

Expected: une compilation, dette attribuée, artefacts conservés et hash exact.

- [ ] **Step 10: Finaliser la table sans recompiler**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py finalize \
  --fragments build/wave0-overflow-diagnostics \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
  --markdown ../../audit/wave0-green-p0-overflow-diagnostics.md
```

Expected: exactement quatre fragments et quatre hashes `after_sha256`; sinon
arrêt avant toute correction.

- [ ] **Step 11: Vérifier exhaustivité et absence d'inconnus**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py verify \
  --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
  --require-state open --require-no-unknown
```

Expected: `0`, quatre variantes, comptes frais après split et attribution de
chaque diagnostic. Aucun nombre historique non nul ne devient oracle.

- [ ] **Step 12: Produire les rasters et le manifeste initial par l'outil testé**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_visual_review.py prepare-initial \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --diagnostics ../../audit/wave0-green-p0-overflow-diagnostics.json \
  --fragments build/wave0-overflow-diagnostics \
  --output ../../audit/visual-wave0-green-p0-overflow-2026-08-13 --dpi 150
python3 scripts/overflow_visual_review.py verify-initial \
  --manifest ../../audit/visual-wave0-green-p0-overflow-2026-08-13/manifest.json
```

Expected: codes `0`, quatre hashes intermédiaires, toutes pages pilotées,
images/hash/outils complets, décision `pending`, baseline false.

- [ ] **Step 13: Committer la preuve initiale séparément**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
git status --short
python3 Mathematiques/manuel-maths/scripts/overflow_diagnostics.py verify \
  --json audit/wave0-green-p0-overflow-diagnostics.json \
  --require-state open --require-no-unknown
python3 Mathematiques/manuel-maths/scripts/overflow_visual_review.py verify-initial \
  --manifest audit/visual-wave0-green-p0-overflow-2026-08-13/manifest.json
git add audit/wave0-green-p0-overflow-diagnostics.json \
  audit/wave0-green-p0-overflow-diagnostics.md \
  audit/visual-wave0-green-p0-overflow-2026-08-13/manifest.json \
  audit/visual-wave0-green-p0-overflow-2026-08-13/before
while IFS= read -r path; do
  case "$path" in
    audit/wave0-green-p0-overflow-diagnostics.json|\
    audit/wave0-green-p0-overflow-diagnostics.md|\
    audit/visual-wave0-green-p0-overflow-2026-08-13/manifest.json|\
    audit/visual-wave0-green-p0-overflow-2026-08-13/before/*) ;;
    *) printf 'staged interdit: %s\n' "$path" >&2; exit 1 ;;
  esac
done < <(git diff --cached --name-only)
git diff --cached --check
git diff --cached --stat
git commit -m "[AUDIT] attribue les débordements après séparation"
```

Expected: preuve/images avant seules ; aucun correctif, PDF ou baseline.

## Chunk 3: Corriger par cause, prouver visuellement et versionner

### Task 8: Corriger la largeur des folios du sommaire

**Files:**
- Create: `Mathematiques/manuel-maths/tests/test_p0_overflow_layout.py`
- Modify: `Mathematiques/manuel-maths/gabarits/nexus-pages-froides.sty`
- Modify: `audit/wave0-green-p0-overflow-diagnostics.json`
- Modify: `audit/wave0-green-p0-overflow-diagnostics.md`

- [ ] **Step 1: Écrire la fixture Red des pages à trois chiffres**

Compiler trois passes un mini-sommaire avec folios `99`, `100`, `999` en
chargeant vraie classe/charte et exiger zéro Overfull. Le helper de fixture
échoue si LuaLaTeX/config/timeout manque et conserve log/fls/PDF dans tmp.

- [ ] **Step 2: Observer le dépassement de 0.95421 pt**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_p0_overflow_layout.py \
  -k three_digit_toc_page_numbers -vv -p no:cacheprovider
```

Expected: Red sur le folio à trois chiffres, cohérent avec le sommaire tracé.

- [ ] **Step 3: Appliquer le correctif local au sommaire**

Dans l'entrée `tocline` de chapitre, ajouter
`pagenumberwidth=2.4em`. Ne changer ni `numwidth=11mm`, corps, marges,
interligne, densité, intitulés ou sections. Si la fixture prouve une autre
cause, arrêter et documenter l'hypothèse plutôt qu'élargir le correctif.

- [ ] **Step 4: Rendre la fixture sommaire verte**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_p0_overflow_layout.py \
  -k three_digit_toc_page_numbers -q -p no:cacheprovider
```

Expected: PASS, contenu conservé et zéro `0.95421pt`.

- [ ] **Step 5: Rejouer le build `1SPE-eleve` après le sommaire**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[1SPE-eleve]' -vv -p no:cacheprovider
```

Expected: la famille `0.95421pt` a disparu du log ; les autres familles
inventoriées peuvent encore rendre ce cas rouge.

- [ ] **Step 6: Rejouer le build `1SPE-professeur` après le sommaire**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[1SPE-professeur]' -vv -p no:cacheprovider
```

Expected: aucune occurrence `0.95421pt`; autres dettes encore rouges permises.

- [ ] **Step 7: Rejouer le build `TSPE_2026_2027-eleve` après le sommaire**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[TSPE_2026_2027-eleve]' -vv -p no:cacheprovider
```

Expected: aucune occurrence `0.95421pt`; autres dettes encore rouges permises.

- [ ] **Step 8: Rejouer le build `TSPE_2026_2027-professeur` après le sommaire**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[TSPE_2026_2027-professeur]' -vv -p no:cacheprovider
```

Expected: aucune occurrence `0.95421pt`; autres dettes encore rouges permises.

- [ ] **Step 9: Persister le replay sommaire `1SPE:eleve`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py capture-one \
  --build-id '1SPE:eleve' \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --work-dir build/wave0-overflow-after-toc/1SPE-eleve \
  --fragment build/wave0-overflow-after-toc/1SPE-eleve.json
```

Expected: un fragment frais, sans nouveau diagnostic.

- [ ] **Step 10: Persister le replay sommaire `1SPE:professeur`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py capture-one \
  --build-id '1SPE:professeur' \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --work-dir build/wave0-overflow-after-toc/1SPE-professeur \
  --fragment build/wave0-overflow-after-toc/1SPE-professeur.json
```

Expected: un fragment frais, sans nouveau diagnostic.

- [ ] **Step 11: Persister le replay sommaire `TSPE_2026_2027:eleve`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py capture-one \
  --build-id 'TSPE_2026_2027:eleve' \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --work-dir build/wave0-overflow-after-toc/TSPE_2026_2027-eleve \
  --fragment build/wave0-overflow-after-toc/TSPE_2026_2027-eleve.json
```

Expected: un fragment frais, sans nouveau diagnostic.

- [ ] **Step 12: Persister le replay sommaire `TSPE_2026_2027:professeur`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py capture-one \
  --build-id 'TSPE_2026_2027:professeur' \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --work-dir build/wave0-overflow-after-toc/TSPE_2026_2027-professeur \
  --fragment build/wave0-overflow-after-toc/TSPE_2026_2027-professeur.json
```

Expected: un fragment frais, sans nouveau diagnostic.

- [ ] **Step 13: Annoter puis réconcilier la cause sommaire ligne par ligne**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
mapfile -t toc_fingerprints < <(python3 - <<'PY'
import json
from pathlib import Path
payload = json.loads(Path('../../audit/wave0-green-p0-overflow-diagnostics.json').read_text(encoding='utf-8'))
print('\n'.join(row['fingerprint'] for row in payload['diagnostics'] if row['magnitude'] == '0.95421pt' and row['state'] == 'open'))
PY
)
test "${#toc_fingerprints[@]}" -gt 0
for fingerprint in "${toc_fingerprints[@]}"; do
  python3 scripts/overflow_diagnostics.py annotate \
    --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
    --markdown ../../audit/wave0-green-p0-overflow-diagnostics.md \
    --fingerprint "$fingerprint" \
    --cause toc-page-number-box-too-narrow \
    --fix 'chapter pagenumberwidth=2.4em' \
    --test 'tests/test_p0_overflow_layout.py::test_three_digit_toc_page_numbers'
done
for build_id in '1SPE:eleve' '1SPE:professeur' 'TSPE_2026_2027:eleve' 'TSPE_2026_2027:professeur'; do
  fragment="build/wave0-overflow-after-toc/${build_id//:/-}.json"
  python3 scripts/overflow_diagnostics.py reconcile \
    --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
    --markdown ../../audit/wave0-green-p0-overflow-diagnostics.md \
    --build-id "$build_id" --fragment "$fragment" --require-no-new
done
python3 scripts/overflow_diagnostics.py verify \
  --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
  --require-no-unknown
python3 - <<'PY'
import json
from pathlib import Path
payload = json.loads(Path('../../audit/wave0-green-p0-overflow-diagnostics.json').read_text(encoding='utf-8'))
rows = [row for row in payload['diagnostics'] if row.get('cause') == 'toc-page-number-box-too-narrow']
assert rows and all(row['state'] == 'fixed' and isinstance(row['new_page'], int) for row in rows)
assert not [row for row in payload['diagnostics'] if row['magnitude'] == '0.95421pt' and row['state'] == 'open']
assert not payload.get('new_diagnostics', [])
PY
```

Expected: tous les fingerprints sommaire annotés individuellement sont
absents des replays et `fixed`; aucune nouvelle ligne n'apparaît, même si
d'autres dettes restent `open`.

- [ ] **Step 14: Committer la cause sommaire**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
git status --short
python3 -m pytest Mathematiques/manuel-maths/tests/test_p0_overflow_layout.py \
  -k three_digit_toc_page_numbers -q -p no:cacheprovider
git add Mathematiques/manuel-maths/gabarits/nexus-pages-froides.sty \
  Mathematiques/manuel-maths/tests/test_p0_overflow_layout.py \
  audit/wave0-green-p0-overflow-diagnostics.json \
  audit/wave0-green-p0-overflow-diagnostics.md
test "$(git diff --cached --name-only | sort)" = "$(printf '%s\n' \
  Mathematiques/manuel-maths/gabarits/nexus-pages-froides.sty \
  Mathematiques/manuel-maths/tests/test_p0_overflow_layout.py \
  audit/wave0-green-p0-overflow-diagnostics.json \
  audit/wave0-green-p0-overflow-diagnostics.md | sort)"
git diff --cached --check
git diff --cached --stat
git commit -m "[LATEX] élargit la boîte des folios du sommaire"
```

Expected: une cause et sa preuve, sans PDF ou baseline.

### Task 9: Rendre les huit grilles QCM diagnostics sécables

**Files:**
- Modify: `Mathematiques/manuel-maths/scripts/build_qcm_tex.py`
- Modify: `Mathematiques/manuel-maths/tests/test_qcm_source_unique.py`
- Modify: `Mathematiques/manuel-maths/tests/test_p0_overflow_layout.py`
- Modify: `Mathematiques/manuel-maths/chapitres/*/diagnostics/*-QCM-DIAGNOSTICS.tex`
- Modify: `audit/wave0-green-p0-overflow-diagnostics.json`
- Modify: `audit/wave0-green-p0-overflow-diagnostics.md`

- [ ] **Step 1: Écrire les tests Red du rendu professeur**

Pour les huit IDs de la spec séparation, exiger une liste descriptive sécable :
un bloc par question avec capacité/réponse, puis un item enveloppable par
distracteur/erreur/renvoi. Interdire tableau externe `{|c|c|c|l|}` et
sous-`tabular`. Vérifier conservation exacte depuis JSON ; rien n'est abrégé.

- [ ] **Step 2: Observer le Red structurel du générateur**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_qcm_source_unique.py \
  -k 'diagnostics_layout or qcm_diagnostics_preserves_json' \
  -vv -p no:cacheprovider
```

Expected: FAIL sur structure non sécable, sans compilation réelle groupée.

- [ ] **Step 3: Compiler la seule grille Suites et voir le Red layout**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_p0_overflow_layout.py \
  -k qcm_diagnostics_long_grid -vv -p no:cacheprovider
```

Expected: FAIL sur le log de la longue grille professeur.

- [ ] **Step 4: Corriger le générateur, jamais les dérivés à la main**

Produire la même information sous liste descriptive enveloppable et sécable.
Conserver META/ID/type `qcm_diagnostics`, ordre JSON, rubrique externe et
absence de `\clearpage` interne. Ne réduire ni corps ni contenu.

- [ ] **Step 5: Régénérer exactement les huit sorties séparées**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
for chapter in 1SPE-SUITES 1SPE-SECOND-DEGRE 1SPE-DERIVATION-LOCAL 1SPE-DERIVATION-GLOBAL 1SPE-EXPONENTIELLE 1SPE-PRODUIT-SCALAIRE 1SPE-VARIABLES-ALEATOIRES TSPE-CONTINUITE
do
  python3 scripts/build_qcm_tex.py --chap "$chapter"
  python3 scripts/build_qcm_tex.py --chap "$chapter" --check
done
```

Expected: huit générations/checks `0`; seuls diagnostics dérivés changent. Les
QCM élèves et JSON restent byte-identiques à la branche séparation.

- [ ] **Step 6: Rendre les tests structurels verts**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_qcm_source_unique.py \
  -k 'diagnostics_layout or qcm_diagnostics_preserves_json' \
  -q -p no:cacheprovider
```

Expected: PASS et contenu JSON exhaustif.

- [ ] **Step 7: Rendre la fixture longue QCM verte**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_p0_overflow_layout.py \
  -k qcm_diagnostics_long_grid -q -p no:cacheprovider
```

Expected: PASS, zéro hbox/vbox et texte complet.

- [ ] **Step 8: Rejouer le professeur `1SPE` seul**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[1SPE-professeur]' -vv -p no:cacheprovider
```

Expected: les sept grands hbox QCM 1SPE et vbox QCM ont disparu ; autres
familles encore ouvertes permises.

- [ ] **Step 9: Rejouer le professeur `TSPE_2026_2027` seul**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[TSPE_2026_2027-professeur]' -vv -p no:cacheprovider
```

Expected: la famille QCM TSPE a disparu ; autres familles ouvertes permises.

- [ ] **Step 10: Persister le replay QCM `1SPE:eleve`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py capture-one \
  --build-id '1SPE:eleve' \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --work-dir build/wave0-overflow-after-qcm/1SPE-eleve \
  --fragment build/wave0-overflow-after-qcm/1SPE-eleve.json
```

Expected: fragment frais, aucun diagnostic nouveau.

- [ ] **Step 11: Persister le replay QCM `1SPE:professeur`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py capture-one \
  --build-id '1SPE:professeur' \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --work-dir build/wave0-overflow-after-qcm/1SPE-professeur \
  --fragment build/wave0-overflow-after-qcm/1SPE-professeur.json
```

Expected: fragment frais, aucun diagnostic nouveau.

- [ ] **Step 12: Persister le replay QCM `TSPE_2026_2027:eleve`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py capture-one \
  --build-id 'TSPE_2026_2027:eleve' \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --work-dir build/wave0-overflow-after-qcm/TSPE_2026_2027-eleve \
  --fragment build/wave0-overflow-after-qcm/TSPE_2026_2027-eleve.json
```

Expected: fragment frais, aucun diagnostic nouveau.

- [ ] **Step 13: Persister le replay QCM `TSPE_2026_2027:professeur`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py capture-one \
  --build-id 'TSPE_2026_2027:professeur' \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --work-dir build/wave0-overflow-after-qcm/TSPE_2026_2027-professeur \
  --fragment build/wave0-overflow-after-qcm/TSPE_2026_2027-professeur.json
```

Expected: fragment frais, aucun diagnostic nouveau.

- [ ] **Step 14: Annoter puis réconcilier chaque fingerprint QCM**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
mapfile -t qcm_fingerprints < <(python3 - <<'PY'
import json
from pathlib import Path
payload = json.loads(Path('../../audit/wave0-green-p0-overflow-diagnostics.json').read_text(encoding='utf-8'))
print('\n'.join(row['fingerprint'] for row in payload['diagnostics'] if row.get('canonical_path', '').endswith('-QCM-DIAGNOSTICS.tex') and row['state'] == 'open'))
PY
)
test "${#qcm_fingerprints[@]}" -gt 0
for fingerprint in "${qcm_fingerprints[@]}"; do
  python3 scripts/overflow_diagnostics.py annotate \
    --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
    --markdown ../../audit/wave0-green-p0-overflow-diagnostics.md \
    --fingerprint "$fingerprint" \
    --cause qcm-diagnostics-nonbreakable-table \
    --fix 'render each question and distractor as breakable descriptive items' \
    --test 'tests/test_p0_overflow_layout.py::test_qcm_diagnostics_long_grid'
done
python3 scripts/overflow_diagnostics.py reconcile \
  --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
  --markdown ../../audit/wave0-green-p0-overflow-diagnostics.md \
  --build-id '1SPE:eleve' \
  --fragment build/wave0-overflow-after-qcm/1SPE-eleve.json --require-no-new
python3 scripts/overflow_diagnostics.py reconcile \
  --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
  --markdown ../../audit/wave0-green-p0-overflow-diagnostics.md \
  --build-id '1SPE:professeur' \
  --fragment build/wave0-overflow-after-qcm/1SPE-professeur.json --require-no-new
python3 scripts/overflow_diagnostics.py reconcile \
  --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
  --markdown ../../audit/wave0-green-p0-overflow-diagnostics.md \
  --build-id 'TSPE_2026_2027:eleve' \
  --fragment build/wave0-overflow-after-qcm/TSPE_2026_2027-eleve.json --require-no-new
python3 scripts/overflow_diagnostics.py reconcile \
  --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
  --markdown ../../audit/wave0-green-p0-overflow-diagnostics.md \
  --build-id 'TSPE_2026_2027:professeur' \
  --fragment build/wave0-overflow-after-qcm/TSPE_2026_2027-professeur.json --require-no-new
python3 scripts/overflow_diagnostics.py verify \
  --json ../../audit/wave0-green-p0-overflow-diagnostics.json --require-no-unknown
python3 - <<'PY'
import json
from pathlib import Path
payload = json.loads(Path('../../audit/wave0-green-p0-overflow-diagnostics.json').read_text(encoding='utf-8'))
rows = [row for row in payload['diagnostics'] if row.get('cause') == 'qcm-diagnostics-nonbreakable-table']
assert rows and all(row['state'] == 'fixed' and isinstance(row['new_page'], int) for row in rows)
assert not [row for row in payload['diagnostics'] if row.get('canonical_path', '').endswith('-QCM-DIAGNOSTICS.tex') and row['state'] == 'open']
assert not payload.get('new_diagnostics', [])
PY
```

Expected: seuls les fingerprints QCM disparaissent et passent `fixed` avec
`new_page`; aucun diagnostic nouveau malgré les autres dettes encore ouvertes.

- [ ] **Step 15: Committer la cause QCM**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
git status --short
python3 -m pytest Mathematiques/manuel-maths/tests/test_qcm_source_unique.py \
  Mathematiques/manuel-maths/tests/test_p0_overflow_layout.py \
  -k 'diagnostics_layout or qcm_diagnostics_preserves_json or qcm_diagnostics_long_grid' \
  -q -p no:cacheprovider
git add Mathematiques/manuel-maths/scripts/build_qcm_tex.py \
  Mathematiques/manuel-maths/tests/test_qcm_source_unique.py \
  Mathematiques/manuel-maths/tests/test_p0_overflow_layout.py \
  Mathematiques/manuel-maths/chapitres/1SPE-SUITES/diagnostics/1SPE-SUITES-QCM-DIAGNOSTICS.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/diagnostics/1SPE-SECDEG-QCM-DIAGNOSTICS.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/diagnostics/1SPE-DERIVATION-LOCAL-QCM-DIAGNOSTICS.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/diagnostics/1SPE-DERIVATION-GLOBAL-QCM-DIAGNOSTICS.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/diagnostics/1SPE-EXPONENTIELLE-QCM-DIAGNOSTICS.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/diagnostics/1SPE-PRODUIT-SCALAIRE-QCM-DIAGNOSTICS.tex \
  Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/diagnostics/1SPE-VARALEA-QCM-DIAGNOSTICS.tex \
  Mathematiques/manuel-maths/chapitres/TSPE-CONTINUITE/diagnostics/TSPE-CONTINUITE-QCM-DIAGNOSTICS.tex \
  audit/wave0-green-p0-overflow-diagnostics.json \
  audit/wave0-green-p0-overflow-diagnostics.md
while IFS= read -r path; do
  case "$path" in
    Mathematiques/manuel-maths/scripts/build_qcm_tex.py|\
    Mathematiques/manuel-maths/tests/test_qcm_source_unique.py|\
    Mathematiques/manuel-maths/tests/test_p0_overflow_layout.py|\
    Mathematiques/manuel-maths/chapitres/*/diagnostics/*-QCM-DIAGNOSTICS.tex|\
    audit/wave0-green-p0-overflow-diagnostics.json|\
    audit/wave0-green-p0-overflow-diagnostics.md) ;;
    *) printf 'staged interdit: %s\n' "$path" >&2; exit 1 ;;
  esac
done < <(git diff --cached --name-only)
git diff --cached --check
git diff --cached --stat
git commit -m "[LATEX] rend les diagnostics QCM sécables"
```

Expected: générateur, huit dérivés, tests et preuve de cette cause, sans JSON
de contenu ou PDF.

### Task 10: Rendre les ouvertures longues adaptatives

**Files:**
- Modify: `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls`
- Modify: `Mathematiques/manuel-maths/tests/test_p0_overflow_layout.py`
- Modify: `audit/wave0-green-p0-overflow-diagnostics.json`
- Modify: `audit/wave0-green-p0-overflow-diagnostics.md`

- [ ] **Step 1: Écrire la fixture Red Géométrie et la non-régression Probabilités**

Construire depuis les vrais contrats les ouvertures `TSPE-PROBABILITES` et
`TSPE-GEOMETRIE-ESPACE`, capacités complètes, et compiler chacune trois passes.
Exiger zéro vbox et tous codes/libellés dans `pdftotext`. Géométrie doit
reproduire la famille observée `127.74112pt`. Probabilités est un cas de
non-régression : son attendu initial est dérivé de la ligne Task 7, jamais
présumé rouge. Paramétrer le node exact
`test_long_opening_has_no_overfull` avec les ids de chapitre.

- [ ] **Step 2: Caractériser `TSPE-PROBABILITES` sans présumer un Red**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_layout.py::test_long_opening_has_no_overfull[TSPE-PROBABILITES]' -vv -p no:cacheprovider
```

Expected: si Task 7 n'attribue aucun vbox à cette ouverture, PASS de
non-régression avec texte complet. Si Task 7 l'attribue, FAIL avec fingerprint
et magnitude exactement réconciliés dans la table ; toute autre sortie arrête.

- [ ] **Step 3: Observer le Red `TSPE-GEOMETRIE-ESPACE` seul**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_layout.py::test_long_opening_has_no_overfull[TSPE-GEOMETRIE-ESPACE]' -vv -p no:cacheprovider
```

Expected: FAIL sur `127.74112pt`, avec texte complet.

- [ ] **Step 4: Attribuer la cause avant toute édition de classe**

Comparer marqueurs ouverture/shipout, extrait brut, boîte TeX et fixture de
Géométrie. N'inclure Probabilités dans la cause que si Task 7 lui attribue un
diagnostic exact et que les preuves convergent. Ne modifier ni `nxcard` ni un
composant global à ce stade.

Expected: une hypothèse falsifiable unique pour le `127.74112pt` Géométrie et
la tcolorbox exacte qui refuse le repli. Si les causes diffèrent ou restent ambiguës, HARD STOP et addendum revu
selon Task 11 ; aucune correction conjecturale.

- [ ] **Step 5: Autoriser uniquement le repli local prouvé**

Si et seulement si Step 4 prouve que la tcolorbox des objectifs de
`\ouverturechapitre` est la cause commune, lui ajouter uniquement `breakable`.
Ne pas remplacer ni modifier `nxcard`, bandeau, marges, corps, interligne,
titres, densité ou contenu. Si la preuve désigne une autre boîte, arrêter et
faire approuver l'addendum exact avant toute édition.

- [ ] **Step 6: Rejouer la non-régression `TSPE-PROBABILITES`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_layout.py::test_long_opening_has_no_overfull[TSPE-PROBABILITES]' -q -p no:cacheprovider
```

Expected: PASS, texte complet, zéro vbox nouveau. Si elle était verte en
Task 7, aucun correctif ne lui est attribué dans le registre.

- [ ] **Step 7: Rendre la fixture `TSPE-GEOMETRIE-ESPACE` verte**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_layout.py::test_long_opening_has_no_overfull[TSPE-GEOMETRIE-ESPACE]' -q -p no:cacheprovider
```

Expected: PASS, texte complet, disparition de `127.74112pt`.

- [ ] **Step 8: Rejouer `TSPE_2026_2027-eleve` seul**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[TSPE_2026_2027-eleve]' -vv -p no:cacheprovider
```

Expected: vbox d'ouverture absents ; dettes de lignes restantes permises.

- [ ] **Step 9: Rejouer `TSPE_2026_2027-professeur` seul**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[TSPE_2026_2027-professeur]' -vv -p no:cacheprovider
```

Expected: vbox d'ouverture absents ; dettes de lignes restantes permises.

- [ ] **Step 10: Persister le replay ouverture `TSPE_2026_2027:eleve`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py capture-one \
  --build-id 'TSPE_2026_2027:eleve' \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --work-dir build/wave0-overflow-after-opening/TSPE_2026_2027-eleve \
  --fragment build/wave0-overflow-after-opening/TSPE_2026_2027-eleve.json
```

Expected: fragment frais, aucun diagnostic nouveau ni token inconnu.

- [ ] **Step 11: Persister le replay ouverture `TSPE_2026_2027:professeur`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py capture-one \
  --build-id 'TSPE_2026_2027:professeur' \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --work-dir build/wave0-overflow-after-opening/TSPE_2026_2027-professeur \
  --fragment build/wave0-overflow-after-opening/TSPE_2026_2027-professeur.json
```

Expected: fragment frais, aucun diagnostic nouveau ni token inconnu.

- [ ] **Step 12: Annoter puis réconcilier chaque ouverture prouvée**

Atteindre cette étape signifie que Step 4 a prouvé la même cause pour toute
ligne Probabilités éventuellement ouverte ; sinon le HARD STOP a déjà conduit
à l'addendum de Task 11. L'absence de ligne Probabilités reste le cas nominal.

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
mapfile -t opening_fingerprints < <(python3 - <<'PY'
import json
from pathlib import Path
payload = json.loads(Path('../../audit/wave0-green-p0-overflow-diagnostics.json').read_text(encoding='utf-8'))
ids = {'TSPE-GEOMETRIE-ESPACE', 'TSPE-PROBABILITES'}
rows = [row for row in payload['diagnostics'] if row.get('object_or_opening') in ids and row['state'] == 'open']
assert any(row.get('object_or_opening') == 'TSPE-GEOMETRIE-ESPACE' for row in rows)
print('\n'.join(row['fingerprint'] for row in rows))
PY
)
test "${#opening_fingerprints[@]}" -gt 0
for fingerprint in "${opening_fingerprints[@]}"; do
  python3 scripts/overflow_diagnostics.py annotate \
    --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
    --markdown ../../audit/wave0-green-p0-overflow-diagnostics.md \
    --fingerprint "$fingerprint" \
    --cause opening-objectives-box-nonbreakable \
    --fix 'add breakable to the local opening objectives tcolorbox' \
    --test 'tests/test_p0_overflow_layout.py::test_long_opening_has_no_overfull'
done
python3 scripts/overflow_diagnostics.py reconcile \
  --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
  --markdown ../../audit/wave0-green-p0-overflow-diagnostics.md \
  --build-id 'TSPE_2026_2027:eleve' \
  --fragment build/wave0-overflow-after-opening/TSPE_2026_2027-eleve.json \
  --require-no-new
python3 scripts/overflow_diagnostics.py reconcile \
  --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
  --markdown ../../audit/wave0-green-p0-overflow-diagnostics.md \
  --build-id 'TSPE_2026_2027:professeur' \
  --fragment build/wave0-overflow-after-opening/TSPE_2026_2027-professeur.json \
  --require-no-new
python3 scripts/overflow_diagnostics.py verify \
  --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
  --require-no-unknown
python3 - <<'PY'
import json
from pathlib import Path
payload = json.loads(Path('../../audit/wave0-green-p0-overflow-diagnostics.json').read_text(encoding='utf-8'))
ids = {'TSPE-GEOMETRIE-ESPACE', 'TSPE-PROBABILITES'}
rows = [row for row in payload['diagnostics'] if row.get('cause') == 'opening-objectives-box-nonbreakable']
assert rows and all(row['state'] == 'fixed' and isinstance(row['new_page'], int) for row in rows)
assert not [row for row in payload['diagnostics'] if row.get('object_or_opening') in ids and row['state'] == 'open']
assert not payload.get('new_diagnostics', [])
PY
```

Expected: chaque fingerprint d'ouverture réellement observé et prouvé est
absent du replay, annoté et `fixed`; aucune ligne nouvelle n'apparaît malgré
les autres dettes éventuellement encore `open`.

- [ ] **Step 13: Committer la cause ouverture prouvée**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
git status --short
python3 -m pytest Mathematiques/manuel-maths/tests/test_p0_overflow_layout.py \
  -k long_opening -q -p no:cacheprovider
git add Mathematiques/manuel-maths/gabarits/nexus-manuel.cls \
  Mathematiques/manuel-maths/tests/test_p0_overflow_layout.py \
  audit/wave0-green-p0-overflow-diagnostics.json \
  audit/wave0-green-p0-overflow-diagnostics.md
test "$(git diff --cached --name-only | sort)" = "$(printf '%s\n' \
  Mathematiques/manuel-maths/gabarits/nexus-manuel.cls \
  Mathematiques/manuel-maths/tests/test_p0_overflow_layout.py \
  audit/wave0-green-p0-overflow-diagnostics.json \
  audit/wave0-green-p0-overflow-diagnostics.md | sort)"
git diff --cached --check
git diff --cached --stat
git commit -m "[LATEX] replie les ouvertures longues dans le flux"
```

Expected: classe Mathématiques, fixtures et preuve seulement ; NSI/baseline
intacts.

### Task 11: Corriger chaque ligne mathématique insécable restante

**Files:**
- Create if debt remains: `docs/superpowers/plans/2026-08-13-green-p0-overflow-preflight-diagnostic-addendum.md`
- Modify: `audit/wave0-green-p0-overflow-diagnostics.json`
- Modify: `audit/wave0-green-p0-overflow-diagnostics.md`

- [ ] **Step 1: Rejouer `1SPE:eleve` après les correctifs partagés**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py capture-one \
  --build-id '1SPE:eleve' \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --work-dir build/wave0-overflow-after-shared-fixes/1SPE-eleve \
  --fragment build/wave0-overflow-after-shared-fixes/1SPE-eleve.json
```

Expected: une compilation ; fragment sans token inconnu.

- [ ] **Step 2: Rejouer `1SPE:professeur` après les correctifs partagés**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py capture-one \
  --build-id '1SPE:professeur' \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --work-dir build/wave0-overflow-after-shared-fixes/1SPE-professeur \
  --fragment build/wave0-overflow-after-shared-fixes/1SPE-professeur.json
```

Expected: une compilation ; fragment sans token inconnu.

- [ ] **Step 3: Rejouer `TSPE_2026_2027:eleve` après les correctifs partagés**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py capture-one \
  --build-id 'TSPE_2026_2027:eleve' \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --work-dir build/wave0-overflow-after-shared-fixes/TSPE_2026_2027-eleve \
  --fragment build/wave0-overflow-after-shared-fixes/TSPE_2026_2027-eleve.json
```

Expected: une compilation ; fragment sans token inconnu.

- [ ] **Step 4: Rejouer `TSPE_2026_2027:professeur` après les correctifs partagés**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py capture-one \
  --build-id 'TSPE_2026_2027:professeur' \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --work-dir build/wave0-overflow-after-shared-fixes/TSPE_2026_2027-professeur \
  --fragment build/wave0-overflow-after-shared-fixes/TSPE_2026_2027-professeur.json
```

Expected: une compilation ; fragment sans token inconnu.

- [ ] **Step 5: Réconcilier les quatre fragments sans réinitialiser le registre**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py reconcile \
  --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
  --markdown ../../audit/wave0-green-p0-overflow-diagnostics.md \
  --build-id '1SPE:eleve' \
  --fragment build/wave0-overflow-after-shared-fixes/1SPE-eleve.json \
  --require-no-new
python3 scripts/overflow_diagnostics.py reconcile \
  --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
  --markdown ../../audit/wave0-green-p0-overflow-diagnostics.md \
  --build-id '1SPE:professeur' \
  --fragment build/wave0-overflow-after-shared-fixes/1SPE-professeur.json \
  --require-no-new
python3 scripts/overflow_diagnostics.py reconcile \
  --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
  --markdown ../../audit/wave0-green-p0-overflow-diagnostics.md \
  --build-id 'TSPE_2026_2027:eleve' \
  --fragment build/wave0-overflow-after-shared-fixes/TSPE_2026_2027-eleve.json \
  --require-no-new
python3 scripts/overflow_diagnostics.py reconcile \
  --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
  --markdown ../../audit/wave0-green-p0-overflow-diagnostics.md \
  --build-id 'TSPE_2026_2027:professeur' \
  --fragment build/wave0-overflow-after-shared-fixes/TSPE_2026_2027-professeur.json \
  --require-no-new
python3 scripts/overflow_diagnostics.py verify \
  --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
  --require-no-unknown
python3 - <<'PY'
import json
from pathlib import Path
payload = json.loads(Path('../../audit/wave0-green-p0-overflow-diagnostics.json').read_text(encoding='utf-8'))
assert not payload.get('new_diagnostics', [])
assert all(row['state'] in {'open', 'fixed'} for row in payload['diagnostics'])
assert all(row.get('cause') and row.get('fix') and row.get('test') for row in payload['diagnostics'] if row['state'] == 'fixed')
PY
```

Expected: les transitions antérieures sont conservées ligne par ligne ; toute
ligne restante est `open`, avec fingerprint, build, variante, token résolu,
chemin canonique, ligne et page, et aucun diagnostic nouveau.

- [ ] **Step 6: HARD STOP et écrire l'addendum exact si une dette reste**

Ne modifier aucune source LaTeX restante depuis ce plan générique. Pour chaque
ligne `open`, écrire dans l'addendum une Task distincte avec, sans placeholder :
fingerprint exact, chemin canonique et ligne, build/variante/page, extrait brut,
cause prouvée, node pytest exact, commande Red exacte et sortie attendue,
correction minimale exacte, commande Green exacte, replay d'un seul build et
message de commit atomique exact. Après le Green local, chaque Task doit donner
les commandes persistantes complètes et dans cet ordre : `capture-one` vers un
fragment propre de ce seul build ; `annotate --fingerprint ... --cause ...
--fix ... --test ...` pour chaque ligne exacte de la cause ; `reconcile
--build-id ... --fragment ... --require-no-new` ; `verify
--require-no-unknown` ; assertion Python que ces fingerprints ont disparu,
portent `new_page` et `state=fixed`, tandis que `new_diagnostics` reste vide.
Chaque commit d'addendum doit aussi imposer status, test exact, allowlist,
staging explicite, diff cached check/stat, message exact et contrôle
`git diff-tree` après commit. Trois hypothèses infructueuses imposent un arrêt
humain ; jamais `ignored`, tolérance ou contenu abrégé.

- [ ] **Step 7: Faire approuver et versionner l'addendum avant exécution**

Faire relire l'addendum complet par `plan-document-reviewer`, corriger tous les
findings, obtenir l'approbation humaine explicite, puis le committer seul avec
`[DOCS] planifie les corrections overflow diagnostiquées` :

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
git status --short
git diff --check -- docs/superpowers/plans/2026-08-13-green-p0-overflow-preflight-diagnostic-addendum.md
git add docs/superpowers/plans/2026-08-13-green-p0-overflow-preflight-diagnostic-addendum.md
test "$(git diff --cached --name-only)" = \
  docs/superpowers/plans/2026-08-13-green-p0-overflow-preflight-diagnostic-addendum.md
git diff --cached --check
git diff --cached --stat
git commit -m "[DOCS] planifie les corrections overflow diagnostiquées"
```

Exécuter ensuite
ses Tasks TDD exactes via `superpowers:executing-plans`. Ne reprendre Step 8
qu'après tous ses commits et replays terminés. Si aucune ligne n'est `open`,
consigner ce fait dans la table ; aucun addendum vide n'est créé.

- [ ] **Step 8: Obtenir le Green final `1SPE-eleve`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[1SPE-eleve]' -vv -p no:cacheprovider
```

Expected: PASS, trois passes, préflight `0`, zéro hbox/vbox.

- [ ] **Step 9: Obtenir le Green final `1SPE-professeur`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[1SPE-professeur]' -vv -p no:cacheprovider
```

Expected: PASS, trois passes, préflight `0`, zéro hbox/vbox.

- [ ] **Step 10: Obtenir le Green final `TSPE_2026_2027-eleve`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[TSPE_2026_2027-eleve]' -vv -p no:cacheprovider
```

Expected: PASS, trois passes, préflight `0`, zéro hbox/vbox.

- [ ] **Step 11: Obtenir le Green final `TSPE_2026_2027-professeur`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[TSPE_2026_2027-professeur]' -vv -p no:cacheprovider
```

Expected: PASS, trois passes, préflight `0`, zéro hbox/vbox.

- [ ] **Step 12: Fermer la table sans masquer de dette**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py verify \
  --json ../../audit/wave0-green-p0-overflow-diagnostics.json \
  --require-state fixed --require-no-unknown
```

Expected: `0`; chaque ligne initiale porte old/new page, cause, fix, test et
`fixed`, sans `ignored`.

## Chunk 4: Sceller la preuve visuelle, promouvoir et rejouer les gates

### Task 12: Produire le manifeste visuel immuable et tester sa mutation

**Files:**
- Modify: `Mathematiques/manuel-maths/scripts/overflow_visual_review.py`
- Modify: `Mathematiques/manuel-maths/tests/test_overflow_visual_review.py`
- Modify: `audit/visual-wave0-green-p0-overflow-2026-08-13/manifest.json`
- Create: `audit/visual-wave0-green-p0-overflow-2026-08-13/after/`
- Create: `audit/visual-wave0-green-p0-overflow-2026-08-13/diff/`
- Create: `audit/visual-wave0-green-p0-overflow-2026-08-13/contact-sheets/`
- Create: `audit/visual-wave0-green-p0-overflow-2026-08-13/diagnostic-pages.json`

- [ ] **Step 1: Étendre Red le manifeste initial au manifeste final fermé**

Exiger quatre PDF avant/final, chaque page calculée depuis la table, SHA-256 de
PDF/image/diff/planche, versions outils/polices, résolution, date,
approbateur/rôle/décision/réserves et `baseline_updated=false`. Refuser chemin
non canonique, artefact non listé, hash divergent, diagnostic sans avant/après
et promotion d'une décision non approuvée.

- [ ] **Step 2: Ajouter la mutation d'un octet**

Dans `tmp_path`, copier un PDF fixture approuvé, modifier un octet et exiger
`ManifestVerificationError`/code CLI `1`. Ne jamais muter le vrai candidat.

- [ ] **Step 3: Écrire le contrat Red complet de `approve`**

Avec des manifestes et artefacts sous `tmp_path`, ajouter les nodes exacts :

- `test_approve_rejects_incomplete_or_invalid_human_decision` refuse nom, rôle
  ou réserves absents, et toute décision autre que `approved`/`rejected`, code 2 ;
- `test_approve_seals_exact_human_fields_without_hash_changes` conserve tous
  les hashes, scelle exactement les chaînes reçues et `baseline_updated=false` ;
- `test_approve_rejects_artifact_drift` remplace un octet dans `tmp_path` et
  exige code 1 sans modifier le manifeste ;
- `test_no_command_auto_approves` prouve que prepare/verify/promote ne changent
  jamais `pending` et qu'une promotion pending est refusée code 1.

La date UTC est produite uniquement par `approve`; aucun test ne préremplit un
approbateur fictif dans le manifeste de production.

- [ ] **Step 4: Observer le Red de toutes les sous-commandes**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_overflow_visual_review.py -vv -p no:cacheprovider
```

Expected: sous-commandes finales absentes puis tests rouges sur
prepare/verify/approve/promote ; `prepare-initial`/`verify-initial` restent verts.

- [ ] **Step 5: Implémenter `prepare`, `verify`, `approve` et `promote`**

Conserver le même schéma/producteur initial. `prepare` lit quatre hashes
séparation et table, rasterise à 150 dpi avec
`pdftoppm`, fabrique diffs/planches via Pillow et écrit le manifeste trié. Il
inclut au minimum pages des huit QCM, deux ouvertures TSPE, toute page de
composant partagé et deux pages si pagination déplacée. `verify` recalcule les
hashes. `approve` exige les quatre champs humains, revérifie tous les artefacts,
conserve leurs hashes et scelle la date UTC sans jamais toucher
`baseline_updated=false`. `promote` accepte seulement les quatre chemins
canoniques, exige `approved`, puis remplace atomiquement avec les octets au hash
approuvé. Codes CLI fermés : `0` succès, `1` intégrité/état, `2` usage.

- [ ] **Step 6: Rendre les tests visuels et d'approbation verts**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_overflow_visual_review.py -q -p no:cacheprovider
```

Expected: tout vert, mutation incluse, approbation incomplète/dérive refusées,
champs humains exacts et promotion pré-approbation refusée.

- [ ] **Step 7: Committer l'outil visuel avant ses preuves**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
git status --short
python3 -m pytest Mathematiques/manuel-maths/tests/test_overflow_visual_review.py \
  -q -p no:cacheprovider
git add Mathematiques/manuel-maths/scripts/overflow_visual_review.py \
  Mathematiques/manuel-maths/tests/test_overflow_visual_review.py
test "$(git diff --cached --name-only | sort)" = "$(printf '%s\n' \
  Mathematiques/manuel-maths/scripts/overflow_visual_review.py \
  Mathematiques/manuel-maths/tests/test_overflow_visual_review.py | sort)"
git diff --cached --check
git diff --cached --stat
git commit -m "[PYTHON] complète le manifeste visuel overflow"
```

Expected: outil et tests seuls ; aucune image, décision, baseline ou PDF.

- [ ] **Step 8: Construire le candidat final `1SPE:eleve`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py build-final-one \
  --build-id '1SPE:eleve' \
  --output build/wave0-overflow-final-candidates/1SPE-eleve \
  --diagnostics ../../audit/wave0-green-p0-overflow-diagnostics.json
```

Expected: un candidat, trois passes, preflight `0`, zéro Overfull, sans
`--record-observed`; canonique intermédiaire non remplacé.

- [ ] **Step 9: Construire le candidat final `1SPE:professeur`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py build-final-one \
  --build-id '1SPE:professeur' \
  --output build/wave0-overflow-final-candidates/1SPE-professeur \
  --diagnostics ../../audit/wave0-green-p0-overflow-diagnostics.json
```

Expected: un candidat vert ; aucun canonique remplacé.

- [ ] **Step 10: Construire le candidat final `TSPE_2026_2027:eleve`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py build-final-one \
  --build-id 'TSPE_2026_2027:eleve' \
  --output build/wave0-overflow-final-candidates/TSPE_2026_2027-eleve \
  --diagnostics ../../audit/wave0-green-p0-overflow-diagnostics.json
```

Expected: un candidat vert ; aucun canonique remplacé.

- [ ] **Step 11: Construire le candidat final `TSPE_2026_2027:professeur`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py build-final-one \
  --build-id 'TSPE_2026_2027:professeur' \
  --output build/wave0-overflow-final-candidates/TSPE_2026_2027-professeur \
  --diagnostics ../../audit/wave0-green-p0-overflow-diagnostics.json
```

Expected: un candidat vert ; aucun canonique remplacé.

- [ ] **Step 12: Vérifier les quatre candidats sans recompiler**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_diagnostics.py verify-final \
  --root build/wave0-overflow-final-candidates \
  --diagnostics ../../audit/wave0-green-p0-overflow-diagnostics.json
```

Expected: exactement quatre build ids, quatre preflights `0`, zéro diagnostic
et aucun chemin canonique modifié.

- [ ] **Step 13: Générer images, diffs et planches**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_visual_review.py prepare \
  --intermediate-manifest ../../audit/visual-wave0-green-p0-separation-2026-08-13/manifest.json \
  --diagnostics ../../audit/wave0-green-p0-overflow-diagnostics.json \
  --before-root ../../audit/visual-wave0-green-p0-overflow-2026-08-13/before \
  --final-root build/wave0-overflow-final-candidates \
  --output ../../audit/visual-wave0-green-p0-overflow-2026-08-13 --dpi 150
python3 scripts/overflow_visual_review.py verify \
  --manifest ../../audit/visual-wave0-green-p0-overflow-2026-08-13/manifest.json \
  --allow-pending
```

Expected: `0`, manifeste `pending`, toutes cibles avant/après/diff/planches,
aucun changement dans `validations/` ou une baseline.

### Task 13: Pause obligatoire pour approbation humaine

**Files:**
- Review: `audit/visual-wave0-green-p0-overflow-2026-08-13/contact-sheets/`
- Modify only after decision: `audit/visual-wave0-green-p0-overflow-2026-08-13/manifest.json`

- [ ] **Step 1: Présenter la preuve sans promouvoir les PDF**

Fournir planches, diffs et `diagnostic-pages.json`. Demander explicitement
lisibilité, absence de coupe, hiérarchie, densité et continuité pédagogique,
avec nom, rôle et réserves.

- [ ] **Step 2: HARD STOP — attendre la réponse humaine**

Ne pas auto-approuver, éditer le statut, promouvoir les PDF, mettre à jour la
baseline ou poursuivre avant réponse explicite.

- [ ] **Step 3: Sceller uniquement la décision reçue**

Après approbation uniquement, saisir dans le terminal les valeurs exactes de
la réponse humaine ; `aucune` est une réserve explicite valide :

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
read -r -p 'Nom exact de l approbateur : ' overflow_approver
read -r -p 'Role exact : ' overflow_role
read -r -p 'Reservations exactes, ou aucune : ' overflow_reservations
test -n "$overflow_approver"
test -n "$overflow_role"
test -n "$overflow_reservations"
python3 Mathematiques/manuel-maths/scripts/overflow_visual_review.py approve \
  --manifest audit/visual-wave0-green-p0-overflow-2026-08-13/manifest.json \
  --approver "$overflow_approver" --role "$overflow_role" \
  --decision approved --reservations "$overflow_reservations"
```

Expected: statut approved, date UTC, identité/rôle/réserves exacts et baseline
false. Si rejet/changements demandés, ne pas promouvoir ; revenir à la cause.

- [ ] **Step 4: Vérifier l'immuabilité après approbation**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_visual_review.py verify \
  --manifest ../../audit/visual-wave0-green-p0-overflow-2026-08-13/manifest.json
```

Expected: `0`; toute modification candidat/image/diff/planche invalide.

- [ ] **Step 5: Committer l'audit sans PDF canonique**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
git status --short
python3 Mathematiques/manuel-maths/scripts/overflow_visual_review.py verify \
  --manifest audit/visual-wave0-green-p0-overflow-2026-08-13/manifest.json
git add audit/visual-wave0-green-p0-overflow-2026-08-13 \
  audit/wave0-green-p0-overflow-diagnostics.json \
  audit/wave0-green-p0-overflow-diagnostics.md
while IFS= read -r path; do
  case "$path" in
    audit/visual-wave0-green-p0-overflow-2026-08-13/*|\
    audit/wave0-green-p0-overflow-diagnostics.json|\
    audit/wave0-green-p0-overflow-diagnostics.md) ;;
    *) printf 'staged interdit: %s\n' "$path" >&2; exit 1 ;;
  esac
done < <(git diff --cached --name-only)
git diff --cached --check
git diff --cached --stat
git commit -m "[AUDIT] consigne la revue visuelle sans changer la baseline"
```

Expected: preuves/audit seulement ; aucun outil, test, PDF canonique ou
validation.

### Task 14: Promouvoir exactement les quatre PDF approuvés

**Files:**
- Modify: `Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf`
- Modify: `Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf`
- Modify: `Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf`
- Modify: `Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.pdf`

- [ ] **Step 1: Vérifier candidats et approbation une dernière fois**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_visual_review.py verify \
  --manifest ../../audit/visual-wave0-green-p0-overflow-2026-08-13/manifest.json
```

Expected: `0`, décision approved.

- [ ] **Step 2: Promouvoir atomiquement les quatre hashes approuvés**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 scripts/overflow_visual_review.py promote \
  --manifest ../../audit/visual-wave0-green-p0-overflow-2026-08-13/manifest.json \
  --candidate-root build/wave0-overflow-final-candidates --repository-root ../..
```

Expected: exactement quatre remplacements ; aucun log/master/receipt/manifeste
observé. Chaque canonique a le hash final approuvé.

- [ ] **Step 3: Vérifier qpdf, polices et hashes**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
for pdf in build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.pdf
do
  qpdf --check "$pdf"
  pdffonts "$pdf" | awk 'NR > 2 && NF { if ($(NF-4) != "yes") exit 1 } END { if (NR <= 2) exit 1 }'
done
python3 scripts/overflow_visual_review.py verify \
  --manifest ../../audit/visual-wave0-green-p0-overflow-2026-08-13/manifest.json \
  --canonical
```

Expected: qpdf/polices/manifeste verts, aucune police non incorporée.

- [ ] **Step 4: Rejouer les tests affectés sans compilation de manuel**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_pdf_integrity.py tests/test_assemble_manuel_observed.py \
  tests/test_overflow_diagnostics.py tests/test_qcm_source_unique.py \
  tests/test_overflow_visual_review.py tests/test_maquette_v5.py \
  -q -p no:cacheprovider
```

Expected: tout vert ; ces nodes utilisent runners/fixtures, pas la matrice
réelle quatre manuels.

- [ ] **Step 5: Rejouer le build promu `1SPE-eleve`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[1SPE-eleve]' -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 6: Rejouer le build promu `1SPE-professeur`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[1SPE-professeur]' -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 7: Rejouer le build promu `TSPE_2026_2027-eleve`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[TSPE_2026_2027-eleve]' -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 8: Rejouer le build promu `TSPE_2026_2027-professeur`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[TSPE_2026_2027-professeur]' -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 9: Committer seulement les quatre PDF approuvés**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
git status --short
python3 Mathematiques/manuel-maths/scripts/overflow_visual_review.py verify \
  --manifest audit/visual-wave0-green-p0-overflow-2026-08-13/manifest.json \
  --canonical
git add Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf \
  Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf \
  Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf \
  Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.pdf
test "$(git diff --cached --name-only | sort)" = "$(printf '%s\n' \
  Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf \
  Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf \
  Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf \
  Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.pdf | sort)"
git diff --cached --check
git diff --cached --stat
git commit -m "[PDF] régénère les éditions sans débordement"
```

Expected: quatre binaires uniquement, après le commit d'audit approuvé.

### Task 15: Vérifier les gates verts du lot et les rouges hors lot

**Files:**
- Read: `audit/wave0-green-p0-overflow-diagnostics.json`
- Read: `audit/visual-wave0-green-p0-overflow-2026-08-13/manifest.json`
- Do not modify: `audit/visual-baseline-review/`
- Do not modify: `Mathematiques/manuel-maths/validations/`

- [ ] **Step 1: Rejouer les gates unitaires du lot**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest tests/test_pdf_integrity.py \
  tests/test_overflow_diagnostics.py tests/test_overflow_visual_review.py \
  -q -p no:cacheprovider
```

Expected: tout vert ; fail-fast, attribution et manifeste intègre.

- [ ] **Step 2: Rejouer le gate réel `1SPE-eleve`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[1SPE-eleve]' -q -p no:cacheprovider
```

Expected: PASS, zéro diagnostic.

- [ ] **Step 3: Rejouer le gate réel `1SPE-professeur`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[1SPE-professeur]' -q -p no:cacheprovider
```

Expected: PASS, zéro diagnostic.

- [ ] **Step 4: Rejouer le gate réel `TSPE_2026_2027-eleve`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[TSPE_2026_2027-eleve]' -q -p no:cacheprovider
```

Expected: PASS, zéro diagnostic.

- [ ] **Step 5: Rejouer le gate réel `TSPE_2026_2027-professeur`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow/Mathematiques/manuel-maths
python3 -m pytest 'tests/test_p0_overflow_artifact.py::test_p0_real_manual_produces_no_overfull[TSPE_2026_2027-professeur]' -q -p no:cacheprovider
```

Expected: PASS, zéro diagnostic.

- [ ] **Step 6: Confirmer la dérive charte historique exacte**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
python3 - <<'PY'
import subprocess

completed = subprocess.run(
    ['python3', 'scripts/check_charte_sync.py'],
    check=False, capture_output=True, text=True,
)
assert completed.returncode == 1
assert completed.stderr == ''
assert completed.stdout.splitlines() == [
    'Dérive de charte détectée :',
    '- gabarits/nexus-manuel.cls',
    '- scripts/pdf_integrity.py',
]
print(completed.stdout, end='')
PY
```

Expected: code `1`, exactement `gabarits/nexus-manuel.cls` et
`scripts/pdf_integrity.py`. Ne pas copier vers NSI ni convertir ce rouge.

- [ ] **Step 7: Verrouiller la sortie exacte du gate `--check`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
python3 - <<'PY'
import json
import subprocess

completed = subprocess.run(
    ['python3', 'scripts/inventory_collection.py', '--check', '--require-clean'],
    check=False, capture_output=True, text=True,
)
payload = json.loads(completed.stdout)
assert completed.returncode == 3
assert completed.stderr == ''
assert payload == {
    'blocker_count': 1,
    'dimensions': {
        'execution': 'not_covered', 'mathematics': 'not_covered',
        'pedagogy': 'not_covered', 'print': 'not_covered',
        'regulation': 'not_covered', 'structure': 'failed',
        'visual': 'not_covered',
    },
    'exit_code': 3,
    'gate': 'check',
    'reasons': ['check_error:source_digest du manifeste de build incohérent'],
    'success': False,
}
print(completed.stdout, end='')
PY
```

Expected: JSON canonique ci-dessus, code `3`, une raison exacte. Toute raison
différente arrête le lot ; ne pas régénérer le manifeste de build.

- [ ] **Step 8: Verrouiller la sortie exacte de `--validate-model`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
python3 - <<'PY'
import json
import subprocess

completed = subprocess.run(
    ['python3', 'scripts/inventory_collection.py', '--validate-model'],
    check=False, capture_output=True, text=True,
)
payload = json.loads(completed.stdout)
assert completed.returncode == 6
assert completed.stderr == ''
assert payload['gate'] == 'validate-model'
assert payload['exit_code'] == 6 and payload['success'] is False
assert payload['dimensions']['structure'] == 'failed'
assert payload['reasons'] == [
    'inventaire:recalcul_impossible:source_digest du manifeste de build incohérent',
    'policy_gate:couverture active non recalculable:source_digest du manifeste de build incohérent',
]
assert payload['blocker_count'] == 2
print(completed.stdout, end='')
PY
```

Expected: code `6`, exactement les deux raisons triées ci-dessus. Toute dette
supplémentaire ou raison absente est un blocage, pas une sortie acceptable.

- [ ] **Step 9: Verrouiller la sortie exacte de `--fail-on-new`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
python3 - <<'PY'
import json
import subprocess

completed = subprocess.run(
    ['python3', 'scripts/inventory_collection.py', '--fail-on-new'],
    check=False, capture_output=True, text=True,
)
payload = json.loads(completed.stdout)
assert completed.returncode == 5
assert completed.stderr == ''
assert payload['gate'] == 'fail-on-new'
assert payload['exit_code'] == 5 and payload['success'] is False
assert payload['dimensions']['structure'] == 'failed'
assert payload['reasons'] == [
    'comparaison fingerprint-v1 impossible:source_digest du manifeste de build incohérent',
]
assert payload['blocker_count'] == 1
print(completed.stdout, end='')
PY
```

Expected: code `5`, une raison exacte ; aucune baseline n'est étendue.

- [ ] **Step 10: Verrouiller la sortie exacte de `--release-strict`**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
python3 - <<'PY'
import json
import subprocess

completed = subprocess.run(
    ['python3', 'scripts/inventory_collection.py', '--release-strict'],
    check=False, capture_output=True, text=True,
)
payload = json.loads(completed.stdout)
assert completed.returncode == 7
assert completed.stderr == ''
assert payload['gate'] == 'release-strict'
assert payload['exit_code'] == 7 and payload['success'] is False
assert payload['dimensions']['structure'] == 'failed'
assert payload['dimensions']['execution'] == 'failed'
assert payload['reasons'] == [
    'inventaire_indisponible:source_digest du manifeste de build incohérent',
]
assert payload['blocker_count'] == 1
print(completed.stdout, end='')
PY
```

Expected: code `7`, raison exacte ; verdict **NO-GO**.

- [ ] **Step 11: Rejouer l'oracle release sur le checkout d'intégration attesté**

Run uniquement si le checkout principal est propre et pointe sur
`integration/1spe-bo2026-traceability` :

```bash
cd /home/alaeddine/Documents/Manuels_Nexus
test "$(git branch --show-current)" = 'integration/1spe-bo2026-traceability'
test -z "$(git status --porcelain)"
python3 - <<'PY'
import json
import subprocess

completed = subprocess.run(
    [
        'python3', 'scripts/inventory_collection.py', '--check',
        '--release-strict', '--require-clean',
    ],
    check=False, capture_output=True, text=True,
)
payload = json.loads(completed.stdout)
assert completed.returncode == 7
assert completed.stderr == ''
assert payload['gate'] == 'release-strict'
assert payload['exit_code'] == 7 and payload['success'] is False
assert payload['blocker_count'] == 67
assert payload['dimensions'] == {
    'execution': 'failed', 'mathematics': 'not_covered',
    'pedagogy': 'not_covered', 'print': 'not_covered',
    'regulation': 'not_covered', 'structure': 'failed',
    'visual': 'not_covered',
}
required = {
    'dimension_non_couverte:mathematics',
    'dimension_non_couverte:pedagogy',
    'dimension_non_couverte:print',
    'dimension_non_couverte:regulation',
    'dimension_non_couverte:visual',
}
assert required <= set(payload['reasons'])
assert payload['reasons'] == sorted(set(payload['reasons']))
print(completed.stdout, end='')
PY
```

Expected: code `7`, `67` raisons canoniques imprimées, dimensions exactes.
Si le checkout attesté n'est pas propre/à cette branche, arrêter et demander
un checkout propre approuvé ; ne changer ni branche ni WIP automatiquement.

- [ ] **Step 12: Prouver absence de baseline/record observed**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
git diff green/p0-student-separation...HEAD -- audit/visual-baseline-review \
  Mathematiques/manuel-maths/validations audit/BUILD_MANIFEST.json
rg -n -- '--record-observed|baseline_updated' \
  audit/visual-wave0-green-p0-overflow-2026-08-13/manifest.json \
  Mathematiques/manuel-maths/scripts/overflow_diagnostics.py
```

Expected: diff vide ; uniquement `baseline_updated: false`; aucun recorder.

- [ ] **Step 13: Demander la revue indépendante de conformité**

Faire relire spec/TDD/gates/Git, quatre hashes, tokens 40 hex, zéro unknown,
décision humaine et absence d'affaiblissement. Corriger chaque blocage
atomiquement et rejouer son contrôle avant de demander le verdict final.

- [ ] **Step 14: Demander la revue indépendante qualité/PDF**

Avec un reviewer distinct, faire relire LaTeX, attribution, pages diagnostiques,
planches, qpdf, polices et promotion des quatre seuls hashes. Corriger chaque
blocage atomiquement et obtenir un verdict final explicite.

- [ ] **Step 15: Encadrer chaque commit de correction de revue par sa lane**

Pour chaque finding, choisir exactement une lane parmi `tests`, `python`,
`latex`, `audit`, `pdf`. Avant la production, ajouter ou resserrer dans un
fichier de test déjà prévu le node exact indiqué par le reviewer, le lancer et
observer le Red attendu ; appliquer ensuite le correctif minimal et obtenir le
Green du même node. Une correction exigeant un fichier nouveau, une lane
supplémentaire, un changement de baseline ou une modification hors allowlist
arrête la revue et requiert un addendum approuvé. Exécuter ensuite ce bloc dans
la même shell, en saisissant le node pytest exact déjà observé Green :

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
git status --short
test -z "$(git ls-files --others --exclude-standard)"
test -z "$(git diff --cached --name-only)"
read -r -p 'Lane exacte tests|python|latex|audit|pdf : ' review_lane
read -r -p 'Node pytest exact déjà Red puis Green : ' review_node
case "$review_lane" in
  tests)
    subject='[TESTS] corrige la revue overflow'
    stage_roots=(
      Mathematiques/manuel-maths/tests/test_pdf_integrity.py
      Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py
      Mathematiques/manuel-maths/tests/test_p0_overflow_artifact.py
      Mathematiques/manuel-maths/tests/test_overflow_diagnostics.py
      Mathematiques/manuel-maths/tests/test_p0_overflow_layout.py
      Mathematiques/manuel-maths/tests/test_qcm_source_unique.py
      Mathematiques/manuel-maths/tests/test_overflow_visual_review.py
    ) ;;
  python)
    subject='[PYTHON] corrige la revue overflow'
    stage_roots=(
      Mathematiques/manuel-maths/scripts/assemble_manuel.py
      Mathematiques/manuel-maths/scripts/overflow_diagnostics.py
      Mathematiques/manuel-maths/scripts/overflow_visual_review.py
      Mathematiques/manuel-maths/scripts/build_qcm_tex.py
      Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py
      Mathematiques/manuel-maths/tests/test_overflow_diagnostics.py
      Mathematiques/manuel-maths/tests/test_overflow_visual_review.py
      Mathematiques/manuel-maths/tests/test_qcm_source_unique.py
    ) ;;
  latex)
    subject='[LATEX] corrige la revue overflow'
    stage_roots=(
      Mathematiques/manuel-maths/gabarits/nexus-manuel.cls
      Mathematiques/manuel-maths/gabarits/nexus-pages-froides.sty
      Mathematiques/manuel-maths/chapitres
      Mathematiques/manuel-maths/tests/test_p0_overflow_layout.py
      Mathematiques/manuel-maths/tests/test_qcm_source_unique.py
      audit/wave0-green-p0-overflow-diagnostics.json
      audit/wave0-green-p0-overflow-diagnostics.md
    ) ;;
  audit)
    subject='[AUDIT] corrige la revue overflow'
    stage_roots=(
      audit/wave0-green-p0-overflow-diagnostics.json
      audit/wave0-green-p0-overflow-diagnostics.md
      audit/visual-wave0-green-p0-overflow-2026-08-13
    ) ;;
  pdf)
    subject='[PDF] corrige la revue overflow'
    stage_roots=(
      Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf
      Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf
      Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf
      Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.pdf
    ) ;;
  *) printf 'lane interdite: %s\n' "$review_lane" >&2; exit 2 ;;
esac
test -n "$review_node"
python3 -m pytest "$review_node" -q -p no:cacheprovider
if test "$review_lane" = audit || test "$review_lane" = pdf; then
  python3 Mathematiques/manuel-maths/scripts/overflow_visual_review.py verify \
    --manifest audit/visual-wave0-green-p0-overflow-2026-08-13/manifest.json
fi
allowed_path() {
  case "$review_lane:$1" in
    tests:Mathematiques/manuel-maths/tests/test_pdf_integrity.py|\
    tests:Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py|\
    tests:Mathematiques/manuel-maths/tests/test_p0_overflow_artifact.py|\
    tests:Mathematiques/manuel-maths/tests/test_overflow_diagnostics.py|\
    tests:Mathematiques/manuel-maths/tests/test_p0_overflow_layout.py|\
    tests:Mathematiques/manuel-maths/tests/test_qcm_source_unique.py|\
    tests:Mathematiques/manuel-maths/tests/test_overflow_visual_review.py|\
    python:Mathematiques/manuel-maths/scripts/assemble_manuel.py|\
    python:Mathematiques/manuel-maths/scripts/overflow_diagnostics.py|\
    python:Mathematiques/manuel-maths/scripts/overflow_visual_review.py|\
    python:Mathematiques/manuel-maths/scripts/build_qcm_tex.py|\
    python:Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py|\
    python:Mathematiques/manuel-maths/tests/test_overflow_diagnostics.py|\
    python:Mathematiques/manuel-maths/tests/test_overflow_visual_review.py|\
    python:Mathematiques/manuel-maths/tests/test_qcm_source_unique.py|\
    latex:Mathematiques/manuel-maths/gabarits/nexus-manuel.cls|\
    latex:Mathematiques/manuel-maths/gabarits/nexus-pages-froides.sty|\
    latex:Mathematiques/manuel-maths/chapitres/*.tex|\
    latex:Mathematiques/manuel-maths/chapitres/*/*.tex|\
    latex:Mathematiques/manuel-maths/chapitres/*/*/*.tex|\
    latex:Mathematiques/manuel-maths/tests/test_p0_overflow_layout.py|\
    latex:Mathematiques/manuel-maths/tests/test_qcm_source_unique.py|\
    latex:audit/wave0-green-p0-overflow-diagnostics.json|\
    latex:audit/wave0-green-p0-overflow-diagnostics.md|\
    audit:audit/wave0-green-p0-overflow-diagnostics.json|\
    audit:audit/wave0-green-p0-overflow-diagnostics.md|\
    audit:audit/visual-wave0-green-p0-overflow-2026-08-13/*|\
    audit:audit/visual-wave0-green-p0-overflow-2026-08-13/*/*|\
    pdf:Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf|\
    pdf:Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf|\
    pdf:Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf|\
    pdf:Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.pdf) return 0 ;;
    *) return 1 ;;
  esac
}
while IFS= read -r path; do allowed_path "$path" || {
  printf 'working path interdit pour %s: %s\n' "$review_lane" "$path" >&2
  exit 1
}; done < <(git diff --name-only)
git add -u -- "${stage_roots[@]}"
test -n "$(git diff --cached --name-only)"
while IFS= read -r path; do allowed_path "$path" || {
  printf 'staged path interdit pour %s: %s\n' "$review_lane" "$path" >&2
  exit 1
}; done < <(git diff --cached --name-only)
git diff --cached --check
git diff --cached --stat
git commit -m "$subject"
test "$(git show -s --format=%s HEAD)" = "$subject"
while IFS= read -r path; do allowed_path "$path" || {
  printf 'commit path interdit pour %s: %s\n' "$review_lane" "$path" >&2
  exit 1
}; done < <(git diff-tree --no-commit-id --name-only -r HEAD)
git status --short
test -z "$(git status --porcelain)"
```

Expected: le node exact est Green ; le commit est non vide, mono-lane, porte
le message imposé et son `diff-tree` respecte la même allowlist. Répéter le
bloc pour chaque finding ; ne jamais amender un commit antérieur.

- [ ] **Step 16: Vérifier le worktree**

Run:

```bash
cd /home/alaeddine/Documents/Manuels_Nexus/.worktrees/green-p0-overflow
git status --short --branch
git diff --stat
git diff --check
git log --oneline --decorate green/p0-student-separation..HEAD
```

Expected: propre ; commits atomiques `[TESTS]`, `[PDF]`, `[PYTHON]`, `[AUDIT]`,
un ou plusieurs `[LATEX]`, `[AUDIT]`, puis `[PDF]`. Aucun merge/push forcé.

- [ ] **Step 17: Produire le compte rendu contractuel**

```text
ÉTAT (SHA retourné par git rev-parse HEAD)
Branche : green/p0-overflow
Phase : Green P0 overflow/preflight terminé, release encore NO-GO
Commits : liste exacte retournée par git log
Tests : commandes exactes et comptes observés
Gates verts : overfull 4/4, préflight, qpdf, polices, manifeste visuel
Gates rouges : charte-sync=1, check=3, validate-model=6, fail-on-new=5, release-strict=7 avec JSON ci-dessus
P0 ouverts : liste dérivée des 67 raisons release de l'oracle attesté
Décisions humaines : approbateur, rôle, date et réserves du manifeste
PR : URL exacte ou mention non créée
Prochaine action : intégrer selon l'orchestrateur sans déclarer la release publiable
```

Le verdict reste **NO-GO publication**. Métadonnées métier, signets, liens
globaux et balisage PDF ne font pas partie de ce plan.
