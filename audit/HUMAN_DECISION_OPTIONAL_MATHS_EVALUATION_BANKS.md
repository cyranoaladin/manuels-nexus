# Décision humaine — banques d'évaluations mathématiques optionnelles

**Identité du décideur.** `abenrhouma` (Release Owner)

**Objets couverts, nominativement.**

- `1SPE::banque_evaluations`
- `TSPE_2026_2027::banque_evaluations`

## Décision

Ces deux livrables restent :

- `PROPOSED_NOT_APPROVED`
- `OPTIONAL = true`
- **`NOT_REQUIRED_FOR_2026_2027_RELEASE`**

Ils ne constituent pas des produits obligatoires de la release courante et ne
doivent donc plus produire de blocage `PRODUCT_P1`.

## Ce que la décision n'autorise pas

- Ne pas les supprimer : leur historique et leur proposition éditoriale sont
  conservés.
- Ne pas les construire artificiellement pour faire tomber un compteur.
- Ne pas étendre l'exemption aux évaluations déjà présentes dans les manuels,
  ni à aucun autre produit requis.

## Constat qui a motivé la décision

La matrice de périmètre classait déjà ces deux livrables
`PROPOSED_NOT_APPROVED`, `optional: true`, `a_valider_humain: true`, avec pour
seule origine `f5001666 (2026-07-20) — aucune clause de mission
correspondante`. Le gate les comptait pourtant comme blocages de publication.
La décision lève cette contradiction dans le sens que la matrice indiquait.

## Forme de l'exemption

La clé est le **couple** `(manuel, variante)`, jamais le seul nom de variante.
`banque_evaluations` reste requis partout ailleurs. L'exemption ne se déduit
d'aucun motif, d'aucun suffixe, d'aucune heuristique : elle est énumérée.

## Réversibilité

Retirer un couple de la liste rétablit immédiatement le blocage. Un test le
vérifie en vidant la liste et en exigeant que la variante redevienne requise :
un passage futur à `required` bloque tant que le livrable n'est pas prêt.

## Invariant exigé

`OPTIONAL_DELIVERABLE_COUNTED_AS_REQUIRED = 0`
