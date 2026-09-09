# AUDIT — État des lieux du dépôt `Manuels_Nexus`

**Date de l'audit** : 2026-09-09
**Périmètre** : dépôt `/home/alaeddine/Documents/Manuels_Nexus`, son worktree, ses 30 branches
locales, ses 7 branches distantes, et les trois arborescences non versionnées présentes à la racine.
**Nature** : constat. Ce document n'approuve rien, ne publie rien, ne modifie rien.
Il n'a autorité que descriptive et ne remplace ni `SOURCE_DE_VERITE.md`, ni `AGENTS.md`,
ni `audit/PUBLISH_READINESS_CHAPTER_MATRIX.json`.

---

## 1. Synthèse en dix lignes

Le projet produit six manuels scolaires (Mathématiques 1re/Tle × 3 voies, NSI 1re/Tle) plus,
depuis le 9 septembre, une septième collection HGGSP entièrement hors du dispositif habituel.
La production réelle vit **dans un worktree, sur une branche jamais poussée** :
`codex/t3-publish-readiness-current`, 1 396 commits d'avance sur `origin`, arrêtée le 8 septembre.
Le dépôt distant GitHub est figé au **15 août 2026** : il ignore 1 526 commits, soit trois semaines
et demie de travail intensif (~60 commits/jour). La checkout principale est, elle, restée sur une
branche de sauvetage du 28 août (`rescue/t2-legacy-wip-…`), obsolète, et porte trois modifications
non commitées faites **aujourd'hui** qui n'existent nulle part ailleurs.
Sur le fond : les 52 chapitres sont tous `MACHINE_REVIEW_COMPLETE`, mais **0 sur 52** ont reçu la
clôture humaine, et 2 552 unités de dette de revue restent explicitement bloquantes pour la release.
Trois artefacts de statut se contredisent frontalement. Aucun manuel n'est publiable.

---

## 2. Topologie physique

### 2.1 Arborescences

| Emplacement | Nature | Taille | Branche | État |
|---|---|---:|---|---|
| `/home/alaeddine/Documents/Manuels_Nexus` | checkout principale | 6,4 Go | `rescue/t2-legacy-wip-2026-08-28-761508d9` | 3 fichiers modifiés non commités, 3 dossiers non suivis |
| `…/.worktrees/t3-publish-readiness` | worktree git | 359 Mo | `codex/t3-publish-readiness-current` | 2 modifiés + 3 non suivis |
| `…/HGGSP` | **dépôt git imbriqué autonome** | 186 Mo | `correctif/verificateur` | 33 entrées non commitées, **aucun remote** |

`.worktrees/` est dans `.gitignore` : le worktree est invisible du point de vue de l'index.
`git worktree prune --dry-run` ne signale aucun worktree fantôme. Les deux worktrees déclarés
existent bien et sont sains structurellement.

### 2.2 Répartition du volume (checkout principale)

```
5,3 Go  Mathematiques/     (dont un .venv embarqué qui gonfle tout balayage naïf)
186 Mo  HGGSP/             non suivi, dépôt imbriqué
 96 Mo  audit/
 39 Mo  NSI/
 17 Mo  MANUELS_PDF_PUBLICATION/
 16 Mo  Fiches_cours_exercices/   ignoré depuis aujourd'hui
 12 Mo  _SAUVEGARDES_HGGSP/       non suivi
```

Base d'objets git : 289 Mo en pack, 74 412 objets. `git fsck` relève 444 commits, 1 987 arbres et
3 411 blobs inatteignables — résidu normal de rebases et resets passés, sans perte identifiée.

---

## 3. État Git

### 3.1 Le fait central : le distant est trois semaines et demie en retard

`origin` = `github.com/cyranoaladin/manuels-nexus` (public). Il répond, il est joignable, et ses
7 têtes distantes correspondent **exactement** aux refs de suivi locales. Aucune divergence,
aucun conflit : simplement, **rien n'a été poussé depuis le 15 août 2026**.

```
Commits locaux absents de toute ref origin : 1 526
Dernier fetch enregistré                   : 12 août 2026
Branches locales                           : 30
Branches distantes                          : 7
Branches locales jamais poussées            : 23
```

Sur les 7 branches distantes, 5 sont contenues dans `main` ou identiques à lui.
La plus avancée, `integration/1spe-bo2026-traceability` (15 août), est déjà à 1 349 commits
derrière la production courante.

**Conséquence** : la totalité de la production du 15 août au 8 septembre — l'essentiel du travail
d'assainissement, de preuve et de correction disciplinaire — n'existe que sur ce disque.
Il n'y a **aucune copie hors machine**. C'est le risque numéro un du projet.

### 3.2 Rythme de production

2 364 commits au total, 2 361 d'un seul auteur (Alaeddine Ben Rhouma).
Activité soutenue et régulière, sans interruption notable :

```
août     : 10→141, 11→95, 16→165, 19→116, 23→98, 26→69, 29→56, 30→64, 31→57
septembre: 01→60, 02→34, 03→61, 04→86, 05→34, 06→82, 07→171, 08→77
```

Dernier commit du dépôt : `274a7b811`, 8 septembre 2026,
« [MATH] corriger le modele du TD stylos et fournir ses treize reponses ».
**Aucun commit le 9 septembre** dans le dépôt principal — la journée d'aujourd'hui a été
consacrée à HGGSP (dépôt imbriqué) et à trois éditions non commitées.

### 3.3 Cartographie des 30 branches

`codex/t3-publish-readiness-current` est le **tronc** : il contient comme ancêtres 15 des
30 branches, dont `main`, `production/collection-v2`, `finalisation/collection-v1`,
`integration/1spe-bo2026-traceability`, toute la lignée `codex/t2-*`, `audit/*` et
`backup/pre-remediation-84b5185b`. Ces 15 branches sont donc **archivables sans perte**.

Restent 15 branches portant du contenu unique :

| Branche | Commits uniques vs t3 | Verdict |
|---|---:|---|
| `codex/urgent-1nsi-content` | **51** | Lot 1NSI réel (retrait de ~500 clones synthétiques, rédaction de méthodes et remédiations, fermeture INT-004/006). **À réconcilier — le plus gros enjeu.** |
| `green/openrouter-only` | 46 | Lignée « OpenRouter » ancienne (14 août), non intégrée |
| `feature/1spe-bat-2026` | 34 | Non fusionnée depuis le 29 juillet — cas documenté dans `SOURCE_DE_VERITE.md` §« Ce qui reste hors de main » |
| `docs/openrouter-only` | 27 | Doublon documentaire de la précédente |
| `manifest-fix-tspe` | 15 | Ancien (15 août) |
| `green/p0-programme-tspe` | 13 | Vague 0, 13 août |
| `green/p0-student-separation`, `wave0/p0-green-launch` | 9 | Vague 0, 13 août |
| `wave0/p0-red-contracts` | 7 | Vague 0, 13 août |
| `codex/shared-infra-integration` | 4 | Infra partagée ; les 4 commits ont des jumeaux de contenu dans `codex/urgent-1nsi-content` |
| `codex/t2-inventory-refresh` | 2 | Résidu |
| `codex/nsi-direct-fallback-4835`, `rescue/codex-a4-optional-review-65891f2`, `rescue/codex-tnsi-fix-2bcbd09` | 1 chacun | Résidu |
| `rescue/t2-legacy-wip-2026-08-28-761508d9` | **1** | Le commit de sauvetage `88bbc9426` : 122 fichiers, 96 129 insertions (gouvernance de revue humaine, audits QCM/variance, préflight PDF élève). Statut de réconciliation : voir §3.5. |

### 3.4 La checkout principale est sur la mauvaise branche

`HEAD` de la checkout principale = `88bbc9426` (28 août), branche `rescue/t2-legacy-wip-…`.
Le reflog confirme qu'elle n'a plus bougé depuis le 29 août, alors que la production a continué
dans le worktree jusqu'au 8 septembre. Conséquences observables :

- `audit/` y contient 454 fichiers contre **1 068** dans le worktree ;
- `scripts/` : 39 contre **222** ;
- `tests/` : 20 contre **257** (et 32 vs 16 côté Maths, 21 vs 15 côté NSI) ;
- `ETAT_COLLECTION.md` y annonce 66 bloqueurs et une provenance `audit/adversarial-reconciliation-2026`
  qui n'est même pas la branche courante — artefact généré ailleurs, jamais rafraîchi.

**Quiconque ouvre le projet à la racine lit un état périmé de trois semaines.**

### 3.5 Travail non commité — inventaire exhaustif

**a) Checkout principale — 3 modifications datées d'aujourd'hui, uniques au monde**

```
M .gitignore                        + Fiches_cours_exercices/
M scripts/build_d7_proof_bundle.py  exclusion Fiches_cours_exercices du balayage disque
M scripts/build_style_inventory.py  refactor is_scannable() + même exclusion
```

Vérification faite : ces trois modifications **ne sont présentes ni sur `codex/t3-publish-readiness-current`,
ni dans le worktree**. Le `.gitignore` de la branche t3 a divergé dans une autre direction
(il ignore `.env*` et `/build/`, pas `Fiches_cours_exercices/`).
Ce sont des correctifs légitimes — les deux scripts balaient le disque et non l'index git, donc
un dossier local non versionné doit être exclu nommément — mais ils sont posés sur une branche morte.
**Risque de perte réel et immédiat.**

**b) Worktree t3 — 5 entrées**

```
M scripts/build_nsi_coupled_review_debt.py
M scripts/qcm_independent_solver.py
? audit/QCM_OPTION_VALUE_SEMANTICS_QA_2026_09_08.json
? tests/test_nsi_coupled_execution_binding.py
? tests/test_qcm_option_value_semantics.py
```

Travail en cours du 8 septembre : sémantique des options de QCM et liaison d'exécution NSI.
Deux tests neufs non commités — donc hors de toute preuve.

**c) Deux stashs, tous deux du 15 août, sur `integration/1spe-bo2026-traceability`**

| Stash | Portée | Contenu |
|---|---|---|
| `stash@{0}` `tmp-release-tspe-gates` | 4 602 fichiers | Régénérations massives d'inventaire (`INVENTAIRE_COLLECTION.json` : −157 k lignes), `ECARTS_ET_CONTRADICTIONS.yaml`, `CHAPTER_READINESS.json` |
| `stash@{1}` `tmp-release-run` | 4 812 fichiers | Quasi identique, une passe antérieure |

Ce sont des **sorties de générateurs**, pas du contenu d'auteur : reproductibles en relançant
`inventory_collection.py`. Ils sont aujourd'hui incohérents avec un arbre qui a trois semaines
d'avance. Ils encombrent une pile partagée entre les deux worktrees.
Leur conservation ne se justifie plus, mais leur suppression relève d'une décision humaine
(`AGENTS.md` interdit tout nettoyage automatique).

### 3.6 Tags

16 tags, tous locaux à la lignée 1SPE/TSPE : 13 `chap/*-v1` et 3 `manuel/1SPE-v1{,.1,.2}`.
Aucun tag ne couvre la production d'août-septembre. Le dernier gel visuel/éditorial taggué
est très antérieur à l'état courant.

---

## 4. Source de vérité — le point le plus problématique

### 4.1 Ce que la règle écrite affirme

`SOURCE_DE_VERITE.md` (consolidé le 11 août, amendé le 7 septembre) pose :

> `/home/alaeddine/Documents/Manuels_Nexus`, branche **`main`**, est l'unique source de vérité.
> Aucun contenu de la collection ne doit vivre ailleurs : **ni dans un worktree, ni dans une
> branche non fusionnée**, ni dans un dossier externe.

### 4.2 Ce que le disque montre

Cette règle est **violée sur ses trois termes simultanément** :

| Règle | Réalité |
|---|---|
| `main` est la source de vérité | `main` = `a21ff5327`, 11 août, **1 443 commits de retard**. Il ne décrit plus rien. |
| Pas de contenu dans un worktree | Toute la production courante est dans `.worktrees/t3-publish-readiness`. |
| Pas de contenu en branche non fusionnée | 1 526 commits locaux, dont 51 sur `codex/urgent-1nsi-content` encore hors du tronc. |
| Le distant est le miroir | Il est figé au 15 août. |

Le document lui-même n'est plus à jour : il annonce « 51 chapitres, 2 751 objets » alors que
l'état courant en compte **52 chapitres et ~3 445 objets** (le chapitre `TNSI-PROJET` a été ajouté,
prouvé par `NSI/manifests/books/TNSI.json` et le commit d'introduction `59ace0225`).

**Source de vérité *de facto*** : `codex/t3-publish-readiness-current` @ `274a7b811`,
matérialisée dans `.worktrees/t3-publish-readiness`. C'est le seul arbre où contenu, scripts,
tests et audits sont mutuellement cohérents.

### 4.3 Trois verdicts de publication qui se contredisent

| Artefact | Date | Verdict affiché |
|---|---|---|
| `audit/COLLECTION_PUBLISH_READINESS.md` | 6 sept. | `ALL_CANONICAL_MANUALS_ZERO_DEBT_PUBLISH_READY`, **12/12 PUBLISH_READY**, signoff release owner `True`, dette ouverte `0` |
| `ETAT_COLLECTION.md` (worktree) | ~7 sept. | Gate `release-strict` : **ROUGE, 113 bloqueurs** |
| `audit/PUBLISH_READINESS_CHAPTER_MATRIX.json` | 8 sept. | 52/52 `MACHINE_REVIEW_COMPLETE`, **`human_closed: 0`**, `approves_nothing: true`, **2 552 unités de dette bloquante** |

L'arbitrage est écrit noir sur blanc dans `ETAT_COLLECTION_2026_2027.md` :

> **NON AUTORITAIRE — DIAGNOSTIC HISTORIQUE.** Le verdict de release appartient exclusivement à
> `audit/PUBLISH_READINESS_CHAPTER_MATRIX.json`.

Donc : **`COLLECTION_PUBLISH_READINESS.md` est périmé et trompeur**. Il date du 6 septembre, avant
la campagne de correction disciplinaire des 7 et 8 septembre, et son affirmation « dette ouverte 0 /
signoff final True » est démentie par l'artefact autoritaire deux jours plus tard.
C'est le document le plus dangereux du dépôt : il est le seul à dire « prêt ».

### 4.4 Fraîcheur des artefacts générés

| Artefact | Dernier commit qui le touche | Commits de contenu depuis |
|---|---|---|
| `audit/PUBLISH_READINESS_CHAPTER_MATRIX.json` | `0c7a470fc`, 8 sept. 02:21 | **57 commits, 346 fichiers de chapitre modifiés** |
| `audit/COLLECTION_PUBLISH_READINESS.json` | `d82c62db8`, 6 sept. 17:52 | ~2 jours de production |
| `audit/gates/*.json` | `533d19198`, **15 août** | **~3,5 semaines** |
| `MANUELS_PDF_PUBLICATION/*.pdf` | `43d9f5dac`, 6 sept. (restauration d'un instantané historique) | les 12 PDF datent du **15 août** |

Même l'artefact autoritaire est en retard de 57 commits sur l'arbre. Les verdicts de gate sont
antiques. Et — détail qui compte — `533d19198`, dernier commit à toucher `audit/gates/`, est
précisément le commit identifié par le projet lui-même comme le **commit de remplissage
synthétique** (973 objets recopiés dans quinze chapitres), démonstration empirique qui a conduit
à abandonner le critère « ≥50 exercices/chapitre » le 7 septembre.

---

## 5. État d'avancement du contenu

### 5.1 Périmètre canonique

6 manuels, 52 chapitres, ~3 445 objets pédagogiques (inventaire suivi : 3 441),
24 livrables requis (12 éditions élève/professeur + 12 auxiliaires).

| Manuel | Chapitres | Objets (matrice 8 sept.) |
|---|---:|---:|
| 1SPE — Maths 1re spécialité | 10 | 1 450 |
| TSPE_2026_2027 — Maths Tle spécialité | 11 | 829 |
| TCOMPL — Maths Tle complémentaires | 9 | 318 |
| TEXPERTES — Maths Tle expertes | 5 | 243 |
| 1NSI — NSI 1re | 10 | 413 |
| TNSI — NSI Tle | 7 | 192 |

Sources : 4 003 `.tex` côté Mathématiques, 1 713 côté NSI.
Chaîne LaTeX partagée : `gabarits/` (classe `nexus-manuel-v5.cls` + `nexus-charte-v6.sty` +
`nexus-pont-v6.sty`), synchronisée à l'identique dans `Mathematiques/` et `NSI/`, vérifiée par test.

### 5.2 Revue machine : terminée. Revue humaine : nulle.

`audit/PUBLISH_READINESS_CHAPTER_MATRIX.json`, 8 septembre :

```
chapters                  : 52
machine_review_complete   : 52
machine_review_incomplete : 0
human_closed              : 0        ← aucun chapitre validé par un humain
ALL_MACHINE_CONTENT_COMPLETE : true
approves_nothing          : true     ← l'artefact le dit de lui-même
```

Les douze dimensions machine (programme, couverture des rôles, clones, EX/CO, cross-discipline,
assemblage de cours, oracle, QCM, diacritiques, évaluations) sont `COMPLETE` sur les 52 chapitres.
C'est un vrai résultat, obtenu en trois semaines. Mais il ne certifie que le calculable.

**Dette de revue déclarée bloquante pour la release : 2 552 unités**, réparties sur 22 registres :

| Registre | Unités |
|---|---:|
| `UNCHANGED` | 2 110 |
| `QCM_ANSWER_SEMANTICS` | 128 |
| `A4_METHOD_REQUALIFICATION_STALE_83` | 83 |
| `TSPE_GEO_NEW_40` | 40 |
| `NSI_COUPLED_NEW_32` / `T3_AUTHORED_REVIEW_DEBT` | 32 / 32 |
| `TNSI_EXAM_BANKS_…_26`, `NSI_METHOD_SHEETS_…_20`, `RESIDUAL_TRUE_NEW_13`, `VARALEA_C6C7_…_12` | 26 / 20 / 13 / 12 |
| 12 autres registres | ≤10 chacun |

Deux files de lecture humaine, disjointes (intersection 0, union 501) :
- `NEW_AUTHORING_REVIEW_PENDING` : **290** objets neufs. Tous ont un oracle qui passe
  (`ORACLE_FAILURES: 0`), mais un oracle prouve l'exactitude calculable, pas l'adéquation au
  programme, ni la qualité de l'énoncé, ni le niveau. Concentration : `TEXP-ARITHMETIQUE` 49,
  `TEXP-GRAPHES` 20, `TEXP-MATRICES-MARKOV` 19, `TCOMPL-MODELES-FONCTION` 15.
- `NON_FORMALIZABLE_REVIEW_PENDING` : **207** objets sur 417 — ceux qui ne peuvent structurellement
  pas porter d'oracle : 105 coups de pouce, 84 méthodes, 9 versions aménagées, 4 expérimentations,
  3 algorithmes, 1 projet, 1 remédiation. 16 revus à ce jour, 0 défaut trouvé.

Verdict pédagogique recalculé : **50 chapitres `ADEQUATE` + 2 `STRONG`**, aucun `WEAK`.
Le document précise qu'aucun verdict n'est affirmé — ils sont dérivés des compétences déclarées.

### 5.3 Défauts disciplinaires ouverts, nommément

Le `audit/REPRISE_CHECKPOINT_2026-09-08.md` liste cinq défauts scientifiques constatés le 8 septembre
et **explicitement non refermés** :

1. accroche de boîte cubique présentée comme quadratique (contrat du second degré) ;
2. preuve du discriminant ne traitant pas correctement `a < 0` ;
3. frontière pédagogique de la forme canonique à corriger ;
4. condition `pgcd(a,n) | b` manquante en remédiation des congruences ;
5. domaine non précisé dans `PGCD(n,0) = n`.

> « Ces constats interdisent d'extrapoler une clôture produit depuis les compteurs structurels. »

Autres points ouverts du même checkpoint :
`PROGRAM_EVIDENCE_MISSING_SOURCE` = 23 occurrences / 12 chemins ;
`VALIDATION_STALE` = 1 431 artefacts JSON sur 4 788 (preuves sans empreinte source suffisante) ;
`REUSED_RETIRED_IDS_WITH_DIFFERENT_CONTENT` = 218 ;
`UNRESOLVED_CLONE_GROUPS` = 5 near-clones ;
jointure d'identité défectueuse sur les capacités du second degré (8 capacités de contrat contre
5 atomes officiels) ;
`ASTRA_CONTROLS_MAPPED/OBSOLETE/PARTIAL/NOT_COVERED` = **`NON_VERIFIE`** sur 273 contrôles.

Tests ciblés du kit de revue humaine : **13 passés / 5 échoués**. Suite complète non lancée.

### 5.4 Les 12 PDF

Les 12 PDF de `MANUELS_PDF_PUBLICATION/` sont suivis dans git et présents à l'identique dans les
deux arbres (mêmes tailles à l'octet). Ils datent du **15 août** — antérieurs à toute la campagne
d'assainissement. Le commit du 6 septembre qui les touche est libellé « restore canonical historical
publication snapshot » : ce sont des **instantanés historiques**, pas des sorties de l'état courant.
36 PDF sont suivis au total (12 publication + 8 builds Maths + 4 builds NSI + BO officiels + pack P13).

Maturité des livrables (`RELEASE_DELIVERABLE_READINESS.md`, 7 sept.) :
`DEVELOPMENT_READY` 24/24, `ASSEMBLY_READY` 24/24, `BUILD_TARGET_READY` 24/24,
`DEVELOPMENT_BUILD_PASS` 24/24, **`RELEASE_READY` 0/24** — « attendu pendant cette phase ».

### 5.5 Verdicts des gates (périmés, mais unanimes)

`audit/gates/` — 6 exécutions, **toutes en échec**, cause racine identique
« source_digest du manifeste de build incohérent » :

| Gate | exit | bloqueurs |
|---|---:|---:|
| `check` | 3 | 1 |
| `require-clean` | 4 | **5 485** |
| `fail-on-new` | 5 | 1 |
| `validate-model` | 6 | 2 |
| `release-strict` (+ repeat) | 7 | 1 |

Le digest incohérent bloque `structure`, ce qui cascade et laisse toutes les autres dimensions
`not_covered` — donc **non mesurées**, pas « vertes ». À rejouer avant toute conclusion.

---

## 6. HGGSP — une septième collection, hors dispositif

Apparue le 9 septembre 2026 (aujourd'hui). C'est une collection HGGSP 2027 en 5 volumes pour
candidats individuels au baccalauréat.

**Ce qu'elle n'est pas** : elle n'est pas dans le dépôt. C'est un **dépôt git imbriqué autonome**
(`HGGSP/.git`, branche `correctif/verificateur`, 2 commits, **aucun remote configuré**, 33 entrées
non commitées). Le dépôt parent ne voit qu'un `?? HGGSP/`. Elle n'utilise pas la chaîne LaTeX
`gabarits/` — aucun `.tex` — mais une chaîne Markdown/JSON → PDF/HTML distincte.
328 fichiers, 186 Mo.

**Ce qui existe** : les 5 PDF de l'édition 1.0, vérifiés identiques par SHA-256 à l'édition de
référence — V01 Manuel cycle terminal (156 p.), V02 Niveau 1 Première (95 p.),
V03 Compagnon d'autocorrection (82 p.), V04 Épreuves blanches et corrigés (46 p.),
V05 Épreuves sujets seuls (18 p.). Plus 5 couvertures PNG.

**Ce qui manque — et c'est bloquant** : la chaîne de fabrication est absente du disque.
`HGGSP/01_FABRICATION/SOURCES_MANQUANTES.md` documente que **14 fichiers sur 113** de l'archive
`HGGSP_2027_Edition_complete.zip` (5 300 272 octets, SHA-256 `47c37f71…`) ont été retrouvés.
Manquent les 11 chapitres source, la banque pédagogique, les 9 examens, le référentiel,
`build.py`, `assemble.py`, `verifier.py`, les feuilles de style, le manifeste SHA-256.
Recherche de l'archive sur tout `/home/alaeddine` : **introuvable**.

Second blocage déclaré : les couvertures existent mais ne sont pas intégrées aux PDF
(`couverture_integree_au_pdf: false` pour les 5 volumes), et sont à ~128 ppi, insuffisant pour
l'impression (2480×3508 px requis).

Statut auto-déclaré (`CATALOGUE_COLLECTION.json`, `README.md`) :
« collection constituée ; consolidation éditoriale et validation finale à terminer… pas prêt à
diffuser ». L'audit du jour conclut : « Ce rapport ne constitue pas un bon à tirer ».
**Aucune validation disciplinaire humaine n'a eu lieu.**

Satellites non suivis : `_SAUVEGARDES_HGGSP/HGGSP_avant_rangement_20260909.tar.gz` (12 Mo,
sauvegarde pré-réorganisation) et `AUDIT_HGGSP_20260909T154409_985043Z/` (rapport d'inventaire).

---

## 7. Outillage, tests, CI

### 7.1 Volumétrie (worktree t3, l'état réel)

- `scripts/` : **222** fichiers Python. Familles : inventaire (`inventory_collection.py`, 388 Ko —
  producteur canonique), construction de manifeste (`build_manifest.py`, 88 Ko), gates
  (`ci_audit_collection.py`), gouvernance de revue humaine (`human_review_governance.py`, 45 Ko),
  audits disciplinaires ciblés, forensique et réconciliation, tableaux de bord.
- `tests/` : **257** à la racine + 32 Maths + 21 NSI = **310** fichiers de test.
- `audit/` : **1 068** fichiers, dont ~130 paquets de revue humaine par chapitre et les registres
  machine.

Point d'entrée canonique unique : `pyproject.toml`,
`testpaths = ["Mathematiques/manuel-maths/tests", "NSI/tests", "tests"]`,
`--import-mode=importlib`, couverture `fail_under = 76.83` sur `scripts`.
`data_file` de couverture forcé hors de l'arbre (`/tmp/nexus-coverage/.coverage`) — précaution
délibérée : un `.coverage` non suivi suffit à faire échouer le gate « dépôt sale ».

### 7.2 CI GitHub Actions — 3 workflows

| Workflow | Déclencheurs | Contenu |
|---|---|---|
| `ci-audit-collection.yml` | toute PR, push sur `finalisation/collection-v1`, manuel | ruff + mypy, `validate-data`, `run-gates --require-clean --check --validate-model --fail-on-new --release-strict`, pytest + couverture branchée, double build comparé octet à octet |
| `ci-mathematiques.yml` | PR/push `main` touchant `Mathematiques/**` ou les gabarits | charte-sync, gate SymPy par chapitre modifié, `make specimen`, assemblage |
| `ci-nsi.yml` | PR/push `main` touchant `NSI/**` ou les gabarits | charte-sync, pytest NSI, gate accents R10, `verify_python.py`, assemblage |

**Aucun de ces workflows ne s'est exécuté sur le travail des trois dernières semaines** : ils se
déclenchent sur PR, sur `main` ou sur `finalisation/collection-v1`, et rien n'a été poussé.
La CI est correctement conçue et totalement inopérante en pratique.

### 7.3 Gouvernance (`AGENTS.md`)

Ordre d'autorité posé : textes officiels > cahier des charges > `AGENTS.md` local >
schémas et gates > décisions humaines approuvées > rapports générés > historiques.
Interdits sans instruction humaine explicite : `reset --hard`, `clean`, `restore`, `checkout --`,
`rebase`, `merge`, `push --force[-with-lease]`, déplacement de tags, fusion dans `main`.
Règle de fond : « Aucun contenu `generated`, `draft` ou `needs_*_review` n'est publiable » et
« un agent ne s'auto-approuve pas sur une correction disciplinaire critique ».

Ces règles expliquent — et légitiment — l'accumulation de branches et le refus de fusionner.
Elles n'expliquent pas l'absence de push : `git push` d'une branche de travail n'est dans aucun interdit.

---

## 8. Risques classés

| # | Risque | Gravité | Constat |
|---|---|---|---|
| R1 | **Point unique de défaillance** | Critique | 1 526 commits, ~3,5 semaines de travail, n'existent que sur ce disque. Aucune sauvegarde hors machine. |
| R2 | **Perte du travail du jour** | Élevée | 3 fichiers modifiés aujourd'hui dans la checkout principale, sur une branche morte, absents de t3. |
| R3 | **`COLLECTION_PUBLISH_READINESS.md` annonce « prêt »** | Élevée | Seul artefact à dire 12/12 PUBLISH_READY ; démenti par l'artefact autoritaire. Piège pour tout lecteur pressé. |
| R4 | **`SOURCE_DE_VERITE.md` désigne `main`** | Élevée | `main` a 1 443 commits de retard. La règle écrite et le disque se contredisent. |
| R5 | **Racine du projet trompeuse** | Élevée | Ouvrir le dossier montre l'état du 28 août : 20 tests au lieu de 310, 39 scripts au lieu de 222. |
| R6 | **51 commits 1NSI hors du tronc** | Moyenne | `codex/urgent-1nsi-content` porte un lot de contenu réel non réconcilié. |
| R7 | **Artefacts de preuve périmés** | Moyenne | Matrice autoritaire en retard de 57 commits ; gates du 15 août ; 1 431 validations `VALIDATION_STALE`. |
| R8 | **HGGSP sans remote, chaîne source perdue** | Moyenne | Dépôt imbriqué sans distant ; 99/113 fichiers source introuvables. |
| R9 | **CI jamais déclenchée** | Moyenne | Trois workflows corrects, zéro exécution sur la production courante. |
| R10 | **Stashs obsolètes sur pile partagée** | Faible | 2 stashs du 15 août, ~4 800 fichiers de sorties de générateurs, incohérents avec l'arbre. |
| R11 | **`.gitignore` divergents** | Faible | La checkout principale et t3 ont des `.gitignore` incompatibles. |

---

## 9. Ce qu'il reste à faire pour publier

Dans l'ordre de dépendance, tel que l'état des artefacts le dicte :

1. **Sauvegarder.** Pousser les branches porteuses vers `origin` (au minimum
   `codex/t3-publish-readiness-current` et `codex/urgent-1nsi-content`). Contrôle PII préalable
   exigé par `SOURCE_DE_VERITE.md` : dépôt public, recherche de secrets, données d'élèves, CSV, sqlite.
2. **Sauver le travail du jour** : porter les 3 modifications de la checkout principale sur une
   branche vivante.
3. **Réconcilier** les 51 commits de `codex/urgent-1nsi-content` avec le tronc t3.
4. **Trancher la source de vérité** : soit `main` avance sur t3, soit `SOURCE_DE_VERITE.md` est
   réécrit pour désigner la branche réellement porteuse. L'état actuel est intenable.
5. **Neutraliser `COLLECTION_PUBLISH_READINESS.md`** — y apposer le même bandeau
   « NON AUTORITAIRE » que `ETAT_COLLECTION_2026_2027.md`, ou le régénérer.
6. **Rejouer les gates** sur l'arbre courant et corriger la cause racine
   « source_digest du manifeste de build incohérent ».
7. **Corriger les 5 défauts disciplinaires** nommés au §5.3, avec test de régression pour chacun
   (exigence `AGENTS.md`).
8. **Régénérer** la matrice autoritaire après les 57 commits qui la dépassent.
9. **Lancer la revue humaine** : 290 objets neufs + 207 non formalisables, 501 en union.
   C'est le chemin critique — aucun outillage ne peut s'y substituer.
10. **Reconstruire les 12 PDF** depuis l'état validé : ceux publiés datent du 15 août.
11. **Décider** du sort de `feature/1spe-bat-2026` (branche indivisible, 7 conflits réels, arbitrage
    de baseline visuelle V5.B-it2 contre anti-collision en attente depuis le 29 juillet).
12. **HGGSP** : retrouver ou reconstituer `HGGSP_2027_Edition_complete.zip`, intégrer les
    couvertures, décider si la collection rejoint le dépôt ou reste autonome — et lui donner un remote.

---

## 10. Verdict

**Aucun manuel de la collection n'est publiable au 9 septembre 2026.**
52 chapitres sur 52 ont franchi la revue machine ; **0 sur 52** ont franchi la revue humaine.
2 552 unités de dette sont déclarées bloquantes par l'artefact que le projet a lui-même désigné
comme seul autoritaire, et qui déclare de lui-même `approves_nothing: true`.

Le travail accompli est considérable et méthodologiquement sérieux : l'appareil de preuve
(310 tests, 222 scripts, 1 068 artefacts d'audit), le refus documenté du remplissage synthétique,
l'abandon assumé du seuil « 50 exercices » au profit d'un critère qualitatif, la traçabilité des
décisions. Rien de cela n'est en cause.

Le problème n'est pas la qualité de la production. Il est que cette production **n'existe qu'à un
seul endroit, sur une branche que le dépôt distant ignore, dans un worktree que la règle écrite du
projet interdit, sous une racine qui affiche un état vieux de trois semaines.**

Le premier geste utile n'est pas éditorial. C'est `git push`.

---

*Rapport établi le 2026-09-09 par observation directe du disque, des refs git et des artefacts
générés. Il ne constitue ni une approbation, ni un bon à tirer, ni une clôture de revue.*
