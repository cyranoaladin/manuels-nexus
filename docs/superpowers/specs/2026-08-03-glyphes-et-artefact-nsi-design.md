# Glyphes LaTeX et artefact PDF NSI — Design

## Contexte

La CI du SHA `90b2436ea73d17dbd58af8f61b62e7cddddc948f` termine avec succès, mais ses
journaux révèlent deux défauts fail-open :

- des sources assemblées utilisent directement `◆`, `✓` ou `✗`, absents des
  fontes TeX Gyre actives ;
- le workflow NSI ne produit aucun PDF lors d'un changement limité à la
  charte, puis tolère l'absence d'artefact avec `if-no-files-found: warn`.

La baseline visuelle ne doit pas être modifiée. Le manuel reste NO-GO.

## Décision approuvée

Traiter les deux défauts en deux unités atomiques.

### 1. Intégrité des glyphes

- Remplacer les losanges Unicode par `\parcoursUn`, `\parcoursDeux` ou
  `\parcoursTrois`.
- Remplacer les coches Unicode par `\checkmark` et les croix Unicode par
  `\(\times\)`.
- Étendre le préflight partagé `pdf_integrity.py` afin qu'un journal contenant
  `Missing character:` refuse le PDF.
- Synchroniser exactement ce préflight entre Mathématiques et NSI.
- Ajouter une régression unitaire et vérifier les journaux des assemblages
  réellement concernés.

Ce choix réutilise les composants Nexus et les symboles mathématiques déjà
chargés. Il évite l'ajout d'une fonte, la suppression d'avertissements et toute
mise à jour de référence visuelle.

### 2. Artefact PDF NSI

- Ajouter une cible `make specimen` dans NSI, avec préflight du PDF produit.
- Exécuter ce spécimen sans condition dans la CI NSI.
- Ancrer la détection des chapitres modifiés à la racine Git avec
  `:(top)NSI/chapitres`, puis extraire le troisième segment du chemin.
- Rendre l'absence d'un PDF bloquante avec `if-no-files-found: error`.
- Ajouter un test de contrat du workflow et du Makefile.

Le spécimen garantit un artefact même lorsqu'aucun chapitre n'a changé. La
boucle corrigée continue parallèlement à compiler tout chapitre NSI modifié.

## Contrat de validation

- Les tests ajoutés échouent avant le correctif et passent après.
- Les spécimens Mathématiques et NSI compilent avec préflight vert.
- Le chapitre `1NSI-TYPES-CONSTRUITS` et les deux manuels Mathématiques sont
  réassemblés ; aucun journal ne contient `Missing character:`.
- Le chemin `NSI/build/**/*.pdf` contient au moins un PDF après un clone/build
  équivalent à la CI.
- `scripts/check_charte_sync.py` reste vert.
- Aucun fichier sous `validations/`, aucun PNG de référence et aucune baseline
  visuelle ne change.
- `--release-strict` reste rouge tant que les dettes de publication subsistent.

