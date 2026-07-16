# SPECIMEN A VALIDER --- Charte v4

PDF : `build/specimen/specimen.pdf` (5 pages, 68 Ko)

## Changement principal v3.2 -> v4

Le sous-titre de couverture etait code en dur « Manuel NSI Premiere --- Nexus Reussite »
(cls:361). Il est desormais parametre par `\matiere` et `\niveau` :

```latex
\matiere{Mathematiques}\niveau{Premiere specialite}  % => Mathematiques --- Premiere specialite --- Nexus Reussite
\matiere{NSI}\niveau{Premiere}                        % => NSI --- Premiere --- Nexus Reussite
```

Defaut : NSI / Premiere (retro-compatible avec les chapitres NSI existants).
Les gabarits `chapitre_master.tex` fixent la matiere pour chaque projet.

## Invariants preserves

- Noms et signatures d'environnements inchanges (nxdef, nxthm, nxprop, nxerr, nxstar,
  nxcard, fmbox, fichemethode, exercice, corrige, codereference, python, console,
  evaluation, miniprojet, ouverturechapitre).
- Losanges de parcours (parcoursUn, parcoursDeux, parcoursTrois) conserves.
- Moteur LuaLaTeX obligatoire (\RequireLuaTeX).
- Polices embarquees (Libertinus, Montserrat, JetBrains Mono).

## Gate visuel (5 cibles compilees)

| Cible | Pages | Ko | Sous-titre couverture | Verdict |
|---|---:|---:|---|---|
| 1SPE-SUITES | 77 | 462 | Mathematiques --- Premiere specialite --- Nexus Reussite | PASS |
| 1SPE-SECOND-DEGRE | 61 | 349 | Mathematiques --- Premiere specialite --- Nexus Reussite | PASS |
| 1NSI-TYPES-CONSTRUITS | 34 | 213 | (pas d'ouverture dans le maitre) | PASS |
| Specimen maths | 5 | 68 | NSI --- Premiere --- Nexus Reussite | PASS |

## Tests

- `test_nexus_class_has_no_hardcoded_subject_label` : PASS
- `make test` maths : 343 pass
- `make test` NSI : 214 pass
- `check_charte_sync` : 7/7 identiques

## Decision requise

Valider la charte v4 (parametrage matiere/niveau).
Pause non bloquante : la production (PHASE C) peut enchainer immediatement.
