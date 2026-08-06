# LOT 3 — Cours TCOMPL-TEMPS-ATTENTE
2 fichiers de cours (loi geometrique : definition, calcul explicite,
absence de memoire verifiee par calcul reel ; loi exponentielle :
verification de densite par integrale, fonction de repartition,
esperance calculee par integrale symbolique, absence de memoire
verifiee).

Defaut de notation trouve et corrige avant commit : la propriete
d'absence de memoire de la loi geometrique etait ecrite
"P(X>n)(X>n+k) = P(X>k)" sans le soulignement de sous-indice attendu
(devrait etre P_{X>n}(X>n+k), notation coherente avec P_B(A) utilisee au
chapitre Bayes) -- repere lors du spot-check visuel du PDF compile,
corrige. 0 FAIL verify_sympy.py, 0 erreur pdflatex.
