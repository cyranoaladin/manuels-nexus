# Registre des tests ignorés

État observé le 30 juillet 2026 : **5 tests collectés, 5 ignorés**.

Le mécanisme est un marqueur de module inconditionnel :

```python
pytestmark = pytest.mark.skip(
    reason="MODE FICHIERS : index RAG non disponible"
)
```

Ce skip n'est pas acceptable comme état permanent. Il est non bloquant pour le
gel structurel de Phase 0, mais reste bloquant pour une release du manuel tant
que l'oracle de recherche et l'index ne sont pas disponibles et validés.

## Inventaire

Fichier commun :
`Mathematiques/manuel-maths/tests/test_retrieval.py`.

La raison exacte portée par le marqueur Pytest est identique pour les cinq cas :

```text
MODE FICHIERS : index RAG non disponible
```

| Nom | Raison exacte | Dépendance manquante | Condition de réactivation | Propriétaire | Impact release | Solution prévue |
|---|---|---|---|---|---|---|
| `test_topk_contains_type[montrer qu'une suite est géométrique-exercice]` | `MODE FICHIERS : index RAG non disponible` | PostgreSQL 16+, extension `pgvector`, corpus Suites indexé avec BGE-M3 et dépendances Python RAG figées | index reproductible disponible ; résultat top 10 de type `exercice` ; oracle relu par la direction scientifique | `ingenierie_build_qualite` | **bloquant** : aucune preuve de rappel d'un exercice adapté | job CI RAG dédié, service PostgreSQL/pgvector, construction puis empreinte de l'index, exécution sans skip |
| `test_topk_contains_type[somme des premiers termes suite géométrique démonstration-cours]` | `MODE FICHIERS : index RAG non disponible` | PostgreSQL 16+, extension `pgvector`, corpus Suites indexé avec BGE-M3 et dépendances Python RAG figées | index reproductible disponible ; résultat top 10 de type `cours` ; oracle relu par la direction scientifique | `ingenierie_build_qualite` | **bloquant** : aucune preuve de rappel du cours/démonstration attendu | job CI RAG dédié, service PostgreSQL/pgvector, construction puis empreinte de l'index, exécution sans skip |
| `test_topk_contains_type[erreur fréquente suites arithmétiques rapport jury-erreur_type]` | `MODE FICHIERS : index RAG non disponible` | PostgreSQL 16+, extension `pgvector`, corpus qualifié incluant les sources institutionnelles, index BGE-M3 et dépendances Python RAG figées | index reproductible disponible ; résultat top 10 de type `erreur_type` ; provenance des sources et oracle relus | `ingenierie_build_qualite` | **bloquant** : aucune preuve de rappel d'une erreur-type sourcée | job CI RAG dédié, corpus qualifié et empreinté, contrôle de provenance, exécution sans skip |
| `test_topk_contains_type[algorithme seuil boucle while suite-exercice]` | `MODE FICHIERS : index RAG non disponible` | PostgreSQL 16+, extension `pgvector`, corpus Suites/Python indexé avec BGE-M3 et dépendances Python RAG figées | index reproductible disponible ; résultat top 10 de type `exercice` contenant un algorithme de seuil exécutable ; oracle relu | `ingenierie_build_qualite` | **bloquant** : aucune preuve de rappel d'un exercice Python pertinent et exécutable | job CI RAG dédié, index versionné, oracle enrichi d'un contrôle de code source, exécution sans skip |
| `test_topk_contains_type[activité introduction suites intérêts composés-activite]` | `MODE FICHIERS : index RAG non disponible` | PostgreSQL 16+, extension `pgvector`, corpus Suites indexé avec BGE-M3 et dépendances Python RAG figées | index reproductible disponible ; résultat top 10 de type `activite` ; pertinence pédagogique relue | `ingenierie_build_qualite` | **bloquant** : aucune preuve de rappel d'une activité d'introduction pertinente | job CI RAG dédié, index versionné, validation pédagogique de l'oracle, exécution sans skip |

La `direction_scientifique_programme` doit relire les types attendus et la
pertinence des résultats avant réactivation ; la responsabilité primaire de
l'infrastructure et de la reproductibilité reste
`ingenierie_build_qualite`.

## Conditions cumulatives de réactivation

1. PostgreSQL 16 ou version ultérieure et `pgvector` sont disponibles dans un
   job dédié.
2. Le schéma est chargé et le corpus est indexé avec la version BGE-M3
   documentée.
3. Le périmètre « suites » contient au moins 300 chunks issus d'au moins
   10 sources qualifiées.
4. Les dépendances `FlagEmbedding`, `sentence-transformers`, `psycopg` et
   `pgvector` sont figées.
5. L'oracle est complété de 5 à 20 requêtes, relu par
   `direction_scientifique_programme`.
6. Le skip de module est retiré ; une absence d'infrastructure produit alors un
   échec explicite du job dédié.

La `direction_editoriale_pedagogique` relit en plus le cas de type `activite`.
Le propriétaire primaire du rétablissement technique reste
`ingenierie_build_qualite`.

Preuve de reproduction :

```text
SKIPPED [5] test_retrieval.py:18:
MODE FICHIERS : index RAG non disponible
5 skipped
```
