# LOT 3 — Cours TNSI-STRUCTURES-DONNEES
5 fichiers de cours (interface/implementation avec pile a 2 implementations
contrastees, classes Python, piles/files, arbres binaires, graphes).
Bug LaTeX generalisable trouve et corrige : \begin{python}...\end{python}
(environnement lstlisting/verbatim) ne peut pas etre imbrique dans
\exemple{...} (macro a argument accolade standard) -- provoque
"Paragraph ended before \lst@next was complete" et une cascade d'erreurs
en aval. Corrige dans les 5 fichiers (exemple ferme avant le bloc de
code, \textbf{Exemple.} manuel utilise a la place). A eviter
systematiquement dans tous les chapitres NSI suivants. make verify
(verify_python.py, execution reelle en sandbox) : 0 FAIL. Code verifie
par execution effective (SymPy n'existe pas ici, verite = execution).
