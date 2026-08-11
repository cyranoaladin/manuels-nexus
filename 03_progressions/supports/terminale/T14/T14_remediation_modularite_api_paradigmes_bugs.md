---
title: "T14 - remediation - modularité, API, paradigmes et bugs"
level: "terminale"
sequence_id: "T14"
document_type: "remediation"
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

# T14 - Remédiation - modularité, API, paradigmes et bugs

## Diagnostic
- import avec effet de bord.
- API sans docstring.
- bug corrigé sans test.

## Activités correctives
1. Annoter `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`.
2. Refaire la tâche `définir fonction publique documentée` et comparer avec `moyenne_temperature(releves) -> 30.0`.
3. Traiter le cas limite `liste vide`.
4. Relier la réponse à T-LANG-03A.

## Critères de sortie
- Donnée exacte.
- Résultat final explicite.
- Cas limite décidé.
