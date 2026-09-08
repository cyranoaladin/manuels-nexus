# Vue de lecture — Produit scalaire — EXPERT_MATHEMATIQUE

Chapitre `1SPE-PRODUIT-SCALAIRE` · manuel `1SPE` (Première, Spécialité mathématiques) · packet A · role `EXPERT_MATHEMATIQUE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-PRODUIT-SCALAIRE/packet-A-EXPERT_MATHEMATIQUE.json`
> Etat de revue : `audit/reviews/human/1SPE-PRODUIT-SCALAIRE/REVIEW_STATE.json`
> Producteur de cette vue : `scripts/build_human_review_reading_views.py`
>
> Toute divergence entre cette vue et le packet se tranche en faveur du packet. Cette vue ne cree, ne ferme et ne reduit aucune obligation.

## 1. Ce que vous decidez

- L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.
- Aucun humain n'a encore approuve ce chapitre : REVIEW_DELTA_BASELINE = NONE. Le perimetre de revue est le CHAPITRE COURANT ENTIER. Les listes ci-dessous dirigent l'attention, elles ne reduisent pas le perimetre.
- CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST (`sha256:c7c704558c02255341ae17e45afd38bef72087c89add29a5c911446a6f83ac45`) ; l'approbation graphique releve de la porte D7, independante.
- Verdicts autorises, a rendre dans le packet JSON canonique et jamais dans cette vue : `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`.
- Cette vue ne porte aucune decision et ne nomme personne : l'assignation du role reste `PENDING_UNASSIGNED`, l'etat du packet reste `PENDING_UNASSIGNED`.

| Perimetre | Valeur |
| --- | --- |
| Objets du chapitre dans le packet | 145 |
| Empreinte de l'ensemble d'objets | `sha256:6cac1a2c49baa43a9ad95684214f2f0944b700450f83a64a4a24e63ab9c320cd` |
| Empreinte semantique liee a l'approbation | `sha256:c7c704558c02255341ae17e45afd38bef72087c89add29a5c911446a6f83ac45` |
| Empreinte du packet | `sha256:fb0ad02aacb782a086f6f98af8744866caf958fb25d2d5be7885789abef76f14` |
| Revision du depot gelee dans le packet | `dfc99058e7a7c16ae4af46b99245edbe14b4f8e5` |
| Preuve de rendu portee par le packet | `ABSENT` |

## 2. Le chapitre et ses capacites du programme officiel

**Produit scalaire** — programme applicable 2026-2027, MENE2602917A, BO n° 14 du 2026-04-02.
Source officielle : https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A

Situation d'accroche declaree : Un randonneur se deplace de 5 km vers le nord-est puis de 3 km vers le sud-est. Quelle distance le separe de son point de depart ? Comment calculer l'angle entre deux trajets dans le plan ?

Temps estime declare : parcours 1 : 12 h · parcours 2 : 10 h · parcours 3 : 8 h.

| Code | Libelle eleve | Libelle BO | Demonstration exigible |
| --- | --- | --- | --- |
| `C1` | Je sais calculer un produit scalaire (definition geometrique, projection, expression analytique). | Définir le produit scalaire de deux vecteurs (définition géométrique, projection orthogonale, expression analytique). | non |
| `C2` | Je sais utiliser les proprietes du produit scalaire (bilinearite, symetrie, norme). | Connaître et utiliser les propriétés du produit scalaire (bilinéarité, symétrie, norme). | oui — Démonstration de l'expression analytique à partir de la bilinéarité. |
| `C3` | Je sais determiner l'orthogonalite de deux vecteurs et calculer un angle. | Utiliser le produit scalaire pour déterminer des angles, des orthogonalités et des longueurs. | non |
| `C4` | Je sais utiliser le produit scalaire dans des problemes geometriques (mediatrice, hauteurs, aires). | Résoudre des problèmes géométriques à l'aide du produit scalaire. | non |
| `C5` | Je sais appliquer la formule d'Al-Kashi et en connais la demonstration. | Développer les carrés des normes de la somme et de la différence de deux vecteurs ; connaître et démontrer la formule d'Al-Kashi. | oui — Démonstration de la formule d'Al-Kashi par le produit scalaire. |

**Attendus officiels rattaches, capacite par capacite**

- `C1` — 2 attendus :
    - `1SPE-OFFICIAL-128` (MANDATORY_KNOWLEDGE, Calcul vectoriel et produit scalaire) : Produit scalaire à partir de la projection orthogonale et de la formule avec le cosinus. Caractérisation de l’orthogonalité.
    - `1SPE-OFFICIAL-133` (MANDATORY_CAPACITY, Calcul vectoriel et produit scalaire) : En vue de la résolution d’un problème, calculer le produit scalaire de deux vecteurs en choisissant une méthode adaptée (en utilisant la projection orthogonale, à l’aide des coordonnées, à l’aide des normes et d’un angle, à l’aide de normes).
- `C2` — 2 attendus :
    - `1SPE-OFFICIAL-129` (MANDATORY_KNOWLEDGE, Calcul vectoriel et produit scalaire) : Bilinéarité, symétrie. En base orthonormée, expression du produit scalaire et de la norme, critère d’orthogonalité. Expression des coordonnées dans une base orthonormée en termes de produits scalaires avec les vecteurs de la base.
    - `1SPE-OFFICIAL-130` (MANDATORY_KNOWLEDGE, Calcul vectoriel et produit scalaire) : Développement de ‖𝑢 ⃗ + 𝑣‖2 et ‖𝑢 ⃗ − 𝑣 ‖2 . Formule d’Al-Kashi.
- `C3` — 1 attendu :
    - `1SPE-OFFICIAL-132` (MANDATORY_CAPACITY, Calcul vectoriel et produit scalaire) : Utiliser le produit scalaire pour démontrer une orthogonalité, pour calculer un angle, une longueur dans le plan.
- `C4` — 3 attendus :
    - `1SPE-OFFICIAL-131` (MANDATORY_KNOWLEDGE, Calcul vectoriel et produit scalaire) : Transformation de l’expression M ⃗⃗⃗⃗⃗⃗B. ⃗⃗⃗⃗⃗⃗⃗A ⋅ M
    - `1SPE-OFFICIAL-134` (MANDATORY_CAPACITY, Calcul vectoriel et produit scalaire) : Utiliser le produit scalaire pour résoudre un problème géométrique.
    - `1SPE-OFFICIAL-136` (MANDATORY_SKILL, Calcul vectoriel et produit scalaire) : Ensemble des points M tels que M ⃗⃗⃗⃗⃗⃗B = 0 (démonstration avec le produit scalaire). ⃗⃗⃗⃗⃗⃗⃗A ⋅ M
- `C5` — 1 attendu :
    - `1SPE-OFFICIAL-135` (MANDATORY_SKILL, Calcul vectoriel et produit scalaire) : Formule d’Al-Kashi (démonstration avec le produit scalaire).

**Prerequis declares par le contrat du chapitre**

| Code | Libelle | Chapitre d'origine |
| --- | --- | --- |
| `R1` | Vecteurs et coordonnees dans le plan | 2GT |
| `R2` | Norme d'un vecteur | 2GT |
| `R3` | Trigonometrie (cos, sin, valeurs remarquables) | 1SPE-TRIGONOMETRIE |
| `R4` | Calcul litteral (identites remarquables, developpement) | 2GT |
| `R5` | Theoreme de Pythagore | 2GT |

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

19 objets pour ce chapitre, regroupes par famille scientifique — la capacite du referentiel du depot, avec son libelle BO — puis par type d'objet.

### Famille `C1` — Définir le produit scalaire de deux vecteurs (définition géométrique, projection orthogonale, expression analytique).

Capacite eleve : « Je sais calculer un produit scalaire (definition geometrique, projection, expression analytique). »

5 objets · 6 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 4 objets, 4 affirmations a verifier :
    - `1SPE-PRODSCAL-EX-001-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-001-CDP.tex`
    - `1SPE-PRODSCAL-EX-002-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-002-CDP.tex`
    - `1SPE-PRODSCAL-EX-003-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-003-CDP.tex`
    - `1SPE-PRODSCAL-EX-004-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-004-CDP.tex`
- **`methode`** — 1 objet, 2 affirmations a verifier :
    - `1SPE-PRODSCAL-ME-001` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/methodes/1SPE-PRODSCAL-ME-001.tex`

### Famille `C2` — Connaître et utiliser les propriétés du produit scalaire (bilinéarité, symétrie, norme).

Capacite eleve : « Je sais utiliser les proprietes du produit scalaire (bilinearite, symetrie, norme). »

5 objets · 19 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 4 objets, 8 affirmations a verifier :
    - `1SPE-PRODSCAL-EX-011-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-011-CDP.tex`
    - `1SPE-PRODSCAL-EX-012-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-012-CDP.tex`
    - `1SPE-PRODSCAL-EX-013-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-013-CDP.tex`
    - `1SPE-PRODSCAL-EX-014-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-014-CDP.tex`
- **`methode`** — 1 objet, 11 affirmations a verifier :
    - `1SPE-PRODSCAL-ME-002` (11 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/methodes/1SPE-PRODSCAL-ME-002.tex`

### Famille `C3` — Utiliser le produit scalaire pour déterminer des angles, des orthogonalités et des longueurs.

Capacite eleve : « Je sais determiner l'orthogonalite de deux vecteurs et calculer un angle. »

1 objet · 7 affirmations calculables sans preuve machine.

- **`methode`** — 1 objet, 7 affirmations a verifier :
    - `1SPE-PRODSCAL-ME-003` (7 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/methodes/1SPE-PRODSCAL-ME-003.tex`

### Famille `C4` — Résoudre des problèmes géométriques à l'aide du produit scalaire.

Capacite eleve : « Je sais utiliser le produit scalaire dans des problemes geometriques (mediatrice, hauteurs, aires). »

5 objets · 17 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 4 objets, 8 affirmations a verifier :
    - `1SPE-PRODSCAL-EX-031-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-031-CDP.tex`
    - `1SPE-PRODSCAL-EX-032-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-032-CDP.tex`
    - `1SPE-PRODSCAL-EX-033-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-033-CDP.tex`
    - `1SPE-PRODSCAL-EX-034-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-034-CDP.tex`
- **`methode`** — 1 objet, 9 affirmations a verifier :
    - `1SPE-PRODSCAL-ME-004` (9 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/methodes/1SPE-PRODSCAL-ME-004.tex`

### Famille `C5` — Développer les carrés des normes de la somme et de la différence de deux vecteurs ; connaître et démontrer la formule d'Al-Kashi.

Capacite eleve : « Je sais appliquer la formule d'Al-Kashi et en connais la demonstration. »

3 objets · 9 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 2 objets, 2 affirmations a verifier :
    - `1SPE-PRODSCAL-EX-041-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-041-CDP.tex`
    - `1SPE-PRODSCAL-EX-042-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/exercices/1SPE-PRODSCAL-EX-042-CDP.tex`
- **`methode`** — 1 objet, 7 affirmations a verifier :
    - `1SPE-PRODSCAL-ME-005` (7 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/methodes/1SPE-PRODSCAL-ME-005.tex`

## 5. Question de QCM routee vers l'humain

Aucune question de ce chapitre n'est routee vers une revue humaine par `audit/QCM_INDEPENDENT_EVIDENCE_V2.json`.

## 6. Ce que la machine a deja etabli, et ce qu'elle n'etablit pas

Ces mesures viennent de `audit/PUBLISH_READINESS_CHAPTER_MATRIX.json`. Elles ne reduisent pas le perimetre de votre lecture : une dimension `COMPLETE` signifie que la machine a fini de mesurer, pas que le contenu est juste.

| Mesure | Valeur |
| --- | --- |
| Etat machine vertical | `MACHINE_REVIEW_COMPLETE` |
| Cloture humaine | `PENDING` |
| Objets passes par l'oracle | 121 reussites, 0 echecs, 20 en science humaine requise, 24 en revue manuelle |
| Attendus officiels obligatoires | 9 rattaches sur 9, 0 manquants, 0 hors annee |
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

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-PRODUIT-SCALAIRE/packet-A-EXPERT_MATHEMATIQUE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
