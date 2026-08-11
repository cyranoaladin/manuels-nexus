---
title: "Corrigé professeur - représentation des données"
niveau: premiere
source: "Prototype interne"
status: needs_review
version: "0.5.0"
notion: "corrigé professeur"
objectifs: "Document professeur exploitable en prototype, à relire avant usage."
sequence: s01_representation_donnees
private_data: false
---

# Corrigé professeur - représentation des données

**Document professeur uniquement. Statut : `needs_review`.**

## Question 1 - Conversion entière

- Capacité officielle associée : P-DATA-BASE-01.
- Réponse attendue : 45 = 101101 en base 2 et 2D en base 16..
- Justification : Décomposition en puissances de deux puis groupement par quatre bits..
- Barème question par question : 2.5 points, dont 0,5 compréhension, 1 méthode, 0,5 résultat, 0,5 justification.
- Variante acceptable : Divisions successives acceptées..
- Erreurs fréquentes : restes lus dans le mauvais ordre.
- Remédiation associée : reprendre un exemple à deux chiffres puis vérifier en base 10.
- Critère de réussite : la valeur est conservée dans chaque base.

## Question 2 - Bits nécessaires

- Capacité officielle associée : P-DATA-BASE-02A.
- Réponse attendue : 255 nécessite 8 bits ; 256 nécessite 9 bits..
- Justification : 8 bits codent de 0 à 255, donc 256 dépasse cette plage..
- Barème question par question : 2.5 points, dont 0,5 compréhension, 1 méthode, 0,5 résultat, 0,5 justification.
- Variante acceptable : raisonnement par puissances de deux accepté..
- Erreurs fréquentes : confondre nombre de valeurs et plus grande valeur.
- Remédiation associée : faire écrire les intervalles 0..2^n-1.
- Critère de réussite : l’intervalle est cité.

## Question 3 - Complément à deux

- Capacité officielle associée : P-DATA-BASE-02B.
- Réponse attendue : 1101..
- Justification : 3 vaut 0011, inversion 1100, ajout de 1 : 1101..
- Barème question par question : 2.5 points, dont 0,5 compréhension, 1 méthode, 0,5 résultat, 0,5 justification.
- Variante acceptable : 16 - 3 = 13 donc 1101 accepté..
- Erreurs fréquentes : oublier la taille fixe.
- Remédiation associée : dresser la table sur 4 bits.
- Critère de réussite : la vérification 13-16=-3 est donnée.

## Question 4 - Booléens

- Capacité officielle associée : P-DATA-BASE-04.
- Réponse attendue : Seule la ligne A vrai et B faux est fausse..
- Justification : La négation porte seulement sur A..
- Barème question par question : 2.5 points, dont 0,5 compréhension, 1 méthode, 0,5 résultat, 0,5 justification.
- Variante acceptable : notation 0/1 acceptée..
- Erreurs fréquentes : nier toute l’expression.
- Remédiation associée : séparer les colonnes A, B, non A, résultat.
- Critère de réussite : quatre lignes sont présentes.

## Question 5 - Unicode

- Capacité officielle associée : P-DATA-BASE-05A.
- Réponse attendue : Unicode fournit un répertoire commun de caractères au-delà d’ASCII..
- Justification : Il évite de limiter les textes aux caractères latins simples..
- Barème question par question : 2.5 points, dont 0,5 compréhension, 1 méthode, 0,5 résultat, 0,5 justification.
- Variante acceptable : exemple non latin accepté..
- Erreurs fréquentes : confondre caractère et police.
- Remédiation associée : comparer symbole affiché et code stocké.
- Critère de réussite : ASCII et Unicode sont distingués.

## Question 6 - Tuple

- Capacité officielle associée : P-DATA-CONSTR-01.
- Réponse attendue : Une fonction peut retourner `(q, r)`..
- Justification : Un p-uplet regroupe plusieurs valeurs de retour..
- Barème question par question : 2.5 points, dont 0,5 compréhension, 1 méthode, 0,5 résultat, 0,5 justification.
- Variante acceptable : tuple nommé accepté si expliqué..
- Erreurs fréquentes : modifier une variable globale.
- Remédiation associée : faire tracer entrée et sortie.
- Critère de réussite : deux valeurs sont retournées.

## Question 7 - Tableau

- Capacité officielle associée : P-DATA-CONSTR-02A.
- Réponse attendue : Les indices valides sont 0, 1 et 2..
- Justification : L’indexation Python commence à zéro..
- Barème question par question : 2.5 points, dont 0,5 compréhension, 1 méthode, 0,5 résultat, 0,5 justification.
- Variante acceptable : boucle sur valeurs acceptée si l’indice n’est pas utile..
- Erreurs fréquentes : utiliser l’indice 3.
- Remédiation associée : dessiner cases et indices.
- Critère de réussite : aucun accès hors borne.

## Question 8 - Tests

- Capacité officielle associée : P-LANG-04.
- Réponse attendue : Tester 0 et une valeur avec lettre hexadécimale, par exemple 45..
- Justification : Les tests couvrent cas limite et cas standard..
- Barème question par question : 2.5 points, dont 0,5 compréhension, 1 méthode, 0,5 résultat, 0,5 justification.
- Variante acceptable : test d’erreur accepté..
- Erreurs fréquentes : donner une entrée sans sortie attendue.
- Remédiation associée : imposer entrée, sortie, raison.
- Critère de réussite : les tests sont exécutables.
