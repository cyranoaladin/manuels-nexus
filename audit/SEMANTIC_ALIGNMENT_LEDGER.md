# Registre d'alignement sémantique

Ce registre **n'approuve rien** et ne rend aucune cellule verte. Il route
les cellules que la mesure laisse en
`DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED` : pour chacune, il dit ce que la machine
peut démontrer et ce qu'elle ne peut pas.

L'objectif n'est pas `DEFAUT_ETABLI = 0` — une revue humaine est un
résultat légitime — mais `UNKNOWN = 0`.

- portée : `1SPE`
- cellules examinées : `381`
- `SEMANTIC_ROUTING_UNRESOLVED` : `0`
- `SEMANTIC_CERTIFICATION_PENDING` : `381`
- `DEFAUT_ETABLI` : `0`
- `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS` : `381`
- `UNKNOWN` : `0`

| Chapitre | DEFAUT_ETABLI | JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS | Total |
|---|---:|---:|---:|
| `1SPE-DERIVATION-GLOBAL` | 0 | 35 | **35** |
| `1SPE-DERIVATION-LOCAL` | 0 | 35 | **35** |
| `1SPE-EXPONENTIELLE` | 0 | 35 | **35** |
| `1SPE-GEOMETRIE-REPEREE` | 0 | 35 | **35** |
| `1SPE-PROBA-COND` | 0 | 35 | **35** |
| `1SPE-PRODUIT-SCALAIRE` | 0 | 35 | **35** |
| `1SPE-SECOND-DEGRE` | 0 | 52 | **52** |
| `1SPE-SUITES` | 0 | 56 | **56** |
| `1SPE-TRIGONOMETRIE` | 0 | 14 | **14** |
| `1SPE-VARIABLES-ALEATOIRES` | 0 | 49 | **49** |

## Défauts établis

Aucun. Les canaux de preuve disponibles ne contredisent aucune
cellule de cette portée. Ce n'est pas un satisfecit : cela signifie
que l'alignement sémantique reste, pour toutes ces cellules, un
jugement pédagogique humain.

## Ce que ce registre s'interdit

- aucune liste blanche, aucun solveur par identifiant d'objet ;
- aucune valeur attendue codée en dur, aucune règle nommant un chapitre ;
- aucun appariement par ressemblance lexicale entre le libellé d'une
  capacité et le corps d'un objet ;
- aucune certification **positive** d'alignement sémantique.

Chaque corps rattaché porte son `sha256` : le dossier se périme dès que
le contenu change.
