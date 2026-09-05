# Rapport de Validation du Code Imprime -- Nexus Reussite

- **Statut fidelite globale** : `PASS`
- **Erreurs de syntaxe** : `0`
- **Divergences de sortie attendue** : `0`
- **Guillemets courbes detectes** : `0`
- **Ligatures destructives** : `0`

## Metriques de couverture et reconciliation
- Blocs Python audites : 1014
- Blocs SQL audites : 152 (dont 110 requetes executees avec succes sous SQLite et 42 schemas relationnels textuels)
- Blocs Console audites : 123
- Blocs complementaires : 134 (46 codereference, 10 verbatim, 78 pseudocode)
- **TOTAL BLOCS DE CODE IMPRIMES** : **1423**
- **CODE NON CLASSIFIE** : **`0`**
- Executions BEGIN-VERIFY verifiees : 133
- Fichiers sources audites : 5384

## Justification des ecarts de certification
- **1423 vs 1289** : 1289 blocs correspondent aux environnements directement exécutables et consoles (1014 Python + 152 SQL + 123 consoles). Les 134 blocs complémentaires qui portent le grand total à 1423 blocs de code imprimés se décomposent en : 46 fiches de référence syntaxique codereference, 10 extraits verbatim de flux bruts, et 78 spécifications d'algorithmes en pseudo-code formalisé. Aucun bloc de code n'est non classifié (0).
- **SQL 152 vs 133** : Sur les 152 blocs SQL imprimés, exactement 133 correspondent à des requêtes actives (SELECT, INSERT, UPDATE, DELETE) accompagnées de leur bloc d'assertion BEGIN-VERIFY exécuté sans erreur dans SQLite. Les 19 blocs restants correspondent aux schémas relationnels textuels Inscription(...) des exercices de modélisation (13 blocs) et aux définitions déclaratives CREATE TABLE du cours (6 blocs) ne nécessitant pas de jeu d'essai isolé.

## Rapports de fidelite par manuel
- **1SPE** : `PASS`
- **TSPE_2026_2027** : `PASS`
- **TCOMPL** : `PASS`
- **TEXPERTES** : `PASS`
- **1NSI** : `PASS`
- **TNSI** : `PASS`
