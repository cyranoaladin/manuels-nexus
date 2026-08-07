# LOT 6 — Evaluations TCOMPL-INEGALITES
EV-A / EV-B : 45 min chacune, corriges dedies. Defaut de conception
detecte et corrige avant commit : le premier modele choisi pour EV-A,
L(x)=(3x^2-x)/2, n'etait PAS une courbe de Lorenz valide (L'(0)=-1/2<0,
donc decroissante au voisinage de 0, ce qui est impossible pour une
courbe de Lorenz) -- detecte par verification systematique du signe de
L' avant redaction, remplace par L(x)=(3x^2+x)/4 (verifie croissante et
convexe sur tout [0,1]). 0 FAIL apres correctif.
