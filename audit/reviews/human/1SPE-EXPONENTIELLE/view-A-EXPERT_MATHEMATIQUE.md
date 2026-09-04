# Vue de lecture — Fonction exponentielle — EXPERT_MATHEMATIQUE

Chapitre `1SPE-EXPONENTIELLE` · manuel `1SPE` (Première, Spécialité mathématiques) · packet A · role `EXPERT_MATHEMATIQUE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-EXPONENTIELLE/packet-A-EXPERT_MATHEMATIQUE.json`
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
| Empreinte du packet | `sha256:c149ea15242d4aac3a83c4ab9d6409904bb15b4a7b88d4714f754c406315383c` |
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

## 4. Points d'attention scientifiques, par famille

Le registre `audit/1SPE_MANUAL_REVIEW_DISPOSITION_LEDGER.json` classe chaque objet du manuel. Ceux qui portent la disposition `SCIENCE_HUMAINE_REQUISE` contiennent des affirmations calculables qu'aucune preuve machine n'etablit : ce sont eux que la lecture scientifique doit atteindre en priorite.

10 objets pour ce chapitre, regroupes par famille scientifique — la capacite du referentiel du depot, avec son libelle BO — puis par type d'objet.

### Famille `C1` — Connaître la définition de la fonction exponentielle comme unique fonction dérivable sur ℝ vérifiant f'=f et f(0)=1.

Capacite eleve : « Je sais que la fonction exponentielle est l'unique fonction égale à sa dérivée valant 1 en 0. »

3 objets · 8 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 3 objets, 8 affirmations a verifier :
    - `1SPE-EXPO-EX-002-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-002-CDP.tex`
    - `1SPE-EXPO-EX-003-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-003-CDP.tex`
    - `1SPE-EXPO-EX-004-CDP` (4 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-004-CDP.tex`

### Famille `C2` — Connaître et utiliser les propriétés algébriques de la fonction exponentielle : exp(a+b)=exp(a)exp(b), exp(-a)=1/exp(a), exp(na)=(exp(a))^n.

Capacite eleve : « Je sais utiliser les propriétés algébriques de l'exponentielle (somme, produit, puissance). »

1 objet · 2 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 1 objet, 2 affirmations a verifier :
    - `1SPE-EXPO-EX-014-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-014-CDP.tex`

### Famille `C3` — Connaître le signe, le sens de variation et la courbe représentative de la fonction exponentielle ; faire le lien avec les suites géométriques.

Capacite eleve : « Je sais exploiter le signe, la croissance et la courbe de l'exponentielle, en lien avec les suites géométriques. »

2 objets · 3 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 2 objets, 3 affirmations a verifier :
    - `1SPE-EXPO-EX-022-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-022-CDP.tex`
    - `1SPE-EXPO-EX-024-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-024-CDP.tex`

### Famille `C4` — Pour a réel, déterminer la dérivée de la fonction t → $e^{at}$.

Capacite eleve : « Je sais dériver la fonction t → $e^{at}$ pour un réel a. »

1 objet · 1 affirmation calculable sans preuve machine.

- **`coup_de_pouce`** — 1 objet, 1 affirmation a verifier :
    - `1SPE-EXPO-EX-032-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-032-CDP.tex`

### Famille `C5` — Pour k strictement positif, représenter t → e^{-kt} et t → e^{kt} ; modéliser une croissance ou une décroissance exponentielle.

Capacite eleve : « Je sais représenter et utiliser un modèle de croissance ou de décroissance exponentielle. »

2 objets · 2 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 2 objets, 2 affirmations a verifier :
    - `1SPE-EXPO-EX-041-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-041-CDP.tex`
    - `1SPE-EXPO-EX-042-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-042-CDP.tex`

### Famille `CAPACITE_NON_DECLAREE_PAR_L_OBJET`

Objets dont ni le META ni l'exercice servi ne declare de capacite du chapitre. Rien n'est devine ici : la famille reste a etablir par lecture.

1 objet · 3 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 1 objet, 3 affirmations a verifier :
    - `1SPE-EXPO-EX-034-CDP` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-034-CDP.tex`

## 5. Question de QCM routee vers l'humain

Aucune question de ce chapitre n'est routee vers une revue humaine par `audit/QCM_INDEPENDENT_EVIDENCE_V2.json`.

## 6. Ce que la machine a deja etabli, et ce qu'elle n'etablit pas

Ces mesures viennent de `audit/PUBLISH_READINESS_CHAPTER_MATRIX.json`. Elles ne reduisent pas le perimetre de votre lecture : une dimension `COMPLETE` signifie que la machine a fini de mesurer, pas que le contenu est juste.

| Mesure | Valeur |
| --- | --- |
| Etat machine vertical | `MACHINE_REVIEW_COMPLETE` |
| Cloture humaine | `PENDING` |
| Objets passes par l'oracle | 122 reussites, 0 echecs, 11 en science humaine requise, 19 en revue manuelle |
| Attendus officiels obligatoires | 7 rattaches sur 7, 0 manquants, 0 hors annee |
| Sujets d'evaluation | 2 sujets, 2 corriges, statut `COMPLETE` |
| QCM | 15 questions, capacites evaluees C1, C2, C3, C4, C5 |
| Relation exercice/corrige | ANSWER_COVERAGE_ESTABLISHED : 50 ; 0 echecs de cardinalite |

La relation exercice/corrige n'est etablie que structurellement : une COUVERTURE de reponses n'atteste pas qu'un corrige corrige bien son exercice. Cette fidelite est un point de votre checklist.

Dettes de revue declarees pour ce chapitre :

- `EXPONENTIELLE_C1_METHOD_REVIEW_DEBT_1` — 1 unite, categorie `OBJECT_REVIEW`, bloquant : oui.
- `RESIDUAL_TRUE_NEW_13` — 2 unites, categorie `OBJECT_REVIEW`, bloquant : oui.
- `UNCHANGED` — 145 unites, categorie `OBJECT_REVIEW`, bloquant : oui.

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

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-EXPONENTIELLE/packet-A-EXPERT_MATHEMATIQUE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
