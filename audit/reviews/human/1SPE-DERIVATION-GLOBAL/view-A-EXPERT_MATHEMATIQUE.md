# Vue de lecture — Dérivation : applications aux variations — EXPERT_MATHEMATIQUE

Chapitre `1SPE-DERIVATION-GLOBAL` · manuel `1SPE` (Première, Spécialité mathématiques) · packet A · role `EXPERT_MATHEMATIQUE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-DERIVATION-GLOBAL/packet-A-EXPERT_MATHEMATIQUE.json`
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
| Empreinte du packet | `sha256:c4d8fde8c6ca8bc5a7b3ddb3abb84600d7f950453827344e3c8bb0630069a4c5` |
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

## 4. Points d'attention scientifiques, par famille

Le registre `audit/1SPE_MANUAL_REVIEW_DISPOSITION_LEDGER.json` classe chaque objet du manuel. Ceux qui portent la disposition `SCIENCE_HUMAINE_REQUISE` contiennent des affirmations calculables qu'aucune preuve machine n'etablit : ce sont eux que la lecture scientifique doit atteindre en priorite.

7 objets pour ce chapitre, regroupes par famille scientifique — la capacite du referentiel du depot, avec son libelle BO — puis par type d'objet.

### Famille `C2` — Calculer la dérivée d'une somme, d'un produit par un réel, d'un produit, d'un quotient de fonctions dérivables.

Capacite eleve : « Je sais utiliser les règles de dérivation (somme, produit, quotient). »

1 objet · 42 affirmations calculables sans preuve machine.

- **`cours`** — 1 objet, 42 affirmations a verifier :
    - `1SPE-DERGLOBAL-COURS-C2` (42 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/cours/11_C2_regles_derivation.tex`

### Famille `C4` — Déterminer les extremums d'une fonction polynôme de degré 3.

Capacite eleve : « Je sais trouver les extremums d'une fonction en annulant sa dérivée. »

5 objets · 32 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 4 objets, 4 affirmations a verifier :
    - `1SPE-DERGLOBAL-EX-031-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-031-CDP.tex`
    - `1SPE-DERGLOBAL-EX-032-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-032-CDP.tex`
    - `1SPE-DERGLOBAL-EX-033-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-033-CDP.tex`
    - `1SPE-DERGLOBAL-EX-034-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/exercices/1SPE-DERGLOBAL-EX-034-CDP.tex`
- **`cours`** — 1 objet, 28 affirmations a verifier :
    - `1SPE-DERGLOBAL-COURS-C4` (28 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/cours/13_C4_extremums.tex`

### Famille `C5` — Résoudre un problème d'optimisation.

Capacite eleve : « Je sais modéliser et résoudre un problème d'optimisation à l'aide de la dérivation. »

1 objet · 28 affirmations calculables sans preuve machine.

- **`cours`** — 1 objet, 28 affirmations a verifier :
    - `1SPE-DERGLOBAL-COURS-C5` (28 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/cours/14_C5_optimisation.tex`

## 5. Question de QCM routee vers l'humain

Aucune question de ce chapitre n'est routee vers une revue humaine par `audit/QCM_INDEPENDENT_EVIDENCE_V2.json`.

## 6. Ce que la machine a deja etabli, et ce qu'elle n'etablit pas

Ces mesures viennent de `audit/PUBLISH_READINESS_CHAPTER_MATRIX.json`. Elles ne reduisent pas le perimetre de votre lecture : une dimension `COMPLETE` signifie que la machine a fini de mesurer, pas que le contenu est juste.

| Mesure | Valeur |
| --- | --- |
| Etat machine vertical | `MACHINE_REVIEW_COMPLETE` |
| Cloture humaine | `PENDING` |
| Objets passes par l'oracle | 124 reussites, 0 echecs, 8 en science humaine requise, 22 en revue manuelle |
| Attendus officiels obligatoires | 16 rattaches sur 16, 0 manquants, 0 hors annee |
| Sujets d'evaluation | 2 sujets, 2 corriges, statut `COMPLETE` |
| QCM | 15 questions, capacites evaluees C1, C2, C3, C4, C5 |
| Relation exercice/corrige | ANSWER_COVERAGE_ESTABLISHED : 53 ; 0 echecs de cardinalite |

La relation exercice/corrige n'est etablie que structurellement : une COUVERTURE de reponses n'atteste pas qu'un corrige corrige bien son exercice. Cette fidelite est un point de votre checklist.

Dettes de revue declarees pour ce chapitre :

- `UNCHANGED` — 152 unites, categorie `OBJECT_REVIEW`, bloquant : oui.

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

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-DERIVATION-GLOBAL/packet-A-EXPERT_MATHEMATIQUE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
