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

## Architecture proposee (6 chapitres) — A_VALIDER_HUMAIN

| # | Chapitre | Contenu BO | Taille relative |
|---|---|---|---|
| 1 | TEXP-COMPLEXES-ALGEBRE-GEOMETRIE | Point de vue algebrique + geometrique | ~1 chapitre standard |
| 2 | TEXP-COMPLEXES-TRIGO-POLYNOMES | Trigonometrie/Euler-Moivre + equations polynomiales | ~1 chapitre standard |
| 3 | TEXP-ARITHMETIQUE-DIVISIBILITE | Division euclidienne, congruences, Euclide/PGCD, Bezout, Gauss | ~1 chapitre standard |
| 4 | TEXP-ARITHMETIQUE-PREMIERS | Nombres premiers, applications (RSA, etc. si approfondissement) | option : fusionner avec #3 |
| 5 | TEXP-GRAPHES | Vocabulaire des graphes, connexite, graphe complet | ~1 chapitre standard |
| 6 | TEXP-MATRICES-MARKOV | Calcul matriciel, suites de matrices, chaines de Markov | ~1 chapitre standard |

**Points ouverts A_VALIDER_HUMAIN** :
- Fusionner #3+#4 en un seul chapitre "Arithmetique" (BO ne les separe pas
  explicitement — 1 bloc de taille comparable a 1 chapitre standard) →
  architecture a 5 chapitres si fusion.
- Fusionner #5+#6 en un seul chapitre "Graphes et matrices" (titre du BO
  lui-meme, themes deliberement entrelaces) → architecture a 4 chapitres si
  double fusion. C'est l'option la plus fidele au decoupage BO litteral ; le
  decoupage a 6 proposee ci-dessus suit plutot la granularite deja en usage
  dans TSPE (1 chapitre par sous-bloc de taille comparable, ex. derivation
  global/local en 1SPE).

## Prerequis avant LOT 0 du premier chapitre

1. Texte BO depose : **fait** (`sources/txt/BO2019_TEXPERTES_optionnel.txt`).
2. Extraction des capacites vers `referentiel/capacites_TEXPERTES_*.json` : **a faire**.
3. Validation humaine du decoupage en chapitres (4, 5 ou 6 selon fusions
   ci-dessus) : **A_VALIDER_HUMAIN**.
4. Manuel independant (option en plus de la specialite, public restreint et
   ambitieux) — recommande separe du manuel TSPE specialite, a valider.

## Workflow

Meme pipeline que 1SPE/TSPE : LOT 0 a LOT 7, memes gates (VERIFY, resolution
aveugle A+B, compilation, PNG, tag, CI verte).
