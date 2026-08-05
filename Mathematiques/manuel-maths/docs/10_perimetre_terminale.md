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

## Architecture (10 chapitres, programme 2019) — CORRIGE 2026-08-05

**Correction (2026-08-05)** : les anciens chapitres 11 (Nombres complexes) et 12
(Arithmetique) ont ete retires de ce perimetre apres verification textuelle de
`sources/txt/BO2019_TSPE_specialite.txt` (grep exhaustif : aucune occurrence de
"complexe" au sens nombre complexe, ni de "arithmetique/PGCD/Bezout/congruence").
Ces deux notions **ne figurent pas** au programme de la specialite mathematiques
de terminale (2019) : elles appartiennent exclusivement au programme optionnel
**Mathematiques expertes** (voir `11_perimetre_terminale_complementaires.md` et
`12_perimetre_terminale_expertes.md`). L'ancienne liste a 12 chapitres etait donc
non conforme au programme (R1/R7) ; elle n'a jamais ete signalee car aucun de ces
deux chapitres n'avait encore ete redige.

Le theme "Fonctions sinus et cosinus" (derivees, variations, courbes, ancien
chapitre implicite) est en revanche bien present dans le texte BO 2019 TSPE
(section "Fonctions sinus et cosinus", cf. lignes 640-651 de l'extrait) : il est
conserve sous le chapitre 5 ci-dessous (`capacites_TSPE_TRIGONOMETRIE.json` deja
extrait). La note "sin/cos retires si confirme" en tete de ce document concerne
uniquement le backlog **TSPE v2 / rentree 2027-2028** (programme 2026), pas le
programme 2019 actuellement en vigueur.

| # | Chapitre | Theme BO 2019 | Referentiel |
|---|---|---|---|
| 1 | TSPE-SUITES-LIMITES | Suites : limites, theoremes de convergence | `capacites_TSPE_SUITES_LIMITES.json` |
| 2 | TSPE-LIMITES-FONCTIONS | Fonctions : limites, comparaison, asymptotes | `capacites_TSPE_LIMITES_FONCTIONS.json` |
| 3 | TSPE-CONTINUITE | Continuite, TVI | `capacites_TSPE_CONTINUITE.json` |
| 4 | TSPE-DERIVATION-CONVEXITE | Complements de derivation (convexite, points d'inflexion) | `capacites_TSPE_DERIVATION_CONVEXITE.json` |
| 5 | TSPE-TRIGONOMETRIE | Fonctions sinus et cosinus : derivees, variations, courbes | `capacites_TSPE_TRIGONOMETRIE.json` |
| 6 | TSPE-LOGARITHME | Fonction logarithme neperien | `capacites_TSPE_LOGARITHME.json` |
| 7 | TSPE-PRIMITIVES-EQDIFF | Primitives, equations differentielles y'=ay, y'=ay+b | `capacites_TSPE_PRIMITIVES_EQDIFF.json` |
| 8 | TSPE-CALCUL-INTEGRAL | Calcul integral | `capacites_TSPE_CALCUL_INTEGRAL.json` |
| 9 | TSPE-COMBINATOIRE | Denombrement, coefficients binomiaux | `capacites_TSPE_COMBINATOIRE.json` |
| 10 | TSPE-PROBABILITES | Succession d'epreuves, echantillonnage | `capacites_TSPE_PROBABILITES.json` |
| 10bis | TSPE-CONCENTRATION-LGN | Inegalite de concentration, loi des grands nombres (sous-partie de Probabilites, BO) | `capacites_TSPE_CONCENTRATION_LGN.json` |
| 11 | TSPE-GEOMETRIE-ESPACE | Geometrie dans l'espace (droites, plans, orthogonalite) | `capacites_TSPE_GEOMETRIE_ESPACE.json` |

> Les matrices ne figurent pas au programme 2019 de Terminale specialite (elles
> sont en Maths expertes). Nombres complexes et arithmetique : idem, voir
> Maths expertes. Point ouvert A_VALIDER_HUMAIN : fusionner TSPE-CONCENTRATION-LGN
> dans TSPE-PROBABILITES (1 chapitre) ou le garder distinct (2 chapitres) — a
> trancher au LOT 0 de ce chapitre.

**Etat des chapitres deja amorces** (avant validation du perimetre corrige) :
`TSPE-SUITES-LIMITES`, `TSPE-LIMITES-FONCTIONS`, `TSPE-DERIVATION-CONVEXITE`
ont des dossiers avec LOT-0 a LOT-7 (variable) mais **ne sont brances dans aucun
assembleur de manuel** (cf. audit `finalisation-collection-v1`/`audit/AUDIT_CONSOLIDE.md`).
A auditer avant reprise (contenu peut-etre non conforme a ce perimetre corrige).

## Workflow

Meme pipeline que 1SPE : LOT 0 a LOT 7, memes gates (VERIFY, resolution
aveugle A+B, compilation, PNG, tag, CI verte).

## Prerequis

1. Texte BO 2019 depose dans `sources/BO2019_TSPE_specialite.pdf` : **fait**
2. Extraction texte et creation des `capacites_TSPE_*.json` : a faire
3. Validation humaine de la liste de chapitres : A_VALIDER_HUMAIN
