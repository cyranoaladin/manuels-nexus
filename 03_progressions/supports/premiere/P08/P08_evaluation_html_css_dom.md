---
title: "P08 - Évaluation - HTML, CSS et DOM"
level: "premiere"
sequence_id: "P08"
document_type: "evaluation"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Interactions dans une page Web"
notion: "Structure HTML, sélecteurs CSS, événements et modification du DOM"
bareme: "P08_bareme_html_css_dom.md"
corrige: "P08_corrige_html_css_dom.md"
private_data: false
official_program:
  capacities:
    - "P-IHM-01A"
    - "P-IHM-01B"
    - "P-IHM-02"
---

# P08 - Évaluation - HTML, CSS et DOM

## Cadre

- Durée : 40 minutes.
- Total : 20 points.
- Documents : non autorisés.
- Capacités évaluées : `P-IHM-01A`, `P-IHM-01B`, `P-IHM-02`.
- Le code fourni est complet : aucune connaissance d'une page extérieure n'est nécessaire.

## Contexte — vote pour l'exposition du lycée

La page suivante permet de choisir un projet. Le serveur n'est pas étudié dans cette évaluation : on analyse uniquement la page exécutée dans le navigateur.

```html
<header>
  <h1>Exposition scientifique</h1>
</header>
<main>
  <form id="vote">
    <label for="projet">Projet préféré</label>
    <select id="projet" name="projet">
      <option value="">-- choisir --</option>
      <option value="robot">Robot trieur</option>
      <option value="serre">Serre connectée</option>
    </select>
    <button id="valider" type="submit">Voter</button>
  </form>
  <p id="message" class="info" aria-live="polite"></p>
</main>

<script>
const bouton = document.querySelector("#valider");
const choix = document.querySelector("#projet");
const message = document.querySelector("#message");

bouton.addEventListener("click", traiterVote);

function traiterVote(event) {
  event.preventDefault();
  if (choix.value === "") {
    message.textContent = "Choisissez un projet.";
    return;
  }
  message.textContent = "Vote enregistré : " + choix.value;
}
</script>
```

## Question 1 — Structure HTML et composants (4 points)

1. Représenter l'arbre HTML limité à `header`, `main`, `form`, `label`, `select`, `button` et `p`.
2. Expliquer le rôle de `header`, `main`, `form`, `label` et `button` dans cette page.
3. Justifier l'association entre le `label` et la liste `select` à l'aide de leurs attributs.

**Production attendue.** Un arbre parent-enfant et trois phrases fondées sur les balises ou attributs du code.

## Question 2 — Sélecteurs CSS (4 points)

1. Écrire le sélecteur CSS qui cible uniquement le paragraphe de message par son identifiant.
2. Écrire un sélecteur qui cible le bouton situé dans le formulaire `vote`.
3. Écrire une règle CSS qui affiche le message en bleu foncé et en gras.
4. Expliquer pourquoi le sélecteur `p` serait plus large que le sélecteur demandé en 1.

## Question 3 — Objets DOM et événement (4 points)

1. Associer les variables `bouton`, `choix` et `message` aux trois éléments HTML correspondants.
2. Nommer l'événement écouté et la fonction exécutée lorsqu'il se produit.
3. Expliquer le rôle de `event.preventDefault()` dans le cas d'un bouton `type="submit"`.

## Question 4 — Tracer le comportement (4 points)

Pour chaque scénario, écrire dans l'ordre : valeur de `choix.value`, condition évaluée, affectation réalisée, texte finalement visible.

1. L'utilisateur ne choisit aucun projet puis clique sur « Voter ».
2. L'utilisateur choisit « Serre connectée » puis clique sur « Voter ».

## Question 5 — Modifier le gestionnaire (4 points)

On veut empêcher un second vote après un choix valide, tout en laissant le bouton actif lorsque le choix est vide.

1. Indiquer à quel endroit précis de `traiterVote` ajouter l'instruction.
2. Écrire l'instruction DOM qui désactive le bouton.
3. Expliquer pourquoi placer cette instruction avant le `if` ne respecte pas le besoin.

## Repères enseignant — à masquer dans la projection élève

| Question | Réponse attendue centrale | Raisonnement observable | Piège à éviter | Critère décisif |
|---|---|---|---|---|
| 1 | `header` et `main` sont frères ; `form` contient `label`, `select`, `button` ; `p` est frère de `form` | `for="projet"` désigne `id="projet"` | placer `p` dans le formulaire ou confondre `id` et `name` | arbre et association label/champ justifiés |
| 2 | `#message`, `#vote button`, puis règle sur `#message` ou `.info` | comparer l'ensemble des éléments ciblés | proposer `message` sans `#` | sélecteurs effectivement applicables au code |
| 3 | clic → `traiterVote`; `preventDefault` bloque la soumission/rechargement par défaut | suivre liaison DOM puis événement | croire que `querySelector` modifie déjà la page | événement, fonction et effet par défaut distingués |
| 4 | vide → message d'erreur ; `serre` → « Vote enregistré : serre » | suivre branche puis `return` | afficher le libellé « Serre connectée » au lieu de la valeur `serre` | deux traces complètes et ordonnées |
| 5 | ajouter `bouton.disabled = true;` après la branche vide, avant ou après le message valide | l'instruction n'est atteinte que pour un choix valide | désactiver avant le test | placement relié à la condition |

## Critères de réussite et erreurs fréquentes — repères enseignant

- **Critère de réussite observable 1.** L'arbre produit permet de retrouver sans ambiguïté les relations parent, enfant et frère du fragment fourni.
- **Critère de réussite observable 2.** La trace du clic nomme l'événement, la branche exécutée, le contenu final de `#message` et l'état final du bouton.
- **Erreur fréquente 1 — confondre valeur et libellé d'une option.** `select.value` renvoie ici `serre`, pas « Serre connectée ». Antidote : lire séparément l'attribut `value` et le texte visible.
- **Erreur fréquente 2 — désactiver avant la validation.** Le bouton deviendrait inactif même quand le choix est vide. Antidote : placer l'instruction après le `return` de la branche d'erreur.

Le résultat attendu pour la question 4 comporte deux traces distinctes et ordonnées ; une phrase donnant seulement le message final ne constitue pas une correction vérifiable.

## Aménagement

La version commune `P08_version_amenagee_web_http_dom_formulaires.md` doit être utilisée en ne dévoilant que les aides HTML/CSS/DOM correspondant à ce sujet.
