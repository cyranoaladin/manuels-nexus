# A3 — FORENSIQUE DES 3 DUPLICATE_ASSEMBLY_OBJECTS (AVANT CORRECTION)

État de référence : `START_SHA = 018a0adbba10fc4e18a74a23f671b25c1b3241e3`.
Document établi AVANT toute modification. Version machine :
`audit/A3_DUPLICATE_ASSEMBLY_FORENSICS.json`.

## Vue d'ensemble

Les 3 anomalies partagent un unique assemblage et une unique cause :

- **Assemblage** : `math:static:Mathematiques/manuel-maths/build/maquette-v5/maquette.tex`
  (maquette éditoriale V5, 15 pages, chapitre source `1SPE-DERIVATION-LOCAL`,
  variante unique `maquette-v5` — aucune dimension élève/professeur).
- **Objets** : exercices `1SPE-DERLOCAL-EX-001`, `EX-002`, `EX-005`.
- **Double inclusion structurelle** (deux `\input` chacun dans le master) :
  - bloc `methodePairee` ME-001, pages 6-8 (lignes 41-43 du master) — les
    exercices y sont rendus comme **applications de la méthode M1** ;
  - `grilleExercices`, pages 9-10 (lignes 50, 51, 56) — grille complète des
    20 exercices, où ils portent les numéros 1, 2 et 7.

## Autorité de l'occurrence attendue (indépendante de l'assembleur)

Le manifest canonique suivi `build/maquette-v5/manifest.json` déclare :

```json
"rendered_method": {"id": "1SPE-DERLOCAL-ME-001",
  "applications": ["1SPE-DERLOCAL-EX-001", "1SPE-DERLOCAL-EX-002", "1SPE-DERLOCAL-EX-005"]}
```

et `exercise_order` contient les 20 exercices (dont ces 3, positions 1, 2, 7).
La table de renvois générée depuis ce manifest impose la chaîne éditoriale
`required_strings: "S'entraîner : ex. 1, 2, 7 p. 9"` — la méthode renvoie
explicitement vers la grille où les mêmes exercices figurent. Donc :

- **EXPECTED_OCCURRENCE_COUNT = 2** pour ces 3 objets dans CET assemblage
  (1 en application de méthode + 1 en grille), source : manifest canonique,
  antérieur au diagnostic (aucun ajustement d'expected sur l'observé) ;
- expected = 1 pour tout autre objet de l'assemblage (17 exercices, cours,
  méthodes, QCM, corrigés — tous observés à 1).

## Preuve PDF (build existant, maquette 15 pages PASS)

L'énoncé d'EX-001 (« Calculer le taux de variation de f entre 1 et 4 »)
apparaît exactement 1 fois page 8 (bloc « Application » de la méthode) et
1 fois page 9 (grille, entrée n°1) ; `pdftotext` page 7-8 contient
« S'entraîner : ex. 1, 2, 7 p. 9 ». La double apparition est publiée et
correspond au gabarit validé (maquette 15 pages, D7 bundle).

## Les 3 cas individuellement

| champ | #1 | #2 | #3 |
| --- | --- | --- | --- |
| fingerprint | `19669084dffa5d5b` | `b912c1041392a181` | `2695d63b022fe9f0` |
| object_id | 1SPE-DERLOCAL-EX-001 | 1SPE-DERLOCAL-EX-002 | 1SPE-DERLOCAL-EX-005 |
| source_path | chapitres/1SPE-DERIVATION-LOCAL/exercices/1SPE-DERLOCAL-EX-001.tex | …EX-002.tex | …EX-005.tex |
| sha256 (obj) | `42007b26399a82a5…` | `e896c34ea006a77c…` | `824f39b800e1bb39…` |
| manual | — (maquette hors matrice manuels ; chapitre 1SPE) | idem | idem |
| chapter | 1SPE-DERIVATION-LOCAL | idem | idem |
| variant | maquette-v5 (unique) | idem | idem |
| object_type | exercice | exercice | exercice |
| all_inclusion_paths | master l.41 (methodePairee) + l.50 (grille) | master l.42 + l.51 | master l.43 + l.56 |
| manifest_entries | applications[0] + exercise_order[0] | applications[1] + exercise_order[1] | applications[2] + exercise_order[6] |
| producer | build_maquette_v5.py (renvois) | idem | idem |
| assembler | build/maquette-v5/maquette.tex (master statique suivi) | idem | idem |
| generated_master | aucun (master écrit à la main, suivi) | idem | idem |
| occurrence_count_expected | **2** (manifest) | **2** | **2** |
| occurrence_count_observed | 2 | 2 | 2 |
| pdf_occurrence | 2 (p.8 + p.9) | 2 (p.8 + p.9) | 2 (p.8 + p.9) |
| root_cause | détecteur : expected=1 codé en dur, aucune notion de réutilisation contractuelle | idem | idem |
| real_product_defect | **NO** (comportement éditorial voulu et publié) | NO | NO |
| analyzer_false_positive | partiel : l'observation « 2 inclusions » est exacte, le verdict « anomalie » est faux faute de contrat déclaré | idem | idem |
| intentional_reuse_candidate | **YES — confirmé par le manifest et la chaîne de renvois** | YES | YES |

## Classification (§3)

**INTENTIONAL_REUSE** pour les 3 (une seule cause racine partagée).
Aucun GLOB_OVERLAP (master écrit ligne à ligne), aucune double entrée de
manifest (applications et exercise_order sont deux rôles distincts), aucun
bug de variante (assemblage mono-variante), aucune duplication d'alias
(chemins strictement identiques), aucun contenu à supprimer (§4 : les deux
inclusions sont légitimes ; l'objectif est de contractualiser le chemin
d'inclusion, pas de toucher au contenu ni au master).

## Décision de correction (niveau : analyseur + contrat déclaré)

1. Créer un registre suivi `audit/ASSEMBLY_REUSE_CONTRACTS.yaml`
   (+ schéma) déclarant, par (assembly_id, object_path), l'occurrence
   attendue avec autorité et justification — alimenté par le manifest
   canonique, jamais par l'observation.
2. Le détecteur statique applique l'invariant permanent bidirectionnel :
   `occurrence_count == expected_occurrence_count` (défaut 1) ; toute
   inclusion double NON déclarée reste une anomalie, et une occurrence
   observée ≠ contrat (y compris inférieure) devient une anomalie.
3. Tests : rouge avant correction (réutilisation déclarée → 0 anomalie ;
   dépôt réel → duplicate_assembly_objects == 0), mutations (double non
   déclarée → FAIL ; observé ≠ contrat → FAIL), autorité (le registre doit
   refléter exactement `rendered_method.applications ∩ exercise_order` du
   manifest).
4. Le master `maquette.tex`, les 3 objets, le PDF et la pagination sont
   inchangés : `expected_content_loss = NONE`, PDF avant == PDF après.
