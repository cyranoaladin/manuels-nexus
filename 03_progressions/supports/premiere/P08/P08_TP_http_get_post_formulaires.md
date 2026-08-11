---
title: "P08 - tp - HTTP, GET, POST et formulaires"
level: "premiere"
sequence_id: "P08"
document_type: "tp"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "HTTP, GET, POST et formulaires"
notion: "HTTP, GET, POST et formulaires"
private_data: false
official_program:
  capacities:
    - "P-IHM-03A"
    - "P-IHM-03B"
    - "P-IHM-03C"
    - "P-IHM-04A"
    - "P-IHM-04B"
    - "P-IHM-04C"
---

# P08 - TP - HTTP, GET, POST et formulaires

## Statut du TP
TP exécutable : le livrable élève est un fichier Python d'analyse HTTP/URL complété et vérifié par tests.

## Objectifs opérationnels
- Objectif 1 : analyser une URL GET et transformer la chaîne de requête en dictionnaire (P-IHM-04B).
- Objectif 2 : distinguer l'emplacement des paramètres selon la méthode HTTP GET ou POST (P-IHM-03A, P-IHM-04A).
- Objectif 3 : identifier ce qui est mémorisé côté client (cookie, localStorage) vs retransmis au serveur (P-IHM-03B).
- Objectif 4 : reconnaître quand la transmission est chiffrée (HTTP vs HTTPS) (P-IHM-03C, P-IHM-04C).

## Donnée fournie
`URL /club?jour=mercredi ; <form method=post action=/reservation><input id=nom name=nom></form> ; cookie session_id=abc123 ; localStorage theme=sombre`

## Travail demandé
1. Préparer la donnée : identifier la ressource, la query string, la méthode et les données du formulaire.
2. Réaliser : écrire `parametres_get(url)` qui transforme la chaîne de requête en dictionnaire (P-IHM-04B).
3. Réaliser : écrire `action_formulaire(methode, params)` qui décrit où sont les paramètres selon GET ou POST (P-IHM-04A).
4. Réaliser : écrire `classer_mecanisme(nom)` qui indique si un mécanisme est mémorisé, retransmis ou les deux (P-IHM-03B).
5. Tester le cas limite `paramètre jour absent` et `URL sans query string`.
6. Produire le livrable : les trois fonctions passent tous les tests.

## Déroulé en classe
1. Ouvrir le starter et repérer les fonctions d'analyse HTTP.
2. Lire l'URL `/club?jour=mercredi` comme une ressource suivie d'une chaîne de requête.
3. Transformer `jour=mercredi` en dictionnaire `{"jour": "mercredi"}`.
4. Comparer GET et POST : les paramètres GET sont dans l'URL, les paramètres POST sont dans le corps.
5. Classer les mécanismes : cookie (mémorisé + retransmis), localStorage (mémorisé seul), corps POST (envoyé une fois).
6. Discuter HTTP vs HTTPS : sans TLS, les données circulent en clair.
7. Lancer les tests pour identifier les fonctions encore incomplètes.
8. Relancer les tests après chaque fonction corrigée.

## Tests attendus à interpréter
- Test GET : `parametres_get("https://nsi.test/recherche?q=tri&page=2")` doit renvoyer `{"q": "tri", "page": "2"}`.
- Test POST : `action_formulaire("POST", {"nom": "Ada"})` doit renvoyer `"paramètres dans le corps de la requête"`.
- Test GET méthode : `action_formulaire("GET", {"q": "tri"})` doit renvoyer `"paramètres dans l'URL"`.
- Test cookie : `classer_mecanisme("cookie")` doit renvoyer `"mémorisé côté client et retransmis au serveur"`.
- Test localStorage : `classer_mecanisme("localStorage")` doit renvoyer `"mémorisé côté client uniquement"`.
- Test invalide : `parametres_get("https://nsi.test/recherche")` (sans `?`) doit renvoyer `{}`.

## Remédiation immédiate
- Si GET et POST sont inversés, revenir au schéma URL / corps de requête.
- Si cookie et localStorage sont confondus, rappeler que seul le cookie est envoyé automatiquement.
- Si POST est assimilé à du chiffrement, distinguer méthode HTTP et protocole HTTPS.

## Barème associé
- 2 points : donnée préparée (URL, méthode, paramètres identifiés).
- 3 points : `parametres_get` correcte avec gestion URL sans query string.
- 3 points : `action_formulaire` correcte distinguant GET et POST.
- 2 points : `classer_mecanisme` correcte et cas limite `paramètre jour absent` traité.

## Corrigé question par question
### Corrigé question 1
Résultat attendu : ressource = `/club`, query string = `jour=mercredi`, méthode formulaire = POST, données = `nom=...`.
### Corrigé question 2
Résultat attendu : `parametres_get("/club?jour=mercredi")` renvoie `{"jour": "mercredi"}`.
### Corrigé question 3
Résultat attendu : `action_formulaire("POST", {"nom": "Ada"})` renvoie `"paramètres dans le corps de la requête"`.
### Corrigé question 4
Résultat attendu : `classer_mecanisme("cookie")` → `"mémorisé côté client et retransmis au serveur"` ; `classer_mecanisme("localStorage")` → `"mémorisé côté client uniquement"`.
### Corrigé question 5
Résultat attendu : `parametres_get("/club")` renvoie `{}` (URL sans query string).

## Liens
- TD lié : `P08_TD_http_get_post_formulaires.md`.
- TP complémentaire : `P08_TP_html_css_dom.md` (structure HTML, CSS, DOM).
- Évaluation liée : `P08_evaluation_http_get_post_formulaires.md`.

## Cas limites travaillés
- paramètre jour absent.
- URL sans query string.
- cookie expiré (non retransmis).

## Erreurs fréquentes
- POST confondu avec chiffrement.
- localStorage supposé envoyé au serveur.
- GET avec HTTPS : paramètres chiffrés en transit mais visibles dans l'historique.

## Critères de réussite observables
- Les trois fonctions passent tous les tests du starter.
- Le cas limite `URL sans query string` renvoie un dictionnaire vide.
- L'élève distingue mémorisé côté client vs retransmis au serveur.



## Protocole de validation complémentaire
1. Préparer un jeu nominal propre à P08 et noter la sortie attendue avant exécution.
2. Préparer un cas limite distinct et expliquer pourquoi il doit être accepté ou refusé.
3. Exécuter le starter : il doit échouer sur au moins un test complet, ce qui confirme que le travail élève reste à produire.
4. Exécuter le corrigé professeur : il doit produire exactement les valeurs attendues dans les tests.
5. Comparer la trace obtenue avec la consigne : chaque étape doit être justifiée par une donnée du sujet.
6. Noter l'erreur fréquente observée et choisir la remédiation ciblée dans le support associé.

## Livrable vérifiable complémentaire
- Fichier élève complété avec les fonctions demandées dans le TP.
- Trace courte indiquant entrée, traitement, sortie et cas limite.
- Capture textuelle des tests attendus : nominal OK, cas limite OK, entrée invalide traitée.
- Commentaire final indiquant la capacité officielle réellement travaillée.

## Assets Python
- Starter élève : `code/P08_starter_web_http_dom_formulaires.py`.
- Tests attendus : `code/P08_tests_attendus_web_http_dom_formulaires.py`.
- Corrigé professeur : `code/P08_corrige_professeur_web_http_dom_formulaires.py`.
- Fonctions à compléter : `titre_page`, `textes_classe`, `parametres_get`, `action_formulaire`.
- Cas testés : titre HTML, classe DOM répétée, paramètre GET absent, formulaire sans action.
