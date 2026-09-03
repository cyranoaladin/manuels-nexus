# Vue de lecture — Fonction exponentielle — EXPERT_PROGRAMME_PEDAGOGIE

Chapitre `1SPE-EXPONENTIELLE` · manuel `1SPE` (Première, Spécialité mathématiques) · packet B · role `EXPERT_PROGRAMME_PEDAGOGIE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-EXPONENTIELLE/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`
> Etat de revue : `audit/reviews/human/1SPE-EXPONENTIELLE/REVIEW_STATE.json`
> Producteur de cette vue : `scripts/build_human_review_reading_views.py`
>
> Toute divergence entre cette vue et le packet se tranche en faveur du packet. Cette vue ne cree, ne ferme et ne reduit aucune obligation.

## 1. Ce que vous decidez

- L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.
- Aucun humain n'a encore approuve ce chapitre : REVIEW_DELTA_BASELINE = NONE. Le perimetre de revue est le CHAPITRE COURANT ENTIER. Les listes ci-dessous dirigent l'attention, elles ne reduisent pas le perimetre.
- CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST (`sha256:315df40027aaedb26f1ac573d1a20e0011615f9fe894db94db02ac3623e64bc1`) ; l'approbation graphique releve de la porte D7, independante.
- Verdicts autorises, a rendre dans le packet JSON canonique et jamais dans cette vue : `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`.
- Cette vue ne porte aucune decision et ne nomme personne : l'assignation du role reste `PENDING_UNASSIGNED`, l'etat du packet reste `PENDING_UNASSIGNED`.

| Perimetre | Valeur |
| --- | --- |
| Objets du chapitre dans le packet | 147 |
| Empreinte de l'ensemble d'objets | `sha256:c67e1bd9a552906b11f0df7f15bf1d59e04ef5f832dee6befb8d0568e87dd703` |
| Empreinte semantique liee a l'approbation | `sha256:315df40027aaedb26f1ac573d1a20e0011615f9fe894db94db02ac3623e64bc1` |
| Empreinte du packet | `sha256:b8211f57aea4b87ece70fe9faa8457637f087eaccae6a9b10d4718ba6484d5be` |
| Revision du depot gelee dans le packet | `5bc44275a0afe33f10b7ce2ec7700778f8de6308` |
| Preuve de rendu portee par le packet | `ABSENT` |

## 2. Le chapitre et ses capacites du programme officiel

**Fonction exponentielle** — programme applicable 2026-2027, MENE2602917A, BO n° 14 du 2026-04-02.
Source officielle : https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A

Situation d'accroche declaree : La population d'une culture bactérienne double toutes les 20 minutes. Combien de bactéries y aura-t-il après 3 heures si l'on part de 1000 ? Comment modéliser cette croissance exponentielle ?

Temps estime declare : parcours 1 : 12 h · parcours 2 : 10 h · parcours 3 : 8 h.

| Code | Libelle eleve | Libelle BO | Demonstration exigible |
| --- | --- | --- | --- |
| `C1` | Je sais que la fonction exponentielle est l'unique fonction égale à sa dérivée valant 1 en 0. | Connaître la définition de la fonction exponentielle comme unique fonction dérivable sur ℝ vérifiant f'=f et f(0)=1. | non |
| `C2` | Je sais utiliser les propriétés algébriques de l'exponentielle (somme, produit, puissance). | Connaître et utiliser les propriétés algébriques de la fonction exponentielle : exp(a+b)=exp(a)exp(b), exp(-a)=1/exp(a), exp(na)=(exp(a))^n. | non |
| `C3` | Je sais exploiter le signe, la croissance et la courbe de l'exponentielle, en lien avec les suites géométriques. | Connaître le signe, le sens de variation et la courbe représentative de la fonction exponentielle ; faire le lien avec les suites géométriques. | non |
| `C4` | Je sais dériver la fonction t → $e^{at}$ pour un réel a. | Pour a réel, déterminer la dérivée de la fonction t → $e^{at}$. | non |
| `C5` | Je sais représenter et utiliser un modèle de croissance ou de décroissance exponentielle. | Pour k strictement positif, représenter t → e^{-kt} et t → e^{kt} ; modéliser une croissance ou une décroissance exponentielle. | non |

**Attendus officiels rattaches, capacite par capacite**

- `C1` — 1 attendu :
    - `1SPE-OFFICIAL-108` (MANDATORY_KNOWLEDGE, Fonction exponentielle) : Définition de la fonction exponentielle comme unique fonction dérivable sur ℝ vérifiant ƒ ‘ = ƒ et ƒ (0) = 1. L’existence et l’unicité sont admises. Notation exp(𝑥).
- `C2` — 2 attendus :
    - `1SPE-OFFICIAL-109` (MANDATORY_KNOWLEDGE, Fonction exponentielle) : Pour tous réels 𝑥 et 𝑦, exp(𝑥 + 𝑦) = exp(𝑥) exp(𝑦) et exp(𝑥) exp(–𝑥) = 1. Nombre e. Notation e 𝑥.
    - `1SPE-OFFICIAL-111` (MANDATORY_CAPACITY, Fonction exponentielle) : Transformer une expression en utilisant les propriétés algébriques de la fonction exponentielle.
- `C3` — 1 attendu :
    - `1SPE-OFFICIAL-110` (MANDATORY_KNOWLEDGE, Fonction exponentielle) : Signe, sens de variation et courbe représentative de la fonction exponentielle. Lien avec les suites géométriques.
- `C4` — 1 attendu :
    - `1SPE-OFFICIAL-112` (MANDATORY_CAPACITY, Fonction exponentielle) : Pour a réel, dérivée de la fonction t ↦ eat.
- `C5` — 2 attendus :
    - `1SPE-OFFICIAL-113` (MANDATORY_CAPACITY, Fonction exponentielle) : Pour une valeur numérique strictement positive de k, représenter graphiquement les fonctions t ↦ e–kt et t ↦ ekt.
    - `1SPE-OFFICIAL-114` (MANDATORY_CAPACITY, Fonction exponentielle) : Modéliser une situation par une croissance, une décroissance exponentielle (par exemple évolution d’un capital à taux fixe, décroissance radioactive).

**Prerequis declares par le contrat du chapitre**

| Code | Libelle | Chapitre d'origine |
| --- | --- | --- |
| `R1` | Dérivée d'une somme, d'un produit, d'un quotient | 1SPE-DERIVATION-GLOBAL |
| `R2` | Signe de la dérivée et sens de variation | 1SPE-DERIVATION-GLOBAL |
| `R3` | Résolution d'équations et d'inéquations du second degré | 1SPE-SECOND-DEGRE |
| `R4` | Puissances entières et règles de calcul | 2GT |
| `R5` | Suites géométriques et coefficient multiplicateur | 1SPE-SUITES |

## 3. Structure reelle et ordre d'assemblage courant

L'ordre ci-dessous n'est pas l'ordre alphabetique des repertoires : il est lu chez l'assembleur du manuel (`Mathematiques/manuel-maths/scripts/assemble_manuel.py`, `collect_chapter`). C'est la sequence que le lecteur du PDF recoit.

| Rang | Rubrique imprimee | Objets (professeur) |
| --- | --- | --- |
| 1 | Cours | 6 |
| 2 | Méthodes | 6 |
| 3 | Exercices | 68 |
| 4 | TD | 2 |
| 5 | Auto-évaluation | 1 |
| 6 | Évaluation | 4 |
| 7 | Remédiation | 10 |
| 8 | Corrigés | 50 |

Total assemble : 147 objets en variante professeur, 95 en variante eleve (la variante eleve exclut les corriges et les corriges d'evaluation).

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

### Capacite `C1` — « Je sais que la fonction exponentielle est l'unique fonction égale à sa dérivée valant 1 en 0. »

Libelle BO : Connaître la définition de la fonction exponentielle comme unique fonction dérivable sur ℝ vérifiant f'=f et f(0)=1.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 10 | `1SPE-EXPO-CO-001..004`, `1SPE-EXPO-CO-006..008`, `1SPE-EXPO-CO-010`, `1SPE-EXPO-CO-047`, `1SPE-EXPO-CO-050` |
| cours | 1 | `1SPE-EXPO-COURS-C1` |
| evaluations | 2 | `1SPE-EXPO-EV-A`, `1SPE-EXPO-EV-B` |
| exercices | 10 | `1SPE-EXPO-EX-001..004`, `1SPE-EXPO-EX-006..008`, `1SPE-EXPO-EX-010`, `1SPE-EXPO-EX-047`, `1SPE-EXPO-EX-050` |
| methodes | 1 | `1SPE-EXPO-ME-006` |
| QCM | 3 | `Q1..3` |
| remediation | 1 | `1SPE-EXPONENTIELLE-RE-C1` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 10.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-EXPO-EV-A`, `1SPE-EXPO-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (5–5 min) — `1SPE-EXPO-EX-001..004`
- parcours 2 : 3 exercices (8–10 min) — `1SPE-EXPO-EX-006..008`
- parcours 3 : 3 exercices (12–15 min) — `1SPE-EXPO-EX-010`, `1SPE-EXPO-EX-047`, `1SPE-EXPO-EX-050`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C2` — « Je sais utiliser les propriétés algébriques de l'exponentielle (somme, produit, puissance). »

Libelle BO : Connaître et utiliser les propriétés algébriques de la fonction exponentielle : exp(a+b)=exp(a)exp(b), exp(-a)=1/exp(a), exp(na)=(exp(a))^n.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 9 | `1SPE-EXPO-CO-011..014`, `1SPE-EXPO-CO-016..018`, `1SPE-EXPO-CO-047`, `1SPE-EXPO-CO-050` |
| cours | 1 | `1SPE-EXPO-COURS-C2` |
| evaluations | 2 | `1SPE-EXPO-EV-A`, `1SPE-EXPO-EV-B` |
| exercices | 9 | `1SPE-EXPO-EX-011..014`, `1SPE-EXPO-EX-016..018`, `1SPE-EXPO-EX-047`, `1SPE-EXPO-EX-050` |
| methodes | 1 | `1SPE-EXPO-ME-001` |
| QCM | 3 | `Q4..6` |
| remediation | 1 | `1SPE-EXPONENTIELLE-RE-C2` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 9.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-EXPO-EV-A`, `1SPE-EXPO-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 4 exercices (5–5 min) — `1SPE-EXPO-EX-011..014`
- parcours 2 : 3 exercices (8–10 min) — `1SPE-EXPO-EX-016..018`
- parcours 3 : 2 exercices (15–15 min) — `1SPE-EXPO-EX-047`, `1SPE-EXPO-EX-050`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C3` — « Je sais exploiter le signe, la croissance et la courbe de l'exponentielle, en lien avec les suites géométriques. »

Libelle BO : Connaître le signe, le sens de variation et la courbe représentative de la fonction exponentielle ; faire le lien avec les suites géométriques.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 9 | `1SPE-EXPO-CO-006`, `1SPE-EXPO-CO-021..022`, `1SPE-EXPO-CO-024..026`, `1SPE-EXPO-CO-030`, `1SPE-EXPO-CO-047`, `1SPE-EXPO-CO-049` |
| cours | 1 | `1SPE-EXPO-COURS-C3` |
| evaluations | 2 | `1SPE-EXPO-EV-A`, `1SPE-EXPO-EV-B` |
| exercices | 9 | `1SPE-EXPO-EX-006`, `1SPE-EXPO-EX-021..022`, `1SPE-EXPO-EX-024..026`, `1SPE-EXPO-EX-030`, `1SPE-EXPO-EX-047`, `1SPE-EXPO-EX-049` |
| methodes | 1 | `1SPE-EXPO-ME-002` |
| QCM | 3 | `Q7..9` |
| remediation | 1 | `1SPE-EXPONENTIELLE-RE-C3` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 9.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-EXPO-EV-A`, `1SPE-EXPO-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 3 exercices (5–5 min) — `1SPE-EXPO-EX-021..022`, `1SPE-EXPO-EX-024`
- parcours 2 : 3 exercices (8–10 min) — `1SPE-EXPO-EX-006`, `1SPE-EXPO-EX-025..026`
- parcours 3 : 3 exercices (15–15 min) — `1SPE-EXPO-EX-030`, `1SPE-EXPO-EX-047`, `1SPE-EXPO-EX-049`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C4` — « Je sais dériver la fonction t → $e^{at}$ pour un réel a. »

Libelle BO : Pour a réel, déterminer la dérivée de la fonction t → $e^{at}$.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 8 | `1SPE-EXPO-CO-031..033`, `1SPE-EXPO-CO-035..038`, `1SPE-EXPO-CO-049` |
| cours | 1 | `1SPE-EXPO-COURS-C4` |
| evaluations | 2 | `1SPE-EXPO-EV-A`, `1SPE-EXPO-EV-B` |
| exercices | 8 | `1SPE-EXPO-EX-031..033`, `1SPE-EXPO-EX-035..038`, `1SPE-EXPO-EX-049` |
| methodes | 1 | `1SPE-EXPO-ME-003` |
| QCM | 3 | `Q10..12` |
| remediation | 1 | `1SPE-EXPONENTIELLE-RE-C4` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 8.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-EXPO-EV-A`, `1SPE-EXPO-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 3 exercices (5–7 min) — `1SPE-EXPO-EX-031..033`
- parcours 2 : 4 exercices (10–10 min) — `1SPE-EXPO-EX-035..038`
- parcours 3 : 1 exercice (15–15 min) — `1SPE-EXPO-EX-049`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C5` — « Je sais représenter et utiliser un modèle de croissance ou de décroissance exponentielle. »

Libelle BO : Pour k strictement positif, représenter t → e^{-kt} et t → e^{kt} ; modéliser une croissance ou une décroissance exponentielle.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 8 | `1SPE-EXPO-CO-041..046`, `1SPE-EXPO-CO-049..050` |
| cours | 1 | `1SPE-EXPO-COURS-C5` |
| evaluations | 2 | `1SPE-EXPO-EV-A`, `1SPE-EXPO-EV-B` |
| exercices | 8 | `1SPE-EXPO-EX-041..046`, `1SPE-EXPO-EX-049..050` |
| methodes | 2 | `1SPE-EXPO-ME-004..005` |
| QCM | 3 | `Q13..15` |
| remediation | 1 | `1SPE-EXPONENTIELLE-RE-C5` |

**Richesse declaree**

- type de capacite : `ATOMIC_SUPPORT` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 2 · qcm : 3 · remediation : 1 · targeted_practice : 8.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-EXPO-EV-A`, `1SPE-EXPO-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 2 exercices (8–8 min) — `1SPE-EXPO-EX-041..042`
- parcours 2 : 2 exercices (10–12 min) — `1SPE-EXPO-EX-043..044`
- parcours 3 : 4 exercices (15–15 min) — `1SPE-EXPO-EX-045..046`, `1SPE-EXPO-EX-049..050`

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
- attendus officiels obligatoires rattaches : 7 sur 7 ; manquants : 0 ; hors annee : 0.
- chapitres dont ce chapitre depend par ses prerequis : `1SPE-DERIVATION-GLOBAL`, `1SPE-SECOND-DEGRE`, `1SPE-SUITES`, `2GT`. La coherence au niveau du manuel se juge avec eux.

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

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-EXPONENTIELLE/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
