# Vue de lecture — Trigonométrie — EXPERT_PROGRAMME_PEDAGOGIE

Chapitre `1SPE-TRIGONOMETRIE` · manuel `1SPE` (Première, Spécialité mathématiques) · packet B · role `EXPERT_PROGRAMME_PEDAGOGIE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-TRIGONOMETRIE/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`
> Etat de revue : `audit/reviews/human/1SPE-TRIGONOMETRIE/REVIEW_STATE.json`
> Producteur de cette vue : `scripts/build_human_review_reading_views.py`
>
> Toute divergence entre cette vue et le packet se tranche en faveur du packet. Cette vue ne cree, ne ferme et ne reduit aucune obligation.

## 1. Ce que vous decidez

- L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.
- Aucun humain n'a encore approuve ce chapitre : REVIEW_DELTA_BASELINE = NONE. Le perimetre de revue est le CHAPITRE COURANT ENTIER. Les listes ci-dessous dirigent l'attention, elles ne reduisent pas le perimetre.
- CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST (`sha256:590269373f7f0589819979a8639273f402b32de7d0d4dda4ac6328d1ee2fb243`) ; l'approbation graphique releve de la porte D7, independante.
- Verdicts autorises, a rendre dans le packet JSON canonique et jamais dans cette vue : `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`.
- Cette vue ne porte aucune decision et ne nomme personne : l'assignation du role reste `PENDING_UNASSIGNED`, l'etat du packet reste `PENDING_UNASSIGNED`.

| Perimetre | Valeur |
| --- | --- |
| Objets du chapitre dans le packet | 78 |
| Empreinte de l'ensemble d'objets | `sha256:b4679995be20574bd17f70368d5afe83fab601caca60bda18c05da8f40eb5fa3` |
| Empreinte semantique liee a l'approbation | `sha256:590269373f7f0589819979a8639273f402b32de7d0d4dda4ac6328d1ee2fb243` |
| Empreinte du packet | `sha256:9f11013f2cf2028ac58cf766a7a1a554c940b3063af73dd9ae3d61ac93a93d4e` |
| Revision du depot gelee dans le packet | `5bc44275a0afe33f10b7ce2ec7700778f8de6308` |
| Preuve de rendu portee par le packet | `ABSENT` |

## 2. Le chapitre et ses capacites du programme officiel

**Trigonométrie** — programme applicable 2026-2027, MENE2602917A, BO n° 14 du 2026-04-02.
Source officielle : https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A

Situation d'accroche declaree : Une grande roue de fete foraine a un rayon de 25 metres et son centre est a 27 metres du sol. A quelle hauteur se trouve un passager apres un tour d'un sixieme du cercle ? Le radian et la lecture du cercle trigonometrique permettent de repondre.

Temps estime declare : parcours 1 : 6 h · parcours 2 : 5 h · parcours 3 : 4 h.

| Code | Libelle eleve | Libelle BO | Demonstration exigible |
| --- | --- | --- | --- |
| `C1` | Je sais placer un angle oriente sur le cercle trigonometrique et convertir degres/radians. | Connaître le cercle trigonométrique, la mesure en radian, les angles orientés. | non |
| `C2` | Je sais determiner les cosinus et sinus de valeurs remarquables et d'angles associes par lecture du cercle trigonometrique. | Connaître et utiliser cos et sin (relation fondamentale, valeurs remarquables, symétries). | non |

**Attendus officiels rattaches, capacite par capacite**

- `C1` — 3 attendus :
    - `1SPE-OFFICIAL-120` (MANDATORY_KNOWLEDGE, Trigonométrie) : Cercle trigonométrique. Longueur d’arc. Radian.
    - `1SPE-OFFICIAL-121` (MANDATORY_KNOWLEDGE, Trigonométrie) : Enroulement de la droite sur le cercle trigonométrique. Image d’un nombre réel.
    - `1SPE-OFFICIAL-123` (MANDATORY_CAPACITY, Trigonométrie) : Placer un point sur le cercle trigonométrique.
- `C2` — 3 attendus :
    - `1SPE-OFFICIAL-122` (MANDATORY_KNOWLEDGE, Trigonométrie) : Cosinus et sinus d’un nombre réel. Lien avec le sinus et le cosinus dans un triangle rectangle. Valeurs remarquables.
    - `1SPE-OFFICIAL-124` (MANDATORY_CAPACITY, Trigonométrie) : Par lecture du cercle trigonométrique, déterminer, pour des valeurs remarquables de 𝑥, les cosinus et sinus d’angles associés à 𝑥.
    - `1SPE-OFFICIAL-125` (MANDATORY_SKILL, Trigonométrie) : Calcul de cos , sin , cos , sin . 4 4 3 3

**Prerequis declares par le contrat du chapitre**

| Code | Libelle | Chapitre d'origine |
| --- | --- | --- |
| `R1` | Theoreme de Pythagore | 2GT |
| `R2` | Reperage dans le plan : coordonnees, distance | 2GT |

## 3. Structure reelle et ordre d'assemblage courant

L'ordre ci-dessous n'est pas l'ordre alphabetique des repertoires : il est lu chez l'assembleur du manuel (`Mathematiques/manuel-maths/scripts/assemble_manuel.py`, `collect_chapter`). C'est la sequence que le lecteur du PDF recoit.

| Rang | Rubrique imprimee | Objets (professeur) |
| --- | --- | --- |
| 1 | Cours | 2 |
| 2 | Méthodes | 5 |
| 3 | Exercices | 36 |
| 4 | TD | 2 |
| 5 | Auto-évaluation | 1 |
| 6 | Évaluation | 4 |
| 7 | Remédiation | 4 |
| 8 | Corrigés | 24 |

Total assemble : 78 objets en variante professeur, 52 en variante eleve (la variante eleve exclut les corriges et les corriges d'evaluation).

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

`audit/SEMANTIC_ALIGNMENT_LEDGER.json` decoupe le manuel en cellules capacite x role pedagogique. Ce chapitre en porte 14. Elles sont regroupees ici par capacite : une checklist cellule par cellule ne se lit pas.

**Pourquoi ces cellules arrivent chez vous.** Seul le META rattache les corps a une capacite ; l'identite declaree est resolue par egalite exacte, et la couverture de reponses n'etablit qu'une COUVERTURE. Etablir qu'un corps SERT la capacite est un jugement pedagogique, pas un calcul : c'est un resultat terminal, pas une lacune de mesure. C'est pourquoi chaque cellule de ce chapitre est routee vers vous.

Chaque capacite rappelle ensuite ce qui lui est propre : le nombre de cellules, leur disposition, les preuves eventuellement attachees et l'etat de sa richesse.

### Capacite `C1` — « Je sais placer un angle oriente sur le cercle trigonometrique et convertir degres/radians. »

Libelle BO : Connaître le cercle trigonométrique, la mesure en radian, les angles orientés.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 12 | `1SPE-TRIGO-CO-001..010`, `1SPE-TRIGO-CO-021..022` |
| cours | 1 | `1SPE-TRIGO-CR-010` |
| evaluations | 2 | `1SPE-TRIGO-EV-A`, `1SPE-TRIGO-EV-B` |
| exercices | 12 | `1SPE-TRIGO-EX-001..010`, `1SPE-TRIGO-EX-021..022` |
| methodes | 1 | `1SPE-TRIGO-ME-001` |
| QCM | 8 | `Q1..3`, `Q7..9`, `Q10`, `Q15` |
| remediation | 1 | `1SPE-TRIGO-RE-C1` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 8 · remediation : 1 · targeted_practice : 14.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-TRIGO-EV-A`, `1SPE-TRIGO-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 8 exercices (5–10 min) — `1SPE-TRIGO-EX-001..004`, `1SPE-TRIGO-EX-021..022`, `1SPE-TRIGO-EX-021..022-CDP`
- parcours 2 : 3 exercices (10–12 min) — `1SPE-TRIGO-EX-005..007`
- parcours 3 : 3 exercices (12–15 min) — `1SPE-TRIGO-EX-008..010`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C2` — « Je sais determiner les cosinus et sinus de valeurs remarquables et d'angles associes par lecture du cercle trigonometrique. »

Libelle BO : Connaître et utiliser cos et sin (relation fondamentale, valeurs remarquables, symétries).

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 10 | `1SPE-TRIGO-CO-011..018`, `1SPE-TRIGO-CO-020`, `1SPE-TRIGO-CO-023` |
| cours | 1 | `1SPE-TRIGO-CR-011` |
| evaluations | 2 | `1SPE-TRIGO-EV-A`, `1SPE-TRIGO-EV-B` |
| exercices | 10 | `1SPE-TRIGO-EX-011..018`, `1SPE-TRIGO-EX-020`, `1SPE-TRIGO-EX-023` |
| methodes | 1 | `1SPE-TRIGO-ME-002` |
| QCM | 7 | `Q4..6`, `Q11..14` |
| remediation | 1 | `1SPE-TRIGO-RE-C2` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 7 · remediation : 1 · targeted_practice : 11.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-TRIGO-EV-A`, `1SPE-TRIGO-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (8–10 min) — `1SPE-TRIGO-EX-011..014`
- parcours 2 : 5 exercices (5–12 min) — `1SPE-TRIGO-EX-015..017`, `1SPE-TRIGO-EX-023`, `1SPE-TRIGO-EX-023-CDP`
- parcours 3 : 2 exercices (15–15 min) — `1SPE-TRIGO-EX-018`, `1SPE-TRIGO-EX-020`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

## 5. Question de QCM routee vers l'humain

Aucune question de ce chapitre n'est routee vers une revue humaine par `audit/QCM_INDEPENDENT_EVIDENCE_V2.json`.

## 6. Coherence du chapitre et coherence au niveau du manuel

- diversite des gestes de raisonnement au niveau du chapitre : `INSUFFICIENT` (declaratif : `INSUFFICIENT`).
- aucun profil de diversite declare pour ce chapitre : les gestes de raisonnement ne sont pas mesures, ils restent a juger.
- capacites routees vers l'humain : 2 sur 2.
- attendus officiels obligatoires rattaches : 6 sur 6 ; manquants : 0 ; hors annee : 0.
- chapitres dont ce chapitre depend par ses prerequis : `2GT`. La coherence au niveau du manuel se juge avec eux.

La regle du depot : « la richesse se mesure en occasions distinctes et en gestes de raisonnement declares ; jamais en nombre de fichiers ».

## 7. Barème commenté — propositions à juger

La politique est fixée : pour chaque question évaluée, des POINTS, un ATTENDU ESSENTIEL, et un CRÉDIT PARTIEL seulement lorsqu'une décomposition objective le justifie. Le corrigé scientifique reste séparé et complet ; le barème ne le remplace pas.

Ces propositions sont **machine** et ne valent aucune approbation. Elles sont le contenu candidat que votre verdict de chapitre couvre.

### 1SPE-TRIGO-EV-A

**Exercice 1** — 4 points (C1)

- **Q1** — 1 pt — Attendu : convertir — $225° = 225 \times \dfrac{\pi}{180} = \dfrac{5\pi}{4}$.
- **Q2** — 1 pt — Attendu : convertir — $\dfrac{7\pi}{6} = \dfrac{7\pi}{6} \times \dfrac{180}{\pi} = 210°$.
- **Q3** — 1 pt — Attendu : déterminer — Mesure principale : $\dfrac{3\pi}{4}$.
- **Q4** — 1 pt — Attendu : donner — Coordonnées : $\left(-\dfrac{1}{2}\,;\,-\dfrac{\sqrt{3}}{2}\right)$.

**Exercice 2** — 4 points (C2)

- **Q1** — 1,5 pt — Attendu : donner — $\dfrac{5\pi}{6} = \pi - \dfrac{\pi}{6}$ : $\cos\dfrac{5\pi}{6} = -\cos\dfrac{\pi}{6} = -\dfrac{\sqrt{3}}{2}$, \quad $\sin\dfrac{5\pi}{6} = \sin\dfrac{\pi}{6} = \dfrac{1}{2}$.
- **Q2** — 1 pt — Attendu : donner — $\dfrac{7\pi}{4} = 2\pi - \dfrac{\pi}{4} = -\dfrac{\pi}{4} + 2\pi$ : $\sin\dfrac{7\pi}{4} = -\sin\dfrac{\pi}{4} = -\dfrac{\sqrt{2}}{2}$.
- **Q3** — 1,5 pt — Attendu : calculer — Comme $x \in \left]\dfrac{\pi}{2};\pi\right[$, $\sin x > 0$, donc $\sin x = \dfrac{4}{5}$.

**Exercice 3** — 4 points (C1) · 1 question(s) en attente de jugement

- **Q1** — 2 pts — Attendu : calculer — Avec $s=r\theta$, $s=12\times\dfrac{5\pi}{6}=\boxed{10\pi\ \text{cm}}$.
- **Q2** — 1 pt — Attendu : donner — $\theta=\dfrac{s}{r}=\dfrac{9}{6}=\boxed{\dfrac32\ \text{rad}}$.
- **Q3** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le geste évalué ne se lit pas dans l'énoncé

**Exercice 4** — 4 points (C2)

- **Q1** — 1,5 pt — Attendu : donner — Le point image de $-\dfrac{\pi}{3}$ a pour coordonnées $\boxed{\left(\dfrac12;-\dfrac{\sqrt3}{2}\right)}$.
- **Q2** — 1,5 pt — Attendu : donner — Le point image de $\dfrac{3\pi}{4}$ a pour coordonnées $\boxed{\left(-\dfrac{\sqrt2}{2};\dfrac{\sqrt2}{2}\right)}$.
- **Q3** — 1 pt — Attendu : justifier — Oui : les coordonnées lues sur le cercle a l'angle $3\pi/4$ sont exactement celles de $M$.

**Exercice 5** — 4 points (C1, C2) · 1 question(s) en attente de jugement

- **Q1** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le geste évalué ne se lit pas dans l'énoncé
- **Q2** — 1 pt — Attendu : donner — Le point associe a $\pi/3$ a pour coordonnées $\boxed{\left(\dfrac12;\dfrac{\sqrt3}{2}\right)}$.
- **Q3** — 1,5 pt — Attendu : en déduire — La hauteur est l'altitude du centre augmentee de l'ordonnée sur la roue : $\boxed{27+\dfrac{25\sqrt3}{2}\ \text{m}}$.
- **Q4** — 0,5 pt — Attendu : donner — $27+\dfrac{25\sqrt3}{2}\approx\boxed{48{,}7\ \text{m}}$.

### 1SPE-TRIGO-EV-B

**Exercice 1** — 4 points (C1)

- **Q1** — 1 pt — Attendu : convertir — $315° = 315 \times \dfrac{\pi}{180} = \dfrac{7\pi}{4}$.
- **Q2** — 1 pt — Attendu : convertir — $\dfrac{5\pi}{3} = \dfrac{5\pi}{3} \times \dfrac{180}{\pi} = 300°$.
- **Q3** — 1 pt — Attendu : déterminer — Mesure principale : $-\dfrac{\pi}{6}$.
- **Q4** — 1 pt — Attendu : donner — Coordonnées : $\left(-\dfrac{\sqrt{2}}{2}\,;\,\dfrac{\sqrt{2}}{2}\right)$.

**Exercice 2** — 4 points (C2)

- **Q1** — 1,5 pt — Attendu : donner — $\dfrac{4\pi}{3} = \pi + \dfrac{\pi}{3}$ : $\cos\dfrac{4\pi}{3} = -\cos\dfrac{\pi}{3} = -\dfrac{1}{2}$, \quad $\sin\dfrac{4\pi}{3} = -\sin\dfrac{\pi}{3} = -\dfrac{\sqrt{3}}{2}$.
- **Q2** — 1 pt — Attendu : donner — $\dfrac{11\pi}{6} = 2\pi - \dfrac{\pi}{6}$ : $\cos\dfrac{11\pi}{6} = \cos\dfrac{\pi}{6} = \dfrac{\sqrt{3}}{2}$.
- **Q3** — 1,5 pt — Attendu : calculer — Comme $x \in \left]0;\dfrac{\pi}{2}\right[$, $\cos x > 0$, donc $\cos x = \dfrac{12}{13}$.

**Exercice 3** — 4 points (C1) · 1 question(s) en attente de jugement

- **Q1** — 2 pts — Attendu : calculer — Avec $s=r\theta$, $s=8\times\dfrac{3\pi}{4}=\boxed{6\pi\ \text{cm}}$.
- **Q2** — 1 pt — Attendu : donner — $\theta=\dfrac{s}{r}=\dfrac74=\boxed{\dfrac74\ \text{rad}}$.
- **Q3** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le geste évalué ne se lit pas dans l'énoncé

**Exercice 4** — 4 points (C2)

- **Q1** — 1,5 pt — Attendu : donner — Le point image de $\dfrac{4\pi}{3}$ a pour coordonnées $\boxed{\left(-\dfrac12;-\dfrac{\sqrt3}{2}\right)}$.
- **Q2** — 1,5 pt — Attendu : donner — Le point image de $\dfrac{7\pi}{4}$ a pour coordonnées $\boxed{\left(\dfrac{\sqrt2}{2};-\dfrac{\sqrt2}{2}\right)}$.
- **Q3** — 1 pt — Attendu : justifier — Oui : la lecture du cercle a l'angle $5\pi/6$ donne exactement les coordonnées de $N$.

**Exercice 5** — 4 points (C1, C2) · 1 question(s) en attente de jugement

- **Q1** — `JUGEMENT PÉDAGOGIQUE REQUIS` : le geste évalué ne se lit pas dans l'énoncé
- **Q2** — 1 pt — Attendu : donner — Le point associe a $3\pi/4$ a pour coordonnées $\boxed{\left(-\dfrac{\sqrt2}{2};\dfrac{\sqrt2}{2}\right)}$.
- **Q3** — 1,5 pt — Attendu : en déduire — La hauteur est $\boxed{20+18\times\dfrac{\sqrt2}{2}=20+9\sqrt2\ \text{m}}$.
- **Q4** — 0,5 pt — Attendu : donner — $20+9\sqrt2\approx\boxed{32{,}7\ \text{m}}$.

Ce chapitre porte 34 question(s) évaluée(s), dont 4 attendent votre jugement. Ce ne sont pas autant de signatures : votre verdict porte sur le chapitre.

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

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-TRIGONOMETRIE/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-TRIGONOMETRIE/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
