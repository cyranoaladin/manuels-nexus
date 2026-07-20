# Dimensionnement automatique des onglets de rubrique — conception

**Date :** 2026-07-20
**Branche :** `charte/v5-b-it2`
**Statut :** validé par le responsable de projet

## Problème observé

Les onglets latéraux de la classe `gabarits/nexus-manuel-v5.cls` utilisent une
épaisseur fixe de 12 mm et une longueur fixe de 16 mm. Le texte est tourné à
90 degrés, mais la longueur du fond n'est pas liée à la largeur typographique du
libellé.

Sur les pages 11 et 12, `AUTO-ÉVALUATION` dépasse donc le rectangle coloré. La
fin du texte blanc se retrouve sur le fond blanc de la page et devient
partiellement invisible. Le même défaut peut réapparaître pour toute future
rubrique dont le nom dépasse la capacité du fond fixe.

## Objectif

Dimensionner automatiquement la longueur du fond coloré à partir du libellé
réel, sans réduire la police et sans modifier l'épaisseur, la couleur, la
position de départ ou la logique recto-verso de l'onglet.

La correction est générique : elle s'applique à tous les onglets. Les libellés
courts doivent néanmoins conserver le gabarit visuel actuel.

## Décision retenue

L'option validée est **A — longueur automatique**.

Pour chaque page, la classe mesure `\MakeUppercase{\nxRubriquePage}` avec
exactement la police utilisée dans l'onglet. La longueur est ensuite calculée
par la règle :

```text
longueur = max(16 mm, largeur_typographique(libellé) + 6 mm)
```

Les 6 mm correspondent à un minimum de 3 mm de respiration avant et après le
texte dans la branche auto-dimensionnée. Lorsqu'un libellé court reste soumis au
minimum de 16 mm, le surplus est réparti également par le centrage. La mesure
est locale au rendu de l'en-tête ; aucun état global de rubrique n'est introduit
et le mécanisme de marks reste la source du libellé.

## Géométrie et rendu

- épaisseur extérieure : 12 mm, inchangée ;
- longueur minimale : 16 mm, afin de préserver les onglets courts ;
- padding longitudinal : 3 mm à chaque extrémité ;
- police : `\titrefont\fontsize{6}{6}\selectfont`, inchangée ;
- texte : centré sur la longueur calculée ;
- ancrage supérieur : inchangé ;
- page impaire : fond vers la gauche depuis `current page.north east`, rotation
  `90` degrés ;
- page paire : miroir depuis `current page.north west`, rotation `-90` degrés.

Dans un groupe local, le libellé uppercase est composé et mesuré une seule fois,
après sélection de `\titrefont\fontsize{6}{6}\selectfont`. Une unique longueur
résultante pilote à la fois l'extension verticale du rectangle et son
demi-décalage pour le centre du nœud, dont `inner sep` reste nul. Une duplication
de calcul entre le fond et le texte serait considérée comme un défaut, car elle
pourrait recréer un décalage.

## Cas limites

Les rubriques sont un vocabulaire éditorial contrôlé. Aucun mécanisme de
réduction automatique de police, de césure ou de passage sur deux lignes n'est
ajouté. Un libellé plus long produit simplement un onglet plus long selon la
même formule. Cette règle privilégie la lisibilité et évite les catégories de
taille maintenues manuellement.

## Vérification et non-régression

La correction suit un cycle test-first.

1. Un contrat source exige une composition/mesure unique, un minimum de 16 mm,
   un padding total de 6 mm et l'utilisation de la même dimension pour le
   rectangle et le centrage du texte.
2. Une fixture LaTeX réelle rend au moins un libellé court (`COURS`) et le
   libellé long (`AUTO-ÉVALUATION`) sur pages impaire et paire. Elle prouve que :
   - la longueur courte reste à 16 mm ;
   - la longueur longue est strictement supérieure ;
   - les deux côtés utilisent la même valeur pour un même libellé ;
   - aucun `Overfull` ou avertissement de géométrie n'est émis.
   La preuve de contenance ne repose pas sur le log : TikZ en `overlay` peut
   dépasser sans `Overfull`. Le test combine la boîte du mot tournée issue de
   `pdftotext -bbox-layout` et la composante colorée de l'onglet détectée dans un
   raster à 300 dpi. Après conversion points/pixels, il exige sur les deux
   parités que la boîte du texte soit entièrement incluse dans le rectangle,
   que la branche auto-dimensionnée conserve au moins 3 mm à chaque extrémité
   (avec une tolérance de rasterisation d'au plus 0,5 pt) et que l'écart entre
   les deux respirations ne dépasse pas 0,5 mm. Pour la branche minimale de
   16 mm, il exige l'inclusion et un surplus réparti symétriquement.
3. La maquette complète est recompilée en trois passes. Les pages 11 et 12 sont
   inspectées à 150 dpi et à pleine résolution : texte entièrement contenu,
   centrage, padding visible et symétrie recto-verso.
4. Avant recompilation, les rendus actuels `validations/v5/page-11.png` et
   `page-12.png` sont copiés dans `validations/v5-it1/` et leurs SHA-256
   historiques sont figés. Après inspection, les nouveaux rendus remplacent
   `validations/v5/page-11.png` et `page-12.png` et sont copiés dans
   `validations/v5-it2/`. Le contrôleur vérifie le SHA des deux oracles itération
   2 puis exige `AE=0` entre chacun d'eux et le PNG généré.
5. Seules les entrées 11 et 12 de `NON_DIAGNOSTICS_PAGE_SHA256` sont remplacées
   par leurs nouvelles valeurs. Les pages 1–10 et 14–15 conservent leurs
   SHA-256 canoniques ; la page 13 reste régie par son oracle dédié.
6. La source QCM
   `chapitres/1SPE-DERIVATION-LOCAL/qcm/1SPE-DERIVATION-LOCAL-QCM.tex` est
   strictement interdite de modification et conserve le SHA-256 canonique
   `cb34cb2351761e1c60d15eb5b95bcbc656c718fb19b6dca15290e3df3384b9e3`.
   Les bornes BBox et intervalles de log sans débordement des diagnostics p.13
   restent actifs ; son oracle itération 2 conserve le SHA-256
   `2edeb64a24a83e38a88a0aefab83e54452eec3c9270cbeee3dc3afefb201af23`.

## Livrables et garde-fous

- classe v5 corrigée ;
- tests unitaires, fixture PDF et contrôleur d'acceptation mis à jour ;
- PNG corrigés des pages 11 et 12 à 150 dpi ;
- PDF de maquette à 15 pages ;
- tableau AVANT/APRÈS mis à jour dans `MAQUETTE_V5_A_VALIDER.md` ;
- commit local au format `[CHARTE][V5.B-it2]` ;
- aucun push, merge ou déploiement avant le verdict humain
  `MAQUETTE V5 VALIDÉE`.
