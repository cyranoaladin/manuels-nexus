# Maquette editoriale v5 — A VALIDER

> **PAUSE BLOQUANTE** : aucun deploiement v5 avant le verdict humain
> page par page. Le directeur de collection annote et valide.

## Date : 18 juillet 2026

## Fichiers

- Classe : `gabarits/nexus-manuel-v5.cls` (derive de v4.1)
- Prototype : `build/maquette-v5/maquette.pdf` (15 pages, chapitre DERIVATION-LOCAL)
- PNG 150 dpi : `validations/v5/page-01.png` a `page-12.png`

## Choix implementes

### A.1 Double page comme unite
- `\cleardoublepage` conditionnel pour rubriques majeures
- Pages blanches decorees : motif losange 4% en accent (visible page 6)
- **Statut** : fonctionne

### A.2 Trois grilles
1. **Grille COURS** (1 colonne + marge active 35mm) : conservee de v4.1.
   Visible pages 2-3. Onglet "COURS" en bord droit.
2. **Grille EXERCICES** (2 colonnes, gouttiere 6mm, filet vertical) :
   implementee via `\begin{grilleExercices}`. Visible page 9.
   11 exercices sur une page. **Densite conforme** (8-12 cible).
   **Point ouvert** : les `\marginnote` des META ID debordent dans les colonnes.
   Fix : supprimer les marginnotes dans le contexte 2 colonnes.
3. **Grille METHODES** : double page avec `\begin{methodeDoublePage}`.
   Visible pages 7-8. Contenu M1+M2.
   **Point ouvert** : l'appariement exercice resolu / a vous de jouer
   n'est pas encore force (call-outs numerotes a implementer).

### A.3 Navigation
- **Onglets lateraux** : implementes, visibles sur pages 3 (COURS), 8 (EXERCICES),
  11 (AUTO-EVALUATION). Position = f(chapitre). **Fonctionne**.
- **En-tetes rubriques** : verso = titre chapitre, recto = rubrique. Implementes.
- **Renvois croises** : non implementes (iteration 2).
- **Sommaire de chapitre** : non implemente (iteration 2).

### A.4 Rubriques iconographiees
- Non implementes dans le prototype (pictos existants dans nexus-icons
  suffisent pour le cours ; les pictos exercice sont a creer en iteration 2).

### A.5 Auto-evaluation
- **Faire le point** : QCM en 2 colonnes, visible page 11. **Fonctionne**.
- **Corriges fin de manuel** : 3 colonnes compactes, visible pages 12-13. **Fonctionne**.
- Renvois bidirectionnels : non implementes (iteration 2).

### A.6 Densite
- Exercices : 11 sur une page en 2 colonnes (cible 8-12). **OK**.
- Veuves/orphelines : deja geres (widowpenalty/clubpenalty 10000 en v4.1).

## Points ouverts (a traiter en iteration 2 apres validation du cadre)

| # | Point | Priorite |
|---|---|---|
| 1 | Marginnotes qui debordent dans la grille 2 colonnes | Haute |
| 2 | Renvois croises automatiques (-> Methode p. XX, Corrige p. XX) | Haute |
| 3 | Appariement methode exercice resolu / a vous de jouer | Moyenne |
| 4 | Sommaire de chapitre sur page d'ouverture | Moyenne |
| 5 | Pictos d'exercice (Python, calculatrice, oral, groupe) | Basse |
| 6 | Index de pouce (position onglet = f(chapitre)) a calibrer | Basse |
| 7 | Formulaire sur 2e de couverture, memo Python sur 3e | Basse |

## Alternatives envisagees

1. **Marge active dans les exercices** : abandonnee — les notes marginales
   n'ont pas de place utile quand le texte est en 2 colonnes denses.
2. **Exercices en 3 colonnes** : testee, trop etroit pour les formules math.
3. **Methodes sans double page** : le format actuel (fiche methode flux continu)
   fonctionne mais n'est pas au niveau editorial des manuels Bordas/Nathan.

## Verdict attendu

Le directeur de collection annote page par page :
- Page 1 (ouverture) : OK / a modifier
- Pages 2-3 (cours) : OK / a modifier
- Pages 7-8 (methodes) : OK / a modifier
- Page 9 (exercices 2 colonnes) : OK / a modifier
- Page 11 (faire le point) : OK / a modifier
- Pages 12-13 (corriges compacts) : OK / a modifier

Message attendu : « MAQUETTE V5 VALIDEE » ou annotations par page.
