# Perimetre Terminale — enseignement optionnel Mathematiques expertes

## Source reglementaire

Arrete MENE1921264A, BO special n 8 du 25 juillet 2019, application rentree 2020.
Texte depose : `sources/txt/BO2019_TEXPERTES_optionnel.txt` (extrait
`pdftotext -layout`, depose le 5 aout 2026, cf. `sources/SOURCES.md`).

Public cible : eleves ayant garde la specialite mathematiques en terminale et
visant des formations a forte dominante mathematique (CPGE, etc.). S'ajoute
**en plus** de la specialite (pas un substitut).

**Important — perimetre historiquement mal attribue** : les nombres complexes et
l'arithmetique avaient ete listes par erreur dans le perimetre de la
*specialite* (`10_perimetre_terminale.md`, chapitres 11-12, corriges le
2026-08-05). Verification faite : ces deux themes, ainsi que les graphes et
matrices, sont exclusivement au programme de **Mathematiques expertes** et n'apparaissent
pas dans `BO2019_TSPE_specialite.txt`.

## Structure du programme (BO)

3 grands themes, chacun subdivise en sous-parties par le texte officiel lui-meme :

### 1. Nombres complexes (4 sous-parties BO)
- Point de vue algebrique (ensemble ℂ, operations, conjugaison, binome)
- Point de vue geometrique (affixe, module, argument, forme trigonometrique)
- Nombres complexes et trigonometrie (formules d'Euler/Moivre, forme exponentielle)
- Equations polynomiales (factorisation, racines, degre)

### 2. Arithmetique (bloc unique BO)
Division euclidienne dans ℤ, congruences et compatibilite avec les operations,
algorithme d'Euclide/PGCD, theoreme de Bezout, theoreme de Gauss, nombres
premiers (infinitude, recherche de nombres premiers particuliers).

### 3. Graphes et matrices (bloc unique BO, deliberement entrelace)
Graphes (sommets, aretes, degre, chaines, connexite), matrices (operations,
inverse, puissances), representations matricielles, suites de matrices,
chaines de Markov (2-3 etats), marches aleatoires sur un graphe.

## Architecture retenue (5 chapitres) — decidee le 2026-08-06

| # | Chapitre | Contenu BO | Referentiel |
|---|---|---|---|
| 1 | TEXP-COMPLEXES-ALGEBRE-GEOMETRIE | Point de vue algebrique + geometrique | `capacites_TEXPERTES_COMPLEXES-ALGEBRE-GEOMETRIE.json` (5 capacites) |
| 2 | TEXP-COMPLEXES-TRIGO-POLYNOMES | Trigonometrie/Euler-Moivre + equations polynomiales + geometrie | `capacites_TEXPERTES_COMPLEXES-TRIGO-POLYNOMES.json` (7 capacites) |
| 3 | TEXP-ARITHMETIQUE | Divisibilite, congruences, Euclide/PGCD, Bezout, Gauss, nombres premiers, Fermat | `capacites_TEXPERTES_ARITHMETIQUE.json` (9 capacites) |
| 4 | TEXP-GRAPHES | Vocabulaire des graphes, matrice d'adjacence, denombrement de chemins | `capacites_TEXPERTES_GRAPHES.json` (5 capacites) |
| 5 | TEXP-MATRICES-MARKOV | Calcul matriciel, suites de matrices, chaines de Markov | `capacites_TEXPERTES_MATRICES-MARKOV.json` (7 capacites) |

**Decision** (tranchee dans le cadre de la mission "aller jusqu'au bout") :
fusion #3+#4 retenue (Arithmetique = 1 seul chapitre, conforme au bloc
unique du BO) ; fusion #5+#6 **non** retenue -- Graphes et Matrices/Markov
restent 2 chapitres distincts malgre l'entrelacement du BO, pour rester a
une granularite geree (chaque chapitre a 5-9 capacites, comparable aux
autres manuels de la collection). Repartition des capacites du bloc unique
« Graphes et matrices » entre les deux fichiers referentiel tracee et
justifiee dans la note de chaque fichier JSON.

## Prerequis avant LOT 0 du premier chapitre

1. Texte BO depose : **fait** (`sources/txt/BO2019_TEXPERTES_optionnel.txt`).
2. Extraction des capacites vers `referentiel/capacites_TEXPERTES_*.json` :
   **fait** (2026-08-06, 5/5 fichiers).
3. Decoupage en 5 chapitres : **decide** (cf. tableau ci-dessus).
4. Manuel independant (option en plus de la specialite, public restreint et
   ambitieux) — retenu, separe du manuel TSPE specialite.

## Workflow

Meme pipeline que 1SPE/TSPE : LOT 0 a LOT 7, memes gates (VERIFY, resolution
aveugle A+B, compilation, PNG, tag, CI verte).
