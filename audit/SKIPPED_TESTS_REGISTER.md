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

| Test paramétré | Type attendu | Raison | Propriétaire | Réactivation | Phase 0 | Release |
|---|---|---|---|---|---|---|
| `montrer qu'une suite est géométrique` | `exercice` | index RAG absent | `ingenierie_build_qualite` | index reproductible disponible et oracle scientifique relu | non bloquant | bloquant |
| `somme des premiers termes suite géométrique démonstration` | `cours` | index RAG absent | `ingenierie_build_qualite` | index reproductible disponible et oracle scientifique relu | non bloquant | bloquant |
| `erreur fréquente suites arithmétiques rapport jury` | `erreur_type` | index RAG absent | `ingenierie_build_qualite` | index reproductible disponible et oracle scientifique relu | non bloquant | bloquant |
| `algorithme seuil boucle while suite` | `exercice` | index RAG absent | `ingenierie_build_qualite` | index reproductible disponible et oracle scientifique relu | non bloquant | bloquant |
| `activité introduction suites intérêts composés` | `activite` | index RAG absent | `ingenierie_build_qualite` | index reproductible disponible et oracle scientifique relu | non bloquant | bloquant |

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

Preuve de reproduction :

```text
SKIPPED [5] test_retrieval.py:18:
MODE FICHIERS : index RAG non disponible
5 skipped
```
