# P0 — clonage pédagogique et fausse déclaration de capacité

Des objets pédagogiques partagent un corps rigoureusement identique tout
en déclarant des capacités différentes. Le cas le plus net : dix-sept
fiches de remédiation de `TSPE-GEOMETRIE-ESPACE`, déclarées `C1` à `C16`,
portent le même corps, dont l'en-tête annonce « FICHE DE REMEDIATION —
C7 : produit scalaire ». Un élève en échec sur `C1` recevait la fiche `C7`.

## Mesure

- objets analysés : `5582`
- groupes de corps identiques : `332`
- objets excédentaires : `1535`
- objets à crédit invalide : `1498`
- UNKNOWN : `0`

## Dispositions

| Disposition | Groupes | Objets excédentaires |
|---|---:|---:|
| `BOILERPLATE_ONLY` | 18 | 50 |
| `CAPACITY_MISREPRESENTING_CLONE` | 305 | 1455 |
| `CROSS_CHAPTER_CONTAMINATION` | 3 | 6 |
| `CROSS_MANUAL_CONTAMINATION` | 2 | 2 |
| `REDUNDANT_SAME_CAPACITY` | 4 | 22 |

## Par manuel

| Manuel | Objets excédentaires |
|---|---:|
| `1NSI` | 517 |
| `1SPE` | 18 |
| `TNSI` | 610 |
| `TSPE` | 390 |

Le corps pédagogique est le fichier moins sa seule ligne d'identité
`% META:`. Énoncé, mathématiques, code, méthode, solution, diagnostic,
remédiation, consigne et bloc de vérification en font partie : deux objets
dont seul le META diffère sont donc détectés.
