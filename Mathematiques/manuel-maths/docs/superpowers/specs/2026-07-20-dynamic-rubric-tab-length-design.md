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

Les 6 mm correspondent à 3 mm de respiration avant et après le texte. La
mesure est locale au rendu de l'en-tête ; aucun état global de rubrique n'est
introduit et le mécanisme de marks reste la source du libellé.

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

Le rectangle et le centre du nœud texte doivent dériver de la même longueur
calculée. Une duplication de calcul entre le fond et le texte serait considérée
comme un défaut, car elle pourrait recréer un décalage.

## Cas limites

Les rubriques sont un vocabulaire éditorial contrôlé. Aucun mécanisme de
réduction automatique de police, de césure ou de passage sur deux lignes n'est
ajouté. Un libellé plus long produit simplement un onglet plus long selon la
même formule. Cette règle privilégie la lisibilité et évite les catégories de
taille maintenues manuellement.

## Vérification et non-régression

La correction suit un cycle test-first.

1. Un contrat source exige une longueur mesurée, un minimum de 16 mm, un
   padding total de 6 mm et l'utilisation de la même dimension pour le rectangle
   et le centrage du texte.
2. Une fixture LaTeX réelle rend au moins un libellé court (`COURS`) et le
   libellé long (`AUTO-ÉVALUATION`) sur pages impaire et paire. Elle prouve que :
   - la longueur courte reste à 16 mm ;
   - la longueur longue est strictement supérieure ;
   - les deux côtés utilisent la même valeur pour un même libellé ;
   - aucun `Overfull` ou avertissement de géométrie n'est émis.
3. La maquette complète est recompilée en trois passes. Les pages 11 et 12 sont
   inspectées à 150 dpi et à pleine résolution : texte entièrement contenu,
   centrage, padding visible et symétrie recto-verso.
4. Les anciennes pages 11 et 12 sont conservées comme références historiques
   dans `validations/v5-it1/`. Les rendus corrigés sont figés dans
   `validations/v5-it2/`, puis comparés avec une métrique AE égale à zéro.
5. Les pages 1–10 et 13–15 restent protégées par leurs SHA-256 canoniques. La
   page 13 et son oracle itération 2 ne doivent pas changer.

## Livrables et garde-fous

- classe v5 corrigée ;
- tests unitaires, fixture PDF et contrôleur d'acceptation mis à jour ;
- PNG corrigés des pages 11 et 12 à 150 dpi ;
- PDF de maquette à 15 pages ;
- tableau AVANT/APRÈS mis à jour dans `MAQUETTE_V5_A_VALIDER.md` ;
- commit local au format `[CHARTE][V5.B-it2]` ;
- aucun push, merge ou déploiement avant le verdict humain
  `MAQUETTE V5 VALIDÉE`.
