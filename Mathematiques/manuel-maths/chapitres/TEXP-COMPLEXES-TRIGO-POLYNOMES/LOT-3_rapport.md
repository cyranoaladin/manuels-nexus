# LOT 3 — Cours TEXP-COMPLEXES-TRIGO-POLYNOMES
3 fichiers de cours (forme exponentielle et formules d'Euler/Moivre ;
formule d'addition demontree par produit scalaire, equations
polynomiales avec demonstration de factorisation par telescopage ;
geometrie des complexes et demonstration complete de la description de
U_n).

Defauts trouves et corriges avant commit :
1. Artefact de scratch-work ("if False else None") laisse dans un bloc
   VERIFY (meme pattern recurrent, deja identifie et corrige a plusieurs
   reprises dans les chapitres precedents).
2. Limite de simplify() de sympy confirmee a deux reprises dans ce
   chapitre : les comparaisons exactes entre forme exponentielle et
   forme algebrique/trigonometrique d'un complexe ne se simplifient pas
   toujours automatiquement a 0 (ex. sqrt(2)*exp(-I*pi/4) vs 1-i, ou
   exp(2*I*pi/3) vs sa forme algebrique) -- remplace par verification
   numerique exacte (N() avec tolerance) dans les deux cas, regle
   generalisable aux chapitres Maths expertes suivants qui manipuleront
   frequemment des formes exponentielles.

0 FAIL et 0 erreur pdflatex apres correctifs.
