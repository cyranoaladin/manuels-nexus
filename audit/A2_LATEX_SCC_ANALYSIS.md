# A2 LaTeX Strongly Connected Components (SCC) Analysis

Analyse des 10 anomalies `latex_cycles` historiques et de leur résolution.

> Corrigé le 2026-08-18 suite au diagnostic de provenance
> (`audit/PROVENANCE_CORRECTION_1361cf37.md`). La version précédente de ce
> rapport attribuait la résolution au lot A2 et parlait de « canonical class
> redirection » sans identifier de commit. Les faits ci-dessous sont établis
> par reproduction hermétique.

## Résultat reproduit (SHA 9ddcffee, deux worktrees frais, A == B)

- **FULL_REPOSITORY_LATEX_GRAPH — SCC cycliques** : `0`
- **PRODUCTION_REACHABLE_LATEX_GRAPH — SCC cycliques** : `0`
- **Topologie** : DAG strict sur l'ensemble du graphe analysé.

L'objectif release (`PRODUCTION_GRAPH cyclic SCC = 0`) est atteint, et le
graphe complet (fixtures, prototypes, archives inclus) est également acyclique.

## Nature réelle du défaut

Les 10 anomalies partageaient **un unique motif de défaut**, dupliqué dans
2 fichiers sources :

- `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls`
- `NSI/gabarits/nexus-manuel.cls`

Ces wrappers contenaient un fallback littéral auto-référentiel :

```tex
\IfFileExists{...}{...}{\input{nexus-manuel.cls}}  % auto-référence
```

L'analyseur résolvait `nexus-manuel.cls` vers le wrapper lui-même → self-loop
SCC. Le défaut était réel dans le graphe source (auto-inclusion littérale),
mais latent à l'exécution LaTeX (branche uniquement atteinte si la classe
canonique `gabarits/common/nexus-manuel.cls` est absente).

- **Commit de correction** : `fed6d28a` (2026-08-16, lot A1,
  « resolve all 5 A1 broken_latex_references ») — suppression du fallback
  auto-référentiel dans les 2 wrappers.
- **Changement de source dans le lot A2** : AUCUN (aucun `.tex/.sty/.cls`
  modifié entre `1361cf37` et `9ddcffee`). A2 est un lot de vérification et
  de documentation.
- **Faux positifs d'analyseur** : 0 (l'auto-inclusion existait littéralement).

## Décomposition des 10 surfaces d'anomalie

Un défaut par fichier wrapper (2 défauts sources) apparaissait sur 10 champs
d'assemblage statique (un par point d'entrée `.tex` dont le graphe atteint le
wrapper) :

| # | Champ | Portée | Défaut source | Corrigé par |
| --- | --- | --- | --- | --- |
| 1 | `math:static:.../build/maquette-v5/maquette.tex` | PRODUCTION_REACHABLE | wrapper maths | `fed6d28a` |
| 2 | `math:static:.../gabarits/chapitre_master.tex` | PRODUCTION_REACHABLE | wrapper maths | `fed6d28a` |
| 3 | `math:static:.../gabarits/objet_standalone.tex` | PROTOTYPE_ONLY | wrapper maths | `fed6d28a` |
| 4 | `math:static:.../gabarits/specimen-pont-v6.tex` | FIXTURE_ONLY | wrapper maths | `fed6d28a` |
| 5 | `math:static:.../gabarits/specimen-v6.tex` | FIXTURE_ONLY | wrapper maths | `fed6d28a` |
| 6 | `math:static:.../gabarits/specimen.tex` | ARCHIVE_ONLY | wrapper maths | `fed6d28a` |
| 7 | `nsi:static:NSI/gabarits/book_master.tex` | FIXTURE_ONLY | wrapper NSI | `fed6d28a` |
| 8 | `nsi:static:NSI/gabarits/chapitre_master.tex` | FIXTURE_ONLY | wrapper NSI | `fed6d28a` |
| 9 | `nsi:static:NSI/gabarits/objet_standalone.tex` | PROTOTYPE_ONLY | wrapper NSI | `fed6d28a` |
| 10 | `nsi:static:NSI/gabarits/specimen.tex` | ARCHIVE_ONLY | wrapper NSI | `fed6d28a` |

Nomenclature officielle (arbitrage 2026-08-18) :

- **A1 : wrapper self-reference defect = FIXED** (commit `fed6d28a`).
- **A2 : stale cycle-report reconciliation = COMPLETED** (aucun changement
  de source ; réconciliation du rapport stale et vérification hermétique).
- **real production root causes = 1** (motif fallback auto-référentiel).
- **affected production wrapper files = 2**.
- **inventory surfaces/fingerprints = 10** (dont 2 production-reachable,
  4 fixture, 2 prototype, 2 archive).
- **current cycles = 0** (graphe complet ET graphe production).
- Les 10 surfaces ne doivent PAS être présentées comme dix défauts release
  distincts, et A2 ne doit pas être présenté comme ayant corrigé dix défauts.

## Pourquoi l'ancien rapport annonçait encore « 10 cycles »

L'ancien décompte provenait de `audit/INVENTAIRE_COLLECTION.json` committé,
généré AVANT `fed6d28a` et jamais régénéré/committé depuis. Toute analyse
fraîche postérieure à `fed6d28a` donne 0 cycle. Voir
`audit/PROVENANCE_CORRECTION_1361cf37.md`.

## Invariant d'architecture

L'invariant `common -> discipline -> manual` est préservé sans référence
arrière : vérifié sur le graphe frais reproduit (SCC max = 1, aucune arête de
retour vers `gabarits/common`).
