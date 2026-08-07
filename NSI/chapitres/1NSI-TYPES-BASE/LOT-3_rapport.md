# LOT 3 — Cours 1NSI-TYPES-BASE
5 fichiers de cours (conversions de base avec methode d'Horner et
divisions successives ; complement a 2 avec verification par methode
"inversion des bits + 1" et verification de l'addition binaire brute ;
flottants avec piege 0.1+0.2 et fonction presque_egaux ; booleens avec
table de and/or, demi-additionneur xor/and, court-circuit and/or ;
encodage de texte ASCII/ISO-8859-1/UTF-8 avec reencodage et gestion
d'erreur UnicodeEncodeError). Chaque exemple, propriete et bloc
"erreur frequente" verifie par execution python reelle avant redaction
(dont un cas ou l'hypothese initiale etait fausse : sum([0.1]*10)==1.0
en pratique, contrairement a l'intuition -- corrige avec sum([0.1]*3)
qui casse effectivement le test d'egalite). 0 FAIL verify_python.py,
ruff clean, 0 erreur pdflatex des le premier essai.
