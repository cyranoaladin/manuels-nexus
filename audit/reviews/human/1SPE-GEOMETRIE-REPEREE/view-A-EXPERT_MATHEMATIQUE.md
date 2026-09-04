# Vue de lecture — Géométrie repérée — EXPERT_MATHEMATIQUE

Chapitre `1SPE-GEOMETRIE-REPEREE` · manuel `1SPE` (Première, Spécialité mathématiques) · packet A · role `EXPERT_MATHEMATIQUE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-GEOMETRIE-REPEREE/packet-A-EXPERT_MATHEMATIQUE.json`
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
| Empreinte du packet | `sha256:64a0d0be0b35f5c4eed8eb2e648f3b96e84a340e0def79095053527208f94cf8` |
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

## 4. Points d'attention scientifiques, par famille

Le registre `audit/1SPE_MANUAL_REVIEW_DISPOSITION_LEDGER.json` classe chaque objet du manuel. Ceux qui portent la disposition `SCIENCE_HUMAINE_REQUISE` contiennent des affirmations calculables qu'aucune preuve machine n'etablit : ce sont eux que la lecture scientifique doit atteindre en priorite.

12 objets pour ce chapitre, regroupes par famille scientifique — la capacite du referentiel du depot, avec son libelle BO — puis par type d'objet.

### Famille `C1` — Déterminer une équation cartésienne d'une droite dans le plan repéré.

Capacite eleve : « Je sais déterminer une équation cartésienne d'une droite ax+by+c=0 et l'exploiter. »

2 objets · 36 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 1 objet, 1 affirmation a verifier :
    - `1SPE-GEOREP-EX-003-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-003-CDP.tex`
- **`cours`** — 1 objet, 35 affirmations a verifier :
    - `1SPE-GEOREP-CR-010` (35 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-GEOMETRIE-REPEREE/cours/10_C1_equation_cartesienne_droite.tex`

### Famille `C2` — Utiliser un vecteur normal à une droite pour déterminer son équation.

Capacite eleve : « Je sais utiliser un vecteur normal à une droite, passer d'une équation cartésienne à un vecteur directeur/normal et réciproquement. »

3 objets · 21 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 2 objets, 2 affirmations a verifier :
    - `1SPE-GEOREP-EX-011-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-011-CDP.tex`
    - `1SPE-GEOREP-EX-012-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-012-CDP.tex`
- **`cours`** — 1 objet, 19 affirmations a verifier :
    - `1SPE-GEOREP-CR-011` (19 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-GEOMETRIE-REPEREE/cours/11_C2_vecteur_normal.tex`

### Famille `C3` — Déterminer une équation du cercle de centre (a,b) et de rayon r.

Capacite eleve : « Je sais déterminer et exploiter l'équation d'un cercle (x-a)²+(y-b)²=r². »

3 objets · 37 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 2 objets, 2 affirmations a verifier :
    - `1SPE-GEOREP-EX-021-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-021-CDP.tex`
    - `1SPE-GEOREP-EX-023-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-023-CDP.tex`
- **`cours`** — 1 objet, 35 affirmations a verifier :
    - `1SPE-GEOREP-CR-012` (35 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-GEOMETRIE-REPEREE/cours/12_C3_equation_cercle.tex`

### Famille `C4` — Étudier les positions relatives de droites et cercles (parallélisme, intersection, tangence).

Capacite eleve : « Je sais étudier les positions relatives de droites et de cercles (parallélisme, intersection, tangence). »

2 objets · 33 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 1 objet, 1 affirmation a verifier :
    - `1SPE-GEOREP-EX-033-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-GEOMETRIE-REPEREE/exercices/1SPE-GEOREP-EX-033-CDP.tex`
- **`cours`** — 1 objet, 32 affirmations a verifier :
    - `1SPE-GEOREP-CR-013` (32 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-GEOMETRIE-REPEREE/cours/13_C4_positions_relatives.tex`

### Famille `C5` — Résoudre des problèmes de géométrie plane dans un repère orthonormé.

Capacite eleve : « Je sais résoudre des problèmes géométriques dans un repère orthonormé. »

1 objet · 12 affirmations calculables sans preuve machine.

- **`cours`** — 1 objet, 12 affirmations a verifier :
    - `1SPE-GEOREP-CR-014` (12 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-GEOMETRIE-REPEREE/cours/14_C5_problemes_repere.tex`

### Famille `CAPACITE_NON_DECLAREE_PAR_L_OBJET`

Objets dont ni le META ni l'exercice servi ne declare de capacite du chapitre. Rien n'est devine ici : la famille reste a etablir par lecture.

1 objet · 2 affirmations calculables sans preuve machine.

- **`cours`** — 1 objet, 2 affirmations a verifier :
    - `1SPE-GEOREP-COURS-00` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-GEOMETRIE-REPEREE/cours/00_ouverture.tex`

## 5. Question de QCM routee vers l'humain

Aucune question de ce chapitre n'est routee vers une revue humaine par `audit/QCM_INDEPENDENT_EVIDENCE_V2.json`.

## 6. Ce que la machine a deja etabli, et ce qu'elle n'etablit pas

Ces mesures viennent de `audit/PUBLISH_READINESS_CHAPTER_MATRIX.json`. Elles ne reduisent pas le perimetre de votre lecture : une dimension `COMPLETE` signifie que la machine a fini de mesurer, pas que le contenu est juste.

| Mesure | Valeur |
| --- | --- |
| Etat machine vertical | `MACHINE_REVIEW_COMPLETE` |
| Cloture humaine | `PENDING` |
| Objets passes par l'oracle | 117 reussites, 0 echecs, 13 en science humaine requise, 25 en revue manuelle |
| Attendus officiels obligatoires | 9 rattaches sur 9, 0 manquants, 0 hors annee |
| Sujets d'evaluation | 2 sujets, 2 corriges, statut `COMPLETE` |
| QCM | 15 questions, capacites evaluees C1, C2, C3, C4, C5 |
| Relation exercice/corrige | ANSWER_COVERAGE_ESTABLISHED : 50 ; 0 echecs de cardinalite |

La relation exercice/corrige n'est etablie que structurellement : une COUVERTURE de reponses n'atteste pas qu'un corrige corrige bien son exercice. Cette fidelite est un point de votre checklist.

Dettes de revue declarees pour ce chapitre :

- `UNCHANGED` — 148 unites, categorie `OBJECT_REVIEW`, bloquant : oui.

## 7. Checklist du role `EXPERT_MATHEMATIQUE`

1. exactitude scientifique
2. hypotheses
3. definitions
4. notations
5. demonstrations et raisonnements
6. calculs
7. fidelite exercice/corrige
8. verite des QCM
9. verite des evaluations
10. items de science humaine requise
11. concepts d'une autre annee

Cette checklist est celle du role. Elle s'applique au CHAPITRE COURANT ENTIER, y compris aux objets qu'aucune section de cette vue ne cite.

## 8. Reference de lecture : le PDF candidat

Le PDF sert a lire le chapitre dans l'ordre ou l'eleve le recevra. Il n'est pas une preuve : le packet ne porte aucune preuve de rendu (`render_evidence = ABSENT`), et aucun index page-objet n'est etabli.

| Fichier | Variante | Pages | Role declare | Etat declare |
| --- | --- | --- | --- | --- |
| `MANUELS_PDF_PUBLICATION/01_Maths_1re_Spe_Eleve.pdf` | eleve | 371 | HISTORICAL_PUBLICATION_SNAPSHOT | STALE_UNDECIDED |
| `MANUELS_PDF_PUBLICATION/02_Maths_1re_Spe_Professeur.pdf` | professeur | 617 | HISTORICAL_PUBLICATION_SNAPSHOT | STALE_UNDECIDED |

Ces instantanes sont declares `STALE_UNDECIDED` dans `audit/PDF_ARTIFACT_REGISTRY.yaml` : ils ne sont pas garantis identiques au contenu courant. Le candidat d'impression courant se reconstruit par `python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py --manual 1SPE --variant <variant> --record-observed` (recu : `audit/1SPE_PRINT_CANDIDATE_BUILD_RECEIPT.json`, statut `PRINT_CANDIDATE`).

Rappel du recu : Ces PDF ne sont pas finals : aucun 1SPE_FINAL_CONTENT_SHA n'est figé, les deux revues humaines par chapitre et le dossier D7 restent en attente.

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-GEOMETRIE-REPEREE/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-GEOMETRIE-REPEREE/packet-A-EXPERT_MATHEMATIQUE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
