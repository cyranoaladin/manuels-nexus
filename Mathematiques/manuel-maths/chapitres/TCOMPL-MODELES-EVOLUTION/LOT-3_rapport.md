# LOT 3 — Cours TCOMPL-MODELES-EVOLUTION
3 fichiers de cours (suites geometriques avec demonstration de la limite
de la somme ; suites recurrentes avec representation graphique
"escalier/spirale" et cas arithmetico-geometrique avec demonstration
complete ; equations differentielles y'=ay et y'=ay+b avec demonstration
de la caracterisation des solutions).

2 defauts trouves et corriges avant commit :
1. Bug de performance/timeout : une iteration de 30 racines carrees
   imbriquees en SymPy symbolique (sans evaluation numerique) provoque un
   timeout du gate de verification (expression symbolique exponentiellement
   complexe) -- remplace par une iteration en flottants natifs Python
   (math.sqrt), le calcul symbolique n'etant utilise que pour verifier le
   point fixe exact separement.
2. Erreur LaTeX fatale ("Missing $ inserted") : le libelle_eleve de la
   capacite C3 dans contrat.yaml contenait `u_{n+1}=f(u_n)` hors mode
   mathematique (recidive du meme piege deja documente et corrige une
   fois dans TSPE-CALCUL-INTEGRAL lors de la session precedente) --
   corrige en encadrant par `$...$`. Grep proactif des autres contrat.yaml
   TCOMPL deja committes : aucune autre occurrence.

0 FAIL et 0 erreur pdflatex apres les deux correctifs.
