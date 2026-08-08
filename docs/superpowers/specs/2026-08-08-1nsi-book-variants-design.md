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
- Le choix CLI expose déjà `professeur` et `parcours1`, mais la logique actuelle de
  collecte ne les traite pas explicitement.
- `TNSI` ne compte que 6 chapitres à la date du 8 août 2026 ; il reste hors périmètre
  de cette passe.

## Décision

Le mode livre devient sensible au `--variant` :

- `complet` : assemble tous les chapitres du manifeste ayant du contenu complet.
- `remediation` : assemble tous les chapitres ayant un dossier `remediation/` non vide.
- `methodes` : assemble uniquement les chapitres ayant un dossier `methodes/` non vide.
- `amenagee` : assemble uniquement les chapitres ayant un dossier `amenagee/` non vide.

Le comportement est volontairement tolérant par chapitre, mais strict au niveau du livre :

- un chapitre sans contenu pour la variante demandée est ignoré ;
- un résumé des chapitres inclus/exclus est affiché ;
- si aucun chapitre n'est éligible, l'assemblage échoue ;
- aucun manifeste `TNSI` n'est ajouté dans cette passe.

## Hors périmètre

- pas d'assemblage `TNSI` ;
- pas de livret `professeur` tant que les objets dédiés ne sont pas structurés
  proprement dans le dépôt ;
- pas de changement de contenu pédagogique des chapitres.

## Impact code

- centraliser la résolution des fichiers d'un chapitre par variante ;
- réutiliser cette résolution aussi bien pour `--chap` que pour `--book` ;
- rendre explicite le comportement des variantes non encore supportées ;
- ajouter des tests unitaires ciblant l'inclusion/exclusion de chapitres par variante.

## Vérification prévue

- tests unitaires assembleur sur la sélection des chapitres ;
- build réel `1NSI` en `complet`, `remediation`, `methodes`, `amenagee` ;
- `verify_pdf` sur chaque PDF généré ;
- `git diff --check`.
