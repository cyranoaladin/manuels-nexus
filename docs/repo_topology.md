# Topologie canonique du dépôt NSI

## Doctrine

Le dépôt canonique de production et de validation est `nsi-enseignement/`.
Il est un clone Git autonome situé dans le dossier parent local
`<workspace_parent>/`.

En CI GitHub Actions, le même dépôt peut être extrait dans un répertoire nommé
`NSI`. Dans ce cas, l'identité canonique est vérifiée par le remote Git
`cyranoaladin/NSI` et non par le nom absolu du dossier local.

Le dépôt parent local peut contenir des outils ou miroirs de travail, mais
`nsi-enseignement/` ne doit pas être suivi comme simple sous-dossier du dépôt
parent. La relation correcte est donc :

```text
<workspace_parent>/                       = espace local de travail
<workspace_parent>/.git                   = dépôt parent éventuel
<workspace_parent>/nsi-enseignement/.git  = dépôt canonique autonome
```

## Dossiers sources versionnés

Les sources versionnées du corpus et des gardes sont celles suivies par Git
dans le dépôt canonique `nsi-enseignement/`.

Les archives livrables `source_clean` sont construites depuis `git ls-files`.
Un fichier non suivi par Git ne doit pas entrer dans l'archive de livraison.

## Miroirs locaux

Les chemins suivants sont des miroirs ou bases locales et ne sont pas des
sources versionnées du corpus canonique :

```text
scrapping_NSI/ressources_nsi_centralisees
scrapping_NSI/ressources_nsi_extraites
scrapping_NSI/ressources_nsi_extraites_v2
scrapping_NSI/sqlite_data
Documents_DRIVE/
drive_quarantine/
```

Ces dossiers peuvent exister dans l'espace parent ou local, mais ils ne doivent
pas être suivis par Git dans le dépôt parent ni dans `nsi-enseignement/`.

## Interdits dans les archives livrables

Les archives livrables doivent exclure :

```text
.git/
nsi-enseignement/.git
dist/
build/
01_build_reports/
__pycache__/
.pytest_cache/
.ruff_cache/
.mypy_cache/
.venv/
scrapping_NSI/ressources_nsi_centralisees
scrapping_NSI/ressources_nsi_extraites
scrapping_NSI/ressources_nsi_extraites_v2
scrapping_NSI/sqlite_data
Documents_DRIVE/
```

## Interdits dans les index RAG

Les index RAG ne doivent pas pointer vers :

```text
/AUDIT
dist/
.git/
Documents_DRIVE/
drive_quarantine/
reports/lot1/
reports/lot2/
reports/lot3/
scrapping_NSI/ressources_nsi_centralisees
scrapping_NSI/ressources_nsi_extraites
scrapping_NSI/ressources_nsi_extraites_v2
scrapping_NSI/sqlite_data
```

Les dossiers `premiere/sequences/` et `terminale/sequences/` restent des
golden examples. Ils ne sont pas le canon de production et ne prouvent pas une
couverture pédagogique interne.
