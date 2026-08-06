# LOT 3 — Cours TNSI-BASES-DE-DONNEES
5 fichiers de cours (modele relationnel, SGBD, SELECT/WHERE, JOIN/ORDER BY,
INSERT/UPDATE/DELETE).

Infrastructure ajoutee : nouvel environnement \begin{sql}...\end{sql}
(gabarits/nexus-code.tex, style nxsql) sur le meme gabarit visuel que
\begin{python} (listings, language=SQL, memes couleurs/regle/numerotation)
-- absent du projet jusqu'ici (seuls python et console existaient). Verifie
par compilation et inspection visuelle (rendu conforme, mots-cles SQL en
couleur chapcolor). Reutilisable tel quel pour tout futur chapitre SQL.

Toute affirmation sur le comportement de SQL est verifiee par execution
reelle via sqlite3 (aucune sortie de requete ecrite de tete), y compris la
persistance (ecriture/relecture d'un fichier .db reel). 0 FAIL
(verify_python.py, execution en sandbox).
