# Vue de lecture — Fonctions polynômes du second degré — EXPERT_MATHEMATIQUE

Chapitre `1SPE-SECOND-DEGRE` · manuel `1SPE` (Première, Spécialité mathématiques) · packet A · role `EXPERT_MATHEMATIQUE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-SECOND-DEGRE/packet-A-EXPERT_MATHEMATIQUE.json`
> Etat de revue : `audit/reviews/human/1SPE-SECOND-DEGRE/REVIEW_STATE.json`
> Producteur de cette vue : `scripts/build_human_review_reading_views.py`
>
> Toute divergence entre cette vue et le packet se tranche en faveur du packet. Cette vue ne cree, ne ferme et ne reduit aucune obligation.

## 1. Ce que vous decidez

- L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.
- Aucun humain n'a encore approuve ce chapitre : REVIEW_DELTA_BASELINE = NONE. Le perimetre de revue est le CHAPITRE COURANT ENTIER. Les listes ci-dessous dirigent l'attention, elles ne reduisent pas le perimetre.
- CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST (`sha256:080a729e99ba25e3ac48b7ef480a1ff1b6b37be65945b34aed30ee74c86bb7e9`) ; l'approbation graphique releve de la porte D7, independante.
- Verdicts autorises, a rendre dans le packet JSON canonique et jamais dans cette vue : `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`.
- Cette vue ne porte aucune decision et ne nomme personne : l'assignation du role reste `PENDING_UNASSIGNED`, l'etat du packet reste `PENDING_UNASSIGNED`.

| Perimetre | Valeur |
| --- | --- |
| Objets du chapitre dans le packet | 152 |
| Empreinte de l'ensemble d'objets | `sha256:e4a5653a775bdf85a7ed42d96f50810dd2d955883f36f7823c205a775f79d8a8` |
| Empreinte semantique liee a l'approbation | `sha256:080a729e99ba25e3ac48b7ef480a1ff1b6b37be65945b34aed30ee74c86bb7e9` |
| Empreinte du packet | `sha256:33804e4cdbf7cf5e4622669ff00494840789d2f2597775d439bfc9abf99017d0` |
| Revision du depot gelee dans le packet | `836d1ff0d491c68bbe53d845f77a9b84577eb516` |
| Preuve de rendu portee par le packet | `ABSENT` |

## 2. Le chapitre et ses capacites du programme officiel

**Fonctions polynômes du second degré** — programme applicable 2026-2027, MENE2602917A, BO n° 14 du 2026-04-02.
Source officielle : https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A

Situation d'accroche declaree : Un artisan fabrique des boites en carton en decoupant des carres aux coins d'une feuille rectangulaire. Quel cote de carre maximise le volume de la boite ? Un probleme d'optimisation qui se ramene a l'etude d'un polynome du second degre.

Temps estime declare : parcours 1 : 12 h · parcours 2 : 10 h · parcours 3 : 8 h.

| Code | Libelle eleve | Libelle BO | Demonstration exigible |
| --- | --- | --- | --- |
| `C1` | Je sais reconnaitre un polynome du second degre et passer d'une forme a une autre. | Determiner les fonctions polynomes du second degre definies sur R. Reconnaitre la forme developpee, factorisee et canonique. | non |
| `C2` | Je sais determiner le sommet, l'axe de symetrie et dresser le tableau de variations. | Determiner l'axe de symetrie et le sommet de la parabole. Dresser le tableau de variations de la fonction polynome du second degre. | non |
| `C3` | Je sais calculer le discriminant et resoudre une equation du second degre. | Calculer le discriminant d'une equation du second degre. Determiner les solutions reelles selon le signe du discriminant. | oui — Etablissement des formules donnant les solutions d'une equation du second degre. |
| `C4` | Je sais factoriser un trinome et etudier son signe. | Factoriser, si possible, un polynome du second degre. Determiner le signe d'un polynome du second degre a partir de ses racines ou du discriminant. | non |
| `C5` | Je sais resoudre une inequation du second degre. | Resoudre une inequation du second degre. Resoudre une equation ou inequation se ramenant au second degre. | non |
| `C6` | Je sais modeliser un probleme concret par un polynome du second degre et trouver un optimum. | Modeliser un probleme a l'aide d'une fonction polynome du second degre. Problemes d'optimisation. | non |

**Attendus officiels rattaches, capacite par capacite**

- `C1` — 1 attendu :
    - `1SPE-OFFICIAL-074` (MANDATORY_CAPACITY, Équations, fonctions polynômes du second degré) : Choisir une forme adaptée (développée réduite, canonique, factorisée) d’une fonction polynôme du second degré dans le cadre de la résolution d’un problème (équation, inéquation, optimisation, variations).
- `C2` : aucun attendu officiel rattache dans `audit/SEMANTIC_ALIGNMENT_LEDGER.json`.
- `C3` — 2 attendus :
    - `1SPE-OFFICIAL-070` (MANDATORY_KNOWLEDGE, Équations, fonctions polynômes du second degré) : Forme canonique d’une fonction polynôme du second degré. Discriminant. Factorisation éventuelle. Résolution d’une équation du second degré. Signe.
    - `1SPE-OFFICIAL-075` (MANDATORY_SKILL, Équations, fonctions polynômes du second degré) : Résolution de l’équation du second degré.
- `C4` — 7 attendus :
    - `1SPE-OFFICIAL-031` (MANDATORY_SKILL, Automatismes — calcul numérique et algébrique) : Déterminer les solutions d’une équation produit nul.
    - `1SPE-OFFICIAL-032` (MANDATORY_SKILL, Automatismes — calcul numérique et algébrique) : Déterminer le signe d’une expression du premier degré, d’une expression factorisée du second degré.
    - `1SPE-OFFICIAL-033` (MANDATORY_SKILL, Automatismes — calcul numérique et algébrique) : Développer, factoriser, réduire une expression algébrique simple.
    - `1SPE-OFFICIAL-069` (MANDATORY_KNOWLEDGE, Équations, fonctions polynômes du second degré) : Fonction polynôme du second degré donnée sous forme factorisée. Racines, signe, expression de la somme et du produit des racines.
    - `1SPE-OFFICIAL-071` (MANDATORY_CAPACITY, Équations, fonctions polynômes du second degré) : Étudier le signe d’une fonction polynôme du second degré donnée sous forme factorisée.
    - `1SPE-OFFICIAL-072` (MANDATORY_CAPACITY, Équations, fonctions polynômes du second degré) : Déterminer les fonctions polynômes du second degré s’annulant en deux nombres réels distincts.
    - `1SPE-OFFICIAL-073` (MANDATORY_CAPACITY, Équations, fonctions polynômes du second degré) : Factoriser une fonction polynôme du second degré, en diversifiant les stratégies : racine évidente, détection des racines par leur somme et leur produit, identité remarquable, application des formules générales.
- `C5` : aucun attendu officiel rattache dans `audit/SEMANTIC_ALIGNMENT_LEDGER.json`.
- `C6` : aucun attendu officiel rattache dans `audit/SEMANTIC_ALIGNMENT_LEDGER.json`.

**Prerequis declares par le contrat du chapitre**

| Code | Libelle | Chapitre d'origine |
| --- | --- | --- |
| `R1` | Calcul litteral : developper, factoriser, identites remarquables | 2GT |
| `R2` | Equations du premier degre et produit nul | 2GT |
| `R3` | Fonctions : image, antecedent, courbe representative | 2GT |
| `R4` | Fonctions de reference : carre, inverse | 2GT |
| `R5` | Inegalites : regles de calcul, tableau de signes | 2GT |

## 3. Structure reelle et ordre d'assemblage courant

L'ordre ci-dessous n'est pas l'ordre alphabetique des repertoires : il est lu chez l'assembleur du manuel (`Mathematiques/manuel-maths/scripts/assemble_manuel.py`, `collect_chapter`). C'est la sequence que le lecteur du PDF recoit.

| Rang | Rubrique imprimee | Objets (professeur) |
| --- | --- | --- |
| 1 | Ouverture | 1 |
| 2 | Diagnostic | 1 |
| 3 | Cours | 6 |
| 4 | Méthodes | 6 |
| 5 | Exercices | 70 |
| 6 | TD | 2 |
| 7 | Auto-évaluation | 1 |
| 8 | Évaluation | 4 |
| 9 | Remédiation | 11 |
| 10 | Corrigés | 50 |

Total assemble : 152 objets en variante professeur, 100 en variante eleve (la variante eleve exclut les corriges et les corriges d'evaluation).

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

21 objets pour ce chapitre, regroupes par famille scientifique — la capacite du referentiel du depot, avec son libelle BO — puis par type d'objet.

### Famille `C1` — Determiner les fonctions polynomes du second degre definies sur R. Reconnaitre la forme developpee, factorisee et canonique.

Capacite eleve : « Je sais reconnaitre un polynome du second degre et passer d'une forme a une autre. »

4 objets · 59 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 3 objets, 3 affirmations a verifier :
    - `1SPE-SECDEG-EX-001-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-001-CDP.tex`
    - `1SPE-SECDEG-EX-002-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-002-CDP.tex`
    - `1SPE-SECDEG-EX-043-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-043-CDP.tex`
- **`cours`** — 1 objet, 56 affirmations a verifier :
    - `1SPE-SECDEG-CR-010` (56 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/cours/10_C1_formes_trinome.tex`

### Famille `C2` — Determiner l'axe de symetrie et le sommet de la parabole. Dresser le tableau de variations de la fonction polynome du second degre.

Capacite eleve : « Je sais determiner le sommet, l'axe de symetrie et dresser le tableau de variations. »

2 objets · 39 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 1 objet, 1 affirmation a verifier :
    - `1SPE-SECDEG-EX-006-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-006-CDP.tex`
- **`cours`** — 1 objet, 38 affirmations a verifier :
    - `1SPE-SECDEG-CR-011` (38 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/cours/11_C2_parabole_variations.tex`

### Famille `C3` — Calculer le discriminant d'une equation du second degre. Determiner les solutions reelles selon le signe du discriminant.

Capacite eleve : « Je sais calculer le discriminant et resoudre une equation du second degre. »

4 objets · 58 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 3 objets, 7 affirmations a verifier :
    - `1SPE-SECDEG-EX-007-CDP` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-007-CDP.tex`
    - `1SPE-SECDEG-EX-008-CDP` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-008-CDP.tex`
    - `1SPE-SECDEG-EX-009-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-009-CDP.tex`
- **`cours`** — 1 objet, 51 affirmations a verifier :
    - `1SPE-SECDEG-CR-012` (51 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/cours/12_C3_discriminant.tex`

### Famille `C4` — Factoriser, si possible, un polynome du second degre. Determiner le signe d'un polynome du second degre a partir de ses racines ou du discriminant.

Capacite eleve : « Je sais factoriser un trinome et etudier son signe. »

4 objets · 51 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 3 objets, 10 affirmations a verifier :
    - `1SPE-SECDEG-EX-011-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-011-CDP.tex`
    - `1SPE-SECDEG-EX-012-CDP` (4 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-012-CDP.tex`
    - `1SPE-SECDEG-EX-044-CDP` (5 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-044-CDP.tex`
- **`cours`** — 1 objet, 41 affirmations a verifier :
    - `1SPE-SECDEG-CR-013` (41 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/cours/13_C4_factorisation_signe.tex`

### Famille `C5` — Resoudre une inequation du second degre. Resoudre une equation ou inequation se ramenant au second degre.

Capacite eleve : « Je sais resoudre une inequation du second degre. »

2 objets · 48 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 1 objet, 2 affirmations a verifier :
    - `1SPE-SECDEG-EX-015-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-015-CDP.tex`
- **`cours`** — 1 objet, 46 affirmations a verifier :
    - `1SPE-SECDEG-CR-014` (46 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/cours/14_C5_inequations.tex`

### Famille `C6` — Modeliser un probleme a l'aide d'une fonction polynome du second degre. Problemes d'optimisation.

Capacite eleve : « Je sais modeliser un probleme concret par un polynome du second degre et trouver un optimum. »

4 objets · 28 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 3 objets, 5 affirmations a verifier :
    - `1SPE-SECDEG-EX-016-CDP` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-016-CDP.tex`
    - `1SPE-SECDEG-EX-017-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-017-CDP.tex`
    - `1SPE-SECDEG-EX-018-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-018-CDP.tex`
- **`cours`** — 1 objet, 23 affirmations a verifier :
    - `1SPE-SECDEG-CR-015` (23 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/cours/15_C6_optimisation.tex`

### Famille `CAPACITE_NON_DECLAREE_PAR_L_OBJET`

Objets dont ni le META ni l'exercice servi ne declare de capacite du chapitre. Rien n'est devine ici : la famille reste a etablir par lecture.

1 objet · 3 affirmations calculables sans preuve machine.

- **`cours`** — 1 objet, 3 affirmations a verifier :
    - `1SPE-SECDEG-CR-000` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/cours/00_ouverture.tex`

## 5. Question de QCM routee vers l'humain

Aucune question de ce chapitre n'est routee vers une revue humaine par `audit/QCM_INDEPENDENT_EVIDENCE_V2.json`.

## 6. Ce que la machine a deja etabli, et ce qu'elle n'etablit pas

Ces mesures viennent de `audit/PUBLISH_READINESS_CHAPTER_MATRIX.json`. Elles ne reduisent pas le perimetre de votre lecture : une dimension `COMPLETE` signifie que la machine a fini de mesurer, pas que le contenu est juste.

| Mesure | Valeur |
| --- | --- |
| Etat machine vertical | `MACHINE_REVIEW_COMPLETE` |
| Cloture humaine | `PENDING` |
| Objets passes par l'oracle | 118 reussites, 0 echecs, 22 en science humaine requise, 28 en revue manuelle |
| Attendus officiels obligatoires | 10 rattaches sur 10, 0 manquants, 0 hors annee |
| Sujets d'evaluation | 2 sujets, 2 corriges, statut `COMPLETE` |
| QCM | 18 questions, capacites evaluees C1, C2, C3, C4, C5, C6 |
| Relation exercice/corrige | ANSWER_COVERAGE_ESTABLISHED : 50 ; 0 echecs de cardinalite |

La relation exercice/corrige n'est etablie que structurellement : une COUVERTURE de reponses n'atteste pas qu'un corrige corrige bien son exercice. Cette fidelite est un point de votre checklist.

Dettes de revue declarees pour ce chapitre :

- `UNCHANGED` — 153 unites, categorie `OBJECT_REVIEW`, bloquant : oui.

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

Ces instantanes sont declares `STALE_UNDECIDED` dans `audit/PDF_ARTIFACT_REGISTRY.yaml` : ils ne sont pas garantis identiques au contenu courant. Le candidat d'impression courant se reconstruit par `python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py --manual 1SPE --variant <variant>` (recu : `audit/1SPE_PRINT_CANDIDATE_BUILD_RECEIPT.json`, statut `PRINT_CANDIDATE`).

Rappel du recu : Ces PDF ne sont PAS finals : aucun 1SPE_FINAL_CONTENT_SHA n'est fige, les deux revues humaines et D7 restent PENDING.

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-SECOND-DEGRE/packet-A-EXPERT_MATHEMATIQUE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
