# Vue de lecture — Probabilités conditionnelles et indépendance — EXPERT_PROGRAMME_PEDAGOGIE

Chapitre `1SPE-PROBA-COND` · manuel `1SPE` (Première, Spécialité mathématiques) · packet B · role `EXPERT_PROGRAMME_PEDAGOGIE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-PROBA-COND/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`
> Etat de revue : `audit/reviews/human/1SPE-PROBA-COND/REVIEW_STATE.json`
> Producteur de cette vue : `scripts/build_human_review_reading_views.py`
>
> Toute divergence entre cette vue et le packet se tranche en faveur du packet. Cette vue ne cree, ne ferme et ne reduit aucune obligation.

## 1. Ce que vous decidez

- L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.
- Aucun humain n'a encore approuve ce chapitre : REVIEW_DELTA_BASELINE = NONE. Le perimetre de revue est le CHAPITRE COURANT ENTIER. Les listes ci-dessous dirigent l'attention, elles ne reduisent pas le perimetre.
- CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST (`sha256:f92f4ce599c27d295f5108e529d2cb2bbe2071d60756f2bcfd5ddd22c5f4e31e`) ; l'approbation graphique releve de la porte D7, independante.
- Verdicts autorises, a rendre dans le packet JSON canonique et jamais dans cette vue : `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`.
- Cette vue ne porte aucune decision et ne nomme personne : l'assignation du role reste `PENDING_UNASSIGNED`, l'etat du packet reste `PENDING_UNASSIGNED`.

| Perimetre | Valeur |
| --- | --- |
| Objets du chapitre dans le packet | 148 |
| Empreinte de l'ensemble d'objets | `sha256:129c6e2442c6787ee3f96e1cfe6568bd879542ad9e7b78b876b662c6a7055982` |
| Empreinte semantique liee a l'approbation | `sha256:f92f4ce599c27d295f5108e529d2cb2bbe2071d60756f2bcfd5ddd22c5f4e31e` |
| Empreinte du packet | `sha256:7c667d91390118278c39dac03e21f64c781abde497fc2fb2ceba68de6f6102a2` |
| Revision du depot gelee dans le packet | `836d1ff0d491c68bbe53d845f77a9b84577eb516` |
| Preuve de rendu portee par le packet | `ABSENT` |

## 2. Le chapitre et ses capacites du programme officiel

**Probabilités conditionnelles et indépendance** — programme applicable 2026-2027, MENE2602917A, BO n° 14 du 2026-04-02.
Source officielle : https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A

Situation d'accroche declaree : Un test de depistage detecte correctement 95 \% des personnes malades, mais donne aussi un resultat positif chez 3 \% des personnes saines. Si 1 \% de la population est atteinte, quelle est la probabilite d'etre reellement malade quand le test est positif ? Un probleme qui necessite les probabilites conditionnelles.

Temps estime declare : parcours 1 : 12 h · parcours 2 : 10 h · parcours 3 : 8 h.

| Code | Libelle eleve | Libelle BO | Demonstration exigible |
| --- | --- | --- | --- |
| `C1` | Je sais calculer une probabilite conditionnelle $P_A(B) = P(A \cap B) / P(A)$. | Calculer des probabilités conditionnelles P_A(B). | non |
| `C2` | Je sais construire et lire un arbre pondere. | Construire et exploiter un arbre pondéré. | non |
| `C3` | Je sais appliquer la formule des probabilites totales. | Appliquer la formule des probabilités totales. | oui — Démonstration de la formule des probabilités totales à partir de la partition. |
| `C4` | Je sais determiner si deux evenements sont independants. | Reconnaître et utiliser l'indépendance de deux événements. | non |
| `C5` | Je sais resoudre un probleme contextualise de probabilites conditionnelles. | Résoudre des problèmes contextualisés faisant intervenir des probabilités conditionnelles. | non |

**Attendus officiels rattaches, capacite par capacite**

- `C1` — 2 attendus :
    - `1SPE-OFFICIAL-042` (MANDATORY_SKILL, Automatismes — probabilités) : Calculer des probabilités conditionnelles lorsque les évènements sont présentés sous forme de tableau croisé d’effectifs ou d’arbres pondérés.
    - `1SPE-OFFICIAL-043` (MANDATORY_SKILL, Automatismes — probabilités) : Distinguer P(A ∩ B), PA (B), PB (A).
- `C2` — 2 attendus :
    - `1SPE-OFFICIAL-153` (MANDATORY_KNOWLEDGE, Probabilités conditionnelles et indépendance) : Succession de deux épreuves indépendantes. Représentation par un arbre ou un tableau.
    - `1SPE-OFFICIAL-157` (MANDATORY_CAPACITY, Probabilités conditionnelles et indépendance) : Représenter la succession de deux épreuves indépendantes par un arbre ou un tableau.
- `C3` — 2 attendus :
    - `1SPE-OFFICIAL-152` (MANDATORY_KNOWLEDGE, Probabilités conditionnelles et indépendance) : Partition de l’univers (systèmes complets d’évènements). Formule des probabilités totales.
    - `1SPE-OFFICIAL-155` (MANDATORY_CAPACITY, Probabilités conditionnelles et indépendance) : Dans des cas simples, calculer une probabilité à l’aide de la formule des probabilités totales.
- `C4` — 2 attendus :
    - `1SPE-OFFICIAL-151` (MANDATORY_KNOWLEDGE, Probabilités conditionnelles et indépendance) : Indépendance de deux évènements.
    - `1SPE-OFFICIAL-156` (MANDATORY_CAPACITY, Probabilités conditionnelles et indépendance) : Savoir utiliser ou justifier l’indépendance de deux évènements.
- `C5` : aucun attendu officiel rattache dans `audit/SEMANTIC_ALIGNMENT_LEDGER.json`.

**Prerequis declares par le contrat du chapitre**

| Code | Libelle | Chapitre d'origine |
| --- | --- | --- |
| `R1` | Probabilites de base : vocabulaire, union, intersection, complementaire | 2GT |
| `R2` | Fractions et pourcentages : conversions, operations | 2GT |
| `R3` | Arbres de denombrement | 2GT |
| `R4` | Calcul litteral : mise en equation, resolution | 2GT |
| `R5` | Tableaux de donnees : lecture, frequences, effectifs | 2GT |

## 3. Structure reelle et ordre d'assemblage courant

L'ordre ci-dessous n'est pas l'ordre alphabetique des repertoires : il est lu chez l'assembleur du manuel (`Mathematiques/manuel-maths/scripts/assemble_manuel.py`, `collect_chapter`). C'est la sequence que le lecteur du PDF recoit.

| Rang | Rubrique imprimee | Objets (professeur) |
| --- | --- | --- |
| 1 | Diagnostic | 1 |
| 2 | Cours | 6 |
| 3 | Méthodes | 5 |
| 4 | Exercices | 69 |
| 5 | TD | 2 |
| 6 | Auto-évaluation | 1 |
| 7 | Évaluation | 4 |
| 8 | Remédiation | 10 |
| 9 | Corrigés | 50 |

Total assemble : 148 objets en variante professeur, 96 en variante eleve (la variante eleve exclut les corriges et les corriges d'evaluation).

La page d'ouverture du chapitre est composee par l'assembleur a partir de `contrat.yaml` (titre, capacites, situation d'accroche, temps estime) : elle n'apparait donc pas comme un objet de la sequence.

**Placement des temps pedagogiques dans la progression**

- rang 1 — le diagnostic ouvre le chapitre.
- rang 2 — le cours precede les methodes.
- rang 3 — les methodes sont regroupees avant les exercices.
- rang 4 — les exercices suivent les methodes en un seul bloc.
- rang 5 — le TD est place apres les exercices.
- rang 6 — le QCM d'auto-evaluation suit le TD.
- rang 7 — les evaluations viennent apres le QCM.
- rang 8 — la remediation est placee apres les evaluations.
- rang 9 — les corriges ferment la variante professeur.

Cet ordre est un fait d'assemblage, pas un jugement : sa pertinence pedagogique fait partie de ce que vous evaluez.

## 4. Capacite par capacite : cellules, contributeurs, richesse

`audit/SEMANTIC_ALIGNMENT_LEDGER.json` decoupe le manuel en cellules capacite x role pedagogique. Ce chapitre en porte 35. Elles sont regroupees ici par capacite : une checklist cellule par cellule ne se lit pas.

**Pourquoi ces cellules arrivent chez vous.** Seul le META rattache les corps a une capacite ; l'identite declaree est resolue par egalite exacte, et la couverture de reponses n'etablit qu'une COUVERTURE. Etablir qu'un corps SERT la capacite est un jugement pedagogique, pas un calcul : c'est un resultat terminal, pas une lacune de mesure. C'est pourquoi chaque cellule de ce chapitre est routee vers vous.

Chaque capacite rappelle ensuite ce qui lui est propre : le nombre de cellules, leur disposition, les preuves eventuellement attachees et l'etat de sa richesse.

### Capacite `C1` — « Je sais calculer une probabilite conditionnelle $P_A(B) = P(A \cap B) / P(A)$. »

Libelle BO : Calculer des probabilités conditionnelles P_A(B).

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 10 | `1SPE-PROBCOND-CO-001..010` |
| cours | 3 | `1SPE-PROBCOND-CR-010`, `1SPE-PROBCOND-TD-001..002` |
| evaluations | 2 | `1SPE-PROBCOND-EV-A`, `1SPE-PROBCOND-EV-B` |
| exercices | 10 | `1SPE-PROBCOND-EX-001..010` |
| methodes | 1 | `1SPE-PROBCOND-ME-001` |
| QCM | 4 | `Q1..4` |
| remediation | 1 | `1SPE-PROBCOND-RE-C1` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 4 · remediation : 1 · targeted_practice : 10.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-PROBCOND-EV-A`, `1SPE-PROBCOND-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 5 exercices (8–10 min) — `1SPE-PROBCOND-EX-001..005`
- parcours 2 : 3 exercices (10–12 min) — `1SPE-PROBCOND-EX-006..008`
- parcours 3 : 2 exercices (15–15 min) — `1SPE-PROBCOND-EX-009..010`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C2` — « Je sais construire et lire un arbre pondere. »

Libelle BO : Construire et exploiter un arbre pondéré.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 10 | `1SPE-PROBCOND-CO-011..020` |
| cours | 3 | `1SPE-PROBCOND-CR-011`, `1SPE-PROBCOND-TD-001..002` |
| evaluations | 2 | `1SPE-PROBCOND-EV-A`, `1SPE-PROBCOND-EV-B` |
| exercices | 10 | `1SPE-PROBCOND-EX-011..020` |
| methodes | 1 | `1SPE-PROBCOND-ME-002` |
| QCM | 3 | `Q5..7` |
| remediation | 1 | `1SPE-PROBCOND-RE-C2` |

**Richesse declaree**

- type de capacite : `ATOMIC_SUPPORT` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 10.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-PROBCOND-EV-A`, `1SPE-PROBCOND-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 5 exercices (8–10 min) — `1SPE-PROBCOND-EX-011..015`
- parcours 2 : 3 exercices (12–15 min) — `1SPE-PROBCOND-EX-016..018`
- parcours 3 : 2 exercices (15–15 min) — `1SPE-PROBCOND-EX-019..020`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C3` — « Je sais appliquer la formule des probabilites totales. »

Libelle BO : Appliquer la formule des probabilités totales.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 10 | `1SPE-PROBCOND-CO-021..030` |
| cours | 3 | `1SPE-PROBCOND-CR-012`, `1SPE-PROBCOND-TD-001..002` |
| evaluations | 2 | `1SPE-PROBCOND-EV-A`, `1SPE-PROBCOND-EV-B` |
| exercices | 10 | `1SPE-PROBCOND-EX-021..030` |
| methodes | 1 | `1SPE-PROBCOND-ME-003` |
| QCM | 4 | `Q8..9`, `Q10..11` |
| remediation | 1 | `1SPE-PROBCOND-RE-C3` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 4 · remediation : 1 · targeted_practice : 10.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-PROBCOND-EV-A`, `1SPE-PROBCOND-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 5 exercices (10–12 min) — `1SPE-PROBCOND-EX-021..025`
- parcours 2 : 3 exercices (12–15 min) — `1SPE-PROBCOND-EX-026..028`
- parcours 3 : 2 exercices (15–15 min) — `1SPE-PROBCOND-EX-029..030`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C4` — « Je sais determiner si deux evenements sont independants. »

Libelle BO : Reconnaître et utiliser l'indépendance de deux événements.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 10 | `1SPE-PROBCOND-CO-031..040` |
| cours | 2 | `1SPE-PROBCOND-CR-013`, `1SPE-PROBCOND-TD-002` |
| evaluations | 2 | `1SPE-PROBCOND-EV-A`, `1SPE-PROBCOND-EV-B` |
| exercices | 10 | `1SPE-PROBCOND-EX-031..040` |
| methodes | 1 | `1SPE-PROBCOND-ME-004` |
| QCM | 3 | `Q12..14` |
| remediation | 1 | `1SPE-PROBCOND-RE-C4` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 3 · remediation : 1 · targeted_practice : 10.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-PROBCOND-EV-A`, `1SPE-PROBCOND-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 5 exercices (8–10 min) — `1SPE-PROBCOND-EX-031..035`
- parcours 2 : 3 exercices (12–12 min) — `1SPE-PROBCOND-EX-036..038`
- parcours 3 : 2 exercices (15–15 min) — `1SPE-PROBCOND-EX-039..040`

**Routage de cette capacite vers l'humain**

- les 7 cellules portent `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS`.
- aucun artefact de preuve ne contredit ces cellules, et aucun n'atteste non plus qu'elles soient servies.
- richesse : statut `CANDIDATE_NON_SEMANTIC`, validation semantique `UNKNOWN`.

### Capacite `C5` — « Je sais resoudre un probleme contextualise de probabilites conditionnelles. »

Libelle BO : Résoudre des problèmes contextualisés faisant intervenir des probabilités conditionnelles.

**Roles pedagogiques concernes et objets contributeurs**

| Role pedagogique | Corps rattaches | Objets contributeurs |
| --- | --- | --- |
| corriges | 10 | `1SPE-PROBCOND-CO-041..050` |
| cours | 3 | `1SPE-PROBCOND-CR-014`, `1SPE-PROBCOND-TD-001..002` |
| evaluations | 2 | `1SPE-PROBCOND-EV-A`, `1SPE-PROBCOND-EV-B` |
| exercices | 10 | `1SPE-PROBCOND-EX-041..050` |
| methodes | 1 | `1SPE-PROBCOND-ME-005` |
| QCM | 4 | `Q15..18` |
| remediation | 1 | `1SPE-PROBCOND-RE-C5` |

**Richesse declaree**

- type de capacite : `PROCEDURAL` ; occasions distinctes : 5 ; statut declaratif : `SUFFICIENT`.
- occasions existantes : assessment : 2 · method : 1 · qcm : 4 · remediation : 1 · targeted_practice : 10.
- gestes de raisonnement declares : aucun geste distinct declare ; la diversite du raisonnement est a juger a la lecture.
- evaluee par : `1SPE-PROBCOND-EV-A`, `1SPE-PROBCOND-EV-B`.

**Progression de difficulte declaree**

- parcours 1 : 5 exercices (10–12 min) — `1SPE-PROBCOND-EX-041..045`
- parcours 2 : 3 exercices (15–15 min) — `1SPE-PROBCOND-EX-046..048`
- parcours 3 : 2 exercices (20–20 min) — `1SPE-PROBCOND-EX-049..050`

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
- attendus officiels obligatoires rattaches : 8 sur 8 ; manquants : 0 ; hors annee : 0.
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

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-PROBA-COND/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-PROBA-COND/packet-B-EXPERT_PROGRAMME_PEDAGOGIE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
