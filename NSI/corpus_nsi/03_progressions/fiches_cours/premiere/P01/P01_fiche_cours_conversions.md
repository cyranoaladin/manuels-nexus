---
title: "P01 - Fiche cours - Conversions entre bases"
level: "premiere"
sequence_id: "P01"
document_type: "fiche_cours"
status: "needs_review"
version: "0.1.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Représentation des entiers"
notion: "conversions"
official_program:
  capacities:
    - "P-DATA-BASE-01"
readiness: operational
private_data: false
---
# P01 - Fiche cours - Conversions entre bases

## À savoir
- conversions entre bases se travaille dans le contexte “entiers positifs” avec des données vérifiables.
- La fiche distingue vocabulaire, méthode, exemple corrigé et contrôle pour conversions.
- Les capacités P-DATA-BASE-01 sont rappelées ici sans être déclarées couvertes.
- L’élève doit pouvoir refaire un exemple de conversions entre bases avec une valeur, une table ou un code différent.

## Méthodes
1. Capacités explicitement travaillées dans les méthodes et exercices : P-DATA-BASE-01.
2. P-DATA-BASE-01 : choisir la base cible puis écrire les divisions ou les poids.
3. En décimal vers binaire, noter quotient et reste dans deux colonnes.
4. En binaire vers décimal, additionner les puissances de deux associées aux bits à 1.
5. En binaire vers hexadécimal, grouper par 4 bits depuis la droite.

## Exemples corrigés
### Exemple corrigé 1 - Conversion décimal vers binaire
45₁₀ : 45/2 donne reste 1, 22/2 reste 0, 11/2 reste 1, 5/2 reste 1, 2/2 reste 0, 1/2 reste 1. La lecture inverse donne 101101₂.
### Exemple corrigé 2 - Lecture positionnelle
101101₂ vaut 1×32 + 0×16 + 1×8 + 1×4 + 0×2 + 1×1 = 45₁₀.
### Exemple corrigé 3 - Binaire vers hexadécimal
1110 1010₂ se découpe en 1110 puis 1010 : 1110₂ = E₁₆ et 1010₂ = A₁₆, donc EA₁₆.
### Exemple corrigé 4 - Même valeur, écritures différentes
45₁₀, 101101₂ et 2D₁₆ représentent la même valeur ; la vérification passe par la conversion vers 45₁₀.

## Erreurs fréquentes
- Confondre le vocabulaire de conversions avec une simple récitation : corriger par un exemple calculé ou exécuté.
- Oublier une hypothèse de entiers positifs : corriger en l’écrivant avant la méthode.
- Conclure sans contrôle sur conversions entre bases : corriger par un cas limite ou une vérification inverse.

## Cas limites
- Cas de départ vide ou nul pour conversions, à traiter selon la convention du chapitre P01.
- Donnée invalide dans entiers positifs, par exemple symbole interdit, clé absente ou requête trop large selon la fiche.
- Cas frontière de conversions entre bases où une seule valeur change la méthode ou le résultat attendu.

## Mini-exercices
### Mini-exercice 1
P-DATA-BASE-01 : convertir 19₁₀ en binaire par divisions.
### Mini-exercice 2
P-DATA-BASE-01 : convertir 100110₂ en décimal par poids.
### Mini-exercice 3
Convertir 7B₁₆ en décimal.
### Mini-exercice 4
Vérifier que 11111₂ vaut 31₁₀.

## Réponses rapides
1. 19₁₀ = 10011₂ : les restes 1,1,0,0,1 sont lus du dernier au premier.
2. 100110₂ = 38₁₀ car seuls les poids 32, 4 et 2 sont actifs.
3. 7B₁₆ = 123₁₀ : B vaut 11 et la position de gauche vaut 16.
4. 11111₂ = 31₁₀, ce qui vérifie l’écriture binaire par addition des cinq poids.

## À retenir
- P01 : conversions se révise avec une définition, une méthode et un exemple corrigé.
- Les capacités P-DATA-BASE-01 restent en travail tant que TD, TP, évaluation, barème et revues humaines manquent.
- Un exemple de conversions entre bases doit changer autre chose qu’une simple valeur pour tester la compréhension.
- Pour P01, le tableau de liens distingue les supports existants et les supports inscrits au registre.
- La fiche P01 sur conversions reste needs_review et ne déclenche ni publication ni couverture.

## Lien avec la progression

| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | P01-S1 | prête | séance présente dans la progression |
| TD | 03_progressions/supports/premiere/P01/P01_td_conversions_bases.md | existant | support associé existant dans 03_progressions/supports |
| TP | 03_progressions/supports/premiere/P01/P01_tp_conversions_bases.md | existant | support associé existant dans 03_progressions/supports |
| Évaluation | 03_progressions/supports/premiere/P01/P01_evaluation_conversions_bases.md | existant | support associé existant dans 03_progressions/supports |

## Auto-évaluation
- Je peux expliquer conversions avec un exemple différent de ceux de la fiche P01.
- Je peux citer au moins une capacité parmi P-DATA-BASE-01 et dire où elle est travaillée dans la fiche.
- Je peux dire quel support lié à P01 existe déjà ou reste inscrit au registre.
- Je peux identifier un cas limite de conversions entre bases sans transformer la fiche en corrigé complet.
