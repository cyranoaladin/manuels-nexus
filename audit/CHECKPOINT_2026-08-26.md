# Checkpoint — 2026-08-26

Commit de référence : `761508d9`. Branche `codex/t2-programme-coverage-ox-alpha`.

**Aucun push. Aucun merge. Aucune baseline update. Aucun oracle D7 modifié.
Aucune auto-approbation. Aucun statut d'objet promu.**

Le dépôt portait déjà 60 fichiers modifiés non commités avant cette session
(vague QCM). Ils sont conservés tels quels.

---

## HUMAN REVIEW GOVERNANCE

**Schema implemented** — oui.

| Élément | Chemin |
|---|---|
| Contrat machine | `audit/HUMAN_REVIEW_GOVERNANCE.yaml` |
| Contrat lisible | `audit/HUMAN_REVIEW_GOVERNANCE.md` |
| Schéma du contrat | `audit/schemas/v1/human-review-governance.schema.json` |
| Schéma du reçu (`HUMAN_REVIEW_RECEIPT_SCHEMA_VERSION = 1`) | `audit/schemas/v1/human-review-receipt.schema.json` |
| Moteur | `scripts/human_review_governance.py` |
| Tests | `tests/test_human_review_governance.py` |

Les deux schémas sont enregistrés dans `SCHEMA_REGISTRY`
(`scripts/inventory_collection.py`), sans quoi
`test_v1_schema_directory_contains_exactly_the_registered_contracts` échouait.

**Mutation tests** — les 11 mutations A à K de la section 17 sont implémentées et
passent, plus les invariants d'indépendance, de fraîcheur et de gate QCM :
**65 tests, 65 passés**.

| Id | Mutation | Attendu | Obtenu |
|---|---|---|---|
| A | même humain pour A et B | FAIL | FAIL |
| B | agent IA comme reviewer (Codex, Claude, Copilot, bot, GPT-5, automation) | FAIL | FAIL |
| C | mauvais `object_set_digest` / `object_count` | FAIL | FAIL |
| D | mauvais `semantic_review_digest` | FAIL | FAIL |
| E | mauvais `packet_digest` | FAIL | FAIL |
| F | `APPROVED` avec `blocking_findings` | FAIL | FAIL |
| G | source sémantique modifiée après review | STALE | STALE |
| H | changement style-only, digest sémantique identique | contenu CURRENT, visuel STALE | idem |
| I | QCM ajouté après review | STALE | STALE |
| J | objet externe à l'ensemble gelé | aucun bénéfice | refusé |
| K | verdict inconnu (`AUTO_APPROVED`, `APPROVED_BY_MACHINE`, …) | FAIL | FAIL |

**Pending packet count** — 4 packets émis, tous `PENDING_UNASSIGNED` :

| Chapitre | Objets | Questions QCM | Packet A | Packet B |
|---|---:|---:|---|---|
| `1SPE-SUITES` | 156 | 21 | `EXPERT_MATHEMATIQUE` | `EXPERT_PROGRAMME_PEDAGOGIE` |
| `1SPE-VARIABLES-ALEATOIRES` | 153 | 15 | `EXPERT_MATHEMATIQUE` | `EXPERT_PROGRAMME_PEDAGOGIE` |

**Approved / rejected count** — **0 / 0**. Aucun reçu n'existe dans le dépôt.

**Rôle NSI** : `EXPERT_NSI`. Le schéma `1nsi-content-review` ne portait que
`reviewer_id` / `reviewer_model` pour des revues *machine* ; aucun nom de rôle
humain n'y existait. `EXPERT_NSI` est projeté sur la dimension `scientific`
existante, `EXPERT_PROGRAMME_PEDAGOGIE` sur `pedagogical`. Aucun nom préexistant
remplacé.

### Contradiction de gouvernance ouverte — bloquante

La section 2 de la décision déclare `1SPE-SUITES` à **161 objets**,
`object_set_digest sha256:67d80062…`. **Aucune énumération cohérente du dépôt ne
produit ces valeurs** ; le digest déclaré n'existe nulle part dans le dépôt. La
machine énumère **156 objets**, `sha256:9d9ab4b6…`.

Quatre hypothèses de reconstruction ont été examinées et rejetées, dont la seule
qui tombe juste numériquement (156 + les 5 fiches `FR-R*`), rejetée parce
qu'elle double-compte : ces 5 fiches portent déjà un `% META` et sont déjà dans
les 12 objets `remediation`.

`audit/HUMAN_REVIEW_FROZEN_SET_RECONCILIATION.{json,md}` — statut
`MISMATCH_UNRESOLVED`. Tant qu'il n'est pas tranché, un test interdit
l'enregistrement de tout reçu sur ce chapitre.

**Décision attendue de vous** : soit confirmer 156 / `sha256:9d9ab4b6…` comme
ensemble gelé contractuel, soit fournir l'algorithme qui produit 161 /
`sha256:67d80062…` pour que la machine le reproduise et le verrouille.

---

## SUITES

| Élément | État |
|---|---|
| Review A (`EXPERT_MATHEMATIQUE`) | `PENDING_UNASSIGNED` |
| Review B (`EXPERT_PROGRAMME_PEDAGOGIE`) | `PENDING_UNASSIGNED` |
| Gate QCM humain | `PENDING` |
| FULL | **0** |
| 156 statuts d'objets | inchangés (`generated`) |
| Contrat | inchangé (`draft`) |

Le décompte de 15 atomes obligatoires vient de votre section 15 ; il n'a pas de
source dans le dépôt. Ce qui est mesuré : 0 approbation humaine, donc 0 atome
FULL quel qu'en soit le dénominateur.

---

## VARALEA

**P0 findings** — 1 trouvé, 1 corrigé.

`1SPE-VARALEA-CO-048` affirmait `σ ≈ 3946 €` pour le portefeuille de 5 projets,
sans énoncer la variance et sans assertion correspondante dans son bloc
`BEGIN-VERIFY`. Corrigé :

- `E(Y) = 160`, `E(Y²) = 3 136 000`, `V(Y) = 3 110 400` ;
- `V(S) = 5 × 3 110 400 = 15 552 000` ;
- `σ(S) = √15 552 000 ≈ 3 944 €` (valeur exacte 3943,602…) ;
- l'écart type est exactement divisé par `√5` par rapport au projet unique.

L'oracle sympy assertait auparavant l'espérance seule. Il asserte désormais
`V == 77760000`, `round(σ) == 8818`, `V_Y == 3110400`, `V_S == 15552000`,
`|σ_S − 3943.602| < 1e-3`, `round(σ_S) == 3944` et `σ/σ_S == √5`. Il s'exécute.
`check_latex.py` : OK.

**Recherche de la CLASSE du défaut** — `scripts/audit_variance_sigma_consistency.py`,
appuyé sur un évaluateur arithmétique LaTeX fermé (`scripts/latex_arith.py`).
Cinq classes : `VARIANCE_SIGMA_SWAP`, `ROOT_MISMATCH`, `ROUNDING_MISMATCH`,
`UNIT_ON_VARIANCE`, `SIGMA_WITHOUT_ORACLE`.

Balayage des **35 chapitres de mathématiques**, pas seulement VARALEA :

| | Avant correction | Après |
|---|---:|---:|
| P0 | 1 | **0** |
| P2 | 1 | 1 |

Le seul P2 restant est `1SPE-VARALEA-EXP-004` : `σ = 2,1` y est exact mais établi
dans un autre objet du chapitre ; l'objet ne porte ni variance écrite ni oracle
propre. Non bloquant, à instruire.

Quatre faux positifs initiaux ont été éliminés en corrigeant l'extracteur :
une chaîne d'égalités terminée par un arrondi (`= 125/3 ≈ 41,7`) ne doit jamais
servir de référence à la racine — c'est la dernière écriture **exacte** qui fait
foi. 26 tests verrouillent ce comportement, dont quatre écritures réelles du
corpus qui ne doivent jamais être signalées.

**Machine science / pedagogy / editorial** — je ne peux pas déclarer
`MACHINE_SCIENCE_PASS`, `MACHINE_PEDAGOGY_PASS` ni `MACHINE_EDITORIAL_PASS` :
ces trois dimensions nommées n'existent pas comme gates outillés dans le dépôt.
Ce qui existe et a été exécuté sur VARALEA : le contrôle de classe
variance/écart-type (0 P0), les oracles `BEGIN-VERIFY`, `check_latex`. La
fermeture verticale complète de VARALEA (PROGRAM, SCIENCE, PEDAGOGY, EDITORIAL,
QCM, REMEDIATION, ASSESSMENT, EXERCISE/SOLUTION, VARIANT, RENDER) **n'est pas
faite**.

**Human packet state** — packets A et B émis, 153 objets, 15 questions QCM,
`PENDING_UNASSIGNED`.

### Défaut corrigé dans l'énumérateur lui-même

VARALEA porte 5 objets sous `cours/experimentations/` qui n'entrent dans le
manuel que par l'`\input` d'un objet de premier niveau. Ma première version de
l'énumérateur les excluait : 148 objets au lieu de 153. Du contenu publié serait
resté hors du périmètre approuvé. L'énumérateur suit désormais les arêtes
d'inclusion transitives et les insère à leur point d'insertion dans l'ordre
d'assemblage. `1SPE-SUITES` n'a aucun objet imbriqué : ses 156 objets sont
inchangés.

---

## GLOBAL

| Indicateur | Valeur mesurée |
|---|---|
| **FULL / 596** | Le dénominateur 596 n'a pas de source dans le dépôt. Mesuré : **5 622** objets `% META` (maths + NSI), 51 chapitres dans `CHAPTER_READINESS.json`, dont 4 `release_ready`. **0 chapitre approuvé par revue humaine.** |
| **Chapitres science machine-complete** | 0 au sens d'un gate nommé — la dimension n'existe pas comme gate outillé. |
| **Chapitres pedagogy machine-complete** | 0, même raison. |
| **Chapitres human-approved** | **0**. Aucun reçu humain n'existe. |
| **13/89 sunset** | Introuvable : aucune occurrence de « sunset » dans `audit/`. Non reproductible. |
| **QCM gaps** | **70** couples capacité×chapitre non interrogés sur **18 chapitres** ; **99** distracteurs sans diagnostic sur **5 chapitres** (`audit/QCM_CAPACITY_COVERAGE_DEBT.json`, statut `PENDING_CONTENT_LOT`). Ni `1SPE-SUITES` ni `1SPE-VARIABLES-ALEATOIRES` n'ont de trou de couverture. |
| **TSPE remediation** | 6 chapitres TSPE avec trous de couverture QCM (`CALCUL-INTEGRAL`, `COMBINATOIRE`, `GEOMETRIE-ESPACE`, `LOGARITHME`, `PRIMITIVES-EQDIFF`, `PROBABILITES`) et 3 avec trous de distracteurs (`DERIVATION-CONVEXITE`, `PROBABILITES`, `TRIGONOMETRIE`). |
| **Style debt** | **33** fichiers `.sty`/`.cls` suivis par git (pas 63 ; 363 en comptant les 10 worktrees). **24 sur 33 n'ont aucune arête de chargement LaTeX** — `nexus-manuel.cls` est monolithique. **10** groupes de duplicatas (pas 21), tous `PER_DISCIPLINE_COPY`, **aucun survivant dérivable du contenu**, **0 fichier safe-to-delete**. Détail : `audit/STYLE_GRAPH_CLASSIFICATION.{json,md}`. |
| **Layout debt** | D7 reste `BLOCKED` : 12 pages divergentes sur 15 dans `audit/D7_VISUAL_PENDING.json`, oracles gelés. Les 20 échecs de `test_maquette_v5.py` sont ce blocage, par construction. **Le rebuild 1SPE élève/professeur avec rasterisation BEFORE/AFTER demandé en section 21 n'a pas été fait.** |
| **Dependency warnings** | **4 + 1 post-summary**, tous amont, tous déclenchés par `test_retrieval.py` : pandas/numexpr, pandas/bottleneck, `SwigPyPacked`, `SwigPyObject`, `swigvarlink`. Registre : `audit/DEPENDENCY_WARNING_AND_PINNING_LEDGER.{json,md}`. Constat réel : les 4 paquets impliqués **ne figurent dans aucun fichier de dépendances du dépôt**. 30 paquets épinglés, dont **8 en dérive et 1 absent** localement — la suite locale ne tourne pas sur l'ensemble de la CI. 14 déclarations `>=` non bornées dans `NSI/requirements.txt`, dont 5 en double avec le fichier épinglé. |
| **Tests / gates** | Suite complète : **8 026 passés, 110 échoués, 63 erreurs** en 21 min 51 s. Répartition des échecs : `NSI/test_assemble_book.py` 71, `test_maquette_v5.py` 20 (D7 BLOCKED), `test_inventory_collection.py` 10, `test_baseline_qualification.py` 5, `NSI/test_gates_corpus.py` 2 ; les 63 erreurs dans `NSI/test_assemble_manuel.py`. **Tous vérifiés préexistants** contre un worktree propre à `761508d9`. `test_renvois_generated_dependency_architecture` échoue sur `META V5: qcm.sha256 ne correspond pas au fichier`, conséquence directe des 40+ QCM modifiés non commités. |
| **release-strict** | **FAILED**, exit 7, 1 bloqueur : `inventaire_indisponible: source_digest du manifeste de build incohérent` — même cause. |

### Deux régressions introduites puis corrigées

Le baseline sur worktree propre a révélé deux échecs qui m'étaient imputables :

1. `test_v1_schema_directory_contains_exactly_the_registered_contracts` — mes
   deux nouveaux schémas n'étaient pas enregistrés dans `SCHEMA_REGISTRY`.
2. `test_live_1nsi_runtime_selection_matches_declared_manual_assemblies` — mon
   chargeur d'assembleur laissait `common` et `pdf_integrity` dans
   `sys.modules` ; l'assembleur NSI résolvait alors le `common` des
   mathématiques et cherchait le manifeste `1NSI.json` sous `manuel-maths`.

Les deux sont corrigées et vérifiées. Après correction, `tests/` retrouve
exactement le jeu d'échecs du worktree propre.

---

## Ce qui n'a pas été fait

- **Section 20** — fermeture verticale complète de VARALEA sur les 10 dimensions.
  Seul le contrôle de classe variance/écart-type a été outillé et exécuté.
- **Section 21** — rebuild 1SPE élève/professeur, localisation des anciennes et
  nouvelles pages, rasterisation BEFORE/AFTER, exigence `visible defect = 0`.
- **Section 24** — vagues EXPONENTIELLE et TNSI-PROJET.
- **Section 22** — la fermeture elle-même (fichier de contraintes, `--require-hashes`,
  arbitrage des 5 paquets déclarés deux fois) : seul le registre est produit,
  conformément à la consigne de ne rien changer pendant la vague de contenu.

## Prochaine décision qui vous revient

La réconciliation de l'ensemble gelé de `1SPE-SUITES` (156 vs 161). Elle bloque
l'assignation de tout reviewer sur ce chapitre.
