# Vue de lecture — Suites numériques — EXPERT_MATHEMATIQUE

Chapitre `1SPE-SUITES` · manuel `1SPE` (Première, Spécialité mathématiques) · packet A · role `EXPERT_MATHEMATIQUE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-SUITES/packet-A-EXPERT_MATHEMATIQUE.json`
> Etat de revue : `audit/reviews/human/1SPE-SUITES/REVIEW_STATE.json`
> Producteur de cette vue : `scripts/build_human_review_reading_views.py`
>
> Toute divergence entre cette vue et le packet se tranche en faveur du packet. Cette vue ne cree, ne ferme et ne reduit aucune obligation.

## 1. Ce que vous decidez

- L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.
- Aucun humain n'a encore approuve ce chapitre : REVIEW_DELTA_BASELINE = NONE. Le perimetre de revue est le CHAPITRE COURANT ENTIER. Les listes ci-dessous dirigent l'attention, elles ne reduisent pas le perimetre.
- CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST (`sha256:5ef8abbb56f0cdb286ae93b021d435dc81775fa1c0d2287a80f1e302cda93785`) ; l'approbation graphique releve de la porte D7, independante.
- Verdicts autorises, a rendre dans le packet JSON canonique et jamais dans cette vue : `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`.
- Cette vue ne porte aucune decision et ne nomme personne : l'assignation du role reste `PENDING_UNASSIGNED`, l'etat du packet reste `PENDING_UNASSIGNED`.

| Perimetre | Valeur |
| --- | --- |
| Objets du chapitre dans le packet | 161 |
| Empreinte de l'ensemble d'objets | `sha256:fac8d9dc89cd3699c20ae65783a82b7cfb068007a357721549edfa055858b135` |
| Empreinte semantique liee a l'approbation | `sha256:5ef8abbb56f0cdb286ae93b021d435dc81775fa1c0d2287a80f1e302cda93785` |
| Empreinte du packet | `sha256:8d43181f18c185cedc662df916dd50afaefc146c861c49005d5d0073b98b54ba` |
| Revision du depot gelee dans le packet | `5bc44275a0afe33f10b7ce2ec7700778f8de6308` |
| Preuve de rendu portee par le packet | `ABSENT` |

## 2. Le chapitre et ses capacites du programme officiel

**Suites numériques** — programme applicable 2026-2027, MENE2602917A, BO n° 14 du 2026-04-02.
Source officielle : https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A

Situation d'accroche declaree : Deux offres d'épargne : versement fixe mensuel (modèle linéaire) contre intérêts composés (modèle exponentiel). À partir de quand la seconde dépasse-t-elle la première ? Résolue au TD fil rouge avec les outils du chapitre (C2, C3, C6, C7).

Temps estime declare : parcours 1 : 14 h · parcours 2 : 11 h · parcours 3 : 10 h.

| Code | Libelle eleve | Libelle BO | Demonstration exigible |
| --- | --- | --- | --- |
| `C1` | Je sais calculer les termes d'une suite (explicite/récurrence), à la main et en Python. | Dans le cadre de l'étude d'une suite, utiliser le registre de la langue naturelle, le registre algébrique, le registre fonctionnel. Générer une suite définie de façon explicite ou par récurrence. | non |
| `C2` | Je sais montrer qu'une suite est arithmétique et exprimer son terme général. | Reconnaître si une suite est arithmétique. Exploiter la relation entre termes, la formule explicite. | non |
| `C3` | Je sais montrer qu'une suite est géométrique et exprimer son terme général. | Reconnaître si une suite est géométrique. Exploiter la relation entre termes, la formule explicite. | non |
| `C4` | Je sais calculer la somme des premiers entiers et d'une suite géométrique. | Calculer la somme des n premiers entiers, la somme des premiers termes d'une suite géométrique. | oui — Calcul de 1+2+...+n et de 1+q+...+q^n. |
| `C5` | Je sais étudier le sens de variation d'une suite par la méthode adaptée. | Étudier le sens de variation d'une suite : étude du signe de u(n+1)−u(n), ou du quotient si les termes sont strictement positifs, ou utilisation de la fonction associée. | non |
| `C6` | Je sais modéliser une situation concrète par une suite. | Modéliser un phénomène discret par une suite (évolutions successives, suites arithmétiques et géométriques comme modèles linéaire et exponentiel discrets). | non |
| `C7` | Je sais écrire et lire un programme Python (terme, somme, seuil). | Écrire et interpréter un programme calculant un terme, une somme de termes, un seuil. | non |
| `C8` | Je sais reconnaître intuitivement une limite finie, une limite infinie ou une absence de limite, sans formalisation. | Sensibilisation intuitive à la notion de limite d'une suite : limite finie, limite infinie et absence de limite ; toute formalisation est exclue. | non |

**Attendus officiels rattaches, capacite par capacite**

- `C1` — 4 attendus :
    - `1SPE-OFFICIAL-048` (MANDATORY_KNOWLEDGE, Suites numériques, modèles discrets) : Exemples de modes de génération d’une suite : explicite 𝑢𝑛 = ƒ (𝑛), par une relation de récurrence 𝑢𝑛 + 1 = ƒ (𝑢𝑛), par un algorithme, par des motifs géométriques.
    - `1SPE-OFFICIAL-049` (MANDATORY_KNOWLEDGE, Suites numériques, modèles discrets) : Notations : 𝑢(𝑛), 𝑢𝑛, (𝑢(𝑛)), (𝑢𝑛).
    - `1SPE-OFFICIAL-054` (MANDATORY_CAPACITY, Suites numériques, modèles discrets) : Dans le cadre de l’étude d’une suite, utiliser le registre de la langue naturelle, le registre algébrique, le registre graphique, et passer de l’un à l’autre.
    - `1SPE-OFFICIAL-056` (MANDATORY_CAPACITY, Suites numériques, modèles discrets) : Calculer des termes d’une suite définie explicitement, par récurrence ou par un algorithme.
- `C2` — 3 attendus :
    - `1SPE-OFFICIAL-050` (MANDATORY_KNOWLEDGE, Suites numériques, modèles discrets) : Suites arithmétiques : exemples, définition, calcul du terme général. Lien avec l’étude d’évolutions successives à accroissements constants. Lien avec les fonctions affines. Calcul de 1 + 2 + … + 𝑛.
    - `1SPE-OFFICIAL-057` (MANDATORY_CAPACITY, Suites numériques, modèles discrets) : Pour une suite arithmétique ou géométrique, calculer le terme général, la somme de termes consécutifs, déterminer le sens de variation.
    - `1SPE-OFFICIAL-060` (MANDATORY_SKILL, Suites numériques, modèles discrets) : Calcul du terme général d’une suite arithmétique, d’une suite géométrique.
- `C3` — 1 attendu :
    - `1SPE-OFFICIAL-051` (MANDATORY_KNOWLEDGE, Suites numériques, modèles discrets) : Suites géométriques : exemples, définition, calcul du terme général. Lien avec l’étude d’évolutions successives à taux constant. Lien avec la fonction exponentielle. Calcul de 1 + 𝑞 + … + 𝑞𝑛.
- `C4` — 2 attendus :
    - `1SPE-OFFICIAL-061` (MANDATORY_SKILL, Suites numériques, modèles discrets) : Calcul de 1 + 2 + … + 𝑛.
    - `1SPE-OFFICIAL-062` (MANDATORY_SKILL, Suites numériques, modèles discrets) : Calcul de 1 + 𝑞 + … + 𝑞𝑛.
- `C5` — 1 attendu :
    - `1SPE-OFFICIAL-052` (MANDATORY_KNOWLEDGE, Suites numériques, modèles discrets) : Sens de variation d’une suite.
- `C6` — 2 attendus :
    - `1SPE-OFFICIAL-055` (MANDATORY_CAPACITY, Suites numériques, modèles discrets) : Proposer, modéliser une situation permettant de générer une suite de nombres. Déterminer une relation explicite ou une relation de récurrence pour une suite définie par un motif géométrique, par une question de dénombrement.
    - `1SPE-OFFICIAL-058` (MANDATORY_CAPACITY, Suites numériques, modèles discrets) : Modéliser un phénomène discret à croissance linéaire par une suite arithmétique, un phénomène discret à croissance exponentielle par une suite géométrique.
- `C7` : aucun attendu officiel rattache dans `audit/SEMANTIC_ALIGNMENT_LEDGER.json`.
- `C8` — 2 attendus :
    - `1SPE-OFFICIAL-053` (MANDATORY_KNOWLEDGE, Suites numériques, modèles discrets) : Sur des exemples, introduction intuitive de la notion de limite, finie ou infinie, ou l’absence de limite d’une suite.
    - `1SPE-OFFICIAL-059` (MANDATORY_CAPACITY, Suites numériques, modèles discrets) : Conjecturer, dans des cas simples, la limite éventuelle d’une suite.

**Prerequis declares par le contrat du chapitre**

| Code | Libelle | Chapitre d'origine |
| --- | --- | --- |
| `R1` | Calcul littéral : développer, factoriser, réduire | 2GT |
| `R2` | Pourcentages : coefficient multiplicateur, évolutions successives | 2GT |
| `R3` | Fonctions : image, antécédent, sens de variation | 2GT |
| `R4` | Inégalités et signe d'une expression | 2GT |
| `R5` | Python : variables, boucle for, boucle while (SNT) | SNT |

## 3. Structure reelle et ordre d'assemblage courant

L'ordre ci-dessous n'est pas l'ordre alphabetique des repertoires : il est lu chez l'assembleur du manuel (`Mathematiques/manuel-maths/scripts/assemble_manuel.py`, `collect_chapter`). C'est la sequence que le lecteur du PDF recoit.

| Rang | Rubrique imprimee | Objets (professeur) |
| --- | --- | --- |
| 1 | Ouverture | 1 |
| 2 | Diagnostic | 1 |
| 3 | Cours | 8 |
| 4 | Méthodes | 8 |
| 5 | Exercices | 72 |
| 6 | TD | 2 |
| 7 | Auto-évaluation | 1 |
| 8 | Évaluation | 4 |
| 9 | Remédiation | 13 |
| 10 | Corrigés | 51 |

Total assemble : 161 objets en variante professeur, 108 en variante eleve (la variante eleve exclut les corriges et les corriges d'evaluation).

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

25 objets pour ce chapitre, regroupes par famille scientifique — la capacite du referentiel du depot, avec son libelle BO — puis par type d'objet.

Un objet qui declare plusieurs capacites apparait dans plusieurs familles : 25 objets distincts pour 29 rattachements.

### Famille `C1` — Dans le cadre de l'étude d'une suite, utiliser le registre de la langue naturelle, le registre algébrique, le registre fonctionnel. Générer une suite définie de façon explicite ou par récurrence.

Capacite eleve : « Je sais calculer les termes d'une suite (explicite/récurrence), à la main et en Python. »

5 objets · 36 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 4 objets, 6 affirmations a verifier :
    - `1SPE-SUITES-EX-002-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-002-CDP.tex`
    - `1SPE-SUITES-EX-003-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-003-CDP.tex`
    - `1SPE-SUITES-EX-004-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-004-CDP.tex`
    - `1SPE-SUITES-EX-005-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-005-CDP.tex`
- **`cours`** — 1 objet, 30 affirmations a verifier :
    - `1SPE-SUITES-CR-010` (30 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/10_C1_generalites_suites.tex`

### Famille `C2` — Reconnaître si une suite est arithmétique. Exploiter la relation entre termes, la formule explicite.

Capacite eleve : « Je sais montrer qu'une suite est arithmétique et exprimer son terme général. »

4 objets · 43 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 3 objets, 7 affirmations a verifier :
    - `1SPE-SUITES-EX-006-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-006-CDP.tex`
    - `1SPE-SUITES-EX-007-CDP` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-007-CDP.tex`
    - `1SPE-SUITES-EX-008-CDP` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-008-CDP.tex`
- **`cours`** — 1 objet, 36 affirmations a verifier :
    - `1SPE-SUITES-CR-011` (36 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/11_C2_suites_arithmetiques.tex`

### Famille `C3` — Reconnaître si une suite est géométrique. Exploiter la relation entre termes, la formule explicite.

Capacite eleve : « Je sais montrer qu'une suite est géométrique et exprimer son terme général. »

6 objets · 73 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 5 objets, 9 affirmations a verifier :
    - `1SPE-SUITES-EX-001-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-001-CDP.tex`
    - `1SPE-SUITES-EX-009-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-009-CDP.tex`
    - `1SPE-SUITES-EX-010-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-010-CDP.tex`
    - `1SPE-SUITES-EX-012-CDP` (4 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-012-CDP.tex`
    - `1SPE-SUITES-EX-018-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-018-CDP.tex`
- **`cours`** — 1 objet, 64 affirmations a verifier :
    - `1SPE-SUITES-CR-012` (64 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/12_C3_suites_geometriques.tex`

### Famille `C4` — Calculer la somme des n premiers entiers, la somme des premiers termes d'une suite géométrique.

Capacite eleve : « Je sais calculer la somme des premiers entiers et d'une suite géométrique. »

4 objets · 49 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 3 objets, 8 affirmations a verifier :
    - `1SPE-SUITES-EX-011-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-011-CDP.tex`
    - `1SPE-SUITES-EX-012-CDP` (4 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-012-CDP.tex`
    - `1SPE-SUITES-EX-013-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-013-CDP.tex`
- **`cours`** — 1 objet, 41 affirmations a verifier :
    - `1SPE-SUITES-CR-013` (41 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/13_C4_sommes.tex`

### Famille `C5` — Étudier le sens de variation d'une suite : étude du signe de u(n+1)−u(n), ou du quotient si les termes sont strictement positifs, ou utilisation de la fonction associée.

Capacite eleve : « Je sais étudier le sens de variation d'une suite par la méthode adaptée. »

5 objets · 36 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 4 objets, 8 affirmations a verifier :
    - `1SPE-SUITES-EX-007-CDP` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-007-CDP.tex`
    - `1SPE-SUITES-EX-010-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-010-CDP.tex`
    - `1SPE-SUITES-EX-014-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-014-CDP.tex`
    - `1SPE-SUITES-EX-016-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-016-CDP.tex`
- **`cours`** — 1 objet, 28 affirmations a verifier :
    - `1SPE-SUITES-CR-014` (28 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/14_C5_variations.tex`

### Famille `C6` — Modéliser un phénomène discret par une suite (évolutions successives, suites arithmétiques et géométriques comme modèles linéaire et exponentiel discrets).

Capacite eleve : « Je sais modéliser une situation concrète par une suite. »

2 objets · 26 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 1 objet, 1 affirmation a verifier :
    - `1SPE-SUITES-EX-018-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-018-CDP.tex`
- **`cours`** — 1 objet, 25 affirmations a verifier :
    - `1SPE-SUITES-CR-015` (25 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/15_C6_modelisation.tex`

### Famille `C7` — Écrire et interpréter un programme calculant un terme, une somme de termes, un seuil.

Capacite eleve : « Je sais écrire et lire un programme Python (terme, somme, seuil). »

2 objets · 12 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 1 objet, 1 affirmation a verifier :
    - `1SPE-SUITES-EX-020-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-020-CDP.tex`
- **`cours`** — 1 objet, 11 affirmations a verifier :
    - `1SPE-SUITES-CR-016` (11 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/16_C7_algorithmique.tex`

### Famille `C8` — Sensibilisation intuitive à la notion de limite d'une suite : limite finie, limite infinie et absence de limite ; toute formalisation est exclue.

Capacite eleve : « Je sais reconnaître intuitivement une limite finie, une limite infinie ou une absence de limite, sans formalisation. »

1 objet · 3 affirmations calculables sans preuve machine.

- **`cours`** — 1 objet, 3 affirmations a verifier :
    - `1SPE-SUITES-CR-017` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/17_C8_limites_intuitives.tex`

## 5. Question de QCM routee vers l'humain

Aucune question de ce chapitre n'est routee vers une revue humaine par `audit/QCM_INDEPENDENT_EVIDENCE_V2.json`.

## 6. Ce que la machine a deja etabli, et ce qu'elle n'etablit pas

Ces mesures viennent de `audit/PUBLISH_READINESS_CHAPTER_MATRIX.json`. Elles ne reduisent pas le perimetre de votre lecture : une dimension `COMPLETE` signifie que la machine a fini de mesurer, pas que le contenu est juste.

| Mesure | Valeur |
| --- | --- |
| Etat machine vertical | `MACHINE_REVIEW_COMPLETE` |
| Cloture humaine | `PENDING` |
| Objets passes par l'oracle | 122 reussites, 0 echecs, 26 en science humaine requise, 31 en revue manuelle |
| Attendus officiels obligatoires | 15 rattaches sur 15, 0 manquants, 0 hors annee |
| Sujets d'evaluation | 2 sujets, 2 corriges, statut `COMPLETE` |
| QCM | 21 questions, capacites evaluees C1, C2, C3, C4, C5, C6, C7, C8 |
| Relation exercice/corrige | ANSWER_COVERAGE_ESTABLISHED : 51 ; 0 echecs de cardinalite |

La relation exercice/corrige n'est etablie que structurellement : une COUVERTURE de reponses n'atteste pas qu'un corrige corrige bien son exercice. Cette fidelite est un point de votre checklist.

Dettes de revue declarees pour ce chapitre :

- `RESIDUAL_TRUE_NEW_13` — 5 unites, categorie `OBJECT_REVIEW`, bloquant : oui.
- `UNCHANGED` — 157 unites, categorie `OBJECT_REVIEW`, bloquant : oui.

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

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-SUITES/packet-A-EXPERT_MATHEMATIQUE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
