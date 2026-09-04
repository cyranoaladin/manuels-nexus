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
