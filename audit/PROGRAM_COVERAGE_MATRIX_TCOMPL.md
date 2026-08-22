# Matrice programme ↔ manuel — TCOMPL (mathématiques complémentaires, édition 2026-2027)

Recalculée directement contre le texte officiel `MENE1921265A` (BO spécial
n°8 du 25 juillet 2019, programme inchangé pour 2026-2027 — le nouveau
texte 2026 MENE2902920A n'entre en application qu'en 2027-2028), déposé et
empreinté sous
`Mathematiques/manuel-maths/sources/txt/BO2019_TCOMPL_optionnel.txt`
(`sha256:dad0e4941fc0eb7e93a727bfabd49b3298b1e378eafb7fbe1bbdee35b9c4ac27`,
vérifié identique à `docs/programmes/PROGRAMMES_2026_2027.yaml`). Détail
complet dans `audit/PROGRAM_COVERAGE_MATRIX_TCOMPL.json` (56 lignes).

## Chiffres finaux

```
TOTAL_MANDATORY_ATOMS      = 53
STRUCTURALLY_MAPPED        = 50   (capacité + fichier(s) cours identifiés — FULL=0, revue scientifique/pédagogique non faite)
FULL                       = 0
PARTIAL                    = 1    (approche intuitive de la limite / théorème des gendarmes — pas nommément repris comme capacité C1-C5 dédiée)
MISSING                    = 0
TRANSVERSAL (hors grille)  = 2    (vocabulaire ensembliste/logique, algorithmique — le BO lui-même les déclare transversaux, pas des chapitres)

Non obligatoire (3 lignes) :
  OUT_OF_SCOPE_WITH_PROOF  = 3    (histoire des mathématiques, exemples d'algorithme, remarque lexicale "démonstration possible" vs "exigible")
  WRONG_YEAR                = 0
  UNSUPPORTED_CLAIM         = 0
```

Aucune trouvaille WRONG_YEAR ni UNSUPPORTED_CLAIM pour TCOMPL — contraste
net avec 1SPE (où le nouveau programme 2026 a créé un vrai risque de
dérive). Le référentiel TCOMPL est structuré par les **9 thèmes d'étude**
du BO (`CALCULS-AIRES`, `CORRELATION-CAUSALITE`, `ECHANTILLONNAGE`,
`INEGALITES`, `INFERENCE-BAYESIENNE`, `LOGARITHME-HISTORIQUE`,
`MODELES-EVOLUTION`, `MODELES-FONCTION`, `TEMPS-ATTENTE`), correspondance
directe et fidèle aux neuf thèmes officiels ("Modèles d'une fonction d'une
variable", "Modèles d'évolution", "Approche historique du logarithme",
"Calculs d'aires", "Répartition des richesses, inégalités", "Inférence
bayésienne", "Répétition d'expériences...échantillonnage", "Temps
d'attente", "Corrélation et causalité").

## Particularité méthodologique — capacités groupées par fichier

Contrairement à 1SPE (un fichier `cours/` par capacité), TCOMPL regroupe
plusieurs capacités dans un même fichier (`% META capacites_codes:
["C1","C2"]`, `["C3","C6"]`, etc.). Vérifié explicitement avant de conclure
à tort à des capacités manquantes (ex. `TCOMPL-INEGALITES` n'a que 3
fichiers `cours/` pour 5 capacités déclarées — les 5 sont bien réparties
dans ces 3 fichiers, confirmé par inspection directe des en-têtes `% META`,
pas une absence de contenu).

## Point à trancher (PARTIAL)

**MODELES-EVOLUTION** : le BO liste, dans "Suites numériques, modèles
discrets" → Contenus, une approche intuitive de la limite d'une suite
(opérations sur les limites, passage à la limite dans les inégalités,
théorème des gendarmes) en plus des capacités calculatoires (C1-C5 du
référentiel, qui couvrent modélisation, calcul de limite géométrique,
représentation graphique, récurrence arithmético-géométrique, équation
différentielle). Cette partie "Contenus" plus qualitative (gendarmes,
opérations sur les limites) n'apparaît pas nommément comme une capacité
C1-C5 dédiée — à vérifier lors de l'audit de contenu si elle est traitée
en cours sans être individuellement trackée, ou réellement absente.

## Observation lexicale — "démonstration possible" vs "exigible"

Le texte TCOMPL 2019 utilise systématiquement "Démonstration(s) possible(s)"
partout où le BO 1SPE 2026 utilise "Démonstration(s) exigible(s)". Signalé
comme `EXPLICIT_LIMITATION`, non tranché ici : à confirmer lors de l'audit
pédagogique si cette différence lexicale a une portée réglementaire réelle
(obligation atténuée) ou est un simple choix de rédaction du texte 2019.

## Ce que cette matrice ne couvre pas encore

Audit scientifique (exactitude des démonstrations/calculs/simulations
Python), audit pédagogique (progression, qualité des exercices),
EXAM_ALIGNMENT (TCOMPL évalué en contrôle continu, MENE2215445N, coefficient
2 — pas d'épreuve terminale spécifique à aligner).

## Prochaine étape

TSPE, TEXPERTES, 1NSI, TNSI.
