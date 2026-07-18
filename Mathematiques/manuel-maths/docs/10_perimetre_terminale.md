# Perimetre Terminale specialite mathematiques (TSPE)

## Source reglementaire

### TSPE v1 (rentree 2026-2027)
Programme de specialite mathematiques, classe terminale generale.
**BO special n 8 du 25 juillet 2019** (arrete du 19-07-2019, MENE1921247A).
Texte depose : `sources/BO2019_TSPE_specialite.pdf`.

### TSPE v2 (rentree 2027-2028 — backlog)
Le nouveau programme Terminale (arrete MENE2602919A) n'entre en application
qu'a la rentree 2027-2028. Le manuel TSPE v2 sera produit sur ce referentiel
quand la rentree 2027 approchera. Les contenus retires de 1SPE par le BO 2026
(notamment fonctions sin/cos si confirme) basculent dans le backlog TSPE v2.

## Architecture (12 chapitres, programme 2019)

| # | Chapitre | Theme BO 2019 |
|---|---|---|
| 1 | TSPE-SUITES-LIMITES | Suites : limites, theoremes de convergence |
| 2 | TSPE-FONCTIONS-LIMITES | Fonctions : limites, comparaison, asymptotes |
| 3 | TSPE-CONTINUITE | Continuite, TVI |
| 4 | TSPE-DERIVATION | Complementes de derivation (convexite, points d'inflexion) |
| 5 | TSPE-LOGARITHME | Fonction logarithme neperien |
| 6 | TSPE-PRIMITIVES-INTEGRALES | Primitives et calcul integral |
| 7 | TSPE-EQUATIONS-DIFFERENTIELLES | Equations differentielles y'=ay, y'=ay+b |
| 8 | TSPE-COMBINATOIRE-DENOMBREMENT | Combinatoire, coefficients binomiaux |
| 9 | TSPE-PROBABILITES | Lois a densite, loi normale, estimation |
| 10 | TSPE-GEOMETRIE-ESPACE | Geometrie dans l'espace (droites, plans, orthogonalite) |
| 11 | TSPE-NOMBRES-COMPLEXES | Nombres complexes (forme algebrique, trigonometrique, exponentielle) |
| 12 | TSPE-ARITHMETIQUE | Arithmetique (divisibilite, congruences, PGCD) |

> Les matrices ne figurent pas au programme 2019 de Terminale specialite.
> Chapitre 13 supprime.

## Workflow

Meme pipeline que 1SPE : LOT 0 a LOT 7, memes gates (VERIFY, resolution
aveugle A+B, compilation, PNG, tag, CI verte).

## Prerequis

1. Texte BO 2019 depose dans `sources/BO2019_TSPE_specialite.pdf` : **fait**
2. Extraction texte et creation des `capacites_TSPE_*.json` : a faire
3. Validation humaine de la liste de chapitres : A_VALIDER_HUMAIN
