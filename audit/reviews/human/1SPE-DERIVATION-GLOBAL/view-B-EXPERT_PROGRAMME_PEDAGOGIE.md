# Vue de lecture — Dérivation : applications aux variations — EXPERT_PROGRAMME_PEDAGOGIE

Chapitre `1SPE-DERIVATION-GLOBAL` · manuel `1SPE` (Première, Spécialité mathématiques) · packet B · role `EXPERT_PROGRAMME_PEDAGOGIE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-DERIVATION-GLOBAL/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`
> Etat de revue : `audit/reviews/human/1SPE-DERIVATION-GLOBAL/REVIEW_STATE.json`
> Producteur de cette vue : `scripts/build_human_review_reading_views.py`
>
> Toute divergence entre cette vue et le packet se tranche en faveur du packet. Cette vue ne cree, ne ferme et ne reduit aucune obligation.

## 1. Ce que vous decidez

- L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.
- Aucun humain n'a encore approuve ce chapitre : REVIEW_DELTA_BASELINE = NONE. Le perimetre de revue est le CHAPITRE COURANT ENTIER. Les listes ci-dessous dirigent l'attention, elles ne reduisent pas le perimetre.
- CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST (`sha256:532209e1d6fb906707a0631eef12a5a438d0a8dbaf477b923be219a35d83ff36`) ; l'approbation graphique releve de la porte D7, independante.
- Verdicts autorises, a rendre dans le packet JSON canonique et jamais dans cette vue : `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`.
- Cette vue ne porte aucune decision et ne nomme personne : l'assignation du role reste `PENDING_UNASSIGNED`, l'etat du packet reste `PENDING_UNASSIGNED`.

| Perimetre | Valeur |
| --- | --- |
| Objets du chapitre dans le packet | 151 |
| Empreinte de l'ensemble d'objets | `sha256:8356fd05cbe695f0bffd4fda5ed5fd8b0cc3566675daaa189e44bdf2710f6d6c` |
| Empreinte semantique liee a l'approbation | `sha256:532209e1d6fb906707a0631eef12a5a438d0a8dbaf477b923be219a35d83ff36` |
| Empreinte du packet | `sha256:6266b04b6828ca689666a4695bfdbf8c3b53877f66aed355494330f3d3773548` |
| Revision du depot gelee dans le packet | `5bc44275a0afe33f10b7ce2ec7700778f8de6308` |
| Preuve de rendu portee par le packet | `ABSENT` |

## 2. Le chapitre et ses capacites du programme officiel

**Dérivation : applications aux variations** — programme applicable 2026-2027, MENE2602917A, BO n° 14 du 2026-04-02.
Source officielle : https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A

Situation d'accroche declaree : Un fabricant de boîtes de conserve veut minimiser la quantité de métal utilisée pour un volume donné de 500 mL. Quelles dimensions de la boîte cylindrique choisir ? La dérivation permet de répondre à ce problème d'optimisation.

Temps estime declare : parcours 1 : 12 h · parcours 2 : 10 h · parcours 3 : 8 h.

| Code | Libelle eleve | Libelle BO | Demonstration exigible |
| --- | --- | --- | --- |
| `C1` | Je sais dériver les fonctions de référence (puissances, inverse, racine carrée). | Calculer la dérivée de fonctions de référence : x^n, 1/x, racine(x). | non |
| `C2` | Je sais utiliser les règles de dérivation (somme, produit, quotient). | Calculer la dérivée d'une somme, d'un produit par un réel, d'un produit, d'un quotient de fonctions dérivables. | oui — Dérivée d'une somme et d'un produit par un scalaire. |
| `C3` | Je sais utiliser le signe de la dérivée pour dresser le tableau de variations. | Exploiter le lien entre le signe de la dérivée et le sens de variation d'une fonction. | non |
| `C4` | Je sais trouver les extremums d'une fonction en annulant sa dérivée. | Déterminer les extremums d'une fonction polynôme de degré 3. | non |
| `C5` | Je sais modéliser et résoudre un problème d'optimisation à l'aide de la dérivation. | Résoudre un problème d'optimisation. | non |

**Attendus officiels rattaches, capacite par capacite**

- `C1` — 6 attendus :
    - `1SPE-OFFICIAL-084` (MANDATORY_KNOWLEDGE, Dérivation — point de vue global) : Fonction dérivable sur un intervalle. Fonction dérivée.
    - `1SPE-OFFICIAL-085` (MANDATORY_KNOWLEDGE, Dérivation — point de vue global) : Fonction dérivée des fonctions carré, cube, inverse, racine carrée.
    - `1SPE-OFFICIAL-087` (MANDATORY_KNOWLEDGE, Dérivation — point de vue global) : Pour 𝑛 dans ℤ, fonction dérivée de la fonction 𝑥 ↦ 𝑥 𝑛.
    - `1SPE-OFFICIAL-088` (MANDATORY_KNOWLEDGE, Dérivation — point de vue global) : Fonction valeur absolue : étude de la dérivabilité en 0.
    - `1SPE-OFFICIAL-096` (MANDATORY_SKILL, Point de vue global) : La fonction racine carrée n’est pas dérivable en 0.
    - `1SPE-OFFICIAL-097` (MANDATORY_SKILL, Point de vue global) : Fonction dérivée de la fonction carrée, de la fonction inverse.
- `C2` — 3 attendus :
    - `1SPE-OFFICIAL-086` (MANDATORY_KNOWLEDGE, Dérivation — point de vue global) : Opérations sur les fonctions dérivables : somme, produit, inverse, quotient.
    - `1SPE-OFFICIAL-094` (MANDATORY_CAPACITY, Point de vue global) : Dans des cas simples, calculer une fonction dérivée en utilisant les propriétés des opérations sur les fonctions dérivables.
    - `1SPE-OFFICIAL-098` (MANDATORY_SKILL, Point de vue global) : Fonction dérivée d’un produit.
- `C3` — 4 attendus :
    - `1SPE-OFFICIAL-100` (MANDATORY_KNOWLEDGE, Variations et courbes représentatives des fonctions) : Représentation algébrique et graphique de fonctions paires, impaires. Traduction géométrique.
    - `1SPE-OFFICIAL-101` (MANDATORY_KNOWLEDGE, Variations et courbes représentatives des fonctions) : Lien entre le sens de variation d’une fonction dérivable sur un intervalle et signe de sa fonction dérivée ; caractérisation des fonctions constantes.
    - `1SPE-OFFICIAL-105` (MANDATORY_CAPACITY, Variations et courbes représentatives des fonctions) : Exploiter les variations d’une fonction pour établir une inégalité. Étudier la position relative de deux courbes représentatives.
    - `1SPE-OFFICIAL-106` (MANDATORY_CAPACITY, Variations et courbes représentatives des fonctions) : Étudier, en lien avec la dérivation, une fonction polynôme du second degré : variations, extrémum, allure selon le signe du coefficient de 𝑥².
- `C4` — 2 attendus :
    - `1SPE-OFFICIAL-102` (MANDATORY_KNOWLEDGE, Variations et courbes représentatives des fonctions) : Nombre dérivé en un extrémum, tangente à la courbe représentative.
    - `1SPE-OFFICIAL-103` (MANDATORY_CAPACITY, Variations et courbes représentatives des fonctions) : Étudier les variations d’une fonction. Déterminer les extrémums.
- `C5` — 1 attendu :
    - `1SPE-OFFICIAL-104` (MANDATORY_CAPACITY, Variations et courbes représentatives des fonctions) : Résoudre un problème d’optimisation.

**Prerequis declares par le contrat du chapitre**

| Code | Libelle | Chapitre d'origine |
| --- | --- | --- |
| `R1` | Taux de variation et nombre dérivé | 1SPE-DERIVATION-LOCAL |
| `R2` | Équation de la tangente | 1SPE-DERIVATION-LOCAL |
| `R3` | Calcul littéral (développer, factoriser, signe d'un produit/quotient) | 2GT |
| `R4` | Fonctions polynômes du second degré (racines, signe, tableau de signes) | 1SPE-SECOND-DEGRE |
| `R5` | Sens de variation d'une fonction (définition, croissante/décroissante) | 2GT |

## 3. Structure reelle et ordre d'assemblage courant

L'ordre ci-dessous n'est pas l'ordre alphabetique des repertoires : il est lu chez l'assembleur du manuel (`Mathematiques/manuel-maths/scripts/assemble_manuel.py`, `collect_chapter`). C'est la sequence que le lecteur du PDF recoit.

| Rang | Rubrique imprimee | Objets (professeur) |
| --- | --- | --- |
| 1 | Cours | 5 |
| 2 | Méthodes | 5 |
| 3 | Exercices | 71 |
| 4 | TD | 2 |
| 5 | Auto-évaluation | 1 |
| 6 | Évaluation | 4 |
| 7 | Remédiation | 10 |
| 8 | Corrigés | 53 |

Total assemble : 151 objets en variante professeur, 96 en variante eleve (la variante eleve exclut les corriges et les corriges d'evaluation).

La page d'ouverture du chapitre est composee par l'assembleur a partir de `contrat.yaml` (titre, capacites, situation d'accroche, temps estime) : elle n'apparait donc pas comme un objet de la sequence.

**Placement des temps pedagogiques dans la progression**

- rubrique « Diagnostic » : aucun objet assemble dans ce chapitre.
- rang 1 — le cours precede les methodes.
- rang 2 — les methodes sont regroupees avant les exercices.
- rang 3 — les exercices suivent les methodes en un seul bloc.
- rang 4 — le TD est place apres les exercices.
- rang 5 — le QCM d'auto-evaluation suit le TD.
- rang 6 — les evaluations viennent apres le QCM.
- rang 7 — la remediation est placee apres les evaluations.
- rang 8 — les corriges ferment la variante professeur.

Cet ordre est un fait d'assemblage, pas un jugement : sa pertinence pedagogique fait partie de ce que vous evaluez.

## 4. Capacite par capacite : cellules, contributeurs, richesse

`audit/SEMANTIC_ALIGNMENT_LEDGER.json` decoupe le manuel en cellules capacite x role pedagogique. Ce chapitre en porte 35. Elles sont regroupees ici par capacite : une checklist cellule par cellule ne se lit pas.

**Pourquoi ces cellules arrivent chez vous.** Seul le META rattache les corps a une capacite ; l'identite declaree est resolue par egalite exacte, et la couverture de reponses n'etablit qu'une COUVERTURE. Etablir qu'un corps SERT la capacite est un jugement pedagogique, pas un calcul : c'est un resultat terminal, pas une lacune de mesure. C'est pourquoi chaque cellule de ce chapitre est routee vers vous.

Chaque capacite rappelle ensuite ce qui lui est propre : le nombre de cellules, leur disposition, les preuves eventuellement attachees et l'etat de sa richesse.

### Capacite `C1` — « Je sais dériver les fonctions de référence (puissances, inverse, racine carrée). »

Libelle BO : Calculer la dérivée de fonctions de référence : x^n, 1/x, racine(x).

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 14 | `1SPE-DERGLOBAL-CO-001..010`, `1SPE-DERGLOBAL-CO-047`, `1SPE-DERGLOBAL-CO-050`, `1SPE-DERGLOBAL-CO-052..053` |
| cours | 1 | `1SPE-DERGLOBAL-COURS-C1` |
| evaluations | 2 | `1SPE-DERGLOBAL-EV-A`, `1SPE-DERGLOBAL-EV-B` |
| exercices | 14 | `1SPE-DERGLOBAL-EX-001..010`, `1SPE-DERGLOBAL-EX-047`, `1SPE-DERGLOBAL-EX-050`, `1SPE-DERGLOBAL-EX-052..053` |
| methodes | 1 | `1SPE-DERGLOBAL-ME-001` |
| QCM | 3 | `Q1..3` |
| remediation | 1 | `1SPE-DERIVATION-GLOBAL-RE-C1` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 14.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-DERGLOBAL-EV-A`, `1SPE-DERGLOBAL-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 5 exercices (5–6 min) — `1SPE-DERGLOBAL-EX-001..004`, `1SPE-DERGLOBAL-EX-053`
- parcours 2 : 5 exercices (10–12 min) — `1SPE-DERGLOBAL-EX-005..008`, `1SPE-DERGLOBAL-EX-052`
- parcours 3 : 4 exercices (18–20 min) — `1SPE-DERGLOBAL-EX-009..010`, `1SPE-DERGLOBAL-EX-047`, `1SPE-DERGLOBAL-EX-050`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C2` — « Je sais utiliser les règles de dérivation (somme, produit, quotient). »

Libelle BO : Calculer la dérivée d'une somme, d'un produit par un réel, d'un produit, d'un quotient de fonctions dérivables.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 13 | `1SPE-DERGLOBAL-CO-011..020`, `1SPE-DERGLOBAL-CO-047..048`, `1SPE-DERGLOBAL-CO-050` |
| cours | 1 | `1SPE-DERGLOBAL-COURS-C2` |
| evaluations | 2 | `1SPE-DERGLOBAL-EV-A`, `1SPE-DERGLOBAL-EV-B` |
| exercices | 13 | `1SPE-DERGLOBAL-EX-011..020`, `1SPE-DERGLOBAL-EX-047..048`, `1SPE-DERGLOBAL-EX-050` |
| methodes | 1 | `1SPE-DERGLOBAL-ME-002` |
| QCM | 3 | `Q4..6` |
| remediation | 1 | `1SPE-DERIVATION-GLOBAL-RE-C2` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 13.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-DERGLOBAL-EV-A`, `1SPE-DERGLOBAL-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (5–5 min) — `1SPE-DERGLOBAL-EX-011..014`
- parcours 2 : 4 exercices (12–12 min) — `1SPE-DERGLOBAL-EX-015..018`
- parcours 3 : 5 exercices (18–20 min) — `1SPE-DERGLOBAL-EX-019..020`, `1SPE-DERGLOBAL-EX-047..048`, `1SPE-DERGLOBAL-EX-050`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C3` — « Je sais utiliser le signe de la dérivée pour dresser le tableau de variations. »

Libelle BO : Exploiter le lien entre le signe de la dérivée et le sens de variation d'une fonction.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 14 | `1SPE-DERGLOBAL-CO-021..030`, `1SPE-DERGLOBAL-CO-047..049`, `1SPE-DERGLOBAL-CO-051` |
| cours | 1 | `1SPE-DERGLOBAL-COURS-C3` |
| evaluations | 2 | `1SPE-DERGLOBAL-EV-A`, `1SPE-DERGLOBAL-EV-B` |
| exercices | 14 | `1SPE-DERGLOBAL-EX-021..030`, `1SPE-DERGLOBAL-EX-047..049`, `1SPE-DERGLOBAL-EX-051` |
| methodes | 1 | `1SPE-DERGLOBAL-ME-003` |
| QCM | 3 | `Q7..9` |
| remediation | 1 | `1SPE-DERIVATION-GLOBAL-RE-C3` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 14.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-DERGLOBAL-EV-A`, `1SPE-DERGLOBAL-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 5 exercices (5–8 min) — `1SPE-DERGLOBAL-EX-021..024`, `1SPE-DERGLOBAL-EX-051`
- parcours 2 : 4 exercices (12–15 min) — `1SPE-DERGLOBAL-EX-025..028`
- parcours 3 : 5 exercices (18–20 min) — `1SPE-DERGLOBAL-EX-029..030`, `1SPE-DERGLOBAL-EX-047..049`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C4` — « Je sais trouver les extremums d'une fonction en annulant sa dérivée. »

Libelle BO : Déterminer les extremums d'une fonction polynôme de degré 3.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 12 | `1SPE-DERGLOBAL-CO-031..040`, `1SPE-DERGLOBAL-CO-048..049` |
| cours | 1 | `1SPE-DERGLOBAL-COURS-C4` |
| evaluations | 2 | `1SPE-DERGLOBAL-EV-A`, `1SPE-DERGLOBAL-EV-B` |
| exercices | 12 | `1SPE-DERGLOBAL-EX-031..040`, `1SPE-DERGLOBAL-EX-048..049` |
| methodes | 1 | `1SPE-DERGLOBAL-ME-004` |
| QCM | 3 | `Q10..12` |
| remediation | 1 | `1SPE-DERIVATION-GLOBAL-RE-C4` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 12.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-DERGLOBAL-EV-A`, `1SPE-DERGLOBAL-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (5–5 min) — `1SPE-DERGLOBAL-EX-031..034`
- parcours 2 : 4 exercices (12–15 min) — `1SPE-DERGLOBAL-EX-035..038`
- parcours 3 : 4 exercices (18–20 min) — `1SPE-DERGLOBAL-EX-039..040`, `1SPE-DERGLOBAL-EX-048..049`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C5` — « Je sais modéliser et résoudre un problème d'optimisation à l'aide de la dérivation. »

Libelle BO : Résoudre un problème d'optimisation.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 8 | `1SPE-DERGLOBAL-CO-041..046`, `1SPE-DERGLOBAL-CO-049..050` |
| cours | 1 | `1SPE-DERGLOBAL-COURS-C5` |
| evaluations | 2 | `1SPE-DERGLOBAL-EV-A`, `1SPE-DERGLOBAL-EV-B` |
| exercices | 8 | `1SPE-DERGLOBAL-EX-041..046`, `1SPE-DERGLOBAL-EX-049..050` |
| methodes | 1 | `1SPE-DERGLOBAL-ME-005` |
| QCM | 3 | `Q13..15` |
| remediation | 1 | `1SPE-DERIVATION-GLOBAL-RE-C5` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 8.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-DERGLOBAL-EV-A`, `1SPE-DERGLOBAL-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 2 exercices (5–5 min) — `1SPE-DERGLOBAL-EX-041..042`
- parcours 2 : 2 exercices (15–15 min) — `1SPE-DERGLOBAL-EX-043..044`
- parcours 3 : 4 exercices (20–20 min) — `1SPE-DERGLOBAL-EX-045..046`, `1SPE-DERGLOBAL-EX-049..050`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

## 5. Question de QCM routee vers l'humain

Aucune question de ce chapitre n'est routee vers une revue humaine par `audit/QCM_INDEPENDENT_EVIDENCE_V2.json`.

## 6. Coherence du chapitre et coherence au niveau du manuel

- diversite des gestes de raisonnement au niveau du chapitre : `INSUFFICIENT` (declaratif : `INSUFFICIENT`).
- aucun profil de diversite declare pour ce chapitre : les gestes de raisonnement ne sont pas mesures, ils restent a juger.
- capacites routees vers l'humain : 5 sur 5.
- attendus officiels obligatoires rattaches : 16 sur 16 ; manquants : 0 ; hors annee : 0.
- chapitres dont ce chapitre depend par ses prerequis : `1SPE-DERIVATION-LOCAL`, `1SPE-SECOND-DEGRE`, `2GT`. La coherence au niveau du manuel se juge avec eux.

La regle du depot : « la richesse se mesure en occasions distinctes et en gestes de raisonnement declares ; jamais en nombre de fichiers ».

## 7. Barème commenté — propositions à juger

La politique est fixée : pour chaque question évaluée, des POINTS, un ATTENDU ESSENTIEL, et un CRÉDIT PARTIEL seulement lorsqu'une décomposition objective le justifie. Le corrigé scientifique reste séparé et complet ; le barème ne le remplace pas.

Ces propositions sont **machine** et ne valent aucune approbation. Elles sont le contenu candidat que votre verdict de chapitre couvre.

### 1SPE-DERGLOBAL-EV-A

**Exercice 1** — 5 points (C1, C2)

- **Q1** — 1 pt — Attendu : calculer — $f(x) = 3x^2 - 2x + 1$, donc $f'(x) = 6x - 2.$.
- **Q2** — 1,5 pt — Attendu : calculer — La courbe « monte » localement avec une pente de $10$ en ce point.
- **Q3** — 1,5 pt — Attendu : donner — $f(2) = 3 \times 4 - 2 \times 2 + 1 = 12 - 4 + 1 = 9.$ Équation de la tangente : \[ T : y = f'(2)(x - 2) + f(2) = 10(x-2) + 9 = 10x - 20 + 9 = 10x - 11.
- **Q4** — 1 pt — Attendu : déterminer — Tangente horizontale $\Leftrightarrow f'(x) = 0 \Leftrightarrow 6x - 2 = 0 \Leftrightarrow x = \dfrac{1}{3}.$.

**Exercice 2** — 6 points (C3, C4) · 1 question(s) en attente de jugement

- **Q1** — 1,5 pt — Attendu : calculer — $g(x) = x^3 - 6x$, donc $g'(x) = 3x^2 - 6 = 3(x^2 - 2) = 3(x - \sqrt{2})(x + \sqrt{2}).$.
- **Q2** — 1,5 pt — Attendu : résoudre — $g'(x) = 0 \Leftrightarrow x = -\sqrt{2}$ ou $x = \sqrt{2}$ \quad ($\sqrt{2} \approx 1{,}41$).
- **Q3** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le corrigé n'établit aucun résultat repérable
- **Q4** — 1 pt — Attendu : donner — $g$ admet un \textbf{minimum local} de $-4\sqrt{2} \approx -5{,}66$ en $x = \sqrt{2}$.

**Exercice 3** — 5 points (C2, C3, C4) · 1 question(s) en attente de jugement

- **Q1** — 2 pts — Attendu : calculer — \[ h'(x) = \frac{u'v - uv'}{v^2} = \frac{2x(x-1) - (x^2+2)}{(x-1)^2} = \frac{2x^2 - 2x - x^2 - 2}{(x-1)^2} = \frac{x^2 - 2x - 2}{(x-1)^2}.
- **Q2** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le corrigé n'établit aucun résultat repérable
- **Q3** — 1,5 pt — Attendu : construire — Le signe de $h'$ est celui du numérateur $x^2-2x-2$ : $h'(x) < 0$ pour $1 < x < 1+\sqrt{3}$ et $h'(x) > 0$ pour $x > 1+\sqrt{3}$.

**Exercice 4** — 4 points (C5)

- **Q1** — 1 pt — Attendu : exprimer — $R(x) = x \times (20 - x) = 20x - x^2.$.
- **Q2** — 2 pts — Attendu : calculer — $R'(x) = 20 - 2x.$ $R'(x) = 0 \Leftrightarrow x = 10.$ $R'(x) > 0$ pour $x < 10$ et $R'(x) < 0$ pour $x > 10$ : $R$ est maximale en $x = 10$.
- **Q3** — 1 pt — Attendu : calculer — Le maraîcher maximise son chiffre d'affaires en vendant $10$ kg de tomates au prix de $10$ euros/kg, pour un chiffre d'affaires de $\mathbf{100}$ euros.

### 1SPE-DERGLOBAL-EV-B

**Exercice 1** — 5 points (C1, C2)

- **Q1** — 1 pt — Attendu : calculer — $f(x) = 2x^2 + 3x - 4$, donc $f'(x) = 4x + 3.$.
- **Q2** — 1,5 pt — Attendu : calculer — La courbe monte localement avec une pente de $7$ en ce point.
- **Q3** — 1,5 pt — Attendu : donner — \] Vérification : $T(1) = 7 - 6 = 1 = f(1)$.
- **Q4** — 1 pt — Attendu : déterminer — Tangente horizontale $\Leftrightarrow f'(x) = 0 \Leftrightarrow 4x + 3 = 0 \Leftrightarrow x = -\dfrac{3}{4}.$.

**Exercice 2** — 6 points (C3, C4) · 2 question(s) en attente de jugement

- **Q1** — 1,5 pt — Attendu : calculer — $g(x) = 2x^3 - 9x^2 + 12x$, donc $g'(x) = 6x^2 - 18x + 12 = 6(x^2 - 3x + 2) = 6(x-1)(x-2).$.
- **Q2** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le corrigé n'établit aucun résultat repérable
- **Q3** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le corrigé n'établit aucun résultat repérable
- **Q4** — 1 pt — Attendu : donner — $g$ admet un \textbf{minimum local} de $4$ en $x = 2$.

**Exercice 3** — 5 points (C2, C3, C4)

- **Q1** — 1 pt — Attendu : simplifier — $x^2 - 4 = (x-2)(x+2)$, donc pour $x \neq -2$ : \[ h(x) = \frac{(x-2)(x+2)}{x+2} = x - 2.
- **Q2** — 1,5 pt — Attendu : en déduire — $h(x) = x - 2$ (pour $x \neq -2$), donc $h'(x) = 1$.
- **Q3** — 2,5 pts — Attendu : résoudre — $h$ est strictement croissante sur $]-\infty\,;\,-2[$.

**Exercice 4** — 4 points (C5) · 1 question(s) en attente de jugement

- **Q1** — 1 pt — Attendu : exprimer — $R(x) = x \times (30 - 2x) = 30x - 2x^2.$.
- **Q2** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le corrigé n'établit aucun résultat repérable
- **Q3** — 1 pt — Attendu : calculer — Le producteur maximise son chiffre d'affaires en vendant $7{,}5$ litres au prix de $30 - 2 \times 7{,}5 = 15$ euros/L, pour un chiffre d'affaires de $\mathbf{112{,}5}$ euros.

Ce chapitre porte 28 question(s) évaluée(s), dont 5 attendent votre jugement. Ce ne sont pas autant de signatures : votre verdict porte sur le chapitre.

## 8. Checklist du role `EXPERT_PROGRAMME_PEDAGOGIE`

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

## 9. Reference de lecture : le PDF candidat

Le PDF sert a lire le chapitre dans l'ordre ou l'eleve le recevra. Il n'est pas une preuve : le packet ne porte aucune preuve de rendu (`render_evidence = ABSENT`), et aucun index page-objet n'est etabli.

| Fichier | Variante | Pages | Role declare | Etat declare |
| --- | --- | --- | --- | --- |
| `MANUELS_PDF_PUBLICATION/01_Maths_1re_Spe_Eleve.pdf` | eleve | 371 | HISTORICAL_PUBLICATION_SNAPSHOT | STALE_UNDECIDED |
| `MANUELS_PDF_PUBLICATION/02_Maths_1re_Spe_Professeur.pdf` | professeur | 617 | HISTORICAL_PUBLICATION_SNAPSHOT | STALE_UNDECIDED |

Ces instantanes sont declares `STALE_UNDECIDED` dans `audit/PDF_ARTIFACT_REGISTRY.yaml` : ils ne sont pas garantis identiques au contenu courant. Le candidat d'impression courant se reconstruit par `python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py --manual 1SPE --variant <variant> --record-observed` (recu : `audit/1SPE_PRINT_CANDIDATE_BUILD_RECEIPT.json`, statut `PRINT_CANDIDATE`).

Rappel du recu : Ces PDF ne sont pas finals : aucun 1SPE_FINAL_CONTENT_SHA n'est figé, les deux revues humaines par chapitre et le dossier D7 restent en attente.

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-DERIVATION-GLOBAL/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
