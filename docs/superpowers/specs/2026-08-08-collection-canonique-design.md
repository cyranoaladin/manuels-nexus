# Collection canonique des manuels Nexus - Design

**Date :** 8 aout 2026
**Statut :** approuve par decision humaine
**Branche cible :** `finalisation/collection-v1`
**Lane :** gouvernance de release et inventaire
**Decision de publication :** inchangee ; `release-strict` reste rouge

## 1. Objectif

Creer, dans le depot `Manuels_Nexus`, une seule arborescence de reference qui
regroupe les sources de travail retenues, les outils necessaires a leur build,
les manifests et les livrables deja produits pour les six manuels modelises :

- `1SPE` ;
- `TSPE_2026_2027` ;
- `TCOMPL` ;
- `TEXPERTES` ;
- `1NSI` ;
- `TNSI`.

La migration doit aboutir a des deplacements reels. Les anciens emplacements
redondants ne restent ni comme copies, ni comme liens symboliques, ni comme
alias de build. L'historique Git et le rapport de migration conservent la
preuve des chemins d'origine.

Cette operation consolide l'organisation. Elle ne corrige pas le contenu des
manuels et n'ameliore aucun statut de publication.

## 2. Perimetre

### 2.1 Inclus

Les seuls candidats autorises sont les fichiers deja presents dans :

1. le worktree actif `finalisation/collection-v1` ;
2. le repertoire principal du meme depot `Manuels_Nexus`.

Le worktree actif n'est prioritaire qu'en dernier departage entre deux
candidats de completude et de qualite equivalentes. Un artefact plus complet du
repertoire principal ne peut donc pas etre masque par un extrait du worktree.

Sont inclus :

- les chapitres et referentiels propres a chaque manuel ;
- les gabarits, scripts, schemas, tests et configurations utilises pour les
  produire ;
- les manifests d'assemblage et de build ;
- les PDF nommes et les preuves associees deja produits ;
- les rapports d'etat, d'inventaire et de provenance applicables.

### 2.2 Exclus

Sont explicitement hors perimetre :

- tout dossier externe au depot, notamment `00_NSI`, `NSI-recovery` et les
  projets Nexus Reussite voisins ;
- les caches et fichiers temporaires (`__pycache__`, `.pytest_cache`,
  `.mypy_cache`, fichiers auxiliaires LaTeX, repertoires `.run`) ;
- les specimens non attribuables a un manuel final ;
- la creation de contenu manquant pour TNSI ;
- toute correction mathematique, pedagogique ou visuelle ;
- toute declaration de release ou mise a jour de baseline.

## 3. Arborescence cible

```text
collection_canonique/
|-- README.md
|-- INDEX.md
|-- inventory/
|   |-- collection.json
|   |-- migration-report.json
|   |-- migration-state.final.json
|   `-- checksums.sha256
|-- shared/
|   |-- collection/
|   |-- mathematiques/
|   `-- nsi/
`-- manuels/
    |-- 1SPE/
    |   |-- source/
    |   |-- build/
    |   |-- manifests/
    |   `-- meta/
    |-- TSPE_2026_2027/
    |   |-- source/
    |   |-- build/
    |   |-- manifests/
    |   `-- meta/
    |-- TCOMPL/
    |   |-- source/
    |   |-- build/
    |   |-- manifests/
    |   `-- meta/
    |-- TEXPERTES/
    |   |-- source/
    |   |-- build/
    |   |-- manifests/
    |   `-- meta/
    |-- 1NSI/
    |   |-- source/
    |   |-- build/
    |   |-- manifests/
    |   `-- meta/
    `-- TNSI/
        |-- source/
        |-- manifests/
        `-- meta/
```

Chaque `source/` contient uniquement les objets propres au manuel : chapitres,
referentiels, tests et ressources qui ne concernent que ce manuel. Les
declarations d'assemblage ne vivent pas dans `source/` : leur emplacement
autoritaire est `manifests/`. Les composants partages ne sont pas dupliques :
ils vivent sous `shared/collection`, `shared/mathematiques` ou `shared/nsi`.

Chaque `build/` contient seulement les livrables nommes retenus et leurs preuves
directes. Les fichiers de compilation regenerables et temporaires n'y sont pas
conserves. TNSI ne possede pas de `build/` tant qu'aucun manuel final n'existe.

Chaque `meta/` contient au minimum :

- `PROVENANCE.md`, avec anciens chemins, branche, SHA et empreintes ;
- `STATUS.yaml`, genere depuis l'inventaire observe ;
- les decisions humaines propres au manuel, lorsqu'elles existent.

## 4. Responsabilites des composants

### 4.1 `manuels/<ID>/source`

Possede le contenu specifique a un seul manuel. Son interface publique est le
fichier `manifests/assembly.json`, conforme a un schema versionne et contenant
au minimum l'identifiant du manuel, le perimetre cible, la liste ordonnee des
chapitres, les variantes permises et les dependances partagees. Aucun build ne
doit decouvrir des chapitres par balayage implicite d'un autre manuel.

### 4.2 `shared/mathematiques` et `shared/nsi`

Possedent les moteurs d'assemblage, gabarits, schemas, tests, configurations et
ressources communes a leur discipline. Ils ne possedent aucun chapitre ni
referentiel dont le nom identifie un seul manuel. Une modification partagee
doit donc rester unique et servir tous les manuels concernes.

### 4.3 `shared/collection`

Possede l'inventaire global, les schemas de gouvernance, la generation de
rapports et le controle de migration. Il ne compile pas directement le contenu
disciplinaire ; il appelle les interfaces declarees par les manifests.

### 4.4 `inventory`

Contient les sorties observees et regenerables. `collection.json` est la source
machine de l'index humain. `migration-report.json` relie chaque ancien chemin a
son chemin canonique ou a une exclusion motivee. Pendant la migration, le
journal autoritaire vit sous `.migration/control/migration-state.json`, hors de
tous les chemins deplaces. Son etat final est archive dans
`migration-state.final.json`. `checksums.sha256` couvre les sources retenues,
les manifests et les livrables.

### 4.5 Regles d'affectation

L'affectation de chaque fichier est determinee avant tout deplacement :

- un chapitre dont le prefixe correspond a un manuel appartient a
  `manuels/<ID>/source/chapitres` ;
- un referentiel dont l'identifiant ne concerne qu'un manuel appartient a
  `manuels/<ID>/source/referentiel` ;
- un test ou un asset utilise par un seul manuel appartient au meme
  `source/tests` ou `source/assets` ;
- un script, schema, test, gabarit, configuration ou asset utilise par plusieurs
  manuels de la meme discipline appartient a `shared/<discipline>` ;
- l'inventaire global, ses schemas, ses tests et ses rapports appartiennent a
  `shared/collection` ;
- une declaration d'assemblage appartient exclusivement a
  `manuels/<ID>/manifests/assembly.json` ;
- un fichier dont les dependances ne permettent pas une affectation unique
  bloque la migration et doit recevoir une decision explicite.

Le preflight construit un graphe de references pour prouver les usages uniques
ou partages. Le nom du fichier seul ne suffit pas pour classer un composant
ambigu.

## 5. Regles de selection

La selection groupe d'abord les candidats par identite logique :
`manual_id`, `deliverable_role` et `edition`. `deliverable_role` distingue par
exemple `manual_eleve`, `manual_professeur`, `methodes`, `remediation` et
`evaluations`. `artifact_kind` est un critere de classement, jamais une partie
de l'identite ; un specimen et un manuel nomme visant le meme role sont donc
compares. La selection applique ensuite cet ordre :

1. preuve d'attribution et manifeste valides avant fichier non prouve ;
2. perimetre observe le plus complet avant extrait partiel ;
3. gates applicables les plus forts sans nouvelle regression ;
4. assemblage final nomme avant specimen ou artefact intermediaire ;
5. variante explicite avant nom generique ;
6. descendance Git ou SHA de build le plus recent lorsque les candidats sont
   directement comparables ;
7. candidat du worktree actif en dernier departage seulement.

Une date de modification du systeme de fichiers ne constitue jamais, seule,
une preuve de recence ou de qualite. Les decisions utilisent le SHA Git, les
manifests observes, les empreintes et les gates.

Un conflit de contenu entre deux candidats n'est jamais ecrase. La migration
s'arrete pour ce manuel, enregistre les deux empreintes et exige soit une regle
objective deja approuvee, soit une decision humaine. Un perdant suivi par Git
reste recuperable dans l'historique. Un perdant unique non suivi ne peut etre
supprime qu'avec une disposition `discard_approved` contenant son empreinte, sa
taille, sa raison et l'approbateur humain ; sinon il bloque la fin de migration.
La quarantaine de migration est temporaire et ne peut pas subsister dans
l'arborescence canonique declaree terminee.

## 6. Etat initial a rederiver

L'inventaire versionne a `d03c1d8` est historique : il indique encore 1NSI a
1 chapitre, alors que le `HEAD` courant inclut des commits d'integration
ulterieurs. La premiere etape d'execution doit donc regenerer l'inventaire sur
le WIP preserve avant toute selection definitive.

Les observations actuelles servent uniquement d'hypotheses de depart :

| Manuel | Candidat observe | Statut minimal conserve |
|---|---|---|
| `1SPE` | builds eleve, professeur, methodes, remediation et evaluations | non publiable |
| `TSPE_2026_2027` | builds eleve et professeur | non publiable |
| `TCOMPL` | builds eleve et professeur | non publiable |
| `TEXPERTES` | builds eleve et professeur | non publiable |
| `1NSI` | source annoncee a 10 chapitres et builds livre/declinaisons presents | a revalider sur le WIP |
| `TNSI` | 6 ensembles de chapitres observes, aucun livre final | bloque jusqu'a 12/12 |

La migration ne peut transformer aucune de ces hypotheses en assertion sans un
inventaire et un build observes sur le SHA retenu.

## 7. Flux de migration

### 7.1 Preflight immuable et WIP

Avant toute ecriture, l'outil parcourt chaque ancien arbre avec `lstat`, sans
suivre les liens, et produit :

- la liste exhaustive des entrees, y compris fichiers caches, repertoires
  vides, liens symboliques et fichiers speciaux ;
- leur nature suivie ou non suivie par Git ;
- leur mode, taille, `mtime_ns`, empreinte SHA-256 et objet Git eventuel ;
- leur attribution a un manuel ou a un composant partage ;
- leur decision proposee : deplacer, exclure ou bloquer ;
- le `git status`, la branche et le SHA de chaque worktree.

Le preflight refuse un depot dont le WIP n'est pas explicitement inventorie.
Le WIP 1NSI courant doit d'abord etre valide et committe par commits atomiques
propres a son plan existant, sans etre mele a la migration. Aucun stash,
nettoyage ou restauration automatique n'est autorise. Apres gel du preflight,
toute variation de mode, taille, date ou empreinte qui ne correspond pas a une
operation autorisee dans le journal bloque la phase suivante et impose un
nouvel inventaire approuve. Chaque operation autorisee indique l'ancien chemin,
le nouveau chemin, l'empreinte attendue et l'etat qui la permet ; le journal met
a jour l'etat attendu apres son execution.

### 7.2 Etats et construction controlee

`.migration/control/migration-state.json` utilise les etats ordonnes
`inventoried`, `staged`, `verified`, `cutover_in_progress`, `cutover` et
`legacy_removed`. Chaque transition possede ses preconditions et peut etre
reprise sans repeter une suppression.

| Etat | Arbre actif | Operations permises | Invariant requis | Reprise |
|---|---|---|---|---|
| `inventoried` | legacy | generation du plan seulement | snapshot exhaustif gele | regenerer si derive externe |
| `staged` | legacy | copies vers `.migration/staged/collection_canonique` | legacy identique au snapshot | reprendre les copies manquantes |
| `verified` | legacy | aucune mutation de source | staging complet, builds et empreintes valides | corriger le plan puis restager |
| `cutover_in_progress` | aucun, fenetre de maintenance | `git mv`, deplacement des non-suivis et bascule des consommateurs journalises | chaque operation terminee est conforme au journal | reprendre au premier mouvement absent |
| `cutover` | canonique | checks post-cutover seulement | toutes les destinations egalent le staging et tous les consommateurs visent le canonique | corriger puis relancer les checks |
| `legacy_removed` | canonique | retrait des exclusions et du staging verifies | zero entree legacy, zero blocage, checks post-cutover verts | aucune suppression supplementaire hors nouveau plan |

Le staging est une copie inactive qui permet les builds avec une option de
racine explicite. Les fichiers suivis ne quittent les chemins legacy qu'en
`cutover_in_progress`, avec `git mv`. Les artefacts non suivis sont deplaces
vers leur destination finale avec une operation atomique sur le meme systeme
de fichiers. Aucun build concurrent n'est autorise pendant cette fenetre de
maintenance. Le staging reste disponible comme preuve de comparaison jusqu'aux
checks post-cutover, puis disparait a `legacy_removed`. Le resultat final est un
deplacement reel sans copie active residuelle.

### 7.3 Bascule des consommateurs

Avant le cutover, les scripts d'inventaire et les assembleurs recoivent une
option de racine permettant de tester le staging sans changer leur valeur par
defaut legacy. Le checkpoint `cutover` regroupe dans la meme operation logique
les `git mv`, le deplacement des artefacts non suivis et le changement de la
racine par defaut des Makefiles, tests et CI. Il ne peut donc pas etre committe
avec des assembleurs pointant vers des chemins retires. Les chemins historiques
deviennent ensuite interdits par un test de regression. Apres `cutover`, la
reprise ne revient pas automatiquement aux anciens chemins : elle termine la
reconciliation et la suppression, ou s'arrete pour intervention humaine.

### 7.4 Verification avant abandon

Pour chaque fichier retenu, l'empreinte de destination doit etre identique a
l'empreinte candidate. Pour chaque exclusion, le rapport doit contenir une
raison stable. L'invariant exhaustif impose :

```text
entrees_scanees = entrees_deplacees + entrees_exclues + entrees_bloquees
entrees_bloquees = 0 avant legacy_removed
```

Les liens symboliques et fichiers speciaux sont bloquants tant qu'une decision
explicite ne les materialise, ne les reclasse ou ne les exclut. Les builds
cibles sont executes depuis l'arborescence canonique, puis les inventaires sont
regeneres deux fois et compares.

### 7.5 Abandon des anciens chemins

Les anciens emplacements ne sont retires qu'apres les controles precedents et
un controle final de leur empreinte contre le preflight gele. Une racine legacy
n'est abandonnee que si chacune de ses entrees satisfait l'invariant exhaustif.
Aucun lien de compatibilite n'est laisse.

La migration est realisee et verifiee sur `finalisation/collection-v1`. Le
repertoire principal sur `main` reste une entree de comparaison en lecture
seule jusqu'au checkpoint final. La fin physique a un seul tree exige ensuite :

1. une autorisation humaine explicite pour faire avancer `main` en fast-forward
   jusqu'au commit de migration, sans merge ni reecriture ;
2. la reconciliation explicite de chaque fichier non suivi restant dans le
   worktree `main` ;
2. la verification du meme SHA et d'un tree propre ;
3. le retrait du worktree `finalisation-collection-v1` devenu redondant.

Sans cette autorisation, la migration peut etre techniquement validee sur sa
branche, mais ne peut pas etre declaree terminee au sens « un seul emplacement
physique ».

## 8. Gestion des erreurs et reprise

- Une destination existante avec une empreinte differente bloque la migration.
- Un fichier source non attribuable bloque la suppression de son ancien parent.
- Un livrable sans manifeste reste classe `non_attribue` et n'entre pas dans un
  `build/` canonique.
- Un manifeste stale ne valide pas le build courant. S'il est suivi, son ancien
  contenu reste recuperable dans Git et seule sa provenance est reportee. S'il
  est unique et non suivi, il suit la meme disposition humaine que tout perdant
  divergent.
- Un echec de build conserve les anciens chemins et interdit la bascule finale.
- Un echec avant `cutover` laisse les anciens chemins comme source active et
  permet de supprimer uniquement la zone `staged` apres verification de l'etat.
- Un echec apres `cutover` interdit toute suppression non comptabilisee ; la
  commande `--resume` reprend au premier invariant non satisfait.
- Le script de migration est idempotent : un second `--check` ne propose aucun
  changement apres une migration reussie.

## 9. Inventaire, index et gouvernance

`INDEX.md` est genere depuis `inventory/collection.json` et affiche, pour chaque
manuel :

- le nombre observe de chapitres et le perimetre cible ;
- les variantes source et build ;
- les chemins canoniques ;
- le SHA et les empreintes ;
- les gates verts et rouges ;
- `artifact_kind` (`release_named`, `supplement`, `specimen`, `absent`) ;
- `coverage_status` (`complete`, `partial`, `blocked`) ;
- `publication_eligible`, derive uniquement des gates contractuels.

Un livrable `release_named` n'est pas necessairement publiable.
`publication_eligible` reste derive uniquement des gates contractuels.

TNSI doit rester `bloque` avec une raison machine stable tant que le manifeste
ne declare pas exactement les 12 chapitres attendus et qu'un build observe ne
les confirme pas. Aucun PDF TNSI factice, specimen renomme ou assemblage 6/12
n'est publie dans `build/`.

## 10. Validation

### 10.1 Tests de migration

- pour un manuel nomme et un specimen de meme role, selection du seul manuel
  nomme et disposition explicite du specimen ;
- pour un candidat racine complet et un candidat worktree partiel, selection du
  candidat racine complet ;
- pour deux candidats equivalents en role, completude, gates et recence,
  departage en faveur du worktree actif ;
- pour un perdant divergent unique non suivi, blocage sans disposition
  `discard_approved` ;
- pour un candidat TNSI 6/12, absence de gagnant dans `build/` ;
- detection des collisions de contenu ;
- rejet des fichiers temporaires et caches ;
- attribution unique des PDF ;
- conservation des empreintes avant/apres ;
- detection d'une mutation apres gel du preflight ;
- reconciliation des fichiers caches, liens, repertoires vides et fichiers
  speciaux ;
- idempotence ;
- refus de supprimer un ancien chemin non totalement comptabilise.

### 10.2 Tests d'integration

- inventaire et index generes depuis le seul chemin canonique ;
- aucune reference active a `Mathematiques/manuel-maths` ou `NSI` hors rapport
  de provenance et historique documentaire ;
- assemblage des variantes deja supportees ;
- comparaison eleve/professeur lorsqu'elle existe ;
- validation des manifests et des schemas ;
- deux generations consecutives deterministes.

### 10.3 Gates de fin de migration

La migration est terminee uniquement si :

1. chaque entree scannee est deplacee ou exclue avec justification ;
2. aucun conflit non resolu ne subsiste ;
3. les anciens repertoires de production ont disparu du tree courant ;
4. les chemins canoniques sont les seuls lus par les outils ;
5. les PDF retenus possedent une attribution et une empreinte ;
6. `--validate-model` est vert ;
7. `--fail-on-new` ne signale aucune regression introduite par la migration ;
8. `--release-strict` reste rouge pour les bloqueurs reels existants ;
9. TNSI reste sans build final tant que le perimetre 12/12 manque ;
10. le WIP 1NSI preexistant est preserve ou integre par commits atomiques
    distincts ;
11. `main` et le worktree de migration pointent sur le meme SHA apres
    autorisation humaine, puis le worktree redondant est retire.

## 11. Strategie de commits

La migration est decoupee en checkpoints independamment verifiables :

1. `[DOCS]` specification et plan ;
2. commits 1NSI existants, valides selon leur propre plan ;
3. `[TESTS]` contrats de migration en echec ;
4. `[AUDIT]` outil non destructif de preflight et rapport initial ;
5. `[AUDIT]` manifests canoniques et option de racine, sans changement des
   chemins actifs ;
6. `[AUDIT]` staging complet, builds Mathématiques/NSI et verrou TNSI ;
7. `[AUDIT]` cutover transactionnel des sources et valeurs par defaut des
   consommateurs ;
8. `[CI]` checks post-cutover et interdiction des chemins legacy ;
9. `[AUDIT]` abandon verifie des exclusions et du staging ;
10. checkpoint humain puis `[AUDIT]` attestation de l'unicite physique.

Chaque checkpoint laisse un etat testable et n'autorise le suivant que si son
inventaire est coherent. Aucun commit n'utilise un prefixe non prevu par
`AGENTS.md`.

Les modifications 1NSI deja presentes dans le worktree ne sont jamais melees
au commit documentaire ou aux commits de migration sans revue explicite.

## 12. Criteres d'acceptation utilisateur

- Une seule arborescence courante contient les sources, builds et preuves des
  manuels.
- Aucun ancien dossier de production redondant ne reste actif.
- Les versions perdantes ne sont ni exposees comme livrables, ni silencieusement
  ecrasees.
- Les builds les plus aboutis observes sont faciles a trouver dans `INDEX.md`.
- Les sources permettant de les reconstruire sont identifiables et testees.
- 1NSI conserve ses declinaisons existantes apres validation.
- TNSI reste explicitement bloque jusqu'a la presence reelle de 12 chapitres.
- Le statut NO-GO de 1SPE et les autres gates rouges restent visibles.
