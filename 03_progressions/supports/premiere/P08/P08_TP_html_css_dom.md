---
title: "P08 - tp - HTML, CSS et DOM"
level: "premiere"
sequence_id: "P08"
document_type: "tp"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "HTML, CSS et DOM"
notion: "HTML, CSS et DOM"
private_data: false
official_program:
  capacities:
    - "P-IHM-01A"
    - "P-IHM-01B"
    - "P-IHM-02"
---

# P08 - TP - HTML, CSS et DOM

## Statut du TP
TP exécutable : le livrable élève est un fichier Python d'analyse HTML complété et vérifié par tests.

## Objectifs opérationnels
- Objectif 1 : extraire un titre HTML et signaler un document sans balise `title` (P-IHM-01A).
- Objectif 2 : repérer les textes associés à une classe CSS sans confondre balise, attribut et contenu (P-IHM-01B).
- Objectif 3 : manipuler le DOM en ciblant un élément par son identifiant (P-IHM-02).

## Donnée fournie
```html
<html><head><title>Mini site NSI</title></head>
<body><header><h1>Accueil</h1></header>
<main><p class="alerte">Erreur</p><p>Bienvenue</p>
<form method=post action=/reservation><label for=nom>Nom</label><input id=nom name=nom></form>
</main></body></html>
```

## Travail demandé
1. Préparer la donnée : identifier les balises, attributs et contenus textuels.
2. Réaliser : écrire `titre_page(html)` qui extrait le contenu de `<title>` (P-IHM-01A).
3. Réaliser : écrire `textes_classe(html, classe)` qui retourne les textes des éléments portant la classe CSS donnée (P-IHM-01B).
4. Réaliser : écrire `valeur_champ(html, id_champ)` qui cible un élément par `id` et retourne sa valeur (P-IHM-02).
5. Tester le cas limite `document sans title`.
6. Produire le livrable : les trois fonctions passent tous les tests.

## Déroulé en classe
1. Ouvrir le starter et repérer les trois fonctions à compléter.
2. Lire l'extrait HTML en distinguant balise, attribut et contenu textuel.
3. Extraire le contenu de `<title>` avant de chercher les classes CSS.
4. Pour `textes_classe`, chercher uniquement les éléments qui portent la classe demandée.
5. Vérifier sur l'exemple que la classe `alerte` donne la liste `["Erreur"]`.
6. Pour `valeur_champ`, cibler l'élément par `id` puis lire son attribut `value` ou son contenu.
7. Lancer les tests sur le starter pour identifier les fonctions encore incomplètes.
8. Relancer les tests après chaque fonction corrigée pour localiser les erreurs.

## Tests attendus à interpréter
- Test HTML : `titre_page(HTML)` doit renvoyer `"Mini site NSI"`.
- Test DOM : `textes_classe(HTML, "alerte")` doit renvoyer `["Erreur"]`.
- Test DOM id : `valeur_champ(HTML, "nom")` doit renvoyer le contenu du champ `nom`.
- Test invalide : un document HTML sans `<title>` doit lever `ValueError`.

## Remédiation immédiate
- Si le titre contient des balises, reprendre la suppression du balisage avant le nettoyage des espaces.
- Si la classe absente renvoie une valeur, vérifier que le sélecteur ne récupère pas tous les paragraphes.
- Si l'identifiant cible le mauvais élément, vérifier que le sélecteur utilise `id` et non `class`.

## Barème associé
- 2 points : donnée préparée (balises, attributs, contenus identifiés).
- 3 points : `titre_page` correcte avec gestion de l'absence.
- 3 points : `textes_classe` correcte avec sélection par classe CSS.
- 2 points : `valeur_champ` correcte et cas limite `document sans title` traité.

## Corrigé question par question
### Corrigé question 1
Résultat attendu : balises identifiées (`html`, `head`, `title`, `body`, `header`, `h1`, `main`, `p`, `form`, `label`, `input`) ; attributs (`class`, `method`, `action`, `for`, `id`, `name`) ; contenus (`Mini site NSI`, `Accueil`, `Erreur`, `Bienvenue`, `Nom`).
### Corrigé question 2
Résultat attendu : `titre_page(HTML)` renvoie `"Mini site NSI"`.
### Corrigé question 3
Résultat attendu : `textes_classe(HTML, "alerte")` renvoie `["Erreur"]`.
### Corrigé question 4
Résultat attendu : `valeur_champ(HTML, "nom")` cible `<input id=nom>` via le DOM.
### Corrigé question 5
Résultat attendu : `titre_page("<html><body></body></html>")` lève `ValueError`.

## Liens
- TD lié : `P08_TD_html_css_dom.md`.
- TP complémentaire : `P08_TP_http_get_post_formulaires.md` (HTTP, GET/POST, formulaires).
- Évaluation liée : `P08_evaluation_html_css_dom.md`.

## Cas limites travaillés
- document sans `<title>`.
- classe CSS absente du document.
- identifiant inconnu dans le DOM.

## Erreurs fréquentes
- attribut confondu avec contenu textuel.
- sélecteur trop large (tous les `<p>` au lieu de ceux portant la classe).
- balise `<title>` confondue avec `<h1>`.

## Critères de réussite observables
- Les trois fonctions passent tous les tests du starter.
- Le cas limite `document sans title` est traité par une exception.
- L'élève distingue balise, attribut et contenu sur l'exemple fourni.



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
