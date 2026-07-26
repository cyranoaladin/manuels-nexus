# Conformité au programme 1SPE applicable à la rentrée 2026

## Autorité normative

Le référentiel canonique est fondé sur l’arrêté du 26 février 2026,
NOR `MENE2602917A`, publié au Journal officiel du 27 mars 2026 et au
Bulletin officiel n° 14 du 2 avril 2026. Son annexe remplace, pour la classe de
première, l’annexe du programme publiée en 2019 et s’applique à compter de la
rentrée scolaire 2026-2027 (`normative_from: 2026-09-01`).

- page officielle :
  <https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A> ;
- annexe officielle de 11 pages :
  <https://www.education.gouv.fr/sites/default/files/document/Annexe%20%E2%80%93%20Programme%20d%26%23039%3Benseignement%20de%20sp%C3%A9cialit%C3%A9%20de%20math%C3%A9matiques%20de%20la%20classe%20de%20premi%C3%A8re%20de%20la%20voie%20g%C3%A9n%C3%A9rale-515408.pdf> ;
- copie locale non versionnée :
  `sources/BO2026_1SPE_specialite.pdf` ;
- SHA-256 du PDF :
  `5303df0fcf6335f06d00c969a61dcd82cc3fdfd105271ae5c2ef580ff49b6c08` ;
- extraction canonique :
  `sources/txt/BO2026_1SPE_specialite.txt` ;
- SHA-256 du TXT :
  `4e70f1989cdb47caf184cb138d839799e895fcdc5addec3737f0216b6bfa33df`.

Une page Éduscol peut encore présenter le texte de 2019 dans une rubrique
« programmes en vigueur » avant la rentrée. Cette présentation transitoire ne
prévaut pas sur l’arrêté de 2026 et sa date d’application. Le PDF de 2019 est
conservé au registre comme archive non normative.

## Périmètre de la transcription

`referentiel/programme_1SPE_2026.json` transcrit, sans reformulation :

- les contenus ;
- les capacités attendues ;
- les démonstrations ;
- les exemples d’algorithmes ;
- les approfondissements possibles ;
- les prescriptions des trois parties transversales ;
- les quatre expérimentations de la rubrique « Expérimentations ».

La règle de sélection des rubriques « Objectifs » est explicite : les phrases
qui fixent une prescription ou une borne de périmètre sont transcrites ; le
contexte purement descriptif et l’histoire des mathématiques ne sont pas
transformés artificiellement en obligations. Les passages transversaux qui
fixent une progression ou une modalité de mise en œuvre sont conservés comme
`contextual_guidance`.

Six phrases prescriptives ou bornes des rubriques d’objectifs complètent ainsi
les rubriques structurées :

- autres types de suites non exigibles :
  `OBJ-ALG-SUITES-BORNE-001` ;
- aucune formalisation des limites de suites :
  `OBJ-ALG-LIMITE-BORNE-001` ;
- forme canonique générale non attendue :
  `OBJ-ALG-SD-BORNE-001` ;
- aucune définition formelle du nombre dérivé :
  `OBJ-ANA-DERIVEE-BORNE-001` ;
- maintien du calcul vectoriel en géométrie non repérée :
  `OBJ-GEO-VECTEURS-PRESC-001` ;
- univers finis et variables aléatoires réelles :
  `OBJ-PROB-UNIVERS-BORNE-001`.

Le programme comporte exactement quatre domaines thématiques :

1. Algèbre ;
2. Analyse ;
3. Géométrie ;
4. Probabilités et statistiques.

« Vocabulaire ensembliste et logique », « Algorithmique et programmation » et
« Automatismes » sont modélisés comme domaines transversaux, jamais comme un
cinquième domaine thématique.

## Classification normative

La classe d’obligation décrit le statut du texte officiel ; le verdict éditorial
décrit séparément le choix de fabrication du manuel.

| Rubrique officielle | Type | Classe d’obligation |
|---|---|---|
| Contenus | `contenu` | `mandatory_content` |
| Capacités attendues | `capacite` | `prescribed_teaching` |
| Démonstrations | `demonstration` | `prescribed_teaching` |
| Exemples d’algorithmes | `algorithme` | `contextual_guidance` |
| Expérimentations | `algorithme` | `mandatory_content` |
| Approfondissements possibles | `approfondissement` | `optional_extension` |
| Prescriptions transversales | `transversal` | selon le libellé officiel |

Les quatre expérimentations sont donc obligatoires dans le périmètre éditorial :

- `VA-EXP-SIMULER` ;
- `VA-EXP-FONCTION-MOYENNE` ;
- `VA-EXP-DISTANCE-MOYENNE-ESPERANCE` ;
- `VA-EXP-PROPORTION-2SIGMA`.

La loi binomiale et ses paramètres ne sont pas ajoutés au référentiel : le
programme prescrit seulement, pour `n ≤ 4`, la répétition de `n` épreuves de
Bernoulli indépendantes et identiques.

## Cardinalités exactes

La double lecture de l’annexe, complétée par la revue indépendante des phrases
prescriptives dans les objectifs, fixe 175 items :

| Type | Classe | Nombre |
|---|---|---:|
| `contenu` | `mandatory_content` | 42 |
| `contenu` | `contextual_guidance` | 5 |
| `capacite` | `prescribed_teaching` | 44 |
| `demonstration` | `prescribed_teaching` | 11 |
| `algorithme` | `mandatory_content` | 4 |
| `algorithme` | `contextual_guidance` | 11 |
| `approfondissement` | `optional_extension` | 17 |
| `transversal` | `mandatory_content` | 8 |
| `transversal` | `prescribed_teaching` | 29 |
| `transversal` | `contextual_guidance` | 4 |

Soit 134 items thématiques et 41 items transversaux.

## Contrôle reproductible

L’extraction ne normalise que `CRLF` et `CR` vers `LF` :

```bash
.venv/bin/python scripts/extract_official_source.py
```

Le contrôleur vérifie le schéma fermé, le PDF, l’extraction TXT, les citations
sur leur page, les identifiants, les cardinalités, les classes d’obligation et
les affectations :

```bash
.venv/bin/python scripts/check_programme_1spe_2026.py
```

Un code 0 et `status: certified` certifient ces contrôles machine. Ils ne
remplacent pas la revue réglementaire indépendante consignée dans
`validations/release-1spe/revue-programme.md`.

## Textes connexes

Les automatismes détaillés par d’autres textes et la note de service
`MENE2515469N` relative à l’épreuve anticipée de mathématiques sont des sources
connexes. Les caractéristiques de l’épreuve ne sont pas injectées dans les
items de l’annexe du programme, sauf lorsqu’une prescription figure réellement
dans cette annexe.
