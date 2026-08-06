# LOT 3 — Cours TCOMPL-MODELES-FONCTION
3 fichiers de cours (etude de fonction avec exemple file de cout moyen
f(x)=x+9/x ; convexite avec caracterisation par f'' et contre-exemple
explicite montrant l'independance entre signe de f' et signe de f'' ;
statistique a deux variables avec calcul reel de la droite des moindres
carres par resolution symbolique du systeme normal, verifiant qu'elle
passe par le point moyen).

Defaut trouve et corrige avant commit (dans les exercices/evaluations,
pas le cours) : sympy factorise automatiquement certaines derivees
secondes (6*x-12 devient 6*(x-2)), faisant echouer une comparaison
d'egalite structurelle directe (hpp == 6*x-12) alors que l'expression est
mathematiquement correcte -- remplace par simplify(hpp-(6*x-12))==0 dans
les 4 fichiers concernes. 0 FAIL apres correctif (verify_sympy.py).
