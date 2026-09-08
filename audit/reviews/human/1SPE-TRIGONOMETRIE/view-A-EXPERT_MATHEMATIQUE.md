# Vue de lecture — Trigonométrie — EXPERT_MATHEMATIQUE

Chapitre `1SPE-TRIGONOMETRIE` · manuel `1SPE` (Première, Spécialité mathématiques) · packet A · role `EXPERT_MATHEMATIQUE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-TRIGONOMETRIE/packet-A-EXPERT_MATHEMATIQUE.json`
> Etat de revue : `audit/reviews/human/1SPE-TRIGONOMETRIE/REVIEW_STATE.json`
> Producteur de cette vue : `scripts/build_human_review_reading_views.py`
>
> Toute divergence entre cette vue et le packet se tranche en faveur du packet. Cette vue ne cree, ne ferme et ne reduit aucune obligation.

## 1. Ce que vous decidez

- L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.
- Aucun humain n'a encore approuve ce chapitre : REVIEW_DELTA_BASELINE = NONE. Le perimetre de revue est le CHAPITRE COURANT ENTIER. Les listes ci-dessous dirigent l'attention, elles ne reduisent pas le perimetre.
- CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST (`sha256:590269373f7f0589819979a8639273f402b32de7d0d4dda4ac6328d1ee2fb243`) ; l'approbation graphique releve de la porte D7, independante.
- Verdicts autorises, a rendre dans le packet JSON canonique et jamais dans cette vue : `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`.
- Cette vue ne porte aucune decision et ne nomme personne : l'assignation du role reste `PENDING_UNASSIGNED`, l'etat du packet reste `PENDING_UNASSIGNED`.

| Perimetre | Valeur |
| --- | --- |
| Objets du chapitre dans le packet | 78 |
| Empreinte de l'ensemble d'objets | `sha256:b4679995be20574bd17f70368d5afe83fab601caca60bda18c05da8f40eb5fa3` |
| Empreinte semantique liee a l'approbation | `sha256:590269373f7f0589819979a8639273f402b32de7d0d4dda4ac6328d1ee2fb243` |
| Empreinte du packet | `sha256:4e2e7cbe35461a9578c74a5d2232bd48fffa09f666b4a1448e8c65e4815591cd` |
| Revision du depot gelee dans le packet | `dfc99058e7a7c16ae4af46b99245edbe14b4f8e5` |
| Preuve de rendu portee par le packet | `ABSENT` |

## 2. Le chapitre et ses capacites du programme officiel

**Trigonométrie** — programme applicable 2026-2027, MENE2602917A, BO n° 14 du 2026-04-02.
Source officielle : https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A

Situation d'accroche declaree : Une grande roue de fete foraine a un rayon de 25 metres et son centre est a 27 metres du sol. A quelle hauteur se trouve un passager apres un tour d'un sixieme du cercle ? Le radian et la lecture du cercle trigonometrique permettent de repondre.

Temps estime declare : parcours 1 : 6 h · parcours 2 : 5 h · parcours 3 : 4 h.

| Code | Libelle eleve | Libelle BO | Demonstration exigible |
| --- | --- | --- | --- |
| `C1` | Je sais placer un angle oriente sur le cercle trigonometrique et convertir degres/radians. | Connaître le cercle trigonométrique, la mesure en radian, les angles orientés. | non |
| `C2` | Je sais determiner les cosinus et sinus de valeurs remarquables et d'angles associes par lecture du cercle trigonometrique. | Connaître et utiliser cos et sin (relation fondamentale, valeurs remarquables, symétries). | non |

**Attendus officiels rattaches, capacite par capacite**

- `C1` — 3 attendus :
    - `1SPE-OFFICIAL-120` (MANDATORY_KNOWLEDGE, Trigonométrie) : Cercle trigonométrique. Longueur d’arc. Radian.
    - `1SPE-OFFICIAL-121` (MANDATORY_KNOWLEDGE, Trigonométrie) : Enroulement de la droite sur le cercle trigonométrique. Image d’un nombre réel.
    - `1SPE-OFFICIAL-123` (MANDATORY_CAPACITY, Trigonométrie) : Placer un point sur le cercle trigonométrique.
- `C2` — 3 attendus :
    - `1SPE-OFFICIAL-122` (MANDATORY_KNOWLEDGE, Trigonométrie) : Cosinus et sinus d’un nombre réel. Lien avec le sinus et le cosinus dans un triangle rectangle. Valeurs remarquables.
    - `1SPE-OFFICIAL-124` (MANDATORY_CAPACITY, Trigonométrie) : Par lecture du cercle trigonométrique, déterminer, pour des valeurs remarquables de 𝑥, les cosinus et sinus d’angles associés à 𝑥.
    - `1SPE-OFFICIAL-125` (MANDATORY_SKILL, Trigonométrie) : Calcul de cos , sin , cos , sin . 4 4 3 3

**Prerequis declares par le contrat du chapitre**

| Code | Libelle | Chapitre d'origine |
| --- | --- | --- |
| `R1` | Theoreme de Pythagore | 2GT |
| `R2` | Reperage dans le plan : coordonnees, distance | 2GT |

## 3. Structure reelle et ordre d'assemblage courant

L'ordre ci-dessous n'est pas l'ordre alphabetique des repertoires : il est lu chez l'assembleur du manuel (`Mathematiques/manuel-maths/scripts/assemble_manuel.py`, `collect_chapter`). C'est la sequence que le lecteur du PDF recoit.

| Rang | Rubrique imprimee | Objets (professeur) |
| --- | --- | --- |
| 1 | Cours | 2 |
| 2 | Méthodes | 5 |
| 3 | Exercices | 36 |
| 4 | TD | 2 |
| 5 | Auto-évaluation | 1 |
| 6 | Évaluation | 4 |
| 7 | Remédiation | 4 |
| 8 | Corrigés | 24 |

Total assemble : 78 objets en variante professeur, 52 en variante eleve (la variante eleve exclut les corriges et les corriges d'evaluation).

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

6 objets pour ce chapitre, regroupes par famille scientifique — la capacite du referentiel du depot, avec son libelle BO — puis par type d'objet.

### Famille `C1` — Connaître le cercle trigonométrique, la mesure en radian, les angles orientés.

Capacite eleve : « Je sais placer un angle oriente sur le cercle trigonometrique et convertir degres/radians. »

2 objets · 8 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 1 objet, 1 affirmation a verifier :
    - `1SPE-TRIGO-EX-021-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-021-CDP.tex`
- **`methode`** — 1 objet, 7 affirmations a verifier :
    - `1SPE-TRIGO-ME-001` (7 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-TRIGONOMETRIE/methodes/1SPE-TRIGO-ME-001.tex`

### Famille `C2` — Connaître et utiliser cos et sin (relation fondamentale, valeurs remarquables, symétries).

Capacite eleve : « Je sais determiner les cosinus et sinus de valeurs remarquables et d'angles associes par lecture du cercle trigonometrique. »

4 objets · 12 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 3 objets, 5 affirmations a verifier :
    - `1SPE-TRIGO-EX-013-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-013-CDP.tex`
    - `1SPE-TRIGO-EX-014-CDP` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-014-CDP.tex`
    - `1SPE-TRIGO-EX-023-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-TRIGONOMETRIE/exercices/1SPE-TRIGO-EX-023-CDP.tex`
- **`methode`** — 1 objet, 7 affirmations a verifier :
    - `1SPE-TRIGO-ME-002` (7 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-TRIGONOMETRIE/methodes/1SPE-TRIGO-ME-002.tex`

## 5. Question de QCM routee vers l'humain

Aucune question de ce chapitre n'est routee vers une revue humaine par `audit/QCM_INDEPENDENT_EVIDENCE_V2.json`.

## 6. Ce que la machine a deja etabli, et ce qu'elle n'etablit pas

Ces mesures viennent de `audit/PUBLISH_READINESS_CHAPTER_MATRIX.json`. Elles ne reduisent pas le perimetre de votre lecture : une dimension `COMPLETE` signifie que la machine a fini de mesurer, pas que le contenu est juste.

| Mesure | Valeur |
| --- | --- |
| Etat machine vertical | `MACHINE_REVIEW_COMPLETE` |
| Cloture humaine | `PENDING` |
| Objets passes par l'oracle | 63 reussites, 0 echecs, 7 en science humaine requise, 15 en revue manuelle |
| Attendus officiels obligatoires | 6 rattaches sur 6, 0 manquants, 0 hors annee |
| Sujets d'evaluation | 2 sujets, 2 corriges, statut `COMPLETE` |
| QCM | 15 questions, capacites evaluees C1, C2 |
| Relation exercice/corrige | ANSWER_COVERAGE_ESTABLISHED : 24 ; 0 echecs de cardinalite |

La relation exercice/corrige n'est etablie que structurellement : une COUVERTURE de reponses n'atteste pas qu'un corrige corrige bien son exercice. Cette fidelite est un point de votre checklist.

Dettes de revue declarees pour ce chapitre :

- `TRIGO_OPTIONAL_EXTENSION_REQUALIFICATION_STALE_3` — 3 unites, categorie `OBJECT_REVIEW`, bloquant : oui.
- `UNCHANGED` — 60 unites, categorie `OBJECT_REVIEW`, bloquant : oui.

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

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-TRIGONOMETRIE/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-TRIGONOMETRIE/packet-A-EXPERT_MATHEMATIQUE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
