# LOT 4 — Exercices TCOMPL-LOGARITHME-HISTORIQUE
4 exercices + corriges (simplification par equation fonctionnelle,
resolution d'equation avec domaine, seuil de decroissance avec sens de
l'inegalite, derivee de ln compose).

Defaut serieux trouve et corrige avant commit : l'assertion de
verification initiale (`simplify(A) == 0`) pour l'exercice 1 etait
mathematiquement FAUSSE (A=ln(12)-ln(3)-ln(2) vaut en realite ln(2), pas
0 -- confirme par calcul sympy independant) ; le corrige redige en
consequence contenait un raisonnement visiblement confus et contradictoire
(plusieurs tentatives successives dans le texte final). Entierement
recalcule et reecrit proprement, avec l'enonce reformule pour demander le
resultat sous forme k*ln(2) plutot que de supposer a tort un resultat nul.
0 FAIL apres correctif.
