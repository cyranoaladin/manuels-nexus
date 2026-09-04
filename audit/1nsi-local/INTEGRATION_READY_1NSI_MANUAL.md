# INTEGRATION_READY_1NSI_MANUAL — branche satellite `codex/urgent-1nsi-content`

Produit par l'instance B2 le 2026-09-04. Ce document n'approuve rien : il décrit
un état machine local et ce qu'il reste à faire hors de cette branche.

## Verdict machine

```
1NSI_MACHINE_CONTENT_COMPLETE_LOCAL = YES          (10 / 10 chapitres)
GOVERNANCE_CURRENT                  = CURRENT_AFTER_INT006_INT007_INT001_INT005_LOCAL_CHERRY_PICKS
NSI governance tests                = GREEN  (1748 passed / 0 failed ; racine 77 passed / 0 failed)
INT006_failures = 0   INT001_false_orphans = 0   INT005_stale_diagnostics = 0   UNKNOWN = 0
1NSI_PRINT_READY                    = NOT_CLAIMED
1NSI_PUBLISH_READY                  = NOT_CLAIMED
```

Reste hors de portée de cette branche : intégration par A, INT-008 (registre
global de clones périmé, propriété de A), INT-002 / INT-003 (hors contenu),
20 verdicts humains, D7, build final, prépresse, reproductibilité.

## Lot d'intégration autorisé (2026-09-04, après le milestone)

| Ordre | Commit C | Commit local | Objet |
|---|---|---|---|
| 1 | `ba89af6b` | `4863adc0` (déjà intégré avant le sweep) | INT-006 |
| 2 | `dad673c7` | `f89e661d` | garde `content_untouched` |
| 3 | `e9490cb8` | `ef5ed34e` | INT-001 |
| 4 | `b4483b61` | `16931ca3` | INT-005 |

Puis `50fe291d` (commit de cause : `1NSI-TC-QCM-DIAG` régénéré, une ligne
META, seul fichier généré affecté) et `61577bfd` (dérivés régénérés par leurs
producteurs : registres de ré-observation, `content_untouched`, `EX_CO_GRAPH`).
Aucun conflit ; idempotence prouvée (`--check` → `CURRENT` / `NO` / `current`,
arbre propre). `HUMAN_RECEIPTS_AFFECTED = 0`.

Unités, tenues séparées : `REOBSERVATION_SOURCE_FILE_COUNT = 468` (458 objets
+ 10 `contrat.yaml`), `OBJECT_COUNT = 458`. L'ancien `807 → 802` était un
`objects_total` ; en fichiers source il aurait valu `817 → 812`.

## Provenance

| | |
|---|---|
| BASE_SHA | `ec12c2b5bdac1ce6a7b77a42c5438c6564f4e3d9` |
| CONTENT_HEAD_SHA | `987edb6efcf1cc65886c85dbdac6d67a932e2ce7` |
| Commits depuis la base | 43 (ordre topologique ci-dessous) |
| Push / PR / merge | aucun |
| Cherry-pick vers A | aucun |
| Cherry-pick depuis C | un seul, INT-006 (`ba89af6b` → `4863adc0`), sur instruction explicite |

Le commit qui contient ce document et les artefacts `audit/1nsi-local/*` est
documentaire ; il ne modifie aucune source de chapitre.

## Ordre d'intégration (topologique, ne pas squasher)

```text
git log --reverse --format='%H %s' ec12c2b5..987edb6e
```

1. `4c7df9df` [TYPES-CONSTRUITS] restore explicit EX/CO metadata links
2. `de4e7039` [TYPES-CONSTRUITS] seal the remediation false-credit finding
3. `780bd9a7` [1NSI] mark the two algorithmic chapters protected-healthy at base SHA
4. `0ca6f92b` [TYPES-CONSTRUITS] remove five semantically redundant remediation copies
5. `0aced484` [TYPES-CONSTRUITS] re-observe the two 1NSI pending registers and close INT-004
6. `d051fd9e` [TYPES-CONSTRUITS] declare the capacity of the last corrige that lacked one
7. `e44be8e3` [1NSI] close INT-004 in the handoff and add the INT-001 fixtures
8. `f55fd910` [TYPES-CONSTRUITS] seal the local machine state and the capacity-role matrix
9. `b0f7cc1d` [1NSI] recompute the risk scheduler from current sources only
10. `16388110` [WEB-IHM] remove 99 synthetic filler copies and restore the true coverage
11. `a99aee0a` [WEB-IHM] re-observe the two pending registers after the filler removal
12. `33b10054` [WEB-IHM] author four real méthodes and retire the 95-character stub
13. `6703e3a7` [WEB-IHM] author the eight missing remediations from documented misconceptions
14. `9cafa435` [WEB-IHM] extend both assessments to the nine capacities and fix two authoring defects
15. `39afe1d0` [1NSI] document INT-006: re-observation cannot attribute authored additions
16. `774c671c` [WEB-IHM] record the two distinct statuses and the delta ledger
17. `cb662c89` [LANGAGE] remove 81 synthetic filler copies and restore the true coverage
18. `96f2fcaf` [LANGAGE] author four real méthodes and retire the 95-character stub
19. `142c26cf` [LANGAGE] author the six missing remediations from documented misconceptions
20. `dab9b096` [LANGAGE] extend both assessments to the seven capacities
21. `ec594a2f` [LANGAGE] record the two distinct statuses and the delta ledger
22. `02b234b8` [LANGAGE] trace the three specification capacities in both assessments
23. `1c491bec` [TYPES-BASE] remove 55 synthetic filler copies and restore the true coverage
24. `8abc056f` [TYPES-BASE] author four real méthodes and retire the 95-character stub
25. `100f1b00` [TYPES-BASE] author the four missing remediations and close the chapter
26. `8fbfeb1a` [ARCHITECTURE-OS] remove 55 synthetic filler copies and restore the true coverage
27. `f602c7d5` [ARCHITECTURE-OS] author four méthodes and fix a pre-existing syntax defect
28. `de23e1bc` [ARCHITECTURE-OS] author four remediations, evaluate the command line, close the chapter
29. `1bce9de4` [DICHO-GLOUTON-KNN] declare the official capacity refs on the three méthodes
30. `57b15caa` [RESEAUX] remove 55 synthetic filler copies and restore the true coverage
31. `f3122cbd` [RESEAUX] author four méthodes and retire the 95-character stub
32. `7f8e4e6d` [RESEAUX] author four remediations, evaluate the IHM capacity, close the chapter
33. `b90bd4f2` [TABLES] remove 42 synthetic filler copies and restore the true coverage
34. `087e9adc` [TABLES] fix six pre-existing defects in the canonical objects
35. `1aba5147` [TABLES] author four méthodes and retire the 95-character stub
36. `30de9677` [TABLES] author three remediations and close the chapter
37. `7b8a62d4` [PROJET-METHODES] establish canonical ownership, then remove 42 filler copies
38. `858c0089` [PROJET-METHODES] author four méthodes
39. `533ae735` [PROJET-METHODES] author three remediations, evaluate the oral capacity, close the chapter
40. `7cbe3337` [1NSI] align the printed duration and barème of six extended evaluations
41. `4863adc0` [governance] support exact added/removed source-set reobservation (cherry-pick d'INT-006)
42. `5d1643ce` [1NSI] re-observe the two pending registers after INT-006
43. `987edb6e` [1NSI] regenerate the two NSI ledgers that pin source digests

44. `b2cba3a1` [1NSI] seal the manual-level sweep and the integration package
45. `a587186c` [1NSI] state that the tracked manual PDFs are not rewritten by this branch
46. `f89e661d` [tests] report the shared-template change count instead of asserting it positive (cherry-pick de `dad673c7`)
47. `ef5ed34e` [governance] ex_co_graph accepts a remediation as explicit correction target (cherry-pick de `e9490cb8`)
48. `16931ca3` [qcm] propagate the QCM capacities to the generated diagnostics sheet (cherry-pick de `b4483b61`)
49. `50fe291d` [1NSI] regenerate QCM diagnostics capacity metadata after INT-005
50. `61577bfd` [1NSI] regenerate the derived registers after INT-001, INT-005 and INT-007
51. (ce commit) [1NSI] record the integration lot in the sweep and the package

Commits 1–29 : instance B. Commits 30–45, 49–51 : instance B2. Les commits
41, 46, 47 et 48 sont les seuls à toucher une surface partagée (`scripts/`,
`tests/`), tels que livrés par l'instance C, dans l'ordre imposé. Le seul
fichier de contenu touché après le milestone est `1NSI-TC-QCM-DIAG.tex`
(généré, commit 49).

## Matrice d'état des chapitres

| Chapitre | Objets base → current | Cellules cap×rôle | Statut machine | Statut local |
|---|---|---|---|---|
| 1NSI-TYPES-CONSTRUITS | 134 → 129 | 35/35 | COMPLETE | PROTECTED_LOCAL_MACHINE_COMPLETE (B) |
| 1NSI-ALGO-PARCOURS-TRIS | 38 → 38 | 42/42 | COMPLETE | PROTECTED_HEALTHY (B) |
| 1NSI-ALGO-DICHO-GLOUTON-KNN | 27 → 27 | 21/21 | COMPLETE | HEALTHY, refs officielles sur les 3 méthodes (B) |
| 1NSI-WEB-IHM | 120 → 40 | 63/63 | COMPLETE | LOCAL_MACHINE_CONTENT_COMPLETE (B) |
| 1NSI-LANGAGE | 104 → 38 | 49/49 | COMPLETE | LOCAL_MACHINE_CONTENT_COMPLETE (B) |
| 1NSI-TYPES-BASE | 78 → 32 | 35/35 | COMPLETE | LOCAL_MACHINE_CONTENT_COMPLETE (B) |
| 1NSI-ARCHITECTURE-OS | 76 → 32 | 35/35 | COMPLETE | LOCAL_MACHINE_CONTENT_COMPLETE (B) |
| 1NSI-RESEAUX | 76 → 32 | 35/35 | COMPLETE | LOCAL_MACHINE_CONTENT_COMPLETE (B2) |
| 1NSI-TABLES | 64 → 31 | 28/28 | COMPLETE | LOCAL_MACHINE_CONTENT_COMPLETE (B2) |
| 1NSI-PROJET-METHODES | 64 → 31 | 28/28 | COMPLETE | LOCAL_MACHINE_CONTENT_COMPLETE (B2) |

Total : 371 cellules, 0 MISSING, 0 UNKNOWN, 0 faux crédit. Détail par gate
dans `audit/1nsi-local/1NSI_MANUAL_SWEEP.json`.

## Ensembles d'objets (B2, base → current, `.tex` des trois chapitres)

Registres exacts avec condensats : `audit/1nsi-local/{RESEAUX,TABLES,PROJET_METHODES}_LOCAL_DELTA_LEDGER.json`.

| Chapitre | Base | Current | ADDED | REMOVED | MODIFIED |
|---|---|---|---|---|---|
| RESEAUX | 76 | 32 | 12 | 56 | 4 |
| TABLES | 64 | 31 | 10 | 43 | 6 |
| PROJET-METHODES | 64 | 31 | 10 | 43 | 6 |

- **Supprimés (synthétiques)** : copies `EX-006..`, `CO-006..`, `REMED-0n`, stub `METH-01` de chaque chapitre.
- **Nouvellement rédigés** : 4 méthodes par chapitre ; remédiations RESEAUX RE-C2..C5, TABLES RE-C1/C3/C4, PM RE-C1/C2/C4, et leurs corrigés.
- **Modifiés** : évaluations A/B de RESEAUX et PM (exercice 3) ; TABLES EX-001, CO-001, CO-003, COURS-C1, COURS-C3, COURS-C4 (défauts préexistants) ; PM EX-005, CO-005 (ligne `CAPACITY-MAP`).

À l'échelle des dix chapitres (`git diff --name-status ec12c2b5..987edb6e -- 'NSI/chapitres/1NSI-*'`) :
92 A, 441 D, 87 M. Ré-observation INT-006 (périmètre sources du producteur) :
`SOURCES_ADDED=92`, `SOURCES_REMOVED=337`, `SOURCES_MODIFIED=32`, `UNEXPLAINED_DELTA=0`.

## Reçus

**Tests.** Suite NSI (`NSI/tests`) : `0 failed / 1748 passed` après INT-006
(`15 failed / 1733 passed` avant). Modules NSI racine : `57 passed / 1 failed`
(`test_1nsi_content_untouched::test_the_baseline_is_the_commit_the_repository_itself_named`,
attribué INT-007). Aucun xfail, skip ou exclusion ajouté.

**Code.** `verify_python --check` sur les dix chapitres : 366 OK, 56 REVIEW
(objets sans code), 0 FAIL.

**Rendu.** Source `987edb6e`. Les deux PDF ont été reconstruits localement
puis **remis à leur état committé** : les fichiers suivis
`NSI/build/MANUEL_1NSI/*.pdf` ne sont pas réécrits par cette branche (ils
doivent être régénérés à l'intégration, jamais cherry-pickés comme
attestation). Les mesures ci-dessous sont celles de la construction observée
sur `987edb6e` ; elles ne constituent pas une preuve D7.

| Variante | Pages | SHA-256 | Erreurs | Overfull | Underfull | Glyphes manquants |
|---|---|---|---|---|---|---|
| MANUEL_1NSI_eleve | 136 | `3aadc3d00d9b31abed117b1fe915aefb4ef6964f7d8bf0270fb74d4244443487` | 0 | 0 | 0 | 0 |
| MANUEL_1NSI_professeur | 251 | `b9bfb8ffb076bd51095285d8836c2a2fd4216294346f43515af6802c440c4f71` | 0 | 0 | 0 | 0 |

Isolation : élève 0 corrigé / 0 clé / 0 contenu enseignant sur 219 `\input` ;
professeur 149 corrigés (= 149 fichiers) + 20 corrigés d'évaluation sur 458
`\input`.

## Demandes d'infra partagée

`audit/1nsi-local/SHARED_INFRA_INTEGRATION_REQUESTS.md` : INT-006 intégré
localement ; INT-001 (48 faux `ORPHAN_CO`, 0 réel), INT-005, INT-007 ouverts
avec correctifs déjà livrés côté C ; INT-002, INT-003 hors contenu.

## Gouvernance

- `audit/1NSI_PENDING_STATE_REOBSERVATION.{json,md}`, `audit/1NSI_CONTENT_REVIEW_CAMPAIGN_STATE.json`,
  `audit/1NSI_STATUS_GOVERNANCE_PENDING.json` : régénérés par le producteur INT-006 (`5d1643ce`).
- `audit/NSI_COUPLED_ALGORITHMICS_REVIEW_DEBT.json`, `audit/NSI_CROSS_DISCIPLINE_CONTENT_LEDGER.json` :
  régénérés par leurs producteurs (`987edb6e`), six condensats.
- `HUMAN_RECEIPTS 0` avant comme après ; `review_a`/`review_b` `PENDING_UNASSIGNED` ;
  `publication_approval false`.

## Relecture humaine

`audit/1nsi-local/1NSI_HUMAN_REVIEW_PREP.json` : condensé sémantique et
items d'attention par chapitre. Besoin : 10 verdicts EXPERT_NSI + 10 verdicts
EXPERT_PROGRAMME_PEDAGOGIE. Aucun verdict n'est généré ici.
