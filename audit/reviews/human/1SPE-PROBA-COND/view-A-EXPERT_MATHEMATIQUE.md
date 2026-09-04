# Vue de lecture — Probabilités conditionnelles et indépendance — EXPERT_MATHEMATIQUE

Chapitre `1SPE-PROBA-COND` · manuel `1SPE` (Première, Spécialité mathématiques) · packet A · role `EXPERT_MATHEMATIQUE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-PROBA-COND/packet-A-EXPERT_MATHEMATIQUE.json`
> Etat de revue : `audit/reviews/human/1SPE-PROBA-COND/REVIEW_STATE.json`
> Producteur de cette vue : `scripts/build_human_review_reading_views.py`
>
> Toute divergence entre cette vue et le packet se tranche en faveur du packet. Cette vue ne cree, ne ferme et ne reduit aucune obligation.

## 1. Ce que vous decidez

- L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.
- Aucun humain n'a encore approuve ce chapitre : REVIEW_DELTA_BASELINE = NONE. Le perimetre de revue est le CHAPITRE COURANT ENTIER. Les listes ci-dessous dirigent l'attention, elles ne reduisent pas le perimetre.
- CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST (`sha256:158783b246ae18c6b799fef38e07ea3e2aadb4b4fc7226fe8cd81adf30d47d9b`) ; l'approbation graphique releve de la porte D7, independante.
- Verdicts autorises, a rendre dans le packet JSON canonique et jamais dans cette vue : `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`.
- Cette vue ne porte aucune decision et ne nomme personne : l'assignation du role reste `PENDING_UNASSIGNED`, l'etat du packet reste `PENDING_UNASSIGNED`.

| Perimetre | Valeur |
| --- | --- |
| Objets du chapitre dans le packet | 148 |
| Empreinte de l'ensemble d'objets | `sha256:129c6e2442c6787ee3f96e1cfe6568bd879542ad9e7b78b876b662c6a7055982` |
| Empreinte semantique liee a l'approbation | `sha256:158783b246ae18c6b799fef38e07ea3e2aadb4b4fc7226fe8cd81adf30d47d9b` |
| Empreinte du packet | `sha256:35b04f69f493ae60412bd28faee1073b831ada86ff52c47ffe06614ffbdb56ae` |
| Revision du depot gelee dans le packet | `dfc99058e7a7c16ae4af46b99245edbe14b4f8e5` |
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

## 4. Points d'attention scientifiques, par famille

Le registre `audit/1SPE_MANUAL_REVIEW_DISPOSITION_LEDGER.json` classe chaque objet du manuel. Ceux qui portent la disposition `SCIENCE_HUMAINE_REQUISE` contiennent des affirmations calculables qu'aucune preuve machine n'etablit : ce sont eux que la lecture scientifique doit atteindre en priorite.

6 objets pour ce chapitre, regroupes par famille scientifique — la capacite du referentiel du depot, avec son libelle BO — puis par type d'objet.

### Famille `C1` — Calculer des probabilités conditionnelles P_A(B).

Capacite eleve : « Je sais calculer une probabilite conditionnelle $P_A(B) = P(A \cap B) / P(A)$. »

1 objet · 12 affirmations calculables sans preuve machine.

- **`cours`** — 1 objet, 12 affirmations a verifier :
    - `1SPE-PROBCOND-CR-010` (12 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-PROBA-COND/cours/10_C1_probabilite_conditionnelle.tex`

### Famille `C2` — Construire et exploiter un arbre pondéré.

Capacite eleve : « Je sais construire et lire un arbre pondere. »

1 objet · 7 affirmations calculables sans preuve machine.

- **`cours`** — 1 objet, 7 affirmations a verifier :
    - `1SPE-PROBCOND-CR-011` (7 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-PROBA-COND/cours/11_C2_arbre_pondere.tex`

### Famille `C3` — Appliquer la formule des probabilités totales.

Capacite eleve : « Je sais appliquer la formule des probabilites totales. »

1 objet · 5 affirmations calculables sans preuve machine.

- **`cours`** — 1 objet, 5 affirmations a verifier :
    - `1SPE-PROBCOND-CR-012` (5 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-PROBA-COND/cours/12_C3_probabilites_totales.tex`

### Famille `C4` — Reconnaître et utiliser l'indépendance de deux événements.

Capacite eleve : « Je sais determiner si deux evenements sont independants. »

1 objet · 15 affirmations calculables sans preuve machine.

- **`cours`** — 1 objet, 15 affirmations a verifier :
    - `1SPE-PROBCOND-CR-013` (15 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-PROBA-COND/cours/13_C4_independance.tex`

### Famille `C5` — Résoudre des problèmes contextualisés faisant intervenir des probabilités conditionnelles.

Capacite eleve : « Je sais resoudre un probleme contextualise de probabilites conditionnelles. »

2 objets · 11 affirmations calculables sans preuve machine.

- **`algorithme`** — 1 objet, 3 affirmations a verifier :
    - `1SPE-PROBCOND-ALG-001` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-PROBA-COND/cours/15_algorithmique_monte_carlo.tex`
- **`cours`** — 1 objet, 8 affirmations a verifier :
    - `1SPE-PROBCOND-CR-014` (8 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-PROBA-COND/cours/14_C5_problemes_contextualises.tex`

## 5. Question de QCM routee vers l'humain

Aucune question de ce chapitre n'est routee vers une revue humaine par `audit/QCM_INDEPENDENT_EVIDENCE_V2.json`.

## 6. Ce que la machine a deja etabli, et ce qu'elle n'etablit pas

Ces mesures viennent de `audit/PUBLISH_READINESS_CHAPTER_MATRIX.json`. Elles ne reduisent pas le perimetre de votre lecture : une dimension `COMPLETE` signifie que la machine a fini de mesurer, pas que le contenu est juste.

| Mesure | Valeur |
| --- | --- |
| Etat machine vertical | `MACHINE_REVIEW_COMPLETE` |
| Cloture humaine | `PENDING` |
| Objets passes par l'oracle | 117 reussites, 0 echecs, 7 en science humaine requise, 26 en revue manuelle |
| Attendus officiels obligatoires | 8 rattaches sur 8, 0 manquants, 0 hors annee |
| Sujets d'evaluation | 2 sujets, 2 corriges, statut `COMPLETE` |
| QCM | 18 questions, capacites evaluees C1, C2, C3, C4, C5 |
| Relation exercice/corrige | ANSWER_COVERAGE_ESTABLISHED : 50 ; 0 echecs de cardinalite |

La relation exercice/corrige n'est etablie que structurellement : une COUVERTURE de reponses n'atteste pas qu'un corrige corrige bien son exercice. Cette fidelite est un point de votre checklist.

Dettes de revue declarees pour ce chapitre :

- `UNCHANGED` — 149 unites, categorie `OBJECT_REVIEW`, bloquant : oui.

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

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-PROBA-COND/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-PROBA-COND/packet-A-EXPERT_MATHEMATIQUE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
