# Vue de lecture — Variables aléatoires — EXPERT_MATHEMATIQUE

Chapitre `1SPE-VARIABLES-ALEATOIRES` · manuel `1SPE` (Première, Spécialité mathématiques) · packet A · role `EXPERT_MATHEMATIQUE`.

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**
>
> Packet canonique : `audit/reviews/human/1SPE-VARIABLES-ALEATOIRES/packet-A-EXPERT_MATHEMATIQUE.json`
> Etat de revue : `audit/reviews/human/1SPE-VARIABLES-ALEATOIRES/REVIEW_STATE.json`
> Producteur de cette vue : `scripts/build_human_review_reading_views.py`
>
> Toute divergence entre cette vue et le packet se tranche en faveur du packet. Cette vue ne cree, ne ferme et ne reduit aucune obligation.

## 1. Ce que vous decidez

- L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.
- Aucun humain n'a encore approuve ce chapitre : REVIEW_DELTA_BASELINE = NONE. Le perimetre de revue est le CHAPITRE COURANT ENTIER. Les listes ci-dessous dirigent l'attention, elles ne reduisent pas le perimetre.
- CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST (`sha256:c68406a0ef2cad2dc64b773691e7be431e62d11f149b1783e9b94fa48974fc7c`) ; l'approbation graphique releve de la porte D7, independante.
- Verdicts autorises, a rendre dans le packet JSON canonique et jamais dans cette vue : `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`.
- Cette vue ne porte aucune decision et ne nomme personne : l'assignation du role reste `PENDING_UNASSIGNED`, l'etat du packet reste `PENDING_UNASSIGNED`.

| Perimetre | Valeur |
| --- | --- |
| Objets du chapitre dans le packet | 167 |
| Empreinte de l'ensemble d'objets | `sha256:32b2dd9bff3bc3c7c82007986ef3a2009ee89d1aecb9fcad87cf1670af00490e` |
| Empreinte semantique liee a l'approbation | `sha256:c68406a0ef2cad2dc64b773691e7be431e62d11f149b1783e9b94fa48974fc7c` |
| Empreinte du packet | `sha256:9943fd16ddace27b7af542496caeb9d5df3fe28e5e35da0a28db632ce1e0d34b` |
| Revision du depot gelee dans le packet | `bdb5edb33b59fceb3e69105f8ce108712b0d051c` |
| Preuve de rendu portee par le packet | `ABSENT` |

## 2. Le chapitre et ses capacites du programme officiel

**Variables aléatoires** — programme applicable 2026-2027, MENE2602917A, BO n° 14 du 2026-04-02.
Source officielle : https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A

Situation d'accroche declaree : Un assureur propose un contrat couvrant la casse d'un smartphone. La prime annuelle est de 50 euros. En cas de casse, l'assureur rembourse 300 euros. Si la probabilite de casse est de 1/10, ce contrat est-il avantageux pour l'assure ? Pour l'assureur ? Un probleme de decision qui se ramene a l'etude de l'esperance d'une variable aleatoire.

Temps estime declare : parcours 1 : 14 h · parcours 2 : 11 h · parcours 3 : 9 h.

| Code | Libelle eleve | Libelle BO | Demonstration exigible |
| --- | --- | --- | --- |
| `C1` | Je sais interpreter les evenements lies a une variable aleatoire et determiner sa loi de probabilite. | Interpréter les événements liés à une variable aléatoire et déterminer sa loi de probabilité sur un univers fini. | non |
| `C2` | Je sais calculer l'esperance E(X), la variance V(X) et l'ecart type sigma(X) d'une variable aleatoire. | Calculer l'espérance, la variance et l'écart type d'une variable aléatoire. | non |
| `C3` | Je sais representer par un arbre la repetition de n <= 4 epreuves de Bernoulli independantes et identiques, puis etudier le nombre de succes. | Pour n ≤ 4, représenter par un arbre la répétition d'épreuves de Bernoulli indépendantes et identiques afin de calculer les probabilités liées au nombre de succès. | non |
| `C4` | Je sais utiliser la linearite de l'esperance pour calculer E(aX+b). | Utiliser la linéarité de l'espérance. | non |
| `C5` | Je sais resoudre des problemes contextualises (jeux, decisions, assurances) a l'aide de variables aleatoires. | Résoudre des problèmes contextualisés faisant intervenir des variables aléatoires. | non |
| `C6` | Je sais simuler une variable aleatoire et des echantillons, et lire, comprendre et ecrire une fonction Python renvoyant la moyenne d'un echantillon de taille n. | Le travail expérimental de simulation d’échantillons prolonge celui entrepris en seconde. L’objectif est de faire percevoir le principe de l’estimation de l’espérance d’une variable aléatoire, ou de la moyenne d’une variable statistique dans une population, par une moyenne observée sur un échantillon. Simuler une variable aléatoire avec Python ou un tableur. Lire, comprendre et écrire une fonction Python renvoyant la moyenne d’un échantillon de taille n d’une variable aléatoire. | non |
| `C7` | Je sais etudier experimentalement la fluctuation des moyennes d'echantillons autour de l'esperance, simuler N echantillons et interpreter l'ecart entre moyenne empirique et esperance, notamment au regard de 2 sigma / racine(n). | Étudier sur des exemples la distance entre la moyenne d’un échantillon simulé de taille n d’une variable aléatoire et l’espérance de cette variable aléatoire. Simuler, avec Python ou un tableur, N échantillons de taille n d’une variable aléatoire, d’espérance μ et d’écart type σ. Si m désigne la moyenne d’un échantillon, calculer la proportion des cas où l’écart entre m et μ est inférieur ou égal à 2𝜎/√n. | non |

**Attendus officiels rattaches, capacite par capacite**

- `C1` — 4 attendus :
    - `1SPE-OFFICIAL-162` (MANDATORY_KNOWLEDGE, Variables aléatoires réelles) : Variable aléatoire réelle : modélisation du résultat numérique d’une expérience aléatoire ; formalisation comme fonction définie sur l’univers et à valeurs réelles.
    - `1SPE-OFFICIAL-163` (MANDATORY_KNOWLEDGE, Variables aléatoires réelles) : Loi d’une variable aléatoire.
    - `1SPE-OFFICIAL-167` (MANDATORY_CAPACITY, Variables aléatoires réelles) : Interpréter en situation et utiliser les notations {X = a}, {X ⩽ a}, P(X = a), P(X ⩽ a). Passer du registre de la langue naturelle au registre symbolique et inversement.
    - `1SPE-OFFICIAL-169` (MANDATORY_CAPACITY, Variables aléatoires réelles) : Déterminer la loi de probabilité d’une variable aléatoire.
- `C2` — 3 attendus :
    - `1SPE-OFFICIAL-164` (MANDATORY_KNOWLEDGE, Variables aléatoires réelles) : Espérance, variance, écart type d’une variable aléatoire.
    - `1SPE-OFFICIAL-166` (MANDATORY_KNOWLEDGE, Variables aléatoires réelles) : Formule de König-Huygens.
    - `1SPE-OFFICIAL-170` (MANDATORY_CAPACITY, Variables aléatoires réelles) : Calculer une espérance, une variance, un écart type.
- `C3` — 2 attendus :
    - `1SPE-OFFICIAL-154` (MANDATORY_KNOWLEDGE, Probabilités conditionnelles et indépendance) : Pour 𝑛 ⩽ 4, répétition de 𝑛 épreuves de Bernoulli indépendantes et identiques.
    - `1SPE-OFFICIAL-158` (MANDATORY_CAPACITY, Probabilités conditionnelles et indépendance) : Pour 𝑛 ⩽ 4, représenter l’arbre associé à la répétition de 𝑛 épreuves de Bernoulli indépendantes et identiques afin de calculer des probabilités.
- `C4` — 1 attendu :
    - `1SPE-OFFICIAL-165` (MANDATORY_KNOWLEDGE, Variables aléatoires réelles) : Linéarité de l’espérance.
- `C5` — 2 attendus :
    - `1SPE-OFFICIAL-168` (MANDATORY_CAPACITY, Variables aléatoires réelles) : Modéliser une situation à l’aide d’une variable aléatoire.
    - `1SPE-OFFICIAL-171` (MANDATORY_CAPACITY, Variables aléatoires réelles) : Utiliser la notion d’espérance dans une résolution de problème (mise pour un jeu équitable, etc.).
- `C6` — 3 attendus :
    - `1SPE-OFFICIAL-175` (MANDATORY_ALGORITHM, Variables aléatoires réelles) : Le travail expérimental de simulation d’échantillons prolonge celui entrepris en seconde. L’objectif est de faire percevoir le principe de l’estimation de l’espérance d’une variable aléatoire, ou de la moyenne d’une variable statistique dans une population, par une moyenne observée sur un échantillon.
    - `1SPE-OFFICIAL-176` (MANDATORY_ALGORITHM, Variables aléatoires réelles) : Simuler une variable aléatoire avec Python ou un tableur.
    - `1SPE-OFFICIAL-177` (MANDATORY_ALGORITHM, Variables aléatoires réelles) : Lire, comprendre et écrire une fonction Python renvoyant la moyenne d’un échantillon de taille n d’une variable aléatoire.
- `C7` — 2 attendus :
    - `1SPE-OFFICIAL-178` (MANDATORY_ALGORITHM, Variables aléatoires réelles) : Étudier sur des exemples la distance entre la moyenne d’un échantillon simulé de taille n d’une variable aléatoire et l’espérance de cette variable aléatoire.
    - `1SPE-OFFICIAL-179` (MANDATORY_ALGORITHM, Variables aléatoires réelles) : Simuler, avec Python ou un tableur, N échantillons de taille n d’une variable aléatoire, d’espérance μ et d’écart type σ. Si m désigne la moyenne d’un échantillon, calculer la proportion des cas où l’écart entre m et μ est inférieur ou égal à 2𝜎/√n.

**Prerequis declares par le contrat du chapitre**

| Code | Libelle | Chapitre d'origine |
| --- | --- | --- |
| `R1` | Probabilites de base : experience aleatoire, univers, evenements, probabilite d'un evenement | 2GT |
| `R2` | Probabilites conditionnelles et independance | 1SPE-PROBA-COND |
| `R4` | Suites et sommes : notation sigma, suites arithmetiques et geometriques | 1SPE-SUITES |
| `R5` | Puissances : regles de calcul, puissances entieres | 2GT |

## 3. Structure reelle et ordre d'assemblage courant

L'ordre ci-dessous n'est pas l'ordre alphabetique des repertoires : il est lu chez l'assembleur du manuel (`Mathematiques/manuel-maths/scripts/assemble_manuel.py`, `collect_chapter`). C'est la sequence que le lecteur du PDF recoit.

| Rang | Rubrique imprimee | Objets (professeur) |
| --- | --- | --- |
| 1 | Ouverture | 1 |
| 2 | Diagnostic | 1 |
| 3 | Cours | 6 |
| 4 | Méthodes | 9 |
| 5 | Exercices | 72 |
| 6 | TD | 2 |
| 7 | Auto-évaluation | 1 |
| 8 | Évaluation | 4 |
| 9 | Remédiation | 12 |
| 10 | Corrigés | 54 |

Total assemble : 162 objets en variante professeur, 106 en variante eleve (la variante eleve exclut les corriges et les corriges d'evaluation).

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

**Objets du perimetre de revue absents de la sequence assemblee**

5 objets du packet n'apparaissent dans aucune rubrique assemblee : le perimetre de revue les couvre, le PDF ne les imprime pas.

- `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/cours/experimentations/02_frequences_lettres.tex`
- `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/cours/experimentations/03_simuler_variable.tex`
- `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/cours/experimentations/04_fonction_moyenne.tex`
- `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/cours/experimentations/05_distance_moyenne_esperance.tex`
- `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/cours/experimentations/06_proportion_2sigma.tex`

## 4. Points d'attention scientifiques, par famille

Le registre `audit/1SPE_MANUAL_REVIEW_DISPOSITION_LEDGER.json` classe chaque objet du manuel. Ceux qui portent la disposition `SCIENCE_HUMAINE_REQUISE` contiennent des affirmations calculables qu'aucune preuve machine n'etablit : ce sont eux que la lecture scientifique doit atteindre en priorite.

19 objets pour ce chapitre, regroupes par famille scientifique — la capacite du referentiel du depot, avec son libelle BO — puis par type d'objet.

Un objet qui declare plusieurs capacites apparait dans plusieurs familles : 19 objets distincts pour 23 rattachements.

### Famille `C1` — Interpréter les événements liés à une variable aléatoire et déterminer sa loi de probabilité sur un univers fini.

Capacite eleve : « Je sais interpreter les evenements lies a une variable aleatoire et determiner sa loi de probabilite. »

4 objets · 16 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 3 objets, 6 affirmations a verifier :
    - `1SPE-VARALEA-EX-001-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-001-CDP.tex`
    - `1SPE-VARALEA-EX-002-CDP` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-002-CDP.tex`
    - `1SPE-VARALEA-EX-005-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-005-CDP.tex`
- **`methode`** — 1 objet, 10 affirmations a verifier :
    - `1SPE-VARALEA-ME-001` (10 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/methodes/1SPE-VARALEA-ME-001.tex`

### Famille `C2` — Calculer l'espérance, la variance et l'écart type d'une variable aléatoire.

Capacite eleve : « Je sais calculer l'esperance E(X), la variance V(X) et l'ecart type sigma(X) d'une variable aleatoire. »

4 objets · 14 affirmations calculables sans preuve machine.

- **`algorithme`** — 1 objet, 1 affirmation a verifier :
    - `1SPE-VARALEA-ALG-001` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/cours/15_experimentations.tex`
- **`coup_de_pouce`** — 2 objets, 3 affirmations a verifier :
    - `1SPE-VARALEA-EX-013-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-013-CDP.tex`
    - `1SPE-VARALEA-EX-017-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-017-CDP.tex`
- **`methode`** — 1 objet, 10 affirmations a verifier :
    - `1SPE-VARALEA-ME-002` (10 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/methodes/1SPE-VARALEA-ME-002.tex`

### Famille `C3` — Pour n ≤ 4, représenter par un arbre la répétition d'épreuves de Bernoulli indépendantes et identiques afin de calculer les probabilités liées au nombre de succès.

Capacite eleve : « Je sais representer par un arbre la repetition de n <= 4 epreuves de Bernoulli independantes et identiques, puis etudier le nombre de succes. »

3 objets · 6 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 3 objets, 6 affirmations a verifier :
    - `1SPE-VARALEA-EX-002-CDP` (3 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-002-CDP.tex`
    - `1SPE-VARALEA-EX-005-CDP` (2 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-005-CDP.tex`
    - `1SPE-VARALEA-EX-017-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-017-CDP.tex`

### Famille `C4` — Utiliser la linéarité de l'espérance.

Capacite eleve : « Je sais utiliser la linearite de l'esperance pour calculer E(aX+b). »

1 objet · 1 affirmation calculable sans preuve machine.

- **`coup_de_pouce`** — 1 objet, 1 affirmation a verifier :
    - `1SPE-VARALEA-EX-017-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-017-CDP.tex`

### Famille `C5` — Résoudre des problèmes contextualisés faisant intervenir des variables aléatoires.

Capacite eleve : « Je sais resoudre des problemes contextualises (jeux, decisions, assurances) a l'aide de variables aleatoires. »

3 objets · 13 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 2 objets, 2 affirmations a verifier :
    - `1SPE-VARALEA-EX-041-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-041-CDP.tex`
    - `1SPE-VARALEA-EX-047-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-047-CDP.tex`
- **`methode`** — 1 objet, 11 affirmations a verifier :
    - `1SPE-VARALEA-ME-005` (11 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/methodes/1SPE-VARALEA-ME-005.tex`

### Famille `C7` — Étudier sur des exemples la distance entre la moyenne d’un échantillon simulé de taille n d’une variable aléatoire et l’espérance de cette variable aléatoire. Simuler, avec Python ou un tableur, N échantillons de taille n d’une variable aléatoire, d’espérance μ et d’écart type σ. Si m désigne la moyenne d’un échantillon, calculer la proportion des cas où l’écart entre m et μ est inférieur ou égal à 2𝜎/√n.

Capacite eleve : « Je sais etudier experimentalement la fluctuation des moyennes d'echantillons autour de l'esperance, simuler N echantillons et interpreter l'ecart entre moyenne empirique et esperance, notamment au regard de 2 sigma / racine(n). »

1 objet · 1 affirmation calculable sans preuve machine.

- **`methode`** — 1 objet, 1 affirmation a verifier :
    - `1SPE-VARALEA-ME-009` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/methodes/1SPE-VARALEA-ME-009.tex`

### Famille `CAPACITE_NON_DECLAREE_PAR_L_OBJET`

Objets dont ni le META ni l'exercice servi ne declare de capacite du chapitre. Rien n'est devine ici : la famille reste a etablir par lecture.

7 objets · 30 affirmations calculables sans preuve machine.

- **`coup_de_pouce`** — 5 objets, 8 affirmations a verifier :
    - `1SPE-VARALEA-EX-022-CDP` (4 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-022-CDP.tex`
    - `1SPE-VARALEA-EX-024-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-024-CDP.tex`
    - `1SPE-VARALEA-EX-026-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-026-CDP.tex`
    - `1SPE-VARALEA-EX-031-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-031-CDP.tex`
    - `1SPE-VARALEA-EX-033-CDP` (1 affirmation) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-033-CDP.tex`
- **`methode`** — 2 objets, 22 affirmations a verifier :
    - `1SPE-VARALEA-ME-003` (7 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/methodes/1SPE-VARALEA-ME-003.tex`
    - `1SPE-VARALEA-ME-004` (15 affirmations) — `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/methodes/1SPE-VARALEA-ME-004.tex`

## 5. Question de QCM routee vers l'humain

Aucune question de ce chapitre n'est routee vers une revue humaine par `audit/QCM_INDEPENDENT_EVIDENCE_V2.json`.

## 6. Ce que la machine a deja etabli, et ce qu'elle n'etablit pas

Ces mesures viennent de `audit/PUBLISH_READINESS_CHAPTER_MATRIX.json`. Elles ne reduisent pas le perimetre de votre lecture : une dimension `COMPLETE` signifie que la machine a fini de mesurer, pas que le contenu est juste.

| Mesure | Valeur |
| --- | --- |
| Etat machine vertical | `MACHINE_REVIEW_COMPLETE` |
| Cloture humaine | `PENDING` |
| Objets passes par l'oracle | 133 reussites, 0 echecs, 20 en science humaine requise, 29 en revue manuelle |
| Attendus officiels obligatoires | 17 rattaches sur 17, 0 manquants, 0 hors annee |
| Sujets d'evaluation | 2 sujets, 2 corriges, statut `COMPLETE` |
| QCM | 21 questions, capacites evaluees C1, C2, C3, C4, C5, C6, C7 |
| Relation exercice/corrige | ANSWER_COVERAGE_ESTABLISHED : 54 ; 0 echecs de cardinalite |

La relation exercice/corrige n'est etablie que structurellement : une COUVERTURE de reponses n'atteste pas qu'un corrige corrige bien son exercice. Cette fidelite est un point de votre checklist.

Dettes de revue declarees pour ce chapitre :

- `RESIDUAL_TRUE_NEW_13` — 4 unites, categorie `OBJECT_REVIEW`, bloquant : oui.
- `UNCHANGED` — 152 unites, categorie `OBJECT_REVIEW`, bloquant : oui.
- `VARALEA_C6C7_REVIEW_DEBT_12` — 12 unites, categorie `OBJECT_REVIEW`, bloquant : oui.

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

En cas d'ecart entre le PDF et les fichiers sources, ce sont les sources du chapitre qui font foi : `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/`.

---

Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique. Le packet de ce role est `audit/reviews/human/1SPE-VARIABLES-ALEATOIRES/packet-A-EXPERT_MATHEMATIQUE.json`. L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.

Marche a suivre commune aux deux roles : `audit/reviews/human/ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md`.
