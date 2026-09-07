# P0 — clonage pédagogique et fausse déclaration de capacité

Des objets pédagogiques partagent un corps rigoureusement identique tout
en déclarant des capacités différentes. Le cas le plus net : dix-sept
fiches de remédiation de `TSPE-GEOMETRIE-ESPACE`, déclarées `C1` à `C16`,
portent le même corps, dont l'en-tête annonce « FICHE DE REMEDIATION —
C7 : produit scalaire ». Un élève en échec sur `C1` recevait la fiche `C7`.

## Mesure

- objets analysés : `3224`
- groupes de corps identiques : `6`
- objets excédentaires : `14`
- objets à crédit invalide : `0`
- UNKNOWN : `0`

## Dispositions

| Disposition | Groupes | Objets excédentaires |
|---|---:|---:|
| `REDUNDANT_SAME_CAPACITY` | 6 | 14 |

## Par manuel

| Manuel | Objets excédentaires |
|---|---:|

Le corps pédagogique est le fichier moins sa seule ligne d'identité
`% META:`. Énoncé, mathématiques, code, méthode, solution, diagnostic,
remédiation, consigne et bloc de vérification en font partie : deux objets
dont seul le META diffère sont donc détectés.
