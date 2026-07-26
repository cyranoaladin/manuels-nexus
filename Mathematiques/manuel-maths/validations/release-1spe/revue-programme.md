# Revue réglementaire indépendante du programme 1SPE 2026

Statut : `approved`

## Identification de la revue

- acteur : Codex, agent distinct `task2_regulatory_review` ;
- nature : seconde revue indépendante complète après corrections ;
- date : 2026-07-27, fuseau `Africa/Tunis` ;
- référentiel revu :
  `referentiel/programme_1SPE_2026.json` ;
- SHA-256 du référentiel revu :
  `79357aebc60c2c53d82c62760175c97bfb8069c82b3300c52e3fe438b8faf91a` ;
- schéma revu :
  `schemas/programme_1spe_2026.schema.json` ;
- SHA-256 du schéma revu :
  `61e3c2c4a7093c5c38af1d6c3fd2a791804d9d2980e616c860dc7a36242e1140` ;
- documentation de conformité revue :
  `referentiel/CONFORMITE_BO2026.md` ;
- SHA-256 de la documentation revue :
  `66ba2770e23cd8fe1f1c5bd44a6cfff5190af54e5a5e6b7a93995fc963e00c8a` ;
- attestation machine revue :
  `validations/release-1spe/programme-1spe-2026.attestation.json` ;
- SHA-256 de l’attestation revue :
  `4d8b6bbc670c3387dd9684f26e294f4079317c645ec9277a259cedd28ba5a071` ;
- enregistrements comparés individuellement : **181 / 181**, soit
  **175 items** et **6 couvertures d’objectifs** ;
- verdict : **`approved`** ; aucun écart P0, P1 ou P2 ouvert.

Ce verdict porte uniquement sur l’état exact identifié par les empreintes
ci-dessus. Une modification ultérieure du référentiel, du schéma, de la
documentation de conformité ou de l’attestation exige une nouvelle revue.

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
- SHA-256 du PDF local et du PDF retéléchargé depuis l’URL officielle :
  `5303df0fcf6335f06d00c969a61dcd82cc3fdfd105271ae5c2ef580ff49b6c08` ;
- nombre de pages PDF : 11 ;
- extraction locale :
  `sources/txt/BO2026_1SPE_specialite.txt` ;
- SHA-256 de l’extraction locale et d’une nouvelle exécution indépendante de
  `pdftotext -layout` :
  `4e70f1989cdb47caf184cb138d839799e895fcdc5addec3737f0216b6bfa33df`.

Le PDF officiel retéléchargé est identique octet par octet à la copie locale.
Sa nouvelle extraction `pdftotext -layout` est identique octet par octet au
TXT canonique.

## Méthode indépendante

La revue a laissé inchangés le référentiel, le schéma, la conformité, les
scripts et les tests. Seul le présent rapport a été actualisé après les
contrôles indépendants.

Les preuves combinent :

1. lecture des 11 pages du PDF et repérage des rubriques officielles ;
2. téléchargement direct du PDF officiel, contrôle SHA-256 et nouvelle
   extraction avec `pdftotext -layout` ;
3. comparaison indépendante des 181 citations après la seule normalisation
   `normalize = " ".join(value.split())`, page par page ;
4. recalcul, pour chaque citation, de `bo_occurrence`, `bo_offset` et de la
   dernière rubrique officielle applicable, y compris lorsque le tableau se
   poursuit sur la page suivante ;
5. reconstruction des types, classes d’obligation, domaines, affectations,
   cardinalités et portes de diffusion ;
6. validation du schéma fermé, de l’attestation et des tests du projet.

Le recalcul indépendant a produit :

```text
pdf_pages 11
items 175
objective_coverage 6
records_checked 181
missing_quotes 0
wrong_pages 0
wrong_occurrences 0
wrong_offsets 0
wrong_sections 0
duplicate_item_ids 0
item_ids_sha256 ccc2928bf78c5872b2c9d434bc34f5e5e66b5b04e4a17fab7e80ba87b83fd7a8
matrix_sha256 ed08ca8997ccdfd55ffdf5ed023859fc81f320304779ebc0f8b524b109fe7d59
```

Deux citations ont plusieurs occurrences dans leur page source :
`ALG-SUI-DEM-002` et `ALG-SUI-DEM-003`. Elles ciblent correctement la
deuxième occurrence, respectivement aux offsets `2439` et `2466`.

Avant l’actualisation du présent rapport, le contrôleur retournait
`status: review_required` pour l’unique motif
`rapport de revue périmé pour le référentiel courant`. Toutes les autres
catégories d’erreur étaient vides. Les tests ciblés donnaient
`55 passed, 1 failed`, l’unique échec étant le test qui exige un contrôleur
certifié et donc un rapport à jour.

Après actualisation, le contrôleur retourne `status: certified`, avec
`item_count: 175` et toutes les listes d’erreurs vides. Les deux fichiers de
tests ciblés donnent `56 passed`.

## Recompte indépendant

### Matrice des dix cardinalités

| Type | Classe d’obligation | Recompte indépendant |
|---|---|---:|
| `contenu` | `mandatory_content` | 42 |
| `contenu` | `contextual_guidance` | 5 |
| `capacite` | `mandatory_content` | 44 |
| `demonstration` | `prescribed_teaching` | 11 |
| `algorithme` | `mandatory_content` | 4 |
| `algorithme` | `prescribed_teaching` | 11 |
| `approfondissement` | `optional_extension` | 17 |
| `transversal` | `mandatory_content` | 8 |
| `transversal` | `prescribed_teaching` | 29 |
| `transversal` | `contextual_guidance` | 4 |
| **Total** |  | **175** |

Le total se répartit en **134 items thématiques** et **41 items
transversaux**. Le B.O. ne publie pas lui-même le nombre « 175 » : il résulte
de la granularité explicite du référentiel, revue citation par citation.

### Reconstruction par rubrique thématique

| Rubrique | Rubriques structurées | Ajouts ciblés | Total |
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

### Six prescriptions ou bornes ciblées

| ID | Page | Section | Type × classe | Affectation |
|---|---:|---|---|---|
| `OBJ-ALG-SUITES-BORNE-001` | 5 | `Objectifs` | `contenu × contextual_guidance` | `1SPE-SUITES` |
| `OBJ-ALG-LIMITE-BORNE-001` | 5 | `Objectifs` | `contenu × contextual_guidance` | `1SPE-SUITES` |
| `OBJ-ALG-SD-BORNE-001` | 5 | `Objectifs` | `contenu × contextual_guidance` | `1SPE-SECOND-DEGRE` |
| `OBJ-ANA-DERIVEE-BORNE-001` | 7 | `Objectifs` | `contenu × contextual_guidance` | `1SPE-DERIVATION-LOCAL` |
| `OBJ-GEO-VECTEURS-PRESC-001` | 9 | `Objectifs` | `capacite × mandatory_content` | `1SPE-PRODUIT-SCALAIRE` |
| `OBJ-PROB-UNIVERS-BORNE-001` | 10 | `Variables aléatoires réelles` | `contenu × contextual_guidance` | `1SPE-VARIABLES-ALEATOIRES` |

Les cinq bornes décrivent le périmètre ou le niveau d’exigibilité et sont
correctement conservées comme `contextual_guidance`. La prescription de
calcul vectoriel en géométrie non repérée relève d’une capacité obligatoire
et est correctement classée `capacite × mandatory_content`. Les six verdicts
éditoriaux sont distincts et valent `included`.

### Six couvertures d’objectifs bloquantes

Les six prescriptions d’objectifs déjà portées par des items structurés ne
sont pas dupliquées. Elles sont enregistrées comme portes de diffusion :

| ID | Items porteurs | Chapitre | Nature |
|---|---|---|---|
| `OBJ-COV-SUITES-TAUX-FIXE` | `ALG-SUI-CONT-004`, `ALG-SUI-CAP-005` | `1SPE-SUITES` | `required_learning_outcome` |
| `OBJ-COV-SD-COMPLETION-CARRE` | `ALG-SD-CONT-002` | `1SPE-SECOND-DEGRE` | `required_learning_outcome` |
| `OBJ-COV-SD-FACTORISATION-DIRECTE` | `ALG-SD-CAP-003` | `1SPE-SECOND-DEGRE` | `required_learning_outcome` |
| `OBJ-COV-DERIVEE-GRAPHIQUE` | `ANA-DERLOC-CONT-001`, `ANA-DERLOC-CONT-003` | `1SPE-DERIVATION-LOCAL` | `required_introduction_modality` |
| `OBJ-COV-DERIVEE-ALGEBRIQUE` | `ANA-DERLOC-CAP-001` | `1SPE-DERIVATION-LOCAL` | `required_introduction_modality` |
| `OBJ-COV-DERIVEE-NUMERIQUE` | `ANA-DERLOC-CONT-004`, `ANA-DERLOC-CAP-005` | `1SPE-DERIVATION-LOCAL` | `required_introduction_modality` |

Chaque enregistrement porte `release_gate: true`, une citation officielle
exacte, un chapitre cohérent et au moins un item porteur affecté à ce même
chapitre. Le schéma et le contrôleur interdisent leur omission silencieuse.

### Rubriques algorithmiques corrigées

Les six entrées suivantes sont toutes rattachées exactement à
`Exemple d’algorithme` et classées
`algorithme × prescribed_teaching` :

- `ANA-DERLOC-ALG-001` ;
- `ANA-VAR-ALG-001` ;
- `ANA-EXP-ALG-001` ;
- `ANA-EXP-ALG-002` ;
- `ANA-TRIG-ALG-001` ;
- `PROB-COND-ALG-001`.

Les trois entrées sous `Exemples d’algorithme` et les deux sous
`Exemples d’algorithmes` portent la même classe. Les quatre
`Expérimentations` restent, elles, classées
`algorithme × mandatory_content`.

## Contrôles des 175 items

- citations exactes après normalisation des espaces : 175 conformes sur 175 ;
- pages PDF 1-based : 175 conformes sur 175 ;
- occurrences et offsets : 175 conformes sur 175 ;
- rubriques `bo_section` : 175 conformes sur 175 ;
- identifiants : 175 uniques, aucune collision avec les six IDs de
  couverture ;
- types et classes : conformes aux rubriques officielles ;
- domaines : quatre thématiques et trois transversaux, conformes au B.O. ;
- affectations : chaque item porte au moins un chapitre cohérent ;
- verdict éditorial : toutes les obligations sont `included` ; les
  17 approfondissements facultatifs sont `excluded_with_rationale` avec une
  justification non vide ;
- quatre expérimentations : présentes, distinctes, page 11, affectées à
  `1SPE-VARIABLES-ALEATOIRES`, classées
  `algorithme × mandatory_content`.

## Écarts

### P0

Aucun.

### P1

Aucun écart ouvert.

### P2

Aucun écart ouvert.

Les écarts des passes précédentes sont clos : prescriptions d’objectifs
manquantes, sept rubriques `bo_section` incorrectes, taxonomie documentaire
périmée, attestation ne couvrant pas la conformité et couverture d’objectifs
insuffisamment bloquante.

## Limites de la preuve

- La normalisation des espaces préserve la sortie `pdftotext`, mais certaines
  formules disposées en deux dimensions ont un ordre textuel peu lisible,
  notamment `ANA-EXP-ALG-002`, `ANA-TRIG-DEM-001`, `GEO-PS-CONT-004`,
  `GEO-PS-DEM-002` et `VA-EXP-PROPORTION-2SIGMA`. Leur concordance a été
  recoupée avec le PDF ; ces citations ne sont pas du texte mathématique prêt
  à publier.
- Les affectations de chapitres sont des choix éditoriaux, non des données
  publiées par le B.O.
- Les six `objective_coverage` imposent un audit futur de la réalisation
  effective dans les manuscrits. La présente revue certifie la qualité du
  référentiel et du gate, pas encore la preuve de couverture dans les deux
  ouvrages.
- La revue ne valide ni le contenu mathématique des manuscrits ni la
  conformité d’un futur PDF élève ou professeur.

## Verdict

**`approved`**

Les 175 items et les six couvertures d’objectifs sont fidèles à l’annexe
officielle dans le périmètre de sélection explicite. Les dix cardinalités,
les occurrences, les offsets, les rubriques et les portes de diffusion ont
été recomptés indépendamment. Aucun écart P0, P1 ou P2 ne reste ouvert sur
l’état exact identifié en tête du présent rapport.
