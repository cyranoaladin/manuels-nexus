# A4 — fermeture comptable finale des catégories

Observation fraîche et en lecture seule au SHA source A4
`535d623703cb3d36ee66849fbd05e3fa0c18a31d`. Le commit de rapport de départ
est `b6bf3f8f1326f9ebb3b23f3ebd42c73566d16180`.

## Résultat

```text
RAW                         2971
SUM(primary categories)     2971
UNIQUE primary fingerprints 2971
BLOCKING                    2971
NONBLOCKING                    0
UNKNOWN                        0
cross-primary duplicates       0
secondary tags                 0
BALANCE                     PASS
```

Les tags secondaires sont comptés séparément et sont absents de ce snapshot.
Chaque fingerprint actif appartient donc à exactement une catégorie primaire.

## Toutes les catégories primaires actives dans le registre

| Catégorie | Compte |
|---|---:|
| `assembler_invalid` | 0 |
| `blocking_statuses` | 2222 |
| `broken_assembly_references` | 0 |
| `broken_latex_references` | 0 |
| `broken_meta_references` | 0 |
| `chapters_not_in_manual` | 0 |
| `context_mismatches` | 3 |
| `contract_invalid` | 0 |
| `contract_missing` | 0 |
| `duplicate_assembly_objects` | 0 |
| `duplicate_capacity_refs` | 0 |
| `duplicate_ids` | 0 |
| `invalid_capacities` | 0 |
| `invalid_meta_references` | 0 |
| `invalid_statuses` | 0 |
| `latex_cycles` | 0 |
| `metadata_invalid` | 0 |
| `metadata_missing` | 0 |
| `missing_assemblers` | 0 |
| `missing_corrections` | 0 |
| `orphan_files` | 12 |
| `unassembled_objects` | 52 |
| `unattributed_pdfs` | 22 |
| `unavailable_inspiration_sources` | 0 |
| `unclassified_types` | 660 |
| `unknown_chapter_prefixes` | 0 |
| **Somme** | **2971** |

## Les 25 fingerprints absents du résumé précédent

Le résumé précédent explicitait `2222 + 660 + 52 + 12 = 2946`. Son écart de
25 est exactement :

```text
context_mismatches   3
unattributed_pdfs   22
TOTAL               25
```

Les trois `context_mismatches` sont :

- `412440a833f2a67e` — `TCOMPL-AIRES-CR-010-DERIVEE` — `Mathematiques/manuel-maths/chapitres/TCOMPL-CALCULS-AIRES/cours/10_C1_derivee_composee.tex` ;
- `d4d96a91fdd7f2ca` — `TCOMPL-AIRES-COURS-07-FR` — `Mathematiques/manuel-maths/chapitres/TCOMPL-CALCULS-AIRES/cours/07_td_fil_rouge.tex` ;
- `dc3c58388e2cfe7c` — `TCOMPL-AIRES-COURS-07-TC` — `Mathematiques/manuel-maths/chapitres/TCOMPL-CALCULS-AIRES/cours/07_td_contextualise.tex`.

Pour chacun, le champ `chapitre` vaut `TSPE-DERIVATION-CONVEXITE` alors que
le contexte de chemin attendu vaut `TCOMPL-CALCULS-AIRES`. Aucune correction
n'est apportée : cette catégorie est hors périmètre A5.

Les 22 `unattributed_pdfs` sont :

- `e67df1603e86960a` — `MANUELS_PDF_PUBLICATION/01_Maths_1re_Spe_Eleve.pdf` ;
- `19f86fa8a95e8a2a` — `MANUELS_PDF_PUBLICATION/02_Maths_1re_Spe_Professeur.pdf` ;
- `9f6f3eebe9648fa5` — `MANUELS_PDF_PUBLICATION/03_Maths_Tle_Spe_Eleve.pdf` ;
- `3318b77d82f01509` — `MANUELS_PDF_PUBLICATION/04_Maths_Tle_Spe_Professeur.pdf` ;
- `c66b4f81d520b956` — `MANUELS_PDF_PUBLICATION/05_Maths_Tle_Expertes_Eleve.pdf` ;
- `3ef9c1ecc68a20fd` — `MANUELS_PDF_PUBLICATION/06_Maths_Tle_Expertes_Professeur.pdf` ;
- `89c3008b764beb79` — `MANUELS_PDF_PUBLICATION/07_Maths_Tle_Complementaires_Eleve.pdf` ;
- `64372cc4e21b0fea` — `MANUELS_PDF_PUBLICATION/08_Maths_Tle_Complementaires_Professeur.pdf` ;
- `389e14684d9fc93f` — `MANUELS_PDF_PUBLICATION/09_NSI_1re_Eleve.pdf` ;
- `2f17d20dda3ce4ac` — `MANUELS_PDF_PUBLICATION/10_NSI_1re_Professeur.pdf` ;
- `7cf107c2cd4e352b` — `MANUELS_PDF_PUBLICATION/11_NSI_Tle_Eleve.pdf` ;
- `cdf57df87e7567ab` — `MANUELS_PDF_PUBLICATION/12_NSI_Tle_Professeur.pdf` ;
- `e1f587fb6ddd4ee4` — `NSI/corpus_nsi/00_programmes_officiels/programme_nsi_premiere.pdf` ;
- `26c041687903b4ed` — `NSI/corpus_nsi/00_programmes_officiels/programme_nsi_terminale.pdf` ;
- `3fee3dc53f03dea3` — `NSI/corpus_nsi/latex/packs/premiere/P13/P13_aides.pdf` ;
- `afab4b5b2e6ebc53` — `NSI/corpus_nsi/latex/packs/premiere/P13/P13_corrige.pdf` ;
- `a7b80bac81c82c6d` — `NSI/corpus_nsi/latex/packs/premiere/P13/P13_cours.pdf` ;
- `32d4022e33cf6216` — `NSI/corpus_nsi/latex/packs/premiere/P13/P13_evaluation.pdf` ;
- `998b6ab69aa0bf30` — `NSI/corpus_nsi/latex/packs/premiere/P13/P13_fiche_methode.pdf` ;
- `abbc3a4972db5b2c` — `NSI/corpus_nsi/latex/packs/premiere/P13/P13_td.pdf` ;
- `cf9eaad11ac001e5` — `NSI/corpus_nsi/latex/packs/premiere/P13/P13_tp.pdf` ;
- `52f548465adbd5ca` — `NSI/corpus_nsi/latex/packs/premiere/P13/P13_trace.pdf`.

Leur raison brute est « PDF suivi sans attribution fiable à un livrable ».
Ils n'ont aucun tag secondaire actif et restent hors périmètre A5.

## Snapshot PRE-A5

```text
RAW                     2971
BLOCKING                2971
NONBLOCKING                0
unclassified_types       660
blocking_statuses        2222
unassembled                52
orphans                    12
unattributed_pdfs          22
context_mismatches          3
missing_corrections         0
broken_meta                 0
duplicates                  0
P0                          0
broken_latex                0
cycles                      0
NEW_UNQUALIFIED             0
EXPECTED_REVIEW_DEBT       89
```

```text
REFERENCE_BASELINE full SHA256 = 3e9225668121a67c2fdea1248ec420ff16bd3910c8557e3a98df8bb7997250e1
HUMAN_POLICY digest = sha256:07597ede77c7fce1a167a87227178f05a10faabbad4ca1e04d7bb2048fda12a7
inventory source_digest = sha256:56435df0a27c718dc75ca91e60ac83c4c21553a9e61f78a296643e0ab4f2cc00
```

La baseline de référence et la politique humaine sont seulement hashées ;
elles ne sont ni modifiées ni mises à jour.
