# A4 — Matrice de builds

## Matrice correcte

6 ouvrages × 2 variantes = **12 sorties**, toutes suivies par Git.

| Ouvrage | Famille | Élève | Professeur | Touché par A4 | Construit au replay v3 | Motif si non construit |
|---|---|---|---|---|---|---|
| 1SPE | Mathématiques | oui | oui | **oui** (3 fiches TRIGO) | oui | — |
| TSPE_2026_2027 | Mathématiques | oui | oui | non (aucune fiche produite) | **NON** | omission de la matrice du replay |
| TCOMPL | Mathématiques | oui | oui | **oui** (50 fiches) | oui | — |
| TEXPERTES | Mathématiques | oui | oui | **oui** (33 fiches) | oui | — |
| 1NSI | NSI | oui | oui | **oui** (3 fiches ADGK) | oui | — |
| TNSI | NSI | oui | oui | non | oui | — |

## Réponse explicite

```
OLD_REPLAY               = 10
CORRECT_EXPECTED_MATRIX  = 12
MISSING_FROM_OLD_REPLAY  = TSPE_2026_2027 élève, TSPE_2026_2027 professeur
```

`WHY_10_AND_NOT_12` : le replay avait été construit sur le périmètre « manuels
ayant reçu des fiches méthodes ». TSPE n'a reçu aucune fiche de la campagne
A4, il avait donc été écarté — à tort, pour deux raisons indépendantes.

`WHY_INCLUDED_NOW` :

1. **Producteur partagé modifié.** La correction de reproductibilité touche
   `assemble_manuel.py` (Mathématiques), donc TSPE aussi : ses PDF changent
   même si aucune de ses sources pédagogiques ne change.
2. **PDF suivis par Git.** Les deux PDF TSPE sont versionnés
   (`Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/…`) : les laisser
   hors matrice reviendrait à committer un arbre dont deux artefacts suivis ne
   correspondent plus à leur producteur.

Noter que TNSI était déjà construit sans être touché par A4 : le périmètre du
replay était donc incohérent avec lui-même, ce que cette matrice corrige.

## Sorties hors matrice de build

`MANUELS_PDF_PUBLICATION/` contient 12 PDF de publication distincts des
artefacts de build. Ils ne sont pas régénérés par les assembleurs de la
matrice ci-dessus et ne relèvent pas de la clôture A4 ; ils restent inchangés.

## Reconstruction de clôture (12/12)

Reconstruction complète depuis un arbre propre après la correction du
producteur. Preuves par cible dans `A4_BUILD_MATRIX_EVIDENCE.json`
(identité de trailer, SHA du PDF, pagination, SHA du master et du `.fls`).

| Métrique | Valeur |
|---|---|
| Builds attendus | 12 |
| Builds réussis | **12** |
| Builds échoués | **0** |
| Fichiers PDF modifiés | **12** |
| Fichiers non-PDF modifiés | **0** |
| Paginations changées | **0** |
| Textes extraits changés | **0** |
| Divergences structurelles autres que `/ID` | **0** |

`VISUAL_CHANGE = 0` : pour chacune des 12 cibles, la comparaison du PDF
d'avant et d'après donne exactement deux lignes divergentes en représentation
QDF — le seul champ `/ID`, désormais canonique au lieu d'aléatoire.

`SELF_REFERENCE = NO`, revérifié **après** remplacement des PDF suivis : les
12 identités recalculées sont rigoureusement identiques à celles de la matrice
établie avant reconstruction.
