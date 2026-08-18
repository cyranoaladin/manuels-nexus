# STALE COMMITTED REPORTS LEDGER

Registre des rapports CURRENT committés qui étaient stales, et contrat
d'architecture pour empêcher la récidive. Créé le 2026-08-18 dans le cadre de
la clôture hermétique A1/A2 (voir `audit/PROVENANCE_CORRECTION_1361cf37.md`).

## Principe obligatoire

- **CURRENT REPORT** = vérité régénérée depuis le HEAD courant. Un rapport
  courant committé ne doit jamais rester stale : il est régénéré et
  recommitté à chaque scellement qui change les sources dont il dérive.
- **HISTORICAL SNAPSHOT** = preuve historique immuable, attachée à un SHA
  explicite (ex. `PROVENANCE_CORRECTION_1361cf37.md`,
  `A0_A1_STATE_TRANSITIONS.*`). Ne se régénère jamais.
- Les deux ne se mélangent pas : aucun test ne doit épingler le contenu d'un
  rapport CURRENT comme s'il était un snapshot historique, et aucun snapshot
  historique ne doit être « rafraîchi ».

## Les 6 rapports CURRENT qui étaient stales

Tous ont le même producteur : `scripts/inventory_collection.py` (render
pipeline, mode par défaut). Tous sont de type CURRENT. Leur dernier refresh
committé datait du 2026-08-16 (`7297c4cd`, contenu généré à
`2026-08-16T07:53:29Z`, provenance `head_sha e701b30a`), antérieur à la
correction des wrappers (`fed6d28a`) et à tout le lot A1-final/A2 : ils
affichaient encore `RAW 6541, latex_cycles 10, broken_latex 5` alors que
toute génération fraîche donne `RAW 5615, 0, 0`. C'est ce contenu stale qui a
produit la fausse mesure « 10 cycles » du rapport contesté.

| path | producer | type | source_sha_recorded (stale) | stale_since | refreshed |
| --- | --- | --- | --- | --- | --- |
| `audit/INVENTAIRE_COLLECTION.json` | inventory_collection.py | CURRENT | `e701b30a` (généré 2026-08-16) | premier commit source après `7297c4cd` | OUI — recommitté avec `provenance.head_sha` = SHA observé à la génération |
| `audit/INVENTAIRE_COLLECTION.md` | inventory_collection.py | CURRENT | idem (rendu du JSON) | idem | OUI |
| `audit/AUDIT_CONSOLIDE.md` | inventory_collection.py | CURRENT | idem | idem | OUI |
| `audit/ECARTS_ET_CONTRADICTIONS.yaml` | inventory_collection.py | CURRENT | idem | idem | OUI |
| `audit/MATRICE_LIVRABLES.yaml` | inventory_collection.py | CURRENT | idem | idem | OUI |
| `ETAT_COLLECTION.md` | inventory_collection.py | CURRENT | dernier refresh `1d0c3fda` (2026-08-12) | idem | OUI |

`actual_head` au moment du refresh : `3018b3097f82dfe4aa59b47e276b9a2320a7f3ab`
(le rapport régénéré enregistre ce SHA dans `provenance.head_sha`, contrat
« SHA réellement observé à la génération » — jamais le SHA du commit qui
contiendra le rapport).

## tests_pinning_old_content — diagnostic corrigé

**Aucun test n'épinglait réellement le contenu stale de ces 6 rapports.**
Le rapport de session précédent affirmait que 3 tests bloquaient leur
régénération ; ce diagnostic était un artefact de mesure : les 3 échecs
observés provenaient de l'**arbre de travail sale** pendant le run (le render
venait de modifier les 6 fichiers, et `_load_observed_build_manifest` refuse
un dépôt sale), pas d'un épinglage de contenu. Ces tests calculent
l'inventaire en direct et passent sur arbre propre quel que soit l'état des
rapports committés.

Deux tests couplaient néanmoins l'état LIVE du dépôt à des oracles figés, et
ont été restructurés par principe (« la résolution d'un défaut réel ne doit
jamais casser le test qui servait à le détecter ») :

| test | why_pinned (avant) | target_architecture (après) |
| --- | --- | --- |
| `test_real_reports_expose_known_exercise_contradictions` | épinglait les défauts réels vivants (471 vs 477, TRIGONOMETRIE 50 vs 24, DIRECTIVES l.50) comme oracle éternel | scindé : invariant de cohérence interne sur le dépôt réel (`test_real_report_reconciliation_is_internally_consistent`) + fixture synthétique historique gelée (`test_fixture_exposes_historical_1spe_exercise_contradictions`) |
| `test_repository_baseline_is_frozen_schema_valid_and_gate_green` | mélangeait intégrité du snapshot historique et gate courant | scindé : `HISTORICAL_BASELINE_INTEGRITY` (baseline figée, schéma + drapeaux) et `CURRENT_NO_REGRESSION` (`test_repository_fail_on_new_gate_is_green`) |

## Reproductibilité du rapport courant

Deux générations indépendantes depuis des clones frais du même SHA produisent
des artefacts **byte-identiques** (prouvé aux SHAs `9ddcffee` et `0b0c3685`,
sha256 identiques entre clones A et B). Le seul champ temporel,
`provenance.generated_at_utc`, dérive de la date du commit observé (pas de
l'horloge murale) et est donc déterministe.
