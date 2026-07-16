Vérification complète du chapitre $ARGUMENTS :
1. `make verify CHAP=$ARGUMENTS (exécution + traces + ruff)` — corrige toute erreur mathématique détectée (dans l'objet, pas dans le test).
2. `make similarity CHAP=$ARGUMENTS` — régénère tout objet en fail (mode inspiration : nouvelles valeurs ET nouveau contexte).
3. `make coverage CHAP=$ARGUMENTS` — comble les manquants.
4. Passe le vérificateur adversarial (`prompts/verificateur_adversarial.md`, modèle Opus) sur : toutes les démonstrations, tous les sujets d'évaluation, 20 % des corrigés tirés au hasard.
5. Synthèse dans `chapitres/$ARGUMENTS/validations/RAPPORT_GATES.md` avec la liste des objets nécessitant revue humaine.
