# LOT 3 — Cours TNSI-ALGORITHMIQUE
7 fichiers de cours (arbres : taille/hauteur/parcours profondeur+largeur ;
ABR recherche/insertion ; graphes : BFS/DFS, cycle, chemin ; diviser pour
regner : tri fusion ; programmation dynamique : rendu de monnaie memoise,
gain de performance mesure empiriquement (memo ~2000x plus rapide que
naif sur somme=24, verifie par execution reelle avec time.perf_counter,
marge tres large donc non flaky) ; Boyer-Moore simplifie (regle du mauvais
caractere) compare a la recherche naive sur plusieurs cas.

Bug generalisable trouve et corrige : \lstinline{...} utilise "{" comme
delimiteur sans comptage de profondeur -- tout contenu avec des accolades
litterales (ex. \lstinline{memo={0: 0}}) tronque silencieusement le
rendu et provoque une erreur pdflatex "Extra }" absorbee sans faire
echouer la compilation (exit code 0). Trouve via lecture du .log
pdflatex (jamais inspecte en detail jusqu'ici) suite a une anomalie
visuelle repérée au spot-check. Corrige avec \lstinline|...| (delimiteur
"|"), sauf a l'interieur d'une macro a argument accolade
(\erreurFrequente{}) ou \lstinline reste incompatible quel que soit le
delimiteur (le contenu est deja tokenise avant que \lstinline ne puisse
changer les catcodes) : dans ce cas, \texttt{...\{...\}} avec accolades
echappees. Meme bug retrouve et corrige retroactivement dans
TNSI-STRUCTURES-DONNEES (commit separe). Regle a appliquer
systematiquement aux chapitres NSI suivants. 0 FAIL verify_python.py, 0
erreur pdflatex apres correctif (verifie par lecture du .log, pas
seulement le code de sortie).
