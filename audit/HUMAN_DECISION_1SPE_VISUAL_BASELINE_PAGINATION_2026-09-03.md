# Décision humaine — baseline visuelle de pagination 1SPE {#decision-1spe-visual-baseline-pagination-2026-09-03}

`decision_id` : `decision-1spe-visual-baseline-pagination-2026-09-03`
`decision_date` : 2026-09-03
`decision` : **`RATIFY_VISUAL_BASELINE_CHANGE`**

## Décision

Chaque ouverture de chapitre 1SPE doit commencer sur une **page propre**. La
correction en place, qui coupe la page en tête de `\ouverturechapitre` par un
`\clearpage`, est **approuvée**. Elle ne doit pas être révertée.

`\cleardoublepage` est **refusé** en l'absence d'un contrat distinct et
explicite : aucune source n'exige un départ systématique en page impaire, et
cette obligation ne sera pas inventée ici.

## Motif

Le sommaire et les signets annonçaient une page qui n'était pas l'ouverture du
chapitre. `\addcontentsline` s'exécutait alors que TeX composait encore la
dernière page du chapitre précédent ; la coupure, émise ensuite par
l'assembleur, arrivait trop tard. L'entrée enregistrait donc la page d'avant.

Un sommaire qui ment est un défaut de publication. La correction est conservée.

## Diff avant / après

| Mesure | Avant | Après |
|---|---:|---:|
| Pages élève | 359 | 363 |
| Pages professeur | 633 | 635 |
| Folios de chapitre faux — élève | 3 | 0 |
| Folios de chapitre faux — professeur | 6 | 0 |

L'ancienne baseline `359 / 633` est **`SUPERSEDED_BY_EDITORIAL_PAGINATION_FIX`**.

Commit de la correction : `ab8d84e9c3047d6ed1e02fe78b6b9e3f3ea51fee`.

## Ce que cette décision N'EST PAS

| Portée | État |
|---|---|
| `CONTENT_APPROVAL` | **false** |
| `D7_APPROVAL` | **false** |
| `PUBLICATION_APPROVAL` | **false** |
| `HUMAN_CHAPTER_REVIEW` | **false** |
| `FINAL_CONTENT_SHA` | **false** |
| `PRINT_READY` | **false** |
| ISBN autorisé | **false** |

Elle autorise uniquement le changement éditorial de pagination qui corrige les
folios et les frontières de chapitre.

## Les compteurs de pages ne sont pas épinglés

`363` et `635` sont les compteurs de la **candidate courante**. Ils peuvent
encore évoluer sous l'effet de corrections release-critical — barèmes, rendu,
sommaire, correctifs D7. Ils ne deviennent pas une norme. Le compte définitif
sera capturé sur les PDF finals, et sur eux seuls.

## Classe de changement autorisée

Le seul changement autorisé est `EXPECTED_PAGE_BOUNDARY_CHANGE`, avec ses
effets de bord nommés : propagation des folios, déplacement de l'onglet de
rubrique avec sa page, mise à jour des folios du sommaire.

Sont interdits, et vérifiés comme tels par le producteur :
`MISSING_CONTENT`, `DUPLICATED_CONTENT`, `UNEXPECTED_REORDERING`.

## Vérification

Cette décision est un **docket** : elle ne mesure rien elle-même. Le
producteur `scripts/build_1spe_pagination_baseline_ratification.py` confronte
chaque valeur déclarée ci-dessus à des preuves calculées sur les deux PDF
courants et sur les deux PDF d'avant la correction, relus dans l'historique
Git au parent du commit de correction. Le résultat vit dans
`audit/1SPE_PAGINATION_BASELINE_RATIFICATION.json` et son compagnon Markdown.

Une valeur déclarée fausse fait échouer le producteur : la ratification ne peut
pas s'auto-confirmer.
