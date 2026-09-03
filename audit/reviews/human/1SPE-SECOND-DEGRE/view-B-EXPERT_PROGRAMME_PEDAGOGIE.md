# Vue de lecture — Fonctions polynômes du second degré — EXPERT_PROGRAMME_PEDAGOGIE

Chapitre `1SPE-SECOND-DEGRE` · manuel `1SPE` (Première, Spécialité mathématiques) · packet B · role `EXPERT_PROGRAMME_PEDAGOGIE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-SECOND-DEGRE/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`
> Etat de revue : `audit/reviews/human/1SPE-SECOND-DEGRE/REVIEW_STATE.json`
> Producteur de cette vue : `scripts/build_human_review_reading_views.py`
>
> Toute divergence entre cette vue et le packet se tranche en faveur du packet. Cette vue ne cree, ne ferme et ne reduit aucune obligation.

## 1. Ce que vous decidez

- L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.
- Aucun humain n'a encore approuve ce chapitre : REVIEW_DELTA_BASELINE = NONE. Le perimetre de revue est le CHAPITRE COURANT ENTIER. Les listes ci-dessous dirigent l'attention, elles ne reduisent pas le perimetre.
- CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST (`sha256:080a729e99ba25e3ac48b7ef480a1ff1b6b37be65945b34aed30ee74c86bb7e9`) ; l'approbation graphique releve de la porte D7, independante.
- Verdicts autorises, a rendre dans le packet JSON canonique et jamais dans cette vue : `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`.
- Cette vue ne porte aucune decision et ne nomme personne : l'assignation du role reste `PENDING_UNASSIGNED`, l'etat du packet reste `PENDING_UNASSIGNED`.

| Perimetre | Valeur |
| --- | --- |
| Objets du chapitre dans le packet | 152 |
| Empreinte de l'ensemble d'objets | `sha256:e4a5653a775bdf85a7ed42d96f50810dd2d955883f36f7823c205a775f79d8a8` |
| Empreinte semantique liee a l'approbation | `sha256:080a729e99ba25e3ac48b7ef480a1ff1b6b37be65945b34aed30ee74c86bb7e9` |
| Empreinte du packet | `sha256:c48e1e5d7497d4e246c5fb1cce899fcd7cca605e87d0ce02a34507555bbedca6` |
| Revision du depot gelee dans le packet | `5bc44275a0afe33f10b7ce2ec7700778f8de6308` |
| Preuve de rendu portee par le packet | `ABSENT` |

## 2. Le chapitre et ses capacites du programme officiel

**Fonctions polynômes du second degré** — programme applicable 2026-2027, MENE2602917A, BO n° 14 du 2026-04-02.
Source officielle : https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A

Situation d'accroche declaree : Un artisan fabrique des boites en carton en decoupant des carres aux coins d'une feuille rectangulaire. Quel cote de carre maximise le volume de la boite ? Un probleme d'optimisation qui se ramene a l'etude d'un polynome du second degre.

Temps estime declare : parcours 1 : 12 h · parcours 2 : 10 h · parcours 3 : 8 h.

| Code | Libelle eleve | Libelle BO | Demonstration exigible |
| --- | --- | --- | --- |
| `C1` | Je sais reconnaitre un polynome du second degre et passer d'une forme a une autre. | Determiner les fonctions polynomes du second degre definies sur R. Reconnaitre la forme developpee, factorisee et canonique. | non |
| `C2` | Je sais determiner le sommet, l'axe de symetrie et dresser le tableau de variations. | Determiner l'axe de symetrie et le sommet de la parabole. Dresser le tableau de variations de la fonction polynome du second degre. | non |
| `C3` | Je sais calculer le discriminant et resoudre une equation du second degre. | Calculer le discriminant d'une equation du second degre. Determiner les solutions reelles selon le signe du discriminant. | oui — Etablissement des formules donnant les solutions d'une equation du second degre. |
| `C4` | Je sais factoriser un trinome et etudier son signe. | Factoriser, si possible, un polynome du second degre. Determiner le signe d'un polynome du second degre a partir de ses racines ou du discriminant. | non |
| `C5` | Je sais resoudre une inequation du second degre. | Resoudre une inequation du second degre. Resoudre une equation ou inequation se ramenant au second degre. | non |
| `C6` | Je sais modeliser un probleme concret par un polynome du second degre et trouver un optimum. | Modeliser un probleme a l'aide d'une fonction polynome du second degre. Problemes d'optimisation. | non |

**Attendus officiels rattaches, capacite par capacite**

- `C1` — 1 attendu :
    - `1SPE-OFFICIAL-074` (MANDATORY_CAPACITY, Équations, fonctions polynômes du second degré) : Choisir une forme adaptée (développée réduite, canonique, factorisée) d’une fonction polynôme du second degré dans le cadre de la résolution d’un problème (équation, inéquation, optimisation, variations).
- `C2` : aucun attendu officiel rattache dans `audit/SEMANTIC_ALIGNMENT_LEDGER.json`.
- `C3` — 2 attendus :
    - `1SPE-OFFICIAL-070` (MANDATORY_KNOWLEDGE, Équations, fonctions polynômes du second degré) : Forme canonique d’une fonction polynôme du second degré. Discriminant. Factorisation éventuelle. Résolution d’une équation du second degré. Signe.
    - `1SPE-OFFICIAL-075` (MANDATORY_SKILL, Équations, fonctions polynômes du second degré) : Résolution de l’équation du second degré.
- `C4` — 7 attendus :
    - `1SPE-OFFICIAL-031` (MANDATORY_SKILL, Automatismes — calcul numérique et algébrique) : Déterminer les solutions d’une équation produit nul.
    - `1SPE-OFFICIAL-032` (MANDATORY_SKILL, Automatismes — calcul numérique et algébrique) : Déterminer le signe d’une expression du premier degré, d’une expression factorisée du second degré.
    - `1SPE-OFFICIAL-033` (MANDATORY_SKILL, Automatismes — calcul numérique et algébrique) : Développer, factoriser, réduire une expression algébrique simple.
    - `1SPE-OFFICIAL-069` (MANDATORY_KNOWLEDGE, Équations, fonctions polynômes du second degré) : Fonction polynôme du second degré donnée sous forme factorisée. Racines, signe, expression de la somme et du produit des racines.
    - `1SPE-OFFICIAL-071` (MANDATORY_CAPACITY, Équations, fonctions polynômes du second degré) : Étudier le signe d’une fonction polynôme du second degré donnée sous forme factorisée.
    - `1SPE-OFFICIAL-072` (MANDATORY_CAPACITY, Équations, fonctions polynômes du second degré) : Déterminer les fonctions polynômes du second degré s’annulant en deux nombres réels distincts.
    - `1SPE-OFFICIAL-073` (MANDATORY_CAPACITY, Équations, fonctions polynômes du second degré) : Factoriser une fonction polynôme du second degré, en diversifiant les stratégies : racine évidente, détection des racines par leur somme et leur produit, identité remarquable, application des formules générales.
- `C5` : aucun attendu officiel rattache dans `audit/SEMANTIC_ALIGNMENT_LEDGER.json`.
- `C6` : aucun attendu officiel rattache dans `audit/SEMANTIC_ALIGNMENT_LEDGER.json`.

**Prerequis declares par le contrat du chapitre**

| Code | Libelle | Chapitre d'origine |
| --- | --- | --- |
| `R1` | Calcul litteral : developper, factoriser, identites remarquables | 2GT |
| `R2` | Equations du premier degre et produit nul | 2GT |
| `R3` | Fonctions : image, antecedent, courbe representative | 2GT |
| `R4` | Fonctions de reference : carre, inverse | 2GT |
| `R5` | Inegalites : regles de calcul, tableau de signes | 2GT |

## 3. Structure reelle et ordre d'assemblage courant

L'ordre ci-dessous n'est pas l'ordre alphabetique des repertoires : il est lu chez l'assembleur du manuel (`Mathematiques/manuel-maths/scripts/assemble_manuel.py`, `collect_chapter`). C'est la sequence que le lecteur du PDF recoit.

| Rang | Rubrique imprimee | Objets (professeur) |
| --- | --- | --- |
| 1 | Ouverture | 1 |
| 2 | Diagnostic | 1 |
| 3 | Cours | 6 |
| 4 | Méthodes | 6 |
| 5 | Exercices | 70 |
| 6 | TD | 2 |
| 7 | Auto-évaluation | 1 |
| 8 | Évaluation | 4 |
| 9 | Remédiation | 11 |
| 10 | Corrigés | 50 |

Total assemble : 152 objets en variante professeur, 100 en variante eleve (la variante eleve exclut les corriges et les corriges d'evaluation).

La page d'ouverture du chapitre est composee par l'assembleur a partir de `contrat.yaml` (titre, capacites, situation d'accroche, temps estime) : elle n'apparait donc pas comme un objet de la sequence.

**Placement des temps pedagogiques dans la progression**

- rang 2 — le diagnostic ouvre le chapitre.
- rang 3 — le cours precede les methodes.
- rang 4 — les methodes sont regroupees avant les exercices.
- rang 5 — les exercices suivent les methodes en un seul bloc.
- rang 6 — le TD est place apres les exercices.
- rang 7 — le QCM d'auto-evaluation suit le TD.
- rang 8 — les evaluations viennent apres le QCM.
- rang 9 — la remediation est placee apres les evaluations.
- rang 10 — les corriges ferment la variante professeur.

Cet ordre est un fait d'assemblage, pas un jugement : sa pertinence pedagogique fait partie de ce que vous evaluez.

## 4. Capacite par capacite : cellules, contributeurs, richesse

`audit/SEMANTIC_ALIGNMENT_LEDGER.json` decoupe le manuel en cellules capacite x role pedagogique. Ce chapitre en porte 42. Elles sont regroupees ici par capacite : une checklist cellule par cellule ne se lit pas.

**Pourquoi ces cellules arrivent chez vous.** Seul le META rattache les corps a une capacite ; l'identite declaree est resolue par egalite exacte, et la couverture de reponses n'etablit qu'une COUVERTURE. Etablir qu'un corps SERT la capacite est un jugement pedagogique, pas un calcul : c'est un resultat terminal, pas une lacune de mesure. C'est pourquoi chaque cellule de ce chapitre est routee vers vous.

Chaque capacite rappelle ensuite ce qui lui est propre : le nombre de cellules, leur disposition, les preuves eventuellement attachees et l'etat de sa richesse.

### Capacite `C1` — « Je sais reconnaitre un polynome du second degre et passer d'une forme a une autre. »

Libelle BO : Determiner les fonctions polynomes du second degre definies sur R. Reconnaitre la forme developpee, factorisee et canonique.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 13 | `1SPE-SECDEG-CO-001..003`, `1SPE-SECDEG-CO-019..022`, `1SPE-SECDEG-CO-031..032`, `1SPE-SECDEG-CO-035`, `1SPE-SECDEG-CO-038`, `1SPE-SECDEG-CO-040`, `1SPE-SECDEG-CO-043` |
| cours | 2 | `1SPE-SECDEG-CR-000`, `1SPE-SECDEG-CR-010` |
| evaluations | 2 | `1SPE-SECDEG-EV-A`, `1SPE-SECDEG-EV-B` |
| exercices | 13 | `1SPE-SECDEG-EX-001..003`, `1SPE-SECDEG-EX-019..022`, `1SPE-SECDEG-EX-031..032`, `1SPE-SECDEG-EX-035`, `1SPE-SECDEG-EX-038`, `1SPE-SECDEG-EX-040`, `1SPE-SECDEG-EX-043` |
| methodes | 1 | `1SPE-SECDEG-ME-001` |
| QCM | 3 | `Q1..3` |
| remediation | 1 | `1SPE-SECDEG-RE-C1` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 13.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-SECDEG-EV-A`, `1SPE-SECDEG-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (10–10 min) — `1SPE-SECDEG-EX-001..003`, `1SPE-SECDEG-EX-043`
- parcours 2 : 6 exercices (20–20 min) — `1SPE-SECDEG-EX-019..022`, `1SPE-SECDEG-EX-031..032`
- parcours 3 : 3 exercices (35–40 min) — `1SPE-SECDEG-EX-035`, `1SPE-SECDEG-EX-038`, `1SPE-SECDEG-EX-040`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C2` — « Je sais determiner le sommet, l'axe de symetrie et dresser le tableau de variations. »

Libelle BO : Determiner l'axe de symetrie et le sommet de la parabole. Dresser le tableau de variations de la fonction polynome du second degre.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 13 | `1SPE-SECDEG-CO-004..006`, `1SPE-SECDEG-CO-019..020`, `1SPE-SECDEG-CO-027..028`, `1SPE-SECDEG-CO-035`, `1SPE-SECDEG-CO-037`, `1SPE-SECDEG-CO-040`, `1SPE-SECDEG-CO-042`, `1SPE-SECDEG-CO-045`, `1SPE-SECDEG-CO-049` |
| cours | 2 | `1SPE-SECDEG-CR-000`, `1SPE-SECDEG-CR-011` |
| evaluations | 2 | `1SPE-SECDEG-EV-A`, `1SPE-SECDEG-EV-B` |
| exercices | 13 | `1SPE-SECDEG-EX-004..006`, `1SPE-SECDEG-EX-019..020`, `1SPE-SECDEG-EX-027..028`, `1SPE-SECDEG-EX-035`, `1SPE-SECDEG-EX-037`, `1SPE-SECDEG-EX-040`, `1SPE-SECDEG-EX-042`, `1SPE-SECDEG-EX-045`, `1SPE-SECDEG-EX-049` |
| methodes | 1 | `1SPE-SECDEG-ME-002` |
| QCM | 3 | `Q4..6` |
| remediation | 1 | `1SPE-SECDEG-RE-C2` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 13.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-SECDEG-EV-A`, `1SPE-SECDEG-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 3 exercices (10–12 min) — `1SPE-SECDEG-EX-004..006`
- parcours 2 : 5 exercices (15–20 min) — `1SPE-SECDEG-EX-019..020`, `1SPE-SECDEG-EX-027..028`, `1SPE-SECDEG-EX-045`
- parcours 3 : 5 exercices (15–40 min) — `1SPE-SECDEG-EX-035`, `1SPE-SECDEG-EX-037`, `1SPE-SECDEG-EX-040`, `1SPE-SECDEG-EX-042`, `1SPE-SECDEG-EX-049`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C3` — « Je sais calculer le discriminant et resoudre une equation du second degre. »

Libelle BO : Calculer le discriminant d'une equation du second degre. Determiner les solutions reelles selon le signe du discriminant.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 16 | `1SPE-SECDEG-CO-007..009`, `1SPE-SECDEG-CO-021..024`, `1SPE-SECDEG-CO-029..030`, `1SPE-SECDEG-CO-035..036`, `1SPE-SECDEG-CO-038..039`, `1SPE-SECDEG-CO-041..042`, `1SPE-SECDEG-CO-046` |
| cours | 2 | `1SPE-SECDEG-CR-000`, `1SPE-SECDEG-CR-012` |
| evaluations | 2 | `1SPE-SECDEG-EV-A`, `1SPE-SECDEG-EV-B` |
| exercices | 16 | `1SPE-SECDEG-EX-007..009`, `1SPE-SECDEG-EX-021..024`, `1SPE-SECDEG-EX-029..030`, `1SPE-SECDEG-EX-035..036`, `1SPE-SECDEG-EX-038..039`, `1SPE-SECDEG-EX-041..042`, `1SPE-SECDEG-EX-046` |
| methodes | 1 | `1SPE-SECDEG-ME-003` |
| QCM | 3 | `Q7..9` |
| remediation | 1 | `1SPE-SECDEG-RE-C3` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 16.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-SECDEG-EV-A`, `1SPE-SECDEG-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 3 exercices (10–12 min) — `1SPE-SECDEG-EX-007..009`
- parcours 2 : 7 exercices (15–20 min) — `1SPE-SECDEG-EX-021..024`, `1SPE-SECDEG-EX-029..030`, `1SPE-SECDEG-EX-046`
- parcours 3 : 6 exercices (35–40 min) — `1SPE-SECDEG-EX-035..036`, `1SPE-SECDEG-EX-038..039`, `1SPE-SECDEG-EX-041..042`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C4` — « Je sais factoriser un trinome et etudier son signe. »

Libelle BO : Factoriser, si possible, un polynome du second degre. Determiner le signe d'un polynome du second degre a partir de ses racines ou du discriminant.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 13 | `1SPE-SECDEG-CO-010..012`, `1SPE-SECDEG-CO-023..026`, `1SPE-SECDEG-CO-031..032`, `1SPE-SECDEG-CO-036`, `1SPE-SECDEG-CO-038`, `1SPE-SECDEG-CO-041`, `1SPE-SECDEG-CO-044` |
| cours | 2 | `1SPE-SECDEG-CR-000`, `1SPE-SECDEG-CR-013` |
| evaluations | 2 | `1SPE-SECDEG-EV-A`, `1SPE-SECDEG-EV-B` |
| exercices | 13 | `1SPE-SECDEG-EX-010..012`, `1SPE-SECDEG-EX-023..026`, `1SPE-SECDEG-EX-031..032`, `1SPE-SECDEG-EX-036`, `1SPE-SECDEG-EX-038`, `1SPE-SECDEG-EX-041`, `1SPE-SECDEG-EX-044` |
| methodes | 1 | `1SPE-SECDEG-ME-004` |
| QCM | 3 | `Q10..12` |
| remediation | 1 | `1SPE-SECDEG-RE-C4` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 13.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-SECDEG-EV-A`, `1SPE-SECDEG-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (10–12 min) — `1SPE-SECDEG-EX-010..012`, `1SPE-SECDEG-EX-044`
- parcours 2 : 6 exercices (20–20 min) — `1SPE-SECDEG-EX-023..026`, `1SPE-SECDEG-EX-031..032`
- parcours 3 : 3 exercices (35–40 min) — `1SPE-SECDEG-EX-036`, `1SPE-SECDEG-EX-038`, `1SPE-SECDEG-EX-041`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C5` — « Je sais resoudre une inequation du second degre. »

Libelle BO : Resoudre une inequation du second degre. Resoudre une equation ou inequation se ramenant au second degre.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 15 | `1SPE-SECDEG-CO-013..015`, `1SPE-SECDEG-CO-025..026`, `1SPE-SECDEG-CO-029..030`, `1SPE-SECDEG-CO-033..034`, `1SPE-SECDEG-CO-036..037`, `1SPE-SECDEG-CO-039`, `1SPE-SECDEG-CO-041`, `1SPE-SECDEG-CO-047`, `1SPE-SECDEG-CO-050` |
| cours | 2 | `1SPE-SECDEG-CR-000`, `1SPE-SECDEG-CR-014` |
| evaluations | 2 | `1SPE-SECDEG-EV-A`, `1SPE-SECDEG-EV-B` |
| exercices | 15 | `1SPE-SECDEG-EX-013..015`, `1SPE-SECDEG-EX-025..026`, `1SPE-SECDEG-EX-029..030`, `1SPE-SECDEG-EX-033..034`, `1SPE-SECDEG-EX-036..037`, `1SPE-SECDEG-EX-039`, `1SPE-SECDEG-EX-041`, `1SPE-SECDEG-EX-047`, `1SPE-SECDEG-EX-050` |
| methodes | 1 | `1SPE-SECDEG-ME-005` |
| QCM | 3 | `Q13..15` |
| remediation | 1 | `1SPE-SECDEG-RE-C5` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 15.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-SECDEG-EV-A`, `1SPE-SECDEG-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 3 exercices (10–12 min) — `1SPE-SECDEG-EX-013..015`
- parcours 2 : 7 exercices (15–25 min) — `1SPE-SECDEG-EX-025..026`, `1SPE-SECDEG-EX-029..030`, `1SPE-SECDEG-EX-033..034`, `1SPE-SECDEG-EX-047`
- parcours 3 : 5 exercices (15–40 min) — `1SPE-SECDEG-EX-036..037`, `1SPE-SECDEG-EX-039`, `1SPE-SECDEG-EX-041`, `1SPE-SECDEG-EX-050`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C6` — « Je sais modeliser un probleme concret par un polynome du second degre et trouver un optimum. »

Libelle BO : Modeliser un probleme a l'aide d'une fonction polynome du second degre. Problemes d'optimisation.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 12 | `1SPE-SECDEG-CO-016..018`, `1SPE-SECDEG-CO-027..028`, `1SPE-SECDEG-CO-033..034`, `1SPE-SECDEG-CO-037`, `1SPE-SECDEG-CO-039..040`, `1SPE-SECDEG-CO-042`, `1SPE-SECDEG-CO-048` |
| cours | 2 | `1SPE-SECDEG-CR-000`, `1SPE-SECDEG-CR-015` |
| evaluations | 2 | `1SPE-SECDEG-EV-A`, `1SPE-SECDEG-EV-B` |
| exercices | 12 | `1SPE-SECDEG-EX-016..018`, `1SPE-SECDEG-EX-027..028`, `1SPE-SECDEG-EX-033..034`, `1SPE-SECDEG-EX-037`, `1SPE-SECDEG-EX-039..040`, `1SPE-SECDEG-EX-042`, `1SPE-SECDEG-EX-048` |
| methodes | 1 | `1SPE-SECDEG-ME-006` |
| QCM | 3 | `Q16..18` |
| remediation | 1 | `1SPE-SECDEG-RE-C6` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 12.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-SECDEG-EV-A`, `1SPE-SECDEG-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 3 exercices (12–15 min) — `1SPE-SECDEG-EX-016..018`
- parcours 2 : 5 exercices (15–25 min) — `1SPE-SECDEG-EX-027..028`, `1SPE-SECDEG-EX-033..034`, `1SPE-SECDEG-EX-048`
- parcours 3 : 4 exercices (35–40 min) — `1SPE-SECDEG-EX-037`, `1SPE-SECDEG-EX-039..040`, `1SPE-SECDEG-EX-042`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

## 5. Question de QCM routee vers l'humain

Aucune question de ce chapitre n'est routee vers une revue humaine par `audit/QCM_INDEPENDENT_EVIDENCE_V2.json`.

## 6. Coherence du chapitre et coherence au niveau du manuel

- diversite des gestes de raisonnement au niveau du chapitre : `INSUFFICIENT` (declaratif : `INSUFFICIENT`).
- aucun profil de diversite declare pour ce chapitre : les gestes de raisonnement ne sont pas mesures, ils restent a juger.
- capacites routees vers l'humain : 6 sur 6.
- attendus officiels obligatoires rattaches : 10 sur 10 ; manquants : 0 ; hors annee : 0.
- chapitres dont ce chapitre depend par ses prerequis : `2GT`. La coherence au niveau du manuel se juge avec eux.

La regle du depot : « la richesse se mesure en occasions distinctes et en gestes de raisonnement declares ; jamais en nombre de fichiers ».

## 7. Checklist du role `EXPERT_PROGRAMME_PEDAGOGIE`

1. completude du programme officiel
2. alignement des capacites
3. progression
4. prerequis
5. methodes
6. diversite des exercices
7. difficulte
8. richesse
9. remediation
10. conception des evaluations
11. pertinence pedagogique des QCM
12. coherence du chapitre
13. coherence au niveau du manuel

Cette checklist est celle du role. Elle s'applique au CHAPITRE COURANT ENTIER, y compris aux objets qu'aucune section de cette vue ne cite.

## 8. Reference de lecture : le PDF candidat

Le PDF sert a lire le chapitre dans l'ordre ou l'eleve le recevra. Il n'est pas une preuve : le packet ne porte aucune preuve de rendu (`render_evidence = ABSENT`), et aucun index page-objet n'est etabli.

| Fichier | Variante | Pages | Role declare | Etat declare |
| --- | --- | --- | --- | --- |
| `MANUELS_PDF_PUBLICATION/01_Maths_1re_Spe_Eleve.pdf` | eleve | 371 | HISTORICAL_PUBLICATION_SNAPSHOT | STALE_UNDECIDED |
| `MANUELS_PDF_PUBLICATION/02_Maths_1re_Spe_Professeur.pdf` | professeur | 617 | HISTORICAL_PUBLICATION_SNAPSHOT | STALE_UNDECIDED |

Ces instantanes sont declares `STALE_UNDECIDED` dans `audit/PDF_ARTIFACT_REGISTRY.yaml` : ils ne sont pas garantis identiques au contenu courant. Le candidat d'impression courant se reconstruit par `python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py --manual 1SPE --variant <variant>` (recu : `audit/1SPE_PRINT_CANDIDATE_BUILD_RECEIPT.json`, statut `PRINT_CANDIDATE`).

Rappel du recu : Ces PDF ne sont PAS finals : aucun 1SPE_FINAL_CONTENT_SHA n'est fige, les deux revues humaines et D7 restent PENDING.

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-SECOND-DEGRE/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
