# LOT 4 — Exercices TNSI-ALGORITHMIQUE
5 exercices + corriges (comptage de feuilles, construction et recherche
dans un ABR, recherche de chemin BFS sur un graphe metro, Fibonacci
memoise, maximum par diviser pour regner), parcours 1/2. Une erreur de
conception initiale detectee et corrigee avant commit : EX-003 supposait
un trajet a 3 stations entre "A" et "E" sans avoir recalcule le resultat
reel du BFS (qui donne en fait 4 stations, A-B-C-E) -- corrige en
recalculant explicitement via execution Python independante puis en
alignant enonce, VERIFY et corrige sur le resultat verifie. 0 FAIL
verify_python.py sur les 10 objets.
