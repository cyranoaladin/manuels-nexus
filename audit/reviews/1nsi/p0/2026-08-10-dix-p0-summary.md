# Synthese des dix corrections P0 scientifiques 1NSI

Date de consolidation : 2026-08-10  
Perimetre : 1NSI uniquement  
Verdict consolide : dix corrections approuvees, sans declaration de publication

## Cycles TDD et attestations

| P0 | Source | Recu | Rouge observe | Vert atteste | Reviewer / run | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| `1NSI-REV-LANG-COURS-C4-MAXIMUM-ZERO` | `2d0bd28b502aeefabff9c733eea6fec308a0b116` | `20d3eeba0f7d0518009ca2466f15ee10bcd7cb86` | Echec sur le cas `[-5, 0, -8]` et sur la condition necessaire « positive ou nulle ». | `2 passed in 0.14s` | `019fed12-0461-7e60-8a96-beee9cf917b8` / `1nsi-p0-maximum-zero-2026-08-10-turing-v1` | `approved` |
| `1NSI-REV-LANGAGE-RE-C4-CORRIGE-LISTE-VIDE` | `ab6a104bd89c2fd8360f31be66647a9ed987fe5a` | `7e63c70800b6f8b1e90ccf79f2c1958b0f220404` | Echec sur la source canonique absente et la liste vide non rejetee. | `3 passed in 0.96s` | `019fed26-ba51-77c0-8bfa-9bb3d16621e3` / `1nsi-p0-minimum-corrige-liste-vide-2026-08-10-hooke-v1` | `approved` |
| `1NSI-REV-LANGAGE-RE-C4-LISTE-VIDE` | `b30ed9dcb2fe0521694f2cf583dd8825f6ea9c16` | `f4268362d9105b2d19707185910b293e4d7eb083` | Echec sur la precondition « liste non vide » absente et sur `[]` non classe hors contrat. | `4 passed in 1.01s` | `019fed3d-6312-7430-99e8-2100b205f381` / `1nsi-p0-minimum-remediation-liste-vide-2026-08-10-cicero-v1` | `approved` |
| `1NSI-REV-PM-COURS-C2-JALONS-VIDES` | `2eb90874903578a0f3faa4145fc3999c19c577d4` | `0ed49d4c04ce762d463d4c185baa09207b604064` | Echec sur l'absence de precondition et la division par zero pour `[]`. | `5 passed in 0.96s` | `019fed4c-57ff-73c3-ab97-f4d502910316` / `1nsi-p0-avancement-jalons-vides-2026-08-10-laplace-v1` | `approved` |
| `1NSI-REV-PM-COURS-C3-POIDS-NEGATIFS` | `1853c768044ccf9f9d8672c57d43d16bc8cdd518` | `48f254d167b57a46ca8114d1ac834dd0c688c1f0` | Echec car un poids negatif et une somme nulle n'etaient pas refuses avant le calcul. | `6 passed in 1.00s` | `019fed56-b86a-7043-9474-f956273238bd` / `1nsi-p0-moyenne-poids-negatifs-2026-08-10-copernicus-v1` | `approved` |
| `1NSI-REV-TAB-COURS-C4-COLLISION-COLONNES` | `04571b9b848427f7d15163472654f5d8612c6b61` | `8ad14938cd82250f091e304271043b2da90483dc` | Echec car une colonne non-cle commune aux deux tables pouvait etre ecrasee silencieusement. | `7 passed in 1.01s` | `019fed63-47c4-73d1-ad09-d5cea07ec23e` / `1nsi-p0-fusion-collision-colonnes-2026-08-10-rawls-v1` | `approved` |
| `1NSI-REV-WEB-SERVER-VISIBILITY-COURSE` | `13023dec636d3c6a46f8b93d13a038d471db4e60` | `fe80e40cb64047abee8bb07946e152e9f04e4bdc` | Echec sur l'affirmation absolue « ne voit jamais » et l'absence de distinction avec la reponse HTTP. | `8 passed in 1.00s` | `019fed6e-cf35-7ce2-b2dd-171bb78a328a` / `1nsi-p0-code-serveur-visibilite-2026-08-10-socrates-v1` | `approved` |
| `1NSI-REV-TC-COURS-C5-COPIE-PROFONDE-INCOMPLETE` | `8ec7de50df630d4e9ee2372d69f3efe3e76725ff` | `7ad815d2c1a0a2c167d7ae1799aaa10f56e12dee` | Echec sur la garantie de copie profonde generale et l'absence de limite pour une cellule mutable. | `9 passed in 0.98s` | `019fed80-e9bd-7ef3-bfd6-a4352f2df7ef` / `1nsi-p0-cours-copie-deux-niveaux-2026-08-10-hypatia-v1` | `approved` |
| `1NSI-REV-TC-CO-053-COPIE-PROFONDE-INCOMPLETE` | `16eac039532770345a70fc770097f52c6c463a12` | `b47d1b14864030e0fcb80b840897d3551517d36b` | Echec sur la divergence de contrat entre l'exercice 053, son corrige et la source a deux niveaux. | `10 passed in 1.02s` | `019fed94-8b9b-74c1-b664-3cc3b56aac23` / `1nsi-p0-corrige-053-copie-deux-niveaux-2026-08-10-franklin-v1` | `approved` |
| `1NSI-REV-TC-CO-054-COPIE-PROFONDE-INCOMPLETE` | `398f7d48fc1b519f280fbfe2ccac51731260b2d4` | `52aa49cb41ae8b32c03fd95fbaed188fe5b416a4` | `1 failed, 10 deselected` sur l'ancien nom et la garantie de copie profonde generale. | `11 passed in 1.09s` | `e4261a54-86f8-5a6e-9f7a-f283bedf97ca` / `1nsi-p0-corrige-054-copie-deux-niveaux-2026-08-10-codex-main-v1` | `approved` |

## Controles consolides

- Les dix `p0_id`, commits source, commits de recu, `reviewer_id` et `review_run_id` sont distincts.
- Chaque recu est un enfant Git direct de son commit source et scelle les empreintes des fichiers relus.
- Le correctif 054 a aussi recu une seconde revue qualite/build independante : reviewer `0e173d8f-39a4-5972-bc99-5faaa9b19ee0`, run `1nsi-p0-co-054-quality-build-2026-08-10-codex-main-v1`, verdict `approved`.
- Les variantes `eleve`, `professeur` et `remediation` compilent en `--staging-only`; les artefacts canoniques restent inchanges.
- Les dettes scientifiques ou pedagogiques non visees, notamment les statuts C5 non exigibles et les objets encore `needs_review`, restent ouvertes et observables.
- Aucun fichier TNSI n'a ete modifie depuis le garde `bdd3285b75aeedf2c23382c58aacb0d99070a1b9`.
- Aucun appel LLM externe n'a ete effectue pour ces deux revues finales; le cache est `not_applicable`.

Cette synthese clot les dix cycles P0 cibles. Elle ne transforme pas le manuel 1NSI en livrable publiable et ne remplace pas la gouvernance des 349 qualifications.
