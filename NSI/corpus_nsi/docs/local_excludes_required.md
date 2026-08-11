# Exclusions locales requises

Le dépôt canonique `nsi-enseignement/` versionne la doctrine de topologie dans
`docs/repo_topology.md`. Les exclusions locales du dépôt parent ne sont pas une
source de vérité suffisante.

Si le dépôt parent `<workspace_parent>/` existe, les chemins suivants
doivent être ignorés par une `.gitignore` versionnée du parent ou, à défaut,
être explicitement couverts par cette politique versionnée :

```text
nsi-enseignement/
scrapping_NSI/ressources_nsi_centralisees
scrapping_NSI/ressources_nsi_extraites
scrapping_NSI/ressources_nsi_extraites_v2
scrapping_NSI/sqlite_data
```

Le fichier local `.git/info/exclude` peut rester une défense complémentaire,
mais il ne remplace pas cette politique versionnée.
