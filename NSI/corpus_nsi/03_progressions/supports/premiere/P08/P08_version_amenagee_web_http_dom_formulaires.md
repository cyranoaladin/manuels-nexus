---
title: "P08 - version_amenagee - HTML, CSS, DOM, HTTP et formulaires"
level: "premiere"
sequence_id: "P08"
document_type: "version_amenagee"
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

# P08 - Version aménagée - HTML, CSS, DOM, HTTP et formulaires

## Aides intégrées
- Donnée fournie : `<form method=post action=/reservation><input id=nom name=nom></form>, URL /club?jour=mercredi`.
- Mots utiles : HTML structurel, sélecteur CSS, DOM, événement submit, GET.
- Méthode guidée : repérer header main form label input puis cibler #nom en CSS et DOM.

## Exercice guidé
1. Recopier la donnée utile.
2. Choisir la capacité : P-IHM-01A ou P-IHM-01B.
3. Compléter le résultat : `________________` (utiliser les balises HTML adaptées pour associer un libellé au champ).
4. Cocher le cas limite : champ nom vide.
5. Vérification : le sélecteur CSS `#nom` cible-t-il un élément unique ?
6. Expliquer en une phrase comment le navigateur transmet `jour` au serveur dans l'URL fournie.

## Repères enseignant — réponses de référence
- Réponse 1 : <label for=nom>Nom</label><input id=nom name=nom>.
- Réponse 2 : document.querySelector("#nom").value lit la saisie.
- Réponse 3 : GET /club?jour=mercredi transporte jour.
