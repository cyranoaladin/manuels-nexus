# Vue de lecture — Variables aléatoires — EXPERT_PROGRAMME_PEDAGOGIE

Chapitre `1SPE-VARIABLES-ALEATOIRES` · manuel `1SPE` (Première, Spécialité mathématiques) · packet B · role `EXPERT_PROGRAMME_PEDAGOGIE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-VARIABLES-ALEATOIRES/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`
> Etat de revue : `audit/reviews/human/1SPE-VARIABLES-ALEATOIRES/REVIEW_STATE.json`
> Producteur de cette vue : `scripts/build_human_review_reading_views.py`
>
> Toute divergence entre cette vue et le packet se tranche en faveur du packet. Cette vue ne cree, ne ferme et ne reduit aucune obligation.

## 1. Ce que vous decidez

- L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.
- Aucun humain n'a encore approuve ce chapitre : REVIEW_DELTA_BASELINE = NONE. Le perimetre de revue est le CHAPITRE COURANT ENTIER. Les listes ci-dessous dirigent l'attention, elles ne reduisent pas le perimetre.
- CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST (`sha256:6769b01062b6f2b8deab01472485cc9344797abe0b3b770af2d85e4e487e8e92`) ; l'approbation graphique releve de la porte D7, independante.
- Verdicts autorises, a rendre dans le packet JSON canonique et jamais dans cette vue : `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`.
- Cette vue ne porte aucune decision et ne nomme personne : l'assignation du role reste `PENDING_UNASSIGNED`, l'etat du packet reste `PENDING_UNASSIGNED`.

| Perimetre | Valeur |
| --- | --- |
| Objets du chapitre dans le packet | 167 |
| Empreinte de l'ensemble d'objets | `sha256:32b2dd9bff3bc3c7c82007986ef3a2009ee89d1aecb9fcad87cf1670af00490e` |
| Empreinte semantique liee a l'approbation | `sha256:6769b01062b6f2b8deab01472485cc9344797abe0b3b770af2d85e4e487e8e92` |
| Empreinte du packet | `sha256:a68a21e0301154b1b516a187be1c3dd4bb6a642ebb2e07012c8a0691fe84180f` |
| Revision du depot gelee dans le packet | `5bc44275a0afe33f10b7ce2ec7700778f8de6308` |
| Preuve de rendu portee par le packet | `ABSENT` |

## 2. Le chapitre et ses capacites du programme officiel

**Variables aléatoires** — programme applicable 2026-2027, MENE2602917A, BO n° 14 du 2026-04-02.
Source officielle : https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A

Situation d'accroche declaree : Un assureur propose un contrat couvrant la casse d'un smartphone. La prime annuelle est de 50 euros. En cas de casse, l'assureur rembourse 300 euros. Si la probabilite de casse est de 1/10, ce contrat est-il avantageux pour l'assure ? Pour l'assureur ? Un probleme de decision qui se ramene a l'etude de l'esperance d'une variable aleatoire.

Temps estime declare : parcours 1 : 14 h · parcours 2 : 11 h · parcours 3 : 9 h.

| Code | Libelle eleve | Libelle BO | Demonstration exigible |
| --- | --- | --- | --- |
| `C1` | Je sais interpreter les evenements lies a une variable aleatoire et determiner sa loi de probabilite. | Interpréter les événements liés à une variable aléatoire et déterminer sa loi de probabilité sur un univers fini. | non |
| `C2` | Je sais calculer l'esperance E(X), la variance V(X) et l'ecart type sigma(X) d'une variable aleatoire. | Calculer l'espérance, la variance et l'écart type d'une variable aléatoire. | non |
| `C3` | Je sais representer par un arbre la repetition de n <= 4 epreuves de Bernoulli independantes et identiques, puis etudier le nombre de succes. | Pour n ≤ 4, représenter par un arbre la répétition d'épreuves de Bernoulli indépendantes et identiques afin de calculer les probabilités liées au nombre de succès. | non |
| `C4` | Je sais utiliser la linearite de l'esperance pour calculer E(aX+b). | Utiliser la linéarité de l'espérance. | non |
| `C5` | Je sais resoudre des problemes contextualises (jeux, decisions, assurances) a l'aide de variables aleatoires. | Résoudre des problèmes contextualisés faisant intervenir des variables aléatoires. | non |
| `C6` | Je sais simuler une variable aleatoire et des echantillons, et lire, comprendre et ecrire une fonction Python renvoyant la moyenne d'un echantillon de taille n. | aucun libelle BO : le referentiel du depot ne declare pas cette capacite | non |
| `C7` | Je sais etudier experimentalement la fluctuation des moyennes d'echantillons autour de l'esperance, simuler N echantillons et interpreter l'ecart entre moyenne empirique et esperance, notamment au regard de 2 sigma / racine(n). | aucun libelle BO : le referentiel du depot ne declare pas cette capacite | non |

**Attendus officiels rattaches, capacite par capacite**

- `C1` — 4 attendus :
    - `1SPE-OFFICIAL-162` (MANDATORY_KNOWLEDGE, Variables aléatoires réelles) : Variable aléatoire réelle : modélisation du résultat numérique d’une expérience aléatoire ; formalisation comme fonction définie sur l’univers et à valeurs réelles.
    - `1SPE-OFFICIAL-163` (MANDATORY_KNOWLEDGE, Variables aléatoires réelles) : Loi d’une variable aléatoire.
    - `1SPE-OFFICIAL-167` (MANDATORY_CAPACITY, Variables aléatoires réelles) : Interpréter en situation et utiliser les notations {X = a}, {X ⩽ a}, P(X = a), P(X ⩽ a). Passer du registre de la langue naturelle au registre symbolique et inversement.
    - `1SPE-OFFICIAL-169` (MANDATORY_CAPACITY, Variables aléatoires réelles) : Déterminer la loi de probabilité d’une variable aléatoire.
- `C2` — 3 attendus :
    - `1SPE-OFFICIAL-164` (MANDATORY_KNOWLEDGE, Variables aléatoires réelles) : Espérance, variance, écart type d’une variable aléatoire.
    - `1SPE-OFFICIAL-166` (MANDATORY_KNOWLEDGE, Variables aléatoires réelles) : Formule de König-Huygens.
    - `1SPE-OFFICIAL-170` (MANDATORY_CAPACITY, Variables aléatoires réelles) : Calculer une espérance, une variance, un écart type.
- `C3` — 2 attendus :
    - `1SPE-OFFICIAL-154` (MANDATORY_KNOWLEDGE, Probabilités conditionnelles et indépendance) : Pour 𝑛 ⩽ 4, répétition de 𝑛 épreuves de Bernoulli indépendantes et identiques.
    - `1SPE-OFFICIAL-158` (MANDATORY_CAPACITY, Probabilités conditionnelles et indépendance) : Pour 𝑛 ⩽ 4, représenter l’arbre associé à la répétition de 𝑛 épreuves de Bernoulli indépendantes et identiques afin de calculer des probabilités.
- `C4` — 1 attendu :
    - `1SPE-OFFICIAL-165` (MANDATORY_KNOWLEDGE, Variables aléatoires réelles) : Linéarité de l’espérance.
- `C5` — 2 attendus :
    - `1SPE-OFFICIAL-168` (MANDATORY_CAPACITY, Variables aléatoires réelles) : Modéliser une situation à l’aide d’une variable aléatoire.
    - `1SPE-OFFICIAL-171` (MANDATORY_CAPACITY, Variables aléatoires réelles) : Utiliser la notion d’espérance dans une résolution de problème (mise pour un jeu équitable, etc.).
- `C6` — 3 attendus :
    - `1SPE-OFFICIAL-175` (MANDATORY_ALGORITHM, Variables aléatoires réelles) : Le travail expérimental de simulation d’échantillons prolonge celui entrepris en seconde. L’objectif est de faire percevoir le principe de l’estimation de l’espérance d’une variable aléatoire, ou de la moyenne d’une variable statistique dans une population, par une moyenne observée sur un échantillon.
    - `1SPE-OFFICIAL-176` (MANDATORY_ALGORITHM, Variables aléatoires réelles) : Simuler une variable aléatoire avec Python ou un tableur.
    - `1SPE-OFFICIAL-177` (MANDATORY_ALGORITHM, Variables aléatoires réelles) : Lire, comprendre et écrire une fonction Python renvoyant la moyenne d’un échantillon de taille n d’une variable aléatoire.
- `C7` — 2 attendus :
    - `1SPE-OFFICIAL-178` (MANDATORY_ALGORITHM, Variables aléatoires réelles) : Étudier sur des exemples la distance entre la moyenne d’un échantillon simulé de taille n d’une variable aléatoire et l’espérance de cette variable aléatoire.
    - `1SPE-OFFICIAL-179` (MANDATORY_ALGORITHM, Variables aléatoires réelles) : Simuler, avec Python ou un tableur, N échantillons de taille n d’une variable aléatoire, d’espérance μ et d’écart type σ. Si m 2𝜎 désigne la moyenne d’un échantillon, calculer la proportion des cas où l’écart entre m et μ est inférieur ou égal à . √n

**Prerequis declares par le contrat du chapitre**

| Code | Libelle | Chapitre d'origine |
| --- | --- | --- |
| `R1` | Probabilites de base : experience aleatoire, univers, evenements, probabilite d'un evenement | 2GT |
| `R2` | Probabilites conditionnelles et independance | 1SPE-PROBA-COND |
| `R4` | Suites et sommes : notation sigma, suites arithmetiques et geometriques | 1SPE-SUITES |
| `R5` | Puissances : regles de calcul, puissances entieres | 2GT |

## 3. Structure reelle et ordre d'assemblage courant

L'ordre ci-dessous n'est pas l'ordre alphabetique des repertoires : il est lu chez l'assembleur du manuel (`Mathematiques/manuel-maths/scripts/assemble_manuel.py`, `collect_chapter`). C'est la sequence que le lecteur du PDF recoit.

| Rang | Rubrique imprimee | Objets (professeur) |
| --- | --- | --- |
| 1 | Ouverture | 1 |
| 2 | Diagnostic | 1 |
| 3 | Cours | 6 |
| 4 | Méthodes | 9 |
| 5 | Exercices | 72 |
| 6 | TD | 2 |
| 7 | Auto-évaluation | 1 |
| 8 | Évaluation | 4 |
| 9 | Remédiation | 12 |
| 10 | Corrigés | 54 |

Total assemble : 162 objets en variante professeur, 106 en variante eleve (la variante eleve exclut les corriges et les corriges d'evaluation).

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

**Objets du perimetre de revue absents de la sequence assemblee**

5 objets du packet n'apparaissent dans aucune rubrique assemblee : le perimetre de revue les couvre, le PDF ne les imprime pas.

- `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/cours/experimentations/02_frequences_lettres.tex`
- `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/cours/experimentations/03_simuler_variable.tex`
- `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/cours/experimentations/04_fonction_moyenne.tex`
- `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/cours/experimentations/05_distance_moyenne_esperance.tex`
- `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/cours/experimentations/06_proportion_2sigma.tex`

## 4. Capacite par capacite : cellules, contributeurs, richesse

`audit/SEMANTIC_ALIGNMENT_LEDGER.json` decoupe le manuel en cellules capacite x role pedagogique. Ce chapitre en porte 49. Elles sont regroupees ici par capacite : une checklist cellule par cellule ne se lit pas.

**Pourquoi ces cellules arrivent chez vous.** Seul le META rattache les corps a une capacite ; l'identite declaree est resolue par egalite exacte, et la couverture de reponses n'etablit qu'une COUVERTURE. Etablir qu'un corps SERT la capacite est un jugement pedagogique, pas un calcul : c'est un resultat terminal, pas une lacune de mesure. C'est pourquoi chaque cellule de ce chapitre est routee vers vous.

Chaque capacite rappelle ensuite ce qui lui est propre : le nombre de cellules, leur disposition, les preuves eventuellement attachees et l'etat de sa richesse.

### Capacite `C1` — « Je sais interpreter les evenements lies a une variable aleatoire et determiner sa loi de probabilite. »

Libelle BO : Interpréter les événements liés à une variable aléatoire et déterminer sa loi de probabilité sur un univers fini.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 14 | `1SPE-VARALEA-CO-001..010`, `1SPE-VARALEA-CO-029..030`, `1SPE-VARALEA-CO-039`, `1SPE-VARALEA-CO-046` |
| cours | 2 | `1SPE-VARALEA-CR-000`, `1SPE-VARALEA-CR-010` |
| evaluations | 2 | `1SPE-VARALEA-EV-A`, `1SPE-VARALEA-EV-B` |
| exercices | 14 | `1SPE-VARALEA-EX-001..010`, `1SPE-VARALEA-EX-029..030`, `1SPE-VARALEA-EX-039`, `1SPE-VARALEA-EX-046` |
| methodes | 1 | `1SPE-VARALEA-ME-001` |
| QCM | 3 | `Q1..3` |
| remediation | 1 | `1SPE-VARALEA-RE-C1` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 14.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-VARALEA-EV-A`, `1SPE-VARALEA-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 8 exercices (10–12 min) — `1SPE-VARALEA-EX-001..004`, `1SPE-VARALEA-EX-006`, `1SPE-VARALEA-EX-009`, `1SPE-VARALEA-EX-029`, `1SPE-VARALEA-EX-039`
- parcours 2 : 4 exercices (15–15 min) — `1SPE-VARALEA-EX-005`, `1SPE-VARALEA-EX-007`, `1SPE-VARALEA-EX-010`, `1SPE-VARALEA-EX-030`
- parcours 3 : 2 exercices (15–20 min) — `1SPE-VARALEA-EX-008`, `1SPE-VARALEA-EX-046`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C2` — « Je sais calculer l'esperance E(X), la variance V(X) et l'ecart type sigma(X) d'une variable aleatoire. »

Libelle BO : Calculer l'espérance, la variance et l'écart type d'une variable aléatoire.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 14 | `1SPE-VARALEA-CO-011..020`, `1SPE-VARALEA-CO-029..030`, `1SPE-VARALEA-CO-039`, `1SPE-VARALEA-CO-046` |
| cours | 2 | `1SPE-VARALEA-CR-000`, `1SPE-VARALEA-CR-011` |
| evaluations | 2 | `1SPE-VARALEA-EV-A`, `1SPE-VARALEA-EV-B` |
| exercices | 14 | `1SPE-VARALEA-EX-011..020`, `1SPE-VARALEA-EX-029..030`, `1SPE-VARALEA-EX-039`, `1SPE-VARALEA-EX-046` |
| methodes | 1 | `1SPE-VARALEA-ME-002` |
| QCM | 3 | `Q4..6` |
| remediation | 1 | `1SPE-VARALEA-RE-C2` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 15.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-VARALEA-EV-A`, `1SPE-VARALEA-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 7 exercices (10–12 min) — `1SPE-VARALEA-EX-011..013`, `1SPE-VARALEA-EX-015`, `1SPE-VARALEA-EX-019`, `1SPE-VARALEA-EX-029`, `1SPE-VARALEA-EX-039`
- parcours 2 : 4 exercices (15–15 min) — `1SPE-VARALEA-EX-014`, `1SPE-VARALEA-EX-016..017`, `1SPE-VARALEA-EX-030`
- parcours 3 : 3 exercices (15–20 min) — `1SPE-VARALEA-EX-018`, `1SPE-VARALEA-EX-020`, `1SPE-VARALEA-EX-046`
- parcours non declare : 1 exercice (duree non declaree) — `1SPE-VARALEA-EX-017-CDP`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C3` — « Je sais representer par un arbre la repetition de n <= 4 epreuves de Bernoulli independantes et identiques, puis etudier le nombre de succes. »

Libelle BO : Pour n ≤ 4, représenter par un arbre la répétition d'épreuves de Bernoulli indépendantes et identiques afin de calculer les probabilités liées au nombre de succès.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 5 | `1SPE-VARALEA-CO-002`, `1SPE-VARALEA-CO-005`, `1SPE-VARALEA-CO-017`, `1SPE-VARALEA-CO-030`, `1SPE-VARALEA-CO-046` |
| cours | 2 | `1SPE-VARALEA-CR-000`, `1SPE-VARALEA-CR-012` |
| evaluations | 2 | `1SPE-VARALEA-EV-A`, `1SPE-VARALEA-EV-B` |
| exercices | 5 | `1SPE-VARALEA-EX-002`, `1SPE-VARALEA-EX-005`, `1SPE-VARALEA-EX-017`, `1SPE-VARALEA-EX-030`, `1SPE-VARALEA-EX-046` |
| methodes | 1 | `1SPE-VARALEA-ME-006` |
| QCM | 3 | `Q7..9` |
| remediation | 1 | `1SPE-VARALEA-RE-C3` |

**Richesse declaree**

- type de capacite : `ATOMIC_SUPPORT` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 6.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-VARALEA-EV-A`, `1SPE-VARALEA-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 1 exercice (10–10 min) — `1SPE-VARALEA-EX-002`
- parcours 2 : 3 exercices (15–15 min) — `1SPE-VARALEA-EX-005`, `1SPE-VARALEA-EX-017`, `1SPE-VARALEA-EX-030`
- parcours 3 : 1 exercice (20–20 min) — `1SPE-VARALEA-EX-046`
- parcours non declare : 1 exercice (duree non declaree) — `1SPE-VARALEA-EX-017-CDP`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C4` — « Je sais utiliser la linearite de l'esperance pour calculer E(aX+b). »

Libelle BO : Utiliser la linéarité de l'espérance.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 4 | `1SPE-VARALEA-CO-014`, `1SPE-VARALEA-CO-017`, `1SPE-VARALEA-CO-020`, `1SPE-VARALEA-CO-046` |
| cours | 2 | `1SPE-VARALEA-CR-000`, `1SPE-VARALEA-CR-013` |
| evaluations | 2 | `1SPE-VARALEA-EV-A`, `1SPE-VARALEA-EV-B` |
| exercices | 4 | `1SPE-VARALEA-EX-014`, `1SPE-VARALEA-EX-017`, `1SPE-VARALEA-EX-020`, `1SPE-VARALEA-EX-046` |
| methodes | 1 | `1SPE-VARALEA-ME-007` |
| QCM | 3 | `Q10..12` |
| remediation | 1 | `1SPE-VARALEA-RE-C4` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 5.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-VARALEA-EV-A`, `1SPE-VARALEA-EV-B`.

**Progression de difficulte declaree**

- parcours 2 : 2 exercices (15–15 min) — `1SPE-VARALEA-EX-014`, `1SPE-VARALEA-EX-017`
- parcours 3 : 2 exercices (20–20 min) — `1SPE-VARALEA-EX-020`, `1SPE-VARALEA-EX-046`
- parcours non declare : 1 exercice (duree non declaree) — `1SPE-VARALEA-EX-017-CDP`
- palier sans exercice cible : parcours 1.

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C5` — « Je sais resoudre des problemes contextualises (jeux, decisions, assurances) a l'aide de variables aleatoires. »

Libelle BO : Résoudre des problèmes contextualisés faisant intervenir des variables aléatoires.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 8 | `1SPE-VARALEA-CO-041..043`, `1SPE-VARALEA-CO-045..048`, `1SPE-VARALEA-CO-050` |
| cours | 2 | `1SPE-VARALEA-CR-000`, `1SPE-VARALEA-CR-014` |
| evaluations | 2 | `1SPE-VARALEA-EV-A`, `1SPE-VARALEA-EV-B` |
| exercices | 8 | `1SPE-VARALEA-EX-041..043`, `1SPE-VARALEA-EX-045..048`, `1SPE-VARALEA-EX-050` |
| methodes | 1 | `1SPE-VARALEA-ME-005` |
| QCM | 3 | `Q13..15` |
| remediation | 1 | `1SPE-VARALEA-RE-C5` |

**Richesse declaree**

- type de capacite : `COMPOSITE_REASONING` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 8.
- gestes de raisonnement declares : `calcul`, `interpretation`, `modelisation`, `synthese`.
- evaluee par : `1SPE-VARALEA-EV-A`, `1SPE-VARALEA-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 3 exercices (12–12 min) — `1SPE-VARALEA-EX-041..042`, `1SPE-VARALEA-EX-045`
- parcours 2 : 2 exercices (15–15 min) — `1SPE-VARALEA-EX-043`, `1SPE-VARALEA-EX-047`
- parcours 3 : 3 exercices (20–20 min) — `1SPE-VARALEA-EX-046`, `1SPE-VARALEA-EX-048`, `1SPE-VARALEA-EX-050`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C6` — « Je sais simuler une variable aleatoire et des echantillons, et lire, comprendre et ecrire une fonction Python renvoyant la moyenne d'un echantillon de taille n. »

Libelle BO : aucun libelle BO : le referentiel du depot ne declare pas cette capacite (`Mathematiques/manuel-maths/referentiel/capacites_1SPE_VARIABLES_ALEATOIRES.json`). Le contrat du chapitre la declare, le referentiel ne lui donne aucun attendu officiel : la rattacher au programme fait partie de votre jugement.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 2 | `1SPE-VARALEA-CO-051..052` |
| cours | 1 | `1SPE-VARALEA-CR-000` |
| evaluations | 2 | `1SPE-VARALEA-EV-A`, `1SPE-VARALEA-EV-B` |
| exercices | 2 | `1SPE-VARALEA-EX-051..052` |
| methodes | 1 | `1SPE-VARALEA-ME-008` |
| QCM | 3 | `Q16..18` |
| remediation | 1 | `1SPE-VARALEA-RE-C6` |

**Richesse declaree**

- type de capacite : `ATOMIC_SUPPORT` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 2.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-VARALEA-EV-A`, `1SPE-VARALEA-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 1 exercice (10–10 min) — `1SPE-VARALEA-EX-051`
- parcours 2 : 1 exercice (15–15 min) — `1SPE-VARALEA-EX-052`
- palier sans exercice cible : parcours 3.

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C7` — « Je sais etudier experimentalement la fluctuation des moyennes d'echantillons autour de l'esperance, simuler N echantillons et interpreter l'ecart entre moyenne empirique et esperance, notamment au regard de 2 sigma / racine(n). »

Libelle BO : aucun libelle BO : le referentiel du depot ne declare pas cette capacite (`Mathematiques/manuel-maths/referentiel/capacites_1SPE_VARIABLES_ALEATOIRES.json`). Le contrat du chapitre la declare, le referentiel ne lui donne aucun attendu officiel : la rattacher au programme fait partie de votre jugement.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 2 | `1SPE-VARALEA-CO-053..054` |
| cours | 1 | `1SPE-VARALEA-CR-000` |
| evaluations | 2 | `1SPE-VARALEA-EV-A`, `1SPE-VARALEA-EV-B` |
| exercices | 2 | `1SPE-VARALEA-EX-053..054` |
| methodes | 1 | `1SPE-VARALEA-ME-009` |
| QCM | 3 | `Q19..21` |
| remediation | 1 | `1SPE-VARALEA-RE-C7` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 2.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-VARALEA-EV-A`, `1SPE-VARALEA-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 1 exercice (12–12 min) — `1SPE-VARALEA-EX-053`
- parcours 2 : 1 exercice (15–15 min) — `1SPE-VARALEA-EX-054`
- palier sans exercice cible : parcours 3.

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

## 5. Question de QCM routee vers l'humain

1 question sur 21 n'a pas pu recevoir de preuve independante de la machine. Elle est reproduite ici en entier pour qu'elle ne se perde pas dans la masse.

### `1SPE-VARIABLES-ALEATOIRES` / `Q16` (capacite `C6`)

**Enonce**, reproduit tel quel depuis la source canonique, notations LaTeX comprises :

> Dans la fonction \code{simuler_variable(n, graine)} du chapitre, que designe $n$ ?

**Options proposees**

- **A.** Le nombre de valeurs prises par $X$
- **B.** La graine du generateur
- **C.** La taille de l'échantillon simule
- **D.** Le nombre d'échantillons simulés

**Pourquoi la machine a route vers l'humain** — aucune famille mathematique generique ne modelise cet enonce sans ecrire une derivation propre a la question

- bloquant pour la publication : oui ;
- source canonique : `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/qcm/1SPE-VARALEA-QCM.json` ;
- empreinte semantique de la question : `sha256:0fa5fcd1a4b8358652374ce5b70c07f8cb4ca21cd96dff23cc93182a9cb049b3` ;
- la cle declaree n'est pas reproduite dans cette vue : elle figure dans la source canonique, et le contrat d'independance du depot interdit de faire circuler la cle avec l'enonce. Etablissez la reponse par vous-meme, puis comparez.

## 6. Coherence du chapitre et coherence au niveau du manuel

- diversite des gestes de raisonnement au niveau du chapitre : `CANDIDATE_NON_SEMANTIC` (declaratif : `SUFFICIENT`).
- profil de diversite declare : calcul : 2 · interpretation : 5 · modelisation : 7 · synthese : 1.
- capacites routees vers l'humain : 7 sur 7.
- attendus officiels obligatoires rattaches : 17 sur 17 ; manquants : 0 ; hors annee : 0.
- chapitres dont ce chapitre depend par ses prerequis : `1SPE-PROBA-COND`, `1SPE-SUITES`, `2GT`. La coherence au niveau du manuel se juge avec eux.

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

Ces instantanes sont declares `STALE_UNDECIDED` dans `audit/PDF_ARTIFACT_REGISTRY.yaml` : ils ne sont pas garantis identiques au contenu courant. Le candidat d'impression courant se reconstruit par `python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py --manual 1SPE --variant <variant> --record-observed` (recu : `audit/1SPE_PRINT_CANDIDATE_BUILD_RECEIPT.json`, statut `PRINT_CANDIDATE`).

Rappel du recu : Ces PDF ne sont pas finals : aucun 1SPE_FINAL_CONTENT_SHA n'est figé, les deux revues humaines par chapitre et le dossier D7 restent en attente.

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-VARIABLES-ALEATOIRES/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
