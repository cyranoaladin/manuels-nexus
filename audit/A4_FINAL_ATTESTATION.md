# A4 — Attestation finale de clôture

```
OBSERVED_SOURCE_SHA = 535d623703cb3d36ee66849fbd05e3fa0c18a31d
REPORT_COMMIT_SHA   = distinct (ce rapport est committé APRÈS l'observation)
```

Le SHA observé n'a jamais été réaligné sur le commit qui contient ce rapport,
et aucun build n'a été relancé pour les faire coïncider.

## Toolchain de référence

LuaHBTeX 1.17.0 (TeX Live 2023/Debian, development id 7581), avec
`SOURCE_DATE_EPOCH` et `FORCE_SOURCE_DATE` actifs, `TZ=UTC`,
`LC_ALL=C.UTF-8`, `PYTHONHASHSEED=0`. La reproductibilité binaire est
attestée **pour cette toolchain**.

## Reproductibilité binaire des PDF

Défaut initial : deux clones frais au même SHA produisaient 10 PDF de SHA
différents. Cause racine mesurée : LuaTeX tire les deux éléments de `/ID` au
hasard à chaque exécution, ce que `SOURCE_DATE_EPOCH` ne couvre pas.

Correction **au niveau du producteur** (`79267dd9`) : les assembleurs
injectent `\pdfvariable trailerid` avec une identité déterministe dérivée des
sources — schéma, `producer_schema_version`, ouvrage, variante, corps du
master et condensé de chaque source assemblée plus la classe et la charte
canoniques. Contrat complet : `PDF_TRAILER_ID_PREIMAGE_CONTRACT.md`.

| Invariant | Résultat |
|---|---|
| Cibles | 12 |
| Identités uniques | **12** (0 collision) |
| `SELF_REFERENCE` | **NO** — revérifié après remplacement des PDF suivis |
| Indépendance au chemin absolu | **oui** (test sur arbre recopié) |
| Indépendance au `run_id` et à l'horloge | **oui** |
| Sensibilité au contenu | **oui** — source modifiée ⇒ identité différente, restauration ⇒ identité initiale |
| `VISUAL_CHANGE` | **0** — pagination et texte extrait identiques sur les 12 |

## Reproduction hermétique finale

Deux clones frais au SHA scellé, résultats écrits hors des clones.

| Contrôle | FRESH A | FRESH B | A == B |
|---|---|---|---|
| HEAD | `535d6237` | `535d6237` | oui |
| Suite racine | 1147 passed / 0 failed | idem | oui |
| Suite Math | 4698 passed / 0 failed | idem | oui |
| Suite NSI | 2191 passed / 0 failed | idem | oui |
| `source_digest` d'inventaire | `sha256:56435df0a27c718dc…` | idem | oui |
| `broken_meta` | 0 | 0 | oui |
| fail-on-new | rc 0, 89 dettes, 0 nouveauté | idem | oui |
| release-strict | rc 7, 70 raisons | idem | oui |
| Builds | 12/12 PASS | 12/12 PASS | oui |

**`ALL_12_PDF_BYTE_IDENTICAL = YES`** : pour les 12 cibles,
`COMMITTED == FRESH_A == FRESH_B`.

### Divergence de master expliquée

Les 8 masters Mathématiques diffèrent entre A et B par **une seule ligne** :
`\typeout{NEXUS_BUILD_RUN:<aléatoire>}`, marqueur de run privé écrit dans le
**journal** et jamais dans le PDF. La ligne `\pdfvariable trailerid` est
identique dans les deux clones, et les PDF sont byte-identiques — preuve
directe que ce marqueur n'atteint pas la sortie. Les 4 masters NSI sont
strictement identiques.

## Réconciliation des méthodes

```
original missing targets      = 59
created from original         = 58
original missing now          = 0
superseded (mis-tag corrigé)  = 1   → 1SPE-TRIGONOMETRIE M3 remplacée par M4
newly discovered valid        = 15  (11 complétion C_i↔M_i + 4 découvertes à la clôture)
replacement of mis-tag target = 1
created total                 = 74
rewritten existing            = 15  (M1 contaminées « Dériver une fonction composée »)
touched total                 = 89
duplicates                    = 0
without capacity              = 0
extra unexplained             = 0
```

Équation : **74 créées + 15 réécrites = 89 touchées**. Le jeu initial de 59
cibles est intégralement soldé : 58 créées directement, 1 supersédée avec
preuve (commit `813304c6`). Aucune contradiction ne subsiste.

## Références entrantes

470 références légitimes au départ : **470 résolues, 0 non résolue**, dont 3
reclassées avec preuve (retag `C3/M3 → C4/M4`). Aucune suppression sans
justification, aucune cible ambiguë, aucune cible archive ou prototype.

## Gouvernance de la dette de revue

```
REFERENCE_BASELINE        = audit/ANOMALIES_BASELINE.json
sha256 avant campagne     = 3e9225668121a67c2fdea1248ec420ff16bd3910c8557e3a98df8bb7997250e1
sha256 après campagne     = 3e9225668121a67c2fdea1248ec420ff16bd3910c8557e3a98df8bb7997250e1
REFERENCE_BASELINE_MUTATED = NO
```

Politique humaine : `A4_METHOD_REVIEW_DEBT_POLICY.md#decision-a4-method-review-debt-2026-08-19`,
digest `sha256:07597ede…`, inchangée depuis son scellement.

89 qualifications **dérivées** par prédicat machine. `approved_by` référence
la politique de classe, jamais une personne :
`IMPLICIT_HUMAN_APPROVALS = 0`, `FORGED_HUMAN_SIGNATURES = 0`.

Sémantique clarifiée : `baseline_sha` est une **ancre constante** vers le
champ `git_sha` de la baseline de référence (`7752988a…`) — jamais une
nouvelle baseline approuvée ; `control_digest` est le digest d'enveloppe du
registre dérivé, recalculé à chaque matérialisation machine.

## Packets de revue

89 fiches touchées, **89 packets présents**, **89 liés au SHA courant de leur
fiche**, **0 périmé**. Statuts : **89 `needs_review`, 0 `approved`**.

## Inventaire final (rendu frais)

| Compteur | Valeur |
|---|---|
| RAW | 2971 |
| BLOCKING | 2971 |
| NONBLOCKING | 0 |
| **broken_meta** | **0** |
| blocking_statuses | 2222 |
| missing_corrections | 0 |
| unclassified_types | 660 |
| unassembled | 52 |
| orphans | 12 |
| duplicate_assembly | 0 |
| broken_latex | 0 |
| cycles | 0 |
| context_mismatches | 3 |
| unattributed_pdfs | 22 |

Aucun de ces compteurs résiduels n'a été remédié : ils relèvent des lots
suivants, non démarrés.

## Verdict

`A4_TECHNICAL = PASS` · `HERMETIC = YES` · `D7 = BLOCKED` ·
`NEXT_LOT = NOT_STARTED`.

La dette de revue des 89 fiches reste **bloquante pour la release** : c'est
`release-strict` (exit 7, 70 raisons, aucun nouveau groupe de raison) qui
porte le NO-GO, ainsi que les états déclarés en attente de décision humaine
(D7 visuel, revue de contenu 1NSI, gouvernance des statuts 1NSI, dette QCM).
