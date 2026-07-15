Génère les exercices du chapitre $ARGUMENTS (LOT 4).
1. Prérequis : `dossier_curation.json` validé, cours et méthodes du LOT 3 présents.
2. Adopte `prompts/generateur_exercices.md`. Produis capacité par capacité, parcours par parcours (≥ 2 exercices par case de la matrice, ratio global 40/40/20).
3. Chaque exercice : META conforme au schéma + bloc VERIFY + compilation via l'outil MCP `compile_object`.
4. Enchaîne avec les corrigés (`prompts/redacteur_corriges.md`, SANS relire de corrigé source) puis les coups de pouce des exercices ◆.
5. Lance `make verify CHAP=$ARGUMENTS` puis `make similarity CHAP=$ARGUMENTS` puis `make coverage CHAP=$ARGUMENTS`. Régénère ce qui échoue (3 tentatives max par objet, ensuite statut manual_review).
6. Écris `LOT-4_rapport.md` (verdicts, coûts, objets en manual_review) et arrête-toi.
