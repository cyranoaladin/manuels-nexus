# État réel des variantes aménagées

- `TNSI_AMENAGEE_SOURCE_OBJECTS` : `7`
- `TNSI_AMENAGEE_ACTUAL_CONTENT_COVERAGE` : `7/7`
- Classification : `COMPLETE`
- `READINESS_METRIC_AGREES_WITH_OBJECTS` : `True`

## Défaut historique

La maturite lisait `included_files`, qui compte les `contrat.yaml` des ouvertures de chapitre : une variante sans le moindre objet en declarait sept.

Corrigé par `scripts/build_release_deliverable_readiness.py`. Encore présent : `False` — recalculé contre le producteur de maturité, pas recopié.

| Manuel | Objets | Chapitres couverts | Classification |
|---|---|---|---|
| `1NSI` | 10 | 10/10 | `COMPLETE` |
| `TNSI` | 7 | 7/7 | `COMPLETE` |
