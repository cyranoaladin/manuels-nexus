# LOT 4 — Exercices TNSI-LANGAGES-ET-PROGRAMMATION
4 exercices + corriges (somme des chiffres recursive avec analyse d'arbre
d'appels, exploitation de la documentation du module math y compris un
cas d'erreur de type reel, reecriture imperatif->fonctionnel, debogage
d'un effet de bord par aliasing sur une liste partagee entre bulletins),
parcours 1/2. Une premisse d'enonce corrigee avant commit : le test
initialement prevu sur math.hypot avec un seul argument ne leve pas
d'erreur en Python moderne (fonction variadique depuis 3.8, verifie par
execution) -- remplace par un cas reel d'erreur de type (math.sqrt sur une
chaine). 0 FAIL verify_python.py.
