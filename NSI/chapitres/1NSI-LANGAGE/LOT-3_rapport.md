# LOT 3 — Cours 1NSI-LANGAGE
5 fichiers de cours (constructions elementaires illustrees par une
fonction unique combinant les 5 constructions ; diversite/unite des
langages avec comparaison Python / langage de style C d'une meme
fonction, premiere utilisation de l'environnement console pour du code
non-Python dans cette session ; specification avec preconditions/
postconditions via assert ; mise au point par jeux de tests avec le
bug classique "accumulateur de maximum initialise a 0" et sa
consequence chiffree ; utilisation de bibliotheque avec le module math
et le piege isqrt vs sqrt+round). Un calcul initialement suppose
different (math.isqrt(50) vs round(math.sqrt(50))) s'est revele
identique a l'execution reelle -- corrige avec n=48 qui produit
effectivement un ecart. Chaque exemple verifie par execution python
reelle avant redaction. 0 FAIL verify_python.py, ruff clean.
