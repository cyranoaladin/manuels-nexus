# Roadmap — Collection Terminale (Mathematiques + NSI)

Statut : **cadrage initial, aucun LOT 0 demarre**. Ce document consolide l'etat
des 4 manuels vises et les points necessitant une validation humaine avant
de commencer la production (mode strict LOT-par-LOT, cf. decision du 2026-08-05).

Branche : `terminale/collection-v1`, worktree `.worktrees/terminale-collection-v1`,
issue de `finalisation/collection-v1` (207+ commits d'outillage/remediation 1SPE
deja presents). Le chantier de remediation NO-GO du manuel 1SPE (voir
`AGENTS.md`) reste un chantier separe, mene en parallele sur ses propres
branches — non traite ici.

## Vue d'ensemble des 4 manuels

| Manuel | Programme | BO source | Referentiel capacites | Chapitres rediges | Doc de cadrage |
|---|---|---|---|---|---|
| Maths specialite Terminale (TSPE) | 2019, arrete MENE1921262A | depose | 12/12 fichiers extraits (dont 2 hors-perimetre a retirer, corrige) | 3 amorces, non assembles | `Mathematiques/manuel-maths/docs/10_perimetre_terminale.md` |
| Maths complementaires Terminale | 2019, arrete MENE1921265A | depose ce jour | 0/9 — a extraire | 0 | `Mathematiques/manuel-maths/docs/11_perimetre_terminale_complementaires.md` |
| Maths expertes Terminale | 2019, arrete MENE1921264A | depose ce jour | 0/6 — a extraire | 0 | `Mathematiques/manuel-maths/docs/12_perimetre_terminale_expertes.md` |
| NSI Terminale (TNSI) | 2019, arrete MENE1921247A | deja depose, verifie ce jour | 6/6 fichiers extraits (metadonnee BO a corriger) | 0 | `NSI/docs/11_perimetre_terminale.md` |

Total actuellement projete : **10 + 9 + 4-6 + 6 = 29 a 31 chapitres**, chacun
suivant le pipeline 8 LOTs (contrat, corpus, curation, cours, exercices, QCM,
evaluation, assemblage) avec arret de validation humaine a chaque LOT.

## Corrections apportees lors de ce cadrage (2026-08-05)

1. **TSPE specialite** : retrait des chapitres "Nombres complexes" et
   "Arithmetique" (non-conformite programme, verifiee par recherche textuelle
   exhaustive dans le BO deja depose — zero occurrence). Ces notions relevent
   exclusivement de Maths expertes. Le perimetre passe de 12 a 10-11 chapitres
   selon le sort de TSPE-CONCENTRATION-LGN (fusion ou non avec Probabilites).
2. **Maths complementaires / Maths expertes** : programmes officiels non
   presents dans le depot. Recuperes ce jour depuis education.gouv.fr /
   eduscol.education.gouv.fr (PDF officiels, sources publiques,
   `usage_policy: adaptation_attribution` au sens de `sources/registry.yaml`),
   extraits en texte et deposes dans `sources/txt/`, references ajoutees a
   `sources/SOURCES.md` avec SHA-256.
3. **NSI Terminale** : le PDF source etait deja correctement enregistre dans
   `NSI/sources/SOURCES.md` (SHA-256 verifie identique au fichier recupere ce
   jour). En revanche les 6 fichiers `referentiel/capacites_TNSI_*.json`
   portent une metadonnee `bo_reference` erronee (copiee du gabarit 1NSI,
   citant le mauvais BO). Non corrigee ici — modification de `referentiel/*`
   interdite sans instruction explicite.

## Decisions necessaires avant tout LOT 0 (A_VALIDER_HUMAIN)

1. **Perimetre TSPE specialite corrige** (10 vs 11 chapitres) — valider
   `10_perimetre_terminale.md`.
2. **Decoupage en chapitres de Maths complementaires** (9 chapitres proposes,
   un par theme d'etude BO) — valider `11_perimetre_terminale_complementaires.md`.
3. **Decoupage en chapitres de Maths expertes** (4, 5 ou 6 chapitres selon
   fusions Arithmetique et Graphes/Matrices) — valider `12_perimetre_terminale_expertes.md`.
4. **Decoupage en chapitres NSI Terminale** (6 proposes, granularite
   Structures de donnees / Langages a trancher) — valider `NSI/docs/11_perimetre_terminale.md`.
5. **Correction de la metadonnee `bo_reference`** dans les 6
   `referentiel/capacites_TNSI_*.json` — autorisation explicite requise.
6. **Sort des 3 chapitres TSPE deja amorces** (`TSPE-SUITES-LIMITES`,
   `TSPE-LIMITES-FONCTIONS`, `TSPE-DERIVATION-CONVEXITE`) : reprendre en l'etat,
   auditer d'abord (contenu potentiellement produit avant les gates actuels de
   `finalisation-collection-v1`), ou repartir de zero ?
7. **Ordre de production** entre les 4 manuels — proposition par defaut :
   TSPE specialite d'abord (le plus avance, le plus gros volume d'eleves),
   puis NSI Terminale (referentiel deja pret), puis Complementaires, puis
   Expertes (public le plus restreint). A confirmer ou reordonner.
8. **Manuels separes ou variante d'un meme manuel** pour complementaires et
   expertes (recommandation : manuels independants, publics et programmes
   disjoints de la specialite) — a confirmer.

## Prochaine etape (apres validation de ce cadrage)

LOT 0 du premier chapitre du premier manuel valide : `contrat.yaml` depuis le
referentiel, puis arret pour validation humaine du contrat (regle CLAUDE.md
§3, mode strict LOT-par-LOT choisi par l'utilisateur).
