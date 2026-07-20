# Maquette éditoriale v5 — itération 2 à valider

## Statut

Itération 2 produite sur les mêmes contenus de `1SPE-DERIVATION-LOCAL`, sans
réécriture des objets source et sans modification de la production v4.1/TSPE.
La maquette compte 15 pages et reste strictement locale : aucun push ni
déploiement v5 n'est autorisé avant le verdict humain.

Date : 19 juillet 2026.

## Livrables

- Classe isolée : `gabarits/nexus-manuel-v5.cls`
- Assemblage : `build/maquette-v5/maquette.tex`
- Manifeste META : `build/maquette-v5/manifest.json`
- PDF local non versionné : `build/maquette-v5/maquette.pdf`
- PNG 150 dpi : `validations/v5/page-01.png` à `page-15.png`
- Référence immuable itération 1 : `validations/v5-it1/page-13.png`
- Référence corrigée itération 2 : `validations/v5-it2/page-13.png`
- Générateur : `scripts/build_maquette_v5.py`
- Contrôleur : `scripts/check_maquette_v5.py`
- Régressions : `tests/test_maquette_v5.py`

## Tableau AVANT/APRÈS

| # | Défaut | AVANT — itération 1 | APRÈS — itération 2 | Preuve | Statut |
|---|---|---|---|---|---|
| 1 | Ouverture v5 | Ouverture v4.1, sans bandeau, sommaire à neuf temps ni onglet. | Bandeau et décor v5, onglet `OUVERTURE`, neuf temps avec folios. | Extraction p.1 contrôlée entrée par entrée. | CORRIGÉ |
| 2 | Cours et marge active | Notes écrasées sans filet, trois alertes empilées, approfondissement orphelin. | Deux vocabulaires et un renvoi sur grille 4,5 pt, filet 0,4 pt, au plus deux alertes par page et réservation du bloc d'approfondissement. | Fixture réelle p.2–5 et contrôle de pagination. | CORRIGÉ |
| 3 | Pages blanches | Losanges composés comme caractères dans le flux. | Décor TikZ `overlay` ancré sur `current page`, opacité 0,04 ; boîte texte sans glyphe. | `pdftotext` p.6 et p.14 vide. | CORRIGÉ |
| 4 | Double méthode | Mauvais onglet, annotations superposées, aucun appariement ni call-out. | Marks de page corrects ; M1 résolue p.7, applications 1, 2 et 7 p.8 ; appels ①②③ et légendes regroupées ; fallback documenté pour 0/1 application. | Fixtures 0/1/2/3 applications et absence de glyphe manquant. | CORRIGÉ |
| 5 | Renvois | Placeholders `S'entraîner`, aucun lien Méthode/Corrigé. | Renvois générés depuis les META : `S'entraîner : ex. 1, 2, 7 p. 9` et `→ M1 · Corrigé p. 15`. | Chaînes exactes exigées dans le PDF après trois passes LuaLaTeX. | CORRIGÉ |
| 6 | Badges exercices | IDs bruts visibles, difficulté et pictogrammes absents. | IDs réservés aux META/labels ; difficulté à trois losanges plein/contour ; pictos Python et calculatrice ; 11 badges p.9 et 9 p.10 avec filet central. | Extraction des 20 badges, rejet des 20 IDs et test raster des filets. | CORRIGÉ |
| 7 | QCM étroit | Fractions disloquées et items susceptibles d'être coupés. | `\tfrac` local, chaque question principale boxée, répartition complète Q1–Q8 p.11 / Q9–Q15 p.12. | Extraction question par question ; Q12 et ses quatre réponses restent dans la même colonne. | CORRIGÉ |
| 8 | Diagnostics QCM p.13 | Le tableau quatre colonnes était composé dans une demi-page : débordements de 314.99474 pt et 54.94688 pt, superpositions avec les réponses et le score. | Page pleine largeur hors `multicols`, typographie locale 6,6/7,6 pt, tableau puis réponses puis score sans collision. | Bornes et marges contrôlées par `pdftotext -bbox-layout` ; trois intervalles de log sans `Overfull`; référence it2 SHA-256 `2edeb64a24a83e38a88a0aefab83e54452eec3c9270cbeee3dc3afefb201af23`, `compare -metric AE = 0`. | CORRIGÉ |
| 9 | Corrigés finaux | En-tête/onglet `COURS`, titre doublé et numéros de badges désynchronisés. | Mark et onglet `CORRIGÉS`, un seul titre de contenu, cinq badges neutres et style math étroit dans la grille trois colonnes. | Extraction p.15, aucun ID technique et zéro `Overfull \hbox` dans le bloc. | CORRIGÉ |

La référence de l'itération 1 reste conservée comme preuve du défaut initial,
avec le SHA-256
`ea1750a0f56ecd3b2761614709f96f9b267569ece45bc4103aa11dc2007dacf1` ;
elle n'est plus utilisée comme oracle d'acceptation.

## Contrôle automatique

Commande publique :

```bash
python3 scripts/check_maquette_v5.py --manifest build/maquette-v5/manifest.json
```

Résultat attendu et obtenu :

```text
MAQUETTE V5: PASS — 15 pages; blanches 6,14; renvois 2/2; marginnote colonnes 0
```

Le contrôleur génère la table de renvois, compile exactement trois fois,
contrôle les 15 pages, les marks, le sommaire, les pages blanches, les chaînes
META, l'absence d'IDs et de `\marginnote` émis en colonnes, les débordements
des corrigés compacts, les bornes, marges et collisions de la page 13, ainsi que
le hash de la référence it2, puis régénère exactement les 15 PNG en 150 dpi.

## Verdict attendu

Relire les pages 1 à 15, avec attention particulière aux p.2–5, p.7–13 et
p.15. Le seul message qui lève la pause est :
`MAQUETTE V5 VALIDÉE`.

**PAUSE BLOQUANTE — EN ATTENTE DE « MAQUETTE V5 VALIDÉE »**
