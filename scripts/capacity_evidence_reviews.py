#!/usr/bin/env python3
"""Revue semantique des attributions que la signature n'atteste pas.

`NOT_EVIDENCED_BY_SIGNATURE` ne veut dire ni PASS ni FAIL : la signature n'a
pas vu la preuve qu'elle cherchait. Laisser une attribution dans cet etat
reviendrait a compter une question ouverte comme un resultat.

Chaque attribution est donc LUE, et recoit un verdict motive. Trois issues
seulement changent quelque chose au depot :

`SEMANTICALLY_ALIGNED`   le contenu sert bien la capacite ; c'est la SIGNATURE
                         qui etait trop etroite. On l'elargit -- et le
                         marqueur ajoute est tire du libelle de la capacite,
                         jamais de l'enonce qu'il doit juger. Fabriquer le
                         marqueur a partir de l'exercice reviendrait a lui
                         faire signer son propre certificat.
`MISALIGNED`             le contenu sert une AUTRE capacite ; on corrige le
                         mapping, jamais la signature.
`PARTIALLY_ALIGNED`      le contenu est du bon domaine mais n'exerce pas ce
                         que la capacite demande ; on complete l'enonce.
`AMBIGUOUS`              le contrat ne permet pas de trancher : remonte au
                         Release Owner, jamais resolu unilateralement.
"""

from __future__ import annotations

ALIGNED = "SEMANTICALLY_ALIGNED"
MISALIGNED = "MISALIGNED"
PARTIAL = "PARTIALLY_ALIGNED"
AMBIGUOUS = "AMBIGUOUS"
VERDICTS = (ALIGNED, MISALIGNED, PARTIAL, AMBIGUOUS)


def revue(object_id, chapter, declared, verdict, *, content, expected, why,
          action, corrected=None):
    return {
        "object_id": object_id, "chapter": chapter,
        "declared_capacity": declared, "verdict": verdict,
        "actual_content": content, "expected_signature": expected,
        "why_signature_missed_it": why, "action_taken": action,
        "corrected_capacity": corrected,
    }


REVIEWS = [
    revue("TCOMPL-AIR-EX-003", "TCOMPL-CALCULS-AIRES", "C3", ALIGNED,
          content="calcule l'aire comprise entre les courbes de deux polynomes",
          expected="une integrale, une valeur moyenne ou une aire",
          why="le marqueur exigeait `\\int` ou « integrale » alors que le "
              "libelle de la capacite dit lui-meme « une aire sous une courbe "
              "ou entre deux courbes »",
          action="marqueur `aire` ajoute, tire du libelle de la capacite"),
    revue("TCOMPL-CORR-EX-003", "TCOMPL-CORRELATION-CAUSALITE", "C3", ALIGNED,
          content="linearise y = A x^b par X = ln x, Y = ln y, puis regresse",
          expected="un ajustement affine obtenu par changement de variable",
          why="l'enonce dit « lineariser » et « droite de regression » la ou le "
              "marqueur attendait le mot « affine »",
          action="marqueurs `linearis` et `droite de regression` ajoutes"),
    revue("TCOMPL-ECH-EX-004", "TCOMPL-ECHANTILLONNAGE", "C6", ALIGNED,
          content="ecrit E(X) = somme k P(X=k) pour n = 2 et la calcule",
          expected="l'esperance d'une binomiale, demontree pour n <= 3",
          why="l'enonce ecrit la notation `E(X)` sans employer le mot "
              "« esperance »",
          action="marqueur `E\\(X\\)` ajoute"),
    revue("TCOMPL-INEG-EX-002", "TCOMPL-INEGALITES", "C5", PARTIAL,
          content="demande l'indice de Gini d'un modele L(x) sans exiger le "
                  "passage par l'integrale",
          expected="l'aire entre la courbe et la bissectrice, par une integrale",
          why="la signature cherchait l'integrale, que l'enonce ne demandait "
              "pas explicitement : la capacite C5 porte sur la METHODE, pas "
              "seulement sur le resultat",
          action="enonce complete d'une question intermediaire qui demande "
                 "l'aire par integrale avant d'en deduire Gini"),
    revue("TCOMPL-INEG-EX-003", "TCOMPL-INEGALITES", "C1", MISALIGNED,
          content="estime l'indice de Gini par la methode des trapezes sur des "
                  "donnees par quintiles",
          expected="construire et interpreter une courbe de Lorenz",
          why="l'exercice ne construit aucune courbe de Lorenz : il calcule un "
              "indice de Gini, qui est l'objet de C3",
          action="capacite corrigee C1 -> C3", corrected="C3"),
    revue("TCOMPL-BAYES-EX-002", "TCOMPL-INFERENCE-BAYESIENNE", "C3", ALIGNED,
          content="oppose P_P(N) et P_N(P) sur un exemple concret",
          expected="distinguer la probabilite a posteriori de son inverse",
          why="l'enonce MONTRE l'inversion par ses notations au lieu de la "
              "nommer",
          action="marqueur des deux conditionnements croises ajoute"),
    revue("TCOMPL-BAYES-EX-004", "TCOMPL-INFERENCE-BAYESIENNE", "C5", ALIGNED,
          content="calcule la VPP pour deux prevalences et compare",
          expected="l'etude de la valeur predictive positive selon la prevalence",
          why="l'enonce ecrit l'abreviation `VPP`, que le marqueur ne "
              "connaissait pas",
          action="marqueur `VPP` ajoute"),
    revue("TCOMPL-LOG-EX-001", "TCOMPL-LOGARITHME-HISTORIQUE", "C4", MISALIGNED,
          content="utilise l'equation fonctionnelle pour simplifier des ecritures",
          expected="DEMONTRER ln(ab) = ln a + ln b a partir de l'equation "
                   "fonctionnelle",
          why="l'exercice UTILISE la relation ; la demontrer est une autre "
              "capacite, et c'est C2 qui porte l'usage",
          action="capacite corrigee C4 -> C2", corrected="C2"),
    revue("TCOMPL-LOG-EX-004", "TCOMPL-LOGARITHME-HISTORIQUE", "C5", MISALIGNED,
          content="calcule la derivee de ln(3x+5)",
          expected="DEMONTRER que la derivee de ln est 1/x",
          why="l'exercice applique la formule de derivation ; C1 porte cet "
              "usage, C5 porte la demonstration",
          action="capacite corrigee C5 -> C1", corrected="C1"),
    revue("TCOMPL-ME-EX-001", "TCOMPL-MODELES-EVOLUTION", "C2", PARTIAL,
          content="demande la quantite limite d'un polluant a apport constant "
                  "et degradation proportionnelle",
          expected="la limite d'une suite geometrique et de la somme de ses "
                   "termes",
          why="le modele EST une somme geometrique, mais l'enonce ne le nomme "
              "jamais : l'eleve peut repondre sans jamais identifier la "
              "structure que la capacite demande de reconnaitre",
          action="enonce complete d'une question qui demande d'identifier la "
                 "suite geometrique avant de conclure"),
    revue("TCOMPL-ME-EX-002", "TCOMPL-MODELES-EVOLUTION", "C4", ALIGNED,
          content="resout u(n+1) = 0,75 u(n) + 5 par la suite constante",
          expected="resoudre une arithmetico-geometrique par sa solution "
                   "constante",
          why="l'enonce dit « suite constante » la ou le marqueur attendait "
              "« solution constante »",
          action="marqueur `suite constante` ajoute"),
    revue("TCOMPL-ME-EX-003", "TCOMPL-MODELES-EVOLUTION", "C5", ALIGNED,
          content="resout y'(t) = -0,25 y(t) + 60 avec condition initiale",
          expected="resoudre y' = ay puis y' = ay + b",
          why="le marqueur cherchait la forme litterale `y' = ay` et ne "
              "reconnaissait pas une equation a coefficients numeriques",
          action="marqueur d'equation differentielle a coefficients ajoute"),
    revue("TCOMPL-ME-EX-004", "TCOMPL-MODELES-EVOLUTION", "C1", ALIGNED,
          content="etudie la suite de Heron u(n+1) = (u(n) + 6/u(n))/2",
          expected="modeliser par une suite definie par recurrence",
          why="l'enonce donne la relation de recurrence en formule sans "
              "employer le mot",
          action="marqueur `u_\\{n+1\\}` ajoute"),
    revue("TCOMPL-MF-EX-001", "TCOMPL-MODELES-FONCTION", "C1", ALIGNED,
          content="calcule f'(x), resout f'(x) = 0 et dresse le tableau",
          expected="calculer la derivee, les limites, dresser le tableau",
          why="l'enonce ecrit `f'(x)` sans le mot « derivee »",
          action="notation `f'` acceptee comme marqueur de derivation"),
    revue("TCOMPL-MF-EX-003", "TCOMPL-MODELES-FONCTION", "C5", ALIGNED,
          content="calcule h''(x), etudie son signe, conclut sur la convexite",
          expected="etudier la convexite d'une fonction deux fois derivable",
          why="le marqueur ne connaissait que `f''` et pas `h''`",
          action="marqueur de derivee seconde generalise a toute lettre"),
    revue("TCOMPL-MF-EX-005", "TCOMPL-MODELES-FONCTION", "C1", ALIGNED,
          content="calcule f'(x), son signe, les limites, le tableau",
          expected="calculer la derivee, les limites, dresser le tableau",
          why="meme cause que TCOMPL-MF-EX-001 : la notation `f'` sans le mot",
          action="couvert par la meme generalisation"),
    revue("TCOMPL-ATT-EX-002", "TCOMPL-TEMPS-ATTENTE", "C3", ALIGNED,
          content="applique l'absence de memoire apres quatre echecs",
          expected="utiliser la caracterisation par l'absence de memoire",
          why="le marqueur exigeait « geometrique » ou « caracteris », absents "
              "d'un enonce qui dit « en utilisant l'absence de memoire »",
          action="marqueur `memoire` ajoute"),
    revue("TCOMPL-ATT-EX-004", "TCOMPL-TEMPS-ATTENTE", "C6", ALIGNED,
          content="ecrit l'integrale donnant E(X) pour une exponentielle et la "
                  "calcule",
          expected="calculer l'esperance d'une exponentielle sous forme "
                   "d'integrale",
          why="l'enonce ecrit `E(X)` sans le mot « esperance »",
          action="marqueur `E\\(X\\)` ajoute"),
    revue("TSPE-TRIGO-EX-003", "TSPE-TRIGONOMETRIE", "C1", ALIGNED,
          content="determine les instants ou une hauteur en cosinus atteint "
                  "puis depasse une valeur",
          expected="resoudre cos(x) = a et cos(x) <= a",
          why="l'enonce pose l'equation et l'inequation en langue naturelle -- "
              "« determiner les instants », « superieure ou egale » -- sans "
              "employer les mots equation ni inequation",
          action="marqueurs des formulations naturelles ajoutes"),
    revue("TSPE-TRIGO-EX-016", "TSPE-TRIGONOMETRIE", "C2", MISALIGNED,
          content="simplifie cos x + cos(pi - x) et les expressions d'angles "
                  "associes",
          expected="etudier une fonction trigonometrique : variations, optimum",
          why="l'exercice ne construit ni n'etudie aucune fonction : il "
              "manipule des formules d'angles associes, qui sont le prerequis "
              "R1 du chapitre et non l'une de ses deux capacites",
          action="rattache au prerequis R1, capacite retiree", corrected=None),
    revue("TSPE-TRIGO-EX-019", "TSPE-TRIGONOMETRIE", "C2", MISALIGNED,
          content="demontre cos(pi/2 - x) = sin x et les relations associees",
          expected="etudier une fonction trigonometrique : variations, optimum",
          why="meme cause, et l'enonce renvoie explicitement a « C3 », une "
              "capacite que le contrat de ce chapitre ne comporte pas : la "
              "reference vient d'un autre contrat",
          action="rattache au prerequis R1, capacite retiree", corrected=None),
    revue("TCOMPL-LOG-EX-009", "TCOMPL-LOGARITHME-HISTORIQUE", "C5", ALIGNED,
          content="derive exp(ln x) = x membre a membre et en deduit ln'(x) = 1/x, "
                  "puis verifie sur ln(5x) par deux chemins",
          expected="demontrer que la derivee de ln est 1/x",
          why="l'enonce conduit la demonstration par « ecrire », « deriver », "
              "« en deduire » sans employer le verbe « demontrer »",
          action="marqueur `en deduire` ajoute au groupe des verbes de preuve"),
    revue("TSPE-PROBA-EX-003", "TSPE-PROBABILITES", "C3", MISALIGNED,
          content="calcule P(X=0) puis P(X>=1) pour un tireur, application "
                  "directe de la loi binomiale",
          expected="resoudre un probleme de seuil, de comparaison ou "
                   "d'optimisation avec la loi binomiale",
          why="l'exercice calcule des probabilites sans resoudre aucun "
              "probleme de seuil ni comparer deux situations : c'est le calcul "
              "numerique de C4, pas la resolution de probleme de C3",
          action="capacite corrigee C3 -> C4", corrected="C4"),
    revue("TSPE-PROBA-EX-062", "TSPE-PROBABILITES", "C3", PARTIAL,
          content="compare deux strategies de controle par leur probabilite "
                  "de rejet, a deux taux de defauts",
          expected="mobiliser la loi binomiale pour comparer",
          why="la comparaison est bien la, mais l'enonce ne demandait jamais "
              "d'identifier la loi : l'eleve pouvait comparer deux nombres "
              "sans reconnaitre le modele que la capacite exige de mobiliser",
          action="enonce complete d'une premiere question qui fait justifier "
                 "la loi binomiale et preciser ses parametres ; corrige "
                 "renumerote en consequence"),
]


def by_object() -> dict[str, dict]:
    return {r["object_id"]: r for r in REVIEWS}
