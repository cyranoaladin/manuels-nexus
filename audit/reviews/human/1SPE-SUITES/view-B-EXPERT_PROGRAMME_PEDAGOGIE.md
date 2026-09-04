# Vue de lecture — Suites numériques — EXPERT_PROGRAMME_PEDAGOGIE

Chapitre `1SPE-SUITES` · manuel `1SPE` (Première, Spécialité mathématiques) · packet B · role `EXPERT_PROGRAMME_PEDAGOGIE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-SUITES/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`
> Etat de revue : `audit/reviews/human/1SPE-SUITES/REVIEW_STATE.json`
> Producteur de cette vue : `scripts/build_human_review_reading_views.py`
>
> Toute divergence entre cette vue et le packet se tranche en faveur du packet. Cette vue ne cree, ne ferme et ne reduit aucune obligation.

## 1. Ce que vous decidez

- L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.
- Aucun humain n'a encore approuve ce chapitre : REVIEW_DELTA_BASELINE = NONE. Le perimetre de revue est le CHAPITRE COURANT ENTIER. Les listes ci-dessous dirigent l'attention, elles ne reduisent pas le perimetre.
- CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST (`sha256:5ef8abbb56f0cdb286ae93b021d435dc81775fa1c0d2287a80f1e302cda93785`) ; l'approbation graphique releve de la porte D7, independante.
- Verdicts autorises, a rendre dans le packet JSON canonique et jamais dans cette vue : `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`.
- Cette vue ne porte aucune decision et ne nomme personne : l'assignation du role reste `PENDING_UNASSIGNED`, l'etat du packet reste `PENDING_UNASSIGNED`.

| Perimetre | Valeur |
| --- | --- |
| Objets du chapitre dans le packet | 161 |
| Empreinte de l'ensemble d'objets | `sha256:fac8d9dc89cd3699c20ae65783a82b7cfb068007a357721549edfa055858b135` |
| Empreinte semantique liee a l'approbation | `sha256:5ef8abbb56f0cdb286ae93b021d435dc81775fa1c0d2287a80f1e302cda93785` |
| Empreinte du packet | `sha256:a06075630ddd55f28cefd799671298d32b996465282455d2fcee5defe2adc854` |
| Revision du depot gelee dans le packet | `5bc44275a0afe33f10b7ce2ec7700778f8de6308` |
| Preuve de rendu portee par le packet | `ABSENT` |

## 2. Le chapitre et ses capacites du programme officiel

**Suites numériques** — programme applicable 2026-2027, MENE2602917A, BO n° 14 du 2026-04-02.
Source officielle : https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A

Situation d'accroche declaree : Deux offres d'épargne : versement fixe mensuel (modèle linéaire) contre intérêts composés (modèle exponentiel). À partir de quand la seconde dépasse-t-elle la première ? Résolue au TD fil rouge avec les outils du chapitre (C2, C3, C6, C7).

Temps estime declare : parcours 1 : 14 h · parcours 2 : 11 h · parcours 3 : 10 h.

| Code | Libelle eleve | Libelle BO | Demonstration exigible |
| --- | --- | --- | --- |
| `C1` | Je sais calculer les termes d'une suite (explicite/récurrence), à la main et en Python. | Dans le cadre de l'étude d'une suite, utiliser le registre de la langue naturelle, le registre algébrique, le registre fonctionnel. Générer une suite définie de façon explicite ou par récurrence. | non |
| `C2` | Je sais montrer qu'une suite est arithmétique et exprimer son terme général. | Reconnaître si une suite est arithmétique. Exploiter la relation entre termes, la formule explicite. | non |
| `C3` | Je sais montrer qu'une suite est géométrique et exprimer son terme général. | Reconnaître si une suite est géométrique. Exploiter la relation entre termes, la formule explicite. | non |
| `C4` | Je sais calculer la somme des premiers entiers et d'une suite géométrique. | Calculer la somme des n premiers entiers, la somme des premiers termes d'une suite géométrique. | oui — Calcul de 1+2+...+n et de 1+q+...+q^n. |
| `C5` | Je sais étudier le sens de variation d'une suite par la méthode adaptée. | Étudier le sens de variation d'une suite : étude du signe de u(n+1)−u(n), ou du quotient si les termes sont strictement positifs, ou utilisation de la fonction associée. | non |
| `C6` | Je sais modéliser une situation concrète par une suite. | Modéliser un phénomène discret par une suite (évolutions successives, suites arithmétiques et géométriques comme modèles linéaire et exponentiel discrets). | non |
| `C7` | Je sais écrire et lire un programme Python (terme, somme, seuil). | Écrire et interpréter un programme calculant un terme, une somme de termes, un seuil. | non |
| `C8` | Je sais reconnaître intuitivement une limite finie, une limite infinie ou une absence de limite, sans formalisation. | Sensibilisation intuitive à la notion de limite d'une suite : limite finie, limite infinie et absence de limite ; toute formalisation est exclue. | non |

**Attendus officiels rattaches, capacite par capacite**

- `C1` — 4 attendus :
    - `1SPE-OFFICIAL-048` (MANDATORY_KNOWLEDGE, Suites numériques, modèles discrets) : Exemples de modes de génération d’une suite : explicite 𝑢𝑛 = ƒ (𝑛), par une relation de récurrence 𝑢𝑛 + 1 = ƒ (𝑢𝑛), par un algorithme, par des motifs géométriques.
    - `1SPE-OFFICIAL-049` (MANDATORY_KNOWLEDGE, Suites numériques, modèles discrets) : Notations : 𝑢(𝑛), 𝑢𝑛, (𝑢(𝑛)), (𝑢𝑛).
    - `1SPE-OFFICIAL-054` (MANDATORY_CAPACITY, Suites numériques, modèles discrets) : Dans le cadre de l’étude d’une suite, utiliser le registre de la langue naturelle, le registre algébrique, le registre graphique, et passer de l’un à l’autre.
    - `1SPE-OFFICIAL-056` (MANDATORY_CAPACITY, Suites numériques, modèles discrets) : Calculer des termes d’une suite définie explicitement, par récurrence ou par un algorithme.
- `C2` — 3 attendus :
    - `1SPE-OFFICIAL-050` (MANDATORY_KNOWLEDGE, Suites numériques, modèles discrets) : Suites arithmétiques : exemples, définition, calcul du terme général. Lien avec l’étude d’évolutions successives à accroissements constants. Lien avec les fonctions affines. Calcul de 1 + 2 + … + 𝑛.
    - `1SPE-OFFICIAL-057` (MANDATORY_CAPACITY, Suites numériques, modèles discrets) : Pour une suite arithmétique ou géométrique, calculer le terme général, la somme de termes consécutifs, déterminer le sens de variation.
    - `1SPE-OFFICIAL-060` (MANDATORY_SKILL, Suites numériques, modèles discrets) : Calcul du terme général d’une suite arithmétique, d’une suite géométrique.
- `C3` — 1 attendu :
    - `1SPE-OFFICIAL-051` (MANDATORY_KNOWLEDGE, Suites numériques, modèles discrets) : Suites géométriques : exemples, définition, calcul du terme général. Lien avec l’étude d’évolutions successives à taux constant. Lien avec la fonction exponentielle. Calcul de 1 + 𝑞 + … + 𝑞𝑛.
- `C4` — 2 attendus :
    - `1SPE-OFFICIAL-061` (MANDATORY_SKILL, Suites numériques, modèles discrets) : Calcul de 1 + 2 + … + 𝑛.
    - `1SPE-OFFICIAL-062` (MANDATORY_SKILL, Suites numériques, modèles discrets) : Calcul de 1 + 𝑞 + … + 𝑞𝑛.
- `C5` — 1 attendu :
    - `1SPE-OFFICIAL-052` (MANDATORY_KNOWLEDGE, Suites numériques, modèles discrets) : Sens de variation d’une suite.
- `C6` — 2 attendus :
    - `1SPE-OFFICIAL-055` (MANDATORY_CAPACITY, Suites numériques, modèles discrets) : Proposer, modéliser une situation permettant de générer une suite de nombres. Déterminer une relation explicite ou une relation de récurrence pour une suite définie par un motif géométrique, par une question de dénombrement.
    - `1SPE-OFFICIAL-058` (MANDATORY_CAPACITY, Suites numériques, modèles discrets) : Modéliser un phénomène discret à croissance linéaire par une suite arithmétique, un phénomène discret à croissance exponentielle par une suite géométrique.
- `C7` : aucun attendu officiel rattache dans `audit/SEMANTIC_ALIGNMENT_LEDGER.json`.
- `C8` — 2 attendus :
    - `1SPE-OFFICIAL-053` (MANDATORY_KNOWLEDGE, Suites numériques, modèles discrets) : Sur des exemples, introduction intuitive de la notion de limite, finie ou infinie, ou l’absence de limite d’une suite.
    - `1SPE-OFFICIAL-059` (MANDATORY_CAPACITY, Suites numériques, modèles discrets) : Conjecturer, dans des cas simples, la limite éventuelle d’une suite.

**Prerequis declares par le contrat du chapitre**

| Code | Libelle | Chapitre d'origine |
| --- | --- | --- |
| `R1` | Calcul littéral : développer, factoriser, réduire | 2GT |
| `R2` | Pourcentages : coefficient multiplicateur, évolutions successives | 2GT |
| `R3` | Fonctions : image, antécédent, sens de variation | 2GT |
| `R4` | Inégalités et signe d'une expression | 2GT |
| `R5` | Python : variables, boucle for, boucle while (SNT) | SNT |

## 3. Structure reelle et ordre d'assemblage courant

L'ordre ci-dessous n'est pas l'ordre alphabetique des repertoires : il est lu chez l'assembleur du manuel (`Mathematiques/manuel-maths/scripts/assemble_manuel.py`, `collect_chapter`). C'est la sequence que le lecteur du PDF recoit.

| Rang | Rubrique imprimee | Objets (professeur) |
| --- | --- | --- |
| 1 | Ouverture | 1 |
| 2 | Diagnostic | 1 |
| 3 | Cours | 8 |
| 4 | Méthodes | 8 |
| 5 | Exercices | 72 |
| 6 | TD | 2 |
| 7 | Auto-évaluation | 1 |
| 8 | Évaluation | 4 |
| 9 | Remédiation | 13 |
| 10 | Corrigés | 51 |

Total assemble : 161 objets en variante professeur, 108 en variante eleve (la variante eleve exclut les corriges et les corriges d'evaluation).

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

`audit/SEMANTIC_ALIGNMENT_LEDGER.json` decoupe le manuel en cellules capacite x role pedagogique. Ce chapitre en porte 56. Elles sont regroupees ici par capacite : une checklist cellule par cellule ne se lit pas.

**Pourquoi ces cellules arrivent chez vous.** Seul le META rattache les corps a une capacite ; l'identite declaree est resolue par egalite exacte, et la couverture de reponses n'etablit qu'une COUVERTURE. Etablir qu'un corps SERT la capacite est un jugement pedagogique, pas un calcul : c'est un resultat terminal, pas une lacune de mesure. C'est pourquoi chaque cellule de ce chapitre est routee vers vous.

Chaque capacite rappelle ensuite ce qui lui est propre : le nombre de cellules, leur disposition, les preuves eventuellement attachees et l'etat de sa richesse.

### Capacite `C1` — « Je sais calculer les termes d'une suite (explicite/récurrence), à la main et en Python. »

Libelle BO : Dans le cadre de l'étude d'une suite, utiliser le registre de la langue naturelle, le registre algébrique, le registre fonctionnel. Générer une suite définie de façon explicite ou par récurrence.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 11 | `1SPE-SUITES-CO-002..005`, `1SPE-SUITES-CO-022..023`, `1SPE-SUITES-CO-036..037`, `1SPE-SUITES-CO-040`, `1SPE-SUITES-CO-045`, `1SPE-SUITES-CO-048` |
| cours | 2 | `1SPE-SUITES-COURS-00`, `1SPE-SUITES-CR-010` |
| evaluations | 2 | `1SPE-SUITES-EV-A`, `1SPE-SUITES-EV-B` |
| exercices | 11 | `1SPE-SUITES-EX-002..005`, `1SPE-SUITES-EX-022..023`, `1SPE-SUITES-EX-036..037`, `1SPE-SUITES-EX-040`, `1SPE-SUITES-EX-045`, `1SPE-SUITES-EX-048` |
| methodes | 1 | `1SPE-SUITES-ME-001` |
| QCM | 2 | `Q1..2` |
| remediation | 1 | `1SPE-SUITES-RE-C1` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 2 · remediation : 1 · targeted_practice : 11.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-SUITES-EV-A`, `1SPE-SUITES-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (10–10 min) — `1SPE-SUITES-EX-002..005`
- parcours 2 : 4 exercices (20–22 min) — `1SPE-SUITES-EX-022..023`, `1SPE-SUITES-EX-036..037`
- parcours 3 : 3 exercices (30–35 min) — `1SPE-SUITES-EX-040`, `1SPE-SUITES-EX-045`, `1SPE-SUITES-EX-048`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C2` — « Je sais montrer qu'une suite est arithmétique et exprimer son terme général. »

Libelle BO : Reconnaître si une suite est arithmétique. Exploiter la relation entre termes, la formule explicite.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 15 | `1SPE-SUITES-CO-006..008`, `1SPE-SUITES-CO-017`, `1SPE-SUITES-CO-022..025`, `1SPE-SUITES-CO-028..029`, `1SPE-SUITES-CO-033`, `1SPE-SUITES-CO-035`, `1SPE-SUITES-CO-039`, `1SPE-SUITES-CO-041`, `1SPE-SUITES-CO-047` |
| cours | 3 | `1SPE-SUITES-COURS-00`, `1SPE-SUITES-COURS-07-FR`, `1SPE-SUITES-CR-011` |
| evaluations | 2 | `1SPE-SUITES-EV-A`, `1SPE-SUITES-EV-B` |
| exercices | 15 | `1SPE-SUITES-EX-006..008`, `1SPE-SUITES-EX-017`, `1SPE-SUITES-EX-022..025`, `1SPE-SUITES-EX-028..029`, `1SPE-SUITES-EX-033`, `1SPE-SUITES-EX-035`, `1SPE-SUITES-EX-039`, `1SPE-SUITES-EX-041`, `1SPE-SUITES-EX-047` |
| methodes | 1 | `1SPE-SUITES-ME-002` |
| QCM | 3 | `Q4..6` |
| remediation | 1 | `1SPE-SUITES-RE-C2` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 15.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-SUITES-EV-A`, `1SPE-SUITES-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (10–10 min) — `1SPE-SUITES-EX-006..008`, `1SPE-SUITES-EX-017`
- parcours 2 : 9 exercices (20–25 min) — `1SPE-SUITES-EX-022..025`, `1SPE-SUITES-EX-028..029`, `1SPE-SUITES-EX-033`, `1SPE-SUITES-EX-035`, `1SPE-SUITES-EX-039`
- parcours 3 : 2 exercices (35–35 min) — `1SPE-SUITES-EX-041`, `1SPE-SUITES-EX-047`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C3` — « Je sais montrer qu'une suite est géométrique et exprimer son terme général. »

Libelle BO : Reconnaître si une suite est géométrique. Exploiter la relation entre termes, la formule explicite.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 23 | `1SPE-SUITES-CO-001`, `1SPE-SUITES-CO-009..010`, `1SPE-SUITES-CO-012`, `1SPE-SUITES-CO-015`, `1SPE-SUITES-CO-018..019`, `1SPE-SUITES-CO-026..027`, `1SPE-SUITES-CO-030..032`, `1SPE-SUITES-CO-034`, `1SPE-SUITES-CO-038..039`, `1SPE-SUITES-CO-041`, `1SPE-SUITES-CO-043..046`, `1SPE-SUITES-CO-048..050` |
| cours | 4 | `1SPE-SUITES-COURS-00`, `1SPE-SUITES-COURS-07-FR`, `1SPE-SUITES-COURS-07-TC`, `1SPE-SUITES-CR-012` |
| evaluations | 2 | `1SPE-SUITES-EV-A`, `1SPE-SUITES-EV-B` |
| exercices | 23 | `1SPE-SUITES-EX-001`, `1SPE-SUITES-EX-009..010`, `1SPE-SUITES-EX-012`, `1SPE-SUITES-EX-015`, `1SPE-SUITES-EX-018..019`, `1SPE-SUITES-EX-026..027`, `1SPE-SUITES-EX-030..032`, `1SPE-SUITES-EX-034`, `1SPE-SUITES-EX-038..039`, `1SPE-SUITES-EX-041`, `1SPE-SUITES-EX-043..046`, `1SPE-SUITES-EX-048..050` |
| methodes | 1 | `1SPE-SUITES-ME-003` |
| QCM | 3 | `Q7..9` |
| remediation | 1 | `1SPE-SUITES-RE-C3` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 23.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-SUITES-EV-A`, `1SPE-SUITES-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 7 exercices (10–10 min) — `1SPE-SUITES-EX-001`, `1SPE-SUITES-EX-009..010`, `1SPE-SUITES-EX-012`, `1SPE-SUITES-EX-015`, `1SPE-SUITES-EX-018..019`
- parcours 2 : 9 exercices (15–25 min) — `1SPE-SUITES-EX-026..027`, `1SPE-SUITES-EX-030..032`, `1SPE-SUITES-EX-034`, `1SPE-SUITES-EX-038..039`, `1SPE-SUITES-EX-050`
- parcours 3 : 7 exercices (35–40 min) — `1SPE-SUITES-EX-041`, `1SPE-SUITES-EX-043..046`, `1SPE-SUITES-EX-048..049`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C4` — « Je sais calculer la somme des premiers entiers et d'une suite géométrique. »

Libelle BO : Calculer la somme des n premiers entiers, la somme des premiers termes d'une suite géométrique.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 12 | `1SPE-SUITES-CO-011..013`, `1SPE-SUITES-CO-021`, `1SPE-SUITES-CO-024..027`, `1SPE-SUITES-CO-041..042`, `1SPE-SUITES-CO-046`, `1SPE-SUITES-CO-049` |
| cours | 2 | `1SPE-SUITES-COURS-00`, `1SPE-SUITES-CR-013` |
| evaluations | 2 | `1SPE-SUITES-EV-A`, `1SPE-SUITES-EV-B` |
| exercices | 12 | `1SPE-SUITES-EX-011..013`, `1SPE-SUITES-EX-021`, `1SPE-SUITES-EX-024..027`, `1SPE-SUITES-EX-041..042`, `1SPE-SUITES-EX-046`, `1SPE-SUITES-EX-049` |
| methodes | 1 | `1SPE-SUITES-ME-004` |
| QCM | 3 | `Q10..12` |
| remediation | 1 | `1SPE-SUITES-RE-C4` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 12.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-SUITES-EV-A`, `1SPE-SUITES-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (10–10 min) — `1SPE-SUITES-EX-011..013`, `1SPE-SUITES-EX-021`
- parcours 2 : 4 exercices (20–22 min) — `1SPE-SUITES-EX-024..027`
- parcours 3 : 4 exercices (35–40 min) — `1SPE-SUITES-EX-041..042`, `1SPE-SUITES-EX-046`, `1SPE-SUITES-EX-049`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C5` — « Je sais étudier le sens de variation d'une suite par la méthode adaptée. »

Libelle BO : Étudier le sens de variation d'une suite : étude du signe de u(n+1)−u(n), ou du quotient si les termes sont strictement positifs, ou utilisation de la fonction associée.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 21 | `1SPE-SUITES-CO-007`, `1SPE-SUITES-CO-010`, `1SPE-SUITES-CO-014..016`, `1SPE-SUITES-CO-023`, `1SPE-SUITES-CO-028..033`, `1SPE-SUITES-CO-036..037`, `1SPE-SUITES-CO-040`, `1SPE-SUITES-CO-042..043`, `1SPE-SUITES-CO-045`, `1SPE-SUITES-CO-047..049` |
| cours | 3 | `1SPE-SUITES-COURS-00`, `1SPE-SUITES-COURS-07-TC`, `1SPE-SUITES-CR-014` |
| evaluations | 2 | `1SPE-SUITES-EV-A`, `1SPE-SUITES-EV-B` |
| exercices | 21 | `1SPE-SUITES-EX-007`, `1SPE-SUITES-EX-010`, `1SPE-SUITES-EX-014..016`, `1SPE-SUITES-EX-023`, `1SPE-SUITES-EX-028..033`, `1SPE-SUITES-EX-036..037`, `1SPE-SUITES-EX-040`, `1SPE-SUITES-EX-042..043`, `1SPE-SUITES-EX-045`, `1SPE-SUITES-EX-047..049` |
| methodes | 1 | `1SPE-SUITES-ME-005` |
| QCM | 3 | `Q13..15` |
| remediation | 1 | `1SPE-SUITES-RE-C5` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 21.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-SUITES-EV-A`, `1SPE-SUITES-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 5 exercices (10–10 min) — `1SPE-SUITES-EX-007`, `1SPE-SUITES-EX-010`, `1SPE-SUITES-EX-014..016`
- parcours 2 : 9 exercices (20–22 min) — `1SPE-SUITES-EX-023`, `1SPE-SUITES-EX-028..033`, `1SPE-SUITES-EX-036..037`
- parcours 3 : 7 exercices (30–40 min) — `1SPE-SUITES-EX-040`, `1SPE-SUITES-EX-042..043`, `1SPE-SUITES-EX-045`, `1SPE-SUITES-EX-047..049`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C6` — « Je sais modéliser une situation concrète par une suite. »

Libelle BO : Modéliser un phénomène discret par une suite (évolutions successives, suites arithmétiques et géométriques comme modèles linéaire et exponentiel discrets).

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 15 | `1SPE-SUITES-CO-017..019`, `1SPE-SUITES-CO-024`, `1SPE-SUITES-CO-032..035`, `1SPE-SUITES-CO-038..039`, `1SPE-SUITES-CO-043..044`, `1SPE-SUITES-CO-046`, `1SPE-SUITES-CO-049..050` |
| cours | 4 | `1SPE-SUITES-COURS-00`, `1SPE-SUITES-COURS-07-FR`, `1SPE-SUITES-COURS-07-TC`, `1SPE-SUITES-CR-015` |
| evaluations | 2 | `1SPE-SUITES-EV-A`, `1SPE-SUITES-EV-B` |
| exercices | 15 | `1SPE-SUITES-EX-017..019`, `1SPE-SUITES-EX-024`, `1SPE-SUITES-EX-032..035`, `1SPE-SUITES-EX-038..039`, `1SPE-SUITES-EX-043..044`, `1SPE-SUITES-EX-046`, `1SPE-SUITES-EX-049..050` |
| methodes | 1 | `1SPE-SUITES-ME-006` |
| QCM | 3 | `Q16..18` |
| remediation | 1 | `1SPE-SUITES-RE-C6` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 15.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-SUITES-EV-A`, `1SPE-SUITES-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 3 exercices (10–10 min) — `1SPE-SUITES-EX-017..019`
- parcours 2 : 8 exercices (15–25 min) — `1SPE-SUITES-EX-024`, `1SPE-SUITES-EX-032..035`, `1SPE-SUITES-EX-038..039`, `1SPE-SUITES-EX-050`
- parcours 3 : 4 exercices (35–40 min) — `1SPE-SUITES-EX-043..044`, `1SPE-SUITES-EX-046`, `1SPE-SUITES-EX-049`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C7` — « Je sais écrire et lire un programme Python (terme, somme, seuil). »

Libelle BO : Écrire et interpréter un programme calculant un terme, une somme de termes, un seuil.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 8 | `1SPE-SUITES-CO-020..021`, `1SPE-SUITES-CO-034..035`, `1SPE-SUITES-CO-044`, `1SPE-SUITES-CO-047`, `1SPE-SUITES-CO-049..050` |
| cours | 4 | `1SPE-SUITES-COURS-00`, `1SPE-SUITES-COURS-07-FR`, `1SPE-SUITES-COURS-07-TC`, `1SPE-SUITES-CR-016` |
| evaluations | 2 | `1SPE-SUITES-EV-A`, `1SPE-SUITES-EV-B` |
| exercices | 8 | `1SPE-SUITES-EX-020..021`, `1SPE-SUITES-EX-034..035`, `1SPE-SUITES-EX-044`, `1SPE-SUITES-EX-047`, `1SPE-SUITES-EX-049..050` |
| methodes | 1 | `1SPE-SUITES-ME-007` |
| QCM | 3 | `Q19..21` |
| remediation | 1 | `1SPE-SUITES-RE-C7` |

**Richesse declaree**

- type de capacite : `ATOMIC_SUPPORT` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 8.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-SUITES-EV-A`, `1SPE-SUITES-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 2 exercices (10–10 min) — `1SPE-SUITES-EX-020..021`
- parcours 2 : 3 exercices (15–25 min) — `1SPE-SUITES-EX-034..035`, `1SPE-SUITES-EX-050`
- parcours 3 : 3 exercices (35–40 min) — `1SPE-SUITES-EX-044`, `1SPE-SUITES-EX-047`, `1SPE-SUITES-EX-049`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C8` — « Je sais reconnaître intuitivement une limite finie, une limite infinie ou une absence de limite, sans formalisation. »

Libelle BO : Sensibilisation intuitive à la notion de limite d'une suite : limite finie, limite infinie et absence de limite ; toute formalisation est exclue.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 10 | `1SPE-SUITES-CO-027`, `1SPE-SUITES-CO-037`, `1SPE-SUITES-CO-040`, `1SPE-SUITES-CO-042..043`, `1SPE-SUITES-CO-045..046`, `1SPE-SUITES-CO-048..049`, `1SPE-SUITES-CO-051` |
| cours | 2 | `1SPE-SUITES-COURS-00`, `1SPE-SUITES-CR-017` |
| evaluations | 2 | `1SPE-SUITES-EV-A`, `1SPE-SUITES-EV-B` |
| exercices | 10 | `1SPE-SUITES-EX-027`, `1SPE-SUITES-EX-037`, `1SPE-SUITES-EX-040`, `1SPE-SUITES-EX-042..043`, `1SPE-SUITES-EX-045..046`, `1SPE-SUITES-EX-048..049`, `1SPE-SUITES-EX-051` |
| methodes | 1 | `1SPE-SUITES-ME-008` |
| QCM | 1 | `Q3` |
| remediation | 1 | `1SPE-SUITES-RE-C8` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 1 · remediation : 1 · targeted_practice : 10.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-SUITES-EV-A`, `1SPE-SUITES-EV-B`.

**Progression de difficulte declaree**

- parcours 2 : 3 exercices (15–20 min) — `1SPE-SUITES-EX-027`, `1SPE-SUITES-EX-037`, `1SPE-SUITES-EX-051`
- parcours 3 : 7 exercices (30–40 min) — `1SPE-SUITES-EX-040`, `1SPE-SUITES-EX-042..043`, `1SPE-SUITES-EX-045..046`, `1SPE-SUITES-EX-048..049`
- palier sans exercice cible : parcours 1.

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

## 5. Question de QCM routee vers l'humain

Aucune question de ce chapitre n'est routee vers une revue humaine par `audit/QCM_INDEPENDENT_EVIDENCE_V2.json`.

## 6. Coherence du chapitre et coherence au niveau du manuel

- diversite des gestes de raisonnement au niveau du chapitre : `INSUFFICIENT` (declaratif : `INSUFFICIENT`).
- aucun profil de diversite declare pour ce chapitre : les gestes de raisonnement ne sont pas mesures, ils restent a juger.
- capacites routees vers l'humain : 8 sur 8.
- attendus officiels obligatoires rattaches : 15 sur 15 ; manquants : 0 ; hors annee : 0.
- chapitres dont ce chapitre depend par ses prerequis : `2GT`, `SNT`. La coherence au niveau du manuel se juge avec eux.

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

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-SUITES/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
