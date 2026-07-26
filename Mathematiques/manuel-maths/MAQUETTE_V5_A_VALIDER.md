# Maquette éditoriale v5 — itération 2 à valider

## Statut

Itération 2 produite sur les mêmes contenus de `1SPE-DERIVATION-LOCAL`, sans
réécriture des objets source et sans modification de la production v4.1/TSPE.
La maquette compte 15 pages et reste strictement locale : aucun push ni
déploiement v5 n'est autorisé avant le verdict humain.

Date de clôture technique de l’itération : 26 juillet 2026.

## Livrables

- Classe isolée : `gabarits/nexus-manuel-v5.cls`
- Assemblage : `build/maquette-v5/maquette.tex`
- Manifeste META : `build/maquette-v5/manifest.json`
- PDF local non versionné : `build/maquette-v5/maquette.pdf`
- PNG 150 dpi : `validations/v5/page-01.png` à `page-15.png`
- Références immuables itération 1 : pages 1, 7–13 et 15 dans
  `validations/v5-it1/`
- Références corrigées itération 2 : pages 1, 7–13 et 15 dans
  `validations/v5-it2/`
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
| 8 | Onglets mesurés p.1,7–12,15 | Fond fixe 16 mm : `AUTO-ÉVALUATION` dépassait ; un seuil parasite à 20 mm rabattait aussi les libellés intermédiaires à 16 mm et supprimait leur padding réglementaire. | Mesure en 6 pt et longueur exacte `max(16 mm, largeur + 6 mm)` ; une composition unique du libellé et une voie de rendu commune réutilisent la boîte mesurée, la longueur et sa demi-longueur sur les deux parités. Épaisseur 12 mm, centrage identique et au moins 3 mm de padding à chaque extrémité dès que la mesure dépasse 16 mm. | Fixture six pages à 300 dpi : `COURS`, `OUVERTURE`, `AUTO-ÉVALUATION`; valeur intermédiaire strictement entre 16 et 20 mm et égale à `largeur + 6 mm` à ±0,5 pt ; texte inclus, asymétrie ≤0,5 mm, padding ≥3 mm −0,5 pt et parités à ±0,5 pt. Inspection `view_image` en détail original et crops 100 % des huit pages. Couples it1/it2 figés ci-dessous et `AE = 0` indépendant. | CORRIGÉ |
| 9 | Diagnostics QCM p.13 | Le tableau quatre colonnes était composé dans une demi-page : débordements de 314.99474 pt et 54.94688 pt, superpositions avec les réponses et le score. | Page pleine largeur hors `multicols`, typographie locale 6,6/7,6 pt, tableau puis réponses puis score sans collision. | Bornes et marges contrôlées par `pdftotext -bbox-layout` ; trois intervalles de log sans `Overfull`; référence it2 SHA-256 `2edeb64a24a83e38a88a0aefab83e54452eec3c9270cbeee3dc3afefb201af23`, `compare -metric AE = 0`. | CORRIGÉ |
| 10 | Corrigés finaux | En-tête/onglet `COURS`, titre doublé et numéros de badges désynchronisés. | Mark et onglet `CORRIGÉS`, un seul titre de contenu, cinq badges neutres et style math étroit dans la grille trois colonnes. | Extraction p.15, aucun ID technique et zéro `Overfull \hbox` dans le bloc. | CORRIGÉ |

La référence de l'itération 1 reste conservée comme preuve du défaut initial,
avec le SHA-256
`ea1750a0f56ecd3b2761614709f96f9b267569ece45bc4103aa11dc2007dacf1` ;
elle n'est plus utilisée comme oracle d'acceptation.
Les références historiques des onglets p.11–12 restent également immuables :
`91f971e7ae61251c03e023fcd680982667810e2639d0d5aec02a66140129684d`
et
`eeb87208366ce9f12da4cd478040ad417bcfea65d9b65c591cad477555832093`.

### Références immuables des onglets

| Page | Rubrique | SHA-256 it1 | SHA-256 it2 |
|---:|---|---|---|
| 1 | OUVERTURE | `1e065c44ee1cd031aad570b4f4c5a98aa7ced55bceba78f418ff3ba31d63a24d` | `a3a5ea8b94c92028fad069d3ac11708bbfb51c883efbc2b6a011e69ff0592fd2` |
| 7 | MÉTHODES | `b3499d26ce3c43b206b1913bc3a3bc6960bd0827e131a4634d8807f4f7ecd233` | `0f091b2b8488f89de66884cc22b238450264791875568f8116e4e0bc65cf6280` |
| 8 | MÉTHODES | `7dc9d309b149ce5717e1f7aeab803c45f282c6cb4a4973668ffb3d1d267764ac` | `13ff6daab5f2d5fbd999af3e3f433f7bc92f2fc89f2adfd39f72bdf368e2b70f` |
| 9 | EXERCICES | `fbe900adaa69d7374e0be7ead78dcc2295e03d35671281e4c7e0890d656e726e` | `ccda0af7007a15ecf3b895b5cb60a2f658bcee78e7a725acad4d6590f54135c3` |
| 10 | EXERCICES | `50aec5774963497bdf290b68c571dfa3d13336ded825e5969a3aee66834497be` | `4466330daf59618c2ab25947e244e08da3fcca1f446516af378f8884778e52d1` |
| 11 | AUTO-ÉVALUATION | `91f971e7ae61251c03e023fcd680982667810e2639d0d5aec02a66140129684d` | `7f114a2b9d958da28ec7eb8d3a7b568ba7bd755cc872c9721ba388fc93e0f130` |
| 12 | AUTO-ÉVALUATION | `eeb87208366ce9f12da4cd478040ad417bcfea65d9b65c591cad477555832093` | `3517dc008fd517f5c9c3858c2e5ba7bd3ce39ac677d4522d1e524d3e20d9f44f` |
| 15 | CORRIGÉS | `988b636d4f82ae6fcad93a4651cb43639744aa9094e1d31a4e190a36da1e91b4` | `11de1dad17368d27af7bf1ead77d3afad27188785806821bd01bdc5a1b1a9141` |

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
Il vérifie aussi les huit couples de SHA historiques et it2 des onglets, puis
compare indépendamment chaque page courante à son oracle (`AE = 0`). Les modes
synthétiques désignent individuellement p.1,7–12,15, en plus de p.13. Un oracle
remplacé sans modification explicite de sa constante est donc rejeté.

## Verdict attendu

Relire les pages 1 à 15, avec attention particulière aux onglets p.1,7–13,15
et aux contenus p.2–5. Le seul message qui lève la pause est :
`MAQUETTE V5 VALIDÉE`.

**PAUSE BLOQUANTE — EN ATTENTE DE « MAQUETTE V5 VALIDÉE »**
