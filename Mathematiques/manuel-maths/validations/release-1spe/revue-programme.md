# Revue réglementaire indépendante du programme 1SPE 2026

Statut : `approved`

## Identification de la revue

- acteur : Codex, agent distinct `task2_regulatory_review` ;
- nature : revue indépendante en lecture seule du référentiel ;
- date : 2026-07-26, fuseau `Africa/Tunis` ;
- référentiel revu :
  `referentiel/programme_1SPE_2026.json` ;
- SHA-256 du référentiel revu :
  `eea0e86615b7d4541f2054bf9cdd39b8409dfddb79f4020a8026d6515c618f13` ;
- items comparés individuellement : **175 / 175** ;
- re-revue de correction : les six nouveaux items `OBJ-*` ont été contrôlés
  individuellement, puis les 175 items ont été recoupés de nouveau ;
- verdict : **`approved`** ; aucun écart P0, P1 ou P2 ouvert.

Ce verdict porte sur l’état exact identifié par l’empreinte ci-dessus. Il ne
constitue ni une validation humaine, ni une validation d’une version
ultérieure du référentiel.

## Autorité et sources contrôlées

L’autorité recoupée est l’arrêté du 26 février 2026, NOR `MENE2602917A`,
publié au Journal officiel du 27 mars 2026 et au Bulletin officiel n° 14 du
2 avril 2026. Son article 2 prévoit l’application à la rentrée scolaire
2026-2027.

- page B.O. :
  <https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A> ;
- annexe officielle :
  <https://www.education.gouv.fr/sites/default/files/document/Annexe%20%E2%80%93%20Programme%20d%26%23039%3Benseignement%20de%20sp%C3%A9cialit%C3%A9%20de%20math%C3%A9matiques%20de%20la%20classe%20de%20premi%C3%A8re%20de%20la%20voie%20g%C3%A9n%C3%A9rale-515408.pdf> ;
- copie locale de l’annexe :
  `sources/BO2026_1SPE_specialite.pdf` ;
- SHA-256 du PDF local et du PDF téléchargé depuis l’URL officielle :
  `5303df0fcf6335f06d00c969a61dcd82cc3fdfd105271ae5c2ef580ff49b6c08` ;
- nombre de pages PDF : 11 ;
- extraction locale :
  `sources/txt/BO2026_1SPE_specialite.txt` ;
- SHA-256 de l’extraction locale et d’une nouvelle exécution indépendante de
  `pdftotext -layout` :
  `4e70f1989cdb47caf184cb138d839799e895fcdc5addec3737f0216b6bfa33df`.

## Méthode indépendante

La revue n’a pas modifié le référentiel, le schéma, les scripts ni les tests.
Elle a combiné quatre contrôles distincts :

1. lecture visuelle des 11 pages du PDF et repérage des rubriques ;
2. nouvelle extraction directe du PDF avec `pdftotext -layout`, comparée
   octet par octet au TXT versionné ;
3. comparaison des 175 citations après la seule normalisation
   `normalize = " ".join(value.split())`, sur chacune des 11 pages 1-based ;
4. reconstruction manuelle, par titres et puces du PDF, des rubriques
   « Contenus », « Capacités attendues », « Démonstrations », « Exemples
   d’algorithmes », « Approfondissements possibles », des prescriptions
   transversales et des quatre « Expérimentations ».

Commandes de preuve exécutées depuis la racine du projet :

```bash
sha256sum \
  sources/BO2026_1SPE_specialite.pdf \
  sources/txt/BO2026_1SPE_specialite.txt \
  referentiel/programme_1SPE_2026.json

pdfinfo sources/BO2026_1SPE_specialite.pdf

pdftotext -layout sources/BO2026_1SPE_specialite.pdf - \
  | sha256sum

curl -fsSL \
  'https://www.education.gouv.fr/sites/default/files/document/Annexe%20%E2%80%93%20Programme%20d%26%23039%3Benseignement%20de%20sp%C3%A9cialit%C3%A9%20de%20math%C3%A9matiques%20de%20la%20classe%20de%20premi%C3%A8re%20de%20la%20voie%20g%C3%A9n%C3%A9rale-515408.pdf' \
  | sha256sum

jq -r '.items[] | [.type, .obligation_class] | @tsv' \
  referentiel/programme_1SPE_2026.json \
  | sort | uniq -c

python3.12 scripts/check_programme_1spe_2026.py

.venv/bin/python -m pytest \
  tests/test_official_source_extraction.py \
  tests/test_programme_1spe_2026.py -q
```

Le recoupement indépendant page/citation a produit :

```text
items 175
pdf_pages 11
byte_identical True
missing 0 []
wrong_page 0 []
multi_page 0 []
unique_ids 175
duplicate_exact_quotes 0
```

Le contrôleur du projet a également retourné `status: certified`, sans erreur,
et les tests ciblés ont donné `22 passed`. Le SHA-256 du référentiel est resté
`eea0e86615b7d4541f2054bf9cdd39b8409dfddb79f4020a8026d6515c618f13`
avant et après ces exécutions.

## Recompte indépendant

### Matrice des dix cardinalités

| Type | Classe d’obligation | Recompte indépendant |
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
| **Total** |  | **175** |

Ces cardinalités sont exactes pour la granularité actuellement déclarée dans
le référentiel : 128 items issus des rubriques thématiques explicites, six
prescriptions ou bornes issues des rubriques « Objectifs » et 41 items
transversaux. Le B.O. ne publie pas lui-même le nombre « 175 ».

### Reconstruction par rubrique thématique

| Rubrique | Rubriques structurées | Ajouts « Objectifs » | Total |
|---|---:|---:|---:|
| Suites numériques | 21 | 2 | 23 |
| Second degré | 10 | 1 | 11 |
| Dérivation | 20 | 1 | 21 |
| Variations | 8 | 0 | 8 |
| Fonction exponentielle | 12 | 0 | 12 |
| Trigonométrie | 7 | 0 | 7 |
| Produit scalaire | 12 | 1 | 13 |
| Géométrie repérée | 10 | 0 | 10 |
| Probabilités conditionnelles | 11 | 0 | 11 |
| Variables aléatoires | 13 | 1 | 14 |
| Expérimentations | 4 | 0 | 4 |
| **Total** | **128** | **6** | **134** |

### Prescriptions et bornes des rubriques « Objectifs »

Les six ajouts corrigent l’écart P1 de la première lecture :

| ID | Page | Type × classe | Affectation |
|---|---:|---|---|
| `OBJ-ALG-SUITES-BORNE-001` | 5 | `contenu × contextual_guidance` | `1SPE-SUITES` |
| `OBJ-ALG-LIMITE-BORNE-001` | 5 | `contenu × contextual_guidance` | `1SPE-SUITES` |
| `OBJ-ALG-SD-BORNE-001` | 5 | `contenu × contextual_guidance` | `1SPE-SECOND-DEGRE` |
| `OBJ-ANA-DERIVEE-BORNE-001` | 7 | `contenu × contextual_guidance` | `1SPE-DERIVATION-LOCAL` |
| `OBJ-GEO-VECTEURS-PRESC-001` | 9 | `capacite × prescribed_teaching` | `1SPE-PRODUIT-SCALAIRE` |
| `OBJ-PROB-UNIVERS-BORNE-001` | 10 | `contenu × contextual_guidance` | `1SPE-VARIABLES-ALEATOIRES` |

Les cinq bornes décrivent le périmètre ou le niveau d’exigibilité et ne créent
pas de nouveau contenu obligatoire ; `contextual_guidance` est donc cohérent.
La phrase « Les élèves doivent conserver une pratique… » prescrit une activité
élève et relève correctement de `capacite × prescribed_teaching`. Les six
verdicts éditoriaux sont séparés et valent `included`.

### Quatre expérimentations

Les quatre entrées sont présentes, distinctes, situées page 11, affectées à
`1SPE-VARIABLES-ALEATOIRES`, classées `algorithme × mandatory_content` et
portent un verdict éditorial séparé `included` :

- `VA-EXP-SIMULER` ;
- `VA-EXP-FONCTION-MOYENNE` ;
- `VA-EXP-DISTANCE-MOYENNE-ESPERANCE` ;
- `VA-EXP-PROPORTION-2SIGMA`.

## Contrôles des 175 entrées

- citation exacte après normalisation des espaces : 175 conformes sur 175 ;
- page PDF 1-based : 175 conformes sur 175 ;
- identifiants : 175 uniques, aucune rupture dans les familles numérotées ;
- doublons de citations exactes : aucun ;
- types et classes selon les rubriques explicitement transcrites : conformes ;
- domaines : quatre thématiques et trois transversaux, conformes aux titres du
  B.O. ;
- affectations : chaque item thématique est affecté à son chapitre ; chaque
  item transversal a une affectation non vide et une justification quand elle
  est distribuée ;
- verdict éditorial : champ distinct de la classe réglementaire ; les
  obligations sont `included` et les 17 approfondissements facultatifs sont
  `excluded_with_rationale` avec une justification non vide ;
- texte de préambule présenté à tort comme item prescriptif : aucun ; aucun
  item n’est porté par les pages 1 ou 2, et l’unique item de page 3 commence
  sous le titre « Programme — Vocabulaire ensembliste et logique » ;
- découpages artificiels dans les puces des rubriques transcrites : aucun
  constaté.

## Écarts

### P0

Aucun.

### P1 — bloquant

**Aucun écart ouvert.**

Historique clos : `P1-OBJ-LIMITES-001`, signalé sur le référentiel
`ad91ada4a316ba63c2cf8513c434d0e4c58cc338cafb72c69b65f41d6c3bf465`,
est corrigé. Le référentiel porte désormais une politique explicite :
`include_explicit_prescriptions_and_scope_boundaries`, avec exclusion du
contexte descriptif et de l’histoire des mathématiques. Les six citations,
pages, classes, affectations et verdicts demandés sont présents et ont été
relus indépendamment.

### P2

Aucun. Les limites d’extraction mathématique de `pdftotext` sont décrites
ci-dessous mais ne constituent pas une divergence entre le JSON et
l’extraction canonique.

## Limites de la preuve

- La normalisation des espaces préserve fidèlement la sortie `pdftotext`, mais
  certaines formules disposées en deux dimensions ont un ordre textuel peu
  lisible, notamment `ANA-EXP-ALG-002`, `ANA-TRIG-DEM-001`,
  `GEO-PS-CONT-004`, `GEO-PS-DEM-002` et
  `VA-EXP-PROPORTION-2SIGMA`. Leur concordance textuelle a été recoupée
  visuellement avec le PDF ; la citation ne doit pas être réutilisée comme
  texte mathématique prêt à publier.
- Les affectations de chapitres sont des choix éditoriaux et non des données
  publiées par le B.O. La revue vérifie leur cohérence et leur justification,
  mais pas encore leur réalisation effective dans les deux manuscrits.
- La revue ne valide ni le contenu mathématique des manuscrits, ni la
  conformité d’un futur PDF élève ou professeur ; elle porte uniquement sur
  le référentiel identifié par son SHA-256.

## Verdict

**`approved`**

Les 175 entrées sont fidèles au PDF officiel dans le périmètre de sélection
explicite. Les dix cardinalités, les six prescriptions ou bornes des rubriques
« Objectifs » et les quatre expérimentations sont correctement recomptées.
Aucune citation n’est orpheline, dupliquée ou décalée ; aucun écart P0, P1 ou
P2 ne reste ouvert sur le référentiel identifié par le SHA-256
`eea0e86615b7d4541f2054bf9cdd39b8409dfddb79f4020a8026d6515c618f13`.
