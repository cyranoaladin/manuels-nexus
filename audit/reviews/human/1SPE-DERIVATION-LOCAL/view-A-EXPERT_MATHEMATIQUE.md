# Vue de lecture — Dérivation : point de vue local — EXPERT_MATHEMATIQUE

Chapitre `1SPE-DERIVATION-LOCAL` · manuel `1SPE` (Première, Spécialité mathématiques) · packet A · role `EXPERT_MATHEMATIQUE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-DERIVATION-LOCAL/packet-A-EXPERT_MATHEMATIQUE.json`
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
| Empreinte du packet | `sha256:d499360110f3f47e9dd74fcf32a02b8600678ec748a2ea0adf2ebf3ed5c5a833` |
| Revision du depot gelee dans le packet | `dfc99058e7a7c16ae4af46b99245edbe14b4f8e5` |
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

## 4. Points d'attention scientifiques, par famille

Le registre `audit/1SPE_MANUAL_REVIEW_DISPOSITION_LEDGER.json` classe chaque objet du manuel. Ceux qui portent la disposition `SCIENCE_HUMAINE_REQUISE` contiennent des affirmations calculables qu'aucune preuve machine n'etablit : ce sont eux que la lecture scientifique doit atteindre en priorite.

12 objets pour ce chapitre, regroupes par famille scientifique — la capacite du referentiel du depot, avec son libelle BO — puis par type d'objet.

### Famille `C1` — Calculer un taux de variation, la pente d'une sécante.

Capacite eleve : « Je sais calculer et interpréter un taux de variation et la pente d'une sécante. »

1 objet · 3 affirmations calculables sans preuve machine.

- **`cours`** — 1 objet, 3 affirmations a verifier :
    - `1SPE-DERIVATION-LOCAL-CR-010` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/cours/10_C1_taux_variation.tex`

### Famille `C2` — Interpréter le nombre dérivé en contexte : pente d'une tangente, vitesse instantanée, coût marginal, etc.

Capacite eleve : « Je sais interpréter un nombre dérivé comme une pente ou une vitesse instantanée. »

4 objets · 9 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 3 objets, 4 affirmations a verifier :
    - `1SPE-DERLOCAL-EX-007-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-007-CDP.tex`
    - `1SPE-DERLOCAL-EX-008-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-008-CDP.tex`
    - `1SPE-DERLOCAL-EX-033-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-033-CDP.tex`
- **`cours`** — 1 objet, 5 affirmations a verifier :
    - `1SPE-DERIVATION-LOCAL-CR-011` (5 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/cours/11_C2_nombre_derive.tex`

### Famille `C3` — Déterminer graphiquement un nombre dérivé par la pente de la tangente. Construire la tangente en un point à une courbe représentative connaissant le nombre dérivé.

Capacite eleve : « Je sais lire un nombre dérivé sur un graphique et construire la tangente correspondante. »

1 objet · 3 affirmations calculables sans preuve machine.

- **`cours`** — 1 objet, 3 affirmations a verifier :
    - `1SPE-DERIVATION-LOCAL-CR-012` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/cours/12_C3_tangente.tex`

### Famille `C4` — Déterminer l'équation de la tangente en un point à la courbe représentative d'une fonction.

Capacite eleve : « Je sais écrire l'équation d'une tangente à partir de l'abscisse, de l'image et du nombre dérivé. »

3 objets · 14 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 2 objets, 6 affirmations a verifier :
    - `1SPE-DERLOCAL-EX-019-CDP` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-019-CDP.tex`
    - `1SPE-DERLOCAL-EX-037-CDP` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-037-CDP.tex`
- **`cours`** — 1 objet, 8 affirmations a verifier :
    - `1SPE-DERIVATION-LOCAL-CR-013` (8 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/cours/13_C4_equation_tangente.tex`

### Famille `C5` — Calculer une valeur approchée de f(a+h).

Capacite eleve : « Je sais approcher f(a+h) avec l'approximation linéaire au voisinage de a. »

3 objets · 13 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 2 objets, 6 affirmations a verifier :
    - `1SPE-DERLOCAL-EX-026-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-026-CDP.tex`
    - `1SPE-DERLOCAL-EX-038-CDP` (4 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-038-CDP.tex`
- **`cours`** — 1 objet, 7 affirmations a verifier :
    - `1SPE-DERIVATION-LOCAL-CR-014` (7 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/cours/14_C5_approximation_lineaire.tex`

## 5. Question de QCM routee vers l'humain

Aucune question de ce chapitre n'est routee vers une revue humaine par `audit/QCM_INDEPENDENT_EVIDENCE_V2.json`.

## 6. Ce que la machine a deja etabli, et ce qu'elle n'etablit pas

Ces mesures viennent de `audit/PUBLISH_READINESS_CHAPTER_MATRIX.json`. Elles ne reduisent pas le perimetre de votre lecture : une dimension `COMPLETE` signifie que la machine a fini de mesurer, pas que le contenu est juste.

| Mesure | Valeur |
| --- | --- |
| Etat machine vertical | `MACHINE_REVIEW_COMPLETE` |
| Cloture humaine | `PENDING` |
| Objets passes par l'oracle | 116 reussites, 0 echecs, 13 en science humaine requise, 24 en revue manuelle |
| Attendus officiels obligatoires | 10 rattaches sur 10, 0 manquants, 0 hors annee |
| Sujets d'evaluation | 2 sujets, 2 corriges, statut `COMPLETE` |
| QCM | 15 questions, capacites evaluees C1, C2, C3, C4, C5 |
| Relation exercice/corrige | ANSWER_COVERAGE_ESTABLISHED : 50 ; 0 echecs de cardinalite |

La relation exercice/corrige n'est etablie que structurellement : une COUVERTURE de reponses n'atteste pas qu'un corrige corrige bien son exercice. Cette fidelite est un point de votre checklist.

Dettes de revue declarees pour ce chapitre :

- `UNCHANGED` — 146 unites, categorie `OBJECT_REVIEW`, bloquant : oui.

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

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-DERIVATION-LOCAL/packet-A-EXPERT_MATHEMATIQUE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
