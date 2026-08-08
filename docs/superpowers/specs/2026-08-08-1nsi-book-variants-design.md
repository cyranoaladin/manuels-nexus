# Design — Variantes de Livre 1NSI

Date : 2026-08-08

## Objectif

Étendre le mode `--book` de `NSI/scripts/assemble.py` pour assembler des déclinaisons
de livre `1NSI` à partir du même manifeste, sans introduire de faux manuel `TNSI`
partiel tant que les 12 chapitres attendus ne sont pas présents.

## Contexte observé

- `1NSI` possède 10 chapitres dans `NSI/chapitres/`.
- La déclinaison `remediation` existe dans les 10 chapitres.
- Les déclinaisons `methodes` et `amenagee` n'existent actuellement que dans
  `1NSI-TYPES-CONSTRUITS`.
- Le mode livre actuel assemble uniquement `complet`.
- Le choix CLI chapitre expose `professeur` et `parcours1`; ces variantes restent
  réservées au mode chapitre et sont refusées par le mode livre.
- `TNSI` ne compte que 6 chapitres à la date du 8 août 2026 ; il reste hors périmètre
  de cette passe.

## Décision

Le mode livre devient sensible au `--variant` :

- `complet` : assemble les 10 chapitres du manifeste avec leur contenu élève
  (`cours`, `methodes`, `exercices`, `coups_de_pouce`, TD, `projet`, `qcm`, `ece`).
  Il exclut les évaluations barémées, les packs de remédiation corrigés, les corrigés
  et tout chemin professeur.
- `remediation` : assemble tous les chapitres ayant un dossier `remediation/` non vide.
- `methodes` : assemble uniquement les chapitres ayant un dossier `methodes/` non vide.
- `amenagee` : assemble uniquement les chapitres ayant un dossier `amenagee/` non vide.

Le comportement est volontairement tolérant par chapitre, mais strict au niveau du livre :

- seules les variantes `complet`, `remediation`, `methodes` et `amenagee` sont admises ;
- un chapitre sans contenu pour la variante demandée est ignoré ;
- un résumé des chapitres inclus/exclus est affiché ;
- si aucun chapitre n'est éligible, l'assemblage échoue ;
- aucun manifeste `TNSI` n'est ajouté dans cette passe.

Les quatre sorties utilisent explicitement le mode élève du gabarit. Les corps des
environnements `corrige` sont neutralisés dans ce rendu, sans supprimer ni modifier les
sources professeur. Les identifiants internes restent masqués.

Les 15 corrections de délimiteurs `lstinline` introduites pour les littéraux de dictionnaire
sont conservées : elles garantissent que le corpus professeur futur reste compilable même
si ces objets ne sont pas exposés dans le livre élève complet.

## Hors périmètre

- pas d'assemblage `TNSI` ;
- pas de livret `professeur` tant que les objets dédiés ne sont pas structurés
  proprement dans le dépôt ;
- pas de changement de contenu pédagogique des chapitres.

## Impact code

- conserver la résolution historique du mode chapitre ;
- définir une résolution livre élève distincte et un filtre défensif des chemins professeur ;
- rendre explicite le comportement des variantes non encore supportées ;
- ajouter des tests unitaires ciblant l'inclusion/exclusion de chapitres par variante.

## Vérification prévue

- tests unitaires assembleur sur la sélection des chapitres ;
- build réel `1NSI` en `complet`, `remediation`, `methodes`, `amenagee` ;
- `verify_pdf` sur chaque PDF généré ;
- scan `pdftotext` sans `Corrigé`, `Barème indicatif` ni identifiant `1NSI-*` ;
- logs sans `Overfull`, `Underfull` ni erreur LaTeX fatale ;
- `git diff --check`.
