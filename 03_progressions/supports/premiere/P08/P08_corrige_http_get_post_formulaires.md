---
title: "P08 - Corrigé - HTTP, formulaires et confidentialité"
level: "premiere"
sequence_id: "P08"
document_type: "corrige"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "human_review_remediation"
theme: "Interaction client-serveur"
notion: "GET, POST, HTTPS, cookies et stockages du navigateur"
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

# P08 - Corrigé - HTTP, formulaires et confidentialité

## Question 1 — Requête GET

Les attributs `name` fournissent les noms des paramètres et les valeurs courantes fournissent leurs valeurs :

```text
/catalogue?q=python&niveau=debutant
```

Après l'envoi, les paramètres sont visibles dans l'URL, donc aussi dans la barre d'adresse et potentiellement dans l'historique et les journaux d'accès. GET convient à une recherche non sensible : l'URL décrit le résultat demandé, peut être mise en favori et partagée.

Si `q` est vide :

```text
/catalogue?q=&niveau=debutant
```

**Variantes acceptables.** L'ordre des deux paramètres peut être inversé. Une écriture omettant le paramètre vide n'est acceptée que si le comportement du navigateur ou du script est explicitement justifié ; avec le formulaire fourni, le champ nommé est normalement transmis avec une valeur vide.

## Question 2 — Formulaire POST

- Route : `/connexion`.
- Corps attendu sous forme simplifiée :

```text
pseudo=lecteur7&mot_de_passe=R3seau!
```

Le mot de passe n'apparaît pas dans l'URL : il se trouve dans le corps de la requête. `type="password"` masque les caractères à l'écran, mais n'agit pas sur le réseau. La protection du transport nécessite HTTPS, c'est-à-dire HTTP au-dessus de TLS.

**Erreur typique.** Dire « POST chiffre » confond emplacement et protection : POST déplace les paramètres hors de l'URL, HTTPS chiffre l'échange.

## Question 3 — Ordre client-serveur

1. **Client** : le navigateur sérialise les champs puis envoie la requête vers `/connexion`.
2. **Serveur** : la route lit et vérifie les informations reçues.
3. **Serveur** : il construit une réponse HTTP et peut ajouter un en-tête demandant la création d'un cookie.
4. **Client** : le navigateur reçoit et affiche la réponse, puis mémorise le cookie si les règles sont satisfaites.

Le navigateur ne doit pas accéder directement à la base des comptes : les contrôles d'autorisation et les données sensibles appartiennent au serveur. Un contrôle réalisé seulement en JavaScript pourrait être contourné par un client modifié.

## Question 4 — Stockage et retransmission

| Donnée | Stockage | Durée avec les informations fournies | Retransmission automatique ? |
|---|---|---|---|
| cookie `session_id` | navigateur, côté client | session du navigateur, car aucun `Expires` ou `Max-Age` n'est fourni | oui, vers l'origine et les chemins compatibles, ici `Path=/` |
| `theme` dans `localStorage` | navigateur, côté client | persiste après fermeture jusqu'à suppression | non |
| `onglet` dans `sessionStorage` | navigateur, côté client | jusqu'à la fermeture de l'onglet ou de la session associée | non |

`Secure` interdit l'envoi du cookie sur une connexion HTTP non chiffrée. `HttpOnly` interdit au JavaScript de la page de lire ce cookie ; le navigateur peut néanmoins le joindre automatiquement aux requêtes autorisées.

**Cas limite.** Un cookie expiré ou dont le `Path` ne correspond pas à la route n'est pas retransmis.

## Question 5 — Choix et confidentialité

1. Recherche `algorithmique` : **GET** ; la valeur n'est pas secrète et l'URL du résultat peut être partagée. HTTPS reste souhaitable pour l'intégrité et la confidentialité générale du trafic, même si la valeur n'est pas sensible.
2. Mot de passe : **POST + HTTPS** ; le mot de passe reste hors de l'URL et l'échange est chiffré.
3. Thème local au navigateur : `localStorage` suffit ; aucune requête n'est nécessaire si le serveur n'a pas besoin de cette préférence.
4. Un GET de connexion placerait le secret dans l'URL, l'historique et possiblement les journaux. HTTPS chiffre l'URL pendant le transport mais ne la retire ni de la barre d'adresse ni de l'historique local.

**Erreur typique.** HTTPS ne transforme pas un mauvais choix d'emplacement en bon choix de confidentialité locale.

## Synthèse des erreurs à reprendre

- Utiliser `id` à la place de `name` pour construire les paramètres.
- Confondre visibilité dans l'URL et chiffrement sur le réseau.
- Attribuer au client la vérification de confiance qui appartient au serveur.
- Croire que `localStorage` ou `sessionStorage` est automatiquement joint aux requêtes.
