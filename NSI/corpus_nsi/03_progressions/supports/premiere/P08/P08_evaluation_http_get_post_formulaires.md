---
title: "P08 - Évaluation - HTTP, formulaires et confidentialité"
level: "premiere"
sequence_id: "P08"
document_type: "evaluation"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Interaction client-serveur"
notion: "GET, POST, HTTPS, cookies et stockages du navigateur"
bareme: "P08_bareme_http_get_post_formulaires.md"
corrige: "P08_corrige_http_get_post_formulaires.md"
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

# P08 - Évaluation - HTTP, formulaires et confidentialité

## Cadre

- Durée : 40 minutes.
- Total : 20 points.
- Documents : non autorisés.
- Capacités évaluées : `P-IHM-03A`, `P-IHM-03B`, `P-IHM-03C`, `P-IHM-04A`, `P-IHM-04B`, `P-IHM-04C`.
- Les identifiants fournis sont fictifs et servent uniquement à raisonner sur les échanges.

## Contexte — médiathèque en ligne

La page contient deux formulaires indépendants.

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

<form method="post" action="/connexion">
  <label for="pseudo">Pseudo</label>
  <input id="pseudo" name="pseudo" value="lecteur7">
  <label for="mdp">Mot de passe</label>
  <input id="mdp" name="mot_de_passe" type="password" value="R3seau!">
  <button type="submit">Se connecter</button>
</form>
```

Après une connexion réussie en HTTPS, le navigateur possède :

```text
Cookie: session_id=abc123; Path=/; Secure; HttpOnly
localStorage: theme=sombre
sessionStorage: onglet=aide
```

## Question 1 — Construire une requête GET (4 points)

1. Construire le chemin et la chaîne de paramètres envoyés lors de la soumission du formulaire de recherche.
2. Indiquer où les deux valeurs sont visibles après l'envoi.
3. Expliquer pourquoi GET convient ici à une recherche partageable.
4. Cas limite : donner le chemin obtenu si le champ `q` est vide mais que le niveau reste `debutant`.

## Question 2 — Analyser le formulaire POST (4 points)

1. Donner la route visée et écrire le corps de la requête sous la forme `nom=valeur&nom=valeur`.
2. Indiquer si le mot de passe apparaît dans l'URL.
3. Expliquer pourquoi `type="password"` ne chiffre pas la transmission.
4. Indiquer la condition réseau nécessaire pour protéger l'échange.

## Question 3 — Ordonner client et serveur (4 points)

Remettre dans l'ordre et attribuer chaque action au client ou au serveur :

- la route `/connexion` vérifie les informations reçues ;
- le navigateur construit puis envoie la requête ;
- le serveur renvoie une réponse HTTP et peut demander la création d'un cookie ;
- le navigateur affiche la réponse et stocke le cookie conforme.

Expliquer ensuite pourquoi le JavaScript du navigateur ne doit pas accéder directement à la base des comptes.

## Question 4 — Données mémorisées et retransmises (4 points)

Compléter le tableau pour `session_id`, `theme` et `onglet` : lieu de stockage, durée approximative, retransmission automatique au serveur oui/non. Préciser l'effet de `Secure` et de `HttpOnly` sur le cookie.

## Question 5 — Choisir selon la confidentialité (4 points)

Pour chaque cas, choisir GET ou POST et dire si HTTPS est nécessaire. Justifier avec un critère observable : URL, historique, corps de requête, chiffrement ou partage du lien.

1. Rechercher `algorithmique` dans le catalogue.
2. Envoyer un mot de passe de connexion.
3. Enregistrer le thème d'affichage uniquement dans ce navigateur.
4. Expliquer pourquoi remplacer POST par GET pour la connexion serait une mauvaise décision, même si le site utilise HTTPS.

## Repères enseignant — à masquer dans la projection élève

| Question | Réponse attendue centrale | Raisonnement observable | Piège à éviter | Critère décisif |
|---|---|---|---|---|
| 1 | `/catalogue?q=python&niveau=debutant` ; cas vide `/catalogue?q=&niveau=debutant` | les attributs `name` deviennent les noms des paramètres | utiliser les `id` ou oublier un champ | URL complète et visibilité expliquée |
| 2 | route `/connexion`, corps `pseudo=lecteur7&mot_de_passe=R3seau!`, HTTPS nécessaire | POST place les valeurs dans le corps ; TLS chiffre le transport | affirmer que POST ou `type=password` chiffre | corps, URL et chiffrement distingués |
| 3 | navigateur → serveur → réponse → navigateur | séparer exécution cliente et vérification serveur | faire vérifier le mot de passe par le seul navigateur | ordre et responsabilités corrects |
| 4 | cookie client et automatiquement retransmis ; localStorage/sessionStorage client et non retransmis | raisonner mécanisme par mécanisme | dire que localStorage est envoyé avec chaque requête | stockage et retransmission dissociés |
| 5 | recherche GET ; connexion POST+HTTPS ; thème localStorage ; GET expose le mot de passe dans URL/historique | HTTPS chiffre sans retirer la donnée de l'URL locale | croire que HTTPS rend GET adapté à un secret | choix justifié par confidentialité et usage |

## Critères de réussite et erreurs fréquentes — repères enseignant

- **Critère de réussite observable 1.** Les paramètres GET sont reconstruits avec leurs noms issus de `name`, et l'élève indique où ils deviennent visibles.
- **Critère de réussite observable 2.** Pour chaque stockage, la réponse sépare lieu, durée et retransmission automatique au serveur.
- **Erreur fréquente 1 — dire que POST chiffre les données.** POST change leur emplacement, pas leur confidentialité sur le réseau. Antidote : traiter séparément méthode HTTP et présence de HTTPS.
- **Erreur fréquente 2 — confondre cookie et `localStorage`.** Le cookie peut être joint automatiquement à une requête ; `localStorage` ne l'est pas. Antidote : suivre explicitement le mécanisme de retransmission.

Le résultat attendu pour la question 5 associe une décision et un critère observable à chacun des quatre cas ; une liste « GET, POST, localStorage » sans justification n'est pas une correction complète.

## Aménagement

La version commune `P08_version_amenagee_web_http_dom_formulaires.md` doit être utilisée en ne dévoilant que les aides HTTP/formulaires correspondant à ce sujet.
