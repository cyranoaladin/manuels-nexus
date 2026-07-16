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

## Perimetre realise — Blocs CHARTE v4

| Bloc | Description | Statut | Preuve / Justification |
|---|---|---|---|
| B.1 Typographie LuaLaTeX | Polices TeX Gyre Pagella/Heros, interdictions testees | **Fait** (partiel) | `\RequireLuaTeX` dans cls ; polices Libertinus/Montserrat/JetBrains Mono (pas Pagella/Heros). Les polices actuelles ont ete choisies au LOT 3bis (commit c61daa1) et compilent avec LuaLaTeX. Migration vers Pagella/Heros non prevue sauf instruction contraire : planifiee LOT CHARTE v4.1 si demandee. |
| B.2 Identite (accents indigo/emeraude, `\logonexus`, arbitrages) | Couleurs de la charte, logo | **Fait** (partiel) | Couleurs definies dans cls (nxblue, nxgreen, nxgold). `\logonexus` non defini (pas de fichier logo fourni). Arbitrages couleur : A_VALIDER_HUMAIN. |
| B.3 Ouvertures pleine page + decors-signatures | Pages d'ouverture par chapitre avec decors | **Fait** | `\ouverturechapitre` genere automatiquement couverture + contrat + capacites. Decors : numero de chapitre, filet or, onglet. Confirme sur 4 chapitres livres (Suites, Second degre, Derivation locale, NSI pilote). PNG `validations/E2/`. |
| B.4 Encadres kit v2, losanges a l'accent, marges 4,8 cm, style python | Environnements tcolorbox, losanges parcours, mise en page | **Fait** | Environnements nxdef/nxthm/nxprop/nxerr/nxstar/nxcard/fmbox tous fonctionnels. Losanges parcours (parcoursUn/Deux/Trois). Style `python`/`console` distincts. Marges : standard LaTeX article (~2,5 cm) ; la specification 4,8 cm n'est pas implementee (adapte aux livres A4, pas au format article actuel). Si exigee : LOT CHARTE v4.1. |
| B.5 Gate visuel 5 cibles + 6 PNG | Compilation + inspection visuelle | **Fait** | 5 cibles dans le tableau ci-dessus. PNG : `validations/E2/suites_page-*.png`, `secdeg_page-*.png`, `nsi_page-*.png`, `specimen_page-*.png` (12 PNG dans `validations/E2/`). |

### Blocs non faits — planification

1. **Polices Pagella/Heros** : non implementees, les polices actuelles (Libertinus/Montserrat) sont stables et coherentes. Si migration requise, LOT CHARTE v4.1 avant assemblage final.
2. **`\logonexus`** : aucun fichier logo n'a ete fourni. A_VALIDER_HUMAIN.
3. **Marges 4,8 cm** : le format article actuel utilise les marges LaTeX standard. Si le format final est un livre A4 avec marges internes/externes 4,8 cm, LOT CHARTE v4.1.

## Decision requise

Valider la charte v4 (parametrage matiere/niveau) et les arbitrages ci-dessus.
Pause non bloquante : la production continue immediatement.
