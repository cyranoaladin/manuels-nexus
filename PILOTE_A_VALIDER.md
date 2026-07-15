# PILOTE A VALIDER — 1NSI-TYPES-CONSTRUITS

PDF : `build/1NSI-TYPES-CONSTRUITS/1NSI-TYPES-CONSTRUITS_complet.pdf` (32 pages, 607 Ko)

## Contenu du chapitre pilote

| Composant | Quantite | Status |
|---|---|---|
| Cours 3 strates (C1-C5) | 5 sections | needs_review |
| Fiches methodes (M1-M5) | 5 | needs_review |
| Exercices (3 parcours) | 54 | needs_review |
| Corriges | 3 (pilotes) | needs_review |
| Coups de pouce | 3 (pilotes) | needs_review |
| QCM diagnostique | 16 questions | needs_review |
| Remediation | 5 fiches R1-R5 | needs_review |
| Evaluation A | 4 exercices, 55 min | needs_review |
| Mini-projet | 4 jalons + extensions | needs_review |
| Version amenagee | Source recoltee, a transposer | pending |

## Sources T0 utilisees

- Sequence P04 (tuples/listes/dictionnaires) : 21 fichiers recoltes
- 3 fiches de cours (tuples, listes, dictionnaires)
- Code executable : starter + corrige_professeur + tests_attendus (3/3 OK)
- Contrat P04_contract.yml
- Verdict substance P-DATA-CONSTR-02A : needs_review (human_review_required)

## Points de jugement humain

1. **Figures memoire (C5)** : les schemas TikZ alias/copie sont-ils clairs et corrects ?
   Faut-il plus de figures (ex: representation memoire des dictionnaires) ?

2. **Densite des `\codereference`** : chaque section a un bloc de code de reference commente.
   Le niveau de detail des commentaires est-il adapte a la Premiere ?

3. **Equilibre transposition/reecriture** : le cours est une transposition enrichie du T0
   (ajout de contre-exemples, erreurs frequentes, figures, rubriques "A la machine").
   Le ton et la progressivite sont-ils adaptes au public cible ?

4. **Distinction code/console** : les environnements `python` (code) et `console` (session
   interactive) sont visuellement distincts. Est-ce suffisamment clair ?

5. **QCM distracteurs** : chaque mauvaise reponse pointe vers l'erreur commise et renvoie
   a la definition/methode/erreur frequente correspondante. Le format est-il utile ?

6. **Couverture des 5 capacites** : C1 (tuples), C2 (tableaux), C3 (grilles),
   C4 (dictionnaires), C5 (mutabilite). Des lacunes ?

7. **Evaluation** : le sujet A couvre les 5 capacites en 55 min avec contexte e-sport.
   Le niveau est-il calibre pour la Premiere ?

8. **Mini-projet** : 4 jalons progressifs (donnees, calcul, tri, affichage) avec criteres
   testables. Les extensions ◆◆◆ sont-elles realistes ?

## Statuts herites

- P-DATA-CONSTR-02A : needs_review (human_review_required) — propagation F08
- Tous les objets portent le statut `needs_review` herite du corpus

## Prochaines etapes apres validation

- Completer les corriges pour les 54 exercices
- Completer les coups de pouce (au moins 1 par exercice ◆/◆◆)
- Transposer la version amenagee (F11)
- Produire l'evaluation B
- Harmoniser les renvois entre exercices, methodes et cours
- Enchainer sur les 9 chapitres restants de Premiere
