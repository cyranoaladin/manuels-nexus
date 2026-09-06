# Rapport de Validation du Code Imprime -- Nexus Reussite

- **Statut fidelite globale** : `PASS`
- **Erreurs de syntaxe** : `0`
- **Divergences de sortie attendue** : `0`
- **Guillemets courbes detectes** : `0`
- **Ligatures destructives** : `0`

## Metriques de couverture et reconciliation
- Blocs Python audites : 1020
- Blocs SQL audites : 152 (dont 110 requetes executees avec succes sous SQLite et 42 schemas relationnels textuels)
- Blocs Console audites : 123
- Blocs complementaires : 56 (46 codereference, 10 verbatim)
- **TOTAL BLOCS DE CODE IMPRIMES** : **1351**
- **CODE NON CLASSIFIE** : **`0`**
- Executions BEGIN-VERIFY verifiees : 133
- Fichiers sources audites : 5389

## Justification des ecarts de certification
- **Partition complete** : Le denombrement source distinct couvre 1020 blocs Python, 152 blocs SQL, 123 consoles, 46 fiches de reference syntaxique et 10 extraits verbatim, soit 1351 blocs, tous classifies (0 non classifie).
- **Occurrences imprimees vs blocs distincts** : Les rapports de fidelite comparent 1423 blocs caractere par caractere, mais ce sont des OCCURRENCES PAR VARIANTE, pas des blocs distincts : elles se rapportent a 1014 origines sources uniques, dont 605 composees dans une seule variante et 409 composees dans les deux (eleve et professeur). 605 + 2 x 409 = 1423. Il n'existe donc aucun bloc manquant entre les deux comptages : ce sont deux mesures de la meme population, l'une par surface imprimee, l'autre par source dedupliquee.
- **SQL imprime vs executions SQLite** : Les 133 executions SQLite ne sont pas un sous-ensemble des 152 blocs SQL imprimes : ce sont des harnais de verification Python (blocs BEGIN-VERIFY portant sqlite3) places dans les commentaires TeX, executes pour controler le resultat annonce. Les 152 blocs SQL imprimes se repartissent en 110 requetes executables (categorie EXECUTABLE_QUERY) et 42 schemas relationnels textuels (categorie RELATIONAL_SCHEMA), qui ne sont pas du SQL executable et n'ont donc pas de jeu d'essai.

## Rapports de fidelite par manuel
- **1SPE** : `PASS`
- **TSPE_2026_2027** : `PASS`
- **TCOMPL** : `PASS`
- **TEXPERTES** : `PASS`
- **1NSI** : `PASS`
- **TNSI** : `PASS`
