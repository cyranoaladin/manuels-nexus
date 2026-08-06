# Perimetre Terminale — enseignement optionnel Mathematiques complementaires

## Source reglementaire

Arrete MENE1921265A, BO special n 8 du 25 juillet 2019, application rentree 2020.
Texte depose : `sources/txt/BO2019_TCOMPL_optionnel.txt` (extrait `pdftotext -layout`
d'apres le PDF eduscol officiel, depose le 5 aout 2026, cf. `sources/SOURCES.md`).

Public cible (texte du preambule) : eleves ayant suivi la specialite mathematiques
en premiere et ne la poursuivant pas en terminale, mais devant renforcer leurs
competences mathematiques pour des poursuites d'etudes (medecine, economie,
sciences sociales notamment).

## Structure du programme (BO)

Le texte officiel est organise en **9 themes d'etude** transversaux, puis un
recapitulatif des notions par grand domaine ("Contenus" : Analyse, Probabilites
et statistique, Algorithmique et programmation, Vocabulaire ensembliste et
logique) — meme logique que le programme de specialite (domaines transversaux,
pas de decoupage en chapitres impose par le BO).

## Architecture proposee (9 chapitres, un par theme d'etude) — A_VALIDER_HUMAIN

| # | Chapitre | Theme BO 2019 |
|---|---|---|
| 1 | TCOMPL-MODELES-FONCTION | Modeles definis par une fonction d'une variable |
| 2 | TCOMPL-MODELES-EVOLUTION | Modeles d'evolution (suites, algorithmique) |
| 3 | TCOMPL-LOGARITHME-HISTORIQUE | Approche historique de la fonction logarithme |
| 4 | TCOMPL-CALCULS-AIRES | Calculs d'aires (primitives, integrales) |
| 5 | TCOMPL-INEGALITES | Repartition des richesses, inegalites |
| 6 | TCOMPL-INFERENCE-BAYESIENNE | Inference bayesienne |
| 7 | TCOMPL-ECHANTILLONNAGE | Repetition d'experiences independantes, echantillonnage |
| 8 | TCOMPL-TEMPS-ATTENTE | Temps d'attente (loi exponentielle) |
| 9 | TCOMPL-CORRELATION-CAUSALITE | Correlation et causalite |

Chaque theme mobilise plusieurs domaines transversaux (ex. Temps d'attente ⇒
Analyse + Probabilites + Algorithmique) : le contrat.yaml de chaque chapitre
(LOT 0) devra tracer explicitement quelles capacites de quel domaine BO il
couvre, pour garantir la couverture totale des 4 domaines "Contenus" a l'echelle
du manuel complet (pas forcement 1 pour 1 par chapitre).

## Prerequis avant LOT 0 du premier chapitre

1. Texte BO depose : **fait** (`sources/txt/BO2019_TCOMPL_optionnel.txt`).
2. Extraction des capacites vers `referentiel/capacites_TCOMPL_*.json` (un
   fichier par theme, meme format que `capacites_TSPE_*.json`) : **fait**
   (2026-08-06, 9/9 fichiers, capacites extraites des rubriques "Capacites
   attendues"/"Contenus" du BO et rattachees a chaque theme via ses
   "Contenus associes" ; INEGALITES et INFERENCE-BAYESIENNE n'ont pas de
   rubrique "Capacites attendues" propre dans le BO -- capacites
   construites a partir du descriptif et des problemes possibles du theme,
   combines aux capacites des sections Contenus pertinentes, note tracee
   dans chaque fichier).
3. Validation de la liste de 9 chapitres ci-dessus : validee (correspondance
   1:1 avec les 9 themes d'etude du BO, aucun decoupage alternatif justifie).
4. Decision : manuel independant (`TCOMPL-*`), le public et le programme
   etant disjoints de la specialite (eleves n'ayant pas garde la
   specialite) — retenu.

## Workflow

Meme pipeline que 1SPE/TSPE : LOT 0 a LOT 7, memes gates (VERIFY, resolution
aveugle A+B, compilation, PNG, tag, CI verte).
