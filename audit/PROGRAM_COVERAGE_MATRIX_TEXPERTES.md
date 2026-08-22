# Matrice programme ↔ manuel — TEXPERTES (édition 2026-2027)

Recalculée directement contre le texte officiel `MENE1921264A` (BO spécial
n°8 du 25 juillet 2019), déposé et empreinté sous
`Mathematiques/manuel-maths/sources/txt/BO2019_TEXPERTES_optionnel.txt`
(`sha256:a427dd12f3ff774dd0bdd31a26aaa77423509947bf60589e72430b6f5054a1c5`,
vérifié contre `docs/programmes/PROGRAMMES_2026_2027.yaml`). Aucun autre
audit préexistant de type `CONFORMITE_*.md` n'existait pour ce manuel — ce
document est le premier. Détail complet, ligne par ligne, dans
`audit/PROGRAM_COVERAGE_MATRIX_TEXPERTES.json` (47 lignes).

## ⚠️ Trouvaille critique — priorité avant tout le reste

**5 fichiers de cours identiques, hors sujet, déjà `status: approved`,
confirmés assemblés dans le manuel compilé.**

`cours/10_C1_derivee_composee.tex` — "Dérivée d'une fonction composée"
(règle de dérivation en chaîne, un sujet d'**analyse** 1SPE/TSPE) — existe
**à l'identique** (même corps, seul l'`id`/`chapitre` du META change) dans
les **5 chapitres** de TEXPERTES :

| Chapitre | id META | capacites_codes déclaré | status |
|---|---|---|---|
| TEXP-ARITHMETIQUE | `TEXP-ARI-CR-010-DERIVEE` | `["C1"]` | `approved` |
| TEXP-COMPLEXES-ALGEBRE-GEOMETRIE | `TEXP-CAG-CR-010-DERIVEE` | `["C1"]` | `approved` |
| TEXP-COMPLEXES-TRIGO-POLYNOMES | `TEXP-CTP-CR-010-DERIVEE` | `["C1"]` | `approved` |
| TEXP-GRAPHES | `TEXP-GRA-CR-010-DERIVEE` | `["C1"]` | `approved` |
| TEXP-MATRICES-MARKOV | `TEXP-MAT-CR-010-DERIVEE` | `["C1"]` | `approved` |

Aucun de ces 5 chapitres ne traite d'analyse/dérivation au programme
officiel (arithmétique des entiers, nombres complexes, graphes, matrices —
zéro occurrence de "dérivée" ou de fonction composée dans le texte
MENE1921264A). Chaque fichier prétend pourtant couvrir la capacité C1 du
chapitre où il se trouve, alors que la vraie C1 de chaque chapitre porte
sur un tout autre sujet (déjà couverte par un fichier séparé et correct :
`10_C1_divisibilite_pgcd.tex`, `10_C1_algebre.tex`, etc. — voir la matrice).

**Vérifié : les 5 fichiers sont bien assemblés** (`assemblies[].included_objects`
de l'inventaire courant, `audit/INVENTAIRE_COLLECTION.json`) — ce contenu
erroné fait donc partie du manuel TEXPERTES tel que compilé et approuvé
aujourd'hui, pas d'un brouillon écarté.

**Aucune modification effectuée dans ce lot.** Ceci est un incident de
contenu scientifique/éditorial réel (contenu hors-sujet déjà marqué
approuvé dans cinq chapitres), pas une simple ligne de matrice — signalé
comme prioritaire avant toute autre action sur ce manuel.

**Source et étendue réelles identifiées** (recherche complémentaire,
`md5sum` sur tout `Mathematiques/manuel-maths/chapitres/`) : l'original
légitime est `TSPE-DERIVATION-CONVEXITE/cours/10_C1_derivee_composee.tex`
(id `TSPE-DERCONV-CR-010`), où "dérivée d'une fonction composée" est
réellement la capacité C1 de ce chapitre TSPE. Le même fichier a été
dupliqué à l'identique dans **10 chapitres n'ayant aucun rapport avec ce
sujet** : les 5 chapitres TEXPERTES ci-dessus **et 5 chapitres TCOMPL**
(`TCOMPL-TEMPS-ATTENTE`, `TCOMPL-ECHANTILLONNAGE`,
`TCOMPL-MODELES-FONCTION`, `TCOMPL-INFERENCE-BAYESIENNE`,
`TCOMPL-INEGALITES` — mêmes symptômes : `capacites_codes=["C1"]`,
`status=approved`). Contamination systémique sur **11 fichiers au total**
(1 légitime + 10 dupliqués à tort) touchant **deux manuels**. À traiter
comme un seul incident transversal, pas cinq incidents isolés — la
correction pour TEXPERTES ne doit pas être menée sans traiter TCOMPL en
même temps.

## Chiffres finaux

```
TOTAL_MANDATORY_ATOMS      = 34
STRUCTURALLY_MAPPED        = 34   (100 % — capacité identifiée, fichier existe ; FULL=0, revue scientifique/pédagogique pas encore faite)
FULL                       = 0
PARTIAL                    = 0
MISSING                    = 0
TRANSVERSAL (hors grille)  = 1    (modalités d'évaluation transversales — oral, travaux variés)

Non obligatoire (mandatory=false), 13 lignes :
  OUT_OF_SCOPE_WITH_PROOF  = 7    (histoire des mathématiques, problèmes possibles explicitement facultatifs)
  UNSUPPORTED_CLAIM        = 5    (les 5 fichiers "dérivée composée" contaminants — voir ci-dessus)
  TRANSVERSAL              = 1
```

Contrairement à 1SPE (référentiel avec plusieurs dérives de portée), le
référentiel `capacites_TEXPERTES_*.json` (34 capacités, 5 fichiers) colle
de très près au texte officiel — libellés quasi verbatim, aucune capacité
listée qui soit absente du texte, aucune capacité officielle manquante
(`MISSING = 0`). Le problème découvert ici est d'une nature différente :
non pas une dérive du référentiel, mais une **contamination du contenu
réel** par un fichier hors-sujet dupliqué, invisible dans le référentiel
lui-même (qui, lui, reste correct).

## Ce que cette matrice ne couvre pas encore

- Audit scientifique/pédagogique des 34 capacités structurellement
  mappées.
- Vérification que le contenu réel des fichiers (au-delà de leur seule
  existence) couvre bien chaque capacité — en particulier, s'assurer
  qu'aucun autre fichier ne souffre de la même contamination
  copier-coller que `10_C1_derivee_composee.tex`.
- EXAM_ALIGNMENT : régime `continuous_assessment` confirmé
  (`MENE2215445N`), pas d'épreuve terminale spécifique — cohérence
  cours/évaluation en contrôle continu à vérifier lors de l'audit
  pédagogique.

## Prochaine étape

Traiter la contamination `derivee_composee` comme un incident prioritaire
(vérifier son étendue exacte — un seul fichier dupliqué 5 fois détecté ici,
mais une recherche plus large pourrait en révéler d'autres du même type
dans d'autres manuels), avant de lancer l'audit scientifique/pédagogique
normal des 34 capacités structurellement mappées.
