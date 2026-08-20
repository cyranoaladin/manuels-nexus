# Analyse de reproductibilité — identité de trailer PDF

Correction du producteur : commit `79267dd9`.

## Cause racine (mesurée, non supposée)

Deux compilations d'un même document minimal, sous `SOURCE_DATE_EPOCH` et
`FORCE_SOURCE_DATE` déjà actifs dans la toolchain, produisent des `/ID`
différents et donc des PDF de SHA différents. Avec `\pdfvariable trailerid`,
les mêmes deux compilations deviennent **byte-identiques**. La cause est donc
la génération non déterministe du trailer `/ID` par LuaTeX, et rien d'autre.

## État avant correction (campagne replay v3)

| Manuel/Livre | Variante | SHA A | SHA B | SHA == | Pages A/B | Diff structurel qpdf |
|---|---|---|---|---|---|---|
| 1SPE | eleve | `e42a8935e2f3e484…` | `53f7893a2ed3fd58…` | **non** | 375/375 | NOT_AVAILABLE |
| 1SPE | professeur | `a369e3b6d9290872…` | `05559813d55178f8…` | **non** | 619/619 | NOT_AVAILABLE |
| TSPE_2026_2027 | eleve | NOT_AVAILABLE | NOT_AVAILABLE | — | — | NOT_AVAILABLE |
| TSPE_2026_2027 | professeur | NOT_AVAILABLE | NOT_AVAILABLE | — | — | NOT_AVAILABLE |
| TCOMPL | eleve | `e414b536f05dac39…` | `8d70a05b3175623f…` | **non** | 164/164 | NOT_AVAILABLE |
| TCOMPL | professeur | `372821ba0d9ad3c3…` | `fb676dd203f28eed…` | **non** | 229/229 | NOT_AVAILABLE |
| TEXPERTES | eleve | `861ecd2b5577b150…` | `a59581a6a347f961…` | **non** | 109/109 | 2 lignes, /ID[1] seul |
| TEXPERTES | professeur | `54efae58cd04a8ea…` | `addc09e464488b1e…` | **non** | 153/153 | NOT_AVAILABLE |
| 1NSI | eleve | `42bd600de6fa06d0…` | `40acf03e43e42f98…` | **non** | 235/235 | NOT_AVAILABLE |
| 1NSI | professeur | `b62db582654bb6c0…` | `2f11867c4dc3737e…` | **non** | 378/378 | NOT_AVAILABLE |
| TNSI | eleve | `f3a8559f0eba263c…` | `2a961fdf868d9b7f…` | **non** | 149/149 | NOT_AVAILABLE |
| TNSI | professeur | `b9da49e948ff098a…` | `64eb0342caa22a37…` | **non** | 240/240 | NOT_AVAILABLE |

## Métriques

- cibles totales : **12**
- mesurées avant correction : **10** (les 2 TSPE manquaient à l'ancien replay)
- SHA identiques avant correction : **0**
- SHA différents avant correction : **10**
- paginations identiques avant correction : **10** — le contenu ne variait pas

## Limite d'évidence assumée

Les PDF reconstruits avant correction ont ete ecrases par la restauration d'arbre du replay: seuls leurs SHA256 et paginations subsistent, plus un diff structurel qpdf complet mesure sur TEXPERTES/eleve. Aucune donnee n'est reconstituee.

## Classification

`NONDETERMINISTIC_TRAILER_SECOND_ID_ONLY` pour les 10 cibles mesurées :
pagination identique, aucune divergence de contenu observée, et sur la seule
cible dont les deux PDF ont pu être comparés structurellement, exactement
deux lignes divergentes — le champ `/ID`.

## Preuve finale

Campagne deterministe post-correction: COMMITTED == FRESH_A == FRESH_B pour les 12 cibles (voir rapport de cloture).
