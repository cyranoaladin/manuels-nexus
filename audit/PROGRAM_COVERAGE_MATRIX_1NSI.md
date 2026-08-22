# Matrice programme ↔ manuel — 1NSI (édition 2026-2027)

Recalculée directement contre le texte officiel `MENE1901633A` (BO spécial
n°1 du 22 janvier 2019), extrait par `pdftotext -layout` depuis
`NSI/corpus_nsi/00_programmes_officiels/programme_nsi_premiere.pdf`
(SHA-256 vérifié identique à `docs/programmes/PROGRAMMES_2026_2027.yaml`,
entrée `SRC-BO2019-NSI-PREMIERE`). Détail complet dans
`audit/PROGRAM_COVERAGE_MATRIX_1NSI.json` (52 lignes).

## Chiffres finaux

```
TOTAL_MANDATORY_ATOMS      = 50
STRUCTURALLY_MAPPED        = 49
TRANSVERSAL (hors grille)  = 1   (Histoire de l'informatique — le BO lui-même la décrit comme transversale, pas un chapitre)
FULL                       = 0   (aucun audit scientifique/pédagogique passé — coverage != quality)

Non obligatoire (mandatory=false), 2 lignes :
  OUT_OF_SCOPE_WITH_PROOF  = 1   (limite explicite : norme IEEE-754 non exigible)
  UNSUPPORTED_CLAIM        = 1   (1NSI-TYPES-CONSTRUITS-C5 — mutabilité, absente du texte officiel)
```

Couverture structurelle exceptionnellement propre par rapport à 1SPE :
**49/50 atomes obligatoires (98 %) sont structurellement mappés dès le
premier passage**, avec une correspondance quasi 1:1 entre le référentiel
local (`P-XXX-NN`) et les rubriques du BO. Les 8 chapitres couvrent les 7
rubriques non-transversales du programme (Histoire étant explicitement
transversale par le texte lui-même).

## Une seule trouvaille réelle — `1NSI-TYPES-CONSTRUITS-C5`

`NSI/referentiel/capacites_1NSI_TYPES-CONSTRUITS.json` liste une 5e
capacité : « distinguer types mutables et immuables ; identifier les
effets d'une affectation ou d'un passage en argument ». Recherche
exhaustive (`grep -i "mutable\|immuable"`) sur le texte extrait du PDF
officiel déposé : **zéro occurrence**. La section « Représentation des
données : types construits » du BO ne couvre que p-uplets/tableaux/
dictionnaires (accès, construction, itération) — jamais la sémantique
mutabilité/copie/passage par référence.

`NSI/referentiel/_a_verifier.json` avait déjà repéré un écart partiel sur
cette capacité ("copie, indications, effets" absents du texte officiel")
et conclu à une "formulation YAML paraphrasée, pas une erreur de
programme". Cette vérification indépendante est **plus stricte** : aucune
base textuelle, même paraphrasée, n'a été trouvée — c'est un concept Python
général (mutabilité) enseigné en sus du programme officiel, symétrique à
la trouvaille 1SPE-VARIABLES-ALEATOIRES (loi binomiale absente du BO 2026).

**Aucun contenu supprimé.** Décision éditoriale réelle nécessaire
(reclassifier en approfondissement explicite ou conserver avec
justification pédagogique) — **HUMAN GATE**, pas une correction mécanique.

## Point structurel à noter (pas un gap)

`P-ARCH-04A/04B` (capteurs/actionneurs, IHM matérielle — "Périphériques
d'entrée et de sortie") est placé dans le chapitre **1NSI-RESEAUX**
(`cours/1NSI-RES-COURS-C3.tex`, confirmé par grep positif) plutôt que dans
un chapitre matériel/périphériques dédié. Le BO regroupe architecture +
réseaux + OS + IHM matérielle en une seule section ; le manuel la scinde en
deux chapitres (`1NSI-ARCHITECTURE-OS`, `1NSI-RESEAUX`) sans que le
découpage corresponde exactement aux frontières du texte. La capacité est
réellement couverte — c'est une observation de classification, pas un
vide de contenu.

## Exigence quantitative à vérifier (pas structurelle)

Le BO impose explicitement qu'« au moins un quart de l'horaire » de
première soit réservé à la démarche de projet. Un chapitre
`1NSI-PROJET-METHODES` existe structurellement, mais cette matrice ne
peut pas juger si le volume horaire réel du manuel respecte ce quota — à
vérifier lors de l'audit pédagogique (T3), pas lors de cette passe
structurelle.

## Convention de nommage NSI (note méthodologique)

Contrairement aux manuels de mathématiques (`NN_description.tex`), les
chapitres NSI utilisent deux séries parallèles dans `cours/` :
`PREFIX-COURS-NN.tex` (TD/supports pratiques, ex. « TD 1 — Station météo
connectée ») et `PREFIX-COURS-CN.tex` (cours indexé par capacité). Vérifié
sur `1NSI-TYPES-CONSTRUITS` : ce ne sont PAS des doublons (contenus
distincts, `\section*{}` TD vs `\section{}` cours) — aucun risque de
duplication à corriger ici, contrairement au cas TSPE de T1.4.

## Ce que cette matrice ne couvre pas encore

Audit scientifique (code Python exécuté réellement, complexité,
terminaison, invariants), audit pédagogique, EXAM_ALIGNMENT (1NSI n'a pas
d'épreuve terminale propre — la spécialité n'est évaluée qu'en Terminale),
vérification quantitative du quota horaire projet.
