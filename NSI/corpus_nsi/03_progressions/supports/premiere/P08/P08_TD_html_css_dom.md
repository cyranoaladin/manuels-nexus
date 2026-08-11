---
title: "P08 - TD - HTML, CSS et DOM"
level: "premiere"
sequence_id: "P08"
document_type: "td"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "HTML, CSS et DOM"
notion: "Structure HTML, sélecteurs CSS, DOM et événements"
private_data: false
official_program:
  capacities:
    - "P-IHM-01A"
    - "P-IHM-01B"
    - "P-IHM-02"
---

# P08 - TD - HTML, CSS et DOM

## Objectifs

- Lire une page en distinguant structure HTML, attributs et contenu affiché.
- Expliquer à quel élément s'applique un sélecteur CSS.
- Sélectionner un nœud du DOM, le modifier et relier un événement à son gestionnaire.
- Déboguer un script court sans confondre la recherche d'un élément avec la modification de cet élément.

## Prérequis

- Une balise ouvre et structure un élément ; un attribut précise une propriété de cet élément.
- En CSS, `#` introduit un identifiant et `.` une classe.
- JavaScript peut lire ou modifier le DOM après le chargement de la page.

## Progression socle / standard / approfondissement

- **Socle** : exercices 1 et 2, pour lire le code HTML et les sélecteurs CSS.
- **Standard** : exercices 3 à 6, pour manipuler le DOM et suivre un événement.
- **Approfondissement** : exercices 7 et 8, pour justifier un choix technique et rectifier un raisonnement.

## Exercices

### Exercice 1 — Lire une structure HTML

- Type : lecture/analyse.
- Capacité officielle : P-IHM-01A.
- Données : fragment « structure du club sciences » :

```html
<main>
  <h1>Club sciences</h1>
  <p class="intro">Choisis un atelier.</p>
  <button id="inscrire">S'inscrire</button>
</main>
```

- Consigne : recopie dans un tableau les balises, les attributs et les textes visibles. Puis indique quel élément est enfant de `main`, quel attribut est un `id` et quel attribut est une `class`.
- Critère de réussite : le tableau sépare bien `button`, `id="inscrire"` et le texte « S'inscrire » ; il ne transforme pas une classe en identifiant.

### Exercice 2 — Relier HTML et CSS

- Type : lecture/analyse.
- Capacité officielle : P-IHM-01A.
- Données : fragment « alerte et classe importante » :

```html
<p id="alerte" class="important">Inscription fermée</p>
<p class="important">Apporter une blouse</p>
```

```css
p { color: black; }
.important { font-weight: bold; }
#alerte { color: red; }
```

- Consigne : pour chacun des deux paragraphes, liste les règles CSS qui le ciblent puis décris son apparence finale. Justifie pourquoi `#alerte` ne cible pas le second paragraphe.
- Critère de réussite : la réponse distingue le sélecteur de balise `p`, la classe `.important` et l'identifiant `#alerte`.

### Exercice 3 — Modifier une page par le DOM

- Type : production/écriture.
- Capacité officielle : P-IHM-02.
- Données : fragment « état de l'inscription » :

```html
<p id="etat">En attente</p>
```

- Consigne : écris deux instructions JavaScript : la première sélectionne le paragraphe dans une variable `etat`, la seconde remplace uniquement son texte par « Inscription confirmée ». Explique en une phrase ce que fait chaque instruction.
- Cas limite : prévois ce que tu vérifierais si aucun élément ne portait l'identifiant `etat`.
- Critère de réussite : la sélection et l'affectation à `textContent` sont deux opérations distinctes.

### Exercice 4 — Choisir un sélecteur avec `querySelector`

- Type : production/écriture.
- Capacité officielle : P-IHM-02.
- Données : fragment « deux scores à distinguer » :

```html
<section id="resultats">
  <p class="score">Équipe A : 3</p>
  <p class="score">Équipe B : 2</p>
</section>
```

- Consigne : complète les trois appels suivants en utilisant `querySelector` : sélectionner la section, sélectionner le premier paragraphe de score, sélectionner le paragraphe dont le texte commence par « Équipe B » sans utiliser son texte comme sélecteur. Pour le troisième appel, ajoute l'attribut minimal à l'HTML puis donne le sélecteur correspondant.
- Justification : compare `#resultats`, `.score` et `p`. Indique lequel ne doit pas servir seul pour désigner précisément l'équipe B.
- Critère de réussite : les préfixes `#` et `.` sont employés selon l'attribut ciblé ; l'élève sait que `querySelector` renvoie le premier élément correspondant.

### Exercice 5 — Réagir à un événement

- Type : trace/table.
- Capacité officielle : P-IHM-01B.
- Données : fragment « bouton bonjour et message » :

```html
<button id="bonjour">Dire bonjour</button>
<p id="message"></p>
<script>
const bouton = document.getElementById("bonjour");
const message = document.querySelector("#message");

function saluer() {
  message.textContent = "Bonjour !";
}

bouton.addEventListener("click", saluer);
</script>
```

- Consigne : complète la chronologie suivante : chargement de la page → … → clic de l'utilisateur → … → …. Nomme séparément l'événement et le gestionnaire d'événement.
- Critère de réussite : `click` est identifié comme le signal reçu et `saluer` comme la fonction appelée ; le texte ne change pas au chargement seul.

### Exercice 6 — Déboguer un script DOM

- Type : débogage.
- Capacité officielle : P-IHM-02.
- Données : fragment « compteur avec identifiant erroné » :

```html
<button id="compter">Ajouter</button>
<p id="total">0</p>
<script>
const total = document.getElementById("totale");
document.getElementById("compter").addEventListener("click", () => {
  total.textContent = "1";
});
</script>
```

- Consigne : le navigateur signale une erreur parce que `total` vaut `null`. Localise l'erreur, corrige-la et explique pourquoi la ligne qui modifie `textContent` ne peut pas fonctionner avant cette correction. Propose ensuite une seconde cause possible de `null` liée au moment où le script s'exécute.
- Critère de réussite : la correction remplace l'identifiant erroné et mentionne qu'un script placé avant l'élément doit attendre le chargement ou être déplacé.

### Exercice 7 — Distinguer HTML, CSS et JavaScript

- Type : justification.
- Capacité officielle : P-IHM-01A.
- Données : la page doit afficher un titre, rendre ce titre bleu et afficher « Bienvenue » après le clic sur un bouton.

- Consigne : classe chacune des modifications suivantes dans **HTML (structure)**, **CSS (style)** ou **JavaScript (comportement)**, puis justifie chaque choix :
  1. ajouter `<h2 id="titre">Ateliers</h2>` ;
  2. écrire `#titre { color: blue; }` ;
  3. ajouter un écouteur `click` qui affecte `message.textContent`.
- Transfert : explique pourquoi dire « CSS modifie le DOM » est imprécis dans cette situation.
- Critère de réussite : le rôle de chaque langage est relié à une action visible différente, sans confondre une règle de style et une instruction JavaScript.

### Exercice 8 — Corriger des raisonnements faux

- Type : transfert.
- Capacité officielle : P-IHM-01B.
- Données : quatre affirmations d'un camarade.

1. « `id` et `class` sont interchangeables. »
2. « `querySelector` renvoie toujours plusieurs éléments. »
3. « Un gestionnaire ajouté avec `addEventListener` est exécuté dès le chargement. »
4. « Pour modifier un texte, il suffit d'écrire un sélecteur CSS. »

- Consigne : pour chaque affirmation, écris **vrai** ou **faux**, puis donne un contre-exemple ou une correction technique précise. Pour la troisième affirmation, distingue le moment où l'écouteur est installé et le moment où le clic se produit.
- Critère de réussite : chaque rectification contient un fragment concret tel que `#titre`, `.important`, `document.querySelector("#titre")` ou `element.textContent = "..."`.

## Corrigé — indications de raisonnement

Les indications ci-dessous servent à vérifier une démarche ; le corrigé complet de l'évaluation est séparé dans `P08_corrige_html_css_dom.md`.

### Corrigé exercice 1

- Donnée utilisée : dans le fragment, `main`, `h1`, `p` et `button` sont des balises ; `class="intro"` et `id="inscrire"` sont des attributs ; « Club sciences », « Choisis un atelier. » et « S'inscrire » sont des textes.
- Méthode : lire l'imbrication avant de nommer les attributs. Les trois éléments `h1`, `p` et `button` sont enfants de `main`.
- Résultat : `id="inscrire"` identifie le bouton ; `class="intro"` regroupe éventuellement plusieurs éléments. Aucun de ces mots n'est une balise.
- Vérification : remplacer `class` par `id` changerait la nature de l'attribut, pas le texte affiché.

### Corrigé exercice 2

- Donnée utilisée : les deux paragraphes correspondent à `p` et `.important` ; seul « Inscription fermée » possède `id="alerte"`.
- Méthode : tester chaque sélecteur contre les attributs de chaque élément, sans confondre `#` et `.`.
- Résultat : le premier paragraphe est noir par `p`, gras par `.important` et rouge par `#alerte` ; le second est noir et gras, mais pas rouge.
- Vérification : écrire `.alerte` chercherait une classe nommée `alerte`, absente ici.

### Corrigé exercice 3

- Donnée utilisée : l'élément possède `id="etat"` et son texte initial est « En attente ».
- Méthode : sélectionner d'abord le nœud, puis modifier une propriété de ce nœud.
- Résultat : `const etat = document.getElementById("etat");` puis `etat.textContent = "Inscription confirmée";` produisent le texte demandé.
- Vérification : si `etat` vaut `null`, il faut vérifier l'orthographe de l'identifiant avant toute affectation à `textContent`.

### Corrigé exercice 4

- Donnée utilisée : `#resultats` désigne une section unique ; `.score` correspond aux deux paragraphes.
- Méthode : `document.querySelector("#resultats")` sélectionne la section et `document.querySelector(".score")` le premier score. Pour désigner l'équipe B, on peut ajouter `id="equipe-b"` au second paragraphe puis appeler `document.querySelector("#equipe-b")`.
- Résultat : `p` seul est trop large et `.score` ne distingue pas les deux équipes ; `querySelector` ne renvoie pas une liste, mais le premier élément trouvé.
- Vérification : un sélecteur `#equipe-b` sans identifiant correspondant renverrait `null`.

### Corrigé exercice 5

- Donnée utilisée : le bouton porte `id="bonjour"`, l'écouteur est `addEventListener("click", saluer)` et le paragraphe est `#message`.
- Méthode : séparer installation de l'écouteur et exécution du gestionnaire.
- Résultat : chargement → les constantes sont créées et l'écouteur est installé → clic utilisateur → appel de `saluer` → `message.textContent` devient « Bonjour ! ».
- Vérification : sans clic, la fonction `saluer` n'est pas appelée et le paragraphe reste vide.

### Corrigé exercice 6

- Donnée utilisée : le HTML contient `id="total"`, mais JavaScript demande `"totale"`.
- Méthode : comparer caractère par caractère l'identifiant HTML et l'argument de `getElementById` ; contrôler ensuite que l'élément existe avant le clic.
- Résultat : `const total = document.getElementById("total");` évite `null`, donc `total.textContent = "1";` s'exécute au clic. Un script placé dans `head` avant le paragraphe peut aussi obtenir `null` ; on le place après le HTML ou on attend `DOMContentLoaded`.
- Vérification : un clic après correction affiche `1` dans le paragraphe `#total`.

### Corrigé exercice 7

- Donnée utilisée : `<h2 id="titre">Ateliers</h2>` décrit un élément de page, `#titre { color: blue; }` règle son apparence et l'écouteur traite une action.
- Méthode : demander si l'instruction crée une structure, définit un style ou réagit à une action utilisateur.
- Résultat : 1 est HTML, 2 est CSS, 3 est JavaScript. CSS déclare une présentation ; JavaScript modifie le DOM en affectant par exemple `message.textContent`.
- Vérification : changer `color` ne crée pas de nouveau nœud et ne déclenche aucun clic.

### Corrigé exercice 8

- Donnée utilisée : les affirmations portent sur les préfixes CSS, le retour de `querySelector`, l'événement `click` et `textContent`.
- Méthode : rectifier chaque phrase par un exemple minimal, plutôt que par une définition isolée.
- Résultat : 1 faux : un `id` vise un élément identifié, tandis que `.important` peut viser plusieurs éléments ; 2 faux : `document.querySelector("#titre")` renvoie le premier élément correspondant ; 3 faux : l'écouteur est installé au chargement mais `saluer` attend le clic ; 4 faux : `#titre` cible pour le style, alors que `element.textContent = "Bonjour"` modifie le contenu.
- Vérification : `querySelectorAll(".important")` est l'API qui renvoie tous les éléments correspondants, sous forme de liste de nœuds.

## Erreurs fréquentes

- Confondre l'attribut `id` avec une classe : `#inscrire` et `.intro` ne désignent pas la même chose.
- Croire que sélectionner avec `querySelector` transforme déjà la page : il faut ensuite modifier une propriété telle que `textContent`.
- Nommer `click` comme une fonction : c'est l'événement ; `saluer` est le gestionnaire.
- Oublier qu'un mauvais identifiant ou un script exécuté trop tôt peut produire `null`.

## Différenciation

- **Socle** : surligner d'une couleur les balises, d'une autre les attributs et entourer les textes avant de répondre aux exercices 1 et 2.
- **Standard** : écrire les instructions DOM des exercices 3 à 6 puis les faire relire en identifiant séparément sélecteur, nœud et propriété modifiée.
- **Approfondissement** : dans l'exercice 8, remplacer `querySelector` par `querySelectorAll` et expliquer la conséquence sur la suite du programme.

## Critères de réussite observables

- Une réponse nomme précisément le langage et l'objet manipulé : balise HTML, règle CSS, élément DOM, événement ou gestionnaire.
- Une modification du DOM distingue l'étape de sélection de l'étape d'affectation.
- Une explication d'événement donne l'ordre : installation de l'écouteur, action utilisateur, appel de fonction, effet sur le DOM.
