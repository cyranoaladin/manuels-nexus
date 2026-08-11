---
title: "P08 - td - HTML, CSS, DOM, HTTP et formulaires"
level: "premiere"
sequence_id: "P08"
document_type: "td"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "HTML, CSS, DOM, HTTP et formulaires"
notion: "HTML, CSS, DOM, HTTP et formulaires"
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

# P08 - TD - HTTP, GET, POST et formulaires

## Objectifs

- Analyser une URL avec paramètres GET et construire la requête correspondante à partir d'un formulaire HTML.
- Distinguer l'emplacement des données selon la méthode HTTP (GET dans l'URL, POST dans le corps) et les limites de chaque approche.
- Identifier ce qui est mémorisé côté client (cookie, localStorage) et ce qui est retransmis au serveur, en distinguant HTTP et HTTPS.

## Consigne commune

Travaillez sur papier. Chaque réponse doit nommer précisément les éléments HTML (`name`, `action`, `method`) et les composants HTTP (URL, query string, corps, en-tête) utilisés. Une réponse sans référence aux données fournies ne suffit pas. Les corrections détaillées sont réservées aux repères enseignant.

## Progression socle / standard / approfondissement

- Socle : exercices 1 et 2, pour lire et construire une requête GET.
- Standard : exercices 3 à 6, pour construire des requêtes POST, comparer cookie et localStorage, et distinguer HTTP de HTTPS.
- Approfondissement : exercices 7 et 8, pour déboguer un formulaire et corriger des raisonnements faux.

## Exercices

### Exercice 1

- **Lire une URL avec paramètres GET.**
- Type : lecture/analyse.
- Capacité officielle : P-IHM-04A.
- Données : l'URL suivante apparaît dans la barre d'adresse après soumission d'un formulaire de recherche.

```text
https://mediatheque.example/catalogue?q=python&niveau=debutant
```

- Consigne : identifiez le chemin de la ressource, la query string, et les couples clé/valeur transmis. Précisez où ces paramètres sont visibles (barre d'adresse, historique, logs serveur). Indiquez ce qui se passe si le champ `q` est vide.
- Indice socle : la query string commence après le caractère `?` et les couples sont séparés par `&`.
- Critère de réussite : le chemin, la query string et chaque couple sont identifiés ; le cas `q` vide est traité avec la forme `q=&niveau=debutant`.

#### Repères enseignant — continuité de preuve

- Consigne : lire les paramètres GET dans l'URL ; traiter aussi `champ nom vide` si nécessaire.

### Exercice 2

- **Construire une requête GET issue d'un formulaire.**
- Type : production/écriture.
- Capacité officielle : P-IHM-04B.
- Données : le formulaire HTML suivant.

```html
<form method="get" action="/catalogue">
  <label for="q">Recherche</label>
  <input id="q" name="q" value="python">
  <select name="niveau">
    <option value="debutant" selected>Débutant</option>
    <option value="avance">Avancé</option>
  </select>
  <button type="submit">Chercher</button>
</form>
```

- Consigne : écrivez l'URL complète produite lors de la soumission de ce formulaire. Précisez quels attributs HTML déterminent les noms des paramètres. Expliquez pourquoi `id="q"` n'apparaît pas dans l'URL et pourquoi `name="q"` y apparaît.
- Critère de réussite : l'URL est `/catalogue?q=python&niveau=debutant` ; la distinction `id` vs `name` est expliquée ; l'événement submit est nommé.

#### Repères enseignant — continuité de preuve

- Consigne : construire l'URL GET à partir des attributs `name` ; traiter aussi `paramètre jour absent` si nécessaire.

### Exercice 3

- **Construire une requête POST issue d'un formulaire.**
- Type : production/écriture.
- Capacité officielle : P-IHM-03A.
- Données : le formulaire HTML suivant.

```html
<form method="post" action="/connexion">
  <label for="pseudo">Pseudo</label>
  <input id="pseudo" name="pseudo" value="lecteur7">
  <label for="mdp">Mot de passe</label>
  <input id="mdp" name="mot_de_passe" type="password" value="R3seau!">
  <button type="submit">Se connecter</button>
</form>
```

- Consigne : (3a) indiquez la route visée et écrivez le corps de la requête sous la forme `nom=valeur&nom=valeur`. Précisez si le mot de passe apparaît dans l'URL. Expliquez ce que fait `type="password"` et ce qu'il ne fait pas. (3b) Décrivez l'ordre des actions entre le client et le serveur : qui construit la requête, qui l'envoie, qui lit le corps, qui vérifie les informations, qui renvoie la réponse. Expliquez pourquoi la vérification du mot de passe doit être faite par le serveur et non par le JavaScript du navigateur.
- Critère de réussite : la route est `/connexion` ; le corps est `pseudo=lecteur7&mot_de_passe=R3seau!` ; le mot de passe n'est pas dans l'URL ; `type="password"` masque l'affichage mais ne chiffre pas ; l'ordre client → serveur → réponse est correct ; la vérification serveur est justifiée.

#### Repères enseignant — continuité de preuve

- Consigne : construire le corps POST et distinguer URL et body ; traiter aussi `formulaire sans action` si nécessaire.

### Exercice 4

- **Choisir GET ou POST selon le cas d'usage.**
- Type : justification.
- Capacité officielle : P-IHM-04C.
- Données : quatre cas d'usage sur un site Web.

| Cas | Description |
|---|---|
| A | Un formulaire de connexion avec mot de passe |
| B | Une barre de recherche sur un site |
| C | Un formulaire de contact (nom, email, message) |
| D | Un lien contenant un token d'authentification dans l'URL |

- Consigne : pour chaque cas, indiquez si GET ou POST est approprié et justifiez par un critère observable (visibilité dans l'URL, historique, corps de requête). Pour chaque cas, indiquez si HTTPS est nécessaire et pourquoi. Expliquez pourquoi le token dans l'URL du cas D pose un problème de confidentialité.
- Critère de réussite : chaque cas est classé avec justification ; la distinction GET/POST/HTTPS est explicite ; POST sans HTTPS ne chiffre pas est mentionné.

#### Repères enseignant — continuité de preuve

- Consigne : classer chaque cas selon GET/POST/HTTPS avec justification ; traiter aussi `paramètre jour absent` si nécessaire.

### Exercice 5

- **Cookies, localStorage et retransmission.**
- Type : justification.
- Capacité officielle : P-IHM-03B.
- Données : un formulaire POST envoie `nom=Ali` au serveur ; le serveur répond avec `Set-Cookie: session_id=abc123; Path=/; HttpOnly`. L'utilisateur revient sur la page et le navigateur a aussi un `localStorage.setItem("theme", "sombre")`.
- Consigne : (5a) parmi `session_id`, `nom=Ali` (corps POST) et `theme=sombre` (localStorage), indiquez lesquels sont retransmis automatiquement au serveur à la prochaine requête ; (5b) expliquez pourquoi `localStorage` n'est pas retransmis ; traitez aussi le cas `cookie expiré` si nécessaire.
- Critère de réussite : distinction mémorisé client / retransmis serveur explicite, chaque mécanisme classé.

#### Repères enseignant — continuité de preuve

- Consigne : classer chaque mécanisme (cookie, POST body, localStorage) selon stockage et retransmission ; traiter aussi `cookie expiré` si nécessaire.

### Exercice 6

- **HTTP vs HTTPS et POST n'est pas du chiffrement.**
- Type : lecture/analyse.
- Capacité officielle : P-IHM-03C.
- Données : deux scénarios : (A) formulaire de connexion avec mot de passe envoyé en POST sur `http://example.com/login` ; (B) le même formulaire envoyé en POST sur `https://example.com/login`.
- Consigne : (6a) pour chaque scénario, dites si les données sont chiffrées sur le réseau et justifiez ; (6b) expliquez pourquoi POST seul ne suffit pas à protéger les données ; traitez aussi le cas `GET avec HTTPS` si nécessaire.
- Critère de réussite : distinction HTTP/HTTPS explicite, POST masque les données de l'URL mais ne les chiffre pas, GET avec HTTPS chiffre en transit mais les paramètres restent dans l'historique local.

#### Repères enseignant — continuité de preuve

- Consigne : comparer HTTP et HTTPS, montrer que POST ne chiffre pas ; traiter aussi `GET avec HTTPS` si nécessaire.

### Exercice 7

- **Déboguer un formulaire HTML.**
- Type : cas limite.
- Capacité officielle : P-IHM-04A.
- Données : le formulaire suivant ne fonctionne pas correctement.

```html
<form action="/reservation">
  <label for="nom">Nom</label>
  <input id="nom">
  <label for="date">Date</label>
  <input id="date" name="date" value="2026-03-15">
  <button type="submit">Réserver</button>
</form>
```

Un élève soumet le formulaire et constate que l'URL produite est `/reservation?date=2026-03-15` sans le nom.

- Consigne : identifiez les deux erreurs dans ce formulaire. Pour chaque erreur, expliquez pourquoi elle empêche le bon fonctionnement et proposez la correction HTML. Indiquez quelle méthode HTTP est utilisée par défaut quand `method` est absent. Testez le cas `champ nom vide` après correction.
- Critère de réussite : l'attribut `name` manquant sur le champ nom est identifié ; l'absence de `method` (GET par défaut) est relevée ; les corrections HTML sont écrites ; `<label for=nom>Nom</label><input id=nom name=nom>` apparaît dans la correction.

#### Repères enseignant — continuité de preuve

- Consigne : identifier `name` manquant et `method` absent ; traiter aussi `champ nom vide` si nécessaire.

### Exercice 8

- **Corriger des raisonnements faux.**
- Type : justification.
- Capacité officielle : P-IHM-04B.
- Données : quatre affirmations d'élèves.

| Affirmation | Phrase |
|---|---|
| F1 | « POST est sécurisé car les données ne sont pas dans l'URL. » |
| F2 | « HTTPS transforme GET en POST. » |
| F3 | « Un champ sans attribut `name` est quand même envoyé au serveur. » |
| F4 | « Un formulaire HTML suffit à valider les données côté serveur. » |

- Consigne : pour chaque affirmation, expliquez pourquoi elle est fausse ou trompeuse. Proposez une reformulation correcte en utilisant le vocabulaire précis du cours (URL, corps de requête, chiffrement, TLS, attribut `name`, validation serveur).
- Critère de réussite : chaque correction identifie la confusion précise et utilise le bon terme technique ; une simple négation ne suffit pas.

#### Repères enseignant — continuité de preuve

- Consigne : corriger chaque raisonnement faux avec le vocabulaire précis ; traiter aussi `paramètre jour absent` si nécessaire.

## Erreurs fréquentes

- Confondre `id` et `name` : seul `name` détermine les paramètres de la requête.
- Croire que POST chiffre les données : POST masque les données de l'URL, seul HTTPS chiffre le transport.
- Oublier qu'un champ sans `name` n'est pas transmis au serveur.
- Croire que `type="password"` protège les données sur le réseau.
- Confondre cookie (retransmis automatiquement) et localStorage (jamais retransmis).

## Différenciation et aides graduées

- Aide socle : repérer le `?` et les `&` dans l'URL pour identifier les paramètres ; comparer les attributs `id` et `name` dans le formulaire.
- Aide standard : dessiner un schéma client → serveur avec l'URL et le corps de requête pour chaque méthode.
- Approfondissement : pour l'exercice 7, ajouter un troisième champ et vérifier la requête produite ; pour l'exercice 8, rédiger une explication destinée à un camarade.

## Cas limites travaillés

- champ nom vide ;
- paramètre jour absent ;
- formulaire sans action ;
- champ sans attribut `name` ;
- cookie expiré ;
- GET avec HTTPS (chiffré en transit mais visible dans l'historique).

## Corrigé — repères enseignant

### Corrigé exercice 1

- Donnée utilisée : URL `https://mediatheque.example/catalogue?q=python&niveau=debutant`.
- Méthode : identifier le chemin (`/catalogue`), la query string (`q=python&niveau=debutant`) et chaque couple clé/valeur.
- Résultat : chemin = `/catalogue` ; paramètres = `q=python` et `niveau=debutant` ; visibles dans la barre d'adresse, l'historique et les logs serveur.
- Contrôle : si `q` est vide, l'URL devient `/catalogue?q=&niveau=debutant` ; le paramètre est transmis avec une valeur vide.

### Corrigé exercice 2

- Donnée utilisée : formulaire GET avec `name="q"` et `name="niveau"`, action `/catalogue`.
- Méthode : les attributs `name` deviennent les noms des paramètres dans la query string ; `id` sert au CSS et au DOM mais n'apparaît pas dans l'URL.
- Résultat : URL produite = `/catalogue?q=python&niveau=debutant` ; l'événement submit déclenche la sérialisation des champs `name` en query string.
- Contrôle : un champ sans `name` ne serait pas inclus dans l'URL ; la distinction `id` vs `name` est essentielle.

### Corrigé exercice 3

- Donnée utilisée : formulaire POST avec `name="pseudo"` et `name="mot_de_passe"`, action `/connexion`.
- Méthode : (3a) en POST, les paramètres sont placés dans le corps de la requête, pas dans l'URL. (3b) Ordre : le navigateur (client) sérialise les champs et envoie la requête POST vers `/connexion` ; le serveur lit le corps, vérifie les informations reçues, puis renvoie une réponse HTTP ; le navigateur affiche la réponse.
- Résultat : route = `/connexion` ; corps = `pseudo=lecteur7&mot_de_passe=R3seau!` ; le mot de passe n'apparaît pas dans l'URL. `type="password"` masque les caractères à l'écran mais n'agit pas sur le réseau. La vérification du mot de passe doit être faite par le serveur car un contrôle JavaScript côté client peut être contourné.
- Contrôle : sans HTTPS, le corps POST circule en clair ; POST masque de l'URL mais ne chiffre pas ; la vérification côté serveur est indispensable.

### Corrigé exercice 4

- Donnée utilisée : quatre cas d'usage Web (connexion, recherche, contact, token URL).
- Méthode : classer chaque cas selon la confidentialité des données et le critère observable (URL, historique, corps, chiffrement).
- Résultat : A — POST + HTTPS (mot de passe sensible, ne doit pas apparaître dans l'URL ni les logs) ; B — GET (recherche non sensible, URL partageable) ; C — POST (données personnelles, pas dans l'historique) ; D — risque, le token est visible dans la barre d'adresse, l'historique et les logs serveur.
- Contrôle : POST sans HTTPS ne chiffre pas les données sur le réseau ; HTTPS chiffre le transport mais ne retire pas les paramètres GET de l'historique local.

### Corrigé exercice 5

- Donnée utilisée : cookie `session_id`, corps POST `nom=Ali`, localStorage `theme=sombre`.
- Méthode : classer chaque mécanisme selon le lieu de stockage et la retransmission automatique.
- Résultat : seul le cookie `session_id` est retransmis automatiquement au serveur via l'en-tête `Cookie` ; le corps POST `nom=Ali` n'est pas renvoyé ; `theme=sombre` (localStorage) reste côté client et n'est jamais envoyé au serveur.
- Contrôle : un cookie expiré n'est plus retransmis ; localStorage est un stockage local du navigateur, jamais inclus dans les requêtes HTTP.

### Corrigé exercice 6

- Donnée utilisée : deux scénarios HTTP vs HTTPS avec formulaire de connexion POST.
- Méthode : comparer le niveau de protection réseau (TLS ou non) indépendamment de la méthode HTTP.
- Résultat : scénario A — données POST en clair sur le réseau (HTTP, pas de TLS), interceptables ; scénario B — données POST chiffrées par TLS (HTTPS). POST masque les données de l'URL et de l'historique, mais ne les chiffre pas sur le réseau.
- Contrôle : GET avec HTTPS chiffre les paramètres en transit, mais ils restent dans l'historique et les logs locaux ; la protection réseau dépend de HTTPS, pas de la méthode HTTP.

### Corrigé exercice 7

- Donnée utilisée : formulaire avec `<input id="nom">` sans `name` et sans `method`.
- Méthode : identifier chaque erreur HTML et son impact sur la requête produite.
- Résultat : erreur 1 — l'attribut `name` est manquant sur le champ nom, donc le navigateur ne l'inclut pas dans la requête ; correction : `<label for=nom>Nom</label><input id=nom name=nom>`. Erreur 2 — `method` est absent, donc le formulaire utilise GET par défaut ; si POST est souhaité, ajouter `method="post"`.
- Contrôle : après correction, si le champ nom est vide, l'URL contiendra `nom=&date=2026-03-15` ; le champ est transmis avec une valeur vide.

### Corrigé exercice 8

- Donnée utilisée : quatre affirmations fausses d'élèves.
- Méthode : identifier la confusion précise et reformuler avec le vocabulaire technique.
- Résultat : F1 — POST masque les données de l'URL et de l'historique, mais ne les chiffre pas sur le réseau ; seul HTTPS chiffre le transport. F2 — HTTPS chiffre l'échange HTTP entier (URL, corps, en-têtes) via TLS, mais ne change pas la méthode ; GET reste GET. F3 — un champ sans attribut `name` n'est pas inclus dans la requête ; seuls les champs avec `name` sont sérialisés. F4 — un formulaire HTML contrôle la saisie côté client, mais la validation côté serveur est indispensable car un client modifié peut contourner les contrôles JavaScript.
- Contrôle : chaque correction utilise le terme technique précis (URL, corps, TLS, `name`, validation serveur) et ne se limite pas à une négation.

## Critères de réussite observables

- Les paramètres GET sont reconstruits avec leurs noms issus de `name`, et la visibilité dans l'URL est expliquée.
- La distinction URL / corps de requête est appliquée correctement pour GET et POST.
- Au moins un cas limite de la section précédente est décidé avec justification.
