# Autorité programme officiel — édition 2026-2027

Vérifié le 2026-08-22, indépendamment du registre opérationnel préexistant
`docs/programmes/PROGRAMMES_2026_2027.yaml` (généré le 2026-08-11).
Sources exclusives : Bulletin officiel (education.gouv.fr), Légifrance
(JORF), Éduscol. Détail complet et URLs dans
`audit/OFFICIAL_PROGRAM_AUTHORITY_2026_2027.yaml`.

## Synthèse

| Manuel | Programme applicable 2026-2027 | Texte | BO | Entrée en vigueur | Changement 2026-2027 ? |
|---|---|---|---|---|---|
| **1SPE** | Nouveau (2026) | MENE2602917A | n°14 du 02-04-2026 | rentrée 2026-2027 | **OUI** — seul manuel concerné |
| **TSPE** | 2019, inchangé | MENE1921246A | spécial 8 du 25-07-2019 | rentrée 2020 | NON (nouveau texte MENE2602919A différé à 2027-2028) |
| **TCOMPL** | 2019, inchangé | MENE1921265A | spécial 8 du 25-07-2019 | rentrée 2020 | NON (nouveau texte MENE2902920A différé à 2027-2028) |
| **TEXPERTES** | 2019, inchangé | MENE1921264A | spécial 8 du 25-07-2019 | rentrée 2020 | NON — aucun nouveau texte trouvé |
| **1NSI** | 2019, inchangé | MENE1901633A | spécial 1 du 22-01-2019 | rentrée 2019 | NON — aucun nouveau texte trouvé |
| **TNSI** | 2019, inchangé | MENE1921247A | spécial 8 du 25-07-2019 | rentrée 2020 | NON pour le programme. **Épreuve** modifiée (voir ci-dessous) |

**Conclusion centrale du mandat confirmée par sources primaires** : seul
1SPE change de programme pour l'édition 2026-2027. Les cinq autres manuels
restent sur leur programme 2019, les nouveaux textes 2026 pour
Terminale/mathématiques complémentaires n'entrant en application qu'à la
rentrée **2027-2028** (vérifié texte à l'appui — article 2 des arrêtés
MENE2602919A et MENE2902920A sur Légifrance, formulation identique).

## Trouvaille nouvelle : modalités d'épreuve TNSI 2026

Une note de service (**MENE2516123N**, BO n°31 du 21 août 2025) modifie la
pondération de l'épreuve de spécialité NSI Terminale **à compter de la
session 2026** :

- écrit : 3h30, 3 exercices indépendants, **15/20** (était 12/20) ;
- pratique : 1h, **5/20** (était 8/20) ;
- remplace la note de service n°2020-30 du 11 février 2020.

Ce point comble une lacune explicitement signalée dans le registre
opérationnel (`docs/programmes/PROGRAMMES_2026_2027.yaml`, entrée
`EXAM-BAC-NSI-2026`, marquée `declare_par_instruction_humaine` /
`source_deposee: false`). **Non encore déposé/empreinté** localement (page
BO en 403 direct, PDF miroir académique trop volumineux pour cette passe) —
à faire dans un lot de dépôt de source dédié avant de le citer comme preuve
vérifiée dans le pipeline.

## Correction apportée

Le NOR du futur programme TCOMPL 2026 (hors périmètre 2026-2027) a été
corrigé de `MENE2602920A` (apparu dans une recherche préparatoire) à
**`MENE2902920A`**, confirmé par l'URL réellement servie par
education.gouv.fr.

## Point non confirmé, signalé explicitement

Le format exact de l'épreuve écrite de spécialité mathématiques Terminale
pour la session 2027 (nombre d'exercices) n'a été trouvé que sur des
sources secondaires (digischool.fr, annabac.com) lors de cette
vérification — aucune confirmation education.gouv.fr/Éduscol directe. Ne
pas le présenter comme vérifié tant qu'une source primaire n'est pas
déposée.

## Cohérence avec le registre opérationnel

Aucune contradiction trouvée entre cette vérification et
`docs/programmes/PROGRAMMES_2026_2027.yaml` sur les points qu'il couvre
déjà (arrêtés, BO, dates, statut). Ce fichier d'audit ajoute la couche de
vérification indépendante et les deux points ci-dessus ; il ne remplace pas
le registre opérationnel, qui reste la source consommée par le pipeline
d'inventaire.

## Prochaine étape

Construire la matrice programme ↔ manuel exhaustive (capacité par
capacité, statut de couverture FULL/PARTIAL/MISSING/OUT_OF_SCOPE) pour
chacun des six manuels. Un travail préparatoire existe déjà pour 1SPE :
`Mathematiques/manuel-maths/referentiel/CONFORMITE_BO2026.md` (audit
chapitre par chapitre contre le BO 2026, validation humaine finale encore
requise) et les fichiers `referentiel/capacites_1SPE_*.json`.
