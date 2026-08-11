---
title: "T14 - version_amenagee - modularité, API, paradigmes et bugs"
level: "terminale"
sequence_id: "T14"
document_type: "version_amenagee"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "modularité, API, paradigmes et bugs"
notion: "modularité, API, paradigmes et bugs"
private_data: false
official_program:
  capacities:
    - "T-LANG-03A"
    - "T-LANG-03B"
    - "T-LANG-03C"
    - "T-LANG-04A"
    - "T-LANG-04B"
    - "T-LANG-05"
---

# T14 - Version aménagée - modularité, API, paradigmes et bugs

## Aides intégrées
- Donnée fournie : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`.
- Mots utiles : API, documentation, module, paradigme impératif, paradigme fonctionnel.
- Méthode guidée : définir fonction publique documentée puis séparer module et script principal.

## Exercice guidé
1. Recopier la donnée utile.
2. Choisir la capacité : T-LANG-03A ou T-LANG-03B.
3. Compléter le résultat : moyenne_temperature(releves) -> 30.0.
4. Cocher le cas limite : liste vide.

## Réponses rapides
- Réponse 1 : moyenne_temperature(releves) -> 30.0.
- Réponse 2 : from meteo import moyenne_temperature.
- Réponse 3 : temperature="31" refusée ou convertie.
