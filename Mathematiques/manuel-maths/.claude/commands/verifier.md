Vérification complète du chapitre $ARGUMENTS :
1. `make verify CHAP=$ARGUMENTS` — corrige toute erreur mathématique détectée (dans l'objet, pas dans le test).
2. `make similarity CHAP=$ARGUMENTS` — régénère tout objet en fail (mode inspiration : nouvelles valeurs ET nouveau contexte).
3. `make coverage CHAP=$ARGUMENTS` — comble les manquants.
4. Passe le vérificateur adversarial (`prompts/verificateur_adversarial.md`) via OpenRouter avec le modèle explicitement fourni par `OPENROUTER_MODEL` sur : toutes les démonstrations, tous les sujets d'évaluation, 20 % des corrigés tirés au hasard. Aucun modèle n'est sélectionné implicitement.
5. Synthèse dans `chapitres/$ARGUMENTS/validations/RAPPORT_GATES.md` avec la liste des objets nécessitant revue humaine.

La réponse externe reste consultative : la vérifier localement et conserver les validations humaines requises. Ne transmettre aucun secret ni aucune donnée personnelle.
