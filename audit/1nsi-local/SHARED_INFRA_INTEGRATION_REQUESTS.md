# Demandes d'intégration — branche satellite `codex/urgent-1nsi-content`

Base : `ec12c2b5bdac1ce6a7b77a42c5438c6564f4e3d9`. Aucune de ces demandes n'est
implémentée ici : elles touchent une surface partagée ou une gouvernance dont
cette branche n'est pas propriétaire. L'instance coordinatrice intègre.

---

## INT-001 — `ex_co_graph` ignore les cibles de type `remediation`

**Problème.** `scripts/build_ex_co_graph.py` n'indexe comme cible valide d'un
`exercice_ref` que les objets de rôle `exercices` (ligne ~157). Un corrigé de
remédiation, dont le `exercice_ref` désigne un objet `type_objet: remediation`
existant et correctement lié, est classé `ORPHAN_CO`.

**Exemples courants qui échouent.**
`1NSI-ADGK-RE-C1-CORRIGE` → `1NSI-ADGK-RE-C1` (existe, `type_objet: remediation`) ;
idem `RE-C2`, `RE-C3` sur `1NSI-ALGO-DICHO-GLOUTON-KNN`, et les six `RE-Cn-CORRIGE`
de `1NSI-ALGO-PARCOURS-TRIS`.

**Sémantique attendue.** Un corrigé peut viser un `exercice` **ou** une
`remediation` du même chapitre. La cardinalité et l'unicité restent inchangées.

**Fixture positive attendue (doit passer).**

```
corrigé  1NSI-ADGK-RE-C1-CORRIGE
  META   exercice_ref = "1NSI-ADGK-RE-C1"
  cible  1NSI-ADGK-RE-C1, type_objet = "remediation", même chapitre
  ⇒ ANSWER_COVERAGE_ESTABLISHED, et non ORPHAN_CO
```

**Fixtures négatives à conserver (doivent continuer d'échouer).**

```
cible absente du chapitre            → ORPHAN_CO
cible dans un autre chapitre         → échec
deux références dans la même META    → MISMATCHED_CONTENT
cible de type ni exercice ni remediation → ORPHAN_CO
```

Le correctif minimal est d'élargir l'ensemble des rôles indexés comme cible, sans
toucher à la cardinalité ni à l'unicité.

**Chapitres affectés.** 9 faux `ORPHAN_CO` sur les deux chapitres
d'algorithmique ; à vérifier sur les 8 autres après correction.

**Impact.** `RELEASE_BLOCKING_FOR_TRUTHFUL_AUDIT = YES` — classé
`P1_EX_CO_GRAPH_TARGET_TYPE_BLINDNESS`.

---

## INT-002 — `build_manifest.py` : `source_digest` incohérent

**Problème.** `audit/gates/release-strict.json` s'interrompt sur
`inventaire_indisponible : source_digest du manifeste de build incohérent`.
Cinq dimensions sur sept (`mathematics`, `pedagogy`, `print`, `regulation`,
`visual`) restent `not_covered` : jamais évaluées.

**Statut exact.** `NOT_EVALUATED_DUE_TO_UPSTREAM_PROVENANCE_BLOCKER` — ni vert
ni rouge. Ne bloque pas l'authoring 1NSI local.

**Producteur responsable.** `scripts/build_manifest.py` (trois SHA concurrents
observés dans l'artefact, dont un à 1 449 commits de la base).

---

## INT-003 — Producteurs de tableau de bord sans SHA source

**Problème.** Quatre artefacts de pilotage ne s'auto-lient à aucun SHA :
`PUBLISH_READINESS_CHAPTER_MATRIX`, `release-strict`, `require-clean`,
`HUMAN_REVIEW_QUEUE`. Impossible de dire s'ils décrivent l'arbre courant.

**Conséquence observée.** La matrice annonçait 1SPE à 3/10 alors que le
recalcul à la base donne 10/10 : elle précédait la réémission des seize reçus
SymPy (`4ca0e6d9`). Un artefact non lié a servi de chiffre de pilotage.

**Attendu.** Chaque producteur inscrit le SHA de l'arbre observé, et le
consommateur refuse un artefact dont le SHA ne correspond pas.

**Annexe de nomenclature.** `require-clean.blocker_count` compte en réalité les
fichiers suivis modifiés (`reasons[] = modified_tracked:<fichier>`) : à renommer
`dirty_tracked_files`. Dette de nommage, pas bloqueur de contenu.

---

## INT-004 — FERMÉ le 2026-09-04 — cinq copies de remédiation redondantes

**Problème.** `1NSI-TYPES-CONSTRUITS` porte six objets de remédiation aux corps
**rigoureusement identiques** (md5 du corps : `aa1a0b1eeab8`) :

| Objet | Capacités déclarées |
|---|---|
| `1NSI-TC-REM` (canonique) | C1, C2, C3, C4, C5 |
| `1NSI-TC-REMED-01` … `-05` | C1, puis C2, C3, C4, C5 |

Le document canonique traite réellement R1(C1) à R5(C5). Les cinq copies ne
sont que des duplicats déclarant chacune une capacité : la machine y lit cinq
remédiations distinctes et crédite la couverture de rôle de C1 à C5 alors qu'un
seul document existe. `audit/P0_CONTENT_CLONE_LEDGER.json` les enregistre déjà
en `canonical_object_status: AMBIGUOUS` (groupe CG-0091).

**Correctif souhaité.** Retirer `1NSI-TC-REMED-01` à `-05` ; `1NSI-TC-REM` suffit
et couvre les cinq capacités. Aucun contenu pédagogique n'est perdu.

**Pourquoi ce n'est pas fait ici.** Le retrait a été réalisé, vérifié
(clones 0, faux crédits 0, couverture des cinq capacités maintenue, code
121 OK / 0 FAIL), puis **annulé** : il fait tomber quinze tests de gouvernance
1NSI parce que les cinq fichiers appartiennent à une campagne de relecture
humaine **scellée** (`test_1nsi_content_reviews.py` : 339 sources objet,
10 contrats, digests sha256) et à `audit/1NSI_STATUS_GOVERNANCE_PENDING.json`
(`objects_total: 807`). Modifier ces artefacts pour verdir une branche
satellite reviendrait à réécrire des preuves de relecture.

**Ce que l'intégration doit faire.** Retirer les cinq copies **et** resceller la
campagne de relecture 1NSI sur le nouvel ensemble de sources (334 objets), en
consignant le motif du rescellement.

### Clôture

Autorisée par décision humaine, sous preuve sémantique préalable du bundle
canonique. Appliquée en trois commits : `0ca6f92b` (retrait), `0aced484`
(ré-observation des registres), `d051fd9e` (dernière capacité manquante).

**Preuve sémantique.** `1NSI-TC-REM` porte cinq sections visant cinq
misconceptions distinctes, alignées sur C1…C5 et utilisables isolément. Les cinq
tâches de réinvestissement ont été **exécutées** : 17/17.
`LEGITIMATE_MULTI_CAPACITY_REMEDIATION_BUNDLE = YES`.

**Ensemble de sources, mesuré.** `807 → 802` objets, 10 contrats inchangés.
`REMOVED` = exactement les cinq copies, `ADDED` = 0, `UNCHANGED` = 802.
`OLD_SET_DIGEST sha256:7493cc39…` → `NEW_SET_DIGEST sha256:93b468ab…`.
Le chiffre « 339 → 334 » annoncé au checkpoint précédent était **faux** : cette
attente est court-circuitée par `_guard_campaign_pending()` tant que la campagne
dérive. Mesurer, ne pas présumer.

**Mécanisme.** `scripts/build_1nsi_pending_state_reobservation.py` lit son commit
de cause dans l'historique git : il a reconnu `0ca6f92b` et ses cinq
suppressions. Aucune ligne de code partagée n'a été modifiée.
`SEALED_FIELDS_MUTATED 0`, `UNEXPLAINED_DELTA 0`.

**Ancien scellement préservé.** `audit/1NSI_PENDING_STATE_REOBSERVATION.json`
conserve `declared` face à `observed` sur les neuf champs, avec SHA, sujet et
date du commit de cause. Rien de réécrit rétrospectivement.

**Aucun travail humain perdu.** `HUMAN_RECEIPTS 0` avant comme après,
`review_a`/`review_b` `PENDING_UNASSIGNED`, `publication_approval false`.

**Dette soldée.** `EXPECTED_XFAIL_FOR_INT004 = 0` : les deux `xfail` sont
devenus des invariants verts, plus un test interdisant le retour des copies.


---

## INT-005 — `qcm_diagnostics` ne porte aucune capacité

**Problème.** `1NSI-TC-QCM-DIAG` est le seul objet `qcm_diagnostics` du corpus
NSI et ne déclare aucune capacité, ce qui le laisse en `UNKNOWN` dans la
couverture par capacité.

**Pourquoi ce n'est pas corrigé ici.** Le fichier porte en tête
« Fichier genere par scripts/build_qcm_tex.py — ne pas editer a la main » et un
champ `genere_depuis` pointant le JSON du QCM. La correction relève du
générateur, pas du contenu ; l'éditer à la main serait écrasé au prochain build.

**Correctif attendu.** `build_qcm_tex.py` propage dans la META de l'objet
diagnostics les capacités du QCM dont il dérive — ici C1 à C5, déjà déclarées
par `1NSI-TC-QCM`.

**Portée.** Un seul objet aujourd'hui ; le devient pour chaque chapitre dès que
d'autres diagnostics seront générés.


---

## INT-006 — La ré-observation ne modélise que les suppressions

**Problème.** `scripts/build_1nsi_pending_state_reobservation.py` n'accepte un écart
entre registre déclaré et arbre observé que s'il **égale le nombre de fichiers supprimés**
par le commit de cause :

```python
row["declared"] - row["observed"] != cause["deleted_tex_files"]   # sinon UNEXPLAINED
```

Le commit de cause est lui-même cherché en `--diff-filter=D`. Un lot qui **ajoute** du
contenu authentique — ce qui est précisément l'objet de la campagne — est donc
inattribuable : `UNEXPLAINED_DELTA` reste non nul et quinze tests de gouvernance 1NSI
échouent, alors qu'aucun défaut de contenu n'existe.

**Observé.** Après le lot WEB-IHM : 99 copies retirées puis 19 objets authentiques écrits
(4 méthodes, 8 remédiations, 8 corrigés de remédiation, moins le stub retiré).
`UNEXPLAINED_DELTA = 4`, `DELETED_TEX_FILES_IN_CAUSE_COMMIT = 1`.

**Sémantique attendue.** L'écart doit être explicable par le **bilan net** des commits
depuis la dernière observation — suppressions *et* ajouts — et non par les seules
suppressions du dernier commit destructeur. Le commit de cause devrait être cherché en
`--diff-filter=ADM`, et l'écart comparé au net.

**Fixtures.**

```
lot purement destructif   (−99, +0)   → UNEXPLAINED_DELTA = 0   (déjà le cas)
lot purement additif      (−0, +19)   → UNEXPLAINED_DELTA = 0   (échoue aujourd'hui)
lot mixte                 (−1, +19)   → UNEXPLAINED_DELTA = 0   (échoue aujourd'hui)
écart sans commit de cause            → UNEXPLAINED_DELTA > 0   (doit rester bloquant)
```

**Pourquoi ce n'est pas corrigé ici.** Le producteur est partagé. Le corriger depuis la
branche satellite reviendrait à modifier le moteur de gouvernance pour verdir ma propre
branche.

**Conséquence assumée.** Les deux registres 1NSI restent périmés sur cette branche après
tout lot de rédaction, et quinze tests de gouvernance échouent pour cette seule raison.
Aucun de ces échecs ne signale un défaut de contenu ; ils disparaîtront à l'intégration,
une fois la ré-observation relancée par le coordinateur.

---

## Mise à jour du 2026-09-04 (instance B2, après les dix chapitres)

### INT-006 — INTÉGRÉ LOCALEMENT par cherry-pick

`ba89af6b` (branche `codex/shared-infra-integration`, instance C) est
cherry-pické tel quel en `4863adc0`, avant le sweep manuel, conformément à
l'instruction de reprise. Les deux registres en conflit ont été pris dans la
version livrée puis **régénérés par le producteur** (`--apply`, commit
`5d1643ce`) : `SOURCES_ADDED=92`, `SOURCES_REMOVED=337`, `SOURCES_MODIFIED=32`,
`UNEXPLAINED_DELTA=0`, `HUMAN_RECEIPTS_AFFECTED=0`, `SEALED_FIELDS_MUTATED=0`.

Effet mesuré : la suite NSI passe de **15 failed / 1733 passed** à
**0 failed / 1748 passed**. Les quinze échecs de gouvernance étaient bien
imputables à INT-006 et à rien d'autre.

### INT-001 — mesure current, toujours ouvert côté shared

Séparation faite sur l'arbre current (`REAL_ORPHAN_CO` vs
`SHARED_PRODUCER_FALSE_POSITIVE`) :

```
ANSWER_COVERAGE_OK                 101
REAL_ORPHAN_CO                       0
SHARED_PRODUCER_FALSE_POSITIVE      48   (tous : corrigés RE-Cn-CORRIGE -> remédiation RE-Cn du même chapitre)
```

Les 48 faux positifs se répartissent sur les dix chapitres (3 ADGK, 6 APT,
5 ARCHOS, 7 LANGAGE, 4 PM, 5 RESEAUX, 4 TABLES, 5 TYPES-BASE, 9 WEB-IHM,
0 TC). Le correctif shared existe (`e9490cb8` sur
`codex/shared-infra-integration`) ; il n'est **pas** cherry-pické ici faute
d'instruction explicite. Après intégration, attendu : 0.

### INT-005 — inchangé

`1NSI-TC-QCM-DIAG` reste sans capacité. Le correctif shared existe
(`b4483b61`) ; non cherry-pické ici. Aucune compensation locale.

### INT-007 — garde racine `test_1nsi_content_untouched` (nouveau, mineur)

**Problème.** `tests/test_1nsi_content_untouched.py::test_the_baseline_is_the_commit_the_repository_itself_named`
échoue sur cette branche : `audit/1NSI_CONTENT_UNTOUCHED.json` pointe une
baseline antérieure au registre de ré-observation régénéré (INT-006).

**Pourquoi non corrigé ici.** Régénérer l'artefact (`--check` donne
`CONTENT_FILES_CHANGED=0`, `SHARED_TEMPLATE_FILES_CHANGED=0`) ferait tomber
`test_the_shared_template_change_is_reported_not_hidden`, qui **exige**
`SHARED_TEMPLATE_FILES_CHANGED > 0` — une assertion propre à la campagne 1SPE.
Le correctif shared existe (`dad673c7`, « report the shared-template change
count instead of asserting it positive ») ; non cherry-pické ici.

**Attendu à l'intégration.** Cherry-pick `dad673c7`, puis
`python3 scripts/build_1nsi_content_untouched.py` ; les 26 tests du module
doivent passer. Aucun contenu 1NSI n'est concerné.

### Registres racine régénérés (aucune ligne de code partagée modifiée)

`audit/NSI_COUPLED_ALGORITHMICS_REVIEW_DEBT.json` et
`audit/NSI_CROSS_DISCIPLINE_CONTENT_LEDGER.json` épinglaient trois condensats
périmés (les trois méthodes DICHO dont `1bce9de4` a corrigé la META).
Régénérés par leurs producteurs en `987edb6e` : six lignes de diff, aucun
verdict changé.

---

## Intégration autorisée du 2026-09-04 (instance B2, second lot)

Pré-intégration : arbre propre, branche `codex/urgent-1nsi-content`,
`PRE_INTEGRATION_HEAD = a587186c`. INT-006 (`ba89af6b`) était déjà intégré en
`4863adc0` ; il n'a pas été re-cherry-pické.

| Ordre | Commit C | Commit local | Objet | Conflit |
|---|---|---|---|---|
| 1 | `ba89af6b` | `4863adc0` (déjà fait) | INT-006 ré-observation par ensembles | dérivés seulement, régénérés |
| 2 | `dad673c7` | `f89e661d` | garde `content_untouched` : compte rapporté, non imposé | aucun |
| 3 | `e9490cb8` | `ef5ed34e` | INT-001 cible `remediation` valide dans `ex_co_graph` | aucun |
| 4 | `b4483b61` | `16931ca3` | INT-005 `qcm_diagnostics` hérite les capacités du QCM | aucun |

Puis :

- `50fe291d` — commit de cause : `1NSI-TC-QCM-DIAG` régénéré par le générateur
  (une ligne, la META hérite `1NSI-TYPES-CONSTRUITS-C1..C5`). Ensemble exact des
  générés affectés : ce seul fichier ; les dix `*-QCM.tex` 1NSI sont synchrones
  (`--check` vert).
- `61577bfd` — dérivés régénérés par leurs producteurs : registres de
  ré-observation, `content_untouched`, `EX_CO_GRAPH`. Idempotence prouvée :
  `--check` rend `CURRENT` / `NO` / `current` et n'écrit rien ; arbre propre.

### INT-001 — FERMÉ localement

`FALSE_REMEDIATION_ORPHANS = 0 / 48`, `ORPHAN_CO = 0`, `UNKNOWN = 0` sur les
149 relations 1NSI. Une cible inexistante échoue toujours
(`tests/test_ex_co_graph.py`, 14 passed).

### INT-005 — FERMÉ localement

Un seul objet `qcm_diagnostics` dans le corpus ; régénéré, capacités héritées.

### INT-007 — FERMÉ localement

`test_1nsi_content_untouched` : 26/26 après `dad673c7` et régénération.

### Unités

```
REOBSERVATION_SOURCE_FILE_COUNT = 468   (458 objets + 10 contrat.yaml)
OBJECT_COUNT (objects_total)    = 458
```

L'ancien `807 → 802` était un `objects_total` ; en fichiers source il aurait
valu `817 → 812`. Les deux unités diffèrent toujours des dix contrats.

### INT-008 — `P0_CONTENT_CLONE_LEDGER` périmé (nouveau, artefact global de A)

**Problème.** `build_ex_co_graph` hérite la classe `CLONE` de
`audit/P0_CONTENT_CLONE_LEDGER.json` (`objects_on_invalid_credit` +
`objects_with_indeterminate_credit`), dont la dernière génération (`caa7be76`,
2 septembre) précède tous les retraits de copies synthétiques. Sur cet arbre :
42 relations 1NSI portent `CLONE`, 84 chemins épinglés, **429 partenaires
historiques, 0 encore existant**. Le scan exact current des 477 objets 1NSI
donne 0 groupe.

**Pourquoi non corrigé ici.** Le registre est un artefact de collection
globale, propriété de l'intégration. Il n'est ni régénéré ni édité sur cette
branche.

**Attendu à l'intégration.** `scripts/build_p0_content_clone_ledger.py` puis
`build_ex_co_graph` : les 42 `CLONE` 1NSI doivent tomber à 0 sans qu'aucune
source ne change.
