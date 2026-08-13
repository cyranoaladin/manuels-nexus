# README racine autosuffisant pour audit — Plan d'implémentation

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Créer un `README.md` racine autosuffisant, exact et audit-friendly qui explique le projet Nexus, son métier, son architecture, ses workflows et son état courant sans devenir une source d'autorité concurrente.

**Architecture:** Le README est un manuel d'audit en couches : résumé immédiat, description durable du système, puis état daté et procédure de reproduction. Les faits chiffrés sont attribués au SHA audité et les exigences renvoient à leur niveau d'autorité ; aucun générateur ni correctif métier n'est ajouté dans cette tranche.

**Tech Stack:** Markdown CommonMark/GitHub, Git, Bash, Python 3.12, scripts d'inventaire Nexus, outils CLI existants.

**Spécification approuvée :** `docs/superpowers/specs/2026-08-13-readme-racine-autosuffisant-design.md`

**État de départ :**

- branche `integration/1spe-bo2026-traceability` ;
- état métier audité `1d0c3fdaa24f17d938696b615d23373579042b95` ;
- rapport publié dans le commit `b5c6f9f113dc7be0b33765bb6229b6d4e6611467`
  (`audit/AUDIT_ETAT_PROJET_2026-08-13.md`) ;
- HEAD de conception au lancement du plan
  `d8fd14e1a1dccbd2beaccf21526061f8b1563d10` ;
- aucun `README.md` à la racine ;
- arbre propre après les commits de conception ;
- collection `NO-GO publication`.

---

## Cartographie des fichiers

### Fichier de livraison

- Create: `README.md` — portail autosuffisant pour auditeur, description du
  projet et instantané daté.

### Fichiers de conception et de plan

- Existing: `docs/superpowers/specs/2026-08-13-readme-racine-autosuffisant-design.md`.
- Create: `docs/superpowers/plans/2026-08-13-readme-racine-autosuffisant.md`.

### Sources à lire, jamais à modifier dans cette tranche

- `AGENTS.md` ;
- `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md` ;
- `docs/superpowers/specs/2026-08-12-finalisation-premium-six-manuels-design.md` ;
- `docs/codex/QUALITY_GATES.md` ;
- `docs/codex/CI_AUDIT_PHASE_0.md` ;
- `docs/codex/BUNDLE_INTEGRATION_REPORT.md` ;
- `audit/AUDIT_ETAT_PROJET_2026-08-13.md` ;
- `audit/INVENTAIRE_COLLECTION.json` et `.md` ;
- `audit/BUILD_MANIFEST.json` ;
- `audit/BUILD_PRODUCERS.yaml` ;
- `docs/programmes/PROGRAMMES_2026_2027.yaml` ;
- `Mathematiques/manuel-maths/scripts/assemble_manuel.py` ;
- `NSI/scripts/assemble_manuel.py` ;
- `Mathematiques/manuel-maths/Makefile` ;
- `NSI/Makefile` ;
- `pyproject.toml` ;
- `.github/workflows/*.yml`.

### Hors périmètre

- aucune correction de programme ;
- aucune correction de contenu ou de PDF ;
- aucune modification de charte ;
- aucun changement d'assembleur ou de gate ;
- aucune mise à jour de baseline ;
- aucune refonte des README disciplinaires ;
- aucun générateur du bloc d'état.

---

## Chunk 1: Préflight documentaire et contrat d'acceptation

### Task 1: Verrouiller l'état de départ et les preuves

**Files:**

- Read: `AGENTS.md`
- Read: `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md`
- Read: `audit/AUDIT_ETAT_PROJET_2026-08-13.md`
- Read: `audit/INVENTAIRE_COLLECTION.json`
- Read: `audit/BUILD_MANIFEST.json`
- Read: `docs/programmes/PROGRAMMES_2026_2027.yaml`
- Test: commandes shell en lecture seule

- [ ] **Step 1: Relever l'état Git obligatoire**

Run:

```bash
git status --short --branch
git rev-parse HEAD
git log --oneline --decorate -15
git diff --stat
git diff --check
```

Expected: branche d'intégration, aucun WIP inattendu, seulement le plan déjà
commité ou le fichier de plan en cours selon le point d'exécution.

- [ ] **Step 2: Versionner le plan seul**

Run:

```bash
set -e
git add docs/superpowers/plans/2026-08-13-readme-racine-autosuffisant.md
git diff --cached --check
git diff --cached --stat
git commit -m "[DOCS] ajoute le plan du README racine"
git status --short --branch
```

Expected: un commit contenant seulement le plan, puis un arbre propre.

- [ ] **Step 3: Prouver que le README racine n'existe pas encore**

Run:

```bash
test ! -e README.md
```

Expected: exit 0 avant implémentation.

- [ ] **Step 4: Recalculer les mesures utilisées dans le README**

Run:

```bash
python3 scripts/inventory_collection.py --check --require-clean
```

Expected: exit 0 sur l'arbre propre obtenu à l'étape précédente.

- [ ] **Step 5: Vérifier les interfaces de build documentées**

Run:

```bash
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py --help
python3 NSI/scripts/assemble_manuel.py --help
python3 - <<'PY'
import ast
from pathlib import Path

tree = ast.parse(Path("NSI/scripts/assemble_manuel.py").read_text(encoding="utf-8"))
variants = None
for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "VARIANTS":
                variants = ast.literal_eval(node.value)
assert variants is not None
assert {"eleve", "professeur"} <= set(variants)
PY
```

Expected: les interfaces exposent les sélecteurs de manuel/livre,
`--variant` et `--record-observed`; la constante NSI autorise notamment
`eleve` et `professeur` même si l'aide affiche seulement le métavariable
`VARIANT`.

- [ ] **Step 6: Vérifier la preuve officielle archivée pour 1NSI**

Run:

```bash
set -e
sha256sum --check <<'EOF'
6af0b9dea65d0fcfbc5de970cba25c9683db9ea1f3196bd725003bd7cc24e3fe  audit/sources/1nsi/legifrance-arrete-17-janvier-2019.html
EOF
rg -q 'MENE1901633A' audit/sources/1nsi/legifrance-arrete-17-janvier-2019.html
rg -q "spécialité de numérique et sciences informatiques de la classe de première" \
  audit/sources/1nsi/legifrance-arrete-17-janvier-2019.html
```

Expected: preuve archivée intacte, programme de spécialité NSI de Première et
NOR `MENE1901633A`. Le README donne aussi le lien officiel public
`https://www.education.gouv.fr/bo/19/Special1/MENE1901633A.htm`.

---

## Chunk 2: Rédaction du README

### Task 2: Poser la couche d'orientation

**Files:**

- Create: `README.md`
- Reference: `docs/superpowers/specs/2026-08-13-readme-racine-autosuffisant-design.md`
- Test: assertions shell et relecture indépendante

- [ ] **Step 1: Écrire l'en-tête et le statut immédiat**

Créer :

```markdown
# Manuels Nexus Réussite — Collection 2026-2027
## Statut immédiat
```

Exiger `NO-GO publication`, date, SHA, branche, lien vers l'audit et distinction
PDF/build observé/release.

- [ ] **Step 2: Écrire le résumé en 90 secondes**

Créer `## Le projet en 90 secondes` avec mission, six manuels, 51 chapitres,
2 860 objets, 12 PDF, 2 026 pages, 0 READY, 2 911 entrées non publiables,
67 bloqueurs `release-strict`, 0 build observé et les trois risques majeurs.

- [ ] **Step 3: Expliquer comment lire le portail**

Créer `## Comment lire ce README` et annoncer les trois couches : orientation,
système durable, état audité reproductible.

- [ ] **Step 4: Écrire la hiérarchie d'autorité**

Créer `## Hiérarchie d'autorité`, reprendre les sept niveaux contractuels et
préciser que le README est un portail daté, pas une nouvelle autorité.

- [ ] **Step 5: Vérifier la première couche**

Run:

```bash
rg -n '^# |^## (Statut immédiat|Le projet en 90 secondes|Comment lire ce README|Hiérarchie d.authorité)' README.md
rg -n 'NO-GO publication|1d0c3fda|b5c6f9f1|2 860|0 READY' README.md
```

Expected: toutes les sections et valeurs sont présentes.

### Task 3: Décrire le produit et sa logique métier

**Files:**

- Modify: `README.md`
- Reference: cahier des charges et spécification approuvée
- Test: assertions textuelles ciblées

- [ ] **Step 1: Écrire la mission et la définition du produit**

Créer `## Mission et définition du produit`; distinguer source éditoriale,
livrable PDF, preuve de build et release publiable.

- [ ] **Step 2: Écrire le tableau des six manuels**

Créer `## Les six manuels` avec une ligne par manuel et une ligne totalisant
51 chapitres, 2 860 objets, 12 PDF et 2 026 pages.

- [ ] **Step 3: Définir la condition de terminaison**

Créer `## Ce que signifie « terminé »` et lier complétude de contenu, validation
des statuts, build observé, préflight, comparaison élève/professeur, revue
visuelle et approbation humaine.

- [ ] **Step 4: Décrire la chaîne éditoriale**

Créer `## Logique métier de la chaîne éditoriale` avec le flux source officielle
→ registre → référentiel/contrat → objet `% META:` → assembleur → LuaLaTeX →
préflight/receipt → manifeste → inventaire/gates → revues → release.

- [ ] **Step 5: Décrire le modèle pédagogique Nexus**

Créer `## Modèle pédagogique Nexus` et énumérer exactement les onze étapes de
la boucle Nexus ainsi que les parcours de guidage et remédiation.

- [ ] **Step 6: Décrire un chapitre canonique**

Créer `## Architecture canonique d'un chapitre`; exposer les familles d'objets,
la cible d'exercices et les évaluations A/B sans déclarer la cible atteinte.

- [ ] **Step 7: Définir statuts, READY et variantes**

Créer séparément `## Statuts, READY et release` puis `## Variantes élève et
professeur`; inclure les statuts bloquants et toutes les interdictions élève.

- [ ] **Step 8: Vérifier la couche métier**

Run:

```bash
rg -n '^## (Mission|Les six manuels|Ce que signifie|Logique métier|Modèle pédagogique|Architecture canonique|Statuts|Variantes)' README.md
rg -n 'diagnostic|orientation|re-test|réactivation|transfert|aucun corrigé complet' README.md
```

Expected: les huit sections et les invariants métier sont présents.

### Task 4: Décrire réglementation, sources et architecture

**Files:**

- Modify: `README.md`
- Reference: registre, preuves officielles, assembleurs, manifests et charte
- Test: assertions textuelles et liens locaux

- [ ] **Step 1: Écrire les programmes officiels 2026-2027**

Créer `## Programmes officiels 2026-2027`; employer les NOR corrects, rendre
visibles l'erreur TSPE du registre et la lacune NOR/URL 1NSI, et qualifier les
sources d'épreuve non déposées. Le tableau doit inclure exactement : 1SPE
`MENE2602917A`, épreuve anticipée `MENE2515469N`, TSPE `MENE1921246A`, TCOMPL
`MENE1921265A`, TEXPERTES `MENE1921264A`, 1NSI `MENE1901633A` et TNSI
`MENE1921247A`.

- [ ] **Step 2: Qualifier enrichissements et spécificités NSI**

Créer `## Enrichissements hors programme` puis `## Spécificités NSI et code
Python`; distinguer exigible/approfondissement et rappeler parse, exécution et
comparaison des sorties Python.

- [ ] **Step 3: Écrire l'arborescence annotée**

Créer `## Arborescence du dépôt` avec uniquement des chemins existants et les
rôles de Mathématiques, NSI, scripts, tests, audit, docs et workflows CI.

- [ ] **Step 4: Décrire les sources et métadonnées**

Créer `## Architecture des sources`; expliquer objets `.tex`, `% META:`,
contrats YAML/JSON, schémas et corpus NSI `needs_review` non publiable.

- [ ] **Step 5: Décrire assembleurs et manifests**

Créer `## Assembleurs et manifests`; distinguer le littéral `CHAPITRES`/
`MANUAL_CHAPTERS` côté Mathématiques des manifests JSON 1NSI/TNSI.

- [ ] **Step 6: Décrire la charte v5/v6 réelle**

Créer `## Charte graphique v5/v6`; présenter classe, style, modules, pont,
extensions NSI, duplication physique et limites du gate de synchronisation.

- [ ] **Step 7: Décrire le pipeline de build et de preuve**

Créer `## Pipeline de build et de preuve`; distinguer build local et observé,
les trois passes LuaLaTeX, receipts, `BUILD_MANIFEST.json`, préflight et revues.

- [ ] **Step 8: Vérifier réglementation et architecture**

Run:

```bash
rg -n 'MENE2602917A|MENE2515469N|MENE1921246A|MENE1921265A|MENE1921264A|MENE1901633A|MENE1921247A|MENE1921262A|STMG' README.md
rg -n '^## (Arborescence|Architecture des sources|Assembleurs|Charte graphique|Pipeline)' README.md
```

Expected: références sensibles et sections d'architecture présentes.

### Task 5: Rendre le dépôt opérable

**Files:**

- Modify: `README.md`
- Reference: scripts `--help`, Makefiles et workflows CI
- Test: interfaces CLI existantes

- [ ] **Step 1: Écrire prérequis et installation**

Créer `## Prérequis et installation`; séparer outils minimaux et recommandés,
et interdire tout secret ou `.env` versionné.

- [ ] **Step 2: Documenter les builds locaux**

Créer `## Construire un manuel localement`; donner les commandes Mathématiques
et NSI prouvées, pour variantes élève et professeur, sans enregistrer de preuve.
Inclure exactement au moins ces exemples depuis la racine :

```bash
(cd Mathematiques/manuel-maths && \
  python3 scripts/assemble_manuel.py --manual 1SPE --variant eleve)
(cd NSI && \
  python3 scripts/assemble_manuel.py --book 1NSI --variant eleve)
```

- [ ] **Step 3: Documenter le build observé**

Créer `## Enregistrer un build observé`; expliquer `--record-observed`, ses
écritures de receipts/manifeste, la nécessité d'un arbre propre et de revue.
Inclure exactement au moins ces exemples depuis la racine :

```bash
(cd Mathematiques/manuel-maths && \
  python3 scripts/assemble_manuel.py --manual 1SPE --variant professeur --record-observed)
(cd NSI && \
  python3 scripts/assemble_manuel.py --book 1NSI --variant professeur --record-observed)
```

- [ ] **Step 4: Documenter tests et gates**

Créer `## Tests et gates`; donner les commandes existantes, expliquer les codes
non nuls et ne jamais transformer un gate rouge en succès documentaire.

- [ ] **Step 5: Documenter l'intégration continue**

Créer `## Intégration continue`; décrire les trois workflows, leurs triggers
réels et leurs angles morts actuels.

- [ ] **Step 6: Vérifier l'opérabilité**

Run:

```bash
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py --help \
  | grep -E -- '--manual|--variant|--record-observed'
python3 NSI/scripts/assemble_manuel.py --help \
  | grep -E -- '--book|--variant|--record-observed'
python3 - <<'PY'
from pathlib import Path

text = Path("README.md").read_text(encoding="utf-8")
for command in (
    "cd Mathematiques/manuel-maths &&",
    "cd NSI &&",
    "python3 scripts/assemble_manuel.py --manual 1SPE --variant eleve",
    "python3 scripts/assemble_manuel.py --book 1NSI --variant eleve",
    "python3 scripts/assemble_manuel.py --manual 1SPE --variant professeur --record-observed",
    "python3 scripts/assemble_manuel.py --book 1NSI --variant professeur --record-observed",
):
    assert command in text, command
PY
rg -n '^## (Prérequis|Construire|Enregistrer|Tests et gates|Intégration continue)' README.md
```

Expected: les interfaces et les cinq sections opératoires sont présentes.

### Task 6: Décrire gouvernance, état et passation

**Files:**

- Modify: `README.md`
- Reference: AGENTS, audit daté, décisions et documents applicables
- Test: marqueurs et assertions textuelles

- [ ] **Step 1: Écrire le workflow de contribution**

Créer `## Workflow obligatoire de contribution`; inclure brainstorming, plan
de pas 2–5 minutes, validation humaine, TDD pour le code, sous-agents sur tâches
indépendantes et vérification par preuves.

- [ ] **Step 2: Écrire revue, Git et approbations**

Créer `## Revue indépendante et approbation humaine` puis `## Git, commits et
interdictions`; couvrir corrections critiques, baseline visuelle et commits
atomiques.

- [ ] **Step 3: Documenter Chutes**

Créer `## Consultation externe Chutes`; inclure smoke test, modèles réellement
disponibles, absence de secrets, vérification locale, journalisation dans
`audit/chutes/`, rôle consultatif et HTTP 402 observé.

- [ ] **Step 4: Écrire l'état audité entre les marqueurs exacts**

Créer le bloc `<!-- BEGIN CURRENT AUDITED STATE -->` / `<!-- END CURRENT AUDITED
STATE -->`; inclure mesures, gates, tests, P0, limites PDF, manifeste vide et
distinction `1d0c3fda` / `b5c6f9f1`.

- [ ] **Step 5: Écrire roadmap et décisions**

Créer `## Roadmap approuvée`, `## Décisions humaines acquises` et `## Questions
ouvertes`; distinguer décisions acquises, ordre Wave 0→4 et arbitrages futurs.

- [ ] **Step 6: Écrire carte documentaire et procédure d'audit**

Créer `## Carte documentaire` et `## Procédure pour un nouvel auditeur`; classer
autorités, preuves générées et historiques puis fournir la reproduction minimale.

- [ ] **Step 7: Écrire sécurité, glossaire et compte rendu**

Créer `## Sécurité, propriété intellectuelle et données personnelles`,
`## Glossaire` et `## Format de compte rendu`; signaler visibilité publique,
absence de licence racine et reprendre le format contractuel final.

- [ ] **Step 8: Relire pour DRY et vérifier la dernière couche**

Run:

```bash
git diff --check
rg -n '<!-- (BEGIN|END) CURRENT AUDITED STATE -->' README.md
rg -n '^## (Workflow obligatoire|Consultation externe Chutes|État courant|Roadmap|Carte documentaire|Procédure|Sécurité|Glossaire|Format)' README.md
```

Expected: aucun défaut d'espace, deux marqueurs ordonnés et toutes les sections
de passation présentes; « cible », « actuel », « observé » et « historique »
restent distincts.

---

## Chunk 3: Validation, revues et commit

### Task 7: Vérifier le README comme artefact d'audit

**Files:**

- Test: `README.md`
- Test: tous les chemins locaux mentionnés
- Test: Git et inventaire Nexus

- [ ] **Step 1: Vérifier les sections structurantes**

Run:

```bash
python3 - <<'PY'
from pathlib import Path

text = Path("README.md").read_text(encoding="utf-8")
required = (
    "NO-GO publication",
    "## Le projet en 90 secondes",
    "## Hiérarchie d'autorité",
    "## Les six manuels",
    "## Logique métier de la chaîne éditoriale",
    "## Modèle pédagogique Nexus",
    "## Programmes officiels 2026-2027",
    "## Arborescence du dépôt",
    "## Charte graphique v5/v6",
    "## Tests et gates",
    "## Workflow obligatoire de contribution",
    "## Consultation externe Chutes",
    "<!-- BEGIN CURRENT AUDITED STATE -->",
    "<!-- END CURRENT AUDITED STATE -->",
    "## Procédure pour un nouvel auditeur",
    "## Glossaire",
)
missing = [item for item in required if item not in text]
assert not missing, missing
assert text.index("<!-- BEGIN CURRENT AUDITED STATE -->") < text.index(
    "<!-- END CURRENT AUDITED STATE -->"
)
PY
```

Expected: exit 0.

- [ ] **Step 2: Vérifier les chiffres et références sensibles**

Run:

```bash
python3 - <<'PY'
from pathlib import Path

text = Path("README.md").read_text(encoding="utf-8")
for value in (
    "2 860",
    "2 911",
    "2 026",
    "MENE2602917A",
    "MENE2515469N",
    "MENE1921246A",
    "MENE1921265A",
    "MENE1921264A",
    "MENE1901633A",
    "MENE1921247A",
):
    assert value in text, value
assert "MENE1921262A" in text  # doit être présent uniquement comme erreur signalée
assert "67 bloqueurs" in text
assert "119 nouvelles empreintes" in text
assert "119 qualifications manquantes" in text
PY
```

Expected: exit 0.

- [ ] **Step 3: Vérifier que les contradictions sont explicitement qualifiées**

Run:

```bash
python3 - <<'PY'
from pathlib import Path

text = Path("README.md").read_text(encoding="utf-8")
assert "MENE1921262A" in text and "STMG" in text
assert '"builds": []' in text
assert "physiquement dupliqu" in text
assert "visibilité publique" in text
assert "licence" in text
assert "historique" in text
assert "baseline" in text and "acceptation" in text
PY
```

Expected: exit 0.

- [ ] **Step 4: Vérifier tous les liens Markdown locaux**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
import re

root = Path.cwd()
text = (root / "README.md").read_text(encoding="utf-8")
missing = []
for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
    if target.startswith(("http://", "https://", "#")):
        continue
    clean = target.split("#", 1)[0]
    if clean and not (root / clean).exists():
        missing.append(target)
assert not missing, missing
PY
```

Expected: exit 0.

- [ ] **Step 5: Vérifier les commandes documentées contre les interfaces**

Run:

```bash
python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py --help \
  | grep -E -- '--manual|--variant|--record-observed'
python3 NSI/scripts/assemble_manuel.py --help \
  | grep -E -- '--book|--variant|--record-observed'
python3 - <<'PY'
import ast
from pathlib import Path

tree = ast.parse(Path("NSI/scripts/assemble_manuel.py").read_text(encoding="utf-8"))
variants = None
for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "VARIANTS":
                variants = ast.literal_eval(node.value)
assert variants is not None
assert {"eleve", "professeur"} <= set(variants)
PY
```

Expected: toutes les options documentées sont présentes.

- [ ] **Step 6: Vérifier le diff documentaire**

Run:

```bash
git diff --check
git status --short
git diff --stat
```

Expected: exactement `README.md` non commité à ce stade ; conception et plan
déjà committés.

- [ ] **Step 7: Faire relire la conformité à la spécification**

Dispatch a fresh reviewer with this exact brief:

```text
Relis README.md en lecture seule contre :
- docs/superpowers/specs/2026-08-13-readme-racine-autosuffisant-design.md
- docs/superpowers/plans/2026-08-13-readme-racine-autosuffisant.md
- audit/AUDIT_ETAT_PROJET_2026-08-13.md
- AGENTS.md
Vérifie chaque exigence de la spécification, le périmètre de trois fichiers,
les chiffres, les références officielles, les marqueurs d'état et l'absence de
déclaration de conformité. Réponds exactement `✅ Spec compliant` si tout est
couvert, sinon `❌ Issues Found` suivi de références section/ligne et du correctif
minimal. Ne modifie aucun fichier.
```

Expected: `✅ Spec compliant`, aucune exigence manquante ou ajout hors
périmètre. Toute lacune est corrigée par l'implémenteur puis le même reviewer
est relancé jusqu'à approbation.

- [ ] **Step 8: Faire relire la qualité documentaire**

After spec approval, dispatch a different fresh reviewer with this exact brief:

```text
Audite README.md en lecture seule comme portail remis à un auditeur externe.
Utilise la spec, le plan et audit/AUDIT_ETAT_PROJET_2026-08-13.md. Contrôle
clarté, autonomie, navigation, DRY, liens, commandes, distinction cible/état,
risques et absence d'ambiguïté de release. Réponds exactement `✅ Approved` si
aucun problème important ne subsiste, sinon `❌ Issues Found` avec priorité,
section/ligne et correctif minimal. Ne modifie aucun fichier.
```

Expected: `✅ Approved`, liens, structure, clarté, exactitude et signalement des
risques satisfaisants. Toute remarque importante est corrigée par l'implémenteur
puis le même reviewer est relancé jusqu'à approbation.

- [ ] **Step 9: Committer le README seul**

Run:

```bash
set -e
git add README.md
git diff --cached --check
git diff --cached --stat
git commit -m "[DOCS] ajoute le README racine autosuffisant"
```

Expected: un commit contenant uniquement `README.md`.

- [ ] **Step 10: Vérifier l'arbre propre et le gate structurel après commit**

Run:

```bash
set -e
git status --short --branch
git diff --check
python3 scripts/inventory_collection.py --check --require-clean
```

Expected: arbre propre, `git diff --check` exit 0, gate structurel exit 0.

- [ ] **Step 11: Relever sans les masquer les gates rouges déjà connus**

Run:

```bash
set +e
python3 scripts/check_charte_sync.py
charte_status=$?
python3 scripts/inventory_collection.py --check --validate-model --require-clean
model_status=$?
python3 scripts/inventory_collection.py --check --fail-on-new --require-clean
debt_status=$?
python3 scripts/inventory_collection.py --check --release-strict --require-clean
release_status=$?
set -e
printf 'charte=%s model=%s debt=%s release=%s\n' \
  "$charte_status" "$model_status" "$debt_status" "$release_status"
test "$charte_status" -eq 1
test "$model_status" -eq 6
test "$debt_status" -eq 5
test "$release_status" -eq 7
```

Expected: les mêmes codes rouges documentés, sauf modification concurrente
explicite du projet. Une différence impose un nouvel audit avant toute
conclusion.

---

## Définition de terminé pour cette tranche

La tranche est terminée seulement si :

- la spécification et le plan sont versionnés ;
- `README.md` existe et respecte toutes les sections approuvées ;
- les chiffres et références sensibles sont vérifiés ;
- les liens locaux existent ;
- les commandes documentées correspondent aux interfaces réelles ;
- les deux revues indépendantes sont approuvées ;
- aucun fichier hors périmètre n'est modifié ;
- le README est committé atomiquement ;
- l'arbre final est propre ;
- le gate d'inventaire structurel reste vert ;
- les gates rouges connus restent visibles et ne sont pas affaiblis ;
- aucune affirmation de publication ou de complétude n'est formulée.
