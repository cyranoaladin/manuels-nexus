# T1 — attestation STRUCTURAL_INTEGRITY_ZERO

`SOURCE_SHA = 0babf8873b5de6139314ef7b07dcf8b3715cd942`
Branche `audit/adversarial-reconciliation-2026`. Dépôt propre.

## Verdict

`STRUCTURAL_INTEGRITY_ZERO = YES`.

Sur les 26 catégories d'anomalies du modèle d'inventaire, **25 sont à
zéro**. La seule catégorie non nulle est `blocking_statuses = 2222`.

```text
RAW = 2222 = blocking_statuses (2222) + 0 (toutes les autres catégories)
```

Décomposition complète (toutes catégories du schéma, valeur mesurée) :

| Catégorie | Valeur |
|---|---:|
| `blocking_statuses` | 2222 |
| `assembler_invalid` | 0 |
| `broken_assembly_references` | 0 |
| `broken_latex_references` | 0 |
| `broken_meta_references` | 0 |
| `chapters_not_in_manual` | 0 |
| `context_mismatches` | 0 |
| `contract_invalid` | 0 |
| `contract_missing` | 0 |
| `duplicate_assembly_objects` | 0 |
| `duplicate_capacity_refs` | 0 |
| `duplicate_ids` | 0 |
| `invalid_capacities` | 0 |
| `invalid_meta_references` | 0 |
| `invalid_statuses` | 0 |
| `latex_cycles` | 0 |
| `metadata_invalid` | 0 |
| `metadata_missing` | 0 |
| `missing_assemblers` | 0 |
| `missing_corrections` | 0 |
| `orphan_files` | 0 |
| `unassembled_objects` | 0 |
| `unattributed_pdfs` | 0 |
| `unavailable_inspiration_sources` | 0 |
| `unclassified_types` | 0 |
| `unknown_chapter_prefixes` | 0 |

Cette égalité n'est pas forcée : elle est mesurée directement dans
`audit/INVENTAIRE_COLLECTION.json` au SHA ci-dessus.

## Chemin parcouru (T1.1 → T1.4)

- **T1.1 `context_mismatches`** : fermé pendant A6 (3 → 0, suppression de
  copies redondantes TCOMPL/TSPE).
- **T1.2 `unattributed_pdfs`** : 22 → 0. Registre versionné à 3 rôles
  (`audit/PDF_ARTIFACT_REGISTRY.yaml`), complétude dérivée prouvée sur
  fixtures isolées (6 cas A-F), correction d'un doublon de règle métier
  (22 chemins hardcodés en Python en plus du schéma) qui cassait ~199 tests
  génériques. En-têtes P13 `\nsiheader` corrigés (10 fichiers).
- **T1.3 `orphan_files`** : 12 → 0. Cause racine : 6 fichiers gabarits
  partagés (`gabarits/common/*.cls`) atteignent en réalité, à la
  compilation réelle (TEXINPUTS `./gabarits/:`, cwd = racine du manuel),
  la copie locale de chaque manuel — invisible au graphe de référence
  statique. Preuve concrète : `NSI/gabarits/nexus-code.tex` diverge du
  copie Math/commune pour ajouter le style `sql`/`nxsql`, utilisé par 119
  sources NSI réelles.
- **T1.4 `unassembled_objects`** : 52 → 0. Deux causes : (1) 5 objets
  `1SPE-VARIABLES-ALEATOIRES` réellement `\input` par un objet assemblé
  (fermeture de clôture ajoutée sur le graphe de référence existant) ;
  (2) 47 doublons `TSPE-*-COURS-NN.tex` d'une convention de nommage
  antérieure (`statut: structure`, tous byte-identiques à un frère
  descriptif `status: approved` assemblé), supprimés avec preuve complète
  par fichier dans `audit/T1_4_DELETION_LEDGER.json`.

Chaque lot : cause racine documentée, test RED avant correction, GREEN
après, commit atomique séparé code/contenu/manifest/inventaire, suites
ciblées puis complètes (root + Math + NSI) et les 4 gates rejoués à chaque
étape significative.

## Preuves à ce SHA

- Suites complètes : root **1327 passed**, Math **4698 passed**, NSI
  **2199 passed** — **8224/8224**, 0 failed, 0 skip inattendu.
- `--check --require-clean` : rc **0**.
- `--check --validate-model --require-clean` : rc **0**.
- `--check --fail-on-new --require-clean` : rc **0** (`new=0`,
  `regressions=0`, `failures=0`).
- `--check --release-strict --require-clean` : rc **7**, **64 raisons**
  (dette de publication réelle restante — pas une régression structurelle).

## Ce que ce verdict ne dit PAS

`STRUCTURAL_INTEGRITY_ZERO` ferme la dette de **plomberie du dépôt**. Il ne
dit rien sur :

- la conformité aux programmes officiels 2026-2027 (T2, à venir) ;
- l'exactitude scientifique du contenu (T4) ;
- la qualité pédagogique (T3) ;
- la légitimité des 2222 `blocking_statuses`, qui restent à classifier par
  cause réelle (PROGRAM_REVIEW_REQUIRED, SCIENTIFIC_REVIEW_REQUIRED,
  PEDAGOGICAL_REVIEW_REQUIRED, EDITORIAL_REVIEW_REQUIRED,
  HUMAN_APPROVAL_REQUIRED, STALE_RECEIPT, GENERATED_NOT_REVIEWED,
  DRAFT_CONTENT, NON_PUBLISHABLE_OBJECT, OTHER_EXPLICIT) — travail T7,
  menable en parallèle de T2/T3/T4, non commencé.

`MACHINE_PUBLISH_READY = NO`. `HUMAN_ACCEPTED = NO`. `release-strict` reste
rouge. Aucun push, aucun merge, aucune modification de baseline.

## Dette de gouvernance résiduelle signalée (non bloquante ici)

80 entrées `open_debt` de `audit/BASELINE_QUALIFICATION_REGISTRY.yaml`
référencent des chemins supprimés en T1.4 (débat de dette légitimement
retiré par correction de sa cause, pas une revue de contenu perdue —
détail dans `audit/T1_4_UNASSEMBLED_OBJECTS_FORENSICS.md`). Nettoyage
recommandé en même temps que T7. `validate-model` et `fail-on-new`
restent verts malgré ces entrées désormais orphelines.

## Prochaine action

T2 — construire l'autorité programme officielle exhaustive 2026-2027 pour
les six manuels (1SPE, TSPE, TCOMPL, TEXPERTES, 1NSI, TNSI), sources BO /
education.gouv.fr / Éduscol uniquement, avec vérification explicite de
l'année d'entrée en vigueur pour chaque programme.
