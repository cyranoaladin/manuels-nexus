# Wave 0 — Contrats Red des P0 observés

## Statut et décision

- Date : 13 août 2026.
- Branche d'implémentation : `wave0/p0-red-contracts`.
- Point de départ : `ff55af2e07a35c559802a536f92a7bb12a73b3e3`.
- Décision humaine : livrer un **jalon Red seul**, auditable, avant toute
  modification de production.
- Verdict collection : **NO-GO publication**.

Le jalon ajoute uniquement des tests qui décrivent le comportement attendu et
qui échouent sur l'état courant pour les raisons P0 reproduites. Il ne corrige
ni scripts, ni contenus, ni PDF, ni registre, ni charte, ni baseline.

## Autorité et preuves

L'ordre d'autorité reste celui d'`AGENTS.md` : textes officiels, cahier des
charges, instructions applicables, schémas et gates, décisions humaines,
rapports générés, historiques.

Les faits de départ sont consignés dans
`audit/AUDIT_ETAT_PROJET_2026-08-13.md` :

- fuites de matériel professeur dans les PDF élèves 1SPE et TSPE ;
- renvois provisoires et identifiants internes visibles ;
- grands `Overfull` acceptés par le préflight Mathématiques ;
- NOR TSPE `MENE1921262A` erroné dans les sources locales.

La référence officielle correcte du programme de spécialité mathématiques de
Terminale est `MENE1921246A`. `MENE1921262A` désigne la Terminale STMG.

## Objectif

Fournir trois contrats exécutables, indépendants et volontairement rouges :

1. séparation élève/professeur, renvois et identifiants ;
2. débordements LaTeX refusés par le préflight Mathématiques ;
3. provenance officielle TSPE cohérente.

Chaque contrat doit prouver deux choses lorsqu'un artefact suivi existe :

- le contrôleur reconnaît le défaut sur une fixture minimale ;
- l'artefact ou le registre réel ne contient plus ce défaut.

Ainsi, un futur lot Green ne pourra pas se contenter d'améliorer la détection
sans corriger le produit, ni corriger un PDF isolé sans renforcer le gate.

## Périmètre des modifications

### Fichiers de conception et de plan

- `docs/superpowers/specs/2026-08-13-wave-0-contrats-red-p0-design.md` ;
- `docs/superpowers/plans/2026-08-13-wave-0-contrats-red-p0.md`.

### Tests modifiés ou créés

- `Mathematiques/manuel-maths/tests/test_assemble_manuel_observed.py` ;
- `Mathematiques/manuel-maths/tests/test_pdf_integrity.py` ;
- `tests/test_build_manifest.py` ;
- `tests/test_programme_registry.py`.

Le plan peut retenir un fichier de test dédié supplémentaire si cela rend la
séparation gate/artefact plus claire, à condition qu'il reste limité aux P0
approuvés et n'ajoute aucun helper de production.

### Hors périmètre absolu

- `Mathematiques/manuel-maths/scripts/assemble_manuel.py` ;
- `Mathematiques/manuel-maths/scripts/pdf_integrity.py` ;
- `scripts/build_manifest.py` ;
- `docs/programmes/PROGRAMMES_2026_2027.yaml` ;
- `Mathematiques/manuel-maths/sources/SOURCES.md` ;
- tout `.tex`, PDF, log, reçu ou préflight ;
- toute baseline, disposition ou référence visuelle ;
- toute CI transformant les tests rouges en succès attendu ;
- toute correction Green.

## Contrat 1 — Séparation de la variante élève

### Surface de contrôle

Les deux fonctions existantes doivent être contractuellement alignées :

- `assemble_manuel.student_text_violations()` côté Mathématiques ;
- `build_manifest._student_text_violations()` côté recorder global.

Les fixtures minimales suivantes doivent être reconnues :

| Texte | Motif stable attendu |
|---|---|
| `Correction et diagnostics` | `corrigé` |
| `Réponses correctes` | `corrigé` |
| `Bareme : 6 points` | `barème enseignant` |
| `clé de correction` | `corrigé` |
| `TSPE-DERIVATION-CONVEXITE` | `identifiant interne` |
| `(renvois exercices M1)` | `renvoi provisoire` |

Les accents et la casse ne doivent pas permettre de contourner le gate. Le
test ne doit cependant pas transformer les verbes d'instruction comme
« Corrige le programme » en faux positif. Les six contre-exemples existants du
recorder restent verts ; le cas Mathématiques, auparavant moins complet, est
étendu et devient contractuellement rouge.

L'alignement des contre-exemples a révélé que le filtre Mathématiques courant
signale à tort `corrigé` pour quatre consignes, tandis que le recorder les
accepte. Le jalon Red contractualise aussi cette divergence dans un seul cas
Pytest qui évalue toutes les phrases avant l'assertion. Il est interdit de
corriger le regex dans cette tranche.

### Surface réelle

Le test d'artefact extrait le texte du PDF élève 1SPE suivi avec `pdftotext
-layout`. Il exige l'absence de :

- `Correction et diagnostics` ;
- `Réponses correctes` ;
- `(renvois exercices M`.

Le test échoue actuellement, car l'audit a observé sept pages de correction et
50 renvois provisoires. Si `pdftotext` ou le PDF manque, le test doit échouer
explicitement plutôt que s'ignorer.

Le PDF élève TSPE suivi est lui aussi extrait avec `pdftotext -layout`. Le test
d'artefact y exige, avec tolérance à la casse et aux accents, l'absence de :

- `Cle de correction — reservee au professeur` ;
- `Bareme` ou `Barème` ;
- tout identifiant conforme à `TSPE-[A-Z0-9-]+`.

L'état reproduit contient une clé de correction, deux occurrences de
`TSPE-DERIVATION-CONVEXITE` et deux barèmes. Les fixtures unitaires verrouillent
le contrôleur ; l'extraction TSPE empêche de le rendre vert sans corriger le
produit.

## Contrat 2 — Débordements du préflight Mathématiques

### Surface de contrôle

Une fixture minimale de journal contenant l'un des diagnostics suivants doit
faire retourner `1` à `pdf_integrity.verify_pdf()` :

- `Overfull \hbox` ;
- `Overfull \vbox`.

Le runner de `pdffonts` est simulé uniquement pour isoler le diagnostic du
journal ; il doit représenter une police incorporée valide. Le test porte sur
le vrai `verify_pdf()`, pas sur un mock du résultat attendu.

Deux cas paramétrés sont préférés afin qu'un futur correctif ne couvre pas une
seule orientation de débordement.

### Surface réelle

Le journal `MANUEL_1SPE_eleve.log` observé lors de l'audit est ignoré par Git et
n'existe donc pas dans un worktree neuf. Le test ne doit jamais dépendre de ce
fichier local.

Le test d'intégration génère le master élève 1SPE depuis les sources suivies,
le compile dans un dossier temporaire avec trois passes LuaLaTeX et analyse le
journal temporaire obtenu. La compilation s'exécute avec la racine
Mathématiques comme répertoire courant afin que les `\input` canoniques soient
résolus, tandis que tous les artefacts produits restent sous `tmp_path`.

Le journal temporaire doit ne contenir aucun `Overfull \hbox` ni `Overfull
\vbox` non approuvé. L'échec donne les comptes observés. La reproduction
initiale hors worktree a donné 17 `hbox` et 2 `vbox` ; ces nombres sont une
preuve d'état, pas une constante que le futur Green devra conserver.

Si LuaLaTeX manque ou si la compilation n'aboutit pas, le test échoue
explicitement. Il ne porte aucun `skipif`, conformément au caractère
contractuel du jalon.

Ce contrat ne prétend pas détecter toutes les collisions visuelles. Il ferme
le défaut précis où le préflight Mathématiques accepte des débordements que le
préflight livre NSI refuse déjà.

## Contrat 3 — Provenance officielle TSPE

Un test racine dédié charge
`docs/programmes/PROGRAMMES_2026_2027.yaml` avec `yaml.safe_load` et vérifie :

- la source `SRC-BO2019-TSPE` existe ;
- son champ `arrete` vaut exactement `MENE1921246A` ;
- le manuel `TSPE_2026_2027` référence cette source ;
- `MENE1921262A` n'est pas attribué à TSPE.

Le même test, ou un second test très proche, vérifie que la ligne
`BO2019_TSPE_specialite.pdf` de
`Mathematiques/manuel-maths/sources/SOURCES.md` porte `MENE1921246A` et non
`MENE1921262A`.

Le test reste hors réseau : il verrouille la décision réglementaire déjà
vérifiée et archivée par l'audit. Le futur lot Green devra modifier le registre
et la table de sources dans un commit `[PROGRAMME]` distinct.

## Sémantique du jalon Red

### Rouge attendu

Les nouvelles assertions doivent échouer parce que :

- les filtres ne reconnaissent pas encore les nouvelles formulations ;
- le PDF élève 1SPE contient encore les chaînes interdites ;
- le préflight Mathématiques accepte encore les diagnostics `Overfull` ;
- le log suivi contient encore les débordements ;
- le registre et `SOURCES.md` portent encore le NOR erroné.

La matrice attendue comprend désormais 20 cas rouges : 15 pour la séparation
élève, 3 pour les débordements et 2 pour la provenance. Le quinzième cas élève
est le contrat de non-faux-positif du filtre Mathématiques découvert pendant
l'implémentation.

Un test qui échoue par import, chemin absent, faute de syntaxe, outil invoqué
incorrectement ou fixture mal construite n'est pas un Red valide.

### Vert historique

Avant et après ajout, les tests ciblés historiques qui ne sont pas les nouveaux
contrats doivent rester verts. L'échec préexistant suivant est consigné et ne
doit pas être attribué à ce jalon :

`tests/test_build_manifest.py::test_versioned_build_producers_register_exact_1nsi_manual_surface`

Ce test attend encore deux producteurs alors que le registre versionné en
déclare six. Il est hors périmètre et ne sera ni corrigé ni masqué.

### Interdictions

Les tests du jalon ne portent aucun décorateur `skip`, `skipif`, `xfail` ou
marqueur qui les transforme en succès. Ils ne sont pas soustraits à la collecte
CI. Aucun wrapper ne convertit leur code non nul en zéro.

Le commit est délibérément non vert. Son message et le compte rendu doivent
donner les nœuds Pytest rouges, leurs messages et la dette historique séparée.

## Commits atomiques

Les trois familles métier restent séparées :

1. `[TESTS] caractérise les fuites de la variante élève` ;
2. `[TESTS] caractérise les débordements du préflight mathématiques` ;
3. `[TESTS] verrouille la provenance officielle TSPE`.

La spécification et le plan sont versionnés dans des commits `[DOCS]`
distincts avant les tests.

## Revue et acceptation du jalon

Chaque famille de tests reçoit :

1. une implémentation test-first sans code de production ;
2. une exécution ciblée prouvant un échec pour la bonne raison ;
3. une revue de conformité à cette spécification ;
4. une revue de qualité des tests ;
5. un commit atomique après contrôles Git.

La vérification finale doit produire :

- la liste exacte des nouveaux tests collectés ;
- le nombre de nouveaux tests rouges par famille ;
- les messages montrant les P0 réels ;
- les tests historiques ciblés verts, hors dette préexistante consignée ;
- `git diff --check` vert et un arbre propre ;
- le gate structurel vert dans le checkout d'intégration attesté par le
  manifeste ;
- dans le worktree isolé, le code 3 attendu et uniquement la raison
  `check_error:branche de provenance du manifeste incohérente` ;
- le gate de release toujours rouge code 7 dans le checkout d'intégration,
  sans changement de baseline.

Le manifeste versionné atteste la branche
`integration/1spe-bo2026-traceability`. Il est interdit de le réécrire pour
faire accepter artificiellement la branche de tests. Les codes du worktree et
du checkout attesté sont donc relevés séparément.

## Définition de terminé

Le jalon Red est terminé lorsque les trois familles sont committées, les
nouveaux tests sont collectés et échouent exclusivement sur les comportements
P0 décrits, aucune surface de production n'a changé et les dettes historiques
sont distinguées. Le worktree reste propre ; sa divergence de branche avec la
provenance du manifeste est rapportée comme telle, sans mutation du manifeste.
Il est volontairement interdit de déclarer la collection ou les tests complets
« verts » à ce stade.
