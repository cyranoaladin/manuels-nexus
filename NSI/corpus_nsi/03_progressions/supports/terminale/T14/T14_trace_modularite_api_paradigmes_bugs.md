---
title: "T14 - trace - modularité, API, paradigmes et bugs"
level: "terminale"
sequence_id: "T14"
document_type: "trace"
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

# T14 - Trace - modularité, API, paradigmes et bugs

## Trace courte
- Donnée : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`.
- Vocabulaire : API, documentation, module, paradigme impératif, paradigme fonctionnel.
- Étape 1 : définir fonction publique documentée.
- Étape 2 : séparer module et script principal.
- Résultat de référence : moyenne_temperature(releves) -> 30.0.

## Cas limites à mémoriser
- liste vide.
- clé temperature absente.
- type chaîne.

## Erreurs fréquentes
- import avec effet de bord.
- API sans docstring.
- bug corrigé sans test.

## Critères de réussite observables
- Capacité : T-LANG-03A.
- Résultat final : from meteo import moyenne_temperature.
- Cas limite : liste vide.
