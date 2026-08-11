---
titre: Evaluation corrigee professeur - S01 representation des donnees
niveau: premiere
type: evaluation_corrigee
statut: needs_review
status: needs_review
sequence: S01 representation des donnees
notion: bases, entiers relatifs, booleens, texte, types construits
objectifs:
  - Corriger les conversions en bases 2, 10 et 16.
  - Corriger le complement a deux, les booleens, le texte et le choix de structure.
version: 0.3.0
public: professeur
source: generated
private_data: false
official_program:
  level: premiere
  rubrique: Representation des donnees
  content: Types et valeurs de base, types construits
  capacities:
    - id: P-DATA-BASE-01
      label: Ecrire un entier positif dans les bases 2, 10 et 16
    - id: P-DATA-BASE-02A
      label: Representer un entier relatif en complement a deux
    - id: P-DATA-BASE-04A
      label: Mettre en relation un caractere et son point de code
    - id: P-DATA-CONSTR-01A
      label: Construire et parcourir un tableau Python
---

# Evaluation corrigee professeur - S01 representation des donnees

Statut : document professeur non publiable, a relire pedagogiquement et scientifiquement.

## Conditions d'utilisation professeur

- Status : needs_review.
- Durée standard : 55 minutes.
- Matériel : ordinateur avec Python local ou feuille de brouillon selon version.
- Correction complète : toutes les questions de l'evaluation sont corrigees ci-dessous avec justification, bareme, variante acceptable, erreur frequente et remediation.
- Erreur fréquente : les erreurs signalees servent a preparer la remediation, pas a valider la publication.

## Barème global

- Question 1 : 2 points.
- Question 2 : 2 points.
- Question 3 : 2 points.
- Question 4 : 2 points.
- Question 5 : 2 points.
- Question 6 : 2 points.
- Question 7 : 3 points.
- Question 8 : 5 points.
- Total : 20 points.

## Question 1 - Ecriture positionnelle

- Capacité officielle : P-DATA-BASE-01.
- Reponse attendue : pour `45_10`, on obtient `101101_2` car `45 = 32 + 8 + 4 + 1`; en hexadecimal, `45 = 2 * 16 + 13`, donc `2D_16`.
- Justification : l'eleve doit expliciter les puissances utilisees ou la methode des divisions successives.
- Barème : 1 point pour la base 2 correcte ; 0,5 point pour la base 16 correcte ; 0,5 point pour la justification.
- Variante acceptable : divisions successives par 2 puis par 16, si les restes sont lus dans le bon sens.
- Erreurs fréquentes : lire les restes dans l'ordre de calcul ; confondre `D` avec 14 ; oublier l'indice de base.
- Remédiation : refaire une conversion guidee de `19_10` vers la base 2 avec tableau puissances/restes.
- Critere de reussite : la representation est correcte et la methode est verifiable.

## Question 2 - Base invalide ou chiffre invalide

- Capacité officielle : P-DATA-BASE-01.
- Reponse attendue : `10201_2` n'est pas valide en base 2 car le chiffre `2` n'existe pas dans cette base ; `7F_16` est valide car les chiffres autorises sont `0` a `9` et `A` a `F`.
- Justification : une ecriture en base `b` n'utilise que des chiffres de valeur strictement inferieure a `b`.
- Barème : 1 point pour le rejet de `10201_2` ; 0,5 point pour l'acceptation de `7F_16` ; 0,5 point pour la regle generale.
- Variante acceptable : formuler avec l'alphabet de la base.
- Erreurs fréquentes : juger la validite d'apres la taille du nombre en decimal ; accepter tous les symboles alphanumeriques.
- Remédiation : faire classer six ecritures courtes en valide/invalide avec justification d'un symbole fautif.
- Critere de reussite : chaque decision cite le symbole ou la regle qui la justifie.

## Question 3 - Complement a deux sur 4 bits

- Capacité officielle : P-DATA-BASE-02A.
- Reponse attendue : sur 4 bits, l'intervalle representable est de `-8` a `7`. `-3` se represente par `1101` car `0011` inverse donne `1100`, puis `+1` donne `1101`.
- Justification : le bit de poids fort indique une valeur negative dans cette convention et l'intervalle depend du nombre de bits.
- Barème : 0,5 point pour l'intervalle ; 1 point pour `1101` ; 0,5 point pour la methode.
- Variante acceptable : calculer `16 - 3 = 13`, puis convertir `13` en `1101`.
- Erreurs fréquentes : ecrire seulement un signe `-` devant `0011` ; oublier le `+1`; proposer une representation sur plus de 4 bits.
- Remédiation : reprendre les trois valeurs voisines `-1`, `-2`, `-8` sur 4 bits.
- Critere de reussite : la largeur en bits est conservee pendant tout le calcul.

## Question 4 - Tables de verite et booleens

- Capacité officielle : P-DATA-BASE-03A.
- Reponse attendue : pour l'expression `(a and not b) or c`, la ligne `a=True`, `b=True`, `c=False` donne `False`, car `not b` vaut `False`, donc `a and not b` vaut `False`, puis `False or False` vaut `False`.
- Justification : respecter les priorites `not`, puis `and`, puis `or` ou utiliser des parentheses explicites.
- Barème : 1 point pour la valeur finale ; 1 point pour le detail des etapes.
- Variante acceptable : table complete des huit lignes si la ligne demandee est correcte.
- Erreurs fréquentes : evaluer `or` avant `and`; confondre `not b` avec `b`; utiliser `=` au lieu d'une valeur booleenne.
- Remédiation : faire completer une table partielle avec colonnes intermediaires.
- Critere de reussite : les etapes logiques sont visibles.

## Question 5 - Texte, ASCII et Unicode

- Capacité officielle : P-DATA-BASE-04A.
- Reponse attendue : `A` a pour code Unicode `U+0041` et appartient a ASCII ; `é` a un point de code Unicode mais n'appartient pas a ASCII standard.
- Justification : ASCII standard code 128 caracteres ; Unicode attribue des points de code a un ensemble beaucoup plus large de caracteres.
- Barème : 0,5 point pour `A`; 0,5 point pour ASCII ; 0,5 point pour `é`; 0,5 point pour la distinction ASCII/Unicode.
- Variante acceptable : citer le code decimal `65` pour `A` si le lien avec `U+0041` est clair.
- Erreurs fréquentes : confondre caractere, point de code et encodage en octets ; affirmer que tous les caracteres accentues sont ASCII.
- Remédiation : comparer `A`, `a`, `é`, `🙂` avec une table de points de code.
- Critere de reussite : l'eleve distingue repertoire de caracteres et encodage.

## Question 6 - Liste, tuple, dictionnaire

- Capacité officielle : P-DATA-CONSTR-01A.
- Reponse attendue : une liste convient pour une collection ordonnee modifiable ; un tuple convient pour un enregistrement court non modifie ; un dictionnaire convient pour associer une cle a une valeur, par exemple `notes["Ada"] = 16`.
- Justification : le choix de la structure depend des operations attendues : acces par indice, immutabilite, acces par cle.
- Barème : 0,5 point par structure correctement caracterisee ; 0,5 point pour l'exemple Python pertinent.
- Variante acceptable : utiliser un dictionnaire pour compter des occurrences.
- Erreurs fréquentes : choisir un dictionnaire sans cle explicite ; utiliser un tuple pour des donnees qui doivent etre modifiees ; confondre indice et cle.
- Remédiation : faire associer trois besoins a trois structures avec une phrase de justification.
- Critere de reussite : le choix est justifie par une operation concrete.

## Question 7 - Analyse de code Python

- Capacité officielle : P-DATA-CONSTR-01A.
- Reponse attendue : dans un parcours `for valeur in valeurs`, l'indice n'est pas directement disponible ; si l'on doit modifier la liste a une position precise, il faut parcourir les indices ou construire une nouvelle liste.
- Justification : la boucle sur elements lit les valeurs ; la boucle sur indices donne acces a `valeurs[i]`.
- Barème : 1 point pour l'identification du probleme ; 1 point pour la correction ; 1 point pour l'explication.
- Variante acceptable : utiliser `enumerate` pour obtenir indice et valeur.
- Erreurs fréquentes : modifier la variable locale `valeur` en croyant modifier la liste ; depasser l'indice maximal ; oublier le cas liste vide.
- Remédiation : tracer un exemple a trois elements puis comparer `for valeur in` et `for i in range(len(...))`.
- Critere de reussite : le code corrige produit l'effet annonce sur la structure.

## Question 8 - Programmation courte testee

- Capacité officielle : P-DATA-BASE-01, P-DATA-CONSTR-01A.
- Reponse attendue : une fonction `convertir_vers_base(n, base)` qui refuse une base hors `{2, 10, 16}`, refuse un entier negatif dans cette question, traite `0`, puis construit les chiffres par divisions successives.
- Justification : les tests minimaux doivent couvrir `0`, une valeur ordinaire, une base invalide et un chiffre attendu en hexadecimal.
- Barème : 1 point pour la signature et les preconditions ; 1 point pour le cas `0`; 1 point pour la boucle de divisions ; 1 point pour l'ordre des restes ; 1 point pour les tests.
- Variante acceptable : utiliser une table de chiffres `"0123456789ABCDEF"` ou un dictionnaire de conversion.
- Erreurs fréquentes : boucle infinie si `n` n'est jamais divise ; inversion oubliee ; absence de test d'erreur ; retour d'un entier au lieu d'une chaine.
- Remédiation : fournir le squelette avec trois assertions et faire completer seulement la boucle.
- Critere de reussite : le code est executable, teste et les erreurs annoncees sont gerees.
