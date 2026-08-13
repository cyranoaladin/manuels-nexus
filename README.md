# Manuels Nexus Réussite — Collection 2026-2027

Ce dépôt transforme des sources disciplinaires, réglementaires et pédagogiques
en manuels scolaires PDF pour les mathématiques et la spécialité NSI, avec une
chaîne de preuves destinée à empêcher qu'un artefact simplement présent soit
confondu avec un produit publiable.

## Statut immédiat

> **NO-GO publication.** Aucun des six manuels ne peut être publié dans l'état
> audité. Les douze PDF canoniques existent, mais leur présence ne prouve ni un
> build observé, ni la reproductibilité, ni la conformité, ni une release.

| Repère | Valeur | Sens |
|---|---|---|
| Date de l'état présenté | 13 août 2026 | Instantané, pas vérité intemporelle |
| État métier audité | `1d0c3fdaa24f17d938696b615d23373579042b95` | Sources, PDF, inventaires et gates examinés |
| Rapport d'audit publié | `b5c6f9f113dc7be0b33765bb6229b6d4e6611467` | Commit qui ajoute le rapport de passation |
| HEAD de conception approuvée | `d8fd14e1a1dccbd2beaccf21526061f8b1563d10` | Conception du portail scellée et normalisée |
| Commit du plan approuvé | `0aab5554a5beca7ae2d42d67f8e5c2ee11e41e4f` | HEAD avant création de ce README |
| Branche de travail | `integration/1spe-bo2026-traceability` | Branche dédiée, distincte de `main` |

Le rapport détaillé qui fait foi pour cet instantané est
[l'audit de passation du 13 août 2026](audit/AUDIT_ETAT_PROJET_2026-08-13.md).
Le présent README en expose les conséquences opérationnelles sans modifier les
contenus, le registre réglementaire, les classes LaTeX ou les baselines.

Trois notions doivent rester séparées :

- un **PDF présent** est un fichier versionné sous `build/` ;
- un **build observé** possède un reçu, un préflight et une entrée de manifeste
  produits au même SHA par la chaîne prévue ;
- une **release** satisfait tous les gates scientifiques, programme,
  pédagogiques, variantes, visuels, PDF et reproductibilité, puis reçoit les
  approbations humaines requises.

## Le projet en 90 secondes

| Indicateur observé au SHA métier `1d0c3fda` | Valeur |
|---|---:|
| Manuels | 6 |
| Chapitres | 51 |
| Objets pédagogiques inventoriés | 2 860 |
| PDF canoniques élève/professeur | 12 |
| Pages cumulées | 2 026 |
| Chapitres démontrés `READY` | 0 |
| Entrées objet/contrat à statut bloquant | 2 911 |
| Bloqueurs `release-strict` | 67 |
| Builds observés dans le manifeste global | 0 |

En clair : **0 READY** démontré, même si les PDF et de nombreux objets sont
déjà présents.

Le modèle de production est le suivant : un texte officiel est traduit en
capacités atomiques ; les capacités alimentent des contrats de chapitre ; les
contrats référencent des objets pédagogiques identifiés et statutés ; les
assembleurs sélectionnent les objets des variantes élève ou professeur ;
LuaLaTeX produit les PDF ; les préflights, reçus, manifests, inventaires, gates
et revues indépendantes produisent les preuves ; l'humain approuve enfin une
release déterminée.

Les trois risques dominants sont actuellement :

1. des corrigés, barèmes, clés de réponse et identifiants internes fuient dans
   certaines éditions élèves ;
2. des tableaux et ouvertures débordent ou sont coupés alors que le préflight
   Mathématiques les accepte encore ;
3. la provenance réglementaire, la source de vérité des assemblages et la
   preuve de reproductibilité restent contradictoires ou incomplètes.

Le dépôt est donc une base de production riche et testée, mais pas une
collection validée. Une baseline n'est pas une acceptation de qualité et ne
rend jamais une anomalie acceptable. Un nombre élevé de tests ne remplace pas
la couverture des gates.

## Comment lire ce README

Ce portail est organisé en trois couches :

1. l'orientation immédiate donne le verdict, le périmètre et l'autorité ;
2. la partie durable décrit le métier, la pédagogie, les sources, les builds,
   les tests et la gouvernance ;
3. le bloc `CURRENT AUDITED STATE` fige l'état du 13 août 2026 et les commandes
   permettant de le remettre en cause par de nouvelles preuves.

Sommaire compact :

- **Orientation** — [statut](#statut-immédiat),
  [synthèse](#le-projet-en-90-secondes),
  [autorité](#hiérarchie-dautorité) ;
- **Produit et métier** — [mission](#mission-et-définition-du-produit),
  [périmètre](#les-six-manuels),
  [chaîne éditoriale](#logique-métier-de-la-chaîne-éditoriale),
  [pédagogie](#modèle-pédagogique-nexus) et
  [programmes](#programmes-officiels-2026-2027) ;
- **Architecture** — [arborescence](#arborescence-du-dépôt),
  [sources](#architecture-des-sources),
  [charte](#charte-graphique-v5v6) et
  [pipeline](#pipeline-de-build-et-de-preuve) ;
- **Opérations** — [prérequis](#prérequis-et-installation),
  [build local](#construire-un-manuel-localement),
  [build observé](#enregistrer-un-build-observé),
  [gates](#tests-et-gates) et [CI](#intégration-continue) ;
- **Gouvernance** — [contribution](#workflow-obligatoire-de-contribution),
  [Git](#git-commits-et-interdictions) et
  [Chutes](#consultation-externe-chutes) ;
- **Audit et passation** —
  [état daté](#état-courant-audité--13-août-2026),
  [roadmap](#roadmap-approuvée), [carte documentaire](#carte-documentaire) et
  [procédure d'audit](#procédure-pour-un-nouvel-auditeur).

Les mots **cible**, **exigence** ou **doit** décrivent le produit attendu. Les
mots **observé**, **actuel** ou **au SHA audité** décrivent ce qui est prouvé.
Les documents marqués **historiques** expliquent le passé, mais ne peuvent pas
contredire les sources, builds et tests courants.

## Hiérarchie d'autorité

En cas de contradiction, l'ordre d'autorité est :

1. les textes officiels en vigueur ;
2. le [cahier des charges du manuel 1SPE](CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md) ;
3. le fichier [AGENTS.md](AGENTS.md) applicable au chemin modifié ;
4. les schémas, contrats et gates machine validés ;
5. les décisions humaines approuvées et consignées ;
6. les rapports recalculés depuis les sources et builds observés ;
7. les rapports, directives, prompts et README historiques.

Le registre [PROGRAMMES_2026_2027.yaml](docs/programmes/PROGRAMMES_2026_2027.yaml)
est le registre machine de la collection, mais reste subordonné aux textes
officiels. Il contient encore des écarts réglementaires signalés plus bas.

Le cahier des charges contractuel principal est centré sur `1SPE`. Les règles
de dépôt, la conception approuvée des six manuels et les gates étendent les
invariants communs à la collection sans inventer un programme disciplinaire.

Ce README est un portail daté. S'il contredit une autorité supérieure, une
sortie de build ou un test observé, il est faux et doit être corrigé.

## Mission et définition du produit

La collection Nexus Réussite vise simultanément :

- l'exactitude disciplinaire et la cohérence entre énoncés, réponses,
  distracteurs, diagnostics, remédiations et corrigés ;
- la conformité aux programmes applicables à l'édition 2026-2027 ;
- une pédagogie différenciée qui fait réellement progresser chaque capacité ;
- la séparation stricte des versions élève et professeur ;
- du code Python provenant de fichiers `.py`, parsé, exécuté et comparé à ses
  sorties publiées ;
- une charte graphique commune, stable, lisible et adaptable ;
- des PDF numériques et imprimables avec navigation, métadonnées et polices ;
- une construction reproductible depuis un clone propre ;
- une traçabilité du texte officiel jusqu'à l'artefact final ;
- des revues indépendantes et une approbation humaine finale.

La **source éditoriale** est l'ensemble versionné des objets, contrats,
référentiels, gabarits, scripts et assets. Le **livrable PDF** est un résultat de
composition. La **preuve de build** relie ce résultat à un SHA, un environnement,
des entrées et des gates. La **release publiable** est un livrable prouvé et
approuvé, pas seulement un PDF lisible.

Les deux éditions canoniques attendues par manuel sont :

- une édition élève sans matériel réservé au professeur ;
- une édition professeur avec corrigés, barèmes, diagnostics et conseils.

Les livrets de méthodes ou de remédiation, banques d'évaluations, projets et
sujets sont des ressources séparées. Ils ne doivent pas élargir silencieusement
la surface canonique des douze éditions.

## Les six manuels

| ID canonique | Niveau et discipline | Chapitres | Objets | PDF | Pages élève / professeur |
|---|---|---:|---:|---:|---:|
| `1SPE` | Première, mathématiques spécialité | 10 | 1 401 | 2 | 361 / 601 |
| `TSPE_2026_2027` | Terminale, mathématiques spécialité | 11 | 768 | 2 | 179 / 250 |
| `TCOMPL` | Terminale, mathématiques complémentaires | 9 | 150 | 2 | 66 / 80 |
| `TEXPERTES` | Terminale, mathématiques expertes | 5 | 93 | 2 | 42 / 52 |
| `1NSI` | Première, numérique et sciences informatiques | 10 | 339 | 2 | 109 / 171 |
| `TNSI` | Terminale, numérique et sciences informatiques | 6 | 109 | 2 | 48 / 67 |
| **Total** | **Collection 2026-2027** | **51** | **2 860** | **12** | **2 026 pages** |

Ces nombres proviennent de
[l'inventaire généré](audit/INVENTAIRE_COLLECTION.md) au SHA métier audité.
Ils décrivent l'arbre, pas sa complétude. En particulier, six chapitres TNSI
n'impliquent pas que TNSI soit complet ou publiable.

L'inventaire recense aussi dix PDF de corpus non attribués. Ils ne font pas
partie des douze livrables canoniques et ne doivent pas être additionnés au
total produit.

## Ce que signifie « terminé »

Un chapitre devient `READY` seulement si son contrat, sa traçabilité, sa boucle
Nexus, ses exercices, ses évaluations A/B, ses remédiations, ses revues, son
build et son préflight sont prouvés sans P0 ouvert.

Un manuel devient candidat de release seulement si, au même SHA :

- toutes les capacités obligatoires sont reliées à des sources officielles ;
- les objets publiés ont des statuts approuvés et aucun contenu `generated`,
  `draft` ou `needs_*_review` ne fuit dans la release ;
- aucune erreur disciplinaire connue, sortie Python inventée ou ambiguïté
  bloquante ne subsiste ;
- les variantes élève/professeur sont comparées objet par objet ;
- le build élève et le build professeur sont observés, reproductibles et
  associés à des manifests ;
- les préflights numérique et imprimeur, les métadonnées, signets, liens,
  polices et contrôles d'accessibilité sont satisfaits ;
- toutes les pages ont été rendues et examinées visuellement ;
- `--validate-model`, `--fail-on-new` et `--release-strict` sont verts ;
- les revues scientifique, programme, éditoriale et PDF sont indépendantes ;
- l'approbation humaine finale du manuel est archivée.

Les douze PDF présents au 13 août ne satisfont pas cette définition.

## Logique métier de la chaîne éditoriale

```text
texte officiel applicable
  -> registre des sources et référentiel de capacités
  -> contrat canonique de chapitre
  -> objets pédagogiques identifiés, typés et statutés (% META:)
  -> assemblage déclaré de la variante élève ou professeur
  -> composition LuaLaTeX
  -> préflight PDF et reçu de build
  -> manifeste de builds observés
  -> inventaire, gates et comparaison des variantes
  -> revues indépendantes
  -> approbation humaine
  -> release figée
```

Les termes structurants sont :

- **capacité** : apprentissage atomique rattaché à un attendu officiel ;
- **objet** : unité éditoriale versionnée, par exemple cours, méthode,
  exercice, QCM, remédiation ou corrigé ;
- **contrat** : déclaration de ce qu'un chapitre doit couvrir et prouver ;
- **statut** : niveau de maturité ou type de revue encore requis ;
- **assemblage déclaré** : sélection déduite statiquement des scripts ou
  manifests, sans preuve qu'elle a compilé ;
- **build observé** : exécution ayant produit PDF, préflight, reçu et entrée de
  manifeste cohérents ;
- **gate** : contrôle automatique avec condition et code de sortie explicites ;
- **baseline** : mémoire de dette utilisée pour détecter une aggravation ;
- **disposition** : qualification individuelle et gouvernée d'une anomalie ;
- **release candidate** : ensemble figé qui a franchi les gates techniques et
  attend ou possède les approbations de release.

Une analyse statique répond « ce que les sources déclarent assembler ». Un
build observé répond « ce que cette exécution a réellement produit ». Le second
ne remplace pas les revues de fond, mais il est indispensable à la preuve.

## Modèle pédagogique Nexus

Chaque capacité doit mettre en œuvre, sauf justification humaine approuvée, la
boucle de maîtrise suivante :

1. **Diagnostic** : deux à quatre questions ciblent les prérequis.
2. **Orientation** : une règle objective oriente le parcours.
3. **Cours essentiel** : le minimum exigible est enseigné explicitement.
4. **Exemple expert** : une résolution complète rend le raisonnement visible.
5. **Guidage estompé** : une situation voisine réduit progressivement l'aide.
6. **Entraînement** : consolidation, maîtrise puis approfondissement.
7. **Preuve de maîtrise** : une tâche sans aide atteste la capacité.
8. **Remédiation ciblée** : l'erreur observée déclenche une action précise.
9. **Re-test isomorphe** : de nouvelles données testent la même structure.
10. **Réactivation** : la capacité revient notamment à J+7 et J+21.
11. **Transfert** : un problème mobilise plusieurs capacités ou contextes.

Les parcours qualifient la nature de l'aide, pas une simple couleur de
difficulté :

- **Consolidation** : étapes explicites, exemples proches et coups de pouce ;
- **Maîtrise** : tâches standard, choix de méthode et rédaction autonome ;
- **Approfondissement** : recherche, transfert, démonstration ou modélisation.

Un enrichissement ne peut pas être nécessaire pour réussir le parcours
Maîtrise. Chaque chapitre cible aussi deux évaluations comparables A/B avec
barèmes et corrigés réservés au professeur, diagnostics par erreur,
remédiations et re-tests.

## Architecture canonique d'un chapitre

La cible éditoriale d'un chapitre complet comprend :

1. une ouverture adaptable ;
2. un contrat de capacités ;
3. un diagnostic de prérequis ;
4. une orientation ;
5. le cours essentiel ;
6. les démonstrations exigibles ;
7. les méthodes ;
8. les exercices par capacité et parcours ;
9. un TD ou fil rouge ;
10. une auto-évaluation ;
11. un diagnostic d'erreurs ;
12. une remédiation ;
13. un re-test ;
14. une évaluation A ;
15. une évaluation B ;
16. une réactivation ;
17. un transfert ;
18. les ressources professeur.

La cible quantitative d'exercices principaux est :

```text
TARGET_EXERCISES = min(50, max(24, 6 × nombre_de_capacités))
```

Chaque capacité doit disposer d'au moins trois exercices dédiés et apparaître
dans au moins deux parcours. Les QCM, automatismes, projets, diagnostics et
évaluations ne gonflent pas artificiellement ce seuil. Cette formule est une
exigence de conception approuvée, pas une preuve qu'elle est atteinte dans les
51 chapitres actuels.

## Statuts, READY et release

Les statuts minimaux prévus incluent :

- `draft` et `generated` ;
- `needs_math_review`, `needs_program_review`, `needs_editorial_review` et
  `needs_visual_review` ;
- `approved` ;
- `deprecated` et `rejected`.

Les variantes historiques telles que `review_required` ou `needs_review`
restent bloquantes tant qu'une migration et une revue prouvées ne les ont pas
qualifiées. `generated` signifie produit, jamais approuvé.

`READY` est un état dérivé de preuves, pas une étiquette déclarative. Une
baseline peut rendre un gate de non-régression vert tout en laissant la release
rouge. `--fail-on-new` protège contre l'aggravation de la dette ;
`--release-strict` juge la publiabilité réelle.

## Variantes élève et professeur

La variante élève ne doit contenir :

- aucun corrigé complet, grille de réponses ou clé de correction ;
- aucun barème ou conseil réservé à l'enseignant ;
- aucune note de mise en œuvre professeur ;
- aucun identifiant technique tel que `1SPE-*` ou `TSPE-*` ;
- aucun placeholder, label non résolu ou renvoi provisoire ;
- aucun contenu hors programme présenté comme exigible.

La variante professeur ajoute les corrigés détaillés, barèmes, erreurs
anticipées, stratégies alternatives, critères de réussite, liens au programme
et conseils de différenciation. Les mêmes objets ne doivent pas être dupliqués
manuellement entre variantes : leur inclusion est gouvernée par les
métadonnées et l'assembleur.

[BUILD_PRODUCERS.yaml](audit/BUILD_PRODUCERS.yaml) déclare actuellement 22
assemblages : deux par manuel de mathématiques et sept par livre NSI. La cible
humaine retient douze éditions canoniques, élève et professeur pour chacun des
six manuels. Les variantes NSI `methodes`, `remediation`, `amenagee`,
`evaluations` et `projets` doivent donc rester des ressources séparées tant
qu'un arbitrage de gouvernance n'a pas réconcilié ce registre.

## Programmes officiels 2026-2027

Les références ci-dessous sont celles des textes officiels identifiés. La
colonne « réserve locale » rend visibles les lacunes du registre actuel.

| Périmètre | Texte applicable | Référence officielle | Effet | Réserve locale au 13 août |
|---|---|---|---|---|
| `1SPE` | Programme de spécialité mathématiques de Première | [`MENE2602917A`](https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A) | Rentrée 2026 | Source texte déposée et empreintée |
| Épreuve anticipée 1SPE | Modalités à compter de la session 2027 | [`MENE2515469N`](https://www.education.gouv.fr/bo/2025/Hebdo24/MENE2515469N) | Session 2027 | `source_deposee: false` dans le registre |
| `TSPE_2026_2027` | Programme de spécialité mathématiques de Terminale | [`MENE1921246A`](https://www.education.gouv.fr/bo/19/Special8/MENE1921246A.htm) | Rentrée 2020, encore applicable | Registre local erroné, voir ci-dessous |
| `TCOMPL` | Mathématiques complémentaires | [`MENE1921265A`](https://www.education.gouv.fr/bo/19/Special8/MENE1921265A.htm) | Rentrée 2020 | Source texte déposée et empreintée |
| `TEXPERTES` | Mathématiques expertes | [`MENE1921264A`](https://www.education.gouv.fr/bo/19/Special8/MENE1921264A.htm) | Rentrée 2020 | Source texte déposée et empreintée |
| `1NSI` | Spécialité NSI de Première | [`MENE1901633A`](https://www.education.gouv.fr/bo/19/Special1/MENE1901633A.htm) | Rentrée 2019 | PDF local présent, mais NOR et URL absents du registre |
| `TNSI` | Spécialité NSI de Terminale | [`MENE1921247A`](https://www.education.gouv.fr/bo/19/Special8/MENE1921247A.htm) | Rentrée 2020 | Programme déposé ; modalités 2026 non déposées |

Le registre courant attribue encore à TSPE le NOR `MENE1921262A`. Ce NOR
correspond aux enseignements de spécialité de Terminale **STMG**, pas au
programme de spécialité mathématiques. C'est un P0 de provenance à corriger
dans un lot réglementaire séparé ; le présent README ne le masque ni ne modifie
le registre.

Pour 1NSI, une preuve officielle archivée sous
[audit/sources/1nsi](audit/sources/1nsi/) confirme `MENE1901633A`, mais l'entrée
`SRC-BO2019-NSI-PREMIERE` du registre ne porte encore ni `arrete` ni `url`.

Les modalités d'épreuve avec `source_deposee: false` sont des instructions ou
des références à déposer, pas des preuves réglementaires achevées. Les
modalités TNSI actuellement décrites comme écrit de 3 h 30 et pratique de 1 h
ne doivent donc pas être annoncées comme officiellement vérifiées avant dépôt
et empreinte de leur texte.

Le nouveau programme de Terminale publié en 2026 s'applique à la rentrée
2027-2028. Il reste hors du parcours exigible de l'édition 2026-2027.

## Enrichissements hors programme

Un enrichissement n'est conservé que s'il :

- porte visiblement l'étiquette « Pour aller plus loin » ;
- possède une qualification machine d'enrichissement ;
- est absent des prérequis de maîtrise et du parcours obligatoire ;
- est exclu des évaluations A/B et entraînements obligatoires ;
- ne peut pas être interprété comme exigible en 2026-2027 ;
- reçoit les mêmes revues scientifique et éditoriale que le reste.

Les points sensibles incluent la forme canonique générale, l'exponentielle,
les logarithmes et limites, les listes Python, les simulations et statistiques,
les répétitions de Bernoulli, la loi binomiale, les contenus de Terminale et les
attendus de l'épreuve anticipée. La richesse d'un contenu ne justifie jamais un
glissement de programme.

## Spécificités NSI et code Python

Le code publié doit provenir d'un fichier `.py` canonique. Pour chaque exemple,
la chaîne doit :

1. parser le fichier, notamment avec `ast.parse` ;
2. l'exécuter dans un environnement contrôlé ;
3. tester les cas normaux, limites et la terminaison ;
4. capturer sa sortie ;
5. comparer cette sortie à celle insérée dans le manuel.

Les guillemets typographiques et les opérateurs mathématiques Unicode utilisés
à la place de la syntaxe Python sont interdits. Les boucles `while`, seuils,
indices, complexités et sorties saisies manuellement demandent une attention
particulière.

Le dossier [NSI/corpus_nsi](NSI/corpus_nsi/) est une matière première importée
par subtree. Sa présence ne vaut pas approbation : tout objet repris doit être
attribué à une capacité, adapté à la charte, exécuté si nécessaire, relu et
validé séparément pour les variantes.

## Arborescence du dépôt

Cette carte montre les chemins structurants, pas tous les fichiers suivis :

```text
Manuels_Nexus/
├── AGENTS.md                         règles de travail applicables
├── CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md
├── Mathematiques/manuel-maths/       quatre manuels de mathématiques
│   ├── chapitres/                    objets .tex et contrats YAML
│   ├── gabarits/                     classes, styles, polices et composants
│   ├── scripts/                      assemblage, vérification et PDF
│   ├── tests/                        tests disciplinaires et éditoriaux
│   ├── sources/                      textes officiels et empreintes
│   └── build/                        huit PDF canoniques et artefacts locaux
├── NSI/                              deux manuels NSI
│   ├── chapitres/                    objets pédagogiques 1NSI et TNSI
│   ├── manifests/books/              ordre canonique des livres NSI
│   ├── corpus_nsi/                   corpus importé, non approuvé par défaut
│   ├── gabarits/                     pile LaTeX et extensions NSI
│   ├── scripts/                      assemblage, code et gates corpus
│   ├── tests/                        tests NSI
│   ├── sources/                      programmes déposés
│   └── build/                        quatre PDF canoniques et artefacts locaux
├── scripts/                          inventaire, manifests et gouvernance
├── tests/                            tests transversaux
├── audit/                            preuves, baselines, registres et rapports
├── docs/programmes/                  registre réglementaire de collection
├── docs/codex/                       gates et documentation du cadre qualité
├── docs/superpowers/                 conceptions approuvées et plans
└── .github/workflows/                trois workflows CI
```

Les dossiers `build/` contiennent des artefacts suivis, mais ne sont pas une
source éditoriale. Le dossier `audit/` mélange preuves générées, décisions,
baselines et rapports datés : leur type et leur provenance doivent être lus
avant de leur attribuer une autorité.

## Architecture des sources

Les objets pédagogiques sont principalement des fichiers `.tex` dont les
métadonnées structurées commencent par `% META:`. Elles portent notamment un
identifiant stable, un chapitre, un type d'objet, un statut et des relations
vers les capacités ou corrections.

Les contrats YAML de chapitre expriment la couverture attendue. Les schémas
JSON sous [audit/schemas/v1](audit/schemas/v1/) et les schémas disciplinaires
valident les formes de données. Les identifiants sont internes et doivent
rester disponibles pour les manifests et audits sans apparaître dans le PDF
élève.

Les rapports Markdown ne sont pas la source unique des nombres. L'inventaire
recalcule les faits depuis les fichiers suivis, le graphe de références, les
assemblages et les builds observés. Une affirmation « complet » dans une
ancienne directive est invalide lorsqu'elle contredit ce calcul.

La source locale canonique est la racine du clone Git courant, et le distant
déclaré est `github.com/cyranoaladin/manuels-nexus`. Un contenu retenu ne doit
pas survivre uniquement dans un dossier externe, un worktree oublié, `/tmp` ou
un scratchpad : il doit être intégré ici par une opération Git contrôlée.

Les statuts `needs_review` du corpus NSI, comme tout statut de revue requise,
sont non publiables. Un import ou une génération ne peut pas s'auto-approuver.

## Assembleurs et manifests

L'assembleur Mathématiques
[assemble_manuel.py](Mathematiques/manuel-maths/scripts/assemble_manuel.py)
gère `1SPE`, `TSPE_2026_2027`, `TCOMPL` et `TEXPERTES`. La liste littérale
`CHAPITRES` est actuellement la source statique lue par l'inventaire ; les
groupes `MANUAL_CHAPTERS` sont dérivés de ses préfixes. Cette architecture
fonctionne, mais laisse l'ordre des chapitres codé dans Python.

L'assembleur NSI [assemble_manuel.py](NSI/scripts/assemble_manuel.py) gère
`1NSI` et `TNSI`. Il lit la liste et l'ordre depuis
[1NSI.json](NSI/manifests/books/1NSI.json) et
[TNSI.json](NSI/manifests/books/TNSI.json). Ses sept variantes ne sont pas
toutes des éditions canoniques de collection.

Le [manifeste global](audit/BUILD_MANIFEST.json) agrège uniquement les reçus
observés que `scripts/build_manifest.py` accepte. Il ne doit pas être rempli à
partir du seul examen statique des assembleurs.

## Charte graphique v5/v6

La pile réellement observée est additive :

```text
nexus-manuel.cls historique
  -> nexus-manuel-v5.cls
    -> nexus-charte-v6.sty et modules v6
      -> nexus-pont-v6.sty
```

La classe v5 charge la classe historique. Le style v6 ajoute la couverture,
les pages froides, les boîtes, exercices, figures bibliographiques et décors.
Le pont remappe une partie des composants historiques vers la nouvelle charte.
Il ne couvre pas encore exhaustivement exercices, corrections et coups de
pouce.

Neuf fichiers structurants v5/v6 sont identiques entre les deux disciplines,
mais restent **physiquement dupliqués** dans
`Mathematiques/manuel-maths/gabarits/` et `NSI/gabarits/`. D'autres éléments
divergent : Mathématiques possède notamment un rail de marge que la classe NSI
n'emploie pas, et les ouvertures de chapitre ne partagent pas toutes le même
mécanisme.

Le gate `scripts/check_charte_sync.py` est rouge au SHA audité. Son périmètre
signale `gabarits/nexus-manuel.cls` et `scripts/pdf_integrity.py`, mais ne
couvre pas encore les neuf modules réellement partagés. Une copie globale
d'une discipline vers l'autre serait donc dangereuse.

La cible est un noyau physique commun avec surcharges disciplinaires explicites
et testées. Elle demande un addendum de conception avant migration. Aucune
revue visuelle exhaustive des douze PDF sous v6 n'est enregistrée.

Les assembleurs complets exécutent trois passes LuaLaTeX. Ce minimum est requis
pour stabiliser références, sommaires et éléments de navigation ; il ne prouve
pas à lui seul l'absence de collision ou de texte coupé.

La cible LaTeX/PDF interdit les numéros de page métier codés en dur, les textes
cachés, collisions et débordements. Les notes marginales ont un fallback dans
le flux, les ouvertures acceptent des contenus variables et les en-têtes
reflètent la rubrique réelle. Le PDF final porte métadonnées, signets, liens,
sommaire cliquable et polices incorporées, puis passe les préflights numérique
et imprimeur.

## Pipeline de build et de preuve

Un build canonique complet suit conceptuellement :

```text
sélection manuel + variante
  -> rendu du master .tex
  -> trois passes LuaLaTeX avec trace .fls
  -> contrôles de texte de la variante élève
  -> préflight PDF
  -> promotion atomique des artefacts
  -> reçu *.receipt.json
  -> enregistrement dans audit/BUILD_MANIFEST.json
  -> inventaire et gates de collection
```

Le mode local compose et remplace des artefacts sous `build/`, puis s'arrête
avant la publication des preuves. Le mode `--record-observed` ajoute le
préflight et le reçu, capture versions d'outils et empreintes, puis appelle le
recorder global. Il doit être intentionnel, exécuté sur un arbre propre et
suivi d'une revue du diff.

Un reçu valide relie au minimum le manuel, la variante, le master, le PDF, le
journal, le fichier `.fls`, le préflight, les empreintes, le `run_id`, les
outils et les paramètres de reproductibilité. L'enregistrement échoue si ces
preuves sont incomplètes ou incohérentes.

Au SHA audité, aucun reçu canonique `*.receipt.json` ni artefact canonique
`*.preflight.json` n'est enregistré et le manifeste contient `"builds": []`.
Des contrôles de préflight NSI ont été exécutés ponctuellement avec succès sur
les quatre PDF NSI ; sans artefact archivé ni reçu, ils ne constituent ni une
preuve de préflight enregistrée ni un build observé.

## Prérequis et installation

La CI d'audit utilise Python 3.12.11 sur Ubuntu 24.04. Pour reproduire les
contrôles et builds, prévoir :

- Python 3.12 et les dépendances de `requirements-ci-audit.txt` ;
- LuaLaTeX et TeX Live, notamment les paquets français, scientifiques,
  `latex-extra`, `luatex` et les polices recommandées ;
- les polices JetBrains Mono, Libertinus, Montserrat et TeX Gyre utilisées par
  la collection ;
- Poppler (`pdfinfo`, `pdffonts`, `pdftotext`), qpdf et ImageMagick pour les
  preuves PDF et visuelles ;
- Pandoc lorsque les workflows NSI concernés le demandent ;
- Git et un système de fichiers permettant les promotions atomiques.

Pour l'environnement Python d'audit reproduit par la CI :

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --disable-pip-version-check \
  --no-deps --requirement requirements-ci-audit.txt
python -m pip check
```

Les deux sous-projets proposent aussi des cibles `setup`, à examiner avant
exécution car elles écrivent leurs environnements et installent des polices :

```bash
make -C Mathematiques/manuel-maths setup
make -C NSI setup
```

Il n'existe pas encore de commande racine hermétique construisant exactement
les douze éditions. Les commandes cibles `make quality` ou
`make release-candidate` mentionnées dans le cahier des charges sont des
objectifs futurs, pas des interfaces disponibles.

Seuls les fichiers `.env.example` sont suivis. Un `.env` réel, une clé, un
secret ou une donnée personnelle ne doit jamais être versionné. Les fonctions
RAG ou base de données ne sont pas une précondition prouvée des builds complets
documentés ci-dessous.

## Construire un manuel localement

Depuis la racine, exemples de builds locaux sans enregistrement de preuve :

```bash
(cd Mathematiques/manuel-maths && \
  python3 scripts/assemble_manuel.py --manual 1SPE --variant eleve)
(cd Mathematiques/manuel-maths && \
  python3 scripts/assemble_manuel.py --manual 1SPE --variant professeur)

(cd NSI && \
  python3 scripts/assemble_manuel.py --book 1NSI --variant eleve)
(cd NSI && \
  python3 scripts/assemble_manuel.py --book 1NSI --variant professeur)
```

Remplacer le manuel par l'une des valeurs exposées par `--help` :

- Mathématiques : `1SPE`, `TSPE_2026_2027`, `TCOMPL`, `TEXPERTES` ;
- NSI : `1NSI`, `TNSI`.

Ces commandes écrivent sous les dossiers `build/` suivis. Elles ne sont donc
pas des diagnostics en lecture seule. Vérifier le statut Git avant et après,
ne pas écraser un WIP non audité et ne pas présenter le PDF produit comme un
build observé.

## Enregistrer un build observé

Exemples intentionnels, à lancer sur un arbre propre après validation des
sources :

```bash
(cd Mathematiques/manuel-maths && \
  python3 scripts/assemble_manuel.py --manual 1SPE --variant professeur --record-observed)
(cd NSI && \
  python3 scripts/assemble_manuel.py --book 1NSI --variant professeur --record-observed)
```

`--record-observed` écrit ou met à jour les PDF, journaux, traces, préflights,
reçus et le manifeste global. Toute exécution doit être suivie de :

```bash
git status --short
git diff --check
git diff -- audit/BUILD_MANIFEST.json
```

Un build observé n'autorise aucune mise à jour automatique de baseline et ne
remplace ni comparaison des variantes ni revue visuelle. Pour démontrer la
reproductibilité, la cible reste deux builds contrôlés depuis des clones
propres avec comparaison des artefacts et environnements.

## Tests et gates

Contrôles structurels et de gouvernance depuis la racine :

```bash
git diff --check
python3 scripts/inventory_collection.py --check --require-clean
python3 scripts/check_charte_sync.py
python3 scripts/inventory_collection.py --check --validate-model --require-clean
python3 scripts/inventory_collection.py --check --fail-on-new --require-clean
python3 scripts/inventory_collection.py --check --release-strict --require-clean
```

Tests transversaux observés lors de l'audit :

```bash
python3 -m pytest tests -q
python3 -m pytest -q --collect-only
```

Les familles de gates sont décrites dans
[QUALITY_GATES.md](docs/codex/QUALITY_GATES.md) : dépôt, modèle, mathématiques,
programme, pédagogie Nexus, Python, variantes, LaTeX/visuel, PDF,
reproductibilité et release.

Interprétation impérative :

- un code non nul est un échec, sauf contrat explicitement conçu pour observer
  un rouge déterministe sans le masquer ;
- `--fail-on-new` compare les empreintes et qualifications de dette ;
- une disparition d'anomalie est une amélioration, sa réapparition une
  régression ;
- `--release-strict` doit rester rouge tant que le produit n'est pas réellement
  publiable ;
- `skip`, `xfail`, suppression de test ou régénération globale de baseline ne
  sont pas des corrections.

Pour une PR de release, les tests complets, douze builds, préflights,
comparaisons élève/professeur, contrôles visuels, reproductibilité et trois
gates de modèle/dette/release sont obligatoires. Une modification Markdown
seule ne justifie pas de relancer les builds complets, mais doit préserver et
documenter leur état.

## Intégration continue

Trois workflows existent :

1. [CI audit collection Phase 0](.github/workflows/ci-audit-collection.yml)
   valide données structurées, lint, typage partiel, tests, génération double
   de six artefacts de pilotage et codes des gates. Il se déclenche sur les PR,
   manuellement et, pour les pushes, encore uniquement sur l'ancienne branche
   `finalisation/collection-v1`. Son contrat historique attend certains gates
   plus verts que l'état actuel.
2. [CI manuel mathématiques](.github/workflows/ci-mathematiques.yml) contrôle la
   synchronisation de charte, les schémas, les chapitres modifiés et un
   spécimen sur PR ou push `main` selon des filtres de chemins. Il ne construit
   pas les huit éditions mathématiques complètes.
3. [CI manuels NSI](.github/workflows/ci-nsi.yml) exécute tests NSI, accents,
   spécimen, vérification Python et compilation des chapitres modifiés. Il ne
   construit pas les quatre éditions NSI complètes.

Les filtres de synchronisation de charte citent encore un sous-ensemble de
fichiers historiques et ne couvrent pas les neuf modules v5/v6 dupliqués. Les
actions Mathématiques et NSI ne prouvent pas une construction de collection.
Il n'existe donc pas encore de CI orchestrant exactement les douze PDF, leurs
reçus, préflights et comparaisons.

## Workflow obligatoire de contribution

Toute intervention suit ce cycle :

1. lire `AGENTS.md`, le cahier des charges et les instructions plus proches ;
2. relever branche, SHA, statut, historique court, diff et `diff --check` ;
3. préserver tout WIP et identifier la source de vérité applicable ;
4. reproduire et qualifier le problème avant de proposer un correctif ;
5. mener un brainstorming et faire approuver la conception pour tout nouveau
   développement ou changement de comportement ;
6. écrire un plan de pas de 2 à 5 minutes et obtenir sa validation humaine ;
7. pour le code ou un défaut, appliquer strictement Red → Green → Refactor ;
8. implémenter le plus petit lot cohérent sans affaiblir les gates ;
9. confier à des sous-agents seulement les tâches réellement indépendantes ;
10. exécuter tests ciblés, gates affectés et contrôles adversariaux ;
11. demander une revue indépendante, puis un point de validation utilisateur ;
12. committer atomiquement avec preuves et produire le compte rendu imposé.

Lire avant d'écrire, YAGNI, DRY et absence de sur-ingénierie s'appliquent. Une
correction mathématique critique ajoute un test de régression et ne peut pas
être auto-approuvée par son auteur.

## Revue indépendante et approbation humaine

La chaîne de revue attendue est :

```text
Writer
  -> Scientific Reviewer
  -> Programme Reviewer
  -> Editorial + Student/Professor Reviewer
  -> Build/PDF Reviewer
  -> approbateur humain final
```

Une recommandation de modèle est consultative. Les identités, valeurs,
dérivées, racines, signes, probabilités, algorithmes et sorties doivent être
vérifiés localement. SymPy est utile pour une assertion, mais ne remplace ni la
preuve ni la revue humaine d'une démonstration.

Une baseline visuelle ne change qu'avec approbation explicite, pages
concernées, raison, versions d'outils, anciens/nouveaux hashes et montage
avant/après. La CI ne met jamais à jour une baseline.

L'utilisateur est l'approbateur humain final de chaque manuel, séparément,
après remise des preuves scientifiques, programme, éditoriales et PDF.

## Git, commits et interdictions

Ne jamais travailler directement sur `main`. Préserver le WIP et utiliser des
commits atomiques portant notamment les préfixes :

- `[AUDIT]`, `[MATH]`, `[PROGRAMME]`, `[PEDAGOGIE]` ;
- `[LATEX]`, `[PYTHON]`, `[PDF]`, `[TESTS]`, `[CI]`, `[DOCS]`.

Ne pas mélanger dans un commit correction mathématique, refactorisation,
baseline visuelle, migration de données ou changement réglementaire.

Sans instruction humaine explicite, sont interdits :

- `git reset --hard`, `git clean`, `git restore`, `git checkout --` ;
- `git rebase`, `git merge` ;
- `git push --force`, `git push --force-with-lease` ;
- réécriture ou déplacement de tags ;
- fusion dans `main`.

Avant commit : `git diff --check`, statut, tests ciblés et gates affectés. Avant
push sensible : examiner secrets, données personnelles, bases et artefacts.

## Consultation externe Chutes

Lorsque le MCP Chutes est disponible :

1. effectuer un smoke test ;
2. utiliser seulement les modèles réellement listés ;
3. ne transmettre ni secret, ni clé, ni donnée personnelle ;
4. demander des avis indépendants par domaine ;
5. vérifier localement chaque recommandation ;
6. consigner les consultations utiles sous [audit/chutes](audit/chutes/).

Chutes n'est ni une source d'autorité ni une approbation. Lors de l'audit du 13
août, le catalogue de modèles était accessible, puis la consultation a été
refusée avec HTTP 402 pour quota insuffisant. Aucune expertise externe
exploitable n'a donc été retenue pour cet audit.

<!-- BEGIN CURRENT AUDITED STATE -->

## État courant audité — 13 août 2026

### Identification et portée

- état métier : `1d0c3fdaa24f17d938696b615d23373579042b95` ;
- branche : `integration/1spe-bo2026-traceability` ;
- rapport ajouté au commit : `b5c6f9f113dc7be0b33765bb6229b6d4e6611467` ;
- nature : audit en lecture seule des six manuels, de la charte, des sources de
  vérité, assemblages, PDF, tests et gates ;
- verdict : **NO-GO publication**.

Le commit du rapport est postérieur à l'arbre métier qu'il décrit. Les commits
de conception et de documentation ultérieurs ne constituent pas une nouvelle
validation des manuels.

### Mesures

- 6 manuels, 51 chapitres, 2 860 objets ;
- 12 PDF canoniques, 2 026 pages ;
- 0 chapitre `READY` ;
- 2 911 entrées objet/contrat à statut bloquant ;
- 67 bloqueurs `release-strict` ;
- 10 PDF de corpus non attribués, hors surface canonique ;
- 119 nouvelles empreintes et 119 qualifications manquantes, soit 238 motifs
  rapportés par les gates de baseline ;
- manifeste global : `"builds": []` ;
- aucun reçu canonique `*.receipt.json` ni artefact canonique
  `*.preflight.json` enregistré ;
- des contrôles de préflight NSI ponctuels ont été verts sur les quatre PDF
  NSI, mais sans preuve archivée ni build observé.

### P0 ouverts

1. **Fuites élève.** Le PDF 1SPE élève contient sept pages « Correction et
   diagnostics » avec réponses. Le PDF TSPE élève expose une clé de correction,
   des barèmes et `TSPE-DERIVATION-CONVEXITE`.
2. **Contenu coupé.** Le QCM Suites 1SPE atteint notamment des dépassements de
   `163.04901 pt`, `110.95308 pt` et `224.38853 pt`. L'ouverture TSPE
   « Géométrie dans l'espace » dépasse d'environ `127.741 pt`.
3. **Renvois et identifiants.** Le PDF élève 1SPE contient 50 renvois
   provisoires sur 37 pages ; le PDF TSPE en contient 13 sur neuf pages.
4. **Provenance TSPE.** Le registre porte `MENE1921262A` (STMG) au lieu de
   `MENE1921246A` (spécialité mathématiques).

Le contrôle courant des fuites élèves ne recherche pas encore toutes les
formulations observées. Le préflight Mathématiques accepte les grands
débordements représentatifs que le préflight NSI refuse.

### Source de vérité et charte

- [SOURCE_DE_VERITE.md](SOURCE_DE_VERITE.md) retient douze éditions mais affiche
  encore 2 751 objets au lieu de 2 860 ;
- `BUILD_PRODUCERS.yaml` déclare 22 assemblages ;
- [ETAT_COLLECTION_2026_2027.md](ETAT_COLLECTION_2026_2027.md) porte encore un
  ancien total de 2 782 objets ;
- les rapports d'anomalies non qualifiées annoncent zéro alors que 119
  empreintes nouvelles et 119 qualifications manquantes sont observées ;
- neuf modules v5/v6 identiques restent dupliqués physiquement ;
- le pont v6 ne couvre pas tous les composants et aucune revue visuelle
  exhaustive des douze manuels n'est enregistrée ;
- le gate de synchronisation est rouge et son périmètre est incomplet.

### PDF observés

- les douze PDF sont A4, passent `qpdf --check` et incorporent leurs polices ;
- aucun n'est balisé : `Tagged: no` ;
- les quatre PDF NSI ont des métadonnées, 34 à 51 signets et 34 à 52 liens ;
- les huit PDF Mathématiques ont des métadonnées vides, zéro signet et zéro
  lien ;
- l'absence de reçus empêche de les qualifier de reproductibles au SHA.

### Gates et tests

Verts observés :

- `git diff --check` ;
- inventaire `--check --require-clean` ;
- `qpdf --check` et polices incorporées sur les douze PDF ;
- contrôles de préflight NSI ponctuellement verts sur les quatre PDF NSI, sans
  artefact canonique archivé ni valeur de build observé ;
- tests ciblés du pont et de la pile v5/v6.

Rouges observés :

| Commande | Code / résultat |
|---|---|
| `python3 scripts/check_charte_sync.py` | code 1 |
| `python3 scripts/inventory_collection.py --check --validate-model --require-clean` | code 6, 238 motifs |
| `python3 scripts/inventory_collection.py --check --fail-on-new --require-clean` | code 5, 238 motifs |
| `python3 scripts/inventory_collection.py --check --release-strict --require-clean` | code 7, 67 bloqueurs |
| `python3 -m pytest tests -q` | 1 057 réussis, 9 échoués |
| suite Pytest complète | collecte bloquée après 5 013 tests |

La collecte complète échoue par collision entre deux modules de test nommés
`assemble`. Les codes rouges sont des faits à préserver jusqu'à correction ;
ils ne doivent pas être changés en succès documentaire.

### CI et limite de preuve

Les workflows construisent des spécimens ou chapitres modifiés, pas les douze
manuels complets. Aucun orchestrateur racine ne produit exactement les douze
éditions et leurs preuves. Le fait que des PDF soient suivis par Git ne prouve
donc pas leur reproductibilité depuis un clone propre.

<!-- END CURRENT AUDITED STATE -->

## Roadmap approuvée

La stratégie retenue produit la collection par vagues avec gates communs :

- **Wave 0 — infrastructure commune** : réconcilier source de vérité, registre
  officiel, assemblages, baseline, dashboard, tests et chaîne de preuves ;
- **Wave 1 — première période** : rendre utilisables les premiers chapitres de
  `1SPE`, `1NSI`, `TSPE_2026_2027` et `TNSI` ;
- **Wave 2 — quatre manuels principaux** : finaliser et geler les candidats des
  quatre enseignements principaux ;
- **Wave 3 — options Terminale** : finaliser `TCOMPL`, puis `TEXPERTES` ;
- **Wave 4 — collection et releases** : audit transversal, builds finaux,
  préflights, reproductibilité et approbations manuel par manuel.

L'état actuel est **Wave 0 incomplète et à restabiliser**. Aucun pourcentage
d'avancement n'est inféré du nombre de fichiers ou de chapitres.

L'ordre de reprise recommandé est : sceller les douze éditions, écrire les
tests rouges des P0, corriger fuites et débordements, réparer la provenance,
qualifier les 119 empreintes individuellement, centraliser le noyau de charte,
ajouter l'orchestrateur, reconstruire deux fois et mener les revues humaines.

## Décisions humaines acquises

La [conception premium des six manuels](docs/superpowers/specs/2026-08-12-finalisation-premium-six-manuels-design.md)
consigne :

- `HUM-2026-08-11-WAVES` : production par vagues avec gates communs ;
- `HUM-2026-08-11-VISUAL-MAIN` : maquette actuelle de `main`, correctifs
  anti-collision inclus, comme référence visuelle ;
- `HUM-2026-08-11-1SPE-INTEGRATION` : port sélectif des apports programme et
  traçabilité, sans fusion automatique de la branche source ;
- `HUM-2026-08-11-ENRICHMENTS` : enrichissements conservés seulement s'ils sont
  explicitement non exigibles et hors évaluations obligatoires ;
- `HUM-2026-08-11-BASELINE-WAVE0` : qualification de baseline empreinte par
  empreinte pendant Wave 0, sans suppression pour obtenir du vert ;
- `HUM-2026-08-12-FINAL-APPROVER` : approbation humaine finale par manuel.

Ces décisions cadrent le travail. Elles ne valent ni validation scientifique,
ni revue visuelle des PDF actuels, ni autorisation de release.

## Questions ouvertes

Les arbitrages humains encore nécessaires incluent :

- l'architecture physique du noyau de charte et de ses surcharges ;
- la surface canonique exacte des variantes et ressources NSI ;
- la qualification individuelle des 119 empreintes et dispositions ;
- le dépôt des sources officielles des modalités d'épreuve ;
- la stratégie de correction des fuites élève sans duplication de contenus ;
- l'harmonisation des préflights Mathématiques et NSI ;
- la revue visuelle v6 et l'approbation séparée de chacun des six manuels ;
- le traitement des rapports historiques contradictoires.

Une question ouverte ne doit pas être résolue implicitement par un générateur,
une copie de charte ou une mise à jour de baseline.

## Carte documentaire

### Autorités et exigences

- textes officiels liés dans la section programmes ;
- [CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md](CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md) ;
- [AGENTS.md](AGENTS.md) ;
- [QUALITY_GATES.md](docs/codex/QUALITY_GATES.md).

### Conceptions et décisions approuvées

- [conception premium des six manuels](docs/superpowers/specs/2026-08-12-finalisation-premium-six-manuels-design.md) ;
- [conception du README d'audit](docs/superpowers/specs/2026-08-13-readme-racine-autosuffisant-design.md) ;
- [plan d'implémentation du README](docs/superpowers/plans/2026-08-13-readme-racine-autosuffisant.md) ;
- [décision de qualification de baseline](audit/BASELINE_QUALIFICATION_DECISION.md).

### État généré et preuves

- [inventaire JSON](audit/INVENTAIRE_COLLECTION.json) et
  [synthèse Markdown](audit/INVENTAIRE_COLLECTION.md) ;
- [manifeste de builds](audit/BUILD_MANIFEST.json) ;
- [producteurs déclarés](audit/BUILD_PRODUCERS.yaml) ;
- [readiness des chapitres](audit/CHAPTER_READINESS.json) ;
- [baseline d'anomalies](audit/ANOMALIES_BASELINE.json),
  [dispositions](audit/ANOMALY_DISPOSITIONS.yaml) et
  [anomalies non qualifiées](audit/UNQUALIFIED_ANOMALIES.md).

### Audit courant

- [AUDIT_ETAT_PROJET_2026-08-13.md](audit/AUDIT_ETAT_PROJET_2026-08-13.md) :
  passation de référence pour le bloc daté de ce README.

### Historique ou document à confronter aux preuves

- [DIRECTIVES_COLLECTION.md](DIRECTIVES_COLLECTION.md) ;
- [PROMPT_MISSION_COLLECTION.md](PROMPT_MISSION_COLLECTION.md) ;
- [ROADMAP_TERMINALE.md](ROADMAP_TERMINALE.md) ;
- [ETAT_COLLECTION_2026_2027.md](ETAT_COLLECTION_2026_2027.md) ;
- les README disciplinaires et anciens états datés.

Ces documents restent utiles pour l'histoire. Lorsqu'ils annoncent une
complétude ou un total contredit par l'inventaire, ils sont supplantés par les
preuves recalculées.

## Procédure pour un nouvel auditeur

### 1. Établir le contexte Git

```bash
git status --short --branch
git rev-parse HEAD
git log --oneline --decorate -15
git diff --stat
git diff --check
```

Ne pas changer de branche, nettoyer, stasher ou restaurer automatiquement un
WIP inconnu.

### 2. Lire l'autorité applicable

Lire dans l'ordre les textes officiels concernés, le cahier des charges,
`AGENTS.md`, les schémas/gates, les décisions approuvées, puis seulement les
rapports et historiques.

### 3. Recalculer les contrôles minimaux

```bash
python3 scripts/check_charte_sync.py
python3 scripts/inventory_collection.py --check --require-clean
python3 scripts/inventory_collection.py --check --validate-model --require-clean
python3 scripts/inventory_collection.py --check --fail-on-new --require-clean
python3 scripts/inventory_collection.py --check --release-strict --require-clean
python3 -m pytest tests -q
python3 -m pytest -q --collect-only
```

Comparer les codes et sorties au bloc daté. Toute différence impose une mise à
jour de l'audit avant de reprendre ses conclusions.

### 4. Examiner les artefacts

- confirmer les douze chemins PDF canoniques et leurs nombres de pages ;
- rechercher les reçus, préflights et entrées du manifeste ;
- contrôler qpdf, polices, métadonnées, signets, liens et balisage ;
- comparer les textes et objets inclus des variantes élève/professeur ;
- inspecter toutes les pages, avec priorité aux ouvertures, tableaux, code,
  figures, marges, QCM et pages denses.

### 5. Contrôler le fond

- confirmer chaque source officielle, année d'effet, URL et empreinte ;
- échantillonner les preuves mathématiques et résoudre des exercices à
  l'aveugle ;
- parser et exécuter le Python publié ;
- tracer chaque capacité sur les onze maillons Nexus ;
- vérifier les statuts, revues et approbations ;
- rechercher activement fuites professeur, IDs, placeholders et renvois.

### 6. Auditer la dette

Ne jamais accepter globalement les 119 empreintes. Pour chacune, examiner la
cause, le propriétaire, la disposition, la preuve, l'approbateur et le digest
de politique. Une anomalie baselinée peut rester bloquante pour la release.

### 7. Conclure sans surdéclarer

Consigner SHA, branche, tests, gates, P0, décisions et prochaine action. Un
auditeur ne déclare pas « prêt », « complet » ou « conforme » sans build et
inventaire observés au même SHA, gates correspondants et approbations.

## Sécurité, propriété intellectuelle et données personnelles

Le dépôt distant est publiquement visible. Cette **visibilité publique** ne
constitue pas une licence ouverte : aucune licence racine n'est présente au 13
août 2026. Les licences de polices incluses ne s'étendent pas automatiquement
aux contenus, marques ou autres assets. Toute réutilisation externe doit être
autorisée et juridiquement vérifiée.

Ne jamais versionner :

- données d'élèves, copies, notes ou identifiants personnels ;
- mots de passe, tokens, clés API ou chaînes de connexion ;
- fichiers `.env` réels, bases ou exports contenant des secrets ;
- contenus externes dont les droits ne sont pas établis.

Avant push, examiner au minimum les nouveaux fichiers, les `.env`, CSV, bases
SQLite, PDF importés et assets. Chutes ou tout service externe ne reçoit aucune
donnée personnelle ni aucun secret.

## Glossaire

| Terme | Définition opérationnelle |
|---|---|
| Assemblage déclaré | Composition déduite statiquement des sources |
| Baseline | Ensemble d'anomalies connues servant à détecter les régressions |
| Build observé | Build avec reçu, préflight et manifeste cohérents |
| Capacité | Attendu d'apprentissage atomique relié au programme |
| Contrat | Déclaration structurée des objets et preuves d'un chapitre |
| Disposition | Qualification gouvernée d'une empreinte d'anomalie |
| Gate | Contrôle automatique avec critère et code de sortie |
| Manifeste | Registre machine des builds observés et de leur provenance |
| Objet pédagogique | Unité identifiée : cours, exercice, méthode, QCM, etc. |
| P0 | Défaut bloquant : erreur, fuite, non-conformité ou PDF illisible |
| Préflight | Contrôles techniques et éditoriaux appliqués au PDF |
| `READY` | État dérivé d'une chaîne complète de preuves au niveau chapitre |
| Release | Artefact figé, prouvé, revu et approuvé pour publication |
| Re-test | Nouvelle tâche de même structure après remédiation |
| Reçu | Preuve JSON d'une exécution de build déterminée |
| Source de vérité | Donnée canonique dont les rapports sont dérivés |
| Variante | Sélection élève, professeur ou ressource séparée |

## Format de compte rendu

Chaque session se termine au minimum par :

```text
ÉTAT <SHA>
Branche :
Phase :
Commits :
Tests :
Gates verts :
Gates rouges :
P0 ouverts :
Décisions humaines :
PR :
Prochaine action :
```

Ne jamais conclure « terminé » tant qu'un gate obligatoire est rouge ou qu'une
approbation requise manque.
