# Réconciliation WIP ↔ amont

Données : `audit/WIP_UPSTREAM_RECONCILIATION.json` (généré par
`scripts/reconcile_wip_upstream.py`, ne modifie rien) et
`audit/WIP_DROPPED_DELTA_LEDGER.json`.

| | |
|---|---|
| `WIP_BASE_SHA` | `761508d923d74fd3d93fc055b3f3b1857fb251e1` |
| `UPSTREAM_SHA` | `dc6735d1` (`codex/t2-current-audit-continue`) |
| `WIP_FILE_COUNT` | 59 |
| `WIP_OVERLAP_WITH_UPSTREAM` | 58 |
| `WIP_ONLY` | 1 |
| `WIP_PATCH_SHA256` | `370e247538e8ea8ddce60aaf63bf24e1cd23c054c28646355e3ac589a81a39d7` |
| Sauvegarde hors dépôt | `/tmp/nexus-wip-reconciliation-20260826T224657Z/` (patch + 59 fichiers byte-for-byte + 50 non suivis) |

`LATEST_VALID_SIDE_CAR_HEAD = dc6735d1`, et
`git merge-base --is-ancestor c667f12b dc6735d1` → **PASS**. Le chapitre
`1SPE-SUITES` est identique entre `c667f12b` et `dc6735d1` : le gel reste valide
sur la tête de développement.

## Classification des 59 fichiers

| Classe | Nombre |
|---|---:|
| `GENERATED_DERIVATIVE` | 35 |
| `TRUE_CONFLICT` | 23 |
| `WIP_ADDS_VALID_DELTA` | 1 |
| `UPSTREAM_SUPERSEDES_WIP` | 0 |
| `SEMANTICALLY_EQUIVALENT` | 0 |
| `WIP_OBSOLETE_OR_WRONG` | 0 |
| `WIP_ONLY` | 0 |
| `OTHER_EXPLICIT` | 0 |
| `UNKNOWN` | **0** |

Les 35 `GENERATED_DERIVATIVE` sont les `*-QCM.tex`. Ils portent l'en-tête
« Fichier généré par `scripts/build_qcm_tex.py` — ne pas éditer à la main » et un
`genere_depuis` pointant leur `.json`. Ils ne se réconcilient pas : ils se
régénèrent une fois leur source arbitrée.

## Comparaison sémantique des QCM, question par question

16 QCM `.json` sont en jeu, soit 123 questions touchées d'un côté ou de l'autre :

| Verdict | Questions |
|---|---:|
| `UPSTREAM_ONLY` | 85 |
| `BOTH_DIVERGED` | 35 |
| `BOTH_CONVERGED` | 3 |
| `WIP_ONLY_CHANGE` | **0** |

**Aucune question n'a été modifiée par le WIP sans l'avoir été aussi en amont.**
Le WIP n'apporte donc aucune couverture de question qui lui soit propre — mais il
apporte des champs que l'amont n'a pas, voir plus bas.

Les 35 divergences se répartissent en deux familles nettes :

- **18** — l'amont a remplacé l'énoncé ou les options. Le delta WIP porte sur une
  question qui n'existe plus sous cette forme → `NO_LONGER_REQUIRED`.
- **17** — énoncé et options identiques des deux côtés ; seuls les textes de
  diagnostic diffèrent. C'est là que se trouve le delta portable.

### Les six « désaccords de clé » n'en sont pas

Sur `1SPE-EXPONENTIELLE` Q8 et Q15, `1SPE-SUITES` Q3, `TEXP-GRAPHES` Q3 et
`TSPE-SUITES-LIMITES` Q4, le champ `correcte` diffère **parce que l'amont a
remplacé la question**. Le WIP a conservé la question de base sans y toucher. Ce
ne sont pas des désaccords scientifiques sur une même question.

La seule exception est traitée ci-dessous.

## Couverture des renvois de remédiation — ni l'un ni l'autre n'est un sur-ensemble

| Arbre | Distracteurs diagnostiqués | Avec `renvoi` | Sans |
|---|---:|---:|---:|
| BASE | 990 | 831 | 159 |
| AMONT | 993 | 885 | 108 |
| WIP | 990 | 891 | **99** |

L'amont a complété 51 distracteurs depuis la base, le WIP 60, **sur des ensembles
différents**. C'est la démonstration concrète que « plus récent » ne vaut pas
« meilleur » : le WIP porte 45 renvois que l'amont n'a pas.

## Delta à porter — mécaniquement dérivable, aucun arbitrage requis

| Objet | Portée | Justification |
|---|---|---|
| 45 renvois de remédiation | `TSPE-GEOMETRIE-ESPACE` (15), `TSPE-LOGARITHME` (15), `TSPE-PRIMITIVES-EQDIFF` (12), `TSPE-DERIVATION-CONVEXITE` (3) | énoncé et options identiques des deux côtés ; le cahier exige un renvoi par distracteur incorrect |
| `TSPE-DERIVATION-CONVEXITE` Q3 A/C | renvoi affiné : amont `C1`, WIP `C1, dérivée d'une fonction composée` | raffinement strict |
| `1SPE-VARALEA-CO-048.tex` | assertions supplémentaires du bloc `BEGIN-VERIFY` | la correction P0 est **déjà en amont** (commit `691b6354`) ; le WIP ajoute `V == 77760000`, `round(σ) == 8818`, la décomposition `E_Y`/`E_Y2`/`V_Y`, `\|σ_S − 3943.602\| < 1e-3` et `σ/σ_S == √5` |
| `scripts/inventory_collection.py` | enregistrement des deux schémas human-review | sans lui, `test_v1_schema_directory_contains_exactly_the_registered_contracts` échoue |

## Delta abandonné — chaque abandon a sa raison

| Portée | Raison | Preuve |
|---|---|---|
| 85 questions `UPSTREAM_ONLY` | `SUPERSEDED_BY_CORRECT_UPSTREAM` | la version WIP y est identique à la base |
| 35 `*-QCM.tex` | `NO_LONGER_REQUIRED` | fichiers générés, régénérés après arbitrage de leur source |
| 18 questions à énoncé remplacé | `NO_LONGER_REQUIRED` | le delta porte sur une question qui n'existe plus |
| `1SPE-SUITES` Q9, clé de correction | `SCIENTIFICALLY_WRONG` | voir ci-dessous |
| `TEXP-GRAPHES` Q4 A/B/C, renvoi | `SUPERSEDED_BY_CORRECT_UPSTREAM` | le WIP n'a pas touché ce champ |

`silent_drops = 0`.

### `1SPE-SUITES` Q9 — pas un défaut, mais l'amont est plus clair

Le WIP conserve l'énoncé et les options de la base mais bascule `correcte` de
**C** vers **B**, et déplace les diagnostics de `{A,B,D}` vers `{A,C,D}`. Il fait
donc de :

> B. « Une suite géométrique peut comporter un terme nul. »

la réponse exacte, et reclasse en distracteur :

> C. « Pour montrer qu'une suite est géométrique, il faut calculer $u_{n+1}/u_n$
>    et vérifier que ce quotient est constant pour tout $n$. »

**Correction de ma qualification initiale.** J'avais classé ce delta
`SCIENTIFICALLY_WRONG` ; c'était faux. Sous la définition canonique
$u_{n+1}=q\,u_n$, une suite géométrique **peut** comporter un terme nul : il
suffit de $q=0$, ou d'un terme initial nul. Le quotient $u_{n+1}/u_n$ n'est
qu'une caractérisation **conditionnelle**, valable lorsque les termes sont non
nuls ; ce n'est pas la définition générale.

L'amont est retenu parce qu'il lève l'ambiguïté — il remplace l'option C par la
définition « il existe un réel $q$ tel que, pour tout $n$, $u_{n+1}=q\,u_n$ »,
remplace B par « le quotient $u_{n+1}/u_n$ peut dépendre de $n$ », et garde
`correcte = C`. Classification finale :
`SUPERSEDED_BY_CLEARER_UNAMBIGUOUS_UPSTREAM`, sévérité `NOT_A_DEFECT`.

Quatre régressions verrouillent désormais la définition canonique, et un
contrôle balaie les 35 chapitres : `ZERO_TERM_MISCONCEPTION = 0`,
`QUOTIENT_AS_GENERAL_DEFINITION = 0`. Les trois occurrences qui subsistaient sur
l'arbre périmé étaient déjà corrigées en amont.

## Les deux décisions, rendues le 2026-08-27

### 1. `TEXP-GRAPHES` Q3 — **version amont conservée**

Le WIP corrige l'énoncé en ajoutant **« connexe »** :

> « Un graphe **connexe** admet une chaîne eulérienne si et seulement si le
>   nombre de sommets de degré impair est 0 ou 2. »

C'est une correction mathématique réelle : sans l'hypothèse de connexité,
l'équivalence est fausse.

L'amont a **remplacé entièrement Q3** par une question sur la matrice
d'adjacence, retirant la question eulérienne du QCM.

**Décision rendue : la version amont est conservée.** Elle est directement
alignée sur le contenu officiel Mathématiques expertes — graphes, connexité,
matrices, matrice d'adjacence. Le delta WIP est classé
`SUPERSEDED_BY_CORRECT_UPSTREAM`, et **non** `SCIENTIFICALLY_WRONG` : il était
mathématiquement correct, mais visait une question volontairement remplacée.

Une question eulérienne pourra être réintroduite plus tard comme **objet
séparé**, après audit du chapitre : hypothèse de connexité correcte, absence de
doublon, rôle programme explicite, valeur pédagogique réelle. Aucune
réintroduction automatique.

### 2. `1SPE-GEOMETRIE-REPEREE` — **migration atomique effectuée**

C'est le seul fichier `WIP_ONLY`. Il renomme les cinq `ref_capacite` de
`1SPE-GEOREP-C*` vers `1SPE-GEOMETRIE-REPEREE-C*`.

- Le référentiel `capacites_1SPE_GEOMETRIE_REPEREE.json` porte bien
  `1SPE-GEOMETRIE-REPEREE-C*` → le WIP aligne le contrat sur le référentiel.
- Mais **109 fichiers objets** du chapitre référencent encore `1SPE-GEOREP-C*`,
  et l'amont conserve `1SPE-GEOREP-C*` dans le contrat.

**Décision rendue : migration complète du graphe de consommateurs, sans alias
runtime.** Le delta est reclassé
`VALID_DELTA_REQUIRING_ATOMIC_GRAPH_MIGRATION`, puis appliqué.

Le dénominateur exact a été recalculé avant mutation : **54 fichiers**, et non
109 ni 229. Le motif large `1SPE-GEOREP-C` capture aussi les identifiants
d'objets (`1SPE-GEOREP-CO-*`), d'où les estimations initiales. Les références de
capacité se comptent avec la borne `(?![0-9A-Za-z-])`.

| Disposition | Fichiers | Occurrences |
|---|---:|---:|
| contrat de chapitre — édité | 1 | 5 |
| exercices, champ META `capacites` — édités | 50 | 50 |
| matrice de couverture officielle — éditée | 1 | 9 |
| inventaire et agrégat de couverture — régénérés | 2 | 266 |

Après migration : `LEGACY_GEOREP_CAPACITY_REF = 0`, `BROKEN_CAPACITY_REF = 0`,
`AMBIGUOUS_CAPACITY_ALIAS = 0`, `RUNTIME_CAPACITY_ALIAS = 0`. Les cinq seules
occurrences restantes de la forme courte sont les champs `old_id` du ledger de
migration. Neuf tests A→I verrouillent le résultat.

## Portage des renvois : 9 retenus sur 45

Chacun des 45 candidats a été confronté aux gates. **9 passent** et sont portés
(`TSPE-LOGARITHME` 6, `TSPE-PRIMITIVES-EQDIFF` 3). **36 sont rejetés** : 33 pour
désalignement de capacité — le renvoi pointe `C1` alors que la question porte
`C2`, `C3`, `C4`, `C5`, `C7`, `C11`, `C12` ou `C13` — et 3 parce que l'objet de
remédiation cible n'existe pas. **Aucune cible n'a été fabriquée** ; les 36
findings restent ouverts.

Deux portages initialement validés ont été **annulés après exécution de la
matrice de tests** : `TSPE-DERIVATION-CONVEXITE` Q3 A et C. Un test amont épingle
par égalité exacte `renvoi == "C1"` pour ces questions. Les deux formes de renvoi
coexistent dans le corpus — 373 codes bruts, 474 libellés — mais celles-ci sont
contractuellement en forme brute. Le gate « target canonical » a été complété en
conséquence.

## État final

Les 59 fichiers ont tous une disposition. `UNKNOWN = 0`,
`LOST_VALID_DELTA = 0`, `SILENT_DROP = 0`. Le report a été appliqué sur
`dc6735d1` en commits atomiques, sans push ni merge.
