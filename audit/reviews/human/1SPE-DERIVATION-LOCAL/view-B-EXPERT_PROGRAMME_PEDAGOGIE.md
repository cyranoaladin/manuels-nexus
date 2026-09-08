# Vue de lecture — Dérivation : point de vue local — EXPERT_PROGRAMME_PEDAGOGIE

Chapitre `1SPE-DERIVATION-LOCAL` · manuel `1SPE` (Première, Spécialité mathématiques) · packet B · role `EXPERT_PROGRAMME_PEDAGOGIE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-DERIVATION-LOCAL/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`
> Etat de revue : `audit/reviews/human/1SPE-DERIVATION-LOCAL/REVIEW_STATE.json`
> Producteur de cette vue : `scripts/build_human_review_reading_views.py`
>
> Toute divergence entre cette vue et le packet se tranche en faveur du packet. Cette vue ne cree, ne ferme et ne reduit aucune obligation.

## 1. Ce que vous decidez

- L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.
- Aucun humain n'a encore approuve ce chapitre : REVIEW_DELTA_BASELINE = NONE. Le perimetre de revue est le CHAPITRE COURANT ENTIER. Les listes ci-dessous dirigent l'attention, elles ne reduisent pas le perimetre.
- CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST (`sha256:854b4e1dda5f894278dbd584ffd99da653a9217105a6dc35ca4ced1e0fb0c681`) ; l'approbation graphique releve de la porte D7, independante.
- Verdicts autorises, a rendre dans le packet JSON canonique et jamais dans cette vue : `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`.
- Cette vue ne porte aucune decision et ne nomme personne : l'assignation du role reste `PENDING_UNASSIGNED`, l'etat du packet reste `PENDING_UNASSIGNED`.

| Perimetre | Valeur |
| --- | --- |
| Objets du chapitre dans le packet | 145 |
| Empreinte de l'ensemble d'objets | `sha256:66ee703b23338630536567639b52f69a2e9be842f10d4ec633f8e9903747680d` |
| Empreinte semantique liee a l'approbation | `sha256:854b4e1dda5f894278dbd584ffd99da653a9217105a6dc35ca4ced1e0fb0c681` |
| Empreinte du packet | `sha256:87343ff9f64e47f1030e8072d611a9ccc908a0927d8ccf71eb5daa7c85b4026f` |
| Revision du depot gelee dans le packet | `dfc99058e7a7c16ae4af46b99245edbe14b4f8e5` |
| Preuve de rendu portee par le packet | `ABSENT` |

## 2. Le chapitre et ses capacites du programme officiel

**Dérivation : point de vue local** — programme applicable 2026-2027, MENE2602917A, BO n° 14 du 2026-04-02.
Source officielle : https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A

Situation d'accroche declaree : Un vélo équipé d'un capteur fournit la distance parcourue en fonction du temps. Comment déterminer sa vitesse exacte à l'instant t = 12 s, alors que les mesures disponibles donnent seulement des vitesses moyennes sur de courts intervalles ?

Temps estime declare : parcours 1 : 10 h · parcours 2 : 8 h · parcours 3 : 7 h.

| Code | Libelle eleve | Libelle BO | Demonstration exigible |
| --- | --- | --- | --- |
| `C1` | Je sais calculer et interpréter un taux de variation et la pente d'une sécante. | Calculer un taux de variation, la pente d'une sécante. | non |
| `C2` | Je sais interpréter un nombre dérivé comme une pente ou une vitesse instantanée. | Interpréter le nombre dérivé en contexte : pente d'une tangente, vitesse instantanée, coût marginal, etc. | non |
| `C3` | Je sais lire un nombre dérivé sur un graphique et construire la tangente correspondante. | Déterminer graphiquement un nombre dérivé par la pente de la tangente. Construire la tangente en un point à une courbe représentative connaissant le nombre dérivé. | non |
| `C4` | Je sais écrire l'équation d'une tangente à partir de l'abscisse, de l'image et du nombre dérivé. | Déterminer l'équation de la tangente en un point à la courbe représentative d'une fonction. | oui — Équation de la tangente en un point à une courbe représentative. |
| `C5` | Je sais approcher f(a+h) avec l'approximation linéaire au voisinage de a. | Calculer une valeur approchée de f(a+h). | non |

**Attendus officiels rattaches, capacite par capacite**

- `C1` — 2 attendus :
    - `1SPE-OFFICIAL-080` (MANDATORY_KNOWLEDGE, Dérivation — point de vue local) : Taux de variation. Sécantes à la courbe représentative d’une fonction en un point donné.
    - `1SPE-OFFICIAL-089` (MANDATORY_CAPACITY, Point de vue global) : Calculer un taux de variation, la pente d’une sécante.
- `C2` — 2 attendus :
    - `1SPE-OFFICIAL-081` (MANDATORY_KNOWLEDGE, Dérivation — point de vue local) : Nombre dérivé d’une fonction en un point, comme limite du taux de variation. Notation ƒ ’(a).
    - `1SPE-OFFICIAL-090` (MANDATORY_CAPACITY, Point de vue global) : Interpréter le nombre dérivé en contexte : pente d’une tangente, vitesse instantanée, cout marginal, etc.
- `C3` — 2 attendus :
    - `1SPE-OFFICIAL-082` (MANDATORY_KNOWLEDGE, Dérivation — point de vue local) : Tangente à la courbe représentative d’une fonction en un point, comme « limite des sécantes ». Pente. Équation : la tangente à la courbe représentative de ƒ au point d’abscisse a est la droite d’équation 𝑦 = ƒ (a) + ƒ ‘(a)(𝑥 – a).
    - `1SPE-OFFICIAL-091` (MANDATORY_CAPACITY, Point de vue global) : Déterminer graphiquement un nombre dérivé par la pente de la tangente. Construire la tangente en un point à une courbe représentative connaissant le nombre dérivé.
- `C4` — 2 attendus :
    - `1SPE-OFFICIAL-092` (MANDATORY_CAPACITY, Point de vue global) : Déterminer l’équation de la tangente en un point à la courbe représentative d’une fonction.
    - `1SPE-OFFICIAL-095` (MANDATORY_SKILL, Point de vue global) : Équation de la tangente en un point à une courbe représentative.
- `C5` — 2 attendus :
    - `1SPE-OFFICIAL-083` (MANDATORY_KNOWLEDGE, Dérivation — point de vue local) : Approximation linéaire : fonction affine tangente 𝑥 ↦ ƒ (a) + ƒ ‘(a)(𝑥 – a) et approximation de ƒ (a + h) par ƒ (a) + ƒ ‘(a)h.
    - `1SPE-OFFICIAL-093` (MANDATORY_CAPACITY, Point de vue global) : Calculer une valeur approchée de ƒ (a + h).

**Prerequis declares par le contrat du chapitre**

| Code | Libelle | Chapitre d'origine |
| --- | --- | --- |
| `R1` | Calculer une image et lire une image sur une courbe | 2GT |
| `R2` | Calcul littéral : développer, factoriser et simplifier une fraction | 2GT |
| `R3` | Coefficient directeur et équation d'une droite | 2GT |
| `R4` | Fonctions carré et inverse | 2GT |
| `R5` | Calculer une vitesse moyenne à partir d'une distance et d'une durée | 2GT |

## 3. Structure reelle et ordre d'assemblage courant

L'ordre ci-dessous n'est pas l'ordre alphabetique des repertoires : il est lu chez l'assembleur du manuel (`Mathematiques/manuel-maths/scripts/assemble_manuel.py`, `collect_chapter`). C'est la sequence que le lecteur du PDF recoit.

| Rang | Rubrique imprimee | Objets (professeur) |
| --- | --- | --- |
| 1 | Cours | 5 |
| 2 | Méthodes | 5 |
| 3 | Exercices | 68 |
| 4 | TD | 2 |
| 5 | Auto-évaluation | 1 |
| 6 | Évaluation | 4 |
| 7 | Remédiation | 10 |
| 8 | Corrigés | 50 |

Total assemble : 145 objets en variante professeur, 93 en variante eleve (la variante eleve exclut les corriges et les corriges d'evaluation).

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

### Capacite `C1` — « Je sais calculer et interpréter un taux de variation et la pente d'une sécante. »

Libelle BO : Calculer un taux de variation, la pente d'une sécante.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 12 | `1SPE-DERLOCAL-CO-001..006`, `1SPE-DERLOCAL-CO-031..032`, `1SPE-DERLOCAL-CO-039..040`, `1SPE-DERLOCAL-CO-047`, `1SPE-DERLOCAL-CO-049` |
| cours | 1 | `1SPE-DERIVATION-LOCAL-CR-010` |
| evaluations | 2 | `1SPE-DERLOCAL-EV-A`, `1SPE-DERLOCAL-EV-B` |
| exercices | 12 | `1SPE-DERLOCAL-EX-001..006`, `1SPE-DERLOCAL-EX-031..032`, `1SPE-DERLOCAL-EX-039..040`, `1SPE-DERLOCAL-EX-047`, `1SPE-DERLOCAL-EX-049` |
| methodes | 1 | `1SPE-DERLOCAL-ME-001` |
| QCM | 3 | `Q1..3` |
| remediation | 1 | `1SPE-DERIVATION-LOCAL-RE-C1` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 11.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-DERLOCAL-EV-A`, `1SPE-DERLOCAL-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (5–8 min) — `1SPE-DERLOCAL-EX-001..002`, `1SPE-DERLOCAL-EX-031..032`
- parcours 2 : 4 exercices (12–15 min) — `1SPE-DERLOCAL-EX-003..004`, `1SPE-DERLOCAL-EX-039..040`
- parcours 3 : 3 exercices (15–20 min) — `1SPE-DERLOCAL-EX-005..006`, `1SPE-DERLOCAL-EX-047`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C2` — « Je sais interpréter un nombre dérivé comme une pente ou une vitesse instantanée. »

Libelle BO : Interpréter le nombre dérivé en contexte : pente d'une tangente, vitesse instantanée, coût marginal, etc.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 13 | `1SPE-DERLOCAL-CO-007..012`, `1SPE-DERLOCAL-CO-033..034`, `1SPE-DERLOCAL-CO-041..042`, `1SPE-DERLOCAL-CO-047..048`, `1SPE-DERLOCAL-CO-050` |
| cours | 1 | `1SPE-DERIVATION-LOCAL-CR-011` |
| evaluations | 2 | `1SPE-DERLOCAL-EV-A`, `1SPE-DERLOCAL-EV-B` |
| exercices | 13 | `1SPE-DERLOCAL-EX-007..012`, `1SPE-DERLOCAL-EX-033..034`, `1SPE-DERLOCAL-EX-041..042`, `1SPE-DERLOCAL-EX-047..048`, `1SPE-DERLOCAL-EX-050` |
| methodes | 1 | `1SPE-DERLOCAL-ME-002` |
| QCM | 3 | `Q4..6` |
| remediation | 1 | `1SPE-DERIVATION-LOCAL-RE-C2` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 13.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-DERLOCAL-EV-A`, `1SPE-DERLOCAL-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (5–8 min) — `1SPE-DERLOCAL-EX-007..008`, `1SPE-DERLOCAL-EX-033..034`
- parcours 2 : 4 exercices (12–15 min) — `1SPE-DERLOCAL-EX-009..010`, `1SPE-DERLOCAL-EX-041..042`
- parcours 3 : 5 exercices (20–20 min) — `1SPE-DERLOCAL-EX-011..012`, `1SPE-DERLOCAL-EX-047..048`, `1SPE-DERLOCAL-EX-050`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C3` — « Je sais lire un nombre dérivé sur un graphique et construire la tangente correspondante. »

Libelle BO : Déterminer graphiquement un nombre dérivé par la pente de la tangente. Construire la tangente en un point à une courbe représentative connaissant le nombre dérivé.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 11 | `1SPE-DERLOCAL-CO-013..018`, `1SPE-DERLOCAL-CO-035..036`, `1SPE-DERLOCAL-CO-043`, `1SPE-DERLOCAL-CO-048`, `1SPE-DERLOCAL-CO-050` |
| cours | 1 | `1SPE-DERIVATION-LOCAL-CR-012` |
| evaluations | 2 | `1SPE-DERLOCAL-EV-A`, `1SPE-DERLOCAL-EV-B` |
| exercices | 11 | `1SPE-DERLOCAL-EX-013..018`, `1SPE-DERLOCAL-EX-035..036`, `1SPE-DERLOCAL-EX-043`, `1SPE-DERLOCAL-EX-048`, `1SPE-DERLOCAL-EX-050` |
| methodes | 1 | `1SPE-DERLOCAL-ME-003` |
| QCM | 3 | `Q7..9` |
| remediation | 1 | `1SPE-DERIVATION-LOCAL-RE-C3` |

**Richesse declaree**

- type de capacite : `ATOMIC_SUPPORT` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 11.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-DERLOCAL-EV-A`, `1SPE-DERLOCAL-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (5–8 min) — `1SPE-DERLOCAL-EX-013..014`, `1SPE-DERLOCAL-EX-035..036`
- parcours 2 : 3 exercices (12–15 min) — `1SPE-DERLOCAL-EX-015..016`, `1SPE-DERLOCAL-EX-043`
- parcours 3 : 4 exercices (20–20 min) — `1SPE-DERLOCAL-EX-017..018`, `1SPE-DERLOCAL-EX-048`, `1SPE-DERLOCAL-EX-050`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C4` — « Je sais écrire l'équation d'une tangente à partir de l'abscisse, de l'image et du nombre dérivé. »

Libelle BO : Déterminer l'équation de la tangente en un point à la courbe représentative d'une fonction.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 11 | `1SPE-DERLOCAL-CO-019..024`, `1SPE-DERLOCAL-CO-037`, `1SPE-DERLOCAL-CO-044`, `1SPE-DERLOCAL-CO-047`, `1SPE-DERLOCAL-CO-049..050` |
| cours | 1 | `1SPE-DERIVATION-LOCAL-CR-013` |
| evaluations | 2 | `1SPE-DERLOCAL-EV-A`, `1SPE-DERLOCAL-EV-B` |
| exercices | 11 | `1SPE-DERLOCAL-EX-019..024`, `1SPE-DERLOCAL-EX-037`, `1SPE-DERLOCAL-EX-044`, `1SPE-DERLOCAL-EX-047`, `1SPE-DERLOCAL-EX-049..050` |
| methodes | 1 | `1SPE-DERLOCAL-ME-004` |
| QCM | 3 | `Q10..12` |
| remediation | 1 | `1SPE-DERIVATION-LOCAL-RE-C4` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 11.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-DERLOCAL-EV-A`, `1SPE-DERLOCAL-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 3 exercices (5–8 min) — `1SPE-DERLOCAL-EX-019..020`, `1SPE-DERLOCAL-EX-037`
- parcours 2 : 3 exercices (12–15 min) — `1SPE-DERLOCAL-EX-021..022`, `1SPE-DERLOCAL-EX-044`
- parcours 3 : 5 exercices (20–25 min) — `1SPE-DERLOCAL-EX-023..024`, `1SPE-DERLOCAL-EX-047`, `1SPE-DERLOCAL-EX-049..050`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C5` — « Je sais approcher f(a+h) avec l'approximation linéaire au voisinage de a. »

Libelle BO : Calculer une valeur approchée de f(a+h).

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 11 | `1SPE-DERLOCAL-CO-025..030`, `1SPE-DERLOCAL-CO-038`, `1SPE-DERLOCAL-CO-045..046`, `1SPE-DERLOCAL-CO-048..049` |
| cours | 1 | `1SPE-DERIVATION-LOCAL-CR-014` |
| evaluations | 2 | `1SPE-DERLOCAL-EV-A`, `1SPE-DERLOCAL-EV-B` |
| exercices | 11 | `1SPE-DERLOCAL-EX-025..030`, `1SPE-DERLOCAL-EX-038`, `1SPE-DERLOCAL-EX-045..046`, `1SPE-DERLOCAL-EX-048..049` |
| methodes | 1 | `1SPE-DERLOCAL-ME-005` |
| QCM | 3 | `Q13..15` |
| remediation | 1 | `1SPE-DERIVATION-LOCAL-RE-C5` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 10.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-DERLOCAL-EV-A`, `1SPE-DERLOCAL-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 3 exercices (5–8 min) — `1SPE-DERLOCAL-EX-025..026`, `1SPE-DERLOCAL-EX-038`
- parcours 2 : 4 exercices (12–15 min) — `1SPE-DERLOCAL-EX-027..028`, `1SPE-DERLOCAL-EX-045..046`
- parcours 3 : 3 exercices (20–20 min) — `1SPE-DERLOCAL-EX-029..030`, `1SPE-DERLOCAL-EX-048`

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
- attendus officiels obligatoires rattaches : 10 sur 10 ; manquants : 0 ; hors annee : 0.
- chapitres dont ce chapitre depend par ses prerequis : `2GT`. La coherence au niveau du manuel se juge avec eux.

La regle du depot : « la richesse se mesure en occasions distinctes et en gestes de raisonnement declares ; jamais en nombre de fichiers ».

## 7. Barème commenté — propositions à juger

La politique est fixée : pour chaque question évaluée, des POINTS, un ATTENDU ESSENTIEL, et un CRÉDIT PARTIEL seulement lorsqu'une décomposition objective le justifie. Le corrigé scientifique reste séparé et complet ; le barème ne le remplace pas.

Ces propositions sont **machine** et ne valent aucune approbation. Elles sont le contenu candidat que votre verdict de chapitre couvre.

### 1SPE-DERLOCAL-EV-A

**Exercice 1** — 6 points (C1, C2)

- **Q1** — 1,5 pt — Attendu : calculer — \[ \tau = \frac{f(4)-f(1)}{4-1} = \frac{5-2}{3} = 1. \].
- **Q2** — 2 pts — Attendu : calculer — $f(3) = 9 - 12 + 5 = 2$.
- **Q3** — 1 pt — Attendu : en déduire — $f'(3) = \lim_{h \to 0}(h+2) = 2.$.
- **Q4** — 1,5 pt — Attendu : interpréter — $f'(3) = 2$ signifie que la tangente à la courbe de $f$ au point d'abscisse $3$ a pour pente $2$ : la courbe monte localement avec un coefficient directeur de $2$.

**Exercice 2** — 5 points (C2, C4)

- **Q1** — 1 pt — Attendu : calculer — $g'(1) = 3 \times 1^2 = 3.$.
- **Q2** — 2 pts — Attendu : donner — La tangente $T_1$ en $x=1$ : \[ T_1 : y = g'(1)(x-1) + g(1) = 3(x-1) + 1 = 3x - 2. \].
- **Q3** — 1 pt — Attendu : vérifier — Le point $(0;-2)$ est bien sur $T_1$.
- **Q4** — 1 pt — Attendu : déterminer — La tangente est horizontale au point d'abscisse $0$.

**Exercice 3** — 5 points (C3, C4, C5)

- **Q1** — 1 pt — Attendu : donner — $f(2) = 7$ (ordonnée du point $A$) et $f'(2) = -3$ (pente de la tangente en $A$).
- **Q2** — 1,5 pt — Attendu : donner — $T : y = f'(2)(x-2)+f(2) = -3(x-2)+7 = -3x + 13.$.
- **Q3** — 1,5 pt — Attendu : approcher — $f(2{,}04) \approx f(2) + f'(2) \times 0{,}04 = 7 + (-3) \times 0{,}04 = 7 - 0{,}12 = 6{,}88.$.
- **Q4** — 1 pt — Attendu : justifier — l'écart avec la valeur exacte est d'autant plus petit que $|h|$ est petit.

**Exercice 4** — 4 points (C1, C5)

- **Q1** — 1,5 pt — Attendu : calculer — \[ \tau = \frac{h(3)-h(2)}{3-2} = \frac{\frac{1}{3}-\frac{1}{2}}{1} = \frac{-\frac{1}{6}}{1} = -\frac{1}{6} \approx -0{,}167. \].
- **Q2** — 1,5 pt — Attendu : approcher — \[ h(2{,}05) \approx h(2) + h'(2) \times 0{,}05 = \frac{1}{2} + \left(-\frac{1}{4}\right) \times 0{,}05 = 0{,}5 - 0{,}0125 = 0{,}4875. \].
- **Q3** — 1 pt — Attendu : comparer — L'erreur est de l'ordre de $0{,}0003$, soit environ $0{,}06\,\%$.

### 1SPE-DERLOCAL-EV-B

**Exercice 1** — 6 points (C1, C2)

- **Q1** — 1,5 pt — Attendu : calculer — \[ \tau = \frac{f(5)-f(2)}{5-2} = \frac{5-2}{3} = 1. \].
- **Q2** — 2 pts — Attendu : calculer — \begin{align*} f(5+h) &= (5+h)^2 - 6(5+h) + 10 \\ &= 25 + 10h + h^2 - 30 - 6h + 10 = h^2 + 4h + 5. \end{align*} \[ \frac{f(5+h)-f(5)}{h} = \frac{h^2+4h}{h} = h+4. \].
- **Q3** — 1 pt — Attendu : en déduire — $f'(5) = \lim_{h \to 0}(h+4) = 4.$.
- **Q4** — 1,5 pt — Attendu : interpréter — $f'(5) = 4$ signifie que la tangente à la courbe de $f$ au point d'abscisse $5$ a pour pente $4$ : la courbe monte localement avec un coefficient directeur de $4$.

**Exercice 2** — 5 points (C2, C4)

- **Q1** — 1 pt — Attendu : calculer — $g'(2) = 3 \times 2^2 = 12.$.
- **Q2** — 2 pts — Attendu : donner — La tangente $T_2$ en $x=2$ : \[ T_2 : y = 12(x-2) + 8 = 12x - 16. \].
- **Q3** — 1 pt — Attendu : vérifier — Le point $(0;-16)$ est bien sur $T_2$.
- **Q4** — 1 pt — Attendu : déterminer — Tangente horizontale $\Leftrightarrow g'(a) = 0 \Leftrightarrow 3a^2 = 0 \Leftrightarrow a = 0$.

**Exercice 3** — 5 points (C3, C4, C5)

- **Q1** — 1 pt — Attendu : donner — $f(3) = 4$ et $f'(3) = 2$.
- **Q2** — 1,5 pt — Attendu : donner — $T : y = 2(x-3)+4 = 2x - 2.$.
- **Q3** — 1,5 pt — Attendu : approcher — $f(3{,}02) \approx f(3) + f'(3) \times 0{,}02 = 4 + 2 \times 0{,}02 = 4{,}04.$.
- **Q4** — 1 pt — Attendu : justifier — C'est une valeur approchée ($\approx$).

**Exercice 4** — 4 points (C1, C5)

- **Q1** — 1,5 pt — Attendu : calculer — \[ \tau = \frac{h(5)-h(4)}{5-4} = \frac{\frac{1}{5}-\frac{1}{4}}{1} = \frac{-\frac{1}{20}}{1} = -\frac{1}{20} = -0{,}05. \].
- **Q2** — 1,5 pt — Attendu : approcher — \[ h(5{,}02) \approx h(5) + h'(5) \times 0{,}02 = \frac{1}{5} + \left(-\frac{1}{25}\right) \times 0{,}02 = 0{,}2 - 0{,}0008 = 0{,}1992. \].
- **Q3** — 1 pt — Attendu : comparer — Valeur exacte : $\dfrac{1}{5{,}02} = \dfrac{50}{251} \approx 0{,}19920\ldots$ Approximation : $0{,}1992$.

Ce chapitre porte 30 question(s) évaluée(s), dont 0 attendent votre jugement. Ce ne sont pas autant de signatures : votre verdict porte sur le chapitre.

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

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-DERIVATION-LOCAL/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
