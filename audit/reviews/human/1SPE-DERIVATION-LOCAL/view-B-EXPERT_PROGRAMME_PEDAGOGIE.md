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
| Revision du depot gelee dans le packet | `5bc44275a0afe33f10b7ce2ec7700778f8de6308` |
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
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 12.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-DERLOCAL-EV-A`, `1SPE-DERLOCAL-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (5–8 min) — `1SPE-DERLOCAL-EX-001..002`, `1SPE-DERLOCAL-EX-031..032`
- parcours 2 : 4 exercices (12–15 min) — `1SPE-DERLOCAL-EX-003..004`, `1SPE-DERLOCAL-EX-039..040`
- parcours 3 : 4 exercices (15–25 min) — `1SPE-DERLOCAL-EX-005..006`, `1SPE-DERLOCAL-EX-047`, `1SPE-DERLOCAL-EX-049`

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
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 11.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-DERLOCAL-EV-A`, `1SPE-DERLOCAL-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 3 exercices (5–8 min) — `1SPE-DERLOCAL-EX-025..026`, `1SPE-DERLOCAL-EX-038`
- parcours 2 : 4 exercices (12–15 min) — `1SPE-DERLOCAL-EX-027..028`, `1SPE-DERLOCAL-EX-045..046`
- parcours 3 : 4 exercices (20–25 min) — `1SPE-DERLOCAL-EX-029..030`, `1SPE-DERLOCAL-EX-048..049`

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

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-DERIVATION-LOCAL/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
