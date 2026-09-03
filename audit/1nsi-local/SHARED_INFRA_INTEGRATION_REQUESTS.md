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

**Fixtures négatives à conserver.** cible inexistante → `ORPHAN_CO` ;
cible d'un autre chapitre → échec ; deux références → `MISMATCHED_CONTENT`.

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

## INT-004 — Cinq copies de remédiation figurent dans une campagne scellée

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

**Garde en place.** `NSI/tests/test_1nsi_types_construits_remediation_canonicity.py`
porte deux `xfail(strict=True)` : ils redeviennent bloquants dès que le défaut
est corrigé, et échouent si quelqu'un les neutralise.
