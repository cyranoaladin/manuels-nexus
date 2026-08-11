---
title: "P13 - td - dichotomie, glouton et k-NN"
level: "premiere"
sequence_id: "P13"
document_type: "td"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "dichotomie, glouton et k-NN"
notion: "dichotomie, glouton et k-NN"
private_data: false
official_program:
  capacities:
    - "P-ALGO-03"
    - "P-ALGO-04"
    - "P-ALGO-05"
---

# P13 - TD - dichotomie, glouton et k-NN

## Objectifs
- Travailler dichotomie, variant V = droite − gauche + 1, glouton, choix local, k-NN.
- Produire neuf réponses vérifiables avec données explicites et variées.

## Progression socle / standard / approfondissement
- Socle : exercices 1 et 2.
- Standard : exercices 3 à 6.
- Approfondissement : exercices 7, 8 et 9.

## Exercices
### Exercice 1
- Type : lecture/analyse.
- Capacité officielle : P-ALGO-04.
- Données : tableau trié [4, 9, 18, 23, 37, 41] avec cible 37.
- Consigne : calculer milieu puis réduire l'intervalle ; traiter aussi `cible absente` si nécessaire.
- Réponse attendue : milieux 18 puis 37 → trouvé indice 4.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `cible absente`.
### Exercice 2
- Type : production/écriture.
- Capacité officielle : P-ALGO-04.
- Données : tableau trié [4, 9, 18, 23, 37, 41] avec cible 37.
- Consigne : montrer que le variant V = droite − gauche + 1 décroît strictement à chaque étape ; traiter aussi `cible absente` si nécessaire.
- Réponse attendue : V décroît de 6 à 3 → terminaison (cible trouvée à l'indice 4).
- Critère de réussite : donnée exacte, variant identifié, trace V décroissant, cas `cible absente` décidé.
### Exercice 3
- Type : production/écriture.
- Capacité officielle : P-ALGO-05.
- Données : pièces disponibles [10, 5, 2, 1] pour montant 28.
- Consigne : appliquer l'algorithme glouton pour rendre la monnaie ; traiter aussi `pièce 1 absente` si nécessaire.
- Réponse attendue : 28 = 10+10+5+2+1 (5 pièces).
- Critère de réussite : donnée exacte, méthode glouton appliquée, résultat final et décision sur `pièce 1 absente`.
### Exercice 4
- Type : cas limite.
- Capacité officielle : P-ALGO-03.
- Données : voisins étiquetés rouge distance 1.2, bleu distance 2.0, rouge distance 2.4 avec k=3.
- Consigne : déterminer la classe prédite par vote majoritaire parmi les k plus proches voisins ; traiter aussi `égalité de vote` si nécessaire.
- Réponse attendue : rouge (2 voix) vs bleu (1 voix) → classe rouge.
- Critère de réussite : donnée exacte, distances triées, vote explicite et décision sur `égalité de vote`.
### Exercice 5
- Type : justification.
- Capacité officielle : P-ALGO-04.
- Données : tableau trié [4, 9, 18, 23, 37, 41] avec cible 23.
- Consigne : montrer que le variant V = droite − gauche + 1 décroît strictement à chaque étape ; conclure sur la terminaison.
- Réponse attendue : V décroît de 6 à 3 puis 1 → terminaison (cible trouvée à l'indice 3).
- Critère de réussite : donnée exacte, variant identifié, trace V=6→3→1, terminaison prouvée par trace.
### Exercice 6
- Type : lecture/analyse.
- Capacité officielle : P-ALGO-05.
- Données : pièces disponibles [10, 5, 2, 1] pour montant 13.
- Consigne : appliquer l'algorithme glouton ; traiter aussi `pièce 1 absente` si nécessaire.
- Réponse attendue : 13 = 10+2+1 (3 pièces).
- Critère de réussite : donnée exacte, méthode glouton appliquée, résultat final et décision sur `pièce 1 absente`.
### Exercice 7
- Type : production/écriture.
- Capacité officielle : P-ALGO-03.
- Données : points étiquetés (2,3,A) (5,4,B) (1,1,A) (8,7,B) (3,2,A) avec nouveau point (4,3) et k=3.
- Consigne : calculer les distances, identifier les 3 plus proches voisins et voter ; traiter aussi `égalité de vote (k=2)` si nécessaire.
- Réponse attendue : 3 plus proches = A(3,2) B(5,4) A(2,3) → vote A=2, B=1 → classe A.
- Critère de réussite : distances correctes, tri vérifié, vote majoritaire explicite, cas `k=2` traité.
### Exercice 8
- Type : justification.
- Capacité officielle : P-ALGO-04.
- Données : tableau trié [4, 9, 18, 23, 37, 41] avec cible 38 (absente).
- Consigne : montrer que le variant V = droite − gauche + 1 décroît à chaque étape ; conclure sur la terminaison sans trouver la cible.
- Réponse attendue : V décroît de 6 à 3 puis 1 puis 0 → la boucle s'arrête, cible absente.
- Critère de réussite : donnée exacte, variant identifié, trace V=6→3→1→0, terminaison prouvée par trace.

### Exercice 9
- Type : production/écriture.
- Capacité officielle : P-ALGO-03.
- Données : données d'entraînement = [(2, 3, "A"), (5, 4, "B"), (1, 1, "A"), (8, 7, "B"), (3, 2, "A")]. Nouveau point = (4, 3). k = 3. ; jeu_exercice=iota
- Consigne : (9a) calculer la distance euclidienne entre le nouveau point et chaque point d'entraînement ; (9b) identifier les 3 plus proches voisins ; (9c) déterminer la classe prédite par vote majoritaire ; (9d) que se passe-t-il si k = 2 et les deux voisins sont de classes différentes ?
- Réponse attendue : distances calculées, 3 plus proches identifiés, classe prédite = "A", cas k=2 → égalité.
- Critère de réussite : distances correctes, tri vérifié, vote majoritaire explicite, cas d'égalité traité.

## Corrigé
### Corrigé exercice 1
- Donnée : tableau trié [4, 9, 18, 23, 37, 41] avec cible 37.
- Méthode : calculer milieu puis réduire l'intervalle.
- Résultat : milieux 18 puis 37 → trouvé indice 4.
- Contrôle : capacité P-ALGO-04 vérifiée ; erreur traitée : dichotomie sur liste non triée.
- Cas limite : cible absente → la boucle s'arrête quand gauche > droite.
### Corrigé exercice 2
- Donnée : tableau trié [4, 9, 18, 23, 37, 41] avec cible 37.
- Méthode : montrer que V = droite − gauche + 1 décroît strictement à chaque étape.
- Résultat : V décroît de 6 à 3 → terminaison (cible trouvée à l'indice 4).
- Contrôle : capacité P-ALGO-04 vérifiée ; erreur traitée : variant non identifié.
- Cas limite : cible absente (ex. 38) → V décroît 6→3→1→0, la boucle s'arrête sans trouver.
### Corrigé exercice 3
- Donnée : pièces [10, 5, 2, 1] pour montant 28.
- Méthode : prendre la plus grande pièce possible à chaque étape.
- Résultat : 28 = 10+10+5+2+1 (5 pièces).
- Contrôle : capacité P-ALGO-05 vérifiée ; erreur traitée : glouton supposé toujours optimal.
- Cas limite : pièce 1 absente → montant=28 avec pièces=[10,5,2] → glouton bloqué à reste=1, alors que 28=10+10+2+2+2+2 est représentable.
### Corrigé exercice 4
- Donnée : voisins rouge:1.2, bleu:2.0, rouge:2.4 avec k=3.
- Méthode : trier par distance, voter parmi les k plus proches.
- Résultat : rouge (2 voix) vs bleu (1 voix) → classe rouge.
- Contrôle : capacité P-ALGO-03 vérifiée ; erreur traitée : égalité k-NN non décidée.
- Cas limite : k pair → égalité de vote possible.
### Corrigé exercice 5
- Donnée : tableau trié [4, 9, 18, 23, 37, 41] avec cible 23.
- Méthode : montrer que V = droite − gauche + 1 décroît strictement à chaque étape.
- Résultat : V décroît de 6 à 3 puis 1 → terminaison (cible=23 trouvée à l'indice 3).
- Contrôle : capacité P-ALGO-04 vérifiée ; erreur traitée : variant non identifié.
- Cas limite : cible absente → V atteint 0.
### Corrigé exercice 6
- Donnée : pièces [10, 5, 2, 1] pour montant 13.
- Méthode : prendre la plus grande pièce possible à chaque étape.
- Résultat : 13 = 10+2+1 (3 pièces).
- Contrôle : capacité P-ALGO-05 vérifiée ; erreur traitée : glouton supposé toujours optimal.
- Cas limite : pièce 1 absente → montant=28 avec pièces=[10,5,2] → glouton bloqué à reste=1, alors que 28=10+10+2+2+2+2 est représentable.
### Corrigé exercice 7
- Donnée : points (2,3,A) (5,4,B) (1,1,A) (8,7,B) (3,2,A) avec nouveau (4,3) et k=3.
- Méthode : distance euclidienne, tri, vote majoritaire.
- Résultat : 3 plus proches = A(3,2) B(5,4) A(2,3) → vote A=2, B=1 → classe A.
- Contrôle : capacité P-ALGO-03 vérifiée ; erreur traitée : égalité k-NN non décidée.
- Cas limite : k=2 → A(3,2) et B(5,4) à distance égale → égalité, résultat indéterminé.
### Corrigé exercice 8
- Donnée : tableau trié [4, 9, 18, 23, 37, 41] avec cible 38 (absente).
- Méthode : montrer que V = droite − gauche + 1 décroît strictement à chaque étape.
- Résultat : V décroît de 6 à 3 puis 1 puis 0 → cible absente, boucle terminée.
- Contrôle : capacité P-ALGO-04 vérifiée ; erreur traitée : boucle infinie si variant mal défini.
- Cas limite : V atteint 0, gauche > droite, arrêt sans trouver.

### Corrigé exercice 9
- Capacité mobilisée : P-ALGO-03.
- Résultat attendu : (9a) d(A(2,3))=2.00, d(B(5,4))=1.41, d(A(1,1))=3.61, d(B(8,7))=5.66, d(A(3,2))=1.41. (9b) 3 plus proches : A(3,2) d=1.41, B(5,4) d=1.41, A(2,3) d=2.00. (9c) Vote : A=2, B=1 → classe prédite = "A". (9d) k=2 : A(3,2) et B(5,4) à distance égale → égalité 1-1, résultat indéterminé.
- Justification : la tâche `classifier par k-NN` s'applique aux données d'entraînement avec distance euclidienne et vote majoritaire ; erreur évitée : égalité k-NN non décidée.
- Donnée utilisée iota dans P13 TD dichotomie glouton knn : cas iota de l'exercice 9 avec 5 points et k=3.
- Méthode iota dans P13 TD dichotomie glouton knn : calcul de distance euclidienne, tri, sélection des k plus proches, vote majoritaire.
- Résultat iota dans P13 TD dichotomie glouton knn : classe prédite "A" avec vote 2 contre 1.
- Contrôle iota dans P13 TD dichotomie glouton knn : le cas limite « k=2 avec égalité de vote » est traité explicitement.

## Erreurs fréquentes
- dichotomie sur liste non triée.
- glouton supposé toujours optimal.
- égalité k-NN non décidée.

## Différenciation
- Socle : données annotées.
- Standard : méthode complète.
- Expert : transfert avec `pièce 1 absente`.

## Cas limites travaillés
- cible absente.
- pièce 1 absente.
- égalité de vote.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `milieux 18 puis 37 -> trouvé indice 4`.
- Au moins un cas limite de la section précédente est décidé.

