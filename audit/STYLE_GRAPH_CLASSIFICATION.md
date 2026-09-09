# Classification read-only du graphe de styles

Généré par `scripts/classify_style_graph.py`. **Rien n'est supprimé, rien n'est
modifié.** Données complètes, preuve par preuve (chemin + ligne + extrait) :
`audit/STYLE_GRAPH_CLASSIFICATION.json`.

## Périmètre réel

**33 fichiers `.sty` / `.cls` suivis par git**, pas 63.

Le chiffre de 63 annoncé précédemment n'est pas reproductible : le dépôt en
contient 33 sous suivi git, et 363 si l'on compte les copies présentes dans les
10 worktrees de `.worktrees/`. Aucune énumération ne donne 63. Comme pour
l'ensemble gelé de `1SPE-SUITES`, la valeur déclarée est enregistrée comme
divergente plutôt que reconstruite.

Même remarque pour les « 21 duplicatas » : la machine trouve **10 groupes de
duplicatas de contenu**, soit 20 fichiers dupliqués deux à deux.

## Définition de l'arête de chargement

Une **arête de chargement** est un `\usepackage` / `\RequirePackage` /
`\documentclass` écrit **dans une source LaTeX suivie par git** et résolu vers ce
fichier. La résolution respecte la règle TeX du répertoire courant : une classe
du sous-arbre NSI qui charge `nexus-charte-v6` charge la copie NSI.

Une occurrence du même nom dans un script Python, un test ou un rapport est une
**mention**, pas un chargement. Un test verrouille cette distinction : sans elle,
`scripts/unify_legacy_gabarits_wrappers.py` faisait apparaître
`gabarits/common/nexus-charte.sty` comme chargé alors que la chaîne
`\RequirePackage{...}` n'était qu'un littéral Python.

## Répartition

| Classe | Nombre |
|---|---:|
| `ACTIVE_CANONICAL` | 2 |
| `ACTIVE_NONCANONICAL` | 26 |
| `HISTORICAL_ONLY` | 5 |
| `FIXTURE_ONLY` | 0 |
| `OBSOLETE` | 0 |

Aucun fichier n'est `OBSOLETE` : les 33 portent au moins une mention suivie par
git. **Aucun n'est donc `safe-to-delete`.**

## Constat principal : 24 fichiers sur 33 sans aucune arête de chargement

`gabarits/common/nexus-manuel.cls` est monolithique : il charge directement ses
paquets TeX (`tcolorbox`, `geometry`, `scrlayer-scrpage`, …) et ne charge aucun
module Nexus. En conséquence, ces 24 fichiers ne sont chargés par **aucune**
source LaTeX du dépôt :

| Module | Copies sans arête de chargement |
|---|---|
| `nexus-boites` / `nexus-boites-v6` | `gabarits/common/`, `Mathematiques/manuel-maths/gabarits/`, `NSI/gabarits/` |
| `nexus-couverture` | les trois |
| `nexus-decor` | les trois |
| `nexus-exercices` / `nexus-exercices-v6` | les trois |
| `nexus-figures-bib` | les trois |
| `nexus-pages-froides` | les trois |
| `nexus-pont` / `nexus-pont-v6` | les trois |
| `nexus-charte` | `gabarits/common/` uniquement |
| `nexus-maths`, `nexus-nsi` | `gabarits/maths/`, `gabarits/nsi/` |

Ce constat est un **fait de graphe, pas un verdict de suppression**. Avant toute
suppression il reste à instruire : les mentions en rapports et scripts, les
consommateurs runtime hors dépôt, et l'intention de la consolidation
`gabarits/common/` engagée par `scripts/unify_legacy_gabarits_wrappers.py`.

## Les 9 fichiers réellement chargés

| Fichier | Arêtes | Chargé par |
|---|---:|---|
| `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls` | 3 | `chapitre_master.tex`, `objet_standalone.tex`, `specimen.tex` |
| `Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls` | 3 | `build/maquette-v5/maquette.tex`, `specimen-v6.tex`, `specimen-pont-v6.tex` |
| `Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty` | 3 | `specimen-v6.tex`, `specimen-pont-v6.tex` |
| `Mathematiques/.../reference-v4/manuel-kit/manuel.sty` | 1 | `reference-v4/manuel-kit/main.tex` |
| `NSI/gabarits/nexus-manuel.cls` | 3 | `chapitre_master.tex`, `objet_standalone.tex`, `specimen.tex` |
| `NSI/gabarits/nexus-manuel-v5.cls` | 1 | `book_master.tex` |
| `NSI/gabarits/nexus-charte-v6.sty` | 1 | `book_master.tex` |
| `NSI/corpus_nsi/02_modeles_documents/nsi-preamble.sty` | 18 | les modèles de `corpus_nsi/02_modeles_documents/` |
| `gabarits/common/nexus-manuel.cls` | 1 | `gabarits/common/chapitre_master.tex` |

## Les 10 groupes de duplicatas

Les 10 groupes opposent chacun une copie Mathématiques et une copie NSI de
contenu **strictement identique** :

`nexus-manuel.cls`, `nexus-manuel-v5.cls`, `nexus-charte-v6.sty`,
`nexus-boites-v6.sty`, `nexus-couverture.sty`, `nexus-decor.sty`,
`nexus-exercices-v6.sty`, `nexus-figures-bib.sty`, `nexus-pages-froides.sty`,
`nexus-pont-v6.sty`.

Pour les 10 groupes : `canonical_survivor = null`, `duplicate_kind =
PER_DISCIPLINE_COPY`, `safe_to_delete = false` partout.

**Aucun survivant n'est dérivable du contenu.** Les deux copies sont chargées —
ou destinées à l'être — par leur propre discipline via la résolution relative de
TeX. Supprimer l'une casserait la résolution de l'autre discipline. La
convergence doit se faire **vers `gabarits/common/`**, pas par suppression de
l'une des deux ; c'est une migration, pas une déduplication. Un test refuse tout
arbitrage arbitraire entre deux copies par discipline.

## Migration nécessaire

`migration_needed = true` sur les 20 fichiers des 10 groupes : chacun doit à
terme se résoudre vers `gabarits/common/`. Cette migration est bloquée tant que
les modules `gabarits/common/` n'ont eux-mêmes aucune arête de chargement — il
faut d'abord décider si `nexus-manuel.cls` redevient modulaire ou si les modules
sont retirés.
