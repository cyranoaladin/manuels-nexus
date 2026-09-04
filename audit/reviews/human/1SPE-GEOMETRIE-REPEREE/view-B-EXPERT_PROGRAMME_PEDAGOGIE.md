# Vue de lecture — Géométrie repérée — EXPERT_PROGRAMME_PEDAGOGIE

Chapitre `1SPE-GEOMETRIE-REPEREE` · manuel `1SPE` (Première, Spécialité mathématiques) · packet B · role `EXPERT_PROGRAMME_PEDAGOGIE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-GEOMETRIE-REPEREE/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`
> Etat de revue : `audit/reviews/human/1SPE-GEOMETRIE-REPEREE/REVIEW_STATE.json`
> Producteur de cette vue : `scripts/build_human_review_reading_views.py`
>
> Toute divergence entre cette vue et le packet se tranche en faveur du packet. Cette vue ne cree, ne ferme et ne reduit aucune obligation.

## 1. Ce que vous decidez

- L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.
- Aucun humain n'a encore approuve ce chapitre : REVIEW_DELTA_BASELINE = NONE. Le perimetre de revue est le CHAPITRE COURANT ENTIER. Les listes ci-dessous dirigent l'attention, elles ne reduisent pas le perimetre.
- CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST (`sha256:1c272be34cef94c7ce8923f5d8cb72728c8b8023417d08f4430e4ee4ddce8a9f`) ; l'approbation graphique releve de la porte D7, independante.
- Verdicts autorises, a rendre dans le packet JSON canonique et jamais dans cette vue : `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`.
- Cette vue ne porte aucune decision et ne nomme personne : l'assignation du role reste `PENDING_UNASSIGNED`, l'etat du packet reste `PENDING_UNASSIGNED`.

| Perimetre | Valeur |
| --- | --- |
| Objets du chapitre dans le packet | 147 |
| Empreinte de l'ensemble d'objets | `sha256:8804a15ed1bc1652fa9527db622db88806ec02981d1cc29ccdb1a2d1876d76f1` |
| Empreinte semantique liee a l'approbation | `sha256:1c272be34cef94c7ce8923f5d8cb72728c8b8023417d08f4430e4ee4ddce8a9f` |
| Empreinte du packet | `sha256:495ada6345dfc40a7acf52fb98bf167c3edd2a88c969eaafb3dd9605af6126b3` |
| Revision du depot gelee dans le packet | `dfc99058e7a7c16ae4af46b99245edbe14b4f8e5` |
| Preuve de rendu portee par le packet | `ABSENT` |

## 2. Le chapitre et ses capacites du programme officiel

**Géométrie repérée** — programme applicable 2026-2027, MENE2602917A, BO n° 14 du 2026-04-02.
Source officielle : https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A

Situation d'accroche declaree : Un ingénieur doit vérifier si un câble rectiligne (modélisé par une droite) traverse une zone circulaire interdite (modélisée par un cercle) dans un plan cartographique. Comment traduire ce problème en équations et le résoudre par le calcul ? Résolu au TD fil rouge avec les outils du chapitre (C1, C3, C4, C5).

Temps estime declare : parcours 1 : 12 h · parcours 2 : 10 h · parcours 3 : 9 h.

| Code | Libelle eleve | Libelle BO | Demonstration exigible |
| --- | --- | --- | --- |
| `C1` | Je sais déterminer une équation cartésienne d'une droite ax+by+c=0 et l'exploiter. | Déterminer une équation cartésienne d'une droite dans le plan repéré. | non |
| `C2` | Je sais utiliser un vecteur normal à une droite, passer d'une équation cartésienne à un vecteur directeur/normal et réciproquement. | Utiliser un vecteur normal à une droite pour déterminer son équation. | non |
| `C3` | Je sais déterminer et exploiter l'équation d'un cercle (x-a)²+(y-b)²=r². | Déterminer une équation du cercle de centre (a,b) et de rayon r. | non |
| `C4` | Je sais étudier les positions relatives de droites et de cercles (parallélisme, intersection, tangence). | Étudier les positions relatives de droites et cercles (parallélisme, intersection, tangence). | non |
| `C5` | Je sais résoudre des problèmes géométriques dans un repère orthonormé. | Résoudre des problèmes de géométrie plane dans un repère orthonormé. | non |

**Attendus officiels rattaches, capacite par capacite**

- `C1` — 2 attendus :
    - `1SPE-OFFICIAL-038` (MANDATORY_SKILL, Automatismes — fonctions et représentations) : Déterminer le coefficient directeur d’une droite à partir des coordonnées de deux de ses points.
    - `1SPE-OFFICIAL-143` (MANDATORY_CAPACITY, Géométrie repérée) : Déterminer une équation cartésienne d’une droite connaissant un point et un vecteur normal.
- `C2` — 1 attendu :
    - `1SPE-OFFICIAL-140` (MANDATORY_KNOWLEDGE, Géométrie repérée) : Vecteur normal à une droite. Le vecteur de coordonnées (a, b) est normal à la droite d’équation a𝑥 + b𝑦 + c = 0.
- `C3` — 3 attendus :
    - `1SPE-OFFICIAL-142` (MANDATORY_KNOWLEDGE, Géométrie repérée) : Équation de cercle.
    - `1SPE-OFFICIAL-145` (MANDATORY_CAPACITY, Géométrie repérée) : Déterminer et utiliser l’équation d’un cercle donné par son centre et son rayon.
    - `1SPE-OFFICIAL-146` (MANDATORY_CAPACITY, Géométrie repérée) : Reconnaitre une équation de cercle, déterminer centre et rayon.
- `C4` : aucun attendu officiel rattache dans `audit/SEMANTIC_ALIGNMENT_LEDGER.json`.
- `C5` — 3 attendus :
    - `1SPE-OFFICIAL-141` (MANDATORY_KNOWLEDGE, Géométrie repérée) : Projection orthogonale d’un point sur une droite.
    - `1SPE-OFFICIAL-144` (MANDATORY_CAPACITY, Géométrie repérée) : Déterminer les coordonnées du projeté orthogonal d’un point sur une droite.
    - `1SPE-OFFICIAL-147` (MANDATORY_CAPACITY, Géométrie repérée) : Utiliser un repère pour étudier une configuration.

**Prerequis declares par le contrat du chapitre**

| Code | Libelle | Chapitre d'origine |
| --- | --- | --- |
| `R1` | Repérage dans le plan : coordonnées, milieu, distance | 2GT |
| `R2` | Vecteurs et coordonnées : somme, produit par un scalaire, colinéarité | 2GT |
| `R3` | Produit scalaire : calcul, orthogonalité | 1SPE-PRODUIT-SCALAIRE |
| `R4` | Équations du second degré : discriminant, racines | 1SPE-SECOND-DEGRE |
| `R5` | Systèmes d'équations linéaires à deux inconnues | 2GT |

## 3. Structure reelle et ordre d'assemblage courant

L'ordre ci-dessous n'est pas l'ordre alphabetique des repertoires : il est lu chez l'assembleur du manuel (`Mathematiques/manuel-maths/scripts/assemble_manuel.py`, `collect_chapter`). C'est la sequence que le lecteur du PDF recoit.

| Rang | Rubrique imprimee | Objets (professeur) |
| --- | --- | --- |
| 1 | Ouverture | 1 |
| 2 | Diagnostic | 1 |
| 3 | Cours | 5 |
| 4 | Méthodes | 5 |
| 5 | Exercices | 68 |
| 6 | TD | 2 |
| 7 | Auto-évaluation | 1 |
| 8 | Évaluation | 4 |
| 9 | Remédiation | 10 |
| 10 | Corrigés | 50 |

Total assemble : 147 objets en variante professeur, 95 en variante eleve (la variante eleve exclut les corriges et les corriges d'evaluation).

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

`audit/SEMANTIC_ALIGNMENT_LEDGER.json` decoupe le manuel en cellules capacite x role pedagogique. Ce chapitre en porte 35. Elles sont regroupees ici par capacite : une checklist cellule par cellule ne se lit pas.

**Pourquoi ces cellules arrivent chez vous.** Seul le META rattache les corps a une capacite ; l'identite declaree est resolue par egalite exacte, et la couverture de reponses n'etablit qu'une COUVERTURE. Etablir qu'un corps SERT la capacite est un jugement pedagogique, pas un calcul : c'est un resultat terminal, pas une lacune de mesure. C'est pourquoi chaque cellule de ce chapitre est routee vers vous.

Chaque capacite rappelle ensuite ce qui lui est propre : le nombre de cellules, leur disposition, les preuves eventuellement attachees et l'etat de sa richesse.

### Capacite `C1` — « Je sais déterminer une équation cartésienne d'une droite ax+by+c=0 et l'exploiter. »

Libelle BO : Déterminer une équation cartésienne d'une droite dans le plan repéré.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 10 | `1SPE-GEOREP-CO-001..010` |
| cours | 3 | `1SPE-GEOREP-COURS-00`, `1SPE-GEOREP-COURS-07-FR`, `1SPE-GEOREP-CR-010` |
| evaluations | 2 | `1SPE-GEOREP-EV-A`, `1SPE-GEOREP-EV-B` |
| exercices | 10 | `1SPE-GEOREP-EX-001..010` |
| methodes | 1 | `1SPE-GEOREP-ME-001` |
| QCM | 3 | `Q1..3` |
| remediation | 1 | `1SPE-GEOREP-RE-C1` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 10.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-GEOREP-EV-A`, `1SPE-GEOREP-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (8–10 min) — `1SPE-GEOREP-EX-001..004`
- parcours 2 : 4 exercices (10–12 min) — `1SPE-GEOREP-EX-005..008`
- parcours 3 : 2 exercices (15–15 min) — `1SPE-GEOREP-EX-009..010`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C2` — « Je sais utiliser un vecteur normal à une droite, passer d'une équation cartésienne à un vecteur directeur/normal et réciproquement. »

Libelle BO : Utiliser un vecteur normal à une droite pour déterminer son équation.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 10 | `1SPE-GEOREP-CO-011..020` |
| cours | 2 | `1SPE-GEOREP-COURS-00`, `1SPE-GEOREP-CR-011` |
| evaluations | 2 | `1SPE-GEOREP-EV-A`, `1SPE-GEOREP-EV-B` |
| exercices | 10 | `1SPE-GEOREP-EX-011..020` |
| methodes | 1 | `1SPE-GEOREP-ME-002` |
| QCM | 3 | `Q4..6` |
| remediation | 1 | `1SPE-GEOREP-RE-C2` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 10.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-GEOREP-EV-A`, `1SPE-GEOREP-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (8–10 min) — `1SPE-GEOREP-EX-011..014`
- parcours 2 : 4 exercices (12–15 min) — `1SPE-GEOREP-EX-015..018`
- parcours 3 : 2 exercices (15–15 min) — `1SPE-GEOREP-EX-019..020`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C3` — « Je sais déterminer et exploiter l'équation d'un cercle (x-a)²+(y-b)²=r². »

Libelle BO : Déterminer une équation du cercle de centre (a,b) et de rayon r.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 10 | `1SPE-GEOREP-CO-021..030` |
| cours | 4 | `1SPE-GEOREP-COURS-00`, `1SPE-GEOREP-COURS-07-FR`, `1SPE-GEOREP-COURS-07-TC`, `1SPE-GEOREP-CR-012` |
| evaluations | 2 | `1SPE-GEOREP-EV-A`, `1SPE-GEOREP-EV-B` |
| exercices | 10 | `1SPE-GEOREP-EX-021..030` |
| methodes | 1 | `1SPE-GEOREP-ME-003` |
| QCM | 3 | `Q7..9` |
| remediation | 1 | `1SPE-GEOREP-RE-C3` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 10.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-GEOREP-EV-A`, `1SPE-GEOREP-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (8–12 min) — `1SPE-GEOREP-EX-021..024`
- parcours 2 : 4 exercices (12–15 min) — `1SPE-GEOREP-EX-025..028`
- parcours 3 : 2 exercices (15–15 min) — `1SPE-GEOREP-EX-029..030`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C4` — « Je sais étudier les positions relatives de droites et de cercles (parallélisme, intersection, tangence). »

Libelle BO : Étudier les positions relatives de droites et cercles (parallélisme, intersection, tangence).

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 10 | `1SPE-GEOREP-CO-031..040` |
| cours | 4 | `1SPE-GEOREP-COURS-00`, `1SPE-GEOREP-COURS-07-FR`, `1SPE-GEOREP-COURS-07-TC`, `1SPE-GEOREP-CR-013` |
| evaluations | 2 | `1SPE-GEOREP-EV-A`, `1SPE-GEOREP-EV-B` |
| exercices | 10 | `1SPE-GEOREP-EX-031..040` |
| methodes | 1 | `1SPE-GEOREP-ME-004` |
| QCM | 3 | `Q10..12` |
| remediation | 1 | `1SPE-GEOREP-RE-C4` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 10.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-GEOREP-EV-A`, `1SPE-GEOREP-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (10–12 min) — `1SPE-GEOREP-EX-031..034`
- parcours 2 : 4 exercices (15–15 min) — `1SPE-GEOREP-EX-035..038`
- parcours 3 : 2 exercices (20–20 min) — `1SPE-GEOREP-EX-039..040`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C5` — « Je sais résoudre des problèmes géométriques dans un repère orthonormé. »

Libelle BO : Résoudre des problèmes de géométrie plane dans un repère orthonormé.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 10 | `1SPE-GEOREP-CO-041..050` |
| cours | 4 | `1SPE-GEOREP-COURS-00`, `1SPE-GEOREP-COURS-07-FR`, `1SPE-GEOREP-COURS-07-TC`, `1SPE-GEOREP-CR-014` |
| evaluations | 2 | `1SPE-GEOREP-EV-A`, `1SPE-GEOREP-EV-B` |
| exercices | 10 | `1SPE-GEOREP-EX-041..050` |
| methodes | 1 | `1SPE-GEOREP-ME-005` |
| QCM | 3 | `Q13..15` |
| remediation | 1 | `1SPE-GEOREP-RE-C5` |

**Richesse declaree**

- type de capacite : `COMPOSITE_REASONING` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 10.
- gestes de raisonnement declares : `calcul`, `interpretation_geometrique`, `modelisation`, `raisonnement_par_coordonnees`, `raisonnement_vectoriel`, `synthese`.
- evaluee par : `1SPE-GEOREP-EV-A`, `1SPE-GEOREP-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 2 exercices (12–12 min) — `1SPE-GEOREP-EX-041..042`
- parcours 2 : 4 exercices (15–15 min) — `1SPE-GEOREP-EX-043..046`
- parcours 3 : 4 exercices (20–25 min) — `1SPE-GEOREP-EX-047..050`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

## 5. Question de QCM routee vers l'humain

Aucune question de ce chapitre n'est routee vers une revue humaine par `audit/QCM_INDEPENDENT_EVIDENCE_V2.json`.

## 6. Coherence du chapitre et coherence au niveau du manuel

- diversite des gestes de raisonnement au niveau du chapitre : `CANDIDATE_NON_SEMANTIC` (declaratif : `SUFFICIENT`).
- profil de diversite declare : calcul : 1 · interpretation_geometrique : 2 · modelisation : 1 · raisonnement_par_coordonnees : 6 · raisonnement_vectoriel : 2 · synthese : 1.
- capacites routees vers l'humain : 5 sur 5.
- attendus officiels obligatoires rattaches : 9 sur 9 ; manquants : 0 ; hors annee : 0.
- chapitres dont ce chapitre depend par ses prerequis : `1SPE-PRODUIT-SCALAIRE`, `1SPE-SECOND-DEGRE`, `2GT`. La coherence au niveau du manuel se juge avec eux.

La regle du depot : « la richesse se mesure en occasions distinctes et en gestes de raisonnement declares ; jamais en nombre de fichiers ».

## 7. Barème commenté — propositions à juger

La politique est fixée : pour chaque question évaluée, des POINTS, un ATTENDU ESSENTIEL, et un CRÉDIT PARTIEL seulement lorsqu'une décomposition objective le justifie. Le corrigé scientifique reste séparé et complet ; le barème ne le remplace pas.

Ces propositions sont **machine** et ne valent aucune approbation. Elles sont le contenu candidat que votre verdict de chapitre couvre.

### 1SPE-GEOREP-EV-A — **DÉCISION HUMAINE OBLIGATOIRE**

Le sujet ne value aucune question individuellement : répartir son total est un jugement pédagogique, et il vous revient. Le dossier complet — contraintes du sujet, geste de raisonnement, indicateurs observables, proposition et sa justification — est dans `audit/1SPE_ASSESSMENT_BAREME_TRANSCRIPTION.json`.

**Exercice 1** — 4 points (C1) · 4 question(s) en attente de jugement

- **Q1** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q2** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q3** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q4** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question

**Exercice 2** — 4 points (C2) · 3 question(s) en attente de jugement

- **Q1** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q2** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q3** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question

**Exercice 3** — 4 points (C3) · 4 question(s) en attente de jugement

- **Q1** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q2** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q3** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q4** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question

**Exercice 4** — 4 points (C4) · 3 question(s) en attente de jugement

- **Q1** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q2** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q3** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question

**Exercice 5** — 4 points (C5) · 3 question(s) en attente de jugement

- **Q1** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q2** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q3** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question

### 1SPE-GEOREP-EV-B — **DÉCISION HUMAINE OBLIGATOIRE**

Le sujet ne value aucune question individuellement : répartir son total est un jugement pédagogique, et il vous revient. Le dossier complet — contraintes du sujet, geste de raisonnement, indicateurs observables, proposition et sa justification — est dans `audit/1SPE_ASSESSMENT_BAREME_TRANSCRIPTION.json`.

**Exercice 1** — 4 points (C1) · 4 question(s) en attente de jugement

- **Q1** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q2** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q3** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q4** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question

**Exercice 2** — 4 points (C2) · 3 question(s) en attente de jugement

- **Q1** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q2** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q3** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question

**Exercice 3** — 4 points (C3) · 4 question(s) en attente de jugement

- **Q1** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q2** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q3** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q4** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question

**Exercice 4** — 4 points (C4) · 3 question(s) en attente de jugement

- **Q1** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q2** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q3** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question

**Exercice 5** — 4 points (C5) · 3 question(s) en attente de jugement

- **Q1** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q2** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question
- **Q3** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le sujet ne value pas cette question

Ce chapitre porte 34 question(s) évaluée(s), dont 34 attendent votre jugement. Ce ne sont pas autant de signatures : votre verdict porte sur le chapitre.

## 8. Recommandations d'une revue externe

Ces recommandations viennent d'une revue externe automatisee. Elles ne portent aucune identite humaine, ne valent aucun recu, et ne sont ecrites dans aucun corrige. Elles entrent dans le dossier de revue comme propositions, au meme titre que celles que la machine derive du sujet et du corrige.

Une recommandation qui ne retrouve pas sa question, dont la somme ne tombe pas sur le total declare, ou dont la valeur en points contredit le sujet, est refusee plutot qu'enregistree.

### Repartition de points proposee

*Les taches directes portent moins de poids que les constructions, les deductions, les systemes, les completions de carre ou le projete orthogonal.*

| Evaluation | Exercice | Question | Points |
| --- | ---: | --- | ---: |
| `1SPE-GEOREP-EV-A` | 1 | `Q1` | 1 pt |
| `1SPE-GEOREP-EV-A` | 1 | `Q2` | 1 pt |
| `1SPE-GEOREP-EV-A` | 1 | `Q3` | 1,5 pt |
| `1SPE-GEOREP-EV-A` | 1 | `Q4` | 0,5 pt |
| `1SPE-GEOREP-EV-A` | 2 | `Q1` | 1 pt |
| `1SPE-GEOREP-EV-A` | 2 | `Q2` | 2 pts |
| `1SPE-GEOREP-EV-A` | 2 | `Q3` | 1 pt |
| `1SPE-GEOREP-EV-A` | 3 | `Q1` | 1 pt |
| `1SPE-GEOREP-EV-A` | 3 | `Q2` | 0,5 pt |
| `1SPE-GEOREP-EV-A` | 3 | `Q3` | 0,5 pt |
| `1SPE-GEOREP-EV-A` | 3 | `Q4` | 2 pts |
| `1SPE-GEOREP-EV-A` | 4 | `Q1` | 1,5 pt |
| `1SPE-GEOREP-EV-A` | 4 | `Q2` | 0,5 pt |
| `1SPE-GEOREP-EV-A` | 4 | `Q3` | 2 pts |
| `1SPE-GEOREP-EV-A` | 5 | `Q1` | 1,5 pt |
| `1SPE-GEOREP-EV-A` | 5 | `Q2` | 1,5 pt |
| `1SPE-GEOREP-EV-A` | 5 | `Q3` | 1 pt |
| `1SPE-GEOREP-EV-B` | 1 | `Q1` | 1 pt |
| `1SPE-GEOREP-EV-B` | 1 | `Q2` | 1 pt |
| `1SPE-GEOREP-EV-B` | 1 | `Q3` | 1,5 pt |
| `1SPE-GEOREP-EV-B` | 1 | `Q4` | 0,5 pt |
| `1SPE-GEOREP-EV-B` | 2 | `Q1` | 1 pt |
| `1SPE-GEOREP-EV-B` | 2 | `Q2` | 2 pts |
| `1SPE-GEOREP-EV-B` | 2 | `Q3` | 1 pt |
| `1SPE-GEOREP-EV-B` | 3 | `Q1` | 1 pt |
| `1SPE-GEOREP-EV-B` | 3 | `Q2` | 0,5 pt |
| `1SPE-GEOREP-EV-B` | 3 | `Q3` | 0,5 pt |
| `1SPE-GEOREP-EV-B` | 3 | `Q4` | 2 pts |
| `1SPE-GEOREP-EV-B` | 4 | `Q1` | 1,5 pt |
| `1SPE-GEOREP-EV-B` | 4 | `Q2` | 0,5 pt |
| `1SPE-GEOREP-EV-B` | 4 | `Q3` | 2 pts |
| `1SPE-GEOREP-EV-B` | 5 | `Q1` | 1,5 pt |
| `1SPE-GEOREP-EV-B` | 5 | `Q2` | 1,5 pt |
| `1SPE-GEOREP-EV-B` | 5 | `Q3` | 1 pt |

## 9. Checklist du role `EXPERT_PROGRAMME_PEDAGOGIE`

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

## 10. Reference de lecture : le PDF candidat

Le PDF sert a lire le chapitre dans l'ordre ou l'eleve le recevra. Il n'est pas une preuve : le packet ne porte aucune preuve de rendu (`render_evidence = ABSENT`), et aucun index page-objet n'est etabli.

| Fichier | Variante | Pages | Role declare | Etat declare |
| --- | --- | --- | --- | --- |
| `MANUELS_PDF_PUBLICATION/01_Maths_1re_Spe_Eleve.pdf` | eleve | 371 | HISTORICAL_PUBLICATION_SNAPSHOT | STALE_UNDECIDED |
| `MANUELS_PDF_PUBLICATION/02_Maths_1re_Spe_Professeur.pdf` | professeur | 617 | HISTORICAL_PUBLICATION_SNAPSHOT | STALE_UNDECIDED |

Ces instantanes sont declares `STALE_UNDECIDED` dans `audit/PDF_ARTIFACT_REGISTRY.yaml` : ils ne sont pas garantis identiques au contenu courant. Le candidat d'impression courant se reconstruit par `python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py --manual 1SPE --variant <variant> --record-observed` (recu : `audit/1SPE_PRINT_CANDIDATE_BUILD_RECEIPT.json`, statut `PRINT_CANDIDATE`).

Rappel du recu : Ces PDF ne sont pas finals : aucun 1SPE_FINAL_CONTENT_SHA n'est figé, les deux revues humaines par chapitre et le dossier D7 restent en attente.

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-GEOMETRIE-REPEREE/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-GEOMETRIE-REPEREE/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
