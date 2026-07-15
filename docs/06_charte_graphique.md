# Charte graphique — Nexus Réussite

## 1. Grille de page et rythme de lecture

Le format est A4 recto-verso. La colonne principale occupe la zone de composition entre une marge intérieure de 2 cm et une marge extérieure de 4,5 cm. Cette dernière comprend une colonne pédagogique de 3,6 cm, séparée du texte par 5 mm : elle accueille exclusivement les appuis, repères de méthode et alertes courtes. Aucun calcul indispensable ne vit dans la marge.

Le corps est composé en 11 pt avec un interligne effectif minimal de 1,25 et `\raggedbottom` : une page reste respirante plutôt que d'étirer les blancs. Une unité de lecture ne dépasse pas huit lignes sans respiration (paragraphe, exemple, liste, formule ou encadré). Les listes ont un espacement supérieur et inférieur visible ; les formules longues sont centrées et isolées.

## 2. Hiérarchie typographique

- **H1 — ouverture** : pleine page, 26 pt, gras bleu Nexus. Elle porte le titre, la liste complète « Ce que je vais savoir faire », la carte issue de la situation d'accroche et les temps ◆/◆◆/◆◆◆ du contrat.
- **H2 — section-capacité** : numéro de section + capacité Cn, 15 pt, gras sans empattement bleu ; le rappel « Je sais… » est placé dans la marge dès que la commande `\sectionCapacite` est employée.
- **H3 — sous-partie** : 12 pt, gras sans empattement bleu foncé, avant un changement d'idée, jamais pour maquiller une phrase.
- **Corps** : Libertine avec mathématiques assorties ; titres et titres d'encadrés en sans empattement. Les titres d'encadrés sont en petites capitales. Veuves et orphelines sont interdites (`\widowpenalty=\clubpenalty=10000`).

## 3. Palette Nexus et pictogrammes

| Couleur | Code | Usage exclusif |
|---|---|---|
| Bleu | `#1B3A5C` | savoir, définitions, théorèmes, titres |
| Or | `#C9A227` | méthode, parcours, temps |
| Rouge | `#B0413E` | erreur fréquente, contre-exemple |
| Vert | `#2E6E4E` | exemple validé, corrigé, vérification |
| Gris | `#5A6472` | appui de marge, carte, information secondaire |

Une page ne montre jamais plus de deux couleurs vives parmi bleu, or, rouge et vert ; le gris peut les accompagner. Les fonds sont limités à 4–6 % de teinte (jamais plus de 8 %) afin de rester lisibles en impression N&B. Les pictogrammes sont invariants : ◆/◆◆/◆◆◆ parcours, ▲ erreur, ★ approfondissement, 🗣 oral, `>>>` Python. Ils ne sont jamais le seul porteur de sens : un libellé les accompagne.

## 4. Encadrés, exercices et navigation

Les encadrés sont `breakable`, à coin discret, avec règle gauche fine de 1,2 pt ; aucun cadre lourd bleu intégral. Les définitions, propriétés et théorèmes sont bleus ; méthodes or, erreurs rouges, approfondissements bleus légers. Les exercices affichent au premier regard leur numéro bleu, leur parcours or, leur identifiant et leur durée. Les coups de pouce sont des fichiers compagnons `exercices/{ID}-CDP.tex`, regroupés après les exercices : ils ne figurent jamais dans l'énoncé.

Les en-têtes affichent le chapitre courant et « Nexus Réussite » ; le pied central porte la pagination continue. Le sommaire est précédé de l'ouverture, dont l'entrée est ajoutée automatiquement. Les règles s'appliquent à tous les chapitres et à toutes les déclinaisons.
