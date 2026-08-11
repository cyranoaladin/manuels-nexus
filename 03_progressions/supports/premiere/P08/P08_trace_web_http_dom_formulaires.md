---
title: "P08 - trace - HTML, CSS, DOM, HTTP et formulaires"
level: "premiere"
sequence_id: "P08"
document_type: "trace"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "HTML, CSS, DOM, HTTP et formulaires"
notion: "HTML, CSS, DOM, HTTP et formulaires"
private_data: false
official_program:
  capacities:
    - "P-IHM-01A"
    - "P-IHM-01B"
    - "P-IHM-02"
    - "P-IHM-03A"
    - "P-IHM-03B"
    - "P-IHM-03C"
    - "P-IHM-04A"
    - "P-IHM-04B"
    - "P-IHM-04C"
---

# P08 - Trace - HTML, CSS, DOM, HTTP et formulaires

## Trace courte
- Donnée : `<form method=post action=/reservation><input id=nom name=nom></form>, URL /club?jour=mercredi`.
- Vocabulaire : HTML structurel, sélecteur CSS, DOM, événement submit, GET.
- Étape 1 : repérer header main form label input.
- Étape 2 : cibler #nom en CSS et DOM.
- Résultat de référence : à déterminer (quelle balise HTML associe un libellé à un champ ?).

## Cas limites à mémoriser
- champ nom vide.
- paramètre jour absent.
- formulaire sans action.

## Erreurs fréquentes
- bouton hors formulaire.
- sélecteur trop large.
- POST confondu avec chiffrement.

## Critères de réussite observables
- Capacité : P-IHM-01A.
- Résultat final : vérifier que la saisie du champ est accessible via le DOM.
- Cas limite : champ nom vide.

## Repères enseignant — résultats attendus
- Résultat de référence : <label for=nom>Nom</label><input id=nom name=nom>.
- Résultat final : document.querySelector("#nom").value lit la saisie.
