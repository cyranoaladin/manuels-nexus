---
title: "T15 - version_amenagee - calculabilité, programme comme donnée et arrêt"
level: "terminale"
sequence_id: "T15"
document_type: "version_amenagee"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "calculabilité, programme comme donnée et arrêt"
notion: "calculabilité, programme comme donnée et arrêt"
private_data: false
official_program:
  capacities:
    - "T-LANG-01A"
    - "T-LANG-01B"
    - "T-LANG-01C"
---

# T15 - Version aménagée - calculabilité, programme comme donnée et arrêt

## Aides intégrées
- Donnée fournie : `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`.
- Mots utiles : programme comme donnée, interpréteur, calculabilité, langage indépendant, problème de l arrêt.
- Méthode guidée : encoder un programme comme texte puis raisonner indépendamment de Python.

## Exercice guidé
1. Recopier la donnée utile.
2. Choisir la capacité : T-LANG-01A ou T-LANG-01B.
3. Compléter le résultat : source="print(1)" est une donnée.
4. Cocher le cas limite : programme très long mais fini.

## Réponses rapides
- Réponse 1 : source="print(1)" est une donnée.
- Réponse 2 : arrete(P,x) renvoie True ou False.
- Réponse 3 : Q boucle si arrete(Q,Q) dit True.
