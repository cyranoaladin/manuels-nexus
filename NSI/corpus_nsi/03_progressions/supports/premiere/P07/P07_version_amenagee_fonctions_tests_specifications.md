---
title: "P07 - version_amenagee - fonctions, tests et spécifications"
level: "premiere"
sequence_id: "P07"
document_type: "version_amenagee"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "fonctions, tests et spécifications"
notion: "fonctions, tests et spécifications"
private_data: false
official_program:
  capacities:
    - "P-LANG-01"
    - "P-LANG-02"
    - "P-LANG-03A"
    - "P-LANG-03B"
    - "P-LANG-03C"
    - "P-LANG-04"
    - "P-LANG-05"
---

# P07 - Version aménagée - fonctions, tests et spécifications

## Aides intégrées
- Donnée fournie : `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`.
- Mots utiles : signature, précondition, postcondition, assertion, test unitaire.
- Méthode guidée : écrire def prix_ttc(prix_ht: float, taux: float) -> float puis poser prix_ht >= 0 et taux >= 0.

## Exercice guidé
1. Recopier la donnée utile.
2. Choisir la capacité : P-LANG-01 ou P-LANG-02.
3. Compléter le résultat : signature complète de prix_ttc.
4. Cocher le cas limite : prix_ht=0.

## Réponses rapides
- Réponse 1 : signature complète de prix_ttc.
- Réponse 2 : prix_ttc(80,0.20) -> 96.0.
- Réponse 3 : prix_ttc(-5,0.20) -> ValueError.
