# A6 — attestation locale avant clones frais

Le candidat local part du SHA A5
`761508d923d74fd3d93fc055b3f3b1857fb251e1`. Cette attestation ne préjuge
pas du résultat Fresh A/Fresh B : ces preuves sont exécutées seulement après
son commit, au `A6_SOURCE_SHA` exact.

## PRE-A6 : validation du modèle

`--validate-model` passe de **rc 6 / 9 failures** à **rc 0 / 0 failure**.
Les neuf cas sont tous `ID_MIGRATION_FINGERPRINT_DRIFT`, par une bijection
mécanique exacte documentée dans
`PRE_A6_VALIDATE_MODEL_FORENSICS.{json,md}`. Aucun cas ne requiert une nouvelle
décision humaine. La baseline, les dispositions, les politiques et les
statuts métier restent byte-identiques ; promotions : **0**.

La sémantique A0/A5 de `correction` est fermée dans
`A5_CORRECTION_TYPE_SEMANTICS.md` : A0 et A5 lisent le même champ brut
`% META.type_objet`, mais avec deux responsabilités compatibles. Le
`source_role` est une dimension orthogonale. Conflit : **NO**.

## A6 : contextes

Les trois cas frais sont tous `PATH_CONTEXT_DRIFT`. Les fichiers placés sous
TCOMPL étaient des copies redondantes de sources canoniques TSPE, identiques
hors `META.id`. La correction supprime uniquement ces trois copies et conserve
les jumeaux TSPE.

- avant : `context_mismatches = 3` ;
- après : `context_mismatches = 0` ;
- retirés : `412440a833f2a67e`, `d4d96a91fdd7f2ca`,
  `dc3c58388e2cfe7c` ;
- ajoutés : 0 ;
- reclassifiés : 0 ;
- fingerprints communs modifiés : 0 ;
- `UNKNOWN = 0`.

## Inventaire et gouvernance

L’inventaire frais donne RAW/fingerprints bloquants/non bloquants =
**2308/2308/0**. Le total des fingerprints bloquants n’est pas le compteur de
la catégorie `blocking_statuses`, qui reste strictement **2222→2222**.
Catégories actives : `blocking_statuses=2222`, `unassembled_objects=52`,
`unattributed_pdfs=22`, `orphan_files=12`. Toutes les autres catégories sont
nulles, notamment `context_mismatches`, `unclassified_types`, broken meta,
broken LaTeX, cycles et duplicates. `P0=0`, `NEW_UNQUALIFIED=0` et
`EXPECTED_REVIEW_DEBT=89`.

Les 89 sources de méthodes et 89 packets ont été relus : SHA source du
record, `packet.source_sha256`, SHA courant de la source et SHA courant du
packet concordent ; les deux statuts restent `needs_review` ; stale = **0**.

Autorités inchangées :

- baseline : `3e9225668121a67c2fdea1248ec420ff16bd3910c8557e3a98df8bb7997250e1` ;
- dispositions : `49595a0f28745eee0b8f080a4cbeb2fa7265a798455f2747a93d9d532635cda6` ;
- policy baseline : `07d95c5073da77944ab07a3312483fdfda0f43d6f412ee023f3269c770b282d2` ;
- policy humaine A4 : `07597ede77c7fce1a167a87227178f05a10faabbad4ca1e04d7bb2048fda12a7`.

## Tests et gates locaux

- root : **1199 passed**, 0 failed/skip/xfail ;
- Math : **4695 passed**, 0 failed/skip/xfail ;
- NSI : **2191 passed**, 0 failed/skip/xfail ;
- A6 ciblé : 7 passed ; PRE-A6/validate-model : 43 passed ;
- A5 ontologie : 9 passed ; régressions A1–A4 : 28 passed ;
- `--check --require-clean` : rc 0 ;
- `--validate-model` : rc 0 ;
- `--fail-on-new` : rc 0 ;
- `--release-strict` : rc 7, 65 raisons, aucune raison nouvelle.

La seule raison release retirée est
`TCOMPL:anomalie:context_mismatches:anomalies.context_mismatches:3`.
La publication reste **NO-GO** et D7 **BLOCKED**.

## Builds affectés

Sous l’environnement A4 versionné complet, deux passages donnent des PDF
byte-identiques : chapitre TCOMPL `complet` (`a40e6eec…`, 18 pages),
`parcours1` (`97f61cda…`, 17 pages), manuel élève (`6212a21b…`, 162 pages)
et professeur (`d14ec54c…`, 226 pages). Les smokes 1NSI élève/professeur
restent byte-identiques aux PDF A4.

Sur les 36 PDF suivis, 34 restent inchangés. Les deux changements TCOMPL sont
les sorties attendues de la suppression des copies : élève 164→162 pages,
professeur 229→226 pages. Aucun oracle visuel ni receipt n’a été créé.

## Stop

Aucun push, merge, baseline update, statut promu, qualification humaine ou lot
suivant n’a été commencé. Les clones frais doivent encore reproduire
exactement ce candidat avant verdict A6.
