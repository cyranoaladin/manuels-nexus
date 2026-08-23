<a id="decision-1spe-trigo-optional-extensions-2026-08-23"></a>

# Décision humaine — extensions facultatives de trigonométrie 1SPE

- Date : 23 août 2026
- SHA d'intégration observé : `10cb5f07772842d6630d2a2f78531f6900371023`
- Autorité : opérateur humain du projet, instruction explicite
- Périmètre fermé : `1SPE-TRIGO-ME-003`, `1SPE-TRIGO-ME-004`,
  `1SPE-TRIGO-ME-005`, sans wildcard

## Décision

Les trois méthodes sont conservées comme approfondissements explicitement
facultatifs, respectivement sous `X1`, `X2` et `X3`. Leur état de gouvernance
courant est `OPTIONAL_EXTENSION_REVIEW_PENDING` et leur statut source reste
`needs_review`.

Elles sont exclues de la couverture obligatoire du programme de Première,
des sujets ou simulations d'épreuve anticipée, des QCM obligatoires et des
remédiations du socle.

Les anciens packets A4 restent byte-identiques et sont classés
`HISTORICAL_STALE_RECEIPT`. Ils ne sont ni des receipts courants, ni des
preuves de revue du source courant, ni des autorisations de rebind ou de
mutation de baseline.

De nouveaux packets courants sont liés au SHA exact de chaque source. Les
revues scientifique, pédagogique, éditoriale et de variante restent toutes
`PENDING`. Toute modification du source invalide immédiatement le packet
courant.

## Limites

Cette décision autorise uniquement le modèle de gouvernance ci-dessus. Elle
ne constitue aucune approbation scientifique, pédagogique, éditoriale,
visuelle, de variante, de publication ou de release. Les trois objets restent
bloquants pour `release-strict` tant que les revues requises ne sont pas
fermées par les autorités compétentes.
