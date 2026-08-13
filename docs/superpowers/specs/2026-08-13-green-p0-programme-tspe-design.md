# Green P0 — Provenance officielle TSPE

## Statut

- Date : 13 août 2026.
- Base contractuelle : jalon Red `c50e455e` et tests
  `tests/test_programme_registry.py`.
- Branche prévue : `green/p0-programme-tspe`.
- Lane : conformité programme.
- Décision humaine : correction Green séparée approuvée.

## Objectif

Faire de `MENE1921246A` l'unique NOR actif attribué au programme de spécialité
mathématiques de Terminale applicable à l'édition 2026-2027. Éliminer les
attributions TSPE de `MENE1921262A` (Terminale STMG) et `MENE1921247A` (NSI
Terminale) sans réécrire les audits datés.

## Autorité et preuves

La référence officielle retenue est :

- intitulé : programme de spécialité de mathématiques de Terminale générale ;
- NOR : `MENE1921246A` ;
- BO : spécial n° 8 du 25 juillet 2019 ;
- URL officielle :
  `https://www.education.gouv.fr/bo/19/Special8/MENE1921246A.htm` ;
- application : rentrée 2020, encore applicable à l'édition 2026-2027 ;
- annexe PDF locale externe au checkout, déposée sur la machine de travail le
  18 juillet 2026 mais ignorée par Git : SHA-256
  `eb8369e7c1611e90f51491fecc5a7c2081a9c57f9c7fbb08d0414677b56ce16f` ;
- extraction texte versionnée et seule preuve matérielle reproductible depuis
  un clone : SHA-256
  `65eb5a55df14a2b3025a96db72fbcb1d917b55e8da7feb13669e28b903712210` ;
- preuve d'audit : `audit/AUDIT_ETAT_PROJET_2026-08-13.md`, lignes 87 à 101.

Le serveur officiel a répondu HTTP 403 lors du contrôle automatisé du
13 août 2026. Ce défaut d'accès ne remplace ni l'URL officielle déjà auditée,
ni l'extrait suivi et empreinté. L'annexe PDF locale est une preuve externe
complémentaire, pas une dépendance du test ou de la définition de terminé. Le
lot ne télécharge pas une copie depuis une source secondaire.

## État actuel reproduit

Les contradictions actives sont :

- `docs/programmes/PROGRAMMES_2026_2027.yaml` : `MENE1921262A` ;
- `Mathematiques/manuel-maths/sources/SOURCES.md` : `MENE1921262A` ;
- `ROADMAP_TERMINALE.md` : `MENE1921262A` ;
- `Mathematiques/manuel-maths/docs/10_perimetre_terminale.md` :
  `MENE1921247A` ;
- commentaire TSPE de
  `Mathematiques/manuel-maths/scripts/assemble_manuel.py` :
  `MENE1921247A`.

Le README racine décrit correctement la référence officielle mais affirme
encore que le registre local est erroné. Cette affirmation devient fausse dès
le Green du registre : le lot réglementaire doit donc actualiser les deux
passages concernés sans toucher aux autres P0.

## Périmètre de production

Le lot peut modifier uniquement :

- `docs/programmes/PROGRAMMES_2026_2027.yaml` ;
- `Mathematiques/manuel-maths/sources/SOURCES.md` ;
- `Mathematiques/manuel-maths/docs/10_perimetre_terminale.md` ;
- `ROADMAP_TERMINALE.md` ;
- les passages réglementaires obsolètes de `README.md` ;
- le commentaire réglementaire TSPE de
  `Mathematiques/manuel-maths/scripts/assemble_manuel.py` ;
- les tests réglementaires dédiés.

Il ne modifie pas :

- les extraits officiels ou leurs empreintes ;
- les contrats de capacités ;
- les chapitres ;
- les PDF ;
- les audits datés ;
- le manifeste observé ;
- la baseline.

## Contrat TDD

Les deux tests Red existants doivent devenir verts :

1. la source `SRC-BO2019-TSPE` porte `MENE1921246A`, et le manuel
   `TSPE_2026_2027` la référence de manière unique ;
2. la ligne `BO2019_TSPE_specialite.pdf` de `SOURCES.md` porte le même NOR.

Avant le correctif, un test Red structurel supplémentaire verrouille les trois
documents actifs, le README et le commentaire de l'assembleur. Il refuse
`MENE1921262A` et `MENE1921247A` dans un contexte TSPE tout en laissant
`MENE1921247A` à la ligne TNSI légitime.

Le test du registre verrouille conjointement :

- `reference_bo == "BO spécial n° 8 du 25 juillet 2019"` ;
- `arrete == "MENE1921246A"` ;
- `url == "https://www.education.gouv.fr/bo/19/Special8/MENE1921246A.htm"` ;
- l'unicité de `manual_id: TSPE_2026_2027` ;
- `programme_source == "SRC-BO2019-TSPE"`.

Le test du README exige la disparition des affirmations selon lesquelles le
« registre courant » porterait encore le NOR STMG, tout en conservant le lien
vers `MENE1921246A` et la mention historique nécessaire dans les audits datés.

La correction est un remplacement ciblé de NOR, l'ajout de l'URL officielle
manquante dans le registre et l'actualisation des deux passages du README. Les
champs de fichier et SHA-256 existants sont conservés.

## Validation

Le lot exécute :

- `tests/test_programme_registry.py` ;
- le parse YAML du registre ;
- le contrôle des empreintes des extraits ;
- les tests d'inventaire affectés par le registre ;
- `git diff --check`.

Mutation adversariale : réintroduire temporairement `MENE1921262A` dans une
fixture TSPE doit rendre le test réglementaire rouge.

## Commits attendus

1. `[TESTS] étend le contrat de provenance TSPE` ;
2. `[PROGRAMME] corrige le NOR officiel TSPE`.

La documentation et la production réglementaire ne sont pas mélangées avec
les corrections élève ou LaTeX.

## Définition de terminé

Le lot est terminé lorsque tous les documents TSPE actifs et le README portent
un état courant cohérent avec `MENE1921246A`, que les tests réglementaires et
l'assertion exacte de l'URL sont verts, que l'empreinte de l'extrait suivi
reste inchangée, que le PDF local ignoré n'est pas une dépendance du gate, que
les audits datés sont intacts et que deux revues indépendantes ont approuvé la
conformité et la qualité du diff.
