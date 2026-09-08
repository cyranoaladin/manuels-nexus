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
| Revision du depot gelee dans le packet | `dfc99058e7a7c16ae4af46b99245edbe14b4f8e5` |
| Preuve de rendu portee par le packet | `ABSENT` |

## 2. Le chapitre et ses capacites du programme officiel

**Fonctions polynômes du second degré** — programme applicable 2026-2027, MENE2602917A, BO n° 14 du 2026-04-02.
Source officielle : https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A

Situation d'accroche declaree : Un artisan fabrique des boites en carton en decoupant des carres aux coins d'une feuille rectangulaire. Quel cote de carre maximise le volume de la boite ? Un probleme d'optimisation qui se ramene a l'etude d'un polynome du second degre.

Temps estime declare : parcours 1 : 12 h · parcours 2 : 10 h · parcours 3 : 8 h.

| Code | Libelle eleve | Libelle BO | Demonstration exigible |
| --- | --- | --- | --- |
| `C1` | Je sais reconnaitre un polynome du second degre et passer d'une forme a une autre. | Choisir une forme adaptée (développée réduite, canonique, factorisée) d’une fonction polynôme du second degré dans le cadre de la résolution d’un problème (équation, inéquation, optimisation, variations). | non |
| `C2` | Je sais determiner le sommet, l'axe de symetrie et dresser le tableau de variations. | aucun libelle BO : le referentiel du depot ne declare pas cette capacite | non |
| `C3` | Je sais calculer le discriminant et resoudre une equation du second degre. | Résolution de l’équation du second degré. | oui |
| `C4` | Je sais factoriser un trinome en diversifiant les strategies. | Factoriser une fonction polynôme du second degré, en diversifiant les stratégies : racine évidente, détection des racines par leur somme et leur produit, identité remarquable, application des formules générales. | non |
| `C8` | Je sais etudier le signe d'un polynome du second degre donne sous forme factorisee. | Étudier le signe d’une fonction polynôme du second degré donnée sous forme factorisée. | non |
| `C5` | Je sais resoudre une inequation du second degre. | aucun libelle BO : le referentiel du depot ne declare pas cette capacite | non |
| `C6` | Je sais modeliser un probleme concret par un polynome du second degre et trouver un optimum. | aucun libelle BO : le referentiel du depot ne declare pas cette capacite | non |
| `C7` | Je sais determiner les fonctions polynomes du second degre s'annulant en deux nombres reels distincts, en utilisant la somme et le produit des racines. | Déterminer les fonctions polynômes du second degré s’annulant en deux nombres réels distincts. | non |

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
- `C8` : aucun attendu officiel rattache dans `audit/SEMANTIC_ALIGNMENT_LEDGER.json`.
- `C5` : aucun attendu officiel rattache dans `audit/SEMANTIC_ALIGNMENT_LEDGER.json`.
- `C6` : aucun attendu officiel rattache dans `audit/SEMANTIC_ALIGNMENT_LEDGER.json`.
- `C7` : aucun attendu officiel rattache dans `audit/SEMANTIC_ALIGNMENT_LEDGER.json`.

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
| 3 | Cours | 7 |
| 4 | Méthodes | 8 |
| 5 | Exercices | 72 |
| 6 | TD | 2 |
| 7 | Auto-évaluation | 1 |
| 8 | Évaluation | 4 |
| 9 | Remédiation | 13 |
| 10 | Corrigés | 52 |

Total assemble : 161 objets en variante professeur, 107 en variante eleve (la variante eleve exclut les corriges et les corriges d'evaluation).

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

20 objets pour ce chapitre, regroupes par famille scientifique — la capacite du referentiel du depot, avec son libelle BO — puis par type d'objet.

### Famille `C1` — Choisir une forme adaptée (développée réduite, canonique, factorisée) d’une fonction polynôme du second degré dans le cadre de la résolution d’un problème (équation, inéquation, optimisation, variations).

Capacite eleve : « Je sais reconnaitre un polynome du second degre et passer d'une forme a une autre. »

4 objets · 27 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 3 objets, 3 affirmations a verifier :
    - `1SPE-SECDEG-EX-001-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-001-CDP.tex`
    - `1SPE-SECDEG-EX-002-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-002-CDP.tex`
    - `1SPE-SECDEG-EX-043-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-043-CDP.tex`
- **`methode`** — 1 objet, 24 affirmations a verifier :
    - `1SPE-SECDEG-ME-001` (24 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/methodes/1SPE-SECDEG-ME-001.tex`

### Famille `C2` — Je sais determiner le sommet, l'axe de symetrie et dresser le tableau de variations.

Capacite eleve : « Je sais determiner le sommet, l'axe de symetrie et dresser le tableau de variations. »

2 objets · 28 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 1 objet, 1 affirmation a verifier :
    - `1SPE-SECDEG-EX-006-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-006-CDP.tex`
- **`methode`** — 1 objet, 27 affirmations a verifier :
    - `1SPE-SECDEG-ME-002` (27 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/methodes/1SPE-SECDEG-ME-002.tex`

### Famille `C3` — Résolution de l’équation du second degré.

Capacite eleve : « Je sais calculer le discriminant et resoudre une equation du second degre. »

4 objets · 37 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 3 objets, 7 affirmations a verifier :
    - `1SPE-SECDEG-EX-007-CDP` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-007-CDP.tex`
    - `1SPE-SECDEG-EX-008-CDP` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-008-CDP.tex`
    - `1SPE-SECDEG-EX-009-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-009-CDP.tex`
- **`methode`** — 1 objet, 30 affirmations a verifier :
    - `1SPE-SECDEG-ME-003` (30 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/methodes/1SPE-SECDEG-ME-003.tex`

### Famille `C4` — Factoriser une fonction polynôme du second degré, en diversifiant les stratégies : racine évidente, détection des racines par leur somme et leur produit, identité remarquable, application des formules générales.

Capacite eleve : « Je sais factoriser un trinome en diversifiant les strategies. »

4 objets · 44 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 3 objets, 10 affirmations a verifier :
    - `1SPE-SECDEG-EX-011-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-011-CDP.tex`
    - `1SPE-SECDEG-EX-012-CDP` (4 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-012-CDP.tex`
    - `1SPE-SECDEG-EX-044-CDP` (5 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-044-CDP.tex`
- **`methode`** — 1 objet, 34 affirmations a verifier :
    - `1SPE-SECDEG-ME-004` (34 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/methodes/1SPE-SECDEG-ME-004.tex`

### Famille `C5` — Je sais resoudre une inequation du second degre.

Capacite eleve : « Je sais resoudre une inequation du second degre. »

2 objets · 35 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 1 objet, 2 affirmations a verifier :
    - `1SPE-SECDEG-EX-015-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-015-CDP.tex`
- **`methode`** — 1 objet, 33 affirmations a verifier :
    - `1SPE-SECDEG-ME-005` (33 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/methodes/1SPE-SECDEG-ME-005.tex`

### Famille `C6` — Je sais modeliser un probleme concret par un polynome du second degre et trouver un optimum.

Capacite eleve : « Je sais modeliser un probleme concret par un polynome du second degre et trouver un optimum. »

4 objets · 26 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 3 objets, 5 affirmations a verifier :
    - `1SPE-SECDEG-EX-016-CDP` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-016-CDP.tex`
    - `1SPE-SECDEG-EX-017-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-017-CDP.tex`
    - `1SPE-SECDEG-EX-018-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/exercices/1SPE-SECDEG-EX-018-CDP.tex`
- **`methode`** — 1 objet, 21 affirmations a verifier :
    - `1SPE-SECDEG-ME-006` (21 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/methodes/1SPE-SECDEG-ME-006.tex`

## 5. Question de QCM routee vers l'humain

Aucune question de ce chapitre n'est routee vers une revue humaine par `audit/QCM_INDEPENDENT_EVIDENCE_V2.json`.

## 6. Ce que la machine a deja etabli, et ce qu'elle n'etablit pas

Ces mesures viennent de `audit/PUBLISH_READINESS_CHAPTER_MATRIX.json`. Elles ne reduisent pas le perimetre de votre lecture : une dimension `COMPLETE` signifie que la machine a fini de mesurer, pas que le contenu est juste.

| Mesure | Valeur |
| --- | --- |
| Etat machine vertical | `MACHINE_REVIEW_COMPLETE` |
| Cloture humaine | `PENDING` |
| Objets passes par l'oracle | 130 reussites, 0 echecs, 21 en science humaine requise, 27 en revue manuelle |
| Attendus officiels obligatoires | 10 rattaches sur 10, 0 manquants, 0 hors annee |
| Sujets d'evaluation | 2 sujets, 2 corriges, statut `COMPLETE` |
| QCM | 20 questions, capacites evaluees C1, C2, C3, C4, C5, C6, C7, C8 |
| Relation exercice/corrige | ANSWER_COVERAGE_ESTABLISHED : 52 ; 0 echecs de cardinalite |

La relation exercice/corrige n'est etablie que structurellement : une COUVERTURE de reponses n'atteste pas qu'un corrige corrige bien son exercice. Cette fidelite est un point de votre checklist.

Dettes de revue declarees pour ce chapitre :

- `SECOND_DEGRE_C7_AUTHORED_REVIEW_DEBT_5` — 5 unites, categorie `OBJECT_REVIEW`, bloquant : oui.
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

Ces instantanes sont declares `STALE_UNDECIDED` dans `audit/PDF_ARTIFACT_REGISTRY.yaml` : ils ne sont pas garantis identiques au contenu courant. Le candidat d'impression courant se reconstruit par `python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py --manual 1SPE --variant <variant> --record-observed` (recu : `audit/1SPE_PRINT_CANDIDATE_BUILD_RECEIPT.json`, statut `PRINT_CANDIDATE`).

Rappel du recu : Ces PDF ne sont pas finals : aucun 1SPE_FINAL_CONTENT_SHA n'est figé, les deux revues humaines par chapitre et le dossier D7 restent en attente.

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-SECOND-DEGRE/packet-A-EXPERT_MATHEMATIQUE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
