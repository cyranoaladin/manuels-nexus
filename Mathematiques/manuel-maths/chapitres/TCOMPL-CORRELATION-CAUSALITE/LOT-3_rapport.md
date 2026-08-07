# LOT 3 — Cours TCOMPL-CORRELATION-CAUSALITE
3 fichiers de cours (ajustement affine avec demonstration complete de la
droite des moindres carres par annulation des derivees partielles,
verifiee numeriquement contre la formule directe covariance/variance ;
changement de variable pour linearisation exponentielle avec exemple
parfaitement aligne verifie symboliquement ; correlation vs causalite
avec variable cachee, exemples glaces/noyades et loi de Moore).

Deux artefacts de redaction trouves et corriges avant commit (aucun
n'affectait un bloc VERIFY, repérés a la relecture) : une formule
d'exemple contenant un terme parasite "x^2*0" sans utilite, et une ligne
de code Python inutilement convoluee (Ybar jamais utilisee). 0 FAIL
verify_sympy.py, 0 erreur pdflatex.
