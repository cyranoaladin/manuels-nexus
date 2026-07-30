# Décision humaine requise — baseline visuelle maquette V5

Statut : **NO-GO mise à jour des hashes sans approbation page par page**.

## Conclusion Codex

Les cinq tests rouges sont des contrôles fail-fast sur un oracle antérieur aux
onglets adaptatifs. Les huit divergences réelles sont confinées aux onglets des
pages 1, 7, 8, 9, 10, 11, 12 et 15. Le commit source `f071d37` calcule désormais
la longueur sur le libellé, ajoute 6 mm de marge avec un minimum de 16 mm, puis
recentre le texte. Les pages 11 et 12 montrent en particulier que le libellé
`AUTO-ÉVALUATION`, tronqué dans l'ancien onglet fixe, devient entièrement
lisible.

Les anciennes images correspondent octet pour octet au commit-oracle
`60d0460`; les nouvelles correspondent aux PNG suivis au HEAD. Une
rerastérisation fraîche du PDF courant avec Poppler 24.02.0 donne `AE=0` sur
les huit nouvelles images. L'extérieur de chaque bbox est identique pixel à
pixel. La cause de source est donc démontrée et une dérive uniquement liée à
l'environnement est écartée pour ce rendu.

Verdict Codex : les huit pages sont **techniquement approuvables comme
`expected_change`**, sans régression visuelle détectée dans le périmètre des
diffs. Cette proposition ne vaut pas décision humaine, mise à jour de baseline,
validation mathématique, merge ou release.

## Tableau de décision

| Page | Ancien hash | Nouveau hash | Cause | Diff attendu | Régression détectée | Verdict Codex | Décision humaine |
|---:|---|---|---|---|---|---|---|
| 1 | `1e065c44ee1cd031aad570b4f4c5a98aa7ced55bceba78f418ff3ba31d63a24d` | `a3a5ea8b94c92028fad069d3ac11708bbfb51c883efbc2b6a011e69ff0592fd2` | onglet `OUVERTURE` dimensionné et recentré par `f071d37` | oui, démontré | non | `expected_change` proposé | |
| 7 | `b3499d26ce3c43b206b1913bc3a3bc6960bd0827e131a4634d8807f4f7ecd233` | `0f091b2b8488f89de66884cc22b238450264791875568f8116e4e0bc65cf6280` | onglet `MÉTHODES` dimensionné et recentré par `f071d37` | oui, démontré | non | `expected_change` proposé | |
| 8 | `7dc9d309b149ce5717e1f7aeab803c45f282c6cb4a4973668ffb3d1d267764ac` | `13ff6daab5f2d5fbd999af3e3f433f7bc92f2fc89f2adfd39f72bdf368e2b70f` | onglet `MÉTHODES` dimensionné et recentré par `f071d37` | oui, démontré | non | `expected_change` proposé | |
| 9 | `fbe900adaa69d7374e0be7ead78dcc2295e03d35671281e4c7e0890d656e726e` | `ccda0af7007a15ecf3b895b5cb60a2f658bcee78e7a725acad4d6590f54135c3` | onglet `EXERCICES` dimensionné et recentré par `f071d37` | oui, démontré | non | `expected_change` proposé | |
| 10 | `50aec5774963497bdf290b68c571dfa3d13336ded825e5969a3aee66834497be` | `4466330daf59618c2ab25947e244e08da3fcca1f446516af378f8884778e52d1` | onglet `EXERCICES` dimensionné et recentré par `f071d37` | oui, démontré | non | `expected_change` proposé | |
| 11 | `91f971e7ae61251c03e023fcd680982667810e2639d0d5aec02a66140129684d` | `7f114a2b9d958da28ec7eb8d3a7b568ba7bd755cc872c9721ba388fc93e0f130` | allongement de `AUTO-ÉVALUATION`, auparavant tronqué | oui, démontré | non ; troncature corrigée | `expected_change` proposé | |
| 12 | `eeb87208366ce9f12da4cd478040ad417bcfea65d9b65c591cad477555832093` | `3517dc008fd517f5c9c3858c2e5ba7bd3ce39ac677d4522d1e524d3e20d9f44f` | allongement de `AUTO-ÉVALUATION`, auparavant tronqué | oui, démontré | non ; troncature corrigée | `expected_change` proposé | |
| 15 | `988b636d4f82ae6fcad93a4651cb43639744aa9094e1d31a4e190a36da1e91b4` | `11de1dad17368d27af7bf1ead77d3afad27188785806821bd01bdc5a1b1a9141` | onglet `CORRIGÉS` dimensionné et recentré par `f071d37` | oui, démontré | non | `expected_change` proposé | |

La colonne `Décision humaine` est intentionnellement vide.

## Métriques recomputées

| Page | Pixels modifiés | Pourcentage | Bbox `(x0,y0,x1,y1)` | Côté |
|---:|---:|---:|---|---|
| 1 | 1 711 | 0,078605 % | `(1169,157,1240,257)` | extérieur droit |
| 7 | 1 078 | 0,049524 % | `(1169,161,1240,249)` | extérieur droit |
| 8 | 1 141 | 0,052418 % | `(0,161,71,249)` | extérieur gauche |
| 9 | 1 229 | 0,056461 % | `(1169,160,1240,251)` | extérieur droit |
| 10 | 1 268 | 0,058253 % | `(0,161,71,251)` | extérieur gauche |
| 11 | 4 334 | 0,199107 % | `(1169,148,1240,293)` | extérieur droit |
| 12 | 4 367 | 0,200624 % | `(0,148,71,293)` | extérieur gauche |
| 15 | 740 | 0,033996 % | `(1169,163,1240,245)` | extérieur droit |

## Toolchain commun aux huit divergences

| Élément | Version observée |
|---|---|
| LuaHBTeX | `1.17.0` — TeX Live 2023/Debian |
| Poppler / `pdftoppm` | `24.02.0` |
| ImageMagick | `6.9.12-98 Q16` |
| Pillow | `12.3.0` |
| Rastérisation | `150 dpi`, `1241 × 1754` |

Les versions et SHA-256 individuels des dix fichiers TeX Gyre/AMS réellement
incorporés sont consignés dans le
[manifeste](visual-baseline-review/manifest.json), sous `font_environment`.

## Contrôle visuel adversarial

Dans le tableau suivant, « identique hors bbox » signifie identité pixel à
pixel entre `old.png` et `new.png`.

| Page | Texte coupé | Chevauchement | Débordement | Onglet | Marges / déplacement | Pagination | En-tête / pied | Couche textuelle | Artefact | Environnement seul |
|---:|---|---|---|---|---|---|---|---|---|---|
| 1 | aucun nouveau | aucun | aucun | `OUVERTURE` lisible, padding accru | identiques hors bbox | 15 pages, folio stable | identiques hors bbox | présente, 362 mots bbox | aucun | non, source + rerastérisation AE=0 |
| 7 | aucun | aucun | aucun | `MÉTHODES` lisible et centré | identiques hors bbox | folio 7 stable | identiques hors bbox | présente, 243 mots bbox | aucun | non, source + rerastérisation AE=0 |
| 8 | aucun | aucun | aucun | `MÉTHODES` lisible et centré, côté pair correct | identiques hors bbox | folio 8 stable | identiques hors bbox | présente, 143 mots bbox | aucun | non, source + rerastérisation AE=0 |
| 9 | aucun | aucun | aucun | `EXERCICES` lisible et centré | identiques hors bbox | folio 9 stable | identiques hors bbox | présente, 868 mots bbox | aucun | non, source + rerastérisation AE=0 |
| 10 | aucun | aucun | aucun | `EXERCICES` lisible et centré, côté pair correct | identiques hors bbox | folio 10 stable | identiques hors bbox | présente, 792 mots bbox | aucun | non, source + rerastérisation AE=0 |
| 11 | ancienne troncature du libellé supprimée ; aucun texte courant coupé | aucun | aucun | `AUTO-ÉVALUATION` entièrement lisible | identiques hors bbox | folio 11 stable | identiques hors bbox | présente, 466 mots bbox | aucun | non, source + rerastérisation AE=0 |
| 12 | ancienne troncature du libellé supprimée ; aucun texte courant coupé | aucun | aucun | `AUTO-ÉVALUATION` entièrement lisible, côté pair correct | identiques hors bbox | folio 12 stable | identiques hors bbox | présente, 329 mots bbox | aucun | non, source + rerastérisation AE=0 |
| 15 | aucun | aucun | aucun | `CORRIGÉS` lisible et centré | identiques hors bbox | folio 15 stable | identiques hors bbox | présente, 479 mots bbox | aucun | non, source + rerastérisation AE=0 |

Le PDF est A4, non chiffré, comporte 15 pages et toutes les polices sont
incorporées. `Tagged: no` et la police symbole MSAM7 sans mapping Unicode
restent des dettes PDF préexistantes ; elles ne sont pas causées par les
onglets et ne sont pas effacées par un verdict visuel.

## Dossier de comparaison

- [Planche complète haute résolution](visual-baseline-review/contact-sheet-full.png)
- [Zooms sur les zones modifiées](visual-baseline-review/contact-sheet-zooms.png)
- [Manifeste complet](visual-baseline-review/manifest.json)

## Détail et recommandation par page

### Page 1 — OUVERTURE

[Ancienne image](visual-baseline-review/pages/page-01/old.png) ·
[Nouvelle image](visual-baseline-review/pages/page-01/new.png) ·
[Diff](visual-baseline-review/pages/page-01/diff.png)

Le rectangle et le centrage du libellé changent uniquement dans la bande droite
`x=1169..1240`, sans toucher au sommaire, au titre, à l'en-tête ni au pied.
Recommandation : approuver `expected_change`. Conséquence : une mise à jour
future et explicite pourra remplacer l'oracle de cette page seulement.

### Page 7 — MÉTHODES

[Ancienne image](visual-baseline-review/pages/page-07/old.png) ·
[Nouvelle image](visual-baseline-review/pages/page-07/new.png) ·
[Diff](visual-baseline-review/pages/page-07/diff.png)

Le changement est limité au dimensionnement et au recentrage du libellé dans la
bande droite. Le bloc de méthode, les marges et le folio sont inchangés.
Recommandation : approuver `expected_change`. Conséquence : l'oracle futur
acceptera le calcul adaptatif pour cette page, sans valider son contenu.

### Page 8 — MÉTHODES

[Ancienne image](visual-baseline-review/pages/page-08/old.png) ·
[Nouvelle image](visual-baseline-review/pages/page-08/new.png) ·
[Diff](visual-baseline-review/pages/page-08/diff.png)

Le même changement apparaît dans la bande gauche, conformément à l'alternance
recto-verso. Aucun contenu métier n'est déplacé. Recommandation : approuver
`expected_change`. Conséquence : l'oracle futur acceptera ce rendu pair
uniquement.

### Page 9 — EXERCICES

[Ancienne image](visual-baseline-review/pages/page-09/old.png) ·
[Nouvelle image](visual-baseline-review/pages/page-09/new.png) ·
[Diff](visual-baseline-review/pages/page-09/diff.png)

La page dense reste identique hors du bord droit ; aucune colonne d'exercices
ne bouge et aucun texte ne passe sous l'onglet. Recommandation : approuver
`expected_change`. Conséquence : seul le nouveau padding de l'onglet sera
baseliné.

### Page 10 — EXERCICES

[Ancienne image](visual-baseline-review/pages/page-10/old.png) ·
[Nouvelle image](visual-baseline-review/pages/page-10/new.png) ·
[Diff](visual-baseline-review/pages/page-10/diff.png)

Le changement symétrique est limité à la bande gauche. Le contenu, l'en-tête,
le pied et le folio sont stables. Recommandation : approuver
`expected_change`. Conséquence : seul ce rendu pair pourra recevoir un nouveau
hash après commande humaine explicite.

### Page 11 — AUTO-ÉVALUATION

[Ancienne image](visual-baseline-review/pages/page-11/old.png) ·
[Nouvelle image](visual-baseline-review/pages/page-11/new.png) ·
[Diff](visual-baseline-review/pages/page-11/diff.png)

L'ancien onglet fixe tronque visiblement `AUTO-ÉVALUATION`. Le nouvel onglet
s'allonge jusqu'à `y=293` et rend le libellé complet, sans empiéter sur le QCM.
Recommandation : approuver `expected_change`. Conséquence : l'amélioration de
lisibilité deviendra la référence de non-régression de cette page.

### Page 12 — AUTO-ÉVALUATION

[Ancienne image](visual-baseline-review/pages/page-12/old.png) ·
[Nouvelle image](visual-baseline-review/pages/page-12/new.png) ·
[Diff](visual-baseline-review/pages/page-12/diff.png)

La correction de troncature est reproduite sur le bord gauche de la page paire.
Le contenu du QCM et la pagination restent inchangés. Recommandation : approuver
`expected_change`. Conséquence : l'amélioration symétrique deviendra la
référence de cette page seulement.

### Page 15 — CORRIGÉS

[Ancienne image](visual-baseline-review/pages/page-15/old.png) ·
[Nouvelle image](visual-baseline-review/pages/page-15/new.png) ·
[Diff](visual-baseline-review/pages/page-15/diff.png)

Seuls le padding inférieur et le recentrage du libellé changent dans la bande
droite. Les blocs de corrigés et le folio sont identiques hors bbox.
Recommandation : approuver `expected_change`. Conséquence : l'oracle futur
acceptera cette géométrie d'onglet sans approuver les corrigés eux-mêmes.

## Portée d'une approbation

Une décision humaine `expected_change` autoriserait seulement un lot ultérieur,
explicite et audité de mise à jour des huit hashes sélectionnés. Elle
n'autorise pas :

- la modification automatique de baseline ;
- un `accepted_exception` ;
- l'effacement des cinq tests rouges avant mise à jour contrôlée ;
- la fusion de la PR ;
- la validation mathématique ou réglementaire ;
- la release du manuel.
