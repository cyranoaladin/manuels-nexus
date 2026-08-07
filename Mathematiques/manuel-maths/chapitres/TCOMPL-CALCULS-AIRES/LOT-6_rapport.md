# LOT 6 — Evaluations TCOMPL-CALCULS-AIRES
EV-A (primitive, integrale, demonstration deux primitives) / EV-B (aire
entre courbes, theoreme fonction integrale, encadrement) : 50 min
chacune, corriges dedies.

2 erreurs de calcul detectees et corrigees avant commit par recalcul
sympy independant plutot que suppose : (1) integrale de 4x^3-6x+2 sur
[0,1] supposee valoir 1, recalculee et vaut en realite 0 ; (2) aire entre
-x^2+6x et 2x sur [0,4] supposee valoir 64/3 (avec un artefact de
scratch-work "if False else True" laisse par erreur dans le VERIFY),
recalculee et vaut en realite 32/3. 0 FAIL apres correctifs.
