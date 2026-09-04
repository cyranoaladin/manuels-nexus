# Vue de lecture — Produit scalaire — EXPERT_PROGRAMME_PEDAGOGIE

Chapitre `1SPE-PRODUIT-SCALAIRE` · manuel `1SPE` (Première, Spécialité mathématiques) · packet B · role `EXPERT_PROGRAMME_PEDAGOGIE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-PRODUIT-SCALAIRE/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`
> Etat de revue : `audit/reviews/human/1SPE-PRODUIT-SCALAIRE/REVIEW_STATE.json`
> Producteur de cette vue : `scripts/build_human_review_reading_views.py`
>
> Toute divergence entre cette vue et le packet se tranche en faveur du packet. Cette vue ne cree, ne ferme et ne reduit aucune obligation.

## 1. Ce que vous decidez

- L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.
- Aucun humain n'a encore approuve ce chapitre : REVIEW_DELTA_BASELINE = NONE. Le perimetre de revue est le CHAPITRE COURANT ENTIER. Les listes ci-dessous dirigent l'attention, elles ne reduisent pas le perimetre.
- CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST (`sha256:c7c704558c02255341ae17e45afd38bef72087c89add29a5c911446a6f83ac45`) ; l'approbation graphique releve de la porte D7, independante.
- Verdicts autorises, a rendre dans le packet JSON canonique et jamais dans cette vue : `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`.
- Cette vue ne porte aucune decision et ne nomme personne : l'assignation du role reste `PENDING_UNASSIGNED`, l'etat du packet reste `PENDING_UNASSIGNED`.

| Perimetre | Valeur |
| --- | --- |
| Objets du chapitre dans le packet | 145 |
| Empreinte de l'ensemble d'objets | `sha256:6cac1a2c49baa43a9ad95684214f2f0944b700450f83a64a4a24e63ab9c320cd` |
| Empreinte semantique liee a l'approbation | `sha256:c7c704558c02255341ae17e45afd38bef72087c89add29a5c911446a6f83ac45` |
| Empreinte du packet | `sha256:408b6ef3a881625d2417072c91fa8133fff797809b3cc77156d0ef4480a9cff9` |
| Revision du depot gelee dans le packet | `dfc99058e7a7c16ae4af46b99245edbe14b4f8e5` |
| Preuve de rendu portee par le packet | `ABSENT` |

## 2. Le chapitre et ses capacites du programme officiel

**Produit scalaire** — programme applicable 2026-2027, MENE2602917A, BO n° 14 du 2026-04-02.
Source officielle : https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A

Situation d'accroche declaree : Un randonneur se deplace de 5 km vers le nord-est puis de 3 km vers le sud-est. Quelle distance le separe de son point de depart ? Comment calculer l'angle entre deux trajets dans le plan ?

Temps estime declare : parcours 1 : 12 h · parcours 2 : 10 h · parcours 3 : 8 h.

| Code | Libelle eleve | Libelle BO | Demonstration exigible |
| --- | --- | --- | --- |
| `C1` | Je sais calculer un produit scalaire (definition geometrique, projection, expression analytique). | Définir le produit scalaire de deux vecteurs (définition géométrique, projection orthogonale, expression analytique). | non |
| `C2` | Je sais utiliser les proprietes du produit scalaire (bilinearite, symetrie, norme). | Connaître et utiliser les propriétés du produit scalaire (bilinéarité, symétrie, norme). | oui — Démonstration de l'expression analytique à partir de la bilinéarité. |
| `C3` | Je sais determiner l'orthogonalite de deux vecteurs et calculer un angle. | Utiliser le produit scalaire pour déterminer des angles, des orthogonalités et des longueurs. | non |
| `C4` | Je sais utiliser le produit scalaire dans des problemes geometriques (mediatrice, hauteurs, aires). | Résoudre des problèmes géométriques à l'aide du produit scalaire. | non |
| `C5` | Je sais appliquer la formule d'Al-Kashi et en connais la demonstration. | Développer les carrés des normes de la somme et de la différence de deux vecteurs ; connaître et démontrer la formule d'Al-Kashi. | oui — Démonstration de la formule d'Al-Kashi par le produit scalaire. |

**Attendus officiels rattaches, capacite par capacite**

- `C1` — 2 attendus :
    - `1SPE-OFFICIAL-128` (MANDATORY_KNOWLEDGE, Calcul vectoriel et produit scalaire) : Produit scalaire à partir de la projection orthogonale et de la formule avec le cosinus. Caractérisation de l’orthogonalité.
    - `1SPE-OFFICIAL-133` (MANDATORY_CAPACITY, Calcul vectoriel et produit scalaire) : En vue de la résolution d’un problème, calculer le produit scalaire de deux vecteurs en choisissant une méthode adaptée (en utilisant la projection orthogonale, à l’aide des coordonnées, à l’aide des normes et d’un angle, à l’aide de normes).
- `C2` — 2 attendus :
    - `1SPE-OFFICIAL-129` (MANDATORY_KNOWLEDGE, Calcul vectoriel et produit scalaire) : Bilinéarité, symétrie. En base orthonormée, expression du produit scalaire et de la norme, critère d’orthogonalité. Expression des coordonnées dans une base orthonormée en termes de produits scalaires avec les vecteurs de la base.
    - `1SPE-OFFICIAL-130` (MANDATORY_KNOWLEDGE, Calcul vectoriel et produit scalaire) : Développement de ‖𝑢 ⃗ + 𝑣‖2 et ‖𝑢 ⃗ − 𝑣 ‖2 . Formule d’Al-Kashi.
- `C3` — 1 attendu :
    - `1SPE-OFFICIAL-132` (MANDATORY_CAPACITY, Calcul vectoriel et produit scalaire) : Utiliser le produit scalaire pour démontrer une orthogonalité, pour calculer un angle, une longueur dans le plan.
- `C4` — 3 attendus :
    - `1SPE-OFFICIAL-131` (MANDATORY_KNOWLEDGE, Calcul vectoriel et produit scalaire) : Transformation de l’expression M ⃗⃗⃗⃗⃗⃗B. ⃗⃗⃗⃗⃗⃗⃗A ⋅ M
    - `1SPE-OFFICIAL-134` (MANDATORY_CAPACITY, Calcul vectoriel et produit scalaire) : Utiliser le produit scalaire pour résoudre un problème géométrique.
    - `1SPE-OFFICIAL-136` (MANDATORY_SKILL, Calcul vectoriel et produit scalaire) : Ensemble des points M tels que M ⃗⃗⃗⃗⃗⃗B = 0 (démonstration avec le produit scalaire). ⃗⃗⃗⃗⃗⃗⃗A ⋅ M
- `C5` — 1 attendu :
    - `1SPE-OFFICIAL-135` (MANDATORY_SKILL, Calcul vectoriel et produit scalaire) : Formule d’Al-Kashi (démonstration avec le produit scalaire).

**Prerequis declares par le contrat du chapitre**

| Code | Libelle | Chapitre d'origine |
| --- | --- | --- |
| `R1` | Vecteurs et coordonnees dans le plan | 2GT |
| `R2` | Norme d'un vecteur | 2GT |
| `R3` | Trigonometrie (cos, sin, valeurs remarquables) | 1SPE-TRIGONOMETRIE |
| `R4` | Calcul litteral (identites remarquables, developpement) | 2GT |
| `R5` | Theoreme de Pythagore | 2GT |

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

### Capacite `C1` — « Je sais calculer un produit scalaire (definition geometrique, projection, expression analytique). »

Libelle BO : Définir le produit scalaire de deux vecteurs (définition géométrique, projection orthogonale, expression analytique).

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 10 | `1SPE-PRODSCAL-CO-001..010` |
| cours | 1 | `1SPE-PRODSCAL-COURS-C1` |
| evaluations | 2 | `1SPE-PRODSCAL-EV-A`, `1SPE-PRODSCAL-EV-B` |
| exercices | 10 | `1SPE-PRODSCAL-EX-001..010` |
| methodes | 1 | `1SPE-PRODSCAL-ME-001` |
| QCM | 3 | `Q1..3` |
| remediation | 1 | `1SPE-PRODUIT-SCALAIRE-RE-C1` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 10.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-PRODSCAL-EV-A`, `1SPE-PRODSCAL-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (5–5 min) — `1SPE-PRODSCAL-EX-001..004`
- parcours 2 : 4 exercices (5–5 min) — `1SPE-PRODSCAL-EX-005..008`
- parcours 3 : 2 exercices (5–5 min) — `1SPE-PRODSCAL-EX-009..010`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C2` — « Je sais utiliser les proprietes du produit scalaire (bilinearite, symetrie, norme). »

Libelle BO : Connaître et utiliser les propriétés du produit scalaire (bilinéarité, symétrie, norme).

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 10 | `1SPE-PRODSCAL-CO-011..020` |
| cours | 1 | `1SPE-PRODSCAL-COURS-C2` |
| evaluations | 2 | `1SPE-PRODSCAL-EV-A`, `1SPE-PRODSCAL-EV-B` |
| exercices | 10 | `1SPE-PRODSCAL-EX-011..020` |
| methodes | 1 | `1SPE-PRODSCAL-ME-002` |
| QCM | 3 | `Q4..6` |
| remediation | 1 | `1SPE-PRODUIT-SCALAIRE-RE-C2` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 10.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-PRODSCAL-EV-A`, `1SPE-PRODSCAL-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (5–5 min) — `1SPE-PRODSCAL-EX-011..014`
- parcours 2 : 4 exercices (5–5 min) — `1SPE-PRODSCAL-EX-015..018`
- parcours 3 : 2 exercices (5–5 min) — `1SPE-PRODSCAL-EX-019..020`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C3` — « Je sais determiner l'orthogonalite de deux vecteurs et calculer un angle. »

Libelle BO : Utiliser le produit scalaire pour déterminer des angles, des orthogonalités et des longueurs.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 10 | `1SPE-PRODSCAL-CO-021..030` |
| cours | 1 | `1SPE-PRODSCAL-COURS-C3` |
| evaluations | 2 | `1SPE-PRODSCAL-EV-A`, `1SPE-PRODSCAL-EV-B` |
| exercices | 10 | `1SPE-PRODSCAL-EX-021..030` |
| methodes | 1 | `1SPE-PRODSCAL-ME-003` |
| QCM | 3 | `Q7..9` |
| remediation | 1 | `1SPE-PRODUIT-SCALAIRE-RE-C3` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 10.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-PRODSCAL-EV-A`, `1SPE-PRODSCAL-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (5–5 min) — `1SPE-PRODSCAL-EX-021..024`
- parcours 2 : 4 exercices (5–5 min) — `1SPE-PRODSCAL-EX-025..028`
- parcours 3 : 2 exercices (5–5 min) — `1SPE-PRODSCAL-EX-029..030`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C4` — « Je sais utiliser le produit scalaire dans des problemes geometriques (mediatrice, hauteurs, aires). »

Libelle BO : Résoudre des problèmes géométriques à l'aide du produit scalaire.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 10 | `1SPE-PRODSCAL-CO-031..040` |
| cours | 1 | `1SPE-PRODSCAL-COURS-C4` |
| evaluations | 2 | `1SPE-PRODSCAL-EV-A`, `1SPE-PRODSCAL-EV-B` |
| exercices | 10 | `1SPE-PRODSCAL-EX-031..040` |
| methodes | 1 | `1SPE-PRODSCAL-ME-004` |
| QCM | 3 | `Q10..12` |
| remediation | 1 | `1SPE-PRODUIT-SCALAIRE-RE-C4` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 10.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-PRODSCAL-EV-A`, `1SPE-PRODSCAL-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (5–5 min) — `1SPE-PRODSCAL-EX-031..034`
- parcours 2 : 4 exercices (5–5 min) — `1SPE-PRODSCAL-EX-035..038`
- parcours 3 : 2 exercices (5–5 min) — `1SPE-PRODSCAL-EX-039..040`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C5` — « Je sais appliquer la formule d'Al-Kashi et en connais la demonstration. »

Libelle BO : Développer les carrés des normes de la somme et de la différence de deux vecteurs ; connaître et démontrer la formule d'Al-Kashi.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 7 | `1SPE-PRODSCAL-CO-041..044`, `1SPE-PRODSCAL-CO-046..047`, `1SPE-PRODSCAL-CO-049` |
| cours | 1 | `1SPE-PRODSCAL-COURS-C5` |
| evaluations | 2 | `1SPE-PRODSCAL-EV-A`, `1SPE-PRODSCAL-EV-B` |
| exercices | 7 | `1SPE-PRODSCAL-EX-041..044`, `1SPE-PRODSCAL-EX-046..047`, `1SPE-PRODSCAL-EX-049` |
| methodes | 1 | `1SPE-PRODSCAL-ME-005` |
| QCM | 3 | `Q13..15` |
| remediation | 1 | `1SPE-PRODUIT-SCALAIRE-RE-C5` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 7.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-PRODSCAL-EV-A`, `1SPE-PRODSCAL-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (5–5 min) — `1SPE-PRODSCAL-EX-041..044`
- parcours 2 : 2 exercices (5–5 min) — `1SPE-PRODSCAL-EX-046..047`
- parcours 3 : 1 exercice (5–5 min) — `1SPE-PRODSCAL-EX-049`

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
- attendus officiels obligatoires rattaches : 9 sur 9 ; manquants : 0 ; hors annee : 0.
- chapitres dont ce chapitre depend par ses prerequis : `1SPE-TRIGONOMETRIE`, `2GT`. La coherence au niveau du manuel se juge avec eux.

La regle du depot : « la richesse se mesure en occasions distinctes et en gestes de raisonnement declares ; jamais en nombre de fichiers ».

## 7. Barème commenté — propositions à juger

La politique est fixée : pour chaque question évaluée, des POINTS, un ATTENDU ESSENTIEL, et un CRÉDIT PARTIEL seulement lorsqu'une décomposition objective le justifie. Le corrigé scientifique reste séparé et complet ; le barème ne le remplace pas.

Ces propositions sont **machine** et ne valent aucune approbation. Elles sont le contenu candidat que votre verdict de chapitre couvre.

### 1SPE-PRODSCAL-EV-A

**Exercice 1** — 5 points (C1, C2)

- **Q1** — 1 pt — Attendu : calculer — $\vec{u} \cdot \vec{v} = 3 \times 2 + (-1) \times 5 = 6 - 5 = 1$.
- **Q2** — 1 pt — Attendu : calculer — $\|\vec{u}\| = \sqrt{9 + 1} = \sqrt{10}$ et $\|\vec{v}\| = \sqrt{4 + 25} = \sqrt{29}$.
- **Q3** — 1,5 pt — Attendu : calculer — Vérification directe : $\vec{u} + \vec{v} = \begin{pmatrix} 5 \\ 4 \end{pmatrix}$, $\|\vec{u} + \vec{v}\|^2 = 25 + 16 = 41$.
- **Q4** — 1,5 pt — Attendu : vérifier — $(5)(1) + (4)(-6) = 5 - 24 = -19$.

**Exercice 2** — 5 points (C3)

- **Q1** — 2 pts — Attendu : montrer — Le triangle $ABC$ est \textbf{rectangle en $A$}.
- **Q2** — 2 pts — Attendu : calculer — $\overrightarrow{BA} \cdot \overrightarrow{BC} = 3 + 10 = 13$, $\|\overrightarrow{BA}\| = \sqrt{13}$, $\|\overrightarrow{BC}\| = \sqrt{26}$.
- **Q3** — 1 pt — Attendu : en déduire — Le triangle est rectangle isocele en $A$.

**Exercice 3** — 5 points (C4)

- **Q1** — 1,5 pt — Attendu : déterminer — $\overrightarrow{IM} \cdot \overrightarrow{AB} = 0$ : $6(x - 3) + 0 = 0$, soit $x = 3$.
- **Q2** — 2 pts — Attendu : déterminer — $H = (3; 3)$. *Crédit partiel : 1,5 pt si la première étape est correcte mais la suite erronée.*
- **Q3** — 1,5 pt — Attendu : calculer — $\mathcal{A} = \dfrac{1}{2} |x_B \cdot y_C - x_C \cdot y_B| = \dfrac{1}{2} |6 \times 4 - 2 \times 0| = \dfrac{24}{2} = 12$.

**Exercice 4** — 5 points (C5)

- **Q1** — 2 pts — Attendu : calculer — $BC = 7$.
- **Q2** — 1,5 pt — Attendu : calculer — $\cos\widehat{ABC} = \dfrac{BC^2 + AB^2 - AC^2}{2 \cdot BC \cdot AB} = \dfrac{49 + 64 - 25}{112} = \dfrac{88}{112} = \dfrac{11}{14}$.
- **Q3** — 1,5 pt — Attendu : calculer — $\mathcal{A} = \dfrac{1}{2} \times AB \times AC \times \sin\widehat{BAC} = \dfrac{1}{2} \times 8 \times 5 \times \dfrac{\sqrt{3}}{2} = 10\sqrt{3} \approx 17{,}3$.

### 1SPE-PRODSCAL-EV-B

**Exercice 1** — 5 points (C1, C2)

- **Q1** — 1 pt — Attendu : calculer — $\vec{u} \cdot \vec{v} = 4 \times (-1) + 2 \times 3 = -4 + 6 = 2$.
- **Q2** — 1 pt — Attendu : calculer — $\|\vec{u}\| = \sqrt{16 + 4} = \sqrt{20} = 2\sqrt{5}$ et $\|\vec{v}\| = \sqrt{1 + 9} = \sqrt{10}$.
- **Q3** — 1,5 pt — Attendu : calculer — Vérification : $\vec{u} - \vec{v} = \begin{pmatrix} 5 \\ -1 \end{pmatrix}$, $\|\vec{u} - \vec{v}\|^2 = 25 + 1 = 26$.
- **Q4** — 1,5 pt — Attendu : vérifier — $15 - 5 = 10$.

**Exercice 2** — 5 points (C3)

- **Q1** — 2 pts — Attendu : montrer — Le triangle est \textbf{rectangle en $A$}.
- **Q2** — 2 pts — Attendu : calculer — $\cos\widehat{ABC} = \dfrac{13}{\sqrt{13} \times \sqrt{26}} = \dfrac{13}{13\sqrt{2}} = \dfrac{\sqrt{2}}{2}$.
- **Q3** — 1 pt — Attendu : en déduire — Triangle rectangle isocele en $A$.

**Exercice 3** — 5 points (C4)

- **Q1** — 1,5 pt — Attendu : déterminer — Mediatrice : $8(x - 4) = 0$, soit $x = 4$.
- **Q2** — 2 pts — Attendu : déterminer — $H = \left(\dfrac{288}{61}; \dfrac{240}{61}\right)$.
- **Q3** — 1,5 pt — Attendu : calculer — $\mathcal{A} = \dfrac{1}{2} |x_B \cdot y_C - x_C \cdot y_B| = \dfrac{1}{2} |48 - 0| = 24$.

**Exercice 4** — 5 points (C5)

- **Q1** — 2 pts — Attendu : calculer — $BC = \sqrt{136 - 60\sqrt{2}} \approx 7{,}15$.
- **Q2** — 1,5 pt — Attendu : calculer — $\widehat{ABC} \approx 98{,}6°$.
- **Q3** — 1,5 pt — Attendu : calculer — $\mathcal{A} = \dfrac{1}{2} \times 6 \times 10 \times \sin\!\left(\dfrac{\pi}{4}\right) = 30 \times \dfrac{\sqrt{2}}{2} = 15\sqrt{2} \approx 21{,}2$.

Ce chapitre porte 26 question(s) évaluée(s), dont 0 attendent votre jugement. Ce ne sont pas autant de signatures : votre verdict porte sur le chapitre.

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

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-PRODUIT-SCALAIRE/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
