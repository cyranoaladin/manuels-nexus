---
title: "P08 - Corrigé - HTML, CSS et DOM"
level: "premiere"
sequence_id: "P08"
document_type: "corrige"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "human_review_remediation"
theme: "Interactions dans une page Web"
notion: "Structure HTML, sélecteurs CSS, événements et modification du DOM"
private_data: false
official_program:
  capacities:
    - "P-IHM-01A"
    - "P-IHM-01B"
    - "P-IHM-02"
---

# P08 - Corrigé - HTML, CSS et DOM

## Question 1 — Structure HTML et composants

Arbre limité aux éléments demandés :

```text
document
├── header
└── main
    ├── form#vote
    │   ├── label[for="projet"]
    │   ├── select#projet
    │   └── button#valider
    └── p#message
```

- `header` regroupe l'en-tête de la page et son titre.
- `main` contient le contenu principal propre à cette page.
- `form` regroupe les composants dont les valeurs participent à une soumission.
- `label` donne un libellé accessible au champ ; `for="projet"` désigne l'élément portant `id="projet"`.
- `button type="submit"` déclenche normalement la soumission du formulaire.

**Erreur typique.** `name="projet"` sert à nommer la valeur transmise ; ce n'est pas cet attribut que `for` utilise. L'association label-champ repose sur `for` et `id`.

## Question 2 — Sélecteurs CSS

```css
#message {
  color: #153a66;
  font-weight: bold;
}

#vote button {
  /* cible les boutons descendants du formulaire vote */
}
```

`#message` cible un élément portant l'identifiant unique `message`. Le sélecteur `p` cible tous les paragraphes de la page ; il deviendrait trop large dès qu'un autre paragraphe serait ajouté. `.info` est une variante acceptable pour la règle de style puisque le paragraphe possède cette classe, mais la première sous-question exige l'identifiant.

## Question 3 — Objets DOM et événement

- `bouton` désigne `<button id="valider">`.
- `choix` désigne `<select id="projet">`.
- `message` désigne `<p id="message">`.
- L'événement écouté est `click`; la fonction associée est `traiterVote`.

Le bouton étant de type `submit`, son comportement par défaut est de soumettre le formulaire, ce qui peut charger une nouvelle page. `event.preventDefault()` annule ce comportement pour que le script puisse valider le choix et modifier le texte sans quitter la page.

**Cas limite.** Appuyer sur Entrée dans le formulaire peut déclencher une soumission sans événement `click` selon le contexte. Une écoute de l'événement `submit` sur le formulaire serait plus générale ; cette remarque est un approfondissement, pas une exigence de la question.

## Question 4 — Trace du comportement

### Aucun projet choisi

1. `choix.value` vaut `""`.
2. La condition `choix.value === ""` est vraie.
3. `message.textContent` reçoit `"Choisissez un projet."`.
4. `return` termine la fonction : le second message n'est pas exécuté.

Texte visible : **Choisissez un projet.**

### Serre connectée choisie

1. `choix.value` vaut `"serre"`, car le code lit l'attribut `value` de l'option.
2. La condition est fausse.
3. L'affectation finale concatène `"Vote enregistré : "` et `"serre"`.

Texte visible : **Vote enregistré : serre**.

**Erreur typique.** Le texte visible de l'option est « Serre connectée », mais sa valeur DOM est `serre`.

## Question 5 — Modifier le gestionnaire

Une solution est :

```javascript
function traiterVote(event) {
  event.preventDefault();
  if (choix.value === "") {
    message.textContent = "Choisissez un projet.";
    return;
  }
  message.textContent = "Vote enregistré : " + choix.value;
  bouton.disabled = true;
}
```

L'instruction doit être atteinte seulement après avoir établi que le choix n'est pas vide. La placer avant le `if` désactiverait aussi le bouton lors d'une tentative invalide, empêchant l'utilisateur de corriger son choix.

**Variante acceptable.** Placer `bouton.disabled = true;` juste avant l'affectation du message valide produit le même comportement.

## Synthèse des erreurs à reprendre

- Arbre incorrect : repartir de l'imbrication des balises, pas de leur apparence visuelle.
- Sélecteur trop large : énumérer les éléments effectivement ciblés.
- Événement confondu avec fonction : `click` est le signal, `traiterVote` le traitement.
- Trace incomplète : noter la valeur, le test, la branche et l'effet DOM dans cet ordre.
