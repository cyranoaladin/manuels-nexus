# A4 — Réconciliation des cibles méthodes (lot de clôture)

Campagne mesurée entre `2852cb67` (scellement du jeu de cibles N=59, inbound 470)
et le HEAD courant. Toutes les valeurs ci-dessous sont **mesurées** (git diff,
rendus d'inventaire aux deux SHA, lecture des META et des contrats) — aucune
n'est reprise d'un rapport antérieur. Détail ligne à ligne dans
`A4_METHOD_TARGET_RECONCILIATION.json`.

## Signification des nombres entre parenthèses (somme 66)

Les nombres du rapport de campagne (INEGALITES 5, ... MATRICES-MARKOV 7,
somme 66) comptent les **fiches traitées par lot** = fichiers créés **+**
réécritures des M1 contaminées. Ce ne sont **pas** des nombres de cibles
manquantes produites.

Décomposition mesurée de la campagne complète :

| Population | Nombre |
|---|---|
| Fichiers méthode **créés** (git `A`) | 70 |
| — dont cibles du jeu initial N=59 | 58 |
| — dont complétions de règle C_i↔M_i (capacités C6+ sans ref entrante) | 11 |
| — dont remplacement de la cible mal étiquetée TRIGO M3→M4 | 1 |
| Fichiers méthode **réécrits** (git `M`, M1 contaminées « Dériver une fonction composée ») | 15 |
| **Total fiches touchées** | **85** |

Les 66 du rapport = 55 créations + 11 réécritures M1 sur les 11 lots listés ;
les 19 restantes (TRIGO 1, ADGK 3, CALCULS-AIRES 5, ECHANTILLONNAGE 5,
CORRELATION 5) appartiennent aux lots antérieurs de la même campagne.

## Métriques exigées

| Métrique | Valeur | Exigence | Verdict |
|---|---|---|---|
| ORIGINAL_TARGET_SET_SIZE | 59 | — | — |
| CREATED_TARGETS_FROM_ORIGINAL_SET | 58 | — | — |
| ORIGINAL_TARGETS_NOT_CREATED | **0** | 0 | PASS |
| ORIGINAL_TARGETS_SUPERSEDED | 1 (TRIGO M3→M4, preuve `813304c6`) | explicite | PASS |
| CREATED_METHODS_OUTSIDE_ORIGINAL_SET | 12 (11 + 1, toutes expliquées) | expliquées | PASS |
| DUPLICATE_METHOD_IDS | **0** | 0 | PASS |
| METHODS_WITHOUT_CANONICAL_CAPACITY | **0** | 0 | PASS |
| UNKNOWN (explications) | **0** | 0 | PASS |

### Cible supersédée (1) — preuve

`1SPE-TRIGONOMETRIE:M3` : les 3 objets référents (EX-024, EX-024-CDP, CO-024)
portaient `C3/M3` par erreur d'étiquetage ; la capacité réellement travaillée
(résoudre cos(x)=a) est C4. Commit `813304c6` : création de la fiche M4 et
retag `C3/M3 → C4/M4` des 3 objets. Aucune référence supprimée.

### Hors jeu initial (12) — classes

- `NEWLY_DISCOVERED_VALID_TARGET` (11) : MF M6-M7, ATT M6, ARI M6-M9,
  CTP M6-M7, MAT M6-M7 — capacités canoniques des contrats (C6+) sans
  référence entrante cassée au snapshot (aucun exercice ne les référençait
  encore), mais exigées par la règle conservée « une fiche méthode par
  capacité C_i↔M_i ».
- `OTHER_EXPLICIT` (1) : TRIGO M4 (remplacement du mis-tag, ci-dessus).
- `UNKNOWN` : 0.

### Réécritures (15)

Les 14 M1 TCOMPL/TEXP + ADGK M1 recensées dans
`A4_CONTAMINATED_M1_FICHES.json` (contenu identique « Dériver une fonction
composée » sans rapport avec C1). Classe :
`REPLACEMENT_OF_INVALID_PREEXISTING_METHOD`. Statut redescendu
`approved → needs_review`, anciens contenus préservés dans l'historique git.

## Les 470 références entrantes

Fingerprints pré-campagne reconstruits par un **rendu d'inventaire réel au SHA
`2852cb67`** (clone dédié, branche d'origine) : 470 `broken_meta_references`
exactement, locators `(source, champ, cible)` conservés dans le JSON.

| Métrique | Valeur |
|---|---|
| TOTAL | 470 |
| RESOLVED | **470** |
| — dont résolues par création de la cible | 467 |
| — dont reclassées avec preuve (TRIGO M3→M4, commit `813304c6`) | 3 |
| UNRESOLVED | **0** |
| Références supprimées pour forcer broken_meta=0 | **0** |

Contrôle croisé : le rendu d'inventaire au HEAD courant donne
`broken_meta_references = 0` ; aucun des 470 locators pré-campagne ne figure
dans le rendu courant.

## Addendum — lot de clôture (§8)

La réconciliation de clôture a mesuré l'invariant bidirectionnel C_i↔M_i sur
les 51 chapitres à contrat et révélé **4 capacités du périmètre campagne sans
fiche** : `1SPE-TRIGONOMETRIE` C3 et C5 (capacités canoniques du référentiel
BO, restaurées au contrat par A4.7a `d9cbe5f7`), `TCOMPL-CALCULS-AIRES` C6 et
`TCOMPL-ECHANTILLONNAGE` C6 (capacités de démonstration sans référence
entrante au snapshot — invisibles du jeu dérivé des références cassées).

Ces 4 fiches ont été produites APRÈS réconciliation et inventaire (le STOP de
production était borné « avant réconciliation et inventaire ») par le pipeline
standard : pré-vérification SymPy, blocs VERIFY exécutés réellement, packets,
`needs_review`, qualification EXPECTED_REVIEW_DEBT par la politique de classe.
Totaux finaux : **89 fiches** (59 cibles originales − 1 supersédée + 15
réécritures + 11 complétions de règle + 4 complétions de clôture + 1
remplacement du mis-tag).

Cas TRIGO M3 : la CIBLE M3 du jeu initial (issue de refs mal étiquetées) a été
supersédée par M4 ; la FICHE M3 existe désormais au titre de la capacité
canonique C3 elle-même (deux faits distincts, tous deux tracés).

Invariant final périmètre campagne (16 chapitres) : **1:1 PASS** — chaque
capacité du contrat a exactement une fiche, chaque fiche exactement une
capacité, 0 alias dupliqué, 0 référence méthode non résolue (repo entier).

## Dette résiduelle HORS périmètre (mesurée, non touchée — §17 prochain lot)

22 chapitres / 131 fiches méthodes manquantes (TSPE 8 chapitres/41, 1NSI 8/38,
TNSI 6/52) + 1 anomalie inverse (`TSPE-CONTINUITE` : M3-M5 sans capacité au
contrat). Détail dans le JSON (`bidir_invariant`). Le prochain lot de dette
n'est PAS démarré.
